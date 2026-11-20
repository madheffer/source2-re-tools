# The Store (the main menu's STORE page)

What CS2's store page is built from, read from pak01's panorama files (UI sources: no DLL was read), and which parts
of ours are CS2's and which are the owner's. Code: web/src/cs2web/client/home/store/ (store-view, store-tile,
store-api, store.css), web/server/cs2web/econ/store.js + store-routes.js (migration 017_store.sql, store-test.mjs).
Read with `lasers-bake --decompile <pak01> "panorama/(layout|scripts|styles)/(mainmenu_store_fullscreen|store\.|storeitem|itemtile_store|common/store_items|mainmenu_store_tile_linked|popups/popup_store_status|context_menus/context_menu_store_linked)" <scratch>`
(CS2 build of 2026-11).

## The page (layout/mainmenu_store_fullscreen.vxml, scripts/mainmenu_store_fullscreen.vts)

- Root: `.mainmenu-content__container` > `#id-mainmenu-store` (flow down): the tab row `#id-mainmenu-store-tabs`
  (`.content-navbar__tabs content-navbar__tabs--noflow`) then `#id-store-pages`.
- The tab row: RadioButton `#id-store-nav-home` (`#store_nav_home`, group store-top-nav, `.content-navbar__tabs__btn`),
  then `#id-store-lister-tabs`, filled by `MakeTabsBtnsFromStoreData`: one radio per key of `StoreItems.GetStoreItems()`
  that has items (`#store_nav_<key>`; tournament: `#store_nav_tournament_<eventid>`), then always `id-store-nav-xpshop`
  (`#store_tab_xpshop`, "Armory", with a `content-navbar__tabs__btn-new` count when the XP shop has new goods). At the
  right `#id-store-nav-wallet` (`#Store_Wallet_Balance_dv`, StoreAPI.OpenAccountWalletAddFundsURL): hidden unless the
  launcher is Perfect World (`AccountWalletUpdated`).
- `NavigateToTab(panelId, keyType)`: the home page refills its two sections (`UpdateItemsInHomeSection('coupon',
  'id-store-popular-items', 6)` and `('tournament', 'id-store-tournament-items', 1)`); another tab is made on first
  use (`MakePageFromStoreData`): xpshop loads layout/xpshop.xml, any other key a `JSDelayLoadList.store-dynamic-lister`
  (itemwidth 178px, itemheight 280px, spacersize 4px, spacerperiod 4px) whose cells are itemtile_store panels. The
  shown page has class `Active`.
- The home page `#id-store-page-home` > `.store-home-container`:
  - `#id-rewards-background.store-home-rewards-section`: a CSGOBlurTarget `.store-home-rewards-section-bg` and a Frame
    `.rrs-popup__frame` of layout/rankup_redemption_store.vxml (the Weekly Care Package: docs/game/pets.md). Hidden
    (`.hidden`) without Prime.
  - `#id-prime-background.store-home-prime-section`: the Prime upsell (logo, title, the buy button, three columns over
    de_inferno / de_ancient / de_anubis screenshots). Shown only without Prime (`ShowPrimePanelOnHomePage`).
  - `#id-store-home-section-coupon.store-home-section`: `.store-home-popular__info` with the title
    (`#store_nav_popular`, `.store-home-section__title stratum-regular-condensed fontSize-xxl`), the tiles
    `#id-store-popular-items.store-home-popular__items`, the button `.store-home-popular__btn` (`#store_nav_more`
    + expand.vsvg: `GotoStorePage('id-store-nav-coupon')`). Its background image is set by script:
    `images/backgrounds/store_home_coupon.psd`, position 50% 50%, size cover (suffix `_nightmode2` while the first
    coupon is a new release with id 17293822569102711679).
  - `#id-store-home-section-tournament.store-home-section`: the same for the active tournament, plus the
    TournamentStickers snippet (five random team stickers, rotated; opens popup_major_hub). Hidden with no items and
    no active tournament.
- `ReadyForDisplay`: needs the GC (`ConnectedToGcCheck`: else `#SFUI_SteamConnectionErrorTitle`); rebuilds the item
  list when empty; `PanoramaComponent_Store_PriceSheetChanged` runs it again.

## The items (scripts/common/store_items.vts)

- `MakeStoreItemList`: for each of `StoreAPI.GetBannerEntryCount()` banner entries (the GC's list), the def index ->
  a faux item id, sorted into: `key` (a tool whose first capability is decodable; not on Perfect World), `market`
  (`IsBannerEntryMarketLink`), `coupon` (the entry's custom format string starts "coupon"; "coupon_new" marks
  `isNewRelease`, and with no linked coupon `activationType 'newstore'`; `GetBannerEntryLinkedCoupon` gives `linkedid`),
  else `store`. `AllowDisplayingItemInStore` drops decodables whose restriction is "restricted" or "xray"
  (crate_stattrak_swap_tool always passes). `tournament` comes from `g_ActiveTournamentStoreLayout`
  (generated/items_event_current_generated_store), `prime` stays empty here.
- So the tabs CS2 shows (General = store, Market, Tools = key, the screenshot's "Armory") and what is in New & Popular
  are the Game Coordinator's banner list and Steam's price sheet: nothing of it is in a CS2 file.

## The tile (layout/itemtile_store.vxml, scripts/itemtile_store.vts, styles/itemtile_store.vcss)

- `.itemtile-store` 160 x 270, margin 8, `gradient(linear, 0% 100%, 0% 0%, from(#3a39398f), to(rgba(4,123,4,0)))`,
  shadow rgba(0,0,0,.4) 1px 1px 6px; `.itemtile-store__container` flow down: `.itemtile-store__image-Container` 170px
  (the main ItemImage 100% wide, height 80% of the width, centred; `__item-image-bg` the same image
  pre-transform-scale2d 4, blur mipmapgaussian(2,2,2), saturation .9, opacity .35; the labels `__stattrak`
  (rgb(172,146,0), 12px bold), `__new` (#D8760E, right top, 14px, padding 4px), `__not-released` (blueColor)), then
  `__name` (margin 8px left / top, 14px medium, max-height 34px, ellipsis), then `.itemtile-store__bottomrow` (bottom,
  margin 0 8px 8px): `__price-container` 24px (28px `.has-reduction`): `__price-reduction-container` (positiveColor,
  the "-N%" label 16px medium, padding 0 4px), `__price-labels` (flow down, padding 0 6px 0 4px): `__price-original`
  (12px, line-through, translateY 2px; shown with a reduction) and `__price-sale` (rgb(23,235,23), black weight, 16px,
  14px with a reduction, max 125px, shrink); `#tooltip-hotspot` (info_i.vsvg 16px, right bottom, brightness .5, hover 1).
- Hover (not a drop item): the picture box #fafafa0c, the image scale 1.03, the blurred copy brightness 1.5, all .2s;
  the sound `UIPanorama.inventory_item_rollover`.
- In `.store-home-section` the tile is `ui-scale: 92%`.
- `ItemTileStore.Init(panel, data)`: images (a coupon shows its loot list's first item), name (`useTinyNames`: the
  item_name + `_tinyname`), StatTrak / NEW / not-released labels, price (`StoreAPI.GetStoreItemPercentReduction`,
  `ItemInfo.GetStoreOriginalPrice / GetStoreSalePrice(id, 1)`; a market item: `#SFUI_Store_Market_Link`; a drop item:
  `#op_reward_free`), the click, the claimed state, the tooltip.
- The click (`SetOnActivate`): a market item opens the Steam market search for its set; a linked item a context menu
  (context_menu_store_linked_items); a decodable: a coupon `ShowDecodePopup(id, loot item 0, isNew)`, a volatile
  container popup_offers_laptop, one with a loot list `ShowDecodePopup(id, id, isNew)`, else `ShowInspectPopup`;
  anything else `ShowInspectPopup` (popup_inventory_inspect with `store_item_id`). `ShowDecodePopup` opens
  popup_capability_decodable with `store_item_id`, `force_hide_async_bar: true`, `show_work_type_warning: false`,
  `override_purchase_limit: isNew` (and `&overridepurchasemultiple=1` when new).
- The tooltip: the hotspot's mouseover after .1 s: tooltip_inventory_item for the item (a linked item:
  `#store_linked_item_tooltip`; a not released one its `linkedWarning`).

## The styles (styles/mainmenu_store_fullscreen.vcss; store.vcss is an older sales banner, unused by this layout)

- `store-home-section-width` 1280px. `.store-home-container`: that wide, centred, `overflow: squish scroll`,
  margin-right 64px, padding-bottom 16px, padding-right 32px, flow down. `.store-dynamic-lister`: the same width,
  flow right-wrap, opacity 0 / collapsed until `.Active` (opacity .25s ease-in-out).
- `.store-home-rewards-section`: 100% x 300px, rgba(0,0,0,.384), radius 5px, margin-top 12px; its `-bg`: blur
  mipmapgaussian(4,4,2), `backgrounds/weekly_rewards_png`, cover, 50% 50%.
- `.store-home-section`: 100% x 300px, rgba(0,0,0,.384), radius 5px, margin-top 12px, box-shadow shadowOffset (fill
  #00000050 1px 1px 6px). `.store-home-popular__items`: flow right, vertically centred, right aligned, margin-right
  16px, margin-top 8px. `.store-home-popular__info`: flow down, margin-left 32px, vertically centred; the title 220px
  wide (fontSize-xxl 40px, Stratum2 Condensed). `.store-home-popular__btn`: right top, margin 8px 24px, ui-scale 50%;
  its label 22px normal, margin-right 6px; its image rotateZ(-90deg).
- `.store-home-wallet`: right, margin-right 96px, Stratum2 medium 14px.
- The care package's frame in the section: rankup_redemption_store.vcss `.rrs-root` (100% wide, padding 16px 0),
  `.rrs-directions-panel` right aligned (min-height 270px, the title max 420px), the offers' container 900px.

## Ours (the owner's shelves, 2026-11-18)

Not CS2's, in CS2's section and tile styles:

- **Tabs**: Home, Cases, Stickers, Tools (CS2's are the GC's categories). No Prime upsell, tournament section, market
  links, key tab, wallet line or Armory.
- **Shelves** (server/cs2web/econ/store.js, table econ_store_offers): Daily Special (one case a day, 00:00 UTC),
  Weekly Rotation (store_weekly_count cases, the XP week: Wednesday 01:00 UTC; its own draw, not the drop rotation),
  Always Available (the cases flagged `common`: seeded as the week's drop pool cases, drop-pool.json), Sticker
  Capsules (the baked capsules), Tools (the Storage Unit, items_game 1201 `casket`: listed only). New & Popular: the
  offers with a `popular` place, then the newest of the catalogue, six.
- **The draw**: `drawShelf(defs, n, period, salt)`: the defs sorted, a mulberry32 generator seeded by an xmur3 hash of
  "salt:period", n picks without replacement. The week's shelf is the first store_weekly_count of the week's order;
  the day's case the first of the day's order that is not on the week's shelf. An admin's row in econ_store_picks
  (shelf, period) replaces a draw.
- **Prices**: econ_store_offers.price in the currency's minor units, null until the owner sets them (the tile then
  shows no price); store_daily_percent_off cuts the daily special's price and shows CS2's reduction row. The currency
  is USD (the owner's, with Stripe).
- **The care package's offers** are itemtile_store panels in CS2 (rankup_redemption_store.ts `_CreateItemPanel`:
  `isDropItem`, `noDropsEarned` for a '-' slot; `.rrs-item-container` / `.ghost-item` in its .vcss are leftovers no
  layout makes): ours too, in the popup and the banner (pets/care-package.js, store/itemtile-store.css). The frame is
  `.rrs-popup__frame` (margin 20px) in both; the title 60px Stratum2 Condensed, shrunk to 420px when longer.
- **Not built**: buying (real money through Stripe in USD: parked by the owner until Steam sign-ins are linked to real
  accounts; `purchases: false`), the Storage Unit's use,
  a sticker scraper item (left out by the owner: scraping stays free, as CS2's), the admin panel's Store page (the
  tables are edited by hand; `store.reload()`), the tile's tooltip and rollover sound, the tab sound
  (`UIPanorama.tab_mainmenu_shop`), the header popup_capability_header draws on the store path of the container popup.

## Still to read

- popup_capability_header / popup_inventory_inspect with `store_item_id` (the purchase button, the quantity stepper:
  `overridepurchasemultiple`), popup_store_status, context_menu_store_linked_items, mainmenu_store_tile_linked.
- xpshop.xml / xpshop_track (the Armory), popup_major_store.
- The images this page uses are copied by hand from a decompile (BAKING.md "the store's images").
