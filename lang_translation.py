import streamlit as st
import requests
from langdetect import detect
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
# STABLE LANGUAGE LIST (NO BILLING, NO CRASH)
# --------------------------------------------------
LANGUAGES = {
    "auto": "Auto Detect",
    "en": "English",
    "hi": "Hindi",
    "te": "Telugu",
    "ta": "Tamil",
    "kn": "Kannada",
    "ml": "Malayalam",
    "mr": "Marathi",
    "bn": "Bengali",
    "gu": "Gujarati",
    "pa": "Punjabi",
    "ur": "Urdu",
    "fr": "French",
    "de": "German",
    "es": "Spanish",
    "it": "Italian",
    "pt": "Portuguese",
    "ru": "Russian",
    "ar": "Arabic",
    "zh": "Chinese",
    "ja": "Japanese",
    "ko": "Korean",
    "nl": "Dutch",
    "sv": "Swedish",
    "fi": "Finnish",
    "pl": "Polish",
    "tr": "Turkish",
    "uk": "Ukrainian",
    "ro": "Romanian",
    "el": "Greek",
    "hu": "Hungarian",
    "cs": "Czech",
    "sk": "Slovak",
    "id": "Indonesian",
    "ms": "Malay",
    "th": "Thai",
    "vi": "Vietnamese"
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
st.caption(f"Supports {len(LANGUAGES)-1}+ reliable languages (no billing required)")

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
# TRANSLATION FUNCTION
# --------------------------------------------------
def translate_text(text, source, target):
    url = "https://libretranslate.de/translate"
    payload = {
        "q": text,
        "source": source,
        "target": target,
        "format": "text"
    }
    r = requests.post(url, data=payload, timeout=15)
    r.raise_for_status()
    return r.json()["translatedText"]

# --------------------------------------------------
# TRANSLATE ACTION
# --------------------------------------------------
if st.button("🚀 Translate") and text.strip():
    try:
        with st.spinner("Translating..."):
            if src_lang == "auto":
                src_lang = detect(text)

            translated = translate_text(text, src_lang, tgt_lang)

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

        if enable_audio:
            try:
                fname = f"audio_{uuid.uuid4().hex}.mp3"
                gTTS(text=translated, lang=tgt_lang, slow=slow_audio).save(fname)
                with open(fname, "rb") as f:
                    st.audio(f.read(), format="audio/mp3")
                os.remove(fname)
            except:
                st.warning("Audio not supported for this language.")

    except Exception:
        st.error("❌ Translation failed. Please try again later.")

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
