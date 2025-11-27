# adaptive_core/threat_memory.py

from __future__ import annotations

import json
from pathlib import Path
from typing import List, Dict, Any, Optional

from .threat_packet import ThreatPacket


class ThreatMemory:
    """
    Basic memory container for ThreatPacket objects.

    This is where the Adaptive Core can store, reload and analyse
    past threats reported by all 5 shield layers.
    """

    def __init__(self, storage_path: Optional[Path] = None) -> None:
        # Default location: ./data/threat_memory.json (created if missing)
        if storage_path is None:
            self.storage_path = Path("data") / "threat_memory.json"
        else:
            self.storage_path = storage_path

        self._packets: List[ThreatPacket] = []

    # ---------- core operations ----------

    def add_packet(self, packet: ThreatPacket) -> None:
        """Add a new ThreatPacket to memory."""
        self._packets.append(packet)

    def list_packets(self) -> List[ThreatPacket]:
        """Return all stored packets."""
        return list(self._packets)

    def clear(self) -> None:
        """Clear in-memory packets (does not touch disk)."""
        self._packets.clear()

    # ---------- persistence ----------

    def save(self) -> None:
        """
        Save current packets to disk as JSON.
        Creates parent directory if it does not exist.
        """
        if not self.storage_path.parent.exists():
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        data: List[Dict[str, Any]] = [p.to_dict() for p in self._packets]

        with self.storage_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def load(self) -> None:
        """
        Load packets from disk into memory.
        If file does not exist, memory stays empty.
        """
        if not self.storage_path.exists():
            self._packets = []
            return

        with self.storage_path.open("r", encoding="utf-8") as f:
            raw: List[Dict[str, Any]] = json.load(f)

        self._packets = [ThreatPacket.from_dict(item) for item in raw]
