import socket, threading, time
from .server_replacement import MCVLEmbeddedServer

def test_observed_pid_candidate():
    raw=bytes.fromhex("44 34 4B FF 00 00 00 1B 01 00 18 04 02 00 02 31 30 00 00 00 00 5A FF 00 5C 00 9B 00 00 02 31 31 00 01 36")
    assert MCVLEmbeddedServer._observed_pid_candidate(raw)==1026

def test_unknown_pid_not_guessed():
    raw=bytearray(35)
    raw[10:12]=b"\x99\x99"
    assert MCVLEmbeddedServer._observed_pid_candidate(bytes(raw)) is None
