# CS2 shots on players, traced from server.dll 2026-11-05 (RUST_PORT phase 3)

How a bullet meets a player, what its damage becomes, and how the server rewinds players for it. Addresses are
server_20261105.dll in the Ghidra project; "f32" means the binary works in single floats at that step (the JS uses
Math.fround there). Penetration itself is docs in src/cs2web/penetration.js (FireBullet 180a78120, segments 180a75640,
the walk 180a74900 / 180a97a80).

## 1. The bullet trace reaches the hitboxes

- **FireBullet `180a78120`** builds the bullet filter (interacts-with `0x1c300b`, the shooter and its owner as skip
  entities, flags `0x49 | 2`), sets the global `DAT_182173b20 = 1` (FireBullet is tracing: the hitbox debug log
  checks it) and calls **`180a713e0`**, which runs the interval trace.
- **CGamePhysicsQueryInterface::TraceLineIntervals `180c2ea80`**: the physics world's intervals (vfn `0x520` on the
  world: vphysics2 CastRayIntervals), then, **if the filter's interacts-with byte has bit 1 (the hitboxes layer)**,
  `180181520(CHitboxSystem, out, start, delta, filter, 0, set)` adds the hitboxes' intervals and `180bdb980` sorts
  all of them (0x38-byte entries) by distance. So hitboxes are not in the physics world: the hitbox system adds them.
- **CHitboxSystem intervals `180181520`** (the singleton `*181e146a0` = `181e14cf0`, vtable `18191bcd8`):
  `18018e630` walks an AABB tree of entities that have hitboxes (`param_1+8`) along the ray (radius 1.0, zero
  extents) into a candidate list; for each candidate entity whose hitbox component is live (`+0x88` table,
  `DAT_181d9f830`), the query filter is asked (`DAT_1823ab5c0` vfn `0xe8` -> filter vfn `0x28` with the entity's
  collision attributes, entity vfn `0x2a8`), then the system's vtable slot 0 does the entity.
- **CCSHitboxSystem slot 0 `180a385c0`** (one entity): slot 1 (`180a37900`, below) finds the hitbox the ray hits
  from the start; then that one hitbox's shape (`18149c820`) at the transform the hit stored (`trace+0x30..0x4f`,
  `180188810`) is cast **backwards** from the ray's end (`start + delta`, direction `-delta`, the sign bit flipped
  with `DAT_1817805b0`) through `DAT_1823ab5c0` vfn `0x168`. Exit fraction = `1 - back fraction`, or 1.0 when the
  back cast misses (the ray ends inside). Two entries go out (`180a3ef00`): the entry (`+0x32` byte 0) at the forward
  fraction and the exit (`+0x32` byte 1) at the exit fraction, both `+0x33 = 1`, with the hit point, the hitbox
  pointer, the bone index (`trace+0xb8`), the entity handle and the surface's index (`*(trace+0) + 0x10`).
  **One hitbox per player per bullet**, entered once and left once.

## 2. Which hitbox: CCSHitboxSystem::TraceShapeAgainstHitboxes `180a37900`

- The entity's model (vfn `0x1b8`, `+0x270` -> vfn `0x60`: the skeleton instance) gives
  **GetHitBoxListAndTransforms `180cacd40`**: the hitbox set named by the skeleton's `m_nHitboxSet` (`+0x3bc`,
  `1814a6a20`, the name hashed MurmurHash2 seed `0x31415926`, `180199b90`) and each hitbox's world transform
  (0x20 bytes: position + w, quaternion). The transforms come from, in order: the lag-compensated list
  (`skeleton+0x400`, set by BacktrackPlayer, when its count matches), the skeleton's 4-entry render-time history
  (`+0x3f8`, `180caeae0`, at `curtime - (t[i] - t[i-1]) + 1/64`), else **CSkeletonInstance::GetTransformsForHitboxList
  `180caefb0`** (the current pose).
- **The shape, `18149c820`**, from the CHitBox (modellib): `+0x00` name, `+0x08` surface property name, `+0x18`
  m_vMinBounds, `+0x24` m_vMaxBounds, `+0x30` m_flShapeRadius, `+0x38` m_nGroupId (the hit group), `+0x3c`
  m_nShapeType, `+0x48` the hitbox index. Shape type 1 = sphere (centre mins, radius; query shape 1, or 0 with radius
  0), 2 = capsule (mins, maxs, radius; query shape 3), else box: a point when mins == maxs (query shape 0), else the
  mins / maxs box in bone space (query shape 2, an OBB once transformed). Each is cast with the ray through
  `DAT_1823ab5c0` vfn `0x168(out, ray, start, delta, shape, transform)`.
- **The pick** (180a37900 differs from the base `CHitboxSystem::TraceShapeAgainstHitboxesDefault 1801a82b0`, which
  takes the nearest): every hitbox hit with fraction < the trace's fraction goes to a bucket by hit group, the
  bucket keeping the nearest (`<=`: an equal fraction later in the set replaces it):

  | bucket | 0 | 1 | 2 | 3 | 4 | 5 | 6 |
  |---|---|---|---|---|---|---|---|
  | hit groups | head 1 | stomach 3 | chest 2 | neck 8 | arms 4, 5 | anything else (generic 0) | legs 6, 7 |

  The head bucket is dropped when the stomach's or the chest's fraction is strictly less than the head's. The result
  is the first filled bucket in order 0..6. **Not the nearest hitbox**: an arm in front of the chest gives the chest.
  (src/cs2web/sim/hitboxes.js pickHitbox.)
- The trace gets: the surface (the hitbox's `m_sSurfaceProperty` MurmurHash2'd, looked up through
  `DAT_1823ab5c0` vfn `0xb8` -> `+8`), `m_pHitbox` (`+0x10`), the hit point `start + delta x fraction`, the bone index
  (`+0xb8`, `1814a0130`), contents = the entity's collision contents | 2, the entity handle. A start-solid hit
  (`+0xbb`) gets normal (0, 0, 1) and offset 0.
- `TraceShapeAgainstHitboxesDefault 1801a82b0` (also skips hit groups in the entity's `m_bvDisabledHitGroups`,
  `180b52c10`) is used by FireBullet only for violence_hblood's blood trace (`180a78fb9`) and by a ragdoll decal
  (`180539760`), not for damage.

## 3. The player models' hitboxes (lasers-bake --hitboxes -> web/public/ze-fx/hitboxes.json)

`agents/models/ctm_sas/ctm_sas.vmdl` (VRF `Model.HitboxSets`, the model's MDAT `m_hitboxsets`): set **"cstrike"**,
19 hitboxes, **all capsules (shape 2), all surface "playerflesh"** (m_nameHash 242403237; penetration.json: 0.9,
'F', the same as "flesh"):

| hitbox (= bone) | group | radius | | hitbox | group | radius |
|---|---|---|---|---|---|---|
| head_0 | 1 head | 4.3 | | leg_upper_l / _r | 6 / 7 | 5.0 |
| neck_0 | 8 neck | 3.5 | | leg_lower_l / _r | 6 / 7 | 4.0 |
| pelvis | 3 stomach | 6.0 | | ankle_l / _r | 6 / 7 | 2.6 |
| spine_0 | 3 stomach | 6.0 | | hand_l / _r | 4 / 5 | 2.3 |
| spine_1 | 2 chest | 6.5 | | arm_upper_l / _r | 4 / 5 | 3.3 |
| spine_2 | 2 chest | 6.2 | | arm_lower_l / _r | 4 / 5 | 3.0 |
| spine_3 | 2 chest | 5.0 | | | | |

The ends (bone space) and their exact float bits are in the JSON. **`characters/models/ctm_fbi/ctm_fbi.vmdl` and
`characters/models/tm_phoenix/tm_phoenix.vmdl` (ZR's example classes) have an empty `m_hitboxsets`**: what CS2 hits
on a pawn wearing one is not known (TODO: GetHitBoxListAndTransforms returns 0 for a model without the set, and
180a37900 logs "%s has no hitboxes"; whether CS2 swaps in a default set, or such a pawn really can't be shot, needs a
look at SetModel / the animgraph's model or a test on a real server).

**In use since 2026-11-10** (sim/src/combat/hitbox.rs, section 8): the server loads ctm_sas's set and casts it as
CS2 does (since 2026-11-11 one set per model: 3b). **The pose since 2026-11-10** (server/cs2web/combat/poses.js): the bones' world transforms per player per tick come
from the server running CS2's player anim graph (worldmodel.vnmgraph and the graphs it references, the parameters
ReflectPawnState feeds it: world/anim-graph/params.js), composed down the skeleton's parents and placed by the body
yaw at the origin (the head at 64.08 u standing, 47.03 ducked, still); the lag record keeps them (180ed9330's
transforms, at most 32) and the rewind blends them by 180cb4090 (section 5). **Still a stand-in**: the graph runtime
is a port of Esoterica's (what CS2's NmGraph comes from), not checked against animationsystem.dll; where in CS2's frame
the server evaluates it isn't traced (here: after the tick's moves, before the record).

### 3b. A set per model: GFL's ZR class models (traced 2026-11-11; server/cs2web/combat/hitbox-sets.js)

**Where the list comes from.** GetHitBoxListAndTransforms `180cacd40(skeleton, list*, transforms*, setHash)`: no
model (`skeleton+0x1c0` -> the model handle null) returns 0. The set's name hash is the argument, or with 0 the name
`1814a6a20(model, skeleton+0x3bc m_nHitboxSet)` hashed (`180199b90`, MurmurHash2 seed `0x31415926`). **`1814a0e00(model,
list*, skeleton+0x308 the mesh group mask, hash)`** fills the list: it walks the model's meshes (`model+0x70` count,
`+0x78` the meshes, `+0x90` each one's group mask), takes those whose mask ANDs with the skeleton's, and in each its
hitbox sets (`mesh+0x174` the count) by the hash; an open-addressed table keyed on the hash (`(h >> 16 ^ h) x
-0x7a143595 ...`) tracks what was taken (TODO: its join when several shown meshes carry the set was not read to the
end; in GFL's pack every mesh of a model carries the same-sized "cstrike" set, lasers-bake --zclass
`hitboxSetsByMesh`). The count returned is the list's; the transforms are the lag-compensated list (`skeleton+0x400`)
when its count equals the list's, else the render-time history (`+0x3f8`), else the current pose (180caefb0). **Nothing
substitutes a default set, pads a short one or special-cases a count**: a model's set is used as it is, a model
without the set gives 0 and its callers skip the entity (180a37900 logs "%s has no hitboxes").

**Every caller of 180cacd40** (tools/re/game/callers.py; 9):

| Caller | What |
|---|---|
| `180a37900` | CCSHitboxSystem's trace (section 2): FireBullet's hitboxes |
| `1801a82b0` | TraceShapeAgainstHitboxesDefault: violence_hblood's blood trace, a ragdoll decal (section 2) |
| `180ed9330` / `180edebe0` | the lag record's transforms / StartLagCompensation (section 5) |
| `1802c1020` | CCSBot::ComputePartPositions (cs_bot_vision.cpp): with 0 hitboxes every part is `1802c9d40`'s point; else the hitboxes of groups 0..5 mapped by the table `1817b2518` to 4 parts, each box's centre (`18149c820`, `18157f4e0`). CS2's own bots only |
| `180189050` | CHitboxSystem: an entity's hitboxes against a sphere (`18017cbc0(centre, radius)`), skipping `m_bvDisabledHitGroups` (`180b52c10`), the nearest per group; from `180bb7e20` <- `180b9c320` (a parts / "Disabled" system, not the pawn's damage) |
| `180b9eaf0` | (owner+0x60's entity, out*, hit group): the bounds of that group's hitboxes (boxes by 1814759f0, spheres / capsules by centre +- radius); from `180b94bf0` <- `180bb90b0` (five groups) |
| `180ba1a10` | debug draw of an entity's hitboxes (a colour per group from `181936700`, `180d59c20`); from `180ba4b50`, the entity's debug text ("Health: %d, collision group: %d, nav ignore: %s") |
| `180ca9a20` | list -> `180ca9c60` (colour bytes, a duration): a debug overlay; from `180184bb0` and `180baac70` (sv_debug_overlays_broadcast / ScriptDebugDraw's callers) |

Also read: `180d1d630` (a debug command timing `180181520`: "Traced intervals in %.3fus"), `180cbd2b0` (the skeleton's
4-entry render-time hitbox history, +0x3f8, through 180caefb0). So a player's hitbox set matters to **bullets (and
their blood / decals), the lag record, CS2's bots and debug drawing**; grenades, the knife, +use and triggers never
read it.

**GFL's models** (workshop 3160448201; `web/public/ze-players/<key>/<key>.json` `hitboxSets.cstrike`):

- **The 8 zombie models**: 19 capsules, all "playerflesh", in ctm_sas's order and groups. zombie_chris_walker's are
  ctm_sas's; zombie_cultist and zombie_frozen differ in head_0; zombie_basic, ghoul_soldier, marauder and
  skeleton_bloody_lp in head_0, neck_0, pelvis, spine_0..3, the ankles and the arms (zombie_basic: the head capsule
  (-1.24, -0.07, 0)-(2.95, -0.91, 0) r 4.3 against ctm_sas's (-1, 1.8, 0)-(3.5, 0.2, 0) r 4.3; spine_1 r 4.5 against
  6.5; spine_2 5.5 against 6.2).
- **classic_zombie** (the headcrab zombie): its group-1 box is named and boned **"fake_neck"** (a (4.92, 3.93,
  0.99) b (2.22, -4.70, 0.99) r 4.2), a bone of its own: parent spine_3, bind pose (8.00204, -1.03499, -0.0000064)
  q (-2.9e-7, 2.6e-6, 0.1217463, 0.9925613) (bits 4100085c bf847a90 b6d6f198 / b49e2c8a 362d0f4f 3df95621 3f7e187f;
  neck_0's is 6.5152 along spine_3 with the same turn); its child fake_head carries no hitbox; no head_0 box. Its
  constraint list (m_modelInfo's BoneConstraintList) is the one every model of the pack has (2 CBoneConstraintDotToMorph,
  a CTiltTwistConstraint on head_0, a CPointConstraint on neck_0 + head_0, 2 CAimConstraint on the scapula helpers):
  none of its own that could drive fake_neck (the slaves' names aren't in the KV3 the bake reads: an inference from
  the lists being equal). The server poses fake_neck at its bind pose under the posed spine_3
  (hitbox-sets.js `bindPose`), which is what CS2 does with a model bone the graph's skeleton (the stock .vnmskel)
  doesn't have: section 3c.
- **The 12 human models** ("nohitbox" in 11 names, and `vector`): **one capsule**, "ankle_l" on the bone ankle_l
  (tifa's: "ankle_L"), group 6 (the left leg), radius 2.6, "playerflesh"; five different capsules across the pack
  (e.g. master_chief: (-1.82, -4.26, -0.81)-(6.32, -0.17, -0.38)). By the trace above CS2 uses it as it is: a bullet
  hits such a human only on that ankle (hit group 6, the left leg), the lag
  record keeps one transform (a change of the count, 1 <-> 19 at an infection, clears the older records:
  180eda860), and everything else about the pawn (its collision box for the knife's TraceShape and for movement,
  the "spine_1" bone of the backstab test, grenades) is untouched. That is what the pack's name says it is for:
  teammates' bullets pass through a human's body instead of stopping in it (section 6: a teammate's hitbox costs the
  bullet damage and penetration).

**In use since 2026-11-11**: the sim holds a set per model (`ze_hitbox_set(id, ...)`, sim/src/combat/abi.rs) and a
bullet's player names its own (`ze_bullet`'s player word 7, `HitboxPlayer::set`); the server registers ctm_sas's as 0
(a player with no class model, or a class model that isn't baked) and one per `CLASS_MODELS` key, poses each
player's own set's bones (poses.js: `poseInput().set`) and records that many transforms. The knife's "spine_1" is the
victim's set's hitbox index, or, for a set with no hitbox on it (the one-box humans), the bone itself carried after
the hitbox transforms (`ze_lag_record`'s word 14 bit 8, `lagcomp::Record::spine`: CS2 reads the bone cache, not the
hitbox list). Checked by `node web/server/cs2web/combat/hitbox-sets-test.mjs` (a grid of 7,889 rays a model on one pose:
zombie_basic differs from ctm_sas on 504 from the front, among them head shots on ctm_sas that are chest hits or
misses on it, and from the side a head shot on zombie_basic that misses ctm_sas; a one-box human is hit below 4 u
only; an infection in place switches sets; the spine test on a one-box human).

## 3c. A model bone the graph's skeleton lacks: classic_zombie's fake_neck (traced 2026-11-12)

**What CS2 does: the bone stays at the model's bind pose (its parent-relative position, rotation and scale from the
model's skeleton), under its animated parent.** That is what the server does (hitbox-sets.js `bindPose`, poses.js),
so the hitbox on it is no longer a stand-in. Addresses are `server_20261105.dll` (CSkeletonInstance is
src/game/shared/skeletoninstance.cpp there); the skeleton instance is `sk`, its model `*(*(sk+0x1c0))`.

| | |
|---|---|
| `180cb9bd0` | the model state's set-up for a model (`this` = sk+0x120; 6 callers, the model-change paths): both poses sized for the model (`1814a4420(pose, model handle)` on sk+0x130 and sk+0x160), the per-bone flags rebuilt (sk+0x1e8, 4 bytes a bone, from `1814a3040(model, bone)`), vfn 0x78 (`180cb7d10`: sk+0x410 = 0, the animation pose's valid mask cleared by `1814a4780`), then `180cb7d80` |
| `180cb7d80` | **both poses filled with the bind pose**: `18149f440(model+0x130, 1.0, count, data)` on the animation pose (sk+0x130) and the parent-space pose (sk+0x160) |
| `18149f440` | (model skeleton, scale, n, out): a bone's 0x20 bytes = position `m_bonePosParent` x scale, then the bone's scale x scale, then the quaternion `m_boneRotParent`. The model skeleton (model+0x130): +0x48 the bone count, +0x98 positions (12 bytes a bone), +0xb0 quaternions (16), +0xc8 scales (4) |
| `18149f1e0` | (model skeleton, out, bone): one bone's bind pose from the same arrays (a bad index gives the identity at `182337e70`) |
| `180b44f00` | the anim graph controller after its graph ran (the graph instance at controller+0x410, its result poses at instance+0x108 -> +0x47d8): `180cb69b0(sk, pose)` for the pawn's own skeleton and for each secondary skeleton (controller+0x38 count, +0x40 handles) |
| `180cb69b0` | **the graph's pose into the model's bones**: `map = 18149ee90(model, pose's skeleton)`; for each model bone i < map.count: `j = map.bones[i]`; **`j >= 0` copies the pose's transform j (0x20 bytes, pose+0x10) into the animation pose's bone i; a negative j leaves bone i as it is**; then every bone is marked valid (`1814a4750`: the mask set to all ones). The float channels go the same way through a second map (entry+0x38 count, +0x40) |
| `18149ee90` | (model, graph skeleton): the model's list of maps, one per graph skeleton it names (model+0x440 count, +0x448 entries of 0x50 bytes; an entry's +0 -> the skeleton's handle), searched by the skeleton's pointer; returns entry+8: +0 the count, +8 `int*` (model bone -> the graph skeleton's bone). `1814a19a0` / `1814a1a30` read the same list |
| `180ca5f30` | CSkeletonInstance::CalcAnimationState (line 0xd5b): the bones wanted (flags sk+0x1e8 against the mask) and not valid in the animation pose; a sequence decode is added and run (`g_pAnimationSystem` vfn 0x68) only when the controller's (sk+0x3c0) vfn 0xd0 is neither 2 nor 3 (CBaseAnimGraphController's AddAnimationDecode, vfn 0xa8 `180b78a90`, adds one for mode 1 only, through the callback `18195a0e0`: `180ca3ca0` / `180ca3c20` -> `1814a4110` / `1814a4030`); then `1814a47a0` ors the wanted bones into the valid mask. **With a graph (modes 2, 3) nothing is decoded: a bone nobody wrote is marked valid with what the buffer holds** |
| `180ca4490` | the parent-space pose (flags sk+0x414, mutex sk+0xf8), a bone at a time: an override interface when set (sk+0x3d0, setter `180cb7ff0`, 3 callers; vfn 0 returns 0 none / 1 a parent-space transform / 2 a model-space one), the bone-merge list (`180c01760` / `180c01740`, 0x30 bytes an entry), a physics body's transform when the bone has one (entity vfn 0x1f0 -> `180b55670`, its bone -> body map by vfn 0x90: -1 there gives the bind pose by `18149f1e0`), else **the animation pose's bone copied** (`180cab630` -> `180ca5f30`) |
| `180ca6840` | the world-space bones (the bone cache sk+0x1a0, flags sk+0x418; the knife's caller in section 7): parent = `1814a30a0(model, bone)`, world = `181476030(parent's position, parent's rotation, local position, local rotation)`; a root bone takes the skeleton's own transform (sk+0x10 .. +0x2c, plus `180cab450`'s offset) |

So for classic_zombie: its vmdl names the stock graph and skeleton like every model of the pack
(`animation/graphs/worldmodel/worldmodel.vnmgraph`, `animation/skeletons/characters/worldmodel.vnmskel`: the strings
in classic_zombie.vmdl_c, tools/re/game/vpkgrep.py), the stock skeleton has no fake_neck, so its map entry is negative
and `180cb69b0` never writes it: fake_neck keeps `180cb7d80`'s bind pose (the bits in section 3b) from the moment the
pawn gets the model, `180ca4490` copies it to the parent-space pose and `180ca6840` puts it under spine_3's animated
world transform. No constraint drives it (3b: the constraint list is the pack's common one).

In `animationsystem_20261023.dll`: `1804ac9f0` is `18149ee90`'s twin (its one caller `18007c410`), `1804ac0e0` a
pose's reset (the bind pose by `1804acdd0(model+0x130, n, data)`, every bone valid).

**Unread**: the function that fills a model's map (which model bone is which graph bone). Nothing in server.dll or
animationsystem.dll reaches the list through model+0x440 / +0x448 but the readers above (a raw scan of both for
those displacements), so it is built through another pointer. That a bone the graph's skeleton lacks gets a
negative entry is read from the copy's `>= 0` test and from there being no index it could hold; that the match is by
bone name is an inference. Also unread: `1814a4420` (the pose's allocation) and where the bone constraints run.

## 4. Damage (src/cs2web/sim/damage.js; checked by `node web/src/cs2web/sim/damage-test.mjs`)

The pawn's OnTakeDamage (vtable `181794998`, slot 128 `180b670b0`) -> slot 254 `180adb1f0` -> the damage services'
(`pawn+0xe60`) **`180a93f70`**, in this order:

1. **The hit group, `180a89430`** (when the info has a trace, `info+0x68`). Hit group = `trace->m_pHitbox+0x38`
   (`180cacf80`), stored +1 at `pawn+0x14fc` (m_LastHitGroup). `damage = info+0x44` (f32):
   - head (1): `headshot x damage x mp_damage_scale_<team>_head`, headshot = the weapon vdata's
     **m_flHeadshotMultiplier (`+0x824`)**, 4.0 (`DAT_18179be70`) without a weapon. Same damage with or without a
     helmet; the helmet only decides the victim's aim punch and the flag `info+0x65`.
   - stomach (3): `(float)((double)damage x 1.25) x _body`; chest (2) and neck (8): `x _body`; arms (4, 5): `x _body`
     (no other factor); legs (6, 7): `(float)((double)damage x 0.75) x _body`; generic (0) and others: unchanged.
   - `<team>`: the victim's team 3 (CT) reads `mp_damage_scale_ct_head` / `_ct_body` (`182119e38` / `e28`), anything
     else the `_t_` pair (`e58` / `e48`); all default 1.0.
   - `mp_damage_headshot_only` (`182119e20`): a DMG_BULLET hit off the head does 0 (TODO in damage.js).
   - The victim's aim punch: `mp_flinch_punch_scale` (`182173ac0`) x constants (-0.1, -4 floor; head without helmet
     -0.2 / -12 and a `RandomFloat(-1, 1)` yaw off the global stream clamped to [-9, 9]; chest / stomach / neck
     -0.005 armored, -0.033 not), `180a3f3d0`. Not ported (the global stream isn't on the replicas).
   - The damage force x `phys_playerscale` (`182173ad0`), on a headshot also `phys_headshotscale` (`182173ae0`)
     and flag `0x80000`; 0 for a grenade's head hit. Ragdolls only.
2. listeners; `healthshot_healthboost_damage_multiplier` while boosted (`180ac60b0`).
3. **Friendly fire, `180a89230`**: `ff_damage_reduction_bullets` / `_grenade` / `_grenade_self` / `_other`
   (`1821738c0` / `8a0` / `8b0` / `8d0`) on teammates; 1.0 for an enemy. ZE: mp_friendlyfire 0, teammates take none.
4. gamerules `180231840`.
5. **Armor, `180a88f30`**, for damage type 0 or `& 0xc6` (bullet 2, slash 4, blast 0x40, club 0x80) unless
   `info+0x70` bit 18:
   - **IsArmored `180ad24c0`**: armor (`pawn+0x1514`, m_ArmorValue) > 0 and hit group generic, chest, stomach, arms,
     neck; head only with a helmet (`ItemServices(pawn+0xb18)+0x49`, m_bHasHelmet); **legs never**.
   - `ratio = m_flArmorRatio (vdata +0x828) x 0.5` (0.5 without a weapon; **a blast whose 180a7ab50 lookup finds no
     weapon takes weapon_hegrenade's vdata**: the planted C4's RadiusDamage); `bonus = 0.5` (**1.0 for any blast**:
     gamerules vfn `0x110` is CCSGameRules' 180e83b50, `return 1`; c4-shockwave.md "Armor for the C4"); `health =
     damage x ratio`; `armorDmg = (damage - health) x bonus x (20 for DMG_BURN 8, else 1)`, all f32. Info+0x70 bit 18
     (0x40000: the C4 shockwave's hit) skips the whole step.
   - `armorDmg <= armor`: `armorDmg < 0` -> 1; `armor -= (int)armorDmg`. Else `health = damage - armor / bonus`,
     `armorDmg = armor`, `armor = 0`. `info+0x44 = health`; `dmg_armor = (int)armorDmg` (services `+0x4c`); when the
     armor took damage and `180b5d1e0(pawn)` holds, item_kevlar and item_assaultsuit go through `180a998f0` on the
     item services (`pawn+0xe40`: not read further, probably dropping them from the inventory once the armor is gone).
   - No heavy-armor branch in this build.
6. `buddha` cvars (debug).

Then **CBaseEntity::TakeDamageOld `1803ed610`** (CS2Fixes' signature): `result.m_flDamageDealt (+0x20) =
info.m_flDamage`; after OnTakeDamage: `lost = floor(dmg)`, `carry = (dmg - floor(dmg)) + m_flDamageAccumulator
(entity+0x2dc)`; `carry >= 1` -> `lost += 1, carry -= 1`. Then the **TakeDamageFlags** (traced 2026-11-11): the
info's +0x70 has the entity's m_nTakeDamageFlags (+0x2e8) or'ed in at 1803edad5; 180fba770 builds the result (+0
the info, +0x18 m_nHealthLost = cvttss2si(incoming damage), +0x1c the health before (180cf7020), +0x20 / +0x38
m_flDamageDealt = the incoming damage, +0x48 = the info's flags). At 1803edb3f: flag 0x1 (DFLAG_SUPPRESS_HEALTH_CHANGES)
without 0x10 skips vfn 0x408 and the whole loss. At 1803edc30 (from the result's +0x48 byte): **0x10
(DFLAG_FORCE_DEATH): lost = max(health + 1, cvttss2si(lost))**, else **0x8 (DFLAG_PREVENT_DEATH): lost = min(health -
1, cvttss2si(lost))**, both back through cvtdq2ps; the carry goes to the result's +0x40. `1803c4950`: `m_flDamageDealt
= lost`, `m_nHealthLost (+0x18) = min(cvttss2si(lost), cvttss2si((float)before))`; `1803e55e0` (the apply): nothing
when `flags & 0x11 == 1` (suppressed), else `entity+0x2dc = carry`, `m_iHealth (+0x2d0) = cvttss2si((float)before -
(float)healthLost)` (1803e4060 its change callback). So a 27.9 hit costs 27 and the next one 28. Ported: damage.rs
`health_loss` (job word 23 the flags, 24 applied). Who sets the flags in ZE (a map's damage) isn't traced; nothing
here passes any.

**The carry's reset**: the only writers of +0x2dc (tools/re/game/fieldwrites.py) are CBaseEntity's constructor 180cdcad0
(0), 1803e55e0 (the apply), and **CCSPlayerPawn vfn 0xaf8 180249530** (its respawn: "Player.Respawn", the health set
to the value at [181f9e120] +0x58 when above 0, else 100 (180d0e5d0 / 180d0e730), then +0x2dc = 0); the others
(18110aebe, 1813c7de2, 181487d87) are other classes' fields at the same offset. The pawn persists through an infection
(no 0xaf8), so the carry does too. Ported: server/cs2web/core/game.js spawn zeroes `dmgCarry`. Death when health reaches 0 with health before > 0 (vfn `0x418` / `0x420`).

OnTakeDamage_Alive's post (slot 255 `180adb230` -> `180a94400`) fires **player_hurt** (`180a95d90`): userid,
health, armor (`pawn+0x1514`), dmg_health (services `+0x48`, probably `m_nTotalledHealthLost`: read from
`result+0x34` in `180a88a50`, UNSETTLED), dmg_armor (`+0x4c`), hitgroup (only for DMG_BULLET, `180fca360`),
attacker, attacker_pawn, weapon, priority 6. **ZR's knockback** runs in CS2Fixes' TakeDamageOld post hook
(detours.cpp:184) with `m_flDamageDealt`: the floored damage, not clamped to the health left.

## 5. Lag compensation (player_lagcompensation.cpp)

- **Recording: CLagCompensationManager::FrameUpdatePostEntityThink `180ec7250` -> RecordDataIntoTrack `180ed95e0`**,
  per lag-compensated entity. A track is a list of 0x480-byte records (`180ed9330` fills one): flags (+0, bit 0 =
  alive), abs origin (+4), abs angles (+0x10), collision mins / maxs (+0x1c / +0x28), **tick** (+0x34 =
  `(int)(m_flSimulationTime (+0x32c) x 64 + 0.5)`), sequence (+0x38), cycle (+0x3c), +0x40, and the **hitbox world
  transforms** (GetHitBoxListAndTransforms into a CUtlVector at +0x50, 32 inline 0x20-byte transforms at +0x70).
  - Records older than `(int)((curtime - sv_maxunlag) x 64 + 0.5)` are dropped; a new one is added only when the
    newest's tick is below the entity's simulation tick; a dead entity's track is cleared (`180edaa90`).
  - **Teleport**: a record more than 64 u (squared distance > 4096, `DAT_181926a44`) from the previous one, or with a
    different hitbox count (+0x50), clears every older record (`180eda860`).
- **Rewind: StartLagCompensation `180ee08d0` -> `180edebe0`** (the command's player; not for bots, vfn `0xc20`;
  needs `sv_unlag` and more than one player). The target time comes from the command's **attack history**
  (`cmd+0x78` index into the subtick history `+0x38`): its two interpolation snapshots ("full interp info": the
  client's from / to ticks and fraction, `180ebc9c0`, validated by `180ed23a0`), the client's interp amount
  (`player+0x5a8 x 64 + 1`), clamped to `sv_maxunlag x 64` ticks back. Failing any of that it falls back to the
  **target time** (logged "using target time"). Modes: "target time backtrack", "single interp backtrack",
  "sv_interp0 backtrack", and the two-record full interp.
- **BacktrackPlayer `180ec1200`**: finds the newer and older records around the target tick, `frac = (target -
  older.tick) / (newer.tick - older.tick)` clamped to [0, 1]; origin, mins, maxs lerped `(b - a) x frac + a`
  per component (f32), angles with `1814774c0`; with `sv_unlag_fixstuck` a hull trace (mask `0xc3011`) pulls the
  origin back where it would be stuck; origin / angles set when moved more than 0.1 u (`DAT_1818e9f3c` 0.01 squared);
  animation sequence and cycle restored (cycle lerped, wrapping); **the hitbox transforms interpolated**
  (`180cb4090`: position `(1 - f) x a + f x b`, w `(b - a) x f + a`, the quaternion an approximate slerp: weight
  `f + f(f - 1)(f - 0.5) x poly(|a.b|)` with constants 0.215638, 0.848013, 1.06021, 1.0904, 1.43519, 3.2452,
  3.55645 (`181813da0..db8`), negated when `a.b <= 0`, normalised) and handed to the skeleton (`+0x400`), which
  GetHitBoxListAndTransforms then returns. The float order (disassembly): h = f - 0.5, k = (h f)(f - 1), d = |dpps(a, b)|,
  w = ((((3.55645 - d 1.43519) d - 3.2452) d + 1.0904) h² + ((d 0.215638 - 1.06021) d + 0.848013)) k + f, b w + a (1 - w)
  (w negated first when the dot <= 0), divided by sqrt(dpps(q, q)) (a zero length gives `DAT_181f4a000`, zeros in the
  file); position (1 - f) a + f b, scale (b - a) f + a. Ported as lagcomp.rs `blend_transform`: **BlendOracle +
  `blend_check`, 1,000,000 blends, 0 differ**.
- FinishLagCompensation `180ec7020` restores. `sv_lagcomp_filterbyviewangle` limits who is rewound.
- Cvars: `sv_maxunlag` 1.0 (max 1.0, `18217b4f8`), `sv_maxunlag_player` -1 (`18217b508`), `sv_unlag`,
  `sv_unlag_fixstuck`, `sv_lagcompensationforcerestore`, `sv_lagcomp_filterbyviewangle` (bools; defaults not read),
  `sv_csgo_shoot_lagcompensation_max_error` 1.0 (warns when the client's head hitbox position differs).

## 5b. StartLagCompensation's choice and the full interp (180edebe0, traced 2026-11-11 "knife-interp"; lagcomp.rs `start` / `rewind`)

Ghidra ReVa and tools/re on server_20261105. The job's target (vfn 0x10 of +0x70: CLagCompensationManager vfn 0x28's,
usercmd.md 8) is clamped by 180ec2130 twice: local_948 with the job's max unlag (param_3 + 0x10, sv_maxunlag_player
18217b508 read when it is not above 0) and local_8e0 (the pawns' target, vfn 0x568). Then:

- CUserCmd +0x78 (the attack history index): -1 or not below the command's history count (+0x30, logged "clamped
  invalid attack history index") -> the target time. **sv_csgo_shoot_use_full_interp** (0x18212b270, bool, default 1,
  flags 0x2002) off -> the target time. The entry (+0x38 list + 8 + index x 8) without has-bit 2 (cl_interp, +0x10 >>
  1 & 1) -> the target time.
- **180ebc9c0(out, src, dst, frac)** builds I0 from sv_interp0 (entry +0x28: +0x1c src, +0x20 dst, +0x18 frac; the
  default instance 0x181e0e2d8 when absent) and I1 from sv_interp1 (+0x30). **180ed23a0**: valid when -1 < src <= dst
  and 0 <= frac <= 1; either invalid: "full interp info not valid, using target time".
- **T = 1813b93b0(out, &I0, &I1, cl_interp's frac** (entry +0x20 -> +0x18, the default 0x181e0e300)): each info's time
  = (src, (float)(dst - src) x frac) folded (I1's first, then I0's), d = time(I1) - time(I0) (1813b8fb0 inline), out =
  (time(I0).tick, ((float)d.tick + d.ratio) x f) folded: time(I0)'s own ratio dropped (as 1813b9690).
- now = (gpGlobals +0x44, 0); lower = now - 1813b9230(sv_maxunlag (18217b4f8) x 64); **180ebdc90** (three-way: ticks
  -1 (0xff) / 1, equal ticks: the ratios 0xff / 1 / 0 / 0x80 unordered): T < lower -> lower; else T > now (> 0) -> now;
  else T. Not T itself (the ticks, then ucomiss on the ratios, a NaN not equal): "clamping to sv_max_unlag (%.3f),
  using target time" (180eddd80(3) rate-limits the log).
- **1813b9930(T, interp x 64 + 1)** (the controller's +0x5a8 x 64.0 + 1.0; GameTick + a float count of ticks) - the
  target (local_948), (float)tick + ratio **>= 1**: "full interp info doesn't match target time, using target time
  instead" (one-sided).
- **180ebc010** snaps I0 and I1 (|1 - frac| < 0.01: src = dst; |frac| < 0.01: dst = src); S0 = snapped I0's src, S1 =
  snapped I1's dst: **S1 - S0 == 0 -> the target time; == 1 -> the single interp backtrack** (local_res20 =
  **sv_csgo_shoot_force_full_interp**, 0x18212b280, default 0: set, the full interp instead); **anything else -> the
  full interp**. **sv_csgo_shoot_force_use_target_time** (0x18212b290, default 0) forces the target time. (Neighbours:
  sv_csgo_shoot_log 0x18212b210, sv_csgo_shoot_verify 0x18212b230 (the head check), sv_csgo_shoot_verify_on_attack_only
  0x18212b260 (1), sv_csgo_shoot_log_attack_cmds_only 0x18212b220 (1).)

Per lag-compensated player (the job's filter vfn 0, not the shooter): the target time mode (180edfacb..): local_960 -
1813b9870(lerp x 64 + 1) where lerp = 1/64 for maxClients 1, else (int)(+0x5a8 x 64 + 0.5) x 1/64 (180edf656..), then
**BacktrackPlayer 180ec1200(lc, entity, &{mode, a, b, frac}, the player's record set, restore buf, change buf, 1)** mode
0. The single interp (180edf6f4..): mode 1 with (S0, S1, cl_interp's frac), no buffers ("single interp backtrack" on a
failure). **The full interp** (180edf7d5..180edfa98):
1. mode 1 with sv_interp0's own (src, dst, frac), its change record into a 180ebc050 buffer A (one 0x470 record per
   player, indexed by the player set's +0x920) and the restore record into the player's own (+0x40); a failure (>= 2):
   "sv_interp0 backtrack", the player not moved;
2. mode 1 with sv_interp1's (src, dst, frac): the restore into a scratch buffer (the player's own restore record stays
   the unmoved one), the change into B; a failure: "sv_interp1 backtrack", 180edbbe0 restores the player;
3. **mode 2**: `param_3[2]` = A, `[4]` = B, `[6]` = cl_interp's frac: A the older, B the newer, the blend of 180ec1467
   (origin / mins / maxs `(b - a) f + a`, the angles 1814774c0, the hitboxes 180cb4090, the sequence / cycle; f <= 0
   takes A), the change into the player's own record (+0x4b0) and applied; a failure: "cl_interp backtrack", 180edbbe0.

**BacktrackPlayer 180ec1200**, the rest: no record set -> 2, an empty one -> 3; the restore record (param_5's slot or
+0x40) and the change record (param_6's slot or +0x4b0) reset (180ec2210); mode 1: from the newest, a record at dst is
the newer (src == dst: the older too, done), at src the older (done), below src: none; mode 0 as section 5. No older:
"No valid positions in history for BacktrackPlayer entity %d", 4. sv_unlag_fixstuck (0x1821e1ac0) the hull trace
0xc3011; then the restore record from the entity (+0x10..+0x30 origin, angles, mins, maxs; +0x34 the simulation tick),
the change record from the blend, the entity moved when > 0.1 u (the bits 2 / 4 / 8 / 0x10: moved, turned, resized,
the hitboxes and the animation); returns **1 when nothing changed, 0 when it moved** (the caller's `< 2` is success).

The port: lagcomp.rs `start` (the checks, `Rewind::{Target, Interp, Full}`), `rewind` (Full: two `backtrack_interp`s,
then `lerp_records`), abi.rs ze_lag_poses (17 words: 6-8 sv_interp0, 13-15 sv_interp1, 16 cl_interp's frac),
server/cs2web/combat/combat.js posesAt (the gun's press entry's `interp`), the client's infos (usercmd.md 12). Checked: cargo test
lagcomp (start_and_interp: single at 64 Hz snapshots, full at 32, the fallbacks), the browser (a press's entry carrying
[0.6559, 1902, 1904, 0.5, 1904, 1904, 0] hitting a bot). Not ported: sv_unlag_fixstuck, the angles' blend, the
sequence / cycle (the stand-in pose takes the nearer record's yaw and duck).

## 5c. Who is rewound, the angles' blend, sv_unlag_fixstuck (traced 2026-11-11 "tick64"; lagcomp.rs)

- **WantsLagCompensationOnEntity 180d1b4e0** (pawn, entity, cmd, mask): **mp_friendlyfire** (0x1821b9a88) 0 and the
  pawn's vfn 0xc78(entity) (a teammate): no; an entity whose index bit isn't in the mask: no;
  **sv_lagcomp_filterbyviewangle** (0x18217b520, bool, **default 1**, flags 0x4000) off: yes; else d = |entity abs
  origin - pawn abs origin| (1803d6f50; sqrt((dz dz + dy dy) + dx dx)); speed = the entity's (a player, vfn 0x558)
  +0xb50 (movement services) +0x1ac (m_flMaxspeed), else 300 (0x18179bea8); **sv_maxunlag x (speed x 1.5
  (0x1817a4420)) > d: yes**; else the forward of the command's view angles (180d20ee0: CUserCmd base +0x40 -> its
  +0x40 QAngle +0x18 / +0x1c / +0x20; 181470980) dotted ((fz z + fy y) + fx x) with the direction normalised
  (1e-17 / 1e17 bounds, 1814738b0 outside, 0 stays 0): **0.707107 (0x18196cdb0) <= dot** (comiss / setbe: unordered
  counts as yes). Port: lagcomp.rs `wants_lag_compensation`, abi.rs ze_lag_targets (each player's current origin,
  mover.maxSpeed, team) and words 17-22 of ze_lag_poses' job; combat.js posesAt. A player it refuses keeps their
  current pose (BacktrackPlayer isn't called).
- **The angles' blend in BacktrackPlayer** (180ec1480, LAB_180ec1467): when any of the two records' abs angles
  differ, **1814774c0(out, older, newer, f)**: AngleQuaternion (181473e90) of each, the fitted slerp with the
  constants at 0x181813da0.. (sim/src/math/slerp.rs's, instruction for instruction: q = b w1 + a w0, a zero length
  0x181f4a000 = zeros), QuaternionAngles (181475b60); equal angles: the older's. A pawn's abs angles are (0, yaw, 0):
  lagcomp.rs lerp_records' yaw.
- **sv_unlag_fixstuck** (0x1821e1ac0, bool, **default 0**, "Disallow backtracking a player for lag compensation if
  it will cause them to become stuck"): CS2 doesn't run BacktrackPlayer's hull trace by default; the port doesn't
  either (not ported, so turning it on does nothing here). sv_unlag (0x1821e1a90) default 1.

Checked: cargo test lagcomp (the_view_angle_filter), the combat suites, sim-test.

## 6. The bullet's walk (FireBullet 180a78120, traced 2026-11-10)

- **180a713e0**: the end (180a884e0: start + direction x range), the filter's bit 1 cleared for the call, then
  TraceLineIntervals with radius -1 (vphysics2's base fraction 1), the trace fraction set to 1, the segments.
- **180a75640, the segments** (0x18 each: start +0, end +4, damage +8, penetrations left +0xc, first +0x10 (15
  bits), last +0x12, solid +0x14 bit 0): an entry right after an exit within 1/512 u ((f_i - f_(i-1)) |delta|,
  |delta| from 180225130: (z² + y²) + x²; NaN not) trades places with it, the fractions staying in their slots. Air
  segments end on each entry that follows an exit, each after a solid from the last entry to the hit before; after the
  last air one a solid from its end to 1 on its entry (first = last: no thickness); a first segment that is solid (the
  ray began inside something) turns the list into a zero-length air segment and a solid to 1 on that solid's last hit.
- **180a74900**: (damage, penetration, range modifier, |delta|, 4 left as an **int**) through every segment, each
  given the damage and count after it; the one the bullet stops in gets end 1 and damage 0 and ends the list.
- **180a97a80** (sim/src/combat/penetrate.rs has every branch): air: damage = powf(modifier, (to - from) / 500) x damage
  (tier0's V_powf); a solid: 3000 / 0.1 rules, the thickness from the two intervals' end points ((dz² + dy²) + dx²),
  the least modifier first..last (minss), the material rules, then **lost = wm x (pm x 3) + chunk x damage** and total
  = (thickness² x pm) / 24 + lost, both maxss(0, x); below 1 left stops. The segment's two traces come from 180a74a20
  (an interval as a CGameTrace: start + delta f per component, +0xbb start solid = the exit flag).
- **The loop**: every air segment fires bullet_impact at its end interval's end point and, when that interval has an
  entity, queues a damage info (the segment's damage, +0x7c the solid segments before it); the infos are applied after
  the loop, in order, through TakeDamageOld.

### 6b. The audit (2026-11-16, server_20261105 / vphysics2_20260924)

Re-read from the decompile and disassembly of 180a97a80, 180a74a20, FireBullet 180a78120 and vphysics2's surface
manager; penetrate.rs matched every branch but the inputs below.

- **FireBullet's arguments** (180a78120, rbp = entry rsp - 0x28c8): xmm3 the range (the direction x it, 180a782a9..),
  stack +0x28 (rbp+0x28f0) the penetration, +0x48 (rbp+0x2908) the damage **as an int** (180a784a1 movd + cvtdq2ps:
  m_nDamage), +0x58 (rbp+0x2918) the range modifier; the walk 180a74900 gets (damage, penetration, range modifier) in
  xmm1..3 and 4 penetrations (rbp+0x3b4 = 4 at 180a7827b). The damage info's +0x7c is the count of solid segments
  before the air segment (rbp+0x2908 reused: `inc` at 180a7867e for each solid, stored at 180a791a4), its damage
  the segment's +8 (180a78fe6), type bits `| 0x20040` (180a7919c).
- **The surface** (180a97a80 lines 109-113, 180a74a20 +0x18): the interval's +0x30 short through the physics
  system's (DAT_1823ab5c0) vfn 0xb8, the surface controller, its vfn 0x18 (**vphysics2 1800729c0**: the list at +8,
  index checked 0 <= i < count, else null), then the game table **180c00e80** (surface +0x10 x 0x20 + DAT_18218e4f8
  +0x28; +8 bulletPenetrationDistanceModifier, +0x14 gamematerial). The controller is CVPhysics2SurfacePropertyManager's
  second vtable (offset 0x30, **0x1803fbe20**; the first 0x1803fbe68). Its vfn 8, **find by hash 1800729f0**: an
  open-addressed table (+0x18 slots of 0x10, mask +0x10, -1 empty, linear probe); a hit sets *found = 1 and returns
  the slot's +8, **a miss sets *found = 0 and returns +0x30 (the manager's +0x60)**, which the loader sets at
  **180073875..180073896** to the find of 0x75de364e, "default"'s m_nameHash. vphysics2 names one file,
  `surfaceproperties/surfaceproperties.vsurf` (0x1803fcb00), and pak01 holds only that vsurf_c: a map's own surface
  (and any hash the manager lacks) is "default". bullet.rs `Surfaces::get` reads a missing hash as "default"; on
  de_dust2 / de_mirage / de_inferno / ze_hold_em_p every impact's surface is in the table (penetration-test). Not
  followed: the aggregate loader's own call of vfn 8 for each m_surfacePropertyHashes entry (taken as this find).
- **The game table's order**: the bake resolves a base before its child; CS2 walks in the vsurf's order. The stock
  vsurf (2026-11-16) has one child before its base, concrete (#46, base no_decal #105), and concrete's
  surfaceproperties_game.txt entry sets both keys (0.5, "C"): no surface's values differ.
- **The teammate branch** (180a97a80 lines 200-235): the regular path unless the entry is flesh 'F' (0x46),
  **ff_damage_reduction_bullets** (handle 1821738c8, object 1821738c0, registered at 1800c5c60: default **0.1**) is 0,
  the entry trace's entity is a player (vfn 0x558), **mp_teammates_are_enemies** (handle 18211a6d8, object 18211a6d0,
  registered at 1800a3587, flags 0x282100, default 0: "When set, your teammates act as enemies and all players are
  valid targets") is 0, and the entity its handle (1813aa290 -> 180c10aa0) names is a player (0x558) with vfn 0xca8
  set whose m_iTeamNum (+0x344) equals the shooter's team (the walk's 4th argument): then the modifier is
  **ff_damage_bullet_penetration** (handle 1821738e8, object 1821738e0, registered at 1800c5bb0: default 0, max 1.0),
  0 stopping the bullet (LAB_180a97f93). So the cfgs decide it: gamemode_competitive.cfg / _competitive2v2.cfg set
  ff_damage_reduction_bullets 0.33 (a teammate's body costs what an enemy's does), gamemode_casual.cfg 0 (**a
  teammate's body stops the bullet**), gamemode_deathmatch.cfg 0.0 with mp_teammates_are_enemies 1 (regular).
  Fixed: combat.js passes mp_teammates_are_enemies, gamemodes.js carries the cfgs' ff_damage_reduction_bullets (both
  were missing: a casual match let bullets through teammates). vfn 0xca8 isn't named (a hitbox is only cast for a
  live player here, taken as set).
- **The stop branch with a debug list** (param_5, sv_showimpacts_penetration's): its constants (1.18, 2.8, 0.15) only
  fill the debug record; the damage isn't touched there (returns 1).
- **The contents** (bit 13, PASS_BULLETS): a shape's vfn 0x50 first qword (m_nInteractsAs); a hitbox's entity's
  collision property (vfn 0x228) +0x18, the pawn's m_nInteractsAs (0x40000, solid cleared: 180ae27b0, grenades.md "Players and the projectile's filter"; no bit 13, and a hitbox's flesh
  meets no material rule, so its value can't change a result).
- Checked: `cargo test -p ze-sim combat` (penetrate.rs: teammate_bodies, material_rules, cutoffs: every branch against
  the decompile's formula written out, f32 equal), penetration-test on the three competitive maps (each first wall's
  damage against the formula: one surface, PASS_BULLETS, or a lesser surface's modifier inside, none unexplained; the
  damage behind a body; teammates by the four cvar sets).

## 7. The knife (CKnife 180a2fa80, traced 2026-11-10; sim/src/combat/knife.rs)

PrimaryAttack 180a2f170 (slash, 0) and SecondaryAttack 180a2f500 (stab, 1) both call 180a2fa80:
- **Reach** 48 + 18 (slash) or 32 + 18 (stab) from the shoot position along the eye angles' forward (181470980);
  the player's lag compensation starts with reach + 128.
- **Traces**, TraceShape 180c2f3c0 with interacts-with `0xc3001` (the player layer, so a pawn's collision box, not
  its hitboxes), group 4, flags `0x4b`, object set `0xf`, the attacker's handle / owner / hierarchy id ignored:
  1. a line with the knife's filter (vtable 181916390, ShouldHitEntity 180a2f600, filter +0x20 the attacker's
     handle): no attacker entity, or the hit entity the attacker, returns false; else the hit entity's **vfn 0x350
     (180cfb4b0, every class's: InSameTeam(other))**: other non-null and 180492250(this m_iTeamNum +0x344) ==
     180492250(other's) (180492250: g_Teams[team], null for a team outside the list) -> true, refused. So the first
     line passes through the attacker's teammates. Ported (knife.rs `Pawn.teammate`, the pawn word 4 bit 2); a map
     entity's team is taken as 0 (never the attacker's 2 / 3; a TeamNum key isn't read);
  2. if that missed or hit no pawn: the same line with a plain filter (rbp+0x340, built at 180a2fead);
  3. if that missed: spheres (TraceShape 180a30058 with the plain filter, its 5th argument rbp+0x340) of radius 14, 11, 8, 5, 2 (18048a430 / 180530ae0) to `end - fwd x radius`, each kept
     while it hits, the first miss ends it. vphysics2's sphere casts: the world's CastShape type 1 (1801f5770: a ray
     at radius <= 1e-6, else the clip, the trees, the walk 1801d9dc0), a mesh's vfn 0x20 (180242750 -> 180247c30,
     swept sphere against each triangle 1803157c0 / 180315820) and a hull's (180250b20 -> 180253ac0, GJK): ported in
     sim/src/rn/sphere_tri.rs, sphere_cast.rs, world_sphere.rs; **rubikon/tests/SphereOracle + `sphere_check`: 60,000
     casts through Valve's 180247c30 / 180253ac0, 0 mesh casts differ, 2 hull casts at radius 30 with a 1-ulp normal**.
- **Backstab** (a pawn hit): the attacker-to-victim direction normalised in x, y (180a2f000), dotted (180a2b2c0) with
  the victim's forward from its abs angles and from its eye angles (vfn 0x5f0): above 0.475 either way. Else the
  third test (180a302c3 .. 180a303eb), for a pawn (vfn 0x558) with a model (vfn 0xca8): the bone **"spine_1"**
  (180b61300 -> 180cb4800 by the name's MurmurHash2, `0x6994cde`, seed 0x31415926; not head_0 as first noted) and
  its world transform (180b52420 -> 180caf670: the skeleton's bone cache, skeleton+0x1a0, 0x20 bytes a bone, set up
  by 180ca6840 when the valid mask +0x418 lacks the bits; a bad index gives the node's own transform, 1803d5fa0).
  The direction from the bone to the attacker's eye (vfn 0x5e8) normalised (180148890: |v| = sqrt((y y + z z) +
  x x), 1 / |v| times each part; zero stays zero; below 1e-17 or above 1e17 another path), dotted (y, z, then x)
  with the bone's quaternion applied to `182337f10` = (0, 1, 0) (set at 18012a390; t = 2 (v x q), C + (v + w t))
  and negated: above 0.475 is a backstab. The bone is the bone cache's, not the lag record's blended hitbox
  transforms (the hitbox path's override, +0x3f8): the animation's last pose at the backtracked origin and angles.
  Ported as knife.rs `spine_backstab`; the bone from abi.rs `knife_bone` (the newest record's spine_1 turned by the
  yaw since then; TODO: the float steps of that re-placement are not CS2's compose).
- **Damage** 180a2b280: stab 65, 180 from behind; slash 90 from behind, else 40 when the last attack was more than
  0.4 s before (the knife's +0xeb0 tick), else 25; DMG_SLASH through TakeDamageOld, hit group generic (a pawn box has
  no hitbox).

## 8. The hitbox cast (the physics query's vfn 0x168, traced 2026-11-10; sim/src/combat/hitbox.rs)

`DAT_1823ab5c0` vfn `0x168` is vphysics2 **18006ffb0**, which for one shape goes to **1802e1ac0**: the result reset
(fraction 1, the rest 0, -1 -1 at +0x1c), the shape's points through the hitbox's transform, from the asm: a point v
goes to `(C + (v + w t)) x s + p` with `t = 2 (v x q)` and `C = t x q` lane by lane (q the quaternion's xyz, w its w,
s the transform's scale, p its position); the radius times s. A capsule (query shape 3) is then the ray against the
segment, **18016caf0** (`sim/src/rn/gjk/capsule.rs` `ray_capsule`; 18016b0e0 / 18016b2f0 against a sphere when the
capsule is shorter than 0.001; 18008d5b0 a perpendicular): **rubikon/tests/CapsuleOracle + `capsule_check`: 200,000
rays through Valve's 18016caf0, 35,814 hits, 0 differ** in fraction, point, normal and the start-inside byte. A
fraction below 1 is a hit; 180a385c0's exit is the same cast back from the ray's end.

## What the code does now (2026-11-10)

- **In the sim** (sim/src/combat, called through ze_bullet / ze_damage / ze_lag_*): FireBullet's interval trace (the
  world's CastRayIntervals, then one hitbox per player with CS2's pick and exit), the segments, the walk and the step,
  the impacts with their damage and solids passed; the hit group (with mp_damage_headshot_only and the blast / shock
  bits), armor, the health floor with the carried fraction; lag compensation's recording and target-time rewind.
  ZR's knockback is in the sim too (knockback.rs, docs/game/knockback.md) on m_flDamageDealt; the knife's trace has no hitbox, so no push.
- **Stand-ins (UNSETTLED / TODO)**:
  - The hitboxes' pose: CS2's player anim graph on the server, its runtime an Esoterica port not yet checked against
    animationsystem.dll (section 3); a player who isn't rewound gets their newest record moved to where they stand
    (CS2 sets the bones up there); CS2's capsules, their cast, the pick and the rewind's blend are CS2's (sections 5, 8).
  - Lag compensation: StartLagCompensation's choice is CS2's (section 5, sim/src/combat/lagcomp.rs `start`: the
    target clamped to sv_maxunlag, the single-interp backtrack on the snapshot pair the client drew between, else the
    target time less the interp and a tick); CS2's sv_interp0 / sv_interp1 / cl_interp chain for its two-stage client
    interpolation doesn't apply (this client interpolates once between snapshots 2 ticks apart); no
    sv_unlag_fixstuck; the angles' blend (1814774c0): the abs yaw and duck state are the nearer record's.
  - (Done 2026-11-11, "shot-angles": no check of the shot's direction against the view, as CS2 has none; the
    lag compensation bullet above is ported whole since: sections 5b, 5c. Damage prediction, the client's own hit
    effects, is damage-prediction.md.)
  - The victim's flinch punch is ported (aim-punch.md 5; mp_flinch_punch_scale 0 here). player_hurt's dmg_health source, the pawn's +0x15a8 skip;
    who sets TakeDamageFlags (the clamps are ported, section 4).
  - (Done 2026-11-16, 6b: a surface's penetration data is the bake's table of CS2's own files, and a hash it lacks is
    "default" as vphysics2's find makes it.)
  - The knife (section 7): the spine_1 re-placement's float steps at a backtracked yaw, a map entity's team, a pawn
    box's cooked plane / vertex order (ties only), the world sphere walk not checked natively, 2 of 60,000 hull
    sphere casts with a 1-ulp normal at radius 30.
  - The client's own impact estimate (src/cs2web/sim/hitboxes.js) still uses a head sphere and boxes.
  - A model's hitbox set (3b): classic_zombie's fake_neck at its bind pose; hitboxes that aren't capsules are left
    out (none in ctm_sas's or GFL's sets); 1814a0e00's join over several meshes.
