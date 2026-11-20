# Traces of CS2's game binaries

CS2's game-side DLLs (server, client, and tier0, engine2, vphysics2, scenesystem, materialsystem2, panorama,
particles, networksystem under them): per subsystem, its functions, field offsets, constants and sum orders.

- **Build**: server_20261105.dll (sha256 70c66e85..., base 0x180000000) unless a file names another. Archive each
  build in `tools/re/binaries/<dll>_<yyyymmdd>.dll` and import it into Ghidra under that name.
- **Format**: each file is Functions / Fields / Constants tables, then the order of operations and sum orders, then
  Unread. Keep it that way: data, not prose.
- **Tools**: [tools/re/game/](../../tools/re/game/README.md).
- **Origin**: cs2web's `docs/trace/` (commit 55bb0752, 2026-11-21), cut to the CS2 data. A "cs2web's <path>"
  mention names that project's file. CS:GO notes are in [../csgo/](../csgo/README.md), ze_crazykart's IVP physics in
  [../crazykart/](../crazykart/README.md).
- **Rule**: a reverse session records what it found (addresses, offsets, slots, constants, sum orders, what's
  unread) in the subsystem's file, and any general helper in the tables below, in the same change.

## The files

115 files.

| File | Subject |
|---|---|
| [accolades](accolades.md) | End-of-match accolades |
| [aim-ik](aim-ik.md) | Aim IK (CNmAimCSTask) |
| [aim-punch](aim-punch.md) | Aim punch (recoil and flinch) |
| [anim-graph](anim-graph.md) | Anim graph runtime (NmGraph) |
| [armsrace-hud](armsrace-hud.md) | Arms Race HUD (client) |
| [armsrace](armsrace.md) | Arms Race (CS2's gun game) |
| [auto-exposure](auto-exposure.md) | Auto exposure (the histogram, CTonemapSystem, the volume's values) |
| [barn-lights](barn-lights.md) | Runtime lights ("barn lights"): the GPU record and the shader loop |
| [blood](blood.md) | A player's blood |
| [bot-takeover](bot-takeover.md) | Bot takeover |
| [box-hull](box-hull.md) | A cooked axis-aligned box hull (RnHull_t) |
| [buy](buy.md) | Buying (CanPlayerBuy, buy time, buy zones, the buy command, the buy menu) |
| [c4-shockwave](c4-shockwave.md) | The C4's blast: CS2's baked shockwave and the RadiusDamage fallback |
| [c4](c4.md) | The C4: bomb sites, planting, the planted bomb, defusing, the explosion, the round |
| [cases](cases.md) | Cases (weapon cases, their loot, the unlock) |
| [cs2-materials](cs2-materials.md) | World material shaders |
| [damage-prediction](damage-prediction.md) | Damage prediction (the shooter's own hit effects, predicted kills, the server's half) |
| [death-cam](death-cam.md) | Death camera |
| [death-notice](death-notice.md) | player_death: the server's fields, the assist, the client's death notice |
| [death-panel](death-panel.md) | The death panel ("killed by") |
| [decals](decals.md) | Projected decals: the client's decal record |
| [drops](drops.md) | Weapon drops |
| [entity-index](entity-index.md) | Entity indices: how CS2 hands them out |
| [env-explosion](env-explosion.md) | env_explosion's effect (CMsgTEExplosion) |
| [equip-info](equip-info.md) | The top bar's equipment strip (hudteamcounter snippet-equipment-info) |
| [fire-gate](fire-gate.md) | A gun's fire gate: clocks, PrimaryAttack, burst, zoom, silencer, deploy |
| [flashbang](flashbang.md) | Flashbang: blindness, ring, screen overlay, flashed animation |
| [fp-legs](fp-legs.md) | First-person legs |
| [frame](frame.md) | The server frame: game-system events, usercmds, thinks |
| [friends](friends.md) | Friends list, friend codes, Recent Teammates, Looking to Play |
| [gradient-fog](gradient-fog.md) | env_gradient_fog (C_GradientFog) |
| [grenades](grenades.md) | CS2 grenades |
| [holster](holster.md) | Holster: putting a weapon away |
| [home-menu](home-menu.md) | CS2's main menu: the left column, the play menu, the rating tile |
| [hostage](hostage.md) | Hostage Rescue: CHostage, the carry, func_hostage_rescue, the round's rules and money, the HUD |
| [hurt](hurt.md) | Map damage, heals, filters, a few base inputs |
| [inferno-client](inferno-client.md) | C_Inferno on the client: the ground fire particle |
| [inferno-spread](inferno-spread.md) | Inferno spread (server CInferno: think, CreateFire) |
| [inputs](inputs.md) | The input dispatch and the classes' input tables |
| [intermission](intermission.md) | The map's end: time limit, GoToIntermission, the end-of-match cue |
| [io-queue](io-queue.md) | Entity I/O event queue |
| [io-targets](io-targets.md) | I/O targets and connections |
| [kill-cards](kill-cards.md) | Kill cards above the health / ammo panel |
| [knife](knife.md) | The knife: its swing's sounds and its gate |
| [knockback](knockback.md) | ZR's knockback |
| [land-dip](land-dip.md) | The landing dip |
| [loading-screen](loading-screen.md) | Loading screen |
| [lobby](lobby.md) | CS2's lobbies, invites, Looking to Play and the map pick |
| [match-pause](match-pause.md) | Halftime, tactical timeouts and the surrender vote |
| [matchmaking](matchmaking.md) | Matchmaking, as the client and server show it |
| [math-counter](math-counter.md) | math_counter (CMathCounter) |
| [menu-anim](menu-anim.md) | Main menu characters and scene (uimodel graph, de_dust2_vanity) |
| [menu-look](menu-look.md) | The main menu scene's look (de_dust2_vanity's post volume, the agents' textures) |
| [momentary](momentary.md) | CMomentaryRotButton, ObjectCaps and PlayerUse's continuous use |
| [mouse](mouse.md) | The mouse to the view angles |
| [move-oracle](move-oracle.md) | Running server.dll's movement natively (the movement oracle) |
| [movement](movement.md) | Player movement (CCSPlayer_MovementServices) |
| [movers](movers.md) | The movers' own moves: CBaseToggle, CBaseDoor, CRotDoor, CFuncMoveLinear, CFuncRotating |
| [music-volume](music-volume.md) | Music volume: the csgo_music stack, snd_musicvolume, snd_music_mode, `volume` |
| [muzzle-flash](muzzle-flash.md) | A gun's muzzle flash and shell |
| [net-timeout](net-timeout.md) | Connection timeouts (sv_timeout, cl_timeout) |
| [overtime](overtime.md) | Match end, halftimes and overtime |
| [pets](pets.md) | Pets: CS2's chicken pets, the Weekly Care Package |
| [physics-prop](physics-prop.md) | CPhysicsProp (prop_physics, prop_physics_multiplayer) and the script API's Teleport |
| [pickups](pickups.md) | Weapon pickups: the touch, BumpWeapon, +use, the target ID |
| [ping](ping.md) | Player ping (`player_ping`, Mouse 3) |
| [player-sounds](player-sounds.md) | Player and physics sounds (who hears which sound event) |
| [post-layers](post-layers.md) | The post-processing layers |
| [prop-doors](prop-doors.md) | prop_door_rotating (CPropDoorRotatingBreakable <- CPropDoorRotating <- CBasePropDoor) |
| [pulse](pulse.md) | Pulse: point_pulse graphs on CS2's official maps |
| [push](push.md) | Movers and players: the pusher, the ground's velocity, base velocity |
| [radio](radio.md) | Radio, chat wheel, places, a match's voice cvars |
| [ragdoll-settle](ragdoll-settle.md) | Ragdoll settling: prop_ragdoll's sleep rule |
| [ragdoll](ragdoll.md) | A player's death ragdoll |
| [reload](reload.md) | A gun's reload and the silent reload |
| [round-restart](round-restart.md) | The round restart: what CleanUpMap removes and what it leaves |
| [round-sounds](round-sounds.md) | The round's cues: freeze beeps, match announcements, the kill sound, the death cam's sounds |
| [rubikon-colour-joints](rubikon-colour-joints.md) | Rubikon: joints in a graph-coloured island |
| [rubikon-joint-break](rubikon-joint-break.md) | Rubikon: breaking joints, and their break limits |
| [scene-node](scene-node.md) | Scene node: an entity's transform (CGameSceneNode, each entity's m_pGameSceneNode) |
| [score](score.md) | The kill's score: contribution score and deathmatch points |
| [scoreboard](scoreboard.md) | The scoreboard per game mode (CSGOScoreboard) |
| [settings](settings.md) | Settings menu, crosshair codes and drawing, convar defaults |
| [shadows](shadows.md) | Sun shadows: cascaded shadow maps (CSM) |
| [shots](shots.md) | Shots on players (hitboxes, damage, lag compensation, penetration, knife) |
| [skins](skins.md) | Weapon skins: paint kits, StatTrak, knives, gloves, stickers |
| [skybox](skybox.md) | The 3D skybox and the 2D sky |
| [smoke](smoke.md) | CS2's smoke volume |
| [spawngroups](spawngroups.md) | Spawn groups: info_spawngroup_load_unload |
| [spawns](spawns.md) | Spawn spots (team matches) |
| [spec-xray](spec-xray.md) | Spectator xray: glow through walls, grenade trails |
| [spotting](spotting.md) | Spotting and the radar; the transmit cvars |
| [spread](spread.md) | A shot's inaccuracy and spread |
| [spritecard](spritecard.md) | The spritecard: layer channel mixes, bloom-only renderers, motion-vector scale, the 1D lookup, the trail combo |
| [store](store.md) | The Store (the main menu's STORE page) |
| [switchhands](switchhands.md) | switchhands: changing the viewmodel's hand |
| [tagging](tagging.md) | Tagging: the slowdown on being hit |
| [taser-client](taser-client.md) | Zeus x27 on the client (C_WeaponTaser) |
| [team-intro](team-intro.md) | Team intro (CCSGO_TeamIntroMenu, the intro period, the map preview camera path, DoF) |
| [teamid](teamid.md) | The overhead team id and the decorated player name |
| [teammate-colors](teammate-colors.md) | Competitive teammate colours and the match stakes |
| [tilt-twist](tilt-twist.md) | CTiltTwistConstraint (the agents' _TWIST bones) |
| [touch](touch.md) | Touches (triggers, weapons) |
| [tracer-sound](tracer-sound.md) | A bullet passing by you: FX_TracerSound |
| [trains](trains.md) | CFuncTrackTrain and CPathTrack |
| [transmit](transmit.md) | CheckTransmit: which entities a client is sent |
| [use](use.md) | +use: FindUseEntity, IsUseableEntity, the collision property, ObjectCaps, bodies |
| [usercmd](usercmd.md) | Usercmd timing: input history, tickbase, command queue, pacing, interpolation |
| [video-textures](video-textures.md) | Texture detail and the lightmaps' size (video settings) |
| [vote-controller](vote-controller.md) | Vote controller (callvote / vote, CVoteController, CBaseIssue) |
| [warmup](warmup.md) | Warmup period (CCSGameRules) |
| [weapon-select](weapon-select.md) | Weapon selection (slot keys, invnext / invprev, binds) |
| [weapon-selection](weapon-selection.md) | The weapon list's flash on a new weapon (hudweaponselection) |
| [winpanel](winpanel.md) | Round end panel, MVP, fun facts, round end sounds, end of match |
| [world-vis](world-vis.md) | World visibility: what a CS2 map stores per world object, and the LOD switch |

## General helpers in server.dll (2026-11-05)

Small functions many classes call; once known, the decompiler's output of their callers reads easily. Sum orders
from the disassembly.

| Address | What |
|---|---|
| 0x180b55040 | a controller's m_hPawn (+0x4e0) entity: the current pawn (the observer pawn while dead) |
| 0x1801c8ce0 / 0x1801c9d50 | a pawn's controller (+0xc98) / its original controller (m_hOriginalController +0xe14) entity |
| 0x180223410 | CCSPlayerPawn vfn 0xc28: +0xe14 != +0xc98 (a pawn a player controls in a bot takeover) |
| 0x1801cd1d0 | CCSPlayerPawn vfn 0xc20: the pawn's FL_BOT (m_fFlags +0x388 bit 0x10) |
| 0x180a88120 | a controller's m_bControllingBot (+0x8e0) |
| 0x180b764f0 | SetPawn(controller, pawn, 1, 0, 0, 0): the controller's m_hPawn (the bot takeover's swap 180a9c710) |
| 0x18024d860 | State_Transition(pawn, state): 0 active, 6 observer mode, 7 gungame respawn, 8 dormant |
| 0x18023ee80 | a pawn's bot brain on / off (pawn +0x1508, its CCSBot +0x1500 +0x1a8) |
| 0x180cf16a0 / 0x180cee390 | a collision property's interacts-as (+0x18) \|= bits / &= ~bits (each rebuilds the physics' attributes) |
| 0x180cee420 / 0x180cf1730 | a collision property's interacts-exclude (+0x28) &= ~bits / \|= bits |
| 0x180d0e200 | SetCollisionGroup(collision, group): +0x5e, and the layers group 5 / others change (grenades.md "Players and the projectile's filter") |
| 0x1801783c0 / 0x1801783b0 / 0x18017b8d0 | float min(a, b) (`b <= a ? b : a`) / max(a, b) (`a <= b ? b : a`) / clamp(v, lo, hi) (`lo <= v ? (v <= hi ? v : hi) : lo`), all by pointer |
| 0x180460960 | Approach(target, value, speed) on floats |
| 0x180b23cc0 / 0x180b09ee0 | the weapon services' SwitchToNextBestWeapon(services, current, ...) / GetNextBestWeapon (gear slot, then position; a lower gear slot needs a round) (grenades.md "After the throw") |
| 0x180ab76a0 | the tag: a hit's slowdown and stamina (tagging.md) |
| 0x180ae27b0 / 0x180ae28e0 | a pawn's living layers (player, not solid) / its dead ones (solid, excludes player and playerclip) |
| 0x1801cf720 (2026-10-15) | CCSGameStats::IncrementStat(stats 0x181f4ea10, controller, stat id, delta, plain): the player block (stats + slot x 0x1128 + 0x9c) +0 / +0x4b8 (the round) / +0x970, and the team's (+0x44a9c + team x 0x4b8) unless plain; a controller with +0x834 skipped (winpanel.md "Fun facts") |
| 0x1801cafc0 (2026-10-15) | the CCSGameStats player block of a controller (slot x 0x1128 + 0x9c) |
| 0x18017ea80 (2026-10-15) | float compare (a*, out*, b*): -1 b > a, 1 a > b, 0 equal, 0x80 unordered |
| 0x180936450 / 0x180936810 / 0x180936780 / 0x180936e00 (2026-10-15) | a pistol round (game_type 0, no round played or the half's first, GetStartMoney <= 800) / game_type == 1 / game_type == 0 / m_iRoundWinStatus != 0 |
| 0x1813b8ef0 / 0x1813b9ab0 | GameTime(out*, tick, frac): a fraction outside [0, 1) carries whole ticks (V_modff, a negative one borrowing) |
| 0x1813b8fb0 | GameTime a - b (a*, out*, b*) (checked 2026-11-11: rcx and r8 are read, rdx written): the fractions' difference, a negative one + 1 borrowing a tick |
| 0x180b56470 / 0x180b78640 | the controller's m_nTickBase (+0x4b8) / SetTickBase (usercmd.md 3) |
| 0x180c7cb80 / 0x180c7cdb0 | CPlayer_MovementServices RunCommand (vfn 0xc8) / RunCommands (vfn 0xd0): gpGlobals' tick = the tickbase (usercmd.md 3) |
| 0x180dd8a60 | the frame step: ServerPreEntityThink (game systems' slot 0xf8 via the stub 0x18053355c), the think manager's vfn 0 (0x1805b70a0), ServiceEvents, ServerPostEntityThink (slot 0x100, stub 0x1805332fc) (frame.md) |
| 0x1805b70a0 | the think pass: each slot's controller PhysicsSimulate (vfn 0x508) in slot order first, then the think list (frame.md) |
| 0x180cbc9a0 | the controller of a player slot: the entity at index slot + 1, null outside 0..maxClients - 1 |
| 0x180b67390 / 0x180a93970 | CBasePlayerController PhysicsSimulate (vfn 0x508) -> CCSPlayerController OnSimulateUserCommands (vfn 0x878): the usercmds (frame.md) |
| 0x180b54e20 / 0x180b54e50 | a weapon's primary / secondary attack clock as a GameTime (m_nNext*AttackTick / Ratio, 1813b8ef0) |
| 0x1802a4e90 | the spread seed: SHA-1 of the angles and a tick (BaseGunFire passes the attack time's) unless 0x181daae64 holds a custom seed |
| 0x1813b9aa0 | GameTime + 1 tick (in*, out*) |
| 0x180187770 | a float cvar's value (its registration object's address; buy.md). An int / bool cvar is read as `*(handle + 0x58)`, the handle the qword 8 bytes after the object its registration function passes |
| 0x1804afed0 (scenesystem 1112) | a model's LOD level for p pixels: q = 50 / p, the highest i of n - 1 .. 1 whose switch metric t ([L + 0xc0][i]) is > 0 and < q, else 0 (world-vis.md 5) |
| 0x180499ed0 (scenesystem 1112) | a 3x4 matrix's largest axis scale: sqrt of the largest column's squared length |
| 0x18004da70 (scenesystem 1112) | set a render attribute by its token (MurmurHash2 of the lower-cased name, seed 0x31415926) to a vec4 |
| 0x180ca8180 | ClientPrint(pawn, dest, token, arg1, ...): dest 4 = HUD_PRINTCENTER (buy.md) |
| 0x1809aec60 / client 0x1807c3d20 | a weapon vdata's m_aShootSounds find (vdata +0x4f8, key = WeaponSound_t: the table at 0x181956c.., NEARLYEMPTY 12, ZOOM_IN 19); client 0x180d26730(_, weapon, slot, ...) plays a slot (player-sounds.md "Nearly empty") |
| 0x180c86d20 | CPlayer_WeaponServices::GiveAmmo(svc, count, type, quiet): m_iAmmo[type] (+0x68 words) up to vfn 0x148's max, BaseCombatCharacter.AmmoPickup unless quiet (player-sounds.md) |
| 0x180c83dd0 | CRecipientFilter ctor: +0 vtable, +8 the mask 0, +0x10 -1 (no predicting slot), +0x14 0xff (+0x16 "skip predicting" 0); 0x180c8c8d0 applies the prediction rule |
| client 0x180c2d0a0 | FX_TracerSound (tracer-sound.md); client 0x18175d680 IntersectRayWithRay, 0x181742b20 CalcClosestPointOnLineSegment |
| 0x1801b36b0 / 0x1801b3820 | CItemAssaultSuit / CItemKevlar MyTouch (vtable slot 0x9a8): armour, helmet, Player.EquipArmor_* (player-sounds.md "Armour") |
| 0x180961850 | SetGamePhase(rules + 0xf0c, phase): 2 first half, 3 second half, 4 halftime, 5 ended; fires GamePhaseChanged (overtime.md) |
| 0x18092a5e0 | GetStartMoney(rules): warmup's convar, else m_nOvertimePlaying ? mp_overtime_startmoney : mp_startmoney (overtime.md) |
| 0x18093de70 | the teammate colour mode: game_type 0 and game_mode 6 / 1 / 3 / 4 / 2 (teammate-colors.md) |
| 0x180a9b940 | CCSPlayerController's teammate colour assignment (controller, force) (teammate-colors.md) |
| 0x1809108d0 | CCSGameRules::IsWingman: game type (DAT_182125888 vfn 0x98) 0 and game mode (vfn 0xa0) 2 (pulse.md) |
| .data records | a registered Pulse function / cell: { name, title, description, ..., the function } with the function 9 qwords after the name (CCSPointPulseAPI 181da1100.., CPulseCell_* 181e025d0.., 181e8f160..: pulse.md) |
| 0x18090ee00 | AreTeamsPlayingSwitchedSides(rules) from the phase and the overtime count (overtime.md) |
| 0x1813b9090 | GameTime a + b (a*, out*, b*): s = b.frac + a.frac, one tick carried at s >= 1 (s - 1), then V_modff if still outside [0, 1) (movement.md "The modern jump") |
| 0x180ab6ad0 | GameTime three-way compare (a*, out char*, b*): ticks first (-1 when a's lower, else 1), then the fractions (-1 / 1, 0 equal, -128 unordered); inlined the same in the modern jump |
| 0x180d04ee0 / 0x180d04ed0 | CCollisionProperty OBBMins (+0x40) / OBBMaxs (+0x4c) (movement.md "Players' bodies") |
| 0x180c856b0 / 0x180ac6af0 | the movement services' pawn: fills svc+0x38 / returns it (filling it first) |
| 0x180b55410 | (entity, out*): its controller's (vfn 0xb50) entity index - 1, the player slot; -1 for none |
| 0x180fe1050 | (info*, pawn): +0 null?, +1 vfn 0x558 (a player pawn), +2 vfn 0x570, +4 handle, +8 slot (180b55410), +0xc 180ac5e00 (team?), +0x10 m_iTeamNum |
| 0x180b5d1b0 | pawn+0xb28 (observer services) vfn 0xb8 != 0: observing |
| 0x180c70950 | (svc, button, down): the queued button masks svc+0x70 / +0x78 and +0x198 (a forced press / release) |
| 0x180ae10d0 | mv velocity[axis] = v, its acceleration and half-step part (mv+0x108 / 0x114 [axis]) zeroed (mv*, axis, v) |
| 0x180cacba0 | "now" as a GameTime: gpGlobals (181e328d0) tick +0x44, fraction +0x50 |
| 0x180b3baa0 / 0x180b3bbe0 | a weapon's primary / secondary attack clock set `delay` s after now (mode 0), itself (1) or now not earlier (2); the 0.01 / 0.99 snaps (fire-gate.md 1) |
| 0x180b763d0 / 0x180b76450 | SetNextPrimaryAttack / SetNextSecondaryAttack (this, delay, mode): the other clock too with m_bLinkedCooldowns |
| 0x180b5d3c0 / 0x180b5d470 | the primary / secondary attack clock reached |
| 0x180c629e0 | GameTime -> seconds: tick x 0.015625 + frac x 0.015625 |
| 0x180c51bc0 | seconds -> GameTime: r = V_fmodf(s, 1/64), (int((s - r) x 64 + 0.5), r x 64) |
| 0x18017b8d0 | clamp(v*, lo*, hi*): lo when lo > v, hi when v > hi, else v |
| 0x1801cd370 | Length2D: sqrtss(x x + y y) |
| 0x1813b9090 / 0x1813b9230 | GameTime a + b; f32 ticks -> GameTime (V_modff split, a negative fraction borrowing) |
| 0x1813b9870 | GameTime a - f32 ticks (the ticks V_modff-split as 1813b9230, then 1813b8fb0) |
| 0x180308890 | the tick interval: 0x3c800000 (1/64) |
| 0x180cacba0 | gpGlobals' current GameTime: (180927c50's tick, gpGlobals +0x50 the fraction) |
| 0x180b52570 | the controller's interp for the shoot time: 1/64 x (1 + engine vfn 0xc0 / 100) when engine vfn 0xb8 and not a bot, else 1/64 |
| networksystem 0x1800c5c10 | CNetChan vfn 0x50: max(1e-6, the connection's ping ms (+0x8f04) / 1000), the latency in s (docs/game/usercmd.md 8) |
| 0x1803ebc60 | SetPredictionRandomSeed (0x181daae60, the command's random_seed while it runs) |
| 0x1801783b0 / 0x1801783c0 | max / min (maxss / minss: the second operand unless the first is larger / smaller) |
| 0x18017e2d0 | f32 three-way compare (a*, out char*, b*): -1 when b > a, 1 when a > b, 0 equal, 0x80 unordered |
| 0x1802b3130 | SimpleSplineRemapValClamped(v, a, b, c, d): (3 - 2t) t t (d - c) + c, t = (v - a) / (b - a) clamped (a == b: d once v >= b) |
| 0x180a9b240 / 0x180a7a250 | camera services SetFOV(cam, requester, fov, rate, start) / GetFOV (fire-gate.md 6) |
| 0x180c00e80 | a physics surface's game surface properties (CGameSurfaceProperties, 0x20 bytes: +8 bulletPenetrationDistanceModifier, +0x14 gamematerial): surface +0x10 (its index) into DAT_18218e4f8 +0x28 (shots.md 6b) |
| vphysics2 0x1800729f0 / 0x1800729c0 | the surface controller (CVPhysics2SurfacePropertyManager's vtable 0x1803fbe20) vfn 8, find by name hash (miss: *found = 0, the "default" surface), and vfn 0x18, the surface at an index (null outside the list) (shots.md 6b) |
| 0x1809f7840 | a weapon's gameplay activity setter (activity, flags, -, force): a silencer switch's (600 / 601) clocks freed on leaving it (fire-gate.md 7) |
| 0x180b1cd40 | a weapon's graph output: the sampled WPN_* ID events into flags (+0x2b4 action complete, +0x2b8 / 0x2b9 silencer) |
| 0x1801f95a0 | out = *a - xmm2 (subss); 0x18017dc70 out = xmm2 + *a (addss) |
| 0x1809f9910 | the attack clock step (weapon, info, delay, attack): GetWeaponAttackTime, +0x10c0, the +0x38 pull to now, both clocks + delay from themselves (BaseGunFire; the knife with 1.0 / 0.4) |
| 0x1813b9690 | GameTime lerp(out, a, b, f): (a.tick, ticks(b - a) x f) folded; a's own fraction is not added (usercmd.md 10) |
| 0x180d079f0 / 0x180d075d0 | CBasePlayerPawn::PreThink / PostThink (vtable 0x181963748 slots 0xb10 / 0xb18); PreThink walks the pawn's components (+0xb58, next +0x40) calling each one's vfn 0x60 |
| 0x180b1d430 | CCSPlayer_WeaponServices vfn 0x60: the command's input history entries into its 32-record ring (+0x370, head +0x1278, count +0x127c; usercmd.md 10) |
| 0x180ebc010 / 0x180ed23a0 / 0x180ebc9c0 | an interp info's src / dst snapped by its fraction (within eps of 1: src = dst; of 0: dst = src) / valid (0 <= src <= dst, frac in [0, 1]) / built (out, src, dst, frac) |
| 0x18093d680 / 0x18093e970 | mp_solid_enemies != 0 / mp_solid_teammates not 0 or 2 (docs/game/movement.md) |
| 0x181473e90 | AngleQuaternion(QAngle) -> xmm0 quaternion (x, y, z, w) (sim/src/math/mod.rs, exact) |
| 0x1801fe910 | AngleNormalize(a): inside [-180, 180] as it is; else a - floorf(a x (1/360) + 0.5) x 360, maxss(-180), minss(180) |
| 0x180a7aab0 / 0x1802cc150 | the camera services' view punch now: m_vecCsViewPunchAngle (+0x48) x V_expf(-(curtime - (tick +0x54 + ratio +0x58) / 64) x view_punch_decay) while that is > 0 (movement.md "The view punch") |
| 0x180c7e550 | set the view punch (camera, angle*, time*): sv_suppress_viewpunch off; each lane AngleNormalize'd; time null → gpGlobals tick, ratio 0 |
| 0x180a9ef60 | camera services vfn 0xf8: view punch += delta (decayed first, set now) |
| 0x180c71830 | gpGlobals curtime (+0x30) |
| 0x180c8cbc0 / 0x1813aa290 | the pawn's entity index (from its identity's place in the entity list chunks) |
| 0x180c86c00 | the movement services' player slot (180b55410) |
| 0x180ae5650 | TestPlayerPosition(svc, out handle*, mv, at*, group, trace*): the hull (m_bDucked's) at `at` meeting the pawn's interacts-with → the entity's handle, else -1; counts svc+0x648 twice |
| 0x18054ba10 | murmur2 (seed in r8; 0x31415926 for names) over a lower-cased string |
| 0x180c7ba40 | PlayStepSound(svc, origin*, surface*, volume, force): the footstep set's name for the surface, EmitSound to everyone but the player (movement.md "The step sounds") |
| 0x180ae2230 | SetStepSoundTime (CCSPlayer, svc vfn 0x1c0)(svc, type, walking, velocity*): m_flStepSoundTime by type, + 100 ducking |
| 0x180f69780 | EmitSound(out*, filter*, entity index, EmitSound_t*: +0 name, +8 origin, +0x14 volume) |
| 0x180c83dd0 / 0x180c84870 / 0x180c84e00 / 0x180c8b6a0 / 0x180c8b610 / 0x180c84a60 | CRecipientFilter: ctor / AddAllPlayers / AddRecipient(player, with their mode-2 observers) / RemoveRecipient(player and their observers) / RemoveRecipient(controller) / add the HLTV (player-sounds.md) |
| 0x180a77710 | one sound from a pawn to whoever is in earshot (PAS filter 180c83a60 + 180c864b0 at attenuation 0.8), minus a controller |
| 0x1809bff80 | the smoke on a line between two points (the active smoke grenades' sum) |
| 0x18024b730 | a silent pickup: not the freeze period and the pawn slower than 135.2 u/s over the ground |
| 0x1805a9c70 / 0x180575ab0 / 0x1805ad380 | the physics impact sound: volume min(1, speed^2 / 320^2 x scale) / its queue / CPhysicsGameSystem's flush every 0.05 s (hard or soft by the surfaces) |
| 0x180582670 | the physics world's collision / touch events to the entities (VPhysicsCollision vfn 0x278, its sound vfn 0x280 = 180d1a420) |
| 0x180c70700 | (svc, 0): the movement services' buttons cleared (SetupMove under FL_FROZEN) |
| 0x1823ab5c0 | the physics system: vfn 0xb8 → physprops (vfn 8 surface by hash, vfn 0x18 by index) |
| 0x181475b60 | QuaternionAngles(q*, out*) -> MatrixAngles 181473410 (sim/src/math/transform.rs, exact) |
| 0x181475200 | QuaternionMult(xmm0 a, xmm1 b), not normalized: ((a.w b + a.x (b.w, -b.z, b.y, -b.x)) + a.y (b.z, b.w, -b.x, -b.y)) + a.z (-b.y, b.x, b.w, -b.z) |
| 0x1805517a0 | QuaternionAlign (b negated when dpps(a, b)'s sign bit is set) + QuaternionMult |
| 0x18146c2c0 | Bias(x, b): x / ((1 / b - 2)(1 - x) + 1), x clamped to [0, 1], b to [FLT_MIN, 1] (c4.md: the baked bomb damage) |
| 0x180a4d830 | RemapVal(v, a, b, c, d): (v - a)(d - c) / (b - a) + c; a == b: d once v - b >= 0, else c |
| 0x1809f59e0 | (byte* *p, b): clamp(100 Bias(*p / 100, b), 0, 255) as a byte (1809efda0 the int clamp) |
| 0x180b763d0 / 0x180b5ce80 / 0x180b7c540 | (c4.md) SetNextPrimaryAttack; a weapon's owner holding a button mask; a button pressed this command |
| 0x181476030 | ConcatTransforms (CTransform, __vectorcall) |
| 0x181472d90 | RotationDelta(out*, a*, b*): QuaternionAngles(normalize(Q(b) Q(a)^-1)) |
| 0x181472530 | AngleVectors (angles, forward*, left*, up*): the second vector points left (FireBullet: (forward - x left) + y up) |
| 0x1814738b0 | VectorNormalize's slow path, in doubles |
| 0x180a48c80 | Vector length: sqrt((x x + y y) + z z) |
| 0x180991030 | Vector subtract (out = a - b) |
| 0x18029f040 | Vector add (out = b + a per lane) |
| 0x1809f5b10 | Vector += (a = b + a per lane) |
| 0x180a3e840 | Vector scale (out = s v per lane) |
| 0x1801f9480 | Vector "any lane differs" (ucomiss; NaN differs) |
| 0x18014a300 | Vector / QAngle equal (every lane ==) |
| 0x18017b8d0 | Clamp(v*, lo*, hi*): lo > v ? lo : v > hi ? hi : v |
| 0x1801f5970 | Clamp by maxss(v, lo) then minss(., hi) |
| 0x180253910 | CCollisionProperty WorldToCollisionSpace (P -> collision space; the rotated path with the inverse quaternion and 1 / scale, use.md) |
| 0x18014cf50 | CCollisionProperty CollisionToWorldSpace (v -> world: rotation, x scale, + position) |
| 0x180cea780 | the collision-space clamp: max(mins, min(v, maxs)) per lane, ties as written |
| 0x180ce9200 | CCollisionProperty CalcNearestPoint (to collision space, clamp, back) |
| 0x180cfb4b0 | CBaseEntity vfn 0x350 InSameTeam(other) (no class overrides it): other non-null and g_Teams[m_iTeamNum +0x344] of both equal (shots.md 7) |
| 0x180492250 | g_Teams[team] (the team entity), null for a team below 0 or past the list |
| 0x1809b5210 | weapon vfn 0xbf8: vdata m_bCannotShootUnderwater (+0x71f), every weapon class's (fire-gate.md 3) |
| 0x180b23d70 | weapon services vfn 0xf0 Weapon_Switch(weapon, WeaponSwitchReason_t): the same weapon with reason 4 switches hands, holsters and redeploys (switchhands.md 3) |
| 0x1809b5150 | weapon vfn 0xb48 can switch hands: vfn 0xb40 (can be left-handed; CC4 false) && vfn 0xa08 (can be put away; a gun mid-burst without m_bAllowBurstHolster false) (switchhands.md 3) |
| 0x1802804f0 (client) | RemapValClamped(v, A, B, C, D): t = min(max((v - A) / (B - A), 0), 1), C + (D - C) t; A == B: v - B >= 0 ? D : C |
| 0x1802803b0 (client_20261015) | RemapValClamped(v xmm0, A xmm1, B xmm2, C xmm3, D [rsp+0x28]): the same; A == B: v - B >= 0 ? D : C (the top bar's scales, armsrace-hud.md) |
| 0x1803a2430 / 0x1803a2500 (panorama.dll 1112) | sRGB -> linear (x <= 0.04045 ? x / 12.92 : ((x + 0.055) / 1.055)^2.4) / linear -> sRGB (x <= 0.0031308 ? 12.92 x : 1.055 x^(1/2.4) - 0.055), both clamp x to 0..1 first |
| 0x1803a27e0 / 0x1803a2680 (panorama.dll 1112) | RGB -> HSV (h in degrees, +360 when negative; s 0: h 0) / HSV -> RGB (s 0: grey; h 360 -> 0; i = (int)(h / 60)); hsv-transform's (armsrace-hud.md "Panorama's colours") |
| 0x18026fb30 (client) | SimpleSpline(x): x^2 (3 - (x + x)) |
| 0x1815f27f0 / 0x1815f28d0 / 0x1815f2a70 (client) | GameTick a - b / a + b / from a float count of ticks: instruction for instruction server 1813b8fb0 / 1813b9090 / 1813b9230 (usercmd.md 12) |
| 0x180828580 (client) | GameTick as (float)tick + ratio (ticks) |
| 0x1815f2fc0 (client) | GameTick a - 1815f2a70(x): less a float count of ticks |
| 0x180af4df0 (client) | an interpolation info from a 16-tick latch ring (out, ring 0 / 1, &t): the first tick at or below t's tick from the newest, (it, next, ((t - it) + t.ratio) / (next - it)); newest (it, it, 0); empty (-1, -1, 0) (usercmd.md 12) |
| 0x180cfc880 / 0x180ce0280 (client) | the input history entry writer (record, entry, with-interp bool, 1.0, cl_interp_ratio, pawn): ticks, angles, shoot position, cl_interp / sv_interp0 / sv_interp1 / player_interp / the next entry of the command + 180cfc880 + its index (usercmd.md 12) |
| 0x1813b93b0 | two interp infos lerped (out, I0, I1, f): each (src, (dst - src) x frac) folded, time(I0).tick + (time(I1) - time(I0)) x f, I0's ratio dropped (shots.md 5b) |
| 0x180ebdc90 | GameTick three-way compare (a, out char, b): ticks -1 (0xff) / 1, then the ratios -1 / 1 / 0 / 0x80 unordered |
| 0x1813b9930 | GameTick + a float count of ticks |
| 0x180ec1200 | BacktrackPlayer(lc, entity, &{mode, a, b, frac}, records, restore buf, change buf, 1): mode 0 target time, 1 the records at src / dst, 2 between two buffers' records; moves the entity, returns 0 moved / 1 unchanged / 2-4 failures (shots.md 5b) |
| 0x1808845a0 (client 1105) | IsDamagePredictionEnabled (our name; controller): m_bPredictable, the recording branch (the command's flags), sv_damage_prediction_allowed, the net channel's latency <= min(0.07, sv_maxunlag x 0.95), m_bFireBulletsSeedSynchronized (damage-prediction.md 3) |
| 0x180c671a0 (client 1015) | a pawn's GetHealth: m_iHealth less its predicted damage list (+0x34d8, entries { tick, damage }: damage-prediction.md 6) |
| 0x180c63540 (client 1015) | the death ragdoll's push: the force normalized x a magnitude by the weapon name and headshot (ragdoll.md 3) |
| 0x18095aac0 (client 1015) | a ragdoll's force: ApplyLinearImpulse on the bone's part (its parents' when it has none, else part 0), the rest by mass (ragdoll.md 3) |
| 0x180c8a620 / 0x180c8a560 / 0x180c8e230 (client 1015) | LatchRagdollStandingContext / IsRagdollStillStanding / the standing ragdoll's nudge in the pawn's think 180c67e80 (ragdoll.md 5) |
| 0x180c7c1a0 (client 1015) | the local pawn's ragdoll offset: m_vRagdollServerOrigin - abs origin when >= 1 u, else 0 (ragdoll.md 6) |
| 0x180952940 -> 0x180abb430 (client 1015) | an entity's bone index by name: the skeleton's lookup by 0x1801665b0 (MurmurHash2 of the lower-cased name, seed 0x31415926), -1 none |
| 0x180226380 (client 1015) | a vector copied and normalized (18015a140) |
| 0x1803eee10 | TraceBleed (pawn, damage, dir, trace, type): 2-3 jittered 172 u lines from the hit, a blood decal where each lands (blood.md 2) |
| 0x180d1b4e0 | WantsLagCompensationOnEntity (pawn, entity, cmd, mask): mp_friendlyfire / teammate, the mask, sv_lagcomp_filterbyviewangle's radius (sv_maxunlag x m_flMaxspeed x 1.5) and 45-degree view cone (shots.md 5c) |
| 0x1814774c0 | QAngle slerp (out, a, b, f): AngleQuaternion both, the fitted slerp (0x181813da0..), QuaternionAngles: BacktrackPlayer's angles |
| 0x18088a9b0 / 0x1808cd6d0 / 0x180160d10 (client 1015) | GetInterpolationInfo, the Vec3D / QAngle / generic copies: the sample pair at t, the fraction clamped to [0, 2]; its hermite flag never set (the third sample is the older itself; InterpOracle, usercmd.md 12) |
| 0x180159d40 / 0x181744420 (client 1015) | the interpolated Vector's lerp ((b - a) f + a) / the QAngle's slerp (= server 1814774c0) |
| 0x180a0f4b0 | CCSWeaponBase::ItemPostFrame (the knife's: no override): attack 1, attack 3, attack 2, reload, inspect, the no-attack resets (knife.md "The gate") |
| 0x180a0ee80 / 0x1809c0650 | weapon vfn 0xd28 vdata m_bIsRevolver (+0x71e) / vfn 0xc28 vdata m_nZoomLevels (+0x7f4); 0x180a03fe0 vfn 0xcc8: 0xc28 != 0 |
| 0x1809f7840 | a weapon's gameplay activity set (weapon, activity, flags, 0, force): m_iWeaponGameplayAnimState +0xefc, the duration (0xb draw: m_flDeployDuration) to 180a276f0 (fire-gate.md 5) |
| 0x180a276f0 | (weapon, flags, duration, force): t = curtime + duration; flags 1 / 2 the primary / secondary clock (mode 2, or 0 forced), 8 +0xfc0, 0x10 the pawn's m_flNextAttack (later only unless forced) |
| 0x180a1e400 | the weapon's empty sound (PrimaryAttack's refusal, BaseGunFire's dry fire) |
| 0x180927cb0 | (out*, tick): the tick as seconds (x gpGlobals interval), 0 for tick 0 |
| 0x18017e2d0 | float three-way compare (a*, out char*, b*): -1 when b > a |
| 0x180fba770 / 0x1803c4950 / 0x1803e55e0 | TakeDamageOld's result: built from the info / its loss (m_flDamageDealt, m_nHealthLost) / applied to the entity (the carry, m_iHealth; nothing for SUPPRESS_HEALTH_CHANGES alone) (shots.md 4) |
| 0x180cea8c0 | CCollisionProperty world-space AABB (TransformAABB 0x1814759f0 -> 0x181475680 when rotated, + position) |
| 0x181489c20 / 0x181476b30 | IntersectRayWithBox (start, delta, box, tolerance) / its slab test (use.md) |
| 0x180c78850 | the distance a value lies outside [lo, hi] (0 inside): FindUseEntity's look trace z |
| 0x1803eb7d0 / 0x180d10060 | SetMoveType (+0x2f3, + 0x2f2 the collide) / CCollisionProperty SetSolid (+0x5b) |
| 0x180cee640 / 0x180cf1730 | CCollisionProperty: the function mask's solid contact bit off (+0x3f bit 0) / interacts-exclude |= bits |
| 0x1808ad470 | fabs (andps) |
| 0x180460960 | Approach(target, value, speed): value + speed when target - value > speed, value - speed when below -speed, else target |
| 0x1801d3440 | RemapValClamped(v, a, b, c, d): a == b → (v - b >= 0 ? d : c); else clamp((v - a) / (b - a), 0, 1) x (d - c) + c |
| 0x180158e30 | an entity-local vector into world (out*, local*, scaled): rotated by the scene node's quaternion (1803d5fa0 +0x10), x its scale (1803d6f80) when asked; an identity node (18014a300 against 18177bf90) scales only |
| 0x180242350 | SetViewOffset(entity, v*): per axis a changed value clamped to its encoder's range, stored, notified (docs/game/movement.md "The view offset") |
| 0x1803c1030 / 0x1803c1de0 / 0x1803c1f70 | CQuantizedFloatEncoder setup (enc*, name, bits, flags, lo, hi) / quantize (enc*, name, v, out*) / quantize without the special values: round down (1), round up (2), zero exact (4), integers exact (8: the range stretched to 2^(floor(log2(int range)) + 1), the bits raised); movement.md "Found by the movement oracle" (sim movement/quantize.rs Encoder, exact) |
| 0x1803d6fb0 | GetAbsVelocity(entity, out*): +0x38c (recomputed first when m_iEFlags bit 12) |
| 0x180cad5b0 / 0x180cb8770 | the body component's render offset (+0xe8..0xf0): get / set (each axis clamped to +-128) |
| 0x180bf9270 / 0x180c048b0 | an entity's id for a trace filter (-1 for none) / its hierarchy id (0 for none) |
| 0x1802c35a0 | CGameTrace::DidHit: fraction (+0xac) < 1 or start solid (+0xbb) |
| 0x180cb7b90 | the hull table (GetViewVectors): +0 view, +0xc / +0x18 hull, +0x24 / +0x30 duck hull, +0x3c duck view, +0x48 / +0x54 observer hull |
| 0x1801541a0 | CCSPlayerPawn vfn 0x550 IsAlive: m_lifeState (+0x2d8) == 0 |
| 0x1803d90a0 / 0x1803eb070 | GetLocalAngles / SetLocalAngles |
| 0x1803d91a0 / 0x1803eb270 | GetLocalOrigin / SetLocalOrigin |
| 0x1803d6f50 | GetAbsOrigin |
| 0x1803d5f70 / 0x1803d5fa0 | The node's m_nodeToWorld / local transform (CTransform: pos, scale, quat at +0x10) |
| 0x1803d91c0 / 0x1803eb540 | Local velocity get / SetLocalVelocity |
| 0x1803eb230 | SetLocalAngularVelocity(QAngle) (+0x480, stored when a lane differs) |
| 0x1803eb140 | The same from a rotation vector: QAngle (v.y, v.z, v.x) (1803e9710) |
| 0x1803ede40 | CBaseEntity::Teleport (vfn 0x528) |
| 0x180c28110 | CGameSceneNode::SetWorldTransform(node, CTransform*): m_nodeToWorld as given, the abs split from it, the local from it (scene-node.md "VPhysicsUpdate"; sim/src/game/scene_world.rs, exact) |
| 0x180bf1670 | CTransform -> abs angles (QuaternionAngles), abs origin, abs scale (snapped to 1 within 0.001) |
| 0x180c28080 | A CTransform stored as the local (position, QuaternionAngles, scale) through 180c27ec0 |
| 0x180c27ec0 | The tolerant local store (origin, angles, scale each only past its tolerance; marks nothing) |
| 0x1803c3520 | Body transform -> CTransform copy (scale lane 1, then the source's) |
| 0x18017ca50 | CTransform(pos*, quat*, scale) |
| 0x180591730 / 0x180187f50 | CTransform's scale (+0xc) / its position with the w lane zeroed |
| 0x181476300 | CTransform inverse out of line: at scale 1 the position turned by the unnormalised conjugate (not SetAbsOrigin's inline one; math/transform.rs inverse_out_of_line, exact) |
| 0x180cab2d0 | Skeleton: body index -> bone (+0x370 count, +0x378 u16 = m_modelState +0x250), -1 for none |
| 0x180ca8eb0 / 0x1814a7b50 | CModelState: rebuild the body-to-bone maps / part bone-name hashes -> skeleton bones (scene-node.md "VPhysicsUpdate") |
| 0x180cb7d80 / 0x18149f440 / 0x18149f1e0 | Skeleton instance: both poses filled with the model's bind pose / the fill (model skeleton, scale, n, out) / one bone's bind pose (shots.md 3c) |
| 0x180cb69b0 / 0x18149ee90 | The anim graph's pose into the model's bones through the model's map for that graph skeleton (a negative entry leaves the bone alone) / the map's lookup, model+0x440 (shots.md 3c) |
| 0x180ca5f30 / 0x180ca4490 / 0x180ca6840 | CSkeletonInstance: CalcAnimationState (the animation pose, sk+0x130) / the parent-space pose (sk+0x160) / the world-space bone cache (sk+0x1a0) (shots.md 3c) |
| 0x180cab6e0 | A body's bone place: the local bones concatenated to the root, then the input (bone_pose.rs, exact) |
| 0x180588af0 | PullKinematicTransforms' target: the entity through body 0's bone with sv_phys_animated_hierarchy |
| 0x1800759a0 | sv_phys_animated_hierarchy's registration (0x181ff5738, default on) |
| vphysics2_20260924 0x180075b60 | CVPhysics2Interface::SimulateWorlds (vfn 0x80): each world's Simulate (vfn 0) per substep, then vfn 8 (0x180059fe0: the awake set into the server's push list) |
| vphysics2_20260924 0x180048860 / 0x180013210 | CPhysAggregateInstance asleep (every body) / CPhysicsBody asleep: RnBody +0x249 bit 2 |
| tier0_20261103 0x18015eda0 / 0x18015e1b0 / 0x18015d580 | CUniformRandomStreamImpl RandomFloat / GenerateRandomNumber_Locked / GenerateDefaultRandomSeed (the clock) (lib/cs-random.js, exact) |
| 0x1805aeb70 / 0x1805c9530 | CPhysicsGameSystem::PushDynamicTransformsWorker / one aggregate's pose onto its node |
| 0x181472f90 | MatricesAreEqual(a*, b*, tol): the 3x3 rotation only, |a - b| > tol (comiss / ja) -> false (sim/src/math/matrix.rs rotation_is_identity, exact) |
| 0x180d04f60 | CBaseEntity::ObjectCaps (vfn 0xd0): the parent's caps & 0x87 (| 0x80 for a player parent) (momentary.md) |
| 0x1803d9790 | The parent entity (the node's parent +0x38, its owner +0x30) |
| 0x1803d95f0 | m_nActualMoveType (+0x2f5) |
| 0x1803f0260 | VPhysicsGetObject(e, index) |
| 0x1803ea4a0 | SetAbsVelocity: m_vecAbsVelocity (+0x38c) and the local (+0x398) when a lane differs (ucomiss) |
| 0x1803ea860 | SetBaseVelocity: stored when a lane differs |
| 0x180abdab0 | CheckVelocity(svc, mv, name): inf / NaN lanes zeroed, then each velocity lane to +-sv_maxvelocity |
| 0x1803ebff0 | SetWaterLevel(pawn, v): through m_flWaterLevel's encoder (8 bits, integers exact), stored when it differs, then pawn vfn 0x698 |
| 0x1803eb7d0 | SetMoveType(entity, movetype, collide): +0x2f3, +0x2f2, then vfn 0x2b0 (UpdateActualMoveType 1803e5390: +0x2f5) |
| 0x1803c5940 / 0x1803e8520 | m_fFlags add / remove (entity, bits): stored when it changes, then 180536730 (the flags-changed callback) |
| 0x180c26a40 / 0x1803ea3b0 | CGameSceneNode::SetAbsOrigin / CBaseEntity::SetAbsOrigin |
| 0x1801575b0 | CBaseEntity vfn 0x228: m_pCollision (+0x3d8) |
| 0x1813aa290 | an entity's index from its identity's address (the chunks at [0x182331b00] + 0x10) |
| 0x180c868d0 | the weapon services' active weapon (+0x60 its handle) |
| 0x180cf7020 | m_iHealth (+0x2d0) |
| 0x18009a0c0 | CCSGameRules' view vectors (0x1821193a0, 0x6c bytes) static initialiser |
| 0x180f695d0 | an entity's EmitSound(entity, params*, name, ...) |
| 0x181687041 | RandomFloat(stream, lo, hi) (the global stream 0x181e328d8) |
| 0x1803ee6e0 / 0x1803eb9e0 | SetThink / SetNextThink |
| 0x180927cb0 / 0x180927c20 | The entity's current time / its think interval |
| 0x180d0e750 | SetMoveDoneTime (+0x318: -1 or m_flLocalTime + t) |
| 0x1802a66e0 | FireOutput(output*, activator, caller) |
| 0x1803d9c80 | GetVectors(entity, fwd*, right*, up*): the node's world quaternion (+0x270 -> +0x20) turning each basis vector (0x182337ef0 / f10 / f40, filled at startup), t = 2 (q x u), u + w t + q x t in f32 (prop-doors.md) |
| 0x18014a300 | QAngle / Vector exact compare (each lane ==): true when equal |
| 0x180d3f2f0 | CEntityBlocker::Create(origin, mins, maxs, owner, ?) (prop-doors.md SetOpenDirection) |
| 0x1802a7eb0 / 0x1813948e0 | A spawn keyvalue as int / as a variant (name hashed with MurmurHash2) |
| 0x180ce9200 | CCollisionProperty::CalcNearestPoint |
| 0x180253910 / 0x18014cf50 | WorldToCollisionSpace / CollisionToWorldSpace |
| 0x180156f30 | The OBB center ((maxs + mins) x 0.5) |
| 0x18015a2f0 | WorldSpaceCenter (vfn 0x2c8; CCSPlayerPawn doesn't override it) |
| 0x180cb1d50 / 0x1801542c0 | vfn 0x570 IsWorld: CWorld's `return 1`, every other class CBaseEntity's `return 0` (c4-shockwave.md) |
| 0x1802c35a0 | CGameTrace DidHit: fraction (+0xac) < 1 or start solid (+0xbb) |
| 0x180250e50 | UTIL_TraceLine(query, start, end, ignore, interacts-with, group, trace): CTraceFilter 0x18178c240, flags 0x49, no entity iteration |
| 0x180ab55b0 | CTraceFilterPlayerMovementCS(filter, pawn, interacts-with, group): as +0x18 = 0x40000, flags 0x4b, iterating entities (layout: +0x8 with, +0x10 exclude, +0x18 as, +0x38 group, +0x39 flags, +0x40 iterate) |
| 0x180febc70 / 0x180fc5870 | UTIL_ScreenShake (amplitude capped 16, grounded pawns) / ComputeShakeAmplitude ((1 - d / r) x amp, -1 past r) (c4-shockwave.md) |
| 0x180cbbf60 | UTIL_DecalTrace(trace, decal group symbol, 0): a hit with an entity -> the decal system (decals.md) |
| 0x1803ea3b0 | SetAbsOrigin |
| client 0x180376e20 | the decal record from a material's attributes (decals.md) |
| client 0x18022fee0 | the client's UTIL_TraceLine(query, start, end, ignore, interacts-with, group, trace) (ProbeExplosion 180b99e20; pets.md: flags (b & 0xc9) or 0x49) |
| 0x1803d83c0 | CBaseEntity vfn returning (0, 0, -1) (the explosion maker's line direction, negated) (env-explosion.md) |
| client 0x18015a140 | VectorNormalize (client's copy, 2026-10-15): as server 0x180148890, its out-of-range path 18015a207 (settings.md) |
| client 0x18173d3d0 | Bias(x, b): x clamped [0, 1], b [FLT_MIN, 1], x / ((1 / b - 2) (1 - x) + 1) (the grenade line-up's fade) |
| client 0x181a08ff8 / 0x181a09074 | the CRT's floorf / ceilf (the crosshair's) |
| client 0x18174a050 | an sRGB byte colour (packed rgba) to linear floats: c / 255, <= 0.04045 / 12.92, else V_powf((c + 0.055) / 1.055, 2.4) |
| client 0x180c19db0 / 0x180da17d0 | world to NDC through the view slot's matrix (180c19cd0) / NDC to the panel's pixels (settings.md) |
| tier0 0x180008240 / 0x180008300 / 0x180007f90 | V_sincosf / V_tanf / V_expf: the CRT's AMD-libm sinf / cosf / tanf / expf, ported exactly (settings.md "tier0's maths", tier0-trig.js) |
| 0x180d0bb60 | SUB_CallUseToggle (vfn 0x498 = Use(this, this, USE_TOGGLE)) |
| 0x180148890 | VectorNormalize(v*) in place: len = sqrt((y y + z z) + x x); 1e-17..1e17 → (1 / len) x lanes; 0 → (0, 0, 0); else 1814738b0 |
| 0x1814722c0 | VectorAngles(out*, in*): V_atan2f, x 57.29578, + 360 below 0; x = y = 0 → pitch 270 / 90 (sim/src/game/trains.rs, exact) |
| 0x18146b8e0 | AngleDistance(xmm0 a, xmm1 b): a - b wrapped once (<= -180: + 360, > 180: - 360) (trains.rs, exact) |
| 0x18146bdb0 | ApproachAngle(xmm0 target, xmm1 value, xmm2 speed), with its AngleNormalize (floorf 1816c4664) (trains.rs, exact) |
| 0x180e7a450 | FixupAngles(QAngle*): each lane into [0, 360] by +-360 steps (trains.rs, exact) |
| 0x1814732e0 | The ease (1 - V_cosf(p pi)) / 2 (trains.rs, exact) |
| 0x1816c4664 | floorf (static CRT) |
| 0x1803d6de0 / 0x1803d6e10 / 0x1803ea270 | GetAbsAngles (+0xd4) / GetAbsAngularVelocity (a rotation vector (roll, pitch, yaw)) / SetAbsAngularVelocity |
| 0x180bfca30 / 0x180bfc940 | FindEntityByName (a name symbol / a string), first match |
| 0x1813a8ed0 | AcceptInput(target, input name, activator, caller, variant) (immediate) |
| 0x1813ac4d0 | The input dispatch: the class chain's tables (181373b60), then vfn 0x88 (Pulse), then scripts (inputs.md) |
| 0x181373b60 | A class's input lookup: [class+0x28] vfn 1, else the base (class+0x60 -> +0x18), recursively |
| 0x180535520 | The string pool's insert / find: MurmurHash2 seed 0x31415926 of the ASCII-lower-cased text (18054ba10), strnicmp (180524c70) |
| 0x180308890 | The tick interval (0.015625) |
| 0x180cdf210 | Vector x scalar (out, _, v*, xmm1 s): s x each lane |
| 0x18146bb60 / 0x18146bce0 | AngleMatrix(angles*, out matrix3x4) / with an origin as the fourth column (sim math/matrix.rs, exact) |
| 0x18146fe70 | ConcatRotations(a*, b*, out*): the 3x3 product, translation 0 (matrix.rs, exact) |
| 0x180148890 | VectorNormalize(v*) in place: len = sqrt((y y + z z) + x x), x 1/len inside [1e-17, 1e17] (c4_plant.rs, exact) |
| 0x1814720a0 | VectorAngles(out*, forward*, up*): left = up x forward normalised by rsqrtss + a Newton step, yaw / pitch / roll by atan2 (c4_plant.rs, exact on Zen 4) |
| 0x180ab6130 | the use code's max use distance: minss(out[1 + u], player_use_radius, a weapon 128) (use.md) |
| 0x18024b730 | a silent pickup: not the freeze period and 2D speed < 135.2 |
| 0x180ac8330 | GiveDefuser(item services, from touch): item_pickup, Player.PickupWeapon unless silent, m_bHasDefuser (c4.md) |
| 0x180a4d830 / 0x18146c2c0 / 0x1809efda0 / 0x18017b8d0 | RemapVal / Bias / float to clamped int / clamp(v*, lo*, hi*) (bomb_damage.rs, exact) |
| 0x180c86b40 / 0x180c84490 | the player pawn list by index / a controller connected (+0x514 0 or 3) |
| 0x1814a73e0 / 0x180b77df0 | LookupSequence(model data, name) / SetSequence(entity, seq, playback) |
| 0x18092a140 | GetRoundElapsedTime (now - m_fRoundStartTime; 0 in the freeze / warmup) |
| client 0x180af1c20 / 0x180aebb10 / 0x180b19a00 | an entity's render-attribute block (+0x5e8) / remove an attribute / set one (c4.md "The screen") |
| 0x181470010 | ConcatTransforms(a*, b*, out*): row i = ((a_i2 b2 + a_i1 b1) + a_i0 b0) + (0, 0, 0, a_i3) (combat/c4_spin.rs, exact) |
| 0x1814719c0 | the rotation matrix about a unit axis (axis*, degrees, out*): V_sinf / V_cosf of degrees x pi/180 (c4_spin.rs axis_rotation, exact) |
| 0x181472e50 | RotationDeltaAxisAngle(a*, b*, axis*, angle*): the quaternion delta Q(b) Q(a)^-1, its axis and 2 acos(w) in degrees, -180..180 (c4_spin.rs, exact; 181472d90 is RotationDelta, movers.rs) |
| 0x180a28730 | fabsf (andps with the sign mask) |
| 0x18032ee60 / 0x1802d52b0 | Vector2D distance (a*, b by value) / Vector2D length: sqrt(x x + y y) |
| tier0 imports | 0x18176a590 V_acosf (sim math/acos.rs, exact against tier0 2026-11-03), 0x18176af00 V_sinf, 0x18176b118 V_cosf, 0x18176a598 V_sincosf (math/crt.rs) |
| 0x181473aa0 | VectorTransform (__vectorcall: point xmm0, rows xmm1..3): (t + y m1) + (z m2 + x m0) (matrix.rs, exact) |
| 0x181473a60 | VectorRotate (the same without the translation) |
| 0x181471990 / 0x181473410 | MatrixAngles(matrix*, out*) (matrix.rs matrix_angles, exact) |
| 0x1814750b0 | QuaternionMatrix(q*, out matrix3x4) |
| tier0_20261103 0x1801a5860 / 0x1801a58c0 | CUtlSymbolTable::AddString(this, out sym*, str, created*): an existing string returns its symbol; else (count < 0xfffe) appended: +0x20 the string vector's count + 1 (winpanel.md "The sets' count") |
| tier0_20261103 0x1801a5300 | CUtlSymbolTable constructor: +0x20 count 0, +0x28 data, +0x30 / +0x34 the vector's allocation / flags, +0x38 the pool, +0x58 case-insensitive |
| 0x181478260 / 0x181478d90 | VMatrix from angles (angles*, out*) -> 181478d90(out, origin*, angles*): AngleMatrix's 3x4 (181472530's products, V_sincosf) + the row (0, 0, 0, 1); 181478260 passes the origin 0x18177bf80 (0) (grenade_spin.rs, exact) |
| 0x181478230 | VMatrix rotation about a unit axis (out*, axis*, degrees): 1814719c0 + the row (0, 0, 0, 1) (grenade_spin.rs, exact) |
| 0x181478690 | VMatrix multiply (a*, b*, out*): out = a b, ((a_i0 b_0j + a_i1 b_1j) + a_i2 b_2j) + a_i3 b_3j; copies an operand that aliases out (grenade_spin.rs, exact) |
| 0x181478b30 | VMatrix MatrixAngles (m*, out*): as 181473410 on the 4x4's rows (grenade_spin.rs via matrix_angles, exact) |
| 0x1808c6250 | GetThrower: m_hThrower (+0xaa8) through the entity list, else the owner (+0x3e4) (grenades.md "The spin") |
| 0x1808d6480 | SetThrower(projectile, pawn): +0xaa8 the handle, +0xaac, +0xac4 set once (grenades.md "The spin") |
| 0x180cec250 | CreateEntityByName + spawn from keyvalues (class, origin*, angles*, owner): "classname", "origin", "angles", "owner" (the handle), CEntitySpawner::Spawn: the entity's Spawn runs inside (grenades.md "The spin") |
| 0x181dbcd50 | The field type names ({ const char *name; byte type; }: FIELD_VOID ..) |
| 0x1801ab860 | Vector(out, xmm1 x, xmm2 y, xmm3 z) |
| 0x180bc3df0 | A float output's Set(output*, value*, activator, caller): stores the value (+0x18) and fires |
| 0x180ade3a0 / 0x180ac2cf0 | PlayerUse (CCSPlayer_UseServices) / its use pick (docs/game/momentary.md, pickups.md) |
| 0x180bef630 → 0x18137f420 → 0x18137f1a0 | CreateEntityByName → the entity system's create by class → create (networked or not, a forced handle) (entity-index.md) |
| 0x18137d5d0 / 0x18137cd30 / 0x181385050 | AllocateEntityIdentity / the list's slot (the networked FIFO at list +0x238) / the identity's release (entity-index.md) |
| 0x18137d1c0 / 0x180c065e0 | a new chunk of 512 identities (random serials) / PreservePlayerNetworkables (indices 0..maxplayers kept off the queue) |
| 0x1821ba1c0 | the CCSGameRules pointer (vtable 0x1818c5450; +0xd8 m_bFreezePeriod, +0xc8 m_bGamePaused: movement.md "The freeze period") |
| 0x180aba720 / 0x180adc860 | the pawn's "can move" (vfn 0xcb8) / the movetype switch's can't-move branch (movement.md "The freeze period") |
| 0x1809562c0 / 0x180913f80 | the round's times (m_iRoundTime, m_iFreezeTime) / the Think's freeze-period expiry (round_freeze_end) |
| 0x18093df00 / 0x18093dd30 | the gamerules' matchmaking-mode test / a per-pawn freeze exception (m_bIsValveDS only) |
| 0x18093d780 → 0x180deb490 | the pause test (gamerules vfn 0x340 180de8750: m_bGamePaused), the base SetupMove's no-input gate |
| 0x180b5ceb0 / 0x180b5ce80 | weapon: button held (m_nButtons +0x58) or pressed this command (180c80ad0) / held only (reload.md) |
| 0x1809f7840 | weapon: set m_iWeaponGameplayAnimState (+0xefc): leaving 800..803 clears m_bInReload; flags -> 180a276f0 (reload.md) |
| 0x180a276f0 | weapon: an action's clocks (flags 1 primary, 2 secondary, 8 +0xfc0, 0x10 m_flNextAttack), delay on, mode (b ^ 1) x 2 |
| 0x1809f5880 | weapon: what is left of both attack clocks times a scale (the silent reload's 2 / 0.5) |
| 0x180c629e0 | a GameTime as seconds: (float) tick x 0.015625 + ratio x 0.015625 |
| 0x1801f95b0 | float a - b (curtime minus a stored time) |
| 0x181470980 | AngleVectors, forward only (angles*, out*): yaw x 0x3c8efa35 into V_sincosf, then pitch; (cy cp, sy cp, -sp); checked natively against combat::knife::forward (grenades.md) |
| 0x180225130 | a vector's length: sqrtss((z z + y y) + x x), 0 when the sum is below 0 |
| 0x18015a2f0 | CBaseEntity vfn 0x2c8, WorldSpaceCenter: m_pCollision (vfn 0x228 = +0x3d8) centre (maxs + mins) x 0.5 (0x180156f30) to the world (0x18014cf50: scale x c + abs origin unrotated), else the abs origin (grenades.md) |
| 0x180b0a570 | CCSPlayer_WeaponServices vfn 0xd0: the pawn's eye angles (vfn 0x5f0) + GetAimPunch 0x180a43b90(doubled) |
| 0x180ad2570 | the jump-throw window (pawn*, extra): 0 < (curtime + extra) - pawn+0x1560 <= 0.2 (grenades.md "The jump throw") |
| 0x180e90150 / 0x180e8f1f0 | CBaseEntity::PhysicsSimulate (vfn 0x508: by movetype; 10 = custom -> 0x180e8f1f0 -> vfn 0x720) |
| 0x180e900a0 | PhysicsRunThink: the main think (0x180e8fc10) then each think context |
| 0x1813aa290 | an entity's index for a sound emit (entity*, out*) |
| 0x1803e5db0 | CBaseTrigger PassesTriggerFilters (vfn 0x878): the spawnflag tests, then the filter (hurt.md) |
| 0x180fba3a0 | CTakeDamageInfo's constructor (info*, inflictor, attacker, ability, damage, type, custom) |
| 0x180154650 | MurmurHash2 (data, length, seed): CUtlStringToken with seed length ^ 0x31415926 (hurt.md) |
| 0x180180300 | an entity's scene node SetParent (node, parent node, attachment token, transform or null) -> 180be92e0 |
| 0x180526210 | VectorNormalize(v*) in place, returns the length: sqrt((y y + z z) + x x), 1 / len x each in 1e-17..1e17, else 1814738b0 (smoke.md) |
| 0x1801783b0 | max(a*, b*): b when a <= b, else a (smoke.md) |
| 0x1809af7d0 | smoothstep(a, b, t): x = clamp((t - a) / (b - a), 0, 1); ((3 - (x + x)) x x) x x (smoke.md) |
| 0x1808ad470 | fabs of two packed floats (& 0x7fffffff7fffffff) |
| tier0 0x180007cf0 | V_qsort: jmp to the UCRT qsort 0x1802b0290 (cutoff 8 selection short sort, median of three; src/lib/msvc-qsort.js) (smoke.md) |
| tier0 0x180007f50 / 0x180008280 | V_cosf / V_sinf: jmps to the CRT cosf 0x1802e0d70 / sinf 0x1802e6570 (tier0_20261103) |
| 0x180be8f60 | the game surface entry's parser (scripts/surfaceproperties_game.txt): maxspeedfactor +0, jumpfactor +4, isstairs +0x19, isslippery +0x1a, allowsmokethrough +0x1b, reflectbullets +0x1c, reduceweaponimpact +0x1d, bulletspenetrate +0x1e, gamematerial +0x14 (smoke.md) |
| 0x180c07590 | the game surface table's grow: each new entry 1, 1, 1 (+0, +4, +8), +0xc 0.5, +0x14 0xffff0043, +0x18.. zero (smoke.md) |
| 0x1809ae490 / 0x1809b46d0 / 0x1809b91a0 / 0x1809b8fc0 | CUtlHashtable<u16>: insert (lookup, grow at 3/4, place) / displace along the chain / rehash (pow2 >= max(want, min)) / place without growth (smoke.md "The brick order"; src/lib/utl-hashtable16.js) |
| 0x1803260c0 | the bots' segment-in-sphere length (r^2, pos, a, b): the sphere at pos + 60 z, -1 both ends in, else 2 sqrt(r^2 - d^2) (smoke.md "The bots' smoke test") |
| 0x18032b710 | CBotManager: a grenade's list entry's radius (+0x20) set (TheBots 0x181fa5e10; the smoke's 166 at its pop) |
| 0x18034d880 / 0x1803443c0 | CInferno: the burning fire a point is at (tolerance, line check) / the line from a fire to a point (centre + 30 z, the centre, then 30 z above the point) (smoke.md "A smoke over a fire") |
| scenesystem 0x1804969e0 | a view frustum slice between planar depths d0 / d1: its 8 corners (1804a8770 twice) in world space, returns the largest corner-to-corner distance (shadows.md) |
| scenesystem 0x1804945c0 | sorts a float range ascending (the cascade splits) (shadows.md) |
| scenesystem 0x18004d270 | a view attribute's value by its hash, else the default passed (shadows.md: 0x7b2a64e1 the shadow distance, 0xb506b94b / 0xb7a3d0d5 the visible / caster distances) |
| client 0x180dfd3d0 | the video settings' four level KeyValues (Low .. Very High), built by 180df13a0 / 180df1820 / 180df0f20 / 180df1ca0 (shadows.md) |
| client 0x18015c5e0 / 0x18015a220 | GameTime a - b (two floats) / clamp(x, lo*, hi*) (armsrace-hud.md "Spawn immunity's look") |
| client 0x18075d250 | an entity's "now": gpGlobals->curtime (0x182230090 +0x30), through the gamerules' vfn 0x220 (180ba9260) when they exist |
| client 0x18021a2c0 / 0x18021a140 | an entity and its scene-node children (+0x330: +0x40 first child, +0x48 next sibling, recursive) into a CUtlVector |
| client 0x180941fa0 | an entity's m_hOwnerEntity (+0x520) resolved (null when none) |
| client 0x1811fef80 | the per-view PerViewConstantBufferCsgo_t fill: c4 (+0x40) BlueNoise (textures/dev/blue_noise_256), +0x44 brdf_lut, c11 (+0xb0) the noise's size - 1; the dev texture table 0x1811cba30 (name -> handle global) |
| 0x180bf7da0 | the entities in a sphere (physics query, filter, out list of 0x70-byte records +0x18 the handle) |
| 0x180cfb4b0 | CBaseEntity vfn 0x350 InSameTeam(this, other): g_Teams[+0x344] of both (180492250, null outside the list) equal (armsrace.md "The Zeus") |
| 0x180ad2840 | the pawn's is-enemy test (attacker, other): mp_teammates_are_enemies (0x18211a6d8 +0x58) or the teams differ (armsrace.md) |
| 0x180ee3da0 | the lag compensation job filter's vfn 0 (vtable 0x1819cf9b8): WantsLagCompensationOnEntity then the radius (+0x30; 0 everyone, else \|origin - start\| <= radius + 1024) |
| 0x180b51910 | an entity's attachment's world transform by name (MurmurHash2 0x31415926 -> 180cb4610 the index -> 180cabc70 the bone cache's slot); false: the entity's own transform |
| 0x18015a2f0 | CBaseEntity vfn 0x2c8 WorldSpaceCenter: the collision box's centre in the world (abs origin without one) |
| 0x18157ff20 | CGameTrace's contact point for a sphere / line ray: (end + centre) - radius x normal (cached at +0x9c, +0xbc set) |
| 0x180a1e400 / 0x180b763d0 | PlayEmptySound (ChargeNotReady / ClipEmpty_Pistol / _Rifle, once per command +0xf34) / SetNextAttack(delay, mode): the primary clock delay from now, the secondary too with linked cooldowns (taser-client.md) |
| 0x180ab9620 | CCSPlayer_ItemServices CanAcquire(item, method, out limit): its ladder and return codes (armsrace.md "Buying the Zeus") |
| particles.dll 2026-11-12 0x18015d710 / 0x180206810 | C_INIT_InitSkinnedPositionFromCPSnapshot / C_OP_MovementSkinnedPositionFromCPSnapshot (taser-client.md; Ghidra /particles_20261112.dll) |
| 0x1814a2730 / 0x181475200 | an attachment's world transform from its influences (position (C + (w t + o)) s + p summed by weight; rotation q x r hemisphere-flipped, blended by 1814746a0) / quaternion multiply q x r, its lane sums (armsrace.md) |
| 0x180fe1050 / 0x180a79ab0 | the other's info for 180ad2840 (null, pawn, handle, player slot, team) / a controller's team (sv_coaching_enabled's coached team for a spectator) |
| 0x1802c4430 | CCSBot::EquipBestWeapon: gear slot 0 (bot_allow_*), 1 (bot_allow_pistols), else the first weapon of gear slot 2 (armsrace.md) |
| particles.dll 0x1800a2b90 / 18035c940 / 18035ec60 | the skinning blend's weighted sum (1: copy; 2+: w1 M1 + w0 M0 ...) / 3x4 multiply / a point through a 3x4 ((m3 + m1 y) + (m2 z + m0 x)) (taser-client.md) |
| client 0x1800ddf70 | hud_fastswitch's registration (0x18256aeb0, default 0): 3 makes slot2 / slot4 cycle and slot3 send phys_swap (taser-client.md) |
| 0x180d0e5d0 / 0x180d0e730 | SetHealth (+0x2d0) / SetMaxHealth (+0x2d4), networked (pets.md "Hurt and killed") |
| 0x1803ebce0 | (entity, takes damage byte +0x2e0, flags +0x2e8) |
| 0x1803ed610 | CBaseEntity::TakeDamageOld: floor(damage) with the fraction carried (+0x2dc), health -= it, before > 0 and after <= 0 -> life state 1 and Event_Killed (vfn 0x418; a true return calls vfn 0x420) |
| 0x18014d780 / 0x18014e660 | EyePosition (abs origin + GetViewOffset) / GetViewOffset (m_vecViewOffset +0x818) |
| client 0x18093c660 / 0x18015fab0 / 0x180160770 | the pawn's EyePosition (vfn 0x568: vehicle / observer cases, else 18015fab0) / abs origin + vfn 0x5a0 / vfn 0x5a0: m_vecViewOffset (+0xf60) through its interpolated var (land-dip.md) |
| client 0x180c671d0 | CalcView's landing dip on the camera origin (land-dip.md) |
| 0x181473df0 | (out, v, yaw degrees): v turned about z by the yaw (z kept) |
| 0x180903d10 / 0x1809036a0 / 0x1809033b0 | MSVC std::sort's _Sort_unchecked (first, last, ideal, less) over 4-byte handles / its insertion sort (32 or fewer) / _Guess_median_unchecked (spawns.md) |
| 0x180904350 / 0x180904130 | MSVC std::stable_sort over 4-byte / 8-byte elements (a temp buffer, 32 or fewer an insertion sort: 0x1809036a0 / 0x1809035a0) (spawns.md) |
| 0x1813aa290 | (entity, out*): its entity index from the identity's chunk (+0x10), -1 for none |
| 0x180b563c0 | (controller): CSteamID::IsValid on m_steamID (+0x710): the id or 0 (spawns.md) |
| 0x180916810 | the gamerules' spawn lists' lazy init, once per map (+0xd84 guard): GenerateSpawnPointLists 0x180925a50 (spawns.md) |
| 0x180923bc0 | CCSGameRules::FrameUpdatePreEntityThink: zeroes the frame's deathmatch respawn count (0x180233f10) |
| tier0 0x180140500 | Plat_RelativeTicks: QueryPerformanceCounter, never below its last return (tier0_20261103) |

CBaseEntity fields (schema.py): m_pfnTouch +0x2b0, m_pfnUse +0x2b8, m_pfnBlocked +0x2c0, m_pfnMoveDone +0x2c8
(thinks are think contexts, not a field), m_flSimulationTime +0x32c, m_iHealth +0x2d0, m_nPlatformType +0x2f0, m_MoveType +0x2f3, m_nActualMoveType +0x2f5,
m_flMoveDoneTime +0x318, m_spawnflags +0x360, m_vecAngVelocity +0x480, m_flLocalTime +0x494 (its copy +0x498), the
time scale +0x400, the collision property +0x5e8. Virtuals: Spawn 0x48, Blocked 0x4d8, MoveDone 0x4f8, Teleport
0x528, IsRotatingDoor 0x880 (CBaseDoor), "angles add, not quaternions" 0x628 (CBaseToggle true, CFuncRotating false).

## General helpers in client.dll (client_20261015)

| Address | What |
|---|---|
| 0x1811f75a0 / 0x1811fd000 | the Gaussian bloom chain (downsample, the 4-tap across / down blurs) and its tinted combine (post-layers.md 7) |
| rendersystemdx11 0x1803f37d0 | Source 2 blend mode -> D3D11_BLEND (16 ints: 12 = SRC1_COLOR; VRF names it "InvBlendFactor") (post-layers.md 7) |
| 0x180889e20 | the death cam's ease: t = clamp((e - 1/16) / spec_freeze_traveltime, 0, 1), u = t / 2 + 1/2, ((3u) u - ((u + u) u) u - 1/2) x 2 (death-cam.md) |
| 0x18174a050 | a Color's bytes -> linear floats (out, Color *): each of r g b x 0.00392156886, clamped to 0..1, <= 0.04045 ? / 12.92 : V_powf((c + 0.055) / 1.055, 2.4); alpha not read (gradient-fog.md, barn-lights.md) |
| 0x1801587b0 | clamp(*value, *lo, *hi): maxss then minss (gradient-fog.md) |
| 0x180ae7d50 / 0x180b808e0 / 0x180b7b220 (client 20261015) | Client thinks: (entity, function, time, context) -> the think manager 0x182233c30's add (a linked list, new thinks at the tail; -1293.0 = every frame) and its runner (head to tail, a parent before its child): docs/game/gradient-fog.md "Several fogs" |
| 0x18173cb10 | AngleDiff(dest, src): V_fmodf(dest - src, 360) into [-180, 180) (death-cam.md) |
| 0x181742a00 | VectorAngles: V_atan2f, x 57.2957764, + 360 below 0; (0, 0, z): pitch 270 / 90 (death-cam.md) |
| 0x1817438a0 | (1 - V_cosf(x x 3.1415927)) x 0.5 (death-cam.md) |
| 0x180360720 | CGameTrace DidHit: fraction (+0xac) < 1 or start solid (+0xbb) (death-cam.md) |
| 0x1808a5910 | a camera box sweep (out, pawn, from, to, half-size): (-s..s) box, solid (1), group 5; fraction >= 1 -> to, else endpos (death-cam.md) |
| 0x1801e2ec0 / 0x180ce2950 | WorldToEntitySpace / point_deathcam_bounds' clamp (CTransform inverse, death-cam.md) |
| 0x1808a4520 | RemapValClamped through SimpleSpline (x, a, b, lo, hi): t = clamp((x - a) / (b - a), 0, 1); (3 - (t + t)) * t * t * (hi - lo) + lo; a == b: hi when x >= b, else lo (cases.md: the camera manager's progress) |
| 0x180d119c0 | client: CCSUsrMsg_SendPlayerItemFound's handler: the chat line for an item a player got (method mask 0xe4003e, tokens 182252c00[method - 1], the item name in its rarity's colour) (cases.md "The item found line") |
| 0x181135c10 / 0x181131630 | client: the item schema's rarity definition by value (+4: its colour index) / that colour index's hex string (table 1822532c0, 3 pointers an entry: items_game colors.desc_*) (cases.md) |
| 0x18118e580 | client: an econ item view's display name (item, 1): its description object (+0x200) made on first use, the name by 181131e80 (cases.md) |
| 0x1811a5440 | client: ChatPrintf (chat hud, flags, entindex, fmt, ...): the line vsnprintf'd (0x1000), a trailing newline cut, leading control characters skipped, printed through CCSGO_HudVoiceStatus's chat (cases.md) |
| 0x1809529a0 | LookupSequence(model, &out, name): the sequence index by name, -1 if none (cases.md) |
| 0x1809657b0 | play a sequence on a model (model, seq, ...): SetAnimgraphBool / the icon pose call it (cases.md) |
| 0x1817445e0 | AngleQuaternion (pitch, yaw, roll in degrees -> x, y, z, w; Source's half-angle form) (pets.md "Camera blend") |
| 0x1817463a0 | QuaternionAngles (through the matrix: MatrixAngles; roll kept) (pets.md) |
| 0x18016a3d0 | an entity's local vector to world (its abs rotation quaternion: v + w t + q.xyz x t, t = 2 q.xyz x v; identity skipped; an optional x scale) (team-intro.md) |
| 0x180c6c9c0 | a cubic Bezier's arc length: polyline of 2, 4 ... 128 samples until it changes < tol / 100, four distances a pass (team-intro.md) |
| 0x180cb2100 | the active menu camera (the team intro's, else end_of_match_camera / team_select_camera): HUD and view code ask it (team-intro.md) |
| 0x1811d9d30 | CRenderingPipelineCsgo::AddLayersToView: the frame's layers in order (opaques, translucents, MBOIT, particles, effects bloom 1811d1e80, the DoF 1811f68a0, PostProcessing 1811e88a0) (team-intro.md "Where it runs") |
| 0x181208840 | the colour resolve ("Non-MSAA Resolve PS" / MSAA): with dof2's D_WRITE_COC writes the CoC into alpha ("IntermediateOutputColorResolved") (team-intro.md) |
| rendersystemdx11 0x18042d470 | ImageFormat's info table (24-byte rows: name, bytes, channel bits, flags), indexed by format + 1 (0xf RGBA16161616F, 0x3d R11G11B10_FLOAT, 39 R16F) (team-intro.md "Depth of field") |
| 0x181203740 | Dof2CBParams_t: the DoF's constant buffer and its golden-angle tap spiral, rebuilt when the cvars / size / k change (team-intro.md, world/dof.js dofTaps) |
| 0x180d5a3b0 | the HUD's panels SetHasClass(symbol, bool) (vfn 0x500 on each; StartCamera's HUD_TEAMINTRO_VISIBLE) (team-intro.md) |
| 0x1801b9c30 / 0x1801587b0 | max(*a, *b) / clamp(*x, *lo, *hi) on floats by pointer (read from their uses: team-intro.md) |
| 0x180769bb0 / 0x180769cd0 / 0x180769d30 / 0x180769cf0 | game_type 0 with game_mode 6 / 1 / 3 / 4 / 2; game_type 0; game_type 1; casual 0 / 0 (winpanel.md "Round end sounds") |
| 0x181744420 | the fitted quaternion slerp (CS2's k polynomial, constants 3E5CD035 .. 40639CE0; q = qA (1 - t') + qB (+-t'), normalised; the anim runtime's fslerp) used by the camera manager's angle blend (pets.md) |
| 0x180219a80 / 0x180219a50 / 0x180219ab0 | an entity's abs origin / abs angles / model scale (getters); 0x18022b670 / 0x18022b470 / 0x18022b750 the setters (pets.md: ApplyState, the egg's nest) |
| 0x1809121c0 | CCS2WeaponGraphController::ReflectWeaponState (controller, weapon): the anim graph's weapon parameters, the activity -> action map (c4.md "The graph parameters") |
| 0x1808e3540 | CCS2PawnGraphController::ReflectPawnState (controller, pawn): is_defusing = m_bIsDefusing (+0x1e9a), then ReflectWeaponState (c4.md) |
| 0x1801fea40 | look up a named entry in an entity's keyed handle store (entity +0x10 +0x48: "feed", "placement", "nest" on a vanity chicken) (pets.md) |
| 0x180d42f50 | set a string in that store (the vanity chicken's "feed_anim" request), then vfn 0x150 (pets.md "The feeder") |
| 0x181748480 | CTransform compose: (parent pos with w = scale, parent quat, local pos, local quat) -> (pos, quat): parent.pos + rotate(parent.quat, local.pos) x scale, parent.quat x local.quat |
| 0x18072ed20 | a chicken model's index: V_stristr over { chicken, chick, chicken_polish, chicken_silkie } (181ba52a8), else a number string 0..4 |
| 0x18085d0e0 | the chicken graph controller's post-update: the ACTION_COMPLETED flag from this update's events, flinch cleared |
| 0x180e5e960 | the map panel's SetPetPlacement: none 0, shoulder 1, main-menu-foreground 2, main-menu-background 3, end-of-match 4 |

| 0x18254eae8 | the post-processing interface (CLoopModeGame +0x10, 0x180a24320): vfn 0 -> the system; its vfn 0x68 (slot) the CPostProcessingState, vfn 0x60 (out, slot) the slot's CTonemapSystem (auto-exposure.md) |

## General helpers in scenesystem.dll (scenesystem_20261015)

| Address | What |
|---|---|
| 0x1805f9cc8 | CTonemapSystem's vtable: 0 update(time) -> 18018d440, 0x20 set params 18018d240, 0x28 force 18018d400, 0x40 set luminance 18018d0a0 (auto-exposure.md 3) |
| 0x18018d2a0 | CTonemapSystem's effective min / max / compensation / speeds / range from the controller's, the defaults and the mat_tonemap cvars |

## General helpers in materialsystem2.dll (materialsystem2_20261023)

| Address | What |
|---|---|
| 0x18012ed48 | CPostProcessingState's vtable: 0x08 tick 18005c710, 0x30 compose 180058500, 0x38 layer(resource, group) 180057e50, 0x48 setWeight 18005bff0 (clamp 0..1), 0x50 fadeTo 18005c010 -> 18005c060, 0x88 merge lookups 18005ce80 (post-layers.md) |
| 0x18005a290 / 0x18005b100 / 0x18005b300 / 0x18005bbf0 | the tone map / bloom / vignette / local contrast blends of the weighted layers (post-layers.md 2) |
| 0x18005ded0 | an introsort of an int array, ascending (the state's group list) |

## General helpers in panoramauiclient.dll (the install's, 2026-11-16)

| Address | What |
|---|---|
| 0x1800ff6f0 | CCarousel's `autoscroll-delay` parser: "a, b" durations -> +0x128 / +0x12c (home-menu.md "Map tiles") |
| 0x1800faca0 | CCarousel's autoscroll scheduler: max(a, 0) + RandomFloat(0, b) seconds (home-menu.md) |
| 0x1800fb250 | CCarousel's autoscroll step: the next visible child, mod count, not while its panel has :hover (vslot 0x5f0) (home-menu.md) |

## General helpers in panorama.dll (the install's, md5 df9d91c3, 2026-11-16)

| Address | What |
|---|---|
| 0x1804ccff8 | CUIPanel@panorama's vtable (rtti.py takes `CUIPanel@panorama`) |
| 0x1801117a0 | CUIPanel slot 0x5f0: has :hover (pseudo-class word +0x220 bit 0) |
| 0x180105110 / 0x180105830 | CUIPanel slots 0x5d8 / 0x5e0: add / remove a pseudo-class mask at +0x220 (1 hover, 0x40, 0x100 ...) |
| 0x18013d1f0 | CUIWindowInput::ChangeHoverState: the hover chain's add / remove of mask 1 up to the first already-hovered ancestor |

## General helpers in particles.dll (the install's, PE timestamp 0x6af4a587, 2026-11-16)

| Address | What |
|---|---|
| 0x18035e4a0 | MatrixAngles of a 3x4 (forward, left, up columns): degrees, the 0.001 xy branch (home-menu.md "The particle functions") |
| 0x1801bf980 | fill a float attribute stream with one value for particles 0..n (no clamp) |
| 0x18036ac00 | a vector through a 3x4 matrix (rotation + translation) |

## Methods

| Task | How |
|---|---|
| A function's shape | Ghidra (ReVa) `get-decompilation`; from a string (`Class_API::Input`, a think name, a schema field) `find-cross-references` |
| Sum orders, NaN-sensitive min / max | the disassembly, never the decompiler (it drops register arguments and gets maxss / minss with NaN wrong) |
| A rip-relative constant | read 4 / 16 bytes at the instruction's end + disp (`disasm_consts.py`) |
| A string's users | `strva.py <dll> <string>` -> its VA, then `riprefs.py <dll> <VA>`; a script API's registration names every method, its callback names it again in errors |
| Class, vtable, slot, field, cvar, protobuf | the scanners in [tools/re/game/](../../tools/re/game/README.md) |
| A pure function's exact bits | map the DLL by hand (no loader, no initialisers: fill BSS constants such as the identity quaternion at 0x181f4a000 yourself), bind tier0 / kernel32, call it natively (a thunk for `__vectorcall`); or run it under Unicorn (the `*_oracle.py` scripts, `tier0_link.py` for tier0's maths) |
| A whole subsystem natively | the same mapping with fake objects carrying logged copies of the real vtables, engine calls stubbed or hooked, .pdata registered for real call chains on a fault, int3 watches on counters ([move-oracle](move-oracle.md)) |

Facts found while doing it:

- `bases.py` 2026-11-14, server: CPostProcessingVolume <- CBaseTrigger <- CBaseToggle <- CBaseModelEntity <- CBaseEntity (a post_processing_volume touches as a trigger).
- `vtowner.py`: 180249530 is CCSPlayerPawn's slot 0xaf8. `vslotall.py`: vfn 0xbf8 is 1809b5210 for every weapon class; Deploy 0xa18 has four.
- A ConVarRef (18169e750 with a type) means the cvar lives in another DLL (engine2). A bool / int cvar's default is the setup's +0x37, a float's in xmm2.
- `sibscan.py`: nothing reads the item definition's sound replacements at +0xf8 + slot x 8.
- tier0 loads natively without engine init for its maths; on an FMA3 CPU the CRT takes its FMA path (flag 0x1803ab28c), Unicorn the SSE2 path.

### A live CS2 server

`cs2.exe -dedicated -insecure -usercon -maxplayers 64 -ip 127.0.0.1 +sv_lan 1 +rcon_password <pw> +map <map>`, driven
over RCON (replies come a frame later). No `-condebug` (without a console window it floods console.log in the game
folder); `sv_hibernate_when_empty 0` and `bot_join_after_player 0` for bots; bots need a nav mesh.
`ent_find` lists entity indices ([entity-index](entity-index.md)).

### The CS2 client's console (`-netconport <port>`)

VConsole2's binary protocol: packets of a 4-byte type, u16 version 0x00d4, u32 big-endian length (header included),
u16 handle. A command is `CMND` + text, NUL-terminated; output arrives as `PRNT` (text after 40 bytes). The backlog
replays on connect; one client at a time. `getpos` prints the eye, `setpos` sets the origin (eye - 64 standing).
Retail CS2 has no screenshot command (a window grab via PrintWindow comes back sRGB-encoded twice).
