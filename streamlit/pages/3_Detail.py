import streamlit as st

st.set_page_config(page_title="Opportunity Detail — GovContract Radar", layout="wide")

opp = st.session_state.get("selected_opportunity")
if not opp:
    st.warning("No opportunity selected. Go to the **Feed** and click 'View details'.")
    st.stop()

st.title(opp["title"])
st.caption(f"{opp['agency_name']}  |  NAICS {opp['naics_code']}  |  {opp['days_until_deadline']} days until deadline")

col1, col2, col3 = st.columns(3)
col1.metric("Fit Score", opp["overall_fit_score"])
col2.metric("Confidence", opp.get("confidence", ""))
col3.metric("Days Left", opp["days_until_deadline"])

st.divider()

# Hard gates
st.subheader("Eligibility & Risk Flags")
gates = opp.get("hard_gates", [])
failed = [g for g in gates if g["status"] == "Fail"]
passed = [g for g in gates if g["status"] == "Pass"]

if failed:
    for g in failed:
        st.error(f"❌ **{g['name'].title()}**: {g['reason']}")
for g in passed:
    if g.get("reason"):
        st.info(f"✅ **{g['name'].title()}**: {g['reason']}")
    else:
        st.success(f"✅ **{g['name'].title()}**: Pass")

st.divider()

# Score breakdown
st.subheader("Score Breakdown")
components = opp.get("components", {})
cols = st.columns(len(components))
for i, (name, val) in enumerate(components.items()):
    cols[i].metric(name.replace("_", " ").title(), f"{val}/100")

st.divider()

# Market context
st.subheader("Market Context (NAICS {})".format(opp["naics_code"]))
median = opp.get("naics_median_award_amount")
sb_rate = opp.get("naics_sb_win_rate_pct")
if median:
    col1, col2 = st.columns(2)
    col1.metric("Median Award Amount", f"${median:,.0f}")
    col2.metric("SB Win Rate", f"{sb_rate}%")
else:
    st.caption("No historical award data for this NAICS code.")

st.divider()

# Artifacts placeholder (Week 4)
st.subheader("Pursuit Artifacts")
st.info("Bid/no-bid memo, compliance checklist, and questions for the contracting officer will appear here in Week 4 (GPT-4o).")

# Feedback
st.divider()
st.subheader("Your Assessment")
col1, col2 = st.columns(2)
if col1.button("👍 Worth pursuing", use_container_width=True):
    if "feedback" not in st.session_state:
        st.session_state.feedback = []
    st.session_state.feedback.append({"notice_id": opp["notice_id"], "vote": "up", "opportunity": opp})
    st.success("Feedback saved.")
if col2.button("👎 Not a fit", use_container_width=True):
    if "feedback" not in st.session_state:
        st.session_state.feedback = []
    st.session_state.feedback.append({"notice_id": opp["notice_id"], "vote": "down", "opportunity": opp})
    st.warning("Feedback saved.")

if st.button("← Back to Feed"):
    st.switch_page("pages/2_Feed.py")
