# Buying: CanPlayerBuy, the buy time, buy zones, the buy command, the buy menu

server_20261105.dll and client_20261105.dll (archived in tools/re/binaries), 2026-11-15. Ported in web/src/cs2web/modes/team/buy-items.js (the
shared rules), web/server/cs2web/modes/team/cs2-buy.js (the server), web/src/cs2web/client/modes/team/buy-menu.js (the menu); buy-test.mjs checks it.

## Fields (tools/re/game/schema.py)

| Class | Field | Offset |
|---|---|---|
| CCSPlayerPawn | m_bInBuyZone | 0xf71 |
| CCSPlayerPawn | m_bWasInBuyZone | 0xf90 |
| CCSPlayerPawn | (the touched buy zones: CUtlVector of handles: count +0xf78, data +0xf80, alloc +0xf88 / +0xf8c) | 0xf78 |
| CCSPlayerPawn | m_bGunGameImmunity | 0x15a8 |
| CCSPlayerPawn | m_ArmorValue (read as armor) | 0x1514 |
| CCSPlayerPawn | item services (+0x49: has helmet) | 0xb18 |
| CCSGameRules | m_bFreezePeriod | 0xd8 |
| CCSGameRules | m_bWarmupPeriod | 0xd9 |
| CCSGameRules | m_fWarmupPeriodStart (GameTime) | 0xe0 |
| CCSGameRules | m_iFreezeTime (int) | 0xfc |
| CCSGameRules | m_iRoundTime | 0x100 |
| CCSGameRules | m_fRoundStartTime (float) | 0x108 |
| CCSGameRules | m_gamePhase | 0x11c |
| CCSGameRules | m_bMapHasBombTarget / m_bMapHasBuyZone | 0x131 / 0x133 |
| CCSGameRules | m_bTCantBuy / m_bCTCantBuy | 0xa4c / 0xa4d |
| CCSGameRules | (warmup clock running: 0 -> the warmup end is +inf) | 0xdc4 |
| CCSWeaponBaseVData | m_nPrice | 0x70c |
| CCSWeaponBaseVData | (BuyResult slot / loadout type read by the buy) | 0x700 |

## Cvars (their registration's global; the value is at +0x58 of the handle 8 bytes after it)

| Cvar | Registered in | Object | Read as |
|---|---|---|---|
| mp_buytime | 18009c690 | DAT_1821196f0 | float, FUN_180187770(&obj) |
| mp_buy_anywhere | 18009c530 | DAT_18211a6e0 (handle 6e8) | int: 1 anyone, 2 / 3 that team |
| mp_buy_during_immunity | 18009c5e0 | DAT_18211a6f0 (handle 6f8) | int, as mp_buy_anywhere |
| mp_warmup_pausetimer | 1800a4340 | DAT_1821198e8 (handle 8f0) | int |
| mp_warmuptime | 1800a4460 | DAT_1821198a8 | float |
| mp_freezetime | 18009ef00 | DAT_182119ec8 (handle ed0) | int, copied to m_iFreezeTime by 1809562c0 (2 in the warmup) |
| mp_buy_allow_grenades / mp_buy_allow_guns | 18009c3c0 / (next) | | registered; their reader not found yet |

## CanPlayerBuy (180aba860: pawn, bPrint)

1. CCSGameRules exists; pawn vfn 0x550 (alive) true; and `mp_buy_anywhere == 1 || mp_buy_anywhere == team(+0x344) ||
   m_bInBuyZone` — else false, nothing printed.
2. m_bWarmupPeriod: if the warmup end (18092b540: +inf when +0xdc4 is 0; 0 when the warmup clock doesn't run — vfn
   0x110 of DAT_1821ba010 false and DAT_182119380 / DAT_182119738 off; else m_fWarmupPeriodStart + mp_warmuptime) + 3.0
   compares -1 against the controller's time (18017e2d0): false (no buying in the warmup's last 3 s).
3. m_gamePhase - 4 <= 1 (4 halftime, 5 match ended): false, nothing printed.
4. m_bCTCantBuy and team 3: print `#Cstrike_TitlesTXT_CT_cant_buy`; m_bTCantBuy and team 2:
   `#Cstrike_TitlesTXT_Terrorist_cant_buy` (when bPrint); false.
5. buytime = mp_buytime (float). If mp_buy_during_immunity == 1 or == team: ok = m_bGunGameImmunity; else ok =
   !IsBuyTimeElapsed (18093d470). ok: true. Else with bPrint: V_snprintf(buf, 16, "%d", (int)buytime) and
   ClientPrint(pawn, 4 = HUD_PRINTCENTER, `#Cstrike_TitlesTXT_Cant_buy`, buf) (180ca8180); false.

Callers: the buy command 180a7cf90 (bPrint 1), 180a6fba0, 180236640 (x2), the +use code 180ade3a0 (x2: E opens the
buy menu with cl_use_opens_buy_menu, pickups.md).

## IsBuyTimeElapsed (18093d470) and the buy time (180926430)

- In the warmup (+0xd9) with vfn 0x100 of DAT_18218bff8 true or mp_warmup_pausetimer != 0: never elapsed.
- Else `buytime < elapsed`, elapsed = 18092a140 = now - m_fRoundStartTime (+0x108; skipped while vfn 0x98 of
  DAT_182125888 == 7, 180c597c0, or the warmup) and buytime = 180926430: in the warmup the warmup's length or its
  end; outside, mp_buytime (whose value the warmup branch also falls back to when mp_buytime >= the warmup end).
- m_fRoundStartTime is written by RestartRound (180913f80, `lea rsi, [r13 + 0x108]` at 180913fc8): now + m_iFreezeTime
  (1809562c0: 2 in the warmup, else mp_freezetime). So the buy time runs from the freeze time's end: the freeze time
  (10 s in Wingman) plus mp_buytime (20 s).

## Buy zones

- CBuyZone vtable 0x1817a93a0 (CBaseTrigger 0x1817cc140), overrides (vdiff): 0x878 PassesTriggerFilters 1802af840
  (the base's and a player pawn: vfn 0x558, 0xca8), 0x888 StartTouch 1802af7e0 -> 18022f320(pawn, zone), 0x890
  EndTouch 1802af700 -> 18022f580(pawn, zone).
- 18022f320 appends the zone's handle to the pawn's list (+0xf78/+0xf80) and sets m_bInBuyZone = any listed zone whose
  team (zone +0x344, the `teamnum` keyvalue) is 0 or the pawn's team. 18022f580 removes it and recomputes.
- At map start (180957e50, 180958be4): m_bMapHasBuyZone = FindEntityByClassname("func_buyzone") != null. With none,
  1809058c0 (reads +0x133 at 180906527) makes zones at the spawns — unread; de_dust2 has two (teamnum 2 and 3).

## The buy command (180a7cf90: controller, loadout slot, out item, ..., bForTeammate)

Returns CS2's BuyResult: 0 bought, 1 already have, 2 can't afford, 3 not allowed, 4 / 5 / 6 invalid.

1. CanPlayerBuy(pawn, 1) or 3. Slot -1: 5.
2. The item from the team's loadout (the inventory 180b08430 for the controller's team; slot -2 with a cvar: item
   def 0xc); none or not valid (+0x68): 5. In a running match (18093de70) outside the warmup with the team not 2 / 3: 3.
3. CanAcquire (ItemServices 180ab9620, mode bForTeammate + 1): 0 go on; 2 / 4 / 5 (already owned, the grenade type
   limit, the total limit): `#Cstrike_TitlesTXT_Cannot_Carry_Anymore` (center; not with controller +0x4c / +0x4e set:
   autobuy / rebuy in progress) and 1; anything else 4.
4. item_kevlar -> 180a6f6f0, item_assaultsuit -> 180a6ee50, item_defuser -> 180a6f4c0 (each returns the result);
   anything else 5 = "buy it":
5. price = GetItemPrice (180b0a920); 180a6fc60(controller, price, 1) (the money test, its line
   `#Cstrike_TitlesTXT_Not_Enough_Money` at 180a6ff88) or 2; the money changed by -price (180b00630); the round's
   purchase recorded (180a4ab40); GiveNamedItem (180ab85f0; a teammate's buy drops it between the two).

- item_kevlar (180a6f6f0): armor (+0x1514) < 100: money test (2), with a helmet already
  `#Cstrike_TitlesTXT_Already_Have_Helmet_Bought_Kevlar`, item_pickup event ("vest"), Player.PickupWeapon, armor 100.
  At 100: `#Cstrike_TitlesTXT_Already_Have_Kevlar` (180a6f7c8), 1.
- item_assaultsuit (180a6ee50): the money test first (2); a helmet already: `..._Already_Have_Kevlar_Helmet`, 1; armor
  >= 100 without one: `..._Already_Have_Kevlar_Bought_Helmet` and the buy goes on; item_pickup ("vesthelm"),
  Player.PickupWeapon, the helmet and armor, -price.
- item_defuser (180a6f4c0, controller): no pawn (180c86930) 6; no pawn +0x38 3; price = GetItemPrice(item_defuser's
  def, the definition cached at 0x181e0f2c8 by the schema's vfn 0x148 "item_defuser"); the team (180c86cd0) 3 and
  the gamerules' m_bMapHasBombTarget (18093d460: +0x131), or a hostage map (18093d7b0), else 4; the item services'
  (pawn +0xb18) has-defuser (180ac8960) true: `#Cstrike_TitlesTXT_Already_Have_One` (180ca8180 type 4, not while
  autobuy / rebuy +0x4c / +0x4e) and 1; the money test 180a6fc60 (2); GiveDefuser 180ac8330(services, 0); the
  money -price (180b00630, its reason string "item_defuser", "item_cutters" on a hostage map); the purchase
  recorded (180a6e540(controller, def, price, -1, -1, 0)); 0.
- GiveDefuser 180ac8330(services, bPickedUp): not held (+0x48 false): the item_pickup event (userid, item "defuser",
  silent = 18024b730(pawn), defindex) and, not silent, Player.PickupWeapon on the pawn; then m_bHasDefuser (+0x48) = 1
  (its network change 180ad71d0), 180ae7eb0(services); bPickedUp false: pawn +0x147c = the globals' +0x30 (the curtime:
  the buy's time); 18023a540(pawn); 180a4ab30(pawn +0xe48, bPickedUp).
- GetItemPrice (180b0a920: inventory, def index, item): the vdata's m_nPrice (+0x70c); 0 in the warmup with cvar
  DAT_182178728 (mp_warmup_items_nocost, by its neighbours: unconfirmed); item_assaultsuit with armor >= 100 and no
  helmet (or 180a7ebb0 on +0xe40 true): its price - item_kevlar's (1000 - 650 = 350).

## The client: B (buymenu) and the hint lines

- `buymenu` is registered at 1800e3a90 ("Show or hide main buy menu"); user_keys_default.vcfg binds "b" "buymenu".
- 180ca3f90 (opening it), after its gates (vfn 0x150 / 0x170 of a global, the local pawn's vfns 0x4f0 / 0xab8 /
  0x4e8, 18076b520 on a cvar): if the buy time is over (1808da650 false): ebx = (int) mp_buytime (18075e0a0), "%d",
  `#SFUI_BuyMenu_YoureOutOfTime` when it is 0, else `#SFUI_BuyMenu_OutOfTime` with %s1; then 180e87ef0(text, 1).
  Else not in a buy zone (1808da6a0 false): 180e87ef0(`#SFUI_BuyMenu_NotInBuyZone`, 1). Else the menu opens (a panel
  event). Unread: the 18076b3d0 branch at 180ca4061 (the team / gamemode test before the time check).
- 180dabe70(this, inZone): inZone false -> close the buy menu (180da3790) and 180e87ef0(`#SFUI_BuyMenu_NotInBuyZone`, 1).
  Its caller isn't found (assumed the buy menu's own zone watch).
- 180e87ef0(text, flags): a panorama event with the string: flags & 2 `ShowHudHintTextHighPriority`, else
  `ShowHudHintTextLowPriority` (registered 18010ae70 / 18010aee0, "Display the string in the center of the hud.";
  their parameters "utf8 message string" and "time"). The hold time is the event's; unread.

## The buy menu's layout (pak01 panorama/layout/buymenu.vxml, styles/buymenu.vcss; lasers-bake --panorama)

CSGOBuyMenu (C++): five category containers in this order: ccequip (18 %), ccpistols (18 %), ccmidtier (22 %),
ccrifles (24 %), ccgrenades (18 %), 950 px wide, 180 px down; each item a 90 px button-container (key, name, icon
45 % tall, price, current value), states buywheel-cant-buy / -cant-afford / -already-own; buymenu-info above (money,
`#BuyMenu_TimerText` "Buy Time Remaining" and a CountdownTimer {t:d:duration}, `#BuyMenu_MinMoneyNextRound`); the
navbar: Re-Buy (rebuy), Auto Buy (autobuy), Refund All (sellbackall), Back. The order and labels the C++ gives the
columns aren't read (category key labels come from it: {s:buymenu-category-key}).

The default loadout (items_game.txt, base items with flexible_loadout_default 1, used_by_classes):
secondary0 P2000 / Glock-18, 1 Dual Berettas, 2 P250, 3 Five-SeveN / Tec-9, 4 Desert Eagle; smg0 Nova, 1 XM1014,
2 MP5-SD, 3 P90, 4 MP9 / MAC-10; rifle0 FAMAS / Galil AR, 1 M4A1-S / AK-47, 2 SSG 08, 3 AUG / SG 553, 4 AWP;
equipment0 Kevlar Vest, 1 Kevlar & Helmet, 2 Zeus x27, 3 Defuse Kit (CT); grenade0 Flashbang, 1 Smoke, 2 HE,
3 Incendiary / Molotov, 4 Decoy.

hudmoney.vxml / .vcss: `.money-text-buy-icon` (icons/ui/buyzone.vsvg, 30 x 30, wash lightgreen) at opacity 0, 1 with
`money__in-buy-zone`; who sets that class (CSGOMoneyPanel) is unread.

## Mode cvars (game/csgo/cfg)

gamemode_competitive2v2.cfg / gamemode_competitive.cfg: mp_buytime 20, mp_buy_anywhere 0, mp_buy_during_immunity 0,
mp_respawn_immunitytime -1. gamemode_deathmatch.cfg: mp_buytime 0, mp_buy_anywhere 1, mp_buy_during_immunity 1,
mp_respawn_immunitytime 10, mp_buy_allow_grenades 0.

## Still unread

CanAcquire's whole ladder (180ab9620: the per-round purchase counts, ownership by definition, team / map / mode
answers, where mp_buy_allow_* are read); the warmup's buy clock in full (18092a140's other branches); 1809058c0's
spawn buy zones; the defuse kit's item_pickup event / Player.PickupWeapon (not sent: a server event and sound for
it; 18024b730's silent test, 180a4ab30, 18023a540 unread); 180a6fc60's body; CSGOBuyMenu's C++ (columns, keys, the purchase-failure
label's text, closing at the buy time's end); the hint's hold time.
