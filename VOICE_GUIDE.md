# 🎤 How to Change the Scary Voice in Sahaaya

Don't worry! The scary voice can be easily fixed. Here are several ways to get a calming voice:

## 🚀 Quick Fix Options

### Option 1: Use the Voice Testing Script (Recommended)
```bash
python test_voices.py
```

This interactive script will:
- Show you all available voices on your system
- Let you test each voice with emergency guidance text
- Help you find the most calming voices
- Rate voices from 1-5 for calmness

### Option 2: Use the App's Voice Settings
1. Run the app: `streamlit run app.py`
2. Look in the **sidebar** for "🎤 Voice Settings"
3. Try the **"🧾 Find Calm Voice"** button first
4. Or use the dropdown to manually select different voices
5. Click **"🎧 Test Voice"** to hear each one

### Option 3: Manual Quick Fix
If you know which voice you want, edit the file directly:

1. Open `utils/speech_utils.py`
2. Find the `_select_best_voice` function (around line 80)
3. Add your preferred voice name to the top of the `preferred_voices` list

## 🧘 Recommended Calm Voices

### On macOS:
- **Samantha** (most popular calm voice)
- **Victoria** 
- **Allison**
- **Susan**
- **Moira**

### On Windows:
- **Zira**
- **Hazel** 
- **Catherine**

### On Linux:
- **Female voices** (if available through espeak)

## 🔧 What I Changed to Make Voices Less Scary

1. **Slower Speech Rate**: Reduced from 150 to 130 words per minute
2. **Softer Volume**: Reduced from 0.9 to 0.8
3. **Better Voice Selection**: Prioritizes known calm voices
4. **Calmer Language**: Converts scary words like "EMERGENCY" to "emergency"
5. **Gentle Pauses**: Adds "..." for breathing space
6. **Polite Phrasing**: Adds "Please" to instructions

## 🎧 Testing Your Voice

### Quick Test Command:
```bash
cd /Users/diyasatish/Projects/sahaaya
python -c "
from utils.speech_utils import SpeechProcessor
processor = SpeechProcessor()
processor.test_voice('Hello, I am your calm emergency guide. How do I sound now?')
"
```

### Test Different Voices:
```bash
python test_voices.py
```

## 🚨 If Voices Still Sound Scary

1. **Try Different Voices**: Some system voices are naturally more robotic
2. **Install More Voices**: 
   - macOS: System Preferences > Accessibility > Speech > System Voice
   - Windows: Settings > Time & Language > Speech
3. **Use Online TTS**: The app falls back to Google's TTS which is usually calmer
4. **Adjust Settings**: You can modify the speech rate and volume in the code

## 💡 Pro Tips

- **Female voices** tend to sound more calming in emergencies
- **Slower speech** (120-140 WPM) sounds more reassuring
- **Lower volume** (0.7-0.8) sounds less aggressive
- **Test with actual emergency text** to make sure it sounds right

## 🔍 Finding Your System's Best Voice

Run this command to see all your available voices:
```bash
python -c "
from utils.speech_utils import SpeechProcessor
processor = SpeechProcessor()
voices = processor.get_available_voices()
print('Available voices:')
for i, voice in enumerate(voices, 1):
    print(f'{i}. {voice[\"name\"]} ({voice.get(\"gender\", \"Unknown\")})')
"
```

## 📞 Still Need Help?

If you're still having issues:
1. Try the `test_voices.py` script first
2. Check if you have multiple voices installed on your system
3. The app will automatically fall back to online TTS (Google) if offline TTS fails

Remember: The goal is to have a voice that sounds calm and reassuring during emergencies! 🧘‍♀️