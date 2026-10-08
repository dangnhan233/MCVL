import tempfile
import unittest
from pathlib import Path

from .phase45 import analyze_stream_log


class Phase45Test(unittest.TestCase):
    def write_log(self, content):
        tmp = tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".log", delete=False)
        with tmp:
            tmp.write(content)
        self.addCleanup(lambda: Path(tmp.name).unlink(missing_ok=True))
        return Path(tmp.name)

    def test_splits_concatenated_stream_and_matches_logged_frames(self):
        a = "44334BFF0000001B010018040200023130000000005AFF005C009B0000023131000136"
        b = "00004B010000001101000E03F300000000000100F001400000"
        log = self.write_log(
            "100 CLIENT_ACCEPT remote=/127.0.0.1:1234\n"
            f"101 RX_FRAME_HEX={a}\n"
            f"102 RX_FRAME_HEX={b}\n"
            f"103 RX_STREAM_HEX remote=/127.0.0.1:1234 hex={a}{b}\n"
        )
        report = analyze_stream_log(log)
        self.assertEqual(report["stream_count"], 1)
        self.assertEqual(report["valid_stream_count"], 1)
        self.assertEqual(report["stream_frame_count"], 2)
        self.assertEqual(report["frame_hex_values_matching_streams"], sorted([a.lower(), b.lower()]))

    def test_incomplete_stream_is_reported_not_silently_dropped(self):
        log = self.write_log(
            "103 RX_STREAM_HEX remote=/127.0.0.1:1234 hex=44334BFF0000001B0100\n"
        )
        report = analyze_stream_log(log)
        self.assertEqual(report["stream_count"], 1)
        self.assertEqual(report["invalid_or_incomplete_stream_count"], 1)
        self.assertEqual(report["streams"][0]["status"], "INVALID_OR_INCOMPLETE")
        self.assertEqual(report["streams"][0]["error"], "truncated_frame")

    def test_chunk_read_boundaries_are_not_required(self):
        log = self.write_log(
            "101 RX_CHUNK_HEX remote=/127.0.0.1:1234 hex=44\n"
            "102 RX_CHUNK_HEX remote=/127.0.0.1:1234 hex=33\n"
        )
        report = analyze_stream_log(log)
        self.assertEqual(report["stream_count"], 0)
        self.assertEqual(report["stream_frame_count"], 0)


if __name__ == "__main__":
    unittest.main()
