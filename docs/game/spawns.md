# Spawn spots (team matches)

server_20261105, tier0_20261103, engine2 (same build).

## Functions

| Address | Module | What |
|---|---|---|
| 0x180154270 | server | SpawnPoint vfn 0x430 (its own CanSpawn): `return 1` |
| 0x1808dac10 | server | SetEnabled: +0x4ac = 1; gamerules (DAT_1821ba1c0) exist and it was 0: 0x1809563e0 |
| 0x1808dada0 | server | SetDisabled: +0x4ac = 0; gamerules exist and it was 1: 0x1809563e0 |
| 0x1808daf30 | server | ToggleEnabled: +0x4ac = !+0x4ac; gamerules exist: 0x1809563e0, always |
| 0x18090d240 | server | an entity's spawn: into the base lists, then 0x1809563e0 |
| 0x180916810 | server | the lists' lazy init |
| 0x180925a50 | server | GenerateSpawnPointLists |
| 0x180bfc410 | server | FindEntityByClassname |
| 0x180963890 | server | V_qsort comparator `a.priority - b.priority` (stale handle before live) |
| 0x1809563e0 | server | ordered lists: enabled points, shuffled, stable-sorted by priority |
| 0x180904350 | server | MSVC std::stable_sort (temp buffer up to 0x400; <= 32 insertion sort) |
| 0x1809635f0 | server | `a.priority < b.priority` |
| 0x1809297b0 | server | GetNextSpawnPoint(team) |
| 0x180207d80 | server | EntSelectSpawnPoint |
| 0x18093d920 | server | coop logo map |
| 0x18093e040 | server | deathmatch: game_type 1 && game_mode 2 |
| 0x18023e340 | server | the spot search (class) |
| 0x18093e710 | server | IsSpawnPointValid (CCSGameRules vfn 0x208) |
| 0x180cbbc70 | server | hull free test |
| 0x1801f8ae0 | server | trace filter (pawn, 0xc3001, group 8, object set 0xf) |
| 0x18093e170 | server | occupied |
| 0x18093e660 | server | unseen (spot, pawn, mode) |
| 0x18032d450 | server | seen by team (p, team) |
| 0x18032d260 | server | distance test (p, team) |
| 0x180216260 | server | PutClientInServer |
| 0x1809232f0 | server | the nudge |
| 0x18096cb60 | server | a nudge try |
| 0x1809692b0 | server | line of sight at half hull height |
| 0x180922d30 | server | nearest empty space (approximate spawns) |
| 0x18091f260 | server | the drop to the floor |
| 0x180957e50 | server | RestartRound |
| 0x1809621f0 | server | RestartRound's spawn configuration (rules, players), called at 0x18095a210 |
| 0x180903d10 | server | MSVC std::sort _Sort_unchecked, ideal = count (<= 32: insertion sort 0x1809036a0; else median guess 0x1809033b0 and partition; the heap fallback) |
| 0x180963250 | server | spot comparator (live first; origins as `cvttss2si` x, y, z; entity index) |
| 0x1803d6f50 | server | abs origin |
| 0x1813aa290 | server | entity index (from the identity's chunk, -1 none) |
| 0x1809623c0 | server | shuffle T then CT, then each 0x180904350 by 0x1809635f0 |
| 0x1809035a0 / 0x180904130 | server | std::stable_sort (<= 32 / else buffer up to 0x200) |
| 0x180963130 | server | player comparator |
| 0x180b563c0 | server | CSteamID::IsValid |
| 0x18096d1f0 / 0x18096dc30 | server | connected controller iterator |
| 0x180b55040 | server | controller's pawn |
| 0x180aea7a0 / 0x180a51080 | server | vfn 0xcb0: CCSPlayerPawn `return 0`, CCSObserverPawn `return 1` |
| 180ae27b0 / 180a9aba0, 180a96f00 | server | the mass spawn's loops |
| 0x1809575a0 | server | game-restart reset of rounds played |
| 0x18093fe70 | server | match history restore, a round backup restore (KeyValues "History/SpawnPointsCfg" 0x1818ca760 into +0xdc0; +0xf9c / +0xfa4 = 0) |
| 0x1809058c0 | server | CCSGameRules constructor |
| 0x1809669f0 | server | Think (vtable 0x1818c5450 slot 50, line ~490) |
| 0x180965080 | server | TeamFull (from 18095fce0, 1802d5940, 1802de9b0, 180944090) |
| 0x180910fb0 | server | team balance (from 180954a60) |
| 0x1809543d0 | server | slot 8: a spawn group's load (map name not "<empty>", no landmark, +0x14 == 0, known group: 1805c4090) |
| 0x18015d580 | server | tier0 GenerateDefaultRandomSeed (QueryPerformanceCounter) |
| 0x18176a5e8 | server | import slot: tier0.dll!Plat_RelativeTicks |
| 0x180140500 | tier0 | Plat_RelativeTicks: QueryPerformanceCounter, never below its last return (static) |
| 0x1802085d0 / 0x180237bd0 | server | STATE_GUNGAME_RESPAWN enter (vtable 0x181792e40 slot 0) / think (slot 2) |
| 0x1802521c0 | server | the respawn |
| 0x180923bc0 | server | FrameUpdatePreEntityThink: zeroes the count (0x180233f10) |
| 0x180236f50 -> 0x1802371c0 | server | CCSPlayerPawn::PreThink: CBasePlayerPawn::PreThink 0x180d079f0, then state at pawn +0xd48 vfn 0x10 |
| 0x1805b70a0 | server | controllers' PhysicsSimulate in slot order (frame.md) |
| 18024d670, 1803eb9e0 | server | respawn's calls after setting +0xdf0 (with vfn 0xaf8) |
| engine2 0x1800a3670 | engine2 | CEngineServer vtable 0x1805dd1c0 slot 0x338 -> CServerSideClient vfn 0x230 = 0x1800bc400: client +0xef4 |

## Fields

| Offset | Field |
|---|---|
| CSpawnPoint +0x4a8 | m_iPriority ("priority"; lower first) |
| CSpawnPoint +0x4ac | m_bEnabled ("enabled"; maps write true / false; FGD default true) |
| rules +0xf80 / +0xf88 | T base list count / handles |
| rules +0xf68 / +0xf70 | CT base list |
| rules +0xfc8 / +0xfd0 | T ordered list (std::sort is passed +0xfd0, +0xfc8) |
| rules +0xfb0 / +0xfb8 | CT ordered list (passed +0xfb8, +0xfb0) |
| rules +0xe8c / +0xe90 | count the ordered lists (written by 0x1809563e0) |
| rules +0xf9c / +0xfa0 | CT index / last pick time |
| rules +0xfa4 / +0xfa8 | T index / last pick time |
| rules +0xd84 | lists made (writers: ctor 0, 0x180916810 1, 0x1809543d0 0) |
| rules +0xe94 / +0xe98 | team sizes (mp_retake_t_count / mp_retake_ct_count in Retakes, else engine vfn 0x160 over max players) |
| rules +0x140 | from a cvar (init) |
| rules +0xf98 | mass spawn in progress (set / cleared by RestartRound) |
| rules +0xdc0 | spawn configuration |
| rules +0xf0c | rounds played (short; overtime.md) |
| 0x181da0be8 / 0x181da0bec | static last spot CT (and DM) / T |
| global +0x4b4 | blocks the DM path |
| controller +0x8b8 | m_iDraftIndex |
| controller +0x388 | m_fFlags (bit 8 FL_FAKECLIENT) |
| controller +0x710 | m_steamID |
| pawn +0x344 | team |
| pawn +0x608 | interacts-with |
| pawn +0xdf0 | respawn in progress |
| DAT_181f9ed6c | respawns made this frame |

Classes: CInfoPlayerTerrorist (vtable 0x1818c6d98), CInfoPlayerCounterterrorist (0x1818c7510), CInfoDeathmatchSpawn
derive SpawnPoint (0x1818c4520) <- CServerOnlyPointEntity; CInfoPlayerStart is a plain CPointEntity.

SpawnPoint_API input records (0x50 bytes: +0x00 "SpawnPoint_API::<Input>", +0x08 display name, +0x48 handler):
SetEnabled ("Set Enabled") 0x181e06fe0, SetDisabled ("Set Disabled") 0x181e07030, ToggleEnabled ("Toggle Enabled")
0x181e07080.

## Constants

| Value | What |
|---|---|
| mp_randomspawn | 0x18211a3f8 (value at 0x18211a400 + 0x58), reg 0x1800a0730, default 0: "0 = default; 1 = both teams; 2 = Terrorists; 3 = CTs" |
| mp_randomspawn_los | 0x18211a408, reg 0x1800a0890, default 1 |
| mp_randomspawn_dist | 0x18211a418, reg 0x1800a07e0, default 0 |
| sv_allow_approximate_spawns | 0x18211a428, reg 0x1800a5350, default 0 |
| sv_spawn_random_nudge_offset | 0x18211a438, reg 0x1800a7810, default 0, max 512 |
| sv_max_deathmatch_respawns_per_tick | respawn cap per frame |
| 0x181e04220 | CleanUpMap preserve list (char*): info_player_counterterrorist (0x181e042e0), info_player_terrorist (+8), info_enemy_terrorist_spawn, info_deathmatch_spawn, info_map_parameters, ... |
| 0x1821193ac / b8 | VEC_HULL_MIN / MAX: -16 -16 0 .. 16 16 72 |
| 0.03 s | GetNextSpawnPoint's burst window |
| 32 (0x20) | team-class search tries |
| 0x1818ca4d8 / 0x1818ca510 | "Invalid terrorist spawnpoint at (%.1f,%.1f,%.1f)" / the CT's |
| 0x1818c9928 | "Using spawn points configuration 0x%08X\n" |

Priorities: dust2 20 at 0 and 10 at 1, inferno 19 / 21, mirage 15 / 18, ar_shoots 19 / 15.

| cvar | competitive / wingman / casual | deathmatch | arms race |
|---|---|---|---|
| mp_randomspawn | 0 | 1 | 1 |
| mp_randomspawn_los | 0 | 1 | 0 |
| sv_allow_approximate_spawns | 0 | 0 | 0 |
| sv_spawn_random_nudge_offset | 0 | 0 | 0 |

## Preserved over the restart

The preserve list keeps the spawn point entities, their m_bEnabled and the gamerules' handle lists through every round
of a map (a SetDisabled mid-round holds next round). The maps switch their .standard and .2v2 sets from the Pulse
GameModeCheck (de_inferno, de_nuke, de_overpass, de_vertigo: pulse.md). The inputs' rebuild touches only the ordered
lists (the base lists stay); its shuffle draws from tier0's stream.

## The lists

- **0x18090d240**: info_player_terrorist / info_enemy_terrorist_spawn -> T list, info_player_counterterrorist -> CT
  list; info_deathmatch_spawn isn't listed. Then 0x1809563e0. (The map's points spawn before 0x180916810 first runs;
  a point spawned later by a template is appended unchecked.)
- **0x180916810**: returns when +0xd84 set; else team sizes, +0x140, GenerateSpawnPointLists, the Retakes /
  info_player_logo bits, +0xd84 = 1. Callers: the Think (every frame), TeamFull, team balance, and slot 8 (spawn group
  load, which first clears +0xd84). So the lists are made once per map, at its load (first Think, before any player),
  never at a round restart.
- **GenerateSpawnPointLists 0x180925a50**: +0xf80 and +0xf68 = 0; per class, FindEntityByClassname walks the points;
  IsSpawnPointValid(rules, point, null) (no pawn: +0xf98 clear, vfn 0x430 true, the standing hull with a null pawn's
  filter) false: the "Invalid ... spawnpoint" message, skipped; else appended. Each list > 1 entry V_qsort'ed with
  0x180963890. Then 0x1809563e0.
- **0x1809563e0**: enabled points (+0x4ac) of each base list (stale skipped) into the ordered lists, T first; each
  shuffled (`for (i = 0; i < n - 1; i++) { j = RandomInt(i, n - 1); if (j != i) swap(i, j); }`, tier0's global stream),
  then 0x180904350 by 0x1809635f0: random inside a priority, lowest first. Indices (+0xf9c / +0xfa4) left as they are.

## GetNextSpawnPoint (0x1809297b0)

`random = mp_randomspawn == 1 || mp_randomspawn == team`. Index resets to 0 when at or past the count, or when `!random`
and now > last pick + 0.03 s (a round's spawn burst starts from the first spot again). Returns the spot at the index,
index + 1, last pick = now.

## EntSelectSpawnPoint (0x180207d80)

- Coop logo map (18093d920): info_player_logo.
- Deathmatch (18093e040) with mp_randomspawn the pawn's team or 1 (and global +0x4b4 clear): from 0x181da0be8,
  FindEntityByClassname("info_deathmatch_spawn") RandomInt(1, 10) times (null past the end, the first again after
  null), the first if still null; then 0x18023e340 with that class.
- CT: from 0x181da0be8, 0x18023e340("info_player_counterterrorist"); T: from 0x181da0bec, "info_player_terrorist". The
  chosen handle is kept in the static. Arms Race (game_type 1 mode 0) is not deathmatch: team spawns.
- Nothing: info_player_start ("PutClientInServer: no info_player_start on level").

## The search (0x18023e340)

- Team classes: up to 32 spots from 0x1809297b0(team: 3 CT, 2 T); the first passing IsSpawnPointValid and not at the
  origin. None: the static stays. (So with more players than free spots, pawns stack: the mass spawn's +0xf98 passes
  every spot; 32 failed tries keep the last spot.)
- info_enemy_terrorist_spawn (coop): the same over team 2 unless mp_randomspawn_los...
- Any other class (info_deathmatch_spawn): from the cursor, FindEntityByClassname on and round once (cursor last); an
  enabled, valid, not-at-origin candidate is remembered; with mp_randomspawn_los it is taken at once when 0x18093e660
  and 0x18032d260 pass for the enemy team (`mp_teammates_are_enemies ? 0 : (team != 3) + 2`; mode 0: both). Round the
  list: the last remembered, else the pawn's team class (recursion).

## IsSpawnPointValid (0x18093e710)

1. +0xf98 set and not sv_allow_approximate_spawns: valid.
2. vfn 0x430, then the standing hull at the spot free (0x180cbbc70, filter 0x1801f8ae0).
3. sv_allow_approximate_spawns: valid = not occupied (0x18093e170); else invalid when another living player on a team
   stands at the spot (2D distance under 0.01).

0x18093e170: another living player on team 2 / 3 with |dx| < 32, |dy| < 32, |dz| < 72.

## Sight and distance (deathmatch spawns)

- 0x18093e660(spot, pawn, mode): p = spot + (0, 0, 32); mode 0: not seen by team 3 and not by team 2; 2 / 3: not seen
  by that team; else true.
- 0x18032d450(p, team): seen when for some living player of the team a line from their eye (vfn 0x5e8) to p
  (interacts-with 0x42, group 3, flags 0x49, their handles ignored) ends with fraction 1.
- 0x18032d260(p, team): mp_randomspawn_dist < 1 or mp_randomspawn_los off: true; else true once a living player of the
  team is at least mp_randomspawn_dist away; none: false.

## PutClientInServer (0x180216260)

1. Spot origin and angles (0x180207d80).
2. Nudge 0x1809232f0: sv_spawn_random_nudge_offset > 0: 8 tries of x / y RandomFloat(-n, n); a try (0x18096cb60) drops
   to the floor (0x18091f260 from +16), must land at most 64 below the spot, see the spot (0x1809692b0), have its hull
   free and not be occupied.
3. Approximate: sv_allow_approximate_spawns and occupied: 0x180922d30 ("Spawn point for %s is occupied: placing %.0f
   units away"), else "spawning stuck".
4. Deathmatch only: face the open space: rays from spot + 64 at yaw 0, 40, ... 360 (10), 10000 long, 0xc3001 group 8;
   the direction to their ends' average, pitch 0.
5. Drop 0x18091f260: hull trace from spot + 16 down 500 u with the pawn's interacts-with (+0x608) and collision group;
   place = end + 0.1 up (and the ground entity). Teleport.

## RestartRound's spawn configuration

Rules +0xdc0 (RestartRound 0x180957e50, decompile ~389-404, 0x1809586b4..0x180958712):

```
if (mp_randomspawn == 0) {            // [0x18211a400] + 0x58
  if (+0xdc0 == 0) { +0xdc0 = Plat_RelativeTicks(); if (+0xdc0 == 0) +0xdc0 = 1; }
} else +0xdc0 = Plat_RelativeTicks(); // a new one every restart
ConMsg("Using spawn points configuration 0x%08X\n", +0xdc0);   // 0x1818c9928
```

+0xdc0 keeps the low 32 bits (QueryPerformanceCounter: 10 MHz on Windows 10 and later). Other writers: ctor (0), the
history restore. With mp_randomspawn 0 one configuration holds for the whole map.

0x1809621f0(rules, players), after the players are collected, before the mass spawn (+0xf98 = 1, loops 180ae27b0 /
180a9aba0 then 180a96f00 over the list in order, +0xf98 = 0):

1. `RandomSeed((int)(short)rules+0xf0c ^ rules+0xdc0)` (tier0's global stream).
2. 0x180903d10 over the T list (+0xfd0, +0xfc8), then CT (+0xfb8, +0xfb0) with 0x180963250: live before stale; origins
   as `cvttss2si` ints, x then y then z, `a < b`; then entity index `a < b`. Strict total order.
3. 0x1809623c0.
4. The players list (CUtlVector of controllers, count +0, data +8) shuffled the same way, then stable-sorted
   (0x1809035a0 / 0x180904130) by 0x180963130:
   - m_iDraftIndex == -1 on one side only: the set one first (values never compared);
   - else FL_FAKECLIENT differs: the human first;
   - else 180b563c0 (account type bits 52-55 1..10, universe bits 56-63 1..4; individual (1): non-zero account id and
     instance 1; anonymous game server (7): non-zero account id and instance 0; game server (3): non-zero account id):
     valid first, the lower first;
   - else the lower entity index (slot + 1).

Players list (RestartRound ~1281-1345): every connected controller whose pawn is a player pawn (vfn 0xcb0 false; an
observer pawn gets vfn 0xcc0) on team 2 or 3 (+0x344). Every comparator is a strict total order, so the sorted orders
don't depend on the shuffles; the shuffles' draws still move the seeded stream, which the mass spawn's draws continue.
tier0's stream is drawn by everything else on the server between restarts too.

## Respawn modes' order (deathmatch, Arms Race)

armsrace.md "The respawn": STATE_GUNGAME_RESPAWN's enter and think each call 0x1802521c0 while
`sv_max_deathmatch_respawns_per_tick < 1 || DAT_181f9ed6c < it`, counting only respawns made; 0x180923bc0 (CCSGameRules
0x1818c5450's game-system slot) zeroes the count. The state thinks from PreThink, inside the controller's
PhysicsSimulate: controllers in slot order (0x1805b70a0). So waiting players come back lowest slot first, at most the
cvar a frame. 0x1802521c0 refuses (no count) when the engine's client value (+0xef4, written in
networkserverservice.cpp) is non-zero, or while pawn +0xdf0 is set (it sets it, then 18024d670, vfn 0xaf8, 1803eb9e0).
