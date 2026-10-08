# Embedded Server Replacement

The original source that emitted:
- `SERVER_STARTED port=9001`
- `RX_FRAME`
- `RX_PACKET pid=1026`
- `FRAME_HANDLED`
- `TX_RESPONSE`

was not found in the repository or supplied Godot runtime archive.

This module is therefore an explicit **replacement compatibility server**, not a recovered original implementation.

Safety rules:
- TCP only, localhost by default.
- Payload bytes are logged verbatim.
- No checksum/length/field semantics are inferred.
- PID 1026 recognition is capture-specific evidence only.
- No response bytes are fabricated.
- Existing protocol handlers are not changed.

Important limitation:
`recv()` is intentionally simple and is not a production TCP frame decoder. It is suitable for reproducing the current debug fixture and testing the capture pipeline only. Production wiring requires the real framing evidence.
