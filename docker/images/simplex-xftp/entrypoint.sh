#!/bin/bash
# ============================================
# SimpleX XFTP Server - Entrypoint
# ============================================

set -e

echo "============================================"
echo "  SimpleX XFTP Server - Docker"
echo "============================================"

# Initialize server if not already done
if [ ! -f "/etc/opt/simplex-xftp/xftp-server.ini" ]; then
    echo "🔧 Initializing XFTP server..."
    xftp-server init --ip 0.0.0.0 -l -p /var/opt/simplex-xftp -q 10gb
    echo "✅ Server initialized!"
fi

echo "🚀 Starting XFTP Server..."
echo "============================================"

# Execute the command
exec "$@"
