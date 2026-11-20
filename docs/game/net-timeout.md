# The connection timeouts: sv_timeout, cl_timeout

Read 2026-11-12 from `engine2_20261015.dll` with `tools/re/game/cvardump.py` (no decompile: ReVa was down). Only the
registrations' defaults; how the engine uses them is unread.

| cvar | object | default (the setup's `movss xmm2`) | flags (r8d) |
|---|---|---|---|
| `sv_timeout` | 0x1808da5e0 (value via [0x1808da5e8] + 0x58) | **20.0** (180007aba) | 0x82000 |
| `cl_timeout` | 0x18069bb80 (value via [0x18069bb88] + 0x58) | **30.0** (1800036fa) | not read (the tool printed none) |

- cvardump's help strings for both were another cvar's (it takes the nearest `lea r9`): the help text is unread.
- The disconnect reason: `NETWORK_DISCONNECT_TIMEDOUT` with the token `#GameUI_Disconnect_TimedOut` (the enum's
  descriptor in engine2 and networksystem; its number not read). csgo_english.txt (pak01):
  `"GameUI_Disconnect_TimedOut" "Unable to establish a connection with the gameserver."`
  (`GameUI_Disconnect_ConnectionTimedout` has the same text).

**Unread (TODO):** where the server checks sv_timeout (which receive time it compares against, how often), whether
Steam Networking Sockets' own connection timeout ends the connection first, the client's check of cl_timeout, and
whether the left-the-game chat line for a timed-out player uses this token's text as it does for the other reasons.

**Used by:** web/server/cs2web/core/net.js `SV_TIMEOUT_MS` (20 s without a frame from a socket, the answers to the server's
WebSocket pings included: the player is removed with DISCONNECT.TIMEDOUT and the socket terminated),
web/src/cs2web/client/core/net.js `CL_TIMEOUT_MS` (30 s without a message: the client closes and shows the reason). The checks
themselves (a ping and a look every second) are ours.
