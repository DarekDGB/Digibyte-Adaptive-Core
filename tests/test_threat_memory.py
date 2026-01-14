from __future__ import annotations

import json
from pathlib import Path

from adaptive_core.threat_memory import ThreatMemory
from adaptive_core.threat_packet import ThreatPacket


def _pkt(i: int) -> ThreatPacket:
    return ThreatPacket(
        source_layer="sentinel_ai_v2",
        threat_type="t",
        severity=5,
        description=f"d{i}",
        correlation_id=f"cid-{i}",
        timestamp="2026-01-14T00:00:00Z",
    )


def test_in_memory_mode_no_disk_io():
    mem = ThreatMemory(path=None, max_packets=10)

    # load/save are no-ops in memory-only mode
    mem.load()
    mem.save()

    mem.add_packet(_pkt(1))
    assert len(mem.list_packets()) == 1


def test_enforce_limit_fifo_pruning():
    mem = ThreatMemory(path=None, max_packets=2)

    mem.add_packet(_pkt(1))
    mem.add_packet(_pkt(2))
    mem.add_packet(_pkt(3))  # should prune oldest

    packets = mem.list_packets()
    assert len(packets) == 2
    assert packets[0].correlation_id == "cid-2"
    assert packets[1].correlation_id == "cid-3"


def test_enforce_limit_non_positive_cap_clears_storage():
    mem = ThreatMemory(path=None, max_packets=0)
    mem.add_packet(_pkt(1))
    assert mem.list_packets() == []


def test_load_file_missing_resets_packets(tmp_path: Path):
    p = tmp_path / "threats.json"
    mem = ThreatMemory(path=p, max_packets=10)

    mem.add_packet(_pkt(1))
    assert len(mem.list_packets()) == 1

    # file doesn't exist => resets to []
    mem.load()
    assert mem.list_packets() == []


def test_load_parse_error_resets_packets(tmp_path: Path):
    p = tmp_path / "threats.json"
    p.write_text("not-json", encoding="utf-8")

    mem = ThreatMemory(path=p, max_packets=10)
    mem.load()
    assert mem.list_packets() == []


def test_load_skips_malformed_entries_and_prunes_to_limit(tmp_path: Path):
    p = tmp_path / "threats.json"

    good1 = _pkt(1).to_dict()
    bad = {"not": "a threat packet"}  # missing required fields => from_dict fails
    good2 = _pkt(2).to_dict()

    # also include extra entries to trigger pruning
    good3 = _pkt(3).to_dict()

    p.write_text(json.dumps([good1, bad, good2, good3]), encoding="utf-8")

    mem = ThreatMemory(path=p, max_packets=2)
    mem.load()

    packets = mem.list_packets()
    assert len(packets) == 2
    # oldest kept should be cid-2 then cid-3 (since limit=2)
    assert packets[0].correlation_id == "cid-2"
    assert packets[1].correlation_id == "cid-3"


def test_save_writes_json_when_enabled(tmp_path: Path):
    p = tmp_path / "nested" / "threats.json"
    mem = ThreatMemory(path=p, max_packets=10)

    mem.add_packet(_pkt(1))
    mem.add_packet(_pkt(2))
    mem.save()

    assert p.exists()
    data = json.loads(p.read_text(encoding="utf-8"))
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]["correlation_id"] == "cid-1"
    assert data[1]["correlation_id"] == "cid-2"
