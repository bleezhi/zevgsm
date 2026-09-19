"""ZevGSM virtual 2G-like base station."""

from __future__ import annotations
import argparse
import socket
from packets import Packet

DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 24720
NETWORK = "ZEV-2G"
CELL = "ZEV-PL-01"

def main() -> None:
    parser = argparse.ArgumentParser(description="ZevGSM virtual BTS")
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    args = parser.parse_args()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((args.host, args.port))

    print("ZevGSM Base Station")
    print("-------------------")
    print(f"Network: {NETWORK}")
    print(f"Cell:    {CELL}")
    print(f"UDP:     {args.host}:{args.port}")
    print("Status:  ONLINE")
    print()
    print("Waiting for phones...")

    while True:
        data, address = sock.recvfrom(65535)
        try:
            packet = Packet.decode(data)
        except Exception as exc:
            print(f"[BTS] Invalid packet from {address}: {exc}")
            continue

        print(f"[BTS] {address} -> {packet.kind} {packet.fields}")

        if packet.kind == "REGISTER":
            response = Packet("REGISTER_ACK", {
                "network": NETWORK,
                "cell": CELL,
                "signal": 100,
                "imsi": packet.fields.get("imsi", ""),
            })
            sock.sendto(response.encode(), address)
            print(f"[BTS] Registered {packet.fields.get('imsi', 'unknown')}")

        elif packet.kind == "PING":
            sock.sendto(Packet("PONG", {"cell": CELL}).encode(), address)

if __name__ == "__main__":
    main()
