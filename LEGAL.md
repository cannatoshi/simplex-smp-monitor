# Legal Information / Rechtliche Informationen

> **SimpleX SMP Monitor** - Legal Documentation Overview

---

## English

### Legal Documents

This project maintains the following legal documentation:

| Document | Description |
|----------|-------------|
| [LICENSE](LICENSE) | GNU Affero General Public License v3.0 (AGPL-3.0) |
| [TRADEMARK.md](TRADEMARK.md) | Trademark notice and third-party trademark information |
| [DISCLAIMER.md](DISCLAIMER.md) | Liability disclaimer and limitation of warranties |
| [TESTING_POLICY.md](TESTING_POLICY.md) | Testing guidelines and permitted use |

### Quick Summary

- **License:** This software is licensed under AGPL-3.0. You may use, modify, and distribute it under the terms of this license.
- **Trademarks:** "SimpleX" and "SimpleX Chat" are trademarks of SimpleX Chat Ltd. This project is **not affiliated with or endorsed by** SimpleX Chat Ltd.
- **Liability:** This software is provided "AS IS" without warranty. See [DISCLAIMER.md](DISCLAIMER.md) for full details.
- **Testing:** See [TESTING_POLICY.md](TESTING_POLICY.md) for what testing is permitted on own vs. third-party infrastructure.

---

### Third-Party Software

This project includes or uses the following third-party software:

#### SimpleX Software (AGPL-3.0)

The Docker images provided by this project contain **unmodified binaries** from official SimpleX GitHub releases. These binaries are:

| Software | Description | License | Source |
|----------|-------------|---------|--------|
| **simplex-chat** (CLI) | SimpleX Chat command-line client | AGPL-3.0 | [simplex-chat](https://github.com/simplex-chat/simplex-chat) |
| **smp-server** | SimpleX Messaging Protocol relay server | AGPL-3.0 | [simplexmq](https://github.com/simplex-chat/simplexmq) |
| **xftp-server** | SimpleX File Transfer Protocol server | AGPL-3.0 | [simplexmq](https://github.com/simplex-chat/simplexmq) |
| **ntf-server** | SimpleX Push Notification server (iOS) | AGPL-3.0 | [simplexmq](https://github.com/simplex-chat/simplexmq) |

**Important Notes:**

1. **No Modifications:** We do NOT modify the SimpleX binaries. We download official releases directly from GitHub and include them in our Docker images for convenience.

2. **Source Code Availability:** The complete source code for all SimpleX software is available at:
   - https://github.com/simplex-chat/simplex-chat (CLI client)
   - https://github.com/simplex-chat/simplexmq (SMP, XFTP, NTF servers)

3. **AGPL-3.0 Compliance:** Under AGPL-3.0, you have the right to:
   - Use the software for any purpose
   - Study and modify the source code
   - Distribute the software
   - Run the software and access it over a network

4. **Our Contribution:** Our Docker images add convenience (easier deployment) but do not modify the underlying SimpleX software.

#### Other Dependencies

| Component | License | Usage |
|-----------|---------|-------|
| Django | BSD-3-Clause | Web framework |
| Django REST Framework | BSD-3-Clause | API framework |
| Django Channels | BSD-3-Clause | WebSocket support |
| React | MIT | Frontend framework |
| Vite | MIT | Build tool |
| Tailwind CSS | MIT | Styling |
| Redis | BSD-3-Clause | Message broker |
| PostgreSQL | PostgreSQL License | Database |
| Nginx | BSD-2-Clause | Reverse proxy |
| InfluxDB | MIT | Time-series metrics |
| Grafana | AGPL-3.0 | Dashboards |

---

### Docker Images and Binary Distribution

#### What We Distribute

| Image | Contents | License Compliance |
|-------|----------|-------------------|
| `simplex-smp-monitor-app` | Django + React application | AGPL-3.0 (our code) |
| `simplex-smp-monitor-nginx` | Nginx reverse proxy | BSD-2-Clause |
| `simplex-smp` | smp-server binary | AGPL-3.0 (SimpleX) |
| `simplex-xftp` | xftp-server binary | AGPL-3.0 (SimpleX) |
| `simplex-ntf` | ntf-server binary | AGPL-3.0 (SimpleX) |
| `simplex-cli` | simplex-chat binary | AGPL-3.0 (SimpleX) |

#### Your Rights Under AGPL-3.0

When using our Docker images containing SimpleX software:

1. **Source Code Access:** You can obtain the complete source code from the links above.

2. **No Additional Restrictions:** We do not add any restrictions beyond AGPL-3.0.

3. **Network Use:** If you modify and run SimpleX software accessible over a network, AGPL-3.0 requires you to provide source code access to users.

4. **Attribution:** We provide proper attribution to SimpleX Chat Ltd as the original authors.

---

### Contact

For legal inquiries: [GitHub Issues](https://github.com/cannatoshi/simplex-smp-monitor/issues)

For SimpleX trademark inquiries: chat@simplex.chat

For SimpleX licensing questions: https://github.com/simplex-chat/simplex-chat/blob/stable/LICENSE

---

## Deutsch

### Rechtliche Dokumente

| Dokument | Beschreibung |
|----------|--------------|
| [LICENSE](LICENSE) | GNU Affero General Public License v3.0 (AGPL-3.0) |
| [TRADEMARK.md](TRADEMARK.md) | Markenrechtliche Hinweise |
| [DISCLAIMER.md](DISCLAIMER.md) | Haftungsausschluss |
| [TESTING_POLICY.md](TESTING_POLICY.md) | Test-Richtlinien |

### Kurzzusammenfassung

- **Lizenz:** AGPL-3.0
- **Markenrecht:** "SimpleX" ist eine Marke der SimpleX Chat Ltd. Dieses Projekt ist **nicht mit SimpleX Chat Ltd verbunden**.
- **Haftung:** "WIE BESEHEN" ohne Gewährleistung.
- **Tests:** Siehe [TESTING_POLICY.md](TESTING_POLICY.md)

---

### Drittanbieter-Software

#### SimpleX Software (AGPL-3.0)

Die Docker-Images dieses Projekts enthalten **unveränderte Binärdateien** aus offiziellen SimpleX GitHub-Releases:

| Software | Beschreibung | Lizenz | Quelle |
|----------|--------------|--------|--------|
| **simplex-chat** (CLI) | Kommandozeilen-Client | AGPL-3.0 | [simplex-chat](https://github.com/simplex-chat/simplex-chat) |
| **smp-server** | Messaging-Relay-Server | AGPL-3.0 | [simplexmq](https://github.com/simplex-chat/simplexmq) |
| **xftp-server** | Dateitransfer-Server | AGPL-3.0 | [simplexmq](https://github.com/simplex-chat/simplexmq) |
| **ntf-server** | Push-Benachrichtigungs-Server | AGPL-3.0 | [simplexmq](https://github.com/simplex-chat/simplexmq) |

**Wichtige Hinweise:**

1. **Keine Modifikationen:** Wir modifizieren die SimpleX-Binärdateien NICHT. Wir laden offizielle Releases direkt von GitHub herunter.

2. **Quellcode-Verfügbarkeit:** Der komplette Quellcode ist verfügbar unter:
   - https://github.com/simplex-chat/simplex-chat
   - https://github.com/simplex-chat/simplexmq

3. **AGPL-3.0 Konformität:** Unter AGPL-3.0 haben Sie das Recht:
   - Die Software für jeden Zweck zu nutzen
   - Den Quellcode zu studieren und zu modifizieren
   - Die Software zu verteilen
   - Die Software über ein Netzwerk zu betreiben

---

### Docker-Images und Binärverteilung

#### Was wir verteilen

| Image | Inhalt | Lizenz |
|-------|--------|--------|
| `simplex-smp-monitor-app` | Django + React Anwendung | AGPL-3.0 (unser Code) |
| `simplex-smp-monitor-nginx` | Nginx Reverse Proxy | BSD-2-Clause |
| `simplex-smp` | smp-server Binärdatei | AGPL-3.0 (SimpleX) |
| `simplex-xftp` | xftp-server Binärdatei | AGPL-3.0 (SimpleX) |
| `simplex-ntf` | ntf-server Binärdatei | AGPL-3.0 (SimpleX) |
| `simplex-cli` | simplex-chat Binärdatei | AGPL-3.0 (SimpleX) |

---

### Kontakt

Rechtliche Anfragen: [GitHub Issues](https://github.com/cannatoshi/simplex-smp-monitor/issues)

SimpleX Markenrecht: chat@simplex.chat

SimpleX Lizenzfragen: https://github.com/simplex-chat/simplex-chat/blob/stable/LICENSE

---

*Last updated: January 2026*