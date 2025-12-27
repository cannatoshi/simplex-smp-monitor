# SimpleX SMP Monitor

## Real-Time Server Monitoring & Stress Testing for SimpleX Infrastructure

[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL--3.0-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Python](https://img.shields.io/badge/Python-3.11+-3776ab.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.x-092E20.svg)](https://www.djangoproject.com/)
[![Status](https://img.shields.io/badge/Status-Alpha-orange.svg)](#status)
[![Tor](https://img.shields.io/badge/Tor-Supported-7D4698.svg)](https://www.torproject.org/)
[![Redis](https://img.shields.io/badge/Redis-7.x-DC382D.svg)](https://redis.io/)
[![Maintenance](https://img.shields.io/badge/Maintained-Actively-success.svg)](https://github.com/cannatoshi/simplex-smp-monitor/commits/main)
[![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-brightgreen.svg)](#contributing)

A web-based monitoring dashboard and stress testing suite for self-hosted SimpleX SMP/XFTP relay infrastructure. Built for operators who need visibility into their private messaging servers.

> **Version:** 0.1.8-alpha (27. December 2025)  
> **Status:** Active Development  
> **Tested on:** Debian 12, Ubuntu 24.04, Raspberry Pi OS (64-bit)  
> **Companion to:** [SimpleX Private Infrastructure Tutorial](https://github.com/cannatoshi/simplex-smp-xftp-via-tor-on-rpi-hardened)

---

> ⚠️ **ALPHA SOFTWARE**
>
> This project is in active development. Core features work, but expect rough edges.
> Not recommended for production use without thorough testing.
> 
> ✅ **What works:** Server management, multi-type testing, Tor support, i18n system, **CLI Clients with Delivery Receipts**, **🆕 Real-Time WebSocket Infrastructure**, **🆕 Redis Channel Layer**, **🆕 Auto-Start Event Bridge**  
> 🚧 **In progress:** InfluxDB metrics, Grafana dashboards, Test Panel

---

## 🚀 What's New in v0.1.8 - Real-Time Infrastructure

This release transforms the application from polling-based to **event-driven real-time architecture**:

```bash
# OLD WAY (v0.1.7) - Two separate processes
Terminal 1: python manage.py runserver 0.0.0.0:8000
Terminal 2: python manage.py listen_events  # <- EXTRA STEP!

# NEW WAY (v0.1.8) - Single command, everything auto-starts
python manage.py runserver 0.0.0.0:8000
# Event Bridge starts automatically! ✨
```

| Component | Description |
|-----------|-------------|
| **🔴 Redis Channel Layer** | Production-ready message broker (replaces InMemoryChannelLayer) |
| **🌉 SimplexEventBridge** | Auto-connects to all running containers, processes events, pushes to browsers |
| **📡 WebSocket Consumers** | Browser connections for live updates without page refresh |
| **⚡ Auto-Start** | Event Bridge starts automatically with Django - no more manual commands! |

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
8. [Install Docker](#3-install-docker)
9. [Setup Redis](#4-setup-redis-new-in-v018)
10. [Clone Repository](#5-clone-repository)
11. [Setup Python Environment](#6-setup-python-environment)
12. [Initialize Database](#7-initialize-database)
13. [Start the Server](#8-start-the-server)
14. [Setup CLI Clients](#9-setup-cli-clients)
15. [Event Listener Service (DEPRECATED)](#10-event-listener-service-deprecated-in-v018)

### Configuration
16. [Tor Configuration](#tor-configuration)
17. [Redis Configuration](#redis-configuration-new-in-v018)
18. [Environment Variables](#environment-variables)
19. [Monitoring Stack (Optional)](#monitoring-stack-optional)

### Usage
20. [Adding Servers](#adding-servers)
21. [Connection Testing](#connection-testing)
22. [Multi-Type Testing](#multi-type-testing)
23. [SimpleX CLI Clients - Complete Guide](#simplex-cli-clients---complete-guide)

### Development
24. [Project Structure](#project-structure)
25. [Tech Stack](#tech-stack)
26. [Roadmap](#roadmap)
27. [Troubleshooting](#troubleshooting)
28. [Contributing](#contributing)
29. [Related Projects](#related-projects)
30. [License](#license)
31. [Changelog](#changelog)

---

## About This Project

If you run your own SimpleX SMP/XFTP servers (especially via Tor hidden services), you need answers to questions like:

- **Are my servers reachable?** Test connectivity through Tor or clearnet
- **What's the latency?** Measure response times across your infrastructure  
- **Are messages being delivered?** Run stress tests to verify reliability
- **What's happening over time?** Historical metrics and visualizations
- **Do messages actually arrive at recipients?** Track delivery receipts end-to-end
- **Can I see updates in real-time?** WebSocket live updates without page refresh *(NEW in v0.1.8)*

This tool provides a **single dashboard** to monitor, test, and analyze your SimpleX relay infrastructure.

### Why This Tool?

| Problem | Solution |
|---------|----------|
| "Is my .onion server actually reachable?" | One-click connectivity test via Tor |
| "What's the latency to my servers?" | Real-time latency measurement |
| "Are messages being delivered reliably?" | Stress testing with delivery verification |
| "I have 10 servers, hard to track" | Central dashboard for all servers |
| "I need historical data" | InfluxDB + Grafana integration |
| "Do messages reach the recipient?" | CLI Clients with ✓/✓✓ delivery tracking |
| "I want instant feedback without page reloads" | **Real-time WebSocket updates** *(NEW in v0.1.8)* |
| "Managing the Event Listener is annoying" | **Auto-starts with Django** *(NEW in v0.1.8)* |

---

## Features

### ✅ Implemented (v0.1.8-alpha)

#### 🚀 Real-Time Infrastructure (NEW - Major Feature)

| Feature | Description |
|---------|-------------|
| **🔴 Redis Channel Layer** | Production-ready message broker for WebSocket communication |
| **🌉 SimplexEventBridge** | Auto-connects to all running containers, processes SimpleX events |
| **📡 WebSocket Consumers** | ClientUpdateConsumer + ClientDetailConsumer for live browser updates |
| **⚡ Auto-Start Integration** | Event Bridge starts automatically with Django (no more manual listen_events!) |
| **🟢 Live Status Indicator** | Green/red dot in navbar with connection status |
| **🖥️ Frontend WebSocket Client** | clients-live.js with auto-reconnect |

#### 🎨 UI/UX Improvements (Secondary)

| Feature | Description |
|---------|-------------|
| **4-Corner Stats Cards** | Redesigned statistics layout |
| **AJAX Messaging** | Send messages without page reload |
| **AJAX Connections** | Create/delete connections with animations |
| **Live SMP Server LEDs** | Pulsing indicators for server status |
| **Uptime Tracking** | Formatted display like "2h 15m" |
| **Latency Statistics** | Min/Max/Avg per client |

#### 🐳 CLI Clients & Core Features

| Feature | Description |
|---------|-------------|
| **SimpleX CLI Clients** | Docker-based test clients for end-to-end message delivery testing |
| **Delivery Receipts** | Track message status: ✓ server received, ✓✓ client received |
| **WebSocket Commands** | Real-time communication with SimpleX CLI via WebSocket API |
| **Message Statistics** | Per-client sent/received counters with success rates |
| **Multi-Type Test System** | Monitoring, Stress, and Latency tests with dedicated workflows |
| **APScheduler Integration** | Automated test execution with configurable intervals |
| **i18n Translation System** | Alpine.js based with JSON language files (EN/DE, 25 prepared) |
| **Live Countdown Timer** | Real-time test progress with Alpine.js reactivity |
| **Server Management** | Add, edit, delete SMP/XFTP servers with full CRUD |
| **7-Tab Configuration** | Basic, Monitoring, SSH, Control Port, Telegraf, SimpleX Config, Statistics |
| **Connection Testing** | Real-time connectivity tests with latency measurement |
| **Onion/ClearNet Badges** | Visual indicators for network type in results table |
| **Dynamic Grafana Links** | Auto-detect server IP instead of localhost |
| **Tor Integration** | Automatic .onion detection, tests via SOCKS5 proxy |
| **Category System** | Organize servers with colored category labels |
| **Dark/Light Mode** | Toggle UI theme, persists in localStorage |
| **Language Switcher** | EN/DE toggle in navigation header |
| **Responsive Design** | Works on desktop and mobile |

### 🚧 In Progress

| Feature | Status | Target |
|---------|--------|--------|
| **Test Panel** | UI Design | v0.2.0 |
| **Mesh Connections** | Planned | v0.2.0 |
| **InfluxDB Integration** | Configured | v0.2.0 |
| **Grafana Dashboards** | Docker ready | v0.2.0 |
| **Bridge Status API** | Architecture Ready | v0.2.0 |

### 📋 Planned

| Feature | Description |
|---------|-------------|
| **25 Language Support** | Full i18n for AR, ZH, JA, KO, RU, and 20 more |
| **Alerting** | Email/Webhook notifications on failures |
| **Multi-Node Support** | Monitor servers across multiple hosts |
| **API Endpoints** | REST API for external integrations |
| **Docker Deployment** | One-command setup |

---

## Screenshots

### Server List
![Server List](screenshots/serverlist.png)

*Dashboard showing server cards with status indicators, latency metrics, and quick actions*

### Server Monitoring Detail
![Server Monitoring](screenshots/server_monitoring.png)

*Detailed monitoring view with live countdown, test results table, and Grafana integration*

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         BROWSER (User)                                   │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  clients-live.js (NEW in v0.1.8)                                  │   │
│  │  - Auto-connect WebSocket (/ws/clients/)                          │   │
│  │  - Live DOM updates without refresh                               │   │
│  │  - Auto-reconnect on disconnect                                   │   │
│  └──────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                          WebSocket │ /ws/clients/
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         DJANGO + CHANNELS                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   ┌──────────────────────────────────────────────────────────────────┐  │
│   │  WebSocket Consumers (NEW in v0.1.8)                             │  │
│   │  - ClientUpdateConsumer (/ws/clients/)                           │  │
│   │  - ClientDetailConsumer (/ws/clients/<slug>/)                    │  │
│   └──────────────────────────────────────────────────────────────────┘  │
│                                    │                                    │
│                         Channel Layer (Redis)                           │
│                                    │                                    │
│   ┌──────────────────────────────────────────────────────────────────┐  │
│   │  SimplexEventBridge (NEW in v0.1.8)                              │  │
│   │  - Auto-started in background thread with Django                 │  │
│   │  - Connects to ALL running SimpleX containers                    │  │
│   │  - Processes: newChatItems, chatItemsStatusesUpdated             │  │
│   │  - Updates database, broadcasts to browsers                      │  │
│   └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│   ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐           │
│   │Dashboard│ │ Servers │ │  Tests  │ │ Events  │ │ Clients │           │
│   │  App    │ │   App   │ │   App   │ │   App   │ │   App   │           │
│   └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘           │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
            │                                              │
            │ WebSocket :3031-3080                         │ Pub/Sub
            ▼                                              ▼
┌─────────────────────────┐                    ┌─────────────────────────┐
│  SimpleX CLI Containers │                    │  Redis (Port 6379)      │
│  - Client 001 (:3031)   │                    │  (NEW in v0.1.8)        │
│  - Client 002 (:3032)   │                    │  - Channel Layer        │
│  - Client 003 (:3033)   │                    │  - Message Broker       │
│  - ...                  │                    └─────────────────────────┘
└─────────────────────────┘
            │
            ▼ (Messages via Tor/.onion)
┌─────────────────────────┐
│  Your SMP/XFTP Servers  │
│  (.onion:5223)          │
└─────────────────────────┘
```

---

## Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| **Python** | 3.11+ | With pip and venv |
| **Tor** | Latest | For .onion server testing |
| **Git** | Any | For cloning repository |
| **Docker** | 24.x+ | For CLI Clients, Redis, InfluxDB/Grafana |
| **Redis** | 7.x | **NEW in v0.1.8** - For real-time WebSocket communication |

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

### 3. Install Docker

Docker is required for the SimpleX CLI Clients feature and Redis.

**Debian/Ubuntu/Raspberry Pi OS:**
```bash
# Install Docker
sudo apt install -y docker.io docker-compose

# Add your user to the docker group (avoids needing sudo)
sudo usermod -aG docker $USER

# IMPORTANT: Log out and log back in for group changes to take effect
# Or run: newgrp docker

# Enable Docker to start on boot
sudo systemctl enable docker
sudo systemctl start docker

# Verify Docker is working
docker --version
docker run hello-world
```

**Expected output:**
```
Docker version 24.x.x, build xxxxxxx
Hello from Docker!
This message shows that your installation appears to be working correctly.
```

**Troubleshooting:**
```bash
# If you get "permission denied" errors:
sudo chmod 666 /var/run/docker.sock

# Or re-login to apply group changes:
su - $USER
```

---

### 4. Setup Redis (NEW in v0.1.8)

Redis is the backbone for real-time WebSocket communication.

```bash
# Start Redis container (persistent data)
docker run -d \
  --name simplex-redis \
  --restart unless-stopped \
  -p 6379:6379 \
  -v simplex-redis-data:/data \
  redis:7-alpine redis-server --appendonly yes

# Verify Redis is running
docker ps | grep redis

# Test Redis connection
docker exec simplex-redis redis-cli ping
```

Expected output:
```
PONG
```

**Why Redis?**

| Feature          | InMemoryChannelLayer | Redis        |
|------------------|----------------------|--------------|
| Multi-process    | ❌ No                | ✅ Yes      |
| Production-ready | ⚠️ Dev only          | ✅ Yes      |
| 50+ Clients      | ❓ Maybe             | ✅ Stable   |
| Persistence      | ❌ No                | ✅ Optional |

---

### 5. Clone Repository

```bash
cd ~
git clone https://github.com/cannatoshi/simplex-smp-monitor.git
cd simplex-smp-monitor
```

---

### 6. Setup Python Environment

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

### 7. Initialize Database

```bash
# Run migrations
python manage.py migrate

# Create superuser (optional, for admin access)
python manage.py createsuperuser
```

---

### 8. Start the Server

**Development (local access only):**
```bash
python manage.py runserver
```

**Development (network access):**
```bash
python manage.py runserver 0.0.0.0:8000
```

**You should see (NEW in v0.1.8):**
```
🚀 APScheduler gestartet - prüft alle 30 Sekunden
✅ APScheduler gestartet - Monitoring läuft!
INFO 🌉 Event Bridge thread started
INFO 🚀 SimplexEventBridge starting...
December 27, 2025 - 13:07:32
Django version 5.2.9, using settings 'config.settings'
Starting ASGI/Daphne version 4.2.1 development server at http://0.0.0.0:8000/
```

When you have running clients:
```
INFO ✓ Connected to Client 001
INFO ✓ Connected to Client 002
INFO   📡 Listening: Client 001 (ws://localhost:3031)
INFO   📡 Listening: Client 002 (ws://localhost:3032)
```

**Access the dashboard:**

- Local: http://127.0.0.1:8000
- Network: http://YOUR_IP:8000

---

### 9. Setup CLI Clients

The CLI Clients feature requires a custom Docker image. Follow these steps to set it up:

#### 9.1 Build the Docker Image

```bash
# Navigate to the docker directory
cd ~/simplex-smp-monitor/clients/docker

# Build the image (this may take 2-5 minutes)
docker build -t simplex-cli:latest -f Dockerfile.simplex-cli .

# Verify the image was created
docker images | grep simplex-cli
```

**Expected output:**
```
simplex-cli    latest    abc123def456    1 minute ago    ~350MB
```

#### 9.2 Test the Image (Optional)

```bash
# Run a test container
docker run -d --name test-simplex \
  -e SIMPLEX_PORT=3099 \
  -e PROFILE_NAME=testuser \
  -p 3099:3099 \
  simplex-cli:latest

# Check logs
docker logs test-simplex

# Clean up test container
docker rm -f test-simplex
```

#### 9.3 Return to Project Root

```bash
cd ~/simplex-smp-monitor
```

---

### 10. Event Listener Service (DEPRECATED in v0.1.8)

> ⚠️ **DEPRECATED:** In v0.1.8, the SimplexEventBridge starts automatically with Django. You no longer need to run `listen_events` manually or as a separate service!
>
> The information below is kept for users on v0.1.7 or for troubleshooting purposes.

<details>
<summary>Click to expand v0.1.7 Event Listener documentation</summary>

The Event Listener monitors all running clients for delivery receipts. You can run it manually or as a systemd service.

#### Option A: Manual Start (for Testing)

```bash
# Activate virtual environment
source ~/simplex-smp-monitor/.venv/bin/activate

# Start the listener
python manage.py listen_events
```

You'll see output like:
```
Starting Event Listener...
Listening to 3 clients...
  ✓ Connected: Client 001 (ws://localhost:3031)
  ✓ Connected: Client 002 (ws://localhost:3032)
  ✓ Connected: Client 003 (ws://localhost:3033)
```

#### Option B: Systemd Service (for v0.1.7)

Create a systemd service file:

```bash
sudo nano /etc/systemd/system/simplex-events.service
```

Paste the following (adjust paths and username as needed):

```ini
[Unit]
Description=SimpleX SMP Monitor Event Listener
After=network.target docker.service
Requires=docker.service

[Service]
Type=simple
User=YOUR_USERNAME
Group=YOUR_USERNAME
WorkingDirectory=/home/YOUR_USERNAME/simplex-smp-monitor
Environment="PATH=/home/YOUR_USERNAME/simplex-smp-monitor/.venv/bin"
ExecStart=/home/YOUR_USERNAME/simplex-smp-monitor/.venv/bin/python manage.py listen_events
Restart=always
RestartSec=10

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=simplex-events

[Install]
WantedBy=multi-user.target
```

**Replace `YOUR_USERNAME` with your actual username** (e.g., `cannatoshi`).

Enable and start the service:

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable simplex-events

# Start the service
sudo systemctl start simplex-events

# Check status
sudo systemctl status simplex-events
```

**View logs:**
```bash
# Follow logs in real-time
sudo journalctl -u simplex-events -f

# View last 100 lines
sudo journalctl -u simplex-events -n 100
```

**Manage the service:**
```bash
# Stop
sudo systemctl stop simplex-events

# Restart
sudo systemctl restart simplex-events

# Disable autostart
sudo systemctl disable simplex-events
```

</details>

---

## Tor Configuration

### Default Configuration

The application uses these default Tor settings:

| Setting     | Value        |
|-------------|--------------|
| SOCKS5 Host | `127.0.0.1`  |
| SOCKS5 Port | `9050`       |
| Timeout     | `30 seconds` |

### Custom Tor SOCKS Proxy

If your Tor runs on a different port or host, edit `servers/views.py`:
```python
# Tor SOCKS5 Proxy Settings
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

## Redis Configuration (NEW in v0.1.8)

### Default Configuration

The application expects Redis on localhost:6379.

**Django Settings (`config/settings.py`):**
```python
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
        },
    },
}
```

### Remote Redis

If Redis runs on a different host:
```python
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("192.168.1.100", 6379)],
        },
    },
}
```

### Redis with Authentication

```python
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("redis://:password@127.0.0.1:6379/0",)],
        },
    },
}
```

### Check Redis Status

```bash
# Check if container is running
docker ps | grep redis

# Check Redis logs
docker logs simplex-redis

# Test connection
docker exec simplex-redis redis-cli ping
```

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

# Redis (NEW in v0.1.8)
REDIS_HOST=127.0.0.1
REDIS_PORT=6379

# InfluxDB (optional)
INFLUXDB_URL=http://localhost:8086
INFLUXDB_TOKEN=your-influxdb-token
INFLUXDB_ORG=simplex
INFLUXDB_BUCKET=metrics

# Tor (optional, defaults shown)
TOR_SOCKS_HOST=127.0.0.1
TOR_SOCKS_PORT=9050

# Docker (for CLI Clients)
DOCKER_HOST=unix:///var/run/docker.sock
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

### Multi-Type Testing

The application supports three types of tests:

| Test Type      | Purpose                                | Use Case                   |
|----------------|----------------------------------------|----------------------------|
| **Monitoring** | Connectivity & uptime checks           | Regular health monitoring  |
| **Stress**     | Load testing with multiple connections | Capacity planning          |
| **Latency**    | Response time measurement              | Performance optimization   |

**Creating a Test:**
1. Navigate to **Tests** → **New Test**
2. Select test type (Monitoring, Stress, or Latency)
3. Choose servers to include
4. Configure test parameters
5. Start test and monitor progress with live countdown

---

## SimpleX CLI Clients - Complete Guide

### What Are CLI Clients?

CLI Clients are Docker containers running the SimpleX Chat CLI application. They allow you to:

- **Test message delivery** between multiple clients
- **Verify your SMP servers** are routing messages correctly
- **Measure delivery latency** in real-time
- **Track delivery receipts** (✓ server received, ✓✓ client received)

Each client runs in isolation with its own identity, contacts, and message history.

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     Your Server                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │  Client 001  │  │  Client 002  │  │  Client 003  │           │
│  │   (quinn)    │  │    (rosa)    │  │    (kate)    │           │
│  │  Port 3031   │  │  Port 3032   │  │  Port 3033   │           │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘           │
│         │                 │                 │                   │
│         └────────────┬────┴────┬────────────┘                   │
│                      │         │                                │
│                      ▼         ▼                                │
│              ┌───────────────────────┐                          │
│              │  SimplexEventBridge   │  ← Auto-starts with      │
│              │  (NEW in v0.1.8)      │    Django!               │
│              └───────────┬───────────┘                          │
│                          │                                      │
│                          ▼                                      │
│              ┌───────────────────────┐                          │
│              │   Redis Channel Layer │  ← Real-time pub/sub     │
│              └───────────┬───────────┘                          │
│                          │                                      │
│                          ▼                                      │
│              ┌───────────────────────┐                          │
│              │   Browser WebSocket   │  ← Live updates!         │
│              └───────────────────────┘                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                           │
                           ▼ (Messages via Tor/.onion)
                  ┌─────────────────┐
                  │  Your SMP/XFTP  │
                  │    Servers      │
                  └─────────────────┘
```

### Step 1: Navigate to Clients

1. Open your browser and go to `http://YOUR_IP:8000`
2. Click **Clients** in the navigation bar
3. You'll see the client list (empty initially)

### Step 2: Create Your First Client

1. Click **+ New Client** button
2. The form auto-generates:
   - **Name**: "Client 001", "Client 002", etc.
   - **Slug**: "client-001", "client-002", etc.
   - **Profile Name**: Random name (quinn, rosa, kate, etc.)
   - **WebSocket Port**: Auto-assigned (3031, 3032, etc.)
3. Optionally enable **Tor** if your SMP servers use .onion addresses
4. Click **Create**

### Step 3: Start the Client

After creating, you'll see the client in the list with status "Created".

1. Click on the client name to open the **Detail Page**
2. Click the green **Start** button
3. Wait 10-30 seconds for the container to initialize
4. Status changes to **Running** (green indicator)

**What happens when you start:**
1. Docker creates a container from `simplex-cli:latest`
2. SimpleX CLI initializes with the profile name
3. If Tor is enabled, Tor daemon starts inside the container
4. Socat starts forwarding WebSocket traffic
5. Health check verifies everything is running

### Step 4: Check Container Logs

On the client detail page, you'll see the **Container Logs** section showing:

```
=== SimpleX CLI Container Starting ===
External Port: 3031
Tor: true
Profile: quinn
Starting Tor...
Tor started successfully
Starting simplex-chat...
Starting socat forwarder...
=== Ready ===
```

### Step 5: Create More Clients

Repeat steps 2-3 to create at least **2 clients** (you need 2 to test messaging).

Example setup:
- **Client 001** (quinn) - Port 3031
- **Client 002** (rosa) - Port 3032
- **Client 003** (kate) - Port 3033

### Step 6: Create Connections Between Clients

Clients need to be "connected" before they can exchange messages (just like in the real SimpleX app).

1. Open **Client 001** detail page
2. Find the **Connections** section
3. Click **+ New Connection**
4. Select **Client 002** from the dropdown
5. Click **Connect**

**What happens:**
1. Client 002 creates an invitation address
2. Client 002 enables Auto-Accept for incoming contacts
3. Client 001 connects using the invitation link
4. Both clients exchange keys and establish contact
5. Connection is saved in the database

**Result:**
- Client 001 sees contact named "rosa" (Client 002's profile)
- Client 002 sees contact named "quinn" (Client 001's profile)

### Step 7: Send Messages

Once connected, you can send messages:

1. On **Client 001** detail page, find **Send Message** form
2. Select recipient: **rosa** (Client 002)
3. Type a message: "Hello from Client 001!"
4. Click **Send**

**Message Flow:**
```
Client 001 (quinn)
       │
       │ 1. Send "Hello from Client 001!"
       ▼
  Your SMP Server (.onion)
       │
       │ 2. Server stores message
       │ 3. Server sends ✓ (sndSent) to Client 001
       │
       │ 4. Client 002 retrieves message
       ▼
Client 002 (rosa)
       │
       │ 5. Client 002 sends receipt
       ▼
  Your SMP Server
       │
       │ 6. Server forwards ✓✓ (sndRcvd) to Client 001
       ▼
Client 001 (quinn)
       │
       │ 7. UI shows ✓✓ Delivered (NO PAGE REFRESH in v0.1.8!)
       ▼
```

### Step 8: Understanding Message Status

The **Messages** section shows three tabs:

#### Tab 1: ↑ Sent (Outgoing Messages)

| Time | Recipient | Message | Status | Latency |
|------|-----------|---------|--------|---------|
| 14:32 | rosa | Hello from Client 001! | ✓✓ | 1,234ms |

#### Tab 2: ↓ Received (Incoming Messages)

| Time | Sender | Message | Status |
|------|--------|---------|--------|
| 14:33 | rosa | Hello back! | ✓ |

#### Tab 3: All (Combined View)

| Time | ↕ | Contact | Message | Status | Latency |
|------|---|---------|---------|--------|---------|
| 14:32 | ↑ | rosa | Hello from Client 001! | ✓✓ | 1,234ms |
| 14:33 | ↓ | rosa | Hello back! | ✓ | - |

**Status Icons Explained:**

| Icon | Status | Meaning |
|------|--------|---------|
| ⏳ | pending | Message is being sent |
| ✓ | sent | SMP server received the message |
| ✓✓ | delivered | Recipient client received the message |
| ✗ | failed | Message delivery failed |

### Step 9: Real-Time Updates (NEW in v0.1.8)

In v0.1.8, message status updates happen **automatically** via WebSocket:

- When a message is delivered (✓ → ✓✓), the UI updates instantly
- No page refresh needed
- The SimplexEventBridge handles everything in the background

**Check if it's working:**
- Look for the green "Live" indicator in the navigation bar
- Check Django console for "📡 Listening:" messages

### Step 10: Managing Clients

#### Start/Stop/Restart

- **Stop**: Stops the container but keeps data volume
- **Restart**: Stops and starts the container
- **Start**: Starts a stopped container

#### Delete a Client

1. Click **Delete** button (red)
2. Confirm deletion
3. Both the database entry AND Docker container are removed

> **Note:** In v0.1.7, the delete bug was fixed - containers are now properly removed from Docker.

### Client Statistics

Each client shows statistics:

| Stat             | Description                       |
|------------------|-----------------------------------|
| **Status**       | Running / Stopped / Created       |
| **Sent**         | Number of messages sent           |
| **Received**     | Number of messages received       |
| **Success Rate** | Percentage of delivered messages  |

### Capacity & Performance

**Raspberry Pi 5** (8GB RAM, 128GB NVMe, Debian 12):

| Clients | RAM Usage | Status      |
|---------|-----------|-------------|
| 6       | ~400 MB   | ✅ Stable  |
| 10      | ~650 MB   | ✅ Stable  |
| 20      | ~1.2 GB   | ✅ Stable  |
| 50      | ~3 GB     | ⚠️ Tested  |

**Debian Server** (T1, 128GB RAM, NVMe SSD):

| Clients | RAM Usage | Status      |
|---------|-----------|-------------|
| 50      | ~3 GB     | ✅ Stable  |
| 100     | ~6 GB     | ✅ Stable  |
| 200     | ~12 GB    | ✅ Stable  |
| 500     | ~30 GB    | ⚠️ Tested  |

**Resource usage per client:**
- ~50-60 MB RAM (without Tor)
- ~70-80 MB RAM (with Tor)
- Minimal CPU when idle
- ~1 KB per WebSocket connection

### Troubleshooting CLI Clients

#### Client won't start
```bash
# Check Docker logs
docker logs simplex-client-client-001

# Check if port is in use
ss -tlnp | grep 3031

# Check Docker status
docker ps -a | grep simplex-client
```

#### Messages stuck on ✓ (not ✓✓)
```bash
# v0.1.8: Check if Event Bridge is running
# Look for "📡 Listening:" in Django console

# v0.1.7: Check Event Listener
sudo systemctl status simplex-events
sudo journalctl -u simplex-events -f
```

#### WebSocket connection failed
```bash
# Test WebSocket manually
websocat ws://localhost:3031

# Check container health
docker inspect simplex-client-client-001 | grep -A5 Health
```

#### Container keeps restarting
```bash
# Check container logs for errors
docker logs --tail 50 simplex-client-client-001

# Check disk space
df -h
```

### Best Practices

1. **Start with 2-3 clients** for initial testing
2. **Enable Tor** if your SMP servers use .onion addresses
3. **Check Redis is running** for real-time updates (v0.1.8+)
4. **Monitor RAM usage** when adding many clients
5. **Delete unused clients** to free resources

---

## Project Structure
```
simplex-smp-monitor/
├── config/                     # Django project settings
│   ├── settings.py             # Main configuration + Redis Channel Layer
│   ├── urls.py                 # URL routing
│   ├── asgi.py                 # ASGI config with WebSocket routing
│   └── wsgi.py
├── core/                       # Shared utilities
│   ├── __init__.py
│   └── metrics.py              # InfluxDB writer
├── dashboard/                  # Dashboard app
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── consumers.py            # WebSocket consumers
│   └── routing.py              # WebSocket routing
├── servers/                    # Server management app
│   ├── models.py               # Server & Category models
│   ├── views.py                # CRUD + testing views
│   ├── urls.py
│   └── templatetags/           # Custom template filters
│       └── server_tags.py
├── stresstests/                # Multi-type testing app
│   ├── models.py               # TestRun, TestResult
│   ├── views.py                # Test execution views
│   ├── scheduler.py            # APScheduler integration
│   ├── tasks.py
│   └── urls.py
├── clients/                    # SimpleX CLI Clients app
│   ├── models.py               # SimplexClient, ClientConnection, TestMessage
│   ├── views.py                # Client management views
│   ├── urls.py
│   ├── forms.py                # Client creation forms
│   ├── consumers.py            # 🆕 WebSocket Consumers (v0.1.8)
│   ├── routing.py              # 🆕 WebSocket URLs (v0.1.8)
│   ├── apps.py                 # 🆕 Auto-start Event Bridge (v0.1.8)
│   ├── services/
│   │   ├── docker_manager.py   # Docker container lifecycle
│   │   ├── simplex_commands.py # WebSocket command service
│   │   ├── event_bridge.py     # 🆕 SimplexEventBridge (v0.1.8)
│   │   └── websocket_pool.py   # WebSocket connection pooling
│   ├── docker/
│   │   ├── Dockerfile.simplex-cli
│   │   └── entrypoint.sh
│   ├── management/commands/
│   │   ├── listen_events.py    # Event listener (deprecated in v0.1.8)
│   │   └── clients.py          # Client management commands
│   └── templates/clients/
│       ├── list.html
│       ├── detail.html
│       ├── form.html
│       ├── confirm_delete.html
│       ├── test_panel.html
│       └── partials/
│           ├── _stats.html
│           ├── _sidebar.html
│           └── _connections.html
├── events/                     # Event logging app
│   ├── models.py
│   ├── views.py
│   └── urls.py
├── templates/                  # Global HTML templates
│   ├── base.html
│   ├── dashboard/
│   ├── servers/
│   ├── stresstests/
│   └── events/
├── static/
│   ├── css/
│   │   └── app.css
│   └── js/
│       ├── clients-live.js     # 🆕 Frontend WebSocket client (v0.1.8)
│       ├── i18n.js             # Translation system
│       └── lang/               # Language files
│           ├── en.json
│           └── de.json
├── monitoring/                 # Monitoring stack configs
│   ├── grafana/
│   │   ├── dashboards/
│   │   └── provisioning/
│   └── telegraf/
│       └── telegraf.conf
├── scripts/                    # Helper scripts
│   ├── install_telegraf_rpi.sh
│   └── start_dev.sh
├── screenshots/                # Documentation images
├── docker-compose.yml          # InfluxDB + Grafana + Redis stack
├── requirements.txt
├── manage.py
├── LICENSE                     # AGPL-3.0
├── CHANGELOG.md
├── ROADMAP.md
└── README.md
```

---

## Tech Stack

| Layer | Technology |
|--------------------|-----------------------------------------------------------------|
| **Backend**        | Django 5.x, Django Channels, APScheduler                        |
| **Real-Time**      | **Redis 7.x** (Channel Layer), **WebSockets** *(NEW in v0.1.8)* |
| **Frontend**       | HTMX, Alpine.js, Tailwind CSS                                   |
| **i18n**           | Alpine.js $store with JSON language files                       |
| **Database**       | SQLite (dev), PostgreSQL (prod)                                 |
| **Time-Series**    | InfluxDB 2.x                                                    |
| **Visualization**  | Grafana                                                         |
| **Metrics Agent**  | Telegraf                                                        |
| **ASGI Server**    | Daphne                                                          |
| **Tor Proxy**      | PySocks                                                         |
| **Containers**     | Docker 24.x (for CLI Clients + Redis)                           |
| **WebSocket**      | websockets (Python async library)                               |

---

## Roadmap

### ✅ v0.1.8 - Real-Time Infrastructure (COMPLETED)
- [x] Redis Channel Layer
- [x] SimplexEventBridge with auto-start
- [x] WebSocket Consumers
- [x] Frontend WebSocket client
- [x] Live status indicator
- [x] UI/UX improvements

### v0.2.0 - Test Panel & Mesh Connections
- [ ] Test Panel UI for bulk messaging scenarios
- [ ] Mesh connections (connect all clients with each other)
- [ ] Bulk client creation (create 10/20/50 clients at once)
- [ ] Bridge status API endpoint
- [ ] Complete InfluxDB integration
- [ ] Grafana dashboard templates
- [ ] Automated test schedules

### v0.3.0 - i18n & Alerts
- [ ] Activate all 25 languages
- [ ] RTL support (Arabic, Hebrew)
- [ ] Email/Webhook alerts
- [ ] Test result history
- [ ] Export results (CSV/JSON)

### v0.4.0 - Production Ready
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

## Troubleshooting

### Redis Not Running

```bash
# Check if container exists
docker ps -a | grep redis

# Start if stopped
docker start simplex-redis

# If doesn't exist, create it
docker run -d \
  --name simplex-redis \
  --restart unless-stopped \
  -p 6379:6379 \
  -v simplex-redis-data:/data \
  redis:7-alpine redis-server --appendonly yes

# Test connection
docker exec simplex-redis redis-cli ping
```

### Event Bridge Not Starting

```bash
# In Django output, you should see:
INFO 🌉 Event Bridge thread started
INFO 🚀 SimplexEventBridge starting...

# If not visible, check settings.py logging config
```

### WebSocket Not Connecting

1. Check browser console (F12) for errors
2. Verify ASGI routing in `config/asgi.py`
3. Check Redis is running: `docker exec simplex-redis redis-cli ping`

### 404 Error on "Send Message"

**Cause:** URL routing order - specific routes must come before generic slug routes.

**Solution:** Check `clients/urls.py`:
```python
urlpatterns = [
    # Specific routes FIRST
    path('messages/send/', views.SendMessageView.as_view(), name='send_message'),
    # Generic slug routes LAST
    path('<slug:slug>/', views.ClientDetailView.as_view(), name='detail'),
]
```

### Messages Stuck on ✓ (not ✓✓)

**v0.1.8:** Check Event Bridge is connected:
```bash
# Look for "📡 Listening:" messages in Django console
```

**v0.1.7:** Check Event Listener:
```bash
sudo systemctl status simplex-events
sudo journalctl -u simplex-events -f
```

### Client Won't Start

```bash
# Check Docker logs
docker logs simplex-client-client-001

# Check if port is in use
ss -tlnp | grep 3031

# Check Docker image exists
docker images | grep simplex-cli
```

### Debug Mode

Enable Django debug mode for detailed error messages:
```python
# config/settings.py
DEBUG = True
```

Check browser console (F12 → Console tab) for JavaScript errors.

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

- **[SimpleX Private Infrastructure](https://github.com/cannatoshi/simplex-smp-xftp-via-tor-on-rpi-hardened)**  
  Battle-tested guide to deploy SimpleX SMP/XFTP on Raspberry Pi with Tor

- **[SimpleX Chat](https://github.com/simplex-chat/simplex-chat)**  
  The SimpleX Chat application

- **[SimpleXMQ](https://github.com/simplex-chat/simplexmq)**  
  SimpleX Messaging Queue protocol

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

### v0.1.8-alpha (2025-12-27)

**🚀 MAJOR FEATURE: Real-Time Infrastructure**

The application is transformed from polling-based to event-driven architecture:

- **🔴 Redis Channel Layer** - Production-ready message broker
- **🌉 SimplexEventBridge** - Auto-connects to all containers, processes events
- **📡 WebSocket Consumers** - ClientUpdateConsumer + ClientDetailConsumer
- **⚡ Auto-Start Integration** - Event Bridge starts with Django (no more manual listen_events!)
- **🟢 Live Status Indicator** - Green/red dot with connection status
- **🖥️ Frontend WebSocket Client** - clients-live.js with auto-reconnect

**🎨 Secondary: UI/UX Improvements:**
- 4-Corner Stats Cards layout
- AJAX Messaging System
- AJAX Connection Management
- Live SMP Server LEDs
- Uptime tracking, Latency statistics

**🐛 Fixes:**
- URL routing order (specific routes before slug)
- SendMessageView AJAX response
- SMP LED status field reference

**⚠️ Deprecation:**
- `python manage.py listen_events` is deprecated (still works but not needed)

**📦 New Dependencies:**
```bash
pip install channels-redis
```

**🔧 Upgrade from v0.1.7:**
1. Start Redis container (see Installation Step 4)
2. `pip install channels-redis`
3. Update settings.py with Redis Channel Layer config
4. Copy new files (consumers.py, routing.py, event_bridge.py, clients-live.js)
5. Stop simplex-events service if running
6. Restart Django server

### v0.1.7-alpha (2025-12-27)

**Added:**
- 🆕 **SimpleX CLI Clients App** - Docker-based test clients for end-to-end message delivery testing
- **Docker Container Management** - Start/Stop/Restart/Delete with proper cleanup
- **Dockerfile.simplex-cli** - Custom image with SimpleX CLI, optional Tor, socat forwarder
- **entrypoint.sh** - Container entrypoint with health checks
- **SimplexCommandService** - WebSocket command service for real-time communication
- **Client Connections** - Create connections between clients with Auto-Accept
- **Message Sending** - Send messages via WebSocket with database tracking
- **Delivery Receipt Tracking** - ✓ (server received), ✓✓ (client received)
- **listen_events Command** - Background event listener for delivery confirmations
- **Latency Measurement** - Per-message delivery time in milliseconds
- **Table-based Message UI** - Tabs for Sent/Received/All messages
- **Message Statistics** - Per-client sent/received counters with success rates

**Fixed:**
- **Container Deletion Bug** - Docker containers now properly removed when deleting clients
- **Django 4+ DeleteView** - Changed from `delete()` to `post()` method
- **Auto-Accept Order** - Must be called after address creation, not before
- **Container Lookup** - Fallback to container name if ID lookup fails
- **Template Grid Layout** - Fixed sidebar positioning in client detail view

**Technical:**
- New services: `docker_manager.py`, `simplex_commands.py`
- New Docker files: `Dockerfile.simplex-cli`, `entrypoint.sh`
- New management command: `listen_events.py`
- Port range: 3031-3080 (configurable)
- Tested: 6 clients stable on Raspberry Pi 5 (8GB RAM, 128GB NVMe)

### v0.1.6-alpha (2025-12-26)

**Added:**
- Multi-type test framework (Monitoring, Stress, Latency) with dedicated workflows
- APScheduler integration for automated test execution
- Professional i18n system with Alpine.js `$store.i18n`
- JSON language files (`static/js/i18n/en.json`, `de.json`)
- EN/DE translations active, 25 languages prepared for future activation
- `timeAgo()` function for relative time display (e.g., "2 minutes ago")
- Live countdown timer with real-time Alpine.js updates
- Onion/ClearNet badges in test results table
- Dynamic Grafana IP detection (replaces hardcoded localhost)
- Language switcher in navigation header

**Changed:**
- Complete test system refactor with new models (TestRun, TestResult, ServerStats)
- Symmetric 4-tile monitoring dashboard layout
- Test detail pages redesigned for each test type

**Fixed:**
- Success rate calculation now capped at 100% (was showing 140%+)
- Grafana links now use actual server IP instead of localhost

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
