# Phase 3.3 — Observational PacketCapture Adapter

Status: **READY_FOR_RUNTIME_WIRING**

This phase introduces an adapter that can be called at a verified complete-frame boundary.

Contract:

```
complete raw frame -> PacketCaptureAdapter.capture_frame() -> EvidenceStore
```

The adapter:
- copies the raw bytes;
- normalizes them only for storage;
- preserves the exact bytes in `PacketCapture.raw`;
- records runtime metadata;
- optionally appends to `EvidenceStore`.

It does **not**:
- parse PID;
- infer fields;
- calculate checksum;
- change framing;
- call MetaGPT;
- alter packet dispatch.

Runtime wiring is intentionally deferred until Phase 3.2 identifies the actual source file/function.

Acceptance test:
- captured `raw` must equal the runtime frame bytes byte-for-byte;
- stored hex must round-trip through `bytes.fromhex()`;
- adding capture must not modify the original byte sequence.
