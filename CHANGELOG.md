# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Planned
- Test Panel UI for bulk messaging
- Mesh connections (all-to-all)
- Bulk client creation
- InfluxDB metrics integration
- Grafana dashboard templates
- WebSocket live updates
- Scheduled test runs

---

## [0.1.7-alpha] - 2025-12-27

### 🎉 Major Feature: SimpleX CLI Clients

This release introduces comprehensive Docker-based test client infrastructure for end-to-end message delivery testing across your SimpleX SMP servers.

### Added

#### Docker Container Management
- **Dockerfile.simplex-cli** - Custom Docker image based on `debian:bookworm-slim`
- **entrypoint.sh** - Container entrypoint with optional Tor support
- **docker_manager.py** - Python service for container lifecycle management
- Start/Stop/Restart/Delete controls via Web UI
- Volume management for persistent client data (`simplex-client-{slug}-data`)
- Health checks for container status monitoring
- Bridge networking with individual port mapping (3031-3080)

#### WebSocket Command Service
- **simplex_commands.py** - Synchronous command service for Django views
- `SimplexCommandService` class with singleton pattern
- Correlation ID based request/response matching (async WebSocket → sync API)
- Commands implemented:
  - `create_address()` - Create invitation link
  - `get_address()` - Retrieve existing address
  - `create_or_get_address()` - Smart address handling
  - `connect_via_link()` - Connect to another client
  - `get_contacts()` - List all contacts
  - `enable_auto_accept()` - Enable auto-accept for incoming requests
  - `send_message()` - Send message to contact

#### Client Connections
- **ClientConnection model** - Track bidirectional connections between clients
- `contact_name_on_a` / `contact_name_on_b` - Store how clients see each other
- Auto-Accept feature for seamless connection establishment
- Connection status tracking (pending/connected/disconnected)
- UI modal for creating new connections

#### Delivery Receipt Tracking
- **listen_events management command** - Background WebSocket event listener
- Event types handled:
  - `newChatItems` - Incoming messages
  - `chatItemsStatusesUpdated` - Delivery confirmations
- Status progression:
  - ⏳ `pending` - Message being sent
  - ✓ `sent` - Server acknowledged receipt
  - ✓✓ `delivered` - Recipient client received
  - ✗ `failed` - Delivery failed
- Latency measurement in milliseconds
- Async Django DB access via `sync_to_async`

#### UI Improvements
- **Client List View** - Cards with status indicators, message stats
- **Client Detail View** - Connections, messaging, logs
- **Table-based Message Layout** - Three tabs (Sent/Received/All)
- **Status Icons** - Visual indicators for message status
- **Latency Display** - Per-message delivery time
- **Quick Send Form** - Send messages directly from detail page

### Fixed
- **Container Deletion Bug** - Docker containers now properly removed when deleting clients (was leaving orphaned containers)
- **Django 4+ DeleteView** - Changed from `delete()` to `post()` method for compatibility
- **Auto-Accept Order** - Must be called after address creation, not before
- **Container Lookup** - Added fallback to container name if ID lookup fails
- **Template Grid Layout** - Fixed sidebar positioning in client detail view (was pushed below main content)

### Technical Details

**New Files:**
```
clients/
├── services/
│   ├── docker_manager.py      # Container lifecycle management
│   └── simplex_commands.py    # WebSocket command service
├── docker/
│   ├── Dockerfile.simplex-cli # Container image definition
│   └── entrypoint.sh          # Container startup script
└── management/
    └── commands/
        └── listen_events.py   # Event listener daemon
```

**Dependencies Added:**
- `websockets` - Python async WebSocket client
- `docker` - Docker SDK for Python (docker-py)

**Configuration:**
- Port range: 3031-3080 (50 clients max by default)
- Container naming: `simplex-client-{slug}`
- Volume naming: `simplex-client-{slug}-data`

### Performance

Tested on **Raspberry Pi 5** (8GB RAM, 128GB NVMe SSD, Debian 12):

| Clients | RAM Usage | CPU (idle) | Status |
|---------|-----------|------------|--------|
| 6 | ~400 MB | <5% | ✅ Stable |
| 10 | ~650 MB | <10% | ✅ Stable |
| 20 | ~1.2 GB | <15% | ✅ Stable |
| 50 | ~3 GB | <25% | ⚠️ Tested |

---

## [0.1.6-alpha] - 2025-12-26

### Added
- **Multi-Type Test System** - Monitoring, Stress, and Latency tests with dedicated workflows
- **APScheduler Integration** - Automated test execution with configurable intervals
- **i18n Translation System** - Alpine.js `$store.i18n` with JSON language files
- **Language Files** - `static/js/i18n/en.json`, `de.json` (25 languages prepared)
- **timeAgo() Function** - Relative time display (e.g., "2 minutes ago")
- **Live Countdown Timer** - Real-time test progress with Alpine.js reactivity
- **Onion/ClearNet Badges** - Visual indicators in test results table
- **Dynamic Grafana Links** - Auto-detect server IP instead of localhost
- **Language Switcher** - EN/DE toggle in navigation header

### Changed
- Complete test system refactor with new models (TestRun, TestResult, ServerStats)
- Symmetric 4-tile monitoring dashboard layout
- Test detail pages redesigned for each test type

### Fixed
- Success rate calculation now capped at 100% (was showing 140%+)
- Grafana links now use actual server IP instead of localhost

---

## [0.1.5-alpha] - 2025-12-25

### Added
- **7-Tab Server Form** - Basic, Monitoring, SSH, Control Port, Telegraf, SimpleX Config, Statistics
- **Extended Server Model** - SSH, Control Port, Telegraf, SLA fields
- **Test Result Persistence** - Connection tests save to database on form submit
- **Card Quick Test** - ⚡ button with immediate database update
- **Category System** - Colored labels for server organization
- **Template Tags** - Fingerprint/password extraction from address
- **Screenshots Folder** - `serverlist.png`

### Changed
- Server form completely redesigned with tabbed interface
- Server cards now show quick test button and real-time latency
- Connection testing saves results when form is submitted

### Fixed
- Host property setter error (was read-only property)
- Category views and URLs restored after accidental removal

---

## [0.1.4-alpha] - 2025-12-24

### Added
- **UI Redesign** - Professional dark/light mode with Tailwind CSS
- **Bilingual Support** - English/German language toggle (persists in localStorage)
- **Connection Testing** - Real-time server connectivity tests with latency measurement
- **Tor Integration** - Automatic .onion detection, tests via SOCKS5 proxy
- **Duplicate Detection** - Warning when adding duplicate server addresses
- **Drag & Drop** - Reorder servers visually
- **Server Details** - Host, Fingerprint, Password fields parsed from address
- **Password Toggle** - Show/hide password in server cards
- **Status Persistence** - Test results saved with server (Online/Offline/Error)
- **ONION Badge** - Visual indicator for Tor hidden services

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
- 🎉 **Initial Project Structure**
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
| 0.1.7-alpha | 2025-12-27 | CLI Clients, Docker, Delivery Receipts |
| 0.1.6-alpha | 2025-12-26 | Multi-type tests, i18n, APScheduler |
| 0.1.5-alpha | 2025-12-25 | 7-tab form, categories, quick test |
| 0.1.4-alpha | 2025-12-24 | UI redesign, Tor testing, bilingual |
| 0.1.0-alpha | 2025-12-23 | Initial release |

---

[Unreleased]: https://github.com/cannatoshi/simplex-smp-monitor/compare/v0.1.7-alpha...HEAD
[0.1.7-alpha]: https://github.com/cannatoshi/simplex-smp-monitor/compare/v0.1.6-alpha...v0.1.7-alpha
[0.1.6-alpha]: https://github.com/cannatoshi/simplex-smp-monitor/compare/v0.1.5-alpha...v0.1.6-alpha
[0.1.5-alpha]: https://github.com/cannatoshi/simplex-smp-monitor/compare/v0.1.4-alpha...v0.1.5-alpha
[0.1.4-alpha]: https://github.com/cannatoshi/simplex-smp-monitor/compare/v0.1.0-alpha...v0.1.4-alpha
[0.1.0-alpha]: https://github.com/cannatoshi/simplex-smp-monitor/releases/tag/v0.1.0-alpha
