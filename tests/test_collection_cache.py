"""Unit tests for ``scripts/collection_cache.py``.

``ansible-galaxy`` is replaced by a fake, so the tests check the installer
command line (``--no-deps``) and the ``index.json`` bookkeeping offline.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import collection_cache  # noqa: E402


def _fake_galaxy(monkeypatch, calls):
    monkeypatch.setattr(collection_cache.shutil, "which", lambda _: "ansible-galaxy")

    def fake_run(cmd, **_kwargs):
        calls.append(cmd)
        return subprocess.CompletedProcess(cmd, 0, "", "")

    monkeypatch.setattr(collection_cache.subprocess, "run", fake_run)


def _ensure(tmp_path, version):
    versions = tmp_path / "versions.env"
    versions.write_text(f'ARILLSO_SYSTEM_VERSION="{version}"\n', encoding="utf-8")
    args = collection_cache.build_parser().parse_args(
        ["ensure", "--versions-file", str(versions), "--cache-dir", str(tmp_path / "cache")]
    )
    assert collection_cache.cmd_ensure(args) == 0
    return json.loads((tmp_path / "cache" / "index.json").read_text(encoding="utf-8"))


def test_install_skips_dependencies(tmp_path, monkeypatch, capsys):
    calls = []
    _fake_galaxy(monkeypatch, calls)
    _ensure(tmp_path, "2.0.4")
    capsys.readouterr()
    assert len(calls) == 1
    assert "--no-deps" in calls[0]


def test_index_keeps_timestamp_only_for_same_version_hit(tmp_path, monkeypatch, capsys):
    calls = []
    _fake_galaxy(monkeypatch, calls)

    first = _ensure(tmp_path, "2.0.4")["arillso.system"]
    # Pretend the first download happened long ago.
    index_path = tmp_path / "cache" / "index.json"
    index = json.loads(index_path.read_text(encoding="utf-8"))
    index["arillso.system"]["downloaded_at"] = "2000-01-01T00:00:00+00:00"
    index_path.write_text(json.dumps(index), encoding="utf-8")

    hit = _ensure(tmp_path, "2.0.4")["arillso.system"]
    assert len(calls) == 1  # cache hit, no second install
    assert hit == {"version": first["version"], "downloaded_at": "2000-01-01T00:00:00+00:00"}

    switched = _ensure(tmp_path, "2.0.5")["arillso.system"]
    capsys.readouterr()
    assert len(calls) == 2
    assert switched["version"] == "2.0.5"
    assert switched["downloaded_at"] != "2000-01-01T00:00:00+00:00"
