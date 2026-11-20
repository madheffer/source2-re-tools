# C_Inferno on the client: the ground fire particle

client_20261112 (`game/csgo/bin/win64/client.dll`, md5 b6f4750a...), decompiled on client_20261015 (each function found there by a masked byte signature of its 11-12 body, rel32 / rip disp32 wildcarded, one hit each; constants re-read in 11-12). server_20261105 for the server side, particles.dll 63babcbf.

## Functions

| 11-12 | 10-15 | What |
|---|---|---|
| 180d3bab0 | 180d438f0 | C_Inferno::ClientThink |
| 180d49a00 | 180d517f0 | C_Inferno::SynchronizeDrawables |
| 180d4aec0 | 180d52cb0 | the particle: create / CP0 / CP3 / update (flags) |
| 180d48c00 | 180d509f0 | the drawables' outward edge masks (+0x30) |
| 180d3eb80 | 180d46970 | wall traces, hull planes, CP10 (outline) / CP9 (climbing) snapshots |
| 180d40fd0 | 180d48dc0 | CP1 (core), CP11 (fill), CP12 (base) snapshots |
| 180d40e10 / 180d48700 / 180d48530 | 180d48c00 / 180d504f0 / 180d50320 | build + set CP1 / CP11 / CP12 |
| 180d3c280 | 180d440c0 | the remnant (molotov_groundfire_remnant) |
| 180d4f4c0 (old) | 180d4f4c0 | the bounds (m_minBounds / m_maxBounds) |
| 180d3a770 | 180d425b0 | add a hull plane |
| 180d3d9c0 | 180d45800 | ramp(a, b, c) = a - b / c when a x c > b, else 0 |
| 180d4b730 | | vfn 0x7c8: the effect name |
| 180d391c0 | | constructor (+0x866c = 30, +0x8670 = 80); each drawable 180d39370 zeroes +0xc0, +0x190, +0x194 |

Other addresses (11-12):

| Address | Module | What |
|---|---|---|
| 18021c9b0 | client | network data changed (taken as "the networked fires changed") |
| 18189c530 | client | stop a system (sys, 0, 0, 1, 1) |
| 1809adf10 | client | within 12 u per axis (taken as \|a - b\| <= 12) |
| 181893de0 | client | create a system (mgr, 0, name, origin, -1, seed) |
| 181894fc0 / 181894fb0 | client | set CP0 / CP3 |
| 180d49370 | client | set the system's time back (sys, now - tickBegin x interval) |
| 18015c580 | client | zero-angle world-to-local branch |
| 180d45820 | client | sincos(360 / 15 x k), z 0 |
| 180d4fd30 | client | clear planes |
| 180b722a0 | client | the ray filter (CTraceFilter) |
| 180d40df0 / 180d4de50 | client | cell grid clear / test-and-set |
| 18075d250 | client | 180d40fd0's RandomSeed value |
| 1809d4ec0 | client | create the remnant |
| 180a12420 | client | set a snapshot on a system |
| 0x18015efc0 | client | tier0 RandomInt (RandomFloat beside it) |
| 1800f7b10 / 1800f7690 / 1800f6ac0 | client | register inferno_ct_experiment / inferno_batched_rays / Inferno_concav_plane_threshold |
| 180345dc0 | server | CreateFire (server_20261105; the current build's 180342950) |
| 180350270 | server | sets m_nFireEffectTickBegin (a tick) |
| 180346090 | server | sets m_bInPostEffectTime |
| 18034ecd0 / 18034ec90 | server | m_nInfernoType 0 / 2 |

## Fields

| Offset | Field |
|---|---|
| +0x1108 | m_firePositions (Vector[64]) |
| +0x1408 | m_fireParentPositions |
| +0x1708 | m_bFireIsBurning (bool[64]) |
| +0x1748 | m_BurnNormal |
| +0x1a48 | m_fireCount |
| +0x1a4c | m_nInfernoType |
| +0x1a50 | m_nFireLifetime (float) |
| +0x1a54 | m_bInPostEffectTime |
| +0x1a58 | m_lastFireCount |
| +0x1a5c | m_nFireEffectTickBegin |
| +0x1a60 | 64 drawables of 0x1b0 |
| +0x8660 | m_drawableCount |
| +0x866c / +0x8670 | m_maxFireHalfWidth (30) / m_maxFireHeight (80) |
| +0x8674 / +0x8680 | m_minBounds / m_maxBounds |
| +0x868c | m_flLastGrassBurnThink |
| +0x8690 | list of fire positions with a time each (another consumer, unread) |
| +0x10b8 / +0x10c8 | the system's linked handle / the system |
| +0x10d8 | the remnant's index (-1 none) |
| +0x10e0 / e8 / f0 / f8 / 0x1100 | CP1 / 11 / 10 / 9 / 12 snapshots |
| sys +0x30 | \|= 4 on creation |
| `[system + 0x20]` vfn 0xa8 | SetControlPointSnapshot(cp, snapshot, 0) |
| ParticleSystemMgr +0x148 / +0x150 | snapshot create / fill (particles.dll) |
| global byte +0x58 & 2 | gates the particle |

### Drawable (0x1b0)

| Offset | Field |
|---|---|
| +0x00 | position |
| +0x0c | parent (origin + m_fireParentPositions[i]) |
| +0x18 | normal |
| +0x24 | 0 |
| +0x28 | RandomFloat(0.04, 0.06) |
| +0x2c | RandomInt(0, 100) < 50 |
| +0x2d | walls traced |
| +0x30 | 64-bit outward mask |
| +0x38 | [15] wall fraction |
| +0x74 | [15] point scale |
| +0xb0 | smallest fraction |
| +0xc0 | plane count |
| +0xd0 | [12] planes (n, d) |
| +0x190 | current plane's merge count |
| +0x194 | planes off |
| +0x1a0 | state: 0 growing, 1 burning, 2 dying, 3 out, 4 unseen during a sync |
| +0x1a4 | state's start time |
| +0x1a8 / +0x1ac | size / target size |

Random draws: the client's global stream (CUniformRandomStreamImpl<CAtomicMutex> 0x182230098).

## Constants

| Value | What |
|---|---|
| inferno_ct_experiment | bool, default 1 |
| inferno_batched_rays | bool, default 1: rays batched through the physics query's vfn 0x5e8 (same rays) |
| Inferno_concav_plane_threshold | float, default -10 |
| 0x85ebca6b, 0xc2b2ae35 | murmur3 finalizer (seed of m_nFireEffectTickBegin; 0 stays 0) |
| 0.04 (0x182231a20 x4) | plane merge tolerance per component |
| 1/30 = 0x3d088889 | cell size 30 |
| filter: interacts 0xc3001, group 3, flags 0x49, detail layers 0xffff, object sets 0xf | the wall rays |
| RandomFloat(70, 90) / (50, 70) | target size, m_nInfernoType 0 / else |
| 60 / 40 / 30 / 12 / 10 / 5 | max(60, size) radius, outline lift, ray offsets, sync match, ramp b's |

## Server side (CreateFire)

m_firePositions[i] = fire position (world), m_fireParentPositions[i] = the parent fire's position (its own with none), m_BurnNormal[i] = ground normal, m_bFireIsBurning[i] = 1, m_nFireLifetime = vfn 0x898 (flame lifetime), m_fireCount + 1. The client adds the origin to the parent position anyway.

## ClientThink (180d3bab0)

1. Until m_bInPostEffectTime: flags = 1 when m_fireCount != m_lastFireCount or the network data changed (18021c9b0); SynchronizeDrawables (flags |= its result); m_lastFireCount = m_fireCount.
2. Each drawable: growing: +0x2d = 0, `size = (curtime - t0) x target x 0.5`, burning at target (t0 = curtime); a size change: flags |= 1. Dying: flags |= 1, `size = target - target x 0.5 x (curtime - t0)`; at <= 0 out (t0, bounds).
3. The bounds again when the data changed and no drawable went out this think. Then 180d4aec0(flags).
4. Post-effect time: the remnant once (+0x10d8 == -1), the system stopped and its handle let go (the manager plays it out).

## SynchronizeDrawables (180d49a00)

1. Burning drawables -> 4.
2. Each fire i < m_fireCount: the first drawable within 12 u per axis takes the fire's exact position. Not burning: that drawable out (state 3, bounds; result 3). Burning with a drawable: 4 -> 1. Without one (and < 64): new drawable (state 0, t0 = curtime, parent = origin + m_fireParentPositions[i], target by type; m_drawableCount + 1; result 3).
3. Drawables still 4 start dying (state 2, t0 = curtime).

## The particle (180d4aec0)

1. Only with drawables and the global byte +0x58 & 2.
2. Created once: name by 180d4b730 (m_nInfernoType 0 -> molotov_groundfire; else incendiary_groundfire when inferno_ct_experiment, else molotov_groundfire; firework_crate_ground_effect not chosen there); seed = murmur3 finalizer of m_nFireEffectTickBegin; 181893de0; CP0 = origin; CP3 = (m_nFireLifetime, m_maxFireHeight, 70). On creation the system's time is set back (180d49370) and sys+0x30 |= 4: a late client starts the fire as it is now.
3. flags & 1: edge masks (180d48c00). flags & 3: the edges (180d3eb80: CP10 and, when it has one, CP9), the cores (180d40fd0: CP1, 11, 12).
4. Tail: the remnant.

Snapshots: positions are local (pos - origin: the entity has no angles and scale 1, the 18015c580 branch; the general branch is the inverse of the entity's transform); the ops' m_nLocalSpaceCP 0 brings them back through CP0.

## Edge masks (180d48c00)

Per drawable i, per direction k of 15: the point max(60, size) out; bit k of +0x30 when drawable i is the nearest to it (Euclidean, strict <: the first of equals).

## Edges (180d3eb80)

1. Every drawable not out (all 64 slots: unused ones trace once and give nothing). Planes cleared.
2. A ray up 60 u (filter above).
3. Each direction k (24 degrees apart), when +0x2d is 0: from `(x, y, z + 30 + upFrac x 30 x blocked x upHit)` to `(x + cos x target, y + sin x target, that z + max(upFrac, 0.5) x 30 x blocked)`, blocked once any earlier direction hit.
   - Start-solid: outward mask and the rest of the fractions / scales cleared, loop ends.
   - Hit: a plane through the hit point (local) with the hit normal (180d3a770); `c = -(dir . n) x target`, `scale[k] = ramp(frac, 10, c)`, `frac[k] = ramp(frac, 5, c)`, smallest frac kept (+0xb0).
   - No hit: frac[k] = fraction, `scale[k] = 1 - 10 / max(60, size)`.
   - +0x2d set: the cached values.
4. Each outward direction: two outline points 40 u up at min(size, frac x target) along k and along (2k - 1) x 12 degrees, normals those directions, radius max(60, size) (CP10); when that distance < size a climbing point at the drawable + 40 u up, normal `normalize(cos, sin, RandomFloat(-15, 15) / max(1, distance))` (tier0's global RandomFloat, reseeded in 180d40fd0's RandomSeed), radius max(60, size) (CP9).
5. After the loop a plane still being merged is kept; +0x2d = 1.

Hull planes (180d3a770): nothing once off (+0x194) or 12 planes; the first goes in; a plane whose 2D cross with the current (`n.y x cur.x - n.x x cur.y`) is under Inferno_concav_plane_threshold drops them all (count 0, off); within 0.04 of the current in every component merges (`cur + count x new`, renormalised by the xyz length with rsqrtps + a Newton step; count + 1); else the next slot.

## Cores (180d40fd0)

1. Drawables last to first (index > 63 stops), each with its own CUniformRandomStreamImpl seeded with its index.
2. Two 30-unit cell grids (180d40df0: 32 x 4 words; 180d4de50: word `(floor(z / 30) & 3) x 32 + (floor(y / 30) & 31)`, bit `floor(x / 30) & 31`, true when newly set).
3. N = normalize(local - local(parent)). "Open" = no wall fraction < 1.
4. Each direction k: `r = sqrt(RandomFloatExp(0.1, 0.65, 0.9)) x lim`, `lim = min(max(60, size), scale[k] x target)`, point = local + dir_k x r; near = smallest plane distance (`n.p + d`, FLT_MAX with none).
   - Out drawable: zero entry to CP11.
   - near <= 10, or the cell taken in the first grid and `(y x 0.71 - x x 0.7, y x 0.72 + x x 0.715, z + 35)` taken in the second: zero entry to CP11 (and CP12 when not open).
   - Else (point, N, radius max(60, size), alpha scale[k], scratch min(near, lim - r)) to CP11 and, when not open, CP12.
5. An open drawable then gives CP12 its centre (N, max(60, size), alpha 1, scratch max(60, size)) and 14 zero entries.
6. CP1: one entry a drawable: (centre, normal = the centre (C_OP_SetFromCPSnapshot writes it to the previous position), radius max(60, size), scratch +0xb0); zeros for an out drawable.

Descriptors: CP1 (180d40e10) slots 0, 2, 10, 14 (position, normal, radius, scratch); CP11 / CP12 (180d48700 / 180d48530) also slot 12 (alpha).

## Remnant (180d3c280)

With the system: reads its CP1 / 9 / 11 snapshots (vfn 0xd8); with all three: creates `particles/inferno_fx/molotov_groundfire_remnant.vpcf` (1809d4ec0), CP0 = the system's CP0 transform (vfn 0xc0 / 0xc8 -> a matrix), CP3 = (m_nFireLifetime, m_maxFireHeight, 70), the three snapshots set (180a12420), started (vfn 0x18). From ClientThink's post-effect branch and 180d4aec0's tail.

## Particle classes the tree uses (particles.dll 63babcbf)

| Address | Class |
|---|---|
| 0x1801ff7c0 | C_OP_SetFromCPSnapshot Operate |
| 0x18013cc50 | C_INIT_VelocityFromNormal |
| 0x1801432f0 | C_INIT_Orient2DRelToCP |
| 0x1801537a0 | C_INIT_DistanceToCPInit |
| 0x180166890 | C_INIT_SetAttributeToScalarExpression |
| 0x1801d35a0 | C_OP_RadiusDecay |
| 0x1801d6ad0 | C_OP_Spin (C_OP_SpinYaw: on yaw) |
| 0x18010a207 | C_OP_MaintainEmitter's snapshot count: the CP's snapshot +0x9e0 replaces m_nParticlesToMaintain |
| 0x180114d50 | C_OP_ExternalWindForce |

## Unread

- The +0x8690 fire list and its consumer.
- 180d49370 (the time offset); 18021c9b0's meaning.
- The general world-to-local branch (an inferno with angles or scale).
- 180d40fd0's RandomSeed value (18075d250); the client stream's seed.
- The batched-ray query object (vfn 0x5e8 / 0x10).
- 1809adf10's exact compare.
- C_INIT_DistanceToCPInit's LOS trace and remap bias.
- The water effects pass (m_bOnlyRenderInEffectsWaterPass renderers).
