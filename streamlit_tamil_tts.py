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
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

try:
    import requests
    from huggingface_hub import InferenceClient
    HF_AVAILABLE = True
except ImportError:
    HF_AVAILABLE = False


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
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    
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
        available_engines = []
        if EDGE_TTS_AVAILABLE:
            available_engines.append("Edge TTS (Microsoft)")
        if GTTS_AVAILABLE:
            available_engines.append("gTTS (Google)")
        
        if not available_engines:
            st.error("No TTS engines available!")
            return
            
        engine = st.selectbox(
            "Select Engine",
            available_engines,
            help="Choose TTS engine"
        )
    
    # Voice selection
    voice_id = None
    
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
                tamil_text = "வணக்கம், எப்படி இருக்கிறீர்கள்?"
        with col2:
            if st.button("நன்றி"):
                tamil_text = "நன்றி, நான் நன்றாக இருக்கிறேன்."
        with col3:
            if st.button("தமிழ்"):
                tamil_text = "தமிழ் மிகவும் அழகான மொழி."
    
    # Generate button
    if st.button("🎤 Generate Speech", type="primary", use_container_width=True):
        if not tamil_text.strip():
            st.error("Please enter some text!")
            return
        
        output_dir = Path("generated_audio")
        output_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = str(output_dir / f"tamil_speech_{timestamp}.mp3")
        
        with st.spinner("Generating speech..."):
            try:
                if "Edge TTS" in engine:
                    asyncio.run(generate_edge_tts(tamil_text, voice_id, output_file))
                elif "gTTS" in engine:
                    generate_gtts(tamil_text, output_file)
                
                st.success("✅ Speech generated successfully!")
                st.audio(output_file)
                
                with open(output_file, "rb") as f:
                    st.download_button(
                        "📥 Download Audio",
                        f.read(),
                        file_name=os.path.basename(output_file),
                        mime="audio/mpeg"
                    )
                
            except Exception as e:
                st.error(f"Error: {str(e)}")


def batch_processing_mode():
    """Batch processing mode for multiple texts"""
    
    st.header("📦 Batch Processing")
    st.write("Generate speech for multiple texts at once")
    
    # Input method
    input_method = st.radio(
        "Input Method",
        ["Manual Entry", "Upload CSV", "Upload Text File"],
        horizontal=True
    )
    
    texts = []
    
    if input_method == "Manual Entry":
        st.subheader("Enter Texts (one per line)")
        batch_text = st.text_area(
            "Tamil Texts",
            value="வணக்கம்\nநன்றி\nதமிழ் மொழி",
            height=200
        )
        texts = [t.strip() for t in batch_text.split('\n') if t.strip()]
    
    elif input_method == "Upload CSV":
        uploaded_file = st.file_uploader("Upload CSV file", type=['csv'])
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
            st.write("Preview:", df.head())
            
            text_column = st.selectbox("Select text column", df.columns)
            texts = df[text_column].tolist()
    
    elif input_method == "Upload Text File":
        uploaded_file = st.file_uploader("Upload text file", type=['txt'])
        if uploaded_file:
            content = uploaded_file.read().decode('utf-8')
            texts = [t.strip() for t in content.split('\n') if t.strip()]
    
    # Voice selection
    if EDGE_TTS_AVAILABLE:
        voice_id = st.selectbox(
            "Select Voice",
            list(EDGE_VOICES.keys()),
            format_func=lambda x: f"{EDGE_VOICES[x]['flag']} {EDGE_VOICES[x]['name']}"
        )
    
    # Process batch
    if texts and st.button("🎬 Generate All", type="primary"):
        output_dir = Path("generated_audio/batch")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        generated_files = []
        
        for idx, text in enumerate(texts):
            status_text.text(f"Processing {idx+1}/{len(texts)}: {text[:30]}...")
            
            output_file = str(output_dir / f"batch_{idx+1:03d}.mp3")
            
            try:
                if EDGE_TTS_AVAILABLE:
                    asyncio.run(generate_edge_tts(text, voice_id, output_file))
                elif GTTS_AVAILABLE:
                    generate_gtts(text, output_file)
                
                generated_files.append(output_file)
            except Exception as e:
                st.warning(f"Failed for text {idx+1}: {str(e)}")
            
            progress_bar.progress((idx + 1) / len(texts))
        
        status_text.text("✅ Batch processing complete!")
        
        # Create zip file
        zip_path = "generated_audio/batch_audio.zip"
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for file in generated_files:
                zipf.write(file, os.path.basename(file))
        
        with open(zip_path, 'rb') as f:
            st.download_button(
                "📦 Download All (ZIP)",
                f.read(),
                file_name="tamil_tts_batch.zip",
                mime="application/zip"
            )


def voice_comparison_mode():
    """Compare different voices for the same text"""
    
    st.header("🔄 Voice Comparison")
    st.write("Compare how different voices sound with the same text")
    
    # Text input
    tamil_text = st.text_area(
        "Enter Tamil Text",
        value="வணக்கம், இது தமிழ் உரை செயலாக்கம்.",
        height=100
    )
    
    # Voice selection
    st.subheader("Select Voices to Compare")
    
    selected_voices = []
    cols = st.columns(3)
    
    for idx, (vid, vinfo) in enumerate(EDGE_VOICES.items()):
        with cols[idx % 3]:
            if st.checkbox(
                f"{vinfo['flag']} {vinfo['name']}",
                key=f"compare_{vid}"
            ):
                selected_voices.append(vid)
    
    # Generate comparison
    if st.button("🎭 Compare Voices", type="primary") and selected_voices:
        if not tamil_text.strip():
            st.error("Please enter some text!")
            return
        
        output_dir = Path("generated_audio/comparison")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        st.subheader("🔊 Voice Comparison Results")
        
        for voice_id in selected_voices:
            vinfo = EDGE_VOICES[voice_id]
            
            with st.expander(f"{vinfo['flag']} {vinfo['name']} - {vinfo['gender']}, {vinfo['region']}", expanded=True):
                output_file = str(output_dir / f"compare_{vinfo['name']}.mp3")
                
                with st.spinner(f"Generating {vinfo['name']}..."):
                    try:
                        asyncio.run(generate_edge_tts(tamil_text, voice_id, output_file))
                        st.audio(output_file)
                        st.caption(vinfo['description'])
                    except Exception as e:
                        st.error(f"Error: {str(e)}")


def conversation_mode():
    """Conversation mode with alternating voices"""
    
    st.header("💬 Conversation Mode")
    st.write("Create dialogues with different voices")
    
    # Voice assignment
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("👤 Speaker 1")
        speaker1_voice = st.selectbox(
            "Voice 1",
            list(EDGE_VOICES.keys()),
            format_func=lambda x: f"{EDGE_VOICES[x]['flag']} {EDGE_VOICES[x]['name']}",
            key="speaker1"
        )
    
    with col2:
        st.subheader("👥 Speaker 2")
        speaker2_voice = st.selectbox(
            "Voice 2",
            list(EDGE_VOICES.keys()),
            format_func=lambda x: f"{EDGE_VOICES[x]['flag']} {EDGE_VOICES[x]['name']}",
            key="speaker2",
            index=1
        )
    
    # Conversation input
    st.subheader("📝 Enter Conversation")
    
    col_speaker, col_text, col_add = st.columns([1, 3, 1])
    
    with col_speaker:
        current_speaker = st.selectbox("Speaker", ["Speaker 1", "Speaker 2"])
    
    with col_text:
        dialogue_text = st.text_input("Dialogue")
    
    with col_add:
        st.write("")
        st.write("")
        if st.button("➕ Add"):
            if dialogue_text:
                st.session_state.conversation_history.append({
                    'speaker': current_speaker,
                    'text': dialogue_text,
                    'voice': speaker1_voice if current_speaker == "Speaker 1" else speaker2_voice
                })
    
    # Display conversation
    if st.session_state.conversation_history:
        st.subheader("📜 Conversation Script")
        
        for idx, item in enumerate(st.session_state.conversation_history):
            col1, col2, col3 = st.columns([1, 4, 1])
            with col1:
                st.write(f"**{item['speaker']}**")
            with col2:
                st.write(item['text'])
            with col3:
                if st.button("🗑️", key=f"del_{idx}"):
                    st.session_state.conversation_history.pop(idx)
                    st.rerun()
        
        # Generate conversation
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🎬 Generate Conversation", type="primary", use_container_width=True):
                output_dir = Path("generated_audio/conversation")
                output_dir.mkdir(parents=True, exist_ok=True)
                
                st.subheader("🔊 Generated Conversation")
                
                for idx, item in enumerate(st.session_state.conversation_history):
                    output_file = str(output_dir / f"conv_{idx+1:02d}.mp3")
                    
                    with st.spinner(f"Generating line {idx+1}..."):
                        try:
                            asyncio.run(generate_edge_tts(item['text'], item['voice'], output_file))
                            
                            st.write(f"**{item['speaker']}**: {item['text']}")
                            st.audio(output_file)
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
        
        if st.button("🗑️ Clear All"):
            st.session_state.conversation_history = []
            st.rerun()


if __name__ == "__main__":
    main()
