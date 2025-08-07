#!/usr/bin/env python3
"""
Working Batch Processor - Based on proven nhai_policy_circulars2 code
"""

import csv
import json
import os
import requests
import time
from datetime import datetime
from pathlib import Path

class WorkingBatchProcessor:
    def __init__(self):
        self.downloads_dir = Path("output/pdfs")
        self.extracted_dir = Path("output/extracted_texts")
        self.data_dir = Path("ragflow_integration")
        
        # Create directories
        self.downloads_dir.mkdir(parents=True, exist_ok=True)
        self.extracted_dir.mkdir(parents=True, exist_ok=True)
        
        print("✅ Working Batch Processor initialized")

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

    def extract_text_with_ocr(self, filepath):
        """Extract text using OCR - based on proven working code"""
        try:
            # First try simple text extraction with PyPDF2
            try:
                import PyPDF2
                with open(filepath, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    text = ""
                    for page in pdf_reader.pages:
                        text += page.extract_text()
                    if text.strip():
                        return text, "PyPDF2", False
            except:
                pass
            
            # If no text, use EasyOCR with pdf2image (proven approach)
            try:
                from pdf2image import convert_from_path
                import easyocr
                import numpy as np
                
                # Convert PDF to images
                images = convert_from_path(filepath, first_page=1, last_page=1)
                if not images:
                    return "No images converted", "PDF2Image_Failed", True
                
                # Initialize EasyOCR reader
                reader = easyocr.Reader(['en'])
                
                # Process first page only for speed
                image = images[0]
                
                # Convert PIL Image to numpy array
                image_array = np.array(image)
                
                # Perform OCR
                results = reader.readtext(image_array)
                
                # Extract text from results
                text = ""
                for (bbox, text_detected, confidence) in results:
                    text += text_detected + " "
                
                if text.strip():
                    return text.strip(), "EasyOCR_PDF2Image", True
                else:
                    return "No text detected", "EasyOCR_NoText", True
                    
            except Exception as e:
                return f"EasyOCR Error: {e}", "EasyOCR_Error", True
            
            return "No text extracted", "Failed", False
            
        except Exception as e:
            return f"Error: {e}", "Error", False

    def process_document(self, doc, index, total):
        """Process a single document"""
        print(f"📄 [{index}/{total}] Processing: {doc['Sr_No']}")
        print(f"   Subject: {doc['Subject'][:50]}...")
        
        start_time = time.time()
        
        # Download document
        filename = f"{doc['Sr_No']}.pdf"
        filepath = self.download_pdf(doc['Link'], filename)
        
        if not filepath:
            return {
                'filename': filename,
                'subject': doc['Subject'],
                'sr_no': doc['Sr_No'],
                'policy_no': doc.get('Policy_No', ''),
                'date': doc['Date'],
                'text': 'Download failed',
                'text_length': 0,
                'extraction_method': 'Download_Failed',
                'used_ocr': False,
                'success': False
            }
        
        # Extract text
        text, method, used_ocr = self.extract_text_with_ocr(filepath)
        processing_time = time.time() - start_time
        
        result = {
            'filename': filename,
            'subject': doc['Subject'],
            'sr_no': doc['Sr_No'],
            'policy_no': doc.get('Policy_No', ''),
            'date': doc['Date'],
            'text': text,
            'text_length': len(text),
            'extraction_method': method,
            'used_ocr': used_ocr,
            'success': len(text) > 50  # Success if we got meaningful text
        }
        
        print(f"   ✅ {method}: {len(text)} chars ({processing_time:.2f}s)")
        
        return result

    def process_batch(self, max_documents=1619, start_from=51):
        """Process a batch of documents starting from a specific index"""
        print("🚀 WORKING BATCH PROCESSOR")
        print("=" * 50)
        
        # Read CSV
        csv_file = self.data_dir / "documents_with_links.csv"
        if not csv_file.exists():
            print(f"❌ CSV file not found: {csv_file}")
            return []
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            documents = list(reader)
        
        print(f"📊 Found {len(documents)} documents")
        print(f"🔄 Starting from document {start_from}, processing {max_documents - start_from + 1} documents")
        
        # Process documents starting from start_from
        processed = []
        for i, doc in enumerate(documents[start_from-1:max_documents], start_from):
            result = self.process_document(doc, i, max_documents)
            processed.append(result)
            
            # Save progress after each document
            self.save_progress(processed)
            
            # Save individual file
            self.save_individual_file(result)
            
            # Add small delay to prevent CPU overload
            time.sleep(0.5)
        
        # Save final results
        self.save_final_results(processed)
        
        return processed

    def save_progress(self, processed):
        """Save progress to JSON"""
        progress_file = self.data_dir / "batch_progress.json"
        with open(progress_file, 'w', encoding='utf-8') as f:
            json.dump(processed, f, indent=2, ensure_ascii=False)

    def save_individual_file(self, result):
        """Save individual document result"""
        filename = f"{result['sr_no']}_text.json"
        filepath = self.extracted_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

    def save_final_results(self, processed):
        """Save final results"""
        # Save as JSON
        output_file = self.data_dir / "batch_final_results.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(processed, f, indent=2, ensure_ascii=False)
        
        print(f"\n🎉 BATCH PROCESSING COMPLETED!")
        print(f"📁 Results: {output_file}")
        print(f"📁 Individual files: {self.extracted_dir}")
        print(f"📊 Documents: {len(processed)}")
        
        # Show statistics
        self.show_statistics(processed)

    def show_statistics(self, processed):
        """Show processing statistics"""
        successful = [p for p in processed if p['success']]
        failed = [p for p in processed if not p['success']]
        ocr_used = [p for p in processed if p['used_ocr']]
        
        print(f"\n📊 Statistics:")
        print(f"   ✅ Successful: {len(successful)}")
        print(f"   ❌ Failed: {len(failed)}")
        print(f"   🔍 OCR Used: {len(ocr_used)}")
        print(f"   📝 Total text extracted: {sum(p['text_length'] for p in processed)} chars")

def main():
    processor = WorkingBatchProcessor()
    processor.process_batch(max_documents=1619, start_from=51)  # Start from document 51

if __name__ == "__main__":
    main() 