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
