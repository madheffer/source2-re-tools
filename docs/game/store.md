# The Store (the main menu's STORE page)

pak01 panorama sources only (CS2 build of 2026-11; no DLL read): layout/mainmenu_store_fullscreen.vxml,
scripts/mainmenu_store_fullscreen.vts, styles/mainmenu_store_fullscreen.vcss, layout/itemtile_store.vxml,
scripts/itemtile_store.vts, styles/itemtile_store.vcss, scripts/common/store_items.vts, rankup_redemption_store
(.vxml / .ts / .vcss). Decompiled with `lasers-bake --decompile <pak01> "panorama/(layout|scripts|styles)/(mainmenu_store_fullscreen|store\.|storeitem|itemtile_store|common/store_items|mainmenu_store_tile_linked|popups/popup_store_status|context_menus/context_menu_store_linked)" <scratch>`.

## The page

- Root: `.mainmenu-content__container` > `#id-mainmenu-store` (flow down): tab row `#id-mainmenu-store-tabs`
  (`.content-navbar__tabs content-navbar__tabs--noflow`), then `#id-store-pages`.
- Tab row: RadioButton `#id-store-nav-home` (`#store_nav_home`, group store-top-nav, `.content-navbar__tabs__btn`), then
  `#id-store-lister-tabs` filled by `MakeTabsBtnsFromStoreData`: one radio per key of `StoreItems.GetStoreItems()` with
  items (`#store_nav_<key>`; tournament `#store_nav_tournament_<eventid>`), then always `id-store-nav-xpshop`
  (`#store_tab_xpshop`, "Armory", with a `content-navbar__tabs__btn-new` count when the XP shop has new goods). Right:
  `#id-store-nav-wallet` (`#Store_Wallet_Balance_dv`, StoreAPI.OpenAccountWalletAddFundsURL), hidden unless the
  launcher is Perfect World (`AccountWalletUpdated`).
- `NavigateToTab(panelId, keyType)`: home refills `UpdateItemsInHomeSection('coupon', 'id-store-popular-items', 6)` and
  `('tournament', 'id-store-tournament-items', 1)`; another tab is made on first use (`MakePageFromStoreData`): xpshop
  loads layout/xpshop.xml, any other key a `JSDelayLoadList.store-dynamic-lister` (itemwidth 178px, itemheight 280px,
  spacersize 4px, spacerperiod 4px) of itemtile_store cells. The shown page has class `Active`.
- Home `#id-store-page-home` > `.store-home-container`:
  - `#id-rewards-background.store-home-rewards-section`: CSGOBlurTarget `.store-home-rewards-section-bg` and Frame
    `.rrs-popup__frame` of layout/rankup_redemption_store.vxml (Weekly Care Package: pets.md). `.hidden` without Prime.
  - `#id-prime-background.store-home-prime-section`: Prime upsell (logo, title, buy button, three columns over
    de_inferno / de_ancient / de_anubis screenshots). Only without Prime (`ShowPrimePanelOnHomePage`).
  - `#id-store-home-section-coupon.store-home-section`: `.store-home-popular__info` with the title (`#store_nav_popular`,
    `.store-home-section__title stratum-regular-condensed fontSize-xxl`), tiles `#id-store-popular-items.store-home-popular__items`,
    button `.store-home-popular__btn` (`#store_nav_more` + expand.vsvg: `GotoStorePage('id-store-nav-coupon')`).
    Background set by script: `images/backgrounds/store_home_coupon.psd`, 50% 50%, cover (suffix `_nightmode2` while the
    first coupon is a new release with id 17293822569102711679).
  - `#id-store-home-section-tournament.store-home-section`: the same for the active tournament, plus the
    TournamentStickers snippet (five random team stickers, rotated; opens popup_major_hub). Hidden with no items and no
    active tournament.
- `ReadyForDisplay`: needs the GC (`ConnectedToGcCheck`, else `#SFUI_SteamConnectionErrorTitle`); rebuilds the item list
  when empty; `PanoramaComponent_Store_PriceSheetChanged` runs it again.
- Tab sound: `UIPanorama.tab_mainmenu_shop`.

## The items (store_items.vts)

- `MakeStoreItemList`: each of `StoreAPI.GetBannerEntryCount()` banner entries (the GC's list): def index -> faux item
  id, sorted into `key` (a tool whose first capability is decodable; not on Perfect World), `market`
  (`IsBannerEntryMarketLink`), `coupon` (custom format string starts "coupon"; "coupon_new" marks `isNewRelease`, and
  with no linked coupon `activationType 'newstore'`; `GetBannerEntryLinkedCoupon` gives `linkedid`), else `store`.
- `AllowDisplayingItemInStore` drops decodables whose restriction is "restricted" or "xray" (crate_stattrak_swap_tool
  always passes). `tournament` from `g_ActiveTournamentStoreLayout` (generated/items_event_current_generated_store);
  `prime` stays empty.
- The tabs (General = store, Market, Tools = key, Armory) and New & Popular are the GC's banner list and Steam's price
  sheet: none of it is in a CS2 file. Storage Unit: items_game 1201 `casket`.

## The tile (itemtile_store)

- `.itemtile-store` 160 x 270, margin 8, `gradient(linear, 0% 100%, 0% 0%, from(#3a39398f), to(rgba(4,123,4,0)))`,
  shadow rgba(0,0,0,.4) 1px 1px 6px. `.itemtile-store__container` flow down:
  - `.itemtile-store__image-Container` 170px: main ItemImage 100% wide, height 80% of the width, centred; `__item-image-bg`
    the same image pre-transform-scale2d 4, blur mipmapgaussian(2,2,2), saturation .9, opacity .35; labels `__stattrak`
    (rgb(172,146,0), 12px bold), `__new` (#D8760E, right top, 14px, padding 4px), `__not-released` (blueColor).
  - `__name`: margin 8px left / top, 14px medium, max-height 34px, ellipsis.
  - `.itemtile-store__bottomrow` (bottom, margin 0 8px 8px): `__price-container` 24px (28px `.has-reduction`):
    `__price-reduction-container` (positiveColor, "-N%" 16px medium, padding 0 4px), `__price-labels` (flow down,
    padding 0 6px 0 4px): `__price-original` (12px, line-through, translateY 2px; shown with a reduction), `__price-sale`
    (rgb(23,235,23), black weight, 16px, 14px with a reduction, max 125px, shrink); `#tooltip-hotspot` (info_i.vsvg 16px,
    right bottom, brightness .5, hover 1).
- Hover (not a drop item): picture box #fafafa0c, image scale 1.03, blurred copy brightness 1.5, all .2s; sound
  `UIPanorama.inventory_item_rollover`.
- In `.store-home-section`: `ui-scale: 92%`.
- `ItemTileStore.Init(panel, data)`: images (a coupon shows its loot list's first item), name (`useTinyNames`: item_name
  + `_tinyname`), StatTrak / NEW / not-released labels, price (`StoreAPI.GetStoreItemPercentReduction`,
  `ItemInfo.GetStoreOriginalPrice / GetStoreSalePrice(id, 1)`; market item `#SFUI_Store_Market_Link`; drop item
  `#op_reward_free`), click, claimed state, tooltip.
- Click (`SetOnActivate`): market item -> Steam market search for its set; linked item -> context_menu_store_linked_items;
  decodable: coupon `ShowDecodePopup(id, loot item 0, isNew)`, volatile container popup_offers_laptop, one with a loot
  list `ShowDecodePopup(id, id, isNew)`, else `ShowInspectPopup`; anything else `ShowInspectPopup`
  (popup_inventory_inspect with `store_item_id`). `ShowDecodePopup` opens popup_capability_decodable with
  `store_item_id`, `force_hide_async_bar: true`, `show_work_type_warning: false`, `override_purchase_limit: isNew` (and
  `&overridepurchasemultiple=1` when new).
- Tooltip: hotspot mouseover after .1 s: tooltip_inventory_item (linked item `#store_linked_item_tooltip`; not released:
  its `linkedWarning`).

## Styles (mainmenu_store_fullscreen.vcss; store.vcss is an older sales banner, unused)

- `store-home-section-width` 1280px. `.store-home-container`: that wide, centred, `overflow: squish scroll`,
  margin-right 64px, padding-bottom 16px, padding-right 32px, flow down. `.store-dynamic-lister`: same width, flow
  right-wrap, opacity 0 / collapsed until `.Active` (opacity .25s ease-in-out).
- `.store-home-rewards-section`: 100% x 300px, rgba(0,0,0,.384), radius 5px, margin-top 12px; `-bg`: blur
  mipmapgaussian(4,4,2), `backgrounds/weekly_rewards_png`, cover, 50% 50%.
- `.store-home-section`: 100% x 300px, rgba(0,0,0,.384), radius 5px, margin-top 12px, box-shadow shadowOffset (fill
  #00000050 1px 1px 6px). `.store-home-popular__items`: flow right, vertically centred, right aligned, margin-right 16px,
  margin-top 8px. `.store-home-popular__info`: flow down, margin-left 32px, vertically centred; title 220px wide
  (fontSize-xxl 40px, Stratum2 Condensed). `.store-home-popular__btn`: right top, margin 8px 24px, ui-scale 50%; label
  22px normal, margin-right 6px; image rotateZ(-90deg).
- `.store-home-wallet`: right, margin-right 96px, Stratum2 medium 14px.
- Care package frame: rankup_redemption_store.vcss `.rrs-root` (100% wide, padding 16px 0), `.rrs-directions-panel`
  right aligned (min-height 270px, title max 420px), offers' container 900px; `.rrs-popup__frame` margin 20px; title
  60px Stratum2 Condensed, shrunk to 420px when longer.
- The care package's offers are itemtile_store panels (rankup_redemption_store.ts `_CreateItemPanel`: `isDropItem`,
  `noDropsEarned` for a '-' slot); `.rrs-item-container` / `.ghost-item` in its .vcss are leftovers no layout makes.

## Unread

- popup_capability_header / popup_inventory_inspect with `store_item_id` (purchase button, quantity stepper:
  `overridepurchasemultiple`; the header popup_capability_header draws on the container popup's store path),
  popup_store_status, context_menu_store_linked_items, mainmenu_store_tile_linked.
- xpshop.xml / xpshop_track (the Armory), popup_major_store.
