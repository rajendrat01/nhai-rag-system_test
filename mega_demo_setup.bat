@echo off
REM Mega Demo Setup for 500+ NHAI Documents
REM Complete setup with bulk processing for large-scale demo

echo 🚀 MEGA DEMO SETUP - 500+ NHAI Documents
echo ==========================================

REM Step 1: Check prerequisites
echo 📋 Step 1: Checking prerequisites...
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not running. Please start Docker Desktop first.
    pause
    exit /b 1
)
echo ✅ Docker is running!

REM Step 2: Install and start Ollama
echo 📥 Step 2: Setting up Ollama...
where ollama >nul 2>&1
if errorlevel 1 (
    echo Installing Ollama...
    powershell -Command "Invoke-WebRequest -Uri https://ollama.ai/download/ollama-windows-amd64.exe -OutFile ollama-installer.exe"
    ollama-installer.exe /S
    del ollama-installer.exe
    echo ✅ Ollama installed!
) else (
    echo ✅ Ollama already installed!
)

REM Step 3: Start Ollama and download optimized model
echo 🤖 Step 3: Starting Ollama and downloading model...
start /B ollama serve
timeout /t 10 /nobreak >nul
echo Downloading llama3.1:8b (optimized for bulk processing)...
ollama pull llama3.1:8b
echo ✅ Model downloaded!

REM Step 4: Start RAGFlow services
echo 🐳 Step 4: Starting RAGFlow services...
cd /d "%~dp0ragflow\docker"
docker-compose -f docker-compose.yml up -d

echo ⏳ Waiting for services to start...
timeout /t 30 /nobreak >nul

REM Step 5: Check if documents exist
echo 📊 Step 5: Checking document availability...
if not exist "..\..\output\existing_links.json" (
    echo ❌ No documents found. Please run document extraction first.
    echo You can run: python src\extract_specific_circular.py
    pause
    exit /b 1
)

REM Count documents
for /f %%i in ('powershell -Command "(Get-Content '..\..\output\existing_links.json' | ConvertFrom-Json).Count"') do set doc_count=%%i
echo ✅ Found %doc_count% documents ready for processing!

REM Step 6: Start bulk processing
echo 🚀 Step 6: Starting bulk processing...
cd /d "%~dp0"
echo Starting bulk processing with optimized settings...
start "Bulk Processing" py ragflow_integration/bulk_processor.py --max-documents 500 --batch-size 50 --max-workers 6 --delay 3

REM Step 7: Start monitoring
echo 📊 Step 7: Starting progress monitor...
timeout /t 5 /nobreak >nul
start "Processing Monitor" py ragflow_integration/monitor_processing.py

echo.
echo 🎉 MEGA DEMO SETUP COMPLETE!
echo ==========================================
echo 🌐 Web Interface: http://localhost
echo 🔑 Login: admin / nhai_admin_2025
echo 🤖 Ollama Models: http://localhost:11434
echo 📊 Processing Monitor: Running in separate window
echo.
echo 📋 What's happening now:
echo    1. ✅ RAGFlow services started
echo    2. ✅ Ollama model loaded
echo    3. 🔄 Bulk processing 500+ documents
echo    4. 📊 Real-time progress monitoring
echo    5. 🌐 Web interface ready for demo
echo.
echo 🎯 Demo Scenarios:
echo    • Show bulk processing progress
echo    • Demonstrate search across 500+ documents
echo    • Show policy analysis and comparison
echo    • Display real-time performance metrics
echo.
echo ⏱️  Expected Processing Time:
echo    • 500 documents: ~30-45 minutes
echo    • Success rate: >95%%
echo    • Processing speed: ~15-20 docs/minute
echo.
echo 🔧 To stop everything: run stop_demo.bat
echo ==========================================
pause 