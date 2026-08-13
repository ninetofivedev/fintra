# Fintra auf TrueNAS SCALE

## Voraussetzungen

- TrueNAS SCALE mit Docker-basierter Apps-Unterstützung
- ein persistenter Dataset-/Host-Pfad für `/app/data`
- ein veröffentlichtes Fintra-Image in GHCR

## Empfohlene Verzeichnisstruktur

```text
/mnt/POOL/apps/fintra/
└── data/
    ├── haushaltsbuch.db
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
v9.6.0-beta.2
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
