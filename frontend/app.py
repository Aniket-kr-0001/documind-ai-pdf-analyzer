import streamlit as st
import requests
import time

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="DocuMind AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

BACKEND_URL = "http://127.0.0.1:8000"

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

    /* Global font */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, sans-serif;
    }

    /* Hide Streamlit default header/footer */
    #MainMenu, footer, header { visibility: hidden; }

    /* ── Palette ──
       bg:        #0b0d14
       surface:   #14171f
       surface-2: #1a1e29
       border:    #262b3a
       accent:    #6c5ce7 -> #4f8ef7 gradient
       text hi:   #f1f2f6
       text lo:   #8b90a3
    */

    .stApp {
        background: radial-gradient(circle at 15% 0%, #151a2b 0%, #0b0d14 45%) fixed;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: #0d0f18;
        border-right: 1px solid #1f2330;
    }
    [data-testid="stSidebar"] * { color: #cdd1e0 !important; }
    [data-testid="stSidebar"] .stMarkdown p { color: #8b90a3 !important; }

    /* Brand block */
    .brand-title {
        font-size: 1.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #8b7bff, #4f8ef7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.02em;
        margin-bottom: 0.1rem;
    }
    .brand-sub {
        font-size: 0.8rem;
        color: #6b7085 !important;
        margin-bottom: 1.2rem;
    }

    /* Sidebar section titles */
    .section-title {
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        color: #6c7bff !important;
        margin-bottom: 0.7rem;
        margin-top: 0.3rem;
    }

    /* Cards */
    .card {
        background: linear-gradient(180deg, #161a26 0%, #12151f 100%);
        border: 1px solid #262b3a;
        border-radius: 16px;
        padding: 1.4rem 1.7rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 24px rgba(0,0,0,0.25);
    }

    /* Hero header */
    .hero {
        padding: 0.4rem 0 1.6rem 0;
    }
    .hero-title {
        font-size: 2.4rem;
        font-weight: 800;
        letter-spacing: -0.03em;
        background: linear-gradient(135deg, #f1f2f6, #9aa0c0);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.3rem;
    }
    .hero-sub {
        font-size: 1.02rem;
        color: #7d8299;
        font-weight: 400;
    }

    /* Answer box */
    .answer-box {
        background: #0f1219;
        border: 1px solid #232838;
        border-left: 3px solid #6c5ce7;
        border-radius: 10px;
        padding: 1.1rem 1.5rem;
        color: #e4e6f0;
        line-height: 1.75;
        font-size: 0.96rem;
    }

    /* Question label */
    .q-label {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        color: #8b7bff;
        font-weight: 700;
        font-size: 0.92rem;
        margin-bottom: 0.6rem;
    }
    .q-badge {
        background: linear-gradient(135deg, #6c5ce7, #4f8ef7);
        color: white;
        font-size: 0.7rem;
        font-weight: 700;
        border-radius: 6px;
        padding: 2px 8px;
    }

    /* Source chip */
    .source-chip {
        display: inline-block;
        background: #161c2e;
        color: #8ab4ff;
        border: 1px solid #26304a;
        border-radius: 20px;
        padding: 4px 13px;
        font-size: 0.76rem;
        font-weight: 500;
        margin-right: 6px;
        margin-bottom: 6px;
    }

    /* Status badges */
    .badge-success {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(76, 217, 145, 0.12);
        color: #4cd991;
        border: 1px solid rgba(76, 217, 145, 0.3);
        border-radius: 20px;
        padding: 5px 14px;
        font-size: 0.82rem;
        font-weight: 600;
    }
    .badge-idle {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(139, 144, 163, 0.1);
        color: #8b90a3;
        border: 1px solid rgba(139, 144, 163, 0.25);
        border-radius: 20px;
        padding: 5px 14px;
        font-size: 0.82rem;
        font-weight: 600;
    }

    /* Metrics */
    [data-testid="stMetricValue"] {
        color: #f1f2f6 !important;
        font-weight: 700 !important;
        font-size: 1.4rem !important;
    }
    [data-testid="stMetricLabel"] {
        color: #6b7085 !important;
        font-size: 0.75rem !important;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }

    /* Primary button */
    div.stButton > button {
        background: linear-gradient(135deg, #6c5ce7, #4f8ef7);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.55rem 1.6rem;
        font-weight: 600;
        font-size: 0.9rem;
        box-shadow: 0 4px 14px rgba(108, 92, 231, 0.35);
        transition: all 0.2s ease;
    }
    div.stButton > button:hover {
        opacity: 0.92;
        box-shadow: 0 6px 18px rgba(108, 92, 231, 0.5);
        transform: translateY(-1px);
    }

    /* Form submit button */
    button[kind="formSubmit"] {
        background: linear-gradient(135deg, #6c5ce7, #4f8ef7) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
    }

    /* Input field */
    .stTextInput > div > div > input {
        background: #12151f;
        border: 1px solid #262b3a;
        border-radius: 10px;
        color: #e4e6f0;
        padding: 0.7rem 1.1rem;
        font-size: 0.95rem;
    }
    .stTextInput > div > div > input:focus {
        border-color: #6c5ce7;
        box-shadow: 0 0 0 1px #6c5ce7;
    }
    .stTextInput label { color: #8b90a3 !important; }

    /* File uploader */
    [data-testid="stFileUploaderDropzone"] {
        background: #12151f;
        border: 1.5px dashed #2e3448;
        border-radius: 12px;
    }
    [data-testid="stFileUploaderDropzone"]:hover {
        border-color: #6c5ce7;
    }

    /* Expander */
    .streamlit-expanderHeader {
        background: #12151f !important;
        border-radius: 8px !important;
        color: #8b90a3 !important;
        font-size: 0.85rem !important;
    }

    /* Divider */
    hr { border-color: #1f2330; margin: 1.2rem 0; }

    /* Caption / code text in sources */
    .stCaption, [data-testid="stCaptionContainer"] {
        color: #6b7085 !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.78rem !important;
    }

    /* Info / warning boxes */
    div[data-testid="stAlert"] {
        border-radius: 12px;
        border: 1px solid #262b3a;
    }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-track { background: #0b0d14; }
    ::-webkit-scrollbar-thumb { background: #2a2f42; border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: #3a4060; }
</style>
""", unsafe_allow_html=True)

# ── Session state init ─────────────────────────────────────────────────────────
if "doc_loaded" not in st.session_state:
    st.session_state.doc_loaded = False
if "doc_info" not in st.session_state:
    st.session_state.doc_info = {}
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="brand-title">🧠 DocuMind AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-sub">Intelligent PDF Analysis, powered by Gemini</div>', unsafe_allow_html=True)
    st.divider()

    st.markdown('<p class="section-title">📄 Document Upload</p>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Drop your PDF here",
        type=["pdf"],
        label_visibility="collapsed",
    )

    if uploaded_file:
        st.markdown(f"**Selected:** `{uploaded_file.name}`")
        if st.button("⚡ Process Document", use_container_width=True):
            with st.spinner("Parsing and indexing…"):
                try:
                    files = {
                        "file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")
                    }
                    res = requests.post(f"{BACKEND_URL}/upload", files=files)
                    if res.status_code == 200:
                        data = res.json()
                        st.session_state.doc_loaded = True
                        st.session_state.doc_info = data
                        st.session_state.chat_history = []
                        st.success("Document indexed successfully!")
                    else:
                        st.error(f"Upload failed ({res.status_code})")
                        st.code(res.text)
                except Exception as e:
                    st.error(f"Connection error: {e}")

    st.divider()

    # Document status
    st.markdown('<p class="section-title">📊 Document Status</p>', unsafe_allow_html=True)
    if st.session_state.doc_loaded:
        info = st.session_state.doc_info
        st.markdown('<span class="badge-success">● Active</span>', unsafe_allow_html=True)
        st.markdown(f"**File:** {info.get('fileName', '—')}")
        col1, col2 = st.columns(2)
        col1.metric("Pages", info.get("totalPages", "—"))
        col2.metric("Chunks", info.get("totalChunks", "—"))
    else:
        st.markdown('<span class="badge-idle">○ No document loaded</span>', unsafe_allow_html=True)

    st.divider()
    st.markdown(
        "<small style='color:#4a4f66;'>Powered by Gemini · LangChain · ChromaDB</small>",
        unsafe_allow_html=True,
    )

# ── Main area ──────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="hero">'
    '<div class="hero-title">DocuMind AI</div>'
    '<div class="hero-sub">Ask anything about your uploaded PDF and get precise, context-aware answers.</div>'
    '</div>',
    unsafe_allow_html=True,
)

if not st.session_state.doc_loaded:
    st.info("👈  Upload and process a PDF from the sidebar to get started.")
else:
    # Question input
    st.markdown('<p class="section-title">💬 Ask a Question</p>', unsafe_allow_html=True)

    with st.form(key="question_form", clear_on_submit=True):
        col_input, col_btn = st.columns([5, 1])
        with col_input:
            user_question = st.text_input(
                "Your question",
                placeholder="e.g. What is the main conclusion of this document?",
                label_visibility="collapsed",
            )
        with col_btn:
            submitted = st.form_submit_button("Ask →", use_container_width=True)

    if submitted and user_question.strip():
        with st.spinner("Retrieving context and generating answer…"):
            try:
                res = requests.post(
                    f"{BACKEND_URL}/ask",
                    json={"question": user_question},
                )
                if res.status_code == 200:
                    result = res.json()
                    st.session_state.chat_history.append({
                        "question": user_question,
                        "answer": result.get("answer", ""),
                        "sources": result.get("sources", []),
                    })
                elif res.status_code == 429:
                    st.warning("⏳ Rate limit reached. Please wait a moment and try again.")
                else:
                    st.error(f"Backend error ({res.status_code})")
                    st.code(res.text)
            except Exception as e:
                st.error(f"Could not connect to backend: {e}")

    elif submitted:
        st.warning("Please enter a question before submitting.")

    # ── Chat history (newest first) ────────────────────────────────────────────
    if st.session_state.chat_history:
        st.divider()
        st.markdown('<p class="section-title">🕘 Conversation History</p>', unsafe_allow_html=True)

        for i, entry in enumerate(reversed(st.session_state.chat_history)):
            qnum = len(st.session_state.chat_history) - i
            with st.container():
                st.markdown(
                    f'<div class="card">'
                    f'<div class="q-label"><span class="q-badge">Q{qnum}</span>{entry["question"]}</div>',
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f'<div class="answer-box">{entry["answer"]}</div>',
                    unsafe_allow_html=True,
                )

                sources = entry.get("sources", [])
                if sources:
                    st.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)
                    chips = "".join(
                        f'<span class="source-chip">📄 Page {s.get("page")}</span>'
                        for s in sources
                    )
                    st.markdown(chips, unsafe_allow_html=True)

                    with st.expander("View source excerpts"):
                        for idx, src in enumerate(sources):
                            st.markdown(f"**Chunk {idx + 1} — Page {src.get('page')}**")
                            st.caption(src.get("content", ""))
                            if idx < len(sources) - 1:
                                st.divider()

                st.markdown("</div>", unsafe_allow_html=True)