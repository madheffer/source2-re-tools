# A player's death ragdoll

Read 2026-11-16, session "predict-hit-fx". server_20261105.dll (image base 0x180000000), client_20261015.dll (ReVa;
the same functions in 1105 where named), vphysics2 through source2-compiler's port (src/Source2.Compiler/Maps/
SettleWorld.Aggregate.cs, capture-checked against resourcecompiler's aggregate build and vphysics2's solver).
The port: bake/RagdollBake.cs (`lasers-bake --ragdolls`), rubikon/src/Game/GameWorld.Ragdoll.cs (+ PhysicsApi /
wasm WorldApi), web/src/world/ragdoll-world.js, body-ragdoll.js, web/src/cs2web/client/fx/ragdolls.js,
web/src/cs2web/player/ragdoll-force.js, the server's `rag` event (web/server/cs2web/core/game.js kill).

## 1. The server: the pawn's ragdoll fields (CCSPlayerPawn)

| field | server | client | what |
|---|---|---|---|
| m_nRagdollDamageBone | +0x1004 | +0x1d24 | the hit's trace bone (CGameTrace +0xb8, short; -1 without a trace) |
| m_vRagdollDamageForce | +0x1008 | +0x1d28 | the damage info's force (+8) |
| m_szRagdollDamageWeaponName | +0x1014 (64 chars) | +0x1d34 | player_death's "weapon" |
| m_bRagdollDamageHeadshot | +0x1054 | +0x1d74 | an attacker and the info's 0x80000 (DMG headshot) |
| m_vRagdollServerOrigin | +0x1058 | +0x1d78 | the pawn's abs origin at the death |
| m_bClientSideRagdoll | +0x334 (CBaseAnimGraph) | +0x3e6 | the ragdoll's switch |

- **18024a860 SetRagdoll(pawn, on, bone, force*, ?, weapon, headshot)**: on -> 180ae28e0, 180b69b80 (m_bClientSideRagdoll
  on), the four fields set (each with its NetworkStateChanged); off -> 180ae27b0, 180b69bc0, m_vRagdollServerOrigin 0.
- **1802064f0** (on) from **18091da70** (CCSGameRules' player_death build, after the event's fields): bone = the info's
  trace +0xb8 (-1 none), force = info +8..+0x10, weapon = the event's "weapon", headshot = an attacker and info +0x4c
  bit 0x80000; then m_vRagdollServerOrigin = the abs origin (1803d6f50). 1802057d0 / 180249530 (the spawn) turn it off.
- The forces it carries:
  - a bullet: **180fc2430 CalculateBulletDamageForce(info, ammo, dir, pos, 1.0)**: dir normalized (1e-17 / 1e17
    bounds) x the ammo type's physics force (180b4bfa0) x phys_pushscale (18221ba70) x the scale; +0x14 = pos.
  - RadiusDamage (1809550b0, 180955c5c..): (the target's aim point - the source it was seen from) normalized x the
    info's force length x the scale; the HE / planted C4 fallback (sim/src/game/radius.rs `damage_dir_to`).
  - the bomb's shockwave (1809f72d0): (centre - bomb) normalized x dmg x 50 (c4-shockwave.md).
  - the knife: its swing's forward (CalculateMeleeDamageForce; the trace has no hitbox, so the bone is -1).
  - the hit group step (180a89430) scales the force by phys_playerscale (and phys_headshotscale on a head hit, 0 for a
    grenade's head hit); none of this reaches the client's ragdoll, which normalizes the force (section 3).

## 2. The client: the ragdoll's creation (C_CSPlayerPawn)

- m_bClientSideRagdoll's change callback **OnClientRagdollChanged** (bound at 18042c650) -> entity vfn 0x880; the pawn's
  data update reaches **180c97a60** (callers 180c901f0, 180c62a60): with no predicted ragdoll (+0x34e8 clear),
  18095bf90 (m_bRagdollClientSide, +0x1201) false -> an existing ragdoll is freed (1808e4b60, the physics world's vfn
  0x448 on m_pRagdollControl +0x11b0, 18095b260: back to animating); true and no ragdoll yet (+0x11a8) ->
  1808e4c90, **18095b0b0** (the creation), then 1809429a0 (the ragdoll, +0x11a8) non-null -> 180c8a620,
  **180c63540** (the push, section 3), **18095aac0** (applied), +0x34ec = the push's direction (180226380), 180211750
  (the entity's transform from the ragdoll); 180c9a6f0.
- **18095b0b0**: m_bRagdollEnabled (+0x1200) and the model's physics (vfn 0x70) -> the bone setup (180aa0f80(.., 0x40),
  the pose at +0x1c0) -> **18095acd0(pawn, skeleton, pose, current = +0x1c0, previous = +0x1c0, dt 1/64, origin)**:
  - the physics world's **vfn 0x428 (CreateRagdoll)**(model, pose, motion 2, current, previous, entity, collision group,
    dt) into +0x11a8: the model's aggregate at the pose the bones stand in. Current and previous are the same bone set,
    so no part gets a velocity from them.
  - 18095bfa0 when a cvar (182538578) is set; 18092f070 registers the entity.
  - then, unless ragdoll_gravity_scale and ragdoll_friction_scale are both 1 (they are not: 1.0 and 0.6), every part:
    vfn 0x410 (gravity scale) = ragdoll_gravity_scale; the linear velocity (vfn 0x210 + the pawn's velocity at +0x1ef0
    +0x18) set (vfn 0x200, 180012580); the part's frame (vfn 0x1b0) + 180c7c1a0's offset (the local player's own
    pawn only: m_vRagdollServerOrigin less its predicted origin; zero for anyone else) set back (vfn 0x1a8); every
    shape's material (vfn 0x30 / 0x28) friction x ragdoll_friction_scale.
- The aggregate (vphysics2's CPhysAggregateInstance, 180042ba0): source2-compiler's port, capture-exact on ctm_sas:
  each part at its bind pose (180045630: the column scales, MatrixQuaternion 18125de90 of the unscaled matrix),
  keyframed and woken, its shapes (spheres, capsules, hulls) with the layered attributes (180256c80 / 180256d00), SetMass
  (1e6 cap, 500 when not positive), the inertia scale above 1, damping and drag; the joints (180047600): VPhysXJoint_t
  type 4 / 10 CRnConicalJoint (18005d370), 3 CRnRevoluteJoint (18005cb80), the frames normalized, frequency 0, the
  elastic damping, friction as a mode-1 motor with FrictionTorque (180204d70: radius x ((|g| m) friction)), the swing /
  twist limits through the degree round trip. Every CS2 player model's joints are types 4 and 3, all with friction, no
  motors, world joints or elastic joints (bake/RagdollBake.cs lists them: 22 models, 15 parts / 14 joints for the
  agents, 26 / 24 for classic_zombie).
- CS2's player anim graphs have no ragdoll nodes (pak01's worldmodel / player / agent .vnmgraph: no "Ragdoll"), so a
  player's ragdoll has no pose control (CRagdollPoseControlSystem, m_pRagdollControl's powered motors are for graphs
  that drive one): it is the passive aggregate above.

## 3. The push (client 180c63540, then 18095aac0)

- Weapon name empty: the force as it came. Else the force normalized (18015a140) x a magnitude:
  hegrenade 45000, planted_c4 100000, taser 1; ak47 / aug / famas / galilar / m249 / m4a1 / m4a1_silencer(_off) / negev /
  sg556 / ssg08 38000 (headshot 28000); awp / g3sg1 / scar20 40000 (30000); bizon / mp9 / mp5sd / mac10 / mp7 / p90 /
  ump45 / cz75a / elite / fiveseven / glock / p250 / usp_silencer(_off) / tec9 / hkp2000 20000 (25000); deagle /
  revolver 23000 (28000); mag7 / nova / xm1014 / sawedoff 60000 (27000); any name containing "knife" (V_stristr_fast)
  20000 (25000); anything else 1000. (ragdoll-force.js)
- **18095aac0(pawn, bone, force)**: the ragdoll's bone -> part map (vfn 0x90); a bone without a part walks its parents
  (181776230) until one has; none (or bone -1) -> part 0. ApplyLinearImpulse (vfn 0x250, 180012860: v += J / m) of the
  force on that part's body; then the aggregate's mass (vfn 0xb0) > 0 -> every other dynamic part (vfn 0x20 == 2) gets
  force x (its mass, vfn 0x128 / the total).

## 4. Its end, and the predicted kill's (damage-prediction.md 8)

- 180c97a60 (m_bRagdollClientSide off: the respawn) and 180c8c070 (a predicted ragdoll whose health came back) free it.
- cl_ragdoll_limit 20 ("Maximum number of ragdolls to show", CRagdollLRURetirement: the oldest goes), g_ragdoll_maxcount
  5 / g_ragdoll_important_maxcount 2 (prop_ragdoll's), g_ragdoll_fadespeed 600, g_ragdoll_lvfadespeed 100,
  cl_disable_ragdolls 0, ragdoll_resolve_initial_conflict 1, ragdoll_resolve_separation 1, cl_ragdoll_default_scale 1.0,
  ragdoll_impact_strength 500 (client cvardefs + 1800b6750 / 1800c58d0).

## 5. A ragdoll left standing: the nudge (read 2026-11-16, session "own-ragdoll-nudge")

The cvars (registered 1800b00f0 / 1800b0190 / 1800b0230 / 1800b02d0, flags 0x2002, ConVar objects 0x1825328b0 /
0x1825328a0 / 0x182532890 / 0x182532880; the value at the object's +8 pointer, +0x58):

| cvar | default | bits |
|---|---|---|
| dev_cs_ragdoll_progress_check_interval | 0.25 | 0x3e800000 |
| dev_cs_ragdoll_nudge_max_duration | 1.5 | 0x3fc00000 |
| dev_cs_ragdoll_nudge_intensity | 500 | 0x43fa0000 |
| dev_cs_ragdoll_head_ankle_delta_z_threshold | 35 | 0x420c0000 |

The pawn's fields (client C_CSPlayerPawn): +0x1d8c the next check time, +0x1d90 the nudge's end (-1 none), +0x1d94 the
head's last z, +0x1d98 the head part, +0x1d9c the left ankle part, +0x1da0 the right ankle part (-1 each none), +0x34ec
the push's direction. curtime is PTR_DAT_182230090 +0x30.

- **180c8a620 LatchRagdollStandingContext(pawn)**, from 180c97a60 right after the ragdoll's creation (and the predicted
  kill 180c70920), before the push: the parts -1; the bone "ValveBiped.Bip01_Head", else "head_0" (180952940 -> 180abb430:
  the skeleton's lookup by MurmurHash2 of the lower-cased name, seed 0x31415926 (1801665b0), so case-insensitive); none ->
  next check FLT_MAX, end -1, DevWarning. Head part = the ragdoll's bone -> part map (vfn 0x90; no walk to a parent: a bone
  without its own part is -1); next check FLT_MAX, end -1; with a head part: its body's position (vfn 0x20(part) -> body
  vfn 0x190) z into +0x1d94; "ankle_L" -> its part (missing bone: DevWarning, return), "ankle_R" likewise; next check =
  curtime + the interval (180160b10 reads the cvar).
- 180c97a60 then: the push (180c63540), 18095aac0, **+0x34ec = 180226380(push)**: the push copied and normalized
  (18015a140; zero stays zero).
- **180c8a560 IsRagdollStillStanding(pawn)**: head part < 0 or right ankle part < 0 -> false (DevWarning); else
  |head body z - right ankle body z| > the threshold (COMISS / SETA: strictly greater).
- **180c8e230** (from **180c67e80**, the pawn's think, via 180caf090; the same function holds CS:GO's
  C_CSPlayer::ClientThink deathmatch notices, so it is read as every client frame: the rate is unconfirmed): with the
  ragdoll on (18095bf90) or predicted (+0x34e8), a ragdoll (+0x11a8) and **standing** (else nothing at all):
  1. curtime >= the next check: next check = curtime + interval; no head part -> FLT_MAX, return. The head's z moved more
     than 1 from +0x1d94 -> keep the new z, return (still falling). Else next check FLT_MAX (never again), end = curtime
     + max_duration.
  2. curtime <= end: not standing (180c8a560 again) -> end -1, return. Else F = -(+0x34ec) x intensity, and
     18095aac0(pawn, the part's bone (vfn 0x88: part -> bone), F) for the left ankle part, then the right (each >= 0):
     the impulse on that part, the rest of the body by mass (section 3).
- Note: every agent model has ankle_l / ankle_r parts (the parts 13 / 14 of 15), so the nudge reaches every player model.

The port: src/cs2web/player/ragdoll-nudge.js (latchStanding / nudgeStanding, ragdoll-nudge-test.mjs), driven from
client/fx/ragdolls.js frame() on the ragdoll's newest physics frame (the bodies as the last step left them, vfn 0x190);
the impulses go to the ragdolls' world before its next step (replica `ragdollPush` -> worker `ragpush` ->
RagdollSim.push -> RagdollForce). curtime: the page's clock (performance.now), the intervals being relative.

## 6. Your own pawn's ragdoll

180c97a60 makes the local player's ragdoll as anyone's (it is the same pawn data update); the one difference is
**180c7c1a0** (called on every part's frame in 18095acd0): only for the local player's own pawn (18096a8f0(0) and the
observer checks), when m_vRagdollServerOrigin (+0x1d78) is not zero: d = server origin - the pawn's abs origin
(180219a80); |d| >= 1 -> d is added to each part's frame, else zero. The port: client/fx/ragdolls.js died() takes
own-body.js's body (your first-person legs body: its graph kept running while you live, culled at 15 Hz when the
legs aren't drawn, so the pose is yours at the death), d from the event's `o` less where the body stands, your
prediction's velocity; body-ragdoll.js enterRagdoll turns the legs warp (fade 0) and pass off; game.js ownFrame draws it.

## The port

- The data: `lasers-bake --ragdolls web/public/ze-players [--pack <GFL .vpk>] [--out <dir>]` -> ze-players/ragdolls.bin
  (a physics.bin of the player models: RubikonBake.Model, the same reader as the maps') + ragdolls.json (each part's
  bone, every joint's fields).
- rubikon GameWorld.Ragdoll.cs: Build = CreateAggregate / CreateJoints / FrictionTorque as source2-compiler's; then
  SetTransform to the pose, SetType 2 (MakeDynamic), gravity scale, the friction scale on every shape, the pawn's
  velocity (AddVelocity: the body starts still, so vfn 0x200 with 0x210's + v is the same); RagdollForce = 18095aac0.
  The native probe (`rubikon-probe --ragdoll`, tests/Probe/Ragdoll.cs): ctm_sas dropped on de_dust2 folds onto the floor,
  sleeps after ~250 ticks, its joints' anchors within 0.006 u.
- The world: a world of its own on the client (the map's static world from the same physics.bin, made 48 shapes a tick;
  the round's brush and physbox bodies mirrored keyframed each tick), stepped a tick with each of the replica's on the
  replica's thread (the worker): CS2's client physics world never reaches the server, so the ragdoll never enters the
  round's lockstep replica.
- OURS (rubikon has no body removal): a retired ragdoll's bodies go static and touch nothing and are kept per model;
  the next ragdoll of that model takes them (posed, attributes back, SetType 2 zeroing the joints' impulses as a new
  joint's are); a mover's mirror is kept per entity id and model. Memory stays at the live ragdolls' count.
- The body: body-ragdoll.js reads each part bone's world frame from the body as drawn (its bones, or the worker's
  skinning matrices x the bind; a bone no drawn skeleton has from its parent's by its own local matrix), then draws
  the part bones from the ragdoll (interpolated between its last two ticks) and every other bone by the local
  transform it had at the death.

Unread: the physics world's vfn 0x428 body (which aggregate path; read as vphysics2's aggregate build with the pose);
how often 180c67e80 (the pawn's think) runs: its SetNextClientThink (section 5 assumes every frame); a capture of a CS2 death's ragdoll to compare
against (the solver and the aggregate are exact, the whole has not been compared).
