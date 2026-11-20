# Aim punch (recoil and flinch)

server_20261105 unless named; tier0_20261103. CS2Fixes 59fd932 (src/cvars.cpp pUnCheatCvars).

## Functions

| Address | Module | What |
|---|---|---|
| 0x1809be170 | server | build a weapon's 0x608-byte record (keyed by item definition; manager 0x181e0f9c8): recoil table at +4, spread pattern at +0x408 (spread.md) |
| 0x1809be3c0 | server | build the recoil table |
| 0x180a21030 | server | Recoil (called by BaseGunFire after the accuracy penalty, before m_iShotsFired / recoil index + 1) |
| 1809f8a70 | server | BaseGunFire |
| 0x1803ebc60 | server | SetPredictionRandomSeed |
| 0x180c7f1e0 | server | sets the seed from CBaseUserCmdPB +0x6c (random_seed) |
| 0x180c70120 | server | resets the seed to -1 |
| 0x1809bf7d0 | server | recoil entry (8-byte records: +4 angle, +8 magnitude) |
| 0x180a4c5d0 | server | the kick (services, attack time, angle, magnitude) |
| 0x1813b9090 | server | tick + (ticks, ratio) |
| 0x1813b8fb0 | server | tick difference as (float)tick + ratio |
| 0x1813b9230 | server | from_ticks |
| 0x180a48c80 | server | vector length `sqrtss((x x + y y) + z z)` |
| 180c7e550 | server | camera services vfn 0x108: view punch |
| 0x180a3f8f0 | server | the evaluator |
| 0x180308890 | server | returns 1/64 |
| 0x180a3f190 | server | cache: take the angle |
| 0x1801f5970 | server | clamp |
| 0x181473e90 | server | AngleQuaternion |
| 0x181813da0.. | server | fitted slerp constants (same as 180cb4090's blend) |
| 0x181475b60 | server | QuaternionAngles |
| 0x180a43b90 | server | GetAimPunch |
| 0x180cacba0, 0x1813b9aa0 | server | now + (1, 0) |
| 0x18029f040 | server | angle add |
| 0x180ac5de0 | server | the pawn's GetAimPunch wrapper |
| 0x1802a4f50 | server | FX_FireBullets |
| 0x180a02c60 | server | GetWeaponAttackTime |
| 0x180054470 | server | debug_aim_angle registration |
| 0x180a89430 | server | hit group function (the flinch, shots.md 4) |
| 0x1800c5fa0 | server | mp_flinch_punch_scale registration |
| 0x181687041 | server | RandomFloat on the global stream 0x181e328d8 |
| 0x180a3f3d0 | server | apply the flinch |
| 0x180057d20 | tier0 | MD5_PseudoRandom |

## Fields

| Offset | Field |
|---|---|
| pawn +0xe50 | CCSPlayer_AimPunchServices |
| services +0x48 / +0x4c / +0x50 / +0x5c / +0x68 | recoil: base tick / ratio / angle / angular velocity / step cache |
| services +0xa0 / +0xa4 / +0xb0 | flinch: base tick (ratio 0) / angle / cache (no velocity) |
| cache +0x00 / +0x08 / +0x14 / +0x20 / +0x28 | base / angle / velocity / count / entries (12 bytes each) |
| vdata +0x7d4 | m_nRecoilSeed |
| vdata +0x790 / +0x798 | Angle[m] / AngleVariance[m] |
| vdata +0x7a0 / +0x7a8 | Magnitude[m] / MagnitudeVariance[m] |
| vdata +0x72d | m_bIsFullAuto |
| weapon +0xf98 | m_flRecoilIndex |
| 0x181daae60 | prediction random seed (CBaseUserCmdPB random_seed) |
| pawn +0xb48 | camera services |
| ItemServices +0x49 | helmet; +0xb0 another flag (unread) |

## Constants

| Value | What |
|---|---|
| mp_flinch_punch_scale | default 3.0, flags 0x6002 (FCVAR_CHEAT 0x4000); CS2Fixes 59fd932 removes the cheat flag |
| debug_aim_angle | default 0 |
| 64 x 2 modes | recoil table entries |
| 0.55, 0.75, 0.25 | full-auto smoothing / first-entries ramp |
| 0x3c8efa35 | degrees -> radians (f32) |
| -4.5, 0.015625, 0.03125 | velocity decay, 1/64, zero threshold |
| 0.055 | view punch scale |
| expf(-0.0625), 0.140625, 0.00390625, 0.0078125, 128 | evaluator step decay, friction, half step weight, step, steps/s |
| 0x181f4a000 | zero quaternion fallback |

## Recoil table (0x1809be3c0)

- For m = 0, 1: a CUniformRandomStream seeded with m_nRecoilSeed; 64 entries: `angle = RandomFloat(-AngleVariance[m], AngleVariance[m]) + Angle[m]`, then `mag = RandomFloat(-MagnitudeVariance[m], MagnitudeVariance[m]) + Magnitude[m]`.
- m_bIsFullAuto: entries from 1 `prev + (new - prev) x 0.55` (both); entries 0..3 `mag x (((float)i x 0.25) x 0.25 + 0.75)`.

## Recoil (0x180a21030)

- Index: `(int)m_flRecoilIndex` for a full-auto gun, else the prediction random seed (0x181daae60).
- Entry `(index & 63) + mode x 64`. A zoomed gun with 2+ zoom levels blends the two modes' magnitudes by zoom level / levels.
- Then the kick 0x180a4c5d0.

## The kick (0x180a4c5d0)

1. `T1 = attack + (1, 0)`, `Th = attack + (0, 0.5)`; `punch = evaluate(base, angle, velocity, T1)`.
2. `dt = (Th - base) as ticks`; `k = V_expf((dt > 0 ? dt x 0.015625 : 0) x -4.5)`; `v = k x velocity`, zero when `0.03125 > |v|`.
3. `a = angle x 0x3c8efa35`; `vel.y = v.y - V_sinf(a) x mag`, `vel.x = v.x - V_cosf(a) x mag`, vel.z = v.z; base = Th; angle = punch.
4. View punch (pawn +0xb48 vfn 0x108): `x - cos(a) x mag x 0.055`, `y - sin(a) x mag x 0.055` (decays client-side).

## The evaluator (0x180a3f8f0)

1. `secs = (target - base) as ticks`, `> 0 ? 0.015625 x it : 0`.
2. Cache kept while base / angle / velocity compare equal, else cleared; empty, takes the angle (0x180a3f190).
3. `n = cvttss2si(secs x 128)`. From the cache's count i up to `min(n + 1, 128)`, each step: `p = expf(-0.0625) x p`; `|p| > 0.140625 ? p x (1 - 0.140625 / |p|) : 0`; `t0 = base + from_ticks(((i - 1) x 0.0078125) x 64)`, t1 the same with i; `p = 0.00390625 x v(t0) + p`, then `+ 0.00390625 x v(t1)`, with `v(t) = expf((t - base > 0 ? (t - base) x 0.015625 : 0) x -4.5) x velocity`, zero below 0.03125; pushed.
4. Steps n and n + 1: the cached one, or past the cache the last x `V_powf(expf(-0.0625), j - count + 1)`; each lane clamped to [-89, 89]; AngleQuaternion each.
5. Fitted slerp at `t = secs x 128 - n`; normalised (dpps, sqrtps; zero -> 0x181f4a000); QuaternionAngles; shorter than 0.03125 -> 0; `param_8`: doubled (lane + lane).

## GetAimPunch (0x180a43b90)

- `T = now + (1, 0)`; recoil and flinch systems evaluated at T, added.
- FX_FireBullets shoots along the angles of the attack's input history entry (GetWeaponAttackTime); it computes `EyeAngles (vfn 0x5f0) + GetAimPunch(doubled)` only under debug_aim_angle: non-zero prints it ("Server..." via Msg), 2 shoots along it. The server takes the client's shot angles; its own punch is for the debug cvar, the flinch and the network (m_aimPunch*).

## The flinch (0x180a89430 -> 0x180a3f3d0)

`s = mp_flinch_punch_scale`, d the damage after the hit group's scale; delta (pitch, yaw, roll) from 0:
- Blast (0x40), no armor (and flag r12b, unread): `pitch = 0 - (d s) x 0.1`, floored at `s x -4`.
- Head, no helmet (ItemServices +0x49; flag +0xb0 unread): `pitch = 0 - (d s) x 0.2`, floored at `s x -12`; `yaw = RandomFloat(-1, 1) x (s d)` (global stream), within `+-9 s`.
- Chest, neck, stomach (d x 1.25 first): `pitch = 0 + (d s) x (armor > 0 ? -0.005 : -0.033)`, floored at `s x -4`.
- Arms, legs: none.
- 0x180a3f3d0: `T = now + (1, 0)`; the flinch system at T (base tick, ratio 0, zero velocity) plus the delta becomes its angle; base tick = T.
- CS2Fixes 59fd932 (2026-04-23, "Remove cheat flag from mp_flinch_punch_scale") lets a server set it; GFL's public configs don't set it.

## The command's random seed

- 0x181daae60 is CBaseUserCmdPB's random_seed; set from the client's command.
- MD5_PseudoRandom (tier0 0x180057d20): MD5 of the seed's 4 little-endian bytes, the int at digest bytes 6..9 (`mov eax, [rbp - 0x5a]`, the state at rbp - 0x60). Source's rule for the seed: `MD5_PseudoRandom(command number) & 0x7fffffff`.

## Unread

- CS2's client.dll CreateMove (how the client makes random_seed).
- The blast flinch's flag r12b; ItemServices +0xb0.
