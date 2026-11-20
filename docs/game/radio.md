# The radio, the chat wheel, places, a match's voice cvars

server_20261105.dll / client_20261105.dll (archived in tools/re/binaries), pak01 (resource/csgo_english.txt, resource/ui/radiopanel.txt,
scripts/weapons.vdata, scripts/talker/*.vrr, soundevents/vo/agents/*.vsndevts, panorama/layout|styles/radialradio,
hud/hudradio, hud/hud), game/csgo/cfg/gamemode_*.cfg and user_keys_default.vcfg; read 2026-11-16. Ported in
src/cs2web/data/radio.js (tables), src/cs2web/data/radio-strings.js (generated: tools/radio-strings.mjs), server/cs2web/comms/radio.js,
server/cs2web/comms/places.js, server/cs2web/comms/chat-say.js, client/comms/radio.js; checked by server/cs2web/comms/radio-test.mjs.

Tools this added: `lasers-bake --decompile <vpk> <path regex> <out>` (bake/DecompileBake.cs: any resource through
ValveResourceFormat, for reading panorama / vsndevts / vrr / vdata) and `lasers-bake --vo <pak01> <out> <set,...>`
(bake/VoBake.cs: the agents' radio lines).

## 1. A team match's voice cvars

gamemode_competitive.cfg and gamemode_competitive2v2.cfg both set `sv_talk_enemy_living 0`, `sv_talk_enemy_dead 0`,
`sv_deadtalk 1`, `sv_auto_full_alltalk_during_warmup_half_end 0`; gamemode_deathmatch.cfg `1 / 1 / 1`. None sets
sv_full_alltalk or sv_spec_hear: their registered defaults hold (0 and 3, server/cs2web/comms/voice.js VOICE_CVARS). So in
3v3 / 5v5 only teammates hear each other; a dead player is heard by living teammates and hears them. **1v1 runs
sv_full_alltalk 1: the owner's choice (2026-11-16), not CS2's** (src/cs2web/gamemodes.js OWNER_1V1). sv_full_alltalk is
only read for type 0 (voice) in 1809131f0, so chat and the radio keep the team rule there.

## 2. The radio

| Address | What |
|---|---|
| 1802006b0 | CCSPlayerController's ClientCommand radio half: first 180219840 (the radio commands); then `playerradio`, `playerchatwheel`, `ignorerad` |
| 180219840 | radio command by name (V_stricmp_fast): requires the pawn alive (vfn 0x550) and 180b5d1b0 false (pawn+0xb28's vfn 0xb8: unread, TODO); coverme / takepoint call the throttle and 180239eb0 directly and fire `player_radio` (userid, slot 0x13 / 0x10); the rest go to 180219040 (holdpos 5, followme 6, takepoint 0x10, coverme 0x13, regroup 0x14, takingfire 0x15), 180219230 (go 2, fallback 3, sticktog 4, cheer 10, compliment 11, thanks 12, report 0x16), 180219440 (roger 8, negative 9, enemyspot 0xe, needbackup 0xf, sectorclear 0x11, inposition 0x12, reportingin 0x17, getout 0x18, enemydown 0x19); each: throttle, its switch's (sound, token), 180239eb0, `player_radio` with the slot |
| 180219440 case 8 | roger: RandomInt(0, 1): 0 Radio.Roger / #Cstrike_TitlesTXT_Roger_that, 1 Radio.Affirmitive / #Cstrike_TitlesTXT_Affirmative |
| 180202570 | the radio throttle: the controller's three GameTimes at +0x54 / +0x58 / +0x5c; the first unset (-1) or older than now - sv_radio_throttle_window takes now (returns 1), else 0 |
| 180050a30 | sv_radio_throttle_window registration: float default 10.0, flags 0x80000 (its help string is the allow list's, a copy) |
| 180050980 | sv_playerradio_use_allowlist: bool default 1 |
| 180050cb0 | tv_relayradio: bool default 0 ("Relay team radio commands to TV") |
| 18004f0f0 | bot_chatter_use_rr: bool default 1 ("1 = Use response rules"): the radio's voice goes through the response rules |
| 1800b45e0 | sv_ignoregrenaderadio: bool default 0, flags 0x280000 ("Turn off Fire in the hole messages") |
| 180239eb0 | Radio(controller, sound, token, bool auto, bool chatwheel): (chatwheel && (no gamerules or 18093de70)) or the pawn alive; the retakes text filter (18093df00 / 18093e4b0: retakes only); recipients 180202390; the line: `#SLOTNAME[%d]%s` (slot, name), the place 180926b60(gamerules, 1, controller); a place -> 1802522c0 HUD_PRINTTALK (3) `#Game_radio_location` (name, place, token, %s4), else a TextMsg `#Game_radio` (name, token, "", %s4); %s4 is "auto" (181791f94) when `auto`, else ""; the voice: bot_chatter_use_rr (181f9e2c8 +0x58) on -> the pawn's Speak (vfn 0xc80) of the sound as a concept to the same filter, off -> a SendAudio user message (radio_sound) of the sound event |
| 18093de70 | game_type 0 and game_mode 6, 1, 3, 4 or 2: a dead player may use the chat wheel (the mode numbers read as CS2's game_mode values: TODO) |
| 180202390 | the radio's recipient filter: every controller; a GOTV one (controller+0x510) by tv_relayradio; else not ignoring the radio (pawn+0xe58 -> controller +0x60, ignorerad) and CanPlayerHearPlayer(gamerules, listener, talker, 1) (1809134a0 with type 1: the say's team rule) |
| 1802006b0 `ignorerad` | toggles controller+0x60, prints #Cstrike_TitlesTXT_Ignore_Radio / _Accept_Radio (HUD_PRINTTALK) |
| 1802006b0 `playerchatwheel` | argc must be 3 ("Need two arguments to playerchatwheel"); arg1 (CW.name) looked up in 1817973c0 ({ token, CW.name } pairs, V_stricmp_fast on the name); not found: nothing; throttle; Radio(sound = arg1, token = the table's, auto 0, chatwheel 1) |
| 1802006b0 `playerradio` | argc 2 or the allow list on: arg1 looked up in 181796d90 ({ Radio.X, token } of the 22 commands); the token the table's; else argc must be 3, the sound and token the client's; throttle; Radio(auto 0, chatwheel 0) |
| 1809d4a50 | CBaseCSGrenade's throw: EmitGrenade (vfn 0xdd0) ... then unless sv_ignoregrenaderadio: the weapon vdata's sound slot 0x17 (WEAPON_SOUND_RADIO_USE) and m_szUseRadioSubtitle (vdata + 0x7e8), both non-empty -> Radio(controller (pawn+0xe58), sound, subtitle, auto 1, chatwheel 0): no throttle; then `grenade_thrown` (userid, weapon, priority 1) |

The grenades' lines (scripts/weapons.vdata): weapon_hegrenade Radio.FireInTheHole / #SFUI_TitlesTXT_Fire_in_the_hole
("HE Grenade!"), weapon_flashbang Radio.Flashbang / _Flashbang_in_the_hole, weapon_smokegrenade Radio.Smoke /
_Smoke_in_the_hole, weapon_molotov Radio.Molotov / _Molotov_in_the_hole, weapon_incgrenade Radio.Incendiary /
_Incendiary_in_the_hole, weapon_decoy Radio.Decoy / _Decoy_in_the_hole (the base "grenade" class: Radio.FireInTheHole).

The client's line (client 1811ac670, radio_status.cpp): param %s4 compared with "auto" (5 bytes); not "auto": a check
of the sender (1811acc56 -> 180c0dad0 / 180c13a30(slot); its result skips the line: TODO, read as nothing); then the
sender's team (controller byte +0x3e7) localizes `game_radio_team_prefix_%d` ("[T] " / "[CT] ") into %s4. The strings:
`Game_radio` " %s4\x03%s1\x01: %s2", `Game_radio_location` " %s4\x03%s1\x04﹫%s2\x01: %s3".

### The voice (the response rules)

scripts/talker/response_rules.vrr includes one talker per voice set (phoenix.vrr, sas.vrr, ... 30); each includes
shared.vrr and its soundevents/vo/agents/game_sounds_<set>.vsndevts. A response group's embedded rule asks for a
concept criterion (`TLK_Radio.GoGoGo`: shared.vrr `m_matchKey "concept"`, `m_matchExpr "Radio.GoGoGo"`; the chat
wheel's `TLK_CW.*`), `Is<set>` (`m_matchKey "model"`, e.g. Isphoenix = "tm_phoenix", Issas = "ctm_sas"; an agent item's
`vo_prefix` in items_game names the set of the epic agents) and `IsTalk<set>` (`worldTalk<set> != 1`), and sets
`m_context "Talk<set>:1:1"` with `m_bApplyContextToWorld`: one line of a set at a time, world-wide, for 1 s. Its
responses are SPEAK lines (sound events) or RESPONSE (another group). Some chat wheel concepts have rules and no
responses (CW.NeedGrenade ...): silent. The events (game_sounds_phoenix.vsndevts): mixgroup VO, position_offset
[0, 0, 60], a flat distance curve (1.0 at 0 and 300).

Baked: `lasers-bake --vo <pak01> <out> phoenix,sas` -> vo.json (set -> concept -> events) + soundevents.json + sounds
(372 lines, 36 MB WAV), in web/public/maps/de_dust2/vo (the dev map's folder: TODO move to a shared folder).

TODO: the response system's pick (uniform here; a few lines carry m_params m_odds 3), the "model" context's value
for an agent (read: the model key / vo_prefix), the other criteria (health, place, map ...).

## 3. The radio menus and the chat wheel (client)

user_keys_default.vcfg: `c "+radialradio"`, `v "+radialradio2"`, `z "radio"` (and `mouse3 "player_ping"`).

resource/ui/radiopanel.txt (CCSGO_HudRadio, client "resource/ui/radiopanel.txt", "hotkey", "#SFUI_Radio_Exit"):
groups common (hotkey 0, #SFUI_CommonRadio: roger, negative, cheer, holdpos, followme, thanks), standard (1,
#SFUI_CommandRadio: go, fallback, sticktog, holdpos, followme), group (2, #SFUI_StandardRadio: roger, negative, cheer,
compliment, thanks), report (3, #SFUI_ReportRadio: enemyspot, needbackup, takepoint, sectorclear, inposition), each
timeout 5. `radio` opens hotkey 0, radio1..3 the others (read off the hotkeys: TODO the client's own pick). Layout:
hudradio.vxml (RadioPanelBG, RadioPanel), hudradio.vcss (heading 24 px #999 uppercase, options 18 px #ccc, the panel
#000000b3), hud.vcss `#HudRadio { position: 0px 460px 0px; }`.

The chat wheel (CSGORadialRadio, radialradio.vxml / .vcss; hud.vxml's sounds UIPanorama.loadout_sector_*):
+radialradio / 2 / 3 (client strings), tab N's phrases cl_radial_radio_tab_N_text_1..8 (string ConVars, flags
0x80088; defaults from the registration stubs 1801016f0.., the `lea rdx` before `mov byte [rsp+0x34], 1`):

| tab | 1 (top) | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| 0 | quiet | requestecoround | bplan | requestweapon | midplan | droppedbomb | aplan | requestspend |
| 1, 2 | bombcarrierspotted | requestecoround | multipleenemieshere | requestweapon | rotatetome | ihavethebomb | oneenemyhere | requestspend |

(all `#Chatwheel_*`). The selection says `playerchatwheel %s "%s"` (CW name, token). Not read: cl_radial_radio_version_reset's
rewrite, cl_radial_radio_tap_to_ping / cl_radial_menu_tap_duration (a tap pings), the segments' icons
(icons/ui/chatwheel_*.svg).

## 4. Places (m_szLastPlaceName)

| Address | What |
|---|---|
| schema | CCSPlayerPawn m_szLastPlaceName at pawn + 0xe78 (CNetworkStringBase<18>: networked) |
| 180252d20 | the place update (called from 180236640, the pawn's per-tick think that also holds the AFK bomb drop): point = origin + (0, 0, 35.5); 18020c1b0(point, the place before at +0xfd0 / its kind +0xfd4); kind or handle changed -> m_szLastPlaceName = 180213120's name (V_strncpy 0x12) or "" |
| 18020c1b0 | the lookup: the place before kept if an env_cs_place (kind 2) and the point is inside its collision (181477220(shape, xform, point, 1.0)); else the env_cs_place list from 181f9ef00 through +0x860 (creation order), the first containing the point (kind 2); else the nav mesh's place at the point (18039e7e0, kind 1); else the place before if it is a live env_cs_place; else kind 0 |
| 1801f7bf0 / 1801f98e0 | CCSPlace's constructor (appends to the list's tail 181f9ef08, its place name +0x868 null) and destructor (unlinks) |
| 180213120 | a place's name: kind 1 the nav mesh's place table (1814af390 over 18234ace8+0x98), kind 2 the entity's +0x868 (place_name) |
| 180926b60 | the place a chat / radio line uses: the controller's team (+0x344) T or CT, its pawn a live CS player pawn: pawn + 0xe78, else none |
| 1809268f0 | the say's token: team chat from an alive (or the game phase 4 / 5) T / CT with a place -> Cstrike_Chat_CT_Loc / _T_Loc (" [CT] \x03%s1\x04﹫%s3\x01: %s2") |

de_dust2 has 43 env_cs_place volumes (24 names: TSpawn, TRamp, OutsideTunnel, UpperTunnel, ..., all in the baked
entities.json and hulls.json already). The names: csgo_english's "Place names used in bot chatter, and in location
strings for player chat" section (TSpawn "T Start", CTSpawn "CT Start", ...: src/cs2web/data/radio-strings.js PLACE_NAMES).

Not found on the HUD: hud.vxml, hudradar.vxml and hudteamcounter have no place panel; the client reads
m_szLastPlaceName somewhere not traced (TODO). Not ported: the nav mesh places (maps/de_dust2.nav is v36 with KV3
blocks), #Notice_Teammate_Death_Location (1802089a0, "%s1 died %s2").
