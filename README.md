# Fintra

**Track your finances**

Fintra ist ein selbstgehostetes Haushaltsbuch für persönliche Finanzen.  
Diese Version markiert den Beginn der Beta-Phase.

**Aktuelle Version:** `9.6.0-beta.1`

## Funktionen

- Jahres- und Monatsübersichten
- variable Einnahmen und Ausgaben
- jahresbezogene Fixkosten
- Kategorien und Monatsbudgets
- Transaktionen nachträglich bearbeiten
- CSV-Export und SQLite-Backup
- Light-/Dark-Mode
- Privacy-Modus
- Profilseite mit Passwortänderung
- responsive Burger-Navigation
- lokale SVG-Icons
- lokale Chart.js-Auslieferung im fertigen Container
- A&D-Analyse mit Hash Map, Min-Heap, Sliding Window und IQR
- synthetischer Performance-Test bis 100.000 Transaktionen
- `/health`-Endpoint für Container-Healthchecks

---

# 1. GitHub-Repository anlegen

Erstelle bei GitHub ein neues Repository, zum Beispiel:

```text
fintra
```

Empfehlung für die Beta-Phase:

- Repository zunächst **privat**, solange du den Code noch nicht veröffentlichen möchtest.
- Wenn TrueNAS das GHCR-Image ohne Zugangsdaten laden soll, muss das Container-Paket später öffentlich sein.
- Niemals deine echte `haushaltsbuch.db` committen.

Danach im Fintra-Projekt:

```bash
git init
git branch -M main
git add .
git commit -m "Fintra 9.6.0-beta.1"
git remote add origin https://github.com/DEIN_GITHUB_BENUTZERNAME/fintra.git
git push -u origin main
```

Die enthaltene `.gitignore` ignoriert Datenbanken, `.env`-Dateien und andere lokale Daten.

---

# 2. Docker-Image über GitHub Actions veröffentlichen

Der Workflow liegt unter:

```text
.github/workflows/container.yml
```

Ein normaler Push auf `main` prüft und baut Fintra, veröffentlicht aber **noch kein Release-Image**.

Ein Release wird über einen Git-Tag ausgelöst:

```bash
git tag v9.6.0-beta.1
git push origin v9.6.0-beta.1
```

GitHub Actions:

1. installiert die Python-Abhängigkeiten,
2. prüft den Python-Import,
3. baut das Docker-Image,
4. veröffentlicht es in der GitHub Container Registry (GHCR).

Danach existieren unter anderem:

```text
ghcr.io/DEIN_GITHUB_BENUTZERNAME/fintra:9.6.0-beta.1
ghcr.io/DEIN_GITHUB_BENUTZERNAME/fintra:latest
```

Für die nächste Version:

```bash
git add .
git commit -m "Fintra 9.6.0-beta.2"
git push

git tag v9.6.0-beta.2
git push origin v9.6.0-beta.2
```

Erst der Release-Tag aktualisiert `latest`. So landet nicht jeder Entwicklungsstand automatisch auf deinem Heimserver.

---

# 3. GHCR-Paket für TrueNAS freigeben

Wenn dein TrueNAS das Image ohne GitHub-Anmeldedaten laden soll:

1. Öffne auf GitHub dein Benutzerprofil bzw. deine Organisation.
2. Öffne **Packages**.
3. Öffne das Fintra-Container-Paket.
4. Stelle die Sichtbarkeit des Pakets auf **Public**.

Dein Quellcode-Repository kann unabhängig davon privat bleiben, sofern die GitHub-Paketkonfiguration das für dein Konto zulässt.

Alternativ kannst du ein privates GHCR-Paket verwenden und in TrueNAS Registry-Zugangsdaten hinterlegen.

---

# 4. Persistente Daten auf TrueNAS vorbereiten

Die Finanzdaten dürfen nicht im Container-Image liegen.

Lege auf TrueNAS beispielsweise einen Dataset-/Verzeichnispfad an:

```text
/mnt/DEIN_POOL/apps/fintra/data
```

Fintra verwendet im Container:

```text
/app/data
```

Dort liegen später insbesondere:

```text
haushaltsbuch.db
.session_secret
```

Beim Container-Update bleibt dieses Verzeichnis erhalten.

Wenn du bereits eine Fintra-Datenbank hast, kopiere sie vor dem ersten Start nach:

```text
/mnt/DEIN_POOL/apps/fintra/data/haushaltsbuch.db
```

---

# 5. TrueNAS Custom App per YAML

Eine Vorlage liegt unter:

```text
deploy/truenas-compose.yaml
```

Passe mindestens diese beiden Stellen an:

```yaml
image: ghcr.io/DEIN_GITHUB_BENUTZERNAME/fintra:latest
```

und:

```yaml
- /mnt/DEIN_POOL/apps/fintra/data:/app/data
```

Danach kannst du den YAML-Code in TrueNAS unter **Apps → Install via YAML / Custom App** verwenden.

Beispiel:

```yaml
services:
  fintra:
    image: ghcr.io/deinname/fintra:latest
    pull_policy: always
    container_name: fintra
    ports:
      - "8080:8080"
    environment:
      FINTRA_HTTPS_ONLY: "0"
    volumes:
      - /mnt/tank/apps/fintra/data:/app/data
    restart: unless-stopped
```

Danach erreichst du Fintra typischerweise unter:

```text
http://TRUENAS-IP:8080
```

---

# 6. Updates

Der empfohlene Beta-Workflow:

```text
Code ändern
   ↓
git push
   ↓
GitHub Actions prüft Build
   ↓
Release-Tag setzen
   ↓
GitHub Actions veröffentlicht neues GHCR-Image
   ↓
TrueNAS erkennt neues Image für :latest
   ↓
Update manuell auslösen
```

Vor einem Update solltest du ein Backup deiner Datenbank anlegen.

In Fintra kannst du dafür im Burger-Menü **Datenbank-Backup** verwenden.

---

# 7. Healthcheck

Fintra stellt öffentlich innerhalb des Containers bereit:

```text
GET /health
```

Beispielantwort:

```json
{
  "status": "ok",
  "version": "9.6.0-beta.1"
}
```

Der Docker-Healthcheck verwendet diesen Endpoint automatisch.

---

# 8. Lokale Entwicklung

```bash
docker compose up -d --build
```

Danach:

```text
http://localhost:8080
```

Lokale persistente Daten liegen in:

```text
./data/
```

Optional kannst du `.env.example` nach `.env` kopieren.

---

# Sicherheit

- Passwörter werden mit scrypt gehasht.
- Formulare mit Zustandsänderungen verwenden CSRF-Schutz.
- Sessions verwenden einen geheimen Schlüssel.
- Ohne `FINTRA_SECRET_KEY` erzeugt Fintra einen persistenten Schlüssel unter `/app/data/.session_secret`.
- Bei Betrieb hinter HTTPS sollte `FINTRA_HTTPS_ONLY=1` gesetzt werden.
- Die echte Finanzdatenbank gehört niemals in GitHub oder in das Docker-Image.
- Der TrueNAS-Dataset-Pfad mit `haushaltsbuch.db` sollte regelmäßig gesichert werden.

---

# Versionsschema

Während der Beta-Phase:

```text
9.6.0-beta.1
9.6.0-beta.2
9.6.0-beta.3
```

Git-Tags:

```text
v9.6.0-beta.1
v9.6.0-beta.2
```

Später kann daraus beispielsweise werden:

```text
1.0.0
```
