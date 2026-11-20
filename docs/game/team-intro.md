# Team intro (CCSGO_TeamIntroMenu, the intro period, the map preview camera path, DoF)

client_20261015, server_20261105, rendersystemdx11_20261015. Panorama from pak01: layout/teamintromenu.vxml, scripts/teamintromenu.vts, styles/teamintromenu.vcss, scripts/match_stakes.vts, layout/hud/hud.vxml; the prefabs game/csgo/maps/prefabs/misc/*_intro*.vpk; csgo_english.txt; dof2.vfx (core shaders_pc / _vulkan).

## Functions

| Address | Module | What |
|---|---|---|
| 18008a130 | client | registers `mp_team_intro_type` (server 1800a29a0) |
| 1800a28f0 | server | registers `mp_team_intro_time` |
| 1800acad0 / 1800aca20 | server | register `sv_force_team_intro_variant` / `sv_force_team_intro_random` |
| 18097fa90 | server | the intro type (client 18078ae90): "none" 0 / "normal" 1 / "wingman" 2 / "rush" 3; else mp_halftime's bool (1 or 0) |
| 180965160 | server | ShouldPlayTeamIntro: type != 0 and mp_team_intro_time > 0 |
| 180957e50 | server | RestartRound: the intro's start |
| 18097ded0 | server | (team): a team's variant |
| 18097d720 | server | the spots' randoms and players |
| 18097da90 | server | (spot, controller, team): the spot's player and items |
| 180a35520 | server | the item def's loadout slot for a team |
| 18097d9b0 | server | weapon_m4a1 falling back to weapon_m4a1_silencer |
| 1809669f0 | server | Think: the intro period and its VO (VO set at 1809679a7, period end at 180967a05) |
| 18096ac20 | server | (team, sound, token): a team's radio line |
| 180239eb0 | server | Radio(radio services, sound, token, auto 1, chat wheel 0): the TextMsg (#Game_radio / #Game_radio_location) only when token isn't null; radio.locknload has none, so only the agent's voice line (response concept) plays |
| 180968600 | server | the warmup's end: m_flRestartRoundTime = now + (ShouldPlayTeamIntro ? 1.0 : (float) the int cvar at 182118f30) |
| 18076b420 | client | m_bTeamIntroPeriod's change callback: team_intro_start / team_intro_end |
| 180df6f60 | client | the menu: loads teamintromenu.xml, CSGOTeamIntroMenu panel, listens for both events |
| 180dfc510 | client | team_intro_start: not "active" and the camera 180cb1d90(18078ad90(local team), the team's variant 18075e340) exists -> StartTeamIntro; team_intro_end: active -> EndTeamIntro |
| 18078ad90 / 18078ae10 | client | the camera's / the spots' classname by type and team |
| 180cb1d90 | client | find the camera (class, variant) |
| 18075e340 | client | the team's variant |
| 180e0db60 | client | JS bindings: StartCamera 180e0ed60, ClearModels 180df53a0, AddModel 180df2120, GetModelBonePosition 180dfdcf0, StopCamera 180e0ee40 |
| 180e0ed60 | client | StartCamera: flag 1825c9e3b = 1; the camera -> 180c97510; 180e851f0(0, 1); 180d5a3b0(hud, HUD_TEAMINTRO_VISIBLE, 1) |
| 180e0ee40 | client | StopCamera: flag 0; 180d5a3b0(hud, HUD_TEAMINTRO_VISIBLE, 0) |
| 180c97510 | client | the path's start: SetNextThink of its Think (vfn 0x490 through 18015c5fc) at -1293.0 (0xc4a1a000; 18015b150 just stores the float), m_flLastTime (+0x658) = Plat_FloatTime(), time (+0x660) = 0, playback rate (+0x668) = 1.0 |
| 180d5a3b0 | client | each HUD panel (+0x200 count, +0x208 handles, 12 bytes each): vfn 0x500 (SetHasClass) with the symbol and the bool |
| 180106a30 | client | registers symbol 1825c9f88 "HUD_TEAMINTRO_VISIBLE" (only hudrush.vcss reads that class) |
| 180cb2100 | client | the active menu camera: with 1825c9e3b the team intro's (local team, its variant), else end_of_match_camera / team_select_camera |
| 180eb4df0 | client | CCSGO_HudReticle update (via 180eaf7c0, vtable 181cddda8 slot 6): skips the target ID while it runs |
| 180d049d0 | client | ClientModeCSNormal slot 27: the menu camera's DoF enabled / planes / tilt into the view (+0x4d8 .. +0x4ec) |
| 180c7c9c0 / 180c95630 | client | C_CSPlayerPawn slots 339 / 110: answer "no" while it runs (as do the kill panels, DM bonus, vote and others) |
| 180da0610 | client | crosshair: not hidden by the intro (nor the radar) |
| 180dff150 | client | the menu's key filter while 1825c9e3b: every binding is the menu's but +showscores, messagemode, messagemode2, say_team, +voicerecord (and the other strings it compares) |
| 180df2120 | client | AddModel(team, ordinal): the spot 180789060(class, variant, ordinal); with a player (+0x618) its model 180797dc0; returns { sXuid } |
| 180c96620 | client | a node's world tangents: 18016a3d0 |
| 18016a3d0 | client | rotate by quaternion: `t = 2 (q.xyz x v)`, `v + w t + q.xyz x t`; skipped for an identity rotation |
| 180c94f90 | client | the path build |
| 1817445e0 | client | AngleQuaternion |
| 1801587b0 | client | clamp |
| 180c6d6e0 | client | a segment's length |
| 180c6c9c0 | client | Bezier arc length |
| 180c6c730 | client | the path timing (path, duration) |
| 180c6d9c0 | client | a segment's timing (node, t, prev, next) |
| 180c67d00 | client | the per-frame path update |
| 180c6c050 | client | evaluate the path at t |
| 180c6d7b0 | client | u at t |
| 1817463a0 | client | QuaternionAngles |
| 1811d9d30 | client | CRenderingPipelineCsgo::AddLayersToView (calls 1811f68a0 at 1811deebe) |
| 1811d1e80 | client | the quarter-res effects bloom layer ("BloomFinalPass" / "QuarterResEffectsColor", at 1811de7a3) |
| 1811e88a0 | client | PostProcessing (at 1811dfb2d: Bloom, BloomBuffer) |
| 1811f68a0 | client | DoF (param_1 renderer state, param_3 view, param_4 planes, param_5 tilt) |
| 181208840 | client | colour resolve ("Non-MSAA Resolve PS" or the MSAA one) |
| 181203740 | client | Dof2CBParams_t build (cached) |
| 1811ceb40 | client | 16-byte compare |
| 18015a570 | client | `1.0f / (float)w` |
| 180185170 | client | zero |
| 180127490 / 180127530 | client | register r_dof2_maxblursize / r_dof2_radiusscale |
| 1800908f0 | rendersystemdx11 | a format's byte count: table + fmt x 24 + 0x20 |

## Fields

| Offset | Field |
|---|---|
| CCSGameRules +0x13c4 (client 0xefc) | m_nTTeamIntroVariant |
| CCSGameRules +0x13c8 (client 0xf00) | m_nCTTeamIntroVariant |
| CCSGameRules +0x13cc (client 0xf04) | m_bTeamIntroPeriod |
| CCSGameRules +0x13d0 | m_fTeamIntroPeriodEnd |
| CCSGameRules +0x13d4 | m_bPlayedTeamIntroVO |
| CCSGameRules +0xd9 | m_bWarmupPeriod |
| CCSGameRules +0x124 | m_nRoundsPlayedThisPhase |
| CCSGameRules +0x108 | m_fRoundStartTime |
| CCSGameRules +0xfc | m_iFreezeTime |
| CCSGameRules +0x10c | m_flRestartRoundTime |
| spot +0x4a8 | m_nVariant |
| spot +0x4ac | the random |
| spot +0x4b0 | m_nOrdinal |
| spot +0x4b8 | m_szWeapon |
| spot +0x4c0 | m_xuid |
| spot +0x4c8 | loadout slot 0x26 (customplayer) |
| spot +0x8b0 | loadout slot 0x29 (gloves) |
| spot +0xc98 | the weapon item |
| spot +0x618 (client) | the player |
| controller +0xd40 | m_iPlayerState |
| pawn +0xe58 | radio services |
| path +0x600 | m_flZFar |
| path +0x604 | m_flZNear |
| path +0x608 | m_bLoop |
| path +0x609 | m_bVerticalFOV |
| path +0x60a | m_bConstantSpeed |
| path +0x60c | m_flDuration |
| path +0x62c | node lengths sum |
| path +0x650 | m_flPathLength |
| path +0x654 | m_flPathDuration |
| path +0x658 / +0x660 / +0x668 | m_flLastTime / time / playback rate |
| path +0xc | cached segment index |
| node +0x600 | m_szParentPathUniqueID |
| node +0x608 | m_nPathIndex |
| node +0x60c / +0x618 | m_vInTangentLocal / m_vOutTangentLocal |
| node +0x624 | m_flFOV |
| node +0x628 | m_flCameraSpeed |
| node +0x62c / +0x630 | m_flEaseIn / m_flEaseOut |
| node +0x634 / +0x640 | m_vInTangentWorld / m_vOutTangentWorld |
| view +0x194 / 0x198 / 0x19c | view forward |
| view +0x10 | eye |

Built node (0x90 bytes):

| Offset | Field |
|---|---|
| 0x00 | pos |
| 0x0c / 0x18 | in / out tangent |
| 0x30 | quat = AngleQuaternion(abs angles) |
| 0x40 | fov |
| 0x44 | max(0, speed) |
| 0x48 / 0x4c | ease in / out, clamped [0, 100] |
| 0x50 / 0x54 | length / start length |
| 0x58 / 0x5c | prev / next speed |
| 0x60 / 0x64 | ease in time / distance |
| 0x68 / 0x6c / 0x70 | cruise time / distance / start |
| 0x74 / 0x78 / 0x7c | ease out time / distance / start |
| 0x80 | start |
| 0x84 | segment time |

## Constants

| Value | What |
|---|---|
| `mp_team_intro_type` | string, flags 0x282000, default "auto": "none, normal, wingman, rush, or auto (implies normal if mp_halftime is set, none otherwise)" |
| `mp_team_intro_time` | float 0x40d00000 = 6.5, flags 0x282100, "How many seconds for team intro" |
| `sv_force_team_intro_variant`, `sv_force_team_intro_random` (182120c90) | int; off at <= 0 / not one of the map's |
| 4.0 (0x18179be70) | the VO's lead before the intro's end |
| -1293.0 (0xc4a1a000) | the path's first think time |
| r_dof2_maxblursize | handle 0x1825f5ed0, default 5, flags 2 |
| r_dof2_radiusscale | handle 0x1825f5ec0, default 0.25, flags 2 |
| 2.3999631 (0x1822574c4, bits 0x401998ff) | the golden angle step, read only here |
| 0x1034 | Dof2CBParams_t size |
| combo attrs | invViewProj 0xbaad05b0, lens plane 0xf668431c, k 0x71502b03, D_WRITE_COC 0x2162f981 |
| 0xf = RGBA16161616F, 0x3d = R11G11B10_FLOAT, 39 = R16F | ImageFormat (rows 0x10, 0x3e, 0x28 of 0x18042d470) |
| 0x18042d470 | rendersystemdx11 format table: 24-byte rows { name*, bytes, r, g, b, a, depth, stencil, block bytes, flags, ... }, indexed by format + 1 (row 0 UNKNOWN = -1) |
| 182562090 | timescale |
| 0x80 | arc length's sample limit |

gamemode_competitive2v2.cfg sets mp_team_intro_type wingman; gamemode_rush.cfg rush and mp_team_intro_time 9; no other cfg names them (Competitive: auto with mp_halftime 1 = normal; Casual / deathmatch / Arms Race: mp_halftime 0 = none).

## The server's intro

1. RestartRound (180957e50): m_fTeamIntroPeriodEnd = now; when ShouldPlayTeamIntro, not m_bWarmupPeriod and m_nRoundsPlayedThisPhase == 0: m_nTTeamIntroVariant = 18097ded0(2), m_nCTTeamIntroVariant = 18097ded0(3), 18097d720(), m_bTeamIntroPeriod = 1, +0x13d0 += mp_team_intro_time, m_bPlayedTeamIntroVO = 0; then `m_fRoundStartTime = (float) m_iFreezeTime + +0x13d0`.
2. 18097ded0: the spots of the type's classname (team_intro_terrorist / _counterterrorist, wingman_intro_*, rush_intro_*) in entity order, their m_nVariant collected once each; one equal to sv_force_team_intro_variant returns at once; else RandomInt(0, n - 1) of the list; none -1.
3. 18097d720: per team a random: sv_force_team_intro_random if >= 1, else RandomInt(1, 100) each; ordinals start at 1 per team; controllers 0..63 in slot order, team 2 / 3 only: the team's next ordinal; the spot with m_nVariant == the rules' variant and m_nOrdinal == it gets the random and 18097da90.
4. 18097da90: m_xuid; econ items slot 0x26, 0x29; the weapon: "weapon_knife" slot 0, else the item def's loadout slot for the team (180a35520), weapon_m4a1 falling back to weapon_m4a1_silencer.
5. Think (1809669f0), while m_bTeamIntroPeriod: not m_bPlayedTeamIntroVO and now >= m_fTeamIntroPeriodEnd - 4.0: 18096ac20(3, "radio.locknload", null), 18096ac20(2, ...), m_bPlayedTeamIntroVO = 1; once now >= m_fTeamIntroPeriodEnd: m_bTeamIntroPeriod = 0.
6. 18096ac20: every controller of the team with m_iPlayerState 0 and a living pawn with radio services, one by RandomInt(0, n - 1): Radio.

## The prefabs

A map places each intro as one point-prefab entity (classname `terrorist_team_intro`, `counterterrorist_team_intro`, `..._variant2`, `terrorist_wingman_intro`, ...; targetmapname prefabs/misc/<same>). The prefab's vpk (maps/prefabs/misc/<name>.vpk, entities/default_ents.vents) holds:

- Spots `team_intro_terrorist` ...: ordinal 1..5 (wingman 1..2, rush 1..3), variant (1, or 2 in _variant2), weapon, team_preview_position / team_preview_variant, ct_true, character_mode "team-intro", animgraph ui_player_t / ui_player_ct.vanmgrph, origin 0 and angles (0, 315, 0) for every spot (the clips place them).
- Camera `terrorist_team_intro_camera` ...: variant, duration 5, loop false, constant_speed false (rush: true), useverticalfov false, dof_enabled, dof_near_blurry -100, near_crisp 0, far_crisp 100, far_blurry 450, dof_tilt_to_ground 0.5, pathnodes (the editor's copy), and its `map_preview_camera_path_node` children (path_uniqueid = the camera's hammeruniqueid, path_index, origin, angles, in_tangent_local, out_tangent_local, fov 90, speed, ease_in, ease_out, znear 4, zfar 100).
- The paths' times: team_intro T 22.9 s / CT 24.2 s, _variant2 7.5 / 7.1 s, wingman 11.2 / 8.4 s, rush 5 s (constant speed, one point): the 6.5 s intro sees their start.

## Client panel

- teamintromenu.vcss: the root's top gradient by team (CT rgba(37, 75, 105, .8), T rgba(92, 74, 33, .8), to 0 at 25 %), the icon 100 x 100 at 30 down, the half label 50 px Stratum2 Bold Condensed upper case, the team label 25 px Stratum2, the card (48 px avatar on teamcounter_alivebg<team>, the 30 px name, brightness 2, max 160 px), the black fade.
- Strings: team-intro-1st-half / -2nd-half / -overtime-1st-half:f / -2nd-half:f / -starting-as-t / -ct / -playing-as-t / -ct. MatchStakes shows only for a Premier rank type ([teammate-colors.md](teammate-colors.md) "Match stakes").
- Sounds: UIPanorama.TeamIntro (0.5 s delay in its event), UIPanorama.TeamIntro_TSuits / _CTSuits; the clips' own sound events (CNmClipDocEvent_Sound, ClientOnly, EntityEyePos): TeamIntro.Suit_T / _CT, TeamIntro.Footsteps_Default(.Q), TeamIntro.Weapon_* foley, TeamIntro.Weapon_Catch, HEGrenade.Inspect02.Catch, Knife.Catch.SoftGrab.Quiet, Weapon_Knife.Skeleton.Swish.
- Models: uimodel's SM/Team Intro state (character_mode "team_intro"), is_CT -> Team Variant (team_preview_variant: Reference Pose / v2 / v3) -> Position (team_preview_position: Reference Pose, then a clip per ordinal; the third a Weapon Selector knife / push knife on weapon_type). The intro clips' root motion is the identity.

## The camera path (C_CSGO_MapPreviewCameraPath)

- Build (180c94f90): per node the 0x90 record; the timing fields zeroed; each node's length (180c6d6e0) summed (+0x62c); 180c6c730(path, duration); m_flPathLength = the sum, m_flPathDuration = the time.
- Segment length (180c6d6e0): start length = running sum, length = 180c6c9c0(Bezier pos, pos + out, next + next.in, next, tol 1.0); the last node 0.
- Arc length (180c6c9c0): power basis `a = ((c1 3 - c0 1) - c2 3) + c3`, `b = (c0 3 - c1 6) + c2 3`, `k = c1 3 - c0 3`; n = 2, 4, ... samples of the polyline, distances summed four a pass `(((d1 + acc) + d2) + d3) + d4`, each `sqrt((z z + y y) + x x)`; stop when `|len - prev| / len < tol / 100` or n > 0x80.
- Timing (180c6c730): without m_bConstantSpeed each node but the last speed `max(0, max(0.01, speed))`, then every node 180c6d9c0(node, t, prev, next), t += its time; with it, time = max(0, m_flDuration), every node's speed `max(0, length / time)` and its eases 0, the same walk; the last node's start = the total.
- Segment timing (180c6d9c0): start; prev / next speed (0 without); an ease-in fraction `clamp(easeIn / 100)` only where `|speed - prev| > max(1, |speed - prev|) x 0.0001`, an ease-out the same towards next; their sum over 1 normalized; ease-in distance = `fi len`, time = `it / ((speed - prev) 0.5 + prev)`; cruise distance = `clamp(1 - (fo + fi)) len`, time = `it / speed` (0 at 0), start = the ease-in time; ease-out distance = `len fo`, start = ease in + cruise time, time = `it / ((next - speed) 0.5 + speed)`; segment time = the three summed.
- Per frame (180c67d00): `t += (float) timescale x (Plat_FloatTime - last) x playback rate`; past the end: loop or clamp; 180c6c050(path, t); `fov = (fovB - fovA) frac + fovA` (a fov <= 0 keeps the last); SetAbsOrigin / SetAbsAngles.
- Evaluate (180c6c050): the segment by the start times (cached index); u = 180c6d7b0; position `c0 b0 + b1 c1 + c2 b2 + c3 b3` (`b0 = s s s`, `b1 = (s s 3) u`, `b2 = (s 3 u) u`, `b3 = u u u`); rotation: the fitted slerp of the two nodes' quaternions by u (the k polynomial; identity at zero length), QuaternionAngles; the fov pair and u for the caller.
- u (180c6d7b0): `local = clamp(t - start, 0, segment time)`; ease in: `(sin(local pi / eiT) (prev - speed) eiT + (speed + prev) local pi) / 2 pi`; cruise (no ease out or before its start): `clamp((local - cruise start) speed + ease in distance, 0, len)`; ease out: `cruise + ease in distance + (sin(x / eoT) (speed - next) eoT + (next + speed) x) / 2 pi` with `x = (local - ease out start) pi`; / len, clamped [0, 1] (the Bezier parameter itself, not an arc-length one).

## Depth of field (dof2.vfx, 1811f68a0)

- D_WRITE_COC writes the circle of confusion from the scene depth's world position: `d = dot(g_vLensPlane, (P, 1))`, `coc = max(sat(d k.x + k.y), sat(d k.z + k.w))`; then a gather (Dof2CBParams: up to 256 taps, .xy offset, .zw a smoothstep range, by the tap's coc x a scale).
- Lens plane: normal = normalize(view forward with z lerped to 0 by dof_tilt_to_ground), through the eye: `plane.w = -dot(n, eye)`; `k = (-1 / (nearCrisp - nearBlurry), nearBlurry / (nearCrisp - nearBlurry) + 1, 1 / (farBlurry - farCrisp), -farCrisp / (farBlurry - farCrisp))`.
- Placement (1811d9d30 at 1811deebe): after every translucent layer (BeforeTranslucent, MBOIT smoke / translucent, "Water Translucent Combine", "Mixed Resolution Particles", OverlaySmoke, "GameOverlay Particles", "Translucent Screen Space", the letterbox) and after the bloom layer (1811d1e80), before PostProcessing (1811e88a0). Translucents are already in the colour and take the CoC of the scene depth behind them (they write none); bloom and tone map read the blurred frame.
- No near / far layers and no downsample: two passes at the view's full size (param_3[6]: width, height).
- 1811f68a0: lens plane / k; then 181208840 with invViewProj, lens plane, k and D_WRITE_COC on when the colour's format (vtable 0x4d8 of DAT_18279cf10) is 0xf: "IntermediateOutputColorResolved" (the colour's own format) = rgb + the CoC in alpha. When the view's colour (param_6, its vtable 0x150 info) is 0x3d (no alpha), a separate "DOF2 CoC" pass writes "rtCoCTarget" (format 39) and the final pass takes D_COC_TEXTURE: the same numbers either way. "DOF2 Final" writes the view's colour target (param_6), reading the resolved copy.
- The resolve's own V_powf factor 0xddb2abcf (behind the cvar at DAT_1825f67c8) is the resolve's, not the DoF's: unread.
- Params block for 181203740 (stack local_390): +0x00 k (16 bytes), +0x10 r_dof2_radiusscale (DAT_1825f5ec8 + 0x58), +0x14 r_dof2_maxblursize (DAT_1825f5ed8 + 0x58), +0x18 the angle step, +0x1c / +0x20 the view's width / height (ints).

## Dof2CBParams_t (181203740)

- Rebuilt only when +0x10, +0x14, +0x18, width, height (statics 0x1825f7694 / 98 / 9c / b0 / b4) or k (16 bytes at 0x1825f76a0, 1811ceb40) changed, or there's no buffer; the old one released (vtable 0x228 of DAT_18279cec0), the new created by its vtable 0x218 (size 0x1034, name "Dof2CBParams_t").
- Layout: +0x00 texel (1 / w, 1 / h), +0x08 zeroed, +0x10 the angle step, +0x14 maxblursize (the shader's c1.y: CoC 1 = this many pixels), +0x18 radiusscale, +0x20 k (the D_WRITE_COC pass's c2), +0x30 float4 taps[256] (c3..c258), +0x1030 the count (c259.x).
- Taps (disassembly 1812038ac .. 18120397a), floats in this order: a = 0, r = radiusscale; while maxblursize > r: if i >= 256 return (no buffer made at all); `tap = (V_cosf(a) * texel.x * r, V_sinf(a) * texel.y * r, r - 0.5, r + 0.5)`; `a += step`; `r += radiusscale / r`. V_cosf / V_sinf are tier0 imports (IAT 0x181aad8b0 / 0x181aad8a8: the CRT cosf / sinf). Defaults: 48 taps, r from 0.25 to 4.99.
- Nothing else references either cvar handle.

## The gather (the final pass)

D_COC_TEXTURE reads the CoC from its own texture, else colour .w.

1. `c0 = sample(uv)`; `cap = c0.w x 2`; n = 1; `sum = c0.rgb`.
2. Per tap: `s = sample(uv + tap.xy)`; `coc = s.w > cap ? clamp(s.w, 0, cap) : s.w`; `sum += lerp(sum / n, s.rgb, smoothstep(tap.z, tap.w, coc x c1.y))`; n += 1.
3. `out = (sum / n, 1)`.

Samplers clamp, MinMagLinearMipPoint (bilinear); no blending, no depth test (dof2_states). The offsets are in D3D's uv (the vertex shader flips y): GL's are (x, -y).

## Unread

- The spots' econ items on the models (weapon skins, gloves).
