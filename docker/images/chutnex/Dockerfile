FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    apt-transport-https \
    gnupg \
    wget \
    ca-certificates \
    procps \
    iproute2 \
    sudo \
    && wget -qO- https://deb.torproject.org/torproject.org/A3C4F0F979CAA22CDBA8F512EE8CBC9E886DDD89.asc \
       | gpg --dearmor > /usr/share/keyrings/tor-archive-keyring.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/tor-archive-keyring.gpg] https://deb.torproject.org/torproject.org bookworm main" \
       > /etc/apt/sources.list.d/tor.list \
    && apt-get update && apt-get install -y --no-install-recommends \
       tor \
       tor-geoipdb \
       deb.torproject.org-keyring \
    && rm -rf /var/lib/apt/lists/*

# Create directories
RUN mkdir -p /var/lib/tor/.tor/keys /status \
    && chown -R debian-tor:debian-tor /var/lib/tor \
    && chmod 700 /var/lib/tor

# Copy torrc templates
COPY torrc.base torrc.da torrc.relay torrc.exit torrc.client /opt/

# Copy entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 9050 9051 9001 80

ENTRYPOINT ["/entrypoint.sh"]
