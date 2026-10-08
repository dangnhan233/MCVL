from __future__ import annotations
import argparse, hashlib, json, zipfile
from pathlib import Path
from .runtime_zip_discovery import scan

def sha256_file(path: str) -> str:
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""): h.update(chunk)
    return h.hexdigest()

def verify(archive: str) -> dict:
    p=Path(archive)
    if not p.is_file(): raise FileNotFoundError(archive)
    result=scan(p)
    with zipfile.ZipFile(p) as z:
        entries=[i for i in z.infolist() if not i.is_dir()]
        result["archive_size_bytes"]=p.stat().st_size
        result["archive_sha256"]=sha256_file(p)
        result["zip_entries"]=len(entries)
        result["source_entries"]=[i.filename for i in entries if Path(i.filename).suffix.lower() in {'.gd','.gdshader','.tscn','.tres','.cs','.java','.kt','.cpp','.h','.hpp','.py','.json','.txt','.xml'}]
    return result

def main():
    ap=argparse.ArgumentParser(description="Verify and inventory the MCVL runtime ZIP before integration")
    ap.add_argument("archive"); ap.add_argument("-o","--output",default="runtime_verification.json")
    a=ap.parse_args(); r=verify(a.archive)
    Path(a.output).write_text(json.dumps(r,indent=2),encoding="utf-8")
    print(json.dumps({k:r[k] for k in ("archive_size_bytes","archive_sha256","zip_entries","files_scanned","hit_counts","top_candidates")},indent=2))

if __name__=="__main__": main()
