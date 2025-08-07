#!/usr/bin/env python3
"""
Quick Progress Tracker - Shows document status without heavy processing
"""

import re
import json
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

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
            'filename': link.split('/')[-1] if link else "unknown.pdf",
            'status': 'Pending',
            'processed_date': None,
            'ocr_method': None,
            'content_length': 0,
            'processing_time': 0,
            'error_message': None
        }
        
    except Exception as e:
        return None

def create_progress_excel(documents: List[Dict], output_file: str = "ragflow_integration/NHAI_Progress_Tracker.xlsx"):
    """Create Excel file with document progress"""
    print(f"📊 Creating progress Excel file: {output_file}")
    
    try:
        # Convert to DataFrame
        df = pd.DataFrame(documents)
        
        # Reorder columns for better readability
        column_order = [
            'sr_no',
            'subject', 
            'policy_no',
            'date',
            'category',
            'link',
            'status',
            'processed_date',
            'ocr_method',
            'content_length',
            'processing_time',
            'error_message',
            'filename'
        ]
        
        # Only include columns that exist
        existing_columns = [col for col in column_order if col in df.columns]
        df = df[existing_columns]
        
        # Create Excel writer
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # Main progress sheet
            df.to_excel(writer, sheet_name='Document_Progress', index=False)
            
            # Summary sheet
            create_summary_sheet(writer, df)
            
            # Auto-adjust column widths
            worksheet = writer.sheets['Document_Progress']
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        print(f"✅ Progress Excel file created: {output_file}")
        return output_file
        
    except Exception as e:
        print(f"❌ Error creating Excel file: {e}")
        return None

def create_summary_sheet(writer, df):
    """Create summary sheet"""
    summary_data = {
        'Metric': [
            'Total Documents',
            'Pending Processing',
            'Processed',
            'Failed',
            'Download Failed',
            'Administration Documents',
            'Finance Documents',
            'Technical Documents',
            'Land Acquisition Documents',
            'Environment Documents',
            'Other Categories'
        ],
        'Value': [
            len(df),
            len(df[df['status'] == 'Pending']),
            len(df[df['status'] == 'Processed']),
            len(df[df['status'] == 'Failed']),
            len(df[df['status'] == 'Download Failed']),
            len(df[df['category'] == 'ADMINISTRATION']),
            len(df[df['category'] == 'FINANCE']),
            len(df[df['category'] == 'TECHNICAL']),
            len(df[df['category'] == 'LAND ACQUISITION']),
            len(df[df['category'] == 'ENVIRONMENT']),
            len(df[~df['category'].isin(['ADMINISTRATION', 'FINANCE', 'TECHNICAL', 'LAND ACQUISITION', 'ENVIRONMENT'])])
        ]
    }
    
    summary_df = pd.DataFrame(summary_data)
    summary_df.to_excel(writer, sheet_name='Summary', index=False)

def show_progress(documents: List[Dict], max_show: int = 20):
    """Show progress of documents"""
    print(f"\n📊 Document Progress Summary")
    print("=" * 50)
    print(f"Total Documents: {len(documents)}")
    
    # Count by status
    status_counts = {}
    for doc in documents:
        status = doc['status']
        status_counts[status] = status_counts.get(status, 0) + 1
    
    print(f"\n📋 Status Breakdown:")
    for status, count in status_counts.items():
        print(f"   • {status}: {count}")
    
    # Count by category
    category_counts = {}
    for doc in documents:
        category = doc['category']
        category_counts[category] = category_counts.get(category, 0) + 1
    
    print(f"\n📂 Category Breakdown:")
    for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"   • {category}: {count}")
    
    # Show first few documents
    print(f"\n📄 First {max_show} Documents:")
    print("-" * 80)
    for i, doc in enumerate(documents[:max_show]):
        print(f"{i+1:2d}. {doc['sr_no']:8s} | {doc['status']:12s} | {doc['category']:15s} | {doc['subject'][:40]}...")
    
    if len(documents) > max_show:
        print(f"... and {len(documents) - max_show} more documents")

def main():
    print("🚀 Quick Progress Tracker")
    print("==========================")
    
    # Parse all documents
    documents = parse_extracted_links("data/extracted_links.txt")
    
    if not documents:
        print("❌ No documents found!")
        return
    
    # Show progress
    show_progress(documents)
    
    # Create Excel file
    excel_file = create_progress_excel(documents)
    
    if excel_file:
        print(f"\n🎉 Progress tracking completed!")
        print(f"📊 Excel file: {excel_file}")
        print(f"📄 Total documents tracked: {len(documents)}")
        print("\n📋 Excel file contains:")
        print("   • Document_Progress - All documents with status")
        print("   • Summary - Statistics and breakdowns")
        print("\n🎯 All documents are currently marked as 'Pending'")
        print("🎯 You can now run the full processor to update statuses")
    else:
        print("❌ Failed to create Excel file")

if __name__ == "__main__":
    main() 