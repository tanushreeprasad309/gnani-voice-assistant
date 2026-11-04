import io
import os
import requests
import streamlit as st
from streamlit_mic_recorder import mic_recorder

# --------------------------------------------------
# PAGE CONFIGURATION (Professional App Styling)
# --------------------------------------------------
st.set_page_config(
    page_title="Sahaya Emergency Assistant",
    page_icon="🚨",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Professional CSS Styling
st.markdown("""
    <style>
    .main {
        background-color: #f4f6f8;
    }
    .stApp {
        max-width: 800px;
        margin: 0 auto;
    }
    div.stButton > button {
        width: 100%;
        border-radius: 12px;
        height: 75px;
        font-size: 15px;
        font-weight: 700;
        background-color: #ffffff;
        border: 1px solid #dcdfe6;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        transition: all 0.2s ease;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 5px;
    }
    div.stButton > button:hover {
        border-color: #ff4b4b;
        color: #ff4b4b;
        box-shadow: 0 6px 12px rgba(255,75,75,0.15);
        transform: translateY(-2px);
    }
    .emergency-title {
        color: #1e293b;
        font-weight: 800;
        text-align: center;
        margin-bottom: 20px;
    }
    .custom-divider {
        height: 2px;
        background-color: #e2e8f0;
        margin: 25px 0;
    }
    </style>
""", unsafe_allow_html=True)

# App Header
st.title("🚨 Sahaya Emergency Assistant")
st.markdown("Your intelligent, multilingual first-aid companion. Select an emergency below for immediate, step-by-step guidance.")

st.error(
    "⚠️ **CRITICAL DISCLAIMER**: Sahaya provides immediate first-aid instructions "
    "and informational guidance. It is NOT an emergency dispatch service and cannot "
    "automatically contact emergency services. In India, dial **112** immediately for "
    "police, ambulance, or fire rescue."
)

# --------------------------------------------------
# CREDENTIALS & API CONFIGURATION
# --------------------------------------------------
def get_secret(name):
    try:
        val = st.secrets.get(name)
        if val:
            return val
    except Exception:
        pass
    return os.getenv(name, "")

GNANI_TOKEN = get_secret("GNANI_TOKEN")
GNANI_ACCESS_KEY = get_secret("GNANI_ACCESS_KEY")

STT_API_URL = "https://asr.gnani.ai/recognize"
TTS_API_URL = "https://tts.gnani.ai/synthesize"

LANGUAGE_MAP = {
    "en-IN": "English",
    "kn-IN": "ಕನ್ನಡ (Kannada)",
    "hi-IN": "हिन्दी (Hindi)",
}

# --------------------------------------------------
# COMPREHENSIVE KNOWLEDGE BASE (Major & Minor Scenarios)
# --------------------------------------------------
EMERGENCY_DATA = {
    # MAJOR EMERGENCIES
    "earthquake": {
        "label": "Earthquake", "icon": "🫨",
        "en-IN": "Sahaya here: DROP, COVER, and HOLD ON. Get under a sturdy table, protect your head, and stay away from glass and outer walls. Do not use elevators. Dial 112 once shaking stops.",
        "kn-IN": "ನಾನು ಸಹಾಯ: ತಕ್ಷಣ ನೆಲಕ್ಕೆ ಬಗ್ಗಿ, ಗಟ್ಟಿಯಾದ ಮೇಜಿನ ಕೆಳಗೆ ಆಶ್ರಯ ಪಡೆಯಿರಿ. ಕಿಟಕಿಗಳು ಮತ್ತು ಗೋಡೆಗಳಿಂದ ದೂರವಿರಿ. ಲಿಫ್ಟ್ ಬಳಸಬೇಡಿ. ಕಂಪನ ನಿಂತ ಮೇಲೆ 112 ಗೆ ಕರೆ ಮಾಡಿ.",
        "hi-IN": "मैं सहाय हूँ: तुरंत नीचे झुकें, मजबूत मेज के नीचे सिर ढकें। खिड़कियों और दीवारों से दूर रहें। लिफ्ट का उपयोग न करें। झटके रुकने पर 112 डायल करें।"
    },
    "heart_attack": {
        "label": "Cardiac Arrest", "icon": "💔",
        "en-IN": "Sahaya here: Keep patient calm and seated with knees bent. Loosen tight clothing. If conscious and not allergic, give one 300mg Aspirin to chew. Call 112 immediately.",
        "kn-IN": "ನಾನು ಸಹಾಯ: ರೋಗಿಯನ್ನು ಆರಾಮವಾಗಿ ಕುಳ್ಳಿರಿಸಿ. ಬಿಗಿಯಾದ ಬಟ್ಟೆ ಸಡಿಲಗೊಳಿಸಿ. ಅಲರ್ಜಿ ಇಲ್ಲದಿದ್ದರೆ 300mg ಆಸ್ಪಿರಿನ್ ಜಗಿದು ನುಂಗಲು ಕೊಡಿ. ತಕ್ಷಣ 112 ಗೆ ಕರೆ ಮಾಡಿ.",
        "hi-IN": "मैं सहाय हूँ: मरीज को आराम से बैठाएं। कपड़े ढीले करें। एलर्जी न होने पर 300mg एस्पिरिन चबाने को दें। तुरंत 112 पर कॉल करें।"
    },
    "accident": {
        "label": "Road Accident", "icon": "🚗",
        "en-IN": "Sahaya here: Ensure your own safety first. Do not move an unconscious victim unless there is imminent danger of fire or explosion. Check breathing and call 112 immediately.",
        "kn-IN": "ನಾನು ಸಹಾಯ: ಮೊದಲು ನಿಮ್ಮ ಸುರಕ್ಷತೆ ಮುಖ್ಯ. ಬೆಂಕಿಯ ಅಪಾಯವಿದ್ದರೆ ಮಾತ್ರ ಪ್ರಜ್ಞಾಹೀನರನ್ನು ಸ್ಥಳಾಂತರಿಸಿ. ಉಸಿರಾಟ ಪರೀಕ್ಷಿಸಿ ತಕ್ಷಣ 112 ಗೆ ಕರೆ ಮಾಡಿ.",
        "hi-IN": "मैं सहाय हूँ: पहले अपनी सुरक्षा देखें। आग का खतरा न होने पर घायल को न हिलाएं। सांस की जांच करें और तुरंत 112 डायल करें।"
    },
    "electric_shock": {
        "label": "Electric Shock", "icon": "⚡",
        "en-IN": "Sahaya here: DO NOT touch the victim with bare hands. Switch off the main power supply immediately or use a dry wooden object to push them away from the source. Dial 112.",
        "kn-IN": "ನಾನು ಸಹಾಯ: ಬರಿಗೈಯಿಂದ ಮುಟ್ಟಬೇಡಿ! ಕೂಡಲೇ ಮುಖ್ಯ ವಿದ್ಯುತ್ ಸ್ವಿಚ್ ಆಫ್ ಮಾಡಿ ಅಥವಾ ಒಣ ಮರದ ಕೋಲಿನಿಂದ ವ್ಯಕ್ತಿಯನ್ನು ದೂರ ತಳ್ಳಿ. 112 ಗೆ ಕರೆ ಮಾಡಿ.",
        "hi-IN": "मैं सहाय हूँ: पीड़ित को नंगे हाथों से न छुएं! तुरंत मेन स्विच बंद करें या सूखी लकड़ी की मदद से तार से अलग करें। 112 डायल करें।"
    },
    "stroke": {
        "label": "Stroke (FAST)", "icon": "🧠",
        "en-IN": "Sahaya here: Check F.A.S.T. (Facial drooping, Arm weakness, Speech difficulty, Time to call 112). Keep patient resting, do not give food or water, rush to hospital.",
        "kn-IN": "ನಾನು ಸಹಾಯ: ಮುಖ ಕೋಣೆಯಾಗಿದೆಯೇ, ಕೈ ಬಲಹೀನವಾಗಿದೆಯೇ, ಮಾತು ತೊದಲುತ್ತಿದೆಯೇ ಗಮನಿಸಿ (FAST). ಏನನ್ನೂ ತಿನ್ನಲು ಕೊಡಬೇಡಿ, ತಕ್ಷಣ ಆಸ್ಪತ್ರೆಗೆ ತನ್ನಿ.",
        "hi-IN": "मैं सहाय हूँ: FAST जांचें—चेहरा लटकना, हाथ में कमजोरी, बोलने में दिक्कत। कुछ भी खाने-पीने को न दें, तुरंत अस्पताल ले जाएं।"
    },
    
    # MEDIUM / FIRST AID EMERGENCIES
    "burn": {
        "label": "Burns & Scalds", "icon": "🔥",
        "en-IN": "Sahaya here: Cool the burn under clean running tap water for 15-20 minutes. Do not apply ice, butter, or ointments. Cover loosely with a sterile bandage.",
        "kn-IN": "ನಾನು ಸಹಾಯ: ಸುಟ್ಟ ಗಾಯದ ಮೇಲೆ 15-20 ನಿಮಿಷ ಹರಿಯುವ ತಣ್ಣೀರು ಸುರಿಯಿರಿ. ಮಂಜುಗಡ್ಡೆ ಅಥವಾ ಎಣ್ಣೆ ಹಚ್ಚಬೇಡಿ. ಸ್ವಚ್ಛ ಬಟ್ಟೆಯಿಂದ ಸಡಿಲವಾಗಿ ಮುಚ್ಚಿ.",
        "hi-IN": "मैं सहाय हूँ: जले हुए अंग पर 15-20 मिनट ठंडा पानी डालें। बर्फ या तेल न लगाएं। साफ पट्टी से ढीले ढंग से ढकें।"
    },
    "snake": {
        "label": "Snake Bite", "icon": "🐍",
        "en-IN": "Sahaya here: Keep victim strictly immobile and calm to prevent venom spread. Keep bitten limb below heart level. Do not cut or suction the wound. Seek hospital care immediately.",
        "kn-IN": "ನಾನು ಸಹಾಯ: ವಿಷ ಹರಡದಂತೆ ವ್ಯಕ್ತಿಯನ್ನು ಕದಲದಂತೆ ಶಾಂತವಾಗಿರಿಸಿ. ಕಚ್ಚಿದ ಭಾಗವನ್ನು ಹೃದಯಕ್ಕಿಂತ ಕೆಳಗೆ ಇರಿಸಿ. ಹರಿಯಬೇಡಿ ಅಥವಾ ಕಡ್ಡಾಯವಾಗಿ ಕತ್ತರಿಸಬೇಡಿ.",
        "hi-IN": "मैं सहाय हूँ: जहर फैलने से रोकने के लिए मरीज को हिलने न दें। घाव को दिल के स्तर से नीचे रखें। चीरा न लगाएं। तुरंत अस्पताल पहुंचें।"
    },
    "choking": {
        "label": "Choking", "icon": "🛑",
        "en-IN": "Sahaya here: Lean the person forward and give 5 sharp back blows between shoulder blades. If ineffective, perform 5 abdominal thrusts (Heimlich maneuver).",
        "kn-IN": "ನಾನು ಸಹಾಯ: ವ್ಯಕ್ತಿಯನ್ನು ಮುಂದಕ್ಕೆ ಬಾಗಿಸಿ ಬೆನ್ನಿನ ಮಧ್ಯೆ 5 ಬಾರಿ ಜೋರಾಗಿ ತಟ್ಟಿ. ಪ್ರಯೋಜನವಾಗದಿದ್ದರೆ 5 ಬಾರಿ ಹೊಟ್ಟೆಯ ಮೇಲೆ ಒತ್ತಿ (ಹೀಮ್ಲಿಕ್ ವಿಧಾನ).",
        "hi-IN": "मी सहाय हूँ: व्यक्ति को आगे झुकाकर पीठ पर 5 बार जोर से मारें। आराम न मिलने पर पेट पर 5 बार दबाव (हेमलिच) डालें।"
    },
    "fall": {
        "label": "Fracture / Severe Fall", "icon": "🤕",
        "en-IN": "Sahaya here: Do not attempt to realign broken bones. Immobilize the injured area using a splint or folded cloth. If neck or spine injury is suspected, do not move them.",
        "kn-IN": "ನಾನು ಸಹಾಯ: ಮುರಿದ ಮೂಳೆಗಳನ್ನು ಸರಿಪಡಿಸಲು ಪ್ರಯತ್ನಿಸಬೇಡಿ. ಬಟ್ಟೆ ಅಥವಾ ಹಲಗೆಯಿಂದ ಆಸರೆ ನೀಡಿ ಕದಲದಂತೆ ಮಾಡಿ. ಕುತ್ತಿಗೆ ಗಾಯವಿದ್ದರೆ ವ್ಯಕ್ತಿಯನ್ನು ಎತ್ತಬೇಡಿ.",
        "hi-IN": "मैं सहाय हूँ: टूटी हड्डियों को खुद ठीक करने की कोशिश न करें। पट्टी या कपड़े से अंग को स्थिर करें। गर्दन में चोट हो तो मरीज को न हिलाएं।"
    },
    "heatstroke": {
        "label": "Heatstroke", "icon": "🥵",
        "en-IN": "Sahaya here: Move victim to a cool, shaded place. Loosen clothing, sponge skin with cool water, and fan vigorously. Offer sips of water if fully conscious.",
        "kn-IN": "ನಾನು ಸಹಾಯ: ವ್ಯಕ್ತಿಯನ್ನು ತಂಪಾದ ನೆರಳಿಗೆ ತನ್ನಿ. ಬಟ್ಟೆ ಸಡಿಲಗೊಳಿಸಿ, ಮೈಯನ್ನು ತಣ್ಣೀರಿನಿಂದ ಒರೆಸಿ ಗಾಳಿ ಹಾಕಿ. ಪ್ರಜ್ಞೆ ಇದ್ದರೆ ನೀರು ಕುಡಿಸಿ.",
        "hi-IN": "मैं सहाय हूँ: मरीज को ठंडी छांव में ले जाएं। कपड़े ढीले करें, ठंडे पानी से शरीर पोंछें और पंखा करें। होश में होने पर पानी पिलाएं।"
    },
    
    # MINOR / DAILY INJURIES
    "cut": {
        "label": "Heavy Bleeding", "icon": "✂️",
        "en-IN": "Sahaya here: Apply direct, continuous pressure on the wound using a clean cloth or sterile gauze. Elevate the bleeding limb above the heart level until bleeding stops.",
        "kn-IN": "ನಾನು ಸಹಾಯ: ಸ್ವಚ್ಛವಾದ ಬಟ್ಟೆಯಿಂದ ಗಾಯದ ಮೇಲೆ ನೇರವಾಗಿ ಒತ್ತಿ ಹಿಡಿಯಿರಿ. ರಕ್ತ ನಿಲ್ಲುವವರೆಗೆ ಗಾಯಗೊಂಡ ಭಾಗವನ್ನು ಮೇಲಕ್ಕೆತ್ತಿ ಹಿಡಿದುಕೊಳ್ಳಿ.",
        "hi-IN": "मैं सहाय हूँ: साफ कपड़े से घाव को लगातार जोर से दबाकर रखें। खून बहना बंद होने तक चोट वाले अंग को दिल के स्तर से ऊपर उठाएं।"
    },
    "nosebleed": {
        "label": "Nosebleed", "icon": "🩸",
        "en-IN": "Sahaya here: Sit upright and lean slightly forward. Pinch the soft lower part of the nose firmly against the face for 10 continuous minutes. Breathe through your mouth.",
        "kn-IN": "ನಾನು ಸಹಾಯ: ನೆಟ್ಟಗೆ ಕುಳಿತು ಸ್ವಲ್ಪ ಮುಂದಕ್ಕೆ ಬಾಗಿ. ಮೂಗಿನ ಮೆದು ಭಾಗವನ್ನು 10 ನಿಮಿಷಗಳ ಕಾಲ ಬಿಗಿಯಾಗಿ ಒತ್ತಿ ಹಿಡಿಯಿರಿ. ಬಾಯಿಯ ಮೂಲಕ ಉಸಿರಾಡಿ.",
        "hi-IN": "मैं सहाय हूँ: सीधे बैठें और थोड़ा आगे झुकें। नाक के नरम हिस्से को लगातार 10 मिनट तक दबाकर रखें। मुंह से सांस लें।"
    },
    "sprain": {
        "label": "Sprain / Strain", "icon": "🦴",
        "en-IN": "Sahaya here: Follow R.I.C.E. protocol—Rest the injured limb, apply an ice pack wrapped in a cloth for 15 minutes, apply a supportive bandage, and elevate the area.",
        "kn-IN": "ನಾನು ಸಹಾಯ: R.I.C.E. ನಿಯಮ ಪಾಲಿಸಿ—ಗಾಯಕ್ಕೆ ವಿಶ್ರಾಂತಿ ನೀಡಿ, 15 ನಿಮಿಷ ಮಂಜುಗಡ್ಡೆ ಇಡಿ, ಬ್ಯಾಂಡೇಜ್ ಕಟ್ಟಿ, ಗಾಯಗೊಂಡ ಭಾಗವನ್ನು ಎತ್ತರದಲ್ಲಿಡಿ.",
        "hi-IN": "मैं सहाय हूँ: R.I.C.E. नियम अपनाएं—आराम दें, 15 मिनट कपड़े में लपेटी बर्फ लगाएं, पट्टी बांधें और अंग को ऊंचाई पर रखें।"
    }
}

# --------------------------------------------------
# SESSION STATE MANAGEMENT
# --------------------------------------------------
if 'selected_emergency' not in st.session_state:
    st.session_state.selected_emergency = None
if 'custom_input' not in st.session_state:
    st.session_state.custom_input = ""

def set_emergency(key):
    st.session_state.selected_emergency = key

# --------------------------------------------------
# INTERFACE LAYOUT: PROFESSIONAL BUTTON GRID
# --------------------------------------------------
selected_lang = st.selectbox(
    "🌐 Select Language / ಭಾಷೆಯನ್ನು ಆಯ್ಕೆಮಾಡಿ",
    options=list(LANGUAGE_MAP.keys()),
    format_func=lambda x: LANGUAGE_MAP[x],
)

enable_voice = st.checkbox("🔊 Enable spoken audio response", value=True)

st.markdown("<div class='custom-divider'></div>", unsafe_allow_html=True)
st.markdown("<h3 class='emergency-title'>🚨 Emergency Menu</h3>", unsafe_allow_html=True)

# 3-Column Responsive Grid Layout
cols = st.columns(3)
keys = list(EMERGENCY_DATA.keys())

for idx, key in enumerate(keys):
    col = cols[idx % 3]
    data = EMERGENCY_DATA[key]
    button_label = f"{data['icon']}\n{data['label']}"
    
    col.button(
        button_label,
        key=f"btn_{key}",
        on_click=set_emergency,
        args=(key,)
    )

st.markdown("<div class='custom-divider'></div>", unsafe_allow_html=True)

# --------------------------------------------------
# VOICE INPUT MODULE (Fallback / Alternate Input)
# --------------------------------------------------
st.markdown("### 🎙️ Or Speak Your Emergency")
st.write("Hold the button, describe your situation clearly, and release:")

audio = mic_recorder(
    start_prompt="🎤 Hold to Record Emergency",
    stop_prompt="⏹️ Processing Audio...",
    key="app_microphone",
)

if audio and audio.get("bytes"):
    with st.spinner("Analyzing emergency audio..."):
        transcript = transcribe_audio(audio["bytes"], selected_lang)
        st.session_state.custom_input = transcript
        # Automatically update selection based on speech
        st.session_state.selected_emergency = classify_emergency(transcript)

# --------------------------------------------------
# DYNAMIC GUIDANCE DISPLAY ENGINE
# --------------------------------------------------
if st.session_state.selected_emergency:
    st.markdown("<div class='custom-divider'></div>", unsafe_allow_html=True)
    sc_key = st.session_state.selected_emergency
    scenario_info = EMERGENCY_DATA.get(sc_key, EMERGENCY_DATA["earthquake"])
    
    st.subheader(f"📋 Action Plan: {scenario_info['label']}")
    
    # Retrieve localized guidance
    guidance_text = scenario_info.get(selected_lang, scenario_info["en-IN"])
    
    # High-visibility output box
    st.error(guidance_text)
    
    if enable_voice:
        with st.spinner("Synthesizing audio instructions..."):
            audio_out = speak_text(guidance_text, selected_lang)
            if audio_out:
                st.audio(audio_out, format="audio/wav")

# --------------------------------------------------
# CORE LOGIC & BACKEND SERVICES
# --------------------------------------------------
def classify_emergency(text: str) -> str:
    """Keyword intent matching engine across multiple languages."""
    query = text.lower()
    keywords = {
        "earthquake": ["earthquake", "quake", "tremor", "ಭೂಕಂಪ", "ಭೂಮಿ ಕಂಪಿಸಿದ", "भूकंप", "झटका"],
        "heart_attack": ["heart attack", "chest pain", "cardiac", "ಎದೆ ನೋವು", "ಹೃದಯಾಘಾತ", "हार्ट अटैक", "सीने में दर्द"],
        "accident": ["accident", "collision", "crash", "hit", "ಅಪಘಾತ", "ಡಿಕ್ಕಿ", "ದುರ್ಘಟನೆ", "एक्सीडेंट", "दुर्घटना", "टक्कर"],
        "electric_shock": ["shock", "current", "electrocution", "ವಿದ್ಯುತ್", "ಕರೆಂಟ್", "बिजली", "करंट"],
        "stroke": ["stroke", "paralysis", "face drooping", "ಪಾರ್ಶ್ವವಾಯು", "ಲಕ್ವಾ", "लकवा", "स्ट्रोक"],
        "burn": ["burn", "fire", "scald", "acid", "ಸುಟ್ಟ", "ಸುಟ್ಟಿದೆ", "ಬೆಂಕಿ", "जल", "आग", "छाले"],
        "snake": ["snake", "bite", "venom", "ಹಾವು", "ಕಚ್ಚಿದೆ", "ವಿಷ", "ಸಾಪ್", "सांप", "काट", "डस"],
        "choking": ["chok", "throat", "swallow", "breath", "ಉಸಿರುಗಟ್ಟ", "ಗಂಟಲು", "दम", "सांस रुक"],
        "fall": ["fall", "fracture", "fell", "floor", "ಬಿದ್ದ", "ಮೂಳೆ ಮುರಿತ", "ಮಹಡಿ", "गिर", "हड्डी", "मंजिल"],
        "heatstroke": ["heat stroke", "sunstroke", "dehydration", "ಬಿಸಿಲು", "ತಾಪ", "लू", "गर्मी"],
        "cut": ["cut", "bleeding", "wound", "blood", "ರಕ್ತ", "ಗಾಯ", "ಕಟ್", "खून", "घाव", "कट"],
        "nosebleed": ["nose bleed", "epistaxis", "ಮೂಗಿನಲ್ಲಿ ರಕ್ತ", "नाक से खून", "नकसीर"],
        "sprain": ["sprain", "twisted", "swelling", "ಉಳುಕು", "ಊತ", "मोच", "सूजन"],
    }
    for category, terms in keywords.items():
        if any(term in query for term in terms):
            return category
    return "earthquake" # Default fallback

def transcribe_audio(audio_bytes: bytes, lang: str) -> str:
    """Send audio bytes to Gnani.ai ASR service."""
    if not GNANI_TOKEN or not GNANI_ACCESS_KEY:
        return "Simulated speech detected. (Add API keys to enable live ASR)."
    headers = {"token": GNANI_TOKEN, "accesskey": GNANI_ACCESS_KEY, "lang": lang}
    files = {"audio": ("audio.wav", io.BytesIO(audio_bytes), "audio/wav")}
    try:
        response = requests.post(STT_API_URL, headers=headers, files=files, timeout=15)
        if response.status_code == 200:
            data = response.json()
            return data.get("transcript", data.get("result", "Emergency detected"))
    except Exception:
        pass
    return "Emergency detected"

def speak_text(text: str, lang: str):
    """Convert text instructions to speech using Gnani.ai TTS service."""
    if not GNANI_TOKEN or not GNANI_ACCESS_KEY:
        return None
    headers = {"token": GNANI_TOKEN, "accesskey": GNANI_ACCESS_KEY, "lang": lang, "Content-Type": "application/json"}
    payload = {
        "input": {"text": text},
        "voice": {"languageCode": lang, "ssmlGender": "FEMALE"},
        "audioConfig": {"audioEncoding": "wav", "sampleRate": 16000},
    }
    try:
        response = requests.post(TTS_API_URL, headers=headers, json=payload, timeout=15)
        if response.status_code == 200 and response.content:
            return response.content
    except Exception:
        pass
    return None
