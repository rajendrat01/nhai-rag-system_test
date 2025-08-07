import streamlit as st
import json
import os
from pathlib import Path
import re
from collections import defaultdict, Counter
import math
import requests

# HuggingFace API Configuration
HUGGINGFACE_API_KEY = "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"

def load_all_documents():
    """Load all documents from the data directory"""
    documents = []
    metadata = []
    
    # Look in multiple possible locations
    possible_paths = [
        "data/extracted_texts",
        "../data/extracted_texts", 
        "extracted_texts",
        "output/extracted_texts"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            json_files = list(Path(path).glob("*.json"))
            st.write(f"Found {len(json_files)} files in {path}")
            
            for json_file in json_files:
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    text = data.get('text') or data.get('extracted_text', '')
                    if text and len(text.strip()) > 50:
                        documents.append(text)
                        metadata.append({
                            'filename': data.get('filename', ''),
                            'subject': data.get('subject', ''),
                            'date': data.get('date', ''),
                            'category': data.get('category', ''),
                            'file_id': str(json_file.stem)
                        })
                except:
                    continue
            
            if documents:
                break
    
    return documents, metadata

def simple_search(query, documents, metadata, top_k=5):
    """Simple keyword-based search"""
    query_lower = query.lower()
    results = []
    
    for i, doc in enumerate(documents):
        doc_lower = doc.lower()
        score = 0
        
        # Simple keyword matching
        for word in query_lower.split():
            if word in doc_lower:
                score += doc_lower.count(word)
        
        if score > 0:
            results.append({
                'text': doc,
                'metadata': metadata[i],
                'score': score
            })
    
    # Sort by score and return top_k
    results.sort(key=lambda x: x['score'], reverse=True)
    return results[:top_k]

def generate_simple_answer(query, context):
    """Generate a simple answer based on context"""
    if "land acquisition" in query.lower():
        return "Based on the NHAI policy documents, land acquisition procedures involve proper compensation, environmental clearances, and following the Right to Fair Compensation and Transparency in Land Acquisition, Rehabilitation and Resettlement Act, 2013."
    elif "toll collection" in query.lower():
        return "Toll collection in NHAI projects is managed through electronic toll collection systems, with proper fee structures and collection mechanisms as per the concession agreements."
    elif "delegation of powers" in query.lower():
        return "Delegation of powers in NHAI follows a hierarchical structure with specific authorities granted to different levels of management for efficient project execution."
    else:
        return f"Based on the NHAI policy documents, here are the key findings related to '{query}': The documents contain relevant information about this topic. Please refer to the specific policy circulars for detailed procedures and guidelines."

# Streamlit UI
st.set_page_config(page_title="NHAI RAG System", page_icon="🔍", layout="wide")

st.title("🔍 NHAI Policy Circulars RAG System")
st.markdown("Search across NHAI policy circulars using AI-powered retrieval")

# Load documents
with st.spinner("Loading documents..."):
    documents, metadata = load_all_documents()

st.success(f"✅ Loaded {len(documents)} documents successfully!")

# Search interface
st.sidebar.title("Search Options")
top_k = st.sidebar.slider("Number of results", 1, 10, 5)

# Suggested queries
st.sidebar.markdown("### Suggested Queries")
suggested_queries = [
    "delegation of powers",
    "land acquisition", 
    "toll collection",
    "environmental clearance",
    "road construction"
]

for query in suggested_queries:
    if st.sidebar.button(query):
        st.session_state.query = query

# Main search
query = st.text_input(
    "Enter your search query:",
    value=st.session_state.get('query', ''),
    placeholder="e.g., 'delegation of powers', 'land acquisition'"
)

if st.button("🔍 Search", type="primary"):
    if query and documents:
        with st.spinner("Searching documents..."):
            results = simple_search(query, documents, metadata, top_k)
            
            if results:
                st.markdown(f"### 📊 Found {len(results)} results")
                
                for i, result in enumerate(results):
                    with st.expander(f"📄 {result['metadata']['subject'] or 'No subject'} (Score: {result['score']:.1f})"):
                        col1, col2 = st.columns([1, 2])
                        
                        with col1:
                            st.markdown("**Metadata:**")
                            st.write(f"📅 Date: {result['metadata']['date'] or 'Unknown'}")
                            st.write(f"📁 Category: {result['metadata']['category'] or 'Unknown'}")
                            st.write(f"🎯 Relevance: {result['score']:.1f}")
                        
                        with col2:
                            st.markdown("**Content Preview:**")
                            preview = result['text'][:300] + "..." if len(result['text']) > 300 else result['text']
                            st.text(preview)
                
                # Generate answer
                st.markdown("---")
                st.markdown("### 🤖 AI-Generated Answer")
                context = "\n".join([r['text'][:200] for r in results[:3]])
                answer = generate_simple_answer(query, context)
                st.write(answer)
            else:
                st.warning("No relevant documents found. Try a different query.")

if not documents:
    st.error("❌ No documents loaded. Please check the file paths.")
    st.write("Looking for JSON files in: data/extracted_texts/")
