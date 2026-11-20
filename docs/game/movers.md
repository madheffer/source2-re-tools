# The movers' own moves: CBaseToggle, CBaseDoor, CRotDoor, CFuncMoveLinear, CFuncRotating

server_20261105 (Ghidra; vtables by MSVC RTTI). Sum orders from the disassembly. RotationDelta and the pusher turn
checked natively (SceneOracle `--movers`).

## Functions

| Address | Module | What |
|---|---|---|
| 180d00310 | server | CBaseToggle LinearMove(dest, speed) |
| 1803eb540 | server | SetLocalVelocity |
| 180d0e750 | server | SetMoveDoneTime(t) |
| 180e8fa30 | server | PhysicsPusher |
| 180927c20 -> 180de8650 | server | per-entity interval (else gpGlobals +0x34: the tick) |
| 180e8d810 | server | PerformPush |
| 180e85e50 | server | LinearlyMoveRootPusher ([push.md](push.md)) |
| 1803eb270 | server | SetLocalOrigin (-> the node's 180c27c70) |
| 180d01630 | server | CBaseToggle MoveDone |
| 180d5a9e0 | server | CBaseDoor Spawn |
| 180cda7c0 | server | movedir · size |
| 180d416b0 | server | DoorGoUp |
| 180d41540 | server | DoorGoDown |
| 180d41f50 | server | DoorHitTop |
| 180d41d60 | server | DoorHitBottom |
| 180d21680 | server | input Open |
| 180d3e250 | server | input Close |
| 180d223d0 -> 180d4eb90 | server | input Toggle |
| 180d22540 | server | input SetSpeed |
| 180d55fd0 | server | PlayLockSounds(this, m_ls +0x8f8, locked, flag, pos) |
| 180d3c470 | server | CBaseDoor::Blocked (vtable 0x4d8) |
| 180d57760 | server | CBaseDoor outputs |
| 180d60790 | server | CBaseDoor::Use (vfn 0x498) |
| 180d3d620 | server | chain Use to same-named doors |
| 180d41250 | server | DoorActivate |
| 180fea630 | server | master test |
| 180d42170 | server | DoorTouch (m_pfnTouch +0x2b0) |
| 180fec9a0 | server | "DoorSound.Null" default (taken as "keyvalue left empty", not read) |
| 180dc9df0 | server | CFuncMoveLinear Spawn |
| 180db0f20 | server | CFuncMoveLinear MoveTo(dest, speed) |
| 180db0c10 | server | CFuncMoveLinear MoveDone |
| 180dbba50 | server | CFuncMoveLinear outputs (only OnFullyOpen / OnFullyClosed) |
| 180daca60 / 180dac0b0 | server | CFuncMoveLinear Open / Close |
| 180dc5780 | server | CFuncMoveLinear SetPosition |
| 180dacde0 | server | CFuncMoveLinear SetSpeed |
| 180ce21f0 | server | CBaseToggle AngularMove(dest, speed) |
| 18014a300 | server | lane-equal compare |
| 180991030 | server | angle difference |
| 1803eb230 | server | store angular velocity (QAngle) |
| 1801f9480 | server | any lane differs |
| 180e8f990 | server | PhysicsPushRotate |
| 180e8db80 -> 180e94780 | server | RotateRootPusher |
| 180a3e840 | server | step = avel x movetime per lane |
| 1802902a0 | server | CBaseToggle vfn 0x628: true |
| 18015a2a0 | server | CFuncRotating vfn 0x628: false |
| 1809f5b10 | server | angles = step + angles per lane |
| 1805517a0 | server | QuaternionAlign then QuaternionMult |
| 181475200 | server | QuaternionMult (not normalized) |
| 1803eb070 | server | SetLocalAngles |
| 180d5c300 | server | CRotDoor Spawn |
| 180ce28b0 | server | AxisDir |
| 18029f040 | server | step + angle per lane |
| 180d3aa30 | server | negate moveAng |
| 1814738b0 | server | VectorNormalize (doubles path) |
| 18015a2f0 | server | WorldSpaceCenter = CollisionToWorldSpace((maxs + mins) * 0.5) |
| 180ce9200 | server | CalcNearestPoint |
| 180253910 | server | WorldToCollisionSpace |
| 180cea780 | server | clamp maxss(mins, minss(p, maxs)) |
| 18014cf50 | server | CollisionToWorldSpace (transform_point) |
| 1803ede40 | server | Teleport (vfn 0x528; abs or local unread) |
| 180661510 | server | CFuncRotating think names |
| 180dcb9e0 | server | SpinUpMove |
| 180dcb960 | server | SpinDownMove |
| 180da8350 | server | HurtTouch (unread) |
| 180dc1eb0 | server | RotatingUse |
| 180dc1960 | server | RotateMove |
| 180dc13e0 | server | ReverseMove |
| 1801547a0 | server | CFuncRotating MoveDone (vfn 0x4f8): m_pfnMoveDone alone |
| 180dca3e0 | server | CFuncRotating Spawn |
| 1801f5970 | server | clamp (maxss then minss) |
| 180d0bb60 | server | SUB_CallUseToggle |
| 180da5a80 | server | GetNextMoveInterval |
| 180dd4110 | server | UpdateSpeed(v) |
| 18017b8d0 | server | clamp |
| 180dbeda0 | server | RampPitchVol |
| 1803e9710 | server | vector to QAngle (y, z, x) |
| 1803eb140 | server | store angular velocity when a lane differs |
| 180dc5a20 | server | SetTargetSpeed(v) |
| 180dcb8d0 | server | spin-down step (t) |
| 181472d90 | server | RotationDelta: QuaternionAngles(normalize(Q(b) x Q(a)^-1)) |
| 180a48c80 | server | after RotationDelta |
| 180dad170 | server | SetSpeed's body |
| 180f975a0 / 180f97440 | server | sound stop / start (volume +0x8b0, attenuation +0x8ac) |
| 1803c5940 | server | spawnflag 2048's (0x40000000) |

CFuncRotating_API handlers: SetSpeed 180d73ac0 -> 180dad170, Start 180d742f0, Stop 180d74370, Toggle 180d743f0, Reverse
180d74500, StartForward 180d74760, StartBackward 180d74910, StopAtStartPos 180d74ad0, SnapToStartPos 180d74b90,
SetStartPos 180d74d40, EnableAccelDecel 180d74e60, DisableAccelDecel (just after, ref 0x180d74f0e).

## Fields

| Offset | Field |
|---|---|
| +0x2c8 | m_pfnMoveDone |
| +0x2b0 | m_pfnTouch |
| +0x2f0 | m_nPlatformType |
| +0x2f1 | byte: 1 or 2 with m_bNoNPCs refuses Use (class unread; not a schema field; a player's isn't) |
| +0x318 | m_flMoveDoneTime |
| +0x400 | time scale |
| +0x480 | angular velocity |
| +0x494 | m_flLocalTime |
| toggle +0x850 | toggle state (0 top, 1 bottom, 2 going up, 3 going down) |
| toggle +0x854 | m_flMoveDistance ("distance") |
| toggle +0x860 | flag: when clear, at dest -> MoveDone at once |
| toggle +0x864 / +0x870 | pos1 / pos2 |
| toggle +0x87c | m_vecMoveAng (yaw at +0x880) |
| toggle +0x888 / +0x894 | angle1 / angle2 |
| toggle +0x8a4 | m_hActivator |
| toggle +0x8a8 | m_vecFinalDest |
| toggle +0x8b4 | m_vecFinalAngle |
| toggle +0x8c0 | movement type (1 linear, 2 angular) |
| toggle +0x8c8 | m_sMaster |
| door +0x8f8 | m_ls (+8 locked, +0x10 unlocked sound, +0x18 clock) |
| door +0x900 / +0x908 / +0x910 | locked sound / unlocked sound / its clock |
| door +0x918 / +0x919 / +0x91a / +0x91c | force-closed / sync / m_bLocked / m_bNoNPCs |
| door +0x924 | block damage |
| door +0x928 / +0x930 | move / arrive sound |
| door +0x948 | m_ChainTarget |
| door +0xa4c | speed |
| door +0xa50 | m_isChaining |
| door +0xa51 | networked copy of spawnflag 256 |
| movelinear +0x854 / +0x8d0 / +0x90c / +0x948 | movedistance / authoredposition / startposition / speed |
| movelinear +0x918 / +0x930 | OnFullyOpen / OnFullyClosed |
| collision +0x40 / +0x4c | mins / maxs |

CBaseDoor outputs: OnBlockedOpening 0x968, OnBlockedClosing 0x950, OnUnblockedOpening 0x998, OnUnblockedClosing 0x980,
OnFullyClosed 0x9b0, OnFullyOpen 0x9c8, OnClose 0x9e0, OnOpen 0x9f8, OnLockedUse 0xa10.

CFuncRotating (schema): m_OnStopped 0x850, m_OnStarted 0x868, m_OnReachedStart 0x880, m_localRotationVector 0x898,
m_flSpeed 0x8a4, m_flFanFriction 0x8a8, m_flAttenuation 0x8ac, m_flVolume 0x8b0, m_flTargetSpeed 0x8b4, m_flMaxSpeed
0x8b8, m_NoiseRunning 0x8c0, m_bReversed 0x8c8, m_bAccelDecel 0x8c9, m_prevLocalAngles 0x8e0, m_angStart 0x8ec,
m_bStopAtStartPos 0x8f8; spawnflag 1024's client origin / angles +0x8fc / +0x908.

## Constants

| Value | What |
|---|---|
| 0x181964d68 | CBaseToggle vtable |
| 0x181972270 | CBaseDoor vtable |
| 0x181972cc8 | CRotDoor vtable (shares every Use / touch slot) |
| 0x181829ca0 | CFuncMoveLinear vtable |
| 0x18182dbe8 | CFuncRotating vtable |
| 100 | default speed (door, movelinear), CFuncRotating max |
| 0.8 (0x3f4ccccd), 1 s | DoorActivate's unlocked sound volume, its clock |
| 1 s / 0.5 s | PlayLockSounds' clock (0.5 with the flag) |
| ObjectCaps 0x21 | PlayerUse with spawnflag 256 ([use.md](use.md)) |
| 0.002 | movedir normalise (movelinear) |
| 0.001 | movelinear arrival / SetPosition threshold |
| 2⁻⁴⁶ | movelinear SetSpeed final-dest threshold |
| 0.01 | AngularMove min time |
| 5, 0.99 | CRotDoor side test |
| 1e-17 / 1e17 | inline normalize bounds |
| 1/64, 0.1f | GetNextMoveInterval |
| 0.2f, 0.1f | spin up / down per step (x max x friction) |
| 0.2f | spawnflag 1 SUB_CallUseToggle delay |

Door spawnflags: 1 (Fully outputs swapped / rot door start), 2 (rot reverse), 16 (one way), 32 (toggle: no auto close),
64 roll, 128 pitch, 256 (use opens), 512 (m_bNoNPCs), 1024 (touch opens), 2048 (locked), 4096 (silent), 0x10000 (Use
also from going down). CFuncRotating spawnflags: 1 start on, 2 reverse, 4 / 8 axis, 16 accel, 32 hurt, 128 / 256
attenuation, 1024 client origin / angles, 2048, 4096 local rotation.

## CBaseToggle's linear move

A linear mover is MOVETYPE_PUSH with a local velocity and a move-done time on its own clock, not an interpolation.

- LinearMove (180d00310): +0x8a8 = dest, +0x8c0 = 1. Local origin already dest (and +0x860 clear) -> MoveDone (vfn
  0x4f8) at once. Else `d = dest - origin`, `t = sqrt((dz² + dy²) + dx²) / speed`, SetMoveDoneTime(|t|), velocity =
  `d * (1 / t)` (the reciprocal, then three multiplies; the time's sign kept: a negative speed moves away; speed 0
  never arrives), SetLocalVelocity.
- SetMoveDoneTime: t < 0 -> -1, else `m_flLocalTime + t`, into +0x318.
- PhysicsPusher: `movetime = done < 0 ? -1 : done - local time`; when the interval is below it, `interval * time scale (+0x400)`.
- PerformPush, linear half (no angular velocity):
  1. movetime > 0 -> local time += movetime.
  2. Non-zero local velocity -> PerformLinearPush; LinearlyMoveRootPusher sets `origin + velocity * movetime` per lane.
     Blocked -> local time -= movetime, the root back, Blocked (vfn 0x4d8).
  3. Every call: done <= local time and done > 0 -> MoveDone, **then** done <= local time again -> SetMoveDoneTime(-1).
     Source cleared the time before MoveDone; CS2 checks after, so a MoveDone that sets a time due now is cancelled
     (a door with wait 0 stays open).
- MoveDone (180d01630): type 1 -> SetLocalOrigin(+0x8a8), velocity 0; type 2 -> SetLocalAngles(+0x8b4), angular
  velocity 0; either -> move-done time -1 (if not already); type = 0; then m_pfnMoveDone.

## CBaseDoor (func_door)

- Spawn (180d5a9e0): pos1 = local origin, `pos2 = travel * movedir + pos1` per lane (`travel = movedir · size - lip`,
  movedir rotated into the parent's space); spawnpos 1 or spawnflag 1 -> SetLocalOrigin(pos2), state 0, else 1.
  **No swap** of the ends for spawnflag 1 (Source's obsolete start-open did); spawnflag 1 only swaps the Fully outputs.
  Spawnflag 2048 -> locked; speed 0 -> 100.
- Sound defaults (Spawn's start; vfn 0x880 "rotating"): +0x928 "RotDoorSound.DefaultMove" / "DoorSound.DefaultMove",
  +0x930 "...DefaultArrive", +0x900 "...DefaultLocked", +0x908 "DoorSound.Null".
- DoorGoUp: the moving sound unless already moving (2 / 3) or silent; state 2; m_pfnMoveDone = DoorHitTop; LinearMove(pos2,
  speed) (rotating: AngularMove, ±1 by the activator's side); OnOpen with the activator. DoorGoDown: state 3,
  DoorHitBottom, pos1, OnClose.
- DoorHitTop: arrive sound; state 0; the activator taken and cleared; not spawnflag 32 -> SetMoveDoneTime(wait),
  m_pfnMoveDone = DoorGoDown (the auto-close is this timer, not an I/O event; wait -1 -> never); spawnflag 32 -> the
  touch back. OnFullyOpen (OnFullyClosed with spawnflag 1). DoorHitBottom: state 1, OnFullyClosed (OnFullyOpen with 1).
- An output's activator: m_hActivator's entity; the door itself when none; null when it's gone.
- Inputs: Open: not at the top / going up and not locked -> unlocked sound (PlayLockSounds), the activator, DoorGoUp.
  Close: anything but at the bottom -> the activator, DoorGoDown inlined (Close while closing restarts and fires
  OnClose again; no lock check). Toggle: locked -> nothing; bottom -> GoUp; top -> GoDown; moving -> nothing.
  SetSpeed: m_flSpeed only (the move under way keeps its velocity). Lock / Unlock: +0x91a.
- Blocked (180d3c470): block damage (+0x924), then unless force-closed (+0x918) and with wait >= 0: going down -> GoUp,
  else GoDown; every other CBaseDoor with the same name too (the +0x919 sync of their origin and flags when movedir and
  velocities match: unread).

### Use (180d60790)

1. +0x8a4 = the input's activator.
2. +0x948 set -> 180d3d620: every other door of that name with the same m_bLocked and toggle state gets Use too, +0xa50 set around the call.
3. Activator a player (vfn 0x558) and spawnflag 256 clear -> PlayLockSounds(locked), return.
4. Activator's +0x2f1 is 1 or 2 and +0x91c -> the same.
5. States that go on: 1 always; with 0x10000: 3 too, and a toggle door (32) at 0 or 2; without: a toggle door at 0. Else return.
6. +0x91a -> OnLockedUse (+0xa10, the input's activator and caller), PlayLockSounds(locked). Else DoorActivate.

### DoorActivate (180d41250)

1. Master (+0x8c8, 180fea630) must pass, else return 0.
2. Toggle door (32) at the top -> DoorGoDown.
3. Else, unless silent (4096) and with an unlocked sound (+0x908) whose clock (+0x910) has passed: that sound, volume
   0.8, clock = now + 1 s; then `(state & ~2) != 0` (bottom or going down) -> DoorGoUp. Return 1.

### DoorTouch (180d42170) and PlayLockSounds

- DoorTouch (set in Spawn for every door): chained doors first (as Use); then only for a player toucher with
  **spawnflag 1024**: failed master -> locked sound; locked -> OnLockedUse and locked sound; else the activator and
  DoorActivate, and on success the touch function cleared. Without 1024 a door never opens by touch.
- PlayLockSounds: nothing with 4096; locked (m_ls+8) or unlocked (m_ls+0x10) sound when set and now is past m_ls+0x18;
  then that clock = now + 1 s (0.5 with the flag; Use and DoorTouch pass 0).
- ze_dark_souls' cell doors (Spawn_Door_1..6, spawnflag 256, no connection opens them) open only by Use.

## CFuncMoveLinear (func_movelinear)

- Spawn (180dc9df0): movedir normalised (0.002); movedistance <= 0 -> `(|Δy·dy| + |Δx·dx|) + |Δz·dz|` of the bounds -
  lip; speed <= 0 -> 100. authoredposition: 0 -> `pos1 = origin - dist·dir·start` (start = startposition), `pos2 =
  dist·dir + pos1`; 1 -> pos1 = origin - dist·dir, pos2 = origin; 2 -> pos1 = origin, pos2 = origin + dist·dir.
  `m_vecFinalDest = dist·dir·start + pos1`. With 1 and start != 1, or 2 and start != 0, it then moves itself to the
  start point (the rest of 180dc9df0: unread).
- MoveTo: speed 0 -> nothing; else the start sound and LinearMove.
- MoveDone: the stop sound and its think contexts, CBaseToggle's MoveDone, then |pos2 - origin| < 0.001 -> OnFullyOpen,
  else |pos1 - origin| < 0.001 -> OnFullyClosed, both with itself as activator and caller; sums `(z² + y²) + x²`. No OnReachedPosition.
- Open / Close: the activator; not already at pos2 / pos1 -> MoveTo at speed.
- SetPosition: `target = (pos2 - pos1) * v + pos1` per lane (v not clamped); over 0.001 away (`(z² + y²) + x²`) -> MoveTo.
- SetSpeed: speed = v; m_vecFinalDest over 2⁻⁴⁶ away (`(y² + x²) + z²`) -> |speed| > FLT_EPSILON: LinearMove(final
  dest, speed) (restarted), else speed 1 and LinearMove(origin, 1) (MoveDone at once: stops where it is).

## CBaseToggle's angular move

- AngularMove (180ce21f0): +0x8b4 = dest, type 2. Angles already dest (each lane ==, 18014a300) and +0x860 clear:
  MoveDone now. Else `d = dest - angles` (180991030), `t = maxss(0.01, sqrt((dx^2 + dy^2) + dz^2) / speed)` (negative
  -> 0.01; maxss passes a NaN on, which then gives no move-done time), SetMoveDoneTime(t) inline (only a changed time
  stored), angular velocity = `d * (1 / t)` as a QAngle (1803eb230).
- PerformPush with an angular velocity (+0x480, 1801f9480): PhysicsPushRotate (180e8f990): local time += movetime, then
  (avel not zero) RotateRootPusher: step = avel x movetime per lane (180a3e840);
  - vfn 0x628 true (CBaseToggle's: every door): `angles = step + angles` per lane (1809f5b10);
  - false (CFuncRotating's): `QuaternionAngles(1805517a0(AngleQuaternion(angles), AngleQuaternion(step)))`;
    QuaternionAlign (b's lanes negated when dpps(a, b)'s sign bit is set) then QuaternionMult
    `((a.w b + a.x (b.w, -b.z, b.y, -b.x)) + a.y (b.z, b.w, -b.x, -b.y)) + a.z (-b.y, b.x, b.w, -b.z)`, not normalized;
  - SetLocalAngles (1803eb070). Blocked: saved angles back, local time -= movetime.
  - With a linear velocity too: rotation first, then (not blocked) the clock put back and PhysicsPushMove runs, the
    later of the two times kept. The move-done check after is the linear one's.

## CRotDoor (func_door_rotating)

- Spawn (180d5c300): CBaseDoor::Spawn first (IsRotatingDoor vfn 0x880 skips its pos2 start and state), then AxisDir:
  +0x87c = spawnflag 64: (0, 0, 1) roll, 128: (1, 0, 0) pitch, else (0, 1, 0) yaw; spawnflag 2: x -1. angle1 = local
  angles, `angle2 = moveAng * m_flMoveDistance + angle1` (18029f040). Spawnflag 1: angle1 / angle2 swapped, moveAng
  negated (180d3aa30), Teleport (vfn 0x528) to the new angle1, state 1; else spawnpos 1: Teleport to angle2, state 0; else state 1.
- DoorGoUp's rotating branch: sign +1; with +0x8a4 an entity, spawnflag 16 clear and yaw (+0x880) != 0:
  1. n = CalcNearestPoint(activator's abs origin) - activator's, e = door's abs origin - activator's, both z 0.
  2. `dist = sqrt(((0 - n.z)^2 + (e.y - n.y)^2) + (e.x - n.x)^2)` before normalizing.
  3. e and n normalized inline (`len = sqrt((y^2 + z^2) + x^2)`; 1e-17 <= len <= 1e17: x (1 / len); 0: x, y 0; else 1814738b0 in doubles).
  4. dist < 5 and `(e.y n.y + e.z n.z) + n.x e.x > 0.99`: `e = ((origin - WorldSpaceCenter) + origin) - activator` (normalized the same).
  5. `n.y e.x - e.y n.x > 0`: sign -1. AngularMove(angle2 x sign, speed).
- DoorGoDown: AngularMove(angle1, speed). angle2 x -1 negates every lane, the base yaw too: RE3's strart_1a (angle1 270,
  angle2 360) opened from its other side turns from 270 to -360, 630 degrees.
- CalcNearestPoint (oriented solid): WorldToCollisionSpace (m_nodeToWorld inverted as SetAbsOrigin's inline inverse,
  the point through it), clamp (180cea780), CollisionToWorldSpace. SOLID_NONE / SOLID_BBOX or zero angles: axis-aligned
  `(p - origin) / scale` (the same bits for an identity rotation at scale 1).

## CFuncRotating (func_rotating)

MoveDone is m_pfnMoveDone alone: the speed changes run on the move-done timer.

- Spawn (180dca3e0): `friction = clamp(int(fanfriction) / 100f, 0, 1)` (1801f5970), 0: 1; `Volume = clamp(int / 10, 0, 1)`,
  0: 1; attenuation by 128 / 256; accel = 16; rotation vector 4: (1, 0, 0), 8: (0, 1, 0), else (0, 0, 1) (4096: turned
  by the local rotation), x -1 with 2; max = |maxspeed|, 0: 100; MOVETYPE_PUSH; 1: SUB_CallUseToggle at time + 0.2f;
  32: the hurt touch; speed 0; m_angStart = m_prevLocalAngles = local angles.
- GetNextMoveInterval: 1/64 with m_bStopAtStartPos or +0x2f0, else 0.1f. Each 0.1 s re-arm truncates that tick's step
  (PhysicsPusher's min(time left, tick)): at 64 tick the clock gains 0.1 per 7 ticks, a func_rotating turns at ~91 % of
  its speed in real time.
- UpdateSpeed (v): `speed = clamp(v, -max, max)`; from 0 with |v| > 0: OnStarted; to 0 from non-zero: OnStopped (itself
  as activator and caller); running sound and RampPitchVol; angular velocity = speed x rotation vector as a QAngle
  (1803e9710: (y, z, x)), stored only when a lane differs (1803eb140).
- SetTargetSpeed (v): target = |v| (x -1 reversed); no accel: UpdateSpeed(target), RotateMove next; else opposite
  signs: ReverseMove, |target| < |speed|: SpinDown, equal: RotateMove, larger: SpinUp; SetMoveDoneTime(interval).
- SpinUpMove: `n = |speed| + (max * 0.2f) * friction`; |n| < |target|: UpdateSpeed(n, target's sign); else
  UpdateSpeed(target), RotateMove now; the interval.
- SpinDownMove / ReverseMove via 180dcb8d0 (t): `n = maxss(0, |speed| - (max * 0.1f) * friction)`; |t| >= |n|:
  UpdateSpeed(t), done (SpinDown: RotateMove now; Reverse: SetTargetSpeed(target)); else UpdateSpeed(n with the
  speed's sign), the interval.
- RotateMove: the interval; |RotationDelta(angles, prev)| > |RotationDelta(start, angles)| (the inverse the conjugate
  over dpps; then 180a48c80): OnReachedStart; stopping at the start: SetTargetSpeed(0), SetLocalAngles(start), flag
  cleared (with accel that only starts the spin-down: it snaps to the start and slows down past it); prev = angles.
- Inputs: Start (flag cleared, target max), Stop (flag cleared, 0), Toggle (max from rest, else 0), Reverse (flag
  cleared, prev = angles, reversed flipped, target the speed), StartForward / StartBackward (reversed 0 / 1, max),
  StopAtStartPos (flag set, max, the interval), SnapToStartPos (flag cleared, 0, the start angles), SetStartPos (the
  vector as the start, prev too), Enable / DisableAccelDecel, SetSpeed (180dad170: flag cleared, reversed = v < 0,
  `target = |clamp(|v|, 0, 1) * max|` with v's sign, then SetTargetSpeed's dispatch). RotatingUse: Toggle's rule.

## Unread

- UpdateSpeed's sound half (180f975a0, 180f97440, RampPitchVol 180dbeda0), HurtTouch 180da8350, spawnflag 2048's
  1803c5940(0x40000000), spawnflag 1024's client origin / angles, "movewithoutpushingblockers", spawnflag 4096's turn.
- m_flLocalTime's start; the entity time scale and interval system; movedir's AngleVectors / rotation precision.
- CBaseDoor's wait and CRotDoor's distance defaults without a keyvalue (the schema's defaults).
- The same-named doors' sync (+0x919); the start Teleport (1803ede40: abs or local?); which bounds the model gives the
  collision property (+0x40 / +0x4c: m_vecMins / m_vecMaxs); where thinks run against PhysicsSimulate's push; the moving-sound and nav think
  contexts; CFuncMoveLinear authoredposition 1 / 2's start move; the start-on use's order against the push.
- Related: [momentary.md](momentary.md), [scene-node.md](scene-node.md) (VPhysicsUpdate), [trains.md](trains.md).
