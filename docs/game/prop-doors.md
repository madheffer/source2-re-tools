# prop_door_rotating (CPropDoorRotatingBreakable <- CPropDoorRotating <- CBasePropDoor, server.dll 2026-11-05)

Ported: web/src/world/entities/classes/prop-door.js (the state machine, sounds, inputs, blocking, damage) and
prop-door-geom.js (the axis, the open angles, the sweep bounds, the path sweep, the side pick); checked by
prop-door-test.mjs beside them. FEATURES "prop_door_rotating".

The designer name **prop_door_rotating is CPropDoorRotatingBreakable** (tools/re/game/inputs.py: its chain
CPropDoorRotatingBreakable > CPropDoorRotating > CBasePropDoor > CDynamicProp > CBreakableProp > CBaseProp >
CBaseAnimGraph > CBaseModelEntity > CBaseEntity). The official maps use it for their model doors: de_nuke 4
(metal_door_001_br, `[PR#]door_02` the master of `[PR#]door_01`, two unnamed), de_eldorado 2 (the statue's eyes,
spawnflag 0x8000: no +use, opened by the map's logic_case), de_inferno 1 (break_wooden_door_01), de_cache 1 (its
logic_auto sends SetUnbreakable 1), de_overpass 1; ZE maps too (ze_atix_panic_2017_p, ze_resident_evil_3). All have
spawnflags 0x2000 (use closes), opendir 0 (both ways), returndelay -1, distance 89-90, speed 160-200, hardware 1.
The eldorado eye models (models/eldorado_statue_eye_01a/b.vmdl) are in neither pak01 nor de_eldorado.vpk: no body,
no bounds here (CS2 itself loads the error model).

Vtables (tools/re/game/rtti.py): CPropDoorRotatingBreakable 1819dd938, CPropDoorRotating 1819dce10, CBasePropDoor
181965e80 (tools/re/game/vtdump.py of both and a slot compare: the overrides below).

## Fields (tools/re/game/schema.py)

CBasePropDoor: m_flAutoReturnDelay +0xca0, m_hDoorList +0xca8 (count) / +0xcb0 (handles), m_nHardwareType +0xcc0,
m_bNeedsHardware +0xcc4, m_eDoorState +0xcc8 (0 closed, 1 opening, 2 open, 3 closing, 4 ajar), m_bLocked +0xccc,
m_bNoNPCs +0xccd, m_closedPosition +0xcd0, m_closedAngles +0xcdc, m_hBlocker +0xce8, m_bFirstBlocked +0xcec, m_ls
+0xcf0 (locksound_t: +8 locked sound +0xcf8, +0x10 unlocked +0xd00, +0x18 the next time +0xd08), m_bForceClosed
+0xd10, m_vecLatchWorldPosition +0xd14, m_hActivator +0xd20, m_flSpeed +0xd24, the moving sound's handle +0xd28 (5
dwords to +0xd38), m_SoundMoving +0xd40, m_SoundOpen +0xd48, m_SoundClose +0xd50, m_SoundLock +0xd58, m_SoundUnlock
+0xd60, m_SoundLatch +0xd68, m_SoundPound +0xd70, m_SoundJiggle +0xd78, m_SoundLockedAnim +0xd80, m_numCloseAttempts
+0xd88, m_nPhysicsMaterial +0xd8c, m_SlaveName +0xd90, m_hMaster +0xd98; outputs (the output table 180d08da0)
m_OnBlockedClosing +0xda0, m_OnBlockedOpening +0xdb8, m_OnUnblockedClosing +0xdd0, m_OnUnblockedOpening +0xde8,
m_OnFullyClosed +0xe00, m_OnFullyOpen +0xe18, m_OnClose +0xe30, m_OnOpen +0xe48, m_OnLockedUse +0xe60, **OnAjarOpen
+0xe78**.
CPropDoorRotating: m_vecAxis +0xe90, m_flDistance +0xe9c, m_eSpawnPosition +0xea0, m_eOpenDirection +0xea4 (0 both,
1 forward only, 2 backward only), m_eCurrentOpenDirection +0xea8, m_eDefaultCheckDirection +0xeac, m_flAjarAngle
+0xeb0, m_vecAjarAngles +0xeb4 ("ajarangles"), m_angRotationClosed +0xec0, m_angRotationOpenForward +0xecc,
m_angRotationOpenBack +0xed8, m_angGoal +0xee4, m_vecForwardBoundsMin / Max +0xef0 / +0xefc, m_vecBackBoundsMin /
Max +0xf08 / +0xf14, m_bAjarDoorShouldntAlwaysOpen +0xf20, m_hEntityBlocker +0xf24.
CPropDoorRotatingBreakable: m_bBreakable +0xf30, +0xf31 (whole: vfn 0x9d8 returns it, the areaportals read it),
m_currentDamageState +0xf34, m_damageStates +0xf38 (count) / +0xf40 (model names).
CBaseEntity: m_spawnflags +0x360; the move-done time +0x318; m_pfnMoveDone +0x2c8; the local time +0x494; the
pusher's blocker handle +0x490.

Spawnflags: 1 start open (obsolete), 0x200 no NPCs (Spawn: vfn 0xa88(1), m_bNoNPCs), 0x800 start locked, 0x1000
silent, 0x2000 use closes, 0x8000 ignore +use (ObjectCaps 180d04fc0), 0x80000 start unbreakable.

## Keyvalues (the datamaps)

CBasePropDoor (180cd93b0): hardware +0xcc0, returndelay +0xca0, speed +0xd24, soundmoveoverride +0xd40,
soundopenoverride +0xd48, soundcloseoverride +0xd50, soundjiggleoverride +0xd78, soundsetlockedoverride +0xd58,
soundsetunlockedoverride +0xd60, soundlatchoverride +0xd68, slavename +0xd90, forceclosed +0xd10. m_ls (180f15360,
from Precache 180d07c10): soundlockedoverride -> +0xcf8, soundunlockedoverride -> +0xd00, each only when empty.
CPropDoorRotating (180f018b0): spawnpos +0xea0, opendir +0xea4, distance +0xe9c, ajarangles +0xeb4, ajarangle +0xeb0,
ajardoorshouldntalwaysopen +0xf20.

## Spawn

- **CPropDoorRotatingBreakable::Spawn** (slot 0x48, 180f3bd00): +0xf31 = 1; m_angRotationClosed = the local angles;
  m_vecAxis = 1803d9c80(this, 0, 0, &axis); CalcOpenAngles (vfn 0xad0); CBasePropDoor::Spawn; the sweep bounds
  (180f148d0: closed -> forward into +0xef0 / +0xefc, back -> closed into +0xf08 / +0xf14); a context think at 1200 s
  (180d60df0 with 180f183d0: a bool callback, true for a door named "checkpoint_exit", else not locked: the nav's
  passable test, not ported); m_currentDamageState -1, the damage states cleared; the model's KV "door_options"
  (none: skip to the end) -> "defaults" or the skin's block (FUN_180f3e840 "damage%d", 1 up: each a model name into
  +0xf38); last m_bBreakable = !(spawnflags & 0x80000). CPropDoorRotating::Spawn (180f3bbd0) is the same without the
  breakable parts.
- **1803d9c80(this, fwd*, right*, up*)**: GetVectors off the node's world rotation (+0x270 -> +0x20..+0x2c, a
  quaternion x y z w; the node's +0xf4 dirty flag refreshes it, 180bec940), each a basis vector (0x182337ef0 /
  0x182337f10 / 0x182337f40, filled at startup: (1,0,0) / (0,-1,0) / (0,0,1) taken) turned: t = 2 (q x u) per lane
  (t.x = 2(u.z q.y - u.y q.z), t.y = 2(u.x q.z - u.z q.x), t.z = 2(u.y q.x - u.x q.y)), out.x = ((t.z q.y - t.y q.z) +
  w t.x) + u.x, out.y = (t.x q.z - t.z q.x) + (w t.y + u.y), out.z = (t.y q.x - t.x q.y) + (w t.z + u.z). The axis is
  the up vector.
- **CalcOpenAngles** (vfn 0xad0, 180f14800): d = |m_flDistance| (0: 90), stored back; OpenForward = closed - d x
  (axis.y, axis.z, axis.x) per (pitch, yaw, roll); OpenBack = the same added (d x axis + closed).
- **CBasePropDoor::Spawn** (180d13220): 180b77df0(this, 0, 2, 0); move type PUSH (1803eb7d0(6)); the collision's
  +0x18 flags |= 0x8000401 (when not all set, with the collision's change notify vfn 0x5e0); m_closedPosition =
  vfn 0x2c8, m_closedAngles = the abs angles (1803d6de0); vfn 0xa68 (the start position); 180bc5d40 / 180ba23f0
  (CBreakableProp / CDynamicProp's: the prop data, not read); m_vecLatchWorldPosition = the collision bounds' centre
  in x and z with an edge in y (180f22e80 picks min or max y: not read), turned by the node's transform (180ceaad0);
  spawnflag 0x800: m_bLocked; 0x200: vfn 0xa88(1) (SetNoNPCs: m_bNoNPCs +0xccd); m_flSpeed 0: 100; the hardware
  bodygroup (180b746f0(180b522b0(this, 1), m_nHardwareType)); "Unlocked prop_door ... has no hardware" warning;
  180b49710(this, +0xa40 == 0); m_hBlocker none, m_bFirstBlocked 0; a model: vfn 0xa18(model, kv) (the sounds) and
  the moving sound's handle cleared; no model: Plat_FatalError "prop_door with no model".
- **vfn 0xa68** (180f18210, the start position): spawnflag 1 or spawnpos 1: OpenForward, open; spawnpos 2: OpenBack,
  open; spawnpos 3 (ajar): m_flAjarAngle != 0: vfn 0xad8 + a quaternion blend (18146bb60 / 181475ab0 / 18146fe70 /
  181473410: not read) else m_vecAjarAngles, ajar; else closed; SetLocalAngles (1803eb070).
- **vfn 0xa18** (180ce8380, the sounds): the model's KV "door_sounds" missing (every baked door model): the empty
  ones of m_SoundOpen "DoorMetal.FullyOpened", m_SoundClose "DoorMetal.FullyClosed", m_SoundMoving
  "DoorMetal.PhysMovementLp", m_SoundLatch "DoorMetal.HandleLatch", m_SoundJiggle "DoorMetal.DoorJiggle",
  m_SoundLockedAnim "DoorMetal.HandleAutoJiggle", m_ls locked "DoorMetal.HandleJiggle", m_ls unlocked
  "DoorHandles.Unlocked1"; then "door_options" (none on the baked models: the skin%d block's open / close / move /
  pound / jiggle / surfaceprop, the hardware%d block's locked / unlocked / lock / unlock / latch, the "defaults" block
  for the missing ones); "door_sounds" present instead: opened / closed / move / jiggle / locked / locked_anim / latch
  / unlatch / lock / unlock. Last, each still empty (180fec9a0): "DoorSound.Null" (moving, open, close, both m_ls,
  latch, jiggle), "WoodenDoor.Lock" (lock, unlock), "WoodenDoor.Pound" (pound).
- **Activate** (slot 0x68, 180ce0310(this, type)): 180b964a0 (the base's); the areaportals (180d17f10, open while
  not closed); with a targetname: every entity named m_SlaveName (else its own name; 18137ab40 / 181384da0 /
  181389390 the name iterator), each a CBasePropDoor (1816b6d80 dynamic_cast) other than this: type 2 (a restore):
  join m_hDoorList when its owner (+0x3e4) is this; else, when its own door list is empty: join m_hDoorList, its
  m_hMaster = this (when not already), vfn 0x1b0(it, this) (its owner).
- **CreateVPhysics** (slot 0x238, 180ba1030, CBaseAnimGraph's chain): with +0xc71: 180d0f740(collision, motion 3
  keyframed, group 4, interacts-with 0xc3001) then 180cee2e0(collision) (TODO: what +0xc71 is and what 180cee2e0
  leaves; rubikon BrushPhysics.cs gives the door CDynamicProp's record).
- **ObjectCaps** (180d04fc0): caps.js propDoorCaps.

## Use and the state machine

- **Use** (vfn 0x498, 180d19800): with a master (m_hMaster), the master's Use; else PlayerUse (vfn 0xa90) with
  (activator, caller, 3).
- **PlayerUse** (vfn 0xa90, 180d16590):
  1. m_hBlocker set and closing: m_hActivator = the activator; (not opening / open) opening, m_pfnMoveDone
     OnDoorOpened, BeginOpening(the blocker). Done.
  2. Closed: locked (vfn 0x9e0 = m_bLocked) or (vfn 0x9e8 = !m_bNoNPCs false and the activator an NPC: +0x2f1 1..2):
     vfn 0xa38 and done. Else vfn 0xa40; then (from case open) open and vfn 0x9f8(0) (the close path clear):
     DoorClose, done. Away = m_hActivator; ajar: the moving sound, OnAjarOpen (m_hActivator).
  3. Open: spawnflag 0x2000 clear: nothing; else case 2's path (with the open state its close test applies; the path
     blocked: nothing happens, the state stays open).
  4. Opening: spawnflag 0x2000 clear: nothing; else m_hActivator = the activator, DoorClose.
  5. Closing: m_hActivator = the activator, away = it.
  6. Ajar: m_hActivator = the activator; vfn 0x9f0(it) false: DoorClose; else away = it, the moving sound, OnAjarOpen.
  Then (LAB_180d16afc) not opening / open: opening, m_pfnMoveDone OnDoorOpened, BeginOpening(away), and from closed
  vfn 0xaa0(away, 1).
- **vfn 0xa38** (180d05440, locked use): PlayLockSounds(this, &m_ls, 1, 0, &latch) (180d55fd0), OnLockedUse
  (activator, caller).
- **vfn 0xa40** (180d065c0, unlocked use): m_hActivator = the activator; closed: PlayLockSounds(.., 0, ..).
- **vfn 0x9f0** (180f115a0): m_bAjarDoorShouldntAlwaysOpen: 180f22c60 != (0 <= AngleNormalize(abs yaw - closed
  yaw)); else true.
- **vfn 0x9f8** (180f17fb0(this, any)): a master's own; else each slave (dynamic_cast) its path sweep (the side
  argument an unset register: TODO), a false one false; then this door's: any -> side 2 (both), else the goal's side
  (18014a300(goal, OpenForward) ^ 1).
- **DoorOpen** (180cf07d0(this, away)): ajar: the moving sound (vfn 0xaa8), OnAjarOpen (m_hActivator); not opening /
  open: opening, m_pfnMoveDone OnDoorOpened, BeginOpening(away), from closed vfn 0xaa0(away, 1).
- **vfn 0xaa0** (180d05a90(away, sound)): 180d17f10(this, 1) (the areaportals, below); sound and not silent: the
  moving sound; the "door_open" event (userid: m_hActivator when a player, entindex); OnOpen (m_hActivator, this);
  each slave: its m_hActivator = ours, DoorOpen(away).
- **DoorClose** (180cf01f0): closed or closing: nothing. Not silent: the moving sound; closing; m_pfnMoveDone
  OnDoorClosed (180cf0470); BeginClosing (vfn 0xa50); the "door_close" event; OnClose (this, this); each slave's
  DoorClose.
- **BeginOpening** (vfn 0xa48, 180f122e0(away)): side = GetOpenAngles(away, &goal) (vfn 0xab8), SetOpenDirection(away,
  side) (vfn 0xac0), MoveTo(goal, m_flSpeed) (vfn 0xac8).
- **BeginClosing** (vfn 0xa50, 180f12070): an entity blocker: the path sweep of the goal's side (18014a300(goal,
  OpenForward) ^ 1): blocked: its collision on (180cf1540: function mask |= 7); the debug overlay; then MoveTo(the
  closed angles, m_flSpeed).
- **GetOpenAngles** (vfn 0xab8, 180f14ac0(this, away, out)) -> the side: side = m_eDefaultCheckDirection (1: back,
  else forward), its angles. opendir 1: forward (0); 2: back (1). Both: with `away`: 180f22c60(this, away) ==
  (0 <= AngleNormalize(OpenForward.yaw - the local yaw)) (1802f6c00(angles, 1) the yaw, 1801fe910 AngleNormalize):
  back, side 1. Then m_hBlocker set: done; else m_hActivator a player (vfn 0x558) and `away` a player and
  180f14e50(side) false: the other side's angles, and 180f14e50(other) false too: the first side's again.
- **180f22c60(this, other)**: a = (vfn 0x2c8 WorldSpaceCenter - the abs origin) in 2D, b = (other's abs origin - the
  door's) in 2D, each normalized (length sqrt(y^2 + 0 + x^2); outside [1e-17, 1e17]: 1814738b0, 0 for 0); returns
  0 <= b.y a.x - b.x a.y.
- **1801fe910 AngleNormalize**: outside [-180, 180]: v - floor(v x 0.0027777778 + 0.5) x 360, held to [-180, 180].
- **SetOpenDirection** (vfn 0xac0, 180f15f40(this, away, side)): the side's bounds; the old entity blocker removed
  (180c30c10); a new one: 180d3f2f0(abs origin, min, max, away, 0) (CEntityBlocker), m_hEntityBlocker; the debug
  box (half extent the largest |lane|); its collision group 0x11 (180d0e200), interacts-exclude 0x20000000
  (180cf1730); the path sweep of the side clear: its collision off (180cee2e0). **Group 17 meets only NPC groups**
  (vphysics2's table, rubikon CollisionGroupTable.cs: Stripe(17, 0), then 17 x 20, 12 x 17, 18 x 12 only; 11 player
  movement copies 8, and 8 x 17 stays 0): no effect on players, not ported.
- **The path sweep** (180f14e50(this, side)): side 0 the forward bounds, 1 the back, else per lane min (1801783c0) /
  max (1801783b0) of both; a box shape (18021a5d0) traced from the abs origin to itself (180c2f3c0, the filter object
  vtable 0x1819de460, interacts-with 0xc3001 in +0x180, 0xc0000 in +0x178, the door's entity id and its owner's
  (180bf9270) ignored); a hit (+0x5d) not in the door's hierarchy (180e8e250) and not its entity blocker (vfn 0xae0,
  1803d9980 roots compared): false (blocked); else true.
- **The sweep bounds** (180f148d0(this, angA, angB, min*, max*)): the physics object (+0x270 -> +0x68 -> +0x200); each
  angle to a quaternion (181473e90), times the parent's (1803d9790, 181475200) when parented; vphysics vfn 0xb0(the
  transform at the origin, out AABB) for each, min / max per lane. No physics object: zeros.
- **MoveTo** (vfn 0xac8, 180f11a00): m_angGoal = goal; already there (18014a300, exact): MoveDone now; else delta =
  goal - angles, t = |delta| / speed (|v| = sqrt((x^2 + y^2) + z^2), 180a48c80; no 0.01 floor, unlike CBaseToggle's
  AngularMove), SetMoveDoneTime(t), local angular velocity = delta x (1 / t).
- **MoveDone** (vfn 0x4f8, 180f2d9b0): Teleport(0, &m_angGoal, 0) (vfn 0x528), the local angular velocity 0
  (1803eb140), SetMoveDoneTime(-1), m_pfnMoveDone. vfn 0x628 (180d1b7a0): true (the pusher adds Euler steps).
- **OnDoorOpened** (180cf08e0): m_hBlocker none, m_bFirstBlocked 0; the moving sound stopped (vfn 0xab0, 180d159d0:
  the handle's sound stopped, the 5 dwords cleared); not silent: m_SoundOpen (vfn 0xa80, at the origin); open;
  returndelay != -1: vfn 0xa20; OnFullyOpen (this, this); vfn 0xa28 (180f2e800: the entity blocker's collision off);
  close attempts > 0: the collision's function mask bit 0 back on and the count 0; m_hActivator none.
- **OnDoorClosed** (180cf0470): m_hBlocker none, m_bFirstBlocked 0; the moving sound stopped; not silent: m_SoundClose
  (at the latch); closed; the "door_closed" event; OnFullyClosed (m_hActivator, this); a context think in 0.5 s
  (LAB_180cee380 = 180d17f10(this, 0), context 0xe681819b: the areaportals closed); vfn 0xa30 (180f2e620: the entity
  blocker removed); the close attempts as above; m_hActivator none.
- **vfn 0xa20** (180d0df50, the auto return): t = returndelay + 0.1, the move-done time t + the local time (-1 when t
  < 0); m_pfnMoveDone 180cf0110. **180cf0110**: vfn 0x9f8(1) true: DoorClose; returndelay -1: 1803eb9e0(think) (not
  read); else the same move-done time again.
- **The moving sound** (vfn 0xaa8, 180d156f0): not silent and no handle (+0xd28 0): m_SoundMoving (vfn 0xa80 at the
  origin), its handle kept (the sound's position follows the origin: 180c84870).
- **vfn 0xa80** (180cf12c0(this, out, name, atLatch)): EmitSound at the abs origin, or at m_vecLatchWorldPosition.
- **180d17f10(this, open)** (the areaportals): the 0xe681819b context think cleared; open forced while vfn 0x9d8
  (+0xf31, whole) is false; every func_areaportal whose target is this door's name: its Use with (open).
  Not ported (no areaportals here).

## The inputs

CBasePropDoor_API: Open 180cc2f90 (vfn 0xa98(activator, 0)), OpenAwayFrom 180cc3110 (the named entity, 180bfc940 with
the activator / caller), OpenAwayFromActivator 180cc3210 (m_flSpeed = the float parameter for the call, then back;
vfn 0xa98(activator, activator)), Close 180cc3350 (not closed: OnClose (activator, this), then DoorClose, which fires
OnClose again), Toggle 180cc33f0 (closed and not locked: DoorOpen(0); open: DoorClose), Lock 180cc34a0 (vfn 0xa70(1)),
Unlock 180cc3520 (vfn 0xa78(1)), PlayerOpen 180cc35a0 / PlayerClose 180cc3640 (180cfd6c0 / 180cfd5a0: not read),
SetNoNPCs. CPropDoorRotating_API: SetRotationDistance 180ef83c0 (m_flDistance, CalcOpenAngles, both sweep bounds
from the local angles), SetSpeed 180ef93b0 (m_flSpeed, then vfn 0xa60). CPropDoorRotatingBreakable_API:
SetUnbreakable 180efab40 / SetBreakable 180efba90 (m_bBreakable 0 / 1).
- **vfn 0xa98** (180d06710(activator, away)): not locked; vfn 0x9e8 or the activator no NPC; not opening / open: from
  closed vfn 0xa40, then DoorOpen(away).
- **Lock** (vfn 0xa70, 180d008a0(sound)): m_bLocked 1; with sound: m_SoundLock at the latch, on every slave too.
  **Unlock** (vfn 0xa78, 180d17190): the no-hardware warning; m_bLocked 0; m_SoundUnlock the same way.
- vfn 0xa58 (180f181e0): the local angular velocity 0, SetMoveDoneTime(-1). vfn 0xa60 (180f181c0): MoveTo(m_angGoal,
  m_flSpeed).

## Blocking

PerformPush (180e8d810, docs/game/push.md) keeps the blocker in +0x490: a new one -> EndBlocked (vfn 0x4e0) on the
old, StartBlocked (vfn 0x4d0) with the new; every blocked tick Blocked (vfn 0x4d8). A push that runs unblocked sets
it none (EndBlocked).
- **StartBlocked** (vfn 0x4d0, 180d151f0(other)): m_bFirstBlocked 1; a master: its 180d00d20(other) (each slave, then
  the master: not first-blocked: vfn 0xa58 (stopped); m_hBlocker = other (none: m_bFirstBlocked 0); the moving
  sound stopped; OnBlockedClosing (+0xda0) while closing, else OnBlockedOpening (+0xdb8), activator other); else the
  same for this door alone without the stop.
- **EndBlocked** (vfn 0x4e0, 180cf1bf0): a master's; else each slave not first-blocked vfn 0xa60; not silent: the
  moving sound; OnUnblockedClosing (+0xdd0) while closing, else OnUnblockedOpening (+0xde8), activator this; this one
  not first-blocked: vfn 0xa60.
- **Blocked** (vfn 0x4d8, 180ce3a30(other)): only with m_bForceClosed: a VPHYSICS (move type 5) blocker not taking
  damage: 180e78760(this, other, 1, 4.0) (a push); one taking damage: its own health as damage (180fba3a0 / 1803ed610).
  A player: nothing (the door waits).
- m_numCloseAttempts (+0xd88) is only ever reset here (the NPC code counts it).

## Breaking

- **vfn 0x7f0** (180f30060, OnTakeDamage): not breakable: no damage (1). DMG 0x1040 and >= 40: the info's +0x70 |=
  0x10. Then CBreakableProp's (180bbe860): an invulnerable timer (+0xb50): none; DMG 0x84 with +0xaa8 bit 13: none;
  bullets (2) x m_flDmgModBullet (+0xa88), 0x800 x 2 x it; club (0x80) x +0xa8c; blast (0x40) x +0xa90; burn (8) x
  +0xa94; crush + slash (5) x 10; 0x58000: 0; under m_iMinHealthDmg (+0xb24): none; the explosive delayed break
  (+0xb80, +0xaa8 bit 9); then the base's (180b67140).
- **vfn 0x7f8** (180f30090, OnTakeDamage alive): CBreakableProp's (180bbeca0), then with damage states: the stage =
  health per state (vfn 0x5c8 max health / (count + 1)), a later one: +0xf31 0, the areaportals, the stage models
  (180b75df0 "models/%s.vmdl").
- **vfn 0x418** (180f19590, the break): the damage states left spawned as gibs (181121570, velocity from the damage
  force, 300 at most), the areaportals open (closed doors), OnBreak (+0xad0), then CBreakableProp's (180bad480).
- prop_data: the models' GenericGameData "prop_data" with base Door.Standard (scripts/propdata.vdata_c: health 1000,
  dmg.bullets 1, dmg.club 1.25, dmg.explosive 1.5) for nuke's / overpass' / inferno's doors, Metal.Medium (health 0)
  for cache's (web/src/cs2web/data/door-props.js, tools/door-props.mjs). The rule that takes it over the keyvalue
  health (180bc5d40 / 180ba23f0) isn't read.

## Still not read (the stand-ins in prop-door.js)

180f22e80 (the latch's y edge), 180b77df0 / 180b49710 in Spawn, the ajar start with ajarangle != 0 (vfn 0xad8),
m_eDefaultCheckDirection's keyvalue, PlayerOpen / PlayerClose, the hardware bodygroup, 1803eb9e0, the path sweep's
filter object 0x1819de460 (players only here), 180f17fb0's slave side, CBreakableProp's health rule and break pieces
(the BreakPieceList: not spawned), the door events (door_open / door_close / door_closed: not sent), the
areaportals, the 1200 s nav callback.
