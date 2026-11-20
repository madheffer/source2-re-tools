# Spotting and the radar; the transmit cvars

Read 2026-11-15 from `server_20261105.dll` (ReVa + tools/re: schema, fieldwrites, xref, cvardump, disasm, disasm_consts,
callers) and `client_20261015.dll` (ReVa; the 2026-11-05 client has the same readers 8 bytes on: its pawn's
`m_entitySpottedState` is at 0x1e88, the 2026-10-15 one's at 0x1e80). Ported in web/server/cs2web/comms/spotting.js (the server's
spotting), web/src/cs2web/client/hud/radar-view.js (the radar's rule), web/src/ui/radar.js (the radar's drawing).

## The fields

| class | `m_entitySpottedState` (EntitySpottedState_t) | `m_nSpotRules` |
|---|---|---|
| CCSPlayerPawn (server) | +0x14a0 | +0x14b8 |
| hostage | +0xb98 | +0xbb0 |
| item_cutters (defuser) | +0xae0 | +0xaf8 |
| planted_c4 | +0xf38 | +0xf50 |
| weapon_c4 | +0x12d8 | +0x12f0 |
| C_CSPlayerPawn (client 2026-11-05 / 10-15) | +0x1e88 / +0x1e80 | +0x1ea0 / - |

EntitySpottedState_t: `m_bSpotted` +0x8 (bool), `m_bSpottedByMask` +0xc (uint32[2]: a bit per controller slot).
A pawn's `m_nSpotRules` is set to **9** when it goes active (1801f806f, in the pawn state machine 1801f7ca0 with
"STATE_ACTIVE" / "STATE_DEATH_ANIM"); 1803536c0 copies it (and the state) between pawns.

## The server's update

**Ours, in the port** (web/server/cs2web/comms/spotting.js, the owner's call 2026-11-15): the update is spread over its half
second (each player a phase of 32, updated every 32 ticks: CS2's rate, by the same test; only the tick within the half
second differs), and without mp_teammates_are_enemies the observer walk stops at the first spotter (m_bSpotted the
same; the mask, which nothing reads then, holds that one). At 100 bots on ze_dark_souls: 0.24 ms a tick on average,
p99 1.0 ms, against CS2's all-at-once 2-3 ms (5-9 ms at worst) in one tick each half second. The rare 5-12 ms ticks
left were the trace world's sync (src/cs2web/sim/trace-world.js sync: the physics mirror and mapEntities after map entities were
spawned or removed), paid by whichever trace comes first after a change, not by the spotting test (the traces
themselves: 8 us on average). That sync now sends only what changed (docs/TICK64.md 6c): p99 0.4 ms.


- **CCSEntitySpotting** (RTTI vtable 0x18178bce0). Slot 32 (0x100), **1801b7d80**: `if (curtime > this+0x14 + 0.5)`
  (0x18178057c: 0x3f000000) run **1801d9e50**. Also called from 180923fb0 and 180957e50 (round events: not read).
- **1801d9e50**: `this+0x14 = curtime` (gpGlobals +0x30); for every pawn (the entity list walk 180c86720 /
  180c8ace0 / 180c86b40) passing vfn 0x558 and vfn 0xca8, whose controller's +0x514 (the connection state) is 0 or 3:
  **1801da220**(pawn, pawn+0x14a0, [pawn+0x14b8]); then every hostage (FUN_18093eba0), `item_cutters`, `planted_c4`,
  `weapon_c4` by class name, each with its own fields (above).
- **1801da220**(entity, state, rules): rules 0 does nothing. The observer team asked for: rules & 1: 0 when
  `mp_teammates_are_enemies` (bool, registered 1800a3500, default 0) is set, else `(team != 3) + 2` (the other team);
  else & 2: 3 (CT); else & 4: 2 (T). The point: EyePosition (vfn 0x5e8) when vfn 0x558 says so, else
  WorldSpaceCenter (vfn 0x2c8). Runs the observer walk (**1801b9fd0**: each controller slot, +0x514 0 or 3, a pawn
  (180b55040) passing vfn 0x558) with the query; then `m_bSpotted` written only when it changed (1801ce5b0 notes the
  change), the mask rebuilt (1801c16d0 clears it, then each spotter slot < 64 ORed in through 1801d6920).
- **1801bd100**(query, observer pawn): the query's team (query +0x14) is 0 or the observer's (+0x344); vfn 0x550;
  the controller valid (180927cb0 / 18017e2d0 on pawn +0xd38); eye and forward from **180b4fa70**; d = point - eye;
  length `sqrtss((z*z + y*y) + x*x)` (VectorNormalize 1814738b0 when under 1e-17 or over 1e17, 0 at exactly 0);
  dir = d x (1 / length); `dot = ((fz*dz) + (fy*dy)) + (fx*dx)` (1801bd2a3..2c8); dot < 0 fails.
  - `radarvismethod` 1 (default): `half = FOV / 2` (int, signed shift: cdq / sub / sar); `cone = cosf(half x
    3.1415 / 180)` (0x18178fe08 0x40490e56 = 3.1414999961853027, 0x18178fe1c 180.0, the import at [rip+0x15addf9]);
    `v = powf(length / radarvisdistance, radarvispow)` (import [rip+0x15addbf]); `thr = cone > v ? cone :
    minss(radarvismaxdot, v)`; fails unless `dot > thr` (seta). FOV: **180a7a350** on the camera services
    (pawn +0xb48): `m_iFOV` (+0x178), 0 -> (int)vfn 0xe8; while `m_flFOVRate` (+0x184) != 0 and the time since
    `m_flFOVTime` (1801f95b0 on +0x180) is below the rate and `m_iFOVStart` (+0x17c) <= that FOV: the start.
  - `radarvismethod` 0: passes when dot > 0.995 (0x18178fdf0), or > 0.98 (0x18178fdec) within 900 u (0x18178fe28),
    or > 0.8 (0x18178fde4) within 250 u (0x18178fe20).
  - Line of sight, **1801d7460**: a trace filter (vtable 0x18178c240) with interacts-with 0x800180041, collision group
    3, flags (x & 0xc9) | 0x49, 0x0f00ffff (detail layers 0xffff, target layer 0, object set 0xf), the observer and the
    target ignored (1801d6c60); the ray (180c2f3c0) from the eye to the point must reach it (fraction == 1.0), and
    **18032a570** (DAT_181fa5e10, the smoke volumes) must say the line isn't through smoke.
  - **180a7a4c0**(camera services, target): the distance from the services' pawn's eye (vfn 0x5e8) to the target's
    WorldSpaceCenter (vfn 0x2c8), through **180a7a3e0** (the fog's opacity at that distance): must be < 0.9
    (0x18178fde8 0x3f666666).
  - Spotted: query +0x18 = 1, the observer's slot (180b55410) appended to the query's vector (+0x20 count, +0x28 data).
- The cvars (each read through its object's pointer + 0x58), registrations 18004d830..18004da40, flags 0x4000:
  `radarvismethod` int **1** ("0 for traditional method, 1 for more realistic method"), `radarvisdistance` float
  **1000.0**, `radarvismaxdot` float **0.996**, `radarvispow` float **0.4**.

## The client's radar (client_20261015.dll 180dde830, CCSGO_HudRadar's per-player update)

A record of 0x200 bytes a player slot from radar +0x398 (count +0x380). For each slot with a pawn: whether it is an
enemy, **1808d9290** (another slot whose team (+999 on the controller) differs from yours, or anyone with
`mp_teammates_are_enemies`; an observer-target branch through 1809f6b30 not read); a teammate is shown; an enemy is
shown when your slot's bit is set in its `m_bSpottedByMask` (+0x1e8c..), or, unless `mp_teammates_are_enemies`
(DAT_1824bcf90), when its `m_bSpotted` (pawn +0x3d1 through 1813ce910) is set. Then, for one not seen by a teammate
(180dd8b00), within 1600 u (2D) of your eye and with a clear line (180c8a7d0: a trace's fraction >= 1.0 from your
eye to the pawn's feet + 56): **not** shown that way (unread why: TODO). The radar's own mask (+0x1d3e4) shows a
slot regardless. The 0.25 s timers (+0x134 / +0x13c, flags +0x1fd) fade one in and out.

## Transmit (not ported: every pose is sent; docs/NETWORK.md "Visibility")

- `sv_shared_team_pvs` (bool, 1800f0ec0, default **0**): "PVS is shared between teams".
- `sv_force_transmit_ents` (bool, 1800f0b60.., default **0**): "Will transmit all entities to client, regardless of
  PVS conditions (will still skip based on transmit flags, however)".
- Also registered: `sv_pvs_max_distance`, `sv_use_pvs_cache`, `sv_pvs_cache_query_inflate_amount`, `sv_pvs_random`,
  `sv_hide_ent_in_pvs`, `sv_parallel_checktransmit`; no `sv_occlude_players` string in server.dll (no server-side
  occlusion culling of players).

**Unread (TODO):** CCSPlayerPawn's transmit state (whether a teammate's or a spotted enemy's pawn is sent outside your
PVS, and so where the radar's positions of those come from); the defaults of the other PVS cvars (cvardump took a
neighbour's help for `sv_pvs_max_distance`); 180a7a3e0's fog opacity; 18032a570's smoke test; which game-system hook
slot 32 is; the two forced updates' callers; the 1600 u exception above, the fade timers, the death mark; whether the
trace meets other players' bodies (mask 0x800180041 against the pawns' layers).
