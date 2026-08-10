#!/usr/bin/env python3
"""Rendert ``.well-known/security.txt`` (RFC 9116) zur Build-Zeit.

GitHub Pages liefert nur statische Dateien, RFC 9116 §2.5 verlangt aber ein
``Expires``-Feld. Ein hart eingetragenes Datum liefe irgendwann ab und machte
die Datei ungültig — schlechter als gar keine. Deshalb steht im Repo nur ein
Template mit ``{EXPIRES}``-Platzhalter; das Datum entsteht bei jedem
Sphinx-Build und wandert damit bei jedem Merge auf ``main`` mit.

Bekannte Grenze: bleibt ``main`` zwölf Monate ohne Merge, läuft die Datei ab.
``nightly-security.yml`` deployt nicht. Ein Cron-Deploy wäre die Erweiterung,
falls das eintritt.

Eingehängt wird das Ergebnis über den ``builder-inited``-Hook in ``conf.py``
und ``html_extra_path``.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

EXPIRES_PLACEHOLDER = "{EXPIRES}"

REPO_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_PATH = REPO_ROOT / "_well_known" / "security.txt.in"
OUTPUT_DIR = REPO_ROOT / "_well_known_build" / ".well-known"
OUTPUT_PATH = OUTPUT_DIR / "security.txt"


def _one_year_later(now: datetime) -> datetime:
    """Gibt ``now`` plus ein Jahr zurück, mit Sonderfall 29. Februar.

    ``replace(year=...)`` wirft am Schalttag ``ValueError: day is out of range
    for month``, weil das Folgejahr keinen 29. Februar hat. In dem Fall wird
    auf den 28. gekürzt.
    """
    try:
        return now.replace(year=now.year + 1)
    except ValueError:
        return now.replace(year=now.year + 1, day=28)


def render_security_txt(template_text: str, now: datetime) -> str:
    """Ersetzt den ``{EXPIRES}``-Platzhalter durch ``now`` plus ein Jahr.

    ``now`` muss zeitzonenbewusst sein — RFC 9116 verlangt einen Zeitstempel
    nach RFC 3339, und ein naives ``datetime`` liefert einen ohne Offset.
    Fehlt der Platzhalter, wirft die Funktion, statt still eine Datei ohne
    Ablaufdatum zu erzeugen.
    """
    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("now muss zeitzonenbewusst sein (z. B. datetime.now(timezone.utc))")
    if EXPIRES_PLACEHOLDER not in template_text:
        raise ValueError(f"Platzhalter {EXPIRES_PLACEHOLDER} fehlt im Template {TEMPLATE_PATH}")

    expires = _one_year_later(now).replace(microsecond=0)
    return template_text.replace(EXPIRES_PLACEHOLDER, expires.isoformat())


def write_security_txt(now: datetime) -> Path:
    """Rendert das Template und schreibt das Ergebnis nach ``OUTPUT_PATH``."""
    if not TEMPLATE_PATH.is_file():
        raise FileNotFoundError(f"security.txt-Template fehlt: {TEMPLATE_PATH}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        render_security_txt(TEMPLATE_PATH.read_text(encoding="utf-8"), now),
        encoding="utf-8",
    )
    return OUTPUT_PATH
