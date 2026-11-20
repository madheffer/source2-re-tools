# The round restart: what CleanUpMap removes and what it leaves

server_20261105.dll (image base 0x180000000). Read with tools/re (strings, xref, a pointer-table scan) and Ghidra
(ReVa), 2026-11-12. Port: web/src/cs2web/world/round-carry.js (the carried entities), web/src/cs2web/world/world.js createRoundWorld
(`carry`), web/server/cs2web/core/game.js startRound. Check: web/src/cs2web/world/round-carry-test.mjs.

## CleanUpMap (180917fd0, CCSGameRules; `this` + 0x13d set skips all of it)

1. Every player pawn with a parent is un-parented first (1803ebc00 on a pawn, vfn 0x558, whose 1803d9790 parent is
   set).
2. **The removal walk** over every entity (the iterator 18137ac90 / 181384dc0 / 1813895a0):
   - three class casts first (1816b6d80 against 181ebdbe0, 181ebdbb8, 181ee2318): weapons, their items and one more
     get their own calls (vfn 0xb60 / 0xb58, 0x8c8, 0x8c0) and are handled apart (not read further);
   - any other entity: its classname against the **preserve list** by `V_stricmp_fast`; a class on the list stays;
   - a class not on the list is removed (180c30c10, UTIL_Remove) **only when its identity's world group is 0**:
     `*(int *)(entity->m_pEntity + 0x38) == 0`, CEntityIdentity `m_worldGroupId`. An entity of another world group
     is left alone whatever its class.
3. The respawn pass: 180592260 (spawngroupmgrgamesystem.cpp, the spawn group manager at 182087470) lists every spawn
   group whose record has byte +9 set; for each, its name (1805921a0), its handle (180592e70), its entity lump
   (181ab560's vfn 0x108 by name, then vfn 0x30) and 180bf0b90(manager, group, lump, ..., "cs_respawn", ...) creates
   the lump's entities again, minus the ones the filter 1808d8b30 drops (the same preserve list on each entity's
   "classname" keyvalue). Each created entity then gets vfn 800 per player slot.

## The preserve list (181e04220, 86 pointers, ends at an empty string)

ai_network ai_hint cs_gamerules cs_team_manager cs_player_manager env_cubemap_fog env_soundscape
env_soundscape_proxy env_soundscape_triggerable env_sky env_wind env_fog_controller env_tonemap_controller
env_cascade_light env_combined_light_probe_volume func_brush func_wall func_buyzone func_illusionary
func_hostage_rescue func_bomb_target info_node info_target info_node_hint info_player_counterterrorist
info_player_terrorist info_enemy_terrorist_spawn info_deathmatch_spawn info_map_parameters keyframe_rope
light_environment light_spot light_omni light_ortho move_rope info_ladder player cs_player_controller cs_bot
point_camera scene_manager shadow_control sky_camera soundent trigger_soundscape viewmodel predicted_viewmodel
csgo_viewmodel worldent point_devshot_camera logic_choreographed_scene info_bomb_target_hint_A
info_bomb_target_hint_B info_hostage_rescue_zone_hint generic_actor vote_controller wearable_item point_hiding_spot
game_coopmission_manager chicken global_chatter sky_camera player_spray_decal team_select_camera
team_select_terrorist team_select_counterterrorist terrorist_team_intro_camera terrorist_wingman_intro_camera
terrorist_rush_intro_camera counterterrorist_team_intro_camera counterterrorist_wingman_intro_camera
counterterrorist_rush_intro_camera team_intro_terrorist team_intro_counterterrorist wingman_intro_terrorist
wingman_intro_counterterrorist rush_intro_terrorist rush_intro_counterterrorist end_of_match_camera
end_of_match_character observer point_script point_pulse custom_hud_layout custom_player_camera cs_player_camera

No math_counter, logic_relay, logic_branch or logic_case: in the main map those start again every round.

## What it means for a map

- A `skybox_reference` loads its map into its own world group (its "worldgroupid" keyvalue: ze_dark_souls'
  `skyboxWorldGroup0`). Whatever sits in that map is never removed by a restart: ze_dark_souls keeps 38
  math_counters, 8 logic_relays and a logic_branch there (Level_Counter, NG_Counter, the `*_Tottal` and
  `*_Reset_Counter` counters, Vote_PEmber_Phase_Counter, the QS relays, See_Scene_00), so its level (the first round
  is a warm-up that sets Level_Counter to 1 at 40 s; later rounds read 1: the normal level, or 2: champion), its
  new-game-plus count and its items' totals last for the map.
- An entity of the main map on the preserve list (a func_brush, an info_target, a point_script) keeps its state too.
  Not ported (round-carry.js carries only the other world groups).

## Unread

- Whether the respawn pass makes a second copy of a non-preserved entity that step 2 left standing (a skybox
  math_counter): record byte +9, and what 180bf0b90 does with a group whose entities exist, are not read. The maps
  rely on one counter per name; the port makes none. A local dedicated server would show it (`ent_find` after
  `mp_restartgame 1`); the one try on 2026-11-12 crashed loading ze_dark_souls (an access violation after
  `host_workshop_map`, the live build 1.41.9.6).
- What the restart does with events still in the I/O queue for an entity that stays.
- The weapons' branch of the walk, RestartRound's own stores (18092cdf0).
- Which world group an `info_spawngroup_load_unload` group's entities get.
