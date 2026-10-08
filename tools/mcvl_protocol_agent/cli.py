from __future__ import annotations
import argparse, json
from pathlib import Path
from .ingest import ingest_paths, write_json
from .evidence import EvidenceStore

def main():
    p=argparse.ArgumentParser(description='Ingest MCVL debug logs into protocol evidence captures')
    p.add_argument('logs',nargs='+',help='log files or glob patterns')
    p.add_argument('-o','--output',default='mcvl_captures.json')
    p.add_argument('--pid',type=int,help='show summary for one PID')
    a=p.parse_args()
    paths=[]
    for item in a.logs:
        matches=list(Path('.').glob(item))
        paths.extend(matches or [Path(item)])
    captures=ingest_paths(paths)
    write_json(captures,a.output)
    store=EvidenceStore(captures)
    pids=sorted({c.pid for c in captures})
    print(json.dumps({'files':[str(x) for x in paths],'captures':len(captures),'pids':pids,'output':a.output},indent=2))
    for pid in ([a.pid] if a.pid is not None else pids): print(json.dumps(store.summary(pid),sort_keys=True))

if __name__=='__main__': main()
