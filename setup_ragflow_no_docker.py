#!/usr/bin/env python3
"""
RAGFlow Setup Without Docker - Complete Pipeline
Handles setup, data upload, and demo creation
"""

import json
import os
import time
import requests
from pathlib import Path
from datetime import datetime
import subprocess
import sys

class RAGFlowNoDockerSetup:
    def __init__(self):
        self.extracted_dir = Path("output/extracted_texts")
        self.ragflow_dir = Path("ragflow_integration/ragflow_simple")
        self.api_key = None
        self.base_url = "https://api-inference.huggingface.co"
        
    def setup_ragflow(self):
        """Setup RAGFlow without Docker"""
        print("🚀 SETTING UP RAGFLOW WITHOUT DOCKER")
        print("=" * 50)
        
        # Create RAGFlow directory
        self.ragflow_dir.mkdir(parents=True, exist_ok=True)
        
        # Install required packages
        print("📦 Installing required packages...")
        packages = [
            "ragflow-sdk",
            "sentence-transformers",
            "transformers",
            "torch",
            "chromadb",
            "fastapi",
            "uvicorn"
        ]
        
        for package in packages:
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", package], 
                             check=True, capture_output=True)
                print(f"✅ {package} installed")
            except subprocess.CalledProcessError:
                print(f"⚠️  {package} already installed or failed")
        
        print("✅ RAGFlow setup completed")
        
    def get_huggingface_token(self):
        """Get HuggingFace API token"""
        print("\n🔑 Setting up HuggingFace API")
        print("=" * 30)
        
        # Check if token exists
        token_file = Path("ragflow_integration/hf_token.txt")
        if token_file.exists():
            with open(token_file, 'r') as f:
                self.api_key = f.read().strip()
            print("✅ Using existing HuggingFace token")
            return True
            
        print("📝 Please enter your HuggingFace API token:")
        print("   Get it from: https://huggingface.co/settings/tokens")
        print("   (Free tier allows 30,000 requests/month)")
        
        token = input("Token: ").strip()
        if token:
            self.api_key = token
            with open(token_file, 'w') as f:
                f.write(token)
            print("✅ Token saved")
            return True
        else:
            print("❌ No token provided")
            return False
    
    def test_models(self):
        """Test HuggingFace models"""
        print("\n🧪 Testing HuggingFace Models")
        print("=" * 30)
        
        models = {
            "embedding": "sentence-transformers/all-MiniLM-L6-v2",
            "llm": "microsoft/DialoGPT-medium"
        }
        
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        for model_type, model_name in models.items():
            try:
                url = f"{self.base_url}/models/{model_name}"
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    print(f"✅ {model_type}: {model_name}")
                else:
                    print(f"⚠️  {model_type}: {model_name} - Status: {response.status_code}")
            except Exception as e:
                print(f"❌ {model_type}: {model_name} - Error: {e}")
    
    def create_simple_rag_system(self):
        """Create a simple RAG system"""
        print("\n🔧 Creating Simple RAG System")
        print("=" * 30)
        
        # Create the RAG system
        rag_code = '''
import json
import requests
from pathlib import Path
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings

class SimpleRAGSystem:
    def __init__(self, api_key):
        self.api_key = api_key
        self.embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        self.client = chromadb.Client(Settings(chroma_db_impl="duckdb+parquet", persist_directory="./chroma_db"))
        self.collection = self.client.create_collection("nhai_documents")
        
    def load_documents(self, extracted_dir):
        """Load all extracted documents"""
        print("📚 Loading documents...")
        documents = []
        metadata = []
        ids = []
        
        for json_file in Path(extracted_dir).glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if data.get('extracted_text'):
                    documents.append(data['extracted_text'])
                    metadata.append({
                        'filename': data.get('filename', ''),
                        'subject': data.get('subject', ''),
                        'date': data.get('date', ''),
                        'category': data.get('category', '')
                    })
                    ids.append(str(json_file.stem))
                    
            except Exception as e:
                print(f"⚠️  Error loading {json_file}: {e}")
        
        print(f"✅ Loaded {len(documents)} documents")
        return documents, metadata, ids
    
    def create_embeddings(self, documents):
        """Create embeddings for documents"""
        print("🧠 Creating embeddings...")
        embeddings = self.embedding_model.encode(documents)
        print(f"✅ Created {len(embeddings)} embeddings")
        return embeddings
    
    def build_index(self, documents, metadata, ids):
        """Build search index"""
        print("🔍 Building search index...")
        embeddings = self.create_embeddings(documents)
        
        # Add to ChromaDB
        self.collection.add(
            embeddings=embeddings.tolist(),
            documents=documents,
            metadatas=metadata,
            ids=ids
        )
        print("✅ Search index built")
    
    def search(self, query, top_k=5):
        """Search documents"""
        query_embedding = self.embedding_model.encode([query])
        results = self.collection.query(
            query_embeddings=query_embedding.tolist(),
            n_results=top_k
        )
        return results
    
    def answer_question(self, question):
        """Answer question using RAG"""
        # Search for relevant documents
        search_results = self.search(question, top_k=3)
        
        if not search_results['documents']:
            return "No relevant documents found."
        
        # Create context from top documents
        context = "\\n\\n".join(search_results['documents'][0])
        
        # Use HuggingFace API for LLM
        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {
            "inputs": f"Context: {context}\\n\\nQuestion: {question}\\n\\nAnswer:",
            "parameters": {"max_length": 500}
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/models/microsoft/DialoGPT-medium",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                return result[0]['generated_text']
            else:
                return f"Error: {response.status_code}"
                
        except Exception as e:
            return f"Error: {e}"

# Usage
if __name__ == "__main__":
    rag = SimpleRAGSystem("your_api_key_here")
    documents, metadata, ids = rag.load_documents("output/extracted_texts")
    rag.build_index(documents, metadata, ids)
    
    # Test search
    results = rag.search("delegation of powers")
    print("Search results:", results)
'''
        
        with open(self.ragflow_dir / "simple_rag.py", 'w') as f:
            f.write(rag_code)
        
        print("✅ Simple RAG system created")
    
    def create_web_interface(self):
        """Create a simple web interface"""
        print("\n🌐 Creating Web Interface")
        print("=" * 30)
        
        web_code = '''
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
import uvicorn
from simple_rag import SimpleRAGSystem

app = FastAPI(title="NHAI Policy Circulars RAG")

# Initialize RAG system
rag = SimpleRAGSystem("your_api_key_here")

@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>NHAI Policy Circulars Search</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .container { max-width: 800px; margin: 0 auto; }
            input[type="text"] { width: 100%; padding: 10px; margin: 10px 0; }
            button { padding: 10px 20px; background: #007bff; color: white; border: none; cursor: pointer; }
            .result { margin: 20px 0; padding: 15px; border: 1px solid #ddd; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔍 NHAI Policy Circulars Search</h1>
            <form method="post">
                <input type="text" name="query" placeholder="Enter your question about NHAI policies..." required>
                <button type="submit">Search</button>
            </form>
            <div id="results"></div>
        </div>
    </body>
    </html>
    """

@app.post("/search")
async def search(query: str = Form(...)):
    results = rag.search(query, top_k=5)
    return {"query": query, "results": results}

@app.post("/answer")
async def answer(question: str = Form(...)):
    answer = rag.answer_question(question)
    return {"question": question, "answer": answer}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
        
        with open(self.ragflow_dir / "web_interface.py", 'w') as f:
            f.write(web_code)
        
        print("✅ Web interface created")
    
    def run_complete_setup(self):
        """Run complete setup"""
        print("🚀 STARTING COMPLETE RAGFLOW SETUP")
        print("=" * 60)
        
        # Step 1: Setup RAGFlow
        self.setup_ragflow()
        
        # Step 2: Get API token
        if not self.get_huggingface_token():
            print("❌ Setup failed - no API token")
            return False
        
        # Step 3: Test models
        self.test_models()
        
        # Step 4: Create RAG system
        self.create_simple_rag_system()
        
        # Step 5: Create web interface
        self.create_web_interface()
        
        print("\n🎉 SETUP COMPLETED!")
        print("=" * 30)
        print("📁 Files created:")
        print(f"   📄 RAG System: {self.ragflow_dir}/simple_rag.py")
        print(f"   🌐 Web Interface: {self.ragflow_dir}/web_interface.py")
        print("\n🚀 Next steps:")
        print("   1. Run: py ragflow_integration/ragflow_simple/simple_rag.py")
        print("   2. Run: py ragflow_integration/ragflow_simple/web_interface.py")
        print("   3. Open: http://localhost:8000")
        
        return True

if __name__ == "__main__":
    setup = RAGFlowNoDockerSetup()
    setup.run_complete_setup() 