# Rubikon: breaking joints, and their break limits

How vphysics2 breaks a joint, and where a joint's break limit comes from. Ported in rubikon/src/Simulation/RnWorld.cs
(the step's break pass, `SetJointEnabled`), JointSolver.cs (`RnJoint.OnBreak`, `ClearImpulses`), CollisionFilter.cs /
BroadphaseShape.cs (the pair filter reading the joint's flags live). Addresses are **vphysics2_20260924.dll** (image base
0x180000000) unless a line says client_20261015.dll. The break test itself (CRnJoint_ShouldBreak 180205b40, vtable
+0x38, in the last velocity iteration: 18030f860 whole, 18030f500 chunked) was ported before; docs/game/rubikon-colour-joints.md
has the chunked workers.

## The step's break pass

CRnWorld::Step (180200840; source2-compiler's Vphysics2World.StepPhased drives the same calls) after the continuous
pass (1801ffe80) and before the world bounds clamp (1801faf80): for each joint in the broken list (world +0xa28, count
+0xa4c, filled by FUN_1801f0ef0 from the break tests in solve order), **FUN_1802044c0**, then the count zeroed.

- **FUN_1802044c0** (the break): if joint +0xb8 or +0xc0 is set, call +0xc0(+0xb8, +0xc8): the break callback (an
  object, a function, an argument); then FUN_1802058c0(joint, 0).
- The port: `RnJoint.OnBreak` (an `Action<RnJoint>`) stands for +0xb8 / +0xc0 / +0xc8.

## CRnJoint::SetEnabled (FUN_1802058c0)

`(joint, enable)`. Nothing when the joint already is so (`(~flags & 1) == enable`, flags at +0x28) or misses a body
(+0x18 body 1, +0x20 body 2). The disable half (ported, `RnWorld.SetJointEnabled(j, false)`):

1. **FUN_180205f60** (the joint still enabled): for body 1 then body 2, a dynamic one (body +0x54 == 2) is woken,
   **FUN_1801c0ff0(body, 0)** (the wake without the sleep timer reset: ContactLifecycle.Wake(w, b, false)).
2. Unless the joint lets its bodies collide (+0x28 bit 1): one body's shapes are marked for the pre-step query, so the
   pair finds its contacts again. The body: body 2 when body 1 is static (+0x54 == 0) and body 2 is not; body 1 when
   body 2 is static and body 1 is not; otherwise body 1 unless body 2 has fewer shapes (`cmp [A+0x60], [B+0x60]; cmovg`).
   For each of its shapes (count +0x60; the array +0x68, inline when the capacity at +0x64 & 0x7fffffff is 1, else
   the pointer there), **FUN_1802d6c90(world +0x110, shape +0x1c)** (Broadphase.Touch on the shape's proxy).
3. +0x28 |= 1 (disabled).
4. vtable **+0x58**: the impulses stored as zero (plain stores, not a scale: a -0 or a NaN does not survive).
   CRnConicalJoint (vtable 0x1803e0a70): **FUN_18022aac0**, +0x128..+0x14b (motor, twist low / high, swing, linear).
   CRnRevoluteJoint (0x1803e07e8): **FUN_180217360**, +0x10c..+0x12b (motor, low, high, the two hinge rows, linear).
   Slot +0x50 is the same function in both.
5. **FUN_1801e4000(world +0x118, joint)** (the island manager's joint update: IslandManagerOps.UpdateJoint): a joint
   in the world (+8 != -1), of a type other than 0 (+0xc), enabled, both bodies in the manager (+0x45 != 3), one of
   them dynamic, is an island edge (+0x41); otherwise it is taken out (FUN_1802cd5b0).

The enable half (FUN_1801fe0b0 for a joint that disables collision, the bit cleared, FUN_180205f60, vtable +0x50) is
not ported: nothing in the game enables a joint.

The pair filter (FUN_1801bdea0, CollisionFilter.BodiesMayCollide) walks the body's joint list (body +0x70) and reads
each joint's +0x28 as it stands, so a broken joint no longer keeps its bodies apart. The port's broadphase list held a
copy of the flags taken at AddJoint; it holds the joint now.

## The break limits (joint +0xac, +0xb0)

- The creators copy them from the creation desc: FUN_18005d370 (conical) at 18005d65e: `if (desc +0x64 > 0 || desc
  +0x68 > 0) { joint +0xac = desc +0x64; joint +0xb0 = desc +0x68 }`, then joint +0xc0 = desc +0x78, +0xb8 = desc +0x70
  (the callback). The other creators do the same (stores at 18005c9ef, 18005cdd8, 18005d1d6, 18005da13, 18005e0f2).
- A model's joints (a ragdoll: FUN_180047600 from the aggregate's VPhysXJoint_t) fill the desc from the record:
  VPhysXJoint_t +0xac (m_flFriction) and +0xb0 (m_flElasticity) go to desc +0x58 / +0x5c (one 8-byte copy), +0xb8
  (m_flPlasticity) to desc +0x60 (its upper half, desc +0x64, zeroed with it), +0xb4 (m_flElasticDamping) to the
  type's own part of the desc; desc +0x64 / +0x68 / +0x70 / +0x78 stay zero. VPhysXJoint_t has no break field (its
  m_flMaxForce +0x6c and m_flMaxTorque +0x98 are the motors'; tools/re/game/schema.py --near 0x18044aeb0 lists the class).
- The wrappers' setters: CPhysicsJoint (vtable 0x1803f62a0) slot 0x1a0 (18001c350: +0xac = xmm1) and slot 0x1b0
  (18001c3c0: +0xb0 = xmm1); getters 18001c360 / 18001c3d0.
- client_20261015.dll calls slot 0x1a0 / 0x1b0 nowhere in the ragdoll's code (a scan of every `call [reg + 0x1a0 /
  0x1b0]` from 0x180940000 to 0x180970000 and 0x180c60000 to 0x180ca0000 finds two, 18095af85 in the creation 18095acd0 and
  180956138, both on a body's vtable, not a joint's).

So **a CS2 death ragdoll's joints have break limits 0 and never break**; GameWorld.Ragdoll.cs leaves them 0. A joint
with a limit (a map's constraint entity, which the game does not build yet) breaks as above.

## The port's pool

GameWorld keeps retired ragdolls to reuse (no body removal in the port). A ragdoll with a disabled joint is not pooled
(CS2 builds each one anew; the enable half is not ported), so a broken ragdoll is never handed out again.

## Checked

- rubikon/tests/ColourJointOracle (`dotnet run -c Release -- <binaries> 3000`): vtable +0x58 (both types) against
  RnJoint.ClearImpulses on 3000 random joints with -0 and NaN impulses: every byte equal.
- rubikon/tests/Probe `--ragdoll-break <map physics.bin> <ragdolls.bin> <ragdolls.json> ctm_sas -2836 -4708 -20 200
  <linear> [angular]` on ze_dark_souls: limits of 1e6 break nothing; 60, 5, 400 + 3 break all 14 joints (ticks 3 and
  11); 2000 breaks 12; 1e5 + 40 breaks the 2 revolute ones (a conical joint's angular impulse, vtable +0x10, is 0). Each
  broken joint ran its callback once, is out of its island and holds zero impulses; the next spawn of that model is
  whole and not the broken one.

## Not read

- FUN_1801f0ef0 (the broken list's add) beyond its call; the list's order follows the threads in a chunked job.
- The enable half's FUN_1801fe0b0 (the bodies' contacts destroyed) for a joint enabled again.
