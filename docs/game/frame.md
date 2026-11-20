# The server frame: game-system events, usercmds, thinks

server_20261105. CS2Fixes: gamesystem.cpp:169-177 (ServerPreEntityThink: CGameUIHandler / CPointViewControlHandler::RunThink). hl2sdk igamesystem.h (slots). An older build's order (rubikon CS2_RUNTIME.md "The server frame": its 180dd4970 / 1805af790 are not function starts in server_20261105).

## Functions

| Address | Module | What |
|---|---|---|
| 180dd8a60 | server | the frame step (ServiceEvents' only caller, at 180dd8ecd) |
| 18053baa0 | server | call a stub over every game system |
| 18053355c | server | stub `mov rax, [rcx]; jmp [rax + 0xf8]`: IGameSystem slot 31, ServerPreEntityThink |
| 1805332fc | server | stub `jmp [rax + 0x100]`: slot 32, ServerPostEntityThink |
| 180f99720 | server | frame step 2 (unread) |
| 1805b70a0 | server | think manager vfn 0: the think pass |
| 18138e480 | server | ServiceEvents (the entity I/O queue: io-queue.md) |
| 180fc2f90 / 180fc2f10, 180beccd0, 180d17dd0 | server | after the post-think (unread; physics is the post-think event's handler) |
| 180cbc9a0 | server | slot -> controller (0 <= slot < maxClients: entity index slot + 1 by 180c10aa0 on the entity system) |
| 180c10aa0 | server | entity by index |
| 180927cb0 / 180e900a0 | server | an entity's simulate / think (think list) |
| 180b67390 | server | CBasePlayerController / CCSPlayerController vfn 0x508 PhysicsSimulate (vtables 0x18192f760 / 0x18191f800 slot 161) |
| 180a93970 | server | CCSPlayerController vfn 0x878 (slot 271) OnSimulateUserCommands, called at 180b6753e |
| 180ed4be0 | server | CPlayerCommandQueue ("OnSimulateUserCommands(), generating substitute command ..."; usercmd.md 5) |
| 180b675b0 | server | CBasePlayerPawn PhysicsSimulate (slot 161 of CCSPlayerPawn / CCSObserverPawn / CCSPlayerPawnBase / CBasePlayerPawn) |

## Fields

| Offset | Field |
|---|---|
| [0x181dbd3c0] = 0x181dbdc20 | the think manager (vtable 0x181808c38) |
| 0x1821b9750..70 | gpGlobals-like fields zeroed in step 2 |
| gpGlobals +0x10 | maxClients |
| identity +0x30 bit 9 | clear on a live entity (the think list's test) |
| pawn +0xc98 | controller |
| controller +0x4b8 | m_nTickBase |
| pawn +0xb50 | movement services (vfn 0xc8 RunCommand) |

## The frame step (180dd8a60)

1. 180dd8e12 / 180dd8e3d: 18053baa0(18053355c): **ServerPreEntityThink** (CS2Fixes' CGameSystem hooks it).
2. 180dd8e6f / 180dd8e81: two engine interfaces' vfn 0x50 / vfn 8 (unread); 0x1821b9750..70 zeroed; 180f99720.
3. 180dd8ec4: think manager vfn 0 = 1805b70a0.
4. 180dd8ecd: ServiceEvents 18138e480.
5. 180dd8f56 / 180dd8f7f: 18053baa0(1805332fc): **ServerPostEntityThink**.
6. 180fc2f90 / 180fc2f10, 180beccd0, 180d17dd0, ... (unread).

## The think pass (1805b70a0)

- Loop 1805b7100..1805b7196: slot 0 .. maxClients, 180cbc9a0(slot) (null skipped) -> vfn 0x508 PhysicsSimulate, in slot order.
- Then the think list (filled by manager vfn 8): each live entity through 180927cb0 / 180e900a0, then the rest (1805b7289.., unread).

## PhysicsSimulate

- Controller 180b67390: vfn 0x820, vfn 0xb8, ..., then at 180b6753e vfn 0x878 = 180a93970, which runs the command queue and through it RunCommands / RunCommand (usercmd.md 3).
- Pawn 180b675b0: reads its controller (pawn +0xc98), steps / restores the controller's m_nTickBase (+0x4b8) around movement services' vfn 0xc8 (RunCommand).

## Order

ServerPreEntityThink (CS2Fixes' RunThinks) -> every controller's usercmds, slot order -> other entities' thinks -> the I/O queue -> ServerPostEntityThink -> ... -> CS2Fixes' Hook_GameFramePost (RunTimers, after the whole GameFrame). So a game_ui's RunThink reads the buttons the last frame's commands left, its InValues are accepted before this frame's commands, its DelayInputs run after everything.

## Unread

- 180dd8a60 before step 1 (180dd8a60..180dd8daa: the frame's tick and timing); steps 2 and 6.
- The think list's order (vfn 8).
- When the pawn's PhysicsSimulate runs a command itself.
