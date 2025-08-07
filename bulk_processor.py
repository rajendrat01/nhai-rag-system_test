#!/usr/bin/env python3
"""
Bulk Document Processor for NHAI RAGFlow
Handles 500+ documents efficiently for demo
"""

import os
import json
import sys
import logging
import time
from typing import Dict, List, Optional
from datetime import datetime
import concurrent.futures
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ragflow_integration.nhai_rag_client import NHAIRAGClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ragflow_integration/bulk_processing.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BulkDocumentProcessor:
    """
    Bulk processor for 500+ NHAI documents
    """
    
    def __init__(self, 
                 ragflow_host: str = "localhost", 
                 ragflow_port: int = 80,
                 max_workers: int = 4):
        """
        Initialize bulk processor
        
        Args:
            ragflow_host: RAGFlow server host
            ragflow_port: RAGFlow server port
            max_workers: Number of concurrent workers
        """
        self.client = NHAIRAGClient(ragflow_host, ragflow_port)
        self.max_workers = max_workers
        self.processed_count = 0
        self.failed_count = 0
        self.skipped_count = 0
        
        # Create processing directories
        os.makedirs("ragflow_integration/logs", exist_ok=True)
        os.makedirs("ragflow_integration/processing_status", exist_ok=True)
        
        logger.info(f"✓ Bulk Processor initialized with {max_workers} workers")
    
    def load_all_circulars(self) -> List[Dict]:
        """Load all circulars from existing_links.json"""
        try:
            with open("output/existing_links.json", 'r', encoding='utf-8') as f:
                circulars = json.load(f)
            logger.info(f"✓ Loaded {len(circulars)} circulars from existing_links.json")
            return circulars
        except Exception as e:
            logger.error(f"✗ Error loading circulars: {e}")
            return []
    
    def get_pdf_path(self, policy_no: str) -> Optional[str]:
        """Get PDF path for a policy number"""
        # Try different naming patterns
        patterns = [
            f"{policy_no.replace('/', '_').replace('.', '_')}.pdf",
            f"{policy_no.replace('/', '_')}.pdf",
            f"{policy_no.replace('.', '_')}.pdf",
            f"{policy_no}.pdf"
        ]
        
        for pattern in patterns:
            pdf_path = os.path.join("output/pdfs", pattern)
            if os.path.exists(pdf_path):
                return pdf_path
        
        return None
    
    def process_single_document(self, circular: Dict) -> Dict:
        """
        Process a single document (thread-safe)
        
        Args:
            circular: Circular data from existing_links.json
            
        Returns:
            Processing result
        """
        policy_no = circular['policy_no']
        pdf_path = self.get_pdf_path(policy_no)
        
        result = {
            'policy_no': policy_no,
            'subject': circular.get('subject', ''),
            'date': circular.get('date', ''),
            'pdf_path': pdf_path,
            'processed': False,
            'error': None,
            'upload_result': None,
            'processing_time': 0,
            'file_size': 0
        }
        
        if not pdf_path:
            result['error'] = 'PDF file not found'
            result['skipped'] = True
            return result
        
        try:
            # Check file size
            file_size = os.path.getsize(pdf_path)
            result['file_size'] = file_size
            
            # Skip if file is too large (>50MB) or too small (<1KB)
            if file_size > 50 * 1024 * 1024:  # 50MB
                result['error'] = 'File too large'
                result['skipped'] = True
                return result
            
            if file_size < 1024:  # 1KB
                result['error'] = 'File too small'
                result['skipped'] = True
                return result
            
            start_time = time.time()
            
            # Upload to RAGFlow
            upload_result = self.client.upload_policy_document(
                file_path=pdf_path,
                policy_no=policy_no,
                metadata={
                    'subject': circular.get('subject', ''),
                    'date': circular.get('date', ''),
                    'source_url': circular.get('full_url', ''),
                    'extracted_on': circular.get('extracted_on', ''),
                    'document_type': 'policy_circular'
                }
            )
            
            processing_time = time.time() - start_time
            result['processing_time'] = processing_time
            result['upload_result'] = upload_result
            result['processed'] = True
            
            logger.info(f"✓ Processed {policy_no} in {processing_time:.2f}s")
            
        except Exception as e:
            result['error'] = str(e)
            result['processed'] = False
            logger.error(f"✗ Failed to process {policy_no}: {e}")
        
        return result
    
    def process_documents_batch(self, 
                               circulars: List[Dict], 
                               batch_size: int = 50,
                               delay_between_batches: int = 5) -> List[Dict]:
        """
        Process documents in batches with concurrent processing
        
        Args:
            circulars: List of circulars to process
            batch_size: Number of documents per batch
            delay_between_batches: Delay between batches in seconds
            
        Returns:
            List of processing results
        """
        all_results = []
        total_batches = (len(circulars) + batch_size - 1) // batch_size
        
        logger.info(f"🚀 Starting bulk processing: {len(circulars)} documents in {total_batches} batches")
        
        for batch_num in range(total_batches):
            start_idx = batch_num * batch_size
            end_idx = min(start_idx + batch_size, len(circulars))
            batch_circulars = circulars[start_idx:end_idx]
            
            logger.info(f"📦 Processing batch {batch_num + 1}/{total_batches} ({len(batch_circulars)} documents)")
            
            # Process batch concurrently
            batch_results = []
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                future_to_circular = {
                    executor.submit(self.process_single_document, circular): circular 
                    for circular in batch_circulars
                }
                
                for future in concurrent.futures.as_completed(future_to_circular):
                    result = future.result()
                    batch_results.append(result)
                    
                    # Update counters
                    if result['processed']:
                        self.processed_count += 1
                    elif result.get('skipped'):
                        self.skipped_count += 1
                    else:
                        self.failed_count += 1
            
            all_results.extend(batch_results)
            
            # Save batch results
            self.save_batch_results(batch_results, batch_num + 1)
            
            # Progress update
            logger.info(f"📊 Progress: {self.processed_count} processed, {self.failed_count} failed, {self.skipped_count} skipped")
            
            # Delay between batches (except last batch)
            if batch_num < total_batches - 1:
                logger.info(f"⏳ Waiting {delay_between_batches}s before next batch...")
                time.sleep(delay_between_batches)
        
        return all_results
    
    def save_batch_results(self, results: List[Dict], batch_num: int):
        """Save batch processing results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ragflow_integration/processing_status/batch_{batch_num}_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 Saved batch {batch_num} results to {filename}")
    
    def generate_bulk_report(self, all_results: List[Dict]) -> Dict:
        """Generate comprehensive bulk processing report"""
        total_docs = len(all_results)
        processed = sum(1 for r in all_results if r['processed'])
        failed = sum(1 for r in all_results if not r['processed'] and not r.get('skipped'))
        skipped = sum(1 for r in all_results if r.get('skipped'))
        
        total_size = sum(r.get('file_size', 0) for r in all_results)
        total_time = sum(r.get('processing_time', 0) for r in all_results)
        
        # Calculate statistics
        avg_time = total_time / processed if processed > 0 else 0
        avg_size = total_size / total_docs if total_docs > 0 else 0
        
        # Error analysis
        errors = {}
        for result in all_results:
            if result.get('error'):
                error_type = result['error']
                errors[error_type] = errors.get(error_type, 0) + 1
        
        report = {
            'summary': {
                'total_documents': total_docs,
                'processed': processed,
                'failed': failed,
                'skipped': skipped,
                'success_rate': (processed / total_docs * 100) if total_docs > 0 else 0,
                'total_size_mb': total_size / (1024 * 1024),
                'total_processing_time': total_time,
                'average_processing_time': avg_time,
                'average_file_size_mb': avg_size / (1024 * 1024)
            },
            'errors': errors,
            'performance': {
                'documents_per_minute': (processed / (total_time / 60)) if total_time > 0 else 0,
                'mb_per_minute': (total_size / (1024 * 1024)) / (total_time / 60) if total_time > 0 else 0
            },
            'timestamp': datetime.now().isoformat(),
            'configuration': {
                'max_workers': self.max_workers,
                'ragflow_host': self.client.base_url
            }
        }
        
        return report
    
    def run_bulk_processing(self, 
                           max_documents: Optional[int] = None,
                           batch_size: int = 50,
                           delay_between_batches: int = 5) -> Dict:
        """
        Run bulk processing of all documents
        
        Args:
            max_documents: Maximum number of documents to process (None for all)
            batch_size: Number of documents per batch
            delay_between_batches: Delay between batches in seconds
            
        Returns:
            Processing report
        """
        logger.info("🚀 Starting bulk document processing...")
        
        # Load all circulars
        circulars = self.load_all_circulars()
        
        if not circulars:
            logger.error("❌ No circulars found to process")
            return {'error': 'No circulars found'}
        
        # Limit documents if specified
        if max_documents:
            circulars = circulars[:max_documents]
            logger.info(f"📋 Limited to {max_documents} documents")
        
        logger.info(f"📊 Total documents to process: {len(circulars)}")
        
        # Process documents
        start_time = time.time()
        all_results = self.process_documents_batch(
            circulars, 
            batch_size=batch_size,
            delay_between_batches=delay_between_batches
        )
        total_time = time.time() - start_time
        
        # Generate report
        report = self.generate_bulk_report(all_results)
        report['total_elapsed_time'] = total_time
        
        # Save final report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"ragflow_integration/bulk_processing_report_{timestamp}.json"
        
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # Print summary
        logger.info("🎉 Bulk processing completed!")
        logger.info(f"📊 Summary: {report['summary']['processed']}/{report['summary']['total_documents']} documents processed")
        logger.info(f"⏱️  Total time: {total_time:.2f}s")
        logger.info(f"📈 Success rate: {report['summary']['success_rate']:.1f}%")
        logger.info(f"📄 Report saved to: {report_filename}")
        
        return report

def main():
    """Main function for bulk processing"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Bulk process NHAI documents for RAGFlow')
    parser.add_argument('--max-documents', type=int, default=None, 
                       help='Maximum number of documents to process (default: all)')
    parser.add_argument('--batch-size', type=int, default=50,
                       help='Number of documents per batch (default: 50)')
    parser.add_argument('--max-workers', type=int, default=4,
                       help='Number of concurrent workers (default: 4)')
    parser.add_argument('--delay', type=int, default=5,
                       help='Delay between batches in seconds (default: 5)')
    parser.add_argument('--host', default='localhost',
                       help='RAGFlow host (default: localhost)')
    parser.add_argument('--port', type=int, default=80,
                       help='RAGFlow port (default: 80)')
    
    args = parser.parse_args()
    
    # Initialize processor
    processor = BulkDocumentProcessor(
        ragflow_host=args.host,
        ragflow_port=args.port,
        max_workers=args.max_workers
    )
    
    # Run bulk processing
    report = processor.run_bulk_processing(
        max_documents=args.max_documents,
        batch_size=args.batch_size,
        delay_between_batches=args.delay
    )
    
    if 'error' not in report:
        print(f"\n🎉 Successfully processed {report['summary']['processed']} documents!")
        print(f"📊 Success rate: {report['summary']['success_rate']:.1f}%")
        print(f"⏱️  Total time: {report['total_elapsed_time']:.2f}s")
    else:
        print(f"❌ Processing failed: {report['error']}")

if __name__ == "__main__":
    main() 