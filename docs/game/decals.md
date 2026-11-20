# Projected decals: the client's decal record

client_20261105 (the server addresses' build not recorded). Read for the C4's "Scorch" ([c4-shockwave.md](c4-shockwave.md) "The explosion's effects").

## Functions

| Address | Module | What |
|---|---|---|
| 180376e20 | client | builds the decal record from a material (r8) |
| 180c333f0 | client | allocates the 0x50-byte record |
| 18036dd90 | client | reads DecalDepth with default {4, 0, 0, 0} (.rdata 0x181b0b590): overwrites the 16.0 first written at +0x18 (0x180376f7d, checked against the disassembly) |
| 180160c50 | client | r_decals_default_fade_duration read |
| 180cbbf60 | server | UTIL_DecalTrace -> 1803d10a0 -> 18111bfe0 |

## Constants

| Value | What |
|---|---|
| 0x181ff32e0 | server's decal system |
| 0x31415926 | MurmurHash2 seed of CUtlStringToken (lowercased name; tools/re/game/strtoken.py) |

## The record (180376e20)

Defaults written, then the material's attribute container (material vfn 0x38) searched for each attribute by
CUtlStringToken (SIMD compares against 4 copies of a token in .rdata):

| +off | Default | Attribute (token) | Notes |
| --- | --- | --- | --- |
| 0x00 | 64 | DecalWorldWidth (0xcd8fee5d, .rdata 0x181b0b620) | with 0x04: both found, else the mapping size below |
| 0x04 | 64 | DecalWorldHeight (0xc6268b58, immediate at 0x180377344) | |
| 0x08 | 0 | token 0x6dce1bec (.rdata 0x181b0b610) | name unknown |
| 0x0c | 0 | token 0x8cdeab89 | name unknown |
| 0x10 | 1.0 | | unread |
| 0x14 | 0.25 | | unread |
| 0x18 | 16, then 4 | DecalDepth (0xadee4833) | 16.0 written first; 18036dd90's default 4 overwrites it |
| 0x1c | 0 | DecalDepthOffset (0xae65be16) | |
| 0x20 | 0 | DecalDepthVariance (0x5fffc1b2) | |
| 0x24 | 10, then the cvar | DecalFadeDuration (0xd70d77db, .rdata 0x181b0b630) | r_decals_default_fade_duration before the attribute |
| 0x28 | 3, then the cvar | token 0x39e88e9a (.rdata 0x181b0b600): the fade start | r_decals_default_start_fade before the attribute |
| 0x2c | 1.0 | | unread |
| 0x34 | 0 | DecalAlignWithGravityFactor (0x0acd2902) | |
| 0x38 | 0 | token 0x8033177f | name unknown |
| 0x44 | 1.0 | | unread |
| 0x48 / 0x4c | -1 / 0xff | | unread |

## Size without DecalWorldWidth / DecalWorldHeight (0x180377292)

- Material vfn 0xb0(&w, &h, 0, 1, ..) gives the mapping size in texels (the colour texture's); unless 1 x 1 they become
  width and height as floats (cvtdq2ps), in units.
- A 1 x 1 mapping: vfn 0xa8(.., 0x10, ..) ints x [decal system + 0x88] (unread).
- Scorch (scorch1_projected_triplanar.vmat: no size, DecalFadeStartTime 30, DecalFadeDuration 10, F_TRIPLANAR_MAPPING 1,
  F_BLEND_MODE 1): its 128 x 128 texture, so 128 u square, depth 4, offset 0, fading from 30 s over 10 s.

## Unread

- The record's consumer (projection: how DecalDepth / DecalDepthOffset / variance place the box, rotation about the
  normal, +0x10 / +0x14 / +0x2c) and the fade's curve over DecalFadeDuration.
- Names of tokens 0x6dce1bec, 0x8cdeab89, 0x8033177f; DecalSizeVariance isn't read here.
- r_decals_* cvars' defaults (r_decals_default_start_fade, r_decals_default_fade_duration, ...).
