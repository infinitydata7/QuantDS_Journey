# pages/home.py
import os, sqlite3
import streamlit as st
import pandas as pd
from datetime import datetime, date
from utils import (
    DB_NAME, query_db, write_db, get_agent_kpis,
    priority_label, status_badge, fmt,
    pct_change, pct_change_cost, badge, badge_cost,
    mom_message, load_mainframe
)

# ── Header ──────────────────────────────────────────────────
col_logo, col_title, col_time = st.columns([1, 6, 2])
with col_logo:
    st.markdown("## 💹")
with col_title:
    st.markdown("# Infini Capital")
    st.caption("Quantitative Proprietary Trading · ₹50Cr AUM · Command Center")
with col_time:
    st.markdown(f"<div style='text-align:right;color:#64748b;font-size:12px;padding-top:20px'>{datetime.now().strftime('%A, %d %b %Y  %H:%M')}</div>", unsafe_allow_html=True)

st.markdown("---")

# ── KPI Bar ────────────────────────────────────────────────
kpis           = get_agent_kpis()
overall_total  = int(kpis["total_tasks"].sum())
overall_closed = int(kpis["completed_tasks"].sum())
overall_open   = int(kpis["open_tasks"].sum())
overall_pct    = 0 if overall_total == 0 else overall_closed / overall_total

# Overdue count
today = date.today()
all_tasks = query_db("SELECT due_date, status FROM tasks")
if len(all_tasks) > 0:
    all_tasks["due_date"] = pd.to_datetime(all_tasks["due_date"], errors="coerce").dt.date
    overdue = len(all_tasks[
        (all_tasks["status"] != "Completed") &
        (all_tasks["due_date"] < today)
    ])
else:
    overdue = 0

m1, m2, m3, m4, m5, m6 = st.columns(6)
m1.metric("🏦 AUM",             "₹50 Cr")
m2.metric("📋 Total Tasks",     overall_total)
m3.metric("🟢 Closed",          overall_closed)
m4.metric("🔴 Open",            overall_open)
m5.metric("⚠️ Overdue",         overdue,  delta=f"{'Critical' if overdue > 0 else 'Clear'}", delta_color="inverse" if overdue > 0 else "normal")
m6.metric("✅ Completion",      f"{overall_pct:.0%}")

st.markdown("---")

# ── Dialogs ─────────────────────────────────────────────────
@st.dialog("👤 Add New Agent")
def add_agent_dialog():
    st.markdown("#### Add Agent to Org Chart")
    name       = st.text_input("Agent Name")
    role       = st.text_input("Role")
    reports_to = st.selectbox("Reports To", ["CEO", "CFO", "CDS"])
    dept_map   = {"CEO": "Strategy", "CFO": "Finance", "CDS": "Quantitative"}
    department = st.text_input("Department", value=dept_map[reports_to])
    is_active  = st.toggle("Active", value=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Add Agent", use_container_width=True):
            if name.strip():
                write_db(
                    "INSERT INTO agents (name, role, department, is_active, reports_to) VALUES (?,?,?,?,?)",
                    [name.strip(), role.strip(), department.strip(), int(is_active), reports_to]
                )
                st.success(f"✅ {name} added!")
                st.rerun()
    with col2:
        if st.button("✖ Cancel", use_container_width=True):
            st.rerun()

@st.dialog("➕ Quick Add Task")
def add_task_dialog(agent_id, agent_name):
    st.markdown(f"#### Task for **{agent_name}**")
    title       = st.text_input("Task Title")
    due_date    = st.date_input("Due Date", value=datetime.now().date())
    priority    = st.selectbox("Priority", [1,2,3,4,5], format_func=priority_label, index=2)
    description = st.text_area("Description (optional)", height=80)
    col1, col2  = st.columns(2)
    with col1:
        if st.button("✅ Add Task", use_container_width=True):
            if title.strip():
                write_db(
                    "INSERT INTO tasks (title, agent_id, description, due_date, priority, status) VALUES (?,?,?,?,?,'Not Started')",
                    [title, int(agent_id), description, str(due_date), int(priority)]
                )
                st.success(f"✅ '{title}' added!")
                st.rerun()
    with col2:
        if st.button("✖ Cancel", use_container_width=True):
            st.rerun()

@st.dialog("📋 View Tasks", width="large")
def view_tasks_dialog(agent_id, agent_name, agent_role):
    st.markdown(f"### 🤖 {agent_name} &nbsp; <span style='color:#64748b;font-size:14px'>{agent_role}</span>", unsafe_allow_html=True)

    tasks = query_db(
        "SELECT id, title, description, due_date, priority, status FROM tasks WHERE agent_id=? ORDER BY due_date",
        params=[int(agent_id)]
    )

    completed = len(tasks[tasks["status"]=="Completed"])         if len(tasks)>0 else 0
    in_prog   = len(tasks[tasks["status"]=="In Progress"])       if len(tasks)>0 else 0
    not_start = len(tasks[tasks["status"]=="Not Started"])       if len(tasks)>0 else 0
    open_c    = len(tasks) - completed

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Total",         len(tasks))
    c2.metric("🔴 Open",       open_c)
    c3.metric("🟡 In Progress",in_prog)
    c4.metric("🟢 Closed",     completed)

    # Progress bar
    pct = completed/len(tasks) if len(tasks)>0 else 0
    color = "#22c55e" if pct==1 else "#eab308" if pct>=0.5 else "#ef4444"
    st.markdown(f"""
    <div style='background:#1e293b;border-radius:8px;height:8px;margin:8px 0'>
        <div style='background:{color};width:{pct*100:.0f}%;height:8px;border-radius:8px;transition:width 0.3s'></div>
    </div>
    <div style='color:{color};font-size:12px;text-align:right'>{pct:.0%} closed</div>
    """, unsafe_allow_html=True)

    # Filter tabs
    tab_all, tab_open, tab_done = st.tabs(["All", "Open", "Closed"])

    def render_tasks(task_df):
        if len(task_df)==0:
            st.info("No tasks here.")
            return
        for _, task in task_df.iterrows():
            due   = pd.to_datetime(task["due_date"]).date() if task["due_date"] else None
            is_overdue = due and due < today and task["status"] != "Completed"
            is_today   = due and due == today and task["status"] != "Completed"
            border_color = "#ef4444" if is_overdue else "#eab308" if is_today else "#1e293b"
            with st.container(border=True):
                st.markdown(f"<div style='border-left:3px solid {border_color};padding-left:8px'>", unsafe_allow_html=True)
                col_a, col_b = st.columns([4,1])
                with col_a:
                    st.markdown(f"**{task['title']}**")
                    if task["description"]:
                        st.caption(task["description"])
                    due_str = f"📅 `{task['due_date']}`"
                    if is_overdue:
                        due_str += " 🚨 **OVERDUE**"
                    elif is_today:
                        due_str += " ⚡ **DUE TODAY**"
                    st.write(f"{due_str}  {priority_label(int(task['priority']))}  {status_badge(task['status'])}")
                with col_b:
                    lbl = "✅ Close" if task["status"]!="Completed" else "↩ Reopen"
                    if st.button(lbl, key=f"done_{task['id']}_{task['status']}"):
                        new_s = "Completed" if task["status"]!="Completed" else "In Progress"
                        write_db("UPDATE tasks SET status=?, completed_ts=CURRENT_TIMESTAMP WHERE id=?",
                                 [new_s, int(task["id"])])
                        st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

    with tab_all:
        render_tasks(tasks)
    with tab_open:
        render_tasks(tasks[tasks["status"]!="Completed"])
    with tab_done:
        render_tasks(tasks[tasks["status"]=="Completed"])

    st.divider()
    st.markdown("#### ➕ Add Task")
    with st.form(f"add_{agent_id}"):
        s_title = st.text_input("Task Title")
        c1, c2  = st.columns(2)
        s_due   = c1.date_input("Due Date", value=datetime.now().date())
        s_pri   = c2.selectbox("Priority", [1,2,3,4,5], format_func=priority_label, index=2)
        s_desc  = st.text_area("Description", height=60)
        if st.form_submit_button("Add Task", use_container_width=True):
            if s_title.strip():
                write_db(
                    "INSERT INTO tasks (title, agent_id, description, due_date, priority, status) VALUES (?,?,?,?,?,'Not Started')",
                    [s_title, int(agent_id), s_desc, str(s_due), int(s_pri)]
                )
                st.success(f"✅ '{s_title}' added!")
                st.rerun()

# ── Agent Card ──────────────────────────────────────────────
def agent_card(row, col):
    total     = int(row["total_tasks"])
    completed = int(row["completed_tasks"])
    open_t    = int(row["open_tasks"])
    pct       = float(row["pct"])
    agent_id  = int(row["id"])

    # overdue for this agent
    if total > 0:
        ag_tasks = query_db(
            "SELECT due_date, status FROM tasks WHERE agent_id=?",
            params=[agent_id]
        )
        ag_tasks["due_date"] = pd.to_datetime(ag_tasks["due_date"], errors="coerce").dt.date
        ag_overdue = len(ag_tasks[
            (ag_tasks["status"]!="Completed") &
            (ag_tasks["due_date"] < today)
        ])
    else:
        ag_overdue = 0

    color = "#22c55e" if pct==1 else "#eab308" if pct>=0.5 else "#ef4444" if total>0 else "#475569"
    pct_int = int(pct*100)

    with col:
        with st.container(border=True):
            # Name row
            hcol1, hcol2 = st.columns([3,1])
            with hcol1:
                st.markdown(f"**{row['name']}**")
                st.caption(f"{row['role']} · {row['department']}")
            with hcol2:
                if ag_overdue > 0:
                    st.markdown(f"<div style='color:#ef4444;font-size:11px;text-align:right'>🚨 {ag_overdue} overdue</div>", unsafe_allow_html=True)
                active_icon = "🟢" if row["is_active"] else "🔴"
                st.markdown(f"<div style='text-align:right;font-size:11px;color:#64748b'>{active_icon} {'Active' if row['is_active'] else 'Inactive'}</div>", unsafe_allow_html=True)

            # Stats
            st.markdown(
                f"<div style='display:flex;gap:16px;margin:6px 0'>"
                f"<span style='color:#64748b;font-size:12px'>Open <b style='color:#ef4444'>{open_t}</b></span>"
                f"<span style='color:#64748b;font-size:12px'>Closed <b style='color:#22c55e'>{completed}</b></span>"
                f"<span style='color:#64748b;font-size:12px'>Total <b style='color:#e2e8f0'>{total}</b></span>"
                f"</div>", unsafe_allow_html=True
            )

            # Progress bar
            st.markdown(f"""
            <div style='background:#1e293b;border-radius:6px;height:6px;margin:4px 0'>
                <div style='background:{color};width:{pct_int}%;height:6px;border-radius:6px'></div>
            </div>
            <div style='color:{color};font-size:11px;text-align:right;margin-bottom:8px'>{pct_int}% closed</div>
            """, unsafe_allow_html=True)

            # Buttons
            b1, b2 = st.columns(2)
            with b1:
                open_badge = f" ({open_t})" if open_t > 0 else ""
                   # Change the 2 buttons at the bottom:
    if st.button(f"📋 Tasks{open_badge}", key=f"view_{agent_id}_{context}", use_container_width=True):
        view_tasks_dialog(agent_id, str(row["name"]), str(row["role"]))
    if st.button("➕ Add", key=f"add_{agent_id}_{context}", use_container_width=True):
        add_task_dialog(agent_id, str(row["name"]))

# ── Org Chart ───────────────────────────────────────────────
hdr1, hdr2 = st.columns([5,1])
with hdr1:
    st.markdown("### 🏢 Command Structure")
with hdr2:
    if st.button("👤 Add Agent", use_container_width=True):
        add_agent_dialog()

def org_col(title, name, col):
    with col:
        st.markdown(f"##### {title}")
        rows = kpis[kpis["name"] == name]
        if len(rows) > 0:
            agent_card(rows.iloc[0], col, context=f"head_{name}")   # ← context
        reports = kpis[kpis["reports_to"] == name]
        if not reports.empty:
            st.markdown(...)
            for _, r in reports.iterrows():
                agent_card(r, col, context=f"report_{name}_{r['id']}")
c1, c2, c3 = st.columns(3)
org_col("👔 Chief Executive",   "CEO", c1)
org_col("💰 Chief Financial",   "CFO", c2)
org_col("🔬 Chief Data Sci",    "CDS", c3)

st.markdown("---")

# ── Infini Capital Stats ─────────────────────────────────────
with st.container(border=True):
    ic1, ic2 = st.columns([5,1])
    with ic1:
        st.markdown("### 💹 Infini Capital · Financial Snapshot")
        st.caption("Proprietary Quantitative Trading · Est. 2024")
    with ic2:
        if st.button("📊 View Stats", use_container_width=True):
            st.session_state.show_infini_sidebar = True

with st.container(border=True):
    col_ic1, col_ic2 = st.columns([5, 1])
    with col_ic1:
        st.markdown("### 💹 Infini Capital")
        st.caption("Prop Trading Firm · ₹50Cr AUM · Navigate to Financials for full stats →")
    with col_ic2:
        if st.button("💹 Financials", use_container_width=True):
            st.switch_page("pages/financials.py")