from __future__ import annotations

from pathlib import Path

from adaptive_core.threat_memory import ThreatMemory


def test_threat_memory_in_memory_by_default(tmp_path, monkeypatch):
    # Prove no implicit file write in current working directory
    monkeypatch.chdir(tmp_path)

    tm = ThreatMemory()  # default must be in-memory
    tm.load()
    tm.save()

    assert tm.path is None
    assert not (tmp_path / "threat_memory.json").exists()


def test_threat_memory_disk_is_opt_in(tmp_path):
    # Disk persistence only happens if path is explicitly provided
    p = tmp_path / "threat_memory.json"
    tm = ThreatMemory(path=p)

    tm.save()
    assert p.exists()
    assert p.read_text(encoding="utf-8").strip().startswith("[")
