# CS2's auto exposure (the histogram, CTonemapSystem, the volume's values)

Traced 2026-11-20 (branch agent/mapbake-exposure) from client_20261015, scenesystem_20261015, server_20261105 and
CS2's shaders_vulkan_dir.vpk (VRF 20.1: histogram_cs, post_process). Ported in web/src/world/tonemap-system.js (the
CPU), web/src/world/luminance-meter.js (the GPU), driven by world/tonemap.js. Checked: tonemap-system-test.mjs (cases
worked by hand from the disassembly), the meter against a CPU recomputation of the same frame (relative 3e-8), the
paired shots (docs/MAP_SHOTS.md).

## 1. The pipeline

1. client.dll, every frame (0x180a71710): the view's source of exposure values, in order: its env_tonemap_controller2
   (the handle at +0xa8: C_TonemapController2 0x180272140), else the pawn's active post_processing_volume (pawn
   +0x1328 -> +0x200) when it has m_bExposureControl (0x18029c500, returns 1), else a reset (0x180272390: vfn 0x20 with
   null). Each goes through the post-processing interface `(*0x18254eae8)->vfn 0 ()` (CLoopModeGame +0x10, made by
   0x180a24320; vfn 0 returns +0x60) -> vfn 0x60 (out shared_ptr, slot): the slot's CTonemapSystem.
2. client.dll's post pass 0x1811e88a0 "Histogram Update" -> the pass 0x181212030 (vtable 0x181d2a6d8): clear the bins,
   build (or resolve + build with MSAA under r_csgo_merge_resolve_with_histogram), average, then copy AverageLuminance
   (4 bytes) back to the CPU; the callback 0x181208220 calls the tonemap system's vfn 0x40 with it.
3. scenesystem's CTonemapSystem vfn 0 (0x18018d080) -> 0x18018d440 (time, a double): the adaptation below. Its +0x10
   is the exposure; post_process multiplies the HDR colour by PerViewConstantBuffer_t._m0 (g_flToneMapScalarLinear)
   x PostProcessingConstantBuffer_t._m0 (2^m_flExposureBias). TODO(trace): the per-view filler that copies +0x10 there,
   and the clock passed to vfn 0.

## 2. histogram_cs (game/core, 51 programs; D_HISTOGRAM_MODE 0..2, D_MSAA_SAMPLES, D_TONEMAP_BLEND, D_DITHER_NOISE)

Histogram_t, written by 0x181212030 (0x18 bytes): +0 uint2 the view's size (param_2 +0xc7c), +8 -8.0, +0xc 13.0,
+0x10 1/13 (0x3d9d89d9), +0x14 the pixels per thread side: 3 on an Intel GPU (vendor 0x8086), else 1 (work split
only: every pixel is still counted). The build pass reads +8 / +0x10 (its m2 at c1), the average pass +8 / +0xc (its
m2 at c0.w, the HLSL reflection's packoffset).

- **mode 0 (d0)**, 16 x 16 threads: bin = uint(saturate((log2(max(dot(rgb, (0.2125, 0.7154, 0.0721)), 0.005)) - -8) x
  1/13) x 255); groupshared 256 counters, then imageAtomicAdd into HistogramBins; it also copies the input clamped to
  65504 into Output.
- **mode 2 (d2)**, 256 threads: s[i] = bins[i] x i, a tree sum, then AverageLuminance[0] = exp2(((float(s) /
  max(float(w x h), 1)) x 0.0039215688593685627) x 13 + -8): the geometric mean over the pixels' bins.

The port: the mean of the bins is the mean over the pixels of each pixel's bin, so luminance-meter.js sums the bins
with a 4 x 4 pass and 8 x 8 passes into one R32F texel (exact integers below 2^24) and reads it through a pixel buffer
and a fence.

## 3. CTonemapSystem (scenesystem_20261015, vtable 0x1805f9cc8, 9 slots; made by 0x180183c30, size 0xa0 at +0x10 of a
std::_Ref_count_obj2)

| Offset | What |
|---|---|
| +0x8 | the target (after the clamp and the compensation) |
| +0xc | the current exposure |
| +0x10 | the exposure used (vfn 1 returns it): +0xc, or the blend below |
| +0x14 / +0x18 / +0x1c | a blend weight / its exposure / its start time, set by vfn 0x38 (0x18018d890); after 1 s the weight halves each update, 0 below 0.01; +0x10 = lerp(+0xc, +0x18, w). Nothing we have calls it |
| +0x20 | the ring's count (to 10) |
| +0x24 .. +0x48 | the ring of the last ten raw targets |
| +0x4c | the GPU's average luminance (vfn 0x40 0x18018d0a0 swaps it in; starts 1.0) |
| +0x50 | the last update's time (a double) |
| +0x58 .. +0x6c | defaults: min 0.25, max 8 (then gameinfo Engine2/RenderingPipeline Tonemapping_DefaultAutoExposureMin / Max: CS2's 1.0 / 1.0), compensation 1, speed up 1, speed down 2, smoothing range 100 |
| +0x70 .. +0x84 | the controller's six (vfn 0x20 0x18018d240; null -> -1, -1, 1, -1, -1, 100) |
| +0x88 .. +0x9c | the effective six (0x18018d2a0): each the controller's when >= 0, else the default's, else -1; max raised to min; mat_tonemap_force_min / _max (globals 0x180923560 / 0x180923570) over both, mat_tonemap_uncap_exposure (0x1809235f0) -> 0 .. 100 |

Slots: 0 update (0x18018d080 -> 0x18018d440), 1 +0x10, 2 +0x88, 3 +0x8c, 4 (0x20) set params, 5 (0x28) force
(0x18018d400: v <= 0 -> (min + max) / 2; +0x8 / +0xc / +0x10 = v, +0x14 = 0, the count 0), 6 returns 1.0, 7 (0x38)
the blend, 8 (0x40) the luminance.

**0x18018d440** (floats are movss; the constants read from the DLL: 0x1805ffec8 0.2, 0x1805fff40 1.0, 0x1805ffeec 0.5):
1. dt = float(time - last) (last 0: dt 0); last = time.
2. t = 0.18 / +0x4c; not finite: return.
3. The ring: below 10 entries append, else shift down and put t last. With 10: the weighted mean
   Σ (|i - 5| x 0.2) x r[i] (acc = w x r + acc, i = 0..9), x (1 / the weights' float sum); clamped (min when min > x,
   else minss(max, x)); stored only when finite. Below 10: t clamped, stored.
4. compensation > 0: target x= compensation.
5. speed = speed up; speed up == 0: current = target. Else: current > target -> speed down; lc = log2(current), diff =
   |log2(target) - lc|; range > diff -> speed = min(diff x 0.5, speed); current > target -> -speed; next =
   exp2(speed x max(dt, 0) + lc), then min(next, target) for speed >= 0, max(next, target) below; not finite -> target.
6. mat_tonemap_force_scale (0x1809235e0) > 0, or mat_fullbright 1 (-> 1.0): vfn 0x28 with it.
7. +0x10 = +0xc, then the blend (above).

log2 / exp2 are tier0's V_log2f / V_exp2f; the port uses Math's rounded to float32 (TODO(trace): their last ulp).

## 4. The volume's values (client C_PostProcessingVolume, schema: +0x119c m_flMinLogExposure, +0x11a0
m_flMaxLogExposure, +0x11a4 m_flMinExposure, +0x11a8 m_flMaxExposure, +0x11ac m_flExposureCompensation, +0x11b0
m_flExposureFadeSpeedUp, +0x11b4 m_flExposureFadeSpeedDown, +0x11b8 m_flTonemapEVSmoothingRange, +0x11bc m_bMaster,
+0x11bd m_bExposureControl)

0x18029c040 (becoming active) and 0x18029c500 (each frame) pass { min exposure (<= 0: 2^ min log), max (<= 0: 2^ max
log), 2^ compensation, speed up, speed down, smoothing range }. With the bool 0x1823866c8 set, min = max = the float
0x1823866cc and vfn 0x28 with it (TODO(trace): its cvar; off by default). The client's constructor (0x18029b220)
zeroes them (min / max -1, range 100) until the server's values arrive; the server's (server_20261105 0x18045f0d0,
fields +0x9e0 ..) are the same: a key the map leaves out stays 0 (min / max -1: 2^0 = 1; the range 100). CS2's
csgo/postprocessing.fgd has min / max exposure (default 1.0), enableexposure, speed up / down (1); no baked map sets
compensation, log exposure or the smoothing range. Defaults seen in game/core's fgd: min 0.25, max 8.

C_TonemapController2 (env_tonemap_controller2, 0x180272140): { +0x600 min, +0x604 max, 1.0, +0x608 up, +0x60c down,
+0x610 range } (m_flAutoExposureMin / Max, m_flExposureAdaptationSpeedUp / Down, m_flTonemapEVSmoothingRange). Not
ported: no baked map has one.

## 5. Not read

- Which colour target the histogram reads in the non-MSAA path (ours: the frame the bloom reads, after DoF), and
  whether the viewmodel is in it (ours: yes).
- The readback's latency (CS2 queues one a frame; ours keeps one in flight).
- Whether CLoopModeGame (and so the tonemap state) lives across map changes (ours: reset per map).
