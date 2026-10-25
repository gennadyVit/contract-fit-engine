"""
Daily GovContract Radar pipeline:
  1. Ingest new SAM.gov opportunities → Snowflake RAW
  2. Run dbt models (RAW → DIMENSIONS → MARTS)
  3. Embed new opportunities (NULL EMBEDDING rows)
  4. Score and rank all active opportunities
  5. Send email digest of top 5
"""
from datetime import datetime, timedelta
import os

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

default_args = {
    "owner": "govcontract",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
    "email_on_failure": True,
    "email": [os.getenv("DIGEST_EMAIL", "yezavit@yahoo.com")],
}

with DAG(
    dag_id="govcontract_daily_pipeline",
    description="Ingest → dbt → embed → score → digest",
    schedule_interval="0 6 * * 1",  # Monday 6 AM UTC
    start_date=datetime(2026, 7, 1),
    catchup=False,
    default_args=default_args,
    tags=["govcontract"],
) as dag:

    def ingest_sam_gov(**context):
        import sys
        sys.path.insert(0, "/opt/airflow/govcontract/ingestion")
        from snowflake_conn import get_connection
        from sam_gov import fetch_and_load
        import os

        # DAG runs weekly, so pull the full past week
        today = datetime.utcnow()
        week_ago = today - timedelta(days=7)
        posted_from = week_ago.strftime("%m/%d/%Y")
        posted_to = today.strftime("%m/%d/%Y")

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(f"USE WAREHOUSE {os.getenv('SNOWFLAKE_WAREHOUSE', 'COMPUTE_WH')}")
        count = fetch_and_load(cursor, posted_from=posted_from, posted_to=posted_to)
        conn.commit()
        conn.close()
        print(f"Ingested {count} new opportunities")
        return count

    def embed_new_opportunities(**context):
        import sys
        sys.path.insert(0, "/opt/airflow/govcontract/ingestion")
        from precompute_embeddings import main
        main()

    def score_opportunities(**context):
        import sys
        sys.path.insert(0, "/opt/airflow/govcontract/ingestion")
        from scoring import main
        sys.argv = ["scoring.py", "technova"]  # main() reads the profile from argv
        main()

    def send_digest(**context):
        import sys
        sys.path.insert(0, "/opt/airflow/govcontract")
        from airflow.scripts.digest import send_top_opportunities
        send_top_opportunities()

    task_ingest = PythonOperator(
        task_id="ingest_sam_gov",
        python_callable=ingest_sam_gov,
    )

    # profiles.yml reads the key from a file; the container only has it as a
    # base64-encoded PEM in SNOWFLAKE_PRIVATE_KEY, so write it out first.
    task_dbt = BashOperator(
        task_id="run_dbt",
        bash_command=(
            "set -e && "
            "echo \"$SNOWFLAKE_PRIVATE_KEY\" | base64 -d > /tmp/rsa_key.p8 && "
            "chmod 600 /tmp/rsa_key.p8 && "
            "export SNOWFLAKE_PRIVATE_KEY_PATH=/tmp/rsa_key.p8 && "
            "cd /opt/airflow/govcontract/dbt && "
            "dbt run --profiles-dir /opt/airflow/govcontract/dbt --target prod"
        ),
    )

    task_embed = PythonOperator(
        task_id="embed_new_opportunities",
        python_callable=embed_new_opportunities,
    )

    task_score = PythonOperator(
        task_id="score_opportunities",
        python_callable=score_opportunities,
    )

    task_digest = PythonOperator(
        task_id="send_digest",
        python_callable=send_digest,
    )

    task_ingest >> task_dbt >> task_embed >> task_score >> task_digest
