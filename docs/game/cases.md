# Cases (weapon cases, their loot, the unlock)

items_game.txt, csgo_english.txt (CS2 build of 2026-11); pak01 panorama (popup_capability_decodable.vts / .vcss,
popup_capability_header.vts, popup_acknowledge_item.*, inspect.vts, mainmenu*.vts); client_20261015 (ReVa);
server.dll ([intermission.md](intermission.md)). What the GC decides (the rare tiers' contents, the roll) is in no file.

## Functions

| Address | Module | What |
|---|---|---|
| 180e5ff90 / 180e60630 | client | MapItemPreviewPanel JS bindings (FireEntityInput, StartParticleSystem, SwitchMap, ...) |
| 180e5c1f0 | client | SetCamera |
| 180e65b40 | client | TransitionToCamera(name, seconds) |
| 180e5c200 | client | SetCameraPlaybackSpeed |
| 180e52a20 | client | PlaySequence |
| 180e5bbf0 | client | SetActiveItem |
| 180e5bd60 | client | SetAnimgraphBool(name, value) |
| 180e65c50 | client | camera manager slot 0x48: base transition 180b833b0, then playback speed (+0x74) onto the camera entity |
| 180b833b0 | client | camera manager base transition |
| 180b82920 | client | camera manager slot 0x10 (each frame) |
| 1808a4520 | client | RemapValClamped through SimpleSpline |
| 180b70d70 | client | camera manager slot 0x90: returns progress (+0x44) |
| 1809529a0 | client | (model, &seq, name): sequence by name |
| 1809657b0 | client | (model, seq, 0, 1): play it |
| 180e5c870 / 180e6bcf0 / 180e4f120 | client | read "inventory_icon" (181ccd618); 180e6bcf0 the icon pose (inventory_icon, else inventory_inspect) |
| 18007ce10 | client | registers CS_UM_SendPlayerItemDrops' hook |
| 18007ce70 | client | registers CCSUsrMsg_SendPlayerItemFound_t's hook |
| 180d119c0 | client | item found handler (msg) |
| 180acac70 | client | (entindex): the controller |
| 180903100 | client | (controller + 0x810, &out, 0, 0): the name, flags 0, a 0x294 buffer |
| 1808fbf20 | client | `<font color="%s">%s</font>` |
| 181131630 | client | (colour index): hex of 1822532c0[index] |
| 181135c10 | client | rarity definition (schema 18118e640(), rarity) |
| 18118e580 | client | (item, 1): the item's name |
| 181131e80 | client | name from the description object (+0x200; composition unread) |
| 1811a5440 | client | ChatPrintf (chat hud, flags 0x101, entindex, "%s", text) |

## Fields

| Offset | Field |
|---|---|
| panel +0x4c0 | camera manager |
| panel +0x6c8 / +0x6d0 / +0x6d8 | camera name kept before the map is up / with a duration |
| panel +0x7e8 | with a 0 duration: playback speed 1000.0 (0x447a0000) |
| panel +0x8f8 | the item model handle |
| manager [5] / [6] | current / previous camera |
| manager +0x38 / +0x3c / +0x40 / +0x44 / +0x74 | transitioning / start (slot 0x40's clock) / duration / progress / playback speed |
| camera told: old +0x38, new +0x30 / +0x10 / +0x18 / +0x20 | on a transition |
| msg +0x48 / +0x50 | item block (CEconItemPreviewDataBlock, default 182201d30) / player entity index (-1: nothing) |
| block +0xac | pickup method (low byte; proto field unread) |
| rarity definition +4 | colour index |
| gamerules +0x95c / +0x958 | drops flag / item reveal's end |
| item view vfn 0xa0 | the item's rarity |

## Constants

| Value | What |
|---|---|
| 181ccbd88 | CUI_MapPreviewCameraManager vtable (RTTI) |
| 0xe4003e | pickup methods printed (bit m = method - 1, m < 0x18) |
| 182252c00 | item-found token table [m], 24 pointers |
| 182252b30 | pickup method names (index method - 1) |
| 1822532c0 | colours ("desc_level", 3 pointers an entry: items_game `colors`) |
| 0x23b0 = 9136 | the GC drops message |
| 181baa808 / 181baa828 | strings m_flCMMItemDropRevealStartTime / EndTime (C_CSGameRules, schema only) |
| [150000, 30000, 6000, 1250, 250, 50, 10] | `_GetDisplayWeightForScroll` by GetItemRarity |
| 42 | weapon cases |
| 38, 3, 35 | reel tiles; 'ItemFromContainer', 'ItemStart' |
| 6 s, cubic-bezier(0.075, 0.82, 0.165, 1) | the scroll's transition |
| 42 times, 0 .. 5.004 s | `_TickSoundIntervals` (as listed: 1.483 before 1.351) |
| 1080 rows | panorama layout height (scaled to the screen's height) |

## The case in items_game

- Prefab `weapon_case` -> `weapon_case_base`: item_class supply_crate, capabilities.decodable, image_unusual_item
  `econ/weapon_cases/default_rare_item`, loot_list_rare_item_name `#Exceedingly_Rare_Item`.
- Loot: `attributes."set supply crate series".value` -> `revolving_loot_lists[series]` -> a `client_loot_lists` entry with
  one sub-list per tier: `<name>_rare`, `_mythical`, `_legendary`, `_ancient` (Mil-Spec, Restricted, Classified, Covert)
  and the rare tier (e.g. `community_case_11_unusual`, `spectrum_unusual`, `unusual_revolving_list`). Entries are
  `"[paint kit name]weapon class" "1"`. The rare tiers hold no list (the client only shows image_unusual_item).
- Key: `associated_items` (the first def), its `tool.restriction` matching the case's.
- Paint kit: name `description_tag`; float range `wear_remap_min` / `wear_remap_max`, default from `paint_kits["0"]`
  (0.06 / 0.8). Icon `panorama/images/econ/default_generated/<class>_<paint kit>_light_png.vtex_c` (lower case in the
  paks: `cu_bizon_Curse` is `cu_bizon_curse`); a vanilla knife's is its own image_inventory.
- Rarities: `rarities` (value, loc_key_weapon, color -> `colors.desc_*.hex_color`). Their `weight` keys (common 10000000,
  uncommon 2000000, rare 400000, mythical 80000) are the drop system's, not a case's.
- Not in CS2's files (the GC's roll): Valve's published case odds (Mil-Spec 79.92, Restricted 15.98, Classified 3.20,
  Covert 0.64, Exceedingly Rare 0.26 %); the exteriors FN / MW / FT / WW / BS over 0-.07-.15-.38-.45-1 (the float
  then remapped into [wear_remap_min, wear_remap_max]); no StatTrak on gloves. The exteriors' weights, the pattern
  seed range (0..1000) and the StatTrak chance are not known from any CS2 file (stand-ins elsewhere).

## The popup (popup_capability_decodable.vts)

- `_SetLootListItems`: every loot list item as a `LootListItem` snippet (item-tile--small: 80% ui-scale); the special
  item (id '0') as image_unusual_item with `popup-decodable-wash-color-unusual` (#ffd700).
- `_ShowUnlockAnimation`: loot count > 1 -> `_SetUpCaseOpeningScroll` (else a 5..1 countdown, container_countdown each
  second); plays `container_<type>_open` and `_ticker` (type: weapon for cases).
- `_SetUpCaseOpeningScroll`: loot list hidden; the ImagePreviewPanel path (an image, delay 0.1 s) or the model path
  (TransitionToCamera cam_case_open 1.5 s, the 'open' anim graph bool at 0.75 s, delay 2 s).
- `_FillScrollsWithItems`: each tile by `GetItemBasedOnDisplayWeight` (floor(random * total), the first item whose running
  weight is >= the draw) with the display weights; the special item is never in it.
- `_PlayScrollAnim`: `slack = floor(random * 81 + 10) / 100`; stop at the winner's actualxoffset + width * slack;
  ScrollToFitRegion; reveal at 6 s; `container_weapon_ticker` at `_TickSoundIntervals`.
- Scroll: `.popup-decodable-opening-items-container HorizontalScrollBar` transition; `flow-children: left` (tile 0 rightmost).
- Tiles: `.popup-decodable-scroll-item` 320 x 224 (70%), margin 0 10px, brightness .5, blur 3; `.magnified` 360 x 270,
  sharp, 1px #444 border; centre bar 4 x 268 warningColor (#b1af2d); masks masks/case-opening(-outer).vsvg.
- `_ShowInspect`: close, InventoryItemPreview, reveal sound by GetItemRarity: 4 Uncommon, 5 Rare, 6 Mythical, 7
  Legendary, 8 Ancient, else Common (as written: a Mil-Spec, value 3, plays Common).
- Sounds: CSGOPlaySoundEffect names are `UIPanorama.<name>` events. `container_weapon_fall` (popup open) is in no pak:
  CS2 plays nothing.

## The popup's frame

- popup_capability_header.vts, keyless (no tool_id): CapabilityTitle `#popup_totool_decodeable_header` ("Unlock
  Container"), CapabilityDesc `#popup_decodeable_desc` ("Unlock <b>{s:itemname}</b>"), CapabilityWarning (info.vsvg
  24px + `#popup_decodeable_warning`, "This Container can only be opened once"). popup_capability_shared.vcss:
  .popup-capability__top padding-top 48px; __name 50px / 54px high, medium, max 640px; desc fontSize-l 24px; warning 18px.
- popup_inspect_async-bar.vxml: .popup-capability__button-row 968px, bottom-centred, border-top 1px rgba(145,145,145,.5),
  padding 8px 0; AsyncItemWorkAcceptConfirm (`#popup_decodeable_button`, Positive) then AsyncItemWorkCancelBtn
  (`#GameUI_Close`). Accepting hides accept (spinner); Close stays. "Use <b>key</b>" (`#popup_decodeable_async_desc`) only with a key.
- csgostyles .PopupButton: margin 4px, radius 3px (btnBorderRadius), hover rgba(255,255,255,.05); Label 24px medium,
  condensed, upper case, margin 10px 12px 8px; .Positive positiveColor #0F9D58, hover brightness 1.4.
- Case picture: popup_inventory_inspect.vcss .popup-inspect-image 450px high, width 130% of that, .y-offset
  translateY(-10%) .25s; CSGOBlurTarget blurrects="DecodableLootlistContainer".
- Loot list head: CanDecodableDesc (20px, centred), CanDecodableBrowseBtn (`#popup_inv_lootlist_inspect_all`, right,
  .popup-browse-btn: padding 10px, radius 3px, hover #00000070). A tile's activate opens a context menu with Inspect
  (and the market link); INSPECT ITEMS opens the LootlistItemPreview carousel.
- mainmenu.vcss: .mainmenu-content__container rgba(0,0,0,.75) (+ blue dots at .01); .popup-inspect-border: black 0.932
  at the bottom, clear 40% to 60%, black 0.95 at the top.
- Darken: `blur: mipmapgaussian( 4, 4, 3 )`.

## The scene behind (inspect.vts)

- Model area: a MapItemPreviewPanel on a map: `_GetBackGroundMap` = `ui_inspect_bkgnd_map` + `_vanity` (e.g.
  `warehouse_vanity`, game/csgo/maps/warehouse_vanity.vpk, 20 MB), or `ui/acknowledge_item` (maps/ui/acknowledge_item.vpk,
  1 MB) for the new item's acknowledge view.
- `_InitCaseScene`: active_item_idx 6, camera `cam_case_intro`, then `_TransitionCamera(panel, 'case')` (or
  'case_new_item' in the acknowledge map); no mouse rotation. Unlock: `TransitionToCamera('cam_case_open', 1.5)`, bool
  `open` at 0.75 s, the reel after 2 s.
- warehouse_vanity: item6 at (19.93 -502.63 21.08), yaw 62.75; cam_case_intro (-207.8 -513.6 69.1, fov 30) -> after .25 s
  cam_case (-165.9 -511.5 59.1) over 1 s; cam_case_open (-147.4 -510.7 51.6) over 1.5 s. Cameras carry dof_* keys.
- Acknowledge map: entity `acknowledge_particle` gets `SetControlPoint 16: r g b` (the rarity's colour, `_SetParticlesBg`);
  lights `light_item_new<i>` get `SetColor` (rim light, `_SetRimLight`); popup_acknowledge_item's own ParticleScenePanel
  (`particles/ui/ui_item_present_bokeh.vpcf`, CP16) only for an item with no model.
- maps/ui/acknowledge_item.vpk's world is at maps/ui/acknowledge_item/ in the vpk. Entities: csgo_item_previewmodel
  "item" (0, -44, 0); point_camera_vertical_fov cam_0..cam_8 with _intro (fov 35) and per-weapon zoom cameras;
  info_particle_system "acknowledge_particle" (ui_item_present_bokeh.vpcf, start_active; children ui_item_present_rays /
  _bgglow_boid / _bgglow_burst / _floating / _bgglow_rays); light_barn light_item / light_item_new<i>.
  CParticleSystem takes the SetControlPoint input.
- New case: _InitCaseScene with useAcknowledge: ui/acknowledge_item, the crate on the item spot,
  `_TransitionCamera(panel, 'case_new_item', bSkipIntro true)`: cam_case_new_item at once, no depth of field
  ('disable-depth-of-field' true). SetItemCameraByWeaponType (m_CameraSettingsPerWeapon, else secondary 0, smg 2, 3).
- Crates: items_game model_player (39 of the 42; crate_esports_2013, _2013_winter, _2014_summer have none: CS2 shows the
  picture), sequences idle, fall 1.475 s, open 1.633 s, inventory_icon. Their logo: csgo_vertexlitgeneric's decal layer
  (F_DECAL_TEXTURE, g_tDecal) on separate quads with a second UV set (TEXCOORD_1).

## Camera transition (180e65b40, CUI_MapPreviewCameraManager)

1. TransitionToCamera: before the map is up, keep the name (+0x6c8; with a duration +0x6d0 / +0x6d8); else find the
   camera entity and call the manager (+0x4c0) slot 0x48 (camera, seconds); a 0 duration with +0x7e8 sets playback speed 1000.0.
2. 180b833b0: previous = current ([6] = [5]), current = new ([5]), each told; duration +0x40, start +0x3c, progress
   +0x44 = 0, +0x38 = 1; a 0 duration ends it at once (slot 0x80 on the previous).
3. Slot 0x10 each frame: transitioning and now < start + duration: progress = 1808a4520(now, start, start + duration, 0,
   1); else transitioning = 0, the previous released.
4. 1808a4520: `t = clamp((x - a) / (b - a), 0, 1)` (MAXSS 0, MINSS 1.0); `result = (3 - (t + t)) * t * t * (hi - lo) + lo`
   (that order); a == b: hi if x >= b, else lo.

## The crate's sequences

- models/props/crates/csgo_drop_crate_<x>.vmdl: no anim graph; AnimIncludeModel csgo_drop_crate_anims.vmdl, AnimFiles
  idle / fall / open / inventory_icon each looping false, fade in / out 0.2 s. No vnmgraph names a crate.
- SetAnimgraphBool (180e5bd60): the item model (+0x8f8); 1809529a0(model, &seq, name), found -> 1809657b0(model, seq, 0,
  1). The value is never read: SetAnimgraphBool('open', true) plays "open".
- Nothing plays "fall": client.dll has no "fall" / "idle" / "open" string; the scripts' only "fall" is
  _PlayContainerSound(caseId, 'fall') (a sound no pak has). The crate shows its first sequence, idle.

## The crate's decal (csgo_vertexlitgeneric)

- 14760 programs. Pixel static combos in order S_SPECULAR_DIRECT, S_SPECULAR_INDIRECT, S_FORCE_UV2, S_DECAL_TEXTURE,
  S_DETAIL_TEXTURE, ... (strides 1, 2, 4, 8, 16); the crate's decal materials (F_SPECULAR_DIRECT 1, F_SPECULAR_INDIRECT
  1, F_DECAL_TEXTURE 1) are combo 11 (PixelShader_s11_d*.glsl).
- After the colour's tint lerp, before lighting: `decal = Sample(g_tDecal, g_bUseSecondaryUvForDecal ? uv1 : uv0)`;
  `g_nDecalBlendMode == 0`: `colour = decal.rgb * decal.a + colour * (1 - decal.a)`; else `colour = colour * decal.rgb`.
- The vs input TEXCOORD1 is "S_FORCE_UV2=1, S_DECAL_TEXTURE=1" (the .vfx).

## NEW ITEM (popup_acknowledge_item.vxml / .vcss / .vts)

- "Dark PopupPanel popup-acknowledge" (popups_shared: #1b1b1b, 1px rgb(65,65,65), padding-bottom 16px; appears from
  opacity 0 / scale 1.2 over .5s), popupbackground dim.
- Model area 1080 x 576; .popup-acknowledge-inspect-border (black .932 bottom, clear 40-60%, black .89 top);
  .popup__rarity-bar 16px down the left, rarity-washed; title `#popup_title_crate_unlock` ("New Item") 64px bold
  condensed upper case, rgb(141,141,141) rarity-washed, at 32px / 96px; info block at 96px / 96px from the bottom left:
  name 28px bold, AcknowledgeItemSet (icon 72px high, collection name 18px: InventoryAPI.GetTag(id, 'ItemSet') ->
  items_game item_sets, icons econ/set_icons/<set>; knives / gloves have no set: hidden).
- Button row (border-top rgba(255,255,255,.068), margin 0 32px): EquipItemBtn `#inv_context_openloadout` ("View in
  Loadout"), AcknowledgeItemBtn `#ConfirmButtonText` ("CONTINUE": `UIPanorama.inventory_new_item_accept`).
- mainmenu_inventory.vts: `_RunEveryTimeInventoryIsShown` (from _Init and _OnReadyForDisplay) -> `_OnShowAcknowledgePanel`:
  AcknowledgeItems.GetItems().length > 0 -> `ShowAcknowledgePopup`; `_InventoryUpdated` the same unless the inventory
  is hidden or a capability popup is open. mainmenu.vts `_ShowAcknowledgePopup`: one popup at a time, `UIPanorama.inventory_new_item` as it opens.
- mainmenu.vts `_UpdateInventoryBtnAlert` (main menu shown, inventory updated outside a match): #MainMenuInvAlert
  (btn_alert.vxml: .navbar-btn__notification, #D8760E, radius 2px, shadowOffset, centred at the button's bottom; label
  12px white, padding 0 4px, 16px high; .hidden: opacity 0, scale 0 over .25 s), alert_value = the count.
- GetItems: InventoryAPI.GetUnacknowledgeItemsCount / ByIndex, newest first; type from the item_customization session
  property (crate_ / nametag_ / sticker_ ... else 'acknowledge'); quest / coupon_crate / campaign items acknowledged at
  once; xpshopredeem / quest_reward pickups first. MakeItemPanel per item (title `#popup_title_<type>`: "New Item" for
  acknowledge and crate_unlock), ItemCount "i / n" with more than one, ShowHideOpenItemInLayoutBtn (hidden without a
  loadout category or for a decodable). AcknowledgeAllItems.OnActivate (CONTINUE, and oncancel): all acknowledged, the accept sound.
- Carousel: carousel_nav.vxml (ItemPips, ItemCount, PreviousItemButton / NextItemButton .PaginationArrow); carousel_nav.vcss
  (.popup-acknowledge #ItemPips collapsed; CarouselNav:disabled collapsed); .PaginationArrow (expand.vsvg, 32px in
  .popup-acknowledge, Left rotateZ 90deg, Right -90deg and right aligned, hover brightness 4, disabled opacity .15);
  .PreviouslyLeft / .PreviouslyRight slide, CarouselNav full width, padding 0 32px, margin-bottom 32px; incrementsound
  inventory_new_item_scroll.

## Drops

- Server: at GoToIntermission, with `sv_matchend_drops_enabled` and the intermission not aborted, sends the GC its drops
  message (0x23b0) and sets the drops flag (gamerules +0x95c, cleared once the item reveal's end +0x958 passes:
  `endmatch_cmm_start_reveal_items`). Who gets what is the GC's: nothing of the roll is in server.dll, client.dll or items_game.
- Client: the per-match drop's remains are unused: `rarities.*.drop_sound` (EndMatch.ItemRevealRarityCommon ..
  Legendary), m_flCMMItemDropRevealStartTime / EndTime, CS_UM_SendPlayerItemDrops (18007ce10), csgo_english's
  SFUI_ItemDrop_* lines; pak01 has no end of match drops panel (panorama: endofmatch, -characters, -rank, -skillgroup,
  -voting, -win only). Since 2023 a player's drop is the Weekly Care Package on the week's first rank-up
  ([pets.md](pets.md); the rank panel's free_rewards), where a case still needs a bought key (`rankup_redemption_case_warning`).

## The item found line (180d119c0)

1. Pickup method = block +0xac low byte; `m = method - 1`; printed only when `m < 0x18` and bit m of 0xe4003e: crafted
   2, traded 3, purchased 4, found_in_crate 5, gifted 6, quest_reward 19, rental 22, xpshopredeem 23, purchasedvolatile
   24. A plain drop (1) and an earned item (9) print nothing.
2. Token 182252c00[m]: #Item_Found, _Crafted, _Traded, _Purchased, _FoundInCrate, _Gifted, 0, 0, _Earned, _Refunded,
   _GiftWrapped, _Foreign, _CollectionReward, _PreviewItem, _PreviewItemPurchased, _PeriodicScoreReward, _Recycling,
   _TournamentDrop, _QuestReward, _LevelUpReward, _Ad, _Rental, _XpShopRedeem, _PurchasedVolatile.
   Method names (182252b30, InventoryAPI.GetItemPickupMethod): dropped, crafted, traded, purchased, found_in_crate,
   gifted, support, promotion, earned, refunded, gift_wrapped, foreign, collection_reward, preview_item,
   preview_item_purchased, periodic_score_reward, recycling, tournament_drop, quest_reward, level_up_reward, ad, rental,
   xpshopredeem, purchasedvolatile.
3. %s1: the controller's name (180acac70, 180903100).
4. %s2: `<font color="%s">%s</font>`: colour = 181131630(rarity definition +4), the text 18118e580(item, 1) (e.g.
   "★ StatTrak™ Karambit | Fade"). The item is in its **rarity's** colour; StatTrak shows in the name, not as a colour.
5. Localized with 3 arguments (localizer vfn 0xd8: name, font string, empty third), printed by 1811a5440: the line's
   sender the player (\x03: their team's colour).
- csgo_english Item_FoundInCrate: " \x03%s1\x01 has opened a container and found: %s2".

## Unread

- The cameras' blend by the manager's progress (no static caller in 180b6..180b9 or 180e2..180e7 takes slot 0x90).
- The darken's blur radius (panorama.dll, not in the ReVa project).
- The item's name composition (181131e80); which proto field +0xac is; SendPlayerItemDrops' handler (the old end of match reveal).
- popup_inventory_inspect's full layout, popup_container_open_confirm, the async bar's hold button and work-type warning;
  souvenir / sticker capsules; the count label's font size (panorama's default Label size).
