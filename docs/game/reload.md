# A gun's reload and the silent reload (traced 2026-11-11; src/cs2web/sim/reload.js, loadout.js, sim fire_gate.rs)

server_20261105.dll, Ghidra ReVa (decompiler) and tools/re (disassembly, schema.py, vslot.py, vtowner.py). The weapon
graph is viewmodel_gun.vnmgraph+<variation> from CS2's pak01 (dumped with vpkstuff's --dump-animgraph); its clips'
events through lasers-bake --weapons (bake/WeaponBake.cs reloadClips).

## Fields (schema.py, CCSWeaponBase)

m_iWeaponGameplayAnimState **+0xefc** (short; the reload's states: 800 reloading, 801 the rounds in, 802 silent, 803
silent with the rounds in; 0x32 idle, 0xb deploy, 0x64 / 0x66 BaseGunFire's), m_bInReload **+0xfa8**,
m_bIsInStealthReload **+0xfc4**, m_bInSilentReloadSection +0xfc5, m_bSilentReloadStatPending +0xfc6,
m_flStealthReloadHoldStartTime **+0xfc8**, m_bReloadHeldSinceStart **+0xfcc**, m_flWeaponActionPlaybackRate **+0xfd0**,
m_flRecoilIndex +0xf98. Vdata: m_flDeployDuration +0x7c4, **m_flDisallowAttackAfterReloadStartDuration +0x7c8**,
+0x4e0 / +0x4e2 the reserve-as-clips / keep-loaded flags, +0x734 (a one-round add for single-shell guns). Weapon
services: m_flNextAttack +0xc0 (written by flag 0x10 below).

## Who runs what, per command

The pawn's **PreThink** (CCSPlayerPawn vfn 0xb10, 180236f50) calls **180a27170** (the silent reload) on the active
weapon. Then the movement, then the post-think (vfn 0xb20, 180ac4e30) -> the weapon services' 180b06e70: the active
weapon's **ItemPostFrame** (vfn 0xd00) first, then vfn 0xd08 / 0xd10 and ShootVerify, then
**CCSPlayerWeaponTimingGraph::RunTick** and its tags (vfn 0xd78, 180a1e7c0 for a gun).

## The R key in ItemPostFrame (180a0f4b0)

The else-chain after attack 1 (held, primary ready) / attack3 / attack 2 (held, secondary ready): **180b5ceb0(0x2000)**
(the button held in m_nButtons +0x58, or 180c80ad0: pressed in this command) and not m_bInReload: 1809fb150 (the rounds
a reload would load: min(reserve, max - clip), 0 when the vdata's +0x4e2 and it's negative; 1 with +0x734) == 0 and
the state isn't idle -> 1809f9f70 (unread); then with the primary clock passed (180b5d3c0) **180a10140**: 180a10400,
**Reload (vfn 0xd48)**, and on success the weapon_reload game event. The no-attack branch (the empty reload and the
m_iShotsFired / m_bWaitForNoAttack resets) is the chain's last else, so it doesn't run while R is held.
(180b5ce80 is the plain held test, the silent reload's.)

## Reload

- The gun's vfn 0xd48 **180a21970**: 180a21870 (vfn 0xd50 = the base Reload below, then a stats counter), the zoom
  reset (vfn 0xcc8, +0x1280 / +0xf70), the pawn's m_iShotsFired (+0x14d8) = 0, m_flRecoilIndex + 1, a game-system
  notify (1802302a0).
- The base **1809fb220**: a pawn; the count as 1809fb150; nonzero and vfn 0xa98: m_bInReload = 1, m_bIsInStealthReload
  = 0, **m_bReloadHeldSinceStart = (Clip1 != 0)** (an empty magazine never goes silent), m_flStealthReloadHoldStartTime
  = 0, then **1809f7840(this, 800, 0x13, count, 1)**.
- **1809f7840(weapon, state, flags, n, b)** sets the gameplay state: from 600 / 601 / 800 / 802 to a state outside
  801..803 both clocks are reset to now (180b763d0 / 180b76450 with 0, 0) and +0xfc0 / the services' +0xc0 set to now;
  +0xf00 = curtime; **a state outside 800..803 clears m_bInReload** (and m_bIsInStealthReload, the hold start, and puts
  m_flWeaponActionPlaybackRate back to 1.0); the graph's action (180a1e5e0); then with flags & 0x1b
  **180a276f0(this, flags, delay, b)** with delay = vdata +0x7c8 for 800 / 802, +0x7c4 for 0xb, else 100.0.
- **180a276f0**: flag 1 the primary clock (180b763d0, mode `(b ^ 1) x 2`: 0 here, from now), 2 the secondary
  (180b76450), 8 +0xfc0, 0x10 the weapon services' m_flNextAttack (+0xc0), each `delay` on. So **Reload puts both
  attack clocks at now + m_flDisallowAttackAfterReloadStartDuration** (2.2 s for the USP-S): Mouse 1 / 2 during a
  reload reach nothing, and nothing is kept for after it.

## The timing graph's tags (180b1cd40 -> 180a1e7c0)

180b1cd40 reads the graph's events into flags: **WPN_ACTION_COMPLETE** (symbol 182178640, 1800cab20) +0x2b4,
**WPN_RELOAD_ADD_AMMO** (182178660, 1800cae40) +0x2b5, **WPN_RELOAD_SILENT** (182178668) +0x2b6, ... 180a1e7c0 applies
them: +0x2b6 -> m_bInSilentReloadSection (0 clears +0xfc6); **+0x2b5 -> vfn 0xd80**; **+0x2b4 -> vfn 0xd88**.

- vfn 0xd80, the gun's **180a1dfb0**: the count as 1809fb150; nonzero and vfn 0xa98: **vfn 0xb28 180b61780(0, -1)**
  (or 1 round with +0x734): min(max - clip, n) taken from the reserve (vfn 0xaf8) into the clip (vfn 0xad0);
  m_flRecoilIndex = 0; state 801 (803 when it wasn't 800). (180a1e100 is a single-shell class's: the same, and +0x12a0
  = 1; not ported.)
- vfn 0xd88, the gun's **180a1c800** (180a1c960 the shotgun-like class's): in 801 / 803 m_bInReload = 0,
  m_bIsInStealthReload = 0, state 0x32; m_flWeaponActionPlaybackRate = 1.

In the graph (viewmodel_gun.vnmgraph+usp): the Reload state machine's Reload0 / Reload1 (a ClipSelector: partial_mag
reload_pistol, or empty_mag reload_empty_pistol when **weapon_ammo NearEqual 0**) and ReloadSilent0 / 1
(reload_silent_pistol). Each state's **WPN_ACTION_COMPLETE is a timed-remaining event at 0 s**: the clip's end. The
WPN_RELOAD_ADD_AMMO is a clip event. Reload0 -> ReloadSilent0 when action matches action_reload_silent (transition 178:
0.1 s, **flags 0x108 = MatchSourceTime | match in seconds**: the silent clip starts at the seconds the normal clip had
played). The silent clips are the normal ones at half speed: every gun's is exactly twice the length, its events at
twice the time (USP-S: 2.1667 s / 4.3333 s, ADD_AMMO 0.9 / 1.8). The empty clip exists for the slide-lock pistols and
the SCAR-20 (USP-S: ADD_AMMO 1.0).

## The silent reload: 180a27170 (PreThink)

With a pawn, m_bInReload and the state 800 or 802 (not 801 / 803: after the rounds go in nothing changes):
- `held = 180b5ce80(0x2000)` (the key in the buttons now). m_bReloadHeldSinceStart and not held: the hold start = 0,
  m_bReloadHeldSinceStart = 0, "released".
- State 800 and still m_bReloadHeldSinceStart: the hold start (a float, 0 = none) = curtime if 0; `curtime - start`
  (1801f95b0) **>= 0.25**: 1809f7840(0x322, 0, count, 1) (state 802: no clocks, m_bInReload kept), **1809f5880 with
  2.0**, m_bIsInStealthReload = 1, +0xfc6 = 1, a stats counter.
- State 802: cl_weapon_stealth_reload_toggle (the player's client cvar through the engine, 1821ba010 vfn 0x1a8) above 0
  makes 180b7c540(0x2000) (a press) count as released too; released: **m_flWeaponActionPlaybackRate = 2.0, 1809f5880
  with 0.5**, m_bIsInStealthReload = 0.
- **1809f5880(weapon, scale)**: for the primary then the secondary clock, when now (180cacba0) is before it: the rest
  (1813b8fb0 clock - now) as seconds (**180c629e0: `(float) tick x 0.015625 + ratio x 0.015625`**), times scale, set
  from now (180b763d0 / 180b76450 mode 0; each also moves the other clock when the cooldowns are linked).

So: R held 0.25 s into a magazine reload (rounds left in it) makes it silent: the rest of the clip at half speed and
the attack lock's rest doubled; letting go before the rounds are in brings the clip back to normal speed (rate 2 on the
half-speed clip) and halves the lock's rest.

## Port (src/cs2web/sim/reload.js; loadout.js; weapons/viewmodel.js; sim fire_gate.rs)

- fire_gate.rs: Cmd.reload and the R branch; `scale_remaining` (1809f5880, fire_abi op 2, fire-gate.js gunScale).
- loadout.js: startReload (Reload's clocks, m_iShotsFired 0), tryFire's order: reloadPreThink (stealthStep), the
  gate, finishReload (advance: the rounds at the playing clip's ADD_AMMO, m_bInReload off at its end). A shot or dry
  fire ends m_bInReload (BaseGunFire's state). The snapshot's `me.rl` (1 reloading, 2 silent).
- The viewmodel runs the same model on its frame clock: the clocks, the clip's sounds as it passes them, the graph's
  update times the playback rate (a graph baked before the silent reload: the normal clip at half speed while silent).
  client/core/weapon-sync.js corrects the magazine / reload by the server's state at the acked command.
- reload-test.mjs: the times above for the USP-S (0.9 s, 2.1667 s, the 2.2 s lock, the empty clip's 1.0 s, silent at
  0.25 s, its 1.8 s, R up at 1.0 s -> the rounds at 1.4 s and the lock at 2.575 s, held R after a shot).

## Not read / not ported

- 1809f9f70 (R with nothing to load, not idle); 180c80ad0 (a press inside one command is lost: the command carries the
  key as built); the weapon services' m_flNextAttack (+0xc0) and its readers (vfn 0xd08 / 0xd10).
- The single-shell reloads (shotguns: 180a1e100, their loop / outro states, their silent clips): the old stand-in.
- The R8's ItemPostFrame (180a0fe70 / 180a10400) and its R branch: held R reloads once its clock is ready.
- cl_weapon_stealth_reload_toggle (0 here), the silent reload's stat, who else hears a silent reload (others still
  hear the normal clip's sounds).
- The viewmodel graphs were rebaked 2026-11-11 (the 24 trainer-era gun graphs gained ReloadSilent0 / 1 and their
  reload_silent_* clips; bake-fp's pistols and shotguns had them already), and the viewmodel's graph runtime
  (weapons/fp/ag2/eval.js) now starts a MatchSourceTime | seconds (0x108) transition's clip at the source's seconds,
  so the silent clip picks up where the normal one was. The clips came from vpkstuff on Source 2 Viewer 20.0 next to
  19.2-baked ones (same bones and channels; the old files untouched). Left: that runtime's other match modes and offset.
