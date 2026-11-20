# callers.py <dll> <0xVA> [...]: every `call rel32` / `jmp rel32` in .text to each target, with the calling
# function's start guessed by the int3 padding before it
import sys, pefile
import numpy as np
pe = pefile.PE(sys.argv[1], fast_load=True)
base = pe.OPTIONAL_HEADER.ImageBase
img = pe.get_memory_mapped_image()
text = next(s for s in pe.sections if s.Name.rstrip(b'\0') == b'.text')
t0, tn = text.VirtualAddress, text.Misc_VirtualSize
b = np.frombuffer(bytes(img[t0:t0 + tn]), dtype=np.uint8)
rel = (b[1:-3].astype(np.int64) | (b[2:-2].astype(np.int64) << 8) | (b[3:-1].astype(np.int64) << 16) | (b[4:].astype(np.int64) << 24))
rel = np.where(rel >= 2**31, rel - 2**32, rel)
op = b[:-4]
at = np.arange(len(op), dtype=np.int64) + t0
def start(rva):
    o = rva - t0
    while o > 1 and not (b[o - 1] == 0xCC and b[o - 2] == 0xCC): o -= 1
    return base + t0 + o
for a in sys.argv[2:]:
    tr = int(a, 16) - base
    hits = at[((op == 0xE8) | (op == 0xE9)) & (at + 5 + rel == tr)]
    print(a, len(hits), 'callers')
    for h in hits[:40]: print(f'   {base + h:#x} in ~{start(int(h)):#x}')
