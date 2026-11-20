# Texture detail and the lightmaps' size (video settings)

client.dll (2026-11-19, 39,141,528 bytes), worldrenderer.dll (2026-11-18, 2,029,720 bytes). pak01 `cfg/video_defaults_0..3.txt`.

## Functions

| Address | Module | What |
|---|---|---|
| 0x180deae90 | client | preset 0 (Low) builder of `setting.<convar>` values |
| 0x180deb340 | client | preset 1 (Medium) builder |
| 0x180dea9e0 | client | preset 2 (High) builder |
| 0x180deb7f0 | client | preset 3 (Very High) builder |
| 0x180ddf1e0 | client | the settings' save / load (reads `setting.videocfg_texture_detail`) |
| 0x180df6fd0, 0x180e04200, 0x180e05fc4, 0x180e06617, 0x180e0a790 | client | other readers of `setting.videocfg_texture_detail` (not read) |
| 0x1801068d0 / 0x1801276f0 | client | ConVarRef inits of `r_lightmap_size` (refs 0x1825bbdd0 / 0x1825e79b0; readers not found by a RIP-relative scan) |
| 0x1800016c0 | worldrenderer | `r_lightmap_size` ConVar registration (static init) |
| 0x180001780 | worldrenderer | `r_lightmap_size_directional_irradiance` registration |
| 0x180001840 | worldrenderer | `r_lightmap_set` registration |
| 0x1800fc6a0 | worldrenderer | the ConVar register call |

The preset builders: one function a preset, KeyValues SetString of a literal (the same family as [shadows.md](shadows.md)'s 180df13a0 ..).

## Constants

| Value | What |
|---|---|
| 0x181cbcfc8 | string `setting.r_texture_stream_max_resolution` (client) |
| 0x181cbd570 | string `setting.videocfg_texture_detail` (client) |
| 0x181cbe2f0 | string `r_lightmap_size` (client's only one) |
| `r_lightmap_size` int, default 65536 | "Maximum lightmap resolution." (`mov dword [rsp+0x37], 0x10000`; flags r8d 3 as its neighbours) |
| `r_lightmap_size_directional_irradiance`, default -1 | "Maximum lightmap resolution for directional_irradiance channel. -1 = use value of r_lightmap_size" |
| `r_lightmap_set` | "Lightmap set to use, only works on map load" |

## Presets

| Preset | builder | setting.shaderquality | setting.r_texture_stream_max_resolution | setting.videocfg_texture_detail | r_texturefilteringquality |
|---|---|---|---|---|---|
| 0 Low | 0x180deae90 | 0 | 1024 | 0 | 0 |
| 1 Medium | 0x180deb340 | 0 | 2048 | 1 | 1 |
| 2 High | 0x180dea9e0 | 1 | 8192 | 2 | 3 |
| 3 Very High | 0x180deb7f0 | 1 | 8192 | 2 | 5 |

- Texture detail Low / Medium / High caps the streamed textures' top mip at 1024 / 2048 / 8192 (the largest resolution a streamed texture loads).
- No preset writes `r_lightmap_size`: client.dll has no `setting.r_lightmap_size` string; video_defaults_*.txt don't name it. A map's lightmaps draw at their baked size on every preset (de_dust2: 8192^2 irradiance and shadow mask, 4096^2 directional irradiance).

## Unread

- Which textures the r_texture_stream_max_resolution cap applies to (the world's lightmaps or not): the streamer's reader (scenesystem / materialsystem2).
