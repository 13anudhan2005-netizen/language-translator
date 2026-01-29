import streamlit as st
from deep_translator import GoogleTranslator
from langdetect import detect
from gtts import gTTS
import base64
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
# LANGUAGE MAP (safe & supported)
# --------------------------------------------------
LANGUAGES = {
    "auto": "Auto Detect",
    "en": "English",
    "hi": "Hindi",
    "te": "Telugu",
    "ta": "Tamil",
    "fr": "French",
    "de": "German",
    "es": "Spanish",
    "ur": "Urdu",
    "bn": "Bengali",
    "mr": "Marathi",
    "gu": "Gujarati",
    "kn": "Kannada",
    "ml": "Malayalam",
    "pa": "Punjabi",
    "zh-CN": "Chinese",
    "ja": "Japanese",
    "ko": "Korean",
    "ru": "Russian"
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
st.caption("Translate • Detect Language • Listen • Download")

input_text = st.text_area(
    "✍️ Enter text to translate",
    height=150,
    placeholder="Type any language here..."
)

col1, col2, col3 = st.columns([3, 1, 3])

with col1:
    src_lang = st.selectbox(
        "Source Language",
        list(LANGUAGES.keys()),
        format_func=lambda x: LANGUAGES[x],
        index=0
    )

with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔁 Swap"):
        src_lang, tgt_lang = (
            st.session_state.get("tgt_lang", "en"),
            st.session_state.get("src_lang", "auto")
        )

with col3:
    tgt_lang = st.selectbox(
        "Target Language",
        list(LANGUAGES.keys())[1:],
        format_func=lambda x: LANGUAGES[x],
        index=0
    )

st.session_state.src_lang = src_lang
st.session_state.tgt_lang = tgt_lang

enable_audio = st.checkbox("🔊 Enable Text-to-Speech")
slow_audio = st.checkbox("🐢 Slow Speech")

# --------------------------------------------------
# TRANSLATION
# --------------------------------------------------
if st.button("🚀 Translate") and input_text.strip():

    try:
        with st.spinner("Translating..."):
            if src_lang == "auto":
                detected_lang = detect(input_text)
                src_code = detected_lang
                st.info(f"Detected language: {LANGUAGES.get(detected_lang, detected_lang)}")
            else:
                src_code = src_lang

            translated_text = GoogleTranslator(
                source=src_code,
                target=tgt_lang
            ).translate(input_text)

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
        # TEXT TO SPEECH
        # --------------------------------------------------
        if enable_audio:
            audio_file = f"audio_{uuid.uuid4().hex}.mp3"
            tts = gTTS(text=translated_text, lang=tgt_lang, slow=slow_audio)
            tts.save(audio_file)

            with open(audio_file, "rb") as f:
                audio_bytes = f.read()
                st.audio(audio_bytes, format="audio/mp3")

                b64 = base64.b64encode(audio_bytes).decode()
                st.markdown(
                    f'<a href="data:audio/mp3;base64,{b64}" download="translation.mp3">⬇ Download Audio</a>',
                    unsafe_allow_html=True
                )

            os.remove(audio_file)

    except Exception as e:
        st.error("❌ Translation failed. Please try again with shorter text or another language.")

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
