# CS2's main menu: the left column, the play menu, the rating tile

pak01 panorama (styles/*.vcss_c, scripts/*.vts_c, layouts), gamemodes.txt, resource/csgo_english.txt;
particles.dll (CS2 install 2026-11, PE timestamp 0x6af4a587), panoramauiclient.dll and panorama.dll (install 1112,
md5 df9d91c3 = panorama_installed_1112.dll). Mostly Valve's UI sources, not binaries.

## Functions

| Address | Module | What |
|---|---|---|
| 0x180137cc0 / 0x180137ce0 | particles | C_INIT_CreateOnGrid state (slot 11) / init (slot 34) |
| 0x18036ac00 | particles | CP's 3x4 matrix (local space) |
| 0x1801ce870 / 0x1801ce940 | particles | C_OP_RampScalarLinear init (6) / op (34) |
| 0x1801cc2e0 | particles | C_OP_LerpScalar op (34) |
| 0x180116210 | particles | C_OP_LocalAccelerationForce force (34) |
| 0x18035ec20 | particles | rotate by the CP |
| 0x1801fdd10 | particles | C_OP_RemapControlPointOrientationToRotation op (34) |
| 0x18035d030 -> 0x18035e4a0 | particles | MatrixAngles |
| 0x1801bf980 | particles | write a float into every particle (no clamp, no strength) |
| 0x1800f8b00 | panoramauiclient | builds CCarousel's attribute descriptors (static 0x180278b90, 0x20 apart) |
| 0x1800fa510 | panoramauiclient | attribute setter (vtable slot 0xd8) |
| 0x1800ff6f0 | panoramauiclient | parse autoscroll-delay "a, b" |
| 0x18016b390 | panoramauiclient | parse a duration |
| 0x1800f8500 | panoramauiclient | offset lists |
| 0x1800faca0 | panoramauiclient | schedule the next step |
| 0x1800f86a0 | panoramauiclient | registers the CarouselAutoScroll handler (event 0x18026c044) |
| 0x1800fb250 | panoramauiclient | CarouselAutoScroll handler |
| 0x1800fc670 | panoramauiclient | current child |
| 0x1800ff940 | panoramauiclient | set focus |
| 0x1800ffa90 | panoramauiclient | class pass (only sets classes) |
| 0x1800f9120 | panoramauiclient | class pass for one child + PreviouslyLeft / PreviouslyRight |
| 0x1800ff060 | panoramauiclient | the offsets' scaling (the placement slot after it unread) |
| 0x1800fb9b0 | panoramauiclient | serialises the attributes |
| 0x1801117a0 | panorama | CUIPanel slot 0x5f0: `return pseudoClasses(+0x220) & 1` (:hover) |
| 0x180105110 / 0x180105830 | panorama | slot 0x5d8 add / 0x5e0 remove a pseudo-class mask |
| 0x18013d1f0 | panorama | CUIWindowInput::ChangeHoverState (uiinput.cpp) |
| 180e695e0 | client | CCSGO_Particle3dPanel (kill-cards.md): which attribute / path makes the menu panel square (TODO) |

## Fields

| Offset | Field |
|---|---|
| CreateOnGrid +0x1e8 / +0x360 / +0x4d8 | X / Y / Z counts (float inputs, once; max(v, 1.0)) |
| CreateOnGrid +0x650 / +0x7c8 / +0x940 | X / Y / Z spacings |
| CreateOnGrid +0xab8 / +0xabc / +0xabd / +0xabe | CP (0..63) / m_bLocalSpace / m_bCenter / m_bHollow |
| RampScalarLinear +0x225 | m_bProportionalOp |
| LerpScalar +0x1e8 / +0x360 / +0x364 | m_flOutput (per particle) / start / end |
| LocalAccelerationForce +0x1f0 / +0x1f4 / +0x1f8 | m_nCP / m_nScaleCP / m_vecAccel |
| RemapCPOrientationToRotation +0x1e0 / +0x1e8 / +0x1ec | CP / m_flOffsetRot / m_nComponent |
| CCarousel +0x48 | focus: edge 0 / center 1 / 2 |
| CCarousel +0x4c | wrap |
| CCarousel +0x68 / +0x70 | x-offset list |
| CCarousel +0x11c | panels-visible |
| CCarousel +0x128 / +0x12c | autoscroll a / b |
| CCarousel +0x130 / +0x131 / +0x132 | sequence byte / pending / enabled |
| CCarousel +8 | its IUIPanel |
| CUIPanel +0x220 | pseudo-classes (bit 0 :hover) |

## Constants

| Value | What |
|---|---|
| 0x1804f3508 | C_INIT_CreateOnGrid vtable |
| 0x1805064f0 | C_OP_RampScalarLinear vtable |
| 0x180506fe0 | C_OP_LerpScalar vtable |
| 0x1804e9f40 | C_OP_LocalAccelerationForce vtable |
| 0x18050ce48 | C_OP_RemapControlPointOrientationToRotation vtable |
| 0.0174532924 / 57.2957764 | degrees <-> radians |
| 0x180201920 | CCarousel vtable |
| 0x180278d10 (+0x180) / +0x1a0 | autoscroll-delay / panels-visible descriptors |
| 0x180278b84 | class set when panels-visible <= d |
| 0x1804ccff8 | CUIPanel@panorama vtable |
| csgostyles colours | blueColor #3281AC, blueColorDark #0D354A, warningColor #b1af2d, negativeColor #DB4437, positiveColor #0F9D58, selectedNavColor #82D8FF, disabledColor rgb(130,130,130), baseText #cccccc, ct-color rgb(150,200,250), t-color #eabe54, blurBackgroundColor rgba(255,255,255,.01), contentPanelBackground rgba(20,20,20,0.4), shadowOffset `fill #00000050 1px 1px 6px 0` |

## The left column (layout/mainmenu_left_column.xml)

- `mainmenu.xml`: `<Frame id="JsLeftColumn" hittest="false" class="MainMenuModeOnly" src=".../mainmenu_left_column.vxml">`;
  mainmenu.ts gives it `.hidden` (opacity 0, .25 s) when a content panel opens, collapses it once transparent.
- `.mainmenu-left-column` holds six Frames in order: `id-mainmenu-license-panel` (mainmenu_license),
  `id-mainmenu-mini-store-panel` (mainmenu_mini_store), `id-mainmenu-major-tile-panel` (mainmenu_major_tile),
  `id-mainmenu-xpshop-tile-panel` (mainmenu_xpshop_tile), `id-mainmenu-rush-tile-panel` (mainmenu_rush_tile),
  `id-mainmenu-mission-panel` (mission_tile_mainmenu).
- `.mainmenu-left-column`: `padding: 64px 0 16px 16px; height: fit-children; vertical-align: bottom; width: 620px;
  flow-children: up` (mission tile on top, mini store at the bottom); `.mainmenu-left-column__thin { width: 256px }`.
  Each tile but the mission's has `margin-top: 8px`.
- Every tile hides (`.hidden`: opacity 0, height 0, margin-top 0, .25 s) with nothing to show (no GC, restricted
  licence, no items).
- styles/mainmenu_missions.vcss is an older panel the menu no longer loads (black header bar, greenyellow PLAY badge).
- The licence panel and the Major tile (a promo image, a description, a carousel of major store items): layouts only.

### Mission tile (mission_tile_mainmenu.xml, mission_tile.vcss, mission_tile.ts)

- `#id-mainmenu-mission-panel`: 256 x 180, `box-shadow: shadowOffset`.
- `.mission-root` > `#missionButton.mission-mainmenu`:
  - `.background-contents` (black; `transform` .1 s; hover `scale3d(1.05, 1.05, 1)`): `#missionArtBG.mission-art-bg`
    (opacity .5, `scale3d(1.05, 1.05, 1)`, `position: -4px 0 0`, animation `subtle-motion` position -6 px to 6 px, 8 s
    ease-in-out infinite alternate-reverse), `.mission-bg` (`backgrounds/mission_background_psd.vtex`, 50 % 50 %,
    `background-size: 200%`; hover `brightness: 1.2`), `#id-mission-bg-searching` (linemap.webm washed rgb(20,160,20),
    `scaleY(0)` until `.SEARCHING_FOR_MISSION`).
  - `.mission-main-content` (padding 4 px, flow down):
    - `.mission-header` (margin 4 px, bottom 10 px, 1 px `#ffffff40` bottom border, flow right): `.mission-title` 18 px
      Stratum2 Medium Condensed white "#weekly_mission_title" "MISSION"; `.mission-time-remaining` 12 px Stratum2
      lighter "Expires in <b>...</b>".
    - `.mission-location` > `.mission-mode-mapgroup` (22 px condensed, centred, max-height 24: "#mission_location"
      "<b>{s:gamemode}</b> on <b>{s:location}</b>").
    - `#missionMapicon` / `#missionModeicon` (28 px at y 70, x +-38 %, opacity .5, collapsed by default).
    - `.mission-main` > `.mission-directive` (32 px condensed light, margin-top 5, max-height 50: "#mission_directive:f"
      "<b>{d:mission-points}</b> {s:action_directive}", e.g. "5 KILLS").
    - `.mission-progress-container` (flow right, margin 0 6 px, centred): `#progressBaContainer`
      (segmented_progress_bar) and `.mission-xp-reward-container` (icons/mission-xp-reward.vsvg 50 x 25 washed
      rgb(19,135,168) under `.mission-xp-reward` 18 px Medium Condensed, 40 px wide, y 1.5 px: "{s:mission-xp} XP").
    - `.mission-additional-container` (100 % x 50 px; label 22 px Stratum2 Condensed, shrink to 18, max-height 46).
    - `.searching` ("Searching...", slow pulse while `.SEARCHING_FOR_MISSION`).
  - `.mission-complete` (46 px, bottom; instead of the button when `.COMPLETE`).
- `.DISABLED`: saturation .5, brightness .3, opacity .9.

### Armory tile (mainmenu_xpshop_tile.xml / .vcss / .ts)

- `.mainmenu-xpshop-tile`: 256 x 256, `box-shadow: #00000071 0 0 8px 0`, `margin-top: 8px`, `gradient(linear, 0% 0%,
  0% 100%, from(#317714), to(#14252e))` under `backgrounds/xpshop_background_png.vtex` (`background-size: 500% 250%`,
  0 0, `background-img-opacity: .5`).
- Children: ParticleScenePanel `.mainmenu-xpshop-particle` (particles/ui/xpshop/xpshop_panel_right_glow.vpcf, camera
  0 250 0, fov 40, `translatez(9px) scaleX(-1)`, washed rgb(169,240,169), z 1); `<Carousel
  id="id-mainmenu-xpshop-carousel" panels-visible="3" autoscroll-delay="5s">` (z 2); `.mini-store__carousel-blocker`
  (32 px at the bottom, z 1, `hittest="true" onactivate=""`) with `.mini-store-separator` (1 px white .1);
  `.mainmenu-xphop-tile__title-container` (z 3): `#id-new-item-tag`, `#id-xpshop-title` (Medium Condensed, margin
  12 px, white, uppercase: "#store_tab_xpshop" "Armory"); `#id-btn-open-xpshop.mainmenu-xpshop-tile__btn` (full, z 4:
  `MainMenuGoToStore 'id-store-nav-xpshop'`); `#id-upsell.mainmenu-xpshop-upsell` (bottom, padding 12 12 0 12, z 3,
  flow down: ItemImage 128 px tall x 130 %, `img-shadow: 2px 3px 12px 2 black`; `__label` Stratum2 italic bold 22 px
  xpshop-green `text-shadow: 0 0 6px 4 black` "The Armory Pass"; `.line-2` 14 px medium white; `.line-3` italic light
  white); `.mainmenu-xpshop-info-bar` (full, z 4): `#id-balance` (margin 12, right; "CREDITS BALANCE" 18 px Medium
  Condensed green over a 32 px white number and the 32 px xpshop_star washed green) and
  `#id-tracks-container.mainmenu-xpshop-bottom` (bottom, gradient to `rgba(0,0,0,0.781)`: "Pass Progress" 14 px medium
  green, 1 px green line at .2 opacity 90 % wide margin 4 0, `#id-tracks` margin-bottom 8).
- Carousel tiles (snippet `mainmenu-xpshop-itemtile`): 100 % wide, `transition: opacity, transform, blur .5s`;
  ItemImage 164 px tall, centred, margin-top 10, `img-shadow: 0 4px 12px rgba(0,0,0,.7)`; a set image (opacity .25);
  `.xpshop__item-tile__new-tag` (purple NEW! tab, `rotateZ(-90deg) translateX(-18px) translateY(45%)`) when `.new`.
  `.Focused`: opacity 1, z 3; `.LeftOfFocusN` / `.RightOfFocusN`: opacity 0, `translatex(-+140px) scale3d(1.1, 1.1, 1)`.
- `_SetUpTracks`: with a pass or progress, tracks and title show, upsell hides; with neither, upsell shows, tracks /
  balance / title hide. `_GetItemsForDisplay`: 12 random goods, the new first.

### Mini store (mainmenu_mini_store.xml, itemtile_store.xml, their .vcss)

- `.mini-store-container`: 256 px wide, `rgba(0,0,0,0.6)`, `box-shadow: hollow #00000071 0 0 8px 0`, `margin-top: 8px`.
  Children: `<Carousel id="id-mini-store-carousel" panels-visible="3" autoscroll-delay="20s">`, blocker and separator,
  `<CarouselNav class="mini-store__carousel-nav" incrementsound="inventory_new_item_scroll">` (bottom, margin-bottom 8,
  padding 0 6 px, z 2), `.mini-store__header` (margin 12 px, flow right: "#store_nav_popular" "NEW & POPULAR" Medium
  Condensed white, `#id-open-fullscreen-store-btn` "#store_nav_more" "See All..." margin 4 px, Stratum2 Light TF 12 px,
  white on hover: `MainMenuGoToStore ''`).
- mainmenu_mini_store.ts: 5 items of the store's coupon list (more when more are new releases), each a Button loading
  itemtile_store.xml with `isDisplayedInMainMenu` (`.is-mainmenu-item`).
- `.itemtile-store`: 160 x 270, margin 8, `gradient(linear, 0% 100%, 0% 0%, from(#3a39398f), to(rgba(4,123,4,0)))`,
  `transition: background-color, transform, opacity .2s`. `.is-mainmenu-item`: 275 px wide, margin 0, no shadow,
  container `flow-children: none`; `.itemtile-store__image-Container` margin 18 12 12 12, 170 px tall; main image
  100 % x 80 % of its width, centred; `__mainmenu-item-image-bg` (100 % x 60 %, `pre-transform-scale2d: 4, 3.76`,
  `translateY(-60px) translatex(-40px)`, margin-bottom 250, `blur: mipmapgaussian(2, 2, 2)`, brightness .5);
  `__item-image-bg` (scale 4, blurred, saturation .9, opacity .35); `__name` margin-left 12, margin-bottom 58, 14 px
  medium, rgb(194,194,194), additive, max-height 34; `__new` (`#D8760E`, right top, 14 px bold, padding 4, margin-top
  18); `.itemtile-store__bottomrow` (bottom, margin 0 8 8): `__price-container` 24 px tall (28 with a reduction):
  `__price-reduction` white 16 px medium on positiveColor, `__price-original` 12 px struck out, `__price-sale`
  rgb(23,235,23) black weight 16 px (14 with a reduction), max-width 125. `.Focused` opacity 1; `.LeftOfFocusN` /
  `.RightOfFocusN` opacity 0, `translatex(-+275px)`.
- carousel_nav.xml: `#ItemPips`, `#ItemCount` (collapsed), `#PreviousItemButton.PaginationArrow.Left`,
  `#NextItemButton.PaginationArrow.Right` (`CarouselNavIncrementSelectedIndex(-1 / 1)`). carousel_nav.vcss
  `.mini-store__carousel-nav #ItemPips`: centred, `.PaginationButton` 14 x 14, `rgba(0,0,0,0.418)`, margin 0 2 px,
  `:selected` `rgba(255,255,255,0.555)`; `#ItemPips` margin-right 5 px. csgostyles `.mini-store-container
  .PaginationArrow`: icons/ui/arrowhead.vsvg 12 x 12, margin-left 50 px, `rotateZ(-90deg)`; `.Right` margin-right 56,
  `rotateZ(90deg)`; `:disabled` washed black, opacity .5; `:enabled:hover` brightness 4.
- Carousel turn times (`autoscroll-delay`): mini store 20 s, Armory 5 s, Major tile 10 s.

### Rush tile (mainmenu_rush_tile.xml / .vcss)

- `.mainmenu-rush-tile`: 256 x 256, `#F4E6B2`, same shadow and margin. `.mainmenu-rush-tile__movie`: 100 % x 80 %,
  `file://{resources}/videos/rush_001_preview540.webm` (loose in game/csgo/panorama/videos), cover, `opacity-mask:
  masks/top-bottom-fade-5`. `.mainmenu-rush-tile__button` (full; `OpenPlayMenu` + `PlayMenu_SwitchGameModeTab 'rush'`):
  contents at the bottom, margin 12 0, flow down: "#SFUI_Play" "PLAY" Stratum2 Black 12 px black, letter-spacing 8;
  icons/ui/rush_horizontal.vsvg 240 px wide, margin 4 0 2 0 (hover `scale3d(.95, .95, 1)`, `contrast: -1`, .25 s);
  "#rush_mainmenu_tagline" "A new fast paced 3v3 mode" Stratum2 Black Italic 12 px black, letter-spacing 1.

## The play menu (mainmenu_play.vcss)

- Map tile `.map-selection-btn`: `width: 224px; height: width-percentage(117%)`, `box-shadow: rgba(0,0,0,0.15) 0 0 6px 0`;
  `:selected` `border: 4px solid rgba(255,255,255,0.849)`; `__gradient` `#000000b2`; `.map-selection-info__map-name`
  28 px, centred, bottom; `.map-selection-btn .rating-root` 32 px tall.
- Section header `.map-selection-list-section-header__text`: Stratum2 lighter 28 px white; under it a 1 px
  `rgba(255,255,255,0.1)` border; `__line`: 1 px, `gradient(linear, 0% 0%, 100% 0%, from(#ffffff77), to(rgba(255,255,255,0)))`.
- `.gamemode-setting-radiobutton`: padding 6 px 20 px, hover `rgba(255,255,255,0.05)`; label 16 px Stratum2 medium
  white; `.RadioBox` 16 x 16, 1 px white ring, selected `gradient(radial, 50% 50%, 0% 0%, 35% 35%, from(white),
  color-stop(.8, white), to(#ffffff00))`.
- `.map-selection-list-container`: `background-color: rgba(0,0,0,0.15)`.
- GO `.play-menu__playbtn`: min-width 300, margin 12 px 0, `box-shadow: 0 0 16px #00000041`, `border: 1px solid
  rgba(9,219,9,0.336)`, `background-color: rgba(9,49,9,0.651)`, label 32 px bold uppercase `rgb(85,228,20)`,
  letter-spacing 4 px, padding 8 px 0; `--stopsearch` red border `rgba(204,11,11,0.336)`, label negativeColor 24 px.
- News sub-tabs `.news-panel-navbar`: 48 px, `rgba(0,0,0,0.25)`; underline `gradient(linear, 0% 100%, 0% 99%,
  from(white), ...)` (1 px white at the bottom), margin-right 24 px.

## The top navbar (mainmenu.xml, mainmenu.vcss, mainmenu.vts)

- `#JsMainMenuTopNavBar.mainmenu-top-navbar` in a 64 px `.mainmenu-top-navbar-container`: `background-color:
  blurBackgroundColor` over `backgrounds/linemap_png.vtex` at `background-img-opacity: .05`.
- Left: `#MainMenuNavBarHome` (home.vsvg) and Watch / Overwatch / Settings / Quit icon buttons
  (`.mainmenu-top-navbar__radio-iconbtn`: 32 x 32, margin 0 8 px, hover `rgba(255,255,255,.10)` .15 s ease-in; icon
  22 px, selected `wash-color: selectedNavColor`).
- Centre `#MainMenuNavBarCenterContainer` (left to right): INVENTORY, a small separator, LOADOUT, PLAY (separators
  inside it, left and right), STORE, a small separator, NEWS (`#SFUI_MainMenu_News_Title_uppercase`).
  `.mainmenu-top-navbar__radio-btn`: padding 0 18 px, full height, background .25 s; label `.stratum-regular-condensed`
  28 px, letter-spacing 1 px, `translateY(3px)`, colour / text-shadow .15 s; selected `#82D8FF`. `--play`: 128 px
  wide, label 36 px. `__play_seperator`: 1 px x 40 % `rgba(255,255,255,.3)`, `--small` 30 %.
- `MainMenu.NavigateToTab` (mainmenu.vts 538): `ParticleControls.UpdateMainMenuTopBar(particles, tab)`; old tab gets
  `.mainmenu-content--hidden` (opacity 0, .25 s), new loses it; `_ShowContentPanel` removes
  `.mainmenu-content--offscreen` (`position: -100% 0 0`) with `--animate` (.25 s ease-in-out): slides in from the left
  while fading in. PLAY dispatches `OpenPlayMenu`.

### The navbar's squares (particles/ui/ui_mainmenu_nav_play_mg.vpcf, scripts/particle_controls.vts)

`#MainMenuNavigateParticles`: ParticleScenePanel 670 px wide x the bar's height, centred, `-s2-mix-blend-mode:
additive`, camera `0 470 0` looking at the origin, fov 100.

- `m_nMaxParticles 256`, `m_nInitialParticles 32`, `m_flPreSimulationTime 4`; `C_OP_MaintainEmitter` 96.
- Initializers: `C_INIT_CreateOnGrid` X 35, Z 3, spacing 32 / 32 (`m_bCenter` default true: centred on CP0; the
  playaction system writes `m_bCenter = false` explicitly, so the default is true); radius (field 3) 20;
  lifetime (field 1) RANDOM_BIASED 1..3 through REMAP 80..200 -> 0.5..2 (clamped: 0.5); `C_INIT_RandomSequence` 0..3;
  pitch (field 20) 85..90 with a sign flip; normal (21) 0 1 0; alpha (7) `C_INIT_DistanceToCPInit` from CP1 0..600 ->
  1..0.25, twice (the second `SCALE_INITIAL_VALUE`); alpha2 (16) RANDOM_BIASED 0.25..1; `C_INIT_VelocityRandom` local
  -100..100 on y; colour from CP16.
- Operators: `C_OP_RampScalarLinear` field 16 -2/s (end cap only); `C_OP_OscillateVector` rate -400..400 on x, frequency
  0.1 (end cap on); `C_OP_DistanceToTransform` alpha from CP1, input 100..200 -> output 1..0, `SCALE_INITIAL_VALUE`,
  component scale (X: CP1's change age through a curve 1 (0) / 1 (0.289) / 0.5 (0.406) / 0.5 (1), slopes 0, -1.2316,
  -0.7035, 0; Y 1; Z 4); `C_OP_SetFloat` lifetime = CP2.z remapped 0..1 -> 0.5..3 (`SCALE_INITIAL`); `C_OP_SetFloat`
  alpha x age curve (0,0) (0.199,1 slope 1.2494) (0.800,1 slope -1.2485) (1,0 slope -0.0774) (`SCALE_CURRENT`); `C_OP_Decay`.
- Renderer `C_OP_RenderSprites`: radius scale 0.75, `materials/particle/glow_square_01.vtex` (256 x 256, white, alpha a
  full square with a 1 px soft edge, no sprite sheet: the sequences change nothing), animation rate 0.75 fit lifetime, self-illum 1, additive,
  `ALIGN_TO_PARTICLE_NORMAL`, alpha scale 0.25, desaturation = CP2.z.
- Children: `ui_mainmenu_navbar_press.vpcf` (32 x 2 grid burst on a press, colour CP17 / literal 0 255 212, fading over
  0.25 s of CP1's change age), `ui_mainmenu_nav_play_mg_mask.vpcf` (6 black scan_lines.vtex ropes from x 600 to -600 at z -24).
- `UpdateMainMenuTopBar(panel, tab)`: no tab: CP1 (1,1,1) then 0, CP2 (96, 0, .75), CP16 (85, 212, 238), CP17 (0, 255,
  212); a tab: `CP1.x = (container width / 2 - (button x + button width / 2)) x 1120 / panel width` (set to x + 1 then x
  so it counts as a change), CP2 (label width / 2 + 20 px in units, .1, .25). mainmenu.vts 47 calls it with no tab at
  load; `InitMainMenuTopBar` (CP16 only) is called on the GO bar's panel.
- CS2's camera +x draws on screen left (looking down -y, z up).
- Pixels: CCSGO_Particle3dPanel's default (kill-cards.md) is a square view stretched over the panel (aspect 1,
  squarePixels 0), which would squeeze the 3 rows (96 units) into 6 px on 670 x 64; CS2's menu shows square cells
  (horizontal fov 100, 1120 units across 670 px as particle_controls.vts assumes). TODO: 180e695e0.

### The GO bar (mainmenu_play.xml #PlayMenuActionBar, particle_controls.vts UpdateActionBar)

- `#PlayMenuActionBar_Searching_particles` `.UIMenuPlayActionBar` (particle_controls.vcss): 640 px wide, the bar's
  height, right; camera 570 330 70 at 570 0 70, fov 120; `ui_mainmenu_playaction_active.vpcf` (children
  `ui_mainmenu_playaction_press`, `ui_mainmenu_playaction_active_clouds`).
- `StartSearch` (mainmenu_play.vts): `#StartMatchBtn` takes `.pressed`, `mainmenu_press_GO` plays, then
  `UpdateActionBar(panel, "StartMatchBtn")`: buttonWidth = `__bg` width + 2, height its height;
  `GetWorldExtendsFromCamFov(120, 0, 330, 0, ph, pw)` = { height: `tan(120 * .5) x 330` (Math.tan takes the degrees
  as radians), width: `pw / ph x height` }; `scalar = width x 2 / pw`; `row = floor(buttonHeight x scalar / 32)`;
  CP1 (`(buttonWidth / 2 - 20) x scalar + random`, 0, 70), CP2 (17, row, .25), CP5 (1, 20, 0), CP16 (15, 231, 15).
  `RmoveBtnEffects` (the cancel, `_ShowCancelSearchButton` when not searching or not the host): CP16 0, stopped.
- The play menu stays open through a search.
- GO (`.play-menu__playbtn`, mainmenu_play.vcss 1639): `__bg` is `videos/linemap.webm` (loose in
  game/csgo/panorama/videos, 1024 x 1024 VP8, no alpha) repeated from 20% 60% at its size, washed rgb(33,180,33),
  brightness 1.5, background-img-opacity .5; two 1 px `__bar`s (left, right) white .075 glowing
  `0 0 64px 5px rgba(6,141,6,.767)`, hover brightness 2 and 124 px; `.pressed` `rotateX(100deg)` and opacity 0 in its
  `perspective: 200px` from 0 0, .25 s. `#PartyCancelBtn` (`--stopsearch`): red border, bars `rgba(190,16,16,.24)` /
  `rgba(109,34,34,.767)` (hover `rgba(179,39,4,.637)`), bg washed rgb(180,33,33), label negativeColor 24 px, padding
  12 px, "CANCEL SEARCH" (SFUI_Lobby_Cancel_QueueMode_Search); `:disabled` translateY(64px) + opacity 0 (rises as it
  enables). TODO: wash-color on an opaque image.

### The particle functions (particles.dll; ~0x60 above the 63babcbf build)

| Class | What |
|---|---|
| C_INIT_CreateOnGrid | counts / spacings evaluated once, counts max(v, 1.0); m_bCenter offset `((n - 1) x .5) x spacing`; a persistent float cursor (state, starts 0): wrap x into y, y into z, z to 0; position = prev position = cell x spacing placed on the CP (local: the CP's 3x4); x += 1 |
| C_OP_RampScalarLinear | the window test skipped only for 0 / 0 / 1 / 1 and m_bProportionalOp; alpha / alpha 2 clamp 0..1; where life > 0, start = T[id + 11], end = T[id + 12] lerped into their windows: `v = clamp(v + (T[id] (max - min) + min) x strength x dt)` |
| C_OP_LerpScalar | `t = age / (life + FLT_EPSILON)`; skipped outside [start, end]; lerp from the initial value to m_flOutput, start == end a step; `x = (v - x) x strength + x` |
| C_OP_LocalAccelerationForce | m_vecAccel once; m_nCP >= 0: scaled per axis by m_nScaleCP's position, rotated by the CP; added to every particle, no strength |
| C_OP_RemapControlPointOrientationToRotation | MatrixAngles of the CP; `v = m_flOffsetRot - angle[m_nComponent] x 0.0174532924` into every particle |

MatrixAngles (0x18035e4a0): `xy = sqrtss(f.y^2 + f.x^2)`; xy > 0.001: pitch atan2(-f.z, xy), yaw atan2(f.y, f.x),
roll atan2(l.z, u.z); else yaw atan2(-l.x, l.y), roll 0; x 57.2957764.

## The play menu's layout (mainmenu_play.vxml / .vts / .vcss)

- `.mainmenu-content__container`: padding-top 64 px, `rgba(0,0,0,0.75)` over the blur and `bluedots_large_png` at
  `background-img-opacity: .01`, `backgroundDotsSize` 360 x 360, opacity / transform .25 s ease-in-out.
- Row 1 `.content-navbar__tabs.--noflow` (48 px, `rgba(0,0,0,.25)`, height .25 s), `#PlayTypeTopNav` centred:
  `Play-official` "#play_setting_online" (Matchmaking), `Play-listen` "#play_setting_offline" (Practice),
  `PlayWorkshop` (Workshop Maps), `#PlayCommunity` icon button (community_servers.vsvg, tooltip "Community Server
  Browser", `PlayMenu.OnPressServerBrowser`). `.workshop #id-navbar-tabs` collapses the mode row.
- Row 2 `#id-navbar-tabs.content-navbar__tabs--dark` (42 px, clear), `#GameModeSelectionRadios`: premier, competitive,
  scrimcomp2v2 (Wingman), rush | casual, deathmatch, gungameprogressive (Arms Race), retakes | JsDirectChallengeBtn
  (#DirectChallenge_btn "Private Matchmaking"); the `|` are `.mainmenu-top-navbar__play_seperator` panels.
- `.content-navbar__tabs__btn` (mainmenu.vcss 1245): margin 0 6 px, border-radius 3 px, clear 1 px border; label 16 px
  Stratum2 medium uppercase, padding 4 px 6 px; hover `rgba(255,255,255,.025)`; selected `background-color: #82d7ff1a`,
  label selectedNavColor; disabled `wash-color: disabledColor`; disabled + selected a white 1 px border. Unavailable
  modes disabled (`_SetGameModeRadioButtonAvailableTooltip`, `m_arrGameModeRadios[i].enabled = isAvailable && isEnabled`).
- `.play-maps-controls-contianer`: border-top `rgba(255,255,255,.11)`, margin-right 64 px; `.gamemode-settings-sidebar`
  (margin 5 % 0; play-settings-width 240 px) and `.map-selection-list-container` (`rgba(0,0,0,0.15)`, clipped).
- Side bar order: `#play-lobby-leader-panel` (a party member's view); `#PrimeStatusPanel` (padding 0 16, margin-bottom
  32; `.play-menu-prime` image 32 px + "#elevated_status_enabled" "Prime Enabled" 18 px bold italic uppercase,
  letter-spacing 1.5 px; without Prime `.play-menu-get-prime`: 150 px, blueColorDark, 1.5 px blueColor border, radius
  10, padding 12, linemap at .05, image 64 px, label 16 px bold, hover brightness 1.5 .25 s); the workshop search; the
  bot difficulty; the game mode flags' titles; `#id-play-menu-practicesettings-container` with "#practicesettings_title"
  "Options" (`.map-selection__quick-selection-set-title`: 18 px Stratum2 lighter, `rgba(212,212,212,0.671)`, 20 px in)
  and `#PermissionsSettings` (slider_toggle, "#permissions_open_party" "Open Party": public / private,
  `lobby_default_privacy_bits`); the practice toggles (listen servers only); the map presets.
- `slider_toggle.vcss` `.btn-toggle-slider--playmenu`: 240 px, 6 px 20 px, hover white .05; pill 42 x 20, radius 16,
  1.5 px `rgba(0,0,0,.363)` border, padding 2, `rgba(0,0,0,.363)`; selected `gradient(radial, 50% 60%, 0% 0%, 90% 70%,
  from(#22a527), color-stop(.7, #22a527), to(rgb(10,88,10)))`, border `#147717`; knob white, round, `translateX(50%)`
  when on; all .25 s ease-in-out.
- Tile lists: `_LazyCreateMapListPanel` makes one container a mode (`map-selection-list map-selection-list--inner
  hidden` + `--<server>-<mode>`), reused; `_ShowActiveMapSelectionTab` removes `hidden` from the mode's, adds it to the
  rest, the first show with `skip-transition`; `.map-selection-list` transitions opacity / transform .25 s ease-in-out,
  `.hidden` = opacity 0 + `translateY(500px)`; hidden at the end of its opacity transition -> `visible = false`.
- Sizes: `--official-casual` (and deathmatch, gungameprogressive, scrimcomp2v2, retakes) 90 % wide, flow right, tiles
  `fill-parent-flow(1)` x 90 %, margin 0 8 px, group icons a 340 px column of 125 px icons; `--official-competitive`
  flow right-wrap, 100 % from margin-left 6 %, margin 8 px top / bottom, tiles 10.5 % x 48 %, margin 8 px, icons 60 %;
  an unavailable list's tiles `opacity .5; brightness .3`.
- Action bar `#PlayMenuActionBar.play-menu-controls-actions-bar`: 96 px, contentPanelBackground, border-top white .1,
  padding-left 64 px; GO `#StartMatchBtn.play-menu__playbtn` at the right. `#id-playmenu-mission-panel`
  (mission_tile_playmenu.vxml / .vcss): 200 x 70, 1 px `rgba(118,150,255,0.521)` border, shadow `0 0 16px #00000041`,
  margin-right 40, left; mission_background_short_psd.vtex at 100 % 200 %, 0 30 %; "#mission_location" (22 px Stratum2
  condensed, centred) over the description (22 px condensed, shrinking to 18).

## The catalog (gamemodes.txt in pak01, csgo_english.txt)

- "mapgroups": each `mg_*` has `name`, `nameID` (#SFUI_Mapgroup_*), `icon_image_path`, `grouptype` ("active" for the
  Active Duty single-map groups mg_de_ancient / anubis / cache / dust2 / inferno / mirage / nuke; "reserves" for the
  casual groups; "hostage") and `maps` in display order:
  - mg_casualalpha: de_dust2, de_mirage, de_inferno, de_vertigo, de_cache ("Defusal Group Alpha")
  - mg_casualdelta: de_train, de_anubis, de_ancient_night, de_overpass, de_nuke ("Defusal Group Delta")
  - mg_casualcharlie: de_boulder, de_fachwerk, cs_shelter ("Community Map Group")
  - mg_hostage: cs_office, cs_italy ("Hostage Group"); mg_armsrace: ar_shoots, ar_shoots_night, ar_baggage,
    ar_pool_day ("Arms Race Group", `tooltipMaps` the same four); mg_deathmatch ("SFUI_Mapgroup_allclassic") a long
    classic list; mg_casualsigma (Alpha minus cache), mg_reserves, mg_active and the operation groups.
- Titles: `SFUI_Mapgroup_casualalpha` "Defusal Group Alpha", `_casualdelta` "Defusal Group Delta", `_casualcharlie`
  "Community Map Group", `_hostage` "Hostage Group", `_armsrace` "Arms Race Group".
- Which groups each mode's page lists comes from the GC at run time. Seen in CS2's menu 2026-11-16: Casual lists Alpha,
  Delta, Community, Hostage; sub-tabs PREMIER COMPETITIVE WINGMAN RUSH | CASUAL DEATHMATCH ARMS RACE RETAKES | PRIVATE
  MATCHMAKING. Deathmatch's and Arms Race's lists not seen (TODO).

## Map tiles (mainmenu_play.xml / .ts / .vcss; panoramauiclient.dll)

A tile is a Carousel of flat 720p screenshots, one per map of the group, cross-fading on a random timer, zoomed 1.2
when selected. Only survival / rush tiles use movies (`file://{resources}/videos/<map>_preview.webm`); pak01 holds none
(panorama/videos/ has test gifs only).

- Snippet `MapGroupSelection` (RadioButton for casual / deathmatch / ..., ToggleButton for official competitive /
  wingman: `_GetPanelTypeForMapGroupTile`): `.map-selection-btn` holding, in order, `<Carousel
  id="MapGroupImagesCarousel" autoscroll-delay="2s, 5s" panels-visible="3" class="map-selection-btn__carousel
  full-width full-height">`, `.map-selection-btn__gradient`, `#MapGroupBetaTag`, `#MapSelectionTopRowIcons`
  (`#ActiveGroupIcon` icons/ui/competitive.vsvg 24 x 24), `#MapGroupNewTag`, `#MapGroupMutators`, `#MapSelectionButton`
  (`#MapGroupCollectionMultiIcons`, the rating emblem frame, the wins row, `.map-selection-info` with
  `#MapGroupWaitTime` and `#MapGroupName.map-selection-info__map-name.stratum-regular-condensed`).
- `_UpdateOrCreateMapGroupTile(mg)`: `MapGroupName` = `$.Localize(mg.nameID)` (e.g. `#SFUI_Mapgroup_casualalpha`);
  `ActiveGroupIcon` visible when
  `mg.grouptype === 'active'` (mg_de_ancient, mg_de_ancient_night, mg_de_anubis, mg_de_cache, mg_de_dust2,
  mg_de_inferno, mg_de_mirage, mg_de_nuke, mg_de_shortnuke, mg_active, ...; overpass / train / vertigo "reserves").
- `UpdateIconsAndScreenshots(p, numTiles, mg)`: fewer than 2 maps: one Image `#MapGroupCollectionIcon`
  (`file://{images}/<mg.icon_image_path>.svg`, e.g. map_icons/map_icon_de_dust2, texture 200,
  `map-selection-btn__map-icon`); then per map `MapSelectionScreenshot<i>` (`.map-selection-btn__screenshot`) with
  `background-image: url("file://{images}/map_icons/screenshots/720p/<map>.png")`, `background-position: 50% 0%`,
  `background-size: auto 100%`; 2+ maps: an Image `MapIcon<i>` per map in `#MapGroupCollectionMultiIcons`
  (`map_icons/map_icon_<map>.svg`, default `map_icon_NONE.png`, texture 200, `IconUtil.SetupFallbackMapIcon`),
  `top-bottom-flow-wrap` with more than one tile (one alone `left-right-flow-wrap`). random_classic: icons/ui/random_map.svg,
  screenshots/360p/random.png.
- vcss: `.map-selection-btn` border 0 -> `:selected` 4 px solid rgba(255,255,255,0.849), transitions .25 s ease-in-out;
  `__screenshot` 100% x 100%, `transition: opacity 2s, pre-transform-scale2d .25s ease-in-out`; hover
  `pre-transform-scale2d: 1.02` + `sound: "UIPanorama.submenu_contents_rollover"`; selected 1.2; `.Focused` opacity 1,
  `.LeftOfFocusN` opacity 1, `.RightOfFocusN` opacity 0 (2 s ease-in-out); `__gradient` #000000b2 over it all;
  `__map-icon` centred, square, margin 10 px, `img-shadow: 0px 0px 10px 3.0 #000000`; casual / deathmatch / ... icons
  column 340 px flowing down, icons 125 x 125 margin 0; official-competitive / listen-* icon 60% wide, square; the name
  28 px (90% wide, 36 px tall, margin-bottom 6, centred, ellipsis), `RadioButton.map-selection-btn Label` 32 px and
  margin-bottom 24, official-competitive / listen-* 24 px / 28 px tall / margin-bottom 4; `Label` colour baseText;
  stratum-regular-condensed = Stratum2 Condensed, weight normal.
- Disabled list / a client in someone's lobby: `opacity .5; brightness .3` (selected: 5 px rgb(148,147,147) border).
- Tooltip: `onmouseover` -> `OnMouseOverMapTile(id, mg.tooltipID, maps)` only with a tooltipID: `$.Localize(tooltipID)`,
  for several maps `<br><br>` and their `#SFUI_Map_<map>` names joined ", ", via `UiToolkitAPI.ShowTextTooltip`
  (tooltip_base / tooltip_text: #252b30, padding 16, 2 px black border, shadow #00000066 0 0 8px, label 18 px white,
  80..350 px; no pak01 override; arrows tooltip_arrow_*.vtex in core's pak01).
- `_SetMapGroupModifierLabelElements`: `#MapGroupNewTag` ("NEW!", SFUI_Workshop_New_Map) when `showtagui` is "new"
  (none today: the only one is commented out); `.map-selection-info__new`: 2 px 8 px 2 px 10 px, `new-item-gradient`
  (rgb(85,150,224) to blueColor, left to right), white medium italic 14 px, shadowOffset, bottom right corner 6 px.
- Data the GC supplies: mutators, wait time (LobbyAPI.GetMapWaitTimeInSeconds), rating emblem and wins row (per-map
  Competitive skill groups).

### CCarousel (vtable 0x180201920)

- Attribute descriptors 0x20 apart: wrap, focus, focus-offset, title, x-offset, ... autoscroll-delay +0x180,
  panels-visible +0x1a0.
- Setter 0x1800fa510: `panels-visible` = atoi -> +0x11c; `autoscroll-delay` -> 0x1800ff6f0; `wrap` true/false ->
  +0x4c; `focus` edge / center -> +0x48 (0 / 2 / 1); offset lists -> 0x1800f8500.
- 0x1800ff6f0: "a, b" (one or two durations): +0x128 = a, +0x12c = b (0 when absent); a change reschedules.
- 0x1800faca0: when not pending, enabled, a or b > 0 and 2+ children: `delay = max(a, 0) + 0 + RandomFloat(0, b)` (only
  when b > 0; 1800fad1b..1800fad3f: maxss, addss 0, addss); a CarouselAutoScroll event with the sequence byte (incremented).
- 0x1800fb250: when the byte matches, clears pending; unless vslot 0x5f0 (:hover) focuses the first child after the
  current (index mod count, -1 -> 0) whose vslot 0x638 (visible) is true; reschedules.
- 0x1800ffa90: each child `LeftOfFocus<d>` / `RightOfFocus<d>` / `Focused` by distance d, `DistanceFromFocus<d>` (wrap
  only: min(d, n - d)), and 0x180278b84's class when panels-visible <= d.
- So `autoscroll-delay="2s, 5s"`: each tile steps every 2 + U(0, 5) s, independently, wrapping, never while hovered.
  `panels-visible="3"` marks children 3+ away (no rule in mainmenu_play.vcss uses it). 0x1800fb9b0 only serialises
  the attributes. The tile sets no `x-offset` / `focus-offset`; the shots must share the tile's box (inferred: the
  child placement is unread; the CSS only animates opacity and puts `Focused` at translatex(0), and any shot placed
  beside the first would sit outside the clipped tile, where CS2's cycling could not be seen).
- Hover: ChangeHoverState walks up from the new target to the first ancestor whose 0x5f0 is set, removing mask 1 along
  the old chain, adding it along the new: bit 0 is :hover, on the hit panel and its ancestors. The carousel holds only
  under the pointer over it or its screenshots; over the icons, name or top-row icon (siblings on top; only the
  gradient, #MapGroupMutators and #MapSelectionButton are hittest="false") it keeps going.

## The matchmaking status (matchmaking_status.vxml / .vcss / .vts)

- `.matchmaking-status-container`: 384 px wide on `gradient(linear, 100% 0%, 0% 0%, from(#00000000), color-stop(0.5,
  rgba(0,0,0,0.5)), color-stop(0.6, rgba(0,0,0,0.5)), color-stop(0.9, rgba(0,0,0,0.35)), to(transparent))` (the panel
  sits at the left); `-wait` min-height 64 px, margin-left 24 px; `-left` 64 x 64; `-time` white 16 px, centred, 64 px
  wide, class `stratum-bold-mono` (Stratum2 Bold Monodigit: .mono-spaced-font-bold), default "00:00"; `-header` 16 px
  medium Stratum2, no text-transform, min-width 50, max-width 256; `.hidden` opacity 0 + scaleY(0) over 0.25 s ease-in-out.
- vts: time = `FormatText.SecondsToDDHHMMSSWithSymbolSeperator(LobbyAPI.GetTimeSpentMatchmaking())`, every 1.0 s;
  label `$.Localize(LobbyAPI.GetMatchmakingStatusString())`, e.g. SFUI_QMM_State_find_searching "Searching for players
  and servers..."; a non-host party member with no search sees MatchStatusWait with `#party_waiting_lobby_leader`
  "Waiting for lobby leader...". No estimated wait.

## The rating tile (rating_emblem.vcss / .vts)

- `.rating-root`: 26 px tall, `width: height-percentage(250%)`; on a player card / match stakes / map tile 32 px.
- Tier colours `color-csrating-tier-0..6`: `#b0c3d9 #8cc6ff #6a7dff #c166ff #f03cff #eb4b4b #ffd700`; background
  (`rating__bg`, icons/ui/premier_rating_bg.vsvg: a 178 x 64 slanted bar of greys with two white stripes
  `M12 0H21L9 64H0Z`, `M25 0H34L22 64H13Z`) and labels `wash-color`ed in the tier colour; value Stratum2 Black Italic,
  `brightness: 1.7`, `text-shadow: 1px 1px 1px 0 #000`; major 18 px / minor 14 px (card: 23 / 18). No rating:
  premier_rating_bg_none.vsvg, `#cs_rating_none`.
- `GetClampedRating(rating) = clamp(floor(rating / 1000 / 5), 0, 6)`.
- `SplitRating(rating)`: `strRating = (rating / 1000).toFixed(3).padStart(6, '0')`; `major = strRating.slice(0, 2)`,
  `minor = strRating.slice(-3)`; major's leading `00` -> two spaces, a leading `0` -> one; major all spaces: minor's
  leading zeros the same way, else minor gets a `,` in front. 25519 -> "25" ",519"; 742 -> "  " "742".
  (matchType '2' at exactly 5000 / 10000 / ... / 30000, '1' one below: the rank-up / down effect.)

## Lobby pieces (CS2 has no custom lobby screen; its private lobbies are Steam's)

- teamselectmenu.vcss: `#BtnSelectTeam-CT` `gradient(linear, 0% 0%, 0% 30%, from(rgba(37,75,105,1)),
  to(rgba(37,75,105,0)))`, `#BtnSelectTeam-TERRORIST` the same with `rgba(92,74,33)` (hover: to 40%);
  `.team-select-teammate` 200 px, margin 4 px, opacity 0.8, `box-shadow: #0000005e 0 0 6px 0`, background ct-color /
  t-color, a bot's `#303030`; name label black, 17 px, letter-spacing .35 px; `.team-select-list__title` Stratum2 Bold
  Condensed 50 px uppercase.
- chat.vcss (main menu party chat): `.chat-panel` 400 px; `.chat-panel-blur` `rgba(0,0,0,0.55)`; `.chat-entry Label`
  white 12 px, `text-shadow: 1px 1px rgba(0,0,0,0.8)`, padding 0 8 px; `.chat-container__input` 16 px 'Stratum2 TF' on
  `rgba(0,0,0,0.7)`, placeholder `rgb(184,181,181)` at .5; error lines `#c21b1b50`, green `#4caf4f50`, yellow `#b1af2d50`.
- party.vcss: `.party-status__text` 22 px Stratum2 medium, `text-shadow: 2px 2px 2px #000`; ongoing match bar
  blurBackgroundColor, icon warningColor; `.party-ongoingmatch-abandon` `#d4151fda`.
- The friend lobby's in-scene card sits at the knees (24 units over the feet; read off CS2's screen, its style is not in
  friendlobby.vcss).

## Unread

- mission_tile.ts's body (how fields are filled, the click), segmented_progress_bar (.vts, style), where
  `.mission-time-remaining` sits in the header's row.
- itemtile_store.ts beyond its class switches (tooltip hotspot, click popups); CCarouselNav (panoramauiclient.dll).
- CCarousel's child placement (the slot after 0x1800ff060; x-offset list +0x68 / +0x70 read with 8-bit displacements).
- Panorama's `img-shadow` strength (3.0); mipmap blurs.
- particles.dll's C_OP_OscillateVector; the press / mask children; the GO bar's particles.
- friendlobby.vcss, popups/popup_custom*.vcss, the other vxml layouts.
