# MCVL Protocol Analysis Layer

Independent deterministic evidence layer for reverse-engineering the MCVL protocol.

Rules:
- Captures are immutable evidence.
- A single packet cannot establish field semantics.
- Unknown fields remain unknown.
- Hypotheses require explicit evidence.
- The analyzer does not open sockets and does not modify the MCVL runtime.
- MetaGPT is an optional reasoning layer on top of this deterministic model.

Current fixture: PID 1026 from MCVL_SERVER_DEBUG_20261008_194923.log.txt is registered as unresolved. Only observed frame length and prefix bytes are verified.

Integration boundary: when the runtime source is extracted from mcvl_godot.zip, the TCP decoder can emit PacketCapture objects into this layer. No protocol logic needs to be duplicated in the server.
