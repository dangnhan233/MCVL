import json
import unittest
from pathlib import Path
from .models import PacketCapture
from .phase43 import analyze_corpus, report_to_dict

class Phase43Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        data=json.loads((Path(__file__).parent/"captures/phase4_20261008.json").read_text())
        cls.captures=[PacketCapture(**x) for x in data]

    def test_current_corpus_is_consistent_but_not_large_enough(self):
        r=analyze_corpus(self.captures)
        self.assertEqual(r.total_observations,4)
        self.assertEqual(r.pids,[1011,1026])
        self.assertTrue(r.global_length_rule_valid)
        self.assertTrue(r.global_pid_rule_valid)
        self.assertFalse(r.ready_for_payload_analysis)
        self.assertEqual(r.multi_frame_stream_evidence,"UNRESOLVED")
        self.assertEqual(r.checksum_status,"UNKNOWN")
        self.assertEqual(r.payload_semantics_status,"UNKNOWN")
        by_pid={x.pid:x for x in r.per_pid}
        self.assertEqual(by_pid[1026].observations,2)
        self.assertEqual(by_pid[1011].observations,2)
        self.assertEqual(by_pid[1026].unique_frames,1)
        self.assertEqual(by_pid[1011].unique_frames,1)
        self.assertEqual(by_pid[1026].collection_status,"INSUFFICIENT")

    def test_synthetic_diverse_corpus_reaches_minimum(self):
        xs=[]
        for i in range(5):
            for base in self.captures[:2]:
                raw=bytearray(base.raw)
                raw[-1]=(raw[-1]+i)&0xff
                xs.append(PacketCapture(
                    f"{base.capture_id}_v{i}", base.timestamp_ms+i, base.direction,
                    base.remote+f"/{i}", base.pid, base.session, raw.hex(), base.response_packets))
        r=analyze_corpus(xs)
        self.assertTrue(r.global_length_rule_valid)
        self.assertTrue(r.global_pid_rule_valid)
        self.assertTrue(r.ready_for_payload_analysis)
        self.assertEqual({x.collection_status for x in r.per_pid},{"MINIMUM_REACHED"})
        self.assertEqual({x.unique_frames for x in r.per_pid},{5})

    def test_report_is_serializable(self):
        d=report_to_dict(analyze_corpus(self.captures))
        self.assertEqual(d["total_observations"],4)
        self.assertEqual(d["checksum_status"],"UNKNOWN")

if __name__=="__main__":
    unittest.main()
