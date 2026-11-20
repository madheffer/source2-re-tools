# protodesc.py <dll> <file.proto> [Message ...]: a protobuf FileDescriptorProto embedded in a DLL (the serialized
# descriptor the generated code registers), decoded: each message's fields with number, label, type and name. Finds
# the blob by its leading `0x0a <len> <name>` and grows it until it parses (docs/game/README.md).
import sys, pefile
from google.protobuf import descriptor_pb2
d = open(sys.argv[1], 'rb').read()
name = sys.argv[2].encode()
want = set(sys.argv[3:])
TYPES = {v: k[5:].lower() for k, v in descriptor_pb2.FieldDescriptorProto.Type.items()}
LABELS = {v: k[6:].lower() for k, v in descriptor_pb2.FieldDescriptorProto.Label.items()}
i = d.find(b'\x0a' + bytes([len(name)]) + name)
while i >= 0:
    # the blob's end: walk FileDescriptorProto's top-level fields (1..12, length-delimited, or 10 / 11 varints) until a
    # key that isn't one of them
    def varint(p):
        v = s = 0
        while True:
            b = d[p]; p += 1; v |= (b & 0x7f) << s; s += 7
            if b < 0x80: return v, p
    p = i
    first = True
    ends = []
    while p < len(d):
        ends.append(p)
        key, q = varint(p)
        fld, wire = key >> 3, key & 7
        if fld == 1 and not first:
            break  # the next file's name: the next registered descriptor
        first = False
        if wire == 2 and 1 <= fld <= 14:
            ln, q = varint(q)
            if q + ln > len(d): break
            p = q + ln
        elif wire == 0 and fld in (10, 11):
            _, p = varint(q)
        else:
            break
    # the longest run of whole top-level fields that parses (a trailing field can be the next blob's)
    best = None
    for e in [p] + ends[::-1]:
        f = descriptor_pb2.FileDescriptorProto()
        try:
            f.ParseFromString(d[i:e])
        except Exception:
            continue
        if f.message_type:
            best = f
            break
    if best is None:
        print(f"offset 0x{i:x}: no prefix of {p - i} bytes parses", file=sys.stderr)
    if best is not None:
        print(f"{best.name} at file offset 0x{i:x}, package {best.package!r}, deps {list(best.dependency)}")
        for m in best.message_type:
            if want and m.name not in want: continue
            print(f"message {m.name}")
            for fl in m.field:
                print(f"  {fl.number:3d} {LABELS[fl.label]:8s} {TYPES[fl.type] if not fl.type_name else fl.type_name:28s} {fl.name}")
        break
    i = d.find(b'\x0a' + bytes([len(name)]) + name, i + 1)
