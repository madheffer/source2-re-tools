# xref.py <dll> <string or 0xVA> [...]: each string's VA (exact, NUL-terminated) and every rip-relative
# instruction in .text that points at it (lea / mov with a disp32 to the target), with the function start
# guessed by scanning back to the previous int3 / ret padding.
import sys, struct, pefile
import numpy as np
pe = pefile.PE(sys.argv[1], fast_load=True)
base = pe.OPTIONAL_HEADER.ImageBase
img = pe.get_memory_mapped_image()
text = next(s for s in pe.sections if s.Name.rstrip(b'\0') == b'.text')
t0, tn = text.VirtualAddress, text.Misc_VirtualSize
code = np.frombuffer(img[t0:t0 + tn], dtype=np.uint8)
# every 4-byte little-endian window as int32, and its position
d32 = np.frombuffer(img[t0:t0 + tn - 3] if False else bytes(img[t0:t0 + tn]), dtype=np.uint8)
win = (d32[:-3].astype(np.int64) | (d32[1:-2].astype(np.int64) << 8) | (d32[2:-1].astype(np.int64) << 16) | (d32[3:].astype(np.int64) << 24))
win = np.where(win >= 2**31, win - 2**32, win)
pos = np.arange(len(win), dtype=np.int64) + t0  # RVA of the disp32
def func_start(rva):
    o = rva - t0
    while o > 0:
        if code[o - 1] == 0xCC and code[o - 2] == 0xCC: return base + t0 + o
        o -= 1
    return None
for arg in sys.argv[2:]:
    if arg.startswith('0x'):
        targets = [int(arg, 16) - base]
    else:
        s = arg.encode() + b'\0'
        targets, i = [], 0
        while True:
            i = img.find(s, i)
            if i < 0: break
            if i == 0 or img[i - 1] == 0: targets.append(i)
            i += 1
    for tr in targets:
        print(f'{arg}: {base + tr:#x}')
        # the instruction ends 4 bytes after the disp32 when no immediate follows (lea / mov r, [rip+x])
        for extra in (4, 5, 8):
            hits = pos[(pos + extra + win) == tr]
            for h in hits:
                print(f'   ref at {base + h - 3:#x} (insn end +{extra}) in func ~{func_start(int(h)):#x}')
