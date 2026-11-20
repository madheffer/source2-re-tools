"""capture_missingmaterial.py <addon> <map> [--match REGEX] [--out file]: what a material the content lacks
resolves to (OPEN 1.c5, GROUND_TRUTH 42, CS2_CLOSED_QUEUE A.10).

cardtest's teleport02 lives in another addon, yet at collect time Valve gives it attribute flags
0x160100000 and a 256x256 representative texture. WRB_MeshEntryFlags (0923 180252ae0) loads a mesh's
material through 1801d4dc0 (names, count, out vector): each name gets ".vmat" (0x74616d76) and the
resource system's vf 0x70 returns a handle, stored in the out vector; element 0 is what the flags read,
and only a null one warns "Cannot load". This hooks 1801d4dc0 in a -world -fshallow compile and logs, per
call, the names and the handles; for names matching --match also the handle's target, the resource
name strings near it and the first 0x80 bytes of both. CS2 must be closed; the package is backed up and
restored, cmp-checked.
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

AGENT = r"""
'use strict';
const MATCH = new RegExp(%(match)s, 'i');
function cstr(p) { try { return p.isNull() ? "" : p.readCString(); } catch (e) { return null; } }
function hex(p, n) { try { return Array.from(new Uint8Array(p.readByteArray(n))).map(b => b.toString(16).padStart(2, '0')).join(''); } catch (e) { return null; } }
// Printable strings at, or one pointer from, the first 0x200 bytes of p.
function strings(p) {
  const out = [];
  for (let o = 0; o < 0x200; o += 8) {
    try {
      const q = p.add(o).readPointer();
      let s = cstr(q);
      if (s !== null && /^[ -~]{4,}$/.test(s)) out.push(o.toString(16) + ':' + s);
      for (let o2 = 0; o2 < 0x20; o2 += 8) {
        s = cstr(q.add(o2).readPointer());
        if (s !== null && /^[ -~]{4,}$/.test(s) && /[\/.]/.test(s)) out.push(o.toString(16) + '.' + o2.toString(16) + ':' + s);
      }
    } catch (e) {}
  }
  return out.slice(0, 40);
}
// GROUND_TRUTH 42 / ledger 40: the material's own answers for the entry keys (CMaterial2 vf 0x48,
// GetBoolAttribute(this, bool *out, key)), its vtable's module, the attribute block at +0x180 (12 keys, values
// at +0x30) and the parent block pointer at +0x1e0 (block +0x60) with the same keys read from it.
const KEYS = {AllowBackfaceCulling: 0x3ed9fd4a, SupportsLightmapping: 0xfff20b87,
              SupportsAggregateInstancing: 0x67d9d859, NeedsLightProbe: 0x9885dce5};
function where(p) { const m = Process.findModuleByAddress(p); return m ? m.name + '+' + p.sub(m.base).toString(16) : p.toString(); }
function block(b) {
  const keys = [];
  for (let i = 0; i < 12; i++) keys.push(b.add(i * 4).readU32().toString(16) + '=' + b.add(0x30 + i * 4).readU32().toString(16));
  return {keys: keys, chain: b.add(0x68).readPointer().toString(), parent: b.add(0x60).readPointer().toString()};
}
// Where each entry key sits: the block at b and its chain (+0x68), up to 64 blocks, as "link:slot=value".
function locate(b) {
  const at = {};
  for (let link = 0; link < 64 && !b.isNull(); link++) {
    for (let i = 0; i < 12; i++) {
      const k = b.add(i * 4).readU32();
      for (const [name, key] of Object.entries(KEYS))
        if (k === key && !(name in at)) at[name] = link + ':' + i + '=' + b.add(0x30 + i * 4).readU32().toString(16);
    }
    b = b.add(0x68).readPointer();
  }
  return at;
}
function attrs(t) {
  const out = {};
  try {
    const vt = t.readPointer();
    out.vtable = where(vt);
    const get = new NativeFunction(vt.add(0x48).readPointer(), 'uint8', ['pointer', 'pointer', 'uint32']);
    const box = Memory.alloc(8);
    for (const [name, key] of Object.entries(KEYS)) {
      box.writeU64(0);
      const found = get(t, box, key);
      out[name] = {found: found, value: box.readU8()};
    }
    out.block = block(t.add(0x180));
    out.own = locate(t.add(0x180));
    const parent = t.add(0x1e0).readPointer();
    out.parentAt = where(parent);
    if (!parent.isNull()) { out.parent = block(parent); out.parentHead = hex(parent, 0x80); out.inParent = locate(parent); }
    // The refcounted object CMaterial2's constructor (18003abf0) stores at +0x60 (its fifth argument).
    const owner = t.add(0x60).readPointer();
    out.owner = where(owner);
    if (!owner.isNull()) { out.ownerVtable = where(owner.readPointer()); out.ownerStrings = strings(owner).slice(0, 12); }
  } catch (err) { out.err = String(err); }
  return out;
}
const pending = [];
let late = 0;
function hook() {
  const mod = Process.findModuleByName('resourcecompiler.dll');
  if (mod === null) { setTimeout(hook, 5); return; }
  // The same handles again when WRB_MeshEntryFlags returns, by which time the resource has loaded.
  Interceptor.attach(mod.base.add(%(flags)d), {
    onLeave() {
      late++;
      for (const p of pending) {
        try {
          const t = p.handle.readPointer(), a = attrs(t), key = t.toString() + JSON.stringify(a);
          if (key !== p.last) { p.last = key; send({stage: 'late', call: late, name: p.name, target: t.toString(), attrs: a}); }
        } catch (err) { send({stage: 'late', name: p.name, err: String(err)}); }
      }
    }
  });
  Interceptor.attach(mod.base.add(%(load)d), {
    onEnter(args) {
      this.n = args[1].toInt32();
      this.out = args[2];
      this.names = [];
      for (let i = 0; i < this.n && i < 64; i++) this.names.push(cstr(args[0].add(i * 8).readPointer()));
    },
    onLeave() {
      const n = this.out.readS32(), data = this.out.add(8).readPointer();
      const e = {names: this.names, handles: []};
      let want = this.names.some(s => s !== null && MATCH.test(s));
      for (let i = 0; i < n && i < 64; i++) {
        const h = data.add(i * 8).readPointer();
        const r = {handle: h.toString()};
        if (want && !h.isNull()) {
          r.head = hex(h, 0x80);
          r.strings = strings(h);
          try {
            const t = h.readPointer();
            r.target = t.toString();
            r.targetHead = hex(t, 0x80);
            r.targetStrings = strings(t);
            r.attrs = attrs(t);
            if (pending.length < %(pending)d) pending.push({name: this.names[i] || this.names[0], handle: h});
          } catch (err) { r.err = String(err); }
        }
        e.handles.push(r);
      }
      send(e);
    }
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
    p.add_argument("--match", default="teleport|error")
    p.add_argument("--out")
    p.add_argument("--flags-rva", type=lambda x: int(x, 16),
                   help="WRB_MeshEntryFlags in the installed build when rva_map refuses it (1.41.9.7: 253940, only __LINE__ 0x248 -> 0x228 differs)")
    p.add_argument("--pending", type=int, default=16, help="handles re-read after every WRB_MeshEntryFlags")
    a = p.parse_args()
    if running("cs2.exe"):
        raise SystemExit("CS2 is running; not starting")
    if running("resourcecompiler.exe"):
        raise SystemExit("another resourcecompiler is running; not starting")
    if shutil.disk_usage(os.path.splitdrive(CS2)[0] + "\\").free < 10 * 1024 ** 3:
        raise SystemExit("under 10 GB free on the game drive; not starting")
    rvas = {"load": installed("resourcecompiler", 0x1d4dc0), "flags": a.flags_rva or installed("resourcecompiler", 0x252ae0), "match": json.dumps(a.match), "pending": a.pending}
    out_path = a.out or os.path.join(os.environ.get("TEMP", "."), "missingmaterial_capture", a.map + ".jsonl")
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
