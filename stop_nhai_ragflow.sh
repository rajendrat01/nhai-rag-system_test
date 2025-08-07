#!/bin/bash
# NHAI RAGFlow Stop Script

echo "Stopping NHAI RAGFlow Integration..."

# Navigate to RAGFlow directory
cd "$(dirname "$0")/ragflow/docker"

# Stop RAGFlow services
echo "Stopping RAGFlow services..."
docker-compose -f docker-compose.yml down

echo "NHAI RAGFlow Integration stopped."
