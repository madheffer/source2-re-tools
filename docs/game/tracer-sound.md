# A bullet passing by you: FX_TracerSound

client_20261105.dll (tools/re: fnat, disasm, xref) and client_20261015.dll in Ghidra (decompiled), read 2026-11-17.
Port: web/src/cs2web/client/fx/tracer-sound.js (tracer-sound-test.mjs), called from client/core/game.js for every
other player's bullet (the `impact` event: start = their muzzle record, as the smoke trail and the tracer take it)
and for your own shot.

## FX_TracerSound(start*, end*, type) — 11-05 `180c2d0a0`, 10-15 `180c2b680`

| type | crack | tail | whiz distance | timer (min, max) |
|---|---|---|---|---|
| 1 | BulletBy.Subsonic | BulletBy.Subsonic.Tail | cl_tracer_whiz_distance | 0.1, 0.1 |
| 0x20 | BulletBy.Supersonic.Crack | BulletBy.Supersonic.Tail | cl_tracer_whiz_distance | 0.1, 0.1 |
| 2 | Bullets.GunshipNearmiss | none | 72 | 0.1, 0.1 |
| 4 | Bullets.StriderNearmiss | none | 72 | 0.1, 0.1 |
| 0x10 | Underwater.BulletImpact | none | 48 | 0.3, 0.6 |
| other | nothing | | | |

(A VProf scope "FX_TracerSound" around it.) In order:

1. The listener: MainViewOrigin (vfn 0x310 of the engine client -> 180c15b50). For types 1 / 0x20 only: the bullet
   ray (180c2eaf0 = Ray_t init: start, delta = end - start, a non-zero-delta flag) and the listener's ray (listener,
   listener - 24 z); IntersectRayWithRay (**18175d680**, 10-15 181758c80: both deltas normalized (1 / length, 0 for 0,
   181748760 outside 1e-17 .. 1e17), c = a x b, t on the second = ((-e.z a.z - e.y a.y) - e.x a.x) / |c|^2 with e =
   c x (s1 - s0); 0 when parallel); t clamped to [0, 1] (18015a360), listener z -= t x 24.
2. Return while the timer runs: g_BulletWhizTimer (11-05 0x18223cfb4) - curtime (gpGlobals +0x30) > 0.
3. Return when the listener is exactly the start; or when |listener - start|^2 <= whiz^2 (your own muzzle);
   CalcClosestPointOnLineSegment (**181742b20**, 10-15 18173e120: t = (d . P - d . A) / |d|^2 for |d|^2 >= 1e-5,
   clamped to [0, 1]); return when |listener - closest|^2 >= whiz^2.
4. The crack: direction = normalize(end - start); at = start + direction x max(|start - listener| -
   cl_tracer_whiz_infront_distance, 0); its sound parameters (180c1ce10), EmitSound from the world at `at` (1803e8650,
   hash 0x5a7cce4d). The tail: the same at `end` (an empty name for the water type).
5. "Can't set position/velocity on whiz sound" printed up to 5 times (a counter, no condition).
6. The timer = curtime + RandomFloat(min, max) (CUniformRandomStream at 0x182235110, the client's global stream).

f32 sums: distances (dy^2 + dx^2) + dz^2, lengths (dz^2 + dy^2) + dx^2 (11-05 disassembly); the helpers' as the 10-15
decompile writes them (the port's comments).

Cvars (client, float): **cl_tracer_whiz_distance 72** (1800e2170, handle 0x182575470), **cl_tracer_whiz_infront_distance
32** (1800e2210, handle 0x182575480).

## Callers

| caller | type |
|---|---|
| 180902c40 (10-15 180901390), the weapon services' tracer record (cs_player_weaponservices.cpp), its last step for every bullet (after the smoke trail, with or without a drawn tracer) | 0x20 when the weapon's CSWeaponType (vfn 0xbe0) is 2 / 3 / 5 (SMG, rifle, sniper) and its vdata m_eSilencerType (+0x728) is NONE, else 1 |
| 180bad920 (fx_tracer.cpp), the "ParticleTracer" effect handler | 1 |
| 180bb2be0 (fx_tracer.cpp), the "TracerSound" effect handler | the effect's byte +0x63 |
| 180c2cfe0 (from 180bb29c0, tracer_player.vpcf) | 1 |

The server names "TracerSound" and "ParticleTracer" only in precache lists (180de3310, 180237c40): nothing dispatches
them, so no caller passes 2, 4 or 0x10: **Bullets.GunshipNearmiss, Bullets.StriderNearmiss and Underwater.BulletImpact
never play in CS2**. The record's start: the muzzle attachment's position (18093eec0) when the weapon has one (a
tracer shot puts the original start back when the muzzle is over 100 u from it), else the shot's start.

Unread: the effect handlers' own callers on the client (nothing reaches them from the server); 180c1ce10's parameter
build (the event's volume / soundlevel as the sound system gives them); the random stream's draw (RandomFloat(0.1,
0.1) is 0.1 whatever it draws; the water branch never runs).
