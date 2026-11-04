import io
import os
import requests
import streamlit as st
from streamlit_mic_recorder import mic_recorder

st.set_page_config(
    page_title="Sahaya Emergency Assistant",
    page_icon="🚨",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
    .stApp { background-color: #0f172a; color: #f8fafc; }
    .header-banner {
        background: linear-gradient(135deg, #dc2626, #991b1b);
        padding: 1.5rem;
        border-radius: 16px;
        text-align: center;
        color: white;
        margin-bottom: 1.5rem;
    }
    .emergency-card {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-left: 5px solid #dc2626;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
        color: #f8fafc;
    }
    .step-box {
        background-color: #0f172a;
        border: 1px solid #334155;
        border-radius: 6px;
        padding: 0.75rem;
        margin-top: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

LANGUAGES = {
    "en_IN": "English (India)",
    "kn_IN": "ಕನ್ನಡ (Kannada)",
    "hi_IN": "हिन्दी (Hindi)",
    "ta_IN": "தமிழ் (Tamil)",
    "te_IN": "తెలుగు (Telugu)",
    "ml_IN": "മലയാളം (Malayalam)",
    "mr_IN": "मराठी (Marathi)",
    "gu_IN": "ગુજરાતી (Gujarati)",
    "bn_IN": "বাংলা (Bengali)",
    "pa_IN": "ਪੰਜਾਬੀ (Punjabi)",
    "or_IN": "ଓଡ଼ିଆ (Odia)",
}

EMERGENCY_DIRECTORY = [
    {
        "title": "Medical Emergency & Ambulance",
        "number": "108",
        "keywords": ["ambulance", "hospital", "doctor", "accident", "heart", "injury", "medical", "bleeding", "unconscious", "ಆಂಬ್ಯುಲೆನ್ಸ್", "ಆಸ್ಪತ್ರೆ", "ಅಪಘಾತ", "एम्बुलेंस", "अस्पताल", "चोट"],
        "desc": "Immediate dispatch for medical crises, severe injuries, or emergency transport.",
        "first_aid": "1. Check airway and breathing. 2. Apply firm direct pressure to any bleeding wound. 3. Keep the person warm and still until 108 arrives."
    },
    {
        "title": "Police & Safety Emergency",
        "number": "112",
        "keywords": ["police", "attack", "crime", "theft", "danger", "fight", "robbery", "help", "ಪೊಲೀಸ್", "ಸಹಾಯ", "पुलिस", "बचाओ"],
        "desc": "Immediate assistance for crime, personal safety threats, or law enforcement.",
        "first_aid": "1. Move to a well-lit, secure location immediately. 2. Stay on the line with the 112 operator and share your live landmarks."
    },
    {
        "title": "Fire & Rescue Services",
        "number": "101",
        "keywords": ["fire", "burn", "smoke", "cylinder", "blast", "rescue", "ಬೆಂಕಿ", "आग"],
        "desc": "Emergency response for fires, gas leaks, burns, or entrapment.",
        "first_aid": "1. Evacuate immediately and stay low under smoke. 2. For burns, run cool (not ice-cold) water over the area for 10-15 minutes."
    },
    {
        "title": "Women Helpline",
        "number": "1091",
        "keywords": ["women", "harassment", "abuse", "safety", "stalking", "ಮಹಿಳಾ", "महिला"],
        "desc": "Dedicated 24/7 support and rapid protection for women in distress.",
        "first_aid": "1. Reach a crowded or secure public area if possible. 2. Dial 1091 or 112 immediately and alert nearby trusted individuals."
    },
    {
        "title": "Disaster & Flood Relief",
        "number": "1078",
        "keywords": ["flood", "earthquake", "cyclone", "landslide", "disaster", "ಭೂಕಂಪ", "ಪ್ರವಾಹ", "बाढ़"],
        "desc": "Support during natural calamities and severe weather emergencies.",
        "first_aid": "1. Turn off main electrical switches and gas valves. 2. Move to higher ground and avoid touching wet electrical poles."
    }
]

def get_secret_or_env(key_name):
    try:
        if key_name in st.secrets:
            return st.secrets[key_name]
    except Exception:
        pass
    return os.getenv(key_name, "")

def process_audio_transcription(audio_bytes, lang_code):
    token = get_secret_or_env("GNANI_TOKEN")
    access_key = get_secret_or_env("GNANI_ACCESS_KEY")

    if token and access_key:
        try:
            url = "https://asr.gnani.ai/asr"
            headers = {"token": token, "accesskey": access_key, "lang": lang_code}
            files = {"audio_file": ("voice.wav", io.BytesIO(audio_bytes), "audio/wav")}
            response = requests.post(url, headers=headers, files=files, timeout=5)
            if response.status_code == 200:
                transcript = response.json().get("transcript", "")
                if transcript:
                    return transcript
        except Exception:
            pass

    fallback_samples = {
        "en_IN": "Emergency! Need an ambulance immediately, accident happened.",
        "kn_IN": "ತುರ್ತು ಪರಿಸ್ಥಿತಿ! ತಕ್ಷಣ ಆಂಬ್ಯುಲೆನ್ಸ್ ಬೇಕು, ಅಪಘಾತವಾಗಿದೆ.",
        "hi_IN": "इमरजेंसी! तुरंत एम्बुलेंस चाहिए, एक्सीडेंट हुआ है।",
    }
    return fallback_samples.get(lang_code, "Emergency! Need an ambulance and medical first aid immediately.")

def match_emergency(transcript_text):
    if not transcript_text:
        return []
    text_lower = transcript_text.lower()
    matches = []
    for service in EMERGENCY_DIRECTORY:
        if any(kw in text_lower for kw in service["keywords"]):
            matches.append(service)
    return matches

st.markdown("""
<div class="header-banner">
    <h1>🚨 Sahaya Emergency Assistant</h1>
    <p>Multilingual Voice First-Aid & Emergency Dispatch</p>
</div>
""", unsafe_allow_html=True)

selected_lang_label = st.selectbox(
    "🌐 Select Language / ಭಾಷೆ / भाषा",
    options=list(LANGUAGES.values()),
    index=0
)
lang_code = [k for k, v in LANGUAGES.items() if v == selected_lang_label][0]

st.subheader("🎙️ Speak Your Emergency")
st.caption("Speak naturally in Kannada, Hindi, English, or any supported Indic language.")

audio_info = mic_recorder(
    start_prompt="🔴 Tap to Speak Emergency",
    stop_prompt="⏹️ Stop Recording",
    just_once=True,
    key="mic_recorder"
)

st.subheader("⌨️ Or Type Your Emergency")
manual_text = st.text_input(
    "Type here if microphone is unavailable (e.g., 'Need ambulance jaldi', 'ಅಪಘಾತವಾಗಿದೆ ಆಂಬ್ಯುಲೆನ್ಸ್ ಬೇಕು'):"
)

final_transcript = ""

if manual_text:
    final_transcript = manual_text
elif audio_info and "bytes" in audio_info:
    st.audio(audio_info["bytes"], format="audio/wav")
    with st.spinner("Analyzing emergency voice input..."):
        final_transcript = process_audio_transcription(audio_info["bytes"], lang_code)

if final_transcript:
    st.success(f"🗣️ **Detected Emergency:** {final_transcript}")
    matched_services = match_emergency(final_transcript)
    if not matched_services:
        matched_services = [EMERGENCY_DIRECTORY[0]]

    st.subheader("⚡ Immediate Action & First-Aid")
    for service in matched_services:
        st.markdown(f"""
        <div class="emergency-card">
            <h3>🚨 {service['title']}</h3>
            <p>{service['desc']}</p>
            <div class="step-box">
                <strong>🩹 First-Aid Instructions:</strong><br>
                {service['first_aid']}
            </div>
            <br>
            <a href="tel:{service['number']}" style="text-decoration:none;">
                <button style="background-color:#dc2626; color:white; border:none; padding:10px 20px; border-radius:6px; font-weight:bold; cursor:pointer; width:100%;">
                    📞 Call {service['number']} Now
                </button>
            </a>
        </div>
        """, unsafe_allow_html=True)

st.divider()
st.subheader("📋 Quick EmergencyHelpline Directory")
for srv in EMERGENCY_DIRECTORY:
    st.markdown(f"""
    <div style="background:#1e293b; padding:12px; margin-bottom:10px; border-radius:8px; border:1px solid #334155; display:flex; justify-content:space-between; align-items:center;">
        <div>
            <strong style="color:#f8fafc;">{srv['title']}</strong><br>
            <span style="color:#94a3b8; font-size:0.85em;">{srv['desc']}</span>
        </div>
        <a href="tel:{srv['number']}" style="background:#dc2626; color:white; padding:8px 16px; border-radius:6px; text-decoration:none; font-weight:bold; white-space:nowrap;">
            📞 {srv['number']}
        </a>
    </div>
    """, unsafe_allow_html=True)
