# Traces of CS2's game binaries

What has been reverse-engineered from CS2's own game-side binaries (server.dll, client.dll, and the engine DLLs they
lean on: tier0, engine2, vphysics2, scenesystem, materialsystem2, panorama, particles, networksystem), with
addresses, field offsets, constants and sum orders, so the next port starts from it instead of from the decompiler.
Addresses are **server_20261105.dll** (sha256 70c66e85...; image base 0x180000000) unless a file says otherwise;
archive each build you read in `tools/re/binaries/` (S2C_BINARIES) under `<dll>_<yyyymmdd>.dll` and import it into
the Ghidra project (ReVa) under that name (`/server_20261105.dll`).

**Where these came from.** These notes were written alongside cs2web (a browser port of CS2's game modes) and were
copied here on 2026-11-21 from its `docs/trace/` (commit 55bb0752). Paths such as `sim/...`, `web/...`,
`rubikon/...` or `tools/capture/...` name that project's code (the ports and the native oracles that check them),
not files in this repo; the DLL helpers the notes use are in [tools/re/game/](../../tools/re/game/README.md).
New game-side findings go here, in the subsystem's file.

**Rule: every decompile / reverse session writes down what it found** (addresses, what each function does, offsets,
constants, sum orders, what's still unread) in the subsystem's file here, and any general helper in the table
below, in the same change as the port.

**Rule: every decompile / reverse session writes down what it found** (addresses, what each function does, offsets,
constants, sum orders, what's still unread) in the subsystem's file here, and any general helper in the table
below, in the same change as the port.

## The files

| File | What |
|---|---|
| [round-sounds.md](round-sounds.md) | The round's cues: the freeze time's beeps (server 180913f80: cs_round_start_beep by m_nLastFreezeEndBeep, cs_round_final_beep; the client's UI.CounterBeep / UI.CounterDoneBeep), RestartRound's round_announce_last_round_half / _final / _match_point (180957e50 at 18095aad4) and the HUD alerts' Music.Match.* stingers (client 180e84c60), a kill's UI.KillCard.1 (CCSPlayerPawn Event_KilledOther 180209da0, the enemy test 180ad2700, gg_killed_enemy), the local death's Player.FreezeCam / death cam music (client 180cee4d9), the HLTV replay's Deathcam.Review_* (client 180500ed0), the buy menu's ground pickup (180b0adf0), and which panorama files play the round report / deathmatch bonus / buymenu_purchase sounds |
| [gradient-fog.md](gradient-fog.md) | env_gradient_fog: client.dll's C_GradientFog (vtable 0x181adbf60, its fields and the unschema'd blend state), the cooked values 180275400 (the colour sRGB -> linear x strength, the heights zeroed without heightfog), spawn 180271810, FogStateChanged 18027fd10 (the twelve fields that restart the blend), the frame update 180272420 with its lerp 18027f630 (the fade time read live, Disable at once), server.dll's enabled flag |
| [hostage.md](hostage.md) | Hostage Rescue: CHostage (vtable 0x1817c1bc8; Spawn 1803629a0, the Think 180930450, Use 180931160, the touch 1809610f0, the pickup 180923710, the drop 18035bc40, the rescue 18035d350, OnTakeDamage 180361940 / _Alive 180361960, Event_Killed 18035c280), its fields and states, CCSPlayer_HostageServices 180a7af40 (the back prop), RestartRound's hostage selection (180958e9e..), func_hostage_rescue 180994400 -> the pawn's OnRescueZoneTouch 18023b020, the rescue win 180930260, the clock's HostagesNotRescued (180916fb0), the team / player money tables 180964f60 / 180952190 and the round's money list 1809124d0, PlayerMove's carrier speed (sv_cs_player_speed_has_hostage), the hint's CHostage branch (180ac74c0); client.dll's CCSGO_HudGameIcons 180e7d5d0 / 180e92590 |
| [pets.md](pets.md) | Chicken pets and the Weekly Care Package: items_game's pet items / pet_definitions / attributes; client.dll's pet clock (GetPetGrowthPercent 180d48150, GetPetLifetimeRemaining 180d481f0, GetPetFeedAmount 180d467d0, IsPetLowOnFood 180d4e340, TryAckPetEventAndCheckExpiration 180ffd4e0: 5 / 22 / 28 / 50 / 90 / 140 days, low food 9 d); rankup_redemption_store.ts's rules; server.dll's match pet (CChicken fields, SetOwner 18034fdd0, spawn 1803518c0, the manager 18034f710 / 18033b940 / 18034f4f0 / 18034e060, the spot lists 180354bf0 / 180354190, ChickenPathCost 1817be3f0, the graph controller 180a4f4e0 / 180a4c030, the activity machine, use / ping 180345830); client.dll's chicken graph controller 18084a1b0 / PlaySequence 18085c680, the overhead pet name 180ed0210, TransitionToCamera 180e65b40; second pass: the ping snap 180ab7ec0 / 180ac6b50 and placement 180adb580 (chicken type 0x1a, freeze-time use), ObjectCaps 18034f440 (0x81), the classic gate 18093df90, Move 1803507d0 + sweep 180353d40 (group 5, water), root motion 180342230, feelers 1803423e0, the jump 18034da90; client ApplyState 180d4f1b0, the vanity chicken frame 180d43380, Interact 180d4e890, the food check 180d520f0, the camera manager blend 180b833b0 / 180b82920 / 181744420, the inventory picture 18118d3d0 / 180dcaa00, the egg's nest 180d52620; third pass: the feeder 180d520f0 / 180d42f50 / 181748480, flinch's clear 18085d0e0, health 1 (180d0e5d0), TakeDamageOld 1803ed610, Event_Killed 180347350 (#Pet_Killed, roasted / tased / chicken_gone 180d51420), the party's pets (180cada50 / 180cae080 / 180e5e960), the eye (18014d780) |
| [spawns.md](spawns.md) | Team matches' spawn spots: the per-team lists (0x18090d240, 0x180925a50, the shuffle and priority sort 0x1809563e0 / 0x1809635f0), the next spot and its burst reset (0x1809297b0), EntSelectSpawnPoint (0x180207d80: deathmatch spawns only in deathmatch), the 32-try search (0x18023e340), IsSpawnPointValid (0x18093e710), sight / distance (0x18093e660, 0x18032d450, 0x18032d260), PutClientInServer's nudge, facing and drop (0x180216260, 0x18091f260), the spawn cvars' defaults |
| [armsrace.md](armsrace.md) | Arms Race (CS2's gun game): CCSGameModeRules_ArmsRace's vtable and fields (m_WeaponSequence, the leader / winner slots, the refresh set), the ladder's nine groups and their shuffle (0x180929ca0 / 0x1808ffa60), the kill's points (0x180921c30: m_iScore / 2 a level, knife +2 / -2, taser -1), the cues (0x180951c90), the equip (0x18092c0f0, the knife level's strip 0x180b04ac0), Think's winner (reason 8 / 9 / 10), gamemode_armsrace.cfg |
| [skins.md](skins.md) | Weapon paint kits: the composite request (1807fa510, the legacy path 1807fa62c, 512 at 1807fab0f), the composite system (mutators 1814d441e, the random roll 1814d4481, GENERATE_TEXTURE 1814d5191), csgo_customweapon's combos; what's open (vpkstuff has the rest) |
| [store.md](store.md) | The main menu's Store page from pak01's panorama files (UI sources, no DLL): mainmenu_store_fullscreen (tabs from the GC's banner list, the home page's sections), common/store_items (the categories), itemtile_store (the tile, its price row, what a click opens), the styles' sizes; our shelves' rules (the daily / weekly draw) |
| [cases.md](cases.md) | Weapon cases: items_game's crates, revolving / client loot lists, paint kits and icons; what is the Game Coordinator's (the rare tiers' contents, the odds, wear, StatTrak: stand-ins in the econ tables); popup_capability_decodable.vts's unlock (38-tile reel, display weights, slack, 6 s ease, tick timings, reveal sounds); the match end's drops (CS2's GC message at GoToIntermission, what the client keeps of the old drop, ours); the unbox's chat line (SendPlayerItemFound 180d119c0: the pickup method mask 0xe4003e, the token table 182252c00, the rarity's colour); NEW ITEM for unseen items (the Inventory's trigger, the nav alert, the carousel) |
| [matchmaking.md](matchmaking.md) | CS2's matchmaking as the client and server show it: the accept popup (layout, styles, script, sounds; the 21 s window: engine2 sv_mmqueue_reservation_extended_timeout, client 0x180fb2410 GetReadyTimeRemainingSeconds, 0x180cf8693 plays found / confirmed), the Reconnect panel, the cooldown alert and client 0x180f93b30 / 0x180f93d10 (penalty_reason -> reason string / type), who starts CT (server 0x180a75eb0: the reservation's first half on CT, xor switched sides), mm_dedicated_search_maxping (matchmaking.dll: 150, 25..350), the Premier tile's wins-needed / expired states; what is the GC's |
| [shadows.md](shadows.md) | CS2's cascaded sun shadow maps (scenesystem / client 20261015, csgo_environment's pixel shader): the Global Shadow Quality level tables (client 180df13a0 / 1820 / 0f20 / 1ca0), the csm_* / lb_csm_* / sc_shadow_* convars' defaults, the cascade setup (180496ef0: the split scheme, the texture matrix and its bias, the atlas rects), the fit (180494b40: the slice diameter, the texel snap, the caster extrusion, the exclude planes), the lookup and its constants (1801af7b0: the cross / distance fades, the receiver bias), the product with the baked shadow mask |
| [armsrace-hud.md](armsrace-hud.md) | Arms Race's HUD (client): the weapon list's ladder (#weapon-selection--armsrace-list: build 180ec6bc0 / item 180ea6120, the 0.25 s think 180eafc30 on m_iScore +0x954, the states 180ec3a80, --selected 180ecbfe0, the class tokens 0x1822452b8), the top bar's game_type 1 layout (180ec6730: GameModeGunGame, #TeamAll's 20 sorted by 180eabc80, #ArsenalProgress 180eba820 / 180ecc1f0: level, gglevel-%d, the weapon icon, no health), the immunity's shader inputs (180c67c40, 180c9d440), the game-type helpers (180769d30 / d50 / d90 / e60) |
| [winpanel.md](winpanel.md) | The round end panel (CCSGO_HudWinPanel, client 20261015): cs_win_panel_round -> the title by reason and local team (180eca700 / 180eb6af0), show / hide (180ec9a20), round_mvp (180ec8f10), music kit, funfact and honor icon rules; the server's MVP (server 20261015: 18090bae0 default, CPlantedC4DefusedMVP 1809f1550 / ExplodedMVP 1809f1910, SetMVP 180a76f50) and CCSFunFactMgr (18029aed0: the score and decay, StatBest / StatSum / Player / Generic evaluators, all 61 registered facts and each one's input and writer, CCSGameStats 0x181f4ea10 and its IncrementStat, the stat table 0x181dfb6b0); the MVP banner's ui/match_mvp scene and its camera blend; the round end's music and announcer (client 180ceaab0, PlayMusic 18076cd70, the music table 182212ae0, snd_roundend_volume / snd_mvp_volume) and round_end's nomusic / legacy (server 1809654b0) |
| [teammate-colors.md](teammate-colors.md) | CS2's competitive teammate colours: m_iCompTeammateColor (server +0x828, client +0x858), the assignment 180a9b940 (cl_color, the team latch 180a761a0, five tries), the colour mode 18093de70 / 180769bb0, the client's rule 1808a44a0, the colour table 180889bd0 and cl_teammate_color_1..5, GetPlayerColor 180faf660, the chat dot 180ea9f50, the voice name 180eb3e80, the team counter 180ecc1f0, the HUD class 180e92db0; the controller's rank and predicted rating fields copied from the GC list by 180a9e720 (the match stakes) |
| [team-intro.md](team-intro.md) | CS2's team intro: mp_team_intro_type / _time, the server's period (RestartRound 180957e50, ShouldPlayTeamIntro 180965160, variants 18097ded0, spots 18097d720 / 18097da90, schema 0x13c4..0x13d4), the intro prefabs' spots and cameras, CCSGO_TeamIntroMenu (180dfc510, the JS bindings 180e0db60, AddModel 180df2120), teamintromenu's script / layout / sounds, and C_CSGO_MapPreviewCameraPath's evaluation (180c94f90, 180c6c9c0, 180c6c730, 180c6d9c0, 180c6d7b0, 180c6c050, 180c67d00) |
| [warmup.md](warmup.md) | The warmup period: the think (server 0x180968600: the all-connected cut, the pause's 6 s rule, the end and its delay), its convars and cfg values, the gamerules fields, the HUD alert (client 0x180e8fea0: WAITING FOR PLAYERS / Warmup / Warmup Ending, Alert.WarmupTimeoutBeep); our load gate |
| [muzzle-flash.md](muzzle-flash.md) | A gun's muzzle flash and shell (client_20261015): CBasePlayerWeaponVData's muzzle fields (+0x2d0..+0x4e4, unset for every gun), the shoot clips' CNmParticleEvents (Create / Create_CFG, Self / Weapon, the systems' m_controlPointConfigurations), the silencer tag filter 18080a520, the pawn's and viewmodel's event handlers 1808ebfd0 / 1810d7270 |
| [tagging.md](tagging.md) | Tagging, the slowdown on being hit: the damage hook 180a961f0 (the weapon's / projectile's flinch modifiers, sv_predictable_damage_tag_ticks' delayed message, its handler 18097b670), the tag 180ab76a0 (m_flFlinchStack, mp_tagging_scale, the victim's weapon speed, the stamina, m_flVelocityModifier) with its float order, the stack's recovery in CCSGameRules::Think (180ac8880) |
| [taser-client.md](taser-client.md) | The Zeus on the client (client_20261015): the charge meter ($taser_charge 1808077c0, callback 1807e3df0, C_WeaponTaser vfn 0xad8 18082ea00, the chargemeter material's expressions), slot3's next-in-gear-slot (180c1e680 -> 180c19e30 -> CCSHudWeaponSelection::SelectSlot 1811a9cb0), the predicted fire and rope start (18082e180: weapon_hand_r + 7.61985 X + 2.32976 Z, the viewmodel's muzzle_flash in first person), cstaserrope's handler (180d1e3d0: CP0 / CP1 / CP3) and the body fx (180d1e300), the dry fire (server 180a1e400) |
| [equip-info.md](equip-info.md) | The top bar's equipment strip: when CS2 shows it (180ecd9a0: game_type 0, game_mode not casual, an observer, or a teammate during freeze time / warmup / after the round / while you're dead), its rows (money, SHRINK-MONEY, best weapon, grenades, armor, kit, C4), the .vcss |
| [weapon-selection.md](weapon-selection.md) | The weapon list's flash on a new weapon: the class tokens (180eb8970), an item added (180ea7660: weapon-selection-item--active), a count going up (180ec6b10), the animation-enable count (debug only), the .vcss blink |
| [weapon-select.md](weapon-select.md) | The weapon selection keys (client_20261015): slot6..slot11 by class (1811aa450 / 5d0 / 6b0 / 790 / 1811aa1e0 / 1811aad90, 180902f90 the by-name find), invnext / invprev (1811a68c0 -> 1811a7530, 1811a6980 -> 1811a77c0: the (gear slot, position) walk), vfn 0x258 180c0cc30 (the position at or after), the confirm vfn 0x268 1811a9bc0 (Player.DenyWeaponSelection), the gear slot positions, user_keys_default.vcfg |
| [death-panel.md](death-panel.md) | The death panel: CCSUsrMsg_SendLastKillerDamageToClient's fields and handler (180c8d8c0 / 180e8e3c0), when it shows and hides (180e8aaf0 / 180e877b0 / 180e8d660), the damage rows (180e8bbd0), the line (180e89ed0: the weapon names, own grenade / fire / C4 / self), the .vcss |
| [auto-exposure.md](auto-exposure.md) | CS2's auto exposure: client's per-frame source pick 0x180a71710 (env_tonemap_controller2 0x180272140, the volume 0x18029c500, the reset 0x180272390), the "Histogram" pass 0x181212030 and histogram_cs's bins / average, the readback 0x181208220; scenesystem's CTonemapSystem (vtable 0x1805f9cc8: its fields, params 0x18018d2a0, the adaptation 0x18018d440); the volume's exposure fields and server defaults |
| [post-layers.md](post-layers.md) | materialsystem2's CPostProcessingState (materialsystem2_20261023 vtable 0x18012ed48): the weighted .vpost layers, their groups and cross-fades, the per-category budget compose (180058500), the tone map / bloom / vignette / local contrast blends, the lookup merge (18005ce80, combine_colorcorrection_lut_cs) and post_process's lookup / vignette constants; who makes the layers in client_20261015 (C_PostProcessingVolume 18029c040 group 0, ClientModeCSNormal's overlays 180cf1d20 / 180d0d540); the overlay .vposts' contents |
| [death-cam.md](death-cam.md) | CS2's death camera (client_20261015): CalcView 180882530 -> 1808818a0 (the pelvis + m_vDeadViewHeight 14, death_chase_distance 76, the 180889e20 ease over spec_freeze_traveltime, m_flDeathCamTilt, the water lines on 0x18000, the 9 u solid sweep 1808a5910, m_qDeathEyeAngles, point_deathcam_bounds 180ce3c50 / 180ce2950), the view setup chain (CViewRender 180c1a710 -> 180b9c970), the server's m_flDeathTime / m_qDeathEyeAngles (180208400) and m_bKilledByHeadshot (180912130), ClientModeCSNormal::Update's overlay weights (180d0d540) and DeathFadeLayer (180d0ef50) |
| [rubikon-joint-break.md](rubikon-joint-break.md) | vphysics2 (0924): breaking a joint: the step's break pass (world +0xa28 / +0xa4c after 1801ffe80), the break 1802044c0 (callback +0xb8 / +0xc0 / +0xc8), CRnJoint::SetEnabled 1802058c0 (wake 180205f60 / 1801c0ff0, the shapes re-queued 1802d6c90, bit 0, vtable +0x58 18022aac0 / 180217360, the island update 1801e4000); the break limits +0xac / +0xb0 from the creators' desc +0x64 / +0x68 (18005d370), 0 for a model's joints (180047600, VPhysXJoint_t has none), CPhysicsJoint slots 0x1a0 / 0x1b0, unused by client_20261015's ragdolls |
| [rubikon-colour-joints.md](rubikon-colour-joints.md) | vphysics2 (0924): a graph-coloured island's joints: the plan (RnSolver_BuildColoured 180338710, its layout), the joint jobs 180337c00 (buckets of more than 8 in parallel chunks of 8, the rest and the overflow whole, bucket order), the chain 1803109c0 (joints, type-1, contacts in every pass), the chunk workers 18030eb50 / 18030fb00 / 18030f500 / 18030f250 against the whole ones 18030f0b0 / 180312650 / 18030f860 / 1803120f0 |
| [ragdoll.md](ragdoll.md) | A player's death ragdoll: the pawn's ragdoll fields (server 18024a860 / 1802064f0 from player_death 18091da70: bone, force, weapon, headshot, origin), the damage forces (CalculateBulletDamageForce 180fc2430, RadiusDamage's direction, the shockwave's), the client's creation (180c97a60 -> 18095b0b0 -> 18095acd0: the physics world's CreateRagdoll at the bone pose, ragdoll_gravity_scale 1, ragdoll_friction_scale 0.6, the pawn's velocity), the weapon push table 180c63540 and its application 18095aac0, cl_ragdoll_limit 20; the aggregate build (source2-compiler's port) |
| [ragdoll-settle.md](ragdoll-settle.md) | Ragdolls falling asleep: CS2's client death ragdolls have no settle rule (vphysics2's island sleep only), the world's 8 / 2 iterations (CRnWorld ctors 1801e7df0 / 1801f5fb0; CVPhys2World slots 24-26), VPhysXBodyPart_t's fields; why a pile stays awake; the server's CRagdollProp settle think (180e95f00 / 180e6f920, ragdoll_prop_sleepaftertime 4, sleepdisabletime 1.5), CPhysicsBody slots 125-129 (Sleep 1801be010) |
| [blood.md](blood.md) | A player's blood: m_bShouldBleed / m_bShouldSpark (the hit group step 180a89430), the damage services' post 180a88a50 (csblood's CEffectData, the helmet's sparks, the blood level, TraceBleed 1803eee10 and UTIL_BloodDecalTrace 180cbb810's Blood / Bloodlvl2..6), the client's fx_cs_blood.cpp 180d226c0 (high / med / low / friendly by damage_impact_heavy 40 / _medium 20, the spray's frame, the local player's variants) |
| [damage-prediction.md](damage-prediction.md) | Damage prediction (cl_predict_body_shot_fx / head / kill_ragdolls, sv_damage_prediction_allowed): CSGOUserCmdPB fields 11-13 (+0x49..+0x4b) written by client 180d04950 behind the gate 1808845a0 (m_bPredictable, latency <= min(0.07, sv_maxunlag x 0.95), m_bFireBulletsSeedSynchronized = sv_usercmd_custom_random_seed off: server 180a9e270 / 180c7f1e0), the client FireBullet's predicted TakeDamage (180887d60), the victim's predicted damage list and GetHealth (1808de930, 180c671a0), the predicted effects / feedback (180887960, 18089d3b0, 1808a0150), the kill ragdoll and its snap back (180c8f940, 180c8c070, 1808a1250), the server's exclusions (180a77f60, 180a30179) |
| [kill-cards.md](kill-cards.md) | The kill cards above the health / ammo panel: the round's kills and kill-type queue (180912130, 180b0b6e0, 180a6e260 push, 180931910 types, cleared at the respawn), the client's classes (180e92db0: HUD--NumKills, HUD--Kill{i}--type, animate / HUD--on-kill), the .vcss fan |
| [source1-bake.md](source1-bake.md) | `lasers-bake --source1`: a CS:GO BSP hand-baked into the CS2 map folder; each Source 1 thing and the CS2 data it becomes (brush contents -> world_physics collision attributes, read off the CS2 maps' own sets and source2-compiler's MaterialCollision table; brushes / displacements / static props through the RnHullCreate / RnMeshCreate ports; lightmaps as the irradiance lightmap; light_environment's CS2 keys); ze_crazykart_v4's unhandled classes |
| [death-notice.md](death-notice.md) | player_death: the server's fields (18091cf40: the weapon name, _off, penetrated count, noscope, thrusmoke, attackerblind, attackerinair), the death notice (18091da70), the damage assister (1809284a0, cs_AssistDamageThreshold 25, bullets first) and flash assister (180913af0), the damage records (180b00ba0, CDamageRecord), thrusmoke (1809165e0); the client's notice (180e885f0): classes, icons, the assist |
| [ping.md](ping.md) | The player ping: player_ping (180ab7ec0: the double ping, the 0.3 s spam filter, 5 tokens at player_ping_token_cooldown 20 s, the 2 x 16384 x sqrt 3 trace, smoke, the 36-unit entity snap), placing it (180adb580: m_iType, m_bUrgent, 6 s, the event), the client's icon (team colour bytes on CP1) and sound (UI.PlayerPing / Urgent), teammates only |
| [box-hull.md](box-hull.md) | A cooked axis-aligned box hull (RnHull_t) as the bake writes it, read from de_dust2's physics.bin: the vertex and plane order, the half-edge tables, the derived fields' rules (for the game's own box models: world/box-physics.js) |
| [transmit.md](transmit.md) | CSource2GameEntities::CheckTransmit (180dd7150): the per-client pass 180de3590, the per-entity 180de3df0, the transmit-state bits (+0x1b8: 8 always, 4 PVS check, 0x10 never), the cvars; IsInPVS 18018ed80 (clusters, sv_pvs_max_distance), the client record 180b48900 (its eye origin), CCSPlayerPawn ShouldTransmit 18024b840 / 180d11e00 and SetTransmit 180d10cd0; WorldSpaceSurroundingBounds 180d1b7c0 and the m_nSurroundType switch 180cebd90; client_20261015's rules for what the HUD shows of others: scoreboard money 180fb0940 (team or spectator), the top bar's health 180eba820 / 180ce2420 / 1808d9290 IsOtherEnemy |
| [spotting.md](spotting.md) | CCSEntitySpotting (every 0.5 s): m_bSpotted / m_bSpottedByMask, the observer cone (radarvismethod, the FOV, powf), the line of sight; the client radar's per-player rule (180dde830); the transmit cvars (sv_shared_team_pvs) |
| [round-restart.md](round-restart.md) | CleanUpMap (180917fd0): the preserve list (181e04220, 86 class names), the world-group test that keeps a skybox map's entities, the "cs_respawn" pass over the spawn groups |
| [movers.md](movers.md) | CBaseToggle's linear / angular moves, PerformPush, CBaseDoor, CRotDoor, CFuncMoveLinear, CFuncRotating |
| [trains.md](trains.md) | CFuncTrackTrain (Next, the velocity and orientation updates, the inputs), CPathTrack's LookAhead / GetOrientation |
| [momentary.md](momentary.md) | CMomentaryRotButton (Use, its thinks, SetPosition), ObjectCaps' use bits, PlayerUse's continuous use |
| [push.md](push.md) | The pusher: CPhysicsPushedEntities, blocked movers |
| [tracer-sound.md](tracer-sound.md) | A bullet passing by you: client FX_TracerSound 180c2d0a0 (the crack and tail, cl_tracer_whiz_distance / _infront_distance, the whiz timer), its callers and their tracer types (supersonic: SMG / rifle / sniper without a silencer type) |
| [switchhands.md](switchhands.md) | switchhands (H): the client's wanted hand, left_hand_desired, Weapon_Switch's eUserInitiatedSwitchHands, SwitchHandedness, the arms' dip (client_20261105.dll too) |
| [friends.md](friends.md) | The main menu's friends list sidebar (mainmenu.ts Expand / MinimizeSidebar, friendslist / friendtile / context_menu_playercard / popup_add_friend sources and styles), client.dll's friend codes (encode 180f88150, decode 180f87f90, parse 180f88570, GetFriendCode 18106f180, GetXuidFromFriendCode 180fb9280: the Unicorn oracle), TeammatesAPI.GetCoPlayerTime 18106d430 (4500 s "Just Now"), the status strings, Looking to Play's sources (not built). Tools it added: tools/re/game/impat.py (which import an IAT slot holds), friendcode_oracle.py |
| [loading-screen.md](loading-screen.md) | CS2's loading screen: its layout, style and script (PopulateLoadingScreen's arguments, the slide show), the strings; what ours stands in |
| [home-menu.md](home-menu.md) | The main menu's UI: the left column's tiles from their layouts (mission, Armory, mini store + item tile, Rush, the carousel nav), the play menu's map tiles / section headers / settings radios / GO, the rating tile (tier colours, GetClampedRating, SplitRating) from pak01's .vcss / .vts (UI sources, no DLL) |
| [menu-anim.md](menu-anim.md) | The main menu: de_dust2_vanity's preview / UI-slot entities, CS2's uimodel / uimodel_walkup / uimodel_idles graphs (states, parameters, selector weights), the haze cards' csgo_effects parameters (resource data, no DLL) |
| [holster.md](holster.md) | Holster (vfn 0xa20 -> 0xd40): the base (the reload, the R8 hammer, an empty grenade removed, the holster activity), the gun's (silencer switch, zoom), the grenade's (pin, throw), the C4's, the taser's |
| [scene-node.md](scene-node.md) | CGameSceneNode: the hierarchy, ConcatTransforms, QuaternionAngles, SetAbs* / SetLocal*, SetParent; template placement (the spawn matrix); Kill / KillHierarchy / UpdateOnRemove's children |
| [spawngroups.md](spawngroups.md) | info_spawngroup_load_unload (CInfoSpawnGroupLoadUnload): its fields, the four inputs' virtuals, the load request, the loading and unloading thinks and when each output fires; what the engine's half leaves untraced |
| [io-queue.md](io-queue.md), [io-targets.md](io-targets.md), [inputs.md](inputs.md) | The entity I/O event queue; target searches; the input dispatch and each class's input table |
| [movement.md](movement.md) | Player movement |
| [inferno-spread.md](inferno-spread.md) | the server's CInferno spread (not ported yet): CreateFire 180345dc0 (the fire record, its timers: every flame dies at the inferno's start + the lifetime), the think 180352350 (the hashed SetSeed, the round robin under inferno_max_trace_per_tick, the 4 tries' directions, the velocity push into the ground plane, the 55..75 u step, the ground and line traces, inferno_forward_reduction_factor), the cvars by address |
| [inferno-client.md](inferno-client.md) | client C_Inferno's ground fire (ported): ClientThink, SynchronizeDrawables, the particle (seed, CP0 / CP3), the edge masks, the wall traces and hull planes (Inferno_concav_plane_threshold), the CP1 / 9 / 10 / 11 / 12 snapshots, the remnant; the server's networked fire fields (CreateFire); the particle classes it needed |
| [spritecard.md](spritecard.md) | particles.dll / spritecard PS: the layer channel mixes (layers 1-3 against the earlier layers), the scene-object layer mask (bloom-only 0x80), the motion-vector scale (PC c3.xy from the motion texture's max distance), how to dump the PS combos; the 1D lookup layer's UV; the trail combo (ropes and trails: the width-projective U, F_ADDRESS_V_CLAMP from m_bClampV at CBaseTrailRenderer +0x3350 / C_OP_RenderRopes +0x34ec, the motion warp and its weights); the vertex writer's sheet time per animation type (MANUAL_FRAMES: attribute 38 as a sequence position) |
| [music-volume.md](music-volume.md) | The csgo_music stack's volume chain (snd_musicvolume x the event's volume convar by snd_music_mode, 0.16 fallback, x snd_gain), client.dll's snd_music_mode (180d0c420, game_type / game_mode), soundsystem.dll's `volume` / snd_musicvolume / snd_gain |
| [mouse.md](mouse.md) | client.dll: the mouse to the view angles (sensitivity, sensitivity_y_scale, m_yaw / m_pitch, the zoom's scale, mouse_inverty; AngleNormalize, the cl_pitchup / down clamp), the per-frame input entry that holds the view angles |
| [net-timeout.md](net-timeout.md) | sv_timeout / cl_timeout: their defaults (engine2's registrations), NETWORK_DISCONNECT_TIMEDOUT's token and text; the checks unread |
| [usercmd.md](usercmd.md) | The usercmd's timing (client.dll + server.dll): the client's input history and attack1_start_history_index, RunCommand and the tickbase, CPlayerCommandQueue's tickbase, the spread seed's tick |
| [frame.md](frame.md) | The server frame's order: ServerPreEntityThink, the controllers' usercmds in slot order, the thinks, the I/O queue, ServerPostEntityThink (where CS2Fixes' RunThinks sit) |
| [shots.md](shots.md), [fire-gate.md](fire-gate.md), [spread.md](spread.md), [aim-punch.md](aim-punch.md), [knockback.md](knockback.md), [use.md](use.md), [grenades.md](grenades.md), [flashbang.md](flashbang.md), [env-explosion.md](env-explosion.md) | Combat: the bullet, damage (TakeDamageOld and its flags), lag compensation, the knife; a gun's fire gate and Deploy; spread; the aim punch; ZR's knockback; +use; grenades; the flashbang's blindness, ring, screen overlay and flashed animation (flashed_amount on the anim graphs); env_explosion's effect (CMsgTEExplosion, C_BaseExplosionEffect) |
| [reload.md](reload.md) | A gun's reload: the R key's branch, Reload's clocks, the timing graph's WPN_RELOAD_ADD_AMMO / WPN_ACTION_COMPLETE, the empty and silent clips, the held-R silent reload (180a27170, 1809f5880) |
| [knife.md](knife.md) | The knife swing's hit sounds (flesh from the victim, HitWall from the knife) and its gate: CCSWeaponBase's ItemPostFrame, the swing's 1809f9910 clocks (0.4 / 1.0 s), m_bFirstAttack, the Deploy |
| [pickups.md](pickups.md), [drops.md](drops.md), [touch.md](touch.md) | Weapon pickups, drops, touches |
| [radio.md](radio.md) | The radio: ClientCommand's radio commands (1802006b0, 180219840 and its three switches), Radio 180239eb0 (alive, recipients 180202390 through CanPlayerHearPlayer type 1, Game_radio / _location, the voice through the response rules: bot_chatter_use_rr), the throttle 180202570 (sv_radio_throttle_window 10), playerchatwheel / playerradio / ignorerad, the grenade throw's line (1809d4a50); the client's line (1811ac670: the team prefix, "auto"); the radio menus (radiopanel.txt) and the chat wheel's default phrases (cl_radial_radio_tab_*); places: m_szLastPlaceName (pawn + 0xe78), its update 180252d20 / lookup 18020c1b0 over env_cs_place; a match's voice cvars from the cfgs |
| [buy.md](buy.md) | Buying: CanPlayerBuy (180aba860), IsBuyTimeElapsed and m_fRoundStartTime (the buy time from the freeze's end), CBuyZone's touches and m_bInBuyZone, the buy command's order (180a7cf90: CanAcquire, kevlar / assault suit, GetItemPrice's helmet-only price), the client's buymenu checks and its hint lines (180ca3f90, 180dabe70, ShowHudHintTextLowPriority), the buy menu's layout and CS2's default loadout (items_game.txt) |
| [hurt.md](hurt.md) | Map damage: CTriggerHurt (the flag test, HurtThink, HurtAllTouchers, HurtEntity's one output, EndTouch), a map damage's hit group and armor, Blocked's DMG_CRUSH, CPointHurt, TakeHealth; filter_multi's ten slots, filter_proximity, filter_activator_attribute_int; AddAttribute and CS2Fixes' Steam ID attribute, FollowEntity, func_movelinear TeleportToTarget |
| [player-sounds.md](player-sounds.md) | Who hears which sound event: a hit's Victim / AttackerFeedback / Onlooker events (180a95310), a death's (180ac13d0), a pickup's (BumpWeapon's tail), the recipient filters; the physics impact sounds (the collision dispatcher, VPhysicsCollision, the queue and its 0.05 s flush) and vphysics2's collision events behind them (1801fe920, 180059170, 180058a90; the server's speed 180593af0) |
| [anim-graph.md](anim-graph.md), [aim-ik.md](aim-ik.md), [fp-legs.md](fp-legs.md), [tilt-twist.md](tilt-twist.md) | Animation; tilt-twist.md: animationsystem.dll's CTiltTwistConstraint (the solve 1804b7ca0, its angle 1804b8c60, AngleQuaternion 180490910, the fields), the agents' twist bones |
| [score.md](score.md) | server_20261105: the kill's score: the contributionscore_* cvars (handles, defaults), Event_KilledOther 180209da0's objective / team kill flags, 18095f4b0 / 18095f620, the suicide in 180952250, the hostage and planted C4 proximity tests (1802225f0 / 180222530); deathmatch's 180922080 (base, weapon price tiers, the bonus weapon, the Zeus streak, the healthshot, the assist) and 18090d0d0's award lines; three behaviours checked to be CS2's |
| [scoreboard.md](scoreboard.md) | panorama (pak01 2026-11-20, no client.dll): CSGOScoreboard per game mode: _LoadScoreboardTemplate / _GetPlayerRowForGameMode / _GetSortOrderForMode, the sort orders, stat updates and the pulse, the status images, the timeline (_ResetTimeline, _UpdateRound, the clinch, the casualties, the half scores, the loss bonus), the end of match rules, what is client.dll's |
| [teamid.md](teamid.md) | client.dll: the decorated player name (`{g:player_name}`: the clan tag in CS2's brackets, the name, the puppeteer; its modifier flags and the controller's provider), the overhead team id's entries, panels, head-bone anchor, 0.7 scale and health line. Tools it added: tools/re/game/vtall.py (a class's vtables at every sub-object offset), strtoken.py (CUtlStringToken's hash: find a name for a token), vpkgrep.py (search the game's pak01: localization, panorama) |
| [bot-takeover.md](bot-takeover.md) | CS2's bot takeover: CCSObserver_UseServices' +use (180a4c2d0), CanControlBot (180a71120), TakeControlOfBot (180a9cbe0), the pawn swap (180a9c710), ReleaseControlOfBot (180a991e0) and what calls it (the death, RestartRound, a team change, a disconnect), m_bCanControlObservedBot (180236ce0), the controller fields, who is credited (the pawn's +0xe14), the client's view, takeover panel and legend hint |
| [c4-shockwave.md](c4-shockwave.md) | The bomb's blast, ported: CS2's baked shockwave (baked_bomb_damage.vdata's format, the table load 180a508c0, tier0's CVertexKDTree build / nearest, the lookup's RemapVal, the ducked / facing Bias, the 3000 u/s wave and its hit), the KdOracle check, the stand-ins, the RadiusDamage fallback |
| [settings.md](settings.md) | The Settings menu's sources (pak01's settings layouts / styles / strings, `lasers-bake --settings-ref`, tools/settings-layout.mjs), CS2's styles the page ports; client.dll's crosshair codes (apply_crosshair_code 180dc2c40, the base-57 decoders 180bd3c70 / 180daf640, the 32-byte record and its clamps, the classic code's conversion, the float struct 180daf490, the rescale 180dbca70, the convar writes 180dbafb0, tier0's V_roundf), the Unicorn oracle; the crosshair's drawing (180da0610's spread / dynamic gap / alpha, every style's shapes, csgo_crosshair's pixel shader); convar registrations' two forms and the crosshair family's defaults (tools/re/game/cvardefs.py) |
| [overtime.md](overtime.md) | The match's end and overtime: the mp_overtime_* / mp_halftime / mp_maxrounds / mp_match_can_clinch registrations and defaults, CheckWinLimit's rounds half (1809101e0: the clinch takes mp_halftime, total = k * ot + maxrounds, the next overtime with no tie test), IsLastRoundBeforeHalftime (18093d850), RestartRound's halftime branch (no swap at an overtime's start), AreTeamsPlayingSwitchedSides (18090ee00), GetStartMoney (18092a5e0) |
| [match-pause.md](match-pause.md) | The halftime (mp_halftime_duration / pausetimer), tactical and technical timeouts (StartTerroristTimeOut 180964c10, the freeze hold in 180913f80, the gamerules' timeout fields), the vote issues (CSurrender / CStartTimeOutIssue vtables, CanTeamCallVote and m_bAbandonAllowsSurrender, GetNumberOfVotesRequired 1802789f0, the surrender's TerminateRound reasons 17 / 18), the sv_vote_* timers, the vote menu (context_menu_vote.ts) |
| [vote-controller.md](vote-controller.md) | CS2's CVoteController: callvote 1802905b0, CreateVote 1802690c0, TryCastVote 18028db40, the think 18028f970 (the pass test, sv_vote_command_delay, the 5 s reset), the reset 180286890, its fields (+0x4a8..+0x648), vote_create_failed_t, the sv_vote_* cvars by handle, CBaseIssue's slots, which issues a server registers (18091ba50), Kick / ChangeLevel / NextLevel / RestartGame / Scramble / Swap, StartTimeOut / Surrender's reason maps, client.dll's reason table 0x181cdfa40, context_menu_vote.vjs's menu |
| [pulse.md](pulse.md) | Pulse graphs on the official maps (point_pulse, vpulse_c2): where each map's graph lives, the compiled format and instructions, the cells (GetIsWingman 1801dbe50 -> IsWingman 1809108d0, EntFire FireAtName 1808950a0 / Run 180894d20, RandomInt::Eval 1815ace70, CycleRandom 1815c9c00, Wait 1815ca640), what GameModeCheck / WorkplaceInjury / the lightning do |
| [spawns.md](spawns.md) | Team spawn points: CSpawnPoint m_iPriority / m_bEnabled (+0x4a8 / +0x4ac), GenerateSpawnPointLists 180925a50, the enabled lists' shuffle and priority sort 1809563e0, GetNextSpawnPoint 1809297b0 (the 0.03 s wave reset), RestartRound's spawn configuration 1809621f0 (unported) |
| [prop-doors.md](prop-doors.md) | prop_door_rotating = CPropDoorRotatingBreakable (1819dd938 <- CPropDoorRotating 1819dce10 <- CBasePropDoor 181965e80): fields, keyvalue datamaps (180cd93b0, 180f15360, 180f018b0), Spawn 180f3bd00 / 180d13220, Activate's slave list 180ce0310, PlayerUse 180d16590, DoorOpen / DoorClose, GetOpenAngles 180f14ac0, the path sweep 180f14e50, the sweep bounds 180f148d0, the entity blocker (group 17), MoveTo / MoveDone, StartBlocked / EndBlocked 180d151f0 / 180cf1bf0, the inputs, the sounds 180ce8380, the breakable damage 180f30060 / 180bbe860 |
| [crazykart-physics.md](crazykart-physics.md) | **CS:GO legacy** (not CS2: ze_crazykart's kart, docs/CRAZYKART.md): the kart's .phy (hull, mass, inertia, mass centre), phys_thruster's SetupForces 0x102eea80 / CalculateVelocityOffset vphysics 0x1001ca30 / the controller 0x1001a4f0, vphysics' step, damping 0x10076f20, gravity, drag, limits, friction, CKeepUpright 0x102f0500 / 0x102f06d0, the prop's spawnflags (0x8 = motion off), VScript TraceLine 0x103e52a0, CGameUI::Think, GetAngles' wrap (VPhysicsUpdate 0x10207cd0); the oracle (rubikon/tests/KartOracle: vphysics.dll's interfaces and vtables, the server's environment setup 0x102f5f60, a raw-stack scan of each callback's IVP call chain) and IVP's PSI 0x10084fb0 (its stages, the simulation unit 0x10072540, the core's next-PSI step 0x100970f0, the hull managers 0x10097db0); sleeping and waking, the unit lists and their walk, several bodies, Sleep / EnableMotion / SetVelocity / SetPosition, the limit hooks, the damping's expf (12) |
| [ivp-mindist.md](ivp-mindist.md) | **CS:GO legacy** IVP's collision detection for ze_crazykart's kart (sim/src/ivp, mindist_check): compact ledges (.phy, BBoxToCollide 0x1000a860), the cache 0x1006cd90, the minimize solver (recalc_mindist 0x100982d0 and its cases), the mindist's layout, its creation (recheck_ov_element 0x10094de0, init_mindist 0x10094150, insert_and_recalc_exact_mindist 0x10094be0), the hull managers (0x100974e3, 0x100975f0, 0x10097db0, the hull event 0x100957c0, reset 0x10093bb0), the OO watcher 0x100b77f0, the range manager 0x100a1150 / 0x100a1240, update_exact_mindist_events 0x10095310, the KK / PF / PP / PK event solvers (0x100a2d90 / 0x100a2160 / 0x100a35c0 / 0x100a3f40, IVP_3D_Solver 0x100b72a0 / 0x100b7510 / 0x100b7130), the time events (0x10085440, 0x10095dd0) and the hand-off to do_impact (slot 8, 0x1008b020); ledge trees (the walk 0x100789b0 / 0x10078bc0, create_exact_mindists 0x10094300's pair loop with the diff hash 0x10096850 / 0x10096710, the watcher's vector removal 0x1009b470, the mindist's ledges 0x10094110) and calc_unscaled_KK_vals' parallel fallback 0x10079be4 |
| [ivp-shadow.md](ivp-shadow.md) | **CS:GO legacy** vphysics.dll's shadow controller and server.dll's movers: which brushes are shadows (CreateVPhysics slot 154, VPhysicsInitShadow 0x102083a0 / VPhysicsInitStatic 0x10207ff0, PhysModelCreate 0x1031a3d0, PhysModelParseSolid 0x1031a270 with g_SolidSetup's defaults), when they're updated (PhysicsPusher, FinishPush 0x10303370, the frame's pusher list 0x10303170, UpdatePhysicsShadowToCurrentPosition slot 163), SetShadow 0x1001dac0 / UpdateShadow 0x1001db50, CShadowController (ctor 0x10024990, attach 0x10024a60, Update 0x10024ff0, do_simulation 0x10024f20, ComputeShadowControllerIVP 0x10024130 with 0x10020fa0 / 0x10023fb0), UseShadowMaterial's revival (SetMaterialIndex 0x1001dca0, 0x10076950), SetMass 0x1001c100, CollideGetAABB of a ledge tree 0x10032e60; shadow_check |
| [ivp-impact.md](ivp-impact.md) | **CS:GO legacy** vphysics.dll's impact system and the kart on the ground end to end: do_impact 0x1008b020, 0x1008ac60, the core's sync 0x100779f0, the rescue 0x1008ba70, the friction system from a mindist 0x10088450 (0x1008df50 / 0x1008def0 / 0x100831f0 / 0x10083110, pairs 0x100870c0, cores and controllers 0x100871f0 / 0x10071d40), the impact system 0x1008b380 / 0x1008b4c0 / 0x10081fe0 / 0x1008b2c0 / rounds 0x1008b590 / end 0x1008bb40 / 0x100730d0, the stage-5 rot step 0x10096fe9, env+0x114's stages, a core leaving a system 0x10087270 / 0x10071dc0, the unit's rebuild 0x10071800 / 0x100713b0, vphysics' friction listener 0x10011eb0, the freeze's collision side 0x10077820 / 0x100775f0, 0x10082ce0; ivp_check's ground mode |
| [ivp-contacts.md](ivp-contacts.md) | **CS:GO legacy** vphysics.dll's contacts: the friction system (ctor 0x10086de0, its controllers 0x10082e70 / 0x10082ff0 / 0x10082f60 at priorities 2000 / 600 / 0), the contact point (0x1007ec20 from a mindist, its geometry 0x1008d230 with 0x1008c2e0 / 0x1008c490 / 0x1008bd50 / 0x1008c850, its spring mass 0x10082a60), the static friction 0x1007fb40 over IVP_Solver_Core_Reaction 0x1009c010 / 0x1009b4e0 / 0x1009c0c0, the pairs' springs and energy (0x10080720, 0x10080840, 0x100820b0, 0x100826d0, 0x100821a0), the normal pressures' great-matrix solve 0x100a0b30 and the impacts 0x1008b0e0 / 0x10089a50 (call level); IVP_Mindist_Settings 0x1010d23c / 0x1010d240; the oracle's breakpoint probes (Probes.cs) and their `.raw` lines |
| [ivp-touch.md](ivp-touch.md) | **CS:GO legacy** vphysics.dll with two dynamic bodies touching: friction systems as a list (a static core's infos per system), their merge 0x10081280 (0x10086fb0) and split 0x10082f60 -> 0x100815a0 / 0x100816a0, simulation units of several cores (0x10071d40 / 0x10071dc0 / 0x100713b0 / 0x100718e0 / 0x10071aa0, the unit's PSI 0x10072540, sleep 0x100722d0, revive 0x10071ef0, split test 0x10071710 with the controllers' slot 2 0x10007ca0 / 0x10082e60, split 0x100715c0), vphysics' pair-time listener (0x100127e0 / 0x100128c0, the cleanup 0x10012630), the rescue push 0x100980a0 (0x10083e40, 0x10012a10 / 0x10012cb0, 0x100839a0, 0x10083760, async push 0x10074e10, the core matrix 0x10076b50), the cache ring 0x1006ccb0 / 0x10001b50 |
| [ivp-collide-off.md](ivp-collide-off.md) | **CS:GO legacy** vphysics.dll: an object's collisions off and on (EnableCollisions slot 12 0x1001b710: the friction snapshot 0x1001c050 / 0x100184c0 with Mark 0x10018610 and DeleteAllMarkedContacts 0x10018570 -> 0x10073be0, the OV element's dtor 0x1009a370, 0x10073ba0, 0x10095180 / 0x1009a2e0), SetPosition 0x1001d4e0 with isTeleport, the beam 0x10074b20 -> 0x10097750 (time code, hull managers, a frozen object's cache let go, 0x10073a50), EnableMotion's collision part 0x10072af0 / 0x10072c90, recheck_ov_element's pair filter (both cores static or pinned), several cores revived in one stage 1 |
| [ivp-virtualmesh.md](ivp-virtualmesh.md) | **CS:GO legacy** engine.dll / vphysics.dll / server.dll: the displacements' physics. The engine's terrain collides (CollisionBSPData_LoadDispInfo 0x101e6650 and its CCoreDispInfo calls, CDispCollTree's layout, CM_CreateDispPhysCollide 0x101e7760 and the PHYSDISP lump, CVirtualTerrain's three callbacks, AABBTree_GetTrisInSphere 0x101f3360), vphysics' virtual mesh (CreateVirtualMesh 0x1002b980, the frame 0x1002acf0, a triangle's ledge 0x10002fc0, the packed hull's unpack 0x10002cc0, the surface manager 0x100e37a8: get_all_ledges_within_radius 0x1002af50, the point-triangle distance 0x1007a3e0), the server's vdisp_%04d objects 0x1031aa20; the oracle loading engine.dll (Disp.cs), the port (sim/src/ivp/vmesh.rs) and its checks |
| [csgo-vscript.md](csgo-vscript.md) | **CS:GO legacy** server.dll's embedded Squirrel prelude: EntFire (caller = self, a null activator = self, a false value = ""), EntFireByHandle; found by a byte search, no disassembly (csgo/vscript/ent-fire.js) |
| [csgo-effects.md](csgo-effects.md) | **CS:GO legacy** client.dll / server.dll / engine.dll: env_steam (C_SteamJet's Start / Update / SimulateParticles / light ramp / RenderParticles, the engine's GetLightForPoint), env_spritetrail (C_SpriteTrail's UpdateTrail / DrawModel, CBeamSegDraw's NextSeg / SpecifySeg), func_precipitation (CClient_Precipitation's systems per type, Simulate / UpdateParticlePrecip's four rays, the dispatches' control points), RayTracingEnvironment's Trace4Rays, the particle library's C_INIT_RtEnvCull and C_INIT_LifespanFromVelocity; what's unread |
| [csgo-triggers.md](csgo-triggers.md) | **CS:GO legacy** server.dll: CBaseTrigger's vtable (0x108da2f0), datamap offsets (m_OnStartTouch +0x414 ... m_OnNotTouching +0x48c, m_bDisabled +0x408, m_hTouchingEntities +0x4a4), Disable 0x103b5ab0 (FSOLID_TRIGGER off, PhysicsTouchTriggers), EndTouch 0x103b6170 (OnEndTouch fires with no m_bDisabled test), PassesTriggerFilters 0x103b5dd0, OnEndTouchAll 0x103b6030. Not read: a killed trigger, the untouch frame, Enable / StartTouch |
| [ivp-physbox.md](ivp-physbox.md) | **CS:GO legacy** server.dll / vphysics.dll: func_physbox (CPhysBox::Spawn 0x1031ca00 and CreateVPhysics 0x1031ce60: the debris group, PhysModelParseSolid, PhysSolidOverride 0x102f7de0, the Wake / EnableMotion flags), vphysics ParseSolid 0x100338c0's keys; ze_crazykart's items on IVP |
| [ivp-pileup.md](ivp-pileup.md) | **CS:GO legacy** vphysics.dll / server.dll with a core past the impacts per PSI: 0x10088f10's anomaly slot 3 (0x10012b00), the frozen branch 0x1008a0aa (speeds into the pending changes, both cores pushed), who reads flags 0xc0 (the impact system's round); the server's ShouldFreezeObject 0x102f7090 with FindMaxContact 0x102f6f80 and the crush damage; ShouldCollide's root move parent and SOLID_NONE (CBaseButton::Spawn 0x10226b10 spawnflag 0x4000); vphysics' friction snapshot (0x100184c0, vtable 0x100e1d94) |
| [spec-xray.md](spec-xray.md) | The dead's xray (client_20261015): the grenade trail 1807c81c0 (its fields, the 0.05 s point clock, CP 3 / 16, the 1024-point snapshot, who sees it, sv_grenade_trajectory_time_spectator: Competitive's 4), spectator_utility_trail.vpcf; the pawn glow 180c9a3a0 and its xray rule 180c7d380 (spec_show_xray, mp_forcecamera's enemy cut, team / deathmatch colours, the spec_glow_* noise curve over m_flEmitSoundTime), 1808d9120 (enemies), 180ce2420 (a caster); server EmitSoundByHandle 180f698d0 (public.display_broadcast token 0x442583); particles.dll 2026-11-12 0x18006fac5 PF_TYPE_PARTICLE_NUMBER; CS2's glow pass 1811faa40 (solid colour, downsample, blur, stencil, bicubic composite; its materials and shaders, the glow colour path 180ba92f0 / 180b78090 / 180b56b20) |
| [video-textures.md](video-textures.md) | Texture detail's convar (the presets' builders 0x180deae90 / deb340 / dea9e0 / deb7f0: r_texture_stream_max_resolution 1024 / 2048 / 8192), worldrenderer's r_lightmap_size (default 65536, no preset writes it: full lightmaps on every preset), r_lightmap_size_directional_irradiance (-1), r_lightmap_set |
| [world-vis.md](world-vis.md) | A CS2 world node's visibility data (vwnod_c) against our PVS culling, the bake's LOD levels, and CS2's LOD switch (scenesystem 2026-11-12): a model's level on the CPU (0x1800fc2c0: bounding sphere -> screen fraction -> pixels of the view's height, 0x1804afed0's 50 / pixels against the switch metrics), the world aggregates' on the GPU (0x18006a1b7: the screen-size LOD scale / sc_instanced_mesh_lod_bias and the view height as render attributes 0x20913434 / 0x6e996b2f; the consuming shader not found). Tool: lasers-bake --shader-names (every shader's variable / attribute names, to hash for a token) |
| [lobby.md](lobby.md) | CS2's lobby and invite flow from pak01 (party / friend lobby, the invite toast and popup, its strings), the map veto (Premier's pick / ban panel), the server browser: what our custom lobbies take from each |
| [c4.md](c4.md) | Defuse: func_bomb_target's touch (m_bInBombZone), CC4's plant (the ground hull trace, 3 s arming on a 0.3 s clock, the duck override, AbortPlant), the planted bomb's spawn (mp_c4timer 40), C4Think (beeps, the defuse checks and the spin lockout, the blow + 1 s detonation), Use (CT only, line of sight, 10 / 5 s), OnDefuse, the explosion (500 / 3.5 R RadiusDamage, or the baked bomb damage shockwave at 3000 u/s with its Bias for ducking / facing), the round-start C4 gift, the win check's bomb outcomes and money reasons, the round clock (TargetSaved, nothing while planted), the voice alert, the defuse kit (CItemDefuser), the team damage rule, the duck override / defusing movement; client.dll's C_PlantedC4 beep and light schedule, the top bar's bomb status, the progress bar, the animations; the cvars |

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
| csgo legacy server.dll file offset 0xa36915 (text) | `function EntFire(target, action, value, delay, activator)`: the Squirrel prelude in the DLL; search `function <Name>(` for any other script helper (csgo-vscript.md 1) |
| csgo legacy server.dll 0x103b5ab0 / 0x103b6170 / 0x103b5dd0 | CBaseTrigger::Disable / EndTouch / PassesTriggerFilters; its vtable 0x108da2f0, found from the type descriptor 0x10a71a60 (".?AVCBaseTrigger@@") and the datamap builder at 0x103b5300 (a class's output offsets: search the output's name string, its one code xref is the builder) (csgo-triggers.md) |
| csgo legacy vphysics.dll 0x100b8030 | AngleVectors(angles ecx, forward edx, right, up): radians in SSE, x87 fsincos stored as f32, the vectors in SSE (crazykart-physics.md 11) |
| csgo legacy vphysics.dll 0x1006d240 | IVP_U_Quat::set_quaternion(IVP_U_Matrix3) (trace and largest-diagonal branches, normalised past 1e-10) |
| csgo legacy vphysics.dll 0x10075300 / 0x100760e0 | IVP_U_Matrix product (a.rows b, a.t + a.rows b.t; sums ((0 + 1) + 2)) / inverse (transpose, -(R^T t)) |
| csgo legacy vphysics.dll 0x1001e7a0 / 0x10074750 / 0x1001bc70 | CreatePhysicsObject / IVP_Real_Object::init_object_core / CPhysicsObject::ComputeDragBasis (crazykart-physics.md 11) |
| csgo legacy server.dll 0x1031ab20 / 0x1031aa20 | PhysCreateWorld_Shared (the BSP's world solids as static objects, the key parser's blocks, SetWorldMaterialIndexTable) / the virtual-terrain displacements vdisp_%04d (crazykart-physics.md 14) |
| csgo legacy vphysics.dll 0x10002380 / 0x10036220 / 0x100b8a70 | ParseFile (signed-char whitespace, `{}()':` breaks, `//` and `/* */`, 0x3ff cap) / ParseKeyvalue (both lowercased, no value after `}`) / ASCII stricmp (ivp-contacts.md 7a) |
| csgo legacy vphysics.dll 0x10018e70 / 0x10018f50 / 0x10019130 / 0x10034130 / 0x10033800 / 0x10035100 | GetSurfaceIndex ($MATERIAL_INDEX_SHADOW -> 0xf000) / GetPhysicsProperties (0xf000 -> +0x180, else >= 0x80 -> 0, out of range -> entry 0) / copy an index's data / the key parser's ParseSurfaceTable / NextBlock / ParseCustom (SkipBlock) (ivp-contacts.md 7a; ported: tools/kart-ivp-surfaces.mjs) |
| csgo legacy vphysics.dll 0x100984c0 | IVP_Mindist_Minimize_Solver::p_minimize_FF: two triangles through each other, the nearest of point / point, point / face, point / edge, edge / edge by brute force (x 1.000001 margin), then that pair's case (ivp-mindist.md 14; sim/src/ivp/minimize_ff.rs) |
| csgo legacy engine.dll 0x101e6650 / 0x101e7760 / 0x101e7660 / 0x101f52a0 / 0x101f5150 / 0x101f1cd0 | CollisionBSPData_LoadDispInfo (the displacement trees from the lumps) / CM_CreateDispPhysCollide (a virtual mesh per tree) / the PHYSDISP lump's hull offsets / DispCollTrees_Alloc / CDispCollTree::Create / its degenerate-triangle check (ivp-virtualmesh.md 2) |
| csgo legacy engine.dll 0x101d7030 / 0x101d76f0 / 0x101d67f0 / 0x101d6930 / 0x101d9cc0 | CCoreDispInfo: ctor / InitDispInfo / the surface's FindSurfPointStartIndex / AdjustSurfPointData / Create (called natively by KartOracle's Disp.cs; their math TODO) (ivp-virtualmesh.md 2) |
| csgo legacy engine.dll 0x101e7580 / 0x101e75d0 / 0x101e7620 / 0x101f5200 / 0x101f3360 | CVirtualTerrain::GetVirtualMesh / GetWorldspaceBounds / GetTrianglesInSphere, CDispCollTree::GetVirtualMeshList, AABBTree_GetTrisInSphere (radius in XMM2; sim/src/ivp/vmesh.rs tris_in_sphere) (ivp-virtualmesh.md 2, 5) |
| csgo legacy vphysics.dll 0x10007ea0 / 0x1002b980 / 0x1002b370 / 0x1002b3e0 / 0x1002bdc0 / 0x1002acf0 | CreateVirtualMesh (collision slot 47) / CPhysCollideVirtualMesh's ctor / the frame's cache lock / build / cache insert / CMeshInstance::Init (ivp-virtualmesh.md 3) |
| csgo legacy vphysics.dll 0x10002fc0 / 0x10003240 / 0x10002cc0 / 0x100024a0 / 0x1002ac70 | a virtual mesh triangle's two-sided ledge / the packed hulls' unpack / one hull's ledge / a packed hull's data start / the hulls' unpacked size (ivp-virtualmesh.md 3) |
| csgo legacy vphysics.dll 0x1002bc50 / 0x1002af50 / 0x1002b110 / 0x1007a3e0 / 0x1002baf0 / 0x1002bc00 / 0x1002b260 / 0x1002b2d0 | the mesh surface manager's get_all_ledges_within_radius / its triangle query / its hull list / a point's squared distance to a ledge's first triangle / radius and deviation / mass centre / the collide's GetMassCenter / GetSphereRadius (ivp-virtualmesh.md 3, 5) |
| csgo legacy server.dll 0x1031ca00 / 0x1031ce60 / 0x102f7de0 / 0x1031cd80 / 0x1043c2d0 / 0x102b56f0 | CPhysBox::Spawn (0x4000 -> group 1) / CreateVPhysics / PhysSolidOverride (a no-defaults handler) / the thin-model damping test / CCSGameRules::ShouldCollide / CGameRules::ShouldCollide (ivp-physbox.md, ivp-pileup.md 8) |
| csgo legacy server.dll 0x1069bf80 / 0x1069b0d0 / 0x1069b500 / 0x1069af90 / 0x1069bb10 / 0x101cb0c0 | AngleMatrix (x87 fsincos, yaw pitch roll) / MatrixInvert / ConcatTransforms (SSE rows, +0.0 lanes) / MatrixAngles / VectorAngles (f64 x 1/pi) / the fpatan leaf; CPhysThruster::OnActivate 0x102ee940, ScriptSetForward 0x10206080 (ivp-physbox.md 7; sim/src/math/csgo_mathlib.rs, checked natively) |
| csgo legacy server.dll 0x1069f9d0 / 0x1069fbe0 / 0x10347270 / 0x10347630 / 0x10267350 | VMatrix::SetupMatrixOrgAngles (AngleMatrix + origin column) / MatrixMultiply (4x4, plain order) / CPointTemplate::AddTemplate (inline InverseTR, matEntityToTemplate) / CreateInstance / CEnvEntityMaker::SpawnEntity (ivp-physbox.md 8; sim/src/math/csgo_mathlib.rs, checked natively) |
| csgo legacy vphysics.dll 0x100338c0 | ParseSolid's keys (index, surfaceprop, mass, inertia, damping, rotdamping, volume, drag, massCenterOverride) (ivp-physbox.md 2; sim/src/ivp/solid_keys.rs) |
| csgo legacy vphysics.dll 0x10073b10 / 0x100767c0 / 0x10075060 | delete_and_check_vicinity's second half (a static: the recheck at 0x21, 0x10082ce0, 0x100767c0) / a static core's contacts redone, their dynamic partners woken / ensure_in_simulation (Wake) (ivp-collide-off.md 7) |
| csgo legacy server.dll 0x1028c550 / 0x1028c400 | CBreakable::Die (NOT_SOLID now, SUB_Remove at curtime + 0.1: 6 ticks) / its drop of what rests on top (ivp-collide-off.md 7a) |
| csgo legacy vphysics.dll 0x100149f0 / 0x1001b560 / 0x100739f0 / 0x10073810 / 0x100781d0 / 0x10071980 / 0x100123c0 | CleanupDeleteList (Simulate's first step) / CPhysicsObject's dtor (shadow, then the vicinity wake when +0x14 & 0x20 and not silent) / delete_and_check_vicinity / IVP_Real_Object's dtor (hull listeners, contacts, out of its core) / the core's deletion (revive queue, controllers, out of its unit: no split) / the unit's core removal / the friction created event ("touched dynamic" 0x20) (ivp-collide-off.md 7) |
| csgo legacy vphysics.dll 0x10012980 / 0x1001ba20 / 0x1001b850 / 0x10014760 | the IVP collision filter (the solver's answer; 0 for a 0x800 / 0x400 pair) / IsMoveable / RecheckCollisionFilter / DestroyObject (fast-remove, +0x1c 0x400, the delete queue) (ivp-pileup.md 7, ivp-collide-off.md 7) |
| csgo legacy server.dll 0x10222080 / 0x10221f70 / 0x10221ff0 / 0x102341d0 / 0x1020a4a0 | CFuncWallToggle Toggle / TurnOff / TurnOn / CCollisionProperty::SetSolidFlags / CollisionRulesChanged (ivp-pileup.md 7) |
| csgo legacy vphysics.dll 0x10019180 / 0x10019d30 / 0x10019ea0 / 0x10019d00 | CPhysicsSurfaceProps::ParseSurfaceData (0xac-byte entries, the IVP material at +0, +8 always 0: no contact slides) / its insert / its grow / the material manager's slot 1 (a triangle's index through the world table) (ivp-contacts.md 7) |
| csgo legacy vphysics.dll 0x100722d0 / 0x10077820 / 0x10077750 | the unit's sleep check (all cores' movement state 3) / a core frozen / its speeds zeroed and q_next = q_last (crazykart-physics.md 12) |
| csgo legacy vphysics.dll 0x10087370 / 0x10071ef0 / 0x10086b70 | stage 1's revive of the Wake queue / a unit revived to the active list's head / a core revived (speeds kept only when t_psi == 0) |
| csgo legacy vphysics.dll 0x10072850 | the active units' walk: the first n - 3 in order, the last three from the last back |
| csgo legacy vphysics.dll 0x10073370 / 0x1001bfe0 / 0x10072af0 | IPhysicsObject::Sleep (reference 1 at now - 20 s, then the sleep check) / EnableMotion / the core's pin |
| csgo legacy vphysics.dll 0x1001d910 / 0x1001c700 / 0x1001d4e0 | SetVelocity / ApplyForceCenter / SetPosition (-> 0x10074b20 beam_object_to_new_position -> the core's 0x10097750) |
| csgo legacy vphysics.dll 0x10012b60 / 0x100836e0 | the anomaly manager's speed (0.99 x max) / rot speed (0.9 x the limit) hooks, stage 3 |
| csgo legacy vphysics.dll 0x100d8112 | the CRT's SSE2 expf (k = round(x 16384 / ln 2), three 2^(j/16384) tables, a degree-1 term): math/csgo_libm.rs expf |
| csgo legacy vphysics.dll 0x100982d0 / 0x10099850 | IVP_Mindist::recalc_mindist (time stamp, P_Finish_Counter 20, the minimize table 0x10110a28) / minimize_default_poly_poly: the closest-feature walk PP 0x100b4e20, PK 0x100b6070, Leave_PK 0x100b62d0, KK 0x100b3070, Leave_KK 0x100b36f0, PF 0x100b1ca0, Leave_PF 0x100b26d0 (ivp-mindist.md 5) |
| csgo legacy vphysics.dll 0x1006cd90 / 0x10074000 | IVP_Cache_Object's update (the object's pose at the environment's time; q_last when f32(t - t_psi) == 0) / get_m_world_f_object_AT (ivp-mindist.md 3) |
| csgo legacy vphysics.dll 0x10095310 / 0x10093ce0 | update_exact_mindist_events (the hull conversion, the max collision speed, the event's time and delays) / calc_time_of_next_event (table 0x10110bb0: KK 0x100a2d90, PF 0x100a2160 over IVP_3D_Solver 0x100b72a0 / 0x100b7510 / 0x100b7130) (ivp-mindist.md 7-8) |
| csgo legacy vphysics.dll 0x100957c0 / 0x10097db0 / 0x10093bb0 | the mindist's hull event (the halfspace estimate) / stage 4's synapse loop / IVP_Hull_Manager's reset (ivp-mindist.md 6) |
| csgo legacy vphysics.dll 0x100a68e0 / 0x100a6bb0 | IVP_U_Min_List add (ascending, a value goes before its equals) / remove: the hull managers' and the time manager's queues (ivp-mindist.md 6) |
| csgo legacy vphysics.dll 0x1007ac30 / 0x10079920 | IVP_Compact_Ledge_Solver::calc_qlen_KK (the squared edge-edge distance by the KK checks) / the KK input's line distance (ivp-mindist.md 5) |
| csgo legacy vphysics.dll 0x10099e60 | IVP_Compact_Ledge_Solver::minimize_on_other_side: from the pierce triangle over non-positive qr edges to unvisited neighbours (ivp-mindist.md 5) |
| csgo legacy vphysics.dll 0x10094bc0 / 0x10094b40 | exact_mindist_went_invalid / insert_invalid_mindist (the manager's +0x14 list) (ivp-mindist.md 10) |
| csgo legacy vphysics.dll 0x10082ce0 | a revived core's exact mindists to a dynamic core outside any friction system: recalc, below remove_dist a contact (0x10088450) and the units merged; answer 1 restarts 0x10071ef0's walk (ivp-pileup.md 6) |
| csgo legacy vphysics.dll 0x10072850 / 0x10071ef0 | stage 2's walk over the active list (+0x18, next +8, three behind) / a unit's revival (unlinked from +0x1a8, linked at +0x18's head) (ivp-pileup.md 6) |
| csgo legacy vphysics.dll 0x10094300 (0x10094419, 0x100945ec) | create_exact_mindists gives each object of the pair a cache when it has none (0x1006ccb0), a frozen one's from its frozen core (ivp-pileup.md 6) |
| csgo legacy vphysics.dll 0x10073a50 / 0x100980e0 / 0x10094a70 | an object's invalid mindists rechecked in stage 2 / recalc_mindist with the finish counter 0 / insert_exact_mindist (no recalc, no events) (ivp-pileup.md 5) |
| csgo legacy vphysics.dll 0x100789b0 | the compact ledge tree walk of get_all_ledges_within_radius: node sphere then per-axis box size bytes x radius x 0.004 (ivp-mindist.md 10) |
| csgo legacy vphysics.dll 0x100a1150 / 0x100a1240 | IVP_Range_Manager get_coll_range_intra_objects / get_coll_range_in_world (constants from its ctor 0x100a10c0) (ivp-mindist.md 4) |
| csgo legacy vphysics.dll 0x1009c010 / 0x1009b4e0 / 0x1009c0c0 | IVP_Solver_Core_Reaction: the cores' response at a point along 1-3 world directions (levers M^T (d x dir), the matrix ((r1 c1 + r0 c0) + r2 c2) + 1/m), and pushes along two of them into the speeds (ivp-contacts.md 4) |
| csgo legacy vphysics.dll 0x100d7fc5 / 0x100d7a68 | the CRT's SSE2 cosf (sinf's body, its own constants 0x100fc4b0, the row a quarter turn on: edx + 0x1c7610) / asinf (|x| in [0.0625, sqrt(3)/2]: asin(c) from the row 0x100fb690 + a correction; [2^-16, 0.0625): x + x^3/6 + 0.075 x^5 + 0.0446 x^7; below: x): math/csgo_libm.rs, bit for bit over the oracle's sweep (ivp-impact.md 2-3) |
| csgo legacy vphysics.dll 0x100779f0 / 0x1008bb40 | an impact's core synchronised to the event's time (rot, q_next saved at core+0x1ac; rot from asinf of the last step's rotation) / the impact system's end (the next PSI from now, stage 4's events, the mindists re-planned) (ivp-impact.md 3, 5) |
| csgo legacy vphysics.dll 0x100b18a0 / 0x100b16e0 / 0x100b14f0 / 0x100b1a00 / 0x100b1b30 / 0x100b1af0 | IVP_Mindist_Recursive (vtable 0x100f2ef8, delegator 0x100f2ee8): its ctor / slot 7 and slot 8 (split a ledge tree node's hull: the side by the terminal ledge, the virtual features, the bigger node) / its own mindists (create_exact_mindists with a fixed and a "from" ledge) / its hull event (recalc with P_Finish_Counter 0, 0x100980e0) / folded back into an exact mindist (ivp-mindist.md 13) |
| csgo legacy vphysics.dll 0x10096180 / 0x10094a70 / 0x10094b40 | insert_hull_mindist at the managers' next-PSI value without the angular hull times / insert_exact_mindist / insert_invalid_mindist (ivp-mindist.md 13) |
| csgo legacy vphysics.dll 0x1007ec20 | IVP_Contact_Point ctor: each synapse head-inserted into its object's friction-synapse list (IVP object +0x28): a list runs newest contact first (ivp-collide-off.md 1) |
| csgo legacy vphysics.dll 0x10094de0 (0x10094fd4..) | recheck_ov_element's pair filter: either object moving, not both cores flags & 0x12 (static / pinned), +0x44 0x200 / 0x400, the env's collision filter (ivp-collide-off.md 4) |
| csgo legacy vphysics.dll 0x100187f0 / 0x10018720 | the friction snapshot's GetNormalForce (contact +0x54 x 39.370079) / GetSurfaceNormal (+0x7c..+0x84 into Source axes, signed by side, over |n| + 1.1920929e-07) (ivp-pileup.md 2) |
| csgo legacy server.dll 0x102087d0 | an entity's root move parent (ShouldCollide's same-hierarchy test, ivp-pileup.md 3) |
| csgo legacy server.dll 0x102f6b10 | CCollisionEvent::ShouldCollide: two fixed entities (movetype NONE / PUSH, parented, custom with a shadow) never collide; then collision groups, contents (ivp-shadow.md 8) |
| csgo legacy vphysics.dll 0x10019ba1..0x10019c38 | the surfaceproperties parser's fallback entry for material index 0xf000 (the shadow material): friction 0.8, elasticity 0.001 (ivp-shadow.md 8) |
| csgo legacy vphysics.dll 0x10020fa0 / 0x10023fb0 | ComputeController (damp the speed by -damping capped at maxDampSpeed, add delta x scale capped at maxSpeed; the impulse out) / a quaternion's delta a x conj(b) in its sum order, normalised past 1e-10 (ivp-shadow.md 4) |
| csgo legacy vphysics.dll 0x10076950 | a core's objects changed (a new material, a mass): calc_calc, the objects' movement bytes, a core not simulated revived now (0x10071ef0) else its references re-timed, the friction contacts re-mixed (ivp-shadow.md 3) |
| csgo legacy vphysics.dll 0x10032e60 | CollideGetAABB's ledge-tree walk (left child at +0x1c first, then +[node]; a leaf's six support points into the min / max) (ivp-shadow.md 5) |
| csgo legacy server.dll 0x101f7f40 | CBaseEntity::UpdatePhysicsShadowToCurrentPosition (slot 163): UpdateShadow(abs origin +0x1dc, abs angles +0x1e8, false, dt) unless VPHYSICS (ivp-shadow.md 1) |
| csgo legacy vphysics.dll 0x100713b0 / 0x10071d40 / 0x10071dc0 | a simulation unit's controller list rebuilt from its cores' lists (each from its last controller: equal priorities reversed) / a controller attached to a core and its unit / detached (ivp-impact.md 4, 6) |
| csgo legacy vphysics.dll 0x100d7e25 | the CRT's SSE2 atanf (table 0x100fbee8 by c's high word; ported bit for bit: sim/src/math/csgo_atan.rs, ivp-contacts.md 6) |
| csgo legacy vphysics.dll 0x1009c880 / 0x1009c980 / 0x1009d270 | IVP_Great_Matrix_Many_Zero Gauss with pivoting / back substitution; IVP_Linear_Constraint_Solver (the complementarity solve) (ivp-contacts.md 5) |
| csgo legacy vphysics.dll 0x1006dc70 | the environment's temporary memory (env+0xa0 / +0x9c): a block per PSI (the long-term infos) |
| csgo legacy client.dll 0x107ab700 / 0x107ab7c0 / 0x107ac160 / 0x107ac270 | C_SteamJet: Start / Update (a particle a spawn event) / SimulateParticles / the lighting ramp (csgo-effects.md 1) |
| csgo legacy client.dll 0x10368f00 / 0x103690e0 / 0x10368ca0 | C_SpriteTrail: UpdateTrail (the ring's new point) / DrawModel (the beam's width, alpha, texture coordinate per point) / its bounds (csgo-effects.md 2) |
| csgo legacy client.dll 0x10799220 / 0x107998b0 / 0x107996a0 / 0x10796110 | CClient_Precipitation: InitializeParticlePrecip (systems per type) / the inner and outer dispatch (control points) / Precache (csgo-effects.md 3) |
| csgo legacy server.dll 0x10629060 | CSteamJet::Spawn (env_steamjet faces left, InitialState emits) (csgo-effects.md 1) |
| csgo legacy client.dll 0x107abea0 / 0x107abc20 / 0x1022f980 | C_SteamJet::RenderParticles (the ramp's lerp, the size by lifetime) / the unrolled quad / the rolled quad (csgo-effects.md 1) |
| csgo legacy engine.dll 0x100b6160 / 0x100b7210 / 0x10247b80 / 0x10246ea0 | IVEngineClient::GetLightForPoint (CEngineClient vtable 0x1047d850 slot 1) / slot 72 / ComputeLighting (no normal: the cube's six faces x 1/6, local lights folded in) / LightcacheGetDynamic (csgo-effects.md 1) |
| csgo legacy client.dll 0x109a94c0 / 0x109a9c50 / 0x109a9620 | CBeamSegDraw: Start / NextSeg (the segment normal, averaged at a point) / SpecifySeg (the two vertices) (csgo-effects.md 2) |
| csgo legacy client.dll 0x10798a30 / 0x10798ba0 / 0x10796430 / 0x10799600 | CClient_Precipitation: Simulate (the 0.125 s trace timer) / UpdateParticlePrecip (four rays: inside, nearby) / OnDataChanged (density = alpha x 0.01) / DestroyInnerParticlePrecip (csgo-effects.md 3) |
| csgo legacy client.dll 0x10994260 / 0x10995b30 / 0x109960d0 / 0x10994ee0 | RayTracingEnvironment: Trace4Rays / its traversal and triangle test (two-sided, 1e-10 epsilons, the triangle's own normal) / AddTriangle / SetupAccelerationStructure (unread) (csgo-effects.md 3) |
| csgo legacy client.dll 0x109616c0 / 0x1095fed0 / 0x10975cb0 | particle library: C_INIT_RtEnvCull (vtable 0x10d0765c) / C_INIT_LifespanFromVelocity (0x10d08c90) InitNewParticlesScalar / C_OP_SetControlPointToImpactPoint::Operate (0x10d0d1e8, unread) (csgo-effects.md 3) |
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

## How

- **Ghidra (ReVa MCP)**: `get-decompilation` for the shape; `find-cross-references` from a string (an input's
  "Class_API::Input" name, a think's "ClassThinkName", a schema field name) to its function; the decompiler drops
  register arguments and gets maxss / minss with NaN wrong, so read the disassembly for every sum.
- **tools/re/game/** (Python, read the DLL file directly; each takes the DLL path first):
  - `rtti.py <dll> <Class>`: the class's vtable through MSVC RTTI.
  - `bases.py <dll> <Class>`: the class's base classes through MSVC RTTI (the hierarchy descriptor), nearest first.
    2026-11-14, server.dll: CPostProcessingVolume <- CBaseTrigger <- CBaseToggle <- CBaseModelEntity <- CBaseEntity
    (so a post_processing_volume touches as a trigger: classes/triggers.js TOUCH_CLASSES).
  - `vslot.py <dll> <vtables> <slots>`: which function each class runs for a virtual.
  - `vdiff.py <dll> <base vt> <derived vt>`: the slots a class overrides (its Spawn is slot 0x48).
  - `disasm.py <dll> <va> [bytes] [--all]`: the instructions (pefile + capstone). `disasm_consts.py` (same
    arguments, `--fp` for float / call / jump lines only) also prints each rip-relative operand's address and f32.
  - `strings.py <dll> <regex>`: strings and their VAs (a class's think names, "Class_API::Input" names).
  - `xref.py <dll> <string | 0xVA> ...`: every rip-relative lea / mov to it and its function (Ghidra's xrefs
    without Ghidra). `callers.py <dll> <0xVA> ...`: every `call` / `jmp rel32` to a function.
  - `vtfind.py <dll> <vtable> <0xfunc> ...`: which slots of a vtable point at those functions.
  - `vtowner.py <dll> <0xfunc> ...`: the reverse: every class vtable and slot holding a function (through the RTTI
    locator before each vtable), e.g. that 180249530 is CCSPlayerPawn's slot 0xaf8. Slow for a function in hundreds of
    vtables (a base class's default).
  - `vslotall.py <dll> <0xslot> <Class> ...`: each class's function at one slot, to see who overrides a vfn
    (vfn 0xbf8 is 1809b5210 for every weapon class; Deploy 0xa18 has four).
  - `vcalls.py <dll> <0xslot> ...`: every `call [reg + slot]`, i.e. every virtual call through that slot.
  - `argcalls.py <dll> <0xcallee> <r8|rdx|rcx|r9>`: every direct call / jmp to a function with the last write to that
    argument register before it (which tracer type each FX_TracerSound caller passes: tracer-sound.md).
  - `svccall.py <dll> <0xfield> <0xslot>`: a load of `[reg + field]` followed by `call [reg + slot]`: who calls a
    services object's virtual through its owner's field (the pawn's water services +0xb30).
  - `f32refs.py <dll> <value>`: the f32's copies in the image and every rip-relative read of one (the client's twin of
    a server function by a shared constant: 9.765625e-06, the impact volume, player-sounds.md).
  - `enumtab.py <dll> <name>`: the pointers to a string with the 30 entries either side (an enum's name / value
    table: WeaponSound_t, player-sounds.md "Nearly empty").
  - `riprefs.py <dll> <0xVA> [...] [--imm N]`: every rip-relative operand in .text pointing at a VA (a string, a ConVar
    object, a global), found by bytes in seconds (an int32 at i with i + 4 + disp == target), with its .pdata function and
    the instruction; misses an operand with an immediate after it unless --imm N. E.g. the reservation reader
    (matchmaking.md) from the "[%x]" string.
  - `dispuses.py <dll> <0xstart> <0xend> <0xdisp> [...]`: every instruction in a VA range with one of the
    displacements in a memory operand, lea included (a field of one class's object inside that class's code: the
    physics game system's impact queue). An offset used as an immediate (`add rcx, 0x4c8`) needs a byte search.
  - `fieldwrites.py <dll> <0xoffset> [--reads]`: every store (or with --reads every use) of `[reg + offset]` (disp32,
    offsets >= 0x80), decoded by a linear sweep from the function's start; e.g. the five writers of
    m_flDamageAccumulator. Any class with a field at that offset shows up: read the function.
  - `reva.mjs <tool> <json>`: Ghidra ReVa over HTTP when the session's ReVa MCP tools are down (its header: how to
    start the headless server). `cvarreg.mjs <program> <cvar> ...`: a cvar's registration decompiled by ReVa (its
    object, default, flags), e.g. for engine2's cvars.
  - `protomsg.py <dll> <Message> ...`: one protobuf message's DescriptorProto decoded on its own, for a .proto blob
    protodesc.py can't parse whole (engine2's netmessages: CSVCMsg_PacketEntities' cmd_recv_status).
  - `cvardump.py <dll> <cvar> ...`: a ConVar's registration: its object (the value at [object + 8] + 0x58), flags,
    help text and the setup's default stores (a bool / int's default is the setup's +0x37; a float's in xmm2). A
    ConVarRef (18169e750 with a type) means the cvar lives in another DLL (engine2).
  - `cvardefs.py <dll> <names file> <out.json>`: many registrations at once, decoded to { type, default, min, max,
    flags, help, handle } (the int / bool and float forms: settings.md "Convar defaults").
  - `xhair_oracle.py <client.dll> <out.json> [count]`: client.dll's crosshair-code parse + rescale run under Unicorn
    (imports stubbed, globals pointed at test values): the pattern for checking a pure client function without the game.
  - `xhair_draw_oracle.py <client.dll> <out.json> [count]`: the crosshair's style functions under Unicorn on random
    crosshairs, their shape lists dumped (a fake object with the list pointer, the struct and the dynamic values).
  - `xhair_proj_oracle.py <client.dll> <out.json> [count]`: the crosshair's spread projection (180d9e560) through the
    real world-to-screen (180c19db0 / 180c19cd0 / 180da17d0) and AngleVectors (181740910) on random views, a view
    matrix planted at the slot's global; web/src/cs2web/client/settings/crosshair-proj-test.mjs checks crosshair-proj.js against it.
  - `xhair_lineup_oracle.py <client.dll> <out.json> [count]`: the grenade line-up crosshair (180da7770) on random views,
    with stubs for the engine, the view render's aspect, the UtlVector allocator and g_pMemAlloc's free (a bump heap).
  - `tier0_link.py`: the real tier0.dll in a client oracle's Unicorn (relocated to 0x260000000, the named imports
    pointed at its exports, its CRT FMA flag cleared): `tier0_link.link(uc, client_pe, tier0_path, ['V_tanf', ...])`.
    Use it instead of Python stand-ins for tier0's maths (they round differently).
  - `tier0_trig_oracle.py <tier0.dll> <out.json> [count]`: tier0's V_sincosf / V_tanf / V_atanf / V_expf / V_powf /
    V_roundf on random inputs (tier0-trig-test.mjs checks tier0-trig.js against it): the SSE2 path (Unicorn has no FMA).
  - `tier0_native.py <tier0.dll> <in.json> <out.json>`: the same inputs through tier0 loaded natively (ctypes, Windows
    x64): on an FMA3 CPU the CRT's FMA path, the oracle for tier0-fma.js. Native loading works for tier0 (no engine
    init needed for its maths): use it for any CPU-dispatched tier0 function.
  - `lasers-bake --shader-src <name> <out> --vars`: also the shader's variable descriptions, field by field
    (<name>_vars.txt: a texture's sampler, defaults, register; a sampler is a __RenderStateLiteral__).
  - `lasers-bake --shader-src <name> <out>`: a shader's programs from shaders_vulkan_dir.vpk decompiled (VRF's SPIR-V
    reflection) and its .vfx reconstructed; `--shader-api` prints VRF's shader API for a VRF update.
  - `fnat.py <dll> <0xVA> [--consts] [--around N]`: the function holding an address, from .pdata (exact bounds,
    its chained parts gathered), disassembled whole or around the address. Use it instead of guessing a start.
  - `protodesc.py <dll> <file.proto> [Message ...]`: a protobuf descriptor embedded in the DLL, decoded (field
    numbers, types, names: cs_usercmd.proto). `vtdump.py <dll> <0xvtable> [n]`: a vtable's slots with their sizes.
  - `pbsetters.py <dll> <0xhasbits> <0xbit> <0xfield>` / `nearstores.py <dll> <0xfield> <0xbit>`: inlined protobuf
    setters (an `or` of the has-bit next to the field's store; nearstores sweeps .text linearly, minutes on client.dll).
  - `fnstrings.py <dll> <0xstart> <0xend>`: the strings a function references (directly or via a pointer, as a
    ConVar's name), to name a vfn ("Player.Respawn").
  - `sibscan.py <dll> <0xdisp> [scale]`: every mov / lea / cmp with a `[base + index x scale + disp32]` operand, by
    bytes (seconds): who indexes an array inside a struct. E.g. that nothing reads the item definition's sound
    replacements at +0xf8 + slot x 8 (player-sounds.md "The vdata sound slots").
  - `schema.py <dll> <m_field>` / `--near <entry>`: a field's offset from the schema binding tables, and its class's
    neighbours (how CFuncRotating's layout came out in one call).
  - Constants: read 4 / 16 bytes at `rip + disp` (the instruction's end + disp) with pefile.
- **A live server's own state, tools/capture/** (Node): a local CS2 dedicated server from the Steam install
  (`cs2.exe -dedicated -insecure -usercon -maxplayers 64 -ip 127.0.0.1 +sv_lan 1 +rcon_password <pw> +map <map>`, run in
  the background, stopped after) driven over RCON: `rcon-cmd.mjs <port> <pw> <cmd>...` prints each reply (CS2 answers a
  frame later: rcon.mjs waits for the packets to stop), `entities.mjs` snapshots every entity's index through
  `ent_find` (docs/game/entity-index.md "Captured"). Gotchas: no `-condebug` (with no console window it floods
  console.log in the game folder), `sv_hibernate_when_empty 0` and `bot_join_after_player 0` for bots, and bots need a
  nav mesh (the ZE maps have none: use a stock map for anything about players).
- **The CS2 client's console, tools/capture/netcon.mjs** (2026-11-19, the paired shots: docs/MAP_SHOTS.md): a client
  started with `-netconport <port>` speaks VConsole2's binary protocol, not text: packets of a 4-byte type, u16
  version 0x00d4, u32 big-endian length (header included), u16 handle; a command is `CMND` + its text NUL-terminated,
  output comes as `PRNT` (text after 40 bytes). Its backlog is replayed on connect; one client at a time works best
  (close the socket cleanly). `getpos` prints the eye, `setpos` sets the origin (eye - 64 standing). Retail CS2 has no
  screenshot command: tools/capture/grab-window.ps1 (PrintWindow) + decode-grab.py (the grab is sRGB-encoded twice).
- **Checking a port bit for bit**: rubikon/tests/SceneOracle maps server.dll by hand (no loader, no initialisers:
  fill BSS constants such as the identity quaternion at 0x181f4a000 yourself), binds tier0 and kernel32 and calls a
  pure function natively, through a small thunk for __vectorcall ones; it writes the cases, a sim/src/bin/*_check
  compares the Rust port's bits. Modes: (none) AngleQuaternion, `--concat`, `--angles`, `--nodes`, `--movers`.
- **Calling a whole subsystem natively** (sim/src/bin/move_oracle, move-oracle.md): the same mapping in Rust, in one
  process with the sim: fake objects with logged copies of the real vtables, the engine's functions stubbed or hooked,
  TraceShape hooked onto the sim's trace world, .pdata registered for real call chains on a fault, int3 watches on a
  counter's increments.
- **A string's users** (`tools/re/game/strva.py <dll> <string>` -> its address, then `tools/re/game/riprefs.py <dll> <address>`):
  how the script API's `Entity.Teleport` was found (physics-prop.md 4): the registration function names every
  method, the callback itself names it again in its error messages.
