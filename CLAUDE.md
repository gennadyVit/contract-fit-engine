# govcontract-radar

## Project Overview
Pipeline that ingests federal contract data from SAM.gov and USASpending.gov, loads it into Snowflake, transforms it with dbt, and surfaces insights via a Streamlit dashboard.

## Stack
- **Ingestion**: Python scripts in `ingestion/` hitting SAM.gov and USASpending APIs
- **Orchestration**: Airflow DAGs in `dags/`
- **Warehouse**: Snowflake
- **Transformation**: dbt (`dbt/models/`)
- **Dashboard**: Streamlit (`dashboard/app.py`)

## Environment
Copy `.env.example` to `.env` and fill in credentials before running anything.

## Key APIs
- SAM.gov: requires `SAM_GOV_API_KEY`
- USASpending.gov: public API, no key required
