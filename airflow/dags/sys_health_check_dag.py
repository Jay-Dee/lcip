from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

from lib.system.system_health import get_system_health_status


DEFAULT_ARGS = {
    "owner": "lcip",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
}


with DAG(
    dag_id="system_health_check",
    description="Monitor local CPU and memory health",
    default_args=DEFAULT_ARGS,
    start_date=datetime(2025, 1, 1),
    schedule="*/2 * * * *",
    catchup=False,
    tags=["health", "monitoring", "system"],
) as dag:

    system_health_task = PythonOperator(
        task_id="get_system_health_status",
        python_callable=get_system_health_status,
    )

    system_health_task