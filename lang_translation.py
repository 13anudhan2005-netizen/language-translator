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
# GET 100+ LANGUAGES FROM API
# --------------------------------------------------
@st.cache_data
def get_languages():
    url = "https://libretranslate.de/languages"
    response = requests.get(url, timeout=10)
    response.raise_for_status()

    langs = response.json()
    lang_map = {"auto": "Auto Detect"}

    for lang in langs:
        lang_map[lang["code"]] = lang["name"]

    return lang_map

LANGUAGES = get_languages()

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------
if "history" not in st.session_state:
    st.session_state.history = []

# --------------------------------------------------
# UI
# --------------------------------------------------
st.title("🌍 Multilingual Language Translator")
st.caption(f"Supports {len(LANGUAGES) - 1}+ languages • Fast & Cloud-Ready")

input_text = st.text_area(
    "✍️ Enter text to translate",
    height=150,
    placeholder="Type any language here..."
)

col1, col2 = st.columns(2)

with col1:
    src_lang = st.selectbox(
        "Source Language",
        list(LANGUAGES.keys()),
        format_func=lambda x: LANGUAGES[x],
        index=0
    )

with col2:
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
    response = requests.post(url, data=payload, timeout=15)
    response.raise_for_status()
    return response.json()["translatedText"]

# --------------------------------------------------
# TRANSLATE BUTTON
# --------------------------------------------------
if st.button("🚀 Translate") and input_text.strip():

    try:
        with st.spinner("Translating..."):
            if src_lang == "auto":
                detected = detect(input_text)
                src_code = detected
                st.info(f"Detected language: {LANGUAGES.get(detected, detected)}")
            else:
                src_code = src_lang

            translated_text = translate_text(
                input_text,
                src_code,
                tgt_lang
            )

        st.subheader("✅ Translated Text")
        st.text_area("", translated_text, height=180)

        # Save history
        st.session_state.history.append({
            "input": input_text,
            "output": translated_text,
            "source": LANGUAGES.get(src_lang, src_lang),
            "target": LANGUAGES.get(tgt_lang, tgt_lang)
        })

        # Download translated text
        st.download_button(
            "📄 Download Text",
            translated_text,
            file_name="translation.txt"
        )

        # --------------------------------------------------
        # TEXT TO SPEECH (BEST EFFORT)
        # --------------------------------------------------
        if enable_audio:
            try:
                audio_file = f"audio_{uuid.uuid4().hex}.mp3"
                tts = gTTS(
                    text=translated_text,
                    lang=tgt_lang[:2],
                    slow=slow_audio
                )
                tts.save(audio_file)

                with open(audio_file, "rb") as f:
                    st.audio(f.read(), format="audio/mp3")

                os.remove(audio_file)
            except:
                st.warning("Audio not supported for this language.")

    except Exception:
        st.error("❌ Translation failed. Please try again later.")

# --------------------------------------------------
# HISTORY
# --------------------------------------------------
if st.session_state.history:
    st.divider()
    st.subheader("🕘 Translation History (Session)")

    for i, item in enumerate(reversed(st.session_state.history[-5:]), 1):
        st.markdown(
            f"""
            **{i}. {item['source']} → {item['target']}**  
            🔹 Input: {item['input'][:80]}  
            🔹 Output: {item['output'][:80]}
            """
        )
