# Flashbang: blindness, ring, screen overlay, flashed animation

server_20261105, client_20261015. Shader csgo_flashbang_overlay (shaders/vfx/csgo_flashbang_overlay_vulkan_50_features.vcs,
_psrs.vcs); animation/graphs/worldmodel/worldmodel.vnmgraph; dsp_core.vdsp; game_sounds_weapons.

## Functions

| Address | Module | What |
|---|---|---|
| 1803a4a80 | server | CFlashbangProjectile::Detonate |
| 1803a7410 | server | RadiusFlash(origin, grenade, thrower (1808c6250), 3.0 (0x40400000), ..., 0x40, &+0xb44, &+0xb45) |
| 1803a6ea0 | server | PercentageOfFlashForPlayer |
| 1803a4450 | server | point test: TraceShape origin -> point, then eye -> its end |
| 1803a7ec0 | server | the traces' ShouldHitEntity: false for CCSWeaponBase, CBaseGrenade, CHostage (RTTI 0x181ebdbe0 / 0x181ebe088 / 0x181ebe0d0) |
| 1801d6c60 | server | filter ignore setup (handles +0x20 / +0x24, owners +0x28 / +0x2c, hierarchy +0x30 / +0x32) |
| 1801fef10 -> 1801fef80 | server | Blind, CCSPlayerPawn vfn 0xcd0 (a bot hook when +0x1508 / +0x1500) |
| 1801ffa20 | server | blind reset (caller 1801d63e0, unread) |
| 180249fa0 | server | respawn's blind reset (from 180249530) |
| 180feb800 | server | DSP back (controller, 0.01, 0, 0x12) |
| 180203510 | server | Deafen(d) |
| 1805c4680 | server | sound system emit (no entity 0xffff) |
| 180bfd170 | server | FindEntityInSphere |
| 181470980 | server | AngleVectors (forward) of the eye angles |
| 181472530 | server | AngleVectors(ang, null, &side, &up) |
| 1814722c0 | server | VectorAngles |
| 1814738b0 | server | normalise fallback (< 1e-17 or > 1e17) |
| 180c2f3c0 | server | TraceShape |
| 180913af0 | server | flash assist (reads services +0x220) |
| 18095f1c0, 1802ac490 | server | enemies-flashed stat |
| 180ad2840 | server | enemy test |
| 180ae0aa0 | server | CCS2PawnGraphController::ReflectPawnState (cs_player_pawngraphcontroller.cpp line 0x7a; from 180ac4e30) |
| 180ab48e0 | server | pawn graph controller constructor |
| 1802106c0 | server | flashed_amount(pawn) |
| 180ac8cb0 | server | returns 0x3dc16c17 = 0.094444446 |
| 180ac8b40 | server | flash alphas (server copy of client 1808cf060) |
| 180a3d2e0 | server | float graph parameter setter |
| 180b1e620, 180ae02f0, 180ae04e0, 180ae0760 | server | ReflectPawnState's rest: weapon, aim, ..., move type / ladder |
| 180927cb0 | server | curtime (entity +0x10 -> +0x38) |
| 180c56ae0 | client | registers the change callbacks |
| LAB_180c61df4 | client | OnFlashDurationChanged: `jmp [vfn 0xae8]` |
| 180c8eb30 -> 180c8eb70 | client | C_CSPlayerPawn (0x181c8a138) slot 0xae8: the duration change |
| 180c8ed50 | client | OnFlashMaxAlphaChanged (stores it) |
| 180c666f0 | client | restarts the +0x1e18 timer (also 180c75890) |
| 180ca1830 | client | view camera within a cvar's distance of the pawn's eye (first person) |
| 1808538e0 / 180853840 | client | observer mode / target |
| 18094dc30 | client | demo check |
| 180c686f0 | client | flash think |
| 1808cf060 | client | alphas (start, now, duration, buildUp, maxAlpha, &overlay, &screenshot) |
| 1808cf1d0 | client | 0.094444446 |
| 1811d98b0 | client | FlashbangOverlay layer |
| 180c7c160 | client | local pawn |
| 180ce2420 | client | spectator-tools test (also gates utility trails 1807c81c0, target ID's #SFUIHUD_targetid_FLASHED 180eb4260) |
| 18096a8b0 / 1809420c0 | client | local controller / its observer pawn (vfn 0x4f0) |
| 1808d9430, 180769bb0 | client | a demo / HLTV playback check (taken as) |
| 1811d9d30 | client | CRenderingPipelineCsgo::AddLayersToView |
| 1811e88a0 | client | post-processing (Histogram Update, Bloom, PostProcessing), called at 0x1811dfb2d |
| 1807696e0 / 18076a040 | client | engine checks (draw only when false) |
| 18121beb0 | client | the frame grab |
| 1808bca70 | client | pawn graph controller constructor |
| 1808e3540 | client | ReflectPawnState (from 180c905e0) |
| 1808492a0 | client | graph parameter setter |
| 1802803b0 | client | timer fraction |

## Fields

| Offset | Field |
|---|---|
| grenade +0xb44 / +0xb45 | flashed enemies / teammates count (stats) |
| thrower +0x1bc | stats |
| pawn +0xd38 | m_blindUntilTime |
| pawn +0xd3c | m_blindStartTime |
| pawn +0xd40 | state (8: not flashed) |
| pawn +0xe04 | m_flFlashDuration |
| pawn +0xe08 | m_flFlashMaxAlpha |
| pawn +0xe48 | services: +0x220 the flash attacker's handle |
| pawn +0x14be (server) / +0x1e9a (client) | is_defusing |
| client pawn +0x14fc | m_flFlashBangTime |
| +0x1500 | m_flFlashScreenshotAlpha |
| +0x1504 | m_flFlashOverlayAlpha |
| +0x1508 | m_bFlashBuildUp |
| +0x1509 | m_bFlashDspHasBeenCleared |
| +0x150a | m_bFlashScreenshotHasBeenGrabbed |
| +0x150c | m_flFlashMaxAlpha |
| +0x1510 | m_flFlashDuration |
| +0x1e18 | a timer { owner, ..., +0x10 start, +0xc length } (not schema; after m_GunGameImmunityColor +0x1e10) |
| controller +0x790 / +0x6f0 | 180ce2420's flags |
| graph controller | flashed_amount: server +0x7a0 (instance +0x7a8, index +0x7b0), client +0x4b8 (+0x4c0, +0x4c8); index 0x1ffff unset; neighbours ik_left_foot / ik_right_foot before, aim_angle_pitch after |

## Constants

| Value | What |
|---|---|
| 3000 (0x181daa828, float in .data) | flash radius; k = 3.0 / 3000 |
| 0.6 (0x1817b2be0) / 0.3 (0x18178fddc) / -0.2 (0x1817c98dc) | dot tiers |
| 0.167 (0x3e2b020c) | a visible point's share |
| 50 / 75 / 10 | point offsets (up, side, up) |
| 1.4 (0x18179be64) | fade divisor |
| 0.01 (0x18179be54) | added when d equals the old duration |
| 255 | Blind's alpha |
| 100 / 500 / 1000 | Deafen distances |
| 0x31415926 | MurmurHash2 seed (^ length), lowercased names |
| 0x1817c8b90 | the traces' CTraceFilter vtable |
| 0x2800100001 | interacts-with (solid 0, bit 20, csgo_moveable 35, csgo_monster 37) |
| 0x140000 | exclude (player 18, bit 20) |
| 0.094444446 (0x181c1369c, 0x1819269e0, 0x3dc16c17) | build-up time: 255 / 45 / 60 |
| 3 (0x181ac607c) | overlay fade window |
| 0x181780580 / 0x181784e18 | 1 / 255 |
| 0.28..0.34 (0x3e8f5c29 / 0x3eae147b) | +0x1e18 timer length |
| r_spectator_flashbang_opacity | float 0.6, 0.2..1, handle 0x1825f5e48 |
| force_spectator_only_tools | object 0x18257b360, registered 1800ee0b0; byte 0x1825603a0 |
| cl_display_flashbang_values | int 0: prints "FLASBANG: Time Alpha Snapshot" |
| float4 0x47dc283c / 0xf0372cc4 | g_flFlashbangAlpha (overlay x opacity) / g_flFlashbangScreenshotAlpha (screenshot x opacity) |
| bool 0xe7e6b006 | grabbed before this frame |
| texture 0xd163891a | cs_flash_frame_render_target_split_%d |
| vtable 0x181d2ad98 | FlashbangResolveLayer |

Strings / names: `flashbang_detonate` (userid, entityid, x / y / z), Flashbang.Explode, `player_blind` (userid, attacker,
entityid, blind_duration = +0xe04), Flashbang.Ring.Long / .Medium / .Short, control.deafenLong / Medium / Short, DevMsg
"FLASHBANG: %0.2f", cs_flash_frame_texture_player_%d, RenderingPipelineCsgoFlashbangOverlay,
CFlashbangResolveLayerRenderer, "FlashbangOverlay" (mode CsgoForward), materials/effects/flashbang_overlay/
csgo_flashbang_overlay.vmat (shader csgo_flashbang_overlay.vfx, g_tColor default).

## RadiusFlash 1803a7410

1. Detonate: `flashbang_detonate`, RadiusFlash, Flashbang.Explode, the thrower's stats.
2. origin.z += 1.0; entities in a 3000 u sphere (FindEntityInSphere; the thrower or the grenade as attacker `plVar15`).
3. Each player pawn (vfn 0x558): pct = PercentageOfFlashForPlayer; `0 < pct`: `d = |origin - eye|` (eye vfn 0x5e8, `(dy
   dy + dz dz) + dx dx`, sqrtss), `base = 3 - d x k`.
4. `0 < base`: fwd = 181470980 of the eye angles (vfn 0x5f0, no punch); dir = (origin - eye) x 1 / len (the same
   length); `dot = (f.z d.z + f.y d.y) + f.x d.x`. Tiers by comiss / jb (NaN to the last), both x pct:

   | dot | hold | fade |
   |---|---|---|
   | >= 0.6 | base x 1.25 | base x 2.5 |
   | >= 0.3 | base x 0.8 | base x 1.75 |
   | >= -0.2 | base x 0.5 | base |
   | else | base x 0.25 | base x 0.5 |

5. Alive (vfn 0xca8, always 1 for CCSPlayerPawn: `mov al, 1`): Blind(hold, fade, 255); `plVar15` a live player pawn
   and the victim vfn 0x550: services +0x220 = attacker; `dot >= 0` and an enemy: enemies-flashed stat;
   `player_blind`; Deafen(d) (from the direction's length).

## PercentageOfFlashForPlayer 1803a6ea0

1. 0 unless a player pawn and not state 8 (+0xd40).
2. ang = VectorAngles(eye - origin); 181472530(ang, null, &side, &up), each normalised (`(z z + y y) + x x`).
3. TraceShape eye -> origin: fraction exactly 1.0 -> 1.0.
4. Else three points through 1803a4450 (0.167 when the second fraction is 1.0): `up x 50 + origin`, `(origin - side x
   75) + up x 10`, `(side x 75 + origin) + up x 10`; summed `((a + 0) + b) + c`.

Filter: CTraceFilter 0x1817c8b90, interacts-with 0x2800100001, exclude 0x140000, interacts-as 0, ignore the grenade
and the pawn, detail layers 0xffff, object set 0xf, group 3, flags `(x & 0xc9) | 0x49`, iterate entities.

## Blind 1801fef80

1. `until = max(until, (now + hold) + fade x 0.5)` (18017dc70 adds, 1801f6b80).
2. `fade /= 1.4`; start = now.
3. `now > old until` (18017e2d0): duration = fade, maxAlpha = alpha. Else `d = max((oldStart + duration) - now, fade)`
   (18017dc70, 1801f95b0, 1801783b0), + 0.01 when d equals the old duration; maxAlpha = max(maxAlpha, alpha).
4. No spectator branch (CS:GO's observer ScreenFade gone). Times are GameTime floats.

Resets 1801ffa20 / 180249fa0: now < m_blindUntilTime -> 180feb800(controller, 0.01, 0, 0x12), m_flFlashDuration 0,
m_flFlashMaxAlpha 255; both times 0.

## Deafen 180203510

vfn 0xcb0 is `xor al, al` for a pawn: always runs. One-player reliable filter; `d < 100`: control.deafenLong +
Flashbang.Ring.Long; `< 500`: Medium; `< 1000`: Short; none beyond.

No muffle: no control.deafen* sound event exists in CS2's paks (csgo and core soundevents, soundevents_manifest.vrman),
and nothing names dsp_core.vdsp's `core.flashbang.muffle.long / medium / short` (presets 134-136: duration 1.6 / 0.2 /
0.1, a type-10 and a 3000 Hz type-7 processor). The ring events: explosion_ring.vsnd, volume 0.1, mixgroup Explosions,
flat distance curve to 2800, a time-volume curve (Long ends 4.18 s, Medium 3.0, Short 2.0).

## Client state

- 180c8eb70(new): build-up false; new != 0: halved unless the local viewer (the local pawn alive (vfn 0xab8), or its
  in-eye observer target: mode 2) passes 180ca1830 (first person). The test is about the viewer only: in first person
  every pawn's flash runs full; from a third-person view all are halved. A no-op when 18094dc30 holds and the value is
  unchanged. Old duration <= 0 or m_flFlashBangTime <= curtime -> both alphas 1, build-up on, grabbed off; duration =
  new; m_flFlashBangTime = duration + curtime. new == 0: alphas 0, build-up / grabbed off, duration 0, time 0. Then
  DSP-cleared off. 180c8eb30 then restarts the +0x1e18 timer (RandomFloat(0.28, 0.34) when the last finished: its
  fraction outside (0, 1)).
- Think 180c686f0: m_flFlashBangTime < curtime or maxAlpha <= 0 -> alphas 0; else 1808cf060(start = m_flFlashBangTime -
  duration, ...). Build-up ends when `max(curtime - (m_flFlashBangTime - duration), 0) >= 0.094444446`.
- 1808cf060: build-up: both = `clamp(((now - start) / 0.094444446) x max, 0, max)`; else `left = (start + duration) -
  now`: screenshot = `clamp((left x max) / duration, 0, max)`, overlay = `(left <= 3 ? (left / 3)^2 : 1) x max`, max(0),
  min(max); both / 255.

## FlashbangOverlay 1811d98b0

1. Opacity: the viewer is the local pawn or its observer target (vfn 0xac0): 1; observer mode 2 with 180ce2420 ->
   r_spectator_flashbang_opacity; modes 1 and 4 -> 0.2; other non-2 modes -> 0.6.
2. 180ce2420: force_spectator_only_tools set -> true; else local controller +0x790 set -> byte 0x1825603a0; else its
   +0x6f0; else its observer pawn, 1808d9430 and 180769bb0. A player spectating in-eye: false (opacity 1).
3. Drawn while duration > 0, curtime < m_flFlashBangTime, 1807696e0 / 18076a040 false. Not grabbed -> 18121beb0
   copies the frame, grabbed on. Then the draw with the two floats, the bool and the texture.
4. Layer order in 1811d9d30: world passes, MBOIT smoke and translucents, OverlaySmoke, CsgoForward "GameOverlay
   Particles" (0x1811de377), Translucent Screen Space, letterbox, PlayerHealthGlow, GrenadeCamera, post-processing
   1811e88a0 (0x1811dfb2d), PanoramaAlpha copy / setup, the flashbang overlay (0x1811e013d), Fade To Black
   (0x1811e0181), MagBorder: on the tonemapped image, over the hitmarkers, under the HUD.
5. 18121beb0: the target's size and format (render context vfn 0x150), cs_flash_frame_texture_player_%d made (remade on
   a size change), FlashbangResolveLayer resolves into it.

Pixel shader (PS s0 d0): `out.rgb = pow(clamp(frame, 0, 1), 2.2) x lin(g_flFlashbangScreenshotAlpha) x 4 +
lin(g_flFlashbangAlpha)`, out.a = 0; frame = g_tFlashbangFrame (SrgbRead, point clamp) at gl_FragCoord x the inverse
view size; `lin(x)` of saturate(x): `x <= 0.04045 ? x x 0.0773994 : ((x x 0.947867) + 0.0521327)^2.4`.
Render state: no depth, stencil NotEqual ref 3 / read 1 (features PSRS block); the blend is in
csgo_flashbang_overlay_vulkan_50_psrs.vcs (every combo): BlendEnable, One / One / Add, alpha Zero / Zero / Add, mask
All, SrgbWriteEnable false (added to the raw encoded values). The pixel program's own VfxRenderStateInfo are defaults
(depth on), unused.

## The flashed animation

1. Parameter `flashed_amount`, written by ReflectPawnState on both sides; constructors 180ab48e0 / 1808bca70 make each
   parameter { symbol (MakeGlobalSymbol), graph instance, short index }.
2. Server 180ae0aa0: is_defusing from +0x14be, flashed_amount = 1802106c0(pawn) via 180a3d2e0, then the rest (+0x670,
   180b1e620, +0x6a0, 180ae02f0, 180ae04e0, 180ae0760).
3. 1802106c0: now = GameTime of curtime; `buildUp = (now - m_blindStartTime) < 180ac8cb0()` (SETA on the comiss);
   180ac8b40(m_blindStartTime, now, m_flFlashDuration, buildUp, m_flFlashMaxAlpha, &overlay, &screenshot); returns
   the overlay alpha.
4. 180ac8b40: outputs 0; `now > start + duration` (18017dc70, 18017e2d0: -1) -> nothing; build-up `(now - start) /
   0.094444446 x max` clamped [0, max] (1801f5970), both; else as 1808cf060 (max(0) 1801783b0, min(max) 1801783c0).
   Keyed on m_blindStartTime, not m_flFlashBangTime - duration.
5. Client 1808e3540 (Client Animation budget): is_defusing from +0x1e9a, flashed_amount = m_flFlashOverlayAlpha
   (+0x1504) as is (1808492a0), so each body takes its own flash think's overlay (with 180c8eb70's halving).
6. Graph: control parameter 20 `flashed_amount` (float). State machine layer `flashed` (node 1841, ModelSpace, in the
   root's layer blend): Off (1842) and flashed (1843). Off -> flashed when NOT (flashed_amount <= 0.1) (1850 / 1851),
   back when <= 0.1; both 0.2 s, linear, bone mask blend-in 33 %. flashed: Blend 1D (1844) over move_crouch_amount
   (node 64) 0..1 between flashed.vnmclip and flashed_crouch.vnmclip (single-frame); layer weight =
   FloatRemap(flashed_amount, 0.1..1 -> 0..0.95) (1847); bone mask Flashed (1848: clavicle_L, arm_upper_L, neck_0,
   head_0 1.0, spine_3 0.9, spine_2 0.7, spine_1 0.25, clavicle_R 0.2, spine_0 0.1). CNmSnapWeaponNode (node 65) takes
   the left hand off the gun while flashed_amount > 0. No leg bones in the mask.

## Unread

- 180ce2420's last branch (1808d9430, 180769bb0): taken as a demo / HLTV check.
- A resize mid-flash: CS2 remakes the grab texture and keeps the grabbed flag (what it shows then).
- normalise's other path (1814738b0); m_iEnemiesFlashed and player_blind's listeners; 1801ffa20's caller 1801d63e0.
- The +0x1e18 timer's reader (not the graph's flashed layer); the client think vs ReflectPawnState order in a frame;
  where 180ac4e30 runs in the server's tick against the movement.
