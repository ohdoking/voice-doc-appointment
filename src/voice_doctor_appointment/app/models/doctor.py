"""Doctor data model for the Doctor Booking Assistant."""
from dataclasses import dataclass, field
from typing import Dict, Any, Optional

@dataclass
class Doctor:
    """Represents a doctor's information."""
    id: str
    name: str
    location: Dict[str, Any]
    link: str
    specialty: Optional[str] = None
    profile_image_url: Optional[str] = None
    languages: list[str] = field(default_factory=list)
    
    @property
    def booking_url(self) -> str:
        """Get the full booking URL."""
        from ..config import DOCTOLIB_BASE_URL
        return f"{DOCTOLIB_BASE_URL}{self.link}"
    
    @property
    def address(self) -> str:
        """Get the formatted address."""
        return self.location.get('address', 'Address not available')
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the doctor object to a dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'specialty': self.specialty,
            'location': self.location,
            'link': self.link,
            'profile_image_url': self.profile_image_url,
            'languages': self.languages
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Doctor':
        """Create a Doctor instance from a dictionary."""
        return cls(
            id=str(data.get('id', '')),
            name=data.get('name', 'Doctor'),
            specialty=data.get('specialty', ''),
            location=data.get('location', {}),
            link=data.get('link', ''),
            profile_image_url=data.get('profile_image_url'),
            languages=data.get('languages', [])
        )
