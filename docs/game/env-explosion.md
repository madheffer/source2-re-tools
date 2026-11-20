# env_explosion's effect (CMsgTEExplosion)

server_20261105, client_20261015 (fx_explosion.cpp). scripts/explosion_types.vdata,
scripts/surfaceproperties_explosion_debris_effects.txt. The damage side (RadiusDamage): radius.md.

## Functions

| Address | Module | What |
|---|---|---|
| 180d74170 -> 180dac170 | server | InputExplode: packs the entity into the maker's struct |
| 1803d6f50 / 1803d6de0 | server | GetAbsOrigin / angles |
| 180d98c70 | server | the explosion maker (struct p) |
| 1803d83c0 | server | p+0x20's vfn: returns (0, 0, -1) always |
| 180250e50 | server | UTIL_TraceLine |
| 181120f40 | server | fills CMsgTEExplosion |
| 181121100 | server | the debris normal |
| 180c83dd0 / 181121190 | server | send to the PAS filter |
| 180fb9d90 -> 180df0300 | server | the damage |
| 1800d1950 | server | MakeGlobalSymbol("custom") -> 182182da0 |
| 180c4f310 | server | DispatchParticleEffect(effect, origin, angles) |
| 1814722c0 | server | VectorAngles |
| 180cbbf60 | server | applies the type's decal (unread) |
| 180b867f0 | client | C_BaseExplosionEffect::Create (vtable 0x181c66910) |
| 180b958d0 | client | ProbeExplosion(origin, magnitude, out normal +0x14, out scale +0x20) |
| 180b99e20 | client | one probe line (18022fee0, interacts-with 1, group 3) |
| 18015a140 | client | normalise |
| 180b86910 | client | vfn 0x08: the sound |
| 180b86af0 | client | vfn 0x10: the particle (radius) |
| 1809d4ec0 | client | create the particle |
| 181742a00 | client | VectorAngles |
| 180a11f30 | client | set CP |
| 180b86d00 | client | vfn 0x18: the debris |
| 180b86e80 | client | vfn 0x30(0): the dynamic light (vfns 0x20 / 0x28 empty) |
| 180ae5370 | client | CDynamicLightManager alloc (manager 18255c048, game system 1800c8f50, vtable 0x181c45438: slots 180ad13c0, 180ad14c0, 180ad1510) |
| 180ae6a90 | client | C_DynamicLight: records carry a scene light at +0x48 (freed through 18279cf10 vfn 0x80) |

## Fields

### The maker's struct (180dac170)

| Struct | From (CEnvExplosion) | Field |
|---|---|---|
| +0x00 | GetAbsOrigin | origin |
| +0x0c | 1803d6de0 | angles |
| +0x18 | +0x3e4 handle | owner |
| +0x20 | +0x864 m_hInflictor (else the explosion) | inflictor |
| +0x30 | +0x850 m_iMagnitude (int -> float) | magnitude |
| +0x34 | +0x854 m_flPlayerDamage | player damage |
| +0x38 | +0x860 m_flDamageForce | force |
| +0x3c | +0x858 m_iRadiusOverride (int -> float) | radius override |
| +0x40 | +0x85c m_flInnerRadius | inner radius |
| +0x44 | +0x360 | spawnflags |
| +0x48 | +0x8a0 m_hEntityIgnore | ignored entity |
| +0x50 / +0x54 | +0x88c / +0x890 m_iClassIgnore / 2 | ignored classes |
| +0x58 | +0x870 | explosion type (global symbol) |
| +0x68 / +0x6c | +0x868 m_iCustomDamageType / +0x86c m_bHasCustomDamageType | |
| +0x70 | +0x878 m_iszCustomEffectName | explosion_custom_effect |
| +0x78 | +0x880 m_iszCustomSoundName | explosion_custom_sound |
| +0x80 | +0x86d m_bCreateDebris | |

Other: +0x888 m_bSuppressParticleImpulse, +0x898 m_iszEntityIgnoreName.

### CMsgTEExplosion

| Offset | Field |
|---|---|
| +0x40 | has-bits (1 sound) |
| +0x48 | sound name (custom, else the type's m_SoundName) |
| +0x50 | origin sub-message (has-bit 1) |
| +0x58 | normal (default (0, 0, 1)) |
| +0x60 | debris hit point sub-message |
| +0x68 | flags |
| +0x6c | radius (int) |
| +0x70 | magnitude (int) |
| +0x74 / +0x75 | affect ragdolls / create debris |
| +0x78 | type (fallback) |
| +0x7c | hit surface hash (0x75de364e without one) |
| +0x80 | type name token (CUtlStringToken, has-bit 0x800) |

Client effect: origin +0x8, normal +0x14, scale +0x20, flags +0x24, type +0x28. CExplosionTypeData: +0x10
m_ParticleEffect, +0xf8 m_DecalType.

## Constants

| Value | What |
|---|---|
| 0x1b001, group 4 | maker's line: interacts-with (world only), p+0x20 ignored |
| 8 / 40 | line from origin + dir x 8 to that - dir x 40 |
| 24 | message origin = end + normal x 24 on a hit |
| 2.5 | radius = magnitude x 2.5 without an override |
| flags 4 | TE_EXPLFLAG_NOSOUND: `(spawnflags >> 4) & 4` (spawnflag 64) |
| flags 2 | dynamic light (left out with spawnflag 128) |
| spawnflag 1 / 16 / 0x2000 / 0x8000 | no damage / no decal / damage info flag 0x1000 / custom effect at the entity's angles |
| 0x6f76f648 / 0xb201eb35 | sound parameters radius / magnitude (when both > 0) |
| 182542598 / 1825425a8 | client symbols "none" / "custom" |
| dlight | +0x10 = 255.0 radius, colour 255, 220, 128 (+0x14..0x16), +0x1c = 200.0 decay, die now + 0.1 |

## The maker 180d98c70

1. dir = -(p+0x20 vfn 1803d83c0) = (0, 0, 1). Line from origin + dir x 8 to that - dir x 40 (8 u above to 32 below).
2. Message origin = p's; a hit (fraction != 1): end + normal x 24.
3. Unless spawnflag 16: the type's decal taken into the trace's record (only "ice" has one).
4. flags; radius = p+0x3c, else magnitude x 2.5.
5. 181120f40: origin, flags, radius, magnitude, sound, type token, normal, affect ragdolls.
6. m_bCreateDebris and a hit: has-bits 0x108, +0x75 = 1, the hit point into +0x60, surface hash +0x7c, has-bit 0x400,
   the normal (181121100).
7. Sent to the PAS at the origin. Unless spawnflag 1, the damage.
8. Type "custom" only (p+0x58 == 182182da0) with a custom effect: 180c4f310(effect, origin, VectorAngles(hit normal)),
   or the entity's angles (p+0x0c) with spawnflag 0x8000.

## Client: C_BaseExplosionEffect

1. Create 180b867f0: origin, flags = msg+0x68, type = FindGlobalSymbolByHash(msg+0x80) (has-bit 0x800; else msg+0x78).
2. ProbeExplosion 180b958d0: six lines along +-x, +-y, +-z of length magnitude; each k = 1 - fraction, adds -axis x k;
   normal = sum, scale = 1 + sum of k. Zero sum: normal (0, 0, 1), scale 2. Normal normalised.
3. Sound 180b86910: msg+0x48 unless flags & 4, with the radius / magnitude parameters.
4. Particle 180b86af0: "none" / "custom" draw none; empty type = "default"; the type's m_ParticleEffect, CP0 at the
   origin with the angles of the probe normal, CP1 = (radius, scale, 1.0).
5. Debris 180b86d00: has-bit 0x100 and msg+0x75: the surface (msg+0x7c) in CExplosionDebrisEffectsManager, its effect
   at msg+0x60 facing msg+0x58. CS2's file lists no surface (`SurfacePropertiesList = []`): nothing draws.
6. Dynamic light 180b86e80, flags & 2.

## The types (explosion_types.vdata)

Every m_ParticleEffect is one of particles/entity/env_explosion/explosion_*.vpcf (core's pak01, not csgo's), all ten
the same placeholder: 10 sprites of textures/particle/largesmoke.vtex, colour (112, 39, 0), radius 10..20 growing 0.125
-> 2.0, life 0.01..0.1 s, 100 u/s along the CP's local Y. molotov, fireworks, shrapnel and ice use explosion_default;
none and custom have no fields. ze_resident_evil_3's three custom effects ride type "" and draw nothing.

## Unread

- How CDynamicLightManager's records become scene lights (frame hook, brightness of a radius-255 colour-255,220,128
  dlight).
- How 180cbbf60 applies the type's decal (Ice_Explosion_Decal).
