# CS2's scene node: an entity's transform (RUST_PORT phase 4f, server.dll 2026-11-05)

Where an entity is and how it's turned: CGameSceneNode (each entity's m_pGameSceneNode), its local and absolute
transform, its parent. The step after the I/O (io-queue.md, io-targets.md): the entities' own state into the sim.
Addresses are server_20261105.dll (archived in tools/re/binaries); CGameSceneNode's vtable is 0x1819459f8 (RTTI).

## The node

- **The fields**: m_nodeToWorld, a CTransform at +0x10 (position +0x10, scale +0x1c, quaternion xyzw +0x20); the owner
  entity +0x30; the parent node +0x38; the first child +0x40, the next sibling +0x48 (a child is linked at the head);
  m_vecOrigin (local) +0x80; m_angRotation (local QAngle: pitch, yaw, roll in degrees) +0xb8; m_flScale +0xc4;
  m_vecAbsOrigin +0xc8; m_angAbsRotation +0xd4; m_flAbsScale +0xe0; the attachment / bone index +0xe4; the depth
  +0xeb; **m_nHierarchyType +0xec** (0 none, 1 bone-merge follow, 2 attachment, 3 a plain parent, 4 a bone: what the
  parent's vfn 0xd0 answers for the attach name); **the abs-stale byte +0xf4**; the node's lock +0xf8 (a CAtomicMutex,
  thread id +0x100); the pending flags +0x10c.
- **vfn 0x70, the dirty marking** (180c0b6c0; serial when 0x18218b070 is clear, as on a server tick): the flags are
  or'ed into +0x10c; the newly set ones: 1 | 2 | 4 (origin, angles, scale changed) set +0xf4 and call vfn 0x88; 0x100
  clears +0xf4 (the caller has already put the abs right); 0x10 / 0x40 / 0x80 are cleared without a skeleton instance
  (vfn 0x68). With any of 1 | 2 | 4 every child gets (flags without 0x100, 0x200, 0x80, 0x40, 0x10) | 1 (| 8 when
  +0xf0 is 0): so every descendant goes stale. Then +0x10c is handed to vfn 0x98 and cleared.
- **The abs cache** (180bec940, under the node's lock; the getter 180c12130 calls it when +0xf4 is set): a node with
  no parent takes its local as its abs (abs origin, angles, scale; m_nodeToWorld = (origin, scale,
  AngleQuaternion(angles))); a parented one runs 180c14210; +0xf4 cleared.
- **The parented update** (180c14210): for type 3, the parent's abs is worked out first if stale, the local
  CTransform is 1803c34d0 (origin, scale, AngleQuaternion(angles)), 180bed920 concatenates (type 3: parent's
  m_nodeToWorld then the local, 181476030), and 180bf1670 splits m_nodeToWorld back: abs scale its scale (snapped to 1
  within 0.001), abs angles QuaternionAngles(its rotation) (181475b60), abs origin its position. Types 1, 2 and 4 go
  through the skeleton (the attachment's or bone's transform, 180ca6840 / 180cabc70 / 1814a2df0): not ported.
- **ConcatTransforms** (181476030, __vectorcall: a in xmm0 / xmm1, b in xmm2 / xmm3): position a.q(b.p) a.s + a.p
  (the rotate: t = 2 (q x v), then (q x t) + (v + w t)), scale a.s b.s, rotation ((a.w b + a.x (b.w, -b.z, b.y, -b.x))
  + a.y (b.z, b.w, -b.x, -b.y)) + a.z (-b.y, b.x, b.w, -b.z) normalized by dpps (the identity 0x181f4a000 = (0, 0, 0,
  1) where the length is 0). The same lanes as rubikon's verified C# (Transforms.Concat, 1814738d0 in the older build).
- **QuaternionAngles** (181475b60 -> MatrixAngles 181473410): the rotation matrix from q + q, then with
  xy = sqrt(m10² + m00²) over 0.001 (0x181784de8): pitch atan2(-m20, xy), yaw atan2(m10, m00), roll atan2(m21, m22);
  else yaw atan2(-m01, m11), roll 0; each x 57.29578 (0x1817bfedc). atan2 is tier0's V_atan2f (import 0x18176a4a8): the
  CRT's atan2f (tier0 1802e0184), ported from rubikon's CrtMath.Atan2.
- **AngleQuaternion** (181473e90, 114 callers): each angle x pi/360 (0x3c0efa35 at 0x181aab8a0), V_sincosf, then
  x = cy (sr cp) - sy (cr sp), y = cy (cr sp) + sy (sr cp), z = sy (cr cp) - cy (sr sp), w = sy (sr sp) + cy (cr cp).

## The setters

- **SetLocalOrigin** (180c27c70): if any lane differs (180bcffd0), the store (180c26380: lane by lane, only the lanes
  that differ by ucomiss, so a 0 isn't overwritten by a -0; each a network change); a root that isn't stale takes it
  as its abs origin and m_nodeToWorld's position at once (vfn 0x70 0x101), else 1.
- **SetLocalAngles** (180c27b20): if the angles differ (1801f9480), the network change and the store; a root's whole
  abs is redone at once (abs = local, m_nodeToWorld from AngleQuaternion; 0x102), a child's marked (2).
- **SetLocalScale** (180c27d30 -> 180c129a0): on a change (ucomiss), the store; a root's abs redone at once (0x104),
  a child marked (4).
- **SetAbsOrigin** (180c26a40): nothing for a lane with an all-ones exponent (inf, NaN); the abs worked out; nothing
  when every lane is close enough to the abs origin now (180c00ea0: |a - b| <= max(1/256, max(|a|, |b|) x
  (1/256) / g_flConfigMaxCoord), maxss's operand order; tier0's g_flConfigMaxCoord is 16384, through the data import
  read by 18053afa0); else abs origin = m_nodeToWorld's position = v, and the local origin v (a root) or v through
  the parent's inverse (below): v turned by the inverse's rotation, times its scale, plus its position. The local
  store as SetLocalOrigin's (lane by lane); 0x101 (the children go stale).
- **SetAbsAngles** (180c26600): the abs worked out; nothing when the abs angles equal (18014a300); else abs angles = a,
  m_nodeToWorld's rotation = AngleQuaternion(a) (the abs origin and position stay); the local angles a (a root),
  (0, 0, 0) when a equals the parent's abs angles, else QuaternionAngles(the parent's inverse concat m_nodeToWorld)
  (181476030, 181475b60); stored if they differ; 0x102.
- **The parent's inverse** (inline in SetAbsOrigin 180c26c73.. and SetAbsAngles 180c266ff..): the rotation times
  (-1, -1, -1, 1) (0x181e886b0), normalized by dpps (a zero length divides by FLT_EPSILON, 0x181e88650); scale 1
  (ucomiss): the position turned by it, 0 - each lane, scale 1; else s' = 1 / s (0: 8388608, 0x18178058c): the turned
  position times s', 0 - each lane, scale s'. (Not quite 181473ba0's: that one turns by the unnormalized conjugate at
  scale 1.)
- **StartHierarchicalAttachment** (180c2c1f0, from the m_hParent change 180c12b40 / 180c15090): the parent node from
  m_hParent, the type from the parent's vfn 0xd0 (the attach name), the attachment / bone index for 2 / 4; then the
  parent pointer, the type, linked at the head of the parent's children, depth = the parent's + 1 (the descendants'
  too, 180be74f0), vfn 0x70 with 7 (0x87 for type 1). The local transform is kept: the world moves with the parent.
- **ClearParent** (180bf4be0, before a new parent or none): off the parent's child list; the depth and the type (a
  2-byte store at +0xeb) and the attachment index cleared. Nothing is marked: the abs cache keeps its last value.

## Ported and checked (4f-2, 2026-11-10)

- sim/src/math/atan.rs (atan2f), sim/src/math/transform.rs (rotate, concat_transforms, quaternion_angles,
  inverse_transform, transform_point), sim/src/game/scene.rs (the nodes: calc_abs, the setters, set_parent /
  clear_parent for type 3, vfn 0x70's marking, flush).
- rubikon/tests/SceneOracle maps server.dll (Image.cs: its sections, its tier0 and kernel32 imports bound to the real
  ones) and calls the DLL's own functions; `scene_check` compares every bit:
  - `--concat` (1,000,000 transform pairs, rotations from AngleQuaternion and raw ones, scales 0 .. 4): **0 differ**;
  - `--angles` (1,000,000 quaternions, the gimbal branch included): **0 differ**;
  - `--nodes` (Nodes.cs: 200,000 scenes of a root, a child and a grandchild on fake nodes whose vfn 0x70 is the
    DLL's own marking; six steps each: the lazy abs, SetAbsOrigin and SetAbsAngles on the child, SetLocalAngles /
    SetLocalOrigin on the root, SetLocalScale on the child, SetAbsOrigin / SetAbsAngles on the root; 3.6M node
    states): **0 differ**. web/src/cs2web/world/scene-test.mjs replays the same file through the .wasm and es.scene: 0
    differ (84 scenes skipped: a -0 local the setters can't place over a root's +0).
  - AngleQuaternion's AQT1 file is unchanged (the same cases): 0 of 1,000,000 differ.

## In the EntitySystem (4f-3, 2026-11-10)

The round's EntitySystem owns a Scene (sim/src/game/scene.rs, exports sim/src/game/scene_abi.rs `ze_es_node_*`,
`ze_es_scene_*`; web/src/world/entities/scene-nodes.js as `engine.es.scene`): nodes by slot (a removed one's slot is
reused), the setters above, set_parent for a plain parent, a node's state (24 words), and `flush()`: every live
node's abs worked out and its m_nodeToWorld in one Float32Array (8 floats a slot) the renderer and the classes can
read without a call per entity. Nothing uses it yet (4f-4): seeded rounds on all four maps are the same as master's.

## Parents and spawn (4f-4, 2026-11-10)

- **CBaseEntity::SetParent** (1803ebc00: skipped when either entity has bit 9 of its +0x10 +0x30 flags; the parent's
  +0x1be = 0x101) -> 180180300 -> **CGameSceneNode::SetParent** (180be92e0: node, parent node, attachment token,
  transform or null). The same parent and attachment: nothing (with a transform given: the local origin / angles /
  scale from it). Else 180bf2480 (below); no new parent: 180c33710 (the entity side: move type vfn 0x2b0, physics,
  the children's notes) and done. A new one: its vfn 0xd0 answers the type for the attachment (0: refused); the
  node's abs worked out; m_hParent (+0x78), +0x7c, the attachment (+0x104, 0 for type 3) set; with no transform
  given: **the parent's inverse** (the parent's m_nodeToWorld through 180bed5a0, the same inline inverse as
  SetAbsOrigin's: 180be9667..) **concat its m_nodeToWorld** (181476030), then 180c27ec0(origin, QuaternionAngles,
  scale); vfn 0xa0 (ClearParent, 180c151c0 -> 180bf4be0), vfn 0xa8 (the attach from m_hParent: 180c15090 ->
  StartHierarchicalAttachment, vfn 0x70 with 7), 180c33710. So the world transform is kept.
- **The unparent** (180bf2480): with a parent (m_hParent set or +0x7c): the abs worked out, m_hParent / +0x7c /
  the attachment cleared, its m_nodeToWorld made the local transform (180188810 copies it, 180c28080: 180c27ec0 with
  the position, QuaternionAngles of the rotation, the scale), vfn 0xa0, vfn 0xa8: the world transform is kept.
- **180c27ec0, the tolerant local store** (marks nothing): the origin's lanes stored (180c26380) unless every lane is
  within SetAbsOrigin's tolerance of the old; the angles whole if a lane is 0.001 degrees or more away by 18146bd20
  (V_fmodf(a - b, 360), tier0's AMD fmodf: exact; into (-180, 180) on the side a > b picks) and they differ; the
  scale if past 180c00ea0(1.1920929e-5 relative, 0.001 absolute) and different.
- **Spawn** (the node's keyvalues, 180c2ae00, vtable slot 8): the kv origin / angles are the abs ones and
  m_nodeToWorld = (abs origin, scale, AngleQuaternion(abs angles)); with a parentname resolved and no attachment (or
  "!absorigin"): the local transform the parent's inverse concat that (as SetParent), stored by 180c27ec0; with an
  attachment: the identity local; no parent: the abs as the local. ("useLocalOffset" / "positionInLocalSpace" take
  the kv as local: not ported.)

Ported (sim/src/game/scene_parent.rs: set_parent, unparent_keep_world, set_local_transform, attach, clear_parent)
and checked: SceneOracle `--nodes` has two more steps (SetParent(G, P) on the DLL's own 180be92e0, the attach done as
StartHierarchicalAttachment does for type 3; SetParent(C, none)): 200,000 eight-step scenes, **0 differ** natively and
through the .wasm.

**The entities on the nodes (4f-4):** every Entity has a node (entity.js: localOrigin / localAngles / getWorld /
worldOrigin / worldQuat read it; setLocalOrigin / setLocalAngles / setAbsOrigin / setAbsAngles / setAbsQuat /
setParent write it; `pos` / `quat` are gone and throw), players too (engine.addPlayer; placePlayer sets the pawn
node's abs origin and (0, yaw, 0): a stand-in for the pawn's own node). The spawn sets the kv origin / angles and
link() calls SetParent (keep world) as 180c2ae00 does; the SetLocalOrigin / SetLocalAngles / SetAbsOrigin /
SetAbsAngles inputs and CS2Fixes' origin / angles keyvalues call the node's setters; the movers move as CS2's
(docs/game/movers.md: rotating doors add to the QAngle, func_rotating turns by quaternions), momentary_rot_button
turns one lane of the QAngle (f32 sums); bodies' poses go through SetAbsOrigin + SetAbsAngles(QuaternionAngles). Stand-ins left: the
template placement (the template's transform concat the entity's, CPointTemplate's own untraced), the trainer's
matrix callers (setWorldTransform: logic_measure_movement), momentary_rot_button's own sums, the kv scale (not read: every node's scale 1), a killed entity's node removed with the frame's
kills.

## Template placement (2026-11-10)

- **CPointTemplate's spawn** (the script ForceSpawn 1804633f0 shows the shape): the spawn point is the template's
  abs origin (1803d6f50) and abs angles (1803d6de0, m_angAbsRotation +0xd4), or another entity's;
  async (+0x4c4) → nothing here. 180461810(template, origin*, angles*, 0, callback) -> 180461a00: the spawn
  group's transform = **AngleMatrix(angles, origin)** (18146bce0 = 18146bb60 AngleMatrix + the origin as the fourth
  column: a matrix3x4), the request to the engine (vfn 0x1e0 of 0x1821ba010), the spawned entities' callback.
- **env_entity_maker** (CEnvEntityMaker_API has only ForceSpawn and ForceSpawnAtEntityOrigin): SpawnEntity
  (180d5c480, origin*, angles*): its entitytemplate found by name (180bfc940, caller the maker); the maker's abs
  origin and angles, unless the origin passed isn't (FLT_MAX x 3): then that origin and those angles.
  ForceSpawnAtEntityOrigin (180d21cb0): the named entity (180bfc940 with the input's activator / caller) gives
  its abs origin and its own abs angles. Then 180461810 with the post-spawn callback 180d55290 (not read);
  spawnflag 1: a think 0.5 s on (180d3d850, not read).
- **The keyvalue parse** (181373fa0, per field, with the spawn's matrix at +8 and a transform flag at +0x10 of
  its context): FIELD_POSITION_VECTOR (0xc) → VectorTransform (181473aa0: each row (t + y m1) + (z m2 + x m0));
  FIELD_DIRECTION_VECTOR_WORLDSPACE (0x1c, with the flag) → 181473a60 (the rotation alone); FIELD_QANGLE_WORLDSPACE
  (0x1d, with the flag) → MatrixAngles(ConcatRotations(m, AngleMatrix(angles))) (18146bb60, 18146fe70,
  181471990 -> 181473410); FIELD_QUATERNION_WORLDSPACE (0x1e, with the flag) → 1814750b0 (QuaternionMatrix),
  ConcatRotations, 1814742a0. The field type names: the table at 0x181dbcd50 ({ name, type }). The node's abs
  origin / angles (+0xc8 / +0xd4) come out of it, and 180c2ae00 builds m_nodeToWorld from them (above).
- **ConcatRotations** (18146fe70, a, b, out): the 3x3 product, out[i][j] summed in the disassembly's pairs
  ((a00 b00 + a01 b10) + a02 b20; (a01 b11 + a00 b01) + a02 b21; (a01 b12 + a00 b02) + a02 b22; (a11 b10 + a10
  b00) + a12 b20; (a11 b11 + a10 b01) + a12 b21; (a10 b02 + a11 b12) + a12 b22; (a20 b00 + a21 b10) + a22 b20;
  (a21 b11 + a20 b01) + a22 b21; (a20 b02 + a21 b12) + a22 b22), the translation column 0.
- **AngleMatrix** (18146bb60): V_sincosf of each angle x pi/180; its columns are AngleVectors' forward, left and up
  (the same products in the same order).
- Ported: sim/src/math/matrix.rs (angle_matrix, concat_rotations, vector_transform, matrix_angles, spawn_place;
  QuaternionAngles now calls matrix_angles), scene_abi.rs `ze_es_node_place_spawn`, scene-nodes.js placeSpawn,
  engine.spawnTemplate(tpl, origin, angles, ...), classes/spawners.js. Checked: SceneOracle `--spawn` (server.dll's
  18146bce0, 181473aa0, 18146fe70, 181471990 chained as the parse does) + the spawn_check bin: origin and angles 0 of
  1,000,000 differ; scene_check (ConcatTransforms, QuaternionAngles, the node scenes) still 0 differ;
  web/src/cs2web/world/template-test.mjs on all four maps.
- **The transform flag** (2026-11-10): the parse's context is built on the stack of its caller 1813762d0 (+0 whether
  0x182331b00 +8 is set; +8 the spawn group's matrix, 1813856d0; +0x10 the flag): **flag = !181472f90(the identity
  0x181785c10, the matrix, 1e-5 (0x3727c5ac))**. 181472f90 is MatricesAreEqual over the 3x3 rotation only (rows 0x10
  apart, the translation column not read): false as soon as |a - b| (andps with the abs mask) > tol by comiss / ja (a
  NaN difference counts as equal). So positions are always VectorTransform'ed, and angles / directions / quaternions
  only when the spawn rotation isn't the identity (a template at angles near 0 0 0 keeps each entity's angles bit for
  bit). Ported: matrix.rs rotation_is_identity, `ze_es_node_place_spawn`. Checked: SceneOracle `--spawn` now writes
  "SPW2" with the DLL's 181472f90 answer per case (5% of the spawn angles within 0.002 degrees of 0): spawn_check,
  origin, angles and the identity test 0 of 1,000,000 differ (22,270 identity).
- **useLocalOffset / positionInLocalSpace** (180c2ae00's "take the kv as local"): not ported; on the four baked maps
  every entity's uselocaloffset is false and none has positioninlocalspace, so the path never runs there.
- **env_entity_maker's spawn callback** (180d55290, the callback 180461810 is given): with no entity spawned,
  nothing. The first spawned entity's handle into +0x4c0 / +0x4c4 and its abs origin into +0x4c8; when the maker's
  mins (+0x4a8) are all 0, they and the maxs (+0x4b4) become that entity's collision bounds (vfn 0x228 +0x40 / +0x4c
  through 180cea8c0, or its abs origin with no collision) less its abs origin (what reads them, spawnflag 2's
  space check, not read). Then **OnEntitySpawned** (+0x4f8, FireOutputInternal 181392440) **with the maker as
  activator and caller**. Then, when postspawnspeed (+0x4e4) isn't 0, every spawned entity whose m_nActualMoveType
  (+0x2f5, 1803d95f0) isn't NONE: the direction postspawndirection (+0x4d4), plus, with postspawninheritangles
  (+0x4e8), the abs angles (1803d6de0) of the maker's parent (1803d9790: the node parent's owner) or the maker's own;
  AngleVectors (181472530: forward, right, up); v = forward; v + (right r0) var; v + (forward r1) var; v + (up r2)
  var, each r a RandomFloat(-1, 1) off the global uniform stream (181687041, 0x181e328d8) and var
  postspawndirectionvariance (+0x4e0); the inlined VectorNormalize (length sqrt((z z + y y) + x x); out of [1e-17,
  1e17] 1814738b0, 0 -> 0); times the speed; VPhysicsGetObject (1803f0260(e, 0)) -> body vfn 0x208 (AddVelocity),
  else SetAbsVelocity (1803ea4a0). Ported: sim/src/game/maker.rs (`ze_maker_velocity`), classes/spawners.js
  postSpawn, engine.spawnTemplate's maker OnEntitySpawned. The draws: tier0's CUniformRandomStreamImpl (lib/cs-random.js,
  exact: SceneOracle `--random` + random-test.mjs, 0 of 4,000,000 draws differ) as engine.globalRandom, seeded with
  the round seed (CS2 seeds its global stream from the clock, GenerateDefaultRandomSeed tier0 18015d580: no two servers
  agree, and every server system draws from it). Stand-in:
  the move type taken as VPHYSICS for an unparented physbox with a
  body, NONE for the rest. Checked: maker-test.mjs on RE3 (the rocket launcher's [PR#]weapon_rocket2: its missile
  physbox leaves at 2,994 u/s one step on, speed 3000; the activator; the replica's hash).
- **Not read**: which field type the node's origin / angles keys have (taken as the position vector and the
  world-space QAngle, which is what the parse transforms).

## Kill, KillHierarchy and removal (2026-11-10, started; from the disassembly alone)

- **InputKill** (CBaseEntity_API::Kill 180cc4dd0 -> 180cfce50): the owner (m_hOwnerEntity +0x3e4) told (its vfn
  0x3b8 with this, then this's vfn 0x1b0(0)); a player (vfn 0x558) goes another way (a kick through the engine,
  vfn 0x308 of 0x1821ba010 with reason 0x27); else UTIL_Remove (180c30c10) on this entity alone.
- **InputKillHierarchy** (180cc4e40): every child first (the node's first child 1803d6930, next sibling 1803e5160),
  each through 180cfd4c0 (the same walk on its own children, then the owner notice and UTIL_Remove), then the owner
  notice and UTIL_Remove of itself.
- **UTIL_Remove** (180c30c10) -> 18138a3e0 (the entity system): an entity with no instance pointer is freed at once
  (181385050); flag bit 11 (+0x30) -> 181380c50; else bit 9 set and the entity queued (+0xc98 / +0xca0 list,
  18137c770), the queue run by 1813829c0 (not read).
- **The deletion** (1813829c0, the queue's run): each batch through the game entity system's vfn 0xb8 (180c34000 ->
  181391560: each entity's vfn 0x70, UpdateOnRemove), then vfn 0x80 per entity, the name table's swap-remove
  (18138b030) and the free.
- **CBaseEntity::UpdateOnRemove** (180d18f80, vfn 0x70 of 0x181962408): ... the entity's children (1803d7360: every
  child entity of its node) from the last: those with **m_iEFlags (+0x414) bit 9 (0x200)** set → SetParent(null)
  (1803ebc00: unparented, keeping the world place); then the children left → "Warning: Deleting orphaned children
  of %s" and UTIL_Remove (180c30c10) on each. So **a plain Kill takes the children with it** (they're removed in
  the same deletion), except children with bit 9, which stay, unparented. engine.js removes every child (ze_lifeforms_v1_1's
  phase2_door_move_c takes its parented platform with it, as the trainer saw).
- **What sets m_iEFlags bit 9** (2026-11-10): a sweep of server.dll's .text for every store to +0x414 with an
  `or` / `bts` of bit 9 in the 8 instructions before it finds one: 180d130a6 (`bts eax, 9`) in **FUN_180d12ea0,
  CBasePlayerPawn's vfn 0x48** (vtable 0x181963748: the spawn with the keyvalues, which also reads "controller";
  CCSPlayerPawnBase's vfn 0x48 18024b950 calls it after "original_controller"). No immediate store sets it (the
  datamap 0x181ddfc60 could on a restore). So only a player pawn has the bit: a killed parent unparents a pawn
  (keeping its world place) and removes every other child. Players are never parented in this engine (no
  SetParent for a player), so engine.js removing every child is CS2's for every child it can have.

## VPhysicsUpdate: a dynamic body's pose onto its entity (2026-11-10)

CS2 has no per-entity VPhysicsUpdate virtual on this path: the physics game system pushes every moved aggregate's
pose onto its node after the step (rubikon/CS2_RUNTIME.md "The server frame" for the frame order).
- **The push** (inside FUN_1805a6870, the post-step part of CPhysicsGameSystem's OnSimulate; 1805a7260, which
  CS2_RUNTIME.md calls PushDynamicTransforms, is an address inside it): SimulateFrame (1805c1580, "CPhysicsGameSystem::
  SimulateFrame", physicsgamesystem.cpp:0xb71) steps the world (IVPhysics2World vfn 0x80 with the system's +0x480 list
  as its output: the aggregates vphysics reports for the step), then **PushDynamicTransformsWorker** (1805aeb70,
  physicsgamesystem.cpp:0x507; threaded through g_pThreadPool vfn 0x98 when 0x181ff5760 +0x58 is set, else serial)
  over that list (+0x30 count, +0x38 array): each entry with a node (entry +8) and its vfn 0x40 not 2 goes to
  1805c9530. The list is the physics world's awake set after the step (below, "The push list").
- **1805c9530** (system, node, aggregate): nothing unless the node's m_nHierarchyType (+0xec) is 0, body 0
  (aggregate vfn 0xc0(0)) has motion vfn 0x20 == 2 (dynamic), and the aggregate's body count (vfn 0x48 -> +0x18) is
  at most 1. Then the body's transform (body vfn 0x1b0, GetTransform: the frame origin and orientation; 1803c3520
  copies it as a CTransform), the abs worked out if stale (+0xf4 -> 180bec940), the scale replaced by the node's abs
  scale (+0xe0). The bind-pose undo: a correction transform starts as the identity (18017ca50: zero position
  0x18177bf80, scale 1, quaternion 0x181f4a000); when the node's aggregate (+0x200) has exactly one body and the
  skeleton's body-to-bone map (+0x370 count, +0x378 u16 array; 180cab2d0) gives a bone for body 0, the correction is
  that bone's model-space bind (180cab6e0: the bone chain up to the root through 1814a30a0, concatenated by
  181476030, from the model at +0x1c0; the identity when there's no model) and the pose becomes
  ConcatTransforms(pose, inverse(correction)) (181476300, 1805c08e0 sets the scale lane, 181476030: renormalized);
  with no bone and the identity's scale 1 the pose is used as it is. Then SetWorldTransform(node, pose) (180c28110).
  After it, an aggregate of more than one body (a ragdoll) marks the node with vfn 0x70(0x80).
- **SetWorldTransform** (180c28110, node, CTransform*): m_nodeToWorld (+0x10..+0x2f) = the transform, its
  quaternion as it is (not rebuilt from angles); 180bf1670 splits it into the abs (abs scale = its scale, snapped to
  1 within 0.001; abs angles QuaternionAngles 181475b60; abs origin its position). The old local origin / angles /
  scale are kept; a root (no parent +0x38): 180c28080 (the local is the transform: 180591730 the scale, QuaternionAngles,
  180187f50 the position) through 180c27ec0; a child: the parent's abs worked out if stale, the parent's inverse
  inline (the rotation times (-1, -1, -1, 1) 0x181e886b0 over its dpps length (0 -> 0x181e88650); scale 1 (ucomiss
  with 1.0): position 0 - q(p); else s' = 1 / s (0 -> 8388608, 0x18178058c), 0 - q(p) s', scale s': the same as
  SetAbsOrigin's), ConcatTransforms(inverse, transform), split and stored by 180c27ec0. Then the flags, old local
  against new: origin 1 when any lane fails 180c00ea0(old, new, 1/256 / g_flConfigMaxCoord (18053afa0), 1/256
  0x18191d444); angles 2 when any lane fails 18146bd20(old, new, 0.001 0x181784de8); scale 4 when 180c00ea0(old,
  new, 1.1920929e-5 0x1817d0e8c, 0.001) fails. No flags: +0xf4 = 0; else vfn 0x70(flags | 0x100) (the jmp at
  180c285cd).
- Ported: sim/src/game/scene_world.rs (set_world_transform, push_dynamic), scene_abi.rs `ze_es_node_push_dynamic` /
  `ze_es_node_world`, scene-nodes.js pushDynamic / setWorld, entity.pushDynamic; physics-rubikon.js followBody and
  weapon-body.js followWeaponBody push through it (before: SetAbsOrigin + SetAbsAngles(QuaternionAngles), which
  rebuilt m_nodeToWorld's rotation from the angles and skipped origins within SetAbsOrigin's tolerance). Checked:
  SceneOracle `--world` (World.cs: 180c28110 itself on fake nodes, root and child, nudges within the tolerances) +
  scene_check, 0 of 200,000 scenes differ natively; scene-test.mjs on the same file through the .wasm, 0 differ.
- **The push list** (vphysics2_20260924.dll, the build rubikon traces): the server's SimulateFrame calls
  CVPhysics2Interface vfn 0x80 (SimulateWorlds 180075b60: worlds, count, dt, substeps, threaded, the out list): each
  world's vfn 0 (CVPhys2World Simulate 180059f30) per substep, then **vfn 8 (180059fe0)** with the list. vfn 8 walks
  the world's changed set (+0x78, +0x80 entries of 0x10, +0x8c count): an object whose vfn 0x180 says awake is added
  to the awake set (+0x58, 1800698e0) and, if new there, to out list 0 (+0, +8); one asleep is removed (1800696a0)
  and goes to list 1 (+0x18); then **every object in the awake set goes to list 2 (+0x30 count, +0x38 data)**, the one
  PushDynamicTransformsWorker reads; the changed set is cleared. The objects are CPhysAggregateInstance (vtable
  0x1803f8740): vfn 0x180 (180048860) is asleep when every body's (+0x38 count, +0x40) vfn 0x408 says so, and
  CPhysicsBody (vtable 0x1803f44e0) vfn 0x408 (180013210) is the RnBody's +0x249 bit 2 (rubikon's Flags249 & 4). So
  an aggregate is pushed every tick it is awake after the step, and not in the step it falls asleep in (its entity
  keeps the pose of the step before). Ported: PhysicsApi.WritePoses' awake slot is that bit (it was ActiveIndex),
  weapon-body.js pushAwakePose (physboxes and weapons). Checked: physbox-test.mjs (an awake body's pose is the node's
  each tick, a sleeping one's node keeps its last awake pose).
- **The body-to-bone map** (CModelState, the skeleton instance's m_modelState at +0x120; its +0x250 count / +0x258 u16
  array = skeleton +0x370 / +0x378): rebuilt by **180ca8eb0** (cleared, then, with a model (+0xa0) and an aggregate
  (+0xe0), **1814a7b50**(the model's skeleton +0x130, the aggregate's data (vfn 0x48), the map, the reverse map
  +0x268)): nothing unless the skeleton has bones (1814a2710); then per part (the data's +0x18 count, +0x20 u32 name
  hashes: m_boneNames') the skeleton bone of that hash (18149ed00, -1 for none), and the reverse map bone -> part.
  The pull (**180588af0**, PullKinematicTransforms' per-body target) reads it too, behind **sv_phys_animated_hierarchy**
  (registered at 1800759a0 into 0x181ff5738, default on): the entity's m_nodeToWorld with its scale lane 1, through
  180cab6e0 with body 0's bone. A bake probe on dark souls: every brush model has no skeleton bones (no map: the
  pose as it is), the 66 stock weapons put their one part on `weapon_offset` (no offset, a near-identity turn) under
  the root `weapon` (the model's offset: the AK (2.97, -0.19, 2.98), the M4 (18.2, -0.19, 12.4)), so a dropped
  weapon's body sits that far from its entity; m_indexNames / m_indexHash are placeholders ("0", 0).
- **180cab6e0** (node, out, input, bone): without a model (+0x1c0) the input; else the bones set up (180ca5f30(node,
  0xfffff)), acc = the bone's local CTransform (+0x138's array at 18149ef60's offset, 0x20 a bone; the identity
  0x182337e70 / 0x182337e80 without one), for each parent (1814a30a0) acc = Concat(parent's, acc), then Concat(input,
  acc). **181476300**, the out-of-line inverse (not SetAbsOrigin's inline one): the rotation times (-1, -1, -1, 1)
  over its dpps length; scale 1: the position turned by the **unnormalised** conjugate, 0 - each lane; else the
  normalised conjugate, s' = 1 / s (0: 1 / FLT_EPSILON), the position times 0 - s', scale s'.
- Ported: sim/src/game/bone_pose.rs (bone_place, pull_pose, push_pose, `ze_bone_pose`), math/transform.rs
  inverse_out_of_line, `ze_es_node_push_dynamic` with the chain; the bake's physics_bones.json (RubikonBake.cs
  BoneChain: each one-part model whose part names a skeleton bone, the bone's parent-space transforms to the root),
  world/physics-bones.js, engine.boneChains; weapon-body.js: the spawn, the throw, the keyframed drive and the
  teleport go through the pull (from the node's m_nodeToWorld: they decomposed a three.js matrix before), the push
  through the chain. Checked: SceneOracle `--bones` (181476300, the pull and the push through the DLL's own
  inverse and ConcatTransforms) + the bone_check bin, 0 of 1,000,000 differ each; weapon-bone-test.mjs (a dropped
  AK's node the body through the chain bit for bit, 4.212 u off, the replica's hash).
- **Stand-ins left**: the skeleton's local bones taken as the reference pose (m_bonePosParent / m_boneRotParent,
  scale 1) where CS2 reads the set-up bones (180ca5f30: a weapon with no animation leaves them so); the body's
  creation taken to place it as the pull does; a physbox's own pull (a brush model: no chain, exact).

## To trace next

1. The skeleton instance's bone setup (180ca5f30) for a dropped weapon (the chain's local bones taken as the reference
   pose) and the body's placement at its creation (1809ff9b0 -> 180d0f2c0). (Done: the movers' paths, movers.md /
   trains.md; UpdateOnRemove; template placement; VPhysicsUpdate's transform path, its push list and the body-to-bone
   map, above.)
2. The attachment and bone parents (types 2, 4: the model's attachment / bone transform; SetParentAttachment), type
   1's bone-merge follow; the +0xe9 / +0xea flag bits.
3. Whether a CS2 map sets a session max coord (Worldsize_SetSessionMaxCoord) that SetAbsOrigin's tolerance would read.

## The plan for the state

- **4f-2** (done): the hierarchy math, ported and checked against the DLL.
- **4f-3** (done): the scene nodes in the sim's EntitySystem, the exports and the Float32Array view.
- **4f-4** (done): the Entity's transform is its node (above).
- **4f-5** (done, 2026-11-10): the world hash in the sim (sim/src/game/world_hash.rs) over the entity list and each
  node's local origin, with the enabled flag and health mirrored in from JS; the same bits as the JS version on all
  four maps. engine.flushView(): every node's m_nodeToWorld in one call, which Entity.getWorld reads while it's
  current (the client flushes once a frame and once a tick).
- **4f-6** (started 2026-11-10: the linear movers, docs/game/movers.md): the movers' own transform paths and the rest of "To trace next" 1; then the classes' inputs (1813ac4d0)
  family by family.
