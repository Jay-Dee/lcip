from __future__ import annotations

from airflow.exceptions import AirflowException

from lib.common.health_schema import HealthEvent


def raise_for_unhealthy(event: HealthEvent) -> None:
    """Translate LCIP health status into Airflow task state."""
    if event.status == "unhealthy":
        raise AirflowException(f"Health check failed: {event.to_dict()}")
