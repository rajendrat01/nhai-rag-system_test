#!/usr/bin/env python3
"""
Test script to verify document loading
"""

import json
from pathlib import Path

def test_loading():
    extracted_dir = Path("output/extracted_texts")
    json_files = list(extracted_dir.glob("*.json"))
    
    print(f"Found {len(json_files)} JSON files")
    
    loaded_count = 0
    for json_file in json_files[:5]:  # Test first 5 files
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Check for both possible field names
            text = data.get('extracted_text') or data.get('text')
            if text:
                print(f"✅ Loaded {json_file.name}: {len(text)} characters")
                print(f"   Subject: {data.get('subject', 'No subject')}")
                print(f"   Date: {data.get('date', 'No date')}")
                loaded_count += 1
            else:
                print(f"❌ No text found in {json_file.name}")
                
        except Exception as e:
            print(f"❌ Error loading {json_file.name}: {e}")
    
    print(f"\nSuccessfully loaded {loaded_count} documents")

if __name__ == "__main__":
    test_loading() 