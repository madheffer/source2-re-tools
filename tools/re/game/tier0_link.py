# tier0_link.py: the real tier0.dll in a Unicorn oracle, so the client functions it runs call tier0's own maths instead
# of Python stand-ins (docs/game/README.md). tier0 and client share the preferred base 0x180000000, so tier0 is
# relocated (pefile relocate_image) to `base`. link(uc, client_pe, tier0_path, names) writes tier0's export address
# into each named import slot of the client; tier0's CRT FMA flag (0x1803ab28c - its base) is cleared (the SSE2 path:
# Unicorn has no FMA), GS points at a zeroed TEB for the CRT's errno.
import struct
import pefile

FMA_FLAG_RVA = 0x3ab28c   # tier0 2026-10-15: the CRT's __use_fma3 style flag (cmp dword [rip+..], 0 in sinf / cosf / ...)


def load(uc, path, base=0x260000000, teb=0x270000000):
    pe = pefile.PE(path, fast_load=False)
    pe.relocate_image(base)
    img = pe.get_memory_mapped_image(ImageBase=base)
    uc.mem_map(base, (len(img) + 0xfff) & ~0xfff)
    uc.mem_write(base, bytes(img))
    uc.mem_write(base + FMA_FLAG_RVA, struct.pack('<i', 0))
    try:
        uc.mem_map(teb, 0x10000)
    except Exception:
        pass
    from unicorn.x86_const import UC_X86_REG_GS_BASE
    uc.reg_write(UC_X86_REG_GS_BASE, teb)
    return {e.name.decode(): base + e.address for e in pe.DIRECTORY_ENTRY_EXPORT.symbols if e.name}


def link(uc, client_pe, tier0_path, names, base=0x260000000):
    exports = load(uc, tier0_path, base)
    client_pe.parse_data_directories([pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_IMPORT']])
    done = set()
    for entry in client_pe.DIRECTORY_ENTRY_IMPORT:
        if entry.dll.lower() != b'tier0.dll':
            continue
        for imp in entry.imports:
            if imp.name and imp.name.decode() in names:
                uc.mem_write(imp.address, struct.pack('<Q', exports[imp.name.decode()]))
                done.add(imp.name.decode())
    missing = set(names) - done
    if missing:
        raise SystemExit(f'tier0_link: no client import for {sorted(missing)}')
    return exports
