# Phase 3.5 — Runtime Wiring Boundary

## Status: READY_FOR_VERIFIED_SERVER_SOURCE

The project now has one explicit observational wiring boundary:

```
verified complete frame
        |
        v
RuntimeCaptureHook.observe(frame, context)
        |
        +--> PacketCaptureAdapter -> EvidenceStore
        |
        v
return original frame unchanged
        |
        v
existing decoder / dispatcher
```

This is a **wiring harness**, not a runtime patch.

### Why it is not connected to Godot

Phase 3.4 verified that `MCVL_Godot_Android_Landscape.zip` has no TCP/socket/packet layer. Connecting the hook to its map scripts would be incorrect.

### Server-side wiring contract

When the actual server/network source is available, insert exactly one call immediately after complete-frame reconstruction and before protocol dispatch:

```python
frame = receive_complete_frame(...)
frame = capture_hook.observe(frame, context)
dispatch(frame)
```

The existing decoder and dispatcher remain unchanged.

### Acceptance criteria

1. returned frame equals input byte-for-byte;
2. EvidenceStore receives exactly one capture;
3. no protocol field is inferred by the hook;
4. no MetaGPT call occurs in the network path;
5. removing the hook leaves existing dispatch behavior unchanged.

### Current gate

**BLOCKED_FOR_LIVE_WIRING** until the source implementing `SERVER_STARTED port=9001`, `RX_FRAME`, and `RX_PACKET pid=1026` is identified.
