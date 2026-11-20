# Player movement (CCSPlayer_MovementServices)

server_20261105 (client_20261105 for the move buttons, vphysics2_20261103 for the surface load). CS2Fixes
gamedata/cs2fixes.jsonc, src/patches.cpp (the movement unlocker); CS2Fixes sdk public/const.h (the flags).

`svc` = CCSPlayer_MovementServices (RCX), `mv` = CMoveData (RDX), `pawn` = svc+0x38. "read" = decompiler only; sums
still to check in the disassembly where they decide bits.

## Functions

| Address | Module | What |
|---|---|---|
| 180c7b050 | server | per-command caller: CheckMovingGround (vfn 0x168), vfn 0x108 (returns the CMoveData), 180c60a80, SetupMove, the subtick loop, FinishMove |
| 180c60a80 | server | (mv, cmd, tick = globals+0x44, force): the command's span |
| 180c7e8d0 | server | base SetupMove (player_movementservices.cpp:0x2b4) |
| 180ae2320 | server | CCS SetupMove (vfn 0x110) |
| 180c7eba0 | server | step builder: the cmd's steps, the last at 1.0, equal-angle steps pruned; vfn 0x120 at its end (180c7efe1) |
| 180ae2c50 | server | vfn 0x120: the step builder's own cuts (call at 180ae2f90 to 180ae2a50) |
| 180c7f0f0 | server | the base class's vfn 0x120, runs first (unread) |
| 180ae2a50 | server | (jump, mv): the modern jump's cuts |
| 180c78620 | server | (mv, f): insert a cut (skips 0, 1, a time already listed) |
| 180c78450 | server | the weapon's times into mv+0x78's own list (not movement's) |
| 180c70c90 | server | (svc, time, mv, force): the apex cut |
| 180c6f2a0 | server | CPlayer_MovementServices::DoMovement::Subtick (player_movementservices.cpp:0x711) |
| 180c610b0 | server | (mv): cuts the piece |
| 180c80540 | server | applies a step's button |
| 180ae26b0 | server | vfn 0x118: before each piece |
| 180adf830 | server | PlayerMove (vfn 0xe0) |
| 180ac4c00 | server | vfn 0x138: after each piece |
| 180ac4b20 | server | FinishMove (vfn 0x130) |
| 180c701a0 | server | base FinishMove |
| 180c70140 | server | base FinishMove's vfn 0x140: mv+0x14 -> pawn+0xbc8 (v_angle; the old one to +0xbd4) |
| 180adc390 | server | the movetype switch (PlayerMove's dispatch) |
| 180adc860 | server | the frozen / dead / can't-move move |
| 180adca80 | server | FullWalkMove(svc, mv, skipPrelude) |
| 180adce30 | server | the prelude -> bool (0: stop) |
| 180abb1d0 | server | CategorizePosition(svc, mv, bool) |
| 180abcf10 | server | CheckParameters(svc, mv) |
| 180ae34a0 | server | AirMove(svc, mv) |
| 180aea7d0 | server | WalkMove(svc, mv) |
| 180ac5310 | server | Friction(svc, mv) |
| 180ab6c70 | server | Accelerate -> 180ab6d30(svc, mv, frametime, wishdir, wishspeed, accel) |
| 180ab7420 | server | AirAccelerate(svc, mv, wishdir, wishspeed, accel) |
| 180ab72d0 | server | AddGravity |
| 180ae6e40 | server | TryPlayerMove(svc, mv, firstDest*, firstTrace*, blocked*) |
| 180ae49a0 | server | StepMove(svc, mv, oldOrigin*, oldVelocity*) -> bool |
| 180ae4660 | server | StayOnGround |
| 180ad2d00 | server | IsStandable(svc, trace) |
| 180ae1cf0 | server | SetGroundEntity(svc, mv, trace*) |
| 180ae5df0 | server | CategorizePosition's hull-sweep fallback over the four quadrants? |
| 180ac1ec0 | server | Duck(svc, mv) |
| 180ac47e0 / 180ac4ef0 | server | FinishDuck / FinishUnDuck |
| 180abab50 | server | CanUnduck |
| 180ac51a0 | server | (svc, mv, 1) after FinishDuck's shift (unread) |
| 180abbcb0 | server | legacy jump object (svc+0x6b8) tick |
| 180abc3f0 | server | legacy CheckJumpButton(jump, mv) |
| 180abbe60 | server | modern jump object (svc+0x6d0) tick (jump, mv) |
| 180ae66b0 | server | modern CheckJumpButton(jump, mv) |
| 180ae6ac0 | server | the modern jump itself |
| 180ab8d30 / 180ab8da0 | server | the jump's stamina scale: legacy (jump) / modern (jump, t) |
| 180ad63f0 | server | PreventBunnyJumping |
| 180ada490 | server | the jump's record |
| 180adbeb0 | server | jump sound / animation (pawn, origin, surface, flag): always Default.WalkJump |
| 180abb840 | server | CheckFalling(svc, mv) |
| 180ada630 | server | modern landing record (jump, mv, fall) |
| 180adaaa0 | server | the landing (pawn, fall) |
| 180adc190 | server | fall damage (mv) |
| 180ade0a0 | server | impact punch (svc, mv, scale) |
| 180adcb90 | server | PlayerMove_PostMove(svc, mv, slide); 180adc694 is the noclip call (slide 0) |
| 180adeec0 | server | v -= base velocity; v += half (the second half-step) |
| 180adef70 | server | AirMove's air record (jump, mv) |
| 180abd670 | server | CheckStuck's gate (svc, mv) |
| 180abd6c0 | server | CheckStuck(svc, mv) |
| 180ac0e60 | server | CreateStuckTable |
| 180ae5650 | server | TestPlayerPosition(svc, &h, mv, pos, group, &trace) |
| 180abdab0 | server | CheckVelocity(svc, mv, caller name) |
| 180abe290 | server | CheckWater |
| 180abe530 | server | CheckWaterJump |
| 180add3f0 | server | the water move's dispatch; 180aeb880 the water move |
| 180adf4b0 | server | ladder move (LadderMove returns at once for noclip: 180ad522c) |
| 180ada5e0 | server | IsLadder (a climbable surface too) |
| 180ad5150 | server | ladder test in the prelude |
| 180ac5640 | server | noclip / observer move (svc, mv, speed, accel) |
| 180ac5720 | server | movetype 4 move |
| 180ae9260 | server | the view offset (svc, frametime) |
| 180a73870 | server | the stair estimator (est = svc+0x290) -> bool |
| 180a707a0 | server | estimator probe (est, start, end, box, &h) |
| 180a7ec80 | server | rect overlap area |
| 180a7a830 | server | estimator result (its +0x34, FLT_MAX read as 0) |
| 180a6af20 | server | estimator cache insert |
| 180ab5b80 | server | estimator free |
| 180242350 | server | SetViewOffset(pawn, view) |
| 1806892e0 | server | CNetworkViewOffsetVector constructor |
| 180158e30 | server | (pawn, out, pawn+0x818, 1): view offset through the node |
| 180ac6340 | server | the eye (grenades.md) |
| 180ae4570 | server | (pawn): the jump's pose for the weapons |
| 180ae54a0 | server | CCSPlayerPawn::Teleport (vfn 0x528); unreferenced: view offset step 6 alone |
| 180ae2020 | server | movement services reset (m_flMaxspeed 260; pawn vfn 0xb70(out, 1)) |
| 180c7d520 | server | observers' view offset (0x18177bf80) |
| 180c6b810 | server | constructors writing mv+0x124 |
| 180ab4dc0 | server | svc constructor (m_ModernJump's at 180ab5169; the estimator's at 180ab4e33..56) |
| 180ab4c60 | server | m_ModernJump constructor (vtable 0x181923ee8) |
| 180ae9a50 | server | CS UpdateStepSound (svc vfn 0x1a8) |
| 180c80000 | server | base UpdateStepSound |
| 180c80100 | server | the step-sound decision |
| 180ae2230 | server | SetStepSoundTime (vfn 0x1c0) |
| 180c7ba40 | server | PlayStepSound (vfn 0x1b0) |
| 180adc080 | server | svc vfn 0x1d0: PlayStepSound + player_footstep |
| 180c718e0 | server | vfn 0x1b8: 135 walk, 220 run |
| 180ac65a0 | server | vfn 0x1a0: ladder surface (svc+0x404 index, else 180c71630 by hash) |
| 180ae0230 | server | CSMovementVelocityQuantizer_t |
| 1803c1030 | server | CQuantizedFloatEncoder setup (enc, name, bits, flags, lo, hi) |
| 1803c1de0 | server | quantize |
| 1803c6a80 | server | the multiplier (bits, range) |
| 1803d6020 | server | m x range overflow test |
| 1803c1f70 | server | value already exact on the grid |
| 180c7e550 | server | view punch setter (camera, angle*, time*) |
| 180a7aab0 | server | view punch getter: CCSPlayer_CameraServices vfn 0x108 (inline at 1802cc150, 180ade146, 180a9ef81) |
| 180a9ef60 | server | vfn 0xf8: punch add = decayed + delta (1809f5b10), time null |
| 180c7e550 callers | server | respawn 180216260 (from 180249530 "Player.Respawn"), 180ade0a0, CheckFalling (180abbae2), Recoil 180a4c5d0 (through 180a9bda0) |
| 180aba720 | server | pawn "can move" vfn 0xcb8 |
| 0x180ae3280 | server | ShouldHitEntity(filter, entity) |
| 180ae7da0 / 180ae7c60 | server | stand-on-head rules (hit, mover) / (h, m, z) |
| 180ad2840 | server | (me, other): stand on another player |
| 180fe1050 | server | (info, other): player info record |
| 180ac8970 | server | (pawn): first live connected pawn standing on this one |
| 180c70950 | server | (svc, button, down): queue a button |
| 180ae1cf0 helpers | server | 180e95a10 (store ground handle), 180c7e7d0 (touch, keeps the surface), 180c60e40(mv, trace+0x90), 180e8b700 (pawn vfn 0x670: ground changed, vfn 0x678 / 0x680 both `ret`) |
| 180c4d5f0 | server | AddTouch (mv, trace, v): touch list, sums normals into mv+0xb0 |
| 180addc00 | server | TraceShape with the movement filter (svc+0x7b0) |
| 180ab55b0 | server | movement filter builder |
| 180adefc0 | server | (svc+0x7b0, hull, origin, filter, maxspeed / 64, stepsize): an unstick? |
| 180cb7b90 | server | GetViewVectors (hull table) |
| 180ab9560 | server | CalcRoll |
| 1801fe910 | server | AngleNormalize |
| 181472530 | server | AngleVectors |
| 180460960 | server | Approach(target, value, step) |
| 1801d3440 | server | RemapValClamped |
| 180c010c0 | server | game surface table load -> 18158b9f0 -> 18158ba90(loader, kv, physprops) |
| 180be8f60 | server | surface entry parse (loader vfn 0x10) |
| 180beeb90 | server | loader vfn 8: entry[k] = entry[base] |
| 180c07590 | server | loader vfn 0: defaults |
| 180c00e80 | server | surface record -> game entry (record +0x10 index) |
| 18054ba10 | server | murmur2 (seed 0x31415926) |
| 180073760 | vphysics2 | loads physprops |
| 1809562c0 | server | the round's times |
| 1809669f0 | server | CCSGameRules Think |
| 180913f80 / 180916fb0 | server | freeze expiry / round time |

### Helpers

| Address | What |
|---|---|
| 180a42950 | dot(a, b) = `(a.z b.z + a.y b.y) + a.x b.x` (disasm) |
| 1801cd370 | length2D = `sqrt(x² + y²)` (disasm) |
| 180225130 | length 3D (order TODO) |
| 1802d4490 | small-vector test (0.01) |
| 1801783b0 / 1801783c0 | max(*a, *b) / min (minss) |
| 18017b8d0 | clamp(v, lo, hi): lo when lo > v, hi when v > hi |
| 18017e2d0 | f32 three-way compare |
| 180148890 | normalize |
| 1814738b0 | the f64 normalize: the fallback for lengths outside 1e-17..1e17 (18008d4e0's shape) |
| 180ae10d0 | (mv, axis, v): velocity[axis] = v, a[axis] = 0, half[axis] = 0 |
| 180187770 | read a float cvar |
| 1802a8a50 | reads sv_gravity |
| 180189990 | (mv+0xe8, 0, 0, 0) clear |
| 180c5fdb0 | (mv) at the prelude's start |
| 180308890 | 1/64 (0x3c800000, the tick interval) |
| 180ac7100 | frametime |
| 180ac70e0 | (mv) = mv+0xe0 - mv+0xdc (the piece of the tick this move covers) |
| 180ac70d0 | sv_stepsize (1821d3588) |
| 180ac6db0 / 180ac6e10 | hull mins / maxs |
| 180ac6af0 | (svc) the pawn |
| 180c856b0 | fills svc+0x38 |
| 1803d95f0 | m_nActualMoveType |
| 1803d9090 | m_lifeState (pawn+0x2d8) |
| 1803d9e40 | water level int(v x 4 + 1) |
| 1803d9e70 | water type |
| 1803d6f50 | GetAbsOrigin (node +0xc8) |
| 1803d7090 / 1803d6fb0 | abs velocity (pawn+0x38c; 1803d6fb0 unless EFL_DIRTY_ABSVELOCITY: m_iEFlags bit 12, 180ce7940) |
| 1803d7740 | base velocity (m_vecBaseVelocity pawn+0x3c8) |
| 1803d91c0 | the pawn's velocity |
| 1803d8270 | pawn friction |
| 1803dfd50 | IsFloating |
| 1803ea3b0 / 1803ea4a0 | SetAbsOrigin / SetAbsVelocity (pawn+0x38c, exact) |
| 1803ea860 | SetBaseVelocity |
| 1803eb7d0 | (pawn, type, 0) set movetype |
| 1803ebff0 | m_flWaterLevel setter |
| 1803ec0d0 | m_nWaterType setter |
| 1803c5940 / 1803e8520 | m_fFlags bit on / off (then flags-changed callback 180536730) |
| 180cf7020 | (pawn) alive? (> 0) |
| 180b5d1b0 | (pawn) observer (pawn+0xb28 vfn 0xb8 != 0) |
| 180c80ad0 | (svc, button) pressed this piece |
| 180c80890 | the move's int-to-float (unread) |
| 180c7eb90 | before vfn 0x118 (unread) |
| 180c86b20 | movetype |
| 180c86c00 | (svc, &slot) player slot (180b55410: controller index - 1) |
| 180c8cbc0 | (svc, &i) the pawn's entity index (1813aa290) |
| 1801883f0 | CSkeletonInstance: the scene node's vfn 0x60 (180cad5d0's check) is the node itself; render offset +0x120 + 0xe8..0xf0 |
| 180c86d00 / 180927cb0 | pawn identity +0x38 / curtime (globals+0x30) |
| 1809209f0 | (out, tick, flag): the tick as is when the flag (180c86d00: pawn+0x10 -> +0x38, the identity's m_worldGroupId) is set, else (0) through the gamerules' 180de69a0 (paused ticks, global +0xc0, taken off) |
| 180c629e0 | seconds = `tick x 1/64 + frac x 1/64` |
| 180c51bc0 | GameTime from seconds: (int((s - fmodf(s, 1/64)) x 64 + 0.5), fmodf(s, 1/64) x 64) |
| 1813b8ef0 / 1813b9ab0 | build a GameTime (tick, frac): a frac outside [0, 1) carries whole ticks (V_modff) |
| 1813b8fb0 | (a, out, b) a - b (a negative fraction borrows a tick) |
| 1813b9090 | (a, out, b) a + b: s = b.frac + a.frac, frac = s >= 1 ? s - 1 : s, tick = b + a (+ 1 unless s < 1) |
| 180ab6ad0 | (a, out, b) three-way compare: ticks differ -> -1 when a's is lower else 1; equal -> -1 / 1 by fraction, 0 equal, -128 (0x80) unordered |
| 180ac65f0 / 180ac5f50 / 180ac5ec0 | landed (+0x20 / 0x24) / landed + W / landed + one tick |
| 1801f95a0 / 18017dc70 | subss / addss |
| 1801f95b0 | time difference |
| 18029f040 | punch + view per lane |
| 1802b9f70 | scale a vector |
| 1801f9480 | any lane unequal (ucomiss) |
| 1802c35a0 | DidHit: fraction < 1 or start solid |
| 1803e5180 | (v) direction |
| 18021a120 | stuck statistic (pawn+0x15c0, a global count) |
| 180b54920 | the controller's command number |
| 180c84440 / 180c86b40 | connected state / per-slot pawn |
| 18093d780 | pause: -> 180deb490 -> gamerules vfn 0x340 (180de8750), m_bGamePaused |
| 180de86d0 | game time |

## Fields

### CMoveData

| Offset | Field |
|---|---|
| mv+0 | bit 0 = (cmd+0x90 != 0) \|\| force, bit 1 = (cmd+0x90 != 0) |
| mv+4 | the pawn's handle |
| mv+8, +0x14 | view angles (SetupMove); +0x14 the move angles, AngleVectors' input |
| mv+0x2c / 0x30 / 0x34 | forward / side (left) / up move (CheckParameters scales by maxspeed at its end) |
| mv+0x38 / 0x3c / 0x40 | velocity |
| mv+0x44 / 0x48 / 0x4c | view angles + punch (CheckParameters; nothing else reads them) |
| mv+0x60 / 0x68 | subtick step count / array (0x20 bytes: +0 when, +8 button, +0x10 pressed, +0x10 / +0x14 analog deltas, +0x18 / +0x1c view angles) |
| mv+0x78 | the weapon's own time list |
| mv+0xb0 | sum of touch normals |
| mv+0xc8 / 0xcc / 0xd0 | origin |
| mv+0xd4 / 0xd8 | start / end tick |
| mv+0xdc / 0xe0 | start / end fraction |
| mv+0xe8 | outgoing wish (cleared at the prelude) / Friction's v |
| mv+0xf0 | the jump's vz added |
| mv+0xf4..0xfc | the command's angles (= pawn+0xbc8) |
| mv+0x100 / 0x104 | wish velocity (WalkMove) |
| mv+0x108..0x110 | the piece's acceleration a (`a = Δv / frametime`, integrated half before, half after) |
| mv+0x114..0x11c | the half step already applied (taken back out at the end) |
| mv+0x120 | max speed |
| mv+0x124 | m_flMaxspeed copy (svc+0x1ac, 260) |
| mv+0x128 | Friction's leftover `max(0, drop - speed)` |
| mv+0x12c / 0x130 / 0x134 | air record: origin.z / vz - (a.z x frametime) x 0.5 / a.z |
| mv+0x138 | the piece starts airborne |
| mv+0x139 | the command right after a Teleport (cmd+8 == svc+0x680 + 1) |
| mv+0x13a | the speed latch's set |

### Movement services

| Offset | Field |
|---|---|
| svc+0x38 | pawn |
| svc+0x48 | buttons cleared when frozen |
| svc+0x50 / 0x70 / 0x78 / 0x190 / 0x198 | button state (180c70950) |
| svc+0x58 | buttons (u64): bit 0 IN_ATTACK?, bit 1 IN_JUMP, bit 2 IN_DUCK, 8 IN_FORWARD, 0x10 IN_BACK, 0x200 IN_MOVELEFT, 0x400 IN_MOVERIGHT, 0x10000 IN_SPEED |
| svc+0x188 | m_nLastCommandNumberProcessed: the usercmd's number, stored at 180c7ff17 before the movement (that code also fills the pressed-button command numbers) |
| svc+0x1a0 / 0x1a4 / 0x1a8 | usercmd forward / left / up (CBaseUserCmdPB cmd+0x40 +0x58 / +0x5c / +0x60; 180c7ff64..ff8f, also 180c7b39a) |
| svc+0x1ac | m_flMaxspeed (260) |
| svc+0x1b0 | four-slot list for apex times past the command |
| svc+0x1c0.. | base FinishMove's moves |
| svc+0x238 | queued releases |
| svc+0x258 | m_flStepSoundTime |
| svc+0x25c | m_flFallVelocity |
| svc+0x26c | m_surfaceFriction |
| svc+0x270 / 0x278 | landed surface hash / record (never cleared) |
| svc+0x280 | foot toggle |
| svc+0x290 | stair estimator |
| svc+0x310 | 180a9d5a0 at FinishMove |
| svc+0x368 | set by the jump |
| svc+0x3f0 / 0x3f4 | estimator set / view ease |
| svc+0x404 | m_nLadderSurfacePropIndex |
| svc+0x408 | m_bDucked |
| svc+0x40c | m_flDuckAmount |
| svc+0x410 | m_flDuckSpeed |
| svc+0x414 | m_bDuckOverride (C4 arming 180a23df0; CanUnduck refuses) |
| svc+0x415 | IN_DUCK copy |
| svc+0x416 | m_bDucking |
| svc+0x418 | m_flDuckOffset (view) |
| svc+0x41c | view duck ease |
| svc+0x420 | m_flLastDuckTime |
| svc+0x424 | jump-duck offset (0 / -8) |
| svc+0x428 | the ground trace's surface record |
| svc+0x430 | where the duck speed last recovered |
| svc+0x438 | duck-jump in the air |
| svc+0x439 | set by WalkMove, cleared by the jump |
| svc+0x43a | m_bInStuckTest (written only by CheckStuck and PlayerMove 180adfb4b; no reader in 0x180a00000..0x180d00000) |
| svc+0x440 | CheckVelocity's warn CUtlMap |
| svc+0x448 + slot x 4 | CheckStuck's last time (not a schema field) |
| svc+0x648 | trace count |
| svc+0x64c | m_StuckLast |
| svc+0x650 | duck slowdown applied this tick |
| svc+0x654 / 0x658 | water level at the prelude's end / time entered |
| svc+0x65c / 0x668 / 0x674 | AngleVectors forward / right / up |
| svc+0x680 | command number at the Teleport |
| svc+0x684 / 0x688 | footstep flag / count |
| svc+0x68c | m_fStashGrenadeParameterWhen (the jump stamp) |
| svc+0x690 / 0x694 / 0x698 | m_bUseFrictionStashedSpeed / m_flUseFrictionStashedSpeedUntilFrac / m_flFrictionStashedSpeed (the speed latch) |
| svc+0x69c | m_flStamina |
| svc+0x6a0 | m_flHeightAtJumpStart |
| svc+0x6a4 / 0x6a8 | m_flMaxJumpHeightThisJump / LastJump |
| svc+0x6ac | m_flStaminaAtJumpStart |
| svc+0x6b0 | m_flVelMulAtJumpStart |
| svc+0x6b4 | m_flAccumulatedJumpError |
| svc+0x6b8 | m_LegacyJump (+8 svc, +0x10 m_bJumpBlocked?, +0x14 last press time) |
| svc+0x6d0 | m_ModernJump (below); its fields at svc+0x6e0..0x700: 0x6f0 / 0x6f4 m_nLastLandedTick / Frac, 0x6f8..0x700 m_flLastLandedVelocityX / Y / Z |
| svc+0x708 / 0x70c | m_nLastJumpTick / m_flLastJumpFrac |
| svc+0x710 | m_flLastJumpVelocityZ |
| svc+0x714 | m_bJumpApexPending |
| svc+0x718 | m_flTicksSinceLastSurfingDetected |
| svc+0x7a8 / 0x7ac | the last piece's wish |
| svc+0x7b0 | the trace helper |
| svc+0xdcc | cleared by PostMove |
| svc+0xfd4 | start-solid ground trace counter (> 31: 18021a120) |

m_ModernJump (svc+0x6d0): +8 svc, +0x10 / 0x14 m_nLastActualJumpPressTick / Frac (-1024 / 0), +0x18 / 0x1c
m_nLastUsableJumpPressTick / Frac (-1024 / 0; "cleared" = tick -1024 (0xfffffc00), the fraction kept), +0x20 / 0x24
m_nLastLandedTick / Frac (0 / 0), +0x28 / 0x2c / 0x30 m_flLastLandedVelocityX / Y / Z (0). Networked notifies, one a
field: 180ad9d00, 180ad85b0, 180ada0a0, 180ad8f60, 180ad9f70, 180ad8aa0, 180ad8bd0, 180ad8d00, 180ad8e30. The reset
180ae2020 doesn't touch it.

### Pawn and others

| Offset | Field |
|---|---|
| pawn+0x270 | body component (vfn 0x60 -> 180cad5d0: +0x120 render offset, z +0xf0; vfn 0x68 -> 180cb8910 -> 180cb8770) |
| pawn+0x2d8 | m_lifeState |
| pawn+0x2f2 | cleared leaving a ladder |
| pawn+0x344 | m_iTeamNum |
| pawn+0x388 | m_fFlags: bit 0 FL_ONGROUND, 1 FL_DUCKING, 2 (4) FL_WATERJUMP, 5 FL_FROZEN (0x20), 6 FL_ATCONTROLS (0x40), 12 |
| pawn+0x38c | m_vecAbsVelocity |
| pawn+0x3c8 | m_vecBaseVelocity |
| pawn+0x3d8 | m_pCollision (vfn 0x228, 1801575b0) |
| pawn+0x3ec | m_hGroundEntity |
| pawn+0x404 | m_flWaterLevel |
| pawn+0x40c | gravity scale |
| pawn+0x412 | m_nWaterType (datamap 0x181ddfc40): bit 0 water (contents bit 15), 2 slime (bit 16) |
| entity+0x414 | m_iEFlags (datamap 0x181ddfc60): bit 5 refused by CheckWaterJump, 12 EFL_DIRTY_ABSVELOCITY, 19 floating |
| pawn+0x5e8 / 0x608 | m_Collision / m_collisionAttribute.m_nInteractsWith (attribute +0x10, interacts-with +0x10) |
| pawn+0x818 | m_vecViewOffset (CBaseModelEntity; floats +0 / 4 / 8, m_vecX +0x10, m_vecY +0x18, m_vecZ +0x20; encoders pawn+0x828 / 0x830 / 0x838 +4, chain pawn+0x824) |
| pawn+0xb10 | weapon services (active weapon 0x162 x 8) |
| pawn+0xb28 | observer services |
| pawn+0xb30 | water services: +0x54 water-jump / trigger timer, +0x58 / 0x5c / 0x60 jump speed, +100 swim sound timer |
| pawn+0xb48 | camera services (vfn 0x108 punch) |
| pawn+0xb50 | movement services (+0x1ac, +0x408) |
| pawn+0xbc8 / 0xbd4 | v_angle / the old one |
| pawn+0xc98 | controller handle |
| pawn+0xd30 | ping services |
| pawn+0xd40 | must be 0 / 6 to move |
| pawn+0xdf1 | set when moving |
| pawn+0xe38 | m_pHostageServices (+0x48 m_hCarriedHostage) |
| pawn+0x1478 | m_bIsWalking |
| pawn+0x14be / 0x14bf / 0x14c0 | m_bIsDefusing / ... (any set: can't move) |
| pawn+0x14e0 | velocity modifier |
| pawn+0x1560 / 0x1564 | jump stamp copy / pose taken |
| pawn+0x1568 / 0x1574 / 0x1580 / 0x158c | jump pose: eye angles + aim punch / eye / trace start (vfn 0x2c8) / velocity |
| pawn+0x15a4 / 0x15a8 | jump cooldown (unread) |
| pawn+0x15c0 | stuck statistic |
| weapon+0xec0 | clip (vfn 0xac0, 1809be910) |
| weapon+0xfa8 | m_bInReload (schema 180a09571) |
| weapon+0x12c9 | C4 arming flag (can't move) |
| vdata+0x7dc | m_flAttackMovespeedFactor (vfn 0xc58, 1809be800) |
| camera+0x48 / 0x54 / 0x58 | m_vecCsViewPunchAngle (QAngle) / tick / fraction |
| collision+0x20 | interacts-with (m_collisionAttribute.m_nInteractsWith: pawn+0x608 for a pawn) |
| collision+0x40 | OBBMins (180d04ee0) |
| collision+0x4c | OBBMaxs (180d04ed0) |
| collision+0x5e | m_CollisionGroup |
| trace +0 / +8 / +0x28 / +0x68 / +0x8c / +0x90 / +0x98 / +0xbb | surface record (+8 hash) / body / layers / 0x8000 world / end z / normal / normal z / start solid |
| gpGlobals (PTR_DAT_181e328d0) +0x10 / +0x30 / +0x34 / +0x44 / +0x70 | player slots / curtime / frametime / tick / (frozen test) |
| CCSGameRules (0x1821ba1c0, vtable 0x1818c5450) | m_bGamePaused +0xc8, m_bFreezePeriod +0xd8, m_bWarmupPeriod +0xd9, m_bTerroristTimeOutActive +0xe4, m_iFreezeTime +0xfc, m_iRoundTime +0x100, m_fRoundStartTime +0x108, m_bIsValveDS +0x13c, +0x1148 |

Hull table 180cb7b90 (GetViewVectors): +0 view (0, 0, 64), +0xc / +0x18 hull min / max (z 0 / 72; max.z 0x20, min.z
0x14), +0x24 / +0x30 duck hull (z 0 / 54; dmax.z 0x38, dmin.z 0x2c), +0x3c duck view, +0x48 / +0x54 observer hull.

## Constants

Registrations: the data pointer is the handle + 8; the value struct's +0x37 is the default.

| Handle / data | Cvar | Default |
|---|---|---|
| 182175438 / 182175440 | sv_staminarecoveryrate | 60 (0x182175430 is dev_create_move_report's data) |
| 182175490 / 182175498 | sv_step_move_vel_min | 64 |
| 181ff5798 (DAT_181ff57a0) | sv_gravity | 800 |
| 1821754c8 | sv_jump_impulse | 301.993378 (0x4396ff27) |
| 182175448 | sv_staminamax | 80 |
| 1821753b8 / 1821753c8 | sv_staminajumpcost / landcost | 0.08 / 0.05 |
| 1821754d8 | sv_jump_spam_penalty_time | 0.015625 |
| 182175458 | sv_timebetweenducks | 0.4 |
| 182175518 / 182175520 | sv_standable_normal | 0.7 |
| 182175508 / 182175510 | sv_walkable_normal | 0.7 |
| 1821754e8 | sv_air_max_wishspeed | 30 |
| 1821d3588 | sv_stepsize | 18 |
| 1821d34d8 | sv_maxspeed | 320 |
| 182175568 / 182175570 | sv_water_slow_amount | 0.9 |
| 1821d3568 / 1821d3570 | sv_bounce | 0 |
| 1821d3558 / 1821d3560 | sv_friction | 5.2 |
| 1821d3458 / 1821d3460 | sv_stopspeed | 80 |
| 1821d34e8 / 1821d34f0 | sv_accelerate | 5.5 |
| 1821d34f8 / 1821d3500 | sv_airaccelerate | 12 |
| 182175578 / 182175580 | sv_jump_precision_enable | 1 (TryPlayerMove's z snap, the jump's 196608 rounding; 0x82000) |
| 182175468 / 182175470 | sv_accelerate_use_weapon_speed | 1 (0x82100) |
| 182175600 / 182175608 | sv_optimizedmovement | 1 (0x2002 FCVAR_DEVELOPMENTONLY; the prelude skips CategorizePosition for WALK, only vz > 250 clears the ground) |
| 182175620 / 182175628 | sv_autobunnyhopping | 0 |
| 1821755a8 / 1821755b0 | sv_legacy_jump | 0 (GFL runs 1; registered 1800c9ad0, 0x82000: a map can set it) |
| 182175400 / 182175408 | sv_bhop_time_window | 0.0078125 (0x18179be50; registered 1800c9040, 0x82000; "sv_legacy_jump disabled only: The time window (in seconds) around landing where a jump press is considered a bhop attempt.") |
| 182175588 / 182175590 | sv_quantize_movement_input | 1 (0x82000; "Quantize movement input values. Enabling this restricts players from using analog input to move at fractional speeds normally impossible with digital button input.") |
| 0x181922ce0 / c40 / cb0 (names) | sv_ladder_scale_speed / dampen / angle | 0.78 / 0.2 / -0.707 (0x82000) |
| 1821754a8 / 1821754b0 | sv_use_playercache | 1 (a trace cache: same results) |
| 182175478 / 182175480, 182175488 / 182175490 | sv_accelerate_debug_speed, sv_show_move_collisions | debug |
| 18211a3a8 / 18211a3b0 | mp_solid_teammates | 1 (int, 1800a1f30: "0 = transparent; 1 = fully solid; 2 = can stand on top of heads"; 18093e970 = value != 0 && != 2) |
| 18211a3b8 / 18211a3c0 | mp_solid_enemies | 1 (int, 1800a1e80; 18093d680 = value != 0) |
| 0x1821d3578 | sv_maxvelocity | 3500 (0x82000, registered 180104100) |
| 0x1821754f8 | view_punch_decay | 18 |
| 0x182191440 | sv_suppress_viewpunch | 0 (0x6002) |
| 0x1821d3528 | sv_footsteps | 1 (0x2102 FCVAR_DEVELOPMENTONLY, "Play footstep sound for players") |
| 0x182119ec8 | mp_freezetime | 6 (int, 18009ef00, 0x282100, "how many seconds to keep players frozen when the round starts"; gamemode_casual.cfg 5, competitive 15) |
| 0x1821d3538 / 0x1821d3548 | sv_rollspeed / sv_rollangle | 200 / 0 (CalcRoll) |
| 0x1821b9a20 | host_timescale | |
| 0x1821756c8 | dev_cs_force_disable_move | (pawn vfn 0xcb8) |
| 0x1821753d8 / 0x182175428 | dev_create_bhop_reports / dev_create_move_report | |
| 0x1821755f0 (data 1821755f8) | bot_crouch | (the duck's forced duck, with pawn vfn 0xc20) |
| 0x182175610 | sv_enablebunnyhopping | |
| 0x182175768 | sv_max_distance_transmit_footsteps | |
| 0x181f9e210 | bot_mimic | SetupMove (180ae24bd) zeroes a bot's moves when bot_mimic == its slot (180c86c00) + 1 |
| 0x182191538 | in_spewbuttondelta | 180c70950's debug print |
| 0x182197ee0 | developer | |
| 18211a6d8 (+0x58) | taken as mp_teammates_are_enemies (TODO name) | |
| 182175490 (DAT) | WalkMove's debug overlay (also sv_step_move_vel_min above) | |
| 182175430 | debug: with svc+0x58 & 0x61e, DAT_182175af8 = 0x80 (counted down by vfn 0x138) | |
| 1821754b0 | the prelude's unstick | |
| 1821d3548 / 1821d3538 | CalcRoll's | |

| Value | What |
|---|---|
| 0x1817d0e90 | pi/180 (0.017453292) |
| 0x18179be50 | 0.0078125 (the jump's 1/128) |
| 0x1817bc124 | 140 |
| 0x1818d21a8 | 1.0 (frozen max speed) |
| 0x1818d21a0 | 260 (PlayerMove's cap: mv+0x120 = min(260, sv_maxspeed or the pawn's +0xb50 +0x1ac), then min(weapon vfn 0xc20)) |
| 0x1818d21b4 | 0.52 |
| 0x181781734 | 0.0 |
| 0x18178057c | 0.5 |
| 0x181780580 | 1.0 |
| 0x1819269d4 | 0.0005 (0x3a03126f) |
| 0x3e4ccccd | 0.2 |
| 0x1817b2be0 | 0.6 (0x3f19999a) |
| 0x18178fe18 | 100 |
| 0x181784dec | 0.015625 |
| 0x181926a00 | 1.1111894 (0x3f8e3b74) |
| 0x181926a50 / 0x181926a54 | 131072 / 196608 rounding constants |
| 0x181926a4c | 19600 |
| 0x18178fdc8 | 0.1 (0x3dcccccd) |
| 0x18179be60 | 1.1 |
| 0x181784e08 | 3.0 |
| 0x181784df4 | 0.05 |
| 0x181784e1c | 1000 |
| 0x181784de4 | 0.0001 |
| 0x18179be5c | 0.65 |
| 0x1819269d8 | 0.013 |
| 0x1817b2bfc | 0.85 |
| 0x42700000 / 0x43160000 | 60 / 150 |
| 0x3d4ccccd | 0.05 |
| 0xc07f5c29 / 0x407f5c29 | -3.99 / 3.99 |
| 0x75de364e | "default" surface hash (surfaces.json) |
| 0xe2a5b837 / 0x5f0a183a | "ladder" / "wade" hashes |
| 0x18177bf80 | zero vector |
| DAT_181926a28 / 1817c3d60 / 18179bea4 / 181926a38 / 181926a30 / 18178fe20 / 1817b2c84 / 181784de8 | CheckFalling's thresholds (fall water sound / 350 / 200 / 580 / 290 / 250 / 1024 / 0.001) |
| DAT_1819216d0 | estimator neighbours (-1, -5, +1, +5) |

Strings: "Can't move" (VPROF), "Water.PlayerEnter" / "Exit", "Player.Swim", "Land_WaterVol.StepLeft", "CT_Water.StepLeft"
(0x1819537f0; not in client_20261105.dll), "player_footstep" (0x18178d9f8), "player_jump", "%s stuck on object %i/%s
from %s". client_20261105 "moveup" / "movedown" (0x181c65728 / 0x181c65730): nothing binds them, so
the noclip up move is 0.

CCSPlayer_MovementServices' vtable 0x181923f70 (slot 0xe0 at 0x181924050). Layers (18093b180, explicit indices,
strings 0x1818cb4b8..): 31 csgo_team1, 32 csgo_team2, 33 csgo_grenadeclip, 34 csgo_droneclip, 35 csgo_moveable, 36
csgo_opaque, 37 csgo_monster, 38 csgo_chicken, 39 csgo_thrown_grenade, 40 csgo_dropped_hostage (after vphysics2's
0..30; a name neither knows takes 41 on: TODO how server.dll numbers those).

## The command around the pieces

1. 180c7b050: CheckMovingGround (vfn 0x168), vfn 0x108, 180c60a80: mv+0xd8 = tick, mv+0xdc = 0, mv+0xe0 = 1.0, mv+0
   bits, mv+0xd4 = tick - (bit 0 ^ 1) (a normal command spans [tick - 1, tick]).
2. SetupMove (vfn 0x110), the subtick loop 180c6f2a0 (per step: vfn 0x118, PlayerMove vfn 0xe0, vfn 0x138), FinishMove
   (vfn 0x130). FL_FROZEN etc.: 180c7b42d clears as SetupMove does (with the queued releases 180c70950 over svc+0x238).

### Base SetupMove 180c7e8d0

- mv+4 handle; view angles (mv+8, +0x14); mv+0xc8 abs origin (1803d6f50); mv+0x38 abs velocity (1803d7090: exact).
- mv+0x2c / 0x30 / 0x34 from svc+0x1a0 / 0x1a4 / 0x1a8 through 180c80890: forward only with IN_FORWARD | IN_BACK,
  left only with IN_MOVELEFT | IN_MOVERIGHT, up always.
- FL_ATCONTROLS (180c7ea5a): the usercmd's moves aren't copied (stay 0); buttons and steps stay (a key changing inside
  the tick still adds its +-1: 180c6f2a0, 180c7eba0, 180c80540 read no flag).
- FL_FROZEN (180c7ead8), or 18093d780 / vfn 0x160, developer, gpGlobals +0x70, or curtime < 3 -> 180c70700(svc, 0),
  svc+0x48 = 0 (buttons gone), moves 0, the step builder told (r9 1): no input.
- Then the step builder 180c7eba0 and its vfn 0x120.

### vfn 0x120 180ae2c50: the step builder's cuts

180c78620(mv, f) inserts a step at f with no button and the *next* step's +0x18 / +0x1c (its view angles), in time
order. In order:
1. The active weapon's three times (180b54e20, 180b54e50, 180a02300) inside the command -> mv+0x78 (180c78450).
2. The speed latch: svc+0x690 set -> cut at svc+0x694.
3. sv_legacy_jump 0: 180ae2a50 (below).
4. The jump stamp: 180c51bc0(svc+0x68c), its tick == globals+0x44 - 1 (mv+0xd4) -> cut at its fraction.
5. The apex: svc+0x714 and not FL_ONGROUND and WALK (1803d95f0 == 2) and vz > 0 and mv+0 bit 0 clear:
   `a = ((sv_gravity x pawn+0x40c) x 0.015625) x 0.5`, `d = m_vecBaseVelocity.z x 0.015625 - (a + a)`; `d + vz <= 0` ->
   `t = -vz / d`; t not 0 or 1 -> 180c70c90(svc, (mv+0xd4, t), mv, 1): at or after mv+0xd8 -> svc+0x1b0's list; after
   (mv+0xd4, mv+0xdc) -> cut.

### CCS SetupMove 180ae2320 (after the base, so the cuts saw the velocity before this)

1. Not FL_ONGROUND: t = 180c629e0((mv+0xd4, 0) - (svc+0x708, 0x70c)) (1813b8fb0); `v = clamp(svc+0x710 - sv_gravity x
   pawn+0x40c x t, -16384, 16384)`; mv+0x40 == quantize(v) (180ae0230) -> mv+0x40 = v.
2. mv+0x44 = mv+0x14.
3. Interacts-with: m_lifeState 1 -> 0x800003011; else mp_solid_enemies ? 0xc3011 : 0x800003011, and with
   mp_solid_teammates 0 or 2, team 2 -> | 0x80000000, 3 -> | 0x100000000; 180d0e6a0(pawn+0x5e8, (pawn+0x608 &
   0xfffffffe7ff3cfee) | that). (The pawn's solid-mask vfn 0xb88, 180b67a60, returns 0xc3011.)
4. mv+0x13a = 0, mv+0x139 = (cmd+8 == svc+0x680 + 1), mv+0xf4 = pawn+0xbc8, mv+0x124 = svc+0x1ac (180ae2644); 180991b50
   for a live non-noclip pawn.

### The subtick loop 180c6f2a0

For each step (count mv+0x60) whose `when` differs from the last: view angles (mv+0x14) from the step when
sv_subtick_movement_view_angles (vfn 0x128); 180c610b0(mv) cuts the piece; `frametime = (mv+0xe0 - mv+0xdc) x (mv+0xd8 -
mv+0xd4 ticks) x interval`; `curtime = tick x interval + when x interval` (a when >= 1 is the next tick, < 0 the one
before); vfn 0x118 / 0xe0 / 0x138; then the step's button (180c80540) or analog deltas: IN_FORWARD 8 / IN_BACK 0x10 ->
forward +-1, IN_MOVELEFT 0x200 / IN_MOVERIGHT 0x400 -> side +-1 (sign by pressed).

### vfn 0x118 180ae26b0 (before each piece)

180c7eb90; mv+0x100..0x110 and +0x114..0x11c zeroed, mv+0x128..0x137 zeroed (180ae2706 / 0d), mv+0x138 = !(pawn+0x388 &
1); IN_JUMP's 180c80ad0(svc, 2) unless svc+0x58 bit 1; sv_quantize_movement_input -> mv+0x2c / 0x30 / 0x34 = V_roundf
(tier0 0x1800081c0 -> 0x1802a9ffc: CRT roundf, half away from zero); AngleVectors(mv+0x14).

### PlayerMove 180adf830

svc+0x650 = 0, svc+0x648 = 0; mv+0x120 = the max speed (0x1818d21a0 cap); "can move" test (180adfa5b, without the cvar
and the C4) failing -> mv+0x120 = 1.0 (180adfb35); svc+0x43a = 0 (180adfb4b); dispatch 180adc390. Telemetry add of
svc+0x648 at 180adfdd9 (lock add to 182176528).

### vfn 0x138 180ac4c00 (after each piece)

1. Not FL_ONGROUND -> `svc+0x6a4 = maxss(svc+0x6a4, ((mv+0xd0 + 196608) - 196608) - svc+0x6a0)`.
2. 180c80ad0 / 180c70950 (duck button); DAT_182175af8 counts down.
3. SetAbsOrigin (1803ea3b0) / SetAbsVelocity (1803ea4a0) from mv; 180ae9260(svc, frametime).
4. Jump stamp svc+0x68c > 0 (18017e2d0 against 0x181781734) and (mv+0xd4, mv+0xe0) >= its GameTime -> 180ae4570(pawn)
   (pawn+0x1564 = 1 and the pose) and svc+0x68c = 0.
5. svc+0x7a8 = mv+0x100 (8 bytes).

### FinishMove 180ac4b20

180c701a0 (svc+0x1c0.. the moves, SetAbsOrigin / Velocity unless movetype 5, vfn 0x140, 180c5e7c0); svc+0x25c = -mv+0x40
(180ac4b3f); svc+0x1ac = mv+0x124 (180ac4ba7); 180a9d5a0(svc+0x310); svc+0x690 = mv+0x13a.

## The movetype switch 180adc390

- Pawn vfn 0xcb8 false -> "Can't move" (180adc79d): CheckParameters, 180adc860.
- Else pawn+0xb30 with +0x54 > 0 (water-jump timer): CheckParameters, prelude, the timer (cap 10000, minus frametime x
  1000; at 0 or out of water: cleared, 1803e8520(pawn, 4)); velocity x / y from +0x58 / +0x5c; 180ae6e40, 180abe290,
  180adcb90.
- Else by movetype (1803d95f0):
  - water level (1803d9e40) > 2 and WALK: CheckParameters, 180add3f0.
  - 2 WALK: CheckParameters, FullWalkMove(svc, mv, 0).
  - 4: CheckParameters, prelude, 180ac1ec0, 180ac5720, 180adcb90.
  - 7 / 8 (noclip / observer): CheckParameters, prelude, 180ac1ec0, 180ac5640(svc, mv, sv_noclipspeed (x 1 /
    host_timescale above 1), sv_noclipaccelerate), PostMove(svc, mv, 0) (180adc694).
  - 9 LADDER: CheckParameters, prelude; still not WALK: 180ac1ec0, 180abe290, the jump object (180abbcb0 / 180abbe60),
    180adf4b0, 180ae6e40, 180adeec0, 180adcb90; became WALK: FullWalkMove(svc, mv, 1).
  - any other (0 NONE, 1, 3, 5 VPHYSICS, 6, 10+): returns at once (`if (type != 9) return`): no CheckParameters, prelude,
    duck, gravity or velocity; the pawn keeps its place and velocity. (ze_resident_evil_3's NPC grab fires `KeyValues
    movetype 1` / `movetype 2`.) CS2Fixes customio.cpp `AddOutputCustom_MoveType` (key "movetype", two tokens) is
    `SetMoveType(clamp(Q_atoi(value), MOVETYPE_NONE, MOVETYPE_LAST))` only.

### The can't-move move 180adc860

Forward / left / up 0; prelude (false: stop); FL_ONGROUND -> velocity, mv+0x108, mv+0x114 = 0x18177bf80, duck 180ac1ec0;
airborne -> `vz -= ((sv_gravity x pawn+0x40c) x frametime) x 0.5`, `vz = m_vecBaseVelocity.z x frametime + vz`,
SetBaseVelocity with z 0, CheckVelocity, duck, then (pawn+0xb30 null or its +0x54 0) the second half of gravity;
PostMove(slide 1). No jump, no walk / air move.

### Pawn "can move" vfn 0xcb8 (180aba720)

False when dev_cs_force_disable_move (+0x58), movetype NONE, pawn+0xd40 not 0 / 6, +0x14be / +0x14bf / +0x14c0 set,
the active weapon a C4 with +0x12c9, or m_bFreezePeriod unless 18093df00(gamerules) (engine vfn 0x98 / 0xa0 == 5 and a
cvar match; then 18093dd30(gamerules+0x1148, pawn): m_bIsValveDS, team 2, a freeze-time window: matchmaking only).

## FullWalkMove 180adca80(svc, mv, skipPrelude)

prelude unless skipped (0: stop) -> 180ac1ec0 -> jump object (180abbcb0(svc+0x6b8) / 180abbe60(svc+0x6d0, mv)) ->
FL_ONGROUND ? 180aea7d0 : 180ae34a0 -> 180adcb90 -> Water.PlayerEnter / Exit when the level crossed 0 (pawn+0x1478 and
+0xb50+0x408 clear).

## The prelude 180adce30(svc, mv) -> bool

1. mv+0xe8 cleared (180189990); 180c5fdb0(mv).
2. Stamina s > 0: `s -= sv_staminarecoveryrate x frametime`, < 0 -> 0.
3. pawn+0xb30 +100 timer -= frametime x 1000, floor 0.
4. 181472530(mv+0x14, svc+0x65c, svc+0x668, svc+0x674).
5. Cvar 1821754b0 on: filter 180ab55b0 (group 0xb, interacts-with pawn+0x608 | 0x20 when pawn vfn 0xc20), hull
   (180cb7b90 by svc+0x408, observer when 180b5d1b0); 180adefc0(svc+0x7b0, hull, origin, filter, maxspeed / 64,
   cvar 1821d3588).
6. Movetype not 7 / 0 / 8 and m_lifeState != 2: 180abd670 nonzero -> return 0 (stuck; call at 180add182).
7. WALK and !mv+0x139 and sv_optimizedmovement (180add1bf): vz > 250 -> 180ae1cf0(svc, mv, null); else
   CategorizePosition(svc, mv, 0).
8. svc+0x654 = water level. No ground (pawn vfn 0x668 null): WALK -> fall = max(fall, -vz) (when fall > 0, else -vz);
   else 0.
9. svc vfn 0x1a8(svc, svc+0x428, origin, velocity) (180ae9a50, call at 180add311); m_lifeState != 2 and 180ad5150 false
   and LADDER -> 1803eb7d0(pawn, 2, 0), pawn+0x2f2 = 0.
10. Returns 1. A stuck return 0: FullWalkMove does nothing more; CheckParameters, the countdowns and AngleVectors ran.

## CategorizePosition 180abb1d0(svc, mv, bool)

1. Surface friction = 1; CheckWater (with a controller, pawn+0xc98). Movetype 7 / 8 -> ground off (180abb29a), svc+0xfd4
   = 0.
2. start = end = origin; moving up = vz > 140 (relative to the ground entity's vz: vfn 0x668, 1803d6fb0).
3. On a ground with m_flWaterLevel != 1.0 (and WALK): end.z -= 180ac70d0 (step down); with the bool: end.z -=
   sv_stepsize; else end.z -= 2. LADDER and vz > 0.02, or moving up -> ground off.
4. Trace: filter 180ab55b0 (group 0xb, interacts-with 180ade310), ray from start (+0, +0, +4 on z), hull mins
   (180ac6db0) less (0, 0, 4)?, maxs (180ac6e10) — TODO the Ray_t layout (stack -0x2c8 start, -0x2b8 maxs, -0x2ac mins).
   180addc00(svc+0x7b0, trace, ray, end, ...); svc+0x428 = the surface record (180abb534; a miss: the trace reset's
   static).
5. Surface record +8 == 0x75de364e ("default"): a second trace (180abb5c7) from the same start, the movement's query
   but interacts-with 0x3001 (interacts-as 0x40000, exclude 0x40000, the pawn ignored, query flags 0x4b, iterating
   entities; 180ab55b0's arguments are only the start of the query: an interacts-as of 0 misses shapes this hits); a
   hit replaces svc+0x428. svc+0x428 is untouched when the trace doesn't run (moving up).
6. Start solid and pawn vfn 0x550: svc+0xfd4++ (> 31 -> 18021a120), else 0.
7. 180ad2d00 false: 180ae5df0, still false: ground off; vz > 0 and not 7 / 8 -> friction 0.25. True: ground on
   (180ae1cf0(svc, mv, trace)); step down taken, not start solid, 0 < f < 1: origin = trace end.

## CheckParameters 180abcf10(svc, mv)

1. IN_DUCK changed (svc+0x415 vs bit 2): store; `svc+0x410 = max(0, svc+0x410 - 2)`. svc+0x438 cleared while ducking.
2. Walk (IN_SPEED, not IN_DUCK, not svc+0x416, not FL_DUCKING): speed (180225130 of 1803d91c0) < `maxspeed x 0.52 + 25`
   -> maxspeed x= 0.52, m_bIsWalking = 1; else 0.
3. Not 7 / 8 (180abd0fa): k = svc+0x278 ? *180c00e80() (maxspeedfactor) : 1; FL_ONGROUND: k *= pawn+0x14e0; active
   weapon with buttons bit 0 and vfn 0xac0 (the clip; skipped while m_bInReload): k *= vfn 0xc58; maxspeed *= k.
   Stamina s > 0: `maxspeed = clamp(1 - s / 100, 0, 1)^2 x maxspeed`.
4. Modern landing slowdown (180abd251..36d; still inside step 3's not-7 / 8 block, after the stamina; sv_legacy_jump 0
   and a ground (pawn vfn 0x668)): f = `clamp(svc+0x700 x 0.0005 + 1.0, 0.2,
   1.0)`, d = now - landed (1813b8fb0); `x = (float(d.tick) x 0.015625) x 1.1111894 + f x f` (cvtdq2ps: the fraction
   unused); `mv+0x120 = minss(x, 1.0) x mv+0x120`.
5. Moves zeroed unless (not FL_FROZEN (bit 5, 180abd3a8) and 180cf7020 > 0), or the observer mode is 4.
6. Angles (180abd406..4e3): dead -> mv+0xf4; alive -> view + punch (18029f040), roll = CalcRoll 180ab9560(svc, angles,
   velocity, sv_rollangle, sv_rollspeed) unless 7 / 8 (180abd472); yaw = 1801fe910.
7. Stack (180abd51b..0x180abd629): not 180b5d1b0 and not LADDER: count = 0; g = vfn 0x668; while g is a pawn and count < 2: g =
   vfn 0x668(g), count++. count > 1 -> mv+0x2c = mv+0x120 x 3.0, mv+0x30 = 0, then 180c70950(svc, b, 0) for 8, 0x10,
   0x200, 0x400, 2, 4.
8. forward / side / up x= mv+0x120.

AngleNormalize 1801fe910: outside [-180, 180] or NaN, `a - floorf(a x (1/360) + 0.5) x 360`, then maxss(-180),
minss(180). AngleVectors 181472530: each angle x pi/180 -> V_sincosf (CRT sinf 1802e6430 / cosf 1802e0c30, FMA3 build);
forward = (cp cy, cp sy, -sp); right = (sr sp cy - cr sy, ...) as decompiled, up likewise.

## AirMove 180ae34a0(svc, mv)

1. CheckVelocity (180ae34f8). fwd, right from mv+0x14; svc+0x714 and no ground and vz <= 0: low = `vz > -(t x g x
   0.5)`, t = 180308890(); svc+0x714 = 0.
2. fwd.z = right.z = 0; each normalized: `(y² + 0) + x²` -> sqrt; < 1e-17 or > 1e17: 1814738b0 (zero: 0), else x 1/len
   (z = 1/len x 0).
3. wish x = `fwd.x f + right.x s`, y = `right.y s + fwd.y f` (orders differ per lane), z 0; wishdir = normalize;
   wishspeed = len capped at maxspeed (TODO the `(false || fVar12 != 0)` gate: len 0 -> wishspeed 0).
4. AirAccelerate(svc, mv, wishdir, wishspeed, sv_airaccelerate).
5. AddGravity 180ab72d0.
6. h = `frametime x a x 0.5`; v -= h; mv+0x114 += h. v += base velocity (1803d7740).
7. Modern jump: 180adef70 (180ae3987): mv+0x12c = origin.z, mv+0x134 = a.z, mv+0x130 = `vz - (a.z x frametime) x 0.5`.
8. low and 2D speed > 0: vz aside, vz = 0; `speed x frametime < 0.09375` -> v = `wishdir x (0.09375 / frametime)`;
   TryPlayerMove(0, 0, 0); v xy = 0, vz back; TryPlayerMove; then v, a, half restored.
   Else TryPlayerMove(0, 0, &blocked): not blocked and svc+0x718 < 1: svc+0x718 += 180ac70e0(mv); blocked: 0.
9. 180adeec0.

## WalkMove 180aea7d0(svc, mv)

1. svc+0x439 = 1; trace reset; fwd, right; the ground handle (or -1).
2. fwd.z, right.z zeroed (fwd via 180148890, right with the 1e-17 rule) when nonzero.
3. wish = `(fwd.x f + right.x s, fwd.y f + right.y s)` -> mv+0x100 / 0x104; wishdir, len as AirMove; len > 0:
   pawn+0x1564 = 0.
4. The speed latch: clear -> look; set and svc+0x694 == mv+0xdc -> clear, look, again = 1; else nothing. Look: q =
   180ae0230(`sqrt(vx² + vy²)`) (x², y² then addss); changed = svc+0x7a8 != mv+0x100 || svc+0x7ac != mv+0x104; `(again
   && svc+0x698 != q) || changed` -> svc+0x690 = 1, svc+0x694 = mv+0xdc, svc+0x698 = q, mv+0x13a = 1.
5. 180ae10d0(mv, 2, 0); svc+0x25c = 0; Friction; CheckVelocity (180aeac90); wishspeed = min(len, maxspeed);
   180ae10d0(mv, 2, 0); Accelerate(sv_accelerate) (call at 180aeacdf).
6. vz = a.z = half.z = 0. `|v|² (x² + y², + z²) > maxspeed²` (comiss at 180aead42, jbe at 180aead45): `v x= maxspeed /
   |v|`, frametime > 0: `a += (v' - v) / frametime`.
7. Half step (180aeadfa): h = `frametime x a x 0.5`; v -= h; half += h. v += base velocity.
8. t = `180308890() - 180ac7100(mv) x 0.5`; `|v + t a| < 1` -> v = a = half = 0; v -= base; v += half; return.
9. dest = origin + v x frametime (x, y; z the origin's). Filter (vtable 0x181923f18, group 0xb, interacts-as 0x40000,
   flags |= 2, the pawn's ids), hull (svc+0x408 / 180b5d1b0); TraceShape 180addc00. (DAT_182175490: debug overlay.)
10. mv+0xe8 += wishdir x min(len, maxspeed).
11. Fraction 1: origin = trace end; -> 13. Else on a ground, or in water, with no water-jump timer: TryPlayerMove(&dest,
    tr, 0); StepMove(&oldOrigin, &oldVelocity); returns 0 and `0 < |oldVelocity| < sv_step_move_vel_min` and a move
    pressed: oldVelocity x= cvar / |oldVelocity|, StepMove again; -> 13. Otherwise 180adeec0, return.
13. v -= base; v += half; StayOnGround 180ae4660.

### The movement unlocker (CS2Fixes "ServerMovementUnlock")

Not CS2's: `cs2f_movement_unlocker_enable` 1 (g_CommonPatches[0], "clients will not predict"; cfg ships 0). Signature
`0F 86 AF ? ? ? 0F 57 C0 0F 2E C2`, patch `E9 B0 00 00 00 90`; one match, 180aead45:

```
180aeacfa  xmm7 / xmm10 / xmm11 = mv+0x38 / 0x3c / 0x40;  xmm6 = mv+0x120
180aead42  comiss |v|² (x² + y², + z²), max²
180aead45  jbe 180aeadfa   ; 0f 86 af 00 00 00 -> e9 b0 00 00 00 90 (jmp; nop)
180aead4b  v x= max / sqrt(|v|²); frametime > 0: change / frametime into mv+0x108..0x110
180aeadfa  the half step
```

It always skips step 6. Friction, Accelerate, PreventBunnyJumping's 286 and the stamina stay: a landing at 309 u/s
builds ~15 stamina, a ground tick cut to 250 x 0.85² ≈ 183 in CS2; unlocked, friction alone takes it to 287.

## Friction 180ac5310(svc, mv)

1. Skipped with a water-jump timer (pawn+0xb30 +0x54 != 0). speed = length2D(v).
2. q = svc+0x690 ? svc+0x698 : quantize(speed) (TODO: check the argument). q >= 0.1:
3. drop = 0; on ground (pawn vfn 0x660): control = max(q, sv_stopspeed); `decel = control x ((sv_friction x surface
   friction svc+0x26c) x pawn friction 1803d8270)` (180ac53ee..5431); `drop = frametime x decel + 0`. speed > 0 and
   frametime > 0: speed < drop -> decel = speed / frametime; a -= normalize3D(v) x decel (`(z² + y²) + x²`, the
   1e-17 / 1e17 rule).
4. mv+0x128 = max(0, drop - speed). mv+0xe8 = v. speed > 0: v x= max(0, speed - drop) / speed (all axes).

## Accelerate 180ab6c70 -> 180ab6d30

1. Gate: pawn+0xd40 == 0 needs no water-jump timer; != 0 needs 180b5d1b0(pawn).
2. cur = dot(v, wishdir); add = wishspeed - cur; add <= 0 -> return. curPos = max(cur, 0).
3. ducking = IN_DUCK || svc+0x416 || FL_DUCKING. walking = IN_SPEED && !ducking. goal = max(250, wishspeed); scale = 1,
   goalW = goal.
4. sv_accelerate_use_weapon_speed and a weapon: wmax = vfn 0xc20; scoped = vfn 0xcb0 (m_zoomLevel) > 0 && vfn 0xc28
   (m_nZoomLevels) > 1 && wmax x 0.52 < 110; r = min(1, wmax / 250); `(!ducking && !walking) || scoped` -> scale = r;
   goalW = r x goal.
5. Water level >= 2: goalW x= sv_water_slow_amount; ducking -> DUCK; !walking -> s = `goal x slow x scale`, FINAL;
   walking -> WALK. Water < 2: ducking -> DUCK; else WALK / plain.
6. DUCK: goalW x= 0.34; scale = min(0.34, scale).
7. s = goal x scale. Walking: s x= 0.52 unless m_hCarriedHostage (pawn+0xe38 +0x48) is live or scoped; lim = `goalW x
   0.52 - 5`; lim < curPos: `accel' = clamp(1 - max(0, curPos - lim) / max(0, goalW x 0.52 - lim), 0, 1) x accel`
   (below 0: accel x 0).
8. FINAL: frametime > 0: `rate = s x accel' x surface friction - mv+0x128 / frametime`; rate > 0: amount = rate x
   frametime; add < amount -> rate = add / frametime, amount = add; a += wishdir x rate. v += wishdir x amount.

## AirAccelerate 180ab7420

Dead or a water-jump timer: nothing. cap = min(wishspeed, sv_air_max_wishspeed); add = cap - dot(v, wishdir); <= 0 ->
nothing. amount = add; frametime > 0: `full = wishspeed x accel x surface friction x frametime`; half = full x 0.5;
half <= add: amount = half, mv+0x114 += wishdir x (full <= add ? half : add - half); else amount = add. mv+0xe8 +=
wishdir x amount; v += wishdir x amount.

## AddGravity 180ab72d0

No water-jump timer; g = sv_gravity x pawn+0x40c; vz -= g x frametime; a.z -= g; vz += bz x frametime, a.z += bz;
base z = 0 (SetBaseVelocity). CheckVelocity at its end (180ab7403).

## CheckVelocity 180abdab0

A velocity or origin lane with an all-ones exponent (inf, NaN) is zeroed (warned, throttled per entity through
svc+0x440 and Plat_FloatTime); then each velocity lane: v > max -> max, else -max > v -> -max (sv_maxvelocity). Callers:
AirMove 180ae34f8, WalkMove 180aeac90, PostMove 180adcbe3, AddGravity 180ab7403, 180ac5720, 180adc860.

## TryPlayerMove 180ae6e40(svc, mv, firstDest*, firstTrace*, blocked*)

1. blocked = 0; v_orig = v; airborne = !FL_ONGROUND; snap = sv_jump_precision_enable; t = frametime; done = 0; k =
   max(1, |v|) (`(y² + z²) + x²`). Filter and hull.
2. A ground (vfn 0x668) and 180ac8970(pawn) (0x180ae7147..0x180ae71cb): v = a = half = 0 (the loop ends at once).
3. v1 = v. Loop, at most 4:
   - |v| == 0 -> END.
   - dest = origin + v t; unless snap && airborne && t != 0. With it: x, y = `v t + 0 + origin`; z through svc+0x6b4:
     `zz = vz t + acc`; `r = (vz t + 196608) - 196608`; `dest.z = ((zz - r) + r + 196608 + origin.z) - 196608`; `acc = zz
     - (dest.z - origin.z)`.
   - planes == 1: dest += n[0] x 0.03125.
   - firstDest equal to dest -> firstTrace; else TraceShape.
   - f = fraction; `done == 0 and f < 1 and 0.03125 <= |v| t and f |v| t < 0.03125` -> f = 0.
   - `f x k > 0.03125`: origin = trace end; v1 = v; planes = 0.
   - done += f; f == 1 -> END.
   - AddTouch 180c4d5f0(mv, trace, v). t -= fraction x t (unmodified fraction).
   - planes > 4, or (airborne, vz < 0, normal z >= sv_standable_normal, IsStandable, length2D(v) < 1): zero, END.
   - n[planes++] = normal.
   - planes == 1, WALK (180ae7654), no ground: n.z <= sv_walkable_normal -> blocked = 1, `d = -dot(n, v1) x ((1 - surface
     friction) x sv_bounce + 1)`; else `d = -dot(n, v1)`; `d = max(d, 0) + 0.03125`; v1 += n x d; v = v1 (dot here: `n.z
     v.z + n.y v.y + v.x n.x`). Next. (Not WALK, e.g. a ladder or noclip: the multi-plane clip below, with its
     `dot(v, v_orig) <= 0` stop.)
   - More planes: for i: `v = v1 + n[i] x (max(0, -dot(n[i], v1)) + 0.03125)`; ok when dot(v, n[j]) >= 0 for every j !=
     i. None ok: two planes -> dir = normalize(n0 x n1) (`x = n1.z n0.y - n1.y n0.z`, `y = n1.x n0.z - n0.x n1.z`, `z = n0.x
     n1.y - n1.x n0.y`); `d = (vz dz + vy dy) + vx dx`; `v = (n1.x x 0 + n0.x x 0) + dx d` (same for y, z); then the test
     below. More than two -> zero, END.
   - dot(v, v_orig) > 0 -> next; else zero, END.
4. END: done == 0 with planes -> zero. lost = length2D(v_orig) - length2D(v): > 1160 -> 180ade0a0(svc, mv, 1.0); > 580
   -> 0.85.

## StepMove 180ae49a0 -> bool

1. Keep origin o1 and velocity; origin = oldOrigin, v = oldVelocity. step = sv_stepsize.
2. Trace up to origin + (0, 0, step + 0.03125); fraction > 0 -> origin = its end. TryPlayerMove(0, 0, 0).
3. Trace down to origin - (0, 0, step + 0.0625). Hit (f < 1 or start solid): ok; normal z < sv_walkable_normal: ok
   only if |oldVelocity| < 64 and a box shrunk by 2 on x / y traced to down - step x 0.5 hits standable, then a trace
   from origin along 1803e5180(v) and, from its end when f > 0, one down by step + 0.0625 that hits (1802c35a0)
   standable. No hit: not ok.
4. hit, ok, f > 0: origin = the down end, unless it went less far along oldVelocity's xy than o1 -> o1 and its velocity;
   returns 1. Else origin = o1, v = the entry velocity, returns 0. vz restored to the entry's either way.

## IsStandable 180ad2d00(svc, trace)

trace+8 null or start solid -> false. Not a player (vfn 0x558): normal z >= sv_standable_normal (182175518 via 180187770).
A pawn: its vfn 0x668 == svc's pawn -> false; 180ad2840(svc pawn, hit (vfn 0x560 -> 180b55040, else vfn 0x558)) ->
true; mp_solid_teammates 0 -> false; else 180ae7c60(hit, 180ac6af0(svc), trace end z). No normal test for a player.

## SetGroundEntity 180ae1cf0(svc, mv, trace*)

new = trace ? trace+8 : null. On a change: leaving -> base velocity + old ground's velocity (z = its z); landing -> -
the new's; 1803ea860(pawn, base velocity); 180e95a10(pawn, new) (handle `((h >> 15) - (identity+0x30 & 1)) << 15 |
index`, FL_ONGROUND on / off). Landing: 180c7e7d0 (keeps svc+0x278 / 0x270); surface friction = `min(1,
surface(*trace)+0x28 x 1.25)`; +0x54 = 0; AddTouch when fraction >= 1 and not start solid, or the hit isn't the world
(trace+0x68 != 0x8000); 180c60e40(mv, trace+0x90); not 7 / 8: vz = a.z = half.z = 0.

## StayOnGround 180ae4660

up = origin + (0, 0, 2), down = origin - (0, 0, stepsize). Trace origin -> up, then (origin.x, origin.y, that end z) ->
down. 0 < f < 1, not start solid, normal z >= sv_walkable_normal (182175508), `|origin.z - end.z| > 1/64` -> origin = end.

## PostMove 180adcb90(svc, mv, slide)

CategorizePosition(svc, mv, onGround); CheckVelocity (180adcbe3); on ground: vz = a.z = half.z = 0. CheckFalling. slide
&& |v| not small (1802d4490, 0.01): TryPlayerMove(0, 0, 0). mv+0x138 and on ground: `svc+0x6a4 = max(svc+0x6a4,
((origin.z + 196608) - 196608) - svc+0x6a0)`. On ground: pawn+0x14e0 < 1 -> clamp(+ frametime x 0.4, 0, 1).
pawn+0xdf1 = 1 when moving. svc+0xdcc = 0.

## Players' bodies

Pawn bodies: SOLID_BBOX, mins (-16, -16, 0), maxs (16, 16, 72 / 54 ducked). Filter +0x20: first entity id to ignore
(RnQueryShapeAttr_t at filter+8, +0x18 of the query); +0x38: collision group (11).

- ShouldHitEntity 0x180ae3280: no entity, +0x20 == -1 or no entity system -> false; the filter's own entity (entity list
  181f47078, 0x70-byte slots, serial +0x10) gone -> false. Group 11 only: the hit's m_CollisionGroup == 16 -> false;
  the pass entity's interacts-with & 0x180000000 nonzero and equal to the hit's -> 180ae7da0(hit, pass). Else true.
- 180ae7da0(hit, mover): mp_solid_teammates != 2 -> false; else 180ae7c60(hit, mover, GetAbsOrigin(mover).z).
- 180ae7c60(h, m, z): h == m -> 0; LADDER on either -> 0; either collision null -> 0; vfn 0x660(h) == m or vfn 0x660(m)
  == h (taken as GetGroundEntity: TODO, IsStandable uses 0x668) -> 1; `(z + OBBMins(m).z) > (h.z + OBBMaxs(h).z)` -> 1
  (0x180ae7d22..d43: movaps xmm6, z; addss mins; xmm0 = h.z + maxs; comiss / ja); `(h.z + OBBMins(h).z) > (z +
  OBBMaxs(m).z)` -> 1 (0x180ae7d50..d64); else 0.
- 180ad2840(me, other): null -> false; 180fe1050(info, other) (+0 null?, +1 vfn 0x558, +2 vfn 0x570, +4 handle, +8
  180b55410(other): the controller's entity index - 1, +0xc 180ac5e00(other) (taken as the team: TODO), +0x10
  m_iTeamNum +0x344); 180b55410(me) == info+8 (the same player) -> false; the bool at 18211a6d8 set -> true (taken as
  mp_teammates_are_enemies: TODO its name); me+0xc98 live -> 180a79ab0(controller) != info+0xc; else me+0x344 != info+0xc.
- 180ac8970(pawn) (callers 0x180abc7c5, 0x180ae6882, 0x180ae7179): over the player list (181e22ee8, 180c86b40,
  180c84440: state 0 or 3, neither vfn 0x810 nor 0x818), the first live pawn whose ground (vfn 0x668) is this pawn.
  WalkMove's clear move never reaches TryPlayerMove's check, so the one under a head can walk out; the jump is refused.
- Legacy CheckJumpButton 0x180abc70c..0x180abc778: r12 = ground is a pawn (vfn 0x558) and not vfn 0x570; r15 = that and
  its ground null. r15 -> mv+0x40 = 0, +0x110 = +0x11c = 0 (0x180abca35); else `!+0x438 && !+0x416 && !(m_fFlags & 2) &&
  !r12` -> impulse less the gravity half step, x the jump factor; else impulse x factor.
- Modern 0x180ae6830..0x180ae68b4: ground a pawn whose ground is null, or 180ac8970 -> 180ada0a0, +0x18 = -1024, return.
  r13 (on a pawn) used later: unread.
- 180c70950(svc, button, down): when the pawn is the one at 1821974e0 (a listen host's?) it updates svc+0x50's state
  (18068b200) and svc+0x190; down -> svc+0x78 |= b, +0x70 |= b; up -> +0x78 |= b, +0x70 &= ~b; both: +0x198 &= ~b; then
  in_spewbuttondelta's print. TODO: what the next command makes of +0x70 / +0x78 / +0x198.

Unread: the pawn body's broadphase walk order (a pawn and a map shape at the same fraction), its shape (cooked planes /
vertex order), body type (keyframed taken), m_nInteractsAs (0x40000: 180ae27b0's player layer with solid cleared,
grenades.md "Players and the projectile's filter"; earlier bits unread), its collision group at spawn (8 taken), surface
("default"), shape flags.

## Duck 180ac1ec0(svc, mv)

1. 0x424: `s = frametime x 6.4 x -8`; 0x414 ? `max(s + v, -8)` : `min(v - s, 0)`.
2. inAir = no ground and not LADDER (180ac1fcc). forced = pawn vfn 0xc20 && bot_crouch. spamOk = duck speed >= 1.5 and
   (FL_DUCKING or `sv_timebetweenducks + lastDuckTime <= curtime`). want = `(0x438 && inAir) || 0x414 || forced ||
   (IN_DUCK && spamOk)`.
3. Dead (180cf7020 < 1) and not observer-ish: 0x414 = 0; FL_DUCKING -> FinishUnDuck; return.
4. 0x438 clear:
   - speed = Approach(8, speed, frametime x 3) (180460960: value + step if target - value > step, value - step if below
     -step, else target). speed < 8 and amount not in (0, 1): 2D distance² from 0x430 to the pawn's origin
     (1803d6f50, not mv's: 180ac257b) > 4096 -> speed = Approach(8, speed, frametime x 6); speed >= 8: 0x430 = origin.
   - want: amount < 1 -> ducking = 1; ducking: amount = Approach(1, amount, `speed x 0.8 x (pawn+0x14be ? 0.4 : 1) x
     frametime`); `(1 <= amount) || ground == null` (r12, 180ac296d) -> FinishDuck.
   - !want: amount > 0 -> ducking = 1; ducking: CanUnduck false -> amount = 1, ducked = 1, ducking = 0, FL_DUCKING on;
     true -> amount = Approach(0, amount, `max(1.5, speed) x (0x14be ? 0.4 : 1) x frametime`); ducked = 0; amount <= 0
     or no ground -> FinishUnDuck; amount <= 0.75 and FL_DUCKING -> off.
   - Slowdown once per tick (0x650): IN_DUCK or ducking or FL_DUCKING: `k = (amount x 0.34 + 1) - amount`; forward,
     up, side, maxspeed x= k; 0x650 = 1.
5. 0x438 set: not FL_DUCKING -> 0x438 = 0, return. inAir: vz > 0 -> return; trace the standing hull from `origin -
   ((max - min) - (dmax - dmin))` per axis down by stepsize (vtable 0x181924e18, group 0xb, interacts 180ade310, team
   bits 0x180000000 for a player); start solid or f == 1 -> return. Then 0x438 = 0; CanUnduck -> FinishUnDuck.

- FinishDuck 180ac47e0: in air (no ground, not LADDER (180ac4832), water level < 3): off = `((max - min) - (dmax - dmin))
  x 0.5` per axis; else off = -(dmin - min) (sign by XOR). ducking = 0, ducked = 1, lastDuckTime = curtime,
  FL_DUCKING on; origin += off; 0x418 -= off.z; 180ac51a0(svc, mv, 1); CategorizePosition(svc, mv, 0); amount = 1.
- FinishUnDuck 180ac4ef0: in air (not LADDER, 180ac4f58): off = `((max - min) - (dmax - dmin)) x -0.5 - 0`; else off =
  dmin - min. origin += off; 0x418 -= off.z; FL_DUCKING off; ducked = ducking = 0; CategorizePosition; amount = 0.
- CanUnduck 180abab50: 0x414 -> false. 7 / 8 -> true, no trace (180abab96). end = origin; in air: end -= `((max - min) -
  (dmax - dmin)) x 0.5`; on ground: end += (dmin - min). TraceShape with the standing hull, vtable 0x181924e30 (group
  0xb, interacts-as 0x40000, flags |= 2), origin -> end: start solid or f != 1 -> false. Else true.

## The legacy jump 180abbcb0 (sv_legacy_jump 1)

1. Neither held (bit 1) nor 180c80ad0(svc, 2) -> return. Block cleared when `(block && sv_jump_spam_penalty_time + last
   < curtime)` or sv_autobunnyhopping.
2. CheckJumpButton 180abc3f0; block = 1; pressed -> last = curtime - frametime.

### CheckJumpButton 180abc3f0

1. Dead -> return. pawn+0xc98's controller with 180a6ffb0 < 0 -> return; pawn+0x15a8 / +0x15a4 cooldown -> return.
2. Not autobhop and not pressed -> return. Water-jump timer +0x54 != 0: counts down by frametime (floor 0), return.
3. Water level > 2: ground off; type 0x8000 -> vz = 100, 0x10000 -> vz = 80 (neither: unchanged); a.z = half.z = 0;
   swim timer (pawn+0xb30 +100) <= 0 -> 1000 and "Player.Swim" unless walking (pawn+0x1478) or ducked (svc+0x408)
   (180abc6a8); return.
4. onPlayer / grounded2 (above). svc+0x439 = 0. No ground -> return. 180ac8970 -> return. block -> return.
5. 180ad63f0; ground off. Jump stamp svc+0x68c (180abc7fe..8aa) = `(curtime (180927cb0) - frametime (1801f95a0)) + 0.1`
   (18017dc70) -> pawn+0x1560; pawn+0x1564 = 0.
6. svc+0x6a0 = `(origin.z + 196608) - 196608`; 0x6a8 = 0x6a4; 0x6a4 = 0; 0x6ac = stamina; 0x6b4 = origin.z - 0x6a0.
7. `sqrt((z² + y²) + x²) > 140` (0x1817bc124; 180abc921) -> svc vfn 0x1d0(svc, origin, svc+0x428, 1.0, 1, 0).
8. svc+0x368 = 1. k = svc+0x278 ? its +4 (jumpfactor) : 1.
9. Not IN_DUCK and CanUnduck (and pawn vfn 0xc20): svc+0x438 = 1, FinishDuck.
10. vz0 = vz. grounded2: vz = 0. Else not 0x438, 0x416, FL_DUCKING, onPlayer: `vz = (impulse - sv_gravity x pawn+0x40c
    x 0.5 x 0.0078125) x k`; else `vz = impulse x k`, and ducked == 0 with IN_DUCK -> flag = 1. a.z = half.z = 0.
11. 180adbeb0(pawn, origin, svc+0x428, flag). s = 180ab8d30(jump); vz x= s; svc+0x6b0 = s. mv+0xf0 += vz - vz0. Stamina
    = `clamp(stamina + sv_staminajumpcost x mv+0xf0', 0, sv_staminamax)`. 180ada490. Event player_jump.

## The modern jump (sv_legacy_jump 0)

Every sv_legacy_jump (1821755b0) reader: CheckFalling 180abbb56, CheckParameters 180abd251, the ladder dispatch
180adc629, FullWalkMove 180adcaad, the water move 180add47d (these three choose the object), vfn 0x120 180ae2f79, AirMove
180ae3970, the view offset 180ae9532.

W = `1813b9ab0(from_seconds(window x 0.5), (frac + 131072) - 131072)`: a quarter tick at the default. One tick =
180c51bc0(0.015625) rounded the same way = (1, 0). Now = 1813b8ef0(1809209f0(mv+0xd4), mv+0xdc) (the piece's start).

### The tick 180abbe60(jump, mv)

1. pressed = 180c80ad0(svc, 2). Pressed: now_r = 1813b9ab0(now, `(now.frac + 131072) - 131072`); last press (+0x10 /
   0x14) = now_r; d = seconds(now_r - the old last press); `sv_jump_spam_penalty_time >= d` (comiss / jb) -> pressed =
   0. Else: u = usable (+0x18); `u < landed - W` (-1) or `u >= landed + W` (0 / 1; unordered skips) -> usable = now_r.
2. (sv_autobunnyhopping and IN_JUMP held) or pressed -> CheckJumpButton 180ae66b0.
3. Else: compare(u, landed - W) negative (-1 / -128) -> clear usable. Else u < landed + W -> CheckJumpButton; else u <
   landed + one tick -> CheckJumpButton; else clear.

### CheckJumpButton 180ae66b0 (no water branch, no timer, no pressed gate)

1. LIFE_DEAD -> clear usable, return. Controller (pawn+0xc98 via 181f47078) with 180a6ffb0 < 0 -> clear, return.
   pawn+0x15a8 set and 1801f95b0(pawn+0x15a4, curtime (180927cb0(identity+0x38))) > 1.0 -> clear, return.
2. Ground null -> return (usable kept). A player (vfn 0x558) whose ground is null -> clear, return; 180ac8970 -> clear,
   return.
3. c = compare(landed - W, u) (`neg cl; js`): c -1 or 0 and 180ab6ad0(u, landed + W) == -1 -> bhop; else
   sv_autobunnyhopping and compare(now, landed + (1, 0)) <= 0 (`neg; js`) -> bhop. A bhop with autobhop, or with
   `mv+0x120² < landed vx² + vy²` (x² then + y²; comiss / jb: unordered too) -> t = landed (180ac65f0), mv+0x38 / 0x3c =
   the landed velocity x / y, jump. Else: now < landed + one tick (180ac5ec0, -1) -> return (usable kept); else jump.
   No jump within a tick of the landing unless it keeps the landing's speed.
4. The jump 180ae6ac0: clear usable; 180ad63f0; ground off; svc+0x439 = 0; stamp svc+0x68c = `(curtime - frametime) +
   0.1`, pawn+0x1560 = it, pawn+0x1564 = 0; svc+0x6a0 = `(origin.z + 196608) - 196608` (0x181926a54), 0x6a8 = 0x6a4,
   0x6a4 = 0, 0x6ac = stamina, 0x6b4 = origin.z - 0x6a0; `(vx² + vy²) + vz² > 19600` (180ae6c2a) -> vfn 0x1d0(origin,
   svc+0x428, 1.0, 1, 0); svc+0x368 = 1; a bot (controller +0x388 bit 8) not holding IN_DUCK and CanUnduck -> svc+0x438
   = 1, FinishDuck; k = jumpfactor or 1; vz0 = vz; 0x438 or 0x416 or FL_DUCKING or onPlayer -> 180ae10d0(mv, 2, `k x
   sv_jump_impulse`) and the flag when not ducked with IN_DUCK; else 180ae10d0(mv, 2, `(sv_jump_impulse - ((pawn+0x40c x
   sv_gravity) x 0.5) x 0.0078125) x k`).
5. s = 180ab8da0(jump, t); `vz = s x vz`; svc+0x6b0 = s; `mv+0xf0 = (vz - vz0) + mv+0xf0`; 180adbeb0; 180ada490. No
   stamina cost.

### The jump's scale 180ab8da0(jump, t)

`f = clamp(+0x30 x 0.0005 + 1.0, 0.2, 1.0)`; d = `(t - landed) + (1, 0)` (1813b8fb0, 1813b9090); `k = minss(f +
seconds(d) x 0.6, 1.0)`; stamina s: `0 > s` skips (comiss / ja), s <= 0 or unordered skips (comiss / jbe); else k x=
`clamp(1.0 - s / 100, 0, 1)`.

### The landing's record 180ada630(jump, mv, fall)

From CheckFalling 180abbc0f (fall = xmm7 from 180abbb5d). dz = origin.z - mv+0x12c, frac = mv+0xe0, vz = -fall. `0 >
dz` and `0 > v0` (mv+0x130) and `0 > a` (mv+0x134): `disc = (a + a) x dz + v0 x v0`; disc >= 0 (comiss / jb): s =
sqrtss(disc), `tt = (-v0 - s) / a`; 0 > tt -> 0, else minss(frametime, tt); `vz = tt x a + v0`; `frac = tt /
180308890() + mv+0xdc`. Then landed = 1813b9ab0(1809209f0(mv+0xd4), `(frac + 131072) - 131072`); vx, vy, vz through
CSMovementVelocityQuantizer_t (1803c1de0 on 182176538) into +0x28 / 0x2c / 0x30.

### The step builder's jump cuts 180ae2a50

T = 1809209f0(mv+0xd4); x = the landing slowdown with now = (T, 0); `1.0 > x` (comiss / jbe) -> cut at landed.frac
(+0x24); landed + W tick == T -> cut at its fraction; landed + one tick tick == T -> cut at its fraction.

## The jump's record 180ada490 and PreventBunnyJumping 180ad63f0

- 180ada490: svc+0x708 / 0x70c = 1813b9ab0(mv+0xd4, `(mv+0xdc + 131072) - 131072`), svc+0x710 = mv+0x40, svc+0x714 = 1.
- 180ad63f0: sv_enablebunnyhopping off -> cap = svc+0x1ac x 1.1 (0x18179be60); `0 < cap` and |v| (180225130, 3D) > cap
  -> v x= cap / |v| (x, y, z). (The cap is m_flMaxspeed's, not mv+0x120's.)

## CheckFalling 180abb840 (from PostMove)

1. Alive, on a ground, fall (svc+0x25c) > 0.
2. In water and fall >= DAT_181926a28 -> "Land_WaterVol.StepLeft".
3. fall >= 350 (DAT_1817c3d60), out of water: a floating ground (1803dfd50) -> fall -= 200 (DAT_18179bea4); a ground
   moving down (180ac6af0 -> vfn 0x668 -> 1803d6fb0): fall += its vz, then max(0.1, fall) (1801783b0(&0.1, &fall)).
4. Impact punch 180ade0a0(svc, mv, scale): > 580 -> 180adc190(mv) first, 1.0; > 290 -> 0.85; > 200 -> 0.5; else 0; in
   water always 0.5.
5. View punch (180abbae2) when `250 < fall <= 1024` (water or not, after the impact): pitch = max(fall x 0.001, 0.75)
   over the decayed punch, set at now (180c7e550).
6. Landing stamina: modern -> 180ada630; legacy -> `clamp(stamina + sv_staminalandcost x fall, 0, max)`. svc+0x714 = 0.
   180adaaa0(pawn, fall) (the adjusted fall). fall = 0.

IsFloating 1803dfd50: m_iEFlags bit 19 (Source's EFL_TOUCHING_FLUID), then the body's physics material +0x30 (density)
below 1000. Nothing in server.dll sets bit 19 on an entity (no `or` / `bts` of 0x80000 / 19 stored to [r + 0x414] within
8 instructions, no `or [r + 0x414], imm`, no atomic or byte write to +0x414..0x416, no AddEFlags helper; the only
`or [rdi + 0x414], esi` (180ca6480, masks 0xfffff) is a network-state block's): the 200 never comes off.

## CheckStuck

1. 180abd670 (prelude 180add182): i = 180c8cbc0 (the entity index: the identity's place in the list's 0x70-byte chunks,
   512 a chunk, 0x4000 + ... for the second list); `(svc+0x188 + i) & 63 != 0` -> 0. Then jmp CheckStuck.
2. 180abd6c0: CreateStuckTable 180ac0e60 once (54 x 12-byte table at 0x181e17630, init flag 0x181e17f70): (0, 0, z) z =
   -0.125..0.125 step 0.125, (0, y, 0), (x, 0, 0), the 8 corners at +-0.125 (x outer, y, z inner), (0, 0, 0 / 1 / 6),
   (0, y, 0) y = -2..2 step 2, (x, 0, 0), then z in 0 / 1 / 6 over x, y = -2..2 step 2; the 54th zero.
3. slot = 180c86c00; -1 -> 0. TestPlayerPosition(svc, &h, mv, mv+0xc8, 0xb, &trace) with svc+0x43a = 1 around it.
4. h == -1, -2, an empty chunk or a serial mismatch ([entry + 0x10] != h) -> m_StuckLast = 0, return 0. developer ->
   the "stuck on object" print.
5. now = (float)Plat_FloatTime() (import slot 0x18176b250, cvtsd2ss). `svc+0x448 + slot x 4 >= now - 0.05` (subss;
   comiss / jb: NaN goes on) -> return 1. Else it = now; 180c4d5f0(mv, &trace, mv+0x38) (skipping the pawn; mv+0xb0 +=
   trace+0x90).
6. Up to 27 (0x1b) tries: i = m_StuckLast++, d = table[i % 54] (signed: imul 0x4bda12f7 / sar 4), at = `(o.x + d.x, o.y
   + d.y, d.z + o.z)` (o = origin at the first test); TestPlayerPosition(at) == -1 -> m_StuckLast = 0, mv+0xc8 = at,
   return 0. All 27 hit -> return 1 (m_StuckLast kept).

TestPlayerPosition 180ae5650: svc+0x648 counted on entry and at its trace (180ae5818); hull by svc+0x408 (180cb7b90
+0x24 / +0xc / +0x48 when 180b5d1b0); trace 180addc00 at -> at; a hit whose layers (+0x28) meet pawn+0x608 (| 0x20
when vfn 0xc20) gives its handle `((h >> 15) - (identity+0x30 & 1)) << 15 | index`, else -1.

Trace count svc+0x648 `inc` sites: 180abb4ce / 5e4 (CategorizePosition, both traces), 180abea98 / eba6 / ebdb
(CheckWaterJump), 180ad55b8 / 57c8 / 598c / 5c07 (LadderMove), 180ae01af, 180ae48a4 / 48cd (StayOnGround), 180ae4c2d /
4ccf / 4e20 / 4f35 / 5009 (StepMove), 180ae5671 / 5818 (TestPlayerPosition), 180ae5d19, 180ae5eb8 / 5f9b / 603a / 6104
(the quadrants), 180ae746d (TryPlayerMove), 180aeb33c (WalkMove), 180aec121 / c171 (WaterMove). CanUnduck and the
duck's air check call TraceShape directly: not counted.

## Water

- CheckWater 180abe290: ray from origin + (0, 0, hull max z) to origin; CTraceFilter (0x18178c240) interacts-with
  0x18000, group 5, query flags 0x4d. Hit (1802c35a0): m_flWaterLevel = clamp(1 - fraction, 0, 1), type from contents;
  miss: 0. Entering (svc+0x654 0 and a level now): svc+0x658 = curtime. Returns level > 1. Called at CategorizePosition's
  start (with a controller, pawn+0xc98), the ladder tick after the duck, the water jump's flight after its slide,
  FullTossMove.
- m_flWaterLevel setter 1803ebff0: CQuantizedFloatEncoder "m_flWaterLevel" (1803c1030(enc 0x181fb2138, 8 bits, flags 8
  = integers exact, 0, 1), made once under 0x181fb2156 bit 2): a 1/128 grid over [0, 1.9921875]; then pawn vfn 0x698
  (180b67370 -> water services vfn 0xb8). Level = int(v x 4 + 1) unclamped: 4 above 0.75, 5 at 1. Readers: >= 2
  (Accelerate), > 2 (switch, CheckJumpButton), < 3 (FinishDuck), != 0, CheckWaterJump == 3 (180add42a: levels 4 and
  5 don't water-jump).
- CFuncWater::Spawn (vfn 9, 180999c60): 180d0f2c0(collision, 3, 2, interacts-with) (SetCollisionGroup 180d0e200 to 2,
  trigger), shape attributes wiped (vfn 0x60 with a zeroed record), 180d0e5f0: interacts-as 0x8004 (water | trigger),
  interacts-with 0x340001, exclude the entity's. Trigger (2) touches only player_movement (11): the movement passes
  through, CheckWater (its query flags with 4) hits.
- Water move 180aeb880: `water friction = surface friction x ((speed x frametime) x sv_friction)`, `acceleration =
  (frametime x (wishspeed x sv_accelerate)) x surface friction`; mv+0x124 (180aeb9b1 / 180aeb9fd).
- CheckWaterJump 180abe530: forward svc+0x65c; the wall's m_iEFlags bit 5 tested before the jump speed is stored (never
  set in CS2: no or / bts of 0x20 on [r + 0x414], no or'ed store within 4 instructions; 180ca6480 works on a
  network-state block (+0x1c0, +0xf8 mutex; callers 180b55b70 pass 0xfffff, 180ca6840 a mask)); water services +0x58 /
  0x5c / 0x60 = normal x -50; FL_WATERJUMP 1803c5940(pawn, 4); second probe at origin.z + m_vecViewOffset (180158e30) + 8.

## The view offset 180ae9260(svc, frametime)

"Alive" = pawn vfn 0x550 (CCSPlayerPawn 0x1801541a0: m_lifeState == 0).

1. svc+0x418 (FinishDuck / FinishUnDuck's origin shift): dead -> 0 (notify 180ad7f70); else Approach(0, it, `((((max.z
   - min.z) - (dmax.z - dmin.z)) x 0.5) / 0.1) x frametime`) (max.z hull +0x20, min.z +0x14, dmax.z +0x38, dmin.z +0x2c;
   0.1 = 0x3dcccccd). off = `0 + svc+0x418`.
2. svc+0x3f0 = 180a73870(svc+0x290) (notify 180ad7930); set -> off -= 180a7a830(svc+0x290). Changed -> svc+0x3f4 =
   (body +0x120 z +0xf0) - off (notify 180ad9310).
3. svc+0x3f4: dead -> 0; else Approach(0, it, rate x frametime): !0x3f0 -> 1801783b0(`|vz x 0.5|` (1808ad470; vz from
   1803d6fb0 GetAbsVelocity: pawn+0x38c unless EFL_DIRTY_ABSVELOCITY), sv_gravity x 0.05); 0x3f0 and sv_legacy_jump off -> max(|svc+0x700|, 60) (180ae953f); else 150. off += 0x3f4; off = clamp(off,
   -32, 32).
4. Body 180cb8770(body+0x120, (0, 0, off), 0): each axis clamped to [-128, 128] into +0xe8 / 0xec / 0xf0 (notifies
   1806e8780 / 88c0 / 8a00), vfn 0x70(0x80) on a change.
5. svc+0x41c: dead -> 0 (notify 180ad81f0); else Approach(`(dz - hz) x m_flDuckAmount - svc+0x418`, it, `((hz - dz) /
   0.2) x frametime`), hz = 72, dz = 54.
6. z = `((((body z + svc+0x41c) + svc+0x424) + view z) + 196608) - 196608`; SetViewOffset 180242350: per axis a changed
   value stored clamped to its encoder's range (GetQuantizedFloatEncoderByReg) and notified. Then 180b21ba0(pawn+0xb10).

m_vecViewOffset encoders (1806892e0, FindOrCreateQuantizedFloatEncoder(reg*, 1, name, bits, flags, lo, hi)): m_vecX /
m_vecY 10 bits, flags 4, [-64, 64]; m_vecZ 12 bits, flags 2 (round up), [0, 64]: `lo += (hi - lo) / 2^bits`, so z is in
[1/64, 64]. Readers: CheckWaterJump (180abe530: the offset rotated by the node quaternion and scaled), the eye 180ac6340,
180ae4570.

### The stair estimator 180a73870(est = svc+0x290) -> bool

est: +0 svc, +8 height cache (key the cell's (uint)floorf(x), (uint)floorf(y), value at +0xc of a 0x10 entry; +0x18
count, +0x1c slots), +0x28..0x30 last floored origin, +0x34 result. The constructor (the svc constructor,
180ab4e33..56) sets +0x28..0x34 to FLT_MAX; 180ab5b80 frees it.

1. No svc or pawn -> false. Ground (pawn vfn 0x660 0x18014ec60 -> vfn 0x668 0x180e7c2a0) null or its vfn 0x570 false
   (CWorld 0x180cb1d50 true; CBaseEntity's and brush / door / physbox / train's 0x1801542c0 false) -> false.
2. pos = abs origin floored to 1/100 (`floorf(v x 100) / 100`). Equal to +0x28..0x30 -> true.
3. Cache over 0x200 -> freed, count 0.
4. s = sv_stepsize with movement services (pawn+0xb50), else 18. Static (182174cc8, made once): (-24, -24, -2 s, 24) and
   (24, s + 1). box = pos + those (static first); footprint pos.xy +- 16.
5. Grid: `x0 = int((((x - V_fmodf(x, 8)) - 16) - 4))` (+8 when x > 0), y0 the same. For i, j in 0..5 (x0 + 8 i, y0 + 8
   j): start = `(fx + 0, fy + 0, (s + s) + z)`, end = `(fx - 0, fy - 0, z - (s + s))`; 180a707a0: the cached height when
   keyed and (start.x, start.y, h) is inside the box; else TraceShape (180c2f3c0) of (-3.99, -3.99, 0)..(3.99, 3.99, 0)
   from floorf(start) to floorf(end), CTraceFilter (0x18178c240) interacts-with 0x2011, group 11, entity / owner ids -1
   (180bf9270(null)), hierarchy 0 (180c048b0(null)), detail layers 0xffff, object set 0xf, flags `(stack byte & 0xc9) |
   0x49` (bit 7 never read), +0x40 = 0; DidHit, not start solid, normal z > sv_standable_normal (182175520, strictly) ->
   h = `floorf(end z x 10) / 10`, cached (180a6af20). A miss: h FLT_MAX, the cell skipped. The probe runs before the
   area test, so a cell outside the footprint is still cached.
   Area 180a7ec80(cmin (fx - 4, fy - 4), cmax (fx + 4, fy + 4), fmin, fmax): 0 unless fmin.x < cmax.x, fmin.y < cmax.y,
   cmin.x < fmax.x, cmin.y < fmax.y; else `(minss(cmax.y, fmax.y) - maxss(cmin.y, fmin.y)) x (minss(cmax.x, fmax.x) -
   maxss(cmin.x, fmin.x))`. Area > 0 -> record (0x1c: area, x, y, h, i x 5 + j, -1, 1.0), min / max of x, y, h (`h <=
   min`, `max <= h`).
6. No record, or `z - max h >= s` (comiss / jae) -> +0x34 = 0. Else max h - min h >= s: the nearest by `((dy² + dx²) +
   dz²)` (strictly nearer replaces: the first of equals) gets distance 0, weight maxss(0.01, area x 1/64); until a pass changes nothing: each
   record with distance >= 0, each direction (-1 when idx % 5 != 0, +1 when (idx + 1) % 5 != 0, -5 when idx > 4, +5 when
   idx < 20): idx + d at -1 with |h - its h| < s gets distance + 1, weight min(this, maxss(0.01, min(areas) x 1/64)),
   linked. Records still -1 removed (from the end, order kept).
7. `w = (RemapValClamped(h, s + z, (s + s) + z, 1, 0) x RemapValClamped(h, z - s, z - (s + s), 1, 0))²` (1801d3440: `(v -
   a) / (b - a)` clamped to [0, 1], `x (d - c) + c`), x the weight when linked, x area; sum w, sum w x h. sum w > 0 ->
   +0x34 = clamp(z - sum wh / sum w, 0, 24); else 0. pos -> +0x28..0x30. True.

## The view punch

- Getter 180a7aab0: out = +0x48; `t = curtime (180c71830) - (float(tick +0x54) + ratio +0x58) x 0.015625`; `x = t x
  view_punch_decay`; x > 0 -> out x= V_expf(-x) (import slot 0x18176ae78).
- Setter 180c7e550: sv_suppress_viewpunch -> nothing. Each lane AngleNormalize'd (z, y, x), stored when any lane
  compares unequal (1801f9480; notes 180c7aac0); time given -> its tick / ratio (each stored when it differs); null ->
  gpGlobals tick (+0x44) through 180c86d00 / 1809209f0 (the pawn identity's m_worldGroupId (+0x38) 0 -> 180de69a0
  takes the paused ticks (global +0xc0) off), ratio 0.
- Writers: every caller of 180c7e550 and of the add (vfn 0xf8 180a9ef60 = decayed + delta, time null): the respawn
  (zero), 180ade0a0 (TryPlayerMove's speed loss, CheckFalling's landing), CheckFalling's view punch, Recoil, the maps'.
- 180ade0a0(svc, mv, scale): scale > 0 -> svc+0x258 = 400, svc vfn 0x1d0(svc, mv+0xc8, svc+0x428, max(scale, 0.1), 1,
  0), then the decayed punch with roll = `-(quantize(svc+0x25c)) x 0.013` (180ade296's encoder: 20 bits, flags 4,
  [-16384, 16384]), pitch 8 when above 8, set at now; scale > 0.85 (0x1817b2bfc) -> pawn vfn 0xbb0(0x12, 0, 0) (an
  animation event).
- Recoil 180a4c5d0: `yaw -= sinf(a) x (magnitude x 0.055)`, `pitch -= cosf(a) x (magnitude x 0.055)` (V_sinf / V_cosf
  0x18176af00 / 0x18176b118), set at the attack time (180a9bda0 -> 180c7e550).
- Maps: env_viewpunch (CEnvViewPunch_API::ViewPunch 180d2a290 -> 180feca00: falloff 1 - d / r), trigger_impact
  (CTriggerImpact vfn 0x888, 180fdbcc0: pitch / roll from the push direction x m_flMagnitude x 0.1), env_physexplosion
  (CPhysExplosion vfn 0x68 -> 180ec6140 -> 180ec0960).
- Nothing in the movement reads mv+0x44: every [r + 0x44..0x4c] read with the CMoveData register in 0x180ab0000..
  0x180af0000 and 0x180c60000..0x180c90000 is CheckParameters' own; WalkMove, AirMove, WaterMove, LadderMove, noclip and
  CheckWaterJump take AngleVectors of mv+0x14 (the prelude's 181472530 into svc+0x65c / 0x668 / 0x674), and the base
  FinishMove's vfn 0x140 (180c70140) copies mv+0x14 into pawn+0xbc8 (v_angle; the old one to +0xbd4). The punch never
  moves a player (Source 1 the same: m_vecAngles = view + punch, the moves read m_vecViewAngles).

## Step sounds

1. 180ae9a50(svc, surface, origin, velocity): pawn vfn 0xc20 (m_fFlags bit 4) with identity +0x30 bit 7 -> nothing;
   vfn 0x550 false -> nothing; movetype 2: `s² = (x² + y²) + z²` against `(0.52 x 260)²`: below, or m_bIsWalking -> `10 >
   s²` -> vfn 0x1c0(svc, 0, 0, velocity); nothing more. Else the base.
2. 180c80000: m_flStepSoundTime > 0 -> `t - frametime x 1000` stored (0 below 0); > 0 -> return. m_fFlags & 0x60,
   movetype 7 / 8, sv_footsteps 0 -> return (180c8007c). Else 180c80100.
3. 180c80100: speed = `sqrt((z² + y²) + x²)`, horizontal `sqrt(x² + y²)`; vfn 0x1b8; m_fFlags bit 12 -> return; vfn
   0xb90 (m_bIsWalking) or speed < 135 -> return; not ladder: FL_ONGROUND and horizontal > 0.0001; walking = 220 >
   speed. Ladder: vfn 0x1a0, 0.5, vfn 0x1c0(1). Level 3 (180a793f5 in client the same): "wade" 0.65, type 2. 1 / 2:
   wade 0.2 / 0.5, type 3. Else (0, 4, 5): the given surface (null -> return before the timer), type 0, 0.2 / 0.5.
   Level >= 1: "CT_Water.StepLeft" too, at the step's volume before the duck's scale (EmitSound 180f69780, EmitSound_t
   +0 name, +8 origin, +0x14 volume; client.dll has no such splash). FL_DUCKING (+0x388 & 2, 0x18179be5c):
   volume x 0.65. vfn 0x1b0(svc, origin copy, surface, volume, 0).
4. SetStepSoundTime 180ae2230(svc, type, walking, velocity): 0 / 3 -> 400 walking else 300; 1 -> `floorf(35 -
   min(max((|vz| - 150) / 100, 0), 1) x 10) x 10`; 2 -> 600; FL_DUCKING -> + 100.
5. PlayStepSound 180c7ba40(svc, origin*, surface*, volume, force): gpGlobals +0x10 > 1 and sv_footsteps 0, or no surface
   -> nothing; foot svc+0x280 toggles; name from the pawn's footstep set (vfn 0x900, vfn 0 by the record's +0x10: a
   5-dword lookup, the third used; left and right names equal), sound system 0x1823ab500; EmitSound_t (pitch 100) to
   every player but its own (180590da0 with 0x181ff56c8, 1813aa290, 180f69780).
6. svc vfn 0x1d0 180adc080: PlayStepSound, then with sv_footsteps and a surface svc+0x688++, "player_footstep",
   svc+0x684 = 1. Called by 180ade0a0 (forced) and both jumps (origin before the jump) on svc+0x428.

## The freezes and the freeze period

- m_fFlags bit 5 FL_FROZEN (0x20), bit 6 FL_ATCONTROLS (0x40). CS2Fixes' game_ui (entities.cpp 425-475:
  SF_GAMEUI_FREEZE_PLAYER 32, Activate adds FL_ATCONTROLS, Deactivate removes) and point_viewcontrol (UpdatePlayerState
  507-549: FL_FROZEN with SF_POINT_VIEWCONTROL_FROZEN 1 << 5 = 32 or during m_bFreezePeriod, every frame; cleared by
  every other enable and the disable).
- 1809562c0: m_iRoundTime = mp_roundtime x 60 (cvttss2si); m_iFreezeTime = 2 in warmup, else mp_freezetime.
- Think 1809669f0: at 180967853 18092cdf0, then m_bFreezePeriod ? 180913f80 : 180916fb0. 180913f80 compares
  m_fRoundStartTime with the game time (180de86d0, 18017e2d0), a per-player pass (180a9ca80 for team 2 / 3: unread),
  timeout adjustments (+0xe4, m_iFreezeTime: unread), clears m_bFreezePeriod (18091479e), fires "round_freeze_end"
  (1809147ac; ZR_OnRoundFreezeEnd). Stores of 1 to +0xd8: 18092d991 (18092cdf0), 18094e249, 18094e5a9, 18094eada,
  18094f690, 1809588ef (which is RestartRound: unread).
- Other +0xd8 readers: CanPrimaryAttack 180a0fb0e / secondary 180a1022d (unread), CKnife 180a2fa80 (180a2fac1: no
  swing), grenades' vfn 0xcf8 (1809d0650: false, else vfn 0xda8(1): unread), a sound volume in 180adb580 (180adbe08,
  `cmp [rdi], 0x1a`: unread), 1809131d0 (= !m_bFreezePeriod), and 1802371c0, 180238d30, 18024b730, 1802809a0 / 1802809e0,
  18028e620, 18030d950, 180310fa0, 180332110, 18092c6a0, 18092e130, 18094df20 / e290 / ea70, 180951540, 180a6ecb0,
  180b00630 / 180b00730 / b00, 180deef20 (unread).
- The pause (m_bGamePaused) is SetupMove's 18093d780 test, not the freeze period.

## Velocity quantizer and CQuantizedFloatEncoder

- 180ae0230 CSMovementVelocityQuantizer_t (tier0 quantizedfloatencoder.h): 1803c1030(enc, name, 20 bits, flags 4,
  -16384, 16384), applied by 1803c1de0; also 182176538 for the landing record.
- Setup 1803c1030(enc, name, bits, flags, lo, hi): bits 1..31 and lo < hi (else pass-through: +0x1e = 3); zero-exact
  dropped when lo or hi is 0 with the matching round flag, turned into round down (lo == 0) / round up (hi == 0),
  dropped unless `0 > lo` and `hi > 0`; integers exact (8) drops the round and zero flags; +0x1d = `flags | flags << 4`
  (high nibble 1 / 2 / 4: lo, hi, zero exact); round down: `hi -= (hi - lo) / 2^bits`; round up: `lo +=` it; integers
  exact: n = floor(log2(int(hi) - int(lo))) (0 when <= 1), bits raised until 2^bits >= 2^(n + 1) (shl count mod 32: at
  31 it wraps, with a warning), `hi = (lo + 2^(n + 1)) - 2^(n + 1) / 2^bits`; +0x18 = 0 without round flags.
- Multiplier 1803c6a80: `m = (2^20 - 1) / (double)(max - min as float)` when |range| > 0.001; while 1803d6020 says m x
  range overflows (trunc to u32 > 2^20 - 1, or `(double)(2^20 - 1) < m x range`) a float f steps down one ULP from 1.0
  (integer DEC on its bits) and `m' = m x f`. For +-16384 / 20 bits m = 1048575 / 32768 passes at once. +0x10 = m,
  +0x20 = `1 / (2^bits - 1)` (double). +0x1e: bit 1 set; bits 2.. = log2(range) when a power of two.
- A special value already exact (1803c1f70) loses its bit (+0x1d >> 4: bit 0 min, 1 max, 2 zero).
- Quantize 1803c1de0: +0x1e bit 0 -> v. v < lo -> lo; v > hi -> hi; a special value -> itself. Else `q =
  (u32)(i64)((double)(v - lo) x m + 0.5)`; `r = (float)((double)q x inv x (double)(hi - lo) + (double)lo)`; minss(r, hi).

## Networked setters

Store only when the value compares unequal (ucomiss: NaN unequal), so an equal value keeps its old bits (-0.0 stays):
SetBaseVelocity 1803ea860, SetAbsVelocity 1803ea4a0, m_flFallVelocity (svc+0x25c: prelude, WalkMove, CheckFalling,
FinishMove), svc+0x418 / 0x3f4 / 0x41c, the body render offset (180cb8770: per axis, against the clamped value),
SetViewOffset 180242350 (against the new value, the clamped one stored), m_flWaterLevel 1803ebff0.

## The game surface table (scripts/surfaceproperties_game.txt)

- Entry 0x20 bytes (180be8f60): +0 maxspeedfactor, +4 jumpfactor, +8 / +0xc bullet penetration modifiers, +0x10
  legacymaterialtag, +0x14 gamematerial, +0x16 soundstackmaterial, +0x18 climbable, +0x19 isstairs, +0x1a isslippery,
  +0x1b allowsmokethrough, +0x1c reflectbullets, +0x1d reduceweaponimpact, +0x1e bulletspenetrate.
- 18158ba90(loader, kv, physprops): n = physprops vfn 0x10; defaults (180c07590: +0 1.0, +4 1.0, +8 1.0, +0xc 0.5, +0x10
  0, +0x14 0xffff0043, +0x18.. 0); map[n] = -1; each "SurfacePropertiesList" block's surfacePropertyName hashed
  (18054ba10) and found (physprops vfn 8) -> map[surface +0x10] = the block. For k in 0..n: s = physprops vfn 0x18(k);
  s+0x14 (base index) >= 0 -> 180beeb90 (entry[k] = entry[base] as it stands); map[k] >= 0 -> 180be8f60 parses over
  entry[k].
- vphysics2 180073760 loads physprops from "surfaceproperties/surfaceproperties.vsurf" (csgo's 164 surfaces; game/core's
  81-surface copy with "woodladder" behind it). On CS2's data an in-order copy and a transitive resolve give the same
  table (concrete's base no_decal comes after it: both are the defaults); four leave
  the defaults: slipperyslime / slipperyslide jump 0.7, ladder / wood_ladder climbable.

## Unread

- 180c80890 (the move's int-to-float), 180c7eb90, 180c7f0f0, 180ac51a0.
- 180a6ffb0 (the controller's), pawn+0x15a4 / 0x15a8, 180adbeb0's flag, 180ab72d0's TODO, 180308890 / 180ac7100 timing
  reads.
- The Ray_t layout in CategorizePosition; 180225130's sum order; 1814738b0's fallback; Friction's quantize argument.
- svc+0x690..0x698 latch's other effects (networking of the walk speed).
- How server.dll numbers collision layers past 40.
