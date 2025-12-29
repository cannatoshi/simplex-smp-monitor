# SimpleX SMP Monitor - Roadmap v2.1 for 2025/2026

## 🎯 Vision

**SimpleX SMP Monitor** is the world's first comprehensive security testing and infrastructure validation tool for SimpleX messaging infrastructure. It enables infrastructure operators / journalists, whistleblowers, NGOs, security researchers / to test their own SimpleX deployment with the same capabilities that external adversaries (including state-level actors) would have.

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

**Stack (v0.1.8):**
```
Frontend: Django Templates + HTMX + Alpine.js
Backend:  Django + Channels + Redis
Clients:  Docker containers (simplex-chat CLI)
Network:  Tor hidden services (.onion)
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
│                              │                                  │
│                    SimplexEventBridge                           │
│                              │                                  │
└─────────────────────────────────────────────────────────────────┘
           │                                    │
           ▼                                    ▼
┌─────────────────────┐              ┌─────────────────────┐
│  Docker Containers  │              │  Redis              │
│  (SimpleX CLI)      │              │  (Channel Layer)    │
└─────────────────────┘              └─────────────────────┘
```

---

### 2.2 React Project Setup

#### 2.2.1 Technology Stack
- [x] **Vite** - Fast build tool (not Create React App)
- [x] **React 18** - Latest React with concurrent features
- [x] **TypeScript** - Type safety throughout
- [x] **Tailwind CSS** - Utility-first styling
- [x] **React Router v6** - Client-side routing
- [x] **react-i18next** - Internationalization (DE/EN active)
- [x] **Lucide React** - Icon library
- [ ] **Zustand** - Lightweight state management
- [ ] **React Query** - Server state & caching
- [ ] **Recharts** - Charts and visualizations

#### 2.2.2 Project Structure
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
│   │   ├── ServerForm.tsx         # ✅ Migrated
│   │   ├── Clients.tsx            # ✅ Migrated
│   │   ├── ClientDetail.tsx       # ✅ Migrated
│   │   ├── ClientForm.tsx         # ✅ Migrated
│   │   ├── Categories.tsx         # ✅ Migrated
│   │   ├── Tests.tsx              # ⚠️ Placeholder only
│   │   └── Events.tsx             # ⚠️ Placeholder only
│   ├── i18n/
│   │   ├── index.ts               # ✅ i18n configuration
│   │   └── locales/
│   │       ├── de.json            # ✅ German translations
│   │       └── en.json            # ✅ English translations
│   ├── App.tsx                    # ✅ Router configuration
│   └── main.tsx                   # ✅ Entry point
├── vite.config.ts                 # ✅ Vite + Proxy config
├── tailwind.config.js             # ✅ Tailwind config
├── tsconfig.json                  # ✅ TypeScript config
└── package.json                   # ✅ Dependencies
```

#### 2.2.3 Django REST API Endpoints

**Servers API:** ✅ Complete
```
GET    /api/v1/servers/              # List all servers
POST   /api/v1/servers/              # Create server
GET    /api/v1/servers/{id}/         # Get server details
PUT    /api/v1/servers/{id}/         # Update server
DELETE /api/v1/servers/{id}/         # Delete server
POST   /api/v1/servers/{id}/test/    # Test server connection
```

**Clients API:** ✅ Complete
```
GET    /api/v1/clients/              # List all clients
POST   /api/v1/clients/              # Create client
GET    /api/v1/clients/{slug}/       # Get client details
PUT    /api/v1/clients/{slug}/       # Update client
DELETE /api/v1/clients/{slug}/       # Delete client
POST   /api/v1/clients/{slug}/start/ # Start container
POST   /api/v1/clients/{slug}/stop/  # Stop container
GET    /api/v1/clients/{slug}/logs/  # Get container logs
GET    /api/v1/clients/{slug}/connections/  # Get connections
```

**Messages API:** ✅ Complete (NEW in v0.1.9)
```
GET    /api/v1/messages/                     # List all messages
GET    /api/v1/messages/?client={uuid}       # Filter by client
GET    /api/v1/messages/?direction=sent      # Filter sent
GET    /api/v1/messages/?direction=received  # Filter received
```

**Dashboard API:** ✅ Complete
```
GET    /api/v1/dashboard/stats/      # Dashboard statistics
GET    /api/v1/dashboard/activity/   # Activity data
GET    /api/v1/dashboard/latency/    # Latency data
```

**Categories API:** ✅ Complete
```
GET    /api/v1/categories/           # List categories
```

**Connections API:** ✅ Complete
```
GET    /api/v1/connections/          # List connections
POST   /api/v1/connections/          # Create connection
DELETE /api/v1/connections/{id}/     # Delete connection
```

**Tests API:** ❌ Needs React Integration
```
GET    /api/v1/tests/                # List test runs
POST   /api/v1/tests/                # Create/start test
GET    /api/v1/tests/{id}/           # Get test details
POST   /api/v1/tests/{id}/stop/      # Stop running test
GET    /api/v1/tests/{id}/results/   # Get test results
```

**Events API:** ❌ Needs React Integration
```
GET    /api/v1/events/               # List events
GET    /api/v1/events/{id}/          # Get event details
```

---

### 2.3 Vite Proxy Configuration ✅

```typescript
// vite.config.ts - IMPLEMENTED
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3001,
    host: true,
    proxy: {
      '/api': { target: 'http://localhost:8000', changeOrigin: true },
      '/clients/messages/send/': { target: 'http://localhost:8000', changeOrigin: true },
      '/clients/connections/': { target: 'http://localhost:8000', changeOrigin: true },
      '^/clients/[a-z0-9-]+/connect/$': { target: 'http://localhost:8000', changeOrigin: true },
      '^/clients/[a-z0-9-]+/start/$': { target: 'http://localhost:8000', changeOrigin: true },
      '^/clients/[a-z0-9-]+/stop/$': { target: 'http://localhost:8000', changeOrigin: true },
      '^/clients/[a-z0-9-]+/restart/$': { target: 'http://localhost:8000', changeOrigin: true },
      '/ws': { target: 'ws://localhost:8000', ws: true },
    },
  },
})
```

---

### 2.4 Migration Progress

#### ✅ v0.1.9 - Part 1: Core Pages (COMPLETED)

| Task | Status |
|------|--------|
| Set up Vite + React project | ✅ Done |
| Configure Tailwind CSS | ✅ Done |
| Set up React Router | ✅ Done |
| Create Layout component | ✅ Done |
| Implement API service layer | ✅ Done |
| Add dark/light mode toggle | ✅ Done |
| Add language switcher (i18n) | ✅ Done |
| CSRF-exempt for HTMX views | ✅ Done |
| TestMessageViewSet API | ✅ Done |
| Migrate Dashboard page | ✅ Done |
| Migrate Servers list page | ✅ Done |
| Migrate Server detail page | ✅ Done |
| Migrate Server form page | ✅ Done |
| Migrate Clients list page | ✅ Done |
| Migrate Client detail page | ✅ Done |
| Migrate Client form page | ✅ Done |
| Migrate Categories page | ✅ Done |

#### 🔄 v0.2.0 - Part 2: Tests, Events & WebSocket (TODO)

| Task | Status |
|------|--------|
| Migrate Tests list page | ❌ Todo |
| Migrate Test detail page | ❌ Todo |
| Migrate Test form page | ❌ Todo |
| Migrate Events list page | ❌ Todo |
| Migrate Event detail page | ❌ Todo |
| Create useWebSocket hook | ❌ Todo |
| Integrate WebSocket in Clients | ❌ Todo |
| Live status updates without refresh | ❌ Todo |
| Add Zustand for state management | ❌ Todo |
| Add React Query for caching | ❌ Todo |
| Configure production build | ❌ Todo |
| Update deployment scripts | ❌ Todo |
| Remove legacy Django templates | ❌ Todo |

---

### 2.5 WebSocket Integration (Planned for v0.2.0)

```typescript
// Planned: useWebSocket hook
function useWebSocket(url: string) {
  const [status, setStatus] = useState<'connecting' | 'connected' | 'disconnected'>('connecting');
  const [lastMessage, setLastMessage] = useState<any>(null);
  
  useEffect(() => {
    const ws = new WebSocket(url);
    ws.onopen = () => setStatus('connected');
    ws.onclose = () => {
      setStatus('disconnected');
      // Auto-reconnect after 3 seconds
      setTimeout(() => reconnect(), 3000);
    };
    ws.onmessage = (e) => setLastMessage(JSON.parse(e.data));
    return () => ws.close();
  }, [url]);
  
  return { status, lastMessage };
}

// Usage in ClientDetail
function ClientDetail() {
  const { status, lastMessage } = useWebSocket('/ws/clients/');
  
  useEffect(() => {
    if (lastMessage?.type === 'client_stats') {
      // Update stats without page refresh
      setStats(lastMessage.payload);
    }
  }, [lastMessage]);
}
```

---

### 2.6 Development Workflow

```bash
# Development (two terminals)
# Terminal 1: Django backend
cd ~/simplex-smp-monitor
source .venv/bin/activate
python manage.py runserver 0.0.0.0:8000

# Terminal 2: React frontend
cd ~/simplex-smp-monitor/frontend
npm run dev  # Vite dev server on :3001

# Production build (planned)
cd frontend/
npm run build  # Creates dist/ folder
# Then serve via Django or separate web server
```

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

#### 3.3.2 Message Timeline
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

#### 3.3.3 Activity Heatmap
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

#### 3.3.4 Latency Distribution
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

#### 3.3.5 Packet Size Analysis
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
│     HIGH CONFIDENCE CORRELATION DETECTED                        │
│                                                                 │
│  An adversary observing both endpoints can determine with       │
│  94.7% confidence that Client A and Client B are communicating. │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### 4.4.3 Security Recommendations

```
┌─────────────────────────────────────────────────────────────────┐
│    SECURITY RECOMMENDATIONS                                     │
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
│  [ Generate Full Report]    [ Export PDF]    [ Re-analyze]      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 4.5 Technical Implementation

#### 4.5.1 Timing Correlation Algorithm

```python
class TimingCorrelator:
    """
    Implements timing correlation attack simulation.
    """
    
    def __init__(self, time_window_ms=5000):
        self.time_window = time_window_ms
        
    async def analyze(self, client_a_id, client_b_id, duration_minutes=60):
        cutoff = timezone.now() - timedelta(minutes=duration_minutes)
        
        sends = await TrafficEvent.objects.filter(
            client_id=client_a_id,
            direction='out',
            timestamp__gte=cutoff
        ).order_by('timestamp').values('timestamp', 'correlation_id')
        
        receives = await TrafficEvent.objects.filter(
            client_id=client_b_id,
            direction='in',
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
                        'probability': probability,
                    })
        
        return {
            'correlations': correlations,
            'overall_probability': self._aggregate_probability(correlations),
        }
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
        
        return patterns
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

| Test Type | Description | Use Case |
|-----------|-------------|----------|
| **Delivery Reliability** | Test message delivery across clients | Verify infrastructure |
| **Latency Benchmark** | Measure round-trip times | Performance tuning |
| **Stress Test** | High-volume message load | Capacity planning |
| **Mesh Connection** | Create full mesh between clients | Network testing |
| **Bulk Operations** | Create/manage many clients at once | Scale testing |

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
| 0.1.8 | 2025-12-27 | Real-Time Infrastructure | ✅ Complete |
| **0.1.9** | **2025-12-29** | **React Migration Part 1** (Core Pages) | ✅ **Complete** |
| **0.2.0** | **2026-01-15** | **React Migration Part 2** (Tests, Events, WebSocket) | 🔄 **Next** |
| 0.2.5 | 2026-02-01 | Traffic Analysis Dashboard | 📋 Planned |
| 0.3.0 | 2026-02-15 | Adversary View (Security Audit) | 📋 Planned |
| 0.3.5 | 2026-03-01 | Advanced Test Panel | 📋 Planned |
| 0.4.0 | 2026-03-15 | Monitoring & Grafana | 📋 Planned |
| 0.5.0 | 2026-04-01 | Enterprise Features | 📋 Planned |
| 1.0.0 | 2026-05-01 | Production Ready | 📋 Future |

---

## 🛠️ Technology Stack (Current)

### Frontend (v0.1.9)
| Component | Technology | Status |
|-----------|------------|--------|
| Framework | React 18 + TypeScript | ✅ Implemented |
| Build Tool | Vite 5.x | ✅ Implemented |
| Styling | Tailwind CSS 3.x | ✅ Implemented |
| Routing | React Router v6 | ✅ Implemented |
| State | useState + Props | ✅ Implemented |
| i18n | react-i18next | ✅ Implemented |
| Icons | Lucide React | ✅ Implemented |
| State Management | Zustand | 📋 Planned (v0.2.0) |
| Server State | React Query | 📋 Planned (v0.2.0) |
| WebSocket | Custom Hook | 📋 Planned (v0.2.0) |
| Charts | Recharts | 📋 Planned (v0.2.5) |

### Backend (Stable)
| Component | Technology | Status |
|-----------|------------|--------|
| Framework | Django 5.x | ✅ Stable |
| API | Django REST Framework | ✅ Stable |
| WebSocket | Django Channels | ✅ Stable |
| Message Broker | Redis 7.x | ✅ Stable |
| Task Queue | Celery | 📋 Planned |
| Database | SQLite → PostgreSQL | ✅ / 📋 |
| Time-Series | InfluxDB | 📋 Planned (v0.4.0) |

### Infrastructure
| Component | Technology | Status |
|-----------|------------|--------|
| Containers | Docker 24.x | ✅ Stable |
| SimpleX CLI | simplex-chat in Docker | ✅ Stable |
| Network | Tor hidden services | ✅ Stable |
| Monitoring | Grafana | 📋 Planned (v0.4.0) |

### Legacy (Deprecated)
| Component | Technology | Status |
|-----------|------------|--------|
| Frontend | Django Templates | ⚠️ Deprecated |
| Interactivity | HTMX + Alpine.js | ⚠️ Deprecated |
| i18n | Alpine.js $store | ⚠️ Deprecated |

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

| Area | Difficulty | Impact | Version |
|------|------------|--------|---------|
| Tests Page (React) | Medium | High | v0.2.0 |
| Events Page (React) | Medium | High | v0.2.0 |
| WebSocket React Hooks | Medium | High | v0.2.0 |
| Traffic Visualization | Hard | Very High | v0.2.5 |
| Timing Correlation Algorithm | Hard | Very High | v0.3.0 |
| Pattern Detection Engine | Hard | Very High | v0.3.0 |
| Grafana Dashboard Templates | Easy | Medium | v0.4.0 |
| Documentation & Tutorials | Easy | High | Ongoing |

---

*Last updated: 2025-12-29*
*Version: Roadmap v2.1*
*Author: cannatoshi*
