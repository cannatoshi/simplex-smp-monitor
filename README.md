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
> ✅ **What works:** Server management, multi-type testing, Tor support, i18n system, **CLI Clients with Delivery Receipts**, **AJAX Messaging**, **Live UI Updates**  
> 🚧 **In progress:** InfluxDB metrics, Grafana dashboards, WebSocket updates, Test Panel

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
9. [Clone Repository](#4-clone-repository)
10. [Setup Python Environment](#5-setup-python-environment)
11. [Initialize Database](#6-initialize-database)
12. [Start the Server](#7-start-the-server)
13. [Setup CLI Clients](#8-setup-cli-clients-new-in-v017)
14. [Setup Event Listener Service](#9-setup-event-listener-service-new-in-v017)

### Configuration
15. [Tor Configuration](#tor-configuration)
16. [Environment Variables](#environment-variables)
17. [Monitoring Stack (Optional)](#monitoring-stack-optional)

### Usage
18. [Adding Servers](#adding-servers)
19. [Connection Testing](#connection-testing)
20. [Multi-Type Testing](#multi-type-testing)
21. [SimpleX CLI Clients - Complete Guide](#simplex-cli-clients---complete-guide)
22. [Client Detail Page - UI Features (NEW in v0.1.8)](#client-detail-page---ui-features-new-in-v018)

### Development
23. [Project Structure](#project-structure)
24. [Tech Stack](#tech-stack)
25. [Roadmap](#roadmap)
26. [Troubleshooting](#troubleshooting)
27. [Contributing](#contributing)
28. [Related Projects](#related-projects)
29. [License](#license)
30. [Changelog](#changelog)

---

## About This Project

If you run your own SimpleX SMP/XFTP servers (especially via Tor hidden services), you need answers to questions like:

- **Are my servers reachable?** Test connectivity through Tor or clearnet
- **What's the latency?** Measure response times across your infrastructure  
- **Are messages being delivered?** Run stress tests to verify reliability
- **What's happening over time?** Historical metrics and visualizations
- **Do messages actually arrive at recipients?** Track delivery receipts end-to-end *(NEW)*
- **What's my success rate?** Real-time statistics with latency tracking *(NEW in v0.1.8)*

This tool provides a **single dashboard** to monitor, test, and analyze your SimpleX relay infrastructure.

### Why This Tool?

| Problem | Solution |
|---------|----------|
| "Is my .onion server actually reachable?" | One-click connectivity test via Tor |
| "What's the latency to my servers?" | Real-time latency measurement |
| "Are messages being delivered reliably?" | Stress testing with delivery verification |
| "I have 10 servers, hard to track" | Central dashboard for all servers |
| "I need historical data" | InfluxDB + Grafana integration |
| "Do messages reach the recipient?" | CLI Clients with ✓/✓✓ delivery tracking *(NEW)* |
| "I want instant feedback without page reloads" | AJAX messaging with live UI updates *(NEW in v0.1.8)* |

---

## Features

### ✅ Implemented (v0.1.8-alpha)

| Feature | Description |
|---------|-------------|
| **🆕 AJAX Messaging System** | Send messages without page reload, instant UI feedback with animations |
| **🆕 AJAX Connection Management** | Create/delete connections with smooth slide-in/slide-out animations |
| **🆕 4-Corner Stats Cards** | Redesigned statistics display with corner-based information layout |
| **🆕 Equal Height Layout** | Sidebar and content always match heights dynamically using CSS Grid + Flexbox |
| **🆕 Live SMP Server LEDs** | Pulsing green indicators for online servers, red for offline, gray for unknown |
| **🆕 Smart Connection Button** | Shows "(no more clients)" when all possible connections exist |
| **🆕 Uptime Tracking** | Shows formatted uptime like "2h 15m" or "3d 5h" for running clients |
| **🆕 Latency Statistics** | Min/Max/Average latency per client with sparkline placeholder |
| **🆕 Model Methods** | New start(), stop(), set_error() methods for client lifecycle management |
| **SimpleX CLI Clients** | Docker-based test clients for end-to-end message delivery testing |
| **Delivery Receipts** | Track message status: ✓ server received, ✓✓ client received |
| **WebSocket Commands** | Real-time communication with SimpleX CLI via WebSocket API |
| **Event Listener** | Background service for delivery confirmation events |
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
| **Redis Integration** | Architecture Ready | v0.2.0 |
| **InfluxDB Integration** | Configured | v0.2.0 |
| **Grafana Dashboards** | Docker ready | v0.2.0 |
| **WebSocket Live Updates** | Channels ready | v0.3.0 |

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
│   │   ┌─────────┐                                           │   │
│   │   │ Clients │  🆕 SimpleX CLI Test Clients              │   │
│   │   │   App   │  Docker + WebSocket + Delivery Tracking   │   │
│   │   └─────────┘  + AJAX Messaging (v0.1.8)                │   │
│   │                                                         │   │
│   │   ┌─────────────────────────────────────────────────┐   │   │
│   │   │              Core Module                        │   │   │
│   │   │   SimplexCLIManager  │  MetricsWriter          │   │   │
│   │   │   APScheduler        │  i18n System            │   │   │
│   │   │   AJAX Handlers      │  WebSocket Channels     │   │   │
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
│   │   ┌──────────┐  🆕 Prepared for stress testing         │   │
│   │   │  Redis   │    Real-time pub/sub, session storage   │   │
│   │   └──────────┘                                          │   │
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
| **Docker** | 24.x+ | For CLI Clients and InfluxDB/Grafana stack |

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

Docker is required for the SimpleX CLI Clients feature (NEW in v0.1.7).

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

### 4. Clone Repository
```bash
cd ~
git clone https://github.com/cannatoshi/simplex-smp-monitor.git
cd simplex-smp-monitor
```

---

### 5. Setup Python Environment
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

### 6. Initialize Database
```bash
# Run migrations
python manage.py migrate

# Create superuser (optional, for admin access)
python manage.py createsuperuser
```

---

### 7. Start the Server

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

### 8. Setup CLI Clients (NEW in v0.1.7)

The CLI Clients feature requires a custom Docker image. Follow these steps to set it up:

#### 8.1 Build the Docker Image

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

#### 8.2 Test the Image (Optional)

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

#### 8.3 Return to Project Root

```bash
cd ~/simplex-smp-monitor
```

---

### 9. Setup Event Listener Service (NEW in v0.1.7)

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

#### Option B: Systemd Service (Recommended for Production)

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

| Test Type | Purpose | Use Case |
|-----------|---------|----------|
| **Monitoring** | Connectivity & uptime checks | Regular health monitoring |
| **Stress** | Load testing with multiple connections | Capacity planning |
| **Latency** | Response time measurement | Performance optimization |

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
│              │   Django Application  │                          │
│              │   (WebSocket API)     │                          │
│              └───────────┬───────────┘                          │
│                          │                                      │
│                          ▼                                      │
│              ┌───────────────────────┐                          │
│              │   Event Listener      │                          │
│              │   (Delivery Receipts) │                          │
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
       │ 7. UI shows ✓✓ Delivered
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

### Step 9: Event Listener for Delivery Receipts

The **Event Listener** is required for ✓✓ (delivered) status updates.

**Check if it's running:**
```bash
sudo systemctl status simplex-events
```

**What it does:**
- Connects to all running clients via WebSocket
- Listens for `chatItemsStatusesUpdated` events
- Updates message status from ✓ to ✓✓ when recipient confirms
- Calculates and stores delivery latency

**Without the Event Listener:**
- Messages will show ✓ (sent) but never ✓✓ (delivered)
- Latency won't be calculated

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

| Stat | Description |
|------|-------------|
| **Status** | Running / Stopped / Created |
| **Sent** | Number of messages sent |
| **Received** | Number of messages received |
| **Success Rate** | Percentage of delivered messages |

### Capacity & Performance

Tested on **Raspberry Pi 5** (8GB RAM, 128GB NVMe, Debian 12):

| Clients | RAM Usage | Status |
|---------|-----------|--------|
| 6 | ~400 MB | ✅ Stable |
| 10 | ~650 MB | ✅ Stable |
| 20 | ~1.2 GB | ✅ Stable |
| 50 | ~3 GB | ⚠️ Tested |

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
# Check Event Listener
sudo systemctl status simplex-events

# View Event Listener logs
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
3. **Run Event Listener** as systemd service for production
4. **Monitor RAM usage** when adding many clients
5. **Delete unused clients** to free resources

---

## Client Detail Page - UI Features (NEW in v0.1.8)

The v0.1.8 release brings a **completely redesigned Client Detail page** with modern AJAX-based interactions, animated transitions, and a professional UI layout.

### 4-Corner Stats Cards Layout

The statistics section has been rebuilt with a new **4-card layout** (replacing the previous 5-card design). Each card uses a sophisticated **4-corners + center** information pattern:

```
┌─────────────────┬─────────────────┬─────────────────┬─────────────────┐
│     STATUS      │   MESSAGES      │  SUCCESS RATE   │     LATENCY     │
├─────────────────┼─────────────────┼─────────────────┼─────────────────┤
│ Port 3031    2h │ ✓4          ✗0  │ Today:4   Tot:4 │ ↓574ms   ↑802ms │
│                 │                 │                 │                 │
│   🟢 Running    │   4    │    2   │    100.0%       │     663ms       │
│     Status      │ ↑Send  │ ↓Recv  │   Success Rate  │    Ø Latency    │
│                 │                 │                 │                 │
│ 1 Conn.    tom  │ ⏳0    2min ago │ ████████ 100%   │ ▁▃▅▇▅▃▁  L.15   │
└─────────────────┴─────────────────┴─────────────────┴─────────────────┘
```

**Card Details:**

| Card | Top-Left | Top-Right | Center | Bottom-Left | Bottom-Right |
|------|----------|-----------|--------|-------------|--------------|
| **Status** | Port number | Uptime | Status LED + Text | Connection count | Profile name |
| **Messages** | ✓ Delivered | ✗ Failed | Sent \| Received split | ⏳ Pending | Last message time |
| **Success Rate** | Today count | Total count | Percentage (color-coded) | Progress bar | - |
| **Latency** | ↓ Min latency | ↑ Max latency | Ø Average latency | Sparkline | Trend label |

### AJAX Messaging System

Send messages **without page reload**:

1. Type your message in the textarea
2. Click "Send" button
3. Button shows loading spinner during operation
4. **Success:** Green feedback message, new message slides into table
5. **Error:** Red feedback message with error details

**Technical Implementation:**
```javascript
// Messages are sent via Fetch API with XMLHttpRequest header
const response = await fetch('/clients/messages/send/', {
    method: 'POST',
    headers: {
        'X-CSRFToken': csrfToken,
        'X-Requested-With': 'XMLHttpRequest'  // Identifies AJAX request
    },
    body: formData
});

// Server returns JSON for AJAX requests
const data = await response.json();
// { success: true, message_id: "...", content: "...", recipient: "...", status: "sent" }
```

**Features:**
- Instant success/error feedback
- Live stats counter update after send
- New messages appear with slide-in animation
- No page flicker or reload

### AJAX Connection Management

**Creating Connections:**
1. Click "New Connection" button
2. Select target client from dropdown panel
3. Click "Connect"
4. New connection slides into the list with animation
5. Panel closes automatically on success

**Deleting Connections:**
1. Click the red "✗" button on a connection
2. Confirm deletion
3. Connection slides out with animation and disappears

**Slide Animations:**
```css
@keyframes slide-in-right {
    from { opacity: 0; transform: translateX(30px); }
    to { opacity: 1; transform: translateX(0); }
}

@keyframes slide-out-right {
    from { opacity: 1; transform: translateX(0); }
    to { opacity: 0; transform: translateX(30px); }
}
```

### Smart Connection Button

The "New Connection" button intelligently adapts based on available connections:

| Condition | Display |
|-----------|---------|
| Client not running | Button hidden |
| Running + other clients available | "New Connection" button shown |
| Running + all possible connections exist | "(no more clients)" text shown |

**Implementation:**
```django
{% if client.is_running %}
    {% if other_running_clients %}
        <button>New Connection</button>
    {% else %}
        <span class="text-slate-400">(no more clients)</span>
    {% endif %}
{% endif %}
```

### Live SMP Server Status LEDs

Servers in the sidebar show **real-time status with animated LEDs**:

| Status | Color | Animation |
|--------|-------|-----------|
| `online` | 🟢 Emerald green | Pulsing ping effect |
| `offline` | 🔴 Red | Static |
| `error` | 🔴 Red | Static |
| `unknown` | ⚪ Gray | Static |

**Pulsing LED HTML:**
```html
<span class="relative flex h-2.5 w-2.5">
    <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
    <span class="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
</span>
```

### Equal Height Layout

The main content and sidebar now **always match heights** using CSS Grid + Flexbox:

**How it works:**
- CSS Grid with `align-items: stretch` makes both columns equal height
- Content column: Messages table has `flex-1` (grows to fill space)
- Sidebar column: SMP Server box has `flex-1` (grows to fill space)

**Behavior:**
- If **content is taller** → SMP Server box stretches to match
- If **sidebar is taller** → Messages table stretches to match
- Both have `min-h-[...]` to prevent collapsing when empty

### Uptime Display

Running clients now show formatted uptime:

| Duration | Display |
|----------|---------|
| < 1 minute | "45s" |
| 1-59 minutes | "12m" |
| 1-23 hours | "2h 15m" |
| 1+ days | "3d 5h" |

**Property Implementation:**
```python
@property
def uptime_display(self):
    if not self.started_at or self.status != 'running':
        return None
    delta = timezone.now() - self.started_at
    seconds = int(delta.total_seconds())
    
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        return f"{seconds // 60}m"
    elif seconds < 86400:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"
    else:
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        return f"{days}d {hours}h"
```

### Latency Statistics

Each client now tracks latency statistics from sent messages:

| Statistic | Description |
|-----------|-------------|
| **Min Latency** | Fastest message delivery time |
| **Max Latency** | Slowest message delivery time |
| **Avg Latency** | Average delivery time across all messages |
| **Sparkline** | Visual representation of last 15 messages (placeholder) |

**Model Properties:**
```python
@property
def avg_latency_ms(self):
    result = self.sent_messages.filter(
        total_latency_ms__isnull=False
    ).aggregate(avg=Avg('total_latency_ms'))
    return round(result['avg']) if result['avg'] else None

@property
def min_latency_ms(self):
    result = self.sent_messages.filter(
        total_latency_ms__isnull=False
    ).aggregate(min=Min('total_latency_ms'))
    return result['min']

@property
def max_latency_ms(self):
    result = self.sent_messages.filter(
        total_latency_ms__isnull=False
    ).aggregate(max=Max('total_latency_ms'))
    return result['max']
```

### Unified Button Styling

All action buttons now use consistent **cyan-blue** styling:

```html
<button class="px-3 py-1.5 bg-cyan-600 hover:bg-cyan-700 text-white rounded-lg text-sm font-medium transition-colors">
    Action
</button>
```

**Applied to:**
- Start/Stop/Restart buttons
- Send message button
- New connection button
- Edit/Delete buttons
- All form submit buttons

---

## Troubleshooting

### Common Issues (v0.1.8)

#### 404 Error on "Send Message"

**Symptom:** Clicking send returns 404 error or "Network Error"

**Cause:** URL routing order - `<slug:slug>/` was matching before specific routes like `messages/send/`

**Solution:** Update `clients/urls.py` - specific routes must come BEFORE generic slug routes:

```python
# CORRECT ORDER:
urlpatterns = [
    # Specific routes FIRST
    path('messages/send/', views.SendMessageView.as_view(), name='send_message'),
    path('connections/create/', views.ConnectionCreateView.as_view(), name='connection_create'),
    
    # Generic slug routes LAST
    path('<slug:slug>/', views.ClientDetailView.as_view(), name='detail'),
]
```

#### Message Stuck on ✓ (Never Shows ✓✓)

**Symptom:** Messages show "sent" status but never update to "delivered"

**Cause:** Event Listener not running

**Solution:**
```bash
# Check if Event Listener is running
sudo systemctl status simplex-events

# Start if not running
sudo systemctl start simplex-events

# Check logs for errors
sudo journalctl -u simplex-events -f
```

#### SMP Server LEDs Not Pulsing (All Gray/White)

**Symptom:** All server LEDs show gray instead of green for online servers

**Cause:** Template checking wrong field (`is_online` instead of `last_status`)

**Solution:** Ensure `_sidebar.html` uses correct field:
```django
{% if server.last_status == 'online' %}
    <!-- Pulsing green LED -->
{% elif server.last_status == 'offline' or server.last_status == 'error' %}
    <!-- Red LED -->
{% else %}
    <!-- Gray LED -->
{% endif %}
```

#### Sidebar and Content Different Heights

**Symptom:** Sidebar is shorter or longer than main content area

**Cause:** Missing CSS flex properties

**Solution:** Ensure these classes are present:
- Grid container: `style="align-items: stretch;"`
- Content column: `h-full flex flex-col`
- Messages box: `flex-1 min-h-[300px]`
- Sidebar container: `h-full`
- SMP Server box: `flex-1 min-h-[150px]`

#### Stats Not Updating After Sending Message

**Symptom:** Sent counter stays at old value after sending

**Cause:** AJAX response not updating DOM elements

**Solution:** Check that stats elements have correct IDs:
- `#stat-sent` - Sent message count
- `#stat-received` - Received message count
- `#stat-success-rate` - Success percentage

#### Client Won't Start

**Symptom:** Start button does nothing or shows error

**Causes & Solutions:**

1. **Docker not running:**
   ```bash
   sudo systemctl start docker
   ```

2. **Port already in use:**
   ```bash
   ss -tlnp | grep 3031
   # Kill conflicting process or change client port
   ```

3. **Docker image not built:**
   ```bash
   cd ~/simplex-smp-monitor/clients/docker
   docker build -t simplex-cli:latest -f Dockerfile.simplex-cli .
   ```

4. **Insufficient permissions:**
   ```bash
   sudo usermod -aG docker $USER
   # Log out and log back in
   ```

#### WebSocket Connection Failed

**Symptom:** "WebSocket connection failed" in browser console or logs

**Causes & Solutions:**

1. **Container not healthy:**
   ```bash
   docker logs simplex-client-client-001
   docker inspect simplex-client-client-001 | grep -A5 Health
   ```

2. **Port not exposed:**
   ```bash
   docker port simplex-client-client-001
   ```

3. **Firewall blocking:**
   ```bash
   sudo ufw allow 3031:3080/tcp
   ```

### Debug Mode

Enable Django debug mode for detailed error messages:

```python
# config/settings.py
DEBUG = True
```

Check browser console (F12 → Console tab) for JavaScript errors.

### Known Limitations (v0.1.8)

| Limitation | Workaround | Fix Target |
|------------|------------|------------|
| Latency sparkline shows placeholder | Displays static bars | v0.2.5 |
| Stats don't auto-refresh | Send message to trigger update | v0.2.0 |
| Uptime resets on app restart | Expected behavior | - |
| No bulk client operations | Create clients individually | v0.2.0 |

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
├── stresstests/            # Multi-type testing app
│   ├── models.py           # TestRun, TestResult, ServerStats
│   ├── views.py            # Test execution views
│   ├── scheduler.py        # APScheduler integration
│   └── urls.py
├── clients/                # SimpleX CLI Clients app
│   ├── models.py           # SimplexClient, ClientConnection, TestMessage
│   ├── views.py            # Client management, AJAX messaging views
│   ├── urls.py             # 🆕 Reordered for AJAX routes (v0.1.8)
│   ├── forms.py            # Client creation forms
│   ├── services/
│   │   ├── docker_manager.py    # Docker container lifecycle
│   │   └── simplex_commands.py  # WebSocket command service
│   ├── docker/
│   │   ├── Dockerfile.simplex-cli  # Container image
│   │   └── entrypoint.sh           # Container entrypoint
│   ├── management/
│   │   └── commands/
│   │       └── listen_events.py    # Delivery receipt listener
│   └── templates/
│       └── clients/
│           ├── detail.html         # 🆕 Redesigned with AJAX (v0.1.8)
│           └── partials/
│               ├── _stats.html     # 🆕 4-corner card layout (v0.1.8)
│               ├── _sidebar.html   # 🆕 SMP LEDs, equal height (v0.1.8)
│               └── _connections.html  # 🆕 Smart button, animations (v0.1.8)
├── events/                 # Event logging app
│   ├── models.py
│   └── views.py
├── templates/              # HTML templates
│   ├── base.html           # Base template with nav + i18n
│   ├── dashboard/
│   ├── servers/
│   ├── stresstests/
│   │   ├── list.html
│   │   ├── type_select.html
│   │   ├── detail_monitoring.html
│   │   ├── detail_stress.html
│   │   ├── detail_latency.html
│   │   └── ...
│   ├── clients/            # Client templates
│   │   ├── list.html       # Client overview with cards
│   │   ├── detail.html     # Client detail with messaging
│   │   ├── form.html       # Create/edit form
│   │   └── confirm_delete.html
│   └── events/
├── static/
│   └── js/
│       └── i18n/           # Translation files
│           ├── en.json     # English translations
│           └── de.json     # German translations
├── screenshots/            # Documentation images
├── docker-compose.yml      # InfluxDB + Grafana stack
├── telegraf.conf           # Telegraf configuration
├── requirements.txt        # Python dependencies
├── manage.py               # Django management script
├── LICENSE                 # AGPL-3.0 license
├── CHANGELOG.md            # Version history
├── ROADMAP.md              # Development roadmap
└── README.md               # This file
```

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Backend** | Django 5.x, Django Channels, APScheduler |
| **Frontend** | HTMX, Alpine.js, Tailwind CSS |
| **AJAX** | Fetch API, XMLHttpRequest pattern *(NEW in v0.1.8)* |
| **Animations** | CSS Keyframes (slide-in, slide-out, fade, ping) *(NEW in v0.1.8)* |
| **i18n** | Alpine.js $store with JSON language files |
| **Database** | SQLite (dev), PostgreSQL (prod) |
| **Time-Series** | InfluxDB 2.x |
| **Visualization** | Grafana |
| **Metrics Agent** | Telegraf |
| **ASGI Server** | Daphne |
| **Tor Proxy** | PySocks |
| **Containers** | Docker 24.x (for CLI Clients) |
| **WebSocket** | websockets (Python async library) |
| **Real-Time** | Django Channels (WebSocket), Redis (planned for v0.2.0) |

---

## Roadmap

### v0.2.0 - Test Panel & Mesh Connections
- [ ] Test Panel UI for bulk messaging scenarios
- [ ] Mesh connections (connect all clients with each other)
- [ ] Bulk client creation (create 10/20/50 clients at once)
- [ ] Redis integration for real-time updates
- [ ] Complete InfluxDB integration
- [ ] Grafana dashboard templates
- [ ] Automated test schedules

### v0.3.0 - Real-Time & i18n
- [ ] WebSocket live updates (stats auto-refresh)
- [ ] Real-time test progress
- [ ] Activate all 25 languages
- [ ] RTL support (Arabic, Hebrew)

### v0.4.0 - Automation
- [ ] Scheduled test runs
- [ ] Email/Webhook alerts
- [ ] Test result history
- [ ] Export results (CSV/JSON)

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

### v0.1.8-alpha (2025-12-27)

**🎨 UI/UX Overhaul:**
- 🆕 **4-Corner Stats Cards** - Redesigned statistics with corner-based information layout
- 🆕 **AJAX Messaging System** - Send messages without page reload, instant UI feedback
- 🆕 **AJAX Connection Management** - Create/delete connections with smooth slide animations
- 🆕 **Equal Height Layout** - Sidebar and content always match heights dynamically
- 🆕 **Live SMP Server LEDs** - Pulsing green indicators for online servers
- 🆕 **Smart Connection Button** - Shows "(no more clients)" when all connected
- 🆕 **Unified Cyan Buttons** - Consistent button styling throughout the UI

**🔧 Model Enhancements:**
- 🆕 **started_at Field** - Tracks when client was started (for uptime calculation)
- 🆕 **start() Method** - Sets status to running and records start time
- 🆕 **stop() Method** - Sets status to stopped
- 🆕 **set_error() Method** - Sets error status with message
- 🆕 **uptime_display Property** - Formatted uptime like "2h 15m" or "3d 5h"
- 🆕 **avg_latency_ms Property** - Average latency from sent messages
- 🆕 **min_latency_ms Property** - Minimum latency
- 🆕 **max_latency_ms Property** - Maximum latency
- 🆕 **messages_delivered Property** - Count of successfully delivered messages

**🐛 Critical Fixes:**
- **URL Routing Order** - Specific routes now come before generic slug routes (fixes 404 on message send)
- **SendMessageView AJAX** - Returns JsonResponse for AJAX requests instead of redirect
- **SMP Server LEDs** - Fixed field reference (uses `last_status` instead of `is_online`)

**🏗️ Infrastructure:**
- AJAX patterns ready for upcoming Test Panel
- WebSocket Channels integration for real-time broadcasts
- Architecture prepared for Redis integration
- CSS animations for professional UI transitions

**📁 Files Modified:**
- `clients/models.py` - New fields, properties, and methods
- `clients/views.py` - AJAX support for SendMessageView
- `clients/urls.py` - Route ordering fix
- `clients/templates/clients/detail.html` - Grid layout, AJAX handlers
- `clients/templates/clients/partials/_stats.html` - 4-corner card layout
- `clients/templates/clients/partials/_sidebar.html` - SMP LEDs, flex-grow
- `clients/templates/clients/partials/_connections.html` - Smart button, animations

**⚠️ Migration Required:**
```bash
python manage.py makemigrations clients
python manage.py migrate
```

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
