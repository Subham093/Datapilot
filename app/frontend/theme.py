"""
Visual theme for DataPilot.

Design direction: "flight deck" — a nod to the product name. White
working canvas (like a bright cockpit display), deep navy for
structure and text, a single amber accent used sparingly for the
active tab / primary actions, and a monospace face for numbers and
metrics so they read like instrument readouts. This is purely a CSS
injection — it does not touch any application logic.
"""

import streamlit as st

NAVY = "#0B1F3A"
NAVY_SOFT = "#33455f"
AMBER = "#F5A623"
SURFACE = "#F4F6F9"
BORDER = "#E3E7ED"


def inject_theme() -> None:
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

        html, body, [class*="css"] {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }}

        .stApp {{
            background-color: #FFFFFF;
        }}

        /* ---- Headings ---- */
        h1, h2, h3 {{
            color: {NAVY};
            font-weight: 700;
            letter-spacing: -0.01em;
        }}

        h1 {{
            font-size: 1.9rem !important;
        }}

        /* ---- Sidebar: instrument-panel look ---- */
        section[data-testid="stSidebar"] {{
            background-color: {NAVY};
            border-right: 1px solid {BORDER};
        }}

        section[data-testid="stSidebar"] * {{
            color: #EDEFF3 !important;
        }}

        section[data-testid="stSidebar"] .stMarkdown h1,
        section[data-testid="stSidebar"] .stMarkdown h2,
        section[data-testid="stSidebar"] .stMarkdown h3,
        section[data-testid="stSidebar"] .stMarkdown h4 {{
            color: #FFFFFF !important;
        }}

        section[data-testid="stSidebar"] hr {{
            border-color: {NAVY_SOFT};
        }}

        /* File uploader inside the dark sidebar */
        section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] {{
            background-color: {NAVY_SOFT};
            border: 1px dashed #4c6382;
            border-radius: 10px;
        }}

        /* "Drag and drop..." instructions + size/type caption text */
        section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzoneInstructions"] {{
            color: #D7DEE9 !important;
        }}

        section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzoneInstructions"] svg {{
            fill: #D7DEE9 !important;
        }}

        /* The "Browse files" button itself — was inheriting a
           washed-out grey-on-white look that read as disabled.
           Give it real contrast: white background, navy text. */
        section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] button {{
            background-color: #FFFFFF !important;
            color: {NAVY} !important;
            border: 1px solid #FFFFFF !important;
            font-weight: 600 !important;
            opacity: 1 !important;
        }}

        section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] button:hover {{
            background-color: {SURFACE} !important;
            color: {NAVY} !important;
        }}

        section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] button p,
        section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] button span {{
            color: {NAVY} !important;
        }}

        /* Inline code spans (e.g. "Selected file: `x.csv`") keep a
           light background from Streamlit's base styles — force
           readable dark text on them instead of inheriting the
           sidebar's light text color. */
        section[data-testid="stSidebar"] code {{
            background-color: #EDEFF3 !important;
            color: {NAVY} !important;
            border-radius: 4px;
            padding: 0.1rem 0.35rem;
        }}

        /* Uploaded-file chip: filename + size + remove ("x") button.
           (Streamlit's internal name for this changed to "FileChip"
           in newer versions — the old "FileUploaderFile" testid this
           previously targeted no longer exists, which is why the
           chip was left with default near-white-on-white text.) */
        section[data-testid="stSidebar"] [data-testid="stFileChip"] {{
            background-color: #EDEFF3 !important;
            border-radius: 8px;
        }}

        section[data-testid="stSidebar"] [data-testid="stFileChip"],
        section[data-testid="stSidebar"] [data-testid="stFileChip"] * {{
            color: {NAVY} !important;
            fill: {NAVY} !important;
        }}

        section[data-testid="stSidebar"] [data-testid="stFileChipDeleteBtn"] button {{
            background-color: transparent !important;
        }}

        /* ---- Buttons ---- */
        .stButton > button, .stDownloadButton > button {{
            border-radius: 8px;
            font-weight: 600;
            border: 1px solid {BORDER};
        }}

        .stButton > button[kind="primary"], .stDownloadButton > button[kind="primary"] {{
            background-color: {AMBER};
            color: {NAVY};
            border: none;
        }}

        .stButton > button[kind="primary"]:hover, .stDownloadButton > button[kind="primary"]:hover {{
            background-color: #e2941a;
            color: {NAVY};
        }}

        /* "Upload & Analyze" button — blue background, white text,
           kept distinct from the amber primary-button style used
           elsewhere. */
        .st-key-upload_analyze_btn .stButton > button {{
            background-color: #2563EB;
            color: #FFFFFF;
            border: none;
        }}

        .st-key-upload_analyze_btn .stButton > button:hover {{
            background-color: #1D4ED8;
            color: #FFFFFF;
        }}

        /* ---- Tabs: instrument-panel selector strip ---- */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 4px;
            border-bottom: 2px solid {BORDER};
        }}

        .stTabs [data-baseweb="tab"] {{
            height: 42px;
            background-color: transparent;
            border-radius: 8px 8px 0 0;
            color: {NAVY_SOFT};
            font-weight: 600;
            font-size: 0.92rem;
        }}

        .stTabs [aria-selected="true"] {{
            background-color: {SURFACE};
            color: {NAVY} !important;
            border-bottom: 3px solid {AMBER};
        }}

        /* ---- Metrics: instrument-readout styling ---- */
        [data-testid="stMetricValue"] {{
            font-family: 'JetBrains Mono', 'Courier New', monospace;
            color: {NAVY};
            font-weight: 600;
        }}

        [data-testid="stMetricLabel"] {{
            color: {NAVY_SOFT};
            font-weight: 500;
        }}

        [data-testid="stMetric"] {{
            background-color: {SURFACE};
            border: 1px solid {BORDER};
            border-radius: 10px;
            padding: 0.85rem 1rem 0.6rem 1rem;
        }}

        /* ---- Dataframes / tables ---- */
        [data-testid="stDataFrame"] {{
            border: 1px solid {BORDER};
            border-radius: 8px;
            overflow: hidden;
        }}

        /* ---- Expanders ---- */
        .streamlit-expanderHeader {{
            font-weight: 600;
            color: {NAVY};
        }}

        /* ---- Dividers ---- */
        hr {{
            border-color: {BORDER};
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_app_header() -> None:
    st.markdown(
        f"""
        <div style="
            display: flex;
            align-items: center;
            gap: 0.6rem;
            padding-bottom: 0.2rem;
        ">
            <div style="
                font-size: 1.7rem;
                line-height: 1;
            ">🧭</div>
            <div>
                <div style="
                    font-size: 1.5rem;
                    font-weight: 700;
                    color: {NAVY};
                    line-height: 1.1;
                ">DataPilot</div>
                <div style="
                    font-size: 0.85rem;
                    color: {NAVY_SOFT};
                ">Autonomous AI Data Scientist</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    