#!/usr/bin/env python3
"""
NHAI RAGFlow Integration Client
Provides seamless integration between NHAI policy circulars and RAGFlow
"""

import os
import json
import requests
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NHAIRAGClient:
    """
    Client for integrating NHAI policy circulars with RAGFlow
    """
    
    def __init__(self, 
                 ragflow_host: str = "localhost",
                 ragflow_port: int = 80,
                 api_key: Optional[str] = None):
        """
        Initialize NHAI RAGFlow client
        
        Args:
            ragflow_host: RAGFlow server host
            ragflow_port: RAGFlow server port
            api_key: RAGFlow API key
        """
        self.base_url = f"http://{ragflow_host}:{ragflow_port}"
        self.api_key = api_key or os.getenv("RAGFLOW_API_KEY")
        
        # Session for HTTP requests
        self.session = requests.Session()
        if self.api_key:
            self.session.headers.update({"Authorization": f"Bearer {self.api_key}"})
        
        # Test connection
        self._test_connection()
        
        logger.info(f"✓ NHAI RAGFlow client initialized: {self.base_url}")
    
    def _test_connection(self):
        """Test connection to RAGFlow server"""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                logger.info("✓ RAGFlow server connection successful")
            else:
                logger.warning(f"⚠ RAGFlow server returned status: {response.status_code}")
        except Exception as e:
            logger.error(f"✗ Failed to connect to RAGFlow server: {e}")
            raise ConnectionError(f"Cannot connect to RAGFlow server: {e}")
    
    def upload_policy_document(self, 
                              file_path: str, 
                              policy_no: str,
                              metadata: Optional[Dict] = None) -> Dict:
        """
        Upload a policy document to RAGFlow
        
        Args:
            file_path: Path to the PDF file
            policy_no: Policy number for identification
            metadata: Additional metadata for the document
            
        Returns:
            Upload result with document ID and status
        """
        try:
            # Prepare metadata
            doc_metadata = {
                "policy_no": policy_no,
                "source": "NHAI",
                "document_type": "policy_circular",
                "uploaded_at": datetime.now().isoformat(),
                **(metadata or {})
            }
            
            # Upload file
            with open(file_path, 'rb') as f:
                files = {'file': (os.path.basename(file_path), f, 'application/pdf')}
                data = {'metadata': json.dumps(doc_metadata)}
                
                response = self.session.post(
                    f"{self.base_url}/api/v1/documents/upload",
                    files=files,
                    data=data,
                    timeout=60
                )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"✓ Document uploaded successfully: {policy_no}")
                return result
            else:
                logger.error(f"✗ Upload failed: {response.status_code} - {response.text}")
                return {"error": response.text, "status_code": response.status_code}
                
        except Exception as e:
            logger.error(f"✗ Error uploading document {policy_no}: {e}")
            return {"error": str(e)}
    
    def search_policies(self, 
                       query: str, 
                       filters: Optional[Dict] = None,
                       limit: int = 10) -> List[Dict]:
        """
        Search policies using semantic search
        
        Args:
            query: Natural language query
            filters: Additional filters (policy_no, date_range, etc.)
            limit: Maximum number of results
            
        Returns:
            List of relevant policy documents
        """
        try:
            search_data = {
                "query": query,
                "limit": limit,
                "filters": filters or {}
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/search",
                json=search_data,
                timeout=30
            )
            
            if response.status_code == 200:
                results = response.json()
                logger.info(f"✓ Search completed: {len(results.get('results', []))} results")
                return results.get('results', [])
            else:
                logger.error(f"✗ Search failed: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"✗ Error searching policies: {e}")
            return []
    
    def analyze_policy(self, policy_no: str) -> Dict:
        """
        Get detailed analysis of a specific policy
        
        Args:
            policy_no: Policy number to analyze
            
        Returns:
            Policy analysis with insights and recommendations
        """
        try:
            # Search for the specific policy
            results = self.search_policies(
                query=f"policy number {policy_no}",
                filters={"policy_no": policy_no},
                limit=1
            )
            
            if not results:
                return {"error": f"Policy {policy_no} not found"}
            
            policy_doc = results[0]
            
            # Get detailed analysis
            analysis_data = {
                "document_id": policy_doc.get("id"),
                "analysis_type": "policy_insights"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/analyze",
                json=analysis_data,
                timeout=60
            )
            
            if response.status_code == 200:
                analysis = response.json()
                logger.info(f"✓ Policy analysis completed: {policy_no}")
                return analysis
            else:
                logger.error(f"✗ Analysis failed: {response.status_code} - {response.text}")
                return {"error": response.text}
                
        except Exception as e:
            logger.error(f"✗ Error analyzing policy {policy_no}: {e}")
            return {"error": str(e)}
    
    def compare_policies(self, policy_nos: List[str]) -> Dict:
        """
        Compare multiple policies
        
        Args:
            policy_nos: List of policy numbers to compare
            
        Returns:
            Comparison analysis
        """
        try:
            comparison_data = {
                "policy_numbers": policy_nos,
                "comparison_type": "policy_analysis"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/compare",
                json=comparison_data,
                timeout=120
            )
            
            if response.status_code == 200:
                comparison = response.json()
                logger.info(f"✓ Policy comparison completed: {len(policy_nos)} policies")
                return comparison
            else:
                logger.error(f"✗ Comparison failed: {response.status_code} - {response.text}")
                return {"error": response.text}
                
        except Exception as e:
            logger.error(f"✗ Error comparing policies: {e}")
            return {"error": str(e)}
    
    def generate_policy_summary(self, policy_no: str) -> Dict:
        """
        Generate a summary of a policy
        
        Args:
            policy_no: Policy number to summarize
            
        Returns:
            Policy summary
        """
        try:
            summary_data = {
                "policy_no": policy_no,
                "summary_type": "executive_summary"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/summarize",
                json=summary_data,
                timeout=60
            )
            
            if response.status_code == 200:
                summary = response.json()
                logger.info(f"✓ Policy summary generated: {policy_no}")
                return summary
            else:
                logger.error(f"✗ Summary generation failed: {response.status_code} - {response.text}")
                return {"error": response.text}
                
        except Exception as e:
            logger.error(f"✗ Error generating summary for {policy_no}: {e}")
            return {"error": str(e)}
    
    def get_policy_recommendations(self, context: str) -> List[Dict]:
        """
        Get policy recommendations based on context
        
        Args:
            context: Context or situation description
            
        Returns:
            List of relevant policy recommendations
        """
        try:
            recommendation_data = {
                "context": context,
                "recommendation_type": "policy_guidance"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/recommendations",
                json=recommendation_data,
                timeout=60
            )
            
            if response.status_code == 200:
                recommendations = response.json()
                logger.info(f"✓ Recommendations generated: {len(recommendations.get('recommendations', []))} items")
                return recommendations.get('recommendations', [])
            else:
                logger.error(f"✗ Recommendations failed: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"✗ Error getting recommendations: {e}")
            return []
    
    def get_document_statistics(self) -> Dict:
        """
        Get statistics about uploaded documents
        
        Returns:
            Document statistics
        """
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/statistics",
                timeout=30
            )
            
            if response.status_code == 200:
                stats = response.json()
                logger.info("✓ Document statistics retrieved")
                return stats
            else:
                logger.error(f"✗ Statistics failed: {response.status_code} - {response.text}")
                return {"error": response.text}
                
        except Exception as e:
            logger.error(f"✗ Error getting statistics: {e}")
            return {"error": str(e)}

def main():
    """Example usage of NHAI RAGFlow client"""
    # Initialize client
    client = NHAIRAGClient()
    
    # Example: Search for land acquisition policies
    results = client.search_policies("land acquisition procedures")
    print(f"Found {len(results)} relevant policies")
    
    # Example: Analyze specific policy
    analysis = client.analyze_policy("7.1.88")
    print(f"Policy analysis: {analysis}")
    
    # Example: Get recommendations
    recommendations = client.get_policy_recommendations("road construction project planning")
    print(f"Got {len(recommendations)} recommendations")

if __name__ == "__main__":
    main() 