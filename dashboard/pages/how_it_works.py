import os
import sys
import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "ingestion"))

st.set_page_config(
    page_title="How It Works — ContractFit",
    page_icon="🟦",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={},
)

st.markdown("""
<style>
  [data-testid="collapsedControl"] { display: none; }
  section[data-testid="stSidebar"] { display: none; }
  .stMainBlockContainer, .block-container,
  div[data-testid="stAppViewBlockContainer"] { padding-top: 0 !important; }
  header[data-testid="stHeader"] { display: none !important; }
  #MainMenu { display: none !important; }
  footer { display: none !important; }
  [data-testid="stSidebarCollapsedControl"] { display: none !important; }

  .stButton > button[kind="primary"] {
    background-color: #1d4ed8 !important;
    border-color: #1d4ed8 !important;
    color: white !important;
  }
  .stButton > button[kind="primary"]:hover {
    background-color: #1e40af !important;
    border-color: #1e40af !important;
  }

  .tech-pill {
    display: inline-block;
    background: #f1f5f9;
    color: #334155;
    font-size: 13px;
    font-weight: 500;
    padding: 6px 14px;
    border-radius: 20px;
    margin: 4px;
  }
  .tech-category { font-size: 12px; font-weight: 700; color: #94a3b8; letter-spacing: 1px; text-transform: uppercase; margin: 20px 0 8px 0; }

  .step {
    display: flex;
    align-items: flex-start;
    gap: 20px;
    margin-bottom: 28px;
  }
  .step-num {
    min-width: 36px;
    height: 36px;
    background: #1d4ed8;
    color: white;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 15px;
  }
  .step-content h4 { margin: 0 0 4px 0; font-size: 15px; color: #0f172a; }
  .step-content p  { margin: 0; font-size: 14px; color: #64748b; line-height: 1.5; }

  .section-label {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: #1d4ed8;
    margin-bottom: 8px;
  }
  .section-title {
    font-size: 28px;
    font-weight: 800;
    color: #0f172a;
    margin-bottom: 8px;
  }
  .section-sub {
    font-size: 15px;
    color: #64748b;
    margin-bottom: 36px;
  }

  .st-key-home_reset button {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
    min-height: 0 !important;
    height: 0 !important;
  }
  .st-key-home_reset button:hover,
  .st-key-home_reset button:focus,
  .st-key-home_reset button:active {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
  }
</style>
""", unsafe_allow_html=True)

# ── Nav ───────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="display:flex;justify-content:space-between;align-items:center;padding:14px 0;margin-bottom:24px;border-bottom:1px solid #f1f5f9;">
  <div onclick="window.location.href='/'" style="cursor:pointer;font-size:20px;font-weight:800;color:#0f172a;letter-spacing:-0.5px;">
    Contract<span style="color:#1d4ed8;">Fit</span>
  </div>
  <a href="/" style="font-size:13px;color:#64748b;text-decoration:none;">← Back</a>
</div>
""", unsafe_allow_html=True)

if st.button("", key="home_reset"):
    st.switch_page("app.py")
st.markdown("""
<style>
.st-key-home_reset { display: none !important; }
</style>
""", unsafe_allow_html=True)

# ── Content ───────────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">Under the Hood</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">How Contract Fit Engine works</div>', unsafe_allow_html=True)
st.markdown('<div class="section-sub">From raw SAM.gov data to a ranked, scored opportunity feed. Fully automated, weekly refresh.</div>', unsafe_allow_html=True)

s1, s2, s3 = st.columns(3)
s1.metric("Opportunities scored", "1,387")
s2.metric("Scoring dimensions", "5")
s3.metric("Pipeline refresh", "Weekly")

st.markdown("---")

c1, c2 = st.columns([1, 1])

with c1:
    st.markdown("#### Pipeline")
    st.markdown("""
    <div class="step">
      <div class="step-num">1</div>
      <div class="step-content">
        <h4>Ingest from SAM.gov</h4>
        <p>Apache Airflow pulls active federal contract opportunities weekly from the SAM.gov public API. Raw data lands in Snowflake.</p>
      </div>
    </div>
    <div class="step">
      <div class="step-num">2</div>
      <div class="step-content">
        <h4>Model with dbt</h4>
        <p>dbt transforms raw opportunity data into clean, analytics-ready models — opportunities, agencies, NAICS categories, and scoring features.</p>
      </div>
    </div>
    <div class="step">
      <div class="step-num">3</div>
      <div class="step-content">
        <h4>Embed with Azure OpenAI</h4>
        <p>Each opportunity description is converted into a 1,536-dimension vector embedding using Azure OpenAI's text-embedding-3-small model.</p>
      </div>
    </div>
    <div class="step">
      <div class="step-num">4</div>
      <div class="step-content">
        <h4>Score for fit</h4>
        <p>A conversational AI agent extracts your company profile from natural language, then a weighted scoring engine computes a FIT_SCORE (0–100) across 5 dimensions.</p>
      </div>
    </div>
    <div class="step">
      <div class="step-num">5</div>
      <div class="step-content">
        <h4>Index for search</h4>
        <p>Azure AI Search indexes all opportunities with their embeddings, enabling hybrid keyword + vector search across the full dataset.</p>
      </div>
    </div>
    <div class="step">
      <div class="step-num">6</div>
      <div class="step-content">
        <h4>Surface in dashboard</h4>
        <p>Streamlit dashboard shows the ranked opportunity feed, semantic search, analytics, and AI-generated fit explanations.</p>
      </div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("#### Scoring Model")
    st.markdown("""
    | Component | Weight | What it measures |
    |---|---|---|
    | Capability similarity | **35%** | Cosine similarity between opportunity and company profile embeddings |
    | Past performance | **25%** | NAICS code and past agency match |
    | Contract size fit | **15%** | Value within company's comfortable range |
    | Competition | **15%** | Small biz win rate + set-aside match |
    | Strategic alignment | **10%** | Keyword overlap with company focus |
    """)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("**Hard gates** cap scores for eligibility mismatches:")
    st.markdown("""
    - Set-aside mismatch → max score **40**
    - Clearance required → max score **50**
    - Contract 10× above max → max score **65**
    """)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("**Decision thresholds**")
    st.markdown("🟢 **PURSUE** — score ≥ 70  \n🟡 **WATCH** — score 50–69  \n🔴 **NO BID** — score < 50")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("**Roadmap: ML-based scoring**")
    st.markdown("Current rule-based weights will be replaced by an ML classifier trained on USASpending.gov award outcomes and user bid results.")
    st.markdown('<span class="tech-pill">XGBoost</span><span class="tech-pill">Feature store in Snowflake</span><span class="tech-pill">USASpending.gov</span>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('[View full scoring methodology →](https://gennadyvit.github.io/contract-fit-engine/scoring-model.html)')

st.markdown("---")
st.markdown("#### Tech Stack")

ts1, ts2, ts3 = st.columns(3)
with ts1:
    st.markdown('<div class="tech-category">Data & Pipeline</div>', unsafe_allow_html=True)
    st.markdown('<span class="tech-pill">Apache Airflow</span><span class="tech-pill">Snowflake</span><span class="tech-pill">dbt</span><span class="tech-pill">Python</span><span class="tech-pill">SAM.gov API</span>', unsafe_allow_html=True)
with ts2:
    st.markdown('<div class="tech-category">AI & Search</div>', unsafe_allow_html=True)
    st.markdown('<span class="tech-pill">Azure OpenAI GPT-4o</span><span class="tech-pill">text-embedding-3-small</span><span class="tech-pill">Azure AI Search</span><span class="tech-pill">RAG</span><span class="tech-pill">Function calling</span>', unsafe_allow_html=True)
with ts3:
    st.markdown('<div class="tech-category">Infrastructure</div>', unsafe_allow_html=True)
    st.markdown('<span class="tech-pill">Azure Container Apps</span><span class="tech-pill">Azure Container Registry</span><span class="tech-pill">Streamlit</span><span class="tech-pill">Docker</span>', unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)
if st.button("→ Try It Now", type="primary"):
    st.switch_page("app.py")
