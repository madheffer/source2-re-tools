# xhair_oracle.py <client.dll> <out.json> [count]: CS2's own crosshair-code decode run under Unicorn, for
# web/src/cs2web/client/settings/crosshair-code-test.mjs (docs/game/settings.md "Crosshair codes").
# Emulates client.dll 2026-10-15's 180daf490 (BApplyCrosshairCode's parse 180daf640 + the record -> float struct)
# and 180dbca70 (the rescale to the screen height 180b80220 returns) over random codes: classic CSGO- codes
# (versions 0..6, right and wrong checksums), "CS" + 44-digit codes (clamped fields, bad versions / checksums),
# bad digits and overflowing numbers. Stubs: the imports V_roundf (the CRT roundf: tier0 1802a9ebc) and
# _V_StringAfterPrefixCaseSensitive, 180b80220 (returns the case's screen height); the cl_ironsight_usecrosshaircolor
# / cl_ironsight_dot_scale value blocks (globals 1825c86f0 / 1825c8700 -> +0x58) point at the case's values.
# Writes [{ code, use, scale, height, ok, s: <0x44 struct bytes hex>, r: <after rescale hex>, changed }].
import sys, json, random, struct, math
import pefile
from unicorn import Uc, UC_ARCH_X86, UC_MODE_64, UC_HOOK_CODE
from unicorn.x86_const import *

dll, out = sys.argv[1], sys.argv[2]
count = int(sys.argv[3]) if len(sys.argv) > 3 else 400
pe = pefile.PE(dll, fast_load=True)
pe.parse_data_directories([pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_IMPORT']])
B = pe.OPTIONAL_HEADER.ImageBase
img = pe.get_memory_mapped_image()
size = (len(img) + 0xfff) & ~0xfff

F_STRUCT, F_RESCALE, F_SCREEN_H = 0x180daf490, 0x180dbca70, 0x180b80220
G_USE, G_SCALE = 0x1825c86f0, 0x1825c8700
STUB, STACK, HEAP, STOP = 0x10000000, 0x20000000, 0x30000000, 0x40000000

uc = Uc(UC_ARCH_X86, UC_MODE_64)
uc.mem_map(B, size)
uc.mem_write(B, bytes(img))
for a in (STUB, STACK, HEAP, STOP):
    uc.mem_map(a, 0x100000)
uc.mem_write(STOP, b'\xc3')

stubs = {}
for entry in pe.DIRECTORY_ENTRY_IMPORT:
    for imp in entry.imports:
        if imp.name in (b'V_roundf', b'_V_StringAfterPrefixCaseSensitive'):
            addr = STUB + 0x10 * len(stubs)
            stubs[addr] = imp.name.decode()
            uc.mem_write(imp.address, struct.pack('<Q', addr))
            uc.mem_write(addr, b'\xc3')
stubs[F_SCREEN_H] = 'screen_h'
assert {'V_roundf', '_V_StringAfterPrefixCaseSensitive'} <= set(stubs.values()), stubs

state = {'h': 1080}


def f32(x):
    return struct.unpack('<f', struct.pack('<f', x))[0]


def crt_roundf(x):
    return f32(math.copysign(math.floor(abs(x) + 0.5), x)) if math.isfinite(x) else x


def read_cstr(a):
    s = b''
    while True:
        c = uc.mem_read(a, 1)
        if c == b'\0':
            return s
        s += bytes(c)
        a += 1


def ret():
    rsp = uc.reg_read(UC_X86_REG_RSP)
    rip = struct.unpack('<Q', uc.mem_read(rsp, 8))[0]
    uc.reg_write(UC_X86_REG_RSP, rsp + 8)
    uc.reg_write(UC_X86_REG_RIP, rip)


def hook(uc_, addr, size_, _):
    name = stubs.get(addr)
    if not name:
        return
    if name == 'V_roundf':
        x = struct.unpack('<f', uc.reg_read(UC_X86_REG_XMM0).to_bytes(16, 'little')[:4])[0]
        uc.reg_write(UC_X86_REG_XMM0, int.from_bytes(struct.pack('<f', crt_roundf(x)) + b'\0' * 12, 'little'))
    elif name == '_V_StringAfterPrefixCaseSensitive':
        s, p = uc.reg_read(UC_X86_REG_RCX), uc.reg_read(UC_X86_REG_RDX)
        ps = read_cstr(p)
        uc.reg_write(UC_X86_REG_RAX, s + len(ps) if read_cstr(s).startswith(ps) else 0)
    elif name == 'screen_h':
        uc.reg_write(UC_X86_REG_RAX, state['h'])
    ret()


uc.hook_add(UC_HOOK_CODE, hook, begin=STUB, end=STUB + 0x1000)
uc.hook_add(UC_HOOK_CODE, hook, begin=F_SCREEN_H, end=F_SCREEN_H + 1)


def call(fn, *args):
    rsp = STACK + 0x80000
    uc.mem_write(rsp, struct.pack('<Q', STOP))
    regs = [UC_X86_REG_RCX, UC_X86_REG_RDX, UC_X86_REG_R8, UC_X86_REG_R9]
    for r, v in zip(regs, args):
        uc.reg_write(r, v)
    uc.reg_write(UC_X86_REG_RSP, rsp)
    uc.emu_start(fn, STOP, count=2_000_000)
    return uc.reg_read(UC_X86_REG_RAX)


# the two convar value blocks the classic branch reads
BLK_USE, BLK_SCALE = HEAP + 0x1000, HEAP + 0x2000
uc.mem_write(G_USE, struct.pack('<Q', BLK_USE))
uc.mem_write(G_SCALE, struct.pack('<Q', BLK_SCALE))

ALPHA = 'ABCDEFGHJKLMNOPQRSTUVWXYZabcdefhijkmnopqrstuvwxyz23456789'


def encode(b, digits):
    n = int.from_bytes(bytes(b), 'big')
    s = ''
    for _ in range(digits):
        s += ALPHA[n % 57]
        n //= 57
    return s  # least significant digit first: the decoder reads it backwards


def classic(rng):
    M = [rng.randrange(256) for _ in range(18)]
    M[1] = rng.choice([0, 1, 2, 3, 3, 3, 4, 4, 5, 6])
    M[0] = sum(M[1:16]) & 0xff
    if rng.random() < 0.1:
        M[0] ^= 1 + rng.randrange(255)
    d = encode(M, 25)
    return 'CSGO-' + '-'.join(d[i:i + 5] for i in range(0, 25, 5))


def newcode(rng):
    r = [rng.randrange(256) for _ in range(32)]
    r[1] = 1 if rng.random() < 0.92 else rng.randrange(256)
    if rng.random() < 0.05:
        r[2] = r[3] = 0
    if rng.random() < 0.5:  # plausible values too, not only noise
        r[4] = rng.randrange(10) | (rng.randrange(8) << 5)
        r[13] = rng.randrange(33) | (rng.randrange(3) << 6)
        h = rng.choice([480, 720, 768, 1080, 1440, 2160, 100])
        r[2], r[3] = h & 0xff, h >> 8
    r[0] = sum(r[1:32]) & 0xff
    if rng.random() < 0.08:
        r[0] ^= 1 + rng.randrange(255)
    return 'CS' + encode(r, 44)


rng = random.Random(730)
cases = []
fixed = ['', 'CSGO-', 'CS' + '9' * 44, 'CS' + 'A' * 44, 'CSGO-AAAAA-AAAAA-AAAAA-AAAAA-AAAAA', 'CSGO-99999-99999-99999-99999-99999',
         'CSGO-0AAAA-AAAAA-AAAAA-AAAAA-AAAAA', 'CSGO_AAAAA-AAAAA-AAAAA-AAAAA-AAAAA']
codes = fixed + [classic(rng) if i % 2 else newcode(rng) for i in range(count)]
for code in codes:
    use = rng.randrange(2)
    scale = rng.choice([1.0, 0.1, 2.0, 0.05, 3.0, 0.55, 1.37, f32(rng.uniform(0, 2.5))])
    h = rng.choice([1080, 1440, 720, 2160, 1009, 480, 240])
    uc.mem_write(BLK_USE + 0x58, bytes([use]))
    uc.mem_write(BLK_SCALE + 0x58, struct.pack('<f', scale))
    sp = HEAP + 0x10000
    uc.mem_write(sp, code.encode() + b'\0')
    s = HEAP + 0x20000
    init = bytes(0x40) + struct.pack('<f', 1.0)  # the caller's struct: zeros, the dot scale slot 1.0 (180dc2c40)
    uc.mem_write(s, init)
    ok = call(F_STRUCT, s, sp) & 0xff
    sb = bytes(uc.mem_read(s, 0x44))
    state['h'] = h
    changed = None
    rb = None
    if ok:
        changed = call(F_RESCALE, s) & 0xff
        rb = bytes(uc.mem_read(s, 0x44)).hex()
    cases.append({'code': code, 'use': use, 'scale': scale, 'height': h, 'ok': ok, 's': sb.hex(), 'r': rb, 'changed': changed})
json.dump({'dll': dll.replace('\\', '/').split('/')[-1], 'cases': cases}, open(out, 'w', newline='\n'), indent=0)
print(f'{len(cases)} cases, {sum(c["ok"] for c in cases)} valid')
