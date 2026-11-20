# riprefs.py <dll> <0xVA> [...]: every rip-relative operand in .text that points at a VA (a string, a ConVar object, a
# global), found by bytes: an int32 at offset i with i + 4 + disp == target (the operand ends the instruction: a mov /
# lea / cmp without an immediate after it), printed with the containing function (the .pdata RUNTIME_FUNCTION) and
# the instruction disassembled. Seconds over a whole server.dll, where a capstone sweep takes minutes. With an
# immediate after the operand (cmp [rip+x], imm) the hit is missed: pass --imm N to also try N-byte immediates.
# (docs/game/README.md; docs/game/matchmaking.md found the reservation reader this way)
import sys, struct, bisect, pefile, capstone
import numpy as np

args = [a for a in sys.argv[1:] if not a.startswith('--')]
imms = [0]
if '--imm' in sys.argv: imms += [int(sys.argv[sys.argv.index('--imm') + 1])]
pe = pefile.PE(args[0], fast_load=True)
pe.parse_data_directories(directories=[pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_EXCEPTION']])
base = pe.OPTIONAL_HEADER.ImageBase
img = pe.get_memory_mapped_image()
text = next(s for s in pe.sections if s.Name.rstrip(b'\0') == b'.text')
t0, tn = text.VirtualAddress, text.Misc_VirtualSize
code = np.frombuffer(img[t0:t0 + tn - (tn % 1)], dtype=np.uint8)
funcs = sorted((f.struct.BeginAddress, f.struct.EndAddress) for f in getattr(pe, 'DIRECTORY_ENTRY_EXCEPTION', []))
starts = [f[0] for f in funcs]
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64)

def func_of(rva):
    k = bisect.bisect_right(starts, rva) - 1
    return funcs[k] if k >= 0 and funcs[k][0] <= rva < funcs[k][1] else None

# int32 at every offset (4 shifted views)
n = len(code) - 8
d32 = (code[0:n].astype(np.int64) | (code[1:n + 1].astype(np.int64) << 8) | (code[2:n + 2].astype(np.int64) << 16) | (code[3:n + 3].astype(np.int64) << 24))
d32 = np.where(d32 >= 1 << 31, d32 - (1 << 32), d32)
idx = np.arange(n, dtype=np.int64)
for a in args[1:]:
    target = int(a, 16) - base
    print(f'--- refs to {a}')
    for imm in imms:
        hits = np.nonzero(t0 + idx + 4 + imm + d32 == target)[0]
        for h in hits:
            rva = t0 + int(h)
            f = func_of(rva)
            # find the instruction: try starts 2..7 bytes before the disp
            ins = None
            for back in range(2, 8):
                s = rva - back
                for i in md.disasm(img[s:s + 15], base + s):
                    if i.address == base + s and s + i.size == rva + 4 + imm:
                        ins = i
                    break
                if ins: break
            fs = f'fn 0x{base + f[0]:x}-0x{base + f[1]:x}' if f else 'fn ?'
            print(f'0x{base + rva:x}  {fs}  {ins.mnemonic + " " + ins.op_str if ins else "(?)"}')
