# Fintra auf TrueNAS SCALE

## Voraussetzungen

- TrueNAS SCALE mit Docker-basierter Apps-Unterstützung
- ein persistenter Dataset-/Host-Pfad für `/app/data`
- ein veröffentlichtes Fintra-Image in GHCR

## Empfohlene Verzeichnisstruktur

```text
/mnt/POOL/apps/fintra/
└── data/
    ├── database.db
    └── .session_secret
```

## YAML

Kopiere `truenas-compose.yaml` in den YAML-Editor von TrueNAS und ersetze:

- `DEIN_GITHUB_BENUTZERNAME`
- `DEIN_POOL`

Die Anwendung verwendet absichtlich `:latest`, damit TrueNAS denselben Image-Tag
beobachten kann, während GitHub bei jedem expliziten Fintra-Release dessen Digest aktualisiert.

## Update-Strategie

Fintra veröffentlicht `latest` nur bei einem Git-Tag wie:

```text
v9.6.0-beta.38
```

Dadurch ist ein einfacher Push auf `main` noch kein Server-Update.

Vor dem manuellen Update:

1. Fintra-Datenbank sichern.
2. Neues Image in GitHub Actions erfolgreich bauen lassen.
3. In TrueNAS das erkannte Image-Update installieren.
4. `/health` bzw. den App-Status kontrollieren.

## HTTPS

Wenn Fintra über einen HTTPS-Reverse-Proxy erreichbar ist, setze:

```yaml
FINTRA_HTTPS_ONLY: "1"
```

Bei reinem HTTP im privaten LAN bleibt der Wert `0`.


### Datenbank-Dateiname

Seit Fintra 9.6.0-beta.35 lautet der Standard-Dateiname `database.db`. Liegt im eingebundenen `/app/data`-Verzeichnis noch die historische `haushaltsbuch.db`, wird sie beim ersten Start automatisch in `database.db` umbenannt. Ein explizit gesetzter `DB_PATH` bleibt unverändert.

### Demo-Profil

Fintra enthält für Präsentationen ein separates Demo-Profil. Standardmäßig ist es aktiviert:

- Benutzername: `demo`
- Passwort: `demo`
- Datenbank: `/app/data/demo.db`
- Die Demo-Daten sind vollständig fiktiv und werden bei jeder Demo-Anmeldung auf den Ausgangszustand zurückgesetzt.
- Das private Profil verwendet weiterhin ausschließlich `/app/data/database.db`.

Optional kann das Demo-Profil deaktiviert oder das Passwort geändert werden:

```yaml
environment:
  FINTRA_DEMO_MODE: "0"
  # FINTRA_DEMO_PASSWORD: "eigenes-demo-passwort"
```
