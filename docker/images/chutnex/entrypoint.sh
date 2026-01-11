#!/bin/bash
# ============================================================================
# ChutneX - Private Tor Network for SimpleX Forensics
# ============================================================================
# Copyright (c) 2025 cannatoshi
# ============================================================================

set -e

BOOTSTRAP_FLAG=/var/lib/tor/.bootstrapped
TOR_DIR=/var/lib/tor/.tor
KEYS_DIR=${TOR_DIR}/keys

TORRC=/etc/tor/torrc
TORRC_BASE=/opt/torrc.base
TORRC_DA=/opt/torrc.da
TORRC_RELAY=/opt/torrc.relay
TORRC_EXIT=/opt/torrc.exit
TORRC_CLIENT=/opt/torrc.client
STATUS_AUTHORITIES=/status/dir-authorities

if [[ -z "${ROLE}" ]]; then
    echo "❌ No ROLE defined!"
    exit 1
fi

echo "🧅 ChutneX Node Starting..."
echo "   Role: ${ROLE}"
echo "   Nick: ${NICK:-anonymous}"

function bootstrap {
    # Get container IP from eth0 (works in isolated network)
    IP_ADDR=$(hostname -i | awk '{print $1}')
    
    if [[ -z "${IP_ADDR}" ]]; then
        IP_ADDR=$(ip -4 addr show eth0 | grep -oP '(?<=inet\s)\d+(\.\d+){3}' | head -1)
    fi
    
    echo "   IP: ${IP_ADDR}"

    # Start with base config
    cp ${TORRC_BASE} ${TORRC}

    case ${ROLE} in
    da)
        echo "🏛️  Configuring as Directory Authority..."
        echo "Nickname ${NICK}" >> ${TORRC}
        echo "Address ${IP_ADDR}" >> ${TORRC}
        echo "ContactInfo ${NICK} <${NICK}@chutnex.local>" >> ${TORRC}
        cat ${TORRC_DA} >> ${TORRC}

        # Create keys directory
        mkdir -p ${KEYS_DIR}
        chown -R debian-tor:debian-tor ${TOR_DIR}
        cd ${KEYS_DIR}

        # Generate DA certificate (12 month validity)
        PASSPHRASE=$(tr -dc A-Za-z0-9 </dev/urandom | head -c 12)
        echo ${PASSPHRASE} | sudo -u debian-tor tor-gencert --create-identity-key -m 12 -a ${IP_ADDR}:80 --passphrase-fd 0

        cd ${TOR_DIR}
        
        # Generate fingerprint
        sudo -u debian-tor tor --list-fingerprint --dirauthority "placeholder 127.0.0.1:80 0000000000000000000000000000000000000000" 2>/dev/null || true

        # Get fingerprints
        AUTH_CERT_FINGERPRINT=$(grep "fingerprint" ${KEYS_DIR}/authority_certificate | cut -d " " -f 2)
        SERVER_FINGERPRINT=$(cat ${TOR_DIR}/fingerprint | cut -d " " -f 2)

        echo "   🔑 Server Fingerprint: ${SERVER_FINGERPRINT}"
        echo "   🔑 Auth Fingerprint: ${AUTH_CERT_FINGERPRINT}"

        # Silence warnings
        touch ${TOR_DIR}/{approved-routers,sr-state}
        chown debian-tor:debian-tor ${TOR_DIR}/{approved-routers,sr-state}

        # Write DirAuthority line to shared volume
        mkdir -p /status
        echo "DirAuthority ${NICK} orport=9001 no-v2 v3ident=${AUTH_CERT_FINGERPRINT} ${IP_ADDR}:80 ${SERVER_FINGERPRINT}" >> ${STATUS_AUTHORITIES}
        echo "   ✅ DirAuthority registered"
        ;;

    relay|guard|middle)
        echo "🛡️  Configuring as Relay..."
        echo "Nickname ${NICK}" >> ${TORRC}
        echo "Address ${IP_ADDR}" >> ${TORRC}
        echo "ContactInfo ${NICK} <${NICK}@chutnex.local>" >> ${TORRC}
        cat ${TORRC_RELAY} >> ${TORRC}
        ;;

    exit)
        echo "🚪 Configuring as Exit Relay..."
        echo "Nickname ${NICK}" >> ${TORRC}
        echo "Address ${IP_ADDR}" >> ${TORRC}
        echo "ContactInfo ${NICK} <${NICK}@chutnex.local>" >> ${TORRC}
        cat ${TORRC_EXIT} >> ${TORRC}
        ;;

    client)
        echo "💻 Configuring as Client..."
        cat ${TORRC_CLIENT} >> ${TORRC}
        ;;

    hs)
        echo "🧅 Configuring as Hidden Service..."
        cat ${TORRC_CLIENT} >> ${TORRC}
        echo "HiddenServiceDir /var/lib/tor/hidden_service/" >> ${TORRC}
        echo "HiddenServicePort ${HS_PORT:-80} ${SERVICE_IP:-127.0.0.1}:${SERVICE_PORT:-80}" >> ${TORRC}
        ;;

    *)
        echo "❌ Unknown role: ${ROLE}"
        exit 1
        ;;
    esac

    touch ${BOOTSTRAP_FLAG}
}

# Bootstrap if not done
if [ ! -f ${BOOTSTRAP_FLAG} ]; then
    bootstrap
fi

# Wait for DAs to register (non-DAs wait)
if [[ "${ROLE}" != "da" ]]; then
    echo "⏳ Waiting for Directory Authorities..."
    WAIT_COUNT=0
    while [ ! -s ${STATUS_AUTHORITIES} ] && [ ${WAIT_COUNT} -lt 60 ]; do
        sleep 1
        WAIT_COUNT=$((WAIT_COUNT + 1))
    done
    
    if [ -s ${STATUS_AUTHORITIES} ]; then
        echo "   ✅ Found $(wc -l < ${STATUS_AUTHORITIES}) DAs"
    else
        echo "   ⚠️ No DAs found after 60s, continuing anyway..."
    fi
fi

# Add all DirAuthority statements to torrc
if [ -f ${STATUS_AUTHORITIES} ] && [ -s ${STATUS_AUTHORITIES} ]; then
    cat ${STATUS_AUTHORITIES} >> ${TORRC}
    # Remove duplicates
    sort -uo ${TORRC} ${TORRC}
fi

echo "🚀 Starting Tor..."
echo "=========================================="
cat ${TORRC}
echo "=========================================="

# Run Tor as debian-tor user
exec sudo -u debian-tor tor -f ${TORRC}
