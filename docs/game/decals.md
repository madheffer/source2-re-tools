# Projected decals: the client's decal record (client.dll 2026-11-05)

Read 2026-11-16 ("c4-blast") for the C4's "Scorch" (docs/game/c4-shockwave.md "The explosion's effects"). The server
side is UTIL_DecalTrace (server 180cbbf60 -> 1803d10a0 -> 18111bfe0, the decal system 0x181ff32e0). The bullet holes'
decals (bake/ImpactBake.cs, world/decals.js) read the same material attributes.

## The record (180376e20)

Called with a material (r8); 0x50 bytes allocated (180c333f0), defaults written, then the material's attribute
container (the material's vfn 0x38) searched for each attribute by its CUtlStringToken (MurmurHash2 seed 0x31415926 of
the lowercased name: tools/re/game/strtoken.py; the SIMD compares against 4 copies of a token in .rdata):

| +off | default | attribute (token) | notes |
| --- | --- | --- | --- |
| 0x00 | 64 | DecalWorldWidth (0xcd8fee5d, .rdata 0x181b0b620) | with 0x04: both found, else the mapping size below |
| 0x04 | 64 | DecalWorldHeight (0xc6268b58, immediate at 0x180377344) | |
| 0x08 | 0 | token 0x6dce1bec (.rdata 0x181b0b610) | name unknown |
| 0x0c | 0 | token 0x8cdeab89 | name unknown |
| 0x10 | 1.0 | | unread |
| 0x14 | 0.25 | | unread |
| 0x18 | 4 | DecalDepth (0xadee4833) | 18036dd90 with the default {4, 0, 0, 0} (.rdata 0x181b0b590) overwrites the 16 first written |
| 0x1c | 0 | DecalDepthOffset (0xae65be16) | |
| 0x20 | 0 | DecalDepthVariance (0x5fffc1b2) | |
| 0x24 | 10, then the cvar | DecalFadeDuration (0xd70d77db, .rdata 0x181b0b630) | r_decals_default_fade_duration (180160c50) before the attribute |
| 0x28 | 3, then the cvar | token 0x39e88e9a (.rdata 0x181b0b600): the fade start | r_decals_default_start_fade before the attribute |
| 0x2c | 1.0 | | unread |
| 0x34 | 0 | DecalAlignWithGravityFactor (0x0acd2902) | |
| 0x38 | 0 | token 0x8033177f | name unknown |
| 0x44 | 1.0 | | unread |
| 0x48 / 0x4c | -1 / 0xff | | unread |

**The size without DecalWorldWidth and DecalWorldHeight** (0x180377292): the material's vfn 0xb0(&w, &h, 0, 1, ..)
gives its mapping size in texels (the colour texture's); unless it is 1 x 1 they become the width and height as
floats (cvtdq2ps), in units. A 1 x 1 mapping: vfn 0xa8(.., 0x10, ..) ints x [decal system + 0x88] (unread). The Scorch
(scorch1_projected_triplanar.vmat: no size, DecalFadeStartTime 30, DecalFadeDuration 10, F_TRIPLANAR_MAPPING 1,
F_BLEND_MODE 1) is therefore its 128 x 128 texture: 128 u square, depth 4, offset 0, fading from 30 s over 10 s.

The bake (ImpactBake.Material, shared by C4Bake) writes these defaults now (DecalDepth 4, DecalDepthOffset 0; it had
12 / -4). The shared ze-fx/impacts.json is rebaked with them (2026-11-16 "c4-rebake": 59 offsets -4 -> 0, 46 depths 12 -> 4,
nothing else changed; world/decals.js reads both from it).

## Unread

- Who consumes the record (the projection: how DecalDepth / DecalDepthOffset / the variance place the box, the
  rotation about the normal, +0x10 / +0x14 / +0x2c), and the fade's curve over DecalFadeDuration (world/decals.js:
  linear).
- The names of tokens 0x6dce1bec, 0x8cdeab89, 0x8033177f; DecalSizeVariance isn't read here.
- r_decals_* cvars' defaults (r_decals_default_start_fade, r_decals_default_fade_duration, ...).
