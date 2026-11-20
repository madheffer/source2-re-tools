# python f32refs.py <dll> <f32 value>: every 4-byte-aligned copy of the f32 in the image, and each rip-relative
# instruction in .text that reads one (the function start guessed by the int3 padding before it)
import sys, struct, pefile, capstone
pe = pefile.PE(sys.argv[1], fast_load=True)
base = pe.OPTIONAL_HEADER.ImageBase
img = pe.get_memory_mapped_image()
pat = struct.pack('<f', float(sys.argv[2]))
spots = set()
i = img.find(pat)
while i >= 0:
    if i % 4 == 0: spots.add(base + i)
    i = img.find(pat, i + 1)
print('copies:', ', '.join(hex(s) for s in sorted(spots))[:400])
text = next(s for s in pe.sections if s.Name.rstrip(b'\0') == b'.text')
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64); md.detail = True; md.skipdata = True
for ins in md.disasm(text.get_data(), base + text.VirtualAddress):
    if 'rip' not in ins.op_str: continue
    for op in ins.operands:
        if op.type == capstone.x86.X86_OP_MEM and op.mem.base == capstone.x86.X86_REG_RIP:
            if ins.address + ins.size + op.mem.disp in spots: print(f'{ins.address:#x}: {ins.mnemonic} {ins.op_str}')
