# SimpleX SMP Monitor

## Real-Time Server Monitoring & Stress Testing for SimpleX Infrastructure

[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL--3.0-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Python](https://img.shields.io/badge/Python-3.11+-3776ab.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.x-092E20.svg)](https://www.djangoproject.com/)
[![Status](https://img.shields.io/badge/Status-Alpha-orange.svg)](#status)
[![Tor](https://img.shields.io/badge/Tor-Supported-7D4698.svg)](https://www.torproject.org/)
[![Maintenance](https://img.shields.io/badge/Maintained-Actively-success.svg)](https://github.com/cannatoshi/simplex-smp-monitor/commits/main)
[![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-brightgreen.svg)](#contributing)

A web-based monitoring dashboard and stress testing suite for self-hosted SimpleX SMP/XFTP relay infrastructure. Built for operators who need visibility into their private messaging servers.

> **Version:** 0.1.5-alpha (24. December 2025)  
> **Status:** Active Development  
> **Tested on:** Debian 12, Ubuntu 24.04, Raspberry Pi OS  
> **Companion to:** [SimpleX Private Infrastructure Tutorial](https://github.com/cannatoshi/simplex-smp-xftp-via-tor-on-rpi-hardened)

---

> ⚠️ **ALPHA SOFTWARE**
>
> This project is in active development. Core features work, but expect rough edges.
> Not recommended for production use without thorough testing.
> 
> ✅ **What works:** Server management, connectivity testing, Tor support, bilingual UI  
> 🚧 **In progress:** Stress testing, InfluxDB metrics, Grafana dashboards

---

## Table of Contents

### Getting Started
1. [About This Project](#about-this-project)
2. [Features](#features)
3. [Screenshots](#screenshots)
4. [Architecture](#architecture)

### Installation
5. [Prerequisites](#prerequisites)
6. [Install System Dependencies](#1-install-system-dependencies)
7. [Install Tor](#2-install-tor)
8. [Clone Repository](#3-clone-repository)
9. [Setup Python Environment](#4-setup-python-environment)
10. [Initialize Database](#5-initialize-database)
11. [Start the Server](#6-start-the-server)

### Configuration
12. [Tor Configuration](#tor-configuration)
13. [Environment Variables](#environment-variables)
14. [Monitoring Stack (Optional)](#monitoring-stack-optional)

### Usage
15. [Adding Servers](#adding-servers)
16. [Connection Testing](#connection-testing)
17. [Stress Testing](#stress-testing)

### Development
18. [Project Structure](#project-structure)
19. [Tech Stack](#tech-stack)
20. [Roadmap](#roadmap)
21. [Contributing](#contributing)
22. [Related Projects](#related-projects)
23. [License](#license)
24. [Changelog](#changelog)

---

## About This Project

If you run your own SimpleX SMP/XFTP servers (especially via Tor hidden services), you need answers to questions like:

- **Are my servers reachable?** Test connectivity through Tor or clearnet
- **What's the latency?** Measure response times across your infrastructure  
- **Are messages being delivered?** Run stress tests to verify reliability
- **What's happening over time?** Historical metrics and visualizations

This tool provides a **single dashboard** to monitor, test, and analyze your SimpleX relay infrastructure.

### Why This Tool?

| Problem | Solution |
|---------|----------|
| "Is my .onion server actually reachable?" | One-click connectivity test via Tor |
| "What's the latency to my servers?" | Real-time latency measurement |
| "Are messages being delivered reliably?" | Stress testing with delivery verification |
| "I have 10 servers, hard to track" | Central dashboard for all servers |
| "I need historical data" | InfluxDB + Grafana integration |

---

## Features

### ✅ Implemented (v0.1.5-alpha)

| Feature | Description |
|---------|-------------|
| **Server Management** | Add, edit, delete SMP/XFTP servers with full CRUD |
| **7-Tab Configuration** | Basic, Monitoring, SSH, Control Port, Telegraf, SimpleX Config, Statistics |
| **Connection Testing** | Real-time connectivity tests with latency measurement |
| **Test Persistence** | Test results saved to database on form submit and card quick-test |
| **Card Quick Test** | Test servers directly from server card with ⚡ button |
| **Tor Integration** | Automatic .onion detection, tests via SOCKS5 proxy |
| **Category System** | Organize servers with colored category labels |
| **Duplicate Detection** | Warns before adding duplicate server addresses |
| **Drag & Drop Sorting** | Reorder servers visually |
| **Dark/Light Mode** | Toggle UI theme, persists in localStorage |
| **Bilingual UI** | English/German language toggle |
| **Status Tracking** | Online/Offline/Error status saved with server |
| **ONION Badge** | Visual indicator for Tor hidden services |
| **Password Protection** | Show/hide server passwords in UI |
| **Responsive Design** | Works on desktop and mobile |

### 🚧 In Progress

| Feature | Status | Target |
|---------|--------|--------|
| **Stress Testing** | UI ready | v0.2.0 |
| **InfluxDB Integration** | Configured | v0.2.0 |
| **Grafana Dashboards** | Docker ready | v0.2.0 |
| **WebSocket Live Updates** | Channels ready | v0.3.0 |

### 📋 Planned

| Feature | Description |
|---------|-------------|
| **Scheduled Tests** | Cron-based automated testing |
| **Alerting** | Email/Webhook notifications on failures |
| **Multi-Node Support** | Monitor servers across multiple hosts |
| **API Endpoints** | REST API for external integrations |
| **Docker Deployment** | One-command setup |

---

## Screenshots

### Server List
![Server List](screenshots/serverlist.png)

*Dashboard showing server cards with status indicators, latency metrics, and quick actions*

---

## Architecture
```
┌─────────────────────────────────────────────────────────────────┐
│                    SimpleX SMP Monitor                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                  DJANGO APPLICATION                     │   │
│   │                                                         │   │
│   │   ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐      │   │
│   │   │Dashboard│ │ Servers │ │  Tests  │ │ Events  │      │   │
│   │   │  App    │ │   App   │ │   App   │ │   App   │      │   │
│   │   └─────────┘ └─────────┘ └─────────┘ └─────────┘      │   │
│   │                                                         │   │
│   │   ┌─────────────────────────────────────────────────┐   │   │
│   │   │              Core Module                        │   │   │
│   │   │   SimplexCLIManager  │  MetricsWriter          │   │   │
│   │   └─────────────────────────────────────────────────┘   │   │
│   └─────────────────────────────────────────────────────────┘   │
│                              │                                   │
│                              ▼                                   │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                  MONITORING STACK                       │   │
│   │                                                         │   │
│   │   ┌──────────┐    ┌──────────┐    ┌──────────┐         │   │
│   │   │ InfluxDB │◄───│ Telegraf │    │ Grafana  │         │   │
│   │   │ (Metrics)│    │ (Agent)  │    │ (Graphs) │         │   │
│   │   └──────────┘    └──────────┘    └──────────┘         │   │
│   │                                                         │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼ (Tor SOCKS5 Proxy)
                    ┌─────────────────┐
                    │  YOUR SIMPLEX   │
                    │    SERVERS      │
                    │  (.onion:5223)  │
                    └─────────────────┘
```

---

## Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| **Python** | 3.11+ | With pip and venv |
| **Tor** | Latest | For .onion server testing |
| **Git** | Any | For cloning repository |
| **Docker** | Optional | For InfluxDB/Grafana stack |

---

## Installation

### 1. Install System Dependencies

**Debian/Ubuntu:**
```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git curl
```

**Raspberry Pi OS:**
```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git curl
```

---

### 2. Install Tor

Tor is required for testing `.onion` server addresses.

**Debian/Ubuntu/Raspberry Pi OS:**
```bash
# Install Tor
sudo apt install -y tor

# Enable and start Tor service
sudo systemctl enable tor
sudo systemctl start tor

# Verify Tor is running
sudo systemctl status tor
```

**Verify SOCKS5 proxy is available:**
```bash
# Check Tor is listening on port 9050
ss -lntp | grep 9050

# Test Tor connectivity
curl -x socks5h://127.0.0.1:9050 -s https://check.torproject.org/api/ip | jq
```

Expected output:
```json
{
  "IsTor": true,
  "IP": "xxx.xxx.xxx.xxx"
}
```

> **Note:** The application automatically detects `.onion` addresses and routes tests through the Tor SOCKS5 proxy at `127.0.0.1:9050`.

---

### 3. Clone Repository
```bash
cd ~
git clone https://github.com/cannatoshi/simplex-smp-monitor.git
cd simplex-smp-monitor
```

---

### 4. Setup Python Environment
```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

---

### 5. Initialize Database
```bash
# Run migrations
python manage.py migrate

# Create superuser (optional, for admin access)
python manage.py createsuperuser
```

---

### 6. Start the Server

**Development (local access only):**
```bash
python manage.py runserver
```

**Development (network access):**
```bash
python manage.py runserver 0.0.0.0:8000
```

**Access the dashboard:**

- Local: http://127.0.0.1:8000
- Network: http://YOUR_IP:8000

---

## Tor Configuration

### Default Configuration

The application uses these default Tor settings:

| Setting | Value |
|---------|-------|
| SOCKS5 Host | `127.0.0.1` |
| SOCKS5 Port | `9050` |
| Timeout | `30 seconds` |

### Custom Tor SOCKS Proxy

If your Tor runs on a different port or host, edit `servers/views.py`:
```python
# Tor SOCKS5 Proxy Einstellungen
TOR_PROXY_HOST = '127.0.0.1'
TOR_PROXY_PORT = 9050  # Change this if needed
```

### Using a Remote Tor Proxy

If Tor runs on a different machine:
```python
TOR_PROXY_HOST = '192.168.1.100'  # Tor proxy host
TOR_PROXY_PORT = 9050
```

> **Security Note:** Only use remote Tor proxies over trusted networks.

---

## Environment Variables

For production deployment, create a `.env` file:
```bash
# Django
DEBUG=False
SECRET_KEY=your-super-secret-key-here
ALLOWED_HOSTS=your-domain.com,localhost,127.0.0.1

# Database (optional, defaults to SQLite)
DATABASE_URL=postgres://user:pass@localhost/simplex_monitor

# InfluxDB (optional)
INFLUXDB_URL=http://localhost:8086
INFLUXDB_TOKEN=your-influxdb-token
INFLUXDB_ORG=simplex
INFLUXDB_BUCKET=metrics

# Tor (optional, defaults shown)
TOR_SOCKS_HOST=127.0.0.1
TOR_SOCKS_PORT=9050
```

---

## Monitoring Stack (Optional)

For metrics and visualization, start the Docker stack:
```bash
# Start InfluxDB + Grafana
docker-compose up -d

# Check status
docker-compose ps
```

**Access:**

| Service | URL | Credentials |
|---------|-----|-------------|
| **Grafana** | http://localhost:3000 | admin / admin |
| **InfluxDB** | http://localhost:8086 | Set on first run |

---

## Usage

### Adding Servers

1. Navigate to **Servers** in the navigation bar
2. Click **+ Add Server**
3. Fill in the details across **7 configuration tabs**:
   - **Basic:** Name, type, address, location, priority, categories, active/maintenance toggles
   - **Monitoring:** Custom timeout, SLA targets (expected uptime %, max latency)
   - **SSH:** Host, port, username, key path for remote management
   - **Control Port:** SimpleX control port settings (port 5224, admin/user passwords)
   - **Telegraf:** Enable metrics collection, InfluxDB connection settings
   - **SimpleX Config:** Read-only server configuration (synced via SSH)
   - **Statistics:** Test statistics and history (only visible when editing)
4. Click **Test Connection** to verify connectivity
5. Click **Add Server** to save

> **Tip:** The application automatically detects `.onion` addresses and shows a purple "🧅 ONION" badge. Tests will be routed through Tor.

### Connection Testing

**From Add/Edit Form:**
- Click "Test Connection" button to verify server connectivity
- Test results (status + latency) are saved when you submit the form

**From Server Card:**
- Click the ⚡ button on any server card for instant testing
- Results are immediately saved to the database

**Tor Routing:**
- `.onion` addresses automatically use SOCKS5 proxy (127.0.0.1:9050)
- Clearnet addresses use direct TLS connection

**Latency:**
- Displayed in milliseconds after successful test
- Stored in database for historical tracking

### Stress Testing

*Coming in v0.2.0*

---

## Project Structure
```
simplex-smp-monitor/
├── config/                 # Django project settings
│   ├── settings.py         # Main configuration
│   ├── urls.py             # URL routing
│   └── asgi.py             # ASGI config for Daphne
├── core/                   # Shared utilities
│   ├── simplex/
│   │   └── cli_manager.py  # SimpleX CLI wrapper
│   └── metrics.py          # InfluxDB writer
├── dashboard/              # Dashboard app
│   ├── views.py
│   └── urls.py
├── servers/                # Server management app
│   ├── models.py           # Server & Category models
│   ├── views.py            # CRUD + testing views
│   ├── urls.py
│   └── templatetags/       # Custom template filters
├── stresstests/            # Stress testing app
│   ├── models.py
│   ├── views.py
│   └── urls.py
├── events/                 # Event logging app
│   ├── models.py
│   └── views.py
├── templates/              # HTML templates
│   ├── base.html           # Base template with nav
│   ├── dashboard/
│   ├── servers/
│   ├── stresstests/
│   └── events/
├── screenshots/            # Documentation images
├── docker-compose.yml      # InfluxDB + Grafana stack
├── telegraf.conf           # Telegraf configuration
├── requirements.txt        # Python dependencies
├── manage.py               # Django management script
├── LICENSE                 # AGPL-3.0 license
├── CHANGELOG.md            # Version history
└── README.md               # This file
```

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Backend** | Django 5.x, Django Channels |
| **Frontend** | HTMX, Alpine.js, Tailwind CSS |
| **Database** | SQLite (dev), PostgreSQL (prod) |
| **Time-Series** | InfluxDB 2.x |
| **Visualization** | Grafana |
| **Metrics Agent** | Telegraf |
| **ASGI Server** | Daphne |
| **Tor Proxy** | PySocks |

---

## Roadmap

### v0.2.0 - Metrics & Testing
- [ ] Complete InfluxDB integration
- [ ] Grafana dashboard templates
- [ ] Basic stress testing implementation
- [ ] Message send/receive verification

### v0.3.0 - Real-Time
- [ ] WebSocket live updates
- [ ] Real-time test progress
- [ ] Live server status

### v0.4.0 - Automation
- [ ] Scheduled test runs
- [ ] Email/Webhook alerts
- [ ] Test result history

### v0.5.0 - Production Ready
- [ ] Docker deployment
- [ ] PostgreSQL support
- [ ] Security hardening
- [ ] API documentation

### Future
- [ ] Multi-node support
- [ ] Custom test scenarios
- [ ] Performance analytics
- [ ] Mobile app

---

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## Related Projects

| Project | Description |
|---------|-------------|
| **[SimpleX Private Infrastructure](https://github.com/cannatoshi/simplex-smp-xftp-via-tor-on-rpi-hardened)** | Battle-tested guide to deploy SimpleX SMP/XFTP on Raspberry Pi with Tor |
| **[SimpleX Chat](https://github.com/simplex-chat/simplex-chat)** | The SimpleX Chat application |
| **[SimpleXMQ](https://github.com/simplex-chat/simplexmq)** | SimpleX Messaging Queue protocol |

---

## License

This project is licensed under the **GNU Affero General Public License v3.0** (AGPL-3.0).

See [LICENSE](LICENSE) for the full license text.

---

## Disclaimer

This software is provided "AS IS" without warranty of any kind. The authors are not responsible for any damages or issues arising from its use.

This tool is intended for monitoring your **own** infrastructure. Do not use it to test servers you do not own or have explicit permission to test.

---

## Changelog

### v0.1.5-alpha (2025-12-25)

**Added:**
- 7-Tab server configuration form (Basic, Monitoring, SSH, Control Port, Telegraf, SimpleX Config, Statistics)
- Extended server model with SSH, Control Port, Telegraf, SLA fields
- Test result persistence - connection tests save to database on form submit
- Card quick test button (⚡) with immediate database update
- Category system with colored labels for server organization
- Template tags for fingerprint/password extraction from address
- Screenshots folder with serverlist.png

**Changed:**
- Server form completely redesigned with tabbed interface
- Server cards now show quick test button and real-time latency
- Connection testing saves results when form is submitted

**Fixed:**
- Host property setter error (was read-only property)
- Category views and URLs restored after accidental removal

### v0.1.4-alpha (2025-12-24)

**Added:**
- Professional UI redesign with Dark/Light mode
- Bilingual support (English/German)
- Server connection testing with Tor SOCKS5 support
- Automatic .onion address detection
- Duplicate server detection
- Drag & drop server reordering
- Server status persistence (Online/Offline/Error)
- Password show/hide toggle
- ONION badge for Tor hidden services

**Changed:**
- Renamed project to "SimpleX SMP Monitor"
- Complete UI overhaul with Tailwind CSS

### v0.1.0-alpha (2025-12-23)

**Added:**
- Initial project structure
- Django 5.x + HTMX + Alpine.js foundation
- Server management (CRUD)
- Dashboard with statistics
- Event logging system
- InfluxDB/Grafana Docker stack

---

## Contact

- **GitHub:** [@cannatoshi](https://github.com/cannatoshi)
- **Issues:** [GitHub Issues](https://github.com/cannatoshi/simplex-smp-monitor/issues)

---

<p align="center">
  <sub>i(N) cod(E) w(E) trus(T)</sub>
</p>
