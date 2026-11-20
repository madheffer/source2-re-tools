# xhair_draw_oracle.py <client.dll> <out.json> [count]: CS2's crosshair shape list, built by client.dll 2026-10-15's own
# style functions under Unicorn, for web/src/cs2web/client/settings/crosshair-draw-test.mjs (docs/game/settings.md "The crosshair's
# drawing"). The crosshair object 180da0610 passes them: +0 the list (64 x 0x40 + the count at +0x1008), +0x48 / +0x4c /
# +0x50 / +0x54 the inputs, +0x60.. the struct, +0xa4 / +0xa8 the centre, +0xac / +0xb0 / +0xb4 / +0xb8 the dynamic values.
# Each case: the dot first when cl_crosshairdot (180da7510), then the style: 3 180da6a80, 4 180da6ae0, 6 180da6e30,
# 8 180da7110, 9 180da7390, 7 180da6e60, 2 180da66c0 (no pawn); 0 / 1 as 180da0610's switch calls 180da63f0 /
# 180da6290 with the alpha scaled by +0xb8. tier0.dll itself for V_roundf, V_tanf, V_powf (tier0_link.py); stub: 180b80220 (the screen height).
import sys, json, random, struct, math
import pefile
import tier0_link
from unicorn import Uc, UC_ARCH_X86, UC_MODE_64, UC_HOOK_CODE
from unicorn.x86_const import *

dll, out = sys.argv[1], sys.argv[2]
count = int(sys.argv[3]) if len(sys.argv) > 3 else 600
pe = pefile.PE(dll, fast_load=True)
pe.parse_data_directories([pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_IMPORT']])
B = pe.OPTIONAL_HEADER.ImageBase
img = pe.get_memory_mapped_image()
STUB, STACK, HEAP, STOP = 0x10000000, 0x20000000, 0x30000000, 0x40000000
F = {'dot': 0x180da7510, 3: 0x180da6a80, 4: 0x180da6ae0, 6: 0x180da6e30, 8: 0x180da7110, 9: 0x180da7390, 7: 0x180da6e60, 2: 0x180da66c0,
     'bars': 0x180da63f0, 'circle': 0x180da6290}
SCREEN_H = 0x180b80220

uc = Uc(UC_ARCH_X86, UC_MODE_64)
uc.mem_map(B, (len(img) + 0xfff) & ~0xfff)
uc.mem_write(B, bytes(img))
for a in (STUB, STACK, HEAP, STOP):
    uc.mem_map(a, 0x100000)
uc.mem_write(STOP, b'\xc3')
stubs = {}
# tier0's own V_roundf / V_tanf / V_powf (tier0_link.py: the tier0 build beside the client's, same date)
tier0_link.link(uc, pe, dll.replace('client_', 'tier0_'), ['V_roundf', 'V_tanf', 'V_powf'])
stubs[SCREEN_H] = 'screen_h'
state = {'h': 1080}


def f32(x):
    return struct.unpack('<f', struct.pack('<f', x))[0]


def xmm(i):
    return struct.unpack('<f', uc.reg_read(UC_X86_REG_XMM0 + i).to_bytes(16, 'little')[:4])[0]


def set_xmm(i, v):
    uc.reg_write(UC_X86_REG_XMM0 + i, int.from_bytes(struct.pack('<f', v) + b'\0' * 12, 'little'))


def hook(uc_, addr, size_, _):
    name = stubs.get(addr)
    if not name:
        return
    if name == 'V_roundf':
        x = xmm(0)
        set_xmm(0, f32(math.copysign(math.floor(abs(x) + 0.5), x)))
    elif name == 'V_tanf':
        set_xmm(0, f32(math.tan(xmm(0))))
    elif name == 'V_powf':
        set_xmm(0, f32(math.pow(xmm(0), xmm(1))))
    elif name == 'screen_h':
        uc.reg_write(UC_X86_REG_RAX, state['h'])
    rsp = uc.reg_read(UC_X86_REG_RSP)
    uc.reg_write(UC_X86_REG_RIP, struct.unpack('<Q', uc.mem_read(rsp, 8))[0])
    uc.reg_write(UC_X86_REG_RSP, rsp + 8)


uc.hook_add(UC_HOOK_CODE, hook, begin=STUB, end=STUB + 0x1000)
uc.hook_add(UC_HOOK_CODE, hook, begin=SCREEN_H, end=SCREEN_H + 1)

OBJ, LIST, LEG = HEAP, HEAP + 0x1000, HEAP + 0x4000


def call(fn, ints=(), floats=None, stack=()):
    """ints: rcx, rdx, r8, r9 by position; floats: {position: value} into xmm<position>; stack: 5th.. args as 8-byte slots."""
    rsp = STACK + 0x80000
    uc.mem_write(rsp, struct.pack('<Q', STOP))
    for i, v in enumerate(stack):
        uc.mem_write(rsp + 0x28 + 8 * i, v if isinstance(v, bytes) else struct.pack('<Q', v))
    for r, v in zip([UC_X86_REG_RCX, UC_X86_REG_RDX, UC_X86_REG_R8, UC_X86_REG_R9], ints):
        uc.reg_write(r, v)
    for i, v in (floats or {}).items():
        set_xmm(i, v)
    uc.reg_write(UC_X86_REG_RSP, rsp)
    uc.emu_start(fn, STOP, count=500_000)


def rgba(c):
    return c[0] | (c[1] << 8) | (c[2] << 16) | (c[3] << 24)


rng = random.Random(1915)
cases = []
fixed_th = [0, 0.5, 1, 1.5, 2, 2.5, 3, 4, 5, 6.5, 8]
for n in range(count):
    style = rng.choice([0, 1, 2, 3, 4, 6, 7, 8, 9])
    S = {
        'screenHeight': 1080, 'style': style, 'recoil': 0, 'outline': rng.randrange(3), 'dot': rng.randrange(2), 't': rng.randrange(2),
        'gap': float(rng.choice([rng.randint(-6, 40), -1, 0, 1])), 'thickness': float(rng.choice(fixed_th + [rng.randint(0, 12)])),
        'length': float(rng.randint(0, 30)), 'spreadLimit': float(rng.randint(0, 255)),
        'color': [rng.randrange(256) for _ in range(4)], 'outlineColor': [rng.randrange(256) for _ in range(4)],
        'splitDist': float(rng.randint(0, 40)), 'innerAlpha': f32(rng.random()), 'outerAlpha': f32(0.3 + 0.7 * rng.random()),
        'splitRatio': f32(rng.choice([rng.random(), 0.0, 1.0, 0.5])), 'ironsightUseColor': 0, 'dotScale': 1.0,
    }
    dyn = {'spreadPx': float(rng.choice([0, rng.randint(1, 150), 5, 99, 100])), 'spread2Px': float(rng.randint(0, 60)),
           'dynGap': float(rng.randint(0, 120)), 'alphaMul': f32(rng.choice([1.0, 0.2, 0.5 + 0.5 * rng.random()]))}
    inp = {'inacc': f32(rng.choice([0, 0.001, 0.05, 0.2, rng.random() * 0.3])), 'base': f32(rng.choice([0, 0.006, 0.2, rng.random() * 0.1])),
           'spread': f32(rng.choice([0, 0.0006, 0.002])), 'fov': f32(rng.choice([90.0, 40.0, 15.0]))}
    h = rng.choice([1080, 1440, 720, 768])
    cx, cy = float(rng.randint(300, 1300)), float(rng.randint(200, 800))
    state['h'] = h
    obj = bytearray(0x100)
    struct.pack_into('<Q', obj, 0, LIST)
    struct.pack_into('<Q', obj, 8, LEG)
    struct.pack_into('<ffff', obj, 0x48, inp['inacc'], inp['base'], inp['spread'], inp['fov'])
    struct.pack_into('<fi', obj, 0x60, S['screenHeight'], style)
    obj[0x68] = S['recoil']
    struct.pack_into('<i', obj, 0x6c, S['outline'])
    obj[0x70], obj[0x71] = S['dot'], S['t']
    struct.pack_into('<ffff', obj, 0x74, S['gap'], S['thickness'], S['length'], S['spreadLimit'])
    struct.pack_into('<II', obj, 0x84, rgba(S['color']), rgba(S['outlineColor']))
    struct.pack_into('<ffff', obj, 0x8c, S['splitDist'], S['innerAlpha'], S['outerAlpha'], S['splitRatio'])
    struct.pack_into('<ffffff', obj, 0xa4, cx, cy, dyn['spread2Px'], dyn['spreadPx'], dyn['dynGap'], dyn['alphaMul'])
    uc.mem_write(OBJ, bytes(obj))
    uc.mem_write(LIST, bytes(0x1010))
    uc.mem_write(LEG, bytes(16))
    ocol = rgba(S['outlineColor']) if S['outline'] else 0
    if S['dot']:
        call(F['dot'], ints=(OBJ, 0, rgba(S['color']), ocol), floats={1: S['thickness']})
    if style in (3, 4, 6, 8, 9, 7):
        call(F[style], ints=(OBJ,))
    elif style == 2:
        call(F[2], ints=(OBJ, 0))
    else:
        # 180da0610's case 0 / 1: the colour's and the outline's alpha x +0xb8, V_roundf, cast to the byte
        def sc(c, on=True):
            a = c[3] if on else 0
            a = int(f32(math.copysign(math.floor(abs(f32(a * dyn['alphaMul'])) + 0.5), 1.0))) & 0xff
            return (rgba(c) & 0xffffff if on else 0) | (a << 24)
        col, oc = sc(S['color']), sc(S['outlineColor'], bool(S['outline']))
        if style == 0:
            call(F['bars'], ints=(OBJ, S['t']), floats={2: dyn['dynGap'], 3: S['length']}, stack=(struct.pack('<fI', S['thickness'], 0), col, oc))
        else:
            # 180da6290(obj, r xmm1, thickness xmm2, colour r9, outline colour the 5th slot)
            call(F['circle'], ints=(OBJ, 0, 0, col), floats={1: dyn['dynGap'], 2: S['thickness']}, stack=(oc,))
    nlist = struct.unpack('<I', bytes(uc.mem_read(LIST + 0x1008, 4)))[0]
    shapes = []
    for i in range(min(nlist, 64)):
        e = bytes(uc.mem_read(LIST + i * 0x40, 0x40))
        m0 = struct.unpack_from('<4f', e, 0)
        m1, typ = struct.unpack_from('<fI', e, 0x10)
        m3 = struct.unpack_from('<2f', e, 0x18)
        c4, o4 = struct.unpack_from('<4f', e, 0x20), struct.unpack_from('<4f', e, 0x30)
        shapes.append({'type': typ, 'm0': m0, 'm1': m1, 'o': m3, 'color': c4, 'ocolor': o4})
    cases.append({'S': S, 'dyn': dyn, 'inp': inp, 'h': h, 'cx': cx, 'cy': cy, 'shapes': shapes})
json.dump({'dll': dll.replace('\\', '/').split('/')[-1], 'cases': cases}, open(out, 'w', newline='\n'), indent=0)
print(f'{len(cases)} cases, {sum(len(c["shapes"]) for c in cases)} shapes')
