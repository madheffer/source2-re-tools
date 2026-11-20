# Disassemble a function at a VA (docs/game/README.md): the sum order and constants the decompiler hides.
#   python tools/re/disasm.py <dll> <va hex> [bytes] [--all]
# Stops at the first ret / int3 unless --all. Needs pefile and capstone (pip install pefile capstone).
# Don't name a copy dis.py: it shadows the standard library's dis, which capstone imports.
import sys, pefile, capstone
pe = pefile.PE(sys.argv[1], fast_load=True)
base = pe.OPTIONAL_HEADER.ImageBase
# x64 or x86 by the PE's machine (0x14c: CS:GO legacy's 32-bit DLLs)
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32 if pe.FILE_HEADER.Machine == 0x14c else capstone.CS_MODE_64)
va = int(sys.argv[2], 16)
n = int(sys.argv[3]) if len(sys.argv) > 3 and not sys.argv[3].startswith('--') else 400
whole = '--all' in sys.argv
for i in md.disasm(pe.get_data(va - base, n), va):
    print(f"{i.address:x}: {i.mnemonic} {i.op_str}")
    if i.mnemonic in ('ret', 'int3') and not whole: break
