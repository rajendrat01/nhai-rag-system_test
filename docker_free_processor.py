#!/usr/bin/env python3
"""
Docker-Free Document Processor for NHAI
Processes 500+ documents without Docker
"""

import os
import json
import sys
import time
from typing import Dict, List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DockerFreeProcessor:
    """
    Process NHAI documents without Docker
    """
    
    def __init__(self, hf_token: str):
        self.hf_token = hf_token
        self.processed_count = 0
        self.failed_count = 0
        
        # Import the simple RAG client
        sys.path.append("ragflow_integration/docker_free")
        from simple_rag_client import init_client
        self.client = init_client(hf_token)
        
        logger.info("✅ Docker-free processor initialized")
    
    def load_circulars(self) -> List[Dict]:
        """Load circulars from existing_links.json"""
        try:
            with open("output/existing_links.json", 'r', encoding='utf-8') as f:
                circulars = json.load(f)
            logger.info(f"✅ Loaded {len(circulars)} circulars")
            return circulars
        except Exception as e:
            logger.error(f"❌ Error loading circulars: {e}")
            return []
    
    def get_text_content(self, pdf_path: str) -> str:
        """Extract text content using multiple OCR methods"""
        try:
            # Import OCR processor
            sys.path.append("ragflow_integration")
            from ocr_processor import MultiOCRProcessor
            
            # Initialize OCR processor
            ocr_processor = MultiOCRProcessor()
            
            # Extract text using best available method
            result = ocr_processor.extract_text(pdf_path, method='auto')
            
            if result['success'] and result['text'].strip():
                logger.info(f"✅ OCR successful using {result['method']}")
                return result['text']
            else:
                logger.warning(f"⚠️ OCR failed: {result.get('error', 'Unknown error')}")
                # Fallback to simple text extraction
                return self._simple_text_extraction(pdf_path)
                
        except Exception as e:
            logger.error(f"❌ OCR processing failed: {e}")
            # Fallback to simple text extraction
            return self._simple_text_extraction(pdf_path)
    
    def _simple_text_extraction(self, pdf_path: str) -> str:
        """Simple text extraction fallback"""
        try:
            # Try to read as text first
            with open(pdf_path, 'r', encoding='utf-8') as f:
                return f.read()
        except:
            try:
                # Try with different encoding
                with open(pdf_path, 'r', encoding='latin-1') as f:
                    return f.read()
            except:
                # If it's a PDF, return a placeholder
                return f"PDF content from {os.path.basename(pdf_path)}"
    
    def process_documents(self, max_documents: int = 500) -> Dict:
        """Process documents in batches"""
        logger.info(f"🚀 Starting Docker-free processing of {max_documents} documents...")
        
        circulars = self.load_circulars()
        if not circulars:
            return {'error': 'No circulars found'}
        
        # Limit documents
        circulars = circulars[:max_documents]
        
        start_time = time.time()
        results = []
        
        for i, circular in enumerate(circulars):
            try:
                policy_no = circular['policy_no']
                
                # Find the document file
                pdf_path = None
                possible_paths = [
                    f"output/pdfs/{policy_no.replace('/', '_').replace('.', '_')}.pdf",
                    f"output/pdfs/{policy_no.replace('/', '_')}.pdf",
                    f"output/pdfs/{policy_no.replace('.', '_')}.pdf",
                    f"output/pdfs/{policy_no}.pdf"
                ]
                
                for path in possible_paths:
                    if os.path.exists(path):
                        pdf_path = path
                        break
                
                if not pdf_path:
                    logger.warning(f"⚠️ File not found for {policy_no}")
                    self.failed_count += 1
                    continue
                
                # Extract text content
                content = self.get_text_content(pdf_path)
                
                # Upload to RAG system
                metadata = {
                    'policy_no': policy_no,
                    'subject': circular.get('subject', ''),
                    'date': circular.get('date', ''),
                    'source_url': circular.get('full_url', ''),
                    'document_type': 'policy_circular'
                }
                
                result = self.client.upload_document(pdf_path, metadata)
                
                if result['success']:
                    self.processed_count += 1
                    logger.info(f"✅ Processed {policy_no} ({self.processed_count}/{len(circulars)})")
                else:
                    self.failed_count += 1
                    logger.error(f"❌ Failed to process {policy_no}: {result.get('error', 'Unknown error')}")
                
                results.append({
                    'policy_no': policy_no,
                    'success': result['success'],
                    'error': result.get('error'),
                    'doc_id': result.get('doc_id')
                })
                
                # Small delay to avoid overwhelming the API
                time.sleep(0.1)
                
            except Exception as e:
                self.failed_count += 1
                logger.error(f"❌ Error processing {circular.get('policy_no', 'Unknown')}: {e}")
                results.append({
                    'policy_no': circular.get('policy_no', 'Unknown'),
                    'success': False,
                    'error': str(e)
                })
        
        total_time = time.time() - start_time
        
        # Generate report
        report = {
            'summary': {
                'total_documents': len(circulars),
                'processed': self.processed_count,
                'failed': self.failed_count,
                'success_rate': (self.processed_count / len(circulars) * 100) if circulars else 0,
                'total_time': total_time,
                'documents_per_minute': (self.processed_count / (total_time / 60)) if total_time > 0 else 0
            },
            'results': results,
            'timestamp': time.time()
        }
        
        # Save report
        with open("ragflow_integration/docker_free/processing_report.json", 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info("🎉 Processing completed!")
        logger.info(f"📊 Summary: {self.processed_count}/{len(circulars)} documents processed")
        logger.info(f"⏱️ Total time: {total_time:.2f}s")
        logger.info(f"📈 Success rate: {report['summary']['success_rate']:.1f}%")
        
        return report

def main():
    """Main function"""
    print("🚀 Docker-Free NHAI Document Processor")
    print("==========================================")
    
    # Check if config exists
    config_path = "ragflow_integration/docker_free/config.json"
    if not os.path.exists(config_path):
        print("❌ Please run docker_free_setup.py first!")
        return
    
    # Load config
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    hf_token = config.get('hf_token')
    if not hf_token:
        print("❌ HuggingFace token not found in config!")
        return
    
    # Initialize processor
    processor = DockerFreeProcessor(hf_token)
    
    # Process documents
    report = processor.process_documents(max_documents=500)
    
    if 'error' not in report:
        print(f"\n🎉 Successfully processed {report['summary']['processed']} documents!")
        print(f"📊 Success rate: {report['summary']['success_rate']:.1f}%")
        print(f"⏱️ Total time: {report['summary']['total_time']:.2f}s")
        print(f"📈 Speed: {report['summary']['documents_per_minute']:.1f} docs/minute")
    else:
        print(f"❌ Processing failed: {report['error']}")

if __name__ == "__main__":
    main() 