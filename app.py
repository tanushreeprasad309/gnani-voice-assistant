import io
import json
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
==========================================
STYLING
==========================================
st.markdown("""
<style>
.stApp { background-color: #f8fafc; color: #1e293b; }
.header-banner {
background: linear-gradient(135deg, #dc2626, #991b1b);
padding: 1.5rem;
border-radius: 16px;
text-align: center;
color: white;
margin-bottom: 1.5rem;
}
.emergency-card {
background-color: white;
border: 1px solid #e2e8f0;
border-left: 5px solid #dc2626;
border-radius: 8px;
padding: 1rem;
margin-bottom: 1rem;
box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}
</style>
""", unsafe_allow_html=True)
==========================================
11-LANGUAGE SUPPORTED DATA
==========================================
LANGUAGES = {
"en_IN": "English (India)",
"hi_IN": "हिन्दी (Hindi)",
"kn_IN": "ಕನ್ನಡ (Kannada)",
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
"keywords": ["ambulance", "hospital", "doctor", "accident", "heart", "injury", "medical", "ಆಂಬ್ಯುಲೆನ್ಸ್", "ಆಸ್ಪತ್ರೆ", "ಎಕ್ಸಿಡೆಂಟ್", "hospital", "доктор"],
"desc": "Immediate dispatch for medical crises, severe injuries, or transport."
},
{
"title": "Police Control Room",
"number": "112",
"keywords": ["police", "attack", "crime", "theft", "danger", "fight", "robbery", "поліція", "پुलिस", "ಪೊಲೀಸ್"],
"desc": "Assistance for crime, safety threats, or law enforcement."
},
{
"title": "Fire and Rescue Services",
"number": "101",
"keywords": ["fire", "burn", "smoke", "cylander", "blast", "rescue", "आग", "ಬೆಂಕಿ"],
"desc": "Emergency response for fires, gas leaks, or entrapment."
},
{
"title": "Women Helpline",
"number": "1091",
"keywords": ["women", "harassment", "abuse", "safety", "women safety", "महिला", "ಮಹಿಳಾ ಸಹಾಯ"],
"desc": "Dedicated support and protection for women in distress."
},
{
"title": "Disaster Management",
"number": "1078",
"keywords": ["flood", "earthquake", "cyclone", "landslide", "disaster", "ಭೂಕಂಪ", "बाढ़"],
"desc": "Support during natural calamities and severe weather events."
}
]
==========================================
BACKEND LOGIC (Mockable ASR)
==========================================
def process_audio_transcription(audio_bytes, lang_code):
"""
Sends audio to Gnani API if credentials exist,
otherwise returns a safe fallback message to prevent crashes.
"""
token = os.getenv("GNANI_TOKEN")
access_key = os.getenv("GNANI_ACCESS_KEY")
if token and access_key and token != "YOUR_GNANI_TOKEN_HERE":
try:
url = "https://asr.gnani.ai/asr"
headers = {"token": token, "accesskey": access_key, "lang": lang_code}
files = {"audio_file": ("voice.wav", io.BytesIO(audio_bytes), "audio/wav")}
response = requests.post(url, headers=headers, files=files, timeout=10)
if response.status_code == 200:
return response.json().get("transcript", "")
except Exception:
pass # Fallback to text matching
return None
def match_emergency(transcript_text):
if not transcript_text:
return []
text_lower = transcript_text.lower()
matches = []
for service in EMERGENCY_DIRECTORY:
if any(kw in text_lower for kw in service["keywords"]):
matches.append(service)
return matches
==========================================
UI LAYOUT
==========================================
st.markdown("""
<div class="header-banner">
<h1>🚨 Sahaya Emergency Assistant</h1>
<p>Multilingual Emergency Response & Directory</p>
</div>
""", unsafe_allow_html=True)
Language Selector
selected_lang_label = st.selectbox(
"🌐 Select Language / भाषा / ಭಾಷೆ",
options=list(LANGUAGES.values()),
index=0
)
Reverse lookup code
lang_code = [k for k, v in LANGUAGES.items() if v == selected_lang_label][0]
st.write("### 🎙️ Voice Input")
audio_info = mic_recorder(
start_prompt="🔴 Tap to Speak",
stop_prompt="⏹️ Stop Recording",
just_once=True,
key="mic"
)
st.write("### ⌨️ Or Type Request")
manual_text = st.text_input("Type your emergency here (e.g., 'Need ambulance', 'Accident happened'):")
Execution Flow
final_transcript = ""
if audio_info and "bytes" in audio_info:
st.audio(audio_info["bytes"], format="audio/wav")
with st.spinner("Processing voice..."):
transcription = process_audio_transcription(audio_info["bytes"], lang_code)
if transcription:
final_transcript = transcription
else:
final_transcript = manual_text # Fallback to manual if audio processing fails/skips
if manual_text:
final_transcript = manual_text
Results Display
if final_transcript:
st.info(f"Detected Input: {final_transcript}")
matched_services = match_emergency(final_transcript)
st.write("---")
st.header("⚡ Recommended Action")
if matched_services:
for service in matched_services:
st.markdown(f"""
<div class="emergency-card">
<h3>{service['title']}</h3>
<p>{service['desc']}</p>
<a href="tel:{service['number']}">
<button style="background-color:#dc2626; color:white; border:none; padding:10px 20px; border-radius:5px; font-weight:bold; cursor:pointer;">
📞 Call {service['number']}
</button>
</a>
</div>
""", unsafe_allow_html=True)
else:
st.warning("No specific emergency matched. Please use the general emergency number below.")
st.markdown("""
<div class="emergency-card" style="border-left-color: #ca8a04;">
<h3>General Emergency Helpline</h3>
<p>Universal emergency response.</p>
<a href="tel:112">
<button style="background-color:#ca8a04; color:white; border:none; padding:10px 20px; border-radius:5px; font-weight:bold; cursor:pointer;">
📞 Call 112
</button>
</a>
</div>
""", unsafe_allow_html=True)
st.divider()
Directory Section
st.header("📋 Emergency Directory")
for srv in EMERGENCY_DIRECTORY:
st.markdown(f"""
<div style="background:white; padding:10px; margin-bottom:10px; border-radius:5px; border:1px solid #e2e8f0; display:flex; justify-content:space-between; align-items:center;">
<div>
<strong>{srv['title']}</strong>
<span style="color:#64748b; font-size:0.9em;">{srv['desc']}</span>
</div>
<a href="tel:{srv['number']}" style="background:#e2e8f0; color:#1e293b; padding:8px 16px; border-radius:5px; text-decoration:none; font-weight:bold;">
📞 {srv['number']}
</a>
</div>
""", unsafe_allow_html=True)
