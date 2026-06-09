import streamlit as st
import pandas as pd

st.set_page_config(page_title="GovContract Radar", layout="wide")

st.title("GovContract Radar")
st.caption("Federal contract opportunity tracker")

st.info("Connect Snowflake credentials in .env to load live data.")

# Placeholder until Snowflake + dbt pipeline is wired up
sample = pd.DataFrame({
    "Agency": ["DoD", "DHS", "HHS"],
    "Opportunities": [42, 17, 31],
    "Total Value ($M)": [120.5, 44.2, 88.0],
})

st.subheader("Opportunities by Agency")
st.bar_chart(sample.set_index("Agency")["Opportunities"])
st.dataframe(sample, use_container_width=True)
