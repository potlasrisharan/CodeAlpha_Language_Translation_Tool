"""Modern Multi-Language Translation Workbench following anti-slop design directives."""

import streamlit as st
import pandas as pd
from src.constants import SUPPORTED_LANGUAGES, POPULAR_LANGUAGES, SVG_ICONS
from src.translator import TranslationService, TranslationResult
from src.tts import TextToSpeechService
from src.history import HistoryManager

st.set_page_config(
    page_title="Linguistic Workspace / Multi-Language Translator",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Custom High-Taste CSS
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Geist:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Geist', -apple-system, BlinkMacSystemFont, sans-serif;
        background-color: #09090b !important;
        color: #f4f4f5 !important;
    }
    
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2.5rem;
        max-width: 1400px;
    }

    /* Workspace Header */
    .workspace-header {
        border-bottom: 1px solid #27272a;
        padding-bottom: 1rem;
        margin-bottom: 1.75rem;
        display: flex;
        justify-content: space-between;
        align-items: baseline;
    }
    .workspace-title {
        font-size: 1.5rem;
        font-weight: 700;
        letter-spacing: -0.04em;
        color: #f4f4f5;
        margin: 0;
    }
    .workspace-status {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        color: #3b82f6;
        background: rgba(59, 130, 246, 0.1);
        border: 1px solid rgba(59, 130, 246, 0.25);
        padding: 0.2rem 0.6rem;
        border-radius: 9999px;
    }

    /* Workbench Panes */
    .pane-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.5rem;
    }
    .pane-label {
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #a1a1aa;
    }
    .meta-tag {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        color: #71717a;
    }

    /* Output Readout Container */
    .output-box {
        background-color: #121215;
        border: 1px solid #27272a;
        border-radius: 0.75rem;
        padding: 1.25rem;
        min-height: 240px;
        font-size: 1.05rem;
        line-height: 1.65;
        color: #f4f4f5;
        white-space: pre-wrap;
    }
    .output-box-placeholder {
        color: #52525b;
        font-style: italic;
    }

    /* Primary Action Buttons */
    .stButton > button {
        background-color: #2563eb !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 0.875rem !important;
        border-radius: 0.5rem !important;
        border: none !important;
        padding: 0.55rem 1.25rem !important;
        transition: transform 0.1s ease, background-color 0.15s ease !important;
    }
    .stButton > button:hover {
        background-color: #1d4ed8 !important;
    }
    .stButton > button:active {
        transform: scale(0.98) !important;
    }

    /* Secondary outline buttons */
    .sample-pill button {
        background-color: #18181b !important;
        color: #a1a1aa !important;
        border: 1px solid #27272a !important;
        font-size: 0.75rem !important;
        padding: 0.25rem 0.6rem !important;
        border-radius: 9999px !important;
    }
    .sample-pill button:hover {
        background-color: #27272a !important;
        color: #f4f4f5 !important;
    }

    /* Textarea */
    .stTextArea textarea {
        background-color: #121215 !important;
        color: #f4f4f5 !important;
        border: 1px solid #27272a !important;
        border-radius: 0.75rem !important;
        font-size: 1.05rem !important;
        line-height: 1.65 !important;
    }
    .stTextArea textarea:focus {
        border-color: #3b82f6 !important;
        box-shadow: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize Session State
if "history" not in st.session_state:
    st.session_state.history = HistoryManager()
if "src_lang" not in st.session_state:
    st.session_state.src_lang = "Auto Detect"
if "tgt_lang" not in st.session_state:
    st.session_state.tgt_lang = "Spanish"
if "input_text" not in st.session_state:
    st.session_state.input_text = "Hello world, welcome to our AI translation workspace."
if "last_result" not in st.session_state:
    st.session_state.last_result = None

service = TranslationService()
tts_service = TextToSpeechService()

# Header
st.markdown(
    """
    <div class="workspace-header">
        <div>
            <h1 class="workspace-title">Language Translation Workspace</h1>
            <p style="color: #71717a; font-size: 0.85rem; margin-top: 0.25rem;">
                Neural multilingual translation engine with audio synthesis and instant clipboard export.
            </p>
        </div>
        <div>
            <span class="workspace-status">100+ LANGUAGES READY</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Language Selectors & Swap Anchor
lang_col1, lang_col_swap, lang_col2 = st.columns([1.8, 0.4, 1.8], gap="small")

lang_names = list(SUPPORTED_LANGUAGES.keys())
src_options = lang_names
tgt_options = [l for l in lang_names if l != "Auto Detect"]

with lang_col1:
    st.markdown('<div class="pane-label">Source Language</div>', unsafe_allow_html=True)
    selected_src = st.selectbox(
        "Source Language Selector",
        options=src_options,
        index=src_options.index(st.session_state.src_lang) if st.session_state.src_lang in src_options else 0,
        label_visibility="collapsed",
    )
    st.session_state.src_lang = selected_src

with lang_col_swap:
    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
    if st.button("Swap", help="Swap Source and Target Languages"):
        if st.session_state.src_lang != "Auto Detect":
            temp = st.session_state.src_lang
            st.session_state.src_lang = st.session_state.tgt_lang
            st.session_state.tgt_lang = temp
            st.rerun()

with lang_col2:
    st.markdown('<div class="pane-label">Target Language</div>', unsafe_allow_html=True)
    selected_tgt = st.selectbox(
        "Target Language Selector",
        options=tgt_options,
        index=tgt_options.index(st.session_state.tgt_lang) if st.session_state.tgt_lang in tgt_options else 0,
        label_visibility="collapsed",
    )
    st.session_state.tgt_lang = selected_tgt

# Quick sample chips
sample_cols = st.columns([1, 1, 1, 3])
with sample_cols[0]:
    if st.button("Load English Sample"):
        st.session_state.input_text = "Artificial intelligence is reshaping the future of automation and problem solving."
        st.session_state.src_lang = "English"
        st.session_state.tgt_lang = "Spanish"
        st.rerun()
with sample_cols[1]:
    if st.button("Load French Sample"):
        st.session_state.input_text = "Le modèle de détection d'objets fonctionne en temps réel avec une grande précision."
        st.session_state.src_lang = "French"
        st.session_state.tgt_lang = "English"
        st.rerun()
with sample_cols[2]:
    if st.button("Load Hindi Sample"):
        st.session_state.input_text = "कृत्रिम बुद्धिमत्ता आधुनिक सॉफ्टवेयर विकास को बदल रही है।"
        st.session_state.src_lang = "Hindi"
        st.session_state.tgt_lang = "English"
        st.rerun()

# Main Translation Workbench (Split Screen)
work_col1, work_col2 = st.columns(2, gap="medium")

with work_col1:
    st.markdown(
        """
        <div class="pane-header">
            <span class="pane-label">Input Text</span>
            <span class="meta-tag">SOURCE</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    input_text = st.text_area(
        "Source Text Input",
        value=st.session_state.input_text,
        placeholder="Enter text or paste document content to translate...",
        height=240,
        label_visibility="collapsed",
        key="source_text_box",
    )
    st.session_state.input_text = input_text

    # Word and char count for source
    src_chars = len(input_text)
    src_words = len(input_text.split())
    st.markdown(
        f'<div class="meta-tag" style="margin-top: 0.35rem;">{src_words} words · {src_chars} characters</div>',
        unsafe_allow_html=True,
    )

    action_c1, action_c2 = st.columns([1, 1])
    with action_c1:
        translate_trigger = st.button("Translate Text", use_container_width=True)
    with action_c2:
        src_tts_btn = st.button("Listen Source Audio", use_container_width=True)

with work_col2:
    st.markdown(
        """
        <div class="pane-header">
            <span class="pane-label">Synthesized Output</span>
            <span class="meta-tag">TARGET</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Perform Translation when triggered
    if translate_trigger and input_text.strip():
        with st.spinner("Synthesizing translation..."):
            result = service.translate(
                text=input_text,
                source_lang_name=st.session_state.src_lang,
                target_lang_name=st.session_state.tgt_lang,
            )
            st.session_state.last_result = result
            st.session_state.history.add(result)

    result = st.session_state.last_result

    if result and result.error:
        st.error(result.error)
    elif result and result.translated_text:
        st.markdown(
            f'<div class="output-box">{result.translated_text}</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="meta-tag" style="margin-top: 0.35rem;">{result.word_count} words · {result.char_count} characters · Latency: {result.latency_ms}ms · Engine: {result.provider_used}</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="output-box output-box-placeholder">Translated text will appear here. Select languages and click "Translate Text".</div>',
            unsafe_allow_html=True,
        )

    out_c1, out_c2 = st.columns(2)
    with out_c1:
        tgt_tts_btn = st.button("Listen Translated Audio", use_container_width=True)
    with out_c2:
        if result and result.translated_text:
            st.download_button(
                label="Download Translation",
                data=result.translated_text,
                file_name=f"translation_{result.target_lang_code}.txt",
                mime="text/plain",
                use_container_width=True,
            )

# Audio synthesis handlers
if src_tts_btn and input_text.strip():
    src_code = SUPPORTED_LANGUAGES.get(st.session_state.src_lang, "en")
    audio_bytes = tts_service.synthesize_to_bytes(input_text, lang_code=src_code)
    if audio_bytes:
        st.audio(audio_bytes, format="audio/mp3")
    else:
        st.warning("Speech synthesis unavailable for this text.")

if tgt_tts_btn and result and result.translated_text:
    audio_bytes = tts_service.synthesize_to_bytes(result.translated_text, lang_code=result.target_lang_code)
    if audio_bytes:
        st.audio(audio_bytes, format="audio/mp3")
    else:
        st.warning("Speech synthesis unavailable for this target language.")

# Translation History Section
st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
with st.expander("Translation History Log & Export", expanded=False):
    history_records = st.session_state.history.get_all()
    if history_records:
        df_hist = pd.DataFrame(history_records)
        st.dataframe(
            df_hist[["timestamp", "source_lang", "target_lang", "source_text", "translated_text", "latency_ms"]],
            use_container_width=True,
            hide_index=True,
        )
        col_h1, col_h2 = st.columns([1, 4])
        with col_h1:
            st.download_button(
                label="Export History (JSON)",
                data=st.session_state.history.export_json(),
                file_name="translation_history.json",
                mime="application/json",
            )
        with col_h2:
            if st.button("Clear History"):
                st.session_state.history.clear()
                st.rerun()
    else:
        st.info("No translations recorded in this session yet.")
