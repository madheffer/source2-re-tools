"""capture_texshift.py <addon> <map> [--out file]: which meshes take the texcoord island shift (OPEN 1.a5).

NodeOverlays.Recentre takes an overlay face's texcoords off by its box centre truncated toward zero, a rule
measured on atixref's 297 overlays with no code behind it. The one texcoord shift read in resourcecompiler is
HammerMesh_ShiftTexcoordIslands (0923 1810d93c0, called from ConvertMeshForBuilder), which shifts each UV island
by TexcoordIsland_Recentre (1813cc880: box centre (min + max) * 0.5, rounded half away from zero, unless the box
lies inside [0, 1]). This hooks both in a -world -fshallow compile and logs, per island call, the mesh object's
vtable (CHammerPolyMesh in 1.41.9.7), a backtrace, whether CMapStaticOverlay_GetOverlayDescs
(0923 181194f40) is running, the count and the texcoords before and
after. One JSON line per call. CS2 must be closed; the map's .vpk is backed up and restored, cmp-checked.
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

CS2 = os.environ.get("CS2_DIR", r"D:\Steam\steamapps\common\Counter-Strike Global Offensive")
BIN = os.path.join(CS2, "game", "bin", "win64")

AGENT = r"""
'use strict';
let current = null, calls = 0, inOverlay = 0;
function uvs(p, n) {
  const out = [];
  for (let i = 0; i < n && i < 256; i++) out.push([p.add(i * 8).readFloat(), p.add(i * 8 + 4).readFloat()]);
  return out;
}
function hook() {
  const m = Process.findModuleByName('resourcecompiler.dll');
  if (m === null) { setTimeout(hook, 5); return; }
  Interceptor.attach(m.base.add(%(islands)d), {
    onEnter(args) {
      const vt = args[0].readPointer();
      current = {mesh: args[0].toString(), vtable: '0x' + vt.sub(m.base).toString(16)};
      const bt = Thread.backtrace(this.context, Backtracer.ACCURATE).slice(0, 8)
        .map(a => { const mm = Process.findModuleByAddress(a); return mm ? mm.name.replace('.dll', '') + '+0x' + a.sub(mm.base).toString(16) : a.toString(); });
      send({ev: 'islands', mesh: current.mesh, vtable: current.vtable, overlay: inOverlay, stack: bt});
    },
    onLeave() { current = null; }
  });
  // CMapStaticOverlay_GetOverlayDescs (0923 181194f40): island calls made while it runs belong to an overlay.
  Interceptor.attach(m.base.add(%(descs)d), {
    onEnter(args) { inOverlay++; send({ev: 'descs', overlay: args[0].toString(), vtable: '0x' + args[0].readPointer().sub(m.base).toString(16)}); },
    onLeave() { inOverlay--; }
  });
  Interceptor.attach(m.base.add(%(recentre)d), {
    onEnter(args) {
      this.n = args[0].toInt32();
      this.p = args[1];
      try { this.before = uvs(this.p, this.n); } catch (e) { this.before = String(e); }
    },
    onLeave() {
      calls++;
      let after;
      try { after = uvs(this.p, this.n); } catch (e) { after = String(e); }
      const caller = this.returnAddress ? '0x' + this.returnAddress.sub(m.base).toString(16) : null;
      send({ev: 'recentre', call: calls, mesh: current ? current.mesh : null, vtable: current ? current.vtable : null,
            caller: caller, n: this.n, before: this.before, after: after});
    }
  });
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
    a = p.parse_args()
    if running("cs2.exe"):
        raise SystemExit("CS2 is running; not starting")
    if running("resourcecompiler.exe"):
        raise SystemExit("another resourcecompiler is running; not starting")
    if shutil.disk_usage(os.path.splitdrive(CS2)[0] + "\\").free < 10 * 1024 ** 3:
        raise SystemExit("under 10 GB free on the game drive; not starting")
    rvas = {"islands": installed("resourcecompiler", 0x10d93c0), "recentre": installed("resourcecompiler", 0x13cc880),
            "descs": installed("resourcecompiler", 0x1194f40)}
    out_path = a.out or os.path.join(os.environ.get("TEMP", "."), "texshift_capture", a.map + ".jsonl")
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
