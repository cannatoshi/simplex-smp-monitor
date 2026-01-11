#!/bin/bash
# ============================================
# SimpleX SMP Server - Entrypoint
# ============================================
set -e

echo "============================================"
echo "  SimpleX SMP Server - Docker"
echo "============================================"

# Use ADDR environment variable or default to 0.0.0.0
SERVER_ADDR="${ADDR:-0.0.0.0}"
echo "📍 Server Address: $SERVER_ADDR"

# Initialize server if not already done
if [ ! -f "/etc/opt/simplex/smp-server.ini" ]; then
    echo "🔧 Initializing SMP server..."
    
    # Initialize with the correct IP address
    if [ "$SERVER_ADDR" = "0.0.0.0" ]; then
        smp-server init --ip "$SERVER_ADDR" -l --yes
    else
        smp-server init --ip "$SERVER_ADDR" -l --yes
    fi
    
    echo "✅ Server initialized!"
fi

# Disable HTTPS web interface if WEB_MANUAL=1 or no certs exist
CONFIG_FILE="/etc/opt/simplex/smp-server.ini"
if [ -f "$CONFIG_FILE" ]; then
    # Check if WEB_MANUAL mode is enabled OR if certificates don't exist
    if [ "$WEB_MANUAL" = "1" ] || [ ! -f "/etc/opt/simplex/web.crt" ]; then
        echo "🔧 Disabling HTTPS web interface..."
        
        # Comment out the HTTPS-related lines in [WEB] section
        # This prevents the "no HTTPS credentials" error
        sed -i 's/^https:/#https:/' "$CONFIG_FILE" 2>/dev/null || true
        sed -i 's/^cert:/#cert:/' "$CONFIG_FILE" 2>/dev/null || true
        sed -i 's/^key:/#key:/' "$CONFIG_FILE" 2>/dev/null || true
        
        echo "✅ HTTPS web interface disabled"
    fi
fi

# Show server info
if [ -f "/etc/opt/simplex/fingerprint" ]; then
    FINGERPRINT=$(cat /etc/opt/simplex/fingerprint)
    echo "🔑 Fingerprint: $FINGERPRINT"
    echo "📡 Server address: smp://$FINGERPRINT@$SERVER_ADDR:5223"
fi

echo "🚀 Starting SMP Server..."
echo "============================================"

# Execute the command
exec "$@"