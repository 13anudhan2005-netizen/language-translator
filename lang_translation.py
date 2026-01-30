import streamlit as st
from deep_translator import GoogleTranslator
from gtts import gTTS
import os
import uuid

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="Multilingual Language Translator",
    page_icon="🌍",
    layout="wide"
)

# --------------------------------------------------
# LANGUAGE LIST (100+ – FIXED)
# --------------------------------------------------
LANGUAGES = {
    "auto": "Auto Detect",

    "af": "Afrikaans",
    "sq": "Albanian",
    "am": "Amharic",
    "ar": "Arabic",
    "hy": "Armenian",
    "az": "Azerbaijani",
    "eu": "Basque",
    "be": "Belarusian",
    "bn": "Bengali",
    "bs": "Bosnian",
    "bg": "Bulgarian",
    "ca": "Catalan",
    "ceb": "Cebuano",
    "ny": "Chichewa",
    "zh-CN": "Chinese (Simplified)",
    "zh-TW": "Chinese (Traditional)",
    "co": "Corsican",
    "hr": "Croatian",
    "cs": "Czech",
    "da": "Danish",
    "nl": "Dutch",
    "en": "English",
    "eo": "Esperanto",
    "et": "Estonian",
    "tl": "Filipino",
    "fi": "Finnish",
    "fr": "French",
    "fy": "Frisian",
    "gl": "Galician",
    "ka": "Georgian",
    "de": "German",
    "el": "Greek",
    "gu": "Gujarati",
    "ht": "Haitian Creole",
    "ha": "Hausa",
    "haw": "Hawaiian",
    "he": "Hebrew",
    "hi": "Hindi",
    "hmn": "Hmong",
    "hu": "Hungarian",
    "is": "Icelandic",
    "ig": "Igbo",
    "id": "Indonesian",
    "ga": "Irish",
    "it": "Italian",
    "ja": "Japanese",
    "jv": "Javanese",
    "kn": "Kannada",
    "kk": "Kazakh",
    "km": "Khmer",
    "rw": "Kinyarwanda",
    "ko": "Korean",
    "ku": "Kurdish (Kurmanji)",
    "ky": "Kyrgyz",
    "lo": "Lao",
    "la": "Latin",
    "lv": "Latvian",
    "lt": "Lithuanian",
    "lb": "Luxembourgish",
    "mk": "Macedonian",
    "mg": "Malagasy",
    "ms": "Malay",
    "ml": "Malayalam",
    "mt": "Maltese",
    "mi": "Maori",
    "mr": "Marathi",
    "mn": "Mongolian",
    "my": "Myanmar (Burmese)",
    "ne": "Nepali",
    "no": "Norwegian",
    "ps": "Pashto",
    "fa": "Persian",
    "pl": "Polish",
    "pt": "Portuguese",
    "pa": "Punjabi",
    "ro": "Romanian",
    "ru": "Russian",
    "sm": "Samoan",
    "gd": "Scots Gaelic",
    "sr": "Serbian",
    "st": "Sesotho",
    "sn": "Shona",
    "sd": "Sindhi",
    "si": "Sinhala",
    "sk": "Slovak",
    "sl": "Slovenian",
    "so": "Somali",
    "es": "Spanish",
    "su": "Sundanese",
    "sw": "Swahili",
    "sv": "Swedish",
    "tg": "Tajik",
    "ta": "Tamil",
    "te": "Telugu",
    "th": "Thai",
    "tr": "Turkish",
    "uk": "Ukrainian",
    "ur": "Urdu",
    "ug": "Uyghur",
    "uz": "Uzbek",
    "vi": "Vietnamese",
    "cy": "Welsh",
    "xh": "Xhosa",
    "yi": "Yiddish",
    "yo": "Yoruba",
    "zu": "Zulu",
    "or": "Odia"
}

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------
if "history" not in st.session_state:
    st.session_state.history = []

# --------------------------------------------------
# UI
# --------------------------------------------------
st.title("🌍 Multilingual Language Translator")
st.caption(f"Supports {len(LANGUAGES)-1}+ languages")

text = st.text_area(
    "✍️ Enter text to translate",
    height=150,
    placeholder="Type any language here..."
)

c1, c2 = st.columns(2)

with c1:
    src_lang = st.selectbox(
        "Source Language",
        list(LANGUAGES.keys()),
        format_func=lambda x: LANGUAGES[x],
        index=0
    )

with c2:
    tgt_lang = st.selectbox(
        "Target Language",
        list(LANGUAGES.keys())[1:],
        format_func=lambda x: LANGUAGES[x],
        index=0
    )

enable_audio = st.checkbox("🔊 Enable Text-to-Speech")
slow_audio = st.checkbox("🐢 Slow Speech")

# --------------------------------------------------
# TRANSLATION
# --------------------------------------------------
if st.button("🚀 Translate") and text.strip():
    try:
        with st.spinner("Translating..."):
            translated = GoogleTranslator(
                source=src_lang,
                target=tgt_lang
            ).translate(text)

        st.subheader("✅ Translated Text")
        st.text_area("", translated, height=180)

        st.session_state.history.append({
            "input": text,
            "output": translated,
            "source": LANGUAGES.get(src_lang, src_lang),
            "target": LANGUAGES.get(tgt_lang, tgt_lang)
        })

        st.download_button(
            "📄 Download Text",
            translated,
            file_name="translation.txt"
        )

        # ------------------------------
        # TEXT TO SPEECH
        # ------------------------------
        if enable_audio:
            try:
                # gTTS only supports short language codes
                tts_lang = tgt_lang.split("-")[0]

                fname = f"audio_{uuid.uuid4().hex}.mp3"
                gTTS(
                    text=translated,
                    lang=tts_lang,
                    slow=slow_audio
                ).save(fname)

                with open(fname, "rb") as f:
                    st.audio(f.read(), format="audio/mp3")

                os.remove(fname)
            except:
                st.warning("Audio not supported for this language.")

    except Exception as e:
        st.error("❌ Translation failed. Please try again.")

# --------------------------------------------------
# HISTORY
# --------------------------------------------------
if st.session_state.history:
    st.divider()
    st.subheader("🕘 Translation History")
    for i, it in enumerate(reversed(st.session_state.history[-5:]), 1):
        st.markdown(
            f"**{i}. {it['source']} → {it['target']}**  \n"
            f"🔹 Input: {it['input'][:80]}  \n"
            f"🔹 Output: {it['output'][:80]}"
        )
