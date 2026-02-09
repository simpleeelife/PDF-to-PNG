@echo off
python -m pdf_to_png_converter.main
if %errorlevel% neq 0 pause
