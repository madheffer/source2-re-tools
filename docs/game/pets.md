# Pets: CS2's chicken pets, the Weekly Care Package

client_20261015, server_20261105; pak01 (items_game.txt, panorama: rankup_redemption_store.ts, vanity_pet_info.ts,
mainmenu.ts, sessionutil.ts, popup_pet_event, the photo booth / HatchBook panels; the anim graphs; the stage maps).
The pet system arrived with the Rush Hour update (2026-09-22). Most of the timing is the GC's (it writes the pet item's
date attributes); the client reads those dates with the constants below. Not in any CS2 file: the stage lengths beyond
what those constants pin, a feed bag's time, the breed / colour draw, the XP rules.

## Functions

| Address | Module | What |
|---|---|---|
| 180fd4f50 | client | registers the InventoryAPI pet natives |
| 180faee60 | client | GetPetItemID |
| 180ffd4e0 | client | TryAckPetEventAndCheckExpiration |
| 180fedb70 | client | RestorePetItemData |
| 180faeb50 | client | GetPetGrowthPercent -> 180d48150 |
| 180faeab0 | client | GetPetFeedAmount -> 180d467d0 |
| 180faeeb0 | client | GetPetLifetimeRemaining -> 180d481f0 |
| 180fd13d0 | client | IsPetLowOnFood -> 180d4e340 |
| 180fe3f80 | client | PetHasAchievement |
| 180fae490 | client | GetPersonalStore |
| 18083b8f0 | client | item lookup (V_atoui64 of the id) |
| 18118bef0 -> 18118d1c0 | client | now: the GC's rtime |
| 1801587b0 | client | clamp (value, min, max) |
| 18112e7e0 | client | attribute by name (read through the item's vtable + 0xe8) |
| 180d46430 | client | `deployment date` (D) |
| 180d48480 | client | `pet next upgrade date` (U) |
| 1807232d0 | client | `upgrade level` (L) |
| 180d48320 | client | the low-food date |
| 180d48150 | client | growth percent (the egg's ring) |
| 180d4e340 | client | low on food |
| 180d481f0 | client | lifetime remaining (chick / pullet / hen rings) |
| 180d467d0 | client | feed amount (the feeder's fill) |
| 1801b9c30 | client | max (with 0x3a83126f = 0.001) |
| 18084a1b0 | client | chicken graph controller ctor (params) |
| 180845430 | client | its param registration |
| 1808492a0 | client | float param write (finite, |f| < 2^31) |
| 180854ca0 | client | ACTION_COMPLETED flag |
| 18093eac0 | client | entity's controller (entity + 0x1130) |
| 18085c680 | client | controller PlaySequence (from PlaySequenceOnItem 180e52ad0) |
| 1809657b0 | client | play a sequence (model without a graph) |
| 1809529a0 | client | sequence by name |
| 180ed0210 | client | overhead pet name (each frame from the reticle's 180eaf7c0) |
| 180d567a0 | client | the pet item's name |
| 180ecb3d0 | client | overhead scale x 0.7 |
| 18022fee0 | client | overhead name trace (engine, eye, pelvis, ignore, interacts-with 1, group 4) |
| 180ebdb10 | client | CSGOHudShowTeamEquipment |
| 180eb7650 / 180eb76d0 | client | +cl_show_team_equipment |
| 180e65b40 | client | TransitionToCamera: time 0 sets the camera, else manager +0x4c0 vfn 0x48 |
| 180860180 | client | activity -> action |
| 180d4f1b0 | client | ApplyState(ent, var) |
| 1808605e0 | client | mode table |
| 180860100 | client | SetActivity (pulses action_reset when unchanged) |
| 180d43380 | client | vanity chicken's frame (vfn) |
| 180860420 / 1808492f0 | client | idle_phase write (a change pulses action_reset) |
| 180d4e890 | client | Interact (interface at entity +0x14b8, vtable around 181cac288) |
| 180852000 | client | flinch: bool node (graph +0x10 [index] +0x18 = 1) + flinch_variation |
| 18085d0e0 | client | controller post-update (vtable 181c092c8): ACTION_COMPLETED from this update, flinch back to 0 |
| 180d520f0 | client | food check / the feeder (from 180cada50 and 180cbeda0) |
| 1809dfb70 | client | find cs_pet_placement (the one whose +0x38 matches the pet's) |
| 180802c40 / 180802e50 | client | the pet's "feed" handle / set "feed" and "placement" handles |
| 180d40b10 / 180d51170 / 180d41ce0 | client | C_DynamicProp create |
| 1815dc490 | client | name "feed" (DAT_181cac328) |
| 1809643c0 | client | set model |
| 180b9b620 | client | render mode from the pet |
| 181748480 | client | transform (origin, quat, local, quat) |
| 1817445e0 | client | AngleQuaternion |
| 1817463a0 | client | QuaternionAngles |
| 180219a80 / 180219a50 / 180219ab0 | client | abs origin / angles / scale |
| 18022b670 / 18022b470 / 18022b750 | client | SetAbsOrigin / SetAbsAngles / set scale |
| 180d42f50 | client | feed_anim (string in the attribute map at identity +0x48, then vfn 0x150) |
| 1808311d0 | client | remove the pending key |
| 18093e020 | client | (0) in the feed sequence play |
| 1815bc1c0 | client | name compare ("feed") |
| 180e5e960 / 180e5e8b0 | client | SetPetActivity[AndVariation]OnItem; also SetPetPlacement names |
| 181cca620 | client | activity names 0..12 |
| 180d50300 | client | set activity when changed |
| 18085c990 | client | preview set: action_snapshot, variation n - 1 |
| 180b833b0 | client | camera manager transition (CUI_MapPreviewCameraManager vtable 181ccbd88, over CBaseCameraManager; vfn 0x48 180e65c50) |
| 180b70cb0 | client | Now(): realtime with +0x48 |
| 180b82920 | client | camera manager frame |
| 1808a4520 | client | smoothstep |
| 180b595e0 | client | angle blend: unchanged when equal, else 181744420 |
| 181744420 | client | the fitted slerp (k polynomial 3E5CD035 .. 40639CE0) |
| 180d52620 | client | the egg's nest (from 180cada50 / 180cae080 / 180cbf0b0) |
| 180a1b890 | client | remove the nest |
| 18118d3d0 | client | GetInventoryImage |
| 181134ad0 | client | pet definition (+0x20 pedestal_display_model) |
| 180dcaa00 | client | ItemImage |
| 181190590 | client | dynamic image test (every flexible_loadout_slot "pet" item but chicken_feed, 180e42740) |
| 180e536d0 | client | runtime image render (type 2) |
| 180cada50 | client | (character, pet handle, item, placement) |
| 180cbb290 | client | replace a character's pet |
| 180cae080 | client | place the pet |
| 180d4db50 | client | set the pet's item |
| 180d48bb0 | client | shoulder placement |
| 180219680 | client | parent to an attachment |
| 18072ed20 | client | model index: chicken 0, chick 1, chicken_polish 2, chicken_silkie 3 (V_stristr over 181ba52a8) |
| 180d51420 | client | dying particles (from 180d4eda0 on m_bSpawnDyingParticles) |
| 180943590 | client | material group |
| 180a11370 | client | the model's material bound |
| 180d45c90 | client | after the dying particles |
| 181012e60 | server | parses pet_definitions ("name must be a positive integer") |
| 18034fdd0 | server | SetOwner(chicken, pawn) |
| 180a969e0 | server | pawn's controller |
| 180b0a450 | server | controller's pet item |
| 180b0a470 | server | pet item id (-1 none) |
| 1808c4e20 | server | upgrade level |
| 181058270 | server | item into m_AttributeManager |
| 1813aa290 | server | seed |
| 181067140 / 181066ed0 | server | pet definition's model / material group (0xff none -> 0) |
| 18034f710 | server | CCSChickenManager: the round's pets (from 18033bad0) |
| 18033bad0 | server | manager events; round_freeze_end's 5 s timer -> 18033b940 |
| 18033b940 | server | every pet's movable flag cleared |
| 18034f4f0 | server | round_end with a winner: tricks |
| 18034e060 | server | deathmatch spawner |
| 180c30c10 | server | remove entity |
| 180a7a9d0 | server | the player's chicken |
| 18093df90 | server | pets allowed: GetCurrentGameType() == 0 |
| 180354190 | server | a spot from a list |
| 180bef630 | server | create `chicken` |
| 180a9b7f0 | server | the player's pet link |
| 1803ea3b0 | server | SetAbsOrigin |
| 180caa5f0 | server | spawn |
| 1802b7cb0 | server | ground trace |
| 1814bb3f0 | server | GetNearestNavArea |
| 1814cb1b0 | server | nav area centre |
| 180307f90 | server | vector add |
| 180348300 | server | follow ("[Chicken Activity] Chicken %d has started following %s"); stamps +0x32a4 with now on every call |
| 180348730 / 1802805e0 | server | follow stops |
| 180347350 | server | Event_Killed (slot 131) |
| 180344730 | server | CChicken think ("CChickenChickenThink"; think table 180347250) |
| 180341f44 / 180341f50 | server | Touch / Use |
| 1803457e0 | server | Use body (vfn 0x9e0) |
| 1803518c0 | server | Spawn |
| 1808c4f60 | server | model scale table by level |
| 180354bf0 -> 1803433b0 | server | the spot lists |
| 1803413f0 / 180341cc0 | server | spawn radius test |
| 180399740 | server | CNavPath build (ChickenPathCost 1817be3f0) |
| 18034cba0 | server | path area refusal |
| 180a4f4e0 | server | graph SetActivity |
| 180a4f460 | server | action_reset |
| 180a4c030 | server | graph update |
| 180a4f790 / 180a4f7d0 | server | graph level / mode (mode_in_game?) |
| 1803515f0 | server | SetDesired activity |
| 180349410 | server | Idle |
| 1803506b0 | server | trick |
| 180349180 | server | Glide |
| 18034deb0 | server | Land |
| 18034da90 | server | panic / jump (sub vfn 0x48) |
| 18034cef0 | server | jumping (now < +0x11e4) |
| 180345830 | server | (chicken, player, checkDist): +use / ping |
| 180351300 | server | follow the player |
| 180346f60 | server | turn to face and trick |
| 180343fd0 | server | HasOwner |
| 180ab7ec0 | server | player_ping (snap) |
| 180ac6b50 | server | ping rank |
| 180adb580 | server | ping placement |
| 18015a2f0 | server | WorldSpaceCenter (vfn 0x2c8) |
| 18034f440 | server | CChicken ObjectCaps (vtable 0x1817bd858 slot 0xd0) |
| 180d04f60 | server | base ObjectCaps (CBaseEntity / CBaseModelEntity) |
| 1803507d0 | server | Move(target) |
| 18034f3f0 | server | size = maxs - mins |
| 180353d40 | server | the sweep |
| 180338b80 | server | timer restart |
| 180a4f760 | server | in_water |
| 180c2a810 | server | sweep filter ShouldHit (vtable 1817af9e0) |
| 180590fe0 | server | physics query (vfn 0x98 gravity) |
| 180342230 | server | root motion apply (vtable slot 0x960) |
| 181473df0 | server | rotate by yaw |
| 1811d824c | server | copies root motion (+0x370 / +0x380 from result +0x10 / +0x20) |
| 1811e12e0 | server | anim context (world transform with scale) |
| 1803423e0 | server | feelers |
| 1802b5420 | server | ray / hull trace |
| 1803ea1a0 | server | yaw += rate x dt |
| 1803480c0 | server | flee |
| 1803544e0 | server | flee from fast players (returns at once for owned chickens) |
| 1803d9090 | server | game rules' state (1: removed) |
| 180d0e5d0 / 180d0e730 | server | SetHealth / SetMaxHealth |
| 1803ebce0 | server | (1, 0): takes damage, flags |
| 180cdcad0 | server | CBaseEntity ctor |
| 180354490 | server | hull bounds |
| 1803eb340 | server | model scale |
| 1803ed610 | server | TakeDamageOld |
| 1816c4664 | server | floor |
| 1803c4950 / 1803e55e0 | server | health -= amount |
| 1803e42f0 | server | life state 1 |
| 180f695d0 | server | Chicken.Death |
| 180b612d0 / 180b52300 | server | the pelvis |
| 1808d4c60 | server | model index |
| 18093d4e0 | server | holiday mode |
| 1803c5900 | server | (0x420) |
| 180922960 | server | game rules' kill hook (a living player attacker) |
| 180bad480 | server | base Event_Killed |
| 18014d780 | server | EyePosition = abs origin + GetViewOffset 18014e660 |
| 18029d180 | server | m_iPetPopulation (unread) |
| 1801d0290 | server | other_death (unread) |

## Fields

CChicken (schema):

| Offset | Field |
|---|---|
| 0xcb0 | m_AttributeManager (chicken +0xd00, inside it: the item read for the level, -> 1808c4e20) |
| 0xca0 | graph controller (vfn 8 origin, 0x60 walk, 0x58 run, 0x48) |
| 0x10e8 | m_updateTimer |
| 0x1100 | m_stuckAnchor (written past 50 u, never read) |
| 0x1110 | m_collisionStuckTimer (+0x111c its time) |
| 0x1128 | m_isOnGround |
| 0x112c | m_vFallVelocity |
| 0x1138 / 0x113c / 0x1140 | m_desiredActivity / m_currentActivity / m_activityTimer |
| 0x1158 | m_turnRate |
| 0x115c | m_fleeFrom |
| 0x1160 | m_moveRateThrottleTimer |
| 0x1178 | m_startleTimer (interval +0x1184) |
| 0x1190 | m_vocalizeTimer |
| 0x11a8 | m_leader |
| 0x11ac | m_owner (+0x11b0 CUtlString model, +0x11bc material group) |
| 0x11c0 | m_reuseTimer |
| 0x11d8 | m_jumpTimer (+0x11e4 its end) |
| 0x11f0 | m_flLastJumpTime |
| 0x11f8 | the nav path (CNavPath); +0x31f8 point count, points 0x20 apart at +0x11e4 (as first read; +0x11e4 is also m_jumpTimer's end: unconfirmed) |
| 0x3200 | m_repathTimer |
| 0x3218 | path follower |
| 0x3290 | taken: the nav area under the pet (+0x40 & 8: NO_JUMP) |
| 0x3298 | m_vecPathGoal |
| 0x32a4 | m_flActiveFollowStartTime |
| 0x32a8 | m_followMinuteTimer |
| 0x32c8 | m_BlockDirectionTimer (+0x32d4; dir +0x32c0) |
| 0x32e0 | the trick after a turn |
| 0x32e1 | trick at the next round start |
| 0x32e2 | movable (following; taken as m_bIsFollowing?: no such schema field, unconfirmed) |
| 0x32e3 | m_bSpawnDyingParticles |

| Offset | Field |
|---|---|
| entity +0x2d0 / +0x2d4 / +0x2dc / +0x2e0 / +0x2e8 | health / max health / damage carry / takes damage / flags |
| entity +0x30 bit 9 | flagged (no live pet) |
| entity +0x3e4 | m_hOwnerEntity |
| entity +0x40c | m_flActualGravityScale |
| entity +0x410 -> +0x370 | the graph's root motion transform |
| entity +0x2f1 | byte (setter unread) |
| entity +0x818 | m_vecViewOffset (no chicken code writes it) |
| collision +0x40 / +0x4c / +0x5a | mins / maxs / flags (& 4) |
| pawn +0x514 | state ({0, 3}: alive-or-3) |
| pawn +0x344 | team |
| pawn +0xd48 | pet item |
| manager +0x68 / +0x80 | T / CT spot lists |
| gamerules +0xd8 | m_bFreezePeriod (g_pGameRules DAT_1821ba1c0) |
| DAT_182125888 | g_pGameTypes (vfn 0x98 GetCurrentGameType) |
| DAT_18234ace8 | nav mesh (+8 area count) |
| nav area +0x24 / +0x28 / +0x30 / +0x34 | lo.x / lo.y / hi.x / hi.y |
| CCSGO_TeamPreviewCharacterPosition +0x1080 | m_petItem (the end-of-match line-up) |
| client chicken +0x14c4 | owner |
| client chicken +0x52c bit 5 | not drawn |
| client chicken +0x1b88 | mode (written only by 180cada50: 0-3) |
| client chicken +0x1b8c | trick count |
| client chicken +0x1b90 | var |
| preview character +0x3760 / +0x98 | its pet / placement |
| controller (client) | params: symbol at S, graph pointer S + 8, index S + 0x10 |
| controller 0xc0 / 0xd8 / 0x100 / 0x118 / 0x130 / 0x148 | action / action_reset (auto-reset ref) / action_variation / in_water / mode / life_stage |
| controller 0x160 (index 0x168; the first read had a +0x158 symbol, handle +0x160) / 0x178 / 0x190 / 0x1a8 / 0x1c0 / 0x1d8 | idle_phase / turn_angle / has_lookat_target / lookat_target / flinch / flinch_variation |
| controller 0x1e8 | byte: ACTION_COMPLETED (server +0x1e8 finished, +0x1c0 action_reset) |
| camera manager +0x28 / +0x30 / +0x3c / +0x40 / +0x48 | cur / prev / start / dur / realtime flag |
| camera slots 0xa8 .. 0xb8 / 0xc0 / 0xd8 | origin / angles / fov |
| damage info +0x4c | bit 3 DMG_BURN, bit 8 DMG_SHOCK |
| trace +0x50 / +0x84 / +0x90 / +0xbb | contents (& 0x18000 water) / endpos / normal / start-solid |

## Constants

| Value | What |
|---|---|
| 0xbdd80 = 777600 s (9 days) | low-food lead |
| 0xb89200 = 12096000 s (140 days) | max age |
| 432000 s (5 days) | egg growth |
| 0x24ea00 (28 d) / 0x41eb00 (50 d) / 0x76a700 = 7776000 (90 d) | stage anchors |
| 1036800 s (12 days) | feed fill span |
| 0x3d4ccccd = 0.05, 0x3ca3d70a = 0.02, 0x3a83126f = 0.001 | clamps |
| 0x9ea | k_EMsgGCAckPetEvent (at most once per RandomFloat(10, 300) s) |
| 1.0 / 0.25 / 0.6 / 1.0, x 1.4 | model scale by level (1808c4f60) |
| (-8, -8, 0)..(8, 8, 16) | hull (raw, after the model scale) |
| 10000 u | GetNearestNavArea range |
| 0x4 / 18 / 256 u | spot flood: excluded attribute / max step / T and CT radius (general list: none) |
| 40 x 40 x 20, 0xc3011 | spot box, mask |
| 0x10802, types 5 / 6, step > 2 | path refusal |
| DAT_182171410 | server activity ID table (idle, squat, walk, run, glide, land, panic, trick, turn, feed, shoulder, snapshot, reveal) |
| 0x1000000 | RandomInt range for action_variation |
| 7.7025 / 86.953 u/s | walk / run root motion (x model scale) |
| 1000 u (1e6, 0x49742400) | +use / ping distance |
| 46 (0x42380000) / 36 | ping snap sphere / max distance |
| 0x18 / 13 / 0x19 / 1 / 0x1b / 0x1a | ping types: param_4 set / urgent / C4 / weapon / defuser / chicken (0 otherwise) |
| 30 / 6 / 1.0 s | ping life: param_4 set / else / a pet used in the freeze time |
| 0x81 | pet ObjectCaps (impulse use, no radius bit) |
| 0.5 / timescale (0x18178057c) | stuck duration (set in Spawn) |
| 0.01, 0.7071 | ground normal tests |
| 0xc3011, group 5, exclude |= 0x40000c0000, flags (b & 0xc9) | 0x49 | the sweep |
| 0x18000, +64, -9 | water sweep: interacts-with, height, wz offset |
| devonly_chicken_feeler_distance 30 / _height 5 / _pitch 45 / _blocktimer 0.2 | feelers (flags 2) |
| 32 | feeler centre ray length |
| 182337ef0 / 182337f40 | forward (1, 0, 0) / up axis constants |
| 3 s, 0.1 s, 0.9 | jump: interval, timer, up . way >= 0.9 |
| 0x4000 | chicken_stop |
| 0xc3011, group 4, flags 0xf, exclude | 0xc0000 | leader-in-sight ray |
| 2000 u (4e6 squared) / 4000 / 0.5 s / 100 u / 60 s | follow: too far / path too long / repath / goal still near / minute timer |
| 90 / 110 .. 180 / 220 | follow distances: idle / walk / run |
| 300, 1700, 0.96, 0.253, 360 deg/s, 0.9 | steering |
| 150 u, 0.7071 | flee |
| 20 / 10 | round step 3: the leader's nav area wider and deeper than 20 -> its centre + (0, 0, 10) |
| 57.295776 | turn_angle rad to deg |
| 512, 0.6, 1.4285715, 0.7, 10 u, (0, 0, 18) | overhead: scale clamp(atan(512 / d), 0.6, 1.4285715), x 0.7, ray within 10 u, Content offset |
| DAT_18252b6e0 | client mode table: 0 unspecified, 1 main_menu_foreground, 2 main_menu_background, 3 end_of_match, 4 in_game |
| DAT_18252b708 | life_stage: egg, chick, adolescent, adult |
| (-15.1731, 11.6387, 0) (0x181cada90 / 0x181cada78), DAT_181ac29d8 | feeder local offset x scale; zero angles |
| 1.75 | chick scale factor (feeder) |
| 0x119bcd9 | shoulder attachment hash |

## Items (items_game.txt)

| Def | Name | item_class | Notes |
|---|---|---|---|
| 4681 | `pet` | pet | `#CSGO_Type_Pet`, loadout slot `pet`, rarity rare, quality unique, `cannot trade` 1, nameable |
| 4948 | `chicken_egg` | chicken_egg | `#chicken_egg`, image `econ/pets/chicken_egg`, pedestal `models/chicken/egg_pristine.vmdl`, `upgrade level` 0 |
| 4949 | `chicken_feed` | chicken_feed | `#chicken_feed` ("Feed your pet to keep it around."), image `econ/pets/chicken_feed_bag`, pedestal `models/chicken_feed/chicken_feed_bag.vmdl`, `upgrade level` 0 |

- `pet_definitions` (`pet id` values): 1 `chicken_egg_01` (egg_pristine), 2 `chicken_chick_01` (`#pet_chick`, chick.vmdl),
  3 `chicken_catalana_01` (`#pet_chicken`, chicken.vmdl), 4 `chicken_silkie_01` (chicken_silkie.vmdl), 5 `chicken_polish_01` (chicken_polish.vmdl).
- Attributes: 296 `pet id` (pet_id, hidden), 180 `deployment date` (value_is_date: the hatch date; an egg's is its due
  date), 268 `upgrade level` (0 egg, 1 chick, 2 pullet, 3 hen), 303 `pet food expiration date`, 304 `pet next upgrade
  date`, 313 `pet seed` (the colour / pattern draw), 111 / 328 / 329 `custom name attr` / `2` / `3` (one name per stage:
  `custom name attr` + (level >= 2 ? ' ' + level : '')).
- `ItemInfo.IsPet` (common/iteminfo.ts): true for `pet`, `chicken_egg`, `chicken_feed`.

## The pet's clock (client)

- Low-food date (180d48320): F = food expiration; 0 when F is 0, else `min(F - 0xbdd80, (D ? D + 0xb89200 : 0) + 0xbdd80)`.
- Growth (180d48150): L == 0 only (else 1.0): `clamp(1 - max(D - now, 0) / 432000.0, 0.05, 1.0)`.
- Low on food (180d4e340): `lowFoodDate(item) <= now`.
- Lifetime remaining (180d481f0): needs D != 0 and D <= now (else 1.0). `end = max(min(U, D + 140 d), D + 1)`; start = D
  (chick), U - 28 d (pullet), D + 50 d (hen); returns `1 - clamp((int)(now - start) / (float)(end - start), 0.02, 1.0)`.
  Stages pinned: chick D .. D + 22 d (pullet's U - 28 d = D + 22 d when U = D + 50 d), pullet .. D + 50 d, hen D + 50 d ..
  D + 140 d. The 22-day chick (U at hatch = D + 22 d) is the GC's (matches the client's anchors and community observation).
- Feed amount (180d467d0): lo = lowFoodDate, up = U, cap = D ? D + 140 d : 0. lo <= up and lo < cap:
  `f = clamp((int)(lo - now) / 1036800.0, 0, 1)`, returns `max(f * f * 0.4, 0.001)`. Otherwise the stage's progress:
  start = D, U - 28 d (L 2), U - 90 d (L 3); `clamp((int)(now - start) / (float)(U - start), 0, 1)` when start < U, else
  0. (The decompiler drops the float return; the second branch's exact clamp use is unread in the disassembly.)
- TryAckPetEventAndCheckExpiration (180ffd4e0): reads pet id, D, L, F, U; due an upgrade event when U <= now (a looked-up
  definition first when L != 0); expired when F < now or D + 140 d < now: "maxage" when D + 140 d <= F, else "nofood".
  On an event sends 0x9ea. Popup lines: pet_expired_notification_* (title_nofood_egg for an egg), pet_upgrade_notification_msg_<L>.

## The Weekly Care Package (rankup_redemption_store.ts)

- The GC's `PersonalStore`: `generation_time`, `items` (four item ids; `'-'` x4 for none), `redeemable_balance`.
- A claim costs 1, 2 for `chicken_egg` or `chicken_feed` (`_GetClaimCost`); a tile is selectable while selection cost +
  its cost <= balance; selecting plays UIPanorama.gift_deselect, deselecting gift_select (CS2's own swap); a refused pick
  pulses the selected tiles with UIPanorama.buymenu_failure.
- Redeem: nothing selected pulses every unclaimed tile; inventory full (NUM_BACKPACK_SLOTS) refuses;
  `StoreAPI.StoreRedeemFreeRewards("id,id")`, a 10 s timeout popup (#rankup_redemption_store_timeout_*); the GC answers
  `free_reward_redeemed`, claimed tiles play `reveal-anim` + UIPanorama.gift_claim. Claiming a pet item while not the
  lobby's pet host closes the lobby (LobbyAPI.CloseSession) and zooms the menu onto the pet.
- Badge: balance > 0 `#rankup_redemption_store_directive` ("Claim your rewards"); 0 left `#rankup_redemption_store_closed`;
  no store `#rankup_redemption_store_earn_xp`. Below: XP bar (`GetFriendXp / GetXpPerLevel`), rank icon
  `icons/xp/level<N>.png`; `care-package-eligible` when the active XP bonuses include `2` (`#tooltip_xp_bonus_2`: "Get a
  Weekly Care Package the next time you rank up!"), else `#rankup_redemption_store_rollover_wait` with
  StoreAPI.GetSecondsUntilXpRollover.
- tooltip_player_xp.ts: bonus `2` with a pet whose F < U adds `#tooltip_xp_bonus_pet_feed`.

## A pet in a match (server)

A pet is a `chicken` (CChicken) whose m_owner is its player and whose m_AttributeManager holds the pet item.

- SetOwner (18034fdd0): controller (180a969e0) -> pet item (180b0a450) -> level (1808c4e20); **only level > 1 (pullet,
  hen) becomes a match chicken** (else 0). Sets m_owner, the item into m_AttributeManager (181058270); model: an item
  without its definition loaded (+0x68 == 0) gets one of 4 stock `models/chicken/chicken.vmdl`.. (table 1817bd750, by
  (seed - 1) & 3 from 1813aa290), else the definition's model (181067140) and material group (181066ed0) at +0x11b0 / +0x11bc.
- Spawn (1803518c0): scale by level x 1.4; hull after the scale; SetHealth(1), SetMaxHealth(1), 1803ebce0(1, 0) (+0x2e0
  takes damage, +0x2e8 flags 0); the stuck duration. The colour is the item's style (the material group; set by the GC with the breed).
- Manager events: round_start -> 18034f710; round_freeze_end -> 18033bad0's 5 s timer -> 18033b940 (every +0x32e2
  cleared for good: stops following, squats); round_end with a winner -> 18034f4f0: pets whose owner or leader won do a
  trick now (1803506b0) and again at the next round start (+0x32e1). Game type 0 (classic) uses the team lists; game
  type 1 (deathmatch) 18034e060 every RandomFloat(10, 20) s spawns a pet on the general list for whoever has a pullet /
  hen and no chicken. Pets aren't startled by gunfire.

### The round's pets (18034f710)

Needs 18093df90, gamerules, the nav mesh and its area count > 0 (none: nothing at all, not even the cleanup).
1. Every `chicken` with an owner removed (180c30c10) unless the owner is +0x514 in {0, 3}, owns it (180a7a9d0 == chicken),
   is T or CT (+0x344 in {2, 3}) and still has the same item (+0xd48 == 180b0a470).
2. For each T / CT player with a pet item (180b0a470 != -1): no live pet (or one flagged +0x30 bit 9): a spot from the
   team's list (180354190), a new `chicken` (180bef630), SetOwner, 180a9b7f0, spawned (1803ea3b0, 180caa5f0); a live pet
   moved to a spot (1803ea3b0).
3. A pet with a leader (not flagged): GetNearestNavArea (1814bb3f0, flags 0x10, 10000) at the leader's abs origin; area
   width and depth both > 20: the pet goes to its centre (1814cb1b0) + (0, 0, 10) (180307f90); then +0x32e1's trick.
   (Also a ground trace 1802b7cb0: half hull + 71, 16 u.)

### Spots and paths

- Lists (180354bf0 -> 1803433b0): the enabled info_player_terrorist / _counterterrorist, each one's nearest nav area; a
  flood over the links keeping an area when its attributes lack 0x4, its step from the area it came from is <= 18 and
  (radius > 0) its centre is within the radius of a spawn (1803413f0 / 180341cc0).
- A spot (180354190): a random area of the list, a random point in it, the box above it clear, else another (as many tries as areas).
- Path (180399740, ChickenPathCost 1817be3f0): area refused with attributes & 0x10802, connection types 5 / 6, or step > 2
  (18034cba0); A* by distance.
- Nav meshes: maps/<map>.nav in the map's vpk (nested in a workshop vpk). de_dust2 v36.1 2242 areas,
  ze_atix_panic_2017_p 2445; ze_hold_em_p / ze_resident_evil_3 ship one with 0 areas, ze_dark_souls none.

### The graph (server 180a4f4e0 / 180a4c030)

- SetActivity: `action` = the activity's ID (DAT_182171410); the same action again sets `action_reset` (180a4f460), a new
  one clears it; `action_variation` = the given variation or RandomInt(0, 0x1000000).
- Each update: finished (+0x1e8) = this update's events hold ACTION_COMPLETED (timed-remaining state events), then
  action_reset clears (+0x1c0). Every chicken transition is m_rootMotionBlend "Blend"; a layer keeps its base's root
  motion (m_bOnlySampleBaseRootMotion); m_bSampleRootMotion off gives none.
- Root motion: copied as it is (1811d824c); 180342230 turns its translation by the yaw (181473df0), angles (0, normalised
  yaw, 0), Move(origin + delta); nothing when neither moves.
- Clip root motion: chick_walk 9.76 u over 1.267 s = 7.70 u/s, chick_run 104.34 u over 1.2 s = 86.95 u/s, chick_start_walk
  4.83 u/s, chick_walk_swim 20.76, chick_run_swim 87.68; turns chick_45l/r 2.14 rad/s, 90 2.77, 135 3.07, 180 3.25.

### Activities

0 IDLE, 1 SQUAT, 2 WALK, 3 RUN, 4 GLIDE, 5 LAND, 6 PANIC, 7 TRICK, 8 TURN_IN_PLACE, 9 FEED, 10 SHOULDER.

- SetDesired 1803515f0 (a settled pet only 0 / 1 / 6 / 7 / 8); Idle 180349410 (30 % squat); walk / run (+0xca0 vfn 0x60 /
  0x58: immediate while following); trick 1803506b0 (owned pets only); glide 180349180 on leaving the ground; land
  18034deb0 on landing; panic 18034da90 when the leader is steeply above (dir.z >= 0.9, on the ground, 3 s apart).
- The timer's end with nobody to follow: idle -> 30 % walk; squat / walk back to idle; run -> walk; land -> walk.
- A finished action (or a move waiting on its desired activity) switches to the desired one: idle / squat 1-5 s, walk
  1-3 s with a +-45 deg/s turn, run 1-4 s with +-45; land -> idle, panic -> run, trick -> idle, turn -> the trick after it (+0x32e0).
- Vocalize timer RandomFloat(0.5, 1).

### The think (180344730)

1. Removed when 1803d9090 is 1. The graph: the item's level (+0xd00 -> 1808c4e20) into 180a4f790, mode 4 (180a4f7d0).
2. Off the ground: `v += dt * m_flActualGravityScale (+0x40c) * g` (dt globals +0x34, g 180590fe0 vfn 0x98); Move(origin + v dt).
3. Startle timer (duration -1 from Spawn, no starter anywhere: dead for pets): on expiry, in activity 3 a 20 % chance (else
   50 %) of activity 6 (1803515f0(6, 1)), else flee from +0x115c (1803480c0). chicken_stop (0x4000) skips to Idle.
4. Following m_leader (activity not 7 / 8), every RandomFloat(0, 0.5) s (+0x1160): distance from the controller's origin
   (+0xca0 vfn 8) to the leader's: < 90 and not idle -> idle; 110 .. 180 and not 2 -> walk; > 220 and not 3 -> run.
   Walking to a leader (and fleeing within 150) restarts +0x1140 every think.
5. Walking / running, no flee target: hull trace to the leader (1802b5420, 0xc3011, filter 1817af9e0): clear (fraction 1)
   -> at the leader, else at +0x3298; `t = clamp((dist - 300) / 1700, 0, 1)`; facing (forward from the rotation
   quaternion, 182337ef0) . direction >= `0.96 - 0.253 t` -> +0x1158 = 0, else 360 deg/s toward the side (the cross's
   sign); the feelers can override; facing . dir >= 0.9 -> vfn 0x48; yaw += rate x dt (1803ea1a0).
6. Fleeing: away from +0x115c; past 150 u it stops (-1); within 0.7071 of the way out no turn, else 360 deg/s.
7. Follow (180354870): with a leader and +0x32e2: leader > 2000 u or path > 4000 stops it (180348300(0) + idle); else the
   path recomputed every 0.5 s (+0x3200, 180399740) unless its last point is within 100 u of the leader; the follower
   (+0x3218, 1803a22a0) steps along it; +0x32a8 restarts at 60 s.
8. The leader-in-sight test: a ray from EyePosition (vfn 0x5e8) to its abs origin (0xc3011, group 4, flags 0xf, exclude | 0xc0000).
- The chicken's eye: EyePosition is 18014d780 = abs origin + view offset (never written: the origin).

### Move(target) (1803507d0)

1. mins +0x40, maxs +0x4c, size = maxs - mins (18034f3f0).
2. Horizontal: a box with mins.z raised to mins.z + size.z (a plate at the hull's top: the step is its height), swept
   origin -> target by 180353d40 up to 3 times: no hit -> +0x1110 restarted (180338b80), end = target; a hit with
   `now >= +0x111c`, not jumping (sub vfn 0x50) and start-solid -> `end = (t - o) * 0.5 + o` (collision ignored); else
   slide: `d = t - o`, `dot = (d.y n.y + d.z n.z) + d.x n.x`, `t = (d + o) - dot n`; after 3 hits the last endpos.
3. Ground (not jumping): full hull from (e.x, e.y, e.z + size.z) to (e.x, e.y, e.z - size.z); in_water from +0x50 &
   0x18000 (180a4f760); a hit -> the ground endpos unless the normal is ~0 (all |n| < 0.01), n.z <= 0.7071 or start-solid
   (then e); SetAbsOrigin; not on the ground -> set it, SetAbsVelocity(0), Land; +0x112c = 0.
4. No hit, or jumping: origin e, off the ground, Glide (the vocalize timer restarted at RandomFloat(0.5, 1) unless gliding
   with it running, Chicken.Fly, activity 4 if movable).

### The sweep (180353d40)

- 0xc3011, group 5, ignore self, owner +0x3e4 unless collision +0x5a & 4, exclude |= 0x40000c0000, flags (b & 0xc9) |
  0x49; filter (1817af9e0, 180c2a810) skips players (0x558), byte +0x2f1 in {1, 2} and vfn 0x208 == 2: moving brushes and props are hit.
- Water: a second sweep from the start to (end.x, end.y, max(start.z, end.z) + 64), interacts-with 0x18000, flags | 4; a
  hit: `wz = endpos.z - 9`, and when the main end's z < wz the result is the water trace at z = wz.

### Feelers (1803423e0)

- `f = AngleVectors(-pitch, yaw, roll)` (up 45), `s = origin + (0, 0, height)`; `L = s + ((-f.y + f.x), (f.x + f.y), f.z) D`;
  `R = s + ((f.y + f.x), (-f.x + f.y), f.z) D`; `C = s + 32 f`; rays (1802b5420) 0xc3011 group 4.
- +0x32c8 running: dir (+0x32c0) 1 -> -360 else +360; else only R hit +360, only L -360, both: R.frac <= L.frac -> +360 dir
  2 else -360 dir 1, the timer started; none 0. Returns `turn * ((1 - C.frac) + 1)`. Non-zero steers instead of +0x1158.

### The jump (18034da90, activity 6)

When sub vfn 0x20's +0x3290 is null or its +0x40 & 8 is clear, not jumping, `curtime - +0x11f0 > 3`, on the ground:
+0x11d8 0.1 s, activity 6, last = now. The test is the body's up axis (182337f40) . the way to the leader >= 0.9.

### +use and the ping

- 180345830(ch, player, checkDist): null -> return; checkDist and `(dy^2 + dx^2) + dz^2 > 1e6` -> return; movable
  (+0x32e2) -> follow 180351300 (reuse timer +0x11c0, 1 s); else with an owner -> 180346f60 (turn_angle =
  `V_atan2f(cross, dot) * 57.295776` against its facing) and a trick after.
- Use (180341f50 -> 1803457e0): the activator only when IsPlayer (0x558) and alive (0xca8), checkDist 1.
- ObjectCaps (18034f440): `base() | 1`; base 180d04f60: 0x80 with no move parent, else `parent & 0x87` (| 0x80 for a
  player parent). A pet: 0x81: FindUseEntity finds it by the look trace only.
- Ping (180ab7ec0): the eye trace's entity when a CBaseAnimGraph (RTTI 181ebbe30), ranked by 180ac6b50 (CPlantedC4 4,
  CCSWeaponBase 3, CItemDefuser 2, CChicken 1, else 0). Below rank 3 a 46-unit sphere query at the hit; a candidate wins
  with rank > 1, rank >= the current, WorldSpaceCenter within 36 and (higher rank or nearer). A chicken is pinged only
  when the eye ray hits it; a weapon / defuser / C4 within 36 beats it.
- Placement (180adb580(ping, pawn, urgent, param_4, ent, pos)): type `param_4 ? 0x18 : urgent ? 13 : 0`; an entity: C4 at
  its abs origin 0x19, else at WorldSpaceCenter with weapon 1, defuser 0x1b, chicken 0x1a. Life `param_4 ? 30 : 6`.
  **A pet is used by the ping only in the freeze time**: `type == 0x1a && g_pGameRules && m_bFreezePeriod && HasOwner
  (180343fd0)` -> 180345830(ch, pawn, 0) (no distance check), the ping lasts 1.0 s.

### Hurt and killed

- TakeDamageOld (1803ed610): `amount = floor(damage)` (1816c4664), the fraction + carry (+0x2dc), carry >= 1 adds one;
  damage-info flag bits 4 / 3 clamp it; health -= amount; before > 0 and after <= 0 with life state 0 -> life state 1,
  Event_Killed (vfn 0x418); a true return -> vfn 0x420.
- Event_Killed (180347350): Chicken.Death (180f695d0); the pelvis; model index (1808d4c60); DMG_BURN (+0x4c bit 3):
  chicken_roasted.vpcf at the pelvis, CP1 (index == 3 ? 1 : 0, 0, 0); DMG_SHOCK (bit 8): chicken_tased.vpcf; else +0x32e3
  = 1, 1803c5900(0x420), next think now + 3, no particle here. Holiday mode (18093d4e0): weapon_confetti_omni.
- A leader: TextMsg type 3 "#Pet_Killed" (" Your chicken has been killed. She was yours for %s1 seconds.") with now -
  +0x32a4 ("%d" from 1 s, else "%.1f"); the follow stops (180348730 / 1802805e0), m_leader = -1; 180922960; base
  Event_Killed 180bad480. Returns +0x32e3 == 0.
- Client 180d51420: chicken_gone.vpcf at the pelvis (CP0), CP1 = (model index, material group 180943590, 0), the model's
  material bound (180a11370), then 180d45c90.

## Client

### The controller (18084a1b0)

- Params: action, action_reset, action_variation, in_water, mode, life_stage, idle_phase, turn_angle, has_lookat_target,
  lookat_target, flinch, flinch_variation. in_water, has_lookat_target, lookat_target: no client writer (networked; the menu leaves them false).
- Activity -> action (180860180): 0 idle, 1 squat, 2 walk, 3 run, 4 glide, 5 land, 6 panic, 7 trick, 8 turn, 9 feed, 10
  sleep, 11 shoulder, 12 low_on_food (the server's table differs past 9).
- PlaySequence (18085c680): chick_chicken_reveal / _reveal02 / chicknegg_hatch01 / 02 -> action_reveal with variation 0 /
  1 / 2 / 3; chick_retirement01 / 02 -> action_retirement with 0 / 1 (action_reset when already that action); a model
  without a graph plays the sequence itself (1809657b0).
- Flinch: 180852000; the post-update 18085d0e0 clears +0x1e8, sets it from this update's events, writes flinch back to 0: one update.

### ApplyState (180d4f1b0(ent, var))

ent+0x1b90 = var; the "feed" / "placement" attachments (entity handles: with both, the pet takes the placement's abs
origin and angles); `life_stage = tbl[UpgradeLevel (3 when missing or >= 5)]`; `mode = tbl[ent+0x1b88]`; SetActivity:
the action, variation `(float)(var < 0 ? RandomInt(0, 0x1000000) : var)`.

### The vanity frame (180d43380)

- On ACTION_COMPLETED: an egg -> 0; else (not 11) from 0: r < 0.1 squat, < 0.2 sleep, < 0.3 feed when the "feed"
  attachment entity exists; from anything else 0 while +0x1b8c < 3, else squat / sleep (0.5); squat / feed / sleep zero
  the count, a trick adds one; ApplyState(-1).
- An egg: `f = (no GC time ? 1 : clamp(1 - (float)(int64)max(0, deploy - now) / 432000.0f, 0.05f, 1))`,
  `idle_phase = (float)(int)floorf(f * 4)`: 0..4, a step every 1.25 days.
- After the graph part: the "feed" entity and a pending feed_anim -> that entity plays the sequence of that name (1809529a0,
  1809657b0 cycle 0, 18093e020(0), rate 1 vfn 0x108, +0x330 vfn 0x70 -> vfn 0x78(0x40)), the key removed (1808311d0).
  chicken_feed.vmdl has no graph: full / empty (loop, held) and interact (1 s).

### Interact (180d4e890)

param_3 the entity clicked; feed = its identity +0x18 (name) is "feed" (1815bc1c0).
1. Egg: idle -> panic, done.
2. Feed and now < low-food date -> feed_anim "interact", Chicken.Feed.Seed (1.0, 0.5, 1.0).
3. Busy (activity != 0): feed -> nothing, else flinch.
4. Idle: Chicken.Idle.Chick / .Pullet / .Hen, then activity feed ? 9 : 7 and the trick count rule.

### The feeder (180d520f0)

1. Mode 1 (+0x1b88) with level > 0: the cs_pet_placement (1809dfb70) and the pet's "feed" handle (180802c40); none -> a
   C_DynamicProp named "feed", models/chicken_feed/chicken_feed.vmdl (1809643c0), owner the pet (vfn 0x1b0), render mode
   from the pet (180b9b620), stored as "feed", the placement as "placement" (180802e50).
2. Every check: 181748480(placement origin w 1, AngleQuaternion(placement angles), local `(-15.1731, 11.6387, 0) * s` w 1
   (s = pet scale), AngleQuaternion(0, 0, 0)): `origin + rotate(quat, local)`; SetAbsOrigin, QuaternionAngles ->
   SetAbsAngles; scale `s * (1.75 for a chick, else 1)`.
3. feed_anim (180d42f50) = "full" when now < low-food date, else "empty".
4. Activity: fed and 12 -> 9; low and not 12 -> 12; ApplyState(-1).

### The nest (180d52620)

A level 0 pet in mode 1 or 2 gets a C_DynamicProp of models/nest/nest.vmdl (made once, the pet's "nest" handle, vfn 0x1b0
with the pet) at the pet's abs origin, angles and scale; otherwise the nest is removed (180a1b890).

### Overhead name (180ed0210)

- Every `chicken` with an owner (+0x14c4) and drawn (+0x52c bit 5 clear): a MiscOverhead panel, Content offset (0, 0, 18),
  a misc__label; owner's name and item name (180d567a0) in #HUD_overhead_pet_quoted, #pet_chicken in _unquoted without an item.
- At the "pelvis" bone, scale clamp(atan(512 / d), 0.6, 1.4285715) (x 0.7 in 180ecb3d0), opacity the render alpha.
- Visible when the trace (18022fee0: ignore you, or the watched player in mode 2; flags (b & 0xc9) | 0x49) hits the pet
  or reaches the point and the view ray passes within 10 u; param+0x70 = show team equipment (held: every pet name shows).

### Camera blend (180b833b0 / 180b82920)

- A new camera: prev (+0x30) = current target, cur (+0x28) = new, dur (+0x40), start (+0x3c) = Now(), frac 0, blending; time 0 sets it.
- Each frame: frac = smoothstep (1808a4520: `t = clamp((x - a) / (b - a))`, `(3 - 2t) t^2`). Origin lerped (0xa8 ..
  0xb8), fov lerped (0xd8), angles (0xc0, 180b595e0): AngleQuaternion of each, the fitted slerp, QuaternionAngles, roll included.

### The egg's graph

egg_pristine_world.vnmgraph (skeleton animation/skeletons/egg/pristine_egg_world.vnmskel, 2 bones, 15 clips):
action_idle picks chick_egg_idle_phase01_still..04 by idle_phase, action_panic the reactions 01-08 by variation,
action_viewmodel the viewmodel clips.

### Inventory picture

GetInventoryImage (18118d3d0) for `pet`: pet id -> definition (181134ad0) +0x20 pedestal_display_model; ItemImage
(180dcaa00): 181190590 true -> "file://{images}/<model>.png" rendered at runtime (180e536d0, type 2). chicken_feed keeps
its static image + "_%u" of the pet seed.

### The party's pets

- mainmenu.ts _UpdatePlayerVanityModel: every lobby member's vanity presence (PartyListAPI.SetLocalPlayerVanityPresence:
  team, character, gloves, slot, weapon, **pet item**); player index 0 -> SetPetPlacement('main-menu-foreground'), the
  rest 'main-menu-background'; no pet -> 'none'. sessionutil.ts BCanUseMyPetInCurrentLobby: alone, or the lobby host
  (the panel's hover and zoom only).
- SetPetPlacement names (180e5e960): none 0, shoulder 1, main-menu-foreground 2, main-menu-background 3, end-of-match 4 (into +0x98).
- 180cada50: each preview character owns its pet (+0x3760); a new one replaces it (180cbb290), owner link vfn 0x1b0,
  placed (180cae080); mode +0x1b88 = 1 / 2 / 3 for 2 / 3 / 4, else 0; the item (180d4db50); placement 1 -> 180d48bb0,
  else the nest (180d52620) and the feeder (180d520f0).
- 180cae080: 1 shoulder: parented (180219680, attachment hash 0x119bcd9) at local (7, -1, -3.5), angles (180, -90, -20),
  activity 11; 2 foreground: unparented at cs_pet_placement's origin and angles (none: as 3); 3 / 4: unparented at the
  character's origin + rotate(its quat, (15, 0, 0)), its angles with yaw + RandomFloat(-30, 30); 5: the character's
  origin, angles and scale.

## The photo booth and the HatchBook (panorama; no DLL read)

Panels: popup_pet_photobooth.{xml,ts,css}, pet_photo_tag.ts, pet_photo_library.{xml,ts,css}, popup_pet_book.{xml,ts,css},
pet_book_pages.ts, pet_book_turn.ts, pet_book_page_styles.css, context_menu_photo_viewer.{xml,ts,css}; the stage maps
(game/csgo/maps/ui/pet_photo_studio.vpk, ui/pet_photo_park.vpk, warehouse_vanity.vpk); the graphs chicken / uimodel.

### Opening

- vanity_pet_info.ts shows `id-photo-booth` and `id-pet-book` from upgrade level 1 (`hide` below). _OpenPhotoBooth passes
  pet_id, upgrade_level (+ action-type / title / msg / callback, unused); _OpenPetBook opens the book bare.
- The booth's OpenBook: spread = book_spread, booth_setup = the setup string, from_booth = 1; the book's OpenPhotoBooth:
  pet_id, upgrade_level, book_spread, booth_setup, from_book = 1 (only with a live pet).
- Setup string `key:value;key:value` of stage, paper, pose, aspect, filter, headwear and every adjustment slider,
  applied .25 s after the booth opens (after the filters reset).

### The stage

- A MapPlayerPreviewPanel (`cam_pet_photo`, pin-fov vertical, panzoom, drag rotate, yaw limit 30).
- STAGES: studio `ui/pet_photo_studio` (id 0, default), picnic `ui/pet_photo_park` (1), warehouse `warehouse_vanity` (4,
  age_requirement 2), airport / dust2 / mirage / inferno / nuke / cache / train / ancient `<map>_vanity` (3, 2, 5..10,
  achievement `visited-<map>`).
- Studio entities: csgo_item_previewmodel `pet1` (-30.5, -450.4, -255.8, yaw 282.9: the solo pet), csgo_player_previewmodel
  `vanity_character6` (-33.9, 54.8, -255.9, yaw 262.8: the posed agent); cameras `cam_pet_pose_solo_intro`,
  `cam_pet_pose_solo_0..3` (by growth: solo_1 chick, _2 pullet, _3 hen), `cam_pet_pose_intro`, `cam_pet_pose_1..10`
  (vfov 35); 9 effects as info_particle_system (start_active false) in two sets (`explosion`, `lightning`, `fire`, `beam`
  (photo_ufo), `lasers`, `sparks`, `confetti`, `bubbles`, `feathers` by the agent; `solo_*` by pet1:
  particles/pet_photo/<name>/photo[_solo]_*.vpcf); post volumes (post_vanity master; pet_post_normal / bw / sepia / warm /
  cool / crisp / moonlight / silvertone / psychedelic, _bloom, _exposure_up / _down, _vibrance_up / _down, _contrast_up /
  _down, _saturation_up / _down: lighting/postprocessing/effects/pet_*.vpost); two prop_dynamic `backdrop`
  (models/photobooth/photobooth_backdrop.vmdl, 11 material groups: paper grey / blue / green / purple / yellow / brown /
  red / black, sky, wallpaper, abstract); light_barn `chick_light`, `agent_light` (the colour picker's SetColor targets).
- The park: the same names (pet1 (159.2, -367.9, 35.4) yaw 8.3, vanity_character6 yaw 348.2).

### Poses

- POSES `0` (solo) and `8 9 10` (orbit 80) `2` (100) `4` (110) `5` (80) `6` (90) `1 3 7` (100).
- A pose: ResetPanZoom, ResetDragRotate, SetDragRotateRadius(orbit; solo 36 / 45 / 55 by growth), SetZoomLimit(25), the
  intro camera at once (`cam_pet_pose_solo_intro` / `cam_pet_pose_intro`), then the pose's camera over 2 s.
- Solo: SpawnItem (growth entity `chick` / `teen` / `adult`, pet, '', 'pet1') once, its Alpha 255 and dynamic_player6's 0.
- Posed: the loadout's agent for the team (`customplayer`, `clothing_hands`), SetActiveCharacter(6), SetPetPlacement('origin'),
  EquipPlayerWithPet, PlayChickSnapshotAnimation(pose).
- Agent graph (uimodel.vnmgraph state `chick_snapshot`, node 811): SM -> ParameterizedClipSelector on `chick_life_stage`
  (egg / baby / adolescent / adult) -> ParameterizedClipSelector on `chick_snapshot_variant` over
  `chick_snapshots_char01..10[_adolescent|_baby]` (taken: variant = pose - 1, life stage = upgrade level).
- Pet graph `SM/Snapshot` (node 168, entered by action == action_snapshot) -> by life_stage -> ParameterizedClipSelector on
  action_variation (node 6) over `chick_snapshots_01..10[_adolescent]`: one-frame poses whose root sits in the agent's
  hands (04: root (-11.6, -19.8, 56.2)), so the pet stands at the agent's origin (18085c990). A selector picks once; the
  one-frame clip says ACTION_COMPLETED at once (the pose holds).
- Age gates (_ApplyAgeGates): poses 8-10 only up to the chick (#pet_photo_booth_age_outgrown), 2 4 5 6 from the pullet
  (_dangerous), 1 3 7 from the hen (_maturity); effects sparks / laser / beam from the pullet, fire / lightning / explosion
  from the hen unless the pet has killed-by-burn / -taser / -planted-c4 (#pet_photo_booth_age_scary_brave); activities
  jump / wag / moonwalk from the pullet, kick / fly from the hen (_age_tricks). Team buttons off in the solo pose; the
  light button only in the studio.

### Activities and effects

- ACTIVITIES (SetPetActivity[AndVariation]OnItem): sit = trick 2, panic = panic, wag = trick 9, moonwalk = trick 5, jump =
  trick 11, kick = trick 12, fly = trick 1; only in the solo pose, one at a time.
- _TickActivity polls every .1 s: the first time the pet's activity is the row's it plays the row's sound for the growth
  (sit: Chicken.Idle.Single.Chick.PhotoBooth / Chicken.Idle.Single.PhotoBooth; panic: Chicken.Panic.<Chick|Pullet|Hen>.PhotoBooth);
  ends when the pet has left it, after .5 s unseen, or at 5 s. GetPetActivityOnItem's variation -1: random.
- PlayEffect: Chicken.Camera.FX + the effect's Photobooth.FX.* sound, Chicken.Idle.<growth>.PhotoBooth .5 s later, the
  system (`solo_` prefix in the solo pose) Start, Stop 1 s later.

### Hats

- HEADWEAR 0-9: helmet, armor (armor_helmet), alien, banana, glasses, nose_glasses, party, sprout, top_hat, wizard_hat
  (models/photobooth/silly_hats/*.vmdl).
- AttachModelToItemWithScale(model, pet, 'eyewear_attach' for a *glasses* model else 'head_attach', scale 1.0 chick / 0.43
  pullet / 0.55 hen). head_attach on `head`, offset (0.776, -0.070, 0), rotation (0.706, 0, 0, 0.708). The hat models are
  skinned to a `head` bone of their own.

### Adjust and filters

- aAdjust (type, kind, min, max, default): exposure / saturation / vibrance / contrast post-pair -1..1 0 (up volume weight
  = max(v, 0), down = max(-v, 0)); brightness 0.8..2 1 (the 3D panel's `brightness` style); bloom post-single 0..1 0;
  vignette 0..0.8 0.14, grain 0..0.7 0, grime 0..0.5 0 (overlays: opacity, hidden at 0); filter-strength 0..1 1 (the
  filter volume's weight). Reset: all but the strength. Grid slider 0..0.5, 0.1 (the grid's style says .25 until it moves).
- FILTERS 0-8: normal, bw, sepia, warm, cool, crisp, moonlight, silvertone, psychedelic: the old `pet_post_<f>` Disable,
  the new Enable, the strength row hidden for normal, strength back to 1. Settling a stage disables post_vanity and every
  filter, Enables every adjust volume.

### Formats and the shutter

- ASPECTS (id / name): 3 1x1, 1 4x3, 2 5x4, 0 16x9, 5 3x4, 4 4x5, 6 9x16; frame class photo-booth-ratio-<a> (896 x 896,
  1195 x 896, 1120 x 896, 1120 x 630, 765 x 1020, 816 x 1020, 484 x 1020, padding 16); the orientation buttons swap the
  shown set and flip the checked one (FlipAspect: 4x3 <-> 3x4).
- TakePhoto: the composition layer named by the aspect, then (3 2 1 with UI.Premier.CounterTimer a second apart)
  _WritePhoto after .1 s: `pet_<Date.now()>` + PetPhotoTag.Compose + `.jpg`, WriteCompositionLayerJPEG (PreparePetPhoto's
  path in USRLOCAL pet/<id>/library, long edge 1200, quality 95), the white flash (.5 s), Chicken.Camera.Shoot;
  _VerifyPhoto after .2 s, retried 4 times, then the #pet_photo_save_failed popup.
- Zoom readout every .1 s (#pet_photo_booth_zoom_readout; bands wide 0-9 / mid 10-19 / closeup 20-25),
  Chicken.Photo.ZoomIn / Zoomout on a change.

### PetPhotoTag

- Compose: `_p<pose>_f<filter id>_s<stage id>_g<growth>_a<aspect id>_z<zoom>[_v<activity id>][_e<headwear id>]`; Parse skips
  the first two `_` tokens.
- Book name `book_<stem>_k<page>_y<layout id>_l<slot>[_x<x>_w<y>_m<zoom>]` (slot 255 = unplaced; the frame only when not
  50 / 50 / 100; zoom 100-300); RollName strips k y l x w m.
- Describe's order g z s v e f p with the caption tokens; a hole's require string `name:a|b,name:c` (growth / zoom bands /
  stage / pose / filter / activity / headwear), Unmet / Matches / TermWords (`<loc><name>_inline` when it exists).

### The library

Folder names sorted, reversed (newest first), rows 200 x 96; hover: the settings tooltip (`tooltip-pet-photo-settings`)
and the trash button (#pet_photo_library_delete_* yes / no, DeletePetPhoto); click: the viewer context menu (image up to
640 px, copy to clipboard, open the folder); the book's rows drag. Files: USRLOCAL `pet/<pet item id>/library|book` and Steam Cloud.

### The HatchBook

- LAYOUTS (id / snippet / holes): intro 1 (zoom:closeup), feet 2 (zoom:wide), early-days 3 (pose:8|9|10), chick-park 4
  (stage:picnic), teen-warehouse 5 (stage:warehouse), teen-trip-1 6 (stage:dust2|airport|inferno|train), teen-trip-2 7
  (stage:mirage|nuke|cache|ancient), birthday 8 (activity:jump, headwear:party), adult-perch 10 (pose:1|3|6|7,
  filter:sepia), adult-tricks 11 (activity:kick|fly), adult-close 13 (pose:4|5), brave-fire / -taser / -c4 15 / 16 / 17
  (achievement killed-by-burn / -taser / -planted-c4, no holes), free 14 (slots 0 | 1 2 | 3 4 5 | 6 7 8 9: single /
  pair / trio / quad).
- Sections: chick (stage 1) intro, feet, early-days, chick-park, free, free; pullet (2) teen-warehouse, teen-trip-1,
  teen-trip-2, birthday, free, free; brave (3) the three; hen (3) adult-perch, adult-tricks, adult-close, free, free.
  Every hole also requires the section's growth.
- A page shows when unlocked (no achievement, or photos on it, or the achievement) and (the pet hasn't outgrown its
  section, or it has photos, or a photo of either folder fits a hole).
- Paragraphs: `<token>_<capture ms of slot 0's photo % variants>` with the pet's names (pet_name, pet_name_1..3: a
  stage's name, else an earlier, else a later, else the item's) and the hatch date (#pet_book_hatch_due for an egg).
- The book is the live pet's, else the newest book (GetPetBookCloudFileKeys' last).
- _Reconcile on open: a roll photo whose capture time is in the book is deleted; a book photo unplaced, on a page whose
  layout changed, or doubling a hole or a photo goes back to the roll.
- A drop: the hole must take it, and a displaced photo must fit where the dragged one came from (else back to the roll);
  Chicken.Photo.Pickup / Accepted / Rejected; a slot's photo dragged off the book goes back to the roll.
- Frame bar (260 x 156, beside the slot): zoom 100-300, pan x / y (enabled when the photo overflows the hole that way),
  committed into the name .4 s after the last change.
- PetBookTurn: PAGE 560 x 640, MARGIN 8, the book 1136 x 768; sides blank, cover, pages, [blank], back; FLIP 650 ms, ease
  `(smoothstep t)^0.72`, leaf shade 0.32 (x1.25 on its back), cast shadow 170 px at 0.28, gutter 0.40, page shadow
  `0.40 * |sin|` (x |sin(a/2)| opening / closing); closed, the book sits half a page left; sounds UI.BookOpen / Close /
  PageFwd / PageBwd; a turn asked mid-flight runs after.
- Bar: prev / next, a chapter button per section shown (pet_chick / pet_pullet / pet_field_report / pet_hen icons),
  `#pet_book_page_counter` {page} / {total}.
- Stickers: locked (#pet_photo_booth_no_stickers).

## Unread

- server: m_iPetPopulation 18029d180; what +0x3290 is (taken: the nav area, its NO_JUMP bit) and who sets +0x2f1; whether
  the ping ray (0x1c1003) hits a chicken (its interacts-as layers); whether animationsystem scales root motion by the
  world transform (1811e12e0 carries it with its scale); 180341cb0's yaw composition; animationsystem's own root motion
  sampling and blend; a bullet / knife on a chicken (hitboxes, penetration); the damage-info flag clamps; 1803c5900(0x420);
  other_death (1801d0290) and the kill feed; 18034f710's step 3 past the ground trace.
- server think past line 400 of the decompile: the idle / squat / activity switch (18034560c), the activity timer's
  choices, vocalizing (m_vocalizeTimer, Chicken.Idle.*), stuck handling.
- client: the dynamic image generator's camera, pose and lighting (180e536d0); upgrade level 4's life_stage; who calls
  Interact (the map panel's pick on a click); the shoulder placement's caller; the end-of-match line-up's pets;
  PlayChickSnapshotAnimation; AttachModelToItemWithScale's maths (taken: at the attachment, scaled); how several weighted
  post volumes combine; MapPlayerPreviewPanel's pan / zoom / orbit; LocalizeRentalDate's format; the composition layer's resolution.
- The colour / pattern draw from `pet seed` (client `chicken_metadata`) and the breed draw (GC).
- The XP rules (GetXpPerLevel, the weekly bonus), the PersonalStore's generation, the pet achievements (GC).
