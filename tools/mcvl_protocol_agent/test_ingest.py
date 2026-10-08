import tempfile, unittest
from pathlib import Path
from .ingest import ingest_log

LOG='''1791463763419 === MCVL EMBEDDED SERVER DEBUG START ===\n1791463773197 CLIENT_ACCEPT remote=/127.0.0.1:39296\n1791463777311 RX_FRAME bytes=35\n1791463777338 RX_FRAME_HEX=44344BFF0000001B010018040200023130000000005AFF005C009B0000023131000136\n1791463777359 RX_PACKET pid=1026 session=false\n1791463777397 TX_RESPONSE packets=0\n'''

class IngestTest(unittest.TestCase):
    def test_ingest_pid_1026(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'MCVL_SERVER_DEBUG_test.log'; p.write_text(LOG)
            xs=ingest_log(p)
            self.assertEqual(len(xs),1); self.assertEqual(xs[0].pid,1026); self.assertEqual(len(xs[0].raw),35); self.assertEqual(xs[0].response_packets,0)

if __name__=='__main__': unittest.main()
