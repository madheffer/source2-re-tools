# The mouse to the view angles

client_20261105 (image base 0x180000000), disassembly only.

## Functions

| Address | Module | What |
|---|---|---|
| 180babd40 | client | (cvar object, slot): per-split-screen-slot getter |
| 180b7de10 | client | CClientInput frame (input, slot, frametime), once a rendered frame ("...ProcessI...") |
| 180b65bd0 | client | frame step after vfn 0xf0 |
| 180b70000 | client | vfn 0xe8: view angles out of entry +0x430 |
| 180b61e00 / 180b61b70 | client | the keyboard's turn (positive frametime x a scale) |
| 180b65450 | client | vfn 0xa8: the clamp (input, angles*) |
| 180b81fa0 | client | vfn 0xe0: angles back into entry +0x430 |
| 1801588f0 | client | analog moves held to -1 .. 1 |
| 180ce5e80 | client | CCSGOInput vfn 0xb0 = jmp 180b66e40 |
| 180b66e40 | client | CClientInput: the mouse into the angles (input, slot, angles*, r9, ..., frametime) |
| 180cfea60 | client | vfn 0xb8: the mouse is the game's (no cursor / menu) |
| 180b81ba0 | client | CCSGOInput vfn 0xc0: returns its argument (1) |
| 180ba81d0 | client | the frame's counts (slot, scale, frametime, pitch*, yaw*, dx*, dy*) |
| 180ba7fa0 | client | fills the r9 pair, added to another pair (unread) |
| 18035b3d0 | client | AngleNormalize(v) |
| 181a0da58 | client | floorf |
| 181225990 | client | analog accumulator read |
| 180ba8720 | client | stick path (unread) |
| 180ba88f0 | client | counts to degrees (slot, y, x, scale, pitch*, yaw*, dx*, dy*) |
| 18096c1c0 | client | (slot): the pawn |
| 180ba8460 | client | the look keys |
| 18015a360 | client | clamp (value*, min*, max*) |
| 180160c50 | client | cvar read (cl_pitchdown / cl_pitchup) |
| 180b66190 | client | subtick steps (input, slot, oldAngles*, input+0x718, angles*, entry+0x2c, entry+0x30, 0x20) |
| 181ab2808 / 181ab2800 | client | the steps' grow path (unread) |

## Fields

| Offset | Field |
|---|---|
| cvar object: `[object + 8] + 0x58` | a float cvar's value |
| input +0xb58 / +0xb50 | per-frame entries (0x440 bytes each) / count |
| entry +0x430 | the view angles (QAngle, 12 bytes) |
| entry +0x1c / +0x20 / +0x18 | analog moves (vfn 0xa0 / 0x98 / 0x90) |
| entry +0x24 / +0x28 | dx / dy (int) |
| input +0xb70 / +0xb68 | per-slot button event lists / count; event time at +0x18 |
| step record (0x28 bytes) | +0 pitch, +4 yaw |
| accumulator (stride 0x230) | +0x28 this frame's sum, +0x24 last frame's, +0x10 / +0x14 min / max, +0x30 frame stamp with low bit |
| pawn +0x149c | zoomed mouse scale (zoom_sensitivity_ratio x fov / default fov, 1 unzoomed; [fire-gate.md](fire-gate.md) "The zoomed mouse") |
| [0x1827a2350] | null: no mouse |

## Constants

| Cvar / value | Object | Registration | Default (min .. max) | Flags |
|---|---|---|---|---|
| sensitivity | 0x182567c40 | 1800d8230 | 1.25 (0.0001 .. 8) | 0x8280 |
| sensitivity_y_scale ("Multiplies the mouse Y axis for finer pitch vs yaw aim") | 0x182567c50 | 1800d82f0 | 1.0 (max 2.0; min unread) | 0x8280 |
| m_yaw | 0x182567c60 | 1800d7460 | 0.022 (0x3cb43958) | |
| m_pitch | 0x182567c70 | 1800d5af0 | 0.022 | 2 |
| mouse_inverty (bool) | 0x182567be0 | 1800d7500 | 0 | 0x280 |
| zoom_sensitivity_ratio | 0x1825600d8 | 1800c95c0 | 1.0 (0.01 .. 3) | 0x8080 |
| cl_pitchdown / cl_pitchup | via 0x182564ce0 / 0x182564cf0 | 1800ceaa0 / 1800cebe0 | 89 / 89 | |
| input_filter_relative_analog_inputs (bool) | 0x1825fca98 | 18012a250 | unread (taken 0) | 0x80 |
| sv_cheats (client's ref) | [0x182564540] | 1800d1e60 | | |
| dev_create_sensitivity_report | 0x18256a010 | | timer at [0x18256a3ec] (debug) | |
| mouse x / y accumulators | 0x182567c80 / 0x182568560 | | | |
| 0.00277777785 (0x3b360b61) | 1/360 in AngleNormalize | | | |
| roll clamp | -50 .. 50 | | | |

## The frame (180b7de10)

`entry` = the newest per-frame entry. In order:

1. vfn 0xf0(input, slot, entry, frametime); 180b65bd0.
2. vfn 0xe8 (180b70000): angles from entry +0x430 into a local.
3. The keyboard's turn (180b61e00, 180b61b70), then vfn 0xa8 (the clamp).
4. vfn 0xa0 / 0x98 / 0x90: analog moves into entry +0x1c / +0x20 / +0x18.
5. vfn 0xb0: the mouse (180b66e40).
6. vfn 0xa8 (180b65450): the clamp; vfn 0xe0 (180b81fa0): angles back into entry +0x430.
7. 180b66190 (subtick moves), the rest of the frame.

The view angles live in the frame's input entry; a command takes them from there ([usercmd.md](usercmd.md): in the
command's base and in each input-history entry, protobuf floats); they change once a frame.

## The mouse into the angles (180b66e40)

1. Nothing when [0x1827a2350] is null or vfn 0xb8 says no.
2. scale = vfn 0xc0(input, 1.0) = 1.
3. 180ba81d0(slot, scale, frametime, &pitch, &yaw, &entry+0x24, &entry+0x28); 180ba7fa0.

```
angles[0] (pitch) = AngleNormalize(pitchDelta + angles[0])      180b66f2a..3a
angles[1] (yaw)   = AngleNormalize(yawDelta + angles[1])        180b66f3f..4f
```

AngleNormalize (18035b3d0): -180 <= v <= 180 -> v; else `v - floor(v * 0.00277777785 + 0.5) * 360`, then max(-180),
min(180). f32 throughout.

## The frame's counts (180ba81d0)

1. Mouse x / y from the two accumulators, read by 181225990 (+0x28; with input_filter_relative_analog_inputs the mean
   with +0x24; held to +0x10 / +0x14). The newer +0x30 stamp picks the path: **bit 0 -> 180ba8720 (stick), else the
   mouse 180ba88f0**; an axis whose bit differs reads 0. Who fills the accumulators (inputsystem) is unread.
2. Zoom: pawn = 18096c1c0(slot); +0x149c > 0: scale x= it.
3. 180ba88f0, then 180ba8460 (four analog actions): `pitch += (a - b) * frametime * 45`, `yaw -= (c - d) * frametime * 90`.
4. Mouse path and mouse_inverty: pitch x= -1 (180ba83b5..ce).

## Counts to degrees (180ba88f0)

All mulss, f32:

```
s  = sensitivity(slot)
X  = (x * scale) * s                         180ba892d, 180ba893e
Y  = ((y * scale) * s) * sensitivity_y_scale 180ba895b, 180ba896a, 180ba896f
*dx = (int) X (cvttss2si);  *dy = (int) Y    entry +0x24 / +0x28
p  = m_pitch(slot);  sv_cheats' ref null or its flags bit 10 -> p = 0.022
     else sv_cheats on -> p stays;  else p > 0 -> 0.022, else -0.022       180ba8987..b8
*pitch = p * Y                               180ba89cf
*yaw   = (m_yaw(slot) * X) * -1              180ba89fd, 180ba8a08
```

A count right turns yaw down by m_yaw x sensitivity degrees; a count down turns pitch up by 0.022 x sensitivity;
m_pitch's own value only counts with sv_cheats (its sign always does).

## The clamp (180b65450)

`pitch = clamp(pitch, -cl_pitchup, cl_pitchdown)` (18015a360); roll = clamp(roll, -50, 50). Yaw untouched.

## Subtick steps (180b66190)

- Each step is a 0x28-byte record from the frame's button events and, when the analog moves changed, one for them.
- Every record takes its angles from the fifth argument (the frame's angles after the mouse and the clamp)
  (180b66293 / 180b663c4: `[rbp + 0x50]` -> +0 pitch, +4 yaw).
- So a key pressed between two frames is the later frame's: a step at the key's own time with that frame's angles.
- A command is built on the command clock ([usercmd.md](usercmd.md) 6), not by a frame: it carries what the frames before its time left.

## Unread

- 180ba7fa0, the stick's 180ba8720, the accumulators' writer; whether the server alters a command's angles.
- The step record's other fields; the grow path (181ab2808 / 181ab2800).
- No native oracle for 180ba88f0 (reads cvars through 180babd40).
