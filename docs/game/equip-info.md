# The top bar's equipment strip (hudteamcounter snippet-equipment-info)

client_20261015.dll. Ported in web/src/cs2web/client/hud/equip-info.js (+ teamcounter.js / .css), the server's row in
web/server/cs2web/core/equip-info.js (the board's `eq`) and the phase bits in snapshots.js meRest (`ph`).

## When it shows: 180ecd9a0 (per avatar)
- SHOW-EQUIPINFO = the game rules exist (DAT_1825651d0) and **180769cd0** (game_type == 0: vfn 0x98 of the game type
  interface 1824c47b8) and **180769bb0** (game_type 0 and game_mode (vfn 0xa0) 6, 1, 3, 4 or 2: not casual 0) and
  the local controller and the player's exist, and either **1808d9430** (the local player is an observer) or: the
  same team (+999), and (C_CSGameRules m_eRoundWinReason (+0x9b0) != 0, or m_bFreezePeriod (+0x40), or
  m_bWarmupPeriod (+0x41, 18076a1e0), or the local player not alive (vfn 0x4e8)).
- The same rule (local observer and 180ec8a30) sets SHOW-EQUIPINFO on the score / clock panel (param_1 +0x68).
- Content only filled when shown: money `{d:money}` (row +0xa4) with #buymenu_money, SHRINK-MONEY when the text's
  length > 6; health; SHOW-WEAPON with the image at row +0x18 (the best weapon's path); the grenades: for each weapon
  of the player's pawn's weapon services (+0x25e*8 list) whose vdata slot (+0x700) is 3 (grenades) and has an econ
  name: JsNade-<item vfn 0x38 index> set to `file://{images}/icons/equipment/<name less weapon_>.svg`, the rest
  cleared; SHOW-NADES off; then SHOW-ARMOR / SHOW-ARMOR-HELMET / SHOW-DEFUSER / SHOW-C4.

## Styles (hudteamcounter-equipmentinfo.vcss)
- .equipinfo-root: opacity 0, translateY(-100px), 0.5 s ease-in-out, full width, ignore-parent-flow, z -10;
  .SHOW-EQUIPINFO: opacity 1, translate 0. Container padding-top 86; rows 16 tall, margin 2 0, centred; money 17px
  (15 SHRINK-MONEY) white; nades 16 x 13.5 flowing left; armor row flowing right, icons 20 wide
  (hud/teamcounter/armor(_helmet).svg, icons/ui/defuser_white.svg, icons/equipment/c4.svg); dead: deadwhite wash.

## More traced
- The best weapon (180ecec30, outside gun game 180769d90): the pawn's weapon services' GetWeaponInSlot(0), else (1),
  else (2) (180a7f0b0: rifle, pistol, knife); its item def index -> 180eba820 -> "file://{images}/icons/equipment/%s.svg"
  of the item's name less weapon_.
- The grenades: JsNade-<CCSWeaponBaseVData vfn 0x38> = 18080ca60 `mov eax, [rcx + 0x704]` = m_GearSlotPosition (HE 0,
  flashbang 1, smoke 2, decoy 3, molotov / incendiary 4).
- The backdrop (ported): equipinfo__bg-container (94 % x 176, 101 dead) with world-blur, bluedots (0.15) and black, both
  through masks/top-bottom-fade-4.

## Cadence
- The strip's data rides every snapshot (me.eqp, sent when it changes), as the controllers' networked fields
  reach CS2's clients, not the once-a-second board.

## Still unread
- The health / armor lines 300-360 in detail.
