#!/usr/bin/env python3
"""
Simple Working Processor - Fast and reliable text extraction
"""

import csv
import json
import os
import requests
import time
from datetime import datetime

def download_pdf(url, filename):
    """Download PDF file"""
    try:
        response = requests.get(url, timeout=30, verify=False)
        response.raise_for_status()
        
        os.makedirs("output/pdfs", exist_ok=True)
        filepath = f"output/pdfs/{filename}"
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        return filepath
    except Exception as e:
        print(f"❌ Download failed: {e}")
        return None

def extract_text_simple(filepath):
    """Extract text with PyPDF2 first, then EasyOCR if needed"""
    try:
        # Try PyPDF2 first (fastest)
        import PyPDF2
        with open(filepath, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            if text.strip():
                return text, "PyPDF2"
    except:
        pass
    
    # If PyPDF2 fails, use EasyOCR
    try:
        import easyocr
        import fitz  # PyMuPDF
        
        # Initialize EasyOCR reader
        reader = easyocr.Reader(['en'])
        
        # Open PDF and convert first page to image
        doc = fitz.open(filepath)
        page = doc[0]  # First page only for speed
        
        # Convert page to image with higher resolution
        mat = fitz.Matrix(2, 2)  # 2x zoom for better quality
        pix = page.get_pixmap(matrix=mat)
        
        # Save as temporary PNG file
        temp_img_path = "temp_page.png"
        pix.save(temp_img_path)
        doc.close()
        
        # Perform OCR on the saved image
        results = reader.readtext(temp_img_path)
        
        # Clean up temporary file
        if os.path.exists(temp_img_path):
            os.remove(temp_img_path)
        
        # Extract text from results
        text = ""
        for (bbox, text_detected, confidence) in results:
            text += text_detected + " "
        
        if text.strip():
            return text.strip(), "EasyOCR"
        else:
            return "No text detected", "EasyOCR_Failed"
            
    except Exception as e:
        return f"OCR Error: {e}", "OCR_Error"
    
    # If all methods fail, return placeholder
    return f"Document {os.path.basename(filepath)} - Text extraction failed", "Failed"

def process_10_documents():
    """Process 10 documents quickly and reliably"""
    print("🚀 SIMPLE WORKING PROCESSOR")
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
        print(f"   Subject: {doc['Subject'][:50]}...")
        
        start_time = time.time()
        
        # Download
        filename = f"{doc['Sr_No']}_{doc['Category']}.pdf"
        filepath = download_pdf(doc['Link'], filename)
        
        if filepath:
            print(f"   ✅ Downloaded: {filename}")
            
            # Extract text
            text, method = extract_text_simple(filepath)
            processing_time = time.time() - start_time
            
            result = {
                'id': doc['Sr_No'],
                'title': doc['Subject'],
                'content': text,
                'category': doc['Category'],
                'date': doc['Date'],
                'method': method,
                'filepath': filepath,
                'processing_time': processing_time,
                'content_length': len(text)
            }
            
            print(f"   ✅ {method}: {len(text)} chars ({processing_time:.2f}s)")
        else:
            result = {
                'id': doc['Sr_No'],
                'title': doc['Subject'],
                'content': 'Download failed',
                'category': doc['Category'],
                'date': doc['Date'],
                'method': 'Download_Failed',
                'filepath': None,
                'processing_time': 0,
                'content_length': 0
            }
            print(f"   ❌ Download failed")
        
        processed.append(result)
        
        # Save progress after each document
        with open("ragflow_integration/simple_progress.json", 'w', encoding='utf-8') as f:
            json.dump(processed, f, indent=2, ensure_ascii=False)
    
    # Save final results
    with open("ragflow_integration/simple_final_results.json", 'w', encoding='utf-8') as f:
        json.dump(processed, f, indent=2, ensure_ascii=False)
    
    print(f"\n🎉 COMPLETE!")
    print(f"📁 Results: ragflow_integration/simple_final_results.json")
    print(f"📊 Documents: {len(processed)}")
    
    return processed

if __name__ == "__main__":
    process_10_documents() 