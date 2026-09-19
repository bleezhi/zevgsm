"""ZevGSM virtual phone client."""

from __future__ import annotations
import argparse
import socket
import time
from packets import Packet

DEFAULT_BTS = "127.0.0.1"
DEFAULT_PORT = 24720
IMSI = "999010000000001"
PHONE_NUMBER = "+48000000001"

def main() -> None:
    parser = argparse.ArgumentParser(description="ZevGSM virtual mobile")
    parser.add_argument("--bts", default=DEFAULT_BTS)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    args = parser.parse_args()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(5)

    print("zevMobile 2G")
    print("------------")
    print()
    print("Searching for network...")

    packet = Packet("REGISTER", {"imsi": IMSI, "phone": PHONE_NUMBER})
    sock.sendto(packet.encode(), (args.bts, args.port))

    try:
        data, _ = sock.recvfrom(65535)
        response = Packet.decode(data)
    except socket.timeout:
        print("No network found.")
        return

    if response.kind != "REGISTER_ACK":
        print(f"Unexpected network response: {response.kind}")
        return

    signal = int(response.fields.get("signal", 0))
    bars = max(0, min(10, round(signal / 10)))

    print(f"Found:  {response.fields.get('network', 'unknown')}")
    print(f"Cell:   {response.fields.get('cell', 'unknown')}")
    print(f"Signal: {'█' * bars}{'░' * (10 - bars)}")
    print()
    print("REGISTERING...")
    time.sleep(0.4)
    print()
    print("Registered!")
    print(f"Phone:  {PHONE_NUMBER}")

if __name__ == "__main__":
    main()
