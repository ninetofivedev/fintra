# Changelog

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
