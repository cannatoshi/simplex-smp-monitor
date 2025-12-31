#!/bin/bash
# ============================================
# SimpleX SMP Server - Entrypoint
# ============================================

set -e

echo "============================================"
echo "  SimpleX SMP Server - Docker"
echo "============================================"

# Initialize server if not already done
if [ ! -f "/etc/opt/simplex/smp-server.ini" ]; then
    echo "🔧 Initializing SMP server..."
    smp-server init --ip 0.0.0.0 -l --yes
    echo "✅ Server initialized!"
fi

echo "🚀 Starting SMP Server..."
echo "============================================"

# Execute the command
exec "$@"
