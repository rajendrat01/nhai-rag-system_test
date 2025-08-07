#!/bin/bash
# NHAI RAGFlow Demo Startup Script
# For demo using external models from the internet

echo "🚀 Starting NHAI RAGFlow Demo Setup..."
echo "=========================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running. Please start Docker first."
    exit 1
fi

# Check if Ollama is installed (for free local models)
if ! command -v ollama &> /dev/null; then
    echo "⚠️  Ollama not found. Installing Ollama for free local models..."
    curl -fsSL https://ollama.ai/install.sh | sh
    echo "✅ Ollama installed successfully!"
else
    echo "✅ Ollama is already installed"
fi

# Start Ollama service
echo "🔄 Starting Ollama service..."
ollama serve &
OLLAMA_PID=$!

# Wait for Ollama to start
sleep 5

# Pull a lightweight model for demo
echo "📥 Downloading demo model (llama3.1:8b)..."
ollama pull llama3.1:8b

# Navigate to RAGFlow directory
cd "$(dirname "$0")/ragflow/docker"

# Copy demo configuration
echo "⚙️  Setting up demo configuration..."
cp ../../demo_config.yaml ./service_conf.yaml

# Start RAGFlow services
echo "🚀 Starting RAGFlow services..."
docker-compose -f docker-compose.yml up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Check service status
echo "🔍 Checking service status..."
docker-compose -f docker-compose.yml ps

# Test Ollama connection
echo "🧪 Testing Ollama connection..."
curl -X POST http://localhost:11434/api/generate -d '{
  "model": "llama3.1:8b",
  "prompt": "Hello, this is a test for NHAI demo",
  "stream": false
}' | head -c 200

echo ""
echo "=========================================="
echo "🎉 NHAI RAGFlow Demo Setup Complete!"
echo "=========================================="
echo "🌐 Web Interface: http://localhost"
echo "🔑 Default Login: admin / nhai_admin_2025"
echo "🤖 Ollama Models: http://localhost:11434"
echo "📊 API Endpoint: http://localhost/api"
echo ""
echo "📋 Demo Features Available:"
echo "   ✅ Document Upload & Processing"
echo "   ✅ Semantic Search"
echo "   ✅ Policy Analysis"
echo "   ✅ Q&A with NHAI Documents"
echo "   ✅ Policy Summarization"
echo ""
echo "🔧 To stop services: ./stop_demo.sh"
echo "📝 To view logs: docker-compose -f docker-compose.yml logs -f"
echo "=========================================="

# Save PID for cleanup
echo $OLLAMA_PID > .ollama_pid 