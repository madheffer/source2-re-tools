# CS2 movement, traced from server.dll 2026-11-05 (RUST_PORT phase 2)

Working notes for `sim/src/movement/`. `svc` = CCSPlayer_MovementServices (RCX), `mv` = CMoveData (RDX), `pawn` =
svc+0x38. Addresses are server_20261105.dll in the Ghidra project. "read" = read in the decompiler, sums still to check
in the disassembly where they decide bits.

## CMoveData fields seen

| mv+ | what |
|---|---|
| 0x2c / 0x30 / 0x34 | forward / side / up move (CheckParameters scales them by maxspeed at its end) |
| 0x38 / 0x3c / 0x40 | velocity x / y / z |
| 0x44 / 0x48 / 0x4c | view angles (pitch, yaw, roll); 0xf4..0xfc the command's angles |
| 0xc8 / 0xcc / 0xd0 | origin |
| 0xe8 | (cleared at the PlayerMove prelude: FUN_180189990(mv+0xe8, 0, 0, 0)) |
| 0x108..0x110 / 0x114..0x11c | the piece's acceleration / the half-step part already applied (vfn 0x118 zeroes both) |
| 0x120 | max speed |
| 0x139 | the command right after CCSPlayerPawn::Teleport (SetupMove: cmd+8 == svc+0x680 + 1): the prelude runs CategorizePosition, not sv_optimizedmovement's check |

## svc fields seen

| svc+ | what |
|---|---|
| 0x58 | buttons (u64): bit 2 = IN_DUCK, bit 16 (0x10000) = IN_SPEED (walk), bit 0 = IN_ATTACK? |
| 0x25c | m_flFallVelocity |
| 0x26c | m_surfaceFriction (1.0 at CategorizePosition's start; 0.25 airborne moving up) |
| 0x410 / 0x415 / 0x416 | duck: m_flDuckAmount? (410 -2 clamp), m_bDucked? (415 = IN_DUCK copy), 416 |
| 0x428 | the ground trace's hit (body) |
| 0x438 | flag cleared on duck press |
| 0x648 | the trace count: incremented at each call site of the trace wrapper 180addc00 (TestPlayerPosition twice), not by CanUnduck or the duck's air check (TraceShape directly) |
| 0x654 | water level at the prelude's end (for Water.PlayerEnter / Exit) |
| 0x69c | m_flStamina (decays by sv_staminarecoveryrate (handle 0x182175438) x frametime in the prelude) |
| 0x6b8 / 0x6d0 | legacy / modern jump objects (sv_legacy_jump = DAT_1821755b0) |
| 0x6e0..0x700 | the modern jump object m_ModernJump (+0x10..0x30: 0x6f0 / 0x6f4 m_nLastLandedTick / Frac, 0x6f8..0x700 m_flLastLandedVelocityX / Y / Z; "The modern jump") |
| 0x7b0 | the trace helper (FUN_180addc00 = TraceShape with the movement filter) |
| 0xfd4 | stuck-on-ground counter (> 31: FUN_18021a120) |

Globals: PTR_DAT_181e328d0+0x34 = gpGlobals->frametime. FUN_180187770(cvar) reads a float cvar.

## The dispatch: FUN_180adc390 (PlayerMove's movetype switch)

Pawn vfn 0xcb8 false (can't move) → CheckParameters, 180adc860 (the frozen / dead move), "Can't move". Else, the
pawn's +0xb30 (trigger velocity / grab?) with +0x54 > 0: CheckParameters, prelude 180adce30, then the +0x54 timer
(cap 10000, minus frametime x 1000; at 0 or out of water: cleared, FUN_1803e8520(pawn, 4)); velocity x/y from +0x58 /
+0x5c; then 180ae6e40, 180abe290, 180adcb90. Otherwise by movetype (FUN_1803d95f0):
- water level (FUN_1803d9e40) > 2 and WALK (2): CheckParameters, 180add3f0 (the water move)
- 2 WALK: CheckParameters, FullWalkMove 180adca80(svc, mv, 0)
- 4: CheckParameters, prelude, 180ac1ec0, 180ac5720, 180adcb90
- 7 / 8 (noclip / observer): CheckParameters (its speed factors and stamina skipped), prelude, 180ac1ec0, 180ac5640(svc, mv,
  sv_noclipspeed (x 1 / host_timescale above 1), sv_noclipaccelerate), PostMove(svc, mv, 0) (180adc694; earlier notes missed
  CheckParameters and PostMove)
- 9 LADDER: CheckParameters, prelude; if the prelude left it not WALK: 180ac1ec0, 180abe290, the jump object
  (legacy 180abbcb0 / modern 180abbe60), 180adf4b0 (ladder move), 180ae6e40, 180adeec0, 180adcb90; if it became WALK:
  FullWalkMove(svc, mv, 1) (prelude already run)

- **any other movetype** (0 NONE, 1, 3, 5 VPHYSICS, 6, 10+): the switch returns at once (after the 9 test, `if (type
  != 9) return`): no CheckParameters, no prelude, no duck, no gravity, no velocity applied. The pawn stays where it
  is with the velocity it had. Read 2026-11-18 for ze_resident_evil_3's zombie NPCs, whose grab fires `KeyValues
  movetype 1` at the human and `movetype 2` to let go.

### A movetype without a move (a map's `movetype` keyvalue)

CS2Fixes' customio.cpp `AddOutputCustom_MoveType` (key "movetype", two tokens) is
`SetMoveType(clamp(Q_atoi(value), MOVETYPE_NONE, MOVETYPE_LAST))` and nothing else (no Teleport, no velocity change).
Ours: keyvalues.js playerInput -> the player hook setMoveType (server/cs2web/core/player.js) -> the mover's
`moveNone` (2 clears it, 7 is noclip, any other but 4 / 8 / 9 sets it) -> the move job's flag 0x4000 -> prelude.rs
run_piece returns before check_parameters, past the can't-move branch and a running water jump (the switch's order).
`moveNone` is in the replicated move state (move-state.js BOOL), so the owner's prediction holds still too.
STAND-IN: 4 (fly), 8 (observer) and 9 (ladder) set by a map leave the type as it was (their moves exist in the sim
only as the dispatch reaches them itself).

## FullWalkMove: FUN_180adca80(svc, mv, skipPrelude)

prelude 180adce30 unless skipped (returns 0: stop) → 180ac1ec0 (duck?) → jump object (legacy 180abbcb0(svc+0x6b8) /
modern 180abbe60(svc+0x6d0, mv)) → pawn+0x388 bit 0 ? 180aea7d0 : 180ae34a0 (the walk / air move) → 180adcb90 (post)
→ Water.PlayerEnter / Exit when the level crossed 0 (pawn+0x1478 and +0xb50+0x408 clear).

## The prelude: FUN_180adce30(svc, mv) → bool

1. mv+0xe8 cleared; FUN_180c5fdb0(mv).
2. Stamina: s = svc+0x69c; if s > 0: s -= cvar(1821_75438) x frametime; < 0 → 0.
3. pawn+0xb30's +100 timer -= frametime x 1000, floor 0.
4. FUN_181472530(mv+0x14, svc+0x65c, svc+0x668, svc+0x674) (AngleVectors of the view angles: what every move reads; the punch never enters, "The view punch" below).
5. Cvar 1821754b0 on: a movement filter (180ab55b0, group 0xb, interacts-with pawn+0x608 | 0x20 when pawn vfn 0xc20)
   and the hull (180cb7b90: +0xc / +0x18 standing, +0x24 / +0x30 ducked (svc+0x408 byte), +0x48 / +0x54 when
   180b5d1b0(pawn)); 180adefc0(svc+0x7b0, hull, origin, filter, maxspeed / 64, cvar 1821d3588) (an unstick?).
6. Movetype not 7 / 0 / 8 and FUN_1803d9090(pawn) != 2: 180abd670(svc, mv) nonzero → return 0 (stuck).
7. WALK and !mv+0x139 and cvar 1821_75608: vz > 250 → 180ae1cf0(svc, mv, null) (ground off); else CategorizePosition
   180abb1d0(svc, mv, 0).
8. svc+0x654 = water level. No ground entity (pawn vfn 0x668 null): WALK → fall velocity = max(fall, -vz) (when
   fall > 0, else -vz); not WALK → 0.
9. svc vfn 0x1a8(svc, svc+0x428, origin, velocity) (CheckFalling?); FUN_1803d9090 != 2 and 180ad5150 false and
   LADDER → movetype WALK (FUN_1803eb7d0(pawn, 2, 0)), pawn+0x2f2 = 0.
Returns 1.

## CategorizePosition: FUN_180abb1d0(svc, mv, bool)

surface friction = 1. Movetype 7 / 8 → ground off (180ae1cf0(svc, mv, 0)), svc+0xfd4 = 0. start = origin, end =
origin; vz = mv+0x40; moving up = vz > 140 (relative to a ground entity's velocity z when there is one: vfn 0x668,
FUN_1803d6fb0). On a ground entity with pawn+0x404 != 1 (and WALK): end.z -= 180ac70d0 (the step down); with the bool:
end.z -= cvar 1821d3588; else end.z -= 2. LADDER and vz > 0.02, or moving up → ground off. The trace: filter
180ab55b0(group 0xb, interacts-with 180ade310) and a ray built from start (+0, +0, +4 on z), the hull mins (180ac6db0)
less (0, 0, 4)?, the maxs (180ac6e10) — TODO the exact Ray_t layout (stack -0x2c8: start, -0x2b8 maxs, -0x2ac mins).
180addc00(svc+0x7b0, trace, ray, end, ...). svc+0x428 = trace body. A body whose +8 is 0x75de364e: a second trace
with interacts-with 0x3001 replaces it when it hits. trace start-solid and pawn vfn 0x550: svc+0xfd4++ (> 31 →
FUN_18021a120), else 0. 180ad2d00(svc, trace) (is standable) false: 180ae5df0 (the hull-sweep fallback over the four
quadrants?) then if still false: ground off; vz > 0 and not 7/8 → friction 0.25. True: ground on (180ae1cf0(svc, mv,
trace)); with a step down taken, not start solid and 0 < f < 1: origin = trace end.

## CheckParameters: FUN_180abcf10(svc, mv)

- IN_DUCK changed (svc+0x415 vs buttons bit 2): store it; svc+0x410 = max(0, svc+0x410 - 2) (FUN_1801783b0 = max).
- svc+0x438 cleared while ducking.
- Walk (IN_SPEED, not IN_DUCK, not svc+0x416, pawn+0x388 bit 1 clear): if speed (FUN_180225130 of the pawn's
  velocity, FUN_1803d91c0) < maxspeed x 0.52 + 25: maxspeed = maxspeed x 0.52, pawn+0x1478 (m_bIsWalking) = 1.
  Else m_bIsWalking = 0.
- Not 7 / 8: k = svc+0x278 ? *FUN_180c00e80() : 1 (the velocity modifier); pawn+0x388 bit 0: k *= pawn+0x14e0; the
  active weapon (pawn+0xb10 / 0x162*8) when buttons bit 0 and its vfn 0xac0: k *= vfn 0xc58 (the weapon's speed
  while firing?); maxspeed *= k. Stamina s > 0: maxspeed = clamp(1 - s / 100, 0, 1)^2 x maxspeed (FUN_18017b8d0 =
  clamp(v, lo, hi)). Modern jump (sv_legacy_jump 0) with a ground entity: a landing factor from svc+0x700 (vz x 0.0005
  + 1 clamped 0.2..1) and ticks since landing (+0x6f0 / +0x6f4): min(1, ticks x (1/64) x 1.1111894 + f²) x maxspeed (only the whole ticks of now - landed: "The modern jump").
- forward / side / up zeroed unless pawn+0x388 bit 5 clear and FUN_180cf7020(pawn) > 0 (alive?), or the observer
  target's vfn 0xb8 == 4.
- Angles: dead → the command's (mv+0xf4); alive → view + punch (pawn+0xb48 vfn 0x108, FUN_18029f040), roll =
  180ab9560(svc, angles, velocity, cvar 1821d3548, cvar 1821d3538) (CalcRoll) unless 7 / 8; yaw = FUN_1801fe910
  (anglemod).
- Standing on a stack of 2+ ground entities that are players (vfn 0x558), not LADDER and not 180b5d1b0: up = 0,
  forward = maxspeed x 3, and the buttons 8, 0x10, 0x200, 0x400, 2, 4 released (FUN_180c70950).
- forward / side / up x= maxspeed.

## FullWalkMove's branch: pawn+0x388 (m_fFlags) bit 0 FL_ONGROUND → WalkMove 180aea7d0, else AirMove 180ae34a0

More mv fields: 0x14 the move angles (AngleVectors 181472530(mv+0x14, fwd, right, up)); 0x100 / 0x104 the wish
velocity (WalkMove writes it); 0x108..0x110 **the move's acceleration** (a = Δv / frametime, integrated half before
and half after the move); 0x114..0x11c the half-step part already applied (taken back out at the end); 0x13a a bool.
FUN_180308890(globals) and FUN_180ac7100(mv) / 180ac70e0(mv): times (TODO: read). DAT_181ff57a0 = sv_gravity.

### AirMove 180ae34a0(svc, mv)

1. fwd, right from mv+0x14; svc+0x714 (just jumped?) and no ground entity and vz <= 0: low = vz > -(t x g x 0.5) with
   t = FUN_180308890(globals); svc+0x714 = 0.
2. fwd.z = right.z = 0; each normalized as (y² + 0) + x² → sqrt, < 1e-17 or > 1e17: FUN_1814738b0 (zero length: 0),
   else x 1/len (z = 1/len x 0).
3. wish = fwd x fmove + right x smove (x: fwd.x f + right.x s; y: right.y s + fwd.y f — the sum order differs per lane),
   z 0; wishdir = normalize (same rule); wishspeed = len, capped at maxspeed (len == 0 → maxspeed? no: when len is 0
   the cap compare is skipped and wishspeed = len... TODO: the `(false || fVar12 != 0)` gate: len 0 → wishspeed = 0).
4. AirAccelerate 180ab7420(svc, mv, wishdir, wishspeed, sv_airaccelerate DAT_1821d3500).
5. 180ab72d0(svc, mv) (TODO).
6. Half-step: h = frametime x a x 0.5 (a = mv+0x108..); velocity -= h; mv+0x114 += h.
7. velocity += base velocity (FUN_1803d7740(pawn)).
8. Modern jump only: 180adef70(svc+0x6d0, mv).
9. low and 2D speed > 0: vz kept aside, vz = 0; if speed x frametime < 0.09375: velocity = wishdir x (0.09375 /
   frametime); TryPlayerMove 180ae6e40(svc, mv, 0, 0, 0); velocity xy = 0, vz back; TryPlayerMove again; then
   velocity, a and the half-step part restored (a 2-pass slide: horizontal then vertical).
   Else TryPlayerMove(svc, mv, 0, 0, &blocked): not blocked and svc+0x718 < 1: svc+0x718 += 180ac70e0(mv); blocked:
   svc+0x718 = 0.
10. 180adeec0(svc, mv) (the end: base velocity out, the second half-step?).

### WalkMove 180aea7d0(svc, mv)

1. svc+0x439 = 1; a trace reset; fwd, right from mv+0x14; the ground entity's handle (or -1).
2. fwd.z, right.z zeroed (fwd via FUN_180148890 = normalize, right with the 1e-17 rule) when nonzero.
3. wish = (fwd.x f + right.x s, fwd.y f + right.y s) → mv+0x100 / 0x104; wishdir, len as AirMove; len > 0: pawn+0x1564 = 0.
4. svc+0x690 / 0x694 / 0x698 (a speed-change latch: 180ae0230(2D speed); sets mv+0x13a) — networking of the walk
   speed, TODO: whether it affects movement.
5. 180ae10d0(mv, 2, 0); fall velocity svc+0x25c = 0; **Friction 180ac5310(svc, mv)**; wishspeed = min(len, maxspeed);
   180ae10d0(mv, 2, 0); **Accelerate 180ab6c70(svc, mv, wishdir, wishspeed, sv_accelerate DAT_1821d34f0)**.
6. vz = 0, a.z = 0, half.z = 0. |v|² (x² + y² + z²) > maxspeed²: v x= maxspeed / |v|, and a += (v' - v) / frametime.
7. Half-step: h = frametime x a x 0.5; v -= h; half += h. v += base velocity.
8. t = FUN_180308890(globals) - 180ac7100(mv) x 0.5; |v + t a| < 1 → v = 0, a = 0, half = 0; v -= base velocity; v +=
   half; return.
9. dest = origin + v x frametime (x, y; z the origin's). The movement filter (vtable 0x181923f18, group 0xb,
   interacts-as 0x40000, flags |= 2, the pawn's ids) and the hull (+0x0c / +0x18, ducked +0x24 / +0x30 by svc+0x408,
   +0x48 / +0x54 when 180b5d1b0(pawn)); TraceShape 180addc00(svc+0x7b0, tr, origin, dest, hull, filter).
   (Cvar DAT_182175490: debug overlay.)
10. mv+0xe8 += wishdir x min(len, maxspeed).
11. Fraction == 1: origin = trace end; → 13. Else: on a ground entity, or in water (FUN_1803d9e40), and no trigger
    velocity (pawn+0xb30 +0x54 == 0): TryPlayerMove(svc, mv, &dest, tr, 0); StepMove 180ae49a0(svc, mv, &oldOrigin,
    &oldVelocity); when it returns 0 and 0 < |oldVelocity| (FUN_180225130: 3D length?) < cvar DAT_182175498 and the
    player is pressing a move: oldVelocity x= cvar / |oldVelocity| and StepMove again. → 13. Otherwise
    180adeec0(svc, mv) and return.
13. v -= base velocity; v += half; 180ae4660(svc, mv) (StayOnGround).

## Helpers (exact sums from the disassembly where noted)

- 180a42950 dot(a, b) = (a.z b.z + a.y b.y) + a.x b.x (disasm).
- 1801cd370 length2D = sqrt(x² + y²) (disasm). 180225130: length 3D (TODO order). 1801783b0 max(*a, *b), 1801783c0
  min, 18017b8d0 clamp(v, lo, hi). 1814738b0: normalize's fallback for lengths outside 1e-17..1e17 (TODO).
- 180ae10d0(mv, axis, value): velocity[axis] = value, a[axis] = 0, half[axis] = 0.
- 180adeec0(svc, mv): v -= base velocity; v += half (the second half-step).
- **180ae0230: CSMovementVelocityQuantizer_t**: CQuantizedFloatEncoder (tier0 quantizedfloatencoder.h), set up by
  1803c1030(enc, name, 20 bits, flags 4 = encode zero exactly, -16384, 16384) and applied by 1803c1de0.
  Setup: min < 0 < max keeps flag 4; no round flags so +0x18 = 0; +0x1d = 4 | 4 << 4. Multiplier 1803c6a80:
  m = (2^20 - 1) / (double)(max - min as float) when |range| > 0.001; while 1803d6020 says m x range overflows
  (trunc to u32 > 2^20 - 1, or (double)(2^20 - 1) < m x range) a float f steps down one ULP from 1.0 (integer DEC
  on its bits) and m' = m x f. For +-16384 / 20 bits m = 1048575 / 32768 passes at once. +0x10 = m, +0x20 =
  1 / (2^20 - 1) (double). +0x1e: bit 1 set; bits 2.. = log2(range) when it rounds to a power of two.
  Each special flag (+0x1d >> 4: bit 0 min, bit 1 max, bit 2 zero) is cleared when 1803c1f70 says that value already
  encodes exactly. Quantize(v): +0x1e bit 0 → v. v < min → min; v > max → max. For i in 0..3 with that special bit:
  v == (min | max | 0) → that value. Else q = (u32)(i64)((double)(v - min) x m + 0.5);
  r = (float)((double)q x inv x (double)(max - min) + (double)min); min(r, max).

## Friction 180ac5310(svc, mv)

Skipped with a trigger velocity (pawn+0xb30 +0x54 != 0). speed = length2D(v) (1801cd370 on mv+0x38).
q = svc+0x690 ? svc+0x698 : quantize(speed) (TODO: check the call's argument is that length). q >= 0.1:
drop = 0; on ground (pawn vfn 0x660): friction = sv_friction (1821d3560) x surface friction (svc+0x26c) x pawn
friction (1803d8270(pawn)); control = max(q, sv_stopspeed 1821d3460); decel = control x ((sv_friction x
surface) x pawn) (180ac53ee..5431; the move oracle corrected the order); drop = frametime x decel + 0. speed > 0 and frametime > 0: speed < drop → decel = speed / frametime;
a -= normalize3D(v) x decel (normalize: (z² + y²) + x², the 1e-17 / 1e17 rule).
stored = max(0, drop - speed) → mv+0x128. mv+0xe8 = v. speed > 0: v x= max(0, speed - drop) / speed (all axes).

## Accelerate 180ab6c70 → 180ab6d30(svc, mv, frametime, wishdir, wishspeed, accel)

Gate: pawn+0xd40 == 0 needs no trigger velocity; pawn+0xd40 != 0 needs 180b5d1b0(pawn). Then:
cur = dot(v, wishdir); add = wishspeed - cur; add <= 0 → return. curPos = max(cur, 0).
ducking = IN_DUCK || svc+0x416 || pawn flags bit 1 (FL_DUCKING). walking = IN_SPEED && !ducking.
goal = max(250, wishspeed). scale = 1, goalW = goal.
sv_accelerate_use_weapon_speed (182175470) and an active weapon: wmax = weapon vfn 0xc20; scoped = vfn 0xcb0 (m_zoomLevel) > 0 &&
vfn 0xc28 (m_nZoomLevels) > 1 && wmax x 0.52 < 110; r = min(1, wmax / 250); (!ducking && !walking) || scoped → scale
= r; goalW = r x goal.
Water level >= 2: goalW x= sv_water_slow_amount (182175570); ducking → DUCK; !walking → s = goal x slow x scale and
FINAL; walking → WALK below. Water < 2: ducking → DUCK; else WALK / plain.
DUCK: goalW x= 0.34; scale = min(0.34, scale).
s = goal x scale. Walking: s x= 0.52 unless the pawn's +0xe38 → +0x48 handle is live or scoped; lim = goalW x 0.52
- 5; lim < curPos: accel' = clamp(1 - max(0, curPos - lim) / max(0, goalW x 0.52 - lim), 0, 1) x accel (below 0:
accel x 0).
FINAL: frametime > 0: rate = s x accel' x surface friction - mv+0x128 / frametime; rate > 0: amount = rate x
frametime; add < amount → rate = add / frametime, amount = add; a += wishdir x rate. v += wishdir x amount (0 if none).

## AirAccelerate 180ab7420(svc, mv, wishdir, wishspeed, accel)

Dead (1803d9090 == 2) or a trigger velocity: nothing. cap = min(wishspeed, sv_air_max_wishspeed 1821754e8);
add = cap - dot(v, wishdir); add <= 0 → nothing. amount = add; frametime > 0: full = wishspeed x accel x surface
friction x frametime; half = full x 0.5; half <= add: amount = half and mv+0x114 += wishdir x (full <= add ? half :
add - half); else amount = add. mv+0xe8 += wishdir x amount; v += wishdir x amount.

## TryPlayerMove 180ae6e40(svc, mv, firstDest*, firstTrace*, blocked*)

blocked = 0. v_orig = v. airborne = !(flags & FL_ONGROUND). snap = cvar 182175580. t = frametime; done = 0.
k = max(1, |v|) ((y² + z²) + x²). The movement filter and hull. On a ground entity with 180ac8970(pawn): v = a = half = 0.
v1 = v (the clip base). Loop:
- |v| == 0 (180225130) → END.
- dest = origin + v t; unless snap && airborne && t != 0: x, y = v t + 0 + origin; z through svc+0x6b4:
  zz = vz t + acc; r = (vz t + 196608) - 196608; dest.z = ((zz - r) + r + 196608 + origin.z) - 196608;
  acc = zz - (dest.z - origin.z).
- planes == 1: dest += n[0] x 0.03125.
- firstDest given and equal to dest → firstTrace; else TraceShape(origin, dest, hull, filter).
- f = fraction; done == 0 and f < 1 and 0.03125 <= |v| t and f |v| t < 0.03125 → f = 0.
- f x k > 0.03125: origin = trace end; v1 = v; planes = 0.
- done += f; f == 1 → END.
- AddTouch 180c4d5f0(mv, trace, v) (the touch list; sums the normals into mv+0xb0). t -= fraction x t (unmodified).
- planes > 4, or (airborne, vz < 0, normal z >= sv_standable_normal 182175520, IsStandable(trace), length2D(v) < 1):
  v = a = half = 0, END.
- n[planes++] = normal.
- planes == 1, WALK, no ground entity: n.z <= sv_walkable_normal (182175510) → blocked = 1, d = -dot(n, v1) x ((1 -
  surface friction) x sv_bounce 1821d3570 + 1); else d = -dot(n, v1); d = max(d, 0) + 0.03125; v1 += n x d; v = v1
  (dot order here: n.z v.z + n.y v.y + v.x n.x). Next iteration.
- More planes: for i: v = v1 + n[i] x (max(0, -dot(n[i], v1)) + 0.03125); ok when dot(v, n[j]) >= 0 for every j != i.
  None: two planes → dir = normalize(n0 x n1) (x = n1.z n0.y - n1.y n0.z, y = n1.x n0.z - n0.x n1.z, z = n0.x n1.y -
  n1.x n0.y); d = (vz dz + vy dy) + vx dx; v = (n1.x x 0 + n0.x x 0) + dx d (same for y, z); then the test below.
  More than two → zero, END.
- dot(v, v_orig) > 0 → next iteration; else zero, END. At most 4 iterations.
END: done == 0 and any planes → zero. lost = length2D(v_orig) - length2D(v): > 1160 → 180ade0a0(svc, mv, 1.0);
> 580 → 180ade0a0(svc, mv, 0.85).

## StepMove 180ae49a0(svc, mv, oldOrigin*, oldVelocity*) → bool

Keep origin o1, velocity; origin = oldOrigin, v = oldVelocity. step = sv_stepsize (1821d3588).
Trace up to origin + (0, 0, step + 0.03125); fraction > 0 → origin = its end. TryPlayerMove(svc, mv, 0, 0, 0).
Trace down to origin - (0, 0, step + 0.0625). Hit (f < 1 or start solid): ok = true; if normal z < sv_walkable_normal
(182175508): ok = false unless |oldVelocity| < 64 and: a box shrunk by 2 on x / y traced to down - step x 0.5 hits
standable, then a trace from origin along 1803e5180(v) and, from its end when f > 0, one down by step + 0.0625 that
hits (1802c35a0) standable → ok. No hit → ok = false.
Keep the step (origin = the down trace's end) when hit and ok and f > 0, unless it went less far along oldVelocity's
xy than o1 did → back to o1 and the velocity; returns 1. Else origin = o1, v = the velocity on entry, returns 0. vz
is restored to the entry's either way.

## Ground and floor

- 180ac70d0 = sv_stepsize (1821d3588). 180308890 = 1/64 (0x3c800000, the tick interval). 180ac7100 = frametime.
  180ac70e0(mv) = mv+0xe0 - mv+0xdc (the piece of the tick this move covers).
- **IsStandable 180ad2d00(svc, trace)**: an entity and not start solid (trace+0xbb); not a player (vfn 0x558):
  normal z (trace+0x98) >= sv_standable_normal (182175518). Players: not the one standing on us, then 180ad2840
  (stand on another player), or cvar 18211a3b0 → 180ae7c60. Else false. (Whole: "Players' bodies" below.)
- **SetGroundEntity 180ae1cf0(svc, mv, trace*)**: new = trace ? trace+8 : null; base velocity adjusted by the ground
  entity's velocity when the ground changes (leaving: + old ground's velocity, z = its z; landing: - the new's);
  1803ea860(pawn, base velocity); 180e95a10(pawn, new). Landing: touch (180c7e7d0); surface friction = min(1,
  surface(*trace)+0x28 x 1.25); trigger velocity +0x54 = 0; AddTouch when the fraction >= 1 and not start solid, or
  the hit isn't the world (trace+0x68 != 0x8000); 180c60e40(mv, trace+0x90); not 7 / 8: vz = a.z = half.z = 0.
- **StayOnGround 180ae4660**: up = origin + (0, 0, 2), down = origin - (0, 0, stepsize). Trace origin → up, then
  (origin.x, origin.y, that trace's end z) → down. 0 < f < 1, not start solid, normal z >= sv_walkable_normal (handle 182175508)
  and |origin.z - end.z| > 1/64 → origin = end.
- AddGravity 180ab72d0: no trigger velocity; g = sv_gravity (181ff5798, 1802a8a50 reads it) x pawn+0x40c (gravity
  scale); vz -= g x frametime; a.z -= g; then the base velocity's z: vz += bz x frametime, a.z += bz; base z = 0.

## Duck 180ac1ec0(svc, mv)

(2026-11-15: svc+0x414 is m_bDuckOverride, set by the C4's arming (180a23df0); it and pawn+0x14be m_bIsDefusing are
the sim's `duck_override` / `defusing` inputs now, with the exact scale orders: docs/game/c4.md "Movement while
planting / defusing".)

svc: 0x408 m_bDucked, 0x40c m_flDuckAmount, 0x410 m_flDuckSpeed, 0x414 (ducking forced? CanUnduck refuses), 0x416
m_bDucking, 0x418 m_flDuckOffset (view), 0x420 m_flLastDuckTime, 0x424 (jump-duck offset, approaches 0 / -8 at
frametime x 6.4 x 8), 0x430 the place the duck speed last recovered from, 0x438 (duck-jump in the air), 0x650 (the
duck slowdown applied this tick). Hull table 180cb7b90 (GetViewVectors): +0 view, +0xc / +0x18 hull, +0x24 / +0x30
duck hull, +0x3c duck view, +0x48 / +0x54 observer hull.
1. 0x424: s = frametime x 6.4 x -8; 0x414 ? max(s + v, -8) : min(v - s, 0).
2. inAir = no ground entity and not LADDER. forced = pawn vfn 0xc20 && cvar 1821755f8.
   spamOk = duck speed >= 1.5 and (FL_DUCKING or sv_timebetweenducks (182175458) + lastDuckTime <= curtime (globals
   +0x30)).
   want = (0x438 && inAir) || 0x414 || forced || (IN_DUCK && spamOk).
3. Dead (180cf7020 < 1) and not observer-ish: 0x414 = 0; FL_DUCKING → FinishUnDuck; return.
4. 0x438 clear:
   - speed = Approach(8, speed, frametime x 3) (180460960(target, value, step): value + step if target - value >
     step, value - step if below -step, else target). speed < 8 and the duck amount not in (0, 1): with the 2D
     distance² from 0x430 to the pawn's origin (1803d6f50) > 4096: speed = Approach(8, speed, frametime x 6);
     speed >= 8: 0x430 = the origin. The pawn's origin, not mv's: on a ladder the prelude's LadderMove has moved mv
     by then and the pawn is still at the piece's start (the move oracle; duck.rs).
   - want: amount < 1 → ducking = 1; ducking: amount = Approach(1, amount, speed x 0.8 x (pawn+0x14be ? 0.4 : 1) x
     frametime); amount >= 1 or inAir... (`(1 <= amount) || ground == null`) → FinishDuck.
   - !want: amount > 0 → ducking = 1; ducking: CanUnduck false → amount = 1, ducked = 1, ducking = 0, FL_DUCKING on
     (1803c5940(pawn, 2)); true → amount = Approach(0, amount, max(1.5, speed) x (0x14be ? 0.4 : 1) x frametime);
     ducked = 0; amount <= 0 or no ground → FinishUnDuck; amount <= 0.75 and FL_DUCKING → FL_DUCKING off
     (1803e8520(pawn, 2)).
   - Slowdown once per tick (0x650): IN_DUCK or ducking or FL_DUCKING: k = (amount x 0.34 + 1) - amount; forward,
     up, side and maxspeed x= k; 0x650 = 1.
5. 0x438 set: not FL_DUCKING → 0x438 = 0, return. inAir: vz > 0 → return; trace the standing hull from origin -
   (hull extents − duck extents) x 1 (origin − ((max − min) − (dmax − dmin)) per axis) down by stepsize with
   CTraceFilterPlayerMovementCS-like vtable 0x181924e18 (group 0xb, interacts 180ade310, team bits 0x180000000 when
   the pawn is a player); start solid or f == 1 → return. Then 0x438 = 0; CanUnduck → FinishUnDuck.
- **FinishDuck 180ac47e0**: in air (no ground, not LADDER, water level < 3): off = ((hull max − min) − (duck max −
  min)) x 0.5 per axis; else off = −(duck min − hull min) (sign flipped by XOR). ducking = 0, ducked = 1,
  lastDuckTime = curtime, FL_DUCKING on; origin += off; duck offset 0x418 −= off.z; 180ac51a0(svc, mv, 1);
  CategorizePosition(svc, mv, 0); amount = 1.
- **FinishUnDuck 180ac4ef0**: in air (no ground, not LADDER): off = ((hull max − min) − (duck max − min)) x −0.5 − 0;
  else off = duck min − hull min. origin += off; 0x418 −= off.z; FL_DUCKING off; ducked = 0, ducking = 0;
  CategorizePosition; amount = 0.
- **CanUnduck 180abab50**: 0x414 → false. Not 7 / 8: end = origin; in air: end −= ((hull max − min) − (duck max −
  min)) x 0.5; on ground: end += hull min... (duck min − hull min). TraceShape with the standing hull (+0xc / +0x18),
  CTraceFilter vtable 0x181924e30 (group 0xb, interacts-as 0x40000, flags |= 2), origin → end: start solid or
  f != 1 → false. True.

## The legacy jump object 180abbcb0(jump = svc+0x6b8: +8 svc, +0x10 m_bJumpBlocked?, +0x14 last press time)

180c80ad0(svc, 2) = IN_JUMP pressed this tick. Neither held (buttons bit 1) nor pressed → return. block cleared when
(block && sv_jump_spam_penalty_time (1821754d8) + last < curtime) or sv_autobunnyhopping (182175628).
CheckJumpButton 180abc3f0. block = 1. Pressed → last = curtime - frametime.

### CheckJumpButton 180abc3f0(jump, mv)

Dead → return. (pawn+0xc98 handle: a vehicle / item whose 180a6ffb0 < 0 → return; pawn+0x15a8 / +0x15a4 a
cooldown → return.) Not autobhop and not pressed → return. Trigger velocity +0x54 != 0: it counts down by frametime
(floor 0), return. Water level > 2: ground off; water type (1803d9e70) 0x8000 → vz = 100, 0x10000 → vz = 80; a.z =
half.z = 0; the swim sound timer pawn+0xb30 +100 <= 0 → 1000 and "Player.Swim" unless walking; return.
Standing on a player (ground vfn 0x558 and not 0x570): onPlayer; when that player is also on a ground: grounded2.
svc+0x439 = 0. No ground entity → return. 180ac8970(pawn) → return. block → return.
180ad63f0(svc, mv); ground off. svc+0x68c = (something from the view angles and frametime, 180c86d00 / 180927cb0 /
1801f95a0 / 18017dc70 with DAT_18178fdc8) → pawn+0x1560; pawn+0x1564 = 0.
svc+0x6a0 = (origin.z + 196608) - 196608; svc+0x6a8 = svc+0x6a4; svc+0x6a4 = 0; svc+0x6ac = stamina (svc+0x69c);
svc+0x6b4 = origin.z - svc+0x6a0 (the snap accumulator TryPlayerMove uses).
|v| > DAT_1817bc124: svc vfn 0x1d0(svc, origin, svc+0x428, 1.0, 1, 0) (the jump's footstep).
svc+0x368 = 1. k = svc+0x278 ? (the velocity modifier object's +4) : 1.
Not IN_DUCK and (CanUnduck): svc+0x438 = 1 and FinishDuck (the jump's duck: crouch-jump in the air). (When pawn vfn
0xc20 too.)
impulse = sv_jump_impulse (1821754c8). vz0 = vz. grounded2: vz = 0. Else: not 0x438, not ducking (0x416), not
FL_DUCKING, not onPlayer: vz = (impulse - sv_gravity x gravity scale (pawn+0x40c) x 0.5 x DAT_18179be50) x k;
else vz = impulse x k, and ducked == 0 with IN_DUCK → flag = 1. a.z = half.z = 0.
180adbeb0(pawn, origin, svc+0x428, flag) (the jump sound / animation). s = 180ab8d30(jump) (the stamina scale);
vz x= s; svc+0x6b0 = s. mv+0xf0 += vz - vz0. Stamina: svc+0x69c = clamp(stamina + sv_staminajumpcost (1821753b8) x
mv+0xf0', 0, sv_staminamax (182175448)). 180ada490(svc, mv). Event player_jump.

## The modern jump (sv_legacy_jump 0, CS2's default; 2026-11-11, sim/src/movement/modern.rs)

server.dll 2026-11-05, disassembly read (capstone, tools/re/game/disasm_consts.py) after the decompiler. Every
`sv_legacy_jump` (1821755b0) reader (xref): CheckFalling 180abbb56, CheckParameters 180abd251, the ladder dispatch
180adc629, FullWalkMove 180adcaad, the water move 180add47d (these three: the legacy object 180abbcb0(svc+0x6b8) or the
modern 180abbe60(svc+0x6d0, mv) at the same place), the step builder's vfn 0x120 180ae2f79, AirMove 180ae3970, the
view offset 180ae9532. Nothing else branches on it.

**The object m_ModernJump** (svc+0x6d0, schema; vtable 0x181923ee8 set by its constructor 180ab4c60, called from the
svc constructor 180ab4dc0 at 180ab5169): +8 the svc, +0x10 / 0x14 m_nLastActualJumpPressTick / Frac (-1024 / 0), +0x18
/ 0x1c m_nLastUsableJumpPressTick / Frac (-1024 / 0; "cleared" = the tick set to -1024 (0xfffffc00), the fraction
kept), +0x20 / 0x24 m_nLastLandedTick / Frac (0 / 0), +0x28 / 0x2c / 0x30 m_flLastLandedVelocityX / Y / Z (0). Each
store is networked (notifies 180ad9d00, 180ad85b0, 180ada0a0, 180ad8f60, 180ad9f70, 180ad8aa0, 180ad8bd0, 180ad8d00,
180ad8e30, one per field). The movement services' reset (180ae2020) doesn't touch it.

**sv_bhop_time_window** (handle 182175400, registered 1800c9040: default 0.0078125 (0x18179be50), flags 0x82000,
"sv_legacy_jump disabled only: The time window (in seconds) around landing where a jump press is considered a bhop
attempt."). W = 1813b9ab0(from_seconds(window x 0.5 (0x18178057c)), (frac + 131072) - 131072) (0x181926a50): a quarter
tick at the default. The one tick: 180c51bc0(0.015625) rounded the same way = (1, 0).

GameTime helpers (a tick int + a fraction in [0, 1)): 1813b8ef0 / 1813b9ab0 build one (carry by V_modff),
1813b8fb0(a, out, b) a - b, **1813b9090(a, out, b) a + b**: s = b.frac + a.frac, frac = s >= 1 ? s - 1 : s, tick =
b + a (+ 1 unless s < 1), a frac still outside [0, 1) through V_modff / 1813b8ef0. **180ab6ad0(a, out, b) the three-way
compare** (every inlined compare here is the same): ticks differ → -1 when a's is lower, else 1; equal → -1 / 1 by the
fraction, 0 equal, -128 (0x80) unordered. 180c629e0 seconds = tick x 1/64 + frac x 1/64. The piece's "now" =
1813b8ef0(1809209f0(mv+0xd4), mv+0xdc) (its start). Helpers on the object: **180ac65f0** = landed (+0x20 / 0x24),
**180ac5f50** = landed + W, **180ac5ec0** = landed + one tick.

**The tick 180abbe60(jump, mv)**:
1. pressed = 180c80ad0(svc, 2) (IN_JUMP pressed this piece). Pressed: now_r = 1813b9ab0(now, (now.frac + 131072) -
   131072); last press (+0x10 / 0x14) = now_r; d = seconds(now_r - the old last press); sv_jump_spam_penalty_time
   (1821754d8) >= d (comiss / jb) → pressed = 0. Else: u = usable (+0x18); u < landed - W (compare -1) or u >= landed +
   W (compare 0 / 1; unordered skips) → usable = now_r.
2. (sv_autobunnyhopping (182175628) and IN_JUMP held (svc+0x58 bit 1)) or pressed → CheckJumpButton 180ae66b0.
3. Else: compare(u, landed - W) negative (-1 / -128) → clear usable. Else u < landed + W → CheckJumpButton; else u <
   landed + one tick → CheckJumpButton; else clear usable.

**CheckJumpButton 180ae66b0(jump, mv)** (no water branch, no water-jump timer, no "pressed" gate: the object did that):
1. m_lifeState LIFE_DEAD (1803d9090 == 2) → clear usable, return. The controller (pawn+0xc98's handle, via the entity
   list 181f47078) with 180a6ffb0 < 0 → clear, return. pawn+0x15a8 set and 1801f95b0(pawn+0x15a4, curtime
   (180927cb0(pawn identity +0x38))) > 1.0 → clear, return (both as the legacy CheckJumpButton: not ported, no movement
   writer).
2. Ground entity (pawn vfn 0x668) null → return (usable kept). Its vfn 0x558 (a player) → onPlayer, and that player's
   ground null → clear, return; 180ac8970(pawn) (someone on this pawn) → clear, return.
3. u = usable, now, landed; c = compare(landed - W, u) (then `neg cl; js`): c is -1 or 0 (u >= landed - W) and
   180ab6ad0(u, landed + W) == -1 → **bhop**; otherwise sv_autobunnyhopping and compare(now, landed + (1, 0)) <= 0
   (`neg; js` again: -1 / 0) → **bhop**. A bhop with sv_autobunnyhopping, or with mv+0x120² < landed vx² + vy² (x² then
   + y²; comiss / jb: unordered too) → t = landed (180ac65f0), mv+0x38 / 0x3c = the landed velocity x / y, jump. Else
   (not a bhop, or a slow one): now < landed + one tick (180ac5ec0, compare -1) → return (usable kept); else jump. So no
   jump goes within a tick of the landing unless it keeps the landing's speed.
4. The jump (180ae6ac0): clear usable; PreventBunnyJumping 180ad63f0; ground off 180ae1cf0(svc, mv, 0); svc+0x439 = 0;
   the jump stamp svc+0x68c = (curtime - frametime (1801f95a0)) + 0.1 (18017dc70), pawn+0x1560 = it, pawn+0x1564 = 0;
   svc+0x6a0 = (origin.z + 196608) - 196608 (0x181926a54), 0x6a8 = 0x6a4, 0x6a4 = 0, 0x6ac = stamina, 0x6b4 = origin.z
   - 0x6a0; (vx² + vy²) + vz² > 19600 (0x181926a4c) → svc vfn 0x1d0(origin, svc+0x428, 1.0, 1, 0) (the footstep); svc+0x368
   = 1; a bot (the controller's +0x388 bit 8) not holding IN_DUCK and CanUnduck → svc+0x438 = 1, FinishDuck; k = the
   landed surface's jumpfactor (svc+0x278 → 180c00e80 +4) or 1; vz0 = vz; svc+0x438 or 0x416 or FL_DUCKING or onPlayer →
   180ae10d0(mv, 2, k x sv_jump_impulse) and the flag when not ducked with IN_DUCK; else 180ae10d0(mv, 2,
   (sv_jump_impulse - ((pawn+0x40c x sv_gravity) x 0.5) x 0.0078125) x k). **180ae10d0(mv, axis, v)**: mv+0x38[axis] =
   v, mv+0x108[axis] = mv+0x114[axis] = 0.
5. s = 180ab8da0(jump, t); vz = s x vz; svc+0x6b0 = s; mv+0xf0 = (vz - vz0) + mv+0xf0; 180adbeb0 (the sound); 180ada490
   (the jump's record). **No stamina cost** (the legacy one's sv_staminajumpcost).

**The jump's scale 180ab8da0(jump, t)**: f = clamp(+0x30 x 0.0005 (0x1819269d4 = 0x3a03126f) + 1.0 (0x181780580), 0.2
(0x3e4ccccd), 1.0) (18017b8d0: lo when lo > v, hi when v > hi); d = (t - landed) + (1, 0) (1813b8fb0, 1813b9090); k =
minss(f + seconds(d) x 0.6 (0x1817b2be0 = 0x3f19999a), 1.0) (1801783c0 = minss); stamina s: 0 > s skips (comiss / ja),
s <= 0 or unordered skips (comiss / jbe); else k x= clamp(1.0 - s / 100 (0x18178fe18), 0, 1).

**CheckParameters' landing slowdown** (180abd251..36d, after the stamina slowdown, sv_legacy_jump 0 and a ground entity
(pawn vfn 0x668)): f as above (from svc+0x700), d = now - landed (1813b8fb0); x = (float(d.tick) (cvtdq2ps: the
fraction unused) x 0.015625 (0x181784dec)) x 1.1111894 (0x181926a00 = 0x3f8e3b74) + f x f; mv+0x120 = minss(x, 1.0)
x mv+0x120.

**AirMove's air record 180adef70(jump, mv)** (180ae3987, after the half step and the base velocity, before the
slide): mv+0x12c = origin.z (mv+0xd0), mv+0x134 = a.z (mv+0x110), mv+0x130 = vz - (a.z x frametime) x 0.5. vfn 0x118
(180ae2706 / 0d) zeroes mv+0x128..0x137 before every piece, so a piece that never ran AirMove has zeros there.

**The landing's record 180ada630(jump, mv, fall)** (CheckFalling 180abbc0f, `fall` = the same fall velocity the legacy
stamina reads (xmm7 from 180abbb5d); the legacy branch adds sv_staminalandcost instead): dz = origin.z - mv+0x12c, frac
= mv+0xe0 (the piece's end), vz = -fall. 0 > dz and 0 > mv+0x130 (v0) and 0 > mv+0x134 (a): disc = (a + a) x dz + v0 x
v0; disc >= 0 (comiss / jb: unordered skips): s = sqrtss(disc), tt = (-v0 - s) / a; 0 > tt → 0, else minss(frametime,
tt); vz = tt x a + v0; frac = tt / 180308890() (1/64) + mv+0xdc. Then landed = 1813b9ab0(1809209f0(mv+0xd4), (frac +
131072) - 131072); the velocity x / y (mv+0x38 / 0x3c) and vz through CSMovementVelocityQuantizer_t (1803c1de0 on
182176538: 20 bits, flags 4, -16384..16384, set up once by 1803c1030) into +0x28 / 0x2c / 0x30.

**The step builder's cuts 180ae2a50(jump, mv)** (vfn 0x120 180ae2c50 at 180ae2f90, after the latch's cut, before the
jump stamp's): T = 1809209f0(mv+0xd4); x = the landing slowdown with now = (T, 0); 1.0 > x (comiss / jbe) → cut at
landed.frac (+0x24) (180c78620(mv, f)); landed + W: its tick == T → cut at its fraction; landed + one tick: its tick == T
→ cut at its fraction (the landed one again). 180c78620 skips 0, 1 and a time already in the list.

**The view offset** (180ae953f): with the stair smoothing on and sv_legacy_jump 0 the ease's rate is max(fabs(svc+0x700)
(1808ad470), 60 (0x42700000)).

Schema (tools/re/game/schema.py): m_LegacyJump 0x6b8, m_ModernJump 0x6d0, m_nLastJumpTick 0x708, m_flLastJumpFrac 0x70c,
m_flLastJumpVelocityZ 0x710, m_bJumpApexPending 0x714, m_flTicksSinceLastSurfingDetected 0x718, m_flHeightAtJumpStart
0x6a0, m_flMaxJumpHeightThisJump / LastJump 0x6a4 / 0x6a8, m_flStaminaAtJumpStart 0x6ac, m_flVelMulAtJumpStart 0x6b0,
m_flAccumulatedJumpError 0x6b4, m_fStashGrenadeParameterWhen 0x68c (the jump stamp), m_bUseFrictionStashedSpeed 0x690,
m_flUseFrictionStashedSpeedUntilFrac 0x694, m_flFrictionStashedSpeed 0x698 (the speed latch).

Unread here: 180a6ffb0 (the controller's), pawn+0x15a4 / 0x15a8 (the same two the legacy port skips), 180adbeb0's flag.

## CheckFalling 180abb840(svc, mv) (PlayerMove_PostMove calls it)

Alive and on a ground entity and fall velocity (svc+0x25c) > 0: in water and fall >= DAT_181926a28 →
"Land_WaterVol.StepLeft". fall >= DAT_1817c3d60 (the fall-damage threshold): not in water: the ground's 1803dfd50 →
fall -= DAT_18179bea4; a ground moving down: fall += its vz, at least 0.1. fall > DAT_181926a38 → 180adc190(mv)
(damage) and punch 1.0; > DAT_181926a30 → 0.85 (DAT_1817b2bfc); > fatal-ish DAT_18179bea4 → 0.5; else 0; 180ade0a0
(svc, mv, punch). DAT_18178fe20 < fall <= DAT_1817b2c84: view punch fall x DAT_181784de8 (min 0.75). Landing
stamina: modern → 180ada630(svc+0x6d0, mv, fall); legacy → stamina = clamp(stamina + sv_staminalandcost (1821753c8)
x fall, 0, max). svc+0x714 = 0. 180adaaa0(pawn, fall). fall = 0.

## PlayerMove_PostMove 180adcb90(svc, mv, slide)

CategorizePosition(svc, mv, onGround); on ground: vz = a.z = half.z = 0. CheckFalling. slide && |v| (1802d4490
against 0.01) not small: TryPlayerMove(svc, mv, 0, 0, 0). mv+0x138 and on ground: svc+0x6a4 = max(svc+0x6a4,
((origin.z + 196608) - 196608) - svc+0x6a0). On ground: velocity modifier pawn+0x14e0 < 1 → clamp(+ frametime x 0.4,
0, 1). pawn+0xdf1 = 1 when moving. svc+0xdcc = 0.

## Cvars (registrations read: default, the data pointer is the handle + 8)

| handle / data | name | default |
|---|---|---|
| 182175438 / 440 | sv_staminarecoveryrate | 60 (182175430 / 438 below was a misread: 0x182175430 is dev_create_move_report's data) |
| 182175490 / 498 | sv_step_move_vel_min | 64 |
| 181ff5798 | sv_gravity | 800 |
| 1821754c8 | sv_jump_impulse | 301.993378 (0x4396ff27) |
| 182175448 | sv_staminamax | 80 |
| 1821753b8 / 1821753c8 | sv_staminajumpcost / landcost | 0.08 / 0.05 |
| 1821754d8 | sv_jump_spam_penalty_time | 0.015625 |
| 182175458 | sv_timebetweenducks | 0.4 |
| 182175518 / 520 | sv_standable_normal | 0.7 |
| 182175508 / 510 | sv_walkable_normal | 0.7 |
| 1821754e8 | sv_air_max_wishspeed | 30 |
| 1821d3588 | sv_stepsize | 18 |
| 1821d34d8 | sv_maxspeed | 320 |
| 182175568 / 570 | sv_water_slow_amount | 0.9 |
| 1821d3568 / 570 | sv_bounce | 0 |
| 1821d3558 / 560 | sv_friction | 5.2 |
| 1821d3458 / 460 | sv_stopspeed | 80 |
| 1821d34e8 / 4f0 | sv_accelerate | 5.5 |
| 1821d34f8 / 500 | sv_airaccelerate | 12 |
| 182175578 / 580 | sv_jump_precision_enable | 1 (the z snap in TryPlayerMove, the jump's 196608 rounding) |
| 182175468 / 470 | sv_accelerate_use_weapon_speed | 1 |
| 182175600 / 608 | sv_optimizedmovement | 1 (the prelude skips CategorizePosition for WALK: only vz > 250 clears the ground) |
| 182175620 / 628 | sv_autobunnyhopping | 0 |
| 1821755a8 / 5b0 | sv_legacy_jump | 0 (GFL runs 1; registered 1800c9ad0, 0x82000: a map can set it) |
| 182175400 / 408 | sv_bhop_time_window | 0.0078125 (registered 1800c9040, 0x82000; the modern jump only) |
| 182175588 / 590 | sv_quantize_movement_input | 1 (vfn 0x118 rounds the moves) |
| 0x181922ce0 / c40 / cb0 (names) | sv_ladder_scale_speed / dampen / angle | 0.78 / 0.2 / -0.707 (0x82000) |
| 1821754a8 / 4b0 | sv_use_playercache | 1 (the trace cache: same results, not modelled) |
| 182175478 / 480, 182175488 / 490 | sv_accelerate_debug_speed, sv_show_move_collisions | debug only |
| 18211a3a8 / 3b0 | mp_solid_teammates | 1 (int, registered 1800a1f30: "0 = transparent; 1 = fully solid; 2 = can stand on top of heads"; 18093e970 = value != 0 && != 2) |
| 18211a3b8 / 3c0 | mp_solid_enemies | 1 (int, registered 1800a1e80; 18093d680 = value != 0) |

Constants: 0x1817d0e90 = pi/180 (float 0.017453292); 0x18179be50 = 0.0078125 (the jump's 1/128); 0x1817bc124 = 140;
0x1818d21a8 = 1.0; 0x1818d21a0 = 260 (PlayerMove's max speed cap: mv+0x120 = min(260, sv_maxspeed or the pawn's
+0xb50 +0x1ac), then min(weapon vfn 0xc20)).

AngleVectors 181472530: each angle x pi/180 → V_sincosf (tier0: CRT sinf 1802e6430 / cosf 1802e0c30, the FMA3 build:
rubikon CrtMath.cs); forward = (cp cy, cp sy, -sp); right = (sr sp cy - cr sy... as decompiled), up likewise.
1814738b0 = the f64 normalize (sim rn::vec, 18008d4e0's shape).

## The subtick loop: CPlayer_MovementServices::DoMovement::Subtick 180c6f2a0 (player_movementservices.cpp:0x711)

For each subtick step (mv+0x68 array, 0x20 bytes: +0 when, +8 button, +0x10 pressed, +0x10 / +0x14 analog deltas;
count mv+0x60) whose `when` differs from the last: the view angles (mv+0x14) from the step when
sv_subtick_movement_view_angles (vfn 0x128); 180c610b0(mv) cuts the piece; frametime (globals+0x34) = (mv+0xe0 -
mv+0xdc) x (mv+0xd8 - mv+0xd4 ticks) x interval; curtime (globals+0x30) = tick x interval + when x interval (a when
>= 1 is the next tick, < 0 the one before); vfn 0x118 / 0xe0 (PlayerMove 180adf830) / 0x138; then the step's button
(180c80540) or analog deltas: IN_FORWARD 8 / IN_BACK 0x10 → forward ±1, IN_MOVELEFT 0x200 / IN_MOVERIGHT 0x400 →
side ±1 (sign by pressed). web/src/cs2web/sim/move-state.js runCmd models this already (pieces, keys).
PlayerMove 180adf830: svc+0x650 = 0, svc+0x648 = 0; mv+0x120 = the max speed (above); svc+0x43a = 0; the dispatch
180adc390.

## The command around the pieces (2026-11-10; sim/src/movement/cmd.rs, web/src/cs2web/sim/move-state.js extraCuts)

The per-command caller 180c7b050 (it calls 180c6f2a0, the subtick loop): CheckMovingGround (vfn 0x168), vfn 0x108
(returns the CMoveData), **180c60a80(mv, cmd, tick = globals+0x44, force)**: mv+0xd8 = tick, mv+0xdc = 0, mv+0xe0 = 1.0,
mv+0 bit 0 = (cmd+0x90 != 0) || force, bit 1 = (cmd+0x90 != 0), mv+0xd4 = tick - (bit 0 ^ 1) (a normal command spans
[tick - 1, tick]); then **SetupMove (vfn 0x110)**, the subtick loop (per step: vfn 0x118, PlayerMove vfn 0xe0, vfn
0x138), **FinishMove (vfn 0x130)**. CCSPlayer_MovementServices' vtable: 0x181923f70 (slot 0xe0 at 0x181924050).

**The base SetupMove 180c7e8d0** (player_movementservices.cpp:0x2b4): mv+4 the pawn's handle; the view angles (mv+8,
+0x14); mv+0xc8 the abs origin (1803d6f50); mv+0x38 the abs velocity (1803d7090: pawn+0x38c m_vecAbsVelocity, exact);
mv+0x2c / 0x30 / 0x34 forward / left / up move from svc+0x1a0 / 0x1a4 / 0x1a8 through 180c80890 (forward only with
IN_FORWARD | IN_BACK in svc+0x58, left only with IN_MOVELEFT | IN_MOVERIGHT, up always). svc+0x1a0..0x1a8 are the
usercmd's CBaseUserCmdPB (cmd+0x40) +0x58 forwardmove, +0x5c leftmove, +0x60 **upmove** (180c7ff64..ff8f; also copied
at 180c7b39a). client.dll has "moveup" / "movedown" buttons (client_20261105 0x181c65728 / 0x181c65730): nothing here
binds them, so the noclip up move is 0 (noclip.rs). Then **the step builder 180c7eba0** (the cmd's steps, the last at
1.0, the pruning of equal-angle steps) and at its end (180c7efe1) **vfn 0x120**.

**vfn 0x120 180ae2c50, the step builder's own cuts** (180c78620(mv, f): a step at f with no button and the *next*
step's +0x18 / +0x1c, i.e. its view angles (the subtick loop copies step+0x18 / +0x1c into mv+0x14 / +0x18), unless f
is 0, 1 or already a step's time; inserted in time order). In order: the active weapon's three times (180b54e20,
180b54e50, 180a02300) inside the command go to mv+0x78's own list (180c78450: not movement's); **the speed latch**:
svc+0x690 set → cut at svc+0x694; sv_legacy_jump 0 only: 180ae2a50 (the modern jump object svc+0x6d0's times: "The modern jump");
**the jump stamp**: 180c51bc0(svc+0x68c) = (int((s - fmodf(s, 1/64)) x 64 + 0.5), fmodf(s, 1/64) x 64), its tick
== globals+0x44 - 1 (mv+0xd4) → cut at its fraction; **the apex**: svc+0x714 (just jumped) and not FL_ONGROUND
(pawn+0x388 bit 0) and movetype WALK (1803d95f0 == 2) and vz (mv+0x40) > 0 and mv+0 bit 0 clear: a = ((sv_gravity x
pawn+0x40c) x 0.015625) x 0.5, d = m_vecBaseVelocity.z (pawn+0x3c8, 1803d7740) x 0.015625 - (a + a); d + vz <= 0 → t =
-vz / d, t not 0 or 1 → 180c70c90(svc, (mv+0xd4, t), mv, force 1): a time at or after mv+0xd8 goes to svc+0x1b0's
four-slot list instead; one after (mv+0xd4, mv+0xdc) is cut (180c78620). (180c7f0f0, the base class's vfn 0x120,
runs first: unread.)

**CCS SetupMove 180ae2320** (after the base, so the cuts above saw the velocity before this): not FL_ONGROUND → t =
180c629e0((mv+0xd4, 0) - (svc+0x708, 0x70c)) (1813b8fb0: the fractions' difference, a negative one borrowing a tick;
180c629e0 = tick x 0.015625 + frac x 0.015625), v = clamp(svc+0x710 - sv_gravity x pawn+0x40c x t, -16384, 16384)
(18017b8d0: lo when lo > v, hi when v > hi); mv+0x40 == quantize(v) (180ae0230) → mv+0x40 = v. (The cvar at
DAT_182175430 set and svc+0x58 & 0x61e → DAT_182175af8 = 0x80: a debug counter vfn 0x138 counts down.) mv+0x44 =
mv+0x14 (the angles). The pawn's interacts-with: m_lifeState (pawn+0x2d8, 1803d9090) 1 → 0x800003011; else mp_solid_enemies ?
0xc3011 : 0x800003011, and when mp_solid_teammates is 0 or 2, m_iTeamNum (pawn+0x344) 2 → | 0x80000000, 3 → |
0x100000000; 180d0e6a0(pawn+0x5e8, (pawn+0x608 & 0xfffffffe7ff3cfee) | that). **mv+0x13a = 0**, mv+0x139 = (cmd+8 ==
svc+0x680 + 1), mv+0xf4 = pawn+0xbc8, mv+0x124 = svc+0x1ac; then 180991b50 for a live non-noclip pawn.

server.dll's own layers (18093b180, explicit indices): 31 csgo_team1, 32 csgo_team2, 33 csgo_grenadeclip, 34
csgo_droneclip, 35 csgo_moveable, 36 csgo_opaque, 37 csgo_monster, 38 csgo_chicken, 39 csgo_thrown_grenade, 40
csgo_dropped_hostage (strings 0x1818cb4b8..). rubikon's CollisionRules registers these ten at the same bits after
vphysics2's 0..30, so a map's csgo_* names take the game's bits (atixref's csgo_grenadeclip 33) and the team bits 31 /
32 SetupMove adds touch no map layer; a name neither knows takes 41 on (TODO: how server.dll numbers those).

**vfn 0x118 180ae26b0** (before each piece): 180c7eb90, mv+0x100 = 0 (the wish), mv+0x108 / 0x110 reset.

**WalkMove's speed latch** (180aea7d0, after the wish, before 180ae10d0 / Friction; svc+0x690 bool, +0x694 float,
+0x698 float, +0x7a8 / 0x7ac the last piece's wish): latch clear → look; latch set and svc+0x694 == mv+0xdc (the
piece starts where it was set) → clear it, look, again = 1; else nothing. Look: q = 180ae0230(sqrt(vx² + vy²)) (x², y²
then addss); changed = svc+0x7a8 != mv+0x100 || svc+0x7ac != mv+0x104; (again && svc+0x698 != q) || changed → svc+0x690
= 1, svc+0x694 = mv+0xdc, svc+0x698 = q, mv+0x13a = 1. Friction then controls by svc+0x698 while svc+0x690 holds.

**vfn 0x138 180ac4c00** (after every piece): not FL_ONGROUND → svc+0x6a4 = maxss(svc+0x6a4, ((mv+0xd0 + 196608) -
196608) - svc+0x6a0) (the airborne jump rise); 180c80ad0 / 180c70950 (the duck button's state); DAT_182175af8
counts down; SetAbsOrigin (1803ea3b0) / SetAbsVelocity (1803ea4a0: pawn+0x38c, exact) from mv; 180ae9260(svc,
frametime); the jump stamp: svc+0x68c > 0 (18017e2d0 against 0.0 at 0x181781734) and (mv+0xd4, mv+0xe0) >= its
GameTime → 180ae4570(pawn) (pawn+0x1564 = 1, +0x1568 the eye angles + aim punch, +0x1574 the eye, +0x1580 the trace start (vfn 0x2c8), +0x158c the velocity: the
jump's pose for the weapons) and svc+0x68c = 0; **svc+0x7a8 = mv+0x100** (8 bytes).

**FinishMove vfn 0x130 180ac4b20**: 180c701a0 (the base: svc+0x1c0.. the moves, SetAbsOrigin / Velocity unless
movetype 5, vfn 0x140, 180c5e7c0); svc+0x25c = -mv+0x40; svc+0x1ac = mv+0x124; 180a9d5a0(svc+0x310); **svc+0x690 =
mv+0x13a**.

**The jump's record 180ada490** (CheckJumpButton): svc+0x708 / 0x70c = 1813b9ab0(mv+0xd4, (mv+0xdc + 131072) - 131072)
(the piece start on 1/64ths, normalized), svc+0x710 = mv+0x40, svc+0x714 = 1. **The jump stamp** (CheckJumpButton
180abc7fe..8aa): svc+0x68c = (curtime (180927cb0: globals+0x30) - frametime (globals+0x34): 1801f95a0 is a subss) + 0.1
(0x18178fdc8 = 0x3dcccccd, 18017dc70 addss), copied to pawn+0x1560, pawn+0x1564 = 0. The modern jump's 180ae66b0
(called from 180abbe60) writes it the same way. GameTime helpers: 1813b8ef0(out, tick, frac) (a fraction outside [0, 1)
carries whole ticks: V_modff), 1813b9ab0 the same, 180c51bc0 from seconds, 1809209f0(out, tick, flag) the tick as it
is when the flag (180c86d00: pawn+0x10 → +0x38) is set, else through the gamerules' 180de69a0.

Still unread here: 180c80890 (the move's int-to-float), 180c7eb90. (180ae9260, vfn 0x138's call: "The view offset"
below.)

## Before each piece: vfn 0x118 (180ae26b0), and the last stand-ins read (2026-11-11)

vfn 0x118(svc, mv), after 180c7eb90: mv+0x100..0x110 and +0x114..0x11c (the wish and the half step) zeroed, mv+0x128 /
0x130 = 0, **mv+0x138 = !(pawn+0x388 & 1)** (the piece starts airborne: PostMove 180adcb90 records the jump's rise
(svc+0x6a4) only with it set and on the ground after, i.e. on the landing piece), IN_JUMP's 180c80ad0(svc, 2) unless
svc+0x58 bit 1; **sv_quantize_movement_input** (182175588 / 590, default 1, flags 0x82000: "Quantize movement input
values. Enabling this restricts players from using analog input to move at fractional speeds normally impossible with
digital button input.") → mv+0x2c / 0x30 / 0x34 = V_roundf (tier0 0x1800081c0 → 0x1802a9ffc: the CRT's roundf, half
away from zero) of themselves; AngleVectors(mv+0x14).

- **CategorizePosition's second trace**: the first trace's surface record (trace +0) with +8 == 0x75de364e (the
  "default" surface's hash, surfaces.json) → a second trace (interacts-with 0x3001, the rest the movement's: "The step sounds" below) from
  the same start; a hit replaces svc+0x428 (the ground's surface pointer: the server's step sounds read it). Also: the
  jump sound 180adbeb0 takes two arguments and always plays Default.WalkJump. svc+0xfd4 (start-solid ground traces of a
  live pawn) > 31 → 18021a120: a statistic (pawn+0x15c0, a global count). svc+0x648 (the traces count) is read only
  by PlayerMove's telemetry add (180adfdd9: lock add to 182176528).
- **WaterMove's mv+0x124** (180aeb9b1 / 180aeb9fd) = svc+0x1ac m_flMaxspeed (SetupMove 180ae2644; FinishMove
  180ac4ba7 writes it back): only the constructors (180c6b810) and the reset 180ae2020 (260) write it.
- **Accelerate's 0.52 skip**: pawn+0xe38 is m_pHostageServices (schema), +0x48 m_hCarriedHostage (ported 2026-11-16: the
  sim's Input carrying_hostage, J[53] 0x80000; PlayerMove's carrier speed: docs/game/hostage.md).
- **TryPlayerMove's 180ac8970(pawn)**: over the player list (181e22ee8, 180c86b40 per slot, 180c84440: connected
  state 0 or 3 and neither vfn 0x810 nor 0x818), the first live pawn whose ground entity (vfn 0x668) is this pawn: a
  player standing on it ("Players' bodies" below; ported).
- **CheckWaterJump's m_iEFlags bit 5** on the wall's entity: nothing in server.dll sets it. Scans of the whole .text:
  no or / bts of 0x20 (or bit 5) on [r + 0x414], no store to [r + 0x414] of a register or'ed with 0x20 in the 4
  instructions before; 180ca6480 (the only or [r + 0x414], reg) works on a network-state block (its +0x1c0, +0xf8
  mutex; callers 180b55b70 pass 0xfffff, 180ca6840 a mask), not an entity. Source's check here was the player-held
  physics object, which CS2 players can't do: a dead check, never true in CS2 or the sim.
- Registration flags read (the value struct's +0x37 is the default): sv_ladder_scale_speed / dampen / angle,
  sv_legacy_jump (default 0), sv_jump_precision_enable (1), sv_quantize_movement_input (1): 0x82000;
  sv_accelerate_use_weapon_speed 0x82100; sv_optimizedmovement 0x2002 (FCVAR_DEVELOPMENTONLY: a map can't set it).

## The view offset (2026-11-11; sim/src/movement/view.rs)

vfn 0x138 (180ac4c00), after setting the pawn's abs origin (1803ea3b0, mv+0xc8) and abs velocity (1803ea4a0,
mv+0x38), calls **180ae9260(svc, gpGlobals->frametime (+0x34): the piece's)**. Hull table 180cb7b90: +0 view (0, 0,
64), +0xc / +0x18 hull min / max (z 0 / 72), +0x24 / +0x30 duck min / max (z 0 / 54). "Alive" is pawn vfn 0x550
(CCSPlayerPawn 0x1801541a0: m_lifeState (+0x2d8) == 0).

1. svc+0x418 (FinishDuck / FinishUnDuck's origin shift): dead → 0 (notify 180ad7f70); else Approach(0, it,
   ((((max.z 0x20 - min.z 0x14) - (dmax.z 0x38 - dmin.z 0x2c)) x 0.5) / 0.1 (0x3dcccccd)) x frametime).
   off = 0 + svc+0x418.
2. svc+0x3f0 = 180a73870(svc+0x290) (notify 180ad7930); set → off -= 180a7a830(svc+0x290) (its +0x34, FLT_MAX read
   as 0). Changed → svc+0x3f4 = (pawn+0x270 vfn 0x60 → 180cad5d0: the body component's +0x120 render offset, its z
   +0xf0) - off (notify 180ad9310).
3. svc+0x3f4: dead → 0; else Approach(0, it, rate x frametime), rate = !0x3f0: maxss-like 1801783b0(|vz x 0.5|
   (1808ad470; vz from 1803d6fb0 GetAbsVelocity: pawn+0x38c unless EFL_DIRTY_ABSVELOCITY (m_iEFlags bit 12,
   180ce7940)), sv_gravity (181ff5798) x 0.05 (0x3d4ccccd)); 0x3f0 and sv_legacy_jump (1821755b0) off: max(|svc+0x700|,
   60); else 150 (0x43160000). off += 0x3f4; off = clamp(off, -32, 32) (18017b8d0).
4. pawn+0x270 vfn 0x68 → 180cb8910 → 180cb8770(body+0x120, (0, 0, off), 0): each axis clamped to [-128, 128] into
   +0xe8 / 0xec / 0xf0 (notifies 1806e8780 / 88c0 / 8a00), vfn 0x70(0x80) on a change.
5. svc+0x41c: dead → 0 (notify 180ad81f0); else Approach((dz - hz) x m_flDuckAmount (svc+0x40c) - svc+0x418, it,
   ((hz - dz) / 0.2 (0x3e4ccccd)) x frametime), hz = max.z - min.z (72), dz = dmax.z - dmin.z (54).
6. view = the table's view; z = ((((body z + svc+0x41c) + svc+0x424) + view z) + 196608) - 196608;
   **SetViewOffset 180242350(pawn, view)**: per axis, a changed value is stored clamped (18017b8d0) to its encoder's
   range (GetQuantizedFloatEncoderByReg on pawn+0x828 / 0x830 / 0x838 +4) and notified with the field's offset
   (pawn+0x824's chain). Then 180b21ba0(pawn+0xb10).

**m_vecViewOffset** is CBaseModelEntity +0x818 (schema), a CNetworkViewOffsetVector whose floats are +0 / 4 / 8 and
whose CNetworkedQuantizedFloat members (m_vecX +0x10, m_vecY +0x18, m_vecZ +0x20) carry the encoders. Its constructor
**1806892e0** registers them (tier0 FindOrCreateQuantizedFloatEncoder(reg*, 1, name, bits, flags, lo, hi)): m_vecX and
m_vecY 10 bits, flags 4 (encode zero exactly), [-64, 64]; **m_vecZ 12 bits, flags 2 (round up), [0, 64]**. Round up
raises the low end one step (server.dll's own copy of the setup, 1803c1030: flags & 2 → lo += (hi - lo) / 2^bits), so
z is kept in [1/64, 64]. The readers: CheckWaterJump (180abe530: 180158e30(pawn, out, pawn+0x818, 1), the offset
rotated by the pawn's node quaternion and scaled by its scale: (0, 0, z) as it is), the eye 180ac6340 (grenades.md),
180ae4570. Other writers: 180ae2020 (the movement services' reset: pawn vfn 0xb70(out, 1)), 180c7d520 (observers:
0x18177bf80), 180ae54a0 (unreferenced: step 6 alone).

### The stair estimator 180a73870(est = svc+0x290) → bool

est: +0 the svc, +8 the height cache (a hash: key the cell's (uint)floorf(x), (uint)floorf(y), value its height at
+0xc of a 0x10 entry; +0x18 its count, +0x1c its slot count), +0x28..0x30 the last floored origin, +0x34 the result.
The constructor (in 180ab4xxx's svc constructor, 180ab4e33..56) sets +0x28..0x34 to FLT_MAX; 180ab5b80 frees it.

1. No svc or pawn → false. Pawn vfn 0x660 (0x18014ec60 → vfn 0x668 0x180e7c2a0: m_hGroundEntity, pawn+0x3ec) null or
   its vfn 0x570 false (CWorld 0x180cb1d50 true; CBaseEntity's and every brush / door / physbox / train's 0x1801542c0
   false) → false.
2. pos = the abs origin (1803d6f50) floored to 1/100 per axis (floorf(v x 100) / 100). Equal to +0x28..0x30 → true
   (the result kept).
3. The cache holding more than 0x200 → every slot freed, count 0.
4. s = sv_stepsize (180ac70d0: 1821d3588) when the pawn has movement services (pawn+0xb50), else 18. A function-local
   static (182174cc8, made once, by the process's first call): (-24, -24, -2 s, 24) and (24, s + 1).
   box = pos + those (per lane, the static first); the hull's footprint pos.xy +- 16.
5. Grid: x0 = int((((x - V_fmodf(x, 8)) - 16) - 4)) (+8 when x > 0), y0 the same. For i 0..5 (x0 + 8 i), j 0..5
   (y0 + 8 j): start = (fx + 0, fy + 0, (s + s) + z), end = (fx - 0, fy - 0, z - (s + s));
   **180a707a0(est, start, end, box, &h = FLT_MAX)**: the cached height when its key is there and (start.x, start.y,
   h) is inside the box; else TraceShape (180c2f3c0) of a box (-3.99, -3.99, 0)..(3.99, 3.99, 0) (0xc07f5c29 /
   0x407f5c29, a static built once) from floorf(start) to floorf(end), filter: a CTraceFilter (vtable 0x18178c240),
   interacts-with 0x2011, group 11, entity ids -1 (180bf9270(null)), owner ids -1, hierarchy 0 (180c048b0(null)),
   detail layers 0xffff, object set 0xf, flags (stack byte & 0xc9) | 0x49 (bit 7 unset by the code: never read by the
   query), no entity iteration (+0x40 = 0); DidHit (1802c35a0: fraction < 1 or start solid), not start solid (+0xbb),
   normal z (+0x98) > sv_standable_normal (182175520, strictly) → h = floorf(end z (+0x8c) x 10) / 10, kept in the cache
   (180a6af20). A miss leaves h FLT_MAX: the cell is skipped. The probe runs before the area test, so a cell outside
   the footprint is still cached.
   Area = **180a7ec80**(cell min (fx - 4, fy - 4), cell max (fx + 4, fy + 4), footprint min, footprint max): 0 unless
   fmin.x < cmax.x, fmin.y < cmax.y, cmin.x < fmax.x, cmin.y < fmax.y; else (minss(cmax.y, fmax.y) - maxss(cmin.y,
   fmin.y)) x (minss(cmax.x, fmax.x) - maxss(cmin.x, fmin.x)). Area > 0 → a record (0x1c: area, x, y, h, i x 5 + j,
   -1, 1.0) appended (and hashed by its index for the fill), min / max of x, y, h kept (`h <= min`, `max <= h`).
6. No record, or z - max h >= s (comiss / jae) → +0x34 = 0. Else, when max h - min h >= s: the nearest record by
   ((dy² + dx²) + dz²) (strictly nearer replaces; the first of equals) gets distance 0, weight maxss(0.01, area x
   1/64); then until a pass changes nothing: for each record in order with a distance >= 0, for each direction of
   DAT_1819216d0 (-1, -5, +1, +5; -1 only when idx % 5 != 0, +1 when (idx + 1) % 5 != 0, -5 when idx > 4, +5 when idx
   < 20), the record at idx + d with distance -1 and |h - its h| < s gets distance + 1 and weight min(this weight,
   maxss(0.01, min(areas) x 1/64)), "linked" set. Records still at -1 are removed (from the end, order kept).
7. Weights (records in order): w = (RemapValClamped(h, s + z, (s + s) + z, 1, 0) x RemapValClamped(h, z - s, z - (s +
   s), 1, 0))² (1801d3440: (v - a) / (b - a) clamped to [0, 1], x (d - c) + c), x the record's weight when linked, x
   area; sum w, sum w x h. sum w > 0 → +0x34 = clamp(z - sum wh / sum w, 0, 24); else 0. pos → +0x28..0x30. True.

Measured (sim-test hold_em, 63 bots, 60 s): 3.70 ms a tick with it, 3.39 with the estimator off: about 0.3 ms, the
probes' casts on new cells.

## Players' bodies: the filter, standing on a player, the stack (2026-11-11; sim/src/game/pawn_bodies.rs)

The movement filter meets the other pawns' bodies (their collision property: SOLID_BBOX, mins (-16, -16, 0), maxs
(16, 16, 72 / 54 ducked)). The filter's +0x20 is its first entity id to ignore (RnQueryShapeAttr_t at filter+8, so
+0x18 of the query): the moving pawn's handle; +0x38 is the query's collision group (11).

- **ShouldHitEntity 0x180ae3280(filter, entity)**: no entity, +0x20 == -1 or no entity system → false; the filter's
  own entity (+0x20 through the entity list: 181f47078, 0x70-byte slots, serial at +0x10) gone → false. Group 11
  only: the hit's collision property (vfn 0x228) +0x5e (m_CollisionGroup) == 16 → false; the pass entity's
  collision +0x20 (m_collisionAttribute.m_nInteractsWith, pawn+0x608) & 0x180000000 nonzero and equal to the hit's
  → 180ae7da0(hit, pass). Else true.
- **180ae7da0(hit, mover)**: mp_solid_teammates (18211a3b0, value +0x58) != 2 → false; else 180ae7c60(hit, mover,
  GetAbsOrigin(mover).z (1803d6f50 +8)).
- **180ae7c60(h, m, z)**: h == m → 0; m_nActualMoveType (1803d95f0) 9 (LADDER) on either → 0; either collision
  property null → 0; vfn 0x660(h) == m or vfn 0x660(m) == h (taken as GetGroundEntity: TODO, IsStandable uses 0x668)
  → 1; (z + OBBMins(m).z) > (h.z + OBBMaxs(h).z) → 1 (0x180ae7d22..d43: movaps xmm6, z; addss mins; xmm0 = h.z +
  maxs; comiss / ja); (h.z + OBBMins(h).z) > (z + OBBMaxs(m).z) → 1 (0x180ae7d50..d64); else 0. h.z is
  GetAbsOrigin(h).z. OBBMins 180d04ee0 = collision +0x40, OBBMaxs 180d04ed0 = +0x4c.
- **IsStandable 180ad2d00(svc, trace)**, whole: trace+8 null or start solid (+0xbb) → false; not vfn 0x558 (a player
  pawn) → normal z (+0x98) >= sv_standable_normal (182175518 via 180187770). A pawn: vfn 0x668(hit) non-null and ==
  svc's pawn (svc+0x38, 180c856b0 fills it) → false; 180ad2840(svc pawn, hit as a pawn: vfn 0x560 → 180b55040, else
  vfn 0x558) → true; mp_solid_teammates (18211a3b0) 0 → false; else 180ae7c60(hit, 180ac6af0(svc) (the pawn),
  trace end z (+0x8c)). No normal test for a player.
- **180ad2840(me, other)**: other null → false; 180fe1050(info, other) (+0 null?, +1 vfn 0x558, +2 vfn 0x570, +4 the
  handle, +8 180b55410(other): the controller's entity index - 1, +0xc 180ac5e00(other), +0x10 m_iTeamNum +0x344);
  180b55410(me) == info+8 (the same player) → false; the bool at 18211a6d8 set → true (taken as
  mp_teammates_are_enemies; combat/penetrate.rs reads it as the teammate rule too: TODO its name); me+0xc98 (the
  controller handle) live → 180a79ab0(controller) != info+0xc; else me+0x344 != info+0xc. TODO: 180ac5e00 read as the
  pawn's team.
- **180ac8970(pawn)** (three callers: CheckJumpButton 0x180abc7c5, the modern one 0x180ae6882, TryPlayerMove
  0x180ae7179): the first live, connected pawn whose ground is this one.
- **TryPlayerMove 0x180ae7147..0x180ae71cb**: a ground entity (vfn 0x668) and 180ac8970 → mv+0x38 (velocity), +0x108,
  +0x114 = 0 (the loop then ends at once). WalkMove's clear move (its first trace at fraction 1) never gets here, so
  the one under a head can still walk out; the jump is refused outright.
- **The legacy CheckJumpButton 0x180abc70c..0x180abc778**, before svc+0x439: r12 = the ground (vfn 0x668) is a pawn
  (vfn 0x558) and not vfn 0x570; r15 = that and its own ground is null. After the ground / 180ac8970 / blocked
  returns: r15 → mv+0x40 = 0, +0x110 = +0x11c = 0 (no vz: 0x180abca35); else !+0x438 && !+0x416 && !(m_fFlags & 2) &&
  !r12 → the impulse less the gravity half step, x the jump factor; else the impulse x the factor.
- **The modern CheckJumpButton 0x180ae6830..0x180ae68b4**: the ground a pawn whose ground is null, or 180ac8970 →
  180ada0a0 and the jump object's +0x18 = -1024 (the usable press), return. r13 (on a pawn) is used later: unread.
- **CheckParameters 0x180abd51b..0x180abd629** (after the angles): not 180b5d1b0(pawn) (pawn+0xb28 vfn 0xb8 != 0: an
  observer) and not LADDER: count = 0; g = vfn 0x668; while g is a pawn and count < 2: g = vfn 0x668(g), count++.
  count > 1 → mv+0x2c = mv+0x120 x 3.0 (181784e08), mv+0x30 = 0, then 180c70950(svc, b, 0) for 8, 0x10, 0x200,
  0x400, 2, 4. The scale by mv+0x120 follows for all three moves.
- **180c70950(svc, button, down)**: when the pawn is the one at 1821974e0 (a listen host's?) it updates
  svc+0x50's button state (18068b200) and svc+0x190; down → svc+0x78 |= b, +0x70 |= b; up → +0x78 |= b, +0x70 &= ~b;
  both: +0x198 &= ~b; then a debug cvar's print. TODO: what the next command makes of +0x70 / +0x78 / +0x198.

Not traced (stand-ins, pawn_bodies.rs): the pawn body's broadphase tree and walk order (a pawn and a map shape at the
same fraction: the map's first here), its shape (a box hull taken; its cooked planes / vertex order), body type
(keyframed), m_nInteractsAs (0x40000: traced 2026-11-20 as 180ae27b0's player layer with solid cleared, grenades.md "Players and the projectile's filter"; the bits before it unread), its collision group at spawn (8 taken), surface ("default"), shape flags;
CheckStuck now runs in the sim (stuck.rs) on the movement's own TestPlayerPosition, which meets the bodies the world holds.

## Movers, the ground's velocity, base velocity, CheckStuck

In docs/game/push.md (2026-11-10): CS2's pusher on players, SetGroundEntity's base velocity, CategorizePosition's
moving up relative to the ground, CheckMovingGround (svc vfn 0x168), CheckStuck (180abd670: once every 64 commands,
then 180abd6c0 over CreateStuckTable 180ac0e60's 53 nudges, 27 tries a call; all of it: "CheckStuck" below).

## The fields the stand-ins named, identified (2026-11-10)

- **pawn+0x404 m_flWaterLevel** (its setter 1803ebff0 networks "m_flWaterLevel"; 1803d9e40 reads it as int(v x 4 + 1)):
  CategorizePosition takes no step down at 1.0.
- **weapon+0xfa8 m_bInReload** (schema registration at 180a09571): CheckParameters' attack slowdown skips a reloading
  weapon. vfn 0xac0(weapon, 0) is +0xec0 (the clip: 1809be910), vfn 0xc58 the vdata's +0x7dc
  (m_flAttackMovespeedFactor: 1809be800).
- **pawn+0x608 m_Collision.m_collisionAttribute.m_nInteractsWith** (m_Collision +0x5e8, the attribute +0x10, interacts-
  with +0x10): the pawn's solid-mask vfn (slot 0xb88, 180b67a60) returns 0xc3011; SetupMove stores it every command
  (180ae2320 → 180d0e6a0(pawn+0x5e8, ...): "The command around the pieces" below).
- **entity+0x414 m_iEFlags** (datamap 0x181ddfc60): CheckWaterJump refuses a wall whose entity has bit 5 set (Source's
  "a physics object the player holds" test).
- **pawn+0x412 m_nWaterType** (datamap 0x181ddfc40): CheckWater's 1803ec0d0, bit 0 water (contents bit 15), | 2 slime
  (bit 16).

## CheckWater (180abe290) and func_water

A ray from origin + (0, 0, the standing / ducked hull's max z) to the origin: CTraceFilter (0x18178c240) interacts-with
0x18000, group 5, query flags 0x4d. Hit (fraction < 1 or start solid, 1802c35a0): m_flWaterLevel = clamp(1 - fraction,
0, 1), the type from the contents; miss: 0. Entering (svc+0x654 0 and a level now): svc+0x658 = curtime. Returns level >
1. Called at CategorizePosition's start (when the pawn has a controller, pawn+0xc98), the ladder tick after the duck,
the water jump's flight after its slide, FullTossMove. CFuncWater::Spawn (vfn 9, 180999c60): 180d0f2c0(collision, 3, 2,
interacts-with) (SetCollisionGroup 180d0e200 to 2, trigger), each shape's attributes wiped (vfn 0x60 with a zeroed
record), then 180d0e5f0: interacts-as 0x8004 (water | trigger), interacts-with 0x340001, exclude the entity's. In the
group table trigger (2) only touches player_movement (11): movement passes through, CheckWater (flags with 4) hits.

## The game surface table (scripts/surfaceproperties_game.txt)

Loaded by 180c010c0, each entry 0x20 bytes, parsed by 180be8f60: +0 maxspeedfactor, +4 jumpfactor, +8 / +0xc the bullet
penetration modifiers, +0x10 legacymaterialtag, +0x14 gamematerial, +0x16 soundstackmaterial, +0x18 climbable, +0x19
isstairs, +0x1a isslippery, +0x1b allowsmokethrough, +0x1c reflectbullets, +0x1d reduceweaponimpact, +0x1e
bulletspenetrate. A surface record's +0x10 is its index (180c00e80). SetGroundEntity's 180c7e7d0 keeps the landed
surface (svc+0x278, its hash +0x270), never cleared: CheckParameters' k starts as its maxspeedfactor, the jump's k is its
jumpfactor; IsLadder (180ada5e0) takes a climbable surface too. Baked: `node tools/surfaces-game.mjs` ->
web/src/lib/surfaces-game.js.

## Found by the movement oracle (2026-11-11; docs/game/move-oracle.md)

server.dll's own movement run natively on the sim's inputs (sim/src/bin/move_oracle). What it showed, each fixed in
the sim unless it says otherwise:

- **Friction**: decel = control x ((sv_friction x surface friction) x the pawn's friction) (180ac53ee..5431).
- **Networked setters store only when a value compares unequal** (ucomiss: NaN unequal), so an equal value keeps its
  old bits (-0.0 stays): SetBaseVelocity 1803ea860 (AddGravity's base z, SetGroundEntity's), SetAbsVelocity
  1803ea4a0, m_flFallVelocity (svc+0x25c: the prelude, WalkMove, CheckFalling, FinishMove), the view offset's svc+0x418
  / 0x3f4 / 0x41c, the body render offset (180cb8770: per axis, against the clamped value), SetViewOffset 180242350
  (against the new value, the clamped one stored), m_flWaterLevel (1803ebff0). vecs.rs set_if_differs, view.rs set_f.
- **FinishMove** (180ac4b3f): m_flFallVelocity = -vz.
- **CheckVelocity 180abdab0(svc, mv, caller name)**: a velocity or origin lane whose exponent is all ones (inf, NaN)
  is zeroed (warned, throttled per entity through svc+0x440's CUtlMap and Plat_FloatTime), then each velocity lane
  is held to +-sv_maxvelocity (handle 0x1821d3578, 3500, 0x82000; registered 180104100): v > max → max, else -max >
  v → -max. Called at AirMove's start (180ae34f8), in WalkMove after Friction (180aeac90), in PostMove after
  CategorizePosition (180adcbe3), at AddGravity's end (180ab7403), and in 180ac5720 / 180adc860. The sim had none:
  accel.rs check_velocity, sv_maxvelocity as job word 137.
- **The command after a teleport**: CCSPlayerPawn::Teleport (vfn 0x528, 180ae54a0) sets svc+0x680 = the controller's
  command number (180b54920); SetupMove's mv+0x139 = (cmd+8 == svc+0x680 + 1), which lasts the command's pieces; with
  it the prelude runs CategorizePosition instead of sv_optimizedmovement's vz > 250 check (180add1bf). The job's piece
  flag 8 (JS: world/movement.js teleport and game.js setOrigin stamp it, move-sim.js passes it on the next command).
- **The water level**: m_flWaterLevel's setter 1803ebff0 quantizes through its own CQuantizedFloatEncoder
  ("m_flWaterLevel": 1803c1030(enc 0x181fb2138, 8 bits, flags 8 = integers exact, 0, 1), made once under the flag
  0x181fb2156 bit 2), a 1/128 grid over [0, 1.9921875]; then pawn vfn 0x698 (180b67370 → the water services' vfn
  0xb8). The level is int(v x 4 + 1) unclamped: 4 above 0.75, 5 at 1. Its readers test >= 2 (Accelerate), > 2 (the
  switch, CheckJumpButton), < 3 (FinishDuck), != 0, and CheckWaterJump == 3 (180add42a): 4 and 5 don't water-jump.
- **CQuantizedFloatEncoder** (server.dll's copy of tier0's), the setup 1803c1030(enc, name, bits, flags, lo, hi):
  bits 1..31 and lo < hi (else a pass-through encoder: +0x1e = 3); flags: zero-exact dropped when lo or hi is 0 with
  the matching round flag, turned into round down (lo == 0) / round up (hi == 0), dropped unless 0 > lo and hi > 0;
  with integers exact (8) the round and zero flags go; +0x1d = flags | flags << 4 (the high nibble's 1 / 2 / 4: lo,
  hi, zero kept exact); round down: hi -= (hi - lo) / 2^bits; round up: lo += it; integers exact: n = floor(log2(int(hi)
  - int(lo))) (0 when the range is <= 1), bits raised until 2^bits >= 2^(n + 1) (shl takes the count mod 32: at 31 bits
  it goes round, with a warning), hi = (lo + 2^(n + 1)) - 2^(n + 1) / 2^bits; mul = 1803c6a80(bits, hi - lo), inv = 1 /
  (2^bits - 1); a special value already exact on the grid (1803c1f70) loses its bit. The quantize 1803c1de0: below lo
  → lo, above hi → hi, a special value as it is, else q = (u32)(i64)((v - lo) x mul + 0.5) (doubles), r = (float)(q x
  inv x (hi - lo) + lo), minss(r, hi). movement/quantize.rs Encoder (checked: 200,000 configurations).
- **The water move** 180aeb880: water friction surface friction x ((speed x frametime) x sv_friction), the
  acceleration (frametime x (wishspeed x sv_accelerate)) x surface friction; mv+0x124 is SetupMove's copy of
  svc+0x1ac m_flMaxspeed (260).
- **CheckWaterJump** 180abe530: the forward from svc+0x65c (the prelude's AngleVectors of mv+0x14: +0x65c forward,
  +0x668 right, +0x674 up); the wall's entity m_iEFlags bit 5 is tested before the jump speed is stored, three lanes
  (water services +0x58 / 0x5c / 0x60 = normal x -50); FL_WATERJUMP is m_fFlags 4 (1803c5940(pawn, 4)); the second
  probe starts at origin.z + m_vecViewOffset (180158e30 through the node) + 8.
- **The swim stroke's sound** (CheckJumpButton, 180abc6a8): only when not walking (pawn+0x1478) and not ducked
  (svc+0x408). The swim up: vz 100 for water (1803d9e70 == 0x8000), 80 for slime (0x10000), neither: unchanged.
- **The duck on a ladder**: the duck's in-air flag (180ac1fcc), FinishDuck (180ac4832) and FinishUnDuck (180ac4f58) all
  exclude MOVETYPE_LADDER (no ground and not 9); FinishDuck's call is "amount >= 1 or no ground entity" (r12, the ground
  itself: 180ac296d), so on a ladder the duck finishes at once.
- **The duck speed's recovery place** (svc+0x430, 180ac257b): the pawn's origin (1803d6f50, the node's +0xc8), which on
  a ladder is still the piece's start while mv has moved by the prelude's LadderMove; the sim read mv's.
- **TryPlayerMove's one-plane bounce** needs MOVETYPE_WALK (180ae7654) and no ground entity; a ladder takes the general
  clip.
- **CheckFalling** 180abb840 (fall >= 350, out of water): a ground that is a light physics object (1803dfd50: m_iEFlags
  bit 19 and its physics material's +0x30 below 1000) takes 200 off (dead: nothing sets bit 19 on an entity, "CheckFalling's floating ground" below); a ground moving
  down adds its vz (180ac6af0 → vfn 0x668 → 1803d6fb0), then max(0.1, fall) (1801783b0(&0.1, &fall)); the impact
  punch 180ade0a0(svc, mv, scale): 1.0 above 580 (the fall damage 180adc190 first), 0.85 above 290, 0 below 200, else
  0.5; in water always 0.5. The landing (180adaaa0(pawn, fall)) and the job's `landed` take the adjusted fall.
- **The trace count** (svc+0x648): `inc` sites 180abb4ce / 5e4 (CategorizePosition and its "default"-surface second
  trace, which the sim now counts), 180abea98 / eba6 / ebdb (CheckWaterJump), 180ad55b8 / 57c8 / 598c / 5c07
  (LadderMove; the sim counts its probe on a map without ladders), 180ae01af, 180ae48a4 / 48cd (StayOnGround),
  180ae4c2d / 4ccf / 4e20 / 4f35 / 5009 (StepMove), 180ae5671 / 5818 (TestPlayerPosition: two per call), 180ae5d19,
  180ae5eb8 / 5f9b / 603a / 6104 (the quadrants), 180ae746d (TryPlayerMove), 180aeb33c (WalkMove), 180aec121 / c171
  (WaterMove). CanUnduck 180abab50 and the duck's air check call TraceShape directly: not counted.
- **Noclip** (movetype 7): CheckParameters (180abd0fa: 7 / 8 skip the speed factors (surface, velocity modifier, the
  attack slowdown), the stamina and the modern jump's landing factor; 180abd472: CalcRoll skipped), the prelude
  (CategorizePosition: surface friction 1, CheckWater, then 7 / 8 leave the ground, 180abb29a), the duck, the noclip
  move, PostMove; LadderMove returns at once (180ad522c); CanUnduck is true with no trace (180abab96).
- **CheckParameters adds the view punch to the move angles**: angles = view + the camera services' vfn 0x108
  (CCSPlayer_CameraServices 180a7aab0: the punch +0x48 (QAngle), its time +0x54 tick / +0x58 fraction, decayed while
  view_punch_decay (handle 0x1821754f8, 18) x (now - (tick + frac) / 64) > 0 by tier0's expf of minus that
  (1802b9f70 scales it)). The punches: TryPlayerMove's and CheckFalling's 180ade0a0, CheckFalling's 180c7e550 (its
  view punch: "CheckFalling" above; the math: "The view punch" below). **Read to the end (2026-11-11): nothing in the
  movement reads mv+0x44, so the punch never moves a player**: the sim moving on the view angles is CS2.
- Named while setting the oracle up: bot_mimic (0x181f9e210: SetupMove (180ae24bd) zeroes a mimicking bot's moves when -bot_mimic == the player slot (180c86c00) + 1 (
  "the command number + 1" was a misreading), in_spewbuttondelta (0x182191538: 180c70950's button debug), sv_rollspeed
  (0x1821d3538, 200) and sv_rollangle (0x1821d3548, 0: CalcRoll 180ab9560), host_timescale (0x1821b9a20),
  dev_cs_force_disable_move (0x1821756c8, pawn vfn 0xcb8), dev_create_bhop_reports (0x1821753d8),
  dev_create_move_report (0x182175428), bot_crouch (0x1821755f0: the duck's forced duck), sv_enablebunnyhopping
  (0x182175610), sv_max_distance_transmit_footsteps (0x182175768), view_punch_decay (0x1821754f8), sv_maxvelocity
  (0x1821d3578). The pawn's vfn 0xcb8 "can move" 180aba720; vfn 0x228 1801575b0 m_pCollision (+0x3d8); vfn 0x670
  180e8b700 (the ground changed: vfn 0x678 / 0x680, both `ret` for the pawn); SetGroundEntity's 180e95a10 stores the
  ground handle as ((h >> 15) - (identity +0x30 & 1)) << 15 | index and calls 1803c5940 / 1803e8520 (FL_ONGROUND on /
  off, then the flags-changed callback 180536730); the scene node's vfn 0x60 (180cad5d0's check) is the node itself
  (CSkeletonInstance 1801883f0), its render offset +0x120 + 0xe8..0xf0.

## The last stand-ins, read to the end (2026-11-11, session "movement final")

### CheckStuck (sim/src/movement/stuck.rs; under the oracle)

- **180abd670(svc, mv)**, the prelude's call at 180add182 (not movetype 7 / 0 / 8, m_lifeState (1803d9090) not 2):
  180c8cbc0(svc, &i) is the pawn's entity index (1813aa290: the identity's place in the entity list's 0x70-byte
  chunks, 512 a chunk, 0x4000 + ... for the second list); (svc+0x188 m_nLastCommandNumberProcessed + i) & 63 != 0 →
  0. svc+0x188 is the usercmd's number, stored at 180c7ff17 before the movement (it also fills the pressed-button
  command numbers). Then jmp CheckStuck.
- **CheckStuck 180abd6c0(svc, mv)**: CreateStuckTable 180ac0e60 (once: the 54 x 12-byte table at 0x181e17630, its
  init flag 0x181e17f70: (0, 0, z) z = -0.125..0.125 step 0.125, (0, y, 0), (x, 0, 0), the 8 corners at +-0.125 (x
  outer, y, z inner), (0, 0, 0 / 1 / 6), (0, y, 0) y = -2..2 step 2, (x, 0, 0), then z in 0 / 1 / 6 over x, y = -2..2
  step 2; the 54th zero). 180c86c00(svc, &slot) (180b55410: the controller's index - 1); -1 → 0.
  TestPlayerPosition 180ae5650(svc, &h, mv, mv+0xc8, group 0xb, &trace) with svc+0x43a m_bInStuckTest = 1 around it
  (written only here and in PlayerMove 180adfb4b; no reader in 0x180a00000..0x180d00000). h == -1 → m_StuckLast
  (svc+0x64c) = 0, return 0. The entity list (0x181f47078) lookup of h: -2, an empty chunk or a serial that doesn't
  match ([entry + 0x10] != h) → the same "not stuck". developer (handle 0x182197ee0) → a "%s stuck on object %i/%s
  from %s" print. now = (float)Plat_FloatTime() (tier0 import slot 0x18176b250, cvtsd2ss). The slot's svc+0x448 + slot
  x 4 (not a schema field: each side's own) >= now - 0.05 (subss 0x181784df4; comiss / jb: a NaN goes on) → return 1.
  Else it = now; 180c4d5f0(mv, &trace, mv+0x38) (the move's touch list: AddToTouched, skipping the pawn itself; mv+0xb0
  += the trace's +0x90). Up to 27 (0x1b) tries: i = m_StuckLast, m_StuckLast = i + 1, d = table[i % 54] (signed:
  imul 0x4bda12f7 / sar 4), at = (o.x + d.x, o.y + d.y, d.z + o.z) with o the origin at the first test;
  TestPlayerPosition(at) == -1 → m_StuckLast = 0, mv+0xc8 = at, return 0. All 27 hit → return 1 (m_StuckLast kept).
- **TestPlayerPosition 180ae5650**: svc+0x648 counted on entry and at its trace (180ae5818); the hull by svc+0x408
  m_bDucked (180cb7b90 +0x24 ducked, +0xc standing, +0x48 when 180b5d1b0); the trace 180addc00 from at to at; a hit
  whose layers (+0x28) meet the pawn's interacts-with (pawn+0x608, | 0x20 when vfn 0xc20) gives its entity's handle
  ((h >> 15) - (identity+0x30 & 1)) << 15 | index, else -1.
- A stuck prelude returns 0 from 180adce30: FullWalkMove does nothing more (no duck, jump, move, PostMove); CheckParameters,
  the stamina's and the swim timer's countdowns and AngleVectors have run. The JS stand-in (move-sim.js checkStuck,
  before the whole piece, the 0.05 s as "the same command") is gone.

### The view punch: it never reaches the movement

- **CheckParameters** writes view + punch into mv+0x44 (180abd406..4e3: 18029f040 = punch + view per lane), then
  roll = CalcRoll (180ab9560; 0 for movetype 7 / 8) and yaw = 1801fe910 (AngleNormalize: outside [-180, 180] or NaN, a
  - floorf(a x (1/360) + 0.5) x 360, then maxss(-180), minss(180)). **Nothing in the movement reads mv+0x44**: every
  read of [r + 0x44..0x4c] in 0x180ab0000..0x180af0000 and 0x180c60000..0x180c90000 with the CMoveData register is
  CheckParameters' own; WalkMove, AirMove, WaterMove, LadderMove, noclip and CheckWaterJump take AngleVectors of mv+0x14
  (the prelude's 181472530 into svc+0x65c / 668 / 674); the base FinishMove's vfn 0x140 (180c70140) copies mv+0x14 into
  pawn+0xbc8 (v_angle; the old one to +0xbd4). So CS2 moves on the view angles without the punch, as the sim does: not a
  stand-in. (Source 1 does the same: m_vecAngles = view + punch, the moves read m_vecViewAngles.)
- **The getter** (CCSPlayer_CameraServices vfn 0x108, 180a7aab0; the same inline at 1802cc150 and 180ade146,
  180a9ef81): out = m_vecCsViewPunchAngle (+0x48, schema); t = gpGlobals curtime (+0x30, 180c71830) - (float(tick
  +0x54) + ratio +0x58) x 0.015625; x = t x view_punch_decay (handle 0x1821754f8, 18; 180187770 reads a float cvar);
  x > 0 → out x= V_expf(-x) (tier0, import slot 0x18176ae78; 1802b9f70 scales a vector).
- **The setter 180c7e550(camera, angle*, time*)**: sv_suppress_viewpunch (handle 0x182191440, flags 0x6002, default 0)
  on → nothing. Each lane AngleNormalize'd (1801fe910: z, y, x in that order), stored when any lane compares unequal
  (1801f9480, ucomiss; the change notes 180c7aac0); the time: given → its tick / ratio (each stored when it differs);
  null → tick = gpGlobals tick (+0x44) through 180c86d00 / 1809209f0 (the pawn identity's m_worldGroupId (+0x38): 0 →
  180de69a0 takes the paused ticks (global +0xc0) off), ratio 0.
- **The writers** (every caller of 180c7e550 and of the add, vfn 0xf8 180a9ef60 = decayed + delta (1809f5b10), time
  null): the respawn (180216260 from 180249530 "Player.Respawn": zero); the impact punch **180ade0a0(svc, mv, scale)**
  (TryPlayerMove's speed loss, CheckFalling's landing): scale > 0 → svc+0x258 m_flStepSoundTime = 400, the step
  sound svc vfn 0x1d0(svc, mv+0xc8, svc+0x428 the ground trace's surface, max(scale, 0.1), 1, 0), then the decayed
  punch with roll = -(CSMovementVelocityQuantizer_t (180ade296's encoder: 20 bits, flags 4, [-16384, 16384]) of
  m_flFallVelocity svc+0x25c) x 0.013 (0x1819269d8), pitch 8 when above 8, set at now; scale > 0.85 (0x1817b2bfc)
  → pawn vfn 0xbb0(0x12, 0, 0) (an animation event). CheckFalling's view punch (180abbae2: any fall in
  (250, 1024], water or not, after the impact): pitch = max(fall x 0.001, 0.75) over the decayed punch, set at now.
  The gun's kick (180a4c5d0, Recoil): the decayed punch, yaw -= sinf(a) x (magnitude x 0.055), pitch -= cosf(a) x
  (magnitude x 0.055) (V_sinf / V_cosf imports 0x18176af00 / 0x18176b118), set at the attack time (its argument,
  through 180a9bda0 → 180c7e550). The map's: env_viewpunch (CEnvViewPunch_API::ViewPunch, 180d2a290 → 180feca00: a
  radius falloff 1 - d / r), trigger_impact (CTriggerImpact vfn 0x888, 180fdbcc0: pitch / roll from the push
  direction x m_flMagnitude x 0.1), env_physexplosion (CPhysExplosion vfn 0x68 → 180ec6140 → 180ec0960). None of the
  baked maps has env_viewpunch or trigger_impact; atix panic has one env_physexplosion (no class in the engine yet).
- The client camera's punch (lib/view-punch.js) is this state, in the sim (sim/src/movement/view_punch.rs, the job's
  words 183-188; ze_view_punch for the camera's read and the gun's kick): set by your first-time predicted moves at
  the piece's gpGlobals curtime / tick, read at the prediction's game time. Checked under the move oracle with
  server.dll's own setter 180c7e550 and impact 180ade0a0 running (2026-11-11).

### CheckFalling's floating ground (1803dfd50): dead in CS2

1803dfd50 is Source's IsFloating: m_iEFlags (+0x414) bit 19, Source's EFL_TOUCHING_FLUID (the numbering checks:
SetAbsVelocity clears bit 12, EFL_DIRTY_ABSVELOCITY), then the body's physics material +0x30 (density) below 1000
(0x181784e1c). **No code in server.dll sets bit 19 on an entity**: no `or` / `bts` of 0x80000 / 19 into a register
stored to [r + 0x414] (within 8 instructions), no `or [r + 0x414], imm` with it, no atomic or byte write to
+0x414..0x416 with it, no register-or AddEFlags helper; the only generic `or [rdi + 0x414], esi` (180ca6480, masks of
0xfffff) is a network-state block's field at the same offset, not an entity's. So the 200 off a landing on a floating
object never happens, as CheckWaterJump's bit 5 never does.

### The game surface table's inheritance (tools/surfaces-game.mjs)

180c010c0 → 18158b9f0 → **18158ba90(loader, kv, physprops)**: n = physprops vfn 0x10 (the surface count); the table
sized to n (loader vfn 0 → 180c07590: each entry +0 1.0, +4 1.0, +8 1.0, +0xc 0.5, +0x10 0, +0x14 0xffff0043, +0x18..
0 → maxspeedfactor 1, jumpfactor 1, climbable false); map[n] = -1; each "SurfacePropertiesList" block's
surfacePropertyName hashed (18054ba10, murmur2 seed 0x31415926) and found (physprops vfn 8) → map[surface +0x10] =
the block. Then for k in 0..n: s = physprops vfn 0x18(k); s+0x14 (the base's index) >= 0 → loader vfn 8 (180beeb90:
entry[k] = entry[base], 0x20 bytes) as entry[base] stands then; map[k] >= 0 → vfn 0x10 (180be8f60) parses the block over
entry[k]. vphysics2_20261103 (180073760) loads physprops from the one resource "surfaceproperties/surfaceproperties.vsurf"
(csgo's 164 surfaces; game/core's own 81-surface copy, with "woodladder", is behind it on the search path). On CS2's
data the in-order copy and a transitive resolve give the same table (concrete's base no_decal comes after it: both
are the defaults); four surfaces leave the defaults: slipperyslime / slipperyslide jump 0.7, ladder / wood_ladder
climbable.

### PreventBunnyJumping's cap (fixed 2026-11-11)

180ad63f0: sv_enablebunnyhopping off → cap = svc+0x1ac m_flMaxspeed (260) x 1.1 (0x18179be60); 0 < cap and |v|
(180225130, 3D) > cap → v x= cap / |v| (x, y, z). The sim had capped at PlayerMove's max speed (mv+0x120, the weapon's):
a jump at 275..286 u/s with a 250 u/s weapon differed (the oracle on a fresh hold_em round).

### The movement unlocker: CS2Fixes' "ServerMovementUnlock" patch (2026-11-12; sim/src/movement/walk.rs)

Not CS2's: a byte patch CS2Fixes applies to server.dll when `cs2f_movement_unlocker_enable` is 1 (src/patches.cpp
g_CommonPatches[0], "clients will not predict"; cfg/cs2fixes.cfg ships 0). gamedata/cs2fixes.jsonc: signature
`0F 86 AF ? ? ? 0F 57 C0 0F 2E C2` (windows), patch `E9 B0 00 00 00 90`. In server_20261105.dll the signature has one
match, **180aead45**, inside WalkMove (180aea7d0) right after Accelerate (the call at 180aeacdf):

```
180aeacfa  xmm7 / xmm10 / xmm11 = mv+0x38 / 0x3c / 0x40 (velocity);  xmm6 = mv+0x120 (the max speed)
180aead42  comiss |v|² (x² + y², + z²), max²
180aead45  jbe 180aeadfa            ; 0f 86 af 00 00 00  ->  e9 b0 00 00 00 90  (jmp 180aeadfa; nop)
180aead4b  ... v x= max / sqrt(|v|²); with frametime > 0 the change / frametime into mv+0x108..0x110
180aeadfa  the half step (v -= frametime x a x 0.5)
```

So the patch always skips WalkMove's clamp of the ground velocity to the max speed (step 6 above; the max speed
is the weapon's x the velocity modifier x the stamina's (1 - s / 100)², CheckParameters). Nothing else changes:
Friction, Accelerate (which only adds up to the wish speed), PreventBunnyJumping's 286 at each jump and the stamina
are CS2's. What it does to a bhop: a landing at 309 u/s builds ~15 stamina, so a tick on the ground is cut to
250 x 0.85² ≈ 183 in CS2; unlocked, friction alone takes it to 287 (src/cs2web/sim/bhop-test.mjs).

The sim: `Cvars::movement_unlocker` (the job's word 83 bit 0x400). The move oracle patches the same six bytes into
its mapped server.dll per piece (piece.rs set_cvars; `ZE_ORACLE_UNLOCK=1 / 0` for the fuzz): a recorded hold_em round
13,826 pieces and the fuzz 71,829 pieces, on and off: 0 differ.

### The step sounds at water levels 4 / 5, and the server's own step code (ported 2026-11-11: server_steps.rs)

The server's PlayStepSound decision 180c80100 (UpdateStepSound's body, from svc vfn 0x1a8 180ae9a50 → 180c80000): the
level (1803d9e40, int(v x 4 + 1)) 3 → the wade step at 0.65 (type 2); 1 or 2 → wade at 0.2 walking / 0.5 (type 3);
anything else (0, 4, 5) → the floor's step on the surface it was given (r15 = svc+0x428, CategorizePosition's ground
trace) at 0.2 / 0.5 (type 0): so levels 4 / 5 step like dry ground. client.dll does the same (180a793f5: 3, then
`dec al; cmp al, 1; jbe` for 1 / 2, else the floor), so world/footsteps.js clamping the level to 3 (levels 4 / 5 playing
the deep wade) was wrong: fixed. What the server adds that client.dll's (steps.rs's source) doesn't: every level >= 1
also plays "CT_Water.StepLeft" (0x1819537f0, EmitSound 180f69780 with an EmitSound_t: +0 the name, +8 the origin, +0x14
the volume; the string isn't in client_20261105.dll) at the step's volume before ducking; the CS override 180ae9a50.

**The whole path** (sim/src/movement/server_steps.rs; under the move oracle):

- **180ae9a50(svc, surface, origin, velocity)**, the prelude's call at 180add311 (after CategorizePosition and the
  fall velocity, before LadderMove's exit; svc+0x428, mv+0xc8, mv+0x38): pawn vfn 0xc20 (m_fFlags bit 4) with the
  identity's +0x30 bit 7 → nothing; pawn vfn 0x550 (m_lifeState == 0) false → nothing; movetype (180c86b20) 2: s² =
  (x² + y²) + z² against (0.52 x 260)² (0x1818d21b4 x 0x1818d21a0, squared): below it, or m_bIsWalking (pawn+0x1478)
  → 10 > s² → vfn 0x1c0(svc, 0, 0, velocity); either way nothing more. Else (and any other movetype) the base.
- **180c80000** (base UpdateStepSound): svc+0x258 m_flStepSoundTime > 0 → t - gpGlobals frametime x 1000 (0x181784e1c)
  stored, 0 when below 0; > 0 → return. m_fFlags & 0x60, movetype 7 / 8, sv_footsteps (handle 0x1821d3528, flags
  0x2102: FCVAR_DEVELOPMENTONLY, "Play footstep sound for players", default 1) 0 → return. Else 180c80100.
- **180c80100(svc, surface, origin, velocity)**: speed = sqrt((z² + y²) + x²), horizontal sqrt(x² + y²); vfn 0x1b8
  (180c718e0: 135 walk, 220 run); m_fFlags bit 12 → return; pawn vfn 0xb90 (m_bIsWalking) or speed < 135 → return;
  not a ladder (9) → FL_ONGROUND and horizontal > 0.0001 (0x181784de4) needed; walking = 220 > speed. Ladder: vfn
  0x1a0 (180ac65a0: physprops by svc+0x404 m_nLadderSurfacePropIndex, else 180c71630: by hash 0xe2a5b837 "ladder"),
  0.5, vfn 0x1c0(1). Level 3: physprops by 0x5f0a183a "wade", 0.65, type 2. 1 / 2: wade, 0.2 / 0.5, type 3. Else: the
  given surface (null → return before the timer), type 0, 0.2 / 0.5. Level >= 1: the splash. FL_DUCKING (+0x388 & 2):
  volume x 0.65 (0x18179be5c). vfn 0x1b0 PlayStepSound(svc, origin copy, surface, volume, 0).
- **SetStepSoundTime** (vfn 0x1c0, CCSPlayer's 180ae2230(svc, type, walking, velocity)): 0 / 3 → 400 walking, else 300;
  1 → floorf(35 - min(max((|vz| - 150) / 100, 0), 1) x 10) x 10; 2 → 600; FL_DUCKING → + 100.
- **PlayStepSound 180c7ba40(svc, origin*, surface*, volume, force)**: gpGlobals +0x10 (the player slots) > 1 and
  sv_footsteps 0, or no surface → nothing; the foot svc+0x280 toggles; the name from the pawn's footstep set (vfn
  0x900, vfn 0 by the record's +0x10 index: a 5-dword lookup, the third used; CS2's left and right names are the same),
  the sound system's 0x1823ab500; the EmitSound_t (+0 name, +8 origin, +0x14 volume, pitch 100) to every player but its
  own (180590da0 with the sound system 0x181ff56c8, 1813aa290 the entity index, 180f69780).
- **svc vfn 0x1d0 (180adc080)**: PlayStepSound, then with sv_footsteps and a surface svc+0x688++, the "player_footstep"
  event (0x18178d9f8), svc+0x684 = 1. The impact 180ade0a0 (svc+0x258 = 400, then this at max(scale, 0.1), forced) and
  both jumps (legacy 180abc921: sqrt((z² + y²) + x²) > 140; modern 180ae6c2a: (x² + y²) + z² > 19600; volume 1.0, the
  origin before the jump) call it on svc+0x428.
- **svc+0x428**: CategorizePosition's ground trace's surface record (180abb534), the trace reset's static on a miss (no
  sound can come of it); untouched when the trace doesn't run (moving up). The "default" surface's second trace
  (180abb5c7) carries, read back from server.dll by the oracle, the movement's query but for interacts-with 0x3001:
  interacts-as 0x40000, exclude 0x40000, the pawn ignored, query flags 0x4b, iterating entities (180ab55b0's
  arguments are only the start of it; an interacts-as of 0 hit shapes it misses: the oracle found it on atix).

m_fFlags 0x20 / 0x40 silence it (see "The freezes" below); bits 12 and 4 nothing here sets.

### The freezes: FL_FROZEN and FL_ATCONTROLS (2026-11-11)

m_fFlags (pawn+0x388) bit 5 FL_FROZEN (0x20) and bit 6 FL_ATCONTROLS (0x40) (CS2Fixes sdk public/const.h). Who sets
them on a ZE server: CS2Fixes' game_ui (entities.cpp 425-475: with SF_GAMEUI_FREEZE_PLAYER 32, Activate adds
FL_ATCONTROLS, Deactivate removes it) and point_viewcontrol (UpdatePlayerState 507-549: FL_FROZEN set when its
SF_POINT_VIEWCONTROL_FROZEN, 1 << 5 = 32, is set or during m_bFreezePeriod, cleared by every other enable and the
disable). The port had read the viewcontrol's freeze as spawnflag 4 and froze every viewcontrol player.

What the movement does with them (server.dll 2026-11-05):
- **The base SetupMove 180c7e8d0**: FL_ATCONTROLS (180c7ea5a) → the usercmd's forward / left / up (svc+0x1a0..0x1a8)
  aren't copied (mv+0x2c..0x34 stay 0); the buttons and the step builder's steps stay, so a key changing inside the
  tick still adds its +-1 for the rest of it (the subtick loop 180c6f2a0, the step builder 180c7eba0 and the step
  apply 180c80540 read no flag). FL_FROZEN (180c7ead8), or 18093d780 / vfn 0x160, developer, gpGlobals +0x70, or
  curtime < 3 → 180c70700(svc, 0) and svc+0x48 = 0 (the buttons gone), the moves 0, the step builder told so (r9 1):
  no input at all. The per-command caller 180c7b050 does the same at 180c7b42d (with the queued releases 180c70950
  over svc+0x238's bits).
- **CheckParameters** (180abd3a8): FL_FROZEN (or not alive) zeroes the moves unless the observer services' mode is 4.
- **The step sounds** (180c8007c): m_fFlags & 0x60 → none.

In the port: the mover's flFrozen / flAtControls (src/cs2web/sim/move-state.js runCmd: no input / no tick-start moves; in the
saved move state, so your client predicts them as CS2 does with the networked m_fFlags); the job's word 53 0x10 / 0x20
(sim: CheckParameters, the steps). CS2Fixes' point_viewcontrol also sets FL_FROZEN on its listed players during the
freeze period (UpdatePlayerState, every frame: server/cs2web/cs2fixes/entities/viewcontrol.js).

### The freeze period: m_bFreezePeriod (2026-11-11, session "viewcontrol-freeze")

CCSGameRules (the global 0x1821ba1c0; schema: m_bFreezePeriod +0xd8, m_bWarmupPeriod +0xd9, m_iFreezeTime +0xfc,
m_iRoundTime +0x100, m_fRoundStartTime +0x108, m_bGamePaused +0xc8, m_bIsValveDS +0x13c). Vtable 0x1818c5450.
- **1809562c0** (the round's times): m_iRoundTime = mp_roundtime x 60 (cvttss2si), m_iFreezeTime = 2 in warmup, else
  mp_freezetime (int, handle 0x182119ec8, registered 18009ef00: default 6, flags 0x282100, "how many seconds to keep
  players frozen when the round starts"). CS2's gamemode_casual.cfg sets 5 (GFL's mode), competitive 15.
- **The Think 1809669f0**: at 180967853 18092cdf0, then m_bFreezePeriod ? 180913f80 (the freeze's expiry) : 180916fb0
  (the round time's). 180913f80 compares m_fRoundStartTime with the game time (180de86d0, compare 18017e2d0), runs a
  per-player pass (180a9ca80 for team 2 / 3 pawns: unread), adjusts m_fRoundStartTime for timeouts (+0xe4 m_bTerrorist
  TimeOutActive ..., m_iFreezeTime: unread in detail), clears m_bFreezePeriod (18091479e) and fires
  "round_freeze_end" (1809147ac), which CS2Fixes' ZR starts its infection countdown on (ZR_OnRoundFreezeEnd). Stores of
  1 to +0xd8: 18092d991 (18092cdf0), 18094e249, 18094e5a9, 18094eada, 18094f690, 1809588ef (unread which is
  RestartRound).
- **The pawn's "can move" vfn 0xcb8 (180aba720)**: false when dev_cs_force_disable_move (0x1821756c8 +0x58), movetype
  NONE (1803d95f0), pawn +0xd40 not 0 / 6, +0x14be / +0x14bf / +0x14c0 set, the active weapon a C4 with +0x12c9 set,
  or **m_bFreezePeriod** unless the exception cl (18093df00(gamerules): engine vfn 0x98 / 0xa0 == 5 and a cvar match;
  then 18093dd30(gamerules +0x1148, pawn): needs m_bIsValveDS, team 2 (pawn +0x344), a freeze-time window:
  matchmaking only, false on a community server).
- **PlayerMove 180adf830**: the same test (180adfa5b) without the cvar and the C4; failing it, mv+0x120 (the max speed)
  = 1.0 (0x1818d21a8, 180adfb35) instead of min(260, ...).
- **The movetype switch 180adc390**: "can move" false → 180adc79d (VPROF "Can't move") → CheckParameters → 180adc860:
  forward / left / up 0; the prelude 180adce30 (false: stop); FL_ONGROUND → velocity, mv+0x108, mv+0x114 = the zero
  vector (0x18177bf80), the duck 180ac1ec0; airborne → vz -= ((sv_gravity (0x181ff5798, 1802a8a50) x pawn+0x40c) x
  frametime) x 0.5 (0x18178057c), vz = m_vecBaseVelocity.z (1803d7740) x frametime + vz, SetBaseVelocity (1803ea860)
  with z 0, CheckVelocity 180abdab0, the duck, then (pawn+0xb30 null or its +0x54 water-jump timer 0) the second half
  of gravity; PostMove 180adcb90(slide 1). No jump, no walk / air move. sim/src/movement/cant_move.rs; checked under the
  move oracle (fuzz job word 53 0x40: the oracle's "can move" stub follows it, mv+0x120 1.0; ~7k freeze pieces a map,
  half airborne, 0 differ).
- Found by it: TryPlayerMove's one-plane clip (180ae7654) needs movetype WALK (2), so noclip takes the multi-plane clip
  and its "dot(v, v_orig) <= 0 → stop"; slide.rs had only excluded the ladder (noclip only reaches the slide here).
- Other readers of +0xd8, by what they do: CanPrimaryAttack's (the gun 180a0fb0e, its secondary 180a1022d: unread),
  CKnife's swing 180a2fa80 (180a2fac1: no swing), the grenades' vfn 0xcf8 (1809d0650: false, else vfn 0xda8(1):
  unread), a sound volume in 180adb580 (180adbe08, `cmp [rdi], 0x1a`: unread), 1809131d0 (= !m_bFreezePeriod), and
  gamerules / HUD state (1802371c0, 180238d30, 18024b730, 1802809a0 / 9e0, 18028e620, 18030d950, 180310fa0, 180332110,
  18092c6a0, 18092e130, 18094df20 / e290 / ea70, 180951540, 180a6ecb0, 180b00630 / 730 / b00, 180deef20): unread.
- The pause (m_bGamePaused +0xc8) is what the base SetupMove's 18093d780 → 180deb490 → gamerules vfn 0x340 (180de8750)
  reads (the "FL_FROZEN, or 18093d780 / vfn 0x160" test above): not the freeze period.
