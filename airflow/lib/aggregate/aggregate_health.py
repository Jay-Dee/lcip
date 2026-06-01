from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from airflow.exceptions import AirflowException
from airflow.models import DagRun, TaskInstance
from airflow.settings import Session

from lib.common.health_schema import HealthEvent


DB_DAG_ID = "db_health_dag"
DB_TASK_ID = "get_db_health_status"

SYS_DAG_ID = "system_health_check"
SYS_TASK_ID = "get_system_health_status"

DB_MAX_AGE_MINUTES = 10
SYS_MAX_AGE_MINUTES = 5


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _parse_timestamp(value: str | None) -> datetime | None:
    if not value:
        return None

    try:
        # Handles ISO timestamps ending in Z as UTC.
        normalised = value.replace("Z", "+00:00")
        parsed = datetime.fromisoformat(normalised)

        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=timezone.utc)

        return parsed.astimezone(timezone.utc)
    except ValueError:
        return None


def _build_missing_component_event(
    *,
    component: str,
    reason: str,
) -> dict[str, Any]:
    return HealthEvent(
        component=component,
        status="unhealthy",
        metrics={},
        meta={
            "reason": reason,
        },
    ).to_dict()


def _build_stale_component_event(
    *,
    event: dict[str, Any],
    age_seconds: float,
    max_age_seconds: int,
) -> dict[str, Any]:
    component = event.get("component", "unknown")

    return HealthEvent(
        component=component,
        status="warning",
        metrics=event.get("metrics", {}),
        meta={
            **event.get("meta", {}),
            "reason": "stale_health_event",
            "source_status": event.get("status"),
            "age_seconds": round(age_seconds, 2),
            "max_age_seconds": max_age_seconds,
        },
    ).to_dict()


def _get_latest_task_event(
    *,
    dag_id: str,
    task_id: str,
    component: str,
    max_age_minutes: int,
) -> dict[str, Any]:
    session = Session()

    try:
        latest_dag_run = (
            session.query(DagRun)
            .filter(DagRun.dag_id == dag_id)
            .order_by(DagRun.execution_date.desc())
            .first()
        )

        if latest_dag_run is None:
            return _build_missing_component_event(
                component=component,
                reason=f"no_dag_run_found_for_{dag_id}",
            )

        task_instance = (
            session.query(TaskInstance)
            .filter(
                TaskInstance.dag_id == dag_id,
                TaskInstance.task_id == task_id,
                TaskInstance.run_id == latest_dag_run.run_id,
            )
            .first()
        )

        if task_instance is None:
            return _build_missing_component_event(
                component=component,
                reason=f"no_task_instance_found_for_{dag_id}.{task_id}",
            )

        if task_instance.state != "success":
            return _build_missing_component_event(
                component=component,
                reason=f"latest_task_state_{task_instance.state}",
            )

        event = task_instance.xcom_pull(
            task_ids=task_id,
            key="return_value",
            session=session,
        )

        if not isinstance(event, dict):
            return _build_missing_component_event(
                component=component,
                reason="latest_task_return_value_missing_or_not_dict",
            )

        timestamp = _parse_timestamp(event.get("timestamp"))
        if timestamp is None:
            return _build_missing_component_event(
                component=component,
                reason="latest_task_event_timestamp_missing_or_invalid",
            )

        max_age_seconds = max_age_minutes * 60
        age_seconds = (_utc_now() - timestamp).total_seconds()

        if age_seconds > max_age_seconds:
            return _build_stale_component_event(
                event=event,
                age_seconds=age_seconds,
                max_age_seconds=max_age_seconds,
            )

        return event

    finally:
        session.close()


def _aggregate_status(component_events: list[dict[str, Any]]) -> str:
    statuses = [event.get("status", "unhealthy") for event in component_events]

    if "unhealthy" in statuses:
        return "unhealthy"

    if "warning" in statuses:
        return "warning"

    return "healthy"


def get_platform_health_status() -> dict[str, Any]:
    component_events = [
        _get_latest_task_event(
            dag_id=DB_DAG_ID,
            task_id=DB_TASK_ID,
            component="lcip-data-store",
            max_age_minutes=DB_MAX_AGE_MINUTES,
        ),
        _get_latest_task_event(
            dag_id=SYS_DAG_ID,
            task_id=SYS_TASK_ID,
            component="airflow-runtime-host",
            max_age_minutes=SYS_MAX_AGE_MINUTES,
        ),
    ]

    status = _aggregate_status(component_events)

    event = HealthEvent(
        component="lcip-platform",
        status=status,
        metrics={
            "component_count": len(component_events),
            "healthy_count": sum(
                1 for component_event in component_events
                if component_event.get("status") == "healthy"
            ),
            "warning_count": sum(
                1 for component_event in component_events
                if component_event.get("status") == "warning"
            ),
            "unhealthy_count": sum(
                1 for component_event in component_events
                if component_event.get("status") == "unhealthy"
            ),
        },
        meta={
            "components": component_events,
        },
    )

    payload = event.to_dict()

    if status == "unhealthy":
        raise AirflowException(f"LCIP platform health check failed: {payload}")

    return payload