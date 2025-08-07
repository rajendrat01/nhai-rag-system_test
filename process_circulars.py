#!/usr/bin/env python3
"""
Process NHAI Policy Circulars for RAGFlow Integration
Uploads all extracted PDFs to RAGFlow for advanced analysis
"""

import os
import json
import sys
import logging
from typing import Dict, List, Optional
from datetime import datetime
import time

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ragflow_integration.nhai_rag_client import NHAIRAGClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ragflow_integration/processing.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class NHAICircularProcessor:
    """
    Process NHAI policy circulars for RAGFlow integration
    """
    
    def __init__(self, ragflow_host: str = "localhost", ragflow_port: int = 80):
        """
        Initialize the processor
        
        Args:
            ragflow_host: RAGFlow server host
            ragflow_port: RAGFlow server port
        """
        self.client = NHAIRAGClient(ragflow_host, ragflow_port)
        self.processed_count = 0
        self.failed_count = 0
        self.skipped_count = 0
        
        # Create processing log directory
        os.makedirs("ragflow_integration/logs", exist_ok=True)
        
        logger.info("✓ NHAI Circular Processor initialized")
    
    def load_existing_circulars(self) -> List[Dict]:
        """Load existing circulars from the JSON file"""
        try:
            with open("output/existing_links.json", 'r', encoding='utf-8') as f:
                circulars = json.load(f)
            logger.info(f"✓ Loaded {len(circulars)} circulars from existing_links.json")
            return circulars
        except Exception as e:
            logger.error(f"✗ Error loading circulars: {e}")
            return []
    
    def get_processed_policies(self) -> set:
        """Get list of already processed policies"""
        try:
            stats = self.client.get_document_statistics()
            if "error" not in stats:
                # Extract policy numbers from statistics
                processed = set()
                # This would depend on RAGFlow's statistics format
                # For now, we'll check the logs
                return processed
            return set()
        except Exception as e:
            logger.warning(f"Could not get processed policies: {e}")
            return set()
    
    def process_single_circular(self, circular: Dict) -> Dict:
        """
        Process a single circular
        
        Args:
            circular: Circular data from existing_links.json
            
        Returns:
            Processing result
        """
        policy_no = circular['policy_no']
        pdf_path = os.path.join("output/pdfs", f"{policy_no.replace('/', '_').replace('.', '_')}.pdf")
        
        result = {
            'policy_no': policy_no,
            'subject': circular['subject'],
            'date': circular['date'],
            'pdf_path': pdf_path,
            'processed': False,
            'error': None,
            'upload_result': None,
            'processed_at': datetime.now().isoformat()
        }
        
        try:
            # Check if PDF exists
            if not os.path.exists(pdf_path):
                result['error'] = f"PDF file not found: {pdf_path}"
                self.skipped_count += 1
                return result
            
            # Check if already processed
            # This would require checking RAGFlow's document store
            # For now, we'll process all
            
            # Prepare metadata
            metadata = {
                'subject': circular['subject'],
                'date': circular['date'],
                'link_path': circular['link_path'],
                'full_url': circular['full_url'],
                'direct_pdf_url': circular['direct_pdf_url'],
                'extracted_on': circular['extracted_on'],
                'source': 'NHAI',
                'document_type': 'policy_circular'
            }
            
            # Upload to RAGFlow
            logger.info(f"Processing policy {policy_no}: {circular['subject'][:80]}...")
            upload_result = self.client.upload_policy_document(
                file_path=pdf_path,
                policy_no=policy_no,
                metadata=metadata
            )
            
            if "error" not in upload_result:
                result['processed'] = True
                result['upload_result'] = upload_result
                self.processed_count += 1
                logger.info(f"✓ Successfully processed policy {policy_no}")
            else:
                result['error'] = upload_result['error']
                self.failed_count += 1
                logger.error(f"✗ Failed to process policy {policy_no}: {upload_result['error']}")
            
        except Exception as e:
            result['error'] = str(e)
            self.failed_count += 1
            logger.error(f"✗ Error processing policy {policy_no}: {e}")
        
        return result
    
    def process_circulars_batch(self, 
                               circulars: List[Dict], 
                               start_index: int = 0,
                               batch_size: int = 10,
                               delay: int = 2) -> List[Dict]:
        """
        Process circulars in batches
        
        Args:
            circulars: List of circulars to process
            start_index: Starting index
            batch_size: Number of circulars to process
            delay: Delay between uploads (seconds)
            
        Returns:
            List of processing results
        """
        end_index = min(start_index + batch_size, len(circulars))
        batch_circulars = circulars[start_index:end_index]
        
        logger.info(f"Processing batch {start_index+1}-{end_index} of {len(circulars)} circulars")
        
        results = []
        for i, circular in enumerate(batch_circulars):
            logger.info(f"Processing {start_index + i + 1}/{len(circulars)}: {circular['policy_no']}")
            
            result = self.process_single_circular(circular)
            results.append(result)
            
            # Add delay between uploads
            if i < len(batch_circulars) - 1:  # Don't delay after the last one
                time.sleep(delay)
        
        return results
    
    def save_processing_results(self, results: List[Dict], batch_num: int):
        """Save processing results to file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"ragflow_integration/logs/processing_results_batch_{batch_num}_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✓ Processing results saved to {filename}")
    
    def generate_processing_report(self, all_results: List[Dict]) -> Dict:
        """Generate a comprehensive processing report"""
        total_processed = len([r for r in all_results if r['processed']])
        total_failed = len([r for r in all_results if not r['processed'] and r['error']])
        total_skipped = len([r for r in all_results if not r['processed'] and 'not found' in str(r.get('error', ''))])
        
        # Group by error types
        error_types = {}
        for result in all_results:
            if result.get('error'):
                error_type = type(result['error']).__name__
                error_types[error_type] = error_types.get(error_type, 0) + 1
        
        # Get successful policy numbers
        successful_policies = [r['policy_no'] for r in all_results if r['processed']]
        failed_policies = [r['policy_no'] for r in all_results if not r['processed'] and r['error']]
        
        report = {
            'processing_summary': {
                'total_circulars': len(all_results),
                'successfully_processed': total_processed,
                'failed': total_failed,
                'skipped': total_skipped,
                'success_rate': f"{(total_processed/len(all_results)*100):.1f}%" if all_results else "0%"
            },
            'error_analysis': error_types,
            'successful_policies': successful_policies,
            'failed_policies': failed_policies,
            'processing_timestamp': datetime.now().isoformat(),
            'ragflow_integration': {
                'host': self.client.base_url,
                'client_version': '1.0.0'
            }
        }
        
        return report
    
    def run_full_processing(self, 
                           start_index: int = 0,
                           max_circulars: Optional[int] = None,
                           batch_size: int = 5) -> Dict:
        """
        Run full processing of NHAI circulars
        
        Args:
            start_index: Starting index for processing
            max_circulars: Maximum number of circulars to process (None for all)
            batch_size: Number of circulars to process per batch
            
        Returns:
            Processing report
        """
        logger.info("Starting full NHAI circular processing for RAGFlow")
        
        # Load circulars
        circulars = self.load_existing_circulars()
        if not circulars:
            return {"error": "No circulars found to process"}
        
        # Apply limits
        if max_circulars:
            circulars = circulars[start_index:start_index + max_circulars]
        else:
            circulars = circulars[start_index:]
        
        logger.info(f"Processing {len(circulars)} circulars (starting from index {start_index})")
        
        all_results = []
        batch_num = 1
        
        # Process in batches
        for i in range(0, len(circulars), batch_size):
            batch_start = start_index + i
            batch_results = self.process_circulars_batch(
                circulars, 
                start_index=i, 
                batch_size=batch_size
            )
            
            all_results.extend(batch_results)
            
            # Save batch results
            self.save_processing_results(batch_results, batch_num)
            
            # Print progress
            processed_so_far = len([r for r in all_results if r['processed']])
            logger.info(f"Batch {batch_num} completed. Total processed: {processed_so_far}/{len(circulars)}")
            
            batch_num += 1
        
        # Generate final report
        report = self.generate_processing_report(all_results)
        
        # Save final report
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_filename = f"ragflow_integration/logs/final_processing_report_{timestamp}.json"
        
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✓ Full processing completed. Report saved to {report_filename}")
        logger.info(f"Final Summary: {report['processing_summary']}")
        
        return report

def main():
    """Main function to run the processing"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Process NHAI circulars for RAGFlow")
    parser.add_argument("--start-index", type=int, default=0, help="Starting index for processing")
    parser.add_argument("--max-circulars", type=int, default=None, help="Maximum number of circulars to process")
    parser.add_argument("--batch-size", type=int, default=5, help="Batch size for processing")
    parser.add_argument("--ragflow-host", default="localhost", help="RAGFlow server host")
    parser.add_argument("--ragflow-port", type=int, default=80, help="RAGFlow server port")
    
    args = parser.parse_args()
    
    # Initialize processor
    processor = NHAICircularProcessor(args.ragflow_host, args.ragflow_port)
    
    # Run processing
    report = processor.run_full_processing(
        start_index=args.start_index,
        max_circulars=args.max_circulars,
        batch_size=args.batch_size
    )
    
    if "error" in report:
        logger.error(f"Processing failed: {report['error']}")
        return False
    
    print("\n" + "="*60)
    print("PROCESSING COMPLETED")
    print("="*60)
    print(f"Total circulars: {report['processing_summary']['total_circulars']}")
    print(f"Successfully processed: {report['processing_summary']['successfully_processed']}")
    print(f"Failed: {report['processing_summary']['failed']}")
    print(f"Success rate: {report['processing_summary']['success_rate']}")
    print("="*60)
    
    return True

if __name__ == "__main__":
    main() 