from __future__ import annotations

import re
from pathlib import Path
from typing import Any

START_RE = re.compile(r"^(\d+) === MCVL EMBEDDED SERVER DEBUG START ===")
ACCEPT_RE = re.compile(r"^(\d+) CLIENT_ACCEPT remote=(.+)$")
RX_FRAME_RE = re.compile(r"^(\d+) RX_FRAME_HEX=([0-9A-Fa-f]+)$")
RX_PID_RE = re.compile(r"^(\d+) RX_PACKET pid=(\d+) session=(true|false)$")
TX_PACKET_RE = re.compile(
    r"^(\d+) TX_PACKET pid=(\d+) error=(true|false) data_hex=([0-9A-Fa-f]*)$"
)
TX_SUMMARY_RE = re.compile(r"^(\d+) TX_RESPONSE packets=(\d+).*$")


def _decode_utf8_hex(raw_hex: str) -> tuple[str | None, str | None]:
    try:
        return bytes.fromhex(raw_hex).decode("utf-8"), None
    except (ValueError, UnicodeDecodeError) as exc:
        return None, type(exc).__name__


def analyze_response_log(path: str | Path) -> dict[str, Any]:
    """Extract request/response observations and decode UTF-8 response payloads when valid."""
    path = Path(path)
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    remote = "unknown"
    pending: dict[str, Any] | None = None
    requests: list[dict[str, Any]] = []
    responses: list[dict[str, Any]] = []
    response_summaries: list[dict[str, Any]] = []

    for line_no, line in enumerate(lines, start=1):
        m = ACCEPT_RE.match(line)
        if m:
            remote = m.group(2)
            continue
        m = RX_FRAME_RE.match(line)
        if m:
            pending = {
                "timestamp_ms": int(m.group(1)),
                "remote": remote,
                "frame_hex": m.group(2).lower(),
                "frame_line": line_no,
                "pid": None,
                "session": None,
            }
            continue
        m = RX_PID_RE.match(line)
        if m:
            if pending is not None:
                pending["pid"] = int(m.group(2))
                pending["session"] = m.group(3) == "true"
                pending["pid_line"] = line_no
                requests.append(pending)
                pending = None
            else:
                requests.append({
                    "timestamp_ms": int(m.group(1)), "remote": remote,
                    "pid": int(m.group(2)), "session": m.group(3) == "true",
                    "frame_hex": None, "frame_line": None, "pid_line": line_no,
                })
            continue
        m = TX_PACKET_RE.match(line)
        if m:
            timestamp = int(m.group(1))
            pid = int(m.group(2))
            error = m.group(3) == "true"
            raw_hex = m.group(4).lower()
            decoded, decode_error = _decode_utf8_hex(raw_hex)
            responses.append({
                "timestamp_ms": timestamp,
                "pid": pid,
                "error": error,
                "data_hex": raw_hex,
                "data_bytes": len(raw_hex) // 2,
                "utf8_text": decoded,
                "utf8_decode_error": decode_error,
                "line": line_no,
            })
            continue
        m = TX_SUMMARY_RE.match(line)
        if m:
            response_summaries.append({
                "timestamp_ms": int(m.group(1)),
                "packet_count": int(m.group(2)),
                "line": line_no,
            })

    request_pids = {r["pid"] for r in requests if r["pid"] is not None}
    response_pids = {r["pid"] for r in responses}
    return {
        "phase": "4.6",
        "source_log": str(path),
        "request_count": len(requests),
        "response_packet_count": len(responses),
        "requests": requests,
        "responses": responses,
        "response_summaries": response_summaries,
        "pid_overlap": sorted(request_pids & response_pids),
        "request_pids_without_response": sorted(request_pids - response_pids),
        "response_pids_without_request": sorted(response_pids - request_pids),
        "interpretation_limits": [
            "Timestamp proximity and PID overlap are evidence for correlation, not proof of a protocol-level request/response transaction ID.",
            "UTF-8 decoding is attempted for payload bytes but does not imply the entire payload is text.",
            "The session flag is reported as logged; its protocol meaning is not inferred.",
            "Checksum and payload field semantics remain UNKNOWN unless independently verified.",
        ],
    }
