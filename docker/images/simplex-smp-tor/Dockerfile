# ============================================
# SimpleX SMP Server - Tor Hidden Service
# ============================================
FROM debian:bookworm-slim

LABEL maintainer="SimpleX SMP Monitor"
LABEL description="SimpleX SMP Server with Tor Hidden Service support"
LABEL version="1.0"

# Install dependencies including Tor
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    netcat-openbsd \
    openssl \
    tor \
    && rm -rf /var/lib/apt/lists/*

# Download SimpleX SMP Server binary
RUN curl -sSL https://github.com/simplex-chat/simplexmq/releases/latest/download/smp-server-ubuntu-22_04-x86-64 \
    -o /usr/local/bin/smp-server \
    && chmod +x /usr/local/bin/smp-server

# Create directories
RUN mkdir -p /etc/opt/simplex /var/opt/simplex /var/log/simplex \
    /var/lib/tor/simplex-smp /run/tor \
    && chmod 755 /etc/opt/simplex /var/opt/simplex /var/log/simplex \
    && chmod 700 /var/lib/tor/simplex-smp

# Create non-root user for simplex
RUN useradd -r -s /bin/false -d /var/opt/simplex simplex

# Configure Tor Hidden Service
RUN echo "DataDirectory /var/lib/tor" > /etc/tor/torrc && \
    echo "HiddenServiceDir /var/lib/tor/simplex-smp/" >> /etc/tor/torrc && \
    echo "HiddenServicePort 5223 127.0.0.1:5223" >> /etc/tor/torrc && \
    echo "HiddenServicePort 443 127.0.0.1:443" >> /etc/tor/torrc && \
    echo "Log notice file /var/log/tor/notices.log" >> /etc/tor/torrc && \
    mkdir -p /var/log/tor && \
    chown -R debian-tor:debian-tor /var/lib/tor /var/log/tor /run/tor

# Set correct permissions
RUN chown -R simplex:simplex /etc/opt/simplex /var/opt/simplex /var/log/simplex

# Copy entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN sed -i 's/\r$//' /entrypoint.sh && chmod +x /entrypoint.sh

# Expose ports (not really needed for Tor, but for documentation)
EXPOSE 5223 443

# Health check - check if Tor and SMP are running
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD nc -z localhost 5223 && test -f /var/lib/tor/simplex-smp/hostname || exit 1

# Volumes for persistent data
VOLUME ["/var/opt/simplex", "/etc/opt/simplex", "/var/lib/tor/simplex-smp"]

# Run as root initially (entrypoint handles user switching)
WORKDIR /var/opt/simplex

ENTRYPOINT ["/entrypoint.sh"]
CMD ["smp-server", "start"]