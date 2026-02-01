"""
Advanced Streamlit App for Tamil TTS
Includes batch processing, voice comparison, and conversation mode
"""

import streamlit as st
import os
import asyncio
from pathlib import Path
import pandas as pd
import zipfile
from datetime import datetime

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
    page_title="Tamil TTS Studio Pro",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        color: #FF6B6B;
        text-align: center;
        margin-bottom: 1rem;
    }
    .feature-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .voice-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    </style>
""", unsafe_allow_html=True)


# Edge TTS voice database
EDGE_VOICES = {
    'ta-IN-PallaviNeural': {
        'name': 'Pallavi',
        'gender': 'Female',
        'region': 'India',
        'flag': '🇮🇳',
        'description': 'Clear, professional female voice'
    },
    'ta-IN-ValluvarNeural': {
        'name': 'Valluvar',
        'gender': 'Male', 
        'region': 'India',
        'flag': '🇮🇳',
        'description': 'Authoritative male voice'
    },
    'ta-SG-VenbaNeural': {
        'name': 'Venba',
        'gender': 'Female',
        'region': 'Singapore',
        'flag': '🇸🇬',
        'description': 'Friendly female voice'
    },
    'ta-SG-AnbuNeural': {
        'name': 'Anbu',
        'gender': 'Male',
        'region': 'Singapore',
        'flag': '🇸🇬',
        'description': 'Warm male voice'
    },
    'ta-LK-SaranyaNeural': {
        'name': 'Saranya',
        'gender': 'Female',
        'region': 'Sri Lanka',
        'flag': '🇱🇰',
        'description': 'Gentle female voice'
    },
    'ta-LK-KumarNeural': {
        'name': 'Kumar',
        'gender': 'Male',
        'region': 'Sri Lanka',
        'flag': '🇱🇰',
        'description': 'Strong male voice'
    }
}


async def generate_edge_tts(text, voice, output_file):
    """Generate speech using Edge TTS"""
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_file)


def generate_coqui_tts(text, speaker_wav, output_file):
    """Generate speech using Coqui TTS"""
    if not COQUI_AVAILABLE:
        raise ImportError("Coqui TTS not available")
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    
    # Initialize TTS only once using session state
    if 'tts_model' not in st.session_state:
        with st.spinner("Loading voice cloning model... (first time only)"):
            st.session_state.tts_model = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
    
    st.session_state.tts_model.tts_to_file(
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
    st.markdown('<h1 class="main-header">🎙️ Tamil TTS Studio Pro</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem;">Professional Tamil Text-to-Speech with Multiple Voices</p>', unsafe_allow_html=True)
    
    # Initialize session state
    if 'generated_files' not in st.session_state:
        st.session_state.generated_files = []
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Mode selection
        app_mode = st.radio(
            "Select Mode",
            ["🎤 Single Generation", "📦 Batch Processing", "🔄 Voice Comparison", "💬 Conversation"],
            help="Choose the operation mode"
        )
        
        st.markdown("---")
        
        # Engine availability
        st.subheader("Available Engines")
        if EDGE_TTS_AVAILABLE:
            st.success("✅ Edge TTS (6 voices)")
        else:
            st.error("❌ Edge TTS")
            
        if COQUI_AVAILABLE:
            st.success("✅ Coqui XTTS (Cloning)")
        else:
            st.warning("⚠️ Coqui XTTS")
            
        if GTTS_AVAILABLE:
            st.success("✅ Google TTS")
        else:
            st.warning("⚠️ Google TTS")
    
    # Main content based on mode
    if app_mode == "🎤 Single Generation":
        single_generation_mode()
    
    elif app_mode == "📦 Batch Processing":
        batch_processing_mode()
    
    elif app_mode == "🔄 Voice Comparison":
        voice_comparison_mode()
    
    elif app_mode == "💬 Conversation":
        conversation_mode()


def single_generation_mode():
    """Single text generation mode"""
    
    st.header("🎤 Single Text Generation")
    
    # Engine selection
    col1, col2 = st.columns([2, 1])
    
    with col1:
        engine = st.selectbox(
            "Select Engine",
            ["Edge TTS (Microsoft)", "Coqui XTTS (Voice Cloning)", "gTTS (Google)"],
            help="Choose TTS engine"
        )
    
    # Voice/sample selection
    voice_id = None
    speaker_file_path = None
    
    if "Edge TTS" in engine:
        st.subheader("🎙️ Voice Selection")
        
        # Display voice cards
        cols = st.columns(3)
        selected_voice = None
        
        for idx, (vid, vinfo) in enumerate(EDGE_VOICES.items()):
            with cols[idx % 3]:
                if st.button(
                    f"{vinfo['flag']} {vinfo['name']}\n{vinfo['gender']} • {vinfo['region']}",
                    key=vid,
                    use_container_width=True
                ):
                    selected_voice = vid
        
        # Keep selection in session state
        if selected_voice:
            st.session_state.selected_voice = selected_voice
        
        voice_id = st.session_state.get('selected_voice', 'ta-IN-PallaviNeural')
        
        # Show selected voice info
        vinfo = EDGE_VOICES[voice_id]
        st.info(f"**Selected**: {vinfo['flag']} {vinfo['name']} ({vinfo['gender']}, {vinfo['region']})")
    
    elif "Coqui" in engine:
        if not COQUI_AVAILABLE:
            st.error("❌ Coqui TTS not available. Install with: pip install TTS torch")
            return
        
        st.subheader("🎯 Voice Cloning Setup")
        
        speaker_file = st.file_uploader(
            "Upload Voice Sample (WAV/MP3, 3-10 seconds)",
            type=['wav', 'mp3'],
            help="Upload clear audio of the target voice"
        )
        
        if speaker_file:
            speaker_file_path = "temp_speaker.wav"
            with open(speaker_file_path, "wb") as f:
                f.write(speaker_file.getvalue())
            
            st.success(f"✅ Uploaded: {speaker_file.name}")
            st.audio(speaker_file)
    
    # Text input
    st.subheader("📝 Text Input")
    
    tamil_text = st.text_area(
        "Enter Tamil Text",
        value="வணக்கம், இது தமிழ் உரை செயலாக்கம்.",
        height=120,
        help="Enter Tamil text to convert to speech"
    )
    
    # Sample texts
    with st.expander("📌 Sample Texts"):
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("வணக்கம்"):
                st.session_state.tamil_text = "வணக்கம், எப்படி இருக்கிறீர்கள்?"
        with col2:
            if st.button("நன்றி"):
                st.session_state.tamil_text = "நன்றி, நான் நன்றாக இருக்கிறேன்."
        with col3:
            if st.button("மீண்டும்"):
                st.session_state.tamil_text = "நன்றி, மீண்டும் சந்திப்போம்."
    
    if 'tamil_text' in st.session_state:
        tamil_text = st.session_state.tamil_text
    
    # Generate button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🎤 Generate Speech", type="primary", use_container_width=True):
            if not tamil_text.strip():
                st.error("Please enter some text!")
                return
            
            output_dir = Path("generated_audio")
            output_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            with st.spinner("🎵 Generating..."):
                try:
                    if "Edge TTS" in engine:
                        output_file = str(output_dir / f"edge_{timestamp}.mp3")
                        asyncio.run(generate_edge_tts(tamil_text, voice_id, output_file))
                    
                    elif "Coqui" in engine:
                        if not speaker_file_path:
                            st.error("Please upload a voice sample!")
                            return
                        output_file = str(output_dir / f"cloned_{timestamp}.wav")
                        generate_coqui_tts(tamil_text, speaker_file_path, output_file)
                    
                    else:  # gTTS
                        output_file = str(output_dir / f"gtts_{timestamp}.mp3")
                        generate_gtts(tamil_text, output_file)
                    
                    st.success("✅ Speech generated!")
                    
                    # Play and download
                    st.audio(output_file)
                    
                    with open(output_file, "rb") as f:
                        st.download_button(
                            "📥 Download Audio",
                            f.read(),
                            file_name=os.path.basename(output_file),
                            mime="audio/mpeg" if output_file.endswith(".mp3") else "audio/wav"
                        )
                    
                    # Save to history
                    st.session_state.generated_files.append(output_file)
                    
                except Exception as e:
                    st.error(f"Error: {str(e)}")


def batch_processing_mode():
    """Batch processing mode"""
    
    st.header("📦 Batch Processing")
    st.info("Generate multiple audio files from a list of texts")
    
    # Input method
    input_method = st.radio(
        "Input Method",
        ["Manual Entry", "Upload CSV", "Upload Text File"]
    )
    
    texts = []
    
    if input_method == "Manual Entry":
        text_input = st.text_area(
            "Enter texts (one per line)",
            height=200,
            placeholder="வணக்கம்\nநன்றி\nமீண்டும் சந்திப்போம்"
        )
        texts = [line.strip() for line in text_input.split('\n') if line.strip()]
    
    elif input_method == "Upload CSV":
        csv_file = st.file_uploader("Upload CSV (with 'text' column)", type=['csv'])
        if csv_file:
            df = pd.read_csv(csv_file)
            if 'text' in df.columns:
                texts = df['text'].tolist()
                st.success(f"Loaded {len(texts)} texts from CSV")
                st.dataframe(df.head())
            else:
                st.error("CSV must have a 'text' column")
    
    else:  # Text file
        txt_file = st.file_uploader("Upload Text File", type=['txt'])
        if txt_file:
            content = txt_file.read().decode('utf-8')
            texts = [line.strip() for line in content.split('\n') if line.strip()]
            st.success(f"Loaded {len(texts)} texts")
    
    if texts:
        st.write(f"**Total texts**: {len(texts)}")
        
        # Voice selection
        voice_id = st.selectbox(
            "Select Voice",
            list(EDGE_VOICES.keys()),
            format_func=lambda x: f"{EDGE_VOICES[x]['name']} ({EDGE_VOICES[x]['gender']}, {EDGE_VOICES[x]['region']})"
        )
        
        if st.button("🎬 Generate All", type="primary"):
            output_dir = Path("batch_output")
            output_dir.mkdir(exist_ok=True)
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            generated_files = []
            
            for idx, text in enumerate(texts):
                status_text.text(f"Processing {idx+1}/{len(texts)}: {text[:30]}...")
                
                output_file = str(output_dir / f"batch_{idx+1:03d}.mp3")
                
                try:
                    asyncio.run(generate_edge_tts(text, voice_id, output_file))
                    generated_files.append(output_file)
                except Exception as e:
                    st.warning(f"Failed for text {idx+1}: {str(e)}")
                
                progress_bar.progress((idx + 1) / len(texts))
            
            status_text.text("✅ All files generated!")
            
            # Create ZIP
            zip_path = "batch_output.zip"
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for file in generated_files:
                    zipf.write(file, os.path.basename(file))
            
            with open(zip_path, 'rb') as f:
                st.download_button(
                    "📦 Download All (ZIP)",
                    f.read(),
                    file_name="tamil_audio_batch.zip",
                    mime="application/zip"
                )


def voice_comparison_mode():
    """Voice comparison mode"""
    
    st.header("🔄 Voice Comparison")
    st.info("Compare the same text with different voices")
    
    tamil_text = st.text_area(
        "Enter Tamil Text",
        value="வணக்கம், இது குரல் ஒப்பீடு சோதனை.",
        height=100
    )
    
    # Select voices to compare
    st.subheader("Select Voices to Compare")
    
    selected_voices = []
    cols = st.columns(3)
    
    for idx, (vid, vinfo) in enumerate(EDGE_VOICES.items()):
        with cols[idx % 3]:
            if st.checkbox(
                f"{vinfo['flag']} {vinfo['name']}",
                value=True,
                key=f"comp_{vid}"
            ):
                selected_voices.append(vid)
    
    if st.button("🎵 Generate Comparison", type="primary"):
        if not selected_voices:
            st.error("Please select at least one voice!")
            return
        
        output_dir = Path("voice_comparison")
        output_dir.mkdir(exist_ok=True)
        
        st.subheader("🔊 Generated Voices")
        
        for voice_id in selected_voices:
            vinfo = EDGE_VOICES[voice_id]
            
            with st.container():
                st.markdown(f"### {vinfo['flag']} {vinfo['name']} ({vinfo['gender']}, {vinfo['region']})")
                
                output_file = str(output_dir / f"{voice_id}.mp3")
                
                with st.spinner(f"Generating {vinfo['name']}..."):
                    asyncio.run(generate_edge_tts(tamil_text, voice_id, output_file))
                
                st.audio(output_file)
                
                with open(output_file, 'rb') as f:
                    st.download_button(
                        f"📥 Download {vinfo['name']}",
                        f.read(),
                        file_name=f"{vinfo['name']}.mp3",
                        key=f"dl_{voice_id}"
                    )
                
                st.markdown("---")


def conversation_mode():
    """Conversation/dialogue mode"""
    
    st.header("💬 Conversation Mode")
    st.info("Create multi-speaker dialogues")
    
    # Initialize conversation
    if 'conversation' not in st.session_state:
        st.session_state.conversation = []
    
    # Add dialogue line
    st.subheader("Add Dialogue Line")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        speaker_voice = st.selectbox(
            "Speaker",
            list(EDGE_VOICES.keys()),
            format_func=lambda x: f"{EDGE_VOICES[x]['name']}",
            key="new_speaker"
        )
    
    with col2:
        dialogue_text = st.text_input(
            "Dialogue",
            key="new_dialogue",
            placeholder="வணக்கம், எப்படி இருக்கிறீர்கள்?"
        )
    
    if st.button("➕ Add Line"):
        if dialogue_text.strip():
            st.session_state.conversation.append({
                'voice': speaker_voice,
                'text': dialogue_text
            })
            st.success("Added!")
            st.rerun()
    
    # Display conversation
    if st.session_state.conversation:
        st.subheader("📜 Conversation Script")
        
        for idx, line in enumerate(st.session_state.conversation):
            vinfo = EDGE_VOICES[line['voice']]
            col1, col2, col3 = st.columns([2, 5, 1])
            
            with col1:
                st.write(f"**{vinfo['name']}** ({vinfo['gender']})")
            with col2:
                st.write(line['text'])
            with col3:
                if st.button("🗑️", key=f"del_{idx}"):
                    st.session_state.conversation.pop(idx)
                    st.rerun()
        
        # Generate conversation
        if st.button("🎬 Generate Conversation", type="primary"):
            output_dir = Path("conversation")
            output_dir.mkdir(exist_ok=True)
            
            all_files = []
            
            for idx, line in enumerate(st.session_state.conversation):
                output_file = str(output_dir / f"line_{idx+1:02d}.mp3")
                
                with st.spinner(f"Generating line {idx+1}..."):
                    asyncio.run(generate_edge_tts(line['text'], line['voice'], output_file))
                
                all_files.append(output_file)
            
            st.success("✅ Conversation generated!")
            
            # Play all
            st.subheader("🔊 Playback")
            for idx, (line, audio_file) in enumerate(zip(st.session_state.conversation, all_files)):
                vinfo = EDGE_VOICES[line['voice']]
                st.write(f"**{idx+1}. {vinfo['name']}**: {line['text']}")
                st.audio(audio_file)
            
            # Download ZIP
            zip_path = "conversation.zip"
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for file in all_files:
                    zipf.write(file, os.path.basename(file))
            
            with open(zip_path, 'rb') as f:
                st.download_button(
                    "📦 Download Conversation (ZIP)",
                    f.read(),
                    file_name="tamil_conversation.zip"
                )
        
        if st.button("🗑️ Clear All"):
            st.session_state.conversation = []
            st.rerun()


if __name__ == "__main__":
    main()
