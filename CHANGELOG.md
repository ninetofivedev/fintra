# Changelog

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
