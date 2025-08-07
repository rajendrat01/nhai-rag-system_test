#!/usr/bin/env python3
"""
Test script to check parsing without downloading or OCR
"""

import re
from datetime import datetime
from typing import Dict, List, Optional

def parse_extracted_links(file_path: str) -> List[Dict]:
    """Parse the extracted_links.txt file"""
    print(f"📄 Parsing extracted links from: {file_path}")
    
    documents = []
    current_category = "UNKNOWN"
    
    categories = {
        '1.': 'ADMINISTRATION',
        '2.': 'FINANCE',
        '3.': 'TECHNICAL',
        '4.': 'LAND ACQUISITION',
        '5.': 'ENVIRONMENT',
        '6.': 'CONTRACTS',
        '7.': 'IT & SYSTEMS',
        '8.': 'HR & PERSONNEL',
        '9.': 'PROJECT MANAGEMENT',
        '10.': 'LEGAL',
        '11.': 'SECURITY',
        '12.': 'OTHER'
    }
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split by document separators
        doc_sections = content.split('--------------------------------------------------------------------------------')
        
        for section in doc_sections:
            section = section.strip()
            if not section:
                continue
            
            # Check if this is a category header
            if any(cat in section for cat in categories.keys()):
                for cat_key, cat_name in categories.items():
                    if cat_key in section:
                        current_category = cat_name
                        print(f"📂 Found category: {current_category}")
                        break
                continue
            
            # Skip header sections
            if 'NHAI Policy Circulars' in section or 'Total Links Found' in section:
                continue
            
            # Check if this section contains document information
            if 'Sr.No:' in section and 'Link:' in section:
                # Parse document information
                doc_info = parse_document_section(section, current_category)
                if doc_info:
                    documents.append(doc_info)
                    print(f"📄 Found document: {doc_info['sr_no']} - {doc_info['subject'][:30]}...")
        
        print(f"✅ Parsed {len(documents)} documents from {len(doc_sections)} sections")
        return documents
        
    except Exception as e:
        print(f"❌ Error parsing extracted links: {e}")
        return []

def parse_document_section(section: str, category: str) -> Optional[Dict]:
    """Parse individual document section"""
    try:
        # Extract Sr.No
        sr_no_match = re.search(r'Sr\.No:\s*(.+)', section)
        sr_no = sr_no_match.group(1).strip() if sr_no_match else "Unknown"
        
        # Extract Subject
        subject_match = re.search(r'Subject:\s*(.+)', section)
        subject = subject_match.group(1).strip() if subject_match else "No Subject"
        
        # Extract Policy No
        policy_match = re.search(r'Policy No:\s*(.+)', section)
        policy_no = policy_match.group(1).strip() if policy_match else "No Policy Number"
        
        # Extract Date
        date_match = re.search(r'Date:\s*(.+)', section)
        date_str = date_match.group(1).strip() if date_match else "Unknown Date"
        
        # Extract Link
        link_match = re.search(r'Link:\s*(.+)', section)
        link = link_match.group(1).strip() if link_match else ""
        
        # Only process if we have a valid Sr.No and link
        if sr_no == "Unknown" or not link:
            return None
        
        return {
            'sr_no': sr_no,
            'subject': subject,
            'policy_no': policy_no,
            'date': date_str,
            'link': link,
            'category': category,
            'filename': link.split('/')[-1] if link else "unknown.pdf"
        }
        
    except Exception as e:
        print(f"⚠️ Error parsing section: {e}")
        return None

def main():
    print("🧪 Testing Document Parsing")
    print("============================")
    
    # Parse documents
    documents = parse_extracted_links("data/extracted_links.txt")
    
    print(f"\n📊 Found {len(documents)} documents")
    
    # Show first 10 documents
    print("\n📋 First 10 documents:")
    for i, doc in enumerate(documents[:10]):
        print(f"{i+1}. {doc['sr_no']} - {doc['subject'][:50]}... ({doc['category']})")
    
    print(f"\n✅ Parsing test completed! Found {len(documents)} total documents")

if __name__ == "__main__":
    main() 