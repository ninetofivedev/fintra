# Fintra 9.6.0-beta.1

Diese Version ist für den ersten GitHub/GHCR/TrueNAS-Beta-Workflow vorbereitet.

Wichtig vor dem ersten Push:
1. Prüfe README.md.
2. Ersetze Platzhalter in `deploy/truenas-compose.yaml`.
3. Committe niemals `data/haushaltsbuch.db`.
4. Erstelle nach dem ersten Push den Tag `v9.6.0-beta.1`.
5. Stelle das GHCR-Paket öffentlich oder hinterlege Registry-Credentials in TrueNAS.

Das Image `:latest` wird nur bei expliziten `v*`-Release-Tags veröffentlicht.
Normale Commits auf `main` werden geprüft und gebaut, lösen aber kein Server-Release aus.
