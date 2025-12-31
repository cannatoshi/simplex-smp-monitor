# 🐳 Docker Deployment

## Quick Start
```bash
# Clone the repository
git clone https://github.com/cannatoshi/simplex-smp-monitor.git
cd simplex-smp-monitor

# Copy environment file
cp .env.example .env

# Start all services
docker compose up -d
```

**That's it!** 🚀 Open http://localhost:8080

---

## Default Credentials

| Service | URL | Username | Password |
|---------|-----|----------|----------|
| **Web UI** | http://localhost:8080 | `admin` | `simplex123` |
| **Django Admin** | http://localhost:8080/admin/ | `admin` | `simplex123` |
| **Grafana** | http://localhost:3002 | `admin` | `simplex123` |
| **InfluxDB** | http://localhost:8086 | `admin` | `simplex123` |

> ⚠️ **Change these in production!** Edit `.env` before deploying.

---

## Services Overview

| Service | Container | Port | Purpose |
|---------|-----------|------|---------|
| **Nginx** | simplex-monitor-nginx | 8080 | Reverse Proxy + React |
| **App** | simplex-monitor-app | - | Django API |
| **PostgreSQL** | simplex-monitor-postgres | - | Database |
| **Redis** | simplex-monitor-redis | - | Cache |
| **InfluxDB** | simplex-monitor-influxdb | 8086 | Metrics |
| **Grafana** | simplex-monitor-grafana | 3002 | Dashboards |
| **Tor** | simplex-monitor-tor | - | .onion testing |

---

## Architecture
```
                    ┌─────────────────────────────────────┐
                    │            NGINX (:8080)            │
                    │   React SPA + Reverse Proxy         │
                    └──────────────┬──────────────────────┘
                                   │
              ┌────────────────────┼────────────────────┐
              │                    │                    │
              ▼                    ▼                    ▼
        ┌──────────┐        ┌──────────┐        ┌──────────┐
        │  React   │        │  Django  │        │  Admin   │
        │   SPA    │        │   API    │        │  Panel   │
        │   /*     │        │  /api/*  │        │ /admin/* │
        └──────────┘        └────┬─────┘        └──────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
         ▼                       ▼                       ▼
   ┌──────────┐           ┌──────────┐           ┌──────────┐
   │PostgreSQL│           │  Redis   │           │   Tor    │
   │    DB    │           │  Cache   │           │  Proxy   │
   └──────────┘           └──────────┘           └──────────┘
```

---

## Commands

### Start Services
```bash
docker compose up -d
```

### Stop Services
```bash
docker compose down
```

### View Logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f app
docker compose logs -f nginx
```

### Restart Service
```bash
docker compose restart app
docker compose restart nginx
```

### Rebuild After Code Changes
```bash
docker compose build
docker compose up -d
```

### Update to Latest Version
```bash
git pull
docker compose build --no-cache
docker compose up -d
```

### Full Reset (⚠️ Deletes All Data!)
```bash
docker compose down -v
docker compose up -d
```

---

## Configuration

### Custom Ports

Edit `.env`:
```bash
APP_PORT=9000      # Web UI
GRAFANA_PORT=3003  # Grafana
INFLUXDB_PORT=8087 # InfluxDB
```

### Production Settings
```bash
# Generate secure secret key
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Edit `.env`:
```bash
DEBUG=False
SECRET_KEY=your-generated-secret-key-here
ADMIN_PASSWORD=your-secure-password
POSTGRES_PASSWORD=another-secure-password
```

---

## Data Persistence

All data is stored in Docker volumes:

| Volume | Content |
|--------|---------|
| `simplex-monitor-postgres` | Database |
| `simplex-monitor-redis` | Cache |
| `simplex-monitor-influxdb-data` | Metrics |
| `simplex-monitor-grafana` | Dashboards |
| `simplex-monitor-app-data` | App data |
| `simplex-monitor-app-media` | Uploads |

### Backup Database
```bash
docker exec simplex-monitor-postgres pg_dump -U simplex simplex_monitor > backup.sql
```

### Restore Database
```bash
cat backup.sql | docker exec -i simplex-monitor-postgres psql -U simplex simplex_monitor
```

---

## Troubleshooting

### Container won't start
```bash
docker compose logs app
docker compose ps
```

### Port already in use
```bash
# Check what's using the port
sudo lsof -i :8080

# Use different port in .env
APP_PORT=9000
```

### Database connection error
```bash
docker compose logs postgres
docker compose restart postgres
```

### Reset admin password
```bash
docker compose exec app python manage.py changepassword admin
```

### Enter container shell
```bash
docker compose exec app /bin/bash
```

---

## Development vs Production

| | Development | Production (Docker) |
|---|-------------|---------------------|
| **Start** | `python manage.py runserver` | `docker compose up -d` |
| **Frontend** | `npm run dev` (hot reload) | Pre-built, served by Nginx |
| **Database** | SQLite | PostgreSQL |
| **Port** | 8000 / 3001 | 8080 |
| **Speed** | Slower (dev tools) | Faster (optimized) |

You can run **both simultaneously** for development!

---

## System Requirements

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| **RAM** | 2 GB | 4 GB |
| **Disk** | 5 GB | 10 GB |
| **Docker** | 20.10+ | Latest |
| **Docker Compose** | 2.0+ | Latest |

---

## Support

- **GitHub Issues:** https://github.com/cannatoshi/simplex-smp-monitor/issues
- **Documentation:** See README.md

---

*Built with 💜 for the SimpleX ecosystem*
