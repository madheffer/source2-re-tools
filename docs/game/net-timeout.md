# Connection timeouts (sv_timeout, cl_timeout)

engine2_20261015 (cvar registrations only, read with tools/re/game/cvardump.py; no decompile). pak01 csgo_english.txt.

## Constants

| Value | What |
|---|---|
| 20.0 | `sv_timeout` (object 0x1808da5e0, value via [0x1808da5e8] + 0x58; default `movss xmm2` at 180007aba; flags 0x82000) |
| 30.0 | `cl_timeout` (object 0x18069bb80, value via [0x18069bb88] + 0x58; default at 1800036fa; flags not read) |
| `NETWORK_DISCONNECT_TIMEDOUT` | the disconnect reason (enum descriptor in engine2 and networksystem; its number not read) |
| `#GameUI_Disconnect_TimedOut` | its token: "Unable to establish a connection with the gameserver." (`GameUI_Disconnect_ConnectionTimedout` has the same text) |

- cvardump's help strings for both were another cvar's (it takes the nearest `lea r9`): the help text is unread.

## Unread

- Where the server checks sv_timeout (which receive time it compares against, how often).
- Whether Steam Networking Sockets' own connection timeout ends the connection first.
- The client's check of cl_timeout.
- Whether the left-the-game chat line for a timed-out player uses this token's text as for the other reasons.
