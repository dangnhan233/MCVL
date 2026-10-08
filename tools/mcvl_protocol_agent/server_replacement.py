from __future__ import annotations

import argparse
import socket
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 9001
BUFFER_SIZE = 64 * 1024


@dataclass(frozen=True)
class RxChunk:
    connection_id: int
    sequence: int
    timestamp_ms: int
    raw: bytes


class MCVLEmbeddedServer:
    """Evidence-first TCP capture server.

    This replaces the missing original embedded-server source. It deliberately
    does not claim a protocol frame boundary. TCP recv() chunks are logged as
    chunks; multiple chunks are accumulated as one connection stream.

    PID 1026 is NOT inferred here. A downstream analyzer may compare repeated
    captures and only promote a PID/framing hypothesis when evidence supports it.
    """

    def __init__(
        self,
        host: str = DEFAULT_HOST,
        port: int = DEFAULT_PORT,
        capture_dir: str | Path | None = None,
        logger=None,
    ):
        self.host = host
        self.port = port
        self.capture_dir = Path(capture_dir) if capture_dir else None
        if self.capture_dir:
            self.capture_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logger
        self.server: Optional[socket.socket] = None
        self.stop_event = threading.Event()
        self._connection_seq = 0
        self._lock = threading.Lock()

    def start(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((self.host, self.port))
        s.listen(16)
        self.server = s
        self._log("SERVER_STARTED host=%s port=%d", self.host, self.port)
        while not self.stop_event.is_set():
            s.settimeout(0.5)
            try:
                conn, addr = s.accept()
            except socket.timeout:
                continue
            with self._lock:
                self._connection_seq += 1
                connection_id = self._connection_seq
            threading.Thread(
                target=self._client,
                args=(conn, addr, connection_id),
                daemon=True,
            ).start()

    def stop(self):
        self.stop_event.set()
        if self.server:
            try:
                self.server.close()
            except OSError:
                pass

    def _client(self, conn: socket.socket, addr, connection_id: int):
        remote = f"/{addr[0]}:{addr[1]}"
        self._log("CLIENT_ACCEPT id=%d remote=%s", connection_id, remote)
        chunks: list[bytes] = []
        sequence = 0
        with conn:
            while not self.stop_event.is_set():
                try:
                    data = conn.recv(BUFFER_SIZE)
                except (ConnectionResetError, OSError) as exc:
                    self._log("RX_ERROR id=%d error=%s", connection_id, type(exc).__name__)
                    break
                if not data:
                    break
                sequence += 1
                chunks.append(data)
                ts = int(time.time() * 1000)
                self._log(
                    "RX_CHUNK id=%d seq=%d bytes=%d",
                    connection_id,
                    sequence,
                    len(data),
                )
                self._log("RX_CHUNK_HEX id=%d seq=%d hex=%s", connection_id, sequence, data.hex().upper())
                self._write_chunk(RxChunk(connection_id, sequence, ts, data))
        stream = b"".join(chunks)
        self._log("RX_STREAM id=%d chunks=%d bytes=%d", connection_id, len(chunks), len(stream))
        if stream:
            self._log("RX_STREAM_HEX id=%d hex=%s", connection_id, stream.hex().upper())
        self._log("FRAME_BOUNDARY status=UNRESOLVED id=%d", connection_id)
        self._log("PID_1026 status=UNRESOLVED id=%d", connection_id)
        self._log("FRAME_HANDLED packets=0 session=false")
        self._log("TX_RESPONSE packets=0")

    def _write_chunk(self, chunk: RxChunk):
        if not self.capture_dir:
            return
        path = self.capture_dir / f"conn_{chunk.connection_id:04d}.jsonl"
        line = (
            f'{{"connection_id":{chunk.connection_id},'
            f'"sequence":{chunk.sequence},'
            f'"timestamp_ms":{chunk.timestamp_ms},'
            f'"bytes":{len(chunk.raw)},'
            f'"hex":"{chunk.raw.hex().upper()}"}}\n'
        )
        with path.open("a", encoding="utf-8") as fh:
            fh.write(line)

    def _log(self, msg: str, *args):
        print(f"{int(time.time() * 1000)} {msg % args}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default=DEFAULT_HOST)
    ap.add_argument("--port", type=int, default=DEFAULT_PORT)
    ap.add_argument("--capture-dir", default=None)
    args = ap.parse_args()
    server = MCVLEmbeddedServer(args.host, args.port, args.capture_dir)
    try:
        server.start()
    except KeyboardInterrupt:
        server.stop()


if __name__ == "__main__":
    main()
