"""Doctor service for handling doctor-related operations."""
import requests
from typing import List, Dict, Any, Optional
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from voice_doctor_appointment.app.models.doctor import Doctor
from voice_doctor_appointment.app.models.location import Location
from voice_doctor_appointment.app.config import DOCTOLIB_BASE_URL, DEFAULT_HEADERS

class DoctorService:
    """Service for handling doctor-related operations."""
    
    @staticmethod
    def search_doctors(
        place: Dict,
        specialty: str,
        languages: List[str],
        insurance_sector: str = "public"
    ) -> List[Doctor]:
        """Search for doctors based on location, specialty, and languages."""
        url = f"{DOCTOLIB_BASE_URL}/phs_proxy/raw?page=0"
        
        payload = {
            "keyword": specialty,
            "location": {"place": place},
            "filters": {"insuranceSector": insurance_sector},
            "languages": languages,
        }
        
        print("phs_proxy payload", payload)
        try:
            response = requests.post(
                url,
                json=payload,
                headers=DEFAULT_HEADERS,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            doctors = data.get("healthcareProviders", [])
            
            # Process doctors data
            processed_doctors = []
            for doc in doctors:
                # Skip telehealth providers
                if doc.get("onlineBooking", {}).get("telehealth", False):
                    continue
                    
                # Add profile image URL if cloudinaryPublicId exists
                cloudinary_id = doc.get("cloudinaryPublicId")
                if cloudinary_id:
                    doc["profile_image_url"] = f"https://media.doctolib.com/image/upload/q_auto:eco,f_auto,dpr_2/w_62,h_62,c_fill,g_face/{cloudinary_id}"
                
                # Clean and set specialty, ensuring no newlines or extra whitespace
                if isinstance(specialty, str):
                    doc["specialty"] = specialty.strip()
                else:
                    doc["specialty"] = str(specialty).strip() if specialty else ""
                
                # Clean other string fields that might contain newlines
                for field in ['name', 'address', 'description']:
                    if field in doc and doc[field]:
                        if isinstance(doc[field], str):
                            doc[field] = doc[field].replace('\n', ' ').strip()
                
                processed_doctors.append(Doctor.from_dict(doc))
                
            return processed_doctors
            
        except requests.RequestException as e:
            print(f"Error searching for doctors: {e}")
            return []
    
    @staticmethod
    def get_doctor_details(doctor_id: str) -> Optional[Doctor]:
        """Get detailed information about a specific doctor."""
        url = f"{DOCTOLIB_BASE_URL}/api/healthcare_professionals/{doctor_id}.json"
        
        try:
            response = requests.get(url, headers=DEFAULT_HEADERS, timeout=10)
            response.raise_for_status()
            return Doctor.from_dict(response.json())
            
        except requests.RequestException as e:
            print(f"Error fetching doctor details: {e}")
            return None

    @staticmethod
    def get_specialty_info(symptom_query: str):
        url = "https://www.doctolib.de/api/searchbar/autocomplete.json"
        params = {"search": symptom_query}
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, params=params, headers=headers)
        resp.raise_for_status()
        data = resp.json()

        specialities = data.get("specialities", [])
        if not specialities:
            raise ValueError(f"No specialties found for '{symptom_query}'")

        first_specialty = specialities[0]
        return {
            "value": first_specialty["value"],
            "slug": first_specialty["slug"],
            "name": first_specialty["name"]
        }

    @staticmethod
    def resolve_location_name(location_query: str):
        url = "https://www.doctolib.de/patient_app/place_autocomplete.json"
        params = {"query": location_query}
        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()

        data = response.json()
        if not data:
            raise ValueError(f"No results found for location: {location_query}")

        first = data[0]
        return {
            "description": first["description"],
            "place_id": first["place_id"]
        }