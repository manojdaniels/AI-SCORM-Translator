# 🎧 SCORM Audio Translator — AI-Powered LMS Audio Converter

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Flask](https://img.shields.io/badge/Flask-3.x-green)
![GoogleTranslator](https://img.shields.io/badge/Translation-Deep--Translator-orange)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

> **An intelligent Flask-based system that automatically translates SCORM course narrations into multiple languages — preserving the original course structure and playback through an integrated SCORM player.**

---

## 🧠 Overview

This **Audio-Only Edition** of the SCORM Translator focuses on **speech translation**, converting audio narration within SCORM packages into any selected language.  
It automatically detects launch files using the SCORM `imsmanifest.xml`, supports playback for both original and translated packages, and provides an elegant web interface for uploading, translating, and playing courses.

---

## ✨ Key Features

| Feature | Description |
|----------|--------------|
| 🎧 **AI-Powered Audio Translation** | Converts narration from SCORM courses into any supported language using Google Translator + gTTS |
| 📦 **Automatic Manifest Detection** | Finds and loads SCORM launch files automatically from `imsmanifest.xml` |
| 🌍 **Multi-Language Support** | English, French, Spanish, Hindi, Russian, Arabic, Chinese, Japanese, and more |
| 🖥 **SCORM Player (Local Mode)** | Plays SCORM packages locally with built-in LMS API mock (no LMS server required) |
| ⚙️ **GPU Compatible (CUDA)** | Optional PyTorch support for GPU-accelerated translation pipelines |
| 🗂 **Metadata Persistence** | Keeps track of uploaded, translated, and deleted courses using `metadata.json` |
| 🧰 **User-Friendly Web UI** | Built with Bootstrap 5 for simplicity and responsiveness |

---

## ⚙️ Installation & Setup

### 1️⃣ Clone or Download Repository

```bash
git clone https://github.com/<yourusername>/scorm-audio-translator.git
cd scorm-audio-translator


2️⃣ Create a Virtual Environment
python -m venv venv
venv\Scripts\activate   # (Windows)
# or
source venv/bin/activate  # (Linux/Mac)


3️⃣ Install Dependencies
pip install -r requirements.txt


💡 If you have a GPU (CUDA 12.9), update requirements.txt lines:
torch==2.5.0+cu129
torchaudio==2.5.0+cu129
--extra-index-url https://download.pytorch.org/whl/cu129


🚀 Running the Application
▶ Option 1: Run via Flask
python app.py

▶ Option 2: Use Auto-Launcher
Windows:
run_app.bat

Linux/Mac:
./run_app.sh


💻 How It Works

- Upload a SCORM .zip file via the web interface
- The system extracts and analyzes its structure
- It automatically detects the main launch HTML file from imsmanifest.xml
- You select a target language (e.g., French 🇫🇷, Hindi 🇮🇳, Spanish 🇪🇸)
- The app transcribes audio → translates text → regenerates voice using gTTS
- The translated course becomes playable in the integrated SCORM player


🌐 Supported Languages
| Language   | Code | Language             | Code  |
| ---------- | ---- | -------------------- | ----- |
| English    | en   | Hindi                | hi    |
| French     | fr   | Japanese             | ja    |
| German     | de   | Chinese (Simplified) | zh-cn |
| Spanish    | es   | Korean               | ko    |
| Portuguese | pt   | Russian              | ru    |
| Italian    | it   | Arabic               | ar    |


🧰 Dependencies
| Library           | Purpose                                       |
| ----------------- | --------------------------------------------- |
| Flask             | Web Framework                                 |
| deep-translator   | Google-based translation                      |
| gTTS              | Text-to-Speech engine                         |
| SpeechRecognition | Speech-to-Text (Google API)                   |
| pydub             | Audio format conversion                       |
| torch (optional)  | GPU acceleration (future Whisper integration) |


🧩 Future Enhancements
🧠 Text Translation Integration (AI-assisted for full multilingual SCORM)
🪶 Whisper GPU-based Audio Transcription (offline & faster)
☁️ Cloud Upload/Download support for enterprise LMS sync
🔐 User Authentication / Course Access Control

📜 License
This project is licensed under the MIT License — feel free to use, modify, and distribute it.
MIT License © 2025 Manoj Daniels

🪄 Maintained By
👨‍💻 MD (IT Professional)

End-to-end AI + Web Integrations • SCORM Systems • Translation Automation
📧 For collaboration inquiries — contact available upon request.
