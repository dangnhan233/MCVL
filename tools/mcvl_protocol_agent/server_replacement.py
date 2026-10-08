from __future__ import annotations
import argparse
import logging
import socket
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

DEFAULT_HOST="127.0.0.1"
DEFAULT_PORT=9001
OBSERVED_PID=1026

@dataclass(frozen=True)
class Frame:
    raw: bytes

class MCVLEmbeddedServer:
    """Deterministic TCP compatibility server for the observed MCVL debug contract.

    This is a replacement for the missing embedded-server source. It deliberately
    treats payload bytes as opaque. The only PID recognition currently supported
    is the observed fixture value 0x0402 (1026) at byte offsets 10:12; this is
    labeled as a capture-specific candidate and must not be promoted to protocol
    semantics without additional evidence.
    """

    def __init__(self, host=DEFAULT_HOST, port=DEFAULT_PORT, logger=None):
        self.host=host
        self.port=port
        self.logger=logger or logging.getLogger("mcvl_server")
        self.server: Optional[socket.socket]=None
        self.stop_event=threading.Event()

    def start(self):
        s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        s.bind((self.host,self.port))
        s.listen(16)
        self.server=s
        self._log("SERVER_STARTED port=%d",self.port)
        while not self.stop_event.is_set():
            s.settimeout(0.5)
            try: conn,addr=s.accept()
            except socket.timeout: continue
            threading.Thread(target=self._client,args=(conn,addr),daemon=True).start()

    def stop(self):
        self.stop_event.set()
        if self.server:
            try:self.server.close()
            except OSError:pass

    def _client(self,conn,addr):
        remote=f"/{addr[0]}:{addr[1]}"
        self._log("CLIENT_ACCEPT remote=%s",remote)
        with conn:
            data=conn.recv(64*1024)
            if not data: return
            frame=Frame(data)
            self._log("RX_FRAME bytes=%d",len(frame.raw))
            self._log("RX_FRAME_HEX=%s",frame.raw.hex().upper())
            pid=self._observed_pid_candidate(frame.raw)
            if pid is not None:
                self._log("RX_PACKET pid=%d session=false",pid)
            else:
                self._log("RX_PACKET pid=UNKNOWN session=false")
            self._log("FRAME_HANDLED packets=0 session=false")
            self._log("TX_RESPONSE packets=0")

    @staticmethod
    def _observed_pid_candidate(raw: bytes) -> Optional[int]:
        # Evidence-only recognition for the exact observed PID candidate.
        if len(raw)>=12 and raw[10:12]==b"\x04\x02":
            return OBSERVED_PID
        return None

    def _log(self,msg,*args):
        now=int(time.time()*1000)
        print(f"{now} {msg % args}",flush=True)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--host",default=DEFAULT_HOST)
    ap.add_argument("--port",type=int,default=DEFAULT_PORT)
    a=ap.parse_args()
    server=MCVLEmbeddedServer(a.host,a.port)
    try: server.start()
    except KeyboardInterrupt: server.stop()

if __name__=="__main__":
    main()
