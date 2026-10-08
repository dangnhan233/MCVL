from __future__ import annotations
import argparse, json, re, zipfile
from pathlib import PurePosixPath

TEXT_EXT={'.gd','.gdshader','.tscn','.tres','.cs','.java','.kt','.cpp','.h','.hpp','.py','.json','.txt','.xml'}
PATTERNS={'tcp':r'(?i)\b(TCP|StreamPeerTCP|TcpServer|Socket|socket|connect_to_host|listen|accept|NetworkStream)\b','udp':r'(?i)\b(UDP|PacketPeerUDP|Datagram|sendto|recvfrom)\b','packet':r'(?i)\b(packet|opcode|pid|frame|payload|packet_id|message_id|serialize|deserialize|encode|decode)\b','server':r'(?i)\b(server|listener|listen|accept|client_connected|peer_connected)\b'}
WEIGHTS={'tcp':4,'server':4,'packet':3,'udp':2}

def scan(archive):
    archive=str(archive); hits=[]; files=0
    with zipfile.ZipFile(archive) as z:
        for info in z.infolist():
            if info.is_dir(): continue
            suffix=PurePosixPath(info.filename).suffix.lower()
            if suffix not in TEXT_EXT: continue
            files+=1
            try: text=z.read(info).decode('utf-8','ignore')
            except Exception: continue
            for kind,pat in PATTERNS.items():
                for m in re.finditer(pat,text):
                    hits.append({'kind':kind,'file':info.filename,'line':text.count('\n',0,m.start())+1,'match':m.group(0)})
    candidates=[]
    for f in sorted({h['file'] for h in hits}):
        kinds=sorted({h['kind'] for h in hits if h['file']==f})
        score=sum(WEIGHTS[k] for k in kinds)
        candidates.append({'file':f,'kinds':kinds,'score':score})
    candidates.sort(key=lambda x:(-x['score'],x['file']))
    return {'archive':archive,'files_scanned':files,'hit_counts':{k:sum(h['kind']==k for h in hits) for k in PATTERNS},'top_candidates':candidates[:50],'hits':hits}

def main():
    ap=argparse.ArgumentParser(description='Discover MCVL runtime network/packet integration points directly inside a ZIP')
    ap.add_argument('archive'); ap.add_argument('-o','--output',default='runtime_zip_discovery.json')
    a=ap.parse_args(); result=scan(a.archive)
    with open(a.output,'w',encoding='utf-8') as f: json.dump(result,f,indent=2)
    print(json.dumps({k:result[k] for k in ('archive','files_scanned','hit_counts','top_candidates')},indent=2))

if __name__=='__main__': main()
