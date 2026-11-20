# Buying (CanPlayerBuy, buy time, buy zones, the buy command, the buy menu)

server_20261105, client_20261105. pak01 panorama/layout/buymenu.vxml, styles/buymenu.vcss, hudmoney.vxml / .vcss; items_game.txt; game/csgo/cfg; cfg/user_keys_default.vcfg.

## Functions

| Address | Module | What |
|---|---|---|
| 180aba860 | server | CanPlayerBuy(pawn, bPrint) |
| 18092b540 | server | the warmup end (warmup.md) |
| 18017e2d0 | server | f32 compare |
| 18093d470 | server | IsBuyTimeElapsed |
| 180926430 | server | the buy time |
| 18092a140 | server | elapsed = now - m_fRoundStartTime |
| 180c597c0 | server | (skip test with DAT_182125888 vfn 0x98 == 7) |
| 180ca8180 | server | ClientPrint |
| 180913f80 | server | RestartRound (writes m_fRoundStartTime: `lea rsi, [r13 + 0x108]` at 180913fc8) |
| 1809562c0 | server | freeze time (2 in the warmup, else mp_freezetime) |
| 180187770 | server | float cvar value |
| 180a6fba0, 180236640 (x2), 180ade3a0 (x2) | server | other CanPlayerBuy callers (180ade3a0: +use, E opens the buy menu with cl_use_opens_buy_menu, pickups.md) |
| 1802af840 | server | CBuyZone vfn 0x878 PassesTriggerFilters (the base's and a player pawn: vfn 0x558, 0xca8) |
| 1802af7e0 -> 18022f320 | server | CBuyZone vfn 0x888 StartTouch -> add zone (pawn, zone) |
| 1802af700 -> 18022f580 | server | CBuyZone vfn 0x890 EndTouch -> remove zone (pawn, zone) |
| 180957e50, 180958be4 | server | map start: m_bMapHasBuyZone |
| 1809058c0 | server | makes zones at the spawns when none (reads +0x133 at 180906527; unread) |
| 180a7cf90 | server | the buy command (controller, loadout slot, out item, ..., bForTeammate) |
| 180b08430 | server | the team's loadout inventory |
| 18093de70 | server | running match |
| 180ab9620 | server | CanAcquire (ItemServices, mode bForTeammate + 1) |
| 180a6f6f0 | server | buy item_kevlar |
| 180a6ee50 | server | buy item_assaultsuit |
| 180a6f4c0 | server | buy item_defuser (controller) |
| 180b0a920 | server | GetItemPrice (inventory, def index, item) |
| 180a6fc60 | server | money test (controller, price, 1); `#Cstrike_TitlesTXT_Not_Enough_Money` at 180a6ff88 |
| 180b00630 | server | change money |
| 180a4ab40 | server | record the round's purchase |
| 180ab85f0 | server | GiveNamedItem |
| 180c86930 | server | controller's pawn |
| 180c86cd0 | server | team |
| 18093d460 | server | m_bMapHasBombTarget (+0x131) |
| 18093d7b0 | server | hostage map |
| 180ac8960 | server | has defuser |
| 180ac8330 | server | GiveDefuser(services, bPickedUp) |
| 180a6e540 | server | record purchase (controller, def, price, -1, -1, 0) |
| 18024b730 | server | silent test (unread) |
| 180ad71d0 | server | m_bHasDefuser network change |
| 180ae7eb0 | server | (services) after GiveDefuser |
| 18023a540 | server | (pawn) after GiveDefuser (unread) |
| 180a4ab30 | server | (pawn +0xe48, bPickedUp) (unread) |
| 180a7ebb0 | server | (+0xe40) helmet-only price test |
| 1800e3a90 | client | `buymenu` registration ("Show or hide main buy menu") |
| 180ca3f90 | client | open the buy menu |
| 1808da650 | client | buy time not over |
| 18075e0a0 | client | (int) mp_buytime |
| 1808da6a0 | client | in a buy zone |
| 18076b520, 18076b3d0 | client | gates (18076b3d0 branch at 180ca4061: team / gamemode test, unread) |
| 180e87ef0 | client | hint (text, flags) |
| 180dabe70 | client | (this, inZone): false -> close (180da3790) and `#SFUI_BuyMenu_NotInBuyZone` (caller not found) |
| 18010ae70 / 18010aee0 | client | ShowHudHintTextHighPriority / LowPriority registrations |

## Fields

| Offset | Field |
|---|---|
| CCSPlayerPawn +0xf71 | m_bInBuyZone |
| +0xf90 | m_bWasInBuyZone |
| +0xf78 | touched buy zones: CUtlVector of handles (count +0xf78, data +0xf80, alloc +0xf88 / +0xf8c) |
| +0x15a8 | m_bGunGameImmunity |
| +0x1514 | m_ArmorValue |
| +0xb18 | item services (+0x49 has helmet, +0x48 m_bHasDefuser) |
| +0x147c | defuser buy time |
| +0x344 | team |
| CCSGameRules +0xd8 | m_bFreezePeriod |
| +0xd9 | m_bWarmupPeriod |
| +0xe0 | m_fWarmupPeriodStart |
| +0xfc | m_iFreezeTime (int) |
| +0x100 | m_iRoundTime |
| +0x108 | m_fRoundStartTime |
| +0x11c | m_gamePhase |
| +0x131 / +0x133 | m_bMapHasBombTarget / m_bMapHasBuyZone |
| +0xa4c / +0xa4d | m_bTCantBuy / m_bCTCantBuy |
| +0xdc4 | warmup clock running (0: end +inf) |
| CCSWeaponBaseVData +0x70c | m_nPrice |
| +0x700 | slot / loadout type read by the buy |
| item +0x68 | valid |
| controller +0x4c / +0x4e | autobuy / rebuy in progress |
| zone +0x344 | team (`teamnum`) |
| gpGlobals +0x30 | curtime |

## Constants

Cvar value at +0x58 of the handle 8 bytes after the object.

| Cvar | Registered | Object | Read as |
|---|---|---|---|
| mp_buytime | 18009c690 | DAT_1821196f0 | float |
| mp_buy_anywhere | 18009c530 | DAT_18211a6e0 (handle 6e8) | int: 1 anyone, 2 / 3 that team |
| mp_buy_during_immunity | 18009c5e0 | DAT_18211a6f0 (handle 6f8) | int, as mp_buy_anywhere |
| mp_warmup_pausetimer | 1800a4340 | DAT_1821198e8 (handle 8f0) | int |
| mp_warmuptime | 1800a4460 | DAT_1821198a8 | float |
| mp_freezetime | 18009ef00 | DAT_182119ec8 (handle ed0) | int, copied to m_iFreezeTime by 1809562c0 |
| mp_buy_allow_grenades / mp_buy_allow_guns | 18009c3c0 / next | | reader not found |
| DAT_182178728 | | | mp_warmup_items_nocost (by its neighbours, unconfirmed) |

| Value | What |
|---|---|
| 0 bought, 1 already have, 2 can't afford, 3 not allowed, 4 / 5 / 6 invalid | BuyResult |
| 3.0 | no buying in the warmup's last 3 s |
| 4 halftime, 5 match ended | m_gamePhase blocking buys |
| 4 = HUD_PRINTCENTER | ClientPrint type |
| 0xc | item def for slot -2 with a cvar |
| 100 | full armor |
| 1000 - 650 = 350 | assaultsuit price with full armor and no helmet |
| 0x181e0f2c8 | cached item_defuser definition (schema vfn 0x148) |
| 0x182 | 180b61d70 arg (damage-prediction.md) |

## CanPlayerBuy (180aba860)

1. Gamerules exist; pawn vfn 0x550 (alive); `mp_buy_anywhere == 1 || mp_buy_anywhere == team || m_bInBuyZone`; else false, nothing printed.
2. m_bWarmupPeriod: warmup end (18092b540: +inf when +0xdc4 is 0; 0 when the clock doesn't run (DAT_1821ba010 vfn 0x110 false and DAT_182119380 / DAT_182119738 off); else m_fWarmupPeriodStart + mp_warmuptime) + 3.0 compares -1 against the controller's time: false.
3. `m_gamePhase - 4 <= 1`: false, nothing printed.
4. m_bCTCantBuy and team 3: `#Cstrike_TitlesTXT_CT_cant_buy`; m_bTCantBuy and team 2: `#Cstrike_TitlesTXT_Terrorist_cant_buy` (when bPrint); false.
5. `mp_buy_during_immunity == 1 || == team`: ok = m_bGunGameImmunity; else ok = !IsBuyTimeElapsed. ok: true. Else with bPrint: `V_snprintf(buf, 16, "%d", (int)buytime)`, ClientPrint(pawn, 4, `#Cstrike_TitlesTXT_Cant_buy`, buf); false.

## IsBuyTimeElapsed (18093d470), buy time (180926430)

- Warmup with DAT_18218bff8 vfn 0x100 true or mp_warmup_pausetimer != 0: never elapsed.
- Else `buytime < elapsed`; elapsed = now - m_fRoundStartTime (skipped while DAT_182125888 vfn 0x98 == 7, or the warmup); buytime: in the warmup its length or end; outside, mp_buytime (also the warmup branch's fallback when mp_buytime >= the warmup end).
- m_fRoundStartTime = now + m_iFreezeTime (RestartRound): the buy time runs from the freeze time's end (Wingman 10 s freeze + mp_buytime 20 s).

## Buy zones

- CBuyZone vtable 0x1817a93a0 (CBaseTrigger 0x1817cc140).
- 18022f320 appends the zone handle; m_bInBuyZone = any listed zone with team 0 or the pawn's. 18022f580 removes and recomputes.
- Map start: m_bMapHasBuyZone = FindEntityByClassname("func_buyzone") != null. de_dust2 has two (teamnum 2 and 3).

## The buy command (180a7cf90)

1. CanPlayerBuy(pawn, 1) or 3. Slot -1: 5.
2. Item from the team's loadout (slot -2 with a cvar: def 0xc); none or invalid: 5. Running match outside warmup with team not 2 / 3: 3.
3. CanAcquire: 0 go on; 2 / 4 / 5 (already owned, grenade type limit, total limit): `#Cstrike_TitlesTXT_Cannot_Carry_Anymore` (center; not during autobuy / rebuy) and 1; else 4.
4. item_kevlar / item_assaultsuit / item_defuser -> their functions (return their result); else:
5. price = GetItemPrice; money test or 2; money -price; purchase recorded; GiveNamedItem (a teammate's buy drops it between the two).

- **item_kevlar**: armor < 100: money test (2); with a helmet `#Cstrike_TitlesTXT_Already_Have_Helmet_Bought_Kevlar`; item_pickup ("vest"), Player.PickupWeapon, armor 100. At 100: `#Cstrike_TitlesTXT_Already_Have_Kevlar` (180a6f7c8), 1.
- **item_assaultsuit**: money test first (2); helmet already: `#Cstrike_TitlesTXT_Already_Have_Kevlar_Helmet`, 1; armor >= 100 without: `#Cstrike_TitlesTXT_Already_Have_Kevlar_Bought_Helmet` and the buy goes on; item_pickup ("vesthelm"), Player.PickupWeapon, helmet and armor, -price.
- **item_defuser**: no pawn 6; no pawn +0x38 3; price = GetItemPrice(the cached def); team 3 and m_bMapHasBombTarget, or a hostage map, else 4; has defuser: `#Cstrike_TitlesTXT_Already_Have_One` (type 4, not during autobuy / rebuy) and 1; money test (2); GiveDefuser(services, 0); money -price (reason "item_defuser", "item_cutters" on a hostage map); 180a6e540; 0.
- **GiveDefuser** (180ac8330): not held: item_pickup (userid, item "defuser", silent = 18024b730(pawn), defindex) and, not silent, Player.PickupWeapon; m_bHasDefuser = 1 (180ad71d0), 180ae7eb0(services); bPickedUp false: pawn +0x147c = curtime; 18023a540(pawn); 180a4ab30(pawn +0xe48, bPickedUp).
- **GetItemPrice**: vdata m_nPrice; 0 in the warmup with DAT_182178728; item_assaultsuit with armor >= 100 and no helmet (or 180a7ebb0 on +0xe40 true): its price - item_kevlar's.

## Client: buymenu and hints

- user_keys_default.vcfg binds "b" "buymenu".
- 180ca3f90, after its gates (a global's vfn 0x150 / 0x170, the local pawn's vfns 0x4f0 / 0xab8 / 0x4e8, 18076b520 on a cvar): buy time over: `ebx = (int) mp_buytime`, "%d", `#SFUI_BuyMenu_YoureOutOfTime` when 0, else `#SFUI_BuyMenu_OutOfTime` with %s1; 180e87ef0(text, 1). Else not in a zone: 180e87ef0(`#SFUI_BuyMenu_NotInBuyZone`, 1). Else the menu opens (a panel event).
- 180e87ef0(text, flags): panorama event; flags & 2 `ShowHudHintTextHighPriority`, else `ShowHudHintTextLowPriority` ("Display the string in the center of the hud."; params "utf8 message string", "time").

## Buy menu layout (buymenu.vxml / .vcss)

- CSGOBuyMenu (C++): five category containers: ccequip (18 %), ccpistols (18 %), ccmidtier (22 %), ccrifles (24 %), ccgrenades (18 %); 950 px wide, 180 px down.
- Item: 90 px button-container (key, name, icon 45 % tall, price, current value); states buywheel-cant-buy / -cant-afford / -already-own.
- buymenu-info: money, `#BuyMenu_TimerText` "Buy Time Remaining" + CountdownTimer {t:d:duration}, `#BuyMenu_MinMoneyNextRound`.
- Navbar: Re-Buy (rebuy), Auto Buy (autobuy), Refund All (sellbackall), Back. Category key labels from C++ ({s:buymenu-category-key}).
- hudmoney: `.money-text-buy-icon` (icons/ui/buyzone.vsvg, 30 x 30, wash lightgreen) opacity 0, 1 with `money__in-buy-zone` (set by CSGOMoneyPanel, unread).

## Default loadout (items_game.txt, flexible_loadout_default 1)

| Slot | 0 | 1 | 2 | 3 | 4 |
|---|---|---|---|---|---|
| secondary | P2000 / Glock-18 | Dual Berettas | P250 | Five-SeveN / Tec-9 | Desert Eagle |
| smg | Nova | XM1014 | MP5-SD | P90 | MP9 / MAC-10 |
| rifle | FAMAS / Galil AR | M4A1-S / AK-47 | SSG 08 | AUG / SG 553 | AWP |
| equipment | Kevlar Vest | Kevlar & Helmet | Zeus x27 | Defuse Kit (CT) | |
| grenade | Flashbang | Smoke | HE | Incendiary / Molotov | Decoy |

## Mode cvars (game/csgo/cfg)

- gamemode_competitive2v2.cfg / gamemode_competitive.cfg: mp_buytime 20, mp_buy_anywhere 0, mp_buy_during_immunity 0, mp_respawn_immunitytime -1.
- gamemode_deathmatch.cfg: mp_buytime 0, mp_buy_anywhere 1, mp_buy_during_immunity 1, mp_respawn_immunitytime 10, mp_buy_allow_grenades 0.

## Unread

- CanAcquire's ladder (180ab9620: per-round purchase counts, ownership by definition, team / map / mode answers, where mp_buy_allow_* are read).
- The warmup's buy clock in full (18092a140's other branches).
- 1809058c0's spawn buy zones.
- 18024b730's silent test, 180a4ab30, 18023a540.
- 180a6fc60's body.
- CSGOBuyMenu's C++ (columns, keys, the purchase-failure label's text, closing at the buy time's end); the hint's hold time; 18076b3d0's branch.
