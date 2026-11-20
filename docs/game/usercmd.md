# The usercmd's timing: the client's input history, the server's tickbase and command queue (traced 2026-11-11)

client_20261105.dll (source2-compiler tools/re/binaries) and server_20261105.dll. What decides **when** a shot
happens: which history entry a press is, the attack time it gives, and the tick a command runs at. The port's side:
src/cs2web/client/core/tick-input.js, client/core/game.js localTick, src/cs2web/sim/move-state.js cleanCmd (cmd[11]), server/cs2web/combat/combat.js
act, sim/src/combat/fire_gate.rs `attack_time`.

## 1. The protobuf messages (cs_usercmd.proto, decoded from client.dll by tools/re/game/protodesc.py)

`CSGOInputHistoryEntryPB`: 2 view_angles, 4 render_tick_count, 5 render_tick_fraction, 6 player_tick_count,
7 player_tick_fraction, 12 cl_interp, 13 sv_interp0, 14 sv_interp1, 15 player_interp, 64 frame_number,
65 target_ent_index, 66 shoot_position, 67 target_head_pos_check, 68 target_abs_pos_check, 69 target_abs_ang_check.

`CSGOUserCmdPB`: 1 base (CBaseUserCmdPB), 2 input_history (repeated), 6 attack1_start_history_index,
7 attack2_start_history_index, 9 left_hand_desired, 11 / 12 / 13 is_predicting_body_shot_fx / head_shot_fx /
kill_ragdolls.

In memory (CSGOUserCmdPB's Clear 1807b1e20 and ByteSize 1807b1ed0, vtable 181bd1e30): has-bits +0x10, input_history
RepeatedPtrField +0x18 (count +0x20, rep +0x28), base +0x30 (bit 1), the four bools +0x38..0x3b (bits 2..0x10),
**attack1_start_history_index +0x3c (bit 0x20), attack2 +0x40 (bit 0x40), both -1 when cleared**. The CCSGOUserCmd
wrapper holds the message at +0x10, so the server reads them at cmd +0x4c / +0x50 and the history at +0x38 / count
+0x30 (fire-gate.md 3, GetWeaponAttackTime). The server's entry: player_tick_count +0x68, player_tick_fraction +0x6c.

## 2. The client's history: CCSGOInput

**180d07790** (CCSGOInput, called every frame and at the start of the command's finish 180d04300): with the input's
button-event list (180b72060(input, slot), events of 0x20 bytes from +0x38, count +0x2c, the last one read kept at
input +0xbf0): **an event whose button is 1 (IN_ATTACK) or 0x800 (IN_ATTACK2) sets input +0xbc8[i] to its down byte
and marks attack i pressed when it is a down event** (i = 0 for IN_ATTACK). The frame's view record (vfn 0x568 of the
object at [182566100]: +0 the frame number, +4.. render tick / fraction and player tick / fraction, +0x18 the view
data). A frame with the same number and no attack press adds nothing. Else the frame's entry (0x60 bytes in the array
at input +0xbe0, count +0xbd8, capacity +0xbe8): +0..+0xf the ticks and fractions, +0x10..+0x4c the view angles,
shoot position, target ent (-1), the target checks; +0x50 the frame number; +0x54 its index in the command (-1 until
sent); a frame already recorded is reused. Then **for each attack i pressed in this frame, when input +0xbcc[i] is -1
it takes this entry's index** (the first press of the command wins); for attack 1 the weapon services' shoot position
record (180d0c170) is refreshed too.

**180d04300** (CCSGOInput vfn 0xc8, the command's history out): 180d07790 first; with more than one entry, when the
newest's tick (+8) is below the oldest's (the clock went back), only the newest is kept (moved to the front,
181a5b480) and a set press index becomes 0; a press index at or past the count is logged and cleared. With more than 4 entries and cl_csgo_shoot_trim_input_frames ([1825809e8]) on, a reduction picks which go out (section 12)
(each pressed entry always, 180ce0280 / 180cfc880 write one); else every entry goes out. **attack1_start_history_index
= the pressed entry's +0x54 (its position in the command's input_history)**, has-bit 0x20, else -1 (has-bit cleared);
the same for attack 2 (bit 0x40). An index at or past the history's count is logged and set to -1. Then the
is_predicting_* bools from the pawn's weapon (vfn 0xab8, +0x1ecc, +0x14bc's target) and three cvars.

So: **a command has an attack's history entry exactly when the attack button went down (a down event) in one of its
frames; holding it adds none; the entry is the frame of the first press**, with that frame's player tick and fraction
(the attack time) and render tick and fraction (the lag compensation's target).

The port (tick-input.js readTick): each mouse button event carries its button and down; the first down of each attack
button in the tick gives its time as the fraction of the tick (the browser event's time: the port has no frames inside
a tick, so the event is its own frame); a trigger that went down without a mouse event (touch, a test's trigger) is
pressed at the tick's read (0.99999). Sent as cmd[11] [attack1, attack2], -1 for none.

## 3. The server's tick for a command

- **RunCommand 180c7cb80** (CPlayer_MovementServices vfn 0xc8; CCSPlayer_MovementServices' 180ae1920 calls it after
  180a9be50): when cmd +0x90 is 0 and gpGlobals' frametime (+0x34) isn't 0, the controller's **m_nTickBase (+0x4b8)
  + 1** (SetTickBase 180b78640). Then gpGlobals' tick (+0x44) = m_nTickBase, curtime (+0x30) = tick x 1/64, the
  fraction (+0x50) 0, frametime 1/64 when cmd +0x90 is 0 (else 0); 180b70e10 / 180b70d20 note the tick and command
  number; 180c7b050 runs it (the movement, ItemPostFrame); vfn 0x158; gpGlobals restored.
- **vfn 0xd0 180c7cdb0** (RunCommands(cmds, n, last)): drops the commands older than the last's number less a limit
  (cvar at [182191508] +0x58, or 180c6c240's) through vfn 0xd8; sets gpGlobals' tick to m_nTickBase, curtime to it /
  64, **frametime 0** and the fraction 0, then for each: 180b750e0 (the current command), vfn 0xc8 (RunCommand: no
  tickbase step, frametime 0), 180b75cd0. Then the last command's 180b511d0 and gpGlobals restored.
- **CPlayerCommandQueue 180ed4be0** (vtable 1819d04a0; cvars cq_enable, cq_dilation_percentage, cq_buffer_bloat_msecs_max,
  cq_max_starved_substitute_commands, sv_cq_min_queue, sv_cq_trim_bloat_*, sv_cq_trim_catchup_remainder; logs "STARVE",
  "BLOAT", "catchup"): **before each run of commands it sets the tickbase to gpGlobals' tick - 1** (180b78640 at
  180ed5758, 180ed5a5d after vfn 0xd0, 180ed5ca8); a pawn's spawn sets the tickbase to the tick (180d0e9a0 ->
  180d0eace).

**Corrected 2026-11-11 (the queue's session, section 5)**: the earlier reading "every command of a tick runs at tick
- 1" holds only for the **late** ones. The queue runs those through vfn 0xd0 (frametime 0, no tickbase step: tick -
1); then the **on-time** command runs through the movement services' vfn 0xc8 directly (180ed5cdf) with the frame's
frametime, so RunCommand steps the tickbase to **the server tick itself**, which the entities' thinks and the lag
compensation's record share. **Lined up 2026-11-11 (the "usercmd left" session)**: the port ran its on-time command
at the round world's tick before the step (T) and recorded after it (T + 1), a tick behind CS2. Now game.js runs the
on-time command at the frame's tick (`frameTick` = T + 1: gpGlobals' tick after AdvanceTick, the world's after the
step, the lag records' and the snapshot's), a late one at frameTick - 1, and UpdateAccuracyPenalty's per-tick pass at
frameTick too; the snapshot's `at` (the acked command's tick) moves with it, so the client's predicted tick does.

## 4. The seed's tick and the attack time

The spread's seed (1802a4e90, called by BaseGunFire at 1809f8fb4 with GetWeaponAttackTime's tick) is SHA-1 of the
angles and **the attack time's tick**, unless 0x181daae64 differs from 0x181daae60 (the command's random_seed, set by
vfn 0x150 180c7f1e0 / reset to -1 by 180c70120): 180c7f1e0 puts a fresh random there only with
**sv_usercmd_custom_random_seed** (default 0: the ConVar's default byte is +0x37 of its setup, checked on
sv_autobunnyhopping 0 / sv_subtick_movement_view_angles 1). Recoil's own seed is still the command's random_seed
(aim-punch.md 1). The attack time: fire-gate.md 3 (GetWeaponAttackTime), with its clamp and the calculated time.

The port: fire_gate.rs `attack_time` (job words 24 / 25 the entries' fractions, 26 +0x10c0, 27-28 the time out); the
seed and the kick take it (combat.js fireGun). The client predicts its command's tick from the snapshot's `at` (the
tick the server ran the acked command at) + one a command, as CS2's client predicts its tickbase.

The shoot position and the rewind's target from the entry: section 8. The history reduction's rule
(180d04300 with more than 4 entries): section 12. CPlayerCommandQueue: section 5.

## 5. CPlayerCommandQueue (traced 2026-11-11, Ghidra ReVa + tools/re; server/cs2web/core/cmd-queue.js)

The queue object (0x270 bytes, built by 180ec0430 from the controller's connect 180b74930, kept at controller
+0x6e0; vtable 1819d04a0). Its commands wait on the **controller's CUtlLinkedList at +0x4c0** (0xa0-byte elements,
prev / next +0x98 / +0x9c, head +0x4d0, tail +0x4d4, count +0x4dc). Fields: +8 the controller; +0x15c the substitutes
in a row; +0x160 trimmed total; +0x164 substitutes total; +0x168 the highest trimmed number; +0x16c "extended
starvation"; **+0x170 the warm-up count** (0x7fffffff when built: no warm-up); **+0x174 a host catch-up request**
(set only for a fake client, controller +0x388 bit 8, or 180b5cf10's: never a remote player); +0x178 the bloat
streak; **+0x198 a history of up to 60 numbers** (0x138-byte entries: [0] the number, +8 a real command, +0xa0 a
substitute's copy, +0xa8 its number); +0x268 the cq_logging stats (180ee1010).

**Receive, 180b68540** (the controller's, per client message, with the engine's arrival margin): the last run number
= vfn 4 (180ed2700: max(controller +0x5c0, +0x168)); each command: the highest received (+0x650) and an arrival
status ring (+0x654, 16 entries: 0x10000 / 0x10040 / 0x10080 / 0x10081, the margin encoded by 180b4e850 for the
last of a message) the client is told; a number above the last run goes in by **180b69000**: from the head, before the
first with a higher number, **an equal number dropped**, else at the tail. Not above: vfn 5 (**180ed9220**): if the
history has an entry with that number holding a substitute but no real command yet, the real one goes into it ("LATE"
in the log). Then the queue's vfn 7 (180ed7480: logs "got %d new commands", its latency bucket 180ed48d0).

**Each server tick, vfn 2 180ed4ea0** (a fake client's queue does nothing: controller +0x388 bit 8; the client's
history of real commands first, see run):
1. cq_fake_starve (0) discards that many.
2. **Empty: a substitute** (180ed4be0, "OnSimulateUserCommands(), generating substitute command %d from %d"), from the
   last command run (controller +0x5b8): starve counts + 1; **number = the last's + 1, the same once the count
   reaches cq_max_starved_substitute_commands (4)**; "extended starvation" when that number is at least 64 past the
   highest received (with the default cap, never). 180b511d0 builds it: mode 0 a copy with the subtick moves and the
   input history cleared, base +0x68 cleared, cmd flags (base +0x80) 0x50 cleared and 0x80 set, the tick count + 1,
   random_seed = MD5_PseudoRandom(number) & 0x7fffffff; mode 1 (extended) a new command with only the last view
   angles. It goes in through 180b69000 (no "newer" test: a repeated number runs again) and into the history
   (entry +0xa0). The bloat streak goes to 0.
3. **Not empty**: a starve count above 1 logs "OnBuffer", then the starve count and the extended flag go to 0. On a
   frame's first tick (gpGlobals +0x14 == 0; +0x18 the frame's ticks, 1 here): **cap = max(sv_cq_min_queue + 1,
   (int)(clamp(cq_buffer_bloat_msecs_max, 0, 1000) / 1000 x 64 + 0.5))** = 10 (32 with a catch-up request); excess
   = count - cap + ticks; the streak + 1 while it is above 0, else 0; the warm-up: below 4, + 1 and a warm-up tick.
   With a catch-up request, a streak above 2 and excess and ticks above 2: run excess / 4 + 2 this tick. **A warm-up
   tick or a streak above 2 x ticks trims**: keep = max(cl_cq_min_queue (controller +0x6e8: the client's userinfo,
   clamped 0..2, 180b64d60), sv_cq_min_queue) + sv_cq_trim_catchup_remainder (a warm-up) or
   sv_cq_trim_bloat_remainder, a bloat's at least cap - sv_cq_trim_bloat_space, never above the cap ("CQ limit");
   target = (ticks - 1) + run + keep (a catch-up's: no trim within 1..99 of it, run += min(that, 20)); **while the count
   is above it the head goes to the history as a real command** (+0x168 its number). Trimmed with one tick a frame and
   the warm-up below 4: the warm-up goes to 4. Logged "CQ %s: removed %d" ("bloat" / "catchup").
4. The warm-up at 4..0x7ffffffe goes to 0x7fffffff and 180b4ad90 notes the head's number ("catchup").
5. **Run**, `run` times while there are commands: pop the head; **the history's real commands not yet run go first,
   through RunCommands (vfn 0xd0, 180c7cdb0) at the tickbase tick - 1 with frametime 0**, that drops those more than
   sv_late_commands_allowed (5; negative: from the round trip, 180c6c240) before this one through vfn 0xd8; then the
   tickbase to tick - 1 and **this one through the movement services' vfn 0xc8 (RunCommand: frametime 1/64, the
   tickbase stepped to the tick)**; 180edcb20, 180b75cf0. The history keeps the numbers within 60 of it.
6. The frame's last tick: 180ee1010 (the cq_logging stats).

**vfn 6 180ec7240**: the warm-up to 0. Called through 180b50b20 for every controller by CCSGameRules::RestartRound
(180953c00, before round_poststart).

Defaults (tools/re/game/cvardump.py: a bool / int's default is the setup's +0x37): cq_enable 1, cq_max_starved_substitute
_commands 4, sv_cq_trim_bloat_remainder 1, sv_cq_trim_bloat_space 0, sv_cq_trim_catchup_remainder 1, cq_fake_starve 0,
sv_late_commands_allowed 5, cq_dilation_percentage 5 (0.1..10); engine2 (2026-10-29): sv_cq_min_queue 0,
cq_buffer_bloat_msecs_max 150, cl_cq_min_queue 0.

The port (server/cs2web/core/cmd-queue.js, cmd-queue-test.mjs): all of the above for a remote player with one tick a frame;
a late command runs whole a tick before the on-time one: its movement at frametime 0, then its weapon / +use
actions; a substitute is move-state.js substituteCmd.

**A late command's movement (traced 2026-11-11, the late-move session)**: the command run 180c7b050 sets gpGlobals'
frametime to RunCommand's (0 in the late batch) and calls **180c60a80**(mv, cmd, tick, force): mv+0 bit 0 = (cmd +0x90,
the late link, non-null) || force, bit 1 = the late link, mv+0xd8 = tick, mv+0xd4 = tick - (bit 0 ^ 1): a late
command's span is **0 ticks** (an on-time one's [tick - 1, tick]). Then SetupMove (vfn 0x110), the subtick loop
**180c6f2a0**: per step, frametime = (mv+0xd8 - mv+0xd4) x 1/64 x (mv+0xe0 - mv+0xdc) = **0**, the step's time taken
as 0 when mv+0 bit 0 is set (else its own), the view angles from the step (sv_subtick_movement_view_angles), then
**vfn 0x118, PlayerMove (0xe0), vfn 0x138 for every step**, then its button change (180c80540); the step builder's
apex cut needs bit 0 clear. FinishMove (vfn 0x130) after. So a late command's movement runs: nothing moves, but the
angles, the button states and a jump's impulse do. Ported: move-state.js runLate (each step a zero-time piece, no
extra cuts, the movement's tick count not stepped: world/movement.js tick's `late`), server/cs2web/core/player.js move(…,
late), game.js; checked by late-move-test.mjs (no movement, no tick counted, finite state, a jump's 298.9 impulse,
through the queue: 3 substitutes then the real ones late).
**On (CQ_ENABLE true) since the pacing session**, with the client's pacing (section 6). Unread: vfn 0xd8 (the dropped
late ones), the catch-up path's exact counts, 180b4ad90.

**The arrival status and the report** (traced 2026-11-11, the pacing session): 180b4e850 encodes a margin as
floorf(clamp(m, -15.99998, 15.99998) x 4096 + 0.5) (0x417fff00 the clamp); a status above 0xffff is a flag:
0x10000 received (no margin yet), 0x10040 never received (a gap below a newer number), 0x10080 not the last command
of its message, 0x10081 a number below 1. The receive (180b68540, the message's arrival margin `param_5` from the
engine's message object +0x20, CSource2GameClients vfn 21 180def9d0) gives the last command of a message
encode(min(n - last run - 1, queue count) / 64 + param_5). **180b525e0** builds the snapshot's report
(CSVCMsg_PacketEntities: last_cmd_number_executed = controller +0x5c0, last_cmd_number_recv_delta from +0x650,
cmd_recv_status): the last run, the highest received, the last message's margin (+0x6dc), then at most 8 status words
walking down from the highest received - 1 over 16 numbers: a run of 0x10000..0x1003f statuses packed as 0xffff +
its length, any other as it is, stopping at 0x10081; the queue's vfn 3 (180ec8590) adds cq_starved_command_ticks and
cq_discarded_command_ticks. The port sends it as the snapshot's `cq` (server/cs2web/core/cmd-queue.js report). The
arrival margin itself (the message's +0x20) is networksystem's: section 7. The server's ticks run on their own times
(a timer to each due time, game.js start) as the engine's do; the old 5 ms poll ran them in bursts.

## 6. The client's pacing (engine2 2026-10-15, traced 2026-11-11; src/cs2web/net/cmd-pacing.js)

engine2 keeps the client's commands arriving cl_tickpacket_recvmargin_desired ahead of when the server's queue
needs them ("Recvmargin-based usercommand pacing"). Read in engine2_20261015 (the Ghidra project's; no 2026-11-05
build is available):
- **The command clock** (cl_async_usercmd_send 1, the default): a scheduled function (1800651d0) builds the command
  due (180063f30: **+0xb0 += +0xac**, the time of the command), sends it, then **180062820**: +0xac = 1/64 /
  host_timescale + 1800628a0(the next number, +0xb0 + that interval, interval). The port: client/core/game.js commands()
  on a timer at the next command's time, the frame loop catching up.
- **The send history** (+0x2c35a8, 256 entries of 0x38 bytes by number & 0xff, 180063f30 / 1800652e0): +0 number,
  +0x8 the build time, +0x10 Plat_FloatTime at the build, **+0x18 the packet's send time**, +0x20 a float from the
  send (+0x2ccfe0; at least 0 to count: TODO(trace), the port's 0), +0x28 **the largest margin reported** (FLT_MAX
  until one), +0x30 a late flag.
- **180062230**, a snapshot's report: "first" for the highest received: (highest - last run) x interval + the
  message margin (when that is at least 0); then down from highest - 1, each status word: a margin (v / 4096,
  "history"), a run (0xffff + k: k numbers skipped), 0x10081 ("CQ: Server set re-sync at cmd %d": +0x2c3580 = that
  number + 1, older samples ignored), 0x10040 / 0x10080 ("backfill": the next number's margin - 1 tick when it is above
  -3 ticks), else "unknown". **180061e90** records one: kept when larger than the one before, a negative one marks it
  late.
- **1800626c0**, the desired margin: cl_tickpacket_recvmargin_desired x 0.001 + max(sv_cq_min_queue,
  cl_tickpacket_desired_queuelength) / 64 (+ cl_debug_build_recvmargin_min with engine_frametime_warnings_enable off,
  + cl_async_usercmd_send_recvmargin_min with cl_async_usercmd_send off); 5 ms at the defaults. The send (1800642d0)
  also sets the userinfo cl_cq_min_queue to (int)(that x 64) ("Used by the client to inform the server of their
  desired queue length"): 0.
- **1800628a0**, the step: the samples of the last (int)(cl_tickpacket_recvmargin_window x 64 + 0.5) numbers (at most
  256, none at or before the re-sync), each projected: ((next - n) x (1/64 / timescale) + its send time - the next
  command's time) + its margin; with at least max(1, minsamples) of them, excess = the smallest - desired, a negative
  one no lower than -max(0, (cq_buffer_bloat_msecs_max x 0.001 + 0.99 / 64 - 0.005) - the largest) (1800736d0 max);
  then (1 - V_expf(-(1 / clamp(timeconstant, 0.01, 10)) x clamp(interval, 0.001, 1))) x excess, clamped
  (1800736e0) to +-clamp(adjust_limit, 0, 90) % of the interval. A proportional step: a steady clock drift leaves a
  steady error (a 1 % slow clock settles 4 ms under the target).
- Defaults (engine2 2026-10-15, cvarreg via ReVa): cl_tickpacket_recvmargin_desired 5 ms, cl_tickpacket_desired_
  queuelength 0 (0..5), cl_tickpacket_recvmargin_window 4 s, _minsamples 10, _timeconstant 0.4 s, _adjust_limit 5 %,
  cl_async_usercmd_send 1, engine_frametime_warnings_enable 1, cl_async_usercmd_send_recvmargin_min 1,
  cl_debug_build_recvmargin_min 2, cl_usercmd_max_per_movemsg 4, host_timescale 1, sv_cq_min_queue 0,
  cq_buffer_bloat_msecs_max 150, cl_cq_min_queue 0.

Checked: web/src/cs2web/net/cmd-pacing-test.mjs (the pacing against the queue, closed loop: 0 / +-0.05 % clock skew and
4 ms jitter, no starvation once settled, an early client slowed back); in the browser (a dev server, the frame loop
driven at 60 fps): 64.03 commands a second, the interval at 15.625 ms, 2 late commands in 30 s, prediction
corrections median 0 / max 0.23 u while walking, the replica drift 0. Not ported: the clock sync's
cl_clock_recvmargin_* (the interpolation's own pacing), the EMAs at +0x2caf2c / +0x2caf34 (logging only).

**Not ported on purpose: the move packet's resends.** CS2 sends the last commands again in every move packet
(1800642d0: from latest - min(the unacknowledged count, cl_usercmd_max_per_movemsg 4) + 1 to latest) because its
netchannel is UDP: a lost packet's commands still arrive in the next one, and the server drops the repeats (180b69000:
an equal number). The port's socket is a WebSocket (TCP): nothing is lost, and a resend inside the same ordered
stream can't arrive before the original it repeats, so it would only add bytes. What TCP does instead is hold later
commands behind a lost segment (head-of-line delay): they arrive late rather than missing, and the queue handles that
as CS2 does a late command (a substitute, then the real one at frametime 0). Revisit only if the transport becomes
unreliable (WebRTC data channels / WebTransport datagrams).

## 7. The message's arrival margin (traced 2026-11-11, the "usercmd left" session; server/cs2web/core/cmd-queue.js recvMargin)

Read with Ghidra ReVa (server_20261105, engine2_20261015) and tools/re (capstone) on networksystem_20261015.dll
(source2-compiler tools/re/binaries; not in the Ghidra project).

- **Server side, CSource2GameClients vfn 21 180def9d0** (server): param_3 is the CNetMessagePB<CCLCMsg_Move>; its
  protobuf is at +0x30 (data +0x48, last_command_number +0x50: CCLCMsg_Move has only fields 3 data and 4
  last_command_number, tools/re/game/protomsg.py on engine2_20261029), so **+0x20 is the net-message wrapper's**, not a
  proto field. Called from engine2's **ProcessMove 1800bc480** (CServerSideClient, serversideclient.cpp:112; more
  than one Move message in a packet disconnects: "Too many move messages", the counter +0xee8 reset per packet by
  1800c0c00).
- **networksystem 1800c2230**, the netchannel's packet processing (called only from 1800f7e00 = **CNetworkSystem vfn
  20 (0xa0), the poll**, vtable 0x18023a788): margin xmm8 = -1; with the packet's receive time (+0x60, int64 µs,
  the socket's clock) and the caller's poll time (r8) both non-zero, d = poll - receive; when d + 5000 is at most
  105000 unsigned (d in [-5000, 100000] µs) **margin = (float)(max(d, 1) x 1e-6)** (double multiply, constant
  0x3eb0c6f7a0b5ed8d, then cvtpd2ps). Also xmm10 = (receive - [0x1802a3998]) / 1e6, the receive time as the
  engine's Plat_FloatTime seconds ([0x1802a3998] = the socket clock - Plat_FloatTime x 1e6, set in 1800f7e00). The
  dispatcher **1800c00b0** stores the margin at **message +0x20** (1800c03be), the receive seconds at +8, the
  channel's +0x8dac at +0x1c. The same margin x 1000 is the TraceLogging event NetChanRecv's RecvMarginMS (MsgTick =
  the packet's +0x74).
- **The poll's time**: 1800f7e00 reads the socket clock once ([0x1802a59f0] vfn 0x60, µs) before walking the
  received packets (r13), and every packet of the poll is measured against it.
- **When the poll runs: engine2 18022b960**, the server's per-tick job, straight-line: EventServerAdvanceTick
  (18022e840) -> **EventServerPollNetworking** (18022ea00) -> EventServerProcessNetworking (18022ebc0) ->
  EventServerBeginSimulate (18022ed80). So the margin is how long the packet waited for the tick that takes it.
  (Event registrations: CLoopTypeClientServerService 180223c30, CNetworkServerService 1801dfd30.)

The port: net.js stamps each 'cmd' message's receive time (cmd-queue.js usecNow, integer µs of performance.now)
before parsing and holds it (player.js inbox); game.js pollNetworking at the tick's start (after the clock steps,
before the commands) reads the clock once and hands each message to the queue with recvMargin(poll, receive).
Checked: cmd-queue-test 8-9 (the window's edges, 1 µs floor, -1 without a time; held until the poll), the pacing test,
and in the browser: 256 reported margins median 15.6 ms, 0 late, the interval settled at 15.67 ms, drift 0.

## 8. The shot's time and place: GetWeaponAttackTime's other outputs and the rewind's target (2026-11-11)

- **GetWeaponAttackTime 180a02c60(weapon, out, attack 0 / 1)** fills an attack info: +0 the attack time (section 4),
  **+0xc the entry's render_tick_count / render_tick_fraction (entry +0x60 / +0x64)**, +0x14 the shoot position,
  +0x20 the entry's view angles (+0x18's), +0x38 / +0x39 flags, +0x3c the source (0 an entry, 2 the history). With an
  entry it also reads the entry's player interp (+0x38, 180a1e3d0: src, dst, frac; kept when 0 <= src <= dst and frac
  in [0, 1]) and +0x40 (three floats) for 180a02700. **Without one** (held fire, a bot) it walks the weapon services'
  input history (svc +0x370, 32 records of 0x78: +0x68 / +0x6c render tick, +0x70 / +0x74 player tick, +0x18.. a
  position, +0x48 a vector) for the two records around the calculated attack time and lerps the render tick
  (1813b9690) and the angles. **Not ported**: that history (its writer unread) and the lerp: the port's command
  carries its own render tick instead (TODO(trace)).
- **The shoot position, 180a02700(out, player, attack time, entry +0x40, player interp)**: the shoot time = the
  attack time less 1813b9870(180b52570 x 64): **180b52570** = 1/64 x (1 + engine vfn 0xc0 / 100) when engine vfn 0xb8
  and the controller isn't a bot (+0x388 bit 8), else 1/64; the default server: one tick. Then
  **GetInterpolatedShootPosition 180b07db0(svc, out, time)**: **180b08260** walks CCSPlayer_WeaponServices' shoot
  position history (a CFixedSizeCircularBuffer<ShootPositionHistoryEntry_t, 32, int> at svc +0xe0, its records at
  +0xe8, 0x14 bytes: tick, fraction, x, y, z; head +0x368, count +0x36c) from the oldest over consecutive pairs: a
  first record later than the time fails, the first second record at or past it gives f = ticks(t - a) / ticks(b -
  a) (1813b8fb0, float) and the eye (1 - f) a + f b per component; not found: logged ("weapon services didn't find a
  shoot position history entry") and vfn 0xc8, the eye now. The entry's own shoot_position is only compared (more than
  1 u off: "Using server position").
- **The history's writer, 180b21ba0(svc)**: the time = (gpGlobals' tick (180927c50 via 180cacba0), gpGlobals +0x50
  the fraction), the eye = vfn 0xc8; the newest record replaced when its time is equal, else pushed (the oldest
  overwritten at 32). Called only from **180ae9260** (the view offset's update, after it sets the eye height), from
  **CCSPlayer_MovementServices vfn 0x138, 180ac4c00** (sets the origin from mv +0xc8 and the velocity, then
  180ae9260 with gpGlobals' frametime): the per-step call after PlayerMove in the subtick loop (section 5's late-move
  note). So every movement step records the eye at its time.
- **The rewind's target: CLagCompensationManager vfn 0x28, 180ecb710(out, player, time)** (vtable 0x1819cf820, vfn
  0x10 = StartLagCompensation's wrapper 180ee08d0, which keeps it at its job object's +0x34 (vtable 1819cf9b8: vfn
  0x10 returns it, 180ecb6d0); the taser's 180a2c980 passes the attack info's +0xc): lat = now less from_ticks(the
  latency / 1/64) (the engine's vfn 0x148(slot) = the player's net channel, its **vfn 0x50 = networksystem 1800c5c10:
  max(1e-6, the connection's ping (+0x8f04, SteamNetworking's real-time status m_nPing, ms) / 1000)**, refreshed
  from vfn 0x80 when stale); the candidate = the time, or with none (ticks + fraction <= 0) the current command's base
  +0x54 tick count at fraction 0; **kept when (int)(|seconds(candidate) - seconds(lat)| x 1000) < 201** (180c629e0),
  else lat; then 180ec2130 (clamp to [now - sv_maxunlag x 64, now]). StartLagCompensation 180edebe0 then reads the
  command's lag-comp history index (CUserCmd +0x78, -1 "had no attack history information, using target time"; its
  writer unread), the entry's has-bit 1 and its two interpolation infos (+0x28 / +0x30, 180ebc9c0 from their +0x1c /
  +0x20), validated (180ed23a0), lerped (1813b93b0), and the rest of lagcomp.rs `start`.

The port: sim/src/combat/lagcomp.rs `target_time` (job words 11 latency, 12 the command's tick: abi.rs ze_lag_poses);
server/cs2web/combat/combat.js posesAt passes the press entry's render tick (cmd[7]) and the client's measured ping; the client
(client/core/tick-input.js setFrameRecord, client/core/game.js localTick) takes cmd[7] / cmd[10] from the attack press's frame
(the replica's lagInfo when the down event came in), else from the command's own build. server/cs2web/core/shoot-history.js
(the ring, the lookup, the shoot time), player.js move (each step's eye at (tick - 1, its end), the last at (tick, 0);
a late command's once at its tick), move-state.js runCmd's `p.onStep`, combat.js fireGun's eye. Checked: cargo test
lagcomp (target_time_window), shoot-history-test.mjs, the combat suites; in the browser a press command's cmd[7] /
cmd[10] are the press frame's (3018.53, pair 3014 -> 3016 at 0.765) while the next command's own is 3021.14.
TODO(trace): the subtick loop's gpGlobals tick / +0x50 stores during a step (180c6f2a0), taken as the step's time in
the command's span [tick - 1, tick]; CUserCmd +0x78's writer (the port takes attack 1's entry, else attack 2's).

## 9. Bots' commands (2026-11-11)

**CBot vfn 0xb0, 1802ed0b0** (vtable 0x1817b00b0): flags into +0xd0's buttons (+0xc1 / +0xc0), all zero for a frozen
pawn (+0x414 bit 8); vfn 0xb8 builds the command at +0x28 with the pawn's eye angles (vfn 0x5f0), the moves (+0xc4,
+0xc8, +0xcc) and buttons (+0xd0); vfn 0xc0 (1802bc530: nothing); then **the controller's receive
180b68540 with that one command and margin -1.0**, like a client's (its queue then does nothing: a fake client,
section 5). **CBot vfn 0xb8, 1802be4f0**: 180cb7060 clears the command (the CSGOUserCmdPB's Clear: input_history
empty, attack1 / attack2_start_history_index -1); the number (cmd +8) and the base's +0x54 tick count = gpGlobals'
tick; base +0x6c random_seed = RandomInt(0, 0x7fffffff) from the global uniform stream (PTR 181e328d8); forward
+0x58, side +0x5c, up +0x60 (has-bits 0x40 / 0x80 / 0x100, cleared when 0); the buttons (+0x58, 18068b000); impulse
+0x64; the view angles (+0x40's x / y / z, has-bits 1 / 2 / 4). **No input history**, so a bot's shot always takes
GetWeaponAttackTime's no-entry path with an empty weapon services' history: the calculated time, or now + 1 tick when
that is before now (section 10). The port: combat.js act (no cmd[11]: no press, pressed or held), bots.js (the
number and cmd[7] = the frame's tick). TODO(trace): the random seed (tier0's stream isn't on this server: the recoil
seed takes the number); bot_crouch (1821755f0's value) is read in the duck code 180ac1ec0 (a bot ducks), not here.

## 10. Held fire, the step's time and which entry the rewind takes (2026-11-11, the "held-fire-steps" session)

Ghidra ReVa (server_20261105, started headless and stopped after) and tools/re (capstone).

**The weapon services' input history** (what GetWeaponAttackTime walks without an entry, section 8):
- A **CFixedSizeCircularBuffer<CSGOInputHistoryEntryPB, 32, int>** (RTTI 0x181f164e0) at CCSPlayer_WeaponServices
  **+0x370** (its allocator vtable; vfn 0 constructs, vfn 1 destroys a slot), records of **0x78 bytes from +0x378**
  (each a whole CSGOInputHistoryEntryPB copied by 1809a0f40: +0x18 view angles, +0x40 shoot position, +0x60 / +0x64
  render tick / fraction, +0x68 / +0x6c player tick / fraction), **head +0x1278, count +0x127c** (relative to +0x370:
  +0xf08 / +0xf0c). No other writer of either: never cleared after the services are built.
- **Its writer: 180b1d430 = CCSPlayer_WeaponServices vfn 0x60** (vtable 0x181928778 slot 12). The pawn's controller
  (pawn +0xc98 handle) +0x708, the current command; newest = the ring's newest record's player tick, or (0, 0) when
  empty; for each history entry of the command in order (count +0x30, the list +0x38): when newest is before the
  entry's player tick (ints, then the fractions; NaN not before), the entry is copied in at (head + count) % 32, or
  at 32 over the head (destroy, construct, copy, head + 1), and newest = the entry's tick. Entries at or before the
  newest are skipped.
- **Called from CBasePlayerPawn::PreThink 180d079f0** (vtable 0x181963748 slot 0xb10; "CBasePlayerPawn::PreThink"
  vprof string 0x181965cf8): the pawn's component list, head **pawn +0xb58**, next **+0x40**, each one's vfn 0x60
  (CCSPlayer_MovementServices' is 180c7c040, its +0x25c update). CCSPlayerPawn's PreThink **180236f50** (slot 0xb10)
  runs it through 1802371c0 only while **pawn +0xff0 == 0** (unnamed). The command run 180c7b050 calls the pawn's
  vfn 0xb10 at 180c7b203, before 180c60a80 / SetupMove / the subtick loop: every command, late or on time.
  CBasePlayerPawn::PostThink is 180d075d0 (slot 0xb18, "CBasePlayerPawn::PostThink" 0x181965d28).

**GetWeaponAttackTime 180a02c60 without the attack's entry**, after section 8's entry path (attack info +0x38 = 1
there, +0x3c = 0): A = the clock + 1 tick + +0x10c0 (the "calculated" time, stored at +0 first). The walk
(180a032cc..180a037d4, xmm11 = 0 throughout): from the newest record (i = count - 1) down: a record whose player tick
is after A is skipped; else d = A - its tick (1813b8fb0) and d after (4, 0) **ends the walk with nothing**; else when
it is the newest: +0xc = its render tick, the shoot position 180a02700(A, none), +0x3c = 2; else with the next record
(i + 1): f = ((float)(A - T_i).tick + ratio) / ((float)(T_{i+1} - T_i).tick + ratio) (divss), **+0xc =
1813b9690(R_i, R_{i+1}, f)**, the shoot position under cvar DAT_18212b230 from the records' +0x40 lerped (else the
shoot history), the angles slerped between the records' quaternions (181473e90, the dpps / polynomial slerp), +0x3c
= 1. Either way the attack time stays A and +0x38 stays 0. **Nothing found** (180a037d9): now + 1 tick
(180cacba0, 1813b9aa0) against A + (1, 0) (1813b9090): **now + 1 later → +0 = now + 1 tick, +0x38 = 1** (logged
"Firing first shot, sv tick ..., but no attack information present in command" for a non-bot, vfn 0xc20); else +0 =
A. Then +0xc = the attack time, the shoot position the pawn's (180b54f80), the angles the eye angles (vfn 0x5f0),
+0x3c = 5; with history entries in the command, the first entry's angles (+0x3c = 3), slerped from pawn +0xbd4 (the
last command's eye angles, copied at 180c7b537) when its render time is after the attack time (+0x3c = 4).
**1809f9910's "clocks no earlier than now" (1809f99b3) tests +0x38**: an entry or the now + 1 fallback.

**1813b9690(out, a, b, f)**: d = b - a (1813b8fb0's borrow, V_modff fold); out = (a.tick, ((float)d.tick + d.ratio)
x f), folded into [0, 1) (V_modff, a negative fraction borrowing, 1813b9170 if still out). **a's fraction is not
added** (read only for d).

**Which entry the rewind takes: CUserCmd +0x78**, written by **FX_FireBullets 1802a4f50 at 1802a545c**: the
controller's current command's attack2_start_history_index (+0x50) when the attack argument ([rbp + 0x340]) is 1,
else attack1's (+0x4c); also the debug ShootVerify block of the weapon services' post-frame (180b07191: an entry
index, lag compensation started and finished, then -1 at 180b071bd). StartLagCompensation's -1 is "Lag comp cmd had no
attack history information, using target time": a held shot has no pair. FX_FireBullets gets the attack info's +0xc
as the lag compensation's time (BaseGunFire 1809f8a70 passes `&info + 0xc`).

**The step's time** (180c6f2a0, the subtick loop): for each step whose `when` differs from the last (the first
compared against 0): gpGlobals' tick (+0x44) = mv+0xd4, fraction (+0x50) = `when`, or 0 with mv+0 bit 0 (a late
command); a fraction at 1 or more → tick + 1, fraction - 1; below 0 → tick - 1, fraction + 1; curtime = tick / 64 +
fraction / 64; frametime = (mv+0xe0 - mv+0xdc) x (mv+0xd8 - mv+0xd4) / 64; the thread id at +0x58; vfn 0x118, 0xe0,
0x138, then all five restored. 180b21ba0 reads the tick through 180c86d00 (the pawn identity's +0x38, its time
domain) -> 180927c50 (gpGlobals +0x44 directly for a non-zero domain; else with the CCSGameRules pointer 0x1821ba1c0
set, 180de8680: its vfn 0x370 with gpGlobals +0x48; no gamerules: +0x44) and back through 1809249b0 (180de82d0): the port takes gpGlobals' tick.

The port: server/cs2web/core/input-history.js (the ring, push), combat.js act (pushes the command's entries, cmd[13], before
the gate; a live pawn), client/core/game.js (each frame's render tick, `frameHist`; cmd[13] = the frames in the command's
span and the presses at their event times, [fraction, render]), move-state.js cleanCmd (up to 16), fire_gate.rs
`attack_time` (the walk, the fallback, `lerp_tick`; AttackInfo), fire_abi.rs (words 29-31 out, 32.. the ring in),
combat.js posesAt (a held shot's render tick, no pair; the interp kept), player.js recordStep (the step's time).
Checked: cargo test fire_gate (no_history_falls_back_to_now, held_render_tick_from_the_history), fire-gate-test 7-8.
Left (section 11 took the angles, the knife and the press frame): CS2's history reduction past 4 entries (client
cvar 1825809e8); pawn +0xff0's name.

## 11. The shot's angles, the knife's rewind, the press's frame (2026-11-11, the "shot-angles" session)

Ghidra ReVa (server_20261105, headless, stopped after) and tools/re.

**The angles (attack info +0x20)**, what BaseGunFire hands FX_FireBullets (the bullets' direction) and the spread
seed (1802a4e90 hashes them), and the knife its swing (180a2fa80: 181470980 AngleVectors of info +0x20):
- source 0 (the entry): the entry's view_angles (+0x18's CMsgQAngle, 1809f8a50);
- source 2 (the newest record): its +0x20 (the record's view angles: 180545f20 from +0x18 / +0x1c / +0x20, at
  180a037a6);
- source 1 (between records i and i + 1): **181473e90 (AngleQuaternion) of each, CS2's fitted slerp by the same f as
  the render tick, QuaternionAngles (181475b60)** (180a0360e..180a03734): a = record i (x w0), b = record i + 1 (x w1);
  the instruction order is UpdateOrientationBlend's (trains.md) to the last op: one function now, sim/src/math/slerp.rs;
- source 5: the pawn's eye angles (vfn 0x5f0, m_angEyeAngles);
- source 3: the command's first entry's angles; source 4 (180a03b6a..180a03d74): when that entry's render tick is
  after the attack time and its fraction > 0, and (its tick, 0) isn't after the attack time: slerp(a = pawn +0xbd4, b
  = the entry's, f = (attack - (tick, 0)) / (render - (tick, 0))). **pawn +0xbd4** is copied from m_angEyeAngles
  +0xbc8 at 180c7b537, after PostThink (vfn 0xb18) and before vfn 0xb20 (ItemPostFrame): at the shot, the eye angles.
  The entry's angles are the client's view + the aim punch (aim-punch.md: FX_FireBullets adds nothing outside
  debug_aim_angle), so a source-5 shot has no punch: as CS2's (bots').

**1809f9910(weapon, info, delay, attack)**, the clock step BaseGunFire and the knife share: GetWeaponAttackTime, +0x10c0
= attack - (now + 1), with +0x38 both clocks (180b54e20 / 180b54e50) no earlier than now (1809f99b3..1809f9b27), then
SetNextPrimaryAttack(delay, 1) and SetNextSecondaryAttack(delay, 1) (180b763d0 / 180b76450 from the clocks
themselves). The knife: delay 1.0 (0x3f800000) for attack 1 (the stab), 0.4 (0x3ecccccd) else; weapon +0xfe8 = &info.

**The knife's rewind**: 180a2fa80 calls the lag compensation manager (PTR 181e448e0) vfn 0x10 with the pawn, 2, info
+0x14 (the shoot position: the eye), info +0x20 (the angles), the range + 128 (fVar21: 32 or 48, + 18) and **info +0xc
(the render tick) as the time**. It never writes CUserCmd +0x78: **every CUserCmd is built with +0x78 = -1** (the
parse scratch's at 180deff0a, the controller's embedded command +0x5b8 -> +0x630 at 180b3e7cc; the copy constructors
180b3efdf / 180ed568f carry it), FX_FireBullets (1802a545c) the only setter outside the ShootVerify debug block. So a
swing is "using target time": no pair. (A queue substitute copies its source's +0x78: after a gun shot, a knife swing
on a substitute would take the shot's index; the port has no per-command +0x78.)

**The press's frame (client)**: section 2's 180d07790 marks an attack pressed when a down event is read, and the entry
it takes is the frame being read (a new frame's entry, or the one already in the command), its view record's ticks,
render tick and angles: the frame that processed the event, not the event's time. 180d04300 runs 180d07790 first at
the command's build: an event the frames haven't read is read there on the last frame's record (a new entry for it
when that frame isn't in the command: its player tick then the previous one).

The port: sim/src/math/slerp.rs (trains.rs calls it), fire_gate.rs attack_time(s, c, attack) (AttackInfo.angles; the
entries by index, `first`, `eye`), fire_abi.rs (376 words: 7-word records and entries, 370-372 the eye, 373-375 the
angles out, op 5 the knife's GetWeaponAttackTime), src/cs2web/sim/fire-gate.js (attackTime), loadout.js (knifeInfo; the
shot's info), combat.js (fireGun's angles, the knife's eye / aim / rewind, posesAt's pair only for a gun's entry),
src/cs2web/client/core/input-history.js (ClientHistory: frame / press / build), client/core/game.js (cmd[11] the indices, cmd[13]
[fraction, render, pitch, yaw, src, dst, frac], cmd[8] gone), tick-input.js (setPressHook), move-state.js cleanCmd,
server/cs2web/core/input-history.js (entriesOf, the ring's angles). Checked: cargo test fire_gate, input-history-test.mjs,
fire-gate-test, reload / zoom tests, train-test (the shared slerp), sim-test.
(Since section 12 an entry is [fraction, render, pitch, yaw] and a pressed one adds its interpolation infos.)

## 12. The client's history trim and the entry's interpolation infos (2026-11-11, the "knife-interp" session)

client_20261105.dll with tools/re (disasm; scratch helpers: a rip-operand reader and a cvar namer that pairs `lea rcx,
[object]` with the `lea rdx, [name]` before it), and Ghidra ReVa on client_20261015 (the project has no 1105 client)
for the decompiles; every 1015 function used was matched to its 1105 twin by instructions (addresses normalised).

**The trim, 180d04300 at 180d044bf..180d0478f** (1015: 180d02130), with more than 4 entries and
**cl_csgo_shoot_trim_input_frames** (value 1825809e8, object 1825809e0, registered 1800ec3d0: bool, default 1, flags 2):
- tags: attack 2's pressed entry's +0x58 = 1, then attack 1's = 0 (the entry constructor 180cdac50 sets +0x50.. +0x5c
  to -1: the frame number's slot, the command index +0x54, the tag +0x58, the bucket +0x5c);
- span s = 180828580(newest +8 - oldest +8) (1815f27f0, the same instructions as server 1813b8fb0): **(float)tick +
  ratio** (ticks, not seconds); q = s x 0.25 (0x181b03ca0); step = 1815f2a70(q) (= server 1813b9230); end = oldest +
  step (1815f28d0 = server 1813b9090); h = q x 0.5 (0x181acb080);
- buckets k = 0, 1, ... while entries are left: mid = end - 1815f2a70(h); best = FLT_MAX (0x181acb0b8); walking on
  from the last entry taken: k < 3 and the entry not before end (its tick, then comiss on the ratios: 0xff and the
  unordered 0x80 are "before", 0 and 1 end the bucket) ends the bucket; else +0x5c = k; tag -1: |(float)d.tick +
  d.ratio| (andps 0x181acb100) of (entry - mid) below best (comiss, jae: strictly) takes it; a tag: **180cfc880 writes
  it at once** (bool 1: its interp infos; +0x54 = its index in the command) and the bucket is "written"; after the
  bucket, not written and a best: **180ce0280** (the 1015 180cde100: next CSGOInputHistoryEntryPB, 180cfc880, +0x54)
  with bool = !sv_csgo_shoot_verify_on_attack_only (0x1824cf638, default 1); end += step.
- else (4 or fewer, or the cvar off): every entry through 180ce0280 with bool = pressed || !sv_csgo_shoot_log_attack_cmds_only
  (0x1824cf5f8, default 1). So with CS2's defaults **only a pressed entry carries the interp infos**.
- 180d04300's other constants: param_4 = 1.0 (0x181acb084), param_5 = **cl_interp_ratio**'s value (0x182581638).

**The entry writer 180cfc880** (1015: 180cfa6b0; arguments: the history record, the entry message, the bool, 1.0,
cl_interp_ratio, the local pawn): render tick +0x60 / fraction +0x64 (has-bits 0x200 / 0x400); with
PTR 18223b370's +0xca the player tick / fraction (+0x68 / +0x6c, 0x800 / 0x1000); the view angles (+0x18, bit 1);
under sv_csgo_shoot_verify (0x1824cf608) the shoot position (+0x40, 0x20) and the target's head / abs origin / angles
(+0x48 / +0x50 / +0x58) with the target entity (+0x74, 0x4000); the frame number (+0x70, 0x2000). **The interp block**,
under **sv_csgo_shoot_use_full_interp** (0x1824cf648) and the bool: player_interp (+0x38, 0x10) from 1809eae60 (the
pawn's +0x330: its own interpolation at the player tick; written when its src is below the player tick, else logged
"Invalid player history"); then with param_4 and param_5 finite (exponent not 0xff):
- **cl_interp** (+0x20, bit 2): only its frac (+0x18), from **180af4df0(ring 0, render - 1815f2fc0(param_4 = 1.0))**;
- **sv_interp0** (+0x28, bit 4): 180af4df0(ring 1, (cl_interp's src, 0) - cl_interp_ratio ticks) -> src +0x1c, dst
  +0x20, frac +0x18;
- **sv_interp1** (+0x30, bit 8): the same at (cl_interp's dst, 0) - cl_interp_ratio.

1815f2fc0 (1015: 1815ee5c0) = a GameTick less 1815f2a70(x) (a float count of ticks). **180af4df0(out, ring, &t)**
(1015: 180af3510, the same instructions): ring 0 = 0x1822332d0, ring 1 = 0x182233280 (1015: 18222e250 / 18222e200),
each 16 int ticks at +8, head +0x48, count +0x4c; empty: (-1, -1, 0); from the newest (i = count - 1) down, the first
tick at or below t's **tick** (its ratio isn't compared): i the newest -> (it, it, 0); else (it, the next newer,
((float)(t.tick - it) + t.ratio) / (float)(next - it)) (cvtdq2ps, addss, divss); none -> (the oldest, the oldest, 0).
**The rings' writer: C_BaseEntity::LatchAndSaveLastSimulationValuesForInterpolationList** (1015 180b00730, the vprof
name; c_baseentity.cpp): list 1 (called from the frame stage switch 180b6d700 after the network update) pushes the
network interface's vfn 0xb8 -> vfn 0x40 tick (the update's server tick); list 0 (from 180a4f840 on a simulation
tick's last pass) the client's gpGlobals tick (+0x44); both rings full at 16 overwrite the oldest.

The server's use of the three: shots.md 5b. **The port** (web/src/cs2web/client/core/interp-info.js): ring 1 = the snapshots'
ticks as they arrive (replica.js `netTicks`, latched in `snapshot`); ring 0 = every tick (the client simulates each),
so cl_interp = (render's tick - 1, render's tick, render's fraction); cl_interp_ratio = the port's interp in whole ticks
(lagInfo: render = drawn + interp + 1), which puts sv_interp0 / sv_interp1 around the drawn time; the infos go on the
pressed entries only (client/core/input-history.js build: the entry's 7 more words), the fractions as their f32s. The trim:
sim/src/combat/trim_history.rs (ze_trim_history), src/cs2web/sim/trim-history.js, ClientHistory.build (on the fractions as
they go out; `trim` false is the cvar off). Checked: cargo test trim_history (4), lagcomp; input-history-test (the
trim, the infos for a 2-tick ring), fire-gate-test (cleanCmd's 4 / 11 words); the browser: a press entry
[0.03209, 1904.6559, 4.8543, -25.1043, 0.6559, 1902, 1904, 0.5, 1904, 1904, 0] hit a frozen bot. Not checked natively
(180d04300 needs a live CCSGOInput). Left: player_interp and the shoot position / target fields aren't sent (the
server reads them only under sv_csgo_shoot_verify).

**The interpolation amount and the drawn time (2026-11-11, the "tick64" session).** client_20261105 with tools/re,
client_20261015 in ReVa:
- **cl_interp_ratio** (value 0x182542348, registered 1800b66e0: a float, min 0 (18076bda0 with xmm1 0), max 19.0
  (0x181bd8ec0, 18076bd90), **default 2.0** (0x181acb088), flags 0x200; help "Set number of client simulation
  interpolation ticks."). **cl_interp** (0x182542378) is read-only ("Read the effective client simulation
  interpolation amount in terms of time"). cl_interpolate 1, cl_extrapolate 1, **cl_interp_hermite 1** (0x18255f2b8,
  flags 0x4000), cl_interp_threadmodeticks (int). sv_client_min / max_interp_ratio are server-side.
- Ring 0 is list 0's latch, the client's gpGlobals tick on each simulation tick (180a4f840): every tick, so the port's
  "every tick" is CS2's. With the entry writer's formula the others are drawn at the render tick - 1 - cl_interp_ratio
  = render - 3: the port's replica DELAY 3 (client/core/replica.js), the interp reported 2 ticks (config.js CL_INTERP_RATIO).
- **The per-frame setup 180affc10** (1015: 180afe330) copies cl_interp_hermite into a global (0x18225de40; 1015
  0x182258d90) and the interpolation amount (180160c50). **GetInterpolationInfo 180160d10 (1015)** for one
  interpolated var at time t (seconds; less the var's own offset (+0x18) unless asked not to): its sample ring
  (head / count / stride packed in +8: count bits 13..18, head 0..5, base 19..24); from the newest, the first sample
  pair whose older's tick x 1/64 is at or before t: info +0x00 the newer sample, +0x08 its tick, +0x10 the older,
  +0x18 its tick, +0x34 the fraction (t - older) / (newer - older) (ticks x 0.015625), +0x30 it clamped to [0, 2]
  (1801587c0); past the newer: +0x39 extrapolate, +0x30 = 1. With one more older sample (+0x20, its tick +0x28) whose
  tick is below the older's, **+0x38 = cl_interp_hermite**. None: the oldest twice.
- **The Vector instantiation 180164e20 (1015)**: no info -> vfn 0x98; hermite (+0x38): the third sample's tick moved
  to make the spacing even ((newer - older) > 0 and unequal to (older - third): third = older - (newer - older)), then
  **180159e00(out, -, +0x30, +0x20 sample, +0x10 sample, +0x00 sample)**, the spline: h00 = (2t^3 - 3t^2) + 1,
  h01 = 3t^2 - 2t^3, h10 = (t^3 - 2t^2) + t, h11 = t^3 - t^2; out = h00 a + h10 (b - a) + h01 c + h11 (c - b) with
  (a, b, c) its arguments (180159e2a..; the disassembly's operands: r9 = +0x20, the 5th = +0x10, the 6th = +0x00).
  Not hermite: 18016da70 (0 or 1 exactly: that sample; else 180159d40, a lerp of older -> newer).
  (The spline itself puts h00 on its first argument, the third sample, where Source 1's Hermite_Spline(p0, p1, p2)
  puts it on p1: it would start a sample behind. It is never reached, below.)

**The drawn interpolation, settled natively (2026-11-11, the "hermite" session; rubikon/tests/InterpOracle).** The
oracle maps client_20261015's image (no loader), points ThreadInMainThread (IAT 0x181aacb00) at a stub and V_sincosf /
V_atan2f (0x181aac630 / 0x181aac680) at tier0_20261015's, writes the slerp's zero-length constant 0x18236fa60 as the
identity (a static initialiser's), sets the hermite global, and builds a var by hand as the Vec3D copy of
GetInterpolationInfo **18088a9b0** reads it (var +0x10 flags: bit 0 linear only, 0x20 the second history; +0x20 the
history: +0 the block, +8 the packed word (bits 0..5 the newest's slot, 6..11 the stride, 13..18 the count, 19..24 the
capacity), +0x18 the time offset; the block's slots [i32 tick, i16 index], newest first; a Vec3D's values from
capacity x 8 at index x stride x 12).
- **The hermite never engages.** For every pair (samples 100..103, t = 100.5 / 101.5 / 102.5) the "third" sample the
  template fills (+0x20 / +0x28) is the older one itself, so `older's tick - third's tick > 0` fails and +0x38 stays
  0, with cl_interp_hermite on: an off-by-one in the index it takes (head + 1 + the loop counter, the older's slot).
  The same in the generic copy **180160d10** and the QAngle copy **1808cd6d0**. So cl_interp_hermite changes nothing
  and CS2 draws these vars linearly. Past the newest sample (t = 103.4): +0x39 extrapolate, +0x30 = 1.
- **The Vector blend** (18089c450 -> 1808a63e0 -> 18016da70 -> **180159d40**): f exactly 0 or 1 that sample; one sample
  for both that one; else per component ((newer - older) x f) + older (f32: subss, mulss, addss).
- **The QAngle var** (vtable 0x181c3a918, slot 0x80 180a663d0 -> **1808d84c0**, its info 1808cd6d0): the same cases
  (1808ec0a0), then 1808badd0: all three components equal the older's, else **181744420 = the server's 1814774c0**
  (AngleQuaternion 1817445e0, the fitted slerp, QuaternionAngles 1817463a0 -> MatrixAngles 1817439d0 with V_atan2f).
- The fraction: (t - older x 1/64) / (newer x 1/64 - older x 1/64) in f32, clamped to [0, 2] (1801587c0).
- **Checked**: `dotnet run -c Release -- <binaries> --cases <file>` writes 20,000 random pairs through client.dll's
  Vector and QAngle interpolates; `node web/server/cs2web/dev/interp-check.mjs <file>` runs them through the sim's
  `ze_interp_pose` (sim/src/game/interp.rs): **0 of 20,000 differ**, bit for bit.
- The port: replica.js sample -> client/core/interp-pose.js -> ze_interp_pose for the origin, the view offset's z and the
  angles (pitch, yaw, 0). Stand-ins kept: the 64 u teleport cut (CS2 resets a var's history on its own teleport
  flag, untraced), the duck state from the nearer sample (the stand-in pose), extrapolation (18089c450's branch needs
  the var's time offset above 1e-6 and a global: which vars have one isn't traced; a pose past the newest holds it).
  CInterpolatedVar<CTransform> (vtable 0x181c75170, an array of them is "m_iv_Transforms[ %d ]") blends the same
  way in both branches (181748920: position (b - a) f + a, the rotation the fitted slerp).
