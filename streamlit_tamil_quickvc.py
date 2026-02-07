"""
Tamil TTS with QuickVC Voice Conversion
Combines gTTS for Tamil text-to-speech with QuickVC for voice conversion
"""

import streamlit as st
import os
import subprocess
import tempfile
import shutil
from pathlib import Path
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

try:
    import torchaudio
    TORCHAUDIO_AVAILABLE = True
except ImportError:
    TORCHAUDIO_AVAILABLE = False

import numpy as np
from datetime import datetime

# Try importing required modules
try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

try:
    import soundfile as sf
    SOUNDFILE_AVAILABLE = True
except ImportError:
    SOUNDFILE_AVAILABLE = False

try:
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False

# Page configuration
st.set_page_config(
    page_title="Tamil TTS + Voice Converter",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #FF6B6B;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .workflow-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        text-align: center;
    }
    .step-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #FF6B6B;
    }
    .success-box {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #28a745;
    }
    </style>
""", unsafe_allow_html=True)


def generate_gtts(text, output_file):
    """Generate speech using gTTS"""
    tts = gTTS(text=text, lang='ta', slow=False)
    tts.save(output_file)
    return output_file


def convert_audio_format(input_file, output_file, target_sr=16000):
    """Convert audio to required format for QuickVC (16kHz, mono)"""
    try:
        # Load audio
        audio, sr = librosa.load(input_file, sr=target_sr, mono=True)
        # Save as wav
        sf.write(output_file, audio, target_sr)
        return output_file
    except Exception as e:
        st.error(f"Audio conversion error: {e}")
        return None


def setup_quickvc():
    """Check if QuickVC is available and set it up"""
    quickvc_path = Path("QuickVC-VoiceConversion")
    
    if not quickvc_path.exists():
        st.info("📥 QuickVC not found. Cloning repository...")
        try:
            result = subprocess.run(
                ["git", "clone", "https://github.com/quickvc/QuickVC-VoiceConversion.git"],
                capture_output=True,
                text=True,
                timeout=60
            )
            if result.returncode == 0:
                st.success("✅ QuickVC cloned successfully!")
            else:
                st.error(f"Failed to clone QuickVC: {result.stderr}")
                return None
        except Exception as e:
            st.error(f"Error cloning QuickVC: {e}")
            return None
    
    return quickvc_path


def check_quickvc_model():
    """Check if QuickVC pretrained model exists"""
    model_paths = [
        Path("QuickVC-VoiceConversion/logs/quickvc/G_0.pth"),
        Path("QuickVC-VoiceConversion/logs/quickvc/G_*.pth"),
    ]
    
    logs_dir = Path("QuickVC-VoiceConversion/logs/quickvc")
    if logs_dir.exists():
        pth_files = list(logs_dir.glob("G_*.pth"))
        if pth_files:
            return pth_files[0]
    
    return None


def create_convert_txt(source_wav, target_wav, output_wav):
    """Create convert.txt file for QuickVC"""
    # Get relative paths from QuickVC directory
    content = f"{source_wav}|{target_wav}|{output_wav}\n"
    return content


def run_quickvc_conversion(source_audio, target_audio, output_audio):
    """Run QuickVC voice conversion"""
    quickvc_path = Path("QuickVC-VoiceConversion")
    
    if not quickvc_path.exists():
        return False, "QuickVC not found"
    
    # Convert audio formats if needed
    temp_dir = Path(tempfile.gettempdir()) / "quickvc_temp"
    temp_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Prepare source audio (16kHz, mono, wav)
    source_wav = temp_dir / f"source_{timestamp}.wav"
    convert_audio_format(source_audio, str(source_wav))
    
    # Prepare target audio (16kHz, mono, wav)
    target_wav = temp_dir / f"target_{timestamp}.wav"
    convert_audio_format(target_audio, str(target_wav))
    
    output_wav = temp_dir / f"output_{timestamp}.wav"
    
    # Create convert.txt
    convert_txt_path = quickvc_path / "convert.txt"
    
    # Use absolute paths
    with open(convert_txt_path, 'w') as f:
        f.write(f"{source_wav.absolute()}|{target_wav.absolute()}|{output_wav.absolute()}\n")
    
    try:
        # Run QuickVC conversion
        result = subprocess.run(
            ["python", "convert.py"],
            cwd=str(quickvc_path),
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode == 0:
            if output_wav.exists():
                shutil.copy(str(output_wav), output_audio)
                return True, "Conversion successful"
            else:
                return False, f"Output file not created. Stdout: {result.stdout}, Stderr: {result.stderr}"
        else:
            return False, f"Conversion failed: {result.stderr}"
            
    except Exception as e:
        return False, f"Error during conversion: {str(e)}"


def fallback_voice_conversion(source_audio, target_audio, output_audio):
    """
    Fallback voice conversion using basic audio processing
    This is used when QuickVC is not available
    """
    try:
        import librosa
        import soundfile as sf
        import numpy as np
        
        # Load audio files
        source, sr_source = librosa.load(source_audio, sr=16000)
        target, sr_target = librosa.load(target_audio, sr=16000)
        
        # Extract pitch and timbre characteristics from target
        # This is a simplified approach - not as good as QuickVC
        
        # Compute spectral features
        source_stft = librosa.stft(source)
        target_stft = librosa.stft(target[:len(source)])  # Match lengths
        
        # Get magnitude and phase
        source_mag = np.abs(source_stft)
        source_phase = np.angle(source_stft)
        target_mag = np.abs(target_stft)
        
        # Blend spectral characteristics (simple timbre transfer)
        # Use target's spectral envelope
        alpha = 0.7  # Blend factor
        converted_mag = alpha * target_mag + (1 - alpha) * source_mag
        
        # Reconstruct audio
        converted_stft = converted_mag * np.exp(1j * source_phase)
        converted = librosa.istft(converted_stft)
        
        # Normalize
        converted = converted / np.max(np.abs(converted)) * 0.9
        
        # Save output
        sf.write(output_audio, converted, 16000)
        
        return True, "Fallback conversion completed"
        
    except Exception as e:
        return False, f"Fallback conversion failed: {str(e)}"


def main():
    """Main Streamlit app"""
    
    # Header
    st.markdown('<h1 class="main-header">🎙️ Tamil TTS + Voice Converter</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem;">Convert Tamil text to speech and transform voice characteristics</p>', unsafe_allow_html=True)
    
    # Workflow visualization
    st.markdown("""
        <div class="workflow-box">
            <h3>🔄 Workflow</h3>
            <p style="font-size: 1.1rem;">
                Tamil Text → 📝 → gTTS → 🔊 → QuickVC → 🎭 → Target Voice
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Check dependencies
    with st.sidebar:
        st.header("⚙️ System Status")
        
        if GTTS_AVAILABLE:
            st.success("✅ gTTS (Tamil TTS)")
        else:
            st.error("❌ gTTS - Install: pip install gtts")
        
        if SOUNDFILE_AVAILABLE:
            st.success("✅ SoundFile")
        else:
            st.warning("⚠️ SoundFile - Install: pip install soundfile")
        
        if LIBROSA_AVAILABLE:
            st.success("✅ Librosa")
        else:
            st.warning("⚠️ Librosa - Install: pip install librosa")
        
        # QuickVC setup
        quickvc_path = setup_quickvc()
        if quickvc_path:
            st.success("✅ QuickVC Repository")
            
            model_file = check_quickvc_model()
            if model_file:
                st.success(f"✅ Model: {model_file.name}")
            else:
                st.warning("⚠️ QuickVC Model Not Found")
                st.info("Download pretrained model from QuickVC releases and place in logs/quickvc/")
        else:
            st.error("❌ QuickVC Not Available")
    
    # Main interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📝 Step 1: Enter Tamil Text")
        
        tamil_text = st.text_area(
            "Tamil Text",
            value="வணக்கம், இது தமிழ் உரை செயலாக்கம்.",
            height=100,
            help="Enter Tamil text to convert to speech"
        )
        
        # Sample texts
        cols = st.columns(4)
        sample_texts = {
            "வணக்கம்": "வணக்கம், எப்படி இருக்கிறீர்கள்?",
            "நன்றி": "நன்றி, நான் நன்றாக இருக்கிறேன்.",
            "தமிழ்": "தமிழ் மிகவும் அழகான மொழி.",
            "காலை": "காலை வணக்கம், இனிய நாள்!"
        }
        
        for idx, (label, text) in enumerate(sample_texts.items()):
            with cols[idx]:
                if st.button(label, use_container_width=True):
                    tamil_text = text
                    st.rerun()
    
    with col2:
        st.markdown("### 🎭 Step 2: Upload Target Voice")
        
        target_voice = st.file_uploader(
            "Upload voice sample (WAV/MP3)",
            type=['wav', 'mp3'],
            help="Upload a voice sample to convert the TTS voice to this voice"
        )
        
        if target_voice:
            st.success("✅ Voice sample uploaded")
            st.audio(target_voice)
    
    # Process section
    st.markdown("---")
    
    if not tamil_text.strip():
        st.info("👆 Enter Tamil text to get started")
        return
    
    if not target_voice:
        st.info("👆 Upload a target voice sample to enable voice conversion")
        
        # Still allow basic TTS without conversion
        if st.button("🎤 Generate Basic TTS Only", type="secondary"):
            with st.spinner("Generating Tamil speech..."):
                output_dir = Path("generated_audio")
                output_dir.mkdir(exist_ok=True)
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                tts_output = output_dir / f"tamil_tts_{timestamp}.mp3"
                
                generate_gtts(tamil_text, str(tts_output))
                
                st.success("✅ Tamil TTS Generated!")
                st.audio(str(tts_output))
                
                with open(tts_output, "rb") as f:
                    st.download_button(
                        "📥 Download Audio",
                        f.read(),
                        file_name=f"tamil_tts_{timestamp}.mp3",
                        mime="audio/mpeg"
                    )
        return
    
    # Full workflow with voice conversion
    if st.button("🚀 Generate & Convert Voice", type="primary", use_container_width=True):
        
        progress_container = st.container()
        
        with progress_container:
            # Step 1: Generate TTS
            st.markdown("#### Step 1: Generating Tamil TTS...")
            
            output_dir = Path("generated_audio")
            output_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            with st.spinner("Generating gTTS output..."):
                tts_output = output_dir / f"tamil_tts_{timestamp}.mp3"
                generate_gtts(tamil_text, str(tts_output))
            
            st.success("✅ Tamil TTS Generated!")
            
            col_a, col_b = st.columns(2)
            
            with col_a:
                st.markdown("**Original gTTS Output:**")
                st.audio(str(tts_output))
            
            # Step 2: Voice Conversion
            st.markdown("#### Step 2: Converting Voice...")
            
            with st.spinner("Running voice conversion..."):
                # Save uploaded target voice temporarily
                temp_target = output_dir / f"target_{timestamp}.wav"
                with open(temp_target, "wb") as f:
                    f.write(target_voice.getvalue())
                
                # Output path
                converted_output = output_dir / f"converted_voice_{timestamp}.wav"
                
                # Try QuickVC first, fallback to basic conversion
                model_file = check_quickvc_model()
                
                if model_file and quickvc_path:
                    success, message = run_quickvc_conversion(
                        str(tts_output),
                        str(temp_target),
                        str(converted_output)
                    )
                else:
                    st.info("Using fallback voice conversion (QuickVC model not available)")
                    success, message = fallback_voice_conversion(
                        str(tts_output),
                        str(temp_target),
                        str(converted_output)
                    )
                
                if success:
                    with col_b:
                        st.markdown("**Converted Voice:**")
                        st.audio(str(converted_output))
                    
                    st.success(f"✅ Voice conversion complete! ({message})")
                    
                    # Download buttons
                    col_dl1, col_dl2 = st.columns(2)
                    
                    with col_dl1:
                        with open(tts_output, "rb") as f:
                            st.download_button(
                                "📥 Original TTS",
                                f.read(),
                                file_name=f"tamil_tts_{timestamp}.mp3",
                                mime="audio/mpeg"
                            )
                    
                    with col_dl2:
                        with open(converted_output, "rb") as f:
                            st.download_button(
                                "📥 Converted Voice",
                                f.read(),
                                file_name=f"converted_voice_{timestamp}.wav",
                                mime="audio/wav"
                            )
                else:
                    st.error(f"❌ Voice conversion failed: {message}")
                    st.info("Showing original TTS output instead")


if __name__ == "__main__":
    main()
