# dispuses.py <dll> <0xstart> <0xend> <0xdisp> [...]: every instruction in a VA range whose memory operand has one of
# the displacements (lea included, which fieldwrites.py skips), by a linear sweep that restarts after each int3 run.
# For finding who touches a field of an object inside one class's code (docs/game/README.md).
import sys, pefile, capstone
from capstone import x86
pe = pefile.PE(sys.argv[1], fast_load=True)
base = pe.OPTIONAL_HEADER.ImageBase
a, e = int(sys.argv[2], 16), int(sys.argv[3], 16)
want = {int(x, 16) for x in sys.argv[4:]}
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64)
md.detail = True
data = pe.get_data(a - base, e - a)
pos, fn = 0, a
while pos < len(data):
    n = 0
    for i in md.disasm(data[pos:], a + pos):
        n = i.address + i.size - (a + pos)
        if i.mnemonic == 'int3':
            fn = i.address + i.size
            continue
        for op in i.operands:
            if op.type == x86.X86_OP_MEM and op.mem.disp in want and op.mem.base != x86.X86_REG_RIP:
                print(f'{i.address:x}: {i.mnemonic} {i.op_str}    (after int3 at ~{fn:x})')
    pos += max(n, 1)
