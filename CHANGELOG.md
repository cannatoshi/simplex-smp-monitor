# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Planned
- InfluxDB metrics integration
- Grafana dashboard templates
- Stress testing implementation
- WebSocket live updates
- Scheduled test runs

---

## [0.1.5-alpha] - 2025-12-24

### Added
- **UI Redesign:** Professional dark/light mode with Tailwind CSS
- **Bilingual Support:** English/German language toggle (persists in localStorage)
- **Connection Testing:** Real-time server connectivity tests with latency measurement
- **Tor Integration:** Automatic .onion detection, tests via SOCKS5 proxy
- **Duplicate Detection:** Warning when adding duplicate server addresses
- **Drag & Drop:** Reorder servers visually
- **Server Details:** Host, Fingerprint, Password fields parsed from address
- **Password Toggle:** Show/hide password in server cards
- **Status Persistence:** Test results saved with server (Online/Offline/Error)
- **ONION Badge:** Visual indicator for Tor hidden services

### Changed
- Renamed project from "SimpleX Test Suite" to "SimpleX SMP Monitor"
- Footer updated with copyright and slogan
- Server cards redesigned with better information display

### Fixed
- CSRF token for HTMX DELETE requests
- Form submission handling for server creation

---

## [0.1.0-alpha] - 2025-12-23

### Added
- 🎉 Initial project structure
- Django 5.x project setup with ASGI support
- Server management (CRUD operations)
- Dashboard with statistics overview
- Event logging system
- Stress test framework (UI only)
- Docker Compose stack (InfluxDB, Grafana, Telegraf)
- SimplexCLIManager for CLI integration
- MetricsWriter for InfluxDB
- HTMX + Alpine.js frontend
- Basic Tailwind CSS styling

---

## Version History

| Version | Date | Highlights |
|---------|------|------------|
| 0.1.5-alpha | 2025-12-24 | UI redesign, Tor testing, bilingual |
| 0.1.0-alpha | 2025-12-23 | Initial release |

---

[Unreleased]: https://github.com/cannatoshi/simplex-smp-monitor/compare/v0.1.5-alpha...HEAD
[0.1.5-alpha]: https://github.com/cannatoshi/simplex-smp-monitor/compare/v0.1.0-alpha...v0.1.5-alpha
[0.1.0-alpha]: https://github.com/cannatoshi/simplex-smp-monitor/releases/tag/v0.1.0-alpha
