#!/usr/bin/env python3
"""
Monitor Progress - Check processing status
"""

import json
import time
from pathlib import Path

def monitor_progress():
    """Monitor the processing progress"""
    progress_file = Path("ragflow_integration/batch_progress.json")
    
    while True:
        if progress_file.exists():
            with open(progress_file, 'r', encoding='utf-8') as f:
                processed = json.load(f)
            
            successful = [p for p in processed if p['success']]
            failed = [p for p in processed if not p['success']]
            ocr_used = [p for p in processed if p['used_ocr']]
            total_chars = sum(p['text_length'] for p in processed)
            
            print(f"\n📊 Progress Update: {time.strftime('%H:%M:%S')}")
            print(f"   📄 Processed: {len(processed)}/50")
            print(f"   ✅ Successful: {len(successful)}")
            print(f"   ❌ Failed: {len(failed)}")
            print(f"   🔍 OCR Used: {len(ocr_used)}")
            print(f"   📝 Total chars: {total_chars:,}")
            
            if len(processed) >= 50:
                print("\n🎉 Processing completed!")
                break
        else:
            print("⏳ Waiting for processing to start...")
        
        time.sleep(10)  # Check every 10 seconds

if __name__ == "__main__":
    monitor_progress() 