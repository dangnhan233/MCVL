# Phase 3 — Runtime Source Discovery

Purpose: identify the real MCVL runtime TCP/server/frame-decoder/dispatcher integration point before connecting live PacketCapture evidence.

Run against an extracted Godot project:

    python -m tools.mcvl_protocol_agent.runtime_discovery /path/to/mcvl_godot -o runtime_discovery.json

The scanner ranks files containing TCP/socket/server and packet encode/decode symbols. It is read-only and does not modify the project.

Integration contract:

    runtime decoder -> PacketCapture -> EvidenceStore

The runtime must not import MetaGPT. The MetaGPT bridge remains downstream of the evidence layer.

Current status: mcvl_godot.zip is present in the repository, but the current GitHub connector cannot materialize binary ZIP contents in this session. Therefore no runtime source file is claimed as verified yet.
