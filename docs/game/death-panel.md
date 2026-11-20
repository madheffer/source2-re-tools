# The death panel ("killed by")

client_20261015.dll (Ghidra) unless marked. Ported in web/src/ui/death-panel.js / .css, the strings by
tools/deathpanel-strings.mjs (web/src/cs2web/data/death-panel-strings.js), the server's numbers in server/cs2web/combat/kill-notice.js
lastKillerDamage.

## The message: CCSUsrMsg_SendLastKillerDamageToClient (cstrike15_usermessages.proto, tools/re/game/protomsg.py)
- Fields: 1 num_hits_given, 2 damage_given, 3 num_hits_taken, 4 damage_taken, 5 actual_damage_given,
  6 actual_damage_taken (int32). C++ layout +0x48 .. +0x5c in that order.
- Client handler **180c8d8c0** -> **180e8e3c0**(panel, damage_taken, hits_taken, damage_given, hits_given,
  actual_given, actual_taken): stored at panel +0x1a8 / +0x1ac / +0x1b0 / +0x1b4 / +0x1b8 / +0x1bc, +0x1c0 = 1 (armed);
  then with the local player's state (180c97a10) 4 and the game state (+0x84) not 5: show (180e8aaf0) if not shown;
  else disarmed, and a shown panel hides (180e877b0) unless a replay (1804ffb20 / 1804ffd30) runs.
- **180e8d660** (from 180c76830) and **180e97430**: disarm, then the same show / hide rule (the respawn hides it).
- Server sender **180b21fd0** (server_20261105), called on the lethal hit (180a94520) with the victim's +0x800 services
  and the attacker: over the victim's records, the one victim -> killer gives num_hits_given (+0x6c), damage_given
  ((int) +0x64), actual_damage_given ((int) +0x68), the one killer -> victim the taken ones; built with 1807ad580 and
  sent through 1821b9498 vfn 0x78.

## Showing: 180e8aaf0
- DeathPanelRoot--Hidden off, +0x1a0 = 1; 180e8f3a0(1): DeathPanel--Hidden off, DeathPanel--FadeIn re-triggered;
  180e8f4c0(0) (the screenshot panel off); DeathCancel--Hidden on.
- The killer: the local player's killer (controller +0x1ed4 -> m_hPawn), its controller; killer_playerslot for the
  name label; the health fraction = max(health +0x34c, 0) / max health (vfn 0x550), forced -1 when the cvar at
  1825510d8 is set, 0 when not alive (vfn 0x4e8); 180e8b640(panel, killer, fraction) (not read: the bar).
- 180e8bbd0: DeathPanel__Damage--Hidden on the Taken row when damage_taken == 0, the Given row when damage_given == 0;
  the dialog variables hits_taken, damage_taken, hits_given, damage_given, actual_damage_given, actual_damage_taken;
  ProgressDamageTaken / Given: ProgressBarVisible when the actual damage > 0, min 0, max 100, value = the actual
  damage.
- DeathFrameBorderIndex = DeathPanelRoot--BorderNone.

## The line: 180e89ed0 (from the player_death handler)
- Another player's kill: the weapon's econ item (weapon_itemid / fauxitemid) when it has a custom look: its name in
  its rarity colour; else by the event's weapon: prop_exploding_barrel, hegrenade (#SFUI_WPNHUD_HE_Grenade),
  frag_grenade, flashbang, diversion, decoy, smokegrenade, firebomb, incgrenade, molotov, planted_c4 (#CSGO_Type_C4)
  with #Panorama_DeathPanel_Killer1_Weapon ("killed you with the {s:weapon_name}"); inferno: #SFUI_Inferno with
  _Weapon_Plural ("killed you with fire"); stomp_damage: the custom string; anything else
  `#SFUI_WPNHUD_<weapon>` (the raw name when missing) with _Weapon.
- dominated / revenge (the event, 18089c930): #DeathPanel_NewNemesis1 / OldNemesis1 / Revenge1 (not ported).
- No other killer: dangerzone_controller, env_gunfire, prop_exploding_barrel; hegrenade / flashbang / decoy /
  smokegrenade -> #DeathPanel_KilledByOwnGrenade; incgrenade / molotov / inferno -> #DeathPanel_KilledByFire;
  planted_c4 -> #DeathPanel_KilledByC4; else #DeathPanel_KilledSelf. DeathPanel__ItemContainer--Hidden without an item.

## Styles (huddeathpanel.vcss)
- .DeathPanel top centre, flow down, rgba(0,0,0,.5) (world-blur); .DeathPanel__Content 410 wide; avatar 80 box, 66
  image radius 3; health bar 86 x 5 bottom (#dee5c8); name #ccc bold 24; desc #c93121 bold 18 padding-left 8; damage
  label 18 Stratum2 padding 4 10, Taken border-top 2px #25252540; bars 3 tall red / green over #25252550; item 150
  wide, border-left 2px #25252540; DeathPanel--FadeIn 0.3 s linear.

## More traced
- 180e8b640: the avatar (killer's or the local player's), team--CT / team--TERRORIST on the avatar box; a fraction >= 0
  removes DeathPanel__AvatarHealthBar--Hidden and sets the bar's value, < 0 adds it. The .vcss keeps
  .DeathPanel__AvatarHealthBar at visibility: collapse, so the bar never shows.
- The item: the event's weapon_itemid / fauxitemid item view; m_bInitialized (CEconItemView +0x1e8, plVar10[0x3d]) set
  (a default item too) takes "<font color=rarity>item name</font>" with #Panorama_DeathPanel_Killer1_Weapon and shows
  the item's picture; no item (the inferno, the planted bomb) hides DeathPanel__ItemContainer. Rarity colours from
  items_game (default AK uncommon #5e98d9, grenades / knife common #b0c3d9): tools/deathpanel-strings.mjs.
- The nemesis lines: dominated -> #DeathPanel_NewNemesis1, else the killer dominating you (18089c930) ->
  _OldNemesis1, else revenge -> #DeathPanel_Revenge1; FUN_180e8bff0's DominationIconType group (None / Nemesis /
  Revenge) gets 1 (Nemesis) for all three (r15d = 1 at both jumps into 180e8a9b3).

## Still unread
- 180c97a10's state 4 (taken as "dead"); the cvar at 1825510d8 (only gates the bar, which never shows).
