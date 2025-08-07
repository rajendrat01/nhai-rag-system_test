#!/usr/bin/env python3
"""
Working EasyOCR Processor - Based on proven nhai_policy_circulars2 approach
"""

import csv
import json
import os
import requests
import time
import warnings
from datetime import datetime
from pathlib import Path

warnings.filterwarnings('ignore')

class WorkingEasyOCRProcessor:
    def __init__(self):
        self.downloads_dir = Path("output/pdfs")
        self.extracted_dir = Path("output/extracted_texts")
        self.data_dir = Path("ragflow_integration")
        
        # Create directories
        self.downloads_dir.mkdir(parents=True, exist_ok=True)
        self.extracted_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize EasyOCR reader once
        try:
            import easyocr
            self.reader = easyocr.Reader(['en'])
            print("✅ EasyOCR initialized successfully")
        except Exception as e:
            print(f"❌ EasyOCR initialization failed: {e}")
            self.reader = None

    def download_pdf(self, url, filename):
        """Download PDF file"""
        try:
            response = requests.get(url, timeout=30, verify=False)
            response.raise_for_status()
            
            filepath = self.downloads_dir / filename
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            return str(filepath)
        except Exception as e:
            print(f"❌ Download failed: {e}")
            return None

    def extract_text_with_easyocr(self, filepath):
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
            
            # If no text, use EasyOCR
            if self.reader:
                try:
                    import fitz  # PyMuPDF
                    
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
                    results = self.reader.readtext(temp_img_path)
                    
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
            
            return "No text extracted", "Failed"
            
        except Exception as e:
            return f"Error: {e}", "Error"

    def process_document(self, doc, index, total):
        """Process a single document"""
        print(f"📄 [{index}/{total}] Processing: {doc['Sr_No']}")
        print(f"   Subject: {doc['Subject'][:50]}...")
        
        start_time = time.time()
        
        # Download document
        filename = f"{doc['Sr_No']}_{doc['Category']}.pdf"
        filepath = self.download_pdf(doc['Link'], filename)
        
        if not filepath:
            return {
                'id': doc['Sr_No'],
                'title': doc['Subject'],
                'content': 'Download failed',
                'category': doc['Category'],
                'date': doc['Date'],
                'method': 'Download_Failed',
                'filepath': None,
                'processing_time': 0
            }
        
        # Extract text
        text, method = self.extract_text_with_easyocr(filepath)
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
        
        return result

    def process_batch(self, max_documents=10):
        """Process a batch of documents"""
        print("🚀 WORKING EASYOCR PROCESSOR")
        print("=" * 50)
        
        # Read CSV
        csv_file = self.data_dir / "documents_with_links.csv"
        if not csv_file.exists():
            print(f"❌ CSV file not found: {csv_file}")
            return []
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            documents = list(reader)
        
        print(f"📊 Found {len(documents)} documents, processing first {max_documents}")
        
        # Process documents
        processed = []
        for i, doc in enumerate(documents[:max_documents]):
            result = self.process_document(doc, i+1, max_documents)
            processed.append(result)
            
            # Save progress after each document
            self.save_progress(processed)
        
        # Save final results
        self.save_final_results(processed)
        
        return processed

    def save_progress(self, processed):
        """Save progress to JSON"""
        progress_file = self.data_dir / "processing_progress.json"
        with open(progress_file, 'w', encoding='utf-8') as f:
            json.dump(processed, f, indent=2, ensure_ascii=False)

    def save_final_results(self, processed):
        """Save final results"""
        # Save as JSON
        output_file = self.data_dir / "final_processed_data.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(processed, f, indent=2, ensure_ascii=False)
        
        # Save as CSV
        csv_file = self.data_dir / "final_processed_data.csv"
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['id', 'title', 'category', 'date', 'method', 'content_length', 'processing_time']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for doc in processed:
                writer.writerow({
                    'id': doc['id'],
                    'title': doc['title'],
                    'category': doc['category'],
                    'date': doc['date'],
                    'method': doc['method'],
                    'content_length': doc['content_length'],
                    'processing_time': doc['processing_time']
                })
        
        print(f"\n🎉 PROCESSING COMPLETE!")
        print(f"📁 JSON: {output_file}")
        print(f"📁 CSV: {csv_file}")
        print(f"📊 Documents: {len(processed)}")

def main():
    processor = WorkingEasyOCRProcessor()
    processor.process_batch(max_documents=10)

if __name__ == "__main__":
    main() 