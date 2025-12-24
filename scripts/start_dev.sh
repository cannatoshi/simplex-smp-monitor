#!/bin/bash
# SimpleX Test Suite - Development Startup Script

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║           SimpleX Reliability Test Suite                  ║"
echo "║              i(N) cOD(E) w(E) tRUS(T)                     ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check Python venv
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv .venv
fi

source .venv/bin/activate

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
pip install -q -r requirements.txt

# Run migrations
echo -e "${YELLOW}Running migrations...${NC}"
python manage.py migrate --no-input

# Check Docker
if command -v docker &> /dev/null; then
    if ! docker ps | grep -q simplex-influxdb; then
        echo -e "${YELLOW}Starting InfluxDB and Grafana...${NC}"
        docker-compose up -d
        echo -e "${GREEN}Waiting for services to start...${NC}"
        sleep 5
    else
        echo -e "${GREEN}InfluxDB and Grafana already running${NC}"
    fi
else
    echo -e "${YELLOW}Docker not found. InfluxDB/Grafana not started.${NC}"
    echo -e "${YELLOW}Metrics will be logged but not persisted.${NC}"
fi

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Starting Django development server...${NC}"
echo ""
echo -e "  ${BLUE}Django:${NC}   http://localhost:8000"
echo -e "  ${BLUE}Grafana:${NC}  http://localhost:3000  (admin/simplextest123)"
echo -e "  ${BLUE}InfluxDB:${NC} http://localhost:8086  (admin/simplextest123)"
echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo ""

# Start Django with ASGI (for WebSocket support)
python manage.py runserver 0.0.0.0:8000
