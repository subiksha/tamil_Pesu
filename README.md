---
title: Tamil TTS + Voice Cloning
emoji: 🎙️
colorFrom: red
colorTo: purple
sdk: streamlit
sdk_version: 1.28.0
app_file: app.py
pinned: false
license: mit
---

# 🎙️ Tamil TTS + Voice Cloning

Convert Tamil text to speech using gTTS, then clone the voice to match your voice using Microsoft SpeechT5 AI.

## 🔄 Workflow

```
Tamil Text → gTTS → 🔊 → SpeechT5 AI → 🎭 → Your Voice Clone
```

## 🚀 Powered By

- **gTTS** - Google Text-to-Speech for Tamil language support
- **Microsoft SpeechT5** - State-of-the-art voice conversion (Hugging Face Transformers)
- **WavLM** - Speaker embedding extraction for voice characteristics
- **Hugging Face Spaces** - Free hosting with GPU/CPU support

## 📖 How to Use

1. **Enter Tamil Text** - Type or paste Tamil text in the input field
2. **Upload Your Voice** - Upload a 5-30 second voice sample (WAV or MP3)
3. **Generate & Clone** - Click the button to convert and clone
4. **Download** - Save your cloned voice audio

## 💡 Tips

- Use clear speech without background noise for best results
- 10-20 seconds of voice sample works best
- The first run will download models (may take 1-2 minutes)

## 🛠️ Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
streamlit run app.py
```

## 📄 License

MIT License - See LICENSE file for details
