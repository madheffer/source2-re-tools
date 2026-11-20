# Damage prediction (the shooter's own hit effects, predicted kills, the server's half)

client_20261105 (cvars, usercmd writer, gate), client_20261015 (decompiled flow), server_20261105. Image base 0x180000000. cstrike15_usermessages.proto (DescriptorProto decoded by hand).

Damage prediction decides who plays a hit's effects first (the shooter's client on fire, or everyone on the server's damage). Lag compensation is separate (shots.md 5, 5b, 5c; usercmd.md).

## Functions

| Address | Module | What |
|---|---|---|
| 180d04950..180d04bce | client 1105 | CSGOUserCmdPB writer (the three bools) |
| 1808845a0 | client 1105 | IsDamagePredictionEnabled(controller) (name ours) |
| 180af5490 | client 1105 | recording branch test (unread) |
| 180b84fa0 | client 1105 | net channel (0) |
| 18015a150 | client 1105 | minss |
| 180882d00 | client 1015 | same gate for the fire paths (recording branch: the command's flags) |
| 180887d60 | client 1015 | FireBullet |
| 18082e180 / 180833b30 / 180d02130 | client 1015 | taser / knife / other fire path using 180882d00 |
| 180af3bb0 | client 1015 | controller test |
| 18022e9e0 | client 1015 | victim's client-side TakeDamage(victim, info, 0) |
| 180b61d70 | client 1015 | (&msg, 0x182): gates sending CCSUsrMsg_DamagePrediction (engine vfn 400) |
| 180b754f0 | client 1015 | camera-shake-like call when the command's +0x94 == 2 |
| 1808de930 | client 1015 | pawn TakeDamage vfn 1: push predicted damage |
| 18089fb40 | client 1015 | (pawn+0x15a0) == 0 gate |
| 1809442a0 | client 1015 | controller's command tick |
| 180c671a0 | client 1015 | GetHealth: `m_iHealth (+0x34c) - sum of the list's damages` |
| 1808debc0 | client 1015 | pawn TakeDamage vfn 2 |
| 180957580 | client 1015 | first call of 1808debc0 |
| 1808c8880 | client 1015 | death's attacker feedback |
| 180c8f940 | client 1015 | predicted kill ragdoll |
| 1808a00e0 | client 1015 | hit effects (pawn+0x15a0, info) |
| 180887960 | client 1015 | (info, head, mode): the attacker that did not predict this |
| 18089d3b0 | client 1015 | the blood |
| 180aadf40 | client 1015 | hit group from the trace |
| 18122a800 | client 1015 | blood effect (CEffectData) |
| 1808a0150 | client 1015 | the hit sounds (copy of server 180a95310) |
| 180834006 | client 1015 | knife flesh hit (reads +0x49) |
| 180c70920 | client 1015 | make the ragdoll (pawn, bone, force, 180905020(), 0x80000) |
| 180905020 | client 1015 | argument of the ragdoll |
| 1808a1250 | client 1015 | frame hook (from 180a81630): expire predicted damage |
| 18093f590 | client 1015 | latency (-1) |
| 180c914f0 | client 1015 | drop entries with tick <= expire (swap with the last) |
| 1808a1080 | client 1015 | frame walk: 180c8c070 |
| 180c8c070 | client 1015 | predicted ragdoll undone when GetHealth > 0 again |
| 1808e4b60, 18095b260 | client 1015 | undo calls (snap back) |
| 180c91350 | client 1015 | clear the list (pawn reset) |
| 180a9e270 | server 1105 | set m_bFireBulletsSeedSynchronized (from 180ac46e0, per controller each frame) |
| 180a8a650 | server 1105 | NetworkStateChanged |
| 180c7f1e0 | server 1105 | command run: seeds A / B |
| 1803ebc60 / 1803ebc70 | server 1105 | setters of A (181daae60) / B (181daae64) |
| 180c70120 | server 1105 | A = -1 after the command |
| 1802a4e90 | server 1105 | the shot's seed (from 1809f8a70 / 1809ffd30) |
| 18029f080 | server 1105 | angle hash step |
| 180a77f60 | server 1105 | (info, head): attacker to leave out of feedback (player-sounds.md 1) |
| 180a95310 / 180ac13d0 | server 1105 | hit / death feedback |
| 180a94400 | server 1105 | the hit's sounds gate (type & (armor ? 0x28 : 0x20)) |
| 180a30179 | server 1105 | knife hit: flesh PAS filter (1809f3e40) drops the attacker (RemoveRecipient 180c8b610) when +0x49 |

## Fields

| Offset | Field |
|---|---|
| CSGOUserCmdPB +0x20 | has-bits: 0x2 left hand, 0x4 / 0x8 / 0x10 the three bools, 0x20 / 0x40 the attack indices |
| +0x48 | left_hand_desired |
| +0x49 / +0x4a / +0x4b | is_predicting_body_shot_fx / _head_shot_fx / _kill_ragdolls |
| +0x4c / +0x50 | attack1 / attack2 start history index |
| CBaseUserCmdPB (+0x40) +0x6c | random seed (-1 with none) |
| client controller +0x569 | m_bPredictable |
| client controller +0x780 | current CSGOUserCmdPB (+8 command_num) |
| client controller +0x790 | m_bIsLocalPlayerController |
| client controller +0x97c | m_bFireBulletsSeedSynchronized |
| server controller +0xa39 | m_bFireBulletsSeedSynchronized |
| server controller +0x708 | last CSGOUserCmdPB |
| client pawn +0x14bc | controller handle |
| client pawn +0x34d8 / +0x34d0 / +0x34e0 / +0x34e4 | predicted damage CUtlVector {tick, damage}: data / count / alloc |
| client pawn +0x34e8 | predicted ragdoll flag |
| client pawn +0x11a8 / +0x11b0 | ragdoll present / ragdoll (freed through vfn 0x448) |
| client pawn +0x34c | m_iHealth |
| info +0x2c..+0x34 | force position |
| info +0x38 / +0x3c | inflictor / attacker |
| info +0x44 | damage |
| info +0x68 | trace (entry + 0x120); trace +0xb8 bone |
| info +8..+0x10 | force |
| info +100 / +0x65 | blood byte / helmet |
| FireBullet damage list (local_2598) | 0x1e0-byte entries, victim at +0x128 |
| gpGlobals +0x44 | expire floor |

## Constants

| cvar | DLL | Site | Handle | Flags | Default | What |
|---|---|---|---|---|---|---|
| cl_predict_body_shot_fx | client | 1800ad5ec | 182533430 | 0x80088 | 0 | "Predict Body Shot Effects" |
| cl_predict_head_shot_fx | client | 1800ad69c | 182533440 | 0x80088 | 0 | "Predict Head Shot Effects" |
| cl_predict_kill_ragdolls | client | 1800ad74c | 182533450 | 0x80088 | 1 ([rsp+0x37] = 1) | "Predict Kill Ragdolls" |
| sv_damage_prediction_allowed | server / client | 1800c64fc / 1800aef3c | 182173a28 / 182533420 | 0x82000 (replicated) | 1 | the server lets clients predict |
| sv_usercmd_custom_random_seed | server | 1800d9f40 | 182191578 | 0x80000 | 0 ([rsp+0x37] = 0) | "When enabled server will populate an additional random seed independent of the client" |

| Value | What |
|---|---|
| 0x3d8f5c29 = 0.07 | latency cap |
| 1/64 + 0.1, x 64 | expire margin |
| 0x80000 | ragdoll damage bit |
| 4 | DMG_SLASH bit: no blood |
| 0x28 / 0x20 | sound skip mask (armor hit / not) |
| 0xdd82057c | attacker feedback sound parameter |
| 1.4 | smoke gate |
| 0x182 | 180b61d70 argument |
| CSGOUserCmdPB fields | 1 base, 2 input_history, 6 attack1_start_history_index, 7 attack2_start_history_index, 9 left_hand_desired, 11 is_predicting_body_shot_fx, 12 is_predicting_head_shot_fx, 13 is_predicting_kill_ragdolls |

The three client cvars have one reader each, the usercmd writer; every later test reads the command's copies.

## Usercmd writer (180d04950)

- Local pawn vfn 0xab8 (alive), controller (+0x14bc) resolved, `1808845a0(controller)` true -> the three bytes = the cvars (convar +0x58), has-bits set. Else left unset (false).

## The gate (1808845a0)

```
if (!controller.m_bPredictable (+0x569)) return false
if (engine client vfn 0x150 ())            // read as "playing back a recording"
  return 180af5490() && controller+0x780 && (+0x49 || +0x4a || +0x4b)
if (!sv_damage_prediction_allowed) return false
nc = 180b84fa0(0)
if (nc && nc vfn 0x50 () > min(0.07, sv_maxunlag x 0.95)) return false   // 18015a150 = minss
return controller.m_bFireBulletsSeedSynchronized (+0x97c)
```

- With sv_maxunlag 1 a client over 70 ms away predicts nothing. vfn 0x50: which latency (one way / round trip) unread.

## Seed synchronisation (server)

- 180a9e270: `m_bFireBulletsSeedSynchronized = (181daae64 == 181daae60)`, NetworkStateChanged on change.
- 180c7f1e0: A = the command's random seed (-1 with none); B = the same, unless sv_usercmd_custom_random_seed: B = SHA1(Plat_FloatTime() + 2^32 as a double, RandomInt(0, 0x7fffffff), 0) word +0x64. 180c70120: A = -1 after.
- 1802a4e90: A == B -> the client's seed hashed with the two angles (18029f080 each) and the shot's int (a 12-byte MD5-style update via the import at 0x...f09 / f1f / f2a, unread); else B.
- Default (0): every controller synchronized; the gate passes on latency alone.

## FireBullet's predicted damage (client 180887d60, decompile lines ~632-748)

1. After the bullet walk, with the shooter's controller, 180af3bb0 and 180882d00 true: for each player damaged (alive: vfn 0x4f0, 0xab8), info gets the force position and its trace; `18022e9e0(victim, info, 0)`.
2. Fills CCSUsrMsg_DamagePrediction (command_num = controller+0x780 +8, pellet_idx = param_9, victim_slot, victim_starting_health (180c671a0 before), victim_damage = (int)info+0x44, shoot_pos, shoot_dir, aim_punch); sent via engine vfn 400 only when 180b61d70(&msg, 0x182). The server registers the class; no server reader found.

## Victim's client TakeDamage (vtables 181c8a898 / 181c8a8a0, 181c905d8 / e0, 181c911a8 / b0, 181c95d18 / 20)

- 1808de930: `18089fb40(pawn+0x15a0) == 0` and the inflictor an alive pawn whose controller passes 180af3bb0 -> push {tick = 1809442a0(controller), damage = (int)info+0x44}.
- 180c671a0 GetHealth is every client read of a pawn's health (HUD, target ID, death tests).
- 1808debc0: 180957580; GetHealth < 1 -> 1808c8880; 180c8f940; 1808a00e0(pawn+0x15a0, info).

## Hit effects (client)

- **180887960(info, head, mode)**: attacker (+0x3c) alive with a controller; inflictor (+0x38) the attacker; its command (+0x780) with +0x49 (body) / +0x4a (head) set; then mode 1 -> 0 (predicted: play here), mode 0 -> 0 only for the local controller (+0x790). Any test failing: returns the controller (the server's copy plays). No attacker: 0.
- **1808a00e0**: unless damage bits have 4, 18089d3b0 (blood); then as server 180a94400, `type & (armor hit ? 0x28 : 0x20)` clear -> 1808a0150 (sounds).
- **18089d3b0**: needs info +100; head = hit group 1 (180aadf40); `180887960(info, head, 1) == 0` -> head, damage > 0 and helmet (+0x65): `particles/impact_fx/impact_helmet_headshot.vpcf` at the hit; then victim vfn 0x4e0 with a level from health left vs damage (< 1: -1; < 12: 0; < 16: 3; < 22: 4; < 31: 5; < 75: 6; else 7; health - damage <= 0: 7), then vfn 0x4e0(0), then 18122a800 (CEffectData at the hit, shot direction negated). Effect names unread.
- **1808a0150**: attacker feedback only (`Player.DamageBody[Armor][.Knife].AttackerFeedback`, `Player.DamageHeadShot[Armor].AttackerFeedback`, parameter 0xdd82057c), same line-of-sight and smoke (< 1.4) gate (player-sounds.md 2), only when `180887960(info, head, 1) == 0`. Burn / club / Player.DamageKevlar as the server's.
- **1808c8880**: `Player.Death[Body|HeadShot][Armor].AttackerFeedback`, same gate.
- Knife flesh (client 180834006, server 180a30179): a body-predicting attacker plays `Weapon_Knife.Hit.*.Flesh` itself.

## Predicted kill ragdoll (client)

- 180c8f940: inflictor's controller passes 180af3bb0, GetHealth < 1, command +0x4b set, pawn +0x34e8 clear (then set), no ragdoll (+0x11a8 == 0): `180c70920(pawn, trace bone (+0x68 -> +0xb8, -1 without), info force (+8..+0x10), 180905020(), 0x80000)`.
- 1808a1250: `expire = 1809442a0() - (int)((min(0.07, sv_maxunlag x 0.95) + 18093f590(-1) + 1/64 + 0.1) x 64)`, at least gpGlobals +0x44; 180c914f0 drops entries with tick <= expire.
- 1808a1080 -> 180c8c070: a predicted ragdoll whose GetHealth > 0 again -> 1808e4b60, ragdoll (+0x11b0) freed via vfn 0x448, 18095b260: the player snaps back ("the target snaps back to its server-authoritative position").

## Server's half

- Controller +0x708 is the last command (+0x49 / +0x4a / +0x4b).
- 180a77f60: the attacker controller left out of the feedback filters when its command has +0x49 (body) / +0x4a (head); used by 180a95310 and 180ac13d0.
- 180a30179: the knife's flesh sound drops the attacker when +0x49.
- No server code reads +0x4b; sv_damage_prediction_allowed has no server reader.

## Unread

- The net channel's vfn 0x50 latency; engine client vfn 0x150 and 180af5490.
- 1802a4e90's hash; 180c70920's ragdoll; 18122a800's effect and the vfn 0x4e0 levels' names.
- 18022e9e0's own steps; the DamagePrediction message's consumer; 180b61d70; 180b754f0.
