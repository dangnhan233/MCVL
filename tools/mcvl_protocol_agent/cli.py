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
    p.add_argument('--phase43',action='store_true',help='print Phase 4.3 corpus evidence report')
    p.add_argument('--phase44',action='store_true',help='print Phase 4.4 differential byte report')
    p.add_argument('--phase45',action='store_true',help='analyze RX_STREAM_HEX reconstruction and compare with logged frames')
    p.add_argument('--phase46',action='store_true',help='analyze TX_PACKET response payloads and correlate by PID')
    p.add_argument('--min-observations',type=int,default=5)
    p.add_argument('--target-observations',type=int,default=10)
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
    if a.phase43:
        print(json.dumps(store.phase43(a.min_observations,a.target_observations),indent=2,sort_keys=True))
    if a.phase44:
        from .phase44 import differential_report
        print(json.dumps(differential_report(captures),indent=2,sort_keys=True))
    if a.phase45:
        from .phase45 import analyze_stream_logs
        print(json.dumps(analyze_stream_logs(paths),indent=2,sort_keys=True))
    if a.phase46:
        from .phase46 import analyze_response_log
        print(json.dumps({'phase': '4.6', 'files': [analyze_response_log(path) for path in paths]}, indent=2, sort_keys=True))

if __name__=='__main__': main()
