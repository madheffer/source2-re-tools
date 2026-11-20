# Loading screen

pak01 (2026-11-18): layout/loadingscreen.xml, layout/base_loadingscreen.xml, styles/loadingscreen.vcss,
scripts/loadingscreen.ts, csgostyles (ProgressBar), resource/csgo_english.txt. No binary.

## Layout (loadingscreen.xml)

- `base_loadingscreen.xml`: `.WindowRoot` holding `<CSGOLoadingScreen id="LoadingScreen">`.
- `.loading-root`:
  - `<CSGOBlurTarget id="BackgroundMapImageBlur" class="loading-screen-blur" blurrects="LoadingScreenContents">`
    (blurred only inside `#LoadingScreenContents`, `blur: mipmapgaussian(6, 6, 3)`): `#BackgroundMapImageDefault`
    (`images/map_icons/screenshots/1080p/default_psd.vtex`, stretch-to-cover), `#LoadingScreenSlideShow`.
  - `#LoadingScreenContents.loading-screen-contents`: `.loading-screen-content__info__bg` (blue dots),
    `#LoadingScreenContentsBottom` > `#LoadingScreenInfo.loading-screen-content__info` > `__info-container` > `__titles`
    holds the first three below; the rest follow in this order (the exact parent of each: not recorded):
    - `#LoadingScreenIcon.loading-screen__mapicon` (texture width 200)
    - `#LoadingScreenMapName.__info__text-title` (`.stratum-bold-condensed`)
    - `.__info__gamemode`: `#LoadingScreenGameModeIcon` (40 x 40 texture) + `#LoadingScreenGameMode`
      (`.stratum-regular-condensed`)
    - then `.__info-line` and `#LoadingScreenModeDesc` (`.stratum-regular`, html)
    - `#LoadingScreenHintContents` (info icon + `#LoadingScreenHintText`; `visibility: collapse`: never shown)
    - `.loading-screen-progress-container`: `#ProgressStatusText` ("#SFUI_LOADING" "Loading..."),
      `#LoadingSecondaryProgressContainer` (`#ProgressSecondaryStatusText` + `#ProgressBarSecondary`), `#ProgressBar`.
  - a full-size empty Panel and a `VanityCrossFadePanel` (the cross-fade from the main menu's vanity scene).
- Snippet `snippet-loadingscreen-slide`: Image `.loading-screen-slide` (stretch-to-cover) holding
  `#LoadingScreenTitle.loading-screen-screenshot-title` ("{s:screenshot-title}").

## Style (loadingscreen.vcss)

| Selector | Rules |
|---|---|
| @define | `maxBlur: 6.0; loadingScreenWidth: 1220px; info-margin: 20px 20px` |
| `.loading-root` | full size, `background-color: rgba(255,255,255,0.03)` |
| `.loading-screen-contents` | `margin-top: 50px; height: 100%; max-height: 1200px; width: 300px; margin-right: 20px; margin-bottom: 20px; horizontal-align: right; vertical-align: center; flow-children: down`; height / opacity .5 s; background written `background-color: rgba(0,0,0,0.5) opacity: 1;` (no semicolon between) |
| `.loading-screen-content__info__bg` | `bluedots_large_png` at `backgroundDotsSize` (360 x 360), `background-img-opacity: 0.03` |
| `.loading-screen-contents-bottom` | `height: fill-parent-flow(1); max-height: 920px` |
| `.loading-screen-content__info` | flow down, `margin-bottom: 24px`; `.hidden` opacity 0 + collapse (.25 s) |
| `__info-container` / `__titles` | flow down, margin 20 px / flow down, centred |
| `.loading-screen__mapicon` | `height: 150px`, `img-shadow: 0 0 6px 4.0 #000`, `visibility: collapse` until the script shows it |
| `__info__text-title` | white 40 px, `text-overflow: shrink`, nowrap, `margin-top: 10px` |
| `__info__gamemode` | flow right, `margin-top: 20px`, centred |
| `__modeicon` | 30 px wide, `margin-right: 8px` |
| `.loading-screen-content_text-gamemode` | 30 px white, shrink |
| `__info__text` | 16 px white, margin 20 px |
| `.loading-screen-content__info-line` | 2 px, white, opacity .3, margin 0 20 px |
| `.loading-screen-progress-container` | bottom, margin 20 px 20 px 0, flow down |
| `.loading-screen-progress-text` | 32 px tall, 22 px, `#CCCCCC` |
| `.loading-screen-progress-secondary-text` | Stratum2 16 px white, margin-bottom 5 |
| `.loading-root #ProgressBar` | 100 % x 8 px, `rgba(0,0,0,0.671)`, margin-bottom 16 px |
| `.ProgressBarLeft` | `gradient(linear, 0% 0%, 100% 0%, from(#134f87), to(#1ab8e0))` |
| `#ProgressBarSecondary` | 5 px, fill blueColor to `#006633` |
| `.loading-screen-slide` | full size, `transition: blur, opacity, background-color 0.1s`; `.show` opacity 1; `.hide` 0; `.show-first` opacity 1 + `slide-show-start` (0.2 s: opacity 0 / scale 1.1 to 1 / 1); `.show-blend-into-teamselect` (black gradient, `slide-show-end`) |
| `.loading-screen--closing` | 2.8 s, opacity 1 until 70 % then 0 |
| `.loading-screen-screenshot-title` | white 50 px, bottom left, margin 50 px |

Unused by the layout: `__overview--background` / `--map` (820 x 820 overhead map, collapsed), `.loading-screen-model*`
(720 px agent models left / right), `.loading-screen-fade--dark` / `--teams`.

## Script (loadingscreen.ts)

- `MAX_SLIDES = 10`, `SLIDE_DURATION = 4`.
- `_Init` (`UnloadLoadingScreenAndReinit`): bar 0, map name "", game mode "#SFUI_LOADING", description "", both icons
  hidden, slides deleted.
- `_UpdateLoadingScreenInfo(mapName, prettyMapName, prettyGameModeName, gameType, gameMode, descriptionText)`
  (`PopulateLoadingScreen`):
  1. `${d:mp_roundtime}` / `mp_fraglimit` / `mp_maxrounds` in the description replaced by the cvars.
  2. `#LoadingScreenIcon` = `file://{images}/map_icons/map_icon_<map>.svg` (`ImageFailedLoad` hides it and swaps the
     name's `...text-title-short` for `-long`; neither class has a rule); `#LoadingScreenMapName` = `prettyMapName`, else
     `GameStateAPI.GetMapDisplayNameToken(mapName)` localized.
  3. Only with `gameMode` (else the info block `.hidden`): `#LoadingScreenGameMode` = `prettyGameModeName`, else
     `#sfui_gamemode_<gameMode>`; `#LoadingScreenGameModeIcon` = `icons/ui/competitive_teams.svg` when
     `GameStateAPI.IsQueuedMatchmakingMode_Team()` or the map is `lobby_mapveto`, else `icons/ui/<gameMode>.svg`
     (hidden on failure); `#LoadingScreenModeDesc` = `descriptionText`.
  4. `_InitSlideShow`: for n in 0..9, `map_icons/screenshots/1080p/<map>[_<n>].png` when `$.BImageFileExists`; title
     `#loadingscreen_title_<map>[_<n>]` when the token exists. When all loaded or failed: `_StartSlideShow` picks a random
     slide, `show-first`; `_NextSlide` every 4 s: the next `show`, the one before `hide` 0.25 s later; one slide just
     shows. `JsOnMapLoadFinished` stops it.

## Strings (csgo_english.txt)

`SFUI_GameMode_casual` "Casual", `_competitive` "Competitive", `_scrimcomp2v2` "Wingman", `_deathmatch` "Deathmatch",
`_gungameProgressive` "Arms Race"; descriptions `SFUI_GameModeCasualDesc`, `SFUI_GameModeCompetitiveDesc`,
`SFUI_GameModeScrimComp2v2Desc`, `SFUI_GameModeDeathmatchDesc`, `SFUI_GameModeGungameProgressiveDesc`; `SFUI_Map_<map>`
(`SFUI_Map_de_fachwerk` "Fachwerk"); `SFUI_LOADING` "Loading...".

## Unread

- Whether panorama's parser keeps the contents panel's colour (the missing semicolon).
- `GetMapDisplayNameToken`'s fallback for a map without a token (client.dll).
