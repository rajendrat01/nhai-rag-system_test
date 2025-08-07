@echo off
REM Docker-Free NHAI RAG Demo Setup
REM No Docker required - uses HuggingFace free API

echo 🚀 Docker-Free NHAI RAG Demo Setup
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

REM Step 2: Check if documents exist
echo 📊 Step 2: Checking documents...
if not exist "output\existing_links.json" (
    echo ❌ No documents found. Please run document extraction first.
    echo You can run: py src\extract_specific_circular.py
    pause
    exit /b 1
)

REM Count documents
for /f %%i in ('powershell -Command "(Get-Content 'output\existing_links.json' | ConvertFrom-Json).Count"') do set doc_count=%%i
echo ✅ Found %doc_count% documents ready for processing!

REM Step 3: Run Docker-free setup
echo 🔧 Step 3: Running Docker-free setup...
py ragflow_integration/docker_free_setup.py

REM Step 4: Process documents
echo 📄 Step 4: Processing documents...
py ragflow_integration/docker_free_processor.py

REM Step 5: Open web interface
echo 🌐 Step 5: Opening web interface...
start ragflow_integration/docker_free/web_interface.html

echo.
echo 🎉 Docker-Free Demo Setup Complete!
echo ==========================================
echo 🌐 Web Interface: ragflow_integration/docker_free/web_interface.html
echo 📊 Processing Report: ragflow_integration/docker_free/processing_report.json
echo.
echo 📋 What's available:
echo    ✅ Document processing without Docker
echo    ✅ Search across NHAI policies
echo    ✅ Web interface for demo
echo    ✅ Real-time processing reports
echo.
echo 🎯 Demo Features:
echo    • Show document processing progress
echo    • Demonstrate search capabilities
echo    • Display processing statistics
echo    • Show web interface functionality
echo.
echo 🔧 No Docker required!
echo ==========================================
pause 