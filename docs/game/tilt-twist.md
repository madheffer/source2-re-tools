# CTiltTwistConstraint (the agents' _TWIST bones)

animationsystem_20261023 (sha256 8aa57d0c..., image base 0x180000000), from the disassembly (Ghidra's decompiler fails
on the solve: "Forced merge caused intersection"). Checked bit for bit against the DLL called natively (AnimOracle ops 14 / 15).

The constraints are the model's `m_modelInfo.m_keyValueText` BoneConstraintList (stock agent: player/ctm_sas/ctm_sas.constraints.json).
Every twist in the stock agents and GFL's pack is a CTiltTwistConstraint (248 of them); none is a CTwistConstraint.

## Functions

| Address | Module | What |
|---|---|---|
| 1805ef7bc | animationsystem | _purecall (CBaseConstraint slot 7) |
| 1804b7fc0 | animationsystem | CTiltTwistConstraint slot 7 (+0x38): jmp 1804b7ca0 |
| 1804b7ca0 | animationsystem | the solve (this, ?, transforms, ..., arg5) |
| 1804b7fd0 | animationsystem | CTwistConstraint solve (m_bInverse, parent / child bind rotations; unread) |
| 1804b59f0 | animationsystem | CAimConstraint solve (unread) |
| 1804bb1a0 | animationsystem | slot 9 (+0x48): init |
| 1804b55c0 | animationsystem | slot 14 (+0x70): "should run" (false when byte +0x19 is 0; true for a null argument; else a bit test) |
| 1804b9cd0 | animationsystem | init precondition |
| 1804ae8e0 | animationsystem | (skeleton, bone): the parent |
| 180b3efd0 | animationsystem | identity quaternion |
| 180491d80 | animationsystem | qmul(a, b) = a * b |
| 1804b8c60 | animationsystem | the angle (transform, axis a, eps) |
| 180490910 | animationsystem | AngleQuaternion (QAngle* in degrees) |
| 18048ebd0 | animationsystem | transform inverse |
| 18048ea80 | animationsystem | transform product |
| 1804bbf70 | animationsystem | write the slave (slave, ?, transforms, &result) |
| 1800865b0 | animationsystem | descendant bit-set walk |
| 180490820 | animationsystem | test on the parent-relative result (unread: likely near-identity) |
| 180606f68 | animationsystem | floorf (the DLL's CRT) |
| 18063f3b8 | animationsystem | V_acosf (import) |
| 18063f3a0 | animationsystem | V_atan2f (import) |
| 18063f2b0 | animationsystem | V_sincosf (import) |
| 180019550 / 180019560 / 1800195b0 | animationsystem | start-up copies of the axis globals |
| 181745900 | client | client.dll's qmul, same lane order as 180491d80 |

## Classes (RTTI)

| Class | Vtable | Slot 7 (+0x38): the solve |
|---|---|---|
| CBoneConstraintBase | 1806eb570 | |
| CBaseConstraint | 1806eb608 | _purecall 1805ef7bc |
| CTiltTwistConstraint | 1806eb6a0 | 1804b7fc0 -> jmp 1804b7ca0 |
| CTwistConstraint | 1806f4368 | 1804b7fd0 |
| CAimConstraint | 1806f42e0 | 1804b59f0 |
| CPointConstraint | 1806f41d0 | |

CTiltTwistConstraint's overrides against CBaseConstraint: 0x0, 0x8, 0x10, 0x18, 0x20, 0x28, 0x38, 0x48.

## Fields

| Offset | Field |
|---|---|
| +0x19 | byte: 0 -> slot 14 false |
| +0x38 / +0x3c / +0x40 | slave count (+0x3c & 0x7fffffff), the slaves |
| CConstraintSlave +0x20 / +0x30 / +0x48 | m_flWeight / bone index at run time / byte: 1804bbf70 skips moving descendants |
| +0x48 / +0x50 | target count, the targets |
| CConstraintTarget +0x20 / +0x4c | m_qOffset / bone index at run time |
| +0x60 | m_nTargetAxis (0 x, 1 y, 2 z) |
| +0x64 | m_nSlaveAxis |
| +0x68 | byte: a last angle is kept |
| +0x6c | float: the last angle (radians, weighted, unwrapped) |
| +0x70 / +0x74 | target bone, its parent (-1: none) |
| +0x78 / +0x7c | slave bone, its parent |
| +0x80 | m_qOffset^-1 (the first target's) |
| transform (0x20 each) | position xyz, scale, quaternion xyzw at +0x10; model space |

## Constants

| Value | What |
|---|---|
| 180817180 | sign mask (quaternion inverse) |
| 180817190 / 1808171a0 / 1808171b0 | qmul sign masks |
| 0.0001 (1807251f4) | eps |
| 12.566371 (4 pi, 1806ebca0), -2 pi 1806a314c, 2 pi 1806a2de0, pi 180688b00 | unwrap |
| 57.2957764 (18064dad4) | rad to deg |
| 180a4be60 | position passed with x to the angle |
| 180a4bf00 / 180a4bf20 / 180a4bf50 | axis globals, from 180725270 / 180688b10 / 180688b20 = (1,0,0), (0,1,0), (0,0,1) |
| 1e7 (1806ebca4), 0.5 (180725208), -1 (180725258), 1 (180725214) | the angle's rounding / clamp |
| pi/2 (180691eec) | aligned test |
| FLT_MIN (180691b60) | len floor |
| 0.0087266462 (pi / 360, 1806a6e50) | AngleQuaternion half-angle |

## Init (1804bb1a0)

Needs targets and slaves (+0x48, +0x38 non-zero) and 1804b9cd0; +0x80 = targets[0].m_qOffset inverted, +0x70 =
targets[0]+0x4c, +0x74 = 1804ae8e0(skeleton, it), +0x78 = slaves[0]+0x30, +0x7c its parent.

## The solve (1804b7ca0)

1. `this->vfn[0x70](arg5)` false: return 0.
2. rel = target's q (parent < 0), else qmul(inv(parent.q), target.q). inv(q) = (-x, -y, -z, w) / dpps(q, q) (divps), the
   identity 180b3efd0 when the dot is 0 (cmpeqps + blendvps).
3. x = qmul(+0x80, rel). qmul: `((aw b + ax (bw, -bz, by, -bx)) + ay (bz, bw, -bx, -by)) + az (-by, bx, bw, -bz)`.
4. angle = 1804b8c60(&{pos 180a4be60, x}, +0x60, 0.0001) * slaves[0].m_flWeight.
5. +0x68 set and +0x6c != angle (ucomiss; NaN unwraps): the unwrap:
   `P = (last + 2pi) - floorf((last + 2pi) / 4pi) * 4pi - 2pi`; A the same of angle; `d = A - P`; |d| >= pi: d -= 2pi
   when A > P, else d += 2pi; `angle = d + last`. Not set: +0x68 = 1. Then +0x6c = angle.
6. v = (0, 0, 0), v[+0x64] = angle; QAngle (pitch v[1], yaw v[2], roll v[0]) each x 57.2957764; AngleQuaternion -> q.
7. Slave: parent < 0: (its position, q); else parent * (local position, q), local = 18048ebd0(parent) 18048ea80 *
   slave. Its own local rotation is not kept: q is the whole of it.
8. 1804bbf70: byte +0x48 clear: every descendant (1800865b0) moved by result * old^-1 first (skipped when 180490820
   passes on the parent-relative result); then transforms[slave] = result. Returns 1.

## The angle (1804b8c60)

q = the rotation normalised (sqrtps(dpps), divps, identity for 0). M's rows: q turning the x, y, z axes; the turn is
`t = 2 (q x v)`, `v + qw t + q x t`. b = (a + 1) % 3, s = (a + 2) % 3; M[i][j] is row i's component j.

- `c = floorf(M[a][a] * 1e7 + 0.5) / 1e7`, then maxss -1, minss 1.
- `y = c + 1` when 0 > c, else `1 - c`; `V_acosf(y) - pi/2`: |.| <= eps is "aligned".
- Aligned: |M[b][b] - 1| <= eps: 0; else `V_atan2f(M[b][s], M[b][b])`.
- Tilted: `len = sqrt(M[a][s]² + M[a][b]²)`, maxss FLT_MIN; `nb = (1 / len) M[a][b]`, `ns = (1 / len) M[a][s]`;
  `V_atan2f(M[s][a] nb - M[b][a] ns, -M[b][a] nb - M[s][a] ns)`.

## AngleQuaternion (180490910)

Each angle x 0.0087266462 through V_sincosf: sp / cp (pitch), sy / cy (yaw), sr / cr (roll).
`srcp = sr cp`, `srsp = sr sp`, `crsp = cr sp`, `crcp = cr cp`; `x = cy srcp - sy crsp`, `y = cy crsp + sy srcp`,
`z = sy crcp - cy srsp`, `w = sy srsp + cy crcp`.

## Bind pose

m_qOffset is the target's bind rotation in its parent (leg_upper_L's: (0.0187, -0.1307, 0.9912, 0.0098), a near-180
degree turn): at the bind pose x is the identity and the twist 0. The solve at the bind pose gives each twist bone's
authored rotation (arm_lower_L_TWIST's bind 0.0122 against the solve's 0.0061, the right arm's: the model's own data).

## Unread

- 18048ebd0 / 18048ea80 not compared with client.dll's transform inverse / product.
- CTwistConstraint 1804b7fd0, CAimConstraint 1804b59f0, CPointConstraint, COrientConstraint, CBoneConstraintDotToMorph.
- Where the constraints run in the frame (after the anim graph's pose; the caller of slot 7) and in what order: taken as the list's order.
- 180490820.
