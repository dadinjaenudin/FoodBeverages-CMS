FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    build-essential \
    libpq-dev \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy project files
COPY . .

# Create entrypoint script directly in Dockerfile
RUN echo '#!/bin/bash\n\
set -e\n\
echo "======================================"\n\
echo "🍽️  F&B POS HO System - Starting..."\n\
echo "======================================"\n\
echo "Waiting for PostgreSQL..."\n\
while ! nc -z $DB_HOST $DB_PORT; do\n\
  sleep 0.5\n\
done\n\
echo "✓ PostgreSQL is ready!"\n\
echo "Waiting for Redis..."\n\
while ! nc -z redis 6379; do\n\
  sleep 0.5\n\
done\n\
echo "✓ Redis is ready!"\n\
exec "$@"' > /app/entrypoint.sh && \
    chmod +x /app/entrypoint.sh

# Create directory for logs
RUN mkdir -p /app/logs

# Collect static files (will be overridden by volume in development)
RUN python manage.py collectstatic --noinput || true

# Expose port
EXPOSE 8000

# Set entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]

# Default command
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
