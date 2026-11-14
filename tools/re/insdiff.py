"""insdiff.py <old.dll> <new.dll> <old_hex> <new_hex> <size>: print the instructions that differ between two
functions of the same length (operands masked only by text comparison after RIP displacement removal)."""
import sys, pefile, capstone, re

def load(path, va, n):
    pe = pefile.PE(path, fast_load=True)
    b = pe.OPTIONAL_HEADER.ImageBase
    return pe.get_data(va - b, n)

old, new = sys.argv[1], sys.argv[2]
oa, na, n = int(sys.argv[3], 16), int(sys.argv[4], 16), int(sys.argv[5])
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64)
oi = list(md.disasm(load(old, oa, n), oa))
ni = list(md.disasm(load(new, na, n), na))
rip = re.compile(r"\[rip [+-] 0x[0-9a-f]+\]")
def norm(i, base):
    s = rip.sub("[rip]", i.op_str)
    if i.mnemonic.startswith("j") or i.mnemonic == "call":
        try:
            t = int(i.op_str, 16)
            s = "+%x" % (t - base) if oa <= t - (base - oa) < oa + n else "ext"
        except ValueError:
            pass
    return i.mnemonic + " " + s
for a, b in zip(oi, ni):
    if norm(a, oa) != norm(b, na):
        print("%x: %-8s %-40s | %x: %-8s %s" % (a.address, a.mnemonic, a.op_str, b.address, b.mnemonic, b.op_str))
