# ptrscan.py <dll> <0xVA> [...]: every 8-aligned qword in the image equal to a VA (vtable slots pointing at a function),
# with the RTTI class of the vtable it falls in when an object locator precedes the run
import sys, struct, pefile
pe = pefile.PE(sys.argv[1], fast_load=True)
base = pe.OPTIONAL_HEADER.ImageBase
img = pe.get_memory_mapped_image()
for a in sys.argv[2:]:
    va = int(a, 16)
    needle = struct.pack('<Q', va)
    i = img.find(needle)
    while i >= 0:
        if i % 8 == 0:
            print(f'{a} at {base + i:#x}')
        i = img.find(needle, i + 1)
