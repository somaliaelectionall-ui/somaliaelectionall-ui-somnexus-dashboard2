import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

st.set_page_config(page_title="SomNexus Simulator", layout="wide")
st.title("💸 SomNexus Agent & Ecosystem Profit Simulator")

st.sidebar.header("Company Economics")
fixed_cost         = st.sidebar.number_input("Monthly Fixed Cost (USD)", 10000, 200000, 40000, 1000)
monthly_volume     = st.sidebar.number_input("Total Monthly Volume (USD)", 100000, 50000000, 10000000, 100000)
digital_pct        = st.sidebar.slider("Digital % of Volume", 0, 100, 60, 1)
digital_margin_bps = st.sidebar.slider("Digital Net Margin (bps)", 30, 120, 60, 5)
cashout_margin_bps = st.sidebar.slider("Gross Cashout Margin (bps)", 50, 300, 150, 5)
avg_incentive      = st.sidebar.slider("Avg Incentive / Digital Tx (USD)", 0.0, 2.0, 0.6, 0.05)

st.sidebar.header("Agent Model")
agent_count      = st.sidebar.number_input("Active Agents", 100, 20000, 1200, 100)
tx_per_agent_day = st.sidebar.slider("Transfers per Agent per Day", 1, 50, 5)
avg_tx_size      = st.sidebar.number_input("Avg Cashout Tx Size (USD)", 10, 1000, 100, 10)
agent_commission = st.sidebar.slider("Agent Commission % per Tx", 0.0, 2.5, 1.0, 0.1)
agent_oper_cost  = st.sidebar.slider("Agent Monthly Operating Cost (USD)", 0, 2000, 300, 50)

st.sidebar.header("Scenario Controls")
growth_pct    = st.sidebar.slider("Volume Growth %", -30, 200, 40, 5)
digital_boost = st.sidebar.slider("Digital Adoption Boost (pp)", -20, 40, 10, 2)
agent_scale   = st.sidebar.slider("Agent Scale Factor (Best case)", 0.5, 5.0, 1.5, 0.1)

digital_margin  = digital_margin_bps  / 10000
cashout_margin  = cashout_margin_bps  / 10000
agent_take_rate = agent_commission    / 100
net_cash_margin = max(0, cashout_margin - agent_take_rate)

digital_volume  = monthly_volume * (digital_pct / 100)
cashout_volume  = monthly_volume - digital_volume
digital_revenue = digital_volume  * digital_margin
cashout_revenue = cashout_volume  * net_cash_margin
total_revenue   = digital_revenue + cashout_revenue
digital_tx      = digital_volume  / max(10, avg_tx_size)
incentive_cost  = digital_tx * avg_incentive
net_profit      = total_revenue - incentive_cost - fixed_cost
blended         = (digital_pct/100 * digital_margin) + ((100-digital_pct)/100 * net_cash_margin)
breakeven_vol   = fixed_cost / blended if blended > 0 else float("nan")

days            = 26
agent_tx_month  = tx_per_agent_day * days
agent_rev_pt    = avg_tx_size * agent_take_rate
agent_monthly_rev    = agent_tx_month * agent_rev_pt
agent_monthly_profit = agent_monthly_rev - agent_oper_cost
agent_roi            = (agent_monthly_profit / agent_oper_cost * 100) if agent_oper_cost > 0 else 999
breakeven_tx_day     = (agent_oper_cost / (avg_tx_size * agent_take_rate * days)) if agent_take_rate > 0 else 0
total_agent_pool     = agent_monthly_profit * agent_count

st.subheader("Company Overview")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Monthly Volume",     f"${monthly_volume:,.0f}")
c2.metric("Digital Revenue",    f"${digital_revenue:,.0f}")
c3.metric("Cashout Revenue",    f"${cashout_revenue:,.0f}")
c4.metric("Company Net Profit", f"${net_profit:,.0f}", delta="Profitable" if net_profit > 0 else "Loss")

c5, c6, c7, c8 = st.columns(4)
c5.metric("Break-even Volume",  f"${breakeven_vol:,.0f}" if not np.isnan(breakeven_vol) else "N/A")
c6.metric("Incentive Cost",     f"${incentive_cost:,.0f}")
c7.metric("Blended Margin bps", f"{blended*10000:.0f}")
c8.metric("Rev per Agent",      f"${total_revenue/max(1,agent_count):,.0f}")

st.markdown("---")
st.subheader("Agent Cashout Income")
a1, a2, a3, a4 = st.columns(4)
a1.metric("Tx / Agent / Month", f"{agent_tx_month:,}")
a2.metric("Agent Revenue / Mo", f"${agent_monthly_rev:,.0f}")
a3.metric("Agent Profit / Mo",  f"${agent_monthly_profit:,.0f}", delta=f"{agent_roi:.0f}% ROI")
a4.metric("Break-even Tx/Day",  f"{breakeven_tx_day:.1f}")

a5, a6, a7, a8 = st.columns(4)
a5.metric("Daily Take-home",    f"${agent_monthly_profit/days:,.0f}")
a6.metric("Active Agents",      f"{agent_count:,}")
a7.metric("Total Agent Pool",   f"${total_agent_pool:,.0f}")
a8.metric("Network Volume",     f"${agent_tx_month*avg_tx_size*agent_count:,.0f}")

st.markdown("---")
st.subheader("Agent Profit vs Daily Transfers")
tx_range = np.arange(1, 41)
curve_df = pd.DataFrame({
    "Tx per Day": tx_range,
    "Monthly Profit": tx_range * days * avg_tx_size * agent_take_rate - agent_oper_cost
})
st.altair_chart(
    alt.Chart(curve_df).mark_line(point=True, color="#1D9E75").encode(
        x="Tx per Day:Q", y="Monthly Profit:Q", tooltip=["Tx per Day","Monthly Profit"]
    ) + alt.Chart(pd.DataFrame({"y":[0]})).mark_rule(color="red",strokeDash=[5,3]).encode(y="y:Q"),
    use_container_width=True
)

st.subheader("Company Profit vs Digital Adoption %")
dig_range = np.arange(0, 101, 5)
prof_list = []
for d in dig_range:
    dv = monthly_volume*(d/100); cv = monthly_volume-dv
    prof_list.append(dv*digital_margin + cv*net_cash_margin - (dv/max(10,avg_tx_size))*avg_incentive - fixed_cost)
sens_df = pd.DataFrame({"Digital %": dig_range, "Net Profit": prof_list})
st.altair_chart(
    alt.Chart(sens_df).mark_line(point=True, color="#378ADD").encode(
        x="Digital %:Q", y="Net Profit:Q", tooltip=["Digital %","Net Profit"]
    ) + alt.Chart(pd.DataFrame({"y":[0]})).mark_rule(color="red",strokeDash=[5,3]).encode(y="y:Q"),
    use_container_width=True
)

st.subheader("Scenario Planner")
def scenario(vol_m, dig_pp, ag_m):
    v = monthly_volume*vol_m; d = min(1,max(0,digital_pct/100+dig_pp/100))
    dv=v*d; cv=v-dv
    cp = dv*digital_margin + cv*net_cash_margin - (dv/max(10,avg_tx_size))*avg_incentive - fixed_cost
    return {"Company Profit": round(cp), "Agent Pool": round(agent_monthly_profit*agent_count*ag_m)}

g = 1 + growth_pct/100
worst = scenario(1+growth_pct/100*0.3, -5, 0.8)
base  = scenario(g, digital_boost, 1.0)
best  = scenario(1+growth_pct/100*1.5, digital_boost*1.5, agent_scale)

s1,s2,s3 = st.columns(3)
s1.metric("Worst — Company",  f"${worst['Company Profit']:,.0f}")
s1.metric("Worst — Agents",   f"${worst['Agent Pool']:,.0f}")
s2.metric("Base — Company",   f"${base['Company Profit']:,.0f}")
s2.metric("Base — Agents",    f"${base['Agent Pool']:,.0f}")
s3.metric("Best — Company",   f"${best['Company Profit']:,.0f}")
s3.metric("Best — Agents",    f"${best['Agent Pool']:,.0f}")

sc_df = pd.DataFrame([
    {"Scenario":"Worst","Type":"Company","Value":worst["Company Profit"]},
    {"Scenario":"Worst","Type":"Agents", "Value":worst["Agent Pool"]},
    {"Scenario":"Base", "Type":"Company","Value":base["Company Profit"]},
    {"Scenario":"Base", "Type":"Agents", "Value":base["Agent Pool"]},
    {"Scenario":"Best", "Type":"Company","Value":best["Company Profit"]},
    {"Scenario":"Best", "Type":"Agents", "Value":best["Agent Pool"]},
])
st.altair_chart(
    alt.Chart(sc_df).mark_bar().encode(
        x=alt.X("Scenario:N", sort=["Worst","Base","Best"]),
        y="Value:Q", color="Type:N", xOffset="Type:N",
        tooltip=["Scenario","Type","Value"]
    ), use_container_width=True
)

st.caption("SomNexus Agent & Ecosystem Profit Simulator — for investor demos and internal planning.")
