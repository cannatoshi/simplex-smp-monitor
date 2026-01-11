#!/bin/bash
# ============================================
# SimpleX NTF Server - Entrypoint
# ============================================

set -e

echo "============================================"
echo "  SimpleX NTF Server - Docker"
echo "============================================"

# Initialize server if not already done
if [ ! -f "/etc/opt/simplex-notifications/ntf-server.ini" ]; then
    echo "🔧 Initializing NTF server..."
    ntf-server init --ip 0.0.0.0 -l
    echo "✅ Server initialized!"
fi

echo "🚀 Starting NTF Server..."
echo "============================================"

# Execute the command
exec "$@"
