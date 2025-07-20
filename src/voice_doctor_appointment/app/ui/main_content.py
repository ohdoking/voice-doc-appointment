"""Main content component for the Doctor Booking Assistant."""
import streamlit as st
from typing import Optional, Dict, Any, List
import json
import sys
from pathlib import Path
import os
import openai
from dotenv import load_dotenv
import time

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from voice_doctor_appointment.app.models.doctor import Doctor
from voice_doctor_appointment.app.models.location import Location
from voice_doctor_appointment.app.services.voice_service import VoiceService
from voice_doctor_appointment.app.services.doctor_service import DoctorService
from voice_doctor_appointment.app.ui.doctor_card import show_doctor_info
from voice_doctor_appointment.app.config import APP_NAME, APP_ICON

# Load environment variables
env_path = project_root / '.env'

# Load environment variables
load_dotenv(env_path, override=True)

openai.api_key = os.getenv("OPENAI_API_KEY")

def display_chat_message(role: str, content: str) -> None:
    """Display a chat message in the Streamlit app.
    
    Args:
        role: Either 'user' or 'assistant'
        content: The message content
    """
    with st.chat_message(role):
        st.markdown(content)

def show_main_content(
    voice_service: VoiceService,
    doctor_service: DoctorService,
    recording_duration: int,
    debug_mode: bool = False
) -> None:
    """Display the main content of the application with a chat interface.
    
    Args:
        voice_service: Instance of VoiceService for voice interactions
        doctor_service: Instance of DoctorService for doctor-related operations
        recording_duration: Duration for voice recording in seconds
        debug_mode: Whether to show debug information
    """
    st.title(f"{APP_ICON} {APP_NAME}")
    
    # Initialize session state variables if they don't exist
    if 'messages' not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! I'm here to help you find the right doctor. Please tell me about your symptoms and location."}
        ]
    if 'recording' not in st.session_state:
        st.session_state.recording = False
    if 'doctor' not in st.session_state:
        st.session_state.doctor = None
    if 'transcript' not in st.session_state:
        st.session_state.transcript = ""
    if 'extracted_info' not in st.session_state:
        st.session_state.extracted_info = None
    
    # Display doctor information in a persistent container if available
    if 'doctor' in st.session_state and st.session_state.doctor:
        show_doctor_info(st.session_state.doctor)
        st.markdown("---")
    
    # Display chat messages
    for message in st.session_state.messages:
        display_chat_message(message["role"], message["content"])
    
    # Chat input area
    if st.button("🎤 Start Voice Recording", type="primary", use_container_width=True):
        st.session_state.recording = True
        # display_chat_message("user", "(Recording...)")
        
        try:
            # Record voice input
            st.session_state.transcript = voice_service.ask_voice(
                "Please describe your symptoms and tell me your location.",
                duration=recording_duration
            )

            # st.session_state.transcript = """
            # i have allergie from last night, i live in berlin pankow, i only can speak english. and i have public insurance. and i want male doctor.
            # """
            
            if st.session_state.transcript:
                # Add user message to chat
                st.session_state.messages.append({"role": "user", "content": st.session_state.transcript})
                
                # Process the transcript
                with st.spinner("Helping you find the right doctor and booking an appointment..."):
                    st.session_state.extracted_info = extract_doctor_info(st.session_state.transcript)
                    
                    if st.session_state.get('Initialize', True):
                        if st.session_state.extracted_info:
                            # Find multiple doctors based on the extracted information (max 5)
                            st.session_state.doctors = find_doctors(
                                doctor_service,
                                st.session_state.extracted_info,
                                debug_mode
                            )
                            
                        # Initialize doctor index if not set
                        if 'current_doctor_index' not in st.session_state:
                            st.session_state.current_doctor_index = 0
                            
                        # Check if we found any doctors
                        if st.session_state.doctors:
                            # Get current doctor
                        
                            current_doctor = st.session_state.doctors[st.session_state.current_doctor_index]
                            doctor_dict = current_doctor.to_dict() if hasattr(current_doctor, 'to_dict') else current_doctor
                            
                            # First message with doctor details
                            # doctor_details = (
                            #     f"I found a {st.session_state.extracted_info.get('recommended_specialty', 'doctor')} "
                            #     f"in {st.session_state.extracted_info.get('location', 'your area')}.\n\n"
                            #     f"**Option {st.session_state.current_doctor_index + 1} of {len(st.session_state.doctors)}**\n\n"
                            #     f"**{doctor_dict.get('name', 'Doctor')}**\n"
                            #     f"📍 {doctor_dict.get('location', {}).get('address', 'Address not available')}\n"
                            #     f"📞 {doctor_dict.get('phone', 'Phone not available')}\n\n"
                            #     f"Say 'I like it' to book this doctor or 'Next option' to see another option."
                            # )
                            # # Add doctor details to chat
                            # st.session_state.messages.append({"role": "assistant", "content": doctor_details})
                            st.session_state.current_doctor = doctor_dict
                            
                            # # Show doctor info card
                            # show_doctor_info(current_doctor)
                            
                            # Set flag to listen for user's choice
                            st.session_state.awaiting_doctor_choice = True
                            
                        else:
                            response = "I couldn't find any matching doctors. Could you provide more details about what you're looking for?"
                            st.session_state.messages.append({"role": "assistant", "content": response})
                    
                    # Handle doctor choice if we're waiting for it
                    if st.session_state.get('awaiting_doctor_choice'):
                        # Reset initialization flag
                        st.session_state.Initialize = False
                        
                        # Use a while loop to handle doctor selection
                        while st.session_state.get('awaiting_doctor_choice', False):
                            # Show the current doctor's info
                            current_doctor = st.session_state.doctors[st.session_state.current_doctor_index]
                            show_doctor_info(current_doctor)
                            
                            # Listen for user's response
                            with st.spinner("Listening for your choice..."):
                                # Create a 2-second delay with progress indicator
                                progress_text = "Waiting for taking a look of your option ..."
                                progress_bar = st.progress(0, text=progress_text)
                                for i in range(100):
                                    time.sleep(0.05)  # 2 seconds total
                                    progress_bar.progress(i + 1, text=progress_text)
                                progress_bar.empty()
                                
                                answer = voice_service.ask_voice(
                                    "Would you like to book this doctor or see another option?",
                                    duration=5
                                )
                            
                            if not answer:
                                continue  # Skip if no answer was provided
                                
                            st.session_state.messages.append({"role": "user", "content": answer})
                            answer_lower = answer.lower()
                            
                            # Process user's choice
                            if "next" in answer_lower or "other" in answer_lower or "option" in answer_lower:
                                # Show next doctor if available
                                if st.session_state.current_doctor_index + 1 < len(st.session_state.doctors):
                                    st.session_state.current_doctor_index += 1
                                    continue  # Show next doctor
                                else:
                                    st.session_state.messages.append({
                                        "role": "assistant", 
                                        "content": "I'm sorry, there are no more options available. Please try a different search."
                                    })
                                    st.session_state.awaiting_doctor_choice = False
                                    st.session_state.current_doctor_index = 0
                                
                            elif "like" in answer_lower or "book" in answer_lower or "yes" in answer_lower:
                                # User wants to book this doctor
                                st.session_state.awaiting_doctor_choice = False
                                st.session_state.ask_for_booking_confirmation = True
                                break  # Exit the loop to proceed with booking
                                
                            else:
                                # Unclear response, ask again
                                st.session_state.messages.append({
                                    "role": "assistant",
                                    "content": "I didn't catch that. Please say 'I like it' to book this doctor or 'Next option' to see another option."
                                })
                                continue  # Ask the same question again
                                
                            st.session_state.Initialize = True
                            break  # Exit the loop if we reach here
                        st.session_state.current_doctor = st.session_state.doctors[st.session_state.current_doctor_index]    
                        
                    if st.session_state.get('ask_for_booking_confirmation'):
                        # Reset the flag first to prevent asking again
                        st.session_state.ask_for_booking_confirmation = False
                        st.session_state.awaiting_booking_confirmation = True
                        
                        # Ask for confirmation
                        confirmation_prompt = "Would you like to book an appointment? Please say yes or no."
                        st.session_state.messages.append({"role": "assistant", "content": confirmation_prompt})
                        
                        # Get voice response
                        with st.spinner("Listening for your response..."):
                            answer = voice_service.ask_voice(confirmation_prompt, duration=2)
                            
                        if answer:
                            st.session_state.messages.append({"role": "user", "content": answer})
                            
                            if "yes" in answer.lower():
                                # Get the doctor details
                                doctor = st.session_state.get('current_doctor')
                                if doctor is not None:
                                    # Use getattr to safely access attributes
                                    doctor_link = getattr(doctor, 'link', '')
                                    doctor_name = getattr(doctor, 'name', 'the doctor')
                                    
                                    # Construct booking URL
                                    booking_url = f"https://www.doctolib.de{doctor_link}" if doctor_link else "#"
                                    confirm_text = f"Great! I'll help you book an appointment with Dr. {doctor_name}. Please visit the following link to proceed with your booking: {booking_url}"
                                    
                                    # Add the message and link
                                    st.session_state.messages.append({"role": "assistant", "content": confirm_text})
                                    
                                    # Add a clickable link
                                    if doctor_link:
                                        st.markdown(f"[Click here to book an appointment with Dr. {doctor_name}]({booking_url})")
                                    else:
                                        st.warning("No booking link available for this doctor.")
                                else:
                                    st.session_state.messages.append({
                                        "role": "assistant",
                                        "content": "I'm sorry, I couldn't find the doctor's information. Please try searching again."
                                    })
                            else:
                                st.session_state.messages.append({
                                    "role": "assistant",
                                    "content": "No problem! Let me know if you need help with anything else."
                                })
                            
                            # Reset the booking confirmation state
                            st.session_state.awaiting_booking_confirmation = False
                            del st.session_state.current_doctor
                            st.session_state.Initialize = True
                            # Rerun to update the UI
                            st.rerun()
                        
                        # Rerun to update the chat display
                        st.rerun()
                    else:
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": "I couldn't understand your request. Could you please describe your symptoms and location again?"
                        })
                        st.session_state.Initialize = True
                        st.rerun()
                        
        except Exception as e:
            print("error!!!!!", {str(e)})
            st.error(f"An error occurred: {str(e)}")
            st.session_state.messages.append({
                "role": "assistant",
                "content": "I'm sorry, I encountered an error. Please try again."
            })
            st.rerun()
            
        finally:
            st.session_state.recording = False
    
    # Debug information (collapsible)
    if debug_mode and 'extracted_info' in st.session_state and st.session_state.extracted_info:
        with st.expander("Debug Information"):
            st.json({
                "transcript": st.session_state.transcript,
                "extracted_info": st.session_state.extracted_info,
                "doctor": st.session_state.doctor
            })

def extract_doctor_info(transcript: str) -> Dict[str, Any]:
    system_prompt = """
    You are an assistant that helps users find the right medical specialist based on their symptoms and preferences.
    
    Your tasks:
    1. Analyze the user's description of their symptoms or health concern
    2. Determine the most appropriate medical specialty that would handle these symptoms
    3. Extract the following information:
       - recommended_specialty: The most relevant medical specialty (e.g., "dermatologist", "cardiologist", "general practitioner")
       - location: City, district, or place name where the doctor should be located
       - languages_found: List of language codes from the user's input
       - gender: The preferred gender of the doctor. MUST be one of: null, "male", or "female" (case-sensitive). 
                 If not specified or unclear, use null. Do not use any other values.
    
    For recommended_specialty, choose from common medical specialties. If the user's description is vague or could apply to multiple specialties,
    recommend seeing a general practitioner first.
    
    For languages_found, use these exact codes:
    - "de" (German)
    - "gb" (English)
    - "ar" (Arabic)
    - "cn" (Chinese)
    - "es" (Spanish)
    - "fr" (French)
    - "gr" (Greek)
    - "it" (Italian)
    - "jp" (Japanese)
    - "sgn" (Sign language)
    - "fa" (Persian)
    - "pl" (Polish)
    - "pt" (Portuguese)
    - "ro" (Romanian)
    - "ru" (Russian)
    - "tr" (Turkish)
    - "ua" (Ukrainian)
    
    Return ONLY a JSON object with these exact keys: recommended_specialty, location, languages_found, gender.
    
    Example 1:
    User: "I have a toothache and need to see a female doctor in Berlin who speaks German and English"
    {
        "recommended_specialty": "dentist",
        "location": "Berlin",
        "languages_found": ["de", "gb"],
        "gender": "female"
    }
    
    Example 2:
    User: "I've been having chest pain and need a male doctor in Paris who speaks French"
    {
        "recommended_specialty": "cardiologist",
        "location": "Paris",
        "languages_found": ["fr"],
        "gender": "male"
    }
    
    Example 3:
    User: "I have a rash on my arm and need someone in Madrid who speaks Spanish"
    {
        "recommended_specialty": "dermatologist",
        "location": "Madrid",
        "languages_found": ["es"],
        "gender": null
    }
    """

    client = openai.OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": transcript},
        ],
        temperature=0.2,
    )

    content = response.choices[0].message.content.strip()
    
    # Handle markdown code blocks by removing them
    if content.startswith('```json') and content.endswith('```'):
        content = content[7:-3].strip()  # Remove ```json and ```
    elif content.startswith('```') and content.endswith('```'):
        content = content[3:-3].strip()  # Remove ``` and ```
    
    try:
        extracted = json.loads(content)
        recommended_specialty = extracted.get("recommended_specialty")
        location = extracted.get("location")
        languages_found = extracted.get("languages_found", [])
        gender = extracted.get("gender")
        
        # Validate gender is one of: null, "male", or "female"
        if gender is not None and gender not in ["male", "female"]:
            gender = None  # Reset to null if invalid value
            
        if not recommended_specialty or not location:
            raise ValueError("Missing required fields in response")
            
    except (json.JSONDecodeError, ValueError) as e:
        print(f"Error processing GPT response: {e}")
        print(f"Raw response: {content}")
        return None

    return {
        "symptom": recommended_specialty,  # Keeping 'symptom' key for backward compatibility
        "recommended_specialty": recommended_specialty,
        "location": location,
        "languages_found": languages_found,
        "gender": gender  # Will be one of: null, "male", or "female"
    }

def find_doctors(
    doctor_service: DoctorService,
    extracted_info: Dict[str, Any],
    debug_mode: bool = False,
    max_results: int = 5
) -> List[Dict[str, Any]]:
    """Find multiple doctors based on extracted information.
    
    Args:
        doctor_service: Instance of DoctorService
        extracted_info: Dictionary containing extracted information
        debug_mode: Whether to show debug information
        max_results: Maximum number of doctors to return (default: 5)
        
    Returns:
        List of Doctor objects if found, empty list otherwise.
    """
    error_info = {}
    
    try:
        # 1. Validate input
        if not extracted_info:
            raise ValueError("No information was extracted from the input")
            
        location_name = extracted_info.get('location', '').strip()
        if not location_name:
            raise ValueError("No location was specified in your request")
        
        # 2. Get specialty information
        specialty_name = extracted_info.get('recommended_specialty', '')
        if not specialty_name:
            raise ValueError("No medical specialty was specified in your request")
            
        if debug_mode:
            print(f"🔍 Looking for {specialty_name} in {location_name}")
        
        specialty = doctor_service.get_specialty_info(specialty_name)
        if not specialty or 'name' not in specialty:
            raise ValueError(f"Could not find information for specialty: {specialty_name}")
            
        # 3. Resolve location details
        if debug_mode:
            print(f"📍 Resolving location: {location_name}")
            
        location_data = doctor_service.resolve_location_name(location_name)
        if not location_data or 'place_id' not in location_data:
            raise ValueError(f"Could not find location: {location_name}")
        
        # 4. Prepare location payload for Doctolib API
        place_info = {
            "id": 1419927,  # This should be dynamic in production
            "placeId": location_data.get('place_id'),
            "name": location_name.split(",")[0],
            "nameWithPronoun": f"in {location_name.split(',')[0]}",
            "slug": None,
            "country": "de",
            "viewport": {
                "northeast": {"lat": 52.5660121802915, "lng": 13.3949812802915},
                "southwest": {"lat": 52.5633142197085, "lng": 13.3922833197085},
            },
            "type": "route",
            "zipcodes": [],
            "gpsPoint": {"lat": 52.5646632, "lng": 13.3936323},
            "locality": location_name.split(",")[0],  # Use first part as locality
            "streetName": None,
            "streetNumber": None,
        }
        
        if debug_mode:
            print("📝 Prepared location info:", json.dumps(place_info, indent=2))
            
        # 5. Search for doctors
        if debug_mode:
            print(f"🔎 Searching for {specialty['slug']} doctors in {location_name}...")
            
        doctors = doctor_service.search_doctors(
            place=place_info,
            specialty=specialty['slug'],
            languages=extracted_info.get('languages_found', [])
        )
        
        if debug_mode:
            if doctors:
                print(f"✅ Found {len(doctors)} doctors")
            else:
                print("❌ No doctors found matching the criteria")
        
        # 6. Return up to max_results doctors
        if doctors:
            if debug_mode:
                print(f"👨‍⚕️ Found {len(doctors)} doctors")
            # Return up to max_results doctors
            return doctors[:max_results]
            
        return []
        
    except ValueError as ve:
        error_msg = f"❌ {str(ve)}"
        if debug_mode:
            error_info = {
                "error": str(ve),
                "type": "validation",
                "extracted_info": extracted_info,
                "traceback": None
            }
            print(f"❌ Validation error: {ve}")
        st.error(error_msg)
        return []
        
    except Exception as e:
        import traceback
        error_msg = "❌ An error occurred while searching for doctors"
        if debug_mode:
            error_info = {
                "error": str(e),
                "type": type(e).__name__,
                "extracted_info": extracted_info,
                "traceback": traceback.format_exc()
            }
            print(f"❌ Unexpected error: {str(e)}\n{traceback.format_exc()}")
        st.error(error_msg)
        return []
        
    finally:
        if debug_mode and error_info:
            print("\n🔍 Debug Information:")
            print(json.dumps(error_info, indent=2))
