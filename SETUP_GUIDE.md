# Tamil TTS + QuickVC Voice Converter Setup Guide

A Streamlit application that converts Tamil text to speech using gTTS and then converts the voice to match a target voice sample using QuickVC.

## 🔄 Workflow

```
Tamil Text → gTTS → Audio → QuickVC → Target Voice
```

## 📋 Prerequisites

- Python 3.8 or higher
- Git (for cloning QuickVC)
- CUDA-capable GPU (recommended for faster processing)

## 🚀 Installation

### Step 1: Clone this repository

```bash
git clone https://github.com/subiksha/tamil_Pesu.git
cd tamil_Pesu
```

### Step 2: Create a virtual environment (recommended)

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On Linux/Mac
source venv/bin/activate
```

### Step 3: Install Python dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Clone QuickVC (automatic or manual)

The app will automatically clone QuickVC when first run, or you can do it manually:

```bash
git clone https://github.com/quickvc/QuickVC-VoiceConversion.git
```

### Step 5: Download QuickVC Pretrained Model

1. Visit [QuickVC Releases](https://github.com/quickvc/QuickVC-VoiceConversion/releases)
2. Download the pretrained model file (e.g., `G_0.pth` or similar)
3. Place it in the `QuickVC-VoiceConversion/logs/quickvc/` directory:

```bash
mkdir -p QuickVC-VoiceConversion/logs/quickvc/
# Copy your downloaded model file
cp /path/to/G_0.pth QuickVC-VoiceConversion/logs/quickvc/
```

## 🎯 Running the Application

```bash
streamlit run streamlit_tamil_quickvc.py
```

The app will open in your browser at `http://localhost:8501`

## 📖 Usage

1. **Enter Tamil Text**: Type or paste Tamil text in the text area
2. **Upload Target Voice**: Upload a WAV or MP3 file of the voice you want to convert to
3. **Generate & Convert**: Click the button to generate TTS and convert the voice

### Sample Tamil Texts

- `வணக்கம், எப்படி இருக்கிறீர்கள்?` (Hello, how are you?)
- `நன்றி, நான் நன்றாக இருக்கிறேன்.` (Thank you, I'm fine.)
- `தமிழ் மிகவும் அழகான மொழி.` (Tamil is a beautiful language.)

## 🔧 Troubleshooting

### QuickVC Model Not Found

If you see a warning about QuickVC model not found:
1. Download the pretrained model from QuickVC releases
2. Place it in `QuickVC-VoiceConversion/logs/quickvc/`
3. Restart the app

### Fallback Conversion

If QuickVC is not available or the model is missing, the app will use a basic fallback voice conversion using spectral blending. This is not as high quality as QuickVC but still provides voice transformation.

### Audio Format Issues

The app automatically converts uploaded audio to:
- Sample rate: 16kHz
- Channels: Mono
- Format: WAV

## 📦 Project Structure

```
tamil_Pesu/
├── streamlit_tamil_quickvc.py  # Main application
├── streamlit_tamil_tts.py      # Original TTS app
├── requirements.txt            # Python dependencies
├── SETUP_GUIDE.md             # This file
├── generated_audio/           # Output directory (created automatically)
└── QuickVC-VoiceConversion/   # Cloned automatically or manually
    ├── convert.py
    ├── logs/
    │   └── quickvc/
    │       └── G_0.pth       # Pretrained model (download separately)
    └── ...
```

## 🛠️ Advanced Configuration

### Using a Different QuickVC Model

You can train your own QuickVC model or use a different pretrained model:

1. Train/fine-tune QuickVC on your target voice dataset
2. Place the model checkpoint in `QuickVC-VoiceConversion/logs/quickvc/`
3. The app will automatically detect and use it

### Customizing the Fallback Conversion

The fallback conversion uses spectral blending. You can adjust the blend factor in the code:

```python
alpha = 0.7  # Increase for more target voice characteristics
```

## 📝 Notes

- **Voice Quality**: QuickVC provides better voice conversion quality than the fallback method
- **Processing Time**: QuickVC conversion may take 10-30 seconds depending on your hardware
- **Target Voice**: Use a clear, clean voice sample (5-30 seconds) for best results
- **GPU Recommended**: QuickVC runs much faster on CUDA-enabled GPUs

## 🔗 Links

- [QuickVC Repository](https://github.com/quickvc/QuickVC-VoiceConversion)
- [gTTS Documentation](https://gtts.readthedocs.io/)
- [Streamlit Documentation](https://docs.streamlit.io/)

## 📄 License

This project combines multiple open-source tools. Please refer to individual licenses:
- QuickVC: Check their repository for license details
- gTTS: MIT License
- Streamlit: Apache 2.0
