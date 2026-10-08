# Phase 3.2 — Runtime Integration Point Contract

## Status

**BLOCKED_PENDING_RUNTIME_SOURCE**

The repository contains `mcvl_godot.zip` (12,501,644 bytes), but the GitHub connector cannot return binary ZIP contents. Therefore Phase 3.2 does **not** claim a verified runtime source file or function.

## Verified evidence

- Debug log evidence identifies a TCP endpoint at `127.0.0.1:9001`.
- A received frame for PID `1026` is 35 bytes.
- The runtime log records `RX_FRAME`, `RX_PACKET pid=1026`, and `FRAME_HANDLED packets=0`.
- The protocol record for PID 1026 remains unresolved.
- No response packet has been observed for the current capture.

## Required integration boundary

The eventual integration point MUST be the first deterministic point where the runtime has:

1. accepted/received bytes from the network;
2. reconstructed a complete frame;
3. before packet semantics are mutated or discarded.

Conceptual contract:

```
socket read
   -> frame reconstruction
   -> PacketCapture(raw bytes + metadata)
   -> existing decoder/dispatcher
   -> existing handler
```

The capture hook must be observational only. It must not:
- alter raw bytes;
- change frame boundaries;
- invent PID/fields;
- invoke MetaGPT from the network receive thread;
- change existing packet handling.

## Acceptance criteria for 3.2

Phase 3.2 can become **VERIFIED** only after the actual Godot/runtime source is available and all of the following are located:

- socket/TCP receive function;
- frame reconstruction function or equivalent;
- packet dispatch/decode call;
- exact source file and function/line;
- a test proving capture preserves the original frame bytes.

Until then, do not modify the runtime.

## Next phase

Phase 3.3 will implement the smallest possible adapter only after 3.2 is verified.
