# Dockerfile — ZORO bot + FastAPI (Phase 3)
FROM python:3.11-slim

WORKDIR /app

# System dependencies (for psycopg2)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip uninstall -y tensorboard tensorboard-data-server tb-nightly || true
RUN pip uninstall -y triton pytorch-triton || true

# Copy all source files
COPY . .

# Make start script executable
RUN chmod +x start.sh

# FastAPI port
EXPOSE 7860

CMD ["./start.sh"]
