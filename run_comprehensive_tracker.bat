@echo off
REM Comprehensive NHAI Document Tracker
REM Processes ALL 1620 links and creates detailed Excel tracking

echo 🚀 Comprehensive NHAI Document Tracker
echo ==========================================

REM Step 1: Check Python
echo 📋 Step 1: Checking Python...
py --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.8+
    pause
    exit /b 1
)
echo ✅ Python found!

REM Step 2: Check if extracted_links.txt exists
echo 📊 Step 2: Checking extracted links...
if not exist "data\extracted_links.txt" (
    echo ❌ extracted_links.txt not found in data folder.
    pause
    exit /b 1
)
echo ✅ Found extracted_links.txt!

REM Step 3: Install required packages
echo 📦 Step 3: Installing required packages...
py -m pip install pandas openpyxl requests

REM Step 4: Run comprehensive tracker
echo 🚀 Step 4: Running comprehensive tracker...
echo.
echo 📊 This will process ALL documents from extracted_links.txt
echo 📊 Creating detailed Excel tracking report with ONE main sheet
echo 📊 Progress will be saved automatically
echo.
echo ⚠️  This may take several hours for all 1620 documents
echo ⚠️  You can stop anytime and resume later
echo.
pause

py ragflow_integration/comprehensive_tracker.py

echo.
echo 🎉 Comprehensive tracking completed!
echo ==========================================
echo 📊 Excel Report: ragflow_integration/NHAI_Document_Tracker.xlsx
echo 📊 Progress File: ragflow_integration/processing_progress.json
echo 📊 Downloads: ragflow_integration/downloads/
echo.
echo 📋 Single Excel Sheet Contains:
echo    • sr_no - Serial number
echo    • subject - Document title  
echo    • policy_no - Policy number
echo    • date - Document date
echo    • category - Administration category (ADMINISTRATION, FINANCE, etc.)
echo    • link - Original document link
echo    • status - Processing status (Processed/Failed/Download Failed)
echo    • processed_date - When it was processed
echo    • ocr_method - Which OCR method was used
echo    • content_length - How much content was extracted
echo    • processing_time - Time taken to process
echo    • error_message - Any errors encountered
echo    • filename - Downloaded filename
echo    • file_path - Local file path
echo.
echo 🎯 Features:
echo    • All 1620 documents in ONE sheet
echo    • Administration category as a column
echo    • Processing status for each document
echo    • Content amount processed
echo    • OCR method used
echo    • Latest processing date
echo    • Sorted by date (latest first)
echo.
echo ==========================================
pause 