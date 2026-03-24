# pages/all_tasks.py
import streamlit as st
import pandas as pd
from datetime import date
from utils import query_db, write_db, priority_label, status_badge

st.markdown("# 📋 All Tasks")
st.caption("Complete task registry across all agents · Infini Capital")
st.markdown("---")

tasks = query_db("""
    SELECT t.id, a.name AS agent, a.department,
           t.title, t.due_date, t.priority, t.status, t.description
    FROM tasks t
    JOIN agents a ON t.agent_id = a.id
    ORDER BY t.due_date ASC
""")

if len(tasks) == 0:
    st.info("No tasks found.")
    st.stop()

today = date.today()
tasks["due_date_parsed"] = pd.to_datetime(tasks["due_date"], errors="coerce").dt.date
tasks["overdue"] = (
    (tasks["status"] != "Completed") &
    (tasks["due_date_parsed"] < today)
)
tasks["due_today"] = (
    (tasks["status"] != "Completed") &
    (tasks["due_date_parsed"] == today)
)

# ── Filters ──────────────────────────────────────────────────
f1, f2, f3, f4 = st.columns(4)
agents      = ["All"] + sorted(tasks["agent"].unique().tolist())
departments = ["All"] + sorted(tasks["department"].unique().tolist())
statuses    = ["All", "Not Started", "In Progress", "Completed"]

sel_agent  = f1.selectbox("Agent",      agents)
sel_dept   = f2.selectbox("Department", departments)
sel_status = f3.selectbox("Status",     statuses)
sel_overdue= f4.selectbox("Due Filter", ["All", "Overdue", "Due Today", "Upcoming"])

df = tasks.copy()
if sel_agent  != "All": df = df[df["agent"]  == sel_agent]
if sel_dept   != "All": df = df[df["department"] == sel_dept]
if sel_status != "All": df = df[df["status"] == sel_status]
if sel_overdue == "Overdue":   df = df[df["overdue"]]
elif sel_overdue == "Due Today": df = df[df["due_today"]]
elif sel_overdue == "Upcoming":  df = df[(~df["overdue"]) & (~df["due_today"]) & (df["status"]!="Completed")]

# ── Summary metrics ──────────────────────────────────────────
m1,m2,m3,m4 = st.columns(4)
m1.metric("Showing",    len(df))
m2.metric("🔴 Open",    len(df[df["status"]!="Completed"]))
m3.metric("🟢 Closed",  len(df[df["status"]=="Completed"]))
m4.metric("🚨 Overdue", len(df[df["overdue"]]))

st.markdown("---")

# ── Export ───────────────────────────────────────────────────
export_df = df[["agent","department","title","due_date","priority","status","description"]].copy()
export_df["priority"] = export_df["priority"].apply(lambda x: priority_label(int(x)))
st.download_button(
    "⬇️ Export to CSV",
    export_df.to_csv(index=False).encode("utf-8"),
    file_name=f"infini_tasks_{today}.csv",
    mime="text/csv",
)

st.markdown("---")

# ── Task List ────────────────────────────────────────────────
for _, task in df.iterrows():
    is_overdue  = task["overdue"]
    is_today    = task["due_today"]
    border      = "#ef4444" if is_overdue else "#eab308" if is_today else "#1e293b"

    with st.container(border=True):
        st.markdown(f"<div style='border-left:3px solid {border};padding-left:10px'>", unsafe_allow_html=True)
        ca, cb, cc = st.columns([3, 1, 1])
        with ca:
            st.markdown(f"**{task['title']}**")
            if task["description"]:
                st.caption(task["description"])
            due_label = f"📅 `{task['due_date']}`"
            if is_overdue:  due_label += " 🚨 **OVERDUE**"
            elif is_today:  due_label += " ⚡ **TODAY**"
            st.write(f"{due_label} &nbsp; {priority_label(int(task['priority']))} &nbsp; {status_badge(task['status'])}")
        with cb:
            st.markdown(f"<div style='color:#64748b;font-size:12px;padding-top:4px'>🤖 {task['agent']}<br>🏢 {task['department']}</div>", unsafe_allow_html=True)
        with cc:
            lbl = "✅ Close" if task["status"] != "Completed" else "↩ Reopen"
            if st.button(lbl, key=f"at_done_{task['id']}"):
                new_s = "Completed" if task["status"] != "Completed" else "In Progress"
                write_db("UPDATE tasks SET status=?, completed_ts=CURRENT_TIMESTAMP WHERE id=?",
                         [new_s, int(task["id"])])
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
