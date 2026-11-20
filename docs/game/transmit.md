# CheckTransmit: which entities a client is sent

server_20261105, client_20261015 (what the HUD shows of others).

## Functions

| Address | Module | What |
|---|---|---|
| 180dd7150 | server | CSource2GameEntities::CheckTransmit (check infos param_2, count param_3, entity list param_5 (ushort indices), count param_8) |
| 180cbc9a0 | server | the controller from the info's +0x240 slot |
| 180de7410 | server | finds an earlier client with the same key |
| 180c10aa0 / 1803d7630 | server | an entity's list (cleared from other clients' bits under sv_remove_ent_from_pvs) |
| 180de3590 | server | one client's pass (this, record, entity count, entity pointers, entity indices, force) |
| 180b51df0 | server | on the controller (zeroed when this+0x848 is clear) |
| 180187ee0 / 180186fd0 / 180188050 | server | three bit vectors (always / don't-send / PVS-check style sets, names unread) |
| 180de3df0 | server | one entity for one client (this, index, record, entity, areas, ..., force-or-controller-bit) |
| 180ddd780 | server | merges the parents' bits (0x200 words) |
| 18018ed80 | server | IsInPVS (identity, record) |
| FUN_1803d9790 | server | walks an entity's move parents |
| FUN_180180e10 | server | rebuilds the component's cluster list from the box through the world's cell table |
| 18018f470 | server | another spawn group's PVS test (portals between worlds; unread) |
| 180b48900 | server | CCSPlayerController vfn 0x7e0: fills the client's 0x50-byte record |
| FUN_180cfa3e0 | server | the controller's pawn |
| 180b524d0 | server | controller vfn 0x7e8: the record's origin: m_hPawn (+0x4e0) vfn 0x600 = 18014d450 -> vfn 0x5e8 (read as EyePosition) |
| 18014d450 | server | pawn vfn 0x600 |
| 18024b840 | server | CCSPlayerPawn ShouldTransmit (vfn 0x2f8) |
| 180d11e00 | server | the base ShouldTransmit |
| 180b5d660 | server | the pawn's controller observed by the client's slot |
| FUN_1801852d0 | server | the component's own state bits |
| 180157430 | server | CCSPlayerPawn vfn 0x770: bare `ret` |
| 180d10cd0 | server | CCSPlayerPawn SetTransmit (vfn 0x300) |
| 180c868d0 | server | the active weapon |
| 180d1b7c0 | server | WorldSpaceSurroundingBounds |
| 180cebd90 | server | recompute surrounding bounds: switch on m_nSurroundType |
| 180ceb430 -> 180cea8c0 | server | type 0: the collision box |
| 180cec040 | server | solid type 6 with a physics object |
| 180ceaf30 | server | best of collision and physics (type 1; type 7 without the physics) |
| 180b4afa0 | server | hitboxes (vfn 0x1c0) |
| 180cec1d0 | server | CCSPlayerPawn vfn 0x2d0: bare `ret` |
| 180ceba70 | server | rotation-expanded |
| 1814759f0 | server | the box rotated |
| 180cebbb0 | server | surround type 8 |
| 180380e50 | server | `m_bTransmitAlways` / `transmit_always` keyvalue |
| 180fb1300 | client | GameStateAPI.GetPlayerStatsJSO's stats object (name at 0x181cf25d8) |
| 180fb0a40 | client | "money" key (0x181cf97a0): the xuid to a slot, then 180fb0940 |
| 180fb0940 | client | (slot): money or a negative code |
| 180889880 | client | local controller's team |
| 18089c9e0 | client | (local controller): a spectator / caster test |
| 180fd06c0 | client | demo / GOTV (vfn 0x150 on DAT_182560ed0, or DAT_1825603a0) |
| 180eba820 | client | CCSGO_HudTeamCounter: fills an avatar's record (param_2) from the player (param_3) |
| 180ecc1f0 | client | applies the avatar record |
| 180ce2420 | client | omniscient test |
| 1808d9430, 180769bb0 | client | the local observer pawn branch |
| 180c7c160 | client | the local pawn |
| 1808d9290 | client | IsOtherEnemy (local pawn, row) |

Registrations: `sv_shared_team_pvs` 1800f0ec0 (default 0, [spotting.md](spotting.md)), `sv_force_transmit_ents` 1800f0b50,
`check_transmit_dump_ents` 1800eeae0, `sv_parallel_checktransmit` 1800f0d60 ("1 ... listen servers, 2 ... dedicated servers"),
`sv_max_distance_transmit_footsteps` 1800c9b80, "Max number of entities to transmit to player" 1800cdd10 (name not read),
`mp_forcecamera` 1800d9a00.

## Fields

| Offset | Field |
|---|---|
| info +0x20 / +0x28 | area id count / list (up to 4) |
| info +0x240 | the client's slot |
| info +0x244 | clear: may share a result |
| record (0x50 bytes) +0 | the info |
| record +8 | the controller (the client's own entity) |
| record +0x10 | the origin (vfn 0x7e8) |
| record +0x20 | the controller's pawn |
| record +0x28 | the observer target; also the sorted spawn-group list (+0x28 / +0x20) |
| record +0x30 / +0x34 | the team (+0x344); +0x34 the key clients are grouped by |
| record +0x39 | the controller's +0x510 byte (GOTV-ish) |
| record +0x3a | the controller's +0x5b4 |
| record +0x3b | observing (observer services +0xb28 mode != 0) |
| record +0x3c | a PVS present / the spawn group |
| record +0x40 | the PVS bits; +0x38 0: no clusters |
| record +0x40 / +0x48 / +0x4c / +0x4e | (CheckTransmit's record) the info / the client's index / earlier same-key client / copy mark |
| param_1 +0x848 | the bool cvar at DAT_1821b9878 |
| param_1 +0x30 | curtime less the float cvar at DAT_1821b9890 |
| this+0x34 | a set whose failing entities walk their move parents |
| controller +2000 (0x7d0) | bit vector |
| entity +0x10 -> +0x1b8 | the networkable's transmit-state word: bit 8 always, bit 4 PVS check, bit 0x10 don't send |
| networkable +0x180 | state: bit 8 never, bit 4, bit 0x10 PVS check |
| entity +0x50 | spawn group |
| entity +0x278 / +0x280 | per-client "sent recently" bits / time |
| CNetworkTransmitComponent +0x190 | its entity |
| component +0x186 | clusters dirty |
| component +0x1a0 | spawn group |
| component +0x28 / +0x2c | (word index, mask) pair count / pairs |
| entity +0x60 | vfn 0x228 radius |
| entity +0x168 / +0x174 | its box (with sv_use_pvs_cache) |
| CCSPlayerPawn +0x334 | always transmit |
| pawn +0x411 | never (with record +0x3a) |
| pawn +0xc98 | m_hController |
| pawn +0xb10 | weapon services: m_hMyWeapons +0x48 / +0x50 |
| gamerules +0x4b0 | the GOTV-ish client's side |
| collision +0x40 / +0x4c | m_vecMins / m_vecMaxs |
| collision +0x5a flag 2 / +0x5c | widened by the trigger bloat (half on top) |
| collision +0x5d | m_nSurroundType |
| collision +0x5e | m_CollisionGroup |
| collision +0x64 / +0x70 | m_vecSpecifiedSurroundingMins / Maxs (scaled) |
| collision +0x7c / +0x88 | m_vecSurroundingMaxs / Mins |
| entity +0x414 bit 14 | surrounding bounds dirty |
| client controller +0x818 -> +0x40 | m_pInGameMoneyServices -> m_iAccount |
| client controller +999 | team |
| client controller +0x888, +0x6f0, +0x790 | spectator / caster flags |
| client identity +0x30 bit 7 | dormant |
| avatar record +0xc / +0x10 / +0x28 / +0x29 | health / armor? / cVar4 / cVar5 (unread) |

## Constants

| Value | What |
|---|---|
| 0x1819943a0 | job string "CSource2GameEntities::CheckTransmit(), ...gameinterface.cpp:3339" |
| 0x181f20b40 | RTTI `CParallelLambdaJob<lambda_2>@CheckTransmit@CSource2GameEntities` |
| DAT_1821b99c8 | bool: same-key clients share one result (sv_shared_team_pvs's block, 0x1821b99c0) |
| DAT_1821b9878 | bool: "sent recently" (name not read) |
| DAT_1821b9890 | float: its window (name not read) |
| DAT_1821b9848 / DAT_181e33c30 | int cvar / flag allowing the thread pool (2+ records) |
| DAT_1821b99d8 | sv_remove_ent_from_pvs (0x1821b99d0): the "transmit only to" cvar |
| DAT_1821b9888 | bool: copies the whole 0x800-byte transmit vector from the second set (sv_force_transmit_ents?, unconfirmed) |
| 0x181f48428 | `sv_pvs_max_distance` (float; default not decoded: taken as 0) |
| 0x181f48408 | `sv_use_pvs_cache` (default 0) |
| 0x181f48418 | `sv_pvs_cache_query_inflate_amount` |
| 0x1821b99c0 | `sv_shared_team_pvs` (default 0) |
| 0x1821b9850 | `sv_hide_ent_in_pvs` |
| 0x181f49c60 / 0x181f49c70 | `sv_pvs_entity` / `sv_pvs_random` (debug) |
| 0x181794998 | CCSPlayerPawn vtable |
| ShouldTransmit 4 / 8 / 0x10 | always / never / PVS |
| -1 / -2 / -3 / -4 / -5 | money: out of range / not in game / no controller / no local controller / hidden |
| DAT_1824bc4f0 +0x58 | bool in the spectator test |
| DAT_1825603a0 | caster / demo flag |
| DAT_18257b368 +0x58 | bool: omniscient |
| DAT_1824bcf90 +0x58 | mp_teammates_are_enemies (client) |
| DAT_1825510d8 +0x58 | int cvar (name not read; taken as mp_forcecamera) |
| 100 / > 40 | healthbartype Full / Normal, else Red |

## CheckTransmit (180dd7150)

1. Per client: the controller; its vfn 0x7e0 fills the record. With DAT_1821b99c8 set and info +0x244 clear, same-key clients share one result.
2. Serial, or the thread pool (2+ records, DAT_1821b9848 allows, DAT_181e33c30 set: sv_parallel_checktransmit).
3. After: DAT_1821b99d8 non-zero: an entity's list is cleared from the transmit bits of every client whose controller isn't that entity.

## One client (180de3590)

1. Areas; 180b51df0; the three sets; the controller's bit vector. DAT_1821b9888 set: the transmit vector copied from the second set first.
2. Each entity: 180de3df0, else the sets inline (an entity in the third set is sent unless info +0x39 / +0x3b, force, the controller's bit and 18018ed80(entity +0x30, record) all say no).
3. Parents' bits merged (180ddd780). check_transmit_dump_ents prints the state word at the end ("%s (-)" the other case).

## One entity (180de3df0)

1. Skipped if already marked. Networkable +0x180 bit 8: never. Another spawn group than the client's four: skipped.
2. Bit 4, or no state bits and vfn 0x2f8 ShouldTransmit(info) & 4: vfn 0x300 SetTransmit(info, always = 1).
3. Else only with bit 0x10: force -> SetTransmit(0); with this+0x848 and a budget (param_6 > 0), the "sent recently" bit (time against this+0x30) keeps it sent (always = 1).
4. IsInPVS true -> SetTransmit(0); an entity in this+0x34's set that fails walks its move parents: a parent sent or in the PVS sends it (always = 1).

## IsInPVS (18018ed80)

1. True for the client's own entity (record +8), record +0x39, or no PVS (record +0x3c clear).
2. sv_pvs_max_distance > 0: false past it, from the record's origin to the entity's origin plus its radius, or with sv_use_pvs_cache to its box.
3. Clusters rebuilt when dirty. Client's spawn group: no clusters sees everything, else any (word, mask) pair set in the PVS bits. Another spawn group: 18018f470.

## CCSPlayerPawn transmit

- ShouldTransmit 18024b840: always when +0x334; else 180d11e00: always for the client's own pawn (record +8 is the pawn's m_hController) or the pawn's controller observed by the client's slot (180b5d660, info +0x240), or a GOTV-ish client (record +0x39) of gamerules +0x4b0's side; never with record +0x3a and pawn +0x411, or no networkable; the component's own state bits; then the record's pawn's vfn 0x770; else PVS.
- SetTransmit 180d10cd0: the base's, then all the pawn's weapons for its own or observing client, else only the active weapon.

## Surrounding bounds (180d1b7c0)

m_vecSurroundingMins / Maxs over the origin, recomputed when +0x414 bit 14 is set, by 180cebd90:

| m_nSurroundType | Bounds |
|---|---|
| 0 | collision box (180ceb430; flag 2 widened by the bloat; solid type 6 with physics -> 180cec040) |
| 1 | best of collision and physics (180ceaf30) |
| 2 | hitboxes (vfn 0x1c0 -> 180b4afa0) |
| 3 | specified (+0x64 / +0x70 scaled) |
| 4 | the entity's vfn 0x2d0 |
| 5 | rotation-expanded (180ceba70) |
| 6 | the box rotated (1814759f0) |
| 7 | 180ceaf30 without the physics |
| 8 | 180cebbb0 |

## What the HUD shows of others (client)

- Scoreboard money (180fb0940): m_iAccount when the row's team equals the local controller's (180889880), or 18089c9e0(local) is set (team 1 a spectator, unless +0x888 and DAT_1824bc4f0 +0x58; or the caster flag: +0x6f0, or DAT_1825603a0 when +0x790 is set), or 180fd06c0. Else the negative codes; scoreboard.ts hides the label below 0.
- Top bar avatar health (180eba820 -> 180ecc1f0): +0xc = the player's (+4) only when 180ce2420 says so (DAT_18257b368 +0x58; the caster flag; or the local observer pawn through 1808d9430 and 180769bb0), or: no omniscience, the local pawn and the row's pawn exist, the row's isn't dormant, and IsOtherEnemy is false or the local pawn is dead (vfn 0x4e8) with DAT_1825510d8 +0x58 == 0. Else 0: 180ecc1f0 hides the +0xc panel (`0 < health`); "healthbartype" Full (100), Normal (> 40) or Red. The same flags gate +0x10, +0x28, +0x29.
- Pings ([ping.md](ping.md)): the pinger's team only.

## Unread

- The pawn's world bounds (+0x168 / +0x174: hull or hitboxes), its m_nSurroundType, and FUN_180180e10's cell walk.
- The cvars at DAT_1821b9878, DAT_1821b9890, DAT_1821b9888 (names; sv_shared_team_pvs = 0x1821b99c8's block, sv_remove_ent_from_pvs = 0x1821b99d8's); sv_pvs_max_distance's default; 180b5d660 (observed by whom).
- Which entity DAT_1821b99d8's clear concerns (likely a debug "transmit only to").
- Where the radar gets a dormant spotted enemy and a dormant teammate ([spotting.md](spotting.md)).
- 180ce2420's observer branch (1808d9430, 180769bb0); 180eba820's other gated fields; the int cvar at DAT_1825510d8.
