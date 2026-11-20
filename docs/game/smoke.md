# CS2's smoke volume (server_20261105.dll, client_20261015.dll), traced 2026-11-16

The smoke grenade's cloud: a voxel volume the server builds by a flood fill over the world from where the grenade
stopped, sends to the clients (m_VoxelFrameData), and answers line-of-sight questions with (bots, spotting). The
clients draw it and carve it with bullets and HE grenades (client-only state). The throw / flight / detonation timing
is docs/game/grenades.md "Smoke".

## Classes and names (RTTI / strings)

- `SmokeVolume` (shared code, both DLLs): `BuildSmokeSimulation(CSmokeGrenadeProjectile*, ...)` (a CCoJobLambda,
  job name `buildSmokeVolume`), `RebuildVoxels(AABB_t const&)`, `GetSmokeDensityInLine(VectorWS, VectorWS, ...)`,
  `GetSmokeDensityLOS(...)` (private); `VoxelOctree::Voxelize(VoxelID const&)`.
- `CSmokeVolumeSystem` (a game system on both sides, string `SmokeVolumeSystem`, server 1800ac890).
- `CSmokeGrenadeProjectile` networked fields: m_nSmokeEffectTickBegin, m_bDidSmokeEffect, m_nRandomSeed,
  m_vSmokeColor, m_vSmokeDetonationPos, **m_VoxelFrameData** (CNetworkUtlVector<uint8>), m_nVoxelFrameDataSize,
  **m_nVoxelUpdate**, m_nSmokeLightProbeRegen (field registration 1809c5440 / 1809b6310). Client: m_bSmokeVolumeDataReceived.
- Thinks (1809baf90 names them): CSmokeGrenadeProjectileThink_Detonate, _Update, _Remove, _BuildingSmokeVolume.
- Client only: `CFixedSizeCircularBuffer<SmokeVolumeBulletTrail_t, 16>`, `CFixedSizeCircularBuffer<
  SmokeVolumeHEGrenadeTrail_t, 5>` (the bullets' and HE grenades' holes: client.dll, the server has neither),
  CSmokeVolumeSceneObject(Desc) (`cs_smoke_volume_visual.cpp`), materials/dev/smoke_volume{,_mask,_depth,_lpv}.vmat,
  render targets SmokeVolumeMaskTex_N / OppacityTex_N / OptimTex_Color_N / _Depth_N / _DepthCombined_N (N 0..4: up to 5
  smokes drawn this way?), SmokeGrenade.Clear (a sound).
- Cvars: server bot_max_visible_smoke_length, inferno_smoke_volume_density, smoke_param1..5, smoke_use_noise_texture,
  sv_smoke_lighting_changed, cl_smoke_origin_height, cl_smoke_torus_ring_radius / _subradius, cl_smoke_edge_feather,
  cl_smoke_lower_speed, smoke_grenade_ct_color / _t_color, sv_kill_smokegrenade, sv_explode_smokegrenade_at_crosshair,
  sv_throw_smokegrenade; client cl_smoke_volumeprop, cl_smoke_volume_growth, sv_smoke_volume_blind_start,
  cl_use_prompt_smoke_density, smoke_volume_lod_ratio_change. Bots: CBotManager::IsLineBlockedBySmoke 18032a570,
  IsVisibleThroughSmoke 18032a6b0. A molotov goes out when more than 1/3 of its fire areas are in smoke (180349500).

## The build (server)

- **`1809b4190`** (called from Detonate 1809b8bb0 on the projectile's +0xbc0, the volume): the owner's handle at
  +0x6c; the grid **`1809b45b0`(vol + 0x10, pos, 640.0, 20.0)**; the origin vol+0xd4..0xdc = pos; vol[0] = 1; a work
  block of 0x10b010 bytes at vol+0x70 (at +0x8: a 0x1000-byte bitset = one bit per voxel; +0x1008: 0x2000 bytes;
  +0x3008: 0x10000 x 16-byte entries; +0x103008: 0x8000 bytes, one per voxel; +0x10b008: a flag), the grid's bitset
  copied into it; vol+0xc = the time argument; the job (vtable 0x1818e9cb0, its run slot 8 = 1809b3e00 ->
  **1809b2390**(job + 0x120): {volume, the trail (0xd0 bytes copied from the projectile's +0x2d70: read 2026-11-16,
  "The trail and the job" below), the owner's handle}).
- **Grid `1809b45b0`(grid, centre, size, voxel)**: n = ((int)ceilf(size / 2 / voxel) + 3 >> 2) * 8 = **32** (640, 20);
  log2(n) at +0x30; words = n^3 >> 6 = **512** (a 64-bit word per 4x4x4 brick); bounds +-n x voxel / 2 = **+-320**; a
  512-qword bitset and a 512-byte array, both zeroed.
- **Voxel coordinates `1809d7150`**: `c = (p - origin) * 0.05 + 16` per axis (16 = n / 2, a static), then 1809b0470
  rounds to three bytes (x, y, z in the low three bytes of a uint). The index is the **Morton code** of (x, y, z):
  each byte spread with `(v << 8 ^ v) & 0x300f00f`, `(v << 4 ^ v) & 0x30c30c3`, `(v * 4 ^ v) & 0x9249249`, then
  `x + (y + z * 2) * 2`; out of the grid when > 0x8000. Its brick = index >> 6 (< 0x200), bit = index & 63.
- **`1809b2390`** (the job): the trail (16 positions, a ring at vol+0x10 + 12 x i, starting at vol+0xd0) walked newest
  to oldest; for each, **1809bd920** (a start at that point), else 1809bd150 for the first; when a start was found
  (vol+0x140 != -1): two 0x1000-byte tables at vol+0x180 / +0x1180 set to 0xff, **1809bb050** (the fill), then
  1809d0110 and 1809bc190; the count at vol+0x2180 **> 39** (0x27) -> 1809b2ec0, done; else the best count so far kept
  (vol+0x219c / +0x2198) and the next trail point tried. No start: `SmokeVolume: Failed to find detonation`. At the
  end vol+0xf0 = 60.0 (0x42700000).
- **A start `1809bd920`**(vol, point, owner, out): the point's voxel; out of the grid -> none. Its brick loaded
  (1809d6b00); if the voxel's bit is set (solid / taken), 1809d58d0 from it; with no start found yet, a trace (mask
  0x3001, group 5) from the point to 20 u above, and from where it stops the same again. If the voxel's bit is clear
  and it isn't in the visited set (out+0x18, hash 1809aedc0), it is pushed (1809b39c0) and the set takes it
  (murmur3 fmix32 of the packed xyz: `(h >> 16 ^ h) * 0x85ebca6b`, `(h >> 13 ^ h) * 0xc2b2ae35`, `h >> 16 ^ h`).
- **A step `1809d58d0`**(vol, from, voxel, owner, queue, list): the six neighbours (offsets from a table of 3-byte
  steps), each: skipped when already in the queue's set; its centre 1809d6960; a trace (TraceShape 180c2f3c0, mask
  0x3001, collision group 5, the owner and the owner's owner ignored) from `from` to the centre; **fraction >= 1.0 and
  not start-solid**: its brick loaded, if its bit is set and a list is given it goes in the list, if clear it goes in
  the queue and the set.
- **Brick load `1809d6b00`**: if the grid has its data (1809d6c40), the brick's word copied from the grid's bitset into
  the work bitset, the brick marked in a set at vol+0x98 (+0x90 |= 2).
- **`1809bb050`**(vol, queue, owner) (first read, 2026-11-16): time-sliced, `Plat_TicksAfterMicroSecs(2000)` then a
  yield (1816a4690) and the owner re-checked (gone: stop); pops the queue (a ring of uint voxels, param_2[4] head /
  [5] tail); its **26 neighbours** (a 26-entry table of int32 (dx, dy, dz), 12 bytes each): inside the grid (Morton <
  0x8000), not in the set (param_2 + 6), brick loaded; clear bit -> pushed and set. A voxel whose cost byte
  (work + 0x103008) is 0 and that took no new neighbour: its 26 bricks loaded; the direction from the origin to its
  centre (centre = (v - 16) x 20 + origin + 10), normalised (1e-17 .. 1e17 guard); `d = dir.z` (dir . (0, 0, 1));
  `d <= 0.8 -> 0`; the voxel at centre + (0, 0, d x 29) (when other than itself and clear, it replaces it); per (x, y)
  column (param_2[0x14 + x * 32 + y] the lowest z, [0x414 + ...] the highest, 0x20 = unset) the z span; an 8-byte record
  {voxel, 0} appended (param_2 + 0x816, count [0x814]); its cost byte + 1; **at 40 records it returns**.
- The 40 records are the volume's **emitters** (read 2026-11-16, below "The server's update"); the rest of the build,
  the grid's solid bits and the frames are in the sections after "The wire (ZE)".

## The wire (ZE)

CS2 networks the volume as **a log of update records** in CSmokeGrenadeProjectile's m_VoxelFrameData
(CNetworkUtlVector<uint8>, +0xb90; its size m_nVoxelFrameDataSize +0xba8, the record count m_nVoxelUpdate +0xbac):
every update (1809d6590, at most every 0.1 s, below) appends one record and never trims, so a late joiner replays
the whole log. The record carries only what the client cannot recompute: the emitters, the world's solid voxels
(bricks as the server voxelizes them) and the dissipation flag. **The client runs the same simulation step itself**,
one record at a time (client_20261015 1807e0d70 -> 1807c70f0: find the record whose seq is the next expected, apply
it 1807c8990, step 1807c5ed0, rebuild the texture 1807dff70, seq + 1; a record ahead of the expected one stops the
walk). This port sends the same records, byte for byte:

- **Pop event** (`smokegrenade_detonate`, grenades.js): `{ k: 'smoke', id, at, t, o: [x, y, z] }`, `o` the volume's
  origin exactly (m_vSmokeDetonationPos, float32 values as JSON numbers; `at` is rounded, don't use it for voxels).
- **Snapshot JSON tail `sv`**: `[[id, from, b64], ...]`: for each live smoke whose log has records this client hasn't
  been sent, `from` = the first one's seq and `b64` = those records concatenated, base64. Each client gets each record
  once (server/cs2web/grenades/smoke-net.js keeps what each connection has; a skipped, backpressured frame loses nothing); a client
  joining late gets the whole log of every live smoke in its first frame. An entry with `from` 0 carries a 4th
  element, the origin `[x, y, z]` (the same as the pop event's `o`), so a late joiner that missed the pop can start
  the volume. A smoke's log goes when the smoke does (`smokeend`). Cost: ~2.5 KB a smoke over its 22 s (de_dust2: a
  first record of ~0.7 KB with the bricks, then ~5-10 B a record), ~110 B/s a client a smoke.
- **`infout` event** `{ k: 'infout', inf, at }`: a molotov / incendiary put out by smoke (Molotov.Extinguish and
  inferno_extinguish, 180349500); the flames themselves go out through the usual `flameout`.
- **One record** (CS2's 1809b9ba0 writes it, 1807c8990 reads it), little-endian:

  | Bytes | Field |
  |---|---|
  | u16 | seq: 0, 1, 2, ... (the volume's +0xd0, + 1 a record) |
  | u16 | len: the bytes after this field |
  | u8 | dissipating (work +0x10b008: the effect's age past 19 s, 1809d47d0) |
  | u8 | flags: 1 the emitters follow, 2 bricks follow (the first record has 3) |
  | flags & 1: u8 n, then n x 8 bytes | the emitters: u32 packed voxel (x \| y << 8 \| z << 16 \| 5 << 24: 5 = log2 32) and f32 weight. Replaces the client's list |
  | flags & 2: u16 count, then count x 10 bytes | solid bricks: u16 brick (Morton index >> 6, 0..511), u64 its 64 solid bits (bit i = the voxel Morton brick x 64 + i). count 0 means all 512 follow |
  | u8 m, then m x 20 bytes | "holes": u32 countdown, f32 x, y, z, f32 radius per count (the server never adds one in this build: m is 0; TODO) |

- **The grid**: 32 x 32 x 32 voxels of 20 u, centred on `o`: voxel (x, y, z) spans `o + (v - 16) x 20 .. + 20` on
  each axis, its centre `o + (v - 16) x 20 + 10` (float32, that order: 1809d6960). A position's voxel: `(int)((p - o)
  x 0.05 + 16)` per axis, truncated (cvttss2si), low byte (1809d7150 / 1809b0470). The Morton index of (x, y, z):
  each 5-bit coordinate's bits spread three apart, x at bit 0, y bit 1, z bit 2 (smoke-volume.js morton()).
- **A voxel's value** is a float32 density (0 .. ~50+; the client draws clamp(d / 50, 0, 1)) that only the
  simulation produces: the wire never carries densities. `web/src/cs2web/sim/smoke-volume.js` is the decoder: it replays the
  records into CS2's client state and gives **CS2's 32^3 RGBA8 texture exactly as 1807dff70 fills it** (x fastest:
  texel ((z x 32 + y) x 32 + x) x 4): G = the voxel's byte `(uint)(clamp(d / 50, 0, 1) x 255)` this record, R = G
  before it, A = G (0 for a solid voxel next to the smoke, whose G is a neighbour's byte, so the filter sees the wall),
  B = A before. Texels of voxels never reached stay 0; a voxel once reached stays in the set (its byte decays to 0).
  The decoder also keeps the voxels' bounds (1807dff70: the smoky voxels' box grown 2 voxels, clamped to the grid, in
  world units) and the dissipation flag.

  ```js
  import { SmokeVolume } from '../smoke-volume.js';
  const v = new SmokeVolume(ev.o);   // on the pop event
  v.push(id, from, b64);             // each `sv` entry for this smoke (records in seq order; a gap throws)
  while (v.applyNext()) {}           // or one a frame, as CS2 (1807e0d70 applies one record a call)
  v.tex        // Uint8Array(32 * 32 * 32 * 4), CS2's texture bytes
  v.seq        // records applied
  v.bounds     // { min: [x, y, z], max: [x, y, z] } world units, or null before any smoke
  v.density(x, y, z)   // the float32 density of a voxel (the simulation's), v.byte(x, y, z) its G byte
  ```

- **Timing**: CS2's server updates a smoke when curtime - its last update (+0xbb8) >= 0.1 (1809d6590): every 7th tick
  at 64 tick (0.109375 s), the first on the pop tick (1809d2780 sets +0xbb8 = 0); several smokes share one update a
  frame (180988170: a round-robin over the smokes, the first due one updates and the walk stops). Updates run until
  the entity goes (22.05 s). The client is free to interpolate R -> G over the 0.1 s (the shader's business).

## The volume's layout (server +0xbc0 in the projectile; client +0x13b8, the same struct 0x10..0x14 bytes longer)

Server offsets (constructor 1809b0250): +0 built flag, +4 a time, **+8 first-pass flag (1)**, +0xc the effect's
start time (interval x m_nSmokeEffectTickBegin), +0x10 the grid (below), +0x6c the owner's handle, **+0x70 the work
block** (0x10b010 bytes: +0 a CRC (1809b6af0, debug), +8 solid bits (512 u64), +0x1008 active bits (2 x 512 u64),
+0x3008 entries (2 x 0x8000 x {f32 density, f32 dir x, y, z}), +0x103008 emitter counts (u8 a voxel), +0x10b008
dissipating), **+0x78/+0x80 the emitters** (CUtlVector of {u32 packed voxel, f32 weight}), **+0x90 flags (3)**, +0x98
the dirty-brick hash set (u16 keys, count +0xa8), +0xb8/+0xc0 this pass's emitter list (the record's), +0xd0 u16
seq, +0xd4 the origin, +0xec the current buffer, **+0xf0 an emitter's density (60)**, +0x118/+0x120 the holes (20 B
each), +0x130.. the build's search (queue ring +0x130, head +0x140 / tail +0x144, seen set +0x148, the columns' lowest /
highest z +0x180 / +0x1180 (u32 x 1024, 0xff-filled per search), the records +0x2180, the best search +0x2198 /
+0x219c, the trail's slots +0x170). The projectile: +0xb68 m_nSmokeEffectTickBegin, +0xb6c m_bDidSmokeEffect, +0xb80
m_vSmokeDetonationPos, +0xb90 m_VoxelFrameData, +0xba8 m_nVoxelFrameDataSize, +0xbac m_nVoxelUpdate, +0xbb8 the last
update's time, +0x2d70 the trail (16 x 12 B at +0x2d78, start +0x2e38, count +0x2e3c), +0x2e40 "went off in a fire"
(1809b5220 sets it after a forced Detonate), +0x2e41 the Scorch decal done. The client's struct: +0x100 buffer, +0x104
the emitter density, +0xe8 the origin, +0x128/+0x130 the holes, +0xd8 the scene object, +0xe0 the texture's bytes.

## The trail and the job (server, all read 2026-11-16)

- **Trail** (1809d4650 each think before the detonate test): the origin pushed when the trail is empty or the newest
  is more than 20 u away (dist^2 > 400); a ring of 16 (1809cd180: full, the oldest slot overwritten, start + 1).
- **Detonate 1809b8bb0** -> **1809b4190**(vol, owner, pos, trail, time): the owner's handle, the grid (1809b45b0(vol +
  0x10, pos, 640, 20)), the origin, a fresh work block (its solid bits from the grid's: all zero then), the job (vtable
  0x1818e9cb0, run slot 1809b3e00 -> 1809b2390 on job + 0x120 = { volume, the trail's 0xd0 bytes, the owner's
  handle }). **At the pop 1809d2780 calls 1809b4090**(vol, m_vSmokeDetonationPos, interval x tick): vol[0] = 1, the
  origin, the work block freed and **a new zeroed one** with the grid's solid bits copied in, +0xc = the time. The
  emitters (+0x78), flags and dirty bricks carry over; densities, active sets and emitter counts start at zero.
- **The job 1809b2390**: the trail newest to oldest (index (start + i) & 15, i from count - 1 down): each a fresh search
  (queue and seen set cleared, records 0; **the emitter counts are not reset between searches**); 1809bd920 at the
  point, and for the oldest (i == 0) with nothing queued 1809bd150; something queued: the column tables 0xff, the fill
  1809bb050, then (the owner still there) 1809d0110 and 1809bc190; **records > 39**: 1809b2ec0, done; else the most
  records so far kept (swapped into the trail slot). After: fewer than 40 -> the best search's records, none: DevMsg
  `SmokeVolume: Failed to find detonation`. The records become the emitters (swap into +0x78); work +0x10b008 = 0;
  +0xf0 = 60.
- **1809bd920** (a start): as above (first read), exactly: the voxel of the point (> 0x8000: none); its brick
  loaded; **solid**: 1809d58d0 from the point (solid neighbours to a local list); queued something: done; else a line
  (UTIL_TraceLine 180250e50, 0x3001, group 5, the grenade ignored) up 20 u: clear -> the voxel there (> 0x8000: done),
  its brick, solid -> 1809d58d0 from there; then the current voxel queued (and seen) when clear and unseen; nothing
  queued: each solid neighbour in the list gets 1809d58d0 from the grenade's origin (no list). Set hashes: murmur3
  fmix32 of the packed voxel.
- **1809d58d0** (a step): the six neighbours (0x1818e4200 table: -x, +x, -y, +y, -z, +z), unseen ones; a TraceShape
  line from `from` to the neighbour's centre (filter 0x18178c240: interacts-with 0x3001, group 5, flags 0x49, object
  set 0xf, the grenade and its owner ignored, no iteration); **fraction >= 1 and not start solid**: the brick loaded,
  solid and a list -> the list; clear -> queued and seen. A neighbour outside the grid (a coordinate 32 or a wrapped
  -1) reads its "solid" bit past the bitset (work +0x1008.. during the build: zero) and is queued: ported as clear.
- **1809bd150** (the fallback): eight points at 40 u (0x181e0fb78) around the grenade: x = V_sinf(i x 0.7853982) x 40 +
  x0, y = y0 + V_cosf(..) x 40, z = z0 + 40 x 0; a clear line from the grenade to each: its voxel queued (seen) when
  unseen, Morton < 0x8001, its brick loaded and clear; else the voxel above (z + 1) the same way. V_cosf / V_sinf
  (tier0_20261103 0x180007f50 -> 0x1802e0d70, 0x180008280 -> 0x1802e6570): the CRT's, ported as src/lib/crt-math.js.
- **1809bb050** (the fill), exactly: pop the queue's head (FIFO); for the 26 neighbours (0x1818e4250: the 8 around in
  z, the 9 above, the 9 below, table order in smoke-grid.js) inside the grid: add its emitter count to a sum; unseen:
  its brick loaded, queued if clear, seen either way. Then if the popped voxel's count and the sum are both 0: the 26
  neighbours' bricks loaded; dir = normalize(centre - origin) (each part ((v - 16) x 20 + o) + 10 - o; length
  sqrt((y y + z z) + x x); zero -> (0, 0, 1)); d = x x 0 + (y x 0 + z) (the disassembly's order); **d <= 0.8 -> 0**;
  the point centre + (d x 29 x 0, d x 29 x 0, d x 29): its voxel v2; v2 != v: its brick, and if clear the count goes
  on v2 instead of v; the column (x x 32 + y of v) keeps v2's z as its lowest / highest (a highest above 0x20 is
  unset); **a record {v2, 0.0}** (v2 even when solid); the count + 1; 40 records end it. Time-sliced: every 2 ms
  (Plat_TicksAfterMicroSecs(2000)) a yield (1816a4690), the owner re-checked (gone: the job stops).
- **1809d0110** (flat tops): for y, for x: the column's highest z (low byte) < 0x20 and equal to the column before's
  (two unset columns in a row break the run): z' = z + k - 1 (k = 1, 2, 0 cycling: a counter mod 3, advanced at every
  flat top), its brick; solid: skip; its count 0: the top's count 0, z''s 1, the column's highest (and lowest, if it
  was the highest) = z'. It then looks the record on the top voxel up and copies its centre to the stack only (the
  disassembly at 1809d05a8: nothing stored): **the records don't move**; only counts and the column tables change.
- **1809bc190** (underhangs): records within 40 u across (sqrt(dy dy + dx dx) < 40) and 0..80 u above the origin
  taken out (count 0, swap-removed); the rest sorted by z (V_qsort, comparator 1809a35f0: a.z - b.z; tier0's V_qsort
  is the UCRT qsort: src/lib/msvc-qsort.js); then for y, for x: a column with a lowest z: up to 9 voxels below it
  walked (each brick loaded) while clear; **4..8 clear** below: from 3 under the lowest down, every 2nd voxel takes the
  last record's place (that record's count 0) as a new record (packed with level byte 0); 43 placed ends it; the taken
  out and the new ones appended, their counts + 1.
- **1809b2ec0** (crowning a 40-record fill): the record within 60 u across (dy dy + dx dx < 3600) with the largest
  |oz - cz| (fabsf 1808ad470); 1809b1850 (2 voxels from it in the grid and clear) up -> {z + 1} appended, then +x, -x,
  then +y, else -y (no counts).

## The grid's solid voxels (VoxelOctree, read 2026-11-16)

- **1809b45b0** grid(+0 words 512, +8 bitset, +0x18 count 512 / +0x20 a built byte a brick, +0x30 log2 n = 5, +0x38
  mins (-320), +0x44 maxs (320), +0x50 the centre (the detonation point), +0x5c the owner's handle).
- **1809d6c40** (a brick built on first use): the voxel's brick (Morton >> 6 < 512) not built: its coordinates
  (every third bit of the brick index), **1809d3810**(grid, brick, log2 n - 2 = 3, test 0x1818e9d40, no bounds), built
  = 1, true. Every caller that gets true marks the brick dirty (+0x98, +0x90 |= 2) and copies its u64 into the work
  block (1809d6b00 and its inlined copies: the fill, 1809d0110, 1809bc190, 1809b1850, the step 1809d1a90).
- **1809d3810**: for the node's 8 children (bit 0 x, 1 y, 2 z) at level + 1: the child box in the grid's frame (size
  = (640 / 2^level) x 0.5: 40 at level 3, 20 at 4; x: -320 + c x size .. (size + c x size) + -320); the test (slot
  +0x10, 1809d7530: the box + the grid's centre, then **1809c7bd0**); a leaf (level 5) that touches sets its bit; an
  inner one that touches recurses.
- **1809c7bd0** (the box test): a TraceShape of the box (half extents (max - min) x 0.5) from its centre to its
  centre: filter 0x18178c240, interacts-with 0x3001, group 4, flags 0x49, no iteration, the grenade and its owner
  ignored; no hit (bit 0 of the result's +0x68, or start solid): clear. A hit on a box wider than 20: solid (recurse).
  A leaf: a world hit (entity index 0x8000) or none: solid unless the hit's collision attribute (table 0x18218e4f8
  +0x28, 0x20-byte entries, index at the result's +0x10) has +0x1b set, which tests eight 10 u sub-boxes (no ignore)
  and is solid if any touches something without the flag; an entity of class 0x181ec16c8 with +0xcc8 != 0 or of
  0x181ec1b50 with +0xf34 >= 2: not solid. Ported as read (smoke-voxels.js; the flag and
  the classes named in "The voxel box test's leaf branch").

## The simulation (1809b3630 server / 1807c5ed0 client; src/cs2web/sim/smoke-sim.js)

Server update **1809d6590** (m_bDidSmokeEffect and 0.1 <= curtime - +0xbb8): +0xbb8 = curtime; a 0xc00-byte buffer
with the old frame data, **1809b3630**(vol, buffer); m_nVoxelFrameDataSize = its size, m_nVoxelUpdate + 1,
m_VoxelFrameData grown to the size rounded up to 0x200 and the changed bytes written (each marked changed). Its
caller **180988170** walks a queue of the smokes (list 0x181faa578, next +0xb60), refilled when empty at a frame's
start, popping until one updates (a game system's frame slot via the thunk 18097ee00). 1809b3630:
1. **The emitter pass 1809d09e0**: +0xf0 = 60. First pass (+8): each emitter's 26 neighbours in the grid, inactive and
   clear: density += 60 x 0.5 (both buffers), active; the emitter's own voxel active; the emitter appended to +0xc0.
   Else: cap = max((1 - weak / 40) x 3.5, 1) (weak: weights not >= 0.01); each emitter in the grid: appended to +0xc0
   (before it changes); not dissipating: dist = |centre - origin| ((dz dz + dy dy) + dx dx); **dist <= 80: w x= 0.8**;
   else 1809b1650 (the six neighbours' mean of clamp(d / 50, 0, 1) over active ones > 0.2): w <= 0 (or NaN) -> 1 unless
   crowded; w > 0 -> x 0.8 if crowded else 1; density = min(cap x 50, (1 - w) x 60 + density) (minss); dissipating:
   density 0, count 0; active; the entry copied to the other buffer. (The holes loop before it moves or removes
   emitters; with no holes it does nothing.)
2. Server only: +0x90 & 1 and fewer than 5 emitters in +0xc0: no emitters (+0x78 = +0xb8 = 0). Both: dissipating:
   no emitters. +0xf0 = max(+0xf0, 0).
3. **Each active voxel** of the current buffer (512 u64 words in order, low bit first; each word read once):
   **1809d1a90** (client 1807dc8c0, the same constants): solid -> its other-buffer density 0. w = clamp(d_other / 50,
   0, 1). For the six neighbours (table order): the server loads its brick; in the grid and clear: nd = its current
   density; k = 0.9 / 1.25 for the four sideways ones by ((-dy x vy) - vz x dz) - vx x dx > 0.2 (the neighbour's
   direction; a NaN takes 0.9), 0.79 down, 1.2 up; **flow = (nd / 6) x ((1 - w) x k)** (the disassembly's order);
   the neighbour's other density = max(0, it - flow) (maxss); inflow += flow; the neighbour inactive and this voxel's
   current density > 5: the neighbour active in the other buffer. Else the face's normal (-d) kept. A voxel on the
   border (a coordinate 0 or 31): other density x 0.3, done. Else other density = inflow + it; g = (l[-x] - l[+x],
   l[-y] - l[+y], 0) (the neighbours' densities, 0 for blocked); for each blocked face g += -(g . n) n ((gz nz + gy
   ny) + nx gx); normalized (length sqrt((gy gy + gz gz) + gx gx), 1 / len times; out of 1e-17 .. 1e17: 1814738b0 in
   double; zero: zero) into the direction; density = max(0, it - 0.5 x (1, or 0.5 dissipating)). (With holes: the
   holes' mean push direction replaces g and the density becomes max(min(d, 15), d x 0) within 80 u of the origin,
   d x 0 beyond.)
4. Server: the CRC 1809b6af0 (debug), **the record 1809b9ba0** ("The wire (ZE)"), then flags 0, the dirty set
   cleared, +0xb8 = 0, seq + 1.
5. The current buffer's active voxels take the other buffer's entries; active[cur] |= active[other], copied back; the
   buffers swap; the holes' countdown - 1 (0: swap-removed); +8 = 0.

The client's record apply **1807c8990**: dissipating byte, flags byte; flags & 1: the old emitters' counts 0, n, n x
8 B (a demo older than 0x368c reads 16-byte float positions instead), the new counts 1; flags & 2: u16 n, n x (u16
brick, u64 bits) into the solid bits; u8 m holes (the list replaced). Its texture **1807dff70** ("The wire (ZE)"):
32^3 RGBA8 (FUN_1813d0610(0x20, 0x20, 0x20, 1, ..)), the byte 1807d90a0: (uint)(clamp(d / 50, 0, 1) x 255); the
bounds into the scene object's +0xe8..+0xfc; "RegenerateTextureBits" uploads it.

## Line of sight (server, read 2026-11-16; server/cs2web/grenades/smoke-los.js)

The walk itself (1809d5000 and its two visitors) is src/cs2web/sim/smoke-walk.js, shared with the client's own line
test (client 1807cd7f0 -> 1807de9d0 with the summing visitor 181bd3c70, the target ID's smoke gate: client/fx/
smoke-sight.js over the densities the client draws; docs/game/settings.md "The friendly warning").

- **1809d5000**(vol, a, b, visitor): the grid's box (origin +-320); a outside it: clipped (181489c20 -> 181476b30:
  the slab test, tolerance 0) and moved 1 u in along the line; then a 3D DDA over the voxels from a's voxel to b's
  (steps 20 / |dir|, the first from V_modff of (p - mins) x 0.05), at most 128, stopping when the voxel's centre
  leaves the box, the visitor says stop, or b's voxel is reached.
- **1809bfc60** (IsLineBlockedBySmoke 18032a570: >= 1.0): per smoke with m_bDidSmokeEffect, the visitor 1809d7440 ->
  1809b14f0: a solid voxel -> 1, stop; clamp(d / 50) >= 0.8 -> 1, stop; > 0.1 adds, the sum >= 0.2 -> 1, stop; the
  smoke's result x smoothstep(22, 17, t) x smoothstep(0.1, 1.5, t) (1809af7d0: (3 - 2x) x x x, t = curtime - +0xc)
  summed, >= 0.2 -> 1.0; else clamp(sum / 0.2, 0, 1).
- **1809bff80** (the damage feedback's < 1.4): the same walk, visitor 1809d7430 -> 1809b1150: a clear voxel adds
  clamp(d / 50); a solid one adds the max over its six active neighbours of a read of **its own** density (0): CS2's
  slip, ported; summed with the same weight, no early out.
- **1809bf8e0** (a point): the weight x 1809bf980: the point's voxel in the grid, its brick built, clear: clamp(d /
  50), else 0. 1809bfb20 sums it over the smokes.
- **IsVisibleThroughSmoke 18032a6b0** sums the bot manager's own smoke list (spheres: +8 position, +0x20 radius;
  1803260c0) against bot_max_visible_smoke_length (200): not ported (the bots here are stand-ins; they use
  IsLineBlockedBySmoke).
- **The inferno 180349500**: burning flames counted; for every smoke and every burning flame **180342d10**: +0x2e40
  (went off in a fire) and the flame within 16 u: out; 1809bfb10 (returns 1.0: the volume path always) -> the
  flame's point + (0, 0, 20), then + (0, 20, 20), (-0, -20, 20), (20, 0, 20), (-20, 0, 20) (20 x the offset + the
  point + 0), denser (1809bf8e0) than **inferno_smoke_volume_density (0.03, 18005c260, flags 0x4000)**: out
  (180347c00). Burning before > 2 and before / 3 < out: the rest out, `Molotov extinguished: when %d/%d fire areas were
  covered by smoke (exceeded 1/3rd).`, Molotov.Extinguish, inferno_extinguish (userid, x, y, z). (The old cylinder
  test after it, 22500 - ramps on dz, is dead.)

## Cvars (server_20261105)

inferno_smoke_volume_density 0.03; bot_max_visible_smoke_length 200 (flags 0x82000); smoke_param1..5 and
smoke_use_noise_texture are registered on the server too (0x4002 / 0x2000: replicated rendering knobs; the
cvardump's float loads near them read 6.26, 8.27, 0.13: which is each default is unsettled, the client's business).

## The voxel box test's leaf branch (read 2026-11-16, round 2)

- **The surface flag** 1809c7bd0 tests is **allowsmokethrough**: CGameSurfaceProperties (0x20 bytes, the table at
  0x18218e4f8 +0x28, a surface's index at its +0x10, 180c00e80) is filled by **180be8f60** from
  scripts/surfaceproperties_game.txt, one key a field: maxspeedfactor +0, jumpfactor +4, isstairs +0x19, isslippery
  +0x1a, **allowsmokethrough +0x1b** (the lea at 180be9030, its default read from +0x1b and stored back), reflectbullets
  +0x1c, bulletspenetrate +0x1e, reduceweaponimpact +0x1d, soundstackmaterial, legacymaterialtag, climbable,
  gamematerial +0x14, bulletPenetrationDistanceModifier +8, bulletPenetrationDamageModifier. The constructor
  (180c07590) zeroes +0x18..+0x1e: false unless set. Set true in the game txt for **chainlink** and **audioblocker**;
  with the vsurf's bases (tools/surfaces-game.mjs: a surface takes its base's entry, then its own keys) the physics
  surfaces that let smoke through are **chainlink, chain, metalrailing** (audioblocker isn't a physics surface in the
  vsurf). src/lib/surfaces-game.js carries `smokeThrough`; the trace's surface word (a hash) is named by the map's
  surfaces.json (game.stepEnv).
- **The two classes**: RTTI 0x181ec16c8 is **CBasePropDoor** (+0xcc8 = **m_eDoorState**, 0 closed) and 0x181ec1b50
  **CPropDoorRotatingBreakable** (+0xf34 = **m_currentDamageState**; +0xf30 m_bBreakable). A voxel touching a door
  that isn't closed, or one broken past damage state 1, is clear. This port's prop_door_rotating doesn't move or break
  (src/world/entities/caps.js gives it its caps only): always closed and whole, so the test is exact for this world;
  smoke-volume-server.js smokeEnv reads a `doorState` / `damageState` the day doors get them.
- The sub-box centres: (w x 0.5) x k + ((size x 0.25) + min) per axis, w the box's x size on all three axes
  (1809c80a9.. adds the 0.25 term to the minimum first), half extents size x 0.25; the sub traces ignore nobody.

## The brick order (round 2: src/lib/utl-hashtable16.js)

The dirty bricks are a **CUtlHashtable<u16>** at +0x98 (+0 allocated, +4 flags, +8 slots, +0x10 count, +0x14
capacity, +0x18 min size 0x20, +0x1c no-grow): a slot is {u16 word, u16 key}, the word's bit 15 empty, bit 14 "last
of its chain", bits 0..13 the hash's low 14 bits; a hash's home is (h14 x 0x4001) & (capacity - 1), probing on.
**Insert 1809ae490**(table, &key, fmix32(brick), 0): a lookup along the home's chain (a hit: nothing), growth when
count x 4 + 4 > capacity x 3 (unsigned, unless +0x1c) to (count x 4 + 4) / 3 (**1809b91a0**: at least the min size,
the next power of two, the old slots re-placed from the top slot down through 1809b8fc0), then the element at its
home: when the home's occupant is of the same chain the new one isn't last and the occupant moves on (**1809b46d0**:
along the chain to the first empty slot, taking the "last" mark), an occupant of another chain moves on too.
**1809b9ba0** walks slots 0..capacity-1 (occupied: word >= 0), and after the record empties them from the top slot
down, the capacity kept. The rehash's capacity is the largest power of two the allocation holds (g_pMemAlloc vfn
0x88, the block's size): taken as the size asked for (4 bytes a slot; tier0's allocator isn't read).

## The holes (round 2): none on the server

Nothing in server_20261105 adds a hole: the writers of +0x118 / +0x120 (fieldwrites.py) are the constructor
(1809b0318), the destructor (1809b0d20) and the step's countdown (1809b389c); no lea of a volume's +0x118 feeds an
append; the smoke list (0x181faa578) is walked only by 180349500, 18034cc30, 180988170, 1809b00c0 / 1809b0a10 /
1809b2a90 (the list itself), 1809bfb20 / 1809bfc60 / 1809bff80, 1809d7f20 / 1809d7f90 (the light probe count);
CSmokeVolumeSystem's own slots (vtable 0x1818d5428) beyond IGameSystem's defaults are 31 and 37 / 64 (empty), 32 (the
update) and 60 (a forward). So a record's hole count is always 0 and the emitter motion in 1809d09e0 (which only
runs inside a hole) is dead code on the server: exact as ported, not a stand-in. (The client's HE holes are its own
ring, "The client: bullet trails and HE holes".)

## The update's place in the frame (round 2)

**180988170 is CSmokeVolumeSystem's slot 32** (vtable 0x1818d5428 +0x100 -> the thunk 18097ee00): IGameSystem
**ServerPostEntityThink** (frame.md: after the think pass and the I/O queue). Its queue holds every smoke projectile
(the list 0x181faa578: 1809b00c0 appends each at construction, so creation order), refilled at a call's start when
empty; it pops until one updates (1809d6590 is 0 for a smoke that hasn't gone off: its turn is used), skipping dead
handles. Ported so (grenades.js smokeUpdate, after the projectiles' thinks). Not read: the game systems' order among
themselves in slot 32 (InitAllSystems 180545fc0 registers them by name in a symbol table; the dispatch list's
order is unread): the smoke update runs before spotting's here.

## A smoke over a fire (round 2: server/cs2web/grenades/smoke-fire.js)

**vfn 0xa00** runs at the end of every collision (ResolveFlyCollisionCustom, 1809cf572, after the bounce counter);
the smoke's is **1809cb9d0** -> **1809b5220** (then a timer at +0xbb4, 0.046875). Until +0x2e40: the entities in a
512 u sphere (180bf7da0, filter interacts-with 0xc3001, group 3) that are a **CInferno** (0x181ec18c0), each through
**180343040** -> **18034d880**(inferno, the grenade's origin, 10, check, grenade): for each burning fire (the
inferno's list +0x11a8, count +0x1190; burning: +0x24 and its timer), across within 10 + 60 of the fire's centre
(+0xc), up |z - (its z (+0x14) - 20)| - 20 <= 0 or (that)^2 + across^2 < 70^2, then **1803443c0**: a line from the
centre + (0, 0, 30) to the point, else from the centre, else (once) from 30 u above the point (interacts-with 0x1001,
group 3, the grenade ignored; filter vtable 0x1817bfb38); the nearest such fire's point (+0) wins. Then a TraceEntity
(180c2e9c0, interacts-with 0x200003001) from the origin to it, the grenade teleported to its end, stopped (movetype
none), the trail takes the point, **Detonate now** (vfn 0x9a8), +0x2e40 = 1. 180342d10's first test then puts out
any flame within 16 u of such a grenade (smokeOut). **CreateFire 180345dc0** (and 180352350) asks **18034cc30**: no
new fire where a smoke is (180342d10 against each smoke). Stand-ins (all from inferno.js, itself a stand-in): a
fire's centre and point are its one `at`, the sphere query is "a flame within 512 u", 0x1817bfb38 is taken as the
plain filter.

## The bots' smoke test (round 2)

CS2's bots see by **CCSBot::IsVisible (1802d3ba0, cs_bot_vision.cpp)**, which calls **IsVisibleThroughSmoke
18032a6b0**; IsLineBlockedBySmoke (18032a570) is used by spotting (1801d7460) and the behaviour tree's
**CBtDecoratorPickerBlockedBySmoke** (1803233b0, slot 10). IsVisibleThroughSmoke: the bot manager's grenade list
(TheBots 0x181fa5e10: +0x18 the head index, nodes 0x10 apart from +0x10, each entry {+0 the grenade, +8 its position,
+0x18 live, +0x20 radius}; 18032b550 clears it); **a smoke's radius is 166 from its pop (1809d2780 -> 18032b710(TheBots,
grenade, 166.0))**; per live entry **1803260c0**(r^2, &pos, from, to): the sphere at pos + (0, 0, 60); -1 when `from`
is within 0.95 R and `to` within R (then visible at once); else 2 sqrt(r^2 - d^2) for the segment's nearest point at
d^2 < r^2 (the sums as the disassembly: (y y + x x) + z z, the projection (z uz + y uy) + x ux); visible when the sum
is at most **bot_max_visible_smoke_length** (200, flags 0x82000). Ported as smoke-los.js visibleThroughSmoke
(grenades.js botSees, bots.js). Not read: the list's adder (where the entry's position comes from; taken as the
smoke's origin, which doesn't move after the pop) and the global at 0x1821ba1c0 the walk also needs.

## The job's timing (round 2: server/cs2web/grenades/smoke-jobs.js, smoke-job-worker.js)

CS2 runs the build on a job thread; the pop is the first think (1809d4330, every tick) that finds the job done. Here
one worker thread a game holds its own sim and a mirror of the physics world: created from the same physics.bin and
spawn groups, then fed every cast the game's own mirror applies, in order (src/cs2web/sim/trace-world.js onCast; the
round's bind makes the first a full cast), so its traces see the world the game thread's do. At Detonate the job goes
to it with a SharedArrayBuffer; the smoke's think reads the status word each tick (no wait) and takes the result
(emitters, the grid's solid bits and built bytes, the dirty hash set's slots, the flags) when set. The build costs the
game tick nothing; the pop is the first tick after the job ends, as CS2's. A ZE server starts the worker at its first
smoke throw (one full cast that tick), a team match at its first round; the game's stop() ends it. ZE_SMOKE_JOB=thread
keeps the job in the game thread (6 ms a tick).

## Comparing with CS2 (round 2: not possible this session)

Tried on a local LAN dedicated server (-insecure, sv_lan 1, port 27115, stopped after): sv_explode_smokegrenade_at_crosshair
and sv_throw_smokegrenade are FCVAR_DEVELOPMENTONLY | CHEAT (0x4002: "Unknown command" in retail); `ent_create
smokegrenade_projectile` needs a player's view (none on a dedicated server: nothing made), and an entity it makes
wouldn't get Create's think anyway; no console command prints a networked vector (ent_* lists: ent_text overlays,
ent_info, ent_dump-like commands absent); a demo (tv_record) needs a thrown smoke (a real client or a bot that
throws one) and a CS2 demo decoder for CSmokeGrenadeProjectile's m_VoxelFrameData. TODO: a client capture (the
owner's client on the LAN server, a tv demo, a demo parser for the field), then compare its records with ours.

## Still unread / stand-ins (server)

- The rehash's capacity (the allocator's block size, taken as asked for).
- Slot 32's order among the game systems (smoke update before spotting here).
- The fires a smoke lands on and that smoke puts out are inferno.js's stand-in flames (its CreateFire, think schedule
  and fire structure aren't ported); for the same reason the inferno's smoke check runs every tick here (CS2's
  180349500 runs on the inferno's own think, rescheduled from its fires' timers).
- The bot manager list's adder (the entry position) and the global 0x1821ba1c0.
- Out-of-grid neighbours in the start's step read memory past the bitset (taken as clear; past the block on -z).
- No comparison with a real CS2 smoke yet (above).

## The client: cvars (client_20261015.dll, traced 2026-11-16)

Registration stubs (the float default in xmm2, the handle in rcx; a value is read at `[handle + 8] + 0x58`):

| cvar | default | flags | stub / handle | read by |
| --- | --- | --- | --- | --- |
| cl_smoke_edge_feather | 21 | 0x2002 | 180097570 / 1824c7198 | (180c9ba00 reads + 8 of 1824c7198: the overlay) |
| cl_smoke_lower_speed | 1 | 0x2002 | 180097610 / 1824c71a8 | 180c686f0 (the in-smoke overlay's fall) |
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

The torus cvars are the in-smoke screen overlay's old path, not the volume: 180c9ba00 (the overlay's fallback when
1807cd400, a constant 1.0, is 0): the nearest live smoke whose horizontal distance from the eye to its origin + (0, 0,
cl_smoke_origin_height) is under ring_radius + subradius (149), age (tick - begin) x interval <= 16.75, sets the overlay
colour (+0x1538 = the projectile's + 0x136c, m_vSmokeColor) and age (+0x1534). The volume path is 180ca06e0 (the density
at the eye). 180c686f0 (the pawn's think) keeps the overlay alpha (+0x2a6 x 8) falling by cl_smoke_lower_speed.

## The client: bullet trails and HE holes

Two global rings (static objects, their vtables stored in .data):

- **Bullets** `CFixedSizeCircularBuffer<SmokeVolumeBulletTrail_t, 16>` at 18223efe0 (vtable 181ca6620), entries at
  18223efe8, 36 bytes each: start (12), end (12), time (+0x18, float), tracer byte (+0x1c), strength (+0x20, float);
  head 18223f228, count 18223f22c.
- **HE** `CFixedSizeCircularBuffer<SmokeVolumeHEGrenadeTrail_t, 5>` at 18223f230 (vtable 181ca6638), entries at
  18223f238, 32 bytes: the projectile (8), pos (12), time (+0x14), smoke mask (+0x18, uint); head 18223f2d8 (% 5),
  count 18223f2dc.
- **Add a bullet `180d2c780`**(start, end, tracer byte, strength float, mode, lefthand): the smoke scene objects (a
  linked list, nodes 16 bytes at 1825be9b8, head index 1825be9c0, next at +10) walked; the first whose box (object +
  0xe8) the segment hits (1817590b0(box, start, end - start)) takes it, the others never see it. mode 1 (your own shot,
  no viewmodel ... see 180901390): start = view origin (18256af48) - v1 x 7 (-7 left-handed) - v2 x 5 (v1 at
  18256af78, v2 at 18256af88: read as right and up); mode 2: start = origin - v2 x 8. time = curtime
  (180161780(18075d250(0))). Full (count 16): the head entry replaced, head = (head + 1) & 15; else appended at
  (head + count) & 15.
- Callers: **180901390** (cs_player_weaponservices.cpp, the tracer record queue flushed by 180901230, each record
  {weapon, shot index, attack index, start, end}): strength 1.0, **0.25 when the weapon's type (vfn 0xbe0) is 4
  (shotgun)**; tracer byte = the weapon's tracer frequency != 0 (+0x7b0[attack], or cvar 182535800 when >= 0); mode 0
  for others (start = the muzzle record), 1 / 2 for the local player. The trail goes in before the tracer frequency's
  `shot % frequency == 0` test: every bullet. **1807dbe30** (the decoy's fake shot): start = the decoy, end = a seeded
  random direction x 100 from it, tracer 1, strength 0.3 (0x3e99999a).
- **Add an HE `180d2cd00`**(projectile, &pos, time): mask = OR over the smokes of **180d1f260**(pos, object + 0xd0):
  18174a510 (the box + 0x18 / + 0x24 against a 256 u sphere), then each point of the object's list (+0x50 data, +0x48
  count, 12 bytes each) within 256 u (d^2 < 65536): a line (18022fee0, mask 0x2001, group 4) from the blast; the first
  unblocked -> `1 << object[+0x3c]` (the atlas slot, object + 0x10c). No bit: nothing kept. Full: the head replaced,
  head = (head + 1) % 5. Then the first of four zero slots at 18257e040 (12 bytes each) gets pos (unread use). Returns
  true -> the caller plays **SmokeGrenade.Clear**: **1810d03d0** (the HE projectile's network change: +0x12fc changed
  and +0x12d8 > 0: time = +0x12d8 (a tick) x 0.015625, pos = +0x12dc).
- **Remove an HE `180d1f020`**(projectile): its entry swapped with the newest, count - 1. Called from the HE
  projectile's destructor 1810c6420 (and 180cac130): the hole lives as long as the projectile entity on the client.
- The point list (+0x118 count / +0x120 data at object + 0xd8): filled by RegenerateTextureBits' first call from the
  volume's list at + 0x80 (count + 0x78, 8-byte entries, 1807e0ea0 turns each into a world point). TODO(trace): what that
  list is (the server's 40 fill records?).

## The client: the renderer (180d20800) and the constant buffer

`SmokeConstantBuffer_t`, 0x9c0 bytes (LockDynamicConstantBuffer), per smoke i < 16 ("Unable to render more than %d
smokes", 0x10) from its scene object o (CSmokeVolumeSceneObject; ctor 180d1c530 / 180d1f4d0, vtable 181ca82c8):

| reg | bytes | value |
| --- | --- | --- |
| c0[i] | +0x000 | o + 0xe8 box min, 1 |
| c16[i] | +0x100 | o + 0xf4 box max, 1 |
| c32[i] | +0x200 | o + 0x100: the grid's centre (the shader's uvw origin), 1 |
| c48[i] | +0x300 | x: now - o + 0xe0 (the smoke's age); y: clamp((now - o + 0xe4) / 0.1) (1807cd430 = 0.1: the frame blend); z: (float) o + 0x10c (the atlas slot); w: smoothstep(clamp((age - 6) / -11)) x 0.25 |
| c64[i] | +0x400 | o + 0xd0: the tint (the shader multiplies the light by it), w: (now - o + 0xdc) x 0.5 when o + 0xdc != 0 else 0 (unread use) |
| c80[i] | +0x500 | x: smoothstep((age - 22) / (17 - 22)) (1807cd420 = 22, 1807cd410 = 17: the fade); y: smoothstep((age - 0.1) / 1.4); z: smoothstep((age - 4) / 14); w: smoothstep((age - 0.1) / 1.9) |
| c96 / c97 | +0x600 / +0x610 | the union of the boxes (1801bcf20) |
| c98 | +0x620 | 180853e30's entity (the bomb?) when 1 < now - t < 10: its position, w (unread) |
| c99[k] | +0x630 | bullet k: start.xyz, age (0 <= now - time < 1); then .z += age x 10 |
| c115[k] | +0x730 | lerp(start, end, age x 10) (not clamped), tracer byte as 0 / 1; then .z += age x 10 |
| c131[k] | +0x830 | strength, 0, 0, 0 |
| c147[j] | +0x930 | HE j (0 <= now - time < 5): pos, time |
| c152 | +0x980 | HE masks as floats (5 used) |
| c154 | +0x9a0 | a flash: 18257e030..3c (pos, time), held up to 1 s (unread source) |
| c155 | +0x9b0 | x: the smokes drawn, y: bullets, z: now (180d25e00 = curtime), w: HE count |

## The client: the volume texture (RegenerateTextureBits 1807dff70)

- The atlas: **SmokeFluidA 542 x 32 x 32** (0x21e; 1807d3f80, the scene object's creation, format 0x1e), 34 texels a
  smoke (x = (34 slot + 32 u) / 542 in the shader), RGBA8; SmokeLPV%dx%dx%d the lighting atlas. Slots from a free list
  (1825be9c8 count 16, 1825be9cc.. 15, 14, ... 2).
- Each frame **1807c70f0** (from 1807e0d70) walks m_VoxelFrameData's records ({u16 frame, u16 length}, bit-packed)
  for the frame numbered volume + 0xd0 (u16); found: 1807c8990 decodes it into the work block (+0x70), 1807c5ed0, then
  RegenerateTextureBits, frame + 1. Older than expected: skipped; newer: return 2 (wait).
- **RegenerateTextureBits**: a 32 KB RGBA8 buffer (o + 0xe0, zeroed once). The voxels of the current set (the work
  block's bitset at +0x1008 + idx x 0x1000, idx at +0x100) in Morton order, each: d = clamp(v / 50, 0, 1) x 255
  (**1807d90a0**, v = the first float of the voxel's 16-byte entry at +0x3008 + ((1 - idx) x 0x8000 + voxel) x 16);
  texel (z x 32 + y) x 32 + x: **R = old G, G = d, B = old A, A = d**. Its six face neighbours (a 12-byte {dx, dy, dz}
  table), inside the grid (Morton < 0x8000) and **set in the +0x8 bitset (solid)**: into a hash set, the first voxel's d
  kept (murmur fmix32 of the packed xyz, as the server's). After the walk each such neighbour: **R = old G, G = its d,
  B = old A, A = 0**. Voxels not in the set are not touched.
- The box: min / max over the voxels with d != 0 and their solid neighbours, -2 / +2, clamped to 0..32 (1807c53c0),
  world = (v - 16) x 20 + the volume's origin (+0xe8); none: left inverted at +-FLT_MAX. Stored at o + 0xe8 / 0xf4.
  o + 0xe4 = now. Uploaded to the atlas at x = slot x 34 (0x22) (renderer vfn 0x270).

## The client: the raymarch (smoke_volume_cs)

shaders_vulkan_dir.vpk shaders/vfx/smoke_volume_cs_vulkan_50_cs.vcs, 291 dynamic combos (D_MBOIT_PASS1/2, OPTIM,
D_SMOKE_INSTANCES 1..6, 4_MOMENTS, QUALITY, USE_NOISE_TEXTURE, NEW_VISUALS, PERF_TEST), read as HLSL with VRF
20.1.7467's VfxShaderFile.GetDecompiledFile (SPIRV-Cross; a scratch tool over ValveResourceFormat, the combo read:
D_MBOIT_PASS2, D_SMOKE_INSTANCES=6, D_SMOKE_QUALITY, D_SMOKE_NEW_VISUALS). Material defaults:
materials/dev/smoke_volume_cs.vmat (g_flRayStepLength 6, g_flDensity 0.85, g_flSmokeNoiseStrength 0.8, NoiseSpeed 1.5,
NoiseScaleLow 3, NoiseScaleHigh 7, NoiseMin 0, NoiseMax 1.05, NoiseOffset -0.95, NoiseStrengthLow 0.5, High 0.35,
BoilStrength -0.3, Wispy 0, AmbientStrength 0.6, DirectStrength 0.35, InteriorDarkening 0.5, VolumeNormalBlend 0.5,
AOEffectDistance 16, Strength 0.06, g_vSmokeColor 1 1 1, noise materials/dev/noise/worley_perlin_z0000).

Per pixel (the mask texture's bit per smoke): the ray against the union box (c96 / c97), then per smoke box an
interval; start t = max(tIn, 4) + 6 x frac(bluenoise + time x 0.618034) x 0.8 x lerp(0.1, 0.8, sat((tIn + 150) x 0.05));
the end min(box exit, scene depth - 2); fixed steps of 6. At each step p:

- **Bullets** (recomputed for the first 16 steps, then every 16th): seg = head - start, v = p - start,
  dn = sat(|v - seg sat(v.seg / seg.seg)| x 0.05 x strength); fl = smoothstep(0, 0.01, age)(1 - smoothstep(0.01, 0.2,
  age)); if dn < 1: hole = max(hole, smoothstep(0, 1, 1 - sat(age + sat(dn + 1 - sat(|p - head| x 0.01))))), push =
  lerp(push, normalize(start - head), hole), line = pow(1 - dn, 64) fl x 10; tracer byte: glow = max(glow,
  max(((1 - sat(|v| x 0.01)) fl)^2, line)). Sample point q = p + normalize(push) hole^3 x 20.
- **Density**: uvw = clamp(((q - centre) x 0.05 + 16) / 32); t4 = atlas; (A, B) = lerp(t4.xz, t4.yw, c48.y);
  w = A > B ? lerp(B, A, smoothstep(10, 40, |q - ray end|)) : B; d0 = sat(lerp(w, -0.05, hole)); on when d0 > 0.01:
  d1 = sat((d0 - 0.01) x 1.0101) x fade; d2 = sat(d1 + (1 - sat(|eye - q| x 0.1)) d1).
- **HE** j with bit (1 << slot) in its mask and dt = now - time < age - 0.4, |q2 - pos| < 250: k = (1 - smoothstep(0,
  2, dt))^128; floor = sat((48 - g) / 48)(1 - smoothstep(0, 7, dt)) (g = max(0, |q - ray end| - min(20, |scene hit.z -
  centre.z| x 2)); 0 for a character pixel); q2 = lerp(q2, pos, (1 - smoothstep(100, 250, dd)) step(dt x 1250, dd)(1 -
  k)); keep = min(keep, max(smoothstep(200, 240, dd + 250 k) + smoothstep(0.5, 5, dt)^1.8, floor)); d = lerp(0.02 d2,
  d2, keep).
- c98 (when c98.w > 0 and < age): a sphere at 3000 u/s x c98.w from c98.xyz (unread source).
- **Noise**: L = uvw - 0.5, P = 7 L, rotated about z by 0.04 t + (0.2 + (sin 5 P.z + 0.5) 0.15) sin(t/2 + 0.5)
  sin(0.187 t + 0.5) 0.2 (t = time x NoiseSpeed), wobbles 0.05; n1 = tex((|P x 3| - (2, 2, 4.5) t x 0.1) x 0.07),
  value (x + 0.95 y) x 4.6 after lerp(NoiseMin, NoiseMax, n); a boil warp of P by the gradient normal; n2 at P2 x 7 x
  0.07; nz = lerp(0.95, sat n1, 0.5) + lerp(0.95, sat n2, 0.35 dot(dir, fwd) sat(|q2 - eye| x 0.005)) - 0.95.
- **Growth** (c80.w < 1): g = clamp(c80.w, 1e-4, 0.9999), e0 = smoothstep(0, 0.8, g), e1 = smoothstep(0.2, 1, g):
  d x smoothstep(e0, e1, |(L.xy, 1.2 L.z)|) (e0 >= e1: a sphere opening out), or d x g when equal.
- final = lerp(d - (1 - nz), d + nz, d) x sat(fade x growth x 8); alpha = smoothstep(0, 0.2 / (0.85 lerp(0.5, 2,
  acc.a)), final); the colour: the LPV atlas' ambient x the darkening terms x nz + the sun x shadow x (1 - hole), tinted
  lerp(c, c x tint x lum ratio, 0.5 (1 - c80.z)), lerp(c, c x keep, 0.6), + c (8, 4, 0) glow, + the c154 flash;
  composited front to back in 6 / 4 = 1.5 units a step; out at alpha > 0.991. Then g_bExtraSample's end step.

## The client: what's unread

- The voxel frames' content and 1807c8990 (the wire: agent/smoke-server), 1807c5ed0, the +0x8 solid bitset's source on
  the client, the point list for the HE test.
- 1817590b0's exact segment rules; who queues the tracer records (per bullet assumed); 18256af78 / 18256af88's names.
- The LPV (smoke_volume_lpv_cs, SmokeLPVSetup 1811d9d30), the shadow cascade terms, the mask / depth passes, the MBOIT
  passes and the composite; the in-smoke overlay (180ca06e0, overlay_smoke); c98's and c154's sources.
- The HE projectile's lifetime on the client (when 180d1f020 runs).

## The client: what the port takes from the wire

With the wire's decoder merged, client/fx/grenades.js takes it by `useSmokeDecoder(SmokeVolume)` (game.js, one line):
a SmokeVolume per pop event at its `o`, the snapshot's `sv` records pushed (held when they come before the pop event
in the same snapshot), one record applied a frame as CS2 does, and its `tex` / `bounds` handed to
SmokeVolumeView.frame as they are (the decoder's texture is RegenerateTextureBits' own). Without the decoder, the
stand-in fill. The other entry: smokeFrame(id, f) (and an event `{ k: 'smokevol', id, ... }`) with `f.density` Uint8Array(32768) in xyz order ((z x 32 + y) x 32 + x), each byte CS2's texture
value clamp(v / 50, 0, 1) x 255 (1807d90a0, v the voxel's simulation value); optional `f.occupied` (Uint8Array 0 / 1: the
frame's voxel set; default: density > 0 or a voxel of an earlier frame's set) and `f.solid` (0 / 1: the work block's
+0x8 bits, the voxels the smoke cannot fill; without it no solid neighbour gets the outer pair). One call per CS2 frame
(the client blends over 0.1 s); the grid's centre is the smoke event's `at` (m_vSmokeDetonationPos), its tint the
event's optional `color` (linear 0..1, m_vSmokeColor; white without). Until frames arrive client/fx/smoke-standin-fill.js
makes stand-in ones.

## The client: the look, second pass (2026-11-16, client_20261015, shaders_vulkan_dir.vpk)

### The lighting volume (smoke_volume_lpv_cs; the port: client/fx/smoke-lpv.js)

One thread per voxel (x, y, slice), the smoke from `SmokeConstantBuffer_t._m0[z].w` (its atlas slot), written at
x = 34 x slot + voxel x. For the voxel's centre `p = (v - 16) x 20 + 10 + centre`:
- the volume: the smoke's list `LightProbeVolumeData_t` (`_m0[smoke]` = how many, `_m1[smoke x 32 + i]` = {box min,
  box max, a world -> local 4x3, priority `_m3`, the per-view index `_m4`}); the distance outside each box
  (`|max(min - l, 0) + max(l - max, 0)|`), 0 inside; the kept one: inside beats outside, then the higher priority,
  then the nearer (the half-voxel test against the voxel's own box for an outside one);
- `l = PerViewLightProbeVolumeConstantBuffer_t[i]._m0 x p`; `l.z /= 6`; clamped to `_m1 .. _m2` (half a texel in);
  `l.z *= 6`; `uvw = l x _m4 + _m5` (into the atlas); `uvw.z /= 6`;
- n = normalize(p - centre); the faces: z + {0, 1/6, 2/6} for +X +Y +Z, + {3/6, 4/6, 5/6} for a negative component
  (`step(n, 0)`); rgb = Σ face x n² (the three taps of g_tLPV_Irradiance, bilinear) x `_m3.xyz`;
- plus every barn light (g_BarnLights: its frustum, cookie, attenuation, the shadow map's 4 / 9-tap PCF) x
  max(0, n . L), each scaled by `lerp(1, 0.1, sat((sqrt(lum(color)) x range - 80) x 0.01))`;
- a = 1 - dot(g_tLPV_Shadows at saturate(l) x _m4 + _m5, the sun's channel mask `PerViewLightingConstantBufferGpu_t._m4`).

The port (2026-11-16, BUGFIXES "black specks along a smoke's top"): the smoke's list is the map's probe volumes whose
world bounds (the box's eight corners) meet the smoke's box (centre +- 320 u), the first 32 in the map's order
(smoke-lpv.js volumesNear; TODO(trace): the scene system's query test and order, 180d323b0). CS2 runs the dispatch
every frame; the port builds the volume once on the CPU (static: no barn lights), a z slice at a time from the grid's
centre out (15, 16, 14, 17, ...), 1 a frame a smoke and 2 in all, plus at once every slice the march can already read:
the growth (c80.w) keeps density inside `length(L.xy, 1.2 L.z) < e0 = smoothstep(0, 0.8, growth)`, and the LPV
coordinate `lu` lies within |L| of the grid's centre, so texels 15.5 +- 32 e0 and their trilinear neighbours
(lpvSlicesNeeded). An unbuilt slice reads 0: no ambient and LPV.a 0 (no sun), black.

### The raymarch's lighting (smoke_volume_cs, the part the first pass left out)

- the volume normal (g_flVolumeNormalBlend 0.5): density taps at uvw + up x -0.03 and + right x 0.03 (right =
  cross(forward, up)), `nVol = normalize(d - dRight, dDown - d, 0.06)` (view space);
- the noise's gradients: the low octave also at `D x 3 + up x 0.2` and `+ right x 0.2`, `g1 = normalize(n1 - n1r,
  n1 - n1u, 0.8 / 3)`; the boil warp `P2 = P + V^T (g1 + nVol) n1^0.1 x boil x 0.2 + (2, 2, 4.5)(n1 - 1) 0.2 boil L.z`;
  the high octave's gradient the same way at `P2 x 7 + up / right x 0.2`;
- the normal `nW = V^T (lerp(V n0, nVol, 0.5) + (g1.xy x 0.5 + gh.xy x lerp(0.5, 1, sat(n1 - 0.5)) x hiStr, 0) x 0.5 x
  lerp(1, 2, sat((200 - |q - centre|) x 0.005)))`, n0 = normalize(L) x (1 - sat(the HE floor term));
- the LPV atlas at `clamp(lerp(L (n0 . nW), normalize(nW + (0, 0, 0.5)) |L|, 0.2) + 0.5, 0.03, 0.97)`;
- the sun: `d = lerp(n0, nW, 0.5) . sunDir`, `pow(sat(0.8 d + 0.2), 1.5) + pow(sat(1.4 d - 0.5), 3)`, x LPV.a x
  lerp(1, the cascade's shadow (min with g_tParticleShadowBuffer), 0.75);
- the ambient: the LPV's rgb with its HSV saturation x 1.1; `normalize(a) min(|a|, 4) x ...` as the first pass lists;
- per unit of the step: the AO term `smoothstep(0, 0.2, final + 0.3) x sat((16 - g) / 16) x density x 6 x 0.06` and the
  sun term summed; at the end `aoK = sat(ao - a x 0.2)`: rgb x (1 - aoK), a + aoK; the rim light rgb x (1 + sun² x
  (r + r^50 x 8)(1 - sqrt a) a x Σsun x 0.25), r = pow(sat(dir . sunDir), 4) x 0.25; a clamped 1e-5 .. 0.9999;
- the flash (c154): `(1 - smoothstep(0, 0.3, now - t)) x (1 - smoothstep(0, 300, |pL - pos|))` added to the colour,
  pL = q + nW (n2 - 1) x 8.

### c98 and c154's sources

- **c98 (the C4)**: 180d20800 -> **180853e30** (the gamerules, + 0xb0 > 0) and **180cb36f0** (the planted C4s,
  list 1824cb3c0 / next + 0x1280: the one with + 0x12bd set and the latest + 0x12b8, its explosion time); when
  `1 < now - t < 11`: c98 = (its origin, now - t - 1). The shader: a shell `r = w x 3000` clearing between r - 4000
  and r (and r - 20000 .. r - 4000 fading back), the floor's 48 u kept, only for smokes older than w.
- **c154 (a flashbang)**: **1807dfdb0** (vfn + 0x70 of every C_BaseCSGrenadeProjectile: the explode effect) with a
  model name containing "flashbang" -> **180d2cbe0**: the first smoke whose box is within 300 u (18174a510) ->
  18257e030 = (pos, now). 180d20800 holds it 1 s.

### The HE's hole lifetime

The client drops a smoke's HE entry in C_HEGrenadeProjectile's destructor (1810c6420 -> 180d1f020). On the server
CBaseGrenade::Explode **1808c3200** sets EF_NODRAW (0x20), zero velocity and the think **180d0bca0 (SUB_Remove) 0.1 s
on** (0x3dcccccd). So the hole lives until the projectile's deletion reaches the client: about 0.1 s plus the
network delay, not the renderer's 5 s window (the shader's refill curve 0.5..5 s only shows if the entry outlives
that). The port does exactly this (server/cs2web/grenades/grenades.js keeps the HE 0.1 s; client/fx/grenades.js drops
the hole when the id leaves the snapshot's gn). TODO(compare): CS2 in play seems to show the clear longer; if a
capture shows that, the client's entity deletion is delayed somewhere unread (C_BaseEntity's release on the client).

### The upsample (mboit_mixed_upsample; the port: UPSAMPLE_FS)

A full-resolution pixel from its four half-resolution texels: bilinear weights (the 8 x 8 group's 6 x 6 shared
tile), x exp(-rel² / (2 σ²)) per texel when any relative depth difference `|z - z_i| / z` is >= the threshold
(`DepthThreshold` hash 0x0b8dbc49 = **r_csgo_upscale_depth_threshold 3**, `JoinedSigma` 0x5f83a799 =
**r_csgo_joint_upscale_sigma 0.002**, set by 1811e0360 at 1811e0df6 / 1811e0e19 from the cvars 1825f66e0 / 1825f66d0;
the attribute names are CUtlStringToken MurmurHash2, seed 0x31415926, of the lowercased name). Before that, with the
smoke's depth range (front, back; normalized log depth): the pixel behind the smoke's back (or no back, < -1) takes
the plain bilinear weights, in front of its front none. A pixel left with no weight is written (1, 0, 0, a) for
**r_csgo_smoke_fullres_pass** (default 1): marched again at full resolution. Other defaults read:
r_csgo_smoke_fullres_enhance 0, r_csgo_smoke_shadow 1, r_csgo_smoke_upscale_discard_pixels_behind 0,
r_csgo_smoke_avoid_flat 1, r_csgo_smoke_clip_sniper 1 (stubs 1801266f0..1801269a0). TODO: which upsample combo
(D_MODE 0..2, D_FORCE_MR) each setting picks; the port follows D_MODE / D_FORCE_MR variant 4.

### The in-smoke overlay

- **180ca06e0** (the pawn's think 180c686f0 when 1807cd400, a constant 1, is set): per smoke the density at the eye
  **1807cd230** (the eye's voxel, if not solid: clamp(v / 50, 0, 1) of the current buffer, x smoothstep(22, 17, age)
  x smoothstep(0.1, 1.5, age); 1807c2fc0 is smoothstep with either edge order) over **sv_smoke_volume_blind_start 0.2**,
  clamped; the colours averaged by it; returns the sum clamped (kept at the old value while 0.2 < it < old and old >
  0.8). 180c686f0: a rise taken at once, a fall by Approach (1803a4e70) at **cl_smoke_lower_speed 1** x frametime.
- **overlay_smoke** D_ACCUM_PASS: a small accumulation (the composite samples its 4 corners at 5 % / 95 %) of the
  smoke's colour where the smoke depth's y < -0.55: a falls max(6 / 255, lerp(3.5, 1.5, a)) x dt, rises toward the
  smoke's alpha at 6 x dt, the colour follows at 2 x dt, halved on g_bHEGrenExplosion; its draw: the corners bilinear,
  alpha smoothstep(0, 0.95, a) (the viewmodel pass: alpha x alpha x 0.75).

### The noise texture and the sounds

- materials/dev/noise/worley_perlin_z0000_tga_37c9ebc1.vtex: 128 x 128 x 128 RGBA8888, 1 mip; R 0..199 (mean 18.9),
  G 17..69 (mean 37.6), B 72..147, A 0..180 (the raymarch reads R and G). Baked (lasers-bake --smoke-noise) to
  ze-fx/smoke/noise.bin, R G bytes as stored.
- Sounds (lasers-bake --smoke-sounds -> ze-fx/smoke/sounds): BaseSmokeEffect.Sound (+ SoundDistant), SmokeGrenade.Bounce
  (+ Bounce_Can), SmokeGrenade.Clear, SmokeGrenade.PullPin / Throw, Decoy.PullPin / Throw. The decoy bounces with
  **Flashbang.Bounce** (CDecoyProjectile vfn 0x9b8 = 1809b3e30, the flashbang's own 1803a46d0 the same string).

### What is not CS2's in the port, and why

- The barn lights in the LPV: the renderer draws the map's lights baked (no realtime barn-light shadows), so the
  LPV leaves them out. The sun's cascade term in the raymarch is CS2's now (world/sun-shadows.js, the line below).
- MBOIT: built in the fourth pass (below) for the particles and the smoke, on smoke frames only.
- The characters-only depth (DepthNoCharacters): built in the fourth pass (world/depth-nochar.js).
- The blue noise: interleaved gradient noise for the start's jitter (CS2's BlueNoise texture not baked).
- g_bExtraSample's end step: not ported (the march stops at the last whole step).
- The probe volume pick: CS2's (fourth pass: priority = indoor_outdoor_level); the probes box-filtered by 4 in the bake.
- The upsample's half-resolution scene depth (LinearDepthHalf): the full-resolution depth under each texel's centre.
- The overlay: its accumulation is 2 x 2 (CS2's size unread), the viewmodel pass not drawn.
- The bullet start for others: their eye (CS2: the muzzle's tracer record), yours: the eye - right 7 - up 5 as traced.

## The client: third pass (2026-11-16)

- **The smoke gone before 22 s is CS2's.** The server sets the dissipation flag at 19 s (1809d47d0); from then the
  records carry it, the client's step (1807c5ed0, src/cs2web/sim/smoke-sim.js) clears the emitters and the densities
  drain; once no voxel has a byte, RegenerateTextureBits' bounds stay at +-FLT_MAX (inverted: the scene object's box
  fails every test) and CS2 draws nothing, as the decoder's `bounds = null` does here. The client's own fade (c80.x,
  17..22 s) runs underneath. Nothing to change; the decoder's header says so and has `emitters` as a getter now.
- **Blue noise**: textures/dev/blue_noise_256.vtex (core pak01; the engine's `BlueNoise` attribute, hash 0x88243422,
  named in client and scenesystem), 256 x 256 RGBA8888, baked by lasers-bake --smoke-bluenoise to ze-fx/smoke/
  bluenoise.bin (R). smoke_volume_cs reads `.x` at `pixel & PerViewConstantBufferCsgo_t c11` (an int2 mask: taken as
  255, the texture's size - 1; the client's write of c11 is unread).
- **g_bExtraSample**: after the loop, one more step at the ray's end (`start + dir x len`), each smoke tested at the
  last step's t (`t - step`), weighted `(tStop - (t - step)) x 0.25` (smoke_volume_cs lines _13238 / _21812 / _13244),
  with the bullets' fields as the loop left them. Ported.
- **Other players' trail start**: their world model's muzzle (weapons/muzzle.js, the eye when it isn't drawn), as
  CS2's tracer record (180901390 mode 0).
- **LinearDepthHalf**: depthtolineardepth's pixel shader writes `1 / ((sat((d - m1) / (m2 - m1)) x m0.z + m0.w) x
  dot(m3, normalize(ray)))` from one texel of the depth at the pixel (no min / max over a block): the radial distance.
  How the half-resolution copy is fed (which depth texture, at which coordinates) is unread; the port takes the
  full-resolution depth under each half-resolution texel.
- **Probe volume priority**: LightProbeVolumeData_t._m1[i]._m3 (an int, the higher wins inside) is filled by client
  code not located (1811d9d30 builds the pass list only); the entities carry no priority key (dust2's 43 volumes:
  indoor_outdoor_level, array_index, ...). Still the smallest volume; TODO(trace) the fill.
- **The GPU timer**: the smoke pass's query now starts only when no other TIME_ELAPSED query is running (prof.js runs
  its own) and drops a result that never comes after 120 frames (`sv.timeGpu = true; sv.gpuMs`).

### Still not CS2's, and what each would take

- **Sun shadow cascade** (smoke_volume_cs `lerp(1, csm, 0.75)` and min with g_tParticleShadowBuffer; the LPV's barn
  lights' shadows): CS2 samples the scene's sun cascades (PerViewLightingConstantBufferGpu_t m13: a 4x4 per cascade,
  the shadow atlas, 4- to 9-tap PCF). **Done since** (2026-11-16): CS2's cascades are the renderer's own now
  (world/sun-shadows.js, docs/game/shadows.md), installed into the smoke through `smokeSunShadow` /
  `setSunShadow` (fx/grenades.js). Still 1: the particle shadow buffer (CS2 builds it at Very High only, not ported).
- **MBOIT**: CS2's translucents write moments (pass 1: zeroth + 4..6 moments of log depth) that the smoke's pass 2
  uses to fade itself behind them, and the smoke's own moments dim particles drawn after. Here no translucent writes
  moments: it needs a moments pass for every particle / effect material (a second draw of each with a moments
  shader) and the resolve in each of their shaders. Not done.
- **Characters-only depth**: a depth pass of the players alone (bodies are a handful of skinned meshes) would let the
  smoke tell a character pixel (> 10 u nearer than the scene without them). Not done; cost: one depth-only render of
  the bodies' skinned meshes into a target of the scene's size when an HE / C4 hole is live.
- **The overlay**: the accumulation's size (CS2 samples it at 5 % / 95 % of m1.x / m0.x), the viewmodel pass (drawn
  over the viewmodel, alpha a^2 x 0.75: the viewmodel here renders after the world in its own pass) and the eye
  density's consumer (180ca06e0's alpha and colour go to the pawn's m_flLastSmokeOverlayAlpha / m_vLastSmokeOverlay
  Color; what reads them is unread) are not ported.
- **Barn lights in the LPV**, the probe priority, the half-resolution depth and the c11 mask, as above.
- **A real CS2 smoke to compare**: no .dem files on this machine (the CS2 folder, Downloads, D:\ to depth 3) and no
  demo parser in the repo's tools; the owner's CS2 was not started (asked to ask first).

## The client: MBOIT as CS2 runs it (traced 2026-11-16; built in the fourth pass)

Moment-based order-independent transparency over CS2's translucents (spritecard: D_MBOIT_PASS1 / D_MBOIT_PASS2
combos, ruled out with S_MODE_GBUFFER, S_OPAQUE and D_PANORAMA_PARTICLE; csgo_effects: the same plus
D_MBOIT_4_MOMENTS; smoke_volume_cs and smoke_volume: PASS1 / PASS2 / OPTIM; the resolves: mboit_mixed_upsample,
mboit_mixed_combine).

- **Pass 1 (moments)**, csgo_effects D_MBOIT_PASS1 (6 moments): `z = (log(dot(fwd, p - eye)) - log near) / (log far
  - log near) x 2 - 1` (PerViewConstantBufferCsgo_t c37.w / c38), `b0 = -log(1 - clamp(alpha, 1e-5, 0.9999))`; three
  targets: SV_Target0 = (b0, 0, 0, 0) (the zeroth moment), SV_Target1 = (z, z²) x b0 (moments), SV_Target2 = (z³, z⁴,
  z⁵, z⁶) x b0 (moments_extra); summed (additive). D_MBOIT_4_MOMENTS keeps z..z⁴. The smoke's pass 1 writes the same
  from its march.
- **Pass 2 (resolve per surface)**: the six moments / b0, lerped toward the bias vector (0, 0.48, 0, 0.451, 0, 0.45)
  by c37.y, the Hankel / Cholesky solve of the 6-moment problem (the code in smoke_volume_cs's end and csgo_effects
  pass 2, identical), the three roots by the trigonometric cubic, the transmittance `T = sat(exp(-b0 x dot(...)))`
  at the surface's z with the overestimation c37.x; output `(rgb x a, clamp(a, 1e-5, 0.9999)) x T`, summed.
- **The smoke in it**: smoke_volume_cs PASS2 multiplies its result by T at its end depth (`_9769`); the OPTIM pass
  (cs variant 4) resolves the smoke's colour at 4 depths between its optim depth range's x and y, adding each
  `colour x T` into the colour target.
- **Mixed resolution**: mboit_mixed_upsample brings half / quarter resolution moments, colour and smoke depth up
  (the joint-depth weights traced before); mboit_mixed_combine (variants with D_UPSCALE_SMOKE_DEPTH, D_HI_LOW,
  D_MBOIT_4_MOMENTS) copies / combines zeroth, moments and extra between resolutions.
- **Located 2026-11-16 (fourth pass, below)**: the final composite (mboitfinal), the targets' formats and sizes, the
  passes' order and resolutions.

## The client: MBOIT located (fourth pass, 2026-11-16, client_20261015 + shaders_vulkan_dir.vpk)

Shaders read with `lasers-bake --shader-src <name>` (bake/ShaderSrcBake.cs now also dumps compute programs:
smoke_volume_cs). Line numbers are the dumped files' (`<name>_PixelShader_s<static>_d<dynamic>.glsl`).

### The final composite: mboitfinal (materials/dev/mboitfinal.vmat)

- Loaded by **1811cba30** with mboitmixedcombine.vmat and mboitmixedupsample.vmat; drawn by the "MboitFinalPass"
  layer (**1811e1b80** / 1811e2920).
- PS s0_d0 (no combo): `c = MoitFinal[px]` (point), `t = 1 - exp(-zeroth[px].x)`,
  `out = (c.rgb x t / (c.a + 1e-5), t >= 0.9999 ? 1 : t)`. Blend (states dump, dynamic 0): **One / InvSrcAlpha**
  colour, SrcAlpha / InvSrcAlpha alpha; no depth test. So the scene becomes `rgb' + scene x e^-b0`.
- Combos: D_UPSCALE_MIXED (s0_d1: MoitFinal / zeroth at low resolution, joint-upsampled with the same weights as
  mboit_mixed_combine below), D_COMBINE_HI_RES (s0_d2: alpha sum = low + hi output), D_DENOISE_SMOKE, D_COVER_GAPS 0..2
  (d6: the output copied with alpha 1), D_SMOKE_PERF_TEST; StencilRef 128.

### The targets (1811f3780)

Twelve names (MBOIT_B0 / B / B_EXTRA / OUTPUT, MBOIT_MR_*, MBOIT_BLOOM_*), created by the render system's vfn 0x2b8
with flags 0x409 and a format from **181d2a510** (6 moments: 0x11, 0x22, 0x13, 0x0f) or **181d2a520**
(r_csgo_mboit_use_4_moments: 0x11, 0x13, 0x0f; three targets). The client's ImageFormat values mapped through
rendersystemvulkan_20261015's table at file offset **0x5619a0** (dword per format + 1, VkFormat): 0x11 -> 100
R32_SFLOAT, 0x22 -> 103 R32G32_SFLOAT, 0x13 -> 109 R32G32B32A32_SFLOAT, 0x0f -> 97 R16G16B16A16_SFLOAT. So
**B0 R32F, B RG32F, B_EXTRA RGBA32F, OUTPUT RGBA16F**. Sizes from the view (param_1[6]): the full set at the view's
size unless r_csgo_mboit_force_mixed_resolution (and the view isn't a +0x31 one, and annotation_auto_load is 0); the
MR set at size / **r_csgo_mixed_resolution_particles_scale** (int, default **2**, 180124b60) when
**r_csgo_mixed_resolution_particles** (bool, default **1**, 180124a10); the BLOOM set at size / 4 always.

### Cvars (registration functions, client_20261015)

| cvar | fn | handle | default |
| --- | --- | --- | --- |
| r_csgo_mboit | 180124370 | 1825f6668 | 1 |
| r_csgo_mboit_bias | 180124420 | 1825f6698 | 5e-6 (0x36a7c5ac) |
| r_csgo_mboit_overestimation | 180124610 | 1825f6688 | 0.01 (0x3c23d70a) |
| r_csgo_mboit_use_4_moments | 180124760 | 1825f66a8 | 0 |
| r_csgo_mboit_force_mixed_resolution | 180124570 | 1825f66c8 | 0 |
| r_csgo_mixed_resolution_particles | 180124a10 | 1825f6628 | 1 |
| r_csgo_mixed_resolution_particles_scale | 180124b60 | 1825f6648 | 2 |

PerViewConstantBufferCsgo_t, filled by **1811fef80**: +0x24c (c36.w) the mixed scale (1 when not mixed), **+0x250
(c37.x) overestimation**, **+0x254 (c37.y) bias** (1811ff9ee / 1811ffa00), +0x258 (c37.z) 1 / scale, **+0x25c
(c37.w) = log(view + 0x30)**, **+0x260 (c38) = log(view + 0x34)** (1811ff353 / 1811ff369: the view's near / far).

### Which views run it (181207024) and the layer order (1811d9d30)

- The view's MBOIT flag (+0x1bb) = `r_csgo_mboit && ((attr(0xaf8c0cb3) && !attr(0xbad93cb2)) || attr(0x3b418add))`,
  attr = the view's attribute set (+0x110, 180161a30) by CUtlStringToken hash; the names weren't found among
  client / scenesystem / engine2's strings (built at run time). Not tied to a smoke being on screen.
- 1811d9d30 (CRenderingPipelineCsgo::AddLayersToView) with the flag set loops the translucent layers twice
  (`count = flag + 1`): **"Static - MBOIT Pass %d"** (1811efcc0: the static translucents) then **"Dynamic - MBOIT
  Pass %d"** (1811e49d0: the dynamic ones, particles among them; pass index at +0x138; its targets the full set
  `param_2 + 0xd8`, the MR set `+ 0xf8` when forced mixed). Then, in order: SmokeLPVSetup, "MBOIT(%d) Smoke 1/4" /
  "1/2" / "Full" (one by the smoke's resolution), "MBOIT(%d) Translucent 1/2" (the mixed-resolution particles),
  "Water Translucent Combine", WriteSmokeDepth, "Mixed Resolution Particles", "Dynamic", SmokeOverlayDataA / B
  (rt_SmokeOverlayData, "OverlaySmokeUpdate", "OverlaySmoke"), then "GameOverlay Particles". The upscale / downsample
  layers: 1811e1710 ("MBOIT(%d) Downsample (%d)"), 1811e3220 / 1811e0360 ("MBOIT(%d) Upscale (%d)", "Upscale CS").

### The passes' shaders

- **Pass 1** (spritecard D_MBOIT_PASS1 s0_d4, csgo_effects the same): `z = (log(dot(c28, p - eye)) - c37.w) / (c38 -
  c37.w) x 2 - 1`, `b0 = -log(1 - clamp(a, 1e-5, 0.9999))`; SV_Target0 (b0, 0, 0, 0), Target1 (z, z^2) b0, Target2
  (z^3, z^4, z^5, z^6) b0. An additive renderer (|SpriteCardPixelControls c1.w| = 0) discards when all of its colour
  < 0.001 and takes alpha 0.0005 when its colour isn't black (s0_d8 803-815, 946-958).
- **Pass 2** (s0_d8 84-189): T at z from the moments (the bias lerp, Cholesky, the cubic's roots, the bound with c37.x);
  discard when T < 1e-4; out `(rgb, clamp(a, 1e-5, 0.9999)) x T`. Its render state for the MBOIT combos: One / One
  colour and alpha (states dump, static 0 dynamic 8).
- **The smoke's pass 1** (smoke_volume_cs D_MBOIT_PASS1, D_SMOKE_INSTANCES=6, D_SMOKE_QUALITY, D_SMOKE_NEW_VISUALS:
  s0_d198 2591-2607): one surface per pixel: alpha = the march's (`a + sat(ao - 0.2 a)` when g_flAOEffectStrength !=
  0), skipped below 1e-5, at the depth of the point where the march stopped (`_13193`: the step past 0.991 or the
  ray's end), added into the three moment UAVs. PASS2 (s0_d199) the colour x T at that same depth.
- **mboit_mixed_combine** (blend states: D_HI_LOW and D_LOW_HI One / Zero, D_LOW_HI_OUTPUT and D_UPSCALE_SMOKE_DEPTH
  One / One): D_HI_LOW (s0_d0) the hi moments bilinear at the low pixel; D_LOW_HI (s0_d1) the low moments up: the hi
  pixel's device depth `d` against the four low texels' (gathered), `rel = |d - d_i| / d`; with the smoke's depth
  (unless g_bIgnoreSmokeDepth): the optim depth's front / back gathered, a pixel behind every covered texel's back with
  all four covered takes rel 0; all rel < lerp(0.0012, 4e-5, sat((d - 0.97) x 33.33)) -> bilinear, else Gaussian
  weights (sigma lerp(0.0009, 6e-5, sat((d - 0.9) x 10))) x the bilinear ones, < 1e-5 in all -> the point sample;
  D_KEEP_FULL_RES (s0_d4) discards where SmokeFullResMask is set (the full-resolution smoke's pixels keep the hi
  moments); D_LOW_HI_OUTPUT (s0_d2) the output up, additive, discarding where the low zeroth is 0.

### The characters-only depth (DepthNoCharacters)

**1811ec0c0** (called from 181201670, the depth prepass layers "Depth Prepass Large / Small / AlphaTested"): when the
cvars at 1825f6948 and 1825f6958 are on and an HE hole is live (the 5-entry table 18223f24c, `0 <= now - t < 5`) or
the C4's explosion (180cb36f0) is, it makes "Temp_NoCharactersDepth", "ResolveDepthNoCharacters" (MSAA),
"CopyDepthNoCharacters": the prepass depth copied before the characters are drawn into it. Otherwise nothing.

### The remaining reads (fourth pass)

- **The probe volume's priority**: **180d323b0** fills SmokeLightProbeVolumeData_t (0x1810 bytes, locked per smoke
  pair) from the scene system's light-probe query over the smoke's box (centre +- 32 voxels x 0.5): per volume (up
  to 32) its attributes "Transform" (+0x30), "VolumeMaxs" / "VolumeMins" (+0x20 / +0x10), **"Priority"** (hash
  0x33631172, +0x64) and "LPVIndex" (0x7176fdea, +0x68). The entity side: env_light_probe_volume /
  env_combined_light_probe_volume's field table (1801fc610 / 1801fcdc0) fills **m_Entity_nPriority from the
  `indoor_outdoor_level` key**. The port (smoke-lpv.js volumeFor): inside, then the higher indoor_outdoor_level,
  then the nearer. TODO(trace): the scene object's copy of m_Entity_nPriority into its "Priority" attribute is
  assumed from the names.
- **The half-resolution depth**: **1811e58b0** makes "HalfResDepth" (format 0x2a: VkFormat 129 D32_SFLOAT_S8_UINT) at
  size / r_csgo_mixed_resolution_particles_scale and, with the cvar at 1825f66b8, "HalfLinearDepth" (0x27: 76
  R16_SFLOAT), filled by a "DownsampleDepth" layer binding the scene depth (attribute 0x6656de6f) with
  materials/dev/downsample_depth.vmat (core pak: downsample_depth, combos D_MINMAX_CHECKER_2X2 (s0_d1: min on odd
  checker pixels, max on even, of the 2 x 2), D_RESOLVE, D_MAX, D_MIN, D_NON_MSAA_DEPTH, D_MSAA_SAMPLES 0..4,
  D_WRITE_COLOR; s0_d0: the texel at pixel x the ratio). Which combo the layer takes is set in its material /
  1811cd9a0: unread. The port keeps the full-resolution depth under each low texel's centre (stand-in).
- **The overlay's accumulation**: SmokeOverlayDataA / B.vtex (1811dd5f6 / 1811dd6e9, "rt_SmokeOverlayData",
  "OverlaySmokeUpdate", "OverlaySmoke") are made at the size of the target in the layer builder's [rbp + 0x2e0]
  (its description by the render system's vfn 0x150, remade when that size changes); that target isn't identified,
  so the port's 2 x 2 stays (the shader samples its corners at 5 % / 95 %, which a 2 x 2 holds exactly only if the
  real one is filled uniformly). The viewmodel pass and the eye density's reader (m_flLastSmokeOverlayAlpha) remain
  unread.

### MBOIT, built (the port)

- world/mboit.js: the spritecard renderers' meshes (fx/effects.js registers them; not bloom-only, GameOverlay, mod2x
  or lighten) leave the scene pass on smoke frames and are drawn twice inside it at the smoke's composite (render
  order 5e5, before the GameOverlay particles at 1e6): twins of their materials with MBOIT 1 / 2, additive,
  depth-tested against a copy of the scene's depth (their own: the soft particles sample the scene copy's).
- client/fx/smoke-mboit-shader.js: HILOW_FS, LOHI_FS (+ an early out with the same result), MASK_FS + SMOKEFULL_FS
  (the full-resolution march under a stencil), RESOLVE_FS, UPSAMPLE_FS, FINAL_FS. The march writes its pass-1 alpha
  and depth beside its depth range; one march serves both passes (CS2 marches twice, PASS1 and PASS2: the same
  inputs give the same alpha, colour and depth, so the resolve of the kept colour is PASS2's result).
- world/depth-nochar.js: DepthNoCharacters (the bodies' group drawn last, a depth blit between) while an HE hole or
  the C4's sweep is live; smoke-shader.js `chr` (s0_d199 230-249: the scene without the characters > 10 u further
  along the ray) keeps the HE floor term (656: kept, not 0) and zeroes the C4's (722). The march's scene texel is
  now pixel x 2 (CS2's `_22509 x g_MixedResolutionScale`; it was the pixel's centre x 2).

## The sun-shadow hook (for agent/sun-shadows)

smoke-shader.js COMMON marks `//@@SUN_SHADOW@@` where a `float smokeSunShadow(vec3 p, float dist)` goes (p the
lighting point pL, dist its distance from the eye): CS2's `min(lerp(cascade visibility, 1, sat(dist x c12 + c11)),
g_tParticleShadowBuffer.z)`. The march multiplies it in exactly where CS2 does: `sun x LPV.a x lerp(1, it, 0.75)`.
The default returns 1. `SmokeVolumeView.setSunShadow({ glsl, uniforms })` puts a hook in (and `null` takes it out).
