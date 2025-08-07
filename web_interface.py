#!/usr/bin/env python3
"""
Web Interface for NHAI RAG System
Simple Flask-based web interface
"""

from flask import Flask, render_template_string, request, jsonify
import json
import re
from pathlib import Path
from collections import defaultdict
import math

app = Flask(__name__)

class WebRAGSystem:
    def __init__(self):
        self.documents = []
        self.metadata = []
        self.word_index = defaultdict(list)
        self.document_vectors = {}
        self.loaded = False
        
    def load_documents(self, extracted_dir):
        """Load all extracted documents"""
        if self.loaded:
            return len(self.documents)
            
        json_files = list(Path(extracted_dir).glob("*.json"))
        
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if data.get('extracted_text'):
                    text = data['extracted_text']
                    self.documents.append(text)
                    self.metadata.append({
                        'filename': data.get('filename', ''),
                        'subject': data.get('subject', ''),
                        'date': data.get('date', ''),
                        'category': data.get('category', ''),
                        'file_id': str(json_file.stem)
                    })
                    
            except Exception as e:
                continue
        
        self.build_index()
        self.loaded = True
        return len(self.documents)
    
    def preprocess_text(self, text):
        """Simple text preprocessing"""
        text = text.lower()
        text = re.sub(r'[^a-z0-9\s]', ' ', text)
        words = text.split()
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his', 'her', 'its', 'our', 'their', 'mine', 'yours', 'his', 'hers', 'ours', 'theirs'}
        words = [word for word in words if word not in stop_words and len(word) > 2]
        return words
    
    def build_index(self):
        """Build simple word-based index"""
        for doc_id, text in enumerate(self.documents):
            words = self.preprocess_text(text)
            
            doc_vector = defaultdict(int)
            for word in words:
                doc_vector[word] += 1
                self.word_index[word].append(doc_id)
            
            self.document_vectors[doc_id] = dict(doc_vector)
    
    def search_simple(self, query, top_k=5):
        """Simple keyword search"""
        query_words = self.preprocess_text(query)
        results = []
        
        for doc_id, text in enumerate(self.documents):
            text_words = self.preprocess_text(text)
            matches = sum(1 for word in query_words if word in text_words)
            
            if matches > 0:
                results.append({
                    'doc_id': doc_id,
                    'score': matches,
                    'text': text,
                    'metadata': self.metadata[doc_id]
                })
        
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:top_k]

# Initialize RAG system
rag_system = WebRAGSystem()

# HTML template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NHAI Policy Circulars RAG System</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 {
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }
        .header p {
            margin: 10px 0 0 0;
            opacity: 0.9;
            font-size: 1.1em;
        }
        .search-section {
            padding: 40px;
            background: #f8f9fa;
        }
        .search-box {
            display: flex;
            gap: 15px;
            margin-bottom: 30px;
        }
        .search-input {
            flex: 1;
            padding: 15px 20px;
            border: 2px solid #e9ecef;
            border-radius: 10px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        .search-input:focus {
            outline: none;
            border-color: #667eea;
        }
        .search-button {
            padding: 15px 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            cursor: pointer;
            transition: transform 0.2s;
        }
        .search-button:hover {
            transform: translateY(-2px);
        }
        .suggestions {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 20px;
        }
        .suggestion {
            padding: 8px 16px;
            background: white;
            border: 1px solid #dee2e6;
            border-radius: 20px;
            cursor: pointer;
            transition: all 0.3s;
            font-size: 14px;
        }
        .suggestion:hover {
            background: #667eea;
            color: white;
            border-color: #667eea;
        }
        .results-section {
            padding: 40px;
        }
        .result-card {
            background: white;
            border: 1px solid #e9ecef;
            border-radius: 10px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            transition: transform 0.2s;
        }
        .result-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        }
        .result-title {
            font-size: 1.3em;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 10px;
        }
        .result-meta {
            display: flex;
            gap: 20px;
            margin-bottom: 15px;
            font-size: 14px;
            color: #6c757d;
        }
        .result-score {
            background: #667eea;
            color: white;
            padding: 4px 12px;
            border-radius: 15px;
            font-weight: 600;
        }
        .result-content {
            color: #495057;
            line-height: 1.6;
        }
        .stats {
            background: #e9ecef;
            padding: 20px;
            text-align: center;
            color: #6c757d;
        }
        .loading {
            text-align: center;
            padding: 40px;
            color: #6c757d;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 NHAI Policy Circulars RAG System</h1>
            <p>Search across 1,629 NHAI policy circulars using AI-powered retrieval</p>
        </div>
        
        <div class="search-section">
            <form method="POST" action="/search">
                <div class="search-box">
                    <input type="text" name="query" class="search-input" placeholder="Enter your search query (e.g., 'delegation of powers', 'land acquisition')" value="{{ query or '' }}" required>
                    <button type="submit" class="search-button">🔍 Search</button>
                </div>
            </form>
            
            <div class="suggestions">
                <div class="suggestion" onclick="setQuery('delegation of powers')">delegation of powers</div>
                <div class="suggestion" onclick="setQuery('land acquisition')">land acquisition</div>
                <div class="suggestion" onclick="setQuery('policy circular')">policy circular</div>
                <div class="suggestion" onclick="setQuery('administration')">administration</div>
                <div class="suggestion" onclick="setQuery('finance')">finance</div>
                <div class="suggestion" onclick="setQuery('toll collection')">toll collection</div>
                <div class="suggestion" onclick="setQuery('road construction')">road construction</div>
                <div class="suggestion" onclick="setQuery('environmental clearance')">environmental clearance</div>
            </div>
        </div>
        
        {% if results %}
        <div class="results-section">
            <h2>📊 Search Results ({{ results|length }} found)</h2>
            {% for result in results %}
            <div class="result-card">
                <div class="result-title">{{ result.metadata.subject or 'No subject' }}</div>
                <div class="result-meta">
                    <span>📅 {{ result.metadata.date or 'Unknown date' }}</span>
                    <span>📁 {{ result.metadata.category or 'No category' }}</span>
                    <span class="result-score">🎯 Score: {{ result.score }}</span>
                </div>
                <div class="result-content">
                    {{ result.text[:300] }}...
                </div>
            </div>
            {% endfor %}
        </div>
        {% elif query %}
        <div class="results-section">
            <div class="loading">
                <h3>❌ No results found for "{{ query }}"</h3>
                <p>Try a different search term or check the spelling.</p>
            </div>
        </div>
        {% endif %}
        
        <div class="stats">
            <p>📚 Total Documents: {{ total_docs }} | 🔍 Ready for queries</p>
        </div>
    </div>
    
    <script>
        function setQuery(query) {
            document.querySelector('.search-input').value = query;
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    # Load documents if not already loaded
    total_docs = rag_system.load_documents("output/extracted_texts")
    return render_template_string(HTML_TEMPLATE, results=None, query=None, total_docs=total_docs)

@app.route('/search', methods=['POST'])
def search():
    query = request.form.get('query', '').strip()
    if not query:
        return home()
    
    # Load documents if not already loaded
    total_docs = rag_system.load_documents("output/extracted_texts")
    
    # Perform search
    results = rag_system.search_simple(query, top_k=10)
    
    return render_template_string(HTML_TEMPLATE, results=results, query=query, total_docs=total_docs)

if __name__ == '__main__':
    print("🌐 Starting NHAI RAG System Web Interface...")
    print("📚 Loading documents...")
    
    # Load documents
    total_docs = rag_system.load_documents("output/extracted_texts")
    print(f"✅ Loaded {total_docs} documents")
    
    print("🚀 Starting web server...")
    print("🌐 Open your browser and go to: http://localhost:5000")
    print("💡 Press Ctrl+C to stop the server")
    
    app.run(host='0.0.0.0', port=5000, debug=False) 