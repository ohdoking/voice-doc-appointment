"""
MediMatch Voice - Streamlit Application

This is the main entry point for the MediMatch Voice application.
It provides a voice-enabled interface for finding and booking healthcare providers.
"""
import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import streamlit as st
from dotenv import load_dotenv

# Import UI components
from voice_doctor_appointment.app.ui.sidebar import show_sidebar
from voice_doctor_appointment.app.ui.main_content import show_main_content

# Import services
from voice_doctor_appointment.app.services.voice_service import VoiceService
from voice_doctor_appointment.app.services.doctor_service import DoctorService

# Load environment variables
load_dotenv(project_root / '.env')

def main():
    """Main entry point for the MediMatch Voice application."""
    # Initialize services
    voice_service = VoiceService()
    doctor_service = DoctorService()
    
    # Configure page settings
    st.set_page_config(
        page_title="MediMatch Voice",
        page_icon="🏥",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Show sidebar and get settings
    recording_duration, debug_mode = show_sidebar()
    
    # Show main content
    show_main_content(
        voice_service=voice_service,
        doctor_service=doctor_service,
        recording_duration=recording_duration,
        debug_mode=debug_mode
    )

if __name__ == "__main__":
    main()
