@echo off
REM Install OCR Dependencies for NHAI Demo
REM All dependencies are FREE to use

echo 📦 Installing OCR Dependencies...
echo ==========================================

echo.
echo 🔍 Installing PyTesseract (Fast, reliable OCR)...
py -m pip install pytesseract
if errorlevel 1 (
    echo ⚠️ PyTesseract installation failed, continuing...
) else (
    echo ✅ PyTesseract installed successfully!
)

echo.
echo 🔍 Installing EasyOCR (Complex layouts)...
py -m pip install easyocr
if errorlevel 1 (
    echo ⚠️ EasyOCR installation failed, continuing...
) else (
    echo ✅ EasyOCR installed successfully!
)

echo.
echo 🔍 Installing PaddleOCR (Fastest for large batches)...
py -m pip install paddlepaddle
py -m pip install paddleocr
if errorlevel 1 (
    echo ⚠️ PaddleOCR installation failed, continuing...
) else (
    echo ✅ PaddleOCR installed successfully!
)

echo.
echo 🔍 Installing Pillow (Image processing)...
py -m pip install Pillow
if errorlevel 1 (
    echo ⚠️ Pillow installation failed, continuing...
) else (
    echo ✅ Pillow installed successfully!
)

echo.
echo 🔍 Installing Requests (API calls)...
py -m pip install requests
if errorlevel 1 (
    echo ⚠️ Requests installation failed, continuing...
) else (
    echo ✅ Requests installed successfully!
)

echo.
echo 🎉 OCR Dependencies Installation Complete!
echo ==========================================
echo.
echo 📊 Available OCR Methods:
echo    1. PyTesseract - Fast, reliable text OCR
echo    2. EasyOCR - Good for complex layouts  
echo    3. PaddleOCR - Fastest for large batches
echo    4. HuggingFace - Cloud-based OCR
echo    5. Text Extraction - For text files
echo.
echo 💰 All methods are FREE to use!
echo.
echo 🚀 Ready to run demo:
echo    ragflow_integration/docker_free_demo.bat
echo.
echo ==========================================
pause 