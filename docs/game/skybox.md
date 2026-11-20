# The 3D skybox and the 2D sky

client_20261015; shaders_vulkan_dir.vpk (sky.vfx, csgo_unlitgeneric.vfx).

## Functions

| Address | Module | What |
|---|---|---|
| 0x180a39760 | client | AddViewsToSceneSystem (loopmodegame.cpp line 0x4d6): reads r_draw3dskybox, builds the skybox view |
| 0x1800c0540 | client | registers r_draw3dskybox |
| 0x180c0d8d0 | client | fog record = `0x18096a8f0() + 0x13e8` |
| 0x18096a8f0 | client | fog record base |
| 0x1807a8240 | client | finds the sky camera volume at view + 0x4a0 |
| 0x1809205f0 | client | reads clip_3D_skybox_near_to_world_far |
| 0x180ad9150 | client | reads enable_separate_skybox_fog |

## Fields

| Offset | Field |
|---|---|
| view +0x4a0 / +0x4a4 / +0x4a8 | the view's eye |
| sky camera scale (int16, local_1550) | 0 = no 3D skybox |
| sky camera origin (local_154c / 1548 / 1544) | |
| fog record +100 | enabled byte |
| fog record +0x24, +0x28 | multiplied by 1 / scale for the skybox view (taken as start / end: UNSETTLED) |
| sky camera volume +0x648 / +0x649 | bytes copied into the view (likely m_bSkyboxReceivesWorldCsm / m_bWorldReceivesSkyboxCsm: UNREAD) |
| sky camera volume +0x630 | handle |
| sky camera volume +0x639 | when set, offset +0x63c..0x644 added to a position (UNREAD) |
| param_1 + 0x60, vtable +0x58 | where the view is handed on |

## Constants

| Value | What |
|---|---|
| r_draw3dskybox | string 0x181ad3088; ConVar 0x18254e650; value byte at [0x18254e658] + 0x58 |
| 0x181bbe320 / 0x181bbe340 | strings m_bSkyboxReceivesWorldCsm / m_bWorldReceivesSkyboxCsm |
| 0x181c1ec48 | string clip_3D_skybox_near_to_world_far |
| 0x181c52860 | string enable_separate_skybox_fog |
| F_BLEND_MODE | 0 Opaque, 1 Translucent, 2 Alpha Test, 3 Mod2x, 4 Additive, 5 Multiply, 6 ModThenAdd |

## Where the skybox lives

- A map's `skybox_reference` names `maps/<dir>/<name>.vmap`; its world `maps/<dir>/<name>/world.vwrld_c` (world nodes,
  own lightmaps, env_cubemap_array). CS2's maps ship it as a vpk: game/csgo/maps/prefabs/de_dust2/de_dust2_skybox.vpk,
  prefabs/de_mirage/3dskybox_mirage_legacy.vpk, prefabs/de_vertigo/skybox2.vpk, prefabs/de_inferno/inferno_skybox.vpk
  (a workshop item carries it inside).
- Team maps' sky materials (materials/skybox/sky_de_dust2.vmat ...) are in pak01, not the map vpk.
- de_vertigo's own env_sky starts disabled; the enabled one (`[PR#]54_sky`, same sky_de_vertigo.vmat) is in its skybox
  prefab. de_inferno's prefab has an enabled env_gradient_fog.

## AddViewsToSceneSystem

- r_draw3dskybox on and scale != 0: skybox eye = `sky camera origin + view eye / scale`.
- The fog record is copied whole into the skybox view, +0x24 / +0x28 x 1 / scale (gradient-fog.md keeps start / end as a pair).
- UNREAD: scenesystem's order of the skybox and world views, the skybox view's near / far,
  clip_3D_skybox_near_to_world_far, the separate skybox fog (fog_*skybox).

## sky.vfx (2D sky)

- VS: cube at the eye; `output_0 = normalize(position x g_matSkyWsToOs)`.
- PS (BC6H, D_FOG_TYPE 1): sample at the direction rotated by `g_flRotation x 2 pi` about z, `z + g_flHorizonOffset`;
  x g_flBrightnessExposureBias x g_flRenderOnlyExposureBias x g_vTint (SkyTint); both biases through
  `Expression(pow(2,this))`. Lerped to the view's fog colour by
  `saturate(min(maxOpacity, saturate(farDistance x scale + bias)^exponent))`: the 2D sky fogged at one fixed distance.
- g_flRotation / g_flHorizonOffset 0 on the team maps read. Combos: D_FOG_TYPE 0..2, D_MIN_ANGULAR_FOG (fog type 2).

## csgo_unlitgeneric.vfx (de_dust2's skybox clouds)

- PS static combo 18 (S_BLEND_MODE=4, S_TWOTEXTURE; radix S_BLEND_MODE x7, S_GRADIENTMODULATION x2, S_TWOTEXTURE x2, ...):
  `g_tColor(uv0) x g_tColor2(uv1) x vertex colour`, fog (g_bFogEnabled) only on alpha.
- VS: vertex colour = `mix(1, instance tint, g_flModelTintAmount) x g_vColorTint`.
- Render states: features file lists target 0..2 One / One, no depth write; D_MBOIT_PASS1 / 2 require S_BLEND_MODE 1
  or 4 (translucent and additive go through MBOIT). VRF decodes the pixel program's per-combo states as defaults and
  _psrs's as null: per-mode factors UNREAD.
- de_dust2's nuke_clouds_002 (Additive, two textures): both white with the cloud in alpha (averages 0.04 and 0.22).
