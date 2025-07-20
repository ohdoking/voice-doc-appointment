"""Configuration settings for the MediMatch Voice."""
from pathlib import Path

# Application settings
APP_NAME = "MediMatch Voice"
APP_ICON = "🏥"
DEFAULT_RECORDING_DURATION = 5

# Paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"

# UI Settings
PAGE_LAYOUT = "wide"
INITIAL_SIDEBAR_STATE = "expanded"

# API Settings
DOCTOLIB_BASE_URL = "https://www.doctolib.de"
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# Default values
DEFAULT_DOCTOR_IMAGE = "https://via.placeholder.com/150"
