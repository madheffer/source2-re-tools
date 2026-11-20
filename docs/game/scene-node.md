# Scene node: an entity's transform (CGameSceneNode, each entity's m_pGameSceneNode)

server_20261105 (CGameSceneNode vtable 0x1819459f8, RTTI); vphysics2_20260924 (the push list); tier0 (atan2f, fmodf,
the random stream). Related: [io-queue.md](io-queue.md), [io-targets.md](io-targets.md), [movers.md](movers.md),
[trains.md](trains.md).

## Functions

| Address | Module | What |
|---|---|---|
| 180c0b6c0 | server | node vfn 0x70: dirty marking (serial when 0x18218b070 is clear, as on a server tick) |
| 180bec940 | server | abs cache (under the node's lock) |
| 180c12130 | server | abs getter: calls 180bec940 when +0xf4 is set |
| 180c14210 | server | parented update |
| 1803c34d0 | server | local CTransform (origin, scale, AngleQuaternion(angles)) |
| 180bed920 | server | concatenates (type 3: parent's m_nodeToWorld then the local) |
| 180bf1670 | server | splits m_nodeToWorld into the abs |
| 180ca6840 / 180cabc70 / 1814a2df0 | server | types 1, 2, 4: the attachment's or bone's transform through the skeleton |
| 181476030 | server | ConcatTransforms (__vectorcall: a in xmm0 / xmm1, b in xmm2 / xmm3) |
| 181475b60 -> 181473410 | server | QuaternionAngles -> MatrixAngles |
| 181473e90 | server | AngleQuaternion (114 callers) |
| 181473ba0 | server | a transform inverse turning by the unnormalized conjugate at scale 1 |
| 180c27c70 | server | SetLocalOrigin |
| 180bcffd0 | server | any lane differs |
| 180c26380 | server | local origin store, lane by lane (only lanes that differ by ucomiss: a 0 isn't overwritten by a -0; each a network change) |
| 180c27b20 | server | SetLocalAngles |
| 1801f9480 | server | angles differ |
| 180c27d30 -> 180c129a0 | server | SetLocalScale |
| 180c26a40 | server | SetAbsOrigin (inline parent inverse at 180c26c73..) |
| 180c00ea0 | server | close enough: `abs(a - b) <= max(abs_tol, max(abs(a), abs(b)) x rel)` |
| 18053afa0 | server | reads tier0's g_flConfigMaxCoord (data import) |
| 180c26600 | server | SetAbsAngles (inline parent inverse at 180c266ff..) |
| 18014a300 | server | angles equal |
| 180c2c1f0 | server | StartHierarchicalAttachment (from the m_hParent change 180c12b40 / 180c15090) |
| 180be74f0 | server | descendants' depth |
| 180bf4be0 | server | ClearParent |
| 1803ebc00 | server | CBaseEntity::SetParent -> 180180300 |
| 180be92e0 | server | CGameSceneNode::SetParent(node, parent node, attachment token, transform or null) |
| 180bf2480 | server | unparent (keeps the world transform) |
| 180c33710 | server | entity side of a parent change (move type vfn 0x2b0, physics, the children's notes) |
| 180bed5a0 | server | the parent's inverse (inline at 180be9667..) |
| 180c151c0 -> 180bf4be0 | server | node vfn 0xa0 ClearParent |
| 180c15090 | server | node vfn 0xa8: attach from m_hParent -> StartHierarchicalAttachment |
| 180188810 | server | copies m_nodeToWorld |
| 180c28080 | server | 180c27ec0 with the position, QuaternionAngles of the rotation, the scale |
| 180c27ec0 | server | tolerant local store (marks nothing) |
| 18146bd20 | server | V_fmodf(a - b, 360) angle compare (tier0's AMD fmodf: exact; into (-180, 180) on the side a > b picks) |
| 180c2ae00 | server | node Spawn (keyvalues; vtable slot 8) |
| 1804633f0 | server | CPointTemplate script ForceSpawn |
| 1803d6f50 / 1803d6de0 | server | abs origin / abs angles (m_angAbsRotation +0xd4) |
| 180461810 -> 180461a00 | server | template spawn (template, origin*, angles*, 0, callback) |
| 18146bce0 | server | AngleMatrix(angles, origin) = 18146bb60 + the origin as the fourth column (matrix3x4) |
| 18146bb60 | server | AngleMatrix |
| 180d5c480 | server | env_entity_maker SpawnEntity(origin*, angles*) |
| 180bfc940 | server | find entity by name |
| 180d21cb0 | server | ForceSpawnAtEntityOrigin |
| 180d55290 | server | env_entity_maker's post-spawn callback |
| 180d3d850 | server | spawnflag 1 think (0.5 s on; not read) |
| 181373fa0 | server | keyvalue parse per field (spawn matrix at +8, transform flag at +0x10 of its context) |
| 1813762d0 | server | the parse's caller (builds the context) |
| 1813856d0 | server | the spawn group's matrix |
| 181473aa0 | server | VectorTransform: each row `(t + y m1) + (z m2 + x m0)` |
| 181473a60 | server | rotate a direction |
| 18146fe70 | server | ConcatRotations(a, b, out) |
| 181471990 -> 181473410 | server | MatrixAngles |
| 1814750b0 | server | QuaternionMatrix |
| 1814742a0 | server | matrix -> quaternion |
| 181472f90 | server | MatricesAreEqual (3x3 rotation only, rows 0x10 apart) |
| 181392440 | server | FireOutputInternal |
| 1803d95f0 | server | m_nActualMoveType (+0x2f5) |
| 1803d9790 | server | the node parent's owner |
| 181472530 | server | AngleVectors (forward, right, up) |
| 181687041 | server | RandomFloat on the global uniform stream (0x181e328d8) |
| 1814738b0 | server | VectorNormalize |
| 1803f0260 | server | VPhysicsGetObject(e, 0) |
| 1803ea4a0 | server | SetAbsVelocity |
| 180cc4dd0 -> 180cfce50 | server | CBaseEntity_API::Kill (InputKill) |
| 180c30c10 | server | UTIL_Remove |
| 180cc4e40 | server | InputKillHierarchy |
| 1803d6930 / 1803e5160 | server | node's first child / next sibling |
| 180cfd4c0 | server | KillHierarchy's per-child walk |
| 18138a3e0 | server | entity system remove |
| 181385050 | server | free at once |
| 181380c50 | server | flag bit 11 path |
| 18137c770 | server | queue for deletion (+0xc98 / +0xca0 list) |
| 1813829c0 | server | deletion queue run |
| 180c34000 -> 181391560 | server | game entity system vfn 0xb8: each entity's vfn 0x70 (UpdateOnRemove) |
| 18138b030 | server | name table swap-remove |
| 180d18f80 | server | CBaseEntity::UpdateOnRemove (vfn 0x70 of 0x181962408) |
| 1803d7360 | server | every child entity of a node |
| FUN_180d12ea0 | server | CBasePlayerPawn vfn 0x48 (vtable 0x181963748): spawn with keyvalues ("controller"); sets m_iEFlags bit 9 at 180d130a6 (`bts eax, 9`) |
| 18024b950 | server | CCSPlayerPawnBase vfn 0x48: calls it after "original_controller" |
| FUN_1805a6870 | server | CPhysicsGameSystem OnSimulate's post-step part (1805a7260, "PushDynamicTransforms", is an address inside it) |
| 1805c1580 | server | SimulateFrame ("CPhysicsGameSystem::SimulateFrame", physicsgamesystem.cpp:0xb71) |
| 1805aeb70 | server | PushDynamicTransformsWorker (physicsgamesystem.cpp:0x507) |
| 1805c9530 | server | (system, node, aggregate): push one pose |
| 1803c3520 | server | body transform as a CTransform |
| 18017ca50 | server | identity transform (zero position 0x18177bf80, scale 1, quaternion 0x181f4a000) |
| 180cab2d0 | server | skeleton body-to-bone map lookup |
| 180cab6e0 | server | (node, out, input, bone): a bone's model-space bind |
| 1814a30a0 | server | bone parent |
| 181476300 | server | out-of-line transform inverse |
| 1805c08e0 | server | sets the scale lane |
| 180c28110 | server | SetWorldTransform(node, CTransform*) |
| 180591730 / 180187f50 | server | local from transform: the scale / the position |
| 180ca8eb0 | server | rebuild the body-to-bone map |
| 1814a7b50 | server | (skeleton, aggregate data, map, reverse map +0x268) |
| 1814a2710 | server | skeleton has bones |
| 18149ed00 | server | bone by name hash (-1 none) |
| 18149ef60 | server | a bone's local transform offset |
| 180588af0 | server | PullKinematicTransforms' per-body target |
| 1800759a0 | server | sv_phys_animated_hierarchy registration (0x181ff5738) |
| 180ca5f30 | server | skeleton bone setup (node, 0xfffff) |
| 1809ff9b0 -> 180d0f2c0 | server | a dropped weapon's body creation (unread) |
| 1813ac4d0 | server | the classes' inputs |
| 18015d580 | tier0 | GenerateDefaultRandomSeed (the global stream seeded from the clock) |
| 1802e0184 | tier0 | CRT atan2f (V_atan2f, import 0x18176a4a8) |
| 180075b60 | vphysics2 | CVPhysics2Interface vfn 0x80 SimulateWorlds(worlds, count, dt, substeps, threaded, out list) |
| 180059f30 | vphysics2 | CVPhys2World vfn 0 Simulate (per substep) |
| 180059fe0 | vphysics2 | CVPhys2World vfn 8: builds the out lists |
| 1800698e0 / 1800696a0 | vphysics2 | add to / remove from the awake set |
| 180048860 | vphysics2 | CPhysAggregateInstance (vtable 0x1803f8740) vfn 0x180: asleep |
| 180013210 | vphysics2 | CPhysicsBody (vtable 0x1803f44e0) vfn 0x408: RnBody +0x249 bit 2 |

## Fields

| Offset | Field |
|---|---|
| node +0x10 | m_nodeToWorld CTransform (position +0x10, scale +0x1c, quaternion xyzw +0x20) |
| node +0x30 | owner entity |
| node +0x38 | parent node |
| node +0x40 / +0x48 | first child / next sibling (a child linked at the head) |
| node +0x70 | m_hParent (schema +0x70: a CGameSceneNodeHandle; schema.py's m_hOwner +0x8 and m_name +0xc entries sit beside it, taken as the handle's) |
| node +0x78 / +0x7c | m_hParent's m_hOwner (the parent entity's handle: what SetParent / the unparent set and clear as "m_hParent") / its m_name (the attachment name; the unparent tests "m_hParent or +0x7c") |
| node +0x80 | m_vecOrigin (local) |
| node +0xb8 | m_angRotation (local QAngle: pitch, yaw, roll, degrees) |
| node +0xc4 | m_flScale |
| node +0xc8 | m_vecAbsOrigin |
| node +0xd4 | m_angAbsRotation |
| node +0xe0 | m_flAbsScale |
| node +0xe4 | attachment / bone index |
| node +0xe9 / +0xea | flag bits (unread) |
| node +0xeb | depth (2-byte store with the type at +0xeb by ClearParent) |
| node +0xec | m_nHierarchyType: 0 none, 1 bone-merge follow, 2 attachment, 3 plain parent, 4 bone (the parent's vfn 0xd0 answer for the attach name) |
| node +0xf0 | (0: children also get flag 8) |
| node +0xf4 | abs-stale byte |
| node +0xf8 | lock (CAtomicMutex, thread id +0x100) |
| node +0x104 | attachment (0 for type 3) |
| node +0x10c | pending flags |
| node +0x120 | skeleton instance's m_modelState (CModelState: +0x250 count / +0x258 u16 array = skeleton +0x370 / +0x378; reverse +0x268) |
| skeleton +0xa0 / +0xe0 | model / aggregate |
| skeleton +0x138 | bone local transforms (0x20 a bone; identity 0x182337e70 / 0x182337e80 without one) |
| skeleton +0x1c0 | model |
| node (skeleton instance) +0x200 | the node's aggregate (1805c9530: exactly one body -> the bind-pose undo) |
| skeleton +0x370 / +0x378 | body-to-bone map count / u16 array |
| model +0x130 | skeleton |
| aggregate data +0x18 / +0x20 | part count / u32 name hashes (m_boneNames') |
| entity +0x10 +0x30 bit 9 | skips SetParent |
| entity +0x1be | parent's set to 0x101 by SetParent |
| entity +0x2f5 | m_nActualMoveType |
| entity +0x3e4 | m_hOwnerEntity |
| entity +0x414 | m_iEFlags (bit 9 0x200: a child kept, unparented, by UpdateOnRemove) |
| entity +0x30 bit 11 / bit 9 | UTIL_Remove: 181380c50 / queued |
| template +0x4c4 | async |
| maker +0x4a8 / +0x4b4 | mins / maxs |
| maker +0x4c0 / +0x4c4 / +0x4c8 | first spawned handle / abs origin |
| maker +0x4d4 / +0x4e0 / +0x4e4 / +0x4e8 | postspawndirection / postspawndirectionvariance / postspawnspeed / postspawninheritangles |
| maker +0x4f8 | OnEntitySpawned |
| physics system +0x480 | out list for the step |
| list +0x30 / +0x38 | count / array (entry +8 node, its vfn 0x40 not 2) |
| world +0x58 | awake set |
| world +0x78 / +0x80 / +0x8c | changed set (0x10 entries) / count |
| out lists +0 / +8, +0x18, +0x30 / +0x38 | 0 newly awake, 1 asleep, 2 every awake (count / data) |
| aggregate +0x38 / +0x40 | body count / bodies |
| parse context +0 / +8 / +0x10 | 0x182331b00 +8 set / spawn group's matrix / transform flag |

## Constants

| Value | What |
|---|---|
| 0x181f4a000 | identity quaternion (0, 0, 0, 1) |
| 0.001 (0x181784de8) | MatrixAngles gimbal threshold; abs scale snap to 1; angle tolerance (degrees) |
| 57.29578 (0x1817bfedc) | radians -> degrees |
| π/360 (0x3c0efa35 at 0x181aab8a0) | AngleQuaternion half-angle |
| 16384 | tier0's g_flConfigMaxCoord |
| 1/256 (0x18191d444) | origin tolerance |
| 1.1920929e-5 (0x1817d0e8c) | scale relative tolerance (absolute 0.001) |
| (-1, -1, -1, 1) (0x181e886b0) | conjugate mask |
| FLT_EPSILON (0x181e88650) | zero-length divisor |
| 8388608 (0x18178058c) | 1 / 0 scale stand-in |
| 1e-5 (0x3727c5ac), identity 0x181785c10 | the transform flag test |
| 0x181dbcd50 | field type name table ({ name, type }) |
| FIELD_POSITION_VECTOR 0xc, FIELD_DIRECTION_VECTOR_WORLDSPACE 0x1c, FIELD_QANGLE_WORLDSPACE 0x1d, FIELD_QUATERNION_WORLDSPACE 0x1e | |
| 0x1821ba010 | the engine (vfn 0x1e0 spawn request; vfn 0x308 kick, reason 0x27) |
| 0x181ddfc60 | CBasePlayerPawn datamap |
| 0x181ff5760 +0x58 | threads the push through g_pThreadPool vfn 0x98 |
| sv_phys_animated_hierarchy default on | |
| 1e-17 / 1e17 | VectorNormalize range |
| FLT_MAX x 3 | env_entity_maker "no origin passed" |

## Dirty marking (vfn 0x70, 180c0b6c0)

1. Flags or'ed into +0x10c; of the newly set: 1 | 2 | 4 (origin, angles, scale) set +0xf4 and call vfn 0x88; 0x100 clears +0xf4 (abs already right); 0x10 / 0x40 / 0x80 cleared without a skeleton instance (vfn 0x68).
2. With any of 1 | 2 | 4 every child gets (flags without 0x100, 0x200, 0x80, 0x40, 0x10) | 1 (| 8 when +0xf0 is 0): every descendant goes stale.
3. +0x10c handed to vfn 0x98 and cleared.

## Abs cache (180bec940)

- No parent: abs = local (origin, angles, scale); m_nodeToWorld = (origin, scale, AngleQuaternion(angles)). A parented one: 180c14210. +0xf4 cleared.
- 180c14210, type 3: the parent's abs first if stale; local = 1803c34d0; 180bed920 (parent's m_nodeToWorld then the local, 181476030); 180bf1670: abs scale its scale (snapped to 1 within 0.001), abs angles QuaternionAngles, abs origin its position.

## Math

- **ConcatTransforms** (181476030): position `a.q(b.p) a.s + a.p` (rotate: `t = 2 (q x v)`, then `(q x t) + (v + w t)`); scale `a.s b.s`; rotation `((a.w b + a.x (b.w, -b.z, b.y, -b.x)) + a.y (b.z, b.w, -b.x, -b.y)) + a.z (-b.y, b.x, b.w, -b.z)` normalized by dpps (the identity where the length is 0). Same lanes as rubikon's verified C# (Transforms.Concat, 1814738d0 in the older build).
- **QuaternionAngles** (181475b60 -> 181473410): the rotation matrix from q + q; `xy = sqrt(m10² + m00²)` over 0.001: pitch `atan2(-m20, xy)`, yaw `atan2(m10, m00)`, roll `atan2(m21, m22)`; else yaw `atan2(-m01, m11)`, roll 0; each x 57.29578. atan2 is tier0's V_atan2f (the CRT's atan2f).
- **AngleQuaternion** (181473e90): each angle x π/360, V_sincosf; `x = cy (sr cp) - sy (cr sp)`, `y = cy (cr sp) + sy (sr cp)`, `z = sy (cr cp) - cy (sr sp)`, `w = sy (sr sp) + cy (cr cp)`.
- **Inline parent inverse** (SetAbsOrigin, SetAbsAngles, SetParent, SetWorldTransform): rotation x (-1, -1, -1, 1), normalized by dpps (a zero length divides by FLT_EPSILON); scale 1 (ucomiss with 1.0): position turned by it, 0 - each lane, scale 1; else `s' = 1 / s` (0: 8388608): turned position x s', 0 - each lane, scale s'.
- **181476300** (out-of-line inverse): rotation x (-1, -1, -1, 1) over its dpps length; scale 1: position turned by the **unnormalised** conjugate, 0 - each lane; else the normalised conjugate, `s' = 1 / s` (0: 1 / FLT_EPSILON), position x (0 - s'), scale s'.
- **ConcatRotations** (18146fe70): 3x3 product in the disassembly's pairs: `(a00 b00 + a01 b10) + a02 b20`; `(a01 b11 + a00 b01) + a02 b21`; `(a01 b12 + a00 b02) + a02 b22`; `(a11 b10 + a10 b00) + a12 b20`; `(a11 b11 + a10 b01) + a12 b21`; `(a10 b02 + a11 b12) + a12 b22`; `(a20 b00 + a21 b10) + a22 b20`; `(a21 b11 + a20 b01) + a22 b21`; `(a20 b02 + a21 b12) + a22 b22`; translation column 0.
- **AngleMatrix** (18146bb60): V_sincosf of each angle x π/180; its columns are AngleVectors' forward, left and up (same products, same order).
- **181472f90**: false as soon as |a - b| (andps abs mask) > tol by comiss / ja (a NaN difference counts as equal); translation column not read.

## Setters

- **SetLocalOrigin**: any lane differs -> 180c26380; a root that isn't stale takes it as its abs origin and m_nodeToWorld's position at once (vfn 0x70 0x101), else 1.
- **SetLocalAngles**: differ -> network change and store; a root's whole abs redone at once (0x102), a child marked (2).
- **SetLocalScale**: on a change (ucomiss) the store; a root's abs redone (0x104), a child marked (4).
- **SetAbsOrigin**: nothing for a lane with an all-ones exponent (inf, NaN); abs worked out; nothing when every lane is close (180c00ea0: `|a - b| <= max(1/256, max(|a|, |b|) x (1/256) / g_flConfigMaxCoord)`, maxss's operand order); else abs origin = m_nodeToWorld's position = v, local = v (root) or v through the parent's inverse (turned by its rotation, times its scale, plus its position), stored lane by lane; 0x101.
- **SetAbsAngles**: abs worked out; nothing when equal (18014a300); else abs angles = a, m_nodeToWorld's rotation = AngleQuaternion(a) (position stays); local = a (root), (0, 0, 0) when a equals the parent's abs angles, else QuaternionAngles(parent inverse concat m_nodeToWorld); stored if different; 0x102.
- **StartHierarchicalAttachment**: parent node from m_hParent, type from the parent's vfn 0xd0, index for 2 / 4; parent pointer, type, linked at the head of the parent's children, depth = parent's + 1 (descendants too), vfn 0x70 with 7 (0x87 for type 1). The local transform is kept: the world moves with the parent.
- **ClearParent**: off the parent's child list; depth, type and attachment index cleared; nothing marked (the abs cache keeps its last value).

## SetParent (1803ebc00 -> 180be92e0)

1. 1803ebc00: skipped when either entity has bit 9 of its +0x10 +0x30 flags; the parent's +0x1be = 0x101.
2. Same parent and attachment: nothing (with a transform: the local origin / angles / scale from it).
3. Else 180bf2480; no new parent: 180c33710, done.
4. New parent: vfn 0xd0 answers the type (0: refused); abs worked out; m_hParent, +0x7c, +0x104 set; with no transform: the parent's inverse (180bed5a0) concat its m_nodeToWorld (181476030), then 180c27ec0(origin, QuaternionAngles, scale); vfn 0xa0, vfn 0xa8 (vfn 0x70 with 7), 180c33710. The world transform is kept.
5. Unparent (180bf2480), with a parent (m_hParent or +0x7c): abs worked out, m_hParent / +0x7c / attachment cleared, m_nodeToWorld made the local transform (180188810, 180c28080), vfn 0xa0, vfn 0xa8.

180c27ec0 (marks nothing): origin lanes stored (180c26380) unless every lane is within SetAbsOrigin's tolerance; the
angles whole if a lane is 0.001 degrees or more away by 18146bd20 and they differ; the scale if past
180c00ea0(1.1920929e-5 relative, 0.001 absolute) and different.

## Spawn (180c2ae00)

- The kv origin / angles are the abs ones; m_nodeToWorld = (abs origin, scale, AngleQuaternion(abs angles)).
- Parentname resolved and no attachment (or "!absorigin"): local = the parent's inverse concat that (as SetParent), stored by 180c27ec0; with an attachment: the identity local; no parent: the abs as the local.
- "useLocalOffset" / "positionInLocalSpace" take the kv as local (the four baked maps: every uselocaloffset false, no positioninlocalspace).

## Templates and env_entity_maker

- CPointTemplate spawn (shape from 1804633f0): spawn point = the template's abs origin and angles, or another entity's; async (+0x4c4) -> nothing here. 180461810 -> 180461a00: the spawn group's transform = AngleMatrix(angles, origin) (18146bce0), the request to the engine (vfn 0x1e0 of 0x1821ba010), the spawned entities' callback.
- env_entity_maker (CEnvEntityMaker_API: ForceSpawn, ForceSpawnAtEntityOrigin). SpawnEntity (180d5c480): its entitytemplate by name (180bfc940, caller the maker); the maker's abs origin and angles, unless the origin passed isn't FLT_MAX x 3: then that origin and those angles. ForceSpawnAtEntityOrigin (180d21cb0): the named entity (with the input's activator / caller) gives its abs origin and its own abs angles. Then 180461810 with callback 180d55290; spawnflag 1: think 0.5 s on (180d3d850).
- Keyvalue parse (181373fa0): FIELD_POSITION_VECTOR -> VectorTransform (181473aa0); FIELD_DIRECTION_VECTOR_WORLDSPACE (with the flag) -> 181473a60; FIELD_QANGLE_WORLDSPACE (with the flag) -> MatrixAngles(ConcatRotations(m, AngleMatrix(angles))) (18146bb60, 18146fe70, 181471990 -> 181473410); FIELD_QUATERNION_WORLDSPACE (with the flag) -> 1814750b0, ConcatRotations, 1814742a0. The node's abs origin / angles (+0xc8 / +0xd4) come out of it.
- Transform flag (1813762d0): `flag = !181472f90(identity 0x181785c10, the matrix, 1e-5)`. Positions are always transformed; angles / directions / quaternions only when the spawn rotation isn't the identity (a template at angles near 0 0 0 keeps each entity's angles bit for bit).
- Callback 180d55290: no entity spawned: nothing. First spawned entity's handle into +0x4c0 / +0x4c4, its abs origin into +0x4c8; maker mins all 0: they and the maxs become that entity's collision bounds (vfn 0x228 +0x40 / +0x4c through 180cea8c0, or its abs origin without collision) less its abs origin. Then OnEntitySpawned (FireOutputInternal) with the maker as activator and caller. Then, postspawnspeed != 0, every spawned entity whose m_nActualMoveType isn't NONE: direction = postspawndirection, plus with postspawninheritangles the abs angles of the maker's parent (1803d9790) or the maker's own; AngleVectors; `v = forward; v + (right r0) var; v + (forward r1) var; v + (up r2) var`, each r a RandomFloat(-1, 1) off the global stream, var = postspawndirectionvariance; inlined VectorNormalize (length `sqrt((z z + y y) + x x)`; out of [1e-17, 1e17] 1814738b0, 0 -> 0); x speed; VPhysicsGetObject -> body vfn 0x208 (AddVelocity), else SetAbsVelocity.
- The global stream is tier0's CUniformRandomStreamImpl, seeded from the clock (GenerateDefaultRandomSeed); every server system draws from it.

## Kill and removal

- InputKill (180cc4dd0 -> 180cfce50): the owner told (its vfn 0x3b8 with this, then this's vfn 0x1b0(0)); a player (vfn 0x558): a kick through the engine (vfn 0x308 of 0x1821ba010, reason 0x27); else UTIL_Remove on this entity alone.
- InputKillHierarchy (180cc4e40): every child first, each through 180cfd4c0 (the same walk on its children, then the owner notice and UTIL_Remove), then itself.
- UTIL_Remove -> 18138a3e0: no instance pointer: freed at once (181385050); flag bit 11 -> 181380c50; else bit 9 set and queued (18137c770), run by 1813829c0.
- 1813829c0: each batch through the game entity system's vfn 0xb8 (UpdateOnRemove per entity), then vfn 0x80 per entity, the name table's swap-remove (18138b030), the free.
- UpdateOnRemove (180d18f80): children (1803d7360) from the last: m_iEFlags bit 9 set -> SetParent(null) (unparented, keeping the world place); the rest -> "Warning: Deleting orphaned children of %s" and UTIL_Remove. A plain Kill takes the children with it, except bit 9 ones.
- m_iEFlags bit 9: a sweep of every store to +0x414 with an `or` / `bts` of bit 9 in the 8 instructions before finds only 180d130a6 (CBasePlayerPawn vfn 0x48); no immediate store sets it (the datamap 0x181ddfc60 could on a restore). Only a player pawn has it.

## Dynamic body pose push (VPhysicsUpdate)

No per-entity VPhysicsUpdate virtual on this path: the physics game system pushes every moved aggregate's pose onto its node after the step.

1. SimulateFrame steps the world (IVPhysics2World vfn 0x80 with the system's +0x480 list as output), then PushDynamicTransformsWorker (threaded when 0x181ff5760 +0x58 is set, else serial) over the list: each entry with a node and its vfn 0x40 not 2 -> 1805c9530.
2. 1805c9530: nothing unless the node's m_nHierarchyType is 0, body 0 (aggregate vfn 0xc0(0)) has motion vfn 0x20 == 2 (dynamic), and the aggregate's body count (vfn 0x48 -> +0x18) <= 1.
3. The body's transform (body vfn 0x1b0 GetTransform; 1803c3520); abs worked out if stale; scale replaced by the node's abs scale (+0xe0).
4. Bind-pose undo: correction starts as the identity (18017ca50); when the node's aggregate has exactly one body and the body-to-bone map (180cab2d0) gives a bone for body 0, correction = that bone's model-space bind (180cab6e0) and `pose = ConcatTransforms(pose, inverse(correction))` (181476300, 1805c08e0, 181476030: renormalized); no bone and scale 1: the pose as it is.
5. SetWorldTransform(node, pose) (180c28110). After it, an aggregate of more than one body (a ragdoll) marks the node vfn 0x70(0x80).

SetWorldTransform (180c28110):
1. m_nodeToWorld (+0x10..+0x2f) = the transform (its quaternion as it is); 180bf1670 splits it into the abs.
2. Old local kept; a root: 180c28080 (180591730 the scale, QuaternionAngles, 180187f50 the position) through 180c27ec0; a child: the parent's abs if stale, the inline inverse, ConcatTransforms(inverse, transform), split and stored by 180c27ec0.
3. Flags, old local vs new: origin 1 when a lane fails 180c00ea0(old, new, 1/256 / g_flConfigMaxCoord, 1/256); angles 2 when a lane fails 18146bd20(old, new, 0.001); scale 4 when 180c00ea0(old, new, 1.1920929e-5, 0.001) fails. No flags: +0xf4 = 0; else vfn 0x70(flags | 0x100) (the jmp at 180c285cd).

Push list (vphysics2): SimulateWorlds runs each world's vfn 0 per substep, then vfn 8 with the list. vfn 8 walks the
changed set: an object whose vfn 0x180 says awake goes into the awake set (1800698e0) and, if new, out list 0; one
asleep is removed (1800696a0) to list 1; then every object in the awake set goes to list 2 (read by the worker); the
changed set is cleared. vfn 0x180 is asleep when every body's vfn 0x408 says so (RnBody +0x249 bit 2, rubikon's
Flags249 & 4). An aggregate is pushed every tick it is awake after the step, not in the step it falls asleep in.

## Body-to-bone map

- 180ca8eb0: cleared; with a model and an aggregate, 1814a7b50: nothing unless the skeleton has bones (1814a2710); per part (hashes) the skeleton bone of that hash (18149ed00), and the reverse map bone -> part.
- 180588af0 (behind sv_phys_animated_hierarchy): the entity's m_nodeToWorld with its scale lane 1, through 180cab6e0 with body 0's bone.
- 180cab6e0: without a model the input; else bones set up (180ca5f30(node, 0xfffff)), acc = the bone's local CTransform, for each parent (1814a30a0) `acc = Concat(parent's, acc)`, then `Concat(input, acc)`.
- Model data (ze_dark_souls bake): brush models have no skeleton bones (pose as it is); the 66 stock weapons put their one part on `weapon_offset` (no offset, a near-identity turn) under the root `weapon` (the model's offset: AK (2.97, -0.19, 2.98), M4 (18.2, -0.19, 12.4)), so a dropped weapon's body sits that far from its entity; m_indexNames / m_indexHash are placeholders ("0", 0).

## Unread

- The node origin / angles keys' field type (taken as the position vector and the world-space QAngle).
- 180ca5f30's bone setup for a dropped weapon (taken as the reference pose: m_bonePosParent / m_boneRotParent, scale 1); the body's placement at creation (1809ff9b0 -> 180d0f2c0).
- Attachment and bone parents (types 2, 4; SetParentAttachment), type 1's bone-merge follow; +0xe9 / +0xea.
- Whether a map sets a session max coord (Worldsize_SetSessionMaxCoord) that SetAbsOrigin's tolerance reads.
- CPointTemplate's own placement beyond 180461810; 180d55290's spawnflag 2 space check; 180d3d850; 1813829c0's queue.
- The classes' inputs (1813ac4d0) family by family.
