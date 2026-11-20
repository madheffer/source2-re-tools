# Usercmd timing: input history, tickbase, command queue, pacing, interpolation

client_20261105 (client_20261015 in Ghidra for decompiles, matched to 1105 by instructions), server_20261105,
engine2_20261015 / 20261029, networksystem_20261015. cs_usercmd.proto (decoded from client.dll by tools/re/game/protodesc.py).

## Functions

| Address | Module | What |
|---|---|---|
| 1807b1e20 / 1807b1ed0 | client | CSGOUserCmdPB Clear / ByteSize (vtable 181bd1e30) |
| 180d07790 | client | CCSGOInput: per frame and at the start of the command's finish: button events -> history entries |
| 180b72060 | client | (input, slot) the button-event list |
| 180d0c170 | client | refreshes the weapon services' shoot position record (attack 1) |
| 180d04300 | client | CCSGOInput vfn 0xc8: the command's history out (1015: 180d02130) |
| 181a5b480 | client | moves the newest entry to the front |
| 180ce0280 | client | next CSGOInputHistoryEntryPB + 180cfc880 + +0x54 (1015: 180cde100) |
| 180cfc880 | client | entry writer (record, entry message, bool, 1.0, cl_interp_ratio, local pawn) (1015: 180cfa6b0) |
| 180cdac50 | client | entry constructor: +0x50..+0x5c = -1 |
| 180828580 -> 1815f27f0 | client | tick difference as (float)tick + ratio (= server 1813b8fb0) |
| 1815f2a70 | client | float ticks -> GameTick (= server 1813b9230) |
| 1815f28d0 | client | GameTick + GameTick (= server 1813b9090) |
| 1815f2fc0 | client | GameTick less 1815f2a70(x) (1015: 1815ee5c0) |
| 1809eae60 | client | player_interp from the pawn's +0x330 (its interpolation at the player tick) |
| 180af4df0 | client | (out, ring, &t): interp info from a tick ring (1015: 180af3510) |
| 180b00730 (1015) | client | C_BaseEntity::LatchAndSaveLastSimulationValuesForInterpolationList (c_baseentity.cpp) |
| 180b6d700 | client | frame stage switch (list 1 after the network update) |
| 180a4f840 | client | a simulation tick's last pass (list 0) |
| 1800ec3d0 | client | cl_csgo_shoot_trim_input_frames registration |
| 1800b66e0 | client | cl_interp_ratio registration |
| 18076bda0 / 18076bd90 | client | cvar min / max setters |
| 180affc10 | client | per-frame interp setup (1015: 180afe330): copies cl_interp_hermite to 0x18225de40 (1015 0x182258d90), the amount (180160c50) |
| 180160d10 (1015) | client | GetInterpolationInfo (generic) |
| 18088a9b0 | client | GetInterpolationInfo, Vec3D copy |
| 1808cd6d0 | client | GetInterpolationInfo, QAngle copy |
| 1801587c0 | client | clamp [0, 2] |
| 180164e20 (1015) | client | CInterpolatedVar<Vector> interpolate |
| 180159e00 | client | the hermite spline (out, -, t, a, b, c) |
| 18016da70 | client | not hermite: 0 or 1 exactly that sample, else 180159d40 |
| 180159d40 | client | lerp older -> newer per component |
| 18089c450 -> 1808a63e0 | client | Vector blend path |
| 180a663d0 -> 1808d84c0 | client | QAngle var slot 0x80 (vtable 0x181c3a918) |
| 1808ec0a0 / 1808badd0 | client | QAngle cases / blend |
| 181744420 | client | = server 1814774c0: AngleQuaternion 1817445e0, fitted slerp, QuaternionAngles 1817463a0 -> MatrixAngles 1817439d0 (V_atan2f) |
| 181748920 | client | CInterpolatedVar<CTransform> (vtable 0x181c75170, "m_iv_Transforms[ %d ]") blend: position (b - a) f + a, rotation the fitted slerp |
| 180c7cb80 | server | RunCommand (CPlayer_MovementServices vfn 0xc8) |
| 180ae1920 | server | CCSPlayer_MovementServices' RunCommand (after 180a9be50) |
| 180b78640 | server | SetTickBase |
| 180b70e10 / 180b70d20 | server | note the tick and command number |
| 180c7b050 | server | the command run (movement, ItemPostFrame) |
| 180c7cdb0 | server | RunCommands(cmds, n, last) (vfn 0xd0) |
| 180c6c240 | server | late command limit from the round trip |
| 180b750e0 / 180b75cd0 | server | current command set / after |
| 180b511d0 | server | builds a substitute / the last command's after-run |
| 180ed4be0 | server | CPlayerCommandQueue (vtable 1819d04a0) substitute generation |
| 180ed5758, 180ed5a5d, 180ed5ca8 | server | tickbase = tick - 1 (SetTickBase calls) |
| 180ed5cdf | server | the on-time command through the movement services' vfn 0xc8 |
| 180d0e9a0 -> 180d0eace | server | pawn spawn: tickbase = the tick |
| 1802a4e90 | server | spread seed (SHA-1), called at 1809f8fb4 |
| 180c7f1e0 / 180c70120 | server | vfn 0x150 random_seed / reset to -1 |
| 180ec0430 | server | builds the queue (from the controller's connect 180b74930) |
| 180b68540 | server | controller receive (per client message, with the arrival margin) |
| 180ed2700 | server | queue vfn 4: last run number = max(controller +0x5c0, +0x168) |
| 180b4e850 | server | encode a margin |
| 180b69000 | server | insert a command (an equal number dropped) |
| 180ed9220 | server | queue vfn 5: a late real command into its substitute's history entry ("LATE") |
| 180ed7480 | server | queue vfn 7: logs "got %d new commands" (latency bucket 180ed48d0) |
| 180ed4ea0 | server | queue vfn 2: each server tick |
| 180b64d60 | server | cl_cq_min_queue from userinfo (clamped 0..2) |
| 180b4ad90 | server | notes the head's number ("catchup") |
| 180edcb20, 180b75cf0 | server | after a run |
| 180ee1010 | server | cq_logging stats |
| 180ec7240 | server | queue vfn 6: warm-up to 0 (through 180b50b20 for every controller by CCSGameRules::RestartRound 180953c00, before round_poststart) |
| 180c60a80 | server | (mv, cmd, tick, force): move span setup |
| 180c6f2a0 | server | the subtick loop |
| 180c80540 | server | a step's button change |
| 180b525e0 | server | builds the snapshot's command report (CSVCMsg_PacketEntities) |
| 180ec8590 | server | queue vfn 3: adds cq_starved_command_ticks, cq_discarded_command_ticks |
| 180def9d0 | server | CSource2GameClients vfn 21: the Move message's margin (+0x20) |
| 180a02c60 | server | GetWeaponAttackTime(weapon, out, attack 0 / 1) |
| 180a1e3d0 | server | player interp (src, dst, frac) |
| 180a02700 | server | shoot position (out, player, attack time, entry +0x40, player interp) |
| 1813b9870 | server | seconds -> ticks |
| 180b52570 | server | 1/64 x (1 + engine vfn 0xc0 / 100) when engine vfn 0xb8 and not a bot, else 1/64 |
| 180b07db0 | server | GetInterpolatedShootPosition(svc, out, time) |
| 180b08260 | server | shoot position history walk |
| 180b21ba0 | server | shoot position history writer |
| 180ae9260 | server | the view offset's update |
| 180ac4c00 | server | CCSPlayer_MovementServices vfn 0x138 |
| 180ecb710 | server | CLagCompensationManager vfn 0x28 (out, player, time): rewind target (vtable 0x1819cf820) |
| 180ee08d0 | server | vfn 0x10 StartLagCompensation's wrapper (job object +0x34; vtable 1819cf9b8, vfn 0x10 180ecb6d0 returns it) |
| 180a2c980 | server | the taser: passes the attack info's +0xc |
| 180c629e0 | server | the window test |
| 180ec2130 | server | clamp to [now - sv_maxunlag x 64, now] |
| 180edebe0 | server | StartLagCompensation |
| 180ebc9c0 / 180ed23a0 / 1813b93b0 | server | interp infos / validate / lerp |
| 1802ed0b0 | server | CBot vfn 0xb0 (vtable 0x1817b00b0) |
| 1802be4f0 | server | CBot vfn 0xb8: builds the command |
| 1802bc530 | server | CBot vfn 0xc0 (nothing) |
| 180cb7060 | server | clears the command (CSGOUserCmdPB Clear) |
| 18068b000 | server | the buttons |
| 180ac1ec0 | server | duck code (reads bot_crouch 1821755f0) |
| 1809a0f40 | server | copies a CSGOInputHistoryEntryPB |
| 180b1d430 | server | CCSPlayer_WeaponServices vfn 0x60 (vtable 0x181928778 slot 12): input history writer |
| 180d079f0 | server | CBasePlayerPawn::PreThink (vtable 0x181963748 slot 0xb10; vprof 0x181965cf8) |
| 180c7c040 | server | CCSPlayer_MovementServices vfn 0x60 (+0x25c update) |
| 180236f50 / 1802371c0 | server | CCSPlayerPawn PreThink (slot 0xb10) / its call |
| 180d075d0 | server | CBasePlayerPawn::PostThink (slot 0xb18, "CBasePlayerPawn::PostThink" 0x181965d28) |
| 180a032cc..180a037d4 | server | GetWeaponAttackTime's history walk |
| 1813b9690 | server | (out, a, b, f) lerp a GameTick |
| 1813b9170 | server | fold if still out |
| 1802a4f50 | server | FX_FireBullets (writes CUserCmd +0x78 at 1802a545c) |
| 1809f8a70 | server | BaseGunFire |
| 180b54e20 / 180b54e50 | server | the primary / secondary clock |
| 180b763d0 / 180b76450 | server | SetNextPrimaryAttack / SetNextSecondaryAttack |
| 180cacba0 | server | now (gpGlobals tick via 180927c50, fraction +0x50) |
| 1813b9aa0 | server | GameTick + 1 tick |
| 181473e90 / 181475b60 | server | AngleQuaternion / QuaternionAngles |
| 180a037a6 | server | source 2's record view angles (180545f20 from +0x18 / +0x1c / +0x20) |
| 180b07191 / 180b071bd | server | ShootVerify debug block (an index, then -1) |
| 180c86d00 | server | the pawn identity's time domain (+0x38) |
| 180de8680 | server | gamerules vfn 0x370 with gpGlobals +0x48 |
| 1809249b0 (180de82d0) | server | back to a tick |
| 1809f8a50 | server | the entry's view_angles (CMsgQAngle) |
| 180545f20 | server | a record's view angles |
| 180a2fa80 | server | the knife's swing (181470980 AngleVectors of info +0x20) |
| 180deff0a / 180b3e7cc | server | CUserCmd built with +0x78 = -1 (parse scratch / controller's embedded command +0x5b8 -> +0x630) |
| 180b3efdf / 180ed568f | server | copy constructors (carry +0x78) |
| 1800651d0 | engine2 | scheduled command build / send |
| 180063f30 | engine2 | builds the command due (+0xb0 += +0xac) |
| 180062820 | engine2 | +0xac = 1/64 / host_timescale + 1800628a0(...) |
| 1800652e0 | engine2 | send history |
| 180062230 | engine2 | a snapshot's report |
| 180061e90 | engine2 | records one margin |
| 1800626c0 | engine2 | the desired margin |
| 1800642d0 | engine2 | the send (move packet; userinfo cl_cq_min_queue) |
| 1800628a0 | engine2 | the step |
| 1800736d0 / 1800736e0 | engine2 | max / clamp |
| 1800bc480 | engine2 | ProcessMove (CServerSideClient, serversideclient.cpp:112) |
| 1800c0c00 | engine2 | resets the Move counter (+0xee8) per packet |
| 18022b960 | engine2 | the server's per-tick job |
| 18022e840 / 18022ea00 / 18022ebc0 / 18022ed80 | engine2 | EventServerAdvanceTick / PollNetworking / ProcessNetworking / BeginSimulate |
| 180223c30 / 1801dfd30 | engine2 | CLoopTypeClientServerService / CNetworkServerService registrations |
| 1800c2230 | networksystem | netchannel packet processing |
| 1800f7e00 | networksystem | CNetworkSystem vfn 20 (0xa0), the poll (vtable 0x18023a788) |
| 1800c00b0 | networksystem | dispatcher: margin into message +0x20 (1800c03be) |
| 1800c5c10 | networksystem | net channel vfn 0x50: max(1e-6, ping (+0x8f04 ms) / 1000) |

## Protobuf messages

`CSGOInputHistoryEntryPB`: 2 view_angles, 4 render_tick_count, 5 render_tick_fraction, 6 player_tick_count,
7 player_tick_fraction, 12 cl_interp, 13 sv_interp0, 14 sv_interp1, 15 player_interp, 64 frame_number,
65 target_ent_index, 66 shoot_position, 67 target_head_pos_check, 68 target_abs_pos_check, 69 target_abs_ang_check.

`CSGOUserCmdPB`: 1 base (CBaseUserCmdPB), 2 input_history (repeated), 6 attack1_start_history_index,
7 attack2_start_history_index, 9 left_hand_desired, 11 / 12 / 13 is_predicting_body_shot_fx / head_shot_fx / kill_ragdolls.

CCLCMsg_Move: only fields 3 data and 4 last_command_number (tools/re/game/protomsg.py on engine2_20261029).

## Fields

| Offset | Field |
|---|---|
| CSGOUserCmdPB +0x10 | has-bits |
| +0x18 / +0x20 / +0x28 | input_history RepeatedPtrField / count / rep |
| +0x30 | base (bit 1) |
| +0x38..0x3b | the four bools (bits 2..0x10) |
| +0x3c / +0x40 | attack1 (bit 0x20) / attack2 (bit 0x40) start_history_index; both -1 when cleared |
| CCSGOUserCmd +0x10 | the message: server reads cmd +0x4c / +0x50 (indices), +0x38 history / +0x30 count |
| CUserCmd +0x78 | lag-comp history index (-1 by default) |
| CUserCmd +0x90 | the late link (0: on time) |
| base +0x54 | tick count |
| base +0x58 / +0x5c / +0x60 | forward / side / up (has-bits 0x40 / 0x80 / 0x100) |
| base +0x64 | impulse |
| base +0x68 | cleared in a substitute |
| base +0x6c | random_seed |
| base +0x80 | cmd flags (substitute: 0x50 cleared, 0x80 set) |
| base +0x40 | view angles x / y / z (has-bits 1 / 2 / 4) |
| server entry +0x18 | view angles (CMsgQAngle) |
| server entry +0x20 / +0x28 / +0x30 / +0x38 | cl_interp / sv_interp0 / sv_interp1 / player_interp infos (bits 2 / 4 / 8 / 0x10; info +0x18 frac, +0x1c src, +0x20 dst) |
| server entry +0x40 | shoot position (0x20) |
| server entry +0x48 / +0x50 / +0x58 | target head / abs origin / abs angles |
| server entry +0x60 / +0x64 | render tick / fraction (0x200 / 0x400) |
| server entry +0x68 / +0x6c | player tick / fraction (0x800 / 0x1000) |
| server entry +0x70 | frame number (0x2000) |
| server entry +0x74 | target entity (0x4000) |
| client input +0x2c / +0x38 | button event count / events (0x20 bytes) |
| client input +0xbc8[i] | attack i's down byte |
| client input +0xbcc[i] | attack i's press index (-1) |
| client input +0xbd8 / +0xbe0 / +0xbe8 | history count / array (0x60-byte entries) / capacity |
| client input +0xbf0 | the last event read |
| client entry +0..+0xf | ticks and fractions |
| client entry +0x10..+0x4c | view angles, shoot position, target ent (-1), target checks |
| client entry +0x50 / +0x54 / +0x58 / +0x5c | frame number / index in the command (-1 until sent) / tag / bucket |
| view record (vfn 0x568 of [182566100]) | +0 frame number, +4.. render tick / fraction and player tick / fraction, +0x18 view data |
| controller +0x4b8 | m_nTickBase |
| controller +0x4c0 | CUtlLinkedList of queued commands (0xa0-byte elements; prev / next +0x98 / +0x9c; head +0x4d0, tail +0x4d4, count +0x4dc) |
| controller +0x388 bit 8 | fake client (bot) |
| controller +0x5b8 | the last command run (embedded command; +0x630 its +0x78) |
| controller +0x5c0 | last_cmd_number_executed |
| controller +0x650 | highest received |
| controller +0x654 | arrival status ring (16) |
| controller +0x6dc | the last message's margin |
| controller +0x6e0 | the queue |
| controller +0x6e8 | cl_cq_min_queue (userinfo) |
| controller +0x708 | current command |
| queue (0x270) +8 | the controller |
| queue +0x15c / +0x160 / +0x164 | substitutes in a row / trimmed total / substitutes total |
| queue +0x168 | the highest trimmed number |
| queue +0x16c | "extended starvation" |
| queue +0x170 | warm-up count (0x7fffffff when built) |
| queue +0x174 | host catch-up request (fake client, or 180b5cf10's; never a remote player) |
| queue +0x178 | bloat streak |
| queue +0x198 | history of up to 60 numbers (0x138-byte entries: [0] number, +8 a real command, +0xa0 a substitute's copy, +0xa8 its number) |
| queue +0x268 | cq_logging stats |
| mv +0 | bit 0 = late link non-null || force; bit 1 = the late link |
| mv +0xc8 | origin |
| mv +0xd4 / +0xd8 | span start tick / tick |
| mv +0xdc / +0xe0 | step fractions |
| gpGlobals +0x14 / +0x18 | the frame's tick index / ticks |
| gpGlobals +0x30 / +0x34 / +0x44 / +0x48 / +0x50 / +0x58 | curtime / frametime / tick / (domain) / fraction / thread id |
| weapon services +0xe0 | shoot position history CFixedSizeCircularBuffer<ShootPositionHistoryEntry_t, 32, int>: records +0xe8 (0x14: tick, fraction, x, y, z), head +0x368, count +0x36c |
| weapon services +0x370 | input history CFixedSizeCircularBuffer<CSGOInputHistoryEntryPB, 32, int> (RTTI 0x181f164e0): records 0x78 from +0x378 (+0x18 view angles, +0x40 shoot position, +0x60 / +0x64 render tick / fraction, +0x68 / +0x6c player tick / fraction; read by the attack-time walk also as +0x18.. a position, +0x48 a vector, +0x70 / +0x74 player tick), head +0x1278, count +0x127c (relative +0xf08 / +0xf0c); never cleared |
| pawn +0xb58 / component +0x40 | PreThink component list head / next |
| pawn +0xbc8 | v_angle (schema; not m_angEyeAngles, which schema.py puts at +0x15b4 on CCSPlayerPawn: checked against the schema and the disassembly at 180c7b529..55b) |
| pawn +0xbd4 | v_anglePrevious: v_angle copied there at 180c7b537 (after PostThink vfn 0xb18 and before vfn 0xb20 ItemPostFrame), then v_angle = the movement services' +0x228 / +0x230: at the shot, the eye angles before this command's |
| pawn +0xff0 | PreThink runs the list only while 0 (unnamed) |
| pawn +0x414 bit 8 | frozen (a bot's buttons zero) |
| attack info +0 | attack time |
| attack info +0xc | render tick / fraction (the lag compensation's time) |
| attack info +0x14 | shoot position |
| attack info +0x20 | view angles |
| attack info +0x38 / +0x39 | has-history flag / vfn 0xb98 or 0xd20 |
| attack info +0x3c | source: 0 entry, 1 between records, 2 newest record, 3 first entry, 4 slerped first entry, 5 eye |
| CBot +0x28 | the command |
| CBot +0xc0 / +0xc1 / +0xd0 | buttons |
| CBot +0xc4 / +0xc8 / +0xcc | moves |
| engine2 client +0xac / +0xb0 | command interval / time |
| engine2 client +0x2c35a8 | send history (256 x 0x38 by number & 0xff: +0 number, +8 build time, +0x10 Plat_FloatTime, +0x18 send time, +0x20 a float from the send (+0x2ccfe0; >= 0 to count), +0x28 largest margin reported (FLT_MAX until one), +0x30 late flag) |
| engine2 client +0x2c3580 | re-sync number |
| engine2 client +0x2caf2c / +0x2caf34 | EMAs (logging only) |
| engine2 server client +0xee8 | Move message counter |
| packet +0x60 / +0x74 | receive time (int64 µs, socket clock) / MsgTick |
| message +8 / +0x1c / +0x20 | receive seconds / channel +0x8dac / margin |
| net channel +0x8f04 | ping (SteamNetworking real-time status m_nPing, ms) |
| interp ring (client) | 16 int ticks at +8, head +0x48, count +0x4c; ring 0 = 0x1822332d0, ring 1 = 0x182233280 (1015: 18222e250 / 18222e200) |
| interp info | +0x00 newer sample, +0x08 its tick, +0x10 older, +0x18 its tick, +0x20 third, +0x28 its tick, +0x30 fraction clamped [0, 2], +0x34 fraction, +0x38 hermite, +0x39 extrapolate |
| interp var +0x10 | flags: bit 0 linear only, 0x20 the second history |
| interp var +0x18 | time offset |
| interp var +0x20 | history: +0 block, +8 packed (bits 0..5 newest slot, 6..11 stride, 13..18 count, 19..24 capacity); slots [i32 tick, i16 index], newest first; Vec3D values from capacity x 8 at index x stride x 12 |

## Constants

| Value | What |
|---|---|
| 1 IN_ATTACK, 0x800 IN_ATTACK2 | attack buttons |
| 0x10000 / 0x10040 / 0x10080 / 0x10081 | arrival status: received (no margin yet) / never received (a gap below a newer number) / not the last command of its message / a number below 1 |
| `floorf(clamp(m, -15.99998, 15.99998) x 4096 + 0.5)` (0x417fff00 the clamp) | margin encoding |
| 0xffff + length | a run of 0x10000..0x1003f statuses |
| MD5_PseudoRandom(number) & 0x7fffffff | substitute random_seed |
| 4 entries | history trim threshold |
| 0.25 (0x181b03ca0), 0.5 (0x181acb080), FLT_MAX (0x181acb0b8), abs mask 0x181acb100 | trim |
| 1.0 (0x181acb084) | 180d04300's param_4 |
| 0x3eb0c6f7a0b5ed8d | 1e-6 (double) |
| d in [-5000, 100000] µs (d + 5000 <= 105000 unsigned) | margin window |
| [0x1802a3998] | socket clock - Plat_FloatTime x 1e6 (set in 1800f7e00) |
| [0x1802a59f0] vfn 0x60 | socket clock (µs) |
| 201 ms | rewind candidate window |
| 1.0 (0x3f800000) / 0.4 (0x3ecccccd) | knife delay: stab / else |
| 0x181e328d8 | global uniform random stream (PTR) |
| 0x1821ba1c0 | CCSGameRules pointer |
| PTR 181e448e0 | lag compensation manager |
| 0x181aacb00 | client IAT ThreadInMainThread |
| 0x181aac630 / 0x181aac680 | client IAT V_sincosf / V_atan2f |
| 0x18236fa60 | client slerp zero-length constant (identity, static init) |

## Cvars

| Cvar | Default | Where |
|---|---|---|
| sv_usercmd_custom_random_seed | 0 | |
| sv_autobunnyhopping / sv_subtick_movement_view_angles | 0 / 1 | (default byte at the setup's +0x37) |
| cl_csgo_shoot_trim_input_frames | bool 1, flags 2 | value 1825809e8, object 1825809e0 |
| sv_csgo_shoot_verify_on_attack_only | 1 | 0x1824cf638 |
| sv_csgo_shoot_log_attack_cmds_only | 1 | 0x1824cf5f8 |
| sv_csgo_shoot_verify | | 0x1824cf608 |
| sv_csgo_shoot_use_full_interp | | 0x1824cf648 |
| cl_interp_ratio | float 2.0 (0x181acb088), min 0, max 19.0 (0x181bd8ec0), flags 0x200 | 0x182542348 (1105), 0x182581638 (read in 180d04300); "Set number of client simulation interpolation ticks." |
| cl_interp | read-only | 0x182542378; "Read the effective client simulation interpolation amount in terms of time" |
| cl_interpolate / cl_extrapolate | 1 / 1 | |
| cl_interp_hermite | 1, flags 0x4000 | 0x18255f2b8 |
| cl_interp_threadmodeticks | int | |
| sv_client_min / max_interp_ratio | | server |
| late command limit | | [182191508] +0x58 |
| cq_enable | 1 | |
| cq_max_starved_substitute_commands | 4 | |
| sv_cq_trim_bloat_remainder / _space | 1 / 0 | |
| sv_cq_trim_catchup_remainder | 1 | |
| cq_fake_starve | 0 | |
| sv_late_commands_allowed | 5 (negative: from the round trip) | |
| cq_dilation_percentage | 5 (0.1..10) | |
| sv_cq_min_queue | 0 | engine2 2026-10-29 |
| cq_buffer_bloat_msecs_max | 150 | engine2 |
| cl_cq_min_queue | 0 | engine2: "Used by the client to inform the server of their desired queue length" |
| cl_tickpacket_recvmargin_desired | 5 ms | engine2 2026-10-15 |
| cl_tickpacket_desired_queuelength | 0 (0..5) | |
| cl_tickpacket_recvmargin_window | 4 s | |
| cl_tickpacket_recvmargin_minsamples | 10 | |
| cl_tickpacket_recvmargin_timeconstant | 0.4 s | |
| cl_tickpacket_recvmargin_adjust_limit | 5 % | |
| cl_async_usercmd_send | 1 | |
| engine_frametime_warnings_enable | 1 | |
| cl_async_usercmd_send_recvmargin_min | 1 | |
| cl_debug_build_recvmargin_min | 2 | |
| cl_usercmd_max_per_movemsg | 4 | |
| host_timescale | 1 | |
| bot_crouch | | 1821755f0 |
| sv_maxunlag | | |
| shoot position lerp cvar | | DAT_18212b230 |

Queue cvars named in the binary: cq_enable, cq_dilation_percentage, cq_buffer_bloat_msecs_max,
cq_max_starved_substitute_commands, sv_cq_min_queue, sv_cq_trim_bloat_*, sv_cq_trim_catchup_remainder; logs "STARVE",
"BLOAT", "catchup".

## Client history (180d07790)

1. Button events (180b72060): an event whose button is 1 or 0x800 sets input +0xbc8[i] to its down byte and marks attack i pressed when a down event.
2. The frame's view record. A frame with the same number and no attack press adds nothing. Else the frame's entry (a frame already recorded is reused).
3. For each attack pressed in this frame, when input +0xbcc[i] is -1 it takes this entry's index (the first press of the command wins); attack 1 also refreshes the shoot position record (180d0c170).
4. The entry is the frame that processed the event, not the event's time. 180d04300 runs 180d07790 first: an event the frames haven't read is read there on the last frame's record (a new entry when that frame isn't in the command: its player tick then the previous one).

So a command has an attack's history entry exactly when the attack button went down in one of its frames; holding adds
none; the entry is the frame of the first press (its player tick / fraction = the attack time; render tick / fraction
= the lag compensation's target).

## Command history out (180d04300)

1. 180d07790. More than one entry and the newest's tick (+8) below the oldest's (the clock went back): only the newest kept (moved to the front) and a set press index becomes 0; a press index at or past the count is logged and cleared.
2. More than 4 entries and cl_csgo_shoot_trim_input_frames on: the trim; else every entry through 180ce0280 with bool = pressed || !sv_csgo_shoot_log_attack_cmds_only.
3. attack1_start_history_index = the pressed entry's +0x54, has-bit 0x20, else -1 (has-bit cleared); attack 2 the same (0x40). An index at or past the history's count is logged and set to -1.
4. is_predicting_* from the pawn's weapon (vfn 0xab8, +0x1ecc, +0x14bc's target) and three cvars.

## Trim (180d044bf..180d0478f)

1. Tags: attack 2's pressed entry's +0x58 = 1, then attack 1's = 0.
2. `s = (float)tick + ratio` of newest +8 - oldest +8 (ticks); `q = s x 0.25`; `step = 1815f2a70(q)`; `end = oldest + step`; `h = q x 0.5`.
3. Buckets k = 0, 1, ... while entries are left: `mid = end - 1815f2a70(h)`; best = FLT_MAX; from the last entry taken: k < 3 and the entry not before end (its tick, then comiss on the ratios: 0xff and the unordered 0x80 are "before", 0 and 1 end the bucket) ends the bucket; else +0x5c = k; tag -1: `|(float)d.tick + d.ratio|` of (entry - mid) below best (strictly) takes it; a tag: 180cfc880 writes it at once (bool 1; +0x54 = its index) and the bucket is "written"; after the bucket, not written and a best: 180ce0280 with bool = !sv_csgo_shoot_verify_on_attack_only; `end += step`.
4. With the defaults only a pressed entry carries the interp infos.

## Entry writer (180cfc880)

- Render tick / fraction; with PTR 18223b370's +0xca the player tick / fraction; view angles; under sv_csgo_shoot_verify the shoot position and target head / abs origin / angles with the target entity; frame number.
- Interp block, under sv_csgo_shoot_use_full_interp and the bool: player_interp from 1809eae60 (written when its src is below the player tick, else "Invalid player history"); then with param_4 and param_5 finite (exponent not 0xff):
  - cl_interp: only its frac, from `180af4df0(ring 0, render - 1815f2fc0(1.0))`;
  - sv_interp0: `180af4df0(ring 1, (cl_interp's src, 0) - cl_interp_ratio ticks)` -> src, dst, frac;
  - sv_interp1: the same at `(cl_interp's dst, 0) - cl_interp_ratio`.
- 180af4df0: empty: (-1, -1, 0); from the newest down, the first tick at or below t's **tick** (ratio not compared): the newest -> (it, it, 0); else (it, the next newer, `((float)(t.tick - it) + t.ratio) / (float)(next - it)`) (cvtdq2ps, addss, divss); none -> (oldest, oldest, 0).
- Rings: list 1 (180b6d700 after the network update) pushes the network interface's vfn 0xb8 -> vfn 0x40 tick (the update's server tick); list 0 (180a4f840) the client's gpGlobals tick, every simulation tick; both overwrite the oldest at 16.
- The others are drawn at render tick - 1 - cl_interp_ratio = render - 3. The server's use: [shots.md](shots.md) 5b.

## Interpolated vars (client)

- GetInterpolationInfo at time t (seconds; less the var's offset unless asked not to): from the newest, the first pair whose older's tick x 1/64 is at or before t: fraction `(t - older) / (newer - older)` (ticks x 0.015625, f32), clamped to [0, 2]; past the newer: extrapolate, +0x30 = 1. With one more older sample whose tick is below the older's: +0x38 = cl_interp_hermite. None: the oldest twice.
- **The hermite never engages**: the "third" sample filled (+0x20 / +0x28) is the older one itself (an off-by-one: head + 1 + the loop counter, the older's slot), so `older's tick - third's tick > 0` fails. Same in 180160d10, 18088a9b0, 1808cd6d0. CS2 draws these vars linearly (seen for every pair of samples 100..103 at t = 100.5 / 101.5 / 102.5, cl_interp_hermite on; at t = 103.4, past the newest: +0x39 extrapolate, +0x30 = 1).
- Hermite path (unreached): third's tick moved to even spacing (`third = older - (newer - older)` when (newer - older) > 0 and unequal to (older - third)); 180159e00: `h00 = (2t^3 - 3t^2) + 1`, `h01 = 3t^2 - 2t^3`, `h10 = (t^3 - 2t^2) + t`, `h11 = t^3 - t^2`; `out = h00 a + h10 (b - a) + h01 c + h11 (c - b)` with (a, b, c) = (r9 = +0x20, 5th = +0x10, 6th = +0x00) (180159e2a..): h00 on the third sample (Source 1's Hermite_Spline puts it on p1).
- Vector (180159d40): f exactly 0 or 1 that sample; one sample for both that one; else per component `((newer - older) x f) + older` (subss, mulss, addss).
- QAngle (1808d84c0): the same cases (1808ec0a0), then 1808badd0: all three components equal the older's, else 181744420.
- Extrapolation (18089c450's branch) needs the var's time offset above 1e-6 and a global.
- Checked natively: rubikon/tests/InterpOracle (client_20261015 image, ThreadInMainThread stubbed, tier0_20261015's V_sincosf / V_atan2f).

## Server tick for a command

- RunCommand (180c7cb80): cmd +0x90 == 0 and frametime != 0: m_nTickBase + 1 (SetTickBase). Then gpGlobals tick = m_nTickBase, curtime = tick x 1/64, fraction 0, frametime 1/64 when cmd +0x90 is 0 (else 0); 180b70e10 / 180b70d20; 180c7b050; vfn 0x158; gpGlobals restored.
- RunCommands (180c7cdb0): drops commands older than the last's number less a limit through vfn 0xd8; gpGlobals tick = m_nTickBase, curtime it / 64, **frametime 0**, fraction 0; each: 180b750e0, vfn 0xc8 (no tickbase step, frametime 0), 180b75cd0. Then the last command's 180b511d0, gpGlobals restored.
- The queue sets the tickbase to gpGlobals' tick - 1 before each run. **Late** commands run through vfn 0xd0 (frametime 0, at tick - 1); the **on-time** command then runs through vfn 0xc8 directly (180ed5cdf) with the frame's frametime: the tickbase steps to the server tick itself (shared with the entities' thinks and the lag compensation's record).

## Seed (1802a4e90)

SHA-1 of the angles and **the attack time's tick**, unless 0x181daae64 differs from 0x181daae60 (the command's
random_seed, set by 180c7f1e0 / reset by 180c70120): 180c7f1e0 puts a fresh random there only with
sv_usercmd_custom_random_seed. Recoil's own seed is still the command's random_seed ([aim-punch.md](aim-punch.md) 1). The
attack time: [fire-gate.md](fire-gate.md) (GetWeaponAttackTime).

## CPlayerCommandQueue

Receive (180b68540):
1. Last run number = vfn 4.
2. Each command: the highest received and the status ring updated (the margin encoded for the last of a message).
3. A number above the last run: 180b69000 (from the head, before the first with a higher number, an equal number dropped, else at the tail). Not above: vfn 5.
4. vfn 7.
5. The last command of a message gets `encode(min(n - last run - 1, queue count) / 64 + param_5)` (param_5 = the message's margin, message +0x20).

Each server tick (180ed4ea0; a fake client's queue does nothing):
1. cq_fake_starve discards that many.
2. **Empty: a substitute** (180ed4be0, "OnSimulateUserCommands(), generating substitute command %d from %d") from the last run: starve count + 1; number = the last's + 1, the same once the count reaches cq_max_starved_substitute_commands; "extended starvation" when that number is at least 64 past the highest received. 180b511d0: mode 0 a copy with the subtick moves and input history cleared, base +0x68 cleared, flags 0x50 cleared / 0x80 set, tick count + 1, random_seed = MD5_PseudoRandom(number) & 0x7fffffff; mode 1 (extended) a new command with only the last view angles. In through 180b69000 (no "newer" test: a repeated number runs again) and into the history (+0xa0). Bloat streak 0.
3. **Not empty**: a starve count above 1 logs "OnBuffer"; starve count and extended flag 0. On a frame's first tick (gpGlobals +0x14 == 0): `cap = max(sv_cq_min_queue + 1, (int)(clamp(cq_buffer_bloat_msecs_max, 0, 1000) / 1000 x 64 + 0.5))` = 10 (32 with a catch-up request); `excess = count - cap + ticks`; streak + 1 while above 0, else 0; warm-up below 4: + 1 and a warm-up tick. Catch-up request, streak above 2, excess and ticks above 2: run `excess / 4 + 2`. A warm-up tick or streak above 2 x ticks trims: `keep = max(cl_cq_min_queue, sv_cq_min_queue) + sv_cq_trim_catchup_remainder` (warm-up) or `+ sv_cq_trim_bloat_remainder`, a bloat's at least `cap - sv_cq_trim_bloat_space`, never above the cap ("CQ limit"); `target = (ticks - 1) + run + keep` (catch-up: no trim within 1..99 of it, run += min(that, 20)); while count > target the head goes to the history as a real command (+0x168 its number). Trimmed with one tick a frame and warm-up below 4: warm-up = 4. Logged "CQ %s: removed %d" ("bloat" / "catchup").
4. Warm-up at 4..0x7ffffffe -> 0x7fffffff and 180b4ad90 ("catchup").
5. **Run**, `run` times while commands remain: pop the head; the history's real commands not yet run go first, through RunCommands at tick - 1 with frametime 0 (dropping those more than sv_late_commands_allowed before this one through vfn 0xd8); then tickbase = tick - 1 and this one through vfn 0xc8 (frametime 1/64, tickbase stepped to the tick); 180edcb20, 180b75cf0. The history keeps numbers within 60.
6. The frame's last tick: 180ee1010.

Report (180b525e0, CSVCMsg_PacketEntities: last_cmd_number_executed = controller +0x5c0, last_cmd_number_recv_delta
from +0x650, cmd_recv_status): the last run, the highest received, the last message's margin, then at most 8 status
words walking down from the highest received - 1 over 16 numbers (a run packed as 0xffff + length, any other as it is,
stopping at 0x10081); vfn 3 adds cq_starved_command_ticks, cq_discarded_command_ticks.

## Late command movement

180c7b050 sets frametime to RunCommand's (0 late) and calls 180c60a80: `mv+0 bit 0 = late || force`, bit 1 = late,
`mv+0xd8 = tick`, `mv+0xd4 = tick - (bit 0 ^ 1)`: a late command's span is 0 ticks (on-time [tick - 1, tick]). SetupMove
(vfn 0x110); 180c6f2a0 per step: `frametime = (mv+0xd8 - mv+0xd4) x 1/64 x (mv+0xe0 - mv+0xdc)` = 0, the step's time 0
when bit 0 is set, the view angles from the step (sv_subtick_movement_view_angles), vfn 0x118, PlayerMove (0xe0), vfn
0x138 every step, then 180c80540; the step builder's apex cut needs bit 0 clear. FinishMove (vfn 0x130) after. Nothing
moves, but the angles, button states and a jump's impulse apply.

## Subtick step time (180c6f2a0)

For each step whose `when` differs from the last (the first against 0): gpGlobals tick = mv+0xd4, fraction = `when`
(0 with mv+0 bit 0); fraction >= 1 -> tick + 1, fraction - 1; < 0 -> tick - 1, fraction + 1; `curtime = tick / 64 +
fraction / 64`; `frametime = (mv+0xe0 - mv+0xdc) x (mv+0xd8 - mv+0xd4) / 64`; thread id at +0x58; vfn 0x118, 0xe0,
0x138; all five restored. 180b21ba0 reads the tick through 180c86d00 -> 180927c50 (gpGlobals +0x44 for a non-zero
domain; else with 0x1821ba1c0 set, 180de8680; no gamerules: +0x44) and back through 1809249b0.

## Client pacing (engine2)

- Command clock (cl_async_usercmd_send 1): 1800651d0 builds the command due (180063f30: `+0xb0 += +0xac`), sends it, then 180062820: `+0xac = 1/64 / host_timescale + 1800628a0(next number, +0xb0 + that interval, interval)`.
- 180062230, a report: "first" for the highest received: `(highest - last run) x interval + message margin` (when >= 0); then down from highest - 1, each status word: a margin (v / 4096, "history"), a run (0xffff + k: k skipped), 0x10081 ("CQ: Server set re-sync at cmd %d": +0x2c3580 = that + 1, older samples ignored), 0x10040 / 0x10080 ("backfill": the next number's margin - 1 tick when above -3 ticks), else "unknown". 180061e90 keeps one when larger than before; a negative one marks it late.
- 1800626c0, desired margin: `cl_tickpacket_recvmargin_desired x 0.001 + max(sv_cq_min_queue, cl_tickpacket_desired_queuelength) / 64` (+ cl_debug_build_recvmargin_min with engine_frametime_warnings_enable off, + cl_async_usercmd_send_recvmargin_min with cl_async_usercmd_send off): 5 ms at the defaults. 1800642d0 sets userinfo cl_cq_min_queue = (int)(that x 64): 0.
- 1800628a0, the step: samples of the last `(int)(cl_tickpacket_recvmargin_window x 64 + 0.5)` numbers (at most 256, none at or before the re-sync), each projected: `((next - n) x (1/64 / timescale) + its send time - the next command's time) + its margin`; with at least max(1, minsamples): `excess = smallest - desired`, a negative one no lower than `-max(0, (cq_buffer_bloat_msecs_max x 0.001 + 0.99 / 64 - 0.005) - largest)`; then `(1 - V_expf(-(1 / clamp(timeconstant, 0.01, 10)) x clamp(interval, 0.001, 1))) x excess`, clamped to +-clamp(adjust_limit, 0, 90) % of the interval. Proportional: a steady clock drift leaves a steady error (a 1 % slow clock settles 4 ms under the target).
- Move packet (1800642d0): resends from latest - min(unacknowledged count, cl_usercmd_max_per_movemsg) + 1 to latest (UDP); the server drops repeats (180b69000).

## Arrival margin

- 180def9d0: param_3 the CNetMessagePB<CCLCMsg_Move>; protobuf at +0x30 (data +0x48, last_command_number +0x50); +0x20 is the net-message wrapper's. From ProcessMove 1800bc480 (more than one Move in a packet disconnects: "Too many move messages").
- 1800c2230 (from the poll 1800f7e00): margin xmm8 = -1; receive time and poll time (r8) non-zero: `d = poll - receive`; d in the window -> `margin = (float)(max(d, 1) x 1e-6)` (double multiply, cvtpd2ps). xmm10 = `(receive - [0x1802a3998]) / 1e6` (Plat_FloatTime seconds). 1800c00b0 stores margin at +0x20, receive seconds at +8, the channel's +0x8dac at +0x1c. Margin x 1000 is TraceLogging NetChanRecv's RecvMarginMS.
- The poll reads the socket clock once before walking the received packets; every packet of the poll is measured against it.
- 18022b960 per tick: AdvanceTick -> PollNetworking -> ProcessNetworking -> BeginSimulate: the margin is how long the packet waited for the tick that takes it.

## GetWeaponAttackTime's outputs (180a02c60)

1. With an entry: +0xc = the entry's render tick / fraction, +0x14 shoot position, +0x20 view angles, +0x3c = 0, +0x38 = 1; the entry's player interp (+0x38, 180a1e3d0: kept when 0 <= src <= dst and frac in [0, 1]) and +0x40 (three floats) for 180a02700.
2. Without: `A = clock + 1 tick + +0x10c0` (stored at +0 first). Walk (xmm11 = 0) from the newest record down: a record whose player tick is after A is skipped; else `d = A - its tick`, d after (4, 0) ends the walk with nothing; the newest: +0xc = its render tick, shoot position 180a02700(A, none), +0x3c = 2, angles its +0x20; else with record i + 1: `f = ((float)(A - T_i).tick + ratio) / ((float)(T_{i+1} - T_i).tick + ratio)` (divss), `+0xc = 1813b9690(R_i, R_{i+1}, f)`, shoot position under DAT_18212b230 from the records' +0x40 lerped (else the shoot history), angles AngleQuaternion of each, fitted slerp by f (a = record i x w0, b = record i + 1 x w1; instruction order as UpdateOrientationBlend's, [trains.md](trains.md)), QuaternionAngles (180a0360e..180a03734), +0x3c = 1. Attack time stays A, +0x38 stays 0.
3. Nothing found (180a037d9): now + 1 tick against A + (1, 0): now + 1 later -> +0 = now + 1 tick, +0x38 = 1 (logged "Firing first shot, sv tick ..., but no attack information present in command" for a non-bot, vfn 0xc20); else +0 = A. Then +0xc = the attack time, shoot position the pawn's (180b54f80), angles the eye angles (vfn 0x5f0), +0x3c = 5; with history entries in the command, the first entry's angles (+0x3c = 3), slerped from pawn +0xbd4 when its render time is after the attack time (180a03b6a..180a03d74: its fraction > 0 and (its tick, 0) not after the attack time; `f = (attack - (tick, 0)) / (render - (tick, 0))`; +0x3c = 4).
4. 1809f9910's "clocks no earlier than now" (1809f99b3) tests +0x38.
5. Entry angles are the client's view + the aim punch (FX_FireBullets adds nothing outside debug_aim_angle); a source-5 shot (bots) has no punch.

1813b9690(out, a, b, f): `d = b - a` (1813b8fb0's borrow, V_modff fold); `out = (a.tick, ((float)d.tick + d.ratio) x f)`,
folded into [0, 1) (V_modff, a negative fraction borrowing, 1813b9170 if still out). a's fraction is not added.

## Shoot position

- 180a02700: shoot time = attack time less 1813b9870(180b52570 x 64) (one tick on a default server); then 180b07db0: 180b08260 walks the shoot position history from the oldest over consecutive pairs: a first record later than the time fails; the first second record at or past it gives `f = ticks(t - a) / ticks(b - a)` (float) and the eye `(1 - f) a + f b` per component; not found: "weapon services didn't find a shoot position history entry", vfn 0xc8 (the eye now). The entry's shoot_position is only compared (more than 1 u off: "Using server position").
- Writer 180b21ba0: time = (gpGlobals tick, +0x50), eye = vfn 0xc8; newest replaced when the time is equal, else pushed (oldest overwritten at 32). Called only from 180ae9260 (after it sets the eye height), from 180ac4c00 (origin from mv +0xc8 and the velocity, then 180ae9260 with frametime): the per-step call after PlayerMove. Every movement step records the eye at its time.

## Weapon services input history writer (180b1d430)

The pawn's controller (pawn +0xc98 handle) +0x708, the current command; newest = the ring's newest player tick, or (0, 0) when empty; for each history entry
in order: when newest is before the entry's player tick (ints, then fractions; NaN not before), copied in at
(head + count) % 32, or at 32 over the head (destroy, construct, copy, head + 1), newest = its tick; entries at or
before the newest skipped. Called from CBasePlayerPawn::PreThink's component list (each vfn 0x60); CCSPlayerPawn's
PreThink runs it only while pawn +0xff0 == 0. 180c7b050 calls the pawn's vfn 0xb10 at 180c7b203, before 180c60a80 /
SetupMove: every command, late or on time.

## Rewind target (180ecb710)

1. `lat = now - from_ticks(latency / (1/64))`; latency = engine vfn 0x148(slot) net channel vfn 0x50 (refreshed from vfn 0x80 when stale).
2. Candidate = the time, or with none (ticks + fraction <= 0) the command's base +0x54 tick at fraction 0; kept when `(int)(|seconds(candidate) - seconds(lat)| x 1000) < 201` (180c629e0), else lat; then 180ec2130.
3. StartLagCompensation 180edebe0: CUserCmd +0x78 (-1: "Lag comp cmd had no attack history information, using target time"), the entry's has-bit 1 and its interp infos (+0x28 / +0x30, 180ebc9c0 from their +0x1c / +0x20), validated (180ed23a0), lerped (1813b93b0).
4. CUserCmd +0x78 is written by FX_FireBullets (1802a545c): attack2_start_history_index when the attack argument ([rbp + 0x340]) is 1, else attack1's; also the ShootVerify debug block. Every CUserCmd is built with +0x78 = -1; a queue substitute copies its source's. FX_FireBullets gets the attack info's +0xc as the lag compensation's time (BaseGunFire passes `&info + 0xc`). A held shot has no pair.

## Knife (180a2fa80)

1809f9910(weapon, info, delay, attack): GetWeaponAttackTime, +0x10c0 = attack - (now + 1), with +0x38 both clocks no
earlier than now (1809f99b3..1809f9b27), then SetNextPrimaryAttack(delay, 1), SetNextSecondaryAttack(delay, 1).
Knife delay 1.0 (stab) / 0.4; weapon +0xfe8 = &info. The swing calls the lag compensation manager vfn 0x10 with the
pawn, 2, info +0x14 (the eye), info +0x20 (the angles), range + 128 (fVar21: 32 or 48, + 18) and info +0xc as the time;
it never writes +0x78: "using target time".

## Bots

- CBot vfn 0xb0 (1802ed0b0): flags into the buttons, all zero for a frozen pawn; vfn 0xb8 builds the command with the pawn's eye angles (vfn 0x5f0), moves and buttons; vfn 0xc0; then the controller's receive 180b68540 with that one command and margin -1.0.
- CBot vfn 0xb8 (1802be4f0): 180cb7060 clears it (input_history empty, indices -1); number (cmd +8) and base +0x54 = gpGlobals tick; random_seed = RandomInt(0, 0x7fffffff) from the global stream; forward / side / up (has-bits cleared when 0); buttons (18068b000); impulse; view angles.
- No input history: a bot's shot takes the no-entry path with an empty weapon services' history (the calculated time, or now + 1 tick).
- bot_crouch is read in the duck code 180ac1ec0.

## Unread

- vfn 0xd8 (the dropped late ones), the catch-up path's exact counts, 180b4ad90.
- The send history's +0x20 float (>= 0 to count).
- cl_clock_recvmargin_* (the interpolation's own pacing).
- The subtick loop's gpGlobals stores during a step beyond the above.
- player_interp and the shoot position / target fields (read by the server only under sv_csgo_shoot_verify).
- A var's history reset on its own teleport flag; which vars have a time offset (extrapolation).
- CUserCmd +0x78 for a knife after a gun shot on a substitute.
