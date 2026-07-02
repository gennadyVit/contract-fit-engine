import streamlit as st
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "utils"))
from api import score_opportunities

st.set_page_config(page_title="Opportunity Feed — GovContract Radar", layout="wide")
st.title("Opportunity Feed")

if not st.session_state.get("profile"):
    st.warning("No profile set. Go to **Profile** first.")
    st.stop()

profile = st.session_state.profile

# Score button
if st.button("Refresh scores", type="primary") or "results" not in st.session_state:
    with st.spinner("Scoring opportunities..."):
        try:
            data = score_opportunities(profile, limit=50)
            st.session_state.results = data
        except Exception as e:
            st.error(f"API error: {e}")
            st.stop()

data = st.session_state.get("results", {})
opportunities = data.get("opportunities", [])

if not opportunities:
    st.info("No opportunities returned. Check the API is running.")
    st.stop()

# Exclusion summary
total_reviewed = data.get("total", len(opportunities))
excluded = total_reviewed  # all scored, filter locally by min_score

col1, col2, col3 = st.columns(3)
col1.metric("Opportunities reviewed", 653)
col2.metric("Shown in feed", len(opportunities))
col3.metric("Azure embeddings", "On" if data.get("azure_embeddings_enabled") else "Off")

st.divider()

# Filters
min_score = st.slider("Minimum fit score", 0, 100, 20)
filtered = [o for o in opportunities if o["overall_fit_score"] >= min_score]

st.caption(f"Showing {len(filtered)} opportunities with score ≥ {min_score}")

# Opportunity cards
for opp in filtered:
    score = opp["overall_fit_score"]
    confidence = opp.get("confidence", "")
    days = opp.get("days_until_deadline", 0)

    # color code by score
    if score >= 70:
        badge = "🟢"
    elif score >= 50:
        badge = "🟡"
    else:
        badge = "🔴"

    deadline_warning = "⚠️ " if days <= 7 else ""

    with st.expander(f"{badge} **{score}** — {opp['title'][:80]}  |  {opp['agency_name']}  |  {deadline_warning}{days}d"):
        col1, col2, col3 = st.columns(3)
        col1.metric("Fit Score", score)
        col2.metric("Confidence", confidence)
        col3.metric("Days Left", days)

        # gate failures
        failed_gates = [g for g in opp.get("hard_gates", []) if g["status"] == "Fail"]
        if failed_gates:
            st.warning("**Disqualifiers detected:**")
            for g in failed_gates:
                st.markdown(f"- {g['reason']}")

        # score components
        st.markdown("**Score breakdown:**")
        components = opp.get("components", {})
        cols = st.columns(len(components))
        for i, (name, val) in enumerate(components.items()):
            cols[i].metric(name.replace("_", " ").title(), val)

        # market context
        median = opp.get("naics_median_award_amount")
        sb_rate = opp.get("naics_sb_win_rate_pct")
        if median:
            st.caption(f"NAICS median award: ${median:,.0f}  |  SB win rate: {sb_rate}%")

        col_a, col_b = st.columns(2)
        if col_a.button("View details", key=f"detail_{opp['notice_id']}"):
            st.session_state.selected_opportunity = opp
            st.switch_page("pages/3_Detail.py")
        if opp.get("ui_link") or True:
            col_b.markdown(f"[View on SAM.gov]({opp.get('ui_link', '#')})")
