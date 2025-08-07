@echo off
REM Quick 2-Hour NHAI Demo Setup for Windows
REM Uses existing models - No training required!

echo 🚀 Quick 2-Hour NHAI Demo Setup Starting...
echo ==========================================

REM Step 1: Check if Docker is running
echo 📋 Step 1: Checking Docker...
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not running. Please start Docker Desktop first.
    pause
    exit /b 1
)
echo ✅ Docker is running!

REM Step 2: Install Ollama if not present
echo 📥 Step 2: Installing Ollama...
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

REM Step 3: Start Ollama and download model
echo 🤖 Step 3: Starting Ollama and downloading model...
start /B ollama serve
timeout /t 10 /nobreak >nul
ollama pull llama3.1:8b
echo ✅ Model downloaded!

REM Step 4: Start RAGFlow services
echo 🐳 Step 4: Starting RAGFlow services...
cd /d "%~dp0ragflow\docker"
docker-compose -f docker-compose.yml up -d

echo ⏳ Waiting for services to start...
timeout /t 30 /nobreak >nul

REM Step 5: Test services
echo 🧪 Step 5: Testing services...
curl -s http://localhost:11434/api/tags >nul 2>&1 && echo ✅ Ollama working!
curl -s http://localhost >nul 2>&1 && echo ✅ RAGFlow web interface working!

echo.
echo 🎉 DEMO READY IN UNDER 30 MINUTES!
echo ==========================================
echo 🌐 Web Interface: http://localhost
echo 🔑 Login: admin / nhai_admin_2025
echo 🤖 Ollama Models: http://localhost:11434
echo.
echo 📋 What you can do now:
echo    1. Upload NHAI PDFs via web interface
echo    2. Ask questions about policies
echo    3. Search across documents
echo    4. Get policy summaries
echo.
echo 🔧 To stop: run stop_demo.bat
echo ==========================================
pause 