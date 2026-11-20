# Settings menu, crosshair codes and drawing, convar defaults

client_20261015 (crosshair code, drawing), client_20261112 (convar registrations), tier0_20261015, rendersystemvulkan_20261015; pak01 of the 2026-11-12 install (layouts: layout/settings/*.xml, scripts/settingsmenu_crosshair.ts, scripts/common/promoted_settings.ts, mainmenu.vcss, settings.vcss, settings_slider.vcss, csgostyles.vcss, resource/csgo_english.txt; game/core's panorama_english.txt, keybindings_english.txt, core/panorama/styles/*.css); the csgo_crosshair shader, materials/dev/csgo_crosshair.vmat.

## Functions

| Address | Module | What |
|---|---|---|
| 1800fb070 | client | registers console command `apply_crosshair_code` -> 180dc2c40 |
| 180dc2c40 | client | apply_crosshair_code: argc == 2; 180daf640 (parse), 180daf490 (record -> struct, its +0x40 preset 1.0), 180dbca70 (rescale), 180dbafb0 (set convars) |
| 181092ba0 | client | registers MyPersonaAPI GetCrosshairCode / BApplyCrosshairCode / BValidateCrosshairCode (scripts/popups/popup_crosshair_code.ts) |
| 180bd3c70 | client | classic share code -> 18 bytes |
| 180daf640 | client | parse -> 32-byte record |
| 180dab5d0 | client | record checksum: sum(record[1..31]) & 0xff |
| 180daf490 | client | record -> float struct S (0x44 bytes) |
| 180dbca70 | client | rescale to the screen height |
| 180b80220 | client | the screen height (unread) |
| 1801b9c30 / 18015a010 | client | maxss / minss |
| 180dbafb0 | client | S -> convars (handles in .data 1825c84e8..1825c86f8) |
| 180da8b00 / 180daa8d0 / 180da0610 / 180dc0420 | client | settings size-edit paths: call 180dbca70 + 180dbafb0 |
| 180da0610 | client | build the crosshair's shape list each frame (callers 180db8e80 the HUD, 1811d3100 the settings preview) |
| 180c7be40 | client | +0x48 / +0x4c / +0x50: inaccuracy / accuracy penalty / spread |
| 1807cc690 | client | interpolated var's value at the frame |
| 18080d490 | client | weapon vfn 0xbd0: vdata m_flSpread[m_weaponMode] |
| 18093c760 | client | eye and forward / right / up |
| 180da17d0 | client | NDC -> pixels: x = (ndc + 1) / 2 W, y = H - (ndc + 1) / 2 H |
| 181740910 | client | AngleVectors (deg x f32 0.017453292) |
| 180c74ec0 | client | pawn vfn 0x570: eye angles |
| 180853a60 / 18084d8b0 | client | aim punch / the aim punch services' (aim-punch.md) |
| 180db0230 | client | struct from the convars |
| 180db03f0 | client | struct from the observed player's code |
| 180d9e560 | client | spread in pixels |
| 180c19db0 -> 180c19cd0 | client | world -> screen with the view-projection |
| 180d9e770 | client | the gap's soft clamp |
| 180da61c0 | client | arc (type 2) |
| 180da7510 | client | the dot |
| 180da63f0 | client | style 0 / 4 bars (T, gap, len, t) |
| 180da6290 | client | style 1 circle (r, t) |
| 180da66c0 | client | style 2 classic |
| 180da6a80 | client | style 3 circle at max(1, gap) |
| 180da6ae0 | client | style 4 bars at max(0, gap) |
| 180da6b60 | client | style 5 legacy |
| 180da6e30 | client | style 6 the dot (unless drawn) |
| 180da6e60 | client | style 7 dynamic quadrant |
| 180da7110 | client | style 8 square |
| 180da7390 | client | style 9 quadrant |
| 180da10c0 | client | split a thickness |
| 180da8410 | client | box (x0, y0, x1 - 1, y1 - 1, type 0) |
| 180da6080 | client | ring (type 1, centre - 0.5) |
| 180219ae0 | client | GetAbsVelocity |
| 180817b50 | client | weapon deploying test |
| 1807cb860 | client | vfn 0xa58: m_iClip1 (+0x1928) |
| 1807ccfb0 | client | vfn 0xb80: m_flRecoilMagnitude (vdata +0x7a0) |
| 18174a050 | client | 0-255 sRGB -> linear floats (0.04045, 12.92, V_powf((c + 0.055) / 1.055, 2.4)), alpha / 255 |
| 180da7770 | client | the grenade line-up crosshair |
| 180d568d0 / 180d56790 | client | HUD state (+0x1c0 of 180d56790's object) |
| 1808cc9c0 | client | active weapon |
| 1819fc50c | client | dynamic cast (1823139c8 / 1823139a0) |
| 1807d62d0 | client | grenade line-up shown |
| 18173d3d0 | client | bias: x / ((1 / b - 2) (1 - x) + 1), x clamped [0, 1], b [FLT_MIN, 1] |
| 180941fa0 | client | owner pawn |
| 18075d250 / 18015c5e0 | client | the entity's time / the difference |
| 180c7c3d0 | client | MapAnNodeManager object (+0x50 node count) |
| 1800e6a30 | client | registers the MapAnNodeManager game system (singleton 182570a80) |
| 180160b10 | client | float cvar read |
| 180828000 | client | m_flAttackHoldStartTime update (from PreThink) |
| 180c905e0 | client | pawn PreThink (vfn 0xa00; called by 180a70de0 before the movement; PostThink vfn 0xa08 runs ItemPostFrame) |
| 180a70de0 | client | movement services' command |
| 18094d9e0 | client | attack / attack2 held (weapon vfn 0xad0 -> movement services' buttons) |
| 180808c40 | client | Deploy: zeroes it, sets m_bWaitForNoAttack |
| 180817f20 | client | CCSWeaponBase::ItemPostFrame (no-attack branch +0x3f6: clears m_bWaitForNoAttack and m_iShotsFired) |
| 1807de430 | client | StartGrenadeThrow (sets m_bThrowAnimating) |
| 1807c93d0 | client | the grenade's Deploy (clears it) |
| 1807d7f70 | client | grenade vfn 0xd18 activity finished: 200 (the pull) -> 0xc9; 0xca (the throw) -> m_bThrowAnimating 0, then activity 0x1b (the draw) |
| 1808212a0 | client | calls vfn 0xd18 on WPN_ACTION_COMPLETE |
| 180910e60 | client | walks the anim graph's tags (token 182535718 sets +0x2b4; 182535728 / 182535730 for action kinds 2 / 3 at +0x2c4) |
| 18015a140 | client | VectorNormalize: len = sqrtss((y y + z z) + x x), x 1 / len between 1e-17 and 1e17; 0: zero vector |
| 180076490 | engine2 | CEngineClient vfn 0x2c0: width / height in f32 unless the convar at 18069be10 is over 0 |
| 180da7640 | client | glyph (x, y, w, h, glyph, colour): type 3 |
| 180dab650 | client | friendly flag + draw byte: the 2 bytes 180dbdc10 last pushed (DAT_1825c8bf8) if Plat_FloatTime - its stamp <= 0.5 |
| 180dbdc10 | client | push the friendly bytes |
| 180eaf7c0 | client | CCSGOHudTargetID: pushes (draw, sameteam && cl_crosshair_friendly_warning) each frame |
| 180eb4260 -> 180eb5b50 | client | (target, observing == 0) |
| 180c7bbf0 | client | the target |
| 1808d9290 / 1808d9120 | client | is an enemy of your team / a player isn't an enemy |
| 180ce2420 | client | spectator tools (force_spectator_only_tools) |
| 180c9ae90 | client | C_CSPlayerPawn target ID each frame (c_cs_player_pawn.cpp:0x1168) |
| 180c0d980 | client | screen fade (-1) vfn 0x18 |
| 180200f20 | client | TraceLine |
| 1809dd600 / 1809ea740 | client | ignore the pawn |
| 180352920 / 180aca060 | client | filter (0xc3003, group 4) |
| 180a7f1b0 / 180a83a50 | client | player list walk |
| 18174cfb0 | client | point-to-line distance |
| 180a1aa70 | client | ClipRayToEntity (a line ray) |
| 1807cd7f0 | client | smoke along a line (each smoke that did its effect +0x1364, grid +0x13b8 walked by 1807de9d0 with the summing visitor 181bd3c70, x the age weight from +0x13c4) |
| 180c9ec60 | client | keeps pawn +0x36f8 m_iTargetedWeaponEntIndex |
| 1800b35c0 | rendersystemvulkan | VkSamplerCreateInfo (sType 31) from a packed sampler description (desc*, device*) |
| 1805c8840 | rendersystemvulkan | device (vfn 0x588 its LOD bias) |

### tier0

| Address | What |
|---|---|
| 180008240 | V_sincosf (sinf then cosf) |
| 180008280 / 180008300 / 180007ef0 | V_sinf / V_tanf / V_atanf |
| 180007f90 / 1800081a0 / 1800081c0 | V_expf / V_powf / V_roundf (-> 1802a9ebc CRT roundf, half away from zero) |
| 1802e6570 / 1802e0d70 / 1802e7e90 | CRT sinf / cosf / tanf (SSE2) |
| 1802e057c / 1802e1ec0 / 1802e5130 | atanf / expf / powf |
| 1802e6910 / 1802e1050 / 1802e8200 / 1802e2030 | FMA paths: sinf / cosf / tanf / expf |
| 1803ab28c | FMA3 flag (set at start-up) |
| 1802e9830 | Payne-Hanek, sinf SSE2 >= 1.6e7 (table 1803404a0) |
| 1802e9290 | Payne-Hanek, cosf SSE2 >= 500000 |
| 1802e8e80 | cosf FMA >= 3373259520 |
| 1802e9478 | expf underflow |
| 1802e96d4 | powf special cases |

## Fields

| Offset | Field |
|---|---|
| object +0 | shape list (64 entries of 0x40 + count at +0x1008: CrosshairParamBuffer_t) |
| +8 | the legacy style's state (+4 feedback, +8 shot count seen) |
| +0x10 / +0x1c / +0x28 / +0x34 | eye / forward / right / up (all zero with no pawn) |
| +0x40 / +0x44 | cx / cy |
| +0x48 / +0x4c / +0x50 | m_flInterpolatedInaccuracy (pawn +0x1f50) / m_fAccuracyPenalty (weapon +0x1a18) / spread |
| +0x54 | pawn FOV (vfn 0x118; 90 with no pawn) |
| +0x58 | screen height / 1080 |
| +0x5c / +0x5d | preview flag / Dynamic Preview |
| +0x60 | the struct S (+0x68 = cl_crosshair_recoil; +0x87 / +0x8b colour / outline alpha) |
| +0xa4 / +0xa8 | centre |
| +0xac / +0xb0 | resting spread (style 7) / spread in pixels |
| +0xb4 / +0xb8 | dynamic gap / alpha multiplier |
| +0xbc | grenade line-up fade |
| weapon vdata +0x750, weapon +0x1a00 | m_flSpread / m_weaponMode |
| weapon +0x1a40 / vdata +0x7c4 | m_nDeployTick / m_flDeployDuration |
| pawn +0x1eb0 | m_iShotsFired |
| pawn +0x3f4 | m_fFlags |
| controller +0x6cc | split-screen slot (pawn vfn 0x998) |
| kbutton_t "attack" 182233ea0 / "attack2" 182233f30 | +0x32 + slot x 0x1c |
| grenade +0x1f25 | m_bThrowAnimating |
| weapon +0x1a44 | m_flAttackHoldStartTime |
| pawn +0x1ebc | m_bWaitForNoAttack |
| movement services +0x50 / +0x58 | m_nButtons / down states |
| param_2 +0 / +4 | panel centre (floor(w / 2 + x), floor(h / 2 + y)) |
| param_2 +8 / +0xc / +0xd / +0xe | screen height / 1080 / friendly flag / 0 / 1 |
| pawn +0x14fc / +0x1504 | m_flFlashBangTime / m_flFlashOverlayAlpha |
| pawn +0x36dc / +0x36e0 | m_iIDEntIndex (client-only) / m_delayTargetIDTimer |
| pawn +0x36fc / +0x3700 | m_iOldIDEntIndex / m_holdTargetIDTimer |
| identity +0x30 bit 7 | dormant |
| view render +0x1cd0 | aspect (vfn 0x88) |
| 18256b020 + slot x 0x40 | view-projection (engine vfn 0x310 the slot; W / H vfn 0x1e8) |

### The 32-byte record

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

The style and outline slots are ints (the decompiler shows float casts; the stores are ints: 5, not 7e-45). The new-format clamps are only on that branch; the classic branch returns its converted record unclamped.

## Checked against the DLL

- 180daf490 and 180dbca70 under Unicorn (tools/re/game/xhair_oracle.py: V_roundf and _V_StringAfterPrefixCaseSensitive stubbed, 180b80220 returning the case's height, the two ironsight value blocks pointed at the case's values) over 608 codes (classic versions 0-6, right and wrong checksums, new codes with noise and plausible fields, bad digits, overflow): every field and the rescale bit-exact, 437 valid.
- The style functions under Unicorn (xhair_draw_oracle.py): 600 crosshairs, 1623 shapes equal.
- 180d9e560 through the real 180c19db0 / 180c19cd0 / 180da17d0 and 181740910 under Unicorn (xhair_proj_oracle.py): 500 random views, every spread, centre and forward equal.
- 180da7770 under Unicorn with tier0's maths (xhair_lineup_oracle.py): 300 views, 9842 shapes equal. The oracles run the real tier0 under Unicorn (tier0_link.py: relocated to 0x260000000, the client's imports pointed at it), so they take tier0's SSE2 path.
- tier0's maths bit for bit, 20000 inputs each (6% huge): the SSE2 path against tier0 under Unicorn (tier0_trig_oracle.py), the FMA path against tier0 called natively on an FMA3 CPU (tier0_native.py: the flag read back is 1).
- The shader against a CPU rasteriser of the same maths: 149 random crosshairs, 782,296 pixels within 1 / 255 (before types 3 / 4); 120 labels, 6 sizes, every glyph: 290,086 of 290,126 pixels within 1 / 255, the other 40 taps exactly on a texel boundary (a 33 px label's centre column).
- Not checked: 180da0610's own arithmetic between those calls (from the disassembly), the friendly icon's rect, 180c9ae90's timers (from the decompile), the shader's float ops (the decompiled SPIR-V).

## Constants

| Value | What |
|---|---|
| 181c75400 | alphabet "ABCDEFGHJKLMNOPQRSTUVWXYZabcdefhijkmnopqrstuvwxyz23456789" (57; no I, O, g, l, 0, 1) |
| 34 (0x22) | classic code length; "CSGO-" prefix, '-' at 10, 16, 22, 28 |
| 46 (0x2e), "CS" (181cb5ec8) | new code length, prefix |
| 1825c86f0 / 1825c8700 (+0x58) | cl_ironsight_usecrosshaircolor / cl_ironsight_dot_scale value blocks |
| maxss 0.1 at 181ada28c, minss 2.0 at 181ac6078, 0.05 at 181ac606c, 0.01 at 181ada280 | classic conversion constants |
| "CSGO-y9Qw8-sCzPb-jORFu-ov6L8-GwMXL" | a bot's default crosshair code |
| weapon_debug_spread_show | 1825c8530, default 0, flags 0xc008, "Draws the current weapon's true inaccuracy + spread radius around the crosshair" |
| cl_grenadecrosshair_keepusercrosshair | 1825c8500 |
| cl_grenadecrosshair_<explosive / flash / fire / decoy / smoke> | 1824c72d8 / 1824c72c8 / 1824c72a8 / 1824c72e8 / 1824c72b8 |
| cl_grenadecrosshairdelay_<same order> | 1824c7320 / 1824c7310 / 1824c72f0 / 1824c7330 / 1824c7300 |
| cl_crosshaircolor_r / g / b / a | 1825c85d0 / 1825c85e0 / 1825c85f0, 1825c8600 |
| cl_grenadecrosshair_tickscaling | 1825c8510, 1.1 [0.5, 2] |
| cl_grenadecrosshair_ticklabels | 1825c8520, byte, default 1 |
| cl_crosshair_friendly_warning | 1825c8690 |
| hud_showtargetid | 182579018, 1 |
| force_spectator_only_tools | 18257b360 |
| mp_playerid / mp_playerid_delay / mp_playerid_hold | 1824bc5d0 (0) / 1824bc5e0 (0.4) / 1824bc5f0 (0.1) |
| 0.0872664600610733 | half of 10 degrees (V_sincosf) |
| 0.008726646 / 114.59155 | deg -> half-angle rad / rad -> 2 deg |
| 18236fa60 | identity quaternion |
| 0x3300a5ff | friendly icon colour (r ff, g a5, b 00, a 0x33) |
| 2000 | eye-to-point distance on screen |
| 2500, 10, 72, 60 | target ID trace length / start offset / extension / player distance |
| 0xc3003, group 3, flags 0x49 | target ID trace |
| 64 | shape cap (a 65th add is dropped) |

## Crosshair codes

- Classic (180bd3c70): the 25 digits read last to first, each `n = n * 57 + digit` into an 18-byte big-endian buffer (fails on a digit outside the alphabet or a carry out of byte 0; the multiply and the add are two passes, same result); out bytes 0..7, 8..15, 16..17 in order.
- Parse (180daf640), classic branch: `byte0 == sum(bytes 1..15) & 0xff` (16, 17 not summed), byte1 (version) >= 3 (else "Invalid or old crosshair code"), converted (below).
- New: the 44 digits last to first into 32 limbs (fail on a limb over 0xff), record[0] most significant; record[1] == 1, the u16 at 2 != 0, record[0] == 180dab5d0's checksum; then clamped.
- Rescale (180dbca70): h = 180b80220(); S0 == h: no change; S0 > 0: `k = h / S0` (f32), `gap = roundf(k * gap)` then max(1, .) if gap > 0 / min(-1, .) if < 0; length, thickness, spread limit, split distance: if > 0, `max(1, roundf(v * k))`; S0 = h.

Classic M (18 bytes) -> record:

1. `u = M[10..13]` as a little-endian u32; version 3: `u = ((M[2] & 0x20) << 23) | (u & 0xcfffffff)`.
2. `record[2..3] = M[14..15]`; `record[4] = ((M[2] & 0x10) << 1) | (M[2] & 0xcf)`; `record[5..8] = M[3..6]`; outline = (0, 0, 0, M[6]).
3. `record[13] = ((u >> 23) & 0x1f) | (((u >> 28) << 6) & 0xff)`; gap = M[7] zero-extended (movzx: never negative); record[16] = M[8], [17] = M[9].
4. D bits 0-6 = `u & 0x7f`; bits 7-13 = `trunc(roundf((((u >> 7) & 0x1f) * 0.05f) / 0.01f))`; bits 14-20 = `trunc(roundf((((u >> 12) & 0xf) * 0.05f) / 0.01f))`, `D &= 0xf01fffff`; bits 21-27 = `(u & 0x7f0000) << 5`; bit 28 = the current cl_ironsight_usecrosshaircolor.
5. `record[22] = trunc(roundf((clamp(current cl_ironsight_dot_scale, 0.1, 2) - 0.1f) / 0.01f))`; record[1] = 1, record[0] = the checksum.

## The crosshair's drawing (180da0610, csgo_crosshair)

- The struct: from the convars (180db0230) or, spectating, the observed player's code (180db03f0: cl_show_observer_crosshair, cl_observed_bot_crosshair), then 180dbca70 to this screen's height (written back to the convars when it changed).
- Centre: truncf of the view's centre (180da17d0); moved to the aim punch's point when cl_crosshair_recoil, a pawn, not the preview: forward (181740910) of the eye angles + the aim punch, 2000 u from the eye, on screen: a coordinate whose ceil is over 1 px from the panel's centre replaces it, truncf.
- Spread (180d9e560): `d = forward - right x (inaccuracy + spread)` (f32), `|d|` as `sqrt((z z + y y) + x x)`, `d / |d|`, `2000 d + eye` on screen, its distance from `forward x 2000 + eye`'s (`(dz dz + dy dy) + dx dx`), V_roundf.
- On screen (180c19cd0): `x = ((m1 p1 + m0 p0) + m2 p2) + m3`, `y = ((m4 p0 + m5 p1) + m6 p2) + m7`, `w = ((m12 p0 + m13 p1) + m14 p2) + m15`; w < 0.001: x 100000, else / w; then `((x + 1) 0.5) W`, `H - ((y + 1) 0.5) H`.
- Dynamic values (styles 0, 1, 7, or weapon_debug_spread_show): `L = spread limit + 64`; gap = 180d9e770 (f32: `x <= lo = 0.75 L`: x; else `L - V_expf(-(1 / (L - lo)) (x - lo)) (L - lo)`), at most L, at least the thickness with the dot on, truncf; `alpha = 1 - 0.8 clamp((x - x0) / (0.25 - x0))`, `x0 = +0x50 + +0x4c` (0.2 when x0 == 0.25f and x >= 0.25). Preview: `x = |V_sinf((float)Plat_FloatTime())| 0.1` while Dynamic Preview runs, else `+0x48 + +0x50`.
- weapon_debug_spread_show ends the frame with 180da61c0 at the centre: radius spread + 2, width 2, 30 degrees, rgba fa fa 32 ff, outline black (1, 1).
- cl_grenadecrosshair_keepusercrosshair 0: `k = 1 - +0xbc` (at least 0; 0 returns before the struct is read), colour and outline alphas x k, (int) truncated.
- The list's order: the friendly icon, the line-up, then the user's crosshair: the dot first (180da7510, cl_crosshairdot), then by style.

### Styles

| Style | Function | Draws |
|---|---|---|
| 0 | 180da63f0 | bars at the dynamic gap, alpha x +0xb8 |
| 1 | 180da6290 | circle at the dynamic gap |
| 2 | 180da66c0 | classic |
| 3 | 180da6a80 | circle at max(1, gap) |
| 4 | 180da6ae0 | bars at max(0, gap) |
| 5 | 180da6b60 | legacy |
| 6 | 180da6e30 | the dot (unless already drawn) |
| 7 | 180da6e60 | dynamic quadrant |
| 8 | 180da7110 | square |
| 9 | 180da7390 | quadrant |

- Thickness split (180da10c0): `n = max(1, cvtss2si(t))` (ties to even), `lo = (n + 1) / 2`, `hi = n - lo`, even = lo == hi.
- Bars (180da63f0)(T, gap, len, t): `g = max(0, gap)`; left `[floor(cx - g) - len, floor(cx - g)) x [cy - lo, cy + hi)`, right from `ceil(cx + g) + (even ? 0 : -1)`, top `[floor(cy - g - len), + len)` (not with T), bottom from `ceil(cy + g) + (even ? 0 : -1)`.
- Circle (180da6290)(r, t): a ring at the centre minus (even ? 0 : 0.5), radius r + t, width max(1, t - 1).
- Square (180da7110): `x0 = floor(cx - g - t + n)`, `x1 = floor(cx + g)` (n = -1 with the dot on an odd thickness), the same in y; boxes top (x0, y0)-(x1, y0 + t), bottom (x0, y1)-(x1, y1 + t), left (x0, y0)-(x0 + t, y1 + t), right (x1, y0)-(x1 + t, y1 + t).
- Quadrant (180da7390): arcs at the centre minus (t >= 1 and odd ? 0.5 : 0), radius max(1, gap) + t, width t, clamp(cl_crosshair_dynamic_maxdist_splitratio, 0, 1) x 90 degrees.
- Dynamic quadrant (180da6e60): with a spread: the ring (width max(1, t - 1), radius it + the dynamic gap) while the spread is under 100 px and within 10 of the resting one, else arcs (radius t + dynamic gap) `45 - 40 clamp((+0x48 - +0x4c) / (0.2 - +0x4c))` degrees wide (45 / 5 when +0x4c == 0.2f); colours x +0xb8; then the bars at max(0, gap) unscaled.
- Classic (180da66c0): `x = (+0x48 + +0x50) 320 / V_tanf(fov / 2)` (preview: `+0x50 = max(0, V_sinf(t) 0.15)`, fov 90); `g1 = roundf(H / 480 x)`, `g2 = roundf(H / 480 min(x, split distance))`; g1 > 0: outer gap = gap + g1, inner = max(0, gap + g2); else `trunc((c + gap) - 4)` with c = 4 (no pawn), else by m_fFlags: 8 without FL_ONGROUND, 2 with FL_DUCKING, else 6 above 100 u/s, else 4. Past the split distance: bars at `(ceil((1 - ratio) len) + outer gap)` of length `floor(len ratio)`, alpha x outermod (cvttss2si), then bars at the inner gap of length `ceil((1 - ratio) len)`, alpha x innermod; else bars at the outer gap, full alpha (disassembly 180da6900-6a30: the decompiler drops the second call's arguments).
- Legacy (180da6b60): not the preview, a pawn and a weapon: unless deploying (180817b50: `now - m_nDeployTick <= (uint)(m_flDeployDuration x 64 + 0.5)`) with m_iShotsFired 0 (then both reset to 0), m_iShotsFired over the count, attack or attack2 down for the controller's slot and m_iClip1 >= 0: adds `(int) m_flRecoilMagnitude[mode] / 3.5`; the count then follows m_iShotsFired. Preview: +15 every RandomFloat(0, 0.6) s. Clamped [0, 25], then minus 42 x frametime; bars at `roundf(max(0, gap) + H x feedback / 1200)`.
- Colours: 18174a050.

### The grenade line-up crosshair (180da0610 +0x124..0x1c7, 180da7770)

1. When the HUD state 180d568d0 is not 3 or 4, the active weapon cast to the grenade class and 1807d62d0 says so: a start time (the object's +8 pointer's float) set to Plat_FloatTime when 0, `+0xbc = 18173d3d0(min(1, (now - start) / 0.2), 0.2)`, then 180da7770; else start and +0xbc are 0.
2. 1807d62d0: owner pawn; not m_bThrowAnimating; `elapsed = curtime - m_flAttackHoldStartTime` when set, else 0; elapsed > 0; the type (vfn 0xd58: 0 explosive, 1 flash, 2 fire, 3 decoy, 4 smoke) picks cl_grenadecrosshair_<type> (off: false; smoke off still passes when the MapAnNodeManager has nodes: map annotations loaded) and cl_grenadecrosshairdelay_<type>: shown when `0 <= delay <= elapsed`.
3. m_flAttackHoldStartTime (180828000 from PreThink): attack or attack2 (0x801) held and m_bWaitForNoAttack (as the last command left it) clear -> now if it was 0; else 0. Deploy zeroes it and sets m_bWaitForNoAttack; ItemPostFrame's no-attack branch clears m_bWaitForNoAttack and m_iShotsFired. So the line-up shows once the pin has been held past the delay (2 s by default), from a fresh press.
4. m_bThrowAnimating: set by StartGrenadeThrow, cleared by the grenade's Deploy and by 1807d7f70 (on WPN_ACTION_COMPLETE that update).
5. 180da7770 colour: cl_crosshaircolor_r / g / b each clamped [0, 255], alpha cl_crosshaircolor_a clamped, x +0xbc, V_roundf, (char) cvttss2si.
6. Ticks: the forward vector turned step by step by a quaternion about the view's up (+0x34) and about its right (+0x28): the axis normalised (18015a140), `q = (axis x s, c)` from V_sincosf(0.0872664600610733) (zero axis: identity). SIMD lanes: `t = 2 (v.zxy q.yzx - v.yzx q.zxy)`, `v' = (t.zxy q.yzx - t.yzx q.zxy) + (v + w t)`; each step's `v' x 2000 + eye` on screen (180c19db0, 180da17d0), kept in a CUtlVector (UtlVectorMemory_*). Counts: across `floor(atan(aspect tan(fov x 0.008726646)) x 114.59155 x 0.5 / 10)` (V_tanf, V_atanf; the aspect the view render's vfn 0x88: +0x1cd0, set from engine2's CEngineClient vfn 0x2c0, 180076490), up `floor(fov x 0.5 / 10)`.
7. Sizes from +0x58 (s = screen height / 1080): label `h = floorf(s 20)`, `w = floorf(h 1.28)`; `s' = floor(s)` when s >= 1; `n = max(1, cvtss2si(s' + s'))`, `a = (n + 1) / 2` above, `b = n - a` below (floats fa, fb).
8. Boxes (180da8410, outline colour 0, outline (0, 0)): (0, cy - fa)-(cx + cx, fb + cy) and (cx - fa, 0)-(fb + cx, cy + cy); per across point `x = floorf(px)`: (x - fa, cy - L)-(x + fb, L + cy), its mirror at `(cx - x) + cx`; per up point `y = floorf(py)`: (cx - L, y - fa)-(cx + L, y + fb) and its mirror `(cy - y) + cy`. L starts at 10 for each set and becomes `floorf(L x cl_grenadecrosshair_tickscaling)` after each tick pair.
9. Labels (cl_grenadecrosshair_ticklabels; 180da7640, type 3, the colour as 180da8410's): the rect (x, y)-(x + w - 1, y + h - 1), +0x10 = (float) glyph; glyph 0x7fffffff: none. Across: `x = floorf(((x - fa) + (x + fb) - w) 0.5)`, `y = (L + cy) + 2`; up: `x = (cx + L) + 2`, `y = floorf(((y - fa) + (y + fb) - h) 0.5)`. Glyph for the k-th tick (k 1..5 only): across `(5 - k) 4` for the computed side (counter -1, -2 ..), + 1 for the mirror (+1, +2 ..); up `22 - 4 k`, + 1 for the mirror: atlas cells "-kx" / "kx" / "-ky" / "ky" (grenade_crosshair_numerals: 4 columns of 64 x 50 texels, rows -5 .. -1 top to bottom).

### The friendly warning (180da0610 +0x92)

- With the flag: `half = V_roundf(+0x58 x 28) x 0.5`, a type 4 shape (cx - half, cy - half)-(half + cx - 1, half + cy - 1), colour 0x3300a5ff through 18174a050, outline 0.
- The flag: 180eb5b50: the target (180c7bbf0) a living player pawn (vfns 0x4f0, 0xab8, 0x4e8) not an enemy (1808d9290 false: "#Panorama_HUD_playerid_sameteam") keeps it; an enemy clears it. Gates: hud_showtargetid; not flashed: m_flFlashBangTime more than 0.5 s ahead of curtime hides the target unless 180ce2420; m_flFlashOverlayAlpha >= 0.7 only picks "#SFUIHUD_targetid_FLASHED" (observer mode 2).
- 180c7bbf0: once m_delayTargetIDTimer elapsed: m_iIDEntIndex, else (-1) m_iOldIDEntIndex while m_holdTargetIDTimer runs.
- 180c9ae90 each frame:
  1. m_iIDEntIndex = -1; mp_playerid 2: done; a screen fade over 75 with this pawn the local / observed one: done.
  2. Camera services vfn 0x108 (eye, angles), AngleVectors; TraceLine 180200f20 from eye + 10 fwd to eye + 2500 fwd (0xc3003, group 3, flags 0x49, the pawn ignored), the nearest hit.
  3. No hit: filter 180352920 + 180aca060, UTIL_ClipTraceToPlayers(start, the line's end + 72 forward, filter, trace, 0, 60, |end - start| / |new end - start|): each player alive (vfn 0x4e8), not dormant, not the filter's two ignored handles, whose centre (vfn 0x2b0) lies 0..60 u from the line (18174cfb0), clipped by ClipRayToEntity (180a1aa70, a line ray); a fraction under the given one (the first line's own end) replaces the trace. (Every player's box is already in the first line's world: it can only find what that line found.)
  4. A hit entity not this pawn (and of its team when mp_playerid is 1), its centre not behind smoke (1807cd7f0 <= 0): a new index starts m_delayTargetIDTimer at mp_playerid_delay (0 for a player 1808d9120 says isn't an enemy); m_iIDEntIndex and m_iOldIDEntIndex = it, m_holdTargetIDTimer = mp_playerid_hold.
- m_iIDEntIndex is client-only (no server.dll field).

### The csgo_crosshair shader

One static combo; the vertex shader passes a quad's screen position and a 64-bit mask of the shapes covering it. Per pixel (gl_FragCoord minus the panel's offset, as ints), for each masked shape, (outline, fill) coverage:

- Type 0: fill inside [x0, z] x [y0, w] inclusive, outline inside it grown by o.x left / top and o.y right / bottom (cl_crosshair_drawoutline 1 = (1, 1), 2 "Half" = (1, 0): top and left only).
- Type 1: `d = |p - c|`, `a = atan2(dx, -dy)`, `t = max(smoothstep(0, pi / 2, a), smoothstep(-pi / 2, -pi, a))`, `fill = smoothstep(r + .5, r - .5, d) smoothstep(r - w - .5, r - w + .5, d)`, outline the same at `r + lerp(o.x, o.y, t)` and `r - w - lerp(o.y, o.x, t)`.
- Type 2: also x `smoothstep(h + (o + .5) / d, h + (o - .5) / d, q)` for the outline and `smoothstep(h + .5 / d, h - .5 / d, q)` for the fill, `q = |a - floor(a 2 / pi) pi / 2 - pi / 4|`, h = angle / 2, d >= 1.
- Types 3 / 4 (csgo_crosshair.vmat: g_tGlyphAtlas t31 grenade_crosshair_numerals, g_tFriendlyIcon t32 friendly_crosshair_icon): outside the rect nothing, else `size = max((zw - xy) + 1, 1)` and the mean of 3 x 3 SampleLevel .x taps (rows outer): type 3 at `(64, 50) (cell (g % 4, g / 4) + ((p + 0.5) - xy) / size) + ((i + 0.5) / 3 - 0.5) (64, 50) / size`, x 1 / 256; type 4 at `((p + 0.5) - xy) / size + ((i + 0.5) / 3 - 0.5) / size`. Type 3 is a fill (coverage x colour alpha) in the best-of choice; type 4 adds colour x coverage x alpha to a sum the composite adds x (1 - a) after.
- Composite: the strongest fill and the strongest outline win (>=), then `out = (lerp(outline.rgb aO, fill.rgb, F) + add (1 - a), a = lerp(aO, 1, F))`, `aO = (1 - F) outline.a` (the outline's colour weighed aO (1 - F)). CS2 writes this linear output into its sRGB target.
- Sampler: DefaultSamplerState (s15 / s16) is a render-state literal (VariableSource __RenderStateLiteral__, IntDefs 0, flags SamplerFlag4): packed description 0 = point sampling, REPEAT on both axes, no bias, no anisotropy (the 3 x 3 taps are its anti-aliasing). Taps exactly on a texel boundary are decided by the GPU's own coordinate rounding (vendor-specific).

### Packed sampler description (1800b35c0)

| Bits | What |
|---|---|
| dword +0 byte 0 | filter, D3D11's enum. 0xff: the texture filtering setting (convar at [18062bfd8] + 0x58 clamped 0..5 indexes 180577a28, 8-byte entries {filter, log2 anisotropy}: bilinear 0x14, trilinear 0x15, then 0x55 at 2x..16x). Switched through byte table 0xb3a34 / jump table 0xb3a10: 0 point (mag / min / mipmap NEAREST), 0x01 / 0x04 / 0x05 / 0x10 / 0x11 / 0x14 / 0x15 the linear mixes (mag +0x14, min +0x18, mipmap +0x1c), 0x55 / 0xd5 anisotropic (enables anisotropy, max min(1 << n, device +0x240)) |
| bits 16-18 / 19-21 / 22-24 | U / V / W address modes through the table at 568240 ({0..4}: REPEAT, MIRRORED_REPEAT, CLAMP_TO_EDGE, CLAMP_TO_BORDER, MIRROR_CLAMP_TO_EDGE) |
| bits 25-27 | log2 anisotropy (or the setting's with dword +8 bit 13) |
| byte 1 | x 0.0625 mip LOD bias (negated with dword +8 bit 14; + the device's bias (vfn 0x588) when +8 bit 12 and not a comparison filter) |

## tier0's maths (CRT, AMD libm)

Each tests 1803ab28c first: set at start-up on a CPU with FMA3, it takes the FMA path. SSE2 path, all in double from the f32 argument:

- sinf: |x| < 2^-13: x; < 2^-7: `x - ((x x) x) / 6`; <= pi / 4: `x + ((S4 x2 + S3) x4 + (S2 x2 + S1)) (x x2)` (S1..S4 = -1/6, 1/120, -1/5040, 2.7557319223985893e-06). Above, below 1.6e7: `n = (int)(|x| 2 / pi + 0.5)`, `rhead = |x| - n 1.5707963267341256`, `rtail = n 6.077100506506192e-11`, `r = rhead - rtail`; when the exponent dropped by more than 15: `t = rhead`, `rhead = t - n 6.077100506303966e-11`, `rtail = n 2.0222662487959506e-21 - ((t - rhead) - n 6.0771...e-11)`, `r = rhead - rtail`. By the first r's exponent e: e >= 0x3f2 the polynomial (sin's for n even, cos's for odd: `(-0.5 x2 + 1) + ((K4 x2 + K3) x4 + (K2 x2 + K1)) x4`, K1..K4 = 1/24, -1/720, 2.48e-05, -2.755731922398589e-07); e > 0x3de: `r - (r / 6) r2` or `1 - r2 / 2`; else r or 1; negated unless bit 1 of n equals the sign. >= 1.6e7: 1802e9830.
- cosf: the same reduction (threshold 500000, beyond: 1802e9290), the quadrants swapped, negated when (n + 1) & 2.
- tanf: |x| < 2^-27: x; < 2^-13: `((x x) x) / 3 + x`; <= pi / 4 and after one reduction step (below 8388608, beyond: an inline Payne-Hanek over the table at 1803403f0): `r + (r2 r) (T1 r2 + T0) / ((U2 r2 + U1) r2 + U0)` (T0 0.3852960712639954, T1 -0.017203248047148168, U0 1.1558882143468838, U1 -0.5139650547885454, U2 0.01844239256901656), -1 / t for odd n, the argument's sign xored in.
- expf: `t = x 92.33248261689366` (64 / ln 2); t >= 8192: inf, t < -9600: 0 (1802e9478); `n = cvtpd2dq(t)` (to nearest even), `r = x - n 0.010830424696249145`, `p = (r r) (r / 6 + 0.5) + r`, `(p T + T) 2^((n - j) >> 6)`, T = the 2^(j / 64) table at 18033e370, j = n & 63.
- Payne-Hanek (sinf SSE2 >= 1.6e7; cosf SSE2 >= 500000; tanf both paths and sinf FMA >= 16779436: inline): e = x's exponent, `off = 0x86 - (e >> 3)` into the byte table at 1803403f0 (1803404a0 the same bytes for 1802e9830), m = the mantissa with its implicit bit; the 192-bit product `m (T[off] + T[off + 8] 2^64 + T[off + 16] 2^128) mod 2^192` in words r8 / r9 / r10 (mul / adc); `s = 54 - (e & 7)`: n = r10 >> s plus the bit below it (when set: all three words complemented and the sign bit set); region = n & 3; r10 keeps its low `54 - (e & 7) - 10` bits, normalised to 53 bits with r9 / r8 shifted in (6-bit shift counts), exponent and sign packed: that double x 1.5707963267948966. cosf FMA >= 3373259520 (1802e8e80): the same words, then a double-double head: the low word as a double, the high one split at 26 bits (& 0xfffffffff8000000), x pi / 2 in three parts (1.5707963109016418 / 1.5893254712295857e-08 / 6.123233995736765e-17) with fused adds.
- FMA path: the same constants, Horner with fused steps (sin: `x + (((S4 x2 + S3) x2 + S2) x2 + S1) x^3`; sinf's cos: `fma(x2, -0.5, 1) + (((K4 x2 + K3) x2 + K2) x2 + K1) x4`; cosf's cos: `1 - x2 0.5` unfused, then the same; tan: `fma(x2 r, (T1 x2 + T0) / ((U2 x2 + U1) x2 + U0), r)`); one reduction step `n = trunc(fma(|x|, 2 / pi, 0.5))`, `r = fma(-n, p1, |x|) - n p1t` (thresholds 16779436 / 3373259520 / 3373259264, beyond them Payne-Hanek); small forms `x - (x x x) / 6`, `1 - x (x / 2)`, `(x x x) / 3 + x` fused; sinf's sign (region >= 2) xor (x < 0), cosf's (region + 1) & 2; expf `r = fma(-n, ln2 / 64, x)`, `p = fma(r2, fma(r, 1/6, 0.5), r)`, `fma(p, T, T) 2^m`.
- atanf equals JavaScript's Math.atan rounded to f32 on every input checked (both paths); powf doesn't (1 ulp on ~0.02% of inputs; its one crosshair use is 18174a050's colour linearisation, which the shader's 8-bit output can't show). powf SSE2: a packed-double log2 (the mantissa's top 8 bits rounded index an inverse table at 180305a30 and a log table at 18033c370; |x - 1| small: an atanh series 18033c300 / 18033c310) times y, then expf's table; then the special cases (negative x with integer y, zeros, infinities: 1802e96d4).

## Convar registrations

tools/re/game/cvardefs.py `<dll> <names file> <out.json>` decodes many registrations at once (cvardump.py prints one's raw stores). Each is its own static initializer: `lea rdx, "name"; lea rcx, [handle]; call ctor`.

- Int / bool, ctor 1819a6e40: a setup struct on the stack, [rsp+0x35] a word of has-min (0x01) / has-max (0x100), [rsp+0x37] default, [rsp+0x47] min, [rsp+0x57] max; r8d flags, r9 help.
- Float, ctor 18015a620: builder 180765060 (xmm1 = min) then 180765050 (xmm1 = max), default in xmm2 (set before or after the name's lea), r9d flags.
- The handle's +8 is the value block; the value at block + 0x58 (as 180daf640 reads the ironsight pair).
- `lea rdx, "name"` + ctor 1819a6010: a lookup of another DLL's convar (volume, fps_max, snd_voipvolume ...): no default here.

### Defaults (client_20261112)

| Convar | Default [min, max] |
|---|---|
| cl_crosshairstyle | 7 [0, 9] |
| cl_crosshaircolor_r/g/b/a | 0 / 255 / 0 / 255 |
| cl_crosshair_drawoutline | 1 [0, 2] |
| cl_crosshairoutline_r/g/b/a | 0 / 0 / 0 / 255 |
| cl_crosshair_thickness | 2 [0, 32] |
| cl_crosshairdot | false |
| cl_crosshair_length | 8 [0, 255] |
| cl_crosshair_gap | 4 [-3840, 3840] |
| cl_crosshair_dynamic_spread_limit | 255 [0, 255] |
| cl_crosshair_dynamic_splitdist | 3 [0, 127] |
| innermod / outermod / maxdist_splitratio | 0 [0, 1] / 1 [0.3, 1] / 1 [0, 1] |
| cl_crosshair_t / cl_crosshair_recoil | false / true |
| cl_crosshair_screen_height | 1080 [240, -] (site 1800fc580, flags 0x8098, "The res at which the user authored their size settings at - changes whenever a size setting is updated") |
| cl_ironsight_usecrosshaircolor / cl_ironsight_dot_scale | false / 1 [0.1, 2] |
| cl_crosshair_friendly_warning | 1 [0, 1] |
| cl_show_observer_crosshair / cl_observed_bot_crosshair | 2 / 2 |
| cl_grenadecrosshair_keepusercrosshair | true |
| cl_grenadecrosshair_<flash / explosive / fire / smoke / decoy> | true; delays 2 [0, 5] |
| cl_sniper_delay_unscope / cl_sniper_show_inaccuracy / cl_sniper_auto_rezoom | false / true / true |
| cl_crosshair_sniper_width | 1 |
| sensitivity / zoom_sensitivity_ratio | 1.25 [0.0001, 8] / 1 [0.01, 3] (as mouse.md has them) |
| hud_scaling | 1 [0.9, 1.1] |
| cl_radar_scale / cl_hud_radar_background_alpha | 0.7 [0.25, 1] / 0.627 |
| snd_menumusic_volume / snd_roundend_volume / snd_mvp_volume / snd_roundstart_volume_casual | 0.04 / 0.16 / 0.16 / 0.0225 ... |

In other DLLs: fps_max, fps_max_ui, sound_device_override, snd_spatialize_lerp, snd_steamaudio_enable_perspective_correction, snd_mute_losefocus, snd_voipvolume, voice_device_override, voice_always_sample_mic, con_enable, rate, install_dlc_workshoptools, thread_pool_option, lobby_default_privacy_bits, cl_hud_telemetry_net_misdelivery_poor.

## The menu (panorama)

- Tabs: layout/settings/settings.xml's nav RadioButtons (`SettingsMenu.NavigateToTab("...")`): Search (icon), Promoted ("New"), VideoSettings, AudioSettings, GameSettings, KeybdMouseSettings, CrosshairSettings (label "Crosshair / Scopes"). Files: settings_video / _audio / _game / _kbmouse / _crosshair.xml.
- Video: two sub tabs (`SettingsMenuVideo.SelectSimpleVideoSettings / SelectAdvancedVideoSettings` over `#video_settings` / `#advanced_video`) and a "HUD Edge Positions" button; the others jump buttons (`SettingsMenuShared.ScrollToId('<section id>')`).
- Sections: `.SettingsBackground`, title `.SettingsSectionTitleLabel`; rows in document order: `CSGOSettingsSlider` (text, convar, min, max, percentage, invert, value100percent, displayprecision, step, toggleconvar, audiogain, eventname), `CSGOSettingsEnumDropDown` / `CCSGOSettingsEnumDropDownBind` (convar or bindkey, Label children = options with `value`, label = the row container's other Label), `CSGOSettingsKeyBinder` (bind), buttons, free text, custom panels (CSGOAudioMeter, CSGOFrameTimeSlider, MapGraphicsSettingsPanel, CSGOCrosshairPreview), the colour rows (`#XhairColorPicker` / `#XhairOutlineColorPicker`: cl_crosshaircolor_r/g/b/a, cl_crosshairoutline_r/g/b/a), the music modes' groups (`#SettingsMusicMode*`, one shown at a time by snd_music_settings_mode).
- Rows per cl_crosshairstyle: settingsmenu_crosshair.ts `OnCrosshairStyleChange` (everything in XHAIR_TOGGLED hidden, then per style; the outline colour row while cl_crosshair_drawoutline != 0, the bot row while cl_show_observer_crosshair == 2; styles 0, 1, 2, 6 are "dynamic-crosshair"; 3, 6, 0, 1, 7, 8, 9 tagged new).
- NEW: promoted_settings.ts' list with start / end dates (none current on 2026-11-16).
- Audio tab: Master Volume, Main Menu Ambience Volume, Audio Device, EQ Profile (snd_headphone_eq Natural / Crisp / Smooth), L/R Isolation (snd_spatialize_lerp slider), Perspective Correction, Play Audio When Game In Background (snd_mute_losefocus, Yes = 0); Voice; Music with per-mode volumes; Game Mode EQ.

### Styles (.vcss)

| File | Values |
|---|---|
| mainmenu.vcss | .mainmenu-content__container rgba(0,0,0,0.75); .content-navbar__tabs 48px rgba(0,0,0,0.25), --dark 42px; tab buttons margin 0 6px radius 3px; Label Stratum2 medium 16px uppercase padding 4px 6px; hover rgba(255,255,255,0.025); selected #82d7ff1a + selectedNavColor #82D8FF; .content-controls-actions-bar 96px padding 0 64px top border 5% |
| settings.vcss | .SettingsBackground 946px padding 42px 64px 0; rows min-height 48px; section title Stratum2 Black Italic 28px rgba(222,222,222,0.4); separator 1px white at 10%; CSGOSettingsEnumDropDown:hover #141c27; .settings-tag Stratum2 Bold 12px #D8760E |
| settings_slider.vcss | #Slider 25.5% + 10px; TextEntry#Value 80px Stratum2 bold 20px border 2px #cccccc15 radius 2px |
| csgostyles.vcss | DropDown height 36px margin 8px, expand.vsvg arrow 16px; .PopupButton radius 3px, hover rgba(255,255,255,0.05), Label Stratum2 medium condensed 24px uppercase margin 10px 12px 8px; DropDownMenu contextMenuBackground #262626 padding 8px 0, its Labels Stratum2 Light 16px padding 8px 16px, hover gradient #00000080 -> clear; Label's font notosans; baseText #cccccc |

Not in the extracted .vcss: the base Slider track / thumb.

## Unread

- 180b80220 (the screen height).
- The encoder behind MyPersonaAPI.GetCrosshairCode.
- The settings menu's size-edit path (180da8b00 / 180daa8d0 / 180da0610 / 180dc0420): rescales the sizes to the screen, then sets the edited one and the height (as cl_crosshair_screen_height's help says).
- 180da0610's own arithmetic between the checked calls (the dynamic gap's clamp, the alpha: from the disassembly); the friendly icon's rect; 180c9ae90's timers (from the decompile); the shader's float ops (decompiled SPIR-V).
- powf against a native call (1 ulp on ~0.02%: see tier0's maths).
- The smoke test's precision: CS2's client simulates its smokes in f32.
