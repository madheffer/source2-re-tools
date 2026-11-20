# Runtime lights ("barn lights"): the GPU record and the shader loop

scenesystem_20261112 / scenesystem_20261015, client_20261112 / client_20261015. csgo_environment's pixel shader
(combo S_SHADER_QUALITY=1, D_BAKED_LIGHTING_FROM_LIGHTMAP=1, static combo 32: the loop at its lines ~1240-1500);
csgo_complex's pixel shader (the BRDF, the cookie branch; the sun at lines ~785-799).

Every runtime light (light_omni2, light_barn, light_rect, light_spot, the sun's direct part when not from the CSM path,
particle lights) is one barn light record in the binner's structured buffer `g_BarnLights` (set 3 binding 31), culled
per tile by `g_CullBits` (binding 30), walked by every lit pixel shader. Stationary lights (directlight 3: "baked
shadows, dynamic light"; ze_resident_evil_3: 249 of 547 light_omni2, 33 of 43 light_barn) add their direct light here,
masked by their channel of the baked shadow lightmap (`direct_light_shadows`, bakedshadowindex 0..3 = R..A); only
their bounce is in the irradiance lightmap.

## Functions

| Address | Module | What |
|---|---|---|
| 0x1800cd8c0 | scenesystem_20261112 | barn light scene object factory: 0x270-byte CSceneObject (vtable stored at 1800cd93d), +0x60 / +0x68 / +0xd8 = -1, +0x264 / +0x26c FLT_MAX (bounds), +0x78 \|= 0x41000, registered as "BarnLight" (0x1805eded0) through 1800e0840 |
| 1800891d3 | scenesystem_20261112 | references "BarnLightObjectDesc" (0x1805e80e8) |
| 0x1801c0ce0 | scenesystem_20261015 | debug draw ("Pos / Range / Falloff / Atten0..2 / Color") |
| 0x1801c11a0 | scenesystem_20261015 | shape outline draw |
| 1804a9b00 | scenesystem_20261015 | cone / frustum draw |
| 0x1801b4530 -> 0x1801b2450 | scenesystem_20261015 | CLightBinnerGPU slot 5: uploads the frame's records |
| 0x1801b14a0 -> 0x1801b14b0 | scenesystem_20261015 | slot 14 (0x70): packs one 0x1e0-byte record (entry, record) |
| 0x1804a65f0 | scenesystem_20261015 | (desc, out, light -> camera-relative transform) |
| 0x180036990 / 0x1801c1e50 | scenesystem_20261015 | CBarnLightObjectDesc / ...GPU slot 6 (a resource check) |
| 0x180d7da70 | client_20261015 | C_BarnLight constructor |
| 0x180d81100 | client_20261015 | builds the 0x12c-byte desc |
| 1817658a0 | client_20261015 | projection(size, range, shear) |
| 181747070 | client_20261015 | matrix inverse |
| 181747920 | client_20261015 | axis matrix |
| 181763bf0 | client_20261015 | a plane from the inverse |
| 181764b10 | client_20261015 | apex(size, range, shear) |
| 1801587b0 | client_20261015 | clamp |
| 181765700 | client_20261015 | shape term |
| 181765730 | client_20261015 | near / far fade scales (skirt_near, skirt, size, range) |
| 181765820 | client_20261015 | (apex, 100) |
| 181763ff0 / 1817627f0 | client_20261015 | (1, 0) / (1, 0, 0) |
| 181764c90 | client_20261015 | luminaire: tan(size / 2) x (sqrt(w) + 100) with the anisotropy |
| 1817642b0 / 181764480 | client_20261015 | luminaire shape 1 / 2 |
| 180d87da0 | client_20261015 | vfn 0x7f0: the colour |
| 18174a050 | client_20261015 | sRGB -> linear |
| 180d80610 | client_20261015 | colour temperature |

Not the packer (checked): 0x1801a5c00 (the view's lighting setup: CSM cascades 180496ef0), 0x1801b55a0 (shadow atlas
debugger UI), 0x1801c1e50.

## Fields

### The shader record (`_200`, row_major, std430, 0x1e0 bytes)

| Field | Type | Read as |
|---|---|---|
| _m0 | mat4 | world -> projection: p' = _m0 x (pos, 1), p'.xyz / p'.w; inside when x, y in (-1, 1), z in (0, 1) |
| _m2 | vec4 | xyz position (w != 0) or direction to it (w == 0: directional); w the near radius² (`I x w / max(d^2, w)`) |
| _m3 | vec4 | x, y distance fade smoothstep(0, 1, x + y d); z > 0 near fade smoothstep(0, 1, z' x z); w > 0 far fade smoothstep(0, 1, (1 - z') x w) |
| _m4 | vec4 | xyz colour (x intensity, linear); w: 0 no cookie (shape term), < 0 cube cookie slice -w (_m5's quaternion turns the direction into lat-long UVs), > 0 2D cookie slice w (the projected xy), in PerViewLighting._m29's 3D texture |
| _m5 | vec4 | orientation quaternion (x, y, z, w); forward = (1 - 2(y^2 + z^2), 2(xy + wz), 2(xz - wy)), dotted with the direction to the luminaire's closest point (area lights) |
| _m6 | vec4 | x, y facing term saturate(x + y x dot(forward, dir)); z half the luminaire's length (segment p +- forward x z) |
| _m8 | vec4 | shadow atlas rect (xy offset, zw scale); z > 0 gates the dynamic shadow |
| _m9 | vec4 | shape (_m4.w == 0): z == 0 rectangle smoothstep(1, x, \|p'.x\|) x smoothstep(1, y, \|p'.y\|) (x, y = 1 - softness); z != 0 superellipse of exponent 2 / z (roundness) with the same softness; with a cookie: UV offset xy, scale zw |
| _m10 | vec4 | baked shadow channel mask: colour x (1 - dot(texel, _m10)) (one-hot) |
| _m11 | float | min roughness as the BRDF reads it (`r = max(rough.x, _m11)`; the packer's 0x100); its other combos' uses unread |
| _m12 | float | dynamic shadow strength: mix(1, shadow, _m12) |
| _m13 | uint | flags: 4 = shadow map xy swapped (p'.yx x (1, -1)) |
| _m15 | mat4x3 | clip box (world -> [-1, 1]^3): outside, nothing |
| _m16.w | float | the sun's min roughness (taken as max(0.04, light_environment's minroughness)) |

_m1, _m7, _m14, _m16.._m23: read by other combos (specular, fog, translucency): unread.

### The packed record (0x1801b14b0; entry 0x640 bytes, list at binner + 0xe3b0; desc at entry + 0x18)

| Offset | From |
|---|---|
| 0x00 | out + 0x00 (projection) |
| 0x40 | out + 0x40 x a bias matrix |
| 0x80 | out + 0x90 (apex / direction, w) |
| 0x90 / 0x94 | out + 0xc8 / 0xcc (distance fade) |
| 0x98 / 0x9c | out + 0xac / 0xb0 (near / far fade) |
| 0xa0..0xa8 | out + 0xb4..0xbc colour x entry + 0x1b8 x (entry + 0x1c0 or + 0x1c4) |
| 0xac | cookie slice (i + 0.5) / n, negated for a cube |
| 0xb0..0xcb | out + 0xd0.. (quaternion, facing term) |
| 0xcc | out + 0xec (light type 1..5) |
| 0xd0 | entry + 0x174.. (shadow atlas rect) |
| 0xe0 | out + 0xa0 / 0xa4 / 0xa8 (shape; (0, 0, 1, 1) with a cookie) |
| 0xf0 | one-hot table 0x1805fe770 by bakedshadowindex (entry + 0x1ea: -1 none, 0..3 R..A) |
| 0x100 | max(0.04, entry + 0x210) (min roughness) |
| 0x104 | entry + 0x1e0 / 0x1e4 (shadow strength) |
| 0x108 | flags (1, 2, 4, 8 has a baked channel, 0x10, << 16 entry + 0x1fc) |
| 0x10c / 0x1a0 | cookie texture / its matrix |
| 0x110 | clip box (entry + 0x214 & 0x100) |
| 0x140..0x18c | bounding sphere (centre, radius >= 0.25, 1 / radius) |

Then the array goes to the structured buffer (render context vfn 0x380).

### The scene object (scenesystem_20261015, from its debug draws)

+0xe0 type (3 cone / frustum, 4 rectangle), +0xe4..+0xec colour, +0xfc range, +0x100 falloff, +0x104 / +0x108 / +0x10c
attenuation 0 / 1 / 2, +0x164 / +0x168 rectangle width / height (x 0.5), +0x16c a second range (> 0: drawn twice),
+0x178..+0x180 position, +0x184 / +0x190 right / up axes, +0x1b0 flags (0x20 drawn dim, 0x100 has a clip box), +0x1d0 /
+0x1e0 / +0x1ec clip box (origin, orientation, extents).

### C_BarnLight (client_20261015, vtable 0x181cb1408)

m_bEnabled 0x1098, m_nColorMode 0x109c, m_Color 0x10a0, m_flColorTemperature 0x10a4, m_flBrightness 0x10a8,
m_flBrightnessScale 0x10ac, m_nBakedShadowIndex 0x10b4, m_nLuminaireShape 0x10c0, m_flLuminaireSize 0x10c4,
m_flLuminaireAnisotropy 0x10c8, m_hLightCookie 0x1188, m_flShape 0x1190, m_flSoftX / Y 0x1194 / 0x1198, m_flSkirt
0x119c, m_flSkirtNear 0x11a0, m_vSizeParams 0x11a4, m_flRange 0x11b0, m_vShear 0x11b4, m_flMinRoughness 0x11ec,
m_flFadeSizeStart / End 0x1210 / 0x1214, bounds / OBBs 0x1224.., light style +0x13a0.

### The desc (0x180d81100, 0x12c bytes)

| Offset | Value |
|---|---|
| +0x00 | 1817658a0(size, range, shear) |
| +0x40 | its inverse (181747070) |
| +0x80 | 181763bf0 (a plane) |
| +0x90 | 181764b10(size, range, shear) (apex) |
| +0xa0 / +0xa4 | clamp(1 - soft_x / soft_y, 0, 0.9999999) |
| +0xa8 | 181765700(shape) |
| +0xac / +0xb0 | 181765730(skirt_near, skirt, size, range) |
| +0xb4 | 180d87da0 x 181765820(+0x90, 100) |
| +0xc0 | 1 / area (shape 1) or pi / (4 x w x h) (shape 2) |
| +0xc4 | cookie |
| +0xc8 | (1, 0) |
| +0xd0 | (0, 0, 0, 1) |
| +0xe0 | (1, 0, 0) |
| +0xf0.. | shape 1's corners |

Other: light_environment is C_LightEnvironmentEntity (C_LightEntity: CLightComponent vtable 0x181acef90, m_Color 0x78,
m_flBrightness 0x80, m_flBrightnessScale 0x84, m_flBrightnessMult 0x88): not this path.

## Constants

| Value | What |
|---|---|
| set 3 binding 31 / 30 | g_BarnLights / g_CullBits |
| 0x1805fe688 | CLightBinnerGPU vtable |
| 0x1805e8248 / 0x1805fe140 | CBarnLightObjectDesc / CBarnLightObjectDescGPU vtables (differ in slot 6 only) |
| 0x1805fd3c0 | "CBarnLightObjectDescGpu" |
| 0x1805fb2d0 / 0x1805ef370 | lightbinner_gpu.cpp / "SceneSystem/GpuLightBinner" (scenesystem_20261112) |
| 0x181ca8be0 / 0x181ca8bf0 | "light_barn" / "C_BarnLight" (client_20261112) |
| 0x181ca8cd8.. | CBarnLight_API script methods |
| 0x181ac6f30 / 0x181aca080 | m_nBakedShadowIndex / "bakedshadowindex" |
| 0.04 | g_flReflectance = ((1.5-1)/(1.5+1))^2; min roughness floor |
| 512 | VTexFlags.CREATE_LINEAR_API_TEXTURE (without it: an sRGB API texture) |

## The loop (per light in the pixel's tile and depth slice)

```
p' = (_m0 * vec4(pos, 1)); p' /= p'.w
if !(p' in (-1,-1,0)..(1,1,1)) or |(_m15 * vec4(pos,1))| > 1: skip
fwd = quat_forward(_m5); seg = fwd * _m6.z
near = _m3.z > 0 ? smoothstep(0, 1, p'.z * _m3.z) : 1
far  = _m3.w > 0 ? near * smoothstep(0, 1, (1 - p'.z) * _m3.w) : near
if _m2.w != 0:                                  // a point / area light
  L = _m2.xyz - pos; d2 = dot(L, L); d = sqrt(d2)
  c = closest point to pos on the segment [L - seg, L + seg]
  dir = L / d
  atten = far * (_m2.w / max(d2, _m2.w)) * smoothstep(0, 1, _m3.x + _m3.y * d)
          * saturate(_m6.x + _m6.y * dot(fwd_side(_m5), normalize(c)))
else: dir = _m2.xyz; atten = far
col = _m4.xyz * (1 - dot(bakedShadow, _m10)) * atten
col *= _m4.w == 0 ? shape(_m9, p'.xy) : cookie(...)
col *= mix(1, dynamicShadow, _m12)               // when _m8.z > 0 and not a no-shadow case
```

## The cookie branch

```
if _m4.w == 0: col *= shape(_m9, p'.xy)
elif _m4.w < 0:                       // cube cookie, slice -_m4.w
  d = direction to the light (_m2.xyz or L) turned by the inverse of _m5
  uv = (atan(d.y, -d.x) / 2pi, acos(d.z) / pi) * _m9.zw + _m9.xy
  col *= textureLod(_m29 3D texture, (uv, -_m4.w), 0).rgb   // g_sTrilinearWrap
else:                                 // 2D cookie, slice _m4.w
  uv = (p'.xy * (0.5, -0.5) + 0.5) * _m9.zw + _m9.xy
  col *= textureLod(_m29 3D texture, (uv, _m4.w), 0).rgb    // g_sCookieSampler
```

_m4.w = (i + 0.5) / n: slice i's centre (z filtering reads slice i alone). Stock cookies: BGRA8888 512^2 single-mip
vtexs (flags 8, NO_LOD) in pak01 materials/effects/lightcookies/; none has CREATE_LINEAR_API_TEXTURE, so they are sRGB.
Against CS2 frames (de_vertigo s6's lamp): read linear the patch's tail sits at ~0.61 of its middle against CS2's 0.25;
read as sRGB the profile follows CS2's within ~3-10 % (a uniform offset).

## The BRDF (csgo_complex)

The sun's lines are the same with its direction, colour x visibility and _m16.w for _m11.

```
NL = max(0, dot(N, L))                       // N: the shading normal (_16230)
r  = max(rough.x, _m11)                      // rough: _11004 = max(material's, pow(saturate(max(|ddx n|^2, |ddy n|^2)), 0.333))
V  = -normalize(pos - eye); H = normalize(L + V)
a  = r * r;  D' = a / ((N.H)^2 (a^2 - 1) + 1)  // pi x GGX's D
k  = (r + 1)^2 / 8
F  = F0 + (1 - F0) pow(max(1e-6, 1 - max(0, L.H)), 5)   // F0 = mix(0.04, albedo, metalness)
spec += F x D'^2 / (4 (NL (1 - k) + k)(max(0, N.V) (1 - k) + k)) x NL x colour
diff += NL x colour
```

After the loop: diffuse = `(diff + indirect x (1 - E) x AO) x albedo x (1 - metalness)` (no 1 / pi; direct diffuse takes
no AO); specular += `spec x (1 + F0 x 0.125 ((rx + ry)^2)^2 x saturate(N.V)) x _13436` (material AO texture's x times
the screen-space AO, 1 without it).

## The desc's math (client_20261015)

- 1817658a0: axes (light x forward, y left, z up) X = -y, Y = z, Z = x; shear `X += k shear.x Z`, `Y -= k shear.y Z` (k =
  max(1 / range, |size.z| x 2^-23)); X / size.x, Y / size.y, `z' = (size.z + k) Z`, `w = size.z Z + 1` (VMatrix
  products, column vectors).
- 181765730(n0, s, size, range): n = clamp(n0) range, f = clamp(1 - s) range, k = 1 / range + size.z; `a = clamp(k n /
  (n size.z + 1))`, `b = clamp(1 - k f / (f size.z + 1))`; -> (a > 0 ? 1 / a : 0, b > 0 ? 1 / b : 0).
- 181764b10: size.z > 0: apex (-1 / size.z) x (1, shear.x / range, shear.y / range), w = its length^2; else
  -normalize(1, shear.x / range, shear.y / range), w = 0 (a directional barn).
- 181765820(apex, 100): w > 0 ? (sqrt(w) + 100)^2 / w : 1.
- 181765700(shape): shape > 0 ? clamp(shape) x 0.875 + 0.125 : 0.
- Luminaire: shape 1 1817642b0 (type 2), shape 2 181764480 (type 1, a rectangle).
- 180d87da0: 0 when disabled; colormode 0: sRGB -> linear (18174a050), else colour temperature (180d80610); x
  2^m_flBrightness (V_exp2f) x m_flBrightnessScale; x the light style's value and colour (+0x13a0).

## Unread

- The rest of the record (_m1, _m7, _m14, _m16.._m23).
- The GPU binner proper (lightbinner_gpu.cpp): next 0x1800e1fc0 (the desc -> object copy, near the factory), 0x1801b2850
  / 0x1801bf6f0 / 0x1801bf9e0 (its asserts), the writer of the 0x1e0-byte record (scenesystem_20261112).
- The keyvalues -> desc conversion (brightness units, colour temperature, size_params, soft_x / soft_y, skirt /
  skirt_near, shear, shape, luminaire_*, range, cookie); C_OmniLight's desc.
- How scenesystem builds the cookie texture (_m29 is a bindless index: size, format, sRGB), g_sCookieSampler's filter /
  wrap.
- The per-view scales (entry + 0x1b8 / 0x1c0); light_environment's colour function (no V_exp2f caller reads its
  fields); the sun's _m16.w fill.
