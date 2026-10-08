from __future__ import annotations
from dataclasses import dataclass
from .models import PacketCapture

@dataclass(frozen=True)
class CaptureMetadata:
    timestamp_ms: int
    direction: str
    remote: str
    pid: int
    session: bool
    capture_id: str

class PacketCaptureAdapter:
    """Observational adapter for a verified runtime frame boundary.

    This class does not decode or mutate protocol bytes. The runtime should
    call capture_frame() only after a complete frame has been reconstructed.
    """

    def __init__(self, evidence_store=None):
        self.evidence_store = evidence_store

    @staticmethod
    def normalize_hex(raw: bytes) -> str:
        return raw.hex(" ").upper()

    def capture_frame(self, raw: bytes, metadata: CaptureMetadata,
                      response_packets: int = 0) -> PacketCapture:
        if not isinstance(raw, (bytes, bytearray, memoryview)):
            raise TypeError("raw must be bytes-like")
        payload = bytes(raw)
        capture = PacketCapture(
            capture_id=metadata.capture_id,
            timestamp_ms=metadata.timestamp_ms,
            direction=metadata.direction,
            remote=metadata.remote,
            pid=metadata.pid,
            session=metadata.session,
            raw_hex=self.normalize_hex(payload),
            response_packets=response_packets,
        )
        if self.evidence_store is not None:
            self.evidence_store.add(capture)
        return capture
