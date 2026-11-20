# fnat.py <dll> <0xVA> [--consts] [--around N]: the function containing an address, from the exception directory
# (.pdata RUNTIME_FUNCTION: exact begin / end, chained unwind parts followed to their primary), disassembled whole
# (or N lines either side of the address, marked >>). --consts shows each rip-relative operand's f32 / pointer.
# Better than guessing a start from int3 padding (docs/game/README.md).
import sys, struct, bisect, pefile, capstone
from capstone import x86
pe = pefile.PE(sys.argv[1], fast_load=True)
base = pe.OPTIONAL_HEADER.ImageBase
img = bytes(pe.get_memory_mapped_image())
va = int(sys.argv[2], 16)
consts = '--consts' in sys.argv
around = int(sys.argv[sys.argv.index('--around') + 1]) if '--around' in sys.argv else None
ed = pe.OPTIONAL_HEADER.DATA_DIRECTORY[3]
rf = [struct.unpack_from('<III', img, ed.VirtualAddress + 12 * i) for i in range(ed.Size // 12)]
starts = [r[0] for r in rf]
def primary(k):
    # a chained unwind info (flag 4) points at its parent RUNTIME_FUNCTION after the unwind codes
    for _ in range(16):
        b, e, u = rf[k]
        if u & 1: return k
        flags = img[u] >> 3
        if not flags & 4: return k
        n = img[u + 2]
        p = u + 4 + 2 * (n + (n & 1))
        pb = struct.unpack_from('<I', img, p)[0]
        k = bisect.bisect_right(starts, pb) - 1
    return k
rva = va - base
k = bisect.bisect_right(starts, rva) - 1
if k < 0 or not (rf[k][0] <= rva < rf[k][1]):
    sys.exit(f'{va:x}: in no .pdata function')
k0 = primary(k)
# the function's parts: the primary and every chained part pointing back to it, in address order
parts = sorted({(rf[j][0], rf[j][1]) for j in range(max(0, k0 - 4000), min(len(rf), k0 + 4000)) if primary(j) == k0})
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64)
md.detail = consts
print(f"; function 0x{base + rf[k0][0]:x}..0x{base + rf[k0][1]:x}" + (f", part 0x{base + rf[k][0]:x}..0x{base + rf[k][1]:x}" if k != k0 else ''))
lines = []
for b, e in parts:
    for i in md.disasm(img[b:e], base + b):
        s = f"{i.address:x}: {i.mnemonic} {i.op_str}"
        if consts:
            for o in i.operands:
                if o.type == x86.X86_OP_MEM and o.mem.base == x86.X86_REG_RIP:
                    t = i.address + i.size + o.mem.disp - base
                    if 0 <= t < len(img) - 8:
                        s += f"   ; [0x{t + base:x}] f32 {struct.unpack_from('<f', img, t)[0]:.9g} q 0x{struct.unpack_from('<Q', img, t)[0]:x}"
        lines.append((i.address, s))
if around is None:
    for _, s in lines: print(s)
else:
    j = min(range(len(lines)), key=lambda n: abs(lines[n][0] - va))
    for a, s in lines[max(0, j - around):j + around + 1]:
        print(('>> ' if a == lines[j][0] else '   ') + s)
