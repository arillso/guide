#!/usr/bin/env python3
"""Collection-Namen-Normalisierer für RST-Dokumentation.

Ersetzt die bisherige ``sed``-Pipeline. Liest alle ``*.rst``-Dateien unter dem
angegebenen ``--root``-Verzeichnis und normalisiert Namespace-Tokens
(``Arillso`` -> ``arillso``, ``.System``/``.Agent``/``.Container`` -> lowercase)
**nur an Wortgrenzen**. Das heißt: ``ArillsoCustomThing`` bleibt unverändert,
während ``Arillso``, ``Arillso.System``, ``arillso.Agent`` etc. zur kanonischen
Kleinschreibung normalisiert werden.

Siehe
``.kiro/specs/refactoring-structure-to-modern-best-practices/design.md``
Abschnitt 6.3 sowie Tasks 3.2 / Requirements 1.3, 2.6, 2.7.

CLI:

    python scripts/normalize_collections.py \
        --root rst \
        [--collections arillso.system arillso.agent arillso.container] \
        [--dry-run]

Exit-Codes:

* ``0`` -- Erfolg; alle gefundenen Collection-Tokens sind in der Whitelist.
* ``1`` -- Ein ungültiger Collection-Name (nicht in ``--collections``) wurde
  in mindestens einer Datei gefunden. Stderr enthält Datei-Pfad und
  Zeilennummer für jeden Fund.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import List, Sequence, Set, Tuple

# Default-Whitelist gemäß design §6.3 und tasks.md §3.2.
DEFAULT_COLLECTIONS: Tuple[str, ...] = (
    "arillso.system",
    "arillso.agent",
    "arillso.container",
)

# Regex 1: ``arillso.<Sub>`` an Wortgrenzen, beide Seiten case-insensitive.
# Wird genutzt, um (a) Casing-Normalisierung durchzuführen und (b) zu prüfen,
# ob ``<Sub>`` (lowercased) in der Whitelist erscheint.
_DOTTED_RE = re.compile(r"\b(?:arillso)\.([A-Za-z][A-Za-z0-9_]*)\b", re.IGNORECASE)

# Regex 2: standalone ``Arillso`` an Wortgrenzen mit Großbuchstaben am Anfang.
# Greift NICHT in zusammengesetzten Wörtern wie ``ArillsoCustomThing`` (folgt
# Großbuchstabe ohne Wortgrenze) -- ``\b`` stellt zusammen mit ``(?![A-Za-z0-9_])``
# sicher, dass nach dem Token entweder ein Nicht-Wortzeichen oder Dateiende kommt.
# Wir kombinieren beides explizit, um robust gegen alle Eingabevarianten zu sein.
_STANDALONE_ARILLSO_RE = re.compile(r"\bArillso\b(?![A-Za-z0-9_])")


def _normalize_text(
    text: str,
    allowed: Set[str],
    *,
    file_path: Path,
    invalid_findings: List[Tuple[Path, int, str]],
) -> Tuple[str, int]:
    """Wendet die Normalisierungs-Patterns auf den Datei-Text an.

    Returns:
        Tupel ``(neuer_text, replacement_count)``.
    """

    replacements = 0

    def _dotted_sub(match: re.Match[str]) -> str:
        nonlocal replacements
        sub = match.group(1)
        canonical = f"arillso.{sub.lower()}"
        original = match.group(0)
        # Whitelist-Check passiert immer, unabhängig von Änderung -- so erkennen
        # wir auch bereits-lowercased ungültige Namen wie ``arillso.UnknownThing``
        # oder ``arillso.foo``.
        if canonical not in allowed:
            # Zeilennummer durch Position im Originaltext berechnen.
            line_no = text.count("\n", 0, match.start()) + 1
            invalid_findings.append((file_path, line_no, original))
        if original != canonical:
            replacements += 1
        return canonical

    new_text = _DOTTED_RE.sub(_dotted_sub, text)

    def _standalone_sub(_match: re.Match[str]) -> str:
        nonlocal replacements
        replacements += 1
        return "arillso"

    new_text = _STANDALONE_ARILLSO_RE.sub(_standalone_sub, new_text)

    return new_text, replacements


def _iter_rst_files(root: Path) -> List[Path]:
    """Liefert eine sortierte Liste aller ``*.rst``-Dateien unter ``root``."""

    return sorted(p for p in root.rglob("*.rst") if p.is_file())


def normalize_tree(
    root: Path,
    allowed: Sequence[str],
    *,
    dry_run: bool = False,
) -> Tuple[int, int, List[Tuple[Path, int, str]]]:
    """Normalisiert alle RST-Dateien unter ``root``.

    Zwei-Phasen-Verarbeitung: zuerst wird der gesamte Baum gescannt und
    geplante Änderungen werden im Speicher gehalten. Werden in irgendeiner
    Datei ungültige Collection-Namen entdeckt, erfolgt **kein** Schreibvorgang
    -- so bleibt der Baum konsistent und der Fehler ist klar zuordenbar.

    Returns:
        ``(geänderte_dateien, gesamt_ersetzungen, invalid_findings)``.
    """

    allowed_set: Set[str] = {name.lower() for name in allowed}
    total_replacements = 0
    invalid_findings: List[Tuple[Path, int, str]] = []
    pending_writes: List[Tuple[Path, str, int]] = []

    for path in _iter_rst_files(root):
        try:
            original = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            print(
                f"warn: skipping non-UTF-8 file: {path}",
                file=sys.stderr,
            )
            continue

        new_text, replacements = _normalize_text(
            original,
            allowed_set,
            file_path=path,
            invalid_findings=invalid_findings,
        )

        if new_text != original:
            total_replacements += replacements
            pending_writes.append((path, new_text, replacements))

    # Bei Whitelist-Verletzungen NICHT schreiben -- der Aufrufer (build.sh)
    # erwartet sonst ein konsistentes Pre-/Post-Image.
    if invalid_findings:
        return 0, 0, invalid_findings

    changed_files = len(pending_writes)
    for path, new_text, replacements in pending_writes:
        if dry_run:
            print(f"M {path} ({replacements} replacements)")
        else:
            path.write_text(new_text, encoding="utf-8")

    return changed_files, total_replacements, invalid_findings


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="normalize_collections.py",
        description=(
            "Normalisiert Arillso-Collection-Tokens (Arillso, .System, .Agent, "
            ".Container) in RST-Dateien an Wortgrenzen zur kanonischen "
            "Kleinschreibung."
        ),
    )
    parser.add_argument(
        "--root",
        required=True,
        type=Path,
        help="Verzeichnis, das rekursiv nach *.rst-Dateien durchsucht wird.",
    )
    parser.add_argument(
        "--collections",
        nargs="+",
        default=list(DEFAULT_COLLECTIONS),
        metavar="NAME",
        help=(
            "Whitelist gültiger Collection-Namen (Form: <namespace>.<name>). "
            f"Default: {' '.join(DEFAULT_COLLECTIONS)}."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help=(
            "Schreibt keine Änderungen; listet nur Dateien, die sich ändern "
            "würden."
        ),
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    root: Path = args.root
    if not root.exists():
        print(f"error: --root path does not exist: {root}", file=sys.stderr)
        return 2
    if not root.is_dir():
        print(f"error: --root is not a directory: {root}", file=sys.stderr)
        return 2

    changed, replacements, invalid = normalize_tree(
        root,
        args.collections,
        dry_run=args.dry_run,
    )

    if invalid:
        # Deterministische Sortierung der Fehler-Ausgabe.
        for path, line_no, token in sorted(invalid, key=lambda t: (str(t[0]), t[1])):
            print(
                f"error: invalid collection name {token!r} at {path}:{line_no}",
                file=sys.stderr,
            )
        print(
            f"error: {len(invalid)} invalid collection reference(s) detected; "
            f"allowed: {', '.join(sorted(set(c.lower() for c in args.collections)))}",
            file=sys.stderr,
        )
        return 1

    if args.dry_run:
        print(
            f"Dry-run: would normalize {changed} file(s), "
            f"{replacements} total replacement(s)."
        )
    else:
        print(
            f"Normalized {changed} file(s), {replacements} total replacement(s)."
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
