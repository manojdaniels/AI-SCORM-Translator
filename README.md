# 🌐 AI-SCORM Translator  
![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-2.2.2-black?logo=flask)
![AI](https://img.shields.io/badge/AI%20Powered-Translation%20%26%20Speech-green?logo=openai)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Status](https://img.shields.io/badge/Status-Active-success)

> 🎓 **AI-Powered SCORM Translation Engine** — Automatically translate, transcribe, and recreate multilingual SCORM packages with embedded audio and text for global eLearning delivery.

---

## 🚀 Overview

**AI-SCORM Translator** is a powerful Python-based application designed to make eLearning courses **globally accessible**.  
It intelligently processes SCORM packages, translates both **audio narration** and **text content**, and rebuilds the SCORM course in the target language.  

This allows organizations, educators, and training professionals to **instantly localize learning content** without manually editing dozens of files.

---

## 🧠 Key Features

- 🌍 **Global Language Support**  
  Translate SCORM content into any target language using AI-powered translation engines.

- 🎧 **Audio Translation**  
  Detects and converts all embedded audio narrations into the selected language using TTS (Text-to-Speech).

- 📝 **Text Transcription & Translation**  
  Extracts all text content (HTML, JSON, XML, etc.) and translates it contextually.

- 📦 **Automatic SCORM Repackaging**  
  Rebuilds the translated files and regenerates a SCORM-compliant ZIP.

- 🎮 **Inbuilt SCORM Player**  
  Play and preview the translated course directly inside the application.

- 💾 **Downloadable SCORM Package**  
  Instantly export the translated SCORM package for LMS upload or distribution.

---

## 🧰 Tech Stack

| Component | Technology |
|------------|-------------|
| 🧩 Framework | Flask |
| 🧠 AI/ML | OpenAI / Google Translate API / SpeechRecognition |
| 🔊 Audio | gTTS / Whisper / pyttsx3 |
| 📂 File Handling | zipfile, os, tempfile |
| 🌐 Web UI | HTML5, Bootstrap, JavaScript |
| 🗃️ Data | XML, JSON, HTML Parsing |

---

## 🧾 Installation

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/ManojDaniels/AI-SCORM-Translator.git
cd AI-SCORM-Translator
