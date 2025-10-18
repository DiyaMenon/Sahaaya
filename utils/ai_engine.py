"""
AI Engine for Emergency Detection and Classification
Handles intent recognition, emergency classification, and NLP processing
"""

import json
import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class EmergencyMatch:
    """Data class for emergency detection results"""
    emergency_type: str
    confidence: float
    matched_keywords: List[str]
    emergency_data: Dict

class EmergencyDetector:
    """AI engine for detecting and classifying emergencies from user input"""
    
    def __init__(self, database_path: str = "data/emergency_database.json"):
        """Initialize the emergency detector with knowledge base"""
        self.database_path = database_path
        self.emergency_data = self._load_emergency_database()
        
    def _load_emergency_database(self) -> Dict:
        """Load emergency database from JSON file"""
        try:
            with open(self.database_path, 'r') as f:
                data = json.load(f)
            logger.info(f"Loaded emergency database with {len(data['emergencies'])} emergency types")
            return data
        except FileNotFoundError:
            logger.error(f"Emergency database not found at {self.database_path}")
            return {"emergencies": {}, "emergency_numbers": {}}
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing emergency database: {e}")
            return {"emergencies": {}, "emergency_numbers": {}}
    
    def preprocess_text(self, text: str) -> str:
        """Clean and normalize input text"""
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower().strip()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep important ones
        text = re.sub(r'[^\w\s\-\'\.]', ' ', text)
        
        return text
    
    def extract_keywords(self, text: str) -> List[str]:
        """Extract relevant keywords from input text"""
        processed_text = self.preprocess_text(text)
        words = processed_text.split()
        
        # Remove common stop words that might interfere
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during',
            'before', 'after', 'above', 'below', 'between', 'among', 'within',
            'please', 'help', 'me', 'my', 'i', 'am', 'is', 'are', 'was', 'were',
            'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
            'would', 'could', 'should', 'may', 'might', 'must', 'can', 'cannot'
        }
        
        # Extract meaningful keywords
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        return keywords
    
    def calculate_keyword_match_score(self, input_text: str, emergency_keywords: List[str]) -> Tuple[float, List[str]]:
        """Calculate how well input text matches emergency keywords"""
        processed_input = self.preprocess_text(input_text)
        input_keywords = self.extract_keywords(input_text)
        
        matched_keywords = []
        total_matches = 0
        
        # Check for exact keyword matches
        for emergency_keyword in emergency_keywords:
            emergency_keyword_processed = self.preprocess_text(emergency_keyword)
            
            # Check if the emergency keyword appears in the input text
            if emergency_keyword_processed in processed_input:
                matched_keywords.append(emergency_keyword)
                total_matches += 1
            else:
                # Check for partial matches with individual words
                emergency_words = emergency_keyword_processed.split()
                if len(emergency_words) > 1:
                    # Multi-word keyword - check if all words are present
                    if all(word in input_keywords for word in emergency_words):
                        matched_keywords.append(emergency_keyword)
                        total_matches += 0.8  # Slightly lower score for partial matches
                else:
                    # Single word keyword
                    if emergency_words[0] in input_keywords:
                        matched_keywords.append(emergency_keyword)
                        total_matches += 1
        
        # Calculate confidence score
        if len(emergency_keywords) == 0:
            confidence = 0.0
        else:
            confidence = min(total_matches / len(emergency_keywords), 1.0)
        
        return confidence, matched_keywords
    
    def detect_emergency(self, user_input: str, min_confidence: float = 0.1) -> Optional[EmergencyMatch]:
        """
        Detect emergency type from user input
        
        Args:
            user_input: User's description of the emergency
            min_confidence: Minimum confidence threshold for detection
            
        Returns:
            EmergencyMatch object with detection results or None
        """
        if not user_input or not user_input.strip():
            return None
        
        best_match = None
        best_confidence = 0.0
        
        # Check each emergency type
        for emergency_type, emergency_info in self.emergency_data['emergencies'].items():
            confidence, matched_keywords = self.calculate_keyword_match_score(
                user_input, emergency_info['keywords']
            )
            
            # Update best match if this is better
            if confidence > best_confidence and confidence >= min_confidence:
                best_confidence = confidence
                best_match = EmergencyMatch(
                    emergency_type=emergency_type,
                    confidence=confidence,
                    matched_keywords=matched_keywords,
                    emergency_data=emergency_info
                )
        
        if best_match:
            logger.info(f"Detected emergency: {best_match.emergency_type} "
                       f"(confidence: {best_match.confidence:.2f})")
        
        return best_match
    
    def get_emergency_steps(self, emergency_type: str) -> List[Dict]:
        """Get step-by-step instructions for an emergency"""
        if emergency_type in self.emergency_data['emergencies']:
            return self.emergency_data['emergencies'][emergency_type]['steps']
        return []
    
    def get_all_emergency_types(self) -> Dict[str, Dict]:
        """Get all available emergency types and their basic info"""
        return {
            etype: {
                'name': info['name'],
                'icon': info['icon'],
                'color': info['color'],
                'urgency': info['urgency']
            }
            for etype, info in self.emergency_data['emergencies'].items()
        }
    
    def get_emergency_number(self, country: str = "US") -> str:
        """Get emergency phone number for a specific country"""
        return self.emergency_data.get('emergency_numbers', {}).get(country, "911")
    
    def get_disclaimer(self) -> str:
        """Get the app disclaimer text"""
        return self.emergency_data.get('disclaimer', 
            "Always seek professional medical help for serious emergencies.")

# Emergency Response Helpers
class EmergencyResponseGenerator:
    """Generate structured emergency response with steps and guidance"""
    
    def __init__(self, detector: EmergencyDetector):
        self.detector = detector
    
    def generate_response(self, emergency_match: EmergencyMatch) -> Dict:
        """Generate complete emergency response with all necessary information"""
        if not emergency_match:
            return self._generate_no_match_response()
        
        emergency_info = emergency_match.emergency_data
        steps = emergency_info.get('steps', [])
        
        response = {
            'emergency_detected': True,
            'emergency_type': emergency_match.emergency_type,
            'emergency_name': emergency_info['name'],
            'confidence': emergency_match.confidence,
            'matched_keywords': emergency_match.matched_keywords,
            'urgency': emergency_info['urgency'],
            'color': emergency_info['color'],
            'icon': emergency_info['icon'],
            'total_steps': len(steps),
            'steps': steps,
            'emergency_number': self.detector.get_emergency_number(),
            'initial_message': self._generate_initial_message(emergency_info),
            'disclaimer': self.detector.get_disclaimer()
        }
        
        return response
    
    def _generate_initial_message(self, emergency_info: Dict) -> str:
        """Generate initial response message based on emergency urgency"""
        urgency = emergency_info.get('urgency', 'medium')
        name = emergency_info.get('name', 'Emergency')
        
        if urgency == 'critical':
            return f"🚨 CRITICAL: {name} detected. Follow these steps immediately while calling emergency services!"
        elif urgency == 'high':
            return f"⚠️ HIGH PRIORITY: {name} situation detected. Take immediate action following these steps:"
        else:
            return f"📋 {name} detected. Here are the recommended steps to follow:"
    
    def _generate_no_match_response(self) -> Dict:
        """Generate response when no emergency is detected"""
        return {
            'emergency_detected': False,
            'message': "I couldn't identify a specific emergency from your description. "
                      "Please try to be more specific, or if this is a serious emergency, "
                      "call emergency services immediately.",
            'suggestions': [
                "Try describing symptoms more specifically",
                "Mention what happened (fall, injury, illness)",
                "Use keywords like 'bleeding', 'not breathing', 'chest pain', etc.",
                "If urgent, call emergency services: 911"
            ],
            'emergency_number': self.detector.get_emergency_number(),
            'disclaimer': self.detector.get_disclaimer()
        }

# Utility functions for the AI engine
def create_ai_engine(database_path: str = "data/emergency_database.json") -> Tuple[EmergencyDetector, EmergencyResponseGenerator]:
    """Factory function to create AI engine components"""
    detector = EmergencyDetector(database_path)
    response_generator = EmergencyResponseGenerator(detector)
    return detector, response_generator

def test_emergency_detection():
    """Test function for emergency detection"""
    detector = EmergencyDetector()
    
    test_cases = [
        "Someone collapsed and is not breathing",
        "Person is choking on food can't speak",
        "Heavy bleeding from a deep cut won't stop",
        "Severe burn from hot water",
        "Person fainted and won't wake up",
        "Allergic reaction with difficulty breathing"
    ]
    
    print("Testing Emergency Detection:")
    print("=" * 50)
    
    for test_input in test_cases:
        result = detector.detect_emergency(test_input)
        if result:
            print(f"Input: {test_input}")
            print(f"Emergency: {result.emergency_data['name']}")
            print(f"Confidence: {result.confidence:.2f}")
            print(f"Keywords matched: {result.matched_keywords}")
            print("-" * 30)
        else:
            print(f"No emergency detected for: {test_input}")
            print("-" * 30)

if __name__ == "__main__":
    test_emergency_detection()