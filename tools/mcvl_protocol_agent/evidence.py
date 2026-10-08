from __future__ import annotations
from dataclasses import dataclass
import json
from pathlib import Path
from .models import PacketCapture

@dataclass
class EvidenceStore:
    captures: list[PacketCapture]
    @classmethod
    def empty(cls): return cls([])
    def add(self, capture: PacketCapture): self.captures.append(capture)
    def for_pid(self, pid: int): return [c for c in self.captures if c.pid == pid]
    def summary(self, pid: int):
        xs=self.for_pid(pid)
        return {"pid":pid,"capture_count":len(xs),"directions":sorted({x.direction for x in xs}),"frame_lengths":sorted({len(x.raw) for x in xs}),"responses":sum(x.response_packets for x in xs),"unique_frames":len({x.raw_hex for x in xs})}

    def phase41(self, pid: int | None = None):
        from .phase41 import analyze_phase41
        xs = self.captures if pid is None else self.for_pid(pid)
        r = analyze_phase41(xs)
        return {
            "observation_count": r.observation_count,
            "pids": r.pids,
            "length_field": {"offset": r.length_field_offset, "width": r.length_field_width, "verified": r.length_rule_verified},
            "pid_field": {"offset": r.pid_field_offset, "width": r.pid_field_width, "verified": r.pid_rule_verified},
            "header": r.header_status,
            "field_8_10": r.field_8_10_status,
            "checksum": r.checksum_status,
            "payload_semantics": r.payload_semantics_status,
            "notes": r.notes,
        }

def load_capture(path: str | Path) -> PacketCapture:
    return PacketCapture(**json.loads(Path(path).read_text(encoding="utf-8")))
