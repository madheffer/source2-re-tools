# The movers' own moves: CBaseToggle, CBaseDoor, CRotDoor, CFuncMoveLinear, CFuncRotating (server.dll 2026-11-05)

Working notes for RUST_PORT 4f-6. Addresses are server_20261105.dll in the Ghidra project (vtables found through MSVC
RTTI: CBaseToggle 0x181964d68, CBaseDoor 0x181972270, CRotDoor 0x181972cc8, CFuncMoveLinear 0x181829ca0,
CFuncRotating 0x18182dbe8). Sum orders are from the disassembly. Ported: web/src/world/entities/classes/toggle.js
(CBaseToggle), movers.js (func_door, func_door_rotating, func_movelinear), rotating.js (func_rotating) and the angle
math in sim/src/game/movers.rs; checked by web/src/cs2web/world/door-test.mjs, rotator-test.mjs and the movers_check bin
(rubikon/tests/SceneOracle `--movers`: server.dll's own RotationDelta and pusher turn, called natively).

## CBaseToggle's linear move

A linear mover is MOVETYPE_PUSH with a local velocity and a move-done time on its own clock, not an interpolation.

- **LinearMove** (180d00310, dest, speed): m_vecFinalDest (+0x8a8) = dest, movement type (+0x8c0) = 1. Local origin
  already dest (and the +0x860 flag clear) → the class's MoveDone (vfn 0x4f8) at once. Else d = dest − origin,
  t = sqrt((dz² + dy²) + dx²) / speed, SetMoveDoneTime(|t|), velocity = d × (1 / t) (the reciprocal, then three
  multiplies; the time's sign kept: a negative speed moves away; speed 0 never arrives), SetLocalVelocity (1803eb540).
- **SetMoveDoneTime** (180d0e750): t < 0 → −1, else m_flLocalTime (+0x494) + t, into m_flMoveDoneTime (+0x318).
- **PhysicsPusher** (180e8fa30): movetime = done < 0 ? −1 : done − local time; when the interval (180927c20 →
  180de8650 per entity, else gpGlobals +0x34: the tick) is below it, interval × the time scale (+0x400).
- **PerformPush** (180e8d810), linear half (no angular velocity): movetime > 0 → local time += movetime; a non-zero
  local velocity → PerformLinearPush (docs/game/push.md), whose LinearlyMoveRootPusher (180e85e50) sets the local
  origin to origin + velocity × movetime per lane (SetLocalOrigin 1803eb270 → the node's 180c27c70); blocked → local
  time −= movetime, the root back, Blocked (vfn 0x4d8). Then, every call: done ≤ local time and done > 0 → MoveDone
  (vfn 0x4f8), **then** done ≤ local time again → SetMoveDoneTime(−1). Source cleared the time before MoveDone; CS2
  checks after it, so a MoveDone that sets a time due now is cancelled (a door with wait 0 stays open).
- **MoveDone** (CBaseToggle 180d01630): type 1 → SetLocalOrigin(m_vecFinalDest), velocity 0; type 2 → SetLocalAngles
  (+0x8b4), angular velocity 0; either → move-done time −1 (if not already); type = 0; then m_pfnMoveDone (+0x2c8).

## CBaseDoor (func_door), the linear path

- **Spawn** (180d5a9e0): pos1 (+0x864) = the local origin, pos2 (+0x870) = travel × movedir + pos1 per lane
  (travel = movedir · size (180cda7c0) − lip, movedir rotated into the parent's space); spawnpos 1 or spawnflag 1 →
  SetLocalOrigin(pos2), toggle state (+0x850) 0 (at the top), else 1 (at the bottom). **No swap** of the ends for
  spawnflag 1 (Source's obsolete start-open did); spawnflag 1 only swaps the Fully outputs' names below. Spawnflag
  2048 → locked (+0x91a); speed (+0xa4c) 0 → 100.
- Toggle states: 0 at the top, 1 at the bottom, 2 going up, 3 going down.
- **DoorGoUp** (180d416b0): the moving sound unless already moving (state 2 / 3) or silent (spawnflag 4096); state 2;
  m_pfnMoveDone = DoorHitTop; LinearMove(pos2, speed) (a rotating door: AngularMove 180ce21f0, ±1 from the
  activator's side); OnOpen (+0x9f8) with the activator. **DoorGoDown** (180d41540): the same with state 3,
  DoorHitBottom, pos1, OnClose (+0x9e0).
- **DoorHitTop** (180d41f50): the arrive sound; state 0; the activator taken and cleared; not spawnflag 32 →
  SetMoveDoneTime(wait) and m_pfnMoveDone = DoorGoDown (the auto-close is this timer, not an I/O event; wait −1 →
  never); spawnflag 32 → the touch back. Fires OnFullyOpen (+0x9c8), OnFullyClosed (+0x9b0) with spawnflag 1.
  **DoorHitBottom** (180d41d60): state 1, OnFullyClosed (OnFullyOpen with spawnflag 1).
- An output's activator: m_hActivator's entity; the door itself when there is none; null when it's gone.
- **Inputs** (CBaseDoor_API): Open (180d21680): not at the top / going up and not locked → the unlocked sound
  (PlayLockSounds 180d55fd0, not ported), the activator, DoorGoUp. Close (180d3e250): anything but at the bottom →
  the activator, DoorGoDown inlined (so Close while closing restarts and fires OnClose again; no lock check).
  Toggle (180d223d0 → 180d4eb90): locked → nothing; at the bottom → GoUp; at the top → GoDown; moving → nothing.
  SetSpeed (180d22540): m_flSpeed only (the move under way keeps its velocity). Lock / Unlock: +0x91a.
- **Blocked** (180d3c470, vtable 0x4d8): block damage (+0x924, world/push.js), then unless force-closed (+0x918) and
  with wait ≥ 0: going down → GoUp, else GoDown; every other CBaseDoor with its name the same (the +0x919 sync of
  their origin and flags when movedir and velocities match is not ported).
- Outputs (180d57760): OnBlockedOpening 0x968, OnBlockedClosing 0x950, OnUnblockedOpening 0x998, OnUnblockedClosing
  0x980, OnFullyClosed 0x9b0, OnFullyOpen 0x9c8, OnClose 0x9e0, OnOpen 0x9f8, OnLockedUse 0xa10.

### CBaseDoor::Use, DoorActivate, DoorTouch, the lock sounds (2026-11-12)

CBaseDoor's vtable 0x181972270, CRotDoor's 0x181972cc8 (tools/re/game/rtti.py); both share every slot below.

- **Use** (vfn 0x498, 180d60790; PlayerUse reaches it through ObjectCaps 0x21, spawnflag 256, docs/game/use.md):
  1. m_hActivator (+0x8a4) = the input's activator.
  2. m_ChainTarget (+0x948) set → 180d3d620: every other door of that name with the same m_bLocked and toggle
     state gets Use too, m_isChaining (+0xa50) set around the call. Not ported (no baked door has one).
  3. The activator is a player (vfn 0x558) and spawnflag 256 is clear → PlayLockSounds(locked) and return.
  4. The activator's byte +0x2f1 is 1 or 2 and m_bNoNPCs (+0x91c, set by spawnflag 512 in Spawn) → the same.
     Which class has +0x2f1 at 1 / 2 is unread (not a schema field; a player's isn't).
  5. Which toggle states (+0x850) go on: 1 (at the bottom) always. With spawnflag 0x10000: 3 (going down) too, and a
     toggle door (spawnflag 32) at 0 or 2. Without it: a toggle door at 0. Anything else returns.
  6. m_bLocked (+0x91a) → OnLockedUse (+0xa10, the input's activator and caller), PlayLockSounds(locked). Else
     DoorActivate.
- **DoorActivate** (180d41250): the master (m_sMaster +0x8c8, 180fea630) must pass, else returns 0. A toggle door
  (spawnflag 32) at the top → DoorGoDown. Else, unless silent (spawnflag 4096) and with an unlocked sound (+0x908)
  whose clock (+0x910) has passed: that sound, volume 0.8 (0x3f4ccccd), clock = now + 1 s; then at the bottom or
  going down ((state & ~2) != 0) → DoorGoUp. Returns 1.
- **DoorTouch** (180d42170, m_pfnTouch +0x2b0, set in Spawn for every door): the chained doors first (as Use); then
  only for a player toucher on a door with **spawnflag 1024** (touch opens): a failed master → the locked sound;
  locked → OnLockedUse and the locked sound; else the activator and DoorActivate, and on success the touch function
  is cleared. A door without 1024 never opens by touch. Not ported (no baked door has 1024).
- **PlayLockSounds** (180d55fd0: this, m_ls +0x8f8, locked, flag, pos): nothing with spawnflag 4096; the locked
  (m_ls+8) or unlocked (m_ls+0x10) sound when set and now is past m_ls+0x18; then that clock = now + 1 s (0.5 with
  the flag; Use and DoorTouch pass 0).
- **Spawn's sound defaults** (180d5a9e0's start; vfn 0x880 says "rotating"): +0x928 "RotDoorSound.DefaultMove" /
  "DoorSound.DefaultMove", +0x930 "...DefaultArrive", +0x900 "...DefaultLocked", +0x908 "DoorSound.Null"
  (180fec9a0: taken as "when the keyvalue left it empty", not read). +0xa51 is a networked copy of spawnflag 256.
- Port: movers.js doorUse / doorActivate, sound.js doorLockSound. ze_dark_souls' cell doors (Spawn_Door_1..6,
  spawnflag 256, no connection opens them) open only this way.

## CFuncMoveLinear (func_movelinear)

- **Spawn** (180dc9df0): movedir normalised (0.002), movedistance (+0x854) ≤ 0 → (|Δy·dy| + |Δx·dx|) + |Δz·dz|
  of the bounds − lip; speed (+0x948) ≤ 0 → 100. By authoredposition (+0x8d0): 0 → pos1 = origin − dist·dir·start
  (start = startposition +0x90c), pos2 = dist·dir + pos1; 1 → pos1 = origin − dist·dir, pos2 = origin; 2 → pos1 =
  origin, pos2 = origin + dist·dir. m_vecFinalDest = dist·dir·start + pos1. With 1 and start ≠ 1, or 2 and start ≠
  0, it then moves itself to the start point (the rest of 180dc9df0: not ported, warned).
- **MoveTo** (180db0f20, dest, speed): speed 0 → nothing; else the start sound and LinearMove.
- **MoveDone** (180db0c10): the stop sound and its think contexts, CBaseToggle's MoveDone, then |pos2 − origin| <
  0.001 → OnFullyOpen (+0x918), else |pos1 − origin| < 0.001 → OnFullyClosed (+0x930), both with itself as activator
  and caller; sums (z² + y²) + x². Its outputs (180dbba50) are only those two: no OnReachedPosition.
- **Inputs** (CFuncMoveLinear_API): Open (180daca60) / Close (180dac0b0): the activator; not already at pos2 / pos1
  → MoveTo at speed. SetPosition (180dc5780): target = (pos2 − pos1) × v + pos1 per lane (v not clamped); over 0.001
  away ((z² + y²) + x²) → MoveTo. SetSpeed (180dacde0): speed = v; m_vecFinalDest over 2⁻⁴⁶ away ((y² + x²) + z²)
  → |speed| > FLT_EPSILON: LinearMove(final dest, speed) (the move restarted), else speed 1 and LinearMove(origin, 1)
  (MoveDone at once: it stops where it is).

## CBaseToggle's angular move

- **AngularMove** (180ce21f0, dest, speed): m_vecFinalAngle (+0x8b4) = dest, movement type 2. Local angles already
  dest (each lane ==, 18014a300) and the +0x860 flag clear: MoveDone now. Else d = dest - angles (180991030),
  t = maxss(0.01, sqrt((dx^2 + dy^2) + dz^2) / speed) (a negative time is 0.01; maxss passes a NaN on, which then
  gives no move-done time), SetMoveDoneTime(t) inline (only a changed time is stored), angular velocity = d x (1 / t)
  stored as a QAngle (1803eb230).
- **PerformPush** (180e8d810) with an angular velocity (+0x480, 1801f9480 "any lane differs"): PhysicsPushRotate
  (180e8f990): local time += movetime, then (avel not zero) 180e8db80 -> RotateRootPusher (180e94780): step = avel x
  movetime per lane (180a3e840); vfn 0x628 true (CBaseToggle's 1802902a0, so every door): angles = step + angles per
  lane (1809f5b10); false (CFuncRotating's 18015a2a0): QuaternionAngles(1805517a0(AngleQuaternion(angles),
  AngleQuaternion(step))), 1805517a0 = QuaternionAlign (b's lanes negated when dpps(a, b)'s sign bit is set) then
  QuaternionMult (181475200: ((a.w b + a.x (b.w, -b.z, b.y, -b.x)) + a.y (b.z, b.w, -b.x, -b.y)) + a.z (-b.y, b.x,
  b.w, -b.z), not normalized); SetLocalAngles (1803eb070). Blocked: the saved angles put back, local time -= movetime.
  With a linear velocity too, the rotation goes first, then (not blocked) the clock is put back and PhysicsPushMove
  runs, the later of the two times kept. The move-done check after is the linear one's.
- **MoveDone** type 2: SetLocalAngles(m_vecFinalAngle), angular velocity 0, move-done time -1.

## CRotDoor (func_door_rotating)

- **Spawn** (180d5c300): CBaseDoor::Spawn first (its speed, wait, lock, sounds RotDoorSound.*; IsRotatingDoor (vfn
  0x880) skips its pos2 start and toggle state), then AxisDir (180ce28b0): m_vecMoveAng (+0x87c) = spawnflag 64:
  (0, 0, 1) roll, 128: (1, 0, 0) pitch, else (0, 1, 0) yaw; spawnflag 2: x -1. angle1 (+0x888) = the local angles,
  angle2 (+0x894) = moveAng x m_flMoveDistance (+0x854, "distance") + angle1 (18029f040: step + angle per lane).
  Spawnflag 1: angle1 and angle2 swapped, moveAng negated (180d3aa30), Teleport (vfn 0x528) to the new angle1, state
  1; else spawnpos 1: Teleport to angle2, state 0; else state 1.
- **DoorGoUp's rotating branch** (180d416b0): sign +1; with m_hActivator (+0x8a4) an entity, spawnflag 16 (one way)
  clear and moveAng's yaw (+0x880) not 0: n = CalcNearestPoint(the activator's abs origin) - the activator's, e = the
  door's abs origin - the activator's, both with z 0; dist = sqrt(((0 - n.z)^2 + (e.y - n.y)^2) + (e.x - n.x)^2)
  before normalizing; e and n normalized inline (len = sqrt((y^2 + z^2) + x^2); 1e-17 <= len <= 1e17: x (1 / len);
  0: x, y 0; else 1814738b0 in doubles); dist < 5 and (e.y n.y + e.z n.z) + n.x e.x > 0.99: e = ((origin -
  WorldSpaceCenter) + origin) - activator (normalized the same; WorldSpaceCenter 18015a2f0 =
  CollisionToWorldSpace((maxs + mins) x 0.5)); n.y e.x - e.y n.x > 0: sign -1. AngularMove(angle2 x sign, speed).
  DoorGoDown: AngularMove(angle1, speed). angle2 x -1 negates every lane, the base yaw too: RE3's strart_1a (angle1
  270, angle2 360) opened from its other side turns from 270 to -360, 630 degrees (as CS2 does it).
- **CalcNearestPoint** (180ce9200) for an oriented solid: WorldToCollisionSpace (180253910: the node's m_nodeToWorld
  inverted as SetAbsOrigin's inline inverse, then the point through it), the clamp (180cea780: maxss(mins, minss(p,
  maxs))), CollisionToWorldSpace (18014cf50: transform_point). SOLID_NONE / SOLID_BBOX or zero angles take an
  axis-aligned path ((p - origin) / scale), the same bits for an identity rotation at scale 1.

## CFuncRotating (func_rotating)

Fields (schema): m_OnStopped 0x850, m_OnStarted 0x868, m_OnReachedStart 0x880, m_localRotationVector 0x898, m_flSpeed
0x8a4, m_flFanFriction 0x8a8, m_flAttenuation 0x8ac, m_flVolume 0x8b0, m_flTargetSpeed 0x8b4, m_flMaxSpeed 0x8b8,
m_NoiseRunning 0x8c0, m_bReversed 0x8c8, m_bAccelDecel 0x8c9, m_prevLocalAngles 0x8e0, m_angStart 0x8ec,
m_bStopAtStartPos 0x8f8. Its think functions (by name, 180661510): SpinUpMove 180dcb9e0, SpinDownMove 180dcb960,
HurtTouch 180da8350, RotatingUse 180dc1eb0, RotateMove 180dc1960, ReverseMove 180dc13e0. MoveDone (vfn 0x4f8,
1801547a0) is m_pfnMoveDone alone: the speed changes run on the move-done timer.

- **Spawn** (180dca3e0): friction = clamp(int(fanfriction) / 100f, 0, 1) (1801f5970: maxss then minss), 0: 1;
  Volume = clamp(int / 10, 0, 1), 0: 1; attenuation by spawnflags 128 / 256; accel = spawnflag 16; the rotation
  vector spawnflag 4: (1, 0, 0), 8: (0, 1, 0), else (0, 0, 1) (4096: turned by the local rotation), x -1 with
  spawnflag 2; max = |maxspeed|, 0: 100; MOVETYPE_PUSH; spawnflag 1: SUB_CallUseToggle (180d0bb60) at time + 0.2f;
  spawnflag 32: the hurt touch; speed 0; m_angStart = m_prevLocalAngles = the local angles.
- **GetNextMoveInterval** (180da5a80): 1/64 with m_bStopAtStartPos or m_nPlatformType (+0x2f0), else 0.1f. Each 0.1 s
  re-arm truncates that tick's step (PhysicsPusher's min(time left, tick)), so at 64 tick the clock gains 0.1 per 7
  ticks: a func_rotating turns at ~91 % of its speed in real time.
- **UpdateSpeed** (180dd4110, v): speed = clamp(v, -max, max) (18017b8d0); from 0 with |v| > 0: OnStarted; to v == 0
  from non-zero: OnStopped (both itself as activator and caller); the running sound and RampPitchVol (180dbeda0); the
  angular velocity = speed x the rotation vector, as a QAngle (1803e9710: (y, z, x)), stored only when a lane
  differs (1803eb140).
- **SetTargetSpeed** (180dc5a20, v): target = |v| (x -1 reversed); no accel: UpdateSpeed(target), RotateMove next;
  else: opposite signs: ReverseMove, |target| < |speed|: SpinDown, equal: RotateMove, larger: SpinUp; SetMoveDoneTime
  of the interval.
- **SpinUpMove**: n = |speed| + (max x 0.2f) x friction; |n| < |target|: UpdateSpeed(n, the target's sign); else
  UpdateSpeed(target), RotateMove now; the interval. **SpinDownMove** / **ReverseMove** through 180dcb8d0 (t):
  n = maxss(0, |speed| - (max x 0.1f) x friction); |t| >= |n|: UpdateSpeed(t), done (SpinDown: RotateMove now;
  Reverse: SetTargetSpeed(target)); else UpdateSpeed(n with the speed's sign), the interval.
- **RotateMove**: the interval; |RotationDelta(angles, prev)| > |RotationDelta(start, angles)| (181472d90:
  QuaternionAngles(normalize(Q(b) x Q(a)^-1)), the inverse the conjugate over dpps; then 180a48c80): OnReachedStart;
  stopping at the start: SetTargetSpeed(0), SetLocalAngles(start), the flag cleared (with accel that only starts the
  spin-down: it snaps to the start and slows down past it); prev = the angles.
- **Inputs** (CFuncRotating_API): Start (flag cleared, target max), Stop (flag cleared, 0), Toggle (max from rest,
  else 0), Reverse (flag cleared, prev = angles, reversed flipped, target the speed), StartForward / StartBackward
  (reversed 0 / 1, max), StopAtStartPos (flag set, max, the interval), SnapToStartPos (flag cleared, 0, the start
  angles), SetStartPos (the vector as the start, prev too), Enable / DisableAccelDecel, SetSpeed (180dad170: flag
  cleared, reversed = v < 0, target = |clamp(|v|, 0, 1) x max| with v's sign, then SetTargetSpeed's dispatch).
  RotatingUse (Use): Toggle's rule. The handlers (each found from its "CFuncRotating_API::<Input>" string): SetSpeed
  180d73ac0 -> 180dad170, Start 180d742f0, Stop 180d74370, Toggle 180d743f0, Reverse 180d74500, StartForward
  180d74760, StartBackward 180d74910, StopAtStartPos 180d74ad0, SnapToStartPos 180d74b90, SetStartPos 180d74d40,
  EnableAccelDecel 180d74e60, DisableAccelDecel (just after, ref 0x180d74f0e).
- **Not read yet**: UpdateSpeed's sound half (FUN_180f975a0 stop, FUN_180f97440 start with volume +0x8b0 and
  attenuation +0x8ac, RampPitchVol 180dbeda0), HurtTouch 180da8350, spawnflag 2048's FUN_1803c5940(0x40000000),
  spawnflag 1024's client origin / angles (+0x8fc / +0x908), "movewithoutpushingblockers".

## What the port does, and its stand-ins

toggle.js keeps the clock, the move-done time, the velocity, the final dest, the movement type and m_pfnMoveDone (a
name in the class's table) in e.state, so engine.unmove's copy puts a blocked mover's clock back with its origin.
The class's think is PhysicsPusher + PerformPush's linear half, once a tick; engine.unmove calls the class's
`blocked` (CBaseDoor::Blocked's reverse) after restoring it. Stand-ins (TODO(trace)): m_flLocalTime's start (0),
the entity time scale (1) and interval system (the tick); movedir's AngleVectors / rotation and the size projection
in f64 then rounded; CBaseDoor's wait without a keyvalue (4); the lock sounds; the same-named doors' sync; the
moving-sound and nav think contexts; authoredposition 1 / 2's start move. A blocked mover's MoveDone outputs fired
in its think before the block was found stay fired (push.js runs after the thinks).

The angular half (toggle.js angularMove / pusherStep, movers.rs): the turn's step, RotationDelta and the door's side
in the sim; movers_check: RotationDelta and the quaternion turn 0 of 1,000,000 differ from server.dll's (the .wasm's
RotationDelta too). Its stand-ins: CRotDoor's start Teleport as SetLocalAngles (no baked rotating door is parented);
`distance` without a keyvalue (90); the collision bounds are the bake's hull bounds (which bounds the model gives
m_vecMins / m_vecMaxs is untraced); CFuncRotating's sounds, hurt touch, spawnflag 4096 (warned), m_nPlatformType (0)
and the start-on use's order against the push (after it, as Source's).

## To trace next

1. (CMomentaryRotButton: done, docs/game/momentary.md.)
2. VPhysicsUpdate (docs/game/scene-node.md "To trace next"). (CPointTemplate's placement and UpdateOnRemove's
   children: done, scene-node.md.)
   (CFuncTrackTrain's moves: done, docs/game/trains.md.)
3. The movers' stand-ins above: m_flLocalTime's start, CBaseDoor's wait and CRotDoor's distance defaults (the
   schema's default values), movedir's AngleVectors / rotation in f32, the lock sounds (PlayLockSounds 180d55fd0), the
   same-named doors' sync (+0x919), the start Teleport (vfn 0x528 1803ede40: abs or local?), which bounds the model
   gives the collision property (+0x40 / +0x4c), where thinks run against PhysicsSimulate's push (the think system).
4. Re-run the native check after a CS2 update: `dotnet run -c Release --project rubikon/tests/SceneOracle --
   <binaries> mov.bin 1000000 --movers`, then `cargo run --release -p ze-sim --bin movers_check -- mov.bin`.
