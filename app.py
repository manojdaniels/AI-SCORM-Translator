<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> 0b1e9e43 (SCORM Audio Translation)
import os
import shutil
import zipfile
import uuid
import json
import re
<<<<<<< HEAD
import threading
=======
>>>>>>> 0b1e9e43 (SCORM Audio Translation)
from pathlib import Path
from datetime import datetime
from flask import (
    Flask, render_template, request, redirect, url_for,
    flash, send_file, jsonify
)
<<<<<<< HEAD
from deep_translator import GoogleTranslator
=======
from deep_translator import GoogleTranslator, MyMemoryTranslator
>>>>>>> 0b1e9e43 (SCORM Audio Translation)
from gtts import gTTS
import speech_recognition as sr
from pydub import AudioSegment
import tempfile
from threading import Lock
import xml.etree.ElementTree as ET
<<<<<<< HEAD
import time
=======

>>>>>>> 0b1e9e43 (SCORM Audio Translation)

# ── Translation progress tracking ───────────────────────────
progress = {}
progress_lock = Lock()


def set_progress(pkg_id, message, percent=None):
    """Update progress info for a package"""
    with progress_lock:
        progress[pkg_id] = {"message": message, "percent": percent or 0}


def get_progress(pkg_id):
    """Read progress info"""
    with progress_lock:
        return progress.get(pkg_id, {"message": "Idle", "percent": 0})


# ── Flask app setup ───────────────────────────────────────
app = Flask(__name__)
app.secret_key = "change-me"

BASE = Path(__file__).parent
UPLOADS = BASE / "uploads"
SCORM_SRC = BASE / "static" / "scorm"
SCORM_TRANSLATED = BASE / "static" / "scorm_translated"
ZIPS = BASE / "zips"
METADATA = BASE / "metadata.json"
TEMP_AUDIO = BASE / "temp_audio"

<<<<<<< HEAD
# Ensure directories exist
for p in (UPLOADS, SCORM_SRC, SCORM_TRANSLATED, ZIPS, TEMP_AUDIO):
    p.mkdir(parents=True, exist_ok=True)

=======
>>>>>>> 0b1e9e43 (SCORM Audio Translation)

@app.route("/progress/<pkg_id>")
def get_progress_route(pkg_id):
    """Return JSON progress for a given course"""
    return jsonify(get_progress(pkg_id))


<<<<<<< HEAD
=======
# Ensure directories exist
for p in (UPLOADS, SCORM_SRC, SCORM_TRANSLATED, ZIPS, TEMP_AUDIO):
    p.mkdir(parents=True, exist_ok=True)


>>>>>>> 0b1e9e43 (SCORM Audio Translation)
# ── Translation utils ──────────────────────────────────────
LANGS = {
    "English": "en", "French": "fr", "German": "de",
    "Hindi": "hi", "Russian": "ru", "Japanese": "ja",
    "Chinese": "zh-cn", "Spanish": "es", "Italian": "it",
    "Portuguese": "pt", "Korean": "ko", "Arabic": "ar"
}

# gTTS language codes
GTTS_LANGS = {
    "en": "en", "fr": "fr", "de": "de", "hi": "hi",
    "ru": "ru", "ja": "ja", "zh-cn": "zh-cn", "es": "es",
    "it": "it", "pt": "pt", "ko": "ko", "ar": "ar"
}

<<<<<<< HEAD
# safe translator wrapper
def do_translate(txt, tgt):
    """Wrapper around GoogleTranslator"""
    if not txt or not txt.strip():
        return txt
    try:
        # ✅ The method is .translate(), NOT .do_translate()
        return GoogleTranslator(source="auto", target=tgt).translate(txt)
    except Exception as e:
        print(f"⚠ Translation error (GoogleTranslator): {e}")
        return txt



# Flexible text patterns in SCORM files (kept conservative)
PATTERNS = [
    re.compile(r'(["\'](altText|title|text|label|caption|description|heading|content)["\']\s*:\s*["\'])([^"\']+)(["\'])'),
    re.compile(r'(>\s*)([^<]{2,})(\s*<)'),  # Capture text between HTML tags
    re.compile(r'(["\'])([A-Za-z0-9 ,.!?;:\-\']{3,})(["\'])')  # General fallback
]

=======
#translate = lambda txt, tgt: GoogleTranslator(source="auto", target=tgt).translate(txt)

def translate_text(text, target_lang):
    try:
        text = text.strip()
        if not text:
            return text
        for _ in range(3):
            try:
                return GoogleTranslator(source="auto", target=target_lang).translate(text)
            except Exception:
                pass
        # fallback
        print(f"⚠ Google blocked, using MyMemory fallback.")
        return MyMemoryTranslator(source="auto", target=target_lang).translate(text)
    except Exception as e:
        print(f"⚠ Translation error: {e}")
        return text



# Flexible text patterns in SCORM files
PATTERNS = [
    re.compile(r'(["\'](altText|title|text|label|caption|description|heading|content)["\']\s*:\s*["\'])([^"\']{3,})(["\'])'),
    re.compile(r'(>\s*)([^<>]{3,})(\s*<)'),  # Capture inner HTML text
    re.compile(r'=\s*["\']([^"\']{3,})["\']'),  # General text assignment
]


>>>>>>> 0b1e9e43 (SCORM Audio Translation)
EXCLUDED = {"data.js", "frame.js", "paths.js", "configuration.js"}
AUDIO_EXTENSIONS = {'.mp3', '.wav', '.ogg', '.m4a', '.flac', '.aac'}


# ── Metadata management ─────────────────────────────────────
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
        backup = METADATA.with_suffix('.json.emergency')
        try:
            with open(backup, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"Metadata saved to emergency backup: {backup}")
        except:
            pass


<<<<<<< HEAD
def add_course_metadata(pkg_id, filename, original_name):
=======
def add_course_metadata(pkg_id, filename, original_name, launch_file=None):
    """Add or update course metadata"""
>>>>>>> 0b1e9e43 (SCORM Audio Translation)
    meta = load_metadata()
    if pkg_id not in meta:
        meta[pkg_id] = {
            'id': pkg_id,
            'original_name': original_name,
            'filename': filename,
            'uploaded_at': datetime.now().isoformat(),
<<<<<<< HEAD
            'translations': {}
        }
        save_metadata(meta)
    return meta[pkg_id]


=======
            'translations': {},
            'launch_file': str(launch_file) if launch_file else None
        }
    else:
        if launch_file:
            meta[pkg_id]['launch_file'] = str(launch_file)
    save_metadata(meta)
    return meta[pkg_id]



>>>>>>> 0b1e9e43 (SCORM Audio Translation)
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


# ── Audio translation ───────────────────────────────────────
def transcribe_audio(audio_path: Path) -> str:
<<<<<<< HEAD
    """Convert audio to text using speech_recognition (Google)"""
=======
    """Convert audio to text using speech recognition"""
>>>>>>> 0b1e9e43 (SCORM Audio Translation)
    recognizer = sr.Recognizer()
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
<<<<<<< HEAD
            try:
                temp_wav.unlink()
            except Exception:
                pass
=======
            temp_wav.unlink()
>>>>>>> 0b1e9e43 (SCORM Audio Translation)


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
    """Full audio translation pipeline"""
    try:
        print(f"Processing audio: {audio_path.name}")
        original_text = transcribe_audio(audio_path)
        if not original_text:
            print(f"  - Could not transcribe audio")
            return False

        print(f"  - Transcribed: {original_text[:50]}...")
<<<<<<< HEAD
        translated_text = do_translate(original_text, target_lang)
=======
        translated_text = translate_text(original_text, target_lang)
>>>>>>> 0b1e9e43 (SCORM Audio Translation)
        print(f"  - Translated: {translated_text[:50]}...")

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


# ── Core functions ──────────────────────────────────────────
def extract_zip(src: Path, dest: Path):
    with zipfile.ZipFile(src) as z:
        z.extractall(dest)


def zip_dir(src_dir: Path, zip_path: Path):
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for p in src_dir.rglob("*"):
            if p.is_file():
                z.write(p, p.relative_to(src_dir))

<<<<<<< HEAD

def find_launch_file_from_manifest(course_folder: Path):
    """
    Parse imsmanifest.xml to find the official launch HTML file.
    Returns a Path if found, else None.
    """
    manifest_path = None
=======
# Utility Function to Parse imsmanifest.xml

def find_launch_file_from_manifest(course_folder: Path) -> Path | None:
    """
    Parse imsmanifest.xml to find the official SCORM launch HTML file.
    Handles namespaces, relative hrefs, and nested manifests.
    """
    manifest_path = None

    # Find imsmanifest.xml recursively
>>>>>>> 0b1e9e43 (SCORM Audio Translation)
    for root, dirs, files in os.walk(course_folder):
        for f in files:
            if f.lower() == "imsmanifest.xml":
                manifest_path = Path(root) / f
                break
        if manifest_path:
            break

    if not manifest_path or not manifest_path.exists():
        print(f"⚠ No imsmanifest.xml found in {course_folder}")
        return None

    try:
        tree = ET.parse(manifest_path)
        root = tree.getroot()

<<<<<<< HEAD
        # Find the <resource> element that defines the SCORM entry point
        for resource in root.findall(".//{*}resource"):
            href = resource.attrib.get("href")
            if href:
                launch_file = (manifest_path.parent / href).resolve()
                if launch_file.exists():
                    print(f"✅ Launch file found via manifest: {launch_file}")
                    return launch_file
        print(f"⚠ No href attribute found in manifest resources.")
=======
        # Detect namespace if present
        nsmap = {}
        if root.tag.startswith("{"):
            uri = root.tag.split("}")[0].strip("{")
            nsmap = {"ns": uri}

        # Try both with and without namespace
        resource_tags = root.findall(".//ns:resource", nsmap) if nsmap else root.findall(".//resource")

        for res in resource_tags:
            href = res.attrib.get("href")
            base = res.attrib.get("xml:base", "") or res.attrib.get("base", "")
            if href:
                launch_path = (manifest_path.parent / base / href).resolve()
                if launch_path.exists():
                    print(f"✅ Launch file found via manifest: {launch_path}")
                    return launch_path

            # Sometimes <file href="story.html"> is nested inside <resource>
            for file_tag in res.findall(".//ns:file", nsmap) if nsmap else res.findall(".//file"):
                href2 = file_tag.attrib.get("href")
                if href2:
                    launch_path = (manifest_path.parent / base / href2).resolve()
                    if launch_path.exists():
                        print(f"✅ Launch file found via <file>: {launch_path}")
                        return launch_path

        print(f"⚠ No valid href found in manifest resources.")

>>>>>>> 0b1e9e43 (SCORM Audio Translation)
    except Exception as e:
        print(f"⚠ Error parsing imsmanifest.xml: {e}")

    return None


<<<<<<< HEAD
=======

>>>>>>> 0b1e9e43 (SCORM Audio Translation)
def translate_storyline_js(js_path: Path, lang_code: str):
    """Translate text inside Storyline JS or HTML files"""
    if js_path.name in EXCLUDED:
        return

    try:
        text = js_path.read_text("utf-8", errors="ignore")
        translations_made = 0
<<<<<<< HEAD

        def do(match):
            nonlocal translations_made
            # choose correct group if pattern varies
            src = None
            groups = match.groups()
            if len(groups) >= 3:
                src = groups[2]
            elif len(groups) >= 2:
                src = groups[1]
            else:
                src = match.group(0)

            if not src or len(src.strip()) < 3 or not any(c.isalpha() for c in src):
                return match.group(0)

            try:
                tgt = do_translate(src, lang_code)
                if tgt and tgt != src:
                    translations_made += 1
                    # reconstruct replacement conservative way
                    prefix = match.group(1) if len(groups) >= 3 else ''
                    suffix = match.group(4) if len(groups) >= 4 else ''
                    return prefix + tgt + suffix
=======
        print(f"🔍 Scanning {js_path.name} for translatable text...")

        def do(match):
            nonlocal translations_made
            src = match.group(3) if len(match.groups()) >= 3 else match.group(2)
            if len(src.strip()) < 3 or not any(c.isalpha() for c in src):
                return match.group(0)

            try:
               # tgt = translate(src, lang_code)
                tgt = translate_text(src, lang_code)
                if tgt and tgt != src:
                    translations_made += 1
                    before = match.group(1) if len(match.groups()) >= 3 else ''
                    after = match.group(4) if len(match.groups()) >= 4 else ''
                    return before + tgt + after
>>>>>>> 0b1e9e43 (SCORM Audio Translation)
            except Exception as e:
                print(f"⚠ Translation error in {js_path.name}: {e}")
            return match.group(0)

        for pat in PATTERNS:
            text = pat.sub(do, text)

        if translations_made > 0:
            js_path.write_text(text, "utf-8")
<<<<<<< HEAD
            print(f"✓ Translated {translations_made} text blocks in {js_path.name}")
=======
            print(f"✅ Translated {translations_made} segments in {js_path.name}")
        
        else:
            print(f"⚠ No translatable text found in {js_path.name}")
>>>>>>> 0b1e9e43 (SCORM Audio Translation)

    except Exception as e:
        print(f"Error processing {js_path.name}: {e}")


<<<<<<< HEAD
# ── Background worker used by /translate route ─────────────
def background_translate(pkg_id, lang_name, target_lang, translate_audio):
    try:
        src_dir = SCORM_SRC / pkg_id
        tgt_dir = SCORM_TRANSLATED / f"{pkg_id}_{target_lang}"

        if not src_dir.exists():
            set_progress(pkg_id, "Source not found", 0)
            return

        set_progress(pkg_id, "Copying course files for translation...", 5)
        if tgt_dir.exists():
            shutil.rmtree(tgt_dir)
        shutil.copytree(src_dir, tgt_dir)

        # Text translation
        set_progress(pkg_id, "Translating text files...", 15)
        js_root = tgt_dir / "story_content"
        if not js_root.exists():
            js_root = tgt_dir / "scormcontent"
        if not js_root.exists():
            js_root = tgt_dir

        js_files = list(js_root.rglob("*.js"))
        total_js = len(js_files)
        for i, js in enumerate(js_files, 1):
            translate_storyline_js(js, target_lang)
            percent = 15 + int(i / max(total_js, 1) * 40)
            set_progress(pkg_id, f"Translated {i}/{total_js} JS files...", percent)

        # Audio translation
        audio_count = 0
        if translate_audio:
            audio_files = find_audio_files(tgt_dir)
            total_audio = len(audio_files)
            if total_audio > 0:
                for i, audio_file in enumerate(audio_files, 1):
                    set_progress(pkg_id, f"Translating audio {i}/{total_audio}...", 60 + int(i / max(total_audio, 1) * 30))
                    output_path = audio_file
                    backup_path = audio_file.with_suffix(audio_file.suffix + '.original')
                    try:
                        shutil.copy2(audio_file, backup_path)
                    except Exception:
                        pass
                    success = translate_audio_file(audio_file, target_lang, output_path)
                    if success:
                        audio_count += 1
                        try:
                            backup_path.unlink()
                        except Exception:
                            pass
                    else:
                        try:
                            shutil.copy2(backup_path, audio_file)
                            backup_path.unlink()
                        except Exception:
                            pass

        set_progress(pkg_id, "Packaging translated SCORM...", 95)
        out_zip = ZIPS / f"{pkg_id}_{target_lang}.zip"
        zip_dir(tgt_dir, out_zip)

        add_translation_metadata(pkg_id, target_lang, lang_name, audio_count)
        set_progress(pkg_id, f"Translation complete ✅ ({lang_name})", 100)
        # keep complete state visible briefly
        time.sleep(2)
        set_progress(pkg_id, "Idle", 0)

    except Exception as e:
        print(f"Error in background_translate: {e}")
        set_progress(pkg_id, f"Error: {e}", 0)


=======
>>>>>>> 0b1e9e43 (SCORM Audio Translation)
# ── Routes ─────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html", languages=LANGS.keys())


@app.route("/library")
def library():
    meta = load_metadata()
    courses = []
    for pkg_id, info in meta.items():
        courses.append({
            'id': pkg_id,
            'name': info.get('original_name', 'Unknown'),
            'uploaded_at': info.get('uploaded_at', ''),
            'translations': info.get('translations', {})
        })
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

    original_name = Path(file.filename).stem
    pkg_id = f"{original_name}-{uuid.uuid4().hex[:5]}"
    src_dir = SCORM_SRC / pkg_id
    src_dir.mkdir(parents=True, exist_ok=True)

    zip_path = UPLOADS / f"{pkg_id}.zip"
    file.save(zip_path)

    try:
<<<<<<< HEAD
        extract_zip(zip_path, src_dir)
        print(f"✓ Extracted SCORM package to: {src_dir}")
    except Exception as e:
        flash(f"Error extracting ZIP file: {e}", "error")
        return redirect("/")

    add_course_metadata(pkg_id, file.filename, original_name)
=======
            extract_zip(zip_path, src_dir)
            print(f"✓ Extracted SCORM package to: {src_dir}")
            # Try to detect and cache launch file at upload time
            launch_file = find_launch_file_from_manifest(src_dir)
            if not launch_file:
                print(f"⚠ Manifest not found; will detect during playback.")
            else:
                print(f"✅ Cached launch file at upload: {launch_file}")


    except Exception as e:
            flash(f"Error extracting ZIP file: {e}", "error")
            return redirect("/")

    add_course_metadata(pkg_id, file.filename, original_name, launch_file)
>>>>>>> 0b1e9e43 (SCORM Audio Translation)
    flash(f"Successfully uploaded: {original_name}", "success")
    return redirect(url_for("library"))


@app.route("/translate", methods=["POST"])
<<<<<<< HEAD
def translate():
    # Kick off background translation and return immediately
=======
def translate_course():
>>>>>>> 0b1e9e43 (SCORM Audio Translation)
    pkg_id = request.form.get("pkg_id")
    lang_name = request.form.get("language")
    target_lang = LANGS.get(lang_name, "en")
    translate_audio = request.form.get("translate_audio") == "on"

    if not pkg_id or not lang_name:
        flash("Missing course ID or language.", "error")
        return redirect(url_for("library"))

<<<<<<< HEAD
    # Start background worker
    t = threading.Thread(target=background_translate, args=(pkg_id, lang_name, target_lang, translate_audio), daemon=True)
    t.start()

    flash(f"Started background translation for {lang_name}.", "info")
=======
    src_dir = SCORM_SRC / pkg_id
    tgt_dir = SCORM_TRANSLATED / f"{pkg_id}_{target_lang}"

    if not src_dir.exists():
        flash("Source course not found.", "error")
        return redirect(url_for("library"))

    set_progress(pkg_id, "Copying course files for translation...", 5)
    if tgt_dir.exists():
        shutil.rmtree(tgt_dir)
    shutil.copytree(src_dir, tgt_dir)

    # Text translation
    js_root = tgt_dir / "story_content"
    if not js_root.exists():
        js_root = tgt_dir / "scormcontent"
    if not js_root.exists():
        js_root = tgt_dir

    set_progress(pkg_id, "Translating text files...", 15)
    js_files = list(js_root.glob("*.js"))
    total_js = len(js_files)
    print(f"🧩 Starting translation of {total_js} JS files for {lang_name}")
    for i, js in enumerate(js_files, 1):
        translate_storyline_js(js, target_lang)
        set_progress(pkg_id, f"Translated {i}/{total_js} JS files...", 15 + int(i / max(total_js, 1) * 40))

    # Audio translation
    audio_count = 0
    if translate_audio:
        audio_files = find_audio_files(tgt_dir)
        total_audio = len(audio_files)
        if total_audio > 0:
            for i, audio_file in enumerate(audio_files, 1):
                set_progress(pkg_id, f"Translating audio {i}/{total_audio}...", 60 + int(i / total_audio * 30))
                output_path = audio_file
                backup_path = audio_file.with_suffix(audio_file.suffix + '.original')
                shutil.copy2(audio_file, backup_path)
                success = translate_audio_file(audio_file, target_lang, output_path)
                if success:
                    audio_count += 1
                    backup_path.unlink()
                else:
                    shutil.copy2(backup_path, audio_file)
                    backup_path.unlink()

    set_progress(pkg_id, "Packaging translated SCORM...", 95)
    out_zip = ZIPS / f"{pkg_id}_{target_lang}.zip"
    zip_dir(tgt_dir, out_zip)
    add_translation_metadata(pkg_id, target_lang, lang_name, audio_count)
    set_progress(pkg_id, f"Translation complete ✅ ({lang_name})", 100)

    flash(f"Successfully translated to {lang_name}!", "success")
>>>>>>> 0b1e9e43 (SCORM Audio Translation)
    return redirect(url_for("library"))


@app.route("/play")
def play():
    pkg = request.args.get("pkg")
    lang = request.args.get("lang", "en")

    if not pkg:
        flash("No course specified.", "error")
        return redirect(url_for("library"))

    folder = SCORM_TRANSLATED / f"{pkg}_{lang}" if lang != "en" else SCORM_SRC / pkg
    if not folder.exists():
        flash("Course folder not found.", "error")
        return redirect(url_for("library"))

<<<<<<< HEAD
=======
    meta = load_metadata()
    course_info = meta.get(pkg, {})

    launch = None

    # 1️⃣ Use cached launch file if available
    cached_launch = course_info.get("launch_file")
    if cached_launch:
        potential = BASE / cached_launch
        if potential.exists():
            print(f"✅ Using cached launch file: {potential}")
            launch = potential
        else:
            print(f"⚠ Cached launch path missing, re-detecting...")

    # 2️⃣ If not cached, detect via manifest
    if not launch:
        print(f"🧭 Detecting launch file in: {folder}")
        launch = find_launch_file_from_manifest(folder)
        if launch:
            # Save it to metadata for next time
            add_course_metadata(pkg, course_info.get("filename"), course_info.get("original_name"), launch)

    # 3️⃣ Fallback: scan for common launch files
    if not launch:
        launch_candidates = {"index_lms.html", "index.html", "story.html", "launch.html", "player.html"}
        for root, _, files in os.walk(folder):
            for f in files:
                if f.lower() in launch_candidates:
                    launch = Path(root) / f
                    print(f"✅ Launch file found via fallback: {launch}")
                    add_course_metadata(pkg, course_info.get("filename"), course_info.get("original_name"), launch)
                    break
            if launch:
                break

    if not launch:
        flash(f"No valid launch file found in {folder.name}", "error")
        return redirect(url_for("library"))

    rel_path = launch.relative_to(BASE / "static")
    course_url = f"/static/{rel_path}".replace("\\", "/")

    return render_template(
        "player.html",
        course_url=course_url,
        pkg=pkg,
        lang=lang,
        languages=LANGS,
        course_info=course_info
    )




def play():
    pkg = request.args.get("pkg")
    lang = request.args.get("lang", "en")

    if not pkg:
        flash("No course specified.", "error")
        return redirect(url_for("library"))

    folder = SCORM_TRANSLATED / f"{pkg}_{lang}" if lang != "en" else SCORM_SRC / pkg
    if not folder.exists():
        flash("Course folder not found.", "error")
        return redirect(url_for("library"))

>>>>>>> 0b1e9e43 (SCORM Audio Translation)
    # 1️⃣ Try manifest-based launch detection first
    launch = find_launch_file_from_manifest(folder)

    # 2️⃣ Fallback to scanning for common HTML entry files
    if not launch:
        launch_candidates = {"index_lms.html", "index.html", "story.html", "launch.html", "player.html"}
        for root, _, files in os.walk(folder):
            for f in files:
                if f.lower() in launch_candidates:
                    launch = Path(root) / f
                    break
            if launch:
                break

    if not launch:
        flash(f"No valid launch file found in {folder.name}", "error")
        return redirect(url_for("library"))

    # Build relative URL for rendering in iframe
    rel_path = launch.relative_to(BASE / "static")
    course_url = f"/static/{rel_path}".replace("\\", "/")

    meta = load_metadata()
    course_info = meta.get(pkg, {})

    return render_template(
        "player.html",
        course_url=course_url,
        pkg=pkg,
        lang=lang,
        languages=LANGS,
        course_info=course_info
    )


<<<<<<< HEAD
=======

>>>>>>> 0b1e9e43 (SCORM Audio Translation)
@app.route('/download/<zipname>')
def download(zipname):
    zip_path = ZIPS / zipname
    if not zip_path.exists():
        flash("Download file not found.", "error")
        return redirect(url_for("library"))
    return send_file(zip_path, as_attachment=True)


<<<<<<< HEAD
@app.route('/delete/<pkg>', methods=['POST'])
def delete(pkg):
    # Delete source folder
    src_dir = SCORM_SRC / pkg
    if src_dir.exists():
        shutil.rmtree(src_dir)

    # Delete all translations
    for trans_dir in SCORM_TRANSLATED.glob(f"{pkg}_*"):
        shutil.rmtree(trans_dir)

    # Delete zip files
    for zip_file in ZIPS.glob(f"{pkg}_*.zip"):
        try:
            zip_file.unlink()
        except Exception:
            pass

    # Update metadata
    meta = load_metadata()
    if pkg in meta:
        del meta[pkg]
=======
@app.route('/delete/<pkg_id>', methods=['POST'])
def delete_course(pkg_id):
    src_dir = SCORM_SRC / pkg_id
    if src_dir.exists():
        shutil.rmtree(src_dir)

    for trans_dir in SCORM_TRANSLATED.glob(f"{pkg_id}_*"):
        shutil.rmtree(trans_dir)

    for zip_file in ZIPS.glob(f"{pkg_id}_*.zip"):
        zip_file.unlink()

    meta = load_metadata()
    if pkg_id in meta:
        del meta[pkg_id]
>>>>>>> 0b1e9e43 (SCORM Audio Translation)
        save_metadata(meta)

    flash("Course deleted successfully.", "success")
    return redirect(url_for("library"))


@app.route('/translate-node', methods=['POST'])
def translate_node():
    d = request.get_json(force=True)
    txt = d.get('text', '')
    tgt = d.get('target', 'fr')
<<<<<<< HEAD
    return jsonify({'t': do_translate(txt, tgt)})
=======
    return jsonify({'t': translate_text(txt, tgt)})
>>>>>>> 0b1e9e43 (SCORM Audio Translation)


@app.route('/test-translation')
def test_translation():
    try:
        test_text = "Hello, this is a test"
<<<<<<< HEAD
        result = do_translate(test_text, "fr")
=======
        result = translate_text(test_text, "fr")
>>>>>>> 0b1e9e43 (SCORM Audio Translation)
        return jsonify({
            'success': True,
            'original': test_text,
            'translated': result,
            'target_language': 'French'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


<<<<<<< HEAD
if __name__ == '__main__':
    app.run(debug=True, port=5000)
=======
import os
import shutil
import zipfile
import uuid
import json
import re
import threading
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
from threading import Lock
import xml.etree.ElementTree as ET
import time

# ── Translation progress tracking ───────────────────────────
progress = {}
progress_lock = Lock()


def set_progress(pkg_id, message, percent=None):
    """Update progress info for a package"""
    with progress_lock:
        progress[pkg_id] = {"message": message, "percent": percent or 0}


def get_progress(pkg_id):
    """Read progress info"""
    with progress_lock:
        return progress.get(pkg_id, {"message": "Idle", "percent": 0})


# ── Flask app setup ───────────────────────────────────────
app = Flask(__name__)
app.secret_key = "change-me"

BASE = Path(__file__).parent
UPLOADS = BASE / "uploads"
SCORM_SRC = BASE / "static" / "scorm"
SCORM_TRANSLATED = BASE / "static" / "scorm_translated"
ZIPS = BASE / "zips"
METADATA = BASE / "metadata.json"
TEMP_AUDIO = BASE / "temp_audio"

# Ensure directories exist
for p in (UPLOADS, SCORM_SRC, SCORM_TRANSLATED, ZIPS, TEMP_AUDIO):
    p.mkdir(parents=True, exist_ok=True)


@app.route("/progress/<pkg_id>")
def get_progress_route(pkg_id):
    """Return JSON progress for a given course"""
    return jsonify(get_progress(pkg_id))


# ── Translation utils ──────────────────────────────────────
LANGS = {
    "English": "en", "French": "fr", "German": "de",
    "Hindi": "hi", "Russian": "ru", "Japanese": "ja",
    "Chinese": "zh-cn", "Spanish": "es", "Italian": "it",
    "Portuguese": "pt", "Korean": "ko", "Arabic": "ar"
}

# gTTS language codes
GTTS_LANGS = {
    "en": "en", "fr": "fr", "de": "de", "hi": "hi",
    "ru": "ru", "ja": "ja", "zh-cn": "zh-cn", "es": "es",
    "it": "it", "pt": "pt", "ko": "ko", "ar": "ar"
}

# safe translator wrapper
def do_translate(txt, tgt):
    """Wrapper around GoogleTranslator"""
    if not txt or not txt.strip():
        return txt
    try:
        # ✅ The method is .translate(), NOT .do_translate()
        return GoogleTranslator(source="auto", target=tgt).translate(txt)
    except Exception as e:
        print(f"⚠ Translation error (GoogleTranslator): {e}")
        return txt



# Flexible text patterns in SCORM files (kept conservative)
PATTERNS = [
    re.compile(r'(["\'](altText|title|text|label|caption|description|heading|content)["\']\s*:\s*["\'])([^"\']+)(["\'])'),
    re.compile(r'(>\s*)([^<]{2,})(\s*<)'),  # Capture text between HTML tags
    re.compile(r'(["\'])([A-Za-z0-9 ,.!?;:\-\']{3,})(["\'])')  # General fallback
]

EXCLUDED = {"data.js", "frame.js", "paths.js", "configuration.js"}
AUDIO_EXTENSIONS = {'.mp3', '.wav', '.ogg', '.m4a', '.flac', '.aac'}


# ── Metadata management ─────────────────────────────────────
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


# ── Audio translation ───────────────────────────────────────
def transcribe_audio(audio_path: Path) -> str:
    """Convert audio to text using speech_recognition (Google)"""
    recognizer = sr.Recognizer()
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
            try:
                temp_wav.unlink()
            except Exception:
                pass


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
    """Full audio translation pipeline"""
    try:
        print(f"Processing audio: {audio_path.name}")
        original_text = transcribe_audio(audio_path)
        if not original_text:
            print(f"  - Could not transcribe audio")
            return False

        print(f"  - Transcribed: {original_text[:50]}...")
        translated_text = do_translate(original_text, target_lang)
        print(f"  - Translated: {translated_text[:50]}...")

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


# ── Core functions ──────────────────────────────────────────
def extract_zip(src: Path, dest: Path):
    with zipfile.ZipFile(src) as z:
        z.extractall(dest)


def zip_dir(src_dir: Path, zip_path: Path):
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for p in src_dir.rglob("*"):
            if p.is_file():
                z.write(p, p.relative_to(src_dir))


def find_launch_file_from_manifest(course_folder: Path):
    """
    Parse imsmanifest.xml to find the official launch HTML file.
    Returns a Path if found, else None.
    """
    manifest_path = None
    for root, dirs, files in os.walk(course_folder):
        for f in files:
            if f.lower() == "imsmanifest.xml":
                manifest_path = Path(root) / f
                break
        if manifest_path:
            break

    if not manifest_path or not manifest_path.exists():
        print(f"⚠ No imsmanifest.xml found in {course_folder}")
        return None

    try:
        tree = ET.parse(manifest_path)
        root = tree.getroot()

        # Find the <resource> element that defines the SCORM entry point
        for resource in root.findall(".//{*}resource"):
            href = resource.attrib.get("href")
            if href:
                launch_file = (manifest_path.parent / href).resolve()
                if launch_file.exists():
                    print(f"✅ Launch file found via manifest: {launch_file}")
                    return launch_file
        print(f"⚠ No href attribute found in manifest resources.")
    except Exception as e:
        print(f"⚠ Error parsing imsmanifest.xml: {e}")

    return None


def translate_storyline_js(js_path: Path, lang_code: str):
    """Translate text inside Storyline JS or HTML files"""
    if js_path.name in EXCLUDED:
        return

    try:
        text = js_path.read_text("utf-8", errors="ignore")
        translations_made = 0

        def do(match):
            nonlocal translations_made
            # choose correct group if pattern varies
            src = None
            groups = match.groups()
            if len(groups) >= 3:
                src = groups[2]
            elif len(groups) >= 2:
                src = groups[1]
            else:
                src = match.group(0)

            if not src or len(src.strip()) < 3 or not any(c.isalpha() for c in src):
                return match.group(0)

            try:
                tgt = do_translate(src, lang_code)
                if tgt and tgt != src:
                    translations_made += 1
                    # reconstruct replacement conservative way
                    prefix = match.group(1) if len(groups) >= 3 else ''
                    suffix = match.group(4) if len(groups) >= 4 else ''
                    return prefix + tgt + suffix
            except Exception as e:
                print(f"⚠ Translation error in {js_path.name}: {e}")
            return match.group(0)

        for pat in PATTERNS:
            text = pat.sub(do, text)

        if translations_made > 0:
            js_path.write_text(text, "utf-8")
            print(f"✓ Translated {translations_made} text blocks in {js_path.name}")

    except Exception as e:
        print(f"Error processing {js_path.name}: {e}")


# ── Background worker used by /translate route ─────────────
def background_translate(pkg_id, lang_name, target_lang, translate_audio):
    try:
        src_dir = SCORM_SRC / pkg_id
        tgt_dir = SCORM_TRANSLATED / f"{pkg_id}_{target_lang}"

        if not src_dir.exists():
            set_progress(pkg_id, "Source not found", 0)
            return

        set_progress(pkg_id, "Copying course files for translation...", 5)
        if tgt_dir.exists():
            shutil.rmtree(tgt_dir)
        shutil.copytree(src_dir, tgt_dir)

        # Text translation
        set_progress(pkg_id, "Translating text files...", 15)
        js_root = tgt_dir / "story_content"
        if not js_root.exists():
            js_root = tgt_dir / "scormcontent"
        if not js_root.exists():
            js_root = tgt_dir

        js_files = list(js_root.rglob("*.js"))
        total_js = len(js_files)
        for i, js in enumerate(js_files, 1):
            translate_storyline_js(js, target_lang)
            percent = 15 + int(i / max(total_js, 1) * 40)
            set_progress(pkg_id, f"Translated {i}/{total_js} JS files...", percent)

        # Audio translation
        audio_count = 0
        if translate_audio:
            audio_files = find_audio_files(tgt_dir)
            total_audio = len(audio_files)
            if total_audio > 0:
                for i, audio_file in enumerate(audio_files, 1):
                    set_progress(pkg_id, f"Translating audio {i}/{total_audio}...", 60 + int(i / max(total_audio, 1) * 30))
                    output_path = audio_file
                    backup_path = audio_file.with_suffix(audio_file.suffix + '.original')
                    try:
                        shutil.copy2(audio_file, backup_path)
                    except Exception:
                        pass
                    success = translate_audio_file(audio_file, target_lang, output_path)
                    if success:
                        audio_count += 1
                        try:
                            backup_path.unlink()
                        except Exception:
                            pass
                    else:
                        try:
                            shutil.copy2(backup_path, audio_file)
                            backup_path.unlink()
                        except Exception:
                            pass

        set_progress(pkg_id, "Packaging translated SCORM...", 95)
        out_zip = ZIPS / f"{pkg_id}_{target_lang}.zip"
        zip_dir(tgt_dir, out_zip)

        add_translation_metadata(pkg_id, target_lang, lang_name, audio_count)
        set_progress(pkg_id, f"Translation complete ✅ ({lang_name})", 100)
        # keep complete state visible briefly
        time.sleep(2)
        set_progress(pkg_id, "Idle", 0)

    except Exception as e:
        print(f"Error in background_translate: {e}")
        set_progress(pkg_id, f"Error: {e}", 0)


# ── Routes ─────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html", languages=LANGS.keys())


@app.route("/library")
def library():
    meta = load_metadata()
    courses = []
    for pkg_id, info in meta.items():
        courses.append({
            'id': pkg_id,
            'name': info.get('original_name', 'Unknown'),
            'uploaded_at': info.get('uploaded_at', ''),
            'translations': info.get('translations', {})
        })
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

    original_name = Path(file.filename).stem
    pkg_id = f"{original_name}-{uuid.uuid4().hex[:5]}"
    src_dir = SCORM_SRC / pkg_id
    src_dir.mkdir(parents=True, exist_ok=True)

    zip_path = UPLOADS / f"{pkg_id}.zip"
    file.save(zip_path)

    try:
        extract_zip(zip_path, src_dir)
        print(f"✓ Extracted SCORM package to: {src_dir}")
    except Exception as e:
        flash(f"Error extracting ZIP file: {e}", "error")
        return redirect("/")

    add_course_metadata(pkg_id, file.filename, original_name)
    flash(f"Successfully uploaded: {original_name}", "success")
    return redirect(url_for("library"))


@app.route("/translate", methods=["POST"])
def translate():
    # Kick off background translation and return immediately
    pkg_id = request.form.get("pkg_id")
    lang_name = request.form.get("language")
    target_lang = LANGS.get(lang_name, "en")
    translate_audio = request.form.get("translate_audio") == "on"

    if not pkg_id or not lang_name:
        flash("Missing course ID or language.", "error")
        return redirect(url_for("library"))

    # Start background worker
    t = threading.Thread(target=background_translate, args=(pkg_id, lang_name, target_lang, translate_audio), daemon=True)
    t.start()

    flash(f"Started background translation for {lang_name}.", "info")
    return redirect(url_for("library"))


@app.route("/play")
def play():
    pkg = request.args.get("pkg")
    lang = request.args.get("lang", "en")

    if not pkg:
        flash("No course specified.", "error")
        return redirect(url_for("library"))

    folder = SCORM_TRANSLATED / f"{pkg}_{lang}" if lang != "en" else SCORM_SRC / pkg
    if not folder.exists():
        flash("Course folder not found.", "error")
        return redirect(url_for("library"))

    # 1️⃣ Try manifest-based launch detection first
    launch = find_launch_file_from_manifest(folder)

    # 2️⃣ Fallback to scanning for common HTML entry files
    if not launch:
        launch_candidates = {"index_lms.html", "index.html", "story.html", "launch.html", "player.html"}
        for root, _, files in os.walk(folder):
            for f in files:
                if f.lower() in launch_candidates:
                    launch = Path(root) / f
                    break
            if launch:
                break

    if not launch:
        flash(f"No valid launch file found in {folder.name}", "error")
        return redirect(url_for("library"))

    # Build relative URL for rendering in iframe
    rel_path = launch.relative_to(BASE / "static")
    course_url = f"/static/{rel_path}".replace("\\", "/")

    meta = load_metadata()
    course_info = meta.get(pkg, {})

    return render_template(
        "player.html",
        course_url=course_url,
        pkg=pkg,
        lang=lang,
        languages=LANGS,
        course_info=course_info
    )


@app.route('/download/<zipname>')
def download(zipname):
    zip_path = ZIPS / zipname
    if not zip_path.exists():
        flash("Download file not found.", "error")
        return redirect(url_for("library"))
    return send_file(zip_path, as_attachment=True)


@app.route('/delete/<pkg>', methods=['POST'])
def delete(pkg):
    # Delete source folder
    src_dir = SCORM_SRC / pkg
    if src_dir.exists():
        shutil.rmtree(src_dir)

    # Delete all translations
    for trans_dir in SCORM_TRANSLATED.glob(f"{pkg}_*"):
        shutil.rmtree(trans_dir)

    # Delete zip files
    for zip_file in ZIPS.glob(f"{pkg}_*.zip"):
        try:
            zip_file.unlink()
        except Exception:
            pass

    # Update metadata
    meta = load_metadata()
    if pkg in meta:
        del meta[pkg]
        save_metadata(meta)

    flash("Course deleted successfully.", "success")
    return redirect(url_for("library"))


@app.route('/translate-node', methods=['POST'])
def translate_node():
    d = request.get_json(force=True)
    txt = d.get('text', '')
    tgt = d.get('target', 'fr')
    return jsonify({'t': do_translate(txt, tgt)})


@app.route('/test-translation')
def test_translation():
    try:
        test_text = "Hello, this is a test"
        result = do_translate(test_text, "fr")
        return jsonify({
            'success': True,
            'original': test_text,
            'translated': result,
            'target_language': 'French'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


if __name__ == '__main__':
    app.run(debug=True, port=5000)
>>>>>>> 5a4cb7880bd31b448b510e9a72ecd28586840cf6
=======
@app.route('/debug-translate/<lang>')
def debug_translate(lang):
    try:
        sample = "Welcome to the training course"
        translated = translate_text(sample, lang)
        return jsonify({
            "source": sample,
            "target_lang": lang,
            "translated": translated
        })
    except Exception as e:
        return jsonify({"error": str(e)})



if __name__ == '__main__':
    app.run(debug=True, port=5000)
>>>>>>> 0b1e9e43 (SCORM Audio Translation)
