# The team intro (CCSGO_TeamIntroMenu, the intro period, the map preview camera path)

client_20261015.dll and server_20261105.dll (ReVa), panorama from pak01 (`lasers-bake --decompile`:
layout/teamintromenu.vxml, scripts/teamintromenu.vts, styles/teamintromenu.vcss, scripts/match_stakes.vts,
layout/hud/hud.vxml), the intro prefabs game/csgo/maps/prefabs/misc/*_intro*.vpk, strings from csgo_english.txt.
Read 2026-11-16. Ported in server/cs2web/modes/team/team-intro.js, src/cs2web/modes/team/team-intro.js,
client/hud/team-intro.js (+ .css), team-intro-camera.js, team-intro-scene.js.

## Convars

| Address | What |
|---|---|
| client 18008a130 / server 1800a29a0 | `mp_team_intro_type` string, flags 0x282000, default "auto": "none, normal, wingman, rush, or auto (implies normal if mp_halftime is set, none otherwise)" |
| server 1800a28f0 | `mp_team_intro_time` float, 0x40d00000 = **6.5**, flags 0x282100, "How many seconds for team intro" |
| server 1800acad0 / 1800aca20 | `sv_force_team_intro_variant`, `sv_force_team_intro_random` (int; read as off at <= 0 / not one of the map's) |

gamemode_competitive2v2.cfg sets mp_team_intro_type wingman; gamemode_rush.cfg rush and mp_team_intro_time 9; no other
cfg names them (Competitive: auto with mp_halftime 1 = normal; Casual / deathmatch / Arms Race: mp_halftime 0 = none).

## Server

| Address | What |
|---|---|
| 18097fa90 (client 18078ae90) | the intro type: the cvar's string against "none" 0 / "normal" 1 / "wingman" 2 / "rush" 3; anything else: mp_halftime's bool (1 or 0) |
| 180965160 | ShouldPlayTeamIntro: type != 0 and mp_team_intro_time > 0 |
| 180957e50 (RestartRound) | m_fTeamIntroPeriodEnd (+0x13d0) = now; when ShouldPlayTeamIntro, not m_bWarmupPeriod (+0xd9) and m_nRoundsPlayedThisPhase (+0x124) == 0: m_nTTeamIntroVariant (+0x13c4) = 18097ded0(2), m_nCTTeamIntroVariant (+0x13c8) = 18097ded0(3), 18097d720(), m_bTeamIntroPeriod (+0x13cc) = 1, +0x13d0 += mp_team_intro_time, m_bPlayedTeamIntroVO (+0x13d4) = 0; then m_fRoundStartTime (+0x108) = (float) m_iFreezeTime (+0xfc) + +0x13d0 |
| 18097ded0 | a team's variant: the spot entities of the type's classname (team_intro_terrorist / _counterterrorist, wingman_intro_*, rush_intro_*) walked in entity order, their m_nVariant (+0x4a8) collected once each; one equal to sv_force_team_intro_variant returns at once; else RandomInt(0, n - 1) of the list; none -1 |
| 18097d720 | per team a random: sv_force_team_intro_random (182120c90) if >= 1, else RandomInt(1, 100) each; ordinals start at 1 per team; controllers 0..63 in slot order, team 2 / 3 only: the team's next ordinal, the spot with m_nVariant == the rules' variant and m_nOrdinal (+0x4b0) == it gets the random (+0x4ac) and 18097da90(spot, controller, team) |
| 18097da90 | the spot's player: m_xuid (+0x4c0), its econ items: loadout slot 0x26 (customplayer, +0x4c8), 0x29 (gloves, +0x8b0), the spot's weapon (m_szWeapon +0x4b8): "weapon_knife" slot 0, else the item def's loadout slot for the team (180a35520), weapon_m4a1 falling back to weapon_m4a1_silencer (18097d9b0) (+0xc98) |
| 1809669f0 (Think) | while m_bTeamIntroPeriod: if not m_bPlayedTeamIntroVO and now >= m_fTeamIntroPeriodEnd - 4.0 (0x18179be70): 18096ac20(3, "radio.locknload", null), 18096ac20(2, ...), m_bPlayedTeamIntroVO = 1 (1809679a7); then once now >= m_fTeamIntroPeriodEnd: m_bTeamIntroPeriod = 0 (180967a05) |
| 18096ac20 | a team's radio line: every controller of the team with m_iPlayerState (+0xd40) 0 and a living pawn with a radio services (+0xe58), one by RandomInt(0, n - 1): Radio 180239eb0(its radio services, sound, token, auto 1, chat wheel 0) |
| 180239eb0 (Radio) | the TextMsg (#Game_radio / #Game_radio_location) only when the token isn't null: radio.locknload has none, so only the agent's voice line (the response concept) plays |
| 180968600 | the warmup's end: m_flRestartRoundTime (+0x10c) = now + (ShouldPlayTeamIntro ? 1.0 : (float) the int cvar at 182118f30) |
| schema | m_nTTeamIntroVariant 0x13c4, m_nCTTeamIntroVariant 0x13c8, m_bTeamIntroPeriod 0x13cc, m_fTeamIntroPeriodEnd 0x13d0, m_bPlayedTeamIntroVO 0x13d4 (client: 0xefc / 0xf00 / 0xf04) |

Ported: comp.js phaseStart (the rounds played when the phase began: the match's start, the halftime's swap, an
overtime's start), TeamIntro.restart, game.js startRound (round.introEnd, startedAt, teamIntroPeriod, the round message's
`intro`), the snapshot's ph bit 8, the VO (round.introVO, comms/radio.js teamLine: the agents' radio.locknload from
maps/<map>/vo, which only maps with a vo bake have, as every radio voice line).

## The prefabs

A map places each intro as one point-prefab entity (classname `terrorist_team_intro`, `counterterrorist_team_intro`,
`..._variant2`, `terrorist_wingman_intro`, ...; targetmapname prefabs/misc/<same>). The prefab's own vpk
(maps/prefabs/misc/<name>.vpk, entities/default_ents.vents) holds, in its frame:
- the spots: `team_intro_terrorist` ... with ordinal 1..5 (wingman 1..2, rush 1..3), variant (1, or 2 in _variant2),
  weapon, team_preview_position / team_preview_variant, ct_true, character_mode "team-intro", animgraph
  ui_player_t / ui_player_ct.vanmgrph, origin 0 and angles (0, 315, 0) for every spot (the clips place them)
- the camera `terrorist_team_intro_camera` ...: variant, duration 5, loop false, constant_speed false (rush: true),
  useverticalfov false, dof_enabled, dof_near_blurry -100, near_crisp 0, far_crisp 100, far_blurry 450,
  dof_tilt_to_ground 0.5, pathnodes (the editor's copy), and its `map_preview_camera_path_node` children
  (path_uniqueid = the camera's hammeruniqueid, path_index, origin, angles, in_tangent_local, out_tangent_local, fov 90,
  speed, ease_in, ease_out, znear 4, zfar 100)
tools/team-intro.mjs writes all eight into web/public/ze-armsrace/winpanel/intro.json.

## Client

| Address | What |
|---|---|
| 18076b420 | m_bTeamIntroPeriod's change callback: fires team_intro_start / team_intro_end |
| 180df6f60 | the menu: loads teamintromenu.xml, CSGOTeamIntroMenu panel, listens for both events |
| 180dfc510 | team_intro_start: not "active" and the camera 180cb1d90(18078ad90(local team), the team's variant 18075e340) exists -> StartTeamIntro; team_intro_end: active -> EndTeamIntro |
| 18078ad90 / 18078ae10 | the camera's / the spots' classname by type and team (the server's names) |
| 180e0db60 | the JS bindings: StartCamera 180e0ed60, ClearModels 180df53a0, AddModel 180df2120, GetModelBonePosition 180dfdcf0, StopCamera 180e0ee40 |
| 180e0ed60 | StartCamera: flag 1825c9e3b = 1; the camera -> 180c97510; 180e851f0(0, 1); 180d5a3b0(hud, HUD_TEAMINTRO_VISIBLE, 1) |
| 180e0ee40 | StopCamera: the flag 0; 180d5a3b0(hud, HUD_TEAMINTRO_VISIBLE, 0) |
| 180c97510 | the path's start: SetNextThink of its Think (vfn 0x490 through 18015c5fc) at -1293.0 (0xc4a1a000: 18015b150 just stores the float), m_flLastTime (+0x658) = Plat_FloatTime(), the time (+0x660) = 0, the playback rate (+0x668) = 1.0 |
| 180d5a3b0 | each of the HUD's panels (+0x200 count, +0x208 handles, 12 bytes each): vfn 0x500 (SetHasClass) with the symbol and the bool; the symbol 1825c9f88 is registered as "HUD_TEAMINTRO_VISIBLE" (180106a30). Only hudrush.vcss reads that class |
| 180cb2100 | the active menu camera: with 1825c9e3b the team intro's camera (the local team's, its variant), else end_of_match_camera / team_select_camera; its readers while it runs: CCSGO_HudReticle's update (180eb4df0 via 180eaf7c0, vtable 181cddda8 slot 6) skips the target ID; ClientModeCSNormal slot 27 (180d049d0) takes the camera's DoF into the view; C_CSPlayerPawn slots 339 (180c7c9c0) / 110 (180c95630) and the kill panels, DM bonus, vote and others answer "no"; nothing hides the crosshair (180da0610) or the radar |
| 180dff150 | the menu's key filter while 1825c9e3b: every binding is the menu's but +showscores, messagemode, messagemode2, say_team, +voicerecord (and the other strings it compares) |
| 180df2120 | AddModel(team, ordinal): the spot 180789060(class, variant, ordinal); with a player (+0x618) its model 180797dc0, returns { sXuid } |

The script (teamintromenu.vts _StartTeamIntro) and its timing are in client/hud/team-intro.js's header. Layout and
styles (teamintromenu.vcss) in team-intro.css: the root's top gradient by team (CT rgba(37, 75, 105, .8), T
rgba(92, 74, 33, .8), to 0 at 25 %), the icon 100 x 100 at 30 down, the half label 50 px Stratum2 Bold Condensed upper
case, the team label 25 px Stratum2, the card (48 px avatar on teamcounter_alivebg<team>, the 30 px name, brightness 2,
max 160 px), the black fade. Strings: team-intro-1st-half / -2nd-half / -overtime-1st-half:f / -2nd-half:f /
-starting-as-t / -ct / -playing-as-t / -ct. MatchStakes shows only for a Premier rank type: here a rated match (client/hud/match-stakes.js; docs/game/teammate-colors.md "Match stakes").
Sounds: UIPanorama.TeamIntro (0.5 s delay in its event), UIPanorama.TeamIntro_TSuits / _CTSuits; the clips' own sound
events (CNmClipDocEvent_Sound, ClientOnly, EntityEyePos): TeamIntro.Suit_T / _CT, TeamIntro.Footsteps_Default(.Q),
TeamIntro.Weapon_* foley, TeamIntro.Weapon_Catch, HEGrenade.Inspect02.Catch, Knife.Catch.SoftGrab.Quiet,
Weapon_Knife.Skeleton.Swish.

The models: uimodel's SM/Team Intro state (character_mode "team_intro"), is_CT -> Team Variant (team_preview_variant:
Reference Pose / v2 / v3) -> Position (team_preview_position: Reference Pose, then a clip per ordinal; the third a
Weapon Selector knife / push knife on weapon_type). The intro clips' root motion is the identity.

## The camera path (C_CSGO_MapPreviewCameraPath)

Schema: path m_flZFar 0x600, m_flZNear 0x604, m_bLoop 0x608, m_bVerticalFOV 0x609, m_bConstantSpeed 0x60a,
m_flDuration 0x60c, m_flPathLength 0x650, m_flPathDuration 0x654; node m_szParentPathUniqueID 0x600, m_nPathIndex
0x608, m_vInTangentLocal 0x60c, m_vOutTangentLocal 0x618, m_flFOV 0x624, m_flCameraSpeed 0x628, m_flEaseIn 0x62c,
m_flEaseOut 0x630, m_vInTangentWorld 0x634, m_vOutTangentWorld 0x640.

| Address | What |
|---|---|
| 180c96620 | a node's world tangents: 18016a3d0 (the local vector turned by the node's world rotation quaternion: t = 2 (q.xyz x v), v + w t + q.xyz x t; skipped for an identity rotation) |
| 180c94f90 | the build: per node (0x90 bytes: 0 pos, 0xc in, 0x18 out, 0x30 quat = AngleQuaternion(abs angles) 1817445e0, 0x40 fov, 0x44 max(0, speed), 0x48 / 0x4c ease in / out clamped [0, 100] (1801587b0)); the timing fields zeroed; each node's length 180c6d6e0 summed (+0x62c); 180c6c730(path, duration); m_flPathLength = the sum, m_flPathDuration = the time |
| 180c6d6e0 | a segment: start length (+0x54), length (+0x50) = 180c6c9c0(Bezier pos, pos + out, next + next.in, next, tol 1.0); the last node 0 |
| 180c6c9c0 | the arc length: the power basis (a = ((c1 3 - c0 1) - c2 3) + c3, b = (c0 3 - c1 6) + c2 3, k = c1 3 - c0 3), n = 2, 4, ... samples of the polyline, the distances summed four a pass (((d1 + acc) + d2) + d3) + d4, each sqrt((z z + y y) + x x); stop when |len - prev| / len < tol / 100 or n > 0x80 |
| 180c6c730 | the timing: without m_bConstantSpeed each node but the last speed max(0, max(0.01, speed)), then every node 180c6d9c0(node, t, prev, next), t += its time; with it, time = max(0, m_flDuration), every node's speed max(0, length / time) and its eases 0, the same walk; the last node's start = the total |
| 180c6d9c0 | a segment: start (+0x80); prev speed (+0x58) / next speed (+0x5c) (0 without); an ease in fraction clamp(easeIn / 100) only where |speed - prev| > max(1, |speed - prev|) x 0.0001, an ease out the same towards next; their sum over 1 normalized; ease in distance (+0x64) = fi len, time (+0x60) = it / ((speed - prev) 0.5 + prev); cruise distance (+0x6c) = clamp(1 - (fo + fi)) len, time (+0x68) = it / speed (0 at 0), its start (+0x70) = the ease in time; ease out distance (+0x78) = len fo, start (+0x7c) = ease in + cruise time, time (+0x74) = it / ((next - speed) 0.5 + speed); the segment's time (+0x84) = the three summed |
| 180c67d00 | each frame: t += (float) timescale (182562090) x (Plat_FloatTime - last) x the playback rate (+0x668); past the end: loop or clamp; 180c6c050(path, t); fov = (fovB - fovA) frac + fovA (a fov <= 0 keeps the last); SetAbsOrigin / SetAbsAngles |
| 180c6c050 | the segment by the start times (cached index +0xc); u = 180c6d7b0; position = c0 b0 + b1 c1 + c2 b2 + c3 b3 (b0 = s s s, b1 = (s s 3) u, b2 = (s 3 u) u, b3 = u u u); rotation: the fitted slerp of the two nodes' quaternions by u (the k polynomial: pose.js fslerp; identity at zero length), QuaternionAngles 1817463a0; fov pair and u for the caller |
| 180c6d7b0 | u: local = clamp(t - start, 0, segment time); in the ease in: (sin(local pi / eiT) (prev - speed) eiT + (speed + prev) local pi) / 2 pi; in the cruise (no ease out or before its start): clamp((local - cruise start) speed + ease in distance, 0, len); in the ease out: cruise + ease in distance + (sin(x / eoT) (speed - next) eoT + (next + speed) x) / 2 pi with x = (local - ease out start) pi; / len, clamped [0, 1] (the Bezier parameter itself, not an arc-length one) |

The paths' times (team-intro-camera-test.mjs): team_intro T 22.9 s / CT 24.2 s, _variant2 7.5 / 7.1 s, wingman
11.2 / 8.4 s, rush 5 s (constant speed, one point): the 6.5 s intro sees their start.

## Depth of field (dof2.vfx, client 1811f68a0)

- dof2.vfx (core shaders_pc / _vulkan: lasers-bake --shader-src dof2): D_WRITE_COC writes the circle of confusion from
  the scene depth's world position: d = dot(g_vLensPlane, (P, 1)), coc = max(sat(d k.x + k.y), sat(d k.z + k.w)); then
  a gather (Dof2CBParams: up to 256 taps .xy offset, .zw a smoothstep range, by the tap's coc x a scale)
- 1811f68a0: the lens plane's normal = normalize(view forward (+0x194 / 0x198 / 0x19c) with z lerped to 0 by
  param_5 = dof_tilt_to_ground), through the eye (+0x10): plane.w = -dot(n, eye); k = (-1 / (nearCrisp - nearBlurry),
  nearBlurry / (nearCrisp - nearBlurry) + 1, 1 / (farBlurry - farCrisp), -farCrisp / (farBlurry - farCrisp))
- 180d049d0 (ClientModeCSNormal slot 27): the menu camera's dof enabled / planes / tilt into the view (+0x4d8 .. +0x4ec)
- Ported: render.js setDof / _dofLens (the coc's constants, the tilted plane), world/dof.js (the passes, the taps, the
  gather); dof-test.mjs checks the table

### Where it runs, and translucents (client_20261015)

- The pipeline builder 1811d9d30 (CRenderingPipelineCsgo::AddLayersToView) calls 1811f68a0 at 1811deebe: after every
  translucent layer it adds (BeforeTranslucent, MBOIT smoke / translucent, "Water Translucent Combine", "Mixed
  Resolution Particles", OverlaySmoke, "GameOverlay Particles", "Translucent Screen Space", the letterbox) and after
  the quarter-res effects bloom layer (1811d1e80 "BloomFinalPass"/"QuarterResEffectsColor" at 1811de7a3), before
  PostProcessing (1811e88a0 at 1811dfb2d: Bloom, BloomBuffer). So translucents are already in the colour and take the
  CoC of the scene depth behind them (they write none); the bloom and the tone map read the blurred frame.
- No near / far layers and no downsample: two passes at the view's full size (param_3[6]: width, height).

### 1811f68a0 (param_1 the renderer's state, param_3 the view, param_4 the planes, param_5 the tilt)

- The lens plane / k as above; then 181208840 (the colour resolve: "Non-MSAA Resolve PS" or the MSAA one) with the
  invViewProj (combo attr 0xbaad05b0), lens plane (0xf668431c), k (0x71502b03) and D_WRITE_COC on (0x2162f981 = 1)
  when the colour's format (vtable 0x4d8 of DAT_18279cf10) is 0xf: "IntermediateOutputColorResolved" (made in the
  colour's own format) = rgb + the CoC in alpha. When the view's colour (param_6, its vtable 0x150 info) is format
  0x3d, which has no alpha, a separate "DOF2 CoC" pass writes "rtCoCTarget" (format 39) and the final pass takes
  D_COC_TEXTURE: the same numbers either way.
- The formats (ImageFormat; rendersystemdx11_20261015's table at 0x18042d470, 24-byte rows { name*, bytes, r, g, b,
  a, depth, stencil, block bytes, flags, ... }, indexed by format + 1: row 0 is UNKNOWN = -1, so 1800908f0 reads a
  format's byte count at table + fmt x 24 + 0x20): **0xf = RGBA16161616F**, **0x3d = R11G11B10_FLOAT**, **39 = R16F**
  (rows 0x10, 0x3e, 0x28). So the normal path keeps the CoC in a half-float RGBA's alpha and the "DOF2 Final" output
  is the same RGBA16F colour target; only an R11G11B10 colour takes a separate R16F CoC texture. Ours: the frame is
  RGBA16F (render.js hdr), so the 0xf path: world/dof.js's colour + CoC target and its output are RGBA16F, as CS2's. (The resolve's own V_powf factor 0xddb2abcf, behind
  the cvar at DAT_1825f67c8, is the resolve's, not the DoF's: unread.)
- The params block for 181203740 (on the stack at local_390): +0x00 k (16 bytes), +0x10 r_dof2_radiusscale
  (DAT_1825f5ec8 + 0x58), +0x14 r_dof2_maxblursize (DAT_1825f5ed8 + 0x58), +0x18 the angle step (0x1822574c4, bits
  0x401998ff = 2.3999631, the golden angle; read only here), +0x1c / +0x20 the view's width / height (ints).
- "DOF2 Final" writes the view's colour target (param_6), reading the resolved copy.

### 181203740: Dof2CBParams_t (0x1034 bytes, cached)

- Rebuilt only when +0x10, +0x14, +0x18, the width, the height (statics 0x1825f7694 / 98 / 9c / b0 / b4) or the k
  (16 bytes at 0x1825f76a0, compared by 1811ceb40) changed, or there is no buffer; the old one released (vtable
  0x228 of DAT_18279cec0), the new created by its vtable 0x218 (size 0x1034, name "Dof2CBParams_t").
- Layout: +0x00 texel (1 / w, 1 / h: `1.0f / (float)w`, 18015a570), +0x08 zeroed (180185170), +0x10 the angle step,
  +0x14 maxblursize (the shader's c1.y: CoC 1 = this many pixels), +0x18 radiusscale, +0x20 k (the D_WRITE_COC
  pass's c2), +0x30 float4 taps[256] (c3..c258), +0x1030 the count (c259.x).
- The taps, floats in this order (disassembly 1812038ac .. 18120397a): a = 0, r = radiusscale; while maxblursize > r:
  if i >= 256 return (no buffer made at all); tap = (V_cosf(a) * texel.x * r, V_sinf(a) * texel.y * r, r - 0.5,
  r + 0.5); a += step; r += radiusscale / r. V_cosf / V_sinf are tier0 imports (IAT 0x181aad8b0 / 0x181aad8a8: the
  CRT cosf / sinf, tier0-trig.js). Defaults: 48 taps, r from 0.25 to 4.99.
- The cvars: r_dof2_maxblursize (180127490: handle 0x1825f5ed0, default 5, flags 2), r_dof2_radiusscale (180127530:
  0x1825f5ec0, default 0.25, flags 2); nothing else references either handle.

### dof2.vfx's gather (the final pass; D_COC_TEXTURE reads the CoC from its own texture, else colour .w)

- c0 = sample(uv); cap = c0.w x 2; n = 1; sum = c0.rgb; per tap: s = sample(uv + tap.xy); coc = s.w > cap ?
  clamp(s.w, 0, cap) : s.w; sum += lerp(sum / n, s.rgb, smoothstep(tap.z, tap.w, coc x c1.y)); n += 1; out =
  (sum / n, 1). Samplers clamp, MinMagLinearMipPoint (bilinear); no blending, no depth test (dof2_states).
- The offsets are in D3D's uv (the vertex shader flips y): GL's are (x, -y).
- Seen in the browser 2026-11-16: a 1v1 competitive custom lobby (de_inferno, no bots) made over two raw lobby
  sockets, each tab joining with its own seat token: bit 8 up, the intro's setDof(-100 / 0 / 100 / 450, tilt 0.5),
  48 taps at 1600 x 900, the lens normal in view space (0.00006, -0.0243, -0.9997), the far buildings softened
  against the same frame drawn with the DoF off.

## Still unread

- the spots' econ items on the models (weapon skins, gloves: not drawn here)
