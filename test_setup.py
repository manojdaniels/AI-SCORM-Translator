<<<<<<< HEAD
#!/usr/bin/env python3
"""
SCORM Audio Translator - Setup Verification Script
Run this to check if all dependencies are properly installed
"""

import sys
import subprocess
from pathlib import Path

def print_header(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")

def check_python_version():
    """Check Python version"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    print(f"   Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major >= 3 and version.minor >= 8:
        print("   ✅ Python version OK (>= 3.8)")
        return True
    else:
        print("   ❌ Python version too old (need >= 3.8)")
        return False

def check_ffmpeg():
    """Check if FFmpeg is installed"""
    print("\n🎬 Checking FFmpeg installation...")
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, 
                              text=True, 
                              timeout=5)
        version_line = result.stdout.split('\n')[0]
        print(f"   {version_line}")
        print("   ✅ FFmpeg is installed")
        return True
    except FileNotFoundError:
        print("   ❌ FFmpeg NOT found")
        print("   📝 Install instructions:")
        print("      Windows: choco install ffmpeg  OR  download from ffmpeg.org")
        print("      Mac: brew install ffmpeg")
        print("      Linux: sudo apt install ffmpeg")
        return False
    except Exception as e:
        print(f"   ⚠️  Error checking FFmpeg: {e}")
        return False

def check_package(package_name, import_name=None):
    """Check if a Python package is installed"""
    if import_name is None:
        import_name = package_name
    
    try:
        __import__(import_name)
        print(f"   ✅ {package_name}")
        return True
    except ImportError:
        print(f"   ❌ {package_name} NOT installed")
        return False

def check_python_packages():
    """Check all required Python packages"""
    print("\n📦 Checking Python packages...")
    
    packages = {
        'Flask': 'flask',
        'deep-translator': 'deep_translator',
        'gTTS': 'gtts',
        'SpeechRecognition': 'speech_recognition',
        'pydub': 'pydub',
        'Werkzeug': 'werkzeug'
    }
    
    results = []
    for display_name, import_name in packages.items():
        results.append(check_package(display_name, import_name))
    
    return all(results)

def check_directories():
    """Check if required directories exist"""
    print("\n📁 Checking directories...")
    
    base = Path.cwd()
    required_dirs = ['uploads', 'static/scorm', 'static/scorm_translated', 
                     'zips', 'temp_audio', 'templates']
    
    results = []
    for dir_path in required_dirs:
        full_path = base / dir_path
        if full_path.exists():
            print(f"   ✅ {dir_path}")
            results.append(True)
        else:
            print(f"   ⚠️  {dir_path} (will be auto-created)")
            results.append(True)  # Not critical, will be created
    
    return all(results)

def check_templates():
    """Check if template files exist"""
    print("\n📄 Checking template files...")
    
    base = Path.cwd()
    templates = ['templates/index.html', 'templates/library.html', 
                 'templates/player.html']
    
    results = []
    for template in templates:
        full_path = base / template
        if full_path.exists():
            print(f"   ✅ {template}")
            results.append(True)
        else:
            print(f"   ❌ {template} NOT found")
            results.append(False)
    
    return all(results)

def test_translations():
    """Test translation functionality"""
    print("\n🌍 Testing translation services...")
    
    try:
        from deep_translator import GoogleTranslator
        translator = GoogleTranslator(source='en', target='fr')
        result = translator.translate('Hello World')
        print(f"   Test: 'Hello World' → '{result}'")
        print("   ✅ Translation service working")
        return True
    except Exception as e:
        print(f"   ❌ Translation test failed: {e}")
        print("   ⚠️  Check internet connection")
        return False

def test_tts():
    """Test text-to-speech"""
    print("\n🔊 Testing text-to-speech...")
    
    try:
        from gtts import gTTS
        import tempfile
        
        with tempfile.NamedTemporaryFile(delete=True, suffix='.mp3') as tmp:
            tts = gTTS(text='Test', lang='en')
            tts.save(tmp.name)
            print("   ✅ Text-to-speech working")
            return True
    except Exception as e:
        print(f"   ❌ TTS test failed: {e}")
        return False

def test_audio_conversion():
    """Test audio conversion with pydub"""
    print("\n🎵 Testing audio conversion...")
    
    try:
        from pydub import AudioSegment
        from pydub.generators import Sine
        
        # Generate a test tone
        sound = Sine(440).to_audio_segment(duration=100)
        print("   ✅ Audio conversion working (pydub + ffmpeg)")
        return True
    except Exception as e:
        print(f"   ❌ Audio conversion failed: {e}")
        print("   ⚠️  This likely means FFmpeg is not properly installed")
        return False

def main():
    """Run all tests"""
    print_header("SCORM Audio Translator - Setup Verification")
    print("This script will check if your system is ready to run the application.\n")
    
    results = {
        'Python Version': check_python_version(),
        'FFmpeg': check_ffmpeg(),
        'Python Packages': check_python_packages(),
        'Directories': check_directories(),
        'Templates': check_templates(),
        'Translation Service': test_translations(),
        'Text-to-Speech': test_tts(),
        'Audio Conversion': test_audio_conversion()
    }
    
    print_header("Summary")
    
    passed = sum(results.values())
    total = len(results)
    
    for check, status in results.items():
        icon = "✅" if status else "❌"
        print(f"{icon} {check}")
    
    print(f"\n{'='*60}")
    print(f"  Results: {passed}/{total} checks passed")
    print(f"{'='*60}\n")
    
    if passed == total:
        print("🎉 All checks passed! Your system is ready.")
        print("\nNext step: Run the application")
        print("   python app.py")
        print("\nThen open: http://localhost:5000")
        return 0
    else:
        print("⚠️  Some checks failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("1. Install missing packages: pip install -r requirements.txt")
        print("2. Install FFmpeg (see setup instructions)")
        print("3. Create template files (see provided HTML files)")
        print("4. Check internet connection for translation services")
        return 1

if __name__ == '__main__':
=======
#!/usr/bin/env python3
"""
SCORM Audio Translator - Setup Verification Script
Run this to check if all dependencies are properly installed
"""

import sys
import subprocess
from pathlib import Path

def print_header(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")

def check_python_version():
    """Check Python version"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    print(f"   Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major >= 3 and version.minor >= 8:
        print("   ✅ Python version OK (>= 3.8)")
        return True
    else:
        print("   ❌ Python version too old (need >= 3.8)")
        return False

def check_ffmpeg():
    """Check if FFmpeg is installed"""
    print("\n🎬 Checking FFmpeg installation...")
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, 
                              text=True, 
                              timeout=5)
        version_line = result.stdout.split('\n')[0]
        print(f"   {version_line}")
        print("   ✅ FFmpeg is installed")
        return True
    except FileNotFoundError:
        print("   ❌ FFmpeg NOT found")
        print("   📝 Install instructions:")
        print("      Windows: choco install ffmpeg  OR  download from ffmpeg.org")
        print("      Mac: brew install ffmpeg")
        print("      Linux: sudo apt install ffmpeg")
        return False
    except Exception as e:
        print(f"   ⚠️  Error checking FFmpeg: {e}")
        return False

def check_package(package_name, import_name=None):
    """Check if a Python package is installed"""
    if import_name is None:
        import_name = package_name
    
    try:
        __import__(import_name)
        print(f"   ✅ {package_name}")
        return True
    except ImportError:
        print(f"   ❌ {package_name} NOT installed")
        return False

def check_python_packages():
    """Check all required Python packages"""
    print("\n📦 Checking Python packages...")
    
    packages = {
        'Flask': 'flask',
        'deep-translator': 'deep_translator',
        'gTTS': 'gtts',
        'SpeechRecognition': 'speech_recognition',
        'pydub': 'pydub',
        'Werkzeug': 'werkzeug'
    }
    
    results = []
    for display_name, import_name in packages.items():
        results.append(check_package(display_name, import_name))
    
    return all(results)

def check_directories():
    """Check if required directories exist"""
    print("\n📁 Checking directories...")
    
    base = Path.cwd()
    required_dirs = ['uploads', 'static/scorm', 'static/scorm_translated', 
                     'zips', 'temp_audio', 'templates']
    
    results = []
    for dir_path in required_dirs:
        full_path = base / dir_path
        if full_path.exists():
            print(f"   ✅ {dir_path}")
            results.append(True)
        else:
            print(f"   ⚠️  {dir_path} (will be auto-created)")
            results.append(True)  # Not critical, will be created
    
    return all(results)

def check_templates():
    """Check if template files exist"""
    print("\n📄 Checking template files...")
    
    base = Path.cwd()
    templates = ['templates/index.html', 'templates/library.html', 
                 'templates/player.html']
    
    results = []
    for template in templates:
        full_path = base / template
        if full_path.exists():
            print(f"   ✅ {template}")
            results.append(True)
        else:
            print(f"   ❌ {template} NOT found")
            results.append(False)
    
    return all(results)

def test_translations():
    """Test translation functionality"""
    print("\n🌍 Testing translation services...")
    
    try:
        from deep_translator import GoogleTranslator
        translator = GoogleTranslator(source='en', target='fr')
        result = translator.translate('Hello World')
        print(f"   Test: 'Hello World' → '{result}'")
        print("   ✅ Translation service working")
        return True
    except Exception as e:
        print(f"   ❌ Translation test failed: {e}")
        print("   ⚠️  Check internet connection")
        return False

def test_tts():
    """Test text-to-speech"""
    print("\n🔊 Testing text-to-speech...")
    
    try:
        from gtts import gTTS
        import tempfile
        
        with tempfile.NamedTemporaryFile(delete=True, suffix='.mp3') as tmp:
            tts = gTTS(text='Test', lang='en')
            tts.save(tmp.name)
            print("   ✅ Text-to-speech working")
            return True
    except Exception as e:
        print(f"   ❌ TTS test failed: {e}")
        return False

def test_audio_conversion():
    """Test audio conversion with pydub"""
    print("\n🎵 Testing audio conversion...")
    
    try:
        from pydub import AudioSegment
        from pydub.generators import Sine
        
        # Generate a test tone
        sound = Sine(440).to_audio_segment(duration=100)
        print("   ✅ Audio conversion working (pydub + ffmpeg)")
        return True
    except Exception as e:
        print(f"   ❌ Audio conversion failed: {e}")
        print("   ⚠️  This likely means FFmpeg is not properly installed")
        return False

def main():
    """Run all tests"""
    print_header("SCORM Audio Translator - Setup Verification")
    print("This script will check if your system is ready to run the application.\n")
    
    results = {
        'Python Version': check_python_version(),
        'FFmpeg': check_ffmpeg(),
        'Python Packages': check_python_packages(),
        'Directories': check_directories(),
        'Templates': check_templates(),
        'Translation Service': test_translations(),
        'Text-to-Speech': test_tts(),
        'Audio Conversion': test_audio_conversion()
    }
    
    print_header("Summary")
    
    passed = sum(results.values())
    total = len(results)
    
    for check, status in results.items():
        icon = "✅" if status else "❌"
        print(f"{icon} {check}")
    
    print(f"\n{'='*60}")
    print(f"  Results: {passed}/{total} checks passed")
    print(f"{'='*60}\n")
    
    if passed == total:
        print("🎉 All checks passed! Your system is ready.")
        print("\nNext step: Run the application")
        print("   python app.py")
        print("\nThen open: http://localhost:5000")
        return 0
    else:
        print("⚠️  Some checks failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("1. Install missing packages: pip install -r requirements.txt")
        print("2. Install FFmpeg (see setup instructions)")
        print("3. Create template files (see provided HTML files)")
        print("4. Check internet connection for translation services")
        return 1

if __name__ == '__main__':
>>>>>>> 0b1e9e43 (SCORM Audio Translation)
    sys.exit(main())