@echo off
echo Creating data directory...
mkdir data\extracted_texts 2>nul

echo Copying extracted text files...
xcopy "..\output\extracted_texts\*.json" "data\extracted_texts\" /Y

echo Copying app files...
copy "simple_huggingface_rag.py" "app.py" /Y
copy "requirements.txt" "requirements.txt" /Y
copy "README.md" "README.md" /Y
copy "DEPLOYMENT_GUIDE.md" "DEPLOYMENT_GUIDE.md" /Y

echo Done! Files ready for GitHub upload.
pause
