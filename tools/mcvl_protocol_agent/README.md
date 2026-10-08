# MCVL Protocol Analysis Layer

Independent deterministic evidence layer for reverse-engineering the MCVL protocol.

## Phase 2.5 — Capture Ingestion CLI

The ingestion layer is offline and deterministic. It reads MCVL debug logs and extracts RX frame hex, PID/session, client endpoint and TX response count into PacketCapture records.

Usage:

    python -m tools.mcvl_protocol_agent LOGFILE -o captures.json

Multiple logs/globs:

    python -m tools.mcvl_protocol_agent 'MCVL_SERVER_DEBUG_*.log.txt' -o captures.json --pid 1026

Pipeline:

    log files -> ingest_log -> PacketCapture -> EvidenceStore -> deterministic analyzer -> optional MetaGPT bridge

The CLI does not open sockets, infer protocol semantics, or modify runtime code.

## Safety rules

- Captures are immutable evidence.
- A single packet cannot establish field semantics.
- Unknown fields remain unknown.
- Hypotheses require explicit evidence.
- MetaGPT is an optional reasoning layer.
- Runtime integration happens only after the actual source decoder is identified.

Current fixture: PID 1026 from MCVL_SERVER_DEBUG_20261008_194923.log.txt is unresolved; only observed frame length and prefix bytes are verified.

## Phase 4.1 — Repeated structural evidence

The Phase 4.1 dataset in `captures/phase4_20261008.json` contains two independent observations for PID 1026 and two independent observations for PID 1011, from two separate client connections/log files.

The deterministic Phase 4.1 analyzer verifies only repeated byte-position relationships supported by those observations:

- `bytes[4:8]` is a 4-byte big-endian value equal to `frame_length - 8` across all four observations.
- `bytes[11:13]` is a 2-byte big-endian value equal to the logged PID across all four observations.
- Therefore the current evidence promotes the **length field offset 4..7** and **PID field offset 11..12** to verified structural rules for the supplied Phase 4.1 evidence set.
- The analyzer does **not** assign semantics to `bytes[0:4]`, `bytes[8:11]`, checksum, or payload.
- TCP `RX_CHUNK` read boundaries are not treated as TCP packet boundaries.

Use:

    python -m unittest tools.mcvl_protocol_agent.test_phase41

The analyzer is deterministic and does not call MetaGPT.

## Phase 4.2 — Deterministic frame/stream validation

`phase42.py` turns the Phase 4.1 structural rules into a conservative validator. It accepts a frame only when:

- the 4-byte value at `bytes[4:8]` equals `len(frame) - 8`;
- the 2-byte value at `bytes[11:13]` is available and, for a capture, matches its externally observed PID;
- concatenated streams can be split using the same length rule.

It explicitly rejects truncated headers, truncated frames, length mismatches, frames that declare an impossible minimum size, and capture/PID mismatches. It does not decode header semantics, `bytes[8:11]`, checksum, session state, or payload semantics.

Test suite:

    python -m unittest tools.mcvl_protocol_agent.test_phase41 tools.mcvl_protocol_agent.test_phase42

The current Phase 4.1 evidence yields frame lengths `35, 25, 35, 25` and PID sequence `1026, 1011, 1026, 1011` when the four observations are concatenated.
