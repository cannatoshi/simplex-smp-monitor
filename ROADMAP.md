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

## ✅ Phase 1.6: Real-Time Infrastructure (COMPLETED - v0.1.8)

### 🚀 This is the MAJOR feature of v0.1.8!

The application was transformed from polling-based to **real-time event-driven architecture**.

### 1.6.1 Redis Channel Layer ✅
- [x] Redis Docker container setup
- [x] channels-redis package integration
- [x] Redis configuration in settings.py
- [x] Replace InMemoryChannelLayer with RedisChannelLayer
- [x] Persistent data volume for Redis

**Docker Command:**
```bash
docker run -d \
  --name simplex-redis \
  --restart unless-stopped \
  -p 6379:6379 \
  -v simplex-redis-data:/data \
  redis:7-alpine redis-server --appendonly yes
```

### 1.6.2 SimplexEventBridge ✅
- [x] New service: `clients/services/event_bridge.py`
- [x] Automatic connection to all running containers
- [x] Connection sync every 5 seconds
- [x] Reconnection on connection loss
- [x] Event processing: `newChatItems`, `chatItemsStatusesUpdated`
- [x] Database updates on events
- [x] Push events to Channel Layer
- [x] Broadcast to browser group "clients_all"

### 1.6.3 WebSocket Consumers ✅
- [x] New file: `clients/consumers.py`
- [x] ClientUpdateConsumer (for client list page)
- [x] ClientDetailConsumer (for detail page)
- [x] Event handlers: client_status, client_stats, message_status, new_message
- [x] Container log streaming (detail page)

### 1.6.4 WebSocket Routing ✅
- [x] New file: `clients/routing.py`
- [x] URL: `/ws/clients/` for list page
- [x] URL: `/ws/clients/<slug>/` for detail page
- [x] ASGI config update in `config/asgi.py`

### 1.6.5 Auto-Start Integration ✅
- [x] Updated `clients/apps.py`
- [x] Event Bridge starts automatically with Django
- [x] Background thread with own event loop
- [x] No more manual `listen_events` command needed!

**Old Way (v0.1.7):**
```bash
# Terminal 1
python manage.py runserver 0.0.0.0:8000
# Terminal 2
python manage.py listen_events  # <- EXTRA STEP!
```

**New Way (v0.1.8):**
```bash
# Single command - everything starts automatically!
python manage.py runserver 0.0.0.0:8000
```

### 1.6.6 Frontend WebSocket Client ✅
- [x] New file: `static/js/clients-live.js`
- [x] Auto-connect on page load
- [x] Auto-reconnect on disconnect
- [x] Event handlers for all message types
- [x] Live DOM updates without refresh
- [x] Toast notifications for new messages
- [x] Uptime tracking

### 1.6.7 Live Status Indicator ✅
- [x] Green/red indicator in navigation bar
- [x] "Live" / "Reconnecting..." text
- [x] Detailed tooltip on hover:
  - WebSocket connection status
  - Event Bridge status
  - Number of connected clients
  - Channel Layer type (Redis)
  - Last event received
  - Connection uptime (live counter)

### 1.6.8 Secondary: UI/UX Improvements ✅
- [x] 4-corner stats card layout
- [x] AJAX messaging system
- [x] AJAX connection management
- [x] Slide animations
- [x] Live SMP server LEDs
- [x] Equal height layout
- [x] Unified button styling

### 1.6.9 Bug Fixes ✅
- [x] URL routing order (specific routes before slug)
- [x] SendMessageView AJAX response
- [x] SMP LED status field reference

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
- [ ] Real-time progress display (via WebSocket!)
- [ ] Success/failure counters

### 2.2 Mesh Connections
- [ ] "Connect All" button - creates connections between all clients
- [ ] Selective mesh (connect specific groups)
- [ ] Connection matrix visualization
- [ ] Bulk disconnect option

### 2.3 Bulk Client Operations
- [ ] Create multiple clients at once (e.g., "Create 10 clients")
- [ ] Auto-port assignment (3031, 3032, ...)
- [ ] Bulk start/stop/restart
- [ ] Bulk delete with cleanup
- [ ] Client group/tag system

### 2.4 Test Results Dashboard
- [ ] Success rate per client
- [ ] Average latency histogram
- [ ] Failed message analysis
- [ ] Time-based graphs (Chart.js)
- [ ] Export to CSV/JSON

### 2.5 Extended Real-Time Features
- [ ] WebSocket bridge status endpoint
- [ ] "Listening to X clients" in tooltip
- [ ] Live client list updates
- [ ] Auto-refresh stats on list page
- [ ] Connection status broadcasts

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
- [ ] Real-time message flow visualization

### 3.4 Historical Statistics
- [ ] Latency sparkline with real data (currently placeholder)
- [ ] Success rate trends over time
- [ ] Per-server message counts
- [ ] Daily/weekly/monthly reports

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
- [ ] Redis clustering
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
| **0.1.8-alpha** | **2025-12-27** | **Real-Time: Redis, WebSocket, Event Bridge** | **✅ Done** |
| 0.2.0 | 2026-01-15 | Test Panel, Mesh, Bulk Ops | 🔄 Next |
| 0.2.5 | 2026-02-01 | InfluxDB, Grafana | 📋 Planned |
| 0.3.0 | 2026-03-01 | Alerts, Notifications | 📋 Planned |
| 0.4.0 | 2026-04-01 | Remote Management | 📋 Planned |
| 0.5.0 | 2026-06-01 | API, Mobile | 📋 Planned |
| 1.0.0 | TBD | Production Ready | 📋 Future |

---

## Technology Stack Evolution

### Current (v0.1.8)

| Component | Technology | Status |
|-----------|------------|--------|
| Backend | Django 5.x | ✅ Active |
| ASGI Server | Daphne | ✅ Active |
| **WebSocket** | **Django Channels** | **✅ NEW in v0.1.8** |
| **Message Broker** | **Redis** | **✅ NEW in v0.1.8** |
| Frontend | HTMX + Alpine.js | ✅ Active |
| AJAX | Fetch API | ✅ Active |
| CSS | Tailwind CSS | ✅ Active |
| Animations | CSS Keyframes | ✅ Active |
| Database | SQLite | ✅ Active |
| Containers | Docker | ✅ Active |

### Planned (v0.2.0+)

| Component | Technology | Target |
|-----------|------------|--------|
| Task Queue | Celery | v0.3.0 |
| Time-Series DB | InfluxDB | v0.2.5 |
| Visualization | Grafana | v0.2.5 |
| Charts | Chart.js | v0.2.0 |
| Production DB | PostgreSQL | v0.5.0 |

---

## Architecture Diagram (v0.1.8)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         BROWSER (User)                                   │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  clients-live.js                                                  │   │
│  │  - Auto-connect WebSocket                                         │   │
│  │  - Live DOM updates                                               │   │
│  │  - Toast notifications                                            │   │
│  └──────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                          WebSocket │ /ws/clients/
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         DJANGO + CHANNELS                                │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  ClientUpdateConsumer / ClientDetailConsumer                      │   │
│  │  - Receives events from Channel Layer                             │   │
│  │  - Sends JSON to browser                                          │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                    │                                     │
│                         Channel Layer                                    │
│                                    │                                     │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  SimplexEventBridge (Auto-started in background thread)          │   │
│  │  - Connects to all running containers                             │   │
│  │  - Processes SimpleX events                                       │   │
│  │  - Updates database                                               │   │
│  │  - Broadcasts to "clients_all" group                              │   │
│  └──────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
            │                                              │
            │ WebSocket :3031-3080                         │ Pub/Sub
            ▼                                              ▼
┌─────────────────────────┐                    ┌─────────────────────────┐
│  SimpleX CLI Containers │                    │  Redis (Port 6379)      │
│  - Client 001 (:3031)   │                    │  - Channel Layer        │
│  - Client 002 (:3032)   │                    │  - Message Broker       │
│  - Client 003 (:3033)   │                    │  - Persistent Storage   │
│  - ...                  │                    │                         │
└─────────────────────────┘                    └─────────────────────────┘
```

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

## Features Added Per Version

### v0.1.8-alpha (Real-Time Infrastructure) 🚀
**MAJOR FEATURE:**
- Redis Channel Layer
- SimplexEventBridge
- WebSocket Consumers
- Auto-start integration
- Frontend WebSocket client
- Live status indicator with tooltip

**Secondary:**
- 4-corner stats card layout
- AJAX messaging system
- AJAX connection management
- Slide animations
- Live SMP server LEDs
- URL routing fix
- SendMessageView AJAX support

### v0.1.7-alpha (CLI Clients)
- Docker container management
- WebSocket command service
- Client connections
- Delivery receipt tracking
- Event listener daemon (now deprecated!)
- Message statistics
- Client detail page
- Container logs display

### v0.1.6-alpha (Testing)
- Multi-type test system
- APScheduler integration
- i18n translation system
- Live countdown timer
- Language switcher

### v0.1.5-alpha (Server Config)
- 7-tab server form
- Category system
- Quick test button
- Extended server model

### v0.1.4-alpha (UI/UX)
- Dark/light mode
- Bilingual support
- Tor integration
- Drag & drop

### v0.1.0-alpha (Foundation)
- Initial project structure
- Server management
- Dashboard
- Event logging

---

## Known Issues & Limitations

### v0.1.8

| Issue | Workaround | Fix Target |
|-------|------------|------------|
| Tooltip shows "0 Clients" | Bridge status endpoint needed | v0.2.0 |
| List page no auto-refresh | Visit detail page | v0.2.0 |
| Toast notifications stack | Refresh page | v0.2.0 |
| Latency sparkline placeholder | Shows static bars | v0.2.5 |

### Architecture Limitations

| Limitation | Impact | Solution |
|------------|--------|----------|
| SQLite for dev only | Single-writer | PostgreSQL in v0.5.0 |
| No task queue | Sync operations | Celery in v0.3.0 |
| Single Redis instance | No HA | Redis cluster in v0.5.0 |

---

## Contributing

Want to help? Check:

1. [Open Issues](https://github.com/cannatoshi/simplex-smp-monitor/issues)
2. [Discussions](https://github.com/cannatoshi/simplex-smp-monitor/discussions)

### Priority Areas for v0.2.0

| Area | Difficulty | Impact |
|------|------------|--------|
| Test Panel UI | Medium | High |
| Bridge status API | Easy | Medium |
| Mesh connection logic | Hard | High |
| Chart.js integration | Medium | Medium |
| Bulk client creation | Easy | Medium |
| List page WebSocket | Easy | Medium |

### How to Contribute

1. Fork the repository
2. Create a feature branch
3. Follow existing code style
4. Add tests if applicable
5. Update documentation
6. Submit a pull request

---

*Last updated: 2025-12-27 (v0.1.8-alpha)*
