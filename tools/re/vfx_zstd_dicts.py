"""Extract the zstd dictionaries CS2's VCS 72 shader files compress their bytecode with, from CS2's own DLLs.

The static combos' bytecode blocks are zstd frames made with a dictionary (frame dictionary ids 0x2bc2fa87 and
0x255df362). Each dictionary sits in materialsystem2.dll (and resourcecompiler.dll, vfxcompile.dll) as the 64 KB
buffer V_ZSTD_createDDict_byReference is handed: zstd dictionary magic 0xec30a437, then the id.

usage: python tools/re/vfx_zstd_dicts.py [--check <dir with vfx_zstd_<id>.bin>] [--out <dir>]
       CS2_DIR picks the install (default: found from Steam, tools/re/paths.py).
"""
import argparse
import os
import struct
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # paths.py
from paths import cs2_dir  # noqa: E402
CS2 = Path(cs2_dir())
DLLS = ["game/bin/win64/materialsystem2.dll", "game/bin/win64/resourcecompiler.dll", "game/bin/win64/vfxcompile.dll"]
IDS = [0x2BC2FA87, 0x255DF362]
SIZE = 0x10000


def find(dll: bytes, did: int) -> list[bytes]:
    needle = struct.pack("<II", 0xEC30A437, did)
    found, at = [], dll.find(needle)
    while at >= 0:
        found.append(dll[at:at + SIZE])
        at = dll.find(needle, at + 1)
    return found


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", help="directory holding vfx_zstd_<id>.bin to compare")
    ap.add_argument("--out", help="directory to write vfx_zstd_<id>.bin to")
    a = ap.parse_args()
    bad = 0
    for did in IDS:
        copies = {}
        for rel in DLLS:
            path = CS2 / rel
            if path.exists():
                for i, d in enumerate(find(path.read_bytes(), did)):
                    copies[f"{rel}#{i}"] = d
        if not copies:
            print(f"{did:08x}: not found in {', '.join(DLLS)}")
            bad += 1
            continue
        distinct = set(copies.values())
        print(f"{did:08x}: {len(copies)} copies ({', '.join(copies)}), {len(distinct)} distinct")
        if len(distinct) != 1:
            bad += 1
            continue
        data = distinct.pop()
        name = f"vfx_zstd_{did:08x}.bin"
        if a.out:
            Path(a.out, name).write_bytes(data)
        if a.check:
            mine = Path(a.check, name).read_bytes()
            same = mine == data
            print(f"  {name}: {'identical' if same else 'DIFFERS'} to CS2's")
            bad += 0 if same else 1
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
