# CMomentaryRotButton, ObjectCaps and PlayerUse's continuous use

server_20261105, read from the disassembly alone. Vtables (MSVC RTTI): CMomentaryRotButton 0x18181e558, CRotButton
0x18181dc88, CBaseButton 0x18181cae8, CCSPlayer_UseServices 0x181923de8.

## Functions

| Address | Module | What |
|---|---|---|
| 180d13c40 | server | CMomentaryRotButton Spawn (vfn 0x48) |
| 180d141a0 | server | the base's Spawn |
| 180d05040 | server | CMomentaryRotButton ObjectCaps (vfn 0xd0) |
| 180d19a00 | server | Use (vfn 0x498) |
| 180d009f0 / 180d17380 | server | vfn 0x8a8 / 0x8b0 (unread) |
| 180d01630 | server | MoveDone (vfn 0x4f8, CBaseToggle's) |
| 1802902a0 | server | vfn 0x628: true (the pusher adds the step to the QAngle) |
| 180ce39e0 | server | Blocked (vfn 0x4d8, CBaseToggle's) |
| 180617af0 | server | thinks by name |
| 180d19ff0 | server | UseMoveDone |
| 180d0b250 | server | ReturnMoveDone |
| 180d0fc60 | server | SetPositionMoveDone |
| 180d19690 | server | UpdateThink |
| 180cf9b40 | server | GetPos(angles) |
| 180cd1400 -> 180cfda50 | server | CMomentaryRotButton_API::SetPosition(v) |
| 180cd2190 | server | SetPositionImmediately |
| 180cd23e0 / 180cd2560 | server | _DisableUpdateTarget / _EnableUpdateTarget |
| 180d19650 | server | set Position output (value, activator) |
| 180d067a0 | server | reached outputs: ideal 1 OnFullyClosed, 0 OnFullyOpen, then OnReachedPosition |
| 180d06640 | server | the locked use (unread) |
| 180bc3df0 | server | float output set |
| 1801ab860 | server | builds a vector |
| 180a3e840, 180991030 / 18029f040 | server | the vector ops building m_start (180a3e840 twice, 180991030) / m_end |
| 180cdf210 | server | Use's angular velocity `m_vecMoveAng x (float(m_direction) x m_flSpeed)` |
| 18017b8d0 | server | clamp |
| 18017dc70 | server | curtime + 0.01 (ReturnMoveDone's next think) |
| 180308890 | server | tick interval 1/64 |
| 180ade3a0 | server | PlayerUse (CCSPlayer_UseServices) |
| 180c80ad0 / 180c80ae0 | server | button pressed / released this command |
| 180ac2cf0 | server | the use pick ([pickups.md](pickups.md)) |
| 180aba860 / 18093e020 | server | pass the pick's cone dots (unread) |
| 180d04f60 | server | CBaseEntity::ObjectCaps (CBaseClientUIEntity's, CCSTeam's, ... slot 0xd0) |
| 180d04ef0 | server | CBaseButton::ObjectCaps (CBaseButton, CPhysicalButton, CRotButton) |
| 180d551b0 | server | CBaseDoor::ObjectCaps (CBaseDoor, CRotDoor) |
| 180cce070 / 180cce210 | server | CBaseButton_API::Enable / Disable -> vfn 0x8b8 / 0x8c0 = 180cf1530 / 180cee2d0 |
| 1803d9790 | server | parent |
| 0x180ac3520 | server | FindUseEntity candidates (IsUseableEntity's shape; see use.md) |

## Fields

| Offset | Field |
|---|---|
| +0x288 | think set |
| +0x360 | spawnflags |
| CBaseToggle 0x854 | m_flMoveDistance |
| 0x87c | m_vecMoveAng |
| 0x8a4 | m_hActivator |
| CBaseButton 0x8d0 | m_angMoveEntitySpace |
| 0x8dc / 0x8dd | m_fStayPushed / m_fRotating |
| 0x8e0 | m_ls |
| 0x900 / 0x908 / 0x910 | m_sUseSound / m_sLockedSound / m_sUnlockedSound |
| 0x920 / 0x921 | m_bLocked / m_bDisabled |
| 0x924 | m_flSpeed |
| 0x928 | m_flUseLockedTime |
| 0x92c | m_bSolidBsp |
| 0x930 / 0x948 / 0x960 / 0x978 / 0x990 | OnDamaged / OnPressed / OnUseLocked / OnIn / OnOut |
| 0x9a8 | m_nState |
| 0x9ac | m_hConstraint |
| 0x9b8 / 0x9c0 | m_sGlowEntity / m_glowEntity |
| 0x9c4 | m_usable (spawnflag 1024) |
| 0x9c8 | m_szDisplayText |
| CMomentaryRotButton 0x9d0 | m_Position (float output, value at 0x9e8) |
| 0x9f0 / 0xa08 / 0xa20 / 0xa38 | OnUnpressed / OnFullyOpen / OnFullyClosed / OnReachedPosition |
| 0xa50 | m_lastUsed |
| 0xa54 / 0xa60 | m_start / m_end |
| 0xa6c | m_IdealYaw |
| 0xa70 | m_sNoise |
| 0xa78 | m_bUpdateTarget |
| 0xa7c | m_direction (int) |
| 0xa80 | m_returnSpeed |
| 0xa84 | m_flStartPosition |
| movement services +0x58 bit 5 | IN_USE held (0x20) |

## Constants

| Value | What |
|---|---|
| spawnflag 1 | not solid |
| spawnflag 32 | no return |
| spawnflag 64 / 128 / else | axis z (0, 0, 1) / x (1, 0, 0) / y (0, 1, 0) |
| spawnflag 256 (bit 8) | door: use opens |
| spawnflag 1024 (bit 10) | use activates (m_usable) |
| spawnflag 2048 | locked |
| spawnflag 8192 | locked jiggle |
| 100 | m_flSpeed when 0 |
| 0.1 s | move-done after the last Use |
| 0.01 s | ReturnMoveDone's think |
| 6 ticks | SetPosition's max move time |
| 0x21 / 0x22 / 0x23 | caps: impulse \| 0x20 / continuous \| 0x20 / both |
| caps bits | 1 impulse (the press), 2 continuous (every held command), 4 on / off |
| USE_OFF 0, USE_ON 1, USE_TOGGLE 3 | use types |
| 0.9238795 / 0.9848077 | cos 22.5 / 10 degrees: the pick's cone |
| 0x18195ed98.. | CBaseButton_API strings: Lock, Unlock, Press, PressIn, PressOut, Enable, Disable |

## Spawn 180d13c40

1. 180d141a0 first; m_vecMoveAng by spawnflag 64 / 128 / else (1801ab860); m_bUpdateTarget 1; m_flSpeed 0 -> 100.
2. m_flStartPosition outside [0, 1] -> a warning and clamp(m_IdealYaw, 0, 1) (on m_IdealYaw, not the start position:
   0 then); m_direction not +-1 -> 1.
3. m_flMoveDistance < 0 -> m_vecMoveAng x -1, distance negated.
4. `m_start = angles - (moveAng x distance) x start` (180a3e840 twice, 180991030); `m_end = angles + (moveAng x
   distance) x (1 - start)` (18029f040); m_IdealYaw = start; start 0 -> m_direction -1, start 1 -> 1.
5. spawnflag 2048 -> m_bLocked; 1024 -> m_lastUsed 0 and Position set to 0 (180bc3df0) when m_bUpdateTarget and it
   isn't 0.
6. Solid (spawnflag 1: not), MOVETYPE 6, m_usable = spawnflag 1024; the glow entity by name.

## GetPos 180cf9b40

sign = -1 when any lane of m_vecMoveAng < 0, else 1; the lane (64 z, 128 x, else y): `((angle - m_start) x sign) /
distance`, clamped [0, 1].

## ObjectCaps

- CMomentaryRotButton 180d05040: not disabled and usable -> 0x21, else 0; | the parent's caps & 7; usable -> | 0x22.
- CBaseEntity 180d04f60: the parent's caps & 0x87, | 0x80 when the parent's vfn 0x558 (a player); no parent 0.
- CBaseButton 180d04ef0: 0x21 when m_bDisabled clear and spawnflag 1024, else 0; | parent's caps & 7 (its vfn 0x558
  called, unused). Without 1024 a button is no use candidate (ze_resident_evil_3's 13 `[PR#]shq_button`).
- CBaseDoor 180d551b0: CBaseEntity's | 0x21 with spawnflag 256.
- Enable / Disable: m_bDisabled = 0 / 1, nothing else.

## Use 180d19a00

1. Disabled -> nothing. Locked -> 180d06640(this, activator) and, with spawnflag 8192, queued SetPosition events (2 /
   distance at 0.01 / 0.1 / 0.2 / 0.3 s, then _EnableUpdateTarget at 0.5).
2. m_hActivator = activator; m_lastUsed 0 -> m_direction negated, OnPressed (activator); m_lastUsed 1.
3. pos = GetPos; move-done time = m_flLocalTime + 0.1 (only a changed time stored).
4. m_direction > 0 and pos >= 1 -> no angular velocity, SetLocalAngles(m_end), OnFullyClosed (itself); m_direction < 0
   and pos <= 0 -> m_start, OnFullyOpen; else (move sound on a fresh press) angular velocity = `m_vecMoveAng x
   (float(m_direction) x m_flSpeed)`, m_pfnMoveDone = UseMoveDone.
5. No think set (+0x288): SetThink(UpdateThink), SetNextThink(curtime).

## Thinks

- UpdateThink 180d19690: Position = GetPos (no activator) when m_bUpdateTarget and changed; again next tick.
- UseMoveDone 180d19ff0: no angular velocity; Position = GetPos (activator itself); OnUnpressed (m_hActivator);
  m_lastUsed 0; not spawnflag 32 and m_returnSpeed > 0 -> m_pfnMoveDone = ReturnMoveDone, m_direction -1, move-done +
  0.1; else SetThink(null), m_pfnMoveDone null.
- ReturnMoveDone 180d0b250: pos <= 0 -> no angular velocity, m_start, Position 0 (no activator), move-done -1,
  m_pfnMoveDone null, no think, OnFullyOpen (itself); else angular velocity = `m_vecMoveAng x -m_returnSpeed`,
  move-done + 0.1, SetThink(UpdateThink) at `curtime + 0.01`.

## SetPosition 180cfda50(v)

1. m_IdealYaw = clamp(v, 0, 1); pos = GetPos; ideal > pos -> angular velocity moveAng x speed, m_direction 1; pos > ideal
   -> x -speed, -1; equal -> no angular velocity, nothing else.
2. m_pfnMoveDone = SetPositionMoveDone, SetThink(UpdateThink) now.
3. `target = m_start + moveAng x (ideal x distance)`; d = |target - angle| on the lane, `t = d / speed`; t under a tick
   -> angular velocity = `(moveAng x (d / tick)) x m_direction`, t = a tick. SetMoveDoneTime(t under a tick ? a tick :
   minss(6 ticks, t)).

- SetPositionMoveDone 180d0fc60: pos >= ideal with m_direction 1, or ideal >= pos with -1 -> no angular velocity,
  SetLocalAngles(`m_start + moveAng x (ideal x distance)`), no think, SetMoveDoneTime(-1), Position = ideal (180d19650,
  itself), then 180d067a0. Else SetPosition's aim again.
- SetPositionImmediately 180cd2190: m_IdealYaw = clamp(v, 0, 1), SetLocalAngles(`m_start + moveAng x (ideal x
  distance)`); no outputs.

## PlayerUse 180ade3a0

1. IN_USE held, pressed or released this command: the use pick 180ac2cf0 (the weapon path first).
2. The picked entity's caps: `(held and caps & 2) or (pressed and caps & 5)` -> Use (vfn 0x498, the pawn as activator
   and caller), USE_ON for caps & 4, else USE_TOGGLE; else released and caps & 4 -> Use with USE_OFF.

## Unread

- The locked use 180d06640; vfn 0x8a8 / 0x8b0; CBaseButton_API's Lock / Unlock / Press...; the move sound.
- The keyvalue names and `distance`'s default (taken 90); m_IdealYaw at Spawn (taken 0).
- Where OnPlayerUse fires (use.md).
- func_rot_button.
