# CS:GO's steam jets, sprite trails and precipitation

CS:GO legacy (32-bit, image base 0x10000000): `csgo/bin/client.dll` (Ghidra `/client.dll.3`), `csgo/bin/server.dll`
(`/csgo_server_legacy.dll`), `bin/engine.dll` (`/engine.dll`). Source SDK names (c_steamjet.cpp, c_spritetrail.cpp,
c_effects.cpp, beamsegdraw.cpp, raytrace.cpp, the particle library); every number from the binary. Data: CS:GO's
particles/rain_fx.pcf.

## Functions

| Address | Module | What |
|---|---|---|
| 0x10629060 | server | CSteamJet::Spawn |
| 0x107ab700 | client | C_SteamJet::Start |
| 0x107ab7c0 | client | C_SteamJet::Update |
| 0x107ac160 | client | C_SteamJet::SimulateParticles |
| 0x107ac270 | client | C_SteamJet::UpdateLightingRamp |
| 0x107abea0 | client | C_SteamJet::RenderParticles |
| 0x107abc20 | client | the unrolled quad (type 1) |
| 0x1022f980 | client | the rolled quad |
| 0x101a3f80 | client | before the quad: the view transform and the alpha (unread) |
| 0x100b6160 | engine | IVEngineClient::GetLightForPoint (CEngineClient vtable 0x1047d850 slot 1) |
| 0x100b7210 | engine | slot 72 |
| 0x10247b80 | engine | ComputeLighting (no normal) |
| 0x10246ea0 | engine | LightcacheGetDynamic: ambient cube and local lights |
| 0x10243a30 / 0x101391d0 / 0x10244230 | engine | local light falloff / (fold) / add into the cube |
| 0x10368f00 | client | C_SpriteTrail::UpdateTrail |
| 0x10368ca0 / 0x10368b80 | client | render bounds (0x10368b80 walks the ring: unread) |
| 0x103690e0 | client | C_SpriteTrail::DrawModel |
| 0x109a94c0 | client | CBeamSegDraw::Start (unread) |
| 0x109a9c50 | client | CBeamSegDraw::NextSeg |
| 0x109a9620 | client | CBeamSegDraw::SpecifySeg |
| 0x10369610 / 0x103697a0 / 0x103698b0 | client | a neighbour class's ctor / dtor / reset (unread) |
| 0x10796110 | client | CClient_Precipitation::Precache |
| 0x10796430 | client | OnDataChanged |
| 0x10798a30 | client | Simulate |
| 0x10799220 | client | InitializeParticlePrecip |
| 0x10798ba0 | client | UpdateParticlePrecip |
| 0x107998b0 | client | DispatchInnerParticlePrecip |
| 0x107996a0 | client | DispatchOuterParticlePrecip |
| 0x10799600 | client | DestroyInnerParticlePrecip |
| 0x10797f60 | client | old ash type's emitter (`effects/fleck_ash1..3`, `effects/ember_swirling001`; unread) |
| 0x10799d20 / 0x1079a580 | client | old types' draw / a ConVar read (unread) |
| 0x10994260 | client | RayTracingEnvironment::Trace4Rays (splits a packet whose directions differ in sign) |
| 0x10995b30 | client | the packet trace |
| 0x109960d0 | client | AddTriangle (stores the three vertices) |
| 0x10994ee0 | client | SetupAccelerationStructure (unread: the normal's cross product, the k-d tree) |
| 0x109616c0 | client | C_INIT_RtEnvCull::InitNewParticlesScalar (vtable 0x10d0765c) |
| 0x10961b0f | client | its normal-flag test |
| 0x1095fed0 | client | C_INIT_LifespanFromVelocity::InitNewParticlesScalar (vtable 0x10d08c90) |
| 0x10960650 / 0x10961b20 | client | their InitNewParticlesBlock (SIMD twins, unread) |
| 0x10975cb0 | client | C_OP_SetControlPointToImpactPoint::Operate (vtable 0x10d0d1e8; unread) |

## Fields

| Offset | Field |
|---|---|
| C_SteamJet (vtable 0x10cd3e80) +700 x 4 | origin (last-ramp test) |
| C_SteamJet +0x2ba bit 0 | spawnflag 1 emissive |
| C_SteamJet +0x2c5 x 4 | five ramp colours, 12 bytes each |
| C_SpriteTrail (vtable 0x10be7a1c) +0x1040 / +0x1044 | ring first index / count (64 points, index & 0x3f) |
| CBeamSegDraw +0x200 | last segment: position, colour bytes +0x210, texture coordinate +0x214, width +0x218 |
| CBeamSegDraw +0x220 / +0x224 | segment count / drawn |
| CBeamSegDraw +0x228 / +0x238 | last normal / camera origin |
| CClient_Precipitation (vtable 0x10ccf358, networkable 0x10ccf660) +0xa00 | m_nPrecipType |
| +0xa08 | m_flDensity |
| +0xa64 | inner distance |
| +0xa68 / +0xa6c / +0xa70 | system names (inner near, inner far, outer) |
| +0xa7c / +0xa88 / +0xa94 | system handles: inner near / inner far / outer |
| +0xa98 / +0xa9c | trace timer interval / left |
| ray-trace triangle (48 bytes) | N +0, D +0xc, id +0x10, two edge equations from +0x14, projection axes' bytes +0x2c / +0x2d |
| C_INIT_RtEnvCull +0x5c / +0x68 / +0x74 | test direction / cull normal / environment number |
| C_INIT_RtEnvCull +0x78 / +0x79 / +0x7a | use velocity / cull on miss / adjust lifespan |
| C_INIT_LifespanFromVelocity +0x5c / +0x68 / +0x6c / +0x70 | bias distance / trace offset / maximum trace length / trace recycle tolerance |
| C_INIT_LifespanFromVelocity +0x74 / +0x7c / +0x100 | collision group / maximum points to cache / trace mask |
| trace cache block (parent collection) +0x1ec0 / +0x1ec4 / +0x1ed8 | count / next index / valid flags (starts, ends, hit points, normals) |

## Constants

| Value | What |
|---|---|
| `particle/particle_smokegrenade` / `sprites/heatwave` | g_Mat_DustPuff[0] / type 1 (heat wave) |
| 0.1 | lighting ramp skip (origin and angles within) |
| 0.25 i | ramp sample i at origin + forward x (Speed x m_Lifetime) x 0.25 i |
| 0.16666667 | cube's six faces' sum scale |
| 0.001 | RenderParticles' die add; unrolled quad's min alpha |
| 254.9 | colour byte scale |
| 64, & 0x3f | sprite trail ring |
| 4.0 (2 units) | sprite trail point spacing |
| 0.015625 | trail update interval x lifetime |
| 0.125 s | precipitation trace interval |
| 320, 320, 320, FLT_MAX | the four rays' TMax |
| 300 | nearby distance |
| 180 / 32 / 100 | outer control point z / inner near forward / inner far forward |
| 0x152ab6e8 / 0x152ab860 | func_precipitation list / func_precipitation_blocker list |
| 1e23 (0x65a96816) | trace's starting distance (id -1, normal 0) |
| 1e-10 | DDotN, t and barycentric thresholds |

Precipitation types (InitializeParticlePrecip, particles/rain_fx.pcf; types 0-3 the old sprite rain / snow / ash / snowfall):

| m_nPrecipType | Inner near | Inner far | Outer | Inner distance |
|---|---|---|---|---|
| 4 (and any other) | `rain` | `rain` | `rain_outer` | 180 |
| 5 | `ash` | `ash` | `ash_outer` | 280 |
| 6 | `rain_storm` | `rain_storm_screen` | `rain_storm_outer` | 0 |
| 7 | `snow` | `snow` | `snow_outer` | 280 |

## env_steam / env_steamjet

- CSteamJet::Spawn: classname `env_steamjet` sets m_bFaceLeft (the jet leaves along -right); `InitialState` non-zero starts emitting. TurnOn / TurnOff / Toggle set m_bEmit; JetLength / Rate / Speed / SpreadSpeed set their field.
- Start: the material; spawn timer rate 1 / Rate; `m_Lifetime = JetLength / Speed`.
- Update: while emitting and drawn last frame, a particle per timer event. Position the origin; velocity `forward x Speed + right x RandomFloat(-SpreadSpeed, SpreadSpeed) + up x RandomFloat(-SpreadSpeed, SpreadSpeed)`, draws in that order (FaceLeft: forward = -right, right = forward); roll RandomFloat(0, 360), roll speed RandomFloat(-RollSpeed, RollSpeed); lifetime 0, die time m_Lifetime; StartSize / EndSize stored as bytes (EndSize 1024 is 0).
- SimulateParticles: lifetime += dt; past die removed; else `roll += roll speed x dt`, `position += velocity x dt` (no gravity, no drag).
- UpdateLightingRamp: five colours; light = GetLightForPoint(point, false); emissive: each `rendercolor / 255 + light` clamped 0..1; else `rendercolor / 255 x light`; a colour whose greatest component is over 1 is divided by it.
- RenderParticles: `f = lifetime / (die + 0.001) x 4`; colour `ramp[(int)f] + (ramp[(int)f + 1] - ramp[(int)f]) x frac(f)`, each at most 1. Type 1: unrolled quad, half-size `StartSize + (EndSize - StartSize) x lifetime` (float sizes); else rolled quad, half-size `start + (end - start) x lifetime` (byte sizes; lifetime in seconds, not its fraction).
- Unrolled quad: not under alpha 0.001; colour bytes `round(component x 254.9)`; corners at the view-space point -+ size, a random normal.
- Alpha (SDK, unread in the binary): `sin(pi x lifetime / die) x renderamt / 255`.
- GetLightForPoint: ComputeLighting folds each local light into the ambient cube; result the six faces' sum x 0.16666667, clamped to 1 only when asked.

## env_spritetrail

- Server: CSpriteTrail is a CSprite (ShowSprite / HideSprite / ToggleSprite); startwidth, endwidth, lifetime, startwidthvariance, textureres, minfadelength are keyvalues the client reads.
- UpdateTrail: not before m_flUpdateTime. The origin becomes a new point unless the last is within 2 units (`(dy^2 + dx^2) + dz^2 <= 4.0`); a full ring drops its oldest. A point: place, die = now + lifetime, width variance RandomFloat(-variance, variance), texture coordinate = last point's + textureres x distance (0 for the first). Then `m_flUpdateTime = now + lifetime x 0.015625`.
- DrawModel: CBeamSegDraw through the points oldest first, then the origin with die now + lifetime. Per point `t = clamp((die - now) / lifetime, 0, 1)`; fade t, or `min(t, (minfade - left) / minfade)` along minfadelength's run; alpha byte `(int)(brightness x fade)`; width `endwidth + (startwidth - endwidth) x t` (startwidth alone when endwidth < 0) + the variance, never below 0; colour rendercolor. An expired point leaves the ring's front.
- NextSeg: from the second point on, `normal = (last - this) x (last - camera)`, normalised as `x / sqrt(length^2 + FLT_EPSILON)` (rsqrtss and one Newton step); the last point drawn by SpecifySeg with that normal when it is the first, else with `normalize((the normal before + this one) x 0.5)`; the final point with the last normal.
- SpecifySeg: two vertices, `point + normal x width x 0.5` with texture (0, coordinate), `point - normal x width x 0.5` with (1, coordinate); the point's colour.

## func_precipitation

- OnDataChanged: `m_flDensity = render alpha byte x 0.01`.
- Simulate: the systems' setup once (0x10799220); first time: trace interval 0.125 s, 0 left; then UpdateParticlePrecip for the local player.
- InitializeParticlePrecip: names by type (table above); two ray-trace environments: every func_precipitation and every func_precipitation_blocker: physcollision's debug mesh of the entity's solids[0], each three vertices a triangle (model space, no entity transform).
- UpdateParticlePrecip, each interval:
  1. forward = EyeVectors' forward, z dropped, `x / (length + FLT_EPSILON)`.
  2. Four rays from the eye against the precipitation environment: forward, normalize(forward - right), normalize(forward + right), (0, 0, 1).
  3. inside = the fourth ray hit and that triangle's normal z < 0; nearby = any hit and any distance <= 300.
  4. inside, or nearby with min(first three distances) < inner distance: all three systems exist -> control point 1 of the outer = eye + (0, 0, 180), inner near + forward x 32, inner far + forward x 100; control point 3 of each = (density x r_RainParticleDensity, 0, 0); else DispatchInnerParticlePrecip.
  5. nearby only: inner two stop (0x10799600), outer made (0x107996a0) or its control points 1 and 3 moved. Neither: all three stop.
- DispatchInnerParticlePrecip: stops all three (StopEmission, particles live on), makes them on the entity; control point 2 follows the player; control point 1 as above but inner far + forward x inner distance; control point 3 the density.
- Trace (0x10995b30), per triangle: `DDotN = dir . N`; hit when DDotN > 1e-10 or < -1e-10 (both sides); `t = (D - origin . N) / DDotN`, t > 1e-10 and < the nearest so far; both barycentrics >= 1e-10 and their sum <= 1. Keeps the triangle's index, t and its own N (never turned to the ray).

## rain_fx.pcf's functions

- **C_INIT_RtEnvCull** ("Cull relative to Ray Trace Environment"): lifetime -1 skipped. One ray from the particle, TMin 0: along the test direction with TMax FLT_MAX, or with use velocity along position - previous (rsqrt-normalised) with `TMax = lifetime x speed` (speed = that length / last dt). hit = a triangle, and with a cull normal other than vec3_origin, its normal equal to it.
  - Velocity branch: adjust lifespan: a hit sets `lifetime = min(lifetime, distance / (speed + FLT_EPSILON))`, a miss culls when cull on miss; else a hit culls unless cull on miss, a miss culls when cull on miss.
  - Direction branch: the same, but a hit with cull on miss culls when a cull normal is set. Culled = lifetime -1.
- **C_INIT_LifespanFromVelocity** ("Lifetime from Time to Impact"): a cache block on the parent collection when there is one. Per particle with lifetime >= 0:
  1. `velocity = (position - previous) / last dt`; `dir = velocity / (speed + FLT_EPSILON)`; `start = position + dir x offset`; `end = start + dir x (max - offset)`.
  2. The cached entry with the least `max(|start - its start|^2, |end - its end|^2)` (a later one on a tie) is used when <= tolerance^2; else TraceLine(start, end, mask, group): point = the end position, or vec3_invalid when `fraction <= 1 - max / (max - offset + FLT_EPSILON)`, start solid, all solid or max = offset; stored at the next index (wraps past points to cache, the count stopping there).
  3. vec3_invalid: lifetime -1; else `lifetime = (|(start - point) x bias| + offset) / (speed + FLT_EPSILON)`.
- What rain_fx.pcf asks: every inner and outer system culls a particle with nothing of a precipitation volume above it (cull on miss, test direction up); rain also takes its lifetime from the world trace (DEBRIS, offset -400, length 600, tolerance 48, 48 cached, bias 0.98: a roof within the 400 units above culls it) and tests the blocker volumes; ash and snow end their lifetime where their velocity leaves the precipitation volumes. The ash and snow outer systems use C_OP_SetControlPointToImpactPoint for control points 4 and 5. Children: `rain_impact_04`, `ash_eddy_b`.
- **`rain_outer` is an empty definition** in CS:GO's rain_fx.pcf (no emitter, operator, renderer or child): the outer rain draws nothing.
- CS2's classes named C_INIT_RtEnvCull / C_INIT_LifespanFromVelocity have other, untraced bodies.

## Unread

- 0x101a3f80 (the steam jet's view transform and alpha register).
- CSpriteTrail's server Spawn, and whether SetScale reaches the trail (the client's draw reads no scale).
- 0x10368b80, CBeamSegDraw::Start 0x109a94c0, 0x10369610 / 0x103697a0 / 0x103698b0.
- 0x10797f60, 0x10799d20, 0x1079a580 (the old types 0-3).
- SetupAccelerationStructure 0x10994ee0 (the normals' direction: the cross product and the debug mesh's winding).
- The InitNewParticlesBlock twins; C_OP_SetControlPointToImpactPoint 0x10975cb0.
- The world trace's mask and the DEBRIS group in the particle trace.
