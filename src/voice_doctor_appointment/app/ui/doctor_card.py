"""Doctor card component for the Doctor Booking Assistant."""
import streamlit as st
from typing import Optional, Dict, Any
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from voice_doctor_appointment.app.models.doctor import Doctor
from voice_doctor_appointment.app.config import DEFAULT_DOCTOR_IMAGE

def show_doctor_info(doctor: Optional[Doctor]) -> None:
    """Display doctor information in a card.
    
    Args:
        doctor: Doctor object or dictionary to display, or None to show a placeholder
    """
    if not doctor:
        st.warning("No doctor information available.")
        return
    
    # Convert to dictionary if it's a Doctor object
    doctor_dict = doctor.to_dict() if hasattr(doctor, 'to_dict') else doctor
    
    with st.container():
        st.subheader("👨‍⚕️ Doctor Found!")
        
        # Create two columns for the layout
        col1, col2 = st.columns([1, 3])
        
        with col1:
            # Display doctor's image or placeholder
            st.image(
                doctor_dict.get('profile_image_url') or DEFAULT_DOCTOR_IMAGE,
                width=200,
                caption=doctor_dict.get('name', 'Doctor')
            )
        
        with col2:
            # Display doctor's information
            st.markdown(f"### {doctor_dict.get('name', 'Doctor')}")
            
            # Specialty
            if doctor_dict.get('specialty'):
                st.markdown(f"**Specialty:** {doctor_dict['specialty']}")
            
            # Address
            address = doctor_dict.get('location', {}).get('address')
            if address:
                st.markdown(f"**Address:** {address}")
            
            # Languages
            if hasattr(doctor, 'languages') and doctor.languages:
                languages = ", ".join(doctor.languages)
                st.markdown(f"**Languages:** {languages}")
            
            # Booking button
            if hasattr(doctor, 'booking_url') and doctor.booking_url:
                st.markdown(
                    f'<a href="{doctor.booking_url}" target="_blank" class="stButton">'
                    '📅 Book Appointment</a>',
                    unsafe_allow_html=True
                )
            
            # Add some space
            st.markdown("---")
            
            # Additional information if available
            if hasattr(doctor, 'description'):
                st.markdown("#### About")
                st.write(doctor.description)
            
            if hasattr(doctor, 'education') and doctor.education:
                with st.expander("Education"):
                    st.write(doctor.education)
            
            if hasattr(doctor, 'experience') and doctor.experience:
                with st.expander("Experience"):
                    st.write(doctor.experience)
            
            if hasattr(doctor, 'reviews') and doctor.reviews:
                with st.expander(f"Reviews ({len(doctor.reviews)})"):
                    for review in doctor.reviews:
                        st.markdown(f"**{review.get('author', 'Anonymous')}**")
                        st.markdown(f"*{review.get('date', '')}*")
                        st.write(review.get('text', ''))
                        st.markdown("---")
