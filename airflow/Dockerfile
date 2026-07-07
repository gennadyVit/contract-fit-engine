FROM apache/airflow:2.9.2

USER root
RUN apt-get update && apt-get install -y git python3-venv && apt-get clean

# Install dbt-snowflake in an isolated virtualenv to avoid Airflow dependency conflicts
RUN python3 -m venv /opt/dbt-venv && \
    /opt/dbt-venv/bin/pip install --no-cache-dir dbt-snowflake

# Make dbt available on PATH via a wrapper script
RUN echo '#!/bin/bash\n/opt/dbt-venv/bin/dbt "$@"' > /usr/local/bin/dbt && \
    chmod +x /usr/local/bin/dbt

USER airflow

# Copy project code into image
COPY --chown=airflow:root ingestion/ /opt/airflow/govcontract/ingestion/
COPY --chown=airflow:root airflow/dags/ /opt/airflow/dags/
COPY --chown=airflow:root airflow/scripts/ /opt/airflow/govcontract/airflow/scripts/

# Install ingestion dependencies into Airflow's Python (not dbt venv)
RUN pip install --no-cache-dir \
    snowflake-connector-python==3.10.0 \
    cryptography \
    azure-identity==1.17.1 \
    azure-keyvault-secrets==4.8.0 \
    openai>=1.50.0 \
    requests==2.32.3 \
    python-dotenv==1.0.1
