"""classify_changes.py <old.dll> <new.dll> <build_diff.txt> <out.txt>: sorts build_diff's same-size "changed" pairs by
what differs per instruction: image addresses (tables, callees, data), small immediates moved by exactly 0x20
(__LINE__ shifts from an edited header, the 1.41.9.7 case), switch-table bytes decoded as junk; the rest is
written to <out.txt> with its differing lines (the ones worth reading). Counts: tables, desc228 (line shifts), other."""
import re, sys, pefile, capstone
old = pefile.PE(sys.argv[1], fast_load=True); new = pefile.PE(sys.argv[2], fast_load=True)
ob, nb = old.OPTIONAL_HEADER.ImageBase, new.OPTIONAL_HEADER.ImageBase
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64)
rip = re.compile(r"\[rip [+-] 0x[0-9a-f]+\]")
imm = re.compile(r"0x[0-9a-f]+")
pairs = []
for l in open(sys.argv[3], encoding="utf-8", errors="replace"):
    m = re.match(r"  changed 0x([0-9a-f]+) -> 0x([0-9a-f]+)\s+(\d+) -> (\d+) bytes.*?differ\s*(.*)$", l.rstrip("\n"))
    if m and m.group(3) == m.group(4):
        pairs.append((int(m.group(1), 16), int(m.group(2), 16), int(m.group(3)), m.group(5)))
counts = {"tables": 0, "desc228": 0, "mixed-benign": 0, "other": 0}
out = open(sys.argv[4], "w", encoding="utf-8")
for oa, na, n, label in pairs:
    oi = list(md.disasm(old.get_data(oa - ob, n), oa)); ni = list(md.disasm(new.get_data(na - nb, n), na))
    shift = na - oa
    kinds = set(); lines = []
    if len(oi) != len(ni):
        kinds.add("junk")
    for a, b in zip(oi, ni):
        sa, sb = rip.sub("[rip]", a.op_str), rip.sub("[rip]", b.op_str)
        if a.mnemonic.startswith("j") or a.mnemonic == "call":
            try:
                ta, tb = int(a.op_str, 16), int(b.op_str, 16)
                if tb - ta == shift or (ob < ta < ob + old.OPTIONAL_HEADER.SizeOfImage and nb < tb < nb + new.OPTIONAL_HEADER.SizeOfImage and not (oa <= ta < oa + n)):
                    continue
            except ValueError:
                pass
        if a.mnemonic == b.mnemonic and sa == sb:
            continue
        ia, ib = imm.findall(sa), imm.findall(sb)
        if a.mnemonic == b.mnemonic and imm.sub("#", sa) == imm.sub("#", sb):
            d = [(int(x, 16), int(y, 16)) for x, y in zip(ia, ib) if x != y]
            size = old.OPTIONAL_HEADER.SizeOfImage
            def addr(v):
                return 0x1000 <= v < size or ob + 0x1000 <= v < ob + size
            if d and all(addr(x) and addr(y) for x, y in d):
                kinds.add("tables"); continue
            if d and all(x - y == 0x20 and x < 0x4000 for x, y in d):
                kinds.add("desc228"); continue
        # Bytes inside an inline jump table decode as junk instructions.
        if a.mnemonic in ("and", "or", "add", "sbb", "adc", "xor", "in", "out", "lodsd", "sti", "cli", "movabs", "push", "pop", "jmp", "ljmp", "lcall", "fild", "fadd", "hlt", "outsd", "insd", "enter", "retf", "wait", "stosb", "fldcw", "test", "jbe", "jo", "jb", "ja", "fld", "imul", "outsb", "loop", "cmp", "mov", "sub", "lea", "jne", "je", "iretd", "int3", "cmc", "cdq", "xchg", "stc", "clc") and ("tables" in kinds or "junk" in kinds or len(oi) != len(ni)):
            kinds.add("junk"); continue
        kinds.add("other"); lines.append("   %x %-8s %-44s | %x %-8s %s" % (a.address, a.mnemonic, a.op_str, b.address, b.mnemonic, b.op_str))
    if "other" in kinds:
        counts["other"] += 1
        out.write("%x -> %x (%d) %s\n" % (oa, na, n, label[:150]))
        out.write("\n".join(lines[:6]) + "\n")
    elif kinds == {"desc228"}:
        counts["desc228"] += 1
    elif kinds <= {"tables", "junk"}:
        counts["tables"] += 1
    else:
        counts["mixed-benign"] += 1
print(counts)
