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

## 🔄 Phase 2: Testing Engine (IN PROGRESS)

### 2.1 Stress Test Framework
- [x] TestRun model
- [x] Basic test execution
- [ ] Parallel server testing
- [ ] Progress tracking via WebSocket
- [ ] Test result visualization

### 2.2 Test Types
- [ ] Connection test (TLS handshake)
- [ ] Latency measurement
- [ ] Throughput test
- [ ] Message delivery test
- [ ] Long-running stability test

### 2.3 Scheduling
- [ ] Celery/Django-Q integration
- [ ] Cron-based scheduling
- [ ] Interval-based monitoring

---

## 📊 Phase 3: Monitoring & Metrics

### 3.1 Telegraf Integration
- [ ] SSH-based metric collection
- [ ] Control port stats collection
- [ ] CSV stats file parsing
- [ ] Auto-generate Telegraf configs

### 3.2 InfluxDB Integration
- [ ] Store test results
- [ ] Historical data queries
- [ ] Retention policies

### 3.3 Grafana Dashboards
- [ ] Pre-built dashboard templates
- [ ] Server health overview
- [ ] Latency trends
- [ ] Uptime tracking

---

## 🔔 Phase 4: Alerts & Notifications

### 4.1 Alert Rules
- [ ] Threshold-based alerts
- [ ] SLA violation detection
- [ ] Anomaly detection

### 4.2 Notification Channels
- [ ] Email notifications
- [ ] SimpleX Chat notifications
- [ ] Webhook support
- [ ] Telegram bot

---

## 🛠️ Phase 5: Advanced Features

### 5.1 Remote Management (via SSH)
- [ ] View server logs
- [ ] Restart services
- [ ] Read/update configuration
- [ ] Backup management

### 5.2 Control Port Integration
- [ ] Real-time stats via control port
- [ ] Server commands (stats, clients, threads)
- [ ] Queue management

### 5.3 Multi-User Support
- [ ] User authentication
- [ ] Role-based permissions
- [ ] Audit logging

---

## 📱 Phase 6: Mobile & API

### 6.1 REST API
- [ ] Full CRUD API
- [ ] API authentication
- [ ] Rate limiting

### 6.2 Mobile Support
- [ ] Responsive design improvements
- [ ] PWA support
- [ ] Push notifications

---

## Version History

### v0.2.0 (2025-12-25) - Current
- Extended server model with SSH, Control Port, Telegraf fields
- 7-tab server form interface
- Connection test persistence (form + card)
- Category management
- Duplicate detection
- Password visibility toggle
- Card-based quick test with DB update

### v0.1.0 (2025-12-24)
- Initial release
- Basic server management
- Simple connection testing
- Dashboard with WebSocket updates
