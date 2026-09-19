"""ZevGSM simulated tower audio beacon.

This is a custom 2G-like protocol, not real GSM RF.
The tower continuously sends a framed FSK beacon to the exact
Voicemeeter VAIO Input playback device.
"""

from __future__ import annotations

import argparse
import math
import struct
import time
import wave

import numpy as np
import sounddevice as sd

OUTPUT_DEVICE = "Voicemeeter Input (VB-Audio Voicemeeter VAIO)"
SAMPLE_RATE = 48000
MARK_HZ = 2200.0
SPACE_HZ = 1200.0
SYMBOL_MS = 20.0
AMPLITUDE = 0.22

NETWORK = "ZEV-2G"
CELL = "ZEV-PL-01"


def find_voicemeeter() -> tuple[int, str]:
    """Find the exact Voicemeeter VAIO Input; never use the default device."""
    devices = sd.query_devices()
    hostapis = sd.query_hostapis()

    matches = []
    for index, device in enumerate(devices):
        if device["name"].strip().lower() != OUTPUT_DEVICE.lower():
            continue
        if device["max_output_channels"] < 1:
            continue
        hostapi = hostapis[device["hostapi"]]["name"]
        matches.append((index, device["name"], hostapi))

    if not matches:
        print(f"[ZevGSM] ERROR: '{OUTPUT_DEVICE}' not found.")
        print("[ZevGSM] Available playback devices:")
        for index, device in enumerate(devices):
            if device["max_output_channels"] > 0:
                hostapi = hostapis[device["hostapi"]]["name"]
                print(f"  [{index}] {device['name']} ({hostapi})")
        raise RuntimeError("Voicemeeter VAIO Input is unavailable.")

    for match in matches:
        if "WASAPI" in match[2].upper():
            return match[0], match[1]

    return matches[0][0], matches[0][1]


def crc8(data: bytes) -> int:
    value = 0
    for byte in data:
        value ^= byte
        for _ in range(8):
            value = ((value << 1) ^ 0x07) & 0xFF if value & 0x80 else (value << 1) & 0xFF
    return value


def frame_payload(network: str, cell: str) -> bytes:
    payload = f"{network}|{cell}|100".encode("ascii")
    return b"ZEV2" + bytes([len(payload)]) + payload + bytes([crc8(payload)])


def bits(data: bytes) -> list[int]:
    return [bit for byte in data for bit in ((byte >> shift) & 1 for shift in range(7, -1, -1))]


def fsk(data: bytes) -> np.ndarray:
    symbol_samples = int(SAMPLE_RATE * SYMBOL_MS / 1000.0)
    out = np.empty(len(data) * 8 * symbol_samples, dtype=np.float32)

    phase = 0.0
    pos = 0

    for bit in bits(data):
        freq = MARK_HZ if bit else SPACE_HZ
        phase_step = 2.0 * math.pi * freq / SAMPLE_RATE
        idx = np.arange(symbol_samples, dtype=np.float32)
        chunk = np.sin(phase + phase_step * idx) * AMPLITUDE

        # Small raised-cosine edge ramps reduce clicks between symbols.
        ramp = max(1, min(symbol_samples // 8, 80))
        window = np.ones(symbol_samples, dtype=np.float32)
        edge = np.linspace(0.0, 1.0, ramp, dtype=np.float32)
        window[:ramp] *= edge
        window[-ramp:] *= edge[::-1]

        out[pos:pos + symbol_samples] = chunk * window
        phase = (phase + phase_step * symbol_samples) % (2.0 * math.pi)
        pos += symbol_samples

    return out


def make_beacon() -> np.ndarray:
    # Repeat a preamble so the receiver can find symbol timing.
    preamble = bytes([0xAA]) * 8
    return fsk(preamble + frame_payload(NETWORK, CELL))


def main() -> None:
    parser = argparse.ArgumentParser(description="ZevGSM simulated 2G tower")
    parser.add_argument("--loop-gap", type=float, default=0.20)
    args = parser.parse_args()

    device_index, device_name = find_voicemeeter()
    hostapi = sd.query_hostapis(sd.query_devices(device_index)["hostapi"])["name"]

    print("ZevGSM simulated tower")
    print("----------------------")
    print(f"Network: {NETWORK}")
    print(f"Cell:    {CELL}")
    print(f"Output:  {device_name}")
    print(f"Audio:   {SAMPLE_RATE} Hz / custom 2-FSK")
    print(f"Backend: {hostapi}")
    print()
    print("FORCED OUTPUT: Voicemeeter VAIO Input")
    print("Starting beacon... Ctrl+C to stop.")

    beacon = make_beacon()

    extra = None
    if "WASAPI" in hostapi.upper():
        extra = sd.WasapiSettings(exclusive=False, auto_convert=True)

    try:
        while True:
            sd.play(
                beacon,
                samplerate=SAMPLE_RATE,
                device=device_index,
                blocking=True,
                extra_settings=extra,
            )
            if args.loop_gap > 0:
                time.sleep(args.loop_gap)
    except KeyboardInterrupt:
        print("\n[ZevGSM] Tower stopped.")
    finally:
        sd.stop()


if __name__ == "__main__":
    main()
