from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

from lib.db.db_health import get_db_health_status


default_args = {
    "owner": "lcip",
    "retries": 1,
    "retry_delay": timedelta(seconds=10),
}

with DAG(
    dag_id="db_health_dag",
    description="LCIP DB health check DAG",
    default_args=default_args,
    start_date=datetime(2024, 1, 1),
    schedule_interval="*/5 * * * *",  # every 5 minutes
    catchup=False,
    tags=["lcip", "health", "postgres"],
) as dag:

    db_health_check_task = PythonOperator(
        task_id="get_db_health_status",
        python_callable=get_db_health_status,
    )

    db_health_check_task