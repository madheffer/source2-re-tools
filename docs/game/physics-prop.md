# CPhysicsProp (prop_physics, prop_physics_multiplayer) and the script API's Teleport

server_20261105; vphysics2_20260924 (one vtable); csgo/pak01 and core/pak01 surfaceproperties.vsurf_c.

## Vtables and slots

| Class | Vtable | Spawn (0x48) | CreateVPhysics (0x238) | Teleport (0x528) |
|---|---|---|---|---|
| CPhysicsProp | `1819c67a0` | `180e98a90` | `180e76070` | `180b7a1e0` |
| CPhysicsPropMultiplayer | `1818e04a8` | `180e98a90` | `180e76070` | `180b7a1e0` |
| CBreakableProp | `1819367e0` | `180bc5720` | `1803d0b90` | |
| CPhysBox | `18183b118` | `180ede010` | `180ec3900` | `1803ede40` (CBaseEntity's) |
| CPhysicsPropOverride | `18183a5a8` | | | |

An earlier build's physbox addresses: `181837f98` / `180ed7520` / `180ebce10`.

## Functions

| Address | What |
|---|---|
| 180d0e5d0 | set health (this, health) |
| 180d0e950 | (this, 1) in Spawn |
| 180d0e200 | SetCollisionGroup: group at collision +0x5e, layers as 180d07730 (group 5 debris not touchall; any group but 2 and 14 touchall, not debris) |
| 180d07730 | physbox's layer setter |
| 180d0e7b0 | (this, FLT_MAX) when +0xc88 |
| 180cf5910 | (collision) with spawnflags 4 + 0x1000 |
| 180cb8510 | (node, 1) for prop_data allow_flatten_hierarchy |
| 180b49710 | (this, +0xa40 == 0) |
| 180cf1730 | (collision, 0x80000) when +0xc8a |
| 180df27a0, 180df2720, 180df2760, 180df26e0 | glow property setters on this + 0x6a0 from +0xcb4 / +0xcb8 / +0xcbc / +0xcc0 |
| 180e6db60, 1813ab520 | called at Spawn's end |
| 180cee2e0 | (collision) with spawnflag 0x200000 |
| 180d0f2c0 | (collision, 1, group, 0xc3001, spawnflags & 1): VPhysicsInit (below) |
| 180d10060 | solid type |
| 1801a43a0 | node motion type |
| 180d111b0 | make the physics |
| 1803e6180 | DisableMotion (this, 0) |
| 18158b530 | (local, aggregate) vfn 0x40 with m_nDynamicContinuousContactBehavior |
| 180bb3800 | bit n of this + 0xaa8 (prop data interactions mask) |
| 1803f0260 | the aggregate (this, 0): part count vfn 0x38, part vfn 0x48 |
| 180b79420 | CBreakableProp's base spawn |
| 1803d77c0 | the model's prop data |
| 1803ebce0 | takedamage |
| 180d0e730 | max health |
| 18024e660 | script Entity.Teleport (registered by 18020a7d0) |
| 1803ea270 | set angular velocity (entity, angularVelocity) |
| 1803cd940 | the entity and what moves with it |
| 1803ee0b0 | teleport one entity |
| 1803ea1a0 | SetAbsAngles |
| 1803ea4a0 | SetAbsVelocity |
| 1803ea860 | sets +0x3c8 vector to the constant at 18177bf80 |
| 180cfb500 | before SetAbsOrigin |
| 1803ea3b0 | SetAbsOrigin |
| 1805c9180 | transform onto physics (physics system, entity, 0): single dynamic body vfn 0x1b8, else aggregate vfn 0x80 |
| 1800113f0 | vphysics2 CPhysicsBody (vtable 1803f44e0) slot 0x58: allocates an object (not matched to the server's interface) |

## Fields (schema near 0x181ded310)

| Offset | Field |
|---|---|
| +0x360 | spawnflags |
| +0x5e8 | collision property; its +0x5e the group |
| +0x6a0 | glow property |
| +0x958 | vfn 0x78 with the transform before / after (CPhysicsProp Teleport) |
| +0x3c8 | vector set by 1803ea860 (unread) |
| +0xa40 | tested in Spawn |
| +0xab0 | = 2 (CBreakableProp Spawn) |
| +0xab4 | = 8 (CPhysicsProp Spawn) |
| CBreakableProp +0xa78 | m_CPropDataComponent (+0xaa8 the interactions mask) |
| +0xab8 / +0xad0 / +0xae8 / +0xb08 | m_OnStartDeath / m_OnBreak / m_OnHealthChanged / m_OnTakeDamage |
| +0xb20 / +0xb24 / +0xb4c | m_impactEnergyScale / m_iMinHealthDmg / m_PerformanceMode |
| +0xc88 / +0xc89 / +0xc8a | m_bForceNavIgnore / m_bNoNavmeshBlocker / m_bForceNpcExclude |
| +0xc8c | m_massScale |
| +0xc90 | m_buoyancyScale |
| +0xc94 | m_damageType |
| +0xc98 / +0xc9c | m_damageToEnableMotion (int) / m_flForceToEnableMotion (float) |
| +0xca0 / +0xca1 / +0xca2 / +0xca3 | m_bDroppedByPlayer / m_bTouchedByPlayer / m_bFirstCollisionAfterLaunch / m_bHasBeenAwakened |
| +0xca4 | m_bIsOverrideProp |
| +0xcac | m_nDynamicContinuousContactBehavior |
| +0xcb4..+0xcc0 | glow state / range / range min / colour |
| +0xcc4 / +0xcc5 / +0xccf | m_bShouldAutoConvertBackFromDebris / m_bMuteImpactEffects / m_bEnableUseOutput |
| +0xd09 | m_bAwake |

## Constants

| Value | What |
|---|---|
| 0x18 | prop default collision group (physbox: 4) |
| 5 | debris group (spawnflag 4) |
| 9 | group when every part's vfn 0x58 is 9 ("breakable_glass" in vphysics2's table) |
| 0xc3001 | interacts-with |
| spawnflags 1 / 4 / 8 | asleep / debris / motion disabled (physbox: 0x4000 debris, 0x8000 motion disabled) |
| spawnflags 0x1000, 0x200000 | see Spawn / CreateVPhysics |
| 6 / 5 | solid type / move type VPHYSICS |
| 0.1 | m_flPressureDelay when 0 |

## CPhysicsProp::Spawn (180e98a90)

1. +0xca4 = classname is "prop_physics_override"; +0xab4 = 8; CBreakableProp::Spawn.
2. `forcemotiondisabled` true: spawnflags |= 8; `phys_start_asleep` true: |= 1.
3. An override with a `health` keyvalue: 180d0e5d0(this, health). 180d0e950(this, 1).
4. Unless the entity flags' bit 9 (`*(this[2] + 0x30) >> 9`): SetCollisionGroup(0x18); +0xc88 -> 180d0e7b0;
   spawnflag 4 -> SetCollisionGroup(5) (and 0x1000 -> 180cf5910); allow_flatten_hierarchy -> 180cb8510;
   CreateVPhysics; 180b49710; +0xc8a -> 180cf1730; the four glow setters; 180e6db60, 1813ab520, +0xca1 = 0.

## CPhysicsProp::CreateVPhysics (180e76070)

1. Spawnflag 0x200000: 180cee2e0.
2. Group = collision +0x5e (4 without a collision property). 180d0f2c0: vfn 0x248; SetCollisionGroup(group);
   interacts-with cleared if any bit, then |= 0xc3001 (each change through vfn 0x5e0); solid 6; SetMoveType(5) for
   motion argument 1 (6 otherwise; 2 becomes 3 with a move parent); node motion type 1; physics made; last argument
   1 -> the physics' vfn 0x178 (Sleep). What VPhysicsInitNormal does for a physbox, plus the group and the sleep.
3. m_massScale > 0 and != 1: vfn 0x148 (mass) x it into vfn 0x150. m_buoyancyScale > 0 and != 1: vfn 0x1b8 (water).
4. No body: `Cannot create physics for %s "%s" (%s) @{%g,%g,%g}`, return 0.
5. Group 0x18 and every part's vfn 0x58 is 9: SetCollisionGroup(9).
6. m_damageType == 1: aggregate flags (vfn 0x460 / 0x468) |= 1.
7. Spawnflag 8, +0xc98 > 0 or +0xc9c > 0: DisableMotion.
8. 18158b530 with +0xcac.
9. Interactions bit 5 and aggregate flag bit 0 clear: flags |= 1; bit 7: |= 4.

No damping, drag or friction set by either function.

CBreakableProp::Spawn (180bc5720): +0xab0 = 2, impact energy scale, a time; base spawn; prop data; `health` ->
180d0e5d0; takedamage by health and breakable flags; max health; m_flPressureDelay 0 -> 0.1; `fire_interactions`
keys (flashpoint, heat_delay, ...). No mass, damping or collision call: unlike CBreakable::Spawn for a physbox
(gamemass, masscenteroffset), a prop's mass is its model's, scaled by massscale in CreateVPhysics alone.

## Entity.Teleport (18024e660)

`Teleport({ position, angles, velocity, angularVelocity })` or `Teleport(position, angles, velocity)`: vfn 0x528 with
the given three; with angularVelocity and move type 5, 1803ea270.

- CPhysicsProp 180b7a1e0: CBaseEntity::Teleport (1803ede40), then +0x958's vfn 0x78.
- CBaseEntity::Teleport: each of 1803cd940's entities through 1803ee0b0, then each one's vfn 0x5e0.
- 1803ee0b0: angles -> SetAbsAngles; velocity -> SetAbsVelocity and +0x3c8 = constant 18177bf80 (taken as zero);
  position -> 180cfb500, SetAbsOrigin. With an aggregate: 1805c9180; with a velocity and vfn 0x2b8's check, every
  body's vfn 0x200 (linear velocity) again.
- SetAbsVelocity with move type 5: every body's vfn 0x200.
- So Teleport({ angles, velocity }) sets the body's transform (position kept) and linear velocity; angular velocity untouched.

## Surface table

CS2 has two surfaceproperties/surfaceproperties.vsurf_c: csgo/pak01's (164 surfaces, each a full physics block:
no_decal density 900, elasticity 0.25, friction 0.8) and core/pak01's (81, some only a density: no_decal, flesh). The
game's search path takes csgo's. With core's values 30 of 73 surfaces of ze_resident_evil_3's physics.bin were wrong
(gravel friction 0.4 for 0.8, woods' elasticity 0.1 for 0.25, densities; two with no friction; no_decal at friction 0,
elasticity 0). A hull pushed at 200 u/s kept 185 u/s after 0.75 s with them.

## Seen

- de_inferno: 390 of 390 props with a physics model get a body, 361 spawn asleep.
- cs_italy's italy_plate_01 / 02 / 03 (thin discs), dropped 12 units, fall through table and floor (11 other models
  there and 14 on de_inferno land): m_nDynamicContinuousContactBehavior is the first thing to read.

## Unread

- The part's vfn 0x58 (the group-9 rule).
- The interactions' names and the aggregate's flag bits.
- The constant at 18177bf80 and what +0x3c8 is.
- Whether CS2 loads core's surface file at all for the names only it has.
- CPhysicsProp's own EnableMotion / DisableMotion / Wake / Sleep handlers; player push, bullet / explosion forces, gibs.
