#!/usr/bin/env python3
"""Collection Cache manager for Ansible Galaxy collections.

Reads ``versions.env`` (shell-style ``KEY="value"`` lines) for required
Arillso collection versions, maintains a versioned local cache under
``~/.cache/arillso-collections/<namespace>/<name>/<version>/`` and, in online
mode, fetches missing versions via ``ansible-galaxy collection install``.

See ``.kiro/specs/refactoring-structure-to-modern-best-practices/design.md``
section 6.2 for the full contract.

Exit codes (per design §6.2):

* ``0`` -- success; JSON manifest written to stdout.
* ``1`` -- offline mode and cache miss.
* ``2`` -- ``versions.env`` could not be read.
* ``3`` -- ``ansible-galaxy`` executable not found.
* ``4`` -- network/installer error during online install.
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Mapping from versions.env environment variable -> (namespace, collection name)
ENV_VAR_TO_COLLECTION: Dict[str, Tuple[str, str]] = {
    "ARILLSO_SYSTEM_VERSION": ("arillso", "system"),
    "ARILLSO_AGENT_VERSION": ("arillso", "agent"),
    "ARILLSO_CONTAINER_VERSION": ("arillso", "container"),
}

# Matches lines like:  KEY="value"
# Anchored to start of line; trailing comments after the closing quote are
# tolerated by the regex but not captured.
_VERSIONS_LINE_RE = re.compile(r'^([A-Z][A-Z0-9_]*)="([^"]+)"')

# Marker file placed inside a version directory once the download completed
# successfully. Presence signals "cache hit"; absence forces a re-download.
CACHE_COMPLETE_MARKER = ".cache_complete"

# Exit codes (must match design §6.2 / requirements §7.1).
EXIT_OK = 0
EXIT_OFFLINE_MISS = 1
EXIT_NO_VERSIONS_FILE = 2
EXIT_NO_ANSIBLE_GALAXY = 3
EXIT_NETWORK_ERROR = 4


def parse_versions_file(path: Path) -> Dict[str, Tuple[str, str]]:
    """Parse a ``versions.env`` shell-style file.

    Returns a mapping ``{"<namespace>.<name>": ("<namespace>", "<name>",
    "<version>")}`` for every known ARILLSO_* environment variable.
    Unknown variables are silently ignored to keep the file compatible with
    future additions and shell sourcing.

    Raises ``FileNotFoundError`` if ``path`` does not exist or is not a file.
    """
    if not path.is_file():
        raise FileNotFoundError(str(path))

    found: Dict[str, Tuple[str, str, str]] = {}
    with path.open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            match = _VERSIONS_LINE_RE.match(line)
            if not match:
                continue
            key, value = match.group(1), match.group(2)
            if key not in ENV_VAR_TO_COLLECTION:
                continue
            namespace, name = ENV_VAR_TO_COLLECTION[key]
            found[f"{namespace}.{name}"] = (namespace, name, value)

    return found  # type: ignore[return-value]


def read_index(cache_dir: Path) -> Dict[str, Dict[str, str]]:
    """Read ``<cache-dir>/index.json``; return empty dict if missing/corrupt."""
    index_path = cache_dir / "index.json"
    if not index_path.is_file():
        return {}
    try:
        with index_path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
            if isinstance(data, dict):
                return data
            return {}
    except (json.JSONDecodeError, OSError):
        # A corrupt index is treated as empty; the next successful install
        # will overwrite it. We do not crash the build for this.
        return {}


def write_index(cache_dir: Path, index: Dict[str, Dict[str, str]]) -> None:
    """Atomically write ``<cache-dir>/index.json``."""
    cache_dir.mkdir(parents=True, exist_ok=True)
    index_path = cache_dir / "index.json"
    tmp_path = index_path.with_suffix(".json.tmp")
    with tmp_path.open("w", encoding="utf-8") as handle:
        json.dump(index, handle, indent=2, sort_keys=True)
        handle.write("\n")
    os.replace(tmp_path, index_path)


def version_dir(cache_dir: Path, namespace: str, name: str, version: str) -> Path:
    """Return the canonical cache path for a (namespace, name, version)."""
    return cache_dir / namespace / name / version


def is_cache_hit(version_path: Path) -> bool:
    """A cache hit requires both the directory and the completion marker."""
    return version_path.is_dir() and (version_path / CACHE_COMPLETE_MARKER).is_file()


def ensure_collection(
    namespace: str,
    name: str,
    version: str,
    cache_dir: Path,
    offline: bool,
) -> Tuple[Path, str]:
    """Ensure a single (namespace, name, version) is available in the cache.

    Returns ``(version_path, status)`` where ``status`` is ``"hit"`` or
    ``"installed"``.

    Raises:
        OfflineCacheMissError: offline mode and the version is not cached.
        AnsibleGalaxyMissingError: ``ansible-galaxy`` not on ``PATH``.
        AnsibleGalaxyInstallError: ``ansible-galaxy`` exited non-zero.
    """
    target = version_dir(cache_dir, namespace, name, version)

    if is_cache_hit(target):
        return target, "hit"

    if offline:
        raise OfflineCacheMissError(namespace, name, version, target)

    galaxy = shutil.which("ansible-galaxy")
    if galaxy is None:
        raise AnsibleGalaxyMissingError()

    # Wipe any partial directory from a previous failed attempt so the
    # ``--force`` install starts from a clean slate.
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True, exist_ok=True)

    coll_spec = f"{namespace}.{name}:{version}"
    cmd = [
        galaxy,
        "collection",
        "install",
        coll_spec,
        "--collections-path",
        str(target),
        "--force",
    ]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError as exc:  # pragma: no cover -- defensive
        raise AnsibleGalaxyInstallError(coll_spec, str(exc)) from exc

    if result.returncode != 0:
        # Surface the actual ansible-galaxy stderr to help diagnose the issue.
        raise AnsibleGalaxyInstallError(coll_spec, result.stderr or result.stdout)

    # Mark the directory as complete only after the installer reported success.
    (target / CACHE_COMPLETE_MARKER).touch()
    return target, "installed"


class CollectionCacheError(Exception):
    """Base class for collection-cache failures with an associated exit code."""

    exit_code: int = 1


class OfflineCacheMissError(CollectionCacheError):
    exit_code = EXIT_OFFLINE_MISS

    def __init__(self, namespace: str, name: str, version: str, target: Path) -> None:
        self.namespace = namespace
        self.name = name
        self.version = version
        self.target = target
        super().__init__(
            f"Offline mode: collection {namespace}.{name} version {version} "
            f"not found in cache at {target}"
        )


class AnsibleGalaxyMissingError(CollectionCacheError):
    exit_code = EXIT_NO_ANSIBLE_GALAXY

    def __init__(self) -> None:
        super().__init__(
            "ansible-galaxy executable not found on PATH. "
            "Install it via 'pip install ansible-core' (see requirements.txt) "
            "or use the Dockerfile builder stage."
        )


class AnsibleGalaxyInstallError(CollectionCacheError):
    exit_code = EXIT_NETWORK_ERROR

    def __init__(self, coll_spec: str, detail: str) -> None:
        self.coll_spec = coll_spec
        self.detail = detail
        super().__init__(
            f"ansible-galaxy collection install {coll_spec} failed:\n{detail}"
        )


def build_manifest(
    cache_dir: Path,
    resolved: List[Tuple[str, str, str, Path]],
) -> Dict[str, object]:
    """Build the stdout JSON manifest consumed by ``build.sh`` (Task 5.1)."""
    return {
        "cache_root": str(cache_dir),
        "collections": [
            {
                "name": f"{namespace}.{name}",
                "version": version,
                "path": str(path),
            }
            for namespace, name, version, path in resolved
        ],
    }


def cmd_ensure(args: argparse.Namespace) -> int:
    versions_path = Path(args.versions_file).expanduser().resolve()
    cache_dir = Path(args.cache_dir).expanduser().resolve()

    try:
        collections = parse_versions_file(versions_path)
    except FileNotFoundError:
        print(f"versions.env not found: {versions_path}", file=sys.stderr)
        return EXIT_NO_VERSIONS_FILE

    cache_dir.mkdir(parents=True, exist_ok=True)
    index = read_index(cache_dir)

    resolved: List[Tuple[str, str, str, Path]] = []
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat(
        timespec="seconds"
    )

    for full_name, (namespace, name, version) in sorted(collections.items()):
        try:
            target, status = ensure_collection(
                namespace=namespace,
                name=name,
                version=version,
                cache_dir=cache_dir,
                offline=args.offline,
            )
        except CollectionCacheError as exc:
            print(str(exc), file=sys.stderr)
            return exc.exit_code

        resolved.append((namespace, name, version, target))

        # Only update the timestamp when we actually downloaded; cache hits
        # leave the original ``downloaded_at`` intact for auditability.
        if status == "installed" or full_name not in index:
            index[full_name] = {
                "version": version,
                "downloaded_at": now_iso if status == "installed"
                else index.get(full_name, {}).get("downloaded_at", now_iso),
            }
        else:
            # Cache hit: still ensure the recorded version matches what we
            # actually used. If a stale entry pointed to a different version
            # but the on-disk cache had the requested one, prefer the truth
            # on disk.
            index[full_name] = {
                "version": version,
                "downloaded_at": index.get(full_name, {}).get(
                    "downloaded_at", now_iso
                ),
            }

    write_index(cache_dir, index)

    manifest = build_manifest(cache_dir, resolved)
    json.dump(manifest, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return EXIT_OK


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="collection_cache.py",
        description=(
            "Manage a versioned local cache of Ansible Galaxy collections "
            "for the arillso guide build pipeline."
        ),
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    ensure_parser = subparsers.add_parser(
        "ensure",
        help=(
            "Ensure all collections referenced in versions.env are present "
            "in the cache; download missing versions (unless --offline)."
        ),
    )
    ensure_parser.add_argument(
        "--versions-file",
        default="versions.env",
        help="Path to versions.env (default: versions.env in CWD)",
    )
    ensure_parser.add_argument(
        "--cache-dir",
        default=str(Path("~/.cache/arillso-collections").expanduser()),
        help=(
            "Cache root directory (default: ~/.cache/arillso-collections)"
        ),
    )
    ensure_parser.add_argument(
        "--offline",
        action="store_true",
        help=(
            "Refuse any network access. Exit 1 if any required collection "
            "version is missing from the cache."
        ),
    )
    ensure_parser.set_defaults(func=cmd_ensure)

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
