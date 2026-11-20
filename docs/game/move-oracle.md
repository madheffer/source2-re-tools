# The movement oracle: server.dll's own movement on the sim's inputs (2026-11-11)

`sim/src/bin/move_oracle` runs server_20261105.dll's movement code natively, in-process, on fake objects, against the
sim's port (`sim/src/movement`, `move_job`) on the same inputs, and compares every state and event word of the move
job bit for bit. It is the "ports of CS2 code are checked against Valve's DLL called natively" check for phase 2
(docs/RUST_PORT.md). Windows x64 only; needs server_20261105.dll and tier0_20261103.dll (source2-compiler
tools/re/binaries).

```bash
B="${S2C_BINARIES:-tools/re/binaries}"; T=$TEMP
cargo run --release -p ze-sim --bin move_oracle -- "$B" 300000          # the leaf functions (units.rs)
cargo run --release -p ze-sim --bin move_oracle -- "$B" --qfe 200000    # CQuantizedFloatEncoder (units.rs)
cargo run --release -p ze-sim --bin move_oracle -- "$B" --throw 200000  # the grenade throw: AngleVectors 181470980, 1809b4ad0 (throw.rs; grenades.md)
# a recorded round (web/server/cs2web/dev/wasm-oracle.mjs keeps its log with ZE_ORACLE_LOG), then its pieces through server.dll
(cd web && ZE_ORACLE_LOG=$T/hold.bin node server/cs2web/dev/wasm-oracle.mjs ze_hold_em_p 12 20)
cargo run --release -p ze-sim --bin move_oracle -- "$B" --log web/public/maps/ze_hold_em_p/physics.bin $T/hold.bin
cargo run --release -p ze-sim --bin move_oracle -- "$B" --fuzz web/public/maps/ze_hold_em_p/physics.bin $T/hold.bin 3000
# ZE_ORACLE_ALT_CVARS=1: every float cvar off its default; ZE_ORACLE_MODERN=1: the modern jump; ZE_ORACLE_STUCK=1: CheckStuck;
# ZE_ORACLE_UNLOCK=1 / 0: CS2Fixes' movement unlocker on / off (a log recorded now has it on: the job's word 83 bit 0x400)
```

Debugging: `ZE_ORACLE_PIECE=<n>` prints piece n's traces, server.dll's (each with svc+0x648 and its caller) then the
sim's (`movement::trace::oracle_log`, native builds only, off unless asked), and every increment of svc+0x648 (each
`inc dword [r + 0x648]` in the movement code becomes an int3 the fault handler emulates: `stubs.rs TRACE_COUNTS`);
the fuzz also prints the piece's input. A fault prints its server.dll VA, the call chain (the image's .pdata
registered with RtlAddFunctionTable, walked with RtlVirtualUnwind), the last logged vcall and its real vtable.

## Results (2026-11-11)

| Run | Pieces / cases | Differences |
|---|---|---|
| Friction / Accelerate / AirAccelerate / AddGravity on random states | 300,000 each | 0 |
| CQuantizedFloatEncoder setup + quantize, random configurations | 200,000 configs, 10.3M values | 0 |
| Recorded rounds (12 bots, 20 s): hold_em, atix panic, dark souls, RE3 | 55,306 | 0 |
| The grenade throw (`--throw 200000`, 2026-11-16): AngleVectors 181470980, 1809b4ad0 with its trace hooked / with sv_grenade_collision_sphere 1 | 200,000 + 400,000 | 0 |
| Fuzz, 12 players x 3000 commands each: the four maps | 287,809 | 0 |
| The same, every float cvar off its default (`ZE_ORACLE_ALT_CVARS=1`, 1500 commands) | 144,447 | 0 |
| A recorded hold_em round and the fuzz with CS2Fixes' movement unlocker patched into server.dll (`ZE_ORACLE_UNLOCK=1`, and `=0`; 2026-11-12) | 13,826 + 71,829 each | 0 |
| The same, the modern jump (`ZE_ORACLE_MODERN=1`: sv_legacy_jump 0, sv_bhop_time_window 0.0625) | 287,809 (1,597 jumps, 1,600 landings) | 0 |

Two runs of the whole set print the same (the TLS block below ended a run-to-run flake in the stair smoothing).

The fuzz covers (dark souls / RE3 / atix): 50k airborne pieces a map, ~550 jumps and landings, 15-27k ducked, 11k
walking (IN_SPEED), 5.7k on a ladder (atix), 12-18k in water and 6-18k swimming (dark souls, RE3), 6k noclip, the
water jump, swim strokes, impacts, step-ups, sv_maxvelocity (falls out of the map), the command after a teleport.
The recorded rounds add the bots' real routes (stairs, movers' grounds, the speed latch, the stair estimator).

## The image (image.rs)

server.dll is mapped by hand (as rubikon/tests/SceneOracle): sections at their RVAs, at the preferred base
0x180000000 when free (relocated otherwise), tier0 and kernel32 imports bound (tier0 staged as
`%TEMP%/ze_tier0_20261103/tier0.dll`), every other import a trap naming itself. Its static TLS gets a block of its own (own_tls: the TEB's array gs:[0x58] copied one slot longer, the template 0x181bcb7e0..0x181bcd4a0 copied in, _tls_index 0x1823ace90 set to the slot): left at 0, server.dll's function-local statics' guard (_Init_thread_header's epoch at gs:[0x58][_tls_index] + 0x238, e.g. 180a73a74, the stair estimator's probe box) read and wrote the oracle exe's own Rust thread-locals, a run-to-run flake in the stair smoothing. No initialisers run: what the code
reads from globals is filled (fakes.rs). `Image::hook` (mov rax, target; jmp rax at a function's entry),
`hook_noting_caller` (the caller's return address stored first), `ret` (with eax), `watch_incs`.

## The objects (fakes.rs, objs.rs)

- **Arena**: 64 MB RWX, never freed. Vtables: logged copies of the real ones (each slot a 28-byte thunk storing
  `(id << 16) | slot` in LAST_VCALL and jumping to server.dll's function), `set_slot` overrides; trap vtables for
  objects the harness implements (each slot names itself and its caller).
- **gpGlobals** (0x181e328d0 → CGlobalVars): +0x30 curtime, +0x34 frametime, +0x44 tick.
- **Entity system** (0x181f47078 → 64 chunk pointers of 512 0x70-byte CEntityIdentity: +0 the entity, +0x10 its
  handle; 0x182331b00 + 0x10 the same chunks for 1813aa290, an identity's index from its address). Handles: the world
  0x8000, the pawn 0x8000 | 0x7ff0, the weapon | 0x7ff1, the controller | 0x7ff2 (past any map entity's index; the
  sim's are the entity id | 0x10000). Each entity: +0 vtable, +0x10 its identity, +0x3d8 m_pCollision = +0x5e8
  (vfn 0x228 1801575b0 returns it), m_Collision +8 its owner.
- **The pawn** (0x4000 bytes, CCSPlayerPawn's vtable 0x181794998): slot 0xe0 (NetworkStateChanged) a no-op, 0xcb8
  ("can move", 180aba720: dev_cs_force_disable_move, the gamerules' freeze, +0xd40 / +0x14be.., a C4) true.
  +0x270 the scene node (CSkeletonInstance's vtable 0x181959ad0: vfn 0x60 / 0x68 return it; +0x10 the local
  CTransform with +0x1c scale 1 and +0x2c quaternion w 1, +0xc8 abs origin, +0xd4 abs angles 0, +0xe0 abs scale 1,
  +0xf4 dirty 0, +0x208..0x210 the render offset: the body z), +0x2d0 m_iHealth (100 alive: CheckParameters keeps the
  moves above 0, 180cf7020), +0x818 m_vecViewOffset (its constructor 1806892e0 run each piece: the encoders' tier0
  registrations), +0xb10 the weapon services (+0x60 the active weapon's handle, 180c868d0), +0xb30
  CCSPlayer_WaterServices (vtable 0x181928258, slot 0xb8 a no-op: the water level's change callback from pawn vfn
  0x698 180b67370), +0xb48 CCSPlayer_CameraServices (vtable 0x1819208c8: vfn 0x108 180a7aab0 the view punch, zero
  here), +0xb50 the movement services, +0xc98 the controller's handle, +0xe38 the hostage services (+0x48 -1).
- **The movement services** (0x2000, CCSPlayer_MovementServices' vtable 0x181923f70): slots 0x1a8 (180ae9a50, the step
  sounds) and 0x1d0 (180adc080, a footstep) server.dll's own ("Not covered" below: what's recorded). +0x38 the pawn, +0x290 the stair
  estimator (+0 the svc; its height cache +0x298..0x2b8 kept per player across pieces, as the sim keeps its own by the
  job's word 121), +0x440 CheckVelocity's warning map (a one-node CUtlMap: the pawn's index, warned "at 1e30": never
  warns), +0x6b8 / 0x6d0 the legacy / modern jump objects (CCSPlayerLegacyJump 0x181923ec8 / ModernJump 0x181923ee8
  vtables, slot 0 a no-op; +8 the svc), +0x1ac m_flMaxspeed 260 (and mv+0x124, SetupMove's copy, every piece).
- **The weapon** (trap vtable): vfn 0xc20 max speed, 0xcb0 m_zoomLevel (+0x1280), 0xc28 m_nZoomLevels (vdata +0x7f4), 0xac0(0) the clip, 0xc58
  m_flAttackMovespeedFactor; +0xfa8 m_bInReload.
- **CMoveData** (0x400): rebuilt from the job each piece; +4 the pawn's handle (the base SetupMove's: every movement
  filter takes its pass entity from it), +8 / +0x14 / +0x44 the angles, +0x2c / 0x30 / 0x34 the moves, +0x38
  velocity, +0xc8 origin, +0xd4 / 0xd8 / 0xdc / 0xe0 the command's ticks and the piece's span, +0x120 max speed,
  +0x124 260, +0x139 the after-teleport flag (lasts the command), +0x13a the latch flag.
- **A CUserCmd** (0x200): +8 its number (svc+0x680 + 1 when the job says "after a teleport").

## The calls per piece (piece.rs)

As move_job: SetupMove (CCS 180ae2320 with its base call 180c7e8d0 at 180ae2344 nopped: the job is what the base
copies) on the command's first piece; vfn 0x118 (180ae26b0); svc+0x650 / 0x648 / 0x43a cleared and the dispatch
180adc390 (PlayerMove 180adf830's own steps: its max speed comes from the job) unless the stuck flag; vfn 0x138
(180ac4c00); FinishMove (180ac4b20, its base call 180c701a0 at 180ac4b3a nopped) on the last.

## The job ↔ the fields

| Job word | Field |
|---|---|
| 0-2, 3-5 | mv+0xc8 (and the node's abs origin), mv+0x38 (and pawn+0x38c abs, +0x398 local velocity) |
| 6-8 | pawn+0x3c8 m_vecBaseVelocity |
| 9 | flags: 1 / 2 / FL_WATERJUMP (0x1000 → m_fFlags 4, 1803c5940(pawn, 4)) in pawn+0x388; svc+0x408 ducked, +0x416 ducking, +0x438 air duck, +0x6c8 jump blocked, +0x714 just jumped, +0x415 the duck key, +0x439 walked; pawn+0x1478 m_bIsWalking; pawn+0x2f3 / 0x2f5 movetype (2 walk, 9 ladder, 7 noclip); pawn+0x412 water type (1 water, 2 slime) |
| 10 | pawn+0x3ec m_hGroundEntity (-1: none) |
| 11-29 | svc+0x25c, 0x26c, 0x40c, 0x410, 0x418, 0x420, 0x424, 0x430, 0x434, 0x69c, 0x6cc (the jump object's +0x14), 0x6a0, 0x6a4, 0x6a8, 0x6ac, 0x6b0, 0x6b4, 0x710, 0x718 |
| 30-32 | pawn+0x14e0, 0x40c, 0x3f4 |
| 33 / 63 | the water level: int(pawn+0x404 x 4 + 1) (0..5) / pawn+0x404 m_flWaterLevel |
| 34-37 | svc+0x3f8 ladder normal, pawn+0x14f4 |
| 39 | svc+0x270 the ground surface's hash, +0x278 its record (tracer.rs) |
| 84-87 | water services +0x54, +0x58, +0x5c, +0x64 |
| 96-105 | pawn+0x608 interacts-with; svc+0x690 / mv+0x13a; svc+0x694, 0x698, 0x7a8, 0x7ac, 0x708, 0x70c, 0x68c |
| 125, 126-134 | sv_bhop_time_window (handle 182175400, data 182175408); m_ModernJump svc+0x6e0..0x700 (its +0x10..0x30: the last press, the usable press, the landing's tick / fraction, the landing's velocity) |
| 112-120 | svc+0x41c, 0x3f4, the node's +0x210, pawn+0x820 (and +0x838), svc+0x2b8..0x2c0, +0x2c4, +0x3f0 |
| 40-43 | svc+0x58 held, +0x60 pressed & held, +0x68 pressed not held (CInButtonState at svc+0x50: 18069c8a0) |
| 44-52, 106-109 | mv+0x2c, 0x30, angles, frametime / curtime / tick (gpGlobals), mv+0xdc, 0xe0, 0xd4, 0x120, piece flags |
| 53-55, 61-62 | alive / dying → pawn+0x2d8 (0, 1, 2) and +0x2d0; team pawn+0x344; the weapon's fields |
| 64-83, 110-111, 122-125, 137 | cvars (below) |
| 88-95 | events: 88 180adaaa0's fall speed, 89-92 the jump sound 180adbeb0's call and origin, 93 180ade0a0's scale above 0, 94 svc+0x648, 95 "Player.Swim" through 180aded10 / 180f695d0 |

## Globals filled (cvar data slots: a value block, the value at +0x58)

From the job: sv_friction 0x1821d3560, sv_stopspeed 0x1821d3460, sv_accelerate 0x1821d34f0, sv_airaccelerate
0x1821d3500, sv_air_max_wishspeed 0x1821754f0, sv_gravity 0x181ff57a0, sv_jump_impulse 0x1821754d0, sv_stepsize
0x1821d3590, sv_standable_normal 0x182175520, sv_walkable_normal 0x182175510 (StayOnGround and StepMove read this one
too), sv_bounce 0x1821d3570, sv_water_slow_amount 0x182175570, sv_staminamax 0x182175450, sv_staminajumpcost
0x1821753c0, sv_staminalandcost 0x1821753d0, sv_staminarecoveryrate 0x182175440, sv_jump_spam_penalty_time
0x1821754e0, sv_timebetweenducks 0x182175460, sv_step_move_vel_min 0x1821754a0, sv_maxvelocity 0x1821d3580 (word
137), sv_ladder_scale_speed 0x182175550, sv_ladder_dampen 0x182175530, sv_ladder_angle 0x182175540, sv_legacy_jump
0x1821755b0, sv_autobunnyhopping 0x182175628, sv_enablebunnyhopping 0x182175618, sv_jump_precision_enable
0x182175580, sv_accelerate_use_weapon_speed 0x182175470, sv_optimizedmovement 0x182175608,
sv_quantize_movement_input 0x182175590, mp_solid_enemies 0x18211a3c0, mp_solid_teammates 0x18211a3b0.
Fixed: sv_noclipspeed 0x1821d3480 (1200), sv_noclipaccelerate 0x1821d3470 (5), sv_maxspeed 0x1821d34e0 (320),
host_timescale 0x1821b9a28 (1), sv_rollspeed 0x1821d3540 (200), sv_rollangle 0x1821d3550 (0), view_punch_decay
0x182175500 (18), bot_mimic 0x181f9e218, in_spewbuttondelta 0x182191540, sv_accelerate_debug_speed 0x182175480,
sv_show_move_collisions 0x182175490, sv_use_playercache 0x1821754b0 (0: the cache gives the same results),
dev_create_bhop_reports 0x1821753e0, dev_create_move_report 0x182175430, bot_crouch 0x1821755f8 (all 0).
(The cvar's handle is the data slot - 8: 180187770 reads [handle + 8] + 0x58.)

Statics made the way their first use would: the velocity quantizer (1803c1030(0x182176538, ..., 20, 4, -16384, 16384),
its guard 0x182176558 set so the thread-safe-static path, which reads a TLS slot, never runs); the view vectors
(GetViewVectors 180cb7b90 with no gamerules returns 0x182197e70: CCSGameRules' table, filled by its static
initialiser 18009a0c0 at 0x1821193a0, copied there, 0x6c bytes); the trace reset's default record (0x18234abd0);
the game surface table (0x18218e4f8 → +0x28: 0x20-byte entries; a surface record's +0x10 is its index, 180c00e80);
the game event manager (0x18218be00: CreateEvent, vfn 0x30, gives none).

## Traces (tracer.rs)

TraceShape 180c2f3c0(query, Ray_t*, start*, end*, CTraceFilter*, CGameTrace*) → bool is hooked: the ray (+0x28 its
type: 0 line from start + offset +0, 1 sphere +0 / +0xc, 2 box +0 mins / +0xc maxs; 18021a5d0 builds it from a hull,
a line when mins == maxs), the filter (RnQueryAttr_t at +8: interacts-with +8, exclude +0x10, as +0x18, entity ids
+0x20 / 0x24, owner ids +0x28, hierarchy +0x30, detail layers +0x34, target +0x36, object set +0x37, group +0x38,
flags +0x39; iterate entities +0x40) go to game::trace::trace_shape on the cast world, each entity through the
filter's own ShouldHitEntity (vfn 8; the movement filter's 180ae3280 needs the pass entity from mv+4, else it hits
nothing), the result written at CGameTrace's offsets (+0 the surface record, +8 the entity, +0x18 body, +0x20 shape,
+0x28 contents, +0x30 the body transform, +0x50 the shape's attributes (+0x68 the entity id), +0x78 start, +0x84 end,
+0x90 normal, +0x9c hit point, +0xa8, +0xac fraction, +0xb0 triangle, +0xb8, +0xba ray type, +0xbb start solid,
+0xbc). A hit's surface is a fake record per hash (+8 the hash, +0x10 its game table index, +0x28 friction). Above
TraceShape everything is server.dll's: the movement wrapper 180addc00 and 180add580, the filters' constructors
(180ab55b0 ...), ShouldHitEntity.

## Hooked and stubbed (stubs.rs)

Hooked to plain stores: CGameSceneNode::SetAbsOrigin 180c26a40 (the node's +0xc8), SetAbsVelocity 1803ea4a0
(m_vecAbsVelocity +0x38c and the local +0x398 when a lane differs), SetMoveType 1803eb7d0 (+0x2f3, +0x2f2, and
m_nActualMoveType +0x2f5 = the movetype: UpdateActualMoveType 1803e5390's parentless case), the collision's interacts-with setter 180d0e6a0(pawn+0x5e8, mask) (SetupMove's at 180ae25e4: +0x20 = pawn+0x608; its change scope 180cdefb0 / 180d09310 and the owner's vfn 0x5e0 update a physics body the fake pawn hasn't: a recorded round's first team change faulted at 1804fdd16).
Hooked to record the sim's events: CheckFalling's landing 180adaaa0(pawn, fall), the jump's sound 180adbeb0(pawn,
origin*, ...), the impact punch 180ade0a0(svc, mv, scale) (its svc+0x258 = 400, footstep and view punch skipped), the
movement's EmitSound 180aded10(svc, name) and an entity's 180f695d0(entity, params, name) ("Player.Swim").
Returned at once: SetupMove's prop push 180991b50 (the props in the pawn's bounds, 180993e00, mass >= 10 get impulses:
the physics world's), FinishMove's svc+0x310 update 180a9d5a0 (animation), the jump's pose 180ae4570, the view punch
180c7e550, the fall damage 180adc190, the flags-changed callback 180536730, the ground's standing list 180e6bfd0 /
180e8f610, pawn+0x3f0's change note 180d03d00, the render offset's change notes 1806e8780 / 88c0 / 8a00 / 97a0. Hooked for CheckStuck: 180c8cbc0 (the
pawn's entity index), 180c86c00 (the slot), Plat_FloatTime's import slot: the job's words 139-141; developer 0.

## Not covered (what the oracle can't see)

- The base SetupMove / FinishMove (the user command into CMoveData and back), PlayerMove's own steps (its max speed:
  min(260, sv_maxspeed or m_flMaxspeed, the weapon's)), the subtick loop and the step builder (cmd.rs, move-state.js):
  JS's, compared through the job's inputs only.
- Standing on players and someone on your head (the recorded rounds run GFL's noblock: no player is solid to another;
  the fuzz passes no pawn); client.dll's step code (steps.rs, your own prediction's). The server's step sounds are covered
  (2026-11-11): UpdateStepSound (svc vfn 0x1a8 180ae9a50 → 180c80000 → 180c80100), SetStepSoundTime and svc vfn
  0x1d0 run as server.dll's own; PlayStepSound 180c7ba40 and EmitSound 180f69780 (the CT_Water.StepLeft splash) are
  recorded as the job's step words 146-182; the impact 180ade0a0 stays hooked (the scale for word 93) and does its
  step half itself (svc+0x258 = 400, then the real vfn 0x1d0); a fake physics system (0x1823ab5c0) answers the
  surface lookups by hash and index with the tracer's records; 180590da0 (the sound system field) returns -1; pawn vfn
  0xbb0 (the impact's animation event) is a no-op. Four maps, every mode: 0 differ. The view punch is covered too: its
  setter 180c7e550 runs (only the network change notes 180c7aac0 / 180c7a850 / 180c7a100 return), the camera services
  carry the job's words 183-187, and 180ade0a0 runs whole behind a trampoline (its first 13 bytes, then a jump back)
  after the hook notes the scale; the fuzz freezes players now and then (FL_FROZEN / FL_ATCONTROLS) and runs the freeze period (job word 53 0x40: the "can move" stub returns false, mv+0x120 1.0: the can't-move branch 180adc860, covered "freeze period" / "freeze period airborne"). CheckStuck is covered (2026-11-11): the pawn's entity index (180c8cbc0), the slot
  (180c86c00) and Plat_FloatTime (the import slot 0x18176b250) come from the job's words 139-141; `ZE_ORACLE_STUCK=1`
  passes the 1-in-64 gate on every command and sinks players into the floor now and then (atix / RE3 / dark souls /
  hold_em: 0 differ, 16k pieces in the check).
