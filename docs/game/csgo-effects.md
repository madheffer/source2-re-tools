# CS:GO's steam jets, sprite trails and precipitation

**CS:GO legacy** (not CS2: a CS:GO map's effect entities, web/src/cs2web/csgo/). Binaries: `csgo legacy/csgo/bin/client.dll`
(Ghidra `/client.dll.3`, image base 0x10000000), `csgo/bin/server.dll` (`/csgo_server_legacy.dll`) and
`bin/engine.dll` (`/engine.dll`). The classes are Source's (c_steamjet.cpp, c_spritetrail.cpp, c_effects.cpp, beamsegdraw.cpp,
raytrace.cpp, the particle library); every number below is read from the binary, the names are the SDK's.

The ports: [web/src/cs2web/csgo/entities/effects.js](../../web/src/cs2web/csgo/entities/effects.js) (the state the
replicas keep) and web/src/cs2web/client/csgo/fx/ (steam-jet.js, sprite-trail.js, precipitation.js, rt-env.js,
particle-functions.js, ambient.js, map-fx.js: drawn, a view only; fx-test.mjs checks the pure pieces).

## 1. env_steam / env_steamjet

Server, CSteamJet::Spawn `server.dll 0x10629060`: the classname `env_steamjet` sets m_bFaceLeft (the legacy entity
whose jet leaves along -right); `InitialState` non-zero starts it emitting. Inputs TurnOn / TurnOff / Toggle set
m_bEmit, JetLength / Rate / Speed / SpreadSpeed set that field.

Client, C_SteamJet (vtable `0x10cd3e80`):

| Address | Function | What it does |
|---|---|---|
| 0x107ab700 | Start | the material: g_Mat_DustPuff[0] = `particle/particle_smokegrenade`, or `sprites/heatwave` for type 1 (the heat wave); the spawn timer's rate 1 / Rate; m_Lifetime = JetLength / Speed |
| 0x107ab7c0 | Update | while emitting and drawn last frame: the timer's events this frame, a particle each. Position the origin; velocity = forward x Speed + right x RandomFloat(-SpreadSpeed, SpreadSpeed) + up x RandomFloat(-SpreadSpeed, SpreadSpeed), in that order of draws (FaceLeft: forward = -right, right = forward); roll RandomFloat(0, 360), roll speed RandomFloat(-RollSpeed, RollSpeed); lifetime 0, die time m_Lifetime; StartSize and EndSize stored as **bytes** (an EndSize of 1024 is 0) |
| 0x107ac160 | SimulateParticles | lifetime += dt; past the die time the particle is removed; else roll += roll speed x dt, position += velocity x dt (no gravity, no drag) |
| 0x107ac270 | UpdateLightingRamp | skipped while the origin (+700 x 4) and the angles are within 0.1 of the last ones. Five colours (+0x2c5 x 4 on, 12 bytes each): at origin + forward x (Speed x m_Lifetime) x 0.25 i, light = engine->GetLightForPoint(point, false); spawnflag 1 (emissive, +0x2ba bit 0): each of rendercolor / 255 + light clamped to 0..1; else rendercolor / 255 x light; then a colour whose greatest component is over 1 is divided by it |
| 0x107abea0 | RenderParticles | f = lifetime / (die + 0.001) x 4; the colour = ramp[(int)f] + (ramp[(int)f + 1] - ramp[(int)f]) x frac(f), each component at most 1; type 1: the quad 0x107abc20 of half-size StartSize + (EndSize - StartSize) x lifetime (the float sizes); else the rolled quad 0x1022f980 of half-size start + (end - start) x **lifetime** (the byte sizes; the lifetime in seconds, not its fraction) |
| 0x107abc20 | the unrolled quad | not drawn under alpha 0.001; colour bytes = round(component x 254.9); four corners at the view-space point -+ size, a random normal |
| 0x101a3f80 | (before the quad) | **not read**: the view transform and the alpha it leaves in a register (c_steamjet.cpp: sin(pi x lifetime / die) x renderamt / 255) |

engine.dll, the light at a point: IVEngineClient::GetLightForPoint `0x100b6160` (CEngineClient vtable `0x1047d850` slot 1)
-> slot 72 `0x100b7210` -> ComputeLighting `0x10247b80` with no normal: LightcacheGetDynamic `0x10246ea0` gives the
ambient cube and the local lights; each local light is folded into the cube (falloff `0x10243a30`, `0x101391d0`, add
`0x10244230`); the result is the six faces' sum x 0.16666667, clamped to 1 only when asked.

Here: the bake computes that at every leaf ambient sample (bake/Source1/AmbientLight.cs PointLightFile ->
`lighting/ambient.bin`: "ZAMB", version 1, flags, count, then x y z r g b floats; 54,243 samples on ze_crazykart_v4)
and the browser takes the nearest sample (ambient.js). Stand-ins: the engine takes the point's own leaf and adds the
lights as seen from the point, here it is the nearest sample of any leaf with the lights as seen from the sample; a map
without the file takes 0.35; type 1's refraction isn't drawn; particles are made whether or not the jet was drawn last
frame.

## 2. env_spritetrail

Server: CSpriteTrail is a CSprite (ShowSprite / HideSprite / ToggleSprite turn it on and off); its startwidth,
endwidth, lifetime, startwidthvariance, textureres, minfadelength are keyvalues the client reads (the map sets them
with AddOutput). Not read: its Spawn, and whether SetScale reaches the trail (the client's draw doesn't read a scale).

Client, C_SpriteTrail (vtable `0x10be7a1c`). The ring of points: 64 of them, the first index at `+0x1040`, the count
at `+0x1044`, an index masked `& 0x3f`.

| Address | Function | What it does |
|---|---|---|
| 0x10368f00 | UpdateTrail | not before m_flUpdateTime. The origin becomes a new point unless the last one is within 2 units ((dy^2 + dx^2) + dz^2 <= 4.0); a full ring drops its oldest. A point: its place, die time = now + lifetime, width variance = RandomFloat(-variance, variance), texture coordinate = the last point's + textureres x the distance (0 for the first). Then m_flUpdateTime = now + lifetime x 0.015625 |
| 0x10368ca0 / 0x10368b80 | the render bounds | from the ring's points (0x10368b80 walks the ring: **seen, not read**) |
| 0x103690e0 | DrawModel | CBeamSegDraw through the points, oldest first, then the origin itself with die time now + lifetime. Per point t = clamp((die - now) / lifetime, 0, 1); fade = t, or min(t, (minfade - left) / minfade) while minfadelength's run along the beam lasts; the alpha byte = (int)(the entity's brightness x fade); width = endwidth + (startwidth - endwidth) x t (startwidth alone when endwidth < 0) + the point's variance, never below 0; colour rendercolor. A point whose die time has passed leaves the ring's front |
| 0x109a94c0 | CBeamSegDraw::Start | **not read** (begins the mesh for the point count) |
| 0x109a9c50 | CBeamSegDraw::NextSeg | the camera's origin at +0x238, the last segment at +0x200 (position, colour bytes +0x210, texture coordinate +0x214, width +0x218), the count drawn +0x224 of +0x220, the last normal +0x228. From the second point on: normal = (last - this) x (last - camera), normalized as x / sqrt(length^2 + FLT_EPSILON) (rsqrtss and one Newton step); the last point is drawn by SpecifySeg with that normal when it is the first, else with normalize((the normal before + this one) x 0.5); the final point with the last normal |
| 0x109a9620 | CBeamSegDraw::SpecifySeg | two vertices: the point + normal x width x 0.5 with texture (0, the point's coordinate), the point - normal x width x 0.5 with (1, the coordinate); both the point's colour |
| 0x10369610 / 0x103697a0 / 0x103698b0 | (a neighbour class: ctor / dtor / reset) | **seen, not read** (not C_SpriteTrail's) |

Stand-ins in sprite-trail.js: the skybox scale, renderfx on the alpha.

## 3. func_precipitation

Client, CClient_Precipitation (vtable `0x10ccf358`; the networkable's `0x10ccf660`). Types 0-3 are the old sprite
rain / snow / ash / snowfall; the map uses the particle types. Fields: m_nPrecipType +0xa00, m_flDensity +0xa08, the
inner distance +0xa64, the three system names +0xa68 / +0xa6c / +0xa70, the systems' handles +0xa7c (inner near),
+0xa88 (inner far), +0xa94 (outer), the trace timer +0xa98 (interval) / +0xa9c (left).

| Address | Function | What it does |
|---|---|---|
| 0x10796110 | Precache | the systems' names per type (below) |
| 0x10796430 | OnDataChanged | m_flDensity = the render alpha byte x 0.01 |
| 0x10798a30 | Simulate | makes the systems' setup once (0x10799220); the first time: the trace timer's interval 0.125 s, 0 left; then UpdateParticlePrecip for the local player |
| 0x10799220 | InitializeParticlePrecip | by m_nPrecipType: 4 (and any other) inner near `rain`, inner far `rain`, outer `rain_outer`, inner distance 180; 5 `ash` / `ash` / `ash_outer`, 280; 6 `rain_storm` / `rain_storm_screen` / `rain_storm_outer`, 0; 7 `snow` / `snow` / `snow_outer`, 280 (particles/rain_fx.pcf). Then two ray-trace environments: from every func_precipitation (the list at 0x152ab6e8) and from every func_precipitation_blocker (0x152ab860): physcollision's debug mesh of the entity's solids[0], each three vertices a triangle (the model's own space, no entity transform) |
| 0x10798ba0 | UpdateParticlePrecip | each timer interval: forward = EyeVectors' forward, z dropped, x / (length + FLT_EPSILON); four rays from the eye against the precipitation environment: forward, normalize(forward - right), normalize(forward + right), (0, 0, 1), TMax 320, 320, 320, FLT_MAX. inside = the fourth ray hit and that triangle's normal z < 0; nearby = any ray hit and any ray's distance <= 300. inside, or nearby with min(the first three distances) < the inner distance: all three systems exist -> control point 1 of the outer = eye + (0, 0, 180), of the inner near + forward x 32, of the inner far + forward x 100, and control point 3 of each = (density x r_RainParticleDensity, 0, 0); else DispatchInnerParticlePrecip. nearby only: the inner two stop (0x10799600), the outer is made (0x107996a0) or its control points 1 and 3 moved. neither: all three stop |
| 0x107998b0 | DispatchInnerParticlePrecip | stops all three (StopEmission, the particles live on), makes them on the entity; control point 2 follows the player; control point 1 as above but the inner far's + forward x the inner distance; control point 3 the density |
| 0x107996a0 / 0x10799600 | DispatchOuterParticlePrecip / DestroyInnerParticlePrecip | the outer alone, the same points / the inner two stopped and released |
| 0x10797f60 | the old ash type's emitter | names `effects/fleck_ash1..3`, `effects/ember_swirling001`: **seen, not read** |
| 0x10799d20 / 0x1079a580 | (the old types' draw / a ConVar read) | **seen, not read** |

The ray tracer (RayTracingEnvironment): Trace4Rays `0x10994260` (splits a packet whose rays' directions differ in
sign) -> `0x10995b30`: the result starts as id -1, distance 1e23 (0x65a96816), normal 0. Per triangle (48 bytes: N at
+0, D at +0xc, the id at +0x10, the two edge equations from +0x14, the projection axes' bytes at +0x2c / +0x2d):
DDotN = dir . N; hit when DDotN > 1e-10 or DDotN < -1e-10 (both sides of the triangle); t = (D - origin . N) / DDotN
with t > 1e-10 and t < the nearest so far; the two barycentrics >= 1e-10 and their sum <= 1. The result keeps the
triangle's index, t and the triangle's own N (never turned to the ray). AddTriangle `0x109960d0` stores the three
vertices; SetupAccelerationStructure `0x10994ee0` (**not read**: the normal's cross product, the k-d tree).

rain_fx.pcf's functions the systems need (the particle library in client.dll):

| Address | Function | What it does |
|---|---|---|
| 0x109616c0 | C_INIT_RtEnvCull::InitNewParticlesScalar ("Cull relative to Ray Trace Environment", vtable 0x10d0765c) | fields: test direction +0x5c, cull normal +0x68, the environment's number +0x74, use velocity +0x78, cull on miss +0x79, adjust lifespan +0x7a. A particle with lifetime -1 is skipped. One ray from the particle, TMin 0: along the test direction with TMax FLT_MAX, or with "use velocity" along position - previous (rsqrt-normalized) with TMax = lifetime x speed (speed = that length / the last dt). hit = a triangle, and with a cull normal other than vec3_origin, its normal equal to it. Velocity branch: "adjust lifespan": a hit sets lifetime = min(lifetime, distance / (speed + FLT_EPSILON)), a miss culls when "cull on miss"; else a hit culls unless "cull on miss", a miss culls when "cull on miss". Direction branch: the same, but a hit with "cull on miss" culls when a cull normal is set (0x10961b0f tests the normal flag). Culled = lifetime -1 |
| 0x1095fed0 | C_INIT_LifespanFromVelocity::InitNewParticlesScalar ("Lifetime from Time to Impact", vtable 0x10d08c90) | fields: bias distance +0x5c, trace offset +0x68, maximum trace length +0x6c, trace recycle tolerance +0x70, collision group +0x74, maximum points to cache +0x7c, the trace mask +0x100. A cache block on the parent collection when there is one (starts, ends, hit points, normals; count +0x1ec0, next index +0x1ec4, valid flags +0x1ed8). Per particle with lifetime >= 0: velocity = (position - previous) / the last dt; dir = velocity / (speed + FLT_EPSILON); start = position + dir x offset; end = start + dir x (max - offset). The cached entry with the least max(|start - its start|^2, |end - its end|^2) (a later one on a tie) is used when that is <= tolerance^2; else TraceLine(start, end, mask, group): the point = the trace's end position, or vec3_invalid when fraction <= 1 - max / (max - offset + FLT_EPSILON), start solid, all solid or max = offset; stored at the next index (which wraps once it passes "points to cache", the count stopping there). vec3_invalid: lifetime = -1; else lifetime = (|(start - point) x bias| + offset) / (speed + FLT_EPSILON) |
| 0x10960650 / 0x10961b20 | their InitNewParticlesBlock | **not read** (the SIMD twins) |
| 0x10975cb0 | C_OP_SetControlPointToImpactPoint::Operate (vtable 0x10d0d1e8) | **not read** (the ash and snow outer systems' control points 4 and 5: the bake still skips it) |

What rain_fx.pcf asks of them (read through the bake's FX_TRACE): every inner and outer system culls a particle with
nothing of a precipitation volume above it ("cull on miss", test direction up); rain also takes its lifetime from the
world trace (DEBRIS, offset -400, length 600, tolerance 48, 48 cached, bias 0.98: a hit within the 400 units above the
particle, a roof over it, culls it) and tests the blocker volumes; ash and snow end their lifetime where their
velocity leaves the precipitation volumes. **`rain_outer` is an empty definition in CS:GO's own rain_fx.pcf** (no
emitter, operator, renderer or child): the outer rain draws nothing in CS:GO.

Here (precipitation.js, rt-env.js, particle-functions.js): a volume is its convex hulls from the bake's hulls.json, a
face tested whole in place of its triangles; the environments are made from the volumes alive, again when that set
changes. Stand-ins: **the normals are taken as pointing into the volume** (the cross product in 0x10994ee0 and the
debug mesh's winding aren't read; "inside" needs z < 0 for the top face seen from within, which only an inward normal
gives); the tracer's clip to TMax is a plain t <= TMax; the particle functions' attribute defaults are CS2's class
defaults; the world trace is the particle runtime's (CS:GO's mask and the DEBRIS group against it not traced); the
player is the camera; r_RainParticleDensity is 1; types 0-3 aren't drawn.

## 4. The bake

`lasers-bake --source1` ships what these draw with: bake/Source1/SpriteBake.cs adds an env_spritetrail's
`spritename` and, for a map with an env_steam / env_steamjet, `particle/particle_smokegrenade.vmt` (type 1:
`sprites/heatwave.vmt`) to sprites/; bake/Source1/Source1Particles.cs adds a func_precipitation's systems by its
preciptype to fx/ (their children come with them: `rain_impact_04`, `ash_eddy_b`); bake/Source1/PcfOps.cs keeps the
two functions above as `CSGO_INIT_RtEnvCull` / `CSGO_INIT_LifespanFromVelocity` (their own class names: CS2's classes
of those names have other, untraced bodies); bake/Source1/AmbientLight.cs writes lighting/ambient.bin.
ze_crazykart_v4: 7 sprites, 44 systems. `FX_TRACE=<system>` on a bake logs which .pcf files define a system and every
function's attributes.
