import tempfile, zipfile
from pathlib import Path
from .runtime_verification import verify

def test_verify_records_archive_identity():
    with tempfile.TemporaryDirectory() as d:
        z=Path(d)/"runtime.zip"
        with zipfile.ZipFile(z,"w") as f:
            f.writestr("Server.gd","var tcp=StreamPeerTCP.new()\nfunc decode_packet(packet): pass\n")
        r=verify(z)
        assert r["archive_size_bytes"] == z.stat().st_size
        assert len(r["archive_sha256"]) == 64
        assert r["zip_entries"] == 1
        assert r["source_entries"] == ["Server.gd"]
        assert r["top_candidates"][0]["file"] == "Server.gd"
