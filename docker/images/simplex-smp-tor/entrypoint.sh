#!/bin/bash
# ============================================
# SimpleX SMP Server - Tor Hidden Service Entrypoint
# ============================================
set -e

echo "============================================"
echo "  SimpleX SMP Server - Tor Hidden Service"
echo "============================================"

# Ensure correct permissions for Tor
chown -R debian-tor:debian-tor /var/lib/tor /run/tor /var/log/tor 2>/dev/null || true
chmod 700 /var/lib/tor/simplex-smp 2>/dev/null || true

# Ensure simplex user owns its directories
chown -R simplex:simplex /etc/opt/simplex /var/opt/simplex /var/log/simplex 2>/dev/null || true

# Start Tor as debian-tor user in background
echo "🧅 Starting Tor daemon..."
su -s /bin/bash debian-tor -c "tor -f /etc/tor/torrc" &
TOR_PID=$!

# Wait for Tor to generate the .onion address
echo "⏳ Waiting for Tor Hidden Service..."
ONION_FILE="/var/lib/tor/simplex-smp/hostname"
MAX_WAIT=120
WAITED=0

while [ ! -f "$ONION_FILE" ] && [ $WAITED -lt $MAX_WAIT ]; do
    sleep 1
    WAITED=$((WAITED + 1))
    if [ $((WAITED % 10)) -eq 0 ]; then
        echo "   Still waiting for .onion address... (${WAITED}s)"
    fi
done

if [ ! -f "$ONION_FILE" ]; then
    echo "❌ ERROR: Tor failed to generate .onion address after ${MAX_WAIT}s"
    echo "Tor logs:"
    cat /var/log/tor/notices.log 2>/dev/null || echo "No tor logs found"
    exit 1
fi

ONION_ADDRESS=$(cat "$ONION_FILE")
echo "✅ Onion address generated: $ONION_ADDRESS"

# Initialize SMP server if not already done
# Use localhost since Tor handles the routing
if [ ! -f "/etc/opt/simplex/smp-server.ini" ]; then
    echo "🔧 Initializing SMP server for Tor..."
    
    # Initialize with localhost - Tor will handle external connections
    su -s /bin/bash simplex -c "smp-server init --ip 127.0.0.1 -l --yes"
    
    echo "✅ Server initialized!"
fi

# Disable HTTPS web interface (not needed for Tor)
CONFIG_FILE="/etc/opt/simplex/smp-server.ini"
if [ -f "$CONFIG_FILE" ]; then
    echo "🔧 Disabling HTTPS web interface..."
    sed -i 's/^https:/#https:/' "$CONFIG_FILE" 2>/dev/null || true
    sed -i 's/^cert:/#cert:/' "$CONFIG_FILE" 2>/dev/null || true
    sed -i 's/^key:/#key:/' "$CONFIG_FILE" 2>/dev/null || true
    echo "✅ HTTPS web interface disabled"
fi

# Get fingerprint
FINGERPRINT=""
if [ -f "/etc/opt/simplex/fingerprint" ]; then
    FINGERPRINT=$(cat /etc/opt/simplex/fingerprint)
fi

# Show server info
echo "============================================"
echo "🧅 Tor Hidden Service Active"
echo "============================================"
echo "📍 Onion Address: $ONION_ADDRESS"
if [ -n "$FINGERPRINT" ]; then
    echo "🔑 Fingerprint: $FINGERPRINT"
    echo "📡 Full SMP Address:"
    echo "   smp://$FINGERPRINT@$ONION_ADDRESS:5223"
fi
echo "============================================"

# Write onion address to a file for the monitor to read
echo "$ONION_ADDRESS" > /var/opt/simplex/onion_address
chown simplex:simplex /var/opt/simplex/onion_address

echo "🚀 Starting SMP Server..."

# Run SMP server as simplex user
exec su -s /bin/bash simplex -c "exec $*"
