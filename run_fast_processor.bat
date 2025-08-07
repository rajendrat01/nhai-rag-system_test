@echo off
echo 🚀 FAST DOCUMENT PROCESSOR
echo ==========================
echo.
echo 📄 Processing 10 documents with fast OCR extraction
echo 📊 Using multiple OCR methods for best results
echo.
echo 🎯 Features:
echo    • Fast text extraction (PyPDF2, pdfplumber, PyMuPDF)
echo    • Fast OCR (PaddleOCR) for image-based PDFs
echo    • Downloads documents automatically
echo    • Shows real-time progress
echo    • Creates detailed CSV report
echo.
echo 📁 Output files:
echo    • output/pdfs/ - Downloaded PDF files
echo    • ragflow_integration/processed_documents.csv - Results
echo.
echo ⏱️  Estimated time: 2-5 minutes for 10 documents
echo.
pause

echo.
echo 🚀 Starting fast document processor...
py ragflow_integration/fast_processor.py

echo.
echo 🎉 Processing completed!
echo 📁 Check the results in: ragflow_integration/processed_documents.csv
echo.
pause 