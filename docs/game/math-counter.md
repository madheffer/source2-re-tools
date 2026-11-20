# math_counter (CMathCounter)

server_20261112 (read with tools/re inputs.py / schema.py / fieldwrites.py / disasm.py).

## Functions

| Address | Module | What |
|---|---|---|
| 0x180df8ab0 | server | input Add |
| 0x180df95c0 | server | input Divide |
| 0x180df9820 | server | input Multiply |
| 0x180df9cc0 | server | input SetValue |
| 0x180dfa130 | server | input SetValueNoFire: with a range (min or max not 0) clamps, then m_OutValue's Init; no output, latches untouched |
| 0x180dfa4d0 | server | input Subtract: m_OutValue (+0x4d0) - the parameter (subss), then UpdateOutValue |
| 0x180dfaa20 | server | input SetHitMax |
| 0x180dfade0 | server | input SetHitMin |
| 0x180dfb1a0 | server | input GetValue |
| 0x180dfb4f0 | server | input Enable |
| 0x180dfb760 | server | input Disable |
| 0x180e36d10 | server | UpdateOutValue (this, activator, float value) |
| 0x18017b220 | server | clamp (&v, &min, &max) |
| 0x180e241e0 | server | m_OutValue's Init (no output) |
| 0x180bbc480 | server | m_OutValue.Set (fires OutValue) |

Every input checks m_bDisabled (+0x4b2) first: set, a console warning and nothing changes.

## Fields

| Offset | Field |
|---|---|
| +0x4a8 | m_flMin |
| +0x4ac | m_flMax |
| +0x4b0 | m_bHitMin |
| +0x4b1 | m_bHitMax |
| +0x4b2 | m_bDisabled |
| +0x4b8 | m_OutValue (its stored float at +0x4d0) |
| +0x4f8 / +0x510 | m_OnHitMin / m_OnHitMax |
| +0x528 / +0x540 | m_OnChangedFromMin / m_OnChangedFromMax |

The only byte stores to +0x4b0 / +0x4b1 are UpdateOutValue's: the latches are false from construction (no Spawn sets them).

## UpdateOutValue (0x180e36d10)

```
if (min != 0 || max != 0) {                      // ucomiss against 0, both
  if (value >= max) { if (!m_bHitMax) { m_bHitMax = 1; m_OnHitMax.FireOutput(activator, this); } }
  else { if (m_OutValue == max) m_OnChangedFromMax.FireOutput(activator, this); m_bHitMax = 0; }
  if (min >= value) { if (!m_bHitMin) { m_bHitMin = 1; m_OnHitMin.FireOutput(activator, this); } }
  else { if (m_OutValue == min) m_OnChangedFromMin.FireOutput(activator, this); m_bHitMin = 0; }
  value = clamp(value, min, max);                // 0x18017b220
}
m_OutValue.Set(value, activator, this);          // 0x180bbc480: OutValue
```

- The limit tests take the unclamped value; OnChangedFrom* compares the value stored before this update (not the latch); the limit outputs fire before OutValue.
- So a counter starting on its min and set to its min fires OnHitMin (latch false). Example: ze_dark_souls' FCS_Spawn_Floor_Count_Counter (min 0, start 0) set to 0..5; its OnUser1 loop (ForceSpawn FCS_Maker, Subtract 1, FireUser1 itself 0.1 s on) relies on OnHitMin's Kill.

## Unread

- Spawn: whether a startvalue outside the range is clamped (Source 1's Spawn clamps); min > max.
- 0x18017b220's own order for min > max.
- SetHitMin / SetHitMax (0x180dfade0 / 0x180dfaa20): whether they re-test the value against the new limit.
- m_OutValue.Set: whether OutValue fires when the value doesn't change.
