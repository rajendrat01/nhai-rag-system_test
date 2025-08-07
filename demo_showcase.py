#!/usr/bin/env python3
"""
Demo Showcase - What you can do with extracted NHAI Policy Circulars
"""

import json
import os
from pathlib import Path
from collections import Counter
import re

class NHAIDemoShowcase:
    def __init__(self):
        self.extracted_dir = Path("output/extracted_texts")
        self.results_file = Path("ragflow_integration/batch_final_results.json")
        
    def load_data(self):
        """Load all extracted data"""
        print("📊 Loading extracted NHAI Policy Circulars data...")
        
        # Load summary results
        if self.results_file.exists():
            with open(self.results_file, 'r', encoding='utf-8') as f:
                self.summary_data = json.load(f)
        else:
            self.summary_data = []
        
        # Load individual documents
        self.documents = []
        json_files = list(self.extracted_dir.glob("*_text.json"))
        
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    doc = json.load(f)
                    self.documents.append(doc)
            except Exception as e:
                print(f"❌ Error loading {json_file}: {e}")
        
        print(f"✅ Loaded {len(self.documents)} documents")
        return len(self.documents) > 0
    
    def show_statistics(self):
        """Show comprehensive statistics"""
        print("\n📈 NHAI Policy Circulars - Statistics")
        print("=" * 50)
        
        if not self.documents:
            print("❌ No documents loaded")
            return
        
        # Basic stats
        total_docs = len(self.documents)
        successful_docs = len([d for d in self.documents if d['success']])
        total_chars = sum(d['text_length'] for d in self.documents)
        avg_chars = total_chars / total_docs if total_docs > 0 else 0
        
        print(f"📄 Total Documents: {total_docs}")
        print(f"✅ Successful Extractions: {successful_docs}")
        print(f"📝 Total Characters: {total_chars:,}")
        print(f"📊 Average Characters per Doc: {avg_chars:.0f}")
        
        # Extraction methods
        methods = Counter(d['extraction_method'] for d in self.documents)
        print(f"\n🔧 Extraction Methods:")
        for method, count in methods.items():
            print(f"   {method}: {count} documents")
        
        # Date analysis
        dates = [d['date'] for d in self.documents if d['date']]
        if dates:
            print(f"\n📅 Date Range:")
            print(f"   Earliest: {min(dates)}")
            print(f"   Latest: {max(dates)}")
    
    def search_keywords(self, keywords):
        """Search for specific keywords in documents"""
        print(f"\n🔍 Keyword Search: {', '.join(keywords)}")
        print("=" * 50)
        
        results = []
        for doc in self.documents:
            if not doc['success'] or not doc['text']:
                continue
            
            text_lower = doc['text'].lower()
            matches = []
            
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    matches.append(keyword)
            
            if matches:
                results.append({
                    'doc': doc,
                    'matches': matches,
                    'match_count': len(matches)
                })
        
        # Sort by match count
        results.sort(key=lambda x: x['match_count'], reverse=True)
        
        print(f"📊 Found {len(results)} documents with keyword matches")
        
        for i, result in enumerate(results[:10], 1):  # Show top 10
            doc = result['doc']
            matches = result['matches']
            print(f"\n{i}. {doc['sr_no']} - {doc['subject'][:60]}...")
            print(f"   📅 Date: {doc['date']}")
            print(f"   🔍 Matches: {', '.join(matches)}")
            print(f"   📝 Text length: {doc['text_length']} chars")
    
    def analyze_topics(self):
        """Analyze common topics and themes"""
        print("\n📋 Topic Analysis")
        print("=" * 50)
        
        # Common NHAI topics
        topics = {
            'delegation': ['delegation', 'power', 'authority', 'approval'],
            'toll': ['toll', 'collection', 'fee', 'payment'],
            'construction': ['construction', 'road', 'highway', 'project'],
            'administration': ['administrative', 'procedure', 'process', 'guideline'],
            'finance': ['financial', 'budget', 'cost', 'expenditure'],
            'tender': ['tender', 'bidding', 'contract', 'procurement'],
            'safety': ['safety', 'security', 'maintenance', 'inspection'],
            'technology': ['technology', 'digital', 'system', 'software']
        }
        
        topic_stats = {}
        
        for topic, keywords in topics.items():
            count = 0
            for doc in self.documents:
                if not doc['success'] or not doc['text']:
                    continue
                
                text_lower = doc['text'].lower()
                if any(keyword in text_lower for keyword in keywords):
                    count += 1
            
            topic_stats[topic] = count
        
        # Sort by frequency
        sorted_topics = sorted(topic_stats.items(), key=lambda x: x[1], reverse=True)
        
        print("📊 Documents by Topic:")
        for topic, count in sorted_topics:
            percentage = (count / len(self.documents)) * 100 if self.documents else 0
            print(f"   {topic.title()}: {count} documents ({percentage:.1f}%)")
    
    def show_sample_documents(self, count=5):
        """Show sample documents with their content"""
        print(f"\n📄 Sample Documents (showing {count})")
        print("=" * 50)
        
        successful_docs = [d for d in self.documents if d['success']]
        
        for i, doc in enumerate(successful_docs[:count], 1):
            print(f"\n{i}. Document: {doc['sr_no']}")
            print(f"   Subject: {doc['subject']}")
            print(f"   Date: {doc['date']}")
            print(f"   Method: {doc['extraction_method']}")
            print(f"   Length: {doc['text_length']} characters")
            
            # Show first 200 characters of text
            text_preview = doc['text'][:200].replace('\n', ' ')
            print(f"   Preview: {text_preview}...")
    
    def create_search_demo(self):
        """Create a simple search demo"""
        print("\n🔍 Interactive Search Demo")
        print("=" * 50)
        print("Type 'quit' to exit")
        
        while True:
            query = input("\n🔍 Enter search term: ").strip()
            
            if query.lower() == 'quit':
                break
            
            if not query:
                continue
            
            # Simple search
            results = []
            for doc in self.documents:
                if not doc['success'] or not doc['text']:
                    continue
                
                if query.lower() in doc['text'].lower():
                    results.append(doc)
            
            print(f"\n📊 Found {len(results)} documents containing '{query}'")
            
            for i, doc in enumerate(results[:5], 1):  # Show top 5
                print(f"\n{i}. {doc['sr_no']} - {doc['subject']}")
                print(f"   Date: {doc['date']}")
                
                # Find the context around the search term
                text_lower = doc['text'].lower()
                query_lower = query.lower()
                pos = text_lower.find(query_lower)
                
                if pos != -1:
                    start = max(0, pos - 50)
                    end = min(len(doc['text']), pos + len(query) + 50)
                    context = doc['text'][start:end].replace('\n', ' ')
                    print(f"   Context: ...{context}...")
    
    def export_summary_report(self):
        """Export a summary report"""
        print("\n📋 Creating Summary Report")
        print("=" * 50)
        
        report = {
            "summary": {
                "total_documents": len(self.documents),
                "successful_extractions": len([d for d in self.documents if d['success']]),
                "total_characters": sum(d['text_length'] for d in self.documents),
                "average_characters": sum(d['text_length'] for d in self.documents) / len(self.documents) if self.documents else 0
            },
            "extraction_methods": Counter(d['extraction_method'] for d in self.documents),
            "date_range": {
                "earliest": min(d['date'] for d in self.documents if d['date']),
                "latest": max(d['date'] for d in self.documents if d['date'])
            },
            "sample_documents": [
                {
                    "sr_no": doc['sr_no'],
                    "subject": doc['subject'],
                    "date": doc['date'],
                    "text_length": doc['text_length'],
                    "extraction_method": doc['extraction_method']
                }
                for doc in self.documents[:10]  # First 10 documents
            ]
        }
        
        # Save report
        report_file = Path("ragflow_integration/nhai_extraction_report.json")
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Summary report saved: {report_file}")
        return report_file
    
    def run_complete_demo(self):
        """Run complete demo showcase"""
        print("🎯 NHAI Policy Circulars - Demo Showcase")
        print("=" * 60)
        
        # Load data
        if not self.load_data():
            print("❌ No data available for demo")
            return
        
        # Run all demos
        self.show_statistics()
        self.analyze_topics()
        self.show_sample_documents()
        
        # Search for common NHAI terms
        self.search_keywords(['delegation', 'toll', 'construction', 'administration'])
        
        # Export report
        self.export_summary_report()
        
        print("\n🎉 Demo Showcase Complete!")
        print("=" * 60)
        print("📊 What you can do with this data:")
        print("   1. 🔍 Search for specific policies and procedures")
        print("   2. 📈 Analyze trends and patterns")
        print("   3. 🤖 Build Q&A systems")
        print("   4. 📋 Generate reports and summaries")
        print("   5. 🔗 Integrate with other systems")
        print("   6. 📱 Create mobile applications")
        print("   7. 🌐 Build web interfaces")
        print("   8. 📊 Create dashboards and analytics")

def main():
    demo = NHAIDemoShowcase()
    demo.run_complete_demo()

if __name__ == "__main__":
    main() 