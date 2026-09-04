# Changelog

## 9.6.0-beta.15

### UI & Bedienung
- Einheitlichere Bearbeitungslogik für Budgets und Transaktionen mit kompakten Icon-Aktionen
- Monatsansicht um Kategorie-Filter und Filter-Zurücksetzen erweitert
- Leere Zustände auf Dashboard, Monats-, Fixkosten-, Kategorien- und Budgetansichten verbessert
- Sticky Tabellenköpfe für Jahresübersicht und Transaktionen ergänzt
- Schneller Jahreswechsel per Dropdown auf Dashboard, Fixkosten und Budgets
- Dashboard-Kennzahlen sind jetzt direkt zu den passenden Ansichten verlinkt
- Budgetkarten mit klareren Fortschritts-, Warn- und Limit-Zuständen überarbeitet
- Aktive Seite wird im Burger-Menü hervorgehoben
- Tastaturfokus, ARIA-Beschriftungen und Reduced-Motion-Unterstützung verbessert
- PWA-Manifest ergänzt, damit Fintra sauber zum Homescreen hinzugefügt werden kann
- UI-Konsistenz als Vorbereitung auf einen späteren stabilen Release weiter vereinheitlicht

## 9.6.0-beta.14

### Kategorien
- Aktionssymbole der Kategorienzeilen vollständig rechtsbündig ausgerichtet
- Gleichmäßiger Abstand zwischen Bearbeiten, Speichern und Löschen
- Unsichtbares Update-Formular belegt keinen zusätzlichen Platz mehr in der Aktionsleiste

## 9.6.0-beta.13

### Kategorien
- Bearbeitungsmodus an die Fixkosten-Seite angeglichen
- Kategorienamen werden direkt an Ort und Stelle editiert
- Separate große Speichern-/Abbrechen-Leiste entfernt
- Kompakte Aktionsleiste mit Bearbeiten, Speichern und Löschen bleibt dauerhaft rechts sichtbar
- Speichern-Button wird erst im Bearbeitungsmodus aktiviert
- Responsive Darstellung für Smartphones vereinheitlicht

## 9.6.0-beta.12

### Fixkosten
- Bearbeitungsmodus vereinfacht: Der Typ-Dropdown und der separate Speichern-Button neben der Bezeichnung wurden entfernt.
- Der bestehende Speichern-Button unter „Aktionen“ speichert jetzt gemeinsam die geänderte Bezeichnung und alle Monatswerte.
- Der Typ einer bestehenden Fixkostenposition bleibt beim Bearbeiten unverändert.

## 9.6.0-beta.11

### Fixkosten
- Im Bearbeitungsmodus wird die statische Bezeichnung ausgeblendet, sodass nur noch das Eingabefeld mit der Bezeichnung sichtbar ist.
- Doppelte Darstellung von Fixkosten-Bezeichnungen in der Desktop-Tabelle behoben.

## 9.6.0-beta.10

### Dashboard
- Desktop-Umschalter für `Ausgaben nach Kategorie` zwischen Doughnut- und horizontalem Balkendiagramm ergänzt
- Gewählte Desktop-Darstellung wird lokal im Browser gespeichert
- Balkenansicht nutzt die kompakte Top-7-plus-`Sonstiges`-Darstellung aus der mobilen Ansicht
- Auf Smartphones bleibt der Umschalter ausgeblendet und das Balkendiagramm wird weiterhin automatisch verwendet
- Zwei neue lokale Diagramm-Icons ergänzt; keine externen Ressourcen erforderlich

## 9.6.0-beta.9

### Fixkosten
- Fixkosten-Seite um kompakte Monats-/Jahres-Zusammenfassung ergänzt
- Desktop-Tabelle mit fixierter Bezeichnung, fixierten Aktionen und Jahressumme verbessert
- Zeilen-Hover und klarerer Bearbeitungszustand ergänzt
- Smartphone-Ansicht als aufklappbare Karten statt breiter Tabelle umgesetzt
- Mobile Karten zeigen Jahressumme, Monatsdurchschnitt und bei Bedarf alle 12 Monatswerte
- Bearbeiten, Speichern und Löschen funktionieren direkt innerhalb der mobilen Karte

## 9.6.0-beta.8

### Mobile
- Dashboard-Diagramme für Smartphones optimiert
- `Einnahmen vs. Ausgaben` verwendet mobil kompakte Monatslabels, kleinere Achsenbeschriftungen und eine reduzierte Diagrammhöhe
- `Ausgaben nach Kategorie` wechselt auf Smartphones automatisch vom Doughnut- zum horizontalen Balkendiagramm
- Mobile Kategorienansicht zeigt die sieben größten Kategorien und fasst weitere als `Sonstiges` zusammen
- Diagramme werden beim Wechsel über die mobile Breakpoint-Grenze automatisch neu aufgebaut
- Desktop-Diagramme bleiben in ihrer bisherigen Darstellung erhalten

## 9.6.0-beta.7

### Fixed
- Tabellenlinie in der Jahresübersicht zwischen `Fixe Einnahmen` und `Variable Ausgaben` wieder über die komplette Breite sichtbar
- Neutral dargestellte Monatsbeträge entfernen die Zell-Trennlinien nicht mehr

## 9.6.0-beta.6

### Branding
- Neues Fintra-Logo auf Basis des stilisierten `F` eingeführt
- Claim auf **Finance and Tracking** vereinheitlicht
- Logo in Hauptnavigation, Login und Ersteinrichtung integriert
- Lokale Favicons und Apple-Touch-Icon ergänzt
- Branding vollständig lokal eingebunden und damit weiterhin offline verfügbar
- README um das neue Fintra-Branding ergänzt

## 9.6.0-beta.5

### Fixed
- Datumsanzeige in der Buchungsübersicht vereinheitlicht: Desktop und Smartphone verwenden jetzt immer `TT.MM.JJJJ`
- Tippfehler in der IQR-Ausreißeranzeige der Analyse behoben; das Transaktionsdatum wird dort jetzt korrekt dargestellt
- Datumsformatierung für angezeigte Transaktionsdaten zentralisiert

### Cleanup
- veralteten Mobile-CSS-Override aus der früheren Buchungskarten-Version entfernt
- nicht mehr verwendete `.burger-user`-CSS-Regeln entfernt
- Python-Cachedateien aus dem Projekt entfernt
- `.directory` zu `.gitignore` hinzugefügt
- redundante `BETA_RELEASE_NOTES.md` entfernt; `RELEASE_NOTES.md` ist die zentrale Release-Historie
- Docker-Compose-, README- und TrueNAS-Versionsangaben auf `9.6.0-beta.5` aktualisiert

## 9.6.0-beta.3

### Mobile
- Buchungskarten auf `month.html` deutlich kompakter gestaltet
- Datum und Einnahme/Ausgabe-Typ stehen jetzt gemeinsam in der Kopfzeile
- Kategorie und Betrag stehen platzsparend nebeneinander
- Kommentar liegt direkt darunter ohne zusätzliche Label-Zeile
- Bearbeiten/Löschen stehen in einer schmalen Aktionsspalte rechts
- Datumsdarstellung auf Smartphones auf `TT.MM.JJJJ` umgestellt
- Desktop-Darstellung bleibt unverändert

## 9.6.0-beta.2

### Mobile
- Buchungsübersicht auf `month.html` als responsive Kartenansicht auf Smartphones
- Such- und Filterfelder für schmale Displays optimiert
- Transaktionsbearbeitung auf Mobile als kompakte Formular-Karte
- Hintergrundscrollen bei geöffnetem Burger-Menü auf Smartphones gesperrt
- Burger-Menü bleibt dadurch fest am Viewport

## 9.6.0-beta.1

Erster Beta-Release.

### Deployment
- GitHub Actions für GHCR-Container-Images
- TrueNAS-Compose-Vorlage
- persistentes `/app/data`
- öffentlicher `/health`-Endpoint
- zentrale Versionsnummer
- Docker-Healthcheck
- `.gitignore` und `.dockerignore` für Finanzdaten und Secrets

### Anwendung
- basiert auf Fintra V9.5.15
- Profilseite und Passwortänderung
- Privacy-Modus
- lokale Icons
- Finanzanalyse und A&D-Demos
