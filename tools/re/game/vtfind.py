# vtfind.py <dll> <vtable 0xVA> <0xfunc> [...]: the slots of a vtable (the first 400) that point at any of the
# functions, e.g. which of a helper's callers is a virtual of a class (docs/game/README.md)
import sys, struct, pefile
pe = pefile.PE(sys.argv[1], fast_load=True)
base = pe.OPTIONAL_HEADER.ImageBase
img = pe.get_memory_mapped_image()
vt = int(sys.argv[2], 16) - base
want = {int(a, 16) for a in sys.argv[3:]}
for i in range(400):
    f = struct.unpack_from('<Q', img, vt + i * 8)[0]
    if f in want: print(f'slot {i * 8:#x}: {f:#x}')
