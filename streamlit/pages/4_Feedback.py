import streamlit as st

st.set_page_config(page_title="Feedback — GovContract Radar", layout="wide")
st.title("Feedback Log")
st.caption("Your assessments help calibrate future scoring.")

feedback = st.session_state.get("feedback", [])

if not feedback:
    st.info("No feedback yet. Review opportunities in the Feed and mark them as worth pursuing or not.")
    st.stop()

up = [f for f in feedback if f["vote"] == "up"]
down = [f for f in feedback if f["vote"] == "down"]

col1, col2 = st.columns(2)
col1.metric("Worth pursuing", len(up))
col2.metric("Not a fit", len(down))

st.divider()

if up:
    st.subheader("👍 Worth pursuing")
    for f in up:
        opp = f["opportunity"]
        st.markdown(f"- **{opp['title'][:70]}** — Score: {opp['overall_fit_score']} | {opp['agency_name']}")

if down:
    st.subheader("👎 Not a fit")
    for f in down:
        opp = f["opportunity"]
        st.markdown(f"- **{opp['title'][:70]}** — Score: {opp['overall_fit_score']} | {opp['agency_name']}")
