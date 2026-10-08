from .adapter import CaptureMetadata, PacketCaptureAdapter
from .evidence import EvidenceStore

def test_capture_preserves_raw_frame():
    raw=bytes.fromhex("44 34 4B FF 00 00 00 1B 01 00 18 04 02 00 02 31 30")
    store=EvidenceStore.empty()
    c=PacketCaptureAdapter(store).capture_frame(
        raw, CaptureMetadata(1,"C2S","127.0.0.1:39296",1026,False,"test-1026")
    )
    assert c.raw == raw
    assert c.raw_hex == "44 34 4B FF 00 00 00 1B 01 00 18 04 02 00 02 31 30"
    assert store.captures == [c]

def test_adapter_rejects_text():
    try:
        PacketCaptureAdapter().capture_frame("44 34", CaptureMetadata(1,"C2S","x",1026,False,"x"))
    except TypeError:
        return
    assert False, "expected TypeError"
