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

def load_capture(path: str | Path) -> PacketCapture:
    return PacketCapture(**json.loads(Path(path).read_text(encoding="utf-8")))
