#!/usr/bin/env python3
"""
EasyOCR Document Processor - Fast OCR extraction using EasyOCR
"""

import re
import os
import csv
import requests
import time
import warnings
from datetime import datetime
from pathlib import Path

# Suppress SSL warnings
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

def download_document(url, filename):
    """Download document from URL"""
    try:
        response = requests.get(url, timeout=30, verify=False)
        response.raise_for_status()
        
        # Create output directory
        os.makedirs("output/pdfs", exist_ok=True)
        
        filepath = f"output/pdfs/{filename}"
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        return filepath
    except Exception as e:
        print(f"❌ Download failed: {e}")
        return None

def extract_text_with_easyocr(filepath):
    """Extract text using EasyOCR"""
    try:
        # First try simple text extraction
        try:
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
        
        # If no text found, use EasyOCR
        try:
            import easyocr
            import fitz  # PyMuPDF
            import numpy as np
            import tempfile
            import os
            
            # Initialize EasyOCR reader (English)
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
            return f"EasyOCR Error: {e}", "EasyOCR_Error"
        
    except Exception as e:
        return f"Error: {e}", "Error"

def process_documents(max_docs=10):
    """Process documents with EasyOCR"""
    print("🚀 EASYOCR DOCUMENT PROCESSOR")
    print("=" * 50)
    
    # Read CSV file
    csv_file = "ragflow_integration/documents_with_links.csv"
    if not os.path.exists(csv_file):
        print(f"❌ CSV file not found: {csv_file}")
        return
    
    # Read documents from CSV
    documents = []
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            documents.append(row)
    
    print(f"📊 Found {len(documents)} documents in CSV")
    print(f"🎯 Processing first {max_docs} documents...")
    
    # Process documents
    processed_docs = []
    
    for i, doc in enumerate(documents[:max_docs]):
        print(f"\n📄 Processing {i+1}/{max_docs}: {doc['Sr_No']}")
        print(f"   Subject: {doc['Subject'][:50]}...")
        print(f"   Category: {doc['Category']}")
        
        start_time = time.time()
        
        # Download document
        filename = f"{doc['Sr_No']}_{doc['Category']}.pdf"
        filepath = download_document(doc['Link'], filename)
        
        if filepath:
            print(f"   ✅ Downloaded: {filename}")
            
            # Extract text with EasyOCR
            text, method = extract_text_with_easyocr(filepath)
            
            processing_time = time.time() - start_time
            
            # Update document info
            doc['Status'] = 'Processed'
            doc['Processed_Date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            doc['OCR_Method'] = method
            doc['Content_Length'] = len(text)
            doc['Processing_Time'] = f"{processing_time:.2f}s"
            doc['File_Path'] = filepath
            
            print(f"   ✅ Extracted {len(text)} characters using {method}")
            print(f"   ⏱️  Time: {processing_time:.2f}s")
            
            # Show first 200 characters of extracted text
            if len(text) > 200:
                print(f"   📝 Preview: {text[:200]}...")
            else:
                print(f"   📝 Content: {text}")
            
        else:
            doc['Status'] = 'Download Failed'
            doc['Processed_Date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            doc['Error'] = 'Download failed'
            print(f"   ❌ Download failed")
        
        processed_docs.append(doc)
    
    # Save results to new CSV
    output_file = "ragflow_integration/easyocr_processed_documents.csv"
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['Sr_No', 'Category', 'Date', 'Subject', 'Link', 'Status', 
                     'Processed_Date', 'OCR_Method', 'Content_Length', 
                     'Processing_Time', 'File_Path', 'Error']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(processed_docs)
    
    # Show summary
    print(f"\n🎉 PROCESSING COMPLETED!")
    print("=" * 50)
    print(f"📊 Processed: {len(processed_docs)} documents")
    print(f"📁 Results: {output_file}")
    
    # Count by status
    status_counts = {}
    for doc in processed_docs:
        status = doc['Status']
        status_counts[status] = status_counts.get(status, 0) + 1
    
    print(f"\n📋 Status Summary:")
    for status, count in status_counts.items():
        print(f"   • {status}: {count}")
    
    # Count by OCR method
    method_counts = {}
    for doc in processed_docs:
        if doc['Status'] == 'Processed':
            method = doc['OCR_Method']
            method_counts[method] = method_counts.get(method, 0) + 1
    
    print(f"\n🔍 Text Extraction Methods Used:")
    for method, count in method_counts.items():
        print(f"   • {method}: {count}")

def main():
    process_documents(max_docs=10)

if __name__ == "__main__":
    main() 