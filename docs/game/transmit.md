# CheckTransmit: which entities a client is sent (read 2026-11-16, 2026-11-18)

Ghidra ReVa on `server_20261105.dll` (the "anticheat" session; read only). For docs/ANTICHEAT.md 3a.

## Found

- **CSource2GameEntities::CheckTransmit, 180dd7150** (its job string "CSource2GameEntities::CheckTransmit(),
  ...gameinterface.cpp:3339" at 0x1819943a0; the parallel lambda's RTTI
  `CParallelLambdaJob<lambda_2>@CheckTransmit@CSource2GameEntities` at 0x181f20b40). Arguments: the clients' check
  infos (param_2, an array of CCheckTransmitInfo pointers), their count (param_3), the entity list (param_5, ushort
  indices) and its count (param_8).
  - Per client: the controller (180cbc9a0 on the info's +0x240 slot); **its vfn 0x7e0(controller, record, info)**
    fills a 0x50-byte record (+0x40 the info, +0x48 the client's index, +0x34 a key the clients are grouped by:
    180de7410 finds an earlier client with the same key, +0x4c, and +0x4e marks it as a copy). With the bool cvar at
    DAT_1821b99c8 set (not named here) and info +0x244 clear, clients that share a key share one result.
  - `*(param_1 + 0x848)` = the bool cvar at DAT_1821b9878; `*(param_1 + 0x30)` = curtime less the float cvar at
    DAT_1821b9890 (not named here).
  - Serial, or on the thread pool when there are 2+ records, the int cvar DAT_1821b9848 allows it and the flag
    DAT_181e33c30 is set (sv_parallel_checktransmit: "1 ... listen servers, 2 ... dedicated servers", registered at
    1800f0d60).
  - After: with the int cvar DAT_1821b99d8 non-zero, an entity's list (180c10aa0 / 1803d7630) is cleared from the
    transmit bits of every client whose controller isn't that entity (unread which entity: likely a debug
    "transmit only to" cvar).
- **180de3590(this, record, entity count, entity pointers, entity indices, force)**, one client's pass: up to 4 area
  ids from the info (+0x20 count, +0x28 list); 180b51df0 on the controller (zeroed when this+0x848 is clear); three
  bit vectors from 180187ee0 / 180186fd0 / 180188050 (always / don't-send / PVS-check style sets, names unread); the
  controller's +2000 (0x7d0) bit vector. With the bool cvar DAT_1821b9888 set (sv_force_transmit_ents?, unconfirmed)
  the whole 0x800-byte transmit vector is copied from the second set first. For each entity: **180de3df0(this,
  index, record, entity, areas, ..., force-or-controller-bit)** decides, else the always / never / PVS-check sets as
  read inline (an entity in the third set is sent unless the info's +0x39 / +0x3b flags, force, the controller's bit
  and 18018ed80(entity +0x30, record) all say no). Then the parents' bits are merged (180ddd780, 0x200 words).
- **The networkable's transmit-state word** (entity +0x10 -> +0x1b8, printed by the check_transmit_dump_ents debug
  path at 180de3590's end): bit 8 always, bit 4 "PVS check", bit 0x10 don't send (the dump's "%s (-)" names the
  other case).
- Cvars seen: `sv_shared_team_pvs` (1800f0ec0, default 0, docs/game/spotting.md), `sv_force_transmit_ents`
  (1800f0b50), `check_transmit_dump_ents` (1800eeae0), `sv_parallel_checktransmit` (1800f0d60),
  `sv_max_distance_transmit_footsteps` (1800c9b80), "Max number of entities to transmit to player" (1800cdd10, name not
  read), `mp_forcecamera` (1800d9a00), `m_bTransmitAlways` / `transmit_always` (an entity keyvalue, 180380e50).

## The per-entity test and the player pawn (read 2026-11-18 for docs/ANTICHEAT.md 11a P1)

- **180de3df0** (one entity for one client): skipped if already marked; the networkable's +0x180 state: bit 8
  never; an entity in another spawn group than the client's four (+0x50 against param_5, then a sorted list at
  record +0x28 / +0x20) skipped; bit 4, or no state bits and **vfn 0x2f8 ShouldTransmit**(info) & 4: **vfn 0x300
  SetTransmit**(info, always = 1). Else only with bit 0x10 (PVS check): force -> SetTransmit(0); with the bool at
  this+0x848 (DAT_1821b9878, name not read) and a budget (param_6 > 0), a per-client "sent recently" bit on the
  entity (+0x278 bits, a time at +0x280 against this+0x30 = curtime less DAT_1821b9890) keeps it sent (always = 1).
  Then **IsInPVS 18018ed80**(identity, record) true -> SetTransmit(0); an entity in this+0x34's set that fails walks
  its move parents (FUN_1803d9790): a parent sent or in the PVS sends it (always = 1).
- **IsInPVS 18018ed80** (CNetworkTransmitComponent +0x190 = its entity): true for the client's own entity (record
  +8), record +0x39, or no PVS (record +0x3c clear). sv_pvs_entity / sv_pvs_random (debug). **sv_pvs_max_distance**
  (0x181f48428, a float; > 0): false past it, from the record's origin (+0x10) to the entity's origin plus its vfn
  0x228 radius (+0x60), or with **sv_use_pvs_cache** (0x181f48408, default 0) to its box (+0x168 / +0x174). Then the
  cluster test: the component's cluster list rebuilt when dirty (+0x186 -> FUN_180180e10 from the box through the
  world's cell table); in the client's spawn group (+0x1a0 0 or the record's +0x3c): a PVS without clusters (+0x38 0)
  sees everything, else any of the entity's (word index, mask) pairs (+0x28 count, +0x2c pairs) set in the PVS bits
  (+0x40). Another spawn group goes through 18018f470 (portals between worlds; unread).
- **The client's record** (CCSPlayerController vfn 0x7e0 = **180b48900**): +0 the info, +8 the controller, +0x39 the
  controller's +0x510 byte, +0x20 its pawn (FUN_180cfa3e0), +0x30 / +0x34 the team (+0x344: the key clients share a
  result by under **sv_shared_team_pvs**, 0x1821b99c0, default 0), +0x3a the controller's +0x5b4, +0x3b observing
  (the pawn's observer services +0xb28 mode != 0) and +0x28 the observer target, +0x3c a PVS present, **+0x10 the
  origin**: vfn 0x7e8 = **180b524d0**, the controller's m_hPawn (+0x4e0) vfn 0x600 = 18014d450 -> vfn 0x5e8 (read as
  EyePosition).
- **CCSPlayerPawn** (vtable 0x181794998): ShouldTransmit (0x2f8) = **18024b840**: always (4) when +0x334, else
  **180d11e00**: always for the client's own pawn (record +8 is the pawn's m_hController, +0xc98) or the pawn's
  controller observed by the client's slot (180b5d660, record info +0x240), or a GOTV-ish client (record +0x39) of
  the gamerules' +0x4b0 side; never (8) with record +0x3a and the pawn's +0x411, or no networkable; the component's
  own state bits (FUN_1801852d0); then the record's pawn's vfn 0x770 (a bare `ret` on CCSPlayerPawn, 180157430); else
  **PVS (0x10)**. SetTransmit (0x300) = **180d10cd0**: the base's, then the pawn's weapons (weapon services +0xb10:
  m_hMyWeapons +0x48 / +0x50) for its own or observing client, else only the active weapon (180c868d0).
- Cvars read: `sv_pvs_max_distance` 0x181f48428, `sv_use_pvs_cache` 0x181f48408, `sv_pvs_cache_query_inflate_amount`
  0x181f48418, `sv_shared_team_pvs` 0x1821b99c0, `sv_hide_ent_in_pvs` 0x1821b9850, `sv_remove_ent_from_pvs`
  0x1821b99d0 (the "transmit only to" cvar above), `sv_pvs_entity` 0x181f49c60, `sv_pvs_random` 0x181f49c70
  (cvardump.py; sv_pvs_max_distance's default not decoded: taken as 0).

- **The surrounding bounds** IsInPVS's clusters come from (FUN_180180e10 via the entity's vfn 0x228, its collision
  property): **WorldSpaceSurroundingBounds 180d1b7c0**: m_vecSurroundingMins (+0x88) / Maxs (+0x7c) over the origin,
  recomputed when the entity's +0x414 bit 14 is set by **180cebd90**, a switch on **m_nSurroundType (+0x5d)**: 0 the
  collision box (**180ceb430** -> 180cea8c0 of m_vecMins +0x40 / m_vecMaxs +0x4c; with flag 2 at +0x5a widened by the
  trigger bloat +0x5c, half of it on top; solid type 6 with a physics object goes to 180cec040), 1 the best of
  collision and physics (180ceaf30), 2 the hitboxes (vfn 0x1c0 -> 180b4afa0), 3 specified (+0x64 / +0x70 scaled), 4
  the entity's vfn 0x2d0 (CCSPlayerPawn's: a bare `ret`, 180cec1d0), 5 rotation-expanded (180ceba70), 6 the box
  rotated (1814759f0), 7 180ceaf30 without the physics, 8 180cebbb0. Schema: m_nSurroundType +0x5d,
  m_vecSpecifiedSurroundingMins +0x64, m_vecSurroundingMins +0x88, m_CollisionGroup +0x5e. The pawn's own type: unread.

Ours: server/cs2web/core/transmit.js (the team modes): the pawn's hull box (type 0's collision box) against the PVS
of the viewer's eye cell.

## What the HUD shows of others (client_20261015, read 2026-11-18 for docs/ANTICHEAT.md 11 P0)

What CS2's client shows a player of the other players, so the server sends no more (server/cs2web/core/board-view.js,
event-recipients.js):

- **Scoreboard money**: GameStateAPI.GetPlayerStatsJSO (its name at 0x181cf25d8; the stats object built by
  **180fb1300**, its "money" key 0x181cf97a0 set from **180fb0a40**: the xuid to a slot, then **180fb0940**(slot)).
  180fb0940 returns the controller's `m_pInGameMoneyServices` (+0x818) -> `m_iAccount` (+0x40) when the row's team
  (controller +999) equals the local controller's (180889880), or **18089c9e0**(local controller) is set (team 1 a
  spectator, unless +0x888 and the bool at DAT_1824bc4f0 +0x58; or the caster flag: +0x6f0, or DAT_1825603a0 when
  +0x790 is set), or **180fd06c0** (vfn 0x150 on DAT_182560ed0, a demo / GOTV, or DAT_1825603a0). Else -5 (-1 out of
  range, -2 not in game, -3 no controller, -4 no local controller). scoreboard.ts hides the label below 0.
- **The top bar's avatar health** (CCSGO_HudTeamCounter): **180eba820** fills the avatar's record (param_2) from the
  player's (param_3) and calls **180ecc1f0**. Health (+0xc) = the player's (+4) only when the omniscient test
  **180ce2420** says so (the bool at DAT_18257b368 +0x58; the caster flag as above; or the local observer pawn
  through 1808d9430 and 180769bb0), or: no omniscience, the local pawn (180c7c160) and the row's pawn exist, the row's
  isn't dormant (its identity +0x30 bit 7), and **1808d9290 IsOtherEnemy**(local pawn, row) is false (another team,
  or mp_teammates_are_enemies at DAT_1824bcf90 +0x58) or the local pawn is dead (vfn 0x4e8) with the int at
  DAT_1825510d8 +0x58 equal to 0 (name not read: board-view.js takes it as mp_forcecamera). Else 0, and 180ecc1f0
  hides the avatar's +0xc panel (`0 < health`) and gives "healthbartype" Full (100), Normal (> 40) or Red.
  The same flags gate +0x10 (armor?), +0x28 and +0x29 (cVar4 / cVar5: unread).
- **Pings** (docs/game/ping.md): the pinger's team only; **hints / rings**: their one player (client/core/game.js).

## Unread (TODO)

- The pawn's world bounds (+0x168 / +0x174: hull or hitboxes) and FUN_180180e10's cell walk; the "sent recently"
  cvar at DAT_1821b9878 and its window DAT_1821b9890; sv_pvs_max_distance's default; 180b5d660 (observed by whom).
- Where CS2's radar gets a dormant spotted enemy and a dormant teammate (spotting.md).
- 180ce2420's observer branch (1808d9430, 180769bb0) and what 180eba820's other gated fields are; the int cvar at
  DAT_1825510d8 (cvardump.py on its registration).
- The names of the cvars at DAT_1821b9878, DAT_1821b9890, DAT_1821b9888 (sv_shared_team_pvs = 0x1821b99c8's block,
  sv_remove_ent_from_pvs = 0x1821b99d8's: read above).
