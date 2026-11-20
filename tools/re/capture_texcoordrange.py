"""capture_texcoordrange.py <addon> <map> [--out file]: ConvertMeshForBuilder's texcoord range tests.

What decides a map mesh's forceHighPrecisionTexcoords (ledger 44): ConvertMeshForBuilder (rc 0923 1810dff20)
calls HammerMesh_TexcoordsOutOfRange (1810e7020, +-1.03125) before the island shift (1810e05a6's test) and
again after it, and HammerMesh_ShiftTexcoordIslands (1810d93c0) between them when the first answers true.
Each call is logged in order with its return address (which of the two calls), its answer, and the range
(min, max over u and v) of every enabled two-float slot of the mesh's face-vertex grid (count +0x248 + 3 * slot
qwords, data the pointer after it, enabled byte +0x1234 + slot), so a mesh can be matched by its texcoords.
Addresses are the 0923 build's, moved to the installed one by rva_map. One JSON line per event; a -world
-fshallow compile; CS2 must be closed, and the map's package is backed up and restored, cmp-checked.
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

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # paths.py
from paths import cs2_dir  # noqa: E402
CS2 = cs2_dir()
BIN = os.path.join(CS2, "game", "bin", "win64")
OUT_OF_RANGE = 0x10e7020
SHIFT = 0x10d93c0
CONVERT = 0x10dff20

AGENT = r"""
'use strict';
function ranges(mesh) {
  const out = [];
  for (let slot = 0; slot < 6; slot++) {
    try {
      if (mesh.add(0x1234 + slot).readU8() === 0) continue;
      const rec = mesh.add((slot * 3 + 0x248) * 8), n = rec.readS32();
      if (n <= 0 || n > 10000000) continue;
      const p = rec.add(8).readPointer();
      let lo = 1e30, hi = -1e30;
      for (let i = 0; i < n * 2; i++) { const f = p.add(i * 4).readFloat(); if (f < lo) lo = f; if (f > hi) hi = f; }
      const vals = [];
      for (let i = 0; i < Math.min(n * 2, %(dump)d); i++) vals.push(p.add(i * 4).readFloat());
      out.push([slot, n, lo, hi, vals]);
    } catch (e) {}
  }
  return out;
}
function hook() {
  const mod = Process.findModuleByName('resourcecompiler.dll');
  if (mod === null) { setTimeout(hook, 5); return; }
  send({ev: 'hooked'});
  let convert = 0;
  Interceptor.attach(mod.base.add(%(convert)d), { onEnter() { convert++; } });
  Interceptor.attach(mod.base.add(%(range)d), {
    onEnter(args) { this.mesh = args[0]; this.ret = this.returnAddress.sub(mod.base).toInt32(); this.before = ranges(args[0]); },
    onLeave(r) { send({ev: 'range', convert: convert, ret: this.ret, answer: r.toInt32() & 0xff, slots: this.before}); }
  });
  Interceptor.attach(mod.base.add(%(shift)d), {
    onEnter(args) { this.ret = this.returnAddress.sub(mod.base).toInt32(); },
    onLeave() { send({ev: 'shift', convert: convert, ret: this.ret}); }
  });
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
    p.add_argument("--dump", type=int, default=0, help="also log this many floats of each slot")
    a = p.parse_args()
    if running("cs2.exe") or running("resourcecompiler.exe"):
        raise SystemExit("CS2 or a compile is running; not starting")
    out_path = a.out or os.path.join(os.environ.get("TEMP", "."), "texcoordrange", a.map + ".jsonl")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    vpk = os.path.join(CS2, "game", "csgo_addons", a.addon, "maps", a.map + ".vpk")
    backup = out_path + ".vpk.bak"
    if os.path.exists(vpk):
        shutil.copy2(vpk, backup)
        os.remove(vpk)  # a current package makes RC skip the compile
    out = open(out_path, "w", encoding="utf-8")
    lock = threading.Lock()
    stats = {}

    def on_message(msg, data):
        if msg.get("type") != "send":
            print("agent:", msg.get("description") or msg, file=sys.stderr)
            return
        pay = msg["payload"]
        stats[pay["ev"]] = stats.get(pay["ev"], 0) + 1
        with lock:
            out.write(json.dumps(pay) + "\n")

    source = os.path.join(CS2, "content", "csgo_addons", a.addon, "maps", a.map + ".vmap")
    cmd = [os.path.join(BIN, "resourcecompiler.exe"), "-nop4", "-game", os.path.join(CS2, "game", "csgo"), "-i", source,
           "-world", "-fshallow"]
    dev = frida.get_local_device()
    pid = dev.spawn(cmd, cwd=BIN, stdio="pipe")
    ses = dev.attach(pid)
    sc = ses.create_script(AGENT % {"range": installed("resourcecompiler", OUT_OF_RANGE, "20260923"),
                                    "shift": installed("resourcecompiler", SHIFT, "20260923"),
                                    "convert": installed("resourcecompiler", CONVERT, "20260923"), "dump": a.dump})
    sc.on("message", on_message)
    sc.load()
    done = threading.Event()
    ses.on("detached", lambda *x: done.set())
    dev.resume(pid)
    killed = False
    while not done.wait(2):
        if running("cs2.exe"):
            subprocess.run(["taskkill", "/F", "/PID", str(pid)], capture_output=True)
            killed = True
    out.close()
    print(out_path, stats, "(killed: cs2 started)" if killed else "")
    if os.path.exists(vpk):
        shutil.copyfile(vpk, out_path + ".vpk")
    if os.path.exists(backup):
        shutil.copy2(backup, vpk)
        ok = filecmp.cmp(backup, vpk, shallow=False)
        print("restored", vpk, "(cmp ok)" if ok else "(CMP FAILED)")
        if ok:
            os.remove(backup)


if __name__ == "__main__":
    main()
