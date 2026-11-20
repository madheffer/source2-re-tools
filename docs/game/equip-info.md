# The top bar's equipment strip (hudteamcounter snippet-equipment-info)

client_20261015. Styles: hudteamcounter-equipmentinfo.vcss.

## Functions

| Address | Module | What |
|---|---|---|
| 180ecd9a0 | client | per avatar: sets SHOW-EQUIPINFO and fills the strip |
| 180769cd0 | client | game_type == 0 (vfn 0x98 of the game type interface 1824c47b8) |
| 180769bb0 | client | game_type 0 and game_mode (vfn 0xa0) 6, 1, 3, 4 or 2 (not casual 0) |
| 1808d9430 | client | the local player is an observer |
| 18076a1e0 | client | m_bWarmupPeriod |
| 180ec8a30 | client | with the local observer: SHOW-EQUIPINFO on the score / clock panel (param_1 +0x68) |
| 180ecec30 | client | the best weapon (outside gun game 180769d90) |
| 180a7f0b0 | client | GetWeaponInSlot (0 rifle, 1 pistol, 2 knife) |
| 180eba820 | client | item def index -> "file://{images}/icons/equipment/%s.svg" of the name less weapon_ |
| 18080ca60 | client | CCSWeaponBaseVData vfn 0x38: `mov eax, [rcx + 0x704]` = m_GearSlotPosition |

## Fields

| Offset | Field |
|---|---|
| DAT_1825651d0 | the game rules |
| player +999 | team |
| C_CSGameRules +0x9b0 | m_eRoundWinReason |
| C_CSGameRules +0x40 | m_bFreezePeriod |
| C_CSGameRules +0x41 | m_bWarmupPeriod |
| pawn vfn 0x4e8 | alive |
| row +0xa4 | money |
| row +0x18 | the best weapon's image path |
| weapon services +0x25e*8 | weapon list |
| weapon vdata +0x700 | slot (3 = grenades) |
| weapon vdata +0x704 | m_GearSlotPosition: HE 0, flashbang 1, smoke 2, decoy 3, molotov / incendiary 4 |

## When it shows (180ecd9a0)

SHOW-EQUIPINFO = game rules exist && 180769cd0 && 180769bb0 && local controller and the player's exist && (1808d9430
|| (same team (+999) && (m_eRoundWinReason != 0 || m_bFreezePeriod || m_bWarmupPeriod || local player not alive))).

## Content (only filled when shown)

- Money `{d:money}` with #buymenu_money; SHRINK-MONEY when the text's length > 6. Health.
- SHOW-WEAPON with the best weapon's image: GetWeaponInSlot(0), else (1), else (2).
- Grenades: each weapon with vdata slot 3 and an econ name sets JsNade-<vfn 0x38 index> to
  `file://{images}/icons/equipment/<name less weapon_>.svg`, the rest cleared; SHOW-NADES off.
- Then SHOW-ARMOR / SHOW-ARMOR-HELMET / SHOW-DEFUSER / SHOW-C4.
- The data is the controllers' networked fields (updates as they reach the client).

## Styles (hudteamcounter-equipmentinfo.vcss)

- .equipinfo-root: opacity 0, translateY(-100px), 0.5 s ease-in-out, full width, ignore-parent-flow, z -10;
  .SHOW-EQUIPINFO: opacity 1, translate 0.
- Container padding-top 86; rows 16 tall, margin 2 0, centred; money 17px (15 SHRINK-MONEY) white; nades 16 x 13.5
  flowing left; armor row flowing right, icons 20 wide (hud/teamcounter/armor(_helmet).svg, icons/ui/defuser_white.svg,
  icons/equipment/c4.svg); dead: deadwhite wash.
- Backdrop equipinfo__bg-container (94 % x 176, 101 dead) with world-blur, bluedots (0.15) and black, both through
  masks/top-bottom-fade-4.

## Unread

- 180ecd9a0's health / armor lines 300-360 in detail.
