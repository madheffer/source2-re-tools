# A player's death ragdoll

server_20261105 (image base 0x180000000), client_20261015 (ReVa; the same functions in 1105 where named); vphysics2
through source2-compiler's port (src/Source2.Compiler/Maps/SettleWorld.Aggregate.cs, capture-checked against
resourcecompiler's aggregate build and vphysics2's solver).

## Functions

| Address | Module | What |
|---|---|---|
| 18024a860 | server | SetRagdoll(pawn, on, bone, force*, ?, weapon, headshot) |
| 180ae28e0 / 180ae27b0 | server | on / off step |
| 180b69b80 / 180b69bc0 | server | m_bClientSideRagdoll on / off |
| 1802064f0 | server | ragdoll on, from 18091da70 (CCSGameRules' player_death build, after the event's fields) |
| 1803d6f50 | server | abs origin |
| 1802057d0 / 180249530 | server | turn it off (the spawn) |
| 180fc2430 | server | CalculateBulletDamageForce(info, ammo, dir, pos, 1.0) |
| 180b4bfa0 | server | the ammo type's physics force |
| 1809550b0 | server | RadiusDamage (force at 180955c5c..) |
| 1809f72d0 | server | the bomb's shockwave ([c4-shockwave.md](c4-shockwave.md)) |
| 180a89430 | server | hit group step (phys_playerscale, phys_headshotscale) |
| 18042c650 | client | binds OnClientRagdollChanged (-> entity vfn 0x880) |
| 180c97a60 | client | the pawn's data update: ragdoll create / free (callers 180c901f0, 180c62a60) |
| 18095bf90 | client | m_bRagdollClientSide (+0x1201) |
| 1808e4b60 | client | free the ragdoll |
| 18095b260 | client | back to animating |
| 1808e4c90 | client | before the creation |
| 18095b0b0 | client | the creation |
| 1809429a0 | client | the ragdoll (+0x11a8) |
| 180c8a620 | client | LatchRagdollStandingContext(pawn) |
| 180c63540 | client | the push magnitude |
| 18095aac0 | client | apply (pawn, bone, force) |
| 180226380 | client | copy + normalize (zero stays zero) |
| 180211750 | client | entity transform from the ragdoll |
| 180c9a6f0 | client | after the creation |
| 180aa0f80 | client | bone setup (.., 0x40) |
| 18095acd0 | client | (pawn, skeleton, pose, current, previous, dt 1/64, origin): create + per-part setup |
| 18095bfa0 | client | when cvar 182538578 is set |
| 18092f070 | client | registers the entity |
| 180012580 | client | set linear velocity (vfn 0x200) |
| 180c7c1a0 | client | own pawn's part offset |
| 18096a8f0 | client | (0): local player check |
| 180219a80 | client | pawn's abs origin |
| 18015a140 | client | normalize |
| 181776230 | client | bone parent walk |
| 180012860 | client | ApplyLinearImpulse (vfn 0x250): v += J / m |
| 180c8c070 | client | frees a predicted ragdoll whose health came back |
| 180c70920 | client | the predicted kill ([damage-prediction.md](damage-prediction.md) 8) |
| 180952940 -> 180abb430 | client | skeleton bone lookup by MurmurHash2 (lower-cased, seed 0x31415926 via 1801665b0) |
| 180160b10 | client | cvar read (the interval) |
| 180c8a560 | client | IsRagdollStillStanding(pawn) |
| 180c8e230 | client | the nudge (from 180c67e80, the pawn's think, via 180caf090) |
| 1800b6750 / 1800c58d0 | client | ragdoll cvar registrations |
| 1800b00f0 / 1800b0190 / 1800b0230 / 1800b02d0 | client | nudge cvar registrations |
| 180042ba0 | vphysics2 | CPhysAggregateInstance build |
| 180045630 | vphysics2 | part bind pose (column scales, MatrixQuaternion 18125de90 of the unscaled matrix) |
| 180256c80 / 180256d00 | vphysics2 | layered shape attributes |
| 180047600 | vphysics2 | joints |
| 18005d370 | vphysics2 | CRnConicalJoint (types 4 / 10) |
| 18005cb80 | vphysics2 | CRnRevoluteJoint (type 3) |
| 180204d70 | vphysics2 | FrictionTorque: `radius * ((|g| m) friction)` |

## Fields

| Field | Server | Client | What |
|---|---|---|---|
| m_nRagdollDamageBone | +0x1004 | +0x1d24 | the hit's trace bone (CGameTrace +0xb8, short; -1 without a trace) |
| m_vRagdollDamageForce | +0x1008 | +0x1d28 | the damage info's force (+8) |
| m_szRagdollDamageWeaponName | +0x1014 (64 chars) | +0x1d34 | player_death's "weapon" |
| m_bRagdollDamageHeadshot | +0x1054 | +0x1d74 | an attacker and the info's 0x80000 (DMG headshot) |
| m_vRagdollServerOrigin | +0x1058 | +0x1d78 | the pawn's abs origin at the death |
| m_bClientSideRagdoll | +0x334 (CBaseAnimGraph) | +0x3e6 | the ragdoll's switch |

| Offset (client pawn) | Field |
|---|---|
| +0x34e8 | predicted ragdoll |
| +0x1201 / +0x1200 | m_bRagdollClientSide / m_bRagdollEnabled |
| +0x11b0 | m_pRagdollControl |
| +0x11a8 | the ragdoll |
| +0x1c0 | the pose |
| +0x1ef0 +0x18 | the pawn's velocity |
| +0x34ec | the push's direction |
| +0x1d8c | next check time |
| +0x1d90 | nudge's end (-1 none) |
| +0x1d94 | head's last z |
| +0x1d98 / +0x1d9c / +0x1da0 | head / left ankle / right ankle part (-1 none) |
| PTR_DAT_182230090 +0x30 | curtime |
| info +0x4c | flags (0x80000 headshot) |

## Constants

| Value | What |
|---|---|
| phys_pushscale | 18221ba70 |
| 1e-17 / 1e17 | normalize bounds in CalculateBulletDamageForce |
| 50 | shockwave force factor: `(centre - bomb) normalized * dmg * 50` |
| ragdoll_gravity_scale / ragdoll_friction_scale | 1.0 / 0.6 |
| 1e6 / 500 | SetMass cap / mass when not positive |
| cl_ragdoll_limit | 20 ("Maximum number of ragdolls to show", CRagdollLRURetirement: the oldest goes) |
| g_ragdoll_maxcount / g_ragdoll_important_maxcount | 5 / 2 (prop_ragdoll's) |
| g_ragdoll_fadespeed / g_ragdoll_lvfadespeed | 600 / 100 |
| cl_disable_ragdolls | 0 |
| ragdoll_resolve_initial_conflict / ragdoll_resolve_separation | 1 / 1 |
| cl_ragdoll_default_scale | 1.0 |
| ragdoll_impact_strength | 500 |

Nudge cvars (flags 0x2002, value at the object's +8 pointer, +0x58):

| Cvar | Object | Default | Bits |
|---|---|---|---|
| dev_cs_ragdoll_progress_check_interval | 0x1825328b0 | 0.25 | 0x3e800000 |
| dev_cs_ragdoll_nudge_max_duration | 0x1825328a0 | 1.5 | 0x3fc00000 |
| dev_cs_ragdoll_nudge_intensity | 0x182532890 | 500 | 0x43fa0000 |
| dev_cs_ragdoll_head_ankle_delta_z_threshold | 0x182532880 | 35 | 0x420c0000 |

## The server

- SetRagdoll: on -> 180ae28e0, 180b69b80, the four fields set (each with NetworkStateChanged); off -> 180ae27b0,
  180b69bc0, m_vRagdollServerOrigin 0.
- 1802064f0: bone = info trace +0xb8 (-1 none), force = info +8..+0x10, weapon = the event's "weapon", headshot = an
  attacker and +0x4c bit 0x80000; then m_vRagdollServerOrigin = abs origin (1803d6f50).
- Forces:
  - bullet: 180fc2430: `dir normalized * ammo physics force (180b4bfa0) * phys_pushscale * scale`; +0x14 = pos.
  - RadiusDamage: `(target's aim point - the source it was seen from) normalized * info's force length * scale` (HE / planted C4).
  - bomb shockwave (1809f72d0): `(centre - bomb) normalized * dmg * 50`.
  - knife: its swing's forward (CalculateMeleeDamageForce; no hitbox in the trace, bone -1).
  - 180a89430 scales by phys_playerscale (and phys_headshotscale on a head hit, 0 for a grenade's head hit); none of this
    reaches the client's ragdoll, which normalizes the force.

## The creation (client)

1. OnClientRagdollChanged -> vfn 0x880; 180c97a60: no predicted ragdoll (+0x34e8 clear):
   - 18095bf90 false -> an existing ragdoll freed (1808e4b60, physics world vfn 0x448 on +0x11b0, 18095b260).
   - true and no ragdoll (+0x11a8) -> 1808e4c90, 18095b0b0; then 1809429a0 non-null -> 180c8a620, 180c63540,
     18095aac0, `+0x34ec = 180226380(push)`, 180211750; 180c9a6f0.
2. 18095b0b0: +0x1200 and the model's physics (vfn 0x70) -> 180aa0f80(.., 0x40) (pose at +0x1c0) -> 18095acd0(pawn,
   skeleton, pose, +0x1c0, +0x1c0, 1/64, origin).
3. 18095acd0:
   - physics world vfn 0x428 (CreateRagdoll)(model, pose, motion 2, current, previous, entity, collision group, dt)
     into +0x11a8: the model's aggregate at the bones' pose. Current and previous are the same set: no part velocity from them.
   - 18095bfa0 when cvar 182538578 is set; 18092f070.
   - Unless gravity and friction scales are both 1, every part: vfn 0x410 = ragdoll_gravity_scale; linear velocity
     (vfn 0x210 + pawn velocity +0x1ef0 +0x18) set (vfn 0x200, 180012580); frame (vfn 0x1b0) + 180c7c1a0's offset
     set back (vfn 0x1a8); every shape's material (vfn 0x30 / 0x28) friction x ragdoll_friction_scale.
4. 180c7c1a0 (own pawn only: 18096a8f0(0) and observer checks), +0x1d78 not zero: `d = server origin - abs origin`
   (180219a80); |d| >= 1 -> d added to each part's frame, else zero.

## The aggregate (180042ba0)

- Each part at its bind pose (180045630), keyframed and woken; shapes (spheres, capsules, hulls) with layered
  attributes (180256c80 / 180256d00); SetMass (1e6 cap, 500 when not positive); inertia scale above 1; damping and drag.
- Joints (180047600): VPhysXJoint_t type 4 / 10 CRnConicalJoint (18005d370), 3 CRnRevoluteJoint (18005cb80); frames
  normalized, frequency 0, elastic damping, friction as a mode-1 motor with FrictionTorque (180204d70); swing / twist
  limits through the degree round trip.
- Every CS2 player model's joints are types 4 and 3, all with friction, no motors, world joints or elastic joints
  (22 models; 15 parts / 14 joints for the agents, 26 / 24 for classic_zombie).
- The player anim graphs (pak01's worldmodel / player / agent .vnmgraph) have no "Ragdoll" nodes: no pose control
  (CRagdollPoseControlSystem); the ragdoll is the passive aggregate.

## The push (180c63540, 18095aac0)

Weapon name empty: the force as it came. Else `normalize(force) (18015a140) * magnitude`:

| Weapons | Magnitude (headshot) |
|---|---|
| hegrenade | 45000 |
| planted_c4 | 100000 |
| taser | 1 |
| ak47, aug, famas, galilar, m249, m4a1, m4a1_silencer(_off), negev, sg556, ssg08 | 38000 (28000) |
| awp, g3sg1, scar20 | 40000 (30000) |
| bizon, mp9, mp5sd, mac10, mp7, p90, ump45, cz75a, elite, fiveseven, glock, p250, usp_silencer(_off), tec9, hkp2000 | 20000 (25000) |
| deagle, revolver | 23000 (28000) |
| mag7, nova, xm1014, sawedoff | 60000 (27000) |
| any name containing "knife" (V_stristr_fast) | 20000 (25000) |
| anything else | 1000 |

18095aac0(pawn, bone, force): bone -> part (vfn 0x90); a bone without a part walks its parents (181776230); none (or
bone -1) -> part 0. ApplyLinearImpulse (vfn 0x250) of the force on that part; then aggregate mass (vfn 0xb0) > 0 ->
every other dynamic part (vfn 0x20 == 2) gets `force * (its mass (vfn 0x128) / the total)`.

## The end

180c97a60 (m_bRagdollClientSide off: the respawn) and 180c8c070 free it.

## The nudge (a ragdoll left standing)

- 180c8a620, from 180c97a60 right after the creation (and 180c70920), before the push:
  1. Parts -1; bone "ValveBiped.Bip01_Head", else "head_0" (180952940, case-insensitive); none -> next check FLT_MAX,
     end -1, DevWarning.
  2. Head part = bone -> part (vfn 0x90; no parent walk: -1 without its own part); next check FLT_MAX, end -1; with a
     head part: its body's position (vfn 0x20(part) -> body vfn 0x190) z into +0x1d94.
  3. "ankle_L" -> its part (missing bone: DevWarning, return), "ankle_R" likewise; next check = curtime + interval (180160b10).
- 180c8a560: head part < 0 or right ankle part < 0 -> false (DevWarning); else `|head z - right ankle z| > threshold`
  (COMISS / SETA: strictly greater).
- 180c8e230 (180c67e80's think via 180caf090; the same function holds CS:GO's C_CSPlayer::ClientThink deathmatch
  notices, read as every client frame: rate unconfirmed): ragdoll on (18095bf90) or predicted (+0x34e8), a ragdoll
  (+0x11a8) and **standing** (else nothing):
  1. curtime >= next check: next check = curtime + interval; no head part -> FLT_MAX, return. Head z moved more than 1
     from +0x1d94 -> keep the new z, return (still falling). Else next check FLT_MAX (never again), end = curtime + max_duration.
  2. curtime <= end: not standing (180c8a560) -> end -1, return. Else `F = -(+0x34ec) * intensity`, 18095aac0(pawn,
     part's bone (vfn 0x88), F) for the left ankle part, then the right (each >= 0).
- Every agent model has ankle_l / ankle_r parts (parts 13 / 14 of 15): the nudge reaches every player model.

## Unread

- Physics world vfn 0x428's body (which aggregate path; read as vphysics2's aggregate build with the pose).
- How often 180c67e80 runs (its SetNextClientThink; assumed every frame).
- No capture of a CS2 death's ragdoll compared as a whole (the solver and the aggregate are exact).
