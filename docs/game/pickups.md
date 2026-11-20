# CS2 weapon pickups, traced from server.dll 2026-11-05 (RUST_PORT phase 3, started)

Working notes for replacing server/cs2web/core/items.js's per-player scan (32% of a 64-player tick, and a stand-in) with CS2's
own pickup. Addresses are server_20261105.dll in the Ghidra project.

## Found

- **CCSPlayer_WeaponServices::BumpWeapon `180b1c290`** (vtable 0x181928818, slot 9 = +0x48; the services object is
  pawn+0xb10): the decision for a weapon a player touches. Reading so far:
  - a bot (pawn vfn 0xc20) asks 180b01690 first;
  - the weapon's CCSWeaponBase (RTTI cast 1816b6d80 to 0x181ebdc30); none → 180cee2e0(weapon+0x5e8) and
    180b062d0(svc, weapon) (a plain item), returns 1;
  - weapon+0xefa set: 180aeb7c0(pawn+0xb38, weapon, cvar 182178790) must pass;
  - an owner already (thunk 180b54f20) or svc vfn 0xd8 (CanUse) false → refused (returns 2 when
    180c30c10 runs for a 180093e040 game mode);
  - cvar 182178778 with pawn+0xfb0: only the weapon's previous owner (weapon+0x100c handle) unless svc+0xd8 / +0xdc;
  - the weapon type (vfn 0xc60): 7 (C4) refused while carrying weapon_c4 or 180a50140(...+0xe48); a taser
    (weapon+0x1fe0 == weapon_taser's id) refused when already carried; a knife refused when one of the same
    definition (+0x700 / +0x704 of the item definition) is carried;
  - otherwise, unless C4 (7), a grenade (11), type 9, the taser or a knife: refused when the gear slot (vfn 0xa70)
    is taken (Weapon_GetSlot 180c86620(svc, slot, -1) != 0): **a touch pickup needs the slot empty**, as items.js
    assumes;
  - svc+0xdc clear: 180b23f00(svc, weapon) must pass (a reach / line-of-sight test, to read);
  - then Weapon_Equip 180b23a70(svc, weapon) (or the owner branch), svc+0xda = 1.
- The buy path is 180a7cf90 (CCSPlayer_ItemServices::BuyItem: item_kevlar / item_assaultsuit / item_defuser, "Cannot
  carry anymore"); GiveDefaultItems is 180ac77d0 (mp_ct_default_* / mp_t_default_*, the taser, the knife).
- Strings: `m_OnPlayerPickup` (the weapon's output), `pickup_groundweapon`, `item_pickup` (fired in 180ac8330,
  180a6ee50, 180a6f6f0, 180b1c290's callees).

## The touch, found (2026-11-09)

A weapon on the ground is picked up by **its own touch**, not a scan by the player:
- the engine's touch (vphysics contacts / trigger overlaps: CS2Fixes' `CVPhys2World::GetTouchingList`) calls
  `CBaseEntity::Touch` (vtable index 151 on Windows, CS2Fixes gamedata; +0x4b8), which for a weapon is
  CCSWeaponBase's 0x180a259f0 → CBasePlayerWeapon's 0x1803eeac0: the entity's touch function pointer (+0x2b0,
  SetTouch) and the parent's touch;
- the weapon's touch function is 0x1809f5b4c (installed by 1809fc590 / 1809ff9b0), a thunk to weapon vfn 0xd60 =
  **CCSWeaponBase::DefaultTouch 0x1809fb3c0**:
  - weapon+0xff8 set (m_bCanBePickedUp, 1 from construction: drops.md; nothing happens while it's 0): the toucher must be a player (vfn 0x558); curtime < weapon+0xffc → no
    pickup yet (anyone's delay); the toucher is the weapon's last owner (handle at +0x100c) and curtime <
    weapon+0x1000 → no (the dropper's own delay). The compare is 18017e2d0 (curtime vs the float: −1 below);
  - a live player (vfn 0x558, 0xca8); FL_ 0x1000000 in its flags (+0x388) → its vfn 0x4b0 first;
  - unless the weapon's +0x360 has bit 1 (no player pickup): **CCSPlayer_WeaponServices vfn 0xe8 = BumpWeapon
    180b1c290** (the services' primary vtable is 0x181928778; 0x181928818 is a secondary one); 1 → the weapon's
    vfn 0xcb8 (picked up).
- The +use pickup and ammo extraction (E on a gun: swap, "#SFUI_AmmoExtracted") is 180aea0a0, from the use code
  (180ade3a0, 180b0adf0): it calls the weapon's Touch with the pawn, or the services' BumpWeapon.

**The touch's shapes (2026-11-09).** A weapon's body is made by 1809ff9b0 at its Spawn (180a24ba0) and on every drop
(drops.md): 180d0f2c0 (group 14 "weapon", interacts-with 0xc3001, motion `(spawnflags & 1) x 2 + 1`: 3 keyframed for
spawnflag 1, else 1), then, when the game rules' vfn 0x148 says so, 180cf16a0(collision, 0x200): **interacts-as gets
layer 9 "pickup"**, and 180cf1ab0: the collision function mask (+0x3f) gets 0x20. Spawn also sets the trigger bounds
(180d1a210(collision, 1, 30.0): m_triggerBloat +0x5c = 30, flag 2 at +0x5a); WorldSpaceTriggerBounds (180d1b920) is the
collision AABB (180cea8c0 of +0x40 / +0x4c) with x and y widened by the bloat each side and the top raised by half of
it; its only users are the surrounding bounds (180cebd90 type 1 → 180ceaf30 / 180cec040: the union with the physics
bounds) and the debug overlay (1803d1e50). vphysics2's group table (0x18045b328, rubikon CollisionGroupTable.cs) has
**0x14 for 14 x 8 ("Player") and 14 x 11 ("player_movement")**: touch events, no solid contact. So the pickup is the
touch pair of the pawn's body and the weapon's own physics shapes; the bloated bounds only widen what the spatial
queries see. Ported (server/cs2web/core/items.js pickups): the pawn's collision box ((-16,-16,0)-(16,16,72), ducked 54) as a box
query in the sim's trace world (sim/src/game/abi_trace.rs ze_world_touching: every start-overlapping entity, in the
all-hits sort's order) with interacts-with "pickup", interacts-as "player", group 0 (a query applies the table's contact
bit, which 8 x 14 lacks) and object sets 0xe (here the all-hits walk returned no body after a start-solid world hit:
not looked into). Stand-ins: the pawn's own body (players have none, touch.md), vphysics2's touch test for a touch-only
pair (margins), the pair list's order, the gamerules' vfn 0x148 (taken as true), and the pickup's timing (after the
player's move, before the step: CS2 dispatches touches after the step).

So the 1:1 port has two halves: the decision (DefaultTouch's gates, BumpWeapon's rules: sim-side or server JS) and
the touch itself (which weapons a player's hull touches this tick: the vphysics touch list, the entity engine's job,
RUST_PORT phase 4). The reach box is gone (2026-11-09: the touch above); it stays only for a weapon with no physics.

## +use on a weapon (2026-11-09: built, server/cs2web/combat/combat.js use, items.js useWeapon, client/hud/targetid.js)

- The use code **180ade3a0** (the pawn's +use, from 180adf4a0): use pressed → the use target 180ac2cf0(svc, tolerance)
  (0x3f6c835e ≈ cos 22.5°; 0x3f7c1c5c when `cl_use_opens_buy_menu` and the buy zone allow E to open the buy menu); the
  target cast to CCSWeaponBase (RTTI 0x181efdb70) → 1809f9d50(w, pawn, 1) → 180adebd0(svc, w) → 180aea0a0(svc, w, 0).
  Otherwise E may open the buy menu ("buymenu
").
- **180aea0a0 (svc, w, silent)**: the pawn must pass vfn 0x550; the slot's current weapon: a rifle (180a0ecf0) → gear
  slot 0, a pistol (180a0ee90) → slot 1, the taser → the carried weapon_taser, weapon_knife → the carried knife.
  **Ammo extraction** (cvar DAT_1821786c8 on, not a grenade (type 11) or type 9, gear slot 0 / 1, the same item
  definition in hand and w's vfn 0xa98): moves clip then reserve from w into yours up to your maximums (vfns 0xaf0,
  0xb18, 0xac0, 0xb20, 0xad8), w teleported to the player (180c8cba0 → vfn 0x528), its body kicked by (RandomFloat(-10,
  10), RandomFloat(-10, 10), 0) (vfn 0x208), "Player.PickupWeapon", and a hint: #SFUI_AmmoExtracted /
  _AmmoExtract_OwnFull / _Empty / _Fail. The cvar is **sv_extract_ammo_from_dropped_weapons, default 0** (registered
  1800cbaf0): not ported. Type 9 (CSWeaponType grenade) of a kind carried: merged into the carried one (vfn 0xaf8), w
  removed. (CSWeaponType: 0 knife, 1 pistol, 2 SMG, 3 rifle, 4 shotgun, 5 sniper, 6 machine gun, 7 C4, 8 taser, 9
  grenade; 18090d960's "1-6" is the guns.)
  **Else the swap**: the slot's weapon dropped by the drop key's path (180b0b020(svc, it, silent 1): CSWeaponDrop mode 1,
  the throw), then, silent 0: w's m_nextOwnerTouchTime cleared while +0xff9 is set (restored after), svc+0xd9 = 1, w's
  Touch (vfn 0x4b8) with the pawn → DefaultTouch → BumpWeapon, svc+0xd9 = 0; silent 1: BumpWeapon directly; the old
  weapon was the active one → SelectItem(w) (svc vfn 0xf0).
- **The use pick 180ac2cf0**: 180ac7120 (a sphere search for long-use map entities, flag 0x2000000: hostages; none in
  ZE, not ported), FindUseEntity 180ac3520 (partly ported: combat.js), then **the weapon trace**: UTIL_TraceLine
  180250e50 from EyePosition along EyeAngles, interacts-with 0x1c1003, group 4, the pawn ignored, length min(128,
  FindUseEntity's distance); a non-world hit that is a weapon (vfn 0x598) passing 180adebd0 is the candidate, one that
  fails fires item_pickup_failed. Either alone wins; both: the weapon, unless only FindUseEntity's is a usable weapon.
- **The gates**: 1809f9d50(w, pawn, 1): m_bCanBePickedUp (+0xff8); curtime < m_nextOwnerTouchTime only with +0xff9;
  the last owner (m_hPrevOwner) waits for m_nextPrevOwnerUseTime (+0x1008). 180adebd0 (= client 1808e1400): types 1-6
  and 8 always, others only while buying is possible: 180926430 returns mp_buytime (registered 18009c690; the warmup's
  own outside a match), not 0, and 18093d470 (buytime < the time since the round began) false, and mp_buy_anywhere
  (DAT_18211a6e8, registered 18009c530) == 1 or == the team (2, 3), or the pawn in a buy zone (+0xf71); then
  CanAcquire 0 or 2. ZE: buying open map-wide (GFL's mp_buy_anywhere 1 and mp_buytime 9999, read by the owner) unless a
  map's cfg says otherwise (src/cs2web/player/weapon-use.js buyOpen reads the round world's cvars), so knife items, grenades and
  the C4 get the E pickup and the pickup line (a zombie on a knife item too).
- **The client's target ID** (CCSGO_HudReticle, constructor 180e9f9b0, hudreticle.xml's #TargetID label; vcss
  `.targetid` y 580, 1040 x 74, 22px bold white, additive, 0.1 s opacity / translateY 7px): its update 180eaf7c0 sets
  the text from 180eb4260 and dialog variables weapon_name, weapon_color, target_owner, player_slot, player_health,
  holding it cppTargetIDDuration (0). The target: m_iIDEntIndex (pawn+0x36f8), written only by UpdateIDTarget
  180c9ec60: a 128 u line from EyePosition along EyeAngles, filter interacts-with 0x41, **interacts-exclude 0x40000**
  (players), group 4, flags 0x49, no iteration (cl_use_entity_as_targetid default 0); a weapon hit (180c61810) needs
  CanBeTargeted 1808043c0 (m_bCanBePickedUp, your own drop not before m_nextPrevOwnerUseTime) and, while its body is
  awake (vfn 0x408: vphysics2 +0x249 bit 2) within 64 ticks of m_nDropTick, a last owner alive and not you;
  1807cd4d0 is the smoke check. The weapon text (180eb62d0): CanAcquire else nothing; 1808e1400 false →
  #Panorama_HUD_weaponid_lookat; the slot (type 1: gear slot 1, else 0, the taser) taken → _swap, else _pickup;
  weapon_name the item's name, weapon_color its rarity colour (no econ item: desc_default, items_game #ded6cc).
  Strings from pak01 csgo_english.txt (tools/weapon-names.mjs → src/cs2web/data/weapon-names.js). `pickup_groundweapon %d`
  (180da95c0) is a panorama event's handler (the buy menu), not this path.

## To trace next

- (Done: the drop and its delays, [drops.md](drops.md).) What the weapon's touch shape is (its physics on which layer: what the player's hull must overlap).
- 180b23f00 (the pre-equip test), 180b23a70 (Weapon_Equip: slot, owner, m_OnPlayerPickup, item_pickup), the drop
  (CSWeaponDrop: its throw velocity and the pickup delay), and what a touch needs (the weapon's trigger bounds:
  that replaces items.js's 40 x 40 x 112 box).
