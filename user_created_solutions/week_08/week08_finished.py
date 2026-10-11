"""
week08_finished.py — Local Port Scanner (Week 8, Tier 2: Beginner)

Fill in the TODOs. Function signatures are given — how you implement the
internals, and how you wire them together in main(), is up to you (that's
the point: sketch the plan/flowchart first, then build it).

Only ever point this at 127.0.0.1 / localhost or another host you own.
"""

import argparse
import concurrent.futures
import ipaddress
import socket
import time


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
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(timeout)
        try:
            return sock.connect_ex((host, port)) == 0
        except OSError:
            return False


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
    scan_ports = range(start_port, end_port + 1)
    open_ports = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_port = {
            executor.submit(scan_port, host, port, timeout): port for port in scan_ports
        }
        for future in concurrent.futures.as_completed(future_to_port):
            port = future_to_port[future]
            if future.result():
                open_ports.append(port)
    return sorted(open_ports)


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
    total_ports = (end_port + 1) - start_port
    result_str = f"Open ports on host {host}: {open_ports}\n"
    result_str += f"Scanned {total_ports} ports in {round(elapsed_seconds, 2)}s - "
    result_str += (
        f"{len(open_ports)} open, {total_ports - len(open_ports)} closed/filtered"
    )
    return result_str


def main() -> None:
    parser = argparse.ArgumentParser(description="Local TCP port scanner")
    parser.add_argument(
        "--host",
        type=ipaddress.IPv4Address,
        default="127.0.0.1",
        help="Target ipv4 host address you own (default: 127.0.0.1 — stick to hosts you own)",
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
    args = parser.parse_args()

    if not (0 <= args.start <= args.end <= 65535):
        parser.error(
            "Valid port ranges must satisfy range 0 to 65535 inclusive. start cannot be greater than end"
        )
    if args.workers < 1:
        parser.error("--workers must be at least 1")
    if args.timeout <= 0:
        parser.error("--timeout must be greater than 0")

    vetted_host = str(args.host)
    print(
        f"Scanning {vetted_host} ports {args.start}-{args.end} with {args.workers} workers..."
    )
    start_time = time.perf_counter()
    scan_result = scan_range(
        vetted_host, args.start, args.end, args.timeout, args.workers
    )
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(format_report(vetted_host, args.start, args.end, scan_result, elapsed_time))


if __name__ == "__main__":
    main()
