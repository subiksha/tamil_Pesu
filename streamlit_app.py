"""
Streamlit Cloud Entry Point
Redirects to the main Tamil TTS + QuickVC application
"""

import streamlit as st
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import and run the main app
from streamlit_tamil_quickvc import main

if __name__ == "__main__":
    main()
