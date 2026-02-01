# Tamil TTS Streamlit Apps - Deployment Guide

## 📱 Two Streamlit Apps Available

### 1. **streamlit_tamil_tts.py** - Basic App
Simple, clean interface for single text generation

### 2. **streamlit_tamil_tts_pro.py** - Pro App
Advanced features:
- 🎤 Single Generation
- 📦 Batch Processing
- 🔄 Voice Comparison
- 💬 Conversation Mode

---

## 🚀 Quick Start

### Installation

```bash
# Install Streamlit
pip install streamlit

# Install TTS engines (choose one or more)
pip install edge-tts              # Microsoft voices (Recommended)
pip install TTS torch             # Voice cloning
pip install gtts                  # Google TTS
```

### Run Basic App

```bash
streamlit run streamlit_tamil_tts.py
```

### Run Pro App

```bash
streamlit run streamlit_tamil_tts_pro.py
```

The app will open automatically in your browser at `http://localhost:8501`

---

## 📋 Requirements

Create `requirements_streamlit.txt`:

```
# Core
streamlit>=1.28.0
asyncio-compat>=0.1.0

# TTS Engines
edge-tts>=6.1.0          # Microsoft Edge TTS (6 Tamil voices)
TTS>=0.22.0              # Coqui XTTS (voice cloning)
torch>=2.0.0             # Required for Coqui
gtts>=2.3.0              # Google TTS

# Data Processing
pandas>=2.0.0            # For batch CSV processing
```

Install all:
```bash
pip install -r requirements_streamlit.txt --break-system-packages
```

---

## 🎯 App Features Comparison

| Feature | Basic App | Pro App |
|---------|-----------|---------|
| Single Generation | ✅ | ✅ |
| Voice Selection | ✅ | ✅ |
| Voice Cloning | ✅ | ✅ |
| Batch Processing | ❌ | ✅ |
| Voice Comparison | ❌ | ✅ |
| Conversation Mode | ❌ | ✅ |
| CSV Upload | ❌ | ✅ |
| ZIP Download | ❌ | ✅ |

---

## 🖥️ Using the Apps

### Basic App Interface

1. **Select TTS Engine**
   - Edge TTS (6 voices)
   - Coqui XTTS (voice cloning)
   - gTTS (basic)

2. **Choose Voice**
   - Region: India/Singapore/Sri Lanka
   - Gender: Male/Female

3. **Enter Tamil Text**
   - Type or paste Tamil text
   - Use sample texts

4. **Generate & Download**
   - Click "Generate Speech"
   - Play audio
   - Download MP3/WAV

### Pro App Modes

#### 🎤 Single Generation
Same as basic app but with enhanced UI

#### 📦 Batch Processing
1. Choose input method:
   - Manual entry (one text per line)
   - Upload CSV file
   - Upload text file
2. Select voice
3. Generate all at once
4. Download as ZIP

#### 🔄 Voice Comparison
1. Enter one text
2. Select multiple voices
3. Generate all versions
4. Compare side-by-side

#### 💬 Conversation Mode
1. Add dialogue lines
2. Assign different voices to each speaker
3. Generate entire conversation
4. Download as ZIP

---

## 🌐 Deploy to Cloud

### Deploy to Streamlit Cloud (FREE)

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Tamil TTS Streamlit App"
   git remote add origin YOUR_GITHUB_REPO
   git push -u origin main
   ```

2. **Deploy on Streamlit Cloud**
   - Go to https://share.streamlit.io
   - Connect your GitHub repo
   - Select the app file
   - Deploy!

3. **Add `requirements.txt`**
   Create in your repo root:
   ```
   streamlit>=1.28.0
   edge-tts>=6.1.0
   pandas>=2.0.0
   ```

### Deploy to Hugging Face Spaces

1. Create new Space at https://huggingface.co/spaces
2. Select "Streamlit" as SDK
3. Upload your files
4. Add `requirements.txt`

### Deploy to Railway/Render

Similar process - most platforms support Streamlit out of the box!

---

## 🔧 Configuration

### Custom Port
```bash
streamlit run streamlit_tamil_tts_pro.py --server.port 8080
```

### Custom Theme
Create `.streamlit/config.toml`:
```toml
[theme]
primaryColor="#FF6B6B"
backgroundColor="#FFFFFF"
secondaryBackgroundColor="#F0F2F6"
textColor="#262730"
font="sans serif"
```

### Server Settings
```toml
[server]
headless = true
enableCORS = false
port = 8501
```

---

## 📱 Mobile-Friendly

Both apps are responsive and work on:
- 📱 Mobile phones
- 📊 Tablets
- 💻 Desktop browsers

---

## 🎨 Customization

### Change Colors
Edit CSS in the app file:
```python
st.markdown("""
    <style>
    .main-header {
        color: #YOUR_COLOR;
    }
    </style>
""", unsafe_allow_html=True)
```

### Add More Voices
Edit `EDGE_VOICES` dictionary to add/remove voices

### Modify Layout
Streamlit uses columns for layout:
```python
col1, col2, col3 = st.columns([1, 2, 1])
```

---

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'streamlit'"
```bash
pip install streamlit
```

### "ModuleNotFoundError: No module named 'edge_tts'"
```bash
pip install edge-tts
```

### Port Already in Use
```bash
streamlit run app.py --server.port 8502
```

### Slow Voice Cloning
- First time loads model (~2GB)
- Subsequent runs are faster
- Use Edge TTS for instant results

### File Upload Not Working
- Check file size limits
- Use WAV format for voice samples
- Ensure file permissions

---

## 📊 Performance Tips

1. **Use Edge TTS for Production**
   - Fast
   - High quality
   - No model loading

2. **Cache Coqui Model**
   - Model loads once per session
   - Stored in session_state

3. **Batch Processing**
   - Use Pro app for multiple files
   - Generates all at once

---

## 🔐 Security Notes

- Apps run locally by default
- No data sent to external servers (except TTS APIs)
- Uploaded files are temporary
- Clear session state on browser close

---

## 📖 Documentation

### Streamlit Docs
https://docs.streamlit.io

### Edge TTS Docs
https://github.com/rany2/edge-tts

### Coqui TTS Docs
https://docs.coqui.ai/en/latest/

---

## 🎓 Examples

### Example 1: Quick Test
```bash
# Start app
streamlit run streamlit_tamil_tts.py

# In browser:
# 1. Select "Edge TTS"
# 2. Choose "Pallavi (Female, India)"
# 3. Enter "வணக்கம்"
# 4. Click "Generate"
```

### Example 2: Batch Processing
```bash
# Start Pro app
streamlit run streamlit_tamil_tts_pro.py

# In browser:
# 1. Select "Batch Processing" mode
# 2. Choose "Manual Entry"
# 3. Enter multiple lines of text
# 4. Select voice
# 5. Generate all
# 6. Download ZIP
```

### Example 3: Voice Comparison
```bash
# In Pro app:
# 1. Select "Voice Comparison" mode
# 2. Enter one Tamil text
# 3. Select multiple voices
# 4. Generate comparison
# 5. Listen and compare
```

---

## 🚀 Advanced Features

### Session State Management
```python
if 'key' not in st.session_state:
    st.session_state.key = value
```

### File Download
```python
with open(file, 'rb') as f:
    st.download_button("Download", f.read())
```

### Progress Bars
```python
progress = st.progress(0)
for i in range(100):
    progress.progress(i + 1)
```

---

## 📞 Support

For issues:
1. Check console output
2. Verify all dependencies installed
3. Check Streamlit version compatibility
4. Review error messages

---

## 🎉 That's It!

You now have professional Tamil TTS web apps ready to use and deploy!

**Choose Your App:**
- Simple tasks → Basic App
- Advanced features → Pro App

**Deployment Options:**
- Local → `streamlit run app.py`
- Cloud → Streamlit Cloud / Hugging Face

---

**Made with ❤️ for Tamil speakers worldwide** 🇮🇳 🇱🇰 🇸🇬
