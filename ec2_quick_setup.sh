#!/bin/bash
# 🚀 EC2 RAGFlow Quick Setup Script
# Run this on your EC2 instance after connecting via SSH

echo "🚀 Starting NHAI RAGFlow Setup..."

# Update system
echo "📦 Updating system..."
sudo apt update && sudo apt upgrade -y

# Install Docker
echo "🐳 Installing Docker..."
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# Install Docker Compose
echo "📋 Installing Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Clone RAGFlow
echo "📥 Cloning RAGFlow..."
git clone https://github.com/infiniflow/ragflow.git
cd ragflow

# Create environment file
echo "⚙️ Creating environment file..."
cat > .env << EOF
RAGFLOW_API_KEY=nhai-demo-key-2024
RAGFLOW_SERVER_URL=http://localhost:9380
EOF

# Create data directory
echo "📁 Creating data directory..."
mkdir -p data/nhai_documents

# Start RAGFlow
echo "🚀 Starting RAGFlow..."
docker-compose up -d

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 30

# Check status
echo "📊 Checking service status..."
docker-compose ps

echo "✅ Setup complete!"
echo "🌐 Your app will be available at: http://$(curl -s ifconfig.me):8501"
echo "📁 Upload your documents to: ~/ragflow/data/nhai_documents/"
echo ""
echo "📋 Next steps:"
echo "1. Upload your JSON files using SCP:"
echo "   scp -i nhai-key.pem -r 'D:\NHAI\Policy Circulars\nhai_policy_circulars\output\extracted_texts\*' ubuntu@YOUR-EC2-IP:~/ragflow/data/nhai_documents/"
echo ""
echo "2. Access your app at: http://YOUR-EC2-IP:8501" 