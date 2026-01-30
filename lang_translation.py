import streamlit as st
import requests
from langdetect import detect
from gtts import gTTS
import os
import uuid

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="Multilingual Language Translator",
    page_icon="🌍",
    layout="wide"
)

# -----------------------------
# READ API KEY SAFELY
# -----------------------------
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("Missing GOOGLE_API_KEY in Streamlit Secrets.")
    st.stop()

API_KEY = st.secrets["GOOGLE_API_KEY"]

# -----------------------------
# LOAD LANGUAGES (SAFE + FALLBACK)
# -----------------------------
@st.cache_data
def get_languages():
    url = (
        "https://translation.googleapis.com/language/translate/v2/languages"
        f"?key={API_KEY}&target=en"
    )
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()
        langs = data["data"]["languages"]
        lang_map = {"auto": "Auto Detect"}
        for l in langs:
            lang_map[l["language"]] = l.get("name", l["language"])
        return lang_map
    except Exception:
        # Fallback so app NEVER crashes
        return {
            "auto": "Auto Detect",
            "en": "English",
            "hi": "Hindi",
            "te": "Telugu",
            "ta": "Tamil",
            "fr": "French",
            "de": "German",
            "es": "Spanish",
            "ar": "Arabic",
            "ru": "Russian",
            "zh": "Chinese",
            "ja": "Japanese",
        }

LANGUAGES = get_languages()

# -----------------------------
# SESSION STATE
# -----------------------------
if "history" not in st.session_state:
    st.session_state.history = []

# -----------------------------
# UI
# -----------------------------
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

# -----------------------------
# TRANSLATION
# -----------------------------
def translate_text(q, source, target):
    url = f"https://translation.googleapis.com/language/translate/v2?key={API_KEY}"
    payload = {"q": q, "target": target}
    if source != "auto":
        payload["source"] = source
    r = requests.post(url, data=payload, timeout=15)
    r.raise_for_status()
    return r.json()["data"]["translations"][0]["translatedText"]

if st.button("🚀 Translate") and text.strip():
    try:
        with st.spinner("Translating..."):
            result = translate_text(text, src_lang, tgt_lang)

        st.subheader("✅ Translated Text")
        st.text_area("", result, height=180)

        st.session_state.history.append({
            "input": text,
            "output": result,
            "source": LANGUAGES.get(src_lang, src_lang),
            "target": LANGUAGES.get(tgt_lang, tgt_lang)
        })

        st.download_button("📄 Download Text", result, file_name="translation.txt")

        if enable_audio:
            try:
                fname = f"audio_{uuid.uuid4().hex}.mp3"
                gTTS(text=result, lang=tgt_lang[:2], slow=slow_audio).save(fname)
                with open(fname, "rb") as f:
                    st.audio(f.read(), format="audio/mp3")
                os.remove(fname)
            except:
                st.warning("Audio not supported for this language.")

    except Exception:
        st.error("❌ Translation failed. Check API key, billing, or quota.")

# -----------------------------
# HISTORY
# -----------------------------
if st.session_state.history:
    st.divider()
    st.subheader("🕘 Translation History")
    for i, it in enumerate(reversed(st.session_state.history[-5:]), 1):
        st.markdown(
            f"**{i}. {it['source']} → {it['target']}**  \n"
            f"🔹 Input: {it['input'][:80]}  \n"
            f"🔹 Output: {it['output'][:80]}"
        )
