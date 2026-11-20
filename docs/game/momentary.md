# CMomentaryRotButton and PlayerUse's continuous use (server.dll 2026-11-05)

Working notes for RUST_PORT 4f-6. Addresses are server_20261105.dll (vtables through MSVC RTTI:
CMomentaryRotButton 0x18181e558, CRotButton 0x18181dc88, CBaseButton 0x18181cae8, CCSPlayer_UseServices
0x181923de8). Read from the disassembly alone (Ghidra's ReVa was down that session: tools/re/game/disasm.py, and the
string / caller scans the session wrote), every sum in its order. Ported: web/src/world/entities/classes/
momentary.js, web/server/cs2web/combat/combat.js (use); checked by web/src/cs2web/world/momentary-test.mjs.

## Fields (schema.py)

CBaseButton: m_angMoveEntitySpace 0x8d0, m_fStayPushed 0x8dc, m_fRotating 0x8dd, m_ls 0x8e0, m_sUseSound 0x900,
m_sLockedSound 0x908, m_sUnlockedSound 0x910, m_bLocked 0x920, m_bDisabled 0x921, m_flSpeed 0x924,
m_flUseLockedTime 0x928, m_bSolidBsp 0x92c, OnDamaged 0x930, OnPressed 0x948, OnUseLocked 0x960, OnIn 0x978, OnOut
0x990, m_nState 0x9a8, m_hConstraint 0x9ac, m_sGlowEntity 0x9b8, m_glowEntity 0x9c0, m_usable 0x9c4 (spawnflag
1024), m_szDisplayText 0x9c8. CBaseToggle: m_flMoveDistance 0x854, m_vecMoveAng 0x87c, m_hActivator 0x8a4.

CMomentaryRotButton: m_Position 0x9d0 (a float output: its value at 0x9e8), OnUnpressed 0x9f0, OnFullyOpen 0xa08,
OnFullyClosed 0xa20, OnReachedPosition 0xa38, m_lastUsed 0xa50, m_start 0xa54, m_end 0xa60, m_IdealYaw 0xa6c,
m_sNoise 0xa70, m_bUpdateTarget 0xa78, m_direction 0xa7c (int), m_returnSpeed 0xa80, m_flStartPosition 0xa84.

Virtuals (vdiff against CBaseButton): Spawn 0x48 180d13c40, ObjectCaps 0xd0 180d05040, Use 0x498 180d19a00, 0x8a8
180d009f0 / 0x8b0 180d17380 (not read); MoveDone 0x4f8 is CBaseToggle's 180d01630, vfn 0x628 1802902a0 (true: the
pusher adds the step to the QAngle), Blocked 0x4d8 CBaseToggle's 180ce39e0. Thinks by name (180617af0):
UseMoveDone 180d19ff0, ReturnMoveDone 180d0b250, SetPositionMoveDone 180d0fc60, UpdateThink 180d19690.

## The button

- **Spawn** (180d13c40): 180d141a0 (the base's) first; m_vecMoveAng = spawnflag 64 (0, 0, 1), 128 (1, 0, 0), else (0,
  1, 0) (1801ab860 builds it); m_bUpdateTarget 1; m_flSpeed 0 → 100; m_flStartPosition outside [0, 1] → a warning
  and clamp(m_IdealYaw, 0, 1) (18017b8d0 on m_IdealYaw, not on the start position: it is 0 then); m_direction not
  ±1 → 1; m_flMoveDistance below 0 → m_vecMoveAng x -1 and the distance negated; m_start = angles - (moveAng x
  distance) x start (180a3e840 twice, 180991030), m_end = angles + (moveAng x distance) x (1 - start) (18029f040);
  m_IdealYaw = start; start 0 → m_direction -1, start 1 → 1; spawnflag 2048 → m_bLocked; spawnflag 1024 → m_lastUsed
  0 and the Position output set to 0 (180bc3df0) when m_bUpdateTarget and it isn't 0; the solid (spawnflag 1: not
  solid), MOVETYPE 6, m_usable = spawnflag 1024; the glow entity found by name.
- **GetPos** (180cf9b40, angles): sign = -1 when any lane of m_vecMoveAng is below 0, else 1; the lane (spawnflag
  64 z, 128 x, else y): ((angle - m_start) x sign) / distance, clamped to [0, 1] (18017b8d0).
- **ObjectCaps** (180d05040): not disabled and usable → 0x21, else 0; a parent's ObjectCaps & 7 or'ed in; usable →
  | 0x22. So a usable, enabled button is 0x23: impulse (1) and continuous (2).
- **Use** (180d19a00): disabled → nothing. Locked → 180d06640(this, activator) and, with spawnflag 8192, a queue of
  SetPosition events (the jiggle: 2 / distance, 0.01 / 0.1 / 0.2 / 0.3 s, then _EnableUpdateTarget at 0.5; not
  ported). Else: m_hActivator = the activator; m_lastUsed 0 → m_direction negated, OnPressed (activator); m_lastUsed
  1; pos = GetPos; the move-done time = m_flLocalTime + 0.1 (only a changed time is stored); m_direction > 0 and pos
  >= 1 → no angular velocity, SetLocalAngles(m_end), OnFullyClosed (itself); m_direction < 0 and pos <= 0 → m_start,
  OnFullyOpen; else (the move sound on a fresh press) angular velocity = m_vecMoveAng x (float(m_direction) x
  m_flSpeed) (180cdf210), m_pfnMoveDone = UseMoveDone. Then with no think set (+0x288): SetThink(UpdateThink),
  SetNextThink(curtime).
- **UpdateThink** (180d19690): Position = GetPos (activator none) when m_bUpdateTarget and it changed; again next
  tick.
- **UseMoveDone** (180d19ff0, 0.1 s after the last Use): no angular velocity; Position = GetPos (activator itself);
  OnUnpressed (activator m_hActivator); m_lastUsed 0; not spawnflag 32 and m_returnSpeed > 0 → m_pfnMoveDone =
  ReturnMoveDone, m_direction -1, the move-done time + 0.1; else SetThink(null), m_pfnMoveDone null.
- **ReturnMoveDone** (180d0b250): pos <= 0 → no angular velocity, m_start, Position 0 (no activator), the move-done
  time -1, m_pfnMoveDone null, no think, OnFullyOpen (itself); else angular velocity = m_vecMoveAng x -m_returnSpeed,
  the move-done time + 0.1 (so it runs again), SetThink(UpdateThink) at curtime + 0.01 (18017dc70).
- **SetPosition** (CMomentaryRotButton_API::SetPosition 180cd1400 → 180cfda50, v): m_IdealYaw = clamp(v, 0, 1); pos
  = GetPos; ideal > pos → angular velocity moveAng x speed, m_direction 1; pos > ideal → x -speed, -1; equal → no
  angular velocity, nothing else. m_pfnMoveDone = SetPositionMoveDone, SetThink(UpdateThink) now. target = m_start +
  moveAng x (ideal x distance); d = |target - angle| on the lane, t = d / speed; t under a tick (180308890: 1/64) →
  angular velocity = (moveAng x (d / tick)) x m_direction, t = a tick. SetMoveDoneTime(t under a tick ? a tick :
  minss(6 ticks, t)).
- **SetPositionMoveDone** (180d0fc60): pos >= ideal with m_direction 1, or ideal >= pos with -1 → no angular
  velocity, SetLocalAngles(m_start + moveAng x (ideal x distance)), no think, SetMoveDoneTime(-1), Position = ideal
  (180d19650, activator itself), then 180d067a0: ideal 1 → OnFullyClosed, 0 → OnFullyOpen, then OnReachedPosition
  (all itself). Else the same aim as SetPosition again.
- **SetPositionImmediately** (180cd2190): m_IdealYaw = clamp(v, 0, 1), SetLocalAngles(m_start + moveAng x (ideal x
  distance)); no outputs. **_DisableUpdateTarget** (180cd23e0) / **_EnableUpdateTarget** (180cd2560): m_bUpdateTarget
  0 / 1. CBaseButton_API: Lock, Unlock, Press, PressIn, PressOut, Enable, Disable (strings 0x18195ed98.., not read).

## PlayerUse (180ade3a0, CCSPlayer_UseServices)

- The buttons (the pawn's movement services +0x58 bit 5 = IN_USE held; 180c80ad0 / 180c80ae0 (0x20) pressed /
  released this command). With any of the three: the use pick (180ac2cf0, docs/game/pickups.md), the weapon path
  first; then the picked entity's ObjectCaps (vfn 0xd0): (held and caps & 2) or (pressed and caps & 5) → Use (vfn
  0x498) with the pawn as activator and caller, USE_ON (1) for caps & 4, else USE_TOGGLE (3); else released and caps
  & 4 → Use with USE_OFF (0). So caps bit 1 is impulse (the press), 2 continuous (every held command), 4 on / off.
- The 0.9238795 / 0.9848077 dot (cos 22.5 / 10 degrees) passed to the pick: 180ac2cf0's cone, by 180aba860 /
  18093e020 (not read).

## What the port does, and its stand-ins

momentary.js keeps the fields in e.state; the think is the pusher's step (toggle.js, euler) with CBaseToggle's
MoveDone calling the class's table, then UpdateThink when due. combat.js runs the use pick on every command +use is
held, pressed or released and uses CS2's rule with each class's caps (caps.js; the pick itself is FindUseEntity in
the sim, use.md). Stand-ins (TODO(trace)): the locked use and the jiggle;
the move sound; the keyvalue names and
`distance`'s default (90); m_IdealYaw at Spawn (0); the Use's type (not passed: the button ignores it);
OnPlayerUse fired by the 'u' stimulus on every held command (where CS2 fires it is untraced); the think time's f32
rounding.

## The other classes' ObjectCaps (2026-11-10)

- **CBaseEntity::ObjectCaps** (180d04f60; CBaseClientUIEntity's, CCSTeam's, ... slot 0xd0): the parent (1803d9790)
  gives its caps (vfn 0xd0) & 0x87, | 0x80 when the parent's vfn 0x558 (a player) answers; no parent: 0.
- **CBaseButton::ObjectCaps** (180d04ef0; CBaseButton, CPhysicalButton and CRotButton slot 0xd0): 0x21 (impulse |
  0x20) when m_bDisabled (+0x921, schema; m_bLocked is +0x920) is clear and spawnflag 1024 (+0x360 bit 10, "use
  activates") is set, else 0; | the parent's caps & 7 (its vfn 0x558 is called, the answer unused). So a button
  without spawnflag 1024 is no use candidate at all.
- **CBaseDoor::ObjectCaps** (180d551b0; CBaseDoor and CRotDoor): CBaseEntity's (180d04f60) | 0x21 with spawnflag 256
  (+0x360 bit 8, "use opens").
- **CBaseButton_API::Enable / Disable** (180cce070 / 180cce210 -> vfn 0x8b8 / 0x8c0 = 180cf1530 / 180cee2d0): m_bDisabled
  = 0 / 1, nothing else. Lock / Unlock are the other two flag inputs (180d06640's locked use not read).
- Ported: web/src/world/entities/caps.js (objectCaps, baseCaps, parentUseCaps), movers.js func_button caps + Enable /
  Disable, func_door / func_door_rotating caps, momentary.js through parentUseCaps; game.usables() keeps an entity
  only with a use bit (caps & 7), in place of the door-only spawnflag test (CS2's FindUseEntity candidates, Source's
  IsUseableEntity shape: TODO(trace) 0x180ac3520). RE3's 13 `[PR#]shq_button` (no spawnflag 1024) were E-usable
  here; now, as in CS2, they aren't.
- Stand-ins left: a parent of a class with no caps() here is taken as CBaseEntity's; func_rot_button isn't a class
  here. Props', physboxes' and prop doors' ObjectCaps and FindUseEntity are traced now (use.md, 2026-11-11).

## To trace next

1. Where OnPlayerUse fires (props' and physboxes' ObjectCaps and FindUseEntity: use.md).
2. The locked use 180d06640.
