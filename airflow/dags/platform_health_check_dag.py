from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

from lib.aggregate.aggregate_health import get_platform_health_status


default_args = {
    "owner": "lcip",
    "retries": 1,
    "retry_delay": timedelta(seconds=10),
}


with DAG(
    dag_id="platform_health_check",
    description="LCIP platform aggregate health check DAG",
    default_args=default_args,
    start_date=datetime(2024, 1, 1),
    schedule_interval="*/10 * * * *",
    catchup=False,
    tags=["lcip", "health", "platform"],
) as dag:

    aggregate_health = PythonOperator(
        task_id="get_platform_health_status",
        python_callable=get_platform_health_status,
    )

    aggregate_health