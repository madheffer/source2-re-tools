# Rubikon: breaking joints, and their break limits

vphysics2_20260924 (image base 0x180000000) unless marked client_20261015. Chunked break workers: rubikon-colour-joints.md.

## Functions

| Address | Module | What |
|---|---|---|
| 180205b40 | vphysics2 | CRnJoint_ShouldBreak (vtable +0x38), in the last velocity iteration |
| 18030f860 / 18030f500 | vphysics2 | last velocity iteration: whole / chunked |
| 180200840 | vphysics2 | CRnWorld::Step |
| 1801ffe80 | vphysics2 | continuous pass (before the break pass) |
| 1801faf80 | vphysics2 | world bounds clamp (after the break pass) |
| 1801f0ef0 | vphysics2 | adds to the broken list (from the break tests, solve order) |
| 1802044c0 | vphysics2 | the break: callback, then SetEnabled(joint, 0) |
| 1802058c0 | vphysics2 | CRnJoint::SetEnabled(joint, enable) |
| 180205f60 | vphysics2 | wake both dynamic bodies |
| 1801c0ff0 | vphysics2 | wake(body, 0): no sleep timer reset |
| 1802d6c90 | vphysics2 | broadphase touch (world +0x110, shape +0x1c) |
| 18022aac0 | vphysics2 | CRnConicalJoint vtable +0x58: zero +0x128..+0x14b (motor, twist low / high, swing, linear) |
| 180217360 | vphysics2 | CRnRevoluteJoint vtable +0x58: zero +0x10c..+0x12b (motor, low, high, two hinge rows, linear) |
| 1801e4000 | vphysics2 | island manager joint update (world +0x118, joint) |
| 1802cd5b0 | vphysics2 | take a joint out of the islands |
| 1801fe0b0 | vphysics2 | enable half for a joint that disables collision (contacts destroyed) |
| 1801bdea0 | vphysics2 | pair filter: walks body +0x70's joints, reads +0x28 live |
| 18005d370 | vphysics2 | conical creator (break limits at 18005d65e) |
| 18005c9ef, 18005cdd8, 18005d1d6, 18005da13, 18005e0f2 | vphysics2 | the other creators' break-limit stores |
| 180047600 | vphysics2 | model joints (ragdoll) desc from VPhysXJoint_t |
| 18001c350 / 18001c360 | vphysics2 | CPhysicsJoint slot 0x1a0 set +0xac (xmm1) / getter |
| 18001c3c0 / 18001c3d0 | vphysics2 | CPhysicsJoint slot 0x1b0 set +0xb0 (xmm1) / getter |
| 0x18044aeb0 | vphysics2 | near VPhysXJoint_t's schema class |
| 18095acd0 / 18095af85, 180956138 | client | the only `call [reg+0x1a0/0x1b0]` in the ragdoll ranges: on a body's vtable, not a joint's |

## Fields

| Offset | Field |
|---|---|
| world +0xa28 / +0xa4c | broken list / count |
| world +0x110 | broadphase |
| world +0x118 | island manager |
| joint +8 | in world (!= -1) |
| joint +0xc | type (0 = none) |
| joint +0x18 / +0x20 | body 1 / body 2 |
| joint +0x28 | flags: bit 0 disabled, bit 1 bodies collide |
| joint +0x41 | island edge |
| joint +0xac / +0xb0 | break limits (linear / angular) |
| joint +0xb8 / +0xc0 / +0xc8 | break callback: object, function, argument |
| body +0x45 | manager state (3 = not in) |
| body +0x54 | type: 0 static, 2 dynamic |
| body +0x60 / +0x64 / +0x68 | shape count / capacity (& 0x7fffffff; 1 = inline) / array |
| body +0x70 | joint list |
| shape +0x1c | broadphase proxy |
| desc +0x58 / +0x5c / +0x60 | VPhysXJoint_t +0xac m_flFriction / +0xb0 m_flElasticity (one 8-byte copy) / +0xb8 m_flPlasticity |
| desc +0x64 / +0x68 | break limits (+0x64 zeroed with +0x60's copy) |
| desc +0x70 / +0x78 | callback -> joint +0xb8 / +0xc0 |
| VPhysXJoint_t +0xb4 | m_flElasticDamping (to the type's own desc part) |
| VPhysXJoint_t +0x6c / +0x98 | m_flMaxForce / m_flMaxTorque (motors; no break field) |

## Constants

| Value | What |
|---|---|
| 0x1803e0a70 | CRnConicalJoint vtable |
| 0x1803e07e8 | CRnRevoluteJoint vtable |
| 0x1803f62a0 | CPhysicsJoint vtable |
| client 0x180940000..0x180970000, 0x180c60000..0x180ca0000 | ranges scanned for slot 0x1a0 / 0x1b0 calls |

## Break pass (CRnWorld::Step)

After 1801ffe80, before 1801faf80: for each joint in the broken list, 1802044c0; count zeroed.
1802044c0: if joint +0xb8 or +0xc0 set, call `+0xc0(+0xb8, +0xc8)`; then 1802058c0(joint, 0).

## SetEnabled(joint, enable)

Nothing when already so (`(~flags & 1) == enable`) or a body is missing. Disable:

1. 180205f60: body 1 then body 2, each dynamic one woken by 1801c0ff0(body, 0).
2. Unless +0x28 bit 1: one body's shapes are broadphase-touched (1802d6c90) so the pair finds contacts again. Body 2
   when body 1 static and body 2 not; body 1 when body 2 static and body 1 not; otherwise body 1 unless body 2 has fewer
   shapes (`cmp [A+0x60], [B+0x60]; cmovg`).
3. +0x28 |= 1.
4. vtable +0x58: impulses stored as zero (plain stores: a -0 or NaN does not survive). Slot +0x50 is the same function
   in both types.
5. 1801e4000: a joint in the world, type != 0, enabled, both bodies in the manager, one dynamic, is an island edge
   (+0x41); otherwise taken out (1802cd5b0).

Enable: 1801fe0b0 (for a joint disabling collision), the bit cleared, 180205f60, vtable +0x50. Nothing in the game
enables a joint.

## Break limits

- Creators: `if (desc +0x64 > 0 || desc +0x68 > 0) { joint +0xac = desc +0x64; joint +0xb0 = desc +0x68 }`, then
  joint +0xc0 = desc +0x78, +0xb8 = desc +0x70.
- Ragdoll joints (180047600): desc +0x64 / +0x68 / +0x70 / +0x78 stay zero. The client never calls the setters on a
  joint, so **a CS2 death ragdoll's joints have limits 0 and never break**.
- Probe on ze_dark_souls (ctm_sas -2836 -4708 -20 200): limits 1e6 break nothing; 60, 5, 400 + 3 break all 14 joints
  (ticks 3 and 11); 2000 breaks 12; 1e5 + 40 breaks the 2 revolute ones (a conical joint's angular impulse, vtable
  +0x10, is 0).

## Unread

- 1801f0ef0 beyond its call; the list's order follows the threads in a chunked job.
- 1801fe0b0 (contacts destroyed) for a joint enabled again.
