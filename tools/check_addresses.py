"""check_addresses.py [--bin DIR]... [--csgo DIR] [docs...]: every Functions-table address checked against its DLL.

A trace doc names its builds in its first lines (server_20261105, client_20261015, ...; a CS:GO doc names its DLLs
by md5) and lists functions as `| <address> | <module> | <what> |`. Each address must be code in that module's
build: a function start (.pdata begin on x64; on x86, code after padding or a ret), or, as a call site or a branch
target, inside a function ("mid"). A row whose own text names a build (client_20261105) is checked against that one.

  --bin DIR   a folder of archived builds, <dll>_<yyyymmdd>.dll (repeatable; S2C_BINARIES and tools/re/binaries
              are searched too)
  --csgo DIR  the CS:GO legacy install (bin/vphysics.dll, bin/engine.dll, csgo/bin/server.dll, csgo/bin/client.dll)

Prints per doc the counts (start / mid / bad / unchecked) and every bad or unchecked row; exits 1 on any bad one.
"""
import bisect
import glob
import hashlib
import os
import re
import sys

import pefile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
BUILD = re.compile(r"\b([a-z][a-z0-9]+)_(20\d{6})\b")
ADDR = re.compile(r"(?<![0-9A-Za-z])(?:0x)?(1[0-9a-f]{7,9})(?![0-9A-Za-z])")
CSGO_FILES = {"vphysics": "bin/vphysics.dll", "engine": "bin/engine.dll",
              "server": "csgo/bin/server.dll", "client": "csgo/bin/client.dll"}
_pe = {}


class Image:
    def __init__(self, path):
        self.path = path
        pe = pefile.PE(path, fast_load=True)
        pe.parse_data_directories([3])  # exception directory (.pdata)
        self.base = pe.OPTIONAL_HEADER.ImageBase
        self.size = pe.OPTIONAL_HEADER.SizeOfImage
        self.x64 = pe.FILE_HEADER.Machine == 0x8664
        self.exec = [(self.base + s.VirtualAddress, self.base + s.VirtualAddress + max(s.Misc_VirtualSize, s.SizeOfRawData))
                     for s in pe.sections if s.Characteristics & 0x20000000]
        self.img = pe.get_memory_mapped_image()
        self.funcs = []
        for e in getattr(pe, "DIRECTORY_ENTRY_EXCEPTION", []) or []:
            self.funcs.append((self.base + e.struct.BeginAddress, self.base + e.struct.EndAddress))
        self.funcs.sort()
        self.starts = [f[0] for f in self.funcs]
        with open(path, "rb") as f:
            self.md5 = hashlib.md5(f.read()).hexdigest()

    def classify(self, va):
        if not any(a <= va < b for a, b in self.exec):
            # a vtable, a global, a constant table or an import slot listed beside the functions
            return "data" if self.base <= va < self.base + self.size else "bad"
        if self.funcs:
            i = bisect.bisect_right(self.starts, va) - 1
            if i >= 0 and self.starts[i] == va:
                return "start"
            if i >= 0 and self.funcs[i][0] <= va < self.funcs[i][1]:
                return "mid"
            # a leaf function has no .pdata entry: a start after int3 / nop padding or a ret
            prev = self.img[va - self.base - 1]
            return "start" if prev in (0xcc, 0x90, 0xc3) else "mid?"
        prev = self.img[va - self.base - 1] if va - self.base >= 1 else 0
        return "start" if prev in (0xcc, 0x90, 0xc3) or va % 16 == 0 else "mid"


def image(path):
    if path not in _pe:
        _pe[path] = Image(path)
    return _pe[path]


def find_build(dirs, dll, build):
    for d in dirs:
        p = os.path.join(d, f"{dll}_{build}.dll")
        if os.path.exists(p):
            return p
    return None


def main(argv):
    dirs, csgo, docs = [], None, []
    it = iter(argv)
    for a in it:
        if a == "--bin":
            dirs.append(next(it))
        elif a == "--csgo":
            csgo = next(it)
        else:
            docs.append(a)
    dirs += [os.environ.get("S2C_BINARIES", ""), os.path.join(HERE, "re", "binaries")]
    dirs = [d for d in dirs if d and os.path.isdir(d)]
    docs = docs or sorted(glob.glob(os.path.join(REPO, "docs", d, "*.md")) for d in ("game", "csgo", "crazykart"))
    docs = [p for group in docs for p in (group if isinstance(group, list) else [group])]
    total = {"start": 0, "mid": 0, "mid?": 0, "data": 0, "bad": 0, "unchecked": 0}
    for doc in docs:
        text = open(doc, encoding="utf-8").read()
        if os.path.basename(doc) == "README.md" and "## General helpers in " not in text:
            continue
        head = "\n".join(text.split("\n")[:6])
        is_csgo = "/csgo/" in doc.replace("\\", "/") or "/crazykart/" in doc.replace("\\", "/")
        builds = {}
        for dll, b in BUILD.findall(head):
            builds.setdefault(dll, []).append(b)
        counts = {k: 0 for k in total}
        notes = []
        helper = None  # a README's "## General helpers in <dll>.dll (<build or date>)": its 2-column rows
        for line in text.split("\n"):
            if line.startswith("## "):
                m = re.match(r"## General helpers in (\w+)\.dll \(([^)]*)\)", line)
                helper = None
                if m:
                    b = BUILD.search(m.group(2))
                    d = re.search(r"(20\d\d)-(\d\d)-(\d\d)", m.group(2))
                    build = b.group(2) if b else (d.group(1) + d.group(2) + d.group(3) if d and "install" not in m.group(2) else None)
                    helper = (m.group(1), build)
                    if build:
                        builds = {m.group(1): [build]}
                continue
            cols = [c.strip() for c in line.strip().strip("|").split("|")]
            if not line.startswith("|"):
                continue
            if helper and len(cols) == 2:
                # a row naming another module or build ("client 0x...", "(scenesystem 1112)") is not this section's
                if re.search(r"[g-wyz]", cols[0].lower().replace("0x", "")):
                    continue
                cols = [cols[0], helper[0], cols[1]]
            if len(cols) < 3:
                continue
            module = cols[1].lower()
            addrs = ADDR.findall(cols[0])
            if not addrs or not re.fullmatch(r"[a-z0-9]+", module) or module in ("module", "offset"):
                continue
            paths = []
            if is_csgo:
                if csgo and module in CSGO_FILES and os.path.exists(os.path.join(csgo, CSGO_FILES[module])):
                    paths = [os.path.join(csgo, CSGO_FILES[module])]
            else:
                own = [b for d_, b in BUILD.findall(line) if d_ == module]
                for b in own or builds.get(module, []):
                    p = find_build(dirs, module, b)
                    if p:
                        paths.append(p)
            for a in addrs:
                va = int(a, 16)
                if not paths:
                    counts["unchecked"] += 1
                    notes.append(f"  unchecked {a} {module}: no build here ({', '.join(builds.get(module, [])) or 'none named'})")
                    continue
                kinds = [image(p).classify(va) for p in paths]
                best = min(kinds, key=["start", "mid", "mid?", "data", "bad"].index)
                counts[best] += 1
                if best in ("bad", "mid?"):
                    names = ", ".join(os.path.basename(p) for p in paths)
                    notes.append(f"  {best} {a} {module} ({names}): {cols[2][:90]}")
        for k in total:
            total[k] += counts[k]
        if any(counts.values()):
            rel = os.path.relpath(doc, REPO)
            print(f"{rel}: " + " ".join(f"{k} {v}" for k, v in counts.items() if v))
            for n in notes:
                print(n)
    print("total: " + " ".join(f"{k} {v}" for k, v in total.items()))
    return 1 if total["bad"] else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
