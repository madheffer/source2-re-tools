"""check_fields.py [--bin DIR]... [docs...]: schema field offsets in the trace docs checked against the DLL's schema.

Pairs a schema name with an offset where a doc writes them together: a table row with one `m_` name and one `+0x..`
offset, or text like `m_flFlinchStack +0x14dc` / `+0x14dc m_flFlinchStack` / `m_hPawn (+0x4e0)`. Each pair is
looked up in the schema binding tables (tools/re/game/schema.py's walk) of every server / client build the doc's
header names (a row naming its own build uses that). A name can sit in several classes at different offsets: a
pair passes when the offset is one of them.

Prints the mismatches (name found, offset not among its offsets) and the count of names not in any schema (the
decompiler's names, CS:GO's, unschema'd fields); exits 1 on a mismatch.
"""
import glob
import os
import re
import struct
import sys

import numpy as np
import pefile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
BUILD = re.compile(r"\b(server|client)_(20\d{6})\b")
NAME = r"(m_[A-Za-z0-9_]+)"
OFF = r"\+(0x[0-9a-fA-F]+)"
PAIRS = [re.compile(NAME + r"\s*\(?(?:[a-z]+\s)?" + OFF), re.compile(OFF + r"\)?\s+" + NAME)]
_schema = {}


def schema(path):
    """{field name: set of offsets} over every schema field entry in the DLL."""
    if path in _schema:
        return _schema[path]
    pe = pefile.PE(path, fast_load=True)
    base = pe.OPTIONAL_HEADER.ImageBase
    img = pe.get_memory_mapped_image()
    names = {}
    for m in re.finditer(rb"(?<=\x00)m_[A-Za-z0-9_]{1,60}\x00", img):
        names[base + m.start()] = m.group()[:-1].decode()
    out = {}
    # an entry is { name*, type*, int32 offset, ... }: every 8-aligned qword that points at a name, its int32 16 on
    data = bytes(img)
    n = (len(data) - 24) // 8
    q = np.frombuffer(data, dtype="<u8", count=n)
    keys = np.fromiter(names.keys(), dtype=np.uint64)
    hits = np.nonzero(np.isin(q, keys))[0]
    for h in hits:
        i = int(h) * 8
        off = struct.unpack_from("<i", data, i + 16)[0]
        if 0 <= off < 0x100000:
            out.setdefault(names[int(q[h])], set()).add(off)
    _schema[path] = out
    return out


def find_build(dirs, dll, build):
    for d in dirs:
        p = os.path.join(d, f"{dll}_{build}.dll")
        if os.path.exists(p):
            return p
    return None


def main(argv):
    dirs, docs = [], []
    it = iter(argv)
    for a in it:
        if a == "--bin":
            dirs.append(next(it))
        else:
            docs.append(a)
    dirs += [os.environ.get("S2C_BINARIES", ""), os.path.join(HERE, "re", "binaries")]
    dirs = [d for d in dirs if d and os.path.isdir(d)]
    docs = docs or sorted(glob.glob(os.path.join(REPO, "docs", "game", "*.md")))
    checked = bad = unknown = 0
    for doc in docs:
        if os.path.basename(doc) == "README.md":
            continue
        text = open(doc, encoding="utf-8").read()
        head = "\n".join(text.split("\n")[:6])
        builds = [find_build(dirs, d, b) for d, b in BUILD.findall(head)]
        builds = [p for p in builds if p]
        if not builds:
            continue
        rel = os.path.relpath(doc, REPO)
        for n, line in enumerate(text.split("\n"), 1):
            pairs = set()
            if line.startswith("|"):
                names, offs = re.findall(NAME, line), re.findall(OFF, line)
                if len(set(names)) == 1 and len(set(offs)) == 1:
                    pairs.add((names[0], offs[0]))
            for p in PAIRS:
                for m in p.finditer(line):
                    a, b = m.groups()
                    pairs.add((a, b) if a.startswith("m_") else (b, a))
            own = [find_build(dirs, d, b) for d, b in BUILD.findall(line)]
            paths = [p for p in own if p] or builds
            for name, off in pairs:
                offs = set()
                for p in paths:
                    offs |= schema(p).get(name, set())
                if not offs:
                    unknown += 1
                    continue
                checked += 1
                # a nested field: the offset from an outer object, through an embedded struct the doc also names
                # (m_iDamage +0x104 = m_matchStats +0xc8 + m_iDamage +0x3c)
                outer = set()
                for other in set(re.findall(NAME, text)) - {name}:
                    for p in paths:
                        outer |= schema(p).get(other, set())
                if int(off, 16) not in offs and not any(int(off, 16) - o in outer for o in offs):
                    bad += 1
                    have = ", ".join(hex(o) for o in sorted(offs))
                    print(f"{rel}:{n}: {name} +{off} not in schema ({have}) [{', '.join(os.path.basename(p) for p in paths)}]")
    print(f"checked {checked}, mismatched {bad}, not in schema {unknown}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
