#!/bin/bash
set -e

echo "=== SimpleX CLI Container Starting ==="
echo "External Port: ${SIMPLEX_PORT:-3030}"
echo "Tor: ${USE_TOR:-false}"
echo "Profile: ${PROFILE_NAME:-bot}"

# Start Tor if enabled
if [ "${USE_TOR}" = "true" ]; then
    echo "Starting Tor..."
    tor &
    sleep 5
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
