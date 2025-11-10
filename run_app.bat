@echo off
:: ==========================================
::  SCORM Audio Translator - Startup Script
:: ==========================================
title SCORM Audio Translator - Flask Server
color 0A
cd /d "%~dp0"

echo 🔹 Activating virtual environment...
call venv\Scripts\activate

echo 🔹 Starting Flask server...
set FLASK_APP=app.py
set FLASK_ENV=development
python -m flask run --port=5000

echo.
pause
