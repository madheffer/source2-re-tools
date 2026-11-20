# env_explosion's effect (CMsgTEExplosion)

How a map's env_explosion looks in CS2: server.dll builds a temp-entity message, client.dll's C_BaseExplosionEffect
plays it. The damage side (RadiusDamage) is radius.md / FEATURES "env_explosion". Read 2026-11-16 (session
"nade-vis") in server_20261105.dll and client_20261015.dll. Ported: web/src/cs2web/client/fx/env-explosion.js (+ its
test), the request in web/src/world/entities/classes/triggers.js, the types baked by `lasers-bake --impacts`
(impacts.json `explosions`).

## server.dll

**InputExplode 180d74170 -> 180dac170** packs the entity into a struct for the explosion maker (offsets in the
struct; CEnvExplosion's schema offsets from tools/re/game/schema.py):

| struct | from | field |
|---|---|---|
| +0x00 | GetAbsOrigin 1803d6f50 | origin |
| +0x0c | 1803d6de0 | angles |
| +0x18 | +0x3e4 handle | owner |
| +0x20 | +0x864 m_hInflictor (else the explosion itself) | inflictor |
| +0x30 | +0x850 m_iMagnitude (int -> float) | magnitude |
| +0x34 | +0x854 m_flPlayerDamage | player damage |
| +0x38 | +0x860 m_flDamageForce | force |
| +0x3c | +0x858 m_iRadiusOverride (int -> float) | radius override |
| +0x40 | +0x85c m_flInnerRadius | inner radius |
| +0x44 | +0x360 | spawnflags |
| +0x48 | +0x8a0 m_hEntityIgnore | ignored entity |
| +0x50 / +0x54 | +0x88c / +0x890 m_iClassIgnore / 2 | ignored classes |
| +0x58 | +0x870 | explosion type (a global symbol) |
| +0x68 / +0x6c | +0x868 m_iCustomDamageType / +0x86c m_bHasCustomDamageType | |
| +0x70 | +0x878 m_iszCustomEffectName | explosion_custom_effect |
| +0x78 | +0x880 m_iszCustomSoundName | explosion_custom_sound |
| +0x80 | +0x86d m_bCreateDebris | |

Other schema fields: +0x888 m_bSuppressParticleImpulse, +0x898 m_iszEntityIgnoreName.

**The explosion maker 180d98c70** (struct p):
- dir = -(vfn 1803d83c0 of p+0x20), and that vfn returns (0, 0, -1) always: dir = (0, 0, 1). A line (UTIL_TraceLine
  180250e50, interacts-with 0x1b001, group 4, p+0x20 ignored, the world only) from origin + dir x 8 to that point -
  dir x 40 (8 u above to 32 u below).
- The message's origin: p's origin; where the line hit (fraction != 1): end + normal x 24.
- Unless spawnflag 16: the type's decal (CExplosionTypeData +0xf8, m_DecalType) taken into the trace's record (how
  it is applied: unread; only "ice" has one).
- flags = (spawnflags >> 4) & 4 (TE_EXPLFLAG_NOSOUND from spawnflag 64) | 2 (the dynamic light), the 2 left out with
  spawnflag 128.
- radius = p+0x3c, else magnitude x 2.5 (as the damage).
- **181120f40** fills CMsgTEExplosion: origin (+0x50 sub-message, has-bit 1), flags +0x68, radius +0x6c (int),
  magnitude +0x70 (int), the sound name +0x48 (the custom sound, else the type's m_SoundName; has-bit 1 of +0x40), the
  type's name token +0x80 (CUtlStringToken, has-bit 0x800), normal +0x58 (default (0, 0, 1)), affect ragdolls +0x74.
- m_bCreateDebris and a hit: has-bits 0x108, +0x75 = 1, the hit point into the +0x60 sub-message, the hit surface's
  hash +0x7c (0x75de364e without one), has-bit 0x400, the normal (181121100).
- Sent (180c83dd0 / 181121190) to the PAS filter at the origin. Then, unless spawnflag 1, the damage (180fb9d90 ->
  180df0300; spawnflag 0x2000 sets info flag 0x1000).
- Type **"custom"** only (p+0x58 == the symbol at 182182da0, made by 1800d1950 = MakeGlobalSymbol("custom")) and a
  custom effect: DispatchParticleEffect 180c4f310(effect, the message's origin, angles) with angles VectorAngles
  (1814722c0) of the line's hit normal, or the entity's angles (p+0x0c) with spawnflag 0x8000.

## client.dll

**C_BaseExplosionEffect** (vtable 0x181c66910; fx_explosion.cpp). **Create 180b867f0** (from the message):
origin +0x8, flags +0x24 = msg+0x68, the type +0x28 = FindGlobalSymbolByHash(msg+0x80) (has-bit 0x800; else from
msg+0x78), then:
- **ProbeExplosion 180b958d0**(origin, magnitude as float, out normal +0x14, out scale +0x20): six lines from the origin
  along (1,0,0), (-1,0,0), (0,1,0), (0,-1,0), (0,0,1), (0,0,-1) of length magnitude (**180b99e20**: 18022fee0,
  interacts-with 1, group 3); each returns k = 1 - fraction and turns its axis into -axis x k; normal = sum, scale =
  1 + sum of k. A zero sum: normal (0, 0, 1), scale 2. The normal normalised (18015a140).
- vfn 0x08 **180b86910** the sound: the name (msg+0x48) unless flags & 4, with parameters 0x6f76f648 = radius,
  0xb201eb35 = magnitude when both > 0.
- vfn 0x10 **180b86af0**(radius as float) the particle: type "none" / "custom" (182542598 / 1825425a8) draw none; an
  empty type is "default"; the type's CExplosionTypeData (+0x10 m_ParticleEffect) created (1809d4ec0), CP0 at the
  origin with the angles of the probe normal (181742a00), CP1 = (radius, scale, 1.0) (180a11f30), started.
- vfn 0x18 **180b86d00** the debris: has-bit 0x100 and msg+0x75: the surface (msg+0x7c) looked up in
  CExplosionDebrisEffectsManager (scripts/surfaceproperties_explosion_debris_effects.txt), its effect at msg+0x60 facing
  msg+0x58. **CS2's file lists no surface** (`SurfacePropertiesList = []`): nothing draws.
- vfn 0x30(0) **180b86e80** the dynamic light, flags & 2: CDynamicLightManager (18255c048; game system 1800c8f50)
  180ae5370 alloc, at the origin: +0x10 = 255.0 (radius), colour bytes 255, 220, 128 (+0x14..0x16), +0x1c = 200.0
  (decay), die time = now + 0.1. vfns 0x20 / 0x28 are empty.

## The types (scripts/explosion_types.vdata, CExplosionTypeData)

Every type's m_ParticleEffect is one of particles/entity/env_explosion/explosion_*.vpcf (in core's pak01, not
csgo's), and all ten are the same placeholder system: 10 sprites of textures/particle/largesmoke.vtex, colour
(112, 39, 0), radius 10..20 growing 0.125 -> 2.0, life 0.01..0.1 s, 100 u/s along the CP's local Y. molotov,
fireworks, shrapnel and ice use explosion_default; none and custom have no fields.

## Not ported / unread

- The dynamic light: how CDynamicLightManager's records become scene lights (its frame hook, the brightness of a
  radius-255 colour-255,220,128 dlight in CS2's lighting) is unread. The manager's vtable 0x181c45438 has only three
  non-trivial slots (180ad13c0, 180ad14c0, 180ad1510); C_DynamicLight 180ae6a90 shows records carry a scene light at
  +0x48 (freed through 18279cf10 vfn 0x80).
- The type's decal (spawnflag 16 off): how 180cbbf60 applies it; Ice_Explosion_Decal isn't baked.
- The sound's radius / magnitude parameters (0x6f76f648, 0xb201eb35): not passed to our sound events.
- Our map bake doesn't collect explosion_custom_effect (no baked map has a "custom" type: ze_resident_evil_3's three
  custom effects ride type "" and draw nothing in CS2 either).
