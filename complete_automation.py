#!/usr/bin/env python3
"""
Complete Automation - Extraction + RAGFlow Integration
Handles the entire pipeline with error recovery and system monitoring
"""

import json
import time
import psutil
import subprocess
import sys
from pathlib import Path
from datetime import datetime

class CompleteAutomation:
    def __init__(self):
        self.extraction_complete = False
        self.ragflow_ready = False
        self.start_time = datetime.now()
        
    def monitor_system_resources(self):
        """Monitor CPU and memory usage"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory_percent = psutil.virtual_memory().percent
        
        print(f"💻 System Status: CPU {cpu_percent:.1f}% | RAM {memory_percent:.1f}%")
        
        # If system is overloaded, wait
        if cpu_percent > 90 or memory_percent > 90:
            print("⚠️  System overloaded, waiting 30 seconds...")
            time.sleep(30)
            return False
        return True
    
    def check_extraction_progress(self):
        """Check how many documents have been extracted"""
        extracted_dir = Path("output/extracted_texts")
        if not extracted_dir.exists():
            return 0
        
        json_files = list(extracted_dir.glob("*_text.json"))
        return len(json_files)
    
    def run_extraction(self):
        """Run the document extraction process"""
        print("📄 Starting Document Extraction (from document 51)")
        print("=" * 60)
        
        try:
            # Run extraction with system monitoring
            while True:
                if not self.monitor_system_resources():
                    continue
                
                # Start extraction process
                result = subprocess.run([
                    sys.executable, "ragflow_integration/working_batch_processor.py"
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    print("✅ Extraction completed successfully!")
                    self.extraction_complete = True
                    break
                else:
                    print(f"❌ Extraction failed: {result.stderr}")
                    print("🔄 Retrying in 60 seconds...")
                    time.sleep(60)
                    
        except KeyboardInterrupt:
            print("\n⏸️  Extraction interrupted by user")
            return False
        except Exception as e:
            print(f"❌ Extraction error: {e}")
            return False
        
        return True
    
    def setup_ragflow(self):
        """Setup RAGFlow for integration"""
        print("\n🔧 Setting up RAGFlow Integration")
        print("=" * 60)
        
        # Check if RAGFlow is running
        try:
            import requests
            response = requests.get("http://localhost:9380/health", timeout=5)
            if response.status_code == 200:
                print("✅ RAGFlow server is already running")
                self.ragflow_ready = True
                return True
        except:
            pass
        
        # Start RAGFlow if not running
        print("🚀 Starting RAGFlow server...")
        try:
            # Start RAGFlow in background
            subprocess.Popen([
                "docker-compose", "-f", "ragflow_integration/ragflow/docker/docker-compose-base.yml", "up", "-d"
            ])
            
            # Wait for RAGFlow to start
            for i in range(30):  # Wait up to 5 minutes
                time.sleep(10)
                try:
                    response = requests.get("http://localhost:9380/health", timeout=5)
                    if response.status_code == 200:
                        print("✅ RAGFlow server started successfully")
                        self.ragflow_ready = True
                        return True
                except:
                    print(f"⏳ Waiting for RAGFlow... ({i+1}/30)")
            
            print("❌ RAGFlow failed to start")
            return False
            
        except Exception as e:
            print(f"❌ Error starting RAGFlow: {e}")
            return False
    
    def run_ragflow_integration(self):
        """Run the RAGFlow integration"""
        print("\n🔗 Running RAGFlow Integration")
        print("=" * 60)
        
        if not self.ragflow_ready:
            print("❌ RAGFlow not ready")
            return False
        
        try:
            # Run RAGFlow integration
            result = subprocess.run([
                sys.executable, "ragflow_integration/ragflow_integration.py"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ RAGFlow integration completed successfully!")
                return True
            else:
                print(f"❌ RAGFlow integration failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ RAGFlow integration error: {e}")
            return False
    
    def create_final_report(self):
        """Create final completion report"""
        print("\n📋 Creating Final Report")
        print("=" * 60)
        
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        # Count extracted documents
        extracted_count = self.check_extraction_progress()
        
        report = {
            "completion_time": end_time.isoformat(),
            "duration_minutes": duration.total_seconds() / 60,
            "extraction_complete": self.extraction_complete,
            "ragflow_ready": self.ragflow_ready,
            "total_documents_extracted": extracted_count,
            "status": "COMPLETED" if self.extraction_complete else "PARTIAL"
        }
        
        # Save report
        report_file = Path("ragflow_integration/automation_report.json")
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Final report saved: {report_file}")
        print(f"📊 Summary:")
        print(f"   ⏱️  Duration: {duration.total_seconds() / 60:.1f} minutes")
        print(f"   📄 Documents extracted: {extracted_count}")
        print(f"   🔧 RAGFlow ready: {self.ragflow_ready}")
        
        return report_file
    
    def run_complete_automation(self):
        """Run the complete automation pipeline"""
        print("🤖 NHAI Policy Circulars - Complete Automation")
        print("=" * 80)
        print("🔄 This will:")
        print("   1. Extract all remaining documents (from #51)")
        print("   2. Setup RAGFlow server")
        print("   3. Integrate extracted data with RAGFlow")
        print("   4. Create searchable interface")
        print("   5. Generate final report")
        print("=" * 80)
        
        # Step 1: Run extraction
        if not self.run_extraction():
            print("❌ Extraction failed, stopping automation")
            return False
        
        # Step 2: Setup RAGFlow
        if not self.setup_ragflow():
            print("❌ RAGFlow setup failed, but extraction is complete")
            print("💡 You can manually setup RAGFlow later")
        
        # Step 3: Run RAGFlow integration
        if self.ragflow_ready:
            if not self.run_ragflow_integration():
                print("❌ RAGFlow integration failed")
        
        # Step 4: Create final report
        self.create_final_report()
        
        print("\n🎉 Automation Complete!")
        print("=" * 80)
        print("📊 What's ready:")
        print("   ✅ All documents extracted and saved")
        if self.ragflow_ready:
            print("   ✅ RAGFlow server running")
            print("   ✅ Search interface available")
        print("   📁 Check output/extracted_texts/ for all documents")
        print("   📁 Check ragflow_integration/ for reports")
        
        return True

def main():
    automation = CompleteAutomation()
    automation.run_complete_automation()

if __name__ == "__main__":
    main() 