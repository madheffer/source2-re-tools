# CS2's Aim IK (CNmAimCSTask), traced from client.dll 2026-10-15

The port: `web/src/world/anim-graph/aim-cs.js` (the task), `ik2.js` (the two-bone IK), `cs-xform.js` (CS2's transform /
quaternion maths), `nodes-cs.js` AimCS (the node: inputs and blends), `web/src/lib/crt-math.js` (tier0's sinf / cosf /
acosf). Addresses are `client_20261015.dll` in the Ghidra project; the source file named by its asserts is
`game/shared/csgo/animgraph2/tasks/animtask_aim_cs.cpp`.

**Checked bit for bit against the DLL called natively**: `rubikon/tests/AimOracle` loads client_20261015.dll unresolved,
patches its two imports (tier0's V_sincosf / V_acosf, IAT 181aac630 / 181aac628) and the start-up globals it reads,
and runs the execute's body calling the DLL for every step; `node web/server/cs2web/combat/aim-test.mjs [n]` writes seeded cases
(the reference pose disturbed, random aim, blends, crouch, class and sub-type; `AIM_STRAIGHT` straightens arms for the
IK's fallbacks, `AIM_REFSTRAIGHT=1` the reference too, `AIM_HANDS=0` / `AIM_STAGE` for bisecting) and compares every
float of the pose and the task. Result (2026-11-10): V_sincosf, V_acosf, the transform product / inverse, the
quaternion product, rotation-between, the task's quaternion difference, model transforms, and the task for every
class with the hands: **0 differ** (10,000 task cases a class set; 1,487 straight-arm IK solves).

The vector maths is SSE throughout; the port does each lane op in floats in the disassembly's order. dpps sums
(x² + y²) + (z² + w²); a zero quaternion normalises to the identity (18236fa60, BSS: set to (0, 0, 0, 1) by 18004db60).

## Start-up globals (BSS, read by the code here)

| address | value | set by |
|---|---|---|
| 18236fa60 | quaternion identity (0, 0, 0, 1) | 18004db60 |
| 1827210e0 | zero vector (the axis-angle helpers' "no axis" test) | 180130810 |
| 182721070 | identity transform (copied from 1827210b0, set first: the init table runs 0x1abbf48 before 0x1abbf50) | 1801306e0 / 180130720 |
| 182721110 | (0, 1, 0, 0) | 1801307b0 |

## The maths (cs-xform.js)

- 181748480 transform product a * b (xmm0/1 = a's position+scale / rotation, xmm2/3 = b's): pos = rot(a.q, b.p) * a.s
  + a.p with rot(q, v) = v + qw t + q x t, t = 2 (q x v); scale a.s * b.s; rotation a.q b.q normalised.
- 181748750 inverse (rcx = &transform): s == 1 rotates the position by the unnormalised conjugate and negates
  (0 - x), else by the normalised one and scales by -1/s (s 0 -> 2^-23); the length 0 -> 2^-23.
- 181745900 quaternion product, not normalised: ((aw b + ax (bw, -bz, by, -bx)) + ay (bz, bw, -bx, -by)) + az (-by, bx, bw, -bz).
- 181745980 rotation between unit u and v (rcx, rdx): m = (u + v) / 2; |m|² > 2^-23: (u x m, u.m); else a turn
  perpendicular to u ((uy, -ux, 0, 0) for |ux| > 0.5, else (0, uz, -uy, 0)); normalised.
- 181745a60: the same on two vectors normalised first (lanes with length over 0), identity if either is zero.
- 18070c3a0 (the task's +0x100): conj(b) a', a' = a negated when conj(b).a has its sign bit set, normalised.
- 1812f1b40 a bone's model transform from a parent-space pose (kind 0, pose+0x20): the root-most ancestor's, times
  each ancestor's down, times the bone's own. Pose: +0 the skeleton (+8 bone count, +0x20 parents), +0x10 transforms.
- 18070a700 axis-angle (degrees -> radians x 0.0174532924, the half angle to V_sincosf; zero axis or angle -> identity);
  inlined the same with radians. 1817445e0 AngleQuaternion; 18070cae0 rotate a vector.
- 18015a140 VectorNormalize (1 / |v| for |v| in [1e-17, 1e17], 0 for 0, else in doubles: 181743d60).
- The fitted slerp (inlined five times): a = |dot|, h = t - 0.5, k = ((3.55644989 - 1.43518996 a) a - 3.24519992) a +
  1.09039998, l = (0.215637997 a - 1.06020999) a + 0.848012984, k1 = (k h² + l) h t (t - 1) + t, k0 = 1 - k1, k1 negated
  for dot <= 0; q = normalise(end k1 + start k0).
- tier0 V_acosf (180007e80): x clamped to [-1, 1], then the CRT's acosf (1802df1e4): a rational fit in z = x² (|x| < 0.5)
  or z = (1 - |x|) / 2, the ends assembled in doubles.

## The node: CNmAimCSNode (FUN_18070dda0 update, 180708790 the blends, 18070ac50 init, 18070ada0 instantiate)

Definition (schema offsets, the field-info table at 182260xxx): +0x18 m_nVerticalAngleNodeIdx, +0x1a Horizontal, +0x1c
WeaponCategory, +0x1e WeaponType, +0x20 WeaponAction, +0x22 WeaponDrop, +0x24 IsDefusing, +0x26 CrouchWeight, +0x28
m_flHandIKBlendInTimeSeconds (0.3), +0x2c m_flActionBlendTimeSeconds (0.4), +0x30 m_flPlantingBlendTimeSeconds (0.2).
Instance (18070ada0): +0x30 horizontal, +0x38 vertical, +0x40 category, +0x48 type, +0x50 crouch, +0x58 action, +0x60
drop, +0x68 defusing; three blend timers +0x80 (plant), +0x8c (hand IK), +0x98 (action, easing +0x99 = 3 set in init).

Blend timer (1812f62d0 update, 1812f5d50 value): { state: 0 off, 1 out, 2 in, 3 on; easing; elapsed; duration }.
On while off -> in from 0; on while out -> in from duration - elapsed; off while in -> out the same; off while on ->
out from 0; in / out advance by dt and finish at duration (in -> on, out -> off). Value: on 1, off 0, else elapsed /
duration eased (3: in-out quadratic, clamped), reversed while out. Init (third argument 1) sets on / off at once with
elapsed = duration = the definition's time.

Per update (180708790): the frame's sampled events are searched for WPN_IK_ACTION_ENDING and WPN_DISABLE_HAND_IK;
action = the action node's symbol in {action_reload, action_deploy, action_silencer_attach, action_silencer_detach}
unless ACTION_ENDING; hand IK on = no DISABLE_HAND_IK and the defusing node false; planting = action_c4_plant. The
hand IK timer updates while on, but is cut to off at once (elapsed = duration = dt) when not; the plant timer with
!planting; the action timer with action.

The task's inputs (FUN_18070dda0 -> the ctor FUN_180705390): w = the plant blend; +0x70 yaw = clamp(AngleNormalize
(horizontal x w), -89, 89), +0x74 pitch the same from vertical (AngleNormalize 18035ae40: outside [-180, 180],
v - 360 floor(v / 360 + 0.5), clamped); +0x84 crouch clamped [0, 1]; +0x80 the action blend; +0x78 the drop node's value
clamped [-10, 10]; +0x7c the hand IK blend; class +0x88 / sub +0x89 from category / type (aim-cs.js classOf).

## Bones (TrySetupSolverData FUN_18070d0f0)

0x90 pelvis, 0x94..0xa0 spine_0..3, 0xa4 neck_0, 0xa8 head_0, 0xac wpnPivot, 0xb0 wpn (DAT_181ba2594), 0xb4 wpnTip, 0xb8
wpnEnd, 0xbc wpnHand_L, 0xc0 wpnHand_R, 0xc4 hand_L, 0xc8 hand_R, 0xcc arm_upper_L, 0xd0 arm_upper_R. Any missing: the
task does nothing. (Looked up by global symbol: the oracle can't call it, its block comes from the cases.)

## The solver data (the execute's local block, then TrySetupSolverData's per-class writes)

| off | default | rifle 3 | pistol 2 | knife 1 | equipment 5 |
|---|---|---|---|---|---|
| 0x00 yaw range | -55, 65 | | | | |
| 0x08 spine pitch | -12.5, 10 | -25.5, 25 | -10c - 25.5, 10 | -15.5, 25 | -15.5, 15 |
| 0x10 yaw weights | .1 .2 .3 .4 | | | | |
| 0x20 pitch weights | .125 .225 .25 .4 | | | | |
| 0x30 weapon pitch | -90, 90 | -15c - 75, 80 | -40, 55 | -35, 25 | -15, 5 |
| 0x38 head pitch | -45, 35 | -35, 20 | 10c - 35, 35 | -35, 20 | -35, 20 |
| 0x40 neck / head | .35 .65 | | | | |
| 0x48 clamp range | -90, 90 | -30, 50 (sub 8: -30, 20) | -70, 50 | | |
| 0x50 lo offset | 0 | -10, 3, -5 (sub 3: 0; 6: -2, 0, 0; 8: -6, 4, -16) | 0 | | |
| 0x5c hi offset | 0 | -1 - 7c, 0c + 3, 8c + 4 (sub 2: 2, 0, 4; 3: 3, 2, 4; 4: -6, 2, 6; 5: 6, 2, 4; 6: 0; 7: -5, 1, 3; 8: -8, 0, 14) | 0, 0, 1 (sub 1: -2, 0, 4) | | |
| 0x68 left hand IK | 1 | 1 | 1 | 0 | 0 (1 for C4, sub 9) |

c = +0x84 (crouch). Grenades (4) and higher classes: left hand off; class 0 keeps the defaults. The pistol's head max
is 35 (r8 still holds the subtrahend: 18070d78c).

## The execute (FUN_180709650)

1. TrySetupSolverData; nothing if a bone is missing.
2. +0x8c: +0x80 > 0: lo = 40 x +0x80 - 90, hi = 90 - 40 x +0x80, pitch mapped from [-90, 90] onto [lo, hi]; else the pitch.
3. +0x100 = 18070c3a0(wpnPivot.q, (wpnPivot * wpn).q).
4. 180706b10 the drop: v = clamp(1 - +0x80) x (1 - clamp(|pitch| / 70)) x +0x78; |v| > 0.001: wpn re-placed so that
   (wpnPivot * wpn) moves by (-0.75 |v|, 0, -v) in the pivot's parent space.
5. 1807061e0 the spine: the chain from head_0 up its parents (neck, spine_3..0, pelvis); +0x110 the head's model
   position; yaw (|yaw| > 0.001): remapped onto 0x00, +0x128 its fraction of the range end, each spine bone's model
   rotation pre-multiplied by a turn about model Z (weights 0x10), the chain below recomputed, locals written back;
   pitch (|p| > 0.001): onto 0x08, +0x12c its fraction, each spine bone's local rotation post-multiplied about local Z
   (weights 0x20), the neck / head by the head range (0x38) x 0x40; +0x11c = (1, 0, 0) turned by AngleQuaternion(pitch,
   the remapped yaw, 0); wpnPivot's local = spine_3's model transform.
6. The class solve (3 180707dc0, 2 180707610, 1 180707170, 5 180706cd0 - the same code as the knife's), else the
   hand target +0xe0 = wpn's model transform.
7. Left hand (0x68): 1812f70c0(hand_L, +0xe0 * wpnHand_L, twist 0, weight +0x7c); right hand the same.

### Rifle (180707dc0)

W = wpnPivot * wpn; R = W in wpnEnd's frame; s = 1 - clamp(+0x80) / 2; wpnEnd turned about its local Y by remap(pitch,
0x30) x s; W = End' R; 180708400 (the clamp); +0x80 < 1: the aim pass (W turned about wpnEnd so (tip - end) goes toward
+0x11c, by the fitted slerp from the full turn at 0 to none at 1); wpnPivot.q *= +0x100; wpn = wpnPivot^-1 W; pitch >
-25: 180705f30 with weight clamp((pitch + 25) / 115); +0xe0 = W.

180708400 the clamp: nothing if both offsets are within 0.01 or the range is [-90, 90]; pitch <= min: lo faded in from
pitch = min (0) to -90 (lo) (180705a60); pitch >= max: hi from max (0) to 90 (hi) (180705ae0); the offset turned by
(pivot^-1 W).q, added to its position, W = pivot (that).

180705f30 the head toward the tip: H = neck * head (model); the turn taking H's local Y onto (tip - H) normalised,
pre-multiplied; the fitted slerp from H by the weight; head = neck^-1 (H.p, q).

### Pistol (180707610)

wpnPivot pre-multiplied by a turn about Y (remap(pitch, 0x30) x s); g = +0x128 x +0x12c x (pitch < 0 ? 5 : -15): the
pivot tilted about normalise((wpn - pivot) x Z) by g; pivot written; W = pivot * wpn; r = +0x128 x +0x12c x (yaw < 0 ?
-45 : 45): W pre-multiplied by a turn about Z; the clamp; the aim pass (+0x80 < 1); wpnPivot.q *= +0x100; wpn =
pivot^-1 W; +0xe0 = W. No head pass.

### Knife / equipment (180707170 = 180706cd0)

The pivot pre-multiplied by a turn about Y (remap(pitch, 0x30), no s); the same tilt by g; pivot written; +0xe0 =
pivot * wpn. No clamp, no aim pass, no +0x100, wpn left as is.

## The two-bone IK (1812f70c0, solve 1812f6530)

1812f70c0(pose, bone, &target, twist (float), byte, weight): w = clamp(weight); <= 0.001 nothing. Chain = [grandparent,
parent, bone]; base = the grandparent's parent's model transform (identity transform 182721070 for none); M0..M2.
w < 1 (and the byte 0, as the aim passes): the target (the caller's copy) blended toward M2 (fitted slerp, position and
scale lerped). The reference copies: the skeleton's +0x50 = m_modelSpaceReferencePose (CNmSkeleton schema: +0x48 the
vector, its data +0x50). Then 1812f6530, then locals written back (hand, lower, upper) and pose+0x38 set to 1 unless 1
or 4, pose+0x20 = 0.

1812f6530(M[3], R[3], target, twist): a = M1 - M0, b = M2 - M1, t = target - M0; la / lb under 0.001: nothing.
c = clamp(-(na.nb)); angle = acos((la² + lb² - lt²) / (2 la lb)) - acos(c) (V_acosf). Axis: |c + 1| > 1e-5: normalise(nb x
na); else (straight) the reference's (e x d, e = R2 - R1, d = R1 - R0): over 1e-6 -> local (0, 1, 0), else
normalise(R1.q^-1 (e x d)), turned by M1.q. The forearm turned by the angle about the axis (hand kept in its frame);
then the upper arm turned by 181745a60(M2 - M0, t) (forearm kept in its frame); M2.q = the target's. The twist pass
(twist > 0, 1812f6c8d ..) isn't ported: the aim passes 0.

## Left

- The anim graph runtime that makes the pose the task starts from: its leaves and main pose nodes are checked against
  animationsystem.dll (docs/game/anim-graph.md), the state machine's transitions, selectors and value nodes not yet.

Settled since the first port: the twist pass (1812f6c8d .. 1812f7052, its signed angle 181744710 and radians axis-angle
1812f6380) is ported and checked (aim-test op 11, any twist and weight); the straight-arm fallback reads CS2's own
m_modelSpaceReferencePose (tools/tp-graph.mjs, exact); the timers' easing bytes are 22 from the instantiate's
word 0x1600 at +0x80 / +0x8c / +0x98 (18070ada0), linear and unclamped like 0, and init sets the action timer's to 3.
