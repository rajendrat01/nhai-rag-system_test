# 🚀 EC2 RAGFlow Deployment - Quick Guide

## ⚡ **30-Minute Setup**

### **Step 1: Launch EC2 Instance (5 minutes)**
1. Go to AWS Console → EC2
2. Launch Instance:
   - **AMI**: Ubuntu 22.04 LTS
   - **Instance Type**: t3.medium (4GB RAM)
   - **Storage**: 20GB GP3
   - **Security Group**: Allow ports 22, 80, 443, 8501

### **Step 2: Connect & Setup (10 minutes)**
```bash
# Connect via SSH
ssh -i your-key.pem ubuntu@your-ec2-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### **Step 3: Deploy RAGFlow (15 minutes)**
```bash
# Clone RAGFlow
git clone https://github.com/infiniflow/ragflow.git
cd ragflow

# Create .env file
cat > .env << EOF
RAGFLOW_API_KEY=your-api-key-here
RAGFLOW_SERVER_URL=http://localhost:9380
EOF

# Start RAGFlow
docker-compose up -d

# Upload your documents
# (Copy your 1600+ extracted JSONs to the data directory)
```

### **Step 4: Access Your App**
- **Local**: http://your-ec2-ip:8501
- **Public**: http://your-ec2-ip:8501

## 💰 **Cost Breakdown**
- **t3.medium**: $0.0416/hour
- **3 days**: $3.00
- **Data transfer**: ~$0.50
- **Total**: **~$3.50 for 3 days**

## 🎯 **Advantages**
- ✅ Full RAGFlow functionality
- ✅ All 1600+ documents
- ✅ Professional AI responses
- ✅ Scalable and reliable
- ✅ Complete GitHub setup

## 🚨 **Important Notes**
- **Stop instance** when not using (saves money)
- **Backup data** before stopping
- **Use t3.small** if budget is tight ($1.44/day)

## 📞 **Support**
- RAGFlow documentation: https://github.com/infiniflow/ragflow
- AWS EC2 pricing: https://aws.amazon.com/ec2/pricing/ 