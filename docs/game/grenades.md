# CS2 grenades, traced from server.dll 2026-11-05

The held grenade, the throw, the jump throw, the projectile's flight, the HE's blast, the molotov and its inferno, the
flashbang's pop, the smoke, the decoy. Addresses are server_20261105.dll in the Ghidra project. Ported in
`web/src/cs2web/sim/grenade-hold.js` (CBaseCSGrenade per command), `sim/src/combat/grenade_throw.rs` (the throw's maths,
ze_grenade_throw), `web/src/cs2web/sim/grenade-sim.js` (the throw's trace and the flight: float32 with `Math.fround` after every
operation), `web/src/world/movement.js` jumpPoseStep (the jump's pose), `web/server/cs2web/grenades/grenades.js` (the throw,
detonations, ZR's hooks), `web/server/cs2web/grenades/smoke-decoy.js` and `web/server/cs2web/grenades/inferno.js` (the fire). Checks:
`node web/server/cs2web/grenades/grenade-test.mjs`, `node web/server/cs2web/dev/grenade-lineups.mjs`, `move_oracle <bins> --throw`.

## The held grenade (traced 2026-11-15, session "grenade-throw"; src/cs2web/sim/grenade-hold.js)

CBaseCSGrenade's vtable `0x1818e7f18` (rtti.py; every grenade class shares these slots): ItemPostFrame vfn 0xd00 =
**`1809c8710`**, vfn 0xd08 = 180a0f050 (the base ItemBusyFrame), **vfn 0xd10 = `1809c8320`** (the throw's think),
Deploy vfn 0xa18 = **`1809b80b0`**, Holster 0xa20 = 180a041f0 (holster.md), PrimaryAttack 0xcf0 = **`1809ccca0`**
(`jmp [vfn 0xda8](this, 0)`), SecondaryAttack 0xcf8 = **`1809d0650`** (the freeze period, gamerules +0xd8, returns 0;
else `jmp [vfn 0xda8](this, 1)`), PullPin vfn 0xda8 = **`1809b3bd0`**, ThrowGrenade vfn 0xdb8 = `1809d4a50`,
EmitGrenade vfn 0xdd0, throw velocity vfn 0xc48 = 1809c0350 (vdata m_flThrowVelocity). Fields (schema.py): m_bRedraw
+0x1280, m_bIsHeldByPlayer +0x1281, m_bPinPulled +0x1282, m_bJumpThrow +0x1283, m_bThrowAnimating +0x1284, m_fThrowTime
+0x1288, m_flThrowStrength +0x128c, m_fDropTime +0x1290, m_fPinPullTime +0x1294, m_bJustPulledPin +0x1298,
m_nNextHoldTick +0x129c, m_flNextHoldFrac +0x12a0, m_hSwitchToWeaponAfterThrow +0x12a4. 180b5ce80(w, mask) = the
pawn's buttons (vfn 0xb30 +0x58) & mask (held).

Per command the weapon services' post-think (180b06e70, fire-gate.md) runs ItemPostFrame, then ItemBusyFrame (0xd08)
while curtime < m_flNextAttack, else vfn 0xd10. Curtime is the command's tick / 64 (f32), the fraction 0.

- **Deploy `1809b80b0`**: m_bRedraw 0, m_bIsHeldByPlayer 1, m_bThrowAnimating 0, m_bPinPulled 0, m_fThrowTime 0,
  m_bJumpThrow 0, m_hSwitchToWeaponAfterThrow -1; with ammo (vfn 0xaf0(0) > 0) the draw (180a276f0 activity 0x1b) and
  CCSWeaponBase::Deploy 1809fb560 (both clocks now + m_flDeployDuration (1.0 for every grenade) not earlier, m_iShotsFired
  0, m_bWaitForNoAttack 1, m_flNextAttack); else the weapon services drop it.
- **ItemPostFrame `1809c8710`** (a pawn first):
  1. m_bPinPulled and attack 1 or 2 held: when now (tick, 0) is not before (m_nNextHoldTick, m_flNextHoldFrac)
     (1813b8ef0 / 18017e2d0's compare: ticks, then the fraction): target 0.5, attack 1 -> 1.0, attack 2 -> target - 0.5
     (so 1 / 0 / both 0.5); **m_bJustPulledPin 0: strength = Approach(target, strength, 0x3ca66666 = 0.0203125)**
     (180460960: `target - value > speed` -> value + speed, `-speed > target - value` -> value - speed, else target);
     m_bJustPulledPin 1: strength = target at once and m_bJustPulledPin 0; m_nNextHoldTick + 1.
  2. m_bPinPulled and neither button: the throw animation (1809f7840 activity 0xca), **StartGrenadeThrow `1809d3cd0`**,
     m_bPinPulled 0, the weapon_fire event; return.
  3. m_bRedraw 0: CCSWeaponBase::ItemPostFrame 180a0f4b0 (knife.md "The gate"): attack 1 and the primary clock ->
     the primary branch (freeze period, m_iShotsFired >= 1 without full auto, m_bWaitForNoAttack refuse) ->
     PrimaryAttack; else attack 2 and the secondary clock -> SecondaryAttack; else (no attack button)
     m_bWaitForNoAttack 0, m_iShotsFired 0. With the pin out it runs too: PullPin refuses.
- **PullPin `1809b3bd0`(this, secondary)**: m_bIsHeldByPlayer, m_bPinPulled 0, not `0 < m_fThrowTime`, a pawn, ammo:
  strength = secondary ? 0 : 1, activity 200 (the pull), m_bPinPulled 1, m_nNextHoldTick = now's tick + 1,
  m_flNextHoldFrac = now's fraction, m_fPinPullTime = curtime, m_bJustPulledPin 1. **There is no pin time**: a
  release on the next command throws (the viewmodel's pull-pin clip is only the look).
- **StartGrenadeThrow `1809d3cd0`**: m_fThrowTime = curtime + **0.1** (0x3dcccccd at 0x18178fdc8; 18017dc70 addss);
  with the controller's current command (pawn +0xc98 -> controller +0x708) late (its link cmd +0x90 non-null, usercmd.md 3):
  m_fThrowTime - (link's number +8 - its number +8) x 0.015625 (cvtdq2ps, mulss 0x3c800000); then curtime >
  m_fThrowTime -> m_fThrowTime = curtime. **180ad2570(pawn, 0.1)** (the jump window, below) -> m_bJumpThrow 1 and
  BaseGrenade.JumpThrowM / F (pawn +0xe6a picks F). m_bThrowAnimating 1; the throw sound.
- **vfn 0xd10 `1809c8320`**: m_fDropTime set and curtime - it < 0.1: an animation event, return (else it is cleared);
  then **`curtime > m_fThrowTime` (strict, with 0 < m_fThrowTime)**: 180ad2570(pawn, 0.1) and m_bJumpThrow 0 ->
  m_fThrowTime = curtime + 0.1, m_bJumpThrow 1, the jump-throw sound, return; else (cvar at 0x182193bc0 +0x58 == 0:
  vfn 0xaf8(0, -1, 0)) **ThrowGrenade (vfn 0xdb8)**, then m_hSwitchToWeaponAfterThrow through the weapon services' vfn
  0xf0 when set. Not throwing, m_bIsHeldByPlayer 0 and m_bThrowAnimating 0: the weapon services' 180b23cc0(this, 0).
  So **the grenade leaves 7 ticks after the release** (release + 0.1 = 6.4 ticks; the first command past it).
- **ThrowGrenade `1809d4a50`**: 1809b4980 (last argument 0), NaN axes 0, EmitGrenade (vfn 0xdd0) with angles (0, 0, 0)
  and angular velocity (600, RandomInt(-1200, 1200), 0) (the global random stream; the draw happens, the value is
  dropped: every Create passes the thrower where it would go, "The spin" below), m_bRedraw 1,
  m_bIsHeldByPlayer 0, m_fThrowTime 0, the radio's 180a4be70 / 180239eb0 (pawn +0xe48 / +0xe58), `grenade_thrown`.
- **After the throw (traced 2026-11-21, session "nade-players")**:
  - **vfn 1809cb940** (the weapon's activity-finished callback: no direct callers): the current activity (+0xefc)
    200 (the pull) -> activity 0xc9; **0xca (the throw) -> m_bThrowAnimating 0 and the draw activity 0x1b**
    (180a276f0); else CCSWeaponBase's (180a1c800). So the throw animates until the throw activity's clip ends.
  - **vfn 1809ccb20(this, target)** (asked before a switch away): not throw-animating -> true; target == this and vfn
    0xaa0(0) false -> false; else **m_hSwitchToWeaponAfterThrow (+0x12a4) = target** (a weapon key pressed during
    the throw is kept) and the result is `!m_bIsHeldByPlayer` (before the release the switch waits; once the grenade
    has left it goes at once).
  - vfn 0xd10 (above), m_bIsHeldByPlayer 0 and m_bThrowAnimating 0: m_hSwitchToWeaponAfterThrow live -> the weapon
    services' vfn 0xf0 (Weapon_Switch) to it; else **180b23cc0(services, this grenade, 0)**.
  - **180b23cc0 (SwitchToNextBestWeapon)**: nothing for a pawn whose life state (1803d9090) is 1 or 2; the current
    weapon's vfn 0xa08 (1809b50c0: true for every weapon) else nothing; **180b09ee0(services, current)**; a result
    other than the current -> vfn 0xf0 (Weapon_Switch).
  - **180b09ee0 (GetNextBestWeapon)**: m_hMyWeapons in order (services +0x48 count, +0x50 handles), each live, vfn
    0xa00 (1809f9ec0: an owner and vfn 0xa48) and not the current one; for a bot (pawn vfn 0xc20) also 1802d42d0;
    the first such weapon is taken whatever its ammo; each later one replaces it when its gear slot (vdata +0x700:
    rifle 0, pistol 1, knife 2, grenades 3, C4 4) is lower **and it has a round** (180b7c520 true: its clip, vfn
    0xac0, >= 1; else vfn 0xaf0(0) >= 1), or the same gear slot with a lower position (vdata +0x704, no ammo test).
  - So with no key pressed: the rifle if its magazine has a round, else the pistol, else the knife (a second grenade
    of the same kind is the thrown weapon itself, never picked; another grenade only without a gun or knife).
  - Ours (server/cs2web/grenades/grenades.js release) is still the STAND-IN: the next grenade, else the last weapon,
    drawn at once. To port: the switch at the throw activity's end (the grenade's throw clip length on CS2's weapon
    graph: unread), the queued key, GetNextBestWeapon's order (the inventory's m_hMyWeapons order: unread here).
  Late commands: the link is taken as the batch's last command (game.js cmdLateBy).

## The throw

- **`1809b4980`**: the pawn's throw parameters (**180ac6340**, below), m_flThrowStrength snapped to 0.5 when `0.1 >=
  |s - 0.5|` (f32 comiss at 1809b4a11, 0.5 0x18178057c, 0.1 0x18178fdc8; a NaN keeps s), vfn 0xc48, then 1809b4ad0.
- **`1809b4ad0`** (the disassembly; ported in sim/src/combat/grenade_throw.rs, ze_grenade_throw):
  - pitch: `p > 90` -> p - 360, else `-90 > p` -> p + 360; `p = p - ((90 - |p|) x 10) / 90` (90 0x1817b2c54, 360
    0x18179beac, -90 0x181813dbc, 10 0x181784e0c), written back;
  - `v = throwVelocity x 0.9` (0x18178fde8); `15 > v` -> 15 (0x1817a4450), else minss(750, v) (0x18179bebc);
    strength `0 > s` -> 0, else minss(1, s); `speed = (s x 0.7 + 0.3) x v` (0x1817ad5d4, 0x18178fddc);
  - `fwd` = AngleVectors **181470980** of (the new pitch, yaw): yaw x 0x3c8efa35 into V_sincosf first, then pitch;
    `(cy cp, sy cp, -sp)` (the knife's combat::knife::forward);
  - `src = (eye.x + 0, eye.y + 0, (s x 12 - 12) + eye.z)` (12 0x1817bfec8), written back into the eye;
  - sv_grenade_collision_sphere (0x1821282a8 +0x58) 0: a box ±2.02 (0x400147ae / 0x1818e9fb8) traced (180c2f3c0) from
    the trace start to `(fwd.x x 16 + src.x, fwd.y x 16 + src.y, fwd.z x 16 + src.z)`; filter interacts-with
    **0x200003001**, collision group **4**, flags (& 0xc9) | 0x49, entity ids (the pawn 180bf9270, its owner +0x3e4
    when m_pCollision +0x5a & 4 is clear), hierarchy id 180c048b0; **src = the trace's end (+0x84), unconditionally**;
    the sphere cvar on: no trace, src as above;
  - `vel = fwd x speed + pawnVelocity x 1.25` (0x1817c98d0).
- **Checked bit for bit against server.dll** (sim/src/bin/move_oracle/throw.rs, `move_oracle <bins> --throw 200000`,
  2026-11-15): AngleVectors 181470980 on 200,000 angles (pitch ±360, yaw ±720) against knife::forward: **0
  differences**; 1809b4ad0 on 400,000 throws (random pitch incl. past ±90, yaw, roll, eye, trace start, velocity,
  throw velocity 0..1200, strengths -0.3..1.3 with 0 / 0.5 / 1), half with its trace hooked (the start, the end and the
  filter's mask / group recorded, the end answered), half with sv_grenade_collision_sphere 1: **0 differences** in the
  pitch, the source, the trace's end and start, the filter and the velocity. The installed CS2 (server 2026-11-12)
  runs the same code: every function here compared instruction by instruction (scratch fncmp: only relocated pointers
  differ; 1809b4ad0 -> 0x1809ad160, 180ac6340 -> 0x180abeb20, 1809c8710 -> 0x1809c0da0, 181470980 -> 0x18145fdd0).
- **180ac6340** (CCSPlayerPawn's throw parameters, (angles, eye, trace start, velocity, bool) out):
  - plain: the angles = the weapon services' (pawn +0xb10) vfn 0xd0 = **180b0a570**: the pawn's eye angles (vfn 0x5f0,
    180b4f890) + **GetAimPunch 180a43b90(pawn +0xe50, doubled)** (18029f040 adds); the eye = the abs origin
    (1803d6f50: the node +0xc8) + m_vecViewOffset (180158e30 on pawn +0x818); **the trace start = pawn vfn 0x2c8 =
    18015a2f0, WorldSpaceCenter**: m_pCollision (vfn 0x228 = 1801575b0, +0x3d8) -> its centre `(maxs + mins) x 0.5`
    (180156f30: maxs.x + mins.x, x 0.5 at 0x18178057c) -> 18014cf50 (an unrotated collision: `scale x c + the abs
    origin`, 180cf6440 / 180cf6430), so **origin + (0, 0, hull height / 2)**: 36 standing, 27 ducked (no
    m_pCollision: the abs origin); the velocity = the abs velocity (1803d6fb0);
  - the jump's (pawn +0x1564 set and, with the last argument 0, `0 < curtime - pawn+0x1560 <= 0.2`, 0.2 0x181784df8 at
    180ac63ca): the saved angles +0x1568, eye +0x1574, trace start +0x1580, velocity +0x158c (returns 1).

## The jump throw

- **The jump's stamp**: CheckJumpButton (legacy 180abc3f0, modern 180ae66b0; movement.md "The jump's record") sets
  svc+0x68c = (curtime - frametime) + 0.1 (the piece's start + 0.1 s), copies it to **pawn +0x1560** and clears
  **pawn +0x1564**. The step builder cuts a piece at the stamp (movement.md, move-state.js extraCuts).
- **vfn 0x138 `180ac4c00`** after each piece: SetAbsOrigin / SetAbsVelocity from mv, the view offset (180ae9260), then
  with svc+0x68c > 0 and the piece's end (mv+0xd4, mv+0xe0) not before its GameTime: **180ae4570(pawn)**: pawn +0x1564
  = 1, +0x1568 the weapon services' vfn 0xd0 angles (eye angles + aim punch), +0x1574 the eye (origin + view offset),
  +0x1580 pawn vfn 0x2c8 (the trace start), +0x158c the abs velocity; svc+0x68c = 0. (movement.md's note, now fixed, had +0x1568 /
  +0x1580 the other way round: the throw's reader 180ac6340 settles it.)
- **180ad2570(pawn, extra)**: `d = (curtime + extra) - pawn+0x1560`, true when `d > 0` and `0.2 >= d`.
- So: a release within (jump, jump + 0.2] sets m_bJumpThrow (StartGrenadeThrow); vfn 0xd10 delays a throw due inside
  that window without m_bJumpThrow by 0.1; and **a throw between 0.1 and 0.3 s after the jump takes the pose at
  exactly jump + 0.1 s** (the piece cut there), not the current one: the jump-throw bind lands the same every time.
- The port: src/world/movement.js jumpPoseStep (after each sim piece: the stamp set -> jumpTime, the pose cleared;
  the stamp cleared -> the pose: origin, velocity, the sim's view offset, the hull's half height), the angles added by
  server/cs2web/grenades/grenades.js jumpPose on the next command. UNSETTLED: the eye angles inside the movement (pawn vfn 0x5f0 at
  180ae4570) taken as that command's view, the aim punch at the command's tick.
- **Sub-tick**: nothing in the throw path reads a sub-tick time. The release, the throw time and the throw itself run
  at the command's tick (fraction 0); only the jump's pose is sub-tick (the piece cut at jump + 0.1 s).

## The projectile

- **Create** (HE `1803a4810`, molotov `1809b7110`): SetDetonateTimerLength (`1809d0680`): HE / flashbang **1.5 s**,
  molotov `molotov_throw_detonate_time` **2.0** (`1800b2ca0`); gravity **0.4** (0x3ecccccd), friction **0.2**,
  elasticity **0.45** (0x3ee66666, `+0x3f8`); HE damage = vdata `m_nDamage` (+0x820: 99) x
  `sv_hegrenade_damage_multiplier` (1, `18005f450`), radius = vdata `m_flRange` (+0x830: 350) x
  `sv_hegrenade_radius_multiplier` (1, `18005f4f0`).
- **Spawn `1809d2d80`**: box (-2, -2, -2)..(2, 2, 2) (or a sphere of `sv_grenade_collision_sphere_radius` 2 when the
  sphere cvar is on), interacts-with **0x200003001** (solid, window, passbullets, bit 33 the csgo grenade clip),
  group 16 (Projectile, 180d0e200), movetype CUSTOM.
- **PhysicsSimulate `1809cc050`**: `n = (int)(frametime * 128)`, one substep when that isn't whole; n - 1 substeps of
  1/128 s and a last one of what's left (two of 1/128 at 64 tick); PhysicsToss each, velocity x0.98 in water
  (flags 0x18000); then the spin step ("The spin" below); m_nTicksAtZeroVelocity (+0xb38): |v| == 0 -> + 1, more than
  8: velocity 0, movetype none, vfn 0xa10 (with +0xa48 clear) and the next think now; else 0. It runs only while
  m_nActualMoveType (1803d95f0, +0x2f5) isn't 0: SetMoveType(4 FLYGRAVITY, 2) and vfn 0xa18 first, SetMoveType(10
  CUSTOM, 0) at the end unless the frame left it none.
- **PhysicsToss `180e904c0`**: ground cleared when vz > 0 or no ground; on the ground with zero velocity: return;
  PhysicsCheckVelocity; **PhysicsAddGravityMove `180e8e9b0`** (`nz = vz - ft * sv_gravity * gravity`,
  `move.z = ((vz + nz) * 0.5 + basevz) * ft`); PhysicsPushEntity; stuck (start solid) -> velocity 0; a hit ->
  PerformFlyCollisionResolution -> ResolveFlyCollisionCustom.
- **PhysicsPushEntity `180e8f7d0`**: TraceEntity (`180c2e7e0`) origin -> origin + move; origin = end unless the fraction
  is 0; a hit entity gets PhysicsImpact (the touches, `180e8f4d0`).
- **ClipVelocity `180e8efa0`**: `b = -((v.z n.z + v.y n.y) + v.x n.x) * overbounce`, at least 0, `+ 0.03125`;
  `out = b * n + v`.
- **ResolveFlyCollisionCustom `1809ce4b0`**: a breakable (func_breakable / _surf, prop_physics_multiplayer or
  prop_dynamic with health) takes **10 DMG_CLUB**; broken -> velocity x0.4, done. `e = clamp(elasticity, 0, 0.9)`;
  `v = ClipVelocity(vel, n, 2.0) * e`; a player hit takes its normal from the player's centre (a living player is never
  hit: "Players and the projectile's filter" below). **Wall** (`n.z <= 0.7 && (n.z <= 0.1 || |v|^2 >= 400)`): velocity = v, push `v * (1 - frac) * ft`, and
  if that push stops before half, again with its remainder clipped off the new normal. **Floor**: over 96000 u^2/s^2,
  `dot = normalize(v) . n`, above 0.5 `v *= (1 - dot) + 0.5`; under 400: ground, velocity 0; else push
  `v * (1 - frac) * ft`. Bounce sound at most every 0.1 s, `grenade_bounce`; then **|v| after the bounce: above 0 a new
  spin, else SetMoveType(0, 0)** (1809cf55f: movetype none, no vfn 0xa10: PhysicsSimulate isn't run again); vfn
  0xa00; 1801ff2f0 / 18022f9e0 (a listener told the bounce: the normal, the count + 1); m_nBounces (+0xae8) < 21: + 1,
  else velocity 0, movetype none, vfn 0xa10 (+0xa48 clear) and the next think. m_vecLastHitSurfaceNormal (+0xb2c) =
  the trace's normal (+0x90), or for a player (vfn 0x558) the direction from its vfn 0x2c8 centre to the trace's end.
- TODO: base velocity (0 here), FL_CONVEYOR's 0.3, the standable test FUN_1803e0100 and two class casts (taken as
  standable), the water level, PhysicsCheckVelocity (CS:GO-shaped clamp, unread). The filter is CS2's 0x200003001:
  rubikon registers server.dll's csgo_* layers at their own bits (31..40), so a map's csgo_grenadeclip is bit 33.

### Players and the projectile's filter (traced 2026-11-20, session "nade-players"; server_20261105)

A thrown grenade flies through living players in CS2: their collision never carries a layer its filter
(0x200003001: solid 0, window 12, passbullets 13, csgo_grenadeclip 33) interacts with.

- **180ae27b0(pawn)** (the living pawn's layers): with a live controller (pawn +0xc98 through the entity list):
  180cf1850 (collision +0x5f |= 1), 180cf1540 (attribute flags +0x3f |= 7), 180cee5a0 (+0x3f &= 0xb7), **180cf16a0(c,
  0x40000)**: interacts-as (collision +0x18) |= player, **180cee390(c, 1)**: interacts-as &= ~solid, 180cee420(c,
  0x40010): exclude (+0x28) &= ~(player | playerclip); then vfn 0x6c8(pawn, +0x3e8 & ~0x20), +0x1be = 0x101,
  180ceffe0. Callers: RestartRound (180957e50, 0x18095a421), CSPlayerPawn's script Reset (18023b580), 18024a860 with
  its flag clear, 180237640, 180923fb0 (both unnamed).
- **180ae28e0(pawn)** (the other way): 180cee540, 180cf1970, 180cf18d0(c, 0), 180cf1a10, **interacts-as |= solid
  (180cf16a0(c, 1)), &= ~player (180cee390(c, 0x40000)), exclude |= 0x40010** (180cf1730), the same tail. Callers:
  **18024a860 with its flag set**, which also writes m_nRagdollDamageBone (+0x1004), the force (+0x1008),
  m_szRagdollDamageWeaponName (+0x1014, 64 chars), m_bRagdollDamageHeadshot (+0x1054): the death; 180208400 and
  1802089a0 (unnamed). Its flag clear: 180ae27b0 and +0x1058..0x1060 zeroed.
- **SetCollisionGroup 180d0e200(collision, group)**: m_CollisionGroup (+0x5e), the attribute's group (+0x3e); group 5
  (debris): interacts-as &= ~0x20000, |= 0x100000; any other but 2 and 14: &= ~0x100000, |= 0x20000 (touchall); 2 and
  14 leave the layers.
- So a living pawn interacts as player (+ touchall under group 8), not solid: no layer of the grenade's filter
  (the grenade's own interacts-with, Spawn 1809d2d80). ResolveFlyCollisionCustom's player branch (vfn 0x558) is for
  what else answers it. Ours: the projectile trace (server/cs2web/grenades/grenades.js PROJECTILE_FILTER) meets no
  pawn, which is CS2's. Unread: the interacts-as bits a pawn starts with before 180ae27b0 (none of 0x200003001 taken),
  whether a dead pawn's solid layer meets anything (its collision's solid type and flags after the death; we keep no
  dead pawn body), which layers the team bits 31 / 32 join.

## The spin (traced 2026-11-16, session "nade-spin"; sim/src/combat/grenade_spin.rs)

Fields (schema.py, CBaseCSGrenadeProjectile): m_vInitialPosition +0xad0, m_vInitialVelocity +0xadc, m_nBounces
+0xae8, m_flSpawnTime +0xb08, m_vecOriginalSpawnLocation +0xb10, m_flLastBounceSoundTime +0xb1c, **m_vecGrenadeSpin
+0xb20** (degrees a second about a world axis), m_vecLastHitSurfaceNormal +0xb2c, m_nTicksAtZeroVelocity +0xb38,
m_bHasEverHitEnemy +0xb3c. The constructor (fn ~1803a4300, 1803a43af) zeroes the spin. Every projectile class
(HE vtable 0x1817c8c68, flashbang 0x1817c80a8, molotov 0x1818e74d0, smoke 0x1818e8f58, decoy 0x1818e5e00) has vfn
0x720 = 1809cc050 and a Spawn (vfn 0x48: 1803a8050, 1803a7f60, 1809d3170, 1809d33a0, 1809d3030) that ends in the base
1809d2d80. m_vecAngVelocity (+0x480, SetLocalAngularVelocity 1803eb230) isn't the spin: a CUSTOM movetype never
integrates it, and PhysicsCustom zeroes it every frame.

- **Create ignores its angular velocity**: HE 1803a4810, flashbang 1803a4760, smoke 1809b79e0, decoy 1809b6c50 call
  the spawner 180cec250(class, origin, angles, **r9 = the thrower**: the "owner" key, 180cec250's fourth argument) and
  never read their angular velocity argument (the molotov's 1809b7110 inlines the same spawner). So ThrowGrenade's and
  the death drop's (600, RandomInt(-1200, 1200), 0) only spend a draw of the global stream.
- **Spawn 1809d2d80** (1809d2f1f..1809d2fe4): GetThrower 1808c6250 (m_hThrower +0xaa8 through the entity list, else
  the owner +0x3e4; set by 1808d6480 only after Create's spawn, so here the owner key); with one:
  SetLocalAngularVelocity(0x18177bf90: 0); the thrower's eye angles (vfn 0x5f0), roll `+ -20` (addss 0x1817bc144) ->
  SetAbsAngles 1803ea1a0 (-> the node's 180c26600: stored when a lane differs, 18014a300's ==); AngleVectors
  181472530(eye angles, null, &left, null); **spin = (-l.x x 1500, -l.y x 1500, -l.z x 1500)** (xorps 0x1817805b0
  then mulss 0x1817b2c94). Then the "thrown" anim graph tag (180b61330 / 180b77df0).
- **PhysicsSimulate 1809cc050 after the tosses** (1809cc2bb..1809cc97d): M = 181478260(GetAbsAngles 1803d6de0) =
  181478d90(out, origin 0x18177bf80 = 0, angles): a VMatrix with AngleVectors' forward / left / up as columns (the
  same V_sincosf 0x18176a598 import and pi/180 0x1817d0e90, the same products as 181472530), the translation 0, the
  row (0, 0, 0, 1). The spin x **0.995** (0x18178fdf0; x, z, y). n = the inline normalize of the spin (len =
  sqrt((z z + y y) + x x); 1e-17 0x181780574 > len or len > 1e17 0x181780590 (comiss / ja, a NaN goes on): 0 when
  len == 0, else 1814738b0; else x (1 / len)). **d = |(n.z m22 + n.y m12) + m02 n.x|** (andps 0x181784e80);
  `d > 0.1` (0x18178fdc8, comiss / jbe): d == 1.0 (ucomiss 0x181780580) -> spin.x + 0.001 (0x181784de8); s = |spin|;
  u = the up column (m02, m12, m22) through VectorNormalize 180148890; plane = (u.z m23 + u.y m13) + u.x m03 (0);
  t = ((u.z sp.z + u.y sp.y) + u.x sp.x) - plane; p = (sp.x - u.x t, sp.y - u.y t, sp.z - u.z t); pn = normalize(p),
  n = normalize(spin); b = (pn - n) x **0.03** (0x1817b6568) + n per lane; **spin = normalize(b) x s** (the axis
  pulled 3% a tick into the model's plane: a tumble, end over end). Then the axis = normalize(spin) and
  **R = 181478230(out, axis, |spin| x gpGlobals frametime (+0x34))**: 1814719c0's rotation about the axis by that many
  degrees (c4_spin.rs axis_rotation) with the row (0, 0, 0, 1); the angles out = **181478b30(181478690(R, M))**:
  181478690 = the VMatrix product a b, each entry ((a_i0 b_0j + a_i1 b_1j) + a_i2 b_2j) + a_i3 b_3j; 181478b30 =
  MatrixAngles on it (xy = sqrt(m00 m00 + m10 m10) over 0.001: yaw atan2(m10, m00), pitch atan2(-m20, xy), roll
  atan2(m21, m22), else yaw atan2(-m01, m11), roll 0, each x 57.2957764 0x1817bfedc, the V_atan2f import
  0x18176a4a8: math/matrix.rs matrix_angles). The out arguments (origin, velocity = the abs ones, angles, angular
  velocity = 0) go to PhysicsCustom 180e8f1f0, which sets the abs angles, the velocity and the angular velocity
  (1803ea1a0, 1803ea4a0, 1803eb230) and moves the entity only when the origin it got back differs (never here).
- **ResolveFlyCollisionCustom's spin** (1809cf191..1809cf555), when |v| after the bounce > 0: v = the velocity at
  entry (1803d6fb0 into local_228, before anything); d = the inline normalize of v; k = ((n.z d.z + n.y d.y) + n.x d.x)
  doubled (addss k, k), n = m_vecLastHitSurfaceNormal; e = (d.x - k n.x, d.y - k n.y, d.z - k n.z) (the reflected
  direction); en = normalize(e); **spin = (-(en.z d.y - en.y d.z), -(en.x d.z - d.x en.z), -(d.x en.y - en.x d.y))**
  (each xorps 0x1817805b0), then **x (RandomFloat(4, 8) x |v|)** (tier0!RandomFloat, IAT 0x18176b218, bounds
  0x18179be70 / 0x181780588: the global stream; |v| = sqrt((z z + y y) + x x)).
- **Checked bit for bit against server.dll** (sim/src/bin/move_oracle/nadespin.rs, `move_oracle <bins> --nadespin
  200000`, 2026-11-16): 181472530's left on 200,000 angles; **1809cc050 itself** on 200,000 random (angles, spin,
  frametime) with its tosses, time scopes and setters stubbed (55,797 without the tumble, 144,202 with it, the |d| ==
  1 case), the spin it leaves and the angles it returns; **1809ce4b0 itself** on 200,000 world hits (no entity: the
  wall branch, the push answered "all the way"), RandomFloat hooked to a known draw: the bounds (4, 8), one draw, the
  spin it leaves: **0 differences**.
- The port: grenade-sim.js spawnSpin (newProjectile's eye angles: grenades.js spawn, the thrower's view with roll 0),
  the spin step at the end of simulate (also on the tick a bounce left it still: the tosses' loop doesn't look), the
  bounce's in `bounced` (vfn 0xa00 after it, then the count, as 1809cf56c..), movetype none (p.stopped) when a bounce
  leaves it still. The draws come from the server's one tier0 stream (core/global-random.js, shared with the spawn
  picks). The snapshot's `gn` carries the abs angles as float32; the client (client/fx/grenades.js) draws them as a
  QAngle (yaw z, pitch y, roll x) between samples with game/interp.rs lerp_angles (the fitted slerp, ze_lerp_angles).
- Nothing in the flight reads the angles or the spin: the trace box is axis aligned (Spawn's box, SOLID_BBOX), the
  bounce's velocity doesn't use the spin. The client draws the samples on the replica's clock (client/fx/grenades.js
  place: the samples by snapshot tick s.k, the tick the players and the map are drawn at, held past the newest as
  replica.js sample), not eased per frame. The smoke's and the decoy's resting angles (1809b38e0) unread.
- m_angRotation on the wire (server 18068c5e0, the scene node's network fields): 18068d451.. registers it with the
  serializer "gameSceneNodeStepSimulationAnglesSerializer" (0x181832bf8, field +0x68) and the encoder
  "qangle_precise" (0x181796878, +0x70). networksystem_20261015's qangle_precise (its name 0x180238178; the class's
  methods from 0x180274548: GetName 1800d4450, encode 1800d3900, decode 1800d3d90) writes three bits, one a
  component, set when |v| >= its threshold (+0x34), then each set component wrapped to [-180, 180] (floor(v / 360 +
  0.5), clamped) as (uint)((double)(v + 180) * scale (+0x38, a double) + 0.5) in +0x2c bits. STAND-IN (TODO(trace)):
  the bit count, threshold and scale (+0x2c / +0x34 / +0x38) are set where the encoder is made from the field's
  metadata, and no code or data reference to that class was found (its methods are reached only through the
  vtable); the snapshot sends the server's float32, finer than any 32-bit-or-less quantization of the same angle.

## Detonations

- **HE Detonate `1803a4f10`**: `hegrenade_detonate`, then CBaseGrenade::Detonate `1808c2380` -> vfn 0x998
  (`1809bcc90` -> Explode `1808c3200`: CTakeDamageInfo(radius +0xa84, damage +0xa90, DMG_BLAST 0x40), vfn 0x9f0 =
  `1803a5420`: BaseGrenade.Explode, the particle (`1803a5da0` with GetPointContents `180c034f0` at the blast: in water
  (0x18000) explosion_basic_water, moved to the water's surface by a line on 0x18000 up / down 512 u; else _hegrenade_brief /
  _hegrenade_dirt / _hegrenade_snow / explosion_basic) and **RadiusDamage** (`180df0300` -> gamerules vfn 0x1f8).
  RadiusDamage is read (2026-11-10): the gamerules' vfn 0x1f8 through CCSGameRules' RTTI vtable 0x1818c5450 is
  0x180956070 -> `1809550b0` (with 0); sim/src/game/radius.rs has every step (the sphere's targets 180bdc700, BodyTarget
  180ce3c10, the visibility 180926130 / 180927370, the sources around corners 18090a6b0, the expf falloff); armor at the
  HE's m_flArmorRatio 1.2.
- **Team damage `180a89230`**: teammates blocked with friendly fire off; your own grenade x
  `ff_damage_reduction_grenade_self` (1, `1800c5da0`).
- **Molotov BounceTouch `1809b3ee0`**: ignores its thrower, func_breakable / _surf, func_ladder; a surface with
  `cos(weapon_molotov_maxdetonateslope) <= normal.z` (30, `1800b49e0`; UNSETTLED: tier0's V_cosf) -> Detonate.
- **Molotov Detonate `1809b82e0`**: `molotov_detonate`; a start-solid check; `1809d5e00`: a line from +10 to -128
  (interacts-with 0xc3001): nothing under it -> Molotov.StartFailed / IncGrenade.StartFailed, the air explosion, no fire;
  else the inferno at the ground point, along the throw velocity (|vz|).
- **Inferno Start `1803536c0`**: Molotov.Start / IncGrenade.Start, Inferno.Loop, `inferno_startburn`, CreateFire
  `180345dc0`. Cvars (each registration read): inferno_damage 40, inferno_damage_timer 0.2, inferno_flame_lifetime 7,
  _incendiary 5.5, inferno_max_range 150, inferno_max_flames 16, inferno_flame_spacing 42,
  inferno_initial_spawn_interval 0.02, inferno_per_flame_spawn_duration 3, inferno_child_spawn_interval_multiplier 0.1,
  inferno_max_child_spawn_interval 0.5, inferno_spawn_angle 45, inferno_child_spawn_max_depth 4. STAND-IN: the spread
  rule (CInferno::Think / CreateFire not read), lifetimes, the flame volume (server/cs2web/grenades/inferno.js lists them).
- **Flashbang**: `flashbang_detonate`, Flashbang.Explode, explosion_flashbang; RadiusFlash, Blind, Deafen and the
  client's overlay: [flashbang.md](flashbang.md).

## The fire grenades' flight sounds, and the throw's sound slot (traced 2026-11-18)

- **CMolotovProjectile's Create `1809b7110`** (at 1809b786a, after the damage 200 / radius 300 and the think): by
  **m_bIsIncGrenade (+0xb40)** the pawn-style emit 180f695d0(this, out, name, 0, 0, 1, 0) of **`IncGrenade.Throw.Loop`**
  (0x1818e8e98), else **`Molotov.Throw.Loop`** (0x1818e8eb0); the returned sound handle (20 bytes) is kept at
  **+0xb44..+0xb57**. The loop events are positional, on the projectile (Molotov's volume 0.7, the incendiary's 0.5;
  self_destruct_time 8 s, a child event Molotov.ThrowFire).
- The handle is read back in two places only (fieldwrites.py 0xb44): **Detonate `1809b82e0`** (molotov_detonate, the
  inferno) at 1809b8b50 and **the air burst `1809d5e00`** (Molotov.StartFailed / IncGrenade.StartFailed,
  explosion_molotov_air / explosion_incend_air) at 1809d6065: the loop stops when the grenade goes off, either way.
- **Its bounce sound, vfn `1809b3e60`**: `IncGrenade.Bounce` (0x1818e8ee8) with m_bIsIncGrenade, else
  `Molotov.Bounce` (0x1818e8f00), by 180f695d0 the same way (the projectile's bounce think calls the vfn at most every
  0.1 s: "The projectile").
- **StartGrenadeThrow `1809d3cd0`'s sound** (at 1809d3fc4..1809d4156): the weapon's vdata (181029810 -> 181067ff0's
  +0x260 name -> 18054a2f0) m_aShootSounds' **slot 2** (WEAPON_SOUND_SINGLE; the find 1809aec60), emitted through a
  0.8-attenuation filter minus the thrower's controller (180c8b5a0) when the name isn't empty. **No grenade's vdata
  has a WEAPON_SOUND_SINGLE**, so it emits nothing: items_game's `sound_single_shot` (Flashbang.Throw, HEGrenade.Throw,
  IncGrenade.Throw) is read by no code (player-sounds.md "The vdata sound slots"). The client's twin is 1807dfaa0.

Port: src/cs2web/player/grenade-sounds.js (GRENADE_BOUNCE's incendiary, FLIGHT_LOOP), client/fx/grenades.js
flightLoop (from the projectile's first snapshot to its last, following it), grenade-sounds-test.mjs. The server sent
Molotov.Bounce for an incendiary before 2026-11-18 and no flight loop.

## Smoke (traced 2026-11-15; server/cs2web/grenades/smoke-decoy.js)

CSmokeGrenade's EmitGrenade (vfn 0xdd0) = 180a2c3a0 (logs `sv_throw_smokegrenade` with the source, angles, velocity
and angular velocity, then a deferred functor, vtable 0x18191a1a0 slot 0x10 = 180a31b80 -> Create). CSmokeGrenadeProjectile
vtable 0x1818e8f58; Detonate vfn 0x9a8 = 1809b8bb0.
- **Create `1809b79e0`**: `smokegrenade_projectile`; the think **1809d4650 from now** (1803ee6e0, SetNextThink(curtime)
  1803eb9e0); the velocity; +0xa90 = 100; gravity 0.4 (1803ead30 0x3ecccccd), friction 0.2 (180d0e560 0x3e4ccccd),
  elasticity 0.45 (+0x3f8); +0xb6c (m_bDidSmokeEffect) 0, +0xb68 (m_nSmokeEffectTickBegin) 0; the colour from the
  vdata / a cvar by team; group 16. No detonate timer. m_flSpawnTime (+0xb08) = curtime at Spawn (1809d2d80, its only
  writer).
- **Think `1809d4650`** (every tick): a trail of up to 16 positions 20 u apart (+0x2d78 ring: visual); then
  `|v|` (180225130: sqrtss((z z + y y) + x x)) and **`0.1 >= |v|` (0x3dcccccd; comiss, a NaN fails) and
  `curtime - m_flSpawnTime >= 1.188` (0x3f981062 at 0x1818e9f58)** -> Detonate; else the next think now.
- **Detonate `1809b8bb0`**: m_vSmokeDetonationPos (+0xb80) = the origin; the voxel fill (1809b4190 on +0xbc0, from
  that point, the +0x2d70 trail, a time from +0xb68); the think **1809d4330** every tick: once the fill job is done
  (1816a6940 false) **1809d2780**: listeners, 1809b38e0, m_nSmokeEffectTickBegin = the tick, 1809b4090,
  hostages within 1000, `smokegrenade_detonate` (userid, entityid, x / y / z = the origin), the detonation record,
  m_bDidSmokeEffect 1, BaseSmokeEffect.Sound, +0x550 = 1, **movetype none**, the think 1809d47d0.
- **`1809d47d0`** (every tick): age = (tick - m_nSmokeEffectTickBegin) x 0.015625; from **12.5** s the render alpha
  = remap(age, 12.5, 17.05 (0x41886666), 1, 0) x 255 (180b77050), a flag at 19; at **21.05** s alpha 0 and the think
  1809d47a0 a second on (the removal, `smokegrenade_expired` 1809cda40). At 0.37 s a Scorch decal (a line 0xc3001 from
  +2 to -64 under it).
- The port: the flight until the pop, then none; the pop event at m_vSmokeDetonationPos; the volume, its wire and
  its sight blocking: docs/game/smoke.md (the build job runs 6 ms a tick from Detonate, the pop when it's done:
  STAND-IN for the job thread's timing); the order of a projectile's think against its flight in the frame
  (taken as the flight first: CS2's think list 1805b70a0 runs PhysicsRunThink 180e900a0; where a projectile's
  PhysicsSimulate vfn 0x508 -> 180e90150 -> 180e8f1f0 -> vfn 0x720 (1809cc050) runs is unread).

## Decoy (traced 2026-11-15; the shots 2026-11-16, session "nade-vis")

CDecoyGrenade's EmitGrenade 1809fcc00 (logs `sv_throw_decoygrenade`); CDecoyProjectile vtable 0x1818e5e00.
- **Create `1809b6c50`**: `decoy_projectile`; the think 1809d4390 at **curtime + 2.0**; damage (+0xa90) **25**, radius
  (+0xa84) **25 x 3.5**; gravity 0.4, friction 0.2, elasticity 0.45. **The gun** (+0xb70, an item definition index):
  the thrower's weapon services' slot 0 (180c86620(services, 0)), else slot 1; neither: **weapon_hkp2000** for team 3
  (the thrower +0x344), else **weapon_glock** (each looked up by name once and cached: 181e0ef48 / 181e0f110). A slot
  weapon whose +0x68 byte is 0 leaves the gun 0xffff. **The sound key** (+0xb74): **2**, or **9** when the gun's vdata
  +0x728 (its silencer type) is set and the weapon's vfn 0xd90 (silencer on) says so: WEAPON_SOUND_SINGLE and the
  silenced shot (the bake's fireSound / fireSoundUnsilenced, WeaponBake). **The pattern** (+0xb68): the entry of the
  table at **181e0e7e0** (6 x 24 bytes) whose first int equals the gun's vdata +0x520 (CSWeaponType), else the first:

  | type | shots (+4..+8) | added between a burst's shots (+0xc) | pause between bursts (+0x10..+0x14) |
  |---|---|---|---|
  | 1 pistol | 1..3 | 0..0.3 | 0.5..4.0 |
  | 2 SMG | 1..5 | 0 | 0.5..4.0 |
  | 3 rifle | 1..3 | 0..0.5 | 0.5..4.0 |
  | 4 shotgun | 1..3 | 0 | 0.5..4.0 |
  | 5 sniper | 1..3 | 0..0.5 | 0.5..4.0 |
  | 6 machine gun | 6..20 | 0 | 0.5..4.0 |

- **`1809d4390`**: **`|v| <= 0.2`** (comiss / jbe: a NaN passes) -> 1809b38e0 (the decoy's resting angles: unported),
  `decoy_started` (x / y / z), m_shotsRemaining (+0xb5c) 0, **m_fExpireTime (+0xb60) = curtime + 14**, the think
  1809c0760 set (1803ee6e0), the bot manager's add (18032b710, 115) and **1809c0760 run at once**; else again at
  curtime + 0.2.
- **`1809c0760`**, one shot: m_shotsRemaining < 1 -> RandomInt(+4, +8); the gun's vdata (18102cf10 -> 181067ff0 ->
  18054a2f0) sound table (+0x4f8, keyed by the sound key, 0x28-byte entries, the name at +0x20) -> EmitSound
  (180f69780) at the decoy's origin through a filter built by 180c864b0(ent, 0.8), volume 1.0, pitch 100;
  DispatchParticleEffect **weapon_decoy_ground_effect_shot.vpcf** at the origin with the decoy's abs angles;
  `decoy_firing` (userid, entityid, x, y, z); m_shotsRemaining - 1. Then: shots left -> SetNextThink((curtime + the
  gun's vdata +0x738 m_flCycleTime) + RandomFloat(0, +0xc)); none left and curtime >= m_fExpireTime (18017e2d0 != -1)
  -> `decoy_detonate`, a record at the decoy (180b06bb0(.., 3): origin, +0xad0), 1808c2380 (the blast), UTIL_Remove;
  none left before it -> (curtime + cycle) + RandomFloat(+0x10, +0x14).
- Ported: server/cs2web/grenades/smoke-decoy.js (decoyGun, decoyPattern, decoyThink), grenades.js (the throw's pick, the
  'decoyshot' event with `s` for key 9), client/fx/grenades.js (fireSound(gun, silenced) and the effect); tests
  decoy-test.mjs, grenade-test.mjs.
- STAND-INS: RandomInt / RandomFloat from Math.random (the server's global uniform stream is vstdlib's); the effect's
  angles (the decoy's own from 1809b38e0 aren't simulated: the world's); the sound filter's 0.8 (180c864b0) and the
  EmitSound's other fields (the event's own levels are used); the blast through the HE's RadiusDamage path (1808c2380,
  its Explode, isn't read); 180b06bb0's record (its use unread); a slot weapon's +0x68 test.

## Lineups (2026-11-15; web/server/cs2web/dev/grenade-lineups.mjs)

Smokes thrown on de_dust2 from (400, 2400, -120) (CT spawn) through the whole server path (the command, ItemPostFrame,
the throw think, ThrowGrenade, the flight, the smoke's think): where each goes off, as this port computes it,
recorded in the test (a change that moves one fails):

| Case (yaw, pitch, buttons) | Detonation |
|---|---|
| 0, 0, Mouse 1 | 142.055 2489.308 -117.994 |
| 45, -30, Mouse 1 | 417.643 2465.083 -117.969 |
| 45, -30, both (0.5) | 429.632 2490.805 -117.958 |
| 45, -30, Mouse 2 (0) | 506.22 2517.413 -116.897 |
| 90, -45, Mouse 1, jump throw (release 2 ticks after the jump) | 374.178 2519.12 -117.393 |
| 90, -45, Mouse 1, running 20 ticks | 403.284 2344.293 -119.048 |

Checked there: the same throw lands the same; a jump throw released 1..11 ticks after the jump's press lands on
one spot (the saved pose), 12 ticks after is past the window and lands elsewhere.

**Against CS2 itself: not captured.** The retail server (2026-11-12) has no `sv_throw_*` commands (development
only: "Unknown command"), a throw needs a player's usercmds (no client can be driven headless here), and bots on a
local de_dust2 (bot_loadout with grenades, sv_bot_buy_grenade_chance 100) threw nothing in three rounds. What stands
instead: the throw's maths and AngleVectors against server.dll natively (0 differences, "The throw"), the same code
in the installed build, the flight's functions read from the disassembly. TODO: a client-side capture (a demo or a
listen server with a scripted client) of a lineup's landing, compared with these.

## Still unread / stand-ins

- PhysicsCheckVelocity (180e8eb40: taken as CS:GO's clamp), base velocity / FL_CONVEYOR in the toss, the standable
  test FUN_1803e0100 and the two class casts in ResolveFlyCollisionCustom (taken as standable): none moves a lineup on
  a static map (no trigger_push / conveyor under a grenade), but a moving or non-standable floor would.
- PhysicsCustom 180e8f1f0 (the caller of vfn 0x720): FUN_1803d9e40 first, then the ground cleared when vz > 0 or the
  ground (vfn 0x668) isn't standable (1803e0100), then vfn 0x720, the angles / velocity / origin set back.
- V_cosf for the molotov's slope (tier0; the JS uses Math.cos rounded).

## CS2Fixes ZR on top (upstream zombiereborn.cpp)

- Napalm (zr:1450-1459): an HE's damage to a zombie from a human: IgnitePawn for `clamp(damage / 50 * 5, 0, 5)` s
  with DMG_FALL (silent), the thrower as attacker: the `'i'` stimulus.
- Knockback (zr:1015-1032): `normalize(victim - projectile + (0, 0, 36))`, z 0 for the inferno, x `(int)damage x
  zr_knockback_scale x weapons.cfg` (hegrenade 3.0, inferno 5.0).
- weapons.cfg.example: flashbang, smokegrenade, decoy disabled; HE, molotov, incgrenade enabled (CanAcquire zr:1481).
