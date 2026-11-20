# C_Inferno on the client: the ground fire particle

client.dll of 2026-11-12 (`game/csgo/bin/win64/client.dll`, md5 b6f4750a..., the same file as source2-compiler's
`tools/re/binaries/client_20261112.dll`), read with tools/re (fnat.py, disasm.py, xref.py, callers.py, fieldwrites.py,
schema.py, impat.py) and decompiled through ReVa on `/client_20261015.dll` (the project has no 11-12 build): every
function below was found in 10-15 by a masked byte signature of its 11-12 body (scratch sigfind: rel32 / rip disp32
wildcarded, one hit each) and its constants re-read in 11-12. First read 2026-11-16 ("keen-brahmagupta"), ported the
same day ("trusting-perlman"): web/src/cs2web/client/fx/inferno.js (the entity) and inferno-snapshots.js (the snapshots).

| 11-12 | 10-15 | what |
|---|---|---|
| 180d3bab0 | 180d438f0 | C_Inferno::ClientThink |
| 180d49a00 | 180d517f0 | C_Inferno::SynchronizeDrawables |
| 180d4aec0 | 180d52cb0 | the particle: create / CP0 / CP3 / update (flags) |
| 180d48c00 | 180d509f0 | the drawables' outward edge masks (+0x30) |
| 180d3eb80 | 180d46970 | the wall traces, hull planes, CP10 (outline) / CP9 (climbing) snapshots |
| 180d40fd0 | 180d48dc0 | CP1 (core), CP11 (fill), CP12 (base) snapshots |
| 180d40e10 / 180d48700 / 180d48530 | 180d48c00 / 180d504f0 / 180d50320 | build + set CP1 / CP11 / CP12 |
| 180d3c280 | 180d440c0 | the remnant (molotov_groundfire_remnant) |
| 180d4f4c0 (old) | 180d4f4c0 | the bounds (m_minBounds / m_maxBounds) |
| 180d3a770 | 180d425b0 | add a hull plane |
| 180d3d9c0 | 180d45800 | ramp(a, b, c) = a - b / c when a x c > b, else 0 |
| 180d4b730 | | vfn 0x7c8: the effect name |
| 180d391c0 | | the constructor (+0x866c = 30, +0x8670 = 80; each drawable 180d39370 zeroes +0xc0, +0x190, +0x194) |

## The entity's fields (schema.py on 11-12)

m_firePositions +0x1108 (Vector[64]), m_fireParentPositions +0x1408, m_bFireIsBurning +0x1708 (bool[64]),
m_BurnNormal +0x1748, m_fireCount +0x1a48, m_nInfernoType +0x1a4c, m_nFireLifetime +0x1a50 (float),
m_bInPostEffectTime +0x1a54, m_lastFireCount +0x1a58, m_nFireEffectTickBegin +0x1a5c, the 64 drawables of 0x1b0 at
+0x1a60, m_drawableCount +0x8660, m_maxFireHalfWidth +0x866c (30), m_maxFireHeight +0x8670 (80), m_minBounds
+0x8674, m_maxBounds +0x8680, m_flLastGrassBurnThink +0x868c. The system: +0x10b8 its linked handle, +0x10c8 the
system, +0x10d8 the remnant's index (-1 none), +0x10e0 / e8 / f0 / f8 / 0x1100 the CP1 / 11 / 10 / 9 / 12 snapshots.

The server (server.dll 2026-11-05 CreateFire 180345dc0; the game's current build at 180342950): m_firePositions[i] =
the fire's position, m_fireParentPositions[i] = its parent fire's position (its own with no parent), m_BurnNormal[i]
the ground normal, m_bFireIsBurning[i] = 1, m_nFireLifetime = vfn 0x898 (the flame lifetime), m_fireCount + 1;
m_nFireEffectTickBegin set in 180350270 (a tick), m_bInPostEffectTime in 180346090, m_nInfernoType 0 / 2 in 18034ecd0 /
18034ec90. Positions are world positions; the client adds the origin to the parent position anyway (below).

## A drawable (0x1b0)

+0x00 position, +0x0c parent (origin + m_fireParentPositions[i]), +0x18 normal, +0x24 0, +0x28 RandomFloat(0.04, 0.06),
+0x2c RandomInt(0, 100) < 50, +0x2d walls traced, +0x30 64-bit outward mask, +0x38 [15] wall fraction, +0x74 [15] the
point scale, +0xb0 the smallest fraction, +0xc0 plane count, +0xd0 [12] planes (n, d), +0x190 the current plane's merge
count, +0x194 planes off, +0x1a0 state (0 growing, 1 burning, 2 dying, 3 out, 4 unseen during a sync), +0x1a4 the
state's start time, +0x1a8 size, +0x1ac target size. The random draws are the client's global stream
(CUniformRandomStreamImpl<CAtomicMutex> 0x182230098; tier0 RandomInt 0x18015efc0 / RandomFloat).

## ClientThink (180d3bab0)

Until m_bInPostEffectTime: flags = 1 when m_fireCount != m_lastFireCount or the entity's network data changed
(18021c9b0); then SynchronizeDrawables (flags |= its result) and m_lastFireCount = m_fireCount. (+0x8690: a list of the
fire positions with a time each for another consumer: not ported.) Each drawable: growing: +0x2d = 0 (traced again),
size = (curtime - t0) x target x 0.5, burning at target (t0 = curtime); a size change sets flags |= 1. Dying: flags |= 1,
size = target - target x 0.5 x (curtime - t0); at <= 0 out (t0, bounds). The bounds again when the data changed and no
drawable went out this think. Then 180d4aec0(flags).

In the post-effect time: the remnant once (+0x10d8 == -1), then the system stopped (18189c530(sys, 0, 0, 1, 1)) and its
handle let go (the manager plays it out).

## SynchronizeDrawables (180d49a00)

Burning drawables become 4. For each fire i < m_fireCount: the first drawable within 12 u per axis (1809adf10) takes
the fire's exact position. A fire not burning puts that drawable out (state 3, the bounds; result 3). A burning fire
with a drawable: 4 -> 1. Without one (and < 64): a new drawable (state 0, t0 = curtime, the parent = origin +
m_fireParentPositions[i], target RandomFloat(70, 90) for m_nInfernoType 0, else (50, 70); m_drawableCount + 1;
result 3). After: drawables still 4 start dying (state 2, t0 = curtime).

## The particle (180d4aec0)

Only with drawables and the global byte +0x58 & 2. Created once: the name by vfn 0x7c8 (180d4b730: m_nInfernoType 0 ->
molotov_groundfire, else incendiary_groundfire when inferno_ct_experiment (bool, default 1, registered 1800f7b10) is on,
else molotov_groundfire; firework_crate_ground_effect is not chosen there), seed = murmur3's finalizer of
m_nFireEffectTickBegin (0x85ebca6b, 0xc2b2ae35; 0 stays 0), 181893de0(mgr, 0, name, origin, -1, seed); CP0 = the origin
(181894fc0), CP3 = (m_nFireLifetime, m_maxFireHeight, 70) (181894fb0). Then flags & 1: the edge masks (180d48c00);
flags & 3: the edges (180d3eb80, its two snapshots to CP10 and, when it has one, CP9: `[system + 0x20]` vfn 0xa8 =
SetControlPointSnapshot(cp, snapshot, 0)), the cores (180d40fd0: CP1, 11, 12). On creation the system's time is set
back (180d49370(sys, now - tickBegin x interval)) and sys+0x30 |= 4. NOT PORTED: that time offset (a late client starts
the fire as it is now; ours gets the event as it starts).

The snapshots (particles.dll's ParticleSystemMgr +0x148 create, +0x150 fill; descriptor slot -> attribute in
web/src/fx/particles/functions/snapshot.js): positions are local (pos - origin: the entity has no angles and scale 1,
the 18015c580 zero-angle branch; the general branch is the inverse of the entity's transform), the ops' m_nLocalSpaceCP
0 brings them back through CP0.

## The edge masks (180d48c00)

Per drawable i, per direction k of 15 (180d45820: sincos(360 / 15 x k), z 0): the point max(60, size) out; bit k of
+0x30 when drawable i is the nearest to it (Euclidean, strict <: the first of equals).

## The edges (180d3eb80)

Every drawable not out (all 64 slots in CS2: the unused ones trace once and give nothing; ours skips them). Planes
cleared (180d4fd30). A ray up 60 u (filter 180b722a0: CTraceFilter interacts 0xc3001, group 3, flags 0x49, detail
layers 0xffff, object sets 0xf; inferno_batched_rays (bool, default 1, registered 1800f7690) casts them batched through
vfn 0x5e8 of the physics query, the same rays: ours casts them one by one). For each direction k (24 degrees apart),
when +0x2d is 0: from (x, y, z + 30 + upFrac x 30 x blocked x upHit) to (x + cos x target, y + sin x target, that z +
max(upFrac, 0.5) x 30 x blocked), blocked once any earlier direction hit. Start-solid: the outward mask and the rest of
the fractions / scales cleared, the loop ends. A hit: a plane through the hit point (local) with the hit normal
(180d3a770); with c = -(dir . n) x target, scale[k] = ramp(frac, 10, c), frac[k] = ramp(frac, 5, c), the smallest
frac kept (+0xb0); no hit: frac[k] = the fraction, scale[k] = 1 - 10 / max(60, size). With +0x2d set the cached values.
For each outward direction: two outline points 40 u up at min(size, frac x target) along k and along (2k - 1) x 12
degrees, normals those directions, radius max(60, size) (CP10); and when that distance < size a climbing point at the
drawable + 40 u up, normal normalize(cos, sin, RandomFloat(-15, 15) / max(1, distance)) (tier0's global RandomFloat,
reseeded in 180d40fd0's RandomSeed), radius max(60, size) (CP9). After the loop a plane still being merged is kept and
+0x2d = 1.

Hull planes (180d3a770): nothing once off (+0x194) or 12 planes; the first goes in; a plane whose 2D cross with the
current one (n.y x cur.x - n.x x cur.y) is under Inferno_concav_plane_threshold (float, default -10, registered
1800f6ac0) drops them all (count 0, off); one within 0.04 (0x182231a20 x4) of the current in every component merges
(cur + count x new, renormalised by the xyz length with rsqrtps + a Newton step; count + 1); else the next slot.

## The cores (180d40fd0)

Drawables from the last to the first (index > 63 stops), each with its own CUniformRandomStreamImpl seeded with its
index; two 30-unit cell grids (180d40df0: 32 x 4 words, 1/30 = 0x3d088889; 180d4de50: word (floor(z / 30) & 3) x 32 +
(floor(y / 30) & 31), bit floor(x / 30) & 31, true when newly set). The normal N = normalize(local - local(parent)). A
drawable is "open" when no wall fraction is < 1. For each direction k: r = sqrt(RandomFloatExp(0.1, 0.65, 0.9)) x lim,
lim = min(max(60, size), scale[k] x target), the point local + dir_k x r; near = the smallest plane distance (n.p + d,
FLT_MAX with none). Out drawable: a zero entry to CP11. near <= 10, or the cell taken in the first grid and (y x 0.71 -
x x 0.7, y x 0.72 + x x 0.715, z + 35) taken in the second: a zero entry to CP11 (and CP12 when not open). Else (point,
N, radius max(60, size), alpha scale[k], scratch min(near, lim - r)) to CP11 and, when not open, to CP12. An open
drawable then gives CP12 its centre (N, max(60, size), alpha 1, scratch max(60, size)) and 14 zero entries. CP1: one
entry a drawable: (centre, normal = the centre (C_OP_SetFromCPSnapshot writes it to the previous position), radius
max(60, size), scratch +0xb0); zeros for an out drawable. Descriptors: CP1 (180d40e10) slots 0, 2, 10, 14 (position,
normal, radius, scratch); CP11 / CP12 (180d48700 / 180d48530) also slot 12 (alpha).

## The remnant (180d3c280)

When the system exists: it reads the system's CP1 / 9 / 11 snapshots (vfn 0xd8), and with all three: creates
`particles/inferno_fx/molotov_groundfire_remnant.vpcf` (1809d4ec0), CP0 = the system's CP0 transform (vfn 0xc0 / 0xc8 ->
a matrix), CP3 = (m_nFireLifetime, m_maxFireHeight, 70), the three snapshots set on it (180a12420), started (vfn 0x18).
Called from ClientThink's post-effect branch and from 180d4aec0's tail.

## Particle classes the tree needed (particles.dll 63babcbf)

C_OP_SetFromCPSnapshot (Operate 0x1801ff7c0), C_INIT_VelocityFromNormal (0x18013cc50), C_INIT_Orient2DRelToCP
(0x1801432f0), C_INIT_DistanceToCPInit (0x1801537a0), C_INIT_SetAttributeToScalarExpression (0x180166890),
C_OP_RadiusDecay (0x1801d35a0), C_OP_SpinYaw (C_OP_Spin's 0x1801d6ad0 on yaw), C_OP_MaintainEmitter's snapshot count
(0x18010a207: the CP's snapshot +0x9e0 replaces m_nParticlesToMaintain): web/src/fx/particles/functions/ported_fire.js,
ported_snapshot.js, ported_children.js. C_OP_ExternalWindForce (0x180114d50) is a reported no-op (no world wind).

## Unread / not ported

The +0x8690 fire list and its consumer; 180d49370 (the time offset); 18021c9b0 (taken as "the networked fires
changed"); the general world-to-local branch (an inferno with angles or scale); the RandomSeed value of 180d40fd0
(18075d250); the client stream's seed; the batched-ray query object (vfn 0x5e8 / 0x10); 1809adf10's exact compare
(taken as |a - b| <= 12 per axis); C_INIT_DistanceToCPInit's LOS trace and remap bias; the water effects pass
(m_bOnlyRenderInEffectsWaterPass renderers are hidden: web/src/fx/effects.js).
