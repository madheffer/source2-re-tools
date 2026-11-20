# Pulse: point_pulse graphs on CS2's official maps

server_20261105. Graphs: pak01 `pulse/csgo_devonly/*.vpulse` (vpulse_c2, KV3).

A `point_pulse` entity's `graph_def` names a `.vpulse`. The map's I/O calls the graph's methods as the entity's inputs;
the gamerules post events to its handlers. The point_pulse is on CleanUpMap's preserve list (its variables carry over a
round).

## Functions

Each cell / function has a registration record in .data (name, title, description, ..., the function).

| Address | Module | What |
|---|---|---|
| 1801dbe50 (record 181da11a0) | server | CCSPointPulseAPI::GetIsWingman: gamerules present && CCSGameRules::IsWingman |
| 1809108d0 | server | CCSGameRules::IsWingman: game_type (vfn 0x98) 0 and game_mode (vfn 0xa0) 2 |
| 1801dbdc0 | server | CCSPointPulseAPI::GetScoreToEndMatch: `rules+0x128 * mp_overtime_maxrounds + mp_maxrounds` (rules+0x128 the overtime count; unused by the pool) |
| 1801dbd30, ... | server | CCSPointPulseAPI::GetTScore / CCSPointPulseAPI::GetCTScore / CCSPointPulseAPI::GetRoundsPlayedThisPhase (unused by the pool) |
| records 181da11f0 ... | server | CCSPointPulseAPI::OnRoundStart / CCSPointPulseAPI::OnRoundFreezeEnd / CCSPointPulseAPI::OnRoundEnd (events): gamerules events to every graph's handlers |
| 1808950a0 (record 181e02620) | server | CPulseCell_Step_EntFire::FireAtName: m_Input on the TargetName with pParam; activator = caller = the domain's entity (vfn 0); empty name logs "Invalid target entity name."; dispatched through the domain's vfn 0x8 |
| 180894d20 | server | CPulseCell_Step_EntFire::Run: handle form: AcceptInput (1813ac4d0) at once, after the entity system's input listeners (+0xc20) |
| 1815ace70 | server | CPulseCell_Value_RandomInt::Eval: tier0 RandomInt(nMin, nMax), the global uniform stream |
| 1815ac7a0 -> 1815c9c00 | server | CPulseCell_Outflow_CycleRandom::Run: n = outputs (+0x48), list +0x50 (0x48 each); n > 0: RandomInt(0, n - 1), cursor vfn 0x30 to that outflow |
| 1815ac080 -> 1815ca640 | server | CPulseCell_Inflow_Wait::Wait: cursor vfn 0x70 (resume point = m_WakeResume), then scheduler (1823ab528) vfn 0x80 (cursor, flDurationSec) |
| 181614f50 | server | CPulseCell_Timeline::Start (record only) |
| 181617a10 / 181617c60 | server | CPulseCursorFuncs::TagCursor / KillCursorsWithTag (records only) |
| 181384290 | server | the I/O system's name search (FireAtName's domain dispatch assumed like it) |

## Vtables

| Address | Class |
|---|---|
| 1818ad288 | CPulseGraphInstance_ServerEntity |
| 1819d1878 | CPointPulse |
| 1819e00a0 | CPulseServerCursor |
| 181abb4b0 | CPulseExecCursor |
| | CCSPointPulseSystem (the game system) |

## Where the graphs are

| Map | point_pulse | graph_def |
|---|---|---|
| de_inferno | [PR#]inferno_script | pulse/csgo_devonly/de_inferno_script.vpulse |
| de_nuke | [PR#]nuke_script | pulse/csgo_devonly/de_nuke_script.vpulse |
| de_overpass | [PR#]overpass_script | pulse/csgo_devonly/de_overpass_script.vpulse |
| de_vertigo | [PR#]vertigo_script | pulse/csgo_devonly/de_vertigo_script.vpulse |
| de_train | (unnamed) | pulse/csgo_devonly/de_train_script.vpulse |

All in pak01, none in the map's own vpk (the file system looks in the map's vpk first, then pak01). No point_pulse:
de_dust2, de_mirage, de_ancient(_night), de_anubis, de_cache, de_boulder, de_fachwerk, de_debris, de_eldorado,
de_poseidon. de_boulder has a `point_script` "[PR#]wingman_script" naming `scripts/de_boulder_wingman.vjs`, in neither
its vpk nor pak01 (loads nothing).

## The compiled graph

- `m_Cells`, by `_class`: CPulseCell_Inflow_Method { m_MethodName, m_EntryChunk, m_bIsPublic },
  CPulseCell_Inflow_EventHandler { m_EventName, m_EntryChunk }, CPulseCell_Step_EntFire { m_Input },
  CPulseCell_Inflow_Wait { m_WakeResume }, CPulseCell_Outflow_CycleRandom { m_Outputs }, CPulseCell_Timeline
  { m_TimelineEvents [{ m_flTimeFromPrevious, m_EventOutflow }], m_OnFinished, m_bWaitForChildOutflows },
  CPulseCell_Value_RandomInt.
- `m_Vars` { m_Name, m_Type, m_DefaultValue }; `m_Constants` { m_Type, m_Value }; `m_DomainValues` (entity names).
- `m_InvokeBindings` { m_FuncName, m_nCellIndex, m_RegisterMap { m_Inparams, m_Outparams }: argument name -> register };
  `m_CallInfos`; `m_Chunks` { m_Instructions, m_Registers (each with its PVAL type) }.
- An outflow is { m_nDestChunk, m_nInstruction }.
- Instructions in the pool's five graphs: NOP, GET_CONST, GET_DOMAIN_VALUE, GET_VAR, SET_VAR, CONVERT_VALUE, ADD, DIV,
  MOD, LT, JUMP, JUMP_COND (to m_nDestInstruction when reg0 is true), CELL_INVOKE / LIBRARY_INVOKE (binding at
  m_nInvokeBindingIndex), PULSE_CALL_SYNC / PULSE_CALL_ASYNC_FIRE (chunk m_nChunk), IMMEDIATE_HALT, RETURN_VOID.
- A flow cell's invoke is followed by IMMEDIATE_HALT: the cell moves the cursor (CycleRandom) or suspends it (Wait), so
  execution never reaches the halt unless nothing took over.

## What the graphs do

- **GameModeCheck** (de_inferno, de_nuke, de_overpass, de_vertigo; private, fired by logic_auto OnMapSpawn):
  GetIsWingman; Wingman: `spawnpoints.standard` SetDisabled, `spawnpoints.2v2` SetEnabled, `brush.blocker` Enable,
  `buyzone.2v2` Enable, `navblocker.2v2` BlockNav, `props.2v2` Enable + EnableCollision (de_inferno's order; de_vertigo
  walls site A off: `brush.blocker.a`, `navblocker.2v2.a`, `props.2v2.a`, and disables `bombsite.tag.b`); otherwise
  `buyzone.2v2` Disable, `navblocker.2v2` UnblockNav, `brush.blocker` Disable.
- **WorkplaceInjury** (de_vertigo; the fall trigger_hurts' OnHurtPlayer): vInjury += 1, then WorkplaceInjuryDisplay:
  below 10 `safetysign.numbers` Skin vInjury, else `safetysign.numbers.ten` Enable, `safetysign.numbers` Skin
  vInjury % 10, `safetysign.numbers.ten` Skin int(float(vInjury) / 10). logic_auto OnMapSpawn fires Display each round;
  the count lives on the preserved point_pulse.
- **Lightning** (de_train): OnRoundStart kills the cursors tagged "lightning" (HardCancel) and async-fires lightningLoop:
  tag "lightning", nextLightningTime = RandomInt(loopTimerMin 20, loopTimerMax 120), Wait it, CycleRandom over
  lightningStrike / _2 / _3 / _4 (thunder / thunder2 / thunder3 StartSound), then the loop again (a sync call: each
  strike adds a frame). OnRoundEnd kills them. lightFlicker_1's Timeline (bombsite / spawn lights' SetStyle) is called by
  nothing.

## Unread

- The domain's FireAtName (vfn 0x8 of the object at cursor context +8): assumed to search as 181384290 does and
  dispatch at once like Run.
- PULSE_CALL_ASYNC_FIRE's order (taken as: the fired cursor runs at once, before the caller goes on).
- The scheduler's wake (which step of the frame a woken cursor runs in).
- Timeline::Start's clock and bWaitForChildOutflows; TagCursor's bInherit; KillCursorsWithTag's SoftCancel.
- CPointPulse's input lookup (the maps fire private methods; taken as every Inflow_Method an input).
- RestartRound's post of OnRoundStart against the frame (taken as: as the round's world is made, before its I/O).
- An integer DIV / MOD by zero (taken as 0).
