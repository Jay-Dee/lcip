from __future__ import annotations

import logging
import socket

import psutil

from lib.common.health_schema import HealthEvent

CPU_WARNING_THRESHOLD = 80
MEMORY_WARNING_THRESHOLD = 80

logger = logging.getLogger(__name__)


def get_system_health_status() -> HealthEvent:
    logger.info("Performing local system health check...")

    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()

    memory_percent = memory.percent
    memory_used_gb = round(memory.used / (1024**3), 2)
    memory_total_gb = round(memory.total / (1024**3), 2)

    status = (
        "healthy"
        if cpu_percent < CPU_WARNING_THRESHOLD
        and memory_percent < MEMORY_WARNING_THRESHOLD
        else "warning"
    )

    event = HealthEvent(
        component="airflow-runtime-host",
        status=status,
        metrics={
            "cpu_percent": cpu_percent,
            "memory_percent": memory_percent,
            "memory_used_gb": memory_used_gb,
            "memory_total_gb": memory_total_gb,
        },
        meta={"host": socket.gethostname()},
    )

    logger.info("Local system health check result: %s", event.to_dict())
    return event
