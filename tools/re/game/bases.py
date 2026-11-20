# A class's base classes in an MSVC x64 DLL, from its RTTI (the complete-object locator's class hierarchy descriptor).
#   python tools/re/bases.py <dll> <ClassName> [<ClassName> ...]
# Finds the type descriptor ".?AV<Class>@@", a complete-object locator (signature 1) pointing at it, and walks its
# hierarchy descriptor's base class array: every base, nearest first as the compiler lists them (the class itself is
# entry 0). docs/game/README.md lists the RE tools.
import struct
import sys

import pefile

pe = pefile.PE(sys.argv[1], fast_load=True)
data = open(sys.argv[1], 'rb').read()
base = pe.OPTIONAL_HEADER.ImageBase


def off(rva):
    return pe.get_offset_from_rva(rva)


def u32(o):
    return struct.unpack_from('<I', data, o)[0]


def td_name(td_rva):
    o = off(td_rva) + 16  # type descriptor: vtable ptr, spare, then the decorated name
    end = data.index(b'\0', o)
    return data[o:end].decode('ascii', 'replace')


for name in sys.argv[2:]:
    needle = f'.?AV{name}@@'.encode() + b'\0'
    at = data.find(needle)
    if at < 0:
        print(f'{name}: no type descriptor')
        continue
    td_rva = pe.get_rva_from_offset(at - 16)
    # a complete-object locator: signature 1, offset, cdOffset, type descriptor rva, hierarchy rva, self rva
    pat = struct.pack('<I', td_rva)
    i, found = 0, None
    while True:
        i = data.find(pat, i)
        if i < 0:
            break
        if i >= 12 and u32(i - 12) == 1 and u32(i - 8) == 0:
            found = i - 12
            break
        i += 4
    if found is None:
        print(f'{name}: no complete-object locator')
        continue
    chd = off(u32(found + 16))
    n, arr = u32(chd + 8), off(u32(chd + 12))
    bases = [td_name(u32(off(u32(arr + 4 * k)))) for k in range(n)]
    print(f'{name}: ' + ' <- '.join(b.removeprefix('.?AV').removesuffix('@@') for b in bases))
