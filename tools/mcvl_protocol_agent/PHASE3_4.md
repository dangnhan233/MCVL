# Phase 3.4 — Runtime Source Extraction / Verification

## Status

**BLOCKED_PENDING_ARCHIVE_MATERIALIZATION**

The repository contains `mcvl_godot.zip` with Git blob SHA:
`f667d5dfc927690c2855f6a07088e38bf0c9419c`.

The GitHub connector can identify the blob but cannot decode its binary contents as UTF-8. The conversation Library also does not currently contain the ZIP. Therefore no runtime source has been claimed as extracted or verified.

## Verification procedure

Once the ZIP is uploaded/materialized locally:

```bash
python -m tools.mcvl_protocol_agent.runtime_verification /path/to/mcvl_godot.zip -o runtime_verification.json
```

The verifier records:
- archive byte size;
- SHA-256;
- ZIP entry count;
- source entry list;
- deterministic TCP/UDP/server/packet candidate ranking.

Then inspect the highest-ranked source files and identify the exact:
1. network receive function;
2. complete-frame boundary;
3. packet decoder/dispatcher;
4. safe observational capture hook.

## Non-negotiable rule

Do not connect `PacketCaptureAdapter` to a guessed function. Phase 3.4 is verified only when the actual source file and function are identified from the archive contents.

## Current conclusion

Runtime integration remains pending. Existing protocol evidence is still valid and unchanged.
