# The main menu scene's look (de_dust2_vanity's post volume, the agents' textures)

No DLL: CS2's files game/csgo/pak01_dir.vpk and maps/de_dust2_vanity.vpk (read with VRF / kv3dump). The scene's entities and animations: menu-anim.md.

## Post volumes

de_dust2_vanity has 19 `post_processing_volume`s, every one `master true`, spawnflags 4097, fadetime 1:

| targetname | postprocessing | startdisabled | min / max exposure |
|---|---|---|---|
| `post_vanity` | lighting/postprocessing/de_dust2_prefab/de_dust2_vanity.vpost | false | 1.0 / 1.0 |
| `pet_post_normal` | the same de_dust2_vanity.vpost | true | 0.8 / 1.2 |
| `pet_post_sepia`, `_bloom`, `_warm`, `_cool`, `_moonlight`, `_silvertone`, `_psychedelic`, `_crisp`, `_exposure_up` / `_down`, `_vibrance_up` / `_down`, `_contrast_up` / `_down`, `_saturation_up` / `_down`, `_bw` | lighting/postprocessing/effects/pet_*.vpost (the pet photo's filters) | true | 0.8 / 1.2 |

The menu's grade is `post_vanity`, the one enabled master. (The last master in the lump is `pet_post_bw`, startdisabled.) Its min / max exposure 1.0 / 1.0: fixed exposure 1.

## de_dust2_vanity.vpost

`lighting/postprocessing/de_dust2_prefab/de_dust2_vanity.vpost_c` in pak01 (not the map's vpk), 133,395 bytes.

| Block | Values |
|---|---|
| `m_bHasTonemapParams true` | m_flExposureBias 0, m_flShoulderStrength 0, m_flLinearStrength 0.001, m_flLinearAngle 0.001, m_flToeStrength 1, m_flToeNum 1, m_flToeDenom 1, m_flWhitePoint 1.498557; m_flLuminanceSource 0, m_flExposureBiasShadows / Highlights 0, m_flMin / MaxShadowLum 0 / 0.5, m_flMin / MaxHighlightLum 2 / 8 |
| `m_bHasBloomParams true` | BLOOM_BLEND_SCREEN, m_flBloomStrength 0, m_flScreenBloomStrength 0.0964, m_flBlurBloomStrength 0, threshold 8.433, threshold width 9.999, skybox 1, start value 1, blur weights 0.11108 x 4 + 0.555679, tints all white |
| `m_bHasVignetteParams false`, `m_bHasLocalContrastParams false` | |
| `m_bHasColorCorrection true` | `m_nColorCorrectionVolumeDim 32` (32^3 RGBA8 lookup, 131,072 bytes) |

- With shoulder 0 and toe 1 / 1 / 1 the curve is f(x) = (1e-6 x + 1) / (0.001 x + 1) - 1 ~ -0.001 x; divided by f(2^1.4986 = 2.826) it is ~ 2.8 x / 2.826: near-linear, clipped at x ~ 1.
- CS2's default curve (no vpost): shoulder 0.15, linear 0.5, angle 0.1, toe 0.2, 0.02 / 0.3, white point 4.
- Measured, the same view at 1360 x 765, default curve -> the vanity's: luma std 27.0 -> 41.4, mean saturation 0.104 -> 0.144, Laplacian variance 59.8 -> 115.1, mean luma 160 -> 189.5.
- Other maps whose volumes name stock vposts in pak01 (each a tone curve and a 32^3 lookup): de_dust2 (de_dust2_prefab.vpost), de_inferno (de_inferno_prefab.vpost), de_mirage (de_mirage.vpost), ze_atix_panic_2017_p (de_nuke_prefab/de_nuke_post.vpost).

## The agents' textures

pak01 characters/models/<agent>/materials, .vtex_c DATA block: version u16, flags u16, reflectivity float4, width u16 @20, height u16 @22, depth u16, format u8 @26, mip count u8 @27.

| texture | CS2 | a 1024 cap |
|---|---|---|
| ctm_sas_body_color / _normal / _ao / _metal | 2048 x 2048, 10 mips | 1024 x 1024 |
| ctm_sas_legs_color / _normal / _cloth / _ao | 2048 x 1024, 9 mips | 1024 x 512 |
| sleeve_sas_* | 1024 x 2048 | 512 x 1024 |
| ctm_sas_head_gasmask_* | 1024 x 1024 | 1024 x 1024 |
| ctm_sas_lenses_ao | 128 x 128 | 128 x 128 |

In the menu: vanity_character is 209 units from cam_default at a 30 degree vertical FOV: ~6.8 screen px a unit at 765 px tall (12 at 1350), ~490 px for the body; a 1024 body texture gives ~13 texels a unit on the torso.

## cam_default

`point_camera_vertical_fov` `[PR#]cam_default`: origin (1305.92, 725.60, 28.76), angles (-1, 75.3465, 0), verticalfov 30, znear 4, zfar 10000, aspectratio 1.1641, dof_enabled true, dof_near_blurry 100, dof_near_crisp 210, dof_far_crisp 210, dof_far_blurry 2000, dof_tilt_to_ground 0.5. Distances from it: vanity_character 209 (on the crisp plane), _1 380, _2 408, _3 327, _4 285.

DoF: team-intro.md "Depth of field" (circle of confusion, dof_tilt_to_ground's lens plane, dof2's gather over Dof2CBParams' taps, 48 by default: at most 5 pixels of blur at any resolution; after the translucents, before the bloom).

## Unread

- csgo_effects' depth feather curve (the haze cards).
