FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED=1

# Install python dependencies
# Copy backend-specific requirements from the build context (root)
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code structure
COPY backend /app/backend
# Also copy config if needed, or rely on env
COPY config.yaml /app/config.yaml

# Expose the port Render assigns (default 10000)
# We don't strictly need EXPOSE but it documents it
EXPOSE 10000

# Run uvicorn using the PORT environment variable
CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-10000}"]
