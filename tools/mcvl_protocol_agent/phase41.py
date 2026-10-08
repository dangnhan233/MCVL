from __future__ import annotations
from dataclasses import dataclass, field
from .models import PacketCapture

@dataclass(frozen=True)
class StructuralEvidence:
    observation_count: int
    pids: list[int]
    length_field_offset: int | None
    length_field_width: int
    length_rule_verified: bool
    pid_field_offset: int | None
    pid_field_width: int
    pid_rule_verified: bool
    header_status: str = "unknown"
    field_8_10_status: str = "unknown"
    checksum_status: str = "unknown"
    payload_semantics_status: str = "unknown"
    notes: list[str] = field(default_factory=list)

def analyze_phase41(captures: list[PacketCapture]) -> StructuralEvidence:
    """
    Deterministic Phase 4.1 structural checker.

    It verifies only repeated byte-position relationships supported by the
    supplied captures. It does not assign semantics to the header, bytes
    8..10, checksum, or payload.
    """
    xs = [c for c in captures if len(c.raw) >= 13]
    length_ok = bool(xs) and all(
        int.from_bytes(c.raw[4:8], "big") == len(c.raw) - 8 for c in xs
    )
    pid_ok = bool(xs) and all(
        int.from_bytes(c.raw[11:13], "big") == c.pid for c in xs
    )
    pids = sorted({c.pid for c in xs})
    notes = []
    if length_ok:
        notes.append("bytes[4:8] consistently equal frame_length - 8 across supplied observations")
    else:
        notes.append("bytes[4:8] length relationship is not consistent across supplied observations")
    if pid_ok:
        notes.append("bytes[11:13] consistently equal logged PID across supplied observations")
    else:
        notes.append("bytes[11:13] PID relationship is not consistent across supplied observations")
    notes.append("bytes[0:4] header/prefix semantics remain unknown")
    notes.append("bytes[8:11] semantics remain unknown")
    notes.append("checksum algorithm/status remains unknown")
    notes.append("payload semantics remain unknown")
    return StructuralEvidence(
        observation_count=len(xs),
        pids=pids,
        length_field_offset=4 if length_ok else None,
        length_field_width=4,
        length_rule_verified=length_ok,
        pid_field_offset=11 if pid_ok else None,
        pid_field_width=2,
        pid_rule_verified=pid_ok,
        notes=notes,
    )

def analyze_pid_phase41(captures: list[PacketCapture], pid: int) -> StructuralEvidence:
    return analyze_phase41([c for c in captures if c.pid == pid])
