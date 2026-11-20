# Weapon pickups: the touch, BumpWeapon, +use, the target ID

server_20261105 (Ghidra), client_20261015. CS2Fixes gamedata (Touch's vtable index), pak01 csgo_english.txt,
hudreticle.xml / .vcss. The drop and its delays: [drops.md](drops.md).

## Functions

| Address | Module | What |
|---|---|---|
| 180b1c290 | server | CCSPlayer_WeaponServices::BumpWeapon (svc vfn 0xe8; secondary vtable 0x181928818 slot 9 = +0x48) |
| 180b01690 | server | bot (pawn vfn 0xc20) asked first |
| 1816b6d80 | server | RTTI cast (to CCSWeaponBase 0x181ebdc30) |
| 180cee2e0 | server | (weapon+0x5e8): plain item path |
| 180b062d0 | server | (svc, weapon): plain item pickup, returns 1 |
| 180aeb7c0 | server | (pawn+0xb38, weapon, cvar 182178790): gate when weapon+0xefa set |
| 180b54f20 | server | thunk: weapon's owner |
| 180c30c10 | server | refused path returning 2 (for a 180093e040 game mode) |
| 180093e040 | server | game mode test |
| 180a50140 | server | (...+0xe48): C4 refusal test |
| 180c86620 | server | Weapon_GetSlot (svc, slot, -1) |
| 180b23f00 | server | pre-equip test (svc, weapon): reach / line of sight (unread) |
| 180b23a70 | server | Weapon_Equip (svc, weapon) (unread: slot, owner, m_OnPlayerPickup, item_pickup) |
| 180a7cf90 | server | CCSPlayer_ItemServices::BuyItem (item_kevlar / item_assaultsuit / item_defuser, "Cannot carry anymore") |
| 180ac77d0 | server | GiveDefaultItems (mp_ct_default_* / mp_t_default_*, the taser, the knife) |
| 180ac8330 / 180a6ee50 / 180a6f6f0 | server | fire item_pickup (BumpWeapon's callees) |
| 0x180a259f0 | server | CCSWeaponBase::Touch -> 0x1803eeac0 |
| 0x1803eeac0 | server | CBasePlayerWeapon::Touch: the entity's touch pointer (+0x2b0) and the parent's touch |
| 0x1809f5b4c | server | the weapon's touch function: thunk to weapon vfn 0xd60 |
| 1809fc590 / 1809ff9b0 | server | install the touch function |
| 0x1809fb3c0 | server | CCSWeaponBase::DefaultTouch |
| 18017e2d0 | server | f32 compare (curtime vs a float: -1 below) |
| 180aea0a0 | server | (svc, w, silent): +use pickup, ammo extraction, swap |
| 180ade3a0 | server | the pawn's +use (from 180adf4a0) |
| 180b0adf0 | server | use code calling 180aea0a0 |
| 180a24ba0 | server | weapon Spawn |
| 1809ff9b0 | server | the weapon's body (at Spawn and every drop) |
| 180d0f2c0 | server | body create (group, interacts-with, motion) |
| 180cf16a0 | server | (collision, 0x200): interacts-as layer 9 "pickup" |
| 180cf1ab0 | server | collision function mask +0x3f |= 0x20 |
| 180d1a210 | server | (collision, 1, 30.0): trigger bloat |
| 180d1b920 | server | WorldSpaceTriggerBounds |
| 180cea8c0 | server | collision AABB of +0x40 / +0x4c |
| 180cebd90 | server | surrounding bounds (type 1 -> 180ceaf30 / 180cec040: union with the physics bounds) |
| 1803d1e50 | server | debug overlay |
| 180ac2cf0 | server | the use pick (svc, tolerance) |
| 1809f9d50 | server | (w, pawn, 1): use gates |
| 180adebd0 | server | (svc, w): can use (= client 1808e1400) |
| 180a0ecf0 / 180a0ee90 | server | is rifle / is pistol |
| 180c8cba0 | server | teleport to the player (-> vfn 0x528) |
| 18090d960 | server | CSWeaponType "1-6" (guns) |
| 180b0b020 | server | (svc, it, silent 1): drop (CSWeaponDrop mode 1, the throw) |
| 180ac7120 | server | sphere search for long-use map entities (flag 0x2000000: hostages) |
| 180ac3520 | server | FindUseEntity |
| 180250e50 | server | UTIL_TraceLine |
| 180926430 | server | returns mp_buytime (the warmup's own outside a match) |
| 18093d470 | server | buytime < time since round began |
| 180da95c0 | server | `pickup_groundweapon %d`: a panorama event's handler (buy menu), not this path |
| 180e9f9b0 | client | CCSGO_HudReticle constructor |
| 180eaf7c0 | client | its update |
| 180eb4260 | client | the target ID text |
| 180c9ec60 | client | UpdateIDTarget |
| 180c61810 | client | is weapon (hit) |
| 1808043c0 | client | CanBeTargeted |
| 1807cd4d0 | client | smoke check |
| 180eb62d0 | client | weapon text |
| 1808e1400 | client | can use (= server 180adebd0) |

## Fields

| Offset | Field |
|---|---|
| pawn +0xb10 | CCSPlayer_WeaponServices (svc) |
| pawn +0xb38 | passed to 180aeb7c0 |
| pawn +0xfb0 | with cvar 182178778: previous-owner-only pickup |
| pawn +0x388 | flags (FL_ 0x1000000 -> vfn 0x4b0 first) |
| pawn +0xf71 | in buy zone |
| pawn +0x36f8 (client) | m_iIDEntIndex |
| svc +0xd8 / +0xdc | allow non-previous-owner; +0xdc clear runs 180b23f00 |
| svc +0xd9 | 1 during the +use swap's Touch |
| svc +0xda | = 1 after equip |
| weapon +0x5e8 | plain item arg |
| weapon +0xefa | gate flag |
| weapon +0xff8 | m_bCanBePickedUp (1 from construction) |
| weapon +0xff9 | gates m_nextOwnerTouchTime |
| weapon +0xffc | m_nextOwnerTouchTime (anyone's delay) |
| weapon +0x1000 | the dropper's own delay |
| weapon +0x1008 | m_nextPrevOwnerUseTime |
| weapon +0x100c | m_hPrevOwner (last owner) |
| weapon +0x1fe0 | item id (weapon_taser's) |
| weapon +0x2b0 | touch function pointer (SetTouch) |
| weapon +0x360 | bit 1: no player pickup |
| item definition +0x700 / +0x704 | knife definition compare |
| collision +0x3f / +0x5a / +0x5c | function mask / flag 2 / m_triggerBloat |
| vphysics2 body +0x249 | bit 2: awake (vfn 0x408) |

## Constants

| Value | What |
|---|---|
| 0x181928778 | CCSPlayer_WeaponServices primary vtable (0x181928818 secondary) |
| 151 (+0x4b8) | CBaseEntity::Touch vtable index (Windows) |
| 14 "weapon", 0xc3001 | weapon body group, interacts-with |
| `(spawnflags & 1) * 2 + 1` | motion: 3 keyframed for spawnflag 1, else 1 |
| 9 "pickup" | interacts-as layer (game rules' vfn 0x148 says so) |
| 30.0 | m_triggerBloat |
| 0x18045b328 | vphysics2 group table: 0x14 for 14 x 8 ("Player") and 14 x 11 ("player_movement"): touch, no solid contact |
| (-16,-16,0)-(16,16,72), ducked 54 | pawn collision box |
| 0x3f6c835e (~ cos 22.5°) / 0x3f7c1c5c | use tolerance / with `cl_use_opens_buy_menu` and the buy zone |
| 0x181efdb70 | RTTI CCSWeaponBase (use) |
| 0x1c1003, group 4, 128 | weapon trace: interacts-with, group, max length |
| sv_extract_ammo_from_dropped_weapons | DAT_1821786c8, default 0, registered 1800cbaf0 |
| mp_buytime | registered 18009c690 |
| mp_buy_anywhere | DAT_18211a6e8, registered 18009c530 |
| GFL | mp_buy_anywhere 1, mp_buytime 9999 |
| cvars 182178790 / 182178778 | BumpWeapon gates (names unread) |
| target ID trace | 128 u, interacts-with 0x41, interacts-exclude 0x40000 (players), group 4, flags 0x49, no iteration |
| cl_use_entity_as_targetid | default 0 |
| 64 ticks | from m_nDropTick: awake-body owner test |
| `.targetid` | y 580, 1040 x 74, 22px bold white, additive, 0.1 s opacity / translateY 7px |
| cppTargetIDDuration | 0 |
| desc_default #ded6cc | items_game colour without an econ item |

CSWeaponType: 0 knife, 1 pistol, 2 SMG, 3 rifle, 4 shotgun, 5 sniper, 6 machine gun, 7 C4, 8 taser, 9 grenade (BumpWeapon also tests 11 for a grenade).

Strings: `m_OnPlayerPickup` (the weapon's output), `pickup_groundweapon`, `item_pickup`, `item_pickup_failed`, "Player.PickupWeapon".

## The touch

A weapon on the ground is picked up by **its own touch**, not a scan by the player:
1. The engine's touch (vphysics contacts / trigger overlaps: CS2Fixes' `CVPhys2World::GetTouchingList`) calls
   `CBaseEntity::Touch` -> 0x180a259f0 -> 0x1803eeac0 -> the touch function 0x1809f5b4c -> DefaultTouch 0x1809fb3c0.
2. DefaultTouch: +0xff8 set (nothing while 0); toucher a player (vfn 0x558); curtime < +0xffc: no; toucher is the last
   owner (+0x100c) and curtime < +0x1000: no (18017e2d0).
3. A live player (vfn 0x558, 0xca8); FL_ 0x1000000 in +0x388 -> its vfn 0x4b0 first.
4. Unless +0x360 bit 1: svc vfn 0xe8 = BumpWeapon; 1 -> weapon vfn 0xcb8 (picked up).

The shapes: 1809ff9b0 at Spawn (180a24ba0) and on every drop: 180d0f2c0 (group 14, 0xc3001, motion), then when the
game rules' vfn 0x148 says so 180cf16a0 (layer 9 "pickup") and 180cf1ab0 (+0x3f |= 0x20). Spawn sets the trigger
bounds (180d1a210: +0x5c = 30, flag 2 at +0x5a). WorldSpaceTriggerBounds (180d1b920) = the AABB with x and y widened
by the bloat each side and the top raised by half of it; only used by the surrounding bounds and the debug overlay.
So the pickup is the touch pair of the pawn's body and the weapon's physics shapes; the bloat only widens spatial queries.
Touches are dispatched after the step.

## BumpWeapon (180b1c290)

1. Bot (pawn vfn 0xc20): 180b01690 first.
2. Not a CCSWeaponBase: 180cee2e0(weapon+0x5e8) and 180b062d0(svc, weapon), returns 1.
3. +0xefa set: 180aeb7c0(pawn+0xb38, weapon, cvar 182178790) must pass.
4. An owner already (180b54f20) or svc vfn 0xd8 (CanUse) false: refused (2 when 180c30c10 runs for a 180093e040 mode).
5. Cvar 182178778 with pawn+0xfb0: only the previous owner (+0x100c) unless svc+0xd8 / +0xdc.
6. Weapon type (vfn 0xc60): 7 (C4) refused while carrying weapon_c4 or 180a50140(...+0xe48); taser (+0x1fe0) refused
   when one is carried; a knife refused when one of the same definition (+0x700 / +0x704) is carried.
7. Unless C4 (7), grenade (11), type 9, taser or knife: refused when the gear slot (vfn 0xa70) is taken
   (180c86620(svc, slot, -1) != 0): **a touch pickup needs the slot empty**.
8. svc+0xdc clear: 180b23f00(svc, weapon) must pass.
9. Weapon_Equip 180b23a70(svc, weapon) (or the owner branch), svc+0xda = 1.

## +use (180ade3a0)

1. Use pressed: target = 180ac2cf0(svc, tolerance); cast to CCSWeaponBase (0x181efdb70) -> 1809f9d50(w, pawn, 1) ->
   180adebd0(svc, w) -> 180aea0a0(svc, w, 0). Otherwise E may open the buy menu ("buymenu").
2. 180aea0a0: pawn passes vfn 0x550; the slot's weapon: rifle (180a0ecf0) gear slot 0, pistol (180a0ee90) slot 1,
   taser the carried weapon_taser, weapon_knife the carried knife.
3. Ammo extraction (sv_extract_ammo_from_dropped_weapons on, not type 11 or 9, gear slot 0 / 1, same item definition
   in hand and w's vfn 0xa98): clip then reserve from w into yours up to your maximums (vfns 0xaf0, 0xb18, 0xac0,
   0xb20, 0xad8); w teleported to the player (180c8cba0); its body kicked by (RandomFloat(-10, 10), RandomFloat(-10,
   10), 0) (vfn 0x208); "Player.PickupWeapon"; hint #SFUI_AmmoExtracted / _AmmoExtract_OwnFull / _Empty / _Fail.
4. Type 9 of a kind carried: merged into the carried one (vfn 0xaf8), w removed.
5. Else the swap: the slot's weapon dropped (180b0b020(svc, it, silent 1)); then silent 0: m_nextOwnerTouchTime cleared
   while +0xff9 set (restored after), svc+0xd9 = 1, w's Touch (vfn 0x4b8) with the pawn -> DefaultTouch -> BumpWeapon,
   svc+0xd9 = 0; silent 1: BumpWeapon directly. The old weapon was active -> SelectItem(w) (svc vfn 0xf0).

## The use pick (180ac2cf0)

1. 180ac7120 (sphere search, long-use entities), FindUseEntity 180ac3520.
2. Weapon trace: 180250e50 from EyePosition along EyeAngles, 0x1c1003, group 4, pawn ignored, length min(128,
   FindUseEntity's distance); a non-world weapon hit (vfn 0x598) passing 180adebd0 is the candidate; one that fails
   fires item_pickup_failed.
3. Either alone wins; both: the weapon, unless only FindUseEntity's is a usable weapon.

## The gates

- 1809f9d50(w, pawn, 1): +0xff8; curtime < +0xffc only with +0xff9; the last owner waits for +0x1008.
- 180adebd0: types 1-6 and 8 always; others only while buying is possible: 180926430 not 0, 18093d470 false, and
  mp_buy_anywhere == 1 or == the team (2, 3), or pawn +0xf71; then CanAcquire 0 or 2. (With GFL's buy anywhere: knife
  items, grenades and the C4 get the E pickup and the pickup line, a zombie on a knife item too.)

## The client's target ID (CCSGO_HudReticle, #TargetID)

- 180eaf7c0: text from 180eb4260; dialog variables weapon_name, weapon_color, target_owner, player_slot, player_health; held cppTargetIDDuration.
- Target: +0x36f8, written only by 180c9ec60 (the trace in Constants from EyePosition along EyeAngles).
- Weapon hit (180c61810): needs 1808043c0 (m_bCanBePickedUp, your own drop not before m_nextPrevOwnerUseTime) and,
  while its body is awake within 64 ticks of m_nDropTick, a last owner alive and not you; 1807cd4d0 the smoke check.
- 180eb62d0: CanAcquire else nothing; 1808e1400 false -> #Panorama_HUD_weaponid_lookat; slot (type 1: gear slot 1,
  else 0, the taser) taken -> _swap, else _pickup; weapon_name the item's name, weapon_color its rarity colour.

## Unread

- 180b23f00 (pre-equip test), 180b23a70 (Weapon_Equip: slot, owner, m_OnPlayerPickup, item_pickup).
- vphysics2's touch test for a touch-only pair (margins), the pair list's order, the game rules' vfn 0x148.
- The names of cvars 182178790 / 182178778.
