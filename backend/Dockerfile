FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
# We copy everything into /app/backend to match the import structure "from backend.services..."
# This assumes we run uvicorn from /app
COPY . /app/backend

# Copy config.yaml if it exists in the root context, 
# but since docker context is usually the root of the repo, we handle this in docker-compose 
# or copy specifically. For now, let's assume we build from the backend dir context?
# Wait, standard microservice pattern: build context is often the service dir.
# But imports "from backend.services" imply we are running from parent of backend?
# Let's adjust imports in main.py or adjust PYTHONPATH.
# Actually, if we copy to /app/backend, and run from /app, "from backend.services" works.

# Expose port
EXPOSE 8000

# Run command
# We run from /app, targeting backend.main:app
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
