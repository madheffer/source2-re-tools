# Ragdoll settling: prop_ragdoll's sleep rule

server_20261105, vphysics2_20260924, client_20261112 (image base 0x180000000).

## Functions

| Address | Module | What |
|---|---|---|
| 180e95f00 | server | "CRagdollPropSettleThink" (think table 0x1806af9a0) |
| 180f85850 | server | all parts asleep (stored at +0xb3c) |
| 180e6f920 | server | the settle |
| 180927cb0 | server | gpGlobals time |
| 1803d6f50 | server | abs origin |
| 1801035d0..1801037bc | server | the convars' registrations |
| FUN_1801c02a0 | vphysics2 | island sleep test (Integrator.SleepTest) |
| 1801e7df0 / 1801f5fb0 | vphysics2 | CRnWorld constructors (iteration stores at 1801e8481 / 1801f681f) |
| 0x180063fc0 / 0x180063fd0 / 0x180063fe0 / 0x180063fa0 | vphysics2 | CVPhys2World slots 24 set +0x1b8 / 25 read it / 26 set +0x1bc / 45 set +0x1c8 |
| 0x1800131a0 | vphysics2 | CPhysicsBody slot 125: sets +0x249 bit 1 (wakes when cleared on a dynamic body) |
| 0x1800131e0 | vphysics2 | slot 126: reads bit 1 |
| 0x1800131f0 -> 1801be010 | vphysics2 | slot 127 Sleep -> CRnBody |
| 0x180013200 -> 1801c0ff0 | vphysics2 | slot 128 Wake |
| 0x180013210 | vphysics2 | slot 129 asleep: +0x249 bit 2 |

## Fields

| Offset | Field |
|---|---|
| CRagdollProp +0x200 / +0x270 vfn 0x68 | the physics object |
| +0x360 bit 17 | settle off |
| +0xa90 / +0xa98 | part count / parts (stride 0x30) |
| +0xb3c | all asleep |
| +0xb60 | last origin |
| +0xb6c | spawn time |
| +0xb70 | last time the origin moved |
| +0xbd8 | object whose vfn 8 the think calls |
| CRnWorld +0x1a0 / +0x1a8 / +0x1b8 / +0x1bc / +0x1c0 / +0x210 | 1.2f / 4 / position iterations 2 / velocity iterations 8 / 4 / 100f |
| CPhysicsBody +0x249 | bit 1 / bit 2 asleep |
| VPhysXBodyPart_t | m_nFlags 0, m_flMass 4, m_rnShape 8, m_nCollisionAttributeIndex 0x70, m_nReserved 0x72, m_flInertiaScale 0x74, m_flLinearDamping 0x78, m_flAngularDamping 0x7c, m_flLinearDrag 0x80, m_flAngularDrag 0x84, m_bOverrideMassCenter 0x88, m_vMassCenterOverride 0x8c (no iteration field) |
| RnBodyDesc_t | m_nGameFlags 0xc0, m_nMinVelocityIterations 0xc4, m_nMinPositionIterations (serialized body state, not a model's) |
| client 0x180878d9f | m_bWasStationaryLastUpdate (CCSPlayerAnimationState's) |

## Constants

| Value | What |
|---|---|
| ragdoll_prop_settle | 1, "Enable more aggressive ragdoll settling" (flags 0x2000) |
| ragdoll_prop_sleepaftertime | 4.0, "After this many seconds of being basically stationary, the ragdoll will go to sleep." |
| ragdoll_prop_sleepdisabletime | 1.5, "Ragdoll is not allowed to physically sleep until this timer has elapsed." |
| ragdoll_scale_sleep_tolerance | 1 (no help) |
| 0.1 (0x3dcccccd) | think interval |
| 0.5 s, speed² 0.16, spin² 0.00487 | island sleep test |
| 0x1803f9b20 / 0x1803f44e0 | CVPhys2World / CPhysicsBody vtables |

## Client death ragdolls

client.dll has no ragdoll sleep convar (strings: `cl_ragdoll_limit`, `cl_ragdoll_physics_enable`,
`cl_ragdoll_workaround_threshold`, `cl_phys_sleep_enable` "Enable sleeping for dynamic physics bodies", nothing like
`ragdoll_prop_sleepaftertime`). A client ragdoll sleeps only through vphysics2's island sleep: every body under the
speed / spin limits for 0.5 s, then the island. No client function calls both `call [reg+0xc0]` / `call
[reg+0xd0]` with an immediate edx: the client keeps 8 / 2 iterations; a ragdoll's island gets the world's.

With these iterations and this sleep test, light parts (3 kg) resting on other ragdolls' parts keep a solved velocity
of ~1-1.5 u/s (above the 0.4 limit) and hold a pile's island awake (measured on a reimplementation of the solver).

## The settle think 180e95f00

1. All parts asleep (180f85850 -> +0xb3c): end. Else +0xbd8's vfn 8, 180e6f920, next think now + 0.1.
2. 180e6f920 (only with +0x360 bit 17 clear and ragdoll_prop_settle):
   1. since = now - +0xb70, age = now - +0xb6c.
   2. since >= sleepdisabletime: physics object vfn 0x168(1.5, 1); else vfn 0x168(1.5, 0) and return.
   3. tolerance = 2 age clamped [2, 20]; with ragdoll_scale_sleep_tolerance x max(0, the smallest part's vfn 0x418 (its
      scale) and 1).
   4. d = abs origin - +0xb60: any |d_i| > tolerance -> +0xb70 = now, +0xb60 = origin, return.
   5. since >= sleepaftertime: every part vfn 0x3f8, then +0xb3c = all asleep.

## Unread

vfn 0x168 in vphysics2 (CPhysAggregateInstance), +0xbd8's vfn 8, when the server restarts the think after a wake.
