#!/usr/bin/env python3
"""
Simple RAG System - No Complex Dependencies
Uses only basic Python libraries
"""

import json
import os
import re
from pathlib import Path
from collections import defaultdict
import math

class SimpleRAGSystem:
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
                    
                if (i + 1) % 100 == 0:
                    print(f"   Loaded {i + 1}/{len(json_files)} documents")
                    
            except Exception as e:
                print(f"Error loading {json_file}: {e}")
        
        print(f"Successfully loaded {len(self.documents)} documents")
        return len(self.documents)
    
    def preprocess_text(self, text):
        """Simple text preprocessing"""
        # Convert to lowercase
        text = text.lower()
        # Remove special characters, keep only letters, numbers, and spaces
        text = re.sub(r'[^a-z0-9\s]', ' ', text)
        # Split into words
        words = text.split()
        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his', 'her', 'its', 'our', 'their', 'mine', 'yours', 'his', 'hers', 'ours', 'theirs'}
        words = [word for word in words if word not in stop_words and len(word) > 2]
        return words
    
    def build_index(self):
        """Build simple word-based index"""
        print("Building search index...")
        
        # Process each document
        for doc_id, text in enumerate(self.documents):
            words = self.preprocess_text(text)
            
            # Create document vector (word frequency)
            doc_vector = defaultdict(int)
            for word in words:
                doc_vector[word] += 1
                self.word_index[word].append(doc_id)
            
            self.document_vectors[doc_id] = dict(doc_vector)
            
            if (doc_id + 1) % 100 == 0:
                print(f"   Indexed {doc_id + 1}/{len(self.documents)} documents")
        
        print("Search index built successfully")
        return True
    
    def calculate_tf_idf(self, word, doc_id):
        """Calculate TF-IDF score for a word in a document"""
        if doc_id not in self.document_vectors or word not in self.document_vectors[doc_id]:
            return 0
        
        # Term Frequency (TF)
        tf = self.document_vectors[doc_id][word]
        
        # Document Frequency (DF)
        df = len(self.word_index[word])
        
        # Inverse Document Frequency (IDF)
        idf = math.log(len(self.documents) / (df + 1)) + 1
        
        return tf * idf
    
    def search(self, query, top_k=5):
        """Search documents using TF-IDF"""
        print(f"Searching for: '{query}'")
        
        # Preprocess query
        query_words = self.preprocess_text(query)
        
        # Calculate scores for each document
        scores = []
        for doc_id in range(len(self.documents)):
            score = 0
            for word in query_words:
                score += self.calculate_tf_idf(word, doc_id)
            scores.append((doc_id, score))
        
        # Sort by score (descending)
        scores.sort(key=lambda x: x[1], reverse=True)
        
        # Get top results
        results = []
        for doc_id, score in scores[:top_k]:
            if score > 0:
                results.append({
                    'doc_id': doc_id,
                    'score': score,
                    'text': self.documents[doc_id],
                    'metadata': self.metadata[doc_id]
                })
        
        return results
    
    def search_simple(self, query, top_k=5):
        """Simple keyword search"""
        print(f"Searching for: '{query}'")
        
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
        
        # Sort by number of matches
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:top_k]

def main():
    print("Simple RAG System for NHAI Policy Circulars")
    print("=" * 50)
    
    # Initialize RAG system
    rag = SimpleRAGSystem()
    
    # Load documents
    num_docs = rag.load_documents("output/extracted_texts")
    
    if num_docs == 0:
        print("No documents found!")
        return
    
    # Build index
    rag.build_index()
    
    print("\nRAG system ready for queries!")
    print("=" * 30)
    
    # Test searches
    test_queries = [
        "delegation of powers",
        "policy circular",
        "administration",
        "finance",
        "land acquisition"
    ]
    
    for query in test_queries:
        print(f"\nSearching: '{query}'")
        results = rag.search_simple(query, top_k=3)
        
        if results:
            print(f"   Found {len(results)} results:")
            for i, result in enumerate(results):
                metadata = result['metadata']
                print(f"   {i+1}. {metadata.get('subject', 'No subject')}")
                print(f"      Date: {metadata.get('date', 'Unknown')}")
                print(f"      Category: {metadata.get('category', 'Unknown')}")
                print(f"      Score: {result['score']}")
                print(f"      Content: {result['text'][:100]}...")
                print()
        else:
            print("   No results found")
    
    print("=" * 50)
    print("Simple RAG system is working!")
    print("Ready for interactive queries!")

if __name__ == "__main__":
    main() 