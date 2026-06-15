"""Unit-Tests für ``scripts/normalize_collections.py``.

Diese Tests rufen den Normalisierer als Subprozess auf — dasselbe Aufrufmuster,
das ``build.sh`` produktiv nutzt — und prüfen das beobachtbare Verhalten gegen
Fixture-RST-Dateien in einem temporären Verzeichnis.

Abgedeckte Cases:

* Wortgrenzen-Treffer (positiv) für ``Arillso``, ``Arillso.System``,
  ``Arillso.Agent``, ``Arillso.Container``.
* Negativ-Test: ``ArillsoCustomThing`` bleibt unverändert.
* Treffer in RST-Headings (Titel-Underline) und Link-Konstrukten
  (``:ref:``, externe Hyperlinks).
* Idempotenz: zweite Anwendung verändert nichts mehr.
* Ungültiger Collection-Name → Exit-Code 1 mit Datei-Pfad und Token
  in stderr.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

NORMALIZER = (
    Path(__file__).resolve().parent.parent / "scripts" / "normalize_collections.py"
)


def _run_normalize(root: Path, *extra_args: str) -> subprocess.CompletedProcess[str]:
    """Ruft ``normalize_collections.py`` als Subprozess auf.

    Bewusst der Subprocess-Pfad: matcht das Aufrufmuster aus ``build.sh``
    und vermeidet, dass Test-Imports den Skript-Lifecycle beeinflussen.
    """

    return subprocess.run(
        [
            sys.executable,
            str(NORMALIZER),
            "--root",
            str(root),
            *extra_args,
        ],
        capture_output=True,
        text=True,
        check=False,
    )


def test_word_boundary_positive_replaces_in_body(tmp_path: Path) -> None:
    """Arillso, Arillso.System, .Agent, .Container im Fliesstext → lowercase."""

    doc = tmp_path / "intro.rst"
    doc.write_text(
        "Einleitung\n"
        "==========\n\n"
        "Diese Seite nutzt Arillso.System, Arillso.Agent und Arillso.Container.\n"
        "Siehe auch Arillso selbst als Namespace.\n",
        encoding="utf-8",
    )

    result = _run_normalize(tmp_path)

    assert result.returncode == 0, (
        f"Normalizer failed unexpectedly.\nstdout={result.stdout!r}\n"
        f"stderr={result.stderr!r}"
    )
    content = doc.read_text(encoding="utf-8")
    assert "arillso.system" in content
    assert "arillso.agent" in content
    assert "arillso.container" in content
    # Standalone-Arillso wurde lowercased.
    assert "arillso selbst" in content
    # Keine Reste der Grossschreibung.
    assert "Arillso.System" not in content
    assert "Arillso.Agent" not in content
    assert "Arillso.Container" not in content


def test_word_boundary_negative_compound_untouched(tmp_path: Path) -> None:
    """Zusammengesetzte Wörter wie ``ArillsoCustomThing`` werden NICHT angefasst."""

    doc = tmp_path / "compound.rst"
    original = (
        "Compound-Token-Test\n"
        "===================\n\n"
        "Die Klasse ArillsoCustomThing bleibt unverändert.\n"
        "Auch ArillsoFoo und ArillsoBarBaz sind tabu.\n"
    )
    doc.write_text(original, encoding="utf-8")

    result = _run_normalize(tmp_path)

    assert result.returncode == 0, (
        f"stdout={result.stdout!r}\nstderr={result.stderr!r}"
    )
    content = doc.read_text(encoding="utf-8")
    assert "ArillsoCustomThing" in content
    assert "ArillsoFoo" in content
    assert "ArillsoBarBaz" in content
    # Datei darf gar nicht verändert worden sein.
    assert content == original


def test_replacement_in_headings_and_links(tmp_path: Path) -> None:
    """Treffer in RST-Title-Underlines, ``:ref:``-Targets und Hyperlinks."""

    doc = tmp_path / "headings.rst"
    doc.write_text(
        "Arillso.System Übersicht\n"
        "========================\n\n"
        "Siehe :ref:`Arillso.Agent <arillso-agent-ref>` für Details.\n\n"
        "Externer Link: `Arillso.Container Docs"
        " <https://example.test/arillso.container>`_\n\n"
        "Und ein Standalone-Verweis auf Arillso.\n",
        encoding="utf-8",
    )

    result = _run_normalize(tmp_path)

    assert result.returncode == 0, (
        f"stdout={result.stdout!r}\nstderr={result.stderr!r}"
    )
    content = doc.read_text(encoding="utf-8")

    # Heading-Text normalisiert.
    assert content.splitlines()[0] == "arillso.system Übersicht"
    # ``:ref:`` Text-Anteil normalisiert.
    assert ":ref:`arillso.agent <arillso-agent-ref>`" in content
    # Hyperlink-Text-Anteil normalisiert.
    assert "`arillso.container Docs" in content
    # Standalone-Arillso normalisiert.
    assert "Verweis auf arillso." in content
    # Keine Grossschreibung-Reste.
    assert "Arillso" not in content


def test_idempotency_second_run_is_noop(tmp_path: Path) -> None:
    """Zweiter Normalisierungs-Lauf produziert KEINE weiteren Änderungen."""

    doc = tmp_path / "idem.rst"
    doc.write_text(
        "Idem-Test\n"
        "=========\n\n"
        "Arillso.System, Arillso.Agent, Arillso.Container, Arillso.\n",
        encoding="utf-8",
    )

    first = _run_normalize(tmp_path)
    assert first.returncode == 0, f"first run failed: {first.stderr!r}"
    after_first = doc.read_text(encoding="utf-8")

    second = _run_normalize(tmp_path)
    assert second.returncode == 0, f"second run failed: {second.stderr!r}"
    after_second = doc.read_text(encoding="utf-8")

    # Inhalt identisch nach zweitem Run.
    assert after_first == after_second
    # Im stdout des zweiten Runs darf kein Datei-Modify gemeldet werden.
    assert "0 file(s)" in second.stdout, (
        f"Expected no-op stdout, got: {second.stdout!r}"
    )


def test_url_and_email_contexts_not_flagged(tmp_path: Path) -> None:
    """``arillso.io`` in URLs/E-Mails/Subdomains ist KEINE Collection.

    Regression für die zu gierige ``arillso.<sub>``-Erkennung, die
    ``hello@arillso.io`` (E-Mail), ``https://arillso.io`` (URL) und
    ``guide.arillso.io`` (Subdomain) als ungültige Collection ``arillso.io``
    gemeldet hat. Vor dem Lookbehind-Fix wäre dies Exit-Code 1 gewesen.
    """

    doc = tmp_path / "contact.rst"
    original = (
        "Kontakt\n"
        "=======\n\n"
        "Schreib an hello@arillso.io oder besuche https://arillso.io/docs.\n"
        "Die Doku liegt unter https://guide.arillso.io.\n"
    )
    doc.write_text(original, encoding="utf-8")

    result = _run_normalize(tmp_path)

    assert result.returncode == 0, (
        f"URL/email contexts wrongly flagged.\nstdout={result.stdout!r}\n"
        f"stderr={result.stderr!r}"
    )
    # Inhalt unverändert — kein Token war eine echte Collection.
    assert doc.read_text(encoding="utf-8") == original


def test_doc_placeholder_collection_not_flagged(tmp_path: Path) -> None:
    """Generischer Platzhalter ``arillso.collection.<role>`` bleibt unangetastet.

    In Anleitungen steht ``arillso.collection.role_name`` als Schablone; das ist
    keine reale Collection und darf weder gemeldet noch normalisiert werden.
    Gross- wie Kleinschreibung des Platzhalters wird abgedeckt.
    """

    doc = tmp_path / "guide.rst"
    original = (
        "Rollen-Beispiel\n"
        "===============\n\n"
        "   - role: arillso.collection.role_name\n"
        "   - role: arillso.COLLECTION.ROLE_NAME\n"
    )
    doc.write_text(original, encoding="utf-8")

    result = _run_normalize(tmp_path)

    assert result.returncode == 0, (
        f"placeholder wrongly flagged.\nstdout={result.stdout!r}\n"
        f"stderr={result.stderr!r}"
    )
    # Platzhalter bleibt wörtlich erhalten (kein Casing-Eingriff).
    assert doc.read_text(encoding="utf-8") == original


def test_real_typo_still_flagged_despite_relaxations(tmp_path: Path) -> None:
    """Ein echter Tippfehler (`arillso.systen`) wird weiterhin als ungültig gemeldet.

    Stellt sicher, dass die URL-/E-Mail-/Platzhalter-Ausnahmen die echte
    Whitelist-Prüfung nicht aufweichen.
    """

    doc = tmp_path / "typo.rst"
    doc.write_text(
        "Typo-Test\n"
        "=========\n\n"
        "Hier referenziert jemand arillso.systen statt arillso.system.\n",
        encoding="utf-8",
    )

    result = _run_normalize(tmp_path)

    assert result.returncode == 1, (
        f"expected exit 1 for real typo, got {result.returncode}\n"
        f"stdout={result.stdout!r}\nstderr={result.stderr!r}"
    )
    assert "arillso.systen" in result.stderr, (
        f"typo token missing from stderr: {result.stderr!r}"
    )


def test_invalid_collection_name_exits_one_with_path_and_token(
    tmp_path: Path,
) -> None:
    """Ungültiger Name (`arillso.NonExistent`) → Exit 1, Pfad+Token in stderr."""

    doc = tmp_path / "invalid.rst"
    doc.write_text(
        "Invalid-Test\n"
        "============\n\n"
        "Hier wird arillso.NonExistent referenziert, was nicht erlaubt ist.\n",
        encoding="utf-8",
    )

    result = _run_normalize(tmp_path)

    assert result.returncode == 1, (
        f"expected exit 1, got {result.returncode}\n"
        f"stdout={result.stdout!r}\nstderr={result.stderr!r}"
    )
    # Datei-Pfad muss in stderr genannt sein.
    assert str(doc) in result.stderr, (
        f"file path missing from stderr: {result.stderr!r}"
    )
    # Der konkrete Collection-Name muss in stderr auftauchen.
    assert "arillso.NonExistent" in result.stderr, (
        f"invalid token missing from stderr: {result.stderr!r}"
    )
    # Datei darf nicht modifiziert worden sein (zwei-Phasen-Verarbeitung).
    assert "arillso.NonExistent" in doc.read_text(encoding="utf-8")
