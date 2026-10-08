from __future__ import annotations
from dataclasses import dataclass, field
from collections import Counter, defaultdict
from .models import PacketCapture
from .phase42 import validate_capture

MIN_OBSERVATIONS_PER_PID = 5
TARGET_OBSERVATIONS_PER_PID = 10

@dataclass(frozen=True)
class CorpusPidReport:
    pid: int
    observations: int
    unique_frames: int
    unique_connections: int
    frame_lengths: list[int]
    structural_valid: bool
    length_rule_failures: int
    pid_rule_failures: int
    collection_status: str
    notes: list[str] = field(default_factory=list)

@dataclass(frozen=True)
class Phase43Report:
    total_observations: int
    pids: list[int]
    per_pid: list[CorpusPidReport]
    global_length_rule_valid: bool
    global_pid_rule_valid: bool
    multi_frame_stream_evidence: str
    checksum_status: str
    payload_semantics_status: str
    ready_for_payload_analysis: bool
    notes: list[str] = field(default_factory=list)

def analyze_corpus(
    captures: list[PacketCapture],
    min_observations_per_pid: int = MIN_OBSERVATIONS_PER_PID,
    target_observations_per_pid: int = TARGET_OBSERVATIONS_PER_PID,
) -> Phase43Report:
    by_pid: dict[int, list[PacketCapture]] = defaultdict(list)
    for capture in captures:
        by_pid[capture.pid].append(capture)

    reports: list[CorpusPidReport] = []
    all_length_ok = True
    all_pid_ok = True

    for pid in sorted(by_pid):
        xs = by_pid[pid]
        checks = [validate_capture(x) for x in xs]
        length_failures = sum(
            1 for x, r in zip(xs, checks)
            if r.declared_body_length is None or len(x.raw) != 8 + r.declared_body_length
        )
        pid_failures = sum(
            1 for x, r in zip(xs, checks)
            if not r.valid or r.pid != pid
        )
        structural_valid = all(r.valid and r.pid == pid for r in checks)
        all_length_ok &= length_failures == 0
        all_pid_ok &= pid_failures == 0

        unique_frames = len({x.raw_hex for x in xs})
        unique_connections = len({(x.remote, x.timestamp_ms) for x in xs})
        lengths = sorted({len(x.raw) for x in xs})

        if len(xs) < min_observations_per_pid:
            collection_status = "INSUFFICIENT"
        elif len(xs) < target_observations_per_pid:
            collection_status = "MINIMUM_REACHED"
        else:
            collection_status = "TARGET_REACHED"

        notes = [
            f"need {max(0, target_observations_per_pid - len(xs))} more observations to reach target"
        ]
        if unique_frames < 2:
            notes.append("payload/frame diversity is currently low")
        if unique_connections < len(xs):
            notes.append("some observations share the same remote/timestamp identity")

        reports.append(CorpusPidReport(
            pid=pid,
            observations=len(xs),
            unique_frames=unique_frames,
            unique_connections=unique_connections,
            frame_lengths=lengths,
            structural_valid=structural_valid,
            length_rule_failures=length_failures,
            pid_rule_failures=pid_failures,
            collection_status=collection_status,
            notes=notes,
        ))

    ready = (
        bool(reports)
        and all(r.observations >= min_observations_per_pid for r in reports)
        and all(r.structural_valid and r.unique_frames >= 2 for r in reports)
        and all_length_ok
        and all_pid_ok
    )

    notes = [
        "Phase 4.3 evaluates evidence quantity and structural consistency only.",
        "RX_CHUNK read boundaries are not TCP packet boundaries.",
        "Checksum remains unknown until an independently supported algorithm is demonstrated.",
        "Payload semantics remain unknown until supported by repeated evidence.",
    ]
    if any(r.unique_frames < 2 for r in reports):
        notes.append("At least one PID has fewer than 2 unique frames; differential payload analysis is not yet informative.")
    if not ready:
        notes.append("Do not promote payload semantics or checksum from the current corpus.")

    return Phase43Report(
        total_observations=len(captures),
        pids=sorted(by_pid),
        per_pid=reports,
        global_length_rule_valid=all_length_ok,
        global_pid_rule_valid=all_pid_ok,
        multi_frame_stream_evidence="UNRESOLVED",
        checksum_status="UNKNOWN",
        payload_semantics_status="UNKNOWN",
        ready_for_payload_analysis=ready,
        notes=notes,
    )

def report_to_dict(report: Phase43Report) -> dict:
    return {
        "total_observations": report.total_observations,
        "pids": report.pids,
        "per_pid": [
            {
                "pid": x.pid,
                "observations": x.observations,
                "unique_frames": x.unique_frames,
                "unique_connections": x.unique_connections,
                "frame_lengths": x.frame_lengths,
                "structural_valid": x.structural_valid,
                "length_rule_failures": x.length_rule_failures,
                "pid_rule_failures": x.pid_rule_failures,
                "collection_status": x.collection_status,
                "notes": x.notes,
            } for x in report.per_pid
        ],
        "global_length_rule_valid": report.global_length_rule_valid,
        "global_pid_rule_valid": report.global_pid_rule_valid,
        "multi_frame_stream_evidence": report.multi_frame_stream_evidence,
        "checksum_status": report.checksum_status,
        "payload_semantics_status": report.payload_semantics_status,
        "ready_for_payload_analysis": report.ready_for_payload_analysis,
        "notes": report.notes,
    }
