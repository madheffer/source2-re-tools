# Cases (weapon cases, their loot, the unlock)

What the home's cases are built from, which parts are CS2's and which stand in for Valve's Game Coordinator (GC).
Code: tools/case-list.mjs, tools/case-rare-import.mjs, bake/CasesBake.cs (`lasers-bake --cases`),
web/server/cs2web/econ/ (catalog, roll, inventory-store, routes, econ-test.mjs), web/src/cs2web/client/home/cases/.

## From CS2's files (items_game.txt, csgo_english.txt; CS2 build of 2026-11)

- A weapon case: an item made from prefab `weapon_case` (-> `weapon_case_base`: item_class supply_crate,
  capabilities.decodable, image_unusual_item default `econ/weapon_cases/default_rare_item`,
  loot_list_rare_item_name `#Exceedingly_Rare_Item`). 42 of them.
- Its loot: `attributes."set supply crate series".value` -> `revolving_loot_lists[series]` -> a
  `client_loot_lists` entry holding one sub-list per tier: `<name>_rare`, `_mythical`, `_legendary`, `_ancient`
  (Mil-Spec, Restricted, Classified, Covert) and the rare tier (e.g. `community_case_11_unusual`, `spectrum_unusual`,
  `unusual_revolving_list`). A tier's entries are `"[paint kit name]weapon class" "1"`.
- The key: `associated_items` (the first def), its `tool.restriction` matching the case's.
- A paint kit's name: `description_tag`; its float range `wear_remap_min` / `wear_remap_max`, default from
  `paint_kits["0"]` (0.06 / 0.8). The icon: `panorama/images/econ/default_generated/<class>_<paint kit>_light_png.vtex_c`
  (lower case in the paks: `cu_bizon_Curse` is `cu_bizon_curse` there); a vanilla knife's is its own image_inventory.
- Rarities: `rarities` (value, loc_key_weapon, color -> `colors.desc_*.hex_color`). Their `weight` keys (common
  10000000, uncommon 2000000, rare 400000, mythical 80000) are the drop system's, not a case's: not used.

## Not in CS2's files (the GC's): stand-ins, seeded into the econ tables and editable there

- **The rare tiers' contents.** items_game names them but holds no list (the client only ever shows
  image_unusual_item). tools/data/case-rare-items.json, imported by tools/case-rare-import.mjs from
  ByMykel/CSGO-API's crates.json (`contains_rare`); every (class, paint kit) checked against items_game.
- **The roll** (server/cs2web/econ/roll.js, numbers in catalog.js):
  - tier: Valve's published case odds as weights (econ_rarities.case_weight): Mil-Spec 79.92, Restricted 15.98,
    Classified 3.20, Covert 0.64, Exceedingly Rare 0.26
  - the item in its tier: econ_case_items.weight (1 each, as the loot lists)
  - wear: an exterior bucket by weight (econ_wear_buckets: FN 3, MW 24, FT 33, WW 24, BS 16 over 0-.07-.15-.38-.45-1),
    a uniform float in it, remapped into [wear_remap_min, wear_remap_max]
  - pattern seed uniform 0..1000 (econ_settings.seed_max), StatTrak 10% (stattrak_chance), never on gloves
  - checked: econ-test.mjs, 200k rolls within 5 sigma of each tier's share

## The popup (panorama/scripts/popups/popup_capability_decodable.vts, decompiled into web/public/ze-cases/reference)

- `_SetLootListItems`: every loot list item as a `LootListItem` snippet (item-tile--small: 80% ui-scale), the special
  item (id '0') as the case's image_unusual_item with `popup-decodable-wash-color-unusual` (#ffd700)
- `_ShowUnlockAnimation`: loot count > 1 -> `_SetUpCaseOpeningScroll` (else the 5..1 countdown, container_countdown
  each second: not built, no case has one item); plays `container_<type>_open` and `_ticker` (type: weapon for cases)
- `_SetUpCaseOpeningScroll`: loot list hidden; the ImagePreviewPanel path (an image, delay 0.1 s) or the model path
  (TransitionToCamera cam_case_open 1.5 s, the 'open' anim graph bool at 0.75 s, delay 2 s). We draw the image.
- `_FillScrollsWithItems`: 38 tiles; tile 3 'ItemFromContainer', tile 35 'ItemStart'; each drawn by
  `GetItemBasedOnDisplayWeight` (floor(random * total), first item whose running weight is >= the draw) with
  `_GetDisplayWeightForScroll`: [150000, 30000, 6000, 1250, 250, 50, 10][GetItemRarity]; the special item is never in it
- `_PlayScrollAnim`: slack = floor(random * 81 + 10) / 100; stop at the winner's actualxoffset + width * slack;
  ScrollToFitRegion; reveal at 6 s; `container_weapon_ticker` at `_TickSoundIntervals` (42 times, 0 .. 5.004 s, as listed:
  1.483 comes before 1.351 in Valve's list)
- the scroll's motion: popup_capability_decodable.vcss `.popup-decodable-opening-items-container HorizontalScrollBar`
  transition 6 s cubic-bezier(0.075, 0.82, 0.165, 1); `flow-children: left` (tile 0 rightmost)
- tiles: `.popup-decodable-scroll-item` 320 x 224 (70%), margin 0 10px, brightness .5, blur 3; `.magnified` 360 x 270,
  sharp, 1px #444 border; the centre bar 4 x 268 warningColor (#b1af2d); masks masks/case-opening(-outer).vsvg
- `_ShowInspect`: close, InventoryItemPreview, the reveal sound by GetItemRarity: 4 Uncommon, 5 Rare, 6 Mythical,
  7 Legendary, 8 Ancient, else Common (as written: a Mil-Spec, value 3, plays Common)
- sounds: CSGOPlaySoundEffect names are `UIPanorama.<name>` sound events. `container_weapon_fall` (played when the
  popup opens) is in no CS2 pak: CS2 plays nothing, nor do we.
- panorama's layout is at 1080 rows, scaled to the screen's height: the whole popup (and the item inspect) is CSS-zoomed
  by innerHeight / 1080, so every px in cases.css is CS2's own.

## The popup's frame (what the decodable popup loads around the reel)

- popup_capability_header.vts on the keyless path (no tool_id): CapabilityTitle `#popup_totool_decodeable_header`
  ("Unlock Container"), CapabilityDesc `#popup_decodeable_desc` ("Unlock <b>{s:itemname}</b>"), CapabilityWarning (info.vsvg
  24px + `#popup_decodeable_warning`, "This Container can only be opened once"). Styles popup_capability_shared.vcss:
  .popup-capability__top padding-top 48px; __name 50px / 54px high, medium, max 640px; desc fontSize-l 24px; warning 18px.
- popup_inspect_async-bar.vxml: .popup-capability__button-row 968px, bottom-centred, border-top 1px rgba(145,145,145,.5),
  padding 8px 0; AsyncItemWorkAcceptConfirm (`#popup_decodeable_button`, class Positive) then AsyncItemWorkCancelBtn
  (`#GameUI_Close`). Accepting hides the accept button (and shows a spinner); Close stays. The "Use <b>key</b>" line
  (`#popup_decodeable_async_desc`) shows only with a key.
- csgostyles .PopupButton: margin 4px, radius 3px (btnBorderRadius), hover rgba(255,255,255,.05); its Label 24px medium,
  condensed, upper case, margin 10px 12px 8px; .Positive positiveColor #0F9D58, hover brightness 1.4.
- the case picture: popup_inventory_inspect.vcss .popup-inspect-image, 450px high, width 130% of that, .y-offset
  translateY(-10%) .25s; CSGOBlurTarget blurrects="DecodableLootlistContainer": what lies under the loot list is blurred.
- the loot list's head: CanDecodableDesc (20px, centred) and CanDecodableBrowseBtn (`#popup_inv_lootlist_inspect_all`,
  right, .popup-browse-btn: padding 10px, radius 3px, hover #00000070). A tile's activate opens a context menu with
  Inspect (and the market link): ours opens the inspect directly; INSPECT ITEMS opens the first item (CS2's
  LootlistItemPreview carousel: not built).
- mainmenu.vcss (baked since): .mainmenu-content__container rgba(0,0,0,.75) (+ blue dots at .01) behind;
  .popup-inspect-border over the scene: black 0.932 at the bottom, clear from 40% to 60%, black 0.95 at the top.

## The scene behind (inspect.vts): maps, not pictures

- the popup's model area is a MapItemPreviewPanel on a map: `_GetBackGroundMap` = the `ui_inspect_bkgnd_map` setting
  + `_vanity` (the YouTube captures: `warehouse_vanity`, game/csgo/maps/warehouse_vanity.vpk, 20 MB), or
  `ui/acknowledge_item` (maps/ui/acknowledge_item.vpk, 1 MB) when it's the new item's acknowledge view
- `_InitCaseScene`: active_item_idx 6, camera `cam_case_intro`, then `_TransitionCamera(panel, 'case')` (or 'case_new_item'
  in the acknowledge map); no mouse rotation. The unlock: `TransitionToCamera('cam_case_open', 1.5)` and the model's
  anim graph bool `open` at 0.75 s (the model path of _SetUpCaseOpeningScroll, delay 2 s before the reel)
- the acknowledge map: entity `acknowledge_particle` gets `SetControlPoint 16: r g b` (the rarity's colour,
  `_SetParticlesBg`), lights `light_item_new<i>` get `SetColor` (rim light, `_SetRimLight`); popup_acknowledge_item's own
  ParticleScenePanel (`particles/ui/ui_item_present_bokeh.vpcf`, CP16) shows only for an item with no model
- built (2026-11-16): client/home/cases/inspect-scene.js draws warehouse_vanity (tools/bake-map.mjs, baked into
  web/public/maps/warehouse_vanity) as the home's scene draws de_dust2_vanity (the shared parts: client/home/vanity-map.js),
  taking the renderer while the popup is open and handing it back (the home's map reloads: ~several s); the case's model
  on item6 (origin 19.93 -502.63 21.08, yaw 62.75); cam_case_intro (-207.8 -513.6 69.1, fov 30) -> after .25 s cam_case
  (-165.9 -511.5 59.1) over 1 s; the unlock to cam_case_open (-147.4 -510.7 51.6) over 1.5 s, "open" at .75 s, the reel
  after 2 s over the scene blurred and darkened (brightness .4). The cameras' depth of field from their dof_* keys.
- the crates: items_game model_player (39 of the 42 cases; crate_esports_2013, _2013_winter and _2014_summer have none:
  CS2 shows their picture, as we do), baked by `lasers-bake --cases --models tools/data/case-models.txt` with their
  sequences (idle, fall 1.475 s, open 1.633 s, inventory_icon). Their logo is csgo_vertexlitgeneric's decal layer
  (F_DECAL_TEXTURE, g_tDecal) on separate quads with a second UV set (TEXCOORD_1); the glTF export drops it, so the bake
  decodes each g_tDecal beside the glb and the client mixes it in its shader (below: "The crate's decal").
- traced since (client_20261015.dll): the camera progress (SimpleSpline) and the crate's sequences ("The camera manager", "The crate's sequences" below). Still ours: how the progress blends the two cameras (lerped), the darken's blur radius.
- seen: some warehouse surfaces (the forklift, the shelving) draw as blocky noise in the test pane; not looked into.

## The crate's decal (csgo_vertexlitgeneric, traced)

- `lasers-bake --shader-src csgo_vertexlitgeneric <out>`: 14760 programs. The pixel shader's static combos in order
  S_SPECULAR_DIRECT, S_SPECULAR_INDIRECT, S_FORCE_UV2, S_DECAL_TEXTURE, S_DETAIL_TEXTURE, ... (strides 1, 2, 4, 8, 16);
  the crate's decal materials (F_SPECULAR_DIRECT 1, F_SPECULAR_INDIRECT 1, F_DECAL_TEXTURE 1) are combo 11
  (PixelShader_s11_d*.glsl). Its decal step, after the colour's tint lerp and before lighting:
  `decal = Sample(g_tDecal, g_bUseSecondaryUvForDecal ? uv1 : uv0)`;
  `g_nDecalBlendMode == 0`: `colour = decal.rgb * decal.a + colour * (1 - decal.a)`; else `colour = colour * decal.rgb`.
  The vs input TEXCOORD1 is "S_FORCE_UV2=1, S_DECAL_TEXTURE=1" (the .vfx). Built: inspect-scene.js applyDecals.

## The item preview panel (client_20261015.dll, ReVa /client_20261015.dll)

- 180e5ff90 / 180e60630: the MapItemPreviewPanel's JS bindings (FireEntityInput, StartParticleSystem, SetCamera
  180e5c1f0, TransitionToCamera 180e65b40, SetCameraPlaybackSpeed 180e5c200, SwitchMap, PlaySequence 180e52a20,
  SetActiveItem 180e5bbf0, SetAnimgraphBool 180e5bd60, ...)
- 180e65b40 TransitionToCamera(name, seconds): before the map is up it keeps the name for later (+0x6c8; with a duration
  +0x6d0 / +0x6d8); else it finds the camera entity and calls the panel's camera manager (panel+0x4c0) at vtable slot
  0x48 with (camera, seconds); a 0 duration with +0x7e8 set also sets the playback speed to 1000.0 (0x447a0000)

## The camera manager (CUI_MapPreviewCameraManager, vtable 181ccbd88 by RTTI: tools/re/rtti_vtable.py)

- slot 0x48 = 180e65c50: the base transition 180b833b0, then the playback speed (+0x74) onto the camera entity
- 180b833b0 (base): to a new camera: previous = current ([6] = [5]), current = the new one ([5]), each told (old +0x38,
  new +0x30 / +0x10 / +0x18 / +0x20); duration at +0x40, start = slot 0x40's clock at +0x3c, progress +0x44 = 0,
  transitioning (+0x38) = 1; a 0 duration ends it at once (slot 0x80 on the previous)
- slot 0x10 = 180b82920 (each frame): while transitioning and now < start + duration, progress =
  1808a4520(now, start, start + duration, 0, 1); else transitioning = 0, the previous released
- 1808a4520: RemapValClamped through SimpleSpline: t = clamp((x - a) / (b - a), 0, 1) (MAXSS 0, MINSS 1.0),
  result = (3 - (t + t)) * t * t * (hi - lo) + lo (that summation order; a == b: hi if x >= b, else lo)
- slot 0x90 = 180b70d70: returns progress (+0x44). Not yet read: which camera-side method takes it to blend the two
  cameras' origin / angles / fov (no static caller in 180b6..180b9 or 180e2..180e7 did); ours lerps them.

## The crate's sequences (traced)

- models/props/crates/csgo_drop_crate_<x>.vmdl: no anim graph; AnimIncludeModel csgo_drop_crate_anims.vmdl, whose
  AnimFiles idle / fall / open / inventory_icon are each looping false, fade in / out 0.2 s. No vnmgraph names a crate.
- 180e5bd60 SetAnimgraphBool(name, value): the panel's item model (handle +0x8f8); `1809529a0(model, &seq, name)`
  (the sequence by that name), and when found `1809657b0(model, seq, 0, 1)` plays it. The value is never read: the
  case popup's SetAnimgraphBool('open', true) plays "open".
- nothing plays "fall": client.dll has no "fall" / "idle" / "open" string, and the scripts' only "fall" is
  _PlayContainerSound(caseId, 'fall') (a sound, container_weapon_fall, which no pak has). The crate shows its first
  sequence, idle.
- "inventory_icon" (181ccd618) is read by 180e5c870, 180e6bcf0, 180e4f120: 180e6bcf0 is the icon pose (inventory_icon,
  else inventory_inspect, through 1809657b0), not the popup's

## Still to trace

- the cameras' blend by the manager's progress (above)
- the darken: panorama's `blur: mipmapgaussian( 4, 4, 3 )` (panorama.dll, not in the ReVa project): its pixel radius

## NEW ITEM's scene (built)

- maps/ui/acknowledge_item.vpk's world is at maps/ui/acknowledge_item/ in the vpk: the bake (Program.cs) now keeps a plain
  map vpk's real world folder and writes it to manifest.json "vmap" (MapDir.World reads it, as for spawn groups), so
  lighting / tiers / vis find it. Baked to maps/acknowledge_item (25 MB; tools/bake-map.mjs --steps map,lighting,tiers:
  the chunks step stops on a missing satellite texture of its world glb, and a map this small needs no chunks)
- its entities: csgo_item_previewmodel "item" (0, -44, 0); point_camera_vertical_fov cam_0..cam_8 with _intro (fov 35)
  and the per-weapon zoom cameras; info_particle_system "acknowledge_particle"
  (particles/ui/ui_item_present_bokeh.vpcf, start_active; its children ui_item_present_rays / _bgglow_boid /
  _bgglow_burst / _floating / _bgglow_rays baked); light_barn light_item / light_item_new<i>
- inspect-scene.js showItem: the camera by SetItemCameraByWeaponType (m_CameraSettingsPerWeapon, else secondary 0,
  smg 2, 3) with _TransitionCamera's intro; `SetControlPoint 16: r g b` (the rarity's colour) into acknowledge_particle
  (CParticleSystem has the input in CS2's table: sim/src/game/input_table.rs; entities/classes/fx.js now takes it,
  render.js draws the set point); the system restarted once the scene draws (its burst fired at spawn while the map
  loaded unseen). The popup's model area clear onto it, the dim only around the panel.
- not built: _SetRimLight's light_item_new<i> SetColor (light_barn isn't a runtime light: world/maplights.js), the
  weapon's model with its paint kit (the popup shows its picture over the scene)

## NEW ITEM (popup_acknowledge_item.vxml / .vcss / .vts, after the reel)

- `_ShowInspect` -> InventoryItemPreview of the new item -> popup_acknowledge_item: "Dark PopupPanel popup-acknowledge"
  (popups_shared: #1b1b1b, 1px rgb(65,65,65), padding-bottom 16px; appears from opacity 0 / scale 1.2 over .5s),
  popupbackground dim
- the Item: model area 1080 x 576; .popup-acknowledge-inspect-border (black .932 bottom, clear 40-60%, black .89 top);
  .popup__rarity-bar 16px down the left, washed with the rarity colour; the title `#popup_title_crate_unlock` ("New
  Item") 64px bold condensed upper case, rgb(141,141,141) washed with the rarity colour, at 32px / 96px; the info block
  at 96px / 96px from the bottom left: the name 28px bold, AcknowledgeItemSet (icon 72px high, then the collection's
  name 18px: InventoryAPI.GetTag(id, 'ItemSet') -> items_game item_sets, icons econ/set_icons/<set>; knives / gloves
  have no set: hidden)
- the button row (border-top rgba(255,255,255,.068), margin 0 32px): EquipItemBtn `#inv_context_openloadout` ("View in
  Loadout") and AcknowledgeItemBtn `#ConfirmButtonText` ("CONTINUE": `UIPanorama.inventory_new_item_accept`)
- built: acknowledge-item.js / cases.css; the scene behind: "NEW ITEM's scene" above (the radial wash shows only until it's up)

## Drops (what CS2 does at a match's end, and ours)

- **CS2's server** (server.dll, docs/game/intermission.md): at GoToIntermission, with `sv_matchend_drops_enabled` and
  the intermission not aborted, it sends the Game Coordinator its drops message (0x23b0 = 9136) and sets the drops flag
  (gamerules +0x95c, cleared once the item reveal's end +0x958 passes: `endmatch_cmm_start_reveal_items`). Who gets
  what is the GC's: nothing of the roll is in server.dll, client.dll or items_game.
- **CS2's client**: what remains of the per-match drop is unused. `rarities.*.drop_sound`
  (EndMatch.ItemRevealRarityCommon .. Legendary), C_CSGameRules m_flCMMItemDropRevealStartTime / EndTime (strings
  181baa808 / 181baa828, schema only), CS_UM_SendPlayerItemDrops (its hook registered at 18007ce10) and csgo_english's
  SFUI_ItemDrop_* lines; pak01 has no end of match drops panel (panorama: endofmatch, -characters, -rank, -skillgroup,
  -voting, -win only). Since 2023 the drop a player sees is the Weekly Care Package on the week's first rank-up
  (docs/game/pets.md; the rank panel's free_rewards), where a case still needs a bought key
  (`rankup_redemption_case_warning`).
- **Ours** (server/cs2web/econ/drops.js; every number a stand-in in econ_settings, the owner's to tune): the director
  is the GC. At a match's end each signed-in player who played it gets one roll: a queued team match and a deathmatch
  from the matchmaker's onMatchOver (players on a side; not a cancelled match, not a private custom lobby; a
  deathmatch only for a player who scored), a Zombie Escape map at its intermission (game.js goToIntermission, where
  CS2 sends its drops message: players active 600 s on the map, modes/ze/ze-xp.js). Chance: 5v5 15 %, 1v1 / 3v3 6 %,
  deathmatch 5 %, a ZE map 12 %; at most 3 a week an account (the week: Wednesday 01:00 UTC, xp.js) and none within
  20 min of the last; guests get none (a guest token is free to make). The case is one of the week's rotation, by
  weight (econ_cases.drop_weight; unset 1, 0 never): an admin's pick for the week (econ_drop_rotation), else six cases
  along a seeded shuffle of the weapon cases, the next six each week. Tuned in the admin panel (docs/ADMIN_PANEL.md
  "Case drops"). It lands in
  ze_inventory with `acknowledged = false` (origin 'drop', econ_drop_log), from a game host through the fleet link's
  `played { id, steamId, kind }` event. No end of match panel shows it (CS2 has none): the Inventory button's alert and
  the NEW ITEM popup do.

## The item found line (client_20261015.dll, the unbox's chat line)

- 18007ce70 registers the hook for CCSUsrMsg_SendPlayerItemFound_t (CS_UM_SendPlayerItemFound); its handler is
  **180d119c0**(msg): msg+0x48 the item block (CEconItemPreviewDataBlock, default 182201d30), msg+0x50 the player's
  entity index (-1: nothing).
  - the pickup method: the block's +0xac, low byte (which proto field that is: unread). `m = method - 1`; printed only
    when `m < 0x18` and bit m of **0xe4003e** is set: crafted 2, traded 3, purchased 4, found_in_crate 5, gifted 6,
    quest_reward 19, rental 22, xpshopredeem 23, purchasedvolatile 24. A plain drop (1) and an earned item (9) print
    nothing.
  - the token: table **182252c00**[m], 24 pointers: #Item_Found, _Crafted, _Traded, _Purchased, _FoundInCrate, _Gifted,
    0, 0, _Earned, _Refunded, _GiftWrapped, _Foreign, _CollectionReward, _PreviewItem, _PreviewItemPurchased,
    _PeriodicScoreReward, _Recycling, _TournamentDrop, _QuestReward, _LevelUpReward, _Ad, _Rental, _XpShopRedeem,
    _PurchasedVolatile. The methods' names (InventoryAPI.GetItemPickupMethod's strings) are the table at 182252b30
    (index method - 1: dropped, crafted, traded, purchased, found_in_crate, gifted, support, promotion, earned,
    refunded, gift_wrapped, foreign, collection_reward, preview_item, preview_item_purchased, periodic_score_reward,
    recycling, tournament_drop, quest_reward, level_up_reward, ad, rental, xpshopredeem, purchasedvolatile).
  - %s1: the controller's name (180acac70(entindex) the controller, 180903100(controller + 0x810, &out, 0, 0): flags
    0, a 0x294 buffer).
  - %s2: `<font color="%s">%s</font>` (1808fbf20): the colour 181131630(colour index) = the hex of
    table 1822532c0[index] ("desc_level", 3 pointers an entry: items_game `colors`), the index the rarity definition's
    +4 (181135c10(schema 18118e640(), the item's rarity: the item view's vfn 0xa0)); the text 18118e580(item, 1), the
    item's name (181131e80 over the item's description object at +0x200: its composition unread; the home's names are
    "★ StatTrak™ Karambit | Fade"). So the item is in its **rarity's** colour; StatTrak shows in the name, not as a colour.
  - localized with 3 arguments (the localizer's vfn 0xd8: the name, the font string, an empty third), printed by
    1811a5440(chat hud, flags 0x101, entindex, "%s", text): ChatPrintf, the line's sender the player (\x03: their
    team's colour).
- csgo_english: Item_FoundInCrate " \x03%s1\x01 has opened a container and found: %s2" (the others:
  server/cs2web/comms/item-found.js).
- Built: econ/routes.js onUnbox -> comms/item-found.js announceItemFound: every match the opener is in (a remote
  host's through the fleet command `itemfound`). The font tag's colour travels beside the text (`hex`, \x11 marks where
  it starts: lib/chat-colors.js chatRuns), since the chat's colour codes hold no arbitrary hex.

## NEW ITEM for what you haven't seen (the drop's popup, the Inventory's alert)

- mainmenu_inventory.vts: `_RunEveryTimeInventoryIsShown` (from _Init and _OnReadyForDisplay) calls
  `_OnShowAcknowledgePanel`: AcknowledgeItems.GetItems().length > 0 -> `ShowAcknowledgePopup`; `_InventoryUpdated` does
  the same unless the inventory is hidden or a capability popup is open. mainmenu.vts `_ShowAcknowledgePopup`: one
  popup at a time (popup_acknowledge_item.xml), `UIPanorama.inventory_new_item` as it opens.
- mainmenu.vts `_UpdateInventoryBtnAlert` (main menu shown, inventory updated outside a match): #MainMenuInvAlert in
  the Inventory nav button (btn_alert.vxml: .navbar-btn__notification, #D8760E, radius 2px, shadowOffset, centred at
  the button's bottom; its label 12px white, padding 0 4px, 16px high; .hidden: opacity 0 and scale 0 over .25 s),
  alert_value = the count.
- popup_acknowledge_item.vts GetItems: InventoryAPI.GetUnacknowledgeItemsCount / ByIndex, newest first; the type from
  the item_customization session property (crate_ / nametag_ / sticker_ ... else 'acknowledge'); quest / coupon_crate /
  campaign items acknowledged at once; xpshopredeem / quest_reward pickups first. MakeItemPanel per item (title
  `#popup_title_<type>`: "New Item" for acknowledge and crate_unlock), ItemCount "i / n" with more than one,
  ShowHideOpenItemInLayoutBtn (View in Loadout hidden without a loadout category or for a decodable).
  AcknowledgeAllItems.OnActivate (CONTINUE, and the popup's oncancel): every item acknowledged, the accept sound.
- the carousel: carousel_nav.vxml (ItemPips, ItemCount, PreviousItemButton / NextItemButton .PaginationArrow),
  carousel_nav.vcss (.popup-acknowledge #ItemPips collapsed; CarouselNav:disabled collapsed), csgostyles
  .PaginationArrow (expand.vsvg, 32px in .popup-acknowledge, Left rotateZ 90deg, Right -90deg and right aligned, hover
  brightness 4, disabled opacity .15), popup_acknowledge_item.vcss (.PreviouslyLeft / .PreviouslyRight slide,
  CarouselNav full width, padding 0 32px, margin-bottom 32px), incrementsound inventory_new_item_scroll.
- a new case's scene: inspect.vts _InitCaseScene with useAcknowledge: the map ui/acknowledge_item, the crate on the
  item spot, `_TransitionCamera(panel, 'case_new_item', bSkipIntro true)`: cam_case_new_item at once, no depth of field
  ('disable-depth-of-field' true in the acknowledge map).
- Built: ze_inventory.acknowledged / the item's `unack`, POST /api/ze/inv/ack; client/home/cases/acknowledge-item.js
  (the carousel), econ-inventory.js showNew (the Inventory shown, an update while it is up), inventory.js (the alert),
  inspect-scene.js showItem (the crate under cam_case_new_item). Ours: the count label's font size (panorama's default
  Label size: unread, 18px here); arrow keys step the carousel.

## Left (unread / not built)

- drops: the GC's real odds and pools (stand-ins above); the item's name composition (181131e80); which proto field the
  pickup method's +0xac is; SendPlayerItemDrops' handler (the old end of match reveal)

- the weapon's 3D model with its paint kit; the camera controller's curve, the crate's sequence choice, the darken blur ("Still to trace"); the warehouse textures' noise
- popup_inventory_inspect's full layout, popup_container_open_confirm, the async bar's hold button and work-type
  warning; keys (econ_cases.needs_key: built server-side, off; keys can't be got yet); souvenir / sticker capsules
- skins in the loadout and drawn in game (paint kit compositing)

