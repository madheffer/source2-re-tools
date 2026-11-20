# CS:GO CBaseTrigger: Disable and EndTouch

server.dll (CS:GO legacy, md5 8048019154549052cb6dc057b76f6a85, Ghidra `/csgo_server_legacy.dll`, base 0x10000000).

## Functions

| Address | Module | What |
|---|---|---|
| 0x103b5300-0x103b54a0 | server | CBaseTrigger's datamap builder (fills the table at 0x10a3568c; class name "CBaseTrigger" set at 0x10bc1cc4) |
| 0x1018b070 | server | input Enable |
| 0x1018b080 | server | input Disable: `jmp [vtable + 0x330]` |
| 0x103ac570 | server | input Toggle: `jmp [vtable + 0x334]` |
| 0x103c659e / 0x103c65a6 / 0x103c65ae | server | inputs TouchTest / StartTouch / EndTouch |
| 0x103b59b0 | server | Enable (vtable 0x324, unread) |
| 0x103b5ab0 | server | Disable (vtable 0x328) |
| 0x102266b0 / 0x102266c0 | server | the inputs' virtuals (vtable 0x32c / 0x330): `call [vtable + 0x324 / 0x328]`, `ret 4` |
| 0x103b5dd0 | server | PassesTriggerFilters (vtable 0x348): spawnflag tests on +0x31c, then the filter +0x410 |
| 0x103b6030 | server | OnEndTouchAll (vtable 0x350): m_OnEndTouchAll.FireOutput(pOther, this); in 36 vtables |
| 0x103b6090 | server | StartTouch (CBaseEntity's slot, unread) |
| 0x103b6170 | server | EndTouch (CBaseEntity's slot) |
| 0x102341d0 | server | SetSolidFlags |
| 0x101baa40 | server | CUtlVector<EHANDLE> Find |
| 0x1022a3a0 | server | COutputEvent::FireOutput |

## Fields

| Offset | Field |
|---|---|
| CBaseEntity +0x114 | solid flags (ushort) |
| CBaseEntity +0x158 | the VPhysics object |
| CBaseTrigger +0x31c | spawnflags |
| CBaseTrigger +0x408 | m_bDisabled |
| CBaseTrigger +0x410 | m_hFilter |
| CBaseTrigger +0x414 | m_OnStartTouch (COutputEvent, 0x18 each) |
| CBaseTrigger +0x42c | m_OnStartTouchAll |
| CBaseTrigger +0x444 | m_OnEndTouch |
| CBaseTrigger +0x45c | m_OnEndTouchAll |
| CBaseTrigger +0x474 | m_OnTouching |
| CBaseTrigger +0x48c | m_OnNotTouching |
| CBaseTrigger +0x4a4 | m_hTouchingEntities (CUtlVector<EHANDLE>; count +0x4b0) |

## Constants

| Value | What |
|---|---|
| 0x108da2f0 | CBaseTrigger's vtable (locator pointer 0x109bbe20 at 0x108da2ec) |
| 0x10a71a60 | RTTI type descriptor (".?AVCBaseTrigger@@" at 0x10a71a68) |
| 0x109a7ee0 | a base class descriptor |
| 8 | FSOLID_TRIGGER; Disable masks flags with 0xfff7 |

## Disable 0x103b5ab0

```
if (m_bDisabled != 1) { NetworkStateChanged(&m_bDisabled) [vtable + 0x354]; m_bDisabled = 1; }
if (VPhysicsGetObject()) VPhysicsGetObject()->EnableCollisions(false)            // +0x158, its slot 0x30
if (solid flags & 8 /* FSOLID_TRIGGER */) {
  SetSolidFlags(flags & 0xfff7)                                                 // 0x102341d0
  PhysicsTouchTriggers(0)                                                       // [vtable + 0x1b4]
}
```

A disabled trigger stops being a trigger solid; nothing touching it is told at once. Its touch links end in the engine's untouch pass (CBaseEntity::PhysicsCheckForEntityUntouch, unread here: a link whose touch stamp was not refreshed this frame is removed and EndTouch called on both sides).

## EndTouch 0x103b6170

```
if (m_hTouchingEntities.Find(pOther's handle) != -1) {        // 0x101baa40 on this + 0x4a4
  m_hTouchingEntities.FindAndRemove(handle)
  m_OnEndTouch.FireOutput(pOther, this)                       // 0x1022a3a0, unconditional: no m_bDisabled test
  // walk the list from the back: a dead handle is removed, a live one sets "still touched"
  if (nothing left) this->OnEndTouchAll(pOther)               // [vtable + 0x350]
}
```

OnEndTouch fires for whatever was inside when the trigger is disabled (the SDK's triggers.cpp has the `!m_bDisabled` test commented out under "FIXME: Without this, triggers fire their EndTouch outputs when they are disabled!"; the binary agrees).

## ze_crazykart's oil puddle

`i_item_oil_trigger` (trigger_multiple, filter_kart): `OnStartTouch !activator RunScriptCode AddSpeed(-0.24)`, `OnEndTouch !activator RunScriptCode AddSpeed(0.24)`. The puddle goes with `OnUser1 !self Disable` at 0, `!self Kill` at 0.05: the speed returns only because Disable ends the touch and EndTouch fires.

## Unread

- A killed trigger: the SDK's CBaseEntity::PhysicsRemoveTouchedList (UpdateOnRemove) calls PhysicsNotifyOtherOfUntouch(this, other), which calls `other->EndTouch(this)`: the removed entity is not told, so a killed trigger fires no OnEndTouch. Read both in this server.dll.
- The frame EndTouch lands on after a Disable (PhysicsCheckForEntityUntouch runs in the toucher's own physics step; for a VPhysics prop its VPhysicsUpdate).
- Enable 0x103b59b0 and StartTouch 0x103b6090: whether an Enable with something already inside starts a touch the same frame.
- A player (not a kart) in a CS:GO map's trigger goes through the CS2 engine's own trigger code, not these rules.
