from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

from lib.db.postgres_db_health import postgres_health_check


default_args = {
    "owner": "lcip",
    "retries": 1,
    "retry_delay": timedelta(seconds=10),
}

with DAG(
    dag_id="postgres_health_dag",
    description="LCIP Postgres health check DAG",
    default_args=default_args,
    start_date=datetime(2024, 1, 1),
    schedule_interval="*/5 * * * *",  # every 5 minutes
    catchup=False,
    tags=["lcip", "health", "postgres"],
) as dag:

    check_db = PythonOperator(
        task_id="postgres_health_check",
        python_callable=postgres_health_check,
    )

    check_db