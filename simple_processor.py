#!/usr/bin/env python3
"""
Simple Document Processor - Uses basic libraries for text extraction
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

def extract_text_simple(filepath):
    """Simple text extraction using basic methods"""
    try:
        # Method 1: Try PyPDF2 (most common)
        try:
            import PyPDF2
            with open(filepath, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
                if text.strip():
                    return text, "PyPDF2"
        except ImportError:
            print("   ⚠️  PyPDF2 not installed")
        except Exception as e:
            print(f"   ⚠️  PyPDF2 failed: {e}")
        
        # Method 2: Try pdfplumber
        try:
            import pdfplumber
            with pdfplumber.open(filepath) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() or ""
                if text.strip():
                    return text, "pdfplumber"
        except ImportError:
            print("   ⚠️  pdfplumber not installed")
        except Exception as e:
            print(f"   ⚠️  pdfplumber failed: {e}")
        
        # Method 3: Try PyMuPDF (fitz)
        try:
            import fitz
            doc = fitz.open(filepath)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            if text.strip():
                return text, "PyMuPDF"
        except ImportError:
            print("   ⚠️  PyMuPDF not installed")
        except Exception as e:
            print(f"   ⚠️  PyMuPDF failed: {e}")
        
        # Method 4: Check if it's a text file
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read()
                if text.strip():
                    return text, "Text File"
        except:
            pass
        
        return "No text extracted - PDF may be image-based", "Failed"
        
    except Exception as e:
        return f"Error: {e}", "Error"

def process_documents(max_docs=10):
    """Process documents with simple text extraction"""
    print("🚀 SIMPLE DOCUMENT PROCESSOR")
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
            text, method = extract_text_simple(filepath)
            
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
            
            # Show first 100 characters of extracted text
            if len(text) > 100:
                print(f"   📝 Preview: {text[:100]}...")
            else:
                print(f"   📝 Content: {text}")
            
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
    
    print(f"\n🔍 Text Extraction Methods Used:")
    for method, count in method_counts.items():
        print(f"   • {method}: {count}")

def main():
    process_documents(max_docs=10)

if __name__ == "__main__":
    main() 