# CS2 grenades

server_20261105 (networksystem_20261015 for qangle_precise). CS2Fixes zombiereborn.cpp, weapons.cfg.example.

## CBaseCSGrenade (vtable 0x1818e7f18; every grenade class shares these slots)

| Slot | Address | What |
|---|---|---|
| ItemPostFrame 0xd00 | 1809c8710 | per command (below) |
| ItemBusyFrame 0xd08 | 180a0f050 | base |
| 0xd10 | 1809c8320 | the throw's think |
| Deploy 0xa18 | 1809b80b0 | |
| Holster 0xa20 | 180a041f0 | holster.md |
| PrimaryAttack 0xcf0 | 1809ccca0 | `jmp [vfn 0xda8](this, 0)` |
| SecondaryAttack 0xcf8 | 1809d0650 | freeze period (gamerules +0xd8) returns 0; else `jmp [vfn 0xda8](this, 1)` |
| PullPin 0xda8 | 1809b3bd0 | (this, secondary) |
| ThrowGrenade 0xdb8 | 1809d4a50 | |
| EmitGrenade 0xdd0 | | per class |
| throw velocity 0xc48 | 1809c0350 | vdata m_flThrowVelocity |
| activity finished | 1809cb940 | no direct callers |
| switch-away query | 1809ccb20 | (this, target) |

## Functions

| Address | What |
|---|---|
| 180b5ce80 | (w, mask): pawn buttons (vfn 0xb30 +0x58) & mask |
| 180b06e70 | weapon services post-think (fire-gate.md) |
| 180a276f0 | activity / clocks (draw activity 0x1b) |
| 1809fb560 | CCSWeaponBase::Deploy: both clocks now + m_flDeployDuration (1.0 for every grenade) not earlier, m_iShotsFired 0, m_bWaitForNoAttack 1, m_flNextAttack |
| 1813b8ef0 / 18017e2d0 | tick + fraction compare |
| 180460960 | Approach(target, value, speed) |
| 1809f7840 | set activity (throw 0xca) |
| 1809d3cd0 | StartGrenadeThrow |
| 18017dc70 | addss helper |
| 180ad2570 | jump window (pawn, extra) |
| 180a0f4b0 | CCSWeaponBase::ItemPostFrame (knife.md "The gate") |
| 180b23cc0 | SwitchToNextBestWeapon (services, weapon, 0) |
| 1803d9090 | life state |
| 1809b50c0 | vfn 0xa08: true for every weapon |
| 180b09ee0 | GetNextBestWeapon (services, current) |
| 1809f9ec0 | vfn 0xa00: an owner and vfn 0xa48 |
| 1802d42d0 | bot extra test |
| 180b7c520 | has a round: clip (vfn 0xac0) >= 1, else vfn 0xaf0(0) >= 1 |
| 1809b4980 | throw parameters, strength snap, then 1809b4ad0 |
| 1809b4ad0 | the throw's maths |
| 181470980 | AngleVectors (forward) |
| 180c2f3c0 | TraceShape |
| 180bf9270 | the pawn's entity id |
| 180c048b0 | hierarchy id |
| 180ac6340 | CCSPlayerPawn throw parameters (angles, eye, trace start, velocity, bool) out |
| 180b0a570 | weapon services vfn 0xd0: eye angles (vfn 0x5f0, 180b4f890) + aim punch |
| 180a43b90 | GetAimPunch (pawn +0xe50, doubled) |
| 18029f040 | vector add |
| 1803d6f50 | abs origin (node +0xc8) |
| 180158e30 | m_vecViewOffset (pawn +0x818) |
| 18015a2f0 | pawn vfn 0x2c8: WorldSpaceCenter |
| 1801575b0 | vfn 0x228: m_pCollision (+0x3d8) |
| 180156f30 | collision centre `(maxs + mins) x 0.5` (maxs.x + mins.x) |
| 18014cf50 | unrotated collision: `scale x c + abs origin` (180cf6440 / 180cf6430) |
| 1803d6fb0 | abs velocity |
| 180abc3f0 / 180ae66b0 | CheckJumpButton legacy / modern (movement.md) |
| 180ac4c00 | pawn vfn 0x138 after each move piece |
| 180ae9260 | view offset |
| 180ae4570 | save the jump pose |
| 1803a4810 / 1803a4760 / 1809b7110 / 1809b79e0 / 1809b6c50 | Create: HE / flashbang / molotov / smoke / decoy |
| 1809d0680 | SetDetonateTimerLength |
| 1800b2ca0 | registers molotov_throw_detonate_time |
| 18005f450 / 18005f4f0 | register sv_hegrenade_damage_multiplier / _radius_multiplier |
| 1809d2d80 | projectile Spawn (base) |
| 1803a8050, 1803a7f60, 1809d3170, 1809d33a0, 1809d3030 | Spawn vfn 0x48: HE, flashbang, molotov, smoke, decoy |
| 180d0e200 | SetCollisionGroup |
| 1809cc050 | PhysicsSimulate (vfn 0x720 of every projectile) |
| 180e904c0 | PhysicsToss |
| 180e8e9b0 | PhysicsAddGravityMove |
| 180e8f7d0 | PhysicsPushEntity |
| 180c2e7e0 | TraceEntity |
| 180e8f4d0 | PhysicsImpact (touches) |
| 180e8efa0 | ClipVelocity |
| 1809ce4b0 | ResolveFlyCollisionCustom |
| 1801ff2f0 / 18022f9e0 | bounce listener (normal, count + 1) |
| 180e8eb40 | PhysicsCheckVelocity (unread) |
| 1803e0100 | standable test (unread) |
| 180e8f1f0 | PhysicsCustom (calls vfn 0x720) |
| 1803d9e40 | PhysicsCustom's first call |
| 1803d95f0 | m_nActualMoveType (+0x2f5) |
| 180ae27b0 | living pawn's collision layers |
| 180ae28e0 | the other way (death) |
| 180cf1850, 180cf1540, 180cee5a0, 180cf16a0, 180cee390, 180cee420, 180ceffe0, 180cee540, 180cf1970, 180cf18d0, 180cf1a10, 180cf1730 | collision layer setters |
| 180957e50 (0x18095a421), 18023b580, 18024a860, 180237640, 180923fb0 | callers of 180ae27b0 (RestartRound, script Reset, 18024a860 flag clear, unnamed) |
| 180208400, 1802089a0 | other callers of 180ae28e0 |
| 1808c6250 | GetThrower (m_hThrower +0xaa8, else owner +0x3e4) |
| 1808d6480 | sets m_hThrower (after Create's spawn) |
| 180cec250 | spawner (class, origin, angles, r9 thrower) |
| 1803eb230 | SetLocalAngularVelocity |
| 1803ea1a0 | SetAbsAngles (-> node 180c26600, stored when a lane differs, 18014a300's ==) |
| 1803ea4a0 | SetAbsVelocity |
| 181472530 | AngleVectors (fwd, right / left, up) |
| 180b61330 / 180b77df0 | "thrown" anim graph tag |
| 181478260 | VMatrix from angles = 181478d90(out, origin 0x18177bf80 = 0, angles) |
| 1803d6de0 | GetAbsAngles |
| 1814738b0 | normalize |
| 180148890 | VectorNormalize |
| 181478230 | rotation about an axis (out, axis, degrees) via 1814719c0 |
| 181478690 | VMatrix product |
| 181478b30 | MatrixAngles |
| 18068c5e0 | scene node network fields (18068d451 registers m_angRotation) |
| 1800d4450 / 1800d3900 / 1800d3d90 | networksystem qangle_precise GetName / encode / decode (methods from 0x180274548) |
| 1803a4f10 | HE Detonate |
| 1808c2380 | CBaseGrenade::Detonate -> vfn 0x998 |
| 1809bcc90 | vfn 0x998 -> Explode |
| 1808c3200 | Explode |
| 1803a5420 | vfn 0x9f0: BaseGrenade.Explode, particle, RadiusDamage |
| 1803a5da0 | explosion particle |
| 180c034f0 | GetPointContents |
| 180df0300 | RadiusDamage -> gamerules vfn 0x1f8 |
| 0x180956070 -> 1809550b0 | gamerules vfn 0x1f8 (CCSGameRules vtable 0x1818c5450), with 0 |
| 180bdc700, 180ce3c10, 180926130 / 180927370, 18090a6b0 | RadiusDamage's sphere targets, BodyTarget, visibility, sources around corners (expf falloff) |
| 180a89230 | team damage |
| 1800c5da0 | registers ff_damage_reduction_grenade_self |
| 1809b3ee0 | Molotov BounceTouch |
| 1800b49e0 | registers weapon_molotov_maxdetonateslope |
| 1809b82e0 | Molotov Detonate (loop stopped at 1809b8b50) |
| 1809d5e00 | ground line / air burst (loop stopped at 1809d6065) |
| 1803536c0 | Inferno Start |
| 180345dc0 | CreateFire |
| 180f695d0 | pawn-style emit (this, out, name, 0, 0, 1, 0) |
| 1809b3e60 | molotov bounce sound vfn |
| 181029810 -> 181067ff0 (+0x260 name) -> 18054a2f0 | weapon vdata lookup |
| 1809aec60 | find shoot sound slot |
| 180c8b5a0 | filter minus the thrower's controller |
| 1807dfaa0 | client.dll: the client's twin of the throw sound |
| 180a2c3a0 | CSmokeGrenade EmitGrenade (logs `sv_throw_smokegrenade`) |
| 180a31b80 | deferred functor (vtable 0x18191a1a0 slot 0x10) -> Create |
| 1803ee6e0 / 1803eb9e0 | set think / SetNextThink |
| 1803ead30 / 180d0e560 | gravity / friction setters |
| 1809d4650 | smoke think (flight) |
| 180225130 | |v| sqrtss((z z + y y) + x x) |
| 1809b8bb0 | smoke Detonate (vfn 0x9a8) |
| 1809b4190 | voxel fill (+0xbc0) |
| 1809d4330 | waits for the fill job (1816a6940 false) |
| 1809d2780 | smoke pop |
| 1809b38e0 | resting angles (smoke, decoy; unread) |
| 1809b4090 | in the pop |
| 1809d47d0 | smoke fade think |
| 180b77050 | remap |
| 1809d47a0 | removal think |
| 1809cda40 | `smokegrenade_expired` |
| 1805b70a0 | think list |
| 180e900a0 | PhysicsRunThink |
| 180e90150 | from vfn 0x508 PhysicsSimulate -> 180e8f1f0 |
| 1809fcc00 | CDecoyGrenade EmitGrenade (logs `sv_throw_decoygrenade`) |
| 180c86620 | gear slot weapon (services, slot) |
| 1809d4390 | decoy rest check think |
| 18032b710 | bot manager add (115) |
| 1809c0760 | decoy shot |
| 18102cf10 -> 181067ff0 -> 18054a2f0 | decoy gun vdata lookup |
| 180f69780 | EmitSound |
| 180c864b0 | filter (ent, 0.8) |
| 180b06bb0 | record (.., 3) |

## Fields

| Offset | Field |
|---|---|
| grenade +0x1280 | m_bRedraw |
| +0x1281 | m_bIsHeldByPlayer |
| +0x1282 | m_bPinPulled |
| +0x1283 | m_bJumpThrow |
| +0x1284 | m_bThrowAnimating |
| +0x1288 | m_fThrowTime |
| +0x128c | m_flThrowStrength |
| +0x1290 | m_fDropTime |
| +0x1294 | m_fPinPullTime |
| +0x1298 | m_bJustPulledPin |
| +0x129c / +0x12a0 | m_nNextHoldTick / m_flNextHoldFrac |
| +0x12a4 | m_hSwitchToWeaponAfterThrow |
| weapon +0xefc | current activity |
| vdata +0x700 / +0x704 | gear slot (rifle 0, pistol 1, knife 2, grenades 3, C4 4) / position |
| vdata +0x820 / +0x830 | m_nDamage (HE 99) / m_flRange (350) |
| vdata +0x520 | CSWeaponType |
| vdata +0x728 | silencer type |
| vdata +0x738 | m_flCycleTime |
| vdata +0x4f8 | sound table (0x28-byte entries, name at +0x20) |
| services +0x48 / +0x50 | m_hMyWeapons count / handles |
| pawn +0xc98 -> controller +0x708 | current command (link +0x90; number +8) |
| pawn +0xe6a | female voice (JumpThrowF) |
| pawn +0xe48 / +0xe58 | radio counters |
| pawn +0xb10 | weapon services |
| pawn +0x1560 | jump stamp |
| pawn +0x1564 | jump pose saved |
| pawn +0x1568 / +0x1574 / +0x1580 / +0x158c | saved angles / eye / trace start / velocity |
| pawn +0x3e8, +0x1be | in 180ae27b0's tail (vfn 0x6c8(pawn, +0x3e8 & ~0x20), +0x1be = 0x101) |
| pawn +0x1004 / +0x1008 / +0x1014 / +0x1054 | m_nRagdollDamageBone / force / m_szRagdollDamageWeaponName (64) / m_bRagdollDamageHeadshot |
| pawn +0x1058..0x1060 | zeroed with the flag clear |
| svc +0x68c | jump stamp (movement services) |
| mv +0xd4 / +0xe0 | the piece's end |
| collision +0x18 / +0x28 | interacts-as / exclude |
| collision +0x3e / +0x3f | attribute group / attribute flags |
| collision +0x5a | & 4: owner id used |
| collision +0x5e / +0x5f | m_CollisionGroup / flags (|= 1) |
| projectile +0x3e4 | owner |
| +0x3f8 | elasticity |
| +0x480 | m_vecAngVelocity (not the spin) |
| +0x550 | = 1 at the smoke pop |
| +0xa48 | gates vfn 0xa10 |
| +0xa84 / +0xa90 | radius / damage |
| +0xaa8 | m_hThrower |
| +0xad0 / +0xadc | m_vInitialPosition / m_vInitialVelocity |
| +0xae8 | m_nBounces |
| +0xb08 | m_flSpawnTime |
| +0xb10 | m_vecOriginalSpawnLocation |
| +0xb1c | m_flLastBounceSoundTime |
| +0xb20 | m_vecGrenadeSpin (degrees / s about a world axis) |
| +0xb2c | m_vecLastHitSurfaceNormal |
| +0xb38 | m_nTicksAtZeroVelocity |
| +0xb3c | m_bHasEverHitEnemy |
| molotov +0xb40 / +0xb44..+0xb57 | m_bIsIncGrenade / flight loop handle (20 bytes) |
| smoke +0xb68 / +0xb6c | m_nSmokeEffectTickBegin / m_bDidSmokeEffect |
| smoke +0xb80 | m_vSmokeDetonationPos |
| smoke +0xbc0 / +0x2d70 / +0x2d78 | voxel grid / trail / trail ring |
| decoy +0xb5c / +0xb60 | m_shotsRemaining / m_fExpireTime |
| decoy +0xb68 / +0xb70 / +0xb74 | pattern / gun (item def index) / sound key |
| trace +0x84 / +0x90 | end / normal |
| gpGlobals +0x34 | frametime |

## Constants

| Value | What |
|---|---|
| 0x3ca66666 = 0.0203125 | strength approach speed |
| 0.1 (0x3dcccccd at 0x18178fdc8) | throw delay, jump-throw delay, drop time, strength snap window |
| 0.5 (0x18178057c) | strength snap target |
| 0x3c800000 = 0.015625 | tick interval |
| 0.2 (0x181784df8 at 180ac63ca) | jump window |
| 90 0x1817b2c54, 360 0x18179beac, -90 0x181813dbc, 10 0x181784e0c | pitch adjust |
| 0.9 (0x18178fde8), 15 (0x1817a4450), 750 (0x18179bebc) | throw velocity scale / min / max |
| 0.7 (0x1817ad5d4), 0.3 (0x18178fddc) | strength mix |
| 0x3c8efa35 | degrees -> radians |
| 12 (0x1817bfec8) | source z offset |
| 0x1821282a8 (+0x58) | sv_grenade_collision_sphere |
| ±2.02 (0x400147ae / 0x1818e9fb8) | throw trace box |
| 16 | throw trace length |
| 0x200003001 | projectile interacts-with: solid 0, window 12, passbullets 13, csgo_grenadeclip 33 |
| group 4, flags (& 0xc9) | 0x49 | throw trace |
| 1.25 (0x1817c98d0) | pawn velocity share |
| 36 / 27 | WorldSpaceCenter height standing / ducked |
| 0x182193bc0 (+0x58) | cvar: 0 -> vfn 0xaf8(0, -1, 0) before ThrowGrenade |
| (600, RandomInt(-1200, 1200), 0) | thrown angular velocity (drawn, dropped) |
| 1.5 s / 2.0 | HE / flashbang timer / molotov_throw_detonate_time |
| 0.4 (0x3ecccccd) / 0.2 (0x3e4ccccd) / 0.45 (0x3ee66666) | gravity / friction / elasticity |
| sv_hegrenade_damage_multiplier 1, sv_hegrenade_radius_multiplier 1 | |
| (-2, -2, -2)..(2, 2, 2); sv_grenade_collision_sphere_radius 2 | projectile box / sphere |
| group 16 | Projectile |
| 128 | substep rate |
| 0.98, flags 0x18000 | water velocity scale, water contents |
| 8 | ticks at zero velocity before stopping |
| 0.03125 | ClipVelocity epsilon |
| 10 DMG_CLUB | to a breakable; broken: velocity x0.4 |
| 0.9 / 2.0 | elasticity clamp / overbounce |
| 0.7 / 0.1 / 400 / 96000 / 0.5 | wall / floor tests |
| 21 | max bounces |
| 0x18177bf90 / 0x18177bf80 | zero vectors |
| -20 (0x1817bc144) | spawn roll offset |
| 1500 (0x1817b2c94), 0x1817805b0 | spin scale, sign mask |
| 0x18176a598 / 0x18176a4a8 | V_sincosf / V_atan2f imports |
| 0x1817d0e90 | pi / 180 |
| 0.995 (0x18178fdf0) | spin decay |
| 1e-17 (0x181780574) / 1e17 (0x181780590) | normalize bounds |
| 0x181784e80 | abs mask |
| 1.0 (0x181780580), 0.001 (0x181784de8) | d == 1 -> spin.x + 0.001 |
| 0.03 (0x1817b6568) | tumble pull |
| 57.2957764 (0x1817bfedc) | radians -> degrees |
| RandomFloat(4, 8): IAT 0x18176b218, bounds 0x18179be70 / 0x181780588 | bounce spin |
| "gameSceneNodeStepSimulationAnglesSerializer" 0x181832bf8 (+0x68), "qangle_precise" 0x181796878 (+0x70), name 0x180238178 | m_angRotation wire |
| DMG_BLAST 0x40 | HE |
| 512 | water surface line |
| m_flArmorRatio 1.2 | HE |
| ff_damage_reduction_grenade_self 1 | |
| weapon_molotov_maxdetonateslope 30 | |
| +10 / -128, 0xc3001 | molotov ground line |
| inferno_damage 40, inferno_damage_timer 0.2, inferno_flame_lifetime 7, _incendiary 5.5, inferno_max_range 150, inferno_max_flames 16, inferno_flame_spacing 42, inferno_initial_spawn_interval 0.02, inferno_per_flame_spawn_duration 3, inferno_child_spawn_interval_multiplier 0.1, inferno_max_child_spawn_interval 0.5, inferno_spawn_angle 45, inferno_child_spawn_max_depth 4 | inferno cvars |
| 200 / 300 | molotov damage / radius |
| IncGrenade.Throw.Loop 0x1818e8e98, Molotov.Throw.Loop 0x1818e8eb0 | flight loops (Molotov 0.7, incendiary 0.5; self_destruct_time 8 s, child Molotov.ThrowFire) |
| IncGrenade.Bounce 0x1818e8ee8, Molotov.Bounce 0x1818e8f00 | |
| 0.8 | throw-sound filter attenuation |
| 100 | smoke +0xa90 |
| 16, 20 u | smoke trail positions, spacing |
| 1.188 (0x3f981062 at 0x1818e9f58) | smoke min age |
| 1000 | hostages radius at the pop |
| 12.5 / 17.05 (0x41886666) / 19 / 21.05 / 0.37 s | smoke fade start / end / flag / removal / Scorch decal (line 0xc3001 +2 to -64) |
| 2.0 / 25 / 25 x 3.5 | decoy think delay / damage / radius |
| 181e0ef48 / 181e0f110 | cached weapon_hkp2000 / weapon_glock |
| 181e0e7e0 | decoy pattern table (6 x 24 bytes) |
| 2 / 9 | decoy sound key: WEAPON_SOUND_SINGLE / silenced |
| 0.2 / 14 | decoy rest speed / lifetime |
| CBaseCSGrenadeProjectile vtables | HE 0x1817c8c68, flashbang 0x1817c80a8, molotov 0x1818e74d0, smoke 0x1818e8f58, decoy 0x1818e5e00 |

## Per command

The post-think runs ItemPostFrame, then ItemBusyFrame while curtime < m_flNextAttack, else vfn 0xd10. Curtime is the
command's tick / 64 (f32), fraction 0.

- Deploy: m_bRedraw 0, m_bIsHeldByPlayer 1, m_bThrowAnimating 0, m_bPinPulled 0, m_fThrowTime 0, m_bJumpThrow 0,
  m_hSwitchToWeaponAfterThrow -1; with ammo (vfn 0xaf0(0) > 0) the draw and 1809fb560; else dropped.
- ItemPostFrame (a pawn first):
  1. m_bPinPulled and attack 1 or 2 held, now not before (m_nNextHoldTick, m_flNextHoldFrac): target 0.5, attack 1
     -> 1.0, attack 2 -> target - 0.5 (1 / 0 / both 0.5); m_bJustPulledPin 0: `strength = Approach(target, strength,
     0.0203125)` (`target - value > speed` -> value + speed, `-speed > target - value` -> value - speed, else target);
     m_bJustPulledPin 1: strength = target, flag 0; m_nNextHoldTick + 1.
  2. m_bPinPulled and neither button: activity 0xca, StartGrenadeThrow, m_bPinPulled 0, weapon_fire; return.
  3. m_bRedraw 0: CCSWeaponBase::ItemPostFrame (knife.md "The gate"): attack 1 and the primary clock -> the primary
     branch (freeze period, m_iShotsFired >= 1 without full auto, m_bWaitForNoAttack refuse) -> PrimaryAttack; else
     attack 2 and the secondary clock -> SecondaryAttack; else (no attack button) m_bWaitForNoAttack 0,
     m_iShotsFired 0. With the pin out it runs too: PullPin refuses.
- PullPin: m_bIsHeldByPlayer, m_bPinPulled 0, not `0 < m_fThrowTime`, a pawn, ammo: strength = secondary ? 0 : 1,
  activity 200, m_bPinPulled 1, m_nNextHoldTick = tick + 1, m_flNextHoldFrac = fraction, m_fPinPullTime = curtime,
  m_bJustPulledPin 1. No pin time: a release on the next command throws.
- StartGrenadeThrow: m_fThrowTime = curtime + 0.1; a late command (link +0x90 non-null, usercmd.md 3): m_fThrowTime -
  (link number +8 - its number +8) x 0.015625 (cvtdq2ps, mulss); curtime > m_fThrowTime -> = curtime.
  180ad2570(pawn, 0.1) -> m_bJumpThrow 1, BaseGrenade.JumpThrowM / F. m_bThrowAnimating 1; the throw sound.
- vfn 0xd10: m_fDropTime set and `curtime - it < 0.1`: animation event, return (else cleared); `curtime > m_fThrowTime`
  (strict, `0 < m_fThrowTime`): 180ad2570(pawn, 0.1) and m_bJumpThrow 0 -> m_fThrowTime = curtime + 0.1,
  m_bJumpThrow 1, jump-throw sound, return; else ThrowGrenade, then m_hSwitchToWeaponAfterThrow via services vfn 0xf0
  when set. Not throwing, m_bIsHeldByPlayer 0, m_bThrowAnimating 0: m_hSwitchToWeaponAfterThrow live -> Weapon_Switch
  to it; else 180b23cc0(services, this, 0). The grenade leaves 7 ticks after the release (release + 0.1 = 6.4 ticks;
  the first command past it).
- ThrowGrenade: 1809b4980 (last argument 0), NaN axes 0, EmitGrenade with angles (0, 0, 0) and angular velocity (600,
  RandomInt(-1200, 1200), 0) (the global stream; the value dropped), m_bRedraw 1, m_bIsHeldByPlayer 0, m_fThrowTime 0,
  radio 180a4be70 / 180239eb0, `grenade_thrown`.
- 1809cb940: activity 200 -> 0xc9; 0xca -> m_bThrowAnimating 0, draw 0x1b; else CCSWeaponBase's (180a1c800).
- 1809ccb20: not throw-animating -> true; target == this and vfn 0xaa0(0) false -> false; else
  m_hSwitchToWeaponAfterThrow = target, return `!m_bIsHeldByPlayer`.
- 180b23cc0: nothing for life state 1 or 2; current's vfn 0xa08 else nothing; 180b09ee0; a different result -> Weapon_Switch.
- 180b09ee0: m_hMyWeapons in order, each live, vfn 0xa00, not the current ; the first taken
  whatever its ammo (a bot, pawn vfn 0xc20, also 1802d42d0); a later one replaces it when its gear slot is lower and it has a round, or same gear slot and lower
  position (no ammo test). So: the rifle with a round, else the pistol, else the knife.

## The throw (1809b4980, 1809b4ad0)

- 1809b4980: 180ac6340; strength snapped to 0.5 when `0.1 >= |s - 0.5|` (f32 comiss at 1809b4a11; NaN keeps s);
  vfn 0xc48; 1809b4ad0.
- 1809b4ad0:
  - pitch: `p > 90` -> p - 360, else `-90 > p` -> p + 360; `p = p - ((90 - |p|) x 10) / 90`, written back;
  - `v = throwVelocity x 0.9`; `15 > v` -> 15, else minss(750, v); strength `0 > s` -> 0, else minss(1, s);
    `speed = (s x 0.7 + 0.3) x v`;
  - `fwd` = AngleVectors 181470980 of (pitch, yaw): yaw x 0x3c8efa35 into V_sincosf first, then pitch; `(cy cp, sy cp, -sp)`;
  - `src = (eye.x + 0, eye.y + 0, (s x 12 - 12) + eye.z)`, written back into the eye;
  - sphere cvar 0: box ±2.02 traced from the trace start to `(fwd.x x 16 + src.x, fwd.y x 16 + src.y, fwd.z x 16 + src.z)`,
    interacts-with 0x200003001, group 4, flags (& 0xc9) | 0x49, entity ids (pawn, its owner +0x3e4 when collision +0x5a
    & 4 clear), hierarchy id; `src = trace end (+0x84)` unconditionally. Sphere cvar on: no trace;
  - `vel = fwd x speed + pawnVelocity x 1.25`.
- Checked natively against server.dll (AngleVectors and 1809b4ad0, both sphere modes): 0 differences. Installed build
  (server 2026-11-12) identical but relocated: 1809b4ad0 -> 0x1809ad160, 180ac6340 -> 0x180abeb20, 1809c8710 ->
  0x1809c0da0, 181470980 -> 0x18145fdd0.
- 180ac6340: plain: angles = 180b0a570; eye = abs origin + m_vecViewOffset; trace start = WorldSpaceCenter (origin +
  (0, 0, hull height / 2); no m_pCollision: the abs origin); velocity = abs velocity. The jump's: pawn +0x1564 set and,
  with the last argument 0, `0 < curtime - pawn+0x1560 <= 0.2`: the saved +0x1568 / +0x1574 / +0x1580 / +0x158c (returns 1).

## The jump throw

- CheckJumpButton sets `svc+0x68c = (curtime - frametime) + 0.1`, copies it to pawn +0x1560, clears pawn +0x1564; the
  step is cut at the stamp (movement.md).
- 180ac4c00 after each piece: SetAbsOrigin / SetAbsVelocity from mv, view offset, then with svc+0x68c > 0 and the
  piece's end not before it: 180ae4570: +0x1564 = 1, +0x1568 = vfn 0xd0 angles, +0x1574 eye, +0x1580 vfn 0x2c8,
  +0x158c abs velocity; svc+0x68c = 0. (+0x1568 / +0x1580 are as here; the throw's reader settles it.)
- 180ad2570: `d = (curtime + extra) - pawn+0x1560`, true when `d > 0` and `0.2 >= d`. So a release within (jump,
  jump + 0.2] sets m_bJumpThrow (StartGrenadeThrow), and vfn 0xd10 delays a throw due inside that window without
  m_bJumpThrow by 0.1.
- A throw 0.1 to 0.3 s after the jump takes the pose at exactly jump + 0.1 s. UNSETTLED: the eye angles inside the
  movement (vfn 0x5f0 at 180ae4570) taken as that command's view, aim punch at the command's tick.
- Nothing in the throw path reads a sub-tick time; only the jump's pose is sub-tick.

## The projectile's flight

- Create: SetDetonateTimerLength; gravity, friction, elasticity; HE damage = m_nDamage x multiplier, radius = m_flRange
  x multiplier.
- Spawn 1809d2d80: box or sphere, interacts-with 0x200003001, group 16, movetype CUSTOM.
- PhysicsSimulate: `n = (int)(frametime * 128)`, one substep when not whole; n - 1 substeps of 1/128 s and a last of
  what's left (two at 64 tick); PhysicsToss each, velocity x0.98 in water; the spin step; m_nTicksAtZeroVelocity:
  |v| == 0 -> + 1, more than 8: velocity 0, movetype none, vfn 0xa10 (+0xa48 clear), next think now; else 0. Only
  while m_nActualMoveType != 0: SetMoveType(4 FLYGRAVITY, 2) and vfn 0xa18 first, SetMoveType(10 CUSTOM, 0) at the
  end unless left none.
- PhysicsToss: ground cleared when vz > 0 or no ground; on ground with zero velocity: return; PhysicsCheckVelocity;
  PhysicsAddGravityMove (`nz = vz - ft * sv_gravity * gravity`, `move.z = ((vz + nz) * 0.5 + basevz) * ft`);
  PhysicsPushEntity; start solid -> velocity 0; a hit -> PerformFlyCollisionResolution -> ResolveFlyCollisionCustom.
- PhysicsPushEntity: TraceEntity origin -> origin + move; origin = end unless fraction 0; hit entity gets PhysicsImpact.
- ClipVelocity: `b = -((v.z n.z + v.y n.y) + v.x n.x) * overbounce`, at least 0, `+ 0.03125`; `out = b * n + v`.
- ResolveFlyCollisionCustom:
  1. A breakable (func_breakable / _surf, prop_physics_multiplayer or prop_dynamic with health) takes 10 DMG_CLUB;
     broken -> velocity x0.4, done.
  2. `e = clamp(elasticity, 0, 0.9)`; `v = ClipVelocity(vel, n, 2.0) * e`; a player (vfn 0x558) gets its normal from its
     centre (a living player is never hit: "Players and the projectile").
  3. Wall (`n.z <= 0.7 && (n.z <= 0.1 || |v|^2 >= 400)`): velocity = v, push `v * (1 - frac) * ft`, and if it stops
     before half, again with the remainder clipped off the new normal.
  4. Floor: over 96000, `dot = normalize(v) . n`, above 0.5 `v *= (1 - dot) + 0.5`; under 400: ground, velocity 0;
     else push `v * (1 - frac) * ft`.
  5. Bounce sound at most every 0.1 s, `grenade_bounce`; |v| > 0 a new spin, else SetMoveType(0, 0) (1809cf55f: no
     vfn 0xa10); vfn 0xa00 (then the count, 1809cf56c..); 1801ff2f0 / 18022f9e0; m_nBounces < 21: + 1, else velocity 0, movetype none, vfn 0xa10,
     next think. m_vecLastHitSurfaceNormal = trace normal, or for a player the direction from its centre to the end.
- Rubikon registers server.dll's csgo_* layers at bits 31..40: a map's csgo_grenadeclip is bit 33.

## Players and the projectile

A grenade flies through living players: their collision carries no layer of 0x200003001.
- 180ae27b0 (with a live controller): collision +0x5f |= 1, attribute flags +0x3f |= 7, +0x3f &= 0xb7,
  interacts-as |= player (0x40000), &= ~solid (1), exclude &= ~(player | playerclip) (0x40010); then vfn 0x6c8,
  +0x1be = 0x101, 180ceffe0.
- 180ae28e0 (18024a860 with its flag set: the death): interacts-as |= solid, &= ~player, exclude |= 0x40010, same tail.
- SetCollisionGroup(collision, group): +0x5e, attribute group +0x3e; group 5 (debris): interacts-as &= ~0x20000,
  |= 0x100000; any other but 2 and 14: &= ~0x100000, |= 0x20000 (touchall); 2 and 14 leave the layers.
- So a living pawn interacts as player (+ touchall under group 8), not solid: no layer of the grenade's filter.
  ResolveFlyCollisionCustom's player branch (vfn 0x558) is for what else answers it.

## The spin

- Create ignores its angular velocity argument (all classes; the molotov inlines the spawner), so ThrowGrenade's and
  the death drop's (600, RandomInt(-1200, 1200), 0) only spend a draw of the global stream; m_vecAngVelocity is
  not the spin (CUSTOM never integrates it; PhysicsCustom zeroes it). The constructor (~1803a4300, 1803a43af) zeroes it.
- Spawn (1809d2f1f..1809d2fe4), with a thrower: SetLocalAngularVelocity(0); thrower eye angles, roll `+ -20` ->
  SetAbsAngles; AngleVectors(eye, null, &left, null); `spin = (-l.x x 1500, -l.y x 1500, -l.z x 1500)` (xorps then
  mulss). Then the "thrown" tag.
- PhysicsSimulate after the tosses (1809cc2bb..1809cc97d):
  1. M = VMatrix of GetAbsAngles (forward / left / up columns, translation 0, row (0, 0, 0, 1)).
  2. spin x 0.995 (x, z, y). n = normalize(spin) (`len = sqrt((z z + y y) + x x)`; outside 1e-17..1e17 (comiss / ja,
     NaN goes on): 0 when len == 0, else 1814738b0; else x (1 / len)).
  3. `d = |(n.z m22 + n.y m12) + m02 n.x|`; `d > 0.1` (comiss / jbe): d == 1.0 -> spin.x + 0.001; s = |spin|;
     u = up column normalized; `plane = (u.z m23 + u.y m13) + u.x m03` (0); `t = ((u.z sp.z + u.y sp.y) + u.x sp.x) - plane`;
     `p = (sp.x - u.x t, sp.y - u.y t, sp.z - u.z t)`; pn = normalize(p), n = normalize(spin);
     `b = (pn - n) x 0.03 + n` per lane; `spin = normalize(b) x s`.
  4. axis = normalize(spin); R = 181478230(axis, |spin| x frametime); angles = 181478b30(181478690(R, M)).
     181478690: `((a_i0 b_0j + a_i1 b_1j) + a_i2 b_2j) + a_i3 b_3j`. 181478b30: `xy = sqrt(m00 m00 + m10 m10)` over
     0.001: yaw atan2(m10, m00), pitch atan2(-m20, xy), roll atan2(m21, m22); else yaw atan2(-m01, m11), roll 0;
     each x 57.2957764.
  5. PhysicsCustom sets abs angles, velocity, angular velocity (0); moves only when the origin differs (never here).
- Bounce spin (1809cf191..1809cf555), |v| after the bounce > 0: v = velocity at entry; d = normalize(v);
  `k = ((n.z d.z + n.y d.y) + n.x d.x)` doubled (addss k, k), n = m_vecLastHitSurfaceNormal;
  `e = (d.x - k n.x, d.y - k n.y, d.z - k n.z)`; en = normalize(e);
  `spin = (-(en.z d.y - en.y d.z), -(en.x d.z - d.x en.z), -(d.x en.y - en.x d.y))`, then x `(RandomFloat(4, 8) x |v|)`
  (global stream; `|v| = sqrt((z z + y y) + x x)`).
- Checked natively: 181472530, 1809cc050 (with and without the tumble, the |d| == 1 case), 1809ce4b0 (wall branch): 0
  differences.
- Nothing in the flight reads the angles or the spin (axis-aligned box, SOLID_BBOX).
- m_angRotation wire: qangle_precise writes three bits (component |v| >= threshold +0x34), then each set component
  wrapped to [-180, 180] (`floor(v / 360 + 0.5)`, clamped) as `(uint)((double)(v + 180) * scale + 0.5)` (scale +0x38,
  a double) in +0x2c bits. TODO: bit count, threshold, scale are set from the field's metadata; no reference found
  (methods reached only through the vtable).

## Detonations

- HE (1803a4f10): `hegrenade_detonate`, 1808c2380 -> 1809bcc90 -> Explode: CTakeDamageInfo(radius +0xa84, damage
  +0xa90, DMG_BLAST); 1803a5420: BaseGrenade.Explode, particle (in water 0x18000 explosion_basic_water, moved to the
  surface by a line up / down 512 u; else _hegrenade_brief / _hegrenade_dirt / _hegrenade_snow / explosion_basic),
  RadiusDamage. Armor at m_flArmorRatio 1.2.
- Team damage (180a89230): teammates blocked with friendly fire off; own grenade x ff_damage_reduction_grenade_self.
- Molotov BounceTouch: ignores its thrower, func_breakable / _surf, func_ladder; `cos(weapon_molotov_maxdetonateslope)
  <= normal.z` -> Detonate (UNSETTLED: tier0's V_cosf).
- Molotov Detonate: `molotov_detonate`; start-solid check; 1809d5e00: a line +10 to -128 (0xc3001): nothing ->
  Molotov.StartFailed / IncGrenade.StartFailed, air explosion (explosion_molotov_air / explosion_incend_air), no fire;
  else the inferno at the ground point along the throw velocity (|vz|).
- Inferno Start: Molotov.Start / IncGrenade.Start, Inferno.Loop, `inferno_startburn`, CreateFire (inferno.md).
- Flashbang: `flashbang_detonate`, Flashbang.Explode, explosion_flashbang (flashbang.md).

## Fire grenades' sounds; the throw's sound slot

- Molotov Create (at 1809b786a, after damage / radius and think): by m_bIsIncGrenade, 180f695d0 of
  IncGrenade.Throw.Loop else Molotov.Throw.Loop, positional on the projectile; handle at +0xb44. Stopped at Detonate
  (1809b8b50) and the air burst (1809d6065).
- Bounce vfn 1809b3e60: IncGrenade.Bounce / Molotov.Bounce, same emit.
- StartGrenadeThrow's sound (1809d3fc4..1809d4156): vdata m_aShootSounds slot 2 (WEAPON_SOUND_SINGLE), 0.8 filter
  minus the thrower's controller, when not empty. No grenade's vdata has one: nothing plays. items_game's
  `sound_single_shot` (Flashbang.Throw, HEGrenade.Throw, IncGrenade.Throw) is read by no code (player-sounds.md).

## Smoke (CSmokeGrenadeProjectile vtable 0x1818e8f58)

- Create 1809b79e0: `smokegrenade_projectile`; think 1809d4650 from now; velocity; +0xa90 = 100; gravity, friction,
  elasticity; +0xb6c 0, +0xb68 0; colour from vdata / a cvar by team; group 16. No detonate timer. m_flSpawnTime =
  curtime at Spawn (its only writer).
- Think 1809d4650 (every tick): trail (visual); `0.1 >= |v|` (comiss, NaN fails) and `curtime - m_flSpawnTime >= 1.188`
  -> Detonate; else next think now.
- Detonate 1809b8bb0: m_vSmokeDetonationPos = origin; voxel fill (from that point, the trail, a time from +0xb68);
  think 1809d4330 every tick; once the job is done 1809d2780: listeners, 1809b38e0, m_nSmokeEffectTickBegin = tick,
  1809b4090, hostages within 1000, `smokegrenade_detonate` (userid, entityid, x / y / z), the detonation record,
  m_bDidSmokeEffect 1, BaseSmokeEffect.Sound, +0x550 = 1, movetype none, think 1809d47d0.
- 1809d47d0: `age = (tick - m_nSmokeEffectTickBegin) x 0.015625`; from 12.5 s alpha = `remap(age, 12.5, 17.05, 1, 0) x
  255`, a flag at 19; at 21.05 s alpha 0 and think 1809d47a0 a second on (removal, `smokegrenade_expired`). At 0.37 s
  a Scorch decal. Volume and sight blocking: smoke.md.
- Think order against the flight in a frame: think list 1805b70a0 runs PhysicsRunThink; where vfn 0x508 -> 180e90150
  -> 180e8f1f0 -> vfn 0x720 runs is unread.

## Decoy (CDecoyProjectile vtable 0x1818e5e00)

- Create 1809b6c50: `decoy_projectile`; think 1809d4390 at curtime + 2.0; damage 25, radius 25 x 3.5; gravity,
  friction, elasticity. Gun: the thrower's slot 0 weapon, else slot 1; neither: weapon_hkp2000 for team 3, else
  weapon_glock (team: the thrower +0x344). A slot weapon whose +0x68 byte is 0 leaves 0xffff. Sound key 2, or 9 when the gun's vdata +0x728 is set
  and vfn 0xd90 (silencer on) says so. Pattern: the 181e0e7e0 entry whose first int equals the gun's CSWeaponType, else
  the first:

  | type | shots (+4..+8) | added between a burst's shots (+0xc) | pause between bursts (+0x10..+0x14) |
  |---|---|---|---|
  | 1 pistol | 1..3 | 0..0.3 | 0.5..4.0 |
  | 2 SMG | 1..5 | 0 | 0.5..4.0 |
  | 3 rifle | 1..3 | 0..0.5 | 0.5..4.0 |
  | 4 shotgun | 1..3 | 0 | 0.5..4.0 |
  | 5 sniper | 1..3 | 0..0.5 | 0.5..4.0 |
  | 6 machine gun | 6..20 | 0 | 0.5..4.0 |

- 1809d4390: `|v| <= 0.2` (comiss / jbe: NaN passes) -> 1809b38e0, `decoy_started` (x / y / z), m_shotsRemaining 0,
  m_fExpireTime = curtime + 14, think 1809c0760 set, 18032b710(115), 1809c0760 run at once; else again at curtime + 0.2.
- 1809c0760: m_shotsRemaining < 1 -> RandomInt(+4, +8); the gun's sound by key -> EmitSound at the origin, filter
  180c864b0(ent, 0.8), volume 1.0, pitch 100; weapon_decoy_ground_effect_shot.vpcf at the origin with the decoy's
  angles; `decoy_firing` (userid, entityid, x, y, z); m_shotsRemaining - 1. Shots left -> next think
  `(curtime + m_flCycleTime) + RandomFloat(0, +0xc)`; none left and curtime >= m_fExpireTime -> `decoy_detonate`, a
  record (180b06bb0(.., 3): origin, +0xad0), 1808c2380, UTIL_Remove; none left before -> `(curtime + cycle) +
  RandomFloat(+0x10, +0x14)`.

## CS2Fixes ZR

- Napalm (zr:1450-1459): an HE's damage to a zombie from a human: IgnitePawn for `clamp(damage / 50 * 5, 0, 5)` s with
  DMG_FALL (silent), the thrower as attacker.
- Knockback (zr:1015-1032): `normalize(victim - projectile + (0, 0, 36))`, z 0 for the inferno, x `(int)damage x
  zr_knockback_scale x weapons.cfg` (hegrenade 3.0, inferno 5.0).
- weapons.cfg.example: flashbang, smokegrenade, decoy disabled; HE, molotov, incgrenade enabled (CanAcquire zr:1481).

## Unread

- PhysicsCheckVelocity (180e8eb40: taken as CS:GO's clamp), base velocity / FL_CONVEYOR's 0.3, the standable test
  1803e0100 and two class casts in ResolveFlyCollisionCustom (taken as standable), the water level.
- PhysicsCustom 180e8f1f0: 1803d9e40, ground cleared when vz > 0 or ground (vfn 0x668) not standable, vfn 0x720, the
  angles / velocity / origin set back.
- V_cosf for the molotov slope.
- The throw's clip length on the weapon graph (when the switch after the throw happens); m_hMyWeapons' order.
- A pawn's interacts-as bits before 180ae27b0; whether a dead pawn's solid layer meets anything; team bits 31 / 32.
- 1809b38e0 (smoke / decoy resting angles); decoy 180c864b0's filter, 180b06bb0's record, the slot weapon +0x68 test.
- The inferno's spread rule (CInferno::Think / CreateFire not read), the flames' lifetimes and volume.
- No capture of a lineup against CS2 itself: retail (server 2026-11-12) has no `sv_throw_*` commands (development
  only: "Unknown command"), and bots on a local de_dust2 (bot_loadout with grenades, sv_bot_buy_grenade_chance 100)
  threw nothing in three rounds.
