import io
import json
import os
import wave
import numpy as np
import requests
import scipy.io.wavfile as wavfile
import streamlit as st
from streamlit_mic_recorder import mic_recorder

# ==========================================
# CONFIGURATION & GNANI.AI CREDENTIALS
# ==========================================
GNANI_TOKEN = os.getenv("GNANI_TOKEN", "YOUR_GNANI_TOKEN_HERE")
GNANI_ACCESS_KEY = os.getenv("GNANI_ACCESS_KEY", "YOUR_GNANI_ACCESS_KEY_HERE")
GNANI_API_URL = "https://asr.gnani.ai/asr"

# ==========================================
# PAGE CONFIGURATION (Professional App UI)
# ==========================================
st.set_page_config(
    page_title="Emergency Indic Voice Assistant",
    page_icon="🚨",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ==========================================
# CUSTOM CSS STYLING (Native Mobile App Look)
# ==========================================
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    .app-header {
        background: linear-gradient(135deg, #d32f2f, #b71c1c);
        padding: 1.5rem;
        border-radius: 16px;
        text-align: center;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 15px rgba(211, 47, 47, 0.4);
    }
    .app-header h1 {
        margin: 0;
        font-size: 1.8rem;
        font-weight: 700;
        color: white;
    }
    .app-header p {
        margin: 0.4rem 0 0 0;
        font-size: 0.95rem;
        color: #ffcdd2;
    }
    .emergency-card {
        background-color: #1e222b;
        border: 1px solid #2e3440;
        border-radius: 14px;
        padding: 1.2rem;
        margin-bottom: 1rem;
        transition: transform 0.2s, border-color 0.2s;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
    }
    .emergency-card:hover {
        border-color: #ef5350;
    }
    .card-title {
        font-size: 1.15rem;
        font-weight: 600;
        margin-bottom: 0.3rem;
        color: #ffffff;
    }
    .card-number {
        font-size: 1.3rem;
        font-weight: 700;
        color: #ff5252;
    }
    .status-box {
        background-color: #161b22;
        border-left: 4px solid #58a6ff;
        padding: 1rem;
        border-radius: 8px;
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 11-LANGUAGE INDIC & CODE-MIXED FRAMEWORK
# ==========================================
LANGUAGES = {
    "Kannada (ಕನ್ನಡ / Kanglish)": {"code": "kn_IN", "label": "ಕನ್ನಡ"},
    "Hindi (हिन्दी / Hinglish)": {"code": "hi_IN", "label": "हिन्दी"},
    "English (India)": {"code": "en_IN", "label": "English"},
    "Tamil (தமிழ் / Tanglish)": {"code": "ta_IN", "label": "தமிழ்"},
    "Telugu (తెలుగు / Tenglish)": {"code": "te_IN", "label": "తెలుగు"},
    "Malayalam (മലയാളം / Manglish)": {"code": "ml_IN", "label": "മലയാളം"},
    "Marathi (मराठी)": {"code": "mr_IN", "label": "मराठी"},
    "Bengali (বাংলা)": {"code": "bn_IN", "label": "বাংলা"},
    "Gujarati (ગુજરાતી)": {"code": "gu_IN", "label": "ગુજરાતી"},
    "Punjabi (ਪੰਜਾਬੀ)": {"code": "pa_IN", "label": "ਪੰਜਾਬੀ"},
    "Odia (ଓଡ଼ିଆ)": {"code": "or_IN", "label": "ଓଡ଼ିଆ"}
}

EMERGENCY_SERVICES = {
    "ambulance": {
        "title": "🚑 Medical & Ambulance",
        "number": "108",
        "desc": "Critical medical emergency, accident, or hospital transport.",
        "keywords": [
            "ambulance", "medical", "hospital", "doctor", "accident", "blood", "heart", "injury", "pain",
            "ಆಂಬ್ಯುಲೆನ್ಸ್", "ಆಸ್ಪತ್ರೆ", "ಡಾಕ್ಟರ್", "ಅಪಘಾತ", "एम्बुलेंस", "अस्पताल", "डॉक्टर",
            "ஆம்புலன்ஸ்", "மருத்துவமனை", "అంబులెన్స్", "ఆసుపత్రి", "ആംബുലൻസ്"
        ]
    },
    "police": {
        "title": "🚓 Police Control Room",
        "number": "112 / 100",
        "desc": "Crime, theft, personal safety threat, or law enforcement.",
        "keywords": [
            "police", "theft", "crime", "robbery", "danger", "attack", "help", "unsafe", "stolen",
            "ಪೊಲೀಸ್", "ಕಳ್ಳತನ", "ಸಹಾಯ", "पुलिस", "चोरी", "बचाओ",
            "போலீஸ்", "காவல்துறை", "పోలీస్", "പോലീസ്"
        ]
    },
    "fire": {
        "title": "🚒 Fire & Rescue Services",
        "number": "101",
        "desc": "Fire outbreak, gas leak, building collapse, or rescue.",
        "keywords": [
            "fire", "smoke", "burn", "gas", "cylinder", "blast", "rescue",
            "ಬೆಂಕಿ", "ಅಗ್ನಿಶಾಮಕ", "आग", "फायर", "தீ", "फायर ब्रिगेड", "अग्निशामक", "मदद"
        ]
    },
    "women": {
        "title": "🛡️ Women & Child Helpline",
        "number": "1091 / 181",
        "desc": "Immediate assistance for women and children in distress.",
        "keywords": [
            "women", "girl", "harassment", "stalking", "domestic", "child", "safety",
            "ಮಹಿಳಾ", "ಮಕ್ಕಳ", "महिला", "सुरक्षा", "பெண்கள்", "महिला हेल्पलाइन"
        ]
    },
    "cyber": {
        "title": "💻 Cyber Crime & Fraud",
        "number": "1930",
        "desc": "UPI fraud, banking scam, OTP theft, or online harassment.",
        "keywords": [
            "cyber", "fraud", "scam", "money", "upi", "bank", "hacked", "otp",
            "ಸೈಬರ್", "ವಂಚನೆ", "साइबर", "धोखाधड़ी", "बैंक"
        ]
    },
    "disaster": {
        "title": "🌊 Disaster Management (NDRF)",
        "number": "1078",
        "desc": "Flood, earthquake, cyclone, landslide, or severe weather.",
        "keywords": [
            "flood", "earthquake", "rain", "storm", "landslide", "disaster", "cyclone",
            "ಪ್ರವಾಹ", "ಭೂಕಂಪ", "बाढ़", "भूकंप", "आपदा"
        ]
    }
}

# ==========================================
# AUDIO PROCESSING & SPEECH-TO-TEXT
# ==========================================
def transcribe_audio(audio_bytes, lang_code):
    """Sends recorded audio bytes to Gnani.ai ASR API with fallback handling."""
    if not audio_bytes:
        return ""

    # If API credentials are valid, call Gnani.ai API
    if GNANI_TOKEN != "YOUR_GNANI_TOKEN_HERE" and GNANI_ACCESS_KEY != "YOUR_GNANI_ACCESS_KEY_HERE":
        try:
            headers = {
                "token": GNANI_TOKEN,
                "accesskey": GNANI_ACCESS_KEY,
                "lang": lang_code,
                "audioformat": "wav"
            }
            files = {"audio_file": ("voice.wav", io.BytesIO(audio_bytes), "audio/wav")}
            response = requests.post(GNANI_API_URL, headers=headers, files=files, timeout=15)
            if response.status_code == 200:
                data = response.json()
                return data.get("transcript", "")
        except Exception as e:
            st.warning(f"API Connection Notice: Switching to fallback mode ({e})")

    return None

def detect_intent(text):
    """Detects emergency category from multilingual or code-mixed text."""
    if not text:
        return []
    text_lower = text.lower()
    matched = []
    for key, service in EMERGENCY_SERVICES.items():
        if any(kw.lower() in text_lower for kw in service["keywords"]):
            matched.append(service)
    return matched

# ==========================================
# MAIN APPLICATION UI
# ==========================================
st.markdown("""
<div class="app-header">
    <h1>🚨 Indic Voice Emergency Response</h1>
    <p>Multilingual & Code-Mixed AI Voice Assistant (11 Languages)</p>
</div>
""", unsafe_allow_html=True)

# 1. Language Selection
selected_lang_name = st.selectbox(
    "🌐 Select Your Language / ನಿಮ್ಮ ಭಾಷೆಯನ್ನು ಆಯ್ಕೆಮಾಡಿ / अपनी भाषा चुनें",
    options=list(LANGUAGES.keys()),
    index=0
)
current_lang_code = LANGUAGES[selected_lang_name]["code"]

st.write("### 🎙️ Speak Your Emergency")
st.caption("Speak naturally (supports pure regional languages as well as Kanglish, Hinglish, Tanglish, etc.)")

# 2. Browser Microphone Recorder (Cloud-Safe)
audio_data = mic_recorder(
    start_prompt="🔴 Tap to Speak Emergency",
    stop_prompt="⏹️ Stop Recording",
    just_once=False,
    use_container_width=True,
    format="wav",
    key="emergency_recorder"
)

# 3. Text / Manual Input Fallback for Testing
manual_query = st.text_input(
    "⌨️ Or type your emergency (e.g., 'Need ambulance jaldi', 'ಪೊಲೀಸ್ ಸಹಾಯ ಬೇಕು'):",
    placeholder="Type here if microphone is unavailable..."
)

# Process Voice or Text Input
active_transcript = ""

if audio_data and "bytes" in audio_data:
    st.audio(audio_data["bytes"], format="audio/wav")
    with st.spinner("Processing voice input..."):
        transcript_result = transcribe_audio(audio_data["bytes"], current_lang_code)
        if transcript_result:
            active_transcript = transcript_result
        else:
            st.info("💡 Voice recorded! (Add your `GNANI_TOKEN` and `GNANI_ACCESS_KEY` in Streamlit Secrets for live ASR, or test intent routing using the text box above.)")

if manual_query:
    active_transcript = manual_query

# Display Detected Intent & Actionable Response
if active_transcript:
    st.markdown(f"""
    <div class="status-box">
        <strong>🗣️ Recognized Input ({LANGUAGES[selected_lang_name]['label']}):</strong><br>
        "{active_transcript}"
    </div>
    """, unsafe_allow_html=True)

    matched_services = detect_intent(active_transcript)

    st.write("### ⚡ Immediate Action Recommended")
    if matched_services:
        for service in matched_services:
            st.markdown(f"""
            <div class="emergency-card" style="border-color: #ff5252; background-color: #2b1d1d;">
                <div class="card-title">{service['title']}</div>
                <div class="card-number">📞 Dial: <a href="tel:{service['number'].split()[0]}" style="color: #ff5252; text-decoration: underline;">{service['number']}</a></div>
                <div style="font-size: 0.9rem; color: #cfd8dc; margin-top: 0.4rem;">{service['desc']}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("General Emergency Detected — Routing to National Emergency Number (112)")
        st.markdown("""
        <div class="emergency-card" style="border-color: #ffa726;">
            <div class="card-title">🚨 National Emergency Response System (ERSS)</div>
            <div class="card-number">📞 Dial: <a href="tel:112" style="color: #ffa726; text-decoration: underline;">112</a></div>
            <div style="font-size: 0.9rem; color: #cfd8dc; margin-top: 0.4rem;">All-in-one emergency dispatch for Police, Fire, and Ambulance.</div>
        </div>
        """, unsafe_allow_html=True)

st.divider()

# ==========================================
# QUICK-DIAL EMERGENCY DIRECTORY GRID
# ==========================================
st.write("### 📋 Quick-Dial Emergency Directory")
col1, col2 = st.columns(2)

services_list = list(EMERGENCY_SERVICES.values())
for idx, srv in enumerate(services_list):
    target_col = col1 if idx % 2 == 0 else col2
    with target_col:
        st.markdown(f"""
        <div class="emergency-card">
            <div class="card-title">{srv['title']}</div>
            <div class="card-number"><a href="tel:{srv['number'].split()[0]}" style="color: #ff5252; text-decoration: none;">📞 {srv['number']}</a></div>
            <div style="font-size: 0.85rem; color: #b0bec5; margin-top: 0.3rem;">{srv['desc']}</div>
        </div>
        """, unsafe_allow_html=True)
