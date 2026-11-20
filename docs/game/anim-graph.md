# CS2's anim graph runtime (NmGraph), traced from animationsystem.dll 2026-10-23

The port: `web/src/world/anim-graph/` (`clip.js` the clips, `pose.js` the blends, `sync-track.js`, `nodes-*.js` the
nodes, `cs-xform.js` the shared quaternion maths). Addresses are `animationsystem_20261023.dll` in the Ghidra project;
its asserts name `src/animlib/` (animpose.cpp, animskeleton.cpp, graph/animgraph_instance.cpp, tasksystem/*).
The runtime is Esoterica's, recompiled by Valve with their own maths (CTransform, the fitted slerp).

**Checked bit for bit against the DLL called natively**: `rubikon/tests/AnimOracle` loads animationsystem_20261023.dll
unresolved, patches tier0's V_modff / V_cosf (IAT 18063f8c0 / 18063f3a8), runs the static initialiser of the identity
quaternion (180001000 -> 180b3efd0, BSS), builds the structures below and calls Valve's functions;
`node web/server/cs2web/combat/anim-test.mjs [n]` writes seeded cases (real player clips from the bakes and synthetic ones, random
poses with zero rotations and every pose type, masks with 0 / 1 / fractions, sync tracks with offsets, every easing)
and compares every float. Result (2026-11-10): **0 differ** on every op (clip decode + sampling over 174 clips; blend,
masked blend, additive, masked additive, model-space blend, GetTime, GetPercentageThrough, the blended track, V_cosf:
400 cases each; the transition blend weight: 20,000 over every easing but Expo; the float curve and Blend2D's
blend-space search: 3,000 each, the latter half over the player's own blend spaces).

## Structures (offsets from the disassembly)

| | |
|---|---|
| skeleton | +8 bone count (high LOD), +0x20 parents (int*), +0x60 the low LOD's count (m_numBonesToSampleAtLowLOD) |
| pose (0x58) | +0 skeleton, +8 count, +0x10 transforms (0x20 each: position xyz, scale, rotation xyzw at +0x10), +0x20 the model-space cache's count (blends zero it), +0x38 type: 1 parent space, 2 reference, 3 zero, 4 additive (3 and 4 are additive), +0x40 / +0x48 float channel sets |
| clip | +0 -> handle -> skeleton, +8 frames, +0xc duration, +0x14 / +0x18 compressed u16 data, +0x28 tracks (0x50: x / y / z / scale range (start, length) +0..+0x1c, constant rotation +0x30, static flags +0x40 rotation / +0x41 translation / +0x42 scale), +0x40 frame offsets (u32, u16 units), +0xc0 the sync track, +0x1c0 additive, +0x1e0 the model-space sampling chain (count; no player clip has one: checked over all 975) |
| bone mask | +0 enabled byte, +0x18 weights (float*) |
| sync track | +0 event count, +4 capacity (10 inline), +8 events (0x10: id 8 bytes, start, duration), +0xa8 the start event offset |

The pose tasks and the parameters a node passes: the LOD byte is the task context's +0x6e (1: the skeleton's +8 count,
every bone; the port computes every bone, or the server's active subset: per-bone results are the same).

## Clips (clip.js)

- 180398ef0 a frame: per bone, rotation 3 x u16: each `(u & 0x7fff) x 4.315969e-05 - 0.70710677` (0x3835065d,
  0xbf3504f3), the dropped one `sqrt(1 - ((x² + y²) + z²))` (no clamp), placed by the first and second words' top bits
  (neither: (w, x, y, z); second: (x, w, y, z); first: (x, y, w, z); both: (x, y, z, w)); translation `u / 65535 x
  length + start` (65535.0f, divss), scale the same; static channels from the track. The resource stores some track
  numbers as doubles: CS2 holds floats (648 of 1,082,700 baked numbers weren't), the port rounds them.
- 18007bf90 the time: the percentage passed **by value in edx**; 0 -> frame 0; 1 -> the last frame; else 18038ef40
  wraps it (V_modff's fraction, a negative one 1 - it), `V_modff((frames - 1) x it)` splits frame and fraction, a
  fraction within 1e-4 is 0.
- 18039a8f0: the frame decoded into the pose; a fraction != 0 decodes the next frame (the same one for a fraction <= 0)
  and blends every bone: the fitted slerp and `t (b - a) + a` on position + scale. Type 4 for an additive clip, else 1.

## Blends (pose.js) and how the tasks call them

The fitted slerp everywhere (cs-xform.js fitK, the same polynomial client.dll's Aim IK inlines): dot = dpps
((ax bx + ay by) + (az bz + aw bw)), `q = normalise(b k1 + a k0)`, a zero length the identity (180b3efd0).

- 180439d40 blend(lod, src, tgt, w, out, layered): w = 0 and src != out copies src first; then `layered or w != 1`
  blends every bone (position + scale `(b - a) w + a`), else copies tgt; type 4 if both additive, else 1.
  CNmBlendTask (18043bb40) passes layered 0, CNmOverlayBlendTask (18043c500) 1.
- 18043a550 masked: w = 0 copies src, `!layered and w = 1` copies tgt, a disabled mask copies src; per bone `bw = w x
  weight`: 0 keeps src's, `!layered and 1` takes tgt's, else the blend.
- 1804399b0 additive(lod, base, add, w, out, flag) / 18043a0c0 masked: rotation fitted-slerped from base to `base x
  add` (qmul, base first), position + scale `w add + base`. Their own `!flag and w = 1` shortcut copies the **additive**
  pose; CNmAdditiveBlendTask passes flag 1 (18043b55a / 18043b573), so it never runs (the port bakes the task's call in).
- 180442450 model space(lod, base, layer, w, mask, out = the layer): model rotations of both (unnormalised products down
  the parents), per bone by the mask's weight alone: position lerped in parent space, rotation slerped in model space,
  back to parent space with the hemisphere test (cs-xform qdiff); weight 0 copies base's bone. Bone 0's rotation is
  never written (it stays the layer's, its model rotation is still the blended one). Then blend(base -> out, w, layered 0).

## Sync tracks (sync-track.js)

1803a5cc0 GetTime (percentage by value in r8d), 1803a5c00 GetPercentageThrough, 1803a51f0 the blended track (L =
lcm(n0, n1); each event `d0' = (n0 / L) d0`, `(n1 / L) d1 - d0'` times w plus d0', the id the second's for w > 0.5,
renormalised by 1 / sum, the last event's duration 1 - its start, offset 0). Esoterica's logic, Valve's floats.

## Nodes

Each node's runtime vtable (RTTI `CNm*Node`): slot 1 IsValid, 8 GetSyncTrack, 9 InitializeInternal, 10
Update(ctx, result, range). Read and ported (no native check: the nodes need a graph instance and its context):

- **Blend1D / CNmParameterizedBlendNode** (init 18045aa90, evaluation 18045a6f0, update 18045b220): the parameter
  clamped into the parameterization range (`min <= v ? (v <= max ? v : max) : min`, NaN -> min), the first blend range
  holding it, `w = (v - min) / (max - min)` (0 for an empty range); `|w| <= 1e-4` the range's first source alone, `|w -
  1| <= 1e-3` the second alone (was 1e-4 here), else both. One source: its sync track copied **without** its start
  offset (18044f920, +0x130 = 0), its duration; two: the blended track, duration `((L / n1) d1 - (L / n0) d0) w + (L /
  n0) d0`. No parent range: `start = GetTime(cur)`, `end = GetTime(18038ef40(cur + dt / duration, looping))` (looping
  wraps to the fraction, no snap to 1). A missing source pose: the zero pose in an additive layer, else the reference.
- **Clip** (init 180438ee0, update 180439730): duration = clip duration / m_flSpeedMultiplier; the time starts at the
  clip's own sync track's percentage (GetSyncTrack 180438e40 returns an override track at +0x40 when set; no player
  clip node has a start sync offset or play-in-reverse input, so neither is ported); the reset input zeroes both
  times; one frame: previous 0 on the first update then 1, current 1; else + dt / duration, clamped, or looping its
  fraction (1 for a whole loop) and the looped flag; with a range: GetPercentageThrough of both ends.
- **AnimationPose** (update 180463370): one frame -> 0; the input (or m_flUserSpecifiedTime) remapped through
  m_inputTimeRemapRange when set (then clamped), / (frames - 1) with m_bUseFramesAsInput, clamped.
- **SpeedScale / DurationScale** (update 180466d70, scales 180466a70 / 180466990): no range: the child's dt x s (0 for
  |s| <= 1e-4) and the node's duration = the child's duration **before** its update / s; with a range the child's after.
  DurationScale's s = child duration / wanted (0 for a wanted <= 1e-4, 1 without a positive child duration).
- **TwoBoneIK** (vtable 1806a5460, init 18046bb40, update 18046bf90; its task 18069e570, execute 180458970, the
  solve 180472d30 = client 1812f70c0's routine): c4.md "The C4 viewmodel's arms" (the blend timer 180473980 /
  180473400, the bone target 18046c7c0, the field offsets). Ported in the viewmodel runtime (weapons/fp/ag2/ik.js).
- **LayerBlend** (update 1803b2c80, the layers 1803b3090): matches the port (weight clamped, the input updated when its
  weight > 0 or it is a state machine layer, dropped at <= 0.001, Overlay / Additive / ModelSpace without a mask ->
  Overlay).
- **State** (update 18044cf60, layer 18044d090): elapsed += dt; a layer state multiplies the layer weight and the root
  motion weight by its clamped inputs (an off state zeroes both); its bone mask goes on the layer's mask task list.
- **Transition blend weight** (18044fc40): duration 0 -> 1, else the easing (below) of the progress, clamped (maxss 0,
  minss 1: NaN -> 0). The layer weights of source and target are lerped by it (180452e70).
- **Transitions** (start 180450340, update 180452410): the option bits are **one above Esoterica's**: & 2
  ClampDuration, & 4 Synchronized, & 8 MatchSourceTime, 0x10 MatchSyncEventIndex, 0x20 MatchSyncEventID, 0x40
  MatchSyncEventPercentage, 0x80 PreferClosestSyncEventID (1803a59d0, unused by the player: not ported), 0x100 / 0x200
  match / offset time in seconds. Unsynchronized: duration clamped to `(1 - source cur) source duration`; without
  MatchSourceTime and |offset| <= 1e-4 the target starts at 0 and updates with dt; else the start is `(float) idx +
  pct + offset` split by V_modff (idx from the source's sync time with 0x10, or the target track's index of an ID with
  0x20: the ID from m_targetSyncIDNodeIdx, else the source event's (1803a5b60); pct with 0x40), or with seconds
  `clamp((source seconds + offset) / target duration)` through GetTime, and the target updates once with dt 0.
  Synchronized: the source's range, the clamp to its remaining sync time, offset floorf, the target at the source
  range + offset. Both: **the starting frame already advances the progress** (`clamp(dt / duration + progress)`); each
  update advances it the same way (no percentage-covered step), a synchronized end time wraps (18038ef40, looping).
  The viewmodel's runtime (web/src/weapons/fp/ag2/eval.js, vpkstuff's previewer) has only the seconds case of
  MatchSourceTime (0x108, the reload's switch to the silent reload: the target clip at the source clip's seconds,
  clamped to its length) besides its target sync ID seek; TODO: the offset, the dt-0 first update (it advances the
  entering clip by the frame's dt), the index / ID / percentage matches.
- **Selectors**: Selector (180464a30) picks and initializes one option; the parameterized clip selector (180464790,
  the pick 180465b50 / 1804655c0) initializes the parameter and every option (shut down together, 180466650), drops
  invalid options with m_bIgnoreInvalidOptions, repeats each by its byte weight, picks `(int) floorf(|v|) % count`.
- **Blend2D** (init 18045cf80, evaluation 18045cac0): the search 18045c3b0 (checked: op 13), then tracks and durations
  as Blend1D's (one source copied without its offset, the third blended at w12).
- **Value nodes** (slot 9 each): FloatComparison 180446690 (`>=` is `!(a < c)`, NearEqual `!(eps < |a - c|)`: a NaN
  passes; an unknown operator keeps the last result), FloatRangeComparison 180447090, IDToFloat 180448ab0, FloatSwitch
  180447960 (as ours), FloatRemap 180447130 (an output range within 2^-23 gives its begin), FloatSpring 180447870
  (`w = hertz x 6.2831855`, `od = w dt`, `vel = (vel - (pos - target)(od w)) / ((2 zeta + od) od + 1)`, `pos += vel
  dt`; init 180447c00), FloatCurve 18049d000 (checked: op 12; clamped to the domain's y), CachedFloat (init 180443ac0,
  180443790: OnExit follows its input while the branch is active, then holds).
- **Easing** (the switch inlined in 18044fc40 and CNmFloatEaseNode 1804467f0; NmEasingOperation_t: Linear, In / Out /
  InOut x Quad, Cubic, Quart, Quint, Sine, Expo, Circ, None): powers multiplied in order, InOut halves at `0.5 > t`
  (`g(2t) / 2`, `g(2t - 1) / 2 + 1/2`), Sine through tier0's V_cosf with pi/2 (0x3fc90fdb), Circ through sqrt; None
  (22) is the identity. Expo calls a tier0 pow: TODO(trace), no player graph uses it.

## The runtime's own rules (2026-11-16: no garbage a frame, root motion)

Performance only: every pose and event is bit-identical to the runtime before (checked over the player, pet, egg and
menu graphs with every parameter driven, 0 differences, and by the anim / aim DLL oracles). Rules for whoever edits a
node:
- **A node's result is its own object, rewritten each update** (nodes-base.js `res(pose, a, b, rmFrom)`, `none(ctx)`,
  `joined(...)` for a blend's events). A parent reads a child's result before that child updates again. A node that
  holds a child's result across another update copies what it needs to locals first: the blends copy their first
  source's pose, range and root motion before the second updates; a transition copies its source's before its target
  updates (a transition to the state it leaves, as an action_reset restart, updates that same node twice in one frame).
- **Ranges** are node-owned too (a blend's / transition's / layer's `_range`, a transition's `_sr`); SyncTrack.time
  takes an `out` object; a State's `eventRange` is written in place (startTransitionOut's caller copies it).
- **Events** come from the context's pool (`ctx.ev(...)`, one shape: anim, id, type, active, ignored, weight, node, sound,
  soundStart): read them before the next update (the pets' controller and sounds do).
- **fitK and qnorm are written out** in pose.js fslerp / lerpBone / lerpBoneAt (same float steps, same order): V8 boxes a
  double passed to or returned from a call it doesn't inline, and these run for every bone of every blend.
- A clip samples straight from its decoded frames at offsets (no subarray views). Result: a pet graph's update went from
  ~4.2 KB to ~0.9 KB of garbage (the rest is V8 boxing at call boundaries).

**Root motion** (root-motion.js), only when the context asks (`ctx.rootMotion`: the server's pets): each result carries
`rm` ([tx, ty, tz, s, qx, qy, qz, qw], identity otherwise). A clip's delta is inverse(T(prev)) x T(cur) over its
rootMotion track (tools/tp-graph.mjs keeps m_transforms), a loop as the end's delta then the start's, none when the node's
m_bSampleRootMotion is off; Blend1D / 2D and transitions lerp position and fitted-slerp rotation by their weight (every
pet transition is m_rootMotionBlend "Blend"); a layer blend keeps its base's (m_bOnlySampleBaseRootMotion); states,
selectors and passthroughs pass their child's on. The graph's root result's delta is `graph.rm`. Esoterica's rules,
not yet checked against animationsystem.dll (TODO(trace)). Measured on the chicken graph: walk 7.3 u/s, run 86.96, a
turn in place exactly its turn_angle.

## Left

- Not yet read against the DLL: the state machine's own update and transition selection (180468d80, 180467b10),
  the rest of the transition update (the source's range shift, the clamped end at progress 1, cached / forced
  sources, the bone-mask start blend, the non-synchronized time advance), ReferencedGraph, the bone mask nodes and
  the mask task list (states' layer masks), the event and state conditions (IDEventCondition, GraphEventCondition,
  StateCompleted, TimeCondition, CurrentSyncEventID), the sampled-event weights, root motion (ported after Esoterica, above), Foot IK (a pass-through in CS2
  too; Snap Weapon is ported: snap-cs.js), PreferClosestSyncEventID and Expo easing (unused).
- The pose the Aim IK starts from at 75-89° (fp-legs.md): with these fixes the standing P90 pose moves under 1e-4 in;
  the hands stay 21-27 units from the eye (hand_R ~21-22, hand_L ~26-27), inside the legs prepass's cone.
