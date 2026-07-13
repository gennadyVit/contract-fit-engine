#!/bin/bash
set -e

# Initialize the metadata DB
airflow db migrate

# Create admin user with static password (idempotent)
airflow users create \
    --username admin \
    --password GovContract2026! \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email yezavit@yahoo.com \
    2>/dev/null || airflow users set-password \
        --username admin \
        --password GovContract2026!

# Start all Airflow components
exec airflow standalone
