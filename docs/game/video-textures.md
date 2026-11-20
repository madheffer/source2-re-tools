# Texture detail and the lightmaps' size (CS2's video settings)

Read 2026-11-20 (branch agent/mapbake-p0done) from the installed client.dll (2026-11-19, 39,141,528 bytes) and
worldrenderer.dll (2026-11-18, 2,029,720 bytes) with source2-compiler tools/re (strxref.py, xref.py --dis,
disasm.py): ReVa was down. Addresses are these builds'.

## Texture detail (Settings > Video > Advanced: `videocfg_texture_detail`)

pak01 `cfg/video_defaults_0..3.txt` (the four presets Low .. Very High) set `setting.videocfg_texture_detail` 0 / 1 / 2 /
2 (and `r_texturefilteringquality` 0 / 1 / 3 / 5). client.dll builds each preset's table of `setting.<convar>` values
in one function a preset (KeyValues SetString of a literal; the same family as shadows.md's 180df13a0 ..):

| preset builder (client) | setting.shaderquality | setting.r_texture_stream_max_resolution | setting.videocfg_texture_detail |
|---|---|---|---|
| 0x180deae90 | 0 | 1024 | 0 |
| 0x180deb340 | 0 | 2048 | 1 |
| 0x180dea9e0 | 1 | 8192 | 2 |
| 0x180deb7f0 | 1 | 8192 | 2 |

So texture detail Low / Medium / High caps the streamed textures' top mip at 1024 / 2048 / 8192 (the convar's name:
the largest resolution a streamed texture loads). The strings: 0x181cbcfc8 `setting.r_texture_stream_max_resolution`,
0x181cbd570 `setting.videocfg_texture_detail` (also read by 0x180ddf1e0, the settings' save / load, and 0x180df6fd0,
0x180e04200, 0x180e05fc4, 0x180e06617, 0x180e0a790: not read). Which textures the cap applies to (the world's
lightmaps or not) is not read: TODO(trace) the streamer's reader of r_texture_stream_max_resolution (scenesystem /
materialsystem2).

Ours: world/cs2mat (main.js matOpts.maxSide) caps the CS2 texture blocks' top mip at these three values.

## The lightmaps' size: `r_lightmap_size`

worldrenderer.dll defines it (its ConVar registration 0x1800016c0, called from the module's static init):

- `r_lightmap_size`, int, "Maximum lightmap resolution.", default **65536** (`mov dword [rsp+0x37], 0x10000` before
  the register call 0x1800fc6a0; flags r8d 3 as its neighbours).
- `r_lightmap_size_directional_irradiance` (0x180001780), "Maximum lightmap resolution for directional_irradiance
  channel. -1 = use value of r_lightmap_size", default **-1**.
- `r_lightmap_set` (0x180001840): "Lightmap set to use, only works on map load".

No video preset writes it: client.dll has no `setting.r_lightmap_size` string (its one `r_lightmap_size` string,
0x181cbe2f0, is two ConVarRef inits, 0x1801068d0 / 0x1801276f0, refs at 0x1825bbdd0 / 0x1825e79b0, readers not
found by a RIP-relative scan), and pak01's video_defaults_*.txt don't name it. So CS2 draws a map's lightmaps at their
baked size on every preset (de_dust2: 8192^2 irradiance and shadow mask, 4096^2 directional irradiance).

Ours: Medium and High load the full lightmaps (1:1). Low loads the q/low tier (1024^2 PNG / WebP, lasers-bake --tiers)
on every GPU: a stand-in, not CS2's (it is also what a GPU without BC6H / BC7, a phone, can take). It costs Low the
thin baked shadows (MAP_SHOTS item 12) and saves ~120 MB of GPU memory on de_dust2 (CLIENT_PERF item 106).
