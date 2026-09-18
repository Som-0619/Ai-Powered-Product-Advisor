#!/bin/bash
set -e

echo "============================================================"
echo "Starting Product Advisor Services (Phase 1)"
echo "============================================================"

# Ensure environment file exists
if [ ! -f .env ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
fi

echo "Starting Docker Compose services..."
docker compose up -d

echo ""
echo "Waiting for core services to report healthy..."
docker compose ps

echo ""
echo "Running infrastructure verification script..."
python3 scripts/verify_services.py || true

echo ""
echo "Product Advisor local environment started successfully:"
echo " - Frontend: http://localhost:3000"
echo " - Backend API: http://localhost:8000"
echo " - API Documentation: http://localhost:8000/docs"
echo " - MinIO Console: http://localhost:9001 (minioadmin / minioadmin)"
echo " - OpenSearch: http://localhost:9200"
echo " - Ollama: http://localhost:11434"
