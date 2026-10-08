import socket
import threading
import time

from .server_replacement import MCVLEmbeddedServer


def test_server_preserves_stream_bytes():
    server = MCVLEmbeddedServer("127.0.0.1", 0)
    captured = []

    def fake_log(msg, *args):
        captured.append(msg % args)

    server._log = fake_log
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("127.0.0.1", 0))
    srv.listen(1)
    port = srv.getsockname()[1]

    raw = bytes.fromhex(
        "44 34 4B FF 00 00 00 1B 01 00 18 04 02 00 02 31 "
        "30 00 00 00 00 5A FF 00 5C 00 9B 00 00 02 31 31 00 01 36"
    )

    def accept():
        conn, addr = srv.accept()
        server._client(conn, addr, 1)

    thread = threading.Thread(target=accept, daemon=True)
    thread.start()
    client = socket.create_connection(("127.0.0.1", port))
    try:
        client.sendall(raw[:11])
        client.sendall(raw[11:])
        client.shutdown(socket.SHUT_WR)
    finally:
        client.close()
    thread.join(timeout=2)
    srv.close()

    stream_lines = [x for x in captured if x.startswith("RX_STREAM_HEX")]
    assert stream_lines
    assert raw.hex().upper() in stream_lines[0]
    assert any("FRAME_BOUNDARY status=UNRESOLVED" in x for x in captured)
    assert any("PID_1026 status=UNRESOLVED" in x for x in captured)
