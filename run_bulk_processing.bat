@echo off
REM Bulk Processing Script for 500+ NHAI Documents
REM Processes all documents efficiently with concurrent workers

echo 🚀 Starting Bulk Processing for 500+ NHAI Documents...
echo ==========================================

REM Check if RAGFlow is running
echo 📋 Checking RAGFlow services...
curl -s http://localhost >nul 2>&1
if errorlevel 1 (
    echo ❌ RAGFlow is not running. Please start it first with quick_demo_setup.bat
    pause
    exit /b 1
)
echo ✅ RAGFlow is running!

REM Check if documents exist
if not exist "output\existing_links.json" (
    echo ❌ No documents found. Please run document extraction first.
    pause
    exit /b 1
)

echo 📊 Found existing_links.json - ready to process!

REM Run bulk processing with optimized settings
echo 🤖 Starting bulk processing...
py ragflow_integration/bulk_processor.py --max-documents 500 --batch-size 50 --max-workers 6 --delay 3

echo.
echo 🎉 Bulk processing completed!
echo ==========================================
echo 📊 Check the logs for detailed results:
echo    - ragflow_integration/bulk_processing.log
echo    - ragflow_integration/processing_status/
echo    - ragflow_integration/bulk_processing_report_*.json
echo.
echo 🌐 Access RAGFlow: http://localhost
echo 🔑 Login: admin / nhai_admin_2025
echo ==========================================
pause 