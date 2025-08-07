#!/usr/bin/env python3
"""
Instant Progress Tracker - Shows immediate progress with CSV export
"""

import re
import os

def main():
    print("🚀 INSTANT PROGRESS TRACKER")
    print("=" * 40)
    
    # Check if file exists
    if not os.path.exists("data/extracted_links.txt"):
        print("❌ File not found: data/extracted_links.txt")
        return
    
    print("📄 Reading file...")
    
    try:
        with open("data/extracted_links.txt", 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Quick count
        sr_count = len(re.findall(r'Sr\.No:', content))
        print(f"✅ Found {sr_count} documents")
        
        # Create CSV content
        csv_content = "Sr_No,Category,Date,Subject,Link,Status\n"
        
        # Parse documents and create CSV
        sections = content.split('--------------------------------------------------------------------------------')
        current_category = "UNKNOWN"
        doc_count = 0
        
        for section in sections:
            section = section.strip()
            if not section:
                continue
            
            # Check for category headers
            if '1. ADMINISTRATION' in section:
                current_category = "ADMINISTRATION"
                continue
            elif '2. FINANCE' in section:
                current_category = "FINANCE"
                continue
            elif '3. TECHNICAL' in section:
                current_category = "TECHNICAL"
                continue
            elif '4. LAND ACQUISITION' in section:
                current_category = "LAND ACQUISITION"
                continue
            elif '5. ENVIRONMENT' in section:
                current_category = "ENVIRONMENT"
                continue
            
            # Skip headers
            if 'NHAI Policy Circulars' in section or 'Total Links Found' in section:
                continue
            
            # Check if this is a document section
            if 'Sr.No:' in section and 'Link:' in section:
                # Extract basic info
                sr_match = re.search(r'Sr\.No:\s*(.+)', section)
                subject_match = re.search(r'Subject:\s*(.+)', section)
                date_match = re.search(r'Date:\s*(.+)', section)
                link_match = re.search(r'Link:\s*(.+)', section)
                
                if sr_match and link_match:
                    sr_no = sr_match.group(1).strip()
                    subject = subject_match.group(1).strip() if subject_match else "No Subject"
                    date = date_match.group(1).strip() if date_match else "No Date"
                    link = link_match.group(1).strip()
                    
                    # Clean subject for CSV
                    subject_clean = subject.replace('"', '""').replace(',', ';')
                    
                    csv_content += f'"{sr_no}","{current_category}","{date}","{subject_clean}","{link}","Pending"\n'
                    doc_count += 1
        
        # Write CSV file
        with open("ragflow_integration/documents_with_links.csv", 'w', encoding='utf-8') as f:
            f.write(csv_content)
        
        print(f"\n📊 Created CSV with {doc_count} documents")
        print("📁 File: ragflow_integration/documents_with_links.csv")
        print("📋 Columns: Sr_No, Category, Date, Subject, Link, Status")
        
        # Show first 5 documents
        print("\n📋 First 5 Documents:")
        print("-" * 80)
        
        lines = content.split('\n')
        show_count = 0
        current_category = "UNKNOWN"
        
        for i, line in enumerate(lines):
            if show_count >= 5:
                break
                
            if '1. ADMINISTRATION' in line:
                current_category = "ADMINISTRATION"
            elif '2. FINANCE' in line:
                current_category = "FINANCE"
            elif '3. TECHNICAL' in line:
                current_category = "TECHNICAL"
            elif '4. LAND ACQUISITION' in line:
                current_category = "LAND ACQUISITION"
            elif '5. ENVIRONMENT' in line:
                current_category = "ENVIRONMENT"
            
            if 'Sr.No:' in line:
                sr_match = re.search(r'Sr\.No:\s*(.+)', line)
                if sr_match:
                    sr_no = sr_match.group(1).strip()
                    show_count += 1
                    print(f"{show_count}. {sr_no} | {current_category}")
        
        print(f"\n🎉 Quick scan completed!")
        print(f"📊 Total documents: {sr_count}")
        print("📁 CSV file created with document links!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 