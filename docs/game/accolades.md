# End-of-match accolades

server_20261105. The nomination each end-of-match stats card shows (player_stats_card.vts SetAccolade: `#accolade_<name>` and `_desc`, `_2` for second place; endofmatch-characters.vts reads allplayerdata[].nomination { eaccolade, value, position }). GoToIntermission (18092cdf0) runs the selection for team 3 then team 2 (one pass for everyone in Arms Race / deathmatch): [intermission.md](intermission.md).

## Functions

| Address | Module | What |
|---|---|---|
| 18092cdf0 | server | GoToIntermission |
| 18004d160 | server | static initializer of the table (and the 41 beside it) |
| 1801bdd00 | server | the selection (players, team) |
| 1813aa290 | server | controller's slot |
| 1801c7300 | server | the player's record list by slot |
| 1801d3440 | server | the score's curve (index, group, c, 0, 0.1) (unread) |
| 1801bdcb0 | server | sort a player's list by score (unread) |
| 180928950 | server | game-rules value in the score (unread) |
| 1801be680 | server | writes { id, value, position } into the player's EndOfMatchAllPlayersData entry; logs "ACCOLADE, FINAL: {name}, player<slot>, VALUE: v, POS: p, SCORE: s" |
| 180b079b0 | server | (action tracking): the ADR (unread) |
| 180b07d50 | server | (action tracking): the headshot % (unread) |
| 180a7a8e0 | server | (controller): MVPs (unread) |
| 18093df90 | server | killreward gate (with a cvar) |

## The table

Entry = 0x181f57380 + id x 0x28: `{ +0 int id, +8 value fn(controller, edx), +0x10 int flags, +0x14 int group, +0x18 float c, +0x1c float d, +0x20 const char *name }`. ids 1..10 are the "gimme_01".."gimme_10" fallbacks (no value function). Offsets in the value column are on the action tracking services unless noted.

| id | name | fn | flags | group | c | d | value |
|---|---|---|---|---|---|---|---|
| 11 | kills | 1801cfed0 | 6 | 1 | 0.02 | 1 | +0xf8 m_matchStats.m_iKills |
| 12 | damage | 1801cfd40 | 6 | 1 | 2 | 100 | +0x104 m_iDamage |
| 13 | adr | 1801cfbe0 | 4 | 1 | 2 | 100 | 180b079b0(action tracking) |
| 14 | mvps | 1801cff50 | 2 | 1 | 0 | 1 | edx <= 1: 0; else 180a7a8e0(controller) |
| 15 | assists | 1801cfbf0 | 6 | 2 | 0.02 | 1 | +0x100 m_iAssists |
| 16 | hsp | 1801cfe00 | 0 | 2 | 10 | 100 | 180b07d50(action tracking) |
| 17 | 3k | 1801cfb80 | 0 | 1 | 0 | 3 | edx <= 1: 0; else +0x138 m_iEnemy3Ks |
| 18 | 4k | 1801cfba0 | 0 | 1 | 0 | 2 | edx <= 1: 0; else +0x134 m_iEnemy4Ks |
| 19 | 5k | 1801cfbc0 | 0 | 1 | 0 | 2 | edx <= 1: 0; else +0x130 m_iEnemy5Ks |
| 20 | headshotkills | 1801cfde0 | 6 | 1 | 0.02 | 1 | +0x118 m_iHeadShotKills |
| 21 | killreward | 1801cfe10 | 6 | 2 | 2 | 200 | 0 in queued matchmaking ("Q"), unless 18093df90 and a cvar (handle 0x181f... + 0x58) != 3; else +0x110 m_iKillReward |
| 22 | utilitydamage | 1801d0110 | 6 | 2 | 1 | 10 | +0x124 m_iUtilityDamage |
| 23 | enemiesflashed | 1801cfda0 | 6 | 2 | 0.02 | 1 | +0x128 m_iEnemiesFlashed |
| 24 | objective | 1801d0040 | 2 | 2 | 0.1 | 1 | edx <= 1: 0; else +0x11c m_iObjective |
| 25 | score | 1801d00a0 | 6 | 2 | 0.2 | 3 | controller +0x91c m_iScore |
| 26 | livetime | 1801cff30 | 2 | 3 | 30 | 180 | +0x114 m_iLiveTime |
| 27 | deaths | 1801cfd60 | 2 | 3 | 0.85 | 1 | +0xfc m_iDeaths |
| 28 | nopurchasewins | 1801cff80 | 2 | 2 | 0.15 | 1 | gated as killreward; +0x3c4 |
| 29 | clutchkills | 1801cfd20 | 6 | 2 | 0.02 | 1 | edx <= 1: 0; else +0x3d0 |
| 30 | pistolkills | 1801d0060 | 6 | 2 | 0.01 | 0.5 | +0x3d4 |
| 31 | firstkills | 1801cfdc0 | 2 | 2 | 0.1 | 1 | edx <= 1: 0; else +0x3cc |
| 32 | sniperkills | 1801d00b0 | 6 | 2 | 0.02 | 0.4 | +0x3d8 |
| 33 | roundssurvived | 1801d0080 | 2 | 2 | 0.1 | 1 | edx <= 1: 0; else +0x3b8 |
| 34 | chickenskilled | 1801cfd00 | 2 | 3 | 0.1 | 1 | +0x2a8 m_numChickensKilled |
| 35 | killswhileblind | 1801cfef0 | 6 | 3 | 0.02 | 0.06 | +0x2ac m_killsWhileBlind |
| 36 | bombcarrierkills | 1801cfc10 | 6 | 2 | 0.01 | 1 | +0x2b0 m_bombCarrierkills |
| 37 | burndamage | 1801cfc30 | 6 | 2 | 0.13 | 1.3 | +0x2b4 m_flBurnDamageInflicted (float) |
| 38 | cashspent | 1801cfc40 | 2 | 3 | 1000 | 8000 | gated as killreward; controller +0x7e8 (in-game money services) +0x50 |
| 39 | uniqueweaponkills | 1801d00f0 | 0 | 2 | 2 | 6 | +0x410 |
| 40 | dinks | 1801cfd80 | 6 | 2 | 0.018 | 1 | +0x1ac (the round block's m_iDinks: +0x198 + 0x14) |
| 41 | knifekills | 1801cff10 | 0 | 1 | 0 | 3 | +0x13c m_iEnemyKnifeKills |
| 42 | taserkills | 1801d00d0 | 0 | 1 | 0 | 3 | +0x140 m_iEnemyTaserKills |

## Fields

| Offset | Field |
|---|---|
| controller +0x7f8 | action tracking services |
| controller +0x7e8 | in-game money services (+0x50 cash spent) |
| controller +0x91c | m_iScore |
| action tracking +0x40 | m_perRoundStats |
| action tracking +0xc8 | m_matchStats (CSMatchStats_t); its CSPerRoundStats_t base fields at +0xf8 |
| CSPerRoundStats_t +0x30 .. +0x60 | m_iKills +0x30, m_iDeaths +0x34, m_iAssists +0x38, m_iDamage +0x3c, m_iEquipmentValue +0x40, m_iMoneySaved +0x44, m_iKillReward +0x48, m_iLiveTime +0x4c, m_iHeadShotKills +0x50, m_iObjective +0x54, m_iCashEarned +0x58, m_iUtilityDamage +0x5c, m_iEnemiesFlashed +0x60 |
| CSMatchStats_t +0x68 .. +0xb8 | m_iEnemy5Ks +0x68, 4Ks +0x6c, 3Ks +0x70, KnifeKills +0x74, TaserKills +0x78, 2Ks +0x7c, m_iUtility_Count +0x80 .. m_iEntryWins +0xb8 (schema.py) |
| action tracking +0x188 | m_iNumRoundKills |
| action tracking +0x2a8 / +0x198 | the m_numChickensKilled block (m_killsWhileBlind, m_bombCarrierkills, m_flBurnDamageInflicted, m_flBlastDamageInflicted, m_iDinks, ...): match / round |
| action tracking +0x3b8 .. +0x410 | unnamed in the schema (not networked) |

## Constants

| Value | What |
|---|---|
| 0x181f57380 | accolade table (0x28 an entry) |
| 0x181da0630 | score weight table: 9 pairs by (group, position), index x 100 is the weight |

## The selection (1801bdd00), read in part

1. For each controller of the team (-1: every one): its slot (1813aa290), then for each id 11..42 with a value function whose value > 0: a record { player, id, value, position, score } in the player's list (1801c7300).
2. Per accolade (the table walked again): the players with it, sorted (V_qsort), position 1.. in order; a first place whose value equals the second's becomes position 2.
3. Score: `c x (flags & 4 and game rules: 180928950 x 0.5)`, looked up by (group, position) in 0x181da0630, then `1801d3440(index, group, c, 0, 0.1) x that weight`.
4. Each player's list sorted by score (1801bdcb0); the first record at position 1 with a score > 0 is theirs, its id marked taken (a 64-bit mask).
5. Then, last player first, one without: their best untaken one, else a random gimme (RandomInt(0, n - 1) over the pool 1..10, taken out as drawn, through the 9 / 10 count at local_dc / local_128).
6. 1801be680 writes and logs the choice.

## Unread

- Every writer of the stats above: the per-round stats and their roll into m_matchStats (the round's end), equipment value, money saved, kill reward, live time, objective, cash earned, the 2k..5k / knife / taser kills, the dinks, the unnamed +0x3b8..+0x410 (rounds survived, no-purchase wins, first kills, clutch kills, pistol kills, sniper kills, unique weapon kills), the money services' cash spent.
- What edx is at the value calls (the gated ones return 0 when it is <= 1); 180b079b0, 180b07d50, 180a7a8e0, 1801d3440, the table at 0x181da0630, 1801bdcb0, 180928950.
- CCSUsrMsg_EndOfMatchAllPlayersData's fields (kills, deaths, assists, adr, hsp, enemiesflashed, utilitydamage, score) and when it is sent.
