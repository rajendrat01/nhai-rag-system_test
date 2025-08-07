import shutil
import os
from pathlib import Path

def copy_extracted_files():
    """Copy all extracted text files to the GitHub repository structure"""
    
    # Source directory (current extracted texts)
    source_dir = Path("../output/extracted_texts")
    
    # Destination directory (GitHub repo structure)
    dest_dir = Path("data/extracted_texts")
    
    # Create destination directory if it doesn't exist
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy all JSON files
    json_files = list(source_dir.glob("*.json"))
    
    print(f"Found {len(json_files)} JSON files to copy...")
    
    copied_count = 0
    for json_file in json_files:
        try:
            shutil.copy2(json_file, dest_dir / json_file.name)
            copied_count += 1
            if copied_count % 10 == 0:
                print(f"Copied {copied_count} files...")
        except Exception as e:
            print(f"Error copying {json_file.name}: {e}")
    
    print(f"Successfully copied {copied_count} files to {dest_dir}")
    
    # Also copy the main app files
    files_to_copy = [
        ("simple_huggingface_rag.py", "app.py"),
        ("requirements.txt", "requirements.txt"),
        ("README.md", "README.md"),
        ("DEPLOYMENT_GUIDE.md", "DEPLOYMENT_GUIDE.md")
    ]
    
    for src, dest in files_to_copy:
        try:
            shutil.copy2(src, dest)
            print(f"Copied {src} to {dest}")
        except Exception as e:
            print(f"Error copying {src}: {e}")

if __name__ == "__main__":
    copy_extracted_files()
