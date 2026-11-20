# CS2's runtime lights ("barn lights"): the GPU record and the shader loop

Every runtime light CS2 draws (light_omni2, light_barn, light_rect, light_spot, the sun's direct part when it isn't
from the CSM path, particle lights) is one **barn light** record in the light binner's structured buffer
`g_BarnLights` (set 3 binding 31), culled per tile by `g_CullBits` (binding 30) and walked by every lit pixel shader.
Stationary lights (directlight 3: "baked shadows, dynamic light", 249 of ze_resident_evil_3's 547 light_omni2 and 33
of its 43 light_barn) add their direct light here, masked by their channel of the baked shadow lightmap
(`direct_light_shadows`, bakedshadowindex 0..3 = R..A): only their bounce is in the irradiance lightmap. A map lit by
stationary barns (RE3's roof windows) with no barn lights is lit by its bounce alone (2026-11-18: our RE3 spawn).

Sources: csgo_environment's pixel shader (lasers-bake --shader-src csgo_environment --glsl --combo
S_SHADER_QUALITY=1,D_BAKED_LIGHTING_FROM_LIGHTMAP=1, static combo 32: the loop at its lines ~1240-1500);
scenesystem_20261112.dll, client_20261112.dll (source2-compiler tools/re/binaries).

## The record (shader view, `_200`, row_major, std430)

| field | type | read as |
|---|---|---|
| _m0 | mat4 | world -> the light's projection: p' = _m0 x (pos, 1), then p'.xyz / p'.w; inside when x, y in (-1, 1) and z in (0, 1) |
| _m2 | vec4 | xyz: the light's position (w != 0) or direction (w == 0: a directional light, xyz the direction to it); w: the near radius squared (the 1 / max(d^2, w) falloff: I x w / max(d^2, w)) |
| _m3 | vec4 | x, y: distance fade smoothstep(0, 1, x + y d); z > 0: near fade smoothstep(0, 1, z' x z) on the projected depth z'; w > 0: far fade smoothstep(0, 1, (1 - z') x w) |
| _m4 | vec4 | xyz: colour (x intensity, linear); w: 0 = no cookie (the shape term below), < 0 = a cube cookie slice -w (the light's orientation quaternion in _m5 turns the direction into lat-long UVs), > 0 = a 2D cookie slice w (the projected xy) in PerViewLighting._m29's 3D texture |
| _m5 | vec4 | the light's orientation quaternion (x, y, z, w): its forward axis (1 - 2(y^2 + z^2), 2(xy + wz), 2(xz - wy)) dots the direction to the luminaire's closest point (area lights) |
| _m6 | vec4 | x, y: the "facing" term saturate(x + y x dot(forward, dir)); z: half the luminaire's length along its forward axis (the line light: the closest point on the segment p +- forward x z) |
| _m8 | vec4 | the shadow atlas rect (xy offset, zw scale) of a shadowed light; z > 0 gates the dynamic shadow lookup |
| _m9 | vec4 | the shape term when _m4.w == 0: z == 0 rectangle: smoothstep(1, x, |p'.x|) x smoothstep(1, y, |p'.y|) (x, y: 1 - softness); z != 0 a superellipse of exponent 2 / z (roundness) with the same softness; with a cookie: xy offset, zw scale of the cookie's UVs |
| _m10 | vec4 | the baked shadow channel mask: colour x (1 - dot(baked shadow texel, _m10)) (a stationary light's bakedshadowindex: one-hot) |
| _m12 | float | dynamic shadow strength: mix(1, shadow, _m12) |
| _m13 | uint | flags: 4 = the shadow map's xy swapped (p'.yx x (1, -1)) |
| _m15 | mat4x3 | a second box (world -> [-1, 1]^3): outside it the light adds nothing (the light's bounds / clip box) |

The rest of the struct (_m1, _m7, _m11, _m14, _m16.._m23) is read by other combos (specular, fog, translucency):
UNREAD.

## The loop (per light hit by the pixel's tile and depth slice)

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
col *= mix(1, dynamicShadow, _m12)               // when _m8.z > 0 and the pixel isn't in a no-shadow case
```
(then the BRDF with the pixel's normal, roughness, specular: the shader's own lighting, world/lighting.js's.)

## scenesystem_20261112.dll

- 0x1800cd8c0: the barn light scene object's factory: a 0x270-byte CSceneObject (vtable stored at 1800cd93d), its
  +0x60 / +0x68 / +0xd8 indices -1, +0x264 / +0x26c FLT_MAX (the bounds), flags +0x78 |= 0x41000, registered under
  "BarnLight" (string 0x1805eded0) through 1800e0840.
- 0x1805e80e8 "BarnLightObjectDesc" (ref 1800891d3): the desc the client fills.
- The GPU binner: lightbinner_gpu.cpp (0x1805fb2d0), "SceneSystem/GpuLightBinner" (0x1805ef370): where the desc
  becomes the record above. UNREAD.

scenesystem_20261015.dll (in the Ghidra project; same strings at other addresses):
- CBarnLightObjectDesc vtable 0x1805e8248, CBarnLightObjectDescGPU vtable 0x1805fe140 (they differ in slot 6 only:
  0x180036990 vs 0x1801c1e50, a resource check, not the packing); "CBarnLightObjectDescGpu" 0x1805fd3c0.
- The barn light scene object's fields, from its debug draws 0x1801c0ce0 ("Pos / Range / Falloff / Atten0..2 /
  Color") and 0x1801c11a0 (the shape outlines): +0xe0 type (3: a cone / frustum drawn by 1804a9b00, 4: a rectangle),
  +0xe4..+0xec colour, +0xfc range, +0x100 falloff, +0x104 / +0x108 / +0x10c attenuation 0 / 1 / 2, +0x164 / +0x168
  the rectangle's width / height (x 0.5), +0x16c a second range (> 0: the light draws twice), +0x178..+0x180
  position, +0x184 / +0x190 its right / up axes, +0x1b0 flags (0x20: drawn dim, 0x100: has a clip box), +0x1d0 /
  +0x1e0 / +0x1ec the clip box (origin, orientation, extents).
- Not the packer (checked): 0x1801a5c00 (the view's lighting setup: the CSM cascades 180496ef0), 0x1801b55a0 (the
  shadow atlas debugger UI), 0x1801c1e50. Next to read: 0x1800e1fc0 (reads every field above: the desc -> object
  copy, near the factory), 0x1801b2850 / 0x1801bf6f0 / 0x1801bf9e0 (lightbinner_gpu.cpp's asserts), and the writer
  of a 0x1e0-byte record (the shader struct's size).

## client_20261112.dll

- "light_barn" 0x181ca8be0, "C_BarnLight" 0x181ca8bf0, CBarnLight_API's script methods (0x181ca8cd8..), the
  m_nBakedShadowIndex field 0x181ac6f30 / "bakedshadowindex" 0x181aca080. The keyvalues -> BarnLightObjectDesc
  conversion (brightness units, colour temperature, size_params, soft_x / soft_y, skirt / skirt_near, shear, shape,
  luminaire_*, range, cookie) is UNREAD; world/maplights.js has light_omni2's from source2-compiler (the compiler's
  side of the same units).

## The packer (scenesystem_20261015)

- CLightBinnerGPU (vtable 0x1805fe688): slot 5 0x1801b4530 -> 0x1801b2450 uploads the frame's records: for each light
  entry (0x640 bytes, binner + 0xe3b0 list), slot 14 (0x70) 0x1801b14a0 -> **0x1801b14b0** packs one 0x1e0-byte
  record, then the array goes to the structured buffer (vfn 0x380 of the render context).
- 0x1801b14b0 (entry, record): 0x1804a65f0(entry + 0x18 = the light desc, out, the light -> camera-relative transform)
  turns the desc camera-relative; then record 0x00 = out + 0x00 (the projection), 0x40 = out + 0x40 x a bias matrix,
  0x80 = out + 0x90 (apex / direction, w), 0x90 / 0x94 = out + 0xc8 / 0xcc (distance fade), 0x98 / 0x9c = out + 0xac /
  0xb0 (near / far fade scales), 0xa0..0xa8 = out + 0xb4..0xbc colour x entry + 0x1b8 x (entry + 0x1c0 or + 0x1c4),
  0xac = the cookie slice ((i + 0.5) / n, negated for a cube), 0xb0..0xcb = out + 0xd0.. (the orientation quaternion,
  the facing term), 0xcc = out + 0xec (the light type 1..5), 0xd0 = entry + 0x174.. (the shadow atlas rect), 0xe0 =
  out + 0xa0 / 0xa4 / 0xa8 (the shape terms; (0, 0, 1, 1) with a cookie), 0xf0 = the one-hot table 0x1805fe770 by
  bakedshadowindex (entry + 0x1ea: -1 none, 0..3 R..A), 0x100 = max(0.04, entry + 0x210) (min roughness), 0x104 =
  entry + 0x1e0 / 0x1e4 (shadow strength), 0x108 = flags (1, 2, 4, 8 has a baked channel, 0x10, << 16 entry + 0x1fc),
  0x10c / 0x1a0 = the cookie texture and its matrix, 0x110 = the clip box (entry + 0x214 & 0x100), 0x140..0x18c a
  bounding sphere (centre, radius >= 0.25, 1 / radius).

## The desc (client_20261015)

- C_BarnLight (vtable 0x181cb1408; schema: m_bEnabled 0x1098, m_nColorMode 0x109c, m_Color 0x10a0,
  m_flColorTemperature 0x10a4, m_flBrightness 0x10a8, m_flBrightnessScale 0x10ac, m_nBakedShadowIndex 0x10b4,
  m_nLuminaireShape 0x10c0, m_flLuminaireSize 0x10c4, m_flLuminaireAnisotropy 0x10c8, m_hLightCookie 0x1188,
  m_flShape 0x1190, m_flSoftX / Y 0x1194 / 0x1198, m_flSkirt 0x119c, m_flSkirtNear 0x11a0, m_vSizeParams 0x11a4,
  m_flRange 0x11b0, m_vShear 0x11b4, m_flMinRoughness 0x11ec, m_flFadeSizeStart / End 0x1210 / 0x1214, the
  precomputed bounds / OBBs 0x1224..). Constructor 0x180d7da70.
- **0x180d81100** builds the 0x12c-byte desc: +0x00 = 1817658a0(size, range, shear) the projection, +0x40 its
  inverse (181747070), +0x80 = 181763bf0 (a plane from the inverse), +0x90 = 181764b10(size, range, shear) the apex,
  +0xa0 / +0xa4 = clamp(1 - soft_x / soft_y, 0, 0.9999999) (1801587b0), +0xa8 = 181765700(shape), +0xac / +0xb0 =
  181765730(skirt_near, skirt, size, range), +0xb4 = vfn 0x7f0 (180d87da0) x 181765820(+0x90, 100), +0xc4 the
  cookie, +0xc8 = (1, 0) (181763ff0), +0xd0 = (0, 0, 0, 1), +0xe0 = (1, 0, 0) (1817627f0), then the luminaire
  (181764c90: tan(size / 2) x (sqrt(w) + 100) with the anisotropy; shape 1 1817642b0 (type 2: +0xf0.. the corners,
  +0xc0 = 1 / area), shape 2 181764480 (type 1: a rectangle, +0xc0 = pi / (4 x w x h))).
- 1817658a0: axes (light x forward, y left, z up) X = -y, Y = z, Z = x; shear X += k shear.x Z, Y -= k shear.y Z
  (k = max(1 / range, |size.z| x 2^-23)); X / size.x, Y / size.y, z' = (size.z + k) Z, w = size.z Z + 1 (VMatrix
  products, column vectors; the axis matrix through 181747920).
- 181765730(n0, s, size, range): n = clamp(n0) range, f = clamp(1 - s) range, k = 1 / range + size.z;
  a = clamp(k n / (n size.z + 1)), b = clamp(1 - k f / (f size.z + 1)); -> (a > 0 ? 1 / a : 0, b > 0 ? 1 / b : 0).
- 181764b10: size.z > 0: the apex (-1 / size.z) x (1, shear.x / range, shear.y / range), w = its length^2; else
  -normalize(1, shear.x / range, shear.y / range), w = 0 (a directional barn).
- 181765820(apex, 100): w > 0 ? (sqrt(w) + 100)^2 / w : 1.
- 181765700(shape): shape > 0 ? clamp(shape) x 0.875 + 0.125 : 0.
- 180d87da0 (the colour): 0 when disabled; colormode 0: the colour sRGB -> linear (18174a050), else the colour
  temperature (180d80610); x 2^m_flBrightness (V_exp2f) x m_flBrightnessScale; x the light style's value and colour
  when it has one (+0x13a0).
- light_environment is C_LightEnvironmentEntity (a C_LightEntity: CLightComponent vtable 0x181acef90, m_Color 0x78,
  m_flBrightness 0x80, m_flBrightnessScale 0x84, m_flBrightnessMult 0x88, ...): not this path; its colour function is
  UNREAD (no V_exp2f caller reads those fields).

## The BRDF after the light's colour (csgo_complex's pixel shader, read 2026-11-20)

The loop's last lines, and the sun's (lines ~785-799) are the same with the sun's direction, colour x its visibility
and _m16.w for _m11:
```
NL = max(0, dot(N, L))                       // N: the shading normal (_16230), L: dir (L / d, or _m2.xyz)
r  = max(rough.x, _m11)                      // rough: _11004 = max(the material's, pow(saturate(max(|ddx n|^2, |ddy n|^2)), 0.333))
V  = -normalize(pos - eye); H = normalize(L + V)
a  = r * r;  D' = a / ((N.H)^2 (a^2 - 1) + 1)  // pi x GGX's D
k  = (r + 1)^2 / 8
F  = F0 + (1 - F0) pow(max(1e-6, 1 - max(0, L.H)), 5)   // F0 = mix(g_flReflectance = ((1.5-1)/(1.5+1))^2 = 0.04, albedo, metalness)
spec += F x D'^2 / (4 (NL (1 - k) + k)(max(0, N.V) (1 - k) + k)) x NL x colour
diff += NL x colour
```
After the loop: diffuse out = (diff + indirect x (1 - E) x AO) x albedo x (1 - metalness) (no 1 / pi; the direct diffuse
takes no AO); specular out += spec x (1 + F0 x 0.125 ((rx + ry)^2)^2 x saturate(N.V)) x _13436 (the material AO
texture's x times the screen-space AO, 1 without it). Ported as barnlights.js cs2Direct, used by the barns, the
omnis (maplights.js) and the sun (lighting.js LIGHTS_BEGIN_PATCHED) on every MeshStandardMaterial in place of three's
RE_Direct (Smith-correlated visibility, a 0.0525 roughness floor plus three's own derivative term). The sun's _m16.w
is taken as max(0.04, light_environment's minroughness), the barns' rule: its own fill is unread.

## The cookie's colour space (2026-11-20)

The shader's sampler is a bindless 3D texture (PerViewLightingConstantBufferGpu_t._m29); how scenesystem builds it is
unread. Measured instead: read as stored, de_vertigo s6's lamp ended along a bright arc where CS2's light trails off
(the patch's tail at ~0.61 of its middle against CS2's 0.25, display values); read as sRGB the profile follows CS2's
down to the wall (within ~3-10 %, a uniform offset: the per-view scales or exposure). A vtex without
VTexFlags.CREATE_LINEAR_API_TEXTURE (512) is an sRGB API texture, which fits: maplights.js reads cookies as sRGB unless
the flag is set (none of CS2's stock cookies has it: flags 8, NO_LOD).

## The cookie branch (csgo_complex's pixel shader, the same loop; read 2026-11-20)

```
if _m4.w == 0: col *= shape(_m9, p'.xy)
elif _m4.w < 0:                       // a cube cookie, slice -_m4.w
  d = the direction to the light (_m2.xyz or L) turned by the inverse of _m5's quaternion
  uv = (atan(d.y, -d.x) / 2pi, acos(d.z) / pi) * _m9.zw + _m9.xy
  col *= textureLod(_m29 3D texture, (uv, -_m4.w), 0).rgb   // g_sTrilinearWrap
else:                                 // a 2D cookie, slice _m4.w
  uv = (p'.xy * (0.5, -0.5) + 0.5) * _m9.zw + _m9.xy        // _m9 = (0, 0, 1, 1) with a cookie (the packer)
  col *= textureLod(_m29 3D texture, (uv, _m4.w), 0).rgb    // g_sCookieSampler
```
_m4.w is (i + 0.5) / n (the packer 0x1801b14b0 +0xac): slice i's centre, so a 3D texture's z filtering reads slice i
alone (ours: a 2D array, layer i). Not read: how the slices are made (size, format, sRGB: PerViewLightingConstantBufferGpu
_m29 is a bindless index), g_sCookieSampler's filter / wrap. The cookies of CS2's stock maps are BGRA8888 512^2
single-mip vtexs (flags NO_LOD), in pak01 materials/effects/lightcookies/.

## Status

world/barnlights.js: stationary light_barn as above (16 nearest in view, three's point BRDF for the specular).
world/maplights.js: stationary light_omni2 from source2-compiler's units (its C_OmniLight desc is untraced). 2D cookies (bake/CookieBake.cs, maplights.js
setCookies) since 2026-11-20. TODO: light_rect / light_spot, light styles, cube cookies, the clip box, dynamic shadows, the area-light specular, the per-view
scales (entry + 0x1b8 / 0x1c0), light_environment's colour.
