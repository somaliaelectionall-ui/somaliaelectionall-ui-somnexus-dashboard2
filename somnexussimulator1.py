import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

st.set_page_config(
    page_title="SomNexus Agent & Ecosystem Profit Simulator",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("💸 SomNexus Agent & Ecosystem Profit Simulator")
st.caption("Full-stack simulation: Digital + Cashout • Agent + Company Profit • Scenario Planning")

# ── SIDEBAR ──────────────────────────────────────────────────────────────────

st.sidebar.header("Global Company Economics")
fixed_cost        = st.sidebar.number_input("Monthly Fixed Cost (USD)", 10000, 200000, 40000, 1000)
digital_margin_bps = st.sidebar.slider("Digital Net Margin (bps)", 30, 120, 60, 5)
cashout_margin_bps = st.sidebar.slider("Gross Cashout Margin (bps)", 50, 300, 150, 5)
avg_incentive     = st.sidebar.slider("Avg Incentive / Digital Tx (USD)", 0.0, 2.0, 0.6, 0.05)

st.sidebar.header("Transaction Mix")
monthly_volume = st.sidebar.number_input("Total Monthly Volume (USD)", 100000, 50000000, 10000000, 100000)
digital_pct    = st.sidebar.slider("Digital % of Volume", 0, 100, 60, 1)
cashout_pct    = 100 - digital_pct

st.sidebar.header("Agent Model (Cashout)")
agent_count      = st.sidebar.number_input("Active Agents", 100, 20000, 1200, 100)
tx_per_agent_day = st.sidebar.slider("Transfers per Agent per Day", 1, 50, 5)
avg_tx_size      = st.sidebar.number_input("Avg Cashout Tx Size (USD)", 10, 1000, 100, 10)
agent_commission = st.sidebar.slider("Agent Commission % per Tx", 0.0, 2.5, 1.0, 0.1)
agent_oper_cost  = st.sidebar.slider("Agent Monthly Operating Cost (USD)", 0, 2000, 300, 50)

st.sidebar.header("Trade-off Simulation Range")
comm_range = st.sidebar.slider("Commission Range to Simulate (%)", 0.0, 3.0, (0.3, 2.0), 0.1)

st.sidebar.header("Scenario Controls")
growth_pct    = st.sidebar.slider("Next-Month Volume Growth %", -30, 200, 40, 5)
digital_boost = st.sidebar.slider("Digital Adoption Boost (pp)", -20, 40, 10, 2)
agent_scale   = st.sidebar.slider("Agent Scale Factor (Best case)", 0.5, 5.0, 1.5, 0.1)

# ── CORE CALCULATIONS ─────────────────────────────────────────────────────────

digital_margin  = digital_margin_bps  / 10000
cashout_margin  = cashout_margin_bps  / 10000
agent_take_rate = agent_commission    / 100
net_cash_margin = max(0, cashout_margin - agent_take_rate)

digital_volume  = monthly_volume * (digital_pct / 100)
cashout_volume  = monthly_volume - digital_volume

digital_revenue = digital_volume  * digital_margin
cashout_revenue = cashout_volume  * net_cash_margin
total_revenue   = digital_revenue + cashout_revenue

digital_tx_count  = digital_volume / max(10, avg_tx_size)
total_incentives  = digital_tx_count * avg_incentive

net_profit_company = total_revenue - total_incentives - fixed_cost

blended_margin = (digital_pct/100 * digital_margin) + (cashout_pct/100 * net_cash_margin)
breakeven_vol  = fixed_cost / blended_margin if blended_margin > 0 else float("nan")

# Agent economics
days_per_month       = 26
agent_tx_month       = tx_per_agent_day * days_per_month
agent_rev_per_tx     = avg_tx_size * agent_take_rate
agent_monthly_rev    = agent_tx_month * agent_rev_per_tx
agent_monthly_profit = agent_monthly_rev - agent_oper_cost
agent_roi            = (agent_monthly_profit / agent_oper_cost * 100) if agent_oper_cost > 0 else 999
breakeven_tx_day     = (agent_oper_cost / (avg_tx_size * agent_take_rate * days_per_month)) if agent_take_rate > 0 else 0
daily_take_home      = agent_monthly_profit / days_per_month

total_agent_pool     = agent_monthly_profit * agent_count
total_network_vol    = agent_tx_month * avg_tx_size * agent_count

# ── KPI DASHBOARD ─────────────────────────────────────────────────────────────

st.subheader("Company Overview")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Monthly Volume",      f"${monthly_volume:,.0f}")
c2.metric("Digital Revenue",     f"${digital_revenue:,.0f}")
c3.metric("Cashout Revenue",     f"${cashout_revenue:,.0f}")
c4.metric("Company Net Profit",  f"${net_profit_company:,.0f}",
          delta=("Profitable" if net_profit_company > 0 else "Loss"))

c5, c6, c7, c8 = st.columns(4)
c5.metric("Break-even Volume",   f"${breakeven_vol:,.0f}" if not np.isnan(breakeven_vol) else "N/A")
c6.metric("Total Incentive Cost",f"${total_incentives:,.0f}")
c7.metric("Blended Margin (bps)",f"{blended_margin*10000:.0f}")
c8.metric("Rev per Agent",       f"${total_revenue/agent_count:,.0f}" if agent_count > 0 else "—")

st.markdown("---")
st.subheader("Agent Cashout Income")

a1, a2, a3, a4 = st.columns(4)
a1.metric("Tx / Agent / Month",  f"{agent_tx_month:,}")
a2.metric("Agent Revenue / Mo",  f"${agent_monthly_rev:,.0f}")
a3.metric("Agent Profit / Mo",   f"${agent_monthly_profit:,.0f}",
          delta=f"{agent_roi:.0f}% ROI")
a4.metric("Daily Take-home",     f"${daily_take_home:,.0f}")

a5, a6, a7, a8 = st.columns(4)
a5.metric("Break-even Tx / Day", f"{breakeven_tx_day:.1f}")
a6.metric("Active Agents",       f"{agent_count:,}")
a7.metric("Total Agent Pool",    f"${total_agent_pool:,.0f}")
a8.metric("Total Network Vol",   f"${total_network_vol:,.0f}")

st.markdown("---")

# ── SECTION 1: Agent Profit Curve ─────────────────────────────────────────────

st.subheader("Agent Profit vs Daily Transfers")
tx_range = np.arange(1, 41, 1)
agent_curve = pd.DataFrame({
    "Tx per Day": tx_range,
    "Monthly Profit (USD)": tx_range * days_per_month * avg_tx_size * agent_take_rate - agent_oper_cost
})
line_agent = alt.Chart(agent_curve).mark_line(point=True, color="#1D9E75").encode(
    x=alt.X("Tx per Day:Q"),
    y=alt.Y("Monthly Profit (USD):Q"),
    tooltip=["Tx per Day", "Monthly Profit (USD)"]
) + alt.Chart(pd.DataFrame({"y": [0]})).mark_rule(color="#E24B4A", strokeDash=[5, 3]).encode(y="y:Q")
st.altair_chart(line_agent, use_container_width=True)

# ── SECTION 2: Sample Agent Distribution ─────────────────────────────────────

st.subheader("Sample Agent Income Distribution (10 Agents)")
rng = np.random.default_rng(42)
multipliers = rng.normal(1.0, 0.18, 10)
agent_df = pd.DataFrame({
    "Agent": [f"Agent {i+1}" for i in range(10)],
    "Tx/Month": (agent_tx_month * multipliers).astype(int)
})
agent_df["Revenue"]    = agent_df["Tx/Month"] * agent_rev_per_tx
agent_df["Profit"]     = agent_df["Revenue"] - agent_oper_cost
agent_df["Profitable"] = agent_df["Profit"] > 0
st.dataframe(
    agent_df.style.format({"Revenue": "${:,.0f}", "Profit": "${:,.0f}"}),
    use_container_width=True
)

st.markdown("---")

# ── SECTION 3: Company Profit vs Digital % ───────────────────────────────────

st.subheader("Company Profit Sensitivity — Digital Adoption %")
dig_range = np.arange(0, 101, 5)
profits = []
for d in dig_range:
    dv = monthly_volume * (d / 100)
    cv = monthly_volume - dv
    dr = dv * digital_margin
    cr = cv * net_cash_margin
    inc = (dv / max(10, avg_tx_size)) * avg_incentive
    profits.append(dr + cr - inc - fixed_cost)

sens_df = pd.DataFrame({"Digital %": dig_range, "Company Net Profit": profits})
line_sens = alt.Chart(sens_df).mark_line(point=True, color="#378ADD").encode(
    x="Digital %:Q",
    y=alt.Y("Company Net Profit:Q", title="Net Profit (USD)"),
    tooltip=["Digital %", "Company Net Profit"]
) + alt.Chart(pd.DataFrame({"y": [0]})).mark_rule(color="#E24B4A", strokeDash=[5, 3]).encode(y="y:Q")
st.altair_chart(line_sens, use_container_width=True)

st.markdown("---")

# ── SECTION 4: Trade-off Engine ───────────────────────────────────────────────

st.subheader("Trade-off Engine — Agent Commission vs Company Profit")
comm_vals = np.arange(comm_range[0], comm_range[1] + 0.01, 0.1)
records = []
for c in comm_vals:
    c_rate = c / 100
    ag_rev   = tx_per_agent_day * days_per_month * avg_tx_size * c_rate
    ag_prof  = ag_rev - agent_oper_cost
    net_cm   = max(0, cashout_margin - c_rate)
    co_cash  = cashout_volume * net_cm
    co_total = digital_revenue + co_cash
    co_prof  = co_total - total_incentives - fixed_cost
    records.append({
        "Commission %": round(c, 2),
        "Avg Agent Profit": round(ag_prof, 2),
        "Company Net Profit": round(co_prof, 2),
        "Both Profitable": int(ag_prof > 0 and co_prof > 0)
    })

trade_df = pd.DataFrame(records)
melted = trade_df.melt("Commission %", ["Avg Agent Profit", "Company Net Profit"],
                        var_name="Party", value_name="Profit (USD)")

color_scale = alt.Scale(domain=["Avg Agent Profit", "Company Net Profit"],
                         range=["#1D9E75", "#378ADD"])
tradeoff_chart = alt.Chart(melted).mark_line(point=True).encode(
    x=alt.X("Commission %:Q"),
    y=alt.Y("Profit (USD):Q"),
    color=alt.Color("Party:N", scale=color_scale),
    tooltip=["Commission %", "Party", "Profit (USD)"]
) + alt.Chart(pd.DataFrame({"y": [0]})).mark_rule(color="#E24B4A", strokeDash=[5, 3]).encode(y="y:Q")
st.altair_chart(tradeoff_chart, use_container_width=True)

win_win = trade_df[trade_df["Both Profitable"] == 1]
if not win_win.empty:
    st.success(
        f"✅ Win-win zone: **{win_win['Commission %'].min():.1f}% – {win_win['Commission %'].max():.1f}%** commission "
        f"keeps both agents and company profitable."
    )
else:
    st.warning("⚠️ No win-win zone found in this range. Try adjusting margins or operating cost.")

st.markdown("---")

# ── SECTION 5: Scenario Planner ───────────────────────────────────────────────

st.subheader("Scenario Planner — Worst / Base / Best")

def run_scenario(vol_mult, dig_pp, ag_mult):
    vol = monthly_volume * vol_mult
    dig = min(1.0, max(0.0, digital_pct/100 + dig_pp/100))
    dv  = vol * dig
    cv  = vol - dv
    dr  = dv * digital_margin
    cr  = cv * net_cash_margin
    inc = (dv / max(10, avg_tx_size)) * avg_incentive
    co_profit = dr + cr - inc - fixed_cost
    ag_count  = int(agent_count * ag_mult)
    ag_profit = agent_monthly_profit * ag_count
    return {"Company Profit": round(co_profit, 0),
            "Agent Pool Profit": round(ag_profit, 0),
            "Volume": round(vol, 0),
            "Agents": ag_count}

worst = run_scenario(1 + growth_pct/100 * 0.3, -5,      0.8)
base  = run_scenario(1 + growth_pct/100,        digital_boost, 1.0)
best  = run_scenario(1 + growth_pct/100 * 1.5,  digital_boost * 1.5, agent_scale)

sc1, sc2, sc3 = st.columns(3)
sc1.metric("Worst — Company Profit",  f"${worst['Company Profit']:,.0f}")
sc1.metric("Worst — Agent Pool",      f"${worst['Agent Pool Profit']:,.0f}")
sc2.metric("Base — Company Profit",   f"${base['Company Profit']:,.0f}")
sc2.metric("Base — Agent Pool",       f"${base['Agent Pool Profit']:,.0f}")
sc3.metric("Best — Company Profit",   f"${best['Company Profit']:,.0f}")
sc3.metric("Best — Agent Pool",       f"${best['Agent Pool Profit']:,.0f}")

scenarios_chart_df = pd.DataFrame([
    {"Scenario": "Worst", "Type": "Company Profit",    "Value": worst["Company Profit"]},
    {"Scenario": "Worst", "Type": "Agent Pool Profit", "Value": worst["Agent Pool Profit"]},
    {"Scenario": "Base",  "Type": "Company Profit",    "Value": base["Company Profit"]},
    {"Scenario": "Base",  "Type": "Agent Pool Profit", "Value": base["Agent Pool Profit"]},
    {"Scenario": "Best",  "Type": "Company Profit",    "Value": best["Company Profit"]},
    {"Scenario": "Best",  "Type": "Agent Pool Profit", "Value": best["Agent Pool Profit"]},
])

sc_color = alt.Scale(
    domain=["Company Profit", "Agent Pool Profit"],
    range=["#378ADD", "#1D9E75"]
)
sc_bar = alt.Chart(scenarios_chart_df).mark_bar().encode(
    x=alt.X("Scenario:N", sort=["Worst", "Base", "Best"]),
    y=alt.Y("Value:Q", title="Profit (USD)"),
    color=alt.Color("Type:N", scale=sc_color),
    xOffset="Type:N",
    tooltip=["Scenario", "Type", "Value"]
)
st.altair_chart(sc_bar, use_container_width=True)

st.caption("SomNexus Agent & Ecosystem Profit Simulator — built for investor demos and internal planning.")
