import streamlit as st
from transformers import pipeline, AutoTokenizer
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
# LOAD MODEL (200+ LANGUAGES)
# --------------------------------------------------
MODEL_NAME = "facebook/nllb-200-distilled-600M"

@st.cache_resource
def load_model():
    translator = pipeline("translation", model=MODEL_NAME)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    return translator, tokenizer

translator, tokenizer = load_model()

# --------------------------------------------------
# LANGUAGE CODES (AUTO 200+)
# --------------------------------------------------
LANGUAGE_CODES = list(tokenizer.lang_code_to_id.keys())

# For UI display (keep codes readable)
LANGUAGES = {code: code for code in LANGUAGE_CODES}
LANGUAGES["auto"] = "Auto Detect"

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------
if "history" not in st.session_state:
    st.session_state.history = []

# --------------------------------------------------
# UI
# --------------------------------------------------
st.title("🌍 Multilingual Language Translator")
st.caption(f"Supports {len(LANGUAGE_CODES)}+ languages using Meta NLLB")

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

with col3:
    tgt_lang = st.selectbox(
        "Target Language",
        [l for l in LANGUAGE_CODES],
        index=0
    )

enable_audio = st.checkbox("🔊 Enable Text-to-Speech (limited languages)")
slow_audio = st.checkbox("🐢 Slow Speech")

# --------------------------------------------------
# LANGUAGE DETECTION (MAP TO NLLB)
# --------------------------------------------------
LANG_MAP = {
    "en": "eng_Latn",
    "hi": "hin_Deva",
    "te": "tel_Telu",
    "ta": "tam_Taml",
    "kn": "kan_Knda",
    "ml": "mal_Mlym",
    "mr": "mar_Deva",
    "fr": "fra_Latn",
    "de": "deu_Latn",
    "es": "spa_Latn",
    "ru": "rus_Cyrl",
    "ja": "jpn_Jpan",
    "zh-cn": "zho_Hans"
}

def detect_nllb_lang(text):
    try:
        code = detect(text)
        return LANG_MAP.get(code, "eng_Latn")
    except:
        return "eng_Latn"

# --------------------------------------------------
# TRANSLATION
# --------------------------------------------------
if st.button("🚀 Translate") and input_text.strip():

    try:
        with st.spinner("Translating..."):
            if src_lang == "auto":
                src_code = detect_nllb_lang(input_text)
                st.info(f"Detected source: {src_code}")
            else:
                src_code = src_lang

            result = translator(
                input_text,
                src_lang=src_code,
                tgt_lang=tgt_lang
            )

            translated_text = result[0]["translation_text"]

        st.subheader("✅ Translated Text")
        st.text_area("", translated_text, height=180)

        # Save history
        st.session_state.history.append({
            "input": input_text,
            "output": translated_text,
            "source": src_code,
            "target": tgt_lang
        })

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
                tts = gTTS(text=translated_text, lang=tgt_lang[:2], slow=slow_audio)
                tts.save(audio_file)

                with open(audio_file, "rb") as f:
                    audio_bytes = f.read()
                    st.audio(audio_bytes, format="audio/mp3")

                os.remove(audio_file)
            except:
                st.warning("Audio not supported for this language.")

    except Exception as e:
        st.error("❌ Translation failed. Try shorter text or another language.")

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
