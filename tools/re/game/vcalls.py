# vcalls.py <dll> <0xslot> [...]: every `call qword ptr [reg + slot]` (disp32, FF /2) in .text, with the calling
# function's start guessed by the int3 / ret padding before it (docs/game/README.md). Any class's vfn at that slot
# matches: read the call site to see whose vtable the register holds.
import sys, struct, pefile
import numpy as np
pe = pefile.PE(sys.argv[1], fast_load=True)
base = pe.OPTIONAL_HEADER.ImageBase
img = pe.get_memory_mapped_image()
text = next(s for s in pe.sections if s.Name.rstrip(b'\0') == b'.text')
t0, tn = text.VirtualAddress, text.Misc_VirtualSize
b = bytes(img[t0:t0 + tn])
def start(o):
    while o > 2:
        if b[o - 1] in (0xcc, 0xc3) and b[o - 2] in (0xcc, 0xc3): return o
        o -= 1
    return 0
for a in sys.argv[2:]:
    slot = struct.pack('<i', int(a, 16))
    for modrm in range(0x90, 0x98):  # mod 10, reg 2 (call), rm = rax..rdi (rsp needs a SIB, skipped)
        if modrm == 0x94: continue
        for rex in (b'', b'\x41'):
            pat = rex + bytes([0xff, modrm]) + slot
            i = b.find(pat)
            while i >= 0:
                if not (rex == b'' and i > 0 and b[i - 1] == 0x41):
                    reg = ['rax', 'rcx', 'rdx', 'rbx', 'rsp', 'rbp', 'rsi', 'rdi'][modrm - 0x90]
                    if rex: reg = ['r8', 'r9', 'r10', 'r11', 'r12', 'r13', 'r14', 'r15'][modrm - 0x90]
                    print(f"{base + t0 + i:x}: call [{reg} + {a}]    (fn ~{base + t0 + start(i):x})")
                i = b.find(pat, i + 1)
