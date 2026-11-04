
import io
import os
import requests
import streamlit as st
from streamlit_mic_recorder import audio_recorder

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Gnani AI Emergency Voice Assistant",
    page_icon="🆘",
    layout="centered"
)

st.title("🆘 Multilingual Emergency Voice Assistant")
st.write(
    "An AI-powered voice assistant for emergency support "
    "in Indian languages."
)

st.warning(
    "This is an assistance tool, not an emergency dispatch service. "
    "It does not automatically contact police, ambulance, or authorities. "
    "In India, call 112 for immediate emergency assistance."
)

# --------------------------------------------------
# GNANI.AI CONFIGURATION
# --------------------------------------------------

def get_secret(name):
    """Read credentials from Streamlit secrets or environment variables."""
    try:
        value = st.secrets.get(name)
        if value:
            return value
    except Exception:
        pass

    return os.getenv(name)


GNANI_TOKEN = get_secret("GNANI_TOKEN")
GNANI_ACCESS_KEY = get_secret("GNANI_ACCESS_KEY")

STT_API_URL = "https://asr.gnani.ai/recognize"
TTS_API_URL = "https://tts.gnani.ai/synthesize"
TRANSLATE_API_URL = "https://translate.gnani.ai/translate"

LANGUAGES = {
    "kn": "Kannada",
    "hi": "Hindi",
    "ta": "Tamil",
    "te": "Telugu",
    "ml": "Malayalam",
    "mr": "Marathi",
    "gu": "Gujarati",
    "bn": "Bengali",
    "pa": "Punjabi",
    "or": "Odia",
    "en": "English"
}


def check_credentials():
    if not GNANI_TOKEN or not GNANI_ACCESS_KEY:
        st.error(
            "Gnani.ai credentials are missing. "
            "Please configure GNANI_TOKEN and GNANI_ACCESS_KEY "
            "in Streamlit secrets."
        )
        return False

    return True


def gnani_headers(json_request=False):
    headers = {
        "token": GNANI_TOKEN,
        "accessKey": GNANI_ACCESS_KEY
    }

    if json_request:
        headers["Content-Type"] = "application/json"

    return headers


# --------------------------------------------------
# SPEECH TO TEXT
# --------------------------------------------------

def gnani_stt(audio_bytes, lang_code):
    try:
        files = {
            "audio": ("input.wav", audio_bytes, "audio/wav")
        }

        data = {
            "lang": lang_code,
            "audio_format": "wav"
        }

        response = requests.post(
            STT_API_URL,
            headers=gnani_headers(),
            data=data,
            files=files,
            timeout=45
        )

        response.raise_for_status()
        result = response.json()

        return result.get("transcript", "").strip()

    except requests.RequestException as error:
        st.error(f"Speech recognition request failed: {error}")
    except (ValueError, KeyError):
        st.error("Could not read the speech recognition response.")

    return ""


# --------------------------------------------------
# TRANSLATION
# --------------------------------------------------

def gnani_translate(text, source_lang, target_lang):
    if not text or source_lang == target_lang:
        return text

    try:
        payload = {
            "text": text,
            "source_lang": source_lang,
            "target_lang": target_lang
        }

        response = requests.post(
            TRANSLATE_API_URL,
            headers=gnani_headers(json_request=True),
            json=payload,
            timeout=30
        )

        response.raise_for_status()
        result = response.json()

        return result.get("translated_text", text)

    except requests.RequestException as error:
        st.warning(f"Translation request failed: {error}")
    except (ValueError, KeyError):
        st.warning("Could not read the translation response.")

    return text


# --------------------------------------------------
# TEXT TO SPEECH
# --------------------------------------------------

def gnani_tts(text, lang_code):
    if not text:
        return None

    try:
        payload = {
            "text": text,
            "lang": lang_code,
            "voice": "female"
        }

        response = requests.post(
            TTS_API_URL,
            headers=gnani_headers(json_request=True),
            json=payload,
            timeout=30
        )

        response.raise_for_status()

        # The original code expects a WAV audio response.
        # Validate that the returned content is a WAV file.
        audio_bytes = response.content

        if audio_bytes[:4] != b"RIFF":
            st.warning(
                "Gnani.ai returned a response that does not appear "
                "to be a WAV audio file. Check your TTS API format."
            )
            return None

        return audio_bytes

    except requests.RequestException as error:
        st.warning(f"Text-to-speech request failed: {error}")

    return None


# --------------------------------------------------
# EMERGENCY AND FIRST-AID KEYWORDS
# --------------------------------------------------

FIRST_AID_GUIDANCE = {
    "burn": {
        "keywords": [
            "burn", "fire", "oil burn", "beppu", "suttu"
        ],
        "guidance": (
            "Cool the burn under cool running water for 20 minutes. "
            "Remove jewellery or clothing near the burn if it is not "
            "stuck to the skin. Do not apply ice, toothpaste, or butter. "
            "Seek urgent medical help for serious burns."
        )
    },

    "snakebite": {
        "keywords": [
            "snake", "snakebite", "haavu", "kaatu"
        ],
        "guidance": (
            "Seek emergency medical care immediately. Keep the person "
            "calm and still. Keep the bitten limb as still as possible. "
            "Do not cut or suck the wound, and do not apply a tight "
            "tourniquet."
        )
    },

    "fall": {
        "keywords": [
            "broken bone", "fracture", "muri",
            "hard fall", "fall"
        ],
        "guidance": (
            "Seek medical help. Avoid moving the injured person if a "
            "head, neck, back, or serious bone injury is suspected, "
            "unless they are in immediate danger. Apply firm direct "
            "pressure to severe external bleeding if safe to do so."
        )
    },

    "choking": {
        "keywords": [
            "choking", "cannot breathe", "throat",
            "swallow", "usiru"
        ],
        "guidance": (
            "If the person cannot breathe, speak, or cough, this is "
            "an emergency. Call emergency services immediately and "
            "follow the instructions of the emergency call handler. "
            "Do not give food or water."
        )
    },

    "assault": {
        "keywords": [
            "attack", "hit", "threat",
            "assault", "maramari"
        ],
        "guidance": (
            "Move to a safer place if possible. Avoid confronting "
            "the attacker. Contact emergency services or someone "
            "you trust for immediate help."
        )
    }
}


DISTRESS_KEYWORDS = [
    "help",
    "kaapaadi",
    "bachao",
    "emergency",
    "danger",
    "sahaya",
    "save me",
    "accident",
    "police",
    "kapadi"
]


def match_first_aid(text):
    lowered = text.lower()

    for emergency_type, item in FIRST_AID_GUIDANCE.items():
        for keyword in item["keywords"]:
            if keyword in lowered:
                return emergency_type, item["guidance"]

    return None, None


def detect_distress(text):
    lowered = text.lower()

    return any(
        keyword in lowered
        for keyword in DISTRESS_KEYWORDS
    )


# --------------------------------------------------
# EMERGENCY RESPONSE PROCESSING
# --------------------------------------------------

def process_emergency_flow(transcript, lang_code):

    st.subheader("📝 Recognized Speech")
    st.write(transcript)

    emergency_type, guidance = match_first_aid(transcript)
    distress_detected = detect_distress(transcript)

    if emergency_type:
        st.error(f"Possible emergency detected: {emergency_type}")

        response_text = guidance

    elif distress_detected:
        st.error("⚠️ Possible distress signal detected.")

        response_text = (
            "You may be in an emergency. Move to a safe place "
            "if possible and call emergency services. "
            "In India, call 112."
        )

    else:
        response_text = (
            "I could not identify a specific emergency. "
            "Please describe the situation clearly. "
            "If you are in immediate danger in India, call 112."
        )

    # Translate response into the selected language.
    if lang_code != "en":
        response_text = gnani_translate(
            response_text,
            source_lang="en",
            target_lang=lang_code
        )

    st.subheader("🤖 Assistant Response")
    st.write(response_text)

    # Generate spoken response.
    with st.spinner("Generating voice response..."):
        audio_response = gnani_tts(
            response_text,
            lang_code
        )

    if audio_response:
        st.subheader("🔊 Voice Response")
        st.audio(audio_response, format="audio/wav")


# --------------------------------------------------
# MAIN APPLICATION
# --------------------------------------------------

st.divider()

st.subheader("🌐 Select Your Language")

selected_language = st.selectbox(
    "Choose your preferred language",
    options=list(LANGUAGES.keys()),
    format_func=lambda code: LANGUAGES[code],
    index=0
)

st.info(
    f"Selected language: {LANGUAGES[selected_language]}"
)

st.subheader("🎙️ Speak to the Assistant")

st.write(
    "Click the microphone button, record your emergency message, "
    "and submit the recording."
)

audio_data = audio_recorder(
    text="Click to record",
    recording_color="#e74c3c",
    neutral_color="#2e86c1",
    icon_name="microphone",
    icon_size="2x"
)

if audio_data:
    st.audio(audio_data, format="audio/wav")

    if st.button("Process Emergency Message", type="primary"):

        if not check_credentials():
            st.stop()

        with st.spinner("Recognizing your speech..."):

            transcript = gnani_stt(
                audio_data,
                selected_language
            )

        if transcript:
            process_emergency_flow(
                transcript,
                selected_language
            )
        else:
            st.error(
                "No speech was recognized. Please try recording again."
            )

st.divider()

st.caption(
    "Gnani AI Multilingual Emergency Voice Assistant | "
    "Prototype project. Not a replacement for emergency services "
    "or professional medical advice."
)
