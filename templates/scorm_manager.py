<<<<<<< HEAD
import os
import shutil
import zipfile
import uuid
import json
import re
from pathlib import Path
from datetime import datetime
from flask import (
    Flask, render_template, request, redirect, url_for,
    flash, send_file, jsonify
)
from deep_translator import GoogleTranslator
from gtts import gTTS
import speech_recognition as sr
from pydub import AudioSegment
import tempfile

# ── app & folders ───────────────────────────────────────
app = Flask(__name__)
app.secret_key = "change‑me"

BASE             = Path(__file__).parent
UPLOADS          = BASE / "uploads"
SCORM_SRC        = BASE / "static" / "scorm"
SCORM_TRANSLATED = BASE / "static" / "scorm_translated"
ZIPS             = BASE / "zips"
METADATA         = BASE / "metadata.json"
TEMP_AUDIO       = BASE / "temp_audio"

for p in (UPLOADS, SCORM_SRC, SCORM_TRANSLATED, ZIPS, TEMP_AUDIO):
    p.mkdir(parents=True, exist_ok=True)

# ── translation util ───────────────────────────────────
LANGS = {
    "English": "en", "French": "fr", "German": "de",
    "Hindi": "hi",   "Russian": "ru", "Japanese": "ja",
    "Chinese": "zh-cn", "Spanish": "es", "Italian": "it",
    "Portuguese": "pt", "Korean": "ko", "Arabic": "ar"
}

# gTTS language codes (slightly different from translator codes)
GTTS_LANGS = {
    "en": "en", "fr": "fr", "de": "de", "hi": "hi", 
    "ru": "ru", "ja": "ja", "zh-cn": "zh-cn", "es": "es",
    "it": "it", "pt": "pt", "ko": "ko", "ar": "ar"
}

translate = lambda txt, tgt: GoogleTranslator(source="auto", target=tgt).translate(txt)

# keys inside Storyline random js
PATTERNS = [
    re.compile(r'("altText"\s*:\s*")(.*?)(")'),
    re.compile(r'("title"\s*:\s*")(.*?)(")'),
    re.compile(r'(\{"text"\s*:\s*")(.*?)(")')
]
EXCLUDED = {"data.js", "frame.js", "paths.js"}

# Supported audio formats
AUDIO_EXTENSIONS = {'.mp3', '.wav', '.ogg', '.m4a', '.flac', '.aac'}

# ── metadata management ────────────────────────────────

def load_metadata():
    if METADATA.exists():
        try:
            with open(METADATA, 'r') as f:
                content = f.read().strip()
                if content:
                    return json.loads(content)
                else:
                    return {}
        except (json.JSONDecodeError, ValueError):
            # If file is corrupted, backup and start fresh
            if METADATA.exists():
                backup = METADATA.with_suffix('.json.backup')
                shutil.copy2(METADATA, backup)
                print(f"Warning: Corrupted metadata.json backed up to {backup}")
            return {}
    return {}

def save_metadata(data):
    try:
        with open(METADATA, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Error saving metadata: {e}")
        # Try to save to a backup location
        backup = METADATA.with_suffix('.json.emergency')
        try:
            with open(backup, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"Metadata saved to emergency backup: {backup}")
        except:
            pass

def add_course_metadata(pkg_id, filename, original_name):
    meta = load_metadata()
    if pkg_id not in meta:
        meta[pkg_id] = {
            'id': pkg_id,
            'original_name': original_name,
            'filename': filename,
            'uploaded_at': datetime.now().isoformat(),
            'translations': {}
        }
        save_metadata(meta)
    return meta[pkg_id]

def add_translation_metadata(pkg_id, lang_code, lang_name, audio_count=0):
    meta = load_metadata()
    if pkg_id in meta:
        meta[pkg_id]['translations'][lang_code] = {
            'language': lang_name,
            'created_at': datetime.now().isoformat(),
            'zip_file': f"{pkg_id}_{lang_code}.zip",
            'audio_files_translated': audio_count
        }
        save_metadata(meta)

# ── audio translation functions ────────────────────────

def transcribe_audio(audio_path: Path) -> str:
    """Convert audio to text using speech recognition"""
    recognizer = sr.Recognizer()
    
    # Convert to WAV if needed
    temp_wav = TEMP_AUDIO / f"temp_{uuid.uuid4().hex}.wav"
    try:
        audio = AudioSegment.from_file(str(audio_path))
        audio.export(str(temp_wav), format="wav")
        
        with sr.AudioFile(str(temp_wav)) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)
            return text
    except Exception as e:
        print(f"Error transcribing {audio_path.name}: {e}")
        return ""
    finally:
        if temp_wav.exists():
            temp_wav.unlink()

def text_to_speech(text: str, lang_code: str, output_path: Path):
    """Convert text to speech in target language"""
    try:
        gtts_lang = GTTS_LANGS.get(lang_code, "en")
        tts = gTTS(text=text, lang=gtts_lang, slow=False)
        tts.save(str(output_path))
        return True
    except Exception as e:
        print(f"Error generating speech: {e}")
        return False

def translate_audio_file(audio_path: Path, target_lang: str, output_path: Path) -> bool:
    """
    Complete audio translation pipeline:
    1. Transcribe audio to text
    2. Translate text
    3. Convert translated text to speech
    """
    try:
        print(f"Processing audio: {audio_path.name}")
        
        # Step 1: Transcribe
        original_text = transcribe_audio(audio_path)
        if not original_text:
            print(f"  - Could not transcribe audio")
            return False
        
        print(f"  - Transcribed: {original_text[:50]}...")
        
        # Step 2: Translate
        translated_text = translate(original_text, target_lang)
        print(f"  - Translated: {translated_text[:50]}...")
        
        # Step 3: Generate speech
        success = text_to_speech(translated_text, target_lang, output_path)
        
        if success:
            print(f"  ✓ Successfully translated audio")
        
        return success
        
    except Exception as e:
        print(f"Error translating audio {audio_path.name}: {e}")
        return False

def find_audio_files(directory: Path) -> list:
    """Find all audio files in directory recursively"""
    audio_files = []
    for ext in AUDIO_EXTENSIONS:
        audio_files.extend(directory.rglob(f"*{ext}"))
    return audio_files

# ── core functions ─────────────────────────────────────

def extract_zip(src: Path, dest: Path):
    with zipfile.ZipFile(src) as z: 
        z.extractall(dest)

def zip_dir(src_dir: Path, zip_path: Path):
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for p in src_dir.rglob("*"):
            if p.is_file():
                z.write(p, p.relative_to(src_dir))

def translate_storyline_js(js_path: Path, lang_code: str):
    if js_path.name in EXCLUDED: 
        return
    text = js_path.read_text("utf-8", errors="ignore")

    def do(match):
        src = match.group(2)
        try:
            tgt = translate(src, lang_code) or src
        except Exception:
            tgt = src
        return match.group(1) + tgt + match.group(3)

    for pat in PATTERNS:
        text = pat.sub(do, text)

    js_path.write_text(text, "utf-8")

# ── routes ─────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html", languages=LANGS.keys())

@app.route("/library")
def library():
    meta = load_metadata()
    courses = []
    for pkg_id, info in meta.items():
        course_data = {
            'id': pkg_id,
            'name': info.get('original_name', 'Unknown'),
            'uploaded_at': info.get('uploaded_at', ''),
            'translations': info.get('translations', {})
        }
        courses.append(course_data)
    
    # Sort by upload date, newest first
    courses.sort(key=lambda x: x['uploaded_at'], reverse=True)
    
    return render_template("library.html", courses=courses, languages=LANGS)

@app.route("/upload", methods=["POST"])
def upload():
    if 'scormZip' not in request.files:
        flash("File field name must be 'scormZip'.", "error")
        return redirect("/")

    file = request.files['scormZip']
    
    if not file.filename or not file.filename.lower().endswith(".zip"):
        flash("Upload a .zip file.", "error")
        return redirect("/")

    # Create unique package ID
    original_name = Path(file.filename).stem
    pkg_id = f"{original_name}-{uuid.uuid4().hex[:5]}"
    src_dir = SCORM_SRC / pkg_id
    src_dir.mkdir(parents=True)

    # Save and extract
    zip_path = src_dir / "course.zip"
    file.save(zip_path)
    extract_zip(zip_path, src_dir)
    
    # Save metadata
    add_course_metadata(pkg_id, file.filename, original_name)
    
    flash(f"Successfully uploaded: {original_name}", "success")
    return redirect(url_for("library"))

@app.route("/translate/<pkg_id>", methods=["POST"])
def translate_course(pkg_id):
    target_lang = request.form.get("language", "fr")
    translate_audio = request.form.get("translate_audio") == "on"
    lang_name = [k for k, v in LANGS.items() if v == target_lang][0]
    
    src_dir = SCORM_SRC / pkg_id
    if not src_dir.exists():
        flash("Course not found.", "error")
        return redirect(url_for("library"))
    
    # Check if translation already exists
    tgt_dir = SCORM_TRANSLATED / f"{pkg_id}_{target_lang}"
    if tgt_dir.exists():
        flash(f"Translation to {lang_name} already exists.", "info")
        return redirect(url_for("play", pkg=pkg_id, lang=target_lang))
    
    # Copy source to target
    shutil.copytree(src_dir, tgt_dir, dirs_exist_ok=True)
    
    # Translate JavaScript text
    js_root = tgt_dir / "html5" / "data" / "js"
    if js_root.exists():
        for js in js_root.glob("*.js"):
            translate_storyline_js(js, target_lang)
    
    # Translate audio files if requested
    audio_count = 0
    if translate_audio:
        audio_files = find_audio_files(tgt_dir)
        total_audio = len(audio_files)
        
        if total_audio > 0:
            flash(f"Found {total_audio} audio files. Starting translation...", "info")
            
            for i, audio_file in enumerate(audio_files, 1):
                print(f"\nTranslating audio {i}/{total_audio}: {audio_file.name}")
                
                # Create output path (same location, same name)
                output_path = audio_file
                
                # Backup original
                backup_path = audio_file.with_suffix(audio_file.suffix + '.original')
                shutil.copy2(audio_file, backup_path)
                
                # Translate
                success = translate_audio_file(audio_file, target_lang, output_path)
                
                if success:
                    audio_count += 1
                    # Remove backup
                    backup_path.unlink()
                else:
                    # Restore from backup if translation failed
                    shutil.copy2(backup_path, audio_file)
                    backup_path.unlink()
    
    # Create zip
    out_zip = ZIPS / f"{pkg_id}_{target_lang}.zip"
    zip_dir(tgt_dir, out_zip)
    
    # Update metadata
    add_translation_metadata(pkg_id, target_lang, lang_name, audio_count)
    
    if translate_audio and audio_count > 0:
        flash(f"Successfully translated to {lang_name}! Translated {audio_count} audio files.", "success")
    else:
        flash(f"Successfully translated text to {lang_name}!", "success")
    
    return redirect(url_for("play", pkg=pkg_id, lang=target_lang))

@app.route("/play")
def play():
    pkg = request.args.get("pkg")
    lang = request.args.get("lang", "en")
    
    if not pkg:
        flash("No course specified.", "error")
        return redirect(url_for("library"))
    
    folder = SCORM_TRANSLATED / f"{pkg}_{lang}" if lang != "en" else SCORM_SRC / pkg
    
    # Try different launch file names
    launch_files = ["index_lms.html", "index.html", "story.html"]
    launch = None
    for launch_name in launch_files:
        potential_launch = folder / launch_name
        if potential_launch.exists():
            launch = potential_launch
            break
    
    if not launch:
        flash(f"Launch file not found for course: {pkg}", "error")
        return redirect(url_for("library"))
    
    course_url = f"/static/{launch.relative_to(BASE / 'static')}"
    zip_name = f"{pkg}_{lang}.zip" if lang != "en" else None
    
    # Get course metadata
    meta = load_metadata()
    course_info = meta.get(pkg, {})
    
    return render_template("player.html", 
                         course_url=course_url,
                         pkg=pkg, 
                         lang=lang, 
                         zip_name=zip_name, 
                         languages=LANGS,
                         course_info=course_info)

@app.route('/download/<zipname>')
def download(zipname):
    zip_path = ZIPS / zipname
    if not zip_path.exists():
        flash("Download file not found.", "error")
        return redirect(url_for("library"))
    return send_file(zip_path, as_attachment=True)

@app.route('/delete/<pkg_id>', methods=['POST'])
def delete_course(pkg_id):
    # Delete source folder
    src_dir = SCORM_SRC / pkg_id
    if src_dir.exists():
        shutil.rmtree(src_dir)
    
    # Delete all translations
    for trans_dir in SCORM_TRANSLATED.glob(f"{pkg_id}_*"):
        shutil.rmtree(trans_dir)
    
    # Delete zip files
    for zip_file in ZIPS.glob(f"{pkg_id}_*.zip"):
        zip_file.unlink()
    
    # Update metadata
    meta = load_metadata()
    if pkg_id in meta:
        del meta[pkg_id]
        save_metadata(meta)
    
    flash("Course deleted successfully.", "success")
    return redirect(url_for("library"))

# ajax translate node
@app.route('/translate-node', methods=['POST'])
def translate_node():
    d = request.get_json(force=True)
    txt = d.get('text', '')
    tgt = d.get('target', 'fr')
    return jsonify({'t': translate(txt, tgt)})

if __name__ == '__main__':
=======
import os
import shutil
import zipfile
import uuid
import json
import re
from pathlib import Path
from datetime import datetime
from flask import (
    Flask, render_template, request, redirect, url_for,
    flash, send_file, jsonify
)
from deep_translator import GoogleTranslator
from gtts import gTTS
import speech_recognition as sr
from pydub import AudioSegment
import tempfile

# ── app & folders ───────────────────────────────────────
app = Flask(__name__)
app.secret_key = "change‑me"

BASE             = Path(__file__).parent
UPLOADS          = BASE / "uploads"
SCORM_SRC        = BASE / "static" / "scorm"
SCORM_TRANSLATED = BASE / "static" / "scorm_translated"
ZIPS             = BASE / "zips"
METADATA         = BASE / "metadata.json"
TEMP_AUDIO       = BASE / "temp_audio"

for p in (UPLOADS, SCORM_SRC, SCORM_TRANSLATED, ZIPS, TEMP_AUDIO):
    p.mkdir(parents=True, exist_ok=True)

# ── translation util ───────────────────────────────────
LANGS = {
    "English": "en", "French": "fr", "German": "de",
    "Hindi": "hi",   "Russian": "ru", "Japanese": "ja",
    "Chinese": "zh-cn", "Spanish": "es", "Italian": "it",
    "Portuguese": "pt", "Korean": "ko", "Arabic": "ar"
}

# gTTS language codes (slightly different from translator codes)
GTTS_LANGS = {
    "en": "en", "fr": "fr", "de": "de", "hi": "hi", 
    "ru": "ru", "ja": "ja", "zh-cn": "zh-cn", "es": "es",
    "it": "it", "pt": "pt", "ko": "ko", "ar": "ar"
}

translate = lambda txt, tgt: GoogleTranslator(source="auto", target=tgt).translate(txt)

# keys inside Storyline random js
PATTERNS = [
    re.compile(r'("altText"\s*:\s*")(.*?)(")'),
    re.compile(r'("title"\s*:\s*")(.*?)(")'),
    re.compile(r'(\{"text"\s*:\s*")(.*?)(")')
]
EXCLUDED = {"data.js", "frame.js", "paths.js"}

# Supported audio formats
AUDIO_EXTENSIONS = {'.mp3', '.wav', '.ogg', '.m4a', '.flac', '.aac'}

# ── metadata management ────────────────────────────────

def load_metadata():
    if METADATA.exists():
        try:
            with open(METADATA, 'r') as f:
                content = f.read().strip()
                if content:
                    return json.loads(content)
                else:
                    return {}
        except (json.JSONDecodeError, ValueError):
            # If file is corrupted, backup and start fresh
            if METADATA.exists():
                backup = METADATA.with_suffix('.json.backup')
                shutil.copy2(METADATA, backup)
                print(f"Warning: Corrupted metadata.json backed up to {backup}")
            return {}
    return {}

def save_metadata(data):
    try:
        with open(METADATA, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Error saving metadata: {e}")
        # Try to save to a backup location
        backup = METADATA.with_suffix('.json.emergency')
        try:
            with open(backup, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"Metadata saved to emergency backup: {backup}")
        except:
            pass

def add_course_metadata(pkg_id, filename, original_name):
    meta = load_metadata()
    if pkg_id not in meta:
        meta[pkg_id] = {
            'id': pkg_id,
            'original_name': original_name,
            'filename': filename,
            'uploaded_at': datetime.now().isoformat(),
            'translations': {}
        }
        save_metadata(meta)
    return meta[pkg_id]

def add_translation_metadata(pkg_id, lang_code, lang_name, audio_count=0):
    meta = load_metadata()
    if pkg_id in meta:
        meta[pkg_id]['translations'][lang_code] = {
            'language': lang_name,
            'created_at': datetime.now().isoformat(),
            'zip_file': f"{pkg_id}_{lang_code}.zip",
            'audio_files_translated': audio_count
        }
        save_metadata(meta)

# ── audio translation functions ────────────────────────

def transcribe_audio(audio_path: Path) -> str:
    """Convert audio to text using speech recognition"""
    recognizer = sr.Recognizer()
    
    # Convert to WAV if needed
    temp_wav = TEMP_AUDIO / f"temp_{uuid.uuid4().hex}.wav"
    try:
        audio = AudioSegment.from_file(str(audio_path))
        audio.export(str(temp_wav), format="wav")
        
        with sr.AudioFile(str(temp_wav)) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)
            return text
    except Exception as e:
        print(f"Error transcribing {audio_path.name}: {e}")
        return ""
    finally:
        if temp_wav.exists():
            temp_wav.unlink()

def text_to_speech(text: str, lang_code: str, output_path: Path):
    """Convert text to speech in target language"""
    try:
        gtts_lang = GTTS_LANGS.get(lang_code, "en")
        tts = gTTS(text=text, lang=gtts_lang, slow=False)
        tts.save(str(output_path))
        return True
    except Exception as e:
        print(f"Error generating speech: {e}")
        return False

def translate_audio_file(audio_path: Path, target_lang: str, output_path: Path) -> bool:
    """
    Complete audio translation pipeline:
    1. Transcribe audio to text
    2. Translate text
    3. Convert translated text to speech
    """
    try:
        print(f"Processing audio: {audio_path.name}")
        
        # Step 1: Transcribe
        original_text = transcribe_audio(audio_path)
        if not original_text:
            print(f"  - Could not transcribe audio")
            return False
        
        print(f"  - Transcribed: {original_text[:50]}...")
        
        # Step 2: Translate
        translated_text = translate(original_text, target_lang)
        print(f"  - Translated: {translated_text[:50]}...")
        
        # Step 3: Generate speech
        success = text_to_speech(translated_text, target_lang, output_path)
        
        if success:
            print(f"  ✓ Successfully translated audio")
        
        return success
        
    except Exception as e:
        print(f"Error translating audio {audio_path.name}: {e}")
        return False

def find_audio_files(directory: Path) -> list:
    """Find all audio files in directory recursively"""
    audio_files = []
    for ext in AUDIO_EXTENSIONS:
        audio_files.extend(directory.rglob(f"*{ext}"))
    return audio_files

# ── core functions ─────────────────────────────────────

def extract_zip(src: Path, dest: Path):
    with zipfile.ZipFile(src) as z: 
        z.extractall(dest)

def zip_dir(src_dir: Path, zip_path: Path):
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for p in src_dir.rglob("*"):
            if p.is_file():
                z.write(p, p.relative_to(src_dir))

def translate_storyline_js(js_path: Path, lang_code: str):
    if js_path.name in EXCLUDED: 
        return
    text = js_path.read_text("utf-8", errors="ignore")

    def do(match):
        src = match.group(2)
        try:
            tgt = translate(src, lang_code) or src
        except Exception:
            tgt = src
        return match.group(1) + tgt + match.group(3)

    for pat in PATTERNS:
        text = pat.sub(do, text)

    js_path.write_text(text, "utf-8")

# ── routes ─────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html", languages=LANGS.keys())

@app.route("/library")
def library():
    meta = load_metadata()
    courses = []
    for pkg_id, info in meta.items():
        course_data = {
            'id': pkg_id,
            'name': info.get('original_name', 'Unknown'),
            'uploaded_at': info.get('uploaded_at', ''),
            'translations': info.get('translations', {})
        }
        courses.append(course_data)
    
    # Sort by upload date, newest first
    courses.sort(key=lambda x: x['uploaded_at'], reverse=True)
    
    return render_template("library.html", courses=courses, languages=LANGS)

@app.route("/upload", methods=["POST"])
def upload():
    if 'scormZip' not in request.files:
        flash("File field name must be 'scormZip'.", "error")
        return redirect("/")

    file = request.files['scormZip']
    
    if not file.filename or not file.filename.lower().endswith(".zip"):
        flash("Upload a .zip file.", "error")
        return redirect("/")

    # Create unique package ID
    original_name = Path(file.filename).stem
    pkg_id = f"{original_name}-{uuid.uuid4().hex[:5]}"
    src_dir = SCORM_SRC / pkg_id
    src_dir.mkdir(parents=True)

    # Save and extract
    zip_path = src_dir / "course.zip"
    file.save(zip_path)
    extract_zip(zip_path, src_dir)
    
    # Save metadata
    add_course_metadata(pkg_id, file.filename, original_name)
    
    flash(f"Successfully uploaded: {original_name}", "success")
    return redirect(url_for("library"))

@app.route("/translate/<pkg_id>", methods=["POST"])
def translate_course(pkg_id):
    target_lang = request.form.get("language", "fr")
    translate_audio = request.form.get("translate_audio") == "on"
    lang_name = [k for k, v in LANGS.items() if v == target_lang][0]
    
    src_dir = SCORM_SRC / pkg_id
    if not src_dir.exists():
        flash("Course not found.", "error")
        return redirect(url_for("library"))
    
    # Check if translation already exists
    tgt_dir = SCORM_TRANSLATED / f"{pkg_id}_{target_lang}"
    if tgt_dir.exists():
        flash(f"Translation to {lang_name} already exists.", "info")
        return redirect(url_for("play", pkg=pkg_id, lang=target_lang))
    
    # Copy source to target
    shutil.copytree(src_dir, tgt_dir, dirs_exist_ok=True)
    
    # Translate JavaScript text
    js_root = tgt_dir / "html5" / "data" / "js"
    if js_root.exists():
        for js in js_root.glob("*.js"):
            translate_storyline_js(js, target_lang)
    
    # Translate audio files if requested
    audio_count = 0
    if translate_audio:
        audio_files = find_audio_files(tgt_dir)
        total_audio = len(audio_files)
        
        if total_audio > 0:
            flash(f"Found {total_audio} audio files. Starting translation...", "info")
            
            for i, audio_file in enumerate(audio_files, 1):
                print(f"\nTranslating audio {i}/{total_audio}: {audio_file.name}")
                
                # Create output path (same location, same name)
                output_path = audio_file
                
                # Backup original
                backup_path = audio_file.with_suffix(audio_file.suffix + '.original')
                shutil.copy2(audio_file, backup_path)
                
                # Translate
                success = translate_audio_file(audio_file, target_lang, output_path)
                
                if success:
                    audio_count += 1
                    # Remove backup
                    backup_path.unlink()
                else:
                    # Restore from backup if translation failed
                    shutil.copy2(backup_path, audio_file)
                    backup_path.unlink()
    
    # Create zip
    out_zip = ZIPS / f"{pkg_id}_{target_lang}.zip"
    zip_dir(tgt_dir, out_zip)
    
    # Update metadata
    add_translation_metadata(pkg_id, target_lang, lang_name, audio_count)
    
    if translate_audio and audio_count > 0:
        flash(f"Successfully translated to {lang_name}! Translated {audio_count} audio files.", "success")
    else:
        flash(f"Successfully translated text to {lang_name}!", "success")
    
    return redirect(url_for("play", pkg=pkg_id, lang=target_lang))

@app.route("/play")
def play():
    pkg = request.args.get("pkg")
    lang = request.args.get("lang", "en")
    
    if not pkg:
        flash("No course specified.", "error")
        return redirect(url_for("library"))
    
    folder = SCORM_TRANSLATED / f"{pkg}_{lang}" if lang != "en" else SCORM_SRC / pkg
    
    # Try different launch file names
    launch_files = ["index_lms.html", "index.html", "story.html"]
    launch = None
    for launch_name in launch_files:
        potential_launch = folder / launch_name
        if potential_launch.exists():
            launch = potential_launch
            break
    
    if not launch:
        flash(f"Launch file not found for course: {pkg}", "error")
        return redirect(url_for("library"))
    
    course_url = f"/static/{launch.relative_to(BASE / 'static')}"
    zip_name = f"{pkg}_{lang}.zip" if lang != "en" else None
    
    # Get course metadata
    meta = load_metadata()
    course_info = meta.get(pkg, {})
    
    return render_template("player.html", 
                         course_url=course_url,
                         pkg=pkg, 
                         lang=lang, 
                         zip_name=zip_name, 
                         languages=LANGS,
                         course_info=course_info)

@app.route('/download/<zipname>')
def download(zipname):
    zip_path = ZIPS / zipname
    if not zip_path.exists():
        flash("Download file not found.", "error")
        return redirect(url_for("library"))
    return send_file(zip_path, as_attachment=True)

@app.route('/delete/<pkg_id>', methods=['POST'])
def delete_course(pkg_id):
    # Delete source folder
    src_dir = SCORM_SRC / pkg_id
    if src_dir.exists():
        shutil.rmtree(src_dir)
    
    # Delete all translations
    for trans_dir in SCORM_TRANSLATED.glob(f"{pkg_id}_*"):
        shutil.rmtree(trans_dir)
    
    # Delete zip files
    for zip_file in ZIPS.glob(f"{pkg_id}_*.zip"):
        zip_file.unlink()
    
    # Update metadata
    meta = load_metadata()
    if pkg_id in meta:
        del meta[pkg_id]
        save_metadata(meta)
    
    flash("Course deleted successfully.", "success")
    return redirect(url_for("library"))

# ajax translate node
@app.route('/translate-node', methods=['POST'])
def translate_node():
    d = request.get_json(force=True)
    txt = d.get('text', '')
    tgt = d.get('target', 'fr')
    return jsonify({'t': translate(txt, tgt)})

if __name__ == '__main__':
>>>>>>> 0b1e9e43 (SCORM Audio Translation)
    app.run(debug=True, port=5000)