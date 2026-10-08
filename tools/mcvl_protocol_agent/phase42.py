from __future__ import annotations
from dataclasses import dataclass
from .models import PacketCapture

HEADER_SIZE = 8
LENGTH_OFFSET = 4
LENGTH_WIDTH = 4
PID_OFFSET = 11
PID_WIDTH = 2
MIN_FRAME_SIZE = PID_OFFSET + PID_WIDTH

@dataclass(frozen=True)
class FrameCheck:
    valid: bool
    frame_length: int
    declared_body_length: int | None
    pid: int | None
    error: str | None = None

@dataclass(frozen=True)
class StreamFrame:
    offset: int
    length: int
    pid: int
    raw_hex: str

@dataclass(frozen=True)
class StreamCheck:
    valid: bool
    frames: list[StreamFrame]
    consumed: int
    error: str | None = None

def check_frame(raw: bytes, expected_pid: int | None = None) -> FrameCheck:
    if len(raw) < HEADER_SIZE:
        return FrameCheck(False, len(raw), None, None, "truncated_before_length_field")
    declared = int.from_bytes(raw[LENGTH_OFFSET:LENGTH_OFFSET + LENGTH_WIDTH], "big")
    expected_length = HEADER_SIZE + declared
    if len(raw) != expected_length:
        return FrameCheck(False, len(raw), declared, None, "length_mismatch")
    if len(raw) < MIN_FRAME_SIZE:
        return FrameCheck(False, len(raw), declared, None, "truncated_before_pid_field")
    pid = int.from_bytes(raw[PID_OFFSET:PID_OFFSET + PID_WIDTH], "big")
    if expected_pid is not None and pid != expected_pid:
        return FrameCheck(False, len(raw), declared, pid, "pid_mismatch")
    return FrameCheck(True, len(raw), declared, pid)

def split_stream(stream: bytes) -> StreamCheck:
    frames = []
    offset = 0
    while offset < len(stream):
        remaining = len(stream) - offset
        if remaining < HEADER_SIZE:
            return StreamCheck(False, frames, offset, "trailing_truncated_header")
        declared = int.from_bytes(stream[offset + LENGTH_OFFSET:offset + HEADER_SIZE], "big")
        length = HEADER_SIZE + declared
        if length < MIN_FRAME_SIZE:
            return StreamCheck(False, frames, offset, "declared_frame_too_short")
        if remaining < length:
            return StreamCheck(False, frames, offset, "truncated_frame")
        raw = stream[offset:offset + length]
        pid = int.from_bytes(raw[PID_OFFSET:PID_OFFSET + PID_WIDTH], "big")
        frames.append(StreamFrame(offset, length, pid, raw.hex()))
        offset += length
    return StreamCheck(True, frames, offset)

def validate_capture(capture: PacketCapture) -> FrameCheck:
    return check_frame(capture.raw, expected_pid=capture.pid)
