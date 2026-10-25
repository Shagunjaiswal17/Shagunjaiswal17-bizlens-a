# Multi-stage Dockerfile for BizLens AI
FROM python:3.11-slim as backend

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source
COPY backend /app/backend
COPY main.py /app/main.py
COPY static /app/static

ENV PORT=8000
ENV PYTHONPATH=/app/backend
EXPOSE 8000

CMD ["python", "main.py"]
