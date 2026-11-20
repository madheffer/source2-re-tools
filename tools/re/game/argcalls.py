# python argcalls.py <dll> <0xcallee> <reg>: every direct call (or jmp) to callee with the last write to reg (and its
# 32-bit form) in the 20 instructions before
import sys, pefile, capstone
pe = pefile.PE(sys.argv[1], fast_load=True)
base = pe.OPTIONAL_HEADER.ImageBase
text = next(s for s in pe.sections if s.Name.rstrip(b'\0') == b'.text')
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64)
md.skipdata = True
tgt = int(sys.argv[2], 16)
regs = {'r8': ('r8', 'r8d', 'r8w'), 'rdx': ('rdx', 'edx', 'dx'), 'rcx': ('rcx', 'ecx'), 'r9': ('r9', 'r9d')}[sys.argv[3]]
win = []
for ins in md.disasm(text.get_data(), base + text.VirtualAddress):
    win.append(ins)
    if len(win) > 20: win.pop(0)
    if ins.mnemonic in ('call', 'jmp') and ins.op_str == hex(tgt):
        w = next((w for w in reversed(win[:-1]) if w.op_str.split(',')[0].strip() in regs), None)
        print(f'{ins.address:#x}: {w.mnemonic + " " + w.op_str if w else "?"}')
