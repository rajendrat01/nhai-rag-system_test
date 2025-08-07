@echo off
REM Stop NHAI RAGFlow Demo Services

echo 🛑 Stopping NHAI RAGFlow Demo Services...
echo ==========================================

REM Navigate to RAGFlow directory
cd /d "%~dp0ragflow\docker"

REM Stop RAGFlow services
echo 🔄 Stopping RAGFlow services...
docker-compose -f docker-compose.yml down

REM Stop Ollama
echo 🔄 Stopping Ollama service...
taskkill /f /im ollama.exe >nul 2>&1

echo ✅ Demo services stopped successfully!
echo ==========================================
pause 