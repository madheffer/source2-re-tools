# Damage prediction: the client's own hit effects, its predicted kills, and the server's half

Read 2026-11-16, session "predict-hit-fx". client_20261105.dll for the cvars, the usercmd writer and the gate;
client_20261015.dll (in ReVa) for the decompiled flow; server_20261105.dll for the server side. Image base
0x180000000. Tools: tools/re/strings, riprefs, cvardefs, disasm, fnstrings, schema, fieldwrites, vtowner, callers;
two scratch scanners (a block pointer's byte fields; one DescriptorProto decoded by hand, since protodesc.py stops
partway through cstrike15_usermessages.proto).

This is what CS2 means by "hit prediction". **Lag compensation is a separate thing** (shots.md 5, 5b, 5c; usercmd.md):
the server rewinds the others to what the shooter drew. Damage prediction only decides **who plays a hit's effects
first**: the shooter's client the moment it fires, or everyone once the server's damage arrives.

## 1. The cvars

| cvar | DLL | handle | flags | default | what |
|---|---|---|---|---|---|
| cl_predict_body_shot_fx | client (1105 site 1800ad5ec) | 182533430 | 0x80088 | **0** | Settings > Game > Damage Prediction "Predict Body Shot Effects" |
| cl_predict_head_shot_fx | client (1800ad69c) | 182533440 | 0x80088 | **0** | "Predict Head Shot Effects" |
| cl_predict_kill_ragdolls | client (1800ad74c) | 182533450 | 0x80088 | **1** ([rsp+0x37] = 1) | "Predict Kill Ragdolls" |
| sv_damage_prediction_allowed | server 1800c64fc / client 1800aef3c | 182173a28 / 182533420 | 0x82000 (replicated) | **1** | the server lets clients predict |
| sv_usercmd_custom_random_seed | server 1800d9f40 | 182191578 | 0x80000 | **0** ([rsp+0x37] = 0) | "When enabled server will populate an additional random seed independent of the client" |

The three client cvars have one reader each, the usercmd writer (section 2). Nothing else reads the cvars: every
later test reads the **command's** copies.

## 2. The usercmd's three bools (client 1105 180d04950..180d04bce, the CSGOUserCmdPB writer)

CSGOUserCmdPB (client 1105's descriptor): 1 base, 2 input_history, 6 attack1_start_history_index, 7
attack2_start_history_index, 9 left_hand_desired, **11 is_predicting_body_shot_fx, 12 is_predicting_head_shot_fx,
13 is_predicting_kill_ragdolls** (bools). In memory: has-bits +0x20 (0x2 left hand, 0x4 / 0x8 / 0x10 the three, 0x20 /
0x40 the attack indices), +0x48 left_hand_desired, **+0x49 / +0x4a / +0x4b the three**, +0x4c / +0x50 the indices.

The writer, with rbx the local pawn: `pawn vfn 0xab8` (alive) and the pawn's controller (handle +0x14bc) resolved,
then **`1808845a0 IsDamagePredictionEnabled(controller)`** (section 3) true -> the three bytes = the three cvars'
values (convar +0x58), their has-bits set. Otherwise the fields are left unset (false).

## 3. The gate: `IsDamagePredictionEnabled` (client 1105 1808845a0; the name is ours)

```
if (!controller.m_bPredictable (+0x569)) return false
if (engine client vfn 0x150 ())            // read as "playing back a recording": the recorded command decides
  return 180af5490() && controller+0x780 (the current CSGOUserCmdPB) && (+0x49 || +0x4a || +0x4b)
if (!sv_damage_prediction_allowed) return false
nc = 180b84fa0(0)                          // the net channel
if (nc && nc vfn 0x50 () > min(0.07, sv_maxunlag x 0.95)) return false   // 18015a150 = minss; 0x3d8f5c29 = 0.07
return controller.m_bFireBulletsSeedSynchronized (+0x97c)
```

- The latency is the net channel's vfn 0x50 (UNSETTLED: which INetChannelInfo latency, one way or round trip; not
  read in engine2 / networksystem yet). **With sv_maxunlag 1 a client more than 70 ms away predicts nothing**: its
  hit effects all come from the server, as for everyone with the cvars at 0.
- 180882d00 (client 1015) is the same test on a controller for the fire paths (FireBullet 180887d60, the taser
  18082e180, the knife 180833b30, 180d02130): with the recording branch it returns the command's flags, else the gate.

## 4. m_bFireBulletsSeedSynchronized (server 1105)

- CCSPlayerController +0xa39 (server schema), +0x97c on the client. Set by **180a9e270** (from 180ac46e0, per
  controller each frame): `= (181daae64 == 181daae60)`, NetworkStateChanged (180a8a650) when it changes.
- **180c7f1e0** (a command's run, vtable slot; before 180c70120 clears it): A (181daae60, setter 1803ebc60) = the
  command's CBaseUserCmdPB random seed (+0x40 -> +0x6c, -1 with none); B (181daae64, setter 1803ebc70) = the same
  seed, unless **sv_usercmd_custom_random_seed**: then B = SHA1(Plat_FloatTime() + 2^32 as a double, RandomInt(0,
  0x7fffffff), 0) word +0x64 (a server-only seed). 180c70120 sets A = -1 after the command.
- **1802a4e90** (the shot's seed, from 1809f8a70 / 1809ffd30): A == B -> the client's seed hashed with the two
  angles (18029f080 each) and the shot's int (a 12-byte MD5-style update through the import at 0x...f09 / f1f / f2a,
  unread), so the client's spread is the server's; else B.
- So with CS2's default (0) every controller is synchronized and the gate passes on the latency alone.

## 5. The client's FireBullet predicts the damage (client 1015 180887d60, lines ~632-748 of the decompile)

After the bullet's walk, with the shooter's controller (pawn +0x14bc), 180af3bb0 and **180882d00** true: for each
player the walk damaged (the list at local_2598, 0x1e0-byte entries; the victim at +0x128, alive: vfn 0x4f0 and
0xab8), the entry's CTakeDamageInfo gets the force position (+0x2c..+0x34) and its trace (+0x68 = entry + 0x120), and
**18022e9e0(victim, info, 0)** runs the victim's client-side TakeDamage. Then it fills a **CCSUsrMsg_DamagePrediction**
(command_num = controller+0x780 +8, pellet_idx = param_9, victim_slot, victim_starting_health = the health read
before (180c671a0), victim_damage = (int)info+0x44, shoot_pos, shoot_dir, aim_punch) and hands it to the engine's
vfn 400 only when 180b61d70(&msg, 0x182) (UNSETTLED: a recording / log path; the server registers the class but no
server code was found reading it). The message is not part of the damage: TakeDamage is.

When the shooter's command has +0x94 == 2 a camera-shake-like call 180b754f0 runs (UNSETTLED).

## 6. The victim's client TakeDamage: two pawn vfns (client 1015 vtables 181c8a898 / 8a0, 181c905d8 / e0, 181c911a8 / b0, 181c95d18 / 20)

- **1808de930** (the first): `18089fb40(pawn+0x15a0)` == 0 and the info's inflictor (+0x38) an alive pawn whose
  controller passes 180af3bb0 -> **push {tick = 1809442a0(controller) (the command's tick), damage = (int)info+0x44}**
  onto the victim's predicted damage list (CUtlVector at +0x34d8, count +0x34d0, alloc +0x34e0 / +0x34e4).
- **180c671a0 GetHealth** (used for every client read of a pawn's health: the HUD, the target ID, the death tests
  below): `m_iHealth (+0x34c) - sum of the list's damages`.
- **1808debc0** (the second): 180957580; GetHealth < 1 -> **1808c8880** (the death's attacker feedback, below);
  **180c8f940** (the kill ragdoll); **1808a00e0(pawn+0x15a0, info)** (the hit's effects).

## 7. The hit's effects on the shooter's client (client 1015 1808a00e0 -> 18089d3b0, 1808a0150)

- **180887960(info, head, mode)**, "the attacker that did not predict this": the info's attacker (+0x3c) alive with a
  controller; the inflictor (+0x38) the attacker; its command (+0x780) with **+0x49 (body) / +0x4a (head)** set; then
  mode 1 -> 0 (predicted: play here), mode 0 -> 0 only when the controller is m_bIsLocalPlayerController (+0x790).
  Any test failing returns the controller (not predicted: the server's copy plays). No attacker at all -> 0.
- **1808a00e0**: unless the damage bits have 4 (DMG_SLASH... read as "not a bullet"), 18089d3b0 (the blood); then,
  as the server's 180a94400, `type & (armor hit ? 0x28 : 0x20)` clear -> 1808a0150 (the sounds).
- **18089d3b0 the blood**: needs the info's +100 byte; head = the trace's hit group == 1 (180aadf40);
  `180887960(info, head, 1) == 0` -> with head, damage > 0 and the info's +0x65 (a helmet): the particle
  `particles/impact_fx/impact_helmet_headshot.vpcf` at the hit; then the victim's vfn 0x4e0 with a level from the
  health left vs the damage (< 1: -1; < 12: 0; < 16: 3; < 22: 4; < 31: 5; < 75: 6; else 7; health - damage <= 0: 7),
  then vfn 0x4e0(0), then the blood effect (18122a800, CEffectData at the hit with the shot's direction negated).
  (Read as the blood decal / spray size; UNSETTLED which effect names.)
- **1808a0150 the sounds**: the client's copy of server 180a95310 (player-sounds.md 2) for **the attacker's feedback
  only** (`Player.DamageBody[Armor][.Knife].AttackerFeedback`, `Player.DamageHeadShot[Armor].AttackerFeedback`, the
  0xdd82057c parameter), with the same line-of-sight and smoke (< 1.4) gate, played only when
  `180887960(info, head, 1) == 0`. Burn / club / Player.DamageKevlar branches as the server's.
- **1808c8880 the death's feedback** (`Player.Death[Body|HeadShot][Armor].AttackerFeedback`), the same gate (180887960
  called from it).
- The knife's flesh hit (client 180834006 reads +0x49; server 180a30179 likewise): a body-predicting attacker plays
  `Weapon_Knife.Hit.*.Flesh` itself.

## 8. The predicted kill ragdoll (client 1015 180c8f940, 180c8c070, 1808a1250, 1808a1080)

- **180c8f940**: the inflictor's controller passes 180af3bb0, GetHealth < 1, its command's **+0x4b** set, the pawn's
  +0x34e8 (predicted ragdoll) clear (then set) and no ragdoll yet (+0x11a8 == 0): **180c70920(pawn, the trace's
  bone (+0x68 -> +0xb8, -1 without), the info's force (+8..+0x10), 180905020(), the damage bit 0x80000)**: the ragdoll.
- **1808a1250** (a frame hook over every alive pawn, 180a81630): expire = `1809442a0() - (int)((min(0.07, sv_maxunlag x
  0.95) + 18093f590(-1) (the latency) + 1/64 + 0.1) x 64)`, at least gpGlobals +0x44; **180c914f0** drops the list's
  entries with tick <= it (swap with the last).
- **1808a1080** (the same walk): **180c8c070**: a predicted ragdoll whose GetHealth is > 0 again (the server's
  m_iHealth arrived and the entries expired) -> 1808e4b60, the ragdoll (+0x11b0) freed through vfn 0x448,
  18095b260: **the player snaps back** (the setting's own help text: "the target snaps back to its
  server-authoritative position"). 180c91350 clears the list (the pawn's reset).

## 9. The server's half (server 1105)

- The controller keeps its last command: **+0x708** is the CSGOUserCmdPB (+0x49 / +0x4a / +0x4b).
- **180a77f60(info, head)** (player-sounds.md 1): the attacker controller to leave out of the feedback filters when its
  command has +0x49 (body) / +0x4a (head). Used by the hit's 180a95310 and the death's 180ac13d0.
- **180a30179** (the knife's hit): the flesh sound's PAS filter (1809f3e40) loses the attacker (RemoveRecipient
  180c8b610) when +0x49 is set.
- No server code reads +0x4b: the ragdoll is the client's alone. sv_damage_prediction_allowed has no server reader (a
  replicated cvar only the client reads).

## What the port does (2026-11-16)

- The server's half: the usercmd carries the three bools as cmd[15] bits 1 / 2 / 4 (move-state.js cleanCmd), kept as
  the controller's last command (combat.js p.predictFx); damage-sounds.js `predictedBy` is 180a77f60 and leaves a
  predicting attacker out of the hit / death feedback (psnd `x`), the blood and the helmet's sparks (blood.md: `x`), and
  the knife's flesh sound (knifehit `x`).
- The effects a client would predict exist now: the blood (blood.md), the death ragdoll (ragdoll.md), the feedback
  sounds (player-sounds.md).
- NOT YET: the client writing the bools (its gate 1808845a0: sv_damage_prediction_allowed, the latency against
  min(0.07, sv_maxunlag x 0.95), m_bFireBulletsSeedSynchronized) and its own FireBullet's TakeDamage on the bodies it
  draws (section 5: CS2's capsules on the drawn poses through the sim's bullet), the victims' predicted damage lists,
  the predicted kill ragdoll and its snap back. Until then the client sends no bools: the server tells it of every
  hit, which is what CS2 does with its default settings for body and head shots (0); the kill ragdoll (default 1)
  comes when the server's death does.

Unread: the net channel's vfn 0x50 latency; engine client vfn 0x150 and 180af5490 (the recording branch); 1802a4e90's
hash; 180c70920's ragdoll; 18122a800's effect and the vfn 0x4e0 levels' names; 18022e9e0's own steps (the client's
TakeDamage before the vfns); the DamagePrediction message's consumer.
