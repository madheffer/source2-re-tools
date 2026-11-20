# The C4's blast: CS2's baked shockwave and the RadiusDamage fallback

server_20261105.dll / tier0 (2026-11-15). The rest of the bomb is in [c4.md](c4.md). **Ported**: maps that ship CS2's
baked bomb damage take the shockwave (web/server/cs2web/modes/team/bomb/c4-shockwave.js over sim/src/game/bomb_damage.rs); the others take
RadiusDamage (planted-c4.js `detonate`), as Explode 180a1d460 chooses (the map bomb damage system has entries:
180a447f0).

## The file (maps/<map>/baked_bomb_damage.vdata, CS2_BOMB_DAMAGE_DATA)

A KV3 vdata: `header.version` (1; the loader takes 1..2) and `data` with three blobs (de_dust2: 2 sites, 85697
vertices; `lasers-bake --bomb-damage <map.vpk> <maps/<name>> [--dump]`, bake/BombDamageBake.cs, writes them unchanged
into **bomb_damage.bin**: "ZBD1", u32 sites, u32 vertices, then the blobs):

- `bombsites`: 7 f32 a site (0x1c): the site's box mins, maxs and its `bomb_damage_power` (the func_bomb_target's
  keyvalue: de_dust2 A 1929, B 3234). The loader grows each box by 32 on every side (mins - 32, maxs + 32, f32).
- `positions`: 3 i16 a vertex (x, y, z), walkable-surface samples.
- `damage_values`: 4 bytes a vertex a site, **site-major** (value i is vertex i % N's for site i / N): u16 value, u8
  yaw byte, u8 pitch byte. The loader checks size(values) / 4 == sites x vertices.

**The load callback 180a508c0** (CMapBombDamageGameSystem; the table object is static 0x181e14bf8, its constructor
180a3dc60): the sites copied and grown; each vertex's position as f32 inserted into a hash map keyed by the position
(murmur2 over the three ints, seed 0xea711bd8: 180a3c1e0), each record sized to the site count; the vertex bounds;
CVertexKDTree::BuildMidpoint(tree +0x38, positions, N, stride 3) after a BuildMidpoint(null, 0, 0); then every value to
its position's record (180a3c670 finds it) at its site: **the last vertex at a position wins**. Logs "Unpacked damage
data for %d bomb sites (%d values)". The tree's block vector is set up by 180a4fed0(tree + 0x20, 0x100, 0x40000, 0):
pages of 2^18 entries (shift 18, mask 0x3ffff).

## CVertexKDTree (tier0 exports; read in tier0_20260923, checked natively against tier0_20261103)

- **BuildMidpoint 180180730** fills a vector of vertex pointers in index order, then **BuildNode 18017feb0**(start,
  count): count > 8: the range's bounds (18017fc30, from the first vertex); the axis of the largest extent
  (ex < ey ? (ey <= ez ? z : y) : (ez < ex ? x : z)); split = (lo + hi) x 0.5 (f32); **the partition 18017ebf0**: m =
  start + count / 2; for i in [m, end): v[i][axis] < split → swap(v[i], v[m]), m++; then j = m - 1, for i from m - 1 down
  to start: split <= v[i][axis] → swap(v[j], v[i]), m--, j--; returns m. Both sides non-empty → an inner node (axis,
  split, children: [start, m) first, [m, end) second), else (and count <= 8) a leaf (axis 0xff, start, count). Node
  records are 16 bytes {a, b, axis, split}; the node index is taken before the children's.
- **Nearest 18017fbd0 -> NearestInternal 180180020**: best = FLT_MAX; a leaf's vertices in order, d = ((dy dy) + dx dx)
  + dz dz (disassembly), taken when **d < best** (strict: the first of equal ones stays); an inner node: q[axis] <
  split → the first child, else the second; then the other child unless best <= (q[axis] - split)^2.

## The lookup 180a40c40 / 180a01cc0

- The first site whose grown box holds the bomb's origin (inclusive, 180a3e870); **none: no damage at all**.
- The nearest vertex to the point (an entity's WorldSpaceCenter, vfn 0x2c8), its record's site entry.
- **damage = trunc_clamp(RemapVal(v, power, power + clamp(v, 0, 1800), 100, 0), 0, 255)** (18017b8d0 the clamp,
  180a4d830 RemapVal (val - a)(d - c) / (b - a) + c, equal ends: d when val - b >= 0 else c; 1809efda0: cvttss2si then
  max 0, min 255). So for v <= 1800 it is 100 x power / v, past 1800 100 - 100 (v - power) / 1800 (continuous at 1800);
  **v = 0 (the vertex at the bomb) gives 100** (the equal ends), small v up to 255.
- **dir** = AngleVectors(QAngle((b3 / 255) x 360, (b2 / 255) x 360, 0)) (1801ab860, 181470980: the sim's
  angle_vectors forward, the same V_sincosf). Constants read: 1800 (inline 0x44e10000), 100 (0x18178fe18), 255
  (0x181784e18), 360 (0x18179beac).
- A player alive, with movement services, not on a ladder (180ad26d0: movetype 9) and with no ground entity (vfn
  0x660) or one whose **vfn 0x570 (IsWorld)** is false: when the line from the centre to the found vertex is blocked
  (1809692b0: interacts-with 1, group 3, flags 0x49; DidHit 1802c35a0), the pawn's hull traced down 2 x 16384 x
  1.7320508 from its origin (180ae58f0, below) gives the point (centre.x, centre.y, (centre.z - origin.z) + floor z) and
  the lookup runs again (its results replace the first's when it succeeds). vfn 0x570 is CBaseEntity's 1801542c0
  (return 0) on every class but CWorld (180cb1d50, return 1: tools/re/game/vtowner.py finds no other user), so a player
  standing on a door, a prop or a train takes the retry as an airborne one does.
- **180ae58f0** (svc, dist, &z): start = the pawn's abs origin, end = start - (dist x 0, dist x 0, dist) (f32);
  CTraceFilterPlayerMovementCS (180ab55b0: vtable 0x181923f18, interacts-with the pawn's solid mask vfn 0xb88 at
  filter +0x8, interacts-as 0x40000 (+0x18), group 11 (+0x38), flags 0x4b (+0x39), the pawn ignored (+0x20), +0x40 = 1:
  iterating entities) then **interacts-exclude (+0x10) |= 0x48100** (the player layer 0x40000 among them: no pawn is
  hit); the hull from GetViewVectors (180cb7b90): 180b5d1b0 (observer) +0x48 / +0x54, ducked (svc+0x408) +0x24 / +0x30,
  else +0xc / +0x18; TraceShape 180c2f3c0; *z = the trace's end z (+0x8c); returns DidHit.
- **WorldSpaceCenter** (vfn 0x2c8) is CBaseEntity's 18015a2f0 on CCSPlayerPawn too (tools/re/game/vslot.py): CollisionToWorld
  ((mins + maxs) x 0.5) (use.md), the abs origin without a collision property. A pawn's box is its hull's, axis-aligned:
  origin + (0, 0, 36), ducked + (0, 0, 27).
- **Below 100, a player**: ducked (m_bDucked) **100 Bias(dmg / 100, 0.45)** (0x1817c98cc); then f = clamp((((dir.z
  fwd.z) + dir.y fwd.y) + dir.x fwd.x - (-1)) x 0.5, 0, 1) (fwd = AngleVectors of the eye angles, vfn 0x5f0; -1
  0x181784e30, 0.5 0x18178057c, 1 0x181780580), **100 Bias(dmg / 100, 0.53 - f x 0.06)** (0.53 0x181911d20, 0.06
  0x181911d1c). Bias 18146c2c0: x = 0 > x ? 0 : min(1, x); b = FLT_MIN > b ? FLT_MIN : min(1, b); x / ((1 / b - 2)(1 -
  x) + 1); 1809f59e0 truncates and clamps it to a byte. Crouching and facing away take less.

## The wave (Explode's list 180a00190, C4Think's tick 1809fed40, the hit 1809f72d0)

- The list at the explosion: entities that aren't vfn 0x570 / 0x560 and are players, have m_bTakesDamage (+0x2e0) or
  are of the class at 0x181fa8d68 (or derive from it: the class info's +0x60 -> +0x18 base chain) — **CInferno** (the
  hit's dynamic_cast 1816b6d80 to .?AVCInferno@@, 0x181ec18c0); inserted by distance from the bomb (1809f2a40).
- Each think (every tick after the explosion): t = (now - m_flC4Blow) - 1; up to 10 s; **r = 3000 t** (180a00540),
  r' = 3000 (t + 0.2). Walked from the list's end: a player not yet in the hit set whose centre's squared distance
  (((dy dy) + dx dx) + dz dz) is below r'^2 hears **c4.shockwave.hit** (a filter of that player alone) and joins the
  set; d2 <= r^2 and (a player or no move parent): the hit, the entity leaves the list (the class 0x182125650 at most 5
  a tick). The list empty (1809f5770): done.
- **The hit 1809f72d0**: not a player (vfn 0x558) and no m_bTakesDamage (+0x2e0): a CInferno is put out (180347920,
  below), anything else nothing. Else the lookup above (no result: nothing); a player: none while observing
  (180b5d1b0) or dead (vfn 0x550); the line from the eye (vfn 0x5e8) to the bomb (1809692b0(.., 0, 1), DidHit) clear:
  dir = (centre - bomb) x (1 / sqrt(((z z) + y y) + x x)) (a length < 1e-17 or > 1e17: VectorNormalize 1814738b0, 0 for
  0); a live pawn (vfn 0x558 and 0xca8): the aim punch services (+0xe50) get (-10 - clamp((dmg - 0) / 100, 0, 1) x 10,
  0, 0) (180a3f3d0, the flinch's add: src/cs2web/sim/aim-punch.js flinchPunch); a non-player takes at least 1; the damage (when
  not 0): CTakeDamageInfo 180fba3a0(info, the bomb, its owner 1809299d0, 0, dmg, DMG_BLAST 0x40, 0), force (dir x dmg)
  x 50 at centre - dir x 100, **info+0x70 |= 0x40000**, TakeDamageOld 1803ed610; the team rule 180a89230 applies
  (c4.md). **0x40000 is bit 18, which the armor step 180a88f30 tests (`info+0x70 >> 0x12 & 1`): the shockwave takes
  no armor.** The force moves only a ragdoll (shots.md: the damage force is ragdolls only on a pawn).
- **180347920** (CInferno, the bomb's origin): for each fire (count +0x1190, pointers from +0x11a8) with its +0x24 byte
  set and its timer test (180cb56b0 at fire+0x68 against fire+0x74, 18017e2d0) negative: fire+0x74 = -1 (18017ca70),
  fire+0x78 = 1.0 (each through its network-change notifier), dir = normalize(fire origin - bomb) as above, and
  particles/inferno_fx/extinguish_fire.vpcf at the fire's origin with angles VectorAngles(dir) (1814722c0; 180c4f310,
  everyone).

## The explosion's effects (1809fbf00, Explode's first step after the win check and the BombExplode output)

Detonate 1809ff5a0's trace (UTIL_TraceLine 180250e50: start origin + (0, 0, 8), end (origin.x + 0, origin.y + 0,
(origin.z + 8) - 40), interacts-with 0xc3001, group 4, flags 0x49, the bomb ignored, +0x40 = 0: no entity iteration)
is Explode's argument (the CGameTrace: end +0x84, normal +0x90, fraction +0xac, start solid +0xbb, entity +0x8).

1. fraction != 1: **SetAbsOrigin 1803ea3b0(normal x 0.6 + end)** (each axis (n x 0.6) + e, f32). Everything after —
   the particle, the sound, the shake, RadiusDamage's origin, the shockwave's list and lookups — uses the moved origin.
2. particles/explosions_fx/explosion_c4_500.vpcf (180c4f310) at origin + (0, 0, 8) (each axis + 0), angles 0, to
   everyone (the filter 180c83dd0 / 180c84870 / 180c8a6e0: all players).
3. **UTIL_DecalTrace 180cbbf60(trace, "Scorch", 0)**: fraction != 1 and a hit entity (the world here) ->
   1803d10a0 -> 18111bfe0: the decal system 0x181ff32e0 with the trace and its end (+0x84) to all players. The decal
   group "Scorch" is scripts/decalgroups.vdata's (one option: materials/decals/scorch1_projected_triplanar.vmat, weight
   1); the client's decal record: [decals.md](decals.md).
4. The sound at the origin to everyone (180f697b0, volume 1.0): **c4.explode** when the map bomb damage system is empty
   (180a447f0), **c4.shockwave.boom** when it has entries.
5. **UTIL_ScreenShake 180febc70**(origin, amplitude, frequency 150 (0x43160000), duration, radius, SHAKE_START 0, air
   false, no filter): without baked damage amplitude 25 (0x41c80000), 1 s, radius 3000 (0x453b8000); with it 3
   (0x40400000), 0.5 s (0x3f000000), 10000 (0x461c4000). It caps the amplitude at 16; walks the pawn handles
   (180c86b40, 180c84490's check); a pawn takes it only when air (param 7), a non-start command, its m_fFlags
   (+0x388) FL_ONGROUND or its vfn 0x460 (1801542b0: false on CBaseEntity and the pawn) say so; **ComputeShakeAmplitude
   180fc5870**(origin, the pawn's WorldSpaceCenter, amplitude, radius): radius <= 0 -> the amplitude; d = sqrt(((dz dz)
   + dy dy) + dx dx) (f32, subtracting centre - pawn); d <= radius: (1 - d / radius) x amplitude, else -1 (skipped); 0
   is skipped for a start. The message (0x58 bytes: command, amplitude, frequency, duration) through the network
   (0x1821b9498 vfn 0x78) to that player.

Then Explode hides the bomb (vfn 0x1b0(0)) and takes RadiusDamage or the shockwave.

## Armor for the C4 (180a88f30; shots.md "Armor")

- The shockwave: none (info+0x70 bit 18, above).
- RadiusDamage (a map without the table): DMG_BLAST; 180a7ab50 finds no weapon behind the planted C4, and for a blast
  with any of its three results null 180a88f30 **takes weapon_hegrenade's vdata** (the item system 181026b50, vfn 0x148
  by name, cached by its change counter +0x34): ratio = its m_flArmorRatio (+0x828, 1.2) x 0.5. The bonus for any
  DMG_BLAST is **1.0**: gamerules vfn 0x110 is CCSGameRules' 180e83b50, `return 1`. (sim/src/combat/damage.rs had 0.5
  for every type: HE grenades took the wrong armor split too.)

## Checked

- **rubikon/tests/KdOracle** (new): tier0_20261103's own BuildMidpoint / Nearest called natively over de_dust2's 85697
  vertices for 300000 queries (random points over the bounds and a margin, points on vertices, points halfway between
  neighbours: the ties) -> **the sim's nearest vertex is the same for all 300000** (web/src/cs2web/modes/team/bomb-damage-test.mjs
  `<bomb_damage.bin> <kdo.bin>`). Usage in its Program.cs.
- bomb-damage-test.mjs also: the table loads, lethal at and near the bomb, nothing for a bomb outside both sites, 0 at
  the T spawn side, unit directions, the scales' order (facing > away, facing > ducked), 100+ kept.
- defuse-test.mjs: on de_dust2 the shockwave runs (not RadiusDamage); the T standing on the bomb dies; a CT 1807 u away
  is hit 0.609 s after the explosion (the wave: 0.602 s) for exactly the table's 59 after the scales (hp 41).
- In the browser (wall clock): c4.shockwave.hit 404 ms after the explosion at 1807 u (r' reaches at 0.402 s), the hp
  drop at 618 ms, 59 damage.
- Not checked natively: the server.dll side (RemapVal, Bias, the byte clamp, the wave): f32 ops ported from the
  disassembly (each instruction's order above). An oracle for them would need server.dll loaded with its imports.

## Ported (2026-11-16, "c4-blast")

server/cs2web/modes/team/bomb/c4-explode.js (Detonate's trace, 1809fbf00: the origin's move, the particle and Scorch positions in the
'exploded' event, the sound by path, UTIL_ScreenShake per player); server/cs2web/modes/team/bomb/c4-pawn.js (WorldSpaceCenter, IsWorld,
180ae58f0); c4-shockwave.js (the IsWorld retry, the floor's movement filter, the 1 / length normalise, the armor flag,
the infernos); sim/src/combat/damage.rs (bit 18, the blast bonus); planted-c4.js (RadiusDamage's HE armor ratio, the
planter not spared); client: c4-view.js (the particle at + 8, the Scorch), grenades.js (extinguish_fire), world/
decals.js (the material's fade), bake/C4Bake.cs (`ze-c4/decals.json`). Checked: defuse-test.mjs (the origin + 0.6, the
particle + 8, the Scorch on the ground, c4.shockwave.boom, the CT's shake 2.4578 = (1 - d / 10000) x 3, armor 100
kept), damage.rs `armor` (the HE ratio's f32 0.6000000238, bonus 1, bit 18).

## Stand-ins (TODO(trace))

- No cap for the class 0x182125650 (unread which); the list's order (1809f2a40's key) only decides that cap here;
  1809f5770 (the list emptied) as the list empty or t > 10.
- An inferno's centre is its origin (CInferno's own WorldSpaceCenter: its collision bounds, unread); which fires
  180347920 ends (the +0x24 byte and the timer test at +0x68 / +0x74, and what +0x74 = -1 / +0x78 = 1 do to the fire)
  read only as far as above: every live flame of server/cs2web/grenades/inferno.js (itself a stand-in) put out at once.
- UTIL_ScreenShake's pawn list: the live players here (a dead player's pawn and its flags unread); the client's shake
  (web/src/app/view-shake.js) is Source's CViewEffects, not client.dll's handler of the message.
- The Scorch's projection: world/decals.js's box (DecalDepth from DecalDepthOffset along the normal) and a random turn
  about the normal; how client.dll projects the record (decals.md) is unread.
- The round end's round_end_via_bombing post effect (client).

## The fallback: RadiusDamage (a map without a table)

R = info_map_parameters' `bombradius` (m_flBombRadius), 500 without one; RadiusDamage (1809550b0, sim/src/game/radius.rs)
with radius 3.5 R and damage R, DMG_BLAST, from the bomb's origin; the team rule as above.

## Second pass (2026-11-16, "c4-pick")

- **The capped class** 0x182125650 is **CPhysicsPropMultiplayer** (prop_physics_multiplayer: its class registration
  1800aec50). The tick (1809fed40) keeps a counter from 0 each tick (1809fee06) and, on an entity due a hit (d^2 <= r^2,
  a player or no move parent) of that class or one derived from it, increments it; past 4 (`cmp ebx, 4; jg`) the
  entity is skipped and stays in the list: **at most 4 a tick**. Ported (c4-shockwave.js). RadiusDamage (1809550b0)
  tests the same class (skipped under its own condition, radius.rs).
- **The wave's end 1809f5770**([bomb origin, &r^2]) after each tick: the bomb damage table (180a447f0) bounds (+0x90 mins,
  +0x9c maxs: the vertices' bounds from the load) all inside the wave: each of the 8 corners' (((y y) + x x) + z z) at
  most r^2; then no next think (else SetNextThink now); no table: false. Ported (bomb-damage.js bounds, c4-shockwave.js
  passed). The list emptying doesn't end it.
- **The fires** (180347920): a fire counts while +0x24 is set and the current time (180cb56b0 at +0x68) is before its
  end (+0x74); put out: +0x74 = -1, +0x78 = 1.0. Here every live flame of inferno.js (its own stand-ins are its system's).
- **The shake's pawn list** 180c86b40: every player pawn (dead ones too, their flags as they died) whose controller is
  connected (180c84490: +0x514 0 or 3). Ported (c4-explode.js).
- **Checked natively** (`move_oracle --bombmath`, 0 differences in 200,000): RemapVal 180a4d830, the clamp 18017b8d0,
  the byte 1809efda0, Bias 18146c2c0 and the player's ducked / facing steps composed from them.
