# tier0_trig_oracle.py <tier0.dll> <out.json> [count]: tier0's V_sincosf / V_tanf / V_atanf / V_expf / V_powf / V_roundf (2026-10-15) run under
# Unicorn on random f32 inputs, their results' bits dumped for web/server/cs2web/tier0-trig-test.mjs (docs/game/settings.md
# "tier0's trig"). The three are wrappers over the statically linked MSVC CRT's sinf / cosf / tanf / atanf (AMD libm
# style: the argument in double, a polynomial, rounded once to float). The CRT picks an FMA3 path when the flag at
# 0x1803ab28c is set (its CPU check at start-up); Unicorn has no FMA, so this runs the SSE2 path (flag 0).
import sys, json, random, struct
import pefile
from unicorn import Uc, UC_ARCH_X86, UC_MODE_64
from unicorn.x86_const import *

dll, out = sys.argv[1], sys.argv[2]
count = int(sys.argv[3]) if len(sys.argv) > 3 else 20000
pe = pefile.PE(dll, fast_load=True)
pe.parse_data_directories([pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_EXPORT']])
B = pe.OPTIONAL_HEADER.ImageBase
img = pe.get_memory_mapped_image()
EXP = {e.name.decode(): B + e.address for e in pe.DIRECTORY_ENTRY_EXPORT.symbols if e.name}
F_SINCOS, F_TAN, F_ATAN = EXP['V_sincosf'], EXP['V_tanf'], EXP['V_atanf']
F_EXP, F_POW, F_ROUND = EXP['V_expf'], EXP['V_powf'], EXP['V_roundf']
FMA_FLAG = 0x1803ab28c
STACK, HEAP, STOP, TEB = 0x20000000, 0x30000000, 0x40000000, 0x50000000

uc = Uc(UC_ARCH_X86, UC_MODE_64)
uc.mem_map(B, (len(img) + 0xfff) & ~0xfff)
uc.mem_write(B, bytes(img))
for a in (STACK, HEAP, STOP, TEB):
    uc.mem_map(a, 0x100000)
uc.mem_write(STOP, b'\xc3')
uc.reg_write(UC_X86_REG_GS_BASE, TEB)  # errno's TLS reads (out-of-range arguments only)
uc.mem_write(FMA_FLAG, struct.pack('<i', 0))


def f32(x):
    return struct.unpack('<f', struct.pack('<f', x))[0]


def bits(x):
    return struct.unpack('<I', struct.pack('<f', x))[0]


def fl(b):
    return struct.unpack('<f', struct.pack('<I', b))[0]


def call(fn, x, ints=(), y=0.0):
    rsp = STACK + 0x80000
    uc.mem_write(rsp, struct.pack('<Q', STOP))
    for r, v in zip([UC_X86_REG_RDX, UC_X86_REG_R8], ints):
        uc.reg_write(r, v)
    uc.reg_write(UC_X86_REG_XMM0, int.from_bytes(struct.pack('<f', x) + b'\0' * 12, 'little'))
    uc.reg_write(UC_X86_REG_XMM1, int.from_bytes(struct.pack('<f', y) + b'\0' * 12, 'little'))
    uc.reg_write(UC_X86_REG_RSP, rsp)
    uc.emu_start(fn, STOP, count=100_000)
    return struct.unpack('<I', uc.reg_read(UC_X86_REG_XMM0).to_bytes(16, 'little')[:4])[0]


rng = random.Random(0x7140)
# inputs as the game passes them: radians from degrees (the crosshair's 0.0872665 half step, AngleVectors' angles, FOV
# halves), small and large, plus random bit patterns over the finite range's useful part
xs = [0.0, -0.0, 0.0872664600610733, 0.7853981852531433, 1.5707963705062866, 3.1415927410125732, 1e-8, 1e-4,
      499999.97, 500000.0, 8388607.5, 8388608.0, 16000000.0, 16779436.0, 3373259264.0, 3373259520.0, 3.4e38, -3.4e38]
while len(xs) < count:
    if rng.random() < 0.06:  # the Payne-Hanek reductions: any finite magnitude
        xs.append(fl(rng.getrandbits(23) | (rng.randint(0x93, 0xfe) << 23) | (rng.getrandbits(1) << 31)))
        continue
    r = rng.random()
    if r < 0.4:
        x = rng.uniform(-180, 180) * 0.017453292
    elif r < 0.6:
        x = rng.uniform(-1.6, 1.6)
    elif r < 0.75:
        x = rng.uniform(-1e-3, 1e-3)
    elif r < 0.9:
        x = rng.uniform(-50, 50)
    else:
        x = fl(rng.getrandbits(32) & 0x47ffffff | (rng.getrandbits(1) << 31))  # |x| < 131072
    xs.append(struct.unpack('<f', struct.pack('<f', x))[0])

SIN, COS = HEAP, HEAP + 0x10
rows = []
for x in xs:
    uc.mem_write(SIN, bytes(8))
    call(F_SINCOS, x, ints=(SIN, COS))
    s = struct.unpack('<I', bytes(uc.mem_read(SIN, 4)))[0]
    c = struct.unpack('<I', bytes(uc.mem_read(COS, 4)))[0]
    t = call(F_TAN, x)
    a = call(F_ATAN, x)
    rd = call(F_ROUND, x * 37.0 if abs(x) < 1e6 else x)
    rows.append([bits(x), s, c, t, a, rd])
# V_expf on the soft clamp's arguments (180d9e770: -(1 / (L - lo)) (spread - lo), <= 0) and wider; V_powf on bases and
# exponents the styles pass (0..4, -3..3)
exps, pows = [], []
for k in range(count):
    r = rng.random()
    x = f32(-rng.random() * (4 if r < 0.5 else 60)) if r < 0.8 else f32(rng.uniform(-80, 80))
    exps.append([bits(x), call(F_EXP, x)])
    b, e = f32(rng.uniform(0, 4)), f32(rng.uniform(-3, 3) if k % 3 else rng.randint(0, 4))
    pows.append([bits(b), bits(e), call(F_POW, b, y=e)])
json.dump({'dll': dll.replace('\\', '/').split('/')[-1], 'fma': 0, 'rows': rows, 'exp': exps, 'pow': pows},
          open(out, 'w', newline='\n'))
print(f'{len(rows)} inputs, {len(exps)} exp, {len(pows)} pow')
