# SimpleX SMP Monitor

## Real-Time Server Monitoring & Stress Testing for SimpleX Infrastructure

[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL--3.0-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Python](https://img.shields.io/badge/Python-3.11+-3776ab.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.x-092E20.svg)](https://www.djangoproject.com/)
[![React](https://img.shields.io/badge/React-18.x-61DAFB.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.x-3178C6.svg)](https://www.typescriptlang.org/)
[![Status](https://img.shields.io/badge/Status-Alpha-orange.svg)](#status)
[![Tor](https://img.shields.io/badge/Tor-Supported-7D4698.svg)](https://www.torproject.org/)
[![Redis](https://img.shields.io/badge/Redis-7.x-DC382D.svg)](https://redis.io/)
[![Maintenance](https://img.shields.io/badge/Maintained-Actively-success.svg)](https://github.com/cannatoshi/simplex-smp-monitor/commits/main)
[![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-brightgreen.svg)](#contributing)
[![Legal](https://img.shields.io/badge/Legal-See%20LEGAL.md-lightgrey.svg)](LEGAL.md)

A web-based monitoring dashboard and stress testing suite for self-hosted SimpleX SMP/XFTP relay infrastructure. Built for operators who need visibility into their private messaging servers.

> **Version:** 0.1.9-alpha (29. December 2025)  
> **Status:** Active Development  
> **Tested on:** Debian 12, Ubuntu 24.04, Raspberry Pi OS (64-bit)  
> **Companion to:** [SimpleX Private Infrastructure Tutorial](https://github.com/cannatoshi/simplex-smp-xftp-via-tor-on-rpi-hardened)

### Dashboard
![Dashboard](screenshots/dashboard_beta.png)

*Real-time infrastructure overview with server stats, activity charts, latency metrics, and system diagnostics preview*

---

> ⚠️ **ALPHA SOFTWARE**
>
> This project is in active development. Core features work, but expect rough edges.
> Not recommended for production use without thorough testing.
> 
> ✅ **What works:** Server management, multi-type testing, Tor support, i18n system, CLI Clients with Delivery Receipts, Real-Time WebSocket Infrastructure, Redis Channel Layer, Auto-Start Event Bridge, **🆕 React SPA Frontend**  
> 🚧 **In progress:** Test Panel (React), Traffic Analysis Dashboard, Adversary View

---

## 🚀 What's New in v0.1.9 - React SPA Migration

This release transforms the frontend from Django Templates + HTMX + Alpine.js to a modern **React Single Page Application**:

```bash
# OLD WAY (v0.1.8) - Django Templates
http://localhost:8000/clients/  # Server-rendered HTML

# NEW WAY (v0.1.9) - React SPA + Django REST API
http://localhost:3001/clients/  # React SPA (Vite Dev Server)
http://localhost:8000/api/v1/   # Django REST API
```

| Component | Old (v0.1.8) | New (v0.1.9) |
|-----------|--------------|--------------|
| **Frontend** | Django Templates | React 18 SPA |
| **Interactivity** | HTMX + Alpine.js | React + TypeScript |
| **Styling** | Bootstrap/Custom | Tailwind CSS |
| **i18n** | Alpine.js $store | react-i18next |
| **Routing** | Django URLs | React Router v6 |
| **Build** | Django collectstatic | Vite 5.x |
| **API** | HTML responses | JSON REST API |

### New Frontend Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    REACT SPA (Port 3001)                        │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Pages              Components         Services           │  │
│  │  ├── Dashboard      ├── Layout        ├── API Client      │  │
│  │  ├── Servers        ├── ClientStats   ├── i18n            │  │
│  │  ├── ServerDetail   ├── ClientConn.   └── Storage         │  │
│  │  ├── ServerForm     ├── ClientSidebar                     │  │
│  │  ├── Clients        └── ClientMessages                    │  │
│  │  ├── ClientDetail                                         │  │
│  │  ├── ClientForm                                           │  │
│  │  └── Categories                                           │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
           │                                    │
    REST API (JSON)                    Vite Proxy (Dev)
           │                                    │
           ▼                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DJANGO REST BACKEND (Port 8000)              │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  /api/v1/clients/          SimplexClientViewSet           │  │
│  │  /api/v1/servers/          SMPServerViewSet               │  │
│  │  /api/v1/connections/      ClientConnectionViewSet        │  │
│  │  /api/v1/messages/         TestMessageViewSet (NEW!)      │  │
│  │  /api/v1/categories/       CategoryViewSet                │  │
│  │  /api/v1/dashboard/        DashboardAPIView               │  │
│  └───────────────────────────────────────────────────────────┘  │
│                              │                                  │
│              SimplexEventBridge (Auto-Start)                    │
│                              │                                  │
└─────────────────────────────────────────────────────────────────┘
```

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
9. [Setup Redis](#4-setup-redis)
10. [Clone Repository](#5-clone-repository)
11. [Setup Python Environment](#6-setup-python-environment)
12. [Setup React Frontend](#7-setup-react-frontend-new-in-v019)
13. [Initialize Database](#8-initialize-database)
14. [Start the Servers](#9-start-the-servers)
15. [Setup CLI Clients](#10-setup-cli-clients)

### Configuration
16. [Tor Configuration](#tor-configuration)
17. [Redis Configuration](#redis-configuration)
18. [Vite Proxy Configuration](#vite-proxy-configuration-new-in-v019)
19. [Environment Variables](#environment-variables)
20. [Monitoring Stack (Optional)](#monitoring-stack-optional)

### Usage
21. [Adding Servers](#adding-servers)
22. [Connection Testing](#connection-testing)
23. [Multi-Type Testing](#multi-type-testing)
24. [SimpleX CLI Clients - Complete Guide](#simplex-cli-clients---complete-guide)

### Development
25. [Project Structure](#project-structure)
26. [Tech Stack](#tech-stack)
27. [Roadmap](#roadmap)
28. [Troubleshooting](#troubleshooting)
29. [Contributing](#contributing)
30. [Related Projects](#related-projects)
31. [License](#license)
32. [Changelog](#changelog)

---

## About This Project

If you run your own SimpleX SMP/XFTP servers (especially via Tor hidden services), you need answers to questions like:

- **Are my servers reachable?** Test connectivity through Tor or clearnet
- **What's the latency?** Measure response times across your infrastructure  
- **Are messages being delivered?** Run stress tests to verify reliability
- **What's happening over time?** Historical metrics and visualizations
- **Do messages actually arrive at recipients?** Track delivery receipts end-to-end
- **Can I see updates in real-time?** WebSocket live updates without page refresh

This tool provides a **single dashboard** to monitor, test, and analyze your SimpleX relay infrastructure.

### Why This Tool?

| Problem                                          | Solution                                         |
|--------------------------------------------------|--------------------------------------------------|
| "Is my .onion server actually reachable?"        | One-click connectivity test via Tor              |
| "What's the latency to my servers?"              | Real-time latency measurement                    |
| "Are messages being delivered reliably?"         | Stress testing with delivery verification        |
| "I have 10 servers, hard to track"               | Central dashboard for all servers                |
| "I need historical data"                         | InfluxDB + Grafana integration                   |
| "Do messages reach the recipient?"               | CLI Clients with ✓/✓✓ delivery tracking         |
| "I want instant feedback without page reloads"   | Real-time WebSocket updates                      |
| "Managing the Event Listener is annoying"        | Auto-starts with Django                          |
| "I want a modern, responsive UI"                 | **React SPA with TypeScript** *(NEW in v0.1.9)*  |

---

## Features

### ✅ Implemented (v0.1.9-alpha)

#### 🆕 React SPA Frontend (NEW - Major Feature)

| Feature                     | Description                                                   |
|-----------------------------|---------------------------------------------------------------|
| **React 18 + TypeScript**   | Modern, type-safe frontend architecture                       |
| **Vite 5.x Build Tool**     | Fast HMR development, optimized production builds             |
| **Tailwind CSS**            | Utility-first styling with dark mode support                  |
| **React Router v6**         | Client-side routing with nested layouts                       |
| **react-i18next**           | Internationalization (DE/EN active, 25+ prepared)             |
| **Modular Components**      | Reusable UI components (ClientStats, ClientConnections, etc.) |
| **REST API Integration**    | Full Django REST Framework backend                            |

#### 🚀 Real-Time Infrastructure (v0.1.8)

| Feature                         | Description                                                           |
|---------------------------------|-----------------------------------------------------------------------|
| **🔴 Redis Channel Layer**     | Production-ready message broker for WebSocket communication           |
| **🌉 SimplexEventBridge**      | Auto-connects to all running containers, processes SimpleX events     |
| **📡 WebSocket Consumers**     | ClientUpdateConsumer + ClientDetailConsumer for live browser updates  |
| **⚡ Auto-Start Integration**  | Event Bridge starts automatically with Django                         |
| **🟢 Live Status Indicator**   | Green/red dot in navbar with connection status                        |

#### 🎨 UI/UX Features

| Feature                         | Description                                 |
|---------------------------------|---------------------------------------------|
| **Dark/Light Mode**             | Toggle with localStorage persistence        |
| **Responsive Design**           | Works on desktop, tablet, and mobile        |
| **Cyan Color Scheme**           | Modern cyan primary color throughout        |
| **Animated Status Indicators**  | Pulsing dots for running clients            |
| **4-Corner Stats Cards**        | Redesigned statistics layout                |
| **AJAX Messaging**              | Send messages without page reload           |
| **AJAX Connections**            | Create/delete connections with animations   |

#### 🐳 CLI Clients & Core Features

| Feature                     | Description                                                                  |
|-----------------------------|------------------------------------------------------------------------------|
| **SimpleX CLI Clients**     | Docker-based test clients for end-to-end message delivery testing            |
| **Delivery Receipts**       | Track message status: ✓ server received, ✓✓ client received                 |
| **WebSocket Commands**      | Real-time communication with SimpleX CLI via WebSocket API                   |
| **Message Statistics**      | Per-client sent/received counters with success rates                         |
| **Multi-Type Test System**  | Monitoring, Stress, and Latency tests with dedicated workflows               |
| **APScheduler Integration** | Automated test execution with configurable intervals                         |
| **Server Management**       | Add, edit, delete SMP/XFTP servers with full CRUD                            |
| **7-Tab Configuration**     | Basic, Monitoring, SSH, Control Port, Telegraf, SimpleX Config, Statistics   |
| **Connection Testing**      | Real-time connectivity tests with latency measurement                        |
| **Tor Integration**         | Automatic .onion detection, tests via SOCKS5 proxy                           |
| **Category System**         | Organize servers with colored category labels                                |

### 🚧 In Progress

| Feature | Status | Target |
|---------|--------|--------|
| **Test Panel (React)** | UI Design | v0.2.0 |
| **Events Page (React)** | Planned | v0.2.0 |
| **WebSocket in React** | Architecture Ready | v0.2.0 |
| **Traffic Analysis Dashboard** | Planned | v0.2.5 |
| **Adversary View** | Planned | v0.3.0 |

### 📋 Planned

| Feature | Description |
|---------|-------------|
| **25 Language Support** | Full i18n for AR, ZH, JA, KO, RU, and 20 more |
| **Alerting** | Email/Webhook notifications on failures |
| **Multi-Node Support** | Monitor servers across multiple hosts |
| **Docker Deployment** | One-command setup |

---

## Screenshots

### Server List
![Server List](screenshots/servers_list.png)

*Server management grid with status indicators, latency metrics, categories, and quick actions*

### Client List
![Client List](screenshots/client_list.png)

*Docker-based CLI client overview with real-time status, message statistics, Tor badges, and container controls*

### Client Detail
![Client Detail](screenshots/client_detail.png)

*Client management dashboard with WebSocket messaging, connection handling, delivery tracking, and SMP server status*

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    REACT SPA (Browser - Port 3001)                      │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  React 18 + TypeScript + Tailwind CSS                            │   │
│  │  - Dashboard, Servers, Clients, Categories pages                 │   │
│  │  - react-i18next for translations                                │   │
│  │  - React Router v6 for navigation                                │   │
│  │  - Centralized API client (src/api/client.ts)                    │   │
│  └──────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                    Vite Proxy │ /api/* → :8000
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    DJANGO REST BACKEND (Port 8000)                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   ┌──────────────────────────────────────────────────────────────────┐  │
│   │  REST API Endpoints (/api/v1/)                                   │  │
│   │  - /clients/          SimplexClientViewSet                       │  │
│   │  - /servers/          SMPServerViewSet                           │  │
│   │  - /connections/      ClientConnectionViewSet                    │  │
│   │  - /messages/         TestMessageViewSet (NEW in v0.1.9)         │  │
│   │  - /categories/       CategoryViewSet                            │  │
│   │  - /dashboard/        DashboardAPIView                           │  │
│   └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│   ┌──────────────────────────────────────────────────────────────────┐  │
│   │  HTMX Action Views (Legacy, CSRF-Exempt for React)               │  │
│   │  - /clients/{slug}/connect/     ClientConnectView                │  │
│   │  - /clients/{slug}/start/       ClientStartView                  │  │
│   │  - /clients/{slug}/stop/        ClientStopView                   │  │
│   │  - /clients/messages/send/      SendMessageView                  │  │
│   │  - /clients/connections/{id}/delete/  ConnectionDeleteView       │  │
│   └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│   ┌──────────────────────────────────────────────────────────────────┐  │
│   │  SimplexEventBridge (Auto-Start with Django)                     │  │
│   │  - Connects to ALL running SimpleX containers                    │  │
│   │  - Processes: newChatItems, chatItemsStatusesUpdated             │  │
│   │  - Updates database, broadcasts to browsers via WebSocket        │  │
│   └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
            │                                              │
            │ WebSocket :3031-3080                         │ Pub/Sub
            ▼                                              ▼
┌─────────────────────────┐                    ┌─────────────────────────┐
│  SimpleX CLI Containers │                    │  Redis (Port 6379)      │
│  - Client 001 (:3031)   │                    │  - Channel Layer        │
│  - Client 002 (:3032)   │                    │  - Message Broker       │
│  - Client 003 (:3033)   │                    └─────────────────────────┘
│  - ...                  │
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

| Requirement | Version | Notes                                     |
|-------------|---------|-------------------------------------------|
| **Python**  | 3.11+   | With pip and venv                         |
| **Node.js** | 18+     | **NEW in v0.1.9** - For React frontend    |
| **npm**     | 9+      | **NEW in v0.1.9** - Package manager       |
| **Tor**     | Latest  | For .onion server testing                 |
| **Git**     | Any     | For cloning repository                    |
| **Docker**  | 24.x+   | For CLI Clients, Redis, InfluxDB/Grafana  |
| **Redis**   | 7.x     | For real-time WebSocket communication     |

---

## Installation

### 1. Install System Dependencies

**Debian/Ubuntu:**
```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git curl

# NEW in v0.1.9: Install Node.js 18+
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
```

**Verify Node.js installation:**
```bash
node --version   # Should be v18.x or higher
npm --version    # Should be v9.x or higher
```

**Raspberry Pi OS:**
```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git curl

# Install Node.js via NodeSource
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
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

### 4. Setup Redis

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

| Feature          | InMemoryChannelLayer  | Redis        |
|------------------|-----------------------|--------------|
| Multi-process    | ❌ No                 | ✅ Yes      |
| Production-ready | ⚠️ Dev only           | ✅ Yes      |
| 50+ Clients      | ❓ Maybe              | ✅ Stable   |
| Persistence      | ❌ No                 | ✅ Optional |

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

### 7. Setup React Frontend (NEW in v0.1.9)

```bash
# Navigate to frontend directory
cd frontend

# Install Node.js dependencies
npm install

# Return to project root
cd ..
```

**Frontend dependencies installed:**
- React 18
- TypeScript 5.x
- Vite 5.x
- Tailwind CSS 3.x
- React Router v6
- react-i18next
- Lucide React (icons)

---

### 8. Initialize Database

```bash
# Run migrations
python manage.py migrate

# Create superuser (optional, for admin access)
python manage.py createsuperuser
```

---

### 9. Start the Servers

**You now need TWO terminals:**

**Terminal 1: Django Backend (REST API)**
```bash
cd ~/simplex-smp-monitor
source .venv/bin/activate
python manage.py runserver 0.0.0.0:8000
```

**Terminal 2: Vite Dev Server (React Frontend)**
```bash
cd ~/simplex-smp-monitor/frontend
npm run dev
```

**You should see:**

**Terminal 1 (Django):**
```
🚀 APScheduler gestartet - prüft alle 30 Sekunden
✅ APScheduler gestartet - Monitoring läuft!
INFO 🌉 Event Bridge thread started
INFO 🚀 SimplexEventBridge starting...
Starting ASGI/Daphne version 4.2.1 development server at http://0.0.0.0:8000/
```

**Terminal 2 (Vite):**
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:3001/
  ➜  Network: http://192.168.1.146:3001/
  ➜  press h + enter to show help
```

**Access the application:**

| Interface | URL | Description |
|-----------|-----|-------------|
| **React App** | http://YOUR_IP:3001 | Main application (NEW!) |
| **Django Admin** | http://YOUR_IP:8000/admin/ | Admin interface |
| **REST API** | http://YOUR_IP:8000/api/v1/ | API endpoints |
| **Legacy HTMX** | http://YOUR_IP:8000/clients/ | Old Django templates |

---

### 10. Setup CLI Clients

The CLI Clients feature requires a custom Docker image. Follow these steps to set it up:

#### 10.1 Build the Docker Image

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

#### 10.2 Test the Image (Optional)

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

#### 10.3 Return to Project Root

```bash
cd ~/simplex-smp-monitor
```

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

## Redis Configuration

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

## Vite Proxy Configuration (NEW in v0.1.9)

The React frontend uses Vite's proxy to forward API requests to Django.

**File:** `frontend/vite.config.ts`

```typescript
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3001,
    host: true,
    proxy: {
      // REST API
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      // HTMX Action Endpoints (specific paths only!)
      '/clients/messages/send/': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/clients/connections/': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      // Dynamic paths for client actions
      '^/clients/[a-z0-9-]+/connect/$': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '^/clients/[a-z0-9-]+/start/$': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '^/clients/[a-z0-9-]+/stop/$': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '^/clients/[a-z0-9-]+/restart/$': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      // WebSocket
      '/ws': {
        target: 'ws://localhost:8000',
        ws: true,
      },
    },
  },
})
```

> **Important:** Do NOT proxy all `/clients/*` requests - this would break React Router!

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

# Redis
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

| Service       | URL                   | Credentials      |
|---------------|-----------------------|------------------|
| **Grafana**   | http://localhost:3000 | admin / admin    |
| **InfluxDB**  | http://localhost:8086 | Set on first run |

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
│              │                       │    Django!               │
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

1. Open your browser and go to `http://YOUR_IP:3001` (React App)
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

1. On **Client 001** detail page, find **Send Message** form (in sidebar)
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

**Tab 1: Sent (Outgoing Messages)**

Shows all messages YOU sent to other clients:
- Time, Recipient, Message content, Delivery status, Latency

**Tab 2: Received (Incoming Messages)**

Shows all messages you RECEIVED from other clients:
- Time, Sender, Message content, Status

**Tab 3: All (Combined View)**

Shows both sent and received messages in chronological order:
- Direction indicator (OUT/IN), Contact name, Message, Status, Latency

**Message Status Progression:**
```
[pending]   →   [sent]   →   [delivered]
    ⏳            ✓             ✓✓

- pending:   Message is being sent (hourglass icon)
- sent:      SMP server received the message (single checkmark)
- delivered: Recipient client received the message (double checkmark)
- failed:    Message delivery failed (X icon)
```

**Example Flow:**
```
You send "Hello!" to rosa
  → Status: pending (sending...)
  → Status: sent (server got it)
  → Status: delivered (rosa received it)
  → Latency: 1,234ms (time from sent to delivered)
```

### Step 9: Managing Clients

#### Start/Stop/Restart

- **Stop**: Stops the container but keeps data volume
- **Restart**: Stops and starts the container
- **Start**: Starts a stopped container

#### Delete a Client

1. Click **Delete** button (red)
2. Confirm deletion
3. Both the database entry AND Docker container are removed

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
# Check if Event Bridge is running
# Look for "📡 Listening:" in Django console
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
3. **Check Redis is running** for real-time updates
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
│   ├── api/                    # REST API endpoints
│   │   ├── views.py
│   │   └── urls.py
│   └── urls.py
├── servers/                    # Server management app
│   ├── models.py               # Server & Category models
│   ├── views.py                # CRUD + testing views
│   ├── api/                    # REST API endpoints
│   │   ├── views.py
│   │   ├── serializers.py
│   │   └── urls.py
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
│   ├── views.py                # Client management views (HTMX)
│   ├── urls.py
│   ├── forms.py                # Client creation forms
│   ├── consumers.py            # WebSocket Consumers
│   ├── routing.py              # WebSocket URLs
│   ├── apps.py                 # Auto-start Event Bridge
│   ├── api/                    # 🆕 REST API endpoints (v0.1.9)
│   │   ├── views.py            # SimplexClientViewSet, TestMessageViewSet
│   │   ├── serializers.py
│   │   └── urls.py
│   ├── services/
│   │   ├── docker_manager.py   # Docker container lifecycle
│   │   ├── simplex_commands.py # WebSocket command service
│   │   ├── event_bridge.py     # SimplexEventBridge
│   │   └── websocket_pool.py   # WebSocket connection pooling
│   ├── docker/
│   │   ├── Dockerfile.simplex-cli
│   │   └── entrypoint.sh
│   ├── management/commands/
│   │   ├── listen_events.py    # Event listener (deprecated)
│   │   └── clients.py          # Client management commands
│   └── templates/clients/      # Legacy Django templates
│       ├── list.html
│       ├── detail.html
│       └── ...
├── events/                     # Event logging app
│   ├── models.py
│   ├── views.py
│   └── urls.py
├── frontend/                   # 🆕 React SPA (NEW in v0.1.9)
│   ├── src/
│   │   ├── api/
│   │   │   └── client.ts       # Centralized API client
│   │   ├── components/
│   │   │   ├── layout/
│   │   │   │   └── Layout.tsx  # Header, Nav, Dark Mode, i18n
│   │   │   └── clients/
│   │   │       ├── ClientStats.tsx
│   │   │       ├── ClientConnections.tsx
│   │   │       ├── ClientSidebar.tsx
│   │   │       └── ClientMessages.tsx
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Servers.tsx
│   │   │   ├── ServerDetail.tsx
│   │   │   ├── ServerForm.tsx
│   │   │   ├── Clients.tsx
│   │   │   ├── ClientDetail.tsx
│   │   │   ├── ClientForm.tsx
│   │   │   ├── Categories.tsx
│   │   │   ├── Tests.tsx
│   │   │   └── Events.tsx
│   │   ├── i18n/
│   │   │   ├── index.ts
│   │   │   └── locales/
│   │   │       ├── de.json
│   │   │       └── en.json
│   │   ├── App.tsx             # React Router configuration
│   │   └── main.tsx
│   ├── vite.config.ts          # Vite + Proxy configuration
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   └── package.json
├── templates/                  # Legacy global Django templates
│   ├── base.html
│   ├── dashboard/
│   ├── servers/
│   ├── stresstests/
│   └── events/
├── static/
│   ├── css/
│   │   └── app.css
│   └── js/
│       ├── clients-live.js     # Frontend WebSocket client (legacy)
│       ├── i18n.js             # Translation system (legacy)
│       └── lang/               # Language files (legacy)
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

| Layer              | Technology                                   |
|--------------------|----------------------------------------------|
| **Frontend**       | **React 18 + TypeScript** *(NEW in v0.1.9)*  |
| **Build Tool**     | **Vite 5.x** *(NEW in v0.1.9)*               |
| **Styling**        | **Tailwind CSS 3.x** *(NEW in v0.1.9)*       |
| **Routing**        | **React Router v6** *(NEW in v0.1.9)*        |
| **i18n**           | **react-i18next** *(NEW in v0.1.9)*          |
| **Icons**          | **Lucide React** *(NEW in v0.1.9)*           |
| **Backend**        | Django 5.x, Django REST Framework            |
| **Real-Time**      | Django Channels, Redis 7.x, WebSockets       |
| **Database**       | SQLite (dev), PostgreSQL (prod)              |
| **Time-Series**    | InfluxDB 2.x                                 |
| **Visualization**  | Grafana                                      |
| **Metrics Agent**  | Telegraf                                     |
| **ASGI Server**    | Daphne                                       |
| **Tor Proxy**      | PySocks                                      |
| **Containers**     | Docker 24.x (CLI Clients + Redis)            |
| **Scheduler**      | APScheduler                                  |

### Legacy (Still Available)

| Layer        | Technology                          | Status     |
|--------------|-------------------------------------|------------|
| **Frontend** | Django Templates + HTMX + Alpine.js | Deprecated |
| **i18n**     | Alpine.js $store with JSON files    | Deprecated |

> **Note:** The legacy Django templates are still accessible at `http://localhost:8000/` but are no longer actively developed.

---

## Roadmap

### ✅ v0.1.9 - React SPA Migration (COMPLETED)
- [x] React 18 + TypeScript setup with Vite
- [x] Tailwind CSS styling
- [x] react-i18next (DE/EN)
- [x] Dashboard page migration
- [x] Servers page migration (List, Detail, Form)
- [x] Clients page migration (List, Detail, Form)
- [x] Categories page migration
- [x] REST API for all entities
- [x] TestMessageViewSet for messages API
- [x] Dark/Light mode toggle
- [x] Modular component architecture

### v0.2.0 - Complete React Migration
- [ ] Tests page (React)
- [ ] Events page (React)
- [ ] WebSocket integration in React
- [ ] Real-time updates without page refresh
- [ ] Remove legacy Django templates

### v0.2.5 - Traffic Analysis Dashboard
- [ ] Live traffic monitoring
- [ ] Message timeline visualization
- [ ] Activity heatmap
- [ ] Latency distribution charts
- [ ] Packet size analysis

### v0.3.0 - Adversary View (Security Audit)
- [ ] Timing correlation analysis
- [ ] Metadata exposure reports
- [ ] Pattern detection engine
- [ ] Security recommendations
- [ ] Risk assessment scoring

### v0.4.0 - Production Ready
- [ ] PostgreSQL support
- [ ] Docker Compose deployment
- [ ] Kubernetes manifests
- [ ] Security hardening
- [ ] API documentation

### Future
- [ ] 25 language support
- [ ] Multi-node monitoring
- [ ] Alerting (Email/Webhook)
- [ ] Mobile app

---

## Troubleshooting

### React App Not Loading

```bash
# Check if Vite is running
cd ~/simplex-smp-monitor/frontend
npm run dev

# Check for build errors
npm run build
```

### API Requests Failing (CORS/404)

```bash
# Ensure Django is running
python manage.py runserver 0.0.0.0:8000

# Check Vite proxy configuration
cat frontend/vite.config.ts
```

### CSRF Errors on POST Requests

The React frontend sends AJAX requests to HTMX views. These views need `@csrf_exempt`:

```python
# clients/views.py
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

@method_decorator(csrf_exempt, name="dispatch")
class ClientConnectView(View):
    ...
```

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

### Messages Stuck on ✓ (not ✓✓)

Check Event Bridge is connected:
```bash
# Look for "📡 Listening:" messages in Django console
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

### TypeScript Build Errors

```bash
cd ~/simplex-smp-monitor/frontend
npm run build

# Common fixes:
# - Check interface types match API responses
# - Ensure all imports are correct
# - Check for missing dependencies
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

### Priority Areas for Contribution

| Area                  | Difficulty       | Impact    |
|-----------------------|------------------|-----------|
| Tests Page (React)    | Medium           | High      |
| Events Page (React)   | Medium           | High      |
| WebSocket React Hooks | Medium           | High      |
| Traffic Visualization | Hard             | Very High |
| Adversary View        | Hard             | Very High |
| Documentation         | Easy             | High      |

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

> **Note:** This project is **not affiliated with or endorsed by SimpleX Chat Ltd**.  
> "SimpleX" is a trademark of SimpleX Chat Ltd. See [TRADEMARK.md](TRADEMARK.md) for details.

For complete legal information, see:
- [LEGAL.md](LEGAL.md) - Legal documentation overview
- [TRADEMARK.md](TRADEMARK.md) - Trademark information
- [DISCLAIMER.md](DISCLAIMER.md) - Full liability disclaimer
- [TESTING_POLICY.md](TESTING_POLICY.md) - Testing guidelines

---

## Changelog

### v0.1.9-alpha (2025-12-29)

**🆕 MAJOR FEATURE: React SPA Migration**

The frontend is completely rebuilt using React 18 + TypeScript:

- **React 18 + TypeScript** - Modern, type-safe frontend
- **Vite 5.x** - Fast build tool with HMR
- **Tailwind CSS** - Utility-first styling with dark mode
- **React Router v6** - Client-side routing
- **react-i18next** - Internationalization (DE/EN active)
- **Modular Components** - ClientStats, ClientConnections, ClientSidebar, ClientMessages

**New REST API Endpoints:**
- `GET /api/v1/messages/` - TestMessageViewSet for message history
- `GET /api/v1/messages/?client={uuid}` - Filter by client
- `GET /api/v1/messages/?direction=sent|received` - Filter by direction

**Migrated Pages:**
- ✅ Dashboard
- ✅ Servers (List, Detail, Form)
- ✅ Clients (List, Detail, Form)
- ✅ Categories

**Technical Changes:**
- CSRF-Exempt decorators for HTMX views (React compatibility)
- Vite proxy configuration for API routing
- TypeScript interfaces for all API types
- UUID-based client IDs (strings, not integers)
- Paginated API response handling

**New Dependencies (Frontend):**
```json
{
  "react": "^18.x",
  "react-dom": "^18.x",
  "react-router-dom": "^6.x",
  "react-i18next": "^14.x",
  "i18next": "^23.x",
  "lucide-react": "^0.x",
  "vite": "^5.x",
  "typescript": "^5.x",
  "tailwindcss": "^3.x"
}
```

**Upgrade from v0.1.8:**
```bash
# Install Node.js 18+ if not already installed
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Install frontend dependencies
cd ~/simplex-smp-monitor/frontend
npm install

# Start both servers
# Terminal 1: python manage.py runserver 0.0.0.0:8000
# Terminal 2: npm run dev (in frontend/)
```

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

### v0.1.6-alpha (2025-12-26)

**Added:**
- Multi-type test framework (Monitoring, Stress, Latency) with dedicated workflows
- APScheduler integration for automated test execution
- Professional i18n system with Alpine.js `$store.i18n`
- JSON language files (`static/js/i18n/en.json`, `de.json`)
- EN/DE translations active, 25 languages prepared for future activation
- `timeAgo()` function for relative time display
- Live countdown timer with real-time Alpine.js updates
- Onion/ClearNet badges in test results table
- Dynamic Grafana IP detection
- Language switcher in navigation header

### v0.1.5-alpha (2025-12-25)

**Added:**
- 7-Tab server configuration form
- Extended server model with SSH, Control Port, Telegraf, SLA fields
- Test result persistence
- Card quick test button (⚡)
- Category system with colored labels
- Template tags for fingerprint/password extraction

### v0.1.4-alpha (2025-12-24)

**Added:**
- Professional UI redesign with Dark/Light mode
- Bilingual support (English/German)
- Server connection testing with Tor SOCKS5 support
- Automatic .onion address detection
- ONION badge for Tor hidden services

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