# govcontract-radar

Automated first-pass capture analyst for federal contract opportunities.

Monitors SAM.gov daily, reads full solicitation text, scores each opportunity against a company profile, suppresses bad matches, and delivers a ranked digest with pursuit artifacts — replacing the manual work a capture analyst does before a bid decision.

## Status

Week 2 complete. Scoring engine live. Target completion: July 2026.

## What it does

```
Daily pipeline
  ↓
Ingest new SAM.gov opportunities
  ↓
Run dbt models (Snowflake star schema)
  ↓
Extract requirements from solicitation text (RAG)
  ↓
Score against company profile
  ↓
Suppress disqualified opportunities
  ↓
Generate pursuit artifacts (bid/no-bid memo, compliance checklist)
  ↓
Email digest — top 5 opportunities only
  ↓
User reviews full memo in Streamlit
```

## What makes it more than a mailing list

**1. Reads the solicitation, not just metadata**

A standard alert says: `New opportunity: Cloud Support Services | NAICS: 541512 | Agency: DOT`

This system says:
```
Requires:
- 3 similar federal past performance examples
- ISO 9001 certification
- On-site support in Cambridge, MA
- Response due in 11 days
- Technical volume limited to 20 pages
```

**2. Scores against a real company profile**

Not just "NAICS matches" — but:
```
Fit score: 74

Matched:
- Azure migration experience
- Small-business eligibility
- Similar contract size

Missing:
- ISO 9001
- No explicit DOT past performance
- Deadline is short
```

**3. Detects hidden disqualifiers**

- Requires facility clearance
- Requires incumbent transition plan
- Requires past performance within last 3 years
- Set-aside does not match company certifications
- Deadline too soon given company bandwidth

**4. Generates pursuit artifacts**

- Bid/no-bid recommendation memo
- Compliance checklist
- Missing requirements list
- Questions for contracting officer
- Capture action items

**5. Shows you what it rejected and why**

```
143 opportunities reviewed
9 included in digest
134 excluded

Top exclusion reasons:
- 51 did not match core capabilities
- 37 deadline too soon
- 22 required certification missing
- 14 wrong set-aside
- 10 contract size outside target range
```

## Fit score formula

```
0.35 × capability_similarity      (Azure OpenAI embeddings)
0.25 × past_performance_match
0.15 × contract_size_fit
0.15 × competition_score
0.10 × strategic_fit
```

Hard gates are caps, not zeros — a disqualified opportunity surfaces with a warning rather than disappearing.

## Stack

| Layer | Technology |
|---|---|
| Data warehouse | Snowflake on Azure |
| Transformations | dbt |
| Orchestration | Apache Airflow on Azure Container Apps |
| Scoring API | FastAPI |
| Embeddings | Azure OpenAI text-embedding-3-small |
| Narrative generation | Azure OpenAI GPT-4o |
| RAG / document search | Azure AI Search |
| UI | Streamlit |
| Ingestion | Python (SAM.gov + USASpending.gov) |

## Weekly build plan

| Week | Scope | Status |
|---|---|---|
| 1 | Data foundation — Snowflake schema, dbt models, ingestion | ✅ Done |
| 2 | Scoring engine — FastAPI, hard gates, weighted score, embeddings | ✅ Done |
| 3 | RAG layer — solicitation text extraction, Azure AI Search, Streamlit UI | In progress |
| 4 | Artifacts + pipeline — GPT-4o memos, Airflow orchestration, email digest | Planned |

## License

MIT
