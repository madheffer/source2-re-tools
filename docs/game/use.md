# +use: FindUseEntity, IsUseableEntity, the collision property, use-relevant ObjectCaps and bodies

server.dll 2026-11-05 (tools/re/binaries/server_20261105.dll). Ported: sim/src/combat/use_pick.rs (+ use_abi.rs
`ze_use_pick`), web/server/cs2web/combat/use-pick.js (the inputs), web/server/cs2web/combat/combat.js `use()` (the weapon trace and the
combine), web/src/world/entities/caps.js (ObjectCaps), movers.js / physics-rubikon.js (func_button's body). Checked by
`cargo test --release --lib use_pick` and web/server/cs2web/combat/use-test.mjs.

## FindUseEntity (CCSPlayer_UseServices, 0x180ac3520)

Called by 180ac2cf0 (the use code PlayerUse 180ade3a0 runs). Inputs:

- R = max(player_use_radius, 128). player_use_radius is registered at 0x182175930, default 80, so R = 128.
- The eye is the pawn's EyePosition (vfn 0x5e8); the angles are EyeAngles (vfn 0x5f0). forward = AngleVectors 0x181472530.
- The tolerance (a cosine) is 0.9238795 (0x3f6c835e, cos 22.5) by default. It is 0.9848077 (cos 10) only in the buy-menu branch, which this server doesn't have.
- The out struct is initialised by 0x180abed80 to {-1, +inf, +inf, +inf}.

### The hint (in FindUseEntity)

0x180ac74c0 flags only CPlantedC4 and CHostage (below, "The high-priority pick"). In FindUseEntity's radius pass a
flagged entity is never the best (IsUseableEntity refuses it, step 1): when its hint has an entity, or
curtime - hint +0x2c <= sv_use_hi_pri_context_switch_time, its level u = (priority > 1) + 1 (the bomb's priority 3: 2)
and 180ae9bd0(copy, pawn, 0, &flags) runs; with flags bit 4 the out struct's level count out[0] = max(out[0], u) and
its distances out[1..u] take min(d, ...) (level 1 of a u > 1 hint takes min(d, max(hint +0x1c - 10, 0))). Then a
second pass at tolerance max(0.9961947, tolerance) runs only when out[0] >= 1, it is the first pass, and
sv_weapon_swap_difficulty_near_hi_pri (0x182175948, flags 0x82000, **default 2**) is neither 0 nor 2: never by default.
The out distance out[1] is what shortens 180ac2cf0's weapon trace (min(128, out[1]) at level >= 1), and only when
the high-priority pick found nothing; it also caps every later candidate's use distance (0x180ab6130 below). **Ported**
(2026-11-16, "c4-pick": sim/src/combat/use_pick.rs `Hint`, use_abi.rs words 46-54, server/cs2web/combat/use-hint.js
radiusHint): the hint counts when it has an entity or its +0x2c is within the switch time; +0x2c is -1 (the hint's
init 180907f40) or, for a CT locked out, 180ac6120(bomb) = m_flDefuseCountDown (+0xf70) - m_flDefuseLength (+0xf6c),
the other's defuse start (1801f95a0 is a - b). The bomb's candidate: SOLID_NONE (its Spawn's SetSolid(0)), bounds
(0, 0, 0)-(8, 8, 8), first in the list (TODO(trace): the spatial query's order). sv_use_hi_pri_context_switch_time is 0x182175958 (flags 0x82000; its default not read: the setup's floats
2.0 / 0.4 / 1.0 are ambiguous). sv_debug_player_use is 0x182175938 (its drawing only).

## The high-priority pick (180ac7120): how the planted bomb is used

Ported: web/server/cs2web/use-hint.js (checked by defuse-test.mjs). 180ac2cf0 (the use code) calls it **before**
FindUseEntity:

- **180ac7120(use services, out)**: r = max(player_use_radius, 128) (1801783b0 is maxss); a sphere of 2r at the
  EyePosition (mask 0xc3001); each entity in it with m_fFlags (+0x388) bit **0x2000000** (CPlantedC4's Spawn sets it:
  180a24fa0 `AddFlags(this, 0x2000000)`, 1803c5940): its hint (180ac74c0) must have an entity, a priority (+8) at
  least the best's, and pass 180ae9bd0(hint, pawn, **0**, null); the best: no best yet, or a higher priority, or a
  smaller dot (+0x28), or a smaller distance (+0x1c). The best's hint is copied out (12 words).
- **180ac74c0(pawn, ent, hint)** for a CPlantedC4 (the first dynamic cast): returns 0 unless m_bBombTicking (+0xa98).
  Entity: the bomb when the gamerules (0x1821ba1c0) exist with m_bMapHasBombTarget (+0x131, 18093d460) and the pawn's
  team (+0x344) is 3, unless the bomb's defuser handle (+0xf60) resolves to another pawn that is alive (vfn 0x550)
  with a controller (1801c8ce0) in state 0 or 3 (+0x514): then null and +0x2c = 180ac6120(bomb) (unread). Not a CT:
  null. Then: +8 priority 3, +0xc type 1, +0x10 the point = GetAbsOrigin + (0 + 0, 0 + 0, 3), +0x1c 62.0 (reach),
  +0x20 36.0 (no line needed), +0x24 -0.7 (the cone, mode 0), +0x28 -0.5 (mode 1). (CHostage, the second cast: docs/game/hostage.md "+use"; ported: use-hint.js hostageHint.)
- **180ae9bd0(hint, pawn, mode, flags*)**: the distance d: type 0 the 3D length (sqrt((dz dz + dy dy) + dx dx), eye -
  point); type 1 d = Vector2D length of (eye.xy - point.xy) (18032ee60 -> 1802d52b0: sqrt(x x + y y)); dz = point.z -
  eye.z; when 0 > dz: h = vfn 0xb48 (CCSPlayerPawn 180b4f9c0: fabs(EyePosition.z - GetAbsOrigin.z), 180a28730 the
  fabs); dz >= -h: d = maxss(d, 0); else d = maxss(d, -(h + dz)); dz >= 0: d = maxss(d, dz). Bit 1: d <= +0x1c (else
  false without flags). Bit 2: d <= +0x20, else a line eye -> point at fraction >= 0.98 (0x3f7ae148 at 0x18178fdec):
  with an entity 1801bb230 over a filter (vtable 0x18178c240, interacts-with 0xc3001, group 5, flags |= 0x49, the
  pawn ignored by 1801d6c60), without UTIL_TraceLine 180250e50 (mask 1, group 5). Bit 4: v = eye - point, len =
  sqrt((z z + y y) + x x), v x (1 / len) inside [1e-17, 1e17] (else zero for 0, 1814738b0 otherwise); forward =
  AngleVectors 181472530 of EyeAngles (vfn 0x5f0); dot = (fz vz + fy vy) + fx vx; **dot < (mode 0 ? +0x24 : +0x28)**.
  Every pass that reaches bit 4 writes the dot into +0x24 and +0x28 and d into +0x1c and +0x20. Without flags: true
  only when all three pass; with flags: *flags = the bits, returns bits == 7.
- **C4Think** (1809f7c30) keeps a defuse going on 180ac74c0(defuser, bomb).entity == the bomb and
  180ae9bd0(hint, defuser, **1**, null): the wider cone (60 degrees against the pick's 45.6).
- **The combine in 180ac2cf0** with a high-priority pick: FindUseEntity is skipped; the weapon trace's length is
  minss(128, maxss(player_use_radius, 128)) = 128. A weapon it hit (a usable one, as before) wins when its
  WorldSpaceCenter's direction from the eye (the same normalize) gives cos = (fz vz + fy vy) + fx vx (forward from
  AngleVectors 181470980) >= -hint.+0x24 and -hint.+0x24 < 0.9659258 (cos 15); else the pick is the bomb (its Use:
  continuous, every command +use is held). So the bomb is reached from up to 62 u (2D, or the height past the pawn),
  looking within 45.6 degrees of its point, and a defuse holds within 60 degrees.

### The ground candidate

The ground entity is a candidate when IsUseable(ground, 0x10), with a starting dot of 0.7071. No class here has caps bit 0x10, so this is omitted.

### The sphere query

0x18048a430 stores the radius at +0xc, as R + R = 256. The sphere is centred on the eye, with interacts-with 0xc3001.

TODO(trace): the query's group and object set. use-pick.js takes RadiusDamage's enumeration filter (group 3, object set 0xe). The sim returns at most 64 entities, in its own order.

### The radius pass: each entity the sphere found

Skipped:

- the pawn;
- an entity that fails IsUseableEntity(e, 0x20);
- a weapon with an owner handle (+0x3e4) or a parent (0x1803d95d0).

For each remaining entity:

1. box = the world AABB (0x180cea8c0).
2. P = IntersectRayWithBox(eye, forward·R, box, tolerance 1.0) (0x181489c20). Its end point is used when the ray hits. On a miss, P = eye + (forward·R)·0.5.
3. Q = CalcNearestPoint(P) (0x180ce9200).
4. d = sqrt((dz² + dy²) + dx²), where (dx, dy, dz) = Q − eye. The candidate needs d ≤ R.
5. dir = (Q − eye) · (1/d) when d > 1e-17, else (Q − eye) unscaled. dot = (fy·diry + fz·dirz) + fx·dirx. The candidate needs tolerance ≤ dot.
6. d ≤ the max use distance (0x180ab6130: minss(out[1 + u], base)). **base is player_use_radius itself (80, the raw cvar FindUseEntity stores at [rbp - 0x58] before its max with 128), 128 for a weapon**; the port had R (128) for buttons and doors until 2026-11-16. The look trace's H uses the same distance (u 0).
7. The better test uses larger = bestDot < dot:
   - If there is no best yet, or the candidate isn't a weapon: the candidate needs larger.
   - If the best is a weapon this pawn can pick up: the candidate needs larger and must be pickable itself.
   - Otherwise: the candidate needs larger, or must be pickable.

   "Pickable" means 0x180adebd0 (weapon-use.js `usable`).
8. Visibility: UTIL_TraceLine eye → Q (0x180250e50), with mask 0xc3081, group 4 and the pawn ignored. The candidate is blocked when the fraction ≠ 1 and the hit isn't the candidate. If blocked, the same trace runs eye → WorldSpaceCenter (vfn 0x2c8). If that is still blocked by another entity, the candidate is skipped.
9. A candidate that passes all of this becomes best, with bestDot = dot.

### The look trace

UTIL_TraceLine eye → eye + forward·1024 (0x1817b2c84), with mask 0xc3081 and group 3 (trace-world.js USE_TRACE). It applies when it hits an entity H that isn't the best and passes IsUseable(H, 0):

- f = 0x180c78850(end.z, origin.z + mins.z, origin.z + maxs.z): how far the value lies outside the range, 0 inside it.
- d = sqrt(((ey − sy)² + f²) + (ex − sx)²).
- If d < H's max use distance, the result is H. The exception: when a best exists and H is a weapon this pawn can't pick up, the result stays the best.

### A bot pawn in the look trace

CCSPlayerPawn's ObjectCaps (vfn 0xd0, 18022c660): CBaseEntity's (180d04f60) with bit 7 cleared, | 1 (impulse use) when
m_pBot (+0x1500) is set and m_bBotAllowActive (+0x1508): IsUseableEntity(bot, 0) passes, (bot, 0x20) doesn't, so a
bot is only ever the look trace's hit. PlayerUse then drops a bot teammate's C4 to the user (c4.md "PlayerUse's C4
branches"). Ported as a ray against each bot's hull box in JS (server/cs2web/combat/use-pick.js lookedAtBot): the sim's
world has no player bodies (TODO(trace): the pawn's own collision shape).

### Stand-ins

- The pawn's z range is its origin plus (0, 72), or (0, 54) ducked.
- The players have no bodies in the sim, so a player never blocks the visibility or look traces (CS2's 0xc3081 includes the player layer).
- An EntWatch item's button parented to the player is picked before the search, wherever the player looks. This rule comes from before the port. TODO(trace): CS2Fixes' EntWatch use path.

## IsUseableEntity (CCSPlayer_UseServices vtable 0x181923de8, slot 0xb8 = 0x180ad2bd0)

In order:

1. False when 0x180ac74c0 flags the entity.
2. A CCSWeaponBase: CanAcquire (0x180ab9620) gives r, and the weapon passes when `(r & ~3) == 0 && r != 1`. weapon-use.js `canAcquire` answers yes or no. TODO(trace): CanAcquire's results 2 and 3 (these pass).
3. A CChicken passes when the caps asked for lack 0x20.
4. vfn 0x458 is false for every class.
5. The base, 0x180c78890: `(ObjectCaps & 7) && (ObjectCaps & req) == req && vfn 0x4a0`. vfn 0x4a0 is always true here.

## The weapon trace and the combine (180ac2cf0)

UTIL_TraceLine from the eye along the view, with interacts-with 0x1c1003, group 4 and the pawn ignored. Its length is min(128, local_1a4), where local_1a4 is FindUseEntity's out-struct distance. Only the hint sets that distance, so the length is 128.

The old port capped it at FindUseEntity's hit distance; fixed (BUGFIXES 2026-11-11). The combine is unchanged (combat.js).

## CCollisionProperty (+0x40 mins, +0x4c maxs, +0x5b m_nSolidType)

The rotated path applies when `m_nSolidType & 0xfd` ≠ 0 (neither NONE 0 nor BBOX 2) and the abs angles are nonzero.

### WorldToCollisionSpace (0x180253910)

Rotated:

- The node's quaternion × (−1, −1, −1, 1), normalised by its dpps length (FLT_EPSILON when the length is 0).
- inv = 1/s when s ≠ 1, or 8388608 when s = 0.
- o = rot(pos)·inv and r = rot(P).
- Each lane is r·inv + (0 − o).
- The rotation is t = 2(v × q.xyz) with t.x = 2(vz·qy − vy·qz), t.y = 2(vx·qz − vz·qx), t.z = 2(vy·qx − vx·qy). Each lane is ((t.z·qy − t.y·qz) + v.x) + w·t.x, and so on.

Not rotated: (P − origin)·(1/scale). A scale of 0 gives 0.

### CollisionToWorldSpace (0x18014cf50)

Rotated: the same t, with each lane ((t.z·qy − t.y·qz) + w·t.x) + v.x, then ·scale + pos. Not rotated: scale·v + pos.

### The clamp (0x180cea780)

max(mins, min(v, maxs)), with ties as written: `maxs <= v ? maxs : v`, then `mins <= that ? that : mins`.

### CalcNearestPoint (0x180ce9200)

To collision space, the clamp, then back to the world.

### WorldSpaceCenter

CollisionToWorld((mins + maxs)·0.5).

### The world AABB (0x180cea8c0)

Rotated:

- TransformAABB (0x1814759f0 → 0x181475680) of scale·mins and scale·maxs, then + pos.
- TransformAABB conjugates by XOR (−0, −0, −0, 0) and normalises (a zero length gives the identity, 0x181f4a000).
- It rotates the basis vectors (BSS 0x182337ef0 / f10 / f40) to rows r_i.
- The extent per lane is ((|ext.x·r.x| + |ext.y·r.y|) + |ext.z·r.z|).
- The centre is rotated by the original quaternion.

Not rotated: scale·mins + pos and scale·maxs + pos.

### IntersectRayWithBox (0x181489c20 → slab test 0x181476b30)

- Start with t1 = −1, t2 = 1, startsolid = 1.
- For i < 3: d1 = mins_i − start_i and d2 = d1 − delta_i. For the other three: d1 = start − maxs and d2 = d1 + delta.
- Both > 0: return false.
- Either > 0:
  - d1 > 0 clears startsolid.
  - Leaving (d1 ≤ d2): t = (d1 + tol)/(d1 − d2), and t2 = min.
  - Entering: t = max(0, d1 − tol)/(d1 − d2), and t1 = max.
- The result is startsolid || (t1 < t2 && t1 ≥ 0).
- The end point is start + t1·delta (with t1 = 0 when startsolid), or the start in the startsolid-only case.

### The bounds

TODO(trace): m_vecMins and m_vecMaxs come from the model's physics bounds. use-pick.js takes the bounds of the baked model-space hull verts.

## ObjectCaps (vfn 0xd0) of the classes +use meets

- **CPhysBox** (0x180ed4b90): base | (m_bEnableUseOutput +0x94d ? 0x40000021 : 0x40000000).
- **CPhysicsProp** (0x180e8a940): base | 0x40000000 | (m_bEnableUseOutput +0xccf ≠ 0). That is impulse only, with no radius bit, so only the look trace finds one.
- **Their keyvalue** is "enableuseoutput". Every prop and physbox on the four baked maps has "false" (use-test.mjs checks this).
- **CBasePropDoor** (0x180d04fc0, CPropDoorRotating's slot 0xd0 as well; vtables 0x1819dce10 and 0x181965e80):
  - parent ? (the parent's caps & 0x87) | (0x80 when the parent is a player, vfn 0x558) : 0x80;
  - | 0x21, unless m_spawnflags (+0x360) has 0x8000.
- **CBaseDoor** (0x180d551b0) and **CBaseButton** (0x180d04ef0): docs/game/momentary.md.

## func_button's body (CBaseButton::Spawn, vtable 0x18181cae8 slot 0x48 = 0x180d127b0)

- 0x1803eb7d0(this, 6): the move type (+0x2f3) becomes 6 (PUSH).
- 0x180d10060(collision +0x5e8, 1): m_nSolidType (+0x5b) becomes 1 (SOLID_BSP).
- 0x180b76060: the model.
- Spawnflag 0x4000: 0x180cee640(collision) clears bit 0 of collision +0x3f. That is m_collisionAttribute (+0x10) m_nCollisionFunctionMask (+0x2f), the solid contact bit. It then calls CollisionRulesChanged (vfn 0x5e0).
- +0x9b4 set: 0x180cf1730(collision, 0x80000) ORs 0x80000 into the attribute's +0x18.

So a non-solid button keeps its body. Queries with flag 2 ("hit solid requires generate-contacts": movement and bullets, 0x4b) skip a shape without bit 0 (sim/src/rn/query.rs). +use's traces (0x49) and the sphere still find it.

Ported as func_button's `functionMask`: 7, or 6 with 0x4000. rubikon's PhysicsApi.SetBrushFunctionMask sets the bits.

Other spawnflags the spawn reads:

- 0x1000: a think (0x1803ee6e0).
- 2: +0x921 (m_bDisabled... the caps' disabled byte).
- 0x800: +0x920.
- 0x400: the use function at +0x2b8.
- 0x100: the touch at +0x2b0.

Unread: the 0x9b4 field's name, and the rest of the spawn's tail (the sounds, the glow).
