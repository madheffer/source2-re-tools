# A gun's reload and the silent reload

server_20261105. Graph: pak01 viewmodel_gun.vnmgraph+<variation>.

## Functions

| Address | Module | What |
|---|---|---|
| 180236f50 | server | CCSPlayerPawn PreThink (vfn 0xb10): calls 180a27170 on the active weapon |
| 180ac4e30 | server | post-think (vfn 0xb20) -> 180b06e70 |
| 180b06e70 | server | weapon services: ItemPostFrame (vfn 0xd00), vfn 0xd08 / 0xd10, ShootVerify, CCSPlayerWeaponTimingGraph::RunTick and its tags (vfn 0xd78) |
| 180a0f4b0 | server | ItemPostFrame (gun) |
| 180b5ceb0 | server | button held (m_nButtons +0x58) or pressed this command (180c80ad0) |
| 180b5ce80 | server | plain held test |
| 180c80ad0 | server | pressed inside the command |
| 180b7c540 | server | a press |
| 1809fb150 | server | rounds a reload would load: min(reserve, max - clip); 0 when vdata +0x4e2 and negative; 1 with +0x734 |
| 1809f9f70 | server | R with nothing to load, not idle (unread) |
| 180b5d3c0 | server | primary clock passed |
| 180a10140 | server | 180a10400, Reload (vfn 0xd48), weapon_reload event on success |
| 180a21970 | server | gun Reload (vfn 0xd48) |
| 180a21870 | server | vfn 0xd50 (base Reload) then a stats counter |
| 1809fb220 | server | base Reload |
| 1802302a0 | server | game-system notify |
| 1809f7840 | server | set gameplay state (weapon, state, flags, n, b) |
| 180b763d0 / 180b76450 | server | set primary / secondary clock |
| 180a1e5e0 | server | the graph's action |
| 180a276f0 | server | set clocks by flags (this, flags, delay, b) |
| 180b1cd40 | server | graph events -> flags |
| 180a1e7c0 | server | applies the tags (vfn 0xd78, gun) |
| 1800cab20 / 1800cae40 | server | register WPN_ACTION_COMPLETE / WPN_RELOAD_ADD_AMMO |
| 180a1dfb0 | server | gun vfn 0xd80 (add ammo) |
| 180b61780 | server | vfn 0xb28 (0, -1): reserve -> clip |
| 180a1e100 | server | single-shell class's add ammo (also +0x12a0 = 1) |
| 180a1c800 / 180a1c960 | server | vfn 0xd88 action complete: gun / shotgun-like |
| 180a27170 | server | the silent reload (PreThink) |
| 1801f95b0 | server | curtime - start |
| 1809f5880 | server | scale the clocks' rest (weapon, scale) |
| 180cacba0 | server | now |
| 1813b8fb0 | server | clock - now |
| 180c629e0 | server | ticks -> seconds |
| 180a0fe70 / 180a10400 | server | taken as the R8's ItemPostFrame (old reading). Disassembly: 180a10400 (0x180a10400..0x180a104f2) is called first by 180a10140 and from 180a0f6e7 (ItemPostFrame): when vfn 0xd28, +0xf70 = 1, +0xfa0 = 0x7fffffff, +0xfa4 = 0, and when +0xfbc is set it is cleared and the state set to 0x32 (1809f7840) |

## Fields

| Offset | Field |
|---|---|
| CCSWeaponBase +0xefc | m_iWeaponGameplayAnimState (short) |
| +0xf00 | = curtime on a state change |
| +0xf98 | m_flRecoilIndex |
| +0xfa8 | m_bInReload |
| +0xfc0 | clock (flag 8) |
| +0xfc4 | m_bIsInStealthReload |
| +0xfc5 | m_bInSilentReloadSection |
| +0xfc6 | m_bSilentReloadStatPending |
| +0xfc8 | m_flStealthReloadHoldStartTime (0 = none) |
| +0xfcc | m_bReloadHeldSinceStart |
| +0xfd0 | m_flWeaponActionPlaybackRate |
| +0x1280 / +0xf70 | zoom reset (vfn 0xcc8) |
| +0x12a0 | single-shell flag |
| +0x2b4 / +0x2b5 / +0x2b6 | tag flags: ACTION_COMPLETE / RELOAD_ADD_AMMO / RELOAD_SILENT |
| vdata +0x4e0 / +0x4e2 | reserve-as-clips / keep-loaded flags |
| vdata +0x734 | one-round add (single-shell) |
| vdata +0x7c4 | m_flDeployDuration |
| vdata +0x7c8 | m_flDisallowAttackAfterReloadStartDuration |
| weapon services +0xc0 | m_flNextAttack |
| pawn +0x14d8 | m_iShotsFired |

## Constants

| Value | What |
|---|---|
| 800 / 801 / 802 (0x322) / 803 | reloading / rounds in / silent / silent with rounds in |
| 0x32 / 0xb / 0x64 / 0x66 | idle / deploy / BaseGunFire's |
| 600 / 601 | states whose exit resets the clocks too |
| 0x2000 | IN_RELOAD |
| 0x13 | Reload's flags |
| 0.25 s | hold to go silent |
| 2.0 / 0.5 | silent: clocks' rest x2 / released: x0.5 (rate 2.0) |
| 100.0 | delay for states other than 800 / 802 / 0xb |
| 182178640 / 182178660 / 182178668 | symbols WPN_ACTION_COMPLETE / WPN_RELOAD_ADD_AMMO / WPN_RELOAD_SILENT |
| 1821ba010 vfn 0x1a8 | engine client convar read (cl_weapon_stealth_reload_toggle, 0 here) |
| 2.2 s | USP-S m_flDisallowAttackAfterReloadStartDuration |

## Per command

PreThink (180236f50: the silent reload 180a27170 on the active weapon), then the movement, then the post-think
(180ac4e30 -> 180b06e70): the active weapon's ItemPostFrame (vfn 0xd00) first, then vfn 0xd08 / 0xd10 and
ShootVerify, then CCSPlayerWeaponTimingGraph::RunTick and its tags (vfn 0xd78, 180a1e7c0 for a gun).

## R in ItemPostFrame (180a0f4b0)

Else-chain after attack 1 (held, primary ready) / attack3 / attack 2 (held, secondary ready): 180b5ceb0(0x2000) and
not m_bInReload: 1809fb150 == 0 and state not idle -> 1809f9f70; then with the primary clock passed, 180a10140. The
no-attack branch (empty reload, m_iShotsFired / m_bWaitForNoAttack resets) is the last else: not run while R is held.

## Reload

- 180a21970: 180a21870, zoom reset, m_iShotsFired = 0, m_flRecoilIndex + 1, 1802302a0.
- 1809fb220: a pawn; count as 1809fb150; nonzero and vfn 0xa98: m_bInReload = 1, m_bIsInStealthReload = 0,
  **m_bReloadHeldSinceStart = (Clip1 != 0)** (an empty magazine never goes silent), hold start = 0, then
  1809f7840(this, 800, 0x13, count, 1).
- 1809f7840: from 600 / 601 / 800 / 802 to a state outside 801..803: both clocks reset to now (with 0, 0), +0xfc0 and
  services +0xc0 = now; +0xf00 = curtime; a state outside 800..803 clears m_bInReload, m_bIsInStealthReload, the hold
  start, rate = 1.0; graph action (180a1e5e0); with flags & 0x1b, 180a276f0(this, flags, delay, b), delay = vdata +0x7c8
  for 800 / 802, +0x7c4 for 0xb, else 100.0.
- 180a276f0: flag 1 primary clock (mode `(b ^ 1) x 2`: 0 here, from now), 2 secondary, 8 +0xfc0, 0x10 services
  m_flNextAttack; each `delay` on. Reload puts both attack clocks at now + m_flDisallowAttackAfterReloadStartDuration:
  Mouse 1 / 2 during a reload do nothing, nothing is buffered.

## Tags (180b1cd40 -> 180a1e7c0)

- +0x2b6 -> m_bInSilentReloadSection (0 clears +0xfc6); +0x2b5 -> vfn 0xd80; +0x2b4 -> vfn 0xd88.
- 180a1dfb0: count as 1809fb150; nonzero and vfn 0xa98: 180b61780(0, -1) (1 round with +0x734): min(max - clip, n)
  from reserve (vfn 0xaf8) into clip (vfn 0xad0); m_flRecoilIndex = 0; state 801 (803 when it wasn't 800).
- 180a1c800: in 801 / 803 m_bInReload = 0, m_bIsInStealthReload = 0, state 0x32; rate = 1.

## The graph (viewmodel_gun.vnmgraph+usp)

- Reload state machine: Reload0 / Reload1 (ClipSelector: partial_mag reload_pistol, empty_mag reload_empty_pistol when
  weapon_ammo NearEqual 0), ReloadSilent0 / 1 (reload_silent_pistol).
- WPN_ACTION_COMPLETE: timed-remaining event at 0 s (clip end). WPN_RELOAD_ADD_AMMO: a clip event.
- Reload0 -> ReloadSilent0 on action_reload_silent (transition 178: 0.1 s, flags 0x108 = MatchSourceTime | match in
  seconds: the silent clip starts at the seconds the normal one had played).
- Silent clips are the normal ones at half speed (twice the length, events at twice the time). USP-S: 2.1667 s /
  4.3333 s, ADD_AMMO 0.9 / 1.8; empty clip (slide-lock pistols, SCAR-20) USP-S ADD_AMMO 1.0.

## Silent reload (180a27170)

With a pawn, m_bInReload, state 800 or 802:
1. `held = 180b5ce80(0x2000)`. m_bReloadHeldSinceStart and not held: hold start = 0, m_bReloadHeldSinceStart = 0, "released".
2. State 800 and still m_bReloadHeldSinceStart: hold start = curtime if 0; `curtime - start >= 0.25`:
   1809f7840(0x322, 0, count, 1) (no clocks, m_bInReload kept), 1809f5880 with 2.0, m_bIsInStealthReload = 1,
   +0xfc6 = 1, a stats counter.
3. State 802: cl_weapon_stealth_reload_toggle > 0 makes 180b7c540(0x2000) count as released; released: rate = 2.0,
   1809f5880 with 0.5, m_bIsInStealthReload = 0.

1809f5880(weapon, scale): primary then secondary, when now is before it: the rest (`clock - now`) in seconds
(`(float) tick x 0.015625 + ratio x 0.015625`) x scale, set from now (mode 0; each also moves the other when the
cooldowns are linked).

Worked example (USP-S): normal ADD_AMMO 0.9 s, end 2.1667 s, lock 2.2 s, empty clip 1.0 s; silent from 0.25 s, its
ADD_AMMO at 1.8 s; R released at 1.0 s -> the rounds at 1.4 s, the lock at 2.575 s.

## Unread

- 1809f9f70; 180c80ad0 (a press inside one command); services m_flNextAttack and its readers (vfn 0xd08 / 0xd10).
- Single-shell reloads (shotguns: 180a1e100, loop / outro states, silent clips).
- R8's ItemPostFrame (180a0fe70 / 180a10400) and its R branch (held R reloads once its clock is ready).
- cl_weapon_stealth_reload_toggle's default, the silent reload's stat, who else hears a silent reload.
- The graph runtime's other match modes and offset (besides MatchSourceTime | seconds 0x108).
