# The flashbang's blindness, ring and screen overlay (traced 2026-11-16)

What a flashbang does to the players who see it: the server's RadiusFlash / Blind / Deafen and the client's flash
state, alphas and the FlashbangOverlay layer with its shader. Server addresses are server_20261105.dll, client ones
client_20261015.dll (both in the Ghidra project). Ported in `sim/src/game/flash.rs` (RadiusFlash, PercentageOfFlash),
`web/src/cs2web/sim/flash.js` (Blind, Deafen's pick, the client callbacks and alphas, the viewer's opacity),
`web/server/cs2web/grenades/flashbang.js` (the detonation, the netvar events), `web/src/cs2web/client/fx/flash-view.js` (the overlay pass).
Check: `node web/server/cs2web/grenades/flash-test.mjs`; the flashed animation on the hitbox graphs:
`node web/server/cs2web/combat/flashed-pose-test.mjs`.

## Server

- **CFlashbangProjectile::Detonate `1803a4a80`**: `flashbang_detonate` (userid, entityid, x / y / z), then
  **RadiusFlash(abs origin, grenade, thrower (1808c6250), 3.0 (0x40400000), ..., 0x40, &+0xb44, &+0xb45)** (the two
  bytes count flashed enemies / teammates for the stats), Flashbang.Explode, the thrower's stats (+0x1bc).
- **RadiusFlash `1803a7410`**: origin.z += 1.0; `k = 3.0 / 3000` (3000 = 0x181daa828, a float in .data); the entities
  in a 3000 u sphere (FindEntityInSphere 180bfd170, the thrower or the grenade as attacker `plVar15`). Each player pawn
  (vfn 0x558): `pct` = PercentageOfFlashForPlayer; `0 < pct`: `d = |origin - eye|` (eye vfn 0x5e8, `(dy dy + dz dz)
  + dx dx`, sqrtss), `base = 3 - d x k`; `0 < base`: `fwd` = AngleVectors **181470980** of the eye angles (vfn 0x5f0,
  no punch), `dir` = (origin - eye) normalised (the same length; 1 / len times each; below 1e-17 or above 1e17
  1814738b0), `dot = (f.z d.z + f.y d.y) + f.x d.x`. Tiers by comiss / jb (a NaN falls to the last):

  | dot | hold | fade |
  |---|---|---|
  | >= 0.6 (0x1817b2be0) | base x 1.25 | base x 2.5 |
  | >= 0.3 (0x18178fddc) | base x 0.8 | base x 1.75 |
  | >= -0.2 (0x1817c98dc) | base x 0.5 | base |
  | else | base x 0.25 | base x 0.5 |

  both x pct. The pawn alive (vfn 0xca8, always 1 for CCSPlayerPawn: `mov al, 1`): **Blind(hold, fade, 255)**
  (vfn 0xcd0); with `plVar15` a live player pawn and the victim vfn 0x550: the victim's services (+0xe48) +0x220 = the
  attacker's handle (the flash assist 180913af0 reads it); `dot >= 0` and an enemy (180ad2840): the enemies-flashed
  stat (18095f1c0, 1802ac490); `player_blind` (userid, attacker, entityid, blind_duration = +0xe04); **Deafen(d)**
  (180203510, the distance from the direction's length).
- **PercentageOfFlashForPlayer `1803a6ea0`**: 0 unless a player pawn and not state 8 (+0xd40). `ang` = VectorAngles
  (1814722c0) of eye - origin; AngleVectors 181472530(ang, null, &side, &up), each normalised (`(z z + y y) + x x`).
  TraceShape (180c2f3c0) eye -> origin: fraction exactly 1.0 -> 1.0. Else three points through 1803a4450 (TraceShape
  origin -> point, then eye -> that trace's end, 0.167 (0x3e2b020c) when the second's fraction is 1.0): `up x 50 +
  origin`, `(origin - side x 75) + up x 10`, `(side x 75 + origin) + up x 10`; summed `((a + 0) + b) + c`. DevMsg
  "FLASHBANG: %0.2f".
- **The traces' filter**: CTraceFilter, vtable **0x1817c8b90**, interacts-with **0x2800100001** (solid 0, bit 20,
  csgo_moveable 35, csgo_monster 37), exclude **0x140000** (player 18, bit 20), interacts-as 0, ignore = the grenade and
  the pawn (1801d6c60: their handles +0x20 / +0x24, owners +0x28 / +0x2c, hierarchy ids +0x30 / +0x32), detail layers
  0xffff, object set 0xf, group 3, flags `(x & 0xc9) | 0x49`, iterate entities. Its ShouldHitEntity **1803a7ec0**:
  false for a CCSWeaponBase, CBaseGrenade or CHostage (dynamic casts; RTTI 0x181ebdbe0 / 0x181ebe088 / 0x181ebe0d0).
- **Blind (CCSPlayerPawn vfn 0xcd0 = `1801fef10`** (a bot hook when +0x1508 / +0x1500) -> **`1801fef80`)**: fields
  m_blindUntilTime +0xd38, m_blindStartTime +0xd3c, m_flFlashDuration +0xe04, m_flFlashMaxAlpha +0xe08 (schema.py).
  `until = max(until, (now + hold) + fade x 0.5)` (18017dc70 adds, 1801f6b80); `fade /= 1.4` (0x18179be64); `start
  = now`; `now > old until` (18017e2d0): duration = fade, maxAlpha = alpha; else `d = max((oldStart + duration) - now,
  fade)` (18017dc70, 1801f95b0, 1801783b0), **+ 0.01 (0x18179be54) when d equals the old duration**, maxAlpha =
  max(maxAlpha, alpha). No spectator branch (CS:GO's ScreenFade for observers is gone). Times are GameTime floats.
- **The resets** `1801ffa20` (caller 1801d63e0, unread) and `180249fa0` (the respawn's, from 180249530): now before
  m_blindUntilTime -> the player's DSP back (180feb800(controller, 0.01, 0, 0x12)), m_flFlashDuration 0,
  m_flFlashMaxAlpha 255; both times 0.
- **Deafen `180203510`**: vfn 0xcb0 is `xor al, al` for a pawn, so it always runs: a one-player reliable filter;
  `d < 100`: control.deafenLong + **Flashbang.Ring.Long**, `< 500`: control.deafenMedium + **.Medium**, `< 1000`:
  control.deafenShort + **.Short** (hashes of the lowercased names, MurmurHash2 seeded 0x31415926 ^ length), none
  beyond; the ring through the sound system (1805c4680, no entity 0xffff).
- **No muffle**: no sound event named control.deafen* exists in CS2's paks (csgo and core soundevents, the
  soundevents_manifest.vrman list; checked 2026-11-16), and nothing names dsp_core.vdsp's `core.flashbang.muffle.long
  / medium / short` (presets 134-136: duration 1.6 / 0.2 / 0.1, a type-10 and a 3000 Hz type-7 processor). A flashed
  player's sound is only the ring. The ring events (game_sounds_weapons): explosion_ring.vsnd, volume 0.1, mixgroup
  Explosions, a flat distance curve to 2800, a time-volume curve (Long ends at 4.18 s, Medium 3.0, Short 2.0).

## Client

- Fields (C_CSPlayerPawnBase, schema.py): m_flFlashBangTime +0x14fc, m_flFlashScreenshotAlpha +0x1500,
  m_flFlashOverlayAlpha +0x1504, m_bFlashBuildUp +0x1508, m_bFlashDspHasBeenCleared +0x1509,
  m_bFlashScreenshotHasBeenGrabbed +0x150a, m_flFlashMaxAlpha +0x150c, m_flFlashDuration +0x1510.
- Change callbacks registered by 180c56ae0: **OnFlashDurationChanged** (LAB_180c61df4: `jmp [vfn 0xae8]`;
  C_CSPlayerPawn 0x181c8a138 slot 0xae8 = **180c8eb30** -> **180c8eb70**, then a 0.28..0.34 s random timer at +0x1e18
  (180c666f0, an animation's)) and **OnFlashMaxAlphaChanged** (180c8ed50: stores it).
- **180c8eb70(new)**: build-up false; new != 0: halved unless the local viewer (alive, or observing in-eye: mode 2
  through 1808538e0 / 180853840) passes **180ca1830** (the view camera within a cvar's distance of the pawn's eye:
  first person); a no-op when a demo check (18094dc30) holds and the value is unchanged; old duration <= 0 or
  m_flFlashBangTime <= curtime -> both alphas 1, build-up on, grabbed off; duration = new; m_flFlashBangTime =
  duration + curtime. new == 0: alphas 0, build-up / grabbed off, duration 0, time 0. Then DSP-cleared off (on the
  local pawn too).
- **The think `180c686f0`**: m_flFlashBangTime < curtime or maxAlpha <= 0 -> both alphas 0; else **1808cf060**(start =
  m_flFlashBangTime - duration, now, duration, build-up, maxAlpha, &overlay, &screenshot): build-up: both =
  clamp(((now - start) / **0.094444446** (0x181c1369c: 255 / 45 / 60)) x max, 0, max); else `left = (start + duration)
  - now`: screenshot = clamp((left x max) / duration, 0, max), overlay = (left <= 3 (0x181ac607c) ? (left / 3)^2 :
  1) x max, max(0), min(max); both / 255. The build-up ends when max(curtime - (m_flFlashBangTime - duration), 0) >=
  1808cf1d0 (0.094444446). `cl_display_flashbang_values` (int 0) prints "FLASBANG: Time Alpha Snapshot".
- **The FlashbangOverlay layer `1811d98b0`**: the viewer is the local pawn (180c7c160), or its observer target
  (vfn 0xac0; 1808538e0): opacity 1; observer mode 2 with **180ce2420** -> `r_spectator_flashbang_opacity` (float 0.6,
  0.2..1, handle 0x1825f5e48); modes 1 and 4 -> 0.2; other non-2 modes -> 0.6. 180ce2420 (also gating the spectator
  utility trails 1807c81c0 and target ID's #SFUIHUD_targetid_FLASHED 180eb4260): true when `force_spectator_only_tools`
  (object 0x18257b360, registered at 1800ee0b0) is set; else the local controller (18096a8b0) +0x790 set -> the byte
  0x1825603a0, else its +0x6f0, true when set; else its observer pawn (1809420c0, vfn 0x4f0), 1808d9430 and the engine
  client's 180769bb0 (a demo / HLTV playback check). An ordinary player spectating in-eye gets false: opacity 1.
- **Where it is drawn**: CRenderingPipelineCsgo::AddLayersToView (**1811d9d30**; its layer names in order, fnstrings.py:
  the world passes, MBOIT smoke and translucents, OverlaySmoke, CsgoForward "GameOverlay Particles" (0x1811de377),
  Translucent Screen Space, letterbox, PlayerHealthGlow, GrenadeCamera, then the post-processing **1811e88a0**
  (Histogram Update, Bloom, PostProcessing: the tonemap) called at 0x1811dfb2d, PanoramaAlpha copy / setup, **the
  flashbang overlay at 0x1811e013d**, Fade To Black (0x1811e0181), MagBorder). So the overlay goes on the tonemapped
  image, over the hitmarkers, under the HUD. Drawn while duration > 0 and curtime < m_flFlashBangTime (and two engine checks 1807696e0 / 18076a040 false):
  not grabbed -> 18121beb0 copies the frame (cs_flash_frame_texture_player_%d, RenderingPipelineCsgoFlashbangOverlay;
  CFlashbangResolveLayerRenderer), grabbed on. The draw "FlashbangOverlay" in mode CsgoForward with float4 0x47dc283c =
  overlay x opacity, 0xf0372cc4 = screenshot x opacity, bool 0xe7e6b006 = grabbed before this frame, texture
  0xd163891a = cs_flash_frame_render_target_split_%d. The material: materials/effects/flashbang_overlay/
  csgo_flashbang_overlay.vmat (shader csgo_flashbang_overlay.vfx, g_tColor default).
- **csgo_flashbang_overlay's pixel shader** (lasers-bake --shader-src csgo_flashbang_overlay:
  shaders/vfx/csgo_flashbang_overlay_vulkan_50_features.vcs, PS s0 d0): `out.rgb = pow(clamp(frame, 0, 1), 2.2) x
  lin(g_flFlashbangScreenshotAlpha) x 4 + lin(g_flFlashbangAlpha)`, out.a = 0; `frame` = g_tFlashbangFrame
  (SrgbRead, point clamp) at gl_FragCoord x the view's inverse size; `lin(x)` of saturate(x): `x <= 0.04045 ? x x
  0.0773994 : ((x x 0.947867) + 0.0521327)^2.4`. Render state: no depth, stencil NotEqual ref 3 / read 1 (the
  features file's PSRS block); **the blend is in the pixel shader's render-state program**
  (csgo_flashbang_overlay_vulkan_50_psrs.vcs, every dynamic combo; `lasers-bake --shader-src` now writes it as
  `<name>_states.txt`): BlendEnable, SrcBlend One, DestBlend One, BlendOp Add, alpha Zero / Zero / Add, write mask
  All, **SrgbWriteEnable false**: the output is added to the target's raw (encoded) values, no sRGB conversion on the
  write. (The pixel program's own per-combo VfxRenderStateInfo are defaults, depth on, unused.)
- **The grab `18121beb0`**: the target's size and format (render context vfn 0x150), cs_flash_frame_texture_player_%d
  made in them (remade when the size changes), the FlashbangResolveLayer (vtable 0x181d2ad98) resolving the target
  into it.

## The flashed animation (traced 2026-11-16)

How a flashed pawn's body reacts in third person: one anim graph control parameter, `flashed_amount`, written by
CCS2PawnGraphController::ReflectPawnState on both sides (cs_player_pawngraphcontroller.cpp line 0x7a), read by the
player's root graph (animation/graphs/worldmodel/worldmodel.vnmgraph, baked to public/player/anim/worldmodel.json).
Ported: `web/src/world/anim-graph/params.js` (flashed_amount), fed per body from `client/fx/flash-view.js` (amount)
through `client/core/game.js` -> `world/peers.js` -> `world/body.js` / `body-graph-worker.js`.

- **The parameter's handle**: the controller's constructor (server **180ab48e0**, client **1808bca70**, the same
  code) makes each parameter a { symbol (MakeGlobalSymbol), graph instance, short index (0x1ffff unset) } triple;
  `flashed_amount` is the server's controller **+0x7a0** (instance +0x7a8, index +0x7b0) and the client's **+0x4b8**
  (instance +0x4c0, index +0x4c8). Neighbours: ik_left_foot / ik_right_foot before, aim_angle_pitch after.
- **Server ReflectPawnState `180ae0aa0`** (called from 180ac4e30 with the pawn): is_defusing from pawn +0x14be, then
  **flashed_amount = 1802106c0(pawn)**, set through 180a3d2e0 (the float parameter setter), then the rest
  (+0x670, the weapon 180b1e620, +0x6a0, aim 180ae02f0, 180ae04e0, move type / ladder 180ae0760).
- **1802106c0(pawn)**: now = the GameTime of curtime (180927cb0 with the entity's +0x10 -> +0x38: gpGlobals' curtime
  in a game frame); `buildUp = (now - m_blindStartTime (+0xd3c)) < 180ac8cb0()` (a function returning **0x3dc16c17 =
  0.094444446**: SETA on the comiss); **180ac8b40**(m_blindStartTime, now, m_flFlashDuration (+0xe04), buildUp,
  m_flFlashMaxAlpha (+0xe08), &overlay, &screenshot); returns **the overlay alpha**.
- **180ac8b40** is the server's copy of the client's 1808cf060: both outputs 0; `now > start + duration` (18017dc70
  adds, 18017e2d0 compares: -1) -> nothing; build-up: `(now - start) / 0.094444446 x max` (0x1819269e0) clamped to
  [0, max] (1801f5970), both alphas; else `left = (start + duration) - now`: screenshot = clamp(left x max / duration,
  0, max), overlay = (left <= 3 ? (left / 3)^2 : 1 (0x181780580)) x max, max(0) (1801783b0), min(max) (1801783c0);
  both / 255 (0x181784e18). The server keys it on m_blindStartTime, not the client's m_flFlashBangTime - duration.
- **Client ReflectPawnState `1808e3540`** (called from 180c905e0; C_CSPlayerPawn's graph controller, Client
  Animation budget): is_defusing from pawn +0x1e9a, then **flashed_amount = the pawn's m_flFlashOverlayAlpha
  (+0x1504)** as is (set through 1808492a0), then the rest as the server's. So on a client every pawn's body takes
  its own flash think's overlay alpha (180c686f0 -> 1808cf060), with OnFlashDurationChanged's halving: 180c8eb70
  halves the new duration unless **the local viewer** (the local pawn alive (vfn 0xab8), else its in-eye observer
  target: mode 2 via 180853840 / 1808538e0) passes 180ca1830 (first person). The test is about the viewer only, never
  which pawn changed: in first person every pawn's flash (yours and the bots') runs full length; from a third-person
  view (here: the ghost camera) all are halved. What the client draws is the client's; the server's own value runs
  the server's graph, whose pose places the hitboxes: here `src/cs2web/sim/flash.js` flashedAmount (1802106c0 +
  180ac8b40 on Blind's state at the tick's curtime) in `server/cs2web/combat/combat.js` record -> poses.js poseInput,
  so a flashed pawn's head hitbox turns away as CS2's does (flashed-pose-test.mjs: 6.5 u at flashed_amount 1).
- **The graph** (worldmodel.vnmgraph): control parameter 20 `flashed_amount` (float). A state machine layer
  `flashed` (node 1841, a ModelSpace state machine layer of the root's layer blend) with states Off (1842, an off
  state) and flashed (1843). Off -> flashed when NOT (flashed_amount <= 0.1) (1850 / 1851), flashed -> Off when
  flashed_amount <= 0.1; both transitions 0.2 s, linear, bone mask blend-in 33 %. The flashed state: Blend 1D (1844)
  over move_crouch_amount (node 64) 0..1 between flashed.vnmclip and flashed_crouch.vnmclip (single-frame poses);
  layer weight = FloatRemap(flashed_amount, 0.1..1 -> 0..0.95) (1847); bone mask **Flashed** (1848: clavicle_L,
  arm_upper_L, neck_0, head_0 1.0, spine_3 0.9, spine_2 0.7, spine_1 0.25, clavicle_R 0.2, spine_0 0.1): the left arm
  up over the eyes, the head and chest turned away. And CNmSnapWeaponNode (node 65) takes the left hand off the gun
  while flashed_amount > 0 (nodes-cs.js). The runtime ran all of this already; nothing set the parameter.
- **The order here**: game.js runs every pawn's flash think (FlashView.frame) before posing the bodies (peers.update),
  then the overlay draws from the same alphas. CS2's order of the think against ReflectPawnState inside a frame is
  unread (both per frame; one frame apart at most).
- **The +0x1e18 timer** (180c8eb30 after a duration change > 0; also 180c75890): 180c666f0 restarts a { owner, ...,
  +0x10 start, +0xc length } timer with RandomFloat(0.28, 0.34) (0x3e8f5c29 / 0x3eae147b) when the last one finished
  (its fraction outside (0, 1), 1802803b0). Not a schema field (after m_GunGameImmunityColor +0x1e10); who reads it
  is unread (not the graph's flashed layer, which reads only flashed_amount).

## Stand-ins / unread (TODO(trace))

- 180ce2420's last branch (1808d9430, 180769bb0): read as a demo / HLTV check; false for every player here.
- A window resize mid-flash: CS2 remakes the grab's texture and keeps the grabbed flag (what it then shows unread);
  the port grabs again.
- The client curtime at a netvar callback against the frame's: one clock (the replica's) for both.
- The ShouldHitEntity classes and the ignored grenade / pawn have no bodies in the sim's world; normalize's other path
  (1814738b0); dead pawns aren't flashed (no pawn while dead here); m_iEnemiesFlashed and player_blind's listeners;
  1801ffa20's caller 1801d63e0.
- The flashed animation: the +0x1e18 timer's reader; the client think vs ReflectPawnState order inside a frame; where
  in the server's tick 180ac4e30 runs against the command's movement (here: record(), after the tick's moves); your
  own first-person legs body doesn't take flashed_amount (the Flashed mask has no leg bones, so nothing of it would
  show there).
- A native check against server.dll (an oracle hooking TraceShape, as move_oracle --throw does) isn't written: the
  numbers are from the disassembly and checked by flash-test.mjs's independent formulas.
