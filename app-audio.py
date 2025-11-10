import os
import shutil
import zipfile
import uuid
import json
import re
import threading
import time
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
import xml.etree.ElementTree as ET
from threading import Lock

# ─────────────────────────────
# CONFIGURATION
# ─────────────────────────────
AUDIO_ONLY = True  # 🔊 Enable Audio-Only Build

progress = {}
progress_lock = Lock()

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

# ─────────────────────────────
# LANGUAGE MAPS
# ─────────────────────────────
LANGS = {
    "English": "en", "French": "fr", "German": "de",
    "Hindi": "hi", "Russian": "ru", "Japanese": "ja",
    "Chinese": "zh-cn", "Spanish": "es", "Italian": "it",
    "Portuguese": "pt", "Korean": "ko", "Arabic": "ar"
}

GTTS_LANGS = {
    "en": "en", "fr": "fr", "de": "de", "hi": "hi",
    "ru": "ru", "ja": "ja", "zh-cn": "zh-cn", "es": "es",
    "it": "it", "pt": "pt", "ko": "ko", "ar": "ar"
}


# ─────────────────────────────
# PROGRESS TRACKING
# ─────────────────────────────
def set_progress(pkg_id, message, percent=None):
    with progress_lock:
        progress[pkg_id] = {"message": message, "percent": percent or 0}


def get_progress(pkg_id):
    with progress_lock:
        return progress.get(pkg_id, {"message": "Idle", "percent": 0})


@app.route("/progress/<pkg_id>")
def get_progress_route(pkg_id):
    return jsonify(get_progress(pkg_id))


# ─────────────────────────────
# TRANSLATION UTILITIES
# ─────────────────────────────
def translate(txt, tgt):
    """Wrapper around GoogleTranslator (safe)."""
    if not txt or not txt.strip():
        return txt
    try:
        return GoogleTranslator(source="auto", target=tgt).translate(txt)
    except Exception as e:
        print(f"⚠ Translation error (GoogleTranslator): {e}")
        return txt


# ─────────────────────────────
# METADATA MANAGEMENT
# ─────────────────────────────
def load_metadata():
    if METADATA.exists():
        try:
            with open(METADATA, "r") as f:
                data = f.read().strip()
                return json.loads(data) if data else {}
        except Exception as e:
            print(f"⚠ Corrupted metadata: {e}")
            return {}
    return {}


def save_metadata(data):
    try:
        with open(METADATA, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"⚠ Error saving metadata: {e}")


def add_course_metadata(pkg_id, filename, original_name):
    meta = load_metadata()
    if pkg_id not in meta:
        meta[pkg_id] = {
            "id": pkg_id,
            "original_name": original_name,
            "filename": filename,
            "uploaded_at": datetime.now().isoformat(),
            "translations": {},
        }
        save_metadata(meta)
    return meta[pkg_id]


def add_translation_metadata(pkg_id, lang_code, lang_name, audio_count=0):
    meta = load_metadata()
    if pkg_id in meta:
        meta[pkg_id]["translations"][lang_code] = {
            "language": lang_name,
            "created_at": datetime.now().isoformat(),
            "zip_file": f"{pkg_id}_{lang_code}.zip",
            "audio_files_translated": audio_count,
        }
        save_metadata(meta)


# ─────────────────────────────
# AUDIO TRANSLATION
# ─────────────────────────────
AUDIO_EXTENSIONS = {".mp3", ".wav", ".ogg", ".m4a", ".flac", ".aac"}


def transcribe_audio(audio_path: Path) -> str:
    """Convert audio to text using Google Speech Recognition."""
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
        print(f"⚠ Error transcribing {audio_path.name}: {e}")
        return ""
    finally:
        if temp_wav.exists():
            try:
                temp_wav.unlink()
            except:
                pass


def text_to_speech(text: str, lang_code: str, output_path: Path):
    """Convert text to speech in target language."""
    try:
        lang = GTTS_LANGS.get(lang_code, "en")
        tts = gTTS(text=text, lang=lang, slow=False)
        tts.save(str(output_path))
        return True
    except Exception as e:
        print(f"⚠ Error generating speech: {e}")
        return False


def translate_audio_file(audio_path: Path, target_lang: str, output_path: Path) -> bool:
    """Full audio translation pipeline."""
    try:
        print(f"🎧 Processing audio: {audio_path.name}")
        original_text = transcribe_audio(audio_path)
        if not original_text:
            print("  - Skipped (no transcription)")
            return False

        print(f"  - Transcribed: {original_text[:80]}...")
        translated_text = translate(original_text, target_lang)
        if translated_text == original_text:
            print("  - Translation unchanged (fallback to original).")

        success = text_to_speech(translated_text, target_lang, output_path)
        if success:
            print("  ✓ Audio translated successfully.")
        return success
    except Exception as e:
        print(f"⚠ Error translating audio {audio_path.name}: {e}")
        return False


def find_audio_files(directory: Path) -> list:
    """Find all audio files in directory recursively."""
    audio_files = []
    for ext in AUDIO_EXTENSIONS:
        audio_files.extend(directory.rglob(f"*{ext}"))
    return audio_files


# ─────────────────────────────
# ZIP UTILITIES
# ─────────────────────────────
def extract_zip(src: Path, dest: Path):
    with zipfile.ZipFile(src) as z:
        z.extractall(dest)


def zip_dir(src_dir: Path, zip_path: Path):
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for p in src_dir.rglob("*"):
            if p.is_file():
                z.write(p, p.relative_to(src_dir))


# ─────────────────────────────
# MANIFEST-BASED LAUNCH DETECTION
# ─────────────────────────────
def find_launch_file_from_manifest(course_folder: Path):
    for root, dirs, files in os.walk(course_folder):
        for f in files:
            if f.lower() == "imsmanifest.xml":
                manifest_path = Path(root) / f
                break
        else:
            continue
        break
    else:
        print(f"⚠ No imsmanifest.xml found in {course_folder}")
        return None

    try:
        tree = ET.parse(manifest_path)
        root = tree.getroot()
        for resource in root.findall(".//{*}resource"):
            href = resource.attrib.get("href")
            if href:
                launch = (manifest_path.parent / href).resolve()
                if launch.exists():
                    print(f"✅ Launch file found: {launch}")
                    return launch
    except Exception as e:
        print(f"⚠ Error parsing manifest: {e}")
    return None


# ─────────────────────────────
# BACKGROUND TRANSLATION THREAD
# ─────────────────────────────
def background_translate(pkg_id, lang_name, target_lang):
    try:
        src_dir = SCORM_SRC / pkg_id
        tgt_dir = SCORM_TRANSLATED / f"{pkg_id}_{target_lang}"

        if not src_dir.exists():
            set_progress(pkg_id, "Source not found", 0)
            return

        set_progress(pkg_id, "Copying course files...", 5)
        if tgt_dir.exists():
            shutil.rmtree(tgt_dir)
        shutil.copytree(src_dir, tgt_dir)

        # Audio-Only Mode
        print("🔇 Skipping text translation (Audio-Only Build).")
        set_progress(pkg_id, "Skipping text translation (audio-only mode)...", 15)
        time.sleep(1)

        # Audio translation
        audio_count = 0
        audio_files = find_audio_files(tgt_dir)
        total_audio = len(audio_files)
        print(f"🎧 Found {total_audio} audio files.")

        if total_audio > 0:
            for i, audio_file in enumerate(audio_files, 1):
                set_progress(pkg_id, f"Translating audio {i}/{total_audio}...", 20 + int(i / total_audio * 70))
                output_path = audio_file
                backup_path = audio_file.with_suffix(audio_file.suffix + ".original")
                try:
                    shutil.copy2(audio_file, backup_path)
                    if translate_audio_file(audio_file, target_lang, output_path):
                        audio_count += 1
                        backup_path.unlink(missing_ok=True)
                    else:
                        shutil.copy2(backup_path, audio_file)
                        backup_path.unlink(missing_ok=True)
                except Exception as e:
                    print(f"⚠ Audio translation error: {e}")

        set_progress(pkg_id, "Packaging translated SCORM...", 95)
        out_zip = ZIPS / f"{pkg_id}_{target_lang}.zip"
        zip_dir(tgt_dir, out_zip)

        add_translation_metadata(pkg_id, target_lang, lang_name, audio_count)
        set_progress(pkg_id, f"Audio translation complete ✅ ({lang_name})", 100)
        print(f"✅ Audio translation complete for {pkg_id} [{lang_name}]")

        time.sleep(2)
        set_progress(pkg_id, "Idle", 0)

    except Exception as e:
        print(f"❌ Error in background translation: {e}")
        set_progress(pkg_id, f"Error: {e}", 0)


# ─────────────────────────────
# FLASK ROUTES
# ─────────────────────────────
@app.route("/")
def index():
    return render_template("index.html", languages=LANGS.keys())


@app.route("/library")
def library():
    meta = load_metadata()
    courses = sorted(
        [
            {
                "id": k,
                "name": v.get("original_name", "Unknown"),
                "uploaded_at": v.get("uploaded_at", ""),
                "translations": v.get("translations", {}),
            }
            for k, v in meta.items()
        ],
        key=lambda x: x["uploaded_at"],
        reverse=True,
    )
    return render_template("library.html", courses=courses, languages=LANGS)


@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("scormZip")
    if not file or not file.filename.lower().endswith(".zip"):
        flash("Please upload a valid .zip SCORM package.", "error")
        return redirect("/")

    original_name = Path(file.filename).stem
    pkg_id = f"{original_name}-{uuid.uuid4().hex[:5]}"
    src_dir = SCORM_SRC / pkg_id
    src_dir.mkdir(parents=True, exist_ok=True)

    zip_path = UPLOADS / f"{pkg_id}.zip"
    file.save(zip_path)

    try:
        extract_zip(zip_path, src_dir)
    except Exception as e:
        flash(f"Error extracting ZIP: {e}", "error")
        return redirect("/")

    add_course_metadata(pkg_id, file.filename, original_name)
    flash(f"Uploaded successfully: {original_name}", "success")
    return redirect(url_for("library"))


@app.route("/translate", methods=["POST"])
def translate_route():
    pkg_id = request.form.get("pkg_id")
    lang_name = request.form.get("language")
    target_lang = LANGS.get(lang_name, "en")

    if not pkg_id or not lang_name:
        flash("Missing course ID or language.", "error")
        return redirect(url_for("library"))

    threading.Thread(
        target=background_translate, args=(pkg_id, lang_name, target_lang), daemon=True
    ).start()

    flash(f"Started background audio translation for {lang_name}.", "info")
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
        flash("Course not found.", "error")
        return redirect(url_for("library"))

    launch = find_launch_file_from_manifest(folder)
    if not launch:
        for root, _, files in os.walk(folder):
            for f in files:
                if f.lower() in {"index.html", "story.html", "launch.html"}:
                    launch = Path(root) / f
                    break
            if launch:
                break

    if not launch:
        flash("No valid launch file found.", "error")
        return redirect(url_for("library"))

    rel = launch.relative_to(BASE / "static")
    course_url = f"/static/{rel}".replace("\\", "/")

    meta = load_metadata()
    info = meta.get(pkg, {})

    return render_template("player.html", course_url=course_url, pkg=pkg, lang=lang, course_info=info)


@app.route("/download/<zipname>")
def download(zipname):
    zip_path = ZIPS / zipname
    if not zip_path.exists():
        flash("File not found.", "error")
        return redirect(url_for("library"))
    return send_file(zip_path, as_attachment=True)


@app.route("/delete/<pkg>", methods=["POST"])
def delete(pkg):
    for folder in [SCORM_SRC / pkg, *SCORM_TRANSLATED.glob(f"{pkg}_*")]:
        if folder.exists():
            shutil.rmtree(folder)

    for z in ZIPS.glob(f"{pkg}_*.zip"):
        try:
            z.unlink()
        except:
            pass

    meta = load_metadata()
    if pkg in meta:
        del meta[pkg]
        save_metadata(meta)

    flash("Course deleted successfully.", "success")
    return redirect(url_for("library"))


# ─────────────────────────────
# ENTRY POINT
# ─────────────────────────────
if __name__ == "__main__":
    app.run(debug=True, port=5000)
