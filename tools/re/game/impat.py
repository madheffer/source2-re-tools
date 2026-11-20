# impat.py <dll> <iat va hex> [...]: which import each IAT slot holds (a `call qword ptr [rip + x]` target)
import sys, pefile
pe = pefile.PE(sys.argv[1], fast_load=True)
pe.parse_data_directories([pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_IMPORT']])
want = {int(a, 16) for a in sys.argv[2:]}
for entry in pe.DIRECTORY_ENTRY_IMPORT:
    for imp in entry.imports:
        if imp.address in want:
            print(f'{imp.address:#x} {entry.dll.decode()}!{(imp.name or b"#%d" % imp.ordinal).decode()}')
