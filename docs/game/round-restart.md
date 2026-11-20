# The round restart: what CleanUpMap removes and what it leaves

server_20261105 (image base 0x180000000).

## Functions

| Address | Module | What |
|---|---|---|
| 180917fd0 | server | CCSGameRules::CleanUpMap (`this` + 0x13d set skips all of it) |
| 1803ebc00 | server | un-parent a pawn |
| 1803d9790 | server | parent |
| 18137ac90 / 181384dc0 / 1813895a0 | server | the entity iterator |
| 1816b6d80 | server | class cast (against 181ebdbe0, 181ebdbb8, 181ee2318) |
| 180c30c10 | server | UTIL_Remove |
| 180592260 | server | spawn groups whose record has byte +9 set (spawngroupmgrgamesystem.cpp; the manager at 182087470) |
| 1805921a0 | server | spawn group name |
| 180592e70 | server | spawn group handle |
| 181ab560 | server | entity lump by name: vfn 0x108, then vfn 0x30 |
| 180bf0b90 | server | (manager, group, lump, ..., "cs_respawn", ...): create the lump's entities again |
| 1808d8b30 | server | respawn filter: the preserve list on each entity's "classname" keyvalue |
| 18092cdf0 | server | RestartRound's own stores (unread) |

## Fields

| Offset | Field |
|---|---|
| CCSGameRules +0x13d | skip CleanUpMap |
| entity->m_pEntity +0x38 | CEntityIdentity m_worldGroupId (int) |
| spawn group record +9 | respawned flag (byte) |

## Constants

| Value | What |
|---|---|
| 181e04220 | the preserve list: 86 pointers, ends at an empty string |

## CleanUpMap (180917fd0)

1. Every player pawn with a parent is un-parented first (1803ebc00 on a pawn, vfn 0x558, whose 1803d9790 parent is set).
2. The removal walk over every entity:
   - three class casts first (weapons, their items and one more) get their own calls (vfn 0xb60 / 0xb58, 0x8c8, 0x8c0) and are handled apart (not read further);
   - any other entity: its classname against the preserve list by `V_stricmp_fast`; a class on the list stays;
   - a class not on the list is removed (180c30c10) only when `*(int *)(entity->m_pEntity + 0x38) == 0`. An entity of another world group is left alone whatever its class.
3. The respawn pass: for each spawn group from 180592260: its name, handle, entity lump, then 180bf0b90 creates the lump's entities again minus the ones 1808d8b30 drops. Each created entity then gets vfn 800 per player slot.

## The preserve list (181e04220)

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

- A `skybox_reference` loads its map into its own world group (its "worldgroupid" keyvalue: ze_dark_souls' `skyboxWorldGroup0`); nothing there is ever removed by a restart. ze_dark_souls keeps 38 math_counters, 8 logic_relays and a logic_branch there (Level_Counter, NG_Counter, the `*_Tottal` and `*_Reset_Counter` counters, Vote_PEmber_Phase_Counter, the QS relays, See_Scene_00): its level (the first round is a warm-up that sets Level_Counter to 1 at 40 s; later rounds read 1: normal, or 2: champion), its new-game-plus count and its items' totals last for the map.
- A main-map entity on the preserve list (a func_brush, an info_target, a point_script) keeps its state too.

## Unread

- Whether the respawn pass makes a second copy of a non-preserved entity step 2 left standing (a skybox math_counter): record byte +9 and what 180bf0b90 does with a group whose entities exist. A local dedicated server would show it (`ent_find` after `mp_restartgame 1`); the one try (2026-11-12) crashed loading ze_dark_souls (an access violation after `host_workshop_map`, live build 1.41.9.6).
- Events still in the I/O queue for an entity that stays.
- The weapons' branch of the walk; RestartRound's own stores (18092cdf0).
- Which world group an `info_spawngroup_load_unload` group's entities get.
