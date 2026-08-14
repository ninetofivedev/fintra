# Fintra – Release Notes

Diese Datei fasst die bisher separat gepflegten Release Notes der Fintra-V9-Reihe zusammen.

Die Einträge sind **absteigend nach Version** sortiert. Inhaltliche Aussagen aus den ursprünglichen Notes wurden beibehalten; wiederkehrende „Basis/Grundbasis“-Hinweise wurden entfernt und die Markdown-Struktur vereinheitlicht.

> **Hinweis:** Für Versionen, zu denen keine separate Notes-Datei vorlag, wurde kein Eintrag ergänzt. Dadurch bleibt die Historie auf die tatsächlich dokumentierten Änderungen beschränkt.

---
## 9.6.0-beta.5

### Fixed
- Einheitliche Transaktions-Datumsanzeige im Format `TT.MM.JJJJ` auf Desktop und Smartphone.
- Datumsanzeige der IQR-Ausreißer auf der Analyse-Seite korrigiert.
- Gemeinsame serverseitige Formatierungsfunktion für angezeigte ISO-Datumswerte eingeführt.

### Cleanup
- Veraltete Mobile-CSS-Regeln entfernt.
- Nicht mehr verwendete Burger-Menü-CSS-Regeln entfernt.
- Projektweite aktuelle Versionsreferenzen auf `9.6.0-beta.5` aktualisiert.
- `BETA_RELEASE_NOTES.md` zugunsten dieser zentralen Release-Historie entfernt.
- `.directory` wird künftig von Git ignoriert.

---

## 9.6.0-beta.4

### Mobile
- Bugfix auf Buchungsübersicht

---

## 9.6.0-beta.3

### Mobile
- Kompaktere Buchungskarten für Smartphones.
- Datum und Transaktionstyp wurden in einer gemeinsamen Kopfzeile verdichtet.
- Kategorie und Betrag werden nebeneinander dargestellt.
- Kommentar und Aktionsbereich benötigen deutlich weniger vertikalen Platz.
- Die Desktop-Tabelle bleibt unverändert.

---

## 9.5.15

- Der bisherige reine Benutzername im Burger-Menü ist jetzt ein normaler Menübutton.
- Neuer lokaler Account-Icon.
- Klick auf den Benutzernamen öffnet `/profile`.
- Profilseite zeigt das Benutzerkonto und ermöglicht Passwortänderungen.
- Passwortänderung erfordert das aktuelle Passwort.
- Neues Passwort: mindestens 10 Zeichen, Bestätigung erforderlich.
- Das neue Passwort darf nicht identisch mit dem aktuellen Passwort sein.
- Passwort wird weiterhin ausschließlich als scrypt-Hash gespeichert.
- CSRF-Schutz bleibt aktiv.

---

## 9.5.14

- `visibility_off.svg` komplett neu gezeichnet.
- Privacy-CSS überarbeitet: der Modus verändert nur noch `filter` und
  `user-select`, nicht mehr `display` oder andere Layout-Eigenschaften.
- Dadurch bleiben die Beträge in den Income-/Expense-Cards auf der Startseite
  beim Aktivieren des Privacy-Modus exakt an ihrer Position.

---

## 9.5.13

- Privacy-Modus auf der Startseite korrigiert.
- Tabellenzellen behalten beim Blur ihre normale `table-cell`-Darstellung.
- Mobile Zahlenzeilen behalten ihr bestehendes Flex-Layout.
- Der Privacy-Modus verändert damit nur noch die Sichtbarkeit der Beträge,
  nicht mehr deren Anordnung.

---

## 9.5.12

- Neuer Augen-Button direkt neben dem Theme-Button.
- Ein Klick blendet die Finanzbeträge der aktuellen Seite per Blur aus.
- Ein weiterer Klick macht die Beträge wieder sichtbar.
- Zustand wird im Browser gespeichert und bleibt beim Seitenwechsel erhalten.
- Lokale Offline-Icons `visibility.svg` und `visibility_off.svg`.
- Betroffen sind Dashboard-/Monatsbeträge, Fixkostenfelder, Budgets,
  Finanzwerte der Analyse und Finanzdiagramme.
- Nicht-finanzielle A&D-Benchmarkwerte, Kategorien, Prozentwerte und Daten
  bleiben lesbar.

---

## 9.5.5

### Behobene Fehler
- Kategorien mit Budget-Referenzen werden beim Löschen jetzt deaktiviert statt
  einen Foreign-Key-Fehler auszulösen.
- Temporäre SQLite-Backup-Dateien werden nach dem Download automatisch gelöscht.
- Fixkosten zeigen bei ungültigen Geldbeträgen nun wie Monatsbuchungen/Budgets
  einen Dialog statt einer blanken Fehlerseite.
- Der synthetische Top-K-Benchmark vergleicht Sortierung und Min-Heap jetzt
  tatsächlich über `n` Transaktionen. Messung und Big-O-Erklärung beziehen sich
  damit auf denselben Datenumfang.

### Optimierungen
- Jahresübersicht: variable Monatswerte werden mit einer gruppierten SQL-Abfrage
  statt 24 Einzelabfragen geladen.
- Datumsfilter wurden auf indexfreundliche Bereichsabfragen umgestellt.
- Fixkosten-Import vermeidet N+1-Abfragen.
- Budget-Speicherung validiert Kategorien mit einer Vorab-Abfrage.
- `.dockerignore` verhindert, dass Finanzdaten, `.env` und Python-Caches in den
  Docker-Build-Kontext gelangen.
- Docker setzt `PYTHONDONTWRITEBYTECODE=1` und `PYTHONUNBUFFERED=1`.
- ungenutzte Funktion `category_suggestion`, ungenutzte CSS-Hilfsklasse und
  vorhandener `__pycache__` wurden entfernt.

### Prüfung
- Python-Syntax: OK
- 10 Jinja-Templates: OK
- CSS-Parser: 0 Fehler
- 23 gerenderte Inline-JavaScript-Blöcke: 0 Syntaxfehler
- SQLite `integrity_check`: OK
- SQLite `foreign_key_check`: 0 Fehler
- Hauptseiten inklusive 100.000er A&D-Test: HTTP 200
- 24 lokale Icon-Dateien vorhanden
- keine externen Frontend-URLs in den Templates

---

## 9.5.4

- Logout-Icon hat im Normalzustand wieder dieselbe Farbe wie die übrigen Burger-Menü-Icons.
- Erst beim Hover über „Abmelden“ werden Text und Logout-Icon gemeinsam rot (`#c9362b`).

---

## 9.5.3

- Das Logout-Icon im Burger-Menü ist jetzt dauerhaft rot.
- Verwendet exakt dieselbe Farbe wie der bestehende Logout-Hoverzustand: `#c9362b`.
- Der Text bleibt im Normalzustand unverändert und wird wie bisher erst beim Hover rot.

---

## 9.5.2

- Dashboard und Analyse laden Chart.js nicht mehr direkt aus einem CDN.
- Beide Templates verwenden `/static/vendor/chart.umd.min.js`.
- Docker lädt beim Image-Build fest gepinnt Chart.js 4.5.1 in das Image.
- Danach funktioniert Chart.js im laufenden Fintra-Container ohne Internet.
- Material-/SVG-Icons bleiben ebenfalls vollständig lokal.
- Chart.js-Lizenzhinweis liegt unter `app/static/vendor/chartjs-LICENSE.txt`.
- Versionsanzeige im Burger-Menü: V9.5.2.

Wichtig: Ein erstmaliger neuer Docker-Build benötigt Internetzugriff, damit Docker
die gepinnte Chart.js-Datei herunterladen kann. Der laufende Container benötigt
diese Verbindung anschließend nicht mehr.

---

## 9.5.1

- Google-Fonts-Verbindung für Material Symbols entfernt.
- Neuer Ordner `app/static/icons/`.
- UI-Icons liegen als lokale SVG-Dateien im Projekt.
- Einbindung über CSS-Masks, dadurch übernehmen die Icons weiterhin `currentColor`.
- Light-/Dark-Mode, Hoverfarben und Buttonfarben funktionieren ohne separate SVG-Farbvarianten.
- Für die Icons ist keine Internetverbindung mehr erforderlich.
- Versionsanzeige im Burger-Menü: V9.5.1.

Hinweis:
Andere externe Ressourcen wie Chart.js können weiterhin eine Internetverbindung benötigen.
Diese Änderung betrifft gezielt die Icon-Abhängigkeit.

---

## 9.5

### UI-Icons
Die bisherigen Emoji-/Unicode-Aktionssymbole wurden durch Google Material Symbols Rounded ersetzt.

Unter anderem:
- Theme: `dark_mode` / `light_mode`
- Bearbeiten: `edit`
- Löschen: `delete`
- Speichern: `save`
- Neue Transaktion: `add`
- Navigation: `arrow_back`, `chevron_left`, `chevron_right`
- Fixkosten: `event_repeat`
- Kategorien: `category`
- Budgets: `savings`
- Analyse: `monitoring`
- A&D: `account_tree`
- Export: `download`
- Backup: `backup`
- Logout: `logout`
- Warnungen: `warning`
- Erfolg: `check_circle`

Buttons, Abstände, Dark Mode, Burger-Menü und bestehende Funktionen bleiben erhalten.

Hinweis:
Material Symbols werden über Google Fonts geladen. Für die Icons benötigt der Browser daher
eine Internetverbindung. Die Finanzdaten selbst bleiben weiterhin lokal in Fintra.

---

## 9.4.3

- Im Burger-Menü wird ganz unten dezent die aktuelle Versionsnummer angezeigt.
- Anzeige: `Fintra · V9.4.3`
- Sonstige Funktionen und Layouts bleiben unverändert.

---

## 9.4.2

### Prüfung
- Python-Syntax geprüft
- alle Jinja-Templates kompiliert
- CSS mit tinycss2 geparst: keine Parserfehler
- Smoke-Tests für Dashboard, Monat, Fixkosten, Kategorien, Analyse, Budgets und A&D

### CSS-Cleanup
48 nicht mehr erreichbare CSS-Selektoren wurden entfernt. Darunter Altlasten aus:
- alter Navigation (`navlinks`, `nav-user`, alte Logout-Regeln)
- früheren Monatskarten (`monthgrid`, `monthcard`)
- älteren Analyse-Komponenten (`analysis-grid`, `ranklist`)
- früherer Jahresdiagramm-Implementierung (`annual-chart*`, `pie-chart`, `pie-legend`, Legend-Klassen)
- alter Kategorie-Edit-Struktur (`cat-edit`)
- nicht mehr verwendeten Hilfsklassen (`actions`, `compact-amount`, `cards.three`)

Die Reihenfolge und aktiven Override-Regeln wurden bewusst nicht aggressiv zusammengeführt,
damit bestehendes Responsive-, Dark-Mode- und Komponentenverhalten unverändert bleibt.

---

## 9.4.1

### Verbesserung der Budget-Validierung
- Ungültige Geldbeträge führen nicht mehr auf eine blanke Fehlerseite.
- Fintra bleibt auf der Budget-Seite und zeigt ein Dialogfenster.
- Zusätzlich validiert JavaScript die Werte bereits vor dem Absenden.
- Leere Felder bleiben erlaubt und entsprechen weiterhin 0 €.
- Unterstützt deutsche Beträge wie `150,00` sowie `150.00`.
- Serverseitige Validierung bleibt als Sicherheitsnetz bestehen.

---

## 9.4

### Navigation
Die bisher volle Navigationsleiste wurde aufgeräumt.

Direkt sichtbar:
- Fintra
- Übersicht
- Neue Transaktion
- Light/Dark-Mode
- Burger-Menü

Im Burger-Menü:
- Fixkosten
- Kategorien
- Budgets
- Finanzanalyse
- Algorithmen & Datenstrukturen
- CSV-Export
- Datenbank-Backup
- Benutzername
- Abmelden

### Bedienung
- Menü öffnet/schließt per Klick.
- Burger-Icon animiert zu einem X.
- Klick außerhalb schließt das Menü.
- Escape schließt das Menü.
- Auf kleineren Displays wird die Navigation weiter reduziert.
- Alle bestehenden V9.3-Funktionen bleiben erhalten.

---

## 9.3

Schwerpunkt: Algorithmen & Datenstrukturen

### Neu
- Interaktive Hash-Map-vs.-Linear-Search-Demo auf echten Fintra-Daten.
- Top-K-Ausgabenkategorien mit Min-Heap und einstellbarem k.
- Sliding-Window-Visualisierung mit 3-Monats-Durchschnitt.
- Detaillierte IQR-Ausreißeranalyse mit Q1, Q3, IQR und Schwelle.
- Synthetischer Performance-Test mit 100 bis 100.000 Transaktionen.
- Vergleich von linearer Suche und Hash-Map-Lookup.
- Vergleich von vollständiger Sortierung und Min-Heap.
- Reproduzierbare synthetische Daten (Seed 42), ausschließlich im RAM.
- Komplexitätsübersicht direkt auf der Analyse-Seite.
- Erweiterte A&D-Theorieseite.

Hinweis:
Die angezeigten Mikrosekunden-Messungen dienen der Demonstration auf der jeweils
verwendeten Hardware. Aussagekräftiger für die Komplexitätsanalyse sind die
Operationszahlen und Big-O-Angaben.

---

## 9.2.4

### Kategorien-Seite
- Kategorien sind standardmäßig nur lesbar.
- Erst ein Klick auf den Stift öffnet das Bearbeitungsfeld.
- Dann erscheinen `Speichern` und `Abbrechen`.
- `Abbrechen` schließt die Bearbeitung ohne Änderung.
- Löschen bleibt direkt verfügbar und weiterhin mit Bestätigungsdialog.
- Die 32×32-px-Aktionsbuttons aus V9.2.2 bleiben erhalten.

---

## 9.2.2

Einheitliche Aktionsbuttons:
- fixed.html: weiterhin 32 × 32 px
- categories.html: Bearbeiten/Löschen jetzt 32 × 32 px
- month.html: Bearbeiten/Löschen jetzt 32 × 32 px
- Einheitlicher Abstand von 6 px bei den Transaktionsbuttons
- Alle bisherigen Anpassungen bleiben erhalten.

---

## 9.2.1

- Grundlage: V9.2 angepasst.
- Aktionszelle in fixed.html bleibt nun eine echte Tabellenzelle.
- Dadurch wird ihre Zeilenhöhe vom selben Tabellenlayout wie alle Monatszellen bestimmt.
- Buttons liegen in einem inneren Flex-Container mit weiterhin exakt 6 px Abstand.

---

## 9.2

Anpassungen an `fixed.html`:
- Bearbeiten, Speichern und Löschen haben exakt denselben Abstand.
- Das unsichtbare Update-Formular erzeugt keinen zusätzlichen Zwischenraum mehr.
- Die Aktionszelle hat dieselbe Höhe wie die übrigen Zellen derselben Tabellenzeile.
- Alle drei Aktionsbuttons sind 32 × 32 px groß und vertikal zentriert.
- Sonstige Funktionen und Anpassungen der Grundbasis wurden nicht verändert.

---

## 9

V9 erweitert Fintra um:
- Transaktionen bearbeiten
- Suche und Filter auf Monatsseiten
- elegante Dialog-Validierung für fehlerhafte Geldbeträge
- Fixkosten umbenennen und Typ ändern
- Fixkosten aus Quelljahr/Quellmonat importieren, nur Kategorien oder inklusive Wert
- Budget-Fortschritt mit Warnstufen
- Jahresdiagramme mit Einnahmen/Ausgaben und Ausgaben nach Kategorie
- CSV-Export
- konsistentes SQLite-Backup
- kräftigere Grün/Rot-Kennzeichnung für Einnahmen/Ausgaben
- Schnellzugriff "Neue Transaktion"

Update-Hinweis:
Beim Upgrade den vorhandenen data/-Ordner behalten, wenn dort echte Finanzdaten liegen.
