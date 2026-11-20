# protomsg.py <dll> <MessageName> [...]: one message's DescriptorProto found inside an embedded .proto descriptor (its
# `0x22 <len> 0x0a <len> <name>` field), decoded alone: field numbers, labels, types, names. For a FileDescriptorProto
# protodesc.py can't parse whole (docs/game/README.md).
import sys
from google.protobuf import descriptor_pb2
d = open(sys.argv[1], 'rb').read()
TYPES = {v: k[5:].lower() for k, v in descriptor_pb2.FieldDescriptorProto.Type.items()}
LABELS = {v: k[6:].lower() for k, v in descriptor_pb2.FieldDescriptorProto.Label.items()}
def varint(p):
    v = s = 0
    while True:
        b = d[p]; p += 1; v |= (b & 0x7f) << s; s += 7
        if b < 0x80: return v, p
for name in sys.argv[2:]:
    nb = b'\x0a' + bytes([len(name)]) + name.encode()
    i = d.find(nb)
    done = False
    while i >= 0 and not done:
        # back up to the 0x22 (field 4, message_type) whose length covers this
        for back in range(2, 5):
            s = i - back
            if d[s] != 0x22: continue
            ln, q = varint(s + 1)
            if q != i: continue
            m = descriptor_pb2.DescriptorProto()
            try:
                m.ParseFromString(d[q:q + ln])
            except Exception:
                continue
            print(f"message {m.name} (file offset 0x{q:x})")
            for fl in m.field:
                print(f"  {fl.number:3d} {LABELS[fl.label]:8s} {TYPES[fl.type] if not fl.type_name else fl.type_name:28s} {fl.name}")
            for nm in m.nested_type:
                print(f"  nested {nm.name}: " + ', '.join(f'{f.number} {f.name}' for f in nm.field))
            done = True
            break
        i = d.find(nb, i + 1)
    if not done:
        print(f"{name}: not found")
