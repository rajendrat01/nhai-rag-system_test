# 🚀 Quick Deployment Guide - Streamlit Cloud

## Step 1: Create GitHub Repository (2 minutes)

1. Go to [GitHub.com](https://github.com)
2. Click "New repository"
3. Name it: `nhai-rag-system`
4. Make it **Public**
5. Click "Create repository"

## Step 2: Upload Files (1 minute)

Upload these files to your GitHub repository:
- `app.py` (main Streamlit app)
- `requirements.txt` (dependencies)
- `README.md` (documentation)

## Step 3: Deploy to Streamlit Cloud (2 minutes)

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click "New app"
4. Select your repository: `nhai-rag-system`
5. Set main file path: `app.py`
6. Click "Deploy"

## Step 4: Add Your Data (2 minutes)

1. **Replace the HuggingFace API Key** in `app.py`:
   ```python
   HUGGINGFACE_API_KEY = "your_actual_api_key_here"
   ```

2. **Add your document data**:
   - Create `data/extracted_texts/` folder in your GitHub repo
   - Upload your JSON files there

## Step 5: Get Your Public URL

Your app will be live at:
```
https://your-app-name.streamlit.app
```

**Total time: 5 minutes!**

## Troubleshooting

- **If deployment fails**: Check that all files are uploaded correctly
- **If app doesn't load**: Verify the HuggingFace API key is correct
- **If no documents found**: Ensure the data folder structure is correct

## Share Your Demo

Once deployed, anyone can access your RAG system using the provided URL! 