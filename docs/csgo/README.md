# CS:GO legacy

Notes on CS:GO's legacy 32-bit binaries (server.dll md5 8048019154549052cb6dc057b76f6a85, client.dll, engine.dll; image base 0x10000000), read to run a CS:GO map on the CS2 engine. **CS:GO, not CS2.** The kart's physics (IVP) is in [../crazykart/](../crazykart/README.md).

## The files

4 files.

| File | Subject |
|---|---|
| [csgo-effects](csgo-effects.md) | CS:GO's steam jets, sprite trails and precipitation |
| [csgo-triggers](csgo-triggers.md) | CS:GO CBaseTrigger: Disable and EndTouch |
| [csgo-vscript](csgo-vscript.md) | CS:GO VScript: the prelude's EntFire |
| [source1-bake](source1-bake.md) | The Source 1 BSP bake (`lasers-bake --source1`) |

## General helpers

Addresses are the CS:GO legacy (32-bit) DLLs' (image base 0x10000000), each row's module first.

| Address | What |
|---|---|
| server.dll file offset 0xa36915 (text) | `function EntFire(target, action, value, delay, activator)`: the Squirrel prelude in the DLL; search `function <Name>(` for any other script helper (csgo-vscript.md 1) |
| server.dll 0x103b5ab0 / 0x103b6170 / 0x103b5dd0 | CBaseTrigger::Disable / EndTouch / PassesTriggerFilters; its vtable 0x108da2f0, found from the type descriptor 0x10a71a60 (".?AVCBaseTrigger@@") and the datamap builder at 0x103b5300 (a class's output offsets: search the output's name string, its one code xref is the builder) (csgo-triggers.md) |
| client.dll 0x107ab700 / 0x107ab7c0 / 0x107ac160 / 0x107ac270 | C_SteamJet: Start / Update (a particle a spawn event) / SimulateParticles / the lighting ramp (csgo-effects.md 1) |
| client.dll 0x10368f00 / 0x103690e0 / 0x10368ca0 | C_SpriteTrail: UpdateTrail (the ring's new point) / DrawModel (the beam's width, alpha, texture coordinate per point) / its bounds (csgo-effects.md 2) |
| client.dll 0x10799220 / 0x107998b0 / 0x107996a0 / 0x10796110 | CClient_Precipitation: InitializeParticlePrecip (systems per type) / the inner and outer dispatch (control points) / Precache (csgo-effects.md 3) |
| server.dll 0x10629060 | CSteamJet::Spawn (env_steamjet faces left, InitialState emits) (csgo-effects.md 1) |
| client.dll 0x107abea0 / 0x107abc20 / 0x1022f980 | C_SteamJet::RenderParticles (the ramp's lerp, the size by lifetime) / the unrolled quad / the rolled quad (csgo-effects.md 1) |
| engine.dll 0x100b6160 / 0x100b7210 / 0x10247b80 / 0x10246ea0 | IVEngineClient::GetLightForPoint (CEngineClient vtable 0x1047d850 slot 1) / slot 72 / ComputeLighting (no normal: the cube's six faces x 1/6, local lights folded in) / LightcacheGetDynamic (csgo-effects.md 1) |
| client.dll 0x109a94c0 / 0x109a9c50 / 0x109a9620 | CBeamSegDraw: Start / NextSeg (the segment normal, averaged at a point) / SpecifySeg (the two vertices) (csgo-effects.md 2) |
| client.dll 0x10798a30 / 0x10798ba0 / 0x10796430 / 0x10799600 | CClient_Precipitation: Simulate (the 0.125 s trace timer) / UpdateParticlePrecip (four rays: inside, nearby) / OnDataChanged (density = alpha x 0.01) / DestroyInnerParticlePrecip (csgo-effects.md 3) |
| client.dll 0x10994260 / 0x10995b30 / 0x109960d0 / 0x10994ee0 | RayTracingEnvironment: Trace4Rays / its traversal and triangle test (two-sided, 1e-10 epsilons, the triangle's own normal) / AddTriangle / SetupAccelerationStructure (unread) (csgo-effects.md 3) |
| client.dll 0x109616c0 / 0x1095fed0 / 0x10975cb0 | particle library: C_INIT_RtEnvCull (vtable 0x10d0765c) / C_INIT_LifespanFromVelocity (0x10d08c90) InitNewParticlesScalar / C_OP_SetControlPointToImpactPoint::Operate (0x10d0d1e8, unread) (csgo-effects.md 3) |
