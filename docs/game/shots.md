# Shots on players (hitboxes, damage, lag compensation, penetration, knife)

server_20261105 unless named; vphysics2_20260924; animationsystem_20261023; player_lagcompensation.cpp; skeletoninstance.cpp; CS2Fixes detours.cpp:184. "f32": the binary works in single floats at that step. Penetration's FireBullet 180a78120, segments 180a75640, walk 180a74900 / 180a97a80 (section 6).

## Functions

| Address | Module | What |
|---|---|---|
| 180a78120 | server | FireBullet |
| 180a713e0 | server | runs the interval trace |
| 180a884e0 | server | end = start + direction x range |
| 180c2ea80 | server | CGamePhysicsQueryInterface::TraceLineIntervals |
| 180bdb980 | server | sort intervals (0x38-byte entries) by distance |
| 180181520 | server | CHitboxSystem intervals (CHitboxSystem, out, start, delta, filter, 0, set) |
| 18018e630 | server | AABB tree walk of hitbox entities (radius 1.0, zero extents) |
| 180a385c0 | server | CCSHitboxSystem slot 0: one entity |
| 180a37900 | server | CCSHitboxSystem slot 1: CCSHitboxSystem::TraceShapeAgainstHitboxes |
| 1801a82b0 | server | CHitboxSystem::TraceShapeAgainstHitboxesDefault (the nearest) |
| 18149c820 | server | hitbox -> query shape |
| 180188810 | server | the hit's stored transform |
| 180a3ef00 | server | emit an interval entry |
| 180cacd40 | server | GetHitBoxListAndTransforms(skeleton, list*, transforms*, setHash) |
| 1814a6a20 | server | hitbox set name (model, m_nHitboxSet) |
| 180199b90 | server | MurmurHash2 seed 0x31415926 |
| 1814a0e00 | server | fill the list (model, list*, mesh group mask, hash) |
| 180caeae0 | server | render-time history transforms |
| 180caefb0 | server | CSkeletonInstance::GetTransformsForHitboxList (current pose) |
| 1814a0130 | server | bone index |
| 180b52c10 | server | m_bvDisabledHitGroups test |
| 180a78fb9 | server | violence_hblood blood trace call |
| 180539760 | server | ragdoll decal |
| 1802c1020 | server | CCSBot::ComputePartPositions (cs_bot_vision.cpp) |
| 1802c9d40 | server | bot part point (no hitboxes) |
| 1817b2518 | server | bot group -> part table (groups 0..5 to 4 parts) |
| 18157f4e0 | server | box centre |
| 180189050 | server | CHitboxSystem: an entity's hitboxes against a sphere (18017cbc0(centre, radius)), skipping m_bvDisabledHitGroups (180b52c10), nearest per group; from 180bb7e20 <- 180b9c320 (a parts / "Disabled" system) |
| 180b9eaf0 | server | (owner+0x60's entity, out*, hit group): group bounds (boxes 1814759f0, spheres / capsules centre +- radius); from 180b94bf0 <- 180bb90b0 (five groups) |
| 180ba1a10 | server | debug draw of hitboxes (colour per group 181936700, 180d59c20); from 180ba4b50 ("Health: %d, collision group: %d, nav ignore: %s") |
| 180ca9a20 -> 180ca9c60 | server | debug overlay (colour bytes, duration); from 180184bb0 and 180baac70 (sv_debug_overlays_broadcast / ScriptDebugDraw callers) |
| 180d1d630 | server | debug command timing 180181520 ("Traced intervals in %.3fus") |
| 180cbd2b0 | server | the skeleton's 4-entry render-time hitbox history (+0x3f8) via 180caefb0 |
| 180eda860 | server | clear older lag records |
| 180cb9bd0 | server | model state set-up for a model (this = sk+0x120; 6 callers, the model-change paths) |
| 1814a4420 | server | pose sized for the model (unread) |
| 1814a3040 | server | per-bone flags |
| 180cb7d10 | server | vfn 0x78: sk+0x410 = 0, valid mask cleared (1814a4780) |
| 180cb7d80 | server | both poses filled with the bind pose |
| 18149f440 | server | bind pose (model skeleton, scale, n, out) |
| 18149f1e0 | server | one bone's bind pose (bad index: identity 182337e70) |
| 180b44f00 | server | anim graph controller after its graph ran |
| 180cb69b0 | server | graph pose into the model's bones |
| 18149ee90 | server | (model, graph skeleton): the model's map for that skeleton, searched by the skeleton's pointer, returns entry+8; 1814a19a0 / 1814a1a30 read the same list |
| 1814a4750 | server | mark all bones valid |
| 180ca5f30 | server | CSkeletonInstance::CalcAnimationState (line 0xd5b) |
| 180b78a90 | server | CBaseAnimGraphController AddAnimationDecode (vfn 0xa8; callback 18195a0e0: 180ca3ca0 / 180ca3c20 -> 1814a4110 / 1814a4030) |
| 1814a47a0 | server | or wanted bones into the valid mask |
| 180ca4490 | server | parent-space pose (one bone) |
| 180cb7ff0 | server | override interface setter (3 callers) |
| 180c01760 / 180c01740 | server | bone-merge list (0x30-byte entries) |
| 180b55670 | server | physics body's transform (entity vfn 0x1f0; bone -> body vfn 0x90) |
| 180cab630 | server | copy the animation pose's bone |
| 180ca6840 | server | world-space bones (bone cache) |
| 1814a30a0 | server | bone parent |
| 181476030 | server | compose (parent pos, parent rot, local pos, local rot) |
| 180cab450 | server | root offset |
| 1804ac9f0 | animationsystem | 18149ee90's twin (caller 18007c410) |
| 1804ac0e0 / 1804acdd0 | animationsystem | pose reset / bind pose (model+0x130, n, data) |
| 180b670b0 | server | pawn OnTakeDamage (vtable 181794998 slot 128) |
| 180adb1f0 | server | slot 254 |
| 180a93f70 | server | pawn +0xe60 services (schema: m_pDamageReactServices; read before as the damage services) |
| 180a89430 | server | hit group step |
| 180cacf80 | server | trace -> m_pHitbox +0x38 |
| 180a3f3d0 | server | flinch (aim-punch.md) |
| 180ac60b0 | server | healthshot boost |
| 180a89230 | server | friendly fire |
| 180231840 | server | gamerules step |
| 180a88f30 | server | armor |
| 180ad24c0 | server | IsArmored |
| 180a7ab50 | server | weapon lookup |
| 180e83b50 | server | CCSGameRules vfn 0x110: `return 1` |
| 180b5d1e0 | server | (pawn) test before dropping armor items |
| 180a998f0 | server | pawn +0xe40 services (schema: m_pBuyServices; read before as the item services) on kevlar / assaultsuit |
| 1803ed610 | server | CBaseEntity::TakeDamageOld |
| 180fba770 | server | build the damage result |
| 180cf7020 | server | health |
| 1803c4950 | server | m_flDamageDealt / m_nHealthLost |
| 1803e55e0 | server | apply |
| 1803e4060 | server | health change callback |
| 180cdcad0 | server | CBaseEntity constructor (+0x2dc = 0) |
| 180249530 | server | CCSPlayerPawn vfn 0xaf8 respawn ("Player.Respawn") |
| 180d0e5d0 / 180d0e730 | server | respawn health |
| 18110aebe, 1813c7de2, 181487d87 | server | other classes' +0x2dc writes |
| 180adb230 -> 180a94400 | server | OnTakeDamage_Alive's post (slot 255) |
| 180a95d90 | server | player_hurt |
| 180a88a50 | server | reads result+0x34 |
| 180fca360 | server | hitgroup for DMG_BULLET |
| 180ec7250 | server | CLagCompensationManager::FrameUpdatePostEntityThink |
| 180ed95e0 | server | RecordDataIntoTrack |
| 180ed9330 | server | fill a record |
| 180edaa90 | server | clear a dead entity's track |
| 180ee08d0 -> 180edebe0 | server | StartLagCompensation |
| 180ebc9c0 | server | build an interp info (out, src, dst, frac) |
| 180ed23a0 | server | interp info valid |
| 180ec1200 | server | BacktrackPlayer |
| 180ec1467 / 180ec1480 | server | the blend (mode 2) / the angles' blend |
| 1814774c0 | server | angles blend (out, older, newer, f) |
| 180cb4090 | server | hitbox transform blend |
| 180ec7020 | server | FinishLagCompensation |
| 180ec2130 | server | clamp target |
| 1813b93b0 | server | interp time (out, &I0, &I1, frac) |
| 1813b8fb0 | server | tick difference |
| 1813b9690 | server | (drops a ratio) |
| 1813b9230 | server | from ticks |
| 180ebdc90 | server | three-way GameTime compare |
| 180eddd80 | server | log rate limit (3) |
| 1813b9930 | server | GameTick + float ticks |
| 1813b9870 | server | GameTick - float ticks |
| 180ebc010 | server | snap infos |
| 180ebc050 | server | per-player record buffer (0x470 a record) |
| 180edbbe0 | server | restore a player |
| 180ec2210 | server | reset a record |
| 180d1b4e0 | server | WantsLagCompensationOnEntity(pawn, entity, cmd, mask) |
| 1803d6f50 | server | abs origin |
| 180d20ee0 | server | command's view angles |
| 181470980 | server | AngleVectors |
| 1814738b0 | server | normalize (doubles) |
| 181473e90 / 181475b60 | server | AngleQuaternion / QuaternionAngles |
| 180a75640 | server | segments |
| 180225130 | server | squared length |
| 180a74900 | server | the walk |
| 180a97a80 | server | a segment's step |
| 180a74a20 | server | interval as a CGameTrace |
| 180c00e80 | server | game surface table |
| 1800729c0 | vphysics2 | surface controller vfn 0x18 (index into the list at +8) |
| 1800729f0 | vphysics2 | vfn 8 find by hash |
| 180073875..180073896 | vphysics2 | default surface set to find(0x75de364e) |
| 180ae27b0 | server | pawn interacts-as (grenades.md) |
| 180a2f170 / 180a2f500 | server | CKnife PrimaryAttack (slash) / SecondaryAttack (stab) |
| 180a2fa80 | server | knife attack |
| 180c2f3c0 | server | TraceShape |
| 180a2f600 | server | knife filter ShouldHitEntity (vtable 181916390) |
| 180cfb4b0 | server | vfn 0x350 InSameTeam(other) |
| 180492250 | server | g_Teams[team] |
| 18048a430 / 180530ae0 | server | sphere shapes |
| 180a30058 | server | sphere TraceShape |
| 180a2f000 | server | 2D normalise |
| 180a2b2c0 | server | dot |
| 180a302c3 .. 180a303eb | server | spine_1 backstab test |
| 180b61300 -> 180cb4800 | server | bone by name hash |
| 180b52420 -> 180caf670 | server | bone world transform (bone cache) |
| 1803d5fa0 | server | node's own transform |
| 180148890 | server | VectorNormalize |
| 18012a390 | server | sets 182337f10 = (0, 1, 0) |
| 180a2b280 | server | knife damage |
| 18006ffb0 -> 1802e1ac0 | vphysics2 | query vfn 0x168: one shape |
| 18016caf0 | vphysics2 | ray against capsule |
| 18016b0e0 / 18016b2f0 | vphysics2 | ray against sphere (capsule < 0.001) |
| 18008d5b0 | vphysics2 | perpendicular |
| 1801f5770 | vphysics2 | world CastShape type 1 |
| 1801d9dc0 | vphysics2 | tree walk |
| 180242750 -> 180247c30 | vphysics2 | mesh sphere cast (triangles 1803157c0 / 180315820) |
| 180250b20 -> 180253ac0 | vphysics2 | hull sphere cast (GJK) |

## Fields

| Offset | Field |
|---|---|
| DAT_182173b20 | FireBullet is tracing (hitbox debug log) |
| *181e146a0 = 181e14cf0 | CHitboxSystem singleton (vtable 18191bcd8) |
| hitbox system +8 | AABB tree |
| entity hitbox component +0x88 | live table (DAT_181d9f830) |
| DAT_1823ab5c0 | physics query (vfn 0xe8 filter, 0x168 shape cast, 0xb8 surfaces) |
| trace +0x30..0x4f | the hit's transform |
| trace +0xb8 | bone index |
| trace +0 (+0x10) | surface (its index) |
| trace +0x10 | m_pHitbox |
| trace +0xbb | start solid |
| interval +0x32 / +0x33 | 0 entry / 1 exit; 1 |
| interval +0x30 | surface short |
| CHitBox +0x00 / +0x08 | name / surface property name |
| +0x18 / +0x24 | m_vMinBounds / m_vMaxBounds |
| +0x30 | m_flShapeRadius |
| +0x38 | m_nGroupId (hit group) |
| +0x3c | m_nShapeType |
| +0x48 | hitbox index |
| skeleton +0x1c0 | model handle |
| entity vfn 0x1b8 (the model), +0x270 -> vfn 0x60 | the skeleton instance |
| sk +0x308 | mesh group mask |
| sk +0x3bc | m_nHitboxSet |
| sk +0x3f8 | render-time history (4 entries) |
| sk +0x400 | lag-compensated transforms |
| sk +0x120 / +0x130 / +0x160 | model state / animation pose / parent-space pose |
| sk +0x1a0 / +0x418 | bone cache / its valid mask |
| sk +0x1e8 | per-bone flags (4 bytes) |
| sk +0x3c0 | controller (vfn 0xd0 mode) |
| sk +0x3d0 | override interface |
| sk +0x410 / +0x414 | animation pose valid / parent-space flags |
| sk +0xf8 | mutex |
| sk +0x10 .. +0x2c | skeleton's own transform |
| model +0x70 / +0x78 / +0x90 | mesh count / meshes / each mesh's group mask |
| mesh +0x174 | hitbox set count |
| model +0x130 | model skeleton (+0x48 bone count, +0x98 positions 12 B, +0xb0 quaternions 16 B, +0xc8 scales 4 B) |
| model +0x440 / +0x448 | graph skeleton maps count / entries (0x50: +0 skeleton handle, +8 {count, int* bones}, +0x38 / +0x40 float channel map) |
| controller +0x410 | graph instance (result poses instance+0x108 -> +0x47d8) |
| controller +0x38 / +0x40 | secondary skeletons count / handles |
| pose +0x10 | transforms (0x20 bytes) |
| info +0x44 | damage (f32) |
| info +0x65 | helmet flag |
| info +0x68 | trace |
| info +0x70 | flags (bit 18 0x40000 skips armor; TakeDamageFlags) |
| info +0x7c | solid segments before the hit |
| pawn +0x14fc | m_LastHitGroup (stored +1) |
| pawn +0x1514 | m_ArmorValue |
| pawn +0xb18 | ItemServices (+0x49 m_bHasHelmet) |
| pawn +0xe40 | m_pBuyServices (CCSPlayerPawn schema, server_20261105; m_pItemServices is +0xb18) |
| pawn +0xe60 | m_pDamageReactServices (schema; m_pDamageServices is another class's) (+0x48 dmg_health, probably m_nTotalledHealthLost; +0x4c dmg_armor) |
| pawn +0x15a8 | skip (unread) |
| entity +0x2dc | m_flDamageAccumulator |
| entity +0x2e8 | m_nTakeDamageFlags |
| entity +0x2d0 | m_iHealth |
| entity +0x32c | m_flSimulationTime |
| result +0 / +0x18 / +0x1c / +0x20 / +0x38 / +0x40 / +0x48 | info / m_nHealthLost / health before / m_flDamageDealt / same / carry / flags |
| vdata +0x824 | m_flHeadshotMultiplier |
| vdata +0x828 | m_flArmorRatio |
| record (0x480) +0 | flags (bit 0 alive) |
| +4 / +0x10 / +0x1c / +0x28 | abs origin / abs angles / mins / maxs |
| +0x34 | tick `(int)(m_flSimulationTime x 64 + 0.5)` |
| +0x38 / +0x3c / +0x40 | sequence / cycle / ? |
| +0x50 / +0x70 | hitbox transforms CUtlVector / 32 inline 0x20-byte transforms |
| player +0x40 / +0x4b0 | restore / change record |
| player set +0x920 | index |
| controller +0x5a8 | interp amount |
| CUserCmd +0x78 / +0x30 / +0x38 | attack history index / history count / list |
| history entry +0x10 | has-bits (bit 2 cl_interp) |
| entry +0x20 -> +0x18 | cl_interp frac (default 0x181e0e300) |
| entry +0x28 / +0x30 | sv_interp0 / sv_interp1 (+0x1c src, +0x20 dst, +0x18 frac; default 0x181e0e2d8) |
| CUserCmd base +0x40 -> +0x40 +0x18 / +0x1c / +0x20 | view angles |
| pawn +0xb50 | movement services (m_pMovementServices) |
| movement services +0x1ac | m_flMaxspeed |
| pawn +0x344 | m_iTeamNum |
| segment (0x18) +0 / +4 / +8 / +0xc / +0x10 / +0x12 / +0x14 | start / end / damage / penetrations left / first (15 bits) / last / solid bit 0 |
| game surface +8 / +0x14 | bulletPenetrationDistanceModifier / gamematerial (surface +0x10 x 0x20 + DAT_18218e4f8 +0x28) |
| CVPhysics2SurfacePropertyManager | first vtable 0x1803fbe68, second (offset 0x30) 0x1803fbe20; table +0x18 slots of 0x10, mask +0x10, -1 empty; miss returns +0x30 (manager +0x60) |
| filter +0x20 | the attacker's handle (knife filter) |
| knife +0xeb0 | last attack tick |
| collision property (vfn 0x228) +0x18 | m_nInteractsAs |

## Constants

| Value | What |
|---|---|
| 0x1c300b, flags `0x49 \| 2` | bullet filter interacts-with |
| bit 1 of interacts-with | hitboxes layer |
| DAT_1817805b0 | sign-flip mask |
| 4.0 (DAT_18179be70) | head multiplier without a weapon |
| 1.25 / 0.75 | stomach / legs |
| mp_damage_scale_ct_head / _ct_body / _t_head / _t_body | 182119e38 / 182119e28 / 182119e58 / 182119e48, default 1.0 |
| mp_damage_headshot_only | 182119e20 |
| mp_flinch_punch_scale | 182173ac0 |
| phys_playerscale / phys_headshotscale | 182173ad0 / 182173ae0; flag 0x80000 |
| ff_damage_reduction_bullets / _grenade / _grenade_self / _other | 1821738c0 / 1821738a0 / 1821738b0 / 1821738d0 (bullets: handle 1821738c8, registered 1800c5c60, default 0.1) |
| ff_damage_bullet_penetration | handle 1821738e8, object 1821738e0, registered 1800c5bb0, default 0, max 1.0 |
| mp_teammates_are_enemies | handle 18211a6d8, object 18211a6d0, registered 1800a3587, flags 0x282100, default 0 ("When set, your teammates act as enemies and all players are valid targets") |
| mp_friendlyfire | 0x1821b9a88 |
| 0xc6 | armor damage types (bullet 2, slash 4, blast 0x40, club 0x80) |
| 0.5 / 1.0 / 20 | armor bonus / blast bonus / DMG_BURN multiplier |
| DFLAG_SUPPRESS_HEALTH_CHANGES 0x1, DFLAG_PREVENT_DEATH 0x8, DFLAG_FORCE_DEATH 0x10 | TakeDamageFlags |
| [181f9e120] +0x58, else 100 | respawn health |
| 4096 (DAT_181926a44) | teleport squared distance (64 u) |
| 0.01 (DAT_1818e9f3c) | moved threshold squared (0.1 u) |
| 0xc3011 | fixstuck hull mask |
| 0.215638, 0.848013, 1.06021, 1.0904, 1.43519, 3.2452, 3.55645 (181813da0..db8) | slerp fit |
| DAT_181f4a000 | zero quaternion |
| sv_maxunlag | 1.0 (max 1.0), 18217b4f8 |
| sv_maxunlag_player | -1, 18217b508 |
| sv_unlag | 0x1821e1a90, default 1 |
| sv_unlag_fixstuck | 0x1821e1ac0, default 0, "Disallow backtracking a player for lag compensation if it will cause them to become stuck" |
| sv_lagcomp_filterbyviewangle | 0x18217b520, default 1, flags 0x4000 |
| sv_lagcompensationforcerestore | bool (default not read) |
| sv_csgo_shoot_lagcompensation_max_error | 1.0 (warns when the client's head hitbox position differs) |
| sv_csgo_shoot_use_full_interp | 0x18212b270, default 1, flags 0x2002 |
| sv_csgo_shoot_force_full_interp | 0x18212b280, default 0 |
| sv_csgo_shoot_force_use_target_time | 0x18212b290, default 0 |
| sv_csgo_shoot_log | 0x18212b210 |
| sv_csgo_shoot_verify | 0x18212b230 (the head check) |
| sv_csgo_shoot_verify_on_attack_only | 0x18212b260, default 1 |
| sv_csgo_shoot_log_attack_cmds_only | 0x18212b220, default 1 |
| 300 (0x18179bea8), 1.5 (0x1817a4420), 0.707107 (0x18196cdb0) | view-angle filter |
| 1/512 u | entry / exit swap distance |
| 500 | range modifier distance unit |
| 3000 / 0.1 | solid step rules |
| 'F' (0x46) | flesh |
| 0x75de364e | "default" surface m_nameHash |
| 0x1803fcb00 | `surfaceproperties/surfaceproperties.vsurf` |
| `\| 0x20040` | bullet damage info type bits |
| 1.18, 2.8, 0.15 | debug-list stop branch (debug record only) |
| 0x6994cde | "spine_1" MurmurHash2 |
| 0xc3001, group 4, flags 0x4b, object set 0xf | knife trace |
| 48 / 32 + 18; +128 | knife reach slash / stab; lag comp reach |
| 14, 11, 8, 5, 2 | knife sphere radii |
| 0.475 | backstab dot |
| 65 / 180; 90; 40 / 25; 0.4 s | stab / backstab; slash backstab; slash fresh / repeat; window |
| 1e-17 / 1e17 | normalize bounds |
| 0.001 | capsule length floor |

## 1. The bullet reaches the hitboxes

- FireBullet builds the bullet filter (0x1c300b, the shooter and its owner as skip entities, flags `0x49 | 2`), sets DAT_182173b20 = 1, calls 180a713e0.
- TraceLineIntervals: the world's intervals (world vfn 0x520: vphysics2 CastRayIntervals), then, **if the filter's interacts-with has bit 1**, 180181520 adds the hitboxes' intervals and 180bdb980 sorts all by distance. Hitboxes are not in the physics world.
- 180181520: 18018e630 into a candidate list; for each candidate with a live hitbox component the query filter is asked (DAT_1823ab5c0 vfn 0xe8 -> filter vfn 0x28 with the entity's collision attributes, entity vfn 0x2a8), then slot 0.
- 180a385c0: slot 1 finds the hitbox hit from the start; that hitbox's shape at the stored transform is cast **backwards** from `start + delta` along `-delta` (vfn 0x168). Exit fraction = `1 - back fraction`, or 1.0 when the back cast misses. Two entries (180a3ef00): entry at the forward fraction, exit at the exit fraction, both +0x33 = 1, with hit point, hitbox pointer, bone index, entity handle, surface index. **One hitbox per player per bullet**, entered once, left once.

## 2. Which hitbox (180a37900)

- Model -> GetHitBoxListAndTransforms: the set named by m_nHitboxSet (hashed) and each hitbox's world transform (0x20: position + w, quaternion), from in order: the lag-compensated list (+0x400, when its count matches), the render-time history (+0x3f8, 180caeae0, at `curtime - (t[i] - t[i-1]) + 1/64`), else the current pose (180caefb0).
- Shape (18149c820): type 1 sphere (centre mins, radius; query shape 1, or 0 with radius 0), 2 capsule (mins, maxs, radius; query shape 3), else box: a point when mins == maxs (query 0), else the mins / maxs box in bone space (query 2, an OBB once transformed). Cast via vfn 0x168(out, ray, start, delta, shape, transform).
- The pick: every hitbox hit with fraction < the trace's goes to a bucket by hit group, each keeping the nearest (`<=`: an equal fraction later in the set replaces it):

  | bucket | 0 | 1 | 2 | 3 | 4 | 5 | 6 |
  |---|---|---|---|---|---|---|---|
  | hit groups | head 1 | stomach 3 | chest 2 | neck 8 | arms 4, 5 | anything else (generic 0) | legs 6, 7 |

  The head bucket is dropped when the stomach's or chest's fraction is strictly less than the head's. Result: the first filled bucket 0..6. **Not the nearest**: an arm in front of the chest gives the chest.
- The trace gets: surface (m_sSurfaceProperty MurmurHash2'd, via vfn 0xb8 -> +8), m_pHitbox, hit point `start + delta x fraction`, bone index (1814a0130), contents = the entity's | 2, the entity handle. Start-solid: normal (0, 0, 1), offset 0.
- 1801a82b0 (also skips m_bvDisabledHitGroups) is used by FireBullet only for violence_hblood's blood trace (180a78fb9) and a ragdoll decal (180539760), not damage.

## 3. Player models' hitboxes

agents/models/ctm_sas/ctm_sas.vmdl (MDAT `m_hitboxsets`): set **"cstrike"**, 19 hitboxes, **all capsules (shape 2), all "playerflesh"** (m_nameHash 242403237; penetration 0.9, 'F', as "flesh"):

| hitbox (= bone) | group | radius | | hitbox | group | radius |
|---|---|---|---|---|---|---|
| head_0 | 1 head | 4.3 | | leg_upper_l / _r | 6 / 7 | 5.0 |
| neck_0 | 8 neck | 3.5 | | leg_lower_l / _r | 6 / 7 | 4.0 |
| pelvis | 3 stomach | 6.0 | | ankle_l / _r | 6 / 7 | 2.6 |
| spine_0 | 3 stomach | 6.0 | | hand_l / _r | 4 / 5 | 2.3 |
| spine_1 | 2 chest | 6.5 | | arm_upper_l / _r | 4 / 5 | 3.3 |
| spine_2 | 2 chest | 6.2 | | arm_lower_l / _r | 4 / 5 | 3.0 |
| spine_3 | 2 chest | 5.0 | | | | |

- characters/models/ctm_fbi/ctm_fbi.vmdl and characters/models/tm_phoenix/tm_phoenix.vmdl have an empty `m_hitboxsets`.
- The pose comes from CS2's player anim graph (worldmodel.vnmgraph and the graphs it references, fed the parameters ReflectPawnState sets); evaluated by an Esoterica-derived runtime (not checked against animationsystem.dll), composed down the skeleton's parents at the body yaw, the head sits at 64.08 u standing, 47.03 ducked, still. The lag record keeps 180ed9330's transforms (at most 32) and the rewind blends them by 180cb4090.

### 3b. A set per model

- 180cacd40: no model (sk+0x1c0 null) -> 0. Hash: the argument, or with 0 the name 1814a6a20(model, m_nHitboxSet) hashed. 1814a0e00 walks the model's meshes, takes those whose group mask ANDs with sk+0x308, and in each its hitbox sets by the hash; an open-addressed table keyed on the hash (`(h >> 16 ^ h) x -0x7a143595 ...`) tracks what was taken.
- Count returned = the list's; transforms: +0x400 when its count equals the list's, else +0x3f8, else 180caefb0. **No default set, no padding, no count special case**: a model without the set gives 0, callers skip it (180a37900 logs "%s has no hitboxes").
- Every caller of 180cacd40 (9): 180a37900 (FireBullet's hitboxes); 1801a82b0 (blood trace, ragdoll decal); 180ed9330 / 180edebe0 (lag record / StartLagCompensation); 1802c1020 (CS2's bots: 0 hitboxes -> every part 1802c9d40's point; else groups 0..5 -> 4 parts via 1817b2518, each box's centre); 180189050; 180b9eaf0; 180ba1a10; 180ca9a20. So a hitbox set matters to bullets (blood / decals), the lag record, CS2's bots and debug drawing; grenades, the knife, +use and triggers never read it.
- GFL's models (workshop 3160448201, `hitboxSets.cstrike`):
  - The 8 zombie models: 19 capsules, all "playerflesh", in ctm_sas's order and groups. zombie_chris_walker's are ctm_sas's; zombie_cultist and zombie_frozen differ in head_0; zombie_basic, ghoul_soldier, marauder and skeleton_bloody_lp in head_0, neck_0, pelvis, spine_0..3, the ankles and the arms (zombie_basic: head (-1.24, -0.07, 0)-(2.95, -0.91, 0) r 4.3 vs ctm_sas's (-1, 1.8, 0)-(3.5, 0.2, 0) r 4.3; spine_1 r 4.5 vs 6.5; spine_2 5.5 vs 6.2).
  - classic_zombie: its group-1 box is named and boned **"fake_neck"** (a (4.92, 3.93, 0.99) b (2.22, -4.70, 0.99) r 4.2), its own bone: parent spine_3, bind pose (8.00204, -1.03499, -0.0000064) q (-2.9e-7, 2.6e-6, 0.1217463, 0.9925613) (bits 4100085c bf847a90 b6d6f198 / b49e2c8a 362d0f4f 3df95621 3f7e187f; neck_0's is 6.5152 along spine_3 with the same turn); child fake_head carries no hitbox; no head_0 box. Its constraint list (m_modelInfo's BoneConstraintList) is the pack's common one (2 CBoneConstraintDotToMorph, a CTiltTwistConstraint on head_0, a CPointConstraint on neck_0 + head_0, 2 CAimConstraint on the scapula helpers): none of its own that could drive fake_neck (the slaves' names aren't in the KV3 read: an inference from the lists being equal). fake_neck is posed per 3c.
  - The 12 human models ("nohitbox" in 11 names, and `vector`): **one capsule**, "ankle_l" on bone ankle_l (tifa's "ankle_L"), group 6, radius 2.6, "playerflesh"; five different capsules across the pack (e.g. master_chief (-1.82, -4.26, -0.81)-(6.32, -0.17, -0.38)). A bullet hits such a human only on that ankle; the lag record keeps one transform (a count change 1 <-> 19 at an infection clears older records: 180eda860); everything else about the pawn (its collision box for the knife's TraceShape and for movement, the backstab's "spine_1" bone, grenades) untouched. Purpose: teammates' bullets pass through a human (section 6: a teammate's hitbox costs damage and penetration).

### 3c. A model bone the graph's skeleton lacks (fake_neck)

**The bone stays at the model's bind pose under its animated parent.** sk = the skeleton instance, its model `*(*(sk+0x1c0))`.

- 180cb9bd0: both poses sized (1814a4420 on sk+0x130 and sk+0x160), per-bone flags rebuilt (sk+0x1e8 from 1814a3040), vfn 0x78 (180cb7d10), then 180cb7d80: `18149f440(model+0x130, 1.0, count, data)` on both poses.
- 18149f440: a bone's 0x20 bytes = position `m_bonePosParent` x scale, then the bone's scale x scale, then quaternion `m_boneRotParent`.
- 180b44f00: `180cb69b0(sk, pose)` for the pawn's skeleton and each secondary skeleton.
- 180cb69b0: `map = 18149ee90(model, pose's skeleton)`; for each model bone i < map.count: `j = map.bones[i]`; **`j >= 0` copies pose transform j into the animation pose's bone i; negative j leaves it**; then every bone marked valid (1814a4750). Float channels the same via the second map.
- 180ca5f30: the wanted bones (flags vs mask) not valid; a sequence decode is added and run (g_pAnimationSystem vfn 0x68) only when the controller's vfn 0xd0 is neither 2 nor 3 (AddAnimationDecode adds one for mode 1 only); then 1814a47a0. **With a graph (modes 2, 3) nothing is decoded: an unwritten bone is valid with what the buffer holds.**
- 180ca4490, per bone: the override interface (vfn 0 returns 0 none / 1 parent-space / 2 model-space transform), the bone-merge list, a physics body's transform (-1 in the bone -> body map: bind pose by 18149f1e0), else the animation pose's bone (180cab630 -> 180ca5f30).
- 180ca6840: `parent = 1814a30a0(model, bone)`, `world = 181476030(parent pos, parent rot, local pos, local rot)`; a root bone takes sk+0x10 .. +0x2c plus 180cab450's offset.
- classic_zombie's vmdl names `animation/graphs/worldmodel/worldmodel.vnmgraph` and `animation/skeletons/characters/worldmodel.vnmskel` like every pack model; the stock skeleton has no fake_neck, so its entry is negative and 180cb69b0 never writes it: fake_neck keeps 180cb7d80's bind pose from the moment the pawn gets the model, 180ca4490 copies it to the parent-space pose and 180ca6840 puts it under spine_3's animated world transform. No constraint drives it.

## 4. Damage (180b670b0 -> 180adb1f0 -> 180a93f70)

1. **Hit group (180a89430)**, with a trace: group = `trace->m_pHitbox+0x38`, stored +1 at pawn +0x14fc. `damage = info+0x44` (f32):
   - head (1): `headshot x damage x mp_damage_scale_<team>_head`, headshot = m_flHeadshotMultiplier, 4.0 without a weapon. Same with or without a helmet (it only decides the flinch and info+0x65).
   - stomach (3): `(float)((double)damage x 1.25) x _body`; chest (2), neck (8), arms (4, 5): `x _body`; legs (6, 7): `(float)((double)damage x 0.75) x _body`; generic (0) and others unchanged.
   - `<team>`: victim team 3 reads the `_ct_` pair, else `_t_`.
   - mp_damage_headshot_only: a DMG_BULLET hit off the head does 0.
   - The flinch: mp_flinch_punch_scale x constants (-0.1, -4 floor; head without helmet -0.2 / -12 and a `RandomFloat(-1, 1)` yaw off the global stream clamped to [-9, 9]; chest / stomach / neck -0.005 armored, -0.033 not), 180a3f3d0 (aim-punch.md 5).
   - Damage force x phys_playerscale, on a headshot also phys_headshotscale and flag 0x80000; 0 for a grenade's head hit. Ragdolls only.
2. Listeners; `healthshot_healthboost_damage_multiplier` while boosted (180ac60b0).
3. **Friendly fire (180a89230)**: ff_damage_reduction_bullets / _grenade / _grenade_self / _other on teammates; 1.0 for an enemy. (ZE runs mp_friendlyfire 0: teammates take none.)
4. Gamerules 180231840.
5. **Armor (180a88f30)**, damage type 0 or `& 0xc6`, unless info+0x70 bit 18 (0x40000: the C4 shockwave's hit):
   - IsArmored (180ad24c0): armor > 0 and hit group generic, chest, stomach, arms, neck; head only with a helmet; **legs never**.
   - `ratio = m_flArmorRatio x 0.5` (0.5 without a weapon; a blast whose 180a7ab50 finds no weapon takes weapon_hegrenade's vdata: the planted C4's RadiusDamage); `bonus = 0.5` (1.0 for any blast: gamerules vfn 0x110 = 180e83b50 `return 1`; c4-shockwave.md); `health = damage x ratio`; `armorDmg = (damage - health) x bonus x (20 for DMG_BURN 8, else 1)`, all f32.
   - `armorDmg <= armor`: `armorDmg < 0` -> 1; `armor -= (int)armorDmg`. Else `health = damage - armor / bonus`, `armorDmg = armor`, `armor = 0`. `info+0x44 = health`; `dmg_armor = (int)armorDmg`; when the armor took damage and 180b5d1e0(pawn): item_kevlar and item_assaultsuit through 180a998f0 (probably dropping them once the armor is gone).
   - No heavy-armor branch.
6. buddha cvars (debug).

### TakeDamageOld (1803ed610)

1. `result.m_flDamageDealt = info.m_flDamage`. The info's +0x70 gets m_nTakeDamageFlags (+0x2e8) or'ed in at 1803edad5; 180fba770 builds the result (+0x18 m_nHealthLost = cvttss2si(incoming), +0x1c health before, +0x20 / +0x38 m_flDamageDealt = incoming, +0x48 = the info's flags).
2. After OnTakeDamage: `lost = floor(dmg)`, `carry = (dmg - floor(dmg)) + m_flDamageAccumulator`; `carry >= 1` -> `lost += 1, carry -= 1`.
3. At 1803edb3f: flag 0x1 without 0x10 skips vfn 0x408 and the whole loss.
4. At 1803edc30 (result +0x48 byte): **0x10: `lost = max(health + 1, cvttss2si(lost))`**, else **0x8: `lost = min(health - 1, cvttss2si(lost))`**, both back through cvtdq2ps; carry to result +0x40.
5. 1803c4950: `m_flDamageDealt = lost`, `m_nHealthLost = min(cvttss2si(lost), cvttss2si((float)before))`.
6. 1803e55e0: nothing when `flags & 0x11 == 1`; else `entity+0x2dc = carry`, `m_iHealth = cvttss2si((float)before - (float)healthLost)` (1803e4060).
- A 27.9 hit costs 27 and the next one 28. Death when health reaches 0 with health before > 0 (vfn 0x418 / 0x420).
- The carry's only writers: the constructor 180cdcad0 (0), 1803e55e0, and the respawn 180249530 ("Player.Respawn", health = [181f9e120] +0x58 when above 0, else 100, then +0x2dc = 0). The pawn persists through an infection (no 0xaf8), so the carry does too.
- Post (180adb230 -> 180a94400) fires **player_hurt** (180a95d90): userid, health, armor, dmg_health (services +0x48, probably m_nTotalledHealthLost: from result+0x34 in 180a88a50, unsettled), dmg_armor (+0x4c), hitgroup (only for DMG_BULLET, 180fca360), attacker, attacker_pawn, weapon, priority 6.
- ZR's knockback runs in CS2Fixes' TakeDamageOld post hook (detours.cpp:184) with m_flDamageDealt: the floored damage, not clamped to the health left.

## 5. Lag compensation

- **Recording** (180ec7250 -> 180ed95e0), per lag-compensated entity; a track is a list of 0x480-byte records (180ed9330).
  - Records older than `(int)((curtime - sv_maxunlag) x 64 + 0.5)` dropped; a new one only when the newest's tick is below the entity's simulation tick; a dead entity's track cleared (180edaa90).
  - Teleport: a record more than 64 u (squared > 4096) from the previous, or with a different hitbox count, clears every older record (180eda860).
- **Rewind** (180ee08d0 -> 180edebe0): the command's player; not bots (vfn 0xc20); needs sv_unlag and more than one player. Target from the command's attack history (+0x78 into +0x38): its two interpolation snapshots (180ebc9c0, validated by 180ed23a0), the interp amount (`player+0x5a8 x 64 + 1`), clamped to `sv_maxunlag x 64` ticks back; failing: the target time ("using target time"). Modes: "target time backtrack", "single interp backtrack", "sv_interp0 backtrack", the two-record full interp.
- **BacktrackPlayer (180ec1200)**: records around the target tick, `frac = (target - older.tick) / (newer.tick - older.tick)` clamped [0, 1]; origin, mins, maxs `(b - a) x frac + a` per component (f32); angles 1814774c0; sv_unlag_fixstuck: a hull trace (0xc3011) pulls the origin back; origin / angles set when moved more than 0.1 u; sequence and cycle restored (cycle lerped, wrapping); hitbox transforms blended (180cb4090) and handed to the skeleton (+0x400).
- **180cb4090**: `h = f - 0.5`, `k = (h f)(f - 1)`, `d = |dpps(a, b)|`, `w = ((((3.55645 - d 1.43519) d - 3.2452) d + 1.0904) h² + ((d 0.215638 - 1.06021) d + 0.848013)) k + f`, `b w + a (1 - w)` (w negated first when the dot <= 0), divided by sqrt(dpps(q, q)) (zero length: DAT_181f4a000); position `(1 - f) a + f b`, scale `(b - a) f + a`. Checked natively: 1,000,000 blends, 0 differ.
- FinishLagCompensation (180ec7020) restores.

### 5b. StartLagCompensation's choice (180edebe0)

1. The job's target (vfn 0x10 of its +0x70: CLagCompensationManager vfn 0x28's, usercmd.md 8) clamped by 180ec2130 twice: local_948 with the job's max unlag (param_3 + 0x10; sv_maxunlag_player read when not above 0) and local_8e0 (the pawns' target, vfn 0x568).
2. +0x78 -1 or not below +0x30 ("clamped invalid attack history index") -> target time. sv_csgo_shoot_use_full_interp off -> target time. The entry (+0x38 list + 8 + index x 8) without has-bit 2 (`+0x10 >> 1 & 1`) -> target time.
3. 180ebc9c0 builds I0 (sv_interp0) and I1 (sv_interp1). 180ed23a0: valid when `-1 < src <= dst` and `0 <= frac <= 1`; invalid: "full interp info not valid, using target time".
4. `T = 1813b93b0(out, &I0, &I1, cl_interp's frac)`: each info's time = (src, `(float)(dst - src) x frac`) folded (I1's first, then I0's), `d = time(I1) - time(I0)`, out = (time(I0).tick, `((float)d.tick + d.ratio) x f`) folded: time(I0)'s own ratio dropped.
5. now = (gpGlobals +0x44, 0); `lower = now - 1813b9230(sv_maxunlag x 64)`; 180ebdc90 (ticks -1 (0xff) / 1, equal ticks: ratios 0xff / 1 / 0 / 0x80 unordered): T < lower -> lower; else T > now (> 0) -> now; else T. Not T itself (the ticks compared, then ucomiss on the ratios; a NaN not equal): "clamping to sv_max_unlag (%.3f), using target time" (180eddd80(3) rate-limits).
6. `1813b9930(T, interp x 64 + 1) - target (local_948)` (the controller's +0x5a8 x 64.0 + 1.0; GameTick + a float count of ticks), `(float)tick + ratio >= 1`: "full interp info doesn't match target time, using target time instead" (one-sided).
7. 180ebc010 snaps I0, I1 (`|1 - frac| < 0.01`: src = dst; `|frac| < 0.01`: dst = src); S0 = I0's src, S1 = I1's dst: **S1 - S0 == 0 -> target time; == 1 -> single interp** (local_res20 = sv_csgo_shoot_force_full_interp: set, the full interp instead); **else full interp**. sv_csgo_shoot_force_use_target_time forces the target time.

Per player (the job's filter vfn 0, not the shooter):
- Target time (180edfacb..): `local_960 - 1813b9870(lerp x 64 + 1)`, lerp = 1/64 for maxClients 1, else `(int)(+0x5a8 x 64 + 0.5) x 1/64` (180edf656..); BacktrackPlayer(lc, entity, &{mode, a, b, frac}, record set, restore buf, change buf, 1) mode 0.
- Single interp (180edf6f4..): mode 1 with (S0, S1, cl_interp's frac), no buffers ("single interp backtrack" on failure).
- Full interp (180edf7d5..180edfa98):
  1. Mode 1 with sv_interp0's (src, dst, frac): change into buffer A (180ebc050; indexed by +0x920), restore into the player's own (+0x40); failure (>= 2): "sv_interp0 backtrack", not moved.
  2. Mode 1 with sv_interp1's: restore into scratch, change into B; failure: "sv_interp1 backtrack", 180edbbe0 restores.
  3. Mode 2: `param_3[2]` = A, `[4]` = B, `[6]` = cl_interp's frac: A older, B newer, the blend 180ec1467 (origin / mins / maxs `(b - a) f + a`, angles 1814774c0, hitboxes 180cb4090, sequence / cycle; f <= 0 takes A), change into the player's own (+0x4b0) and applied; failure: "cl_interp backtrack", 180edbbe0.

BacktrackPlayer, the rest: no record set -> 2, empty -> 3; restore record (param_5's slot or +0x40) and change record (param_6's or +0x4b0) reset (180ec2210); mode 1: from the newest, a record at dst is the newer (src == dst: the older too), at src the older, below src none; mode 0 as above. No older: "No valid positions in history for BacktrackPlayer entity %d", 4. Fixstuck hull trace; restore record from the entity (+0x10..+0x30 origin, angles, mins, maxs; +0x34 simulation tick), change record from the blend, moved when > 0.1 u (bits 2 / 4 / 8 / 0x10: moved, turned, resized, hitboxes and animation); returns **1 nothing changed, 0 moved** (callers' `< 2` is success).

### 5c. Who is rewound, the angles' blend

- **WantsLagCompensationOnEntity (180d1b4e0)**: mp_friendlyfire 0 and pawn vfn 0xc78(entity) (a teammate): no; index bit not in the mask: no; sv_lagcomp_filterbyviewangle off: yes; else `d = |entity origin - pawn origin|` (`sqrt((dz dz + dy dy) + dx dx)`); speed = for a player (vfn 0x558) its movement services' m_flMaxspeed (+0xb50 -> +0x1ac), else 300; **`sv_maxunlag x (speed x 1.5) > d`: yes**; else the forward of the command's view angles dotted `((fz z + fy y) + fx x)` with the normalised direction (1e-17 / 1e17 bounds, 1814738b0 outside, 0 stays 0): **`0.707107 <= dot`** (comiss / setbe: unordered counts as yes). A refused player keeps their current pose.
- **Angles' blend** (180ec1480, LAB_180ec1467): when the two records' abs angles differ, 1814774c0: AngleQuaternion each, the fitted slerp (`q = b w1 + a w0`, zero length 0x181f4a000 = zeros), QuaternionAngles; equal: the older's. A pawn's abs angles are (0, yaw, 0).
- sv_unlag_fixstuck default 0: CS2 doesn't run the hull trace by default.

## 6. The bullet's walk (FireBullet 180a78120)

- **180a713e0**: the end (180a884e0), the filter's bit 1 cleared for the call, TraceLineIntervals with radius -1 (vphysics2's base fraction 1), trace fraction 1, the segments.
- **180a75640**: an entry right after an exit within 1/512 u (`(f_i - f_(i-1)) |delta|`, |delta| from 180225130: `(z² + y²) + x²`; NaN not) trades places with it, fractions staying in their slots. Air segments end on each entry that follows an exit, each after a solid from the last entry to the hit before; after the last air one a solid from its end to 1 on its entry (first = last: no thickness); a first segment that is solid (ray began inside) turns the list into a zero-length air segment and a solid to 1 on that solid's last hit.
- **180a74900**: (damage, penetration, range modifier, |delta|, 4 left as an **int**) through every segment, each given the damage and count after it; the one the bullet stops in gets end 1 and damage 0 and ends the list.
- **180a97a80**: air: `damage = powf(modifier, (to - from) / 500) x damage` (tier0's V_powf); a solid: 3000 / 0.1 rules, thickness from the two intervals' end points (`(dz² + dy²) + dx²`), the least modifier first..last (minss), the material rules, then **`lost = wm x (pm x 3) + chunk x damage`** and `total = (thickness² x pm) / 24 + lost`, both maxss(0, x); below 1 left stops. The segment's two traces from 180a74a20 (an interval as a CGameTrace: `start + delta f` per component, +0xbb start solid = the exit flag).
- **The loop**: every air segment fires bullet_impact at its end interval's end point and, with an entity, queues a damage info (the segment's damage, +0x7c the solids before); applied after the loop, in order, through TakeDamageOld.

### 6b. Audit

- FireBullet's arguments (rbp = entry rsp - 0x28c8): xmm3 the range (180a782a9..), stack +0x28 (rbp+0x28f0) penetration, +0x48 (rbp+0x2908) damage **as an int** (180a784a1 movd + cvtdq2ps: m_nDamage), +0x58 (rbp+0x2918) range modifier; the walk gets (damage, penetration, range modifier) in xmm1..3 and 4 penetrations (rbp+0x3b4 = 4 at 180a7827b). +0x7c is the count of solids before the air segment (rbp+0x2908 reused: `inc` at 180a7867e, stored at 180a791a4); damage the segment's +8 (180a78fe6); type bits `| 0x20040` (180a7919c).
- Surface (180a97a80 decompile lines 109-113, 180a74a20 +0x18): the interval's +0x30 short via vfn 0xb8, the controller's vfn 0x18 (1800729c0: list at +8, `0 <= i < count`, else null), then 180c00e80. Find by hash (1800729f0): open-addressed, linear probe; hit sets *found = 1 and returns the slot's +8; **a miss sets *found = 0 and returns +0x30**, set by the loader to find(0x75de364e) ("default"). vphysics2 names one file, `surfaceproperties/surfaceproperties.vsurf`; pak01 holds only that vsurf_c: a map's own surface (any unknown hash) is "default". The aggregate loader's own vfn 8 call per m_surfacePropertyHashes entry taken as this find.
- Game table order: CS2 walks in the vsurf's order. The stock vsurf (2026-11-16) has one child before its base, concrete (#46, base no_decal #105); concrete's surfaceproperties_game.txt entry sets both keys (0.5, "C"): no surface's values differ by the order.
- **Teammate branch** (decompile lines 200-235): the regular path unless the entry is flesh 'F', ff_damage_reduction_bullets is 0, the entry trace's entity is a player (vfn 0x558), mp_teammates_are_enemies is 0, and the handle's entity (1813aa290 -> 180c10aa0) is a player with vfn 0xca8 set whose m_iTeamNum equals the shooter's (the walk's 4th argument): then the modifier is ff_damage_bullet_penetration, 0 stopping the bullet (LAB_180a97f93). cfgs: gamemode_competitive.cfg / _competitive2v2.cfg ff_damage_reduction_bullets 0.33 (a teammate costs what an enemy does), gamemode_casual.cfg 0 (**a teammate stops the bullet**), gamemode_deathmatch.cfg 0.0 with mp_teammates_are_enemies 1 (regular).
- Stop branch with a debug list (param_5, sv_showimpacts_penetration's): constants 1.18, 2.8, 0.15 fill the debug record only (returns 1).
- Contents (bit 13, PASS_BULLETS): a shape's vfn 0x50 first qword (m_nInteractsAs); a hitbox's entity's collision property +0x18, the pawn's m_nInteractsAs (0x40000, solid cleared: 180ae27b0, grenades.md "Players and the projectile's filter"): no bit 13, and a hitbox's flesh meets no material rule.

## 7. The knife (180a2fa80)

- PrimaryAttack (slash, 0) and SecondaryAttack (stab, 1) call 180a2fa80.
- **Reach** 48 + 18 (slash) or 32 + 18 (stab) along the eye forward (181470980); lag compensation starts with reach + 128.
- **Traces** (TraceShape 180c2f3c0, interacts-with 0xc3001 (the player layer: the pawn's collision box, not hitboxes), group 4, flags 0x4b, object set 0xf, the attacker's handle / owner / hierarchy id ignored):
  1. A line with the knife's filter (+0x20 the attacker's handle): no attacker, or the hit entity is the attacker: false; else the hit entity's vfn 0x350 (180cfb4b0, InSameTeam): other non-null and `180492250(this m_iTeamNum) == 180492250(other's)` (null for a team outside the list) -> refused. The first line passes through teammates.
  2. Missed or hit no pawn: the same line with a plain filter (rbp+0x340, built at 180a2fead).
  3. Missed: spheres (180a30058, plain filter as 5th argument) of radius 14, 11, 8, 5, 2 to `end - fwd x radius`, each kept while it hits, the first miss ends it. vphysics2's sphere casts: CastShape type 1 (1801f5770: a ray at radius <= 1e-6, else the clip, the trees, the walk), a mesh's vfn 0x20 (180242750 -> 180247c30), a hull's (180250b20 -> 180253ac0, GJK). Checked natively: 60,000 casts, 0 mesh casts differ, 2 hull casts at radius 30 with a 1-ulp normal.
- **Backstab** (a pawn hit): attacker-to-victim direction normalised in x, y (180a2f000), dotted (180a2b2c0) with the victim's forward from its abs angles and from its eye angles (vfn 0x5f0): above 0.475 either way. Else (180a302c3 .. 180a303eb), for a pawn (vfn 0x558) with a model (vfn 0xca8): bone **"spine_1"** (180b61300 -> 180cb4800 by MurmurHash2 0x6994cde, seed 0x31415926) and its world transform (180b52420 -> 180caf670: the bone cache sk+0x1a0, 0x20 bytes a bone, set up by 180ca6840 when +0x418 lacks the bits; a bad index gives 1803d5fa0). Direction from the bone to the attacker's eye (vfn 0x5e8) normalised (180148890: `|v| = sqrt((y y + z z) + x x)`, `1 / |v|` times each; zero stays zero; below 1e-17 or above 1e17 another path), dotted (y, z, then x) with the bone's quaternion applied to 182337f10 = (0, 1, 0) (`t = 2 (v x q)`, `C + (v + w t)`) and negated: above 0.475 is a backstab. The bone cache, not the lag record's blended hitbox transforms: the animation's last pose at the backtracked origin and angles.
- **Damage** (180a2b280): stab 65, 180 from behind; slash 90 from behind, else 40 when the last attack was more than 0.4 s before (+0xeb0 tick), else 25; DMG_SLASH through TakeDamageOld, hit group generic (a pawn box has no hitbox).

## 8. The hitbox cast (query vfn 0x168)

- vphysics2 18006ffb0 -> 1802e1ac0: result reset (fraction 1, rest 0, -1 -1 at +0x1c); the shape's points through the transform: `(C + (v + w t)) x s + p` with `t = 2 (v x q)`, `C = t x q` lane by lane (q xyz, w, s scale, p position); radius x s.
- Capsule: ray against the segment, 18016caf0 (18016b0e0 / 18016b2f0 against a sphere when shorter than 0.001; 18008d5b0 a perpendicular). Checked natively: 200,000 rays, 35,814 hits, 0 differ in fraction, point, normal and start-inside byte. Fraction below 1 is a hit; 180a385c0's exit is the same cast back from the ray's end.

## Unread

- What CS2 hits on a pawn with an empty-set model (ctm_fbi / tm_phoenix): 180cacd40 returns 0 and 180a37900 logs "%s has no hitboxes"; whether SetModel / the animgraph's model swaps in a set.
- 1814a0e00's join when several shown meshes carry the set (GFL's pack: every mesh carries the same-sized "cstrike" set).
- The function that fills a model's graph-skeleton map (a raw scan of server.dll and animationsystem.dll finds nothing reaching model+0x440 / +0x448 but the readers, so it is built through another pointer; a negative entry for a missing bone read from the `>= 0` test; match by bone name inferred); 1814a4420; where the bone constraints run.
- Where in CS2's frame the server evaluates the player anim graph; animationsystem.dll's graph runtime itself.
- Who sets TakeDamageFlags in ZE (a map's damage); player_hurt's dmg_health source; pawn +0x15a8.
- 180a998f0's armor item handling.
- vfn 0xca8 (taken as set for a live player).
- The knife: spine_1's re-placement at a backtracked yaw, a map entity's team (TeamNum key), a pawn box's cooked plane / vertex order (ties only), the world sphere walk not checked natively.
- sv_lagcompensationforcerestore's default.
