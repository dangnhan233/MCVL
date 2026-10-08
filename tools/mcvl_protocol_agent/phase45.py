from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from .phase42 import split_stream

STREAM_RE = re.compile(r"^(\d+) RX_STREAM_HEX remote=(.*?) hex=([0-9A-Fa-f]*)\s*$")
FRAME_RE = re.compile(r"^(\d+) RX_FRAME_HEX=([0-9A-Fa-f]+)\s*$")


def analyze_stream_log(path: str | Path) -> dict[str, Any]:
    """Analyze explicitly logged complete input streams without treating read chunks as packets."""
    path = Path(path)
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    streams: list[dict[str, Any]] = []
    logged_frames: list[dict[str, Any]] = []

    for line_no, line in enumerate(lines, start=1):
        match = STREAM_RE.match(line)
        if match:
            timestamp = int(match.group(1))
            remote = match.group(2)
            raw_hex = match.group(3)
            try:
                raw = bytes.fromhex(raw_hex)
            except ValueError:
                streams.append({
                    "line": line_no, "timestamp_ms": timestamp, "remote": remote,
                    "bytes": len(raw_hex) // 2, "status": "INVALID_HEX", "frames": [],
                    "error": "stream_hex_decode_failed",
                })
                continue
            check = split_stream(raw)
            streams.append({
                "line": line_no,
                "timestamp_ms": timestamp,
                "remote": remote,
                "bytes": len(raw),
                "status": "VALID" if check.valid else "INVALID_OR_INCOMPLETE",
                "frames": [
                    {"offset": frame.offset, "length": frame.length, "pid": frame.pid,
                     "raw_hex": frame.raw_hex}
                    for frame in check.frames
                ],
                "consumed": check.consumed,
                "error": check.error,
            })
            continue
        match = FRAME_RE.match(line)
        if match:
            logged_frames.append({
                "timestamp_ms": int(match.group(1)),
                "raw_hex": match.group(2).lower(),
                "line": line_no,
            })

    stream_frames = [
        (stream, frame)
        for stream in streams
        for frame in stream.get("frames", [])
    ]
    logged_hex = {frame["raw_hex"] for frame in logged_frames}
    observed_stream_hex = {frame["raw_hex"] for _, frame in stream_frames}
    matched = sorted(logged_hex & observed_stream_hex)
    return {
        "source_log": str(path),
        "phase": "4.5",
        "stream_count": len(streams),
        "valid_stream_count": sum(s["status"] == "VALID" for s in streams),
        "invalid_or_incomplete_stream_count": sum(
            s["status"] != "VALID" for s in streams
        ),
        "stream_frame_count": len(stream_frames),
        "logged_frame_count": len(logged_frames),
        "frame_hex_values_matching_streams": matched,
        "logged_frame_values_not_seen_in_streams": sorted(logged_hex - observed_stream_hex),
        "stream_frame_values_not_seen_as_logged_frames": sorted(observed_stream_hex - logged_hex),
        "streams": streams,
        "limitations": [
            "RX_STREAM_HEX is analyzed as a reconstructed byte stream, not as TCP segment boundaries.",
            "RX_CHUNK_HEX read boundaries are not interpreted as packet boundaries.",
            "A matching frame hex confirms byte equality only; it does not establish request/response semantics.",
            "Checksum and payload semantics remain UNKNOWN.",
        ],
    }


def analyze_stream_logs(paths: list[str | Path]) -> dict[str, Any]:
    reports = [analyze_stream_log(path) for path in paths]
    return {
        "phase": "4.5",
        "files": reports,
        "totals": {
            "files": len(reports),
            "streams": sum(r["stream_count"] for r in reports),
            "valid_streams": sum(r["valid_stream_count"] for r in reports),
            "invalid_or_incomplete_streams": sum(
                r["invalid_or_incomplete_stream_count"] for r in reports
            ),
            "frames_in_streams": sum(r["stream_frame_count"] for r in reports),
        },
        "correlation_status": "BYTE_MATCH_ONLY",
        "checksum_status": "UNKNOWN",
        "payload_semantics_status": "UNKNOWN",
    }
