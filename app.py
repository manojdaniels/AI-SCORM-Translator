ChatGPT Suggested app.py for Indian version. 




import os
import shutil
import zipfile
import uuid
import json
import threading
import time
from pathlib import Path
from datetime import datetime

from flask import (
    Flask, render_template, request, redirect, url_for,
    flash, send_file, jsonify
)

import speech_recognition as sr
from gtts import gTTS
from pydub import AudioSegment
import xml.etree.ElementTree as ET
from threading import Lock

# ───────────────────────────────────────────────
# CONFIGURATION
# ───────────────────────────────────────────────
AUDIO_ONLY = True  # ✔ AUDIO-ONLY BUILD

app = Flask(__name__)
app.secret_key = "change-me"

BASE = Path(__file__).parent
UPLOADS = BASE / "uploads"
SCORM_SRC = BASE / "static" / "scorm"
SCORM_TRANSLATED = BASE / "static" / "scorm_translated"
ZIPS = BASE / "zips"
METADATA = BASE / "metadata.json"
TEMP_AUDIO = BASE / "temp_audio"

for p in (UPLOADS, SCORM_SRC, SCORM_TRANSLATED, ZIPS, TEMP_AUDIO):
    p.mkdir(parents=True, exist_ok=True)

progress = {}
progress_lock = Lock()

# ───────────────────────────────────────────────
# INDIAN LANGUAGES ONLY 🇮🇳
# ───────────────────────────────────────────────
LANGS = {
    "Hindi (हिन्दी)": "hi",
    "Punjabi (ਪੰਜਾਬੀ)": "pa",
    "Tamil (தமிழ்)": "ta",
    "Telugu (తెలుగు)": "te",
    "Kannada (ಕನ್ನಡ)": "kn",
    "Malayalam (മലയാളം)": "ml",
    "Gujarati (ગુજરાતી)": "gu",
    "Marathi (मराठी)": "mr",
    "Bengali (বাংলা)": "bn",
    "Urdu (اردو)": "ur"
}

GTTS_LANGS = {
    "hi": "hi", "pa": "pa", "ta": "ta",
    "te": "te", "kn": "kn", "ml": "ml",
    "gu": "gu", "mr": "mr", "bn": "bn",
    "ur": "ur"
}

AUDIO_EXTENSIONS = {".mp3", ".wav", ".ogg", ".m4a", ".flac", ".aac"}

# ───────────────────────────────────────────────
# PROGRESS HELPERS
# ───────────────────────────────────────────────
def set_progress(pkg_id, message, percent):
    with progress_lock:
        progress[pkg_id] = {"message": message, "percent": percent}


@app.route("/progress/<pkg_id>")
def progress_route(pkg_id):
    with progress_lock:
        return jsonify(progress.get(pkg_id, {"message": "Idle", "percent": 0}))


# ───────────────────────────────────────────────
# METADATA
# ───────────────────────────────────────────────
def load_metadata():
    if not METADATA.exists():
        return {}
    try:
        return json.loads(METADATA.read_text())
    except:
        return {}


def save_metadata(data):
    METADATA.write_text(json.dumps(data, indent=2))


def add_course_metadata(pkg_id, filename, original_name):
    meta = load_metadata()
    meta[pkg_id] = {
        "id": pkg_id,
        "original_name": original_name,
        "filename": filename,
        "uploaded_at": datetime.now().isoformat(),
        "translations": {}
    }
    save_metadata(meta)


def add_translation_metadata(pkg_id, lang_code, lang_name, audio_count):
    meta = load_metadata()
    if pkg_id not in meta:
        return
    meta[pkg_id]["translations"][lang_code] = {
        "language": lang_name,
        "created_at": datetime.now().isoformat(),
        "zip_file": f"{pkg_id}_{lang_code}.zip",
        "audio_files_translated": audio_count
    }
    save_metadata(meta)


# ───────────────────────────────────────────────
# AUDIO UTILITIES
# ───────────────────────────────────────────────
def transcribe_audio(path: Path) -> str:
    recognizer = sr.Recognizer()
    temp_wav = TEMP_AUDIO / f"{uuid.uuid4().hex}.wav"
    try:
        AudioSegment.from_file(path).export(temp_wav, format="wav")
        with sr.AudioFile(str(temp_wav)) as src:
            audio = recognizer.record(src)
            return recognizer.recognize_google(audio)
    except Exception as e:
        print(f"[ERROR] Transcription failed: {e}")
        return ""
    finally:
        temp_wav.unlink(missing_ok=True)


def tts_generate(text: str, lang: str, output: Path) -> bool:
    try:
        gtts_lang = GTTS_LANGS.get(lang, "hi")
        gTTS(text=text, lang=gtts_lang, slow=False).save(output)
        return True
    except Exception as e:
        print(f"[ERROR] TTS failed: {e}")
        return False


def translate_audio_file(input_audio: Path, target_lang: str) -> bool:
    print(f"🎧 Processing: {input_audio.name}")
    text = transcribe_audio(input_audio)
    if not text:
        print("  - No speech detected, skipping")
        return False

    output_path = input_audio  # overwrite original
    return tts_generate(text, target_lang, output_path)


# ───────────────────────────────────────────────
# ZIP HELPERS
# ───────────────────────────────────────────────
def extract_zip(src: Path, dest: Path):
    with zipfile.ZipFile(src) as z:
        z.extractall(dest)


def zip_dir(src: Path, out_zip: Path):
    with zipfile.ZipFile(out_zip, "w", zipfile.ZIP_DEFLATED) as z:
        for f in src.rglob("*"):
            if f.is_file():
                z.write(f, f.relative_to(src))


# ───────────────────────────────────────────────
# SCORM LAUNCH DETECTOR
# ───────────────────────────────────────────────
def find_launch_file(folder: Path):
    # Look for imsmanifest.xml
    manifest = None
    for r, _, files in os.walk(folder):
        for f in files:
            if f.lower() == "imsmanifest.xml":
                manifest = Path(r) / f
                break
        if manifest:
            break

    # Try reading manifest
    if manifest and manifest.exists():
        try:
            tree = ET.parse(manifest)
            root = tree.getroot()
            for res in root.findall(".//{*}resource"):
                href = res.attrib.get("href")
                if href:
                    candidate = (manifest.parent / href).resolve()
                    if candidate.exists():
                        return candidate
        except:
            pass

    # Fallback
    COMMON = {"index.html", "story.html", "launch.html", "index_lms.html"}
    for r, _, files in os.walk(folder):
        for f in files:
            if f.lower() in COMMON:
                return Path(r) / f

    return None


# ───────────────────────────────────────────────
# BACKGROUND AUDIO TRANSLATION THREAD
# ───────────────────────────────────────────────
def worker_translate(pkg_id, lang_name, target_lang):
    try:
        src = SCORM_SRC / pkg_id
        tgt = SCORM_TRANSLATED / f"{pkg_id}_{target_lang}"

        if tgt.exists():
            shutil.rmtree(tgt)
        shutil.copytree(src, tgt)

        # Audio work
        audio_files = [p for p in tgt.rglob("*") if p.suffix.lower() in AUDIO_EXTENSIONS]
        total = len(audio_files)
        count = 0

        for i, audio in enumerate(audio_files, 1):
            set_progress(pkg_id, f"Processing audio {i}/{total}", int(i / total * 90))
            if translate_audio_file(audio, target_lang):
                count += 1

        # Package
        out_zip = ZIPS / f"{pkg_id}_{target_lang}.zip"
        set_progress(pkg_id, "Packaging...", 95)
        zip_dir(tgt, out_zip)

        add_translation_metadata(pkg_id, target_lang, lang_name, count)
        set_progress(pkg_id, f"Complete ✔ ({lang_name})", 100)
        time.sleep(3)
        set_progress(pkg_id, "Idle", 0)

    except Exception as e:
        print("Worker error:", e)
        set_progress(pkg_id, f"Error: {e}", 0)


# ───────────────────────────────────────────────
# ROUTES
# ───────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html", languages=LANGS.keys())


@app.route("/library")
def library():
    meta = load_metadata()
    courses = [{
        "id": k,
        "name": v["original_name"],
        "uploaded_at": v["uploaded_at"],
        "translations": v["translations"]
    } for k, v in meta.items()]
    courses.sort(key=lambda x: x["uploaded_at"], reverse=True)
    return render_template("library.html", courses=courses, languages=LANGS)


@app.route("/upload", methods=["POST"])
def upload():
    f = request.files.get("scormZip")
    if not f or not f.filename.lower().endswith(".zip"):
        flash("Please upload a valid .zip SCORM package.", "error")
        return redirect("/")

    pkg_id = f"{Path(f.filename).stem}-{uuid.uuid4().hex[:5]}"
    zip_path = UPLOADS / f"{pkg_id}.zip"
    f.save(zip_path)

    src_folder = SCORM_SRC / pkg_id
    src_folder.mkdir()

    extract_zip(zip_path, src_folder)

    add_course_metadata(pkg_id, f.filename, Path(f.filename).stem)

    flash("SCORM uploaded successfully!", "success")
    return redirect(url_for("library"))


@app.route("/translate", methods=["POST"])
def translate():
    pkg_id = request.form.get("pkg_id")
    lang_name = request.form.get("language")
    target_lang = LANGS.get(lang_name)

    if not pkg_id or not target_lang:
        flash("Invalid request.", "error")
        return redirect(url_for("library"))

    threading.Thread(
        target=worker_translate,
        args=(pkg_id, lang_name, target_lang),
        daemon=True
    ).start()

    flash(f"Started audio translation into {lang_name}", "info")
    return redirect(url_for("library"))


@app.route("/play")
def play():
    pkg = request.args.get("pkg")
    lang = request.args.get("lang", "en")

    folder = SCORM_TRANSLATED / f"{pkg}_{lang}" if lang != "en" else SCORM_SRC / pkg
    launch = find_launch_file(folder)

    if not launch:
        flash("Launch file not found.", "error")
        return redirect(url_for("library"))

    rel = launch.relative_to(BASE / "static")
    return render_template("player.html", course_url=f"/static/{rel}")


@app.route("/download/<zipname>")
def download(zipname):
    path = ZIPS / zipname
    return send_file(path, as_attachment=True)


@app.route("/delete/<pkg>", methods=["POST"])
def delete(pkg):
    shutil.rmtree(SCORM_SRC / pkg, ignore_errors=True)
    for t in SCORM_TRANSLATED.glob(f"{pkg}_*"):
        shutil.rmtree(t, ignore_errors=True)
    for z in ZIPS.glob(f"{pkg}_*.zip"):
        z.unlink(missing_ok=True)

    meta = load_metadata()
    meta.pop(pkg, None)
    save_metadata(meta)

    flash("Course deleted.", "success")
    return redirect(url_for("library"))


# ───────────────────────────────────────────────
# ENTRY POINT
# ───────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True, port=5000)
