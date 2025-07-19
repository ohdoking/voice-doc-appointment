"""Doctor card component for the Doctor Booking Assistant."""
import streamlit as st
from typing import Optional, Dict, Any, Tuple, List
import sys
from pathlib import Path
import pandas as pd
import textwrap

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from voice_doctor_appointment.app.models.doctor import Doctor
from voice_doctor_appointment.app.config import DEFAULT_DOCTOR_IMAGE

def get_theme_colors() -> Dict[str, str]:
    """Get theme-appropriate colors based on Streamlit's theme."""
    # Default colors (light theme)
    colors = {
        'bg': '#ffffff',
        'card_bg': '#f8f9fa',
        'text': '#31333f',
        'primary': '#1f77b4',
        'secondary': '#6c757d',
        'border': '#dee2e6',
    }
    
    # Check if dark theme is active
    try:
        if st.get_theme().base == 'dark':
            colors.update({
                'bg': '#0e1117',
                'card_bg': '#1e2130',
                'text': '#f0f2f6',
                'primary': '#4e8bfd',
                'secondary': '#a4b1cd',
                'border': '#2a2f3b',
            })
    except:
        pass
        
    return colors

def create_rounded_card(html_content: str) -> None:
    """Create a styled card with rounded corners and shadow."""
    colors = get_theme_colors()
    st.markdown(
        f"""
        <style>
            .doctor-card {{
                background-color: {colors['card_bg']};
                border-radius: 12px;
                padding: 1.5rem;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                border: 1px solid {colors['border']};
                margin-bottom: 1.5rem;
            }}
            .doctor-name {{
                color: {colors['primary']} !important;
                font-size: 1.5rem !important;
                font-weight: 700 !important;
                margin-bottom: 0.5rem !important;
            }}
            .doctor-specialty {{
                color: {colors['primary']} !important;
                font-weight: 600 !important;
                margin-bottom: 0.5rem !important;
                font-size: 1.1rem !important;
            }}
            .doctor-info {{
                color: {colors['text']} !important;
                margin-bottom: 0.5rem !important;
                font-size: 0.95rem !important;
            }}
            .info-icon {{
                margin-right: 0.5rem;
                color: {colors['primary']} !important;
            }}
            .stTabs [data-baseweb="tab-list"] {{
                border-bottom: 1px solid {colors['border']} !important;
            }}
            .stTabs [data-baseweb="tab"] {{
                color: {colors['text']} !important;
            }}
            .stTabs [aria-selected="true"] {{
                color: {colors['primary']} !important;
                border-bottom: 2px solid {colors['primary']} !important;
            }}
        </style>
        <div class="doctor-card">
            {html_content}
        </div>
        """,
        unsafe_allow_html=True
    )

def extract_coordinates(location_data: Dict[str, Any]) -> Optional[Tuple[float, float]]:
    """Extract latitude and longitude from location data.
    
    Args:
        location_data: Dictionary containing location information
        
    Returns:
        Tuple of (latitude, longitude) or None if not available
    """
    # Check for flat coordinates first (direct lat/lng in the location object)
    if 'lat' in location_data and 'lng' in location_data:
        return (float(location_data['lat']), float(location_data['lng']))
    
    # Check for nested gpsPoint structure
    if 'gpsPoint' in location_data and isinstance(location_data['gpsPoint'], dict):
        gps = location_data['gpsPoint']
        if 'lat' in gps and 'lng' in gps:
            return (float(gps['lat']), float(gps['lng']))
    
    # Check for viewport center as fallback
    if 'viewport' in location_data and isinstance(location_data['viewport'], dict):
        viewport = location_data['viewport']
        if 'northeast' in viewport and 'southwest' in viewport:
            ne = viewport.get('northeast', {})
            sw = viewport.get('southwest', {})
            
            if all(k in ne for k in ['lat', 'lng']) and all(k in sw for k in ['lat', 'lng']):
                lat = (float(ne['lat']) + float(sw['lat'])) / 2
                lng = (float(ne['lng']) + float(sw['lng'])) / 2
                return (lat, lng)
    
    return None

def create_doctor_info_html(doctor_dict: Dict[str, Any]) -> str:
    """Create HTML content for doctor information."""
    # Basic info
    html_parts = [
        f"<h3 class='doctor-name'>{doctor_dict.get('name', 'Doctor')}</h3>"
    ]
    
    # Specialty
    if doctor_dict.get('specialty'):
        html_parts.append(f"<div class='doctor-specialty'>{doctor_dict['specialty']}</div>")
    
    # Address
    address = doctor_dict.get('location', {}).get('address')
    if address:
        html_parts.append(
            f"<div class='doctor-info'>"
            f"<span class='info-icon'>📍</span> {address}"
            "</div>"
        )
    
    # Phone
    phone = doctor_dict.get('phone')
    if phone:
        html_parts.append(
            f"<div class='doctor-info'>"
            f"<span class='info-icon'>📞</span> {phone}"
            "</div>"
        )
    
    # Languages
    if 'languages' in doctor_dict and doctor_dict['languages']:
        languages = ", ".join(doctor_dict['languages'])
        html_parts.append(
            f"<div class='doctor-info'>"
            f"<span class='info-icon'>🗣️</span> {languages}"
            "</div>"
        )
    
    # Booking button
    if doctor_dict.get('booking_url'):
        html_parts.append(
            f"<div style='margin-top: 1rem;'>"
            f"<a href='{doctor_dict['booking_url']}' target='_blank' "
            f"style='background-color: {get_theme_colors()['primary']}; color: white; "
            f"padding: 0.5rem 1rem; border-radius: 8px; text-decoration: none;'>"
            "📅 Book Appointment</a>"
            "</div>"
        )
    
    return "\n".join(html_parts)

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
    
    # Create tabs for better organization
    tab1, tab2 = st.tabs(["👨‍⚕️ Doctor Info", "📍 Location"])
    
    with tab1:
        # Create two columns for the layout
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # Display doctor's image or placeholder
            st.image(
                doctor_dict.get('profile_image_url') or DEFAULT_DOCTOR_IMAGE,
                output_format='PNG'
            )
        
        with col2:
            # Create and display the doctor info card
            html_content = create_doctor_info_html(doctor_dict)
            create_rounded_card(html_content)
            
            # Additional information in expanders
            if doctor_dict.get('description'):
                with st.expander("About"):
                    st.write(doctor_dict['description'])
            
            if doctor_dict.get('education'):
                with st.expander("Education"):
                    st.write(doctor_dict['education'])
            
            if doctor_dict.get('experience'):
                with st.expander("Experience"):
                    st.write(doctor_dict['experience'])
            
            if doctor_dict.get('reviews'):
                with st.expander(f"Reviews ({len(doctor_dict['reviews'])})"):
                    for review in doctor_dict['reviews']:
                        st.markdown(f"**{review.get('author', 'Anonymous')}**")
                        st.markdown(f"*{review.get('date', '')}*")
                        st.write(review.get('text', ''))
                        st.markdown("---")
    
    with tab2:
        # Display map if coordinates are available
        if 'location' in doctor_dict and doctor_dict['location']:
            coords = extract_coordinates(doctor_dict['location'])
            if coords:
                lat, lng = coords
                # Create a DataFrame with the coordinates
                map_data = pd.DataFrame({
                    'lat': [lat],
                    'lon': [lng]
                })
                # Display the map with a marker at the doctor's location
                st.map(map_data, zoom=14, use_container_width=True)
                
                # Show address below map
                address = doctor_dict.get('location', {}).get('address')
                if address:
                    st.markdown(f"**Address:** {address}")
        else:
            st.info("Location information not available.")
