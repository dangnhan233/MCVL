from dataclasses import dataclass, field
from typing import Any

@dataclass(frozen=True)
class PacketCapture:
    capture_id: str
    timestamp_ms: int
    direction: str
    remote: str
    pid: int
    session: bool
    raw_hex: str
    response_packets: int = 0
    @property
    def raw(self) -> bytes:
        return bytes.fromhex(self.raw_hex)

@dataclass
class FieldHypothesis:
    name: str
    offset: int
    length: int
    raw_hex: str
    confidence: float = 0.0
    status: str = "unknown"
    evidence: list[str] = field(default_factory=list)

@dataclass
class AnalysisReport:
    capture_id: str
    pid: int
    frame_length: int
    header_candidates: list[FieldHypothesis] = field(default_factory=list)
    fields: list[FieldHypothesis] = field(default_factory=list)
    checksum_candidates: list[FieldHypothesis] = field(default_factory=list)
    known: list[str] = field(default_factory=list)
    unknown: list[str] = field(default_factory=list)
    hypotheses: list[str] = field(default_factory=list)
    required_evidence: list[str] = field(default_factory=list)
    response_required: bool = True
    response_known: bool = False
    def to_dict(self) -> dict[str, Any]:
        def fd(x): return {"name":x.name,"offset":x.offset,"length":x.length,"raw_hex":x.raw_hex,"confidence":x.confidence,"status":x.status,"evidence":x.evidence}
        return {"capture_id":self.capture_id,"pid":self.pid,"frame_length":self.frame_length,"header_candidates":[fd(x) for x in self.header_candidates],"fields":[fd(x) for x in self.fields],"checksum_candidates":[fd(x) for x in self.checksum_candidates],"known":self.known,"unknown":self.unknown,"hypotheses":self.hypotheses,"required_evidence":self.required_evidence,"response_required":self.response_required,"response_known":self.response_known}
