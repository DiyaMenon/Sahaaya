"""
Helper Utilities for Sahaaya Emergency Aid Companion
Contains utility functions for maps, offline mode, geolocation, and additional features
"""

import json
import os
import requests
import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import streamlit as st

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LocationHelper:
    """Helper for location and map-related functionality"""
    
    @staticmethod
    def get_current_location() -> Optional[Tuple[float, float]]:
        """
        Get current location using browser geolocation (via JavaScript)
        Returns (latitude, longitude) or None if unavailable
        """
        try:
            # This would typically use JavaScript geolocation API
            # For demonstration, we'll simulate location
            # In a real app, you'd use streamlit-geolocation or similar
            
            # Simulated location (San Francisco for demo)
            return (37.7749, -122.4194)
        except Exception as e:
            logger.error(f"Location detection failed: {e}")
            return None
    
    @staticmethod
    def find_nearby_hospitals(lat: float, lon: float, radius_km: float = 10) -> List[Dict]:
        """
        Find nearby hospitals using location coordinates
        
        Args:
            lat: Latitude
            lon: Longitude  
            radius_km: Search radius in kilometers
            
        Returns:
            List of hospital information dictionaries
        """
        try:
            # In a real implementation, you'd use Google Places API, OpenStreetMap, or similar
            # For demo purposes, returning simulated data
            
            hospitals = [
                {
                    "name": "City General Hospital",
                    "address": "123 Medical Center Drive",
                    "phone": "+1-555-0123",
                    "distance_km": 2.3,
                    "emergency": True,
                    "coordinates": (lat + 0.02, lon - 0.02)
                },
                {
                    "name": "Regional Medical Center", 
                    "address": "456 Healthcare Boulevard",
                    "phone": "+1-555-0456",
                    "distance_km": 4.7,
                    "emergency": True,
                    "coordinates": (lat - 0.03, lon + 0.03)
                },
                {
                    "name": "Community Health Clinic",
                    "address": "789 Wellness Street",
                    "phone": "+1-555-0789", 
                    "distance_km": 6.1,
                    "emergency": False,
                    "coordinates": (lat + 0.04, lon + 0.04)
                }
            ]
            
            # Sort by distance
            hospitals.sort(key=lambda x: x['distance_km'])
            return hospitals
            
        except Exception as e:
            logger.error(f"Hospital search failed: {e}")
            return []
    
    @staticmethod
    def generate_maps_url(lat: float, lon: float, search_query: str = "hospital") -> str:
        """
        Generate Google Maps URL for navigation
        
        Args:
            lat: Latitude
            lon: Longitude
            search_query: What to search for (e.g., "hospital", "pharmacy")
            
        Returns:
            Google Maps URL string
        """
        try:
            # Generate Google Maps search URL
            base_url = "https://www.google.com/maps/search/"
            query = f"{search_query}/@{lat},{lon},15z"
            return base_url + query
        except Exception as e:
            logger.error(f"Maps URL generation failed: {e}")
            return "https://www.google.com/maps"

class OfflineMode:
    """Handle offline functionality and data caching"""
    
    def __init__(self, cache_dir: str = "cache"):
        self.cache_dir = cache_dir
        self._ensure_cache_directory()
    
    def _ensure_cache_directory(self):
        """Create cache directory if it doesn't exist"""
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
    
    def cache_emergency_data(self, data: Dict) -> bool:
        """
        Cache emergency data for offline use
        
        Args:
            data: Emergency database dictionary
            
        Returns:
            bool: True if successful
        """
        try:
            cache_file = os.path.join(self.cache_dir, "emergency_data.json")
            with open(cache_file, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info("Emergency data cached for offline use")
            return True
        except Exception as e:
            logger.error(f"Failed to cache emergency data: {e}")
            return False
    
    def load_cached_emergency_data(self) -> Optional[Dict]:
        """
        Load cached emergency data
        
        Returns:
            Dictionary of cached data or None if unavailable
        """
        try:
            cache_file = os.path.join(self.cache_dir, "emergency_data.json")
            if os.path.exists(cache_file):
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                logger.info("Loaded cached emergency data")
                return data
            return None
        except Exception as e:
            logger.error(f"Failed to load cached data: {e}")
            return None
    
    def is_online(self) -> bool:
        """
        Check if internet connection is available
        
        Returns:
            bool: True if online, False if offline
        """
        try:
            # Try to reach a reliable endpoint
            response = requests.get("https://www.google.com", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def get_offline_status(self) -> Dict:
        """
        Get current offline/online status and capabilities
        
        Returns:
            Dictionary with status information
        """
        online = self.is_online()
        cached_data_available = self.load_cached_emergency_data() is not None
        
        return {
            "online": online,
            "cached_data_available": cached_data_available,
            "offline_capable": cached_data_available,
            "features_available": {
                "emergency_detection": True,  # Always available
                "text_to_speech_offline": True,  # pyttsx3
                "text_to_speech_online": online,  # gTTS
                "voice_recognition": online,  # Usually requires internet
                "maps": online,
                "hospital_search": online
            }
        }

class EmergencyLogger:
    """Log emergency interactions for analytics and improvement"""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = log_dir
        self._ensure_log_directory()
    
    def _ensure_log_directory(self):
        """Create log directory if it doesn't exist"""
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
    
    def log_emergency_event(self, event_data: Dict) -> bool:
        """
        Log an emergency event for analytics
        
        Args:
            event_data: Dictionary containing event information
            
        Returns:
            bool: True if logged successfully
        """
        try:
            # Add timestamp
            event_data['timestamp'] = datetime.now().isoformat()
            
            # Create log file name based on date
            log_file = os.path.join(
                self.log_dir, 
                f"emergency_log_{datetime.now().strftime('%Y_%m_%d')}.jsonl"
            )
            
            # Append to log file (JSONL format)
            with open(log_file, 'a') as f:
                json.dump(event_data, f)
                f.write('\n')
            
            return True
        except Exception as e:
            logger.error(f"Failed to log emergency event: {e}")
            return False
    
    def log_user_interaction(self, interaction_type: str, data: Dict = None) -> bool:
        """
        Log user interaction for UX improvement
        
        Args:
            interaction_type: Type of interaction (e.g., "voice_input", "emergency_detected")
            data: Additional data about the interaction
            
        Returns:
            bool: True if logged successfully
        """
        event_data = {
            "type": "user_interaction",
            "interaction_type": interaction_type,
            "data": data or {}
        }
        
        return self.log_emergency_event(event_data)

class CountryHelper:
    """Helper for country-specific emergency information"""
    
    EMERGENCY_NUMBERS = {
        "US": {"number": "911", "name": "United States"},
        "UK": {"number": "999", "name": "United Kingdom"}, 
        "EU": {"number": "112", "name": "European Union"},
        "IN": {"number": "108", "name": "India"},
        "AU": {"number": "000", "name": "Australia"},
        "CA": {"number": "911", "name": "Canada"},
        "JP": {"number": "119", "name": "Japan"},
        "CN": {"number": "120", "name": "China"},
        "BR": {"number": "192", "name": "Brazil"},
        "DE": {"number": "112", "name": "Germany"},
        "FR": {"number": "15", "name": "France"},
        "IT": {"number": "118", "name": "Italy"},
        "ES": {"number": "112", "name": "Spain"},
        "RU": {"number": "103", "name": "Russia"},
        "MX": {"number": "065", "name": "Mexico"}
    }
    
    @classmethod
    def get_emergency_number(cls, country_code: str = "US") -> str:
        """Get emergency number for a country"""
        return cls.EMERGENCY_NUMBERS.get(country_code, {}).get("number", "911")
    
    @classmethod
    def get_all_emergency_numbers(cls) -> Dict:
        """Get all emergency numbers"""
        return cls.EMERGENCY_NUMBERS
    
    @classmethod
    def detect_country_from_ip(cls) -> str:
        """
        Detect country from IP address (simplified)
        In a real app, you'd use a geolocation service
        """
        try:
            # Simplified IP-based country detection
            # In reality, you'd use a service like ipinfo.io or similar
            return "US"  # Default fallback
        except Exception:
            return "US"

class AccessibilityHelper:
    """Helper for accessibility features"""
    
    @staticmethod
    def generate_high_contrast_colors() -> Dict:
        """Generate high contrast color scheme for accessibility"""
        return {
            "background": "#000000",
            "text": "#FFFFFF", 
            "primary": "#FFD700",
            "secondary": "#FF6B6B",
            "success": "#4ECDC4",
            "warning": "#FFE66D",
            "danger": "#FF6B6B",
            "info": "#4ECDC4"
        }
    
    @staticmethod
    def generate_large_text_css() -> str:
        """Generate CSS for large text accessibility"""
        return """
        <style>
        .accessibility-large-text {
            font-size: 1.5rem !important;
            line-height: 1.8 !important;
        }
        .accessibility-large-text h1 { font-size: 3rem !important; }
        .accessibility-large-text h2 { font-size: 2.5rem !important; }
        .accessibility-large-text h3 { font-size: 2rem !important; }
        .accessibility-large-text p { font-size: 1.5rem !important; }
        .accessibility-large-text button { font-size: 1.3rem !important; padding: 1rem 2rem !important; }
        </style>
        """
    
    @staticmethod
    def text_to_speech_instructions(text: str) -> str:
        """
        Optimize text for text-to-speech by adding pauses and emphasis
        
        Args:
            text: Original text
            
        Returns:
            str: TTS-optimized text
        """
        # Add strategic pauses
        tts_text = text.replace(".", ". ... ")  # Pause after sentences
        tts_text = tts_text.replace(":", ": ... ")  # Pause after colons
        tts_text = tts_text.replace(";", "; ... ")  # Pause after semicolons
        
        # Emphasize important words
        important_words = ["EMERGENCY", "CRITICAL", "WARNING", "DANGER", "CALL", "IMMEDIATELY"]
        for word in important_words:
            tts_text = tts_text.replace(word, f"... {word.upper()} ...")
        
        return tts_text

class StreamlitHelpers:
    """Helper functions for Streamlit-specific functionality"""
    
    @staticmethod
    def create_download_button(data: str, filename: str, mime_type: str = "text/plain") -> bool:
        """
        Create a download button for data
        
        Args:
            data: Data to download
            filename: Filename for download
            mime_type: MIME type of the data
            
        Returns:
            bool: True if download was initiated
        """
        return st.download_button(
            label=f"📥 Download {filename}",
            data=data,
            file_name=filename,
            mime=mime_type,
            help=f"Download {filename} to your device"
        )
    
    @staticmethod
    def create_share_url(emergency_type: str, steps_completed: int) -> str:
        """
        Create a shareable URL for the current emergency response
        
        Args:
            emergency_type: Type of emergency
            steps_completed: Number of steps completed
            
        Returns:
            str: Shareable URL (simplified for demo)
        """
        base_url = "https://sahaaya-app.streamlit.app"
        params = f"?emergency={emergency_type}&step={steps_completed}"
        return base_url + params
    
    @staticmethod
    def display_emergency_contact_card(contact_info: Dict):
        """
        Display emergency contact information in a card format
        
        Args:
            contact_info: Dictionary with contact information
        """
        st.markdown(f"""
        <div style="
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 10px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            padding: 15px;
            margin: 10px 0;
        ">
            <h4 style="margin: 0 0 10px 0; color: white;">
                🏥 {contact_info.get('name', 'Emergency Contact')}
            </h4>
            <p style="margin: 5px 0; color: rgba(255,255,255,0.9);">
                📍 {contact_info.get('address', 'Address not available')}
            </p>
            <p style="margin: 5px 0; color: rgba(255,255,255,0.9);">
                📞 {contact_info.get('phone', 'Phone not available')}
            </p>
            <p style="margin: 5px 0; color: rgba(255,255,255,0.7); font-size: 0.9rem;">
                📏 Distance: {contact_info.get('distance_km', 'Unknown')} km
            </p>
        </div>
        """, unsafe_allow_html=True)

# Factory functions for creating helper instances
def create_location_helper() -> LocationHelper:
    """Create LocationHelper instance"""
    return LocationHelper()

def create_offline_mode(cache_dir: str = "cache") -> OfflineMode:
    """Create OfflineMode instance"""
    return OfflineMode(cache_dir)

def create_emergency_logger(log_dir: str = "logs") -> EmergencyLogger:
    """Create EmergencyLogger instance"""
    return EmergencyLogger(log_dir)

# Utility functions
def format_phone_number(phone: str, country_code: str = "US") -> str:
    """
    Format phone number for display
    
    Args:
        phone: Phone number string
        country_code: Country code for formatting
        
    Returns:
        str: Formatted phone number
    """
    # Simplified phone formatting
    if country_code == "US" and len(phone) == 10:
        return f"({phone[:3]}) {phone[3:6]}-{phone[6:]}"
    return phone

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance between two coordinates using Haversine formula
    
    Args:
        lat1, lon1: First coordinate
        lat2, lon2: Second coordinate
        
    Returns:
        float: Distance in kilometers
    """
    import math
    
    # Convert to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Radius of Earth in kilometers
    r = 6371
    
    return c * r

if __name__ == "__main__":
    # Test helper functions
    print("Testing Sahaaya Helper Functions:")
    print("=" * 40)
    
    # Test location helper
    location_helper = LocationHelper()
    current_location = location_helper.get_current_location()
    if current_location:
        print(f"Current location: {current_location}")
        hospitals = location_helper.find_nearby_hospitals(*current_location)
        print(f"Found {len(hospitals)} hospitals nearby")
    
    # Test offline mode
    offline_mode = OfflineMode()
    status = offline_mode.get_offline_status()
    print(f"Offline status: {status}")
    
    print("Helper functions test completed.")