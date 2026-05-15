# govcontract-radar

Azure-native federal contract intelligence platform for small business opportunity discovery.

## Status

Work in progress. Target completion: July 2026.

## Overview

Ingests public procurement data from SAM.gov and USAspending.gov, models it
into analytics-ready tables, scores opportunities against a configurable
company profile, and surfaces matches through a Streamlit dashboard.

## Stack

- Azure Blob Storage (raw landing zone)
- Snowflake on Azure (data warehouse)
- dbt (transformations, tests, documentation)
- Apache Airflow on Azure Container Apps (orchestration)
- Azure Database for PostgreSQL (application data)
- Azure Key Vault (secrets)
- Python (ingestion)
- Streamlit on Azure App Service (UI)

## Documentation

Architecture diagram, setup instructions, and demo screenshots coming in
later commits.

## License

MIT
