# fieldwrites.py <dll> <0xoffset> [--reads]: every instruction in .text with a [reg + offset] memory operand (disp32,
# so offsets >= 0x80), the stores only unless --reads, with the function start guessed by the int3 padding before it.
# Finds who writes or reads a field (docs/game/README.md). Each disp32 window equal to the offset is located by a
# linear sweep from its function's guessed start (so prefixes like REX decode right), keeping the instruction that
# holds the window as its displacement.
import sys, pefile, capstone
import numpy as np
from capstone import x86
pe = pefile.PE(sys.argv[1], fast_load=True)
base = pe.OPTIONAL_HEADER.ImageBase
img = pe.get_memory_mapped_image()
text = next(s for s in pe.sections if s.Name.rstrip(b'\0') == b'.text')
t0, tn = text.VirtualAddress, text.Misc_VirtualSize
off = int(sys.argv[2], 16)
reads = '--reads' in sys.argv
raw = bytes(img[t0:t0 + tn])
b = np.frombuffer(raw, dtype=np.uint8)
w = (b[:-3].astype(np.int64) | (b[1:-2].astype(np.int64) << 8) | (b[2:-1].astype(np.int64) << 16) | (b[3:].astype(np.int64) << 24))
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64)
md.detail = True
md.skipdata = True
LOADS = ('cmp', 'test', 'lea', 'ucomiss', 'comiss', 'push')
def start(o):
    while o > 2:
        if raw[o - 1] in (0xcc, 0xc3) and raw[o - 2] in (0xcc, 0xc3): return o
        o -= 1
    return 0
for pos in np.nonzero(w == off)[0]:
    pos = int(pos)
    f = start(pos)
    hit = None
    for ins in md.disasm(raw[f:pos + 16], base + t0 + f):
        a = ins.address - base - t0
        if a > pos: break
        if a + ins.size > pos + 3:
            hit = ins
            break
    if hit is None or hit.id == 0:
        continue
    try:
        ops = hit.operands
    except capstone.CsError:
        continue
    mem = [k for k, o in enumerate(ops) if o.type == x86.X86_OP_MEM and o.mem.disp == off and o.mem.base != x86.X86_REG_RIP]
    if not mem:
        continue
    store = mem[0] == 0 and len(ops) >= 1 and not hit.mnemonic.startswith(LOADS)
    if store or reads:
        print(f"{hit.address:x}: {hit.mnemonic} {hit.op_str}    (fn ~{base + t0 + f:x}){'' if store else '  [read]'}")
