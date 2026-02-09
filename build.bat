@echo off
echo Building PDF to PNG Converter...
pyinstaller --onefile --windowed --name "PDF_to_PNG" --clean --noconfirm run.py
echo Build complete.
pause
