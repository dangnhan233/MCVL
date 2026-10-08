import json
import unittest
from pathlib import Path
from .models import PacketCapture
from .phase42 import check_frame, split_stream, validate_capture

class Phase42Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        data=json.loads((Path(__file__).parent/"captures/phase4_20261008.json").read_text())
        cls.captures=[PacketCapture(**x) for x in data]

    def test_all_phase41_captures_validate(self):
        for c in self.captures:
            r=validate_capture(c)
            self.assertTrue(r.valid, (c.capture_id, r))
            self.assertEqual(r.pid,c.pid)
            self.assertEqual(r.frame_length,len(c.raw))

    def test_split_two_frames(self):
        stream=self.captures[0].raw+self.captures[1].raw
        r=split_stream(stream)
        self.assertTrue(r.valid)
        self.assertEqual(r.consumed,len(stream))
        self.assertEqual([x.pid for x in r.frames],[1026,1011])
        self.assertEqual([x.length for x in r.frames],[35,25])
        self.assertEqual([x.offset for x in r.frames],[0,35])

    def test_split_all_four_frames(self):
        stream=b"".join(c.raw for c in self.captures)
        r=split_stream(stream)
        self.assertTrue(r.valid)
        self.assertEqual(len(r.frames),4)
        self.assertEqual([x.pid for x in r.frames],[1026,1011,1026,1011])
        self.assertEqual([x.length for x in r.frames],[35,25,35,25])

    def test_truncated_frame_rejected(self):
        raw=self.captures[0].raw
        r=split_stream(raw[:-1])
        self.assertFalse(r.valid)
        self.assertEqual(r.error,"truncated_frame")

    def test_length_mismatch_rejected(self):
        raw=bytearray(self.captures[0].raw)
        raw[7]=0x1C
        r=check_frame(bytes(raw))
        self.assertFalse(r.valid)
        self.assertEqual(r.error,"length_mismatch")

    def test_pid_mismatch_rejected(self):
        r=validate_capture(self.captures[0])
        self.assertTrue(r.valid)
        bad=PacketCapture(self.captures[0].capture_id, self.captures[0].timestamp_ms,
            self.captures[0].direction,self.captures[0].remote,1011,self.captures[0].session,
            self.captures[0].raw_hex,self.captures[0].response_packets)
        x=validate_capture(bad)
        self.assertFalse(x.valid)
        self.assertEqual(x.error,"pid_mismatch")

    def test_no_semantic_inference(self):
        r=validate_capture(self.captures[0])
        self.assertTrue(r.valid)
        # Validator only checks structural length/PID; it never exposes a
        # checksum or payload interpretation.
        self.assertEqual(r.declared_body_length,27)

if __name__=="__main__":
    unittest.main()
