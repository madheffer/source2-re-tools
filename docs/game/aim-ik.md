# Aim IK (CNmAimCSTask)

client_20261015. Source file named by its asserts: `game/shared/csgo/animgraph2/tasks/animtask_aim_cs.cpp`. Imports: tier0's V_sincosf / V_acosf (IAT 181aac630 / 181aac628). Checked bit for bit by running the DLL natively (rubikon AimOracle).

## Functions

| Address | Module | What |
|---|---|---|
| FUN_18070dda0 | client | CNmAimCSNode update -> the task ctor FUN_180705390 |
| 180708790 | client | the node's blends |
| 18070ac50 | client | node init |
| 18070ada0 | client | node instantiate |
| FUN_18070d0f0 | client | TrySetupSolverData (bones, per-class solver data) |
| FUN_180709650 | client | the execute |
| 1812f62d0 / 1812f5d50 | client | blend timer update / value |
| 18035ae40 | client | AngleNormalize: outside [-180, 180], `v - 360 floor(v / 360 + 0.5)`, clamped |
| 18070c3a0 | client | (task +0x100) `conj(b) a'`, a' = a negated when conj(b).a has its sign bit set, normalised |
| 180706b10 | client | the weapon drop |
| 1807061e0 | client | the spine |
| 180707dc0 | client | rifle solve (class 3) |
| 180707610 | client | pistol solve (class 2) |
| 180707170 = 180706cd0 | client | knife (1) / equipment (5) solve: the same code |
| 180708400 | client | the weapon clamp |
| 180705a60 / 180705ae0 | client | lo / hi offset fades |
| 180705f30 | client | head toward the tip |
| 1812f70c0 | client | two-bone IK (pose, bone, &target, twist (float), byte, weight) |
| 1812f6530 | client | two-bone solve (M[3], R[3], target, twist) |
| 1812f6c8d .. 1812f7052 | client | the twist pass |
| 181744710 | client | signed angle (twist pass) |
| 1812f6380 | client | radians axis-angle (twist pass) |
| 181748480 | client | transform product a * b (xmm0/1 = a's position+scale / rotation, xmm2/3 = b's) |
| 181748750 | client | transform inverse (rcx = &transform) |
| 181745900 | client | quaternion product (not normalised) |
| 181745980 | client | rotation between unit u and v (rcx, rdx) |
| 181745a60 | client | the same on two vectors normalised first |
| 1812f1b40 | client | a bone's model transform from a parent-space pose (kind 0, pose+0x20) |
| 18070a700 | client | axis-angle (degrees; inlined the same with radians) |
| 1817445e0 | client | AngleQuaternion |
| 18070cae0 | client | rotate a vector |
| 18015a140 | client | VectorNormalize (1 / \|v\| for \|v\| in [1e-17, 1e17], 0 for 0, else in doubles: 181743d60) |
| 180007e80 | tier0 | V_acosf: x clamped to [-1, 1], then the CRT acosf |
| 1802df1e4 | tier0 | CRT acosf: rational fit in z = x² (\|x\| < 0.5) or z = (1 - \|x\|) / 2, ends assembled in doubles |
| 18004db60 / 180130810 / 1801306e0 / 180130720 / 1801307b0 | client | start-up global setters |

## Start-up globals (BSS)

| Address | Value | Set by |
|---|---|---|
| 18236fa60 | quaternion identity (0, 0, 0, 1) (a zero quaternion normalises to it) | 18004db60 |
| 1827210e0 | zero vector (axis-angle helpers' "no axis" test) | 180130810 |
| 182721070 | identity transform (copied from 1827210b0, set first: init table runs 0x1abbf48 before 0x1abbf50) | 1801306e0 / 180130720 |
| 182721110 | (0, 1, 0, 0) | 1801307b0 |

## Fields

Definition (field-info table at 182260xxx):

| Offset | Field |
|---|---|
| +0x18 / +0x1a | m_nVerticalAngleNodeIdx / Horizontal |
| +0x1c / +0x1e / +0x20 / +0x22 | WeaponCategory / WeaponType / WeaponAction / WeaponDrop |
| +0x24 / +0x26 | IsDefusing / CrouchWeight |
| +0x28 | m_flHandIKBlendInTimeSeconds (0.3) |
| +0x2c | m_flActionBlendTimeSeconds (0.4) |
| +0x30 | m_flPlantingBlendTimeSeconds (0.2) |

Instance (18070ada0):

| Offset | Field |
|---|---|
| +0x30 / +0x38 | horizontal / vertical |
| +0x40 / +0x48 | category / type |
| +0x50 / +0x58 / +0x60 / +0x68 | crouch / action / drop / defusing |
| +0x80 / +0x8c / +0x98 | blend timers: plant / hand IK / action. Easing bytes 22 from the word 0x1600 at each (linear and unclamped, like 0); init sets the action timer's (+0x99) to 3 |

Task:

| Offset | Field |
|---|---|
| +0x70 / +0x74 | yaw / pitch |
| +0x78 | drop, clamped [-10, 10] |
| +0x7c | hand IK blend |
| +0x80 | action blend |
| +0x84 | crouch, clamped [0, 1] |
| +0x88 / +0x89 | class / sub-type (from category / type) |
| +0x8c | the mapped pitch |
| +0x100 | weapon rotation difference |
| +0x110 | head's model position |
| +0x11c | aim direction |
| +0x128 / +0x12c | yaw / pitch fraction of the range end |
| +0xe0 | hand target |
| +0x90 .. +0xd0 | bones (below) |

Pose: +0 skeleton (+8 bone count, +0x20 parents), +0x10 transforms, +0x38 flag (set to 1 unless 1 or 4), +0x20. Skeleton +0x48 m_modelSpaceReferencePose (CNmSkeleton schema; data +0x50).

### Bones (TrySetupSolverData)

0x90 pelvis, 0x94..0xa0 spine_0..3, 0xa4 neck_0, 0xa8 head_0, 0xac wpnPivot, 0xb0 wpn (DAT_181ba2594), 0xb4 wpnTip, 0xb8 wpnEnd, 0xbc wpnHand_L, 0xc0 wpnHand_R, 0xc4 hand_L, 0xc8 hand_R, 0xcc arm_upper_L, 0xd0 arm_upper_R. Looked up by global symbol; any missing: the task does nothing.

## Constants

| Value | What |
|---|---|
| 0.0174532924 | degrees -> radians |
| 2^-23 | inverse's zero-scale / zero-length substitute; rotation-between threshold |
| -89, 89 | yaw / pitch clamp |
| 0.001 | yaw / pitch / drop / weight / bone length thresholds |
| 1e-5 / 1e-6 | straight-arm test / reference cross threshold |
| 70, -0.75 | the drop's pitch fade, x offset |

## Maths

SSE throughout; each lane op in floats in the disassembly's order. dpps sums `(x² + y²) + (z² + w²)`.

- Product (181748480): `pos = rot(a.q, b.p) * a.s + a.p`, `rot(q, v) = v + qw t + q x t`, `t = 2 (q x v)`; scale `a.s * b.s`; rotation `a.q b.q` normalised.
- Inverse (181748750): s == 1 rotates the position by the unnormalised conjugate and negates (0 - x); else by the normalised one and scales by -1/s (s 0 -> 2^-23); length 0 -> 2^-23.
- Quaternion product (181745900): `((aw b + ax (bw, -bz, by, -bx)) + ay (bz, bw, -bx, -by)) + az (-by, bx, bw, -bz)`.
- Rotation between (181745980): `m = (u + v) / 2`; `|m|² > 2^-23`: `(u x m, u.m)`; else a turn perpendicular to u (`(uy, -ux, 0, 0)` for `|ux| > 0.5`, else `(0, uz, -uy, 0)`); normalised. 181745a60: lanes with length over 0 normalised first, identity if either is zero.
- Model transform (1812f1b40): the root-most ancestor's, times each ancestor's down, times the bone's own.
- Axis-angle (18070a700): degrees x 0.0174532924, the half angle to V_sincosf; zero axis or angle -> identity.
- Fitted slerp (inlined five times): `a = |dot|`, `h = t - 0.5`, `k = ((3.55644989 - 1.43518996 a) a - 3.24519992) a + 1.09039998`, `l = (0.215637997 a - 1.06020999) a + 0.848012984`, `k1 = (k h² + l) h t (t - 1) + t`, `k0 = 1 - k1`, k1 negated for dot <= 0; `q = normalise(end k1 + start k0)`.

## Blend timer (1812f62d0 / 1812f5d50)

{ state: 0 off, 1 out, 2 in, 3 on; easing; elapsed; duration }.

- On while off -> in from 0; on while out -> in from duration - elapsed; off while in -> out the same; off while on -> out from 0; in / out advance by dt and finish at duration (in -> on, out -> off).
- Value: on 1, off 0, else elapsed / duration eased (3: in-out quadratic, clamped), reversed while out.
- Init (third argument 1): on / off at once, elapsed = duration = the definition's time.

## Node update (180708790, FUN_18070dda0)

1. The frame's sampled events searched for WPN_IK_ACTION_ENDING and WPN_DISABLE_HAND_IK.
2. action = the action node's symbol in {action_reload, action_deploy, action_silencer_attach, action_silencer_detach} unless ACTION_ENDING; hand IK on = no DISABLE_HAND_IK and defusing false; planting = action_c4_plant.
3. Hand IK timer updates while on, but cut to off at once (elapsed = duration = dt) when not; plant timer with !planting; action timer with action.
4. Task inputs: w = plant blend; +0x70 = `clamp(AngleNormalize(horizontal x w), -89, 89)`, +0x74 the same from vertical; +0x84 crouch; +0x80 action blend; +0x78 drop; +0x7c hand IK blend; class / sub from category / type.

## Solver data (the execute's local block, then per-class writes)

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

c = +0x84 (crouch). Grenades (4) and higher: left hand off; class 0 keeps the defaults. The pistol's head max is 35 (r8 still holds the subtrahend: 18070d78c).

## The execute (FUN_180709650)

1. TrySetupSolverData; nothing if a bone is missing.
2. +0x8c: +0x80 > 0: `lo = 40 x +0x80 - 90`, `hi = 90 - 40 x +0x80`, pitch mapped from [-90, 90] onto [lo, hi]; else the pitch.
3. +0x100 = 18070c3a0(wpnPivot.q, (wpnPivot * wpn).q).
4. Drop (180706b10): `v = clamp(1 - +0x80) x (1 - clamp(|pitch| / 70)) x +0x78`; |v| > 0.001: wpn re-placed so (wpnPivot * wpn) moves by (-0.75 |v|, 0, -v) in the pivot's parent space.
5. Spine (1807061e0): the chain from head_0 up (neck, spine_3..0, pelvis); +0x110 the head's model position.
   - Yaw (|yaw| > 0.001): remapped onto 0x00, +0x128 its fraction of the range end; each spine bone's model rotation pre-multiplied by a turn about model Z (weights 0x10), the chain below recomputed, locals written back.
   - Pitch (|p| > 0.001): onto 0x08, +0x12c its fraction; each spine bone's local rotation post-multiplied about local Z (weights 0x20); neck / head by the head range (0x38) x 0x40.
   - +0x11c = (1, 0, 0) turned by AngleQuaternion(pitch, the remapped yaw, 0); wpnPivot's local = spine_3's model transform.
6. Class solve (3, 2, 1, 5), else +0xe0 = wpn's model transform.
7. Left hand (0x68): 1812f70c0(hand_L, +0xe0 * wpnHand_L, twist 0, weight +0x7c); right hand the same.

### Rifle (180707dc0)

1. W = wpnPivot * wpn; R = W in wpnEnd's frame; `s = 1 - clamp(+0x80) / 2`.
2. wpnEnd turned about its local Y by remap(pitch, 0x30) x s; W = End' R.
3. 180708400.
4. +0x80 < 1: aim pass (W turned about wpnEnd so (tip - end) goes toward +0x11c, by the fitted slerp from the full turn at 0 to none at 1).
5. wpnPivot.q *= +0x100; wpn = wpnPivot^-1 W.
6. pitch > -25: 180705f30 with weight `clamp((pitch + 25) / 115)`. +0xe0 = W.

Clamp (180708400): nothing if both offsets within 0.01 or the range is [-90, 90]; pitch <= min: lo faded in from pitch = min (0) to -90 (lo) (180705a60); pitch >= max: hi from max (0) to 90 (hi) (180705ae0); the offset turned by (pivot^-1 W).q, added to its position, W = pivot (that).

Head (180705f30): H = neck * head (model); the turn taking H's local Y onto (tip - H) normalised, pre-multiplied; fitted slerp from H by the weight; head = neck^-1 (H.p, q).

### Pistol (180707610)

1. wpnPivot pre-multiplied by a turn about Y (remap(pitch, 0x30) x s).
2. `g = +0x128 x +0x12c x (pitch < 0 ? 5 : -15)`: pivot tilted about normalise((wpn - pivot) x Z) by g; pivot written.
3. W = pivot * wpn; `r = +0x128 x +0x12c x (yaw < 0 ? -45 : 45)`: W pre-multiplied by a turn about Z.
4. Clamp; aim pass (+0x80 < 1); wpnPivot.q *= +0x100; wpn = pivot^-1 W; +0xe0 = W. No head pass.

### Knife / equipment (180707170 = 180706cd0)

Pivot pre-multiplied by a turn about Y (remap(pitch, 0x30), no s); the same tilt by g; pivot written; +0xe0 = pivot * wpn. No clamp, no aim pass, no +0x100, wpn left as is.

## Two-bone IK (1812f70c0)

1. w = clamp(weight); <= 0.001 nothing.
2. Chain = [grandparent, parent, bone]; base = the grandparent's parent's model transform (182721070 for none); M0..M2.
3. w < 1 (and the byte 0, as the aim passes): the target (the caller's copy) blended toward M2 (fitted slerp, position and scale lerped).
4. Reference copies from m_modelSpaceReferencePose (skeleton +0x50).
5. 1812f6530; locals written back (hand, lower, upper); pose+0x38 = 1 unless 1 or 4; pose+0x20 = 0.

Solve (1812f6530):

1. `a = M1 - M0`, `b = M2 - M1`, `t = target - M0`; la / lb under 0.001: nothing.
2. `c = clamp(-(na.nb))`; `angle = acos((la² + lb² - lt²) / (2 la lb)) - acos(c)` (V_acosf).
3. Axis: `|c + 1| > 1e-5`: normalise(nb x na); else (straight) the reference's (e x d, e = R2 - R1, d = R1 - R0): over 1e-6 -> local (0, 1, 0), else normalise(R1.q^-1 (e x d)), turned by M1.q.
4. Forearm turned by the angle about the axis (hand kept in its frame); upper arm turned by 181745a60(M2 - M0, t) (forearm kept in its frame); M2.q = the target's.
5. Twist pass (twist > 0, 1812f6c8d .. 1812f7052: 181744710, 1812f6380); the aim passes 0.

## Unread

- The anim graph runtime that makes the starting pose: the state machine's transitions, selectors and value nodes (leaves and main pose nodes: anim-graph.md).
