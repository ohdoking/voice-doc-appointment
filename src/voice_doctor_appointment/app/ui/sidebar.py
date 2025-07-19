"""Sidebar component for the Doctor Booking Assistant."""
import streamlit as st
from typing import Tuple
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

def show_sidebar() -> Tuple[int, bool]:
    """Display the application sidebar.
    
    Returns:
        Tuple containing:
        - recording_duration: Duration for voice recording in seconds
        - debug_mode: Whether debug mode is enabled
    """
    with st.sidebar:
        st.header("Settings")
        
        # Recording settings
        st.subheader("Recording Settings")
        recording_duration = st.slider(
            "Recording duration (seconds)",
            min_value=1,
            max_value=30,
            value=10,
            help="How long to record voice input"
        )
        
        # Debug settings
        st.subheader("Debug")
        debug_mode = st.checkbox(
            "Enable debug mode",
            value=True,
            help="Show additional debug information"
        )
        
        # App information
        st.markdown("---")
        st.subheader("How to Use")
        st.markdown("1. Click 'Start Recording' and speak your request")
        st.markdown("2. The system will find matching doctors")
        st.markdown("3. View and book appointments")
        
        # Version information
        st.markdown("---")
        st.caption("Doctor Booking Assistant v1.0.0")
    
    return recording_duration, debug_mode
