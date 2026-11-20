# strtoken.py <want hex>... [-- name...] [--file path]: Source 2's CUtlStringToken hash (MurmurHash2, seed 0x31415926,
# of the lowercased name) for each candidate, printing the ones that match a wanted value
import sys, re
def mm2(data, seed=0x31415926):
    m = 0x5bd1e995; h = (seed ^ len(data)) & 0xffffffff
    i = 0
    while len(data) - i >= 4:
        k = int.from_bytes(data[i:i + 4], 'little')
        k = (k * m) & 0xffffffff; k ^= k >> 24; k = (k * m) & 0xffffffff
        h = (h * m) & 0xffffffff; h ^= k
        i += 4
    r = len(data) - i
    if r == 3: h ^= data[i + 2] << 16
    if r >= 2: h ^= data[i + 1] << 8
    if r >= 1: h ^= data[i]; h = (h * m) & 0xffffffff
    h ^= h >> 13; h = (h * m) & 0xffffffff; h ^= h >> 15
    return h
args = sys.argv[1:]
want, names = set(), []
mode = 'want'
i = 0
while i < len(args):
    a = args[i]
    if a == '--': mode = 'names'
    elif a == '--file':
        i += 1
        data = open(args[i], 'rb').read()
        names += [m.group().decode() for m in re.finditer(rb'[A-Za-z_][A-Za-z0-9_.\-]{2,40}', data)]
    elif mode == 'want': want.add(int(a, 16))
    else: names.append(a)
    i += 1
seen = set()
for n in names:
    if n in seen: continue
    seen.add(n)
    h = mm2(n.lower().encode())
    if h in want: print(f'{h:#x} {n}')
print('checked', len(seen))
