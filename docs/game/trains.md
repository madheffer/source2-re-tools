# CFuncTrackTrain and CPathTrack

server_20261105 (vtables through MSVC RTTI; sum orders from the disassembly). Native check: rubikon/tests/SceneOracle `--trains` (VectorAngles, the ease, AngleDistance, ApproachAngle, FixupAngles called natively, 0 of 1,000,000 differ each).

## Functions

| Address | Module | What |
|---|---|---|
| 0x1819f5d50 | server | CFuncTrackTrain vtable |
| 0x1819f65d0 | server | CFuncTankTrain vtable |
| 0x1819bc150 | server | CPathTrack vtable |
| 180fe42a0 | server | train vfn 0x48 Spawn |
| 180fbda80 | server | vfn 0x68 Activate |
| 180ff0ec0 | server | vfn 0x498 Use (control volume, unread) |
| 180fc0180 | server | vfn 0x4d8 Blocked |
| 180fd60f0 | server | vfn 0x4f8 MoveDone |
| 18015a2a0 | server | vfn 0x628: false (the pusher turns it by quaternions, as CFuncRotating) |
| 1806d6570 | server | thinks by name |
| 180fd9e00 | server | think CFuncTrackTrainNext |
| 180fc8910 | server | think Find |
| 180fd6310 | server | think NearestPath |
| 180fc5b20 | server | think DeadEnd |
| 180e7dc40 | server | CPathTrack GetNext |
| 180e7e110 | server | GetPrevious |
| 180e7dd20 | server | GetNextInDir(dir) |
| 180e9f480 | server | ValidPath(test) |
| 180e7dfb0 | server | GetOrientationType (+0x4cc) |
| 180e866e0 | server | LookAhead(origin*, dist, move, nextNext*) |
| 1803d91a0 | server | GetLocalOrigin |
| 1803d90a0 | server | local angles |
| 180e7ded0 | server | GetOrientation(out, dir) |
| 180148890 | server | VectorNormalize |
| 18177bf80 | server | zero vector constant |
| 1814738b0 | server | normalize in doubles (out-of-range lengths) |
| 1814722c0 | server | VectorAngles(out, in) |
| 180e7a450 | server | FixupAngles |
| 180e5a9c0 | server | CPathTrack_API::InPass (fires OnPass) |
| 1813a8ed0 | server | AcceptInput |
| 180fe36a0 / 180fe3500 | server | SoundUpdate / SoundStop |
| 1803da030 | server | ent_debug flag test (4) |
| 180ff05b0 | server | UpdateTrainVelocity |
| 180fef2f0 | server | UpdateOrientationAtPathTracks |
| 1803d6de0 | server | abs angles (+0xd4) |
| 180fef610 | server | UpdateOrientationBlend(type, node, nextNext) |
| 1801f9480 | server | angle lanes differ |
| 1814732e0 | server | ease: `(1 - V_cosf(p x pi)) x 0.5` |
| 180fc61d0 | server | DoUpdateOrientation(cur, ang) |
| 1803d6e10 | server | abs angular velocity as rotation vector (roll, pitch, yaw) |
| 1803ea270 | server | SetAbsAngularVelocity |
| 18146b8e0 | server | AngleDistance |
| 18146bdb0 | server | ApproachAngle(target, value, speed) |
| 1816c4664 | server | floorf |
| 180fbf9e0 | server | ArriveAtNode |
| 180fe7560 | server | TeleportToPathTrack |
| 180fe19d0 | server | SetSpeed(v, accel) |
| 180fe7270 | server | Stop |
| 180fe1510 | server | SetDirForward |
| 180fa5b50 | server | input Stop |
| 180fa5d20 / 180fa5db0 | server | input StartForward / StartBackward |
| 180fa5e40 | server | input Toggle |
| 180fa5ed0 | server | input Resume |
| 180fa5f60 | server | input Reverse |
| 180fa6000 | server | input SetSpeed (clamp 18017b8d0) |
| 180fa6150 -> 180fd4940 | server | input SetSpeedDir |
| 180fa6240 | server | input SetSpeedReal |
| 180fa6380 | server | input SetMaxSpeed |
| 180fa6480 -> 180fd4a40 | server | input SetSpeedDirAccel |
| 180fa6570 -> 180fd4520 | server | input MoveToPathNode |
| 180fa6650 -> 180fd4b30 | server | input TeleportToPathNode |
| 180fa6730 / 180fa67e0 | server | input LockOrientation / UnlockOrientation |
| 1803ea4a0 | server | add velocity (Blocked) |
| 180fc91d0, 180e78760 | server | Blocked's unstick |
| 1803ede40 | server | Teleport (abs or local: unread) |
| 180225330 / 18024c740 | server | a player's push (slides, never blocks: push.md) |

## Fields

| Offset | Field |
|---|---|
| CFuncTrackTrain +0x850 | m_ppath (handle) |
| +0x854 | m_length ("wheels") |
| +0x858 / +0x864 | m_vPosPrev / m_angPrev |
| +0x870 | m_flSpeed |
| +0x874 / +0x880 | m_controlMins / m_controlMaxs |
| +0x88c / +0x898 | m_lastBlockPos / m_lastBlockTick |
| +0x89c | m_flVolume |
| +0x8a0 | m_flBank |
| +0x8a4 | m_oldSpeed |
| +0x8a8 | m_flBlockDamage |
| +0x8ac | m_height |
| +0x8b0 | m_maxSpeed |
| +0x8b4 | m_dir (float, +-1) |
| +0x8b8..0x8d0 | sound names |
| +0x8d8 | m_strPathTarget |
| +0x8e0..0x8f0 | move sound times / pitches |
| +0x8f4 / +0x8f8 | m_eOrientationType / m_eVelocityType |
| +0x8fc | move sound handle |
| +0x910 / +0x928 / +0x940 | OnStart / OnNext / OnArrivedAtDestinationNode |
| +0x958 | m_bManualSpeedChanges |
| +0x95c / +0x960 | m_flDesiredSpeed / m_flSpeedChangeTime |
| +0x964 / +0x968 | m_flAccelSpeed / m_flDecelSpeed |
| +0x96c | m_bAccelToSpeed |
| +0x970 | m_flNextMPSoundTime |
| CPathTrack +0x4a8 / +0x4ac / +0x4b0 | m_pnext / m_pprevious / m_paltpath (handles) |
| +0x4b4 / +0x4b8 / +0x4bc | m_flSpeed / m_flRadius / m_length |
| +0x4c0 | m_altName |
| +0x4c8 | m_nIterVal |
| +0x4cc | m_eOrientationType |
| +0x4d0 | OnPass |
| entity +0x360 | spawnflags |
| entity +0x388 | flags (flag 1: Blocked's rider test) |

## Constants

| Value | What |
|---|---|
| path spawnflag 1 | disabled |
| path spawnflag 8 | sets the train's No User Control |
| path spawnflag 16 | teleport to this node (Next) |
| path (spawnflags & 0x8004) == 0x8000 / 0x8004 | alternate forward / reverse branch |
| train spawnflag 1 / 2 / 8 / 16 / 128 / 512 / 1024 | No Pitch / No User Control / passable / Fixed Orientation / solid type / unstick (and other, unread) / other (unread) |
| 0.1f | think step |
| 0.5 | SetMoveDoneTime in Next |
| 100 | Spawn: m_maxSpeed 0 -> m_flSpeed, else 100 (as read); look-ahead distance with m_length <= 0 |
| 60 / 200 | default move sound pitches |
| +72 | control volume height |
| 0x42652ee0 = 57.29578 | rad -> deg |
| 0x181926a2c / 0x1817b2c54 | 270 / 90 |
| 1e-17 .. 1e17 | VectorNormalize's float range |
| 0x181813da0..db8 | blend constants |
| 0x181f4a000 | identity quaternion |
| 0.1, 5 | DoUpdateOrientation dead zone, bank threshold |
| 50, 11 ticks | Blocked: rider push cap, unstick delay |
| 1000 | MoveToPathNode search limit |

## The path

- **GetNext**: m_paltpath when `(spawnflags & 0x8004) == 0x8000`, else m_pnext. **GetPrevious**: m_paltpath when `== 0x8004`, else m_pprevious. **GetNextInDir**: forward GetNext, else GetPrevious. **ValidPath**: null for a disabled node (spawnflag 1) when testing.
- **LookAhead** (over the nodes' **local** origins): left = |dist|; per step: next = GetNextInDir(cur); none: move -> return 0; else Project: prev = GetNextInDir(cur, !dir), none -> 0; `origin = VectorNormalize(cur - prev) x left + cur` (each lane mul then add), return 0. move and next disabled -> 0. `len = sqrt((z^2 + y^2) + x^2)` of next - pos; len == 0: GetNextInDir(next) none (or disabled when moving) -> *nextNext = 0, return `left == dist` (signed) ? 0 : next. left < len -> `origin = (left / len) x d + pos` per lane, stop. Else left -= len, pos = origin = next's, cur = next; while left > 0. Then *nextNext = GetNextInDir(cur), return cur. (A dead end leaves *nextNext as the caller set it: 0.)
- **GetOrientation**: type 2 -> the node's local angles; else a = node, b = GetNextInDir(node, dir), none -> b = node, a = GetNextInDir(node, !dir); VectorAngles(b - a) of local origins.
- **VectorNormalize**: `len = sqrt((y^2 + z^2) + x^2)`; 1e-17 <= len <= 1e17 -> (1 / len) x each lane; 0 -> (0, 0, 0); else 1814738b0.
- **VectorAngles**: y == 0 and x == 0 -> pitch z > 0 ? 270 : 90, yaw 0; else `yaw = V_atan2f(y, x) x 57.29578`, +360 below 0; `pitch = V_atan2f(-z, sqrt(x^2 + y^2)) x 57.29578`, +360 below 0; roll 0.
- **FixupAngles**: each lane while < 0: + 360; while > 360: + -360.
- InPass fires OnPass; the train calls it through AcceptInput with itself as activator and caller.

## Spawn / Activate / Find

- Spawn: CBaseToggle's; volume keyvalue / 10; m_maxSpeed 0 -> m_flSpeed, else 100; pitches 0 -> 60 / 200; no velocities; m_dir 1; MOVETYPE_PUSH; spawnflag 128 picks the solid type, 512 / 1024 other flags, 8 not solid; m_controlMins / Maxs from the bounds (+72 up); volume 0 -> 1.
- Activate: on a map load, SetThink(Find) at the current time.
- Find: FindEntityByName(m_target, caller this) must be a path_track (or env_portal_path_track), else the warning and m_ppath null. LookAhead(path, path's origin, +-m_length, no move) (result unused); Teleport (vfn 0x528) to the path's local origin + (0, 0, m_height), angles = Fixed Orientation ? the train's local angles : the path's local angles (pitch 0 with No Pitch); m_ppath = path; ArriveAtNode; speed not 0 -> SetNextThink(curtime + 0.1f), SetThink(Next), SoundUpdate. m_vPosPrev / m_angPrev = the local origin / angles.

## Next (180fd9e00)

1. Speed 0 -> SoundStop, return (no think again). m_ppath gone -> "Lost path": SoundStop, speed 0.
2. SoundUpdate. `np = local origin - (0, 0, height)`; `node = LookAhead(m_ppath, np, speed x 0.1f, move, &nextNext)`; ManualSpeedChanges with (speed < 0) != (desired < 0) and no node -> node = m_ppath. np.z += height.
3. No node (dead end): d = np - local origin, `l = sqrt((z^2 + y^2) + x^2)`; SoundStop; angular velocity 0; m_oldSpeed = speed, speed 0; l > 0 and old speed not 0: `t = l / |old|`, `velocity = d x (1 / t)`, m_pfnMoveDone = DeadEnd, SetNextThink(never), SetMoveDoneTime(t); else DeadEnd now.
4. node != m_ppath: m_ppath = node; m_vPosPrev / m_angPrev = local origin / angles; nextNext with (forward and nextNext's spawnflag 16) or (backward and node's spawnflag 16) -> TeleportToPathTrack(nextNext) and arrive at nextNext, else at node; OnNext (activator node, caller the train).
5. UpdateTrainVelocity(node, nextNext, np, frametime); not Fixed Orientation: type 1 -> UpdateOrientationAtPathTracks, 2 / 3 -> UpdateOrientationBlend.
6. SetThink(Next), SetMoveDoneTime(0.5), SetNextThink(curtime) (every tick), m_pfnMoveDone = null. The pusher steps the train on its own clock by min(time left, tick).
7. ent_debug flag (1803da030(4)): lines and boxes to the nodes.

## UpdateTrainVelocity (180ff05b0)

- Type 0: `velocity = normalize(np - origin) x |speed|`.
- Types 1 / 2: accelerating (m_bAccelToSpeed): speed != desired -> `step = (|desired| <= |speed| ? decel : accel) x frametime`; desired - speed > step -> speed + step; < -step -> speed - step; else desired. Else with node and nextNext: `ps = node speed != 0 ? |node speed| x m_dir : speed`, `ns = nextNext's != 0 ? |its| x m_dir : ps`; equal -> speed = ps; else seg = |nn - node|, not 0: `p = |train - node| / seg` (both `(z^2 + y^2) + x^2`, local origins); type 2: `p = (3 - (p + p)) x (p x p) + 0` (after p - 0); `speed = (1 - p) x ps + p x ns`. Then the type 0 velocity.
- Types 3+: nothing.
- The normalize inline: `len = sqrt((z^2 + y^2) + x^2)`, 1e-17..1e17 -> (1 / len) x lanes, 0 -> 0, else 1814738b0; then x |speed|.

## UpdateOrientationAtPathTracks (180fef2f0)

- m_ppath alive; `dist = m_length > 0 ? m_length (negated unless forward) : (forward ? 100 : -100)`; LookAhead(m_ppath, origin - height, dist, no move, &nextNext) (only nextNext used); ang = FixupAngles(GetOrientation(m_ppath, forward)); ManualSpeedChanges and nextNext of type 2 -> ang = GetOrientation(nextNext) (not fixed up); cur = FixupAngles(abs angles); DoUpdateOrientation(cur, ang).

## UpdateOrientationBlend (180fef610)

1. prev = FixupAngles(m_angPrev); next = nextNext ? FixupAngles(GetOrientation(nextNext)) : prev; No Pitch: next.x = prev.x.
2. Any lane differs: `l1 = |nextNext - m_vPosPrev|` (`(y^2 + z^2) + x^2`), not 0 -> `p = |origin - m_vPosPrev|` (`(z^2 + y^2) + x^2`) / l1; type 3: p = the ease.
3. The turn (inline): AngleQuaternion both, `d = |dpps(a, b)|`, `h = p - 0.5`, `w1 = ((((((3.5564499 - d x 1.4351900) x d - 3.2451999) x d + 1.0904) x (h x h)) + ((d x 0.215638 - 1.06021) x d + 0.848013)) x ((h x p) x (p - 1))) + p`, `w0 = 1 - w1`, w1 negated unless dpps > 0, `q = b w1 + a w0`, normalized by sqrt(dpps(q, q)) (identity at 0), QuaternionAngles; No Pitch: x = prev.x.
4. DoUpdateOrientation(the local angles, that).

## DoUpdateOrientation (180fc61d0)

- `vx = No Pitch ? 0 : AngleDistance(ang.x, cur.x)`, `vy = AngleDistance(ang.y, cur.y)`, each 0 under 0.1 in size.
- roll = the abs angular velocity's roll; m_flBank not 0: vy < -5 -> `AngleDistance(ApproachAngle(-bank, cur.z, bank + bank), cur.z)`; vy > 5 -> the same toward bank; else `AngleDistance(ApproachAngle(0, cur.z, bank x 4), cur.z) x 4`.
- SetAbsAngularVelocity: the vector (roll, vx, vy) through a parent's rotation, stored as the QAngle (vx, vy, roll) when a lane differs.

## AngleDistance / ApproachAngle

- AngleDistance: `d = a - b`; d <= -180 -> + 360; d > 180 -> + -360.
- ApproachAngle: each of target and value outside [-180, 180] -> `a - floorf(a x (1/360) + 0.5) x 360`, maxss -180 / minss 180; below 0 -> + 360. speed < 0 -> -speed. `delta = t - v`, < -180 -> + 360, > 180 -> + -360. delta > speed -> v + speed; < -speed -> v - speed; else t.

## Arriving, teleporting, dead ends

- **ArriveAtNode**: InPass on the nodes from it up to (not including) its GetNext: the node alone; its spawnflag 8 -> the train's spawnflag 2; the destination (FindEntityByName(m_strPathTarget)) is the node -> OnArrivedAtDestinationNode (activator the node), m_oldSpeed = speed, speed 0, m_strPathTarget cleared, return; else No User Control and the node's speed not 0 -> SetSpeed(node speed).
- **TeleportToPathTrack**: cur = local angles; look = the node's local origin, LookAhead(node, look, +-m_length (sign flipped unless forward), no move); Fixed Orientation or look unchanged -> angles cur, else GetOrientation(node) (pitch cur's with No Pitch); Teleport(node's local origin, those, no velocity); angular velocity 0.
- **DeadEnd**: from m_ppath, while the next in the old speed's direction (>= 0: GetNext, else GetPrevious) is ValidPath(test): step on (no guard: a loop hangs); velocity 0, angular velocity 0; that node: InPass, and the destination -> OnArrivedAtDestinationNode, m_strPathTarget cleared.
- **MoveDone**: m_lastBlockTick -1, m_lastBlockPos 0, then m_pfnMoveDone (never cleared by it).

## Speed and direction

- **SetSpeed**: `new = |v| x m_dir`; m_bAccelToSpeed = accel; accel: desired = new, change time = now, speed 0 and |desired| > 0 -> speed 0.1f, OnStart, Next. Else speed = new; changed: not 0 -> (from 0: OnStart) Next; 0 -> Stop.
- **Stop**: velocity 0, angular velocity 0, m_oldSpeed = speed, speed 0, SoundStop, SetThink(null).
- **SetDirForward**: forward and m_dir != 1: m_ppath = GetPrevious(m_ppath) when there is one, m_dir 1; backward and m_dir != -1: GetNext, m_dir -1.

## Inputs ("CFuncTrackTrain_API::<Input>")

| Input | Does |
|---|---|
| Stop | Stop inline |
| StartForward / StartBackward | StartForward: SetDir(1), SetSpeed(max); StartBackward (180fa5db0) not described, taken as the mirror |
| Toggle | SetSpeed(speed == 0 ? max : 0) |
| Resume | speed = old speed, OnStart, Next |
| Reverse | SetDir(m_dir != 1), SetSpeed(speed) |
| SetSpeed | SetSpeed(clamp(v, 0, 1) x max) |
| SetSpeedDir | SetDir(v >= 0), a = |v|, `c = 0 <= a ? min(a, 1) : 0`, no accel, `speed = |c x max| x m_dir`, then SetSpeed's tail |
| SetSpeedReal | SetSpeed(clamp(v, 0, max)) |
| SetMaxSpeed | max only |
| SetSpeedDirAccel | SetSpeed's accel branch with c x max |
| MoveToPathNode | below |
| TeleportToPathNode | m_strPathTarget = the name; the entity of that name (any class) becomes m_ppath, ArriveAtNode, TeleportToPathTrack; velocity untouched |
| LockOrientation / UnlockOrientation | spawnflag 16 (Fixed Orientation) set, angular velocity 0 / UnlockOrientation 180fa67e0 not described (taken as clearing it) |

- **MoveToPathNode** (180fd4520): m_strPathTarget = the name; dest = FindEntityByName; no m_ppath or dest -> return; speed = m_ppath's speed, 0 -> max. dest is m_ppath: m_dir != 1 -> GetPrevious exists ? forward : Stop; else GetNext exists ? backward : Stop. Else GetNext up to 1000 nodes: found -> forward; else GetPrevious up to 1000 from m_ppath: found -> backward, else return. SetDir, SetSpeed(speed).

## Blocked (180fc0180)

- A blocker riding the train (its ground entity, vfn 0x668) with flag 1 at +0x388: pushed up by min(|speed|, 50); else its velocity += normalize(its origin - the train's) x m_flBlockDamage (1803ea4a0); spawnflag 512: an unstick after 11 ticks (m_lastBlockTick / Pos, 180fc91d0, 180e78760); then the damage.
- Reached only when SpeculativelyCheck(Linear|Rot)Push fails for a moved entity (push.md step 7). A player goes through 180225330 / 18024c740 (slides, never blocks); the push list skips MOVETYPE_NONE / VPHYSICS / PUSH / NOCLIP. Only a non-player the pusher moves (a thrown grenade's own movetype, an NPC) can block a train.

## Unread

- Teleport (1803ede40: abs or local).
- SoundUpdate (180fe36a0) / SoundStop (180fe3500) in this build (only the 2026-09-23 build's bodies read); Use (180ff0ec0) and the control volume.
- CPathTrack::Link / Activate (m_pprevious, m_paltpath) and its inputs in this build.
- NearestPath (180fd6310); the keyvalue names (Source's speed / startspeed / wheels / height / bank / orientationtype / velocitytype / manual*).
- Spawnflags 512 / 1024's other flags.
- Native re-check after an update: `dotnet run -c Release --project rubikon/tests/SceneOracle -- <binaries> trn.bin 1000000 --trains`, then `cargo run --release -p ze-sim --bin trains_check -- trn.bin`.
