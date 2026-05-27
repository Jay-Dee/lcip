from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

from lib.system.system_health import run_system_health_check


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
        task_id="check_local_system_health",
        python_callable=run_system_health_check,
    )

    system_health_task