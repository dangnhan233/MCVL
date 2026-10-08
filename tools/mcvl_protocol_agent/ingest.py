from __future__ import annotations
import re, json
from pathlib import Path
from .models import PacketCapture

START_RE=re.compile(r'^(\d+) === MCVL EMBEDDED SERVER DEBUG START ===')
ACCEPT_RE=re.compile(r'^(\d+) CLIENT_ACCEPT remote=(.+)$')
FRAME_RE=re.compile(r'^(\d+) RX_FRAME bytes=(\d+)$')
HEX_RE=re.compile(r'^(\d+) RX_FRAME_HEX=([0-9A-Fa-f]+)$')
PID_RE=re.compile(r'^(\d+) RX_PACKET pid=(\d+) session=(true|false)$')
TX_RE=re.compile(r'^(\d+) TX_RESPONSE packets=(\d+)$')

def ingest_log(path: str | Path) -> list[PacketCapture]:
    path=Path(path); lines=path.read_text(encoding='utf-8',errors='replace').splitlines()
    state={'remote':'unknown','frame_len':None,'hex':None,'pid':None,'session':False,'frame_ts':0,'response_packets':0}
    out=[]; seq=0
    for line in lines:
        for rx in (START_RE,ACCEPT_RE,FRAME_RE,HEX_RE,PID_RE,TX_RE):
            m=rx.match(line)
            if not m: continue
            if rx is ACCEPT_RE: state['remote']=m.group(2)
            elif rx is FRAME_RE: state['frame_len']=int(m.group(2)); state['frame_ts']=int(m.group(1)); state['hex']=None; state['pid']=None; state['response_packets']=0
            elif rx is HEX_RE: state['hex']=m.group(2)
            elif rx is PID_RE: state['pid']=int(m.group(2)); state['session']=m.group(3)=='true'
            elif rx is TX_RE and state['hex'] and state['pid'] is not None:
                state['response_packets']=int(m.group(2)); seq+=1
                raw=bytes.fromhex(state['hex'])
                if state['frame_len'] is None or state['frame_len']==len(raw):
                    out.append(PacketCapture(f'{path.stem}_{seq}',state['frame_ts'],'C2S',state['remote'],state['pid'],state['session'],state['hex'],state['response_packets']))
            break
    return out

def ingest_paths(paths: list[str | Path]) -> list[PacketCapture]:
    result=[]
    for p in paths: result.extend(ingest_log(p))
    return result

def write_json(captures: list[PacketCapture], output: str | Path):
    Path(output).write_text(json.dumps([c.__dict__ for c in captures],indent=2),encoding='utf-8')
