"""Doctor card component for the Doctor Booking Assistant."""
import streamlit as st
from typing import Optional, Dict, Any, Tuple, List
import sys
from pathlib import Path
import pandas as pd
import textwrap
import time

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

def escape_html(text: Any) -> str:
    """Escape HTML special characters in text."""
    if not isinstance(text, str):
        text = str(text)
    return (
        text.replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;')
            .replace("'", '&#39;')
            .replace('\n', '<br>')
    )

def create_doctor_info_html(doctor_dict: Dict[str, Any]) -> str:
    """Create HTML content for doctor information."""
    # Get and escape values
    name = escape_html(doctor_dict.get('name', 'Doctor'))
    specialty = escape_html(doctor_dict.get('specialty', ''))
    address = escape_html(doctor_dict.get('location', {}).get('address', ''))
    phone = escape_html(doctor_dict.get('phone', ''))
    
    # Basic info
    html_parts = [f"<h3 class='doctor-name'>{name}</h3>"]
    
    # Specialty
    if specialty:
        html_parts.append(f"<div class='doctor-specialty'>{specialty}</div>")
    
    # Address
    if address:
        html_parts.append(
            f"<div class='doctor-info'>"
            f"<span class='info-icon'>📍</span> {address}"
            "</div>"
        )
    
    # Phone
    if phone:
        html_parts.append(
            f"<div class='doctor-info'>"
            f"<span class='info-icon'>📞</span> {phone}"
            "</div>"
        )
    
    # Languages
    if 'languages' in doctor_dict and doctor_dict['languages']:
        languages = ", ".join(escape_html(lang) for lang in doctor_dict['languages'])
        html_parts.append(
            f"<div class='doctor-info'>"
            f"<span class='info-icon'>🗣️</span> {languages}"
            "</div>"
        )
    
    # Booking button
    booking_url = doctor_dict.get('booking_url')
    if booking_url:
        primary_color = get_theme_colors()['primary']
        html_parts.append(
            f"<div style='margin-top: 1rem;'>"
            f"<a href='{escape_html(booking_url)}' target='_blank' "
            f"style='background-color: {primary_color}; color: white; "
            f"padding: 0.5rem 1rem; border-radius: 8px; text-decoration: none; display: inline-block;'>"
            "📅 Book Appointment</a>"
            "</div>"
        )
    
    return "\n".join(html_parts)

def generate_mock_available_dates() -> list:
    """Generate mock available dates for demonstration.
    
    Returns:
        List of dictionaries containing date and time slots
    """
    from datetime import datetime, timedelta
    
    # Generate dates for the next 7 days
    dates = []
    for i in range(1, 8):
        date = datetime.now() + timedelta(days=i)
        # Skip weekends
        if date.weekday() < 5:  # 0-4 = Monday to Friday
            # Generate 3 time slots per day
            time_slots = [
                ("09:00", "09:30"),
                ("11:00", "11:30"),
                ("14:00", "14:30")
            ]
            dates.append({
                'date': date.strftime('%Y-%m-%d'),
                'day': date.strftime('%A'),
                'time_slots': [f"{start} - {end}" for start, end in time_slots]
            })
    return dates

def show_doctor_info(doctor: Optional[Doctor], is_selected: bool = False) -> None:
    """Display doctor information using native Streamlit components.
    
    Args:
        doctor: Doctor object or dictionary to display, or None to show a placeholder
        is_selected: Whether this is the currently selected doctor
    """
    colors = get_theme_colors()
    
    if not doctor:
        st.warning("No doctor information available.")
        return
        
    # Convert Doctor object to dict if needed
    if hasattr(doctor, 'to_dict'):
        doctor_dict = doctor.to_dict()
    else:
        doctor_dict = doctor
        
    # Add selected styling if this is the selected doctor
    if is_selected:
        st.markdown("### ✅ Selected Doctor")
        st.markdown("---")
        
    # Generate mock available dates
    available_dates = generate_mock_available_dates()
    
    # Create tabs for better organization
    tab1, tab2, tab3 = st.tabs(["👨\u200d⚕️ Doctor Info", "📅 Available Dates", "📍 Location"])
    
    with tab1:
        # Create a container for the doctor card
        with st.container():
            st.markdown("---")
            
            # Create two columns for the layout
            col1, col2 = st.columns([1, 2])
            
            with col1:
                # Display doctor's image or placeholder
                profile_image = (
                    doctor.profile_image_url 
                    if hasattr(doctor, 'profile_image_url') and doctor.profile_image_url
                    else DEFAULT_DOCTOR_IMAGE
                )
                st.image(
                    profile_image,
                    width=250,
                    output_format='PNG'
                )
            
            with col2:
                # Doctor's name
                doctor_name = doctor.name if hasattr(doctor, 'name') else 'Doctor'
                st.subheader(doctor_name)
                
                # Contact information
                st.markdown("---")
                
                # Address
                if hasattr(doctor, 'location') and hasattr(doctor.location, 'get') and doctor.location.get('address'):
                    st.markdown(f"📍 **Address:** {doctor.location['address']}")
                
                # Phone
                phone = getattr(doctor, 'phone', None)
                if phone:
                    st.markdown(f"📞 **Phone:** {phone}")
                
                # Gender
                gender = getattr(doctor, 'gender', None)
                if gender:
                    gender_emoji = "👩‍⚕️" if gender.lower() == 'female' else "👨‍⚕️" if gender.lower() == 'male' else "👤"
                    st.markdown(f"{gender_emoji} **Gender:** {gender.capitalize()}")
                
                # Languages
                languages = getattr(doctor, 'languages', None)
                if languages:
                    languages_str = ", ".join(languages) if isinstance(languages, list) else str(languages)
                    st.markdown(f"🗣️ **Languages:** {languages_str}")
                
                # Specialty
                specialty = getattr(doctor, 'specialty', None)
                if specialty:
                    st.markdown(f"⚕️ **Specialty:** {specialty}")
                
                # Booking button (commented out as per previous changes)
                # if hasattr(doctor, 'booking_url') and doctor.booking_url:
                #     st.markdown("---")
                #     st.markdown(f"[📅 Book Appointment]({doctor.booking_url})")
            
            # Additional information in expanders
            description = getattr(doctor, 'description', None)
            if description:
                with st.expander("About"):
                    st.write(description)
            
            education = getattr(doctor, 'education', None)
            if education:
                with st.expander("Education"):
                    st.write(education)
            
            experience = getattr(doctor, 'experience', None)
            if experience:
                with st.expander("Experience"):
                    st.write(experience)
            
            reviews = getattr(doctor, 'reviews', None)
            if reviews:
                with st.expander(f"Reviews ({len(reviews)})"):
                    for review in reviews:
                        author = review.get('author', 'Anonymous') if hasattr(review, 'get') else 'Anonymous'
                        date = review.get('date', '') if hasattr(review, 'get') else ''
                        text = review.get('text', '') if hasattr(review, 'get') else str(review)
                        
                        st.markdown(f"**{author}**")
                        if date:
                            st.markdown(f"*{date}*")
                        st.write(text)
                        st.markdown("---")
            
            st.markdown("---")
    
    with tab2:
        st.subheader("Available Appointments")
        
        if not available_dates:
            st.info("No available dates at the moment. Please check back later.")
        else:
            for date_info in available_dates:
                with st.expander(f"{date_info['date']} ({date_info['day']})"):
                    cols = st.columns(3)  # 3 time slots per row
                    for i, time_slot in enumerate(date_info['time_slots']):
                        with cols[i % 3]:
                            # Create a unique key using doctor ID (or name if ID not available), date, time slot index, and a timestamp
                            doctor_id = getattr(doctor, 'id', getattr(doctor, 'name', 'doctor'))
                            if isinstance(doctor_id, str):
                                doctor_id = doctor_id.replace(' ', '_')
                            time_slot_key = f"slot_{doctor_id}_{date_info['date']}_{i}_{int(time.time())}"
                            
                            if st.button(time_slot, key=time_slot_key):
                                st.session_state['selected_slot'] = {
                                    'date': date_info['date'],
                                    'day': date_info['day'],
                                    'time': time_slot,
                                    'doctor_name': getattr(doctor, 'name', 'the doctor'),
                                    'doctor_id': getattr(doctor, 'id', None)
                                }
                                st.success(f"Selected {time_slot} on {date_info['date']}")
            

    with tab3:
        # Display map if coordinates are available
        if hasattr(doctor, 'location') and doctor.location:
            location = doctor.location
            coords = extract_coordinates(location if isinstance(location, dict) else location.__dict__)
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
                address = None
                if hasattr(location, 'get') and callable(location.get):
                    address = location.get('address')
                elif hasattr(location, 'address'):
                    address = location.address
                
                if address:
                    st.markdown(f"**Address:** {address}")
        else:
            st.info("No location information available for this doctor.")
