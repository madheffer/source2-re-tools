# Radio, chat wheel, places, a match's voice cvars

server_20261105, client_20261105. pak01: resource/csgo_english.txt, resource/ui/radiopanel.txt, scripts/weapons.vdata,
scripts/talker/*.vrr, soundevents/vo/agents/*.vsndevts, panorama radialradio / hud/hudradio / hud/hud;
game/csgo/cfg/gamemode_*.cfg, user_keys_default.vcfg.

## Functions

| Address | Module | What |
|---|---|---|
| 1802006b0 | server | CCSPlayerController's ClientCommand radio half: first 180219840, then `playerradio`, `playerchatwheel`, `ignorerad` |
| 180219840 | server | radio command by name (V_stricmp_fast): pawn alive (vfn 0x550) and 180b5d1b0 false |
| 180b5d1b0 | server | pawn+0xb28's vfn 0xb8 (unread) |
| 180219040 / 180219230 / 180219440 | server | the three command switches: throttle, (sound, token), 180239eb0, `player_radio` with the slot |
| 180202570 | server | radio throttle |
| 180239eb0 | server | Radio(controller, sound, token, bool auto, bool chatwheel) |
| 18093de70 | server | a dead player may use the chat wheel: game_type 0 and game_mode 6, 1, 3, 4 or 2 (read as CS2's game_mode values: TODO) |
| 18093df00 / 18093e4b0 | server | retakes text filter (retakes only) |
| 180202390 | server | the radio's recipient filter |
| 1809134a0 | server | CanPlayerHearPlayer(gamerules, listener, talker, type) (type 1: the say's team rule) |
| 1809131f0 | server | reads sv_full_alltalk, only for type 0 (voice) |
| 180926b60 | server | the place a chat / radio line uses (gamerules, 1, controller) |
| 1802522c0 | server | HUD_PRINTTALK (3) |
| 1809d4a50 | server | CBaseCSGrenade's throw |
| 180252d20 | server | place update (from 180236640) |
| 180236640 | server | the pawn's per-tick think (also the AFK bomb drop) |
| 18020c1b0 | server | place lookup (point, the place before +0xfd0, its kind +0xfd4) |
| 181477220 | server | point in collision (shape, xform, point, 1.0) |
| 18039e7e0 | server | the nav mesh's place at a point (kind 1) |
| 1801f7bf0 / 1801f98e0 | server | CCSPlace constructor (appends to the list tail 181f9ef08, name +0x868 null) / destructor (unlinks) |
| 180213120 | server | a place's name: kind 1 the nav mesh's place table (1814af390 over 18234ace8+0x98), kind 2 the entity's +0x868 (place_name) |
| 1809268f0 | server | the say's token |
| 1802089a0 | server | #Notice_Teammate_Death_Location ("%s1 died %s2") |
| 180050a30 | server | sv_radio_throttle_window registration |
| 180050980 | server | sv_playerradio_use_allowlist registration |
| 180050cb0 | server | tv_relayradio registration |
| 18004f0f0 | server | bot_chatter_use_rr registration |
| 1800b45e0 | server | sv_ignoregrenaderadio registration |
| 1811ac670 | client | the radio line (radio_status.cpp) |
| 1811acc56 -> 180c0dad0 / 180c13a30(slot) | client | sender check: its result skips the line (TODO, read as nothing) |
| 1801016f0.. | client | cl_radial_radio_tab_N_text_* registration stubs |

## Fields

| Offset | Field |
|---|---|
| controller +0x54 / +0x58 / +0x5c | the throttle's three GameTimes |
| controller +0x60 | ignorerad |
| controller +0x510 | GOTV |
| controller +0x344 | team |
| pawn +0xe58 | controller |
| pawn +0xe78 | m_szLastPlaceName (CNetworkStringBase<18>, networked) |
| pawn +0xfd0 / +0xfd4 | the place before / its kind (0 none, 1 nav, 2 env_cs_place) |
| place entity +0x868 | place_name |
| place list 181f9ef00 + 0x860 | env_cs_place list (creation order) |
| weapon vdata sound slot 0x17 | WEAPON_SOUND_RADIO_USE |
| weapon vdata +0x7e8 | m_szUseRadioSubtitle |
| client controller byte +0x3e7 | the sender's team |

## Constants

| Value | What |
|---|---|
| sv_radio_throttle_window float 10.0, flags 0x80000 | its help string is the allow list's (a copy) |
| sv_playerradio_use_allowlist bool 1 | |
| tv_relayradio bool 0 | "Relay team radio commands to TV" |
| bot_chatter_use_rr bool 1 (181f9e2c8 +0x58) | "1 = Use response rules" |
| sv_ignoregrenaderadio bool 0, flags 0x280000 | "Turn off Fire in the hole messages" |
| 181791f94 | "auto" |
| 1817973c0 | chat wheel table: { token, CW.name } pairs |
| 181796d90 | playerradio allow list: { Radio.X, token } of the 22 commands |
| (0, 0, 35.5) | place point offset from origin |
| 0x12 | V_strncpy length of the place name |
| cl_radial_radio_tab_N_text_1..8 flags 0x80088 | string ConVars (defaults: the `lea rdx` before `mov byte [rsp+0x34], 1`) |

## Voice cvars (cfgs)

- gamemode_competitive.cfg and _competitive2v2.cfg: `sv_talk_enemy_living 0`, `sv_talk_enemy_dead 0`, `sv_deadtalk 1`, `sv_auto_full_alltalk_during_warmup_half_end 0`; gamemode_deathmatch.cfg `1 / 1 / 1`.
- None sets sv_full_alltalk or sv_spec_hear: defaults 0 and 3. Only teammates hear each other; a dead player is heard by living teammates and hears them.

## Radio commands (180219840)

| Command | Slot | Switch |
|---|---|---|
| go | 2 | 180219230 |
| fallback | 3 | 180219230 |
| sticktog | 4 | 180219230 |
| holdpos | 5 | 180219040 |
| followme | 6 | 180219040 |
| roger | 8 | 180219440 |
| negative | 9 | 180219440 |
| cheer | 10 | 180219230 |
| compliment | 11 | 180219230 |
| thanks | 12 | 180219230 |
| enemyspot | 0xe | 180219440 |
| needbackup | 0xf | 180219440 |
| takepoint | 0x10 | 180219040 (also called directly) |
| sectorclear | 0x11 | 180219440 |
| inposition | 0x12 | 180219440 |
| coverme | 0x13 | 180219040 (also called directly) |
| regroup | 0x14 | 180219040 |
| takingfire | 0x15 | 180219040 |
| report | 0x16 | 180219230 |
| reportingin | 0x17 | 180219440 |
| getout | 0x18 | 180219440 |
| enemydown | 0x19 | 180219440 |

- coverme / takepoint call the throttle and 180239eb0 directly and fire `player_radio` (userid, slot 0x13 / 0x10).
- roger (180219440 case 8): RandomInt(0, 1): 0 Radio.Roger / #Cstrike_TitlesTXT_Roger_that, 1 Radio.Affirmitive / #Cstrike_TitlesTXT_Affirmative.

## Throttle (180202570)

The first of the three times unset (-1) or older than now - sv_radio_throttle_window takes now (returns 1), else 0.

## Radio (180239eb0)

1. Requires (chatwheel && (no gamerules or 18093de70)) or the pawn alive; the retakes text filter; recipients 180202390.
2. Line `#SLOTNAME[%d]%s` (slot, name); place 180926b60. A place -> 1802522c0 HUD_PRINTTALK `#Game_radio_location` (name, place, token, %s4), else TextMsg `#Game_radio` (name, token, "", %s4); %s4 = "auto" when `auto`, else "".
3. Voice: bot_chatter_use_rr on -> the pawn's Speak (vfn 0xc80) of the sound as a concept to the same filter; off -> a SendAudio user message (radio_sound) of the sound event.

## Recipients (180202390)

Every controller; a GOTV one by tv_relayradio; else not ignoring the radio (pawn+0xe58 -> controller +0x60) and CanPlayerHearPlayer(gamerules, listener, talker, 1).

## ClientCommand (1802006b0)

- `ignorerad`: toggles controller+0x60, prints #Cstrike_TitlesTXT_Ignore_Radio / _Accept_Radio (HUD_PRINTTALK).
- `playerchatwheel`: argc must be 3 ("Need two arguments to playerchatwheel"); arg1 (CW.name) looked up in 1817973c0 (V_stricmp_fast on the name); not found: nothing; throttle; Radio(sound = arg1, token = the table's, auto 0, chatwheel 1).
- `playerradio`: argc 2 or the allow list on: arg1 looked up in 181796d90, the table's token; else argc must be 3, the sound and token the client's; throttle; Radio(auto 0, chatwheel 0).

## Grenade radio (1809d4a50)

EmitGrenade (vfn 0xdd0) ... then unless sv_ignoregrenaderadio: vdata sound slot 0x17 and m_szUseRadioSubtitle both
non-empty -> Radio(controller (pawn+0xe58), sound, subtitle, auto 1, chatwheel 0): no throttle; then `grenade_thrown`
(userid, weapon, priority 1).

| Weapon (weapons.vdata) | Sound | Subtitle |
|---|---|---|
| weapon_hegrenade | Radio.FireInTheHole | #SFUI_TitlesTXT_Fire_in_the_hole ("HE Grenade!") |
| weapon_flashbang | Radio.Flashbang | _Flashbang_in_the_hole |
| weapon_smokegrenade | Radio.Smoke | _Smoke_in_the_hole |
| weapon_molotov | Radio.Molotov | _Molotov_in_the_hole |
| weapon_incgrenade | Radio.Incendiary | _Incendiary_in_the_hole |
| weapon_decoy | Radio.Decoy | _Decoy_in_the_hole |
| "grenade" base class | Radio.FireInTheHole | |

## Client line (1811ac670)

%s4 compared with "auto" (5 bytes); not "auto": the sender check, then the sender's team localizes
`game_radio_team_prefix_%d` ("[T] " / "[CT] ") into %s4. `Game_radio` " %s4\x03%s1\x01: %s2", `Game_radio_location`
" %s4\x03%s1\x04﹫%s2\x01: %s3".

## Voice lines (response rules)

- scripts/talker/response_rules.vrr includes one talker per voice set (phoenix.vrr, sas.vrr, ... 30); each includes shared.vrr and soundevents/vo/agents/game_sounds_<set>.vsndevts.
- A group's rule asks for a concept (`TLK_Radio.GoGoGo`: shared.vrr `m_matchKey "concept"`, `m_matchExpr "Radio.GoGoGo"`; the chat wheel's `TLK_CW.*`), `Is<set>` (`m_matchKey "model"`, e.g. Isphoenix = "tm_phoenix", Issas = "ctm_sas"; an agent item's `vo_prefix` in items_game names the set of epic agents) and `IsTalk<set>` (`worldTalk<set> != 1`), and sets `m_context "Talk<set>:1:1"` with `m_bApplyContextToWorld`: one line of a set at a time, world-wide, for 1 s.
- Responses are SPEAK lines (sound events) or RESPONSE (another group). Some chat wheel concepts have rules and no responses (CW.NeedGrenade ...): silent. A few lines carry m_params m_odds 3.
- Events (game_sounds_phoenix.vsndevts): mixgroup VO, position_offset [0, 0, 60], a flat distance curve (1.0 at 0 and 300). phoenix + sas: 372 lines.

## Radio menus (client)

- user_keys_default.vcfg: `c "+radialradio"`, `v "+radialradio2"`, `z "radio"` (`mouse3 "player_ping"`).
- resource/ui/radiopanel.txt (CCSGO_HudRadio; client strings "resource/ui/radiopanel.txt", "hotkey", "#SFUI_Radio_Exit"), each group timeout 5:

| Group | hotkey | Title | Commands |
|---|---|---|---|
| common | 0 | #SFUI_CommonRadio | roger, negative, cheer, holdpos, followme, thanks |
| standard | 1 | #SFUI_CommandRadio | go, fallback, sticktog, holdpos, followme |
| group | 2 | #SFUI_StandardRadio | roger, negative, cheer, compliment, thanks |
| report | 3 | #SFUI_ReportRadio | enemyspot, needbackup, takepoint, sectorclear, inposition |

- `radio` opens hotkey 0, radio1..3 the others (read off the hotkeys: TODO the client's own pick).
- Layout: hudradio.vxml (RadioPanelBG, RadioPanel), hudradio.vcss (heading 24 px #999 uppercase, options 18 px #ccc, panel #000000b3), hud.vcss `#HudRadio { position: 0px 460px 0px; }`.

## Chat wheel (CSGORadialRadio)

radialradio.vxml / .vcss; hud.vxml's sounds UIPanorama.loadout_sector_*; +radialradio / 2 / 3. All `#Chatwheel_*`:

| Tab | 1 (top) | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| 0 | quiet | requestecoround | bplan | requestweapon | midplan | droppedbomb | aplan | requestspend |
| 1, 2 | bombcarrierspotted | requestecoround | multipleenemieshere | requestweapon | rotatetome | ihavethebomb | oneenemyhere | requestspend |

The selection sends `playerchatwheel %s "%s"` (CW name, token).

## Places

- 180252d20: point = origin + (0, 0, 35.5); 18020c1b0; kind or handle changed -> m_szLastPlaceName = 180213120's name (V_strncpy 0x12) or "".
- 18020c1b0: the place before kept if an env_cs_place (kind 2) containing the point; else the first env_cs_place in the list containing it (kind 2); else the nav mesh's place (kind 1); else the place before if a live env_cs_place; else kind 0.
- 180926b60: the controller's team T or CT and its pawn a live CS player pawn: pawn + 0xe78, else none.
- 1809268f0: team chat from an alive (or game phase 4 / 5) T / CT with a place -> Cstrike_Chat_CT_Loc / _T_Loc (" [CT] \x03%s1\x04﹫%s3\x01: %s2").
- de_dust2: 43 env_cs_place volumes, 24 names (TSpawn, TRamp, OutsideTunnel, UpperTunnel, ...). Display names: csgo_english's "Place names used in bot chatter, and in location strings for player chat" section (TSpawn "T Start", CTSpawn "CT Start", ...). maps/de_dust2.nav is v36 with KV3 blocks.

## Unread

- 180b5d1b0 (pawn+0xb28's vfn 0xb8); the client's sender check (1811acc56).
- 18093de70's mode numbers as game_mode values.
- The response system's pick; the "model" context's value for an agent (the model key / vo_prefix); the other criteria (health, place, map ...).
- radio vs radio1..3: the client's own pick.
- cl_radial_radio_version_reset's rewrite, cl_radial_radio_tap_to_ping / cl_radial_menu_tap_duration (a tap pings), the segments' icons (icons/ui/chatwheel_*.svg).
- Where the client reads m_szLastPlaceName (hud.vxml, hudradar.vxml and hudteamcounter have no place panel).
