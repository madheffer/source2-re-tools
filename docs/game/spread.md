# A shot's inaccuracy and spread (traced 2026-11-11; sim/src/combat/accuracy.rs, spread.rs, spread_abi.rs)

server_20261105.dll; tier0_20261103.dll for the CRT. The JS ports these replace (web/src/cs2web/sim/accuracy.js, spread.js
before 2026-11-11) had the formulas right; what they couldn't have was tier0's float functions and FireBullet's own
direction. The move to the sim keeps every random draw and every formula, and fixes those.

## 1. The weapon's state and its updates

Fields (schema.py): m_fAccuracyPenalty +0xf88, m_flRecoilIndex +0xf98, the last fire's curtime +0x1038, the last
update's curtime +0xf8c, the turning term +0xf74 / its clamped copy +0xf84. vdata: m_flInaccuracyJumpInitial +0x7b8,
JumpApex +0x7bc, Reload +0x7c0, m_flRecoveryTimeCrouch +0x840, Stand +0x844, CrouchFinal +0x848, StandFinal +0x84c,
m_nRecoveryTransitionStartBullet +0x850, EndBullet +0x854.

- **UpdateAccuracyPenalty 0x180a26bd0** (CCSWeaponBaseGun vfn 0xd70; called from CCSPlayer_WeaponServices vfn 0x68
  0x180b1d3d0, a per-frame service call, and from the R8's SecondaryAttack): the target is MOVETYPE_LADDER (or a stack
  of `weapon_accuracy_stack_boost_limit` players under the ground entity): `Ladder[m] + Ladder[0] + 0`; on a ground
  entity: `Crouch()` with FL_DUCKING (pawn +0x388 bit 2) else `Stand[m]`, `+ 0`; in the air
  `Jump[m] x weapon_air_spread_scale + Stand[m] + 0`; `+ Reload` while m_bInReload. Target <= penalty (`a < b || a ==
  b`): with GetRecoveryTime != 0, `penalty = V_expf(-(V_logf(10) / recovery) x frametime) x (penalty - target) +
  target`, else the target; target above: the target. Then 0x180a274b0 (the turning term, behind
  sv_turning_inaccuracy_enabled), 0x1809fbae0 (a 32-entry movement history, behind the strafing cvar); then, with the
  recoil index > 0 and curtime > (last fire + GetCycleTime(0)) + 1/64: `index = V_expf(-(ln10 + ln10) x frametime) x
  (index - 0) + 0`, 0 at or below 0.1. +0xf8c = curtime. frametime is gpGlobals +0x34 (1/64 a frame; the command loop
  zeroes it, so this isn't per command).
- **GetRecoveryTime 0x180a02600**: a ladder RecoveryTimeStand; off FL_ONGROUND RecoveryTimeCrouch x 4; else crouched /
  standing `RemapValClamped((float)(int)index, Start, End, RecoveryTime, RecoveryTimeFinal)`, the base alone when the
  Final is -1.
- **GetInaccuracy 0x180a01400**: weapon_accuracy_forcespread > 0 -> min(it, 1); weapon_accuracy_nospread -> 0. Else
  `move = RemapValClamped(Length2D(velocity) (0x1801cd370: sqrtss(x x + y y)), max x 0.34, max x 0.95, 0, 1)`, max =
  vfn 0xc20 (GetMaxSpeed); `move > 0`: not m_bIsWalking (pawn +0x1478) -> `V_powf(move, 0.25)`, `x Move[m]`; `total =
  penalty + move`; no ground entity: `ji = scale x JumpInitial`, `ja = scale x JumpApex`, `sMax = sqrt(sv_jump_impulse)`,
  `sV = sqrt(fabs(vz))` (0x180a28730), `lo = sMax x 0.25`, `air = ((sV - lo) x (ji - ja)) / (sMax - lo) + ja` (lo ==
  sMax: ji when sV >= sMax, else ja), clamped to [0, ji + ji], added; the stack boost adds 0.0; then
  `(0x180a029b0 (the strafing term) + total) + (+0xf84)`, at most 1.
- **RemapValClamped 0x1801d3440**: a == b -> (v - b >= 0) ? d : c; else `t = (v - a) / (b - a)`, maxss 0, minss 1,
  `t x (d - c) + c`.
- After a shot (BaseGunFire 1809f8a70): `penalty = Fire[mode] + penalty`, `index + 1`; +0x1038 = curtime (the primary
  branch). The landing 0x180a1d870 and the deploy 0x1809fb560: as the JS had them (not re-read).
- **The cvars' defaults** (their registrations): sv_turning_inaccuracy_enabled (0x1800c1de0, object 0x18212b128) and
  sv_strafing_inaccuracy_enabled (0x1800c1b50, 0x18212b158) default false (the bool default byte +0x37 is 0), so
  +0xf84 stays 0 and 0x180a029b0 adds nothing; weapon_air_spread_scale 1.0 (0x1800c2140).

## 2. FX_FireBullets' layout (0x1802a59c0, from 0x1802a4f50)

RandomSeed / RandomFloat are tier0's global stream (IAT 0x18176aee0 / 0x18176b218); the trig is tier0's V_cosf /
V_sinf (0x18176b118 / 0x18176af00), which jump to the CRT's cosf / sinf (tier0_20261103 0x1802e0d70 / 0x1802e6570,
the same code as the 20260923 build's 0x1802e0c30 / 0x1802e6430 that math/crt.rs is checked against: every constant
the same). Per bullet: the first, or every one with weapon_accuracy_shotgun_spread_patterns: `r0 = RandomFloat(0, 1)`,
`θ0 = RandomFloat(0, 2π = 0x40c90fdb)`; the R8 in mode 1 takes `1 - r²`, the Negev under recoil index 3 squares
(3 - index) times and takes `1 - r`; two debug flags (r14b: r = 1; r15b: θ = π/2) belong to the force / no-spread
cvars; `r0 x= inaccuracy`. The spread's (θ1, r1): with the patterns, 0x1809c0260 (the pattern entry, or its own draws);
without, `r1` then `θ1` (the opposite order). `x = cos θ0 x r0 + cos θ1 x r1 x spread` (the second product first, then
added), `y` the same with sin. The seed (0x1802a4e90, SHA-1) and the pattern (0x1809be170) as the JS had them.

## 3. FireBullet's direction (0x180a78120)

`AngleVectors(angles)` (0x181472530: forward, **left**, up), then per lane `(forward - left x X) + up x Y` (X, Y the
offset passed in [rbp+0x2930] / [rbp+0x2938]), **not normalised**, then `x range` for the trace's delta. The JS used
Source's right vector (the offsets mirrored left to right) and normalised the direction.

## What the port does, and its check

sim/src/combat/accuracy.rs, spread.rs, math/random.rs (tier0's stream), math/sha1.rs; `ze_accuracy`, `ze_spread`.
The server keeps every gun's accuracy itself (server/cs2web/combat/combat.js: updated once a server tick, a shot's penalty, the
landing, the deploy) and rolls each shot's bullets from the shot's angles; the client sends those angles (its view +
aim punch) and predicts with the same code. Checked against the old JS (a scratch comparison, 2026-11-11): 100,000
seeds identical; 71,752 offset lanes, the same draws, 114 lanes a few ulps off (tier0's cosf / sinf vs JS doubles,
values near 0); 120,000 accuracy steps, 118,241 identical, none 1e-5 apart (tier0's expf / powf). spread-test.mjs.

Stand-ins: the aim punch isn't on the server (the client's angles, checked within ~30 degrees of the view); the seed's
tick is the attack time's (CS2's, since 2026-11-11: usercmd.md 4; the client predicts its command's tick, and a held
shot's calculated time on its viewmodel's frame clock isn't, so its prediction can differ); the stack boost's count is 0; m_bIsWalking is the walk key; GetMaxSpeed taken as
m_flMaxSpeed[mode]; where in the frame UpdateAccuracyPenalty runs against the commands (after them here); the landing
and deploy functions not re-read; 0x1809c0260's own fallback draws not read (taken as θ then r, as the JS).
