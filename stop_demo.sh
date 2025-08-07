#!/bin/bash
# NHAI RAGFlow Demo Stop Script

echo "🛑 Stopping NHAI RAGFlow Demo Services..."
echo "=========================================="

# Navigate to RAGFlow directory
cd "$(dirname "$0")/ragflow/docker"

# Stop RAGFlow services
echo "🔄 Stopping RAGFlow services..."
docker-compose -f docker-compose.yml down

# Stop Ollama if running
if [ -f .ollama_pid ]; then
    OLLAMA_PID=$(cat .ollama_pid)
    if kill -0 $OLLAMA_PID 2>/dev/null; then
        echo "🔄 Stopping Ollama service..."
        kill $OLLAMA_PID
        rm .ollama_pid
    fi
fi

# Kill any remaining Ollama processes
pkill -f ollama 2>/dev/null || true

echo "✅ Demo services stopped successfully!"
echo "==========================================" 