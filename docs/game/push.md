# Movers and players: the pusher, the ground's velocity, base velocity

server_20261105 (classes named by MSVC RTTI; sum orders from the disassembly). Source SDK 2013's names where the shape matches (physics_main_shared.cpp: CPhysicsPushedEntities); CS2's additions called out.

## Functions

| Address | Module | What |
|---|---|---|
| 180e90150 | server | CBaseEntity::PhysicsSimulate (vfn 0x508): MOVETYPE_PUSH (6) -> PhysicsPusher |
| 180e8fa30 | server | CBaseEntity::PhysicsPusher -> PerformPush |
| 180e8d810 | server | PerformPush(this, movetime) |
| 180b675b0 | server | CBasePlayerPawn::PhysicsSimulate (the usercmds): a pawn moves only as a pusher's moved entity |
| 180e8d600 | server | PerformLinearPush(g_pPushedEntities, this, dt) |
| 180e8db80 | server | PerformRotatePush |
| 180e7ef40 | server | local time -= dt (blocked) |
| 180e8f990 | server | PhysicsPushRotate (local time += dt; PerformRotatePush; blocked -> -= dt) |
| 180e8f8f0 | server | PhysicsPushMove (+= dt, the linear push, blocked -> -= dt) |
| 18024c740 | server | CPhysicsPushedEntities slot 0 SpeculativelyCheckRotPush (CS2's tracktrain player push, rotational) |
| 18024c610 | server | slot 1 SpeculativelyCheckLinearPush |
| 18020ca60 | server | slot 2 FinishRotPushedEntity |
| 180b97870 | server | root's "MoveWithoutPushingBlockers" attribute |
| 180e95f90 | server | SetupAllInHierarchy (root and every child, each with its abs origin, no filter) |
| 180e85e50 | server | LinearlyMoveRootPusher |
| 1803d91c0 | server | local velocity |
| 1803d6fb0 | server | abs velocity |
| 180e94780 | server | RotateRootPusher |
| 180e7a840 | server | GenerateBlockingEntityList(push) |
| 180c2fe30 | server | collision overlaps a pusher at its new place |
| 180e8f4d0 | server | impact / touch with what it hit |
| 1803eb270 / 1803eb070 | server | restore the root |
| 180225330 | server | CS2's player push on a func_tracktrain (linear) |
| 180e99960 | server | SpeculativelyCheckPush(info, push, rotational, ...) |
| 0x1801541d0 | server | vfn 0x5b0 false: CBaseEntity, CBaseToggle, CFuncMoveLinear, CBaseDoor, CFuncRotating, CFuncTrain, CFuncPlat, CPhysBox, CFuncBrush |
| 0x180fd4dd0 | server | vfn 0x5b0 true: CFuncTrackTrain only |
| 180cee2e0 / 180cf1540 | server | a pusher's collision off (remembered at +0x14) / back on |
| 180c2e7e0 | server | UTIL_TraceEntity |
| 1803e21a0 | server | is an NPC |
| 180e83c60 | server | IsPushedPositionValid: zero-length hull trace at its origin, filter 1819c7d78, interacts-with 0xc3001, its group; start solid -> invalid |
| 1803d5f70 | server | abs rotation (quaternion at +0x10) |
| 18093e970 | server | gamerules mode test |
| 180206870 | server | the stuck rule |
| 180e7a080 | server | stuck lift trace (returns 1 always) |
| 180e79e10 | server | 72 u lift along the root's backwards axis (dead branch) |
| 180148890 | server | normalize in place, returns the length |
| 180225190 | server | linear tracktrain finish |
| 180e9bac0 / 180e92420 | server | pushers' collision off / on |
| 180225cf0 | server | the slide push (info, entity, moved, scale) |
| 180e70540 | server | the entity's rotated position (old to new root transform, as a quaternion) |
| 18023c410 | server | rotational slide pushes |
| 180ae1cf0 | server | SetGroundEntity(svc, mv, trace) |
| 180abb1d0 | server | CategorizePosition |
| 180abcd00 | server | CheckMovingGround (CCSPlayer_MovementServices vfn 0x168) |
| 1803c5cd0 | server | ApplyAbsVelocityImpulse |
| 180fe8de0 | server | CTriggerPush Touch (vfn 0x4b8) |
| 180c30c10 | server | disable the trigger |

## Fields

| Offset | Field |
|---|---|
| mover +0x480 | angular velocity |
| mover +0x494 | local time |
| mover +0x490 | blocker handle |
| entity +0x388 | flags; bit 30 FL_UNBLOCKABLE_BY_PLAYER |
| collision +0x3f & 3, +0x5b | solid |
| collision +0x20 | interacts-with |
| entity +0x5e | collision group |
| info +0xe0 | blocked |
| info +0xe1 | pusher-is-ground |
| info +0x64 / +0x60 | push direction / its length |
| info +0x54 | the push's yaw |
| pawn +0x3c8 | base velocity |
| g_pPushedEntities 0x181f9e380 | vtable 0x18179a4d8 |

## Constants

| Value | What |
|---|---|
| sv_stepsize | cvar 1821d3588; blocking box max z + 2 x sv_stepsize |
| 0, 5, 6, 7 | MOVETYPE_NONE / VPHYSICS / PUSH / NOCLIP: not pushed |
| 1819c7d60 | push filter (ignores its own hierarchy and moveable physics) |
| 1819c7d78 | CTraceFilterPushMove |
| 0xc3001 | interacts-with of the validity / slide traces |
| 0x182337ef0 / 0x182337f10 | (1,0,0) / (0,1,0) for the nudges |
| 72 | stuck lift height |
| 1.1 (0x3f8ccccd) | stuck length scale |
| 0.35 (0x3eb33333) | rotational slide scale (up to 3) |
| 4.0 | slide trace start z offset |
| 140 | CategorizePosition's moving-up speed |
| FL_CONVEYOR 0x1000000, FL_BASEVELOCITY 0x800000 | flags |
| DAT_1821ba1c0, DAT_18211a3b0+0x58 | the tracktrain push's `flag` gates |
| 0x80 / 0x1000 | trigger_push spawnflags: push-once / no mass scale |

## PerformPush (180e8d810)

- Angular velocity zero: local time += dt; linear velocity non-zero -> PerformLinearPush; a blocker -> local time -= dt.
- Angular velocity non-zero: velocity non-zero -> saved = local time; PhysicsPushRotate; no blocker -> local time = saved; PhysicsPushMove; the later local time kept. Velocity zero: the rotate only. So rotation first, then translation.
- Blocker handle: a new one -> old vfn 0x4e0 (EndBlocked), vfn 0x4d0(new) (StartBlocked); every tick blocked -> vfn 0x4d8(blocker) (Blocked: the class's own, e.g. CFuncMoveLinear / CBaseDoor's blockdamage).
- Blocked: the mover doesn't move this tick (position restored, local time stepped back): its move runs a tick later.

## PerformLinearPush / PerformRotatePush

1. Root has "MoveWithoutPushingBlockers": move it, push nothing.
2. unblockable = root flags bit 30.
3. SetupAllInHierarchy.
4. Linear: root abs origin += local velocity x dt; push = abs velocity x dt. Rotate: RotateRootPusher; push (0, 0, 0).
5. GenerateBlockingEntityList: bounds of every solid pusher, grown by the push (a negative component grows the max, a positive the min), max z + 2 x sv_stepsize; every entity in the box that is solid, not movetype 0 / 5 / 6 / 7, not seen this push, whose ground entity is a pusher or whose collision overlaps a pusher at its new place. Its root move parent goes on the list with its abs origin.
6. SpeculativelyCheck(Linear|Rot)Push (vfn 1 / 0), moved list from the last down: false -> the blocker index.
7. Blocked: impact (180e8f4d0), root restored, every moved entity back to its saved origin, blocker returned. Not blocked: vfn 0x290(dt) on every pusher and moved entity, the impacts (touch), the rotation's FinishRotPushedEntity (vfn 0x10).

## SpeculativelyCheckLinearPush (18024c610)

Each moved entity, last first: a player (vfn 0x558) with a root answering vfn 0x5b0 true -> 180225330; anything else -> 180e99960(info, push, rotational 0).

## SpeculativelyCheckPush (180e99960)

1. Every pusher's collision off; trace from abs origin to origin + push (x: `push.x + o.x`, y: `o.y + push.y`, z: `o.z + push.z`) with its own hull (UTIL_TraceEntity), filter 1819c7d60, interacts-with collision +0x20, group +0x5e; pushers back on.
2. pusher-is-ground = its ground entity's root move parent is the root.
3. Unblockable and (player or NPC): abs origin = destination. Else: root vfn 0x6e8(entity) false -> blocked (+0xe0 = 1), return false; fraction non-zero -> abs origin = trace end; point-sized / not solid -> true; not rotational and fraction 1 -> true ("Interpenetrating entities!" when the place isn't valid).
4. blocked = !IsPushedPositionValid. Valid -> true. Invalid and not unblockable -> false.
5. Unblockable: four nudges along the root's abs rotation's x then y axis, +0.5 then -0.5 each: valid -> true. None -> the destination again, true.

## The tracktrain player push (180225330 linear, 18024c740 rotational)

`flag = !(DAT_1821ba1c0 && 18093e970())` (a gamerules mode at DAT_18211a3b0+0x58 neither 0 nor 2), passed to the push filter.

- Riding (its ground's root move parent is the root): SpeculativelyCheckPush(push, rotational 0, unblockable 0), 180206870, 180225190.
- Not riding: the push vector kept as direction (+0x64) and length (+0x60, 180148890), then 180225190.
- 180206870: direction zeroed, length 0. Valid -> nothing. Stuck -> 180e7a080: hull trace from origin + (0, 0, 72) down to origin (filter 1819c7d78, 0xc3001, its own value 1); hit (fraction != 1) -> `length = (end.z - origin.z) x 1.1`, else 0; returns 1, so direction (0, 0, 1). (After a 0: the 180e79e10 lift, dead.)
- 180225190: pushers off, slide push 180225cf0(scale 1), pushers on; pusher-is-ground again; not riding and not valid -> "Pushing linear hard!" and the slide push again; blocked = 0. **A tracktrain is never blocked by a player.**
- Rotational (tracktrain root): 180e70540 gives the push; riding -> SpeculativelyCheckPush(push, rotational 1) + 180206870; not riding -> direction + length; then 18023c410: pushers off, up to 3 slide pushes at scale 0.35 until valid, pushers on, still stuck -> "Pushing rotation hard!" and one at 1.0.
- Rotational, not a tracktrain: 180e70540, then SpeculativelyCheckPush(push, rotational 1, unblockable flag, the root).

## The slide push (180225cf0)

```
d = dir (+0x64), dist = scale x len (+0x60)
start = (o.x, o.y, o.z + 4.0)          // the entity's abs origin at entry; never updated
for i in 0..4:
  o = abs origin now
  end = (d.x x dist + o.x, d.y x dist + o.y, d.z x dist + o.z)
  trace start -> end: its hull, filter 1819c7d78 (CTraceFilterPushMove), interacts-with 0xc3001, its group (+0x5e)
  fraction > 0 -> abs origin = trace end
  fraction == 1 or nothing hit -> stop
  n = normal
  dot  = (d.z x n.z + d.y x n.y) + d.x x n.x
  dist = ((1 - |dot|) + 1) x ((1 - fraction) x dist)
  d   -= n x dot                            // x, y, z, each d - n x dot
  dot2 = (n.z x d.z + n.y x d.y) + n.x x d.x
  dot2 < 0 -> d -= n x dot2
```

## Rotation and the view

FinishRotPushedEntity (18020ca60): a non-player's yaw += the push's yaw (+0x54); a player's angles are left alone (carried round, view never turned).

## SetGroundEntity (180ae1cf0)

base = pawn base velocity (+0x3c8).

- Landing (none before, one now): `base -= new.absvel; base.z = new.absvel.z`.
- Leaving (one before, none now): `base += old.absvel; base.z = old.absvel.z`.
- Ground to ground or none to none: unchanged. Then SetBaseVelocity, the ground handle.

CategorizePosition (180abb1d0): moving up = vz > 140, and with a ground entity `vz - ground.absvel.z > 140`.

## CheckMovingGround (180abcd00)

Per usercmd before the move (frametime a double, cast to float):

```
on the ground (flags bit 0), its ground entity FL_CONVEYOR (0x1000000):
  v = ground vfn 0x688 (GetGroundVelocityToApply); FL_BASEVELOCITY (0x800000) set -> v += base; base = v; set FL_BASEVELOCITY
FL_BASEVELOCITY clear:
  k = (float)frametime x 0.5 + 1.0
  ApplyAbsVelocityImpulse(k x base) (1803c5cd0)            // velocity += k x base
  base = 0
clear FL_BASEVELOCITY
```

A mover's ground speed added to base velocity on leaving it becomes the player's velocity at the next command, x (1 + frametime / 2). A base velocity set with FL_BASEVELOCITY lasts while the flag is renewed, then turns into momentum the command after.

## CTriggerPush Touch (180fe8de0)

- Not push-once (spawnflag 0x80 clear), a walking entity: ApplyAbsVelocityImpulse(dir x speed) on every touch (not a base velocity); pushing up (the world direction's dot test) on the ground -> ground off, origin.z += 1 (vfn 0x528).
- Push-once: the impulse once, ground off when up, trigger disabled (180c30c10).
- VPhysics: dir x speed x 100 x frametime (x mass / 100 per object without spawnflag 0x1000).

## Unread

- What the tracktrain push's `flag` changes in the push filter.
- 180e70540's SIMD order.
- How often CS2 calls a trigger's Touch.
