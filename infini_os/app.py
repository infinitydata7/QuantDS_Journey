# app.py  — Infini Capital Task OS  ── Main entry point
import os
import streamlit as st


# ── Absolute path for DB & assets ──────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

st.set_page_config(
    page_title  = "Infini Capital",
    page_icon   = "💹",
    layout      = "wide",
    initial_sidebar_state = "collapsed",
)

# ── Global CSS ──────────────────────────────────────────────
st.markdown("""
<style>
/* ── Font & Base ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* ── Background ── */
.stApp { background: #0a0e1a; color: #e2e8f0; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: #0d1117 !important;
    border-right: 1px solid #1e293b;
}

/* ── Metric cards ── */
[data-testid="metric-container"] {
    background: #111827;
    border: 1px solid #1e293b;
    border-radius: 12px;
    padding: 16px !important;
}
[data-testid="metric-container"] label { color: #64748b !important; font-size: 11px !important; text-transform: uppercase; letter-spacing: 1px; }
[data-testid="metric-container"] [data-testid="stMetricValue"] { color: #f1f5f9 !important; font-size: 28px !important; font-weight: 700; }
[data-testid="metric-container"] [data-testid="stMetricDelta"] { font-size: 12px !important; }

/* ── Containers / Cards ── */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: #111827 !important;
    border: 1px solid #1e293b !important;
    border-radius: 14px !important;
}

/* ── Buttons ── */
.stButton > button {
    background: #1e293b !important;
    color: #94a3b8 !important;
    border: 1px solid #334155 !important;
    border-radius: 8px !important;
    font-size: 12px !important;
    font-weight: 500 !important;
    transition: all 0.2s;
}
.stButton > button:hover {
    background: #2563eb !important;
    color: #ffffff !important;
    border-color: #2563eb !important;
}

/* ── Divider ── */
hr { border-color: #1e293b !important; }

/* ── Dataframe ── */
[data-testid="stDataFrame"] { border-radius: 10px; overflow: hidden; }

/* ── Headers ── */
h1 { color: #f1f5f9 !important; font-weight: 700 !important; }
h2, h3, h4 { color: #cbd5e1 !important; font-weight: 600 !important; }

/* ── Input fields ── */
input, textarea, select {
    background: #1e293b !important;
    color: #e2e8f0 !important;
    border-color: #334155 !important;
    border-radius: 8px !important;
}

/* ── Progress bar ── */
.stProgress > div > div { border-radius: 10px; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: #111827;
    border-radius: 10px;
    padding: 4px;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    color: #64748b;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 500;
}
.stTabs [aria-selected="true"] {
    background: #2563eb !important;
    color: #ffffff !important;
}

/* ── Toast/Alert ── */
.stAlert { border-radius: 10px !important; }

/* ── Select box ── */
[data-baseweb="select"] > div {
    background: #1e293b !important;
    border-color: #334155 !important;
    border-radius: 8px !important;
    color: #e2e8f0 !important;
}
</style>
""", unsafe_allow_html=True)

# ── Navigation ─────────────────────────────────────────────
home_page      = st.Page("pages/home.py",      title="Command Center", icon="🏛️")
tasks_page     = st.Page("pages/all_tasks.py", title="All Tasks",      icon="📋")
reports_page   = st.Page("pages/reports.py",   title="Reports",        icon="📊")
financials_page = st.Page("pages/financials.py", title="Financials",     icon="💹")
pg = st.navigation([home_page, tasks_page, reports_page, financials_page])
pg.run()
