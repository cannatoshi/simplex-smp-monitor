# ============================================
# SimpleX XFTP Server - Docker Image
# ============================================

FROM debian:bookworm-slim

LABEL maintainer="SimpleX SMP Monitor"
LABEL description="SimpleX XFTP Server for secure file transfer"
LABEL version="1.0"

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    netcat-openbsd \
    openssl \
    && rm -rf /var/lib/apt/lists/*

# Download SimpleX XFTP Server binary
RUN curl -sSL https://github.com/simplex-chat/simplexmq/releases/latest/download/xftp-server-ubuntu-22_04-x86-64 \
    -o /usr/local/bin/xftp-server \
    && chmod +x /usr/local/bin/xftp-server

# Create data directories (where xftp-server expects them)
RUN mkdir -p /etc/opt/simplex-xftp /var/opt/simplex-xftp /var/log/simplex-xftp \
    && chmod 755 /etc/opt/simplex-xftp /var/opt/simplex-xftp /var/log/simplex-xftp

# Create non-root user
RUN useradd -r -s /bin/false -d /var/opt/simplex-xftp simplex \
    && chown -R simplex:simplex /etc/opt/simplex-xftp /var/opt/simplex-xftp /var/log/simplex-xftp

# Copy entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN sed -i 's/\r$//' /entrypoint.sh && chmod +x /entrypoint.sh

# Expose XFTP port
EXPOSE 443

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD nc -z localhost 443 || exit 1

# Volume for persistent data
VOLUME ["/var/opt/simplex-xftp", "/etc/opt/simplex-xftp"]

USER simplex
WORKDIR /var/opt/simplex-xftp

ENTRYPOINT ["/entrypoint.sh"]
CMD ["xftp-server", "start"]
