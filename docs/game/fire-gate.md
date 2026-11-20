# A gun's fire gate (traced 2026-11-11; sim/src/combat/fire_gate.rs, game_tick.rs, fire_abi.rs)

server_20261105.dll. CCSWeaponBaseGun's vtable 0x1818f0d38 (rtti.py): PrimaryAttack is slot 0xcf0 (180a206e0),
SecondaryAttack 0xcf8 (180a236b0), ItemPostFrame 0xd00 (180a0f840; the same three at 0x1b50.. in the second table).
Fields (schema.py): weapon m_nNextPrimaryAttackTick +0xeb0 / m_flNextPrimaryAttackTickRatio +0xeb4, the secondary's
+0xeb8 / +0xebc, m_bFireOnEmpty +0xf50, m_weaponMode +0xf70, m_bBurstMode +0xf9c, m_iBurstShotsRemaining +0x1284,
+0x1038 the last fire's curtime, +0x10c0 the last shot's offset (attack time - (now + 1 tick), as float ticks); pawn
m_iShotsFired +0x14d8, m_bWaitForNoAttack +0x14f0; vdata m_bLinkedCooldowns +0x4c6, m_flCycleTimeWhenInBurstMode
+0x740, m_flTimeBetweenBurstShots +0x744, m_nBurstShotCount +0x7cc. Virtuals: 0xac0 Clip1, 0xab0 Clip2, 0xaf0 the
reserve, 0xad8 take ammo, 0xb98 IsFullAuto, 0xbb0(mode) GetCycleTime, 0xd18 HasBurstMode, 0xd20 IsInBurstMode, 0xd28
IsRevolver, 0xcc8 HasZoom, 0xd48 Reload.

## 1. The clocks: tick + ratio (game_tick.rs)

- **1813b8ef0** makes (tick, ratio): a ratio outside [0, 1) is split by V_modff, a negative fraction + 1 (tick - 1),
  the whole part (int, 0 outside +-2^31) added to the tick.
- **1813b8fb0** a - b: ratio difference, below 0 + 1 and tick - 1; then the same fold. **1813b9aa0**: tick + 1.
- **180cacba0** "now": gpGlobals (PTR 181e328d0) tick +0x44 (180927c50) and fraction +0x50.
- **180b5d3c0** primary ready (180b5d470 the secondary): now >= clock, ticks first, then ratios; NaN not ready.
- **180b3baa0** (primary; 180b3bbe0 the secondary, the same 82 instructions) sets a clock `delay` seconds on, base
  `mode` 0 now, 1 the clock itself, 2 now but never earlier: `d = maxss(0, delay)`, `rem = fmodf(d, 0.015625)`,
  `ticks = cvttss2si((d - rem) x 64.0 + 0.5)`, `r = base ratio + rem x 64.0`; `r >= 1`: r - 1, ticks + 1; then
  `0.01 (0x3c23d70a) > r`: r = 0; `r > 0.99 (0x3f7d70a4)`: ticks + 1, r = 0. Mode 2 keeps the clock when the new one
  is earlier (an earlier tick, or the same tick and a lower ratio).
- **180b763d0(this, delay, mode)** the primary clock, and the secondary's too when m_bLinkedCooldowns;
  **180b76450** the secondary, and the primary when linked.

When ItemPostFrame runs, "now" is the command's tick and fraction 0: the command loop (180c7cdb0: catch-up commands)
sets gpGlobals tick +0x44 = the player's tick (180b56470), curtime +0x30 = tick / 64, frametime +0x34 = 0, +0x50 = 0
around each RunCommand (vfn 200); the movement (180adf830) saves and restores the same fields around its own steps.
ItemPostFrame is called once a command: the pawn's post-think (180ac4e30) -> the weapon services' 180b06e70 (vfn 0xd00
on the active weapon, then 0xd08 / 0xd10, then the ShootVerify block).

## 2. ItemPostFrame

- **180a0f840** (the gun's): (a) once the primary clock passed with pawn +0x14bd (the re-zoom flag) and a zoom level
  (+0x1280) > 0, the sniper re-zoom (not ported); (b) **a burst's follow-up**: m_iBurstShotsRemaining > 0, HasBurstMode
  and the primary clock passed -> remember m_iShotsFired, PrimaryAttack (vfn 0xcf0), remaining - 1; if m_iShotsFired
  didn't rise, remaining = 0; (c) the base, **180a0f4b0**.
- **180a0f4b0**, first that applies: attack (1) held and the primary ready -> the primary branch 180a0fac0; else
  attack3 (0x400000000, not bound here); else attack 2 (0x800) held and the secondary ready -> 180a10200 (a
  non-revolver: 1809f9b80 -> SecondaryAttack); else reload (0x2000, held or pressed: 180b5ceb0) -> not reloading:
  1809fb150 / 1809f9f70, then 180a10140 -> Reload when the primary is ready (ported 2026-11-11: reload.md); else 0x100000000 (inspect, not ported); then, with no
  attack button (0x400000801) held: the revolver's idle (180a10400), m_bFireOnEmpty = 0, m_bWaitForNoAttack = 0,
  m_iShotsFired = 0, and **the empty reload**: primary ready, a pawn, vfn 0xa98(0), 180b7c520(0), Clip1 <= 0, the
  reserve >= 1, !vfn 0xc98(2), not reloading -> Reload (vfn 0xd48; untraced: 0xa98, 180b7c520, 0xc98 taken as true).
  So **CS2 reloads an empty gun only once the trigger is up**. Last, 0x800000000 -> 180a23e30 (not read).
- **The primary branch 180a0fac0**: Clip1 == 0 (or Clip2 == 0 and no reserve) -> m_bFireOnEmpty = 1. Nothing if the
  freeze period (gamerules +0xd8), pawn +0x14be, pawn +0xd40, **m_iShotsFired > 0 and (not full auto or Clip1 == 0)**
  or m_bWaitForNoAttack. The revolver's 180a0fe70; the weapon_fire event; PrimaryAttack; +0x1038 = curtime; the
  revolver's secondary clock x 1.7.

## 3. PrimaryAttack 180a206e0 and BaseGunFire 1809f8a70

- PrimaryAttack first: the pawn (180b54f20); its +0xc98 handle resolved, 180a6ffb0(that entity) below 0 returns
  (unread). Then **vfn 0xbf8 = 1809b5210 for every weapon class** (CCSWeaponBase's, no override: the guns, CKnife,
  the grenades, the R8): `return vdata(+0x320)->m_bCannotShootUnderwater (+0x71f)`, with no water-level test anywhere
  on the path (it's the only `call [r + 0xbf8]` in server.dll). Set: 180a1e400 (the weapon's empty sound: the pawn's
  controller's +0x708, the sound emit 180c864b0; also BaseGunFire's dry fire's) and 180b763d0(0.15, mode 0): the primary
  clock now + 0.15, no shot, PrimaryAttack returns 0. The vdata's constructor zeroes +0x71c..0x71f (1809f3be6) and
  weapons.vdata sets it on no gun (the bake's `cannotShootUnderwater`: false for all 34), so no CS2 gun takes it. The
  cycle is GetCycleTime(0); in burst mode with m_iBurstShotsRemaining < 1 it becomes m_nBurstShotCount; with any left,
  the cycle is m_flTimeBetweenBurstShots, and with fewer than 2 `max(1/64, m_flCycleTimeWhenInBurstMode - (between +
  between))` (`0.015625 <= v ? v : 0.015625`). Then BaseGunFire(cycle, m_weaponMode, 0) (a sniper's zoom-out after).
- BaseGunFire with a round in: **1809f9910** (below), the bullets (FX_FireBullets 1802a4f50 with the attack time),
  m_fAccuracyPenalty (+0xf88) += vfn 0xbe8(mode), the recoil, **m_iShotsFired + 1**, the recoil index (+0xf98) + 1,
  **Clip1 - 1** (vfn 0xad8(0, 1)). Empty, with m_bFireOnEmpty: 180a1e400, **the primary clock now + 0.2** (mode 0;
  the revolver's own cycle), the dry-fire sound (0x32), **m_bWaitForNoAttack = 1**.
- **1809f9910**: now; GetWeaponAttackTime (180a02c60, below) into the attack info; +0x10c0 = attack - (now + 1); **with
  an input history entry (info +0x38), each clock no earlier than now** (the compares are against now, not the
  attack time); then 180b763d0(cycle, 1) and 180b76450(cycle, 1): **both clocks + cycle from themselves**. Without an
  entry ("no history - using calculated time") the clocks just run on: a trigger held through a full-auto magazine
  keeps the cycle's fractional grid (0.1 s = 6.4 ticks: 6, 7, 6, ... apart).
- **GetWeaponAttackTime 180a02c60**: the controller's current command (+0x708); its attack1_start_history_index
  (+0x4c; attack 2: +0x50) picks an input history entry (cmd +0x38's list); the entry's player tick (+0x68) and
  fraction (+0x6c) are the attack time, clamped to [now + 1 - 4 ticks, now + 1] ("Player tick from command clamped by
  server"); its render tick (+0x60 / +0x64) goes to the lag compensation. Traced 2026-11-11 (usercmd.md): the index
  must be 0..count-1, else -1; first (out +0 / +0x38 the "has history" byte / +0x39 vfn 0xb98 or 0xd20 / +0x14 the
  eye 180b54f80) **the calculated time = the clock (180b54e20: m_nNextPrimaryAttackTick / Ratio; attack 2 180b54e50)
  + 1 tick (1813b9aa0) + the weapon's +0x10c0 as ticks (1813b9230, 1813b9090)**, which is the attack time without an
  entry (logs "GetWeaponAttackTime: ..." at 180a031e0 / 180a03202 / 180a03238 for no pawn / controller / command).
  With one, the entry's player tick and fraction (1809209f0, 1809f2ef0), clamped to [lo, hi] = [(now + 1) - 4 ticks,
  now + 1] (1813b8ef0(4, 0), 1813b8fb0, the 1809f69c0 compares). Then the shoot position from the weapon services'
  32-entry history at the attack time (svc +0x370, 0x78-byte records, a GameTime at +0x70; unread past the search).
  Back in 1809f9910: **+0x10c0 = (attack - (now + 1 tick)) as (float)tick + ratio** (1813b8fb0, cvtdq2ps, addss),
  written on every shot. So a held trigger's attack times keep the press's fraction, moved by each shot's clock-to-
  tick gap (a press at 100.5, the AK's next shot at 106.9). BaseGunFire seeds the spread with this time's tick
  (usercmd.md 4) and Recoil kicks at it (aim-punch.md 2). Ported: fire_gate.rs `attack_time`.

## 4. SecondaryAttack 180a236b0 (the burst toggle)

HasBurstMode (vfn 0xd18): burst mode off -> "Switch_To_BurstFire", m_bBurstMode = 1, m_weaponMode = 1; on ->
"Switch_To_FullAuto" / "_SemiAuto" (vfn 0xb90), m_bBurstMode = 0, m_weaponMode = 0; Weapon.AutoSemiAutoSwitch
(either way, after the hint: the pawn's EmitSound 180f695d0(pawn, out, name, 0, 0, 1, 0), read 2026-11-17: a filter
built at the pawn's vfn 0x6b8 point (180c83dd0, then the thunk to 180c84870 with that point; vtable 1818e4a70, the dry
fire's PAS filter), volume 1.0, sound level 100, flags `& 0xe5 | 5`, with 0x181e23e88 set to 1 around the emit;
whether it drops the predicting owner as the dry fire's filter does is unread: ours does, the client playing its own
toggle. Port: loadout.js tryFire's 'burst' zoom event, zoom-events.js, client main.js onBurst; burst-sound-test.mjs). Then
**180b76450(0.3, 0)**: the secondary clock now + 0.3 (and the primary when linked). The zoom and silencer branches:
section 6 (traced 2026-11-11, ported in src/cs2web/sim/zoom.js).

## 6. SecondaryAttack's zoom and silencer, SetZoomLevel, SetFOV (traced 2026-11-11)

Fields (schema.py): weapon m_weaponMode +0xf70, m_fAccuracySmoothedForZoom +0xf90, m_bInReload +0xfa8,
m_bSilencerOn +0xfbd, m_flTimeSilencerSwitchComplete +0xfc0 (curtime f32), m_iWeaponGameplayAnimState +0xefc (short),
m_iIronSightMode +0x10b8, m_IronSightController +0x10a0 (m_bIronSightAvailable +8, m_flIronSightAmount +0xc),
m_zoomLevel +0x1280; vdata m_eSilencerType +0x728, m_bUnzoomsAfterShot +0x7f0, m_bHideViewModelWhenZoomed +0x7f1,
m_nZoomLevels +0x7f4, m_nZoomFOV1 / 2 +0x7f8 / +0x7fc, m_flZoomTime0..2 +0x800..0x808, m_flIronSightPullUpSpeed
+0x80c, PutDownSpeed +0x810, m_flIronSightFOV +0x814, m_WeaponType +0x520, m_flMaxSpeed[2] +0x748; pawn m_bIsScoped
+0x14bc, m_bResumeZoom +0x14bd, m_bIsDefusing +0x14be, the controller handle +0xc98, camera services +0xb48, weapon
services +0xb10 (m_flNextAttack +0xc0); camera services m_iFOV +0x178, m_iFOVStart +0x17c, m_flFOVTime +0x180,
m_flFOVRate +0x184, m_hZoomOwner +0x188; controller m_iDesiredFOV +0x71c.

Weapon vfns (CCSWeaponBaseGun, vslotall): 0xb50 SetZoomLevel **180a27870**; 0xc20 GetMaxSpeed **1809bf4f0**
(m_flMaxSpeed[m_weaponMode], [0] outside 0..1); 0xc28 m_nZoomLevels **1809c0650**; 0xc30 m_bUnzoomsAfterShot
1809b9740; 0xc38 the zoom sound 1809c05c0 (m_aShootSounds key 0x13 = WEAPON_SOUND_ZOOM_IN); 0xc60 m_WeaponType
1809c05b0; 0xc70 zoom FOV(n) **180a03ee0** (0: 0, 1: FOV1, 2: FOV2, else 0); 0xc78 zoom time(n) **180a03f10**
(m_flZoomTimeN, else 0); 0xc90 zoomed **180a0f030** (m_zoomLevel > 0); 0xcb0 m_zoomLevel 180a00ab0 (CCSWeaponBase
1809be8f0); 0xcc8 HasZoom 180a03fe0 (0xc28 != 0; CCSWeaponBase 1809c0f90 false); 0xd08 ItemBusyFrame **180a0f0c0**
(CCSWeaponBase 180a0f050: only the m_bWaitForNoAttack clear); 0xd10 1809c8700 (empty); 0xd88 action end
**180a1c800**; 0xd90 IsSilenced 1809c7bc0 (m_bSilencerOn). WeaponSound_t order from server.dll's strings
(EMPTY 0 .. ZOOM_IN 19, ZOOM_OUT 20).

**SecondaryAttack 180a236b0**, in order: no pawn returns. `canSwitch` = vdata m_eSilencerType == 1 (detachable) and
now past m_flTimeSilencerSwitchComplete (18017e2d0(now, +0xfc0) == 1: -1 when b > a, 1 when a > b, 0 equal, 0x80
unordered). `human` = the pawn's controller (+0xc98) resolves and its +0x388 bit 0x100 is clear (TODO: the flag's
name; a bot's has it). Both: the client's cl_silencer_mode (engine vfn 0x1a8, GetClientConVarValue) < 1 and silenced
-> canSwitch false. Then:
- HasZoom: the controller's +0x708 +0x80 bit 1 returns (unread, no clock change); m_bIsDefusing returns;
  m_zoomLevel + 1, past vfn 0xc28 -> 0; SetZoomLevel(level).
- else HasBurstMode: section 4.
- else canSwitch: activity setter 1809f7840(600 + IsSilenced, flags 0x1b, 0, force 1): 600 attach, 601 detach.
- else (vfn 0xd28 revolver with the secondary ready: its own alt fire, lib/revolver.js); otherwise silenced,
  detachable, not switching (180a0eec0: now <= +0xfc0) and cl_silencer_mode < 1 -> 18021a430(pawn,
  "#Cstrike_TitlesTXT_Silencer_Disabled") ("Removal of the silencer is disabled.\nEnable it in settings." in
  resource/csgo_english.txt).
- every branch that didn't return: 180b76450(0.3, 0).

cl_silencer_mode (client 180084140, flags 0x8280 userinfo/archive): int, default **0**, "0: cannot detach; 1: press
secondary fire to detach". cl_sniper_auto_rezoom (client 18009c330, 0x8288): bool, default **1**. Both read by the
server from the client's userinfo.

**SetZoomLevel 180a27870(level)**: !HasZoom returns; m_zoomLevel = level; pawn and camera services or return; type =
vfn 0xc60. Not zoomed (vfn 0xc90): m_weaponMode = 0; a sniper (type 5): cur = camera vfn 0xe0 (GetFOV), def = vfn 0xe8
(default), SetFOV(def int, ZoomTime0, start = int(cur) - int((float)(int(def) - int(cur)) x -0.7)): the zoom-out
starts 70% of the way back. +0xf90 = 0; m_bIsScoped = 0; the active weapon's iron sight controller available ->
180a2d620, SetFOV(int def, 180a2d4c0 = 1 / PutDownSpeed, 0), 180a2f520(ctrl, 0). Zoomed: m_weaponMode = 1; a sniper
SetFOV(vfn 0xc70(level), vfn 0xc78(level), 0); +0xf90 = 0; m_bIsScoped = 1; iron sight: SetFOV((int)180a2d480 =
m_flIronSightFOV, 180a2d490 = 1 / PullUpSpeed, 0), 180a2f520(ctrl, 1). Then 1809f7840(0x32, 0, 0, force 1); zoomed:
the zoom sound (vfn 0xc38 through filter 1809f3e40(weapon, 0.8), volume 1), event "weapon_zoom" (a sniper) /
"weapon_zoom_rifle".

**SetFOV 180a9b240(cam, requester, fov, rate, start)**: requester null returns 0. The same m_iFOV and m_flFOVRate:
with m_hZoomOwner the requester (or none and fov 0) nothing changes (returns 1); another live owner refuses (0).
fov 0 -> m_hZoomOwner = -1, else the requester's handle. start < 1 -> int(vfn 0xe0, GetFOV). m_iFOVStart = start,
m_flFOVTime = curtime, m_iFOV = fov, m_flFOVRate = rate.

**GetFOV 180a7a250**: target = m_iFOV, 0 -> vfn 0xe8 (180c71530 -> the controller's 180b52be0: m_iDesiredFOV, 0 ->
engine vfn 0xf8; CS2's 90). (float)m_iFOVStart == target -> target. Rate != 0: t = (now (180c86a30) - m_flFOVTime) /
rate; t < 1 -> **1802b3130** SimpleSplineRemapValClamped(t, 0, 1, start, target) = `(3 - (c + c)) x c x c x (b - a) +
a`, c clamped to [0, 1]; else target. Rate 0: m_iFOVStart = target (a write), target.

**PrimaryAttack's tail** (180a208bb, BaseGunFire fired): zoomed and m_bUnzoomsAfterShot: m_bIsScoped = 0;
cl_sniper_auto_rezoom != 0 -> m_bResumeZoom = 1, else m_zoomLevel = 0; m_iIronSightMode = 0; SetFOV(int(vfn 0xe8),
0.05, 0); m_weaponMode = 0. The shot itself went in mode 1.

**The gun's ItemPostFrame 180a0f840 start**: the primary clock reached, m_bResumeZoom and m_zoomLevel > 0: Clip1 != 0
or vfn 0xa68 & 2 (180b56580, unread) -> m_weaponMode = 1, SetFOV(vfn 0xc70(level), 0.1, 0), m_bIsScoped = 1,
m_iIronSightMode = 1; m_bResumeZoom = 0 either way. Then the burst follow-up, then 180a0f4b0.

**The weapon services 180b06e70** (the pawn's post-think): vfn 0xd00 (ItemPostFrame), then vfn 0xd08 while curtime <
m_flNextAttack (18017e2d0 == -1), else 0xd10. **ItemBusyFrame 180a0f0c0**: HasZoom, (zoomed or m_bIsScoped) and
m_bInReload: m_bIsScoped = 0; cl_sniper_auto_rezoom 0 -> m_zoomLevel 0, else m_bResumeZoom = 1; SetFOV(vfn 0xc70(0),
vfn 0xc78(0), 0); m_weaponMode = 0. Then no attack button (0x400000801) -> m_bWaitForNoAttack = 0.

**The movement's Accelerate** (180ab6f3e) asks the active weapon: scoped = vfn 0xcb0 (m_zoomLevel) > 0 && vfn 0xc28
(m_nZoomLevels) > 1 && GetMaxSpeed x 0.52 < 110. (The move oracle's trap names these two the other way round; its
values were fed right.) PlayerMove's max speed takes min(260, GetMaxSpeed) (movement.md).

**The iron sight controller**: 180a2d480 / 490 / 4c0 read the weapon's vdata through `ctrl - 0xd80` (the weapon +
0x320). The AUG and SG 553 have m_flIronSightFOV 45, pull-up 10, put-down 8. m_bIronSightAvailable's setter is unread
(controller +8, a disp8 store: fieldwrites can't find it).

## 7. The silencer switch (traced 2026-11-11)

**1809f7840** (the gameplay activity setter), the part the switch takes: the old activity 600 / 601 (or 800 / 0x322
with the new one outside 0x321..0x323): both clocks now (180b763d0 / 180b76450 with 0, mode 0), +0xfc0 = now,
m_flNextAttack = now. Activity 600 / 601 with flags 0x1b: the duration is 100.0 (0x42c80000; 0xb takes vdata +0x7c4,
800 / 0x322 vdata +0x7c8) -> 180a276f0(force 1, mode 0): both clocks, +0xfc0 and m_flNextAttack now + 100. SecondaryAttack's
0.3 then puts the secondary back at now + 0.3.

**The flip**: m_bSilencerOn / m_weaponMode are written only by spawn (180a24ba0), a reset (1809f2fb0), the anim event
handler **180a1e2e0** (AE_SV_ATTACH_SILENCER_COMPLETE 0x29 -> on, mode 1; AE_SV_DETACH_SILENCER_COMPLETE 0x2a -> off,
mode 0; AE_ order from server.dll's strings, AE_PULSE_GRAPH 0) and the graph output handler **180a1e7c0** (+0x2b8 on,
mode 1; +0x2b9 off, mode 0; +0x2b4 -> vfn 0xd88). The graph output (**180b1cd40**) sets those from the sampled ID
events: WPN_ACTION_COMPLETE (182178640) -> +0x2b4, WPN_SILENCER_ATTACH (182178678) -> +0x2b8, WPN_SILENCER_DETACH
(182178680) -> +0x2b9 (others: +0x2b5..0x2ba, 0x2c0, 0x2cc). **vfn 0xd88 180a1c800**: activity 600 / 601 (and 500,
0xb, 100-102, 300, 0x1f5-0x1f9, 0x321 / 0x323, 0x3e9) -> activity 0x32 (forced), which frees the switch's clocks.

**The data** (the viewmodel graph, which the server's weapon runs): viewmodel_gun.vnmgraph+usp / +m4a1s: states
"SilencerOn/SilencerAttach" (node 222) and "SilencerOff/SilencerDetach" (53), each a clip with
m_timedRemainingEvents WPN_ACTION_COMPLETE at <= 0.1 s; the clips (animation/anims/viewmodel/<pistol|rifle>/_default_*/
silencer_attach_*.vnmclip) are 4.8333 s with WPN_SILENCER_ATTACH / _DETACH at 0.696552 (USP-S both), 0.710345 /
0.675862 (M4A1-S) of it. Baked by lasers-bake --weapons (`silencerSwitch`). Not read: when the server's graph updates
in the frame and the global transitions' blend into the state (the port starts the clip at the switch's tick).

## 5. Deploy (vfn 0xa18), traced 2026-11-11

Slot 0xa18: CCSWeaponBase **1809fb560** (also CC4, CCSWeaponBaseShotgun), CCSWeaponBaseGun **1809fb920** (every other
gun, the taser and the R8), CKnife **180a2b1a0**, CBaseCSGrenade 1809b80b0 (not read). Fields by tools/re/game/schema.py.

**1809fb560**, in order:
1. weapon +0x10a0 (when +0x10a8 is set): 180a2f520(.., 2) (unread).
2. With a pawn (180b54f20): **m_iShotsFired (+0x14d8) = 0**, m_bResumeZoom (+0x14bd) = 0, m_bIsScoped (+0x14bc) = 0,
   180a9b240(pawn +0xb48, pawn, 0, 0.0, 0) (the camera services' FOV, unread), **m_bWaitForNoAttack (+0x14f0) = 1**.
3. m_fAccuracyPenalty (+0xf88): 0 with weapon_accuracy_reset_on_deploy (cvar at 18212b1a0 +0x58), else
   RemapValClamped(now - m_flLastAccuracyUpdateTime (+0xf8c), 0, GetRecoveryTime 180a02600, penalty, 0) (accuracy.rs
   `deploy`, ported before). m_flRecoilIndex (+0xf98) = 0; m_flTurningInaccuracyDelta (+0xf74), the turning eye
   direction (+0xf78..f80), m_flTurningInaccuracy (+0xf84) = 0 (not ported: no turning inaccuracy here).
4. No pawn: returns false. Else **1809f7840(weapon, activity 0xb, flags 0x13, 0, force 0)**, the weapon's gameplay
   activity setter (m_iWeaponGameplayAnimState +0xefc, its timestamp +0xf00): for activity 0xb the duration is
   **m_flDeployDuration (vdata +0x7c4), whole** (100 for most activities; 0x320 / 0x322 vdata +0x7c8); flags & 0x1b
   send it to **180a276f0(weapon, flags, duration, force)**: t = curtime + duration; mode = (force ^ 1) x 2 (force 0
   -> 2: now + duration, never earlier); flags 1: 180b763d0(duration, mode) (the primary clock), 2: 180b76450 (the
   secondary), 8: +0xfc0 = t (later only, unless forced), 0x10: the pawn's weapon services (+0xb10) m_flNextAttack
   (+0xc0) = t (later only, unless forced). So the draw: **both attack clocks now + m_flDeployDuration, not earlier**,
   and the pawn's m_flNextAttack. (Activities 0x258 / 0x259 / 0x31f / 0x321 / 0x322 first set both clocks to now,
   mode 0, and +0xfc0 / m_flNextAttack to now.)
5. m_iIronSightMode (+0x10b8) = 2, m_bInReload (+0xfa8) = 0, m_bInspectPending (+0xf08) = 0, **m_nDeployTick (+0xfac)
   = now's tick**; returns true. Always: +0xfd0 = 1.0, +0xfb0 = 0.

**1809fb920** (the gun's): +0xfc0 = 0, **m_iBurstShotsRemaining (+0x1284) = 0**, then 1809fb560; on true: when vfn
0xcc8 (180a03fe0: vfn 0xc28 1809c0650 = vdata m_nZoomLevels +0x7f4, not 0) m_zoomLevel (+0x1280) = 0 and m_weaponMode
(+0xf70) = 0; when vfn 0xd28 (180a0ee80 = vdata m_bIsRevolver +0x71e) m_weaponMode = 1.

**180a2b1a0** (the knife's): 1809fb560; on true the pawn's m_flNextAttack = curtime + 1.0 (forced), the knife's
+0x1280 = 1.

**180a0efc0** (one caller, 180ae06c0): "deploying": 0 <= now tick - m_nDeployTick <= (int)(m_flDeployDuration x 64 +
0.5).

**m_flNextAttack** (weapon services +0xc0) gates nothing in the fire gate: the pawn's post-think (180b06e70) calls
ItemPostFrame (vfn 0xd00) every command, then vfn 0xd08 (ItemBusyFrame, section 6) while curtime < m_flNextAttack,
else vfn 0xd10 (empty for every gun).

## What the port does (2026-11-11)

sim/src/combat/fire_gate.rs runs 180a0f840 + 180a0f4b0 for a non-revolver gun per command: the follow-up, the
primary branch, PrimaryAttack's cycle, BaseGunFire's clocks / dry fire, the burst toggle, the idle resets and the
empty reload; web/src/cs2web/player/loadout.js keeps every gun's state on the loadout per weapon (CS2's clocks live on the
weapon). Checked: `cargo test -p ze-sim fire_gate game_tick`, web/src/cs2web/sim/fire-gate-test.mjs.

The input history entry is CS2's (usercmd.md 2: the client's first down event of the command, sent as cmd[11] with
its fraction of the tick; a bot's command without the list presses when the button goes down, TODO(trace): CS2's
bots' usercmds), and so is the tick a command runs at (usercmd.md 3: CS2's command queue pins the tickbase to the
server tick - 1, every command of a tick at it; the queue's buffering itself isn't ported). A reload holds the shots
back by the clocks Reload sets (now + m_flDisallowAttackAfterReloadStartDuration, reload.md), and the R key is the
gate's branch. Stand-ins: a shot with a round in stops a shell reload (unread); the zoom, the silencer, the re-zoom, attack3, inspect;
PrimaryAttack's +0xc98 handle test; CanPrimaryAttack's freeze period / pawn +0x14be / +0xd40 never set here. The R8
(lib/revolver.js), the knife and grenades keep their own gates.

Deploy (section 5) is ported in loadout.js selectSlot: both clocks now + m_flDeployDuration (mode 2; before
2026-11-11 a stand-in clamped it to 1 s), m_iShotsFired 0, m_bWaitForNoAttack 1, m_iBurstShotsRemaining 0, the
accuracy's part (accuracy.rs `deploy`). Not ported: the zoom and scope resets, the turning inaccuracy, m_flNextAttack
and vfns 0xd08 / 0xd10, the R8's mode 1, the knife's own Deploy, the grenades'. vfn 0xbf8's refusal is ported
(fire_gate.rs `cannot_shoot_underwater`, job word 4 bit 8, out bit 16 `refused`).

The zoom and silencer (sections 6 and 7, 2026-11-11) are src/cs2web/sim/zoom.js, called by loadout.js's gunFire around the
sim's gate (the re-zoom before it, the zoom-out after a shot, SecondaryAttack on the gate's out bit 32, ItemBusyFrame
after) and by holster / deploy, loadoutTick for the switch's graph events; fire_abi.rs ops 2 / 3 set one clock
(SetNextPrimaryAttack / SetNextSecondaryAttack). Stand-ins: the client cvars are CS2's defaults for everyone (no
userinfo), a reload counts as busy (Reload's m_flNextAttack unread), vfn 0xa68 & 2 and the controller flags taken as
clear, the graph's update time. Checked: web/src/cs2web/sim/zoom-test.mjs, cargo test fire_gate.

**The zoomed mouse** (client_20261105.dll **180b240b0**, from the pawn's camera services at +0x1328): a = (int) vfn
0x120, b = (int) vfn 0x118, c = (int) vfn 0x150, f = max(c, b); +0x149c = 1.0; f == a: +0x14a0 = 0, done; else (a 0
-> 1) +0x149c = zoom_sensitivity_ratio (cvar 1825600d8, default 1.0, client 1800c95c0) x f / a, +0x14a0 = cvar
182567c40 x that. Unread: which FOV each vfn is (taken: a the default, b GetFOV, c a floor) and where +0x149c is read
(taken: sensitivity x it). Ported: src/cs2web/client/hud/zoom-view.js.
