# CS2's loading screen

Read 2026-11-18 from CS2's pak01 with `lasers-bake --settings-ref <scratch> --match loading,...` (layout/loadingscreen.xml,
layout/base_loadingscreen.xml, styles/loadingscreen.vcss, scripts/loadingscreen.ts; csgostyles for ProgressBar). Nothing
here is from a binary: these are Valve's own UI sources. Used by web/src/cs2web/client/home/loading.js, loading.css and
loading-info.js.

## Layout (layout/loadingscreen.xml)

- `base_loadingscreen.xml`: a `.WindowRoot` holding `<CSGOLoadingScreen id="LoadingScreen">`.
- `.loading-root`:
  - `<CSGOBlurTarget id="BackgroundMapImageBlur" class="loading-screen-blur" blurrects="LoadingScreenContents">`: the
    picture, blurred only inside the rect of `#LoadingScreenContents` (`blur: mipmapgaussian(6, 6, 3)`). Children:
    `#BackgroundMapImageDefault` (`images/map_icons/screenshots/1080p/default_psd.vtex`, stretch-to-cover) and
    `#LoadingScreenSlideShow`.
  - `#LoadingScreenContents.loading-screen-contents`: `.loading-screen-content__info__bg` (the blue dots),
    `#LoadingScreenContentsBottom` > `#LoadingScreenInfo.loading-screen-content__info` > `__info-container` > `__titles`:
    `#LoadingScreenIcon.loading-screen__mapicon` (texture width 200), `#LoadingScreenMapName.__info__text-title`
    (`.stratum-bold-condensed`), `.__info__gamemode`: `#LoadingScreenGameModeIcon` (40 x 40 texture) +
    `#LoadingScreenGameMode` (`.stratum-regular-condensed`); then `.__info-line` and `#LoadingScreenModeDesc`
    (`.stratum-regular`, html); `#LoadingScreenHintContents` (an info icon + `#LoadingScreenHintText`, `visibility:
    collapse` in the vcss: never shown); `.loading-screen-progress-container`: `#ProgressStatusText` ("#SFUI_LOADING"
    "Loading..."), `#LoadingSecondaryProgressContainer` (`#ProgressSecondaryStatusText` + `#ProgressBarSecondary`),
    `#ProgressBar`.
  - a full-size empty Panel and a `VanityCrossFadePanel` (the cross-fade from the main menu's vanity scene; not drawn by us).
- Snippet `snippet-loadingscreen-slide`: an Image `.loading-screen-slide` (stretch-to-cover) holding
  `#LoadingScreenTitle.loading-screen-screenshot-title` ("{s:screenshot-title}").

## Style (styles/loadingscreen.vcss)

- `@define maxBlur: 6.0; loadingScreenWidth: 1220px; info-margin: 20px 20px`.
- `.loading-root`: full size, `background-color: rgba(255,255,255,0.03)`.
- `.loading-screen-contents`: `margin-top: 50px; height: 100%; max-height: 1200px; width: 300px; margin-right: 20px;
  margin-bottom: 20px; horizontal-align: right; vertical-align: center; flow-children: down`, height / opacity .5 s.
  Its background line is written `background-color: rgba(0,0,0,0.5) opacity: 1;` (no semicolon between them).
  TODO(trace): whether panorama's parser keeps the colour; ours draws it as written (black .5 over the blur).
- `.loading-screen-content__info__bg`: `bluedots_large_png` at `backgroundDotsSize` (360 x 360), `background-img-opacity: 0.03`.
- `.loading-screen-contents-bottom`: `height: fill-parent-flow(1); max-height: 920px`.
- `.loading-screen-content__info`: flow down, `margin-bottom: 24px`; `.hidden` opacity 0 + collapse (.25 s).
  `__info-container`: flow down, margin 20 px. `__titles`: flow down, centred.
  - `.loading-screen__mapicon`: `height: 150px`, `img-shadow: 0 0 6px 4.0 #000`, `visibility: collapse` until the
    script shows it. `__info__text-title`: white 40 px, `text-overflow: shrink`, nowrap, `margin-top: 10px`.
  - `__info__gamemode`: flow right, `margin-top: 20px`, centred; `__modeicon` 30 px wide, `margin-right: 8px`;
    `.loading-screen-content_text-gamemode` 30 px white, shrink.
  - `__info__text` 16 px white, margin 20 px. `.loading-screen-content__info-line`: 2 px, white, opacity .3, margin 0 20 px.
- `.loading-screen-progress-container`: bottom, margin 20 px 20 px 0, flow down. `.loading-screen-progress-text`:
  32 px tall, 22 px, `#CCCCCC`. `.loading-screen-progress-secondary-text`: Stratum2 16 px white, margin-bottom 5.
  `.loading-root #ProgressBar`: 100 % x 8 px, `rgba(0,0,0,0.671)`, margin-bottom 16 px; `.ProgressBarLeft`
  `gradient(linear, 0% 0%, 100% 0%, from(#134f87), to(#1ab8e0))`. `#ProgressBarSecondary`: 5 px, its fill blueColor to `#006633`.
- `.loading-screen-slide`: full size, `transition: blur, opacity, background-color 0.1s`; `.show` opacity 1; `.hide`
  opacity 0; `.show-first` opacity 1 + `slide-show-start` (0.2 s: opacity 0 / scale 1.1 to 1 / 1);
  `.show-blend-into-teamselect` (a black gradient, `slide-show-end`). `.loading-screen--closing`: 2.8 s, opacity 1
  until 70 % then to 0.
- `.loading-screen-screenshot-title`: white 50 px, bottom left, margin 50 px (the slide's own title).
- Unused by the layout today: `__overview--background` / `--map` (820 x 820 overhead map, collapsed),
  `.loading-screen-model*` (720 px agent models left / right), `.loading-screen-fade--dark` / `--teams`.

## Script (scripts/loadingscreen.ts)

- `MAX_SLIDES = 10`, `SLIDE_DURATION = 4`.
- `_Init` (`UnloadLoadingScreenAndReinit`): bar 0, map name "", game mode "#SFUI_LOADING", description "", both icons
  hidden, the slides deleted.
- `_UpdateLoadingScreenInfo(mapName, prettyMapName, prettyGameModeName, gameType, gameMode, descriptionText)`
  (`PopulateLoadingScreen`, from the client):
  - `${d:mp_roundtime}` / `mp_fraglimit` / `mp_maxrounds` in the description are replaced by the cvars' values.
  - map: `#LoadingScreenIcon` = `file://{images}/map_icons/map_icon_<map>.svg` (its `ImageFailedLoad` hides it and
    swaps the name's class `...text-title-short` for `-long`; neither class has a rule in the vcss);
    `#LoadingScreenMapName` = `prettyMapName` when given, else `GameStateAPI.GetMapDisplayNameToken(mapName)` localized.
  - mode (only when `gameMode` is set, else the info block gets `.hidden`): `#LoadingScreenGameMode` =
    `prettyGameModeName` when given, else `#sfui_gamemode_<gameMode>`; `#LoadingScreenGameModeIcon` =
    `icons/ui/competitive_teams.svg` when `GameStateAPI.IsQueuedMatchmakingMode_Team()` or the map is `lobby_mapveto`,
    else `icons/ui/<gameMode>.svg` (hidden when it fails to load); `#LoadingScreenModeDesc` = `descriptionText`.
  - then `_InitSlideShow`: for n in 0..9, `map_icons/screenshots/1080p/<map>[_<n>].png` when `$.BImageFileExists`; a
    slide's title is `#loadingscreen_title_<map>[_<n>]` when that token exists. When every image loaded or failed:
    `_StartSlideShow` picks a random slide, `show-first`; `_NextSlide` every 4 s: the next gets `show`, the one before
    `hide` 0.25 s later; one slide alone just shows. `JsOnMapLoadFinished` stops it.

## Strings (resource/csgo_english.txt)

`SFUI_GameMode_casual` "Casual", `_competitive` "Competitive", `_scrimcomp2v2` "Wingman", `_deathmatch` "Deathmatch",
`_gungameProgressive` "Arms Race"; the descriptions `SFUI_GameModeCasualDesc`, `SFUI_GameModeCompetitiveDesc`,
`SFUI_GameModeScrimComp2v2Desc`, `SFUI_GameModeDeathmatchDesc`, `SFUI_GameModeGungameProgressiveDesc` (copied into
loading-info.js); `SFUI_Map_<map>` (data/map-pool.js MAP_TITLES: `SFUI_Map_de_fachwerk` "Fachwerk"); `SFUI_LOADING`
"Loading...".

## Ours

- loading.js builds this structure with CS2's class names; loading.css is the vcss as CSS (the contents panel's blur
  a `backdrop-filter: blur(6px)`: a stand-in for mipmapgaussian 6).
- The mode shown is the home's pick at once (main.js join's `opts.mode`) and the server's welcome after (`mode`,
  `match`): CS2's icon and description for the CS2 mode the match runs (gamemodes.js cs2GameMode), the name ours
  (the queue, team size and round mode, as a server's `prettyGameModeName`). Zombie Escape: our name, icon and text.
- A map without a `SFUI_Map_` token shows its file name. TODO(trace): `GetMapDisplayNameToken`'s fallback in client.dll.
- Slides: one a map today (the 720p shot `--map-shots` bakes into ze-ui/mm; a ZE map its cover or bake's first
  shot). TODO: bake the 1080p set (`<map>_1` .. `_9`) so CS2's maps cycle as CS2's.
- The status lines carry our steps (client/home/load-progress.js); CS2 writes "Loading..." and download states there.
  The secondary bar isn't drawn. Fade out: ours .45 s (CS2's closing animation is 2.8 s, into team select).
- Not drawn: the slide's title label, the hint row (collapsed in CS2 too), VanityCrossFadePanel.
- Art: `lasers-bake --home-assets web/public/ze-ui/home` (default.webp, modes/*.svg).
