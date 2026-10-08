from __future__ import annotations
import argparse, json, re
from pathlib import Path
TEXT_EXT={'.gd','.gdshader','.tscn','.tres','.cs','.java','.kt','.cpp','.h','.hpp','.py','.json','.txt','.xml'}
PATTERNS={'tcp':r'(?i)\b(TCP|StreamPeerTCP|TcpServer|Socket|socket|connect_to_host|listen|accept|NetworkStream)\b','udp':r'(?i)\b(UDP|PacketPeerUDP|Datagram|sendto|recvfrom)\b','packet':r'(?i)\b(packet|opcode|pid|frame|payload|packet_id|message_id|serialize|deserialize|encode|decode)\b','server':r'(?i)\b(server|listener|listen|accept|client_connected|peer_connected)\b'}
def scan(root):
 root=Path(root); hits=[]; files=0
 for p in root.rglob('*'):
  if not p.is_file() or p.suffix.lower() not in TEXT_EXT: continue
  files+=1
  try: text=p.read_text(encoding='utf-8',errors='ignore')
  except OSError: continue
  for kind,pat in PATTERNS.items():
   for m in re.finditer(pat,text): hits.append({'kind':kind,'file':str(p.relative_to(root)),'line':text.count('\n',0,m.start())+1,'match':m.group(0)})
 by_kind={k:sum(h['kind']==k for h in hits) for k in PATTERNS}; candidates=[]
 for f in sorted({h['file'] for h in hits}):
  kinds=sorted({h['kind'] for h in hits if h['file']==f}); score=sum({'tcp':4,'server':4,'packet':3,'udp':2}[k] for k in kinds); candidates.append({'file':f,'kinds':kinds,'score':score})
 candidates.sort(key=lambda x:(-x['score'],x['file']))
 return {'root':str(root),'files_scanned':files,'hit_counts':by_kind,'top_candidates':candidates[:50],'hits':hits}
def main():
 ap=argparse.ArgumentParser(description='Discover MCVL runtime network/packet integration points'); ap.add_argument('root'); ap.add_argument('-o','--output',default='runtime_discovery.json'); a=ap.parse_args(); result=scan(a.root); Path(a.output).write_text(json.dumps(result,indent=2),encoding='utf-8'); print(json.dumps({k:result[k] for k in ('root','files_scanned','hit_counts','top_candidates')},indent=2))
if __name__=='__main__': main()
