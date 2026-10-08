from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass
from .models import PacketCapture

@dataclass(frozen=True)
class OffsetDiff:
    offset: int
    observed_values: list[str]
    observation_count: int
    variable: bool

@dataclass(frozen=True)
class PidDifferentialReport:
    pid: int
    observations: int
    unique_frames: int
    common_length: int | None
    comparable_offsets: int
    invariant_offsets: list[int]
    variable_offsets: list[OffsetDiff]
    status: str
    notes: list[str]

def analyze_pid_differences(captures: list[PacketCapture], pid: int) -> PidDifferentialReport:
    xs = [c for c in captures if c.pid == pid]
    unique = {c.raw for c in xs}
    lengths = {len(c.raw) for c in xs}
    if not xs:
        return PidDifferentialReport(pid,0,0,None,0,[],[],"NO_EVIDENCE",["No captures for this PID."])
    if len(lengths) != 1:
        return PidDifferentialReport(pid,len(xs),len(unique),None,0,[],[],"MIXED_LENGTHS",[
            "Frames have different lengths; byte offsets are not compared across the entire group.",
            "Analyze each frame-length cohort separately before assigning any field hypotheses."
        ])
    n = next(iter(lengths))
    invariant=[]; variable=[]
    for offset in range(n):
        values=sorted({c.raw[offset] for c in xs})
        if len(values)==1:
            invariant.append(offset)
        else:
            variable.append(OffsetDiff(offset,[f"{v:02X}" for v in values],len(xs),True))
    if len(unique) < 2:
        status="NO_VARIATION"
        notes=["All observations are byte-identical; differential analysis cannot distinguish constants from fields."]
    else:
        status="VARIATION_OBSERVED"
        notes=["Variable offsets are candidates for further investigation, not decoded field semantics."]
    notes += [
        "This report does not identify checksums, counters, IDs, flags, or payload meanings.",
        "Repeated captures of identical bytes count as observations but do not add byte-level variation."
    ]
    return PidDifferentialReport(pid,len(xs),len(unique),n,n,invariant,variable,status,notes)

def differential_report(captures: list[PacketCapture]) -> dict:
    pids=sorted({c.pid for c in captures})
    results=[]
    for pid in pids:
        r=analyze_pid_differences(captures,pid)
        results.append({
            "pid":r.pid,"observations":r.observations,"unique_frames":r.unique_frames,
            "common_length":r.common_length,"comparable_offsets":r.comparable_offsets,
            "invariant_offsets":r.invariant_offsets,
            "variable_offsets":[{"offset":x.offset,"observed_values":x.observed_values,
                                 "observation_count":x.observation_count,"variable":x.variable}
                                for x in r.variable_offsets],
            "status":r.status,"notes":r.notes
        })
    return {
        "phase":"4.4",
        "pids":results,
        "checksum_status":"UNKNOWN",
        "payload_semantics_status":"UNKNOWN",
        "interpretation":"Byte variation is reported only as an observation; no field semantics are inferred."
    }
