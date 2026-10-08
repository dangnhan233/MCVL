import unittest
from pathlib import Path
from .evidence import EvidenceStore, load_capture

class EvidenceTest(unittest.TestCase):
    def test_fixture_summary(self):
        p=Path(__file__).parent/"captures/1026_194923.json"
        c=load_capture(p); s=EvidenceStore([c]).summary(1026)
        self.assertEqual(s["capture_count"],1); self.assertEqual(s["unique_frames"],1); self.assertEqual(s["responses"],0)

if __name__=="__main__": unittest.main()
