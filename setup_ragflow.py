#!/usr/bin/env python3
"""
Simple RAG Setup - No Docker, No Emojis
Creates a working RAG system immediately
"""

import json
import os
import time
from pathlib import Path
from datetime import datetime

def create_working_rag_system():
    """Create a working RAG system without external API"""
    print("CREATING WORKING RAG SYSTEM")
    print("=" * 50)
    
    # Create directory
    ragflow_dir = Path("ragflow_integration/ragflow_simple")
    ragflow_dir.mkdir(parents=True, exist_ok=True)
    
    # Create the RAG system
    rag_code = '''
import json
import os
from pathlib import Path
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
import numpy as np

class WorkingRAGSystem:
    def __init__(self):
        print("Initializing RAG System...")
        self.embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        
        # Setup ChromaDB
        self.client = chromadb.Client(Settings(
            chroma_db_impl="duckdb+parquet", 
            persist_directory="./chroma_db"
        ))
        
        # Create or get collection
        try:
            self.collection = self.client.get_collection("nhai_documents")
            print("Using existing collection")
        except:
            self.collection = self.client.create_collection("nhai_documents")
            print("Created new collection")
        
    def load_documents(self, extracted_dir):
        """Load all extracted documents"""
        print("Loading documents...")
        documents = []
        metadata = []
        ids = []
        
        json_files = list(Path(extracted_dir).glob("*.json"))
        print(f"Found {len(json_files)} JSON files")
        
        for i, json_file in enumerate(json_files):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if data.get('extracted_text'):
                    documents.append(data['extracted_text'])
                    metadata.append({
                        'filename': data.get('filename', ''),
                        'subject': data.get('subject', ''),
                        'date': data.get('date', ''),
                        'category': data.get('category', ''),
                        'file_id': str(json_file.stem)
                    })
                    ids.append(str(json_file.stem))
                    
                if (i + 1) % 100 == 0:
                    print(f"   Loaded {i + 1}/{len(json_files)} documents")
                    
            except Exception as e:
                print(f"Error loading {json_file}: {e}")
        
        print(f"Successfully loaded {len(documents)} documents")
        return documents, metadata, ids
    
    def create_embeddings(self, documents):
        """Create embeddings for documents"""
        print("Creating embeddings...")
        
        # Process in batches to avoid memory issues
        batch_size = 50
        all_embeddings = []
        
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            batch_embeddings = self.embedding_model.encode(batch)
            all_embeddings.extend(batch_embeddings)
            
            if (i + batch_size) % 200 == 0:
                print(f"   Created embeddings for {min(i + batch_size, len(documents))}/{len(documents)} documents")
        
        print(f"Created {len(all_embeddings)} embeddings")
        return all_embeddings
    
    def build_index(self, documents, metadata, ids):
        """Build search index"""
        print("Building search index...")
        
        if not documents:
            print("No documents to index")
            return False
        
        # Create embeddings
        embeddings = self.create_embeddings(documents)
        
        # Add to ChromaDB in batches
        batch_size = 100
        for i in range(0, len(documents), batch_size):
            end_idx = min(i + batch_size, len(documents))
            
            batch_docs = documents[i:end_idx]
            batch_metadata = metadata[i:end_idx]
            batch_ids = ids[i:end_idx]
            batch_embeddings = embeddings[i:end_idx]
            
            self.collection.add(
                embeddings=[emb.tolist() for emb in batch_embeddings],
                documents=batch_docs,
                metadatas=batch_metadata,
                ids=batch_ids
            )
            
            if (i + batch_size) % 200 == 0:
                print(f"   Indexed {min(i + batch_size, len(documents))}/{len(documents)} documents")
        
        print("Search index built successfully")
        return True
    
    def search(self, query, top_k=5):
        """Search documents"""
        try:
            query_embedding = self.embedding_model.encode([query])
            results = self.collection.query(
                query_embeddings=query_embedding.tolist(),
                n_results=top_k
            )
            return results
        except Exception as e:
            print(f"Search error: {e}")
            return None

# Global RAG instance
rag_system = None

def initialize_rag():
    """Initialize the RAG system"""
    global rag_system
    if rag_system is None:
        rag_system = WorkingRAGSystem()
    return rag_system

def load_and_index_documents():
    """Load and index all documents"""
    global rag_system
    rag_system = initialize_rag()
    
    documents, metadata, ids = rag_system.load_documents("output/extracted_texts")
    success = rag_system.build_index(documents, metadata, ids)
    
    if success:
        print("RAG system ready for queries!")
        return True
    else:
        print("Failed to build index")
        return False

def search_documents(query, top_k=5):
    """Search documents"""
    global rag_system
    if rag_system is None:
        print("RAG system not initialized")
        return None
    
    return rag_system.search(query, top_k)

if __name__ == "__main__":
    print("Starting RAG System Setup")
    print("=" * 40)
    
    # Initialize and load documents
    success = load_and_index_documents()
    
    if success:
        print("\\nTesting search functionality...")
        
        # Test searches
        test_queries = [
            "delegation of powers",
            "policy circular",
            "administration",
            "finance"
        ]
        
        for query in test_queries:
            print(f"\\nSearching: '{query}'")
            results = search_documents(query, top_k=3)
            
            if results and results['documents']:
                print(f"   Found {len(results['documents'][0])} results")
                for i, doc in enumerate(results['documents'][0][:2]):
                    print(f"   {i+1}. {doc[:100]}...")
            else:
                print("   No results found")
        
        print("\\nRAG system is working!")
        print("Index saved in: ./chroma_db/")
        print("Ready for queries!")
'''
    
    with open(ragflow_dir / "working_rag.py", 'w', encoding='utf-8') as f:
        f.write(rag_code)
    
    print("Working RAG system created")

def create_simple_interface():
    """Create a simple interface"""
    print("\\nCreating Simple Interface")
    print("=" * 30)
    
    interface_code = '''
import json
from pathlib import Path
from working_rag import initialize_rag, search_documents

def main():
    print("NHAI Policy Circulars Search")
    print("=" * 40)
    
    # Initialize RAG system
    rag = initialize_rag()
    
    # Load documents if not already loaded
    if not Path("./chroma_db").exists():
        print("Loading documents for first time...")
        from working_rag import load_and_index_documents
        load_and_index_documents()
    
    print("\\nReady for queries! Type 'quit' to exit.")
    print("Example queries:")
    print("   - delegation of powers")
    print("   - policy circular")
    print("   - administration")
    print("   - finance")
    print()
    
    while True:
        query = input("Enter your search query: ").strip()
        
        if query.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break
        
        if not query:
            continue
        
        print(f"\\nSearching for: '{query}'")
        print("-" * 40)
        
        results = search_documents(query, top_k=5)
        
        if results and results['documents']:
            docs = results['documents'][0]
            metadatas = results['metadatas'][0]
            
            print(f"Found {len(docs)} results:\\n")
            
            for i, (doc, metadata) in enumerate(zip(docs, metadatas)):
                print(f"{i+1}. {metadata.get('subject', 'No subject')}")
                print(f"   Date: {metadata.get('date', 'Unknown')}")
                print(f"   Category: {metadata.get('category', 'Unknown')}")
                print(f"   Content: {doc[:200]}...")
                print()
        else:
            print("No results found")
        
        print("-" * 40)

if __name__ == "__main__":
    main()
'''
    
    ragflow_dir = Path("ragflow_integration/ragflow_simple")
    with open(ragflow_dir / "search_interface.py", 'w', encoding='utf-8') as f:
        f.write(interface_code)
    
    print("Search interface created")

def run_setup():
    """Run the complete setup"""
    print("QUICK RAG SETUP - NO DOCKER")
    print("=" * 50)
    
    # Step 1: Create RAG system
    create_working_rag_system()
    
    # Step 2: Create interface
    create_simple_interface()
    
    print("\\nSETUP COMPLETED!")
    print("=" * 30)
    print("Files created:")
    print("   RAG System: ragflow_integration/ragflow_simple/working_rag.py")
    print("   Search Interface: ragflow_integration/ragflow_simple/search_interface.py")
    print("\\nNext steps:")
    print("   1. Run: py ragflow_integration/ragflow_simple/working_rag.py")
    print("   2. Or run: py ragflow_integration/ragflow_simple/search_interface.py")
    print("\\nEstimated time for first run: 10-15 minutes")
    print("Subsequent runs will be much faster!")
    
        return True

if __name__ == "__main__":
    run_setup() 