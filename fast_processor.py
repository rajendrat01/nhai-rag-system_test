#!/usr/bin/env python3
"""
Fast Document Processor - Processes documents with quick OCR extraction
"""

import re
import os
import csv
import requests
import time
from datetime import datetime
from pathlib import Path

def download_document(url, filename):
    """Download document from URL"""
    try:
        # Try with SSL verification disabled for problematic sites
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

def extract_text_fast(filepath):
    """Fast text extraction using multiple methods"""
    try:
        # Method 1: Try simple text extraction first (fastest)
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
        
        # Method 2: Try pdfplumber (good for complex layouts)
        try:
            import pdfplumber
            with pdfplumber.open(filepath) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() or ""
                if text.strip():
                    return text, "pdfplumber"
        except:
            pass
        
        # Method 3: Try PyMuPDF (very fast)
        try:
            import fitz
            doc = fitz.open(filepath)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            if text.strip():
                return text, "PyMuPDF"
        except:
            pass
        
        # Method 4: Try OCR with PaddleOCR (fast OCR)
        try:
            from paddleocr import PaddleOCR
            import cv2
            from PIL import Image
            
            # Convert PDF to image
            import fitz
            doc = fitz.open(filepath)
            page = doc[0]  # First page only for speed
            pix = page.get_pixmap()
            img_data = pix.tobytes("png")
            doc.close()
            
            # Save temporary image
            temp_img = "temp_page.png"
            with open(temp_img, "wb") as f:
                f.write(img_data)
            
            # OCR with PaddleOCR
            ocr = PaddleOCR(use_angle_cls=True, lang='en')
            result = ocr.ocr(temp_img, cls=True)
            
            text = ""
            for line in result[0]:
                text += line[1][0] + "\n"
            
            # Clean up
            os.remove(temp_img)
            
            if text.strip():
                return text, "PaddleOCR"
        except:
            pass
        
        return "No text extracted", "Failed"
        
    except Exception as e:
        return f"Error: {e}", "Error"

def process_documents(max_docs=10):
    """Process documents with fast OCR"""
    print("🚀 FAST DOCUMENT PROCESSOR")
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
            
            # Extract text
            text, method = extract_text_fast(filepath)
            
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
            
        else:
            doc['Status'] = 'Download Failed'
            doc['Processed_Date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            doc['Error'] = 'Download failed'
            print(f"   ❌ Download failed")
        
        processed_docs.append(doc)
    
    # Save results to new CSV
    output_file = "ragflow_integration/processed_documents.csv"
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
    
    print(f"\n🔍 OCR Methods Used:")
    for method, count in method_counts.items():
        print(f"   • {method}: {count}")

def main():
    process_documents(max_docs=10)

if __name__ == "__main__":
    main() 