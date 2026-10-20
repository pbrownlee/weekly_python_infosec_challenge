"""
Week 8 Solution — Local Port Scanner  (Tier 2: Beginner, Topic 4)

Assumed interface for this reconstruction:
    scan_port(host, port, timeout=1.0) -> bool
    parse_port_spec(spec) -> list[int]
    scan_ports(host, ports, timeout=1.0, max_workers=100) -> list[int]
    format_report(host, open_ports) -> str
    main()
"""

import argparse
import socket
from concurrent.futures import ThreadPoolExecutor, as_completed


def parse_port_spec(spec):
    """
    Parse a port specification string into a sorted list of unique ints.

    Supports:
      - a single port:      "22"
      - a comma list:       "22,80,443"
      - a range:            "1-1024"
      - a mix:              "22,80,1000-1010"
    """
    ports = set()
    for chunk in spec.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        if "-" in chunk:
            start_str, end_str = chunk.split("-", 1)
            start, end = int(start_str), int(end_str)
            if start > end:
                start, end = end, start
            ports.update(range(start, end + 1))
        else:
            ports.add(int(chunk))
    return sorted(ports)


def scan_port(host, port, timeout=1.0):
    """
    Try to open a TCP connection to (host, port).
    Returns True if the port accepted the connection (i.e. is open), else False.

    A naive first attempt here often forgets `settimeout()` entirely -- without
    it, connect_ex() on a filtered/firewalled port can hang for the OS-default
    timeout (sometimes minutes), making a scan of even a small range feel frozen.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(timeout)
        # connect_ex returns an error indicator instead of raising, which is
        # friendlier for a scan loop than wrapping every call in try/except.
        result = sock.connect_ex((host, port))
        return result == 0


def scan_ports(host, ports, timeout=1.0, max_workers=100):
    """
    Scan `ports` on `host` concurrently using a thread pool (sockets are I/O
    bound, so threads -- not processes -- are the right tool here).
    Returns a sorted list of the ports that are open.
    """
    open_ports = []
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        future_to_port = {
            pool.submit(scan_port, host, port, timeout): port for port in ports
        }
        for future in as_completed(future_to_port):
            port = future_to_port[future]
            try:
                if future.result():
                    open_ports.append(port)
            except OSError:
                # Host unreachable / name resolution hiccup on this attempt --
                # skip rather than letting one bad socket kill the whole scan.
                continue
    return sorted(open_ports)


def format_report(host, open_ports):
    """Build a human-readable summary string for the scan results."""
    if not open_ports:
        return f"No open ports found on {host}."
    lines = [f"Open ports on {host}:"]
    for port in open_ports:
        try:
            service = socket.getservbyport(port)
        except OSError:
            service = "unknown"
        lines.append(f"  {port:>5}/tcp  open  {service}")
    lines.append(f"\n{len(open_ports)} open port(s) found.")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Scan a host for open TCP ports (localhost / local network only)."
    )
    parser.add_argument(
        "--host", default="127.0.0.1", help="Target host (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--ports",
        default="1-1024",
        help="Port spec, e.g. '22,80,443' or '1-1024' (default: 1-1024)",
    )
    parser.add_argument(
        "--timeout", type=float, default=1.0, help="Per-port connect timeout in seconds"
    )
    parser.add_argument(
        "--workers", type=int, default=100, help="Max concurrent scan threads"
    )
    args = parser.parse_args()

    ports = parse_port_spec(args.ports)
    open_ports = scan_ports(
        args.host, ports, timeout=args.timeout, max_workers=args.workers
    )
    print(format_report(args.host, open_ports))


if __name__ == "__main__":
    main()
