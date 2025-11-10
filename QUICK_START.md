<<<<<<< HEAD
# 🚀 Quick Start Guide - SCORM Audio Translator

## ⚡ 3-Minute Setup

### 1️⃣ Install FFmpeg (REQUIRED)
**Windows:** Download from https://ffmpeg.org or run:
```bash
choco install ffmpeg
```

**Mac:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt install ffmpeg
```

### 2️⃣ Install Python Packages
```bash
pip install -r requirements.txt
```

### 3️⃣ Run the App
```bash
python app.py
```

Open: **http://localhost:5000**

---

## 🎯 How to Use

### Upload a Course
1. Go to homepage
2. Click "Browse Files"
3. Select SCORM .zip file
4. Click "Upload Course"

### Translate Text Only (Fast)
1. Go to "My Courses"
2. Select language from dropdown
3. **UNCHECK** "Translate audio files"
4. Click "Translate Course"
5. Wait ~5-10 seconds
6. Click "Play" to view

### Translate Text + Audio (Slower)
1. Go to "My Courses"
2. Select language from dropdown
3. **CHECK** "Translate audio files"
4. Click "Translate Course"
5. Wait (time depends on audio count)
6. Click "Play" to view

---

## 📊 What Gets Translated

### ✅ Text Translation (Always)
- JavaScript text strings
- Titles and labels
- Alt text
- UI elements

### 🎙️ Audio Translation (Optional)
- MP3, WAV, OGG, M4A files
- Voiceover narrations
- Audio instructions
- Sound effects with speech

---

## ⏱️ Processing Time Examples

| Course Type | Text Only | Text + Audio (5 files) | Text + Audio (20 files) |
|-------------|-----------|------------------------|-------------------------|
| Small       | 5 sec     | 2-3 min               | 8-12 min               |
| Medium      | 10 sec    | 3-5 min               | 15-25 min              |
| Large       | 15 sec    | 5-10 min              | 30-60 min              |

---

## 🌍 Supported Languages

**Text Translation:** All languages supported by Google Translate

**Audio Translation (with gTTS):**
- English, French, German, Spanish, Italian
- Portuguese, Russian, Japanese, Chinese
- Hindi, Korean, Arabic

---

## ❌ Common Errors & Fixes

### "FFmpeg not found"
```bash
# Install FFmpeg (see step 1 above)
# Then restart your terminal
ffmpeg -version  # Should show version info
```

### "Could not transcribe audio"
- **Fix:** Ensure audio has clear speech, not just music/sounds
- **Fix:** Check internet connection (required for speech recognition)
- **Fix:** Try with a different audio file first

### "ModuleNotFoundError"
```bash
pip install -r requirements.txt --upgrade
```

### Port 5000 in use
```python
# In app.py, change last line to:
app.run(debug=True, port=8080)
```

---

## 💡 Pro Tips

1. **Test First**: Start with a small course (1-2 audio files)
2. **Monitor Progress**: Watch the terminal/console for status
3. **Text-Only Fast**: Skip audio translation for quick previews
4. **Backup**: Keep original SCORM files safe
5. **Clear Audio**: Better audio quality = better translation

---

## 🎬 Typical Workflow

```
1. Upload SCORM → 2. View in Library → 3. Translate (text/audio)
                                                ↓
                                          4. Play in browser
                                                ↓
                                          5. Download ZIP
```

---

## 📂 File Structure After Upload

```
static/
  scorm/
    mycourse-abc123/              ← Original course
  scorm_translated/
    mycourse-abc123_fr/           ← French translation
    mycourse-abc123_es/           ← Spanish translation

zips/
  mycourse-abc123_fr.zip          ← Downloadable packages
  mycourse-abc123_es.zip
```

---

## 🔍 Checking Translation Progress

Watch your terminal/console for real-time updates:

```
Processing audio: narration_01.mp3
  - Transcribed: Hello and welcome to this course...
  - Translated: Bonjour et bienvenue dans ce cours...
  ✓ Successfully translated audio

Processing audio: narration_02.mp3
  - Transcribed: In this lesson you will learn...
  - Translated: Dans cette leçon vous apprendrez...
  ✓ Successfully translated audio
```

---

## 🆘 Need Help?

1. **Check FFmpeg**: `ffmpeg -version`
2. **Check Dependencies**: `pip list | grep -E "flask|gtts|speech"`
3. **Check Logs**: Watch terminal output during translation
4. **Test Simple First**: Upload a small course without audio

---

## 🎉 Success Indicators

- ✅ FFmpeg version displays
- ✅ Flask starts without errors
- ✅ Upload page loads at localhost:5000
- ✅ Can upload and view original course
- ✅ Text translation completes in seconds
- ✅ Audio translation shows progress in terminal
- ✅ Can play translated course in browser
- ✅ Can download translated ZIP

---

## 🔗 Important URLs

- **Upload**: http://localhost:5000/
- **Library**: http://localhost:5000/library
- **FFmpeg**: https://ffmpeg.org/download.html

---

## 📱 Browser Compatibility

✅ **Works Best In:**
- Chrome / Edge (Recommended)
- Firefox
- Safari

---

## 💾 Storage Requirements

**Per Course:**
- Original: ~50-200 MB (depends on media)
- Each Translation: Same size as original
- Recommended: 5-10 GB free space for multiple courses

---

## 🔄 Updating

```bash
# Update all dependencies
pip install --upgrade -r requirements.txt

# Or update individually
pip install --upgrade flask
pip install --upgrade gtts
pip install --upgrade SpeechRecognition
```

---

=======
# 🚀 Quick Start Guide - SCORM Audio Translator

## ⚡ 3-Minute Setup

### 1️⃣ Install FFmpeg (REQUIRED)
**Windows:** Download from https://ffmpeg.org or run:
```bash
choco install ffmpeg
```

**Mac:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt install ffmpeg
```

### 2️⃣ Install Python Packages
```bash
pip install -r requirements.txt
```

### 3️⃣ Run the App
```bash
python app.py
```

Open: **http://localhost:5000**

---

## 🎯 How to Use

### Upload a Course
1. Go to homepage
2. Click "Browse Files"
3. Select SCORM .zip file
4. Click "Upload Course"

### Translate Text Only (Fast)
1. Go to "My Courses"
2. Select language from dropdown
3. **UNCHECK** "Translate audio files"
4. Click "Translate Course"
5. Wait ~5-10 seconds
6. Click "Play" to view

### Translate Text + Audio (Slower)
1. Go to "My Courses"
2. Select language from dropdown
3. **CHECK** "Translate audio files"
4. Click "Translate Course"
5. Wait (time depends on audio count)
6. Click "Play" to view

---

## 📊 What Gets Translated

### ✅ Text Translation (Always)
- JavaScript text strings
- Titles and labels
- Alt text
- UI elements

### 🎙️ Audio Translation (Optional)
- MP3, WAV, OGG, M4A files
- Voiceover narrations
- Audio instructions
- Sound effects with speech

---

## ⏱️ Processing Time Examples

| Course Type | Text Only | Text + Audio (5 files) | Text + Audio (20 files) |
|-------------|-----------|------------------------|-------------------------|
| Small       | 5 sec     | 2-3 min               | 8-12 min               |
| Medium      | 10 sec    | 3-5 min               | 15-25 min              |
| Large       | 15 sec    | 5-10 min              | 30-60 min              |

---

## 🌍 Supported Languages

**Text Translation:** All languages supported by Google Translate

**Audio Translation (with gTTS):**
- English, French, German, Spanish, Italian
- Portuguese, Russian, Japanese, Chinese
- Hindi, Korean, Arabic

---

## ❌ Common Errors & Fixes

### "FFmpeg not found"
```bash
# Install FFmpeg (see step 1 above)
# Then restart your terminal
ffmpeg -version  # Should show version info
```

### "Could not transcribe audio"
- **Fix:** Ensure audio has clear speech, not just music/sounds
- **Fix:** Check internet connection (required for speech recognition)
- **Fix:** Try with a different audio file first

### "ModuleNotFoundError"
```bash
pip install -r requirements.txt --upgrade
```

### Port 5000 in use
```python
# In app.py, change last line to:
app.run(debug=True, port=8080)
```

---

## 💡 Pro Tips

1. **Test First**: Start with a small course (1-2 audio files)
2. **Monitor Progress**: Watch the terminal/console for status
3. **Text-Only Fast**: Skip audio translation for quick previews
4. **Backup**: Keep original SCORM files safe
5. **Clear Audio**: Better audio quality = better translation

---

## 🎬 Typical Workflow

```
1. Upload SCORM → 2. View in Library → 3. Translate (text/audio)
                                                ↓
                                          4. Play in browser
                                                ↓
                                          5. Download ZIP
```

---

## 📂 File Structure After Upload

```
static/
  scorm/
    mycourse-abc123/              ← Original course
  scorm_translated/
    mycourse-abc123_fr/           ← French translation
    mycourse-abc123_es/           ← Spanish translation

zips/
  mycourse-abc123_fr.zip          ← Downloadable packages
  mycourse-abc123_es.zip
```

---

## 🔍 Checking Translation Progress

Watch your terminal/console for real-time updates:

```
Processing audio: narration_01.mp3
  - Transcribed: Hello and welcome to this course...
  - Translated: Bonjour et bienvenue dans ce cours...
  ✓ Successfully translated audio

Processing audio: narration_02.mp3
  - Transcribed: In this lesson you will learn...
  - Translated: Dans cette leçon vous apprendrez...
  ✓ Successfully translated audio
```

---

## 🆘 Need Help?

1. **Check FFmpeg**: `ffmpeg -version`
2. **Check Dependencies**: `pip list | grep -E "flask|gtts|speech"`
3. **Check Logs**: Watch terminal output during translation
4. **Test Simple First**: Upload a small course without audio

---

## 🎉 Success Indicators

- ✅ FFmpeg version displays
- ✅ Flask starts without errors
- ✅ Upload page loads at localhost:5000
- ✅ Can upload and view original course
- ✅ Text translation completes in seconds
- ✅ Audio translation shows progress in terminal
- ✅ Can play translated course in browser
- ✅ Can download translated ZIP

---

## 🔗 Important URLs

- **Upload**: http://localhost:5000/
- **Library**: http://localhost:5000/library
- **FFmpeg**: https://ffmpeg.org/download.html

---

## 📱 Browser Compatibility

✅ **Works Best In:**
- Chrome / Edge (Recommended)
- Firefox
- Safari

---

## 💾 Storage Requirements

**Per Course:**
- Original: ~50-200 MB (depends on media)
- Each Translation: Same size as original
- Recommended: 5-10 GB free space for multiple courses

---

## 🔄 Updating

```bash
# Update all dependencies
pip install --upgrade -r requirements.txt

# Or update individually
pip install --upgrade flask
pip install --upgrade gtts
pip install --upgrade SpeechRecognition
```

---

>>>>>>> 0b1e9e43 (SCORM Audio Translation)
**That's it! You're ready to translate SCORM courses! 🎓✨**