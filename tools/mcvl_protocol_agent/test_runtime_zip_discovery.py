import tempfile, zipfile
from pathlib import Path
from .runtime_zip_discovery import scan

def test_scan_zip():
    with tempfile.TemporaryDirectory() as d:
        z=Path(d)/'mcvl.zip'
        with zipfile.ZipFile(z,'w') as f:
            f.writestr('game/Server.gd','var s=StreamPeerTCP.new()\ns.accept_client()\nfunc decode_packet(packet): pass\n')
            f.writestr('game/README.md','not scanned')
        result=scan(z)
        assert result['files_scanned']==1
        assert result['top_candidates'][0]['file']=='game/Server.gd'
        assert result['top_candidates'][0]['score']==11
