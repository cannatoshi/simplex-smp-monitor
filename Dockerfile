# ============================================
# SimpleX SMP Monitor - Docker Image
# ============================================

# Stage 1: Build React Frontend
FROM node:24-alpine AS frontend-builder

WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Stage 2: Python Backend
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=config.settings

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    curl \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install production dependencies
RUN pip install --no-cache-dir \
    gunicorn \
    psycopg2-binary \
    whitenoise \
    dj-database-url

# Copy Django project
COPY . .

# Copy built frontend from Stage 1
COPY --from=frontend-builder /app/static/dist /app/static/dist

# Create directories
RUN mkdir -p /app/staticfiles /app/media /app/data

# Setup entrypoint
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN sed -i 's/\r$//' /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Collect static files
RUN python manage.py collectstatic --noinput --clear 2>/dev/null || true

# Create user (but run as root for Docker socket access)
RUN useradd --create-home --shell /bin/bash appuser \
    && chown -R appuser:appuser /app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health/ || exit 1

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "120", "config.wsgi:application"]
