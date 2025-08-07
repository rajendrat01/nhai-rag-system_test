import os
import subprocess
import sys

def run_command(command):
    """Run a command and return the result"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        print(f"Running: {command}")
        if result.stdout:
            print(f"Output: {result.stdout}")
        if result.stderr:
            print(f"Error: {result.stderr}")
        return result.returncode == 0
    except Exception as e:
        print(f"Error running command: {e}")
        return False

def main():
    print("=== NHAI RAG System - Quick GitHub Upload ===")
    
    # Step 1: Initialize git
    if not run_command("git init"):
        print("Git already initialized or error occurred")
    
    # Step 2: Add all files
    if not run_command("git add ."):
        print("Error adding files")
        return
    
    # Step 3: Commit
    if not run_command('git commit -m "Add NHAI RAG system with extracted documents"'):
        print("Error committing files")
        return
    
    # Step 4: Add remote (you'll need to do this manually)
    print("\n=== MANUAL STEP REQUIRED ===")
    print("Run this command:")
    print("git remote add origin https://github.com/rajendrat01/nhai-rag-system_test.git")
    
    # Step 5: Push (you'll need to do this manually)
    print("\nThen run this command:")
    print("git push -u origin main")
    
    print("\n=== FILES READY FOR UPLOAD ===")
    print("All files have been prepared for GitHub upload!")
    print("Just run the two commands above to complete the upload.")

if __name__ == "__main__":
    main()
