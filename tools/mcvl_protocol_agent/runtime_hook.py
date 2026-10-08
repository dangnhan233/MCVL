from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Optional
from .adapter import CaptureMetadata, PacketCaptureAdapter
from .models import PacketCapture

@dataclass(frozen=True)
class RuntimeFrameContext:
    """Metadata supplied by the real network runtime at a verified frame boundary."""
    timestamp_ms: int
    remote: str
    pid: int
    session: bool
    capture_id: str

class RuntimeCaptureHook:
    """Single integration boundary for a verified runtime frame.

    The hook is intentionally independent of Godot and server implementation.
    It captures bytes first, then returns the original bytes unchanged so the
    existing runtime can continue its normal decoder/dispatcher path.
    """

    def __init__(
        self,
        adapter: PacketCaptureAdapter,
        *,
        on_capture: Optional[Callable[[PacketCapture], None]] = None,
    ):
        self.adapter = adapter
        self.on_capture = on_capture

    def observe(self, frame: bytes, context: RuntimeFrameContext) -> bytes:
        capture = self.adapter.capture_frame(
            frame,
            CaptureMetadata(
                timestamp_ms=context.timestamp_ms,
                direction="C2S",
                remote=context.remote,
                pid=context.pid,
                session=context.session,
                capture_id=context.capture_id,
            ),
        )
        if self.on_capture is not None:
            self.on_capture(capture)
        return frame
