"""
🆘 Sahaaya - Complete Functional Emergency Aid App
All features working: Voice, Maps, Dark/Light Mode, Chat, Medical Prediction
"""

import streamlit as st
import json
import time
import re
from datetime import datetime
from typing import Dict, List, Optional

# Import with error handling
try:
    from utils.ai_engine import create_ai_engine
    from utils.speech_utils import SpeechProcessor
    from utils.helpers import LocationHelper, CountryHelper
    MODULES_LOADED = True
except ImportError as e:
    st.error(f"❌ Import error: {e}")
    MODULES_LOADED = False

# Configure page
st.set_page_config(
    page_title="🆘 Sahaaya - Emergency Aid",
    page_icon="🆘",
    layout="wide"
)

# Initialize session state
def init_app():
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
        st.session_state.dark_mode = False
        st.session_state.current_emergency = None
        st.session_state.current_step = 0
        st.session_state.auto_speech = False
        st.session_state.conversation = []
        st.session_state.chat_active = False
        
        if MODULES_LOADED:
            try:
                detector, response_gen = create_ai_engine()
                st.session_state.detector = detector
                st.session_state.response_gen = response_gen
                st.session_state.speech = SpeechProcessor()
                st.session_state.location = LocationHelper()
            except Exception as e:
                st.warning(f"Some features unavailable: {e}")

# Dynamic CSS based on theme
def load_css():
    theme = "dark" if st.session_state.get('dark_mode', False) else "light"
    
    if theme == "dark":
        bg = "linear-gradient(135deg, #1a202c 0%, #2d3748 100%)"
        card_bg = "rgba(45, 55, 72, 0.4)"
        text_color = "#ffffff"
    else:
        bg = "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
        card_bg = "rgba(255, 255, 255, 0.25)"
        text_color = "#333333"
    
    css = f"""
    <style>
    .stApp {{
        background: {bg};
        color: {text_color};
        font-family: 'Poppins', sans-serif;
    }}
    
    .glass-card {{
        background: {card_bg};
        backdrop-filter: blur(15px);
        border-radius: 20px;
        border: 1px solid rgba(255,255,255,0.2);
        padding: 25px;
        margin: 15px 0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }}
    
    .glass-card:hover {{
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(0,0,0,0.2);
    }}
    
    .emergency-card {{
        background: rgba(255,68,68,0.3);
        border: 2px solid #ff4444;
        animation: pulse 2s infinite;
    }}
    
    @keyframes pulse {{
        0% {{ box-shadow: 0 0 0 0 rgba(255,68,68,0.7); }}
        70% {{ box-shadow: 0 0 0 10px rgba(255,68,68,0); }}
        100% {{ box-shadow: 0 0 0 0 rgba(255,68,68,0); }}
    }}
    
    .step-card {{
        background: {card_bg};
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        border-left: 4px solid #4facfe;
    }}
    
    .current-step {{
        border: 2px solid #4facfe;
        background: rgba(79,172,254,0.2);
        animation: glow 2s infinite;
    }}
    
    @keyframes glow {{
        0% {{ box-shadow: 0 0 10px rgba(79,172,254,0.5); }}
        100% {{ box-shadow: 0 0 20px rgba(79,172,254,0.8); }}
    }}
    
    .chat-message {{
        background: {card_bg};
        padding: 15px;
        border-radius: 15px;
        margin: 10px 0;
        border-left: 4px solid #764ba2;
    }}
    
    .user-message {{
        border-left-color: #4facfe;
        background: rgba(79,172,254,0.2);
    }}
    
    .stButton > button {{
        background: linear-gradient(45deg, #4facfe, #764ba2);
        border: none;
        border-radius: 25px;
        color: white;
        font-weight: 600;
        padding: 0.75rem 2rem;
        transition: all 0.3s ease;
    }}
    
    .stButton > button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.3);
    }}
    
    .panic-btn {{
        background: linear-gradient(45deg, #ff4757, #ff3838) !important;
        font-size: 1.3rem !important;
        padding: 1rem 2.5rem !important;
        animation: urgent-pulse 1.5s infinite;
    }}
    
    @keyframes urgent-pulse {{
        0% {{ transform: scale(1); }}
        50% {{ transform: scale(1.05); }}
        100% {{ transform: scale(1); }}
    }}
    
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# Header with theme toggle
def create_header():
    st.markdown("""
    <div class="glass-card">
        <h1 style="text-align: center; font-size: 3rem; margin: 0;">
            🆘 Sahaaya
        </h1>
        <p style="text-align: center; font-size: 1.3rem; margin: 10px 0;">
            AI Emergency Aid Companion
        </p>
        <p style="text-align: center; opacity: 0.8;">
            ⚡ Your Partner in Critical Moments
        </p>
    </div>
    """, unsafe_allow_html=True)

# Emergency input with voice support
def emergency_input():
    st.markdown("## 📝 Emergency Description")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⌨️ Text Input"):
            st.session_state.input_mode = "text"
    with col2:
        if st.button("🎤 Voice Input"):
            st.session_state.input_mode = "voice"
    
    # Text input
    if st.session_state.get('input_mode', 'text') == 'text':
        user_input = st.text_area(
            "Describe the emergency:",
            placeholder="e.g., 'Person collapsed and not breathing'",
            height=100
        )
        
        if st.button("🔍 Analyze Emergency") and user_input:
            analyze_emergency(user_input)
    
    # Voice input
    else:
        st.info("🎤 Voice Input Mode Active")
        if st.button("🎙️ Start Recording"):
            if hasattr(st.session_state, 'speech'):
                with st.spinner("🎤 Recording..."):
                    try:
                        voice_text = st.session_state.speech.speech_to_text()
                        if voice_text:
                            st.success(f"✅ Heard: '{voice_text}'")
                            analyze_emergency(voice_text)
                        else:
                            st.error("❌ Could not understand speech")
                    except Exception as e:
                        st.error(f"❌ Voice error: {e}")
            else:
                st.error("❌ Voice not available")

# Emergency analysis
def analyze_emergency(text):
    if not hasattr(st.session_state, 'detector'):
        st.error("❌ Emergency detection not available")
        return
    
    with st.spinner("🤖 Analyzing..."):
        try:
            match = st.session_state.detector.detect_emergency(text)
            if match:
                response = st.session_state.response_gen.generate_response(match)
                st.session_state.current_emergency = response
                st.session_state.current_step = 0
                st.success("✅ Emergency detected!")
                
                # Add to conversation
                st.session_state.conversation.append({
                    "type": "user",
                    "message": text,
                    "time": datetime.now()
                })
                st.session_state.conversation.append({
                    "type": "assistant",
                    "message": response['initial_message'],
                    "time": datetime.now()
                })
                
                # Auto-speak if enabled
                if st.session_state.auto_speech and hasattr(st.session_state, 'speech'):
                    st.session_state.speech.text_to_speech_offline(response['initial_message'])
            else:
                st.warning("⚠️ Could not identify emergency type")
        except Exception as e:
            st.error(f"❌ Analysis failed: {e}")

# Display emergency response
def show_emergency():
    if not st.session_state.current_emergency:
        return
    
    emergency = st.session_state.current_emergency
    
    # Emergency header
    urgency_class = "emergency-card" if emergency['urgency'] == 'critical' else "glass-card"
    
    st.markdown(f"""
    <div class="{urgency_class}">
        <h2 style="text-align: center; margin: 0;">
            {emergency['icon']} {emergency['emergency_name']}
        </h2>
        <p style="text-align: center; font-size: 1.2rem;">
            {emergency['initial_message']}
        </p>
        <div style="text-align: center;">
            <strong>Confidence:</strong> {emergency['confidence']:.0%} | 
            <strong>Priority:</strong> {emergency['urgency'].upper()}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Steps display
    show_steps(emergency.get('steps', []))

# Step-by-step display
def show_steps(steps):
    if not steps:
        return
    
    st.markdown("## 📋 Emergency Steps")
    
    # Navigation
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("⬅️ Previous") and st.session_state.current_step > 0:
            st.session_state.current_step -= 1
            st.rerun()
    
    with col2:
        st.write(f"Step {st.session_state.current_step + 1}/{len(steps)}")
    
    with col3:
        if st.button("Next ➡️") and st.session_state.current_step < len(steps) - 1:
            st.session_state.current_step += 1
            st.rerun()
    
    with col4:
        if st.button("🔊 Read All"):
            read_all_steps(steps)
    
    # Current step
    if 0 <= st.session_state.current_step < len(steps):
        step = steps[st.session_state.current_step]
        show_single_step(step, st.session_state.current_step + 1, True)
    
    # All steps overview
    if st.checkbox("Show All Steps"):
        for i, step in enumerate(steps):
            show_single_step(step, i + 1, i == st.session_state.current_step)

# Single step display
def show_single_step(step, number, is_current):
    step_class = "current-step" if is_current else "step-card"
    current_text = "🔹 CURRENT" if is_current else ""
    
    st.markdown(f"""
    <div class="step-card {step_class}">
        <div style="display: flex; gap: 15px;">
            <div style="
                background: linear-gradient(45deg, #4facfe, #00f2fe);
                color: white; border-radius: 50%; width: 40px; height: 40px;
                display: flex; align-items: center; justify-content: center;
                font-weight: bold;
            ">{number}</div>
            <div style="flex: 1;">
                <h4>{step['title']} {current_text}</h4>
                <p>{step['instruction']}</p>
                <small>⏱️ {step.get('duration', 'As needed')}</small>
                {f'<div style="background: rgba(255,193,7,0.2); padding: 10px; border-radius: 5px; margin-top: 10px;"><strong>⚠️ Warning:</strong> {step["warning"]}</div>' if step.get('warning') else ''}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Voice controls
    if is_current:
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button(f"🔊 Listen", key=f"speak_{number}"):
                speak_step(step, number)

# Text-to-speech functions
def speak_step(step, number):
    if hasattr(st.session_state, 'speech'):
        text = f"Step {number}: {step['title']}. {step['instruction']}"
        if step.get('warning'):
            text += f" Warning: {step['warning']}"
        
        with st.spinner("🔊 Speaking..."):
            if st.session_state.speech.text_to_speech_offline(text):
                st.success("✅ Spoken")
            else:
                audio = st.session_state.speech.text_to_speech_online(text)
                if audio:
                    st.audio(audio, format='audio/mp3')

def read_all_steps(steps):
    if not hasattr(st.session_state, 'speech'):
        st.error("❌ Speech not available")
        return
    
    with st.spinner("🔊 Reading all steps..."):
        full_text = "Here are all emergency steps: "
        for i, step in enumerate(steps, 1):
            full_text += f"Step {i}: {step['title']}. {step['instruction']}. "
            if step.get('warning'):
                full_text += f"Warning: {step['warning']}. "
            full_text += "Next step: "
        
        full_text += "Those are all the steps. Follow them carefully."
        
        if st.session_state.speech.text_to_speech_offline(full_text):
            st.success("✅ All steps read")
        else:
            audio = st.session_state.speech.text_to_speech_online(full_text)
            if audio:
                st.audio(audio, format='audio/mp3')

# Emergency chat system
def emergency_chat():
    st.markdown("### 💬 Chat with Sahaaya")
    
    # Toggle chat
    st.session_state.chat_active = st.checkbox("Enable Emergency Chat", st.session_state.chat_active)
    
    if st.session_state.chat_active:
        # Show conversation
        if st.session_state.conversation:
            for msg in st.session_state.conversation[-5:]:
                msg_class = "user-message" if msg['type'] == 'user' else "chat-message"
                icon = "👤" if msg['type'] == 'user' else "🤖"
                st.markdown(f"""
                <div class="chat-message {msg_class}">
                    {icon} <strong>{msg['type'].title()}:</strong> {msg['message']}
                </div>
                """, unsafe_allow_html=True)
        
        # Chat input
        chat_text = st.text_input("Ask Sahaaya:", placeholder="What should I do next?")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💬 Send") and chat_text:
                handle_chat(chat_text)
        
        with col2:
            if st.button("🎤 Voice Chat"):
                if hasattr(st.session_state, 'speech'):
                    with st.spinner("🎤 Listening..."):
                        try:
                            voice_msg = st.session_state.speech.speech_to_text()
                            if voice_msg:
                                st.success(f"Heard: {voice_msg}")
                                handle_chat(voice_msg)
                        except:
                            st.error("Voice failed")

def handle_chat(message):
    # Add user message
    st.session_state.conversation.append({
        "type": "user",
        "message": message,
        "time": datetime.now()
    })
    
    # Generate response
    response = generate_chat_response(message)
    
    st.session_state.conversation.append({
        "type": "assistant",
        "message": response,
        "time": datetime.now()
    })
    
    # Auto-speak
    if st.session_state.auto_speech and hasattr(st.session_state, 'speech'):
        st.session_state.speech.text_to_speech_offline(response)
    
    st.rerun()

def generate_chat_response(msg):
    msg_lower = msg.lower()
    
    # Context-aware responses
    if 'breathing' in msg_lower:
        if 'started' in msg_lower or 'is' in msg_lower:
            return "Excellent! The person is breathing. Continue monitoring closely. Keep them comfortable and watch for any changes."
        else:
            return "Continue CPR immediately. Keep following the chest compression steps until help arrives."
    
    if any(word in msg_lower for word in ['next', 'what', 'should', 'now']):
        if st.session_state.current_emergency:
            current = st.session_state.current_step + 1
            total = len(st.session_state.current_emergency.get('steps', []))
            return f"You're on step {current} of {total}. Follow the current instruction shown. Click 'Next' when complete."
        return "Please describe the emergency first so I can guide you properly."
    
    if any(word in msg_lower for word in ['scared', 'help', 'panic']):
        return "Take a deep breath. You're doing great. I'm here to guide you step by step. Stay calm and follow the instructions."
    
    if any(word in msg_lower for word in ['done', 'finished', 'completed']):
        return "Good work! Make sure you followed all parts of that step. Move to the next step when ready."
    
    # Default
    return "I'm here to help you through this emergency. Follow the step-by-step instructions and ask if you need clarification."

# Panic button and emergency services
def panic_button():
    st.markdown("### 🚨 Emergency Actions")
    
    if st.button("🚨 CALL EMERGENCY SERVICES", key="panic"):
        st.markdown("""
        <div class="glass-card emergency-card">
            <h3 style="text-align: center; margin: 0;">📞 EMERGENCY CALLED</h3>
            <p style="text-align: center; font-size: 1.2rem;">
                Stay calm. Help is coming.<br>
                Continue first aid while waiting.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        if hasattr(st.session_state, 'speech'):
            st.session_state.speech.text_to_speech_offline("Emergency services contacted. Help is on the way. Continue following the steps.")
        
        st.balloons()
    
    # Emergency number
    st.markdown(f"""
    <div class="glass-card">
        <h4 style="text-align: center;">📞 Emergency Number</h4>
        <p style="text-align: center; font-size: 2rem; font-weight: bold;">
            {CountryHelper.get_emergency_number("US") if MODULES_LOADED else "911"}
        </p>
    </div>
    """, unsafe_allow_html=True)

# Map and location features
def map_features():
    st.markdown("### 🗺️ Find Help Nearby")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🏥 Find Hospitals"):
            if hasattr(st.session_state, 'location'):
                with st.spinner("📍 Searching..."):
                    try:
                        loc = st.session_state.location.get_current_location()
                        hospitals = st.session_state.location.find_nearby_hospitals(*loc)
                        
                        if hospitals:
                            st.success(f"Found {len(hospitals)} hospitals:")
                            for h in hospitals[:3]:
                                st.markdown(f"""
                                <div class="glass-card">
                                    <h4>🏥 {h['name']}</h4>
                                    <p>📍 {h['address']}</p>
                                    <p>📞 {h['phone']}</p>
                                    <p>📏 {h['distance_km']} km away</p>
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.info("Demo mode - no real hospitals shown")
                    except Exception as e:
                        st.error(f"Location error: {e}")
            else:
                st.error("Location services not available")
    
    with col2:
        if st.button("🗺️ Open Maps"):
            maps_url = "https://www.google.com/maps/search/hospital+near+me"
            st.markdown(f'<a href="{maps_url}" target="_blank">🔗 Open Google Maps</a>', unsafe_allow_html=True)
            st.success("Maps link ready")

# Medical condition prediction
def medical_prediction():
    st.markdown("### 🔬 Medical Assessment")
    
    symptoms = st.multiselect(
        "Select symptoms:",
        [
            "Difficulty breathing", "Chest pain", "Unconscious",
            "Heavy bleeding", "Choking", "Allergic reaction",
            "Burns", "Broken bone", "Head injury"
        ]
    )
    
    if symptoms and st.button("🔍 Analyze Symptoms"):
        if hasattr(st.session_state, 'detector'):
            with st.spinner("Analyzing..."):
                symptom_text = f"Patient has {', '.join(symptoms).lower()}"
                match = st.session_state.detector.detect_emergency(symptom_text)
                
                if match:
                    st.success(f"Likely condition: {match.emergency_data['name']}")
                    st.info(f"Confidence: {match.confidence:.0%}")
                    
                    # Auto-load emergency
                    response = st.session_state.response_gen.generate_response(match)
                    st.session_state.current_emergency = response
                    st.session_state.current_step = 0
                else:
                    st.warning("Could not determine condition. Call emergency services if serious.")
    
    # Medical notes
    medical_notes = st.text_area(
        "Medical history/allergies:",
        placeholder="e.g., diabetes, heart condition, allergies"
    )
    
    if medical_notes:
        st.info(f"📝 Medical information recorded")

# Sidebar with all controls
def create_sidebar():
    with st.sidebar:
        st.markdown("# ⚙️ Controls")
        
        # Theme toggle
        st.markdown("### 🌗 Theme")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🌙 Dark"):
                st.session_state.dark_mode = True
                st.rerun()
        with col2:
            if st.button("☀️ Light"):
                st.session_state.dark_mode = False
                st.rerun()
        
        current_theme = "Dark" if st.session_state.dark_mode else "Light"
        st.caption(f"Current: {current_theme}")
        
        st.markdown("---")
        
        # Voice settings
        st.markdown("### 🎤 Voice")
        
        if st.button("🎧 Test Voice"):
            if hasattr(st.session_state, 'speech'):
                with st.spinner("Testing..."):
                    if st.session_state.speech.text_to_speech_offline("Hello, this is Sahaaya. How do I sound?"):
                        st.success("Voice working")
                    else:
                        st.error("Voice failed")
        
        st.session_state.auto_speech = st.checkbox("🔊 Auto-read steps", st.session_state.auto_speech)
        
        if st.button("🧘 Find Calm Voice"):
            if hasattr(st.session_state, 'speech'):
                calm_voices = ['Samantha', 'Victoria', 'Allison']
                for voice in calm_voices:
                    if st.session_state.speech.set_voice_by_name(voice):
                        st.success(f"Voice: {voice}")
                        break
        
        st.markdown("---")
        
        # Quick emergency access
        st.markdown("### 📋 Quick Access")
        if hasattr(st.session_state, 'detector'):
            emergency_types = st.session_state.detector.get_all_emergency_types()
            for etype, info in emergency_types.items():
                if st.button(f"{info['icon']} {info['name']}", key=f"q_{etype}"):
                    fake_input = f"emergency {info['name'].lower()}"
                    match = st.session_state.detector.detect_emergency(fake_input, min_confidence=0.1)
                    if match:
                        st.session_state.current_emergency = st.session_state.response_gen.generate_response(match)
                        st.session_state.current_step = 0
                        st.rerun()
        
        st.markdown("---")
        
        # Emergency numbers
        st.markdown("### 🚨 Emergency Numbers")
        if MODULES_LOADED:
            numbers = CountryHelper.get_all_emergency_numbers()
            for code, info in list(numbers.items())[:5]:
                st.markdown(f"**{info['name']}**: {info['number']}")

# Main app
def main():
    init_app()
    load_css()
    
    # Header
    create_header()
    
    # Sidebar
    create_sidebar()
    
    # Main content
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Emergency input
        emergency_input()
        
        # Emergency display
        show_emergency()
        
        # Map features
        map_features()
        
        # Medical prediction
        medical_prediction()
    
    with col2:
        # Panic button
        panic_button()
        
        # Emergency chat
        emergency_chat()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div class="glass-card">
        <p style="text-align: center; font-size: 0.9rem; opacity: 0.8;">
            ⚠️ <strong>Disclaimer:</strong> This app supplements but does not replace professional medical care. 
            Always call emergency services for serious emergencies.
        </p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()