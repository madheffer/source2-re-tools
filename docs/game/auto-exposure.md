# Auto exposure (the histogram, CTonemapSystem, the volume's values)

client_20261015, scenesystem_20261015, server_20261105, CS2's shaders_vulkan_dir.vpk (VRF 20.1: histogram_cs, post_process). csgo/postprocessing.fgd, game/core's fgd.

## Functions

| Address | Module | What |
|---|---|---|
| 0x180a71710 | client | every frame: the view's exposure source (tonemap controller, else the post volume, else reset) |
| 0x180272140 | client | C_TonemapController2 (env_tonemap_controller2): passes its six |
| 0x18029c500 | client | post_processing_volume each frame (returns 1 with m_bExposureControl) |
| 0x18029c040 | client | post_processing_volume becoming active |
| 0x180272390 | client | reset: vfn 0x20 with null |
| 0x180a24320 | client | makes the post-processing interface (CLoopModeGame +0x10; vfn 0 returns +0x60) |
| 0x1811e88a0 | client | post pass "Histogram Update" |
| 0x181212030 | client | the histogram pass (vtable 0x181d2a6d8): clear, build (or resolve + build with MSAA), average, copy AverageLuminance (4 bytes) to the CPU |
| 0x181208220 | client | readback callback: tonemap system vfn 0x40 with it |
| 0x18029b220 | client | C_PostProcessingVolume constructor (min / max -1, range 100, rest 0) |
| 0x18045f0d0 | server | the server's post volume (fields +0x9e0 ..), same values |
| 0x180183c30 | scenesystem | makes CTonemapSystem (size 0xa0, at +0x10 of a std::_Ref_count_obj2) |
| 0x18018d080 | scenesystem | CTonemapSystem vfn 0 update -> 0x18018d440 (time, a double) |
| 0x18018d440 | scenesystem | the adaptation |
| 0x18018d0a0 | scenesystem | vfn 0x40: swap in the GPU's luminance |
| 0x18018d240 | scenesystem | vfn 0x20: set the controller's six |
| 0x18018d2a0 | scenesystem | the effective six |
| 0x18018d400 | scenesystem | vfn 0x28 force |
| 0x18018d890 | scenesystem | vfn 0x38 blend |

## Fields

| Offset | Field |
|---|---|
| view +0xa8 | env_tonemap_controller2 handle |
| pawn +0x1328 -> +0x200 | the active post_processing_volume |
| *0x18254eae8 | post-processing interface; vfn 0 (), then vfn 0x60 (out shared_ptr, slot): the slot's CTonemapSystem |
| param_2 +0xc7c | the view's size (to Histogram_t +0) |
| C_PostProcessingVolume +0x119c / +0x11a0 | m_flMinLogExposure / m_flMaxLogExposure |
| +0x11a4 / +0x11a8 | m_flMinExposure / m_flMaxExposure |
| +0x11ac | m_flExposureCompensation |
| +0x11b0 / +0x11b4 | m_flExposureFadeSpeedUp / m_flExposureFadeSpeedDown |
| +0x11b8 | m_flTonemapEVSmoothingRange |
| +0x11bc / +0x11bd | m_bMaster / m_bExposureControl |
| C_TonemapController2 +0x600 / +0x604 | m_flAutoExposureMin / Max |
| +0x608 / +0x60c | m_flExposureAdaptationSpeedUp / Down |
| +0x610 | m_flTonemapEVSmoothingRange |

### CTonemapSystem (vtable 0x1805f9cc8, 9 slots)

| Offset | What |
|---|---|
| +0x8 | the target (after clamp and compensation) |
| +0xc | the current exposure |
| +0x10 | the exposure used (vfn 1): +0xc, or the blend |
| +0x14 / +0x18 / +0x1c | blend weight / its exposure / its start time (vfn 0x38); after 1 s the weight halves each update, 0 below 0.01; +0x10 = lerp(+0xc, +0x18, w) |
| +0x20 | the ring's count (to 10) |
| +0x24 .. +0x48 | ring of the last ten raw targets |
| +0x4c | the GPU's average luminance (starts 1.0) |
| +0x50 | last update's time (double) |
| +0x58 .. +0x6c | defaults: min 0.25, max 8 (then gameinfo Engine2/RenderingPipeline Tonemapping_DefaultAutoExposureMin / Max: CS2's 1.0 / 1.0), compensation 1, speed up 1, speed down 2, smoothing range 100 |
| +0x70 .. +0x84 | the controller's six (null -> -1, -1, 1, -1, -1, 100) |
| +0x88 .. +0x9c | effective six: each the controller's when >= 0, else the default's, else -1; max raised to min; mat_tonemap_force_min / _max (globals 0x180923560 / 0x180923570) over both; mat_tonemap_uncap_exposure (0x1809235f0) -> 0 .. 100 |

| Slot | What |
|---|---|
| 0 | update (0x18018d080 -> 0x18018d440) |
| 1 | returns +0x10 |
| 2 / 3 | +0x88 / +0x8c |
| 4 (0x20) | set params |
| 5 (0x28) | force: v <= 0 -> (min + max) / 2; +0x8 / +0xc / +0x10 = v, +0x14 = 0, count 0 |
| 6 | returns 1.0 |
| 7 (0x38) | blend |
| 8 (0x40) | luminance |

### Histogram_t (0x18 bytes, written by 0x181212030)

| Offset | Value |
|---|---|
| +0 | uint2 the view's size |
| +8 | -8.0 |
| +0xc | 13.0 |
| +0x10 | 1/13 (0x3d9d89d9) |
| +0x14 | pixels per thread side: 3 on Intel (vendor 0x8086), else 1 (work split only) |

The build pass reads +8 / +0x10 (its m2 at c1), the average pass +8 / +0xc (m2 at c0.w; HLSL reflection packoffset).

## Constants

| Value | What |
|---|---|
| 0x1805ffec8 0.2, 0x1805fff40 1.0, 0x1805ffeec 0.5 | 0x18018d440's constants |
| 0.18 | target key |
| mat_tonemap_force_scale | 0x1809235e0 |
| 0x1823866c8 (bool) / 0x1823866cc (float) | forces min = max (cvar unread; off by default) |
| (0.2125, 0.7154, 0.0721) | histogram luma weights |
| 0.005, 65504 | luma floor, output clamp |
| 0.0039215688593685627 | 1 / 255 in the average |

## Pipeline

1. 0x180a71710: env_tonemap_controller2, else the pawn's active post_processing_volume with m_bExposureControl, else reset; through the interface to the slot's CTonemapSystem.
2. "Histogram Update" -> 0x181212030 (MSAA: resolve + build under r_csgo_merge_resolve_with_histogram) -> readback -> vfn 0x40.
3. vfn 0 -> 0x18018d440. +0x10 is the exposure: post_process multiplies HDR colour by PerViewConstantBuffer_t._m0 (g_flToneMapScalarLinear) x PostProcessingConstantBuffer_t._m0 (2^m_flExposureBias).

## histogram_cs

game/core, 51 programs; D_HISTOGRAM_MODE 0..2, D_MSAA_SAMPLES, D_TONEMAP_BLEND, D_DITHER_NOISE.

- Mode 0 (d0), 16 x 16 threads: `bin = uint(saturate((log2(max(dot(rgb, (0.2125, 0.7154, 0.0721)), 0.005)) - -8) x 1/13) x 255)`; groupshared 256 counters, then imageAtomicAdd into HistogramBins; copies the input clamped to 65504 into Output.
- Mode 2 (d2), 256 threads: `s[i] = bins[i] x i`, tree sum, `AverageLuminance[0] = exp2(((float(s) / max(float(w x h), 1)) x 0.0039215688593685627) x 13 + -8)`: the geometric mean over the pixels' bins.

## The adaptation (0x18018d440)

Floats are movss.

1. `dt = float(time - last)` (last 0: dt 0); last = time.
2. `t = 0.18 / +0x4c`; not finite: return.
3. Ring: below 10 append, else shift down and put t last. With 10: weighted mean `Σ (|i - 5| x 0.2) x r[i]` (`acc = w x r + acc`, i = 0..9), x (1 / the weights' float sum); clamped (min when min > x, else minss(max, x)); stored only when finite. Below 10: t clamped, stored.
4. compensation > 0: target x= compensation.
5. speed = speed up; speed up == 0: current = target. Else: current > target -> speed down; `lc = log2(current)`, `diff = |log2(target) - lc|`; range > diff -> `speed = min(diff x 0.5, speed)`; current > target -> -speed; `next = exp2(speed x max(dt, 0) + lc)`, then min(next, target) for speed >= 0, max(next, target) below; not finite -> target.
6. mat_tonemap_force_scale > 0, or mat_fullbright 1 (-> 1.0): vfn 0x28 with it.
7. +0x10 = +0xc, then the blend.

log2 / exp2 are tier0's V_log2f / V_exp2f.

## The volume's values

- 0x18029c040 / 0x18029c500 pass { min exposure (<= 0: 2^ min log), max (<= 0: 2^ max log), 2^ compensation, speed up, speed down, smoothing range }. With 0x1823866c8 set: min = max = 0x1823866cc and vfn 0x28 with it.
- A key the map leaves out stays 0 (min / max -1: 2^0 = 1; range 100).
- C_TonemapController2 passes { +0x600 min, +0x604 max, 1.0, +0x608 up, +0x60c down, +0x610 range }.
- csgo/postprocessing.fgd: min / max exposure (default 1.0), enableexposure, speed up / down (1); no map baked here sets compensation, log exposure or the smoothing range, and none has an env_tonemap_controller2. game/core's fgd: min 0.25, max 8.

## Unread

- The per-view filler that copies +0x10 into the constant buffer; the clock passed to vfn 0.
- V_log2f / V_exp2f's last ulp.
- 0x1823866c8's cvar.
- Which colour target the histogram reads in the non-MSAA path, and whether the viewmodel is in it.
- The readback's latency (CS2 queues one a frame).
- Whether CLoopModeGame (the tonemap state) lives across map changes.
