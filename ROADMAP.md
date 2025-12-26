# SimpleX Test Suite - Roadmap

## ✅ Phase 1: Foundation (COMPLETED)

### 1.1 Project Setup ✅
- [x] Django project with async support (Daphne/ASGI)
- [x] SQLite database
- [x] TailwindCSS + Alpine.js frontend
- [x] Dark mode support
- [x] Bilingual (EN/DE) interface

### 1.2 Server Management ✅
- [x] Server model with extended fields:
  - Basic: name, type, address, description, location, priority
  - Monitoring: custom_timeout, expected_uptime, max_latency
  - SSH: host, port, user, key_path, remote paths
  - Control Port: enabled, port, admin/user passwords
  - Telegraf: enabled, interval, InfluxDB connection
  - Statistics: total_checks, successful_checks, avg_latency
- [x] Category system with colors
- [x] Server CRUD operations
- [x] Connection testing (TLS over Tor for .onion)
- [x] Test result persistence on form submit
- [x] Card-based test with immediate DB update
- [x] Duplicate address detection
- [x] Drag & drop reordering
- [x] 7-tab form interface (Basic, Monitoring, SSH, Control Port, Telegraf, SimpleX Config, Statistics)

### 1.3 Dashboard ✅
- [x] Server overview with stats
- [x] Real-time updates via WebSocket
- [x] Quick actions

---

## ✅ Phase 1.5: CLI Clients (COMPLETED - v0.1.7)

### 1.5.1 Docker Container Management ✅
- [x] Custom Dockerfile for SimpleX CLI
- [x] Entrypoint script with Tor support
- [x] Docker Manager service (Python)
- [x] Start/Stop/Restart/Delete controls
- [x] Volume management for persistent data
- [x] Health checks
- [x] Port mapping (3031-3080)

### 1.5.2 WebSocket Command Service ✅
- [x] SimplexCommandService class
- [x] Correlation ID based request/response
- [x] Commands: /address, /connect, /contacts, /auto_accept
- [x] Message sending via @contact syntax
- [x] Async-to-sync bridge for Django views

### 1.5.3 Client Connections ✅
- [x] ClientConnection model
- [x] Bidirectional contact names
- [x] Auto-Accept feature
- [x] Connection status tracking
- [x] UI modal for new connections

### 1.5.4 Delivery Receipt Tracking ✅
- [x] listen_events management command
- [x] newChatItems event handling
- [x] chatItemsStatusesUpdated event handling
- [x] Status: pending → sent → delivered
- [x] Latency measurement
- [x] Async Django DB access

### 1.5.5 UI Improvements ✅
- [x] Client list view with cards
- [x] Client detail view
- [x] Table-based message layout (3 tabs)
- [x] Status icons (⏳ ✓ ✓✓ ✗)
- [x] Quick send form
- [x] Container logs display

---

## 🔄 Phase 2: Test Panel & Automation (IN PROGRESS - v0.2.0)

### 2.1 Test Panel UI
- [ ] Dedicated test panel view (`/clients/test-panel/`)
- [ ] Select source clients (checkboxes)
- [ ] Select target clients (checkboxes)
- [ ] Configure test parameters:
  - Message count per client
  - Interval between messages (ms)
  - Test duration (minutes)
  - Message content (random/custom template)
- [ ] Start/Stop/Pause controls
- [ ] Real-time progress display
- [ ] Success/failure counters

### 2.2 Mesh Connections
- [ ] "Connect All" button - creates connections between all clients
- [ ] Selective mesh (connect specific groups)
- [ ] Connection matrix visualization
- [ ] Bulk disconnect option

### 2.3 Bulk Client Operations
- [ ] Create multiple clients at once (e.g., "Create 10 clients")
- [ ] Bulk start/stop/restart
- [ ] Bulk delete with cleanup
- [ ] Client group/tag system

### 2.4 Test Results Dashboard
- [ ] Success rate per client
- [ ] Average latency histogram
- [ ] Failed message analysis
- [ ] Time-based graphs (Chart.js)
- [ ] Export to CSV/JSON

---

## 📊 Phase 3: Monitoring & Metrics (v0.2.x)

### 3.1 Telegraf Integration
- [ ] SSH-based metric collection
- [ ] Control port stats collection
- [ ] CSV stats file parsing
- [ ] Auto-generate Telegraf configs

### 3.2 InfluxDB Integration
- [ ] Store test results as time-series
- [ ] Historical data queries
- [ ] Retention policies
- [ ] Client metrics (messages/min, latency)

### 3.3 Grafana Dashboards
- [ ] Pre-built dashboard templates
- [ ] Server health overview
- [ ] Latency trends
- [ ] Uptime tracking
- [ ] Client performance comparison

---

## 🔔 Phase 4: Alerts & Notifications (v0.3.x)

### 4.1 Alert Rules
- [ ] Threshold-based alerts (latency > X ms)
- [ ] SLA violation detection (uptime < X%)
- [ ] Anomaly detection (spike in failures)
- [ ] Client offline alerts

### 4.2 Notification Channels
- [ ] Email notifications
- [ ] SimpleX Chat notifications (dogfooding!)
- [ ] Webhook support (Discord, Slack, etc.)
- [ ] Telegram bot integration

---

## 🛠️ Phase 5: Advanced Features (v0.4.x)

### 5.1 Remote Management (via SSH)
- [ ] View server logs
- [ ] Restart services
- [ ] Read/update configuration
- [ ] Backup management

### 5.2 Control Port Integration
- [ ] Real-time stats via control port
- [ ] Server commands (stats, clients, threads)
- [ ] Queue management
- [ ] Connection inspection

### 5.3 Multi-User Support
- [ ] User authentication
- [ ] Role-based permissions (admin/operator/viewer)
- [ ] Audit logging
- [ ] Per-user client ownership

---

## 📱 Phase 6: Mobile & API (v0.5.x)

### 6.1 REST API
- [ ] Full CRUD API for all models
- [ ] API authentication (token/JWT)
- [ ] Rate limiting
- [ ] OpenAPI/Swagger documentation

### 6.2 Mobile Support
- [ ] Responsive design improvements
- [ ] PWA support (install as app)
- [ ] Push notifications
- [ ] Offline capability

---

## 🚀 Phase 7: Production Ready (v1.0.0)

### 7.1 Scalability
- [ ] PostgreSQL support
- [ ] Redis caching
- [ ] Celery task queue
- [ ] Kubernetes deployment
- [ ] Multi-node support

### 7.2 Security
- [ ] Two-factor authentication
- [ ] Audit logging
- [ ] Role-based access control
- [ ] API rate limiting
- [ ] Security headers

### 7.3 Documentation
- [ ] User guide
- [ ] Admin guide
- [ ] API documentation
- [ ] Video tutorials

---

## Version Timeline

| Version | Target Date | Focus | Status |
|---------|-------------|-------|--------|
| 0.1.0-alpha | 2025-12-23 | Initial release | ✅ Done |
| 0.1.4-alpha | 2025-12-24 | UI redesign, Tor testing | ✅ Done |
| 0.1.5-alpha | 2025-12-25 | 7-tab form, categories | ✅ Done |
| 0.1.6-alpha | 2025-12-26 | Multi-type tests, i18n | ✅ Done |
| 0.1.7-alpha | 2025-12-27 | CLI Clients, Delivery Receipts | ✅ Done |
| 0.2.0 | 2026-01-15 | Test Panel, Mesh Connections | 🔄 Next |
| 0.2.5 | 2026-02-01 | InfluxDB, Grafana | 📋 Planned |
| 0.3.0 | 2026-03-01 | Alerts, Notifications | 📋 Planned |
| 0.4.0 | 2026-04-01 | Remote Management | 📋 Planned |
| 0.5.0 | 2026-06-01 | API, Mobile | 📋 Planned |
| 1.0.0 | TBD | Production Ready | 📋 Future |

---

## Hardware Requirements

### Minimum (Development)
- Raspberry Pi 4 (4GB RAM)
- 32GB SD Card
- Debian 12 / Ubuntu 24.04

### Recommended (Production)
- Raspberry Pi 5 (8GB RAM)
- 128GB NVMe SSD
- Debian 12 (64-bit)

### Tested Capacity

| Hardware | Clients | RAM | Status |
|----------|---------|-----|--------|
| RPi 5 8GB | 6 | ~400 MB | ✅ Stable |
| RPi 5 8GB | 20 | ~1.2 GB | ✅ Stable |
| RPi 5 8GB | 50 | ~3 GB | ⚠️ Tested |
| RPi 5 8GB | 100 | ~6 GB | 🔄 Planned |
| x86 16GB | 200+ | TBD | 📋 Future |

---

## Contributing

Want to help? Check:

1. [Open Issues](https://github.com/cannatoshi/simplex-smp-monitor/issues)
2. [Discussions](https://github.com/cannatoshi/simplex-smp-monitor/discussions)

Priority areas:
- Test Panel UI design
- Grafana dashboard templates
- Documentation improvements
- Translation contributions

---

*Last updated: 2025-12-27*
