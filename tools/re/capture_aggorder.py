"""capture_aggorder.py <addon> <map> [--out file]: where a prop aggregate's fragment order comes from (OPEN 1.c7,
ledger 254: n0.vwnod differs from Valve only in prop aggregate fragment order).

WRBNode_BuildPropAggregates (180272ce0) gives every entry its own 0x1a8-byte object from g_pMemAlloc (vtable +8),
the CMesh at +0x10 of it, and per material bucket runs WRBMeshList_SortMorton (180274be0) and a stable sort by
(entry +0x1b0 & 0x6000000000, entry +0x0: that object's pointer). tier0's allocator is mimalloc
(ULowLevelAllocationScheme_mimalloc), so the pointer order is the allocator's. A -world -fshallow compile under
Frida logs, while BuildNode (18024b430, which loads the prop meshes and runs BuildPropAggregates) runs on a thread:
- every g_pMemAlloc Alloc of 385..448 bytes (mimalloc's 448 bin, which holds 0x1a8) with its sequence number,
  size, pointer and caller, and every Free on that thread (pointer, sequence number);
- each bucket after SortMorton and at WRB_BuildAggregate (180268e80) entry: per entry the object pointer (+0x0),
  CMesh (+0x10), node id (+0x40), attributes (+0x1b0) and the CMesh vertex count.
CS2 must be closed; the package is backed up and restored, cmp-checked.
"""
import argparse
import filecmp
import json
import os
import shutil
import subprocess
import sys
import threading
import frida
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rva_map import installed  # noqa: E402
CS2 = os.environ.get("CS2_DIR", r"D:\Steam\steamapps\common\Counter-Strike Global Offensive")
BIN = os.path.join(CS2, "game", "bin", "win64")

AGENT = r"""
let mod = null, seq = 0, allocHook = null, freeHook = null;
const inside = {};
function entries(list) {
  const n = list.readS32(), data = list.add(8).readPointer(), out = [];
  for (let i = 0; i < n && i < 100000; i++) {
    const e = data.add(i * 0x238), m = e.add(0x10).readPointer();
    out.push({obj: e.readPointer().toString(), mesh: m.toString(), node: e.add(0x40).readS32(),
              attrs: e.add(0x1b0).readU64().toString(16), verts: m.isNull() ? -1 : m.add(0x18).readS32()});
  }
  return out;
}
function attachAllocator() {
  const tier0 = Process.getModuleByName('tier0.dll');
  const g = tier0.getExportByName('g_pMemAlloc').readPointer();
  const vt = g.readPointer();
  allocHook = Interceptor.attach(vt.add(8).readPointer(), {
    onEnter(args) {
      this.tid = Process.getCurrentThreadId();
      if (!inside[this.tid]) { this.tid = 0; return; }
      this.size = args[1].toUInt32(); this.ra = this.returnAddress;
    },
    onLeave(ret) {
      if (this.tid === 0) return;
      seq++;
      if (this.size > 384 && this.size <= 448) {
        const m = Process.findModuleByAddress(this.ra);
        send({stage: 'alloc', seq: seq, tid: this.tid, size: this.size, ptr: ret.toString(),
              caller: m ? m.name + '+' + this.ra.sub(m.base).toString(16) : this.ra.toString()});
      }
    }
  });
  Interceptor.attach(vt.add(0x10).readPointer(), {
    onEnter(args) {
      this.tid = Process.getCurrentThreadId();
      if (!inside[this.tid]) { this.tid = 0; return; }
      this.old = args[1]; this.size = args[2].toUInt32();
    },
    onLeave(ret) {
      if (this.tid === 0) return;
      seq++;
      if ((this.size > 384 && this.size <= 448) || !this.old.isNull())
        send({stage: 'realloc', seq: seq, tid: this.tid, size: this.size, old: this.old.toString(), ptr: ret.toString()});
    }
  });
  freeHook = Interceptor.attach(vt.add(0x18).readPointer(), {
    onEnter(args) {
      const tid = Process.getCurrentThreadId();
      if (!inside[tid] || args[1].isNull()) return;
      seq++;
      send({stage: 'free', seq: seq, tid: tid, ptr: args[1].toString()});
    }
  });
}
function hook() {
  mod = Process.findModuleByName('resourcecompiler.dll');
  if (mod === null || Process.findModuleByName('tier0.dll') === null) { setTimeout(hook, 5); return; }
  attachAllocator();
  Interceptor.attach(mod.base.add(%(build)d), {
    onEnter() { this.tid = Process.getCurrentThreadId(); inside[this.tid] = (inside[this.tid] || 0) + 1;
                send({stage: 'enter', seq: seq, tid: this.tid}); },
    onLeave() { inside[this.tid]--; send({stage: 'leave', seq: seq, tid: this.tid}); }
  });
  Interceptor.attach(mod.base.add(%(morton)d), {
    onEnter(args) { this.list = args[1]; },
    onLeave() { send({stage: 'morton', seq: seq, tid: Process.getCurrentThreadId(), entries: entries(this.list)}); }
  });
  Interceptor.attach(mod.base.add(%(aggregate)d), {
    onEnter(args) { send({stage: 'aggregate', seq: seq, tid: Process.getCurrentThreadId(), entries: entries(args[3])}); }
  });
  send({hooked: true});
}
hook();
"""


def running(name):
    out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq " + name], capture_output=True, text=True).stdout
    return name.lower() in out.lower()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("addon")
    p.add_argument("map")
    p.add_argument("--out")
    a = p.parse_args()
    if running("cs2.exe"):
        raise SystemExit("CS2 is running; not starting")
    if running("resourcecompiler.exe"):
        raise SystemExit("another resourcecompiler is running; not starting")
    if shutil.disk_usage(os.path.splitdrive(CS2)[0] + "\\").free < 10 * 1024 ** 3:
        raise SystemExit("under 10 GB free on the game drive; not starting")
    rvas = {"build": installed("resourcecompiler", 0x24b430), "morton": installed("resourcecompiler", 0x274be0),
            "aggregate": installed("resourcecompiler", 0x268e80)}
    out_path = a.out or os.path.join(os.environ.get("TEMP", "."), "aggorder_capture", a.map + ".jsonl")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    vpk = os.path.join(CS2, "game", "csgo_addons", a.addon, "maps", a.map + ".vpk")
    backup = out_path + ".vpk.bak"
    if os.path.exists(vpk):
        shutil.copyfile(vpk, backup)
        os.remove(vpk)
    out = open(out_path, "w")
    lock = threading.Lock()
    hooked = threading.Event()

    def on_message(msg, _data):
        if msg.get("type") != "send":
            print("agent:", msg.get("description") or msg)
        elif msg["payload"].get("hooked"):
            hooked.set()
        else:
            with lock:
                out.write(json.dumps(msg["payload"]) + "\n")

    source = os.path.join(CS2, "content", "csgo_addons", a.addon, "maps", a.map + ".vmap")
    argv = [os.path.join(BIN, "resourcecompiler.exe"), "-nop4", "-game", os.path.join(CS2, "game", "csgo"),
            "-i", source, "-world", "-fshallow"]
    dev = frida.get_local_device()
    pid = dev.spawn(argv, cwd=BIN, stdio="pipe")
    ses = dev.attach(pid)
    sc = ses.create_script(AGENT % rvas)
    sc.on("message", on_message)
    sc.load()
    done = threading.Event()
    ses.on("detached", lambda *x: done.set())
    dev.resume(pid)
    while not done.wait(2):
        if running("cs2.exe"):
            subprocess.run(["taskkill", "/F", "/PID", str(pid)], capture_output=True)
    while running("resourcecompiler.exe"):
        threading.Event().wait(2)
    out.close()
    print(out_path, "(hooked)" if hooked.is_set() else "(NEVER HOOKED)")
    if os.path.exists(backup):
        shutil.copyfile(backup, vpk)
        ok = filecmp.cmp(backup, vpk, shallow=False)
        print("restored", vpk, "(cmp ok)" if ok else "(CMP FAILED)")
        if ok:
            os.remove(backup)


if __name__ == "__main__":
    main()
