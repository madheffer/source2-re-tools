# Ragdolls settling: CS2's prop_ragdoll sleep rule, and why a death-ragdoll pile never sleeps

What decides when a ragdoll falls asleep in CS2, traced 2026-11-18. Ported (as a labelled deviation on the death
ragdolls) in rubikon/src/Game/RagdollSettle.cs. Addresses: **server_20261105.dll**, **vphysics2_20260924.dll**,
**client_20261112.dll** (source2-compiler tools/re/binaries), image base 0x180000000.

## 1. CS2's client death ragdolls have no settle rule

- client.dll has no ragdoll sleep convar (strings: `cl_ragdoll_limit`, `cl_ragdoll_physics_enable`,
  `cl_ragdoll_workaround_threshold`, `cl_phys_sleep_enable` "Enable sleeping for dynamic physics bodies", nothing like
  `ragdoll_prop_sleepaftertime`). `m_bWasStationaryLastUpdate` (0x180878d9f) is CCSPlayerAnimationState's.
- So a client ragdoll sleeps only through vphysics2's island sleep: every body under the speed / spin limits for 0.5 s
  (Integrator.SleepTest, FUN_1801c02a0: speed² 0.16, spin² 0.00487), then the island.

## 2. The solver's iterations are vphysics2's defaults

- CRnWorld's constructors (1801e7df0 at 1801e8481, 1801f5fb0 at 1801f681f): velocity iterations world+0x1bc = 8,
  position iterations +0x1b8 = 2, +0x1c0 = 4, +0x1a8 = 4, +0x1a0 = 1.2f, +0x210 = 100f.
- CVPhys2World vtable 0x1803f9b20: slot 24 (0x180063fc0) sets +0x1b8, slot 25 (0x180063fd0) reads it, slot 26
  (0x180063fe0) sets +0x1bc, slot 45 (0x180063fa0) sets +0x1c8. A scan of client.dll for `call [reg+0xc0]` /
  `call [reg+0xd0]` with edx from an immediate found no function calling both: the client keeps 8 / 2.
- A model's part (`VPhysXBodyPart_t`, schema in vphysics2: m_nFlags 0, m_flMass 4, m_rnShape 8,
  m_nCollisionAttributeIndex 0x70, m_nReserved 0x72, m_flInertiaScale 0x74, m_flLinearDamping 0x78,
  m_flAngularDamping 0x7c, m_flLinearDrag 0x80, m_flAngularDrag 0x84, m_bOverrideMassCenter 0x88,
  m_vMassCenterOverride 0x8c) has no iteration field; `m_nMinVelocityIterations` (0xc4) /
  `m_nMinPositionIterations` belong to the serialized body state (RnBodyDesc_t, after m_nGameFlags 0xc0), not to a
  model. A ragdoll's island gets the world's 8 / 2, as ours does.

## 3. Why a pile stays awake (measured, rubikon/tests/Probe --pile, PILE_SLEEP=100)

20 ragdolls on one ze_dark_souls spawn rest by tick ~1,300, but 1-3 light parts (3 kg, lying on other ragdolls'
parts, no mesh contact) keep a solved velocity of ~1-1.5 u/s while moving ~0.05 u/s: each tick gravity sinks them,
the 8 velocity iterations leave that much of it, the position solve pushes them back out. Above 0.4 u/s, they hold
the one island awake for good, and twice in 3,000 ticks the whole pile shifts. With the same solver, iterations and
sleep test, CS2's pile behaves the same: the cost is CS2's, not a port difference.

## 4. CS2's server rule: CRagdollProp's settle think

Convars (registered 1801035d0..1801037bc, flags 0x2000):

| convar | default | help |
|---|---|---|
| ragdoll_prop_settle | 1 | "Enable more aggressive ragdoll settling" |
| ragdoll_prop_sleepaftertime | 4.0 | "After this many seconds of being basically stationary, the ragdoll will go to sleep." |
| ragdoll_prop_sleepdisabletime | 1.5 | "Ragdoll is not allowed to physically sleep until this timer has elapsed." |
| ragdoll_scale_sleep_tolerance | 1 | (none) |

- The think table 0x1806af9a0: "CRagdollPropSettleThink" -> **180e95f00**: all parts asleep (180f85850, stored at
  +0xb3c) ends it; else +0xbd8's vfn 8, the settle 180e6f920, and the next think at now + 0.1 (0x3dcccccd).
- **180e6f920** (only when CRagdollProp +0x360 bit 17 is clear and ragdoll_prop_settle):
  - now = gpGlobals time (180927cb0); since = now - +0xb70 (the last time the origin moved), age = now - +0xb6c (spawn).
  - The physics object (+0x270 vfn 0x68, +0x200): since >= sleepdisabletime: its vfn 0x168(1.5, 1); else
    vfn 0x168(1.5, 0) and nothing more (sleep held off).
  - tolerance = 2 age clamped to [2, 20]; ragdoll_scale_sleep_tolerance: times max(0, the smallest part's vfn 0x418
    (its scale) and 1).
  - d = abs origin (1803d6f50) - +0xb60: any |d_i| > tolerance: +0xb70 = now, +0xb60 = origin, return.
  - since >= sleepaftertime: every part (+0xa98, stride 0x30, count +0xa90) gets vfn 0x3f8, then +0xb3c = all asleep.
- vphysics2 CPhysicsBody vtable 0x1803f44e0: slot 125 (0x1800131a0) sets +0x249 bit 1 (and wakes when cleared on a
  dynamic body), 126 (0x1800131e0) reads bit 1, **127 (0x1800131f0) Sleep -> CRnBody 1801be010** (rubikon
  StepGlue.SleepBody), 128 (0x180013200) Wake -> 1801c0ff0 (ContactLifecycle.Wake), 129 (0x180013210) asleep: +0x249
  bit 2.

## 5. As ported on the death ragdolls (RagdollSettle.cs)

The think and 180e6f920 as above, on rubikon's world clock, per live ragdoll. Not CS2's, and why:
- **The sleep acts on a group**: a ragdoll that passes the test sleeps only together with every dynamic body it
  touches (touching contacts, joints), and only when each of those is asleep or part of a ragdoll that passed too.
  Putting one ragdoll of a pile to sleep alone (CS2's per-ragdoll call) gets it woken by its awake neighbours on the
  next step and kicks the pile (measured: 311 of 312 awake at 3,000 ticks, more shifts than without).
- The origin is the heaviest part's frame (stand-in for the root element's: the pelvis in every model here).
- The sleep-disable half (vfn 0x168) is left out: CS2's client ragdolls may sleep on their own from the start.
- A settled ragdoll something wakes (a hit, a mover) starts settling again from that moment (the server restarting its
  think is untraced).

Unread: what vfn 0x168 does in vphysics2 (CPhysAggregateInstance), +0xbd8's vfn 8, and when the server restarts the
settle think after a wake.
