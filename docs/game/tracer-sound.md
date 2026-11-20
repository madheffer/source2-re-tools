# A bullet passing by you: FX_TracerSound

client_20261105 (disassembly), client_20261015 (decompiled).

## Functions

| Address | Module | What |
|---|---|---|
| 180c2d0a0 (10-15 180c2b680) | client | FX_TracerSound(start*, end*, type); VProf scope "FX_TracerSound" |
| 180c15b50 | client | MainViewOrigin (engine client vfn 0x310): the listener |
| 180c2eaf0 | client | Ray_t init: start, delta = end - start, a non-zero-delta flag |
| 18175d680 (10-15 181758c80) | client | IntersectRayWithRay |
| 181748760 | client | 1 / length helper used by IntersectRayWithRay's normalize (1 / length, 0 for a zero length; 181748760 applies outside 1e-17 .. 1e17) |
| 18015a360 | client | clamp |
| 181742b20 (10-15 18173e120) | client | CalcClosestPointOnLineSegment |
| 180c1ce10 | client | the sound's parameters |
| 1803e8650 | client | EmitSound from the world at a point (hash 0x5a7cce4d) |
| 180902c40 (10-15 180901390) | client | weapon services' tracer record (cs_player_weaponservices.cpp): caller |
| 18093eec0 | client | muzzle attachment position |
| 180bad920 | client | "ParticleTracer" effect handler (fx_tracer.cpp): caller, type 1 |
| 180bb2be0 | client | "TracerSound" effect handler (fx_tracer.cpp): caller, type = the effect's byte +0x63 |
| 180c2cfe0 | client | caller (from 180bb29c0, tracer_player.vpcf), type 1 |
| 180de3310, 180237c40 | server | precache lists naming "TracerSound" / "ParticleTracer" (nothing dispatches them) |

## Fields

| Offset | Field |
|---|---|
| gpGlobals +0x30 | curtime |
| weapon vfn 0xbe0 | CSWeaponType |
| weapon vdata +0x728 | m_eSilencerType |
| effect +0x63 | TracerSound's type byte |

## Constants

| Value | What |
|---|---|
| cl_tracer_whiz_distance 72 | client float cvar (reg 1800e2170, handle 0x182575470) |
| cl_tracer_whiz_infront_distance 32 | client float cvar (reg 1800e2210, handle 0x182575480) |
| 0x18223cfb4 (11-05) | g_BulletWhizTimer |
| 0x182235110 | CUniformRandomStream: the client's global stream |
| 24 | listener ray drop (z) |
| 1e-5 | closest-point |d|^2 threshold |
| 5 | max prints of "Can't set position/velocity on whiz sound" |
| 100 u | muzzle-to-start distance beyond which a tracer shot restores the original start |

## Types

| type | crack | tail | whiz distance | timer (min, max) |
|---|---|---|---|---|
| 1 | BulletBy.Subsonic | BulletBy.Subsonic.Tail | cl_tracer_whiz_distance | 0.1, 0.1 |
| 0x20 | BulletBy.Supersonic.Crack | BulletBy.Supersonic.Tail | cl_tracer_whiz_distance | 0.1, 0.1 |
| 2 | Bullets.GunshipNearmiss | none | 72 | 0.1, 0.1 |
| 4 | Bullets.StriderNearmiss | none | 72 | 0.1, 0.1 |
| 0x10 | Underwater.BulletImpact | none | 48 | 0.3, 0.6 |
| other | nothing | | | |

## FX_TracerSound order

1. Listener = MainViewOrigin. Types 1 / 0x20 only: bullet ray and listener ray (listener, listener - 24 z);
   IntersectRayWithRay: both deltas normalized, `c = a x b`, `e = c x (s1 - s0)`, t on the second =
   `((-e.z a.z - e.y a.y) - e.x a.x) / |c|^2` (0 when parallel); t clamped to [0, 1]; listener z -= `t x 24`.
2. Return while `g_BulletWhizTimer - curtime > 0`.
3. Return when listener == start exactly, or `|listener - start|^2 <= whiz^2` (own muzzle). Closest point:
   `t = (d . P - d . A) / |d|^2` for `|d|^2 >= 1e-5`, clamped [0, 1]; return when `|listener - closest|^2 >= whiz^2`.
4. Crack: `dir = normalize(end - start)`; `at = start + dir x max(|start - listener| - cl_tracer_whiz_infront_distance, 0)`;
   parameters (180c1ce10), EmitSound at `at`. Tail: the same at `end` (empty name for type 0x10).
5. The whiz-sound message printed up to 5 times (a counter, no condition).
6. Timer = curtime + RandomFloat(min, max).

f32 sums (11-05 disassembly): distances `(dy^2 + dx^2) + dz^2`, lengths `(dz^2 + dy^2) + dx^2`; the helpers' as the
10-15 decompile writes them.

## Callers

- 180902c40: last step for every bullet (after the smoke trail, with or without a drawn tracer); type 0x20 when
  CSWeaponType is 2 / 3 / 5 (SMG, rifle, sniper) and m_eSilencerType is NONE, else 1. Start: the muzzle attachment
  (18093eec0) when the weapon has one, else the shot's start.
- Nothing passes 2, 4 or 0x10: Bullets.GunshipNearmiss, Bullets.StriderNearmiss, Underwater.BulletImpact never play in CS2.

## Unread

- The effect handlers' own callers on the client (nothing reaches them from the server).
- 180c1ce10's parameter build (volume / soundlevel).
- The random stream's draw (RandomFloat(0.1, 0.1) is 0.1 regardless; the water branch never runs).
