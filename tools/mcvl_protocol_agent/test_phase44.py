import json
import unittest
from pathlib import Path
from .models import PacketCapture
from .phase44 import analyze_pid_differences, differential_report

class Phase44Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        data=json.loads((Path(__file__).parent/"captures/phase4_20261008.json").read_text())
        cls.captures=[PacketCapture(**x) for x in data]

    def test_current_corpus_has_no_byte_variation_per_pid(self):
        for pid in (1011,1026):
            r=analyze_pid_differences(self.captures,pid)
            self.assertEqual(r.observations,2)
            self.assertEqual(r.unique_frames,1)
            self.assertEqual(r.status,"NO_VARIATION")
            self.assertEqual(r.variable_offsets,[])

    def test_diverse_frames_report_offsets_without_semantics(self):
        base=next(c for c in self.captures if c.pid==1026)
        altered=bytearray(base.raw)
        altered[-1] ^= 0x01
        second=PacketCapture("synthetic-different",base.timestamp_ms+1,base.direction,
            "/127.0.0.1:9999",base.pid,base.session,altered.hex(),base.response_packets)
        r=analyze_pid_differences([base,second],1026)
        self.assertEqual(r.status,"VARIATION_OBSERVED")
        self.assertEqual([x.offset for x in r.variable_offsets],[len(base.raw)-1])
        report=differential_report([base,second])
        self.assertEqual(report["checksum_status"],"UNKNOWN")
        self.assertEqual(report["payload_semantics_status"],"UNKNOWN")

    def test_mixed_lengths_are_not_compared_as_one_cohort(self):
        a=next(c for c in self.captures if c.pid==1011)
        b=PacketCapture("different-length",a.timestamp_ms+1,a.direction,a.remote,a.pid,
            a.session,a.raw_hex[:-2],a.response_packets)
        r=analyze_pid_differences([a,b],1011)
        self.assertEqual(r.status,"MIXED_LENGTHS")
        self.assertEqual(r.common_length,None)

if __name__=="__main__":
    unittest.main()
