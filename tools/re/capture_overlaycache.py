"""capture_overlaycache.py <addon> <map> [--out file]: the overlay projection cache as the projector leaves it (OPEN 1.a5).

CMapStaticOverlay_GetOverlayDescs (0923 181194f40) copies each face from 0x4a0-byte records of the overlay's
projection cache (per material 0xf8 apart: face count +0, faces +8; per face texcoords +0x100 count, +0x108 data;
positions +0x28 / +0x30), which per-target jobs (run 18119bac0) fill through the projector 18124f000 (mode 3) or
18124f860, the record as the first argument. This hooks both projectors and, on exit, walks the record: it tries
the material vector at record +8, +0x10, +0x18 and +0x78 and keeps the first that validates, then logs every
face's positions and texcoords. OverlayShiftProbe (TEXSHIFT_CACHE) compares them with the .vmap's raw texcoords:
shifted here means the projector (or its callees) applies the shift. CS2 must be closed; the map's .vpk is backed
up and restored, cmp-checked. The installed RVAs are checked against the 0923 code (rva_map / insdiff.py).
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import threading

import frida

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from package_guard import PackageGuard  # noqa: E402
from rva_map import installed  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # paths.py
from paths import cs2_dir  # noqa: E402
CS2 = cs2_dir()
BIN = os.path.join(CS2, "game", "bin", "win64")

AGENT = r"""
'use strict';
function vec(p) { return {n: p.readS32(), data: p.add(8).readPointer()}; }
function faces(mat) {
  const f = vec(mat), out = [];
  if (f.n < 0 || f.n > 20000 || f.data.isNull()) return null;
  for (let i = 0; i < f.n; i++) {
    const face = f.data.add(i * 0x4a0), uv = vec(face.add(0x100)), pos = vec(face.add(0x28));
    if (uv.n < 0 || uv.n > 256 || pos.n < 0 || pos.n > 256) return null;
    const t = [], q = [];
    for (let k = 0; k < uv.n; k++) t.push([uv.data.add(k * 8).readFloat(), uv.data.add(k * 8 + 4).readFloat()]);
    for (let k = 0; k < pos.n; k++) q.push([pos.data.add(k * 12).readFloat(), pos.data.add(k * 12 + 4).readFloat(), pos.data.add(k * 12 + 8).readFloat()]);
    out.push({uv: t, pos: q});
  }
  return out;
}
function walk(rec) {
  for (const off of [8, 0x10, 0x18, 0x78]) {
    try {
      const m = vec(rec.add(off));
      if (m.n < 1 || m.n > 64 || m.data.isNull()) continue;
      const mats = [];
      let ok = true;
      for (let i = 0; i < m.n && ok; i++) { const f = faces(m.data.add(i * 0xf8)); if (f === null) ok = false; else mats.push(f); }
      if (ok) return {off: off, mats: mats};
    } catch (e) {}
  }
  return null;
}
function hook() {
  const m = Process.findModuleByName('resourcecompiler.dll');
  if (m === null) { setTimeout(hook, 5); return; }
  for (const [name, rva] of [['mode3', %(mode3)d], ['other', %(other)d]]) {
    Interceptor.attach(m.base.add(rva), {
      onEnter(args) { this.rec = args[0]; },
      onLeave() {
        let w = null, head = null;
        try { w = walk(this.rec); head = Array.from(new Uint8Array(this.rec.readByteArray(0xa0))).map(b => b.toString(16).padStart(2, '0')).join(''); } catch (e) {}
        send({ev: name, rec: this.rec.toString(), cache: w, head: w === null ? head : undefined});
      }
    });
  }
  send({ev: 'hooked'});
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
    # 18124f000's primary chunk is 0x2f bytes, so rva_map's 64-byte window refuses it; 1.41.9.7's copy at
    # 0x1250120 has the same 0x18 prologue bytes and equal code over 2,140 bytes (insdiff.py).
    p.add_argument("--mode3-rva", type=lambda x: int(x, 16), default=0x1250120)
    a = p.parse_args()
    if running("cs2.exe"):
        raise SystemExit("CS2 is running; not starting")
    if running("resourcecompiler.exe"):
        raise SystemExit("another resourcecompiler is running; not starting")
    if shutil.disk_usage(os.path.splitdrive(CS2)[0] + "\\").free < 10 * 1024 ** 3:
        raise SystemExit("under 10 GB free on the game drive; not starting")
    rvas = {"mode3": a.mode3_rva, "other": installed("resourcecompiler", 0x124f860)}
    out_path = a.out or os.path.join(os.environ.get("TEMP", "."), "overlaycache_capture", a.map + ".jsonl")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    vpk = os.path.join(CS2, "game", "csgo_addons", a.addon, "maps", a.map + ".vpk")
    source = os.path.join(CS2, "content", "csgo_addons", a.addon, "maps", a.map + ".vmap")
    argv = [os.path.join(BIN, "resourcecompiler.exe"), "-nop4", "-game", os.path.join(CS2, "game", "csgo"),
            "-i", source, "-world", "-fshallow"]
    out = open(out_path, "w")
    lock = threading.Lock()
    hooked = threading.Event()

    def on_message(msg, _data):
        if msg.get("type") != "send":
            print("agent:", msg.get("description") or msg)
        elif msg["payload"].get("ev") == "hooked":
            hooked.set()
        else:
            with lock:
                out.write(json.dumps(msg["payload"]) + "\n")

    with PackageGuard(vpk, out_path + ".vpk.bak") as guard:
        dev = frida.get_local_device()
        pid = dev.spawn(argv, cwd=BIN, stdio="pipe")
        guard.pid = pid
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
    out.close()
    print(out_path, "(hooked)" if hooked.is_set() else "(NEVER HOOKED)")


if __name__ == "__main__":
    main()
