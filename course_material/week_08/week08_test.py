"""
week08_test.py — CI tests for the Week 8 Local Port Scanner.

CI-safe by design: everything runs against 127.0.0.1 using a short-lived
local TCP server spun up in a background thread for the duration of each
test. No real/live hosts, no scanning beyond localhost.

Run locally with:
    pytest -v week08_test.py
"""

import socket
import threading
import time

import pytest
from week08_starter import format_report, scan_port, scan_range


@pytest.fixture
def open_port():
    """Start a tiny TCP server on an OS-assigned free port and yield it.

    Binding to port 0 asks the OS for any free port, which avoids hardcoding
    a port number that might already be in use on the CI runner.
    """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("127.0.0.1", 0))
    server.listen(1)
    port = server.getsockname()[1]

    stop = threading.Event()

    def accept_loop():
        server.settimeout(0.2)
        while not stop.is_set():
            try:
                conn, _ = server.accept()
                conn.close()
            except TimeoutError:
                continue

    thread = threading.Thread(target=accept_loop, daemon=True)
    thread.start()

    yield port

    stop.set()
    server.close()
    thread.join(timeout=1)


@pytest.fixture
def closed_port():
    """Return a port that is (almost certainly) not listening on localhost.

    We bind to it momentarily to get a free one, then immediately close it
    so nothing is listening when the test runs.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    return port


def test_scan_port_detects_open_port(open_port):
    assert scan_port("127.0.0.1", open_port, timeout=0.5) is True


def test_scan_port_detects_closed_port(closed_port):
    assert scan_port("127.0.0.1", closed_port, timeout=0.2) is False


def test_scan_range_finds_the_open_port_in_a_range(open_port):
    start = max(1, open_port - 2)
    end = open_port + 2
    results = scan_range("127.0.0.1", start, end, timeout=0.2, max_workers=10)
    assert open_port in results
    # every other port in this tiny range should be closed
    assert all(p == open_port for p in results)


def test_scan_range_returns_sorted_list(open_port):
    start = max(1, open_port - 2)
    end = open_port + 2
    results = scan_range("127.0.0.1", start, end, timeout=0.2, max_workers=10)
    assert results == sorted(results)


def test_scan_range_runs_concurrently_not_sequentially(closed_port):
    """A rough concurrency sanity check: scanning 20 closed ports with a
    0.3s timeout each should take well under 20 * 0.3s if a thread pool is
    actually being used instead of a sequential loop.
    """
    start = time.monotonic()
    scan_range("127.0.0.1", 1, 20, timeout=0.3, max_workers=20)
    elapsed = time.monotonic() - start
    assert elapsed < 2.0  # generous ceiling; sequential would take ~6s


def test_format_report_includes_key_fields(open_port):
    report = format_report("127.0.0.1", open_port, open_port, [open_port], 0.42)
    assert "127.0.0.1" in report
    assert str(open_port) in report
