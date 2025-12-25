# SimpleX SMP Monitor - Feature Roadmap

> **Version:** v1.0 Target Features  
> **Last Updated:** 2025-12-25  
> **Current Version:** v0.7.3-alpha

---

## 📊 Progress Overview

| Phase | Version | Status | Features |
|-------|---------|--------|----------|
| 1 | v0.2.0 | 🟡 In Progress | Categories, Server-Config, CLI-Basis |
| 2 | v0.3.0 | ⬜ Planned | Test-Framework, Connectivity, Message Delivery |
| 3 | v0.4.0 | ⬜ Planned | Profiles, Stress/Load Tests, Test-UI |
| 4 | v0.5.0 | ⬜ Planned | Scheduled Tests, Background Monitoring |
| 5 | v0.6.0 | ⬜ Planned | InfluxDB, Telegraf, Dashboard, Grafana |
| 6 | v0.7.0 | ⬜ Planned | Alerting, Telegram, Notifications |
| 7 | v1.0.0 | ⬜ Planned | Docs, Docker, Tests, Production |

---

## ✅ Already Implemented

- [x] Server Management (CRUD, Cards, Drag & Drop reordering)
- [x] Tor/Onion Address Detection
- [x] Connection Testing with Tor SOCKS5 Proxy
- [x] Duplicate Server Detection
- [x] Bilingual Support (German/English)
- [x] Dark Mode
- [x] Server Categories (basic)

---

## 🎯 Phase 1: Foundation (v0.2.0)

### 1.1 Server Categories ✅ DONE
- [x] Model: Category (name, description, color, created_at)
- [x] Model: Server.categories (ManyToMany)
- [x] Views: CRUD for categories
- [x] Templates: Category management UI
- [x] Templates: Server category assignment
- [x] Category badges on server cards
- [ ] Filter: Dashboard/Lists by category

### 1.2 Extended Server Configuration
All SimpleX options configurable per server:

- [ ] Model: ServerConfig (all SimpleX options)
- [ ] Model: Server.config (OneToOne)
- [ ] Form: Extended settings UI
- [ ] Defaults: Sensible default values
- [ ] Validation: Value range checking

**TCP Connection Settings:**
| Option | Description | Default |
|--------|-------------|---------|
| TCP connection timeout | Connection establishment timeout | 30 sec |
| TCP connection bg timeout | Background timeout | 60 sec |
| Protocol timeout | SMP protocol timeout | 20 sec |
| Protocol background timeout | Protocol background timeout | 40 sec |
| Protocol timeout per KB | Additional timeout per KB | 0.015 sec |

**Keep-Alive Settings:**
| Option | Description | Default |
|--------|-------------|---------|
| PING interval | Keepalive ping interval | 1200 sec |
| PING count | Pings before disconnect | 3 |
| TCP_KEEPIDLE | Time until first keep-alive probe | 30 sec |
| TCP_KEEPINTVL | Interval between probes | 15 sec |
| TCP_KEEPCNT | Probes before timeout | 4 |

**SOCKS/Tor Settings:**
| Option | Description | Default |
|--------|-------------|---------|
| SOCKS Proxy Host | Proxy address | 127.0.0.1 |
| SOCKS Proxy Port | Proxy port | 9050 |
| Use .onion hosts | No / If available / Required | If available |
| Use random credentials | Tor circuit isolation | On |

**Private Message Routing:**
| Option | Description | Default |
|--------|-------------|---------|
| Private routing | Off / Unprotected / Always | Always |
| Allow downgrade | Allow downgrade | No |

**Transport Isolation:**
| Option | Description | Default |
|--------|-------------|---------|
| Transport isolation | App session / Per connection | App session |
| Use web port | Preset servers / All servers | Preset servers |

### 1.3 SimpleX CLI Integration
- [ ] Service: SimplexCLIService (WebSocket Client)
- [ ] CLI Installation/Setup Documentation
- [ ] Profile Management (create test users)
- [ ] Connection Management
- [ ] Basic communication testing

---

## 🧪 Phase 2: Core Testing (v0.3.0)

### 2.1 Test Framework Base
- [ ] Model: TestRun (type, status, config, results, timestamps)
- [ ] Model: TestResult (metrics, errors, details)
- [ ] Service: TestRunner (orchestrates tests)
- [ ] Service: MetricsCollector (collects metrics)
- [ ] Async: Celery/Django-Q for background jobs

### 2.2 Test Types

#### Connectivity Test (Reachability)
| Feature | Description |
|---------|-------------|
| TCP connection test | Check if port is reachable |
| TLS handshake | Validate TLS 1.3 connection |
| Fingerprint verification | Verify server certificate |
| Latency measurement | Time to establish connection |
| Tor/Clearnet | Automatic detection and routing |

#### Latency Test
| Feature | Description |
|---------|-------------|
| Single Ping | One request, one measurement |
| Multi Ping | X requests, average/min/max |
| Percentiles | Calculate P50, P95, P99 |
| Jitter | Measure latency variance |

#### Message Delivery Test
| Feature | Description |
|---------|-------------|
| One-checkmark tracking | Message sent to server (CISSndSent) |
| Two-checkmark tracking | Message received by recipient (CISSndRcvd) |
| Delivery time | Time from send to delivery |
| Success rate | % successfully delivered |
| Error analysis | Why delivery failed |

#### Throughput Test
| Feature | Description |
|---------|-------------|
| Messages/second | How many messages per second |
| Parallel connections | Multiple simultaneous connections |
| Bandwidth | Measure data transfer rate |
| Queue capacity | Find maximum queue utilization |

### 2.3 Test Parameters (Configurable)

**Base Parameters:**
| Parameter | Description | Range |
|-----------|-------------|-------|
| Message count | How many to send | 1 - 100,000 |
| Message size | Bytes per message | 1B - 16KB |
| Parallelism | Simultaneous connections | 1 - 500 |
| Interval | Pause between messages | 0ms - 60s |
| Timeout | When considered failed | 1s - 600s |
| Warmup | Warmup messages (not counted) | 0 - 100 |
| Retries | Retry attempts on failure | 0 - 10 |

**Server Selection:**
| Option | Description |
|--------|-------------|
| Single server | Test only one server |
| All active | All servers with is_active=True |
| By category | All servers in a category |
| Manual selection | Checkboxes for servers |
| Round-robin | Alternating distribution |
| Random | Random selection |
| Weighted | By server capacity |

---

## 💪 Phase 3: Stress Testing (v0.4.0)

### 3.1 Test Profile System
- [ ] Model: TestProfile (name, config, is_builtin)
- [ ] Create predefined profiles
- [ ] Custom Profile CRUD
- [ ] Profile Import/Export (JSON)
- [ ] UI: Profile selection

**Predefined Profiles:**
| Profile | Messages | Parallel | Interval | Timeout | Purpose |
|---------|----------|----------|----------|---------|---------|
| Quick Check | 5 | 1 | 0ms | 30s | Quick reachability check |
| Basic Health | 20 | 3 | 100ms | 30s | Standard health check |
| Standard Load | 100 | 10 | 50ms | 30s | Normal load test |
| Heavy Load | 500 | 50 | 10ms | 60s | High load |
| Stress Test | 1000 | 100 | 0ms | 120s | Find server limits |
| Endurance 1h | ∞ | 5 | 1s | 30s | 1 hour continuous run |
| Endurance 24h | ∞ | 3 | 5s | 30s | 24 hour continuous run |
| Tor Optimized | 50 | 5 | 500ms | 300s | Optimized for .onion |

### 3.2 Load/Stress Test
- [ ] Manage parallel connections
- [ ] Ramp-up implementation
- [ ] Load control (messages/second)
- [ ] Breaking-point detection
- [ ] Resource monitoring

### 3.3 Test UI
- [ ] Test creation wizard
- [ ] Parameter configuration
- [ ] Server/Category selection
- [ ] Live progress display
- [ ] Result overview

---

## ⏰ Phase 4: Long-term Monitoring (v0.5.0)

### 4.1 Scheduled Tests
- [ ] Model: ScheduledTest (cron, profile, servers)
- [ ] Scheduler: Celery Beat / Django-Q
- [ ] UI: Schedule configuration
- [ ] Cron expression builder
- [ ] Enable/Disable

### 4.2 Background Monitoring Service
- [ ] Daemon: 24/7 monitoring process
- [ ] Configurable interval
- [ ] Automatic retry
- [ ] Graceful shutdown
- [ ] Systemd service unit

### 4.3 Endurance Tests
- [ ] Long-term test (hours/days)
- [ ] Duration-based mode
- [ ] Pause/Resume function
- [ ] Checkpoint saving
- [ ] Memory leak detection

---

## 📈 Phase 5: Metrics & Visualization (v0.6.0)

### 5.1 InfluxDB Integration
- [ ] InfluxDB 2.x setup
- [ ] Metrics writer service
- [ ] Store all test metrics
- [ ] Configure retention policies
- [ ] Continuous queries for aggregation

**Retention Policies:**
| Data | Storage | Retention |
|------|---------|-----------|
| Raw metrics | InfluxDB | 24-48 hours |
| 5min aggregates | InfluxDB | 14 days |
| 1h aggregates | InfluxDB | 90 days |
| Daily aggregates | InfluxDB | 2 years |

### 5.2 Telegraf Integration
- [ ] Telegraf agent configuration
- [ ] System metrics collection (CPU, RAM, Disk, Network)
- [ ] SimpleX server process monitoring
- [ ] Tor service monitoring
- [ ] Custom input plugins for test results
- [ ] Output to InfluxDB

**Telegraf Metrics:**
| Category | Metrics |
|----------|---------|
| System | CPU usage, Memory, Disk I/O, Network I/O |
| Process | SimpleX SMP/XFTP process stats |
| Tor | Circuit count, bandwidth, latency |
| Test Results | Success rate, latency, throughput |

### 5.3 Dashboard Enhancement
- [ ] Server status overview
- [ ] Category statistics
- [ ] Active tests widget
- [ ] Recent results widget
- [ ] Uptime display
- [ ] Real-time metrics

### 5.4 Grafana Dashboards
- [ ] Latency dashboard
- [ ] Uptime monitoring dashboard
- [ ] Throughput analysis dashboard
- [ ] Error analysis dashboard
- [ ] System resources dashboard
- [ ] Export dashboard templates as JSON

**Dashboard Panels:**
| Dashboard | Panels |
|-----------|--------|
| Overview | Server status map, uptime %, active alerts |
| Latency | P50/P95/P99 over time, per-server comparison |
| Throughput | Messages/sec, bandwidth, queue depth |
| Errors | Error rate, error types, trends |
| System | CPU, RAM, Disk, Network per server |

---

## 🚨 Phase 6: Alerting (v0.7.0)

### 6.1 Alert System
- [ ] Model: AlertRule (condition, threshold, actions)
- [ ] Model: Alert (rule, triggered_at, status)
- [ ] Service: AlertEvaluator
- [ ] Threshold checking
- [ ] Alert history

**Alert Conditions:**
| Condition | Description |
|-----------|-------------|
| Server offline | X consecutive failures |
| High latency | Latency > threshold |
| Low success rate | < X% successful |
| High error rate | > X% errors |
| Queue full | Queue depth > limit |

### 6.2 Telegram Integration 🤖
- [ ] Telegram Bot setup
- [ ] Bot token configuration
- [ ] Chat ID management
- [ ] Send notifications
- [ ] Query server status via bot commands

**Bot Commands:**
| Command | Description |
|---------|-------------|
| /status | Overall system status |
| /servers | List all servers with status |
| /server <n> | Detailed server info |
| /test <server> | Run quick test |
| /alerts | Show active alerts |
| /silence <duration> | Silence alerts |

### 6.3 Additional Channels
- [ ] Email (SMTP)
- [ ] Webhook (Generic HTTP POST)
- [ ] In-App notifications
- [ ] Slack integration (optional)

### 6.4 Alert Options
| Option | Description |
|--------|-------------|
| Thresholds | When to trigger alert |
| Cooldown | Pause between alerts |
| Escalation | After X minutes send to Y |
| Grouping | Group similar alerts |

---

## 🚀 Phase 7: Polish & Production (v1.0.0)

### 7.1 Documentation
- [ ] Extend README
- [ ] Installation guide
- [ ] Configuration guide
- [ ] API documentation
- [ ] Troubleshooting guide

### 7.2 Production-Ready
- [ ] Docker Compose (full stack)
- [ ] Environment configuration
- [ ] Security hardening
- [ ] Performance optimization
- [ ] Backup/Restore scripts

**Docker Stack:**
```yaml
services:
  - django        # Web application
  - celery        # Background tasks
  - redis         # Task queue
  - influxdb      # Time-series metrics
  - telegraf      # Metrics collection
  - grafana       # Visualization
  - tor           # SOCKS proxy (optional)
```

### 7.3 Tests & QA
- [ ] Unit tests
- [ ] Integration tests
- [ ] End-to-end tests
- [ ] Load testing the app itself

---

## 🕐 Time Estimates

| Phase | Version | Main Features | Time (estimated) |
|-------|---------|---------------|------------------|
| 1 | v0.2.0 | Categories, Server-Config, CLI-Basis | 13-17 hours |
| 2 | v0.3.0 | Test-Framework, Connectivity, Message Delivery, Latency | 18-24 hours |
| 3 | v0.4.0 | Profiles, Stress/Load Tests, Test-UI | 22-28 hours |
| 4 | v0.5.0 | Scheduled Tests, Background Monitoring, Endurance | 17-22 hours |
| 5 | v0.6.0 | InfluxDB, Telegraf, Dashboard, Grafana | 16-20 hours |
| 6 | v0.7.0 | Alerting, Telegram, Notifications | 13-16 hours |
| 7 | v1.0.0 | Docs, Docker, Tests, Production | 16-21 hours |

**Total: ~115-148 hours** (spread over several weeks/months)

---

## 🏗️ Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | Django 5.x |
| Database | SQLite (dev) / PostgreSQL (prod) |
| Task Queue | Celery + Redis |
| Time-Series DB | InfluxDB 2.x |
| Metrics Agent | Telegraf |
| Visualization | Grafana |
| Frontend | HTMX + Alpine.js + TailwindCSS |
| Tor Integration | SOCKS5 Proxy |

---

## 📝 Notes

### Infrastructure Context
This tool is designed to monitor a SimpleX Private Messaging Infrastructure:
- 10 SMP servers running as Tor v3 hidden services
- 1 XFTP server running as Tor v3 hidden service
- All servers on Raspberry Pi hardware
- Tor-only access (no clearnet)

### Related Projects
- [SimpleX Chat](https://simplex.chat/) - Private messaging platform
- [SimpleX Private Infrastructure Tutorial](https://github.com/cannatoshi/simplex-smp-xftp-via-tor-on-rpi-hardened) - Setup guide

---

## 🤝 Contributing

Contributions are welcome! Please read our contributing guidelines before submitting PRs.

## 📄 License

MIT License - See LICENSE file for details.
