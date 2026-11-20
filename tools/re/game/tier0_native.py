# tier0_native.py <tier0.dll> <in.json> <out.json>: tier0's V_sinf / V_cosf / V_tanf / V_atanf / V_expf / V_powf /
# V_roundf called natively (ctypes) on this machine's CPU, for the inputs of tools/re/tier0-trig-oracle.json (written
# by tier0_trig_oracle.py, which runs the same functions under Unicorn: the SSE2 path). On a CPU with FMA3 the CRT's
# start-up sets its flag (0x1803ab28c) and every function takes its FMA path: this file is that path's oracle
# (tier0-trig-test.mjs checks tier0-fma.js against it). Windows x64 only; the flag read back is written to the file.
import sys, json, struct, ctypes, os

dll, src, out = sys.argv[1], sys.argv[2], sys.argv[3]
os.add_dll_directory(os.path.dirname(os.path.abspath(dll)))
t0 = ctypes.WinDLL(os.path.abspath(dll))
F1 = {}
for n in ('V_sinf', 'V_cosf', 'V_tanf', 'V_atanf', 'V_expf', 'V_roundf'):
    fn = getattr(t0, n)
    fn.restype, fn.argtypes = ctypes.c_float, [ctypes.c_float]
    F1[n] = fn
POW = t0.V_powf
POW.restype, POW.argtypes = ctypes.c_float, [ctypes.c_float, ctypes.c_float]
flag = ctypes.c_int.from_address(t0._handle + 0x3ab28c).value


def fl(b):
    return struct.unpack('<f', struct.pack('<I', b))[0]


def bits(x):
    return struct.unpack('<I', struct.pack('<f', x))[0]


d = json.load(open(src))
rows = []
for xb, *_ in d['rows']:
    x = fl(xb)
    rx = struct.unpack('<f', struct.pack('<f', x * 37.0))[0] if abs(x) < 1e6 else x
    rows.append([xb, bits(F1['V_sinf'](x)), bits(F1['V_cosf'](x)), bits(F1['V_tanf'](x)), bits(F1['V_atanf'](x)), bits(F1['V_roundf'](rx))])
exps = [[xb, bits(F1['V_expf'](fl(xb)))] for xb, _ in d['exp']]
pows = [[bb, eb, bits(POW(fl(bb), fl(eb)))] for bb, eb, _ in d['pow']]
json.dump({'dll': os.path.basename(dll), 'fma': flag, 'rows': rows, 'exp': exps, 'pow': pows}, open(out, 'w', newline='\n'))
print(f'{len(rows)} inputs, fma flag {flag}')
