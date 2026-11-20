# CTiltTwistConstraint (the agents' _TWIST bones)

Read 2026-11-16 from **animationsystem_20261023.dll** (sha256 8aa57d0c..., image base 0x180000000; source2-compiler
tools/re/binaries, the Ghidra project's `/animationsystem_20261023.dll`, whose decompiler fails on the solve: "Forced
merge caused intersection", so this is from the disassembly, tools/re/game/disasm.py). Ported in web/src/world/tilt-twist.js,
checked bit for bit against the DLL called natively: rubikon/tests/AnimOracle ops 14 / 15, web/server/cs2web/combat/tilt-twist-test.mjs.

The constraints come from the model's `m_modelInfo.m_keyValueText` BoneConstraintList (bake/ZClassBake.cs writes them
to ze-players/<class>.json; the stock agent's are player/ctm_sas/ctm_sas.constraints.json). Every twist in the stock
agents and GFL's pack is a CTiltTwistConstraint (248 in ze-players, 2026-11-16); none is a CTwistConstraint.

## Classes (RTTI, tools/re/game/rtti.py)

| class | vtable | slot 7 (+0x38): the solve |
|---|---|---|
| CBoneConstraintBase | 1806eb570 | |
| CBaseConstraint | 1806eb608 | _purecall 1805ef7bc |
| CTiltTwistConstraint | 1806eb6a0 | 1804b7fc0 -> jmp 1804b7ca0 |
| CTwistConstraint | 1806f4368 | 1804b7fd0 (not ported: m_bInverse, the parent / child bind rotations) |
| CAimConstraint | 1806f42e0 | 1804b59f0 |
| CPointConstraint | 1806f41d0 | |

CTiltTwistConstraint's other overrides against CBaseConstraint (tools/re/game/vdiff.py): 0x0, 0x8, 0x10, 0x18, 0x20, 0x28,
0x38, 0x48. Slot 9 (+0x48) 1804bb1a0 is the init (below); slot 14 (+0x70) 1804b55c0 the "should run" test the solve
calls first (false when byte +0x19 is 0; true for a null argument; else a bit test).

## Fields (the instance)

| offset | what |
|---|---|
| +0x38 / +0x3c / +0x40 | slave count (+0x3c & 0x7fffffff), the slaves (CConstraintSlave: +0x20 m_flWeight, +0x30 the bone index at run time, +0x48 a byte: 1804bbf70 skips moving the slave's descendants) |
| +0x48 / +0x50 | target count, the targets (CConstraintTarget: +0x20 m_qOffset, +0x4c the bone index at run time) |
| +0x60 | m_nTargetAxis (0 x, 1 y, 2 z) |
| +0x64 | m_nSlaveAxis |
| +0x68 | byte: a last angle is kept |
| +0x6c | float: the last angle (radians, weighted, unwrapped) |
| +0x70 / +0x74 | the target bone, its parent (-1: none) |
| +0x78 / +0x7c | the slave bone, its parent |
| +0x80 | m_qOffset^-1 (the first target's), set by the init |

Init 1804bb1a0: needs targets and slaves (+0x48, +0x38 non-zero) and 1804b9cd0; +0x80 = targets[0].m_qOffset inverted
(below), +0x70 = targets[0]+0x4c, +0x74 = 1804ae8e0(skeleton, it) (the parent), +0x78 = slaves[0]+0x30, +0x7c its parent.

## The solve 1804b7ca0(this, ?, transforms, ..., arg5)

Transforms are model space, 0x20 each (position xyz, scale, then the quaternion xyzw at +0x10).

1. `this->vfn[0x70](arg5)` false: return 0.
2. rel = the target's q (parent < 0), else qmul(inv(parent.q), target.q). inv(q) = (-x, -y, -z, w) / dpps(q, q) (sign
   mask 180817180, divps), the identity 180b3efd0 when the dot is 0 (cmpeqps + blendvps).
3. x = qmul(+0x80, rel). qmul 180491d80(a, b) = a * b, the same lane order as client.dll's 181745900 (cs-xform.js qmul):
   ((aw b + ax (bw, -bz, by, -bx)) + ay (bz, bw, -bx, -by)) + az (-by, bx, bw, -bz); sign masks 180817190 / 1a0 / 1b0.
4. angle = 1804b8c60(&{pos 180a4be60, x}, +0x60, eps 0.0001 (1807251f4)) * slaves[0].m_flWeight.
5. +0x68 set and +0x6c != angle (ucomiss; NaN unwraps): the unwrap, constants 4 pi 1806ebca0 (12.566371), -2 pi 1806a314c,
   2 pi 1806a2de0, pi 180688b00; floorf 180606f68 (the DLL's CRT):
   P = (last + 2pi) - floorf((last + 2pi) / 4pi) * 4pi - 2pi; A the same of angle; d = A - P; |d| >= pi: d -= 2pi when
   A > P, else d += 2pi; angle = d + last. Not set: +0x68 = 1. Then +0x6c = angle.
6. v = (0, 0, 0), v[+0x64] = angle; QAngle (pitch v[1], yaw v[2], roll v[0]) each x 57.2957764 (18064dad4);
   AngleQuaternion 180490910 -> q.
7. The slave: parent < 0: (its position, q); else parent * (local position, q), local = 18048ebd0(parent) (the inverse)
   18048ea80 * slave (18048ea80 the transform product). Its own local rotation is not kept: q is the whole of it.
8. 1804bbf70(slave, ?, transforms, &result): byte +0x48 clear: every descendant (the bit set walked by 1800865b0) moved by
   result * old^-1 first (skipped when 180490820, unread, passes on the parent-relative result: likely a near-identity
   test); then transforms[slave] = result. Returns 1.

## The angle 1804b8c60(transform, axis a, eps)

q = the transform's rotation normalised (sqrtps(dpps), divps, the identity for 0). M's rows: q turning the x, y, z axes
(globals 180a4bf00 / 180a4bf20 / 180a4bf50, copied at start-up by 180019550 / 180019560 / 1800195b0 from 180725270 /
180688b10 / 180688b20 = (1,0,0), (0,1,0), (0,0,1)); the turn is t = 2 (q x v), v + qw t + q x t (cs-xform.js rotv's
lanes). b = (a + 1) % 3, s = (a + 2) % 3; M[i][j] is row i's component j.

- c = floorf(M[a][a] * 1e7 (1806ebca4) + 0.5 (180725208)) / 1e7, then maxss -1 (180725258), minss 1 (180725214).
- y = c + 1 when 0 > c, else 1 - c; V_acosf(y) (import 18063f3b8) - pi/2 (180691eec): |.| <= eps is "aligned".
- Aligned: |M[b][b] - 1| <= eps: 0; else V_atan2f(M[b][s], M[b][b]) (import 18063f3a0).
- Tilted: len = sqrt(M[a][s]² + M[a][b]²), maxss FLT_MIN (180691b60); nb = (1 / len) M[a][b], ns = (1 / len) M[a][s];
  V_atan2f(M[s][a] nb - M[b][a] ns, -M[b][a] nb - M[s][a] ns).

## AngleQuaternion 180490910(QAngle* in degrees)

Each angle x 0.0087266462 (pi / 360, 1806a6e50) through V_sincosf (import 18063f2b0): sp / cp (pitch), sy / cy (yaw),
sr / cr (roll). srcp = sr cp, srsp = sr sp, crsp = cr sp, crcp = cr cp; x = cy srcp - sy crsp, y = cy crsp + sy srcp,
z = sy crcp - cy srsp, w = sy srsp + cy crcp.

## What the bind pose says

m_qOffset is the target's bind rotation in its parent (leg_upper_L's: (0.0187, -0.1307, 0.9912, 0.0098), a near-180
degree turn): at the bind pose x is the identity and the twist 0. The solve at the bind pose gives each twist bone's
authored rotation (tilt-twist-test.mjs; arm_lower_L_TWIST's bind 0.0122 against the solve's 0.0061, the right arm's, is
the model's own data).

## Not read

- 18048ebd0 / 18048ea80 (the transform inverse and product) are not compared with client.dll's xinv / xmul: the port
  writes the slave's local rotation into the model's tree instead (world/body.js, body-rig.js).
- CTwistConstraint 1804b7fd0, CAimConstraint 1804b59f0, CPointConstraint, COrientConstraint, CBoneConstraintDotToMorph.
- Where the constraints run in the frame (after the anim graph's pose; the caller of slot 7) and in what order: taken
  as the list's order.
