#!/usr/bin/env python3
"""
🎤 Voice Testing Script for Sahaaya
Test different voices to find the most calming one for emergency guidance
"""

import sys
import time
from utils.speech_utils import SpeechProcessor

def print_banner():
    """Print the voice testing banner"""
    banner = """
    ╔══════════════════════════════════════════════════════╗
    ║                                                      ║
    ║        🎤 SAHAAYA VOICE TESTING UTILITY             ║
    ║                                                      ║
    ║      Find the Perfect Voice for Emergency Aid       ║
    ║                                                      ║
    ╚══════════════════════════════════════════════════════╝
    """
    print(banner)

def test_all_voices():
    """Test all available voices"""
    print("🔍 Initializing speech processor...")
    processor = SpeechProcessor()
    
    if not processor.tts_engine:
        print("❌ Text-to-speech engine not available!")
        print("Make sure you have pyttsx3 installed: pip install pyttsx3")
        return
    
    print("✅ Speech processor initialized")
    print("\n📋 Getting available voices...")
    
    voices = processor.get_available_voices()
    if not voices:
        print("❌ No voices found!")
        return
    
    print(f"✅ Found {len(voices)} voices\n")
    
    # Test text for emergency guidance
    test_texts = [
        "Hello, I'm Sahaaya, your emergency aid companion.",
        "Please stay calm. I'm here to guide you through the emergency steps.",
        "Step one: Check if the person is responsive. Gently shake their shoulders.",
        "Remember to breathe deeply and follow each instruction carefully."
    ]
    
    print("🎧 Voice Testing Menu:")
    print("=" * 50)
    
    while True:
        print("\nAvailable options:")
        print("1. List all voices")
        print("2. Test a specific voice")
        print("3. Test all voices (quick)")
        print("4. Find recommended calm voices")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == "1":
            list_voices(voices)
        elif choice == "2":
            test_specific_voice(processor, voices, test_texts)
        elif choice == "3":
            test_all_voices_quick(processor, voices, test_texts[0])
        elif choice == "4":
            find_calm_voices(processor, voices, test_texts[1])
        elif choice == "5":
            print("\n👋 Happy voice testing! Remember to update your app with your preferred voice.")
            break
        else:
            print("❌ Invalid choice. Please enter 1-5.")

def list_voices(voices):
    """List all available voices with details"""
    print("\n📜 Available Voices:")
    print("-" * 70)
    
    for i, voice in enumerate(voices, 1):
        gender = voice.get('gender', 'Unknown')
        languages = voice.get('languages', ['Unknown'])
        lang_str = languages[0] if isinstance(languages, list) else str(languages)
        
        print(f"{i:2d}. {voice['name']:<25} | {gender:<8} | {lang_str}")
    
    print("-" * 70)

def test_specific_voice(processor, voices, test_texts):
    """Test a specific voice selected by user"""
    list_voices(voices)
    
    try:
        choice = int(input(f"\nEnter voice number (1-{len(voices)}): "))
        if 1 <= choice <= len(voices):
            selected_voice = voices[choice - 1]
            
            print(f"\n🎧 Testing voice: {selected_voice['name']}")
            print("   (Listen and rate how calming it sounds)")
            
            # Set the voice
            if processor.set_voice_by_name(selected_voice['name']):
                # Test with multiple sentences
                for i, text in enumerate(test_texts, 1):
                    print(f"\n   Testing phrase {i}...")
                    processor.test_voice(text)
                    
                    if i < len(test_texts):
                        input("   Press Enter for next phrase...")
                
                print(f"\n✅ Voice test complete for {selected_voice['name']}")
                
                # Ask for rating
                rating = input("Rate this voice (1-5, where 5 is most calming): ").strip()
                if rating in ['1', '2', '3', '4', '5']:
                    print(f"📝 You rated {selected_voice['name']}: {rating}/5")
            else:
                print("❌ Failed to set voice")
        else:
            print("❌ Invalid voice number")
    except ValueError:
        print("❌ Please enter a valid number")

def test_all_voices_quick(processor, voices, test_text):
    """Quickly test all voices with the same text"""
    print(f"\n🔄 Testing all {len(voices)} voices with quick sample...")
    print("(Each voice will say: 'Hello, I'm your emergency aid companion')")
    print("\nPress Ctrl+C to stop at any time\n")
    
    try:
        for i, voice in enumerate(voices, 1):
            print(f"🎧 Voice {i}/{len(voices)}: {voice['name']}")
            
            if processor.set_voice_by_name(voice['name']):
                processor.test_voice(f"Voice {i}. {test_text}")
                time.sleep(1)  # Brief pause between voices
            
            # Pause every 5 voices
            if i % 5 == 0 and i < len(voices):
                input("\n   [Tested 5 voices] Press Enter to continue...")
    
    except KeyboardInterrupt:
        print("\n⏸️ Voice testing stopped by user")

def find_calm_voices(processor, voices, test_text):
    """Find and test voices that are likely to be calm"""
    print("\n🧘 Finding and testing calm voices...")
    
    # Preferred calm voice names (common on macOS and Windows)
    calm_voice_names = [
        'samantha', 'victoria', 'allison', 'susan', 'karen', 'moira',
        'fiona', 'tessa', 'veena', 'ava', 'serena',
        'zira', 'hazel', 'catherine', 'helena', 'julie'
    ]
    
    found_calm_voices = []
    
    for voice in voices:
        voice_name_lower = voice['name'].lower()
        for calm_name in calm_voice_names:
            if calm_name in voice_name_lower:
                found_calm_voices.append(voice)
                break
    
    if not found_calm_voices:
        print("❌ No specifically calm voices found by name")
        print("🔍 Looking for female voices instead...")
        
        # Look for female voices as backup
        for voice in voices:
            gender = voice.get('gender', '').lower()
            if 'female' in gender or 'woman' in gender:
                found_calm_voices.append(voice)
    
    if found_calm_voices:
        print(f"✅ Found {len(found_calm_voices)} potentially calm voices:")
        
        for i, voice in enumerate(found_calm_voices, 1):
            print(f"\n🎧 Testing calm voice {i}: {voice['name']}")
            
            if processor.set_voice_by_name(voice['name']):
                processor.test_voice(test_text)
                
                rating = input("Rate calmness (1-5, or 's' to skip): ").strip().lower()
                if rating == 's':
                    continue
                elif rating in ['4', '5']:
                    print(f"⭐ {voice['name']} rated as calm! Remember this one.")
            
            if i < len(found_calm_voices):
                input("Press Enter for next voice...")
    else:
        print("❌ No calm voices found automatically")
        print("💡 Try testing individual voices manually")

def main():
    """Main function"""
    print_banner()
    
    print("This script will help you find the most calming voice for Sahaaya.")
    print("You'll be able to listen to different voices and choose your favorite.\n")
    
    try:
        test_all_voices()
    except KeyboardInterrupt:
        print("\n\n👋 Voice testing cancelled.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Make sure pyttsx3 is installed: pip install pyttsx3")

if __name__ == "__main__":
    main()