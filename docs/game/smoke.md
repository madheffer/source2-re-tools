# CS2's smoke volume

server_20261105, client_20261015, tier0_20261103, rendersystemvulkan_20261015; shaders from shaders_vulkan_dir.vpk
(read as HLSL / GLSL with VRF 20.1.7467's VfxShaderFile.GetDecompiledFile, SPIRV-Cross); assets from pak01 / core pak01.

The smoke grenade's cloud: a voxel volume the server builds by a flood fill over the world from where the grenade
stopped, sends to the clients (m_VoxelFrameData) and answers line-of-sight questions with (bots, spotting). The clients
run the same simulation from the records, draw it and carve it with bullets and HE grenades (client-only state). The
throw / flight / detonation timing: grenades.md "Smoke".

## Names (RTTI / strings)

- `SmokeVolume` (shared, both DLLs): `BuildSmokeSimulation(CSmokeGrenadeProjectile*, ...)` (a CCoJobLambda, job name
  `buildSmokeVolume`), `RebuildVoxels(AABB_t const&)`, `GetSmokeDensityInLine(VectorWS, VectorWS, ...)`,
  `GetSmokeDensityLOS(...)` (private); `VoxelOctree::Voxelize(VoxelID const&)`.
- `CSmokeVolumeSystem` (a game system on both sides, string `SmokeVolumeSystem`, server 1800ac890; server vtable
  0x1818d5428).
- CSmokeGrenadeProjectile networked fields: m_nSmokeEffectTickBegin, m_bDidSmokeEffect, m_nRandomSeed, m_vSmokeColor,
  m_vSmokeDetonationPos, m_VoxelFrameData (CNetworkUtlVector<uint8>), m_nVoxelFrameDataSize, m_nVoxelUpdate,
  m_nSmokeLightProbeRegen (registration 1809c5440 / 1809b6310). Client: m_bSmokeVolumeDataReceived.
- Thinks (named by 1809baf90): CSmokeGrenadeProjectileThink_Detonate, _Update, _Remove, _BuildingSmokeVolume.
- Client only: `CFixedSizeCircularBuffer<SmokeVolumeBulletTrail_t, 16>`, `CFixedSizeCircularBuffer<
  SmokeVolumeHEGrenadeTrail_t, 5>` (the server has neither), CSmokeVolumeSceneObject(Desc) (`cs_smoke_volume_visual.cpp`),
  materials/dev/smoke_volume{,_mask,_depth,_lpv}.vmat, render targets SmokeVolumeMaskTex_N / OppacityTex_N /
  OptimTex_Color_N / _Depth_N / _DepthCombined_N (N 0..4: up to 5 smokes drawn this way?), SmokeGrenade.Clear.
- Cvars: server bot_max_visible_smoke_length, inferno_smoke_volume_density, smoke_param1..5, smoke_use_noise_texture,
  sv_smoke_lighting_changed, cl_smoke_origin_height, cl_smoke_torus_ring_radius / _subradius, cl_smoke_edge_feather,
  cl_smoke_lower_speed, smoke_grenade_ct_color / _t_color, sv_kill_smokegrenade, sv_explode_smokegrenade_at_crosshair,
  sv_throw_smokegrenade; client cl_smoke_volumeprop, cl_smoke_volume_growth, sv_smoke_volume_blind_start,
  cl_use_prompt_smoke_density, smoke_volume_lod_ratio_change.
- sv_explode_smokegrenade_at_crosshair and sv_throw_smokegrenade are FCVAR_DEVELOPMENTONLY | CHEAT (0x4002: "Unknown
  command" in retail); `ent_create smokegrenade_projectile` needs a player's view (nothing on a dedicated server) and
  would not get Create's think.

## Functions (server)

| Address | Module | What |
|---|---|---|
| 1809b8bb0 | server | Detonate -> 1809b4190 on the projectile's +0xbc0 |
| 1809b4190 | server | build start (vol, owner, pos, trail, time) |
| 1809b45b0 | server | grid(grid, centre, size, voxel) |
| 1809b0250 | server | volume constructor (hole writes at 1809b0318) |
| 1809b0d20 | server | volume destructor |
| 1809b3e00 -> 1809b2390 | server | job run slot 8 (job vtable 0x1818e9cb0) -> the job (job + 0x120) |
| 1809d7150 / 1809b0470 | server | voxel coordinates / round to three bytes |
| 1809d6960 | server | a voxel's centre |
| 1809bd920 | server | a start (vol, point, owner, out) |
| 1809bd150 | server | fallback start (8 points at 40 u) |
| 1809aedc0 | server | visited set hash |
| 1809b39c0 | server | queue push |
| 1809d58d0 | server | a step (vol, from, voxel, owner, queue, list): 6 neighbours |
| 180c2f3c0 | server | TraceShape |
| 180250e50 | server | UTIL_TraceLine |
| 1809d6b00 | server | brick load into the work block |
| 1809d6c40 | server | brick built on first use |
| 1809d3810 | server | octree voxelize (grid, brick, level, test, bounds) |
| 1809d7530 | server | box test slot +0x10: box + centre -> 1809c7bd0 |
| 1809c7bd0 | server | the box test (TraceShape of the box) |
| 1809bb050 | server | the fill (vol, queue, owner) |
| 1816a4690 | server | job yield |
| 1809d0110 | server | flat tops |
| 1809bc190 | server | underhangs |
| 1809a35f0 | server | V_qsort comparator a.z - b.z |
| 1809b2ec0 | server | crowning a 40-record fill |
| 1809b1850 | server | 2 voxels from it in the grid and clear |
| 1808ad470 | server | fabsf |
| 1809d4650 | server | trail push (each think before the detonate test) |
| 1809cd180 | server | trail ring push |
| 1809d4330 | server | the think that finds the job done (every tick) |
| 1809d2780 | server | the pop: 1809b4090, +0xbb8 = 0, 18032b710(TheBots, grenade, 166.0) |
| 1809b4090 | server | (vol, m_vSmokeDetonationPos, interval x tick): fresh work block |
| 1809d47d0 | server | dissipation flag at 19 s |
| 1809d6590 | server | server update (every >= 0.1 s) |
| 180988170 | server | CSmokeVolumeSystem slot 32 (vtable +0x100 via thunk 18097ee00): ServerPostEntityThink |
| 1809b3630 | server | the simulation step (vol, buffer) |
| 1809d09e0 | server | emitter pass |
| 1809b1650 | server | six neighbours' mean clamp(d / 50) over active ones |
| 1809d1a90 | server | per-voxel step (client 1807dc8c0) |
| 1814738b0 | server | normalize in double (out of 1e-17 .. 1e17) |
| 1809b6af0 | server | CRC (debug) |
| 1809b9ba0 | server | writes the record |
| 1809b389c | server | the holes' countdown |
| 1809b00c0 / 1809b0a10 / 1809b2a90 | server | smoke list append (construction) / list |
| 1809d5000 | server | the line walk (vol, a, b, visitor) |
| 181489c20 -> 181476b30 | server | slab clip (tolerance 0) |
| 1809bfc60 | server | density along a line (IsLineBlockedBySmoke: >= 1.0); visitor 1809d7440 -> 1809b14f0 |
| 1809af7d0 | server | smoothstep `(3 - 2x) * x * x` |
| 1809bff80 | server | the damage feedback's density (< 1.4); visitor 1809d7430 -> 1809b1150 |
| 1809bf8e0 / 1809bf980 | server | density at a point (weight x) |
| 1809bfb20 | server | point density summed over smokes |
| 1809bfb10 | server | returns 1.0 (the volume path always) |
| 1809d7f20 / 1809d7f90 | server | light probe count |
| 18032a570 | server | CBotManager::IsLineBlockedBySmoke |
| 18032a6b0 | server | CBotManager::IsVisibleThroughSmoke |
| 1803260c0 | server | sphere segment length (r^2, &pos, from, to) |
| 18032b550 / 18032b710 | server | bot grenade list clear / add |
| 1802d3ba0 | server | CCSBot::IsVisible (cs_bot_vision.cpp) |
| 1801d7460 | server | spotting (uses IsLineBlockedBySmoke) |
| 1803233b0 | server | CBtDecoratorPickerBlockedBySmoke (slot 10) |
| 180349500 | server | inferno smoke check: put out when > 1/3 of fire areas in smoke |
| 180342d10 | server | flame vs smoke |
| 180347c00 | server | put a flame out |
| 18034cc30 | server | CreateFire's "no fire in smoke" |
| 180345dc0 / 180352350 | server | CreateFire / seeded spread |
| 1809cf572 | server | ResolveFlyCollisionCustom's vfn 0xa00 call (after the bounce counter) |
| 1809cb9d0 -> 1809b5220 | server | smoke vfn 0xa00: land on a fire |
| 180bf7da0 | server | sphere query |
| 180343040 -> 18034d880 | server | inferno: nearest burning fire's point (inferno, origin, 10, check, grenade) |
| 1803443c0 | server | fire visibility lines |
| 180c2e9c0 | server | TraceEntity |
| 180545fc0 | server | InitAllSystems |
| 1809ae490 | server | CUtlHashtable<u16> insert |
| 1809b91a0 / 1809b8fc0 | server | rehash / re-place |
| 1809b46d0 | server | move an occupant along its chain |
| 180be8f60 | server | CGameSurfaceProperties fill from scripts/surfaceproperties_game.txt (allowsmokethrough lea at 180be9030) |
| 180c07590 | server | CGameSurfaceProperties ctor (zeroes +0x18..+0x1e) |
| 180c00e80 | server | surface index |
| 1809b3e30 | server | CDecoyProjectile vfn 0x9b8 (Flashbang.Bounce; the flashbang's own 1803a46d0 the same string) |
| 1808c3200 | server | CBaseGrenade::Explode: EF_NODRAW (0x20), zero velocity, think 180d0bca0 (SUB_Remove) at + 0.1 (0x3dcccccd) |
| tier0 0x180007f50 -> 0x1802e0d70, 0x180008280 -> 0x1802e6570 | tier0 | V_cosf / V_sinf (the CRT's) |

## Functions (client)

| Address | Module | What |
|---|---|---|
| 1807e0d70 -> 1807c70f0 | client | walk the records for the next seq |
| 1807c8990 | client | apply a record |
| 1807c5ed0 | client | the simulation step |
| 1807dc8c0 | client | per-voxel step (as 1809d1a90) |
| 1807dff70 | client | RegenerateTextureBits |
| 1807d90a0 | client | byte `(uint)(clamp(d / 50, 0, 1) * 255)` |
| 1807c53c0 | client | box clamp to 0..32 |
| 1807e0ea0 | client | volume list (+0x80) entry -> world point |
| 1813d0610 | client | 3D texture (0x20, 0x20, 0x20, 1, ..) |
| 1807d3f80 | client | scene object creation: the SmokeFluidA atlas |
| 1807cd7f0 -> 1807de9d0 | client | line test (summing visitor 181bd3c70): the target ID's smoke gate (settings.md "The friendly warning") |
| 1807cd400 | client | constant 1.0 (volume overlay path on) |
| 1807cd230 | client | density at the eye |
| 1807c2fc0 | client | smoothstep (either edge order) |
| 1807cd430 / 1807cd420 / 1807cd410 | client | constants 0.1 / 22 / 17 |
| 180c9ba00 | client | the in-smoke overlay's old torus path |
| 180ca06e0 | client | the in-smoke overlay's volume path (density at the eye) |
| 180c686f0 | client | the pawn's think: overlay alpha |
| 1803a4e70 | client | Approach |
| 180d2c780 | client | add a bullet trail |
| 1817590b0 | client | segment vs box |
| 180901390 / 180901230 | client | tracer record queue (cs_player_weaponservices.cpp) / flush |
| 1807dbe30 | client | the decoy's fake shot trail |
| 180d2cd00 | client | add an HE hole |
| 180d1f260 | client | HE vs smoke mask (pos, object + 0xd0) |
| 18174a510 | client | box vs sphere |
| 18022fee0 | client | trace line |
| 1810d03d0 | client | HE projectile network change: SmokeGrenade.Clear |
| 180d1f020 | client | remove an HE hole |
| 1810c6420 / 180cac130 | client | HE projectile destructor / other caller of 180d1f020 |
| 180d20800 | client | the renderer (SmokeConstantBuffer_t) |
| 180d1c530 / 180d1f4d0 | client | CSmokeVolumeSceneObject ctor (vtable 181ca82c8) |
| 1801bcf20 | client | box union |
| 180853e30 | client | gamerules + 0xb0 > 0 (c98) |
| 180cb36f0 | client | planted C4s (list 1824cb3c0, next + 0x1280) |
| 180d25e00 | client | curtime |
| 180161780 / 18075d250 | client | curtime (bullet time) |
| 1807dfdb0 | client | C_BaseCSGrenadeProjectile vfn + 0x70 (explode effect) |
| 180d2cbe0 | client | flashbang: first smoke within 300 u -> 18257e030 |
| 180d2f7c0 | client | smoke_volume_lod_ratio_change reader |
| 180ca07b7 / 180c6182b | client | sv_smoke_volume_blind_start / cl_use_prompt_smoke_density readers |
| 1811d9d30 | client | CRenderingPipelineCsgo::AddLayersToView (SmokeLPVSetup, MBOIT layers) |
| 180d323b0 | client | SmokeLightProbeVolumeData_t fill |
| 1801fc610 / 1801fcdc0 | client | env_light_probe_volume / env_combined_light_probe_volume field tables |
| 1811e0360 | client | upscale ("Upscale CS"): sets DepthThreshold / JoinedSigma at 1811e0df6 / 1811e0e19 |
| 1811cba30 | client | loads mboitfinal / mboitmixedcombine / mboitmixedupsample .vmat |
| 1811e1b80 / 1811e2920 | client | "MboitFinalPass" layer |
| 1811f3780 | client | MBOIT targets |
| 181d2a510 / 181d2a520 | client | MBOIT formats (6 / 4 moments) |
| 1811fef80 | client | PerViewConstantBufferCsgo_t fill (1811ff9ee / 1811ffa00, 1811ff353 / 1811ff369) |
| 181207024 | client | the view's MBOIT flag |
| 180161a30 | client | view attribute lookup |
| 1811efcc0 / 1811e49d0 | client | "Static - MBOIT Pass %d" / "Dynamic - MBOIT Pass %d" |
| 1811e1710 / 1811e3220 | client | "MBOIT(%d) Downsample (%d)" / "MBOIT(%d) Upscale (%d)" |
| 1811ec0c0 | client | DepthNoCharacters (from 181201670, depth prepass layers) |
| 1811e58b0 | client | HalfResDepth / HalfLinearDepth |
| 1811cd9a0 | client | (downsample_depth combo choice, unread) |
| 1811dd5f6 / 1811dd6e9 | client | SmokeOverlayDataA / B |
| 1801266f0..1801269a0 | client | r_csgo_smoke_* cvar stubs |

## Fields

Volume (server: projectile +0xbc0; client: +0x13b8, the same struct 0x10..0x14 bytes longer):

| Offset | Field |
|---|---|
| +0 | built flag |
| +4 | a time |
| +8 | first-pass flag (1) |
| +0xc | the effect's start time (interval x m_nSmokeEffectTickBegin) |
| +0x10 | the grid (below) |
| +0x6c | owner's handle |
| +0x70 | work block (0x10b010 bytes, below) |
| +0x78 / +0x80 | emitters (CUtlVector of {u32 packed voxel, f32 weight}) |
| +0x90 | flags (3) |
| +0x98 | dirty-brick CUtlHashtable<u16> (count +0xa8) |
| +0xb8 / +0xc0 | this pass's emitter list (the record's) |
| +0xd0 | u16 seq |
| +0xd4 (..0xdc) | origin |
| +0xec | current buffer |
| +0xf0 | an emitter's density (60.0, 0x42700000) |
| +0x118 / +0x120 | holes (20 B each) |
| +0x130 | build queue ring (head +0x140, tail +0x144; +0x140 != -1: a start found) |
| +0x148 | seen set |
| +0x170 | the trail's slots |
| +0x180 / +0x1180 | columns' lowest / highest z (u32 x 1024, 0xff-filled per search; 0x20 unset) |
| +0x2180 | the records (count) |
| +0x2198 / +0x219c | best search |
| client +0x100 / +0x104 / +0xe8 / +0x128..+0x130 / +0xd8 / +0xe0 | buffer / emitter density / origin / holes / scene object / texture bytes |

Work block (+0x70):

| Offset | Field |
|---|---|
| +0 | CRC (1809b6af0, debug) |
| +8 | solid bits (512 u64; 0x1000 bytes, one bit per voxel) |
| +0x1008 | active bits (2 x 512 u64; 0x2000 bytes) |
| +0x3008 | entries (2 x 0x8000 = 0x10000 x 16 B {f32 density, f32 dir x, y, z}) |
| +0x103008 | emitter counts / cost (u8 a voxel, 0x8000 bytes) |
| +0x10b008 | dissipating |

Grid (1809b45b0):

| Offset | Field |
|---|---|
| +0 | words (512) |
| +8 | bitset (512 qwords) |
| +0x18 / +0x20 | count 512 / a built byte a brick (512 bytes) |
| +0x30 | log2 n (5) |
| +0x38 / +0x44 | mins (-320) / maxs (320) |
| +0x50 | centre (the detonation point) |
| +0x5c | owner's handle |

Projectile:

| Offset | Field |
|---|---|
| +0xb60 | smoke list next |
| +0xb68 | m_nSmokeEffectTickBegin |
| +0xb6c | m_bDidSmokeEffect |
| +0xb80 | m_vSmokeDetonationPos |
| +0xb90 | m_VoxelFrameData |
| +0xba8 | m_nVoxelFrameDataSize |
| +0xbac | m_nVoxelUpdate |
| +0xbb4 | timer after a collision (0.046875) |
| +0xbb8 | last update's time |
| +0x2d70 | trail (16 x 12 B at +0x2d78, start +0x2e38, count +0x2e3c; 0xd0 bytes copied to the job) |
| +0x2e40 | went off in a fire (1809b5220 sets it after a forced Detonate) |
| +0x2e41 | Scorch decal done |
| client +0x136c | m_vSmokeColor |

Other:

| Offset | Field |
|---|---|
| 0x181faa578 | smoke projectile list (next +0xb60; creation order). Walked only by 180349500, 18034cc30, 180988170, 1809b00c0 / 1809b0a10 / 1809b2a90, 1809bfb20 / 1809bfc60 / 1809bff80, 1809d7f20 / 1809d7f90 |
| 0x1818e4200 | 6-neighbour table (3-byte steps: -x, +x, -y, +y, -z, +z) |
| 0x1818e4250 | 26-neighbour table (int32 dx, dy, dz, 12 B: the 8 around in z, the 9 above, the 9 below) |
| 0x1818e9d40 | octree test object |
| 0x18178c240 | trace filter vtable |
| 0x181e0fb78 | 40.0 (fallback radius) |
| 0x18218e4f8 +0x28 | CGameSurfaceProperties table (0x20 B entries; index at the trace result's +0x10) |
| CGameSurfaceProperties | maxspeedfactor +0, jumpfactor +4, bulletPenetrationDistanceModifier +8, gamematerial +0x14, isstairs +0x19, isslippery +0x1a, allowsmokethrough +0x1b, reflectbullets +0x1c, reduceweaponimpact +0x1d, bulletspenetrate +0x1e; also soundstackmaterial, legacymaterialtag, climbable, bulletPenetrationDamageModifier |
| 0x181ec16c8 | CBasePropDoor (+0xcc8 m_eDoorState, 0 closed) |
| 0x181ec1b50 | CPropDoorRotatingBreakable (+0xf34 m_currentDamageState; +0xf30 m_bBreakable) |
| 0x181ec18c0 | CInferno |
| inferno +0x11a8 / +0x1190 | fire list / count; fire +0 point, +0xc centre, +0x14 z, +0x24 burning (and its timer) |
| 0x1817bfb38 | fire line filter vtable (taken as the plain filter) |
| TheBots 0x181fa5e10 | grenade list: +0x18 head index, nodes 0x10 apart from +0x10, entry {+0 grenade, +8 position, +0x18 live, +0x20 radius} |
| 0x1821ba1c0 | global the bot walk also needs (unread) |
| client 18223efe0 | bullet ring (vtable 181ca6620): entries 18223efe8 (36 B: start 12, end 12, time +0x18 f32, tracer byte +0x1c, strength +0x20 f32), head 18223f228, count 18223f22c |
| client 18223f230 | HE ring (vtable 181ca6638): entries 18223f238 (32 B: projectile 8, pos 12, time +0x14, smoke mask +0x18 uint), head 18223f2d8 (% 5), count 18223f2dc |
| client 18223f24c | 5-entry HE table (DepthNoCharacters test) |
| client 1825be9b8 / 1825be9c0 | smoke scene object list (nodes 16 B, next at +10) / head index |
| client 1825be9c8 / 1825be9cc.. | atlas slot free list: count 16, slots 15, 14, ... 2 |
| client 18257e040 | four 12-byte slots taking an HE's pos (use unread) |
| client 18257e030..3c | the flash (pos, time) |
| client 18256af48 / 18256af78 / 18256af88 | view origin / v1 (read as right) / v2 (read as up) |
| client 182535800 | tracer frequency cvar |
| weapon +0x7b0[attack] | tracer frequency |
| weapon vfn 0xbe0 | weapon type (4 shotgun) |
| HE projectile +0x12fc / +0x12d8 / +0x12dc | changed / tick / pos |
| scene object +0xd0 | tint |
| +0xdc | (c64.w source) |
| +0xe0 / +0xe4 | creation time / last regenerate time (RGBA8 bytes at o + 0xe0 in the regenerate) |
| +0xe8 / +0xf4 | box min / max |
| +0x100 | grid centre |
| +0x10c | atlas slot (object[+0x3c] in the mask) |
| +0x48 / +0x50 | point list count / data (12 B) (also +0x118 / +0x120 at object + 0xd8) |
| pawn +0x2a6 x 8 | overlay alpha |
| pawn +0x1538 / +0x1534 | overlay colour / age |
| SmokeLightProbeVolumeData_t | 0x1810 bytes per smoke pair: "Transform" +0x30, "VolumeMaxs" / "VolumeMins" +0x20 / +0x10, "Priority" (hash 0x33631172) +0x64, "LPVIndex" (0x7176fdea) +0x68 |
| PerViewConstantBufferCsgo_t | +0x24c (c36.w) mixed scale (1 not mixed), +0x250 (c37.x) overestimation, +0x254 (c37.y) bias, +0x258 (c37.z) 1 / scale, +0x25c (c37.w) log(view + 0x30), +0x260 (c38) log(view + 0x34) (near / far); c11 an int2 mask (blue noise; taken as 255) |
| view +0x1bb / +0x110 / +0x31 | MBOIT flag / attribute set / a view kind excluded from forced mixed |

## Constants

| Value | What |
|---|---|
| 640.0 / 20.0 | grid size / voxel |
| 32, 512, +-320 | n (`((int)ceilf(size / 2 / voxel) + 3 >> 2) * 8`), words (n^3 >> 6, one u64 per 4x4x4 brick), bounds |
| 0x3001, group 5 | build trace mask / collision group (flags 0x49, object set 0xf; grenade and owner ignored) |
| 0x3001, group 4 | box test |
| 0x8000 | Morton limit (> 0x8000: out of the grid); world entity index |
| 39 (0x27) / 40 | records needed / per fill |
| 43 | underhang placements cap |
| 0.8, 29 | fill's upward test / offset |
| 2000 us | Plat_TicksAfterMicroSecs time slice |
| 0x10b010 | work block size |
| 60.0 | emitter density |
| 0.1 s | update interval |
| 19 s | dissipation |
| 22.05 s | entity life |
| 166.0 | bot smoke radius |
| inferno_smoke_volume_density | 0.03 (18005c260, flags 0x4000) |
| bot_max_visible_smoke_length | 200 (flags 0x82000) |
| smoke_param1..5, smoke_use_noise_texture (server) | flags 0x4002 / 0x2000 (replicated rendering knobs); float loads near them 6.26, 8.27, 0.13 |
| 0x368c | demo version below which emitters are 16-byte float positions |
| 0x1818e9cb0 | job vtable |

Client cvars (registration stubs: float default in xmm2, handle in rcx; value at `[handle + 8] + 0x58`):

| cvar | default | flags | stub / handle | read by |
| --- | --- | --- | --- | --- |
| cl_smoke_edge_feather | 21 | 0x2002 | 180097570 / 1824c7198 | 180c9ba00 (+ 8 of 1824c7198: the overlay) |
| cl_smoke_lower_speed | 1 | 0x2002 | 180097610 / 1824c71a8 | 180c686f0 |
| cl_smoke_origin_height | 68 | 0x2002 | 1800976b0 / 1824c7168 | 180c9ba00 |
| cl_smoke_torus_ring_radius | 61 | 0x2002 | 180097750 / 1824c7178 | 180c9ba00 |
| cl_smoke_torus_ring_subradius | 88 | 0x2002 | 1800977f0 / 1824c7188 | 180c9ba00 |
| cl_smoke_volume_growth | 1 | 0 | 180097890 / 1824c71c8 | no reader found |
| cl_smoke_volumeprop | true (bool) | 0 | 180097930 / 1824c71b8 | 180c9ba00 (+ 8 at 1824c71c0) |
| smoke_param1..5 | 6.26, 8.27, 0.13, 0, ? (int / bool via 1819aca80) | 0x2000 | 180099d40.. / 1824c7228..68 | no reader found |
| smoke_use_noise_texture | true | 0 | 18009a070 / 1824c7278 | no reader by handle (D_SMOKE_USE_NOISE_TEXTURE combo) |
| smoke_volume_lod_ratio_change | 0.6 | 2 | 1800f55a0 / 1825be9a0 | 180d2f7c0 |
| sv_smoke_volume_blind_start | 0.2 | 2 | 1800e75c0 / 1825710b8 | 180ca07b7 |
| cl_use_prompt_smoke_density | 0.03 | 0x4008 | 1800e5020 / 182571020 | 180c6182b |
| r_csgo_mboit | 1 | | 180124370 / 1825f6668 | |
| r_csgo_mboit_bias | 5e-6 (0x36a7c5ac) | | 180124420 / 1825f6698 | |
| r_csgo_mboit_overestimation | 0.01 (0x3c23d70a) | | 180124610 / 1825f6688 | |
| r_csgo_mboit_use_4_moments | 0 | | 180124760 / 1825f66a8 | |
| r_csgo_mboit_force_mixed_resolution | 0 | | 180124570 / 1825f66c8 | |
| r_csgo_mixed_resolution_particles | 1 | | 180124a10 / 1825f6628 | |
| r_csgo_mixed_resolution_particles_scale | 2 (int) | | 180124b60 / 1825f6648 | |
| r_csgo_upscale_depth_threshold | 3 | | handle 1825f66e0 | 1811e0360 |
| r_csgo_joint_upscale_sigma | 0.002 | | handle 1825f66d0 | 1811e0360 |
| r_csgo_smoke_fullres_pass | 1 | | 1801266f0..1801269a0 | |
| r_csgo_smoke_fullres_enhance / _shadow / _upscale_discard_pixels_behind / _avoid_flat / _clip_sniper | 0 / 1 / 0 / 1 / 1 | | same stubs | |

## The build (server)

### Grid and voxels

- 1809b45b0(grid, centre, size, voxel): n = 32 (log2 at +0x30), words 512, bounds +-320; a 512-qword bitset and a
  512-byte array, zeroed.
- Voxel of p (1809d7150): `c = (p - origin) * 0.05 + 16` per axis (16 = n / 2, a static), truncated (cvttss2si), low byte
  (1809b0470: x, y, z in a uint's low three bytes). Index = Morton code: each byte spread with `(v << 8 ^ v) & 0x300f00f`,
  `(v << 4 ^ v) & 0x30c30c3`, `(v * 4 ^ v) & 0x9249249`, then `x + (y + z * 2) * 2` (x bit 0, y bit 1, z bit 2). Brick =
  index >> 6 (< 0x200), bit = index & 63.
- A voxel spans `o + (v - 16) * 20 .. + 20` per axis, centre `o + (v - 16) * 20 + 10` (float32, that order: 1809d6960).
- Packed voxel: x | y << 8 | z << 16 | 5 << 24 (5 = log2 32).
- Set hash: murmur3 fmix32 of the packed xyz: `(h >> 16 ^ h) * 0x85ebca6b`, `(h >> 13 ^ h) * 0xc2b2ae35`, `h >> 16 ^ h`.

### Trail, detonate, the pop

- Trail (1809d4650): the origin pushed when empty or the newest is more than 20 u away (dist^2 > 400); a ring of 16
  (1809cd180: full, oldest overwritten, start + 1).
- 1809b4190(vol, owner, pos, trail, time): owner handle (+0x6c); grid(vol + 0x10, pos, 640, 20); origin; vol[0] = 1; a
  fresh work block (solid bits from the grid's: all zero then); vol+0xc = time; the job {volume, the trail's 0xd0 bytes,
  owner handle}.
- At the pop 1809d2780 calls 1809b4090: vol[0] = 1, the origin, the work block freed and a new zeroed one with the grid's
  solid bits copied in, +0xc = the time. Emitters (+0x78), flags and dirty bricks carry over; densities, active sets and
  emitter counts start at zero. The pop is the first think (1809d4330) that finds the job done.

### The job (1809b2390)

1. The trail newest to oldest (index `(start + i) & 15`, i from count - 1 down): each a fresh search (queue and seen set
   cleared, records 0; the emitter counts are not reset between searches).
2. 1809bd920 at the point; for the oldest (i == 0) with nothing queued, 1809bd150.
3. Something queued: column tables 0xff, the fill 1809bb050, then (owner still there) 1809d0110 and 1809bc190.
4. Records > 39: 1809b2ec0, done; else the most records so far kept (swapped into the trail slot).
5. After: fewer than 40 -> the best search's records; none: DevMsg `SmokeVolume: Failed to find detonation`.
6. Records become the emitters (swap into +0x78); work +0x10b008 = 0; +0xf0 = 60.

### A start (1809bd920)

The point's voxel (> 0x8000: none); its brick loaded; solid: 1809d58d0 from the point (solid neighbours to a local list);
queued something: done; else a line (180250e50, 0x3001, group 5, grenade ignored) up 20 u: clear -> the voxel there
(> 0x8000: done), its brick, solid -> 1809d58d0 from there; then the current voxel queued (and seen) when clear and
unseen; nothing queued: each solid neighbour in the list gets 1809d58d0 from the grenade's origin (no list).

### A step (1809d58d0)

Six neighbours (0x1818e4200), unseen ones; a TraceShape line from `from` to the neighbour's centre (filter 0x18178c240:
0x3001, group 5, flags 0x49, object set 0xf, grenade and owner ignored, no iteration); fraction >= 1 and not start
solid: brick loaded; solid and a list -> the list; clear -> queued and seen. A neighbour outside the grid (coordinate 32
or wrapped -1) reads its "solid" bit past the bitset (work +0x1008.. during the build: zero; past the block on -z) and is
queued.

### Fallback (1809bd150)

Eight points at 40 u: `x = V_sinf(i * 0.7853982) * 40 + x0`, `y = y0 + V_cosf(..) * 40`, `z = z0 + 40 * 0`; a clear line
from the grenade to each: its voxel queued (seen) when unseen, Morton < 0x8001, brick loaded and clear; else the voxel
above (z + 1) the same way.

### Brick load (1809d6b00)

If the grid has the brick (1809d6c40), its word copied from the grid's bitset into the work bitset, the brick marked in
+0x98 (+0x90 |= 2). Inlined copies in the fill, 1809d0110, 1809bc190, 1809b1850, the step 1809d1a90.

### The fill (1809bb050)

1. Pop the queue's head (FIFO ring, param_2[4] head / [5] tail).
2. For the 26 neighbours (0x1818e4250) inside the grid: add its emitter count to a sum; unseen: brick loaded, queued if
   clear, seen either way.
3. If the popped voxel's count and the sum are both 0: the 26 neighbours' bricks loaded; dir = normalize(centre -
   origin) (each part `((v - 16) * 20 + o) + 10 - o`; length `sqrt((y y + z z) + x x)`; 1e-17 .. 1e17 guard; zero ->
   (0, 0, 1)); `d = x * 0 + (y * 0 + z)`; `d <= 0.8 -> 0`; the point `centre + (d * 29 * 0, d * 29 * 0, d * 29)`: its
   voxel v2; v2 != v: its brick, and if clear the count goes on v2 instead of v; the column (`x * 32 + y` of v:
   param_2[0x14 + ..] lowest z, [0x414 + ..] highest) keeps v2's z as its lowest / highest (a highest above 0x20 is
   unset); a record {v2, 0.0} appended (param_2 + 0x816, count [0x814]; v2 even when solid); the count + 1; 40 records
   end it.
4. Time-sliced: every 2 ms (Plat_TicksAfterMicroSecs(2000)) a yield (1816a4690), the owner re-checked (gone: stop).

### Flat tops (1809d0110)

For y, for x: the column's highest z (low byte) < 0x20 and equal to the column before's (two unset in a row break the
run): `z' = z + k - 1` (k = 1, 2, 0 cycling: a counter mod 3, advanced at every flat top), its brick; solid: skip; its
count 0: the top's count 0, z''s 1, the column's highest (and lowest, if it was the highest) = z'. It then looks up the
record on the top voxel and copies its centre to the stack only (disassembly at 1809d05a8: nothing stored): the records
don't move; only counts and column tables change.

### Underhangs (1809bc190)

1. Records within 40 u across (`sqrt(dy dy + dx dx) < 40`) and 0..80 u above the origin taken out (count 0,
   swap-removed).
2. The rest sorted by z (V_qsort = the UCRT qsort, comparator 1809a35f0).
3. For y, for x: a column with a lowest z: up to 9 voxels below walked (each brick loaded) while clear; 4..8 clear below:
   from 3 under the lowest down, every 2nd voxel takes the last record's place (that record's count 0) as a new record
   (packed with level byte 0); 43 placed ends it.
4. The taken out and new ones appended, their counts + 1.

### Crowning (1809b2ec0)

The record within 60 u across (`dy dy + dx dx < 3600`) with the largest |oz - cz| (1808ad470); 1809b1850 (2 voxels from
it in the grid and clear) up -> {z + 1} appended, then +x, -x, then +y, else -y (no counts).

## The grid's solid voxels (VoxelOctree)

- 1809d6c40: the voxel's brick (Morton >> 6 < 512) not built: its coordinates (every third bit of the brick index),
  1809d3810(grid, brick, log2 n - 2 = 3, test 0x1818e9d40, no bounds), built = 1, true. Every caller that gets true marks
  it dirty (+0x98, +0x90 |= 2) and copies its u64 into the work block.
- 1809d3810: the node's 8 children (bit 0 x, 1 y, 2 z) at level + 1: child box in the grid's frame (size `(640 / 2^level)
  * 0.5`: 40 at level 3, 20 at 4; x: `-320 + c * size .. (size + c * size) + -320`); the test (slot +0x10, 1809d7530);
  a leaf (level 5) that touches sets its bit; an inner one that touches recurses.
- 1809c7bd0: TraceShape of the box (half extents `(max - min) * 0.5`) from its centre to its centre: filter 0x18178c240,
  0x3001, group 4, flags 0x49, no iteration, grenade and owner ignored. No hit (bit 0 of the result's +0x68, or start
  solid): clear. A hit on a box wider than 20: solid (recurse). A leaf: a world hit (entity index 0x8000) or none: solid
  unless the hit's surface (table 0x18218e4f8 +0x28, index at the result's +0x10) has allowsmokethrough (+0x1b), which
  tests eight 10 u sub-boxes (no ignore) and is solid if any touches something without the flag; an entity of class
  CBasePropDoor with m_eDoorState != 0, or CPropDoorRotatingBreakable with m_currentDamageState >= 2: not solid (a door
  not closed, or broken past damage state 1, is clear).
- Sub-box centres: `(w * 0.5) * k + ((size * 0.25) + min)` per axis, w the box's x size on all three axes (1809c80a9..
  adds the 0.25 term to the minimum first), half extents `size * 0.25`; the sub traces ignore nobody.
- allowsmokethrough: CGameSurfaceProperties filled by 180be8f60 from scripts/surfaceproperties_game.txt (default read from
  +0x1b and stored back), zeroed by 180c07590 (false unless set). True in the game txt for chainlink and audioblocker;
  with the vsurf's bases (a surface takes its base's entry, then its own keys) the physics surfaces that let smoke
  through are chainlink, chain, metalrailing (audioblocker isn't a physics surface in the vsurf).

## The dirty-brick order (CUtlHashtable<u16> at +0x98)

- Layout: +0 allocated, +4 flags, +8 slots, +0x10 count, +0x14 capacity, +0x18 min size 0x20, +0x1c no-grow. A slot is
  {u16 word, u16 key}: word bit 15 empty, bit 14 "last of its chain", bits 0..13 the hash's low 14 bits. Home =
  `(h14 * 0x4001) & (capacity - 1)`, probing on.
- Insert 1809ae490(table, &key, fmix32(brick), 0): lookup along the home's chain (hit: nothing); growth when `count * 4 +
  4 > capacity * 3` (unsigned, unless +0x1c) to `(count * 4 + 4) / 3` (1809b91a0: at least the min size, the next power
  of two, old slots re-placed from the top slot down through 1809b8fc0); then the element at its home: when the home's
  occupant is of the same chain the new one isn't last and the occupant moves on (1809b46d0: along the chain to the
  first empty slot, taking the "last" mark); an occupant of another chain moves on too.
- 1809b9ba0 walks slots 0..capacity-1 (occupied: word >= 0) and after the record empties them from the top slot down,
  capacity kept.
- The rehash's capacity is the largest power of two the allocation holds (g_pMemAlloc vfn 0x88, the block's size): taken
  as the size asked for (4 bytes a slot).

## The wire (m_VoxelFrameData)

A log of update records in CSmokeGrenadeProjectile's m_VoxelFrameData (CNetworkUtlVector<uint8>, +0xb90; size
m_nVoxelFrameDataSize +0xba8, record count m_nVoxelUpdate +0xbac): every update (1809d6590) appends one record and never
trims, so a late joiner replays the whole log. A record carries only what the client cannot recompute: the emitters, the
world's solid voxels (bricks as the server voxelizes them) and the dissipation flag. The client runs the same step itself,
one record at a time (1807e0d70 -> 1807c70f0: find the record whose seq is the next expected, apply it 1807c8990, step
1807c5ed0, rebuild the texture 1807dff70, seq + 1; an older record is skipped; a record ahead stops the walk, return 2).
Size: ~2.5 KB a smoke over its 22 s (de_dust2: a first record of ~0.7 KB with the bricks, then ~5-10 B a record).

A record (1809b9ba0 writes, 1807c8990 reads), little-endian:

| Bytes | Field |
|---|---|
| u16 | seq: 0, 1, 2, ... (+0xd0) |
| u16 | len: the bytes after this field |
| u8 | dissipating (work +0x10b008: the effect's age past 19 s, 1809d47d0) |
| u8 | flags: 1 emitters follow, 2 bricks follow (the first record has 3) |
| flags & 1: u8 n, then n x 8 bytes | emitters: u32 packed voxel and f32 weight; replaces the client's list |
| flags & 2: u16 count, then count x 10 bytes | solid bricks: u16 brick (Morton >> 6, 0..511), u64 its 64 solid bits (bit i = voxel brick x 64 + i); count 0 means all 512 follow |
| u8 m, then m x 20 bytes | holes: u32 countdown, f32 x, y, z, f32 radius (the server never adds one: m is 0) |

Client apply 1807c8990: dissipating byte, flags byte; flags & 1: the old emitters' counts 0, n, n x 8 B (demo older than
0x368c: 16-byte float positions), the new counts 1; flags & 2: u16 n, n x (u16 brick, u64 bits) into the solid bits;
u8 m holes (the list replaced).

Timing: an update when `curtime - +0xbb8 >= 0.1` (1809d6590): every 7th tick at 64 tick (0.109375 s), the first on the
pop tick (1809d2780 sets +0xbb8 = 0); several smokes share one update a frame (180988170: round-robin, the first due one
updates and the walk stops). Updates run until the entity goes (22.05 s).

## The simulation (1809b3630 server / 1807c5ed0 client)

Server update 1809d6590 (m_bDidSmokeEffect and `0.1 <= curtime - +0xbb8`): +0xbb8 = curtime; a 0xc00-byte buffer with
the old frame data, 1809b3630(vol, buffer); m_nVoxelFrameDataSize = its size, m_nVoxelUpdate + 1, m_VoxelFrameData grown
to the size rounded up to 0x200 and the changed bytes written (each marked changed).

180988170 = CSmokeVolumeSystem slot 32 (ServerPostEntityThink: frame.md, after the think pass and the I/O queue): a
queue of every smoke projectile (0x181faa578, creation order), refilled at a call's start when empty; pops until one
updates (1809d6590 is 0 for a smoke not gone off: its turn is used), skipping dead handles. CSmokeVolumeSystem's slots
beyond IGameSystem's defaults: 31, 37 / 64 (empty), 32 (the update), 60 (a forward).

1809b3630:

1. Emitter pass 1809d09e0: +0xf0 = 60.
   - First pass (+8): each emitter's 26 neighbours in the grid, inactive and clear: density += `60 * 0.5` (both
     buffers), active; the emitter's own voxel active; the emitter appended to +0xc0.
   - Else: cap = `max((1 - weak / 40) * 3.5, 1)` (weak: weights not >= 0.01); each emitter in the grid: appended to +0xc0
     (before it changes); not dissipating: dist = |centre - origin| (`(dz dz + dy dy) + dx dx`); dist <= 80: `w *= 0.8`;
     else 1809b1650 (> 0.2 = crowded): w <= 0 (or NaN) -> 1 unless crowded; w > 0 -> `* 0.8` if crowded else 1; density
     = `min(cap * 50, (1 - w) * 60 + density)` (minss); dissipating: density 0, count 0; active; the entry copied to the
     other buffer.
   - The holes loop runs before it (moves or removes emitters; nothing with no holes: dead on the server).
2. Server only: +0x90 & 1 and fewer than 5 emitters in +0xc0: no emitters (+0x78 = +0xb8 = 0). Both: dissipating: no
   emitters. +0xf0 = max(+0xf0, 0).
3. Each active voxel of the current buffer (512 u64 words in order, low bit first; each word read once): 1809d1a90:
   - Solid -> its other-buffer density 0.
   - w = `clamp(d_other / 50, 0, 1)`. For the six neighbours (table order): the server loads its brick; in the grid and
     clear: nd = its current density; k = 0.9 / 1.25 for the four sideways ones by `((-dy * vy) - vz * dz) - vx * dx >
     0.2` (the neighbour's direction; NaN takes 0.9), 0.79 down, 1.2 up; `flow = (nd / 6) * ((1 - w) * k)`; the
     neighbour's other density = `max(0, it - flow)` (maxss); inflow += flow; the neighbour inactive and this voxel's
     current density > 5: the neighbour active in the other buffer. Else the face's normal (-d) kept.
   - On the border (a coordinate 0 or 31): other density `* 0.3`, done.
   - Else other density = `inflow + it`; g = `(l[-x] - l[+x], l[-y] - l[+y], 0)` (neighbours' densities, 0 blocked); for
     each blocked face `g += -(g . n) n` (`(gz nz + gy ny) + nx gx`); normalized (length `sqrt((gy gy + gz gz) + gx gx)`,
     `1 / len` times; out of 1e-17 .. 1e17: 1814738b0 in double; zero: zero) into the direction; density = `max(0, it -
     0.5 * (1, or 0.5 dissipating))`.
   - With holes: the holes' mean push direction replaces g; density = `max(min(d, 15), d * 0)` within 80 u of the origin,
     `d * 0` beyond.
4. Server: CRC 1809b6af0 (debug), the record 1809b9ba0, then flags 0, dirty set cleared, +0xb8 = 0, seq + 1.
5. The current buffer's active voxels take the other buffer's entries; `active[cur] |= active[other]`, copied back;
   buffers swap; holes' countdown - 1 (0: swap-removed); +8 = 0.

Holes: nothing in server_20261105 adds one (writers of +0x118 / +0x120: the constructor 1809b0318, the destructor
1809b0d20, the countdown 1809b389c; no lea of +0x118 feeds an append), so the record's hole count is always 0 and the
emitter motion in 1809d09e0 is dead code on the server.

## Line of sight (server)

- 1809d5000(vol, a, b, visitor): the grid's box (origin +-320); a outside: clipped (181489c20 -> 181476b30) and moved 1 u
  in; a 3D DDA from a's voxel to b's (steps `20 / |dir|`, the first from V_modff of `(p - mins) * 0.05`), at most 128,
  stopping when the voxel's centre leaves the box, the visitor says stop, or b's voxel is reached. The client's
  1807cd7f0 -> 1807de9d0 is the same walk.
- 1809bfc60 (IsLineBlockedBySmoke 18032a570: >= 1.0): per smoke with m_bDidSmokeEffect, visitor 1809b14f0: solid -> 1,
  stop; `clamp(d / 50) >= 0.8` -> 1, stop; > 0.1 adds, sum >= 0.2 -> 1, stop; the smoke's result `* smoothstep(22, 17,
  t) * smoothstep(0.1, 1.5, t)` (1809af7d0, t = curtime - +0xc) summed, >= 0.2 -> 1.0; else `clamp(sum / 0.2, 0, 1)`.
- 1809bff80 (the damage feedback's < 1.4): the same walk, visitor 1809b1150: a clear voxel adds `clamp(d / 50)`; a solid
  one adds the max over its six active neighbours of a read of its own density (0); same weight, no early out.
- 1809bf8e0: weight x 1809bf980: the point's voxel in the grid, brick built, clear: `clamp(d / 50)`, else 0. 1809bfb20
  sums it over the smokes.
- A molotov goes out when more than 1/3 of its fire areas are in smoke (180349500).

## Bots

CCSBot::IsVisible (1802d3ba0) calls IsVisibleThroughSmoke 18032a6b0; IsLineBlockedBySmoke is used by spotting
(1801d7460) and CBtDecoratorPickerBlockedBySmoke (1803233b0, slot 10).

IsVisibleThroughSmoke: TheBots' grenade list (18032b550 clears it); a smoke's radius is 166 from its pop (1809d2780 ->
18032b710); per live entry 1803260c0(r^2, &pos, from, to): the sphere at pos + (0, 0, 60); -1 when `from` is within 0.95
R and `to` within R (visible at once); else `2 sqrt(r^2 - d^2)` for the segment's nearest point at d^2 < r^2 (sums
`(y y + x x) + z z`, projection `(z uz + y uy) + x ux`); visible when the sum <= bot_max_visible_smoke_length (200).

## The inferno

- 180349500 (on the inferno's own think): burning flames counted; for every smoke and every burning flame 180342d10:
  +0x2e40 set and the flame within 16 u: out; 1809bfb10 (1.0) -> the flame's point + (0, 0, 20), then + (0, 20, 20),
  (-0, -20, 20), (20, 0, 20), (-20, 0, 20) (`20 * offset + point + 0`), denser (1809bf8e0) than
  inferno_smoke_volume_density: out (180347c00). Burning before > 2 and before / 3 < out: the rest out, `Molotov
  extinguished: when %d/%d fire areas were covered by smoke (exceeded 1/3rd).`, Molotov.Extinguish, inferno_extinguish
  (userid, x, y, z). (The old cylinder test after it, 22500 - ramps on dz, is dead.)
- CreateFire 180345dc0 (and 180352350) asks 18034cc30: no new fire where a smoke is (180342d10 against each smoke).

Landing on a fire: vfn 0xa00 runs at the end of every collision (1809cf572); the smoke's 1809cb9d0 -> 1809b5220 (then a
timer at +0xbb4, 0.046875). Until +0x2e40: the entities in a 512 u sphere (180bf7da0, 0xc3001, group 3) that are a
CInferno, each through 180343040 -> 18034d880: per burning fire, across within 10 + 60 of its centre, up `|z - (its z -
20)| - 20 <= 0` or `(that)^2 + across^2 < 70^2`, then 1803443c0: a line from centre + (0, 0, 30) to the point, else from
the centre, else (once) from 30 u above the point (0x1001, group 3, grenade ignored; filter 0x1817bfb38); the nearest
such fire's point wins. Then TraceEntity (180c2e9c0, 0x200003001) from the origin to it, the grenade teleported to its
end, stopped (movetype none), the trail takes the point, Detonate now (vfn 0x9a8), +0x2e40 = 1.

## The client: in-smoke overlay

- Torus path 180c9ba00 (the fallback when 1807cd400 is 0): the nearest live smoke whose horizontal distance from the eye
  to its origin + (0, 0, cl_smoke_origin_height) is under ring_radius + subradius (149), age `(tick - begin) * interval
  <= 16.75`, sets the overlay colour (+0x1538 = m_vSmokeColor) and age (+0x1534).
- Volume path 180ca06e0 (from 180c686f0): per smoke the density at the eye 1807cd230 (the eye's voxel, not solid:
  `clamp(v / 50, 0, 1)` of the current buffer `* smoothstep(22, 17, age) * smoothstep(0.1, 1.5, age)`) over
  sv_smoke_volume_blind_start 0.2, clamped; colours averaged by it; returns the sum clamped (kept at the old value while
  0.2 < it < old and old > 0.8). 180c686f0: a rise at once, a fall by Approach at cl_smoke_lower_speed x frametime; the
  results go to m_flLastSmokeOverlayAlpha / m_vLastSmokeOverlayColor (reader unread).
- overlay_smoke D_ACCUM_PASS: a small accumulation (the composite samples its 4 corners at 5 % / 95 % of m1.x / m0.x) of
  the smoke's colour where the smoke depth's y < -0.55: a falls `max(6 / 255, lerp(3.5, 1.5, a)) * dt`, rises toward
  the smoke's alpha at `6 * dt`, the colour follows at `2 * dt`, halved on g_bHEGrenExplosion; its draw: corners
  bilinear, alpha `smoothstep(0, 0.95, a)` (the viewmodel pass: `alpha * alpha * 0.75`). SmokeOverlayDataA / B.vtex
  ("rt_SmokeOverlayData", "OverlaySmokeUpdate", "OverlaySmoke") are made at the size of the target in the layer
  builder's [rbp + 0x2e0] (description by render system vfn 0x150, remade when it changes).

## The client: bullet trails and HE holes

- Add a bullet 180d2c780(start, end, tracer byte, strength, mode, lefthand): the smoke scene objects walked; the first
  whose box (o + 0xe8) the segment hits (1817590b0(box, start, end - start)) takes it, the others never see it. mode 1
  (your own shot): start = view origin - v1 x 7 (-7 left-handed) - v2 x 5; mode 2: start = origin - v2 x 8. time =
  curtime. Full (16): head entry replaced, `head = (head + 1) & 15`; else appended at `(head + count) & 15`.
- Callers: 180901390 (records {weapon, shot index, attack index, start, end} flushed by 180901230): strength 1.0, 0.25
  for a shotgun (vfn 0xbe0 type 4); tracer byte = the weapon's tracer frequency != 0 (+0x7b0[attack], or cvar 182535800
  when >= 0); mode 0 for others (start = the muzzle record), 1 / 2 for the local player. Every bullet (before the
  `shot % frequency == 0` test). 1807dbe30 (decoy's fake shot): start = the decoy, end = a seeded random direction x
  100, tracer 1, strength 0.3 (0x3e99999a).
- Add an HE 180d2cd00(projectile, &pos, time): mask = OR over the smokes of 180d1f260: 18174a510 (box + 0x18 / + 0x24 vs
  a 256 u sphere), then each point of the object's list within 256 u (d^2 < 65536): a line (18022fee0, 0x2001, group 4)
  from the blast; the first unblocked -> `1 << slot`. No bit: nothing kept. Full: head replaced, `head = (head + 1) % 5`.
  Then the first of four zero slots at 18257e040 gets pos. True -> SmokeGrenade.Clear: 1810d03d0 (+0x12fc changed and
  +0x12d8 > 0: time = `+0x12d8 * 0.015625`, pos = +0x12dc).
- Remove an HE 180d1f020: swapped with the newest, count - 1; from the HE projectile's destructor 1810c6420 (and
  180cac130). On the server CBaseGrenade::Explode 1808c3200 removes the HE 0.1 s later, so a hole lives about 0.1 s plus
  the network delay, not the renderer's 5 s window.
- The point list (o + 0xd8: +0x118 count / +0x120 data): filled by RegenerateTextureBits' first call from the volume's
  list at + 0x80 (count + 0x78, 8-byte entries, 1807e0ea0 turns each into a world point).

## The client: the volume texture (RegenerateTextureBits 1807dff70)

- Atlas SmokeFluidA 542 x 32 x 32 (0x21e; 1807d3f80, format 0x1e), RGBA8, 34 texels a smoke (`x = (34 slot + 32 u) /
  542` in the shader); SmokeLPV%dx%dx%d the lighting atlas. Slots from the free list.
- A 32 KB RGBA8 buffer (o + 0xe0, zeroed once). The current set's voxels (bitset at +0x1008 + idx x 0x1000, idx at
  +0x100) in Morton order: d = 1807d90a0(v), v = the first float of the voxel's entry at `+0x3008 + ((1 - idx) * 0x8000 +
  voxel) * 16`; texel `((z * 32 + y) * 32 + x) * 4`: R = old G, G = d, B = old A, A = d. Its six face neighbours inside
  the grid (Morton < 0x8000) and solid (+0x8 bitset): into a hash set, the first voxel's d kept (fmix32). After the walk
  each such neighbour: R = old G, G = its d, B = old A, A = 0. Voxels not in the set are untouched (a voxel once reached
  stays in the set; its byte decays to 0).
- Box: min / max over voxels with d != 0 and their solid neighbours, -2 / +2, clamped to 0..32 (1807c53c0), world =
  `(v - 16) * 20 + origin`; none: left inverted at +-FLT_MAX (the scene object's box fails every test: nothing drawn).
  Stored at o + 0xe8 / 0xf4 (+0xe8..+0xfc). o + 0xe4 = now. Uploaded at x = slot x 34 (0x22) (renderer vfn 0x270).

## The client: the renderer (180d20800) and SmokeConstantBuffer_t

0x9c0 bytes (LockDynamicConstantBuffer), per smoke i < 16 ("Unable to render more than %d smokes", 0x10) from its scene
object o:

| reg | bytes | value |
| --- | --- | --- |
| c0[i] | +0x000 | o + 0xe8 box min, 1 |
| c16[i] | +0x100 | o + 0xf4 box max, 1 |
| c32[i] | +0x200 | o + 0x100 grid centre (uvw origin), 1 |
| c48[i] | +0x300 | x: now - o + 0xe0 (age); y: clamp((now - o + 0xe4) / 0.1) (1807cd430: the frame blend); z: (float) o + 0x10c (atlas slot); w: smoothstep(clamp((age - 6) / -11)) x 0.25 |
| c64[i] | +0x400 | o + 0xd0 tint (multiplies the light), w: (now - o + 0xdc) x 0.5 when o + 0xdc != 0 else 0 (unread use) |
| c80[i] | +0x500 | x: smoothstep((age - 22) / (17 - 22)) (1807cd420 22, 1807cd410 17: the fade); y: smoothstep((age - 0.1) / 1.4); z: smoothstep((age - 4) / 14); w: smoothstep((age - 0.1) / 1.9) |
| c96 / c97 | +0x600 / +0x610 | union of the boxes (1801bcf20) |
| c98 | +0x620 | the C4: when 1 < now - t < 11: (origin, now - t - 1) |
| c99[k] | +0x630 | bullet k: start.xyz, age (0 <= now - time < 1); then .z += age x 10 |
| c115[k] | +0x730 | lerp(start, end, age x 10) (not clamped), tracer byte 0 / 1; then .z += age x 10 |
| c131[k] | +0x830 | strength, 0, 0, 0 |
| c147[j] | +0x930 | HE j (0 <= now - time < 5): pos, time |
| c152 | +0x980 | HE masks as floats (5 used) |
| c154 | +0x9a0 | a flash: 18257e030..3c (pos, time), held up to 1 s |
| c155 | +0x9b0 | x: smokes drawn, y: bullets, z: now (180d25e00), w: HE count |

- c98: 180853e30 (gamerules + 0xb0 > 0) and 180cb36f0 (planted C4s: the one with + 0x12bd set and the latest + 0x12b8,
  its explosion time). Shader: a shell `r = w * 3000` clearing between r - 4000 and r (r - 20000 .. r - 4000 fading back),
  the floor's 48 u kept, only for smokes older than w.
- c154: 1807dfdb0 with a model name containing "flashbang" -> 180d2cbe0: the first smoke whose box is within 300 u
  (18174a510) -> 18257e030 = (pos, now).

## The client: the raymarch (smoke_volume_cs)

shaders/vfx/smoke_volume_cs_vulkan_50_cs.vcs, 291 dynamic combos (D_MBOIT_PASS1/2, OPTIM, D_SMOKE_INSTANCES 1..6,
4_MOMENTS, QUALITY, USE_NOISE_TEXTURE, NEW_VISUALS, PERF_TEST); read: D_MBOIT_PASS2, D_SMOKE_INSTANCES=6, D_SMOKE_QUALITY,
D_SMOKE_NEW_VISUALS. Material materials/dev/smoke_volume_cs.vmat: g_flRayStepLength 6, g_flDensity 0.85,
g_flSmokeNoiseStrength 0.8, NoiseSpeed 1.5, NoiseScaleLow 3, NoiseScaleHigh 7, NoiseMin 0, NoiseMax 1.05, NoiseOffset
-0.95, NoiseStrengthLow 0.5, High 0.35, BoilStrength -0.3, Wispy 0, AmbientStrength 0.6, DirectStrength 0.35,
InteriorDarkening 0.5, VolumeNormalBlend 0.5, AOEffectDistance 16, Strength 0.06, g_vSmokeColor 1 1 1, noise
materials/dev/noise/worley_perlin_z0000.

Per pixel (the mask texture's bit per smoke): the ray against the union box, then per smoke box an interval; start
`t = max(tIn, 4) + 6 * frac(bluenoise + time * 0.618034) * 0.8 * lerp(0.1, 0.8, sat((tIn + 150) * 0.05))`; end
`min(box exit, scene depth - 2)`; fixed steps of 6. At each step p:

- Bullets (recomputed for the first 16 steps, then every 16th): seg = head - start, v = p - start,
  `dn = sat(|v - seg sat(v.seg / seg.seg)| * 0.05 * strength)`; `fl = smoothstep(0, 0.01, age)(1 - smoothstep(0.01, 0.2,
  age))`; dn < 1: `hole = max(hole, smoothstep(0, 1, 1 - sat(age + sat(dn + 1 - sat(|p - head| * 0.01)))))`, `push =
  lerp(push, normalize(start - head), hole)`, `line = pow(1 - dn, 64) fl * 10`; tracer byte: `glow = max(glow,
  max(((1 - sat(|v| * 0.01)) fl)^2, line))`. Sample point `q = p + normalize(push) hole^3 * 20`.
- Density: `uvw = clamp(((q - centre) * 0.05 + 16) / 32)`; t4 = atlas; `(A, B) = lerp(t4.xz, t4.yw, c48.y)`;
  `w = A > B ? lerp(B, A, smoothstep(10, 40, |q - ray end|)) : B`; `d0 = sat(lerp(w, -0.05, hole))`; on when d0 > 0.01:
  `d1 = sat((d0 - 0.01) * 1.0101) * fade`; `d2 = sat(d1 + (1 - sat(|eye - q| * 0.1)) d1)`.
- HE j with bit (1 << slot) and `dt = now - time < age - 0.4`, |q2 - pos| < 250: `k = (1 - smoothstep(0, 2, dt))^128`;
  `floor = sat((48 - g) / 48)(1 - smoothstep(0, 7, dt))` (`g = max(0, |q - ray end| - min(20, |scene hit.z - centre.z| *
  2))`; 0 for a character pixel); `q2 = lerp(q2, pos, (1 - smoothstep(100, 250, dd)) step(dt * 1250, dd)(1 - k))`;
  `keep = min(keep, max(smoothstep(200, 240, dd + 250 k) + smoothstep(0.5, 5, dt)^1.8, floor))`; `d = lerp(0.02 d2, d2,
  keep)`.
- c98 (c98.w > 0 and < age): a sphere at 3000 u/s x c98.w from c98.xyz.
- Noise: L = uvw - 0.5, P = 7 L, rotated about z by `0.04 t + (0.2 + (sin 5 P.z + 0.5) 0.15) sin(t/2 + 0.5) sin(0.187 t +
  0.5) 0.2` (t = time x NoiseSpeed), wobbles 0.05; `n1 = tex((|P * 3| - (2, 2, 4.5) t * 0.1) * 0.07)`, value `(x + 0.95
  y) * 4.6` after lerp(NoiseMin, NoiseMax, n); a boil warp of P by the gradient normal; n2 at `P2 * 7 * 0.07`;
  `nz = lerp(0.95, sat n1, 0.5) + lerp(0.95, sat n2, 0.35 dot(dir, fwd) sat(|q2 - eye| * 0.005)) - 0.95`.
- Growth (c80.w < 1): g = clamp(c80.w, 1e-4, 0.9999), e0 = smoothstep(0, 0.8, g), e1 = smoothstep(0.2, 1, g):
  `d * smoothstep(e0, e1, |(L.xy, 1.2 L.z)|)` (e0 >= e1: a sphere opening out), or `d * g` when equal.
- `final = lerp(d - (1 - nz), d + nz, d) * sat(fade * growth * 8)`; `alpha = smoothstep(0, 0.2 / (0.85 lerp(0.5, 2,
  acc.a)), final)`; colour: the LPV atlas' ambient x the darkening terms x nz + the sun x shadow x (1 - hole), tinted
  `lerp(c, c * tint * lum ratio, 0.5 (1 - c80.z))`, `lerp(c, c * keep, 0.6)`, `+ c (8, 4, 0) glow`, + the c154 flash;
  composited front to back in 6 / 4 = 1.5 units a step; out at alpha > 0.991.
- g_bExtraSample: after the loop, one more step at the ray's end (`start + dir * len`), each smoke tested at the last
  step's t (`t - step`), weighted `(tStop - (t - step)) * 0.25` (lines _13238 / _21812 / _13244), with the bullets'
  fields as the loop left them.
- Blue noise: textures/dev/blue_noise_256.vtex (core pak01; engine attribute `BlueNoise`, hash 0x88243422, named in
  client and scenesystem), 256 x 256 RGBA8888; reads `.x` at `pixel & c11`.
- The march's scene texel is `_22509 * g_MixedResolutionScale` (pixel x 2). The characters test (s0_d199 230-249: the
  scene without the characters > 10 u further along the ray) keeps the HE floor term (656) and zeroes the C4's (722).

### Lighting

- Volume normal (g_flVolumeNormalBlend 0.5): density taps at uvw + up x -0.03 and + right x 0.03 (right = cross(forward,
  up)), `nVol = normalize(d - dRight, dDown - d, 0.06)` (view space).
- Noise gradients: the low octave also at `D * 3 + up * 0.2` and `+ right * 0.2`, `g1 = normalize(n1 - n1r, n1 - n1u,
  0.8 / 3)`; boil warp `P2 = P + V^T (g1 + nVol) n1^0.1 * boil * 0.2 + (2, 2, 4.5)(n1 - 1) 0.2 boil L.z`; the high
  octave's gradient the same way at `P2 * 7 + up / right * 0.2`.
- Normal `nW = V^T (lerp(V n0, nVol, 0.5) + (g1.xy * 0.5 + gh.xy * lerp(0.5, 1, sat(n1 - 0.5)) * hiStr, 0) * 0.5 *
  lerp(1, 2, sat((200 - |q - centre|) * 0.005)))`, `n0 = normalize(L) * (1 - sat(HE floor term))`.
- LPV atlas at `clamp(lerp(L (n0 . nW), normalize(nW + (0, 0, 0.5)) |L|, 0.2) + 0.5, 0.03, 0.97)`.
- Sun: `d = lerp(n0, nW, 0.5) . sunDir`, `pow(sat(0.8 d + 0.2), 1.5) + pow(sat(1.4 d - 0.5), 3)`, `* LPV.a * lerp(1,
  shadow, 0.75)`; shadow = `min(lerp(cascade visibility, 1, sat(dist * c12 + c11)), g_tParticleShadowBuffer.z)` (p = pL,
  dist from the eye; cascades: PerViewLightingConstantBufferGpu_t m13, a 4x4 per cascade, the shadow atlas, 4- to 9-tap
  PCF; the particle shadow buffer is built at Very High only).
- Ambient: the LPV's rgb with its HSV saturation x 1.1; `normalize(a) min(|a|, 4) * ...`.
- Per unit of the step: AO `smoothstep(0, 0.2, final + 0.3) * sat((16 - g) / 16) * density * 6 * 0.06` and the sun term
  summed; at the end `aoK = sat(ao - a * 0.2)`: rgb x (1 - aoK), a + aoK; rim light `rgb * (1 + sun² * (r + r^50 * 8)(1 -
  sqrt a) a * Σsun * 0.25)`, `r = pow(sat(dir . sunDir), 4) * 0.25`; a clamped 1e-5 .. 0.9999.
- Flash (c154): `(1 - smoothstep(0, 0.3, now - t)) * (1 - smoothstep(0, 300, |pL - pos|))` added, `pL = q + nW (n2 - 1) *
  8`.

### The lighting volume (smoke_volume_lpv_cs)

One thread per voxel (x, y, slice), the smoke from `SmokeConstantBuffer_t._m0[z].w` (atlas slot), written at x = 34 x
slot + voxel x. For the voxel's centre `p = (v - 16) * 20 + 10 + centre`:
- The volume: the smoke's `LightProbeVolumeData_t` list (`_m0[smoke]` count, `_m1[smoke * 32 + i]` = {box min, box max, a
  world -> local 4x3, priority `_m3`, per-view index `_m4`}); distance outside each box (`|max(min - l, 0) + max(l -
  max, 0)|`), 0 inside; kept: inside beats outside, then the higher priority, then the nearer (half-voxel test against
  the voxel's own box for an outside one).
- `l = PerViewLightProbeVolumeConstantBuffer_t[i]._m0 * p`; `l.z /= 6`; clamped to `_m1 .. _m2` (half a texel in);
  `l.z *= 6`; `uvw = l * _m4 + _m5`; `uvw.z /= 6`.
- n = normalize(p - centre); faces z + {0, 1/6, 2/6} for +X +Y +Z, + {3/6, 4/6, 5/6} for a negative component
  (`step(n, 0)`); `rgb = Σ face * n²` (three bilinear taps of g_tLPV_Irradiance) `* _m3.xyz`.
- Plus every barn light (g_BarnLights: frustum, cookie, attenuation, the shadow map's 4 / 9-tap PCF) x max(0, n . L),
  each scaled by `lerp(1, 0.1, sat((sqrt(lum(color)) * range - 80) * 0.01))`.
- `a = 1 - dot(g_tLPV_Shadows at saturate(l) * _m4 + _m5, the sun's channel mask PerViewLightingConstantBufferGpu_t._m4)`.
- The list: 180d323b0 fills SmokeLightProbeVolumeData_t from the scene system's light-probe query over the smoke's box
  (centre +- 32 voxels x 0.5), up to 32 volumes. m_Entity_nPriority comes from the `indoor_outdoor_level` key (field
  tables 1801fc610 / 1801fcdc0); its copy into the "Priority" attribute is assumed from the names. (de_dust2: 43 volumes;
  keys indoor_outdoor_level, array_index, ...)

### The noise texture and the sounds

- materials/dev/noise/worley_perlin_z0000_tga_37c9ebc1.vtex: 128 x 128 x 128 RGBA8888, 1 mip; R 0..199 (mean 18.9), G
  17..69 (mean 37.6), B 72..147, A 0..180 (the raymarch reads R and G).
- Sounds: BaseSmokeEffect.Sound (+ SoundDistant), SmokeGrenade.Bounce (+ Bounce_Can), SmokeGrenade.Clear,
  SmokeGrenade.PullPin / Throw, Decoy.PullPin / Throw. The decoy bounces with Flashbang.Bounce (1809b3e30).

## The client: upsample (mboit_mixed_upsample)

A full-resolution pixel from its four half-resolution texels: bilinear weights (the 8 x 8 group's 6 x 6 shared tile), x
`exp(-rel² / (2 σ²))` per texel when any relative depth difference `|z - z_i| / z` >= the threshold (`DepthThreshold`
hash 0x0b8dbc49 = r_csgo_upscale_depth_threshold, `JoinedSigma` 0x5f83a799 = r_csgo_joint_upscale_sigma; attribute names
are CUtlStringToken MurmurHash2, seed 0x31415926, of the lowercased name). Before that, with the smoke's depth range
(front, back; normalized log depth): behind the back (or no back, < -1) the plain bilinear weights, in front of the
front none. A pixel left with no weight is written (1, 0, 0, a) for r_csgo_smoke_fullres_pass: marched again at full
resolution.

## The client: MBOIT

Moment-based OIT over the translucents (spritecard: D_MBOIT_PASS1 / D_MBOIT_PASS2, ruled out with S_MODE_GBUFFER,
S_OPAQUE and D_PANORAMA_PARTICLE; csgo_effects: the same plus D_MBOIT_4_MOMENTS; smoke_volume_cs and smoke_volume: PASS1
/ PASS2 / OPTIM; resolves mboit_mixed_upsample, mboit_mixed_combine).

- Pass 1 (spritecard s0_d4, csgo_effects the same): `z = (log(dot(c28, p - eye)) - c37.w) / (c38 - c37.w) * 2 - 1`,
  `b0 = -log(1 - clamp(alpha, 1e-5, 0.9999))`; SV_Target0 = (b0, 0, 0, 0), Target1 = (z, z²) b0, Target2 = (z³, z⁴, z⁵,
  z⁶) b0; additive. D_MBOIT_4_MOMENTS keeps z..z⁴. An additive renderer (|SpriteCardPixelControls c1.w| = 0) discards
  when all its colour < 0.001 and takes alpha 0.0005 when not black (s0_d8 803-815, 946-958).
- Pass 2 (s0_d8 84-189): the six moments / b0 lerped toward the bias vector (0, 0.48, 0, 0.451, 0, 0.45) by c37.y, the
  Hankel / Cholesky solve, three roots by the trigonometric cubic, `T = sat(exp(-b0 * dot(...)))` at the surface's z with
  the overestimation c37.x; discard T < 1e-4; out `(rgb * a, clamp(a, 1e-5, 0.9999)) * T`; blend One / One colour and
  alpha (states: static 0 dynamic 8).
- The smoke: PASS1 (s0_d198 2591-2607) one surface per pixel: alpha = the march's (`a + sat(ao - 0.2 a)` when
  g_flAOEffectStrength != 0), skipped below 1e-5, at the depth where the march stopped (`_13193`: the step past 0.991 or
  the ray's end), added into the three moment UAVs; PASS2 (s0_d199) the colour x T at that depth (`_9769`). OPTIM (cs
  variant 4) resolves the colour at 4 depths between its optim depth range's x and y, adding each `colour * T`.
- mboit_mixed_combine (blend: D_HI_LOW and D_LOW_HI One / Zero, D_LOW_HI_OUTPUT and D_UPSCALE_SMOKE_DEPTH One / One;
  variants D_UPSCALE_SMOKE_DEPTH, D_HI_LOW, D_MBOIT_4_MOMENTS): D_HI_LOW (s0_d0) hi moments bilinear at the low pixel;
  D_LOW_HI (s0_d1): the hi pixel's device depth d vs the four low texels' (gathered), `rel = |d - d_i| / d`; with the
  smoke's depth (unless g_bIgnoreSmokeDepth): the optim depth's front / back gathered, a pixel behind every covered
  texel's back with all four covered takes rel 0; all `rel < lerp(0.0012, 4e-5, sat((d - 0.97) * 33.33))` -> bilinear,
  else Gaussian weights (sigma `lerp(0.0009, 6e-5, sat((d - 0.9) * 10))`) x bilinear, < 1e-5 in all -> point sample;
  D_KEEP_FULL_RES (s0_d4) discards where SmokeFullResMask is set; D_LOW_HI_OUTPUT (s0_d2) output up, additive, discarding
  where the low zeroth is 0.
- mboitfinal (materials/dev/mboitfinal.vmat; loaded by 1811cba30, drawn by "MboitFinalPass" 1811e1b80 / 1811e2920): PS
  s0_d0 `c = MoitFinal[px]` (point), `t = 1 - exp(-zeroth[px].x)`, `out = (c.rgb * t / (c.a + 1e-5), t >= 0.9999 ? 1 :
  t)`; blend One / InvSrcAlpha colour, SrcAlpha / InvSrcAlpha alpha; no depth test (scene becomes `rgb' + scene *
  e^-b0`). Combos: D_UPSCALE_MIXED (s0_d1: low-res, joint-upsampled as mboit_mixed_combine), D_COMBINE_HI_RES (s0_d2:
  alpha sum = low + hi), D_DENOISE_SMOKE, D_COVER_GAPS 0..2 (d6: alpha 1), D_SMOKE_PERF_TEST; StencilRef 128.

### Targets (1811f3780)

Twelve names (MBOIT_B0 / B / B_EXTRA / OUTPUT, MBOIT_MR_*, MBOIT_BLOOM_*), render system vfn 0x2b8, flags 0x409,
formats from 181d2a510 (6 moments: 0x11, 0x22, 0x13, 0x0f) or 181d2a520 (4 moments: 0x11, 0x13, 0x0f; three targets).
rendersystemvulkan's table at file offset 0x5619a0 (dword per format + 1, VkFormat): 0x11 -> 100 R32_SFLOAT, 0x22 -> 103
R32G32_SFLOAT, 0x13 -> 109 R32G32B32A32_SFLOAT, 0x0f -> 97 R16G16B16A16_SFLOAT: B0 R32F, B RG32F, B_EXTRA RGBA32F, OUTPUT
RGBA16F. Sizes (param_1[6]): the full set at the view's size unless r_csgo_mboit_force_mixed_resolution (and the view
isn't a +0x31 one, and annotation_auto_load is 0); the MR set at size / r_csgo_mixed_resolution_particles_scale when
r_csgo_mixed_resolution_particles; the BLOOM set at size / 4 always.

### Views and layer order

- The view's MBOIT flag (+0x1bb, 181207024) = `r_csgo_mboit && ((attr(0xaf8c0cb3) && !attr(0xbad93cb2)) ||
  attr(0x3b418add))` (attribute set +0x110 via 180161a30, CUtlStringToken hashes; names not in client / scenesystem /
  engine2 strings). Not tied to a smoke on screen.
- 1811d9d30 with the flag loops the translucent layers twice (`count = flag + 1`): "Static - MBOIT Pass %d" (1811efcc0)
  then "Dynamic - MBOIT Pass %d" (1811e49d0, particles among them; pass index +0x138; targets the full set `param_2 +
  0xd8`, the MR set `+ 0xf8` when forced mixed). Then: SmokeLPVSetup, "MBOIT(%d) Smoke 1/4" / "1/2" / "Full" (one by the
  smoke's resolution), "MBOIT(%d) Translucent 1/2", "Water Translucent Combine", WriteSmokeDepth, "Mixed Resolution
  Particles", "Dynamic", SmokeOverlayDataA / B, then "GameOverlay Particles". Up / down layers: 1811e1710, 1811e3220 /
  1811e0360.

### DepthNoCharacters and HalfResDepth

- 1811ec0c0 (from 181201670, "Depth Prepass Large / Small / AlphaTested"): when the cvars at 1825f6948 and 1825f6958 are
  on and an HE hole is live (18223f24c, `0 <= now - t < 5`) or the C4's explosion (180cb36f0): "Temp_NoCharactersDepth",
  "ResolveDepthNoCharacters" (MSAA), "CopyDepthNoCharacters": the prepass depth copied before the characters are drawn
  into it.
- 1811e58b0: "HalfResDepth" (0x2a: VkFormat 129 D32_SFLOAT_S8_UINT) at size / r_csgo_mixed_resolution_particles_scale
  and, with the cvar at 1825f66b8, "HalfLinearDepth" (0x27: 76 R16_SFLOAT), filled by a "DownsampleDepth" layer binding
  the scene depth (0x6656de6f) with materials/dev/downsample_depth.vmat (combos D_MINMAX_CHECKER_2X2 (s0_d1: min on odd
  checker pixels, max on even, of the 2 x 2), D_RESOLVE, D_MAX, D_MIN, D_NON_MSAA_DEPTH, D_MSAA_SAMPLES 0..4,
  D_WRITE_COLOR; s0_d0: the texel at pixel x ratio).
- depthtolineardepth's PS: `1 / ((sat((d - m1) / (m2 - m1)) * m0.z + m0.w) * dot(m3, normalize(ray)))` from one texel
  (no min / max): the radial distance.

## Unread

- Server: the rehash's real capacity (tier0's allocator); slot 32's order among the game systems (InitAllSystems
  180545fc0 registers by name; dispatch order unread); the bot list's adder (entry position, taken as the smoke's
  origin) and 0x1821ba1c0; out-of-grid neighbours in the start's step (taken as clear).
- No comparison with a real CS2 smoke (needs a client capture / tv demo and a parser for m_VoxelFrameData).
- Client: 1817590b0's exact segment rules; who queues the tracer records (per bullet assumed); 18256af78 / 18256af88's
  names; the point list's source (the server's 40 fill records?); the HE projectile's lifetime on the client (C_BaseEntity
  release); the 18257e040 slots' use; c64.w's use; the client's write of c11.
- The scene system's probe query test and order (180d323b0); the Priority copy; the shadow cascade terms; the LPV's
  setup (SmokeLPVSetup in 1811d9d30).
- Which upsample combo (D_MODE 0..2, D_FORCE_MR) each setting picks; which downsample_depth combo the layer takes
  (1811cd9a0) and how the half-res copy is fed.
- The overlay accumulation target's identity (layer builder [rbp + 0x2e0]); the viewmodel pass; the eye density's reader
  (m_flLastSmokeOverlayAlpha).
- smoke_param1..5's defaults (the client's business).
