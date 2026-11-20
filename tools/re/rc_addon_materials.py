"""rc_addon_materials.py <source addon> <probe addon> [--also <content path>]...: RC references for an
addon's materials.

Copies every file of content/csgo_addons/<source addon>/materials (and each --also path, a file
relative to that addon's content root, with its .txt sibling if any) into a new probe addon
content/csgo_addons/<probe addon>, then compiles every .vmat there with the installed
resourcecompiler (one -r wildcard run, -f, below-normal priority), so
game/csgo_addons/<probe addon> holds RC's output for exactly those sources. Then
`s2c compile-addon <probe addon> -n` reports which of our files are byte-identical ("same").

The probe addon must not exist yet (it is ours to delete afterwards: remove both its content
and game folders). Made for the porter's source1import vmats (GROUND_TRUTH 264). resourcecompiler
on its own touches no game process, so it may run with CS2 open (user, 2026-11-02); run it
through heavy.py.
"""
import ctypes
import os
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # paths.py
from paths import cs2_dir  # noqa: E402
CS2 = cs2_dir()
BIN = os.path.join(CS2, "game", "bin", "win64")


def main():
    args = sys.argv[1:]
    also = []
    while "--also" in args:
        i = args.index("--also")
        also.append(args[i + 1])
        del args[i:i + 2]
    if len(args) != 2:
        raise SystemExit(__doc__)
    source, probe = args
    if "resourcecompiler.exe" in subprocess.run(["tasklist"], capture_output=True, text=True).stdout.lower():
        raise SystemExit("a resourcecompiler is running; not starting")
    src = os.path.join(CS2, "content", "csgo_addons", source)
    dst = os.path.join(CS2, "content", "csgo_addons", probe)
    game = os.path.join(CS2, "game", "csgo_addons", probe)
    if os.path.exists(dst) or os.path.exists(game):
        raise SystemExit(f"{probe} exists; pick a new probe addon name")
    ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x4000)  # BELOW_NORMAL, inherited

    shutil.copytree(os.path.join(src, "materials"), os.path.join(dst, "materials"))
    for rel in also:
        for p in (rel, os.path.splitext(rel)[0] + ".txt"):
            s = os.path.join(src, *p.split("/"))
            if os.path.exists(s):
                os.makedirs(os.path.dirname(os.path.join(dst, *p.split("/"))), exist_ok=True)
                shutil.copyfile(s, os.path.join(dst, *p.split("/")))
    os.makedirs(game, exist_ok=True)

    cmd = [os.path.join(BIN, "resourcecompiler.exe"), "-nop4", "-f", "-r", "-game", os.path.join(CS2, "game", "csgo"),
           "-i", os.path.join(dst, "materials", "*.vmat")]
    r = subprocess.run(cmd, cwd=BIN, capture_output=True, text=True, errors="replace")
    log = os.path.join(game, "rc_addon_materials.log")
    with open(log, "w", encoding="utf-8") as f:
        f.write(r.stdout)
        f.write(r.stderr)
    made = sum(1 for d, _, n in os.walk(game) for x in n if x.endswith(".vmat_c"))
    print(f"rc exit {r.returncode}; {made} vmat_c in {game}; log {log}")


if __name__ == "__main__":
    main()
