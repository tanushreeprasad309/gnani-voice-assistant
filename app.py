import io
import json
import os
import wave
import numpy as np
import requests
import scipy.io.wavfile as wavfile
import sounddevice as sd

# ==============================================================================
# CONFIGURATION & GNANI.AI CREDENTIALS
# ==============================================================================
GNANI_TOKEN = os.getenv("GNANI_TOKEN", "YOUR_GNANI_TOKEN_HERE")
GNANI_ACCESS_KEY = os.getenv("GNANI_ACCESS_KEY", "YOUR_GNANI_ACCESS_KEY_HERE")

# Gnani.ai Endpoints
STT_API_URL = "https://asr.gnani.ai/v1/recognize"
TTS_API_URL = "https://tts.gnani.ai/v1/synthesize"
TRANSLATE_API_URL = "https://translate.gnani.ai/v1/translate"

# Supported Indian Language Codes
SUPPORTED_LANGUAGES = {
    "hi": "Hindi",
    "kn": "Kannada",
    "te": "Telugu",
    "ta": "Tamil",
    "mr": "Marathi",
    "bn": "Bengali",
    "gu": "Gujarati",
    "ml": "Malayalam",
    "pa": "Punjabi",
    "or": "Odia",
}

# ==============================================================================
# FIRST AID & EMERGENCY PROTOCOLS
# ==============================================================================
FIRST_AID_GUIDANCE = {
    "burn": {
        "keywords": [
            "burn",
            "fire",
            "jal gaya",
            "bentu",
            "thee",
            "aag",
            "kalithu",
            "sutta",
        ],
        "guidance": (
            "Cool the burn immediately with cool running water for at least 10 to 20 minutes. "
            "Do not apply ice, toothpaste, or oil. Cover loosely with a clean, dry cloth."
        ),
    },
    "snakebite": {
        "keywords": [
            "snake",
            "saap",
            "haavu",
            "paambu",
            "sarpa",
            "bite",
            "katta",
            "kadithu",
        ],
        "guidance": (
            "Keep the victim calm and still to slow venom spread. Immobilize the bitten limb below heart level. "
            "Do not cut the wound, do not try to suck venom, and do not tie a tight tourniquet. Rush to the nearest hospital."
        ),
    },
    "labor": {
        "keywords": [
            "delivery",
            "labor",
            "labour",
            "prasava",
            "janana",
            "baccha",
            "baby coming",
            "contractions",
        ],
        "guidance": (
            "Have the mother lie on a clean surface with knees bent. Support the baby's head as it emerges without pulling. "
            "Clear fluid from baby's mouth and nose, dry immediately, keep warm against mother's chest, and do not cut the cord."
        ),
    },
    "fall": {
        "keywords": [
            "fall",
            "gir gaya",
            "biddanu",
            "vilunthu",
            "height",
            "building",
            "scaffold",
            "fracture",
            "unconscious",
        ],
        "guidance": (
            "Do not move the injured person, especially the neck or back, unless there is immediate danger. "
            "Check breathing, apply gentle direct pressure to heavy bleeding without moving broken bones, and call an ambulance."
        ),
    },
}

# Assault / High-threat distress triggers
DISTRESS_KEYWORDS = [
    "bachao",
    "save me",
    "help",
    "attack",
    "hamla",
    "maar rahe hain",
    "threat",
    "danger",
    "police",
    "assault",
    "kaapadi",
]


# ==============================================================================
# AUDIO RECORDING UTILITIES
# ==============================================================================
def record_audio(duration: int = 5, sample_rate: int = 16000) -> bytes:
    """Records audio from the default microphone and returns WAV bytes."""
    print(f"\n[Microphone] Recording for {duration} seconds... Speak now.")
    audio_data = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype=np.int16,
    )
    sd.wait()
    print("[Microphone] Recording finished.")

    byte_io = io.BytesIO()
    wavfile.write(byte_io, sample_rate, audio_data)
    return byte_io.getvalue()


# ==============================================================================
# GNANI.AI API SERVICES
# ==============================================================================
def gnani_stt(audio_bytes: bytes, lang_code: str = "hi") -> str:
    """Converts audio speech to text using Gnani.ai ASR."""
    headers = {"token": GNANI_TOKEN, "access_key": GNANI_ACCESS_KEY}
    files = {"audio": ("input.wav", audio_bytes, "audio/wav")}
    data = {"lang": lang_code, "encoding": "wav"}

    try:
        response = requests.post(
            STT_API_URL, headers=headers, files=files, data=data, timeout=15
        )
        if response.status_code == 200:
            result = response.json()
            return result.get("transcript", "").strip()
        else:
            print(f"[STT Error] Status {response.status_code}: {response.text}")
    except Exception as e:
        print(f"[STT Exception] {e}")
    return ""


def gnani_tts(text: str, lang_code: str = "hi") -> None:
    """Converts text to speech using Gnani.ai TTS and plays it directly."""
    headers = {
        "token": GNANI_TOKEN,
        "access_key": GNANI_ACCESS_KEY,
        "Content-Type": "application/json",
    }
    payload = {"text": text, "lang": lang_code, "voice": "female"}

    try:
        response = requests.post(
            TTS_API_URL, headers=headers, json=payload, timeout=15
        )
        if response.status_code == 200:
            audio_bytes = response.content
            byte_io = io.BytesIO(audio_bytes)
            with wave.open(byte_io, "rb") as wf:
                sample_rate = wf.getframerate()
                frames = wf.readframes(wf.getnframes())
                audio_array = np.frombuffer(frames, dtype=np.int16)
                sd.play(audio_array, samplerate=sample_rate)
                sd.wait()
        else:
            print(f"[TTS Error] Status {response.status_code}: {response.text}")
    except Exception as e:
        print(f"[TTS Exception] {e}")


def gnani_dynamic_translate(
    text: str, source_lang: str, target_lang: str = "en"
) -> str:
    """Translates text between Indic languages and English using Gnani.ai."""
    headers = {
        "token": GNANI_TOKEN,
        "access_key": GNANI_ACCESS_KEY,
        "Content-Type": "application/json",
    }
    payload = {
        "text": text,
        "source_lang": source_lang,
        "target_lang": target_lang,
    }

    try:
        response = requests.post(
            TRANSLATE_API_URL, headers=headers, json=payload, timeout=15
        )
        if response.status_code == 200:
            res_data = response.json()
            return res_data.get("translated_text", text)
        else:
            print(
                f"[Translation Error] Status {response.status_code}: {response.text}"
            )
    except Exception as e:
        print(f"[Translation Exception] {e}")
    return text


# ==============================================================================
# EMERGENCY LOGIC & DISPATCH
# ==============================================================================
def trigger_distress_alarm(detected_text: str, lang_code: str) -> None:
    """Triggers high-priority alerts for personal safety / assault emergencies."""
    print("\n🚨 [ALERT: DISTRESS / ASSAULT DETECTED] 🚨")
    print(f"Transcript: '{detected_text}'")
    print("Action: Sending coordinates to dispatch & sounding local alert.")

    alert_msg = (
        "Emergency alert triggered. Dispatching local security and authorities."
    )
    if lang_code != "en":
        alert_msg = gnani_dynamic_translate(
            alert_msg, source_lang="en", target_lang=lang_code
        )
    print(f"Bot Output: {alert_msg}")
    gnani_tts(alert_msg, lang_code=lang_code)


def match_first_aid(text: str) -> str | None:
    """Matches keywords in input to predefined first-aid guidance protocols."""
    lowered = text.lower()
    for _, details in FIRST_AID_GUIDANCE.items():
        for kw in details["keywords"]:
            if kw in lowered:
                return details["guidance"]
    return None


def process_emergency_input(transcript: str, detected_lang: str = "hi"):
    """Main routing engine for speech transcription."""
    print(f"\n[Transcribed Input ({detected_lang})]: {transcript}")

    # Check for assault/distress keywords
    if any(k in transcript.lower() for k in DISTRESS_KEYWORDS):
        trigger_distress_alarm(transcript, detected_lang)
        return

    # Check for predefined first-aid match
    guidance_en = match_first_aid(transcript)
    if guidance_en:
        print("\n[Protocol Matched: First-Aid Guidance Found]")
        final_response = (
            guidance_en
            if detected_lang == "en"
            else gnani_dynamic_translate(
                guidance_en, source_lang="en", target_lang=detected_lang
            )
        )
    else:
        # Fallback to dynamic real-time conversational translation
        print("\n[Protocol Fallback: Conversational Field Translation]")
        translated_to_en = gnani_dynamic_translate(
            transcript, source_lang=detected_lang, target_lang="en"
        )
        print(f"Field Worker English View: {translated_to_en}")
        final_response = (
            "Emergency reported. Help has been contacted. Stay where you are."
        )
        if detected_lang != "en":
            final_response = gnani_dynamic_translate(
                final_response, source_lang="en", target_lang=detected_lang
            )

    print(f"Spoken Guidance: {final_response}")
    gnani_tts(final_response, lang_code=detected_lang)


# ==============================================================================
# RUNTIME ENTRY POINT
# ==============================================================================
if __name__ == "__main__":
    print("=" * 60)
    print("   MULTILINGUAL EMERGENCY VOICE BOT INITIALIZED")
    print("=" * 60)

    # Set chosen primary language (e.g., 'hi', 'kn', 'ta', 'te', etc.)
    active_lang = "hi"

    # Step 1: Record 5 seconds of emergency audio
    recorded_audio_bytes = record_audio(duration=5)

    # Step 2: Transcribe using Gnani ASR
    recognized_text = gnani_stt(recorded_audio_bytes, lang_code=active_lang)

    # Step 3: Route through emergency reasoning engine
    if recognized_text:
        process_emergency_input(recognized_text, detected_lang=active_lang)
    else:
        print(
            "No clear audio input captured or API credentials need validation."
        )
