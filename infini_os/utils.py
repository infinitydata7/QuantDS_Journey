# utils.py  — shared helpers
import os, sqlite3
import streamlit as st
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME  = os.path.join(BASE_DIR, "infini_os.db")

def init_db():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS agents (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            name       TEXT NOT NULL,
            role       TEXT,
            department TEXT,
            is_active  INTEGER DEFAULT 1,
            reports_to TEXT,
            created_ts DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS tasks (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            title        TEXT NOT NULL,
            agent_id     INTEGER REFERENCES agents(id),
            description  TEXT,
            due_date     TEXT,
            priority     INTEGER DEFAULT 3,
            status       TEXT DEFAULT 'Not Started',
            created_ts   DATETIME DEFAULT CURRENT_TIMESTAMP,
            completed_ts DATETIME
        );
    """)
    conn.commit()
    conn.close()

def query_db(sql, params=None):
    fresh = sqlite3.connect(DB_NAME, check_same_thread=False)
    fresh.row_factory = sqlite3.Row
    try:
        clean = tuple(p.item() if hasattr(p,"item") else p for p in params) if params else ()
        cur   = fresh.execute(sql, clean)
        cols  = [d[0] for d in cur.description]
        rows  = [dict(r) for r in cur.fetchall()]
        return pd.DataFrame(rows, columns=cols) if rows else pd.DataFrame(columns=cols)
    finally:
        fresh.close()

def write_db(sql, params=None):
    fresh = sqlite3.connect(DB_NAME, check_same_thread=False)
    try:
        clean = tuple(p.item() if hasattr(p,"item") else p for p in params) if params else ()
        fresh.execute(sql, clean)
        fresh.commit()
    finally:
        fresh.close()

def get_agent_kpis():
    sql = """
    SELECT a.id, a.name, a.role, a.department, a.is_active, a.reports_to,
           COUNT(t.id) AS total_tasks,
           COUNT(CASE WHEN t.status='Completed' THEN 1 END) AS completed_tasks
    FROM agents a LEFT JOIN tasks t ON a.id=t.agent_id
    GROUP BY a.id,a.name,a.role,a.department,a.is_active,a.reports_to
    """
    fresh = sqlite3.connect(DB_NAME, check_same_thread=False)
    fresh.row_factory = sqlite3.Row
    try:
        cur  = fresh.execute(sql)
        cols = [d[0] for d in cur.description]
        rows = [dict(r) for r in cur.fetchall()]
        kpis = pd.DataFrame(rows, columns=cols) if rows else pd.DataFrame(columns=cols)
    finally:
        fresh.close()
    kpis["open_tasks"] = kpis["total_tasks"] - kpis["completed_tasks"]
    kpis["pct"]        = kpis.apply(
        lambda r: r["completed_tasks"]/r["total_tasks"] if r["total_tasks"]>0 else 0, axis=1)
    return kpis

def priority_label(p):
    return {1:"🔥 Critical",2:"⬆ High",3:"➡ Medium",4:"⬇ Low",5:"💤 Minimal"}.get(p,f"P{p}")

def status_badge(s):
    return {"Completed":"🟢","In Progress":"🟡","Not Started":"🔴","Blocked":"🔵"}.get(s,"⚪") + f" `{s}`"

def fmt(val):
    if pd.isna(val): return "₹0"
    if abs(val)>=1_00_000: return f"₹{val/1_00_000:.2f}L"
    if abs(val)>=1_000:    return f"₹{val/1_000:.1f}K"
    return f"₹{val:.0f}"

def load_mainframe():
    path = os.path.join(BASE_DIR, "mainframe-2.csv")
    df   = pd.read_csv(path, index_col=0)
    df   = df.loc[:, ~df.columns.str.contains("^Unnamed")]
    df   = df.loc[:, df.columns.str.strip()!=""]
    return df.apply(pd.to_numeric, errors="coerce")

def pct_change(cur, prev):
    if prev==0: return 0.0,"⚪",""
    chg = ((cur-prev)/abs(prev))*100
    return chg, ("🟢" if chg>=0 else "🔴"), ("▲" if chg>=0 else "▼")

def pct_change_cost(cur, prev):
    if prev==0: return 0.0,"⚪",""
    chg = ((cur-prev)/abs(prev))*100
    return chg, ("🔴" if chg>=0 else "🟢"), ("▲" if chg>=0 else "▼")

def badge(chg, icon, arrow, cur, prev):
    actual = cur-prev
    return f"{icon} {arrow} {abs(chg):.1f}%  |  {'+' if actual>=0 else ''}{fmt(actual)}"

def badge_cost(chg, icon, arrow, cur, prev):
    actual = cur-prev
    return f"{icon} {arrow} {abs(chg):.1f}%  |  {'+' if actual>=0 else ''}{fmt(actual)}"

def mom_message(chg, label=""):
    if chg>=10:   st.success(f"Strong {label} improvement! 🚀")
    elif chg>=0:  st.info(f"Slight {label} improvement.")
    elif chg>=-10:st.warning(f"Slight {label} decline.")
    else:         st.error(f"Significant {label} decline. ⚠️")

def seed_db():
    """Pre-populate default agents if table is empty."""
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    count = conn.execute("SELECT COUNT(*) FROM agents").fetchone()[0]
    if count == 0:  # only seed if empty
        conn.executescript("""
            INSERT INTO agents (name, role, department, is_active, reports_to) VALUES
                ('CEO',  'Chief Executive Officer',     'Strategy',      1, 'CEO'),
                ('CFO',  'Chief Financial Officer',     'Finance',       1, 'CFO'),
                ('CDS',  'Chief Data Scientist',        'Quantitative',  1, 'CDS');
        """)
        conn.commit()
    conn.close()

# === Last lines of utils.py ===
init_db()   # create tables if missing
seed_db()   # populate default agents if empty