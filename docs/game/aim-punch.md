# The aim punch: recoil and flinch (traced 2026-11-11; sim/src/combat/aim_punch.rs, punch_abi.rs, math/md5.rs)

server_20261105.dll unless named. CCSPlayer_AimPunchServices is the pawn's +0xe50. Two punch systems: the recoil's
(base tick +0x48, ratio +0x4c, angle +0x50, angular velocity +0x5c, step cache +0x68) and the flinch's (base tick
+0xa0 at ratio 0, angle +0xa4, no velocity, cache +0xb0). lib/recoil.js had client.dll's evaluator in outline with
CS:GO's kick numbers; this is the server's, every step from the disassembly.

## 1. The recoil table (0x1809be170 -> 0x1809be3c0) and Recoil (0x180a21030)

0x1809be170 builds a weapon's 0x608-byte record (keyed by item definition, the manager 0x181e0f9c8): the recoil
table at +4 by 0x1809be3c0 and the spread pattern at +0x408 (spread.md). **0x1809be3c0**, for each mode m = 0, 1: a
CUniformRandomStream seeded with m_nRecoilSeed (vdata +0x7d4); 64 entries, `angle = RandomFloat(-AngleVariance[m],
AngleVariance[m]) + Angle[m]` (+0x798 / +0x790), then `mag = RandomFloat(-MagnitudeVariance[m], ...) + Magnitude[m]`
(+0x7a8 / +0x7a0); m_bIsFullAuto (+0x72d): entries from 1 `prev + (new - prev) x 0.55` (both), entries 0..3
`mag x (((float)i x 0.25) x 0.25 + 0.75)`. (lib/recoil.js's UNSETTLED 0.55 / 0.75 are these.)

**Recoil 0x180a21030** (BaseGunFire 1809f8a70 calls it after the accuracy penalty and before m_iShotsFired / the
recoil index + 1): the index is `(int)m_flRecoilIndex` (+0xf98) for a full-auto gun, else 0x181daae60, the prediction
random seed (SetPredictionRandomSeed 0x1803ebc60, set by 0x180c7f1e0 from the command's CBaseUserCmdPB +0x6c,
random_seed, and back to -1 by 0x180c70120); entry `(index & 63) + mode x 64` (0x1809bf7d0: +4 angle, +8 magnitude of
8-byte records); a zoomed gun with 2+ zoom levels blends the two modes' magnitudes by zoom level / levels (not
ported: no zoom here). Then the kick, **0x180a4c5d0**(services, attack time, angle, magnitude).

## 2. The kick (0x180a4c5d0)

`T1 = attack + (1, 0)`, `Th = attack + (0, 0.5)` (0x1813b9090); `punch = evaluate(base, angle, velocity, T1)`;
`dt = (Th - base) as ticks` (0x1813b8fb0, (float)tick + ratio); `k = V_expf((dt > 0 ? dt x 0.015625 : 0) x -4.5)`;
`v = k x velocity`, zero when `0.03125 > |v|` (0x180a48c80: sqrtss((x x + y y) + z z)); `a = angle x 0x3c8efa35`;
`vel.y = v.y - V_sinf(a) x mag`, `vel.x = v.x - V_cosf(a) x mag`, vel.z = v.z; base = Th; angle = punch. Then the
camera services' view punch (pawn +0xb48, vfn 0x108 / 180c7e550): `x - cos(a) x mag x 0.055`, `y - sin(a) x mag x
0.055` (client-side its decay, lib/recoil.js).

## 3. The evaluator (0x180a3f8f0)

`secs = (target - base) as ticks`, `> 0 ? 0.015625 x it : 0` (0x180308890 returns 1/64). The cache (+0x00 base,
+0x08 angle, +0x14 velocity, +0x20 count, +0x28 entries of 12 bytes) is kept while base / angle / velocity compare
equal, else cleared; empty, it takes the angle (0x180a3f190). `n = cvttss2si(secs x 128)`. From the cache's count i
up to `min(n + 1, 128)`, each step: `p = expf(-0.0625) x p`; `|p| > 0.140625 ? p x (1 - 0.140625 / |p|) : 0`;
`t0 = base + from_ticks(((i - 1) x 0.0078125) x 64)`, `t1` the same with i (0x1813b9230, 0x1813b9090);
`p = 0.00390625 x v(t0) + p`, then `+ 0.00390625 x v(t1)`, `v(t) = expf((t - base > 0 ? (t - base) x 0.015625 : 0)
x -4.5) x velocity`, zero below 0.03125; pushed. Steps n and n + 1: the cached one, or past the cache the last x
`V_powf(expf(-0.0625), j - count + 1)`; each lane clamped to [-89, 89] (0x1801f5970); AngleQuaternion (0x181473e90)
each; CS2's fitted slerp (0x181813da0.. constants, the same sequence as lagcomp.rs blend_transform, 180cb4090) at
`t = secs x 128 - n`; normalised (dpps, sqrtps; zero -> 0x181f4a000); QuaternionAngles (0x181475b60); shorter than
0.03125 -> 0; `param_8`: doubled (lane + lane).

## 4. GetAimPunch (0x180a43b90) and who uses it

`T = now + (1, 0)` (0x180cacba0, 0x1813b9aa0); recoil system and flinch system evaluated at T, added (0x18029f040).
The pawn's wrapper 0x180ac5de0. **FX_FireBullets (0x1802a4f50) shoots along the angles of the attack's input history
entry** (BaseGunFire's attack info from GetWeaponAttackTime 0x180a02c60); it computes `EyeAngles (vfn 0x5f0) +
GetAimPunch(doubled)` only under the debug cvar **debug_aim_angle** (registered 0x180054470, default 0): non-zero
prints it ("Server..." via Msg), 2 shoots along it. So CS2's server takes the client's shot angles (which carry the
client's own punch); its own punch state is for the debug cvar, the flinch, and the network.

## 5. The flinch (0x180a89430 -> 0x180a3f3d0)

In the hit group function (shots.md 4), with `s = mp_flinch_punch_scale` (registered 0x1800c5fa0: **default 3.0,
flags 0x6002, FCVAR_CHEAT 0x4000**) and d the damage after the hit group's scale, a delta (pitch, yaw, roll) from 0:
- a blast (0x40) with no armor (and a flag r12b, unread): `pitch = 0 - (d s) x 0.1`, floored at `s x -4`;
- head, without a helmet (ItemServices +0x49; another flag at +0xb0 unread): `pitch = 0 - (d s) x 0.2`, floored at
  `s x -12`; `yaw = RandomFloat(-1, 1) x (s d)` (0x181687041 on the global stream 0x181e328d8), within `+-9 s`;
- chest, neck, stomach (d x 1.25 first): `pitch = 0 + (d s) x (armor > 0 ? -0.005 : -0.033)`, floored at `s x -4`;
- arms, legs: none.
**0x180a3f3d0**: `T = now + (1, 0)`; the flinch system evaluated at T (base tick, ratio 0, zero velocity) plus the
delta becomes its angle; its base tick T's.

**CS2Fixes and this server**: CS2Fixes upstream 59fd932 (2026-04-23, Vauff, "Remove cheat flag from
mp_flinch_punch_scale": src/cvars.cpp pUnCheatCvars) lets a server set it; the owner's Helm server (CS2Fixes
0787c87, which includes it) runs without the flinch so a shot zombie's view isn't kicked. GFL's public configs don't
set it. THIS SERVER: mp_flinch_punch_scale 0 (server/cs2web/combat/combat.js flinch), every delta 0.

## 6. The command's random seed

0x181daae60 is CBaseUserCmdPB's random_seed. Our client doesn't send one; both sides take Source's rule,
`MD5_PseudoRandom(command number) & 0x7fffffff` (TODO(trace): CS2's client.dll CreateMove is unread).
MD5_PseudoRandom is tier0's (tier0_20261103 0x180057d20): MD5 of the seed's 4 little-endian bytes, the int at
digest bytes 6..9 (`mov eax, [rbp - 0x5a]`, the state at rbp - 0x60); math/md5.rs, checked against Node's MD5 on
5,000 seeds (punch-test.mjs).

## What the port does

sim/src/combat/aim_punch.rs (the table, the kick, the evaluator, GetAimPunch, the flinch), punch_abi.rs
(`ze_aim_punch`), src/cs2web/sim/aim-punch.js. The client's Recoil (lib/recoil.js) runs on it: the viewmodel kicks from the
entry CS2 picks (m_flRecoilIndex before the shot and m_weaponMode from client/core/gun-accuracy.js, the command's seed)
at its clock, the camera and the shot's angles take GetAimPunch. The server keeps each pawn's (server/cs2web/combat/combat.js:
a kick per shot in BaseGunFire's order, the flinch per bullet hit, a fresh state per spawn, debug_aim_angle 2).
Checked: cargo test aim_punch / md5, punch-test.mjs (the seed, the table, a spray, client = server, the flinch).

The kick's attack time is GetWeaponAttackTime's (fire-gate.md 3, usercmd.md: the history entry's, or the calculated one;
ported 2026-11-11, fire_gate.rs attack_time). Stand-ins: the client's
clock is its viewmodel's seconds x 64; the zoomed blend of modes; the flinch's yaw draw (tier0's global stream, not on
the server: taken as 0, so at scale 0 nothing changes); the blast flinch's other flag; nothing sends the server's punch
to the client (CS2 networks m_aimPunch*; with the flinch off they only differ by when the client's frame clock
samples it); the evaluator is checked through its parts (AngleQuaternion, QuaternionAngles, the blend, expf / powf
against the DLLs), not called natively whole; math::pow's underflow branch (returns 0 here, the CRT's value).
