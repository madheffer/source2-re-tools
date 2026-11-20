# Spotting and the radar; the transmit cvars

server_20261105, client_20261015 (the 2026-11-05 client has the same readers 8 bytes on).

## Functions

| Address | Module | What |
|---|---|---|
| 1801f806f | server | sets a pawn's m_nSpotRules = 9 when it goes active (in the pawn state machine 1801f7ca0, "STATE_ACTIVE" / "STATE_DEATH_ANIM") |
| 1801f7ca0 | server | pawn state machine |
| 1803536c0 | server | copies m_nSpotRules (and the state) between pawns |
| 1801b7d80 | server | CCSEntitySpotting slot 32 (0x100): `if (curtime > this+0x14 + 0.5)` run 1801d9e50 |
| 180923fb0, 180957e50 | server | also call 1801b7d80 (round events: not read) |
| 1801d9e50 | server | the spotting update |
| 180c86720 / 180c8ace0 / 180c86b40 | server | entity list walk |
| FUN_18093eba0 | server | hostage walk |
| 1801da220 | server | (entity, state, rules): one entity's spotting |
| 1801b9fd0 | server | observer walk (each controller slot, +0x514 0 or 3, a pawn (180b55040) passing vfn 0x558) |
| 180b55040 | server | the slot's pawn |
| 1801ce5b0 | server | notes the m_bSpotted change |
| 1801c16d0 / 1801d6920 | server | clear the mask / OR a spotter slot (< 64) in |
| 1801bd100 | server | (query, observer pawn): the view test |
| 180927cb0 / 18017e2d0 | server | the controller valid (on pawn +0xd38) |
| 180b4fa70 | server | eye and forward |
| 1814738b0 | server | VectorNormalize |
| 180a7a350 | server | FOV on the camera services |
| 1801f95b0 | server | time since m_flFOVTime |
| 1801d7460 | server | line of sight |
| 1801d6c60 | server | ignore the observer and target |
| 180c2f3c0 | server | the ray |
| 18032a570 | server | smoke volumes test (DAT_181fa5e10): the line isn't through smoke |
| 180a7a4c0 | server | (camera services, target): fog test |
| 180a7a3e0 | server | the fog's opacity at a distance |
| 180b55410 | server | the observer's slot |
| 1800a3500 | server | `mp_teammates_are_enemies` registration |
| 18004d830..18004da40 | server | radarvis* registrations |
| 1800f0ec0 | server | `sv_shared_team_pvs` registration |
| 1800f0b60.. | server | `sv_force_transmit_ents` registration |
| 180dde830 | client | CCSGO_HudRadar's per-player update |
| 1808d9290 | client | IsOtherEnemy: another team (controller +999), or anyone with mp_teammates_are_enemies |
| 1809f6b30 | client | observer-target branch (not read) |
| 1813ce910 | client | reads m_bSpotted (pawn +0x3d1) |
| 180dd8b00 | client | seen by a teammate |
| 180c8a7d0 | client | a trace's fraction >= 1.0 |

## Fields

| Class | `m_entitySpottedState` (EntitySpottedState_t) | `m_nSpotRules` |
|---|---|---|
| CCSPlayerPawn (server) | +0x14a0 | +0x14b8 |
| hostage | +0xb98 | +0xbb0 |
| item_cutters (defuser) | +0xae0 | +0xaf8 |
| planted_c4 | +0xf38 | +0xf50 |
| weapon_c4 | +0x12d8 | +0x12f0 |
| C_CSPlayerPawn (client 2026-11-05 / 10-15) | +0x1e88 / +0x1e80 | +0x1ea0 / - |

| Offset | Field |
|---|---|
| EntitySpottedState_t +0x8 | m_bSpotted (bool) |
| EntitySpottedState_t +0xc | m_bSpottedByMask (uint32[2]: a bit per controller slot; client pawn +0x1e8c..) |
| CCSEntitySpotting +0x14 | last update time |
| controller +0x514 | connection state (0 or 3 pass) |
| query +0x14 | team asked for |
| query +0x18 | spotted |
| query +0x20 / +0x28 | spotter vector count / data |
| pawn +0x344 | team |
| pawn +0xb48 | camera services: m_iFOV +0x178, m_iFOVStart +0x17c, m_flFOVTime +0x180, m_flFOVRate +0x184 |
| radar +0x380 / +0x398 | player count / 0x200-byte records |
| radar +0x1d3e4 | the radar's own mask (shows a slot regardless) |
| record +0x134 / +0x13c, flags +0x1fd | 0.25 s fade timers |

## Constants

| Value | What |
|---|---|
| 0.5 (0x18178057c: 0x3f000000) | update interval |
| `mp_teammates_are_enemies` bool 0 | client DAT_1824bcf90 |
| object pointer + 0x58 | where each radarvis* cvar's value is read |
| `radarvismethod` int 1 | "0 for traditional method, 1 for more realistic method" (flags 0x4000) |
| `radarvisdistance` float 1000.0 | flags 0x4000 |
| `radarvismaxdot` float 0.996 | flags 0x4000 |
| `radarvispow` float 0.4 | flags 0x4000 |
| 0x18178fe08 0x40490e56 = 3.1414999961853027 | the "pi" in the cone |
| 0x18178fe1c 180.0 | |
| 1e-17 / 1e17 | VectorNormalize bounds |
| 0.995 (0x18178fdf0), 0.98 (0x18178fdec) within 900 u (0x18178fe28), 0.8 (0x18178fde4) within 250 u (0x18178fe20) | radarvismethod 0 |
| 0x800180041 | LOS trace interacts-with; collision group 3; flags `(x & 0xc9) \| 0x49`; 0x0f00ffff (detail layers 0xffff, target layer 0, object set 0xf) |
| 0x18178c240 | LOS trace filter vtable |
| 0.9 (0x18178fde8 0x3f666666) | max fog opacity |
| 0x18178bce0 | CCSEntitySpotting RTTI vtable |
| 1600 u, + 56 | client radar exception: 2D distance, the pawn's feet + 56 |
| 9 | an active pawn's m_nSpotRules |

## Update (1801d9e50)

1. `this+0x14 = curtime` (gpGlobals +0x30).
2. Every pawn passing vfn 0x558 and vfn 0xca8 whose controller's +0x514 is 0 or 3: 1801da220(pawn, pawn+0x14a0, [pawn+0x14b8]).
3. Every hostage, `item_cutters`, `planted_c4`, `weapon_c4` by class name, each with its own fields.

## One entity (1801da220)

1. rules 0: nothing. Observer team: rules & 1: 0 when mp_teammates_are_enemies, else `(team != 3) + 2`; else & 2: 3 (CT); else & 4: 2 (T).
2. Point: EyePosition (vfn 0x5e8) when vfn 0x558 says so, else WorldSpaceCenter (vfn 0x2c8).
3. Observer walk 1801b9fd0 with the query; m_bSpotted written only when changed (1801ce5b0); the mask rebuilt (1801c16d0, then 1801d6920 per spotter).

## View test (1801bd100)

1. Query team 0 or the observer's (+0x344); vfn 0x550; controller valid; eye and forward from 180b4fa70.
2. `d = point - eye`; length `sqrtss((z*z + y*y) + x*x)` (VectorNormalize when under 1e-17 or over 1e17, 0 at exactly 0); `dir = d x (1 / length)`; `dot = ((fz*dz) + (fy*dy)) + (fx*dx)` (1801bd2a3..2c8); dot < 0 fails.
3. radarvismethod 1: `half = FOV / 2` (int, signed shift: cdq / sub / sar); `cone = cosf(half x 3.1415 / 180)` (import [rip+0x15addf9]); `v = powf(length / radarvisdistance, radarvispow)` (import [rip+0x15addbf]); `thr = cone > v ? cone : minss(radarvismaxdot, v)`; fails unless `dot > thr` (seta).
4. radarvismethod 0: dot > 0.995, or > 0.98 within 900, or > 0.8 within 250.
5. Line of sight 1801d7460: the ray from the eye to the point reaches it (fraction == 1.0), and 18032a570 says not through smoke.
6. 180a7a4c0: distance from the services' pawn's eye (vfn 0x5e8) to the target's WorldSpaceCenter (vfn 0x2c8), fog opacity (180a7a3e0) < 0.9.
7. Spotted: query +0x18 = 1, the observer's slot appended.

FOV (180a7a350): m_iFOV, 0 -> (int)vfn 0xe8; while m_flFOVRate != 0 and the time since m_flFOVTime is below the rate and m_iFOVStart <= that FOV: the start.

## Client radar (180dde830)

1. Per slot with a pawn: enemy = 1808d9290. A teammate is shown.
2. An enemy is shown when your slot's bit is set in its m_bSpottedByMask, or, unless mp_teammates_are_enemies, when its m_bSpotted is set.
3. One not seen by a teammate (180dd8b00), within 1600 u (2D) of your eye and with a clear line (180c8a7d0 from your eye to the pawn's feet + 56): **not** shown that way (why unread).
4. The radar's mask +0x1d3e4 shows a slot regardless; 0.25 s timers fade in and out.

## Transmit cvars

- `sv_shared_team_pvs` (bool, default 0): "PVS is shared between teams".
- `sv_force_transmit_ents` (bool, default 0): "Will transmit all entities to client, regardless of PVS conditions (will still skip based on transmit flags, however)".
- Also registered: `sv_pvs_max_distance`, `sv_use_pvs_cache`, `sv_pvs_cache_query_inflate_amount`, `sv_pvs_random`, `sv_hide_ent_in_pvs`, `sv_parallel_checktransmit`; no `sv_occlude_players` string in server.dll (no server-side occlusion culling of players). See [transmit.md](transmit.md).

## Unread

- CCSPlayerPawn's transmit state for teammates / spotted enemies outside your PVS (where the radar's positions come from).
- The other PVS cvars' defaults (cvardump took a neighbour's help for `sv_pvs_max_distance`).
- 180a7a3e0's fog opacity; 18032a570's smoke test.
- Which game-system hook slot 32 is; the two forced updates' callers.
- The client's 1600 u exception, the fade timers, the death mark.
- Whether the LOS trace meets other players' bodies (mask 0x800180041 against the pawns' layers).
