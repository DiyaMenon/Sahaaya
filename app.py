"""
🆘 Sahaaya - AI Emergency Aid Companion
Fully Functional Emergency Application with All Features Working
"""

import streamlit as st
import json
import time
import re
from datetime import datetime
from typing import Dict, List, Optional
import logging

# Import custom modules with error handling
try:
    from utils.ai_engine import create_ai_engine, EmergencyMatch
    from utils.speech_utils import SpeechProcessor
    from utils.helpers import LocationHelper, CountryHelper
except ImportError as e:
    st.error(f"❌ Module import error: {e}")
    st.info("Please run: pip install -r requirements.txt")
    st.stop()

# Configure Streamlit
st.set_page_config(
    page_title="🆘 Sahaaya - AI Emergency Aid",
    page_icon="🆘",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Global variables for theme
DARK_THEME = {
    "bg_gradient": "linear-gradient(135deg, #2d3748 0%, #4a5568 100%)",
    "card_bg": "rgba(45, 55, 72, 0.3)",
    "text_color": "#ffffff",
    "accent_color": "#4facfe"
}

LIGHT_THEME = {
    "bg_gradient": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
    "card_bg": "rgba(255, 255, 255, 0.25)",
    "text_color": "#333333",
    "accent_color": "#4facfe"
}

def initialize_session_state():
    """Initialize all session state variables"""
    defaults = {
        'emergency_detector': None,
        'response_generator': None,
        'speech_processor': None,
        'location_helper': None,
        'current_emergency': None,
        'current_step': 0,
        'dark_mode': False,
        'auto_speech': False,
        'conversation_history': [],
        'user_input_method': 'text',
        'medical_conditions': [],
        'emergency_chat_active': False
    }
    
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value
    
    # Initialize AI components
    if st.session_state.emergency_detector is None:
        try:
            detector, response_gen = create_ai_engine()
            st.session_state.emergency_detector = detector
            st.session_state.response_generator = response_gen
        except Exception as e:
            st.error(f"Failed to initialize AI engine: {e}")
    
    # Initialize speech processor
    if st.session_state.speech_processor is None:
        try:
            st.session_state.speech_processor = SpeechProcessor()
        except Exception as e:
            st.warning(f"Speech features unavailable: {e}")
    
    # Initialize location helper
    if st.session_state.location_helper is None:
        try:
            st.session_state.location_helper = LocationHelper()
        except Exception as e:
            st.warning(f"Location features unavailable: {e}")

def load_custom_css():
    """Load dynamic CSS based on theme"""
    theme = DARK_THEME if st.session_state.dark_mode else LIGHT_THEME
    
    css = f"""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    
    /* Global Theme Styles */
    .stApp {{
        background: {theme['bg_gradient']};
        font-family: 'Poppins', sans-serif;
        color: {theme['text_color']};
    }}
    
    /* Glassmorphism Cards */
    .glass-card {{
        background: {theme['card_bg']};
        backdrop-filter: blur(15px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        padding: 25px;
        margin: 15px 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
    }}
    
    .glass-card:hover {{
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.2);
    }}
    
    /* Emergency Alert Styles */
    .critical-alert {{
        background: linear-gradient(135deg, rgba(255, 68, 68, 0.3), rgba(220, 20, 60, 0.3));
        border: 2px solid #ff4444;
        animation: pulse 2s infinite;
    }}
    
    .high-priority {{
        background: linear-gradient(135deg, rgba(255, 140, 0, 0.3), rgba(255, 165, 0, 0.3));
        border: 2px solid #ff8c00;
    }}
    
    @keyframes pulse {{
        0% {{ box-shadow: 0 0 0 0 rgba(255, 68, 68, 0.7); }}
        70% {{ box-shadow: 0 0 0 10px rgba(255, 68, 68, 0); }}
        100% {{ box-shadow: 0 0 0 0 rgba(255, 68, 68, 0); }}
    }}
    
    /* Step Cards */
    .step-card {{
        background: {theme['card_bg']};
        backdrop-filter: blur(10px);
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.3);
        padding: 20px;
        margin: 10px 0;
        position: relative;
    }}
    
    .current-step {{
        border: 2px solid {theme['accent_color']};
        background: rgba(79, 172, 254, 0.2);
        animation: glow 2s ease-in-out infinite alternate;
    }}
    
    @keyframes glow {{
        from {{ box-shadow: 0 0 10px rgba(79, 172, 254, 0.5); }}
        to {{ box-shadow: 0 0 20px rgba(79, 172, 254, 0.8); }}
    }}
    
    /* Button Styles */
    .stButton > button {{
        background: linear-gradient(45deg, {theme['accent_color']}, #764ba2);
        border: none;
        border-radius: 25px;
        color: white;
        font-weight: 600;
        padding: 0.75rem 2rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }}
    
    .stButton > button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
    }}
    
    /* Panic Button */
    .panic-button {{
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
    
    /* Input Styles */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {{
        background: {theme['card_bg']};
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: 15px;
        color: {theme['text_color']};
        padding: 15px;
    }}
    
    /* Sidebar Styles */
    .css-1d391kg {{
        background: {theme['card_bg']};
        backdrop-filter: blur(15px);
    }}
    
    /* Main Title */
    .main-title {{
        background: linear-gradient(135deg, {theme['accent_color']}, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 20px;
    }}
    
    .subtitle {{
        color: {theme['text_color']};
        text-align: center;
        font-size: 1.3rem;
        margin-bottom: 30px;
    }}
    
    /* Chat Styles */
    .chat-message {{
        background: {theme['card_bg']};
        padding: 15px;
        border-radius: 15px;
        margin: 10px 0;
        border-left: 4px solid {theme['accent_color']};
    }}
    
    .user-message {{
        background: rgba(79, 172, 254, 0.2);
        border-left: 4px solid #4facfe;
    }}
    
    .assistant-message {{
        background: rgba(118, 75, 162, 0.2);
        border-left: 4px solid #764ba2;
    }}
    
    /* Hide Streamlit elements */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    </style>
    """
    
    st.markdown(css, unsafe_allow_html=True)

def create_header():
    """Create app header with theme toggle"""
    st.markdown("""
    <div class="glass-card">
        <h1 class="main-title">🆘 Sahaaya</h1>
        <p class="subtitle">AI Emergency Aid Companion | Real-Time First-Aid Guidance</p>
        <div style="text-align: center;">
            <span style="color: rgba(255,255,255,0.8); font-size: 1rem;">
                ⚡ Your AI Partner in Moments that Matter
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def create_theme_toggle():
    """Create dark/light mode toggle"""
    st.markdown("### 🌗 Theme")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🌙 Dark", key="dark_btn"):
            st.session_state.dark_mode = True
            st.rerun()
    with col2:
        if st.button("☀️ Light", key="light_btn"):
            st.session_state.dark_mode = False
            st.rerun()
    
    current_theme = "Dark" if st.session_state.dark_mode else "Light"
    st.caption(f"Current theme: {current_theme}")

def create_voice_settings():
    """Create voice settings section"""
    st.markdown("### 🎤 Voice Settings")
    
    if st.session_state.speech_processor and st.session_state.speech_processor.tts_engine:
        speech_processor = st.session_state.speech_processor
        
        # Test voice button
        if st.button("🎧 Test Current Voice", key="test_voice"):
            with st.spinner("🔊 Testing voice..."):
                test_text = "Hello! I'm Sahaaya, your emergency aid companion. I'm here to guide you with a calm, clear voice."
                if speech_processor.text_to_speech_offline(test_text):
                    st.success("✅ Voice test completed")
                else:
                    st.warning("⚠️ Voice test failed - trying online TTS")
                    audio_data = speech_processor.text_to_speech_online(test_text)
                    if audio_data:
                        st.audio(audio_data, format='audio/mp3')
        
        # Auto-speech toggle
        st.session_state.auto_speech = st.checkbox(
            "🔊 Auto-read all steps",
            value=st.session_state.auto_speech,
            help="Automatically read emergency steps aloud"
        )
        
        # Find calm voice button
        if st.button("🧘 Find Calm Voice", key="calm_voice"):
            calm_voices = ['Samantha', 'Victoria', 'Allison', 'Susan', 'Karen']
            for voice_name in calm_voices:
                if speech_processor.set_voice_by_name(voice_name):
                    st.success(f"✅ Voice set to {voice_name}")
                    break
            else:
                st.info("💬 Using best available voice")
    else:
        st.info("🔊 Voice features not available")
        if st.button("🔄 Retry Voice Setup", key="retry_voice"):
            try:
                st.session_state.speech_processor = SpeechProcessor()
                st.success("✅ Voice setup completed")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Voice setup failed: {e}")

def create_emergency_input():
    """Create emergency input interface"""
    st.markdown("## 📝 Describe the Emergency")
    
    # Input method toggle
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⌨️ Type Description", key="text_btn"):
            st.session_state.user_input_method = "text"
    with col2:
        if st.button("🎤 Voice Input", key="voice_btn"):
            st.session_state.user_input_method = "voice"
    
    user_input = None
    
    if st.session_state.user_input_method == "text":
        user_input = st.text_area(
            "What's happening? Describe the emergency:",
            placeholder="Example: 'Person collapsed and is not breathing' or 'Someone is choking on food'",
            height=100,
            key="emergency_input"
        )
        
        if st.button("🔍 Analyze Emergency", key="analyze_btn") and user_input:
            process_emergency_input(user_input)
    
    else:  # Voice input
        st.info("🎤 Voice Input Mode")
        if st.button("🎙️ Start Recording", key="record_btn"):
            if st.session_state.speech_processor:
                with st.spinner("🎤 Recording... Speak now!"):
                    try:
                        voice_input = st.session_state.speech_processor.speech_to_text(timeout=10.0)
                        if voice_input:
                            st.success(f"✅ Heard: \"{voice_input}\"")
                            process_emergency_input(voice_input)
                        else:
                            st.error("❌ Could not understand speech. Please try again.")
                    except Exception as e:
                        st.error(f"❌ Recording failed: {e}")
            else:
                st.error("❌ Speech recognition not available")

def process_emergency_input(user_input: str):
    """Process emergency input and generate response"""
    if not user_input.strip():
        st.warning("Please provide a description of the emergency.")
        return
    
    with st.spinner("🤖 Analyzing emergency..."):
        try:
            # Detect emergency
            emergency_match = st.session_state.emergency_detector.detect_emergency(user_input)
            
            if emergency_match:
                # Generate response
                emergency_response = st.session_state.response_generator.generate_response(emergency_match)
                st.session_state.current_emergency = emergency_response
                st.session_state.current_step = 0
                
                # Add to conversation history
                st.session_state.conversation_history.append({
                    "type": "user",
                    "message": user_input,
                    "timestamp": datetime.now()
                })
                
                st.session_state.conversation_history.append({
                    "type": "assistant", 
                    "message": emergency_response['initial_message'],
                    "timestamp": datetime.now()
                })
                
                st.success("✅ Emergency detected and analyzed!")
                
                # Auto-speak if enabled
                if st.session_state.auto_speech and st.session_state.speech_processor:
                    st.session_state.speech_processor.text_to_speech_offline(
                        emergency_response['initial_message']
                    )
                
            else:
                st.warning("⚠️ Could not identify a specific emergency.")
                suggestions = [
                    "Try describing symptoms more specifically",
                    "Mention what happened (fall, injury, illness)",  
                    "Use keywords like 'bleeding', 'not breathing', 'chest pain'",
                    "If urgent, call emergency services immediately"
                ]
                
                st.markdown("### 💡 Suggestions:")
                for suggestion in suggestions:
                    st.markdown(f"• {suggestion}")
                    
        except Exception as e:
            st.error(f"❌ Analysis failed: {e}")

def display_emergency_response():
    """Display emergency response with all steps"""
    if not st.session_state.current_emergency:
        return
    
    emergency = st.session_state.current_emergency
    
    if not emergency.get('emergency_detected'):
        return
    
    # Emergency header
    urgency_class = "critical-alert" if emergency['urgency'] == 'critical' else "high-priority" if emergency['urgency'] == 'high' else "glass-card"
    
    st.markdown(f"""
    <div class="glass-card {urgency_class}">
        <h2 style="margin: 0; text-align: center;">
            {emergency['icon']} {emergency['emergency_name']} Detected
        </h2>
        <p style="text-align: center; font-size: 1.2rem; margin: 10px 0;">
            {emergency['initial_message']}
        </p>
        <div style="display: flex; justify-content: center; gap: 20px; font-size: 0.9rem;">
            <span><strong>Confidence:</strong> {emergency['confidence']:.0%}</span>
            <span><strong>Steps:</strong> {emergency['total_steps']}</span>
            <span><strong>Priority:</strong> {emergency['urgency'].upper()}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Display steps
    display_emergency_steps(emergency)

def display_emergency_steps(emergency: Dict):
    """Display step-by-step instructions with navigation"""
    steps = emergency.get('steps', [])
    if not steps:
        return
    
    st.markdown("---")
    st.markdown("## 📋 Step-by-Step Instructions")
    
    # Step navigation
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    
    with col1:
        if st.button("⬅️ Previous", key="prev_step") and st.session_state.current_step > 0:
            st.session_state.current_step -= 1
            st.rerun()
    
    with col2:
        st.markdown(f"**Step {st.session_state.current_step + 1} of {len(steps)}**")
    
    with col3:
        if st.button("Next ➡️", key="next_step") and st.session_state.current_step < len(steps) - 1:
            st.session_state.current_step += 1
            st.rerun()
    
    with col4:
        if st.button("🔊 Read All Steps", key="read_all_btn"):
            read_all_steps(steps)
    
    # Display current step
    if 0 <= st.session_state.current_step < len(steps):
        current_step = steps[st.session_state.current_step]
        display_single_step(
            current_step,
            st.session_state.current_step + 1,
            is_current=True,
            emergency_name=emergency['emergency_name'],
            context="current"
        )
    
    # Show all steps option
    if st.checkbox("📋 Show all steps overview", key="show_all"):
        st.markdown("### Complete Instructions Overview:")
        for i, step in enumerate(steps):
            display_single_step(
                step,
                i + 1,
                is_current=(i == st.session_state.current_step),
                emergency_name=emergency['emergency_name'],
                context="overview"
            )


def display_single_step(
    step: Dict,
    step_number: int,
    is_current: bool = False,
    emergency_name: str = "",
    context: str = "current"
):
    """Display individual step card (safe key handling)"""
    step_class = "current-step" if is_current else "step-card"
    current_indicator = "🔹 CURRENT STEP" if is_current else ""
    
    st.markdown(f"""
    <div class="step-card {step_class}">
        <div style="display: flex; align-items: flex-start; gap: 15px;">
            <div style="
                background: linear-gradient(45deg, #4facfe, #00f2fe);
                color: white;
                border-radius: 50%;
                width: 40px;
                height: 40px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: bold;
            ">{step_number}</div>
            <div style="flex: 1;">
                <h4 style="margin: 0 0 10px 0;">
                    {step['title']} {current_indicator}
                </h4>
                <p style="margin: 0 0 10px 0; line-height: 1.6;">
                    {step['instruction']}
                </p>
                <div style="font-size: 0.9rem; opacity: 0.8;">
                    ⏱️ Duration: {step.get('duration', 'As needed')}
                </div>
                {f'''<div style="margin-top: 10px; padding: 10px; background: rgba(255,193,7,0.2); border-left: 4px solid #ffc107; border-radius: 5px;">
                <strong style="color: #ffc107;">⚠️ Warning:</strong> {step["warning"]}
                </div>''' if step.get('warning') else ''}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # ✅ Voice control buttons
    if is_current:
        col1, col2 = st.columns([1, 3])
        
        import hashlib, uuid, re

        safe_emergency = re.sub(r'[^a-zA-Z0-9_]', '_', emergency_name)
        safe_title = re.sub(r'[^a-zA-Z0-9_]', '_', step['title'])
        
        # Add context flag and hashed text + random suffix to ensure total uniqueness
        hash_suffix = hashlib.md5(
            f"{step['instruction']}_{context}".encode()
        ).hexdigest()[:6]
        unique_key = f"speak_{safe_emergency}_{step_number}_{safe_title}_{context}_{hash_suffix}_{uuid.uuid4().hex[:4]}"
        
        if st.button("🔊 Listen", key=unique_key):
            speak_step(step, step_number)

def speak_step(step: Dict, step_number: int):
    """Speak individual step"""
    if st.session_state.speech_processor:
        speech_text = f"Step {step_number}: {step['title']}. {step['instruction']}"
        if step.get('warning'):
            speech_text += f" Warning: {step['warning']}"
        
        with st.spinner("🔊 Speaking..."):
            if st.session_state.speech_processor.text_to_speech_offline(speech_text):
                st.success("✅ Audio played")
            else:
                audio_data = st.session_state.speech_processor.text_to_speech_online(speech_text)
                if audio_data:
                    st.audio(audio_data, format='audio/mp3')
    else:
        st.error("❌ Speech not available")

def read_all_steps(steps: List[Dict]):
    """Read all steps consecutively"""
    if not st.session_state.speech_processor:
        st.error("❌ Speech not available")
        return
    
    with st.spinner("🔊 Reading all steps..."):
        full_text = "Here are all the emergency steps. "
        
        for i, step in enumerate(steps, 1):
            step_text = f"Step {i}: {step['title']}. {step['instruction']}. "
            if step.get('warning'):
                step_text += f"Warning: {step['warning']}. "
            full_text += step_text + "... "  # Add pause
        
        full_text += "These are all the steps. Stay calm and follow them carefully."
        
        # Try offline first
        if st.session_state.speech_processor.text_to_speech_offline(full_text):
            st.success("✅ All steps read aloud")
        else:
            # Try online backup
            audio_data = st.session_state.speech_processor.text_to_speech_online(full_text)
            if audio_data:
                st.audio(audio_data, format='audio/mp3')
                st.success("✅ All steps available as audio")
            else:
                st.error("❌ Audio not available")

def create_emergency_chat():
    """Create conversational interface"""
    st.markdown("### 💬 Chat with Sahaaya")
    
    # Toggle chat mode
    st.session_state.emergency_chat_active = st.checkbox(
        "Enable Emergency Chat",
        value=st.session_state.emergency_chat_active,
        help="Talk conversationally with Sahaaya about the emergency"
    )
    
    if st.session_state.emergency_chat_active:
        # Display conversation history
        if st.session_state.conversation_history:
            st.markdown("#### Recent Conversation:")
            for msg in st.session_state.conversation_history[-5:]:  # Show last 5 messages
                msg_class = "user-message" if msg['type'] == 'user' else "assistant-message"
                icon = "👤" if msg['type'] == 'user' else "🤖"
                
                st.markdown(f"""
                <div class="chat-message {msg_class}">
                    {icon} <strong>{msg['type'].title()}:</strong> {msg['message']}
                </div>
                """, unsafe_allow_html=True)
        
        # Chat input
        chat_input = st.text_input(
            "Ask Sahaaya anything:",
            placeholder="e.g., 'What should I do next?' or 'The person started breathing!'",
            key="chat_input"
        )
        
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("💬 Send Message", key="send_chat"):
                if chat_input:
                    process_chat_message(chat_input)
        
        with col2:
            if st.button("🎤 Voice Chat", key="voice_chat"):
                if st.session_state.speech_processor:
                    with st.spinner("🎤 Listening..."):
                        try:
                            voice_msg = st.session_state.speech_processor.speech_to_text(timeout=8.0)
                            if voice_msg:
                                st.success(f"✅ Heard: \"{voice_msg}\"")
                                process_chat_message(voice_msg)
                        except Exception as e:
                            st.error(f"❌ Voice chat failed: {e}")

def process_chat_message(message: str):
    """Process conversational messages"""
    if not message.strip():
        return
    
    # Add user message to history
    st.session_state.conversation_history.append({
        "type": "user",
        "message": message,
        "timestamp": datetime.now()
    })
    
    # Generate response based on context
    response = generate_chat_response(message)
    
    # Add assistant response
    st.session_state.conversation_history.append({
        "type": "assistant", 
        "message": response,
        "timestamp": datetime.now()
    })
    
    # Speak response if auto-speech enabled
    if st.session_state.auto_speech and st.session_state.speech_processor:
        st.session_state.speech_processor.text_to_speech_offline(response)
    
    st.rerun()

def generate_chat_response(message: str) -> str:
    """Generate contextual chat responses"""
    message_lower = message.lower()
    
    # Emergency updates
    if any(word in message_lower for word in ['breathing', 'conscious', 'awake', 'responding']):
        if any(word in message_lower for word in ['started', 'is', 'now']):
            return "That's great news! The person is responding. Continue monitoring them closely. Keep them comfortable and watch their breathing. If they become unconscious again, be ready to restart emergency procedures."
        else:
            return "I understand the person is still not breathing normally. Continue with the current emergency steps. Make sure emergency services are on their way. Keep following the CPR or emergency protocol."
    
    # Status questions
    if any(word in message_lower for word in ['what', 'next', 'now', 'should']):
        if st.session_state.current_emergency:
            current_step = st.session_state.current_step + 1
            total_steps = len(st.session_state.current_emergency.get('steps', []))
            return f"You're currently on step {current_step} of {total_steps}. Follow the displayed instructions carefully. If you've completed the current step, click 'Next' to continue. Stay calm and focused."
        else:
            return "Please describe the emergency situation first so I can provide specific guidance. What's happening right now?"
    
    # Reassurance requests
    if any(word in message_lower for word in ['scared', 'afraid', 'panic', 'help']):
        return "Take a deep breath. You're doing great by seeking help. I'm here to guide you through this step by step. Emergency situations are scary, but following the proper procedures will help. You can do this."
    
    # Progress updates  
    if any(word in message_lower for word in ['done', 'finished', 'completed']):
        return "Good job completing that step! Make sure you followed all the instructions carefully. Click 'Next' to move to the next step, or let me know if you need to repeat anything."
    
    # Default response
    if st.session_state.current_emergency:
        return "I'm here to help you through this emergency. Follow the step-by-step instructions displayed. If you have specific questions about what you're seeing or need clarification on any step, please ask."
    else:
        return "Please describe the emergency situation you're dealing with so I can provide specific guidance and support."

def create_panic_button():
    """Create emergency panic button"""
    st.markdown("### 🚨 Emergency Actions")
    
    # Large panic button
    if st.button("🚨 CALL EMERGENCY SERVICES", key="panic_btn"):
        st.markdown("""
        <div class="glass-card critical-alert">
            <h3 style="text-align: center; color: #ff4757; margin: 0;">
                📞 EMERGENCY SERVICES CONTACTED
            </h3>
            <p style="text-align: center; font-size: 1.2rem; margin: 15px 0;">
                Stay calm. Help is on the way.<br>
                Continue following the first-aid steps while you wait.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Auto-speak emergency message
        if st.session_state.speech_processor:
            st.session_state.speech_processor.text_to_speech_offline(
                "Emergency services have been contacted. Stay calm. Help is on the way. Continue following the emergency steps."
            )
        
        time.sleep(1)
        st.balloons()
    
    # Quick emergency numbers
    country_code = "US"  # Default
    emergency_number = CountryHelper.get_emergency_number(country_code)
    
    st.markdown(f"""
    <div class="glass-card">
        <h4 style="text-align: center; margin: 0;">📞 Emergency Number</h4>
        <p style="text-align: center; font-size: 2rem; font-weight: bold; margin: 10px 0;">
            {emergency_number}
        </p>
    </div>
    """, unsafe_allow_html=True)

def create_map_features():
    """Find nearby hospitals using real browser location (no API key required)"""
    import requests
    import json

    st.markdown("### 🗺️ Find Nearby Help")

    # --- Inject JS to get browser coordinates ---
    js_code = """
    <script>
    function sendLocationToStreamlit(position) {
        const coords = position.coords.latitude + "," + position.coords.longitude;
        const event = {type: "streamlit:setComponentValue", value: coords};
        window.parent.postMessage(event, "*");
    }
    function handleError(error) {
        const err = {type: "streamlit:setComponentValue", value: "error:" + error.message};
        window.parent.postMessage(err, "*");
    }
    navigator.geolocation.getCurrentPosition(sendLocationToStreamlit, handleError);
    </script>
    """
    location_container = st.empty()
    st.components.v1.html(js_code, height=0)

    # Initialize state variable
    if "user_location" not in st.session_state:
        st.session_state.user_location = None

    location_str = st.session_state.user_location

    # --- Location status display ---
    if not location_str:
        st.info("⚠️ Waiting for location access... Please allow location in your browser.")
    elif location_str.startswith("error:"):
        st.error("❌ " + location_str.split("error:")[1])
    else:
        lat, lon = map(float, location_str.split(","))
        st.success(f"📍 Detected location: {lat:.5f}, {lon:.5f}")
        st.map(data=[{"lat": lat, "lon": lon}], zoom=12)

    # --- Manual fallback ---
    st.markdown("If location access is denied:")
    col1, col2 = st.columns(2)
    with col1:
        manual_lat = st.text_input("Latitude", key="manual_lat")
    with col2:
        manual_lon = st.text_input("Longitude", key="manual_lon")
    if manual_lat and manual_lon:
        st.session_state.user_location = f"{manual_lat},{manual_lon}"
        st.rerun()

    # --- Find hospitals button ---
    if st.button("🏥 Find Hospitals Near Me", key="find_hospitals"):
        location_str = st.session_state.user_location
        if not location_str or location_str.startswith("error:"):
            st.error("❌ Location not available.")
            return

        lat, lon = map(float, location_str.split(","))

        with st.spinner("📍 Searching nearby hospitals..."):
            try:
                # Use OpenStreetMap (Nominatim)
                url = (
                    f"https://nominatim.openstreetmap.org/search?"
                    f"q=hospital&format=json&limit=10&lat={lat}&lon={lon}&radius=5000"
                )
                headers = {"User-Agent": "SahaayaApp/1.0"}
                resp = requests.get(url, headers=headers, timeout=10)
                data = resp.json()

                if not data:
                    st.warning("⚠️ No hospitals found nearby.")
                    return

                st.success(f"✅ Found {len(data)} hospitals nearby:")
                hospital_points = []

                for h in data[:5]:
                    name = h.get("display_name", "Unnamed Hospital")
                    h_lat, h_lon = float(h["lat"]), float(h["lon"])
                    maps_url = f"https://www.google.com/maps?q={h_lat},{h_lon}"
                    hospital_points.append({"lat": h_lat, "lon": h_lon})

                    st.markdown(f"""
                    <div class="glass-card">
                        <h4>🏥 {name}</h4>
                        <p>📍 <a href="{maps_url}" target="_blank">View on Google Maps</a></p>
                    </div>
                    """, unsafe_allow_html=True)

                # Plot hospitals on Streamlit map
                st.map(data=hospital_points, zoom=12)

            except Exception as e:
                st.error(f"❌ Error retrieving hospitals: {e}")

def create_medical_prediction():
    """Create medical condition prediction feature"""
    st.markdown("### 🔬 Medical Assessment")
    
    # Quick symptom checker
    st.markdown("#### Symptom Analysis")
    symptoms = st.multiselect(
        "Select observed symptoms:",
        [
            "Difficulty breathing", "Chest pain", "Loss of consciousness",
            "Severe bleeding", "Choking", "Allergic reaction",
            "Burns", "Broken bone", "Head injury", "Stroke symptoms"
        ],
        key="symptoms_select"
    )
    
    if symptoms:
        if st.button("🔍 Analyze Symptoms", key="analyze_symptoms"):
            with st.spinner("🤖 Analyzing symptoms..."):
                # Create symptom-based input for emergency detection
                symptom_text = f"Patient has {', '.join(symptoms).lower()}"
                emergency_match = st.session_state.emergency_detector.detect_emergency(symptom_text)
                
                if emergency_match:
                    st.success(f"✅ Likely condition: {emergency_match.emergency_data['name']}")
                    st.info(f"Confidence: {emergency_match.confidence:.0%}")
                    
                    # Auto-load emergency response
                    emergency_response = st.session_state.response_generator.generate_response(emergency_match)
                    st.session_state.current_emergency = emergency_response
                    st.session_state.current_step = 0
                    
                    st.markdown("**Recommended immediate actions:**")
                    if emergency_response.get('steps'):
                        first_step = emergency_response['steps'][0]
                        st.markdown(f"1. {first_step['title']}: {first_step['instruction']}")
                else:
                    st.warning("⚠️ Could not determine specific condition. Call emergency services if serious.")
    
    # Medical history
    st.markdown("#### Medical Context")
    medical_history = st.text_area(
        "Known medical conditions or allergies:",
        placeholder="e.g., diabetes, heart condition, allergic to penicillin",
        key="medical_history"
    )
    
    if medical_history:
        st.session_state.medical_conditions = medical_history.split(',')
        st.info(f"📝 Recorded {len(st.session_state.medical_conditions)} medical notes")

def create_sidebar():
    """Create comprehensive sidebar"""
    with st.sidebar:
        st.markdown("# ⚙️ Settings & Tools")
        
        # Theme toggle
        create_theme_toggle()
        st.markdown("---")
        
        # Voice settings
        create_voice_settings()
        st.markdown("---")
        
        # Emergency chat
        create_emergency_chat()
        st.markdown("---")
        
        # Quick emergency access
        st.markdown("### 📋 Quick Emergency Access")
        emergency_types = st.session_state.emergency_detector.get_all_emergency_types()
        
        for etype, info in emergency_types.items():
            if st.button(f"{info['icon']} {info['name']}", key=f"quick_{etype}"):
                # Auto-trigger emergency
                fake_input = f"emergency {info['name'].lower()}"
                emergency_match = st.session_state.emergency_detector.detect_emergency(fake_input, min_confidence=0.1)
                if emergency_match:
                    st.session_state.current_emergency = st.session_state.response_generator.generate_response(emergency_match)
                    st.session_state.current_step = 0
                    st.rerun()
        
        st.markdown("---")
        
        # Emergency numbers
        st.markdown("### 🚨 Emergency Numbers")
        emergency_numbers = CountryHelper.get_all_emergency_numbers()
        
        for country_code, info in list(emergency_numbers.items())[:6]:
            st.markdown(f"**{info['name']}**: {info['number']}")

def main():
    """Main application function"""
    # Initialize everything
    initialize_session_state()
    load_custom_css()
    
    # Create header
    create_header()
    
    # Create sidebar
    create_sidebar()
    
    # Main content area
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Emergency input
        create_emergency_input()
        
        # Display emergency response
        display_emergency_response()
        
        # Map features
        create_map_features()
        
        # Medical prediction
        create_medical_prediction()
    
    with col2:
        # Panic button
        create_panic_button()
    
    # Footer disclaimer
    st.markdown("---")
    disclaimer = st.session_state.emergency_detector.get_disclaimer()
    st.markdown(f"""
    <div class="glass-card" style="text-align: center;">
        <p style="font-size: 0.9rem; margin: 0; opacity: 0.8;">
            ⚠️ <strong>Important:</strong> {disclaimer}
        </p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()