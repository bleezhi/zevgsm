"""ZevGSM v0.1 packet protocol."""

from __future__ import annotations
from dataclasses import dataclass
import json

PROTOCOL = "ZEVGSM/0.1"

@dataclass
class Packet:
    kind: str
    fields: dict

    def encode(self) -> bytes:
        payload = {"protocol": PROTOCOL, "kind": self.kind, "fields": self.fields}
        return (json.dumps(payload, separators=(",", ":")) + "\n").encode("utf-8")

    @staticmethod
    def decode(data: bytes) -> "Packet":
        obj = json.loads(data.decode("utf-8"))
        if obj.get("protocol") != PROTOCOL:
            raise ValueError("Unsupported ZevGSM protocol")
        return Packet(obj["kind"], obj.get("fields", {}))
