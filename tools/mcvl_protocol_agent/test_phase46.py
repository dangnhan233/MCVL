import tempfile
import unittest
from pathlib import Path

from .phase46 import analyze_response_log


class Phase46Test(unittest.TestCase):
    def test_extracts_success_and_error_responses(self):
        log_text = (
            "100 === MCVL EMBEDDED SERVER DEBUG START ===\n"
            "101 CLIENT_ACCEPT remote=/127.0.0.1:1234\n"
            "102 RX_FRAME_HEX=44334BFF0000001B010018040200023130000000005AFF005C009B0000023131000136\n"
            "103 RX_PACKET pid=1026 session=false\n"
            "104 TX_PACKET pid=1026 error=false data_hex=3132372E302E302E313A39303031\n"
            "105 TX_RESPONSE packets=1 [1026,34]\n"
            "106 CLIENT_ACCEPT remote=/127.0.0.1:1235\n"
            "107 RX_FRAME_HEX=00004B010000001101000E03F300000000000100F001400000\n"
            "108 RX_PACKET pid=1011 session=false\n"
            "109 TX_PACKET pid=1011 error=true data_hex=506869C3AA6E2068E1BABF742068E1BAA16E\n"
            "110 TX_RESPONSE packets=1 [1011:ERR,62]\n"
        )
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".log", delete=False) as tmp:
            tmp.write(log_text)
            name = tmp.name
        path = Path(name)
        self.addCleanup(lambda: path.unlink(missing_ok=True))
        report = analyze_response_log(path)
        self.assertEqual(report["request_count"], 2)
        self.assertEqual(report["response_packet_count"], 2)
        self.assertEqual(report["pid_overlap"], [1011, 1026])
        self.assertFalse(report["responses"][0]["error"])
        self.assertTrue(report["responses"][1]["error"])
        self.assertEqual(report["responses"][1]["utf8_text"], "Phiên hệt hãy")

    def test_invalid_utf8_is_reported_without_crashing(self):
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".log", delete=False) as tmp:
            tmp.write("1 TX_PACKET pid=7 error=false data_hex=FFFE\n")
            name = tmp.name
        path = Path(name)
        self.addCleanup(lambda: path.unlink(missing_ok=True))
        report = analyze_response_log(path)
        self.assertEqual(report["response_packet_count"], 1)
        self.assertIsNone(report["responses"][0]["utf8_text"])
        self.assertEqual(report["responses"][0]["utf8_decode_error"], "UnicodeDecodeError")


if __name__ == "__main__":
    unittest.main()
