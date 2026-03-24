# pages/reports.py
import streamlit as st
import pandas as pd
from datetime import date
from utils import query_db, fmt, load_mainframe, pct_change, pct_change_cost, badge, badge_cost

st.markdown("# 📊 Reports & Analytics")
st.caption("Performance intelligence · Infini Capital Quantitative Research")
st.markdown("---")

tasks = query_db("""
    SELECT t.id, a.name AS agent, a.department,
           t.title, t.due_date, t.priority, t.status,
           t.created_ts, t.completed_ts
    FROM tasks t JOIN agents a ON t.agent_id = a.id
""")

today = date.today()

if len(tasks) > 0:
    tasks["due_date_parsed"]   = pd.to_datetime(tasks["due_date"],   errors="coerce").dt.date
    tasks["created_dt"]        = pd.to_datetime(tasks["created_ts"], errors="coerce")
    tasks["completed_dt"]      = pd.to_datetime(tasks["completed_ts"],errors="coerce")
    tasks["is_overdue"]        = (tasks["status"]!="Completed") & (tasks["due_date_parsed"] < today)
    tasks["is_closed"]         = tasks["status"] == "Completed"

    tab1, tab2, tab3 = st.tabs(["📋 Task Analytics", "👥 Agent Leaderboard", "💹 Financials"])

    with tab1:
        st.markdown("#### Task Distribution")
        r1, r2, r3, r4, r5 = st.columns(5)
        r1.metric("Total",     len(tasks))
        r2.metric("🟢 Closed", int(tasks["is_closed"].sum()))
        r3.metric("🔴 Open",   int((~tasks["is_closed"]).sum()))
        r4.metric("🚨 Overdue",int(tasks["is_overdue"].sum()))
        r5.metric("✅ Rate",   f"{tasks['is_closed'].mean():.0%}")

        st.markdown("---")
        st.markdown("#### By Department")
        dept_grp = tasks.groupby("department").agg(
            Total    = ("id",        "count"),
            Closed   = ("is_closed", "sum"),
            Overdue  = ("is_overdue","sum"),
        ).reset_index()
        dept_grp["Completion"] = (dept_grp["Closed"]/dept_grp["Total"]).apply(lambda x: f"{x:.0%}")
        dept_grp["Open"]       = dept_grp["Total"] - dept_grp["Closed"]
        st.dataframe(dept_grp[["department","Total","Closed","Open","Overdue","Completion"]],
                     use_container_width=True, hide_index=True)

        st.markdown("---")
        st.markdown("#### By Priority")
        from utils import priority_label
        pri_grp = tasks.groupby("priority").agg(
            Total  = ("id","count"),
            Closed = ("is_closed","sum"),
        ).reset_index()
        pri_grp["Priority"]   = pri_grp["priority"].apply(lambda x: priority_label(int(x)))
        pri_grp["Open"]       = pri_grp["Total"] - pri_grp["Closed"]
        pri_grp["Completion"] = (pri_grp["Closed"]/pri_grp["Total"]).apply(lambda x: f"{x:.0%}")
        st.dataframe(pri_grp[["Priority","Total","Closed","Open","Completion"]],
                     use_container_width=True, hide_index=True)

    with tab2:
        st.markdown("#### Agent Leaderboard")
        agent_grp = tasks.groupby("agent").agg(
            Total   = ("id",        "count"),
            Closed  = ("is_closed", "sum"),
            Overdue = ("is_overdue","sum"),
        ).reset_index()
        agent_grp["Open"]        = agent_grp["Total"] - agent_grp["Closed"]
        agent_grp["Completion %"]= (agent_grp["Closed"]/agent_grp["Total"]*100).round(1)
        agent_grp = agent_grp.sort_values("Completion %", ascending=False).reset_index(drop=True)
        agent_grp.index += 1

        for i, row in agent_grp.iterrows():
            pct   = row["Completion %"] / 100
            color = "#22c55e" if pct==1 else "#eab308" if pct>=0.5 else "#ef4444"
            with st.container(border=True):
                c1, c2, c3, c4 = st.columns([3,1,1,1])
                c1.markdown(f"**#{i} {row['agent']}**")
                c2.metric("Closed", int(row["Closed"]))
                c3.metric("Open",   int(row["Open"]))
                c4.metric("Overdue",int(row["Overdue"]))
                st.markdown(f"""
                <div style='background:#1e293b;border-radius:6px;height:6px;margin:4px 0'>
                    <div style='background:{color};width:{row["Completion %"]}%;height:6px;border-radius:6px'></div>
                </div>
                <div style='color:{color};font-size:11px;text-align:right'>{row["Completion %"]:.1f}%</div>
                """, unsafe_allow_html=True)

    with tab3:
        try:
            df_mf  = load_mainframe()
            months = df_mf.columns.tolist()

            st.markdown("#### Monthly P&L Summary")
            rows = []
            for m in months:
                rev  = df_mf.loc["SystemRevenue", m]
                cost = df_mf.loc["SystemCost",    m]
                net  = df_mf.loc["SystemNet",     m]
                rows.append({
                    "Month":   m,
                    "Revenue": fmt(rev),
                    "Cost":    fmt(cost),
                    "Net P&L": f"{'🟢' if net>=0 else '🔴'} {fmt(net)}",
                    "Margin":  f"{(net/rev*100):.1f}%" if rev!=0 else "—",
                })
            st.dataframe(pd.DataFrame(rows).set_index("Month"),
                         use_container_width=True)

            st.markdown("---")
            cum_rev  = df_mf.loc["SystemRevenue"].sum()
            cum_cost = df_mf.loc["SystemCost"].sum()
            cum_net  = df_mf.loc["SystemNet"].sum()
            active   = len(df_mf.loc["SystemRevenue"][df_mf.loc["SystemRevenue"]!=0])
            t_hrs    = active * 22 * 6.5

            st.markdown("#### Inception Summary")
            s1,s2,s3,s4 = st.columns(4)
            s1.metric("Cum Revenue", fmt(cum_rev))
            s2.metric("Cum Cost",    fmt(cum_cost))
            s3.metric("Cum Net",     fmt(cum_net))
            s4.metric("Rev/Hour",    fmt(cum_rev/t_hrs if t_hrs>0 else 0))

        except Exception as e:
            st.error(f"Could not load financials: {e}")

else:
    st.info("No task data available yet.")
