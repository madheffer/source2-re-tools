# vpkgrep.py <pak_dir.vpk> <path regex> <content regex> [context bytes]: files whose path matches, searched as bytes
import sys, re, vpk
pak = vpk.open(sys.argv[1])
pr = re.compile(sys.argv[2])
cr = re.compile(sys.argv[3].encode())
ctx = int(sys.argv[4]) if len(sys.argv) > 4 else 200
for path in pak:
    if not pr.search(path): continue
    try: data = pak[path].read()
    except Exception as e:
        print('ERR', path, e); continue
    for enc in (None, 'utf-16-le'):
        d = data if enc is None else data.decode('utf-16-le', 'ignore').encode('utf-8', 'ignore')
        for m in cr.finditer(d):
            a, b = max(0, m.start() - ctx), min(len(d), m.end() + ctx)
            print(f'== {path} @{m.start()}{" (utf16)" if enc else ""}')
            sys.stdout.buffer.write(d[a:b].replace(b'\r', b'') + b'\n')
            sys.stdout.flush()
