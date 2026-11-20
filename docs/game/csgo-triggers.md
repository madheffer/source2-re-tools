# CS:GO's CBaseTrigger: Disable and EndTouch (the CS:GO layer's body touches)

Binary: `csgo legacy/csgo/bin/server.dll` (md5 8048019154549052cb6dc057b76f6a85, Ghidra `/csgo_server_legacy.dll`,
base 0x10000000). Read 2026-11-19 for ze_crazykart's oil puddles (BUGFIXES 2026-11-19): a kart kept every puddle's
slowdown, because our touch pass never ended a touch on a trigger that was disabled.

## What the map does

`i_item_oil_trigger` (trigger_multiple, filter_kart): `OnStartTouch !activator RunScriptCode AddSpeed(-0.24)`,
`OnEndTouch !activator RunScriptCode AddSpeed(0.24)`. When the puddle goes: `OnUser1 !self Disable` at 0,
`!self Kill` at 0.05. The speed comes back only if Disable ends the touch and EndTouch fires the output.

## CBaseTrigger

- The datamap's builder is at 0x103b5300-0x103b54a0 (it fills the table at 0x10a3568c; the class name string
  "CBaseTrigger" is set at 0x10bc1cc4). Inputs: Enable -> 0x1018b070, Disable -> 0x1018b080 (`jmp [vtable + 0x330]`),
  Toggle -> 0x103ac570 (`jmp [vtable + 0x334]`), TouchTest 0x103c659e, StartTouch 0x103c65a6, EndTouch 0x103c65ae.
- Outputs (COutputEvent, 0x18 each): m_OnStartTouch +0x414, m_OnStartTouchAll +0x42c, m_OnEndTouch +0x444,
  m_OnEndTouchAll +0x45c, m_OnTouching +0x474, m_OnNotTouching +0x48c.
- Other fields: spawnflags +0x31c, m_hFilter +0x410, m_bDisabled +0x408, m_hTouchingEntities (CUtlVector<EHANDLE>)
  +0x4a4 (its count +0x4b0), the solid flags (ushort) +0x114, the VPhysics object +0x158.
- RTTI: type descriptor 0x10a71a60 (".?AVCBaseTrigger@@" at 0x10a71a68), a base class descriptor 0x109a7ee0.
  CBaseTrigger's vtable is at **0x108da2f0** (the locator pointer 0x109bbe20 sits at 0x108da2ec).

| Slot (offset) | Address | What |
|---|---|---|
| 0x324 | 0x103b59b0 | Enable (not read) |
| 0x328 | **0x103b5ab0** | Disable |
| 0x32c / 0x330 | 0x102266b0 / 0x102266c0 | the input's virtuals: `call [vtable + 0x324 / 0x328]`, `ret 4` |
| 0x348 | 0x103b5dd0 | PassesTriggerFilters (the spawnflag tests on +0x31c, then the filter +0x410) |
| 0x350 | 0x103b6030 | OnEndTouchAll: m_OnEndTouchAll.FireOutput(pOther, this) (in 36 vtables) |
| (CBaseEntity's) | 0x103b6090 | StartTouch (not read) |
| (CBaseEntity's) | **0x103b6170** | EndTouch |

### Disable 0x103b5ab0

```
if (m_bDisabled != 1) { NetworkStateChanged(&m_bDisabled) [vtable + 0x354]; m_bDisabled = 1; }
if (VPhysicsGetObject()) VPhysicsGetObject()->EnableCollisions(false)            // +0x158, its slot 0x30
if (solid flags & 8 /* FSOLID_TRIGGER */) {
  SetSolidFlags(flags & 0xfff7)                                                 // 0x102341d0
  PhysicsTouchTriggers(0)                                                       // [vtable + 0x1b4]
}
```

So a disabled trigger stops being a trigger solid; nothing touching it is told at once. The touch links it holds
end in the engine's untouch pass (CBaseEntity::PhysicsCheckForEntityUntouch, not read in this binary: a link whose
touch stamp was not refreshed this frame is removed and EndTouch called on both sides).

### EndTouch 0x103b6170

```
if (m_hTouchingEntities.Find(pOther's handle) != -1) {        // 0x101baa40 on this + 0x4a4
  m_hTouchingEntities.FindAndRemove(handle)
  m_OnEndTouch.FireOutput(pOther, this)                       // 0x1022a3a0, unconditional: no m_bDisabled test
  // walk the list from the back: a dead handle is removed, a live one sets "still touched"
  if (nothing left) this->OnEndTouchAll(pOther)               // [vtable + 0x350]
}
```

**OnEndTouch fires for whatever was inside when the trigger is disabled.** (The Source SDK's triggers.cpp has the
same body, with the `!m_bDisabled` test commented out under "FIXME: Without this, triggers fire their EndTouch
outputs when they are disabled!"; the binary agrees.)

## Here

`web/src/cs2web/csgo/entities/body-triggers.js` bodyTouches: a trigger a body was in that is alive and no longer
enabled ends the touch on the next pass (the tick after the Disable): OnEndTouch, then OnEndTouchAll when nothing
else touches it. `entities-test.mjs` holds it.

## Not read (TODO)

- A **killed** trigger. The SDK's CBaseEntity::PhysicsRemoveTouchedList (UpdateOnRemove) calls
  PhysicsNotifyOtherOfUntouch(this, other), which calls `other->EndTouch(this)`: the entity removed is not told, so
  a killed trigger fires no OnEndTouch (and the map's "Disable, then Kill 0.05 s later" reads as written for that).
  body-triggers.js does it so (nothing fires); read both functions in this server.dll.
- The frame the EndTouch lands on after a Disable (PhysicsCheckForEntityUntouch runs in the toucher's own physics
  step; for a VPhysics prop that is its VPhysicsUpdate): here the next tick's touch pass.
- Enable 0x103b59b0 and StartTouch 0x103b6090 (whether an Enable with something already inside starts a touch the
  same frame: here the next pass does).
- A player (not a kart) in a CS:GO map's trigger goes through the CS2 engine's own trigger code
  (world/entities/classes/triggers.js), not these rules.
