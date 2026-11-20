"""docs_numbers.py <old.md> <new.md> | --git <rev> <path>...: the addresses, offsets and numbers a doc lost.

For condensing a trace doc without losing data: every hex value (0x..., or a bare 9-10 digit VA like 180ab7ec0)
and every decimal with a fraction or 3+ digits in the old text must still appear in the new one. Prints what's
missing per file; exits 1 if anything is. With --git, the old text of each path is read from <rev>.
"""
import re
import subprocess
import sys

# boundaries by lookaround, not \b: an address glued to a name (FUN_18030eb50, sub_1800...) still counts
B, E = r"(?<![0-9A-Za-z.])", r"(?![0-9A-Za-z])"
TOKEN = re.compile(rf"0x[0-9a-fA-F]+|{B}1[0-9a-f]{{8,9}}{E}|-?{B}\d+\.\d+(?:e-?\d+)?{E}|{B}\d{{3,}}{E}")


def tokens(text):
    out = set()
    for t in TOKEN.findall(text):
        t = t.lower()
        if t.startswith("0x"):
            t = "0x" + (t[2:].lstrip("0") or "0")
        out.add(t)
    return out


def missing(old, new):
    have = tokens(new)
    # an address may be written with or without 0x, and an offset with or without leading zeros
    alt = {("0x" + t if not t.startswith("0x") else t[2:]) for t in have}
    return sorted(t for t in tokens(old) if t not in have and t not in alt
                  and not re.fullmatch(r"20\d{6}|20\d\d", t))  # dates and build stamps


def main(argv):
    pairs = []
    if argv and argv[0] == "--git":
        rev = argv[1]
        for p in argv[2:]:
            old = subprocess.run(["git", "show", f"{rev}:{p}"], capture_output=True).stdout.decode("utf-8", "replace")
            pairs.append((p, old, open(p, encoding="utf-8").read()))
    else:
        pairs.append((argv[1], open(argv[0], encoding="utf-8").read(), open(argv[1], encoding="utf-8").read()))
    bad = 0
    for name, old, new in pairs:
        lost = missing(old, new)
        if lost:
            bad += 1
            print(f"{name}: {len(lost)} lost: {' '.join(lost)}")
    print(f"{len(pairs)} files, {bad} with losses")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
