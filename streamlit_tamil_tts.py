"""
Streamlit Web App for Tamil TTS with Multiple Voices & Voice Cloning
Interactive web interface for generating Tamil speech
"""

import streamlit as st
import os
import asyncio
from pathlib import Path
import base64

# Try importing required modules
try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False

try:
    from TTS.api import TTS
    import torch
    COQUI_AVAILABLE = True
except ImportError:
    COQUI_AVAILABLE = False

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False


# Page configuration
st.set_page_config(
    page_title="Tamil TTS Studio",
    page_icon="🎤",
    layout="wide",
    initial_sidebar_state="expanded"
)


def get_audio_player(audio_file):
    """Create an audio player for the generated file"""
    with open(audio_file, "rb") as f:
        audio_bytes = f.read()
    
    # Convert to base64 for embedding
    audio_b64 = base64.b64encode(audio_bytes).decode()
    
    # Determine MIME type
    ext = Path(audio_file).suffix.lower()
    mime_type = "audio/mpeg" if ext == ".mp3" else "audio/wav"
    
    # Create HTML audio player
    audio_html = f'''
        <audio controls style="width: 100%;">
            <source src="data:{mime_type};base64,{audio_b64}" type="{mime_type}">
            Your browser does not support the audio element.
        </audio>
    '''
    return audio_html


async def generate_edge_tts(text, voice, output_file):
    """Generate speech using Edge TTS"""
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_file)


def generate_coqui_tts(text, speaker_wav, output_file):
    """Generate speech using Coqui TTS (voice cloning)"""
    device = "cuda" if torch.cuda.is_available() else "cpu"
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
    tts.tts_to_file(
        text=text,
        speaker_wav=speaker_wav,
        language="ta",
        file_path=output_file
    )


def generate_gtts(text, output_file):
    """Generate speech using gTTS"""
    tts = gTTS(text=text, lang='ta', slow=False)
    tts.save(output_file)


def main():
    """Main Streamlit app"""
    
    # Header
    st.title("🎤 Tamil TTS Studio")
    st.markdown("### Text-to-Speech with Multiple Voices & Voice Cloning")
    
    # Sidebar - Engine Selection
    st.sidebar.header("⚙️ Settings")
    
    # Check available engines
    available_engines = []
    if EDGE_TTS_AVAILABLE:
        available_engines.append("Edge TTS (Microsoft - 6 voices)")
    if COQUI_AVAILABLE:
        available_engines.append("Coqui XTTS (Voice Cloning)")
    if GTTS_AVAILABLE:
        available_engines.append("gTTS (Google - Basic)")
    
    if not available_engines:
        st.error("⚠️ No TTS engines available!")
        st.info("Please install at least one engine:")
        st.code("pip install edge-tts")
        st.code("pip install TTS torch")
        st.code("pip install gtts")
        st.stop()
    
    # Engine selection
    engine_choice = st.sidebar.selectbox(
        "Select TTS Engine",
        available_engines,
        help="Choose the text-to-speech engine"
    )
    
    # Voice/model selection based on engine
    voice_id = None
    speaker_file = None
    
    if "Edge TTS" in engine_choice:
        st.sidebar.subheader("🎙️ Voice Selection")
        
        # Voice categories
        voice_region = st.sidebar.radio(
            "Region",
            ["India", "Singapore", "Sri Lanka"]
        )
        
        voice_gender = st.sidebar.radio(
            "Gender",
            ["Female", "Male"]
        )
        
        # Map selection to voice ID
        voice_map = {
            ("India", "Female"): ("ta-IN-PallaviNeural", "Pallavi"),
            ("India", "Male"): ("ta-IN-ValluvarNeural", "Valluvar"),
            ("Singapore", "Female"): ("ta-SG-VenbaNeural", "Venba"),
            ("Singapore", "Male"): ("ta-SG-AnbuNeural", "Anbu"),
            ("Sri Lanka", "Female"): ("ta-LK-SaranyaNeural", "Saranya"),
            ("Sri Lanka", "Male"): ("ta-LK-KumarNeural", "Kumar"),
        }
        
        voice_id, voice_name = voice_map[(voice_region, voice_gender)]
        st.sidebar.success(f"Selected: **{voice_name}** ({voice_gender}, {voice_region})")
    
    elif "Coqui XTTS" in engine_choice:
        st.sidebar.subheader("🎯 Voice Cloning")
        st.sidebar.info("Upload a 3-10 second audio sample of the target voice")
        
        speaker_file = st.sidebar.file_uploader(
            "Upload Voice Sample (WAV)",
            type=['wav', 'mp3'],
            help="Audio sample for voice cloning (3-10 seconds recommended)"
        )
        
        if speaker_file:
            # Save uploaded file
            upload_path = "uploaded_speaker.wav"
            with open(upload_path, "wb") as f:
                f.write(speaker_file.getvalue())
            st.sidebar.success(f"✓ Voice sample uploaded: {speaker_file.name}")
            
            # Show audio player
            st.sidebar.audio(speaker_file)
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📝 Text Input")
        
        # Text input
        tamil_text = st.text_area(
            "Enter Tamil Text",
            value="வணக்கம், இது தமிழ் உரை செயலாக்கம்.",
            height=150,
            help="Type or paste Tamil text here"
        )
        
        # Character count
        char_count = len(tamil_text)
        st.caption(f"Characters: {char_count}")
        
        # Sample texts
        with st.expander("📌 Sample Tamil Texts"):
            if st.button("வணக்கம், எப்படி இருக்கிறீர்கள்?"):
                tamil_text = "வணக்கம், எப்படி இருக்கிறீர்கள்?"
                st.rerun()
            if st.button("நன்றி, நான் நன்றாக இருக்கிறேன்."):
                tamil_text = "நன்றி, நான் நன்றாக இருக்கிறேன்."
                st.rerun()
            if st.button("தமிழ் மிகவும் அழகான மொழி."):
                tamil_text = "தமிழ் மிகவும் அழகான மொழி."
                st.rerun()
    
    with col2:
        st.subheader("🎬 Quick Actions")
        
        # Engine info card
        if "Edge TTS" in engine_choice:
            st.info(f"""
            **Engine**: Microsoft Edge TTS  
            **Voice**: {voice_name}  
            **Gender**: {voice_gender}  
            **Region**: {voice_region}  
            **Quality**: ⭐⭐⭐⭐⭐
            """)
        elif "Coqui XTTS" in engine_choice:
            st.info("""
            **Engine**: Coqui XTTS v2  
            **Type**: Voice Cloning  
            **Quality**: ⭐⭐⭐⭐⭐  
            **Requires**: Voice sample
            """)
        elif "gTTS" in engine_choice:
            st.info("""
            **Engine**: Google TTS  
            **Voice**: Default Tamil  
            **Quality**: ⭐⭐⭐  
            **Speed**: Fast
            """)
    
    # Generate button
    st.markdown("---")
    
    col_gen1, col_gen2, col_gen3 = st.columns([1, 2, 1])
    
    with col_gen2:
        generate_btn = st.button(
            "🎤 Generate Speech",
            type="primary",
            use_container_width=True
        )
    
    # Generation logic
    if generate_btn:
        if not tamil_text.strip():
            st.error("⚠️ Please enter some Tamil text!")
            st.stop()
        
        # Create output directory
        output_dir = Path("generated_audio")
        output_dir.mkdir(exist_ok=True)
        
        # Generate output filename
        timestamp = Path("output").stem
        output_file = str(output_dir / f"tamil_speech_{timestamp}.mp3")
        
        # Progress indicator
        with st.spinner("🎵 Generating speech..."):
            try:
                # Generate based on engine
                if "Edge TTS" in engine_choice:
                    asyncio.run(generate_edge_tts(tamil_text, voice_id, output_file))
                
                elif "Coqui XTTS" in engine_choice:
                    if not speaker_file:
                        st.error("⚠️ Please upload a voice sample for cloning!")
                        st.stop()
                    
                    output_file = str(output_dir / f"tamil_speech_{timestamp}.wav")
                    generate_coqui_tts(tamil_text, upload_path, output_file)
                
                elif "gTTS" in engine_choice:
                    generate_gtts(tamil_text, output_file)
                
                # Success message
                st.success("✅ Speech generated successfully!")
                
                # Display audio player
                st.subheader("🔊 Generated Audio")
                
                # Use Streamlit's native audio player
                st.audio(output_file)
                
                # Download button
                with open(output_file, "rb") as f:
                    audio_bytes = f.read()
                
                st.download_button(
                    label="📥 Download Audio",
                    data=audio_bytes,
                    file_name=os.path.basename(output_file),
                    mime="audio/mpeg" if output_file.endswith(".mp3") else "audio/wav",
                    use_container_width=True
                )
                
                # Show file info
                file_size = os.path.getsize(output_file) / 1024  # KB
                st.caption(f"File: {os.path.basename(output_file)} | Size: {file_size:.1f} KB")
                
            except Exception as e:
                st.error(f"❌ Error generating speech: {str(e)}")
                st.exception(e)
    
    # Footer
    st.markdown("---")
    
    # Info tabs
    tab1, tab2, tab3 = st.tabs(["📖 About", "🎯 Features", "💡 Tips"])
    
    with tab1:
        st.markdown("""
        ### Tamil TTS Studio
        
        A comprehensive web application for Tamil text-to-speech with multiple voice options.
        
        **Available Engines:**
        - **Edge TTS**: 6 high-quality Microsoft voices (FREE)
        - **Coqui XTTS**: Advanced voice cloning
        - **gTTS**: Basic Google TTS
        
        **Supported Regions:**
        - India (ta-IN)
        - Singapore (ta-SG)
        - Sri Lanka (ta-LK)
        """)
    
    with tab2:
        st.markdown("""
        ### Features
        
        ✅ **6+ Pre-built Tamil Voices**
        - Male and Female voices
        - Multiple regional accents
        
        ✅ **Voice Cloning**
        - Clone any voice from a sample
        - Unlimited custom voices
        
        ✅ **High Quality**
        - Neural TTS models
        - Natural-sounding speech
        
        ✅ **Easy to Use**
        - Simple web interface
        - Instant playback
        - Download audio files
        """)
    
    with tab3:
        st.markdown("""
        ### Tips for Best Results
        
        **Text Input:**
        - Use proper Tamil script (not transliteration)
        - Keep sentences reasonable length
        - Use proper punctuation
        
        **Voice Cloning:**
        - Upload 3-10 second voice sample
        - Use clear, noise-free audio
        - WAV format recommended
        - Single speaker only
        
        **Edge TTS:**
        - Best quality-to-speed ratio
        - No setup required
        - Multiple voice options
        
        **Download:**
        - Files are saved in MP3/WAV format
        - Compatible with all media players
        """)
    
    # Sidebar footer
    st.sidebar.markdown("---")
    st.sidebar.caption("Tamil TTS Studio v1.0")
    st.sidebar.caption("Made with ❤️ for Tamil speakers")


if __name__ == "__main__":
    main()
