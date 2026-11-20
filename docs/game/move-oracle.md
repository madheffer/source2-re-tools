# Running server.dll's movement natively (the movement oracle)

server_20261105, tier0_20261103. What it takes to call CCSPlayer_MovementServices' code in-process on fake objects (Windows x64): the functions a move runs, the fields and globals it reads, the hooks it needs.

## Functions

| Address | Module | What |
|---|---|---|
| 180ae2320 | server | CCS SetupMove (its base call 180c7e8d0 at 180ae2344) |
| 180c7e8d0 | server | base SetupMove (the user command into CMoveData) |
| 180ae26b0 | server | svc vfn 0x118 |
| 180adc390 | server | the move dispatch (PlayerMove 180adf830's own steps) |
| 180adf830 | server | PlayerMove (max speed: min(260, sv_maxspeed or m_flMaxspeed, the weapon's)) |
| 180ac4c00 | server | svc vfn 0x138 |
| 180ac4b20 | server | FinishMove (its base call 180c701a0 at 180ac4b3a) |
| 180aba720 | server | pawn vfn 0xcb8 "can move" (dev_cs_force_disable_move, the gamerules' freeze, +0xd40 / +0x14be.., a C4) |
| 180adc860 | server | the can't-move branch (freeze period) |
| 1801575b0 | server | entity vfn 0x228: returns m_pCollision |
| 1813aa290 | server | an identity's index from its address |
| 180cf7020 | server | CheckParameters (moves kept above 0 while m_iHealth > 0) |
| 1806892e0 | server | m_vecViewOffset's constructor (the encoders' tier0 registrations) |
| 180c868d0 | server | the active weapon |
| 180b67370 | server | pawn vfn 0x698: water level change -> water services slot 0xb8 |
| 180a7aab0 | server | camera services vfn 0x108: view punch |
| 180ae9a50 | server | svc slot 0x1a8: step sounds (UpdateStepSound -> 180c80000 -> 180c80100) |
| 180adc080 | server | svc slot 0x1d0: a footstep |
| 180c7ba40 | server | PlayStepSound |
| 180f69780 | server | EmitSound (the CT_Water.StepLeft splash) |
| 1803c5940 | server | AddFlags (pawn, 4): FL_WATERJUMP's m_fFlags 4 |
| 18069c8a0 | server | CInButtonState (svc+0x50) |
| 180187770 | server | cvar read: [handle + 8] + 0x58 |
| 1803c1030 | server | velocity quantizer setup (0x182176538, ..., 20, 4, -16384, 16384), guard 0x182176558 |
| 180cb7b90 | server | GetViewVectors: with no gamerules returns 0x182197e70 (CCSGameRules' table, 0x6c bytes, filled by its static initialiser 18009a0c0 at 0x1821193a0) |
| 180c00e80 | server | surface record -> its index (+0x10) |
| 180c2f3c0 | server | TraceShape(query, Ray_t*, start*, end*, CTraceFilter*, CGameTrace*) -> bool |
| 18021a5d0 | server | Ray_t from a hull (a line when mins == maxs) |
| 180ae3280 | server | movement filter ShouldHitEntity (vfn 8; pass entity from mv+4, else hits nothing) |
| 180addc00 / 180add580 | server | movement trace wrappers |
| 180ab55b0 | server | a filter constructor (...) |
| 180c26a40 | server | CGameSceneNode::SetAbsOrigin (node +0xc8) |
| 1803ea4a0 | server | SetAbsVelocity (+0x38c and the local +0x398 when a lane differs) |
| 1803eb7d0 | server | SetMoveType (+0x2f3, +0x2f2, m_nActualMoveType +0x2f5) |
| 1803e5390 | server | UpdateActualMoveType (parentless: = movetype) |
| 180d0e6a0 | server | collision interacts-with setter (pawn+0x5e8, mask); SetupMove's at 180ae25e4: +0x20 = pawn+0x608 |
| 180cdefb0 / 180d09310 | server | its change scope (with the owner's vfn 0x5e0: updates the physics body; 1804fdd16 faults without one) |
| 180adaaa0 | server | CheckFalling's landing (pawn, fall) |
| 180adbeb0 | server | the jump's sound (pawn, origin*, ...) |
| 180ade0a0 | server | impact punch (svc, mv, scale): svc+0x258 = 400, then vfn 0x1d0 (footstep) and the view punch |
| 180aded10 | server | movement EmitSound (svc, name) |
| 180f695d0 | server | an entity's EmitSound (entity, params, name) ("Player.Swim") |
| 180991b50 | server | SetupMove's prop push: props in the pawn's bounds (180993e00), mass >= 10, get impulses |
| 180a9d5a0 | server | FinishMove's svc+0x310 update (animation) |
| 180ae4570 | server | the jump's pose |
| 180c7e550 | server | view punch setter (network change notes 180c7aac0 / 180c7a850 / 180c7a100) |
| 180adc190 | server | fall damage |
| 180536730 | server | flags-changed callback |
| 180e6bfd0 / 180e8f610 | server | the ground's standing list |
| 180d03d00 | server | pawn+0x3f0's change note |
| 1806e8780 / 1806e88c0 / 1806e8a00 / 1806e97a0 | server | the render offset's change notes |
| 180c8cbc0 / 180c86c00 | server | CheckStuck: the pawn's entity index / the slot |
| 180590da0 | server | the sound system field |
| 181470980 / 1809b4ad0 | server | the grenade throw: AngleVectors / the throw (with sv_grenade_collision_sphere; grenades.md) |
| 180a73a74 | server | a function-local static's guard (the stair estimator's probe box) |

## Fields

### Pawn (CCSPlayerPawn, vtable 0x181794998)

| Offset | Field |
|---|---|
| +0x270 | scene node (CSkeletonInstance, vtable 0x181959ad0: vfn 0x60 / 0x68 return it) |
| node +0x10 | local CTransform (+0x1c scale, +0x2c quaternion w) |
| node +0xc8 / +0xd4 / +0xe0 | abs origin / abs angles / abs scale |
| node +0xf4 | dirty |
| node +0x208..0x210 | render offset (the body z) |
| +0x2d0 | m_iHealth (100 alive) |
| +0x2d8 | life state (0, 1, 2) |
| +0x2f2 / +0x2f3 / +0x2f5 | move type fields / movetype (2 walk, 9 ladder, 7 noclip) / m_nActualMoveType |
| +0x344 | team |
| +0x388 | m_fFlags (1, 2, 4 FL_WATERJUMP) |
| +0x38c / +0x398 | abs / local velocity |
| +0x3c8 | m_vecBaseVelocity |
| +0x3d8 | m_pCollision = +0x5e8 (m_Collision +8 its owner) |
| +0x3ec | m_hGroundEntity (-1 none) |
| +0x3f0, +0x3f4, +0x40c | (networked; change note on +0x3f0) |
| +0x404 | m_flWaterLevel (as a level: int(x 4 + 1), 0..5) |
| +0x412 | water type (1 water, 2 slime) |
| +0x608 | interacts-with |
| +0x818 | m_vecViewOffset (+0x820, +0x838) |
| +0xb10 | weapon services (+0x60 active weapon handle) |
| +0xb30 | CCSPlayer_WaterServices (vtable 0x181928258): +0x54, +0x58, +0x5c, +0x64 |
| +0xb48 | CCSPlayer_CameraServices (vtable 0x1819208c8) |
| +0xb50 | movement services |
| +0xc98 | controller handle |
| +0xe38 | hostage services (+0x48 -1) |
| +0x1478 | m_bIsWalking |
| +0x14e0 | m_flVelocityModifier |
| +0x14f4 | (ladder) |
| vfn 0xe0 | NetworkStateChanged |
| vfn 0xbb0 | the impact's animation event |

### Movement services (CCSPlayer_MovementServices, vtable 0x181923f70)

| Offset | Field |
|---|---|
| +0x38 | the pawn |
| +0x50 | CInButtonState: +0x58 held, +0x60 pressed & held, +0x68 pressed not held |
| +0x1ac | m_flMaxspeed (260) |
| +0x258 | impact (400) |
| +0x25c, +0x26c | |
| +0x270 / +0x278 | ground surface's hash / its record |
| +0x290 | stair estimator (+0 the svc); its height cache +0x298..0x2b8; +0x2b8..0x2c0, +0x2c4 |
| +0x310 | animation state (FinishMove) |
| +0x3f0, +0x3f4 | |
| +0x3f8 | ladder normal |
| +0x408 / +0x416 / +0x438 | ducked / ducking / air duck |
| +0x40c, +0x410, +0x418, +0x41c, +0x420, +0x424, +0x430, +0x434 | duck / step state |
| +0x415 / +0x439 | the duck key / walked |
| +0x43a, +0x650 | cleared before the dispatch |
| +0x440 | CheckVelocity's warning map (CUtlMap by pawn index) |
| +0x648 | trace counter (`inc dword [r + 0x648]`) |
| +0x680 | last command number |
| +0x68c, +0x690, +0x694, +0x698 | |
| +0x69c | m_flStamina |
| +0x6a0, +0x6a4, +0x6a8, +0x6ac, +0x6b0, +0x6b4 | |
| +0x6b8 / +0x6d0 | CCSPlayerLegacyJump (vtable 0x181923ec8) / ModernJump (0x181923ee8) objects (+8 the svc) |
| +0x6c8 | jump blocked |
| +0x6cc | the jump object's +0x14 |
| +0x6e0..0x700 | m_ModernJump +0x10..0x30: the last press, the usable press, the landing's tick / fraction, the landing's velocity |
| +0x708, +0x70c, +0x710, +0x718 | |
| +0x714 | just jumped |
| +0x7a8, +0x7ac | |

### Weapon

| Offset | Field |
|---|---|
| vfn 0xc20 | max speed |
| vfn 0xcb0 | m_zoomLevel (+0x1280) |
| vfn 0xc28 | m_nZoomLevels (vdata +0x7f4) |
| vfn 0xac0(0) | the clip |
| vfn 0xc58 | m_flAttackMovespeedFactor |
| +0xfa8 | m_bInReload |

### CMoveData (0x400)

| Offset | Field |
|---|---|
| +4 | the pawn's handle (every movement filter's pass entity) |
| +8 / +0x14 / +0x44 | angles |
| +0x2c / +0x30 / +0x34 | moves |
| +0x38 | velocity |
| +0xc8 | origin |
| +0xd4 / +0xd8 / +0xdc / +0xe0 | the command's ticks and the piece's span |
| +0x120 | max speed (1.0 in the freeze period) |
| +0x124 | SetupMove's copy of m_flMaxspeed (260) |
| +0x139 | after-teleport flag (lasts the command) |
| +0x13a | the latch flag (svc+0x690) |

CUserCmd (0x200): +8 its number.

### Globals

| Address | Field |
|---|---|
| 0x181e328d0 | gpGlobals -> CGlobalVars: +0x30 curtime, +0x34 frametime, +0x44 tick |
| 0x181f47078 | entity system: 64 chunk pointers of 512 0x70-byte CEntityIdentity (+0 entity, +0x10 handle) |
| 0x182331b00 + 0x10 | the same chunks (for 1813aa290) |
| 0x18234abd0 | the trace reset's default record |
| 0x18218e4f8 -> +0x28 | game surface table (0x20-byte entries) |
| 0x18218be00 | game event manager (CreateEvent vfn 0x30) |
| 0x1823ab5c0 | physics system (surface lookups by hash and index) |
| 0x18176b250 | Plat_FloatTime import slot |
| 0x181bcb7e0..0x181bcd4a0 | static TLS template |
| 0x1823ace90 | _tls_index |
| gs:[0x58][_tls_index] + 0x238 | _Init_thread_header's epoch (function-local statics' guards) |

### Ray_t, RnQueryAttr_t, CGameTrace

| Offset | Field |
|---|---|
| Ray_t +0x28 | type: 0 line (start + offset +0), 1 sphere (+0 / +0xc), 2 box (+0 mins / +0xc maxs) |
| filter +8 | RnQueryAttr_t: interacts-with +8, exclude +0x10, as +0x18, entity ids +0x20 / 0x24, owner ids +0x28, hierarchy +0x30, detail layers +0x34, target +0x36, object set +0x37, group +0x38, flags +0x39 |
| filter +0x40 | iterate entities |
| trace +0 / +8 | surface record / entity |
| +0x18 / +0x20 / +0x28 | body / shape / contents |
| +0x30 | body transform |
| +0x50 | shape's attributes (+0x68 the entity id) |
| +0x78 / +0x84 / +0x90 / +0x9c | start / end / normal / hit point |
| +0xa8, +0xac | , fraction |
| +0xb0 | triangle |
| +0xb8, +0xba, +0xbb, +0xbc | , ray type, start solid, |
| surface record +8 / +0x10 / +0x28 | hash / game table index / friction |

## Constants (cvar data slots; the value at +0x58; handle = slot - 8)

| Address | Cvar |
|---|---|
| 0x1821d3560 | sv_friction |
| 0x1821d3460 | sv_stopspeed |
| 0x1821d34f0 | sv_accelerate |
| 0x1821d3500 | sv_airaccelerate |
| 0x1821754f0 | sv_air_max_wishspeed |
| 0x181ff57a0 | sv_gravity |
| 0x1821754d0 | sv_jump_impulse |
| 0x1821d3590 | sv_stepsize |
| 0x182175520 | sv_standable_normal |
| 0x182175510 | sv_walkable_normal (StayOnGround and StepMove read it too) |
| 0x1821d3570 | sv_bounce |
| 0x182175570 | sv_water_slow_amount |
| 0x182175450 | sv_staminamax |
| 0x1821753c0 / 0x1821753d0 | sv_staminajumpcost / sv_staminalandcost |
| 0x182175440 | sv_staminarecoveryrate |
| 0x1821754e0 | sv_jump_spam_penalty_time |
| 0x182175460 | sv_timebetweenducks |
| 0x1821754a0 | sv_step_move_vel_min |
| 0x1821d3580 | sv_maxvelocity |
| 0x182175550 / 0x182175530 / 0x182175540 | sv_ladder_scale_speed / sv_ladder_dampen / sv_ladder_angle |
| 0x1821755b0 | sv_legacy_jump |
| 0x182175628 / 0x182175618 | sv_autobunnyhopping / sv_enablebunnyhopping |
| 0x182175580 | sv_jump_precision_enable |
| 0x182175470 | sv_accelerate_use_weapon_speed |
| 0x182175608 | sv_optimizedmovement |
| 0x182175590 | sv_quantize_movement_input |
| 0x18211a3c0 / 0x18211a3b0 | mp_solid_enemies / mp_solid_teammates |
| 182175400 (data 182175408) | sv_bhop_time_window (modern jump: 0.0625 with sv_legacy_jump 0) |
| 0x1821d3480 | sv_noclipspeed (1200) |
| 0x1821d3470 | sv_noclipaccelerate (5) |
| 0x1821d34e0 | sv_maxspeed (320) |
| 0x1821b9a28 | host_timescale (1) |
| 0x1821d3540 / 0x1821d3550 | sv_rollspeed (200) / sv_rollangle (0) |
| 0x182175500 | view_punch_decay (18) |
| 0x181f9e218 | bot_mimic |
| 0x182191540 | in_spewbuttondelta |
| 0x182175480 | sv_accelerate_debug_speed |
| 0x182175490 | sv_show_move_collisions |
| 0x1821754b0 | sv_use_playercache (0: the cache gives the same results) |
| 0x1821753e0 / 0x182175430 | dev_create_bhop_reports / dev_create_move_report |
| 0x1821755f8 | bot_crouch |

## A move's calls

1. SetupMove (180ae2320) on the command's first piece.
2. vfn 0x118 (180ae26b0).
3. svc+0x650 / 0x648 / 0x43a cleared; dispatch 180adc390 unless stuck.
4. vfn 0x138 (180ac4c00).
5. FinishMove (180ac4b20) on the last piece.

## Loading the image by hand

- Sections at their RVAs, preferred base 0x180000000 (relocated otherwise); tier0 and kernel32 imports bound; .pdata registered with RtlAddFunctionTable for unwinding (RtlVirtualUnwind).
- Static TLS needs its own block: the TEB's array gs:[0x58] one slot longer, the template copied in, _tls_index set to the slot. Left at 0, the function-local statics' guards read and write the host exe's thread-locals.
- No initialisers run: the globals the code reads must be filled; statics made as their first use would (the velocity quantizer with its guard set so the TLS path never runs; the view vectors; the trace reset's record; the surface table; the event manager).
- CheckStuck: 180c8cbc0, 180c86c00 and Plat_FloatTime's import slot; its 1-in-64 gate; developer 0.
- The freeze period: "can move" false, mv+0x120 1.0 -> 180adc860; FL_FROZEN / FL_ATCONTROLS.

## Unread

- The base SetupMove / FinishMove and PlayerMove's own steps, the subtick loop and the step builder (not run natively).
- Standing on players / someone on your head; client.dll's step code.
