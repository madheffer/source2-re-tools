# vtstart.py <dll> <0xslotVA>: walk back from a vtable slot to the vtable start (the qword after the complete object
# locator pointer) and print the class name from the RTTI, the start and the slot index
import sys, struct, pefile
pe = pefile.PE(sys.argv[1], fast_load=True)
base = pe.OPTIONAL_HEADER.ImageBase
img = pe.get_memory_mapped_image()
text = next(s for s in pe.sections if s.Name.rstrip(b'\0') == b'.text')
tlo, thi = base + text.VirtualAddress, base + text.VirtualAddress + text.Misc_VirtualSize
q = lambda va: struct.unpack_from('<Q', img, va - base)[0]
slot = int(sys.argv[2], 16)
p = slot
while tlo <= q(p - 8) < thi:
    p -= 8
col = q(p - 8)
# the COL: signature, offset, cdOffset, typeDescriptor RVA, classDescriptor RVA, self RVA
try:
    sig, off, cd, td = struct.unpack_from('<IIII', img, col - base)
    name = img[td + 0x10: td + 0x10 + 120].split(b'\0')[0].decode(errors='replace')
except Exception:
    name = '?'
print(f'vtable {p:#x} class {name} slot {(slot - p) // 8} (offset {slot - p:#x})')
for k in range(0, 24):
    print(f'  {k:2d} {k * 8:#05x} {q(p + 8 * k):#x}')
