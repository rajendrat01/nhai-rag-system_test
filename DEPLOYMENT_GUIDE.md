# NHAI RAG System - Streamlit Cloud Deployment Guide

## Quick Deployment to Streamlit Cloud

### Step 1: Prepare Your Repository
Your repository is already ready with:
- ✅ `app.py` (main Streamlit application)
- ✅ `requirements.txt` (dependencies)
- ✅ `data/extracted_texts/` (1614+ extracted documents)

### Step 2: Deploy to Streamlit Cloud

1. **Go to Streamlit Cloud**: https://share.streamlit.io/
2. **Sign in with GitHub**
3. **Click "New app"**
4. **Configure your app**:
   - **Repository**: `rajendrat01/nhai-rag-system_test`
   - **Branch**: `master`
   - **Main file path**: `app.py`
   - **App URL**: Choose a custom URL (optional)

### Step 3: Set Environment Variables

In Streamlit Cloud, add this environment variable:
- **Key**: `HUGGINGFACE_API_KEY`
- **Value**: `your_huggingface_api_key_here`

### Step 4: Deploy

Click **"Deploy"** and wait for the build to complete.

## Your App Will Be Live At:
`https://your-app-name.streamlit.app`

## Features Available:
- 🔍 **Smart Document Search**: TF-IDF based search
- 🤖 **AI-Generated Answers**: Using HuggingFace models
- 📊 **Relevance Scoring**: Intelligent document ranking
- 🧹 **Clean OCR Text**: Processed document display
- 📱 **Mobile-Friendly**: Works on all devices

## Sample Queries:
- "What are the land acquisition procedures?"
- "How is toll collection managed?"
- "What are the delegation of powers guidelines?"
- "What are the environmental clearance requirements?"

## Troubleshooting:

### If the app fails to load:
1. Check that `app.py` is in the root directory
2. Verify `requirements.txt` has all dependencies
3. Ensure environment variable is set correctly

### If search doesn't work:
1. Verify documents are in `data/extracted_texts/`
2. Check HuggingFace API key is valid
3. Wait for initial document loading to complete

## Support:
- **GitHub Issues**: Report problems in your repository
- **Streamlit Community**: https://discuss.streamlit.io/
- **Documentation**: https://docs.streamlit.io/ 