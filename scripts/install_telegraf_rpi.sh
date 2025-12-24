#!/bin/bash
# Telegraf Installation Script for Raspberry Pi
# Run this on your Raspberry Pi to enable server monitoring

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║     Telegraf Agent Installation for SimpleX Monitoring    ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check if running on Raspberry Pi / Debian
if [ ! -f /etc/debian_version ]; then
    echo -e "${RED}This script is designed for Debian-based systems.${NC}"
    exit 1
fi

# Get test system IP
read -p "Enter your Test System IP (where InfluxDB runs): " TEST_SYSTEM_IP

if [ -z "$TEST_SYSTEM_IP" ]; then
    echo -e "${RED}Test System IP is required!${NC}"
    exit 1
fi

# Install Telegraf
echo -e "${YELLOW}Adding InfluxData repository...${NC}"
wget -q https://repos.influxdata.com/influxdata-archive_compat.key
echo '393e8779c89ac8d958f81f942f9ad7fb82a25e133faddaf92e15b16e6ac9ce4c influxdata-archive_compat.key' | sha256sum -c
cat influxdata-archive_compat.key | gpg --dearmor | sudo tee /etc/apt/trusted.gpg.d/influxdata-archive_compat.gpg > /dev/null
echo 'deb [signed-by=/etc/apt/trusted.gpg.d/influxdata-archive_compat.gpg] https://repos.influxdata.com/debian stable main' | sudo tee /etc/apt/sources.list.d/influxdata.list
rm influxdata-archive_compat.key

echo -e "${YELLOW}Installing Telegraf...${NC}"
sudo apt-get update
sudo apt-get install -y telegraf

# Configure Telegraf
echo -e "${YELLOW}Configuring Telegraf...${NC}"

# Create config from template
sudo tee /etc/telegraf/telegraf.conf > /dev/null << EOF
# Telegraf Configuration for SimpleX Server Monitoring

[global_tags]
  host = "raspberry-pi"
  environment = "simplex"

[agent]
  interval = "10s"
  round_interval = true
  metric_batch_size = 1000
  metric_buffer_limit = 10000
  collection_jitter = "0s"
  flush_interval = "10s"
  flush_jitter = "0s"
  precision = "0s"
  hostname = ""
  omit_hostname = false

[[outputs.influxdb_v2]]
  urls = ["http://${TEST_SYSTEM_IP}:8086"]
  token = "simplex-test-suite-token-change-in-production"
  organization = "simplex"
  bucket = "metrics"
  timeout = "5s"

[[inputs.cpu]]
  percpu = true
  totalcpu = true
  collect_cpu_time = false
  report_active = false

[[inputs.mem]]

[[inputs.disk]]
  ignore_fs = ["tmpfs", "devtmpfs", "devfs", "iso9660", "overlay", "aufs", "squashfs"]

[[inputs.diskio]]

[[inputs.net]]
  interfaces = ["eth0", "wlan0"]
  ignore_protocol_stats = false

[[inputs.system]]

[[inputs.procstat]]
  pattern = "smp-server"
  prefix = "smp"

[[inputs.procstat]]
  pattern = "xftp-server"
  prefix = "xftp"

[[inputs.procstat]]
  pattern = "tor"
  prefix = "tor"

[[inputs.file]]
  files = ["/sys/class/thermal/thermal_zone0/temp"]
  name_override = "cpu_temperature"
  data_format = "value"
  data_type = "integer"

[[inputs.netstat]]

[[inputs.processes]]
EOF

# Enable and start Telegraf
echo -e "${YELLOW}Starting Telegraf service...${NC}"
sudo systemctl enable telegraf
sudo systemctl restart telegraf

# Check status
sleep 2
if sudo systemctl is-active --quiet telegraf; then
    echo -e "${GREEN}"
    echo "╔═══════════════════════════════════════════════════════════╗"
    echo "║              Telegraf installed successfully!             ║"
    echo "╚═══════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo ""
    echo "Metrics are now being sent to: http://${TEST_SYSTEM_IP}:8086"
    echo ""
    echo "You can check Telegraf status with:"
    echo "  sudo systemctl status telegraf"
    echo ""
    echo "View logs with:"
    echo "  sudo journalctl -u telegraf -f"
else
    echo -e "${RED}Telegraf failed to start. Check logs with:${NC}"
    echo "  sudo journalctl -u telegraf -e"
fi
