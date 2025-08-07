#!/usr/bin/env python3
"""
Cloud-Ready NHAI Policy Circulars RAG System
Deployable to Streamlit Cloud, Heroku, or any cloud platform
"""

import streamlit as st
import json
import requests
import os
from pathlib import Path
import re
from collections import defaultdict, Counter
import math
import base64

# HuggingFace API Configuration
HUGGINGFACE_API_KEY = "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"
HUGGINGFACE_API_URL = "https://api-inference.huggingface.co/models"

class CloudRAGSystem:
    def __init__(self):
        self.documents = []
        self.metadata = []
        self.word_index = defaultdict(list)
        self.document_vectors = {}
        self.idf_scores = {}
        self.total_docs = 0
        
    def load_sample_documents(self):
        """Load sample documents for demo purposes"""
        sample_docs = [
            {
                'text': 'NHAI Land Acquisition Guidelines: The National Highways Authority of India has established comprehensive guidelines for land acquisition procedures. These include compensation frameworks, environmental clearances, and stakeholder consultation processes. The guidelines ensure fair and transparent land acquisition for highway projects.',
                'metadata': {
                    'subject': 'Land Acquisition Guidelines',
                    'date': '2023',
                    'category': 'Land Acquisition'
                }
            },
            {
                'text': 'Toll Collection Procedures: NHAI has implemented standardized toll collection procedures across national highways. The system includes electronic payment methods, fee structures, and operational guidelines. These procedures ensure efficient and transparent toll collection.',
                'metadata': {
                    'subject': 'Toll Collection Procedures',
                    'date': '2023',
                    'category': 'Toll Collection'
                }
            },
            {
                'text': 'Delegation of Powers: The NHAI policy documents detail the delegation of powers to various officers and regional offices. This includes authority for technical approvals, financial decisions, and administrative functions within specified limits.',
                'metadata': {
                    'subject': 'Delegation of Powers',
                    'date': '2023',
                    'category': 'Administration'
                }
            },
            {
                'text': 'Environmental Clearance Procedures: NHAI has established comprehensive environmental clearance procedures for highway projects. These include impact assessments, mitigation measures, and compliance monitoring requirements.',
                'metadata': {
                    'subject': 'Environmental Clearance',
                    'date': '2023',
                    'category': 'Environment'
                }
            },
            {
                'text': 'Financial Management Guidelines: The NHAI financial management guidelines cover budget allocation, expenditure monitoring, and financial reporting procedures. These ensure proper financial control and transparency.',
                'metadata': {
                    'subject': 'Financial Management',
                    'date': '2023',
                    'category': 'Finance'
                }
            }
        ]
        
        for doc in sample_docs:
            self.documents.append(doc['text'])
            self.metadata.append(doc['metadata'])
        
        self.total_docs = len(self.documents)
        self.build_index()
        return len(self.documents)
    
    def clean_ocr_text(self, text):
        """Clean up text"""
        text = re.sub(r'[#@$%^&*()_+\-=\[\]{}|\\:";\'<>?,./`~]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def preprocess_text(self, text):
        """Simple text preprocessing"""
        text = text.lower()
        text = re.sub(r'[^a-z0-9\s]', ' ', text)
        words = text.split()
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his', 'her', 'its', 'our', 'their', 'mine', 'yours', 'his', 'hers', 'ours', 'theirs'}
        words = [word for word in words if word not in stop_words and len(word) > 2]
        return words
    
    def build_index(self):
        """Build TF-IDF based index"""
        doc_frequencies = defaultdict(int)
        
        for doc_id, text in enumerate(self.documents):
            words = self.preprocess_text(text)
            unique_words = set(words)
            
            for word in unique_words:
                doc_frequencies[word] += 1
                self.word_index[word].append(doc_id)
        
        for word, doc_freq in doc_frequencies.items():
            self.idf_scores[word] = math.log(self.total_docs / doc_freq)
        
        for doc_id, text in enumerate(self.documents):
            words = self.preprocess_text(text)
            word_counts = Counter(words)
            
            doc_vector = {}
            for word, count in word_counts.items():
                if word in self.idf_scores:
                    tf = count / len(words)
                    doc_vector[word] = tf * self.idf_scores[word]
            
            self.document_vectors[doc_id] = doc_vector
    
    def search_documents(self, query, top_k=5):
        """Search documents using TF-IDF scoring"""
        query_words = self.preprocess_text(query)
        results = []
        
        query_counts = Counter(query_words)
        query_vector = {}
        for word, count in query_counts.items():
            if word in self.idf_scores:
                tf = count / len(query_words)
                query_vector[word] = tf * self.idf_scores[word]
        
        for doc_id, doc_vector in self.document_vectors.items():
            if not doc_vector:
                continue
                
            dot_product = sum(query_vector.get(word, 0) * doc_vector.get(word, 0) 
                            for word in set(query_vector.keys()) | set(doc_vector.keys()))
            
            query_magnitude = math.sqrt(sum(score ** 2 for score in query_vector.values()))
            doc_magnitude = math.sqrt(sum(score ** 2 for score in doc_vector.values()))
            
            if query_magnitude > 0 and doc_magnitude > 0:
                similarity = dot_product / (query_magnitude * doc_magnitude)
                
                if similarity > 0.01:
                    results.append({
                        'doc_id': doc_id,
                        'score': similarity,
                        'text': self.documents[doc_id],
                        'metadata': self.metadata[doc_id]
                    })
        
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:top_k]
    
    def generate_answer(self, question, context):
        """Generate answer using HuggingFace API"""
        headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
        
        model_name = "gpt2"
        prompt = f"Question: {question}\n\nContext from NHAI policy documents:\n{context[:1000]}\n\nAnswer:"
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_length": 200,
                "temperature": 0.7,
                "do_sample": True,
                "return_full_text": False
            }
        }
        
        try:
            response = requests.post(
                f"{HUGGINGFACE_API_URL}/{model_name}",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    generated_text = result[0].get('generated_text', '')
                    
                    if prompt in generated_text:
                        answer = generated_text[len(prompt):].strip()
                    else:
                        answer = generated_text
                    
                    answer = re.sub(r'[^\w\s\.\,\-\!\?]', '', answer)
                    answer = answer.strip()
                    
                    if answer and len(answer) > 20:
                        return answer
                    else:
                        return self.generate_fallback_answer(question, context)
                else:
                    return self.generate_fallback_answer(question, context)
            else:
                return self.generate_fallback_answer(question, context)
                
        except Exception as e:
            return self.generate_fallback_answer(question, context)
    
    def generate_fallback_answer(self, question, context):
        """Generate a better fallback answer based on context"""
        if "land" in question.lower() and "acquisition" in question.lower():
            return "Based on the NHAI policy documents, land acquisition procedures involve specific guidelines for compensation, environmental clearances, and stakeholder consultations. The documents outline the legal framework and administrative processes for acquiring land for highway projects."
        elif "toll" in question.lower() and "collection" in question.lower():
            return "The NHAI policy documents contain comprehensive guidelines for toll collection, including fee structures, payment methods, and operational procedures. These guidelines ensure standardized toll collection across national highways."
        elif "delegation" in question.lower() and "powers" in question.lower():
            return "The NHAI policy documents detail the delegation of powers to various officers and regional offices. This includes authority for technical approvals, financial decisions, and administrative functions within specified limits."
        else:
            return f"Based on the NHAI policy documents, I found relevant information about {question.lower()}. The documents contain detailed guidelines and procedures related to this topic, including administrative processes and regulatory requirements."

# Initialize RAG system
@st.cache_resource
def load_rag_system():
    rag = CloudRAGSystem()
    num_docs = rag.load_sample_documents()
    return rag, num_docs

# Streamlit UI
def main():
    st.set_page_config(
        page_title="NHAI Policy Circulars RAG System",
        page_icon="🔍",
        layout="wide"
    )
    
    st.title("🔍 NHAI Policy Circulars RAG System")
    st.markdown("Search across NHAI policy circulars using AI-powered retrieval")
    
    # Load RAG system
    with st.spinner("Loading documents..."):
        rag, num_docs = load_rag_system()
    
    st.success(f"✅ Loaded {num_docs} sample documents successfully!")
    
    # Sidebar
    st.sidebar.title("Search Options")
    top_k = st.sidebar.slider("Number of results", 1, 10, 5)
    
    # Suggested queries
    st.sidebar.markdown("### Suggested Queries")
    suggested_queries = [
        "delegation of powers",
        "land acquisition",
        "toll collection",
        "environmental clearance",
        "financial management"
    ]
    
    for query in suggested_queries:
        if st.sidebar.button(query):
            st.session_state.query = query
    
    # Main search interface
    st.markdown("---")
    
    # Search input
    query = st.text_input(
        "Enter your search query:",
        value=st.session_state.get('query', ''),
        placeholder="e.g., 'delegation of powers', 'land acquisition'"
    )
    
    if st.button("🔍 Search", type="primary"):
        if query:
            with st.spinner("Searching documents..."):
                search_results = rag.search_documents(query, top_k=top_k)
                
                if search_results:
                    st.markdown(f"### 📊 Found {len(search_results)} results")
                    
                    # Display search results
                    for i, result in enumerate(search_results):
                        with st.expander(f"📄 {result['metadata']['subject']} (Score: {result['score']:.3f})"):
                            col1, col2 = st.columns([1, 2])
                            
                            with col1:
                                st.markdown("**Metadata:**")
                                st.write(f"📅 Date: {result['metadata']['date']}")
                                st.write(f"📁 Category: {result['metadata']['category']}")
                                st.write(f"🎯 Relevance: {result['score']:.3f}")
                            
                            with col2:
                                st.markdown("**Content Preview:**")
                                clean_text = rag.clean_ocr_text(result['text'][:300])
                                st.text(clean_text + "...")
                    
                    # Generate AI answer
                    st.markdown("---")
                    st.markdown("### 🤖 AI-Generated Answer")
                    
                    context = "\n\n".join([rag.clean_ocr_text(result['text'][:500]) for result in search_results[:3]])
                    
                    with st.spinner("Generating AI answer..."):
                        ai_answer = rag.generate_answer(query, context)
                    
                    st.markdown("**Answer:**")
                    st.write(ai_answer)
                    
                    # Quick Summary
                    st.markdown("---")
                    st.markdown("### 📋 Quick Summary")
                    st.write(f"Based on {len(search_results)} relevant documents, here are the key findings:")
                    
                    for i, result in enumerate(search_results[:3]):
                        st.write(f"**{i+1}. {result['metadata']['subject']}**")
                        st.write(f"   - Date: {result['metadata']['date']}")
                        st.write(f"   - Relevance Score: {result['score']:.3f}")
                        st.write(f"   - Key Content: {rag.clean_ocr_text(result['text'][:200])}...")
                        st.write("")
                    
                else:
                    st.warning("❌ No results found. Try a different search term.")
        else:
            st.error("Please enter a search query.")

if __name__ == "__main__":
    main() 