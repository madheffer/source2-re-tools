# CS2's Settings menu, crosshair codes and convar defaults

What the browser's Settings page (web/src/cs2web/client/settings/) is built from. Builds: client.dll 2026-10-15 (Ghidra
project `/client_20261015.dll`) for the crosshair code, client.dll 2026-11-12 (= the install's, source2-compiler
tools/re/binaries/client_20261112.dll) for the convar registrations; pak01 of the 2026-11-12 install for the layouts.

## The menu itself (panorama)

`lasers-bake --settings-ref <folder>` (bake/SettingsRefBake.cs) decompiles from pak01: every panorama layout / style /
script naming settings, crosshair, dropdown, slider, mainmenu*, csgostyles, the colour picker; resource/csgo_english.txt;
and from game/core's pak01 panorama_english.txt, keybindings_english.txt and the engine's base styles
(core/panorama/styles/*.css). Valve content: written to a scratch folder, never committed.

`node tools/settings-layout.mjs <folder>` turns it into web/src/cs2web/client/settings/cs2-layout.js (committed, generated):

- tabs: layout/settings/settings.xml's nav RadioButtons (`SettingsMenu.NavigateToTab("...")`): Search (icon),
  Promoted ("New"), VideoSettings, AudioSettings, GameSettings, KeybdMouseSettings, CrosshairSettings (label
  "Crosshair / Scopes" in this build). Each tab's file: settings_video / _audio / _game / _kbmouse / _crosshair.xml.
- Video has two sub tabs (`SettingsMenuVideo.SelectSimpleVideoSettings / SelectAdvancedVideoSettings` over
  `#video_settings` / `#advanced_video`) and a "HUD Edge Positions" button; the others jump buttons
  (`SettingsMenuShared.ScrollToId('<section id>')`).
- sections: `.SettingsBackground`, the title `.SettingsSectionTitleLabel`; rows in document order:
  `CSGOSettingsSlider` (text, convar, min, max, percentage, invert, value100percent, displayprecision, step,
  toggleconvar, audiogain, eventname), `CSGOSettingsEnumDropDown` / `CCSGOSettingsEnumDropDownBind` (convar or
  bindkey, Label children = options with `value`, label = the row container's other Label), `CSGOSettingsKeyBinder`
  (bind), buttons, free text, custom panels (CSGOAudioMeter, CSGOFrameTimeSlider, MapGraphicsSettingsPanel,
  CSGOCrosshairPreview), the crosshair's colour rows (`#XhairColorPicker` / `#XhairOutlineColorPicker`: the convars
  settingsmenu_crosshair.ts sets, cl_crosshaircolor_r/g/b/a, cl_crosshairoutline_r/g/b/a), the music modes' groups
  (`#SettingsMusicMode*`, one shown at a time by snd_music_settings_mode).
- the rows each cl_crosshairstyle shows: scripts/settingsmenu_crosshair.ts `OnCrosshairStyleChange` (everything in
  XHAIR_TOGGLED hidden, then per style; the outline colour row while cl_crosshair_drawoutline != 0, the bot row while
  cl_show_observer_crosshair == 2; styles 0, 1, 2, 6 are "dynamic-crosshair"; 3, 6, 0, 1, 7, 8, 9 tagged new).
- NEW: scripts/common/promoted_settings.ts' list with start / end dates (none current on 2026-11-16).
- CS2's current audio tab (differs from older screenshots): Master Volume, Main Menu Ambience Volume, Audio Device,
  EQ Profile (snd_headphone_eq Natural / Crisp / Smooth), L/R Isolation (snd_spatialize_lerp slider), Perspective
  Correction, Play Audio When Game In Background (snd_mute_losefocus, Yes = 0); Voice; Music with per-mode volumes;
  Game Mode EQ.

The look (settings.css) is ported from mainmenu.vcss (.mainmenu-content__container rgba(0,0,0,0.75),
.content-navbar__tabs 48px rgba(0,0,0,0.25), --dark 42px, tab buttons margin 0 6px radius 3px, Label Stratum2 medium
16px uppercase padding 4px 6px, hover rgba(255,255,255,0.025), selected #82d7ff1a + selectedNavColor #82D8FF,
.content-controls-actions-bar 96px padding 0 64px top border 5%), settings.vcss (.SettingsBackground 946px padding
42px 64px 0, rows min-height 48px, section title Stratum2 Black Italic 28px rgba(222,222,222,0.4), separator 1px
white at 10%, CSGOSettingsEnumDropDown:hover #141c27, .settings-tag Stratum2 Bold 12px #D8760E), settings_slider.vcss
(#Slider 25.5% + 10px, TextEntry#Value 80px Stratum2 bold 20px border 2px #cccccc15 radius 2px) and csgostyles.vcss
(DropDown height 36px margin 8px, the expand.vsvg arrow 16px; .PopupButton radius 3px, hover rgba(255,255,255,0.05),
Label Stratum2 medium condensed 24px uppercase margin 10px 12px 8px; DropDownMenu contextMenuBackground #262626
padding 8px 0, its Labels Stratum2 Light 16px padding 8px 16px, hover gradient #00000080 -> clear; Label's font
notosans; baseText #cccccc). Not found in the extracted .vcss: the game's base Slider track / thumb (matched by eye).

## Crosshair codes (client.dll 2026-10-15)

| Address | What |
|---|---|
| 1800fb070 | registers the console command `apply_crosshair_code` -> 180dc2c40 |
| 180dc2c40 | apply_crosshair_code: argc == 2; 180daf640 (parse) then 180daf490 (record -> struct, the struct's +0x40 preset 1.0), then 180dbca70 (rescale), 180dbafb0 (set convars) |
| 181092ba0 | registers MyPersonaAPI's GetCrosshairCode / BApplyCrosshairCode / BValidateCrosshairCode (the panorama popup, scripts/popups/popup_crosshair_code.ts) |
| 180bd3c70 | the classic share code: length 34 (0x22), "CSGO-" prefix, '-' at 10, 16, 22, 28; the 25 digits read last to first, each `n = n * 57 + digit` into an 18-byte big-endian buffer (fails on a digit outside the alphabet or a carry out of byte 0; the multiply and the add are two passes, same result); out: bytes 0..7, 8..15, 16..17 in order |
| 181c75400 | the alphabet "ABCDEFGHJKLMNOPQRSTUVWXYZabcdefhijkmnopqrstuvwxyz23456789" (57; no I, O, g, l, 0, 1) |
| 180daf640 | parse -> 32-byte record. Classic branch: byte0 == sum(bytes 1..15) & 0xff (16, 17 not summed), byte1 (version) >= 3 ("Invalid or old crosshair code" below), converted (below). Else: length 46 (0x2e), prefix "CS" (181cb5ec8), the 44 digits read last to first into 32 limbs (fail on a limb over 0xff), record[0] most significant; record[1] == 1, the u16 at 2 != 0, record[0] == 180dab5d0's checksum; then clamped (below) |
| 180dab5d0 | the record's checksum: sum(record[1..31]) & 0xff |
| 180daf490 | record -> the float struct S (0x44 bytes) |
| 180dbca70 | rescale: h = 180b80220() (the screen height, not read); S0 == h: no change; S0 > 0: k = h / S0 (f32), gap = roundf(k * gap) then max(1, .) if gap > 0 / min(-1, .) if < 0 (helpers 1801b9c30 maxss, 18015a010 minss); length, thickness, spread limit, split distance: if > 0, max(1, roundf(v * k)); S0 = h |
| 180dbafb0 | S -> convars (handles in .data 1825c84e8..1825c86f8, names below) |
| 1800081c0 (tier0) | V_roundf -> 1802a9ebc: the CRT roundf (half away from zero) |

The 32-byte record:

| Bytes | Field | S slot (180daf490) | Convar (180dbafb0) |
|---|---|---|---|
| 0 | checksum | | |
| 1 | version (1) | | |
| 2..3 | u16 screen height (clamped >= 240) | +0x00 f32 | cl_crosshair_screen_height (int) |
| 4 bits 0-4 | style (<= 9) | +0x04 int | cl_crosshairstyle |
| 4 bit 5 | follow recoil | +0x08 byte | cl_crosshair_recoil |
| 4 bit 6 | centre dot | +0x10 byte | cl_crosshairdot |
| 4 bit 7 | T style | +0x11 byte | cl_crosshair_t |
| 5..8 | colour r g b a | +0x24..0x27 | cl_crosshaircolor_r/g/b/a |
| 9..12 | outline colour r g b a | +0x28..0x2b | cl_crosshairoutline_r/g/b/a |
| 13 bits 0-5 | thickness (<= 32) | +0x18 f32 | cl_crosshair_thickness (int) |
| 13 bits 6-7 | outline mode (<= 2) | +0x0c int | cl_crosshair_drawoutline |
| 14..15 | i16 gap (clamped +-3840) | +0x14 f32 | cl_crosshair_gap (int) |
| 16 | length | +0x1c f32 | cl_crosshair_length |
| 17 | dynamic spread limit | +0x20 f32 | cl_crosshair_dynamic_spread_limit |
| 18..21 bits 0-6 | split distance | +0x2c f32 | cl_crosshair_dynamic_splitdist (& 0xff) |
| bits 7-13 | inner split alpha x100 (<= 100) | +0x30 = v * 0.01f | cl_crosshair_dynamic_splitalpha_innermod |
| bits 14-20 | outer split alpha (x100 - 30, <= 70) | +0x34 = v * 0.01f + 0.3f | cl_crosshair_dynamic_splitalpha_outermod |
| bits 21-27 | split size ratio x100 (<= 100) | +0x38 = v * 0.01f | cl_crosshair_dynamic_maxdist_splitratio |
| bit 28 | scope dot uses crosshair colour | +0x3c byte | cl_ironsight_usecrosshaircolor |
| 22 | scope dot scale (x100 - 10, <= 190) | +0x40 = v * 0.01f + 0.1f | cl_ironsight_dot_scale |
| 23..31 | unused | | |

The style and outline slots are ints (the decompiler shows float casts; the stores are ints: the oracle reads 5, not
7e-45). The new-format clamps are only on that branch; the classic branch returns its converted record unclamped.

Classic code (M = its 18 bytes) -> record (180daf640's first branch):
u = M[10..13] as a little-endian u32; version 3: u = ((M[2] & 0x20) << 23) | (u & 0xcfffffff). record[2..3] = M[14..15];
record[4] = ((M[2] & 0x10) << 1) | (M[2] & 0xcf); record[5..8] = M[3..6]; outline = (0, 0, 0, M[6]); record[13] =
((u >> 23) & 0x1f) | (((u >> 28) << 6) & 0xff); gap = M[7] zero-extended (movzx: never negative); record[16] = M[8],
[17] = M[9]; D bits 0-6 = u & 0x7f; bits 7-13 = trunc(roundf((((u >> 7) & 0x1f) * 0.05f) / 0.01f)); bits 14-20 =
trunc(roundf((((u >> 12) & 0xf) * 0.05f) / 0.01f)), D &= 0xf01fffff; bits 21-27 = (u & 0x7f0000) << 5; bit 28 = the
current cl_ironsight_usecrosshaircolor (its value block 1825c86f0 + 0x58); record[22] = trunc(roundf((clamp(current
cl_ironsight_dot_scale (1825c8700 + 0x58), 0.1, 2) - 0.1f) / 0.01f)) (maxss 0.1 at 181ada28c, minss 2.0 at 181ac6078,
0.05 at 181ac606c, 0.01 at 181ada280); record[1] = 1, record[0] = the checksum.

Checked: web/src/cs2web/client/settings/crosshair-code-test.mjs against tools/re/xhair-oracle.json, written by tools/re/game/xhair_oracle.py:
180daf490 and 180dbca70 run under Unicorn (V_roundf and _V_StringAfterPrefixCaseSensitive stubbed, 180b80220
returning the case's height, the two ironsight value blocks pointed at the case's values) over 608 codes (classic
versions 0-6, right and wrong checksums, new codes with noise and plausible fields, bad digits, overflow): every
field and the rescale bit-exact, 437 valid.

Unread: 180b80220 (the screen height; the browser uses the canvas's device-pixel height), the encoder behind
MyPersonaAPI.GetCrosshairCode (the popup's Copy, greyed), the settings menu's own size-edit path (180da8b00 /
180daa8d0 / 180da0610 / 180dc0420 call 180dbca70 + 180dbafb0: the browser rescales the sizes to the screen, then sets
the edited one and the height, as cl_crosshair_screen_height's help says), the crosshair's drawing (HUD and
CSGOCrosshairPreview: the browser's is a stand-in, crosshair-view.js).

## The crosshair's drawing (client.dll 2026-10-15, csgo_crosshair)

Built each frame by **180da0610** (callers 180db8e80: the HUD, 1811d3100: the settings preview), on an object whose +0
points at a shape list (64 entries of 0x40 bytes + the count at +0x1008: csgo_crosshair's `CrosshairParamBuffer_t`), +8
at the legacy style's state; +0x48 / +0x4c / +0x50 from 180c7be40: the pawn's m_flInterpolatedInaccuracy (+0x1f50, or
its interpolated var's value at the frame, 1807cc690), the weapon's m_fAccuracyPenalty (+0x1a18), the weapon's vfunc
0xbd0 (18080d490: its vdata's m_flSpread[m_weaponMode], vdata +0x750, mode +0x1a00); +0x54 the pawn's FOV (vfunc 0x118;
90 with no pawn); +0x10 / +0x1c / +0x28 / +0x34 the eye and its forward / right / up (18093c760; all zero with no pawn:
the main menu's preview has no spread);
+0x5c the preview flag, +0x5d the editor's Dynamic Preview; the struct (180daf490's layout) at +0x60; then
+0xa4 / +0xa8 the centre (truncf of the view's centre, 180da17d0: x = (ndc + 1) / 2 W, y = H - (ndc + 1) / 2 H; moved to
the aim punch's point when cl_crosshair_recoil (+0x68), a pawn, not the preview: forward (181740910 AngleVectors, deg x
f32 0.017453292) of the eye angles (pawn vfunc 0x570, 180c74ec0) + the aim punch (180853a60: the aim punch services'
18084d8b0, the client's aim-punch.js), 2000 u from the eye, on screen: a coordinate whose ceil is over 1 px from the
panel's centre replaces it, truncf), +0xb0 the spread
in pixels, +0xac the "resting" spread (style 7 only), +0xb4 the dynamic gap, +0xb8 the alpha multiplier.

- the struct: from the convars (180db0230) or, spectating, the observed player's code (180db03f0: cl_show_observer_crosshair,
  cl_observed_bot_crosshair; a bot's is the default code "CSGO-y9Qw8-sCzPb-jORFu-ov6L8-GwMXL"), then 180dbca70 to this
  screen's height (written back to the convars when it changed).
- spread (180d9e560): d = forward - right x (inaccuracy + spread) (f32), |d| as sqrt((z z + y y) + x x), d / |d|,
  2000 d + eye on screen, its distance from forward x 2000 + eye's ((dz dz + dy dy) + dx dx), V_roundf. On screen:
  180c19db0 -> 180c19cd0 with the view-projection at 18256b020 + slot x 0x40 (the engine's vfunc 0x310 the slot): x =
  ((m1 p1 + m0 p0) + m2 p2) + m3, y = ((m4 p0 + m5 p1) + m6 p2) + m7, w = ((m12 p0 + m13 p1) + m14 p2) + m15, w < 0.001:
  x 100000, else / w; 180da17d0: ((x + 1) 0.5) W, H - ((y + 1) 0.5) H (W / H the engine's vfunc 0x1e8).
- dynamic values (styles 0, 1, 7, or weapon_debug_spread_show, 1825c8530): L = spread limit + 64; gap = 180d9e770's soft clamp
  (f32: x <= lo = 0.75 L: x; else L - V_expf(-(1 / (L - lo)) (x - lo)) (L - lo)), at most L, at least the thickness
  with the dot on,
  truncf; alpha = 1 - 0.8 clamp((x - x0) / (0.25 - x0)) with x0 = +0x50 + +0x4c (0.2 when x0 == 0.25f and x >= 0.25).
  Preview: x = |V_sinf((float)Plat_FloatTime())| 0.1 while the Dynamic Preview runs, else +0x48 + +0x50. weapon_debug_spread_show (help "Draws
  the current weapon's true inaccuracy + spread radius around the crosshair", default 0, flags 0xc008) also ends the
  frame with 180da61c0 at the centre: radius spread + 2, width 2, 30 degrees, rgba fa fa 32 ff, outline black (1, 1).
  cl_grenadecrosshair_keepusercrosshair 0 (1825c8500) fades the user's crosshair by +0xbc while a grenade's line-up
  crosshair shows: k = 1 - +0xbc (at least 0; 0 returns before the struct is even read), the struct's colour and
  outline alphas (+0x87 / +0x8b) x k, (int) truncated (below, "The grenade line-up crosshair").
- the dot first (180da7510, cl_crosshairdot), then by style: 0 bars (180da63f0) at the dynamic gap, alpha x +0xb8;
  1 circle (180da6290) at the dynamic gap; 2 180da66c0; 3 180da6a80 circle at max(1, gap); 4 180da6ae0 bars at
  max(0, gap); 5 180da6b60; 6 180da6e30 the dot (unless already drawn); 7 180da6e60; 8 180da7110; 9 180da7390.
- 180da10c0 splits a thickness: n = max(1, cvtss2si(t)) (ties to even), lo = (n + 1) / 2, hi = n - lo, even = lo == hi.
- 180da63f0 bars(T, gap, len, t): g = max(0, gap); left [floor(cx - g) - len, floor(cx - g)) x [cy - lo, cy + hi),
  right from ceil(cx + g) + (even ? 0 : -1), top [floor(cy - g - len), + len) (not with T), bottom from ceil(cy + g) +
  (even ? 0 : -1); each a box (180da8410: stores x0, y0, x1 - 1, y1 - 1, type 0).
- 180da6290 circle(r, t): a ring (180da6080, type 1, centre - 0.5) at the centre minus (even ? 0 : 0.5), radius r + t,
  width max(1, t - 1).
- 180da7110 square: x0 = floor(cx - g - t + n), x1 = floor(cx + g) (n = -1 with the dot on an odd thickness), the same
  in y; boxes top (x0, y0)-(x1, y0 + t), bottom (x0, y1)-(x1, y1 + t), left (x0, y0)-(x0 + t, y1 + t), right
  (x1, y0)-(x1 + t, y1 + t).
- 180da7390 quadrant: arcs (180da61c0, type 2) at the centre minus (t >= 1 and odd ? 0.5 : 0), radius max(1, gap) + t,
  width t, clamp(cl_crosshair_dynamic_maxdist_splitratio, 0, 1) x 90 degrees.
- 180da6e60 dynamic quadrant: with a spread: the ring (width max(1, t - 1), radius it + the dynamic gap) while the spread
  is under 100 px and within 10 of the resting one, else arcs (radius t + dynamic gap) 45 - 40 clamp((+0x48 - +0x4c) /
  (0.2 - +0x4c)) degrees wide (45 / 5 when +0x4c == 0.2f); colours x +0xb8; then the bars at max(0, gap) unscaled.
- 180da66c0 classic: x = (+0x48 + +0x50) 320 / V_tanf(fov / 2) (preview: +0x50 = max(0, V_sinf(t) 0.15), fov 90); g1 =
  roundf(H / 480 x), g2 = roundf(H / 480 min(x, split distance)); g1 > 0: outer gap = gap + g1, inner = max(0, gap +
  g2); else trunc((c + gap) - 4) with c = 4 (no pawn), else by the pawn's m_fFlags (+0x3f4): 8 without FL_ONGROUND,
  2 with FL_DUCKING, else 6 above 100 u/s (GetAbsVelocity 180219ae0), else 4. Past the split distance: bars at (ceil((1 - ratio) len) + outer gap) of length floor(len ratio), alpha x
  outermod (cvttss2si), then bars at the inner gap of length ceil((1 - ratio) len), alpha x innermod; else the bars at
  the outer gap, full alpha (the disassembly 180da6900-6a30: the decompiler drops the second call's arguments).
- 180da6b60 legacy: a state at +8: +4 the feedback, +8 the shot count seen. Not the preview, a pawn and a weapon:
  unless the weapon is deploying (180817b50: now - m_nDeployTick (+0x1a40) <= (uint)(m_flDeployDuration (vdata +0x7c4)
  x 64 + 0.5)) with m_iShotsFired 0 (then both reset to 0), m_iShotsFired (pawn +0x1eb0) over the count, the attack or
  attack2 button down for the controller's split-screen slot (the kbutton_t "attack" at 182233ea0 / "attack2" at
  182233f30, +0x32 + slot x 0x1c, the slot the controller's +0x6cc via pawn vfunc 0x998) and m_iClip1 >= 0 (vfunc 0xa58,
  1807cb860: +0x1928) adds (int) m_flRecoilMagnitude[mode] (vfunc 0xb80, 1807ccfb0: vdata +0x7a0) / 3.5; the count
  then follows m_iShotsFired. Preview: +15 every RandomFloat(0, 0.6) s. Clamped [0, 25], then minus 42 x frametime;
  bars at roundf(max(0, gap) + H x feedback / 1200).
- colours: 18174a050 0-255 sRGB -> linear floats (0.04045, 12.92, V_powf((c + 0.055) / 1.055, 2.4)), alpha / 255.

**The grenade line-up crosshair** (180da0610 +0x124..0x1c7, 180da7770):
- 180da0610 builds the list in this order: the friendly icon (below), the line-up, then the user's crosshair (64 shapes
  at most; a 65th add is dropped). The line-up: when the HUD state 180d568d0 (+0x1c0 of 180d56790's object) is not 3 or
  4, the pawn's active weapon (1808cc9c0) cast to the grenade class (1819fc50c with 1823139c8 / 1823139a0) and
  1807d62d0(grenade) says so: a start time (the object's +8 pointer's float) set to Plat_FloatTime when 0, +0xbc =
  18173d3d0(min(1, (now - start) / 0.2), 0.2) (a bias: x / ((1 / b - 2) (1 - x) + 1), x clamped [0, 1], b
  [FLT_MIN, 1]), then 180da7770; else the start and +0xbc are 0.
- 1807d62d0(grenade): its owner pawn (180941fa0), not m_bThrowAnimating (+0x1f25); elapsed = curtime - (+0x1a44,
  m_flAttackHoldStartTime) when that is set (18075d250 the entity's time, 18015c5e0 the difference), else 0; elapsed > 0;
  the type (vfunc 0xd58: 0 explosive, 1 flash, 2 fire, 3 decoy, 4 smoke) picks cl_grenadecrosshair_<type> (1824c72d8 /
  2c8 / 2a8 / 2e8 / 2b8, off: false; smoke off still passes when 180c7c3d0's object +0x50 is non-zero: the
  MapAnNodeManager game system's singleton 182570a80 (registered by 1800e6a30, "MapAnNodeManager"), +0x50 its node
  count: map annotations loaded; this game has none) and cl_grenadecrosshairdelay_<type> (1824c7320 /
  310 / 2f0 / 330 / 300, read through 180160b10): shown when 0 <= delay <= elapsed.
- m_flAttackHoldStartTime: 180828000 from the pawn's PreThink (vfn 0xa00 = 180c905e0, called by the movement
  services' command 180a70de0 before the movement; ItemPostFrame runs later, in PostThink vfn 0xa08): attack or attack2
  (0x801, 18094d9e0: the weapon's vfn 0xad0 -> the movement services' m_nButtons +0x50, its down states +0x58, this
  command's) held and the pawn's m_bWaitForNoAttack (+0x1ebc, as the last command left it) clear -> now if it was 0;
  else 0. Deploy 180808c40 zeroes it and sets
  m_bWaitForNoAttack; CCSWeaponBase::ItemPostFrame's no-attack branch (180817f20 +0x3f6) clears m_bWaitForNoAttack and
  m_iShotsFired. So the line-up shows once the pin has been held past the delay (2 s by default), from a fresh press.
- m_bThrowAnimating (+0x1f25): set by StartGrenadeThrow (1807de430), cleared by the grenade's Deploy (1807c93d0) and
  by its activity-finished handler, vfn 0xd18 = 1807d7f70: activity 200 (the pull) -> 0xc9; activity 0xca (the throw)
  -> m_bThrowAnimating 0, then activity 0x1b (the draw). 1808212a0 calls it when the weapon's animation graph raised
  WPN_ACTION_COMPLETE that update (180910e60 walks the graph's tags: the token at 182535718 sets +0x2b4; 182535728 /
  182535730 do too for the action kinds 2 / 3 at +0x2c4). Ported: weapons/fp/fp.js ends the throw on its graph's
  WPN_ACTION_COMPLETE (the clip's length + 0.25 only a backstop), viewmodel.js throwAnimating.
- 180da7770: the colour: cl_crosshaircolor_r / g / b (1825c85d0 / 5e0 / 5f0), each clamped [0, 255], alpha
  cl_crosshaircolor_a (1825c8600) clamped, x +0xbc, V_roundf, (char) cvttss2si. Ticks: the forward vector turned
  step by step by a quaternion about the view's up (+0x34) and about its right (+0x28): the axis normalised (18015a140
  VectorNormalize: len = sqrtss((y y + z z) + x x), x 1 / len between 1e-17 and 1e17; 0: zero vector), q = (axis x s,
  c) from V_sincosf(0.0872664600610733) (half of 10 degrees; a zero axis: identity 18236fa60). The rotation in SIMD
  lanes: t = 2 (v.zxy q.yzx - v.yzx q.zxy), v' = (t.zxy q.yzx - t.yzx q.zxy) + (v + w t); each step's v' x 2000 + the
  eye (+0x10) on screen (180c19db0, 180da17d0), kept in a CUtlVector (UtlVectorMemory_*). Counts: across floor(atan(
  aspect tan(fov x 0.008726646)) x 114.59155 x 0.5 / 10) (V_tanf, V_atanf, the aspect the view render's vfunc 0x88:
  +0x1cd0, set from engine2's CEngineClient vfunc 0x2c0 (180076490: width / height in f32 unless the convar at
  18069be10 is over 0)), up floor(fov x 0.5 / 10).
- the sizes from +0x58 (s = the screen height / 1080, 180b80220): label h = floorf(s 20), w = floorf(h 1.28); s' =
  floor(s) when s >= 1; n = max(1, cvtss2si(s' + s')), a = (n + 1) / 2 above, b = n - a below (floats fa, fb).
- the boxes (180da8410, outline colour 0, outline (0, 0)): (0, cy - fa)-(cx + cx, fb + cy) and (cx - fa, 0)-(fb + cx,
  cy + cy) (cx / cy +0x40 / +0x44); per across point x = floorf(px): (x - fa, cy - L)-(x + fb, L + cy), its mirror at
  (cx - x) + cx the same; per up point y = floorf(py): (cx - L, y - fa)-(cx + L, y + fb) and its mirror (cy - y) + cy.
  L starts at 10 for each set and becomes floorf(L x cl_grenadecrosshair_tickscaling) (1825c8510, 1.1 [0.5, 2]) after
  each tick pair.
- labels (cl_grenadecrosshair_ticklabels, 1825c8520, a byte, default 1): 180da7640(x, y, w, h, glyph, colour): type 3,
  the rect (x, y)-(x + w - 1, y + h - 1), +0x10 = (float) glyph, the colour as 180da8410's; glyph 0x7fffffff: none.
  Across: x = floorf(((x - fa) + (x + fb) - w) 0.5), y = (L + cy) + 2; up: x = (cx + L) + 2, y = floorf(((y - fa) +
  (y + fb) - h) 0.5). The glyph for the k-th tick (k 1..5 only): across (5 - k) 4 for the computed side (its counter
  runs -1, -2 ..), + 1 for the mirror (+1, +2 ..); up 22 - 4 k, + 1 for the mirror: the atlas cells "-kx" / "kx" /
  "-ky" / "ky" (grenade_crosshair_numerals: 4 columns of 64 x 50 texels, rows -5 .. -1 top to bottom).

**The friendly warning** (180da0610 +0x92):
- param_2 (from the HUD's 1811d3100): +0 / +4 the panel's centre (floor(w / 2 + x), floor(h / 2 + y)), +8 the screen
  height / 1080, +0xc the friendly flag, +0xd 0, +0xe 1; the flag and "draw" byte from 180dab650: the 2 bytes
  180dbdc10 last pushed (DAT_1825c8bf8) if Plat_FloatTime - its stamp <= 0.5.
- with the flag: half = V_roundf(+0x58 x 28) x 0.5, a type 4 shape (cx - half, cy - half)-(half + cx - 1, half + cy -
  1), colour 0x3300a5ff (r ff, g a5, b 00, a 0x33) through 18174a050, outline 0.
- the flag: CCSGOHudTargetID's 180eaf7c0 pushes (draw, sameteam && cl_crosshair_friendly_warning (1825c8690)) each
  frame; 180eb4260 -> 180eb5b50(target, observing == 0): the target (180c7bbf0) a living player pawn (vfuncs 0x4f0,
  0xab8, 0x4e8) not an enemy of your team (1808d9290 false: "#Panorama_HUD_playerid_sameteam") keeps the flag; an
  enemy clears it. Gates: hud_showtargetid (182579018, 1); not flashed: m_flFlashBangTime (+0x14fc) more than 0.5 s
  ahead of curtime hides the target unless 180ce2420 (force_spectator_only_tools, 18257b360, or a spectator's tools);
  m_flFlashOverlayAlpha (+0x1504) >= 0.7 only picks the "#SFUIHUD_targetid_FLASHED" text (observer mode 2).
- 180c7bbf0: once m_delayTargetIDTimer (+0x36e0) is elapsed: m_iIDEntIndex (+0x36dc), else (-1) m_iOldIDEntIndex
  (+0x36fc) while m_holdTargetIDTimer (+0x3700) runs.
- C_CSPlayerPawn 180c9ae90 (each frame, c_cs_player_pawn.cpp:0x1168): m_iIDEntIndex = -1; mp_playerid (1824bc5d0, 0)
  2: done; a screen fade over 75 (180c0d980(-1) vfunc 0x18) with this pawn the local / observed one: done. The camera
  services' vfunc 0x108 (eye position, angles), AngleVectors; TraceLine 180200f20 from eye + 10 fwd to eye + 2500 fwd,
  interacts-with 0xc3003, group 3, flags 0x49, the pawn (1809dd600 / 1809ea740) ignored, the nearest hit. No hit:
  180352920 (a filter, 0xc3003, group 4) + 180aca060, UTIL_ClipTraceToPlayers(start, the line's end + 72 forward, filter,
  trace, 0, 60, |end - start| / |new end - start|): each player (the list walked by 180a7f1b0 / 180a83a50), alive
  (vfn 0x4e8), not dormant (+0x30 bit 7 of its identity), not the filter's two ignored handles, whose centre (vfn 0x2b0)
  lies 0..60 u from the line (18174cfb0), clipped by ClipRayToEntity (180a1aa70, a line ray); a fraction under the given
  one (the first line's own end) replaces the trace. Every player's box is already in the first line's world here, so
  it can only find what that line found: nothing to add. A hit entity not this
  pawn (and of its team when mp_playerid is 1), its centre (vfunc 0x2b0) not behind smoke (1807cd7f0 <= 0): a new index
  starts m_delayTargetIDTimer at mp_playerid_delay (1824bc5e0, 0.4; 0 for a player 1808d9120 says isn't an enemy);
  m_iIDEntIndex and m_iOldIDEntIndex = it, m_holdTargetIDTimer = mp_playerid_hold (1824bc5f0, 0.1).
- m_iIDEntIndex is the client's (no server.dll field): pawn +0x36f8 (m_iTargetedWeaponEntIndex) is the weapon target
  180c9ec60 keeps (client/hud/targetid.js).

**tier0's maths** (tier0.dll 2026-10-15): V_sincosf 180008240 (sinf then cosf), V_sinf 180008280, V_tanf 180008300,
V_atanf 180007ef0, V_expf 180007f90, V_powf 1800081a0, V_roundf 1800081c0 wrap the statically linked MSVC CRT's
(AMD libm): sinf 1802e6570, cosf 1802e0d70, tanf 1802e7e90, atanf 1802e057c, expf 1802e1ec0, powf 1802e5130. Each tests
the flag at 1803ab28c first: set at start-up on a CPU with FMA3, it takes the FMA path (below). SSE2 path, all in
double from the f32 argument:
- sinf: |x| < 2^-13: x; < 2^-7: x - ((x x) x) / 6; <= pi / 4: x + ((S4 x2 + S3) x4 + (S2 x2 + S1)) (x x2) (S1..S4 =
  -1/6, 1/120, -1/5040, 2.7557319223985893e-06); above, below 1.6e7: n = (int)(|x| 2 / pi + 0.5), rhead = |x| - n
  1.5707963267341256, rtail = n 6.077100506506192e-11, r = rhead - rtail; when the exponent dropped by more than 15:
  t = rhead, rhead = t - n 6.077100506303966e-11, rtail = n 2.0222662487959506e-21 - ((t - rhead) - n 6.0771...e-11),
  r = rhead - rtail; by the first r's exponent e: e >= 0x3f2 the polynomial (sin's for n even, cos's for odd: (-0.5 x2
  + 1) + ((K4 x2 + K3) x4 + (K2 x2 + K1)) x4, K1..K4 = 1/24, -1/720, 2.48e-05, -2.755731922398589e-07); e > 0x3de: r -
  (r / 6) r2 or 1 - r2 / 2; else r or 1; negated unless bit 1 of n equals the sign. >= 1.6e7: 1802e9830 (Payne-Hanek).
- cosf: the same reduction (threshold 500000, beyond: 1802e9290), the quadrants swapped, negated when (n + 1) & 2.
- tanf: |x| < 2^-27: x; < 2^-13: ((x x) x) / 3 + x; <= pi / 4 and after one reduction step (below 8388608, beyond: an
  inline Payne-Hanek over the table at 1803403f0): r + (r2 r) (T1 r2 + T0) / ((U2 r2 + U1) r2 + U0) (T0 0.3852960712639954,
  T1 -0.017203248047148168, U0 1.1558882143468838, U1 -0.5139650547885454, U2 0.01844239256901656), -1 / t for odd n,
  the argument's sign xored in.
- expf: t = x 92.33248261689366 (64 / ln 2); t >= 8192: inf, t < -9600: 0 (1802e9478); n = cvtpd2dq(t) (to nearest
  even), r = x - n 0.010830424696249145, p = (r r) (r / 6 + 0.5) + r, (p T + T) 2^((n - j) >> 6), T = the 2^(j / 64)
  table at 18033e370, j = n & 63.
- Payne-Hanek (sinf SSE2 >= 1.6e7: 1802e9830; cosf SSE2 >= 500000: 1802e9290; tanf both paths and sinf FMA
  >= 16779436: inline): e = x's exponent, off = 0x86 - (e >> 3) into the byte table at 1803403f0 (1803404a0 the same
  bytes for 1802e9830), m = the mantissa with its implicit bit; the 192-bit product m (T[off] + T[off + 8] 2^64 +
  T[off + 16] 2^128) mod 2^192 in words r8 / r9 / r10 (x86 mul / adc); s = 54 - (e & 7): n = r10 >> s plus the bit
  below it (when set: all three words complemented and the sign bit set); region = n & 3; r10 keeps its low 54 - (e & 7)
  - 10 bits, is normalised to 53 bits with r9 / r8 shifted in (6-bit shift counts), exponent and sign packed: that
  double x 1.5707963267948966. cosf FMA >= 3373259520 (1802e8e80): the same words, then a double-double head: the
  low word as a double, the high one split at 26 bits (& 0xfffffffff8000000), x pi / 2 in three parts (1.5707963109016418
  / 1.5893254712295857e-08 / 6.123233995736765e-17) with fused adds.
- the FMA path (sinf 1802e6910, cosf 1802e1050, tanf 1802e8200, expf 1802e2030): the same constants, Horner with fused
  steps (sin: x + (((S4 x2 + S3) x2 + S2) x2 + S1) x^3; sinf's cos: fma(x2, -0.5, 1) + (((K4 x2 + K3) x2 + K2) x2 + K1)
  x4; cosf's cos: 1 - x2 0.5 unfused, then the same; tan: fma(x2 r, (T1 x2 + T0) / ((U2 x2 + U1) x2 + U0), r)), one
  reduction step n = trunc(fma(|x|, 2 / pi, 0.5)), r = fma(-n, p1, |x|) - n p1t (thresholds 16779436 / 3373259520 /
  3373259264, beyond them the Payne-Hanek above); small forms x - (x x x) / 6, 1 - x (x / 2), (x x x) / 3 + x fused;
  sinf's sign (region >= 2) xor (x < 0), cosf's (region + 1) & 2; expf r = fma(-n, ln2 / 64, x), p = fma(r2, fma(r, 1/6,
  0.5), r), fma(p, T, T) 2^m.
- atanf equals Math.atan rounded to f32 on every input checked (both paths); powf doesn't (1 ulp on ~0.02%): not ported
  (its one crosshair use, 18174a050, feeds the shader's colours, which a GPU writes in 8 bits; the GL path takes its own
  linear table). Its SSE2 path: a packed-double log2 (the mantissa's top 8 bits rounded index an inverse table at
  180305a30 and a log table at 18033c370; |x - 1| small: an atanh series 18033c300 / 18033c310) times y, then expf's
  table; then the special cases (negative x with integer y, zeros, infinities: 1802e96d4).
Ported: web/src/cs2web/client/settings/tier0-trig.js (the SSE2 path and the dispatch: the FMA path is the default,
setTier0Path('sse2') the other), tier0-fma.js (the FMA path, fma() exact with BigInt), tier0-ph.js (both Payne-Hanek
finishes). Checked bit for bit (tier0-trig-test.mjs, 20000 inputs each, 6% of them huge): the SSE2 path against tier0
under Unicorn (tools/re/game/tier0_trig_oracle.py), the FMA path against tier0 called natively on an FMA3 CPU
(tools/re/game/tier0_native.py: the flag read back is 1). The crosshair oracles run the real tier0 under Unicorn
(tools/re/game/tier0_link.py: relocated to 0x260000000, the client's imports pointed at it): their tests take the SSE2 path.

**csgo_crosshair** (`lasers-bake --shader-src csgo_crosshair`: one static combo; the vertex shader passes a quad's
screen position and a 64-bit mask of the shapes covering it): per pixel (gl_FragCoord minus the panel's offset, as
ints), for each masked shape: (outline, fill) coverage; type 0: fill inside [x0, z] x [y0, w] inclusive, outline inside
it grown by o.x left / top and o.y right / bottom (cl_crosshair_drawoutline 1 = (1, 1), 2 "Half" = (1, 0): top and left
only); type 1: d = |p - c|, a = atan2(dx, -dy), t = max(smoothstep(0, pi / 2, a), smoothstep(-pi / 2, -pi, a)),
fill = smoothstep(r + .5, r - .5, d) smoothstep(r - w - .5, r - w + .5, d), outline the same at r + lerp(o.x, o.y, t)
and r - w - lerp(o.y, o.x, t); type 2: also x smoothstep(h + (o + .5) / d, h + (o - .5) / d, q) for the outline and
smoothstep(h + .5 / d, h - .5 / d, q) for the fill, q = |a - floor(a 2 / pi) pi / 2 - pi / 4|, h = angle / 2, d >= 1;
types 3 / 4 (materials/dev/csgo_crosshair.vmat's g_tGlyphAtlas t31 grenade_crosshair_numerals and g_tFriendlyIcon t32
friendly_crosshair_icon): outside the rect nothing, else size = max((zw - xy) + 1, 1) and the mean of 3 x 3 SampleLevel
.x taps (rows outer): type 3 at (64, 50) (cell (g % 4, g / 4) + ((p + 0.5) - xy) / size) + ((i + 0.5) / 3 - 0.5)
(64, 50) / size, x 1 / 256; type 4 at ((p + 0.5) - xy) / size + ((i + 0.5) / 3 - 0.5) / size. Type 3 is a fill
(coverage x colour alpha) in the best-of choice; type 4 adds colour x coverage x alpha to a sum the composite adds x
(1 - a) after. The strongest fill and the
strongest outline win (>=), then out = (lerp(outline.rgb aO, fill.rgb, F) + add (1 - a), a = lerp(aO, 1, F)), aO = (1 - F) outline.a (the outline's colour weighed aO (1 - F): the CPU port had dropped the (1 - F) until the GPU comparison caught it).

Ported: web/src/cs2web/client/settings/crosshair-draw.js (180da0610's values and every style, the recoil centre, the legacy
feedback, the debug arc, the list's order and its 64 cap), crosshair-lineup.js (1807d62d0, 18173d3d0, 180da7770, the
friendly icon), client/hud/player-target.js (180c9ae90, 180c7bbf0, 180eb5b50's friendly flag), crosshair-proj.js (the eye vectors, the view matrix's rows, 180c19db0 / 180da17d0, 180d9e560,
181740910), crosshair-gl.js (the shader on the GPU, the block as CrosshairParamBuffer_t), crosshair-raster.js (the same
on the CPU: the fallback and the tests' reference), crosshair-view.js (the HUD's canvas, the preview). The client feeds
it per frame (game.js crosshairFrame): the gun's predicted inaccuracy interpolated between its last two ticks by the
frame's fraction (as the interpolated var), its spread and accuracy penalty (gun-accuracy.js: acc.penalty is
m_fAccuracyPenalty), the frame's camera (eye, rendered angles with the punches, FOV), the eye angles, the aim punch, the
pawn's flags / speed, m_iShotsFired as ItemPostFrame keeps it (+1 a shot, 0 on a command with no attack button and no
reload key), the deploy tick, m_iClip1, m_flRecoilMagnitude, m_bWaitForNoAttack and m_flAttackHoldStartTime (the
grenade's name for the line-up), the friendly flag.
Checked: crosshair-draw-test.mjs (the style functions under Unicorn, xhair_draw_oracle.py: 600 crosshairs, 1623 shapes
equal; the band raster equal to the full box), crosshair-proj-test.mjs (180d9e560 through the real 180c19db0 /
180c19cd0 / 180da17d0 and 181740910 under Unicorn, xhair_proj_oracle.py: 500 random views, every spread, centre and
forward equal), crosshair-lineup-test.mjs (180da7770 under Unicorn with tier0's maths, xhair_lineup_oracle.py: 300
views, 9842 shapes equal), the GPU against the CPU in the browser (149 random crosshairs, 782,296 pixels: within 1 / 255;
before types 3 / 4).
Not checked against the DLL: 180da0610's own arithmetic between those calls (the dynamic gap's clamp, the alpha: ported
from the disassembly) and the shader's float ops (the decompiled SPIR-V; GLSL's on the GPU as CS2's). The browser
blends the result in sRGB (CS2 its linear output into its sRGB target); the friendly icon's additive glow goes out
premultiplied with alpha 0 (the CPU raster can only approximate it with straight alpha). Not checked: the friendly icon's
rect (inside 180da0610, from the disassembly), the player target (180c9ae90: the trace is the trace world's, the timers
from the decompile). The target ID's smoke test (1807cd7f0: the client's smokes, each that did its effect +0x1364,
its grid +0x13b8 walked by 1807de9d0 with the summing visitor 181bd3c70, x the age weight from +0x13c4) runs over the
densities the client draws (client/fx/smoke-sight.js: each texel's inner byte / 255; the walk shared with the server,
src/cs2web/sim/smoke-walk.js): CS2's client simulates its smokes in f32, so a voxel under 1 / 255 reads 0 here.
The textures' sampler: the shader's DefaultSamplerState (s15 / s16) is a render-state literal (VRF: VariableSource
__RenderStateLiteral__, IntDefs 0, flags SamplerFlag4; `lasers-bake --shader-src csgo_crosshair <out> --vars`): the
packed sampler description 0. rendersystemvulkan (2026-10-15) builds a VkSamplerCreateInfo (sType 31) from such a
description in **1800b35c0**(desc*, device*): dword +0: byte 0 the filter, D3D11's enum (0xff: the texture filtering
setting instead: the convar at [18062bfd8] + 0x58 clamped 0..5 indexes 180577a28, 8-byte entries {filter, log2
anisotropy}: bilinear 0x14, trilinear 0x15, then 0x55 at 2x..16x), switched through the byte table 0xb3a34 / jump
table 0xb3a10: 0 point (mag / min / mipmap all NEAREST), 0x01 / 0x04 / 0x05 / 0x10 / 0x11 / 0x14 / 0x15 the linear
mixes (mag +0x14, min +0x18, mipmap +0x1c), 0x55 / 0xd5 anisotropic; bits 16-18 / 19-21 / 22-24 the U / V / W address
modes through the table at 568240 ({0, 1, 2, 3, 4}: VK REPEAT, MIRRORED_REPEAT, CLAMP_TO_EDGE, CLAMP_TO_BORDER,
MIRROR_CLAMP_TO_EDGE); bits 25-27 the log2 anisotropy (or the setting's with dword +8 bit 13); byte 1 x 0.0625 the
mip LOD bias (negated with dword +8 bit 14; + the device's bias (vfn 0x588 of 1805c8840) when +8 bit 12 and not a
comparison filter); a filter of 0x55 / 0xd5 enables anisotropy, its max min(1 << n, the device's +0x240). So 0:
point sampling, REPEAT on both axes, no bias, no anisotropy: the shader's own 3 x 3 taps are its anti-aliasing.
Ported: crosshair-gl.js (NEAREST, REPEAT), crosshair-raster.js sample (the texel under (u, v), wrapped; the tap
coordinates in f32 in the shader's order). GPU against CPU (120 labels, 6 sizes, every glyph): 290,086 of 290,126
pixels within 1 / 255; the other 40 are taps exactly on a texel boundary (a 33 px label's centre column), which the
GPU's own coordinate rounding decides (vendor-specific in CS2 as well).
Left (TODO(trace)): powf (its one use is the colour linearisation, 1 ulp on ~0.02% of inputs: no 8-bit output can
show it); the line-up's GPU cost (unmeasured: docs/CLIENT_PERF.md item 88b says how to measure it).

## Convar defaults (client.dll 2026-11-12)

tools/re/game/cvardefs.py <dll> <names file> <out.json> decodes many registrations at once (cvardump.py prints one's raw
stores). Each registration is its own static initializer: `lea rdx, "name"; lea rcx, [handle]; call ctor`.
- int / bool form, ctor 1819a6e40: a setup struct on the stack, [rsp+0x35] a word of has-min (0x01) / has-max
  (0x100), [rsp+0x37] default, [rsp+0x47] min, [rsp+0x57] max; r8d flags, r9 help.
- float form, ctor 18015a620: builder 180765060 (xmm1 = min) then 180765050 (xmm1 = max), default in xmm2 (set before
  or after the name's lea), r9d flags.
- the handle's +8 is the convar's value block; the value sits at block + 0x58 (as 180daf640 reads the ironsight pair).
- a `lea rdx, "name"` + ctor 1819a6010 is a lookup of another DLL's convar (volume, fps_max, snd_voipvolume ...): no
  default here, read them in engine2 / soundsystem.

The crosshair family it gave (crosshair-cvars.js holds them with their help text): cl_crosshairstyle 7 [0, 9];
cl_crosshaircolor_r/g/b/a 0 / 255 / 0 / 255; cl_crosshair_drawoutline 1 [0, 2]; cl_crosshairoutline_r/g/b/a 0 / 0 / 0 /
255; cl_crosshair_thickness 2 [0, 32]; cl_crosshairdot false; cl_crosshair_length 8 [0, 255]; cl_crosshair_gap 4
[-3840, 3840]; cl_crosshair_dynamic_spread_limit 255 [0, 255]; cl_crosshair_dynamic_splitdist 3 [0, 127];
innermod 0 [0, 1]; outermod 1 [0.3, 1]; maxdist_splitratio 1 [0, 1]; cl_crosshair_t false; cl_crosshair_recoil true;
cl_crosshair_screen_height 1080 [240, -] (site 1800fc580, flags 0x8098, "The res at which the user authored their
size settings at - changes whenever a size setting is updated"); cl_ironsight_usecrosshaircolor false;
cl_ironsight_dot_scale 1 [0.1, 2]; cl_crosshair_friendly_warning 1 [0, 1]; cl_show_observer_crosshair 2;
cl_observed_bot_crosshair 2; cl_grenadecrosshair_keepusercrosshair true; cl_grenadecrosshair_<flash / explosive / fire
/ smoke / decoy> true, their delays 2 [0, 5]; cl_sniper_delay_unscope false; cl_sniper_show_inaccuracy true;
cl_sniper_auto_rezoom true; cl_crosshair_sniper_width 1. Also: sensitivity 1.25 [0.0001, 8] and zoom_sensitivity_ratio
1 [0.01, 3] (as mouse.md / zoom-view.js had them: the tool's check), hud_scaling 1 [0.9, 1.1], cl_radar_scale 0.7
[0.25, 1], cl_hud_radar_background_alpha 0.627, the music volumes (snd_menumusic_volume 0.04, snd_roundend_volume
0.16, snd_mvp_volume 0.16, snd_roundstart_volume_casual 0.0225 ...). Unresolved here (other DLLs): fps_max,
fps_max_ui, sound_device_override, snd_spatialize_lerp, snd_steamaudio_enable_perspective_correction,
snd_mute_losefocus, snd_voipvolume, voice_device_override, voice_always_sample_mic, con_enable, rate,
install_dlc_workshoptools, thread_pool_option, lobby_default_privacy_bits, cl_hud_telemetry_net_misdelivery_poor.
