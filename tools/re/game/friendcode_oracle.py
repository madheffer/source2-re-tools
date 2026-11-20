# friendcode_oracle.py <client.dll> <out.json> [count]: CS2's own friend codes run under Unicorn, for
# web/server/cs2web/lobby/friend-code-test.mjs (docs/game/friends.md "Friend codes").
# client.dll 2026-11-12: 180f88150 (account id -> "XXXXX-XXXX", MyPersonaAPI.GetFriendCode's encoder) and 180f87f90
# (FriendsListAPI.GetXuidFromFriendCode's decode: code -> account id, 0 when it isn't one). Every import is trapped;
# the ones these reach are stubbed: tier0 MD5_ProcessSingleBuffer (hashlib), the formatters (V_vsnprintf family:
# only "AAAA-%.*s" is formatted), the CUtlString / allocator calls when they show up (reported, not guessed).
# Writes { enc: [{ id, code }], dec: [{ code, id }] }: random account ids (and edge ones), every encoded code
# decoded back, plus mutated / random strings for the decoder.
import sys, json, random, struct, hashlib
import pefile
from unicorn import Uc, UC_ARCH_X86, UC_MODE_64, UC_HOOK_CODE, UcError
from unicorn.x86_const import *

dll, out = sys.argv[1], sys.argv[2]
count = int(sys.argv[3]) if len(sys.argv) > 3 else 400
pe = pefile.PE(dll, fast_load=True)
pe.parse_data_directories([pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_IMPORT']])
B = pe.OPTIONAL_HEADER.ImageBase
img = pe.get_memory_mapped_image()
size = (len(img) + 0xfff) & ~0xfff

F_ENC, F_DEC = 0x180f88150, 0x180f87f90
STUB, STACK, HEAP, STOP, TLS = 0x10000000, 0x20000000, 0x30000000, 0x40000000, 0x50000000

uc = Uc(UC_ARCH_X86, UC_MODE_64)
uc.mem_map(B, size)
uc.mem_write(B, bytes(img))
for a in (STUB, STACK, HEAP, STOP, TLS):
    uc.mem_map(a, 0x200000)
uc.mem_write(STOP, b'\xc3')

stubs = {}
n = 0
for entry in pe.DIRECTORY_ENTRY_IMPORT:
    for imp in entry.imports:
        name = (imp.name or b'#%d' % imp.ordinal).decode()
        addr = STUB + 0x10 * n
        n += 1
        stubs[addr] = name
        uc.mem_write(imp.address, struct.pack('<Q', addr))
        uc.mem_write(addr, b'\xc3')
heap = [HEAP]


def rd(a, k):
    return bytes(uc.mem_read(a, k))


def cstr(a, limit=4096):
    s = b''
    while len(s) < limit:
        c = rd(a, 1)
        if c == b'\0':
            break
        s += c
        a += 1
    return s


def alloc(k):
    a = heap[0]
    heap[0] += (k + 15) & ~15
    return a


def ret(val=None):
    if val is not None:
        uc.reg_write(UC_X86_REG_RAX, val)
    rsp = uc.reg_read(UC_X86_REG_RSP)
    uc.reg_write(UC_X86_REG_RIP, struct.unpack('<Q', rd(rsp, 8))[0])
    uc.reg_write(UC_X86_REG_RSP, rsp + 8)


def fmt(f, args):
    # only what these functions format: "AAAA-%.*s" (precision, string)
    if f == b'AAAA-%.*s':
        p, s = args[0] & 0xffffffff, cstr(args[1])
        return b'AAAA-' + s[:p]
    raise RuntimeError(f'format {f!r}')


unknown = []


def hook(uc_, addr, size_, _):
    name = stubs.get(addr)
    if not name:
        return
    rcx, rdx, r8, r9 = (uc.reg_read(r) for r in (UC_X86_REG_RCX, UC_X86_REG_RDX, UC_X86_REG_R8, UC_X86_REG_R9))
    if name == 'MD5_ProcessSingleBuffer':
        uc.mem_write(r8, hashlib.md5(rd(rcx, rdx)).digest())
        ret(0)
    elif name in ('V_snprintf', '_V_snprintf'):
        rsp = uc.reg_read(UC_X86_REG_RSP)
        args = [r9] + [struct.unpack('<Q', rd(rsp + 0x28 + 8 * i, 8))[0] for i in range(4)]
        s = fmt(cstr(r8), args)[:rdx - 1] + b'\0'
        uc.mem_write(rcx, s)
        ret(len(s) - 1)
    elif name in ('V_vsnprintf', '_V_vsnprintf', 'V_vsnprintfRet'):
        va = r9
        args = [struct.unpack('<Q', rd(va + 8 * i, 8))[0] for i in range(4)]
        s = fmt(cstr(r8), args)[:rdx - 1] + b'\0'
        uc.mem_write(rcx, s)
        ret(len(s) - 1)
    elif name == '?AppendFormatV@CBufferString@@QEAAHPEBDPEAD@Z':
        # CBufferString::AppendFormatV(this, fmt, va): the decoder's "AAAA-%.*s" into a fresh stack CBufferString,
        # kept inline (+4 bit 30 set: the text at +8, as 180f87fc4 reads it)
        args = [struct.unpack('<Q', rd(r8 + 8 * i, 8))[0] for i in range(4)]
        s = fmt(cstr(rdx), args)
        uc.mem_write(rcx + 4, struct.pack('<I', 0x40000000 | len(s)))
        uc.mem_write(rcx + 8, s + b'\0')
        ret(len(s))
    elif name.startswith('?Purge@CBufferString@@'):
        ret(0)
    elif name in ('MemAlloc_AllocFunc', 'MemAllocAllocFunc'):
        ret(alloc(rcx))
    elif name in ('MemAlloc_FreeFunc', 'MemAllocFreeFunc'):
        ret(0)
    else:
        unknown.append(name)
        uc.emu_stop()


uc.hook_add(UC_HOOK_CODE, hook, begin=STUB, end=STUB + 0x10 * n)


def call(fn, rcx=0, rdx=0):
    heap[0] = HEAP
    rsp = STACK + 0x1f0000
    rsp -= 8
    uc.mem_write(rsp, struct.pack('<Q', STOP))
    uc.reg_write(UC_X86_REG_RSP, rsp)
    uc.reg_write(UC_X86_REG_RCX, rcx)
    uc.reg_write(UC_X86_REG_RDX, rdx)
    uc.reg_write(UC_X86_REG_GS_BASE, TLS)
    del unknown[:]
    uc.emu_start(fn, STOP, count=10_000_000)
    if unknown:
        raise RuntimeError(f'unstubbed import {unknown[0]}')
    return uc.reg_read(UC_X86_REG_RAX)


def encode(acct):
    buf = alloc(64)
    uc.mem_write(buf, b'\0' * 64)
    # returns the text past "AAAA-" (180f8851d: the prefix compared, rax = buf + 5), else a fixed string
    p = call(F_ENC, acct, buf)
    assert p == buf + 5, (acct, cstr(buf))
    return cstr(p).decode()


def decode(code):
    s = alloc(64)
    uc.mem_write(s, code.encode() + b'\0')
    return call(F_DEC, s) & 0xffffffff


rng = random.Random(730)
ids = [1, 2, 15, 16, 0xff, 0x1000, 0xffff, 0x10000, 0x7fffffff, 0x80000000, 0xfffffffe, 0xffffffff, 22202, 81064584]
ids += [rng.randrange(1, 2 ** 32) for _ in range(count)]
ids += [rng.randrange(1, 2 ** 28) for _ in range(count // 4)]
enc = [{'id': i, 'code': encode(i)} for i in ids]
ALNUM = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
codes = [e['code'] for e in enc]
for c in list(codes[:count // 2]):
    k = rng.randrange(len(c))
    if c[k] != '-':
        codes.append(c[:k] + rng.choice(ALNUM) + c[k + 1:])  # one changed character: mostly a bad hash
    codes.append(c.lower())
    codes.append(c.replace('-', ''))
codes += [''.join(rng.choice(ALNUM) for _ in range(5)) + '-' + ''.join(rng.choice(ALNUM) for _ in range(4)) for _ in range(count)]
codes += ['', 'A', 'AAAAA-AAAA', 'SUCJS-SDAO', '99999-9999', 'ZZZZZ-ZZZZ', 'IIIII-OOOO', 'AAAA-AAAAA-AAAA', '00000-0000']
dec = [{'code': c, 'id': decode(c)} for c in codes]
json.dump({'dll': 'client_20261112.dll', 'enc': enc, 'dec': dec}, open(out, 'w', newline='\n'), indent=0)
print(f'{len(enc)} encodes, {len(dec)} decodes ({sum(1 for d in dec if d["id"])} valid)')
