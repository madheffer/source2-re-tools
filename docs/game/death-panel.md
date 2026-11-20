# The death panel ("killed by")

client_20261015 (Ghidra), server_20261105. huddeathpanel.vcss, cstrike15_usermessages.proto.

## Functions

| Address | Module | What |
|---|---|---|
| 180c8d8c0 | client | CCSUsrMsg_SendLastKillerDamageToClient handler -> 180e8e3c0 |
| 180e8e3c0 | client | store (panel, damage_taken, hits_taken, damage_given, hits_given, actual_given, actual_taken), then show / hide |
| 180c97a10 | client | local player's state (4 taken as "dead") |
| 180e8aaf0 | client | show the panel |
| 180e877b0 | client | hide the panel |
| 1804ffb20 / 1804ffd30 | client | a replay runs (a shown panel stays) |
| 180e8d660 | client | disarm + show / hide rule (from 180c76830) |
| 180e97430 | client | the same (the respawn hides it) |
| 180e8f3a0 | client | (1): DeathPanel--Hidden off, DeathPanel--FadeIn re-triggered |
| 180e8f4c0 | client | (0): the screenshot panel off |
| 180e8b640 | client | avatar + health bar (panel, killer, fraction) |
| 180e8bbd0 | client | the damage rows |
| 180e89ed0 | client | the "killed by" line (from the player_death handler) |
| 18089c930 | client | the killer dominates you |
| 180e8bff0 | client | DominationIconType group (None / Nemesis / Revenge) |
| 180b21fd0 | server | sender, on the lethal hit (180a94520) with the victim's +0x800 services and the attacker |
| 1807ad580 | server | builds the message; sent through 1821b9498 vfn 0x78 |

## Fields

| Offset | Field |
|---|---|
| message +0x48 .. +0x5c | the six fields in order (int32) |
| panel +0x1a8 / +0x1ac / +0x1b0 / +0x1b4 / +0x1b8 / +0x1bc | damage_taken, hits_taken, damage_given, hits_given, actual_given, actual_taken |
| panel +0x1c0 | armed (1) |
| panel +0x1a0 | shown (1) |
| game state +0x84 | not 5 to show |
| controller +0x1ed4 | the local player's killer (-> m_hPawn) |
| pawn +0x34c | health |
| record +0x6c / +0x64 / +0x68 | num_hits / damage ((int)) / actual damage ((int)), server's damage records |
| CEconItemView +0x1e8 | m_bInitialized (decompiler plVar10[0x3d]) |
| 1825510d8 | cvar: when set, health fraction forced -1 (only gates the bar) |

## Message fields (CCSUsrMsg_SendLastKillerDamageToClient)

1 num_hits_given, 2 damage_given, 3 num_hits_taken, 4 damage_taken, 5 actual_damage_given, 6 actual_damage_taken (int32).
Server: of the victim's records, victim -> killer gives the given ones, killer -> victim the taken ones.

## Handler (180e8e3c0)

1. Store the six, +0x1c0 = 1.
2. Local state (180c97a10) 4 and game state (+0x84) != 5: show (180e8aaf0) if not shown.
3. Else disarm; a shown panel hides (180e877b0) unless a replay runs.

## Showing (180e8aaf0)

1. DeathPanelRoot--Hidden off, +0x1a0 = 1; 180e8f3a0(1); 180e8f4c0(0); DeathCancel--Hidden on.
2. Killer: controller +0x1ed4 -> m_hPawn, its controller; killer_playerslot for the name label.
3. Health fraction `max(health +0x34c, 0) / max health (vfn 0x550)`; -1 when cvar 1825510d8 set; 0 when not alive (vfn 0x4e8); 180e8b640(panel, killer, fraction).
4. 180e8bbd0: DeathPanel__Damage--Hidden on the Taken row when damage_taken == 0, the Given row when damage_given == 0;
   dialog variables hits_taken, damage_taken, hits_given, damage_given, actual_damage_given, actual_damage_taken;
   ProgressDamageTaken / Given: ProgressBarVisible when actual damage > 0, min 0, max 100, value = actual damage.
5. DeathFrameBorderIndex = DeathPanelRoot--BorderNone.

## Avatar (180e8b640)

- Killer's or the local player's avatar; team--CT / team--TERRORIST on the avatar box.
- Fraction >= 0 removes DeathPanel__AvatarHealthBar--Hidden and sets the value; < 0 adds it.
- The .vcss keeps .DeathPanel__AvatarHealthBar at visibility: collapse: the bar never shows.

## The line (180e89ed0)

- Item: the event's weapon_itemid / fauxitemid item view; m_bInitialized set (a default item too): "<font color=rarity>item name</font>"
  with #Panorama_DeathPanel_Killer1_Weapon, and the item's picture. No item (inferno, planted bomb): DeathPanel__ItemContainer--Hidden.
- Rarity colours from items_game (default AK uncommon #5e98d9, grenades / knife common #b0c3d9).
- Else by the event's weapon, with #Panorama_DeathPanel_Killer1_Weapon ("killed you with the {s:weapon_name}"):
  prop_exploding_barrel, hegrenade (#SFUI_WPNHUD_HE_Grenade), frag_grenade, flashbang, diversion, decoy, smokegrenade,
  firebomb, incgrenade, molotov, planted_c4 (#CSGO_Type_C4).
- inferno: #SFUI_Inferno with _Weapon_Plural ("killed you with fire"); stomp_damage: the custom string; anything else
  `#SFUI_WPNHUD_<weapon>` (raw name when missing) with _Weapon.
- Nemesis: dominated -> #DeathPanel_NewNemesis1, else killer dominating you (18089c930) -> _OldNemesis1, else revenge ->
  #DeathPanel_Revenge1. 180e8bff0's DominationIconType gets 1 (Nemesis) for all three (r15d = 1 at both jumps into 180e8a9b3).
- No other killer: dangerzone_controller, env_gunfire, prop_exploding_barrel; hegrenade / flashbang / decoy / smokegrenade
  -> #DeathPanel_KilledByOwnGrenade; incgrenade / molotov / inferno -> #DeathPanel_KilledByFire; planted_c4 ->
  #DeathPanel_KilledByC4; else #DeathPanel_KilledSelf.

## Styles (huddeathpanel.vcss)

- .DeathPanel top centre, flow down, rgba(0,0,0,.5) (world-blur); .DeathPanel__Content 410 wide.
- Avatar 80 box, 66 image radius 3; health bar 86 x 5 bottom (#dee5c8).
- Name #ccc bold 24; desc #c93121 bold 18 padding-left 8.
- Damage label 18 Stratum2 padding 4 10; Taken border-top 2px #25252540; bars 3 tall red / green over #25252550.
- Item 150 wide, border-left 2px #25252540. DeathPanel--FadeIn 0.3 s linear.

## Unread

- 180c97a10's state 4 (taken as "dead"); the cvar at 1825510d8.
