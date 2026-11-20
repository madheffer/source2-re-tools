# +use: FindUseEntity, IsUseableEntity, the collision property, ObjectCaps, bodies

server_20261105.

## Functions

| Address | Module | What |
|---|---|---|
| 180ade3a0 | server | PlayerUse (runs the use code) |
| 180ac2cf0 | server | the use code: high-priority pick, FindUseEntity, weapon trace, combine |
| 0x180ac3520 | server | CCSPlayer_UseServices FindUseEntity |
| 0x181472530 | server | AngleVectors (FindUseEntity, 180ae9bd0) |
| 181470980 | server | AngleVectors (the combine) |
| 0x180abed80 | server | init the out struct {-1, +inf, +inf, +inf} |
| 180ac7120 | server | high-priority pick (use services, out) |
| 180ac74c0 | server | the hint (pawn, ent, hint): CPlantedC4 and CHostage only |
| 180ae9bd0 | server | hint test (hint, pawn, mode, flags*) |
| 180ac6120 | server | bomb: m_flDefuseCountDown (+0xf70) - m_flDefuseLength (+0xf6c), the other's defuse start |
| 1801f95a0 | server | a - b |
| 180907f40 | server | hint init (+0x2c = -1) |
| 1801783b0 | server | maxss |
| 180a24fa0 | server | CPlantedC4 Spawn: `AddFlags(this, 0x2000000)` (1803c5940) |
| 1803c5940 | server | AddFlags |
| 18093d460 | server | m_bMapHasBombTarget |
| 1801c8ce0 | server | pawn's controller |
| 18032ee60 -> 1802d52b0 | server | Vector2D length: sqrt(x x + y y) |
| 180b4f9c0 | server | CCSPlayerPawn vfn 0xb48: fabs(EyePosition.z - GetAbsOrigin.z) (180a28730 the fabs) |
| 1801bb230 | server | line trace over a filter (with an entity) |
| 1801d6c60 | server | filter: ignore the pawn |
| 180250e50 | server | UTIL_TraceLine |
| 1814738b0 | server | normalize outside [1e-17, 1e17] |
| 1809f7c30 | server | C4Think (keeps a defuse going) |
| 0x18048a430 | server | sphere query setup (radius at +0xc) |
| 0x1803d95d0 | server | parent |
| 0x180cea8c0 | server | world AABB |
| 0x181489c20 -> 0x181476b30 | server | IntersectRayWithBox -> slab test |
| 0x180ce9200 | server | CalcNearestPoint |
| 0x180ab6130 | server | max use distance: minss(out[1 + u], base) |
| 0x180adebd0 | server | pickable (a weapon this pawn can pick up) |
| 0x180c78850 | server | distance outside a range (0 inside) |
| 18022c660 | server | CCSPlayerPawn ObjectCaps (vfn 0xd0) |
| 180d04f60 | server | CBaseEntity ObjectCaps |
| 0x180ad2bd0 | server | IsUseableEntity (UseServices vtable 0x181923de8 slot 0xb8) |
| 0x180ab9620 | server | CanAcquire |
| 0x180c78890 | server | base usable test |
| 0x180253910 | server | WorldToCollisionSpace |
| 0x18014cf50 | server | CollisionToWorldSpace |
| 0x180cea780 | server | clamp to the box |
| 0x1814759f0 -> 0x181475680 | server | TransformAABB |
| 0x180ed4b90 | server | CPhysBox ObjectCaps |
| 0x180e8a940 | server | CPhysicsProp ObjectCaps |
| 0x180d04fc0 | server | CBasePropDoor ObjectCaps (CPropDoorRotating slot 0xd0 too; vtables 0x1819dce10, 0x181965e80) |
| 0x180d551b0 / 0x180d04ef0 | server | CBaseDoor / CBaseButton ObjectCaps (momentary.md) |
| 0x180d127b0 | server | CBaseButton::Spawn (vtable 0x18181cae8 slot 0x48) |
| 0x1803eb7d0 | server | set move type (this, 6) |
| 0x180d10060 | server | set solid type (collision +0x5e8, 1) |
| 0x180b76060 | server | set model |
| 0x180cee640 | server | clear collision +0x3f bit 0 |
| 0x180cf1730 | server | OR into the attribute's +0x18 |
| 0x1803ee6e0 | server | button think (spawnflag 0x1000) |

## Fields

| Offset | Field |
|---|---|
| hint +8 / +0xc | priority / type |
| hint +0x10 | the point |
| hint +0x1c / +0x20 | reach / no-line distance (d written back) |
| hint +0x24 / +0x28 | cone, mode 0 / mode 1 (dot written back) |
| hint +0x2c | time (-1, or the other's defuse start) |
| entity +0x388 | m_fFlags; 0x2000000 high-priority use |
| CPlantedC4 +0xa98 | m_bBombTicking |
| CPlantedC4 +0xf60 | defuser handle |
| CPlantedC4 +0xf6c / +0xf70 | m_flDefuseLength / m_flDefuseCountDown |
| gamerules 0x1821ba1c0 +0x131 | m_bMapHasBombTarget |
| pawn +0x344 | team |
| controller +0x514 | state (0 or 3) |
| weapon +0x3e4 | owner handle |
| pawn +0x1500 / +0x1508 | m_pBot / m_bBotAllowActive |
| FindUseEntity [rbp - 0x58] | the raw player_use_radius |
| collision +0x40 / +0x4c | mins / maxs |
| collision +0x5b | m_nSolidType |
| collision +0x10 (+0x2f, so +0x3f) | m_collisionAttribute m_nCollisionFunctionMask (bit 0: solid contact) |
| attribute +0x18 | \|= 0x80000 when +0x9b4 |
| CPhysBox +0x94d / CPhysicsProp +0xccf | m_bEnableUseOutput |
| entity +0x360 | m_spawnflags |
| entity +0x2f3 | move type |
| button +0x9b4 | (name unread) |
| button +0x920 / +0x921 | m_bLocked (spawnflag 0x800) / m_bDisabled (spawnflag 2; the caps' disabled byte) (schema: CBaseButton's adjacent entries) |
| button +0x2b8 / +0x2b0 | use / touch function |

## Constants

| Value | What |
|---|---|
| player_use_radius | 0x182175930, default 80; R = max(80, 128) = 128 |
| tolerance 0.9238795 (0x3f6c835e, cos 22.5) | default; 0.9848077 (cos 10) only in the buy-menu branch |
| 0.9961947 | the second pass's tolerance floor |
| sv_weapon_swap_difficulty_near_hi_pri | 0x182175948, flags 0x82000, default 2 |
| sv_use_hi_pri_context_switch_time | 0x182175958, flags 0x82000 (default not read: the setup's floats 2.0 / 0.4 / 1.0 are ambiguous) |
| sv_debug_player_use | 0x182175938 (drawing only) |
| 0.98 (0x3f7ae148 at 0x18178fdec) | hint line fraction |
| filter vtable 0x18178c240, interacts 0xc3001, group 5, flags \|= 0x49 | hint line with an entity; without: mask 1, group 5 |
| 62.0, 36.0, -0.7, -0.5, +3 z | the bomb's hint |
| 0.9659258 (cos 15) | combine's weapon threshold |
| 0.7071 | ground candidate's starting dot |
| 1024 (0x1817b2c84) | look trace length |
| 0xc3081, group 4 | visibility trace |
| 0xc3081, group 3 | look trace |
| 0x1c1003, group 4 | weapon trace |
| 0xc3001 | sphere interacts-with |
| 8388608 | inverse scale for s = 0 |
| 0x181f4a000 | identity quaternion (TransformAABB) |
| BSS 0x182337ef0 / f10 / f40 | basis vectors |
| 0x4b / 0x49 | query flags: movement and bullets (flag 2 "hit solid requires generate-contacts") / +use |

## The hint (FindUseEntity's radius pass)

1. A flagged entity (180ac74c0) is never the best (IsUseableEntity refuses it).
2. When its hint has an entity, or `curtime - hint +0x2c <= sv_use_hi_pri_context_switch_time`: level `u = (priority > 1) + 1` (the bomb's priority 3: 2); 180ae9bd0(copy, pawn, 0, &flags).
3. Flags bit 4: `out[0] = max(out[0], u)`; out[1..u] take min(d, ...) (level 1 of a u > 1 hint takes `min(d, max(hint +0x1c - 10, 0))`).
4. A second pass at tolerance max(0.9961947, tolerance) only when out[0] >= 1, the first pass, and sv_weapon_swap_difficulty_near_hi_pri neither 0 nor 2: never by default.
5. out[1] shortens 180ac2cf0's weapon trace (min(128, out[1]) at level >= 1), only when the high-priority pick found nothing; it also caps every later candidate's use distance (0x180ab6130).
6. The bomb's candidate: SOLID_NONE (its Spawn's SetSolid(0)), bounds (0, 0, 0)-(8, 8, 8).

## The high-priority pick (180ac7120), before FindUseEntity

1. `r = max(player_use_radius, 128)`; a sphere of 2r at EyePosition (mask 0xc3001).
2. Each entity with m_fFlags 0x2000000: its hint must have an entity, a priority at least the best's, and pass 180ae9bd0(hint, pawn, 0, null).
3. Best: none yet, or a higher priority, or a smaller dot (+0x28), or a smaller distance (+0x1c). Its hint copied out (12 words).

### 180ac74c0 for a CPlantedC4 (first dynamic cast)

- 0 unless m_bBombTicking.
- Entity: the bomb when gamerules exist with m_bMapHasBombTarget and the pawn's team is 3, unless the defuser handle resolves to another pawn alive (vfn 0x550) with a controller in state 0 or 3: then null and +0x2c = 180ac6120(bomb). Not a CT: null.
- +8 priority 3, +0xc type 1, +0x10 = GetAbsOrigin + (0 + 0, 0 + 0, 3), +0x1c 62.0 (reach), +0x20 36.0 (no line needed), +0x24 -0.7 (cone, mode 0), +0x28 -0.5 (mode 1).
- CHostage (the second cast): hostage.md "+use".

### 180ae9bd0(hint, pawn, mode, flags*)

1. d: type 0 the 3D length `sqrt((dz dz + dy dy) + dx dx)` (eye - point); type 1 the 2D length of (eye.xy - point.xy).
2. `dz = point.z - eye.z`; `0 > dz`: h = vfn 0xb48; `dz >= -h`: `d = maxss(d, 0)`; else `d = maxss(d, -(h + dz))`. `dz >= 0`: `d = maxss(d, dz)`.
3. Bit 1: d <= +0x1c (else false without flags).
4. Bit 2: d <= +0x20, else a line eye -> point at fraction >= 0.98 (with an entity 1801bb230 over the filter, the pawn ignored by 1801d6c60; without, UTIL_TraceLine mask 1, group 5).
5. Bit 4: `v = eye - point`, `len = sqrt((z z + y y) + x x)`, `v x (1 / len)` inside [1e-17, 1e17] (zero for 0, 1814738b0 otherwise); forward = AngleVectors of EyeAngles (vfn 0x5f0); `dot = (fz vz + fy vy) + fx vx`; **`dot < (mode 0 ? +0x24 : +0x28)`**.
6. Every pass that reaches bit 4 writes the dot into +0x24 and +0x28 and d into +0x1c and +0x20.
7. Without flags: true only when all three pass; with flags: *flags = the bits, returns bits == 7.

### C4Think and the combine

- C4Think (1809f7c30) keeps a defuse going on 180ac74c0(defuser, bomb).entity == the bomb and 180ae9bd0(hint, defuser, 1, null): the wider cone (60 degrees against the pick's 45.6).
- 180ac2cf0 with a high-priority pick: FindUseEntity skipped; weapon trace length `minss(128, maxss(player_use_radius, 128))` = 128. A usable weapon it hit wins when its WorldSpaceCenter's direction from the eye gives `cos = (fz vz + fy vy) + fx vx` (forward from 181470980) >= -hint.+0x24 and -hint.+0x24 < 0.9659258; else the pick is the bomb (its Use: continuous, every command +use is held).
- So the bomb is reached from up to 62 u (2D, or the height past the pawn), looking within 45.6 degrees of its point; a defuse holds within 60 degrees.

## FindUseEntity (0x180ac3520)

Called by 180ac2cf0. Eye = EyePosition (vfn 0x5e8), angles = EyeAngles (vfn 0x5f0).

- Ground candidate: the ground entity when IsUseable(ground, 0x10), starting dot 0.7071 (no class here has caps bit 0x10).
- Sphere: 0x18048a430 stores R + R = 256 at +0xc, centred on the eye, interacts-with 0xc3001.

### The radius pass

Skipped: the pawn; IsUseableEntity(e, 0x20) false; a weapon with an owner (+0x3e4) or a parent (0x1803d95d0). Then:

1. box = world AABB (0x180cea8c0).
2. P = IntersectRayWithBox(eye, forward·R, box, tolerance 1.0): its end point on a hit; on a miss `P = eye + (forward·R)·0.5`.
3. Q = CalcNearestPoint(P).
4. `d = sqrt((dz² + dy²) + dx²)` of Q − eye; needs d ≤ R.
5. `dir = (Q − eye) · (1/d)` when d > 1e-17, else unscaled; `dot = (fy·diry + fz·dirz) + fx·dirx`; needs tolerance ≤ dot.
6. d ≤ the max use distance (0x180ab6130: `minss(out[1 + u], base)`); **base = player_use_radius itself (80, the raw cvar at [rbp - 0x58]), 128 for a weapon**. The look trace's H uses the same (u 0).
7. Better, with larger = bestDot < dot: no best yet or the candidate isn't a weapon: needs larger. Best is a weapon this pawn can pick up: needs larger and pickable itself. Otherwise: larger, or pickable (0x180adebd0).
8. Visibility: UTIL_TraceLine eye → Q (mask 0xc3081, group 4, pawn ignored); blocked when fraction ≠ 1 and the hit isn't the candidate; then eye → WorldSpaceCenter (vfn 0x2c8); still blocked by another entity: skipped.
9. Passes: best, bestDot = dot.

### The look trace

UTIL_TraceLine eye → eye + forward·1024 (mask 0xc3081, group 3). When it hits H, not the best, IsUseable(H, 0):

- `f = 0x180c78850(end.z, origin.z + mins.z, origin.z + maxs.z)`.
- `d = sqrt(((ey − sy)² + f²) + (ex − sx)²)`.
- d < H's max use distance: the result is H, except when a best exists and H is a weapon this pawn can't pick up.

### A bot pawn

CCSPlayerPawn ObjectCaps (18022c660): CBaseEntity's with bit 7 cleared, | 1 (impulse use) when m_pBot and m_bBotAllowActive: IsUseableEntity(bot, 0) passes, (bot, 0x20) doesn't, so a bot is only ever the look trace's hit. PlayerUse then drops a bot teammate's C4 to the user (c4.md "PlayerUse's C4 branches"). CS2's 0xc3081 includes the player layer: players block the visibility and look traces.

## IsUseableEntity (0x180ad2bd0)

1. False when 180ac74c0 flags the entity.
2. CCSWeaponBase: CanAcquire (0x180ab9620) gives r; passes when `(r & ~3) == 0 && r != 1`.
3. CChicken: passes when the caps asked for lack 0x20.
4. vfn 0x458: false for every class.
5. Base 0x180c78890: `(ObjectCaps & 7) && (ObjectCaps & req) == req && vfn 0x4a0` (vfn 0x4a0 always true here).

## The weapon trace (180ac2cf0)

UTIL_TraceLine from the eye along the view, interacts-with 0x1c1003, group 4, pawn ignored; length `min(128, local_1a4)`, local_1a4 = FindUseEntity's out distance (only the hint sets it, so 128).

## CCollisionProperty

Rotated path when `m_nSolidType & 0xfd` ≠ 0 (neither NONE 0 nor BBOX 2) and the abs angles are nonzero.

- WorldToCollisionSpace (0x180253910), rotated: the node's quaternion × (−1, −1, −1, 1), normalised by its dpps length (FLT_EPSILON for 0); `inv = 1/s` when s ≠ 1, 8388608 when s = 0; `o = rot(pos)·inv`, `r = rot(P)`; each lane `r·inv + (0 − o)`. Rotation: `t = 2(v × q.xyz)`, `t.x = 2(vz·qy − vy·qz)`, `t.y = 2(vx·qz − vz·qx)`, `t.z = 2(vy·qx − vx·qy)`; each lane `((t.z·qy − t.y·qz) + v.x) + w·t.x`, and so on. Not rotated: `(P − origin)·(1/scale)` (scale 0 gives 0).
- CollisionToWorldSpace (0x18014cf50), rotated: the same t, each lane `((t.z·qy − t.y·qz) + w·t.x) + v.x`, then `·scale + pos`. Not rotated: `scale·v + pos`.
- Clamp (0x180cea780): `maxs <= v ? maxs : v`, then `mins <= that ? that : mins`.
- CalcNearestPoint (0x180ce9200): to collision space, clamp, back.
- WorldSpaceCenter: CollisionToWorld((mins + maxs)·0.5).
- World AABB (0x180cea8c0), rotated: TransformAABB of scale·mins and scale·maxs, then + pos. TransformAABB conjugates by XOR (−0, −0, −0, 0) and normalises (zero length: identity 0x181f4a000), rotates the basis vectors to rows r_i; extent per lane `((|ext.x·r.x| + |ext.y·r.y|) + |ext.z·r.z|)`; centre rotated by the original quaternion. Not rotated: `scale·mins + pos`, `scale·maxs + pos`.

### IntersectRayWithBox (0x181489c20 -> 0x181476b30)

1. t1 = −1, t2 = 1, startsolid = 1.
2. i < 3: `d1 = mins_i − start_i`, `d2 = d1 − delta_i`; the other three: `d1 = start − maxs`, `d2 = d1 + delta`.
3. Both > 0: false. Either > 0: d1 > 0 clears startsolid; leaving (d1 ≤ d2): `t = (d1 + tol)/(d1 − d2)`, t2 = min; entering: `t = max(0, d1 − tol)/(d1 − d2)`, t1 = max.
4. Result: `startsolid || (t1 < t2 && t1 ≥ 0)`; end point `start + t1·delta` (t1 = 0 when startsolid), or the start in the startsolid-only case.

## ObjectCaps (vfn 0xd0)

| Class | Caps |
|---|---|
| CPhysBox (0x180ed4b90) | base \| (m_bEnableUseOutput +0x94d ? 0x40000021 : 0x40000000) |
| CPhysicsProp (0x180e8a940) | base \| 0x40000000 \| (m_bEnableUseOutput +0xccf ≠ 0): impulse only, no radius bit (only the look trace finds one) |
| CBasePropDoor (0x180d04fc0) | parent ? (parent's caps & 0x87) \| (0x80 when the parent is a player, vfn 0x558) : 0x80; \| 0x21 unless m_spawnflags has 0x8000 |
| CBaseDoor / CBaseButton | momentary.md |

The keyvalue is "enableuseoutput" (every prop and physbox on the four ZE maps checked: "false").

## func_button's body (CBaseButton::Spawn 0x180d127b0)

1. 0x1803eb7d0(this, 6): move type (+0x2f3) = 6 (PUSH).
2. 0x180d10060(collision +0x5e8, 1): m_nSolidType = 1 (SOLID_BSP).
3. 0x180b76060: the model.
4. Spawnflag 0x4000: 0x180cee640 clears m_nCollisionFunctionMask bit 0 (solid contact), then CollisionRulesChanged (vfn 0x5e0). Function mask 7, or 6 with 0x4000.
5. +0x9b4 set: 0x180cf1730(collision, 0x80000).

A non-solid button keeps its body: queries with flag 2 (0x4b: movement and bullets) skip a shape without bit 0; +use's traces (0x49) and the sphere still find it.

Other spawnflags: 0x1000 a think (0x1803ee6e0); 2 +0x921 (m_bDisabled); 0x800 +0x920 (m_bLocked); 0x400 the use function at +0x2b8; 0x100 the touch at +0x2b0.

## Unread

- The spatial query's group, object set and order (taken as RadiusDamage's enumeration filter: group 3, object set 0xe; the planted bomb taken as first in the list).
- CanAcquire's results 2 and 3 (these pass).
- m_vecMins / m_vecMaxs: from the model's physics bounds.
- The pawn's own collision shape for the look trace (taken as origin + (0, 72), (0, 54) ducked).
- CS2Fixes' EntWatch use path (an item's button parented to the player).
- sv_use_hi_pri_context_switch_time's default.
- Button +0x9b4's name; the rest of the spawn's tail (sounds, glow).
