# The end-of-match accolades (server_20261105.dll), read 2026-11-18 (end-of-match plan R2; not ported yet)

The nomination each end-of-match stats card shows (player_stats_card.vts SetAccolade: `#accolade_<name>` and
`_desc`, `_2` for second place; endofmatch-characters.vts reads allplayerdata[].nomination { eaccolade, value,
position }). GoToIntermission (18092cdf0) runs the selection for team 3 then team 2 (one pass for everyone in Arms
Race / deathmatch): docs/game/intermission.md.

## The table (static initializers 18004d160 and the 41 beside it; entry = 0x181f57380 + id x 0x28)

`{ +0 int id, +8 value fn(controller, edx), +0x10 int flags, +0x14 int group, +0x18 float c, +0x1c float d,
+0x20 const char *name }`. ids 1..10 are the "gimme_01".."gimme_10" fallbacks (no value function). Read with the
scratch script acctable.py (each initializer's rip-relative stores, constants followed through registers).

| id | name | fn | flags | group | c | d | the value |
|---|---|---|---|---|---|---|---|
| 11 | kills | 1801cfed0 | 6 | 1 | 0.02 | 1 | action tracking +0xf8: m_matchStats.m_iKills |
| 12 | damage | 1801cfd40 | 6 | 1 | 2 | 100 | +0x104 m_iDamage |
| 13 | adr | 1801cfbe0 | 4 | 1 | 2 | 100 | 180b079b0(action tracking): the ADR |
| 14 | mvps | 1801cff50 | 2 | 1 | 0 | 1 | edx <= 1: 0; else 180a7a8e0(controller) |
| 15 | assists | 1801cfbf0 | 6 | 2 | 0.02 | 1 | +0x100 m_iAssists |
| 16 | hsp | 1801cfe00 | 0 | 2 | 10 | 100 | 180b07d50(action tracking): the headshot % |
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
| 37 | burndamage | 1801cfc30 | 6 | 2 | 0.13 | 1.3 | +0x2b4 m_flBurnDamageInflicted (a float) |
| 38 | cashspent | 1801cfc40 | 2 | 3 | 1000 | 8000 | gated as killreward; controller +0x7e8 (in-game money services) +0x50 |
| 39 | uniqueweaponkills | 1801d00f0 | 0 | 2 | 2 | 6 | +0x410 |
| 40 | dinks | 1801cfd80 | 6 | 2 | 0.018 | 1 | +0x1ac (the round block's m_iDinks: +0x198 + 0x14) |
| 41 | knifekills | 1801cff10 | 0 | 1 | 0 | 3 | +0x13c m_iEnemyKnifeKills |
| 42 | taserkills | 1801d00d0 | 0 | 1 | 0 | 3 | +0x140 m_iEnemyTaserKills |

The controller's action tracking services are at +0x7f8; m_matchStats (CSMatchStats_t) at its +0xc8, so its
CSPerRoundStats_t base fields at +0xf8 (m_iKills +0x30, m_iDeaths +0x34, m_iAssists +0x38, m_iDamage +0x3c,
m_iEquipmentValue +0x40, m_iMoneySaved +0x44, m_iKillReward +0x48, m_iLiveTime +0x4c, m_iHeadShotKills +0x50,
m_iObjective +0x54, m_iCashEarned +0x58, m_iUtilityDamage +0x5c, m_iEnemiesFlashed +0x60) and its own (m_iEnemy5Ks
+0x68, 4Ks +0x6c, 3Ks +0x70, KnifeKills +0x74, TaserKills +0x78, 2Ks +0x7c, m_iUtility_Count .. m_iEntryWins
+0x80..+0xb8); m_perRoundStats at +0x40; m_iNumRoundKills +0x188; the m_numChickensKilled block (m_killsWhileBlind,
m_bombCarrierkills, m_flBurnDamageInflicted, m_flBlastDamageInflicted, m_iDinks, ...) at +0x2a8 for the match and
+0x198 for the round (tools/re/game/schema.py names). +0x3b8 .. +0x410 are unnamed in the schema (not networked).

## The selection (1801bdd00, (players, team)), read in part

- For each controller of the team (-1: every one): its slot (1813aa290), then for each accolade id 11..42 with a value
  function whose value > 0: a record { player, id, value, position, score } in the player's list (1801c7300 by slot).
- Per accolade (the table walked again): the players with it, sorted (V_qsort), position 1.. in order; a first place
  whose value equals the second's becomes position 2. The score: c x (flags & 4 and game rules: 180928950 x 0.5),
  looked up by (group, position) in the table at 0x181da0630 (9 pairs: index x 100 is the weight), then
  1801d3440(index, group, c, 0, 0.1) x that weight.
- Each player's list sorted by score (1801bdcb0); the first record at position 1 with a score > 0 is theirs, its id
  marked taken (a 64-bit mask); then, last player first, one without: their best untaken one, else a random gimme
  (RandomInt(0, n - 1) over the pool 1..10, taken out as drawn, through the 9 / 10 count at local_dc / local_128).
- 1801be680 writes the chosen { id, value, position } into the player's EndOfMatchAllPlayersData entry and logs
  "ACCOLADE, FINAL: {name}, player<slot>, VALUE: v, POS: p, SCORE: s".

## Not read yet (needed before the port)

- Every writer of the stats above: CS2's per-round stats and their roll into m_matchStats (the round's end), the
  equipment value, money saved, kill reward, live time, objective, cash earned, the 2k..5k / knife / taser kills, the
  dinks, the unnamed +0x3b8..+0x410 (rounds survived, no-purchase wins, first kills, clutch kills, pistol kills,
  sniper kills, unique weapon kills), the in-game money services' cash spent.
- What edx is at the value calls (the gated ones return 0 when it is <= 1), 180b079b0 (ADR), 180b07d50 (HS%),
  180a7a8e0 (MVPs), 1801d3440 (the score's curve), the table at 0x181da0630, 1801bdcb0 (the sort), 180928950.
- CCSUsrMsg_EndOfMatchAllPlayersData's fields (the stats each card shows: kills, deaths, assists, adr, hsp,
  enemiesflashed, utilitydamage, score) and when it is sent.
