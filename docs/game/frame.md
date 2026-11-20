# The server frame: game-system events, the usercmds, the thinks (server_20261105.dll, 2026-11-11)

Traced with tools/re (fnat.py, callers.py, vcalls.py, vtowner.py) for one question: where CS2Fixes' GameFramePre
handlers (ServerPreEntityThink: CGameUIHandler / CPointViewControlHandler::RunThink, gamesystem.cpp:169-177) run
against the players' usercmds. rubikon/CS2_RUNTIME.md "The server frame" has the same order from an older build
(its 180dd4970 / 1805af790 are not function starts in server_20261105.dll).

## The frame step, 180dd8a60

ServiceEvents' only caller (180dd8ecd). In order:

1. **180dd8e12 / 180dd8e3d**: 18053baa0(the stub 18053355c) over the game systems; the stub is `mov rax, [rcx];
   jmp [rax + 0xf8]`: IGameSystem slot 31, **ServerPreEntityThink** (hl2sdk igamesystem.h: slot 31 PreEntityThink,
   32 PostEntityThink; 31 x 8 = 0xf8). CS2Fixes' CGameSystem hooks it.
2. 180dd8e6f / 180dd8e81: two engine interfaces' vfn 0x50 / vfn 8 (unread); gpGlobals-like fields at 0x1821b9750..70
   zeroed; 180f99720 (unread).
3. **180dd8ec4: the think manager** ([0x181dbd3c0] = 0x181dbdc20, vtable 0x181808c38) **vfn 0 = 1805b70a0**.
4. **180dd8ecd: ServiceEvents 18138e480** (the entity I/O queue: io-queue.md).
5. **180dd8f56 / 180dd8f7f**: 18053baa0(the stub 1805332fc: `jmp [rax + 0x100]`): **ServerPostEntityThink**.
6. Then 180fc2f90 / 180fc2f10, 180beccd0, 180d17dd0, ... (unread: physics is the post-think event's handler,
   CS2_RUNTIME.md).

## The think pass, 1805b70a0 (think manager vfn 0)

- First loop (1805b7100..1805b7196): for slot 0 .. gpGlobals->maxClients (gpGlobals +0x10), 180cbc9a0(slot)
  (0 <= slot < maxClients: the entity at index slot + 1 by 180c10aa0 on the entity system, i.e. the slot's
  controller; null skipped) **-> vfn 0x508, PhysicsSimulate**, in slot order.
- Then the think list (vfn 8 of the manager fills it): each live entity (identity +0x30 bit 9 clear) through
  180927cb0 / **180e900a0** (its simulate / think), then the rest (1805b7289.., unread).

## The controller's PhysicsSimulate runs the usercmds

- **CBasePlayerController / CCSPlayerController vfn 0x508 = 180b67390** (vtowner: vtables 0x18192f760 / 0x18191f800
  slot 161): vfn 0x820, vfn 0xb8, ..., **180b6753e: vfn 0x878 = OnSimulateUserCommands 180a93970** (CCSPlayerController
  slot 271), which runs the command queue (usercmd.md 5: CPlayerCommandQueue 180ed4be0, "OnSimulateUserCommands(),
  generating substitute command ...") and through it RunCommands / RunCommand (usercmd.md 3).
- The pawn's own PhysicsSimulate (CBasePlayerPawn 180b675b0, slot 161 of CCSPlayerPawn / CCSObserverPawn /
  CCSPlayerPawnBase / CBasePlayerPawn) reads its controller from pawn +0xc98 and steps / restores the controller's
  m_nTickBase (+0x4b8) around the movement services' (pawn +0xb50) vfn 0xc8 (RunCommand); when it runs a command of
  its own is unread.

## So

ServerPreEntityThink (CS2Fixes' RunThinks) -> every controller's usercmds, in slot order -> the other entities'
thinks -> the I/O queue -> ServerPostEntityThink -> ... -> CS2Fixes' Hook_GameFramePost (RunTimers, after the whole
GameFrame). A game_ui's RunThink reads the buttons the last frame's commands left, its InValues are accepted before
this frame's commands, and its DelayInputs run after everything. The port: game.js tick calls gameUi.think() and
vc.think() before the commands, the map's 0 s timers run at stepRound's end (engine.runFramePost).

Unread: what 180dd8a60 does before step 1 (lines 180dd8a60..180dd8daa: the frame's tick and timing), steps 2 and 6,
the think list's order (vfn 8), when the pawn's PhysicsSimulate runs a command itself, the port's player order
against CS2's slot order (game.js walks players in join order).
