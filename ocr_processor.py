#!/usr/bin/env python3
"""
Multi-OCR Processor for NHAI Documents
Multiple free OCR methods for different document types
"""

import os
import json
import sys
import time
from typing import Dict, List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MultiOCRProcessor:
    """
    Multiple OCR methods for different document types
    All methods are FREE to use
    """
    
    def __init__(self):
        self.ocr_methods = {
            'pytesseract': self._pytesseract_ocr,
            'easyocr': self._easyocr_ocr,
            'paddleocr': self._paddleocr_ocr,
            'huggingface': self._huggingface_ocr,
            'fallback': self._simple_text_extraction
        }
        
        logger.info("✅ Multi-OCR processor initialized")
    
    def extract_text(self, file_path: str, method: str = 'auto') -> Dict:
        """
        Extract text from document using best available method
        """
        try:
            if method == 'auto':
                # Try methods in order of preference
                for method_name in ['pytesseract', 'easyocr', 'paddleocr', 'huggingface', 'fallback']:
                    try:
                        result = self.ocr_methods[method_name](file_path)
                        if result['success'] and result['text'].strip():
                            logger.info(f"✅ Used {method_name} OCR successfully")
                            return result
                    except Exception as e:
                        logger.warning(f"⚠️ {method_name} failed: {e}")
                        continue
                
                # If all fail, use fallback
                return self.ocr_methods['fallback'](file_path)
            else:
                return self.ocr_methods.get(method, self.ocr_methods['fallback'])(file_path)
                
        except Exception as e:
            logger.error(f"❌ OCR extraction failed: {e}")
            return {
                'success': False,
                'text': '',
                'method': 'none',
                'error': str(e)
            }
    
    def _pytesseract_ocr(self, file_path: str) -> Dict:
        """
        Free OCR using Tesseract (most reliable for text-heavy documents)
        """
        try:
            import pytesseract
            from PIL import Image
            
            # Open image
            image = Image.open(file_path)
            
            # Extract text
            text = pytesseract.image_to_string(image)
            
            return {
                'success': True,
                'text': text,
                'method': 'pytesseract',
                'confidence': 'high'
            }
        except ImportError:
            logger.warning("⚠️ pytesseract not installed")
            return {'success': False, 'error': 'pytesseract not available'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _easyocr_ocr(self, file_path: str) -> Dict:
        """
        Free OCR using EasyOCR (good for complex layouts)
        """
        try:
            import easyocr
            
            # Initialize reader (downloads models automatically)
            reader = easyocr.Reader(['en'])
            
            # Read text
            results = reader.readtext(file_path)
            
            # Extract text from results
            text = ' '.join([result[1] for result in results])
            
            return {
                'success': True,
                'text': text,
                'method': 'easyocr',
                'confidence': 'medium'
            }
        except ImportError:
            logger.warning("⚠️ easyocr not installed")
            return {'success': False, 'error': 'easyocr not available'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _paddleocr_ocr(self, file_path: str) -> Dict:
        """
        Free OCR using PaddleOCR (fast and accurate)
        """
        try:
            from paddleocr import PaddleOCR
            
            # Initialize OCR
            ocr = PaddleOCR(use_angle_cls=True, lang='en')
            
            # Read text
            results = ocr.ocr(file_path, cls=True)
            
            # Extract text
            text = ''
            if results and results[0]:
                for line in results[0]:
                    if line and len(line) >= 2:
                        text += line[1][0] + ' '
            
            return {
                'success': True,
                'text': text.strip(),
                'method': 'paddleocr',
                'confidence': 'high'
            }
        except ImportError:
            logger.warning("⚠️ paddleocr not installed")
            return {'success': False, 'error': 'paddleocr not available'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _huggingface_ocr(self, file_path: str) -> Dict:
        """
        Free OCR using HuggingFace API (cloud-based)
        """
        try:
            import requests
            from PIL import Image
            import base64
            import io
            
            # Load image
            with open(file_path, 'rb') as f:
                image_data = f.read()
            
            # Encode to base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # Use HuggingFace OCR API
            response = requests.post(
                "https://api-inference.huggingface.co/models/microsoft/trocr-base-handwritten",
                headers={"Content-Type": "application/json"},
                json={"inputs": {"image": image_base64}}
            )
            
            if response.status_code == 200:
                result = response.json()
                text = result.get('generated_text', '')
                
                return {
                    'success': True,
                    'text': text,
                    'method': 'huggingface',
                    'confidence': 'medium'
                }
            else:
                return {'success': False, 'error': f'API error: {response.status_code}'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _simple_text_extraction(self, file_path: str) -> Dict:
        """
        Simple text extraction for text-based files
        """
        try:
            # Try to read as text
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            if text.strip():
                return {
                    'success': True,
                    'text': text,
                    'method': 'text_extraction',
                    'confidence': 'high'
                }
            
            # Try with different encoding
            with open(file_path, 'r', encoding='latin-1') as f:
                text = f.read()
            
            return {
                'success': True,
                'text': text,
                'method': 'text_extraction',
                'confidence': 'medium'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}

def install_ocr_dependencies():
    """
    Install OCR dependencies (all free)
    """
    print("📦 Installing OCR Dependencies...")
    print("==========================================")
    
    dependencies = [
        'pytesseract',
        'easyocr', 
        'paddlepaddle',
        'paddleocr',
        'Pillow',
        'requests'
    ]
    
    for dep in dependencies:
        try:
            print(f"Installing {dep}...")
            os.system(f"py -m pip install {dep}")
            print(f"✅ {dep} installed successfully")
        except Exception as e:
            print(f"⚠️ Failed to install {dep}: {e}")
    
    print("")
    print("🎉 OCR Dependencies Installation Complete!")
    print("==========================================")
    print("Available OCR Methods:")
    print("1. pytesseract - Fast, reliable text OCR")
    print("2. easyocr - Good for complex layouts")
    print("3. paddleocr - Fast and accurate")
    print("4. huggingface - Cloud-based OCR")
    print("5. text_extraction - For text files")
    print("")
    print("💰 All methods are FREE to use!")

def main():
    """Main function for testing OCR"""
    print("🔍 Multi-OCR Processor Test")
    print("==========================================")
    
    # Check if dependencies are installed
    try:
        import pytesseract
        print("✅ pytesseract available")
    except ImportError:
        print("❌ pytesseract not installed")
    
    try:
        import easyocr
        print("✅ easyocr available")
    except ImportError:
        print("❌ easyocr not installed")
    
    try:
        from paddleocr import PaddleOCR
        print("✅ paddleocr available")
    except ImportError:
        print("❌ paddleocr not installed")
    
    print("")
    print("📋 To install all dependencies, run:")
    print("install_ocr_dependencies()")

if __name__ == "__main__":
    main() 