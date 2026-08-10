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

Aufgerufen wird das beim Einlesen von ``conf.py``, also bevor Sphinx
``html_extra_path`` validiert; ein späterer Event-Hook käme zu spät.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

EXPIRES_PLACEHOLDER = "{EXPIRES}"

# RFC 9116 §2.5.5 recommends less than a year of validity.
VALIDITY = timedelta(days=364)

REPO_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_PATH = REPO_ROOT / "_well_known" / "security.txt.in"
OUTPUT_DIR = REPO_ROOT / "_well_known_build" / ".well-known"
OUTPUT_PATH = OUTPUT_DIR / "security.txt"


def _expiry_from(now: datetime) -> datetime:
    """Gibt den Ablaufzeitpunkt zurück: ``now`` plus ``VALIDITY``.

    RFC 9116 §2.5.5 empfiehlt eine Gültigkeit von **weniger** als einem Jahr,
    deshalb 364 Tage statt exakt einem Jahr. Ein fester ``timedelta`` umgeht
    zugleich den Schalttag-Sonderfall, an dem ``replace(year=...)``
    ``ValueError: day is out of range for month`` wirft.
    """
    return now + VALIDITY


def render_security_txt(template_text: str, now: datetime) -> str:
    """Ersetzt den ``{EXPIRES}``-Platzhalter durch den Ablaufzeitpunkt.

    ``now`` muss zeitzonenbewusst sein — RFC 9116 verlangt einen Zeitstempel
    nach RFC 3339, und ein naives ``datetime`` liefert einen ohne Offset.
    Fehlt der Platzhalter, wirft die Funktion, statt still eine Datei ohne
    Ablaufdatum zu erzeugen.
    """
    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("now muss zeitzonenbewusst sein (z. B. datetime.now(timezone.utc))")
    if EXPIRES_PLACEHOLDER not in template_text:
        raise ValueError(f"Platzhalter {EXPIRES_PLACEHOLDER} fehlt im Template {TEMPLATE_PATH}")

    expires = _expiry_from(now).replace(microsecond=0)
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
