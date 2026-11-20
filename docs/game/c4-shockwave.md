# The C4's blast: CS2's baked shockwave and the RadiusDamage fallback

server_20261105, tier0_20260923 (checked natively against tier0_20261103). The rest of the bomb: [c4.md](c4.md).
Explode 180a1d460 takes the shockwave when the map bomb damage system has entries (180a447f0), else RadiusDamage.

## Functions

| Address | Module | What |
|---|---|---|
| 180a1d460 | server | CPlantedC4 Explode |
| 180a447f0 | server | the map bomb damage system (has entries / its bounds) |
| 180a508c0 | server | CMapBombDamageGameSystem load callback |
| 180a3dc60 | server | the table object's constructor |
| 180a3c1e0 | server | murmur2 over the three ints, seed 0xea711bd8 |
| 180a3c670 | server | find a position's record |
| 180a4fed0 | server | (tree + 0x20, 0x100, 0x40000, 0): the tree's block vector |
| 180180730 | tier0 | CVertexKDTree::BuildMidpoint |
| 18017feb0 | tier0 | BuildNode(start, count) |
| 18017fc30 | tier0 | the range's bounds (from the first vertex) |
| 18017ebf0 | tier0 | the partition |
| 18017fbd0 | tier0 | Nearest -> 180180020 NearestInternal |
| 180a40c40 / 180a01cc0 | server | the lookup |
| 180a3e870 | server | box holds the origin (inclusive) |
| 18017b8d0 | server | clamp |
| 180a4d830 | server | RemapVal |
| 1809efda0 | server | cvttss2si then max 0, min 255 |
| 1801ab860 / 181470980 | server | AngleVectors (V_sincosf) |
| 180ad26d0 | server | movetype (9 ladder) |
| 1809692b0 | server | line trace (interacts-with 1, group 3, flags 0x49) |
| 1802c35a0 | server | DidHit |
| 180ae58f0 | server | (svc, dist, &z): hull traced down |
| 180ab55b0 | server | CTraceFilterPlayerMovementCS constructor (vtable 0x181923f18) |
| 180cb7b90 | server | GetViewVectors |
| 180b5d1b0 | server | observer |
| 180c2f3c0 | server | TraceShape |
| 18015a2f0 | server | CBaseEntity WorldSpaceCenter (vfn 0x2c8; CCSPlayerPawn too) |
| 1801542c0 | server | CBaseEntity vfn 0x570 IsWorld: return 0 |
| 180cb1d50 | server | CWorld IsWorld: return 1 (no other user) |
| 18146c2c0 | server | Bias |
| 1809f59e0 | server | truncate and clamp to a byte |
| 180a00190 | server | Explode's list |
| 1809fed40 | server | C4Think's tick |
| 1809f72d0 | server | the hit |
| 1816b6d80 | server | dynamic_cast (to .?AVCInferno@@ 0x181ec18c0) |
| 1809f2a40 | server | list insert by distance from the bomb |
| 180a00540 | server | r = 3000 t |
| 1809f5770 | server | the wave's end ([bomb origin, &r^2]) |
| 180347920 | server | CInferno put out (the bomb's origin) |
| 1814738b0 | server | VectorNormalize |
| 180a3f3d0 | server | aim punch add (the flinch's) |
| 180fba3a0 | server | CTakeDamageInfo (info, the bomb, owner, 0, dmg, DMG_BLAST 0x40, 0) |
| 1809299d0 | server | the bomb's owner |
| 1803ed610 | server | TakeDamageOld |
| 180a89230 | server | the team rule ([c4.md](c4.md)) |
| 180a88f30 | server | armor step |
| 180cb56b0 | server | time at fire+0x68 |
| 18017e2d0 | server | f32 compare |
| 18017ca70 | server | write -1 |
| 1814722c0 | server | VectorAngles |
| 180c4f310 | server | particle (everyone) |
| 1809fbf00 | server | the explosion's effects |
| 1809ff5a0 | server | Detonate |
| 180250e50 | server | UTIL_TraceLine |
| 1803ea3b0 | server | SetAbsOrigin |
| 180c83dd0 / 180c84870 / 180c8a6e0 | server | all-players filter |
| 180cbbf60 | server | UTIL_DecalTrace -> 1803d10a0 -> 18111bfe0 |
| 180f697b0 | server | emit sound |
| 180febc70 | server | UTIL_ScreenShake |
| 180c86b40 | server | pawn handle walk |
| 180c84490 | server | controller connected (+0x514 0 or 3) |
| 1801542b0 | server | vfn 0x460: false on CBaseEntity and the pawn |
| 180fc5870 | server | ComputeShakeAmplitude(origin, center, amplitude, radius) |
| 180a7ab50 | server | weapon behind the inflictor (none for the planted C4) |
| 181026b50 | server | item system (vfn 0x148 by name) |
| 180e83b50 | server | CCSGameRules vfn 0x110: `return 1` |
| 1809550b0 | server | RadiusDamage |
| 1800aec50 | server | CPhysicsPropMultiplayer class registration |

## Fields

| Offset | Field |
|---|---|
| tree +0x38 | the KD tree; +0x20 its block vector |
| table +0x90 / +0x9c | vertex bounds mins / maxs |
| CGameTrace +0x8 / +0x84 / +0x8c / +0x90 / +0xac / +0xbb | entity / end / end z / normal / fraction / start solid |
| filter +0x8 / +0x10 / +0x18 / +0x20 / +0x38 / +0x39 / +0x40 | interacts-with / -exclude / -as / ignored / group / flags / iterate entities |
| svc +0x408 | ducked |
| view vectors +0x48 / +0x54, +0x24 / +0x30, +0xc / +0x18 | observer, ducked, standing hull |
| entity +0x2e0 | m_bTakesDamage |
| class info +0x60 -> +0x18 | base chain |
| pawn +0xe50 | aim punch services |
| pawn +0x388 | m_fFlags |
| info +0x70 | flags (0x40000: bit 18, no armor) |
| inferno +0x1190 / +0x11a8 | fire count / pointers |
| fire +0x24 / +0x68 / +0x74 / +0x78 | live byte / time / end / 1.0 when put out |
| hegrenade vdata +0x828 | m_flArmorRatio (1.2) |
| item system +0x34 | change counter (the cache) |
| controller +0x514 | connected state |

## Constants

| Value | What |
|---|---|
| 0x181e14bf8 | the static table object |
| 32 | site box growth each side |
| 2^18 (shift 18, mask 0x3ffff) | block vector pages |
| 8 | KD leaf size |
| 0xff | leaf axis |
| 1800 (inline 0x44e10000), 100 (0x18178fe18), 255 (0x181784e18), 360 (0x18179beac) | lookup |
| 2 x 16384 x 1.7320508 | hull trace length |
| 0x40000 (+0x18), group 11, flags 0x4b, exclude |= 0x48100 | movement filter |
| origin + (0, 0, 36), ducked + (0, 0, 27) | a pawn's WorldSpaceCenter |
| 0.45 (0x1817c98cc) | ducked Bias |
| -1 (0x181784e30), 0.5 (0x18178057c), 1 (0x181780580) | facing f |
| 0.53 (0x181911d20), 0.06 (0x181911d1c) | facing Bias |
| 0x181fa8d68 | CInferno's class (list) |
| 0x182125650 | CPhysicsPropMultiplayer (prop_physics_multiplayer): at most 4 a tick |
| 3000, 0.2, 10 s | wave speed, hear lead, the think's span |
| 1e-17 / 1e17 | normalize bounds |
| -10, 10 | aim punch |
| 50, 100 | force scale, force offset |
| 0x40 | DMG_BLAST |
| 0.6 | SetAbsOrigin normal offset |
| 8, 40 | Detonate's trace start + 8, length 40 |
| 0xc3001, group 4, flags 0x49 | Detonate's trace |
| 0x181ff32e0 | decal system |
| 150 (0x43160000) | shake frequency |
| 25 (0x41c80000), 1 s, 3000 (0x453b8000) | shake without baked damage: amplitude, duration, radius |
| 3 (0x40400000), 0.5 s (0x3f000000), 10000 (0x461c4000) | shake with baked damage |
| 16 | shake amplitude cap |
| 0x58 bytes | shake message (command, amplitude, frequency, duration); 0x1821b9498 vfn 0x78 |
| 1.2 x 0.5 = 0.6000000238 (f32) | RadiusDamage C4 armor ratio; bonus 1.0 |
| 500, 3.5 R | RadiusDamage fallback |

## The file (maps/<map>/baked_bomb_damage.vdata, CS2_BOMB_DAMAGE_DATA)

KV3 vdata: `header.version` (1; the loader takes 1..2) and `data` with three blobs (de_dust2: 2 sites, 85697 vertices):

- `bombsites`: 7 f32 a site (0x1c): box mins, maxs, `bomb_damage_power` (func_bomb_target's keyvalue: de_dust2 A 1929, B 3234).
  The loader grows each box by 32 each side (mins - 32, maxs + 32, f32).
- `positions`: 3 i16 a vertex (x, y, z), walkable-surface samples.
- `damage_values`: 4 bytes a vertex a site, **site-major** (value i is vertex i % N's for site i / N): u16 value, u8 yaw
  byte, u8 pitch byte. The loader checks size(values) / 4 == sites x vertices.

## Load (180a508c0)

1. Sites copied and grown.
2. Each vertex's f32 position into a hash map keyed by position (180a3c1e0), each record sized to the site count; the vertex bounds.
3. BuildMidpoint(tree +0x38, positions, N, stride 3) after a BuildMidpoint(null, 0, 0).
4. Every value to its position's record (180a3c670) at its site: **the last vertex at a position wins**.
5. Logs "Unpacked damage data for %d bomb sites (%d values)".

## CVertexKDTree (tier0)

- BuildMidpoint: a vector of vertex pointers in index order, then BuildNode(start, count).
- BuildNode: count > 8: bounds (18017fc30); axis of the largest extent `ex < ey ? (ey <= ez ? z : y) : (ez < ex ? x : z)`;
  `split = (lo + hi) * 0.5` (f32); partition. Both sides non-empty -> inner node (axis, split, children [start, m)
  first, [m, end) second), else (and count <= 8) a leaf (axis 0xff, start, count). Nodes 16 bytes {a, b, axis, split};
  the node index is taken before the children's.
- Partition (18017ebf0): `m = start + count / 2`; for i in [m, end): v[i][axis] < split -> swap(v[i], v[m]), m++; then
  j = m - 1, for i from m - 1 down to start: split <= v[i][axis] -> swap(v[j], v[i]), m--, j--; returns m.
- NearestInternal: best = FLT_MAX; a leaf's vertices in order, `d = ((dy dy) + dx dx) + dz dz` (disassembly), taken when
  **d < best** (strict: the first of equal ones stays); inner: q[axis] < split -> first child, else second; then the
  other unless `best <= (q[axis] - split)^2`.

## The lookup (180a40c40 / 180a01cc0)

1. The first site whose grown box holds the bomb's origin (180a3e870); **none: no damage at all**.
2. Nearest vertex to the point (WorldSpaceCenter, vfn 0x2c8); its record's site entry.
3. **`damage = trunc_clamp(RemapVal(v, power, power + clamp(v, 0, 1800), 100, 0), 0, 255)`**; RemapVal
   `(val - a)(d - c) / (b - a) + c`, equal ends: d when val - b >= 0 else c. So v <= 1800: `100 * power / v`; past
   1800: `100 - 100 (v - power) / 1800` (continuous at 1800); **v = 0 gives 100** (equal ends), small v up to 255.
4. **dir** = `AngleVectors(QAngle((b3 / 255) * 360, (b2 / 255) * 360, 0))`.
5. Retry: a player alive, with movement services, not on a ladder (180ad26d0: 9), with no ground entity (vfn 0x660) or
   one whose vfn 0x570 (IsWorld) is false, and the line centre -> found vertex blocked (1809692b0, 1802c35a0): the hull
   traced down (180ae58f0) gives `(centre.x, centre.y, (centre.z - origin.z) + floor z)` and the lookup runs again
   (its results replace the first's when it succeeds). IsWorld is true only on CWorld: a player on a door, a prop or
   a train takes the retry as an airborne one does.
6. Below 100, a player: ducked (m_bDucked) `100 Bias(dmg / 100, 0.45)`; then
   `f = clamp((((dir.z fwd.z) + dir.y fwd.y) + dir.x fwd.x - (-1)) * 0.5, 0, 1)` (fwd = AngleVectors of the eye
   angles, vfn 0x5f0), `100 Bias(dmg / 100, 0.53 - f * 0.06)`; 1809f59e0 to a byte. Crouching and facing away take less.
7. Bias (18146c2c0): `x = 0 > x ? 0 : min(1, x)`; `b = FLT_MIN > b ? FLT_MIN : min(1, b)`; `x / ((1 / b - 2)(1 - x) + 1)`.

RemapVal, the clamp, the byte and Bias (and the player steps composed from them) checked natively (move_oracle --bombmath).

## The hull trace down (180ae58f0)

- start = abs origin, end = `start - (dist * 0, dist * 0, dist)` (f32).
- CTraceFilterPlayerMovementCS (180ab55b0): interacts-with the pawn's solid mask (vfn 0xb88) at +0x8, interacts-as
  0x40000, group 11, flags 0x4b, the pawn ignored, +0x40 = 1; then interacts-exclude |= 0x48100 (the player layer
  0x40000 among them: no pawn is hit).
- Hull from GetViewVectors: observer +0x48 / +0x54, ducked (svc+0x408) +0x24 / +0x30, else +0xc / +0x18; TraceShape;
  *z = end z (+0x8c); returns DidHit.
- WorldSpaceCenter: CollisionToWorld((mins + maxs) * 0.5) ([use.md](use.md)), the abs origin without a collision property.

## The wave (180a00190, 1809fed40, 1809f72d0)

1. The list at the explosion: entities that aren't vfn 0x570 / 0x560 and are players, have +0x2e0, or are (or derive
   from) CInferno (0x181fa8d68); inserted by distance from the bomb (1809f2a40).
2. Each think (every tick after the explosion, up to 10 s): `t = (now - m_flC4Blow) - 1`; `r = 3000 t`; `r' = 3000 (t + 0.2)`.
3. Walked from the list's end: a player not yet in the hit set whose centre's `((dy dy) + dx dx) + dz dz` < r'^2 hears
   **c4.shockwave.hit** (a filter of that player alone) and joins the set; d2 <= r^2 and (a player or no move parent):
   the hit, the entity leaves the list.
4. CPhysicsPropMultiplayer cap: a counter from 0 each tick (1809fee06), incremented on an entity due a hit of that
   class (or derived); past 4 (`cmp ebx, 4; jg`) skipped and kept in the list: **at most 4 a tick**. RadiusDamage
   tests the same class.
5. The end (1809f5770): the table's bounds (+0x90 / +0x9c) all inside the wave (each of the 8 corners'
   `((y y) + x x) + z z` <= r^2): no next think (else SetNextThink now); no table: false. The list emptying doesn't end it.

## The hit (1809f72d0)

1. Not a player (vfn 0x558) and no +0x2e0: a CInferno is put out (180347920), anything else nothing.
2. Else the lookup (no result: nothing); a player: none while observing (180b5d1b0) or dead (vfn 0x550).
3. Line from the eye (vfn 0x5e8) to the bomb (1809692b0(.., 0, 1), DidHit) clear:
   `dir = (centre - bomb) * (1 / sqrt(((z z) + y y) + x x))` (length < 1e-17 or > 1e17: VectorNormalize 1814738b0, 0 for 0).
4. A live pawn (vfn 0x558 and 0xca8): aim punch (+0xe50) gets `(-10 - clamp((dmg - 0) / 100, 0, 1) * 10, 0, 0)` (180a3f3d0).
5. A non-player takes at least 1. Damage (when not 0): 180fba3a0(info, bomb, 1809299d0, 0, dmg, 0x40, 0), force
   `(dir * dmg) * 50` at `centre - dir * 100`, **info+0x70 |= 0x40000**, 1803ed610; the team rule 180a89230.
6. 0x40000 is bit 18, which the armor step 180a88f30 tests (`info+0x70 >> 0x12 & 1`): **the shockwave takes no armor**.
   The force moves only a ragdoll ([shots.md](shots.md)).

## Infernos put out (180347920)

For each fire (+0x1190, +0x11a8) with +0x24 set and its timer test (180cb56b0 at +0x68 against +0x74, 18017e2d0)
negative (current time before its end): +0x74 = -1 (18017ca70), +0x78 = 1.0 (each through its network-change notifier),
`dir = normalize(fire origin - bomb)`, particles/inferno_fx/extinguish_fire.vpcf at the fire's origin, angles
VectorAngles(dir) (1814722c0; 180c4f310, everyone).

## The explosion's effects (1809fbf00)

Explode's first step after the win check and the BombExplode output. Its argument is Detonate 1809ff5a0's trace
(180250e50: start origin + (0, 0, 8), end `(origin.x + 0, origin.y + 0, (origin.z + 8) - 40)`, 0xc3001, group 4, flags
0x49, the bomb ignored, +0x40 = 0).

1. fraction != 1: SetAbsOrigin 1803ea3b0(`normal * 0.6 + end`) (each axis `(n * 0.6) + e`, f32). Everything after
   (particle, sound, shake, RadiusDamage's origin, the shockwave's list and lookups) uses the moved origin.
2. particles/explosions_fx/explosion_c4_500.vpcf (180c4f310) at origin + (0, 0, 8) (each axis + 0), angles 0, to everyone.
3. UTIL_DecalTrace 180cbbf60(trace, "Scorch", 0): fraction != 1 and a hit entity (the world) -> the decal system with
   the trace and its end (+0x84) to all players. Decal group "Scorch" (scripts/decalgroups.vdata: one option,
   materials/decals/scorch1_projected_triplanar.vmat, weight 1); the client's record: [decals.md](decals.md).
4. Sound at the origin to everyone (180f697b0, volume 1.0): **c4.explode** when the table is empty (180a447f0),
   **c4.shockwave.boom** when it has entries.
5. UTIL_ScreenShake 180febc70(origin, amplitude, 150, duration, radius, SHAKE_START 0, air false, no filter): amplitude
   capped at 16; the pawns of 180c86b40 (every player pawn, dead ones too with their flags as they died, whose
   controller is connected, 180c84490); a pawn takes it only when air (param 7), a non-start command, its m_fFlags
   FL_ONGROUND or its vfn 0x460 say so.
6. ComputeShakeAmplitude 180fc5870: radius <= 0 -> amplitude; `d = sqrt(((dz dz) + dy dy) + dx dx)` (f32, centre - pawn);
   d <= radius: `(1 - d / radius) * amplitude`, else -1 (skipped); 0 is skipped for a start. E.g. `(1 - d / 10000) * 3`.

Then Explode hides the bomb (vfn 0x1b0(0)) and takes RadiusDamage or the shockwave.

## Armor for the C4 (180a88f30; [shots.md](shots.md) "Armor")

- The shockwave: none (bit 18).
- RadiusDamage: DMG_BLAST; 180a7ab50 finds no weapon behind the planted C4, and for a blast with any of its three
  results null 180a88f30 takes weapon_hegrenade's vdata (181026b50, vfn 0x148 by name, cached by +0x34): ratio =
  m_flArmorRatio (+0x828, 1.2) x 0.5. Bonus for any DMG_BLAST **1.0** (180e83b50).

## The fallback: RadiusDamage

R = info_map_parameters' `bombradius` (m_flBombRadius), 500 without one; RadiusDamage (1809550b0) with radius 3.5 R and
damage R, DMG_BLAST, from the bomb's origin; the team rule as above. The planter is not spared.

## Unread

- An inferno's centre (CInferno's own WorldSpaceCenter: its collision bounds); what +0x74 = -1 / +0x78 = 1 do to the fire.
- The client's handler of the shake message.
- How client.dll projects the Scorch's record ([decals.md](decals.md)).
- The round end's round_end_via_bombing post effect (client).
- server.dll's wave not checked natively.
