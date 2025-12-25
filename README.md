# SimpleX Test Suite

A comprehensive Django-based monitoring and testing dashboard for SimpleX SMP/XFTP servers. Built for managing private messaging infrastructure running on Raspberry Pi devices as Tor v3 hidden services.

![Server List](screenshots/serverlist.png)

## ✨ Features

### Server Management
- **Multi-Server Support** - Manage unlimited SMP and XFTP servers
- **7-Tab Configuration** - Basic, Monitoring, SSH, Control Port, Telegraf, SimpleX Config, Statistics
- **Connection Testing** - TLS handshake verification over Tor for .onion addresses
- **Test Persistence** - Results saved to database with latency tracking
- **Category System** - Organize servers with colored labels
- **Duplicate Detection** - Prevents adding same server twice
- **Drag & Drop Reordering** - Customize server display order

### Dashboard
- **Real-time Updates** - WebSocket-powered live status
- **Quick Actions** - Test, toggle, edit servers directly from cards
- **Dark Mode** - Full dark/light theme support
- **Bilingual** - English and German interface

### Extended Server Fields
- **SSH Access** - Remote management configuration
- **Control Port** - SimpleX server statistics via port 5224
- **Telegraf/InfluxDB** - Metrics collection setup
- **SLA Targets** - Define uptime and latency thresholds

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Tor (for .onion server testing)
- Git

### Installation
```bash
# Clone repository
git clone https://github.com/cannatosihi/simplex-test-suite.git
cd simplex-test-suite

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Start server
python manage.py runserver 0.0.0.0:8000
```

### With Tor Support (for .onion testing)
```bash
# Install Tor
sudo apt install tor

# Ensure Tor is running
sudo systemctl start tor

# Verify SOCKS proxy
curl --socks5 127.0.0.1:9050 https://check.torproject.org/api/ip
```

## 📁 Project Structure
```
simplex-test-suite/
├── core/                   # Django project settings
├── dashboard/              # Main dashboard app
├── servers/                # Server management app
│   ├── models.py          # Server & Category models
│   ├── views.py           # CRUD + test views
│   └── templatetags/      # Custom template filters
├── stresstests/           # Test execution app
├── events/                # Event logging app
├── templates/             # HTML templates
│   ├── base.html         # Base layout
│   ├── dashboard/        # Dashboard templates
│   └── servers/          # Server templates
├── static/               # CSS, JS assets
└── screenshots/          # Documentation images
```

## 🔧 Configuration

### Server Model Fields

| Field | Description |
|-------|-------------|
| `name` | Display name |
| `server_type` | SMP or XFTP |
| `address` | Full SimpleX URL (smp://fingerprint:password@host) |
| `location` | Physical location identifier |
| `priority` | Load balancing priority (1-10) |
| `is_active` | Include in monitoring |
| `maintenance_mode` | Temporarily exclude |
| `custom_timeout` | Override default timeout |
| `expected_uptime` | SLA target percentage |
| `max_latency` | SLA latency threshold (ms) |
| `ssh_host/port/user` | Remote SSH access |
| `control_port` | SimpleX control port (default: 5224) |
| `telegraf_enabled` | Enable metrics collection |

### Environment Variables
```bash
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,192.168.1.146
```

## 🧅 Tor Integration

The test suite automatically detects `.onion` addresses and routes connections through Tor:

- **Clearnet servers**: Direct TLS connection (30s timeout)
- **Onion servers**: SOCKS5 via 127.0.0.1:9050 (120s timeout)
```python
# Automatic detection in views.py
is_onion = '.onion' in host
if is_onion:
    sock.set_proxy(socks.SOCKS5, "127.0.0.1", 9050)
```

## 📊 Roadmap

See [ROADMAP.md](ROADMAP.md) for detailed development plans.

### Completed ✅
- Phase 1: Server Management & Dashboard

### In Progress 🔄
- Phase 2: Stress Testing Engine

### Planned 📋
- Phase 3: Telegraf/InfluxDB/Grafana Integration
- Phase 4: Alerts & Notifications
- Phase 5: Remote SSH Management
- Phase 6: REST API & Mobile Support

## 🛠️ Tech Stack

- **Backend**: Django 5.2, Daphne (ASGI), Channels
- **Frontend**: TailwindCSS, Alpine.js, HTMX
- **Database**: SQLite (default), PostgreSQL ready
- **WebSocket**: Django Channels with InMemory layer
- **Tor**: PySocks for SOCKS5 proxy

## 📝 License

MIT License - see [LICENSE](LICENSE) for details.

## 🤝 Contributing

Contributions welcome! Please read the roadmap first to see current priorities.

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📬 Contact

Part of the [SimpleX Private Infrastructure Tutorial](https://github.com/cannatosihi/simplex-private-infrastructure-tutorial) project.

---

**Built with ❤️ for the privacy community**
