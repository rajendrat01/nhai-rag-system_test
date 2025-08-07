#!/usr/bin/env python3
"""
Comprehensive NHAI Document Tracker
Processes ALL 1620 links and creates detailed Excel tracking
"""

import os
import json
import sys
import time
import re
import requests
from datetime import datetime
from typing import Dict, List, Optional
import logging
import pandas as pd
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ComprehensiveTracker:
    """
    Comprehensive tracking system for all NHAI documents
    """
    
    def __init__(self):
        self.tracking_data = []
        self.categories = {
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
        
        logger.info("✅ Comprehensive tracker initialized")
    
    def parse_extracted_links(self, file_path: str) -> List[Dict]:
        """Parse the extracted_links.txt file"""
        logger.info(f"📄 Parsing extracted links from: {file_path}")
        
        documents = []
        current_category = "UNKNOWN"
        
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
                if any(cat in section for cat in self.categories.keys()):
                    for cat_key, cat_name in self.categories.items():
                        if cat_key in section:
                            current_category = cat_name
                            logger.info(f"📂 Found category: {current_category}")
                            break
                    continue
                
                # Skip header sections
                if 'NHAI Policy Circulars' in section or 'Total Links Found' in section:
                    continue
                
                # Check if this section contains document information
                if 'Sr.No:' in section and 'Link:' in section:
                    # Parse document information
                    doc_info = self._parse_document_section(section, current_category)
                    if doc_info:
                        documents.append(doc_info)
                        logger.info(f"📄 Found document: {doc_info['sr_no']} - {doc_info['subject'][:30]}...")
            
            logger.info(f"✅ Parsed {len(documents)} documents from {len(doc_sections)} sections")
            return documents
            
        except Exception as e:
            logger.error(f"❌ Error parsing extracted links: {e}")
            return []
    
    def _parse_document_section(self, section: str, category: str) -> Optional[Dict]:
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
            
            # Parse date
            try:
                if date_str != "Unknown Date":
                    # Handle different date formats
                    if '.' in date_str:
                        date_obj = datetime.strptime(date_str, '%d.%m.%Y')
                    else:
                        date_obj = datetime.strptime(date_str, '%d/%m/%Y')
                else:
                    date_obj = datetime.now()
            except:
                date_obj = datetime.now()
            
            return {
                'sr_no': sr_no,
                'subject': subject,
                'policy_no': policy_no,
                'date': date_str,
                'date_obj': date_obj,
                'link': link,
                'category': category,
                'filename': self._extract_filename(link),
                'status': 'Pending',
                'processed_date': None,
                'ocr_method': None,
                'content_length': 0,
                'processing_time': 0,
                'error_message': None
            }
            
        except Exception as e:
            logger.warning(f"⚠️ Error parsing section: {e}")
            return None
    
    def _extract_filename(self, link: str) -> str:
        """Extract filename from link"""
        if link:
            return link.split('/')[-1]
        return "unknown.pdf"
    
    def download_document(self, link: str, filename: str) -> Dict:
        """Download document from link"""
        try:
            # Create downloads directory
            download_dir = Path("ragflow_integration/downloads")
            download_dir.mkdir(exist_ok=True)
            
            file_path = download_dir / filename
            
            # Check if already downloaded
            if file_path.exists():
                return {
                    'success': True,
                    'file_path': str(file_path),
                    'message': 'Already downloaded'
                }
            
            # Download file
            response = requests.get(link, timeout=30)
            response.raise_for_status()
            
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            return {
                'success': True,
                'file_path': str(file_path),
                'message': 'Downloaded successfully'
            }
            
        except Exception as e:
            return {
                'success': False,
                'file_path': None,
                'message': str(e)
            }
    
    def process_document_with_ocr(self, file_path: str) -> Dict:
        """Process document with OCR"""
        try:
            # Import OCR processor
            sys.path.append("ragflow_integration")
            from ocr_processor import MultiOCRProcessor
            
            ocr_processor = MultiOCRProcessor()
            result = ocr_processor.extract_text(file_path, method='auto')
            
            if result['success']:
                return {
                    'success': True,
                    'ocr_method': result['method'],
                    'content_length': len(result['text']),
                    'content_preview': result['text'][:200] + "..." if len(result['text']) > 200 else result['text']
                }
            else:
                return {
                    'success': False,
                    'ocr_method': 'failed',
                    'content_length': 0,
                    'error': result.get('error', 'Unknown OCR error')
                }
                
        except Exception as e:
            return {
                'success': False,
                'ocr_method': 'error',
                'content_length': 0,
                'error': str(e)
            }
    
    def process_all_documents(self, max_documents: int = None) -> List[Dict]:
        """Process all documents and track progress"""
        logger.info("🚀 Starting comprehensive document processing...")
        
        # Parse all documents
        documents = self.parse_extracted_links("data/extracted_links.txt")
        
        if max_documents:
            documents = documents[:max_documents]
        
        logger.info(f"📊 Processing {len(documents)} documents...")
        
        processed_count = 0
        failed_count = 0
        
        for i, doc in enumerate(documents):
            try:
                logger.info(f"📄 Processing {i+1}/{len(documents)}: {doc['sr_no']} - {doc['subject'][:50]}...")
                
                start_time = time.time()
                
                # Download document
                download_result = self.download_document(doc['link'], doc['filename'])
                
                if download_result['success']:
                    # Process with OCR
                    ocr_result = self.process_document_with_ocr(download_result['file_path'])
                    
                    # Update tracking data
                    doc.update({
                        'status': 'Processed' if ocr_result['success'] else 'Failed',
                        'processed_date': datetime.now(),
                        'ocr_method': ocr_result.get('ocr_method'),
                        'content_length': ocr_result.get('content_length', 0),
                        'processing_time': time.time() - start_time,
                        'error_message': ocr_result.get('error'),
                        'file_path': download_result['file_path']
                    })
                    
                    if ocr_result['success']:
                        processed_count += 1
                        logger.info(f"✅ Processed: {doc['sr_no']} ({processed_count} successful)")
                    else:
                        failed_count += 1
                        logger.warning(f"❌ Failed: {doc['sr_no']} - {ocr_result.get('error')}")
                else:
                    doc.update({
                        'status': 'Download Failed',
                        'processed_date': datetime.now(),
                        'error_message': download_result['message'],
                        'processing_time': time.time() - start_time
                    })
                    failed_count += 1
                    logger.warning(f"❌ Download failed: {doc['sr_no']} - {download_result['message']}")
                
                self.tracking_data.append(doc)
                
                # Save progress every 10 documents
                if (i + 1) % 10 == 0:
                    self.save_progress()
                
                # Small delay to avoid overwhelming the server
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"❌ Error processing {doc.get('sr_no', 'Unknown')}: {e}")
                doc.update({
                    'status': 'Error',
                    'processed_date': datetime.now(),
                    'error_message': str(e),
                    'processing_time': time.time() - start_time
                })
                self.tracking_data.append(doc)
                failed_count += 1
        
        logger.info(f"🎉 Processing completed! {processed_count} successful, {failed_count} failed")
        return self.tracking_data
    
    def save_progress(self):
        """Save current progress to JSON"""
        try:
            progress_file = "ragflow_integration/processing_progress.json"
            with open(progress_file, 'w', encoding='utf-8') as f:
                json.dump(self.tracking_data, f, indent=2, default=str)
            logger.info(f"💾 Progress saved: {len(self.tracking_data)} documents")
        except Exception as e:
            logger.error(f"❌ Error saving progress: {e}")
    
    def create_excel_report(self, output_file: str = "ragflow_integration/NHAI_Document_Tracker.xlsx"):
        """Create comprehensive Excel report with ONE main sheet"""
        logger.info(f"📊 Creating Excel report: {output_file}")
        
        try:
            # Convert to DataFrame
            df = pd.DataFrame(self.tracking_data)
            
            if df.empty:
                logger.warning("⚠️ No data to create Excel report")
                return None
            
            # Sort by processed date (latest first) if available
            if 'processed_date' in df.columns:
                df['processed_date'] = pd.to_datetime(df['processed_date'])
                df = df.sort_values('processed_date', ascending=False)
            
            # Reorder columns for better readability
            column_order = [
                'sr_no',
                'subject', 
                'policy_no',
                'date',
                'category',  # Administration category as a column
                'link',
                'status',
                'processed_date',
                'ocr_method',
                'content_length',
                'processing_time',
                'error_message',
                'filename',
                'file_path'
            ]
            
            # Only include columns that exist
            existing_columns = [col for col in column_order if col in df.columns]
            df = df[existing_columns]
            
            # Create Excel writer
            with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                # Single main sheet with all details
                df.to_excel(writer, sheet_name='NHAI_Document_Tracker', index=False)
                
                # Auto-adjust column widths
                worksheet = writer.sheets['NHAI_Document_Tracker']
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)  # Cap at 50 characters
                    worksheet.column_dimensions[column_letter].width = adjusted_width
            
            logger.info(f"✅ Excel report created: {output_file}")
            logger.info(f"📊 Single sheet with {len(df)} documents and {len(df.columns)} columns")
            return output_file
            
        except Exception as e:
            logger.error(f"❌ Error creating Excel report: {e}")
            return None

def main():
    """Main function"""
    print("🚀 Comprehensive NHAI Document Tracker")
    print("==========================================")
    
    tracker = ComprehensiveTracker()
    
    # Process exactly 10 documents for testing
    documents = tracker.process_all_documents(max_documents=10)
    
    # Create Excel report
    excel_file = tracker.create_excel_report()
    
    if excel_file:
        print(f"\n🎉 Excel report created: {excel_file}")
        print("📊 Single sheet with ALL details:")
        print("   • sr_no - Serial number")
        print("   • subject - Document title")
        print("   • policy_no - Policy number")
        print("   • date - Document date")
        print("   • category - Administration category (ADMINISTRATION, FINANCE, etc.)")
        print("   • link - Original document link")
        print("   • status - Processing status (Processed/Failed/Download Failed)")
        print("   • processed_date - When it was processed")
        print("   • ocr_method - Which OCR method was used")
        print("   • content_length - How much content was extracted")
        print("   • processing_time - Time taken to process")
        print("   • error_message - Any errors encountered")
        print("   • filename - Downloaded filename")
        print("   • file_path - Local file path")
        print("\n🎯 Sorted by latest processing date (newest first)")
        print(f"\n📊 Processed {len(documents)} documents successfully!")
    else:
        print("❌ Failed to create Excel report")

if __name__ == "__main__":
    main() 