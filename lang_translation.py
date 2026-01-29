import streamlit as st
from googletrans import Translator, LANGUAGES
from langdetect import detect
from gtts import gTTS
import pandas as pd
import base64
import os
import uuid

# -------------------- CONFIG --------------------
st.set_page_config(
    page_title="Multilingual Translator",
    page_icon="🌍",
    layout="wide"
)

# -------------------- INIT --------------------
translator = Translator()

if "history" not in st.session_state:
    st.session_state.history = []

if "src_lang" not in st.session_state:
    st.session_state.src_lang = "auto"

if "tgt_lang" not in st.session_state:
    st.session_state.tgt_lang = "english"

# -------------------- HELPERS --------------------
def text_download_button(text, filename):
    st.download_button(
        label="📄 Download Text",
        data=text,
        file_name=filename,
        mime="text/plain"
    )

def audio_download_link(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode()
    return f'<a href="data:audio/mp3;base64,{b64}" download="translation.mp3">⬇ Download Audio</a>'

# -------------------- UI --------------------
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
        ["auto"] + sorted(LANGUAGES.values()),
        index=0
    )

with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔁 Swap"):
        st.session_state.src_lang, st.session_state.tgt_lang = (
            st.session_state.tgt_lang,
            st.session_state.src_lang
        )

with col3:
    tgt_lang = st.selectbox(
        "Target Language",
        sorted(LANGUAGES.values()),
        index=sorted(LANGUAGES.values()).index("english")
    )

st.session_state.src_lang = src_lang
st.session_state.tgt_lang = tgt_lang

enable_audio = st.checkbox("🔊 Enable Text-to-Speech")
slow_audio = st.checkbox("🐢 Slow Speech")

# -------------------- TRANSLATION --------------------
if st.button("🚀 Translate") and input_text.strip():

    try:
        with st.spinner("Translating..."):
            if src_lang == "auto":
                detected = detect(input_text)
                src_code = detected
                st.info(f"Detected language: `{LANGUAGES.get(detected, detected)}`")
            else:
                src_code = list(LANGUAGES.keys())[list(LANGUAGES.values()).index(src_lang)]

            tgt_code = list(LANGUAGES.keys())[list(LANGUAGES.values()).index(tgt_lang)]

            result = translator.translate(
                input_text,
                src=src_code,
                dest=tgt_code
            )

            output_text = result.text

        st.subheader("✅ Translated Text")
        st.text_area("", output_text, height=180)

        # Save history
        st.session_state.history.append({
            "input": input_text,
            "output": output_text,
            "src": src_lang,
            "tgt": tgt_lang
        })

        text_download_button(output_text, "translation.txt")

        # -------------------- AUDIO --------------------
        if enable_audio:
            audio_id = f"audio_{uuid.uuid4().hex}.mp3"
            tts = gTTS(text=output_text, lang=tgt_code, slow=slow_audio)
            tts.save(audio_id)

            with open(audio_id, "rb") as audio:
                st.audio(audio.read(), format="audio/mp3")

            st.markdown(audio_download_link(audio_id), unsafe_allow_html=True)

            os.remove(audio_id)

    except Exception:
        st.error("❌ Translation failed. Try a shorter text or different language.")

# -------------------- HISTORY --------------------
if st.session_state.history:
    st.divider()
    st.subheader("🕘 Translation History (Session)")

    for i, item in enumerate(reversed(st.session_state.history[-5:]), 1):
        st.markdown(
            f"""
            **{i}. {item['src']} → {item['tgt']}**  
            🔹 Input: {item['input'][:60]}  
            🔹 Output: {item['output'][:60]}
            """
        )
