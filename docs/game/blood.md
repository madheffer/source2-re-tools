# A player's blood

Read 2026-11-16, session "predict-hit-fx". server_20261105.dll, client_20261015.dll (ReVa). The port:
web/server/cs2web/combat/blood.js, web/src/cs2web/client/fx/blood.js, the events `blood` / `bspark` / `bdecal`
(snapshot-events.js codes 9 / 10 / 11), the assets from `lasers-bake --impacts` (ze-fx: the systems below, the decal
groups Blood / Bloodlvl2 .. Bloodlvl6).

## 1. Whether a hit bleeds: the hit group step 180a89430

CTakeDamageInfo m_bShouldBleed (+0x64) and m_bShouldSpark (+0x65) (server schema; the ctor 180fce950 zeroes both) are
set by the hit group step (when the info has a trace): bleed starts 1; an attacker player that 180ad2a20 (victim,
attacker controller) refuses takes 18093d760(gamerules)'s answer; m_bGunGameImmunity (+0x15a8) -> 0; damage bit 0x200
-> 0; bit 0x100 (DMG_SHOCK) -> 0; DMG_BLAST on armor (m_ArmorValue > 0) -> 0; at the end info +0x70 bit 2 -> 0. Spark:
a head hit on a helmet. (180a89a19 / 180a89a1d store them.)

## 2. The server's blood: the damage services' post 180a94400 -> 180a88a50

Before the hit's sounds (180a95310: player-sounds.md), with m_bShouldBleed:
- CEffectData: m_vOrigin = the trace's end (+0x84), m_vStart = its start (+0x78), m_vNormal = the info's direction
  (+0x2c) negated, m_hEntity = the trace's entity, m_flMagnitude = (float)(int) the damage dealt (the result's +0x20).
- excluded = 180a77f60(info, head, 1) (damage-prediction.md 9).
- head, damage > 0 and m_bShouldSpark: impact_helmet_headshot.vpcf at the hit (the trace +0x90's angles) to the PAS of
  the hit less `excluded` (180c4f310).
- the pawn's blood level (vfn 0x538) by the health left (180cf7020) against the magnitude: not above it -> 7; else < 1
  -> -1, < 12 -> 0, < 16 -> 3, < 22 -> 4, < 31 -> 5, < 75 -> 6, else 7.
- head and spark and damage: the magnitude 1.0.
- **TraceBleed 1803eee10(pawn, the damage as it was, the direction, the trace, the type)**: the level (vfn 0x530) -1, a
  zero damage or no 0xc7 bit in the type -> nothing; a dead pawn takes one off a count (vfn 0x5c8; none left ->
  nothing). Level 0: jitter 0.185, 3 traces; 3 / 4: 0.3, 3; 7: 0.15, 2; else 0.2, 2. Each: the direction + three
  RandomFloat(-j, j) (+ a z offset) normalized, a line from the hit 172 u along it (180250e50: interacts 0x1001, group
  3); a hit -> **180cbb810 UTIL_BloodDecalTrace(trace, level)**: 0 Blood, 3 Bloodlvl2, 4 Bloodlvl3, 5 Bloodlvl4, 6
  Bloodlvl5, 7 Bloodlvl6 (else YellowBlood, which decalgroups.vdata doesn't have); a miss -> the next line 200 u, z
  offset -0.35, and the next hit's decal Bloodlvl2.
- the level back to 0; **DispatchEffect("csblood")** (1811190a0) to the PAS at the origin less `excluded`.

## 3. The client's csblood: fx_cs_blood.cpp 180d226c0 (from the effect's callback 180d1e3a0)

(start, origin, entity, normal, magnitude) = CEffectData +0x14, +8, +0x38, +0x20, +0x44. Nothing during the end-of-match
or team-select camera (180cb2100) or for an entity with flag bit 7 (+0x30). The launch-option flag 180aca8d0 (unset).
- **Someone else hit**: a = normalize(origin - start), b = normalize(origin - the victim's abs origin), c =
  normalize(b x a), d = normalize(up x a), t = (c.d) / (c.c), s = clamp(powf(b.z, 10), 0, 1) x 0.5 + 0.5 (the powf's
  arguments from the disassembly: [rbp-0x70] = b.z, 10.0 at 0x181ad0f70), e = normalize(d - c t s). The system by
  magnitude against damage_impact_heavy 40 ("Damage ABOVE ...") and damage_impact_medium 20 ("Damage BELOW ..."):
  above 40 blood_impact_high, from 20 blood_impact_med, above 1 blood_impact_low, else blood_impact_friendly. CP0 the
  origin with VectorVectors(e)'s frame, CP1 the start, CP2 the origin facing -a, CP3 (1, 1, 1 for friendly else 0).
- **Yourself hit** (the victim is the local pawn): dead -> blood_impact_localKillShot at origin + normal; alive: g = the
  view's flat forward, d = start - origin, theta = atan2(-(g x d).z, -(g . d)), phi = -((theta + pi) x 57.29578) x pi /
  180, k = the view's forward . normalize(d):
  - k >= 0.9, k <= -0.8, or a localplayer hit within 0.2 s (18223f628) whose k is within 0.2: k > -0.8 or a rear hit
    within 0.2 s -> blood_impact_localfrontsimple (k <= 0.899 or a front one within 0.2 s; all three clocks set) else
    _localfrontenemy (its clock), offset 0; else _localrearhit with offset (0, 0, -100) (the shooter at most 128 u above
    you or 512 u or more away, else +100).
  - otherwise _localplayer: u = clamp(-sin phi), v = clamp(cos phi), the square to the disc
    ((sqrt(u 2sqrt2 + (u^2 + 2 - v^2)) - sqrt((u^2 + 2 - v^2) - u 2sqrt2)) / 2 x 100, the same for v), z = (k / 2 + 0.5) x 100.
  - DispatchParticleEffect (180a3ce50): CP0 the offset with the normal's angles, CP1 (clamp(magnitude, 15, 65) twice,
    max(flag, magnitude 0)).

## The port

- server/cs2web/combat/blood.js `bleed` from combat.js hurtPlayer (a hit with a trace: bullets from their segment's start,
  the knife from the eye, RadiusDamage from its source to the target's BodyTarget spot), before the pain sounds.
  RandomFloat's draws are the server's Math.random (tier0's global stream is the server's own on CS2: no client can
  follow it either way).
- client/fx/blood.js plays csblood / the sparks / the decals through client/fx/bullet-fx.js (its particle pool and
  decals); `!toggledecals` turns the decals off as the bullet holes.
- On a CS2Fixes server (ZE) the blood on other players follows `!blood` (ours, client-commands.js bloodMode): off by
  default (no csblood particles, no decals), on: a cheap blood, not CS2's (blood.js CHEAP). The official modes draw
  csblood as above, every hit; the effect's children nothing of which is drawn (the ground decals'
  C_OP_RenderProjected, not ported) aren't simulated (fx/effects.js unseenLeaf: the same frame).

Unread: the PAS (every client gets the events, as the other sounds); 18093d760's rule (an attacker 180ad2a20
refuses); vfn 0x5c8's count for a dead pawn (taken as never empty).
