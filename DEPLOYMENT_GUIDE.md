# 🚀 NHAI RAG System - Cloud Deployment Guide

## 🌐 **Option 1: Streamlit Cloud (Recommended - 10 minutes)**

### Step 1: Create GitHub Repository
1. Go to [GitHub](https://github.com) and create a new repository
2. Name it: `nhai-rag-system`
3. Make it public

### Step 2: Upload Files
Upload these files to your GitHub repository:
- `streamlit_app.py` (rename to `app.py`)
- `requirements.txt`

### Step 3: Deploy to Streamlit Cloud
1. Go to [Streamlit Cloud](https://share.streamlit.io/)
2. Sign in with GitHub
3. Click "New app"
4. Select your repository: `nhai-rag-system`
5. Set main file path: `app.py`
6. Click "Deploy"

**✅ Your app will be live at: `https://your-app-name.streamlit.app`**

---

## ☁️ **Option 2: Heroku (Alternative)**

### Step 1: Install Heroku CLI
```bash
# Download from: https://devcenter.heroku.com/articles/heroku-cli
```

### Step 2: Create Heroku App
```bash
heroku create nhai-rag-demo
```

### Step 3: Deploy
```bash
git add .
git commit -m "Initial deployment"
git push heroku main
```

---

## 🔧 **Option 3: Railway (Easiest)**

1. Go to [Railway](https://railway.app/)
2. Connect your GitHub account
3. Create new project from GitHub
4. Select your repository
5. Deploy automatically

---

## 📋 **Files Structure**
```
nhai-rag-system/
├── app.py                 # Main Streamlit app
├── requirements.txt       # Dependencies
└── README.md             # Documentation
```

## 🎯 **Demo Features**
- ✅ TF-IDF search with relevance scores
- ✅ AI-generated answers using HuggingFace
- ✅ Professional interface
- ✅ Sample NHAI documents included
- ✅ Works immediately after deployment

## 🌍 **Public Access**
Once deployed, anyone can access your app using the provided URL!

---

## 🚀 **Quick Start Commands**

```bash
# Test locally first
streamlit run app.py

# Deploy to Streamlit Cloud
# Just upload to GitHub and connect to Streamlit Cloud
```

**Your app will be publicly accessible for 2-3 days or longer!** 🎉 