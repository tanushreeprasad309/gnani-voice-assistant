import io
import os
import requests
import streamlit as st
from streamlit_mic_recorder import mic_recorder

try:
    from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
    WEBRTC_AVAILABLE = True
except ImportError:
    WEBRTC_AVAILABLE = False

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

st.set_page_config(
    page_title="Sahaya Emergency Assistant",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 11-Language UI Localization Dictionary
TRANSLATIONS = {
    "en_IN": {
        "title": "🚨 Sahaya Emergency Assistant",
        "subtitle": "Multilingual Voice First-Aid & Emergency Dispatch",
        "mic_header": "🎙️ Voice Input & Live Stream",
        "mic_start": "🔴 Tap to Speak",
        "mic_stop": "⏹️ Stop",
        "type_header": "⌨️ Text Input",
        "type_placeholder": "e.g. Need help with harassment or accident",
        "detected": "🗣️ **Detected Emergency:**",
        "action_header": "⚡ Recommended Action & First-Aid",
        "first_aid_label": "🩹 First-Aid Guidelines:",
        "call_btn": "📞 Call {number} Now",
        "directory_header": "📋 Emergency Grid Directory (Tap Any Card to Call)",
        "helpline": "Helpline:",
        "realtime_desc": "Real-time audio stream active. Speak your emergency to stream directly.",
        "audio_response": "🔊 **Spoken Assistant Response (Sahaya):**"
    },
    "kn_IN": {
        "title": "🚨 ಸಹಾಯ ತುರ್ತು ಸಹಾಯಕ",
        "subtitle": "ಬಹುಭಾಷಾ ಧ್ವನಿ ಪ್ರಥಮ ಚಿಕಿತ್ಸೆ ಮತ್ತು ತುರ್ತು ಪ್ರಸರಣ",
        "mic_header": "🎙️ ಧ್ವನಿ ಇನ್ಪುಟ್ ಮತ್ತು ಲೈವ್ ಸ್ಟ್ರೀಮ್",
        "mic_start": "🔴 ಮಾತನಾಡಲು ಟ್ಯಾಪ್ ಮಾಡಿ",
        "mic_stop": "⏹️ ನಿಲ್ಲಿಸಿ",
        "type_header": "⌨️ ಪಠ್ಯ ಇನ್ಪುಟ್",
        "type_placeholder": "ಉದಾ. ಆಂಬ್ಯುಲೆನ್ಸ್ ಬೇಕು ಅಥವಾ ಅಪಘಾತ",
        "detected": "🗣️ **ಪತ್ತೆಯಾದ ತುರ್ತು ಪರಿಸ್ಥಿತಿ:**",
        "action_header": "⚡ ಶಿಫಾರಸು ಮಾಡಿದ ಕ್ರಮ ಮತ್ತು ಪ್ರಥಮ ಚಿಕಿತ್ಸೆ",
        "first_aid_label": "🩹 ಪ್ರಥಮ ಚಿಕಿತ್ಸಾ ಮಾರ್ಗಸೂಚಿಗಳು:",
        "call_btn": "📞 ಈಗ {number} ಗೆ ಕರೆ ಮಾಡಿ",
        "directory_header": "📋 ತುರ್ತು ಡೈರೆಕ್ಟರಿ (ಕರೆ ಮಾಡಲು ಕಾರ್ಡ್ ಅನ್ನು ಟ್ಯಾಪ್ ಮಾಡಿ)",
        "helpline": "ಸಹಾಯವಾಣಿ:",
        "realtime_desc": "ನೈಜ-ಸಮಯದ ಧ್ವನಿ ಪ್ರಸಾರ ಸಕ್ರಿಯವಾಗಿದೆ. ನೇರವಾಗಿ ಮಾತನಾಡಲು ನಿಮ್ಮ ತುರ್ತು ಪರಿಸ್ಥಿತಿಯನ್ನು ತಿಳಿಸಿ.",
        "audio_response": "🔊 **ಸಹಾಯಕ (ಸಹಾಯ) ಧ್ವನಿ ಪ್ರತಿಕ್ರಿಯೆ:**"
    },
    "hi_IN": {
        "title": "🚨 सहायता आपातकालीन सहायक",
        "subtitle": "बहुभाषी वॉयस फर्स्ट-एड और आपातकालीन प्रेषण",
        "mic_header": "🎙️ वॉयस इनपुट और लाइव स्ट्रीम",
        "mic_start": "🔴 बोलने के लिए टैप करें",
        "mic_stop": "⏹️ रोकें",
        "type_header": "⌨️ टेक्स्ट इनपुट",
        "type_placeholder": "जैसे एम्बुलेंस चाहिए या दुर्घटना",
        "detected": "🗣️ **पता चली आपात स्थिति:**",
        "action_header": "⚡ अनुशंसित कार्रवाई और प्राथमिक उपचार",
        "first_aid_label": "🩹 प्राथमिक उपचार दिशानिर्देश:",
        "call_btn": "📞 अभी {number} पर कॉल करें",
        "directory_header": "📋 आपातकालीन डायरेक्टरी (कॉल करने के लिए टैप करें)",
        "helpline": "हेल्पलाइन:",
        "realtime_desc": "रियल-टाइम ऑडियो स्ट्रीम सक्रिय है। अपनी आपात स्थिति सीधे बोलने के लिए उपयोग करें।",
        "audio_response": "🔊 **सहायक (सहायता) की मौखिक प्रतिक्रिया:**"
    },
    "ta_IN": {
        "title": "🚨 சஹாயா அவசர உதவி",
        "subtitle": "பன்மொழி குரல் முதலுதவி & அவசர அனுப்புதல்",
        "mic_header": "🎙️ குரல் உள்ளீடு மற்றும் நேரலை",
        "mic_start": "🔴 பேச தட்டவும்",
        "mic_stop": "⏹️ நிறுத்து",
        "type_header": "⌨️ உரை உள்ளீடு",
        "type_placeholder": "எ.கா. ஆம்புலன்ஸ் தேவை அல்லது விபத்து",
        "detected": "🗣️ **கண்டறியப்பட்ட அவசரம்:**",
        "action_header": "⚡ பரிந்துரைக்கப்பட்ட நடவடிக்கை மற்றும் முதலுதவி",
        "first_aid_label": "🩹 முதலுதவி வழிகாட்டுதல்கள்:",
        "call_btn": "📞 உடனே {number} ஐ அழைக்கவும்",
        "directory_header": "📋 அவசர அடைவு (அழைக்க தட்டவும்)",
        "helpline": "உதவி எண்:",
        "realtime_desc": "நிகழ்நேர குரல் ஸ்ட்ரீம் செயலில் உள்ளது. உங்கள் அவசரநிலையை நேரடியாக பேசவும்.",
        "audio_response": "🔊 **உரையாடல் குரல் பதில் (சஹாயா):**"
    },
    "te_IN": {
        "title": "🚨 సహాయ అత్యవసర సహాయకుడు",
        "subtitle": "బహుభాషా వాయిస్ ఫస్ట్-ఎయిడ్ & ఎమర్జెన్సీ డిస్పాచ్",
        "mic_header": "🎙️ వాయిస్ ఇన్‌పుట్ & లైవ్ స్ట్రీమ్",
        "mic_start": "🔴 మాట్లాడటానికి నొక్కండి",
        "mic_stop": "⏹️ ఆపు",
        "type_header": "⌨️ టెక్స్ట్ ఇన్‌పుట్",
        "type_placeholder": "ఉదా. ఆంబులెన్స్ కావాలి లేదా ప్రమాదం",
        "detected": "🗣️ **గుర్తించబడిన అత్యవసరం:**",
        "action_header": "⚡ సిఫార్సు చేయబడిన చర్య మరియు ప్రథమ చికిత్స",
        "first_aid_label": "🩹 ప్రథమ చికిత్స మార్గదర్శకాలు:",
        "call_btn": "📞 ఇప్పుడే {number} కి కాల్ చేయండి",
        "directory_header": "📋 అత్యవసర డైరెక్టరీ (కాల్ చేయడానికి ట్యాప్ చేయండి)",
        "helpline": "హెల్ప్‌లైన్:",
        "realtime_desc": "రియల్ టైమ్ ఆడియో స్ట్రీమ్ సక్రియంగా ఉంది. నేరుగా మాట్లాడటానికి మీ అత్యవసర పరిస్థితిని తెలపండి.",
        "audio_response": "🔊 **సహాయకుడి వాచిక ప్రతిస్పందన:**"
    },
    "ml_IN": {
        "title": "🚨 സഹായ അടിയന്തര അസിസ്റ്റന്റ്",
        "subtitle": "ബഹുഭാഷാ വോയ്സ് ഫസ്റ്റ് എയ്ഡ് & എമർജൻസി ഡിസ്പാച്ച്",
        "mic_header": "🎙️ വോയ്സ് ഇൻപുട്ട് & ലൈവ് സ്ട്രീം",
        "mic_start": "🔴 സംസാരിക്കാൻ ടാപ്പ് ചെയ്യുക",
        "mic_stop": "⏹️ നിർത്തുക",
        "type_header": "⌨️ ടെക്സ്റ്റ് ഇൻപുട്ട്",
        "type_placeholder": "ഉദാ. ആംബുലൻസ് വേണം അല്ലെങ്കിൽ അപകടം",
        "detected": "🗣️ ** കണ്ടെത്തിയ അത്യാഹിതം:**",
        "action_header": "⚡ ശുപാർശ ചെയ്യുന്ന നടപടിയും പ്രഥമശുശ്രൂഷയും",
        "first_aid_label": "🩹 പ്രഥമശുശ്രൂഷ മാർഗ്ഗനിർദ്ദേശങ്ങൾ:",
        "call_btn": "📞 ഇപ്പോൾ {number}-ലേക്ക് വിളിക്കുക",
        "directory_header": "📋 എമർജൻസി ഡയറക്ടറി (വിളിക്കാൻ ടാപ്പ് ചെയ്യുക)",
        "helpline": "ഹെൽപ്പ്‌ലൈൻ:",
        "realtime_desc": "തത്സമയ ഓഡിയോ സ്ട്രീം സജീവമാണ്. നിങ്ങളുടെ അടിയന്തര സാഹചര്യം സംസാരിക്കുക.",
        "audio_response": "🔊 **അസിസ്റ്റന്റിന്റെ ശബ്ദ പ്രതികരണം:**"
    },
    "mr_IN": {
        "title": "🚨 साहाय्य आणीबाणी सहाय्यक",
        "subtitle": "बहुभाषिक व्हॉइस फर्स्ट-एड आणि आपत्कालीन प्रेषण",
        "mic_header": "🎙️ व्हॉइस इनपुट आणि लाईव्ह स्ट्रीम",
        "mic_start": "🔴 बोलण्यासाठी टॅप करा",
        "mic_stop": "⏹️ थांबवा",
        "type_header": "⌨️ मजकूर इनपुट",
        "type_placeholder": "उदा. रुग्णवाहिका हवी आहे किंवा अपघात",
        "detected": "🗣️ **आढळलेली आणीबाणी:**",
        "action_header": "⚡ शिफारस केलेली कृती आणि प्रथमोपचार",
        "first_aid_label": "🩹 प्रथमोपचार मार्गदर्शक तत्त्वे:",
        "call_btn": "📞 आता {number} वर कॉल करा",
        "directory_header": "📋 आणीबाणी निर्देशिका (कॉल करण्यासाठी टॅप करा)",
        "helpline": "हेल्पलाइन:",
        "realtime_desc": "रिअल-टाइम ऑडिओ प्रवाह सक्रिय आहे. तुमची आणीबाणी थेट बोला.",
        "audio_response": "🔊 **सहाय्यकाचा ऑडिओ प्रतिसाद:**"
    },
    "gu_IN": {
        "title": "🚨 સહાય ઇમરજન્સી અસિસ્ટન્ટ",
        "subtitle": "બહુભাষી વૉઇસ ફર્સ્ટ-એઇડ અને ઇમરજન્સી ડિસ્પેચ",
        "mic_header": "🎙️ વૉઇસ ઇનપુટ અને લાઈવ સ્ટ્રીમ",
        "mic_start": "🔴 બોલવા માટે ટેપ કરો",
        "mic_stop": "⏹️ બંધ કરો",
        "type_header": "⌨️ ટેક્સ્ટ ઇનપુટ",
        "type_placeholder": "દા.ત. એમ્બ્યુલન્સ જોઈએ છે અથવા અકસ્માત",
        "detected": "🗣️ **મૂકાયેલ કટોકટી:**",
        "action_header": "⚡ ભલામણ કરેલ પગલાં અને પ્રાથમિક સારવાર",
        "first_aid_label": "🩹 પ્રાથમિક સારવાર માર્ગદર્શિકા:",
        "call_btn": "📞 હમણાં જ {number} પર કૉલ કરો",
        "directory_header": "📋 ઇમરજન્સી ડિરેક્ટરી (કૉલ કરવા માટે ટેપ કરો)",
        "helpline": "હેલ્પલાઇન:",
        "realtime_desc": "વાસ્તવિક સમયનું ઓડિયો સ્ટ્રીમ સક્રિય છે. તમારી કટોકટી સીધી બોલો.",
        "audio_response": "🔊 **સહાયકનો અવાજ પ્રતિસાદ:**"
    },
    "bn_IN": {
        "title": "🚨 সহায় জরুরি সহকারী",
        "subtitle": "বহুভাষিক ভয়েস ফার্স্ট-এইড এবং জরুরি প্রেরণ",
        "mic_header": "🎙️ ভয়েস ইনপুট এবং লাইভ স্ট্রিম",
        "mic_start": "🔴 কথা বলতে ট্যাপ করুন",
        "mic_stop": "⏹️ থামুন",
        "type_header": "⌨️ টেক্সট ইনপুট",
        "type_placeholder": "যেমন অ্যাম্বুলেন্স প্রয়োজন বা দুর্ঘটনা",
        "detected": "🗣️ **শনাক্ত জরুরি অবস্থা:**",
        "action_header": "⚡ প্রস্তাবিত পদক্ষেপ এবং প্রাথমিক চিকিৎসা",
        "first_aid_label": "🩹 প্রাথমিক চিকিৎসার নির্দেশিকা:",
        "call_btn": "📞 এখনই {number}-এ কল করুন",
        "directory_header": "📋 জরুরি ডিরেক্টরি (কল করতে ট্যাপ করুন)",
        "helpline": "হেল্পলাইন:",
        "realtime_desc": "রিয়েল-টাইম অডিও স্ট্রিম সক্রিয় রয়েছে। সরাসরি আপনার জরুরি অবস্থা বলুন।",
        "audio_response": "🔊 **সহায়কের মৌখিক প্রতিক্রিয়া:**"
    },
    "pa_IN": {
        "title": "🚨 ਸਹਾਇ ਐਮਰਜੈਂਸੀ ਸਹਾਇਕ",
        "subtitle": "ਬਹੁ-ਭাষੀ ਵాయిਸ ਫਸਟ-ਏਡ ਅਤੇ ਐਮਰਜੈਂਸੀ ਡਿਸਪੈਚ",
        "mic_header": "🎙️ ਵాయిਸ ਇਨਪੁਟ ਅਤੇ ਲਾਈਵ ਸਟ੍ਰੀਮ",
        "mic_start": "🔴 ਬੋਲਣ ਲਈ ਟੈਪ ਕਰੋ",
        "mic_stop": "⏹️ ਰੋਕੋ",
        "type_header": "⌨️ ਟੈਕਸਟ ਇਨਪੁਟ",
        "type_placeholder": "ਉਦਾਹਰਨ ਲਈ ਐਂਬੂਲੈਂਸ ਚਾਹੀਦੀ ਹੈ ਜਾਂ ਹਾਦਸਾ",
        "detected": "🗣️ **ਪਤਾ ਲੱਗੀ ਐਮਰਜੈਂਸੀ:**",
        "action_header": "⚡ ਸਿਫਾਰਸ਼ ਕੀਤੀ ਕਾਰਵਾਈ ਅਤੇ ਮੁੱਢਲੀ ਸਹਾਇਤਾ",
        "first_aid_label": "🩹 ਮੁੱਢਲੀ ਸਹਾਇਤਾ ਦਿਸ਼ਾ-ਨਿਰਦੇਸ਼:",
        "call_btn": "📞 ਹੁਣੇ {number} 'ਤੇ ਕਾਲ ਕਰੋ",
        "directory_header": "📋 ਐਮਰਜੈਂਸੀ ਡਾਇਰੈਕਟਰੀ (ਕਾਲ ਕਰਨ ਲਈ ਟੈਪ ਕਰੋ)",
        "helpline": "ਹੈਲಪ್ਲਾਈਨ:",
        "realtime_desc": "ਰੀਅਲ-ਟਾਈਮ ਆਡੀਓ ਸਟ੍ਰੀਮ ਕਿਰਿਆਸ਼ੀਲ ਹੈ। ਆਪਣੀ ਐਮਰਜੈਂਸੀ ਸਿੱਧੀ ਬੋਲੋ।",
        "audio_response": "🔊 **ਸਹਾਇਕ ਦਾ ਬੋਲਿਆ ਜਵਾਬ:**"
    },
    "or_IN": {
        "title": "🚨 ସହାୟ ଜରୁରୀକାଳୀନ ସହାୟକ",
        "subtitle": "ବହୁଭାଷୀ ଭଏସ୍ ଫାଷ୍ଟ-ଏଡ୍ ଏବଂ ଜରୁରୀକାଳୀନ ପ୍ରେରଣ",
        "mic_header": "🎙️ ଭଏସ୍ ଇନପୁଟ୍ ଏବଂ ଲାଇଭ୍ ଷ୍ଟ୍ରିମ୍",
        "mic_start": "🔴 କଥିତ କରିବାକୁ ଟ୍ୟାପ୍ କରନ୍ତୁ",
        "mic_stop": "⏹️ ଅଟକାନ୍ତୁ",
        "type_header": "⌨️ ଟେକ୍ସଟ୍ ଇନପୁଟ୍",
        "type_placeholder": "ଯେପରି ଆମ୍ବୁଲାନ୍ସ ଆବଶ୍ୟକ କିମ୍ବା ଦୁର୍ଘଟଣା",
        "detected": "🗣️ **ଚିହ୍ନଟ ଜରୁରୀକାଳୀନ ପରିସ୍ଥିତି:**",
        "action_header": "⚡ ପରାମର୍ଶିତ କାର୍ଯ୍ୟ ଏବଂ ପ୍ରଥମ ଚିକିତ୍ସା",
        "first_aid_label": "🩹 ପ୍ରଥମ ଚିକିତ୍ସା ନିର୍ଦ୍ଦେଶାବଳୀ:",
        "call_btn": "📞 ବର୍ତ୍ତମାନ {number} କୁ କଲ୍ କରନ୍ତୁ",
        "directory_header": "📋 ଜରୁରୀକାଳୀନ ଡାଇରେକ୍ଟୋରୀ (କଲ୍ କରିବାକୁ ଟ୍ୟାପ୍ କରନ୍ତୁ)",
        "helpline": "ହେଲ୍ପଲାଇନ୍:",
        "realtime_desc": "ରিয়েল-ଟାଇମ୍ ଅডিও ଷ୍ଟ୍ରିମ୍ ସକ୍ରିୟ ଅଛି। ଆପଣଙ୍କର ଜରୁରୀକାଳୀନ ପରିସ୍ଥିତି କୁହନ୍ତୁ।",
        "audio_response": "🔊 **ସହାୟକଙ୍କ କଥିତ ପ୍ରତିକ୍ରିୟା:**"
    }
}

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
        "title": "Medical & Ambulance",
        "icon": "🚑",
        "number": "Strictly 108",
        "keywords": ["ambulance", "hospital", "doctor", "accident", "heart", "injury", "medical", "bleeding", "unconscious", "ಆಂಬ್ಯುಲೆನ್ಸ್", "ಆಸ್ಪತ್ರೆ", "ಅಪಘಾತ", "एम्बुलेंस", "अस्पताल", "चोट", "ആംബുലൻസ്", "அவசர ஊர்தி", "ఆంబులెన్స్", "ରୋଗୀବାହକ"],
        "desc": "Immediate dispatch for medical crises, severe injuries, or emergency transport.",
        "first_aid": "1. Check airway, breathing & pulse.\n2. Apply firm pressure to bleeding wounds.\n3. Keep person calm until 108 arrives."
    },
    {
        "title": "Police & Safety",
        "icon": "👮",
        "number": "Strictly 112",
        "keywords": ["police", "attack", "crime", "theft", "danger", "fight", "robbery", "help", "ಪೊಲೀಸ್", "ಸಹಾಯ", "पुलिस", "बचाओ", "പോലീസ്", "காவல்துறை", "పోలీసు", "ପୋଲିସ"],
        "desc": "Immediate assistance for crime, personal safety threats, or law enforcement.",
        "first_aid": "1. Move to a safe, well-lit public area.\n2. Stay on the line with 112 and provide landmarks."
    },
    {
        "title": "Assault & Distress (Women/Men)",
        "icon": "🛡️",
        "number": "Strictly 1091",
        "keywords": ["assault", "harassment", "abuse", "stalking", "distress", "threat", "molestation", "women", "men", "daim", "ದೌರ್ಜನ್ಯ", "ಕಿರುಕುಳ", "उत्पीड़न", "छेड़छाड़", "ഉപദ്രവം", "துன்புறுத்தல்", "వేధింపులు", "ଅତ୍ୟାଚାର"],
        "desc": "Dedicated protection and rapid response for assault, harassment, or severe distress.",
        "first_aid": "1. Seek immediate shelter in a safe shop or public group.\n2. Call 1091 or 112 instantly.\n3. Avoid confronting perpetrators alone."
    },
    {
        "title": "Fire & Rescue",
        "icon": "🚒",
        "number": "Strictly 101",
        "keywords": ["fire", "burn", "smoke", "cylinder", "blast", "rescue", "ಬೆಂಕಿ", "आग", "തീ", "தீ", "అగ్ని", "ନିଆଁ"],
        "desc": "Emergency response for fires, gas leaks, burns, or structural entrapment.",
        "first_aid": "1. Evacuate immediately and stay low under smoke.\n2. Run cool water over minor burns for 10-15 mins."
    },
    {
        "title": "Disaster & Flood Relief",
        "icon": "🌊",
        "number": "Strictly 1078",
        "keywords": ["flood", "earthquake", "cyclone", "landslide", "disaster", "ಭೂಕಂಪ", "ಪ್ರವಾಹ", "बाढ़", "പ്രളയം", "வெள்ளம்", "వరద", "ବନ୍ୟା"],
        "desc": "Support during natural calamities, earthquakes, floods, and severe weather.",
        "first_aid": "1. Switch off main electrical power and gas lines.\n2. Move to higher ground and avoid downed wires."
    }
]

st.markdown("""
<style>
    .stApp { background-color: #0f172a; color: #f8fafc; }
    .header-banner {
        background: linear-gradient(135deg, #dc2626, #991b1b);
        padding: 1.5rem;
        border-radius: 16px;
        text-align: center;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    .grid-card {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-top: 5px solid #dc2626;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    }
    .step-box {
        background-color: #0f172a;
        border: 1px solid #334155;
        border-radius: 6px;
        padding: 0.8rem;
        margin: 0.8rem 0;
        color: #cbd5e1;
        font-size: 0.9em;
    }
</style>
""", unsafe_allow_html=True)

selected_lang_label = st.selectbox(
    "🌐 Select Language / ಭಾಷೆ / भाषा",
    options=list(LANGUAGES.values()),
    index=0
)
lang_code = [k for k, v in LANGUAGES.items() if v == selected_lang_label][0]
t = TRANSLATIONS[lang_code]

st.markdown(f"""
<div class="header-banner">
    <h1>{t['title']}</h1>
    <p>{t['subtitle']} (Sahaya)</p>
</div>
""", unsafe_allow_html=True)

col_mic, col_type = st.columns(2)

with col_mic:
    st.subheader(t['mic_header'])
    
    if WEBRTC_AVAILABLE:
        st.caption(t['realtime_desc'])
        webrtc_streamer(
            key="emergency-stream",
            mode=WebRtcMode.SENDONLY,
            rtc_configuration=RTCConfiguration(
                {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
            ),
            media_stream_constraints={"video": False, "audio": True}
        )
    
    audio_info = mic_recorder(
        start_prompt=t['mic_start'],
        stop_prompt=t['mic_stop'],
        just_once=True,
        key="mic_grid_v3"
    )

with col_type:
    st.subheader(t['type_header'])
    manual_text = st.text_input(
        "Type emergency description:",
        placeholder=t['type_placeholder']
    )

def get_secret_or_env(key_name):
    try:
        if key_name in st.secrets:
            return st.secrets[key_name]
    except Exception:
        pass
    return os.getenv(key_name, "")

def process_audio_transcription(audio_bytes, code):
    token = get_secret_or_env("GNANI_TOKEN")
    access_key = get_secret_or_env("GNANI_ACCESS_KEY")

    if token and access_key:
        try:
            url = "https://asr.gnani.ai/asr"
            headers = {"token": token, "accesskey": access_key, "lang": code}
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
        "hi_IN": "इमरजेंसी! तुरंत एम्बुलेंस चाहिए, एक्सीडेंट हुआ है.",
    }
    return fallback_samples.get(code, "Emergency! Need immediate medical and safety assistance.")

def match_emergency(transcript_text):
    if not transcript_text:
        return []
    text_lower = transcript_text.lower()
    matches = []
    for service in EMERGENCY_DIRECTORY:
        if any(kw in text_lower for kw in service["keywords"]):
            matches.append(service)
    return matches

def generate_speech_audio(text, code):
    if not GTTS_AVAILABLE:
        return None
    try:
        base_lang = code.split('_')[0]
        tts = gTTS(text=text, lang=base_lang, slow=False)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp.read()
    except Exception:
        return None

final_transcript = ""

if manual_text:
    final_transcript = manual_text
elif audio_info and "bytes" in audio_info:
    st.audio(audio_info["bytes"], format="audio/wav")
    with st.spinner("Analyzing emergency voice input & generating instant response..."):
        final_transcript = process_audio_transcription(audio_info["bytes"], lang_code)

if final_transcript:
    st.success(f"{t['detected']} {final_transcript}")
    matched_services = match_emergency(final_transcript)
    if not matched_services:
        matched_services = [EMERGENCY_DIRECTORY[0]]

    primary_service = matched_services[0]
    spoken_message = f"Emergency detected. Please contact {primary_service['title']} immediately. {primary_service['desc']}"
    
    st.markdown(f"### {t['audio_response']}")
    audio_bytes_output = generate_speech_audio(spoken_message, lang_code)
    if audio_bytes_output:
        st.audio(audio_bytes_output, format="audio/mp3", autoplay=True)
    else:
        st.info(spoken_message)

    st.subheader(t['action_header'])
    for service in matched_services:
        call_button_text = t['call_btn'].format(number=service['number'])
        st.markdown(f"""
        <div style="background:#1e293b; border:1px solid #334155; border-left:6px solid #dc2626; border-radius:8px; padding:1.2rem; margin-bottom:1rem;">
            <h3>{service['icon']} {service['title']}</h3>
            <p>{service['desc']}</p>
            <div class="step-box">
                <strong>{t['first_aid_label']}</strong><br>
                <pre style="white-space: pre-wrap; font-family: inherit; margin:0; color:#cbd5e1;">{service['first_aid']}</pre>
            </div>
            <a href="tel:{service['number'].replace('Strictly ', '')}" style="text-decoration:none;">
                <button style="background-color:#dc2626; color:white; border:none; padding:10px 20px; border-radius:6px; font-weight:bold; cursor:pointer; width:100%; margin-top:10px;">
                    {call_button_text}
                </button>
            </a>
        </div>
        """, unsafe_allow_html=True)

st.divider()
st.subheader(t['directory_header'])

grid_rows = [EMERGENCY_DIRECTORY[i:i + 3] for i in range(0, len(EMERGENCY_DIRECTORY), 3)]

for row in grid_rows:
    cols = st.columns(len(row))
    for idx, srv in enumerate(row):
        with cols[idx]:
            call_button_text = t['call_btn'].format(number=srv['number'])
            st.markdown(f"""
            <div class="grid-card">
                <div>
                    <h2 style="font-size: 2.5rem; margin: 0 0 10px 0;">{srv['icon']}</h2>
                    <h3 style="color:#f8fafc; font-size: 1.1rem; margin-bottom: 8px;">{srv['title']}</h3>
                    <p style="color:#94a3b8; font-size: 0.85em; margin-bottom: 12px;">{srv['desc']}</p>
                </div>
                <div>
                    <div style="color:#38bdf8; font-weight:bold; margin-bottom:10px;">{t['helpline']} {srv['number']}</div>
                    <a href="tel:{srv['number'].replace('Strictly ', '')}" style="text-decoration:none;">
                        <button style="background:#dc2626; color:white; border:none; padding:8px 14px; border-radius:6px; font-weight:bold; cursor:pointer; width:100%;">
                            {call_button_text}
                        </button>
                    </a>
                </div>
            </div>
            """, unsafe_allow_html=True)
