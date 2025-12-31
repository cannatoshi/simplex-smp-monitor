#!/bin/bash
set -e

echo "============================================"
echo "  SimpleX SMP Monitor - Docker Startup"
echo "============================================"

# Wait for Database
if [ -n "$DATABASE_URL" ] || [ -n "$POSTGRES_HOST" ]; then
    echo "⏳ Waiting for PostgreSQL..."
    
    if [ -n "$POSTGRES_HOST" ]; then
        DB_HOST="$POSTGRES_HOST"
        DB_PORT="${POSTGRES_PORT:-5432}"
    else
        DB_HOST=$(echo $DATABASE_URL | sed -e 's|.*@\([^:]*\):.*|\1|')
        DB_PORT=$(echo $DATABASE_URL | sed -e 's|.*:\([0-9]*\)/.*|\1|')
    fi
    
    MAX_RETRIES=30
    RETRY_COUNT=0
    while ! nc -z "$DB_HOST" "$DB_PORT" 2>/dev/null; do
        RETRY_COUNT=$((RETRY_COUNT + 1))
        if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
            echo "❌ Database not available after $MAX_RETRIES attempts"
            exit 1
        fi
        echo "   Waiting for database... ($RETRY_COUNT/$MAX_RETRIES)"
        sleep 2
    done
    echo "✅ Database is ready!"
else
    echo "📁 Using SQLite database"
fi

# Wait for Redis
if [ -n "$REDIS_URL" ] || [ -n "$REDIS_HOST" ]; then
    echo "⏳ Waiting for Redis..."
    REDIS_HOST="${REDIS_HOST:-redis}"
    REDIS_PORT="${REDIS_PORT:-6379}"
    
    MAX_RETRIES=15
    RETRY_COUNT=0
    while ! nc -z "$REDIS_HOST" "$REDIS_PORT" 2>/dev/null; do
        RETRY_COUNT=$((RETRY_COUNT + 1))
        if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
            echo "⚠️  Redis not available, continuing..."
            break
        fi
        echo "   Waiting for Redis... ($RETRY_COUNT/$MAX_RETRIES)"
        sleep 1
    done
    if [ $RETRY_COUNT -lt $MAX_RETRIES ]; then
        echo "✅ Redis is ready!"
    fi
fi

# Run Migrations
echo ""
echo "🔄 Running database migrations..."
python manage.py migrate --noinput

# Collect Static Files
echo ""
echo "📦 Collecting static files..."
python manage.py collectstatic --noinput --clear

# Create Superuser
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
    echo ""
    echo "👤 Creating superuser..."
    python manage.py shell << PYEOF
from django.contrib.auth import get_user_model
User = get_user_model()
username = "$DJANGO_SUPERUSER_USERNAME"
email = "${DJANGO_SUPERUSER_EMAIL:-admin@localhost}"
password = "$DJANGO_SUPERUSER_PASSWORD"

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f"✅ Superuser '{username}' created!")
else:
    print(f"ℹ️  Superuser '{username}' already exists")
PYEOF
fi

# Startup Info
echo ""
echo "============================================"
echo "  ✅ SimpleX SMP Monitor Ready!"
echo "============================================"
echo ""
echo "  🌐 Web UI:    http://localhost:8080"
echo "  📊 API:       http://localhost:8080/api/"
echo "  🔧 Admin:     http://localhost:8080/admin/"
echo "  📈 Grafana:   http://localhost:3002"
echo ""
echo "============================================"
echo ""

exec "$@"
