# prop_door_rotating (CPropDoorRotatingBreakable <- CPropDoorRotating <- CBasePropDoor)

server_20261105. scripts/propdata.vdata_c.

prop_door_rotating is CPropDoorRotatingBreakable: CPropDoorRotatingBreakable > CPropDoorRotating > CBasePropDoor > CDynamicProp > CBreakableProp > CBaseProp > CBaseAnimGraph > CBaseModelEntity > CBaseEntity. Vtables: CPropDoorRotatingBreakable 1819dd938, CPropDoorRotating 1819dce10, CBasePropDoor 181965e80.

## Functions

| Address | Module | What |
|---|---|---|
| 180f3bd00 | server | CPropDoorRotatingBreakable::Spawn (slot 0x48) |
| 180f3bbd0 | server | CPropDoorRotating::Spawn (the same without the breakable parts) |
| 1803d9c80 | server | GetVectors(this, fwd*, right*, up*) off the node's world rotation |
| 180bec940 | server | refresh the node's world rotation (+0xf4 dirty) |
| 180f14800 | server | CalcOpenAngles (vfn 0xad0) |
| 180f148d0 | server | the sweep bounds (this, angA, angB, min*, max*) |
| 180d60df0 / 180f183d0 | server | context think at 1200 s / its bool callback (true for "checkpoint_exit", else not locked: the nav's passable test) |
| FUN_180f3e840 | server | "damage%d" damage states (1 up) |
| 180d13220 | server | CBasePropDoor::Spawn |
| 180b77df0 | server | (this, 0, 2, 0) in Spawn (unread) |
| 1803eb7d0 | server | SetMoveType (6 PUSH) |
| 1803d6de0 | server | abs angles |
| 180bc5d40 / 180ba23f0 | server | CBreakableProp / CDynamicProp spawn parts (prop data; unread) |
| 180f22e80 | server | latch y edge: min or max y (unread) |
| 180ceaad0 | server | turn by the node's transform |
| 180b746f0 / 180b522b0 | server | the hardware bodygroup: 180b746f0(180b522b0(this, 1), m_nHardwareType) (unread) |
| 180b49710 | server | (this, +0xa40 == 0) (unread) |
| 180f18210 | server | vfn 0xa68: the start position |
| 18146bb60 / 181475ab0 / 18146fe70 / 181473410 | server | the ajar quaternion blend (unread) |
| 1803eb070 | server | SetLocalAngles |
| 180ce8380 | server | vfn 0xa18: the sounds |
| 180fec9a0 | server | fill an empty sound |
| 180ce0310 | server | Activate (slot 0x68)(this, type) |
| 180b964a0 | server | the base's Activate |
| 180d17f10 | server | the areaportals (this, open) |
| 18137ab40 / 181384da0 / 181389390 | server | the name iterator |
| 1816b6d80 | server | dynamic_cast |
| 180ba1030 | server | CreateVPhysics (slot 0x238, CBaseAnimGraph's chain) |
| 180d0f740 | server | (collision, motion 3 keyframed, group 4, interacts-with 0xc3001) |
| 180cee2e0 / 180cf1540 | server | collision off / on (function mask \|= 7) |
| 180d04fc0 | server | ObjectCaps (use.md) |
| 180d19800 | server | Use (vfn 0x498) |
| 180d16590 | server | PlayerUse (vfn 0xa90) |
| 180d05440 | server | vfn 0xa38: locked use |
| 180d55fd0 | server | PlayLockSounds(this, &m_ls, locked, 0, &latch) |
| 180d065c0 | server | vfn 0xa40: unlocked use |
| 180f115a0 | server | vfn 0x9f0: ajar should open |
| 180f17fb0 | server | vfn 0x9f8(this, any): the close path clear |
| 18014a300 | server | angles equal (exact) |
| 180cf07d0 | server | DoorOpen(this, away) |
| 180d05a90 | server | vfn 0xaa0(away, sound): opening events |
| 180cf01f0 | server | DoorClose |
| 180cf0470 | server | OnDoorClosed |
| 180f122e0 | server | BeginOpening (vfn 0xa48)(away) |
| 180f12070 | server | BeginClosing (vfn 0xa50) |
| 180f14ac0 | server | GetOpenAngles (vfn 0xab8)(this, away, out) -> side |
| 1802f6c00 | server | (angles, 1): the yaw |
| 1801fe910 | server | AngleNormalize |
| 180f22c60 | server | side of (this, other) |
| 1814738b0 | server | normalize outside [1e-17, 1e17] |
| 180f15f40 | server | SetOpenDirection (vfn 0xac0)(this, away, side) |
| 180c30c10 | server | remove an entity |
| 180d3f2f0 | server | CEntityBlocker (abs origin, min, max, away, 0) |
| 180d0e200 | server | set collision group |
| 180cf1730 | server | interacts-exclude |
| 180f14e50 | server | the path sweep (this, side) |
| 1801783c0 / 1801783b0 | server | min / max |
| 18021a5d0 | server | box shape |
| 180c2f3c0 | server | TraceShape |
| 180bf9270 | server | owner's entity id |
| 180e8e250 | server | in the door's hierarchy |
| 1803d9980 | server | root (vfn 0xae0 entity blocker compare) |
| 181473e90 | server | angles -> quaternion |
| 1803d9790 / 181475200 | server | parent's transform / product |
| 180f11a00 | server | MoveTo (vfn 0xac8) |
| 180a48c80 | server | vector length `sqrt((x^2 + y^2) + z^2)` |
| 180f2d9b0 | server | MoveDone (vfn 0x4f8) |
| 1803eb140 | server | set local angular velocity |
| 180d1b7a0 | server | vfn 0x628: true (the pusher adds Euler steps) |
| 180cf08e0 | server | OnDoorOpened |
| 180d159d0 | server | vfn 0xab0: stop the moving sound (the 5 dwords cleared) |
| 180f2e800 | server | vfn 0xa28: entity blocker's collision off |
| LAB_180cee380 | server | think: 180d17f10(this, 0) |
| 180f2e620 | server | vfn 0xa30: entity blocker removed |
| 180d0df50 | server | vfn 0xa20: the auto return |
| 180cf0110 | server | auto-return move done |
| 1803eb9e0 | server | (think) (unread) |
| 180d156f0 | server | vfn 0xaa8: the moving sound |
| 180c84870 | server | sound position follows the origin |
| 180cf12c0 | server | vfn 0xa80(this, out, name, atLatch): EmitSound at the abs origin or m_vecLatchWorldPosition |
| 180d08da0 | server | the output table |
| 180cd93b0 / 180f018b0 | server | datamaps: CBasePropDoor / CPropDoorRotating |
| 180f15360 | server | m_ls keyvalues (from Precache 180d07c10) |
| 180d07c10 | server | Precache |
| 180cc2f90 | server | CBasePropDoor_API Open: vfn 0xa98(activator, 0) |
| 180cc3110 | server | OpenAwayFrom (the named entity, 180bfc940 with the activator / caller) |
| 180cc3210 | server | OpenAwayFromActivator (m_flSpeed = the float parameter for the call, then back; vfn 0xa98(activator, activator)) |
| 180cc3350 | server | Close (not closed: OnClose (activator, this), then DoorClose, which fires OnClose again) |
| 180cc33f0 | server | Toggle (closed and not locked: DoorOpen(0); open: DoorClose) |
| 180cc34a0 / 180cc3520 | server | Lock (vfn 0xa70(1)) / Unlock (vfn 0xa78(1)) |
| 180cc35a0 / 180cc3640 | server | PlayerOpen / PlayerClose (180cfd6c0 / 180cfd5a0: unread) |
| 180ef83c0 | server | CPropDoorRotating_API SetRotationDistance (m_flDistance, CalcOpenAngles, both sweep bounds from the local angles) |
| 180ef93b0 | server | SetSpeed (m_flSpeed, then vfn 0xa60) |
| 180efab40 / 180efba90 | server | CPropDoorRotatingBreakable_API SetUnbreakable / SetBreakable (m_bBreakable 0 / 1) |
| 180d06710 | server | vfn 0xa98(activator, away) |
| 180d008a0 | server | Lock (vfn 0xa70)(sound) |
| 180d17190 | server | Unlock (vfn 0xa78) |
| 180f181e0 | server | vfn 0xa58: angular velocity 0, SetMoveDoneTime(-1) |
| 180f181c0 | server | vfn 0xa60: MoveTo(m_angGoal, m_flSpeed) |
| 180e8d810 | server | PerformPush (push.md) |
| 180d151f0 | server | StartBlocked (vfn 0x4d0)(other) |
| 180d00d20 | server | master's start-blocked (other) |
| 180cf1bf0 | server | EndBlocked (vfn 0x4e0) |
| 180ce3a30 | server | Blocked (vfn 0x4d8)(other) |
| 180e78760 | server | push (this, other, 1, 4.0) |
| 180fba3a0 / 1803ed610 | server | damage (its own health) / TakeDamageOld |
| 180f30060 | server | vfn 0x7f0 OnTakeDamage |
| 180bbe860 | server | CBreakableProp OnTakeDamage |
| 180b67140 | server | the base's |
| 180f30090 | server | vfn 0x7f8 OnTakeDamage alive |
| 180bbeca0 | server | CBreakableProp's alive |
| 180b75df0 | server | stage model ("models/%s.vmdl") |
| 180f19590 | server | vfn 0x418: the break |
| 181121570 | server | spawn gibs |
| 180bad480 | server | CBreakableProp's break |

## Fields

### CBasePropDoor

| Offset | Field |
|---|---|
| +0xca0 | m_flAutoReturnDelay |
| +0xca8 / +0xcb0 | m_hDoorList count / handles |
| +0xcc0 | m_nHardwareType |
| +0xcc4 | m_bNeedsHardware |
| +0xcc8 | m_eDoorState (0 closed, 1 opening, 2 open, 3 closing, 4 ajar) |
| +0xccc / +0xccd | m_bLocked / m_bNoNPCs |
| +0xcd0 / +0xcdc | m_closedPosition / m_closedAngles |
| +0xce8 / +0xcec | m_hBlocker / m_bFirstBlocked |
| +0xcf0 | m_ls (locksound_t: +8 locked sound +0xcf8, +0x10 unlocked +0xd00, +0x18 next time +0xd08) |
| +0xd10 | m_bForceClosed |
| +0xd14 | m_vecLatchWorldPosition |
| +0xd20 | m_hActivator |
| +0xd24 | m_flSpeed |
| +0xd28 | moving sound's handle (5 dwords to +0xd38) |
| +0xd40 / +0xd48 / +0xd50 | m_SoundMoving / m_SoundOpen / m_SoundClose |
| +0xd58 / +0xd60 / +0xd68 | m_SoundLock / m_SoundUnlock / m_SoundLatch |
| +0xd70 / +0xd78 / +0xd80 | m_SoundPound / m_SoundJiggle / m_SoundLockedAnim |
| +0xd88 | m_numCloseAttempts (only reset here; NPC code counts it) |
| +0xd8c | m_nPhysicsMaterial |
| +0xd90 / +0xd98 | m_SlaveName / m_hMaster |
| +0xda0 / +0xdb8 | m_OnBlockedClosing / m_OnBlockedOpening |
| +0xdd0 / +0xde8 | m_OnUnblockedClosing / m_OnUnblockedOpening |
| +0xe00 / +0xe18 | m_OnFullyClosed / m_OnFullyOpen |
| +0xe30 / +0xe48 | m_OnClose / m_OnOpen |
| +0xe60 / +0xe78 | m_OnLockedUse / OnAjarOpen |

### CPropDoorRotating

| Offset | Field |
|---|---|
| +0xe90 | m_vecAxis |
| +0xe9c | m_flDistance |
| +0xea0 | m_eSpawnPosition |
| +0xea4 | m_eOpenDirection (0 both, 1 forward only, 2 backward only) |
| +0xea8 / +0xeac | m_eCurrentOpenDirection / m_eDefaultCheckDirection |
| +0xeb0 / +0xeb4 | m_flAjarAngle / m_vecAjarAngles ("ajarangles") |
| +0xec0 / +0xecc / +0xed8 | m_angRotationClosed / m_angRotationOpenForward / m_angRotationOpenBack |
| +0xee4 | m_angGoal |
| +0xef0 / +0xefc | m_vecForwardBoundsMin / Max |
| +0xf08 / +0xf14 | m_vecBackBoundsMin / Max |
| +0xf20 | m_bAjarDoorShouldntAlwaysOpen |
| +0xf24 | m_hEntityBlocker |

### CPropDoorRotatingBreakable and others

| Offset | Field |
|---|---|
| +0xf30 | m_bBreakable |
| +0xf31 | whole (vfn 0x9d8 returns it; the areaportals read it) |
| +0xf34 | m_currentDamageState |
| +0xf38 / +0xf40 | m_damageStates count / model names |
| entity +0x360 | m_spawnflags |
| entity +0x318 | move-done time |
| entity +0x2c8 | m_pfnMoveDone |
| entity +0x494 / +0x490 | local time / pusher's blocker handle |
| entity +0x2f1 | NPC (1..2) |
| entity +0x3e4 | owner |
| node +0x270 -> +0x20..+0x2c | world rotation quaternion x y z w |
| +0x270 -> +0x68 -> +0x200 | the physics object |
| +0xc71 | CreateVPhysics gate (unread) |
| collision +0x18 | flags \|= 0x8000401 |
| trace +0x5d | the hit (tested for the path sweep) |
| filter +0x180 / +0x178 | interacts-with 0xc3001 / 0xc0000 |
| CBreakableProp +0xb50 | invulnerable timer |
| +0xaa8 | flags (bit 13: no damage from DMG 0x84; bit 9: the explosive delayed break) |
| +0xa88 / +0xa8c / +0xa90 / +0xa94 | the bullet / club (0x80) / blast (0x40) / burn (8) multipliers: m_flDmgModBullet / Club / Explosive / Fire (a nested struct's +0x10..+0x1c) |
| +0xb24 | m_iMinHealthDmg |
| +0xb80 | explosive delayed break |
| +0xad0 | OnBreak |
| damage info +0x70 | \|= 0x10 for DMG 0x1040 >= 40 |

## Constants

| Value | What |
|---|---|
| 1 | spawnflag start open (obsolete) |
| 0x200 | no NPCs (Spawn: vfn 0xa88(1)) |
| 0x800 | start locked |
| 0x1000 | silent |
| 0x2000 | use closes |
| 0x8000 | ignore +use (ObjectCaps 180d04fc0) |
| 0x80000 | start unbreakable |
| 0x182337ef0 / 0x182337f10 / 0x182337f40 | basis (1,0,0) / (0,-1,0) / (0,0,1) (taken) |
| 0.0027777778 | 1/360 in AngleNormalize |
| 0xe681819b | areaportal think context |
| 0x1819de460 | path sweep filter vtable |
| 0x11 (17) | entity blocker collision group; interacts-exclude 0x20000000 |
| 1200 s | nav callback think |
| 90 | distance when 0 |
| 100 | m_flSpeed when 0 |
| 0.1 | added to returndelay |
| 0.5 s | areaportals close delay |
| 300 | max gib speed |

Group 17 meets only NPC groups (vphysics2's table: Stripe(17, 0), then 17 x 20, 12 x 17, 18 x 12 only; 11 player movement copies 8, and 8 x 17 stays 0): no effect on players.

## Keyvalues (datamaps)

| Class | Key -> offset |
|---|---|
| CBasePropDoor (180cd93b0) | hardware +0xcc0, returndelay +0xca0, speed +0xd24, soundmoveoverride +0xd40, soundopenoverride +0xd48, soundcloseoverride +0xd50, soundjiggleoverride +0xd78, soundsetlockedoverride +0xd58, soundsetunlockedoverride +0xd60, soundlatchoverride +0xd68, slavename +0xd90, forceclosed +0xd10 |
| m_ls (180f15360) | soundlockedoverride -> +0xcf8, soundunlockedoverride -> +0xd00 (each only when empty) |
| CPropDoorRotating (180f018b0) | spawnpos +0xea0, opendir +0xea4, distance +0xe9c, ajarangles +0xeb4, ajarangle +0xeb0, ajardoorshouldntalwaysopen +0xf20 |

## Maps

- de_nuke 4 (metal_door_001_br, `[PR#]door_02` the master of `[PR#]door_01`, two unnamed), de_eldorado 2 (the statue's eyes, spawnflag 0x8000: no +use, opened by the map's logic_case), de_inferno 1 (break_wooden_door_01), de_cache 1 (logic_auto sends SetUnbreakable 1), de_overpass 1; ZE: ze_atix_panic_2017_p, ze_resident_evil_3.
- All: spawnflags 0x2000, opendir 0, returndelay -1, distance 89-90, speed 160-200, hardware 1.
- The eldorado eye models (models/eldorado_statue_eye_01a/b.vmdl) are in neither pak01 nor de_eldorado.vpk (CS2 loads the error model).
- prop_data: GenericGameData "prop_data" base Door.Standard (health 1000, dmg.bullets 1, dmg.club 1.25, dmg.explosive 1.5) for nuke's / overpass' / inferno's doors, Metal.Medium (health 0) for cache's.

## Spawn

### CPropDoorRotatingBreakable::Spawn (180f3bd00)

1. +0xf31 = 1; m_angRotationClosed = local angles; m_vecAxis = 1803d9c80(this, 0, 0, &axis) (the up vector); CalcOpenAngles; CBasePropDoor::Spawn.
2. Sweep bounds (180f148d0): closed -> forward into +0xef0 / +0xefc, back -> closed into +0xf08 / +0xf14.
3. Context think at 1200 s (180d60df0 with 180f183d0).
4. m_currentDamageState -1, damage states cleared; model KV "door_options" (none: skip to the end) -> "defaults" or the skin's block ("damage%d", each a model name into +0xf38).
5. m_bBreakable = !(spawnflags & 0x80000).

### GetVectors (1803d9c80)

Each basis vector u turned by q: `t = 2 (q x u)` per lane (`t.x = 2(u.z q.y - u.y q.z)`, `t.y = 2(u.x q.z - u.z q.x)`, `t.z = 2(u.y q.x - u.x q.y)`), `out.x = ((t.z q.y - t.y q.z) + w t.x) + u.x`, `out.y = (t.x q.z - t.z q.x) + (w t.y + u.y)`, `out.z = (t.y q.x - t.x q.y) + (w t.z + u.z)`.

### CalcOpenAngles (180f14800)

`d = |m_flDistance|` (0: 90), stored back; `OpenForward = closed - d x (axis.y, axis.z, axis.x)` per (pitch, yaw, roll); `OpenBack = d x axis + closed`.

### CBasePropDoor::Spawn (180d13220)

1. 180b77df0(this, 0, 2, 0); move type PUSH; collision +0x18 |= 0x8000401 (when not all set, with the change notify vfn 0x5e0).
2. m_closedPosition = vfn 0x2c8, m_closedAngles = abs angles; vfn 0xa68; 180bc5d40 / 180ba23f0.
3. m_vecLatchWorldPosition = collision bounds' centre in x and z with an edge in y (180f22e80), turned by the node's transform.
4. 0x800: m_bLocked; 0x200: vfn 0xa88(1) (SetNoNPCs); m_flSpeed 0: 100.
5. Hardware bodygroup (180b746f0(180b522b0(this, 1), m_nHardwareType)); "Unlocked prop_door ... has no hardware" warning.
6. 180b49710(this, +0xa40 == 0); m_hBlocker none, m_bFirstBlocked 0.
7. A model: vfn 0xa18(model, kv), moving sound handle cleared; none: Plat_FatalError "prop_door with no model".

### Start position (vfn 0xa68, 180f18210)

Spawnflag 1 or spawnpos 1: OpenForward, open; spawnpos 2: OpenBack, open; spawnpos 3 (ajar): m_flAjarAngle != 0: vfn 0xad8 + a quaternion blend, else m_vecAjarAngles, ajar; else closed. SetLocalAngles.

### Sounds (vfn 0xa18, 180ce8380)

1. KV "door_sounds" missing (every baked door model): the empty ones of m_SoundOpen "DoorMetal.FullyOpened", m_SoundClose "DoorMetal.FullyClosed", m_SoundMoving "DoorMetal.PhysMovementLp", m_SoundLatch "DoorMetal.HandleLatch", m_SoundJiggle "DoorMetal.DoorJiggle", m_SoundLockedAnim "DoorMetal.HandleAutoJiggle", m_ls locked "DoorMetal.HandleJiggle", m_ls unlocked "DoorHandles.Unlocked1"; then "door_options" (the skin%d block's open / close / move / pound / jiggle / surfaceprop, the hardware%d block's locked / unlocked / lock / unlock / latch, "defaults" for the missing ones).
2. "door_sounds" present: opened / closed / move / jiggle / locked / locked_anim / latch / unlatch / lock / unlock.
3. Each still empty (180fec9a0): "DoorSound.Null" (moving, open, close, both m_ls, latch, jiggle), "WoodenDoor.Lock" (lock, unlock), "WoodenDoor.Pound" (pound).

### Activate (180ce0310)

180b964a0; the areaportals (open while not closed); with a targetname: every entity named m_SlaveName (else its own name), each a CBasePropDoor other than this: type 2 (restore): join m_hDoorList when its owner (+0x3e4) is this; else, when its own door list is empty: join m_hDoorList, its m_hMaster = this (when not already), vfn 0x1b0(it, this) (its owner).

### CreateVPhysics (180ba1030)

With +0xc71: 180d0f740(collision, motion 3 keyframed, group 4, interacts-with 0xc3001), then 180cee2e0(collision).

## Use and the state machine

- Use (180d19800): with m_hMaster, the master's Use; else PlayerUse (activator, caller, 3).
- PlayerUse (180d16590):
  1. m_hBlocker set and closing: m_hActivator = activator; (not opening / open) opening, m_pfnMoveDone OnDoorOpened, BeginOpening(the blocker). Done.
  2. Closed: locked (vfn 0x9e0 = m_bLocked) or (vfn 0x9e8 = !m_bNoNPCs false and the activator an NPC): vfn 0xa38, done. Else vfn 0xa40; then (from case open) open and vfn 0x9f8(0): DoorClose, done. Away = m_hActivator; ajar: the moving sound, OnAjarOpen (m_hActivator).
  3. Open: 0x2000 clear: nothing; else case 2's path (path blocked: nothing, stays open).
  4. Opening: 0x2000 clear: nothing; else m_hActivator = activator, DoorClose.
  5. Closing: m_hActivator = activator, away = it.
  6. Ajar: m_hActivator = activator; vfn 0x9f0(it) false: DoorClose; else away = it, the moving sound, OnAjarOpen.
  7. Then (LAB_180d16afc) not opening / open: opening, m_pfnMoveDone OnDoorOpened, BeginOpening(away), and from closed vfn 0xaa0(away, 1).
- vfn 0xa38 (180d05440): PlayLockSounds(this, &m_ls, 1, 0, &latch), OnLockedUse (activator, caller).
- vfn 0xa40 (180d065c0): m_hActivator = activator; closed: PlayLockSounds(.., 0, ..).
- vfn 0x9f0 (180f115a0): m_bAjarDoorShouldntAlwaysOpen: `180f22c60 != (0 <= AngleNormalize(abs yaw - closed yaw))`; else true.
- vfn 0x9f8 (180f17fb0): a master's own; else each slave its path sweep (the side argument an unset register), a false one false; then this door's: any -> side 2 (both), else the goal's side (`18014a300(goal, OpenForward) ^ 1`).
- DoorOpen (180cf07d0): ajar: the moving sound (vfn 0xaa8), OnAjarOpen (m_hActivator); not opening / open: opening, m_pfnMoveDone OnDoorOpened, BeginOpening(away), from closed vfn 0xaa0(away, 1).
- vfn 0xaa0 (180d05a90): 180d17f10(this, 1); sound and not silent: the moving sound; event "door_open" (userid: m_hActivator when a player, entindex); OnOpen (m_hActivator, this); each slave: its m_hActivator = ours, DoorOpen(away).
- DoorClose (180cf01f0): closed or closing: nothing. Not silent: the moving sound; closing; m_pfnMoveDone OnDoorClosed; BeginClosing; event "door_close"; OnClose (this, this); each slave's DoorClose.
- BeginOpening (180f122e0): side = GetOpenAngles(away, &goal), SetOpenDirection(away, side), MoveTo(goal, m_flSpeed).
- BeginClosing (180f12070): an entity blocker: the path sweep of the goal's side: blocked -> its collision on (180cf1540); the debug overlay; then MoveTo(the closed angles, m_flSpeed).

### GetOpenAngles (180f14ac0)

1. side = m_eDefaultCheckDirection (1: back, else forward), its angles. opendir 1: forward (0); 2: back (1).
2. Both: with `away`: `180f22c60(this, away) == (0 <= AngleNormalize(OpenForward.yaw - the local yaw))`: back, side 1.
3. m_hBlocker set: done. Else m_hActivator a player (vfn 0x558) and `away` a player and 180f14e50(side) false: the other side's angles; 180f14e50(other) false too: the first side's again.

- 180f22c60: a = (WorldSpaceCenter - abs origin) in 2D, b = (other's abs origin - the door's) in 2D, each normalized (length `sqrt(y^2 + 0 + x^2)`; outside [1e-17, 1e17]: 1814738b0, 0 for 0); returns `0 <= b.y a.x - b.x a.y`.
- AngleNormalize (1801fe910): outside [-180, 180]: `v - floor(v x 0.0027777778 + 0.5) x 360`, held to [-180, 180].

### SetOpenDirection (180f15f40)

The side's bounds; the old entity blocker removed; a new one 180d3f2f0(abs origin, min, max, away, 0), m_hEntityBlocker; debug box (half extent the largest |lane|); its collision group 0x11, interacts-exclude 0x20000000; the path sweep of the side clear: its collision off.

### Path sweep (180f14e50)

Side 0 the forward bounds, 1 the back, else per lane min / max of both; a box shape traced from the abs origin to itself (filter vtable 0x1819de460, interacts-with 0xc3001 in +0x180, 0xc0000 in +0x178, the door's entity id and its owner's ignored); a hit (+0x5d) not in the door's hierarchy and not its entity blocker (vfn 0xae0, roots compared): false (blocked); else true.

### Sweep bounds (180f148d0)

The physics object; each angle to a quaternion, times the parent's when parented; vphysics vfn 0xb0(the transform at the origin, out AABB) for each, min / max per lane. No physics object: zeros.

### MoveTo / MoveDone

- MoveTo (180f11a00): m_angGoal = goal; already there (exact): MoveDone now; else `delta = goal - angles`, `t = |delta| / speed` (no 0.01 floor, unlike CBaseToggle's AngularMove), SetMoveDoneTime(t), local angular velocity = `delta x (1 / t)`.
- MoveDone (180f2d9b0): Teleport(0, &m_angGoal, 0) (vfn 0x528), local angular velocity 0, SetMoveDoneTime(-1), m_pfnMoveDone.
- OnDoorOpened (180cf08e0): m_hBlocker none, m_bFirstBlocked 0; moving sound stopped; not silent: m_SoundOpen (at the origin); open; returndelay != -1: vfn 0xa20; OnFullyOpen (this, this); vfn 0xa28; close attempts > 0: collision function mask bit 0 back on, count 0; m_hActivator none.
- OnDoorClosed (180cf0470): m_hBlocker none, m_bFirstBlocked 0; moving sound stopped; not silent: m_SoundClose (at the latch); closed; event "door_closed"; OnFullyClosed (m_hActivator, this); context think in 0.5 s (areaportals closed); vfn 0xa30; close attempts as above; m_hActivator none.
- vfn 0xa20 (180d0df50): `t = returndelay + 0.1`, move-done time `t + local time` (-1 when t < 0); m_pfnMoveDone 180cf0110. 180cf0110: vfn 0x9f8(1) true: DoorClose; returndelay -1: 1803eb9e0(think); else the same move-done time again.
- Moving sound (180d156f0): not silent and no handle (+0xd28 0): m_SoundMoving at the origin, handle kept.
- Areaportals (180d17f10(this, open)): the 0xe681819b think cleared; open forced while +0xf31 is false; every func_areaportal whose target is this door's name: its Use with (open).

## Inputs

- vfn 0xa98 (180d06710): not locked; vfn 0x9e8 or the activator no NPC; not opening / open: from closed vfn 0xa40, then DoorOpen(away).
- Lock (180d008a0): m_bLocked 1; with sound: m_SoundLock at the latch, on every slave too. Unlock (180d17190): the no-hardware warning; m_bLocked 0; m_SoundUnlock the same way.
- SetNoNPCs.

## Blocking

PerformPush keeps the blocker in +0x490: a new one -> EndBlocked on the old, StartBlocked with the new; every blocked tick Blocked. An unblocked push sets it none (EndBlocked).

- StartBlocked (180d151f0): m_bFirstBlocked 1; a master: its 180d00d20(other) (each slave, then the master: not first-blocked: vfn 0xa58 (stopped); m_hBlocker = other (none: m_bFirstBlocked 0); moving sound stopped; OnBlockedClosing while closing, else OnBlockedOpening, activator other); else the same for this door alone without the stop.
- EndBlocked (180cf1bf0): a master's; else each slave not first-blocked vfn 0xa60; not silent: the moving sound; OnUnblockedClosing while closing, else OnUnblockedOpening, activator this; this one not first-blocked: vfn 0xa60.
- Blocked (180ce3a30): only with m_bForceClosed: a VPHYSICS (move type 5) blocker not taking damage: 180e78760(this, other, 1, 4.0); one taking damage: its own health as damage. A player: nothing (the door waits).

## Breaking

- vfn 0x7f0 (180f30060): not breakable: no damage (1). DMG 0x1040 and >= 40: info +0x70 |= 0x10. Then CBreakableProp's (180bbe860): invulnerable timer: none; DMG 0x84 with +0xaa8 bit 13: none; bullets (2) x m_flDmgModBullet, 0x800 x 2 x it; club (0x80) x +0xa8c; blast (0x40) x +0xa90; burn (8) x +0xa94; crush + slash (5) x 10; 0x58000: 0; under m_iMinHealthDmg: none; the explosive delayed break (+0xb80, +0xaa8 bit 9); then the base's (180b67140).
- vfn 0x7f8 (180f30090): CBreakableProp's (180bbeca0), then with damage states: stage = health per state (vfn 0x5c8 max health / (count + 1)); a later one: +0xf31 0, the areaportals, the stage models ("models/%s.vmdl").
- vfn 0x418 (180f19590): damage states left spawned as gibs (181121570, velocity from the damage force, 300 at most), areaportals open (closed doors), OnBreak (+0xad0), then CBreakableProp's (180bad480).

## Unread

- 180f22e80 (the latch's y edge); 180b77df0 / 180b49710 in Spawn.
- The ajar start with ajarangle != 0 (vfn 0xad8, the blend).
- m_eDefaultCheckDirection's keyvalue.
- PlayerOpen / PlayerClose (180cfd6c0 / 180cfd5a0); the hardware bodygroup; 1803eb9e0.
- 180f17fb0's slave side argument.
- The path sweep's filter object (vtable 0x1819de460): what it lets through.
- +0xc71 and what 180cee2e0 leaves after CreateVPhysics.
- CBreakableProp's health rule (prop_data over the keyvalue health, 180bc5d40 / 180ba23f0) and break pieces (BreakPieceList).
