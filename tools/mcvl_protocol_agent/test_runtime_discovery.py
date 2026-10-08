import tempfile, unittest
from pathlib import Path
from .runtime_discovery import scan
class RuntimeDiscoveryTest(unittest.TestCase):
 def test_network_candidate_ranking(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'Server.gd'; p.write_text('var tcp=StreamPeerTCP.new()\nfunc decode_packet(pid, payload): pass\nfunc accept_client(): pass\n'); r=scan(d); self.assertEqual(r['files_scanned'],1); self.assertEqual(r['top_candidates'][0]['file'],'Server.gd'); self.assertIn('tcp',r['top_candidates'][0]['kinds']); self.assertIn('packet',r['top_candidates'][0]['kinds'])
if __name__=='__main__': unittest.main()
