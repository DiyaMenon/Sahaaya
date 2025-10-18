"""
Speech Processing Utilities
Handles speech-to-text, text-to-speech, and audio processing
"""

import os
import tempfile
import logging
from typing import Optional, Dict, Any
import streamlit as st

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SpeechProcessor:
    """Handles all speech processing functionality"""
    
    def __init__(self):
        """Initialize speech processor with available backends"""
        self.tts_engine = None
        self.stt_recognizer = None
        self.microphone = None
        self._initialize_engines()
    
    def _initialize_engines(self):
        """Initialize speech recognition and text-to-speech engines"""
        try:
            # Initialize text-to-speech (pyttsx3 for offline)
            import pyttsx3
            self.tts_engine = pyttsx3.init()
            self._configure_tts_engine()
            logger.info("Initialized pyttsx3 TTS engine")
        except ImportError:
            logger.warning("pyttsx3 not available, TTS will use gTTS")
        except Exception as e:
            logger.warning(f"Failed to initialize pyttsx3: {e}")
        
        try:
            # Initialize speech recognition
            import speech_recognition as sr
            self.stt_recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
            
            # Adjust for ambient noise
            with self.microphone as source:
                self.stt_recognizer.adjust_for_ambient_noise(source, duration=1)
            
            logger.info("Initialized speech recognition")
        except ImportError:
            logger.warning("speech_recognition not available")
        except OSError as e:
            logger.warning(f"Microphone not available: {e}")
        except Exception as e:
            logger.warning(f"Failed to initialize speech recognition: {e}")
    
    def _configure_tts_engine(self):
        """Configure TTS engine settings for calm, soothing voice"""
        if not self.tts_engine:
            return
        
        try:
            # Set slower speech rate for calming effect (words per minute)
            self.tts_engine.setProperty('rate', 130)  # Slower, more deliberate
            
            # Set moderate volume (0.0 to 1.0)
            self.tts_engine.setProperty('volume', 0.8)  # Slightly softer
            
            # Try to set the most calming voice available
            voices = self.tts_engine.getProperty('voices')
            if voices:
                selected_voice = self._select_best_voice(voices)
                if selected_voice:
                    self.tts_engine.setProperty('voice', selected_voice.id)
                    logger.info(f"Selected voice: {selected_voice.name}")
        
        except Exception as e:
            logger.warning(f"Failed to configure TTS engine: {e}")
    
    def _select_best_voice(self, voices):
        """Select the most calming voice from available options"""
        # Priority order for voice selection (most calming first)
        preferred_voices = [
            # macOS voices (common calm voices)
            'Samantha', 'Victoria', 'Allison', 'Susan', 'Karen', 'Moira',
            'Fiona', 'Tessa', 'Veena', 'Ava', 'Serena',
            # Windows voices
            'Zira', 'Hazel', 'Catherine', 'Helena', 'Julie',
            # Generic patterns for calm voices
            'female', 'woman', 'calm', 'soft', 'gentle'
        ]
        
        # First, try to find voices by exact name match
        for preferred in preferred_voices[:11]:  # First 11 are exact names
            for voice in voices:
                if preferred.lower() in voice.name.lower():
                    return voice
        
        # Then try pattern matching for female/calm voices
        for preferred in preferred_voices[11:]:  # Remaining are patterns
            for voice in voices:
                if preferred in voice.name.lower():
                    return voice
        
        # If no preferred voice found, try to avoid obviously robotic ones
        avoided_voices = ['robot', 'alex', 'fred', 'junior', 'ralph', 'bad']
        for voice in voices:
            if not any(avoid in voice.name.lower() for avoid in avoided_voices):
                return voice
        
        # Last resort: use first available voice
        return voices[0] if voices else None
    
    def get_available_voices(self):
        """Get list of available voices with their details"""
        if not self.tts_engine:
            return []
        
        try:
            voices = self.tts_engine.getProperty('voices')
            voice_list = []
            
            for voice in voices:
                # Extract useful information about each voice
                voice_info = {
                    'id': voice.id,
                    'name': voice.name,
                    'age': getattr(voice, 'age', 'Unknown'),
                    'gender': getattr(voice, 'gender', 'Unknown'),
                    'languages': getattr(voice, 'languages', ['Unknown'])
                }
                voice_list.append(voice_info)
            
            return voice_list
        except Exception as e:
            logger.error(f"Failed to get available voices: {e}")
            return []
    
    def set_voice_by_name(self, voice_name: str) -> bool:
        """Set voice by name or partial name match"""
        if not self.tts_engine:
            return False
        
        try:
            voices = self.tts_engine.getProperty('voices')
            
            # Find voice by name (case-insensitive partial match)
            for voice in voices:
                if voice_name.lower() in voice.name.lower():
                    self.tts_engine.setProperty('voice', voice.id)
                    logger.info(f"Voice changed to: {voice.name}")
                    return True
            
            logger.warning(f"Voice '{voice_name}' not found")
            return False
        except Exception as e:
            logger.error(f"Failed to set voice: {e}")
            return False
    
    def test_voice(self, test_text: str = "Hello, this is your emergency guidance assistant. How does my voice sound?") -> bool:
        """Test the current voice with sample text"""
        return self.text_to_speech_offline(test_text)
    
    def text_to_speech_offline(self, text: str) -> bool:
        """
        Convert text to speech using offline pyttsx3
        
        Args:
            text: Text to speak
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.tts_engine or not text.strip():
            return False
        
        try:
            # Clean text for speech
            speech_text = self._prepare_text_for_speech(text)
            
            self.tts_engine.say(speech_text)
            self.tts_engine.runAndWait()
            return True
        
        except Exception as e:
            logger.error(f"Offline TTS failed: {e}")
            return False
    
    def text_to_speech_online(self, text: str) -> Optional[bytes]:
        """
        Convert text to speech using Google TTS (requires internet)
        
        Args:
            text: Text to speak
            
        Returns:
            bytes: Audio data or None if failed
        """
        try:
            from gtts import gTTS
            import io
            
            if not text.strip():
                return None
            
            speech_text = self._prepare_text_for_speech(text)
            
            # Create gTTS object
            tts = gTTS(text=speech_text, lang='en', slow=False)
            
            # Save to bytes buffer
            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            
            return audio_buffer.getvalue()
        
        except ImportError:
            logger.error("gTTS not available for online TTS")
            return None
        except Exception as e:
            logger.error(f"Online TTS failed: {e}")
            return None
    
    def _prepare_text_for_speech(self, text: str) -> str:
        """
        Prepare text for speech synthesis by cleaning and formatting for calm delivery
        
        Args:
            text: Raw text
            
        Returns:
            str: Cleaned text optimized for calming speech
        """
        if not text:
            return ""
        
        # Remove markdown and HTML
        import re
        
        # Remove markdown links
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
        
        # Remove markdown formatting
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # Bold
        text = re.sub(r'\*([^*]+)\*', r'\1', text)      # Italic
        text = re.sub(r'`([^`]+)`', r'\1', text)        # Code
        
        # Remove or soften aggressive punctuation
        text = re.sub(r'[!]{2,}', '.', text)  # Multiple exclamations to period
        text = re.sub(r'[?]{2,}', '?', text)
        text = text.replace('!', '.')  # Convert exclamations to periods for calmer tone
        
        # Make emergency language less scary
        calming_replacements = {
            'EMERGENCY': 'emergency',
            'CRITICAL': 'important',
            'DANGER': 'caution',
            'URGENT': 'important',
            'IMMEDIATELY': 'right away',
            'PANIC': 'stay calm',
            'DEATH': 'serious condition',
            'DIE': 'become seriously ill',
            'BLOOD': 'bleeding',
        }
        
        for scary, calm in calming_replacements.items():
            text = text.replace(scary, calm)
        
        # Add gentle pauses for better speech flow
        text = text.replace('.', '... ')
        text = text.replace(',', ', ')
        text = text.replace(';', '... ')
        text = text.replace(':', '... ')
        
        # Add calming prefixes for instructions
        if 'step' in text.lower() and any(word in text.lower() for word in ['check', 'call', 'place', 'apply']):
            text = "Please " + text.lower() if not text.startswith(('please', 'Please')) else text
        
        # Clean up extra spaces
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Ensure it doesn't end abruptly
        if text and not text.endswith(('.', '...')):
            text += '.'
        
        return text
    
    def speech_to_text(self, audio_data: Any = None, timeout: float = 5.0) -> Optional[str]:
        """
        Convert speech to text using microphone input
        
        Args:
            audio_data: Optional pre-recorded audio data
            timeout: Recording timeout in seconds
            
        Returns:
            str: Transcribed text or None if failed
        """
        if not self.stt_recognizer or not self.microphone:
            logger.error("Speech recognition not initialized")
            return None
        
        try:
            if audio_data is None:
                # Record from microphone
                with self.microphone as source:
                    logger.info("Listening for speech...")
                    audio_data = self.stt_recognizer.listen(source, timeout=timeout, phrase_time_limit=10)
            
            # Try Google Speech Recognition (requires internet)
            try:
                text = self.stt_recognizer.recognize_google(audio_data)
                logger.info(f"Speech recognized: {text}")
                return text
            except Exception as e:
                logger.warning(f"Google STT failed: {e}")
            
            # Fallback to offline recognition if available
            try:
                text = self.stt_recognizer.recognize_sphinx(audio_data)
                logger.info(f"Offline speech recognized: {text}")
                return text
            except Exception as e:
                logger.warning(f"Offline STT failed: {e}")
            
            return None
        
        except Exception as e:
            logger.error(f"Speech to text failed: {e}")
            return None

class StreamlitSpeechInterface:
    """Streamlit-specific speech interface components"""
    
    def __init__(self):
        self.speech_processor = SpeechProcessor()
    
    def create_voice_input_interface(self) -> Optional[str]:
        """
        Create voice input interface for Streamlit
        
        Returns:
            str: Transcribed text or None
        """
        st.subheader("🎤 Voice Input")
        
        col1, col2 = st.columns([1, 3])
        
        with col1:
            if st.button("🎤 Start Recording", key="voice_record", help="Click to start recording"):
                return self._handle_voice_recording()
        
        with col2:
            st.info("Click the microphone button and speak clearly about the emergency")
        
        return None
    
    def _handle_voice_recording(self) -> Optional[str]:
        """Handle voice recording process with user feedback"""
        try:
            # Show recording status
            with st.spinner("🎤 Recording... Speak now!"):
                import time
                time.sleep(0.5)  # Brief pause for user to start speaking
                
                # Record speech
                transcribed_text = self.speech_processor.speech_to_text(timeout=10.0)
                
            if transcribed_text:
                st.success(f"✅ Heard: \"{transcribed_text}\"")
                return transcribed_text
            else:
                st.error("❌ Could not understand speech. Please try again or type your message.")
                return None
        
        except Exception as e:
            st.error(f"❌ Recording failed: {str(e)}")
            logger.error(f"Voice recording failed: {e}")
            return None
    
    def create_tts_interface(self, text: str) -> bool:
        """
        Create text-to-speech interface for emergency instructions
        
        Args:
            text: Text to speak
            
        Returns:
            bool: True if TTS was triggered
        """
        if not text.strip():
            return False
        
        col1, col2 = st.columns([1, 4])
        
        with col1:
            if st.button("🔊 Listen", key=f"tts_{hash(text)}", help="Click to hear this instruction"):
                return self._handle_text_to_speech(text)
        
        with col2:
            st.caption("Click to hear this step read aloud")
        
        return False
    
    def _handle_text_to_speech(self, text: str) -> bool:
        """Handle text-to-speech with audio playback in browser"""
        try:
            if not text.strip():
                st.warning("⚠️ Nothing to read aloud.")
                return False

            with st.spinner("🔊 Generating speech..."):
                # Try online TTS first (so sound plays in browser)
                audio_data = self.speech_processor.text_to_speech_online(text)

                if audio_data:
                    st.audio(audio_data, format='audio/mp3')
                    st.success("✅ Audio ready — click play above to hear the step.")
                    return True

                # If online fails, try offline pyttsx3
                st.info("📦 Using offline speech engine (sound plays on host system)")
                if self.speech_processor.text_to_speech_offline(text):
                    st.success("✅ Offline TTS executed (sound plays locally)")
                    return True
                else:
                    st.warning("⚠️ Unable to play audio at this time.")
                    return False

        except Exception as e:
            st.error(f"❌ Audio failed: {str(e)}")
            logger.error(f"TTS failed: {e}")
            return False

    
    def create_auto_speech_option(self) -> bool:
        """Create option for automatic speech of all steps"""
        return st.checkbox(
            "🔊 Auto-read all steps aloud",
            value=False,
            help="Automatically read each step aloud when displayed"
        )

# Utility functions
def test_speech_functionality():
    """Test speech functionality"""
    processor = SpeechProcessor()
    
    # Test TTS
    test_text = "This is a test of the text to speech functionality."
    print("Testing Text-to-Speech...")
    
    if processor.text_to_speech_offline(test_text):
        print("✅ Offline TTS working")
    else:
        print("❌ Offline TTS not working")
    
    # Test online TTS
    audio_data = processor.text_to_speech_online(test_text)
    if audio_data:
        print("✅ Online TTS working")
        print(f"Audio data size: {len(audio_data)} bytes")
    else:
        print("❌ Online TTS not working")

def create_speech_interface() -> StreamlitSpeechInterface:
    """Factory function to create speech interface"""
    return StreamlitSpeechInterface()

if __name__ == "__main__":
    test_speech_functionality()