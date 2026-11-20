# A player's blood

server_20261105, client_20261015. Client: fx_cs_blood.cpp. Decal groups Blood / Bloodlvl2 .. Bloodlvl6
(decalgroups.vdata).

## Functions

| Address | Module | What |
|---|---|---|
| 180a89430 | server | hit group step: sets m_bShouldBleed / m_bShouldSpark (stores at 180a89a19 / 180a89a1d) |
| 180fce950 | server | CTakeDamageInfo ctor (zeroes both) |
| 180ad2a20 | server | (victim, attacker controller) refusal test |
| 18093d760 | server | gamerules' answer when 180ad2a20 refuses (unread) |
| 180a94400 | server | damage services' post -> 180a88a50 |
| 180a88a50 | server | the server's blood |
| 180a95310 | server | the hit's sounds (after the blood: player-sounds.md) |
| 180a77f60 | server | excluded client (info, head, 1) (damage-prediction.md 9) |
| 180c4f310 | server | particle to the PAS less excluded |
| 180cf7020 | server | health left |
| 1803eee10 | server | TraceBleed(pawn, damage as it was, direction, trace, type) |
| 180250e50 | server | the trace |
| 180cbb810 | server | UTIL_BloodDecalTrace(trace, level) |
| 1811190a0 | server | DispatchEffect |
| 180d1e3a0 | client | effect callback -> 180d226c0 |
| 180d226c0 | client | csblood |
| 180cb2100 | client | end-of-match / team-select camera test |
| 180aca8d0 | client | launch-option flag (unset) |
| 180a3ce50 | client | DispatchParticleEffect |

## Fields

| Offset | Field |
|---|---|
| CTakeDamageInfo +0x64 | m_bShouldBleed |
| CTakeDamageInfo +0x65 | m_bShouldSpark |
| CTakeDamageInfo +0x2c | direction |
| CTakeDamageInfo +0x70 | bit 2 clears bleed |
| pawn +0x15a8 | m_bGunGameImmunity |
| trace +0x84 / +0x78 / +0x90 | end / start / angles |
| damage result +0x20 | damage dealt |
| pawn vfn 0x538 / 0x530 | blood level: 0x538 called with the level (step 4), 0x530 read by TraceBleed |
| pawn vfn 0x5c8 | dead pawn's count (taken as never empty) |
| CEffectData (client) +0x14, +8, +0x38, +0x20, +0x44 | start, origin, entity, normal, magnitude |
| entity +0x30 | flags (bit 7: no blood) |
| 18223f628 | client: localplayer hit clock |

## Constants

| Value | What |
|---|---|
| 0x200, 0x100 (DMG_SHOCK) | damage bits clearing bleed |
| 0xc7 | type bits TraceBleed needs |
| 172 u / 200 u | bleed trace / retry length |
| -0.35 | retry z offset |
| interacts 0x1001, group 3 | bleed trace |
| 40 / 20 | damage_impact_heavy ("Damage ABOVE ...") / damage_impact_medium ("Damage BELOW ...") |
| 10.0 at 0x181ad0f70 | powf exponent |
| 57.29578 | rad -> deg |

## Bleeds (180a89430)

Bleed starts 1; an attacker player 180ad2a20 refuses takes 18093d760(gamerules)'s answer; m_bGunGameImmunity -> 0; bit
0x200 -> 0; DMG_SHOCK -> 0; DMG_BLAST with m_ArmorValue > 0 -> 0; at the end info +0x70 bit 2 -> 0. Spark: a head hit on
a helmet.

## Server blood (180a88a50, with m_bShouldBleed)

1. CEffectData: m_vOrigin = trace end, m_vStart = trace start, m_vNormal = -direction, m_hEntity = trace entity,
   m_flMagnitude = (float)(int) damage dealt.
2. excluded = 180a77f60(info, head, 1).
3. Head, damage > 0, m_bShouldSpark: impact_helmet_headshot.vpcf at the hit (trace +0x90 angles), PAS less excluded.
4. Blood level (vfn 0x538) by health left vs magnitude: not above it -> 7; else < 1 -> -1, < 12 -> 0, < 16 -> 3, < 22 ->
   4, < 31 -> 5, < 75 -> 6, else 7.
5. Head and spark and damage: magnitude 1.0.
6. TraceBleed (1803eee10): level -1, zero damage or no 0xc7 bit -> nothing; dead pawn takes one off vfn 0x5c8's count
   (none left -> nothing). Level 0: jitter 0.185, 3 traces; 3 / 4: 0.3, 3; 7: 0.15, 2; else 0.2, 2. Each: direction +
   three RandomFloat(-j, j) (+ a z offset) normalized, a line 172 u from the hit; hit -> 180cbb810: 0 Blood, 3 Bloodlvl2,
   4 Bloodlvl3, 5 Bloodlvl4, 6 Bloodlvl5, 7 Bloodlvl6 (else YellowBlood, not in decalgroups.vdata); miss -> next line
   200 u, z offset -0.35, the next hit's decal Bloodlvl2.
7. Level back to 0; DispatchEffect("csblood") to the PAS at the origin less excluded.

RandomFloat draws are the server's tier0 global stream.

## Client csblood (180d226c0)

Nothing during 180cb2100's camera or for an entity with +0x30 bit 7.

Someone else hit:
- a = normalize(origin - start), b = normalize(origin - victim abs origin), c = normalize(b x a), d = normalize(up x a),
  t = `(c.d) / (c.c)`, s = `clamp(powf(b.z, 10), 0, 1) * 0.5 + 0.5` (disassembly: [rbp-0x70] = b.z), e = normalize(`d -
  c t s`).
- System by magnitude: above 40 blood_impact_high, from 20 blood_impact_med, above 1 blood_impact_low, else
  blood_impact_friendly.
- CP0 the origin with VectorVectors(e)'s frame, CP1 the start, CP2 the origin facing -a, CP3 (1, 1, 1 friendly else 0).

Yourself hit (victim is the local pawn):
- Dead: blood_impact_localKillShot at origin + normal.
- Alive: g = view's flat forward, d = start - origin, `theta = atan2(-(g x d).z, -(g . d))`,
  `phi = -((theta + pi) * 57.29578) * pi / 180`, k = view forward . normalize(d).
  - k >= 0.9, k <= -0.8, or a localplayer hit within 0.2 s (18223f628) with k within 0.2: k > -0.8 or a rear hit within
    0.2 s -> blood_impact_localfrontsimple (k <= 0.899 or a front one within 0.2 s; all three clocks set) else
    _localfrontenemy (its clock), offset 0; else _localrearhit with offset (0, 0, -100) (shooter at most 128 u above or
    512 u or more away, else +100).
  - Otherwise _localplayer: u = clamp(-sin phi), v = clamp(cos phi), square to disc
    `(sqrt(u 2sqrt2 + (u^2 + 2 - v^2)) - sqrt((u^2 + 2 - v^2) - u 2sqrt2)) / 2 * 100`, the same for v,
    z = `(k / 2 + 0.5) * 100`.
- 180a3ce50: CP0 the offset with the normal's angles, CP1 (clamp(magnitude, 15, 65) twice, max(flag, magnitude 0)).

## Unread

- The PAS (taken as every client).
- 18093d760's rule (an attacker 180ad2a20 refuses).
- vfn 0x5c8's count for a dead pawn (taken as never empty).
