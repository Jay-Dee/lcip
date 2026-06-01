from __future__ import annotations

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

from lib.common.health_policy import raise_for_unhealthy
from lib.db.db_health import get_db_health_status

DEFAULT_ARGS = {
    "owner": "lcip",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(seconds=10),
}


def run_db_health_check() -> dict:
    event = get_db_health_status()
    raise_for_unhealthy(event)
    return event.to_dict()


with DAG(
    dag_id="db_health_dag",
    description="Monitor the LCIP domain datastore health",
    default_args=DEFAULT_ARGS,
    start_date=datetime(2024, 1, 1),
    schedule="*/5 * * * *",
    catchup=False,
    tags=["lcip", "health", "data-store", "postgres"],
) as dag:
    db_health_check_task = PythonOperator(
        task_id="get_db_health_status",
        python_callable=run_db_health_check,
    )
