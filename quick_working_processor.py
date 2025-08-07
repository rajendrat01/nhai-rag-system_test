#!/usr/bin/env python3
"""
Quick Working Processor - Fast text extraction and RAG setup
"""

import csv
import json
import os
import requests
import warnings
from datetime import datetime

warnings.filterwarnings('ignore')

def download_and_extract_text(url, filename):
    """Download PDF and extract text quickly"""
    try:
        # Download
        response = requests.get(url, timeout=30, verify=False)
        response.raise_for_status()
        
        os.makedirs("output/pdfs", exist_ok=True)
        filepath = f"output/pdfs/{filename}"
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        # Try simple text extraction
        try:
            import PyPDF2
            with open(filepath, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
                if text.strip():
                    return text, "PyPDF2", filepath
        except:
            pass
        
        # If no text, return placeholder
        return f"Document {filename} - Text extraction pending", "Pending", filepath
        
    except Exception as e:
        return f"Error: {e}", "Failed", None

def process_10_documents():
    """Process 10 documents quickly"""
    print("🚀 QUICK WORKING PROCESSOR")
    print("=" * 40)
    
    # Read CSV
    with open("ragflow_integration/documents_with_links.csv", 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        documents = list(reader)
    
    print(f"📊 Processing first 10 documents...")
    
    # Process documents
    processed = []
    for i, doc in enumerate(documents[:10]):
        print(f"📄 {i+1}/10: {doc['Sr_No']}")
        
        filename = f"{doc['Sr_No']}_{doc['Category']}.pdf"
        text, method, filepath = download_and_extract_text(doc['Link'], filename)
        
        processed.append({
            'id': doc['Sr_No'],
            'title': doc['Subject'],
            'content': text,
            'category': doc['Category'],
            'date': doc['Date'],
            'method': method,
            'filepath': filepath
        })
        
        print(f"   ✅ {method}: {len(text)} chars")
    
    # Save as JSON for RAG
    output_file = "ragflow_integration/processed_data.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(processed, f, indent=2, ensure_ascii=False)
    
    print(f"\n🎉 COMPLETE!")
    print(f"📁 Data saved: {output_file}")
    print(f"📊 Documents: {len(processed)}")
    
    return processed

if __name__ == "__main__":
    process_10_documents() 