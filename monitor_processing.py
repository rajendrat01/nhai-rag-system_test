#!/usr/bin/env python3
"""
Real-time monitoring for bulk document processing
Shows progress, performance metrics, and status updates
"""

import os
import json
import time
import glob
from datetime import datetime
from typing import Dict, List

def get_processing_status() -> Dict:
    """Get current processing status from log files"""
    status = {
        'total_processed': 0,
        'total_failed': 0,
        'total_skipped': 0,
        'current_batch': 0,
        'total_batches': 0,
        'processing_time': 0,
        'success_rate': 0,
        'documents_per_minute': 0,
        'last_update': None,
        'errors': {}
    }
    
    # Check batch files
    batch_files = glob.glob("ragflow_integration/processing_status/batch_*.json")
    if batch_files:
        status['total_batches'] = len(batch_files)
        status['current_batch'] = max([int(f.split('_')[1]) for f in batch_files])
        
        # Aggregate results from all batches
        for batch_file in batch_files:
            try:
                with open(batch_file, 'r', encoding='utf-8') as f:
                    batch_results = json.load(f)
                
                for result in batch_results:
                    if result['processed']:
                        status['total_processed'] += 1
                    elif result.get('skipped'):
                        status['total_skipped'] += 1
                    else:
                        status['total_failed'] += 1
                    
                    # Track errors
                    if result.get('error'):
                        error_type = result['error']
                        status['errors'][error_type] = status['errors'].get(error_type, 0) + 1
                    
                    # Track processing time
                    status['processing_time'] += result.get('processing_time', 0)
                
                # Get last update time
                file_time = os.path.getmtime(batch_file)
                if not status['last_update'] or file_time > status['last_update']:
                    status['last_update'] = file_time
                    
            except Exception as e:
                print(f"Error reading {batch_file}: {e}")
    
    # Calculate metrics
    total_docs = status['total_processed'] + status['total_failed'] + status['total_skipped']
    if total_docs > 0:
        status['success_rate'] = (status['total_processed'] / total_docs) * 100
    
    if status['processing_time'] > 0:
        status['documents_per_minute'] = (status['total_processed'] / (status['processing_time'] / 60))
    
    return status

def get_ragflow_status() -> Dict:
    """Get RAGFlow server status"""
    try:
        import requests
        response = requests.get("http://localhost/api/v1/health", timeout=5)
        return {
            'status': 'running' if response.status_code == 200 else 'error',
            'response_time': response.elapsed.total_seconds()
        }
    except:
        return {'status': 'not_available', 'response_time': 0}

def display_progress(status: Dict, ragflow_status: Dict):
    """Display formatted progress information"""
    os.system('cls' if os.name == 'nt' else 'clear')
    
    print("🔄 NHAI Bulk Processing Monitor")
    print("=" * 50)
    
    # Processing Status
    total_docs = status['total_processed'] + status['total_failed'] + status['total_skipped']
    print(f"📊 Processing Progress:")
    print(f"   ✅ Processed: {status['total_processed']}")
    print(f"   ❌ Failed: {status['total_failed']}")
    print(f"   ⏭️  Skipped: {status['total_skipped']}")
    print(f"   📦 Total: {total_docs}")
    
    if total_docs > 0:
        print(f"   📈 Success Rate: {status['success_rate']:.1f}%")
    
    # Batch Information
    print(f"\n📦 Batch Information:")
    print(f"   Current Batch: {status['current_batch']}/{status['total_batches']}")
    
    # Performance Metrics
    if status['processing_time'] > 0:
        print(f"\n⚡ Performance:")
        print(f"   Total Time: {status['processing_time']:.1f}s")
        print(f"   Docs/Minute: {status['documents_per_minute']:.1f}")
        print(f"   Avg Time/Doc: {status['processing_time']/max(1, status['total_processed']):.2f}s")
    
    # RAGFlow Status
    print(f"\n🤖 RAGFlow Status:")
    print(f"   Status: {ragflow_status['status']}")
    if ragflow_status['response_time'] > 0:
        print(f"   Response Time: {ragflow_status['response_time']:.3f}s")
    
    # Last Update
    if status['last_update']:
        last_update = datetime.fromtimestamp(status['last_update'])
        print(f"\n🕒 Last Update: {last_update.strftime('%H:%M:%S')}")
    
    # Error Summary
    if status['errors']:
        print(f"\n⚠️  Error Summary:")
        for error_type, count in status['errors'].items():
            print(f"   {error_type}: {count}")
    
    print("\n" + "=" * 50)
    print("Press Ctrl+C to stop monitoring")

def main():
    """Main monitoring function"""
    print("🚀 Starting NHAI Bulk Processing Monitor...")
    print("Press Ctrl+C to stop")
    
    try:
        while True:
            status = get_processing_status()
            ragflow_status = get_ragflow_status()
            display_progress(status, ragflow_status)
            time.sleep(5)  # Update every 5 seconds
            
    except KeyboardInterrupt:
        print("\n\n🛑 Monitoring stopped")
        print("📊 Final Status:")
        final_status = get_processing_status()
        print(f"   Total Processed: {final_status['total_processed']}")
        print(f"   Success Rate: {final_status['success_rate']:.1f}%")
        print(f"   Total Time: {final_status['processing_time']:.1f}s")

if __name__ == "__main__":
    main() 