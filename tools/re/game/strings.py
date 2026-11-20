# strings.py <dll> <regex>: every NUL-terminated ASCII string matching the regex, with its VA
import sys, re, pefile
pe = pefile.PE(sys.argv[1], fast_load=True)
base = pe.OPTIONAL_HEADER.ImageBase
img = pe.get_memory_mapped_image()
pat = re.compile(rb'[\x20-\x7e]{3,200}\x00')
want = re.compile(sys.argv[2].encode())
for m in pat.finditer(img):
    s = m.group()[:-1]
    if want.search(s): print(f'{base + m.start():#x} {s.decode()}')
