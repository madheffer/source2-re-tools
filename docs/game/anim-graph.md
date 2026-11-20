# Anim graph runtime (NmGraph)

animationsystem_20261023. Asserts name `src/animlib/` (animpose.cpp, animskeleton.cpp, graph/animgraph_instance.cpp,
tasksystem/*). The runtime is Esoterica's, recompiled by Valve with their own maths (CTransform, the fitted slerp).
Checked bit for bit against the DLL called natively (rubikon/tests/AnimOracle).

## Functions

| Address | Module | What |
|---|---|---|
| IAT 18063f8c0 / 18063f3a8 | animationsystem | tier0 V_modff / V_cosf |
| 180001000 -> 180b3efd0 | animationsystem | static initialiser of the identity quaternion (BSS 180b3efd0) |
| 180398ef0 | animationsystem | decode a clip frame |
| 18007bf90 | animationsystem | clip time: the percentage by value in edx |
| 18038ef40 | animationsystem | wrap a percentage (V_modff's fraction; a negative one 1 - it) |
| 18039a8f0 | animationsystem | sample a clip into the pose |
| 180439d40 | animationsystem | blend(lod, src, tgt, w, out, layered) |
| 18043bb40 | animationsystem | CNmBlendTask (layered 0) |
| 18043c500 | animationsystem | CNmOverlayBlendTask (layered 1) |
| 18043a550 | animationsystem | masked blend |
| 1804399b0 / 18043a0c0 | animationsystem | additive(lod, base, add, w, out, flag) / masked additive |
| 18043b55a / 18043b573 | animationsystem | CNmAdditiveBlendTask's calls (flag 1) |
| 180442450 | animationsystem | model-space blend(lod, base, layer, w, mask, out = the layer) |
| 1803a5cc0 | animationsystem | sync track GetTime (percentage by value in r8d) |
| 1803a5c00 | animationsystem | GetPercentageThrough |
| 1803a51f0 | animationsystem | the blended sync track |
| 18045aa90 / 18045a6f0 / 18045b220 | animationsystem | CNmParameterizedBlendNode (Blend1D) init / evaluation / update |
| 18044f920 | animationsystem | copy a sync track without its start offset (+0x130 = 0) |
| 180438ee0 / 180439730 | animationsystem | Clip node init / update |
| 180438e40 | animationsystem | Clip GetSyncTrack: an override track at +0x40 when set |
| 180463370 | animationsystem | AnimationPose update |
| 180466d70 | animationsystem | SpeedScale / DurationScale update |
| 180466a70 / 180466990 | animationsystem | SpeedScale / DurationScale scale |
| 1806a5460 | animationsystem | TwoBoneIK vtable |
| 18046bb40 / 18046bf90 | animationsystem | TwoBoneIK init / update |
| 18069e570 / 180458970 | animationsystem | its task / execute |
| 180472d30 | animationsystem | the solve (= client 1812f70c0's routine) |
| 180473980 / 180473400 | animationsystem | blend timer |
| 18046c7c0 | animationsystem | bone target |
| 1803b2c80 / 1803b3090 | animationsystem | LayerBlend update / the layers |
| 18044cf60 / 18044d090 | animationsystem | State update / layer |
| 18044fc40 | animationsystem | transition blend weight (easing switch inlined) |
| 180452e70 | animationsystem | lerps source / target layer weights |
| 180450340 / 180452410 | animationsystem | transition start / update |
| 1803a59d0 | animationsystem | PreferClosestSyncEventID |
| 1803a5b60 | animationsystem | the source event's ID |
| 180464a30 | animationsystem | Selector |
| 180464790 | animationsystem | parameterized clip selector (pick 180465b50 / 1804655c0; shutdown 180466650) |
| 18045cf80 / 18045cac0 | animationsystem | Blend2D init / evaluation |
| 18045c3b0 | animationsystem | Blend2D blend-space search |
| 180446690 | animationsystem | FloatComparison (slot 9) |
| 180447090 | animationsystem | FloatRangeComparison |
| 180448ab0 | animationsystem | IDToFloat |
| 180447960 | animationsystem | FloatSwitch |
| 180447130 | animationsystem | FloatRemap |
| 180447870 / 180447c00 | animationsystem | FloatSpring / init |
| 18049d000 | animationsystem | FloatCurve |
| 180443ac0 / 180443790 | animationsystem | CachedFloat init / update |
| 1804467f0 | animationsystem | CNmFloatEaseNode |
| 180468d80, 180467b10 | animationsystem | state machine update / transition selection (unread) |

Node vtable slots (RTTI `CNm*Node`): 1 IsValid, 8 GetSyncTrack, 9 InitializeInternal, 10 Update(ctx, result, range).

## Fields

| Object | Offsets |
|---|---|
| skeleton | +8 bone count (high LOD), +0x20 parents (int*), +0x60 low LOD count (m_numBonesToSampleAtLowLOD) |
| pose (0x58) | +0 skeleton, +8 count, +0x10 transforms (0x20 each: position xyz, scale, rotation xyzw at +0x10), +0x20 model-space cache count (blends zero it), +0x38 type: 1 parent space, 2 reference, 3 zero, 4 additive (3 and 4 additive), +0x40 / +0x48 float channel sets |
| clip | +0 -> handle -> skeleton, +8 frames, +0xc duration, +0x14 / +0x18 compressed u16 data, +0x28 tracks, +0x40 frame offsets (u32, u16 units), +0xc0 sync track, +0x1c0 additive, +0x1e0 model-space sampling chain (count; no player clip has one, all 975 checked) |
| clip track (0x50) | x / y / z / scale range (start, length) +0..+0x1c, constant rotation +0x30, static flags +0x40 rotation / +0x41 translation / +0x42 scale |
| bone mask | +0 enabled byte, +0x18 weights (float*) |
| sync track | +0 event count, +4 capacity (10 inline), +8 events (0x10: id 8 bytes, start, duration), +0xa8 start event offset |
| task context | +0x6e LOD byte (1: the skeleton's +8 count, every bone) |

## Constants

| Value | What |
|---|---|
| 4.315969e-05 (0x3835065d) | rotation word scale |
| -0.70710677 (0xbf3504f3) | rotation word offset |
| 65535.0f | translation / scale quantisation (divss) |
| 1e-4 | clip frame fraction snap to 0 |
| 6.2831855 | 2π (FloatSpring) |
| 0x3fc90fdb | π/2 (Sine easing) |
| 2^-23 | FloatRemap empty output range |
| 22 | NmEasingOperation_t None |

## Clips

- 180398ef0, per bone: rotation 3 x u16, each `(u & 0x7fff) x 4.315969e-05 - 0.70710677`; the dropped one `sqrt(1 - ((x² + y²) + z²))` (no clamp), placed by the first and second words' top bits (neither: (w, x, y, z); second: (x, w, y, z); first: (x, y, w, z); both: (x, y, z, w)). Translation `u / 65535 x length + start`; scale the same; static channels from the track. The resource stores some track numbers as doubles: CS2 holds floats (648 of 1,082,700 numbers in the player bakes weren't floats).
- 18007bf90: 0 -> frame 0; 1 -> the last frame; else 18038ef40 wraps it, `V_modff((frames - 1) x it)` splits frame and fraction, a fraction within 1e-4 is 0.
- 18039a8f0: a fraction != 0 decodes the next frame (the same one for a fraction <= 0) and blends every bone: the fitted slerp and `t (b - a) + a` on position + scale. Type 4 for an additive clip, else 1.

## Blends

Fitted slerp everywhere (the same polynomial client.dll's Aim IK inlines): dot = dpps `((ax bx + ay by) + (az bz + aw bw))`,
`q = normalise(b k1 + a k0)`, a zero length the identity (180b3efd0).

- 180439d40: w = 0 and src != out copies src first; then `layered or w != 1` blends every bone (position + scale `(b - a) w + a`), else copies tgt; type 4 if both additive, else 1.
- 18043a550: w = 0 copies src, `!layered and w = 1` copies tgt, a disabled mask copies src; per bone `bw = w x weight`: 0 keeps src's, `!layered and 1` takes tgt's, else the blend.
- 1804399b0 / 18043a0c0: rotation fitted-slerped from base to `base x add` (qmul, base first), position + scale `w add + base`. Their `!flag and w = 1` shortcut copies the **additive** pose; CNmAdditiveBlendTask passes flag 1, so it never runs.
- 180442450: model rotations of both (unnormalised products down the parents); per bone by the mask's weight alone: position lerped in parent space, rotation slerped in model space, back to parent space with the hemisphere test; weight 0 copies base's bone. Bone 0's rotation is never written (stays the layer's; its model rotation is still the blended one). Then blend(base -> out, w, layered 0).

## Sync tracks

1803a51f0: L = lcm(n0, n1); each event `d0' = (n0 / L) d0`, `(n1 / L) d1 - d0'` times w plus d0', the id the second's for
w > 0.5, renormalised by 1 / sum, the last event's duration 1 - its start, offset 0. Esoterica's logic, Valve's floats.

## Nodes

- **Blend1D**: parameter clamped into the parameterization range (`min <= v ? (v <= max ? v : max) : min`, NaN -> min); the first blend range holding it; `w = (v - min) / (max - min)` (0 for an empty range); `|w| <= 1e-4` the range's first source alone, `|w - 1| <= 1e-3` the second alone, else both. One source: its sync track copied **without** its start offset (18044f920), its duration; two: the blended track, duration `((L / n1) d1 - (L / n0) d0) w + (L / n0) d0`. No parent range: `start = GetTime(cur)`, `end = GetTime(18038ef40(cur + dt / duration, looping))` (looping wraps to the fraction, no snap to 1). A missing source pose: the zero pose in an additive layer, else the reference.
- **Clip**: duration = clip duration / m_flSpeedMultiplier; the time starts at the clip's own sync track's percentage (no player clip node has a start sync offset or play-in-reverse input); the reset input zeroes both times; one frame: previous 0 on the first update then 1, current 1; else + dt / duration, clamped, or looping its fraction (1 for a whole loop) and the looped flag; with a range: GetPercentageThrough of both ends.
- **AnimationPose**: one frame -> 0; the input (or m_flUserSpecifiedTime) remapped through m_inputTimeRemapRange when set (then clamped), / (frames - 1) with m_bUseFramesAsInput, clamped.
- **SpeedScale / DurationScale**: no range: the child's dt x s (0 for |s| <= 1e-4) and the node's duration = the child's duration **before** its update / s; with a range the child's after. DurationScale's s = child duration / wanted (0 for a wanted <= 1e-4, 1 without a positive child duration).
- **TwoBoneIK**: [c4.md](c4.md) "The C4 viewmodel's arms" (the blend timer, the bone target, the field offsets).
- **LayerBlend**: weight clamped; the input updated when its weight > 0 or it is a state machine layer; dropped at <= 0.001; Overlay / Additive / ModelSpace without a mask -> Overlay.
- **State**: elapsed += dt; a layer state multiplies the layer weight and the root motion weight by its clamped inputs (an off state zeroes both); its bone mask goes on the layer's mask task list.
- **Transition blend weight** (18044fc40): duration 0 -> 1, else the easing of the progress, clamped (maxss 0, minss 1: NaN -> 0). Source and target layer weights lerped by it (180452e70).
- **Selector** (180464a30): picks and initializes one option. Parameterized clip selector (180464790): initializes the parameter and every option (shut down together), drops invalid options with m_bIgnoreInvalidOptions, repeats each by its byte weight, picks `(int) floorf(|v|) % count`.
- **Blend2D**: search 18045c3b0, then tracks and durations as Blend1D's (one source copied without its offset, the third blended at w12).
- **FloatComparison**: `>=` is `!(a < c)`, NearEqual `!(eps < |a - c|)` (a NaN passes); an unknown operator keeps the last result.
- **FloatRemap**: an output range within 2^-23 gives its begin.
- **FloatSpring**: `w = hertz x 6.2831855`, `od = w dt`, `vel = (vel - (pos - target)(od w)) / ((2 zeta + od) od + 1)`, `pos += vel dt`.
- **FloatCurve**: clamped to the domain's y.
- **CachedFloat**: OnExit follows its input while the branch is active, then holds.
- Foot IK is a pass-through in CS2.

## Transitions (180450340 / 180452410)

Option bits, **one above Esoterica's**:

| Bit | Option |
|---|---|
| 2 | ClampDuration |
| 4 | Synchronized |
| 8 | MatchSourceTime |
| 0x10 | MatchSyncEventIndex |
| 0x20 | MatchSyncEventID |
| 0x40 | MatchSyncEventPercentage |
| 0x80 | PreferClosestSyncEventID (1803a59d0, unused by the player) |
| 0x100 / 0x200 | match / offset time in seconds |

- Unsynchronized: duration clamped to `(1 - source cur) source duration`; without MatchSourceTime and |offset| <= 1e-4 the target starts at 0 and updates with dt; else the start is `(float) idx + pct + offset` split by V_modff (idx from the source's sync time with 0x10, or the target track's index of an ID with 0x20: the ID from m_targetSyncIDNodeIdx, else the source event's (1803a5b60); pct with 0x40), or with seconds `clamp((source seconds + offset) / target duration)` through GetTime; the target updates once with dt 0.
- Synchronized: the source's range, the clamp to its remaining sync time, offset floorf, the target at the source range + offset.
- Both: **the starting frame already advances the progress** (`clamp(dt / duration + progress)`); each update advances it the same way (no percentage-covered step); a synchronized end time wraps (18038ef40, looping).
- The reload's switch to the silent reload is MatchSourceTime in seconds (0x108): the target clip at the source clip's seconds, clamped to its length.

## Easing (18044fc40, 1804467f0)

NmEasingOperation_t: Linear, In / Out / InOut x Quad, Cubic, Quart, Quint, Sine, Expo, Circ, None (22, the identity).
Powers multiplied in order; InOut halves at `0.5 > t` (`g(2t) / 2`, `g(2t - 1) / 2 + 1/2`); Sine through tier0's V_cosf
with π/2; Circ through sqrt. Expo calls a tier0 pow (unread; no player graph uses it).

## Unread

- The state machine's update and transition selection (180468d80, 180467b10).
- The rest of the transition update: the source's range shift, the clamped end at progress 1, cached / forced sources, the bone-mask start blend, the non-synchronized time advance.
- ReferencedGraph; the bone mask nodes and the mask task list (states' layer masks).
- Event and state conditions (IDEventCondition, GraphEventCondition, StateCompleted, TimeCondition, CurrentSyncEventID); the sampled-event weights.
- Root motion, taken after Esoterica and not checked against the DLL: a clip's delta inverse(T(prev)) x T(cur) over its rootMotion track (the resource's m_transforms), a loop as the end's delta then the start's, none when the node's m_bSampleRootMotion is off; Blend1D / 2D and transitions lerp position and fitted-slerp rotation by their weight (m_rootMotionBlend "Blend"); a layer blend keeps its base's (m_bOnlySampleBaseRootMotion); states, selectors and passthroughs pass their child's on.
- PreferClosestSyncEventID and Expo easing (unused).
- The pose the Aim IK starts from at 75-89° ([fp-legs.md](fp-legs.md)).
