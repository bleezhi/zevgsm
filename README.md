# zevGSM

A custom 2G-like virtual cellular network for zevMobile.

This is intentionally not real GSM. The goal is to build a controllable
cellular simulation first, then put a simulated radio/propagation layer such
as SimTX between the phone and the virtual base station.

## v0.1

Current pieces:

- zevgsm/packets.py - ZevGSM packet format
- zevgsm/bts.py - virtual base station
- zevgsm/mobile.py - virtual phone
- zevgsm/simtx_adapter.py - future SimTX radio interface

## Try it

Open two terminals.

Terminal 1:
    cd zevgsm
    python bts.py

Terminal 2:
    cd zevgsm
    python mobile.py

The phone should register on ZEV-2G.

## Planned

1. SMS between virtual phones
2. virtual SIM/IMSI database
3. cell selection and roaming
4. realistic signal strength
5. packet loss and retransmission
6. audio modem
7. SimTX transport
8. zevMobile integration
