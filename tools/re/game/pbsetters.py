# pbsetters.py <dll> <0xhasbits_off> <0xbit> <0xfield_off>: inlined protobuf setters in .text: an `or [reg + hasbits],
# bit` with a store to [same reg + field] within 6 instructions either side, e.g. who sets CSGOUserCmdPB's
# attack1_start_history_index (has-bits +0x10 bit 0x20, field +0x3c). Prints the site and its function's guessed start.
import sys, pefile, capstone
from capstone import x86
pe = pefile.PE(sys.argv[1], fast_load=True)
base = pe.OPTIONAL_HEADER.ImageBase
img = pe.get_memory_mapped_image()
text = next(s for s in pe.sections if s.Name.rstrip(b'\0') == b'.text')
t0, tn = text.VirtualAddress, text.Misc_VirtualSize
raw = bytes(img[t0:t0 + tn])
hb, bit, fo = (int(a, 16) for a in sys.argv[2:5])
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64)
md.detail = True
def start(o):
    while o > 2:
        if raw[o - 1] in (0xcc, 0xc3) and raw[o - 2] in (0xcc, 0xc3): return o
        o -= 1
    return 0
# `or dword ptr [reg + hb], imm8`: 83 /1 with disp8 (mod 01): modrm 0x48..0x4f (0x4c needs a SIB), optional REX 41
pats = []
for rm in range(8):
    if rm == 4: continue
    for rex in (b'', b'\x41'):
        pats.append((rex + bytes([0x83, 0x48 | rm, hb, bit]), rm + (8 if rex else 0)))
seen = set()
for pat, reg in pats:
    i = raw.find(pat)
    while i >= 0:
        f = start(i)
        ins = list(md.disasm(raw[max(f, i - 64):i + 64], base + t0 + max(f, i - 64)))
        k = next((n for n, x in enumerate(ins) if x.address == base + t0 + i), None)
        if k is not None:
            regname = ins[k].op_str.split('[')[1].split(' ')[0]
            for x in ins[max(0, k - 6):k + 7]:
                if x.mnemonic.startswith('mov') and f'[{regname} + 0x{fo:x}]' in x.op_str.split(',')[0] and x.address not in seen:
                    seen.add(x.address)
                    print(f"{x.address:x}: {x.mnemonic} {x.op_str}   (or at {ins[k].address:x}, fn ~{base + t0 + f:x})")
        i = raw.find(pat, i + 1)
