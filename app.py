import io
import os
import requests
import streamlit as st
from streamlit_mic_recorder import mic_recorder

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------
st.set_page_config(
    page_title="Sahaya - Multilingual Emergency Voice Assistant",
    page_icon="🆘",
    layout="centered",
)

st.title("🆘 Sahaya: Emergency Voice Assistant")
st.write(
    "Namaste! I am **Sahaya**, your AI-powered multilingual voice assistant for emergency and first-aid support across India."
)

st.warning(
    "⚠️ **Disclaimer**: Sahaya provides immediate first-aid instructions and guidance, but is not an emergency dispatch system. "
    "Always dial **112** (National Emergency Helpline) immediately for police, ambulance, or fire services in India."
)

# --------------------------------------------------
# GNANI.AI CREDENTIALS & ENDPOINTS
# --------------------------------------------------
def get_secret(name):
    """Safely fetch credentials from Streamlit Secrets or environment variables."""
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

# Supported Indian languages
LANGUAGE_MAP = {
    "kn-IN": "ಕನ್ನಡ (Kannada)",
    "hi-IN": "हिन्दी (Hindi)",
    "en-IN": "English",
    "ta-IN": "தமிழ் (Tamil)",
    "te-IN": "తెలుగు (Telugu)",
    "ml-IN": "മലയാളം (Malayalam)",
    "mr-IN": "मराठी (Marathi)",
    "bn-IN": "বাংলা (Bengali)",
    "gu-IN": "ગુજરાતી (Gujarati)",
    "pa-IN": "ਪੰਜਾਬੀ (Punjabi)",
    "or-IN": "ଓଡ଼ಿଆ (Odia)",
}

# --------------------------------------------------
# COMPREHENSIVE EMERGENCY KNOWLEDGE BASE
# (Major & Minor Emergencies across India)
# --------------------------------------------------
EMERGENCY_KNOWLEDGE_BASE = {
    "earthquake": {
        "en-IN": "Sahaya here: DROP, COVER, and HOLD ON. Get under a sturdy table, protect your head, and stay away from windows and power lines. Do not use elevators. Dial 112 once the shaking stops.",
        "kn-IN": "ನಾನು ಸಹಾಯ: ಭೂಕಂಪವಾದಾಗ ತಕ್ಷಣ ನೆಲಕ್ಕೆ ಬಗ್ಗಿ, ಗಟ್ಟಿಯಾದ ಮೇಜಿನ ಕೆಳಗೆ ಆಶ್ರಯ ಪಡೆಯಿರಿ (Drop, Cover, Hold On). ಕಿಟಕಿಗಳು ಮತ್ತು ವಿದ್ಯುತ್ ಕಂಬಗಳಿಂದ ದೂರವಿರಿ. ಲಿಫ್ಟ್ ಬಳಸಬೇಡಿ. 112 ಗೆ ಕರೆ ಮಾಡಿ.",
        "hi-IN": "मैं सहाय हूँ: भूकंप के दौरान तुरंत नीचे झुकें, मजबूत मेज के नीचे सिर ढकें (Drop, Cover, Hold On)। खिड़कियों और बिजली के तारों से दूर रहें। लिफ्ट का उपयोग न करें। तुरंत 112 पर कॉल करें।",
    },
    "accident": {
        "en-IN": "Sahaya here: Ensure your immediate safety before approaching the vehicle. Do not move an unconscious victim unless there is fire danger. Call 112 immediately and check breathing.",
        "kn-IN": "ನಾನು ಸಹಾಯ: ಮೊದಲು ನಿಮ್ಮ ಸುರಕ್ಷತೆಯನ್ನು ಖಚಿತಪಡಿಸಿಕೊಳ್ಳಿ. ಬೆಂಕಿಯ ಅಪಾಯವಿಲ್ಲದಿದ್ದರೆ ಗಾಯಾಳುವನ್ನು ಹೆಚ್ಚು ಚಲಿಸಬೇಡಿ. ತಕ್ಷಣ 112 ಗೆ ಕರೆ ಮಾಡಿ ಆಂಬ್ಯುಲೆನ್ಸ್ ಕರೆಯಿರಿ.",
        "hi-IN": "मैं सहाय हूँ: पहले अपनी सुरक्षा देखें। अगर आग का खतरा न हो तो घायल व्यक्ति को हिलाएं नहीं। तुरंत 112 डायल करके एम्बुलेंस बुलाएं और सांस की जांच करें।",
    },
    "heart_attack": {
        "en-IN": "Sahaya here: Have the patient sit comfortably with back supported. Loosen tight clothing. If not allergic, give one 300mg soluble Aspirin. Call 112 immediately for an ambulance.",
        "kn-IN": "ನಾನು ಸಹಾಯ: ರೋಗಿಯನ್ನು ಆರಾಮವಾಗಿ ಕೂರಿಸಿ, ಬೆನ್ನಿಗೆ ಆಧಾರ ನೀಡಿ. ಬಿಗಿಯಾದ ಬಟ್ಟೆಯನ್ನು ಸಡಿಲಗೊಳಿಸಿ. ಅಲರ್ಜಿ ಇಲ್ಲದಿದ್ದರೆ ಆಸ್ಪಿರಿನ್ ಮಾತ್ರೆ ನೀಡಿ. ತಕ್ಷಣ 112 ಗೆ ಕರೆ ಮಾಡಿ ಆಸ್ಪತ್ರೆಗೆ ಸಾಗಿಸಿ.",
        "hi-IN": "मैं सहाय हूँ: मरीज को आराम से बैठाएं और कपड़े ढीले करें। अगर एलर्जी न हो तो एक एस्पिरिन (Aspirin) चबाने को दें। बिना देर किए तुरंत 112 डायल करें।",
    },
    "stroke": {
        "en-IN": "Sahaya here: Use FAST (Face drooping, Arm weakness, Speech slurred, Time to call 112). Keep the patient still, do not give anything to eat or drink, and rush to the hospital immediately.",
        "kn-IN": "ನಾನು ಸಹಾಯ: ಮುಖ ವಾಲಿದೆಯೇ, ಕೈಯಲ್ಲಿ ಶಕ್ತಿ ಕಡಿಮೆಯಾಗಿದೆಯೇ, ಮಾತು ತೊದಲುತ್ತಿದೆಯೇ ಗಮನಿಸಿ (FAST). ಏನನ್ನೂ ತಿನ್ನಲು ಅಥವಾ ಕುಡಿಯಲು ನೀಡಬೇಡಿ. ತಕ್ಷಣ 112 ಗೆ ಕರೆ ಮಾಡಿ ಆಸ್ಪತ್ರೆಗೆ ಕರೆದೊಯ್ಯಿರಿ.",
        "hi-IN": "मैं सहाय हूँ: FAST नियम याद रखें—चेहरा लटकना, हाथ की कमजोरी, बोलने में परेशानी। मरीज को कुछ भी खाने-पीने न दें और तुरंत 112 पर कॉल करके अस्पताल ले जाएं।",
    },
    "electric_shock": {
        "en-IN": "Sahaya here: DO NOT touch the victim with bare hands. Turn off the main power switch immediately or use a dry wooden stick to separate them from the wire. Dial 112.",
        "kn-IN": "ನಾನು ಸಹಾಯ: ವ್ಯಕ್ತಿಯನ್ನು ಬರಿಗೈಯಿಂದ ಮುಟ್ಟಬೇಡಿ! ತಕ್ಷಣ ಮುಖ್ಯ ವಿದ್ಯುತ್ ಸ್ವಿಚ್ ಆಫ್ ಮಾಡಿ ಅಥವಾ ಒಣ ಮರದ ಕೋಲಿನಿಂದ ತಂತಿಯನ್ನು ಬೇರ್ಪಡಿಸಿ. ನಂತರ 112 ಗೆ ಕರೆ ಮಾಡಿ.",
        "hi-IN": "मैं सहाय हूँ: पीड़ित को नंगे हाथों से न छुएं! तुरंत मेन स्विच बंद करें या सूखी लकड़ी की छड़ी से तार हटाएं। सांस की जांच करें और 112 पर कॉल करें।",
    },
    "snake": {
        "en-IN": "Sahaya here: Keep the victim calm and strictly still. Immobilize the limb and keep it below heart level. Do NOT cut, suck venom, or tie tight tourniquets. Reach a hospital immediately for Anti-Snake Venom.",
        "kn-IN": "ನಾನು ಸಹಾಯ: ವ್ಯಕ್ತಿಯನ್ನು ಚಲಿಸದಂತೆ ಶಾಂತರಾಗಿರಿಸಿ. ಕಚ್ಚಿದ ಭಾಗವನ್ನು ಹೃದಯದ ಮಟ್ಟಕ್ಕಿಂತ ಕೆಳಗೆ ಇರಿಸಿ. ಬ್ಲೇಡ್‌ನಿಂದ ಕೊಯ್ಯಬೇಡಿ, ವಿಷ ಹೀರುವ ಪ್ರಯತ್ನ ಮಾಡಬೇಡಿ. ತಕ್ಷಣ ಆಸ್ಪತ್ರೆಗೆ ಕೊಂಡೊಯ್ದು ASV ಚುಚ್ಚುಮದ್ದು ಕೊಡಿಸಿ.",
        "hi-IN": "मैं सहाय हूँ: मरीज को शांत रखें और बिल्कुल हिलने न दें। काटे गए अंग को दिल के स्तर से नीचे रखें। चीरा या कसकर पट्टी न बांधें। तुरंत नजदीकी अस्पताल ले जाएं।",
    },
    "heatstroke": {
        "en-IN": "Sahaya here: Move the person to a cool, shaded area. Sponge body with cool water and fan continuously. Offer sips of cool water or ORS if fully conscious. Seek medical help.",
        "kn-IN": "ನಾನು ಸಹಾಯ: ವ್ಯಕ್ತಿಯನ್ನು ತಂಪಾದ ನೆರಳಿನ ಜಾಗಕ್ಕೆ ಕರೆದೊಯ್ಯಿರಿ. ದೇಹದ ಮೇಲೆ ತಣ್ಣೀರು ಚಿಮುಕಿಸಿ ಗಾಳಿ ಹಾಕಿ. ಪ್ರಜ್ಞೆ ಇದ್ದರೆ ನೀರು ಅಥವಾ ಓಆರ್‌ಎಸ್ (ORS) ಕುಡಿಸಿ.",
        "hi-IN": "मैं सहाय हूँ: व्यक्ति को तुरंत ठंडी या छांव वाली जगह ले जाएं। शरीर पर ठंडा पानी छिड़कें और पंखा करें। होश में होने पर ओआरएस (ORS) या पानी पिलाएं।",
    },
    "burn": {
        "en-IN": "Sahaya here: Cool the burn under gentle running tap water for 10–20 minutes. Do not apply ice, butter, or toothpaste. Cover loosely with a clean, sterile cloth and see a doctor.",
        "kn-IN": "ನಾನು ಸಹಾಯ: ಸುಟ್ಟ ಜಾಗಕ್ಕೆ 10-20 ನಿಮಿಷಗಳ ಕಾಲ ನಲ್ಲಿಯ ತಣ್ಣೀರು ಸುರಿಯಿರಿ. ಮಂಜುಗಡ್ಡೆ, ಬೆಣ್ಣೆ ಅಥವಾ ಟೂತ್‌ಪೇಸ್ಟ್ ಹಚ್ಚಬೇಡಿ. ಸ್ವಚ್ಛವಾದ ಬಟ್ಟೆಯಿಂದ ಮುಚ್ಚಿ ಆಸ್ಪತ್ರೆಗೆ ತೆರಳಿ.",
        "hi-IN": "मैं सहाय हूँ: जले हिस्से पर 10-20 मिनट तक सामान्य ठंडा पानी डालें। बर्फ, तेल या टूथपेस्ट न लगाएं। साफ कपड़े से ढकें और डॉक्टर को दिखाएं।",
    },
    "choking": {
        "en-IN": "Sahaya here: If the person cannot breathe, give 5 firm blows between the shoulder blades with the heel of your hand, followed by 5 quick abdominal thrusts (Heimlich maneuver).",
        "kn-IN": "ನಾನು ಸಹಾಯ: ಉಸಿರಾಟ ನಿಂತಿದ್ದರೆ, ಬೆನ್ನಿನ ಮಧ್ಯದಲ್ಲಿ ಅಂಗೈಯಿಂದ 5 ಬಾರಿ ಬಲವಾಗಿ ತಟ್ಟಿ. ನಂತರ ಹೊಟ್ಟೆಯ ಮೇಲ್ಭಾಗವನ್ನು ಒಳಕ್ಕೆ ಮತ್ತು ಮೇಲಕ್ಕೆ ಒತ್ತಿ (ಹೀಮ್ಲಿಕ್ ವಿಧಾನ).",
        "hi-IN": "मैं सहाय हूँ: अगर सांस रुक रही हो, तो पीठ पर 5 बार थपथपाएं, फिर पेट के ऊपरी हिस्से पर अंदर और ऊपर की ओर दबाव (हेमलिच तकनीक) डालें। तुरंत 112 डायल करें।",
    },
    "fall": {
        "en-IN": "Sahaya here: Check for consciousness and normal breathing. If you suspect a neck, back, or bone fracture, do not move the person. Keep them warm and call 112.",
        "kn-IN": "ನಾನು ಸಹಾಯ: ಪ್ರಜ್ಞೆ ಮತ್ತು ಉಸಿರಾಟವನ್ನು ಪರೀಕ್ಷಿಸಿ. ಕುತ್ತಿಗೆ ಅಥವಾ ಬೆನ್ನುಮೂಳೆಗೆ ಏಟಾಗಿದ್ದರೆ ವ್ಯಕ್ತಿಯನ್ನು ಅಲುಗಾಡಿಸಬೇಡಿ. ತಕ್ಷಣ 112 ಗೆ ಕರೆ ಮಾಡಿ.",
        "hi-IN": "मैं सहाय हूँ: होश और सांस की जांच करें। गर्दन या रीढ़ की हड्डी में चोट हो तो मरीज को बिल्कुल न हिलाएं। तुरंत 112 पर संपर्क करें।",
    },
    "cut": {
        "en-IN": "Sahaya here: Apply direct, firm pressure on the wound with a clean cloth or bandage to stop bleeding. Elevate the injured area above the heart if possible. Wash gently and bandage.",
        "kn-IN": "ನಾನು ಸಹಾಯ: ರಕ್ತಸ್ರಾವ ನಿಲ್ಲಿಸಲು ಗಾಯದ ಮೇಲೆ ಸ್ವಚ್ಛವಾದ ಬಟ್ಟೆಯಿಂದ ಗಟ್ಟಿಯಾಗಿ ಒತ್ತಿ ಹಿಡಿಯಿರಿ. ಸಾಧ್ಯವಾದರೆ ಗಾಯಗೊಂಡ ಭಾಗವನ್ನು ಮೇಲಕ್ಕೆತ್ತಿ. ರಕ್ತ ನಿಲ್ಲದಿದ್ದರೆ ಆಸ್ಪತ್ರೆಗೆ ತೆರಳಿ.",
        "hi-IN": "मैं सहाय हूँ: खून बहना रोकने के लिए साफ कपड़े से घाव को कसकर दबाएं। चोट वाले हिस्से को दिल के स्तर से ऊपर उठाएं। खून न रुके तो डॉक्टर को दिखाएं।",
    },
    "nosebleed": {
        "en-IN": "Sahaya here: Sit upright and lean forward slightly—do NOT lean back. Pinch the soft part of the nose firmly for 10 minutes and breathe through the mouth.",
        "kn-IN": "ನಾನು ಸಹಾಯ: ನೆಟ್ಟಗೆ ಕುಳಿತು ಸ್ವಲ್ಪ ಮುಂದಕ್ಕೆ ಬಗ್ಗಿ—ತಲೆಯನ್ನು ಹಿಂದಕ್ಕೆ ಬಾಗಿಸಬೇಡಿ. ಮೂಗಿನ ಮೆದುವಾದ ಮುಂಭಾಗವನ್ನು 10 ನಿಮಿಷ ಗಟ್ಟಿಯಾಗಿ ಒತ್ತಿ ಹಿಡಿಯಿರಿ ಮತ್ತು ಬಾಯಿಯಿಂದ ಉಸಿರಾಡಿ.",
        "hi-IN": "मैं सहाय हूँ: सीधे बैठें और आगे की ओर थोड़ा झुकें (सिर पीछे न करें)। नाक के दोनों नथुनों को 10 मिनट तक दबाकर रखें और मुंह से सांस लें।",
    },
    "sprain": {
        "en-IN": "Sahaya here: Follow R.I.C.E. (Rest the limb, Ice wrapped in cloth for 15 minutes, Compress gently with an elastic bandage, Elevate the limb).",
        "kn-IN": "ನಾನು ಸಹಾಯ: ಊತ ಮತ್ತು ನೋವಿಗೆ ವಿಶ್ರಾಂತಿ ನೀಡಿ, ಬಟ್ಟೆಯಲ್ಲಿ ಸುತ್ತಿದ ಮಂಜುಗಡ್ಡೆಯಿಂದ 15 ನಿಮಿಷ ಶಾಖ ಕೊಡಿ, ಕ್ರೇಪ್ ಬ್ಯಾಂಡೇಜ್ ಕಟ್ಟಿ, ಕಾಲನ್ನು ಎತ್ತರದಲ್ಲಿಡಿ.",
        "hi-IN": "मैं सहाय हूँ: R.I.C.E नियम अपनाएं—आराम करें, कपड़े में लपेटकर बर्फ लगाएं, पट्टी बांधें और अंग को ऊंचाई पर रखें।",
    },
    "crime": {
        "en-IN": "Sahaya here: Prioritize your physical safety first. Move to a crowded public area. Dial 112 immediately to report snatching, robbery, or harassment to the police.",
        "kn-IN": "ನಾನು ಸಹಾಯ: ಮೊದಲು ನಿಮ್ಮ ಸುರಕ್ಷತೆಯನ್ನು ಖಚಿತಪಡಿಸಿಕೊಳ್ಳಿ. ಜನರಿರುವ ಸ್ಥಳಕ್ಕೆ ತೆರಳಿ. ಸರಗಳ್ಳತನ ಅಥವಾ ಕಿರುಕುಳದ ವಿರುದ್ಧ ತಕ್ಷಣವೇ 112 ಗೆ ಕರೆ ಮಾಡಿ ಪೊಲೀಸರಿಗೆ ಮಾಹಿತಿ ನೀಡಿ.",
        "hi-IN": "मैं सहाय हूँ: पहले अपनी सुरक्षा सुनिश्चित करें और भीड़ वाली जगह जाएं। छिनैती या चोरी की सूचना देने के लिए तुरंत 112 पर पुलिस को कॉल करें।",
    },
    "default": {
        "en-IN": "I am Sahaya, your emergency assistant. Stay calm. Please tell me your symptoms or situation (e.g., burn, snake bite, fall, accident, bleeding). For danger, call 112.",
        "kn-IN": "ನಾನು ನಿಮ್ಮ ತುರ್ತು ಸಹಾಯಕಿ ಸಹಾಯ. ಶಾಂತರಾಗಿರಿ. ನಿಮ್ಮ ತುರ್ತು ಪರಿಸ್ಥಿತಿ ಏನು (ಉದಾ: ಸುಟ್ಟ ಗಾಯ, ಹಾವು ಕಡಿತ, ಅಪಘಾತ, ರಕ್ತಸ್ರಾವ)? ತಕ್ಷಣದ ಅಪಾಯಕ್ಕೆ 112 ಗೆ ಕರೆ ಮಾಡಿ.",
        "hi-IN": "मैं आपकी आपातकालीन सहायक सहाय हूँ। शांत रहें। कृपया अपनी समस्या बताएं (जैसे: चोट, सांप का काटना, गिरना, दुर्घटना, जलना)। तुरंत सहायता के लिए 112 डायल करें।",
    },
}

# --------------------------------------------------
# INTENT MATCHING ENGINE
# --------------------------------------------------
def classify_emergency(text: str) -> str:
    """Classify user speech into an emergency scenario across multiple languages."""
    query = text.lower()
    
    keywords = {
        "earthquake": ["earthquake", "quake", "tremor", "ಭೂಕಂಪ", "ಭೂಮಿ ಕಂಪಿಸಿದ", "भूकंप", "झटका"],
        "heart_attack": ["heart attack", "chest pain", "cardiac", "ಎದೆ ನೋವು", "ಹೃದಯಾಘಾತ", "हार्ट अटैक", "सीने में दर्द"],
        "stroke": ["stroke", "paralysis", "face drooping", "ಪಾರ್ಶ್ವವಾಯು", "ಲಕ್ವಾ", "लकवा", "स्ट्रोक"],
        "electric_shock": ["shock", "current", "electrocution", "ವಿದ್ಯುತ್", "ಕರೆಂಟ್", "बिजली", "करंट"],
        "accident": ["accident", "collision", "vehicle crash", "hit", "ಅಪಘಾತ", "ಡಿಕ್ಕಿ", "ದುರ್ಘಟನೆ", "एक्सीडेंट", "दुर्घटना", "टक्कर"],
        "burn": ["burn", "fire", "scald", "acid", "ಸುಟ್ಟ", "ಸುಟ್ಟಿದೆ", "ಬೆಂಕಿ", "जल", "आग", "छाले"],
        "snake": ["snake", "bite", "venom", "ಹಾವು", "ಕಚ್ಚಿದೆ", "ವಿಷ", "ಸಾಪ್", "सांप", "काट", "डस"],
        "heatstroke": ["heat stroke", "sunstroke", "dehydration", "ಬಿಸಿಲು", "ತಾಪ", "लू", "गर्मी"],
        "choking": ["chok", "throat", "swallow", "breath", "ಉಸಿರುಗಟ್ಟ", "ಗಂಟಲು", "दम", "सांस रुक"],
        "fall": ["fall", "fracture", "fell", "floor", "ಬಿದ್ದ", "ಮೂಳೆ ಮುರಿತ", "ಮಹಡಿ", "गिर", "हड्डी", "मंजिल"],
        "cut": ["cut", "bleeding", "wound", "blood", "ರಕ್ತ", "ಗಾಯ", "ಕಟ್", "खून", "घाव", "कट"],
        "nosebleed": ["nose bleed", "epistaxis", "ಮೂಗಿನಲ್ಲಿ ರಕ್ತ", "नाक से खून", "नकसीर"],
        "sprain": ["sprain", "twisted", "swelling", "ಉಳುಕು", "ಊತ", "मोच", "सूजन"],
        "crime": ["snatch", "stole", "rob", "theft", "chain", "ಗಳ್ಳತನ", "ಕಸಿದು", "छीना", "चोरी", "लूट"],
    }
    
    for category, terms in keywords.items():
        if any(term in query for term in terms):
            return category
            
    return "default"

def get_sahaya_response(text: str, lang: str) -> str:
    category = classify_emergency(text)
    entry = EMERGENCY_KNOWLEDGE_BASE.get(category, EMERGENCY_KNOWLEDGE_BASE["default"])
    return entry.get(lang, entry.get("en-IN", entry["en-IN"]))

# --------------------------------------------------
# GNANI.AI ASR & TTS SERVICES
# --------------------------------------------------
def transcribe_audio(audio_bytes: bytes, lang: str) -> str:
    if not GNANI_TOKEN or not GNANI_ACCESS_KEY:
        return "Simulated transcription: Emergency detected (Add GNANI_TOKEN and GNANI_ACCESS_KEY in Secrets for live ASR)."
    
    headers = {
        "token": GNANI_TOKEN,
        "accesskey": GNANI_ACCESS_KEY,
        "lang": lang,
    }
    files = {"audio": ("audio.wav", io.BytesIO(audio_bytes), "audio/wav")}
    try:
        response = requests.post(STT_API_URL, headers=headers, files=files, timeout=15)
        if response.status_code == 200:
            data = response.json()
            return data.get("transcript", data.get("result", str(data)))
    except Exception as err:
        return f"Transcription error: {str(err)}"
    return "Could not transcribe audio. Please speak clearly into the mic."

def speak_text(text: str, lang: str):
    if not GNANI_TOKEN or not GNANI_ACCESS_KEY:
        return None
        
    headers = {
        "token": GNANI_TOKEN,
        "accesskey": GNANI_ACCESS_KEY,
        "lang": lang,
        "Content-Type": "application/json",
    }
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

# --------------------------------------------------
# STREAMLIT USER INTERFACE
# --------------------------------------------------
selected_lang = st.selectbox(
    "Choose Language / ಭಾಷೆಯನ್ನು ಆಯ್ಕೆಮಾಡಿ",
    options=list(LANGUAGE_MAP.keys()),
    format_func=lambda x: LANGUAGE_MAP[x],
)

enable_voice = st.checkbox("Enable spoken responses from Sahaya", value=True)

st.markdown("### 🎙️ Speak to Sahaya")
st.write("Click the mic icon, describe your emergency, and click stop:")

audio = mic_recorder(
    start_prompt="🎤 Start recording",
    stop_prompt="⏹️ Stop recording",
    key="sahaya_recorder",
)

if audio and audio.get("bytes"):
    st.audio(audio["bytes"], format="audio/wav")
    
    if st.button("Get Sahaya's Emergency Assistance", type="primary"):
        with st.spinner("Sahaya is analyzing your emergency..."):
            transcript = transcribe_audio(audio["bytes"], selected_lang)
            st.subheader("📝 Recognized Speech:")
            st.info(transcript)
            
            response = get_sahaya_response(transcript, selected_lang)
            st.subheader("🤖 Sahaya's Guidance:")
            st.success(response)
            
            if enable_voice:
                with st.spinner("Sahaya is preparing voice output..."):
                    audio_out = speak_text(response, selected_lang)
                    if audio_out:
                        st.audio(audio_out, format="audio/wav")
