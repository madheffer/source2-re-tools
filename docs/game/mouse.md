# The mouse to the view angles (client_20261105.dll, traced 2026-11-12)

How CS2's client turns mouse counts into the view angles a frame draws and a command carries. Read with tools/re
(cvardump, xref, fnat, fnstrings, vtowner, vtdump, dispuses) on `tools/re/binaries/client_20261105.dll` (image base
0x180000000); no decompiler. The port: web/src/cs2web/client/core/mouse-look.js (web/src/cs2web/client/core/mouse-look-test.mjs).

## Cvars (a float cvar's value: `[object + 8] + 0x58`; 180babd40(object, slot) is the per-split-screen-slot getter)

| Cvar | Object | Registration | Default (min .. max) | Flags |
|---|---|---|---|---|
| sensitivity | 0x182567c40 | 1800d8230 | 1.25 (0.0001 .. 8) | 0x8280 |
| sensitivity_y_scale ("Multiplies the mouse Y axis for finer pitch vs yaw aim") | 0x182567c50 | 1800d82f0 | 1.0 (max 2.0) | 0x8280 |
| m_yaw | 0x182567c60 | 1800d7460 | 0.022 (0x3cb43958) | |
| m_pitch | 0x182567c70 | 1800d5af0 | 0.022 | 2 |
| mouse_inverty (bool) | 0x182567be0 | 1800d7500 | 0 | 0x280 |
| zoom_sensitivity_ratio | 0x1825600d8 | 1800c95c0 | 1.0 (0.01 .. 3) | 0x8080 |
| cl_pitchdown / cl_pitchup | read through 0x182564ce0 / 0x182564cf0 (180160c50) | 1800ceaa0 / 1800cebe0 | 89 / 89 | |
| input_filter_relative_analog_inputs (bool) | 0x1825fca98 | 18012a250 | unread (taken 0: no filter) | 0x80 |
| sv_cheats (the client's ref) | [0x182564540] | 1800d1e60 | | |

## The frame: CClientInput's 180b7de10(input, slot, frametime)

Called once a rendered frame (its profile scope names it "...ProcessI..."). `entry` = the newest of the input's
0x440-byte per-frame entries (array at input +0xb58, count +0xb50). In order:

1. vfn 0xf0(input, slot, entry, frametime); 180b65bd0.
2. **vfn 0xe8 (180b70000): the view angles out of the entry's +0x430 (a QAngle, 12 bytes)** into a local.
3. The keyboard's turn (180b61e00, 180b61b70, only with a positive frametime x a scale), then vfn 0xa8 (the clamp, below).
4. vfn 0xa0 / 0x98 / 0x90: the analog moves into entry +0x1c / +0x20 / +0x18 (each later held to -1 .. 1, 1801588f0).
5. **vfn 0xb0 (CCSGOInput 180ce5e80 = a jump to CClientInput 180b66e40): the mouse** (below).
6. **vfn 0xa8 (180b65450): the clamp**; **vfn 0xe0 (180b81fa0): the angles back into entry +0x430**.
7. 180b66190 (the subtick moves from the entry), the rest of the frame.

So the view angles live in the frame's input entry, a command takes them from there (usercmd.md: the view angles in
the command's base and in each input-history entry, protobuf floats), and they change once a frame.

### 180b66e40(input, slot, angles*, r9, ..., frametime): the mouse into the angles

Nothing when [0x1827a2350] is null or vfn 0xb8 (180cfea60: the mouse is the game's, no cursor / menu) says no.
scale = vfn 0xc0(input, 1.0) (CCSGOInput's 180b81ba0 returns its argument: 1). Then
180ba81d0(slot, scale, frametime, &pitch, &yaw, &entry+0x24, &entry+0x28) and 180ba7fa0 (unread: fills the r9 pair,
added to another pair), and:

```
angles[0] (pitch) = AngleNormalize(pitchDelta + angles[0])      180b66f2a..3a
angles[1] (yaw)   = AngleNormalize(yawDelta + angles[1])        180b66f3f..4f
```

**AngleNormalize 18035b3d0(v)**: -180 <= v <= 180 → v; else v - floor(v x 0.00277777785 (0x3b360b61) + 0.5) x 360,
then max(-180), min(180). f32 throughout (181a0da58 = floorf).

### 180ba81d0(slot, scale, frametime, pitch*, yaw*, dx*, dy*): the frame's counts

- A timer at [0x18256a3ec] off dev_create_sensitivity_report (0x18256a010): debugging.
- The frame's mouse x and y: two per-slot analog accumulators (stride 0x230), **x at 0x182567c80, y at 0x182568560**,
  read by 181225990 (this frame's sum at +0x28; with input_filter_relative_analog_inputs the mean of it and the last
  frame's +0x24; then held to the accumulator's own min / max, +0x10 / +0x14). Their +0x30 is a frame stamp with a low
  bit: the newer of the two picks the path, **bit 0 → 180ba8720 (a stick, unread), else the mouse 180ba88f0**; an
  axis whose bit differs from the picked one reads 0. Who fills the accumulators (inputsystem's raw counts) is unread.
- **The zoom**: pawn = 18096c1c0(slot); when its +0x149c > 0, scale x= it. (+0x149c is the zoomed mouse scale,
  fire-gate.md "The zoomed mouse": zoom_sensitivity_ratio x fov / default fov, 1 unzoomed.)
- 180ba88f0 (below), then 180ba8460: the look keys (four analog actions; pitch += (a - b) x frametime x 45, yaw -=
  (c - d) x frametime x 90).
- With the mouse path and **mouse_inverty: pitch x= -1** (180ba83b5..ce).

### 180ba88f0(slot, y, x, scale, pitch*, yaw*, dx*, dy*): counts to degrees

Sum order from the disassembly (all mulss, f32):

```
s  = sensitivity(slot)
X  = (x x scale) x s                         180ba892d, 180ba893e
Y  = ((y x scale) x s) x sensitivity_y_scale 180ba895b, 180ba896a, 180ba896f
*dx = (int) X (cvttss2si);  *dy = (int) Y    the entry's +0x24 / +0x28
p  = m_pitch(slot);  sv_cheats' ref null or its flags bit 10 → p = 0.022
     else sv_cheats on → p stays;  else p > 0 → 0.022, else -0.022       180ba8987..b8
*pitch = p x Y                               180ba89cf
*yaw   = (m_yaw(slot) x X) x -1              180ba89fd, 180ba8a08
```

So a count right turns the yaw down by m_yaw x sensitivity degrees, a count down turns the pitch up by 0.022 x
sensitivity; m_pitch's own value only counts with sv_cheats (its sign always does).

### 180b65450(input, angles*): the clamp

pitch = clamp(pitch, -cl_pitchup, cl_pitchdown) (18015a360(value*, min*, max*)); angles[2] (roll) = clamp(roll, -50, 50).
The yaw is not touched (AngleNormalize has it in +-180).

### 180b66190(input, slot, oldAngles*, input+0x718, angles*, entry+0x2c, entry+0x30, 0x20): the frame's subtick steps

Read as far as the steps' angles (2026-11-12): each step is a 0x28-byte record, built from the frame's button
events (the per-slot lists at input +0xb70, count +0xb68; an event's time at its +0x18) and, when the analog moves
changed, one for them. **Every record takes its angles from the fifth argument, the frame's view angles after the
mouse and the clamp** (180b66293 / 180b663c4: `[rbp + 0x50]` → +0 pitch, +4 yaw into the record). So a key pressed
between two frames is the later frame's: a step at the key's own time with that frame's angles. The record's other
fields and the grow path (181ab2808 / 181ab2800) are unread.

A command is built on the command clock (usercmd.md 6), not by a frame: it carries what the frames before its time
left (the entry's angles, the steps).

## The port, and where it is not CS2

- mouse-look.js `mouseAngles` (180ba88f0 + the inversion), `angleNormalize`, `addLook` (the two sums and the clamp);
  client/core/input.js turns the view with them and gives the same deltas to client/core/tick-input.js, whose ticks add them the
  same way: the aim a command carries is the view's, bit for bit, an f32 (it was rounded to 0.01 degrees before).
- The zoom's scale reaches the mouse (input.js `state.lookScale`); before, a scoped rifle turned at the unscoped rate.
- **Per frame, as CS2** (2026-11-12, second pass): client/core/input.js adds the mouse counts up between rendered frames;
  `sampleInput(now)`, the first thing client/core/game.js's frame does, turns the view by the sum (one mouseAngles, one
  addLook) and hands the frame to client/core/tick-input.js `frameInput`: the keys, wheel notches and clicks that came in
  since the last frame get that frame's angles, and a tick reads only what frames up to its end produced (a key no
  frame has seen yet waits for the next command, at its start).
- Settings (app/settings.js, the Controls card, the console): `sensitivity` 1.25 (0.0001 .. 8), `sensitivity_y_scale`
  1 (max 2; its min is unread: 0.01 here), `mouse_inverty`. cl_pitchup / down stay 89 (no setting).
- A touch drag turns by degrees of its own (CS2 has none), added by the same frame.
- Not checked natively: no oracle calls 180ba88f0 (it reads cvars through 180babd40); the port is the disassembly's
  five products. Unread: 180ba7fa0, the stick's 180ba8720, the accumulators' writer, whether the server alters a
  command's angles before it uses them.
- A browser's own limits: mousemove is aligned to the screen's refresh unless Max FPS is off the display (then
  pointerrawupdate); `unadjustedMovement` (no pointer acceleration) is asked for and silently given up when refused.
