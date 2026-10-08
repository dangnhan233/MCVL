import unittest
from .analyzer import analyze_frame
from .models import PacketCapture
class ProtocolAnalyzerTest(unittest.TestCase):
    def test_1026_fixture_is_observation_only(self):
        c=PacketCapture("MCVL_SERVER_DEBUG_20261008_194923",1791463777338,"C2S","/127.0.0.1:39296",1026,False,"44344BFF0000001B010018040200023130000000005AFF005C009B0000023131000136")
        r=analyze_frame(c)
        self.assertEqual(r.pid,1026); self.assertEqual(r.frame_length,35); self.assertEqual(r.header_candidates[0].confidence,1.0); self.assertFalse(r.response_known); self.assertIn("checksum algorithm",r.unknown); self.assertTrue(r.required_evidence)
if __name__=="__main__": unittest.main()
