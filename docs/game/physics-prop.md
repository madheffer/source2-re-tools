# CPhysicsProp (prop_physics, prop_physics_multiplayer) and the script API's Teleport

Read 2026-11-18 from server.dll 2026-11-05 (Ghidra /server_20261105.dll; the file in source2-compiler
tools/re/binaries), for ze_resident_evil_3's zombie NPCs: each one's mover is a prop_physics_multiplayer the map's
script pushes with `Teleport({ angles, velocity })` (web/src/world/entities/classes/scripts-re3-npc.js). The question
was why our stand-in body kept its speed on the floor. **The answer was not here** (section 4): CS2 gives a prop
nothing a physbox does not get. What was read is kept for the port of CPhysicsProp that is still to do.

Found with `tools/re/game/rtti.py` (vtables), `tools/re/game/vslot.py` (slots), `tools/re/game/strva.py` (new: a string's
address) + `tools/re/game/riprefs.py` (who references it).

## 1. Vtables and slots

| Class | Vtable | Spawn (0x48) | CreateVPhysics (0x238) | Teleport (0x528) |
|---|---|---|---|---|
| CPhysicsProp | `1819c67a0` | `180e98a90` | `180e76070` | `180b7a1e0` |
| CPhysicsPropMultiplayer | `1818e04a8` | `180e98a90` | `180e76070` | `180b7a1e0` |
| CBreakableProp | `1819367e0` | `180bc5720` | `1803d0b90` | |
| CPhysBox | `18183b118` | `180ede010` | `180ec3900` | `1803ede40` (CBaseEntity's) |
| CPhysicsPropOverride | `18183a5a8` | | | |

(rubikon/CS2_RUNTIME.md's physbox addresses, `181837f98` / `180ed7520` / `180ebce10`, are an earlier build's.)

## 2. CPhysicsProp::Spawn (`180e98a90`)

- `+0xca4` = the classname is "prop_physics_override"; `+0xab4` = 8.
- CBreakableProp::Spawn (`180bc5720`).
- Keyvalue `forcemotiondisabled` true: spawnflags (`+0x360`) |= 8. `phys_start_asleep` true: |= 1.
- An override with a `health` keyvalue: `FUN_180d0e5d0(this, health)`.
- `FUN_180d0e950(this, 1)`; then, unless the entity flags' bit 9 (`*(this[2] + 0x30) >> 9`) is set:
  - the collision property (`this + 0x5e8`) **SetCollisionGroup(0x18)** (`FUN_180d0e200`: writes the group at
    `+0x5e`, and its layers as a physbox's `FUN_180d07730` does: group 5 is debris and not touchall, any group but 2
    and 14 touchall and not debris);
  - `+0xc88` set: `FUN_180d0e7b0(this, FLT_MAX)`;
  - **spawnflag 4: SetCollisionGroup(5)** (debris), and with spawnflag 0x1000 also `FUN_180cf5910(collision)`;
  - the model's `prop_data` key `allow_flatten_hierarchy`: `FUN_180cb8510(node, 1)`;
  - CreateVPhysics (slot 0x238);
  - `FUN_180b49710(this, +0xa40 == 0)`; `+0xc8a` set: `FUN_180cf1730(collision, 0x80000)`;
  - four setters on `this + 0x6a0` from `+0xcb4`, `+0xcb8`, `+0xcbc`, `+0xcc0` (`180df27a0`, `180df2720`,
    `180df2760`, `180df26e0`: the glow property's fields, not physics);
  - `FUN_180e6db60(this)`, `FUN_1813ab520(this)`, `+0xca1 = 0`.

## 3. CPhysicsProp::CreateVPhysics (`180e76070`)

- Spawnflag 0x200000: `FUN_180cee2e0(collision)`.
- The group handed on is the collision property's (`+0x5e`), 4 when the entity has no collision property.
- `FUN_180d0f2c0(collision, 1, group, 0xc3001, spawnflags & 1)`, read 2026-11-18: the entity's vfn 0x248;
  SetCollisionGroup(group) again (`FUN_180d0e200`); the record's interacts-with cleared when it has any bit, then
  |= 0xc3001 (each change through the entity's vfn 0x5e0); solid type 6 (`FUN_180d10060`); SetMoveType(5) for the
  motion argument 1 (6 otherwise; a motion argument 2 becomes 3 with a move parent); the node's motion type 1
  (`FUN_1801a43a0`); the physics made (`FUN_180d111b0`); and with the last argument 1 **the new physics' vfn 0x178
  (Sleep)**. What VPhysicsInitNormal does for a physbox, plus the group and the sleep.
- On what it returns: `m_massScale` (`+0xc8c`) > 0 and != 1: vfn 0x148 (the mass) times it into vfn 0x150;
  `m_buoyancyScale` (`+0xc90`; not an inertia scale, as first written here) > 0 and != 1: vfn 0x1b8 (water).
- No body: `Cannot create physics for %s "%s" (%s) @{%g,%g,%g}`, return 0.
- The group is 0x18 and every part's vfn 0x58 is 9: SetCollisionGroup(9). NOT READ: what that vfn returns.
- `m_damageType` (`+0xc94`) == 1: the aggregate's flags (vfn 0x460 / 0x468) |= 1.
- Spawnflag 8, `+0xc98` (int) > 0 or `+0xc9c` (float) > 0 (damagetoenablemotion / forcetoenablemotion):
  `FUN_1803e6180(this, 0)` (DisableMotion).
- `FUN_18158b530(local, aggregate)` vfn 0x40 with `m_nDynamicContinuousContactBehavior` (`+0xcac`).
- `FUN_180bb3800(this, n)` is bit n of `this + 0xaa8` (inside m_CPropDataComponent, `+0xa78`: the prop data's
  interactions mask). Bit 5 and the aggregate's flag bit 0 clear: flags |= 1; bit 7: |= 4. NOT READ: the
  interactions' names and what the aggregate's flag bits do.

**No damping, drag or friction is set by either function.** A prop differs from a physbox in its default collision
group (0x18 against 4), its spawnflag bits (debris is 4, not 0x4000; motion disabled 8, not 0x8000; asleep 1) and
the group-9 rule.

### Fields (tools/re/game/schema.py --near 0x181ded310)

CPhysicsProp: `+0xc88` m_bForceNavIgnore, `+0xc89` m_bNoNavmeshBlocker, `+0xc8a` m_bForceNpcExclude, `+0xc8c`
m_massScale, `+0xc90` m_buoyancyScale, `+0xc94` m_damageType, `+0xc98` m_damageToEnableMotion, `+0xc9c`
m_flForceToEnableMotion, `+0xca0` m_bDroppedByPlayer, `+0xca1` m_bTouchedByPlayer, `+0xca2`
m_bFirstCollisionAfterLaunch, `+0xca3` m_bHasBeenAwakened, `+0xca4` m_bIsOverrideProp, `+0xcac`
m_nDynamicContinuousContactBehavior, `+0xcb4`..`+0xcc0` the glow state / range / range min / colour, `+0xcc4`
m_bShouldAutoConvertBackFromDebris, `+0xcc5` m_bMuteImpactEffects, `+0xccf` m_bEnableUseOutput, `+0xd09` m_bAwake.
CBreakableProp: `+0xa78` m_CPropDataComponent, `+0xab8` m_OnStartDeath, `+0xad0` m_OnBreak, `+0xae8`
m_OnHealthChanged, `+0xb08` m_OnTakeDamage, `+0xb20` m_impactEnergyScale, `+0xb24` m_iMinHealthDmg, `+0xb4c`
m_PerformanceMode.

### CBreakableProp::Spawn (`180bc5720`), read for what it does to the physics: nothing

`+0xab0` = 2, the impact energy scale and a time; the base spawn (`180b79420`); the model's prop data
(`FUN_1803d77c0`); a `health` keyvalue -> `FUN_180d0e5d0`; takedamage (`FUN_1803ebce0`) by the health and the
breakable flags; the max health (`FUN_180d0e730`); `m_flPressureDelay` 0 -> 0.1; the model's `fire_interactions`
keys (flashpoint, heat_delay, ...). No mass, damping or collision call: unlike CBreakable::Spawn for a physbox
(gamemass, masscenteroffset), a prop's mass is its model's, scaled by massscale in CreateVPhysics alone.

### The part's vfn 0x58 (the group-9 rule): still not read

The aggregate (`FUN_1803f0260(this, 0)`) gives its part count (vfn 0x38) and a part (vfn 0x48); the part's vfn 0x58
answering 9 for every part turns the group 0x18 into 9. vphysics2's CPhysicsBody vtable (`1803f44e0` in the
2026-09-24 build) has a slot 0x58 (`1800113f0`) that allocates an object, not a getter of a byte: the layout of the
server's interface for this build was not matched to it. Group 9 is "breakable_glass" in vphysics2's table
(rubikon CollisionRules.Groups); the rule is not ported.

## 3b. Ported (2026-11-18): rubikon/src/Game/PhysicsProp.cs

`PhysicsProp.Spawn`: the body dynamic, the record { interacts-with 0xc3001, function mask 7, group 0x18 or 5 with
spawnflag 4 }, the model's layers merged, the group's layers and physics_prop pushed (PhysBox.Push), Sleep with
spawnflag 1, massscale, DisableMotion with spawnflag 8 or a damage / force to enable motion. The engine's classes
prop_physics, prop_physics_multiplayer and prop_physics_override (brushes.js physicsProp) spawn it
(physics-rubikon.js spawnPropBody: "forcemotiondisabled" and "phys_start_asleep" set the flag bits as Spawn does) and
the step treats the body as a physbox's (state.propBody). physics-prop-test.mjs: on de_inferno 390 of 390 props
with a physics model have a body, the 361 spawned asleep stay put, a lifted one falls, lands and rests,
DisableMotion / EnableMotion hold and release it.

Not ported, each named in PhysicsProp.cs: the group-9 rule, spawnflags 0x1000 / 0x200000, buoyancy, the
aggregate's flag bits, m_nDynamicContinuousContactBehavior, the nav / NPC fields. And beyond the spawn: the player
as a physics obstacle (a player does not push a prop), bullets' and explosions' forces, a breaking prop's gibs,
CPhysicsProp's own EnableMotion / DisableMotion / Wake / Sleep handlers (a physbox's are used).
**Seen**: cs_italy's three plate models (italy_plate_01 / 02 / 03), woken and dropped 12 units, fall through the
table and the floor (11 other models on that map and 14 on de_inferno land). Thin discs: the continuous contact
behaviour above is the first thing to read for it. Nothing wakes a sleeping prop in play today but another moving
body.

## 4. The script API's Entity.Teleport (`18024e660`)

Registered by `18020a7d0`. `Teleport({ position, angles, velocity, angularVelocity })` or `Teleport(position,
angles, velocity)`: the entity's vfn 0x528 with the three that were given, then, with an angularVelocity and the
entity's move type 5 (VPHYSICS), `FUN_1803ea270(entity, angularVelocity)`.

- CPhysicsProp's vfn 0x528 (`180b7a1e0`): CBaseEntity::Teleport (`1803ede40`), then `+0x958`'s vfn 0x78 with the
  transform before and after.
- CBaseEntity::Teleport: the entity and what moves with it (`FUN_1803cd940`), each through `FUN_1803ee0b0`, then
  each one's vfn 0x5e0.
- `FUN_1803ee0b0`, for the entity itself: angles -> SetAbsAngles (`1803ea1a0`); velocity -> SetAbsVelocity
  (`1803ea4a0`) and the entity's `+0x3c8` vector set to the constant at `18177bf80` (`1803ea860`; NOT READ: the
  constant, taken to be zero, and what the field is); position -> `FUN_180cfb500`, SetAbsOrigin (`1803ea3b0`).
  Then, with a physics aggregate: `FUN_1805c9180(physics system, entity, 0)`, and with a velocity and the move
  type's check (vfn 0x2b8) every body's vfn 0x200 (the linear velocity) again.
- SetAbsVelocity with move type 5: every body's vfn 0x200 with the velocity.
- `FUN_1805c9180`: the entity's transform onto its physics: a single dynamic body gets vfn 0x1b8 (its transform
  set), otherwise the aggregate's vfn 0x80.

So Teleport({ angles, velocity }) on a physics prop sets the body's transform (its position kept) and its linear
velocity, and **does not touch its angular velocity**: what our port does (`physics.teleport(body, pos, quat,
velocity)`).

## 5. What made the NPCs slide: the surface table, not the prop

`node tools/physics-surfaces.mjs <physics.bin> [model ...]` (new) prints what the physics was given. The mover's
hull has the surface `no_decal`; ze_resident_evil_3's physics.bin had it at friction 0, elasticity 0. CS2 has two
`surfaceproperties/surfaceproperties.vsurf_c`: csgo/pak01's (164 surfaces, every one a full physics block: no_decal
density 900, elasticity 0.25, friction 0.8) and core/pak01's (81, some a density and nothing else: no_decal,
flesh). bake/SurfaceBake.cs read the stock packs in search order, csgo first, each later file replacing the
earlier one's entries: core's replaced csgo's. The game's file is the one CS2 has (the search path; and
source2-compiler's capture-checked settles read csgo/pak01's alone). Read last to first now.

With core's values 30 of the 73 surfaces of ze_resident_evil_3's physics.bin were wrong (gravel friction 0.4 for
0.8, the woods' elasticity 0.1 for 0.25, densities), two with no friction at all. Measured on the mover's hull
pushed to 200 u/s along the floor: 185 u/s left after 0.75 s before; the NPC now stops on its human (distance 0,
speed 0) for the whole grab.

Open: whether CS2 loads core's file at all for the names only it has (kept here); every other map's physics.bin and
(not web/public/ze-players/ragdolls.bin: rebaked 2026-11-18 it is byte-identical, its surfaces read the same either way) is still the
old table until their physics is rebaked.
