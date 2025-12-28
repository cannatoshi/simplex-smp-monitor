# SimpleX SMP Monitor - Roadmap v2 for 2026

## 🎯 Vision

**SimpleX SMP Monitor** is the world's first comprehensive security testing and infrastructure validation tool for SimpleX messaging infrastructure. It enables infrastructure operators—journalists, whistleblowers, NGOs, security researchers—to test their own SimpleX deployment with the same capabilities that external adversaries (including state-level actors) would have.

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

### The Core Insight

> "Your security is only as good as your weakest link. But how do you know what an adversary can see?"

This tool answers that question by providing **Adversary View Mode**—a simulation environment where you can see exactly what metadata and patterns are exposed, even when message content remains encrypted.

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

**Current Stack (v0.1.8):**
```
Frontend: Django Templates + Vanilla JS + Bootstrap
Backend:  Django + Channels + Redis
Clients:  Docker containers (simplex-chat CLI)
Network:  Tor hidden services (.onion)
```

---

## 🚀 Phase 2: React Revolution (v0.2.0)

### The Big Shift: From Django Templates to React SPA

This phase transforms the application from a traditional server-rendered Django application into a modern **Single Page Application (SPA)** with React frontend and Django REST API backend.

### 2.1 Architecture Transformation

**OLD Architecture (v0.1.x):**
```
┌─────────────────────────────────────────────────────────────────┐
│                         BROWSER                                  │
│  Django Templates (HTML) + Vanilla JavaScript                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                    HTTP (Full page loads)
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DJANGO SERVER                                 │
│  Views render HTML templates                                     │
│  WebSocket for live updates                                      │
└─────────────────────────────────────────────────────────────────┘
```

**NEW Architecture (v0.2.0+):**
```
┌─────────────────────────────────────────────────────────────────┐
│                    REACT SPA (Browser)                           │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Components        State           Services               │  │
│  │  ├── Dashboard     ├── Redux/      ├── API Client        │  │
│  │  ├── ClientList    │   Zustand     ├── WebSocket Hook    │  │
│  │  ├── ClientCard    ├── React       ├── Auth Service      │  │
│  │  ├── TestPanel     │   Query       └── Storage           │  │
│  │  ├── Adversary     └── Context                           │  │
│  │  │   View                                                 │  │
│  │  ├── Traffic                                              │  │
│  │  │   Dashboard                                            │  │
│  │  └── Settings                                             │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
           │                                    │
    REST API (JSON)                    WebSocket (Real-time)
           │                                    │
           ▼                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DJANGO REST BACKEND                           │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Django REST Framework    Django Channels                 │  │
│  │  ├── /api/servers/        ├── /ws/clients/               │  │
│  │  ├── /api/clients/        ├── /ws/traffic/               │  │
│  │  ├── /api/messages/       └── /ws/adversary/             │  │
│  │  ├── /api/tests/                                          │  │
│  │  └── /api/analysis/                                       │  │
│  └───────────────────────────────────────────────────────────┘  │
│                              │                                   │
│                    SimplexEventBridge                            │
│                              │                                   │
└─────────────────────────────────────────────────────────────────┘
           │                                    │
           ▼                                    ▼
┌─────────────────────┐              ┌─────────────────────┐
│  Docker Containers  │              │  Redis              │
│  (SimpleX CLI)      │              │  (Channel Layer)    │
└─────────────────────┘              └─────────────────────┘
```

### 2.2 React Project Setup

#### 2.2.1 Technology Stack
- [ ] **Vite** - Fast build tool (not Create React App)
- [ ] **React 18** - Latest React with concurrent features
- [ ] **TypeScript** - Type safety throughout
- [ ] **Tailwind CSS** - Utility-first styling (matches our PoC)
- [ ] **React Router v6** - Client-side routing
- [ ] **Zustand** - Lightweight state management
- [ ] **React Query** - Server state & caching
- [ ] **Recharts** - Charts and visualizations
- [ ] **Lucide React** - Icon library

#### 2.2.2 Project Structure
```
frontend/
├── src/
│   ├── components/
│   │   ├── ui/                    # Base UI components
│   │   │   ├── Button.tsx
│   │   │   ├── Card.tsx
│   │   │   ├── Badge.tsx
│   │   │   ├── Modal.tsx
│   │   │   ├── Toast.tsx
│   │   │   ├── Tooltip.tsx
│   │   │   └── Input.tsx
│   │   ├── layout/                # Layout components
│   │   │   ├── Sidebar.tsx
│   │   │   ├── Header.tsx
│   │   │   ├── Navigation.tsx
│   │   │   └── Footer.tsx
│   │   ├── clients/               # Client-related components
│   │   │   ├── ClientList.tsx
│   │   │   ├── ClientCard.tsx
│   │   │   ├── ClientDetail.tsx
│   │   │   ├── ClientStats.tsx
│   │   │   ├── ConnectionModal.tsx
│   │   │   └── MessagePanel.tsx
│   │   ├── servers/               # Server-related components
│   │   │   ├── ServerList.tsx
│   │   │   ├── ServerCard.tsx
│   │   │   ├── ServerForm.tsx
│   │   │   └── ServerStatus.tsx
│   │   ├── testing/               # Test panel components
│   │   │   ├── TestPanel.tsx
│   │   │   ├── TestConfig.tsx
│   │   │   ├── TestProgress.tsx
│   │   │   └── TestResults.tsx
│   │   ├── traffic/               # Traffic analysis components
│   │   │   ├── TrafficDashboard.tsx
│   │   │   ├── LiveTrafficGraph.tsx
│   │   │   ├── MessageTimeline.tsx
│   │   │   ├── ActivityHeatmap.tsx
│   │   │   ├── LatencyDistribution.tsx
│   │   │   └── PacketSizeChart.tsx
│   │   └── adversary/             # Adversary view components
│   │       ├── AdversaryDashboard.tsx
│   │       ├── TimingCorrelation.tsx
│   │       ├── MetadataExposure.tsx
│   │       ├── RiskAssessment.tsx
│   │       ├── PatternDetection.tsx
│   │       └── Recommendations.tsx
│   ├── pages/
│   │   ├── Dashboard.tsx
│   │   ├── Clients.tsx
│   │   ├── ClientDetail.tsx
│   │   ├── Servers.tsx
│   │   ├── TestPanel.tsx
│   │   ├── TrafficAnalysis.tsx
│   │   ├── AdversaryView.tsx
│   │   └── Settings.tsx
│   ├── hooks/
│   │   ├── useWebSocket.ts
│   │   ├── useClients.ts
│   │   ├── useServers.ts
│   │   ├── useTraffic.ts
│   │   └── useAdversary.ts
│   ├── services/
│   │   ├── api.ts                 # REST API client
│   │   ├── websocket.ts           # WebSocket service
│   │   └── storage.ts             # Local storage
│   ├── store/
│   │   ├── clientStore.ts
│   │   ├── serverStore.ts
│   │   ├── trafficStore.ts
│   │   └── adversaryStore.ts
│   ├── types/
│   │   ├── client.ts
│   │   ├── server.ts
│   │   ├── message.ts
│   │   ├── traffic.ts
│   │   └── adversary.ts
│   ├── utils/
│   │   ├── formatting.ts
│   │   ├── calculations.ts
│   │   └── constants.ts
│   ├── App.tsx
│   ├── main.tsx
│   └── index.css
├── public/
├── package.json
├── tsconfig.json
├── tailwind.config.js
├── vite.config.ts
└── README.md
```

#### 2.2.3 Django REST API Endpoints

**Servers API:**
```
GET    /api/servers/              # List all servers
POST   /api/servers/              # Create server
GET    /api/servers/{id}/         # Get server details
PUT    /api/servers/{id}/         # Update server
DELETE /api/servers/{id}/         # Delete server
POST   /api/servers/{id}/test/    # Test server connection
```

**Clients API:**
```
GET    /api/clients/              # List all clients
POST   /api/clients/              # Create client
GET    /api/clients/{slug}/       # Get client details
PUT    /api/clients/{slug}/       # Update client
DELETE /api/clients/{slug}/       # Delete client
POST   /api/clients/{slug}/start/ # Start container
POST   /api/clients/{slug}/stop/  # Stop container
GET    /api/clients/{slug}/logs/  # Get container logs
GET    /api/clients/{slug}/messages/     # Get messages
POST   /api/clients/{slug}/messages/     # Send message
GET    /api/clients/{slug}/connections/  # Get connections
POST   /api/clients/{slug}/connections/  # Create connection
```

**Traffic Analysis API:**
```
GET    /api/traffic/              # Get traffic overview
GET    /api/traffic/live/         # Get live traffic data
GET    /api/traffic/timeline/     # Get message timeline
GET    /api/traffic/heatmap/      # Get activity heatmap
GET    /api/traffic/latency/      # Get latency distribution
GET    /api/traffic/packets/      # Get packet size analysis
```

**Adversary Analysis API:**
```
GET    /api/adversary/            # Get adversary view overview
GET    /api/adversary/correlation/    # Get timing correlation data
GET    /api/adversary/metadata/       # Get metadata exposure report
GET    /api/adversary/patterns/       # Get detected patterns
GET    /api/adversary/risk/           # Get risk assessment
GET    /api/adversary/recommendations/ # Get security recommendations
POST   /api/adversary/simulate/       # Run adversary simulation
```

**Test Panel API:**
```
GET    /api/tests/                # List test runs
POST   /api/tests/                # Create/start test
GET    /api/tests/{id}/           # Get test details
POST   /api/tests/{id}/stop/      # Stop running test
GET    /api/tests/{id}/results/   # Get test results
```

### 2.3 WebSocket Channels

```typescript
// WebSocket message types

// Client Updates Channel: /ws/clients/
interface ClientUpdate {
  type: 'client_status' | 'client_stats' | 'message_status' | 'new_message';
  payload: ClientPayload;
}

// Traffic Channel: /ws/traffic/
interface TrafficUpdate {
  type: 'traffic_event' | 'latency_update' | 'packet_captured';
  payload: TrafficPayload;
}

// Adversary Channel: /ws/adversary/
interface AdversaryUpdate {
  type: 'correlation_detected' | 'pattern_found' | 'risk_changed';
  payload: AdversaryPayload;
}

// Test Channel: /ws/tests/{test_id}/
interface TestUpdate {
  type: 'progress' | 'message_sent' | 'message_received' | 'error' | 'complete';
  payload: TestPayload;
}
```

### 2.4 Core React Components

#### 2.4.1 Live Status Indicator
```tsx
// Real-time connection status with detailed tooltip
<LiveIndicator
  websocketStatus="connected"
  eventBridgeStatus="running"
  connectedClients={12}
  channelLayer="Redis"
  lastEvent="2 seconds ago"
  uptime="4h 32m"
/>
```

#### 2.4.2 Client Card
```tsx
// Animated client card with live stats
<ClientCard
  name="Client 001"
  status="online"
  profile="quinn"
  messagesSent={142}
  messagesReceived={138}
  deliveryRate={97.2}
  avgLatency={342}
  lastActivity="2 seconds ago"
  onStartStop={() => {}}
  onViewDetails={() => {}}
/>
```

#### 2.4.3 Message Timeline
```tsx
// Visual timeline of messages across clients
<MessageTimeline
  clients={clients}
  events={events}
  timeRange="1h"
  onEventClick={(event) => {}}
  showCorrelations={true}
/>
```

### 2.5 Development Workflow

```bash
# Development (two terminals)
# Terminal 1: Django backend
cd backend/
source venv/bin/activate
python manage.py runserver 0.0.0.0:8000

# Terminal 2: React frontend
cd frontend/
npm run dev  # Vite dev server on :5173

# Production build
cd frontend/
npm run build  # Creates dist/ folder
# Copy to Django static files or serve separately
```

### 2.6 Migration Checklist

- [ ] Set up Vite + React project
- [ ] Configure Tailwind CSS
- [ ] Set up React Router
- [ ] Create base UI components
- [ ] Implement API service layer
- [ ] Implement WebSocket hooks
- [ ] Migrate Dashboard page
- [ ] Migrate Clients list page
- [ ] Migrate Client detail page
- [ ] Migrate Servers page
- [ ] Add dark/light mode toggle
- [ ] Add language switcher (i18n)
- [ ] Configure production build
- [ ] Update deployment scripts

---

## 📊 Phase 3: Traffic Analysis Dashboard (v0.2.5)

### 3.1 Overview

The Traffic Analysis Dashboard provides deep insights into message flow, timing patterns, and network behavior. This is the **legitimate operator's view**—full access to all data because you own the infrastructure.

### 3.2 Traffic Data Model

```python
# Django Model
class TrafficEvent(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    client = models.ForeignKey(SimplexClient, on_delete=models.CASCADE)
    direction = models.CharField(max_length=3, choices=[('in', 'In'), ('out', 'Out')])
    event_type = models.CharField(max_length=20)  # 'message', 'ack', 'connection', etc.
    payload_size = models.IntegerField()  # bytes
    latency_ms = models.IntegerField(null=True)
    correlation_id = models.CharField(max_length=64, null=True)  # Link send→receive
    remote_contact = models.CharField(max_length=64, null=True)  # Anonymized contact ref
    metadata = models.JSONField(default=dict)  # Additional event data

    class Meta:
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['client', 'timestamp']),
            models.Index(fields=['correlation_id']),
        ]
```

### 3.3 Dashboard Components

#### 3.3.1 Live Traffic Monitor
```
┌─────────────────────────────────────────────────────────────────┐
│  📡 Live Traffic                                    ● In  ● Out │
│─────────────────────────────────────────────────────────────────│
│     1000 ┤                                                      │
│      750 ┤        ╭───╮      ╭──╮                               │
│      500 ┤   ╭────╯   ╰──────╯  ╰────╮      ╭──╮               │
│      250 ┤───╯                       ╰──────╯  ╰───            │
│        0 └──────────────────────────────────────────────────────│
│          277s   279s   281s   283s   285s   287s   289s        │
│─────────────────────────────────────────────────────────────────│
│     0.5 KB/s          0.3 KB/s           60                    │
│     Incoming          Outgoing           Events/min            │
└─────────────────────────────────────────────────────────────────┘
```

#### 3.3.2 Message Timeline
```
┌─────────────────────────────────────────────────────────────────┐
│  📨 Message Timeline                              Last 60 min   │
│─────────────────────────────────────────────────────────────────│
│                   -0m     -15m     -30m     -45m     -60m       │
│  Client 001  │    ●●●      ●        ●●       ●        ●●●      │
│  Client 002  │     ●      ●●●       ●       ●●         ●       │
│  Client 003  │    ●●       ●       ●●●       ●        ●●       │
│  Client 004  │     ●       ●        ●       ●●●        ●       │
│─────────────────────────────────────────────────────────────────│
│              ● Sent (solid)    ○ Received (hollow)             │
└─────────────────────────────────────────────────────────────────┘
```

#### 3.3.3 Activity Heatmap
```
┌─────────────────────────────────────────────────────────────────┐
│  🗓️ Activity Heatmap                                            │
│─────────────────────────────────────────────────────────────────│
│       0h  3h  6h  9h  12h 15h 18h 21h                           │
│  Mon  ░░  ░░  ▒▒  ▓▓  ██  ██  ▓▓  ▒▒                           │
│  Tue  ░░  ░░  ▒▒  ▓▓  ██  ██  ▓▓  ░░                           │
│  Wed  ░░  ░░  ░▒  ▓▓  ██  ▓▓  ▒▒  ░░                           │
│  Thu  ░░  ░░  ▒▒  ▓▓  ██  ██  ▓▓  ▒▒                           │
│  Fri  ░░  ░░  ▒▒  ██  ██  ▓▓  ▒▒  ░░                           │
│  Sat  ░░  ░░  ░░  ▒▒  ▓▓  ▓▓  ▒▒  ░░                           │
│  Sun  ░░  ░░  ░░  ▒▒  ▒▒  ▒▒  ░░  ░░                           │
│─────────────────────────────────────────────────────────────────│
│       Low ░░░░▒▒▒▒▓▓▓▓████ High                                │
└─────────────────────────────────────────────────────────────────┘
```

#### 3.3.4 Latency Distribution
```
┌─────────────────────────────────────────────────────────────────┐
│  ⚡ Latency Distribution (ms)                                   │
│─────────────────────────────────────────────────────────────────│
│     50 ┤        ████                                            │
│     40 ┤        ████                                            │
│     30 ┤    ████████                                            │
│     20 ┤    ████████████                                        │
│     10 ┤████████████████████                                    │
│      0 └────────────────────────────────────────────────────────│
│        0-200  200-400  400-600  600-800  800-1000  1000+       │
│─────────────────────────────────────────────────────────────────│
│       342ms              891ms              98.2%               │
│       Median             P95                < 1 second          │
└─────────────────────────────────────────────────────────────────┘
```

#### 3.3.5 Packet Size Analysis
```
┌─────────────────────────────────────────────────────────────────┐
│  📦 Packet Sizes                                                │
│─────────────────────────────────────────────────────────────────│
│    <1 KB  ████████████████████████████████████████  (68%) Text │
│   1-5 KB  ██████████████████████  (22%)                  Text  │
│  5-10 KB  ██████  (6%)                                  Mixed  │
│ 10-50 KB  ██  (3%)                                     Voice?  │
│   >50 KB  █  (1%)                                       Files  │
│─────────────────────────────────────────────────────────────────│
│  ⚠️ Packet size can reveal message type to observers           │
└─────────────────────────────────────────────────────────────────┘
```

### 3.4 Traffic Analysis Features

| Feature | Description | Security Relevance |
|---------|-------------|-------------------|
| **Live Throughput** | Real-time bytes/sec | Volume patterns |
| **Message Timeline** | Per-client message dots | Activity correlation |
| **Activity Heatmap** | Time-of-day patterns | User identification |
| **Latency Distribution** | Delivery time histogram | Network fingerprinting |
| **Packet Size Analysis** | Size distribution | Content type inference |
| **Flow Visualization** | Client-to-client flows | Relationship mapping |

### 3.5 Data Collection

```python
# EventBridge extension for traffic collection
class TrafficCollector:
    async def on_message_event(self, client, event):
        await TrafficEvent.objects.acreate(
            client=client,
            direction='out' if event['type'] == 'sent' else 'in',
            event_type='message',
            payload_size=len(event.get('content', '')),
            latency_ms=event.get('latency'),
            correlation_id=event.get('msg_id'),
            metadata={
                'status': event.get('status'),
                'has_file': event.get('has_file', False),
            }
        )
```

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
│  ADVERSARY CAPABILITY LEVELS                                     │
│─────────────────────────────────────────────────────────────────│
│                                                                  │
│  Level 1: Passive Local Observer                                │
│  ├── Who: Coffee shop WiFi operator, home router                │
│  ├── Sees: That you use Tor, timing of connections              │
│  └── Cannot: See destinations, content, identify contacts       │
│                                                                  │
│  Level 2: ISP / Network Provider                                │
│  ├── Who: Telekom, Vodafone, corporate IT                       │
│  ├── Sees: All Level 1 + traffic volume patterns                │
│  └── Cannot: Break Tor, read content, identify servers          │
│                                                                  │
│  Level 3: State Actor (Single Country)                          │
│  ├── Who: BKA, FBI, local intelligence                          │
│  ├── Sees: All Level 2 + legal access to ISP data               │
│  ├── Tools: Wireshark, standard forensics, court orders         │
│  └── Cannot: Global traffic correlation, break E2E crypto       │
│                                                                  │
│  Level 4: Global Passive Adversary (Theoretical)                │
│  ├── Who: NSA-level capability                                  │
│  ├── Sees: All Level 3 + global traffic patterns                │
│  ├── Can: Timing correlation across multiple endpoints          │
│  └── Cannot: Break E2E encryption, read message content         │
│                                                                  │
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
│  👁️ ADVERSARY VIEW - Security Audit Mode                        │
│─────────────────────────────────────────────────────────────────│
│  Simulating: [Level 3: State Actor ▼]       [▶ Start Analysis]  │
│─────────────────────────────────────────────────────────────────│
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  📊 OVERALL SECURITY SCORE                                  ││
│  │                                                              ││
│  │         ╭──────────────────╮                                ││
│  │         │                  │                                ││
│  │         │       72%        │  GOOD                          ││
│  │         │                  │                                ││
│  │         ╰──────────────────╯                                ││
│  │                                                              ││
│  │  ✅ Content Protection: EXCELLENT (E2E encrypted)           ││
│  │  ✅ Identity Protection: GOOD (No user IDs on server)       ││
│  │  ⚠️ Timing Privacy: MODERATE (Patterns detected)            ││
│  │  ⚠️ Activity Privacy: MODERATE (Regular schedule visible)   ││
│  │                                                              ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

#### 4.4.2 Timing Correlation Analysis

```
┌─────────────────────────────────────────────────────────────────┐
│  ⏱️ TIMING CORRELATION ATTACK SIMULATION                         │
│─────────────────────────────────────────────────────────────────│
│                                                                  │
│  Monitoring Period: 2 hours                                      │
│  Events Analyzed: 847                                            │
│                                                                  │
│  DETECTED CORRELATIONS:                                         │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                                                              ││
│  │  Client A              Correlation              Client B    ││
│  │  ─────────             ───────────              ─────────   ││
│  │  14:32:05 [SEND] ──────── 94.7% ────────► 14:32:07 [RECV]  ││
│  │  14:33:12 [SEND] ──────── 91.2% ────────► 14:33:14 [RECV]  ││
│  │  14:35:00 [SEND] ──────── 96.1% ────────► 14:35:02 [RECV]  ││
│  │  14:38:45 [SEND] ──────── 89.8% ────────► 14:38:47 [RECV]  ││
│  │                                                              ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│  ⚠️ HIGH CONFIDENCE CORRELATION DETECTED                        │
│                                                                  │
│  An adversary observing both endpoints can determine with       │
│  94.7% confidence that Client A and Client B are communicating. │
│                                                                  │
│  Average Latency: 2.1 seconds (consistent = easier to correlate)│
│  Pattern: Regular intervals (~3 minutes) increases risk         │
│                                                                  │
│  🔒 WHAT REMAINS PROTECTED:                                     │
│  ├── Message content: [ENCRYPTED - Not visible]                 │
│  ├── Message topic: [UNKNOWN]                                   │
│  └── Specific identities: [Requires additional correlation]     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

#### 4.4.3 Metadata Exposure Report

```
┌─────────────────────────────────────────────────────────────────┐
│  📋 METADATA EXPOSURE REPORT                                     │
│─────────────────────────────────────────────────────────────────│
│                                                                  │
│  ⚠️ EXPOSED TO ADVERSARY (Level 3):                             │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                                                              ││
│  │  Activity Times                                              ││
│  │  └── User is most active: 09:00-17:00 weekdays              ││
│  │  └── Timezone inference: Likely Central European (CET)      ││
│  │  └── Sleep pattern: Inactive 23:00-07:00                    ││
│  │                                                              ││
│  │  Communication Patterns                                      ││
│  │  └── Average messages/hour: 15                              ││
│  │  └── Burst patterns detected: Yes (meetings?)               ││
│  │  └── Regular intervals: Every ~3 minutes                    ││
│  │                                                              ││
│  │  Traffic Characteristics                                     ││
│  │  └── Average packet size: 1.2 KB (text messages)            ││
│  │  └── Large transfers detected: 3 (likely files)             ││
│  │  └── Network used: Tor (visible to ISP)                     ││
│  │                                                              ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│  🔒 PROTECTED FROM ADVERSARY:                                   │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                                                              ││
│  │  ✅ Message Content         [E2E Encrypted]                 ││
│  │  ✅ Contact Identities      [Not stored on server]          ││
│  │  ✅ Contact List            [Doesn't exist centrally]       ││
│  │  ✅ Server Destination      [Hidden by Tor]                 ││
│  │  ✅ User Account            [No accounts in SimpleX]        ││
│  │                                                              ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

#### 4.4.4 Pattern Detection

```
┌─────────────────────────────────────────────────────────────────┐
│  🔍 PATTERN DETECTION ENGINE                                     │
│─────────────────────────────────────────────────────────────────│
│                                                                  │
│  ⚠️ DETECTED PATTERNS:                                          │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ 🔴 HIGH RISK: Regular Interval Communication              │   │
│  │                                                           │   │
│  │ Client A sends messages every ~180 seconds (±12s)        │   │
│  │ This regularity makes correlation attacks trivial.       │   │
│  │                                                           │   │
│  │ Recommendation: Add random delays between 30-300 seconds │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ 🟡 MEDIUM RISK: Workday Activity Pattern                  │   │
│  │                                                           │   │
│  │ Activity concentrated during business hours (CET)        │   │
│  │ Suggests professional use / European timezone            │   │
│  │                                                           │   │
│  │ Recommendation: Consider scheduled background traffic    │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ 🟢 LOW RISK: Varying Message Sizes                        │   │
│  │                                                           │   │
│  │ Good mix of packet sizes observed                        │   │
│  │ Makes content type inference more difficult              │   │
│  │                                                           │   │
│  │ Status: No action needed                                 │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

#### 4.4.5 Security Recommendations

```
┌─────────────────────────────────────────────────────────────────┐
│  💡 SECURITY RECOMMENDATIONS                                     │
│─────────────────────────────────────────────────────────────────│
│                                                                  │
│  Based on analysis, here are actionable improvements:           │
│                                                                  │
│  1. TIMING OBFUSCATION                          [Implement ▶]   │
│     ├── Current: Messages sent immediately                      │
│     ├── Risk: Timing correlation is trivial                     │
│     └── Fix: Add random delays (30-300s) to break patterns      │
│                                                                  │
│  2. COVER TRAFFIC                               [Implement ▶]   │
│     ├── Current: No dummy messages                              │
│     ├── Risk: Real message timing visible                       │
│     └── Fix: Send periodic dummy messages to create noise       │
│                                                                  │
│  3. MESSAGE BATCHING                            [Implement ▶]   │
│     ├── Current: Each message sent individually                 │
│     ├── Risk: Individual messages can be tracked                │
│     └── Fix: Batch multiple messages, send at intervals         │
│                                                                  │
│  4. ACTIVITY SCHEDULE                           [Review ▶]      │
│     ├── Current: Activity follows work schedule                 │
│     ├── Risk: Timezone/occupation inference possible            │
│     └── Fix: Use delayed delivery, schedule variation           │
│                                                                  │
│  ─────────────────────────────────────────────────────────────  │
│                                                                  │
│  ESTIMATED IMPROVEMENT AFTER IMPLEMENTATION:                    │
│                                                                  │
│  Before: Correlation Probability 94.7%  ████████████████████░░  │
│  After:  Correlation Probability 23.1%  █████░░░░░░░░░░░░░░░░░  │
│                                                                  │
│  [📊 Generate Full Report]  [📥 Export PDF]  [🔄 Re-analyze]    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 4.5 Technical Implementation

#### 4.5.1 Timing Correlation Algorithm

```python
class TimingCorrelator:
    """
    Implements timing correlation attack simulation.
    
    Algorithm:
    1. Collect all send events from Client A
    2. Collect all receive events from Client B
    3. For each send event, find receive events within time window
    4. Calculate correlation probability based on:
       - Time difference (closer = higher probability)
       - Regularity of intervals
       - Historical patterns
    """
    
    def __init__(self, time_window_ms=5000):
        self.time_window = time_window_ms
        
    async def analyze(self, client_a_id, client_b_id, duration_minutes=60):
        # Get events from both clients
        cutoff = timezone.now() - timedelta(minutes=duration_minutes)
        
        sends = await TrafficEvent.objects.filter(
            client_id=client_a_id,
            direction='out',
            event_type='message',
            timestamp__gte=cutoff
        ).order_by('timestamp').values('timestamp', 'correlation_id')
        
        receives = await TrafficEvent.objects.filter(
            client_id=client_b_id,
            direction='in',
            event_type='message',
            timestamp__gte=cutoff
        ).order_by('timestamp').values('timestamp', 'correlation_id')
        
        correlations = []
        
        for send in sends:
            for recv in receives:
                delta_ms = (recv['timestamp'] - send['timestamp']).total_seconds() * 1000
                
                if 0 < delta_ms < self.time_window:
                    probability = self._calculate_probability(delta_ms)
                    correlations.append({
                        'send_time': send['timestamp'],
                        'recv_time': recv['timestamp'],
                        'delta_ms': delta_ms,
                        'probability': probability,
                    })
        
        return {
            'correlations': correlations,
            'overall_probability': self._aggregate_probability(correlations),
            'risk_level': self._assess_risk(correlations),
        }
    
    def _calculate_probability(self, delta_ms):
        """
        Probability decreases with time difference.
        Uses exponential decay model.
        """
        # Peak probability at ~2 seconds (typical Tor latency)
        expected_latency = 2000
        variance = 1000
        
        diff = abs(delta_ms - expected_latency)
        probability = math.exp(-(diff ** 2) / (2 * variance ** 2))
        
        return min(probability * 100, 99.9)  # Cap at 99.9%
```

#### 4.5.2 Pattern Detection Engine

```python
class PatternDetector:
    """
    Detects patterns in communication that could identify users.
    """
    
    async def detect_all_patterns(self, client_id, duration_hours=24):
        events = await self._get_events(client_id, duration_hours)
        
        patterns = []
        
        # Check for regular intervals
        interval_pattern = self._detect_interval_pattern(events)
        if interval_pattern:
            patterns.append(interval_pattern)
        
        # Check for time-of-day patterns
        tod_pattern = self._detect_time_of_day_pattern(events)
        if tod_pattern:
            patterns.append(tod_pattern)
        
        # Check for burst patterns (many messages in short time)
        burst_pattern = self._detect_burst_pattern(events)
        if burst_pattern:
            patterns.append(burst_pattern)
        
        # Check for packet size patterns
        size_pattern = self._detect_size_pattern(events)
        if size_pattern:
            patterns.append(size_pattern)
        
        return patterns
    
    def _detect_interval_pattern(self, events):
        """
        Detect if messages are sent at regular intervals.
        """
        if len(events) < 10:
            return None
            
        intervals = []
        for i in range(1, len(events)):
            delta = (events[i].timestamp - events[i-1].timestamp).total_seconds()
            intervals.append(delta)
        
        mean_interval = statistics.mean(intervals)
        std_dev = statistics.stdev(intervals)
        coefficient_of_variation = std_dev / mean_interval
        
        if coefficient_of_variation < 0.2:  # Very regular
            return {
                'type': 'regular_interval',
                'risk': 'high',
                'description': f'Messages sent every ~{int(mean_interval)} seconds (±{int(std_dev)}s)',
                'recommendation': 'Add random delays between 30-300 seconds',
                'mean_interval': mean_interval,
                'variation': coefficient_of_variation,
            }
        
        return None
```

### 4.6 Adversary View Modes

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

#### 5.2.1 Delivery Reliability Test
```
┌─────────────────────────────────────────────────────────────────┐
│  📬 DELIVERY RELIABILITY TEST                                    │
│─────────────────────────────────────────────────────────────────│
│                                                                  │
│  Configuration:                                                  │
│  ├── Source Clients: [✓] Client 001  [✓] Client 002             │
│  ├── Target Clients: [✓] Client 003  [✓] Client 004             │
│  ├── Messages per pair: [100]                                    │
│  ├── Interval: [500] ms                                          │
│  └── Timeout for delivery: [30] seconds                          │
│                                                                  │
│  [▶ Start Test]                                                  │
│                                                                  │
│  ─────────────────────────────────────────────────────────────  │
│                                                                  │
│  Progress: ████████████████░░░░  80%  (320/400 messages)        │
│                                                                  │
│  Live Results:                                                   │
│  ├── Sent: 320                                                   │
│  ├── Delivered (✓✓): 298                                        │
│  ├── Pending (✓): 18                                             │
│  ├── Failed (✗): 4                                               │
│  └── Success Rate: 93.1%                                        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

#### 5.2.2 Latency Benchmark Test
```
┌─────────────────────────────────────────────────────────────────┐
│  ⚡ LATENCY BENCHMARK TEST                                       │
│─────────────────────────────────────────────────────────────────│
│                                                                  │
│  Test Configuration:                                             │
│  ├── Ping-pong pairs: 4                                          │
│  ├── Iterations: 100                                             │
│  └── Measure: Round-trip time                                    │
│                                                                  │
│  Results:                                                        │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ Route              Min     Avg     Max     P95     P99     │ │
│  │ ──────────────────────────────────────────────────────────│ │
│  │ 001 ↔ 003          1.2s    2.1s    4.8s    3.9s    4.5s   │ │
│  │ 001 ↔ 004          1.4s    2.3s    5.1s    4.2s    4.8s   │ │
│  │ 002 ↔ 003          1.1s    2.0s    4.5s    3.8s    4.3s   │ │
│  │ 002 ↔ 004          1.3s    2.2s    4.9s    4.0s    4.6s   │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  Overall P95: 4.0s   Target: < 5s   Status: ✅ PASS             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

#### 5.2.3 Stress Test
```
┌─────────────────────────────────────────────────────────────────┐
│  🔥 STRESS TEST                                                  │
│─────────────────────────────────────────────────────────────────│
│                                                                  │
│  Configuration:                                                  │
│  ├── Clients: 20 (all)                                           │
│  ├── Messages/client/minute: [60]                                │
│  ├── Duration: [30] minutes                                      │
│  └── Pattern: [Sustained ▼]                                      │
│                                                                  │
│  Expected Load:                                                  │
│  └── 1,200 messages/minute across all clients                    │
│                                                                  │
│  [▶ Start Stress Test]                                          │
│                                                                  │
│  ─────────────────────────────────────────────────────────────  │
│                                                                  │
│  Status: Running (18:42 remaining)                               │
│                                                                  │
│  Metrics:                                                        │
│  ├── Messages Sent: 14,234                                       │
│  ├── Messages Delivered: 13,891                                  │
│  ├── Current Rate: 1,187 msg/min                                 │
│  ├── Error Rate: 2.4%                                            │
│  ├── Avg Latency: 2.8s (increasing ⚠️)                          │
│  └── Memory Usage: 4.2 GB / 8 GB                                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

#### 5.2.4 Mesh Connection Test
```
┌─────────────────────────────────────────────────────────────────┐
│  🕸️ MESH CONNECTION TEST                                        │
│─────────────────────────────────────────────────────────────────│
│                                                                  │
│  Create full mesh between selected clients:                     │
│                                                                  │
│  Select Clients:                                                 │
│  [✓] Client 001   [✓] Client 002   [✓] Client 003               │
│  [✓] Client 004   [ ] Client 005   [ ] Client 006               │
│                                                                  │
│  Connections to create: 6 bidirectional (12 total)              │
│                                                                  │
│  [▶ Create Mesh]                                                 │
│                                                                  │
│  ─────────────────────────────────────────────────────────────  │
│                                                                  │
│  Connection Matrix:                                              │
│                                                                  │
│          001   002   003   004                                   │
│    001    -    ✓✓    ✓✓    ✓✓                                   │
│    002   ✓✓     -    ✓✓    ⏳                                   │
│    003   ✓✓    ✓✓     -    ✓✓                                   │
│    004   ✓✓    ⏳    ✓✓     -                                   │
│                                                                  │
│  Progress: 10/12 connections established                        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 5.3 Bulk Operations

```
┌─────────────────────────────────────────────────────────────────┐
│  📦 BULK OPERATIONS                                              │
│─────────────────────────────────────────────────────────────────│
│                                                                  │
│  Create Multiple Clients:                                       │
│  ├── Quantity: [10]                                              │
│  ├── Prefix: [stress-test-]                                      │
│  ├── Auto-assign ports: ✓ (starting at 3041)                    │
│  └── Auto-start: ✓                                               │
│                                                                  │
│  [Create 10 Clients]                                            │
│                                                                  │
│  ─────────────────────────────────────────────────────────────  │
│                                                                  │
│  Bulk Actions:                                                   │
│  [▶ Start All]  [⏹ Stop All]  [🔄 Restart All]  [🗑️ Delete All] │
│                                                                  │
│  Select by Status:                                               │
│  [Select Online]  [Select Offline]  [Select Errored]            │
│                                                                  │
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

- Latency threshold alerts
- Delivery failure alerts
- Client offline alerts
- Anomaly detection

---

## 🔐 Phase 7: Enterprise Features (v0.5.0)

### 7.1 Multi-User Support

- User authentication
- Role-based access control
- Audit logging
- Per-user/team client ownership

### 7.2 REST API

- Full API for all features
- API authentication
- Rate limiting
- OpenAPI documentation

### 7.3 Production Deployment

- PostgreSQL support
- Redis clustering
- Kubernetes deployment
- High availability

---

## 📅 Version Timeline

| Version | Target | Focus | Status |
|---------|--------|-------|--------|
| 0.1.8 | Done | Real-Time Infrastructure | ✅ Complete |
| **0.2.0** | **2026-01-30** | **React UI + Architecture** | 🔄 Next |
| 0.2.5 | 2026-02-15 | Traffic Analysis Dashboard | 📋 Planned |
| **0.3.0** | **2026-03-01** | **Adversary View (Security Audit)** | 📋 Planned |
| 0.3.5 | 2026-03-15 | Advanced Test Panel | 📋 Planned |
| 0.4.0 | 2026-04-01 | Monitoring & Grafana | 📋 Planned |
| 0.5.0 | 2026-05-01 | Enterprise Features | 📋 Planned |
| 1.0.0 | 2026-06-01 | Production Ready | 📋 Future |

---

## 🛠️ Technology Stack (Final)

### Frontend (NEW)
| Component | Technology |
|-----------|------------|
| Framework | React 18 + TypeScript |
| Build Tool | Vite |
| Styling | Tailwind CSS |
| Routing | React Router v6 |
| State | Zustand + React Query |
| Charts | Recharts |
| Icons | Lucide React |
| WebSocket | Native + Custom Hook |

### Backend (Evolved)
| Component | Technology |
|-----------|------------|
| Framework | Django 5.x |
| API | Django REST Framework |
| WebSocket | Django Channels |
| Message Broker | Redis |
| Task Queue | Celery (planned) |
| Database | SQLite → PostgreSQL |
| Time-Series | InfluxDB (planned) |

### Infrastructure
| Component | Technology |
|-----------|------------|
| Containers | Docker |
| SimpleX CLI | simplex-chat in Docker |
| Network | Tor hidden services |
| Monitoring | Grafana (planned) |

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

## 🤝 Contributing

Priority areas for contribution:

| Area | Difficulty | Impact |
|------|------------|--------|
| React Component Library | Medium | High |
| Timing Correlation Algorithm | Hard | Very High |
| Traffic Visualization | Medium | High |
| Pattern Detection Engine | Hard | Very High |
| Grafana Dashboard Templates | Easy | Medium |
| Documentation & Tutorials | Easy | High |

---

*Last updated: 2025-12-28*
*Version: Roadmap v2.0*
*Author: cannatoshi*
