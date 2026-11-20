# A shot's inaccuracy and spread

server_20261105, tier0_20261103 (the CRT).

## Functions

| Address | Module | What |
|---|---|---|
| 0x180a26bd0 | server | UpdateAccuracyPenalty (CCSWeaponBaseGun vfn 0xd70) |
| 0x180b1d3d0 | server | CCSPlayer_WeaponServices vfn 0x68: a per-frame service call, calls UpdateAccuracyPenalty (also the R8's SecondaryAttack) |
| 0x180a274b0 | server | the turning term (behind sv_turning_inaccuracy_enabled) |
| 0x1809fbae0 | server | 32-entry movement history (behind the strafing cvar) |
| 0x180a02600 | server | GetRecoveryTime |
| 0x180a01400 | server | GetInaccuracy |
| 0x1801cd370 | server | Length2D: `sqrtss(x x + y y)` |
| 0x180a28730 | server | `sqrt(fabs(vz))` |
| 0x180a029b0 | server | the strafing term |
| 0x1801d3440 | server | RemapValClamped |
| 1809f8a70 | server | BaseGunFire |
| 0x180a1d870 | server | the landing (not re-read) |
| 0x1809fb560 | server | the deploy (not re-read) |
| 0x1802a59c0 | server | FX_FireBullets (from 0x1802a4f50) |
| 0x1802a4e90 | server | the seed (SHA-1) |
| 0x1809be170 | server | the spread pattern |
| 0x1809c0260 | server | the pattern entry (or its own draws) |
| 0x180a78120 | server | FireBullet's direction |
| 0x181472530 | server | AngleVectors: forward, **left**, up |
| IAT 0x18176aee0 / 0x18176b218 | server | tier0 RandomSeed / RandomFloat (the global stream) |
| IAT 0x18176b118 / 0x18176af00 | server | tier0 V_cosf / V_sinf |
| 0x1802e0d70 / 0x1802e6570 | tier0_20261103 | CRT cosf / sinf (same code as tier0_20260923's 0x1802e0c30 / 0x1802e6430: every constant the same) |
| 0x1800c1de0 | server | sv_turning_inaccuracy_enabled registration (object 0x18212b128) |
| 0x1800c1b50 | server | sv_strafing_inaccuracy_enabled registration (object 0x18212b158) |
| 0x1800c2140 | server | weapon_air_spread_scale registration |

## Fields

| Offset | Field |
|---|---|
| weapon +0xf74 | the turning term; +0xf84 its clamped copy |
| weapon +0xf88 | m_fAccuracyPenalty |
| weapon +0xf8c | the last update's curtime |
| weapon +0xf98 | m_flRecoilIndex |
| weapon +0x1038 | the last fire's curtime |
| vdata +0x7b8 / +0x7bc / +0x7c0 | m_flInaccuracyJumpInitial / JumpApex / Reload |
| vdata +0x840 / +0x844 | m_flRecoveryTimeCrouch / Stand |
| vdata +0x848 / +0x84c | m_flRecoveryTimeCrouchFinal / StandFinal |
| vdata +0x850 / +0x854 | m_nRecoveryTransitionStartBullet / EndBullet |
| pawn +0x388 bit 2 | FL_DUCKING |
| pawn +0x1478 | m_bIsWalking |
| gpGlobals +0x34 | frametime (1/64 a frame; the command loop zeroes it, so not per command) |

## Constants

| Value | What |
|---|---|
| sv_turning_inaccuracy_enabled false | bool default byte +0x37 is 0: +0xf84 stays 0 |
| sv_strafing_inaccuracy_enabled false | 0x180a029b0 adds nothing |
| weapon_air_spread_scale 1.0 | |
| 0x40c90fdb | 2π (θ0's upper bound) |
| 0.34 / 0.95 | move remap bounds (x max speed) |
| 0.25 | move exponent; `lo` factor |
| 0.1 | recoil index snaps to 0 at or below |
| 1/64 | recoil decay delay past the cycle time |

## UpdateAccuracyPenalty (0x180a26bd0)

1. Target: MOVETYPE_LADDER (or a stack of `weapon_accuracy_stack_boost_limit` players under the ground entity): `Ladder[m] + Ladder[0] + 0`; on a ground entity: `Crouch()` with FL_DUCKING else `Stand[m]`, `+ 0`; in the air `Jump[m] x weapon_air_spread_scale + Stand[m] + 0`; `+ Reload` while m_bInReload.
2. Target <= penalty (`a < b || a == b`): GetRecoveryTime != 0: `penalty = V_expf(-(V_logf(10) / recovery) x frametime) x (penalty - target) + target`, else the target. Target above: the target.
3. 0x180a274b0, then 0x1809fbae0.
4. Recoil index > 0 and curtime > (last fire + GetCycleTime(0)) + 1/64: `index = V_expf(-(ln10 + ln10) x frametime) x (index - 0) + 0`; 0 at or below 0.1.
5. +0xf8c = curtime.

## GetRecoveryTime (0x180a02600)

Ladder: RecoveryTimeStand; off FL_ONGROUND: RecoveryTimeCrouch x 4; else crouched / standing
`RemapValClamped((float)(int)index, Start, End, RecoveryTime, RecoveryTimeFinal)`, the base alone when the Final is -1.

## GetInaccuracy (0x180a01400)

1. weapon_accuracy_forcespread > 0 -> min(it, 1); weapon_accuracy_nospread -> 0.
2. `move = RemapValClamped(Length2D(velocity), max x 0.34, max x 0.95, 0, 1)`, max = vfn 0xc20 (GetMaxSpeed); `move > 0` and not m_bIsWalking -> `V_powf(move, 0.25)`; `x Move[m]`; `total = penalty + move`.
3. No ground entity: `ji = scale x JumpInitial`, `ja = scale x JumpApex`, `sMax = sqrt(sv_jump_impulse)`, `sV = sqrt(fabs(vz))`, `lo = sMax x 0.25`, `air = ((sV - lo) x (ji - ja)) / (sMax - lo) + ja` (lo == sMax: ji when sV >= sMax, else ja), clamped to [0, ji + ji], added. The stack boost adds 0.0.
4. `(0x180a029b0 + total) + (+0xf84)`, at most 1.

## RemapValClamped (0x1801d3440)

a == b -> (v - b >= 0) ? d : c; else `t = (v - a) / (b - a)`, maxss 0, minss 1, `t x (d - c) + c`.

## After a shot (BaseGunFire 1809f8a70)

`penalty = Fire[mode] + penalty`, `index + 1`; +0x1038 = curtime (the primary branch).

## FX_FireBullets (0x1802a59c0)

1. Per bullet (the first, or every one with weapon_accuracy_shotgun_spread_patterns): `r0 = RandomFloat(0, 1)`, `θ0 = RandomFloat(0, 2π)`.
2. R8 in mode 1: `1 - r²`; Negev under recoil index 3: squares (3 - index) times and takes `1 - r`. Two debug flags (r14b: r = 1; r15b: θ = π/2) belong to the force / no-spread cvars. `r0 x= inaccuracy`.
3. Spread (θ1, r1): with patterns 0x1809c0260; without, `r1` then `θ1` (the opposite order).
4. `x = cos θ0 x r0 + cos θ1 x r1 x spread` (the second product first, then added); `y` the same with sin.

## FireBullet's direction (0x180a78120)

`AngleVectors(angles)` (forward, **left**, up), then per lane `(forward - left x X) + up x Y` (X, Y the offset passed in
[rbp+0x2930] / [rbp+0x2938]), **not normalised**, then `x range` for the trace's delta.

## Unread

- The seed's tick is the attack time's ([usercmd.md](usercmd.md) 4).
- Where in the frame UpdateAccuracyPenalty runs against the commands.
- The landing and deploy functions (not re-read).
- 0x1809c0260's own fallback draws (taken as θ then r).
- GetMaxSpeed taken as m_flMaxSpeed[mode]; m_bIsWalking taken as the walk key.
