# Spawn spots (team matches)

server_20261105.dll, read 2026-11-16 (ReVa; tools/re schema / rtti / vslot / vtowner / fieldwrites / impat). Ported in
web/server/cs2web/core/spawn-select.js (game.js spawn for every mode but ZE; game.js newRound at each round's start,
the points' inputs through the engine's 'spawnpoint' event) and spawn-config.js (RestartRound's configuration, run by
comp.js roundStart before its mass spawn, which it orders); web/src/world/entities/classes/spawn-points.js keeps
m_bEnabled; web/src/cs2web/world/round-carry.js carries it over the restart. Tests: web/server/cs2web/core/spawn-test.mjs,
web/server/cs2web/modes/team/official-maps-test.mjs (the Wingman sets).

## CSpawnPoint fields

| Offset | What |
|---|---|
| +0x4a8 | m_iPriority (the "priority" key; lower is handed out first) |
| +0x4ac | m_bEnabled (the "enabled" key; CS2's maps write true / false; the FGD's default true) |

Classes (bases.py): CInfoPlayerTerrorist (vtable 0x1818c6d98), CInfoPlayerCounterterrorist (0x1818c7510) and
CInfoDeathmatchSpawn all derive SpawnPoint (0x1818c4520) <- CServerOnlyPointEntity; CInfoPlayerStart is a plain
CPointEntity. SpawnPoint's vfn 0x430 (IsSpawnPointValid's "its own CanSpawn") is 0x180154270: `return 1`.

CS2's maps switch their .standard and .2v2 sets from the Pulse GameModeCheck (de_inferno, de_nuke, de_overpass,
de_vertigo: docs/game/pulse.md).

**Preserved over the round restart**: CleanUpMap's preserve list (0x181e04220, char* table) names
info_player_counterterrorist (0x181e042e0), info_player_terrorist (+8), info_enemy_terrorist_spawn,
info_deathmatch_spawn, info_map_parameters, ... so the same spawn point entities, their m_bEnabled and the
gamerules' handle lists live through every round of a map. The port's round is a fresh engine with the same entity
ids: the lists keep ids, round-carry.js carries m_bEnabled (a SetDisabled mid-round holds next round).

## SpawnPoint's inputs (SpawnPoint_API)

The entity API's records (0x50 bytes: +0x00 "SpawnPoint_API::<Input>", +0x08 the display name, +0x48 the handler;
tools/re/game/inputs.py's layout), from 0x181e06fe0:

| Input | Record | Handler | Does |
|---|---|---|---|
| SetEnabled ("Set Enabled") | 0x181e06fe0 | 0x1808dac10 | +0x4ac = 1; when gamerules (DAT_1821ba1c0) exist and it was 0: 0x1809563e0 |
| SetDisabled ("Set Disabled") | 0x181e07030 | 0x1808dada0 | +0x4ac = 0; when gamerules exist and it was 1: 0x1809563e0 |
| ToggleEnabled ("Toggle Enabled") | 0x181e07080 | 0x1808daf30 | +0x4ac = !+0x4ac; when gamerules exist: 0x1809563e0, always |

The rebuild is the ordered lists' only (the base lists stay): its shuffle draws from tier0's stream. The port's map
logic (spawn-points.js) runs on the server and every replica alike and only emits 'spawnpoint' (entity, rebuild); the
server's SpawnSelect listens (game.js attachEngine) and rebuilds; a replica has no listener. Nothing replicated changes.

## The lists (gamerules)

- **0x18090d240** (an entity's spawn): info_player_terrorist / info_enemy_terrorist_spawn into the T list (+0xf80
  count, +0xf88 handles), info_player_counterterrorist into the CT list (+0xf68 / +0xf70); info_deathmatch_spawn isn't
  listed. Then 0x1809563e0. (The map's points spawn before 0x180916810 first runs, whose GenerateSpawnPointLists
  clears the counts and lists them again; a point spawned later, by a template, is appended unchecked.)
- **0x180916810** (the lists' lazy init): returns at once when gamerules +0xd84 is set; else the team sizes (+0xe94 /
  +0xe98: mp_retake_t_count / mp_retake_ct_count in Retakes, else engine vfn 0x160 over the max players), +0x140 from
  a cvar, **GenerateSpawnPointLists**, the Retakes / info_player_logo bits, then +0xd84 = 1. Its callers: the Think
  (CCSGameRules vtable 0x1818c5450 slot 50 = 0x1809669f0, line ~490: every frame), TeamFull 0x180965080 (the join-team
  checks: 18095fce0, 1802d5940, 1802de9b0, 180944090), the team balance 0x180910fb0 (from 180954a60), and slot 8 =
  0x1809543d0, a spawn group's load (a map name that isn't "<empty>", no landmark, +0x14 == 0, a known spawn group:
  1805c4090), which first clears +0xd84. +0xd84's only writers (fieldwrites): the constructor 0x1809058c0 (0),
  0x180916810 (1), 0x1809543d0 (0). So **the lists are made once per map**, at its load (the first Think after it,
  before any player is in), never at a round restart.
- **GenerateSpawnPointLists 0x180925a50**: +0xf80 and +0xf68 = 0; for each class in turn FindEntityByClassname
  (0x180bfc410) walks the points; **IsSpawnPointValid(rules, point, null)** (0x18093e710 with no pawn: +0xf98 is clear
  then, vfn 0x430 true, so the standing hull test at the point with a null pawn's filter; nobody is in at a map's load)
  false: "Invalid terrorist spawnpoint at (%.1f,%.1f,%.1f)" (0x1818ca4d8; the CT's 0x1818ca510) and skipped; else its
  handle appended. Each list with more than one entry is V_qsort'ed with 0x180963890 (`a.priority - b.priority`, a
  stale handle before a live one). Then 0x1809563e0. Port: generate() at the map's first round, the hull against the
  world and the round's solids (spawn-select.js hullFree), V_qsort as lib/msvc-qsort.js.
- **0x1809563e0**: the enabled spawn points (+0x4ac) of each base list (a stale handle skipped) into the ordered lists
  (T +0xfc8 / +0xfd0, CT +0xfb0 / +0xfb8; +0xe8c / +0xe90 count them), T first; each shuffled (`for (i = 0; i < n -
  1; i++) { j = RandomInt(i, n - 1); if (j != i) swap(i, j); }`, tier0's global stream), then **0x180904350**: MSVC's
  std::stable_sort (a temp buffer up to 0x400 entries; 32 or fewer an insertion sort) by **0x1809635f0**
  (`a.priority < b.priority`): random inside a priority, the lowest first (dust2 20 at 0 and 10 at 1, inferno 19 / 21,
  mirage 15 / 18, ar_shoots 19 / 15). The indices (+0xf9c / +0xfa4) are left as they are.

## The team's next spot (GetNextSpawnPoint 0x1809297b0)

`random = mp_randomspawn == 1 || mp_randomspawn == team` (mp_randomspawn 0x18211a3f8, its value read at 0x18211a400;
registered 0x1800a0730, default 0: "0 = default; 1 = both teams; 2 = Terrorists; 3 = CTs"). The index (CT +0xf9c, T
+0xfa4) goes back to 0 when it is at or past the count, or when `!random` and now is more than 0.03 s after the last
pick (CT +0xfa0, T +0xfa8): a round's spawn burst starts from the first spot again. The spot at the index is returned,
the index moves on, the last pick's time = now.

## EntSelectSpawnPoint (0x180207d80)

- A coop logo map (18093d920): info_player_logo.
- Deathmatch (18093e040: game_type 1 && game_mode 2) with mp_randomspawn the pawn's team or 1 (and global +0x4b4 clear):
  from the static 0x181da0be8 (shared with the CTs' choice), FindEntityByClassname("info_deathmatch_spawn") RandomInt(1,
  10) times (null past the end, the first again after null), the first if still null; then 0x18023e340 with that class.
- A CT: from 0x181da0be8, 0x18023e340("info_player_counterterrorist"); a T: from 0x181da0bec, "info_player_terrorist".
  The chosen entity's handle is kept in the static. Arms Race (game_type 1 mode 0) is not deathmatch: team spawns,
  whatever mp_randomspawn says.
- Nothing: info_player_start ("PutClientInServer: no info_player_start on level").

## The search (0x18023e340)

- **The team classes**: up to 32 times (0x20) a spot from 0x1809297b0(team: 3 CT, 2 T); the first that gamerules vfn
  0x208 (IsSpawnPointValid) passes and isn't at the origin is the choice. None: the static is left as it was.
- **info_enemy_terrorist_spawn** (coop): the same over team 2 unless mp_randomspawn_los...
- **Any other class** (info_deathmatch_spawn): from the cursor, FindEntityByClassname on and round once (the cursor
  itself last); a candidate enabled, IsSpawnPointValid and not at the origin is remembered; with mp_randomspawn_los
  (0x18211a408, registered 0x1800a0890, default 1) it is taken at once when 0x18093e660 (unseen) and 0x18032d260
  (distance) pass for the enemy team (`mp_teammates_are_enemies ? 0 : (team != 3) + 2`; mode 0: both teams). Round
  the list: the last remembered one, else the pawn's team class (the recursion).

## IsSpawnPointValid (CCSGameRules vfn 0x208 = 0x18093e710)

- gamerules +0xf98 (set and cleared by 0x180957e50, the round restart, around its mass spawn) and not
  sv_allow_approximate_spawns: valid.
- The spot's vfn 0x430 (its own CanSpawn), then the standing hull (VEC_HULL_MIN / MAX at 0x1821193ac / b8: -16 -16 0 ..
  16 16 72) at the spot free (0x180cbbc70, filter 0x1801f8ae0(pawn, 0xc3001, group 8, object set 0xf)).
- sv_allow_approximate_spawns (0x18211a428, registered 0x1800a5350, default 0): valid = not occupied (0x18093e170);
  else invalid when another living player on a team stands at the spot (2D distance under 0.01).
- **0x18093e170** (occupied): another living player on a team (2 / 3) within the hull's extents on each axis (|dx| < 32,
  |dy| < 32, |dz| < 72).

## Sight and distance (deathmatch spawns only)

- **0x18093e660(spot, pawn, mode)**: p = spot + (0, 0, 32); mode 0: not seen by team 3 and not by team 2; 2 / 3: not
  seen by that team; anything else: true.
- **0x18032d450(p, team)**: seen when, for some living player of the team, a line from their eye (vfn 0x5e8) to p with
  interacts-with 0x42, group 3, flags 0x49, their handles ignored, ends with fraction 1.
- **0x18032d260(p, team)**: mp_randomspawn_dist (0x18211a418, registered 0x1800a07e0, default 0) below 1 or
  mp_randomspawn_los off: true; else true as soon as a living player of the team is at least mp_randomspawn_dist
  away; none: false.

## PutClientInServer (0x180216260)

1. The spot's origin and angles (0x180207d80).
2. **The nudge** 0x1809232f0: sv_spawn_random_nudge_offset (0x18211a438, registered 0x1800a7810, default 0, max 512)
   above 0: 8 tries of x / y offsets RandomFloat(-n, n); a try (0x18096cb60) drops to the floor (0x18091f260 from +16),
   must land at most 64 below the spot, see the spot (a line at half the hull's height, 0x1809692b0), have its hull
   free and not be occupied.
3. **Approximate**: sv_allow_approximate_spawns and occupied: 0x180922d30 finds the nearest empty space ("Spawn point
   for %s is occupied: placing %.0f units away"), else "spawning stuck".
4. **Deathmatch only**: the angles face the open space: rays from the spot + 64 at yaw 0, 40, ... 360 (10), 10000 long,
   0xc3001 group 8; the direction to their ends' average, pitch 0.
5. **The drop** 0x18091f260: a hull trace from the spot + 16 down 500 units with the pawn's own interacts-with (+0x608)
   and collision group; the place is the end + 0.1 up (and the ground entity). Then Teleport.

## RestartRound's spawn configuration (0x1809621f0, from RestartRound 0x180957e50)

**The configuration, rules +0xdc0** (RestartRound 0x180957e50, decompile lines ~389-404, 0x1809586b4..0x180958712):

```
if (mp_randomspawn == 0) {            // [0x18211a400] + 0x58
  if (+0xdc0 == 0) { +0xdc0 = Plat_RelativeTicks(); if (+0xdc0 == 0) +0xdc0 = 1; }
} else +0xdc0 = Plat_RelativeTicks(); // a new one every restart
ConMsg("Using spawn points configuration 0x%08X\n", +0xdc0);   // 0x1818c9928
```

Plat_RelativeTicks (tier0 import 0x18176a5e8; tier0_20261103 0x180140500) is QueryPerformanceCounter, never below its
last return (a static); +0xdc0 keeps its low 32 bits. Other writers: the constructor 0x1809058c0 (0), the match
history restore 0x18093fe70 (KeyValues "History/SpawnPointsCfg", 0x1818ca760, with +0xf9c / +0xfa4 = 0: a round backup
restore; the port has no backups). So with mp_randomspawn 0 (the competitive / wingman / casual cfgs) one configuration
holds for the whole map.

**0x1809621f0(rules, players)**, called at 0x18095a210 after the players are collected and just before the mass spawn
(+0xf98 = 1, the loops 180ae27b0 / 180a9aba0 then 180a96f00 over the same list in its order, +0xf98 = 0):

1. `RandomSeed((int)(short)rules+0xf0c ^ rules+0xdc0)`: +0xf0c is the rounds played (overtime.md's table; reset by
   1809575a0 in the game-restart branch). tier0's global stream reseeded.
2. 0x180903d10 (MSVC std::sort's _Sort_unchecked, ideal = count: 32 or fewer an insertion sort 0x1809036a0, else the
   median guess 0x1809033b0 and partition, the heap fallback) over the T list (+0xfd0, +0xfc8), then the CT list
   (+0xfb8, +0xfb0), with **0x180963250**: a live entity before a stale handle; then the origins (0x1803d6f50) compared
   as `cvttss2si` ints, x, then y, then z, `a < b`; then the entity index (0x1813aa290: from the identity's chunk, -1
   for none) `a < b`. A strict total order: the result is the one sorted order, whatever the algorithm.
3. **0x1809623c0**: the T list shuffled (the loop above), the CT list shuffled, then each 0x180904350 by 0x1809635f0 (the
   same as 0x1809563e0's tail).
4. The players list (param_2: a CUtlVector of controllers, count at +0, data at +8) shuffled the same way, then
   std::stable_sort (0x1809035a0 for 32 or fewer, else 0x180904130 with a buffer up to 0x200) by **0x180963130**:
   - m_iDraftIndex (+0x8b8) == -1 on one side only: the one set first (only that is compared, never the values);
   - else the FL_FAKECLIENT bit (m_fFlags +0x388, bit 8) differs: the human first;
   - else **180b563c0** (CSteamID::IsValid on m_steamID +0x710, the id or 0: account type (bits 52-55) 1..10, universe
     (bits 56-63) 1..4; an individual (1) needs a non-zero account id and instance 1; an anonymous game server (7) a
     non-zero account id and instance 0; a game server (3) a non-zero account id): a valid one first, the lower first;
   - else the lower entity index (the slot + 1).

The players list (RestartRound lines ~1281-1345): every connected controller (the 18096d1f0 / 18096dc30 iterator)
whose pawn (180b55040) is a player pawn (vfn 0xcb0 false: CCSPlayerPawn 0x180aea7a0 `return 0`, CCSObserverPawn
0x180a51080 `return 1`; an observer pawn instead gets vfn 0xcc0) on team 2 or 3 (+0x344). Every comparator here is a
strict total order, so the sorted orders don't depend on the shuffles; the shuffles' draws still move the seeded
stream, which the mass spawn's own draws then continue. Port: spawn-config.js (nextConfig, configSeed, originLess,
validSteamId, playerLess, applyConfig), SpawnSelect.restartConfig (one CUniformRandomStream, lib/cs-random.js, for every
spawn draw); comp.js roundStart spawns in the order it returns. The players have no draft index (all -1, equal) and the
slot order is the join order (player ids, cs2fixes/targets.js's convention).

## The cfgs

| cvar | competitive / wingman / casual | deathmatch | arms race |
|---|---|---|---|
| mp_randomspawn | 0 | 1 | 1 |
| mp_randomspawn_los | 0 | 1 | 0 |
| sv_allow_approximate_spawns | 0 | 0 | 0 |
| sv_spawn_random_nudge_offset | 0 | 0 | 0 |

## Port notes

- RandomInt / RandomFloat: tier0's global stream on the server: one CUniformRandomStream (lib/cs-random.js) for the
  spawn choice's draws, first seeded from the clock (tier0's GenerateDefaultRandomSeed 0x18015d580 reads
  QueryPerformanceCounter too), reseeded by each restart's configuration. CS2's stream is also drawn by everything
  else on its server between two restarts; ours only by the spawns.
- The priority sorts: 0x180904350 is std::stable_sort, the stable Array sort exactly; the base lists' V_qsort is
  lib/msvc-qsort.js; the origin sort is a strict total order (any sort).
- The configuration's clock: Plat_RelativeTicks is QueryPerformanceCounter (10 MHz on Windows 10 and later); the port
  reads process.hrtime in 100 ns units (spawn-config.js relativeTicks), its low 32 bits.
- The pawns aren't in our physics world: the hull test's player layer is the occupancy box test against the living
  players.
- The approximate fallback's own search (0x180922d30) is game.js freeAt (the nearest free standing place); no cfg
  turns it on.
- OURS on top (the owner's rule, spawn-select.js header): no stacking. CS2 stacks pawns when a side has more players
  than free spots (the mass spawn's +0xf98 passes every spot; 0x18023e340's 32 failed tries keep the last spot). The
  port refuses a spot already given in the mass spawn and spreads a choice that would still stack (spread: off the
  game's stream, Math.random). Where CS2 doesn't stack, the spots and the stream's draws are CS2's.

## The respawn modes' order (deathmatch, Arms Race)

docs/game/armsrace.md "The respawn": STATE_GUNGAME_RESPAWN's enter (vtable 0x181792e40 slot 0 = 0x1802085d0) and think
(slot 2 = 0x180237bd0) each call the respawn 0x1802521c0 while `sv_max_deathmatch_respawns_per_tick < 1 ||
DAT_181f9ed6c < it`, counting only respawns made; FrameUpdatePreEntityThink (0x180923bc0, CCSGameRules 0x1818c5450's
game-system slot) zeroes the count (0x180233f10). The state thinks from CCSPlayerPawn::PreThink (0x180236f50 ->
0x1802371c0: CBasePlayerPawn::PreThink 0x180d079f0, then the current state at pawn +0xd48, vfn 0x10), which runs in
the pawn's usercmds, inside its controller's PhysicsSimulate: the controllers in slot order (0x1805b70a0, frame.md).
So several waiting players come back lowest slot first, at most the cvar a frame. 0x1802521c0 refuses (no count) when
the engine's client value (CEngineServer vtable 0x1805dd1c0 slot 0x338 = engine2 0x1800a3670 -> CServerSideClient vfn
0x230 = 0x1800bc400: client +0xef4, written in networkserverservice.cpp's code) is non-zero, or while the pawn's
+0xdf0 is set (it sets it, then 18024d670, vfn 0xaf8, 1803eb9e0). The port's server has no engine client state, so
the first never refuses here; comp.js tick walks g.playing() (the join order) with the cap.

## Still to trace

Nothing for the spawn choice.
