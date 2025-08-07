# Circulars RAG System

AI-powered search and analysis system for NHAI (National Highways Authority of India) policy documents.

## Features

- 🔍 **Smart Document Search**: TF-IDF based search with cosine similarity
- 🤖 **AI-Generated Answers**: Using HuggingFace DialoGPT model
- 📊 **Relevance Scoring**: Intelligent document ranking
- 🧹 **OCR Text Cleaning**: Clean display of extracted text
- 📱 **Web Interface**: Streamlit-based user-friendly interface

## Quick Start

1. **Replace the HuggingFace API Key** in `app.py`:
   ```python
   HUGGINGFACE_API_KEY = "your_actual_api_key_here"
   ```

2. **Add your document data** to the `data/extracted_texts/` folder

3. **Deploy to Streamlit Cloud**:
   - Upload to GitHub
   - Connect to Streamlit Cloud
   - Deploy automatically

## Usage

- Ask questions about NHAI policies
- Get AI-generated answers based on relevant documents
- View document previews and metadata
- See relevance scores for each result

## Sample Queries

- "What are the land acquisition procedures?"
- "How is toll collection managed?"
- "What are the delegation of powers guidelines?"

- "What are the environmental clearance requirements?" 
