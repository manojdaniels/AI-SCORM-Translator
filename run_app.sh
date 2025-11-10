#!/bin/bash
# ==========================================
# SCORM Audio Translator - Flask Server
# ==========================================
echo "🔹 Activating virtual environment..."
source venv/bin/activate

echo "🔹 Starting Flask server on port 5000..."
export FLASK_APP=app.py
export FLASK_ENV=development
python -m flask run --port=5000
