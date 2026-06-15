# Manuelle Regressions-Checkliste

## Zweck

Diese Checkliste verifiziert die **visuelle und funktionale Parität**
der gebauten Dokumentation gegenüber der Pre-Refactoring-Baseline
(Requirement 1.6, 5.7, 3.7). Sie dient als manuelles Test-Surrogat
für Aspekte, die sich nicht sinnvoll automatisieren lassen
(Pixel-Layout, Browser-Interaktion, Tastatur-Fokus,
Mobile-Verhalten).

Konkret stellt sie sicher, dass die Phasen 2 (Frontend-Modularisierung)
und 3 (Build-Pipeline-Integration) keine sichtbaren Regressionen
in der ausgelieferten HTML-Doku eingeführt haben.

## Wann ausführen?

- **Vor jedem Release-Tag** (Pflicht-Gate gemäß Requirement 5.7).
- Nach grösseren Frontend-Änderungen
  (z. B. Token-Refaktorierung, neue Komponente, Build-Pipeline-Umbau).
- Nach Änderungen an `_templates/`, `src/styles/` oder `src/scripts/`.
- Nach Upgrade von Sphinx, Furo-Theme oder antsibull-docs.

## Wie ausführen?

1. Sauberen Build erzeugen:

   ```bash
   ./build.sh
   ```

2. Output im lokalen Browser öffnen:

   ```bash
   xdg-open build/html/index.html   # Linux
   open build/html/index.html       # macOS
   ```

3. Diese Checkliste sequenziell durchgehen und jeden Punkt
   abhaken. Falls ein Punkt fehlschlägt: Befund unter dem
   jeweiligen Abschnitt notieren und Release blockieren, bis
   behoben.

4. Browser-DevTools-Konsole offen halten (F12) — JS-Konsolenfehler
   sind ein Fail-Kriterium (Requirement 3.7).

5. Nach Abschluss: Datei mit abgehakten Boxen committen, damit
   der Lauf nachvollziehbar bleibt (`git commit -m "test: pre-release regression check vX.Y.Z"`).

## Baseline-Build-Zeit

Vor dem ersten Refactoring-Merge auf `main` festzuhalten:

- Lokale Wallclock-Zeit `./build.sh`: _TBD_
- CI-Wallclock-Zeit Build-Job: _TBD_

Aktueller Lauf darf nicht signifikant (> 20 %) über der Baseline
liegen.

---

## Layout-Stichproben

Visuelle Inspektion repräsentativer Seitenklassen. Browser:
Aktueller Chrome/Firefox, Desktop-Viewport ≥ 1280 px.

- [ ] **Index-Seite** `build/html/index.html` lädt vollständig:
      Logo links oben, Hauptüberschrift, Sidebar links sichtbar,
      Inhaltsbereich gefüllt, Footer am unteren Rand.
- [ ] **Guide-Landing** `build/html/guide/index.html` rendert
      Sektionsübersicht (Getting Started, Best Practices,
      Development, Reference, Tutorials) als Karten/Listen
      ohne Überlappung.
- [ ] **Einzelne Guide-Seite** `build/html/guide/getting-started/quickstart.html`
      zeigt Headings (H1, H2, H3) in korrekter Hierarchie,
      Absatzabstände konsistent mit Token-Definitionen.
- [ ] **Code-Block-Beispiel** auf `build/html/guide/getting-started/quickstart.html`
      oder `build/html/containers/docker_ansible.html`: monospaced
      Schrift, dunkler/heller Hintergrund je Theme, kein
      Overflow-Cutoff über volle Container-Breite.
- [ ] **Collection-Landing** unter
      `build/html/collections/arillso/system/index.html`
      (oder analoger antsibull-docs-Output) listet Module/Rollen
      mit Beschreibungstabelle ohne Layout-Bruch.
- [ ] **404-Seite** (falls vom Theme bereitgestellt — manuell URL
      `build/html/does-not-exist.html` aufrufen): zeigt
      Fehlerseite mit Navigation zurück zur Index, nicht eine
      kaputte Skeleton-Seite.

## Navigations-Stichproben

Interaktion mit Sidebar, Breadcrumbs und Link-Verhalten.

- [ ] **Sidebar Expand/Collapse**: auf `build/html/index.html`
      die ausklappbaren Sidebar-Knoten (Guide, Containers,
      Libraries, GitHub) per Klick öffnen und schließen — Pfeil
      rotiert, Unterpunkte erscheinen ohne Layout-Sprung.
- [ ] **Breadcrumbs**: auf
      `build/html/guide/best-practices/security.html`
      sind Breadcrumbs sichtbar
      (`Home › Guide › Best Practices › Security`); jeder
      Crumb ist ein funktionierender Link.
- [ ] **Interne Links**: auf `build/html/guide/index.html` zu
      mindestens drei internen Zielen (z. B. Quickstart,
      Architecture, Troubleshooting) klicken — alle laden ohne
      404 und mit korrekter Scrollposition (Anker oder Top).
- [ ] **Sidebar-Aktiv-Status**: auf
      `build/html/guide/getting-started/quickstart.html`
      ist der entsprechende Sidebar-Eintrag visuell als „aktiv"
      hervorgehoben (z. B. Bold, Akzentfarbe, Indikator-Bar).
- [ ] **Externe Links mit Icon**: Externer Link (z. B. zu
      `https://github.com/arillso/`) auf einer Guide-Seite zeigt
      das External-Link-Icon (↗ oder ähnlich) und öffnet in
      neuem Tab (`target="_blank"`).
- [ ] **Anker-Sprungmarken**: in einem längeren Dokument
      (z. B. `build/html/guide/best-practices/standards.html`)
      klick auf TOC-Eintrag → Browser scrollt zur korrekten
      H2/H3 ohne Versatz unter den Sticky-Header.

## Code-Block-Rendering

Funktion und Erscheinungsbild der Code-Komponente. Quelle
typischer Code-Blöcke: jede Quickstart- oder Tutorial-Seite.

- [ ] **Copy-Button erscheint**: auf
      `build/html/guide/getting-started/quickstart.html` zeigt
      jeder Code-Block beim Hover (oder permanent auf Mobile)
      einen Copy-Button in der rechten oberen Ecke.
- [ ] **Copy-Button funktioniert**: Klick auf Copy-Button
      kopiert den Block-Inhalt in die Zwischenablage —
      Verifikation durch Einfügen in ein Terminal oder
      Text-Editor; Button zeigt kurzes Erfolgs-Feedback
      („Copied" o. ä.).
- [ ] **Syntax-Highlighting korrekt**: YAML-Blöcke
      (typisch in `build/html/github/action_playbook.html`)
      heben Schlüssel, Werte, Strings, Kommentare farblich
      ab — kein einfarbiger Plaintext.
- [ ] **Language-Badge**: jeder Code-Block zeigt die
      Sprache (z. B. `yaml`, `bash`, `python`) als kleines
      Label oder Datatag oben am Block.
- [ ] **Inline-Code-Styling**: Inline-`monospace`-Snippets
      in Fließtext (z. B. Modul-Namen, Pfade in
      `build/html/guide/reference/troubleshooting.html`)
      haben subtilen Hintergrund und sind klar vom Fließtext
      abgesetzt.
- [ ] **Long-Line-Verhalten**: Code-Block mit Zeile > 100
      Zeichen scrollt horizontal innerhalb des Blocks
      (oder bricht um, je nach Konvention) — kein Bruch des
      Seitenlayouts, kein Page-Scroll horizontal.

## Mobile-Stichprobe (Viewport 375 px)

Chrome DevTools → Device Toolbar → iPhone SE / 375 × 667 px.

- [ ] **Kein horizontaler Scroll auf Index**:
      `build/html/index.html` bei 375 px zeigt keinen
      horizontalen Scrollbalken am Body; Inhalte passen in
      Viewport-Breite.
- [ ] **Hamburger-Menü (falls vorhanden)**: Sidebar ist bei
      < 768 px hinter Hamburger-Icon versteckt; Klick öffnet
      Sidebar als Overlay/Drawer; Schließen via X oder Klick
      auf Backdrop funktioniert.
- [ ] **Code-Blöcke wrappen oder scrollen sauber**: auf
      `build/html/guide/getting-started/quickstart.html`
      bei 375 px brechen Code-Blöcke entweder um oder
      scrollen intern — der Page-Body bleibt 375 px breit.
- [ ] **Touch-Targets ≥ 44 × 44 px**: Sidebar-Links und
      Buttons (z. B. Copy-Button, Hamburger) sind mit dem
      Finger treffbar — visuell prüfen, kein 12-px-Mini-Link.
- [ ] **Typografie skaliert**: Body-Text bleibt lesbar
      (≥ 14 px effektiv), H1 nicht so gross dass er den
      gesamten Viewport-First-View einnimmt; Line-Length
      bleibt im lesbaren Bereich (≈ 30–75 Zeichen pro Zeile).
- [ ] **Tabellen-Verhalten**: Modul-Tabellen auf
      `build/html/collections/arillso/system/index.html`
      bei 375 px brechen entweder um, scrollen intern oder
      stapeln responsive — kein Page-Layout-Bruch.

## Tastatur-Navigation

Mausunabhängige Bedienung — Voraussetzung für A11y und Power-User.

- [ ] **Tab durch Index**: ab `build/html/index.html`
      `Tab` gedrückt halten bzw. zyklisch betätigen — Fokus
      durchläuft Skip-Link, Logo-Link, Sidebar-Items,
      Hauptinhalt-Links, Footer-Links in sichtbarer,
      logischer Reihenfolge.
- [ ] **Sichtbarer Fokus auf jedem interaktiven Element**:
      jeder Tab-Stop zeigt einen sichtbaren Fokus-Indikator
      (Outline, Underline oder Background-Change) — kein
      verschwundener Fokus, kein nur-Browser-Default falls
      Custom-Outlines verwendet werden.
- [ ] **Keine Fokus-Fallen**: in der Sidebar
      (z. B. ausklappbarer Knoten „Guide") kein Punkt, an dem
      Tab/Shift+Tab den Fokus nicht mehr weiterbewegen kann.
- [ ] **Enter aktiviert Links/Buttons**: auf einem fokussierten
      Sidebar-Link `Enter` navigiert; auf einem fokussierten
      Copy-Button `Enter` oder `Space` kopiert.
- [ ] **Skip-Link funktioniert**: erstes `Tab` von oben zeigt
      einen Skip-Link „Zum Hauptinhalt springen" (oder
      „Skip to content"); Aktivierung springt zum Main-Content
      und überspringt die Sidebar.
- [ ] **Escape schließt Overlays**: falls Mobile-Drawer oder
      Modal vorhanden, `Esc` schliesst diese und stellt Fokus
      auf den auslösenden Trigger zurück.

---

## Befund-Log

Wenn ein Punkt fehlschlägt, hier protokollieren:

| Datum | Punkt | Befund | Fix-Issue/PR |
|-------|-------|--------|--------------|
|       |       |        |              |

## Sign-Off

- [ ] Alle Punkte oben abgehakt oder Befunde dokumentiert.
- Ausgeführt von: ______________________
- Datum: ______________________
- Release-Tag: ______________________
