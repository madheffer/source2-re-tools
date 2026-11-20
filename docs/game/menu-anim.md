# Main menu characters and scene (uimodel graph, de_dust2_vanity)

pak01 (2026-11-15): animation/graphs/ui/uimodel.vnmgraph and its referenced graphs; maps/de_dust2_vanity.vpk
(entities, world/*.glb with each .vmat as extras). No binary. The graph runtime: [anim-graph.md](anim-graph.md).

## de_dust2_vanity's entities

| Class | Count | What |
|---|---|---|
| csgo_player_previewmodel | 7 | `vanity_character` (you), `_1`..`_4` (the party), `_5` (character_mode inventory-inspect), `_6`; each `animgraph characters/models/shared/animgraphs/ui_player_t.vanmgrph` (the model's AnimGraph1 name; the compiled graph run is uimodel.vnmgraph), `character_mode main-menu`, a `weapon_type` ("Pistol", "C4", "Sniper Rifle", "Shotgun": stand-ins) and a model; `_1` has `defaultanim sh_c4_defusal_stand_loop` |
| csgo_item_previewmodel | 13 | `item`, `item1`..`item13`, `pet1`: inventory slots (a weapon / knife on the crate with `weapon_state inspect`, a crate `csgo_drop_crate_fall`, chickens / chicknegg for the pet); filled by the client from the inventory, empty without one |
| prop_dynamic | | `nest` (`startdisabled true`); also `cs_pet_placement` |
| info_particle_system | 25 | active: `particles/environment/ambient_paper_debris_2.vpcf` x4, `particles/ambient_fx/ambient_ground_dust.vpcf`; `start_active false`: pet photo effects (`particles/pet_photo/*`, `[PR#]sparks`, `confetti`, ... and `solo_` twins), `chicken_gone_*` |
| path_particle_rope_clientside | 26 | `effect_name particles/entity/path_particle_cable_static.vpcf`, `pathnodes` / `pathnoderadiusscales` / `particle_spacing 30` / `slack 0` |
| point_camera_vertical_fov | 97 | cam_default is the menu's |
| post_processing_volume | 19 | |
| light_barn | 11 | |

path_particle_cable_static.vpcf: C_OP_InstantaneousEmitter (snapshot CP 0), C_INIT_InitFromCPSnapshot (attributes 0,
34, 6, 3), C_OP_SetFromCPSnapshot (34), C_OP_RenderCables (`materials/cable/csgo_placeholder_cable.vmat`,
TEXTURE_REPETITION_PATH, tesselation 0..4).

## uimodel.vnmgraph

- Control parameters in order: character_mode (ID), team_preview_variant, team_preview_position,
  end_of_match_celebration_ID (ID), is_CT (bool), weapon_type (ID), weapon_category (ID), banner_animation (ID),
  weapon_state (ID), animation_seed, team_preview_random, inspect_turn_angle, action (ID), chick_snapshot_variant,
  character_mode_reset (bool, read only by chick_snapshot), chick_life_stage, action_variation, life_stage.
- Root state machine (default state 9 "Invalid"): MainMenu, BuyMenu, Diorama, TeamSelect, EndOfMatch,
  InventoryInspect, Team Intro, Wingman Intro, mvp_banner, Invalid, chick_snapshot, chick_viewmodel, Rush Intro; each
  entered by `character_mode` = main_menu, buy_menu, diorama_mode, team_select, end_of_match, inventory_inspect,
  team_intro, wingman_intro, mvp_banner, chick_snapshot, chick_viewmodel, rush_intro (global transitions).
- MainMenu (#19) = ReferencedGraphNode (#20, slot 0) -> uimodel_walkup.vnmgraph.
- Outside MainMenu: IDBasedSelectorNode (EndOfMatch's pick by end_of_match_celebration_ID), IDBasedClipSelectorNode,
  OrientationWarpNode.
- 25 graphs (uimodel, _walkup, _idles, 22 celebration / defeat variants), 555 clips, 57.5 MB packed.

## uimodel_walkup.vnmgraph

- Root state machine, default state 2 WalkUp: is_CT -> WPN (weapon category) -> the agent walking into its spot
  (`t_main_menu_knife_walkup` 11 s, ...). Idle (#15) and Idle0 (#17): each a ReferencedGraphNode ->
  uimodel_idles.vnmgraph; StateCompletedConditionNode x3: WalkUp -> Idle, Idle <-> Idle0 (the idles graph re-entered
  each time its clip completes: its selectors pick again).
- Its own parameters add team_preview, override_animation (ID), weapon_is_legacy_model (bool), action_reset (bool).

## uimodel_idles.vnmgraph

- Root: SM -> CT (entry is_CT) / T (Not is_CT) -> WPN by weapon_category (weapon_category_pistol, _knife, _rifle, _smg,
  _machinegun, _sniper, _grenade, _equipment, _shotgun) -> by weapon_type (weapon_elite, weapon_revolver,
  weapon_knife_push, weapon_aug, weapon_famas, weapon_mp7, weapon_m249, weapon_negev, weapon_awp, weapon_ssg08,
  weapon_scar20, weapon_g3sg1, weapon_c4, weapon_nova / weapon_sawedoff, weapon_xm1014, weapon_mag7, ...; the rest a
  Not / And entry) -> ParameterizedClipSelectorNode on animation_seed over that weapon's clips
  (animation/anims/ui_anims/main_menu/{ct,t}/..., 233 clips).
- Weights: none except CT Knife [6,0,0,0,0,0,0,0,0] (backflip, slicedice02, lookat01, idle, flip01, slicedice01,
  lookat02, shrug, headtilt: only ct_main_menu_knife_backflip), CT Rifle [5,1,1,1] (idle_handrepo_m4 x5, lookat,
  shouldershrug, weightshift), T Knife [6,0,...] (a ParameterizedSelectorNode: only t_main_menu_knife_idle). The pick
  is `floor(|seed|) % ` the weighted options.
- Clips don't loop (m_bAllowLooping false); Knife states carry WPN_DISABLE_LEFT_HAND_IK entry / execute / exit events.
- Nothing in the graphs sets animation_seed.

## csgo_effects (the haze cards)

| Material | Masks (g_tMask1 / 2 / 3) | Scale / pan (1; 2; 3) | Feather | Other |
|---|---|---|---|---|
| fog_card_001 | 1x1 white, 1x1 white, cloud_002_mask | (10,10)/(5,0); (0.5,1)/(0.03,0); default | 2000 | opacity 0.597, base (0.41, 0.14, 0.04) |
| smoke_backdrop_001 | smoke_004, smoke_001, smoke_003 | (10,2.5)/(1,0.2); (0.9,0.25)/(0.02,0.006); (0.5,1)/(0.025,0) | 123.077 | base (1, 0.71, 0.46) |
| dust_backdrop_001 | smoke_004b, smoke_005, smoke_005 | (10,5)/(2,0); (0.6,1.1)/(0.05,-0.01); (0.5,1)/(0.06,0.01) | 20 | fresnel exponent 1.96, falloff 10 |

All F_DEPTH_FEATHER 1, g_flFeatherFalloff 1, g_bFogEnabled 1, wrap addressing. g_tColor is a 1x1 constant (VRF's
`_vmat_g_tcolor_e42befc7`, one file for all three); masks greyscale RGB, alpha 255.

## Unread

- client.dll's preview player (C_CSGO_PreviewPlayer / CCSGO_PlayerPreviewModel): animation_seed's source, the
  weapon_type / weapon_category IDs it sends (taken from the graph's own comparison IDs), is_CT.
- C_PathParticleRope's snapshot fill and the cables renderer.
- csgo_effects' pixel shader (shaders_vulkan_dir.vpk csgo_effects_vulkan_*_ps, the F_DEPTH_FEATHER combo): the
  feather's curve and the mask channel.
