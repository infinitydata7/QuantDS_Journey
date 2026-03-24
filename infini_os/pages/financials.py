# pages/financials.py
import streamlit as st
import pandas as pd
from utils import (
    fmt, load_mainframe,
    pct_change, pct_change_cost,
    badge, badge_cost, mom_message
)

st.markdown("# 💹 Financial Snapshot")
st.caption("Proprietary Trading Performance · Infini Capital · ₹50Cr AUM")
st.markdown("---")

try:
    df_mf  = load_mainframe()
    months = df_mf.columns.tolist()
    latest = months[-1]
    prev   = months[-2]

    cur_rev   = df_mf.loc["SystemRevenue", latest]
    cur_cost  = df_mf.loc["SystemCost",    latest]
    cur_net   = df_mf.loc["SystemNet",     latest]
    prev_rev  = df_mf.loc["SystemRevenue", prev]
    prev_cost = df_mf.loc["SystemCost",    prev]
    prev_net  = df_mf.loc["SystemNet",     prev]

    cum_rev   = df_mf.loc["SystemRevenue"].sum()
    cum_cost  = df_mf.loc["SystemCost"].sum()
    cum_net   = df_mf.loc["SystemNet"].sum()

    prev_cum_rev  = df_mf.loc["SystemRevenue"][:-1].sum()
    prev_cum_cost = df_mf.loc["SystemCost"][:-1].sum()
    prev_cum_net  = df_mf.loc["SystemNet"][:-1].sum()

    active_rev  = df_mf.loc["SystemRevenue"][df_mf.loc["SystemRevenue"] != 0]
    active_net  = df_mf.loc["SystemNet"][df_mf.loc["SystemNet"] != 0]
    avg_rev     = active_rev.mean() if len(active_rev) > 0 else 0
    avg_net     = active_net.mean() if len(active_net) > 0 else 0

    prev_act_rev = df_mf.loc["SystemRevenue"][:-1]
    prev_act_rev = prev_act_rev[prev_act_rev != 0]
    prev_act_net = df_mf.loc["SystemNet"][:-1]
    prev_act_net = prev_act_net[prev_act_net != 0]
    prev_avg_rev = prev_act_rev.mean() if len(prev_act_rev) > 0 else 0
    prev_avg_net = prev_act_net.mean() if len(prev_act_net) > 0 else 0

    active_months = len(active_rev)
    trading_days  = active_months * 22
    trading_hours = trading_days * 6.5
    rev_per_hour  = cum_rev / trading_hours if trading_hours > 0 else 0
    prev_t_hours  = len(prev_act_rev) * 22 * 6.5
    prev_rph      = prev_cum_rev / prev_t_hours if prev_t_hours > 0 else 0

    rev_chg,  rev_ic,  rev_ar  = pct_change(cur_rev,      prev_rev)
    cost_chg, cost_ic, cost_ar = pct_change_cost(cur_cost, prev_cost)
    net_chg,  net_ic,  net_ar  = pct_change(cur_net,       prev_net)
    cr_chg,   cr_ic,   cr_ar   = pct_change(cum_rev,       prev_cum_rev)
    cc_chg,   cc_ic,   cc_ar   = pct_change_cost(cum_cost, prev_cum_cost)
    cn_chg,   cn_ic,   cn_ar   = pct_change(cum_net,       prev_cum_net)
    ar_chg,   ar_ic,   ar_ar   = pct_change(avg_rev,       prev_avg_rev)
    an_chg,   an_ic,   an_ar   = pct_change(avg_net,       prev_avg_net)
    rph_chg,  rph_ic,  rph_ar  = pct_change(rev_per_hour,  prev_rph)

    last3 = months[-3:]

    # ── Top KPI Bar ───────────────────────────────────────────
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Active Months",  active_months)
    k2.metric("Trading Days",   trading_days)
    k3.metric("Trading Hours",  f"{trading_hours:,.0f}")
    k4.metric("Cum Revenue",    fmt(cum_rev))
    k5.metric("Cum Net P&L",    f"{'🟢' if cum_net >= 0 else '🔴'} {fmt(cum_net)}")

    st.markdown("---")

    tab1, tab2, tab3, tab4 = st.tabs([
        "📅 Current Month",
        "📈 Since Inception",
        "📊 Monthly Table",
        "📉 MoM Analysis"
    ])

    # ── Tab 1: Current Month ──────────────────────────────────
    with tab1:
        st.markdown(f"#### Performance for `{latest}` &nbsp; vs &nbsp; `{prev}`")
        c1, c2, c3 = st.columns(3)
        with c1:
            with st.container(border=True):
                net_color = "#22c55e" if cur_rev >= 0 else "#ef4444"
                st.markdown(f"<div style='color:#64748b;font-size:11px;text-transform:uppercase;letter-spacing:1px'>Revenue</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='font-size:32px;font-weight:700;color:{net_color}'>{fmt(cur_rev)}</div>", unsafe_allow_html=True)
                st.metric("vs prev month", "", delta=badge(rev_chg, rev_ic, rev_ar, cur_rev, prev_rev))
        with c2:
            with st.container(border=True):
                st.markdown(f"<div style='color:#64748b;font-size:11px;text-transform:uppercase;letter-spacing:1px'>Cost</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='font-size:32px;font-weight:700;color:#f59e0b'>{fmt(cur_cost)}</div>", unsafe_allow_html=True)
                st.metric("vs prev month", "", delta=badge_cost(cost_chg, cost_ic, cost_ar, cur_cost, prev_cost))
        with c3:
            with st.container(border=True):
                net_color = "#22c55e" if cur_net >= 0 else "#ef4444"
                st.markdown(f"<div style='color:#64748b;font-size:11px;text-transform:uppercase;letter-spacing:1px'>Net P&L</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='font-size:32px;font-weight:700;color:{net_color}'>{'▲' if cur_net >= 0 else '▼'} {fmt(cur_net)}</div>", unsafe_allow_html=True)
                st.metric("vs prev month", "", delta=badge(net_chg, net_ic, net_ar, cur_net, prev_net))

        st.markdown("---")
        st.markdown("#### ⏱️ Revenue per Trading Hour")
        with st.container(border=True):
            rph_color = "#22c55e" if rev_per_hour >= 0 else "#ef4444"
            r1, r2 = st.columns([2, 3])
            with r1:
                st.markdown(f"<div style='font-size:36px;font-weight:700;color:{rph_color}'>{fmt(rev_per_hour)}<span style='font-size:14px;color:#64748b'> / hr</span></div>", unsafe_allow_html=True)
                st.metric("vs prev period", "", delta=badge(rph_chg, rph_ic, rph_ar, rev_per_hour, prev_rph))
            with r2:
                st.markdown(f"""
                <div style='color:#64748b;font-size:13px;line-height:2'>
                    📅 &nbsp; <b style='color:#e2e8f0'>{active_months}</b> active months<br>
                    📆 &nbsp; <b style='color:#e2e8f0'>{trading_days}</b> trading days &nbsp; (22 days/month)<br>
                    ⏰ &nbsp; <b style='color:#e2e8f0'>{trading_hours:,.0f}</b> total hours &nbsp; (6.5 hrs/day)
                </div>
                """, unsafe_allow_html=True)

    # ── Tab 2: Since Inception ────────────────────────────────
    with tab2:
        st.markdown("#### Cumulative Performance Since Inception")
        c1, c2, c3 = st.columns(3)
        with c1:
            with st.container(border=True):
                st.markdown("<div style='color:#64748b;font-size:11px;text-transform:uppercase;letter-spacing:1px'>Cumulative Revenue</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='font-size:32px;font-weight:700;color:#22c55e'>{fmt(cum_rev)}</div>", unsafe_allow_html=True)
                st.metric("change", "", delta=badge(cr_chg, cr_ic, cr_ar, cum_rev, prev_cum_rev))
        with c2:
            with st.container(border=True):
                st.markdown("<div style='color:#64748b;font-size:11px;text-transform:uppercase;letter-spacing:1px'>Cumulative Cost</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='font-size:32px;font-weight:700;color:#f59e0b'>{fmt(cum_cost)}</div>", unsafe_allow_html=True)
                st.metric("change", "", delta=badge_cost(cc_chg, cc_ic, cc_ar, cum_cost, prev_cum_cost))
        with c3:
            with st.container(border=True):
                cum_net_color = "#22c55e" if cum_net >= 0 else "#ef4444"
                st.markdown("<div style='color:#64748b;font-size:11px;text-transform:uppercase;letter-spacing:1px'>Cumulative Net</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='font-size:32px;font-weight:700;color:{cum_net_color}'>{'▲' if cum_net >= 0 else '▼'} {fmt(cum_net)}</div>", unsafe_allow_html=True)
                st.metric("change", "", delta=badge(cn_chg, cn_ic, cn_ar, cum_net, prev_cum_net))

        st.markdown("---")
        st.markdown("#### 📊 Monthly Averages (Active Months Only)")
        a1, a2 = st.columns(2)
        with a1:
            with st.container(border=True):
                st.markdown("<div style='color:#64748b;font-size:11px;text-transform:uppercase;letter-spacing:1px'>Avg Revenue / Month</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='font-size:28px;font-weight:700;color:#22c55e'>{fmt(avg_rev)}</div>", unsafe_allow_html=True)
                st.metric("change", "", delta=badge(ar_chg, ar_ic, ar_ar, avg_rev, prev_avg_rev))
        with a2:
            with st.container(border=True):
                avg_net_color = "#22c55e" if avg_net >= 0 else "#ef4444"
                st.markdown("<div style='color:#64748b;font-size:11px;text-transform:uppercase;letter-spacing:1px'>Avg Net / Month</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='font-size:28px;font-weight:700;color:{avg_net_color}'>{fmt(avg_net)}</div>", unsafe_allow_html=True)
                st.metric("change", "", delta=badge(an_chg, an_ic, an_ar, avg_net, prev_avg_net))

    # ── Tab 3: Monthly Table ──────────────────────────────────
    with tab3:
        st.markdown("#### Full Monthly P&L History")
        rows = []
        running_rev = 0
        for m in months:
            rev  = df_mf.loc["SystemRevenue", m]
            cost = df_mf.loc["SystemCost",    m]
            net  = df_mf.loc["SystemNet",     m]
            if rev != 0:
                running_rev += rev
            margin = f"{(net/rev*100):.1f}%" if rev != 0 else "—"
            rows.append({
                "Month":       m,
                "Revenue":     fmt(rev),
                "Cost":        fmt(cost),
                "Net P&L":     f"{'🟢' if net >= 0 else '🔴'} {fmt(net)}",
                "Margin":      margin,
                "Cum Revenue": fmt(running_rev),
            })
        st.dataframe(
            pd.DataFrame(rows).set_index("Month"),
            use_container_width=True
        )

        st.markdown("---")
        st.markdown("#### 3-Month Snapshot")
        rows3 = []
        for m in last3:
            rev  = df_mf.loc["SystemRevenue", m]
            cost = df_mf.loc["SystemCost",    m]
            net  = df_mf.loc["SystemNet",     m]
            rows3.append({
                "Month":   m,
                "Revenue": fmt(rev),
                "Cost":    fmt(cost),
                "Net P&L": f"{'🟢' if net >= 0 else '🔴'} {fmt(net)}",
                "Margin":  f"{(net/rev*100):.1f}%" if rev != 0 else "—",
            })
        st.dataframe(pd.DataFrame(rows3).set_index("Month"), use_container_width=True)

    # ── Tab 4: MoM Analysis ───────────────────────────────────
    with tab4:
        st.markdown(f"#### Month-on-Month: `{prev}` → `{latest}`")

        with st.container(border=True):
            st.markdown("**📈 Revenue**")
            st.markdown(f"### {badge(rev_chg, rev_ic, rev_ar, cur_rev, prev_rev)}")
            mom_message(rev_chg, "revenue")

        st.markdown("")

        with st.container(border=True):
            st.markdown("**💸 Cost**")
            st.markdown(f"### {badge_cost(cost_chg, cost_ic, cost_ar, cur_cost, prev_cost)}")

        st.markdown("")

        with st.container(border=True):
            st.markdown("**💰 Net P&L**")
            st.markdown(f"### {badge(net_chg, net_ic, net_ar, cur_net, prev_net)}")
            mom_message(net_chg, "net")

        st.markdown("---")
        st.markdown("#### Rolling 3-Month MoM")
        for i in range(1, len(last3)):
            m_cur  = last3[i]
            m_prev = last3[i - 1]
            r_c = df_mf.loc["SystemRevenue", m_cur];  r_p = df_mf.loc["SystemRevenue", m_prev]
            c_c = df_mf.loc["SystemCost",    m_cur];  c_p = df_mf.loc["SystemCost",    m_prev]
            n_c = df_mf.loc["SystemNet",     m_cur];  n_p = df_mf.loc["SystemNet",     m_prev]
            r_chg, r_ic, r_ar = pct_change(r_c, r_p)
            c_chg, c_ic, c_ar = pct_change_cost(c_c, c_p)
            n_chg, n_ic, n_ar = pct_change(n_c, n_p)
            with st.container(border=True):
                st.markdown(f"**{m_prev} → {m_cur}**")
                st.markdown(
                    f"Revenue: {badge(r_chg, r_ic, r_ar, r_c, r_p)}  \n"
                    f"Cost: {badge_cost(c_chg, c_ic, c_ar, c_c, c_p)}  \n"
                    f"Net: {badge(n_chg, n_ic, n_ar, n_c, n_p)}"
                )

except Exception as e:
    st.error(f"Could not load financial data: {e}")
    st.info("Make sure `mainframe-2.csv` is in the same folder as `app.py`")
