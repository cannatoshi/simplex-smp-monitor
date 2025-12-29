# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Planned
- Test Panel UI (React) for bulk messaging
- Events Page (React)
- WebSocket integration in React
- Mesh connections (all-to-all)
- Bulk client creation
- Traffic Analysis Dashboard
- Adversary View (Security Audit Mode)
- InfluxDB metrics integration
- Grafana dashboard templates
- Scheduled test runs

---

## [0.1.9-alpha] - 2025-12-29

### 🚀 MAJOR FEATURE: React SPA Migration

This release completely transforms the frontend from Django Templates + HTMX + Alpine.js to a modern **React Single Page Application** with TypeScript.

---

### ✨ Highlights

- **React 18 + TypeScript** - Modern, type-safe frontend architecture
- **Vite 5.x** - Fast HMR development server with optimized production builds
- **Tailwind CSS** - Utility-first styling with dark mode support
- **React Router v6** - Client-side routing with nested layouts
- **react-i18next** - Internationalization system (DE/EN active, 25+ prepared)
- **REST API** - Full Django REST Framework backend for all entities
- **Modular Components** - Reusable UI components with clean separation

---

### Added

#### 🆕 React Frontend (`frontend/`)

Complete React SPA replacing Django Templates:

**New Project Structure:**
```
frontend/
├── src/
│   ├── api/
│   │   └── client.ts              # Centralized API client
│   ├── components/
│   │   ├── layout/
│   │   │   └── Layout.tsx         # Header, Nav, Dark Mode, i18n
│   │   └── clients/
│   │       ├── ClientStats.tsx    # 4 Statistics cards
│   │       ├── ClientConnections.tsx
│   │       ├── ClientSidebar.tsx
│   │       └── ClientMessages.tsx
│   ├── pages/
│   │   ├── Dashboard.tsx
│   │   ├── Servers.tsx
│   │   ├── ServerDetail.tsx
│   │   ├── ServerForm.tsx
│   │   ├── Clients.tsx
│   │   ├── ClientDetail.tsx
│   │   ├── ClientForm.tsx
│   │   ├── Categories.tsx
│   │   ├── Tests.tsx
│   │   └── Events.tsx
│   ├── i18n/
│   │   ├── index.ts
│   │   └── locales/
│   │       ├── de.json
│   │       └── en.json
│   ├── App.tsx
│   └── main.tsx
├── vite.config.ts
├── tailwind.config.js
├── tsconfig.json
└── package.json
```

**Technology Stack:**

| Component | Technology |
|-----------|------------|
| Framework | React 18 |
| Language | TypeScript 5.x |
| Build Tool | Vite 5.x |
| Styling | Tailwind CSS 3.x |
| Routing | React Router v6 |
| i18n | react-i18next |
| Icons | Lucide React |
| HTTP Client | Fetch API |

---

#### 📡 New REST API Endpoints

**TestMessageViewSet** (`/api/v1/messages/`):
```
GET  /api/v1/messages/                    # List all messages
GET  /api/v1/messages/?client={uuid}      # Filter by client
GET  /api/v1/messages/?direction=sent     # Filter sent messages
GET  /api/v1/messages/?direction=received # Filter received messages
```

**Implementation (`clients/api/views.py`):**
```python
class TestMessageViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for test messages (read-only)"""
    queryset = TestMessage.objects.all()
    serializer_class = TestMessageSerializer
    
    def get_queryset(self):
        queryset = TestMessage.objects.all()
        client_id = self.request.query_params.get('client')
        direction = self.request.query_params.get('direction')
        
        if client_id:
            queryset = queryset.filter(
                Q(sender_id=client_id) | Q(recipient_id=client_id)
            )
        
        if direction == 'sent' and client_id:
            queryset = queryset.filter(sender_id=client_id)
        elif direction == 'received' and client_id:
            queryset = queryset.filter(recipient_id=client_id)
        
        return queryset.order_by('-created_at')[:50]
```

---

#### 🎨 Migrated Pages

| Page | Components | Features |
|------|------------|----------|
| **Dashboard** | Stats cards, Activity chart | Real-time statistics |
| **Servers** | List, Detail, Form | Full CRUD, Quick Test |
| **ServerDetail** | 7-tab interface | All server configuration |
| **ServerForm** | Multi-tab form | Create/Edit with validation |
| **Clients** | List with filters | Status badges, Actions |
| **ClientDetail** | Stats, Connections, Messages, Sidebar | Modular components |
| **ClientForm** | Two-column layout | SMP server multi-select |
| **Categories** | List view | Category management |

---

#### 🌐 Centralized API Client (`src/api/client.ts`)

Type-safe API client with all endpoints:

```typescript
// Base configuration
const API_BASE = '/api/v1';

// Type definitions
export interface SimplexClient {
  id: string;           // UUID (not number!)
  slug: string;
  name: string;
  profile_name: string;
  websocket_port: number;
  status: 'running' | 'stopped' | 'error' | 'starting';
  tor_enabled: boolean;
  smp_server_ids: number[];  // number[], not string[]
  messages_sent: number;
  messages_received: number;
  // ...
}

export interface TestMessage {
  id: string;
  direction?: 'sent' | 'received';
  sender: string;
  recipient: string;
  sender_name: string;
  recipient_name: string;
  content: string;
  delivery_status: 'pending' | 'sent' | 'delivered' | 'failed';
  total_latency_ms: number | null;  // null, not undefined!
  created_at: string;
}

// API methods
export const clientsApi = {
  list: () => apiFetch<SimplexClient[]>('/clients/'),
  get: (id: string) => apiFetch<SimplexClient>(`/clients/${id}/`),
  create: (data) => apiFetch('/clients/', { method: 'POST', body: data }),
  update: (id, data) => apiFetch(`/clients/${id}/`, { method: 'PUT', body: data }),
  delete: (id) => apiFetch(`/clients/${id}/`, { method: 'DELETE' }),
  start: (id) => apiFetch(`/clients/${id}/start/`, { method: 'POST' }),
  stop: (id) => apiFetch(`/clients/${id}/stop/`, { method: 'POST' }),
  restart: (id) => apiFetch(`/clients/${id}/restart/`, { method: 'POST' }),
};

export const messagesApi = {
  list: (clientId?: string, direction?: 'sent' | 'received') => 
    apiFetch<TestMessage[]>(`/messages/?client=${clientId}&direction=${direction}`)
      .then(r => Array.isArray(r) ? r : r.results),  // Handle pagination
};
```

---

#### 🔧 Vite Proxy Configuration

Selective proxy for API and HTMX action endpoints:

```typescript
// vite.config.ts
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
      // Dynamic client action paths
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

> **Important:** Do NOT proxy all `/clients/*` - this would break React Router!

---

#### 🌙 Dark Mode Implementation

```tsx
// Layout.tsx
const [darkMode, setDarkMode] = useState(() => {
  const saved = localStorage.getItem('darkMode');
  return saved ? JSON.parse(saved) : true;  // Default: dark
});

useEffect(() => {
  localStorage.setItem('darkMode', JSON.stringify(darkMode));
  document.documentElement.classList.toggle('dark', darkMode);
}, [darkMode]);
```

---

#### 🌐 i18n with react-i18next

```typescript
// src/i18n/index.ts
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import de from './locales/de.json';
import en from './locales/en.json';

i18n.use(initReactI18next).init({
  resources: { de: { translation: de }, en: { translation: en } },
  lng: localStorage.getItem('language') || 'de',
  fallbackLng: 'en',
});
```

**Usage in components:**
```tsx
import { useTranslation } from 'react-i18next';

function MyComponent() {
  const { t } = useTranslation();
  return <h1>{t('clients.title')}</h1>;
}
```

---

### Changed

#### CSRF-Exempt for HTMX Views

React frontend sends AJAX requests to legacy HTMX views. Added `@csrf_exempt` decorator:

```python
# clients/views.py
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

@method_decorator(csrf_exempt, name="dispatch")
class ClientConnectView(View):
    """Create connection between two clients"""
    ...

@method_decorator(csrf_exempt, name="dispatch")
class SendMessageView(View):
    """Send message to a contact"""
    ...

@method_decorator(csrf_exempt, name="dispatch")
class ConnectionDeleteView(View):
    """Delete a connection"""
    ...
```

---

#### TypeScript Type Corrections

**Critical Fix: Client IDs are UUIDs (strings), not integers!**

```typescript
// WRONG (v0.1.8 assumption):
interface SimplexClient {
  id: number;  // ❌
}
messagesApi.list(parseInt(id), "sent")  // ❌

// CORRECT (v0.1.9):
interface SimplexClient {
  id: string;  // UUID: "94a26ed4-eab2-42b9-b69b-3410bcfdb086"
}
messagesApi.list(id, "sent")  // ✓
```

**Other type fixes:**
- `smp_server_ids: number[]` (not `string[]`)
- `total_latency_ms: number | null` (not `number | undefined`)
- `direction?: 'sent' | 'received'` (optional field)

---

#### API Response Handling

REST API returns paginated responses:

```json
{
  "count": 8,
  "next": null,
  "previous": null,
  "results": [...]  // ← Actual data
}
```

**Solution in API client:**
```typescript
// Transform paginated response to array
.then(r => Array.isArray(r) ? r : r.results)
```

---

### Fixed

#### Vite Proxy Breaking React Routes

**Problem:** Proxying all `/clients/*` to Django broke React Router client-side navigation.

**Solution:** Use regex patterns for specific HTMX endpoints only:
```typescript
// ✓ Correct - specific paths
'^/clients/[a-z0-9-]+/connect/$': { target: 'http://localhost:8000' }

// ✗ Wrong - would break React Router
'/clients': { target: 'http://localhost:8000' }
```

---

#### Import Statement Position

**Problem:** Imports were accidentally placed inside docstring in `clients/views.py`.

**Solution:** Moved imports to line 23 after docstring closure.

---

### Technical Details

**New Files:**
```
frontend/
├── src/
│   ├── api/client.ts
│   ├── components/layout/Layout.tsx
│   ├── components/clients/ClientStats.tsx
│   ├── components/clients/ClientConnections.tsx
│   ├── components/clients/ClientSidebar.tsx
│   ├── components/clients/ClientMessages.tsx
│   ├── pages/Dashboard.tsx
│   ├── pages/Servers.tsx
│   ├── pages/ServerDetail.tsx
│   ├── pages/ServerForm.tsx
│   ├── pages/Clients.tsx
│   ├── pages/ClientDetail.tsx
│   ├── pages/ClientForm.tsx
│   ├── pages/Categories.tsx
│   ├── pages/Tests.tsx
│   ├── pages/Events.tsx
│   ├── i18n/index.ts
│   ├── i18n/locales/de.json
│   ├── i18n/locales/en.json
│   ├── App.tsx
│   └── main.tsx
├── vite.config.ts
├── tailwind.config.js
├── tsconfig.json
├── postcss.config.js
├── index.html
└── package.json

clients/api/
├── views.py          # Added TestMessageViewSet
└── urls.py           # Added messages router
```

**Modified Files:**
```
clients/views.py      # CSRF-exempt decorators, import fix
clients/api/views.py  # TestMessageViewSet
clients/api/urls.py   # messages/ endpoint
```

**New Dependencies (package.json):**
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.21.0",
    "react-i18next": "^14.0.0",
    "i18next": "^23.7.0",
    "lucide-react": "^0.303.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "@vitejs/plugin-react": "^4.2.0",
    "autoprefixer": "^10.4.0",
    "postcss": "^8.4.0",
    "tailwindcss": "^3.4.0",
    "typescript": "^5.3.0",
    "vite": "^5.0.0"
  }
}
```

---

### Installation / Upgrade

#### For New Installations

1. Install Node.js 18+:
```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
```

2. Install frontend dependencies:
```bash
cd ~/simplex-smp-monitor/frontend
npm install
```

3. Start both servers:
```bash
# Terminal 1: Django
python manage.py runserver 0.0.0.0:8000

# Terminal 2: Vite
cd frontend && npm run dev
```

4. Access React app at `http://YOUR_IP:3001`

#### For Upgrades from v0.1.8

1. Install Node.js 18+ (see above)
2. Pull latest changes: `git pull`
3. Install frontend: `cd frontend && npm install`
4. Start both servers as shown above

---

### Deprecated

#### Django Templates + HTMX + Alpine.js

The legacy frontend is still accessible at `http://localhost:8000/` but is no longer actively developed.

| Component | Status | Replacement |
|-----------|--------|-------------|
| Django Templates | Deprecated | React components |
| HTMX | Deprecated | React + Fetch API |
| Alpine.js | Deprecated | React hooks |
| Alpine.js $store i18n | Deprecated | react-i18next |
| static/js/i18n.js | Deprecated | src/i18n/index.ts |
| static/js/lang/*.json | Deprecated | src/i18n/locales/*.json |

---

### Known Issues

1. **WebSocket not integrated** - Real-time updates not yet in React (coming in v0.2.0)
2. **Tests page placeholder** - Full functionality planned for v0.2.0
3. **Events page placeholder** - Full functionality planned for v0.2.0

---

## [0.1.8-alpha] - 2025-12-27

### 🚀 MAJOR FEATURE: Real-Time Infrastructure

This release fundamentally transforms the application from polling-based to **real-time event-driven architecture**. The separate `listen_events` management command is replaced by an integrated WebSocket bridge that automatically starts with Django.

---

### ✨ Highlights

- **Redis Channel Layer** - Production-ready message broker replacing InMemoryChannelLayer
- **SimplexEventBridge** - Auto-connects to all running containers, processes events, pushes to browsers
- **WebSocket Consumers** - Browser connections for live updates without page refresh
- **Integrated Auto-Start** - No more manual `python manage.py listen_events`
- **Live Status Indicator** - Real-time connection status with detailed tooltip

---

### Added

#### 🔴 Redis Integration

Redis is now the backbone for real-time communication between components.

**Docker Container Setup:**
```bash
docker run -d \
  --name simplex-redis \
  --restart unless-stopped \
  -p 6379:6379 \
  -v simplex-redis-data:/data \
  redis:7-alpine redis-server --appendonly yes
```

**Django Configuration (`config/settings.py`):**
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

**New Dependency:**
```bash
pip install channels-redis
```

**Why Redis?**
| Feature | InMemoryChannelLayer | Redis |
|---------|---------------------|-------|
| Multi-process | ❌ No | ✅ Yes |
| Production-ready | ⚠️ Dev only | ✅ Yes |
| 50+ Clients | ❓ Maybe | ✅ Stable |
| Persistence | ❌ No | ✅ Optional |

---

#### 🌉 SimplexEventBridge (`clients/services/event_bridge.py`)

The core of the real-time system. Replaces the old `listen_events` management command.

**Architecture:**
```
┌──────────────────────────────────────────────────────────────────┐
│                    DJANGO + CHANNELS                             │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌─────────────────────────────────────────────────────────┐    │
│   │              SimplexEventBridge                         │    │
│   │   - Connects to ALL running containers                  │    │
│   │   - Listens for SimpleX events                          │    │
│   │   - Updates database                                    │    │
│   │   - Pushes to Browser Group "clients_all"               │    │
│   └─────────────────────────────────────────────────────────┘    │
│                              │                                   │
│                              ▼                                   │
│   ┌─────────────────────────────────────────────────────────┐    │
│   │              Channel Layer (Redis)                      │    │
│   └─────────────────────────────────────────────────────────┘    │
│                              │                                   │
│                              ▼                                   │
│   ┌─────────────────────────────────────────────────────────┐    │
│   │              ClientUpdateConsumer                       │    │
│   │   - Browser WebSocket endpoint                          │    │
│   │   - Receives: client_status, message_status, stats      │    │
│   │   - Sends JSON to frontend                              │    │
│   └─────────────────────────────────────────────────────────┘    │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

**Key Features:**
- **Auto-sync connections** - Checks every 5 seconds for new/stopped clients
- **Reconnection handling** - Automatic reconnect on connection loss
- **Event processing** - Handles `newChatItems` and `chatItemsStatusesUpdated`
- **Database updates** - Updates message status and client statistics
- **Channel Layer push** - Broadcasts to all connected browsers

**Event Types Processed:**

| SimpleX Event | Action | Browser Event |
|---------------|--------|---------------|
| `newChatItems` | Mark message delivered, update counters | `new_message`, `client_stats` |
| `chatItemsStatusesUpdated` | Mark as delivered, calculate latency | `message_status` |

---

#### 📡 WebSocket Consumers (`clients/consumers.py`)

Two consumers for different use cases:

**ClientUpdateConsumer** (`/ws/clients/`)
- For the client list page
- Receives updates for ALL clients
- Group: `clients_all`

**ClientDetailConsumer** (`/ws/clients/<slug>/`)
- For individual client detail pages
- Receives updates for specific client + global updates
- Groups: `client_<slug>` + `clients_all`

**Supported Event Types:**
```python
async def client_status(self, event):
    """Client status changed (running/stopped/error)"""
    
async def client_stats(self, event):
    """Message counters updated"""
    
async def message_status(self, event):
    """Delivery status changed (sent/delivered/failed)"""
    
async def new_message(self, event):
    """New message received by a client"""
    
async def container_log(self, event):
    """Container log line (detail page only)"""
```

---

#### 🔌 WebSocket Routing (`clients/routing.py`)

```python
websocket_urlpatterns = [
    re_path(r'ws/clients/$', consumers.ClientUpdateConsumer.as_asgi()),
    re_path(r'ws/clients/(?P<client_slug>[\w-]+)/$', consumers.ClientDetailConsumer.as_asgi()),
]
```

---

#### ⚡ Auto-Start via AppConfig (`clients/apps.py`)

The Event Bridge now starts automatically with Django - no manual command needed!

```python
class ClientsConfig(AppConfig):
    name = 'clients'
    
    def ready(self):
        if os.environ.get('RUN_MAIN') == 'true':
            self._start_bridge_thread()
    
    def _start_bridge_thread(self):
        def run_bridge():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(start_event_bridge())
        
        thread = threading.Thread(target=run_bridge, daemon=True)
        thread.start()
```

**Server Output on Start:**
```
🚀 APScheduler gestartet - prüft alle 30 Sekunden
✅ APScheduler gestartet - Monitoring läuft!
INFO 🌉 Event Bridge thread started
INFO 🌉 Starting Event Bridge in background thread...
INFO 🚀 SimplexEventBridge starting...
INFO ✓ Connected to Client 001
INFO ✓ Connected to Client 002
INFO ✓ Connected to Client 003
INFO   📡 Listening: Client 001 (ws://localhost:3031)
INFO   📡 Listening: Client 002 (ws://localhost:3032)
INFO   📡 Listening: Client 003 (ws://localhost:3033)
```

---

#### 🖥️ Frontend WebSocket Client (`static/js/clients-live.js`)

A complete JavaScript WebSocket client with:

**Features:**
- Auto-connect on page load
- Auto-reconnect on disconnect (3 second delay)
- Event handlers for all message types
- Live DOM updates without page refresh
- Toast notifications for new messages
- Uptime tracking
- Connection status indicator

**Usage:**
```javascript
// Auto-initialized on DOMContentLoaded
window.clientsWS = new ClientsWebSocket();

// Manual event handlers
window.clientsWS.on('new_message', (data) => {
    console.log('New message:', data);
});

// Send commands
window.clientsWS.send({ action: 'ping' });
```

**Built-in DOM Updates:**
- `.status-badge` - Client status badges
- `.stat-sent` / `.stat-received` - Message counters
- `.message-status` - Delivery status icons
- `.message-latency` - Latency values
- `#ws-status` - Connection indicator

---

#### 🟢 Live Status Indicator

Visual indicator in the navigation bar showing real-time connection status:

**States:**
| State | Indicator | Text |
|-------|-----------|------|
| Connected | 🟢 Green dot | "Live" |
| Disconnected | 🔴 Pulsing red | "Reconnecting..." |

**Tooltip Information (on hover):**
- WebSocket: Connected/Disconnected
- Event Bridge: Running
- Listening to: X Clients
- Channel Layer: Redis
- Last Event: 📨 New Message
- Connected: 5m 23s (live counter)

---

### Changed

#### ASGI Configuration (`config/asgi.py`)

Updated to include WebSocket routing:

```python
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from clients.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})
```

#### Logging Configuration

Added logging for real-time components:

```python
LOGGING = {
    'loggers': {
        'clients': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'clients.services.event_bridge': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    },
}
```

---

### Deprecated

#### `listen_events` Management Command

The separate `python manage.py listen_events` command is now **deprecated**. The Event Bridge starts automatically with Django.

**Old Way (v0.1.7):**
```bash
# Terminal 1
python manage.py runserver 0.0.0.0:8000

# Terminal 2 (separate process!)
python manage.py listen_events
```

**New Way (v0.1.8):**
```bash
# Single command - everything starts automatically!
python manage.py runserver 0.0.0.0:8000
```

The old command still works but is no longer needed.

---

### 🎨 Secondary Feature: UI/UX Improvements

In addition to the real-time infrastructure, the Client Detail page received a visual overhaul:

#### 4-Corner Stats Cards

Redesigned statistics display with corner-based layout:

| Card | Corners (TL, TR, BL, BR) | Center |
|------|--------------------------|--------|
| Status | Port, Uptime, Connections, Profile | 🟢 Running |
| Messages | Delivered, Failed, Pending, Last | Sent \| Received |
| Success Rate | Today, Total, -, Progress Bar | 100.0% |
| Latency | Min, Max, -, Sparkline | Ø 663ms |

#### AJAX Messaging System

Send messages without page reload:
- Fetch API with XMLHttpRequest header
- JsonResponse for AJAX requests
- Instant feedback with success/error messages
- Live stats update after send
- Slide-in animation for new messages

#### AJAX Connection Management

- Create connections asynchronously
- Delete with slide-out animation
- Smart button shows "(no more clients)" when all connected

#### Live SMP Server Status LEDs

- 🟢 Pulsing green for online servers (animate-ping)
- 🔴 Red for offline/error
- ⚪ Gray for unknown

#### Equal Height Layout

Sidebar and content always match heights using CSS Grid + Flexbox.

---

### Fixed

#### URL Routing Order (Critical)

**Problem:** `<slug:slug>/` was matching before `messages/send/`, causing 404 errors.

**Solution:** Specific routes now come BEFORE generic slug routes in `clients/urls.py`:

```python
urlpatterns = [
    # === SPECIFIC ROUTES FIRST ===
    path('messages/send/', views.SendMessageView.as_view(), name='send_message'),
    path('connections/create/', views.ConnectionCreateView.as_view(), name='connection_create'),
    
    # === GENERIC ROUTES LAST ===
    path('<slug:slug>/', views.ClientDetailView.as_view(), name='detail'),
]
```

#### SendMessageView AJAX Response

**Problem:** View returned `HttpResponseRedirect` for all requests.
**Solution:** Checks `X-Requested-With` header, returns `JsonResponse` for AJAX.

#### SMP Server LEDs

**Problem:** Template checked `server.is_online` (doesn't exist).
**Solution:** Changed to `server.last_status == 'online'`.

---

### Technical Details

**New Files:**
```
clients/
├── consumers.py                    # WebSocket consumers
├── routing.py                      # WebSocket URL patterns
├── services/
│   └── event_bridge.py             # SimplexEventBridge
└── apps.py                         # Updated with auto-start

config/
└── asgi.py                         # Updated with Channels routing

static/
└── js/
    └── clients-live.js             # Frontend WebSocket client
```

**Modified Files:**
```
config/settings.py                  # Redis Channel Layer, Logging
clients/templates/clients/detail.html
clients/templates/clients/partials/_stats.html
clients/templates/clients/partials/_sidebar.html
clients/views.py                    # AJAX support
clients/urls.py                     # Route ordering
templates/base.html                 # Live status indicator
```

**New Dependencies:**
```
channels-redis>=4.0
redis>=4.6
```

---

### Installation / Upgrade

#### For New Installations

1. Start Redis:
```bash
docker run -d \
  --name simplex-redis \
  --restart unless-stopped \
  -p 6379:6379 \
  -v simplex-redis-data:/data \
  redis:7-alpine redis-server --appendonly yes
```

2. Install dependencies:
```bash
pip install channels-redis
```

3. Update `config/settings.py` with Redis Channel Layer config.

4. Start server (Event Bridge starts automatically):
```bash
python manage.py runserver 0.0.0.0:8000
```

#### For Upgrades from v0.1.7

1. Start Redis container (see above)
2. Install channels-redis: `pip install channels-redis`
3. Update settings.py with Redis config
4. Copy new files (consumers.py, routing.py, event_bridge.py, clients-live.js)
5. Update asgi.py and apps.py
6. Stop the old `listen_events` process (no longer needed!)
7. Restart Django server

---

### Known Issues

1. **Bridge status in tooltip** - "Listening to X Clients" requires additional endpoint (shows 0)
2. **Stats don't auto-refresh on list page** - Only detail page receives live updates
3. **Toast notifications stack** - Multiple rapid messages can overlap

---

## [0.1.7-alpha] - 2025-12-27

### 🎉 Major Feature: SimpleX CLI Clients

This release introduces comprehensive Docker-based test client infrastructure for end-to-end message delivery testing across your SimpleX SMP servers.

### Added

#### Docker Container Management
- **Dockerfile.simplex-cli** - Custom Docker image based on `debian:bookworm-slim`
- **entrypoint.sh** - Container entrypoint with optional Tor support
- **docker_manager.py** - Python service for container lifecycle management
- Start/Stop/Restart/Delete controls via Web UI
- Volume management for persistent client data (`simplex-client-{slug}-data`)
- Health checks for container status monitoring
- Bridge networking with individual port mapping (3031-3080)

#### WebSocket Command Service
- **simplex_commands.py** - Synchronous command service for Django views
- `SimplexCommandService` class with singleton pattern
- Correlation ID based request/response matching (async WebSocket → sync API)
- Commands implemented:
  - `create_address()` - Create invitation link
  - `get_address()` - Retrieve existing address
  - `create_or_get_address()` - Smart address handling
  - `connect_via_link()` - Connect to another client
  - `get_contacts()` - List all contacts
  - `enable_auto_accept()` - Enable auto-accept for incoming requests
  - `send_message()` - Send message to contact

#### Client Connections
- **ClientConnection model** - Track bidirectional connections between clients
- `contact_name_on_a` / `contact_name_on_b` - Store how clients see each other
- Auto-Accept feature for seamless connection establishment
- Connection status tracking (pending/connected/disconnected)
- UI modal for creating new connections

#### Delivery Receipt Tracking
- **listen_events management command** - Background WebSocket event listener
- Event types handled:
  - `newChatItems` - Incoming messages
  - `chatItemsStatusesUpdated` - Delivery confirmations
- Status progression:
  - ⏳ `pending` - Message being sent
  - ✓ `sent` - Server acknowledged receipt
  - ✓✓ `delivered` - Recipient client received
  - ✗ `failed` - Delivery failed
- Latency measurement in milliseconds
- Async Django DB access via `sync_to_async`

#### UI Improvements
- **Client List View** - Cards with status indicators, message stats
- **Client Detail View** - Connections, messaging, logs
- **Table-based Message Layout** - Three tabs (Sent/Received/All)
- **Status Icons** - Visual indicators for message status
- **Latency Display** - Per-message delivery time
- **Quick Send Form** - Send messages directly from detail page

### Fixed
- **Container Deletion Bug** - Docker containers now properly removed when deleting clients
- **Django 4+ DeleteView** - Changed from `delete()` to `post()` method for compatibility
- **Auto-Accept Order** - Must be called after address creation, not before
- **Container Lookup** - Added fallback to container name if ID lookup fails
- **Template Grid Layout** - Fixed sidebar positioning in client detail view

### Performance

Tested on **Raspberry Pi 5** (8GB RAM, 128GB NVMe SSD, Debian 12):

| Clients | RAM Usage | CPU (idle) | Status |
|---------|-----------|------------|--------|
| 6 | ~400 MB | <5% | ✅ Stable |
| 10 | ~650 MB | <10% | ✅ Stable |
| 20 | ~1.2 GB | <15% | ✅ Stable |
| 50 | ~3 GB | <25% | ⚠️ Tested |

---

## [0.1.6-alpha] - 2025-12-26

### Added
- **Multi-Type Test System** - Monitoring, Stress, and Latency tests with dedicated workflows
- **APScheduler Integration** - Automated test execution with configurable intervals
- **i18n Translation System** - Alpine.js `$store.i18n` with JSON language files
- **Language Files** - `static/js/i18n/en.json`, `de.json` (25 languages prepared)
- **timeAgo() Function** - Relative time display (e.g., "2 minutes ago")
- **Live Countdown Timer** - Real-time test progress with Alpine.js reactivity
- **Onion/ClearNet Badges** - Visual indicators in test results table
- **Dynamic Grafana Links** - Auto-detect server IP instead of localhost
- **Language Switcher** - EN/DE toggle in navigation header

### Changed
- Complete test system refactor with new models (TestRun, TestResult, ServerStats)
- Symmetric 4-tile monitoring dashboard layout
- Test detail pages redesigned for each test type

### Fixed
- Success rate calculation now capped at 100% (was showing 140%+)
- Grafana links now use actual server IP instead of localhost

---

## [0.1.5-alpha] - 2025-12-25

### Added
- **7-Tab Server Form** - Basic, Monitoring, SSH, Control Port, Telegraf, SimpleX Config, Statistics
- **Extended Server Model** - SSH, Control Port, Telegraf, SLA fields
- **Test Result Persistence** - Connection tests save to database on form submit
- **Card Quick Test** - ⚡ button with immediate database update
- **Category System** - Colored labels for server organization
- **Template Tags** - Fingerprint/password extraction from address

### Fixed
- Host property setter error (was read-only property)
- Category views and URLs restored after accidental removal

---

## [0.1.4-alpha] - 2025-12-24

### Added
- **UI Redesign** - Professional dark/light mode with Tailwind CSS
- **Bilingual Support** - English/German language toggle (persists in localStorage)
- **Connection Testing** - Real-time server connectivity tests with latency measurement
- **Tor Integration** - Automatic .onion detection, tests via SOCKS5 proxy
- **Duplicate Detection** - Warning when adding duplicate server addresses
- **Drag & Drop** - Reorder servers visually
- **Status Persistence** - Test results saved with server (Online/Offline/Error)
- **ONION Badge** - Visual indicator for Tor hidden services

### Changed
- Renamed project from "SimpleX Test Suite" to "SimpleX SMP Monitor"
- Complete UI overhaul with Tailwind CSS

---

## [0.1.0-alpha] - 2025-12-23

### Added
- 🎉 **Initial Project Structure**
- Django 5.x project setup with ASGI support
- Server management (CRUD operations)
- Dashboard with statistics overview
- Event logging system
- Docker Compose stack (InfluxDB, Grafana, Telegraf)
- HTMX + Alpine.js frontend
- Basic Tailwind CSS styling

---

## Version History

| Version | Date | Highlights |
|---------|------|------------|
| 0.1.9-alpha | 2025-12-29 | **React SPA Migration**: React 18, TypeScript, Vite, Tailwind |
| 0.1.8-alpha | 2025-12-27 | **Real-Time Infrastructure**: Redis, WebSocket, Event Bridge |
| 0.1.7-alpha | 2025-12-27 | CLI Clients, Docker, Delivery Receipts |
| 0.1.6-alpha | 2025-12-26 | Multi-type tests, i18n, APScheduler |
| 0.1.5-alpha | 2025-12-25 | 7-tab form, categories, quick test |
| 0.1.4-alpha | 2025-12-24 | UI redesign, Tor testing, bilingual |
| 0.1.0-alpha | 2025-12-23 | Initial release |

---

[Unreleased]: https://github.com/cannatoshi/simplex-smp-monitor/compare/v0.1.9-alpha...HEAD
[0.1.9-alpha]: https://github.com/cannatoshi/simplex-smp-monitor/compare/v0.1.8-alpha...v0.1.9-alpha
[0.1.8-alpha]: https://github.com/cannatoshi/simplex-smp-monitor/compare/v0.1.7-alpha...v0.1.8-alpha
[0.1.7-alpha]: https://github.com/cannatoshi/simplex-smp-monitor/compare/v0.1.6-alpha...v0.1.7-alpha
[0.1.6-alpha]: https://github.com/cannatoshi/simplex-smp-monitor/compare/v0.1.5-alpha...v0.1.6-alpha
[0.1.5-alpha]: https://github.com/cannatoshi/simplex-smp-monitor/compare/v0.1.4-alpha...v0.1.5-alpha
[0.1.4-alpha]: https://github.com/cannatoshi/simplex-smp-monitor/compare/v0.1.0-alpha...v0.1.4-alpha
[0.1.0-alpha]: https://github.com/cannatoshi/simplex-smp-monitor/releases/tag/v0.1.0-alpha
