"""
Tamil TTS with SpeechT5 Voice Conversion
Hugging Face Spaces Entry Point
Combines gTTS for Tamil text-to-speech with SpeechT5 for voice conversion
"""

import streamlit as st
import os
from pathlib import Path
import numpy as np
from datetime import datetime
import torch
import torchaudio

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

try:
    from transformers import SpeechT5Processor, SpeechT5ForSpeechToSpeech, SpeechT5HifiGan
    from transformers import AutoProcessor, AutoModel
    SPEECHT5_AVAILABLE = True
except ImportError:
    SPEECHT5_AVAILABLE = False

# Page configuration
st.set_page_config(
    page_title="Tamil TTS + Voice Cloning",
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
    .info-box {
        background-color: #e7f3ff;
        color: #004085;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #0066cc;
    }
    </style>
""", unsafe_allow_html=True)

# Global variables for models (cached with st.cache_resource)
@st.cache_resource
def load_speecht5_models():
    """Load SpeechT5 models (cached for Hugging Face Spaces)"""
    processor = SpeechT5Processor.from_pretrained("microsoft/speecht5_vc")
    model = SpeechT5ForSpeechToSpeech.from_pretrained("microsoft/speecht5_vc")
    vocoder = SpeechT5HifiGan.from_pretrained("microsoft/speecht5_hifigan")
    
    # Move to GPU if available
    if torch.cuda.is_available():
        model = model.cuda()
        vocoder = vocoder.cuda()
    
    return processor, model, vocoder


def generate_gtts(text, output_file):
    """Generate speech using gTTS"""
    tts = gTTS(text=text, lang='ta', slow=False)
    tts.save(output_file)
    return output_file


def extract_speaker_embedding(audio_path):
    """Extract speaker embedding from target voice sample"""
    try:
        processor_spk = AutoProcessor.from_pretrained("microsoft/wavlm-base-sv")
        model_spk = AutoModel.from_pretrained("microsoft/wavlm-base-sv")
        
        if torch.cuda.is_available():
            model_spk = model_spk.cuda()
        
        # Load and process target audio
        audio, sr = librosa.load(audio_path, sr=16000, mono=True)
        
        # Process for speaker embedding
        inputs = processor_spk(audio, sampling_rate=16000, return_tensors="pt")
        
        if torch.cuda.is_available():
            inputs = {k: v.cuda() for k, v in inputs.items()}
        
        with torch.no_grad():
            embeddings = model_spk(**inputs).embeddings
        
        # Average over time dimension and normalize
        embeddings = torch.nn.functional.normalize(embeddings, dim=-1).cpu()
        
        return embeddings
        
    except Exception as e:
        st.error(f"Error extracting speaker embedding: {e}")
        return None


def convert_voice_speecht5(source_audio_path, target_audio_path, output_path):
    """Convert voice using SpeechT5"""
    try:
        # Load models
        processor, model, vocoder = load_speecht5_models()
        
        # Load and prepare source audio
        source_audio, sr = librosa.load(source_audio_path, sr=16000, mono=True)
        
        # Extract speaker embedding from target voice
        speaker_embeddings = extract_speaker_embedding(target_audio_path)
        
        if speaker_embeddings is None:
            return False, "Failed to extract speaker embedding"
        
        # Process source audio
        inputs = processor(audio=source_audio, sampling_rate=16000, return_tensors="pt")
        
        if torch.cuda.is_available():
            inputs = {k: v.cuda() if isinstance(v, torch.Tensor) else v for k, v in inputs.items()}
            speaker_embeddings = speaker_embeddings.cuda()
        
        # Generate converted speech
        with torch.no_grad():
            speech = model.generate_speech(
                inputs["input_values"],
                speaker_embeddings,
                vocoder=vocoder
            )
        
        # Save output
        speech = speech.cpu().numpy()
        sf.write(output_path, speech, 16000)
        
        return True, "Voice conversion successful"
        
    except Exception as e:
        return False, f"SpeechT5 conversion error: {str(e)}"


def main():
    """Main Streamlit app for Hugging Face Spaces"""
    
    # Header
    st.markdown('<h1 class="main-header">🎙️ Tamil TTS + Voice Cloning</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem;">Convert Tamil text to speech and clone to your voice</p>', unsafe_allow_html=True)
    
    # Info box
    st.markdown("""
        <div class="info-box">
            <strong>🤖 Powered by:</strong><br>
            • <b>gTTS</b> - Google Text-to-Speech for Tamil<br>
            • <b>Microsoft SpeechT5</b> - Voice cloning AI (Hugging Face)<br>
            • <b>Hugging Face Spaces</b> - Free GPU/CPU hosting
        </div>
    """, unsafe_allow_html=True)
    
    # Workflow
    st.markdown("""
        <div class="workflow-box">
            <h3>🔄 Workflow</h3>
            <p>Tamil Text → gTTS → 🔊 → SpeechT5 AI → 🎭 → Your Voice Clone</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Check dependencies
    with st.sidebar:
        st.header("⚙️ System Status")
        
        if GTTS_AVAILABLE:
            st.success("✅ gTTS (Tamil TTS)")
        else:
            st.error("❌ gTTS")
        
        if SOUNDFILE_AVAILABLE:
            st.success("✅ SoundFile")
        else:
            st.warning("⚠️ SoundFile")
        
        if LIBROSA_AVAILABLE:
            st.success("✅ Librosa")
        else:
            st.warning("⚠️ Librosa")
        
        if SPEECHT5_AVAILABLE:
            st.success("✅ SpeechT5 (Transformers)")
            if torch.cuda.is_available():
                st.success("🚀 CUDA GPU Enabled")
            else:
                st.info("💻 Running on CPU")
        else:
            st.error("❌ SpeechT5")
        
        st.markdown("---")
        st.markdown("### 📖 How to use:")
        st.markdown("""
        1. Enter Tamil text
        2. Upload your voice sample (5-30 sec)
        3. Click 'Generate & Clone Voice'
        4. Download your cloned voice!
        """)
    
    # Main interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📝 Step 1: Enter Tamil Text")
        
        tamil_text = st.text_area(
            "Tamil Text",
            value="வணக்கம், இது தமிழ் உரை செயலாக்கம்.",
            height=100
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
                    st.session_state.tamil_text = text
                    st.rerun()
    
    with col2:
        st.markdown("### 🎭 Step 2: Upload Your Voice")
        
        target_voice = st.file_uploader(
            "Upload voice sample (WAV/MP3)",
            type=['wav', 'mp3'],
            help="Upload 5-30 seconds of clear speech"
        )
        
        if target_voice:
            st.success("✅ Voice uploaded")
            st.audio(target_voice)
    
    # Process section
    st.markdown("---")
    
    if not tamil_text.strip():
        st.info("👆 Enter Tamil text to get started")
        return
    
    if not target_voice:
        st.info("👆 Upload your voice sample to enable voice cloning")
        
        # Basic TTS only
        if st.button("🎤 Generate Tamil TTS Only", type="secondary"):
            with st.spinner("Generating..."):
                output_dir = Path("generated")
                output_dir.mkdir(exist_ok=True)
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                tts_output = output_dir / f"tamil_{timestamp}.mp3"
                
                generate_gtts(tamil_text, str(tts_output))
                
                st.success("✅ Generated!")
                st.audio(str(tts_output))
                
                with open(tts_output, "rb") as f:
                    st.download_button("📥 Download", f.read(), 
                                     file_name=f"tamil_tts_{timestamp}.mp3")
        return
    
    # Full workflow
    if st.button("🚀 Generate & Clone Voice", type="primary", use_container_width=True):
        
        if not SPEECHT5_AVAILABLE:
            st.error("❌ SpeechT5 not available. Check dependencies.")
            return
        
        with st.container():
            # Step 1: Generate TTS
            st.markdown("#### Step 1: Generating Tamil TTS...")
            
            output_dir = Path("generated")
            output_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            with st.spinner("Generating gTTS..."):
                tts_output = output_dir / f"tamil_{timestamp}.wav"
                temp_mp3 = output_dir / f"temp_{timestamp}.mp3"
                
                generate_gtts(tamil_text, str(temp_mp3))
                
                # Convert to wav
                audio, sr = librosa.load(str(temp_mp3), sr=16000, mono=True)
                sf.write(str(tts_output), audio, 16000)
                temp_mp3.unlink(missing_ok=True)
            
            st.success("✅ Tamil TTS Generated!")
            
            col_a, col_b = st.columns(2)
            
            with col_a:
                st.markdown("**Original TTS:**")
                st.audio(str(tts_output))
            
            # Step 2: Voice Conversion
            st.markdown("#### Step 2: Cloning your voice...")
            
            with st.spinner("Processing with SpeechT5 AI..."):
                # Save target voice
                temp_target = output_dir / f"target_{timestamp}.wav"
                with open(temp_target, "wb") as f:
                    f.write(target_voice.getvalue())
                
                # Convert to proper format
                target_audio, sr = librosa.load(str(temp_target), sr=16000, mono=True)
                sf.write(str(temp_target), target_audio, 16000)
                
                # Convert voice
                converted_output = output_dir / f"cloned_{timestamp}.wav"
                success, message = convert_voice_speecht5(
                    str(tts_output),
                    str(temp_target),
                    str(converted_output)
                )
                
                if success:
                    with col_b:
                        st.markdown("**🎭 Your Voice Clone:**")
                        st.audio(str(converted_output))
                    
                    st.success(f"✅ {message}")
                    
                    # Download buttons
                    col_dl1, col_dl2 = st.columns(2)
                    
                    with col_dl1:
                        with open(tts_output, "rb") as f:
                            st.download_button("📥 Original TTS", f.read(), 
                                             file_name=f"tamil_tts_{timestamp}.wav")
                    
                    with col_dl2:
                        with open(converted_output, "rb") as f:
                            st.download_button("📥 Your Voice Clone", f.read(), 
                                             file_name=f"your_voice_clone_{timestamp}.wav")
                else:
                    st.error(f"❌ Failed: {message}")


if __name__ == "__main__":
    main()
