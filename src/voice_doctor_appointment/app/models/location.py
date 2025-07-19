"""Location data model for the Doctor Booking Assistant."""
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Union
from dataclasses_json import dataclass_json

@dataclass_json
@dataclass
class Location:
    """Represents a location with its details for the Doctolib API."""
    id: int
    placeId: str
    name: str
    nameWithPronoun: str
    slug: str
    country: str = "de"
    type: str = "route"
    zipcodes: List[str] = field(default_factory=list)
    locality: Optional[str] = None
    streetName: Optional[str] = None
    streetNumber: Optional[str] = None
    
    # Viewport coordinates (default to Berlin center if not provided)
    viewport: Dict[str, Dict[str, float]] = field(
        default_factory=lambda: {
            "northeast": {"lat": 52.5660121802915, "lng": 13.3949812802915},
            "southwest": {"lat": 52.5633142197085, "lng": 13.3922833197085},
        }
    )
    
    # GPS point (default to Berlin center if not provided)
    gpsPoint: Dict[str, float] = field(
        default_factory=lambda: {"lat": 52.5646632, "lng": 13.3936323}
    )
    
    @property
    def place_id(self) -> str:
        """Alias for placeId to maintain backward compatibility."""
        return self.placeId
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the location to a dictionary with proper field names."""
        return {
            "id": self.id,
            "placeId": self.placeId,
            "name": self.name,
            "nameWithPronoun": self.nameWithPronoun,
            "slug": self.slug,
            "country": self.country,
            "viewport": self.viewport,
            "type": self.type,
            "zipcodes": self.zipcodes,
            "gpsPoint": self.gpsPoint,
            "locality": self.locality,
            "streetName": self.streetName,
            "streetNumber": self.streetNumber
        }
    
    @classmethod
    def create(
        cls,
        place_id: str,
        name: str,
        slug: Optional[str] = None,
        locality: Optional[str] = None,
        **kwargs
    ) -> 'Location':
        """Create a Location instance with sensible defaults.
        
        Args:
            place_id: The place ID from the location service
            name: The location name (e.g., city or street name)
            slug: URL-friendly slug for the location (defaults to lowercase name)
            locality: The city or locality name
            **kwargs: Additional fields to override defaults
            
        Returns:
            A configured Location instance
        """
        name = name.strip()
        if not slug:
            slug = name.lower().replace(" ", "-")
        
        return cls(
            id=kwargs.get("id", 1419927),  # Default ID, should be dynamic in production
            placeId=place_id,
            name=name,
            nameWithPronoun=f"in {name}",
            slug=slug,
            locality=locality or name,
            viewport=kwargs.get("viewport", {
                "northeast": {"lat": 52.5660121802915, "lng": 13.3949812802915},
                "southwest": {"lat": 52.5633142197085, "lng": 13.3922833197085},
            }),
            gpsPoint=kwargs.get("gpsPoint", {"lat": 52.5646632, "lng": 13.3936323}),
            **{k: v for k, v in kwargs.items() if k in cls.__annotations__}
        )
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Location':
        """Create a Location instance from a dictionary."""
        return cls(
            id=data.get("id", 1419927),
            placeId=data.get("placeId", data.get("place_id", "")),
            name=data.get("name", ""),
            nameWithPronoun=data.get("nameWithPronoun", ""),
            slug=data.get("slug", ""),
            country=data.get("country", "de"),
            viewport=data.get("viewport", {
                "northeast": {"lat": 52.5660121802915, "lng": 13.3949812802915},
                "southwest": {"lat": 52.5633142197085, "lng": 13.3922833197085},
            }),
            type=data.get("type", "route"),
            zipcodes=data.get("zipcodes", []),
            gpsPoint=data.get("gpsPoint", {"lat": 52.5646632, "lng": 13.3936323}),
            locality=data.get("locality"),
            streetName=data.get("streetName"),
            streetNumber=data.get("streetNumber")
        )
