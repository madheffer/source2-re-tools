# Movers and players: CS2's pusher, the ground's velocity, base velocity (server.dll 2026-11-05)

Working notes for RUST_PORT phase 2c. Addresses are server_20261105.dll in the Ghidra project; "disasm" = read in
the disassembly (source2-compiler tools/re/game/disasm.py), the sums' order from it. Classes are named through MSVC RTTI
(the CompleteObjectLocator before each vtable). Source SDK 2013's names are used where the shape matches it
(physics_main_shared.cpp: CPhysicsPushedEntities); CS2's own additions are called out.

## Who moves a player standing on (or hit by) a mover

CS2 keeps Source's pusher. CBaseEntity::PhysicsSimulate (180e90150, vfn 0x508) runs MOVETYPE_PUSH (6) through
CBaseEntity::PhysicsPusher 180e8fa30 → PerformPush 180e8d810(this, movetime). The player pawn has its own
PhysicsSimulate (CBasePlayerPawn::PhysicsSimulate 180b675b0: the usercmds), so a pawn is only ever moved by a pusher
as one of the pusher's "moved" entities.

### PerformPush 180e8d810

- angular velocity (+0x480) zero: local time (+0x494) += dt; linear velocity non-zero → PerformLinearPush
  180e8d600(g_pPushedEntities, this, dt); a blocker → local time -= dt (180e7ef40).
- angular velocity non-zero: velocity non-zero → saved = local time; PhysicsPushRotate 180e8f990 (local time += dt;
  PerformRotatePush 180e8db80; blocked → -= dt); no blocker → local time = saved; PhysicsPushMove 180e8f8f0 (+= dt,
  the linear push, blocked → -= dt), the later local time kept. Velocity zero: the rotate only.
  So a mover that both turns and moves pushes its rotation first, then its translation.
- the blocker handle (+0x490): a new one → vfn 0x4e0 on the old (EndBlocked), vfn 0x4d0(new) (StartBlocked); every
  tick blocked → vfn 0x4d8(blocker) (Blocked: the class's own, e.g. CFuncMoveLinear / CBaseDoor's blockdamage).
- blocked means the mover does not move this tick: its position is restored (below) and its local time stepped
  back, so its whole move runs a tick later.

### PerformLinearPush 180e8d600 / PerformRotatePush 180e8db80 (CPhysicsPushedEntities)

g_pPushedEntities = 0x181f9e380 (vtable 0x18179a4d8: slot 0 SpeculativelyCheckRotPush 18024c740, slot 1
SpeculativelyCheckLinearPush 18024c610, slot 2 FinishRotPushedEntity 18020ca60).

1. The root's "MoveWithoutPushingBlockers" attribute (180b97870): move it and push nothing.
2. unblockable = root flags (+0x388) bit 30 (FL_UNBLOCKABLE_BY_PLAYER).
3. SetupAllInHierarchy 180e95f90: the root and every child, recursively, each with its abs origin (no filter).
4. Linear: LinearlyMoveRootPusher 180e85e50: root abs origin += local velocity x dt (1803d91c0), push = abs velocity
   (1803d6fb0) x dt. Rotate: RotateRootPusher 180e94780; the push vector is (0, 0, 0).
5. GenerateBlockingEntityList 180e7a840(push): the bounds of every pusher that is solid (collision +0x3f & 3, +0x5b),
   grown by the push (a negative component grows the max, a positive the min), the max z raised by 2 x sv_stepsize
   (cvar 1821d3588); every entity in that box that is solid, not MOVETYPE_NONE / VPHYSICS / PUSH / NOCLIP (0, 5, 6,
   7) and not seen this push, whose ground entity is one of the pushers, or whose collision overlaps a pusher at its
   new place (180c2fe30). Its root move parent goes on the list with its abs origin.
6. SpeculativelyCheck(Linear|Rot)Push (vfn 1 / 0), the moved list from the last down: false → the blocker index.
7. Blocked: an impact with what it hit (180e8f4d0), the root back to where it was (1803eb270 / 1803eb070), every
   moved entity back to its saved origin, the blocker returned. Not blocked: vfn 0x290(dt) on every pusher and moved
   entity, the impacts (touch: 180e8f4d0), the rotation's FinishRotPushedEntity (vfn 0x10).

### Per moved entity: SpeculativelyCheckLinearPush 18024c610

For each moved entity (last first): a player (vfn 0x558) and a root pusher that answers vfn 0x5b0 true → CS2's
player push 180225330; anything else → SpeculativelyCheckPush 180e99960(info, push, rotational 0). vfn 0x5b0 is
0x1801541d0 (false) on CBaseEntity, CBaseToggle, CFuncMoveLinear, CBaseDoor, CFuncRotating, CFuncTrain, CFuncPlat,
CPhysBox, CFuncBrush, and 0x180fd4dd0 (true) on **CFuncTrackTrain** only.

### SpeculativelyCheckPush 180e99960 (Source's, unchanged in shape)

1. Every pusher's collision off (180cee2e0, remembered at +0x14), the trace from the entity's abs origin to origin
   + push (x: push.x + o.x, y: o.y + push.y, z: o.z + push.z) with its own hull (UTIL_TraceEntity 180c2e7e0), the
   push filter 1819c7d60 (ignores its own hierarchy and moveable physics), interacts-with the entity's own
   (collision +0x20), group the entity's (+0x5e); the pushers back on (180cf1540).
2. pusher-is-ground (+0xe1) = its ground entity's root move parent is the root.
3. unblockable and (a player or an NPC: 1803e21a0): abs origin = the destination. Else: the root's vfn 0x6e8(entity)
   false → blocked (+0xe0 = 1), return false; fraction non-zero → abs origin = the trace's end; point-sized / not
   solid → true; not rotational and fraction 1 → true (a "Interpenetrating entities!" warning when the place isn't
   valid).
4. blocked = !IsPushedPositionValid 180e83c60 (a zero-length trace of its hull at its origin, filter 1819c7d78 with
   interacts-with 0xc3001, its group: start solid → invalid). Valid → true. Not valid and not unblockable → false.
5. Unblockable: four nudges, the root's abs rotation's x then y axis (the quaternion at 1803d5f70 +0x10 turning
   (1,0,0) and (0,1,0), constants 0x182337ef0 / 0x182337f10), +0.5 then -0.5 along each: valid → true. None → the
   destination again, true.

### CS2's player push on a func_tracktrain: 180225330 (linear) / 18024c740 (rotational)

`flag` = !(DAT_1821ba1c0 && 18093e970()) (a gamerules mode at DAT_18211a3b0+0x58 neither 0 nor 2; passed to the
push filter: TODO what it changes; no player bodies here).

- Riding (its ground's root move parent is the root): SpeculativelyCheckPush(push, rotational 0, unblockable 0),
  then 180206870 (the stuck rule below), then 180225190.
- Not riding: the push vector itself kept as the direction (+0x64) and its length (+0x60, 180148890 normalizes in
  place and returns it), then 180225190.

180206870: the push direction zeroed; length 0. Valid (180e83c60) → nothing. Stuck → 180e7a080: a trace of the hull
from origin + (0, 0, 72) down to the origin (filter 1819c7d78, 0xc3001, its own value 1); hit (fraction != 1) →
length = (end.z - origin.z) x 1.1 (0x3f8ccccd), else 0; it returns 1 always, so the direction is (0, 0, 1). (The
branch after a 0 from it, a 72 u lift along the root's backwards axis through 180e79e10, is dead.)

180225190: the pushers' collision off (180e9bac0), the slide push 180225cf0(scale 1), the pushers on (180e92420);
pusher-is-ground again; not riding and not valid → "Pushing linear hard!" and the slide push again; blocked = 0.
**A tracktrain is never blocked by a player.**

Rotational (18024c740, a tracktrain root): the entity's rotated position 180e70540 gives the push (its place through
the root's old to new transform, as a quaternion: TODO the SIMD order); riding → SpeculativelyCheckPush(push,
rotational 1) + 180206870; not riding → direction + length as above; then 18023c410: pushers off, up to 3 slide
pushes at scale 0.35 (0x3eb33333) until valid, pushers on, still stuck → "Pushing rotation hard!" and one at 1.0.
Not a tracktrain: 180e70540, then SpeculativelyCheckPush(push, rotational 1, unblockable flag, the root).

### The slide push 180225cf0(info, entity, moved, scale) (disasm)

```
d = dir (+0x64), dist = scale x len (+0x60)
start = (o.x, o.y, o.z + 4.0)          // the entity's abs origin at entry; never updated
for i in 0..4:
  o = abs origin now
  end = (d.x x dist + o.x, d.y x dist + o.y, d.z x dist + o.z)
  trace start → end: its hull, filter 1819c7d78 (CTraceFilterPushMove), interacts-with 0xc3001, its group (+0x5e)
  fraction > 0 → abs origin = trace end
  fraction == 1 or nothing hit → stop
  n = normal
  dot  = (d.z x n.z + d.y x n.y) + d.x x n.x
  dist = ((1 - |dot|) + 1) x ((1 - fraction) x dist)
  d   -= n x dot                            // x, y, z, each d - n x dot
  dot2 = (n.z x d.z + n.y x d.y) + n.x x d.x
  dot2 < 0 → d -= n x dot2
```

### Rotation and the view

FinishRotPushedEntity 18020ca60: a non-player's yaw += the push's yaw (+0x54); **a player's angles are left alone**:
a turning mover carries a player round but never turns their view.

## The ground's velocity

SetGroundEntity 180ae1cf0(svc, mv, trace): base = the pawn's base velocity (+0x3c8). No ground before, one now
(landing): base -= new.absvel; base.z = new.absvel.z. A ground before, none now (leaving): base += old.absvel;
base.z = old.absvel.z. Ground to ground or none to none: unchanged. Then SetBaseVelocity, the ground handle.

CategorizePosition 180abb1d0: moving up = vz > 140, and with a ground entity vz - ground.absvel.z > 140.

## Base velocity: CheckMovingGround 180abcd00 (CCSPlayer_MovementServices vfn 0x168)

Source's CPlayerMove::CheckMovingGround, per usercmd before the move (frametime a double, cast to float):

```
on the ground (flags bit 0), its ground entity FL_CONVEYOR (0x1000000):
  v = ground vfn 0x688 (GetGroundVelocityToApply); FL_BASEVELOCITY (0x800000) set → v += base; base = v; set FL_BASEVELOCITY
FL_BASEVELOCITY clear:
  k = (float)frametime x 0.5 + 1.0
  ApplyAbsVelocityImpulse(k x base) (1803c5cd0)            // velocity += k x base
  base = 0
clear FL_BASEVELOCITY
```

So the ground speed a jump off a mover adds to base velocity (SetGroundEntity) becomes the player's own velocity at
their next command, x (1 + frametime / 2). A base velocity set with FL_BASEVELOCITY (CS2Fixes' old trigger_push)
lasts while the flag is renewed and turns into momentum the command after it stops.

## Found on the way: CS2's own trigger_push (CTriggerPush vfn 0x4b8, Touch 180fe8de0)

Not push-once (spawnflag 0x80 clear), a walking entity: **ApplyAbsVelocityImpulse(dir x speed) on every touch**, not
a base velocity; pushing up (the world direction's dot test) on the ground → ground off, origin.z += 1 (vfn 0x528).
Push-once: the impulse once, ground off when up, the trigger disabled (180c30c10). VPhysics: dir x speed x 100 x
frametime (x mass / 100 per object without spawnflag 0x1000). web/server/cs2web/core/game.js still treats CS2's push as a
base velocity for the tick (its 'push' events): TODO, with how often CS2 calls a trigger's Touch.
