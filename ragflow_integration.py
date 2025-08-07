#!/usr/bin/env python3
"""
RAGFlow Integration - Upload extracted texts to RAGFlow for search
"""

import json
import os
import requests
import time
from pathlib import Path
from datetime import datetime

class RAGFlowIntegration:
    def __init__(self):
        self.ragflow_url = "http://localhost:9380"
        self.api_key = "your_api_key_here"  # Will be set during setup
        self.dataset_name = "nhai_policy_circulars"
        self.extracted_dir = Path("output/extracted_texts")
        
    def setup_ragflow(self):
        """Setup RAGFlow connection and create dataset"""
        print("🔧 Setting up RAGFlow Integration")
        print("=" * 50)
        
        # Test connection
        try:
            response = requests.get(f"{self.ragflow_url}/health")
            if response.status_code == 200:
                print("✅ RAGFlow server is running")
            else:
                print("❌ RAGFlow server not responding")
                return False
        except Exception as e:
            print(f"❌ Cannot connect to RAGFlow: {e}")
            print("💡 Make sure RAGFlow Docker is running")
            return False
        
        return True
    
    def create_dataset(self):
        """Create dataset in RAGFlow"""
        print(f"📊 Creating dataset: {self.dataset_name}")
        
        # Create dataset API call
        dataset_data = {
            "name": self.dataset_name,
            "description": "NHAI Policy Circulars - Complete collection of extracted documents",
            "document_type": "text"
        }
        
        try:
            response = requests.post(
                f"{self.ragflow_url}/api/v1/datasets",
                json=dataset_data,
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            
            if response.status_code == 201:
                print("✅ Dataset created successfully")
                return True
            else:
                print(f"❌ Failed to create dataset: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error creating dataset: {e}")
            return False
    
    def upload_documents(self):
        """Upload all extracted documents to RAGFlow"""
        print("📤 Uploading documents to RAGFlow")
        print("=" * 50)
        
        # Get all JSON files
        json_files = list(self.extracted_dir.glob("*_text.json"))
        print(f"📁 Found {len(json_files)} documents to upload")
        
        uploaded = 0
        failed = 0
        
        for i, json_file in enumerate(json_files, 1):
            try:
                # Read JSON file
                with open(json_file, 'r', encoding='utf-8') as f:
                    doc_data = json.load(f)
                
                # Prepare document for upload
                document = {
                    "content": doc_data['text'],
                    "metadata": {
                        "sr_no": doc_data['sr_no'],
                        "subject": doc_data['subject'],
                        "date": doc_data['date'],
                        "policy_no": doc_data.get('policy_no', ''),
                        "filename": doc_data['filename'],
                        "extraction_method": doc_data['extraction_method'],
                        "text_length": doc_data['text_length']
                    }
                }
                
                # Upload to RAGFlow
                response = requests.post(
                    f"{self.ragflow_url}/api/v1/datasets/{self.dataset_name}/documents",
                    json=document,
                    headers={"Authorization": f"Bearer {self.api_key}"}
                )
                
                if response.status_code == 201:
                    uploaded += 1
                    print(f"✅ [{i}/{len(json_files)}] Uploaded: {doc_data['sr_no']}")
                else:
                    failed += 1
                    print(f"❌ [{i}/{len(json_files)}] Failed: {doc_data['sr_no']} - {response.text}")
                
                # Small delay to avoid overwhelming the server
                time.sleep(0.1)
                
            except Exception as e:
                failed += 1
                print(f"❌ [{i}/{len(json_files)}] Error uploading {json_file.name}: {e}")
        
        print(f"\n📊 Upload Summary:")
        print(f"   ✅ Uploaded: {uploaded}")
        print(f"   ❌ Failed: {failed}")
        
        return uploaded > 0
    
    def create_search_index(self):
        """Create search index for the dataset"""
        print("🔍 Creating search index")
        
        try:
            response = requests.post(
                f"{self.ragflow_url}/api/v1/datasets/{self.dataset_name}/index",
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            
            if response.status_code == 200:
                print("✅ Search index created successfully")
                return True
            else:
                print(f"❌ Failed to create index: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error creating index: {e}")
            return False
    
    def test_search(self):
        """Test search functionality"""
        print("🧪 Testing search functionality")
        print("=" * 50)
        
        test_queries = [
            "delegation of powers",
            "toll collection",
            "road construction",
            "administrative procedures"
        ]
        
        for query in test_queries:
            try:
                response = requests.post(
                    f"{self.ragflow_url}/api/v1/datasets/{self.dataset_name}/search",
                    json={"query": query, "top_k": 3},
                    headers={"Authorization": f"Bearer {self.api_key}"}
                )
                
                if response.status_code == 200:
                    results = response.json()
                    print(f"🔍 Query: '{query}'")
                    print(f"   Found {len(results.get('results', []))} results")
                    for i, result in enumerate(results.get('results', [])[:2], 1):
                        metadata = result.get('metadata', {})
                        print(f"   {i}. {metadata.get('sr_no', 'N/A')} - {metadata.get('subject', 'N/A')[:50]}...")
                    print()
                else:
                    print(f"❌ Search failed for '{query}': {response.text}")
                    
            except Exception as e:
                print(f"❌ Error testing search for '{query}': {e}")
    
    def create_web_interface(self):
        """Create a simple web interface for searching"""
        print("🌐 Creating web interface")
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>NHAI Policy Circulars Search</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .search-box {{ width: 80%; padding: 15px; font-size: 16px; margin-bottom: 20px; }}
        .search-btn {{ padding: 15px 30px; font-size: 16px; background: #007bff; color: white; border: none; cursor: pointer; }}
        .results {{ margin-top: 20px; }}
        .result-item {{ border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px; }}
        .result-title {{ font-weight: bold; color: #007bff; }}
        .result-meta {{ color: #666; font-size: 14px; }}
        .result-content {{ margin-top: 10px; }}
    </style>
</head>
<body>
    <h1>🔍 NHAI Policy Circulars Search</h1>
    <p>Search through {len(list(self.extracted_dir.glob("*_text.json")))} policy circulars</p>
    
    <input type="text" id="searchQuery" class="search-box" placeholder="Enter your search query...">
    <button onclick="searchDocuments()" class="search-btn">Search</button>
    
    <div id="results" class="results"></div>
    
    <script>
        async function searchDocuments() {{
            const query = document.getElementById('searchQuery').value;
            const resultsDiv = document.getElementById('results');
            
            if (!query) {{
                resultsDiv.innerHTML = '<p>Please enter a search query</p>';
                return;
            }}
            
            resultsDiv.innerHTML = '<p>Searching...</p>';
            
            try {{
                const response = await fetch('{self.ragflow_url}/api/v1/datasets/{self.dataset_name}/search', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                        'Authorization': 'Bearer {self.api_key}'
                    }},
                    body: JSON.stringify({{query: query, top_k: 10}})
                }});
                
                const data = await response.json();
                
                if (data.results && data.results.length > 0) {{
                    let html = '<h3>Search Results:</h3>';
                    data.results.forEach((result, index) => {{
                        const metadata = result.metadata || {{}};
                        html += `
                            <div class="result-item">
                                <div class="result-title">${{index + 1}}. ${{metadata.sr_no || 'N/A'}} - ${{metadata.subject || 'N/A'}}</div>
                                <div class="result-meta">Date: ${{metadata.date || 'N/A'}} | Policy No: ${{metadata.policy_no || 'N/A'}}</div>
                                <div class="result-content">${{result.content.substring(0, 200)}}...</div>
                            </div>
                        `;
                    }});
                    resultsDiv.innerHTML = html;
                }} else {{
                    resultsDiv.innerHTML = '<p>No results found</p>';
                }}
            }} catch (error) {{
                resultsDiv.innerHTML = '<p>Error searching: ' + error.message + '</p>';
            }}
        }}
        
        // Allow Enter key to trigger search
        document.getElementById('searchQuery').addEventListener('keypress', function(e) {{
            if (e.key === 'Enter') {{
                searchDocuments();
            }}
        }});
    </script>
</body>
</html>
        """
        
        # Save HTML file
        web_file = Path("ragflow_integration/nhai_search_interface.html")
        with open(web_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ Web interface created: {web_file}")
        print(f"🌐 Open in browser: file://{web_file.absolute()}")
    
    def run_complete_integration(self):
        """Run complete RAGFlow integration"""
        print("🚀 RAGFlow Integration - Complete Setup")
        print("=" * 60)
        
        # Step 1: Setup
        if not self.setup_ragflow():
            return False
        
        # Step 2: Create dataset
        if not self.create_dataset():
            return False
        
        # Step 3: Upload documents
        if not self.upload_documents():
            return False
        
        # Step 4: Create index
        if not self.create_search_index():
            return False
        
        # Step 5: Test search
        self.test_search()
        
        # Step 6: Create web interface
        self.create_web_interface()
        
        print("\n🎉 RAGFlow Integration Complete!")
        print("=" * 60)
        print("📊 What you can do now:")
        print("   1. 🌐 Open the web interface to search documents")
        print("   2. 🔍 Use the API to integrate with other applications")
        print("   3. 📈 Analyze document patterns and trends")
        print("   4. 🤖 Build chatbots or Q&A systems")
        
        return True

def main():
    integration = RAGFlowIntegration()
    integration.run_complete_integration()

if __name__ == "__main__":
    main() 