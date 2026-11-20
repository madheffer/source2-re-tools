# Pets: CS2's chicken pets, the Weekly Care Package (client_20261015, server_20261105, pak01)

The pet system arrived with CS2's Rush Hour update (2026-09-22). Most of the timing is the Game Coordinator's (it
writes the pet item's date attributes); the client reads those dates through the functions below, so their constants
are CS2's and their inputs are the GC's. What the GC decides (stage lengths beyond what the client's constants pin, a
feed bag's time, the breed / colour draw) is a labelled stand-in in our code.

## Where it lives (2026-11-16)

| Piece | Code | Traced from |
|---|---|---|
| The pet's clock (stages, food, expiry) | src/cs2web/player/pet-clock.js (server and client) | client 180d48150 / 180d481f0 / 180d467d0 / 180d4e340 / 180ffd4e0 |
| The GC's writes (hatch, upgrades, feed, breed, colour = item style) | server/cs2web/econ/pet-gc.js (labelled stand-ins), pet-store.js | not in any CS2 file |
| Weekly Care Package, XP | econ/care-package.js, xp.js, xp-store.js, pet-routes.js; client home/pets/care-package.js | rankup_redemption_store.ts; XP amounts GC stand-ins |
| Match pets: placement, activities, think | server/cs2web/pets/pet-chickens.js, pet-spots.js (nav: world/nav-mesh.js, lasers-bake --nav) | server 18034f710 .. 180344730 (below) |
| Movement: Move, sweep, water, fall, root motion apply, feelers | pets/pet-move.js | server 1803507d0 / 180353d40 / 180342230 / 1803423e0 |
| The chicken graph on the server (events, root motion) | pets/pet-graph.js; anim-graph/root-motion.js | server 180a4f4e0 / 180a4c030 |
| +use, ping | combat/use-pick.js, combat.js; comms/ping.js | server 180345830, 180ab7ec0 / 180adb580, ObjectCaps 18034f440 |
| The network | src/cs2web/net/pets-codec.js (binary delta frames) | ours |
| Drawing in a match, sounds, overhead name | client/fx/pets-view.js, world/pet-body.js, hud/pet-names.js | client 18084a1b0, 180ed0210 |
| The home's pet, egg and nest | home/menu-scene.js, home/pets/menu-pet.js, pet-info.js, pets.js | client 180d43380 / 180d4f1b0 / 180d4e890 / 180d520f0 / 180d52620 |
| The home's feeder (feed, the feed click) | home/pets/feeder.js, menu-pet.js interact(feed) | client 180d520f0 / 180d42f50 / 180d43380 / 180d4e890 ("Third pass") |
| The party's pets in the home | home/pets/party-pets.js; lobby/party.js presence, home/party.js | mainmenu.ts, client 180cada50 / 180cae080 / 180e5e960 |
| Pets hurt and killed in a match | server/cs2web/pets/pet-death.js; combat.js, grenades.js; client/fx/pets-view.js die | server 1803518c0 / 1803ed610 / 180347350, client 180d51420 |
| Inspect | home/pets/pet-inspect.js | vanity_pet_info.ts InventoryItemPreview |
| The camera blend | home/cam-blend.js | client 180b833b0 / 180b82920 / 181744420 |
| Pet event popup | home/pets/pet-event.js (on the home scene) | popup_pet_event.ts / .vcss, client 18085c680 |
| Photo booth, HatchBook, the photos | home/pets/photo-booth.js, booth-*.js, pet-book*.js, photo-tag.js, photo-library.js, photo-store.js; server econ/pet-photos.js | popup_pet_photobooth / popup_pet_book / pet_book_* / pet_photo_* panels (below) |
| Inventory tile and picture | home/cases/econ-inventory.js, home/pets/pet-picture.js | client 18118d3d0 / 180dcaa00 |
| Dev commands | client/console/pets-dev.js (pet_give / skip / food / remove / status / preview / event, carepackage, xp_*) | ours |
| Assets | lasers-bake --pets (web/public/ze-pets: models with attachments in models.json, colours, icons, sounds, the death particles in fx/, the panels for reference incl. the photo booth and HatchBook), tools/tp-graph.mjs (anim, anim-egg) | pak01 |

Tests: econ/pets-test.mjs, pets-db-test.mjs, net/pets-codec-test.mjs, pets/pets-match-test.mjs (headless on
ze_atix_panic_2017_p: spots, settle, turn by root motion, follow, frames). What's still unread: "Still unread" at the end.

## The items (pak01 scripts/items/items_game.txt)

| def | name | item_class | notes |
|---|---|---|---|
| 4681 | `pet` | pet | `#CSGO_Type_Pet`, loadout slot `pet`, rarity rare, quality unique, `cannot trade` 1, nameable |
| 4948 | `chicken_egg` | chicken_egg | `#chicken_egg`, image `econ/pets/chicken_egg`, pedestal `models/chicken/egg_pristine.vmdl`, `upgrade level` 0 |
| 4949 | `chicken_feed` | chicken_feed | `#chicken_feed` ("Feed your pet to keep it around."), image `econ/pets/chicken_feed_bag`, pedestal `models/chicken_feed/chicken_feed_bag.vmdl`, `upgrade level` 0 |

`pet_definitions` (the `pet id` attribute's values): 1 `chicken_egg_01` (egg_pristine), 2 `chicken_chick_01`
(`#pet_chick`, chick.vmdl), 3 `chicken_catalana_01` (`#pet_chicken`, chicken.vmdl), 4 `chicken_silkie_01`
(chicken_silkie.vmdl), 5 `chicken_polish_01` (chicken_polish.vmdl). server 181012e60 parses them ("name must be a
positive integer").

The pet's attributes: 296 `pet id` (pet_id, hidden), 180 `deployment date` (value_is_date: the hatch date; an egg's
is its due date), 268 `upgrade level` (0 egg, 1 chick, 2 pullet, 3 hen), 303 `pet food expiration date`, 304 `pet
next upgrade date`, 313 `pet seed` (pet_seed: the colour / pattern draw), 111 / 328 / 329 `custom name attr` / `2` /
`3` (one name per stage: vanity_pet_info.ts reads `custom name attr` + (level >= 2 ? ' ' + level : '')).

`ItemInfo.IsPet` (common/iteminfo.ts) is true for `pet`, `chicken_egg` and `chicken_feed`.

## The pet's clock (client_20261015.dll)

The Panorama natives are registered in 180fd4f50 (InventoryAPI): GetPetItemID 180faee60,
TryAckPetEventAndCheckExpiration 180ffd4e0, RestorePetItemData 180fedb70, GetPetGrowthPercent 180faeb50,
GetPetFeedAmount 180faeab0, GetPetLifetimeRemaining 180faeeb0, IsPetLowOnFood 180fd13d0, PetHasAchievement 180fe3f80,
GetPersonalStore 180fae490. Each looks the item up (V_atoui64 of the id, 18083b8f0) and calls the item helper below.
`now` is the GC's rtime (18118bef0 -> 18118d1c0). The clamp is 1801587b0 (value, min, max).

Item helpers (attribute reads through the item's vtable + 0xe8, the attribute found by name through 18112e7e0):
- 180d46430 `deployment date` (D); 180d48480 `pet next upgrade date` (U); 1807232d0 `upgrade level` (L).
- 180d48320 the low-food date: F = `pet food expiration date`; returns 0 when F is 0, else
  `min(F - 0xbdd80, (D ? D + 0xb89200 : 0) + 0xbdd80)` (0xbdd80 = 777600 s = 9 days; 0xb89200 = 12096000 s = 140 days).

- **GetPetGrowthPercent** 180d48150 (the egg's ring): L == 0 only (else 1.0):
  `clamp(1 - max(D - now, 0) / 432000.0, 0.05, 1.0)` (432000 s = 5 days; 0x3d4ccccd = 0.05).
- **IsPetLowOnFood** 180d4e340: `lowFoodDate(item) <= now`.
- **GetPetLifetimeRemaining** 180d481f0 (the chick / pullet / hen rings): needs D != 0 and D <= now (else 1.0).
  end = max(min(U, D + 140 d), D + 1); start = D (chick), U - 0x24ea00 (pullet: U - 28 d), D + 0x41eb00 (hen: D + 50 d);
  returns `1 - clamp((int)(now - start) / (float)(end - start), 0.02, 1.0)` (0x3ca3d70a = 0.02).
  So the stages are pinned as: chick D .. D + 22 d (pullet's U - 28 d = D + 22 d when U = D + 50 d), pullet .. D + 50 d,
  hen D + 50 d .. D + 140 d. The 22-day chick (U at hatch = D + 22 d) is the GC's: a stand-in that matches the client's
  other anchors and the community's observation.
- **GetPetFeedAmount** 180d467d0 (the feeder's fill): lo = lowFoodDate, up = U, cap = D ? D + 140 d : 0. If lo <= up and
  lo < cap: `f = clamp((int)(lo - now) / 1036800.0, 0, 1)` (12 days), returns `max(f * f * 0.4, 0.001)` (1801b9c30 with
  0x3a83126f). Otherwise the stage's progress: start = D, U - 28 d (L 2), U - 90 d (L 3, 0x76a700 = 7776000);
  `clamp((int)(now - start) / (float)(U - start), 0, 1)` when start < U, else 0. (The decompiler drops the float
  return; the second branch's exact use of the clamp still to read in the disassembly.)
- **TryAckPetEventAndCheckExpiration** 180ffd4e0: reads `pet id`, `deployment date` (D), `upgrade level`, F, U; the pet
  is due an upgrade event when U <= now (a looked-up definition first when L != 0); it has expired when F < now or
  D + 140 d < now: "maxage" when D + 140 d <= F, else "nofood". On an event it sends k_EMsgGCAckPetEvent (0x9ea) at most
  once per RandomFloat(10, 300) s. The popup's lines: pet_expired_notification_* (title_nofood_egg for an egg),
  pet_upgrade_notification_msg_<L>.

## The Weekly Care Package (panorama/scripts/rankup_redemption_store.ts)

- The store is the GC's `PersonalStore` cache object: `generation_time`, `items` (four item ids; `'-'` x4 when there's
  none), `redeemable_balance`.
- A claim costs 1, but 2 for `chicken_egg` or `chicken_feed` (`_GetClaimCost`); a tile can be selected while the
  selection's cost + its cost <= balance; selecting plays UIPanorama.gift_deselect, deselecting gift_select (CS2's own
  swap), a refused pick pulses the selected tiles with UIPanorama.buymenu_failure.
- Redeem: nothing selected pulses every unclaimed tile; inventory full (NUM_BACKPACK_SLOTS) refuses;
  `StoreAPI.StoreRedeemFreeRewards("id,id")`, a 10 s timeout popup (#rankup_redemption_store_timeout_*); the GC answers
  with `free_reward_redeemed`, the claimed tiles play `reveal-anim` + UIPanorama.gift_claim. Claiming a pet item while
  not the lobby's pet host closes the lobby (LobbyAPI.CloseSession) and zooms the menu onto the pet.
- Badge: balance > 0 `#rankup_redemption_store_directive` ("Claim your rewards"); a store with 0 left
  `#rankup_redemption_store_closed`; no store `#rankup_redemption_store_earn_xp`. Below: XP bar (`GetFriendXp /
  GetXpPerLevel`), the rank icon `icons/xp/level<N>.png`; `care-package-eligible` when the active XP bonuses include `2`
  (`#tooltip_xp_bonus_2`: "Get a Weekly Care Package the next time you rank up!"), else `#rankup_redemption_store_rollover_wait`
  with the time to the week's rollover (StoreAPI.GetSecondsUntilXpRollover).
- tooltip_player_xp.ts: bonus `2` with a pet whose F < U adds `#tooltip_xp_bonus_pet_feed`.

## A pet in a match (server_20261105.dll)

A pet is an ordinary `chicken` (CChicken) whose `m_owner` (+0x11ac, a handle) is its player and whose
`m_AttributeManager` (+0xcb0) holds the pet item. CChicken's fields (schema): m_AttributeManager 0xcb0, m_updateTimer
0x10e8, m_stuckAnchor 0x1100, m_collisionStuckTimer 0x1110, m_isOnGround 0x1128, m_vFallVelocity 0x112c,
m_desiredActivity 0x1138, m_currentActivity 0x113c, m_activityTimer 0x1140, m_turnRate 0x1158, m_fleeFrom 0x115c,
m_moveRateThrottleTimer 0x1160, m_startleTimer 0x1178, m_vocalizeTimer 0x1190, m_leader 0x11a8, m_owner 0x11ac (+0x11b0
a CUtlString model, +0x11bc the material group), m_reuseTimer 0x11c0, m_jumpTimer 0x11d8, m_flLastJumpTime 0x11f0,
m_repathTimer 0x3200, m_vecPathGoal 0x3298, m_flActiveFollowStartTime 0x32a4, m_followMinuteTimer 0x32a8,
m_BlockDirectionTimer 0x32c8, m_bSpawnDyingParticles 0x32e3. The pawn's m_petItem? no: `m_petItem` (+0x1080) is
CCSGO_TeamPreviewCharacterPosition's (the end-of-match line-up).

- **SetOwner** 18034fdd0 (chicken, pawn): the pawn's controller (180a969e0) -> its pet item (180b0a450) -> upgrade level
  (1808c4e20); **only a level > 1 pet (pullet, hen) becomes a match chicken** (else returns 0). Sets m_owner, puts the
  item in m_AttributeManager (181058270), the model: an item without its definition loaded (+0x68 == 0) gets one of the
  4 stock models `models/chicken/chicken.vmdl`.. (table 1817bd750, by (seed - 1) & 3 from 1813aa290), else the pet
  definition's model (181067140) and material group (181066ed0, 0xff = none -> 0) at +0x11b0 / +0x11bc.
- **The round's pets** 18034f710 (CCSChickenManager, called from 18033bad0): (1) every `chicken` with an owner is
  removed (180c30c10) unless its owner is alive-or-state-3 (pawn +0x514 in {0, 3}), owns it (180a7a9d0 == chicken), is a T
  or CT (+0x344 in {2, 3}) and still has the same pet item (+0xd48 == 180b0a470); (2) if pets are allowed (18093df90),
  for each T / CT player with a pet item (180b0a470 != -1): with no live pet (or one flagged +0x30 bit 9), a spot from
  the team's list (manager +0x80 for CT, +0x68 for T; 180354190), a new `chicken` (180bef630), SetOwner, the player's
  pet link (180a9b7f0), spawned (1803ea3b0, 180caa5f0); a live pet is moved to a spot (1803ea3b0); (3) chickens with a
  leader get a ground trace (1802b7cb0: half hull + 71, 16 u)... (rest unread).
- The follow 180348300 ("[Chicken Activity] Chicken %d has started following %s"), the death 180347350
  (Chicken.Death, the pelvis, chicken_roasted.vpcf on DMG_BURN (bit 3), chicken_tased.vpcf on DMG_SHOCK (bit 8)).

### CChicken's think (180344730, "CChickenChickenThink"; the class's think table 180347250, Touch 180341f44, Use 180341f50)

Ported as server/cs2web/pets/pet-chickens.js (2026-11-16: everything below; the earlier notes under it stay as read).

**The manager's events** (CCSChickenManager): round_start -> 18034f710 (above: team spots, a pet already out moved);
round_freeze_end -> 18033bad0's 5 s timer -> 18033b940: every pet's movable flag (+0x32e2) cleared for good (it stops
following, squats); round_end with a winner -> 18034f4f0: the pets whose owner or leader is on the winning side do a
trick now (1803506b0) and again at the next round start (+0x32e1). Game type 0 (classic) uses the team lists; game type
1 (deathmatch) 18034e060 every RandomFloat(10, 20) s spawns a pet on the general list for whoever has a pullet / hen and
no chicken. Pets aren't startled by gunfire.

**Spawn** 1803518c0: the model scale is 1808c4f60's table by the item's level (1.0 / 0.25 / 0.6 / 1.0) x 1.4, the hull
(-8, -8, 0)..(8, 8, 16). The colour is the econ item's style (the material group; set by the GC with the breed).

**The spot lists** (180354bf0 -> 1803433b0): the enabled info_player_terrorist / _counterterrorist, each one's nearest
nav area (GetNearestNavArea, 10000 u); a flood over the areas' links keeping an area when its attributes lack 0x4, its
step from the area it came from is <= 18 and (radius > 0) its centre is within the radius of a spawn (1803413f0 /
180341cc0): the T and CT lists at 256 u, the general list (both sides) with no radius. A spot (180354190): a random area
of the list, a random point in it, the 40 x 40 x 20 box above it clear (mask 0xc3011), else another (as many tries as
areas). **The path** (CNavPath 180399740 with ChickenPathCost 1817be3f0): an area is refused with attributes & 0x10802,
connection types 5 / 6, or a step > 2 (18034cba0); A* by distance. The nav mesh: maps/<map>.nav from the map's vpk
(nested in a workshop vpk), read with VRF's NavMeshFile (bake/NavBake.cs, `lasers-bake --nav`: nav.json); de_dust2 v36.1
2242 areas, ze_atix_panic_2017_p 2445; ze_hold_em_p / ze_resident_evil_3 ship one with 0 areas, ze_dark_souls none.

**The graph controller** (server 180a4f4e0 SetActivity): `action` = the activity's ID (table at DAT_182171410: idle,
squat, walk, run, glide, land, panic, trick, turn, feed, shoulder, snapshot, reveal); the action it already has again
sets `action_reset` (180a4f460), a new one clears it; `action_variation` = the given variation or RandomInt(0,
0x1000000). Each update (180a4c030): the finished flag (+0x1e8) = this update's events hold ACTION_COMPLETED (the
graph's timed-remaining state events), then action_reset clears (+0x1c0).

**The activity machine**: activities 0 IDLE, 1 SQUAT, 2 WALK, 3 RUN, 4 GLIDE, 5 LAND, 6 PANIC, 7 TRICK, 8
TURN_IN_PLACE, 9 FEED, 10 SHOULDER (desired +0x1138, current +0x113c, timer +0x1140). SetDesired 1803515f0 (a settled
pet only 0 / 1 / 6 / 7 / 8); Idle 180349410 (30 % squat); walk / run (+0xca0 vfn 0x60 / 0x58: immediate while
following); trick 1803506b0 (owned pets only); glide 180349180 on leaving the ground (Chicken.Fly), land 18034deb0 on
landing; panic 18034da90 when the leader is steeply above (dir.z >= 0.9, on the ground, 3 s apart). The timer's end with
nobody to follow: idle -> 30 % walk; squat / walk back to idle; run -> walk; land -> walk. A finished action (or a move
waiting on its desired activity) switches to the desired one: idle / squat 1-5 s, walk 1-3 s with a +-45 deg/s turn,
run 1-4 s with +-45; land -> idle, panic -> run, trick -> idle, turn -> the trick after it (+0x32e0). Vocalize timer
RandomFloat(0.5, 1). The speed is the walk / run clips' root motion (7.7025 / 86.953 u/s) x the model scale.

**+use and the ping** (180345830, from CChicken's Use 180341f50 and player_ping's entity snap 180adb580, within 1000 u):
a movable pet follows that player (180351300; the reuse timer +0x11c0, 1 s); a settled one turns to face them
(180346f60: the graph's turn_angle = V_atan2f(cross, dot) x 57.295776 against its facing) and does a trick after.

**Client** (client_20261015): the controller 18084a1b0 makes the params action, action_reset, action_variation,
in_water, mode, life_stage, idle_phase (+0x158 symbol, handle +0x160), turn_angle, has_lookat_target, lookat_target,
flinch, flinch_variation. Its PlaySequence 18085c680 (a preview panel's PlaySequenceOnItem 180e52ad0 on a graph model):
chick_chicken_reveal / _reveal02 / chicknegg_hatch01 / 02 -> action_reveal with variation 0 / 1 / 2 / 3, chick_retirement01
/ 02 -> action_retirement with 0 / 1 (action_reset when already that action); a model without a graph plays the sequence
itself (1809657b0). The overhead name 180ed0210 (each frame from the reticle's 180eaf7c0): every `chicken` with an owner
(+0x14c4) and drawn (+0x52c bit 5 clear): a MiscOverhead panel, Content offset (0, 0, 18), a misc__label; the owner's
name and the item's name (180d567a0) in #HUD_overhead_pet_quoted, #pet_chicken in _unquoted when it has no item; at the
"pelvis" bone, scale clamp(atan(512 / d), 0.6, 1.4285715) (x 0.7 in 180ecb3d0), opacity the render alpha; visible when a
trace from the view reaches it and the view ray passes within 10 u (param+0x70 skips that). TransitionToCamera
180e65b40: time 0 sets the camera, else the camera manager's blend (+0x4c0 vfn 0x48).

**The egg's graph** egg_pristine_world.vnmgraph (skeleton animation/skeletons/egg/pristine_egg_world.vnmskel, 2 bones,
15 clips; ze-pets/anim-egg): action_idle picks chick_egg_idle_phase01_still..04 by idle_phase, action_panic the
reactions 01-08 by variation, action_viewmodel the viewmodel clips.

Performance (ours, behaviour unchanged): the server's graph runs with skel.active empty (no bone computed: the blends and
lerps work on the active bones; events, states and times are bit-identical, checked over every activity): ~3 us an update
against ~12. The client poses a pet only on screen, every other frame past 1500 u; the bone copy sets local transforms
(inverse parent pose x pose, / the armature's 39.37 scale) with no per-bone matrix update: 0.088 ms a pet a frame.

(Earlier notes.) The following itself (180354870): with a leader and m_bIsFollowing? (+0x32e2) set, the
leader too far (> 2000 u, 4e6 squared) or its path longer than 4000 stops it (180348300(0) + idle); otherwise the nav
path (+0x11f8, a CNavPath) is recomputed every 0.5 s (m_repathTimer +0x3200: 180399740 from the chicken to the leader)
unless the path's last point is still within 100 u of the leader (+0x31f8 count, points 0x20 apart at +0x11e4), and the
path follower (+0x3218, 1803a22a0) steps along it; m_followMinuteTimer (+0x32a8) restarts at 60 s. The speed is the
graph's root motion (the clips' rootMotion, tools/tp-graph.mjs keeps it): chick_walk 9.76 u over 1.267 s = 7.70 u/s,
chick_run 104.34 u over 1.2 s = 86.95 u/s, chick_start_walk 4.83 u/s, chick_walk_swim 20.76, chick_run_swim 87.68;
the turns' angular rates chick_45l/r 2.14 rad/s, 90 2.77, 135 3.07, 180 3.25.

The rest of the think, read:
- Removed when the game rules' state (1803d9090) is 1. The anim graph each think: the pet item's level (m_AttributeManager
  +0xd00 -> 1808c4e20) into the graph controller (180a4f790), mode 4 (180a4f7d0: mode_in_game?).
- Off the ground (m_isOnGround +0x1128 false): m_vFallVelocity (+0x112c) += gravity vector (the physics query's +0x98)
  x dt x the entity's gravity scale (+0x40c); the move to origin + v x dt (1803507d0).
- The startle timer (+0x1178, interval +0x1184) on expiry: in activity 3 a 20 % chance (else 50 %) to set activity 6
  (1803515f0(6, 1)), otherwise flee from m_fleeFrom (+0x115c) (1803480c0).
- Following m_leader (+0x11a8, when the activity isn't 7 / 8), every RandomFloat(0, 0.5) s (m_moveRateThrottleTimer
  +0x1160): the distance from the graph controller's origin (+0xca0 vfn 8) to the leader's: < 90 and not idle -> idle
  (180349410); 110 .. 180 and not activity 2 -> walk (+0xca0 vfn 0x60); > 220 and not activity 3 -> run (vfn 0x58).
- Walking / running (activities 2, 3) with no flee target: a hull trace to the leader (1802b5420, mask 0xc3011, ChickenPathCost
  filter 1817af9e0): clear (fraction 1) -> straight at the leader, else at m_vecPathGoal (+0x3298); t = clamp((dist -
  300) / 1700, 0, 1); facing (the body's forward from its rotation quaternion, the forward constant at 182337ef0) dot
  the direction >= 0.96 - 0.253 t -> m_turnRate (+0x1158) 0, else 360 deg/s toward the side (the cross's sign); the
  feelers (1803423e0: "Chicken feeler distance / height / pitch" cvars) can override; facing dot >= 0.9 -> vfn 0x48;
  yaw += rate x dt (1803ea1a0).
- Fleeing: away from m_fleeFrom; past 150 u it stops (m_fleeFrom = -1); within 0.7071 of the way out no turn, else 360 deg/s.
- Still unread past line 400 of the decompile: the idle / squat / activity switch (the switch at 18034560c), the
  activity timer's choices, vocalizing (m_vocalizeTimer, Chicken.Idle.*), the jump (m_jumpTimer), stuck handling.

## Second pass (2026-11-16): the stand-ins traced

### Server (server_20261105)
- **Ping on a chicken.** The snap 180ab7ec0 takes the eye trace's entity when it is a CBaseAnimGraph (RTTI 181ebbe30),
  ranked by 180ac6b50: CPlantedC4 4, CCSWeaponBase 3, CItemDefuser 2, CChicken 1, else 0. Below rank 3 a 46-unit
  (0x42380000) sphere query runs at the hit; a candidate wins with rank > 1, rank >= the current, WorldSpaceCenter within
  36 and (higher rank or nearer). So a chicken is pinged only when the eye ray hits it, and a weapon / defuser / C4
  within 36 beats it. Placement 180adb580 (ping, pawn, urgent, param_4, ent, pos): type `param_4 ? 0x18 : urgent ? 13 :
  0`; an entity: C4 at its abs origin type 0x19, else at WorldSpaceCenter (vfn 0x2c8 = 18015a2f0) with type weapon 1,
  defuser 0x1b, **chicken 0x1a**. Life `param_4 ? 30 : 6`. **A pet is used by the ping only in the freeze time**:
  `type == 0x1a && g_pGameRules (DAT_1821ba1c0) && m_bFreezePeriod (+0xd8) && HasOwner (180343fd0)` -> 180345830(ch,
  pawn, 0) (no distance check) and the ping lasts 1.0 s. Ported: comms/ping.js, pets/pet-chickens.js rayHit / centre.
- **180345830(ch, player, checkDist)**: null player -> return; checkDist and (dy^2 + dx^2) + dz^2 > 1e6 (0x49742400) ->
  return; movable (+0x32e2) -> follow 180351300; else with an owner -> turn and trick 180346f60. Use (180341f50 -> vfn
  0x9e0 = 1803457e0): the activator only when IsPlayer (0x558) and alive (0xca8), checkDist 1.
- **ObjectCaps**: the CChicken vtable 0x1817bd858, slot 0xd0 = 18034f440: `base() | 1`; the base 180d04f60 (CBaseEntity /
  CBaseModelEntity) 0x80 with no move parent, else `parent & 0x87` (| 0x80 for a player parent). A pet: 0x81 (impulse
  use, no radius bit: FindUseEntity finds it by the look trace only).
- **When**: 18093df90 = `g_pGameTypes (DAT_182125888)->vfn 0x98 GetCurrentGameType() == 0`; 18034f710 also needs
  gamerules, the nav mesh (DAT_18234ace8) and its area count (+8) > 0 (none: nothing at all, not even the cleanup).
  Its step 3, for a pet with a leader (not flagged +0x30 bit 9): GetNearestNavArea (1814bb3f0, flags 0x10, 10000) at the
  leader's abs origin; when the area's hi.x - lo.x and hi.y - lo.y (+0x30 - +0x24, +0x34 - +0x28) are both > 20, the
  pet goes to its centre (1814cb1b0) + (0, 0, 10) (180307f90); then +0x32e1's trick.
- **Move(target) 1803507d0** (falls and root motion both): mins collision +0x40, maxs +0x4c, size = maxs - mins
  (18034f3f0). The horizontal pass: a box with mins.z raised to mins.z + size.z (a plate at the hull's top: the step is
  its height), swept origin -> target by 180353d40 up to 3 times: no hit -> m_collisionStuckTimer (+0x1110) restarted
  (180338b80), end = target; a hit with `now >= timer (+0x111c)`, not jumping (sub vfn 0x50) and start-solid (+0xbb) ->
  end = (t - o) x 0.5 + o (collision ignored); else slide: d = t - o, dot = (d.y n.y + d.z n.z) + d.x n.x (n +0x90),
  t = (d + o) - dot n; after 3 hits the last endpos (+0x84). The stuck duration 0.5 / timescale (0x18178057c), set in
  Spawn. The ground pass (not jumping): the full hull from (e.x, e.y, e.z + size.z) to (e.x, e.y, e.z - size.z); in_water
  from the hit's +0x50 & 0x18000 (180a4f760); a hit -> the ground endpos unless the normal is ~0 (all |n| < 0.01),
  n.z <= 0.7071 or start-solid (then e); SetAbsOrigin; not m_isOnGround (+0x1128) -> set it, SetAbsVelocity(0), Land
  18034deb0; m_vFallVelocity (+0x112c) = 0. No hit, or jumping: origin e, off the ground, Glide 180349180 (the vocalize
  timer +0x1190 restarted at RandomFloat(0.5, 1) unless gliding with it running, Chicken.Fly, activity 4 if movable).
- **The sweep 180353d40**: interacts-with 0xc3011, collision group 5, ignore self, owner m_hOwnerEntity (+0x3e4) unless
  collision +0x5a & 4, exclude |= 0x40000c0000, flags (b & 0xc9) | 0x49; the filter (vtable 1817af9e0, ShouldHit
  180c2a810) skips players (0x558), byte +0x2f1 in {1, 2} and vfn 0x208 == 2: moving brushes and props are hit. Water:
  a second sweep from the start to (end.x, end.y, max(start.z, end.z) + 64), interacts-with 0x18000, flags | 4; a hit:
  wz = endpos.z - 9, and when the main end's z < wz the result is the water trace at z = wz.
- **Falling** (the think): dt = globals +0x34, v += dt x m_flActualGravityScale (+0x40c) x g (180590fe0 vfn 0x98),
  Move(origin + v dt). **Root motion** 180342230 (vtable slot 0x960): the graph's root motion transform (+0x410 ->
  +0x370) rotated by the yaw, angles (0, normalised yaw, 0), Move(origin + delta); nothing when neither moves.
- **Feelers 1803423e0** (the turn rate): devonly_chicken_feeler_distance 30, _height 5, _pitch 45, _blocktimer 0.2
  (flags 2). f = AngleVectors(-pitch, yaw, roll) (up 45), s = origin + (0, 0, height); L = s + ((-f.y + f.x), (f.x +
  f.y), f.z) D; R = s + ((f.y + f.x), (-f.x + f.y), f.z) D; C = s + 32 f; rays (1802b5420) 0xc3011 group 4. The
  m_BlockDirectionTimer (+0x32c8, +0x32d4) running: dir (+0x32c0) 1 -> -360 else +360; else only R hit +360, only L
  -360, both: R.frac <= L.frac -> +360 dir 2 else -360 dir 1, the timer started; none 0. Return turn x ((1 - C.frac) +
  1). A non-zero value steers instead of m_turnRate. m_stuckAnchor (+0x1100) is written (moved past 50 u) and never read.
- **The jump** ("panic", activity 6) 18034da90 = sub vfn 0x48: when sub vfn 0x20's +0x3290 is null or its +0x40 & 8 is
  clear (taken: the nav area's NO_JUMP), not jumping, `curtime - m_flLastJumpTime (+0x11f0) > 3`, on the ground:
  m_jumpTimer (+0x11d8) 0.1 s, activity 6, last = now. Jumping = now < the timer (+0x11e4) (18034cef0). The test is the
  body's up axis (182337f40) . the way to the leader >= 0.9; the facing test uses (1, 0, 0) (182337ef0).
- **Startle** (+0x1178): duration -1 from Spawn, no starter anywhere: dead for pets. chicken_stop (0x4000) skips to
  Idle; the flee from fast players (1803544e0) returns at once for owned chickens; walking to a leader (and fleeing
  within 150) restarts m_activityTimer (+0x1140) every think; the leader-in-sight test is a ray from EyePosition (vfn
  0x5e8) to its abs origin (0xc3011, group 4, flags 0xf, exclude | 0xc0000).

### Client (client_20261015)
- **The controller's params** (ctor 18084a1b0, registration 180845430): each a symbol at S, the graph pointer at S + 8,
  the index at S + 0x10 (floats through 1808492a0: finite, |f| < 2^31): action 0xc0, action_reset (an auto-reset ref)
  0xd8, action_variation 0x100, in_water 0x118, mode 0x130, life_stage 0x148, idle_phase 0x160 (index 0x168), turn_angle
  0x178, has_lookat_target 0x190, lookat_target 0x1a8, flinch 0x1c0, flinch_variation 0x1d8; byte 0x1e8 the
  ACTION_COMPLETED flag (180854ca0). The entity's controller: entity + 0x1130 (18093eac0).
- **The client's activity -> action** (180860180): 0 idle, 1 squat, 2 walk, 3 run, 4 glide, 5 land, 6 panic, 7 trick,
  8 turn, 9 feed, 10 sleep, 11 shoulder, 12 low_on_food (the server's table differs past 9). mode (DAT_18252b6e0): 0
  unspecified, 1 main_menu_foreground, 2 main_menu_background, 3 end_of_match, 4 in_game; life_stage (DAT_18252b708):
  egg, chick, adolescent, adult.
- **ApplyState 180d4f1b0(ent, var)**: ent+0x1b90 = var; the "feed" / "placement" attachments; life_stage =
  tbl[UpgradeLevel (1807232d0, 3 when missing or >= 5)]; mode = tbl[ent+0x1b88] (1808605e0; written only by 180cada50:
  0-3); SetActivity: the action (180860100 pulses action_reset when unchanged), variation (float)(var < 0 ?
  RandomInt(0, 0x1000000) : var).
- **The vanity chicken's frame (vfn 180d43380)**: on ACTION_COMPLETED: an egg -> 0; else (not 11) from 0: r < 0.1 squat,
  < 0.2 sleep, < 0.3 feed when the "feed" attachment entity exists; from anything else 0 while ent+0x1b8c < 3, else
  squat / sleep (0.5); squat / feed / sleep zero the count, a trick adds one; ApplyState(-1). An egg: f = (no GC time ?
  1 : clamp(1 - (float)(int64)max(0, deploy - now) / 432000.0f, 0.05f, 1)), idle_phase = (float)(int)floorf(f x 4)
  (180860420 through 1808492f0, a change pulsing action_reset): 0..4, a step every 1.25 days.
- **Interact 180d4e890** (feed or another): an egg at 0 -> panic; feed and fed -> feed_anim "interact", Chicken.Feed.Seed;
  not feed and busy -> flinch (180852000: flinch true, flinch_variation (float)RandomInt(0, 0x1000000)); at 0 ->
  Chicken.Idle.Chick / .Pullet / .Hen, then feed ? 9 : 7 with the count rule. The food check 180d520f0: low -> 12;
  fed from 12 -> 9; in mode 1 with a hatched pet it spawns models/chicken_feed/chicken_feed.vmdl at cs_pet_placement
  (x 1.75 for a chick, feed_anim full / empty). SetPetActivity[AndVariation]OnItem 180e5e960 / 180e5e8b0: names
  (181cca620) to 0..12, 180d50300 sets it when changed. Preview set 18085c990: action_snapshot, variation n - 1.
  in_water, has_lookat_target, lookat_target: no client writer (networked from a server; the menu leaves them false).
- **Camera blend** (CUI_MapPreviewCameraManager vtable 181ccbd88 over CBaseCameraManager): vfn 0x48 180e65c50 ->
  180b833b0: a new camera: prev (+0x30) = the current target, cur (+0x28) = new, dur (+0x40), start (+0x3c) = Now()
  (180b70cb0: realtime with +0x48), frac 0, blending; time 0 sets it. Each frame 180b82920: frac = smoothstep (1808a4520:
  t = clamp((x - a) / (b - a)), ((3 - 2t) t^2)). Origin lerped (slots 0xa8 .. 0xb8), fov lerped (0xd8), angles (0xc0,
  180b595e0: unchanged when equal, else 181744420): AngleQuaternion (1817445e0) of each, the fitted slerp (the k
  polynomial: 3E5CD035 .. 40639CE0), QuaternionAngles (1817463a0), roll included.
- **Overhead pet name trace**: FUN_18022fee0(engine, eye, pelvis, ignore (you, or the watched player in mode 2),
  interacts-with 1, group 4), flags (b & 0xc9) | 0x49; visible when it hits the pet or reaches the point. param+0x70 =
  show team equipment (CSGOHudShowTeamEquipment 180ebdb10, +cl_show_team_equipment 180eb7650 / 180eb76d0): held, every
  pet name shows.
- **The egg's nest** (180d52620, from 180cada50 / 180cae080 / 180cbf0b0): an upgrade level 0 pet in mode 1 or 2 gets a
  C_DynamicProp of models/nest/nest.vmdl (made once, kept as the pet's "nest" handle, vfn 0x1b0 with the pet) at the pet's
  abs origin, angles and scale (180219a80 / 180219a50 / 180219ab0); otherwise the nest is removed (180a1b890).
  ApplyState's "feed" / "placement" are entity handles in the same store: with both, the pet takes the placement's
  abs origin and angles.
- **Inventory picture**: GetInventoryImage 18118d3d0 for the `pet` item: pet id -> the pet definition (181134ad0) +0x20
  = pedestal_display_model; ItemImage 180dcaa00's dynamic test 181190590 true for every flexible_loadout_slot "pet"
  item but chicken_feed (180e42740): "file://{images}/<model>.png" rendered at runtime (180e536d0, type 2). chicken_feed
  keeps its static image + "_%u" of the pet seed.

### Ours, on top (performance; behaviour identical)
- **The network**: the pets go as binary frames (net/pets-codec.js), encoded once per send: a full frame to a viewer that
  hasn't had one, then deltas of what changed; nothing while they're still (~45 B/s a pet against ~3 KB/s of JSON). The
  frames carry the round world's tick: the client draws pets on the players' clock (replica.js), their graph changes
  and sounds at their tick.
- **The anim runtime** (shared with the players, checked bit for bit against the old runtime over every graph with every
  parameter driven, and by the DLL oracles): a result object per node, ranges per node, events pooled in the context,
  sync times into caller-owned objects, the per-bone slerp and lerp with fitK / qnorm written out (V8 boxes a double
  across a call it doesn't inline): ~4.2 KB of garbage an update -> ~0.9 KB.
- **Root motion** through the runtime (root-motion.js), only for the server's pets: a clip's delta inverse(prev) x cur
  (a loop through its end), blends lerp / fitted-slerp the deltas (every chicken transition is m_rootMotionBlend
  "Blend"), a layer keeps its base's (m_bOnlySampleBaseRootMotion), m_bSampleRootMotion off gives none. Walk 7.3 u/s
  (its start blend included), run 86.96, a turn exactly its turn_angle from a fresh start.
- The controller counts ACTION_COMPLETED from the active branch only (a state blending out keeps saying it through its
  transition: without this a pet flipped activities every tick after a trick began).

## Third pass (2026-11-16): the feeder, death, the party's pets, the last stand-ins

### The feeder (client_20261015)
- **180d520f0** (the food check; from 180cada50 on a placement change and 180cbeda0): in mode 1 (main_menu_foreground,
  +0x1b88) with upgrade level > 0: the cs_pet_placement (FUN_1809dfb70 over the class, the one whose +0x38 matches the
  pet's) and the pet's "feed" handle (180802c40); none -> a C_DynamicProp (180d40b10 / 180d51170 / 180d41ce0) named
  "feed" (1815dc490, DAT_181cac328), models/chicken_feed/chicken_feed.vmdl (1809643c0), owner the pet (vfn 0x1b0),
  render mode from the pet (180b9b620), stored as the pet's "feed" handle and the placement as its "placement"
  (180802e50). Every check: transform 181748480(placement origin with w 1, placement quat (AngleQuaternion 1817445e0
  of 180219a50), local ((-15.1731, 11.6387, 0) x s, w 1) (0x181cada90 / 0x181cada78, s = the pet's scale 180219ab0),
  AngleQuaternion(0, 0, 0) (DAT_181ac29d8)): origin + rotate(quat, local); SetAbsOrigin (18022b670), QuaternionAngles
  (1817463a0) -> SetAbsAngles (18022b470); scale s x (1.75 for a chick, else 1) (18022b750). Then the pet's feed_anim
  (180d42f50: a string in the entity's attribute map at identity +0x48, then vfn 0x150) = "full" when now < the
  low-food date (180d48320), else "empty". Then the activity: fed and 12 -> 9; low and not 12 -> 12; ApplyState(-1).
- **180d43380** (the vanity frame) after the graph part: the pet's "feed" handle's entity and a pending feed_anim
  string -> that entity plays the sequence of that name (1809529a0, 1809657b0 cycle 0, 18093e020(0), rate 1 vfn 0x108,
  +0x330 vfn 0x70 -> vfn 0x78(0x40)) and the key is removed (1808311d0). chicken_feed.vmdl has no graph: full / empty
  (loop, held) and interact (1 s).
- **Interact 180d4e890** (an interface at entity +0x14b8, vtable around 181cac288): param_3 the entity clicked; feed =
  its identity +0x18 (the name) is "feed" (1815bc1c0). Egg: idle -> panic, done. Feed and now < low-food date ->
  feed_anim "interact", Chicken.Feed.Seed (1.0, 0.5, 1.0). Busy (activity != 0): feed -> nothing, else flinch
  (180852000). Idle: Chicken.Idle.Chick / .Pullet / .Hen, then activity feed ? 9 : 7 and the trick count rule.
- The flinch: 180852000 writes the graph's bool node (graph +0x10 [index] +0x18 = 1) and flinch_variation; the
  controller's post-update **18085d0e0** (vtable 181c092c8) clears the ACTION_COMPLETED byte (+0x1e8), sets it from
  this update's events, and writes flinch's node back to 0: one update.

### Hurt and killed (server_20261105)
- Spawn 1803518c0: **SetHealth(1)** 180d0e5d0 (+0x2d0), **SetMaxHealth(1)** 180d0e730 (+0x2d4), 1803ebce0(1, 0)
  (+0x2e0 takes damage, +0x2e8 flags 0). CBaseEntity's ctor (180cdcad0) zeroes them. The hull bounds 180354490
  (-8, -8, 0)..(8, 8, 16) are set after the model scale (1803eb340): raw.
- TakeDamageOld 1803ed610: amount = floor(damage) (1816c4664), the fraction + carry (+0x2dc), carry >= 1 adds one;
  damage-info flag bits 4 / 3 clamp it (not used here); health -= amount (1803c4950 / 1803e55e0); before > 0 and after
  <= 0 with life state 0 -> life state 1 (1803e42f0), Event_Killed (vfn 0x418); a true return -> vfn 0x420.
- **Event_Killed 180347350** (slot 131): Chicken.Death (180f695d0); the pelvis (180b612d0 / 180b52300); 1808d4c60's
  model index (client 18072ed20: chicken 0, chick 1, chicken_polish 2, chicken_silkie 3, by V_stristr over the table
  at 181ba52a8); DMG_BURN (+0x4c bit 3): chicken_roasted.vpcf at the pelvis, CP1 (index == 3 ? 1 : 0, 0, 0);
  DMG_SHOCK (bit 8): chicken_tased.vpcf; else m_bSpawnDyingParticles (+0x32e3) = 1, 1803c5900(0x420), next think now
  + 3 and no particle here. Holiday mode (18093d4e0): weapon_confetti_omni. A leader: TextMsg type 3 "#Pet_Killed"
  (" Your chicken has been killed. She was yours for %s1 seconds.") with now - m_flActiveFollowStartTime (+0x32a4,
  "%d" from 1 s, else "%.1f"), then the follow stops (180348730 / 1802805e0) and m_leader = -1; the game rules' hook
  180922960 (a living player attacker only); base Event_Killed 180bad480. Returns m_bSpawnDyingParticles == 0.
- follow 180348300 stamps +0x32a4 with now on every call (any leader, the same one too).
- Client **180d51420** (from 180d4eda0 on m_bSpawnDyingParticles): chicken_gone.vpcf at the pelvis (CP0), CP1 =
  (model index, the material group 180943590, 0), the model's material bound (180a11370), then 180d45c90.

### The party's pets (panorama + client)
- mainmenu.ts _UpdatePlayerVanityModel: every lobby member's vanity presence (PartyListAPI.SetLocalPlayerVanityPresence:
  team, character, gloves, slot, weapon, **pet item**); player index 0 -> SetPetPlacement('main-menu-foreground'), the
  rest 'main-menu-background'; no pet -> 'none'. sessionutil.ts BCanUseMyPetInCurrentLobby: alone, or the lobby host
  (the panel's hover and zoom only).
- The names (180e5e960, the map panel's SetPetPlacement): none 0, shoulder 1, main-menu-foreground 2,
  main-menu-background 3, end-of-match 4 (into the character's +0x98).
- **180cada50(character, pet handle, item, placement)**: each preview character owns its pet (+0x3760); a new one
  replaces it (180cbb290), owner link vfn 0x1b0, placed (180cae080); the pet's mode +0x1b88 = 1 / 2 / 3 for 2 / 3 / 4,
  else 0; the item (180d4db50); placement 1 -> 180d48bb0, else the nest (180d52620) and the feeder (180d520f0).
- **180cae080** (placing): 1 shoulder: parented to the character (180219680, attachment hash 0x119bcd9) at local (7, -1,
  -3.5), angles (180, -90, -20), activity 11; 2 foreground: unparented at cs_pet_placement's origin and angles (no
  placement: as 3); 3 / 4: unparented at the character's origin + rotate(its quat, (15, 0, 0)), its angles with yaw
  + RandomFloat(-30, 30); 5: the character's origin, angles and scale.

### Smaller ones
- The chicken's eye: EyePosition is CBaseEntity's 18014d780 = abs origin + GetViewOffset 18014e660 (m_vecViewOffset
  +0x818); no chicken code writes the view offset: the origin.
- Root motion: the server copies the graph update's root motion as it is (1811d824c: +0x370 / +0x380 from the
  result's +0x10 / +0x20) and 180342230 only turns its translation by the yaw (181473df0) before Move. The context
  (1811e12e0) carries the entity's world transform with its scale; whether animationsystem scales the delta by it is
  unread (ours scales it).
## The photo booth and the HatchBook (2026-11-16, panorama scripts; no DLL read)

Read from CS2's own panels (pak01, decompiled into web/public/ze-pets/reference by `lasers-bake --pets`):
popup_pet_photobooth.{xml,ts,css}, pet_photo_tag.ts, pet_photo_library.{xml,ts,css}, popup_pet_book.{xml,ts,css},
pet_book_pages.ts, pet_book_turn.ts, pet_book_page_styles.css, context_menu_photo_viewer.{xml,ts,css}; the stage maps'
entities (game/csgo/maps/ui/pet_photo_studio.vpk, ui/pet_photo_park.vpk, warehouse_vanity.vpk); the anim graphs
(ze-pets/anim chicken.json, ze-ui/anim uimodel.json). Ours: client/home/pets/photo-booth.js (+ booth-controls.js,
booth-scene.js, booth-capture.js), pet-book.js (+ pet-book-pages.js, pet-book-snippets.js), photo-tag.js,
photo-library.js, photo-store.js, pet-strings.js; server econ/pet-photos.js (migration 009_pet_photos.sql).

**Opening.** vanity_pet_info.ts shows `id-photo-booth` and `id-pet-book` from upgrade level 1 (`hide` below);
_OpenPhotoBooth passes pet_id, upgrade_level (+ action-type / title / msg / callback, unused by the booth);
_OpenPetBook opens the book bare. The booth's OpenBook passes spread = book_spread, booth_setup = the setup string,
from_booth = 1; the book's OpenPhotoBooth passes pet_id, upgrade_level, book_spread, booth_setup, from_book = 1 (only
with a live pet). The setup string: `key:value;key:value` of stage, paper, pose, aspect, filter, headwear and every
adjustment slider, applied .25 s after the booth opens (after the filters reset).

**The stage.** A MapPlayerPreviewPanel (`cam_pet_photo`, pin-fov vertical, panzoom, drag rotate, yaw limit 30) on the
stage's map: STAGES studio `ui/pet_photo_studio` (id 0, the default), picnic `ui/pet_photo_park` (1), warehouse
`warehouse_vanity` (4, age_requirement 2), airport / dust2 / mirage / inferno / nuke / cache / train / ancient
`<map>_vanity` (3, 2, 5..10, achievement `visited-<map>`). The studio's entities: csgo_item_previewmodel `pet1`
(-30.5, -450.4, -255.8, yaw 282.9: the solo pet), csgo_player_previewmodel `vanity_character6` (-33.9, 54.8, -255.9,
yaw 262.8: the posed agent), cameras `cam_pet_pose_solo_intro`, `cam_pet_pose_solo_0..3` (by growth: solo_1 chick,
_2 pullet, _3 hen), `cam_pet_pose_intro`, `cam_pet_pose_1..10` (vfov 35), the 9 effects as info_particle_system
(start_active false) in two sets (`explosion`, `lightning`, `fire`, `beam` (photo_ufo), `lasers`, `sparks`,
`confetti`, `bubbles`, `feathers` by the agent; `solo_*` by pet1: particles/pet_photo/<name>/photo[_solo]_*.vpcf), the
post volumes (post_vanity master; pet_post_normal / bw / sepia / warm / cool / crisp / moonlight / silvertone /
psychedelic, _bloom, _exposure_up / _down, _vibrance_up / _down, _contrast_up / _down, _saturation_up / _down:
lighting/postprocessing/effects/pet_*.vpost), two prop_dynamic `backdrop` (models/photobooth/photobooth_backdrop.vmdl,
11 material groups: paper grey / blue / green / purple / yellow / brown / red / black, sky, wallpaper, abstract),
light_barn `chick_light`, `agent_light` (the colour picker's SetColor targets). The park: the same names at its own
places (pet1 (159.2, -367.9, 35.4) yaw 8.3, vanity_character6 yaw 348.2).

**Poses.** POSES `0` (solo) and `8 9 10` (orbit 80) `2` (100) `4` (110) `5` (80) `6` (90) `1 3 7` (100). A pose:
ResetPanZoom, ResetDragRotate, SetDragRotateRadius(orbit, solo: 36 / 45 / 55 by growth), SetZoomLimit(25), the intro
camera at once (`cam_pet_pose_solo_intro` / `cam_pet_pose_intro`), then the pose's camera over 2 s. Solo: SpawnItem
(growth entity `chick` / `teen` / `adult`, pet, '', 'pet1') once, its Alpha 255 and dynamic_player6's 0. Posed: your
loadout's agent for the team (`customplayer`, `clothing_hands`), SetActiveCharacter(6), SetPetPlacement('origin'),
EquipPlayerWithPet, PlayChickSnapshotAnimation(pose). The agent's graph (uimodel.vnmgraph state `chick_snapshot`, node
811): SM -> a ParameterizedClipSelector on `chick_life_stage` (options egg / baby / adolescent / adult) -> a
ParameterizedClipSelector on `chick_snapshot_variant` over `chick_snapshots_char01..10[_adolescent|_baby]` (taken:
the variant = pose - 1, the life stage = the upgrade level; PlayChickSnapshotAnimation itself unread). The pet: its
graph's `SM/Snapshot` (node 168, entered by action == action_snapshot) -> by life_stage -> a ParameterizedClipSelector on
action_variation (node 6) over `chick_snapshots_01..10[_adolescent]`: each a one-frame pose whose root sits in the agent's
hands (04: root (-11.6, -19.8, 56.2)), so the pet stands at the agent's origin (client 18085c990: action_snapshot,
variation n - 1). The snapshot clips are fetched before the action switches (a selector picks once: a clip on its way
left the reference pose), and the pose holds (its one-frame clip says ACTION_COMPLETED at once).
Age gates (_ApplyAgeGates): poses 8-10 only up to the chick (#pet_photo_booth_age_outgrown), 2 4 5 6 from the pullet
(_dangerous), 1 3 7 from the hen (_maturity); effects sparks / laser / beam from the pullet, fire / lightning / explosion
from the hen unless the pet has killed-by-burn / -taser / -planted-c4 (#pet_photo_booth_age_scary_brave); activities
jump / wag / moonwalk from the pullet, kick / fly from the hen (_age_tricks). The team buttons are off in the solo pose;
the light button only in the studio.

**Activities** (ACTIVITIES, SetPetActivity[AndVariation]OnItem): sit = trick 2, panic = panic, wag = trick 9,
moonwalk = trick 5, jump = trick 11, kick = trick 12, fly = trick 1; only in the solo pose, one at a time. _TickActivity
polls every .1 s: the first time the pet's activity is the row's it plays the row's sound for the growth (sit:
Chicken.Idle.Single.Chick.PhotoBooth / Chicken.Idle.Single.PhotoBooth; panic: Chicken.Panic.<Chick|Pullet|Hen>.PhotoBooth);
it ends when the pet has left it, or after .5 s unseen, or at 5 s. GetPetActivityOnItem's variation is -1 for a
random one (our MenuPet keeps the asked variation until its ACTION_COMPLETED). **Effects** (PlayEffect):
Chicken.Camera.FX + the effect's Photobooth.FX.* sound, Chicken.Idle.<growth>.PhotoBooth .5 s later, the system
(`solo_` prefix in the solo pose) Start, Stop 1 s later.

**Hats** (HEADWEAR 0-9 helmet, armor (armor_helmet), alien, banana, glasses, nose_glasses, party, sprout, top_hat,
wizard_hat: models/photobooth/silly_hats/*.vmdl): AttachModelToItemWithScale(model, pet, 'eyewear_attach' for a
*glasses* model else 'head_attach', scale 1.0 chick / 0.43 pullet / 0.55 hen). The breeds' attachments (models.json):
head_attach on `head` offset (0.776, -0.070, 0) rotation (0.706, 0, 0, 0.708). The hat models are skinned to a `head`
bone of their own. TODO(trace): AttachModelToItemWithScale's own maths (taken: the model at the attachment, scaled).

**Adjust** (aAdjust: type, kind, min, max, default): exposure / saturation / vibrance / contrast post-pair -1..1 0
(the up volume's weight = max(v, 0), the down's = max(-v, 0)), brightness 0.8..2 1 (the 3D panel's `brightness` style),
bloom post-single 0..1 0, vignette 0..0.8 0.14, grain 0..0.7 0, grime 0..0.5 0 (overlays: their opacity, hidden at 0),
filter-strength 0..1 1 (the filter volume's weight). Reset puts all but the strength back. The grid slider 0..0.5,
0.1 (the grid's style says .25 until it moves). Filters (FILTERS 0-8 normal, bw, sepia, warm, cool, crisp, moonlight,
silvertone, psychedelic): the old `pet_post_<f>` Disable, the new Enable, the strength row hidden for normal, the
strength back to 1. Settling a stage disables post_vanity and every filter, Enables every adjust volume. TODO(trace): how
the client combines several weighted volumes (here: CS2's default settings, then each enabled volume mixed in by its
weight in order: world/tonemap.js PostProcess.mix).

**Formats** (ASPECTS id / name / ratio: 3 1x1, 1 4x3, 2 5x4, 0 16x9, 5 3x4, 4 4x5, 6 9x16): the frame's class
photo-booth-ratio-<a> (896 x 896, 1195 x 896, 1120 x 896, 1120 x 630, 765 x 1020, 816 x 1020, 484 x 1020, padding 16);
the orientation buttons swap the shown set and flip the checked one (FlipAspect: 4x3 <-> 3x4).

**The shutter.** TakePhoto: the composition layer named by the aspect, then (timer: 3 2 1 with UI.Premier.CounterTimer
a second apart) _WritePhoto after .1 s: `pet_<Date.now()>` + PetPhotoTag.Compose + `.jpg`, WriteCompositionLayerJPEG
(PreparePetPhoto's path in USRLOCAL pet/<id>/library, long edge 1200, quality 95), the white flash (.5 s), Chicken.Camera.Shoot;
_VerifyPhoto after .2 s, retried 4 times, then the #pet_photo_save_failed popup. The zoom readout every .1 s
(#pet_photo_booth_zoom_readout, the zoom band wide 0-9 / mid 10-19 / closeup 20-25), Chicken.Photo.ZoomIn / Zoomout on a
change. Ours: the composition layer is the frame's pixels flattened in booth-capture.js and sent to the server.

**PetPhotoTag.** Compose: `_p<pose>_f<filter id>_s<stage id>_g<growth>_a<aspect id>_z<zoom>[_v<activity id>][_e<headwear
id>]`; Parse skips the first two `_` tokens; a book name `book_<stem>_k<page>_y<layout id>_l<slot>[_x<x>_w<y>_m<zoom>]`
(slot 255 = unplaced; the frame only when not 50 / 50 / 100; zoom 100-300); RollName strips the place letters k y l x w m.
Describe's order g z s v e f p with the caption tokens; a hole's require string `name:a|b,name:c` (growth / zoom bands /
stage / pose / filter / activity / headwear), Unmet / Matches / TermWords (`<loc><name>_inline` when it exists).

**The library** (PetPhotoLibrary): the folder's names sorted, reversed (newest first), rows 200 x 96; hover: the
settings tooltip (`tooltip-pet-photo-settings`) and the trash button (#pet_photo_library_delete_* yes / no,
DeletePetPhoto); click: the viewer context menu (the image up to 640 px, copy to clipboard, open the folder); the book's
rows drag.

**The HatchBook.** Pages (LAYOUTS id / snippet / holes): intro 1 (zoom:closeup), feet 2 (zoom:wide), early-days 3
(pose:8|9|10), chick-park 4 (stage:picnic), teen-warehouse 5 (stage:warehouse), teen-trip-1 6
(stage:dust2|airport|inferno|train), teen-trip-2 7 (stage:mirage|nuke|cache|ancient), birthday 8 (activity:jump,
headwear:party), adult-perch 10 (pose:1|3|6|7, filter:sepia), adult-tricks 11 (activity:kick|fly), adult-close 13
(pose:4|5), brave-fire / -taser / -c4 15 / 16 / 17 (achievement killed-by-burn / -taser / -planted-c4, no holes), free
14 (slots 0 | 1 2 | 3 4 5 | 6 7 8 9: single / pair / trio / quad). Sections: chick (stage 1) intro, feet, early-days,
chick-park, free, free; pullet (2) teen-warehouse, teen-trip-1, teen-trip-2, birthday, free, free; brave (3) the three;
hen (3) adult-perch, adult-tricks, adult-close, free, free. Every hole also requires the section's growth. A page shows
when unlocked (no achievement, or photos on it, or the achievement) and (the pet hasn't outgrown its section, or it has
photos, or a photo of either folder fits a hole). Paragraphs: `<token>_<capture ms of slot 0's photo % variants>` with
the pet's names (pet_name, pet_name_1..3: a stage's name, else an earlier, else a later, else the item's) and the hatch
date (#pet_book_hatch_due for an egg). The book is the live pet's, else the newest book (GetPetBookCloudFileKeys' last).
_Reconcile on open: a roll photo whose capture time is in the book is deleted; a book photo unplaced, on a page whose
layout changed, or doubling a hole or a photo goes back to the roll. A drop: the hole must take it, and a photo it
displaces must fit where the dragged one came from (else back to the roll); Chicken.Photo.Pickup / Accepted / Rejected;
a slot's photo dragged off the book goes back to the roll. The frame bar (260 x 156, beside the slot): zoom 100-300,
pan x / y (enabled when the photo overflows the hole that way), committed into the name .4 s after the last change.
PetBookTurn: PAGE 560 x 640, MARGIN 8, the book 1136 x 768; sides blank, cover, pages, [blank], back; FLIP 650 ms,
ease (smoothstep t)^0.72, the leaf's shade 0.32 (x1.25 on its back), the cast shadow 170 px at 0.28, the gutter 0.40,
the page shadow 0.40 x |sin| (x |sin(a/2)| opening / closing); closed the book sits half a page left; sounds UI.BookOpen /
Close / PageFwd / PageBwd; a turn asked mid-flight runs after. The bar: prev / next, a chapter button per section shown
(pet_chick / pet_pullet / pet_field_report / pet_hen icons), `#pet_book_page_counter` {page} / {total}.

**Storage (ours).** CS2: files in USRLOCAL `pet/<pet item id>/library|book` and Steam Cloud. Here: ze_pet_photos
(owner, pet, name, data <= 1.5 MB) through /api/ze/pets/photos (econ/pet-photos.js): list, file, put (a `pet_` name,
a JPEG, your live pet), delete, rename (the capture time kept); a past pet's book readable, not writable; 1000 photos an
account (a stand-in for the cloud quota).

**Stand-ins left.** The GC's pet achievements (none recorded: the achievement stages, effects and the brave pages stay
locked); MapPlayerPreviewPanel's pan / zoom / orbit (wheel steps of 1 to 25 dolly toward a pivot `orbit` ahead of the
camera; shift + drag orbits within the 30 deg yaw limit, shift + right drag pans); the weighted post blend; the light
colour (the stages' lights are baked); the stickers (no sticker items: the button stays locked as CS2 locks it with
#pet_photo_booth_no_stickers); the composition layer's resolution; LocalizeRentalDate's format; Panorama's popup stack;
the vanity stages past the warehouse aren't baked (and need an achievement anyway).

## Still unread

- server.dll: m_iPetPopulation 18029d180; what +0x3290 is (taken: the nav area under the pet, its NO_JUMP bit) and who
  sets +0x2f1; whether the ping ray (0x1c1003) hits a chicken (its interacts-as layers); whether animationsystem scales
  root motion by the world transform (taken: scaled); 180341cb0's yaw composition; animationsystem's own root motion
  sampling and blend (Esoterica's taken); a bullet / knife on a chicken (its hitboxes, penetration: ours its hull box,
  the knife 48 / 32 u); the damage-info flag clamps; 1803c5900(0x420); the other_death event (1801d0290) and the kill
  feed.
- client.dll: the dynamic image generator's camera, pose and lighting (180e536d0); upgrade level 4's life_stage; who
  calls Interact (the map panel's pick on a click: ours a click target on the pet and on the feeder); the shoulder
  placement's caller; the end-of-match line-up's pets.
- The photo booth and the HatchBook: ported (section above); their own stand-ins listed there.
- The colour / pattern draw from `pet seed` (client `chicken_metadata`) and the breed draw (GC).
- The XP rules (GetXpPerLevel, the weekly bonus) and the PersonalStore's generation (GC).
