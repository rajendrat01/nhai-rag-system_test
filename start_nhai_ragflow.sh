#!/bin/bash
# NHAI RAGFlow Startup Script

echo "Starting NHAI RAGFlow Integration..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running. Please start Docker first."
    exit 1
fi

# Navigate to RAGFlow directory
cd "$(dirname "$0")/ragflow/docker"

# Start RAGFlow services
echo "Starting RAGFlow services..."
docker-compose -f docker-compose.yml up -d

# Wait for services to be ready
echo "Waiting for services to be ready..."
sleep 30

# Check service status
echo "Checking service status..."
docker-compose -f docker-compose.yml ps

# Display access information
echo ""
echo "=========================================="
echo "NHAI RAGFlow Integration Started Successfully!"
echo "=========================================="
echo "Web Interface: http://localhost"
echo "API Endpoint: http://localhost/api"
echo "Default Login: admin / nhai_admin_2025"
echo ""
echo "To stop services: docker-compose -f docker-compose.yml down"
echo "To view logs: docker-compose -f docker-compose.yml logs -f"
echo "=========================================="
