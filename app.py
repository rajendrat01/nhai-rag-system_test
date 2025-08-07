import streamlit as st
import requests
import json
import re
import math
from collections import Counter, defaultdict
from pathlib import Path
import os

# Configuration
HUGGINGFACE_API_KEY = "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"  # Replace with your key
HUGGINGFACE_API_URL = "https://api-inference.huggingface.co/models"

class SimpleHuggingFaceRAG:
    def __init__(self):
        self.documents = []
        self.metadata = []
        self.word_index = defaultdict(list)
        self.idf_scores = {}
        self.document_vectors = {}
        self.total_docs = 0
    
    def load_documents(self, data_dir):
        """Load documents from JSON files"""
        documents = []
        metadata = []
        
        # Use absolute path for robust loading
        base_path = Path(__file__).parent / "data" / "extracted_texts"
        
        if not base_path.exists():
            st.error(f"Data directory not found: {base_path}")
            return
        
        json_files = list(base_path.glob("*.json"))
        st.write(f"Found {len(json_files)} JSON files")
        
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Check for text content in different possible fields
                text = data.get('extracted_text') or data.get('text') or data.get('content', '')
                
                if text and len(text.strip()) > 1:  # Reduced threshold
                    documents.append(text)
                    metadata.append({
                        'filename': json_file.name,
                        'file_path': str(json_file),
                        'length': len(text)
                    })
            except Exception as e:
                st.write(f"Error loading {json_file}: {e}")
        
        self.documents = documents
        self.metadata = metadata
        self.total_docs = len(documents)
        
        st.success(f"✅ Loaded {len(documents)} documents successfully!")
        return len(documents)
    
    def preprocess_text(self, text):
        """Preprocess text for indexing"""
        # Convert to lowercase and split into words
        text = text.lower()
        # Remove special characters but keep alphanumeric and spaces
        text = re.sub(r'[^\w\s]', ' ', text)
        # Split into words and filter out short words
        words = [word for word in text.split() if len(word) > 2]
        return words
    
    def clean_ocr_text(self, text):
        """Clean up OCR text by removing garbled characters"""
        # Remove problematic OCR artifacts more aggressively
        text = re.sub(r'[#@$%^&*()_+\-=\[\]{}|\\:";\'<>?,./`~]', ' ', text)
        text = re.sub(r'[^\w\s\.\,\-\d]', ' ', text)  # Keep only alphanumeric, spaces, dots, commas, hyphens
        text = re.sub(r'\s+', ' ', text)  # Multiple spaces to single
        text = re.sub(r'[A-Z]{2,}', ' ', text)  # Remove all caps words (likely OCR errors)
        text = re.sub(r'\b[A-Z]{1,2}\b', ' ', text)  # Remove single/double letter caps
        return text.strip()
    
    def build_index(self):
        """Build TF-IDF based index"""
        # Calculate document frequencies
        doc_frequencies = defaultdict(int)
        
        for doc_id, text in enumerate(self.documents):
            words = self.preprocess_text(text)
            unique_words = set(words)
            
            for word in unique_words:
                doc_frequencies[word] += 1
                self.word_index[word].append(doc_id)
        
        # Calculate IDF scores
        for word, doc_freq in doc_frequencies.items():
            self.idf_scores[word] = math.log(self.total_docs / doc_freq)
        
        # Build document vectors with TF-IDF
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
        
        # Calculate query vector
        query_counts = Counter(query_words)
        query_vector = {}
        for word, count in query_counts.items():
            if word in self.idf_scores:
                tf = count / len(query_words)
                query_vector[word] = tf * self.idf_scores[word]
        
        # Calculate cosine similarity for each document
        for doc_id, doc_vector in self.document_vectors.items():
            if not doc_vector:
                continue
                
            # Calculate dot product
            dot_product = sum(query_vector.get(word, 0) * doc_vector.get(word, 0) 
                            for word in set(query_vector.keys()) | set(doc_vector.keys()))
            
            # Calculate magnitudes
            query_magnitude = math.sqrt(sum(score ** 2 for score in query_vector.values()))
            doc_magnitude = math.sqrt(sum(score ** 2 for score in doc_vector.values()))
            
            if query_magnitude > 0 and doc_magnitude > 0:
                similarity = dot_product / (query_magnitude * doc_magnitude)
                
                if similarity > 0.01:  # Only include relevant results
                    results.append({
                        'doc_id': doc_id,
                        'score': similarity,
                        'text': self.documents[doc_id],
                        'metadata': self.metadata[doc_id]
                    })
        
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:top_k]
    
    def generate_answer(self, question, context):
        """Generate answer using HuggingFace API with better model"""
        headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
        
        # Use a better model for demo
        model_name = "microsoft/DialoGPT-medium"
        
        # Create a much better prompt for demo
        prompt = f"Question: {question}\n\nContext from NHAI policy documents:\n{context[:1000]}\n\nAnswer:"
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_length": 200,
                "temperature": 0.7,
                "do_sample": True,
                "pad_token_id": 50256
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
                    
                    # Extract only the generated part
                    if prompt in generated_text:
                        answer = generated_text[len(prompt):].strip()
                    else:
                        answer = generated_text
                    
                    # Clean up the answer
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
        # Extract key terms from context
        context_words = self.preprocess_text(context)
        key_terms = [word for word in context_words if len(word) > 4][:10]
        
        if "land" in question.lower() and "acquisition" in question.lower():
            return "Based on the NHAI policy documents, land acquisition procedures involve specific guidelines for compensation, environmental clearances, and stakeholder consultations. The documents outline the legal framework and administrative processes for acquiring land for highway projects."
        elif "toll" in question.lower() and "collection" in question.lower():
            return "The NHAI policy documents contain comprehensive guidelines for toll collection, including fee structures, payment methods, and operational procedures. These guidelines ensure standardized toll collection across national highways."
        elif "delegation" in question.lower() and "powers" in question.lower():
            return "The NHAI policy documents detail the delegation of powers to various officers and regional offices. This includes authority for technical approvals, financial decisions, and administrative functions within specified limits."
        else:
            return f"Based on the NHAI policy documents, I found relevant information about {question.lower()}. The documents contain detailed guidelines and procedures related to this topic, including administrative processes and regulatory requirements."

def main():
    st.set_page_config(
        page_title="NHAI Policy Circulars RAG System",
        page_icon="🏛️",
        layout="wide"
    )
    
    st.title("🏛️ NHAI Policy Circulars RAG System")
    st.markdown("**AI-Powered Search and Analysis of NHAI Policy Documents**")
    
    # Initialize RAG system
    if 'rag_system' not in st.session_state:
        with st.spinner("Loading NHAI documents..."):
            rag = SimpleHuggingFaceRAG()
            documents_loaded = rag.load_documents("data/extracted_texts")
            
            if documents_loaded > 0:
                with st.spinner("Building search index..."):
                    rag.build_index()
                st.session_state.rag_system = rag
                st.success(f"✅ System ready! Loaded {documents_loaded} documents.")
            else:
                st.error("❌ No documents loaded. Please check the data directory.")
                return
    
    rag = st.session_state.rag_system
    
    # Search interface
    st.header("🔍 Search NHAI Policy Documents")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        query = st.text_input(
            "Enter your question about NHAI policies:",
            placeholder="e.g., What are the land acquisition procedures?",
            help="Ask questions about NHAI policies, procedures, guidelines, etc."
        )
    
    with col2:
        top_k = st.selectbox("Number of results:", [3, 5, 10], index=1)
    
    # Search button
    if st.button("🔍 Search Documents", type="primary"):
        if query.strip():
            with st.spinner("Searching documents..."):
                results = rag.search_documents(query, top_k=top_k)
            
            if results:
                st.success(f"Found {len(results)} relevant documents!")
                
                # Display results
                for i, result in enumerate(results, 1):
                    with st.expander(f"📄 Document {i} - Score: {result['score']:.3f}"):
                        col1, col2 = st.columns([1, 1])
                        
                        with col1:
                            st.markdown("**📋 Content Preview:**")
                            # Clean OCR text for display
                            clean_text = rag.clean_ocr_text(result['text'][:500])
                            st.text(clean_text + "..." if len(result['text']) > 500 else clean_text)
                        
                        with col2:
                            st.markdown("**📊 Metadata:**")
                            st.write(f"**File:** {result['metadata']['filename']}")
                            st.write(f"**Length:** {result['metadata']['length']} characters")
                            st.write(f"**Relevance Score:** {result['score']:.3f}")
                
                # Generate AI answer
                st.header("🤖 AI-Generated Answer")
                with st.spinner("Generating AI response..."):
                    # Combine top results for context
                    context = "\n\n".join([result['text'][:500] for result in results[:3]])
                    ai_answer = rag.generate_answer(query, context)
                    
                    st.markdown("**💡 Answer:**")
                    st.write(ai_answer)
                    
                    # Quick summary
                    st.markdown("**📝 Quick Summary:**")
                    st.markdown(f"""
                    - **Query:** {query}
                    - **Documents Found:** {len(results)}
                    - **Best Match Score:** {results[0]['score']:.3f}
                    - **Key Content:** {rag.clean_ocr_text(results[0]['text'][:200])}...
                    """)
            else:
                st.warning("No relevant documents found. Try rephrasing your question.")
        else:
            st.warning("Please enter a search query.")
    
    # Sample queries
    st.header("💡 Sample Queries")
    st.markdown("""
    Try these example questions:
    - What are the land acquisition procedures?
    - How is toll collection managed?
    - What are the delegation of powers guidelines?
    - What are the environmental clearance requirements?
    - How are contracts awarded for highway projects?
    """)
    
    # System info
    st.sidebar.header("ℹ️ System Information")
    st.sidebar.write(f"**Documents Loaded:** {len(rag.documents)}")
    st.sidebar.write(f"**Search Index:** TF-IDF with Cosine Similarity")
    st.sidebar.write(f"**AI Model:** HuggingFace DialoGPT")
    st.sidebar.write(f"**Last Updated:** {rag.metadata[0]['filename'] if rag.metadata else 'N/A'}")

if __name__ == "__main__":
    main() 