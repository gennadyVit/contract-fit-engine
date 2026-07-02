import streamlit as st

st.set_page_config(
    page_title="GovContract Radar",
    page_icon="🎯",
    layout="wide",
)

st.title("GovContract Radar")
st.caption("Federal Capture Screening Agent")

st.markdown("""
### How it works

1. **Set your profile** — enter your company capabilities, certifications, and contract preferences
2. **Review your feed** — ranked opportunities scored against your profile
3. **Drill into details** — extracted requirements, compliance gaps, bid/no-bid memo
4. **Give feedback** — help the system learn what matters to you

---

**Get started →** Use the sidebar to navigate to **Profile**.
""")

with st.sidebar:
    st.markdown("### Navigation")
    st.page_link("pages/1_Profile.py", label="Profile", icon="🏢")
    st.page_link("pages/2_Feed.py", label="Opportunity Feed", icon="📋")
