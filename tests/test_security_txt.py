"""Unit-Tests für ``scripts/security_txt.py``.

Geprüft wird die reine Renderfunktion, nicht der Sphinx-Build: letzterer
braucht Netz und den Collections-Cache und ist damit kein Unit-Test-Ziel.

Abgedeckte Cases:

* ``Expires`` ist gültiges ISO 8601 in UTC und liegt ein Jahr nach ``now``.
* Im Ergebnis bleibt kein ``{EXPIRES}``-Platzhalter stehen.
* Die Pflichtzeile ``Contact:`` ist vorhanden.
* Fehlt der Platzhalter im Template, wirft die Funktion ``ValueError`` —
  kein stiller Fallback auf eine Datei ohne Ablaufdatum.
* Ein naives ``now`` (ohne Zeitzone) wirft ``ValueError``.
* Der 29. Februar fällt auf den 28., statt ``replace(year=...)`` scheitern
  zu lassen.
"""

from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from security_txt import (  # noqa: E402
    EXPIRES_PLACEHOLDER,
    TEMPLATE_PATH,
    render_security_txt,
)

TEMPLATE = TEMPLATE_PATH.read_text(encoding="utf-8")


def _expires_value(rendered: str) -> str:
    for line in rendered.splitlines():
        if line.startswith("Expires:"):
            return line.split(":", 1)[1].strip()
    raise AssertionError("keine Expires-Zeile im Ergebnis")


def test_expires_is_one_year_after_now_in_utc() -> None:
    now = datetime(2026, 8, 10, 12, 30, 0, tzinfo=timezone.utc)

    expires = datetime.fromisoformat(_expires_value(render_security_txt(TEMPLATE, now)))

    assert expires.tzinfo is not None
    assert expires.utcoffset() == timedelta(0)
    assert expires == now.replace(year=now.year + 1)


def test_expires_has_no_microseconds() -> None:
    now = datetime(2026, 8, 10, 12, 30, 0, 123456, tzinfo=timezone.utc)

    expires = datetime.fromisoformat(_expires_value(render_security_txt(TEMPLATE, now)))

    assert expires.microsecond == 0


def test_no_placeholder_remains() -> None:
    rendered = render_security_txt(TEMPLATE, datetime.now(timezone.utc))

    assert EXPIRES_PLACEHOLDER not in rendered


def test_contact_line_present() -> None:
    rendered = render_security_txt(TEMPLATE, datetime.now(timezone.utc))

    assert any(line.startswith("Contact:") for line in rendered.splitlines())


def test_missing_placeholder_raises() -> None:
    with pytest.raises(ValueError):
        render_security_txt("Contact: mailto:security@arillso.io\n", datetime.now(timezone.utc))


def test_naive_now_raises() -> None:
    with pytest.raises(ValueError):
        render_security_txt(TEMPLATE, datetime(2026, 8, 10, 12, 0, 0))


def test_leap_day_falls_back_to_february_28() -> None:
    now = datetime(2028, 2, 29, 0, 0, 0, tzinfo=timezone.utc)

    expires = datetime.fromisoformat(_expires_value(render_security_txt(TEMPLATE, now)))

    assert (expires.year, expires.month, expires.day) == (2029, 2, 28)
