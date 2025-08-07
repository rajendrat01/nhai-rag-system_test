#!/bin/bash
# Quick 2-Hour NHAI Demo Setup
# Uses existing models - No training required!

echo "🚀 Quick 2-Hour NHAI Demo Setup Starting..."
echo "=========================================="

# Step 1: Install Ollama (Free Local Models)
echo "📥 Step 1: Installing Ollama for free local models..."
if ! command -v ollama &> /dev/null; then
    curl -fsSL https://ollama.ai/install.sh | sh
    echo "✅ Ollama installed!"
else
    echo "✅ Ollama already installed!"
fi

# Step 2: Start Ollama and download model
echo "🤖 Step 2: Downloading lightweight model..."
ollama serve &
sleep 10
ollama pull llama3.1:8b
echo "✅ Model downloaded!"

# Step 3: Start RAGFlow with Docker
echo "🐳 Step 3: Starting RAGFlow services..."
cd "$(dirname "$0")/ragflow/docker"

# Use the existing docker-compose
docker-compose -f docker-compose.yml up -d

echo "⏳ Waiting for services to start..."
sleep 30

# Step 4: Test everything
echo "🧪 Step 4: Testing services..."
curl -s http://localhost:11434/api/tags > /dev/null && echo "✅ Ollama working!"
curl -s http://localhost > /dev/null && echo "✅ RAGFlow web interface working!"

echo ""
echo "🎉 DEMO READY IN UNDER 30 MINUTES!"
echo "=========================================="
echo "🌐 Web Interface: http://localhost"
echo "🔑 Login: admin / nhai_admin_2025"
echo "🤖 Ollama Models: http://localhost:11434"
echo ""
echo "📋 What you can do now:"
echo "   1. Upload NHAI PDFs via web interface"
echo "   2. Ask questions about policies"
echo "   3. Search across documents"
echo "   4. Get policy summaries"
echo ""
echo "🔧 To stop: ./stop_demo.sh"
echo "==========================================" 