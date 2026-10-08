MetaGPT Bridge Contract

Role: MCVLProtocolAnalyst

Input: normalized PacketCapture records plus deterministic analyzer output.

Required separation:
- OBSERVED: directly present in captures.
- HYPOTHESIS: possible interpretation, always unverified.
- REQUIRED_EVIDENCE: captures/tests needed to verify it.

Forbidden:
- inventing response packets;
- declaring checksum/length semantics from one frame;
- modifying runtime code;
- generating packet handlers;
- treating an LLM confidence score as protocol verification.

MetaGPT may reason over evidence, but verification remains deterministic and evidence-driven.
