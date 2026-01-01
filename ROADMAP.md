# SimpleX SMP Monitor - Roadmap v3.1 for 2025/2026

## 🎯 Vision

**SimpleX SMP Monitor** is the world's first comprehensive security testing, infrastructure validation, and **enterprise-grade monitoring platform** for SimpleX messaging infrastructure. It enables infrastructure operators—journalists, whistleblowers, NGOs, security researchers—to test, monitor, and secure their SimpleX deployments with capabilities rivaling commercial enterprise solutions like Palantir.

### What Makes This Tool Unique

| Feature | Other Tools | SimpleX SMP Monitor |
|---------|-------------|---------------------|
| Server Health Checks | ✅ Basic | ✅ Advanced with Tor |
| Message Delivery Testing | ❌ None | ✅ Full E2E with Receipts |
| Timing Correlation Analysis | ❌ None | ✅ **World's First** |
| Adversary View Simulation | ❌ None | ✅ **World's First** |
| Metadata Exposure Reports | ❌ None | ✅ **World's First** |
| Traffic Pattern Detection | ❌ None | ✅ Built-in |
| Security Recommendations | ❌ None | ✅ Actionable Insights |
| Private Tor Network Simulation | ❌ None | ✅ **World's First** |
| Enterprise Graph Visualization | ❌ None | ✅ Palantir-Style |
| Multi-Network Support (Tor + Lokinet) | ❌ None | ✅ **Planned** |
| Deep Packet Inspection | ❌ None | ✅ Zeek + Suricata |
| Docker One-Click Deployment | ❌ None | ✅ **NEW in v0.1.10** |
| Pre-Built SimpleX Server Images | ❌ None | ✅ **NEW in v0.1.10** |

### The Core Insight

> "Your security is only as good as your weakest link. But how do you know what an adversary can see?"

This tool answers that question by providing **Adversary View Mode**—a simulation environment where you can see exactly what metadata and patterns are exposed, even when message content remains encrypted.

---

## 📊 Roadmap Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SIMPLEX SMP MONITOR ROADMAP v3.1                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  PHASE 1: Foundation ✅                          PHASE 2: React Revolution  │
│  ══════════════════════                          ══════════════════════════ │
│  ✅ Django Backend                               ✅ Vite + React 18        │
│  ✅ Docker Client Management                     ✅ TypeScript + Tailwind  │
│  ✅ WebSocket Real-time                          ✅ i18n (DE/EN)           │
│  ✅ Tor Hidden Service Support                   🔄 WebSocket Hooks        │
│  ✅ Docker One-Click Deployment 🆕                                         │
│                                                                             │
│  PHASE 3: Traffic Analysis        PHASE 4: Adversary View                   │
│  ═════════════════════════        ═══════════════════════                   │
│  📋 Live Traffic Monitor          📋 Timing Correlation                    │
│  📋 Message Timeline              📋 Pattern Detection                     │
│  📋 Latency Distribution          📋 Security Scoring                      │
│  📋 Activity Heatmap              📋 Recommendations                       │
│                                                                             │
│  PHASE 5: Test Panel              PHASE 6: Monitoring                       │
│  ═══════════════════              ═══════════════════                       │
│  📋 Stress Tests                  📋 Grafana Integration                   │
│  📋 Reliability Tests             📋 InfluxDB Time-Series                  │
│  📋 Mesh Connections              📋 Alerting                              │
│                                                                             │
│  PHASE 7: Enterprise              PHASE 8: Lab Environment 🔄               │
│  ═══════════════════              ═══════════════════════════               │
│  📋 Multi-User                    ✅ Docker SMP Server Images 🆕           │
│  📋 REST API Auth                 ✅ Docker XFTP Server Images 🆕          │
│  📋 Production Deploy             ✅ Docker NTF Server Images 🆕           │
│                                   📋 Full Packet Capture                    │
│                                                                             │
│  PHASE 9: Private Tor 🆕          PHASE 10: Enterprise Stack 🆕            │
│  ═══════════════════════          ═════════════════════════════             │
│  📋 Chutney Integration           📋 Zeek Protocol Analysis                │
│  📋 Directory Authorities         📋 Suricata IDS/IPS                      │
│  📋 3 Test Modi                   📋 Neo4j + Cytoscape.js                  │
│                                                                             │
│  PHASE 11: Multi-Network 🆕                                                 │
│  ═══════════════════════════                                                │
│  📋 Lokinet Support (.loki)                                                 │
│  📋 Dual-Stack Servers                                                      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## ✅ Phase 1: Foundation (COMPLETED)

### 1.1-1.6: Initial Development ✅
*Completed in v0.1.0 through v0.1.8*

- Django backend with async support
- Server management with Tor/.onion support
- CLI client management via Docker containers
- WebSocket command interface
- Delivery receipt tracking
- Real-time event infrastructure (Redis + EventBridge)
- Basic web UI with Django templates

### 1.7: Docker One-Click Deployment ✅ (NEW in v0.1.10)
*Completed in v0.1.10*

- **Docker Compose Stack** - Complete application deployment in one command
- **Cross-Platform** - Works on Windows 11, Linux, Mac
- **Three Installation Methods**:
  - Clone & Run (`git clone` + `docker compose up -d`)
  - Download Pre-Built Images (wget from GitHub Releases)
  - Pull from GHCR (GitHub Container Registry)
- **Production Compose** - `docker-compose.prod.yml` for standalone deployment
- **CRLF Fix** - Windows line ending compatibility via `.gitattributes`
- **Nginx Reverse Proxy** - Simplified production architecture
- **Whitenoise Integration** - Django serves React SPA directly

**Stack (v0.1.10):**
```
Frontend: React 18 + TypeScript + Tailwind CSS (Vite 5.x)
Backend:  Django + Channels + Redis + PostgreSQL
Clients:  Docker containers (simplex-chat CLI)
Network:  Tor hidden services (.onion)
Deploy:   Docker Compose (one-click)
```

---

## 🔄 Phase 2: React Revolution (v0.1.9 - v0.2.0) - IN PROGRESS

### The Big Shift: From Django Templates to React SPA

This phase transforms the application from a traditional server-rendered Django application into a modern **Single Page Application (SPA)** with React frontend and Django REST API backend.

### 2.1 Architecture Transformation

**OLD Architecture (v0.1.8):**
```
┌─────────────────────────────────────────────────────────────────┐
│                         BROWSER                                 │
│  Django Templates (HTML) + Vanilla JavaScript                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                    HTTP (Full page loads)
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DJANGO SERVER                                │
│  Views render HTML templates                                    │
│  WebSocket for live updates                                     │
└─────────────────────────────────────────────────────────────────┘
```

**NEW Architecture (v0.2.0):**
```
┌─────────────────────────────────────────────────────────────────┐
│                    REACT SPA (Browser)                          │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Components        State           Services               │  │
│  │  ├── Layout        ├── useState    ├── API Client         │  │
│  │  ├── ClientStats   ├── useEffect   ├── WebSocket Hook     │  │
│  │  ├── ClientConn.   ├── Zustand     ├── i18n               │  │
│  │  ├── TestPanel     └── React Query └── Storage            │  │
│  │  └── TrafficView                                          │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
           │                                    │
    REST API (JSON)                    WebSocket (Real-time)
           │                                    │
           ▼                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DJANGO REST BACKEND                          │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Django REST Framework    Django Channels                 │  │
│  │  ├── /api/v1/servers/     ├── /ws/clients/                │  │
│  │  ├── /api/v1/clients/     ├── /ws/traffic/                │  │
│  │  ├── /api/v1/messages/    └── /ws/adversary/              │  │
│  │  ├── /api/v1/connections/                                 │  │
│  │  └── /api/v1/categories/                                  │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
           │                                    │
           ▼                                    ▼
┌─────────────────────┐              ┌─────────────────────┐
│  Docker Containers  │              │  Redis              │
│  (SimpleX CLI)      │              │  (Channel Layer)    │
└─────────────────────┘              └─────────────────────┘
```

### 2.2 Technology Stack
- [x] **Vite** - Fast build tool
- [x] **React 18** - Latest React with concurrent features
- [x] **TypeScript** - Type safety throughout
- [x] **Tailwind CSS** - Utility-first styling (Neon Blue #88CED0, Cyan #22D3EE)
- [x] **React Router v6** - Client-side routing
- [x] **react-i18next** - Internationalization (DE/EN active)
- [x] **Lucide React** - Icon library
- [ ] **Zustand** - Lightweight state management
- [ ] **React Query** - Server state & caching
- [ ] **Recharts** - Charts and visualizations

### 2.3 Project Structure
```
frontend/
├── src/
│   ├── api/
│   │   └── client.ts              # ✅ Centralized API client
│   ├── components/
│   │   ├── layout/
│   │   │   └── Layout.tsx         # ✅ Header, Nav, Dark Mode, i18n
│   │   └── clients/
│   │       ├── ClientStats.tsx    # ✅ 4 Statistics cards
│   │       ├── ClientConnections.tsx  # ✅ Connection management
│   │       ├── ClientSidebar.tsx  # ✅ Actions & Send Message
│   │       └── ClientMessages.tsx # ✅ Sent/Received/All tabs
│   ├── hooks/
│   │   ├── useWebSocket.ts        # ❌ Planned
│   │   ├── useClients.ts          # ❌ Planned
│   │   └── useTraffic.ts          # ❌ Planned
│   ├── pages/
│   │   ├── Dashboard.tsx          # ✅ Migrated
│   │   ├── Servers.tsx            # ✅ Migrated
│   │   ├── ServerDetail.tsx       # ✅ Migrated
│   │   ├── Clients.tsx            # ✅ Migrated
│   │   ├── ClientDetail.tsx       # ✅ Migrated
│   │   ├── Categories.tsx         # ✅ Migrated
│   │   ├── Tests.tsx              # ⚠️ Placeholder
│   │   └── Events.tsx             # ⚠️ Placeholder
│   ├── i18n/
│   │   └── locales/
│   │       ├── de.json            # ✅ German translations
│   │       └── en.json            # ✅ English translations
│   └── App.tsx                    # ✅ Router configuration
└── package.json
```

### 2.4 API Endpoints

**Servers API:** ✅ Complete
```
GET/POST   /api/v1/servers/
GET/PUT/DELETE /api/v1/servers/{id}/
POST       /api/v1/servers/{id}/test/
```

**Clients API:** ✅ Complete
```
GET/POST   /api/v1/clients/
GET/PUT/DELETE /api/v1/clients/{slug}/
POST       /api/v1/clients/{slug}/start/
POST       /api/v1/clients/{slug}/stop/
GET        /api/v1/clients/{slug}/logs/
GET        /api/v1/clients/{slug}/connections/
```

**Messages API:** ✅ Complete
```
GET        /api/v1/messages/
GET        /api/v1/messages/?client={uuid}&direction=sent|received
```

**Dashboard/Categories/Connections API:** ✅ Complete

### 2.5 Migration Progress

| Task | Status |
|------|--------|
| Vite + React project setup | ✅ Done |
| Tailwind CSS + Neon Theme | ✅ Done |
| i18n (German/English) | ✅ Done |
| All Core Pages | ✅ Done |
| Docker Compose Stack | ✅ Done (v0.1.10) |
| WebSocket Hooks | ❌ Todo |
| Tests & Events Pages | ❌ Todo |
| Zustand + React Query | ❌ Todo |

---

## 📊 Phase 3: Traffic Analysis Dashboard (v0.2.5)

### 3.1 Overview

The Traffic Analysis Dashboard provides deep insights into message flow, timing patterns, and network behavior. This is the **legitimate operator's view**—full access to all data because you own the infrastructure.

### 3.2 Dashboard Components

#### 3.2.1 Live Traffic Monitor
```
┌─────────────────────────────────────────────────────────────────┐
│     Live Traffic                                    ● In  ● Out │
│─────────────────────────────────────────────────────────────────│
│     1000 ┤                                                      │
│      750 ┤        ╭───╮      ╭──╮                               │
│      500 ┤   ╭────╯   ╰──────╯  ╰────╮      ╭──╮                │
│      250 ┤───╯                       ╰──────╯  ╰───             │
│        0 └──────────────────────────────────────────────────────│
│          277s   279s   281s   283s   285s   287s   289s         │
│─────────────────────────────────────────────────────────────────│
│     0.5 KB/s          0.3 KB/s           60                     │
│     Incoming          Outgoing           Events/min             │
└─────────────────────────────────────────────────────────────────┘
```

#### 3.2.2 Message Timeline
```
┌─────────────────────────────────────────────────────────────────┐
│     Message Timeline                              Last 60 min   │
│─────────────────────────────────────────────────────────────────│
│                   -0m     -15m     -30m     -45m     -60m       │
│  Client 001  │    ●●●      ●        ●●       ●        ●●●       │
│  Client 002  │     ●      ●●●       ●       ●●         ●        │
│  Client 003  │    ●●       ●       ●●●       ●        ●●        │
│  Client 004  │     ●       ●        ●       ●●●        ●        │
│─────────────────────────────────────────────────────────────────│
│              ● Sent (solid)    ○ Received (hollow)              │
└─────────────────────────────────────────────────────────────────┘
```

#### 3.2.3 Activity Heatmap
```
┌─────────────────────────────────────────────────────────────────┐
│     Activity Heatmap                                            │
│─────────────────────────────────────────────────────────────────│
│       0h  3h  6h  9h  12h 15h 18h 21h                           │
│  Mon  ░░  ░░  ▒▒  ▓▓  ██  ██  ▓▓  ▒▒                            │
│  Tue  ░░  ░░  ▒▒  ▓▓  ██  ██  ▓▓  ░░                            │
│  Wed  ░░  ░░  ░▒  ▓▓  ██  ▓▓  ▒▒  ░░                            │
│  Thu  ░░  ░░  ▒▒  ▓▓  ██  ██  ▓▓  ▒▒                            │
│  Fri  ░░  ░░  ▒▒  ██  ██  ▓▓  ▒▒  ░░                            │
│  Sat  ░░  ░░  ░░  ▒▒  ▓▓  ▓▓  ▒▒  ░░                            │
│  Sun  ░░  ░░  ░░  ▒▒  ▒▒  ▒▒  ░░  ░░                            │
│─────────────────────────────────────────────────────────────────│
│       Low ░░░░▒▒▒▒▓▓▓▓████ High                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### 3.2.4 Latency Distribution
```
┌─────────────────────────────────────────────────────────────────┐
│     Latency Distribution (ms)                                   │
│─────────────────────────────────────────────────────────────────│
│     50 ┤        ████                                            │
│     40 ┤        ████                                            │
│     30 ┤    ████████                                            │
│     20 ┤    ████████████                                        │
│     10 ┤████████████████████                                    │
│      0 └────────────────────────────────────────────────────────│
│        0-200  200-400  400-600  600-800  800-1000  1000+        │
│─────────────────────────────────────────────────────────────────│
│       342ms              891ms              98.2%               │
│       Median             P95                < 1 second          │
└─────────────────────────────────────────────────────────────────┘
```

#### 3.2.5 Packet Size Analysis
```
┌─────────────────────────────────────────────────────────────────┐
│  📦 Packet Sizes                                                │
│─────────────────────────────────────────────────────────────────│
│    <1 KB  ████████████████████████████████████████  (68%) Text  │
│   1-5 KB  ██████████████████████  (22%)                  Text   │
│  5-10 KB  ██████  (6%)                                  Mixed   │
│ 10-50 KB  ██  (3%)                                     Voice?   │
│   >50 KB  █  (1%)                                       Files   │
│─────────────────────────────────────────────────────────────────│
│     Packet size can reveal message type to observers            │
└─────────────────────────────────────────────────────────────────┘
```

### 3.3 Traffic Analysis Features

| Feature | Description | Security Relevance |
|---------|-------------|-------------------|
| **Live Throughput** | Real-time bytes/sec | Volume patterns |
| **Message Timeline** | Per-client message dots | Activity correlation |
| **Activity Heatmap** | Time-of-day patterns | User identification |
| **Latency Distribution** | Delivery time histogram | Network fingerprinting |
| **Packet Size Analysis** | Size distribution | Content type inference |
| **Flow Visualization** | Client-to-client flows | Relationship mapping |

---

## 👁️ Phase 4: Adversary View - Security Audit Mode (v0.3.0)

### 4.1 The Revolutionary Feature

**Adversary View** is what makes SimpleX SMP Monitor unique in the entire SimpleX ecosystem. It simulates what an external observer—whether an ISP, corporate network administrator, or state-level actor—can see about your SimpleX communications.

### 4.2 The Philosophy

> "You cannot defend against threats you don't understand."

Traditional security testing focuses on whether encryption works. Adversary View goes further: it shows you **what metadata leaks even when encryption is perfect**.

### 4.3 Threat Model Simulation

#### 4.3.1 Adversary Levels

```
┌─────────────────────────────────────────────────────────────────┐
│  ADVERSARY CAPABILITY LEVELS                                    │
│─────────────────────────────────────────────────────────────────│
│                                                                 │
│  Level 1: Passive Local Observer                                │
│  ├── Who: Coffee shop WiFi operator, home router                │
│  ├── Sees: That you use Tor, timing of connections              │
│  └── Cannot: See destinations, content, identify contacts       │
│                                                                 │
│  Level 2: ISP / Network Provider                                │
│  ├── Who: Telekom, Vodafone, corporate IT                       │
│  ├── Sees: All Level 1 + traffic volume patterns                │
│  └── Cannot: Break Tor, read content, identify servers          │
│                                                                 │
│  Level 3: State Actor (Single Country)                          │
│  ├── Who: BKA, FBI, local intelligence                          │
│  ├── Sees: All Level 2 + legal access to ISP data               │
│  ├── Tools: Wireshark, standard forensics, court orders         │
│  └── Cannot: Global traffic correlation, break E2E crypto       │
│                                                                 │
│  Level 4: Global Passive Adversary (Theoretical)                │
│  ├── Who: NSA-level capability                                  │
│  ├── Sees: All Level 3 + global traffic patterns                │
│  ├── Can: Timing correlation across multiple endpoints          │
│  └── Cannot: Break E2E encryption, read message content         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### 4.3.2 What We Can Simulate

| Adversary Level | Simulated | How |
|-----------------|-----------|-----|
| Level 1-2 | ✅ Full | Network traffic capture |
| Level 3 | ✅ Full | Timing analysis + metadata |
| Level 4 | ✅ Partial | We control both endpoints |

**Why Level 4 is possible in our test environment:**

```
In the real world:
  Client A ──Tor──► Server ──Tor──► Client B
     │                                  │
     └── Different people, locations ───┘
     
Global adversary needs to observe BOTH endpoints simultaneously.

In our test environment:
  Client A ──Tor──► Server ──Tor──► Client B
     │                                  │
     └──── SAME MACHINE / NETWORK ──────┘
     
We CAN observe both endpoints = Level 4 simulation!
```

### 4.4 Adversary View Dashboard

#### 4.4.1 Main Interface

```
┌─────────────────────────────────────────────────────────────────┐
│     ADVERSARY VIEW - Security Audit Mode                        │
│─────────────────────────────────────────────────────────────────│
│  Simulating: [Level 3: State Actor ▼]       [▶ Start Analysis]  │
│─────────────────────────────────────────────────────────────────│
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │     OVERALL SECURITY SCORE                                  ││
│  │                                                             ││
│  │         ╭──────────────────╮                                ││
│  │         │                  │                                ││
│  │         │       72%        │  GOOD                          ││
│  │         │                  │                                ││
│  │         ╰──────────────────╯                                ││
│  │                                                             ││
│  │     Content Protection: EXCELLENT (E2E encrypted)           ││
│  │     Identity Protection: GOOD (No user IDs on server)       ││
│  │     Timing Privacy: MODERATE (Patterns detected)            ││
│  │     Activity Privacy: MODERATE (Regular schedule visible)   ││
│  │                                                             ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### 4.4.2 Timing Correlation Analysis

```
┌─────────────────────────────────────────────────────────────────┐
│     TIMING CORRELATION ATTACK SIMULATION                        │
│─────────────────────────────────────────────────────────────────│
│                                                                 │
│  Monitoring Period: 2 hours                                     │
│  Events Analyzed: 847                                           │
│                                                                 │
│  DETECTED CORRELATIONS:                                         │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                                                             ││
│  │  Client A              Correlation              Client B    ││
│  │  ─────────             ───────────              ─────────   ││
│  │  14:32:05 [SEND] ──────── 94.7% ────────► 14:32:07 [RECV]   ││
│  │  14:33:12 [SEND] ──────── 91.2% ────────► 14:33:14 [RECV]   ││
│  │  14:35:00 [SEND] ──────── 96.1% ────────► 14:35:02 [RECV]   ││
│  │  14:38:45 [SEND] ──────── 89.8% ────────► 14:38:47 [RECV]   ││
│  │                                                             ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                 │
│     ⚠️  HIGH CONFIDENCE CORRELATION DETECTED                    │
│                                                                 │
│  An adversary observing both endpoints can determine with       │
│  94.7% confidence that Client A and Client B are communicating. │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### 4.4.3 Security Recommendations

```
┌─────────────────────────────────────────────────────────────────┐
│    🛡️ SECURITY RECOMMENDATIONS                                  │
│─────────────────────────────────────────────────────────────────│
│                                                                 │
│  Based on analysis, here are actionable improvements:           │
│                                                                 │
│  1. TIMING OBFUSCATION                          [Implement >]   │
│     ├── Current: Messages sent immediately                      │
│     ├── Risk: Timing correlation is trivial                     │
│     └── Fix: Add random delays (30-300s) to break patterns      │
│                                                                 │
│  2. COVER TRAFFIC                               [Implement >]   │
│     ├── Current: No dummy messages                              │
│     ├── Risk: Real message timing visible                       │
│     └── Fix: Send periodic dummy messages to create noise       │
│                                                                 │
│  3. MESSAGE BATCHING                            [Implement >]   │
│     ├── Current: Each message sent individually                 │
│     ├── Risk: Individual messages can be tracked                │
│     └── Fix: Batch multiple messages, send at intervals         │
│                                                                 │
│  ─────────────────────────────────────────────────────────────  │
│                                                                 │
│  ESTIMATED IMPROVEMENT AFTER IMPLEMENTATION:                    │
│                                                                 │
│  Before: Correlation Probability 94.7%  ████████████████████░░  │
│  After:  Correlation Probability 23.1%  █████░░░░░░░░░░░░░░░░░  │
│                                                                 │
│  [📄 Generate Full Report]  [📥 Export PDF]  [🔄 Re-analyze]   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 4.5 Adversary View Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| **Live Analysis** | Real-time pattern detection | Active monitoring |
| **Historical Audit** | Analyze past N hours/days | Security review |
| **Simulation** | Generate test traffic, analyze | Training |
| **Comparison** | Before/after mitigation | Validate improvements |

---

## 🧪 Phase 5: Advanced Test Panel (v0.3.5)

### 5.1 Test Panel Overview

The Test Panel allows operators to run comprehensive stress tests and reliability checks on their SimpleX infrastructure.

### 5.2 Test Types

| Test Type | Description | Use Case |
|-----------|-------------|----------|
| **Delivery Reliability** | Test message delivery across clients | Verify infrastructure |
| **Latency Benchmark** | Measure round-trip times | Performance tuning |
| **Stress Test** | High-volume message load | Capacity planning |
| **Mesh Connection** | Create full mesh between clients | Network testing |
| **Bulk Operations** | Create/manage many clients at once | Scale testing |

### 5.3 Test Configuration UI

```
┌─────────────────────────────────────────────────────────────────┐
│     🧪 STRESS TEST CONFIGURATION                                │
│─────────────────────────────────────────────────────────────────│
│                                                                 │
│  Test Type:     [Delivery Reliability ▼]                        │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Participants                                           │    │
│  │  ☑ Client 001 (Alice)                                   │   │
│  │  ☑ Client 002 (Bob)                                     │   │
│  │  ☑ Client 003 (Charlie)                                 │   │
│  │  ☐ Client 004 (Diana)                                   │   │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                 │
│  Messages per client:  [100    ]                                │
│  Interval (ms):        [500    ]                                │
│  Timeout (s):          [30     ]                                │
│  Include receipts:     [✓]                                      │
│                                                                 │
│  ────────────────────────────────────────────────────────────   │
│                                                                 │
│  Estimated Duration: ~2 minutes                                 │
│  Total Messages: 600                                            │
│                                                                 │
│  [▶ Start Test]    [📋 Load Preset]    [💾 Save Preset]        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📈 Phase 6: Monitoring & Visualization (v0.4.0)

### 6.1 Grafana Integration

Pre-built dashboards for:
- Server health overview
- Message throughput
- Latency trends
- Client performance comparison
- Real-time message flow

### 6.2 InfluxDB Time-Series Storage

- Store all traffic events
- Historical analysis
- Retention policies
- Downsampling for long-term storage

### 6.3 Alerting

| Alert Type | Trigger | Action |
|------------|---------|--------|
| Latency Spike | P95 > 2s | Notification |
| Delivery Failure | Rate > 5% | Notification + Log |
| Client Offline | No heartbeat 5min | Notification |
| Anomaly | ML-detected pattern | Review flag |

---

## 🔐 Phase 7: Enterprise Features (v0.5.0)

### 7.1 Multi-User Support

- User authentication (Django auth + JWT)
- Role-based access control (Admin, Operator, Viewer)
- Audit logging
- Per-user/team client ownership

### 7.2 REST API Authentication

- API key management
- Rate limiting
- OpenAPI/Swagger documentation
- Webhook support

### 7.3 Production Deployment

- PostgreSQL support ✅ (Added in v0.1.10)
- Redis clustering
- Docker Compose production config ✅ (Added in v0.1.10)
- Kubernetes manifests (optional)
- High availability considerations

---

## 🔄 Phase 8: Lab Environment (v0.6.0) - PARTIALLY COMPLETE

### 8.1 Overview

Transform the monitoring server into a **complete SimpleX lab environment** where SMP/XFTP servers run alongside clients in Docker, enabling full packet capture and analysis without external dependencies.

### 8.2 The Architecture Shift

**Current Architecture:**
```
┌─────────────────────┐              ┌─────────────────────┐
│  Monitoring Server  │◄────Tor────►│  Remote SMP Server  │
│  (Clients only)     │              │  (External)         │
└─────────────────────┘              └─────────────────────┘
```

**New Lab Architecture:**
```
┌─────────────────────────────────────────────────────────────────┐
│                    MONITORING SERVER (Lab Mode)                 │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              Docker Network (bridge)                    │    │
│  │              simplex-monitor-network                    │    │
│  │                                                         │    │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐    │   │
│  │  │SMP Srv 1 │ │SMP Srv 2 │ │XFTP Srv  │ │SMP Srv 3 │    │   │
│  │  │ :5223    │ │ :5224    │ │ :7225    │ │ :5226    │    │   │
│  │  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘    │   │
│  │       │            │            │            │          │   │
│  │       └────────────┴─────┬──────┴────────────┘          │   │
│  │                          │                              │   │
│  │            ┌─────────────▼─────────────┐                │   │
│  │            │    Docker Bridge          │                │   │
│  │            │    PACKET CAPTURE HERE 📡 │                │   │
│  │            └─────────────┬─────────────┘                │   │
│  │                          │                              │   │
│  │  ┌──────────┐ ┌──────────┴─┐ ┌──────────┐               │   │
│  │  │Client 001│ │Client 002  │ │Client 003│               │   │
│  │  └──────────┘ └────────────┘ └──────────┘               │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Django Backend + React Frontend + Analysis Tools       │   │
│  └─────────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────┘
```

### 8.3 Benefits of Lab Mode

| Aspect | Remote over Tor | Local Lab Mode |
|--------|-----------------|----------------|
| **Latency** | 500ms - 5s | < 1ms ⚡ |
| **Packet Capture** | Metrics only | **FULL TRAFFIC** 📡 |
| **Analysis Depth** | Limited | **Everything visible** 🔬 |
| **Debugging** | Difficult | Direct access |
| **Stress Tests** | Tor-limited | **Full bandwidth** |
| **Reproducibility** | Variable | **100% controlled** |
| **Offline Testing** | ❌ No | ✅ Yes |

### 8.4 Server Deployment Types

| Type | Address Format | Use Case |
|------|---------------|----------|
| `docker_local` | `localhost:5223` | Lab testing |
| `remote_tor` | `abc123.onion:5223` | Production Tor |
| `remote_lokinet` | `abc123.loki:5223` | Production Lokinet |
| `remote_clearnet` | `smp.example.com:5223` | Direct connection |

### 8.5 Implementation Progress (NEW in v0.1.10)

- [x] Docker SMP Server image (`simplex-smp:latest` v6.4.4.1)
- [x] Docker XFTP Server image (`simplex-xftp:latest` v6.4.4.1)
- [x] Docker NTF Server image (`simplex-ntf:latest` v6.4.4.1)
- [x] Dockerfiles with proper entrypoints
- [x] Docker Compose integration
- [x] Three installation methods (Build, wget, GHCR)
- [ ] SMPServer Model with deployment_type
- [ ] Docker Manager extension for SMP servers
- [ ] API: `/api/v1/smp-servers/`
- [ ] Frontend: Server deployment selector
- [ ] Auto-extract server fingerprint
- [ ] Connect clients to local servers
- [ ] Docker network packet capture setup

---

## 🆕 Phase 9: Private Tor Network (v0.7.0)

### 9.1 Overview

Simulate a **complete Tor network locally** using Chutney, enabling realistic Tor testing without touching the public Tor network.

### 9.2 What is Chutney?

**Chutney** is the official Tor Project tool for creating private Tor test networks.

**Resources:**
- GitHub: https://github.com/torproject/chutney
- GitLab (Official): https://gitlab.torproject.org/tpo/core/chutney

### 9.3 Three Test Modes

```
┌─────────────────────────────────────────────────────────────────┐
│                      TEST MODE SELECTOR                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ⚡ DIRECT MODE                                                 │
│  ═══════════════                                                │
│  No Tor, minimal latency (~1ms)                                 │
│  Full packet visibility                                         │
│  Best for: Development, debugging, stress tests                 │
│                                                                 │
│  🧪 PRIVATE TOR MODE                                            │
│  ════════════════════                                           │
│  Local Chutney network (~50-200ms)                              │
│  Realistic Tor behavior                                         │
│  Best for: Tor integration testing, timing analysis             │
│                                                                 │
│  🧅 PUBLIC TOR MODE                                             │
│  ═══════════════════                                            │
│  Real Tor network (~500ms-5s)                                   │
│  Production-like conditions                                     │
│  Best for: Final validation, real-world testing                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 9.4 Private Tor Network Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                PRIVATE TOR NETWORK (Chutney)                    │
│                                                                 │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐                   │
│  │ DirAuth 1  │ │ DirAuth 2  │ │ DirAuth 3  │                   │
│  │ (Authority)│ │ (Authority)│ │ (Authority)│                   │
│  └─────┬──────┘ └─────┬──────┘ └─────┬──────┘                   │
│        │              │              │                          │
│        └──────────────┼──────────────┘                          │
│                       │                                         │
│  ┌─────────┐ ┌────────▼────────┐ ┌─────────┐                    │
│  │ Guard 1 │ │  Middle Relays  │ │ Guard 2 │                    │
│  └────┬────┘ └────────┬────────┘ └────┬────┘                    │
│       │               │               │                         │
│       └───────────────┼───────────────┘                         │
│                       │                                         │
│            ┌──────────▼──────────┐                              │
│            │     Exit Nodes      │                              │
│            └──────────┬──────────┘                              │
│                       │                                         │
│  ┌────────────────────▼────────────────────┐                    │
│  │         SMP Server (.onion local)       │                    │
│  └─────────────────────────────────────────┘                    │
│                                                                 │
│  ⏱️ Circuit Build: ~2 seconds (vs 5-30s real Tor)               │
│  📡 Full observability at every hop                             │
└─────────────────────────────────────────────────────────────────┘
```

### 9.5 Chutney Network Configurations

| Config | Nodes | Description |
|--------|-------|-------------|
| `basic` | 3 Auth + 5 Relay + 2 Client | Minimal network |
| `basic-025` | More relays | More stable |
| `hs-025` | + Hidden Services | For .onion tests |
| `bridges` | + Bridge nodes | Bridge testing |

### 9.6 Implementation Tasks

- [ ] Chutney installation documentation
- [ ] Docker Tor node Dockerfiles (authority, relay, exit, client)
- [ ] torrc templates for each node type
- [ ] Django TestEnvironment model
- [ ] API to start/stop private Tor network
- [ ] Frontend: Mode selector component
- [ ] Frontend: Private Tor status dashboard
- [ ] Circuit visualization with stem
- [ ] Latency comparison between modes

---

## 🆕 Phase 10: Enterprise Monitoring Stack (v0.8.0)

### 10.1 Overview

Deploy a **Palantir-grade monitoring infrastructure** with deep packet inspection, graph visualization, and threat intelligence integration.

### 10.2 Full Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    MONITORING SERVER (64GB+ RAM recommended)            │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                        React Frontend                            │   │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌────────────┐  │   │
│  │  │ Cytoscape   │ │  Recharts   │ │ vis-timeline│ │  Grafana   │  │   │
│  │  │ Graph       │ │  Charts     │ │  Forensics  │ │  Embeds    │  │   │
│  │  └─────────────┘ └─────────────┘ └─────────────┘ └────────────┘  │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                    │                                    │
│                         WebSocket + REST API                            │
│                                    │                                    │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                        Django Backend                            │   │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌───────────────┐  │   │
│  │  │  Channels  │ │  REST API  │ │   Celery   │ │  stem (Tor)   │  │   │
│  │  │ WebSocket  │ │   Views    │ │   Tasks    │ │  Controller   │  │   │
│  │  └────────────┘ └────────────┘ └────────────┘ └───────────────┘  │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                         Data Layer                               │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐  │   │
│  │  │PostgreSQL│ │Timescale │ │  Neo4j   │ │   ELK/   │ │Promethe│  │   │
│  │  │  + Redis │ │    DB    │ │  Graph   │ │   Loki   │ │   us   │  │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └────────┘  │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    Security & Analysis Layer                     │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐  │   │
│  │  │   Zeek   │ │ Suricata │ │  Arkime  │ │ ntopng   │ │  MISP  │  │   │
│  │  │ Protocol │ │  IDS/IPS │ │  PCAP    │ │  Flows   │ │ Threat │  │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └────────┘  │   │
│  └──────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

### 10.3 Tool Stack

#### 10.3.1 Network Traffic Analysis

| Tool | RAM | Function | Python Integration |
|------|-----|----------|-------------------|
| **Zeek** | 2-8GB | Protocol analytics, 70+ log types | broker/WebSocket |
| **Suricata** | 2-4GB | IDS/IPS, signature-based | EVE JSON + Redis |
| **Arkime** | 30GB+ | Full packet capture & search | REST API |
| **ntopng** | 2-4GB | Flow analysis, 450+ protocols | `pip install ntopng` |

#### 10.3.2 Tor Integration

| Tool | Library | Function |
|------|---------|----------|
| **stem** | `pip install stem` | Complete Tor Controller API |
| **Onionoo** | REST API | Public relay metrics |
| **OnionBalance** | Unix Socket | Hidden Service load balancing |

#### 10.3.3 Observability Stack

| Tool | RAM | Function |
|------|-----|----------|
| **Prometheus** | 2-4GB | Metrics collection & alerting |
| **Grafana** | 500MB-1GB | Visualization & dashboards |
| **Pushgateway** | 100MB | Push-based metrics over Tor |

#### 10.3.4 Log Aggregation

| Tool | RAM | Function |
|------|-----|----------|
| **Elasticsearch** | 16-32GB | Full-text search & analytics |
| **Grafana Loki** | 500MB-2GB | Label-based log system (lighter) |
| **Promtail** | 50MB | Log shipping with SOCKS support |

#### 10.3.5 Graph Database & Visualization

| Tool | RAM | Function |
|------|-----|----------|
| **Neo4j** | 8-16GB | Graph database, Cypher queries |
| **Cytoscape.js** | - | Interactive graph visualization |
| **Sigma.js** | - | Large-scale WebGL graphs (100K+ nodes) |

#### 10.3.6 Threat Intelligence (Optional)

| Tool | RAM | Library | Function |
|------|-----|---------|----------|
| **SpiderFoot** | 2-4GB | CLI | OSINT automation, 200+ modules |
| **TheHive** | 4-8GB | `thehive4py` | Incident response |
| **Cortex** | 2-4GB | `cortex4py` | Observable analyzers (80+) |
| **MISP** | 4-8GB | `pymisp` | Threat intelligence sharing |
| **OpenCTI** | 8-16GB | `pycti` | Cyber threat intelligence |

### 10.4 Resource Requirements

| Component | RAM |
|-----------|-----|
| Elasticsearch/OpenSearch | 30GB |
| Neo4j | 8GB |
| Prometheus + Grafana | 4GB |
| Django/Celery | 4GB |
| Zeek + Suricata | 8GB |
| Arkime (optional) | 8GB+ |
| **Total Recommended** | **64GB+** |

### 10.5 Implementation Tasks

- [ ] Zeek Docker setup + custom SimpleX scripts
- [ ] Suricata Docker setup + custom rules
- [ ] Neo4j Docker + graph schema design
- [ ] Prometheus + Grafana + Pushgateway
- [ ] Loki + Promtail log aggregation
- [ ] stem Tor Controller integration
- [ ] Cytoscape.js React component
- [ ] Django Neo4j service layer
- [ ] MISP/OpenCTI integration (optional)
- [ ] SpiderFoot OSINT integration (optional)

---

## 🆕 Phase 11: Multi-Network Support (v0.9.0)

### 11.1 Overview

Extend support beyond Tor to include **Lokinet**, enabling operators to run SMP servers accessible via both `.onion` and `.loki` addresses.

### 11.2 Network Comparison

| | Tor | Lokinet |
|---|---|---|
| **Project** | Tor Project | Oxen (Session Messenger) |
| **Routing** | Onion Routing | Onion Routing (LLARP) |
| **Addresses** | .onion | .loki (SNApps) |
| **Incentive** | Voluntary | Blockchain-based (OXEN) |
| **Latency** | Higher | Reportedly lower |
| **SOCKS Port** | 9050 | 1190 |

### 11.3 Four Test Modes (Extended)

```
┌─────────────────────────────────────────────────────────────────┐
│                      TEST MODE SELECTOR v2                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ⚡ DIRECT MODE              ~1ms                               │
│     No overlay network, full visibility                         │
│                                                                 │
│  🧪 PRIVATE TOR MODE         ~50-200ms                          │
│     Local Chutney network                                       │
│                                                                 │
│  🧅 PUBLIC TOR MODE          ~500ms-5s                          │
│     Real Tor network                                            │
│                                                                 │
│  🟣 LOKINET MODE             ~???ms (TBD)                       │
│     Oxen network (.loki addresses)                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 11.4 Dual-Stack Server Support

Servers can be accessible via multiple networks simultaneously:

| Server | .onion Address | .loki Address | Clearnet |
|--------|---------------|---------------|----------|
| SMP-001 | `abc123.onion` | `xyz789.loki` | - |
| SMP-002 | `def456.onion` | - | `smp2.example.com` |
| XFTP-001 | `ghi789.onion` | `uvw321.loki` | - |

### 11.5 Implementation Tasks

- [ ] Research Lokinet SOCKS proxy setup
- [ ] Test SMP server accessibility via .loki
- [ ] Extend SMPServer model for .loki addresses
- [ ] Frontend: Network selector component
- [ ] Latency comparison: Tor vs Lokinet
- [ ] Documentation for dual-stack setup

### 11.6 Community Reference

> **GitHub Issue:** https://github.com/simplex-chat/simplex-chat/issues/1782

The SimpleX team has indicated that .loki address support would be considered when:
1. An Android app provides Lokinet as SOCKS proxy
2. Server-side client makes servers available on .loki

Our tool can help with #2 by providing tooling for server operators.

---

## 📅 Version Timeline

| Version | Target | Focus | Status |
|---------|--------|-------|--------|
| 0.1.8 | 2025-12-27 | Real-Time Infrastructure | ✅ Complete |
| 0.1.9 | 2025-12-29 | React Migration Part 1 | ✅ Complete |
| **0.1.10** | **2026-01-01** | **Docker One-Click Deployment** 🆕 | **✅ Complete** |
| 0.2.0 | 2026-01-15 | React Migration Part 2 | 🔄 Next |
| 0.2.5 | 2026-02-01 | Traffic Analysis Dashboard | 📋 Planned |
| 0.3.0 | 2026-02-15 | Adversary View | 📋 Planned |
| 0.3.5 | 2026-03-01 | Advanced Test Panel | 📋 Planned |
| 0.4.0 | 2026-03-15 | Monitoring & Grafana | 📋 Planned |
| 0.5.0 | 2026-04-01 | Enterprise Features | 📋 Planned |
| **0.6.0** | **2026-05-01** | **Lab Environment** | 🔄 Partially Complete |
| **0.7.0** | **2026-06-01** | **Private Tor Network** | 📋 Planned |
| **0.8.0** | **2026-07-01** | **Enterprise Stack** | 📋 Planned |
| **0.9.0** | **2026-08-01** | **Multi-Network (Lokinet)** | 📋 Planned |
| 1.0.0 | 2026-09-01 | Production Ready | 📋 Future |

---

## 🛠️ Technology Stack

### Frontend
| Component | Technology | Status |
|-----------|------------|--------|
| Framework | React 18 + TypeScript | ✅ |
| Build Tool | Vite 5.x | ✅ |
| Styling | Tailwind CSS (Neon Blue #88CED0) | ✅ |
| Routing | React Router v6 | ✅ |
| i18n | react-i18next | ✅ |
| Icons | Lucide React | ✅ |
| State | Zustand | 📋 Planned |
| Server State | React Query | 📋 Planned |
| Charts | Recharts | 📋 Planned |
| Graphs | Cytoscape.js | 📋 Phase 10 |

### Backend
| Component | Technology | Status |
|-----------|------------|--------|
| Framework | Django 5.x | ✅ |
| API | Django REST Framework | ✅ |
| WebSocket | Django Channels | ✅ |
| Message Broker | Redis 7.x | ✅ |
| Task Queue | Celery | 📋 Planned |
| Database | SQLite → PostgreSQL | ✅ / ✅ (Docker) |
| Time-Series | TimescaleDB | 📋 Phase 10 |
| Graph DB | Neo4j | 📋 Phase 10 |

### Deployment (NEW in v0.1.10)
| Component | Technology | Status |
|-----------|------------|--------|
| Containerization | Docker 24.x | ✅ |
| Orchestration | Docker Compose | ✅ |
| Reverse Proxy | Nginx | ✅ |
| Static Files | Whitenoise | ✅ |
| Database | PostgreSQL 15 | ✅ |
| Metrics | InfluxDB 2.7 | ✅ |
| Dashboards | Grafana | ✅ |
| Tor Proxy | dperson/torproxy | ✅ |

### SimpleX Server Images (NEW in v0.1.10)
| Component | Technology | Status |
|-----------|------------|--------|
| SMP Server | simplex-smp:latest (v6.4.4.1) | ✅ |
| XFTP Server | simplex-xftp:latest (v6.4.4.1) | ✅ |
| NTF Server | simplex-ntf:latest (v6.4.4.1) | ✅ |
| CLI Client | simplex-cli:latest | ✅ |

### Analysis Tools (Phase 10)
| Component | Technology |
|-----------|------------|
| Protocol Analysis | Zeek |
| IDS/IPS | Suricata |
| Full PCAP | Arkime |
| Flow Analysis | ntopng |
| Tor Controller | stem |
| Metrics | Prometheus + Grafana |
| Logs | Grafana Loki / ELK |
| Threat Intel | MISP, SpiderFoot |

### Infrastructure
| Component | Technology | Status |
|-----------|------------|--------|
| Containers | Docker 24.x | ✅ |
| SimpleX CLI | Docker containers | ✅ |
| SimpleX Servers | Docker containers | ✅ (NEW v0.1.10) |
| Network | Tor hidden services | ✅ |
| Private Tor | Chutney | 📋 Phase 9 |
| Multi-Network | Lokinet | 📋 Phase 11 |

---

## ⚖️ Legal Notice

This tool is designed for use on **your own infrastructure** only. See [LEGAL.md](LEGAL.md) for full legal information.

**Key Points:**
- ✅ Using these tools on own infrastructure is **legal** in Germany/EU
- ✅ Operating Tor nodes is **legal** (BGH I ZR 64/17, 2018)
- ✅ Private Tor network simulation is **legal**
- ✅ Developing dual-use security tools is **legal** (BVerfG 2009)
- ⚠️ Testing third-party systems requires **written authorization**

---

## 🎯 What Makes This Tool Unique

### For Journalists & Whistleblowers
> "See what your adversaries see. Improve before they exploit."

### For Security Researchers
> "The first tool to simulate timing correlation attacks on SimpleX."

### For NGOs & Organizations
> "Validate your secure communication infrastructure with real data."

### For Privacy Advocates
> "Prove that SimpleX metadata protection works—or find where it doesn't."

---

## 🎵 Project Anthem

*"Neon Uptime v2.0 - Enterprise Edition"*

> Zeek writes seventy log types, Suricata guards the gate  
> Arkime captures every packet, nothing slips, nothing's late  
> Neo4j mapping connections in gold  
> Palantir vibes but the code is our own  
> Open source power, and we're coming through  

---

## 🤝 Contributing

Priority areas for contribution:

| Area | Difficulty | Impact | Version |
|------|------------|--------|---------|
| WebSocket React Hooks | Medium | High | v0.2.0 |
| Tests/Events Pages | Medium | High | v0.2.0 |
| Traffic Visualization | Hard | Very High | v0.2.5 |
| Timing Correlation Algorithm | Hard | Very High | v0.3.0 |
| Docker SMP Server Integration | Medium | High | v0.6.0 |
| Chutney Integration | Hard | Very High | v0.7.0 |
| Neo4j Graph Integration | Hard | High | v0.8.0 |
| Lokinet Research | Medium | Medium | v0.9.0 |

---

*Last updated: 01 January 2026*
*Version: Roadmap v3.1*
*Authors: cannatoshi* 💎🧅