# GovContract Radar: Full Project Spec

## What It Is
A federal contract intelligence platform that scores whether a specific opportunity is worth pursuing, estimates likely award size, identifies incumbents and competitors, and explains the reasoning with evidence.

Given a company profile + SAM.gov opportunity + USAspending history, the platform returns:
- Bid Fit Score (0-100) with component breakdown
- Confidence level (High / Medium / Low)
- Estimated award range (P25-P75)
- Incumbent and top competitor identification
- LLM-generated recommendation narrative with evidence

---

## Stack
| Layer | Tool |
|---|---|
| Data warehouse | Snowflake |
| Transformation | dbt |
| Orchestration | Airflow (weekly ingestion only) |
| Scoring API | FastAPI on Azure App Service or Container Apps |
| Embeddings | Azure OpenAI text-embedding-3-small |
| Vector search / RAG | Azure AI Search |
| LLM narrative | Azure OpenAI GPT-4o |
| UI | Streamlit on Azure App Service |
| Task tracking | GitHub Projects + GitHub Issues |

---

## Data Sources
- SAM.gov API: active opportunities, entity registrations
- USAspending.gov API: historical contract awards

---

## Data Layer (Snowflake + dbt)

### Raw Tables (loaded by Airflow)
- `raw_sam_opportunities`
- `raw_usaspending_awards`
- `raw_sam_entities`
- `raw_naics_psc_reference`

### dbt Staging Models
- `stg_opportunities`: clean SAM.gov opportunity fields, parse dates, normalize set-aside codes
- `stg_awards`: clean USAspending award fields, normalize vendor names, parse amounts
- `stg_entities`: company registrations, certifications, CAGE codes, business size

### dbt Dimension Models
- `dim_agency`: agency name, code, sub-agency, office
- `dim_vendor`: vendor name, DUNS/UEI, CAGE, normalized name for deduplication
- `dim_naics`: NAICS code, description, sector
- `dim_psc`: PSC code, description, category

### dbt Fact Models
- `fact_awards`: one row per award, foreign keys to dim tables, award amount, dates, set-aside type, contract vehicle
- `fact_opportunities`: one row per active opportunity, foreign keys to dim tables, response deadline, set-aside type, estimated value

### dbt Mart Models
- `mart_opportunity_features`: one row per opportunity, all features needed for scoring precomputed
  - agency_award_count_naics (awards by this agency in this NAICS last 3 years)
  - median_award_amount_naics_agency
  - p25_award_amount, p75_award_amount
  - set_aside_type, set_aside_rate_agency (% of awards set aside by this agency)
  - days_until_response
  - opportunity_text (title + description concatenated for embedding)
  - is_recompete (boolean, derived from incumbent detection)
- `mart_award_prediction_training`: historical awards with features for XGBoost training
  - Features: NAICS, PSC, agency, set-aside type, fiscal year, contract vehicle, place of performance
  - Target: award_amount
- `mart_incumbent_detection`: one row per opportunity, incumbent signals
  - incumbent_vendor (most recent award winner for same agency/NAICS/PSC combination)
  - incumbent_award_count (how many times they won similar work from this office)
  - incumbent_last_award_date
  - incumbent_total_value
  - is_recompete_likely (boolean)
- `mart_competition_intensity`: one row per opportunity, competition signals
  - top_5_vendor_share (% of similar spend captured by top 5 vendors)
  - vendor_count_naics_agency (unique vendors who won similar work)
  - competition_label (Low / Moderate / High)
  - hhi_score (Herfindahl index, optional)

---

## Company Profile Schema
Stored as JSON. Input via Streamlit form or file upload.

```json
{
  "company_summary": "Small data engineering consultancy focused on Azure, SQL Server, Python ETL, and Power BI.",
  "capabilities": ["data engineering", "ETL", "dashboarding", "cloud migration", "database modernization"],
  "naics": ["541511", "541512", "541519"],
  "psc": ["DA01", "DB10", "R408"],
  "certifications": ["small_business"],
  "past_performance": [
    {
      "client": "transportation agency",
      "work": "SQL Server reporting and ETL modernization",
      "value": 350000,
      "outcome": "delivered on time, extended for follow-on work"
    }
  ],
  "preferred_contract_size": {
    "min": 50000,
    "max": 750000
  },
  "locations": ["remote", "Massachusetts", "Washington DC"],
  "clearance": "public trust eligible",
  "prime_or_sub": "either",
  "contract_vehicles": ["GSA Schedule 70"],
  "avoid": ["construction", "hardware procurement", "onsite-only"],
  "keywords_target": ["data warehouse", "ETL", "dashboard", "cloud migration", "analytics"],
  "keywords_avoid": ["hardware", "construction", "janitorial", "staff augmentation"],
  "agency_preferences": ["DOT", "HHS", "VA"],
  "team_size": 5,
  "max_contract_executable": 1000000
}
```

---

## Scoring Architecture

### Precomputed (nightly, stored in Snowflake)
Run once per opportunity regardless of how many companies evaluate it:
- Award range (P25/P75 from mart or XGBoost model)
- Incumbent identification (from mart_incumbent_detection)
- Competition intensity (from mart_competition_intensity)
- Agency trend (set-aside rate, award frequency)
- Opportunity embedding (Azure OpenAI, stored in Azure AI Search)
- Award history chunks (chunked and indexed in Azure AI Search)

### Real-time (on demand, per company per opportunity)
Fast deterministic scoring, target under 100ms before LLM call:
1. Load company profile + company profile embedding (cached)
2. Load precomputed opportunity intelligence from Snowflake
3. Run hard gates (see below)
4. Compute weighted fit score components
5. Combine into final score
6. On user request: RAG retrieval + LLM narrative

---

## Hard Gates (applied before weighted score)
If any gate fails, score is capped, not zeroed:

| Condition | Score Cap |
|---|---|
| Not eligible for required set-aside | 40 |
| Mandatory clearance company lacks | 50 |
| Onsite-only, location impossible | 60 |
| Contract value 10x above company max | 65 |

Gates are displayed separately in UI as Pass / Fail / Partial, not folded into the weighted score.

---

## Fit Score Formula

```
Final Fit Score =
  0.35 * capability_similarity
+ 0.25 * past_performance_match
+ 0.15 * contract_size_fit
+ 0.15 * competition_score
+ 0.10 * strategic_fit

Eligibility: hard gate, shown separately (Pass / Fail / Partial)
Location fit: soft filter, shown separately, not weighted
```

### Component Definitions

**capability_similarity**: cosine similarity between company profile embedding and opportunity embedding. Capped if NAICS/PSC mismatch or no concrete skill/entity overlap detected.

**past_performance_match**: similarity between past performance descriptions and opportunity description. Boosted if same agency or same NAICS appears in past performance.

**contract_size_fit**: how well the opportunity estimated value fits company preferred range. Full score if within range, decays outside range, hard gate if 10x above max.

**competition_score**: inverse of competition intensity. Low competition = high score. Derived from mart_competition_intensity.

**strategic_fit**: keyword match (target/avoid lists), agency preference match, prime/sub alignment with opportunity type.

---

## Confidence Layer
Shown alongside score in UI. Reduces displayed confidence without changing the score:

| Condition | Confidence Impact |
|---|---|
| Opportunity text is short or boilerplate | Downgrade to Medium or Low |
| Company profile is vague or sparse | Downgrade to Medium |
| NAICS/PSC mismatch | Cap capability score, flag Low confidence |
| No prior awards data for this agency/NAICS | Flag Low confidence on award range |
| No concrete skill/entity overlap detected | Cap capability score |

---

## RAG Layer (Azure AI Search)

### Indexes
| Index | Key Fields |
|---|---|
| opportunity_chunks | opportunity_id, naics, psc, agency, set_aside, text, embedding |
| award_history_chunks | vendor, agency, naics, award_amount, date, text, embedding |
| company_profile_chunks | capability, naics, psc, past_performance_text, embedding |
| past_performance_chunks | client, work_description, value, outcome, embedding |

Hybrid search enabled: keyword (NAICS, PSC exact match) + vector (semantic similarity) running simultaneously.

### Retrieval
Top-k chunks retrieved per opportunity at narrative generation time. k=5-10 depending on chunk type. Retrieved chunks passed as context to LLM.

---

## LLM Narrative (Azure OpenAI GPT-4o)
Called on demand only, not blocking fit score display. Score displays immediately, narrative streams in behind it.

### Prompt Structure
```
You are a federal contracting analyst. Given the following inputs, write a 3-paragraph bid/no-bid recommendation with evidence.

Company profile: {profile}
Opportunity: {opportunity_summary}
Fit score components: {score_breakdown}
Estimated award range: {award_range}
Incumbent signals: {incumbent_data}
Competition context: {competition_data}
Retrieved evidence: {rag_chunks}

Format:
Paragraph 1: Overall recommendation and fit score rationale
Paragraph 2: Key risks and disqualifying factors if any
Paragraph 3: Recommended pursuit strategy (prime, sub, skip, or monitor)
```

---

## UI (Streamlit)

### Pages
1. **Company Profile**: form input or JSON upload, save profile, view saved profile
2. **Opportunity Feed**: paginated list of active opportunities with precomputed fit scores, filter by min score / agency / NAICS / set-aside / size range
3. **Opportunity Detail**:
   - Score breakdown display (see below)
   - Award range estimate
   - Incumbent and competitor table
   - Similar past awards
   - Generate Recommendation button (triggers RAG + LLM)
   - Recommendation narrative (streamed)
4. **Feedback**: thumbs up/down per opportunity, stored with full score snapshot

### Score Breakdown Display
```
Overall Fit: 78/100
Confidence: Medium

Eligibility:         Pass
Capability Match:    86/100
Past Performance:    61/100
Contract Size Fit:   74/100
Competition:         Moderate
Location Fit:        Pass
Strategic Fit:       70/100

Main driver: strong semantic match on cloud analytics / data engineering
Main risk: limited direct past performance with this agency
```

---

## Feedback Loop
Store every feedback event:
```json
{
  "company_id": "...",
  "opportunity_id": "...",
  "feedback": "relevant",
  "score_snapshot": { ...full score breakdown at time of rating... },
  "timestamp": "..."
}
```
Used to fine-tune capability similarity weighting per company over time. Stored in Snowflake.

---

## XGBoost Award Range Model
- Features: NAICS (4-digit), PSC, agency code, set-aside type, fiscal year, contract vehicle, place of performance region
- Target: award_amount (log-transformed)
- Output: P25 and P75 of predicted distribution, not a point estimate
- Training data: mart_award_prediction_training
- Fallback if model unavailable: median award amount for same NAICS/agency combination from historical data

---

## Project Structure
```
govcontract-radar/
  airflow/
    dags/
      sam_ingestion.py
      usaspending_ingestion.py
  dbt/
    models/
      staging/
      dimensions/
      facts/
      marts/
    tests/
    sources.yml
  api/
    main.py (FastAPI)
    scoring/
      rules_engine.py
      fit_score.py
      embeddings.py
      incumbent.py
      competition.py
    rag/
      search.py
      narrative.py
    models/
      award_range_model.pkl
      train_model.py
  streamlit/
    app.py
    pages/
      profile.py
      feed.py
      detail.py
      feedback.py
  docs/
    architecture.md
    data_dictionary.md
  README.md
  ROADMAP.md
```

---

## Weekly Plan

### Week 1: Data Foundation ✅
- Confirm SAM + USAspending raw tables are reliable
- Build dbt staging models
- Build all four marts
- Goal: one Snowflake query returns everything needed for scoring

### Week 2: Scoring MVP
- FastAPI scoring endpoint
- Company profile JSON input
- Rules engine and hard gates
- Embedding similarity (Azure OpenAI)
- Weighted score with component breakdown
- Goal: API returns a real fit score for a real opportunity in under 100ms

### Week 3: RAG + UI
- Azure AI Search index setup
- Chunk and embed opportunity and award history text
- Streamlit pages: profile, feed, detail, score breakdown
- Goal: usable end-to-end demo

### Week 4: Narrative + Polish
- Azure OpenAI narrative generation (streamed)
- Confidence layer
- Caching for precomputed scores
- README, architecture diagram, data dictionary
- One polished demo scenario end to end
- Export demo as static screenshots for offline use

---

## Resume / Interview Description
"The scoring API separates fast deterministic scoring from expensive narrative generation. Company and opportunity embeddings are cached, structured opportunity intelligence is precomputed in Snowflake, and the API computes a company-specific fit score in under 100ms. Azure OpenAI is only called on demand to generate an evidence-backed recommendation memo."

---

## Key Design Decisions to Be Able to Explain
1. Why precompute opportunity intelligence but compute fit in real time: opportunity intelligence is company-agnostic, fit is not. Precomputing both wastes compute; computing both on demand creates latency.
2. Why hard gates are caps not zeros: a capped score surfaces the opportunity with a visible warning rather than hiding it. User can still see it and decide.
3. Why eligibility is not in the weighted formula: eligibility is binary, not a gradient. Weighting it distorts scores for ineligible opportunities.
4. Why confidence is separate from score: a high score with low confidence should be treated differently than a high score with high confidence. Conflating them misleads the user.
5. Why feedback events store the full score snapshot: lets you analyze whether the model was systematically wrong in a particular component, not just whether the final score was off.
