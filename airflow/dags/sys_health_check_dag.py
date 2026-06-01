from __future__ import annotations

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

from lib.common.health_policy import raise_for_unhealthy
from lib.system.system_health import get_system_health_status

DEFAULT_ARGS = {
    "owner": "lcip",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
}


def run_system_health_check() -> dict:
    event = get_system_health_status()
    raise_for_unhealthy(event)
    return event.to_dict()


with DAG(
    dag_id="system_health_check",
    description="Monitor local Airflow runtime CPU and memory health",
    default_args=DEFAULT_ARGS,
    start_date=datetime(2025, 1, 1),
    schedule="*/2 * * * *",
    catchup=False,
    tags=["lcip", "health", "monitoring", "system"],
) as dag:
    system_health_task = PythonOperator(
        task_id="get_system_health_status",
        python_callable=run_system_health_check,
    )
