# Pulse: point_pulse graphs on CS2's official maps (server.dll 2026-11-05)

CS2's official maps run part of their logic as compiled Pulse graphs: a `point_pulse` entity whose `graph_def` names a
`.vpulse` resource. The map's I/O calls the graph's methods as the entity's inputs, the gamerules post events to its
handlers. Without it the maps' Wingman cuts, de_vertigo's injury board and de_train's lightning do nothing.

Addresses are server_20261105.dll (the Ghidra project's /server_20261105.dll; the copy in source2-compiler
tools/re/binaries for the python tools). Code: web/src/world/pulse/ (graph.js the checks, vm.js the runtime, cells.js
the cells, load.js the loader), web/src/world/entities/classes/pulse.js (the entity), bake/PulseBake.cs (the bake).

## Where the graphs are

| Map | point_pulse | graph_def | Where the graph lives |
|---|---|---|---|
| de_inferno | [PR#]inferno_script | pulse/csgo_devonly/de_inferno_script.vpulse | pak01 |
| de_nuke | [PR#]nuke_script | pulse/csgo_devonly/de_nuke_script.vpulse | pak01 |
| de_overpass | [PR#]overpass_script | pulse/csgo_devonly/de_overpass_script.vpulse | pak01 |
| de_vertigo | [PR#]vertigo_script | pulse/csgo_devonly/de_vertigo_script.vpulse | pak01 |
| de_train | (unnamed) | pulse/csgo_devonly/de_train_script.vpulse | pak01 |

None is in its map's own vpk: the bake looks in the map's vpk first, then pak01 (as CS2's file system does). The other
pool maps (de_dust2, de_mirage, de_ancient(_night), de_anubis, de_cache, de_boulder, de_fachwerk, de_debris,
de_eldorado, de_poseidon) have no point_pulse. de_boulder has a `point_script` "[PR#]wingman_script" naming
`scripts/de_boulder_wingman.vjs`, which ships in neither its vpk nor pak01 (CS2 loads nothing for it).

## The compiled graph (vpulse_c2, KV3)

`m_Cells` (each `_class`: CPulseCell_Inflow_Method { m_MethodName, m_EntryChunk, m_bIsPublic },
CPulseCell_Inflow_EventHandler { m_EventName, m_EntryChunk }, CPulseCell_Step_EntFire { m_Input },
CPulseCell_Inflow_Wait { m_WakeResume }, CPulseCell_Outflow_CycleRandom { m_Outputs }, CPulseCell_Timeline
{ m_TimelineEvents [{ m_flTimeFromPrevious, m_EventOutflow }], m_OnFinished, m_bWaitForChildOutflows },
CPulseCell_Value_RandomInt), `m_Vars` ({ m_Name, m_Type, m_DefaultValue }), `m_Constants` ({ m_Type, m_Value }),
`m_DomainValues` (entity names), `m_InvokeBindings` ({ m_FuncName, m_nCellIndex, m_RegisterMap { m_Inparams,
m_Outparams }: argument name -> register }), `m_CallInfos`, `m_Chunks` ({ m_Instructions, m_Registers (each with its
PVAL type) }). An outflow is { m_nDestChunk, m_nInstruction }.

Instructions seen in the pool's five graphs: NOP, GET_CONST, GET_DOMAIN_VALUE, GET_VAR, SET_VAR, CONVERT_VALUE, ADD,
DIV, MOD, LT, JUMP, JUMP_COND (to m_nDestInstruction when reg0 is true), CELL_INVOKE / LIBRARY_INVOKE (the binding at
m_nInvokeBindingIndex), PULSE_CALL_SYNC / PULSE_CALL_ASYNC_FIRE (chunk m_nChunk), IMMEDIATE_HALT, RETURN_VOID. A flow
cell's invoke is followed by IMMEDIATE_HALT: the cell moves the cursor (CycleRandom's pick) or suspends it (Wait), so
execution never falls through to the halt unless nothing took over.

## The cells and functions (each one's registration record in .data: name, title, description, ..., the function)

| Function | Address | What |
|---|---|---|
| CCSPointPulseAPI::GetIsWingman | 1801dbe50 (record 181da11a0) | retval = gamerules present && CCSGameRules::IsWingman (1809108d0): game_type (vfn 0x98) 0 and game_mode (vfn 0xa0) 2 |
| CCSPointPulseAPI::GetScoreToEndMatch | 1801dbdc0 | rules+0x128 (the overtime count) x mp_overtime_maxrounds + mp_maxrounds (not used by the pool) |
| CCSPointPulseAPI::GetTScore / GetCTScore / GetRoundsPlayedThisPhase | 1801dbd30, ... | (not used by the pool) |
| CCSPointPulseAPI::OnRoundStart / OnRoundFreezeEnd / OnRoundEnd | events (records 181da11f0 ...) | the gamerules' events to every graph's handlers |
| CPulseCell_Step_EntFire::FireAtName | 1808950a0 (record 181e02620) | the cell's m_Input on the name in TargetName with pParam; activator = caller = the domain's entity (vfn 0); an empty name logs "Invalid target entity name."; dispatched through the domain's vfn 0x8 |
| CPulseCell_Step_EntFire::Run | 180894d20 | the handle form: AcceptInput (1813ac4d0) on the target at once, after the entity system's input listeners (+0xc20) |
| CPulseCell_Value_RandomInt::Eval | 1815ace70 | tier0 RandomInt(nMin, nMax): the global uniform stream |
| CPulseCell_Outflow_CycleRandom::Run | 1815ac7a0 -> 1815c9c00 | n = outputs (+0x48), list +0x50 (0x48 each): with n > 0, RandomInt(0, n - 1), then the cursor's vfn 0x30 to that outflow |
| CPulseCell_Inflow_Wait::Wait | 1815ac080 -> 1815ca640 | the cursor's vfn 0x70 (its resume point: this cell's m_WakeResume), then the scheduler (1823ab528) vfn 0x80 (cursor, flDurationSec) |
| CPulseCell_Timeline::Start | 181614f50 | (read only to its record) |
| CPulseCursorFuncs::TagCursor / KillCursorsWithTag | 181617a10 / 181617c60 | (read only to their records) |

The pulse runtime classes: CPulseGraphInstance_ServerEntity (vtable 1818ad288), CPointPulse (1819d1878),
CPulseServerCursor (1819e00a0), CPulseExecCursor (181abb4b0), CCSPointPulseSystem (the game system).

## What the graphs do

- **GameModeCheck** (de_inferno, de_nuke, de_overpass, de_vertigo; private methods, fired by the map's logic_auto
  OnMapSpawn): GetIsWingman, then Wingman: `spawnpoints.standard` SetDisabled, `spawnpoints.2v2` SetEnabled,
  `brush.blocker` Enable, `buyzone.2v2` Enable, `navblocker.2v2` BlockNav, `props.2v2` Enable + EnableCollision
  (de_inferno's order; de_vertigo walls site A off: `brush.blocker.a`, `navblocker.2v2.a`, `props.2v2.a`, and
  disables `bombsite.tag.b`); otherwise `buyzone.2v2` Disable, `navblocker.2v2` UnblockNav, `brush.blocker` Disable.
- **WorkplaceInjury** (de_vertigo; its fall trigger_hurts' OnHurtPlayer): vInjury += 1, then
  WorkplaceInjuryDisplay: below 10 `safetysign.numbers` Skin vInjury, else `safetysign.numbers.ten` Enable,
  `safetysign.numbers` Skin vInjury % 10, `safetysign.numbers.ten` Skin int(float(vInjury) / 10). The logic_auto's
  OnMapSpawn fires Display each round; the count lives on the preserved point_pulse.
- **The lightning** (de_train): OnRoundStart kills the cursors tagged "lightning" (HardCancel) and async-fires
  lightningLoop: tag "lightning", nextLightningTime = RandomInt(loopTimerMin 20, loopTimerMax 120), Wait it, then
  CycleRandom over lightningStrike / _2 / _3 / _4 (thunder / thunder2 / thunder3 StartSound), then the loop again
  (a sync call: each strike adds a frame). OnRoundEnd kills them. lightFlicker_1's Timeline (bombsite / spawn lights'
  SetStyle) is called by nothing in the map.

## Ours

- GetIsWingman answers from the match (gamemodes.js pulseWingman, sent with the round: game.js pulseRules): a team
  match whose CS2 game mode is 0 / 2 (Competitive 1v1 / 3v3 run Wingman's), except a 1v1 playing our own section cuts
  (they replace Valve's walls; de_inferno has both).
- The point_pulse is on CleanUpMap's preserve list: its variables are carried over a round (round-carry.js). A team
  match's round runs its spawn-time I/O as the world is made (world.js rules.spawnIo), so GameModeCheck has set the
  spawns and walls before anyone spawns, as CS2's preserved spawn points and func_brushes have them.

## Still to trace (TODO(trace) in the code)

- The domain's FireAtName (vfn 0x8 of the object at the cursor context +8): assumed to search the name as the I/O
  system's 181384290 does and dispatch at once like Run.
- PULSE_CALL_ASYNC_FIRE's order (the fired cursor runs at once here, before the caller goes on).
- The scheduler's wake (which step of the frame a woken cursor runs in: here the engine's queue).
- Timeline::Start's clock and bWaitForChildOutflows; TagCursor's bInherit; KillCursorsWithTag's SoftCancel.
- CPointPulse's input lookup (the maps fire private methods; here every Inflow_Method is an input).
- RestartRound's post of OnRoundStart against the frame (here: as the round's world is made, before its I/O).
- An integer DIV / MOD by zero (0 here).
