# math_counter (CMathCounter), traced 2026-11-17

server_20261112.dll (source2-compiler tools/re/binaries), read with tools/re inputs.py / schema.py / fieldwrites.py /
disasm.py. Port: web/src/world/entities/classes/logic.js `math_counter`, test math-counter-test.mjs beside it.

## Fields (schema)

| field | offset |
|---|---|
| m_flMin | +0x4a8 |
| m_flMax | +0x4ac |
| m_bHitMin | +0x4b0 |
| m_bHitMax | +0x4b1 |
| m_bDisabled | +0x4b2 |
| m_OutValue | +0x4b8 (its stored float at +0x4d0) |
| m_OnHitMin / m_OnHitMax | +0x4f8 / +0x510 (the outputs UpdateOutValue fires) |
| m_OnChangedFromMin / Max | +0x528 / +0x540 |

The only byte stores to +0x4b0 / +0x4b1 in the class's code are UpdateOutValue's below: the latches are false from
construction (no Spawn sets them).

## Inputs (inputs.py: the CMathCounter_API bindings)

Add 0x180df8ab0, Divide 0x180df95c0, Multiply 0x180df9820, SetValue 0x180df9cc0, SetValueNoFire 0x180dfa130,
Subtract 0x180dfa4d0, SetHitMax 0x180dfaa20, SetHitMin 0x180dfade0, GetValue 0x180dfb1a0, Enable 0x180dfb4f0,
Disable 0x180dfb760. Each checks m_bDisabled (+0x4b2) first (set: a console warning, nothing changes). Subtract:
m_OutValue (+0x4d0) - the parameter (subss), then UpdateOutValue.

**SetValueNoFire** (0x180dfa130): with a range (min or max not 0) the value clamped (0x18017b220 (&v, &min, &max)),
then m_OutValue's Init (0x180e241e0): no output, the latches untouched.

## UpdateOutValue 0x180e36d10 (this, activator, float value)

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

The limit tests take the unclamped value; OnChangedFrom* compares the value stored before this update (not the
latch); the limit outputs fire before OutValue. What it fixed: our counter fired OnHitMin only when the value came
from above the min, so a counter starting on its min and set to it never did. ze_dark_souls' case picker sets
FCS_Spawn_Floor_Count_Counter (min 0, start 0) to 0..5; on 0 its OnUser1 loop (ForceSpawn FCS_Maker, Subtract 1,
FireUser1 itself 0.1 s on) never met OnHitMin's Kill, and spawned a func_button, an info_particle_system and a
filter every 0.1 s for the rest of the round (5400 entities and growing ~90 a second).

## Unread

- Spawn: whether a startvalue outside the range is clamped (Source 1's Spawn clamps; ours doesn't), min > max
- 0x18017b220's own order for min > max; SetHitMin / SetHitMax (0x180dfade0 / 0x180dfaa20): whether they re-test
  the value against the new limit (ours only sets it)
- m_OutValue.Set: whether OutValue fires when the value doesn't change (ours fires)
