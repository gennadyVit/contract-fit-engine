# Contract Fit Engine

**AI-powered platform that helps small businesses find and prioritize federal contract opportunities using fit scoring and semantic search.**

Small businesses competing for federal contracts face thousands of SAM.gov listings with no easy way to know which ones are worth pursuing. Contract Fit Engine ingests public procurement data, scores every opportunity against a company profile, and surfaces the best bids through a searchable dashboard — so you spend time on the right opportunities, not reading through irrelevant ones.

---

## Features

- **Daily ingestion** — pulls active contract opportunities from the SAM.gov public API via Apache Airflow
- **Data warehouse** — raw opportunity data lands in Snowflake, transformed into analytics-ready models using dbt
- **Fit scoring** — weighted scoring engine computes a FIT_SCORE (0–100) across 5 dimensions and assigns a PURSUE, WATCH, or NO_BID decision for each opportunity
- **Semantic search** — Azure AI Search indexes opportunity descriptions using vector embeddings for hybrid keyword + vector search
- **Dashboard** — Streamlit app with opportunity feed, filters, and direct links to SAM.gov

---

## Scoring Model

Each opportunity is scored across 5 weighted components:

| Component | Weight | What it measures |
|---|---|---|
| Capability similarity | 35% | Cosine similarity between opportunity and company profile embeddings |
| Past performance | 25% | NAICS code and agency match against company history |
| Contract size fit | 15% | Whether contract value falls within company's comfortable range |
| Competition favorability | 15% | Small business win rate for this NAICS + set-aside match |
| Strategic alignment | 10% | Keyword overlap with company focus areas |

Hard gates cap scores for eligibility mismatches (wrong set-aside, clearance level, or contract 10x above company max).

**Decision thresholds:** ≥70 → PURSUE · 50–69 → WATCH · <50 → NO_BID

---

## Tech Stack

| Layer | Technology |
|---|---|
| Orchestration | Apache Airflow |
| Data warehouse | Snowflake |
| Data modeling | dbt |
| Embeddings | Azure OpenAI (text-embedding-3-small) |
| Vector search | Azure AI Search |
| Dashboard | Streamlit |
| Infrastructure | Azure Container Apps |
| Data source | SAM.gov public API |

---

## Architecture

```
SAM.gov API
    ↓ (Airflow DAG — daily)
Snowflake RAW layer
    ↓ (dbt)
Snowflake MARTS layer (opportunity features, scoring inputs)
    ↓ (Azure OpenAI)
Vector embeddings → stored in Snowflake
    ↓ (scoring engine)
AGENT_DECISIONS (FIT_SCORE, DECISION per opportunity)
    ↓ (Azure AI Search indexer)
Search index (hybrid keyword + vector)
    ↓
Streamlit dashboard
```

---

## Running Locally

**Prerequisites:** Python 3.11+, Snowflake account, Azure OpenAI, Azure AI Search

```bash
git clone https://github.com/gennadyVit/contract-fit-engine.git
cd contract-fit-engine
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and fill in your credentials:

```
SNOWFLAKE_ACCOUNT=
SNOWFLAKE_USER=
SNOWFLAKE_PRIVATE_KEY=
SNOWFLAKE_WAREHOUSE=
SNOWFLAKE_DATABASE=
SNOWFLAKE_SCHEMA=
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_API_KEY=
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=
AZURE_SEARCH_ENDPOINT=
AZURE_SEARCH_KEY=
```

Run the dashboard:

```bash
cd dashboard
streamlit run app.py
```

Run the scoring engine:

```bash
cd ingestion
python scoring.py technova
```

---

## Scoring Model Documentation

[View the full scoring methodology →](https://gennadyvit.github.io/contract-fit-engine/scoring-model.html)

---

## Current State

- 2,000 SAM.gov opportunities ingested
- 1,387 scored against company profile (PURSUE: 2, WATCH: 24, NO_BID: 1,361)
- Azure AI Search index live with 1,387 documents
- Streamlit dashboard running, Azure deployment in progress

---

## License

MIT
