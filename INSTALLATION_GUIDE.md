# 🛠️ Installation Guide for NHAI RAGFlow Demo

## ✅ **Current System Status**

Based on your system check:
- ✅ **Python**: 3.12.1 (Perfect!)
- ✅ **Docker**: 28.3.2 (Perfect!)
- ✅ **Python Packages**: requests already installed
- ❌ **Python PATH**: Needs configuration

## 📋 **What You Need to Install/Configure**

### **1. Python PATH Configuration** ⭐ **REQUIRED**

Your Python is installed but not in PATH. You need to configure it:

#### **Option A: Use py command (Recommended)**
```bash
# Use this instead of 'python' in all commands:
py ragflow_integration/bulk_processor.py
py ragflow_integration/monitor_processing.py
```

#### **Option B: Add Python to PATH**
1. Open System Properties → Advanced → Environment Variables
2. Add Python installation path to PATH variable
3. Restart command prompt

### **2. Docker Configuration** ⭐ **REQUIRED**

Make sure Docker Desktop is running and configured:

1. **Start Docker Desktop**
2. **Allocate Memory**: Settings → Resources → Memory → Set to 4GB+
3. **Apply & Restart Docker**

### **3. System Requirements Check**

#### **Hardware Requirements:**
- ✅ **RAM**: 8GB+ (You have sufficient)
- ✅ **Storage**: 10GB+ free space
- ✅ **CPU**: Multi-core processor
- ✅ **OS**: Windows 10/11

#### **Internet Requirements:**
- ✅ **Stable connection** for downloading models and Docker images

## 🚀 **Ready to Start Demo**

### **Step 1: Update Batch Files**
Since you need to use `py` instead of `python`, update the batch files:

```bash
# In all .bat files, replace:
python ragflow_integration/bulk_processor.py
# With:
py ragflow_integration/bulk_processor.py
```

### **Step 2: Start the Demo**
```bash
# Run the mega demo setup
ragflow_integration/mega_demo_setup.bat
```

## 🔧 **Troubleshooting**

### **If Python Commands Don't Work:**
```bash
# Use py instead of python:
py --version
py -m pip install requests
```

### **If Docker Issues:**
1. Make sure Docker Desktop is running
2. Check Docker memory allocation (4GB+)
3. Restart Docker Desktop

### **If Port Conflicts:**
- Change ports in `ragflow_integration/ragflow/docker/docker-compose.yml`
- Default ports: 80 (web), 11434 (Ollama)

## 📊 **Expected Performance**

With your current setup:
- **Processing Speed**: 15-20 documents/minute
- **Memory Usage**: ~4-6GB RAM
- **Storage**: ~2-5GB for indexed documents
- **Total Time**: 30-45 minutes for 500 documents

## 🎯 **Next Steps**

1. ✅ **System Check**: Complete
2. ✅ **Dependencies**: Installed
3. 🔄 **Demo Setup**: Ready to run
4. 🚀 **Start Demo**: Run `mega_demo_setup.bat`

---

**🎉 You're ready to run the 500+ document demo!** 