FROM python:3.11-slim

# Set environment variables for better Docker experience
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_VERSION=1.6.1 \
    DEBIAN_FRONTEND=noninteractive

# Install OpenVPN and other dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    openvpn \
    ffmpeg \
    curl \
    ca-certificates \
    build-essential \
    iputils-ping \
    net-tools \
    procps \
    dnsutils \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create app directory with proper permissions
WORKDIR /app

# Create cache directory
RUN mkdir -p /tmp/youtube_audio_cache && \
    chmod 777 /tmp/youtube_audio_cache

# Copy dependency files first for better caching
COPY pyproject.toml poetry.lock* render_requirements.txt ./

# Install dependencies with robust fallback mechanism
RUN pip install --upgrade pip && \
    pip install --no-cache-dir poetry==${POETRY_VERSION} && \
    poetry config virtualenvs.create false && \
    (poetry install --no-interaction --no-ansi || \
    pip install --no-cache-dir -r render_requirements.txt)

# Copy the VPN configuration first (special handling)
COPY vpn-config.ovpn /etc/openvpn/vpn-config.ovpn

# Create directory for YouTube cookies and other assets
RUN mkdir -p /app/attached_assets

# Copy cookies.txt for YouTube authentication if available
COPY attached_assets/cookies.txt /app/attached_assets/cookies.txt

# Copy the rest of the app
COPY . .

# Create and configure directory for VPN config
RUN mkdir -p /etc/openvpn && \
    chmod 600 /etc/openvpn/vpn-config.ovpn && \
    # Ensure the start script is executable
    chmod +x /start.sh

# Volume for VPN config files and audio cache
VOLUME /etc/openvpn
VOLUME /tmp/youtube_audio_cache

# Expose port for Flask app
EXPOSE 5000

# Comprehensive health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Environment variables for VPN - these can be overridden at runtime
ENV VPN_USERNAME=vpnuser \
    VPN_PASSWORD=vpnpass2025 \
    CACHE_DIR=/tmp/youtube_audio_cache \
    MAX_CACHE_SIZE_MB=500 \
    PREFERRED_REGION=IN

# Run the start script when the container launches
CMD ["./start.sh"]