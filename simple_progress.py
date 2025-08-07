#!/usr/bin/env python3
"""
Simple Progress Tracker - Shows immediate progress without heavy processing
"""

import re
import os

def count_documents():
    """Quick count of documents in the file"""
    print("🔍 Counting documents in extracted_links.txt...")
    
    try:
        with open("data/extracted_links.txt", 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Count Sr.No entries
        sr_no_count = len(re.findall(r'Sr\.No:', content))
        print(f"✅ Found {sr_no_count} documents")
        
        # Count categories
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
        
        print("\n📂 Category Breakdown:")
        for cat_key, cat_name in categories.items():
            count = len(re.findall(rf'{re.escape(cat_key)}', content))
            if count > 0:
                print(f"   • {cat_name}: {count} documents")
        
        return sr_no_count
        
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return 0

def show_first_10_documents():
    """Show first 10 documents with their details"""
    print("\n📄 First 10 Documents:")
    print("=" * 80)
    
    try:
        with open("data/extracted_links.txt", 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split by document separators
        sections = content.split('--------------------------------------------------------------------------------')
        
        current_category = "UNKNOWN"
        doc_count = 0
        
        for section in sections:
            if doc_count >= 10:
                break
                
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
                
                if sr_match:
                    sr_no = sr_match.group(1).strip()
                    subject = subject_match.group(1).strip() if subject_match else "No Subject"
                    date = date_match.group(1).strip() if date_match else "No Date"
                    
                    doc_count += 1
                    print(f"{doc_count:2d}. {sr_no:8s} | {current_category:15s} | {date:10s} | {subject[:40]}...")
        
        print(f"\n✅ Showed first {doc_count} documents")
        
    except Exception as e:
        print(f"❌ Error showing documents: {e}")

def create_simple_csv():
    """Create a simple CSV file with document info"""
    print("\n📊 Creating simple CSV file...")
    
    try:
        with open("data/extracted_links.txt", 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Create CSV content
        csv_content = "Sr_No,Category,Date,Subject,Status\n"
        
        sections = content.split('--------------------------------------------------------------------------------')
        current_category = "UNKNOWN"
        
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
                
                if sr_match:
                    sr_no = sr_match.group(1).strip()
                    subject = subject_match.group(1).strip() if subject_match else "No Subject"
                    date = date_match.group(1).strip() if date_match else "No Date"
                    
                    # Clean subject for CSV
                    subject_clean = subject.replace('"', '""').replace(',', ';')
                    
                    csv_content += f'"{sr_no}","{current_category}","{date}","{subject_clean}","Pending"\n'
        
        # Write CSV file
        with open("ragflow_integration/documents_progress.csv", 'w', encoding='utf-8') as f:
            f.write(csv_content)
        
        print("✅ Created documents_progress.csv")
        print("📁 File location: ragflow_integration/documents_progress.csv")
        
    except Exception as e:
        print(f"❌ Error creating CSV: {e}")

def main():
    print("🚀 Simple Progress Tracker")
    print("==========================")
    print("This will show immediate progress without heavy processing...")
    print()
    
    # Check if file exists
    if not os.path.exists("data/extracted_links.txt"):
        print("❌ File not found: data/extracted_links.txt")
        return
    
    # Count documents
    total_docs = count_documents()
    
    # Show first 10 documents
    show_first_10_documents()
    
    # Create simple CSV
    create_simple_csv()
    
    print(f"\n🎉 Progress tracking completed!")
    print(f"📊 Total documents found: {total_docs}")
    print("📁 CSV file created: ragflow_integration/documents_progress.csv")
    print("\n📋 Next steps:")
    print("   1. Open the CSV file to see all documents")
    print("   2. Run the full processor to update statuses")
    print("   3. Check the Excel file for detailed tracking")

if __name__ == "__main__":
    main() 