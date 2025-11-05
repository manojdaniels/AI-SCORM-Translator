# 🌍 SCORM Audio & Language Translator

A powerful Flask-based web application that translates SCORM e-learning courses including both text content and audio narration into multiple languages.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/flask-3.0+-green.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)

## ✨ Features

### 📝 Text Translation
- Translates JavaScript text strings, titles, labels, and UI elements
- Supports 12+ languages
- Fast processing (5-15 seconds per course)

### 🎙️ Audio Translation (Advanced)
- **Speech-to-Text**: Extracts speech from audio files
- **Translation**: Translates transcribed text
- **Text-to-Speech**: Generates new audio in target language
- Supports MP3, WAV, OGG, M4A, FLAC, AAC formats
- Automatic backup and restoration on failure

### 📚 Course Management
- Upload and organize SCORM packages
- View course library with metadata
- Play courses in embedded browser player
- Download translated packages as ZIP files
- Delete courses and translations

### 🎮 Embedded SCORM Player
- Full-screen course playback
- Responsive design
- Quick navigation between versions
- Download translated packages

## 🚀 Quick Start

### Prerequisites
1. **Python 3.8+**
2. **FFmpeg** (required for audio processing)

### Installation

```bash
# 1. Install FFmpeg
# Windows: choco install ffmpeg
# Mac: brew install ffmpeg
# Linux: sudo apt install ffmpeg

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Verify setup
python test_setup.py

# 4. Run application
python app.py
```

Open **http://localhost:5000** in your browser.

## 📖 Documentation

- **[Quick Start Guide](QUICK_START.md)** - Get up and running in 3 minutes
- **[Setup Instructions](SETUP_INSTRUCTIONS.md)** - Detailed installation guide
- **Test Setup**: Run `python test_setup.py` to verify installation

## 🎯 Usage

### 1. Upload a Course
- Go to homepage
- Click "Browse Files" and select SCORM .zip file
- Click "Upload Course"

### 2. Translate Course

**Text Only (Fast):**
- Select language from dropdown
- Uncheck "Translate audio files"
- Click "Translate Course"
- ⏱️ ~5-10 seconds

**Text + Audio (Complete):**
- Select language from dropdown
- Check "Translate audio files"
- Click "Translate Course"
- ⏱️ Several minutes (depends on audio count)

### 3. Play & Download
- Click "Play" to view in browser
- Click "Download" to get translated ZIP package

## 🌍 Supported Languages

| Language   | Code  | Text | Audio |
|------------|-------|------|-------|
| English    | en    | ✅   | ✅    |
| French     | fr    | ✅   | ✅    |
| German     | de    | ✅   | ✅    |
| Spanish    | es    | ✅   | ✅    |
| Italian    | it    | ✅   | ✅    |
| Portuguese | pt    | ✅   | ✅    |
| Hindi      | hi    | ✅   | ✅    |
| Russian    | ru    | ✅   | ✅    |
| Japanese   | ja    | ✅   | ✅    |
| Chinese    | zh-cn | ✅   | ✅    |
| Korean     | ko    | ✅   | ✅    |
| Arabic     | ar    | ✅   | ✅    |

## 🏗️ Architecture

```
┌─────────────────┐
│  Flask Web App  │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼───┐ ┌──▼───────┐
│ Text  │ │  Audio   │
│Trans- │ │  Trans-  │
│lation │ │  lation  │
└───┬───┘ └──┬───────┘
    │        │
    │   ┌────▼────┐
    │   │Speech-  │
    │   │to-Text  │
    │   └────┬────┘
    │        │
    │   ┌────▼────┐
    │   │Translate│
    │   └────┬────┘
    │        │
    │   ┌────▼────┐
    │   │Text-to- │
    │   │Speech   │
    │   └────┬────┘
    │        │
    └────┬───┴────┘
         │
    ┌────▼────────┐
    │ Translated  │
    │    SCORM    │
    └─────────────┘
```

## 📂 Project Structure

```
scorm-translator/
│
├── app.py                      # Main Flask application
├── requirements.txt            # Python dependencies
├── test_setup.py              # Setup verification script
├── README.md                  # This file
├── QUICK_START.md             # Quick start guide
├── SETUP_INSTRUCTIONS.md      # Detailed setup
│
├── templates/
│   ├── index.html             # Upload page
│   ├── library.html           # Course library
│   └── player.html            # SCORM player
│
├── static/
│   ├── scorm/                 # Original courses
│   └── scorm_translated/      # Translated courses
│
├── uploads/                   # Temporary uploads
├── zips/                      # Downloadable packages
├── temp_audio/                # Audio processing temp files
└── metadata.json              # Course metadata (auto-generated)
```

## 🔧 Configuration

### Change Port
In `app.py`:
```python
app.run(debug=True, port=8080)  # Change 5000 to desired port
```

### Change Secret Key (Important!)
In `app.py`:
```python
app.secret_key = "your-secure-random-key-here"
```

### Production Mode
```python
app.run(debug=False, host='0.0.0.0', port=5000)
```

## 📊 Performance

| Course Size | Text Translation | Audio (5 files) | Audio (20 files) |
|-------------|------------------|-----------------|------------------|
| Small       | 5 sec            | 2-3 min         | 8-12 min         |
| Medium      | 10 sec           | 3-5 min         | 15-25 min        |
| Large       | 15 sec           | 5-10 min        | 30-60 min        |

## ⚠️ Limitations

- **Internet Required**: Translation services need active connection
- **Audio Quality**: Better source audio = better translation
- **Processing Time**: Large courses with many audio files take longer
- **File Size**: Each translation creates a full copy of the course
- **Free Tier**: Uses free Google services (reasonable usage limits)

## 🔍 Troubleshooting

### FFmpeg Not Found
```bash
# Check if installed
ffmpeg -version

# Install if missing
# Windows: choco install ffmpeg
# Mac: brew install ffmpeg  
# Linux: sudo apt install ffmpeg
```

### Audio Translation Fails
- Ensure audio contains clear speech
- Check internet connection
- Verify FFmpeg is properly installed
- Try with simpler audio files first

### Module Not Found
```bash
pip install -r requirements.txt --upgrade
```

### Port Already in Use
```bash
# Change port in app.py or kill existing process
# Windows: taskkill /PID <PID> /F
# Mac/Linux: kill -9 <PID>
```

## 🛡️ Security Notes

For production deployment:
- ✅ Change the secret key
- ✅ Enable HTTPS
- ✅ Add authentication
- ✅ Implement file size limits
- ✅ Sanitize file names
- ✅ Add rate limiting
- ✅ Use environment variables

## 🤝 Contributing

Contributions are welcome! Areas for improvement:
- Additional language support
- Better audio quality algorithms
- Batch processing
- Progress bars for long translations
- User authentication
- Cloud storage integration

## 📝 Dependencies

- **Flask**: Web framework
- **deep-translator**: Google Translate API wrapper
- **gTTS**: Google Text-to-Speech
- **SpeechRecognition**: Speech-to-text conversion
- **pydub**: Audio file processing
- **FFmpeg**: Audio encoding/decoding (external)

## 📄 License

MIT License - feel free to use in your projects!

## 🙏 Acknowledgments

- Google Translate API (via deep-translator)
- Google Speech Recognition
- Google Text-to-Speech (gTTS)
- FFmpeg project
- Flask framework

## 📞 Support

Having issues? 
1. Run `python test_setup.py` to diagnose problems
2. Check [SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md) for detailed help
3. Review [QUICK_START.md](QUICK_START.md) for common solutions
4. Check console output for error messages

## 🗺️ Roadmap

- [ ] Progress bars for translations
- [ ] Batch upload multiple courses
- [ ] User authentication system
- [ ] Cloud storage support (S3, Azure)
- [ ] Advanced audio quality options
- [ ] Translation memory/caching
- [ ] REST API for automation
- [ ] Docker containerization
- [ ] Multi-language UI


