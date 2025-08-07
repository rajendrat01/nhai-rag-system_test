# 🚀 EC2 RAGFlow Setup - Complete Step by Step

## 📋 **Prerequisites**
- AWS Account (free tier available)
- Credit card for billing
- Basic computer knowledge

---

## 🎯 **Step 1: AWS Account Setup (2 minutes)**

### 1.1 Create AWS Account
1. Go to [AWS Console](https://aws.amazon.com/)
2. Click "Create an AWS Account"
3. Fill in your details
4. Add credit card (will only charge ~$3.50 for demo)

### 1.2 Access EC2
1. Login to AWS Console
2. Search for "EC2" in services
3. Click "EC2" to open

---

## 🖥️ **Step 2: Launch EC2 Instance (3 minutes)**

### 2.1 Launch Instance
1. Click "Launch Instance"
2. Name: `nhai-ragflow-demo`

### 2.2 Choose Configuration
- **AMI**: Ubuntu 22.04 LTS (free tier eligible)
- **Instance Type**: t3.medium (4GB RAM)
- **Key Pair**: Create new key pair named `nhai-key`
- **Download the .pem file** (save it safely!)

### 2.3 Network Settings
- **Security Group**: Create new security group
- **Allow these ports**:
  - SSH (22) - Your IP
  - HTTP (80) - Anywhere
  - HTTPS (443) - Anywhere
  - Custom TCP (8501) - Anywhere (for Streamlit)

### 2.4 Launch
1. Click "Launch Instance"
2. Wait 2-3 minutes for it to start

---

## 🔗 **Step 3: Connect to EC2 (2 minutes)**

### 3.1 Get Your Instance IP
1. In EC2 Console, find your instance
2. Copy the "Public IPv4 address" (looks like: 3.250.123.45)

### 3.2 Connect via SSH
**Windows (PowerShell):**
```powershell
# Navigate to where you saved the .pem file
cd C:\Users\YourName\Downloads

# Connect (replace with your actual IP and key name)
ssh -i nhai-key.pem ubuntu@YOUR-EC2-IP
```

**Example:**
```powershell
ssh -i nhai-key.pem ubuntu@3.250.123.45
```

---

## ⚙️ **Step 4: Install Dependencies (8 minutes)**

### 4.1 Update System
```bash
sudo apt update && sudo apt upgrade -y
```

### 4.2 Install Docker
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# Logout and login again
exit
```

**Reconnect:**
```bash
ssh -i nhai-key.pem ubuntu@YOUR-EC2-IP
```

### 4.3 Install Docker Compose
```bash
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

---

## 🚀 **Step 5: Deploy RAGFlow (10 minutes)**

### 5.1 Clone RAGFlow
```bash
git clone https://github.com/infiniflow/ragflow.git
cd ragflow
```

### 5.2 Create Environment File
```bash
cat > .env << EOF
RAGFLOW_API_KEY=nhai-demo-key-2024
RAGFLOW_SERVER_URL=http://localhost:9380
EOF
```

### 5.3 Start RAGFlow
```bash
docker-compose up -d
```

### 5.4 Check Status
```bash
docker-compose ps
```

---

## 📁 **Step 6: Upload Your Documents (5 minutes)**

### 6.1 Create Data Directory
```bash
mkdir -p data/nhai_documents
cd data/nhai_documents
```

### 6.2 Upload Your JSON Files
**Option A: Using SCP (from your Windows machine)**
```powershell
# In a new PowerShell window on your Windows machine
scp -i nhai-key.pem -r "D:\NHAI\Policy Circulars\nhai_policy_circulars\output\extracted_texts\*" ubuntu@YOUR-EC2-IP:~/ragflow/data/nhai_documents/
```

**Option B: Using AWS S3 (if you prefer)**
1. Upload files to S3 bucket
2. Download from S3 to EC2

---

## 🌐 **Step 7: Access Your App (2 minutes)**

### 7.1 Get Your Public URL
Your app will be available at:
```
http://YOUR-EC2-IP:8501
```

### 7.2 Test the App
1. Open browser
2. Go to: `http://YOUR-EC2-IP:8501`
3. Test with queries like "delegation of powers"

---

## 💰 **Cost Management**

### Monitor Costs
1. Go to AWS Billing Dashboard
2. Set up billing alerts at $5
3. **Stop instance when not using**:
   ```bash
   # In AWS Console: EC2 → Instances → Select → Stop
   ```

### Estimated Costs
- **t3.medium**: $0.0416/hour = $1.00/day
- **3 days demo**: ~$3.00
- **Data transfer**: ~$0.50
- **Total**: ~$3.50

---

## 🆘 **Troubleshooting**

### Common Issues:
1. **Can't connect via SSH**: Check security group allows port 22
2. **App not loading**: Check security group allows port 8501
3. **Docker issues**: Restart Docker service

### Useful Commands:
```bash
# Check if services are running
docker-compose ps

# View logs
docker-compose logs

# Restart services
docker-compose restart

# Check disk space
df -h
```

---

## 🎉 **Success!**

Your RAGFlow app is now live at:
```
http://YOUR-EC2-IP:8501
```

**Share this URL with anyone for your demo!**

---

## 📞 **Need Help?**

- **AWS Support**: Available in AWS Console
- **RAGFlow Docs**: https://github.com/infiniflow/ragflow
- **Cost Calculator**: https://calculator.aws/ 