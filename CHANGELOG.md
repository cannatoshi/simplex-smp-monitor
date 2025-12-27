# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Planned
- Test Panel UI for bulk messaging
- Mesh connections (all-to-all)
- Bulk client creation
- InfluxDB metrics integration
- Grafana dashboard templates
- Scheduled test runs

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
│                    DJANGO + CHANNELS                              │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│   ┌─────────────────────────────────────────────────────────┐    │
│   │              SimplexEventBridge                          │    │
│   │   - Connects to ALL running containers                   │    │
│   │   - Listens for SimpleX events                           │    │
│   │   - Updates database                                     │    │
│   │   - Pushes to Browser Group "clients_all"                │    │
│   └─────────────────────────────────────────────────────────┘    │
│                              │                                    │
│                              ▼                                    │
│   ┌─────────────────────────────────────────────────────────┐    │
│   │              Channel Layer (Redis)                       │    │
│   └─────────────────────────────────────────────────────────┘    │
│                              │                                    │
│                              ▼                                    │
│   ┌─────────────────────────────────────────────────────────┐    │
│   │              ClientUpdateConsumer                        │    │
│   │   - Browser WebSocket endpoint                           │    │
│   │   - Receives: client_status, message_status, stats       │    │
│   │   - Sends JSON to frontend                               │    │
│   └─────────────────────────────────────────────────────────┘    │
│                                                                   │
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
| 0.1.8-alpha | 2025-12-27 | **Real-Time Infrastructure**: Redis, WebSocket, Event Bridge |
| 0.1.7-alpha | 2025-12-27 | CLI Clients, Docker, Delivery Receipts |
| 0.1.6-alpha | 2025-12-26 | Multi-type tests, i18n, APScheduler |
| 0.1.5-alpha | 2025-12-25 | 7-tab form, categories, quick test |
| 0.1.4-alpha | 2025-12-24 | UI redesign, Tor testing, bilingual |
| 0.1.0-alpha | 2025-12-23 | Initial release |

---

[Unreleased]: https://github.com/cannatoshi/simplex-smp-monitor/compare/v0.1.8-alpha...HEAD
[0.1.8-alpha]: https://github.com/cannatoshi/simplex-smp-monitor/compare/v0.1.7-alpha...v0.1.8-alpha
[0.1.7-alpha]: https://github.com/cannatoshi/simplex-smp-monitor/compare/v0.1.6-alpha...v0.1.7-alpha
[0.1.6-alpha]: https://github.com/cannatoshi/simplex-smp-monitor/compare/v0.1.5-alpha...v0.1.6-alpha
[0.1.5-alpha]: https://github.com/cannatoshi/simplex-smp-monitor/compare/v0.1.4-alpha...v0.1.5-alpha
[0.1.4-alpha]: https://github.com/cannatoshi/simplex-smp-monitor/compare/v0.1.0-alpha...v0.1.4-alpha
[0.1.0-alpha]: https://github.com/cannatoshi/simplex-smp-monitor/releases/tag/v0.1.0-alpha
