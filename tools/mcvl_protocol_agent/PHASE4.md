# Phase 4 — Real TCP capture

Run the replacement server on `127.0.0.1:9001`, collect real TCP bytes from MCVL, and resolve TCP framing and PID 1026 from repeated evidence.

The server is evidence-first:
- `RX_CHUNK` is a TCP receive chunk, not a protocol frame.
- `RX_STREAM_HEX` is the concatenated byte stream for one connection.
- framing remains UNRESOLVED until repeated captures support a rule.
- PID 1026 remains UNRESOLVED until repeated captures support a field.
- no response bytes are fabricated.

Run:
```bash
python -m tools.mcvl_protocol_agent.server_replacement --host 127.0.0.1 --port 9001 --capture-dir phase4_captures
```

If the APK client is on Android, `127.0.0.1` means Android itself. A PC server therefore requires the PC LAN address or emulator/ADB forwarding.

Collect at least:
1. 10+ independent candidate-1026 connections.
2. A message fragmented across multiple TCP receives.
3. Multiple application messages in one receive, if produced.
4. At least one neighboring/other PID.
5. Complete RX_CHUNK_HEX and RX_STREAM_HEX evidence.

Never infer framing from recv() boundaries. Promote a framing rule only if it survives repeated captures. Promote PID 1026 only if the candidate field tracks the 1026 label across independent captures and alternatives are eliminated.

Existing 35-byte fixture (evidence, not proof):
```
44344BFF0000001B010018040200023130000000005AFF005C009B0000023131000136
```

Exit criteria:
- [ ] real MCVL client connected
- [ ] 10+ real captures
- [ ] fragmentation/coalescing tested
- [ ] framing supported by repeated evidence
- [ ] PID 1026 supported by repeated evidence
- [ ] no unsupported semantics invented
