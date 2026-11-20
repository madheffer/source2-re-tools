# CFuncTrackTrain and CPathTrack (server.dll 2026-11-05)

Working notes for RUST_PORT 4f-6. Addresses are server_20261105.dll (vtables through MSVC RTTI: CFuncTrackTrain
0x1819f5d50, CFuncTankTrain 0x1819f65d0, CPathTrack 0x1819bc150). Sum orders are from the disassembly. Ported:
web/src/world/entities/classes/trains.js (the train), paths.js (LookAhead, GetOrientation, VectorNormalize), the
angle math in sim/src/game/trains.rs (+ trains_abi.rs); checked by web/src/cs2web/world/train-test.mjs and the trains_check
bin (rubikon/tests/SceneOracle `--trains`: VectorAngles, the ease, AngleDistance, ApproachAngle and FixupAngles
called natively, 0 of 1,000,000 differ each).

## Fields (schema.py)

CFuncTrackTrain: m_ppath 0x850 (a handle), m_length 0x854 ("wheels"), m_vPosPrev 0x858, m_angPrev 0x864, m_flSpeed
0x870, m_controlMins 0x874, m_controlMaxs 0x880, m_lastBlockPos 0x88c, m_lastBlockTick 0x898, m_flVolume 0x89c,
m_flBank 0x8a0, m_oldSpeed 0x8a4, m_flBlockDamage 0x8a8, m_height 0x8ac, m_maxSpeed 0x8b0, m_dir 0x8b4 (a float, ±1),
the sound names 0x8b8..0x8d0, m_strPathTarget 0x8d8, the move sound times / pitches 0x8e0..0x8f0,
m_eOrientationType 0x8f4, m_eVelocityType 0x8f8, the move sound's handle 0x8fc, OnStart 0x910, OnNext 0x928,
OnArrivedAtDestinationNode 0x940, m_bManualSpeedChanges 0x958, m_flDesiredSpeed 0x95c, m_flSpeedChangeTime 0x960,
m_flAccelSpeed 0x964, m_flDecelSpeed 0x968, m_bAccelToSpeed 0x96c, m_flNextMPSoundTime 0x970.

CPathTrack: m_pnext 0x4a8, m_pprevious 0x4ac, m_paltpath 0x4b0 (handles), m_flSpeed 0x4b4, m_flRadius 0x4b8,
m_length 0x4bc, m_altName 0x4c0, m_nIterVal 0x4c8, m_eOrientationType 0x4cc, OnPass 0x4d0. Spawnflags 0x360.

Virtuals (vdiff against CBaseToggle): Spawn 0x48 180fe42a0, Activate 0x68 180fbda80, Use 0x498 180ff0ec0, Blocked
0x4d8 180fc0180, MoveDone 0x4f8 180fd60f0, vfn 0x628 18015a2a0 (false: the pusher turns it by quaternions, as
CFuncRotating). Thinks by name (1806d6570): CFuncTrackTrainNext 180fd9e00, Find 180fc8910, NearestPath 180fd6310,
DeadEnd 180fc5b20.

## The path

- **GetNext** (180e7dc40): m_paltpath when (spawnflags & 0x8004) == 0x8000 (alternate on, not a reverse branch),
  else m_pnext. **GetPrevious** (180e7e110): m_paltpath when (spawnflags & 0x8004) == 0x8004, else m_pprevious.
  **GetNextInDir** (180e7dd20, dir): forward GetNext, else GetPrevious. **ValidPath** (180e9f480, test): null for a
  disabled node (spawnflag 1) when testing. GetOrientationType (180e7dfb0): +0x4cc.
- **LookAhead** (180e866e0, origin*, dist, move, nextNext*): the walk over the nodes' **local** origins (GetLocal
  Origin 1803d91a0). left = |dist|; per step: next = GetNextInDir(cur); none: move → return 0; else Project:
  prev = GetNextInDir(cur, !dir), none → 0; origin = VectorNormalize(cur - prev) x left + cur (each lane mul then
  add), return 0. move and next disabled → 0. len = sqrt((z^2 + y^2) + x^2) of next - pos; len == 0: GetNextInDir
  (next) none (or disabled when moving) → *nextNext = 0, return left == dist (the signed one) ? 0 : next. left < len
  → origin = (left / len) x d + pos per lane, stop. Else left -= len, pos = origin = next's, cur = next; while
  left > 0. Then *nextNext = GetNextInDir(cur), return cur. (A dead end leaves *nextNext as the caller set it: 0.)
- **GetOrientation** (180e7ded0, out, dir): type 2 → the node's local angles (1803d90a0); else a = node, b =
  GetNextInDir(node, dir), none → b = node, a = GetNextInDir(node, !dir); VectorAngles(b - a) of local origins.
- **VectorNormalize** (180148890): len = sqrt((y^2 + z^2) + x^2); 1e-17 <= len <= 1e17 → (1 / len) x each lane;
  len 0 → (0, 0, 0) (the constant at 0x18177bf80); else 1814738b0 (doubles).
- **VectorAngles** (1814722c0, out, in): y == 0 and x == 0 → pitch z > 0 ? 270 : 90 (0x181926a2c / 0x1817b2c54),
  yaw 0; else yaw = V_atan2f(y, x) x 57.29578 (0x42652ee0), +360 below 0; pitch = V_atan2f(-z, sqrt(x^2 + y^2)) x
  57.29578, +360 below 0; roll 0.
- **FixupAngles** (180e7a450): each lane while < 0: + 360; while > 360: + -360.
- InPass: the node's input (CPathTrack_API::InPass 180e5a9c0) fires OnPass; the train calls it through AcceptInput
  (1813a8ed0) with itself as activator and caller.

## The train

- **Spawn** (180fe42a0): CBaseToggle's; volume keyvalue / 10; m_maxSpeed 0 → m_flSpeed, else 100; move sound
  pitches 0 → 60 / 200; no velocities; m_dir 1; MOVETYPE_PUSH; spawnflag 128 picks the solid type, 512 / 1024
  other flags (not read), 8 (passable) not solid; m_controlMins / Maxs from the bounds (+72 up); volume 0 → 1.
  **Activate** (180fbda80): on a map load, SetThink(Find) at the current time.
- **Find** (180fc8910): FindEntityByName(m_target, caller this) must be a path_track (or env_portal_path_track),
  else the warning and m_ppath null. LookAhead(path, path's origin, ±m_length, no move) (its result unused); Teleport
  (vfn 0x528) to the path's local origin + (0, 0, m_height), angles = Fixed Orientation (spawnflag 16) ? the train's
  local angles : the path's local angles with pitch 0 for No Pitch (spawnflag 1); m_ppath = path; ArriveAtNode; speed
  not 0 → SetNextThink(curtime + 0.1f), SetThink(Next), SoundUpdate. m_vPosPrev / m_angPrev = the local origin /
  angles.
- **Next** (180fd9e00): speed 0 → SoundStop, return (no think again). m_ppath gone → "Lost path": SoundStop, speed
  0. SoundUpdate (180fe36a0). np = local origin - (0, 0, height); node = LookAhead(m_ppath, np, speed x 0.1f, move,
  &nextNext); ManualSpeedChanges with speed < 0 != desired < 0 and no node → node = m_ppath. np.z += height.
  - No node (a dead end): d = np - local origin, l = sqrt((z^2 + y^2) + x^2); SoundStop; angular velocity 0;
    m_oldSpeed = speed, speed 0; l > 0 and old speed not 0: t = l / |old|, velocity = d x (1 / t), m_pfnMoveDone =
    DeadEnd, SetNextThink(never), SetMoveDoneTime(t); else DeadEnd now.
  - node != m_ppath: m_ppath = node; m_vPosPrev / m_angPrev = the local origin / angles; nextNext with (forward and
    nextNext's spawnflag 16) or (backward and node's spawnflag 16) → TeleportToPathTrack(nextNext) and arrive at
    nextNext, else at node; OnNext (activator node, caller the train).
  - UpdateTrainVelocity(node, nextNext, np, frametime); not Fixed Orientation: type 1 → UpdateOrientationAt
    PathTracks, 2 / 3 → UpdateOrientationBlend.
  - SetThink(Next), SetMoveDoneTime(0.5), SetNextThink(curtime) (every tick), m_pfnMoveDone = null. The pusher
    (toggle.js pusherStep) steps the train on its own clock by min(time left, tick).
  - With the ent_debug flag (1803da030(4)): lines and boxes to the nodes (not ported).
- **UpdateTrainVelocity** (180ff05b0): type 0: velocity = normalize(np - origin) x |speed|. Types 1 / 2: accelerating
  (m_bAccelToSpeed): speed != desired → step = (|desired| <= |speed| ? decel : accel) x frametime; desired - speed
  > step → speed + step; < -step → speed - step; else desired. Else with node and nextNext: ps = node's speed != 0 ?
  |node speed| x m_dir : speed, ns = nextNext's != 0 ? |its| x m_dir : ps; equal → speed = ps; else seg = |nn - node|,
  not 0: p = |train - node| / seg (both (z^2 + y^2) + x^2, local origins), type 2: p = (3 - (p + p)) x (p x p) + 0
  (after p - 0); speed = (1 - p) x ps + p x ns. Then the type 0 velocity. Types 3+: nothing. The normalize inline:
  len = sqrt((z^2 + y^2) + x^2), 1e-17..1e17 → (1 / len) x lanes, 0 → 0, else 1814738b0; then x |speed|.
- **UpdateOrientationAtPathTracks** (180fef2f0): m_ppath alive; dist = m_length > 0 ? m_length (negated unless
  forward) : (forward ? 100 : -100); LookAhead(m_ppath, origin - height, dist, no move, &nextNext) (only nextNext
  used); ang = FixupAngles(GetOrientation(m_ppath, forward)); ManualSpeedChanges and nextNext of type 2 → ang =
  GetOrientation(nextNext) (not fixed up); cur = FixupAngles(the abs angles, 1803d6de0 +0xd4);
  DoUpdateOrientation(cur, ang).
- **UpdateOrientationBlend** (180fef610, type, node, nextNext): prev = FixupAngles(m_angPrev); next = nextNext ?
  FixupAngles(GetOrientation(nextNext)) : prev; No Pitch: next.x = prev.x; any lane differs (1801f9480): l1 =
  |nextNext - m_vPosPrev| ((y^2 + z^2) + x^2), not 0 → p = |origin - m_vPosPrev| ((z^2 + y^2) + x^2) / l1; type 3: p =
  the ease (1814732e0: (1 - V_cosf(p x pi)) x 0.5). The turn (inline): AngleQuaternion both, d = |dpps(a, b)|, h =
  p - 0.5, w1 = ((((((3.5564499 - d x 1.4351900) x d - 3.2451999) x d + 1.0904) x (h x h)) + ((d x 0.215638 -
  1.06021) x d + 0.848013)) x ((h x p) x (p - 1))) + p (constants 0x181813da0..db8), w0 = 1 - w1, w1 negated unless
  dpps > 0, q = b w1 + a w0, normalized by sqrt(dpps(q, q)) (the identity 0x181f4a000 at 0), QuaternionAngles; No
  Pitch: x = prev.x; DoUpdateOrientation(the local angles, that).
- **DoUpdateOrientation** (180fc61d0, cur, ang): vx = No Pitch ? 0 : AngleDistance(ang.x, cur.x), vy =
  AngleDistance(ang.y, cur.y), each 0 under 0.1 in size; roll = the abs angular velocity's roll (1803d6e10 gives the
  rotation vector (roll, pitch, yaw)); m_flBank not 0: vy < -5 → AngleDistance(ApproachAngle(-bank, cur.z, bank +
  bank), cur.z); vy > 5 → the same toward bank; else AngleDistance(ApproachAngle(0, cur.z, bank x 4), cur.z) x 4.
  SetAbsAngularVelocity (1803ea270: the vector (roll, vx, vy) through a parent's rotation, stored as the QAngle
  (vx, vy, roll) when a lane differs).
- **AngleDistance** (18146b8e0): d = a - b; d <= -180 → + 360; d > 180 → + -360. **ApproachAngle** (18146bdb0,
  target, value, speed): each of target and value outside [-180, 180] → a - floorf(a x (1/360) + 0.5) x 360
  (floorf 1816c4664), maxss -180 / minss 180; below 0 → + 360. speed < 0 → -speed. delta = t - v, < -180 → + 360,
  > 180 → + -360. delta > speed → v + speed; < -speed → v - speed; else t.
- **ArriveAtNode** (180fbf9e0): InPass on the nodes from it up to (not including) its GetNext: the node alone;
  its spawnflag 8 → the train's spawnflag 2 (No User Control); the destination (FindEntityByName(m_strPathTarget))
  is the node → OnArrivedAtDestinationNode (activator the node), m_oldSpeed = speed, speed 0, m_strPathTarget
  cleared, return; else No User Control and the node's speed not 0 → SetSpeed(node speed).
- **TeleportToPathTrack** (180fe7560): cur = the local angles; look = the node's local origin, LookAhead(node, look,
  ±m_length (sign flipped unless forward), no move); Fixed Orientation or look unchanged → angles cur, else
  GetOrientation(node) (pitch cur's with No Pitch); Teleport(the node's local origin, those, no velocity); angular
  velocity 0.
- **DeadEnd** (180fc5b20): from m_ppath, while the next in the old speed's direction (>= 0: GetNext, else
  GetPrevious) is ValidPath(test): step on (no guard: a loop hangs); velocity 0, angular velocity 0; that node:
  InPass, and the destination → OnArrivedAtDestinationNode, m_strPathTarget cleared.
- **MoveDone** (180fd60f0): m_lastBlockTick -1, m_lastBlockPos 0, then m_pfnMoveDone (which it never clears).
- **SetSpeed** (180fe19d0, v, accel): new = |v| x m_dir; m_bAccelToSpeed = accel; accel: desired = new, change time
  = now, speed 0 and |desired| > 0 → speed 0.1f, OnStart, Next. Else speed = new; changed: not 0 → (from 0: OnStart)
  Next; 0 → Stop.
- **Stop** (180fe7270): velocity 0, angular velocity 0, m_oldSpeed = speed, speed 0, SoundStop, SetThink(null).
- **SetDirForward** (180fe1510): forward and m_dir != 1: m_ppath = GetPrevious(m_ppath) when there is one, m_dir 1;
  backward and m_dir != -1: GetNext, m_dir -1.
- **Inputs** (each from its "CFuncTrackTrain_API::<Input>" string): Stop 180fa5b50 (Stop inline), StartForward
  180fa5d20 (SetDir(1), SetSpeed(max)), StartBackward 180fa5db0, Toggle 180fa5e40 (SetSpeed(speed == 0 ? max : 0)),
  Resume 180fa5ed0 (speed = old speed, OnStart, Next), Reverse 180fa5f60 (SetDir(m_dir != 1), SetSpeed(speed)),
  SetSpeed 180fa6000 (SetSpeed(clamp(v, 0, 1) x max), 18017b8d0), SetSpeedDir 180fa6150 -> 180fd4940 (SetDir(v >=
  0), a = |v|, c = 0 <= a ? min(a, 1) : 0, no accel, speed = |c x max| x m_dir, then SetSpeed's tail), SetSpeedReal
  180fa6240 (SetSpeed(clamp(v, 0, max))), SetMaxSpeed 180fa6380 (max only), SetSpeedDirAccel 180fa6480 -> 180fd4a40
  (SetSpeed's accel branch with c x max), MoveToPathNode 180fa6570 -> 180fd4520, TeleportToPathNode 180fa6650 ->
  180fd4b30, LockOrientation 180fa6730 (spawnflag 16, angular velocity 0), UnlockOrientation 180fa67e0.
- **MoveToPathNode** (180fd4520): m_strPathTarget = the name; dest = FindEntityByName; no m_ppath or dest → return;
  speed = m_ppath's speed, 0 → max. dest is m_ppath: m_dir != 1 → GetPrevious exists ? forward : Stop; else GetNext
  exists ? backward : Stop. Else GetNext up to 1000 nodes: found → forward; else GetPrevious up to 1000 from m_ppath:
  found → backward, else return. SetDir, SetSpeed(speed).
- **TeleportToPathNode** (180fd4b30): m_strPathTarget = the name; the entity of that name (any class) becomes
  m_ppath, ArriveAtNode, TeleportToPathTrack. The velocity isn't touched.
- **Blocked** (180fc0180): a blocker riding the train (its ground entity, vfn 0x668) with flag 1 at +0x388: pushed up
  by min(|speed|, 50); else the blocker's velocity += normalize(its origin - the train's) x m_flBlockDamage
  (1803ea4a0); spawnflag 512: an unstick after 11 ticks (m_lastBlockTick / Pos, 180fc91d0, 180e78760); then the
  damage. Not ported (push.js does the train's own push).

## What the port does, and its stand-ins

trains.js keeps the train's fields in e.state (the clock and velocities through toggle.js, so engine.unmove's copy
puts a blocked train back with its clock). The think is the pusher's step (vfn 0x628 false) then the think if due
(`thinkFn` 'find' / 'next', `thinkAt` on the engine's clock). Stand-ins (TODO(trace)): Teleport as SetAbsOrigin /
SetAbsAngles; the angular velocity kept local (no parent's rotation); the think's place against the push and its
time's f32 rounding; Blocked; NearestPath (a save restore's); the keyvalue names (Source's speed / startspeed /
wheels / height / bank / orientationtype / velocitytype / manual*); m_pprevious worked out when asked
(paths.js linkedPrevious) rather than by CPathTrack::Link; a TeleportToPathNode to a non-path_track skipped; the
sounds (sound.js, the 2026-09-23 build's SoundUpdate / SoundStop: their 2026-11-05 bodies 180fe36a0 / 180fe3500
not re-read); the train's control volume (m_controlMins / Maxs, Use 180ff0ec0: a player driving it).

**Blocked can't be reached here.** The pusher calls the root's Blocked only when SpeculativelyCheck(Linear|Rot)Push
fails for a moved entity (push.md step 7). A player on a tracktrain's push goes through 180225330 / 18024c740,
which slide it and never block (push.md); the push list skips MOVETYPE_NONE / VPHYSICS / PUSH / NOCLIP, so props,
physboxes and dropped weapons never block one either. Only a non-player the pusher moves (a thrown grenade's own
movetype, an NPC) could, and world/push.js moves players only. So no train ever deals blockdamage or runs the
unstick in CS2 against what this engine has; nothing to port until grenades or NPCs join the push.

## To trace next

1. Teleport (1803ede40: abs or local); Blocked (180fc0180) if grenades join the push.
2. SoundUpdate (180fe36a0) / SoundStop (180fe3500) in this build; Use (180ff0ec0) and the control volume.
3. CPathTrack's Link / Activate (m_pprevious, m_paltpath) and its inputs in this build.
4. Re-run the native check after a CS2 update: `dotnet run -c Release --project rubikon/tests/SceneOracle --
   <binaries> trn.bin 1000000 --trains`, then `cargo run --release -p ze-sim --bin trains_check -- trn.bin`.
