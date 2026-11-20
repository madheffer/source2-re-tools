# recstores.py <dll> <0xstart> <0xend>: functions (.pdata) in a range ranked by how many SSE stores they make to
# [reg + disp] with disp in 0x00..0x200 (a GPU record being filled field by field), with the distinct displacements
import sys, pefile, capstone
from capstone import x86
dll, lo, hi = sys.argv[1], int(sys.argv[2], 16), int(sys.argv[3], 16)
pe = pefile.PE(dll, fast_load=True)
pe.parse_data_directories(directories=[pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_EXCEPTION']])
base = pe.OPTIONAL_HEADER.ImageBase
img = pe.get_memory_mapped_image()
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64)
md.detail = True
fns = sorted({(base + e.struct.BeginAddress, base + e.struct.EndAddress) for e in pe.DIRECTORY_ENTRY_EXCEPTION})
rows = []
for s, e in fns:
    if s < lo or s >= hi:
        continue
    code = img[s - base:e - base]
    disps = set()
    n = 0
    for ins in md.disasm(code, s):
        if not ins.mnemonic.startswith(('movss', 'movups', 'movaps', 'movd', 'movq', 'movlps', 'movhps', 'vmovss', 'vmovups')):
            continue
        ops = ins.operands
        if len(ops) == 2 and ops[0].type == x86.X86_OP_MEM and ops[1].type == x86.X86_OP_REG:
            d = ops[0].mem.disp
            if 0 <= d < 0x200 and ops[0].mem.base not in (x86.X86_REG_RSP, x86.X86_REG_RIP):
                n += 1
                disps.add(d)
    if n >= 12:
        rows.append((n, s, e, sorted(disps)))
for n, s, e, d in sorted(rows, reverse=True)[:15]:
    print(f'{s:#x}-{e:#x} stores {n} max disp {max(d):#x} distinct {len(d)}: {" ".join(hex(x) for x in d[:40])}')
