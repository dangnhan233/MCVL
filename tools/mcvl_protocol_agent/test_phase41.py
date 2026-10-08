import json
import unittest
from pathlib import Path
from .evidence import EvidenceStore
from .models import PacketCapture
from .phase41 import analyze_phase41, analyze_pid_phase41

class Phase41Test(unittest.TestCase):
    def setUp(self):
        data=json.loads((Path(__file__).parent/"captures/phase4_20261008.json").read_text(encoding="utf-8"))
        self.captures=[PacketCapture(**x) for x in data]

    def test_two_independent_observations_per_pid(self):
        self.assertEqual(len([c for c in self.captures if c.pid == 1026]), 2)
        self.assertEqual(len([c for c in self.captures if c.pid == 1011]), 2)
        self.assertEqual(len({c.remote for c in self.captures if c.pid == 1026}), 2)
        self.assertEqual(len({c.remote for c in self.captures if c.pid == 1011}), 2)

    def test_common_structure_is_verified(self):
        r=analyze_phase41(self.captures)
        self.assertEqual(r.observation_count,4)
        self.assertEqual(r.length_field_offset,4)
        self.assertEqual(r.length_field_width,4)
        self.assertTrue(r.length_rule_verified)
        self.assertEqual(r.pid_field_offset,11)
        self.assertEqual(r.pid_field_width,2)
        self.assertTrue(r.pid_rule_verified)

    def test_per_pid_evidence(self):
        for pid in (1026,1011):
            r=analyze_pid_phase41(self.captures,pid)
            self.assertEqual(r.observation_count,2)
            self.assertTrue(r.length_rule_verified)
            self.assertTrue(r.pid_rule_verified)

    def test_unknowns_remain_unknown(self):
        r=analyze_phase41(self.captures)
        self.assertEqual(r.header_status,"unknown")
        self.assertEqual(r.field_8_10_status,"unknown")
        self.assertEqual(r.checksum_status,"unknown")
        self.assertEqual(r.payload_semantics_status,"unknown")

    def test_evidence_store_phase41(self):
        s=EvidenceStore(self.captures)
        r=s.phase41(1026)
        self.assertEqual(r["observation_count"],2)
        self.assertEqual(r["length_field"],{"offset":4,"width":4,"verified":True})
        self.assertEqual(r["pid_field"],{"offset":11,"width":2,"verified":True})

if __name__=="__main__":
    unittest.main()
