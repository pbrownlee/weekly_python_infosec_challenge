"""
week08_starter.py — Local Port Scanner (Week 8, Tier 2: Beginner)

Fill in the TODOs. Function signatures are given — how you implement the
internals, and how you wire them together in main(), is up to you (that's
the point: sketch the plan/flowchart first, then build it).

Only ever point this at 127.0.0.1 / localhost or another host you own.
"""

import argparse


def scan_port(host: str, port: int, timeout: float = 0.5) -> bool:
    """Attempt a TCP connection to (host, port).

    Return True if the port appears open, False otherwise (closed,
    filtered, or any connection error). Should NOT raise for the normal
    "nothing is listening" case — handle that as a return value, not an
    exception.

    Hint: socket.socket(...).connect_ex((host, port)) returns 0 on success
    instead of raising, which is exactly what you want here. Remember to
    close the socket when you're done with it either way.
    """
    # TODO: implement
    raise NotImplementedError


def scan_range(
    host: str,
    start_port: int,
    end_port: int,
    timeout: float = 0.5,
    max_workers: int = 100,
) -> list[int]:
    """Scan every port in [start_port, end_port] (inclusive) concurrently.

    Return a sorted list of the ports that came back open.

    Use a ThreadPoolExecutor to run scan_port() across the range instead of
    looping and calling it one port at a time — this is an I/O-bound task
    (waiting on the network), which is exactly what threads are good for in
    Python.
    """
    # TODO: implement
    raise NotImplementedError


def format_report(
    host: str,
    start_port: int,
    end_port: int,
    open_ports: list[int],
    elapsed_seconds: float,
) -> str:
    """Build the human-readable summary string printed at the end of a scan.

    Should include: the host and range scanned, the list of open ports,
    total ports scanned, how many were open vs. closed/filtered, and the
    elapsed time. See the challenge's "Example Usage" section for the
    expected shape of this output.
    """
    # TODO: implement
    raise NotImplementedError


def main() -> None:
    parser = argparse.ArgumentParser(description="Local TCP port scanner")
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Target host (default: 127.0.0.1 — stick to hosts you own)",
    )
    parser.add_argument("--start", type=int, default=1, help="First port in range")
    parser.add_argument("--end", type=int, default=1024, help="Last port in range")
    parser.add_argument(
        "--timeout",
        type=float,
        default=0.5,
        help="Per-port connection timeout in seconds",
    )
    parser.add_argument(
        "--workers", type=int, default=100, help="Max concurrent threads"
    )
    _args = parser.parse_args()

    # TODO: wire it together —
    #   1. validate host is resolvable / reachable (don't let an unhandled
    #      traceback be the user's first sign something's wrong)
    #   2. time the scan
    #   3. call scan_range()
    #   4. print format_report()


if __name__ == "__main__":
    main()
