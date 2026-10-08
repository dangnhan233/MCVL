from .adapter import PacketCaptureAdapter
from .evidence import EvidenceStore
from .runtime_hook import RuntimeCaptureHook, RuntimeFrameContext

def test_runtime_hook_returns_identical_frame_and_captures():
    raw=bytes.fromhex("44 34 4B FF 00 00 00 1B 01 00 18 04 02 00 02 31 30 00 00 00 00 5A FF 00 5C 00 9B 00 00 02 31 31 00 01 36")
    store=EvidenceStore.empty()
    seen=[]
    hook=RuntimeCaptureHook(PacketCaptureAdapter(store), on_capture=seen.append)
    returned=hook.observe(raw, RuntimeFrameContext(1791463777338,"127.0.0.1:39296",1026,False,"runtime-1026"))
    assert returned == raw
    assert store.captures[0].raw == raw
    assert seen[0] is store.captures[0]

def test_hook_does_not_mutate_bytearray():
    raw=bytearray.fromhex("44 34 4B FF 00 01")
    original=bytes(raw)
    returned=RuntimeCaptureHook(PacketCaptureAdapter()).observe(
        raw, RuntimeFrameContext(1,"x",1026,False,"x")
    )
    assert bytes(raw) == original
    assert bytes(returned) == original
