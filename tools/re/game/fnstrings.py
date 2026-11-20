# fnstrings.py <dll> <0xstart> <0xend>: the strings a function's rip-relative lea / mov operands point at (an ASCII
# run of 4+ printable bytes), e.g. to name a vfn by the events, cvars or messages it uses (docs/game/README.md)
import sys, pefile, capstone
from capstone import x86
pe = pefile.PE(sys.argv[1], fast_load=True)
base = pe.OPTIONAL_HEADER.ImageBase
img = bytes(pe.get_memory_mapped_image())
a, e = int(sys.argv[2], 16), int(sys.argv[3], 16)
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64)
md.detail = True
def cstr(va):
    o = va - base
    if not (0 <= o < len(img)): return None
    s = img[o:o + 120].split(b'\0')[0]
    return s.decode('latin1') if len(s) >= 4 and all(32 <= c < 127 for c in s) else None
for i in md.disasm(img[a - base:e - base], a):
    for o in i.operands:
        if o.type == x86.X86_OP_MEM and o.mem.base == x86.X86_REG_RIP:
            t = i.address + i.size + o.mem.disp
            s = cstr(t)
            if s is None:  # a pointer to a string (a cvar's name at +8, a ConVarRef)
                p = int.from_bytes(img[t - base:t - base + 8], 'little') if 0 <= t - base < len(img) - 8 else 0
                s2 = cstr(p) if p else None
                if s2: s = '*' + s2
            if s: print(f"{i.address:x}: {i.mnemonic} {i.op_str}  -> {s!r}")
