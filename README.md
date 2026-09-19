# zevGSM

A custom 2G-like virtual cellular network for zevMobile.

This is intentionally not real GSM. The goal is to build a controllable
cellular simulation first, then put a simulated radio/propagation layer
such as SimTX between the phone and the virtual base station.

## v0.2 - simulated tower audio

The new `tower.py` generates a continuous custom 2-FSK ZEV-2G beacon and
**automatically forces output to**:

    Voicemeeter Input (VB-Audio Voicemeeter VAIO)

It never uses the Windows default playback device.

The beacon contains:

- network name: ZEV-2G
- cell: ZEV-PL-01
- signal value: 100
- CRC-8 protected frame
- repeated preamble for receiver synchronization

This is a custom simulation protocol, not actual GSM modulation.

## Run the tower

Install dependencies:

    python -m pip install -r requirements.txt

Then:

    python tower.py

The tower continuously sends its beacon into Voicemeeter.

Recommended routing:

    zevGSM tower
        ↓
    Voicemeeter Input (VAIO)
        ↓
    Voicemeeter B1
        ↓
    SimTX transmitter/input
        ↓
    SimTX simulated propagation
        ↓
    SimTX receiver/output
        ↓
    future zevGSM mobile modem

## Existing UDP test

Terminal 1:

    python zevgsm/bts.py

Terminal 2:

    python zevgsm/mobile.py

## Planned

1. FSK receiver/demodulator
2. phone-side audio input
3. two-way radio packets
4. SMS
5. virtual SIM/IMSI database
6. signal strength from received audio
7. packet loss and retransmission
8. SimTX integration
9. zevMobile integration
