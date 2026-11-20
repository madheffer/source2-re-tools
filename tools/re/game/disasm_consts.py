# disasm_consts.py <dll> <va hex> [bytes] [--all] [--fp]: disassembly with each rip-relative operand's f32 value shown
# --fp keeps only float / call / jump / cmp lines
import sys, struct, pefile, capstone
pe = pefile.PE(sys.argv[1], fast_load=True)
base = pe.OPTIONAL_HEADER.ImageBase
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64)
md.detail = True
va = int(sys.argv[2], 16)
args = [a for a in sys.argv[3:] if not a.startswith('--')]
n = int(args[0]) if args else 600
whole = '--all' in sys.argv
fp = '--fp' in sys.argv
img = pe.get_memory_mapped_image()
def f32(a):
    o = a - base
    if 0 <= o < len(img) - 4:
        u = struct.unpack_from('<I', img, o)[0]
        return f'{struct.unpack_from("<f", img, o)[0]!r} ({u:#x})'
    return '?'
keep = ('ss', 'sd', 'ps', 'pd', 'call', 'j', 'ret', 'cmp', 'test', 'cvt', 'sqrt', 'min', 'max', 'fmadd')
for i in md.disasm(pe.get_data(va - base, n), va):
    note = ''
    if 'rip' in i.op_str:
        for op in i.operands:
            if op.type == capstone.x86.X86_OP_MEM and op.mem.base == capstone.x86.X86_REG_RIP:
                tgt = i.address + i.size + op.mem.disp
                note = f'   ; [{tgt:#x}] = {f32(tgt)}'
    line = f'{i.address:x}: {i.mnemonic} {i.op_str}{note}'
    if not fp or any(k in i.mnemonic for k in keep):
        print(line)
    if i.mnemonic in ('int3',) and not whole:
        break
