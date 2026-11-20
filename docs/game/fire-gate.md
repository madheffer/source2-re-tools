# A gun's fire gate: clocks, PrimaryAttack, burst, zoom, silencer, deploy

server_20261105; client_20261105 (the zoomed mouse, cl_silencer_mode / cl_sniper_auto_rezoom). weapons.vdata,
viewmodel_gun.vnmgraph, resource/csgo_english.txt.

## Functions

| Address | Module | What |
|---|---|---|
| 0x1818f0d38 | server | CCSWeaponBaseGun vtable (PrimaryAttack 0xcf0, SecondaryAttack 0xcf8, ItemPostFrame 0xd00; the same three at 0x1b50.. in the second table) |
| 1813b8ef0 | server | make (tick, ratio): a ratio outside [0, 1) split by V_modff, a negative fraction + 1 (tick - 1), the whole part (int, 0 outside +-2^31) added to the tick |
| 1813b8fb0 | server | a - b: ratio difference, below 0 + 1 and tick - 1; then the same fold |
| 1813b9aa0 | server | tick + 1 |
| 1813b9230, 1813b9090 | server | +0x10c0 as ticks |
| 180cacba0 | server | "now": gpGlobals (PTR 181e328d0) tick +0x44 (180927c50) and fraction +0x50 |
| 180927c50 | server | gpGlobals tick |
| 180b5d3c0 / 180b5d470 | server | primary / secondary ready: now >= clock, ticks first, then ratios; NaN not ready |
| 180b3baa0 / 180b3bbe0 | server | set the primary / secondary clock `delay` seconds on (the same 82 instructions) |
| 180b763d0 | server | (this, delay, mode): the primary clock, the secondary too when m_bLinkedCooldowns |
| 180b76450 | server | the secondary clock, the primary too when linked |
| 180c7cdb0 | server | command loop (catch-up commands) |
| 180b56470 | server | the player's tick |
| 180adf830 | server | movement: saves / restores the gpGlobals fields around its steps |
| 180ac4e30 | server | pawn post-think |
| 180b06e70 | server | weapon services: vfn 0xd00 on the active weapon, then 0xd08 / 0xd10, then the ShootVerify block |
| 180a0f840 | server | CCSWeaponBaseGun::ItemPostFrame |
| 180a0f4b0 | server | base ItemPostFrame |
| 180a0fac0 | server | primary branch |
| 180a10200 | server | secondary branch (a non-revolver: 1809f9b80 -> SecondaryAttack) |
| 1809f9b80 | server | -> SecondaryAttack |
| 180b5ceb0 | server | reload button held or pressed |
| 1809fb150 / 1809f9f70 | server | reload path, not reloading |
| 180a10140 | server | -> Reload when the primary is ready ([reload.md](reload.md)) |
| 180a10400 | server | the revolver's idle |
| 180b7c520 | server | empty reload test (untraced; taken as true) |
| 180a23e30 | server | 0x800000000 button (not read) |
| 180a0fe70 | server | the revolver's primary part |
| 180a206e0 | server | PrimaryAttack (vfn 0xcf0) |
| 180a208bb | server | PrimaryAttack's tail (BaseGunFire fired) |
| 180b54f20 | server | the weapon's pawn |
| 180a6ffb0 | server | (entity) below 0 returns (unread) |
| 1809b5210 | server | vfn 0xbf8 for every weapon class: `return vdata(+0x320)->m_bCannotShootUnderwater (+0x71f)` |
| 1809f3be6 | server | vdata constructor: zeroes +0x71c..0x71f |
| 180a1e400 | server | the weapon's empty sound (controller +0x708, emit 180c864b0) |
| 180c864b0 | server | sound emit |
| 1809f8a70 | server | BaseGunFire(cycle, mode, 0) |
| 1802a4f50 | server | FX_FireBullets |
| 1809f9910 | server | attack time and both clocks + cycle |
| 180a02c60 | server | GetWeaponAttackTime |
| 180a031e0 / 180a03202 / 180a03238 | server | logs "GetWeaponAttackTime: ..." for no pawn / controller / command |
| 180b54f80 | server | the eye |
| 180b54e20 / 180b54e50 | server | m_nNextPrimaryAttackTick / Ratio; attack 2's |
| 1809209f0, 1809f2ef0 | server | the entry's player tick and fraction |
| 1809f69c0 | server | the clamp compares |
| 180a236b0 | server | SecondaryAttack (vfn 0xcf8) |
| 180f695d0 | server | the pawn's EmitSound(pawn, out, name, 0, 0, 1, 0) |
| 180c83dd0 -> 180c84870 | server | filter at the pawn's vfn 0x6b8 point (vtable 1818e4a70, the dry fire's PAS filter) |
| 18017e2d0 | server | f32 compare: -1 when b > a, 1 when a > b, 0 equal, 0x80 unordered |
| 1809f7840 | server | gameplay activity setter (weapon, activity, flags, 0, force) |
| 180a0eec0 | server | switching: now <= +0xfc0 |
| 18021a430 | server | (pawn, text) hint |
| 180a27870 | server | SetZoomLevel (vfn 0xb50) |
| 1809bf4f0 | server | GetMaxSpeed (vfn 0xc20): m_flMaxSpeed[m_weaponMode], [0] outside 0..1 |
| 1809c0650 | server | vfn 0xc28: m_nZoomLevels |
| 1809b9740 | server | vfn 0xc30: m_bUnzoomsAfterShot |
| 1809c05c0 | server | vfn 0xc38: zoom sound (m_aShootSounds key 0x13 = WEAPON_SOUND_ZOOM_IN) |
| 1809c05b0 | server | vfn 0xc60: m_WeaponType |
| 180a03ee0 | server | vfn 0xc70 zoom FOV(n): 0: 0, 1: FOV1, 2: FOV2, else 0 |
| 180a03f10 | server | vfn 0xc78 zoom time(n): m_flZoomTimeN, else 0 |
| 180a0f030 | server | vfn 0xc90 zoomed: m_zoomLevel > 0 |
| 180a00ab0 / 1809be8f0 | server | vfn 0xcb0 m_zoomLevel (gun / CCSWeaponBase) |
| 180a03fe0 / 1809c0f90 | server | vfn 0xcc8 HasZoom: 0xc28 != 0 (gun) / false (CCSWeaponBase) |
| 180a0f0c0 / 180a0f050 | server | vfn 0xd08 ItemBusyFrame (gun / CCSWeaponBase: only the m_bWaitForNoAttack clear) |
| 1809c8700 | server | vfn 0xd10 (empty) |
| 180a1c800 | server | vfn 0xd88 action end |
| 1809c7bc0 | server | vfn 0xd90 IsSilenced: m_bSilencerOn |
| 180a2d620 | server | iron sight: off |
| 180a2d480 / 180a2d490 / 180a2d4c0 | server | iron sight: m_flIronSightFOV / 1 / PullUpSpeed / 1 / PutDownSpeed (vdata through `ctrl - 0xd80`) |
| 180a2f520 | server | (ctrl, state) iron sight |
| 1809f3e40 | server | filter (weapon, 0.8) |
| 180a9b240 | server | SetFOV(cam, requester, fov, rate, start) |
| 180a7a250 | server | GetFOV (camera vfn 0xe0) |
| 180c71530 -> 180b52be0 | server | default FOV (vfn 0xe8): m_iDesiredFOV, 0 -> engine vfn 0xf8 (90) |
| 180c86a30 | server | now |
| 1802b3130 | server | SimpleSplineRemapValClamped |
| 180b56580 | server | vfn 0xa68 (& 2: unread) |
| 180ab6f3e | server | movement's Accelerate: scoped test |
| 180a276f0 | server | (weapon, flags, duration, force): set clocks for an activity |
| 180a24ba0 / 1809f2fb0 | server | spawn / reset (write m_bSilencerOn / m_weaponMode) |
| 180a1e2e0 | server | anim event handler |
| 180a1e7c0 | server | graph output handler |
| 180b1cd40 | server | graph output: sets flags from sampled ID events |
| 1809fb560 | server | CCSWeaponBase Deploy (vfn 0xa18; also CC4, CCSWeaponBaseShotgun) |
| 1809fb920 | server | CCSWeaponBaseGun Deploy (every other gun, the taser, the R8) |
| 180a2b1a0 | server | CKnife Deploy |
| 1809b80b0 | server | CBaseCSGrenade Deploy (not read) |
| 180a02600 | server | GetRecoveryTime |
| 180a0ee80 | server | vfn 0xd28: vdata m_bIsRevolver +0x71e |
| 180a0efc0 | server | "deploying" (one caller, 180ae06c0) |
| 180084140 | client | cl_silencer_mode registration |
| 18009c330 | client | cl_sniper_auto_rezoom registration |
| 180b240b0 | client | the zoomed mouse (from the pawn's camera services at +0x1328) |
| 1800c95c0 | client | zoom_sensitivity_ratio registration |

## Vtable slots (CCSWeaponBaseGun)

| Slot | What |
|---|---|
| 0xa18 | Deploy |
| 0xa68 | (& 2 in the re-zoom; unread) |
| 0xa98 | empty reload test (untraced, taken as true) |
| 0xab0 / 0xac0 | Clip2 / Clip1 |
| 0xad8 | take ammo |
| 0xaf0 | the reserve |
| 0xb90 | full / semi auto name |
| 0xb98 | IsFullAuto |
| 0xbb0(mode) | GetCycleTime |
| 0xbe8(mode) | fire inaccuracy |
| 0xbf8 | cannot shoot underwater |
| 0xc98 | empty reload test (untraced, taken as true) |
| 0xd18 / 0xd20 / 0xd28 | HasBurstMode / IsInBurstMode / IsRevolver |
| 0xd48 | Reload |
| WeaponSound_t | EMPTY 0 .. ZOOM_IN 19, ZOOM_OUT 20 (server.dll's strings) |

## Fields

| Offset | Field |
|---|---|
| weapon +0xeb0 / +0xeb4 | m_nNextPrimaryAttackTick / m_flNextPrimaryAttackTickRatio |
| weapon +0xeb8 / +0xebc | the secondary's |
| weapon +0xefc (short) / +0xf00 | m_iWeaponGameplayAnimState / its timestamp |
| weapon +0xf08 | m_bInspectPending |
| weapon +0xf50 | m_bFireOnEmpty |
| weapon +0xf70 | m_weaponMode |
| weapon +0xf74 / +0xf78..f80 / +0xf84 | m_flTurningInaccuracyDelta / turning eye direction / m_flTurningInaccuracy |
| weapon +0xf88 | m_fAccuracyPenalty |
| weapon +0xf8c | m_flLastAccuracyUpdateTime |
| weapon +0xf90 | m_fAccuracySmoothedForZoom |
| weapon +0xf98 | m_flRecoilIndex |
| weapon +0xf9c | m_bBurstMode |
| weapon +0xfa8 | m_bInReload |
| weapon +0xfac | m_nDeployTick |
| weapon +0xfb0 / +0xfd0 | set 0 / 1.0 on every deploy |
| weapon +0xfbd | m_bSilencerOn |
| weapon +0xfc0 | m_flTimeSilencerSwitchComplete (curtime f32) |
| weapon +0x1038 | the last fire's curtime |
| weapon +0x10a0 | m_IronSightController (m_bIronSightAvailable +8, m_flIronSightAmount +0xc); +0x10a8 set |
| weapon +0x10b8 | m_iIronSightMode |
| weapon +0x10c0 | the last shot's offset: attack time - (now + 1 tick), float ticks |
| weapon +0x1280 | m_zoomLevel (the knife: set 1 on deploy) |
| weapon +0x1284 | m_iBurstShotsRemaining |
| weapon +0x2b4 / +0x2b8 / +0x2b9 | graph flags: action complete / silencer on / off (others +0x2b5..0x2ba, 0x2c0, 0x2cc) |
| weapon +0x320 | vdata |
| vdata +0x4c6 | m_bLinkedCooldowns |
| vdata +0x520 | m_WeaponType |
| vdata +0x71c..0x71f | zeroed; +0x71e m_bIsRevolver, +0x71f m_bCannotShootUnderwater |
| vdata +0x728 | m_eSilencerType (1 detachable) |
| vdata +0x740 / +0x744 | m_flCycleTimeWhenInBurstMode / m_flTimeBetweenBurstShots |
| vdata +0x748 | m_flMaxSpeed[2] |
| vdata +0x7c4 / +0x7c8 | m_flDeployDuration / activities 0x320, 0x322's duration |
| vdata +0x7cc | m_nBurstShotCount |
| vdata +0x7f0 / +0x7f1 | m_bUnzoomsAfterShot / m_bHideViewModelWhenZoomed |
| vdata +0x7f4 | m_nZoomLevels |
| vdata +0x7f8 / +0x7fc | m_nZoomFOV1 / 2 |
| vdata +0x800..0x808 | m_flZoomTime0..2 |
| vdata +0x80c / +0x810 / +0x814 | m_flIronSightPullUpSpeed / PutDownSpeed / m_flIronSightFOV |
| pawn +0x14bc / +0x14bd / +0x14be | m_bIsScoped / m_bResumeZoom (re-zoom flag) / m_bIsDefusing |
| pawn +0x14d8 | m_iShotsFired |
| pawn +0x14f0 | m_bWaitForNoAttack |
| pawn +0xc98 | controller handle |
| pawn +0xd40 | blocks the primary branch |
| pawn +0xb10 | weapon services (m_flNextAttack +0xc0; 32-entry shoot history +0x370: 0x78-byte records, GameTime at +0x70) |
| pawn +0xb48 | camera services: m_iFOV +0x178, m_iFOVStart +0x17c, m_flFOVTime +0x180, m_flFOVRate +0x184, m_hZoomOwner +0x188 |
| controller +0x388 bit 0x100 | set for a bot (name unread) |
| controller +0x708 | current command (+0x80 bit 1: SecondaryAttack's zoom returns; unread) |
| controller +0x71c | m_iDesiredFOV |
| gamerules +0xd8 | freeze period |
| gpGlobals +0x30 / +0x34 / +0x44 / +0x50 | curtime / frametime / tick / fraction |
| command +0x4c / +0x50 | attack1_start_history_index / attack 2's |
| command +0x38 | input history list |
| history entry +0x60 / +0x64 | render tick / fraction (to lag compensation) |
| history entry +0x68 / +0x6c | player tick / fraction (the attack time) |
| attack info +0 / +0x14 / +0x38 / +0x39 | out / the eye / "has history" byte / vfn 0xb98 or 0xd20 |
| client camera services +0x149c / +0x14a0 | zoom sensitivity factor / that x cvar 182567c40 |

## Constants

| Value | What |
|---|---|
| 0.015625 / 64.0 | tick |
| 0.01 (0x3c23d70a) / 0.99 (0x3f7d70a4) | ratio snap to 0 / to the next tick |
| 0.15 | cannot-shoot-underwater clock |
| 0.2 | dry fire clock (mode 0) |
| 0x32 | dry-fire sound; also activity 0x32 (idle) |
| 0.3 | SecondaryAttack's secondary clock |
| 1.7 | the revolver's secondary clock factor |
| 4 ticks | attack time clamp window |
| 1 (attack), 0x800 (attack 2), 0x2000 (reload), 0x100000000 (inspect), 0x400000000 (attack3), 0x800000000 | buttons |
| 0x400000801 | any attack button |
| 600 / 601 | activity: silencer attach / detach (600 + IsSilenced) |
| 0x1b, 0x13 | activity flags (switch, deploy) |
| 0xb | deploy activity |
| 100.0 (0x42c80000) | default activity duration |
| AE_SV_ATTACH_SILENCER_COMPLETE 0x29 / AE_SV_DETACH_SILENCER_COMPLETE 0x2a | anim events (AE_PULSE_GRAPH 0) |
| WPN_ACTION_COMPLETE 182178640 / WPN_SILENCER_ATTACH 182178678 / WPN_SILENCER_DETACH 182178680 | graph ID events |
| 0.52, 110 | scoped speed test |
| 260 | PlayerMove's max speed cap: min(260, GetMaxSpeed) ([movement.md](movement.md)) |
| 0.7 | zoom-out starts 70 % of the way back |
| 0.05 / 0.1 | FOV rate after a shot's unzoom / re-zoom |
| 0.8 | zoom sound filter |
| 0x181e23e88 | set to 1 around the burst toggle's emit |
| weapon_accuracy_reset_on_deploy | cvar at 18212b1a0 +0x58 |
| cl_silencer_mode int 0, flags 0x8280 (userinfo / archive) | "0: cannot detach; 1: press secondary fire to detach" |
| cl_sniper_auto_rezoom bool 1, flags 0x8288 | |
| zoom_sensitivity_ratio 1.0 (cvar 1825600d8) | |
| "#Cstrike_TitlesTXT_Silencer_Disabled" | "Removal of the silencer is disabled.\nEnable it in settings." |

## Clocks

- 180b3baa0: base `mode` 0 now, 1 the clock itself, 2 now but never earlier. `d = maxss(0, delay)`, `rem = fmodf(d, 0.015625)`, `ticks = cvttss2si((d - rem) x 64.0 + 0.5)`, `r = base ratio + rem x 64.0`; `r >= 1`: r - 1, ticks + 1; then `0.01 > r`: r = 0; `r > 0.99`: ticks + 1, r = 0. Mode 2 keeps the clock when the new one is earlier (an earlier tick, or the same tick and a lower ratio).
- When ItemPostFrame runs, now is the command's tick and fraction 0: 180c7cdb0 sets gpGlobals tick = the player's tick (180b56470), curtime = tick / 64, frametime = 0, +0x50 = 0 around each RunCommand (vfn 200). ItemPostFrame runs once a command (180ac4e30 -> 180b06e70).
- 180b06e70: vfn 0xd00, then vfn 0xd08 while curtime < m_flNextAttack (18017e2d0 == -1), else 0xd10. m_flNextAttack gates nothing in the fire gate.

## ItemPostFrame (180a0f840)

1. Primary clock passed, m_bResumeZoom and m_zoomLevel > 0: Clip1 != 0 or vfn 0xa68 & 2 -> m_weaponMode = 1, SetFOV(vfn 0xc70(level), 0.1, 0), m_bIsScoped = 1, m_iIronSightMode = 1; m_bResumeZoom = 0 either way.
2. Burst follow-up: m_iBurstShotsRemaining > 0, HasBurstMode, primary clock passed -> remember m_iShotsFired, PrimaryAttack, remaining - 1; if m_iShotsFired didn't rise, remaining = 0.
3. 180a0f4b0.

## 180a0f4b0 (first that applies)

1. attack held and the primary ready -> 180a0fac0.
2. attack3 (0x400000000).
3. attack 2 held and the secondary ready -> 180a10200.
4. reload (held or pressed) -> not reloading: 1809fb150 / 1809f9f70, then 180a10140.
5. 0x100000000 (inspect).
6. Then, no attack button held: the revolver's idle (180a10400), m_bFireOnEmpty = 0, m_bWaitForNoAttack = 0, m_iShotsFired = 0, and the empty reload: primary ready, a pawn, vfn 0xa98(0), 180b7c520(0), Clip1 <= 0, reserve >= 1, !vfn 0xc98(2), not reloading -> Reload (vfn 0xd48). An empty gun reloads only once the trigger is up.
7. Last, 0x800000000 -> 180a23e30.

## Primary branch (180a0fac0)

1. Clip1 == 0 (or Clip2 == 0 and no reserve) -> m_bFireOnEmpty = 1.
2. Nothing if: freeze period (gamerules +0xd8), pawn +0x14be, pawn +0xd40, **m_iShotsFired > 0 and (not full auto or Clip1 == 0)**, or m_bWaitForNoAttack.
3. The revolver's 180a0fe70; weapon_fire event; PrimaryAttack; +0x1038 = curtime; the revolver's secondary clock x 1.7.

## PrimaryAttack (180a206e0)

1. The pawn (180b54f20); its +0xc98 handle resolved, 180a6ffb0(that entity) below 0 returns.
2. vfn 0xbf8 (1809b5210, no override; the only `call [r + 0xbf8]` in server.dll, no water-level test on the path) set: 180a1e400 and 180b763d0(0.15, mode 0), no shot, returns 0. weapons.vdata sets it on none of the 34 guns.
3. cycle = GetCycleTime(0); in burst mode with m_iBurstShotsRemaining < 1 remaining = m_nBurstShotCount; with any left, cycle = m_flTimeBetweenBurstShots, and with fewer than 2 `max(1/64, m_flCycleTimeWhenInBurstMode - (between + between))` (`0.015625 <= v ? v : 0.015625`).
4. BaseGunFire(cycle, m_weaponMode, 0).
5. Tail (180a208bb): zoomed and m_bUnzoomsAfterShot: m_bIsScoped = 0; cl_sniper_auto_rezoom != 0 -> m_bResumeZoom = 1, else m_zoomLevel = 0; m_iIronSightMode = 0; SetFOV(int(vfn 0xe8), 0.05, 0); m_weaponMode = 0. The shot itself went in mode 1.

## BaseGunFire (1809f8a70)

- A round in: 1809f9910, the bullets (FX_FireBullets with the attack time), m_fAccuracyPenalty += vfn 0xbe8(mode), the recoil, m_iShotsFired + 1, recoil index + 1, Clip1 - 1 (vfn 0xad8(0, 1)).
- Empty with m_bFireOnEmpty: 180a1e400, the primary clock now + 0.2 (mode 0; the revolver's own cycle), the dry-fire sound (0x32), m_bWaitForNoAttack = 1.
- The spread is seeded with the attack time's tick ([usercmd.md](usercmd.md) 4); Recoil kicks at it ([aim-punch.md](aim-punch.md) 2).

## 1809f9910

1. now; GetWeaponAttackTime into the attack info; +0x10c0 = attack - (now + 1).
2. With an input history entry (info +0x38): each clock no earlier than now (compares against now, not the attack time); then 180b763d0(cycle, 1) and 180b76450(cycle, 1): both clocks + cycle from themselves.
3. No entry ("no history - using calculated time"): the clocks run on: a held full-auto trigger keeps the cycle's fractional grid (0.1 s = 6.4 ticks: 6, 7, 6, ... apart).
4. +0x10c0 = `(attack - (now + 1 tick))` as `(float)tick + ratio` (1813b8fb0, cvtdq2ps, addss), written on every shot. A held trigger's attack times keep the press's fraction, moved by each shot's clock-to-tick gap (a press at 100.5, the AK's next shot at 106.9).

## GetWeaponAttackTime (180a02c60)

1. The controller's current command; attack1_start_history_index (attack 2: +0x50) picks an entry; the index must be 0..count-1, else -1.
2. First: calculated time = the clock (180b54e20 / 180b54e50) + 1 tick (1813b9aa0) + the weapon's +0x10c0 as ticks (1813b9230, 1813b9090): the attack time without an entry.
3. With one: the entry's player tick and fraction, clamped to [lo, hi] = [(now + 1) - 4 ticks, now + 1] (1813b8ef0(4, 0), 1813b8fb0, 1809f69c0) ("Player tick from command clamped by server"); the render tick to lag compensation.
4. Then the shoot position from the 32-entry history at the attack time (unread past the search).

## SecondaryAttack (180a236b0)

1. No pawn returns. `canSwitch` = m_eSilencerType == 1 and now past m_flTimeSilencerSwitchComplete (18017e2d0(now, +0xfc0) == 1). `human` = the controller resolves and its +0x388 bit 0x100 is clear. Both: cl_silencer_mode (engine vfn 0x1a8, GetClientConVarValue) < 1 and silenced -> canSwitch false.
2. HasZoom: controller +0x708 +0x80 bit 1 returns (no clock change); m_bIsDefusing returns; m_zoomLevel + 1, past vfn 0xc28 -> 0; SetZoomLevel(level).
3. Else HasBurstMode: off -> "Switch_To_BurstFire", m_bBurstMode = 1, m_weaponMode = 1; on -> "Switch_To_FullAuto" / "_SemiAuto" (vfn 0xb90), m_bBurstMode = 0, m_weaponMode = 0; then Weapon.AutoSemiAutoSwitch (180f695d0: filter at the pawn's vfn 0x6b8 point, volume 1.0, sound level 100, flags `& 0xe5 | 5`, 0x181e23e88 = 1 around the emit).
4. Else canSwitch: 1809f7840(600 + IsSilenced, flags 0x1b, 0, force 1).
5. Else vfn 0xd28 revolver with the secondary ready: its alt fire; otherwise silenced, detachable, not switching (180a0eec0) and cl_silencer_mode < 1 -> 18021a430(pawn, "#Cstrike_TitlesTXT_Silencer_Disabled").
6. Every branch that didn't return: 180b76450(0.3, 0).

## SetZoomLevel (180a27870)

1. !HasZoom returns; m_zoomLevel = level; pawn and camera services or return; type = vfn 0xc60.
2. Not zoomed: m_weaponMode = 0; a sniper (type 5): cur = camera vfn 0xe0, def = vfn 0xe8, `SetFOV(def int, ZoomTime0, start = int(cur) - int((float)(int(def) - int(cur)) x -0.7))`; +0xf90 = 0; m_bIsScoped = 0; iron sight available -> 180a2d620, SetFOV(int def, 1 / PutDownSpeed, 0), 180a2f520(ctrl, 0).
3. Zoomed: m_weaponMode = 1; a sniper SetFOV(vfn 0xc70(level), vfn 0xc78(level), 0); +0xf90 = 0; m_bIsScoped = 1; iron sight: SetFOV((int)m_flIronSightFOV, 1 / PullUpSpeed, 0), 180a2f520(ctrl, 1).
4. 1809f7840(0x32, 0, 0, force 1); zoomed: the zoom sound (vfn 0xc38 through 1809f3e40(weapon, 0.8), volume 1), event "weapon_zoom" (a sniper) / "weapon_zoom_rifle".

## SetFOV (180a9b240) and GetFOV (180a7a250)

- SetFOV: requester null returns 0. Same m_iFOV and m_flFOVRate: with m_hZoomOwner the requester (or none and fov 0) nothing changes (returns 1); another live owner refuses (0). fov 0 -> m_hZoomOwner = -1, else the requester's handle. start < 1 -> int(GetFOV). m_iFOVStart = start, m_flFOVTime = curtime, m_iFOV = fov, m_flFOVRate = rate.
- GetFOV: target = m_iFOV, 0 -> vfn 0xe8. (float)m_iFOVStart == target -> target. Rate != 0: `t = (now - m_flFOVTime) / rate`; t < 1 -> `SimpleSplineRemapValClamped(t, 0, 1, start, target) = (3 - (c + c)) x c x c x (b - a) + a`, c clamped to [0, 1]; else target. Rate 0: m_iFOVStart = target (a write), target.

## ItemBusyFrame (180a0f0c0)

HasZoom, (zoomed or m_bIsScoped) and m_bInReload: m_bIsScoped = 0; cl_sniper_auto_rezoom 0 -> m_zoomLevel 0, else
m_bResumeZoom = 1; SetFOV(vfn 0xc70(0), vfn 0xc78(0), 0); m_weaponMode = 0. Then no attack button -> m_bWaitForNoAttack = 0.

## Movement and iron sights

- Accelerate (180ab6f3e): scoped = `vfn 0xcb0 (m_zoomLevel) > 0 && vfn 0xc28 (m_nZoomLevels) > 1 && GetMaxSpeed x 0.52 < 110`.
- 180a2d480 / 180a2d490 / 180a2d4c0 read the weapon's vdata through `ctrl - 0xd80` (the weapon + 0x320).
- AUG and SG 553: m_flIronSightFOV 45, pull-up 10, put-down 8. m_bIronSightAvailable's setter unread (controller +8, a disp8 store).

## Silencer switch

1. 1809f7840, the switch's part: old activity 600 / 601 (or 800 / 0x322 with the new one outside 0x321..0x323): both clocks now (mode 0), +0xfc0 = now, m_flNextAttack = now. Activity 600 / 601 with flags 0x1b: duration 100.0 (0xb takes vdata +0x7c4, 800 / 0x322 vdata +0x7c8) -> 180a276f0(force 1, mode 0): both clocks, +0xfc0 and m_flNextAttack now + 100. SecondaryAttack's 0.3 then puts the secondary at now + 0.3.
2. m_bSilencerOn / m_weaponMode are written only by spawn (180a24ba0), a reset (1809f2fb0), 180a1e2e0 (0x29 -> on, mode 1; 0x2a -> off, mode 0) and 180a1e7c0 (+0x2b8 on, mode 1; +0x2b9 off, mode 0; +0x2b4 -> vfn 0xd88).
3. 180b1cd40: WPN_ACTION_COMPLETE -> +0x2b4, WPN_SILENCER_ATTACH -> +0x2b8, WPN_SILENCER_DETACH -> +0x2b9.
4. vfn 0xd88 (180a1c800): activity 600 / 601 (and 500, 0xb, 100-102, 300, 0x1f5-0x1f9, 0x321 / 0x323, 0x3e9) -> activity 0x32 (forced), freeing the switch's clocks.
5. Data: viewmodel_gun.vnmgraph+usp / +m4a1s: states "SilencerOn/SilencerAttach" (node 222) and "SilencerOff/SilencerDetach" (53), each a clip with m_timedRemainingEvents WPN_ACTION_COMPLETE at <= 0.1 s; clips (animation/anims/viewmodel/<pistol|rifle>/_default_*/silencer_attach_*.vnmclip) 4.8333 s with WPN_SILENCER_ATTACH / _DETACH at 0.696552 (USP-S both), 0.710345 / 0.675862 (M4A1-S) of it.

## Deploy (vfn 0xa18)

1809fb560:
1. weapon +0x10a0 (when +0x10a8 set): 180a2f520(.., 2).
2. With a pawn: m_iShotsFired = 0, m_bResumeZoom = 0, m_bIsScoped = 0, 180a9b240(pawn +0xb48, pawn, 0, 0.0, 0), m_bWaitForNoAttack = 1.
3. m_fAccuracyPenalty: 0 with weapon_accuracy_reset_on_deploy, else `RemapValClamped(now - m_flLastAccuracyUpdateTime, 0, GetRecoveryTime, penalty, 0)`. m_flRecoilIndex = 0; +0xf74, +0xf78..f80, +0xf84 = 0.
4. No pawn: returns false. Else 1809f7840(weapon, 0xb, flags 0x13, 0, force 0): for 0xb the duration is m_flDeployDuration, whole (100 for most activities; 0x320 / 0x322 vdata +0x7c8); flags & 0x1b -> 180a276f0: `t = curtime + duration`; `mode = (force ^ 1) x 2` (force 0 -> 2); flags 1: 180b763d0(duration, mode), 2: 180b76450, 8: +0xfc0 = t (later only, unless forced), 0x10: m_flNextAttack = t (later only, unless forced). (Activities 0x258 / 0x259 / 0x31f / 0x321 / 0x322 first set both clocks to now, mode 0, and +0xfc0 / m_flNextAttack to now.)
5. m_iIronSightMode = 2, m_bInReload = 0, m_bInspectPending = 0, m_nDeployTick = now's tick; returns true. Always: +0xfd0 = 1.0, +0xfb0 = 0.

- 1809fb920 (gun): +0xfc0 = 0, m_iBurstShotsRemaining = 0, then 1809fb560; on true: HasZoom -> m_zoomLevel = 0, m_weaponMode = 0; revolver -> m_weaponMode = 1.
- 180a2b1a0 (knife): 1809fb560; on true m_flNextAttack = curtime + 1.0 (forced), +0x1280 = 1.
- 180a0efc0: `0 <= now tick - m_nDeployTick <= (int)(m_flDeployDuration x 64 + 0.5)`.

## Zoomed mouse (client 180b240b0)

a = (int) vfn 0x120, b = (int) vfn 0x118, c = (int) vfn 0x150, f = max(c, b); +0x149c = 1.0; f == a: +0x14a0 = 0, done;
else (a 0 -> 1) `+0x149c = zoom_sensitivity_ratio x f / a`, `+0x14a0 = cvar 182567c40 x that`.

## Unread

- 180a6ffb0; vfns 0xa98, 0xc98, 180b7c520 (the empty reload's tests); vfn 0xa68 & 2 (180b56580); controller +0x708 +0x80 bit 1; +0x388 bit 0x100's name.
- The shoot position history past the search; 180a23e30; the sniper re-zoom's other parts; attack3; inspect.
- Whether Weapon.AutoSemiAutoSwitch's filter drops the predicting owner (the dry fire's does).
- A shot with a round in stopping a shell reload; Reload's m_flNextAttack.
- CBaseCSGrenade's Deploy (1809b80b0); 180a2f520.
- When the server's weapon graph updates in the frame; the global transitions' blend into the silencer states.
- The zoomed mouse: which FOV each vfn is (taken: a the default, b GetFOV, c a floor); where +0x149c is read (taken: sensitivity x it).
- CS2's bots' usercmds (a bot's command without the history list).
