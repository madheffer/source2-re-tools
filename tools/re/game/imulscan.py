# imulscan.py <dll> <0ximm> [...]: every imul / lea-scale-free multiply by the given immediates in .text, with the
# containing .pdata function (a record array's stride)
import sys, bisect, pefile, capstone
from capstone import x86
pe = pefile.PE(sys.argv[1], fast_load=True)
pe.parse_data_directories(directories=[pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_EXCEPTION']])
base = pe.OPTIONAL_HEADER.ImageBase
img = pe.get_memory_mapped_image()
imms = {int(a, 16) for a in sys.argv[2:]}
fns = sorted({(base + e.struct.BeginAddress, base + e.struct.EndAddress) for e in pe.DIRECTORY_ENTRY_EXCEPTION})
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64)
md.detail = True
hits = {}
for s, t in fns:
    for ins in md.disasm(img[s - base:t - base], s):
        if ins.mnemonic == 'imul':
            for op in ins.operands:
                if op.type == x86.X86_OP_IMM and op.imm in imms:
                    hits.setdefault(s, []).append(f'{ins.address:#x} {ins.mnemonic} {ins.op_str}')
for s, l in sorted(hits.items()):
    print(f'fn {s:#x}: {len(l)}  ' + ' | '.join(l[:3]))
