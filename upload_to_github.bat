@echo off
echo ========================================
echo NHAI RAG System - GitHub Upload Script
echo ========================================

echo.
echo Step 1: Initialize Git repository (if not already done)
git init

echo.
echo Step 2: Add all files to Git
git add .

echo.
echo Step 3: Commit the changes
git commit -m "Add NHAI RAG system with extracted documents"

echo.
echo Step 4: Add remote repository (replace with your actual repo URL)
echo Please run this command manually:
echo git remote add origin https://github.com/rajendrat01/nhai-rag-system_test.git

echo.
echo Step 5: Push to GitHub
echo Please run this command manually:
echo git push -u origin main

echo.
echo ========================================
echo Manual steps to complete:
echo 1. git remote add origin https://github.com/rajendrat01/nhai-rag-system_test.git
echo 2. git push -u origin main
echo ========================================

pause
