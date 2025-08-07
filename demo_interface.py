#!/usr/bin/env python3
"""
Interactive Demo Interface for NHAI RAG System
"""

import json
import re
from pathlib import Path
from collections import defaultdict
import math

class DemoRAGSystem:
    def __init__(self):
        self.documents = []
        self.metadata = []
        self.word_index = defaultdict(list)
        self.document_vectors = {}
        
    def load_documents(self, extracted_dir):
        """Load all extracted documents"""
        print("Loading documents...")
        
        json_files = list(Path(extracted_dir).glob("*.json"))
        print(f"Found {len(json_files)} JSON files")
        
        for i, json_file in enumerate(json_files):
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
        
        print(f"Successfully loaded {len(self.documents)} documents")
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
        print("Building search index...")
        
        for doc_id, text in enumerate(self.documents):
            words = self.preprocess_text(text)
            
            doc_vector = defaultdict(int)
            for word in words:
                doc_vector[word] += 1
                self.word_index[word].append(doc_id)
            
            self.document_vectors[doc_id] = dict(doc_vector)
        
        print("Search index built successfully")
        return True
    
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

def main():
    print("=" * 60)
    print("NHAI POLICY CIRCULARS RAG SYSTEM - DEMO")
    print("=" * 60)
    print()
    print("Loading RAG system...")
    
    # Initialize RAG system
    rag = DemoRAGSystem()
    
    # Load documents
    num_docs = rag.load_documents("output/extracted_texts")
    
    if num_docs == 0:
        print("No documents found!")
        return
    
    # Build index
    rag.build_index()
    
    print()
    print("=" * 60)
    print("RAG SYSTEM READY FOR DEMO!")
    print("=" * 60)
    print(f"📚 Total Documents: {num_docs}")
    print("🔍 Search across all NHAI policy circulars")
    print("💡 Type 'quit' to exit")
    print("=" * 60)
    
    # Demo queries
    demo_queries = [
        "delegation of powers",
        "land acquisition",
        "policy circular",
        "administration",
        "finance",
        "toll collection",
        "road construction",
        "environmental clearance"
    ]
    
    print("\n📝 SUGGESTED DEMO QUERIES:")
    for i, query in enumerate(demo_queries, 1):
        print(f"   {i}. {query}")
    
    print("\n" + "=" * 60)
    
    while True:
        print()
        query = input("🔍 Enter your search query: ").strip()
        
        if query.lower() in ['quit', 'exit', 'q']:
            print("👋 Demo completed!")
            break
        
        if not query:
            continue
        
        print(f"\n🔍 Searching for: '{query}'")
        print("-" * 50)
        
        results = rag.search_simple(query, top_k=5)
        
        if results:
            print(f"📊 Found {len(results)} results:\n")
            
            for i, result in enumerate(results, 1):
                metadata = result['metadata']
                print(f"{i}. 📄 {metadata.get('subject', 'No subject')}")
                print(f"   📅 Date: {metadata.get('date', 'Unknown')}")
                print(f"   📁 Category: {metadata.get('category', 'Unknown')}")
                print(f"   🎯 Relevance Score: {result['score']}")
                print(f"   📝 Content Preview: {result['text'][:150]}...")
                print()
        else:
            print("❌ No results found")
        
        print("-" * 50)

if __name__ == "__main__":
    main() 