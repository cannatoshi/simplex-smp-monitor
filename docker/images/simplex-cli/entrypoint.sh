#!/bin/bash
set -e
echo "=== SimpleX CLI Container Starting ==="
echo "External Port: ${SIMPLEX_PORT:-3030}"
echo "Tor: ${USE_TOR:-false}"
echo "ChutneX Mode: ${CHUTNEX_MODE:-0}"
echo "Profile: ${PROFILE_NAME:-bot}"

# Start Tor/SOCKS proxy based on mode
if [ "${USE_TOR}" = "true" ]; then
    if [ "${CHUTNEX_MODE}" = "1" ]; then
        # ChutneX Internal: Forward to ChutneX client node SOCKS
        # Find a ChutneX client node in the network
        CHUTNEX_SOCKS_HOST="${CHUTNEX_SOCKS_HOST:-}"
        
        if [ -z "${CHUTNEX_SOCKS_HOST}" ]; then
            # Try to find a chutnex client node via DNS
            # ChutneX client nodes are named like chutnex-<network>-client1
            for i in 1 2; do
                for host in chutnex-*-client${i}; do
                    if getent hosts "${host}" >/dev/null 2>&1; then
                        CHUTNEX_SOCKS_HOST="${host}"
                        break 2
                    fi
                done
            done
        fi
        
        if [ -z "${CHUTNEX_SOCKS_HOST}" ]; then
            # Fallback: Try to resolve via IP range (10.99.1.x)
            # Client1 is usually at .13, Client2 at .14
            CHUTNEX_SOCKS_HOST="10.99.1.13"
        fi
        
        echo "ChutneX Mode: Forwarding localhost:9050 -> ${CHUTNEX_SOCKS_HOST}:9050"
        socat TCP-LISTEN:9050,bind=127.0.0.1,fork,reuseaddr TCP:${CHUTNEX_SOCKS_HOST}:9050 &
        sleep 2
    else
        # Standard: Start local Tor
        echo "Starting Tor..."
        tor &
        sleep 5
    fi
fi

# Start simplex-chat on internal port 3030
CHAT_ARGS="-p 3030 -d /data"
if [ -n "${PROFILE_NAME}" ]; then
    CHAT_ARGS="${CHAT_ARGS} --create-bot-display-name ${PROFILE_NAME}"
fi

echo "Starting simplex-chat with: ${CHAT_ARGS}"
simplex-chat ${CHAT_ARGS} &

# Wait for simplex-chat to start
sleep 2

# Start socat to forward external port to internal 3030
echo "Starting socat: 0.0.0.0:${SIMPLEX_PORT:-3030} -> 127.0.0.1:3030"
exec socat TCP-LISTEN:${SIMPLEX_PORT:-3030},bind=0.0.0.0,fork,reuseaddr TCP:127.0.0.1:3030
