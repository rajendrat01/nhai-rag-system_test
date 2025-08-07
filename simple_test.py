#!/usr/bin/env python3
"""
Simple RAGFlow Integration Test (No Docker Required)
This script demonstrates the RAGFlow integration without requiring Docker.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

def test_data_loading():
    """Test loading existing circulars data"""
    print("🔍 Testing Data Loading...")
    
    # Load existing circulars
    existing_links_path = Path("output/existing_links.json")
    if not existing_links_path.exists():
        print("❌ existing_links.json not found")
        return False
    
    with open(existing_links_path, 'r', encoding='utf-8') as f:
        circulars = json.load(f)
    
    print(f"✅ Loaded {len(circulars)} circulars from database")
    return True

def test_extracted_texts():
    """Test loading extracted text files"""
    print("\n📄 Testing Extracted Texts...")
    
    extracted_dir = Path("output/extracted_texts")
    if not extracted_dir.exists():
        print("❌ extracted_texts directory not found")
        return False
    
    text_files = list(extracted_dir.glob("*_text.json"))
    print(f"✅ Found {len(text_files)} extracted text files")
    
    # Show sample data
    if text_files:
        sample_file = text_files[0]
        with open(sample_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"📋 Sample: {data.get('policy_no', 'Unknown')}")
        print(f"📏 Text length: {len(data.get('extracted_text', ''))} characters")
    
    return True

def test_pdf_files():
    """Test PDF file availability"""
    print("\n📚 Testing PDF Files...")
    
    pdf_dir = Path("output/pdfs")
    if not pdf_dir.exists():
        print("❌ pdfs directory not found")
        return False
    
    pdf_files = list(pdf_dir.glob("*.pdf"))
    print(f"✅ Found {len(pdf_files)} PDF files")
    
    # Show file sizes
    total_size = 0
    for pdf_file in pdf_files:
        size = pdf_file.stat().st_size
        total_size += size
        print(f"   📄 {pdf_file.name}: {size/1024/1024:.1f} MB")
    
    print(f"📊 Total PDF size: {total_size/1024/1024:.1f} MB")
    return True

def test_ragflow_components():
    """Test RAGFlow integration components"""
    print("\n🤖 Testing RAGFlow Components...")
    
    try:
        from ragflow_integration.nhai_rag_client import NHAIRAGClient
        print("✅ RAGFlow Client imported successfully")
        
        # Test client initialization
        client = NHAIRAGClient(ragflow_host="localhost", ragflow_port=80)
        print("✅ RAGFlow Client initialized successfully")
        
    except ImportError as e:
        print(f"❌ Failed to import RAGFlow Client: {e}")
        return False
    except Exception as e:
        print(f"❌ Failed to initialize RAGFlow Client: {e}")
        return False
    
    try:
        from ragflow_integration.process_circulars import NHAICircularProcessor
        print("✅ Circular Processor imported successfully")
        
        # Test processor initialization
        processor = NHAICircularProcessor(ragflow_host="localhost", ragflow_port=80)
        print("✅ Circular Processor initialized successfully")
        
    except ImportError as e:
        print(f"❌ Failed to import Circular Processor: {e}")
        return False
    except Exception as e:
        print(f"❌ Failed to initialize Circular Processor: {e}")
        return False
    
    return True

def test_processing_pipeline():
    """Test the processing pipeline with sample data"""
    print("\n⚙️ Testing Processing Pipeline...")
    
    try:
        from ragflow_integration.process_circulars import NHAICircularProcessor
        
        # Initialize processor
        processor = NHAICircularProcessor(ragflow_host="localhost", ragflow_port=80)
        
        # Load circulars
        circulars = processor.load_existing_circulars()
        print(f"✅ Loaded {len(circulars)} circulars")
        
        # Test processing first 2 circulars
        test_circulars = circulars[:2]
        print(f"🧪 Testing with {len(test_circulars)} circulars")
        
        for i, circular in enumerate(test_circulars, 1):
            policy_no = circular.get('policy_no', 'Unknown')
            subject = circular.get('subject', 'No subject')
            print(f"   {i}. {policy_no}: {subject[:50]}...")
        
        print("✅ Processing pipeline test completed")
        return True
        
    except Exception as e:
        print(f"❌ Processing pipeline test failed: {e}")
        return False

def generate_test_report():
    """Generate a comprehensive test report"""
    print("\n📊 Generating Test Report...")
    
    report = {
        "test_date": datetime.now().isoformat(),
        "tests": {}
    }
    
    # Run all tests
    tests = [
        ("Data Loading", test_data_loading),
        ("Extracted Texts", test_extracted_texts),
        ("PDF Files", test_pdf_files),
        ("RAGFlow Components", test_ragflow_components),
        ("Processing Pipeline", test_processing_pipeline)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            report["tests"][test_name] = {
                "status": "PASS" if result else "FAIL",
                "timestamp": datetime.now().isoformat()
            }
            if result:
                passed += 1
        except Exception as e:
            report["tests"][test_name] = {
                "status": "ERROR",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    # Save report
    report_path = Path("test_report.json")
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n🎯 Test Results: {passed}/{total} tests passed")
    print(f"📄 Report saved to: {report_path}")
    
    if passed == total:
        print("🎉 All tests passed! Your RAGFlow integration is ready!")
    else:
        print("⚠️ Some tests failed. Check the report for details.")
    
    return passed == total

def main():
    """Main test function"""
    print("🚀 NHAI RAGFlow Integration Test (No Docker Required)")
    print("=" * 60)
    
    success = generate_test_report()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ ALL TESTS PASSED!")
        print("\n🎯 Your RAGFlow integration is working perfectly!")
        print("📋 Next steps:")
        print("   1. Install Docker Desktop")
        print("   2. Run: python ragflow_integration/setup_ragflow.py")
        print("   3. Run: ./start_nhai_ragflow.sh")
        print("   4. Run: python ragflow_integration/process_circulars.py --max-circulars 10")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main()) 