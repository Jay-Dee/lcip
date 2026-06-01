from __future__ import annotations

import logging
import psutil

from lib.common.health_schema import HealthEvent

CPU_WARNING_THRESHOLD = 80
MEMORY_WARNING_THRESHOLD = 80

logger = logging.getLogger(__name__)

def get_system_health_status() -> HealthEvent:
    logger.info("Performing system health check...")
    cpu_percent = psutil.cpu_percent(interval=1)

    memory = psutil.virtual_memory()
    memory_percent = memory.percent
    memory_used_gb = round(memory.used / (1024**3), 2)
    memory_total_gb = round(memory.total / (1024**3), 2)

    system_health_event = HealthEvent(
        component="system",
        status="healthy" if cpu_percent < CPU_WARNING_THRESHOLD and memory_percent < MEMORY_WARNING_THRESHOLD else "warning",
        metrics={
            "cpu_percent": cpu_percent,
            "memory_percent": memory_percent,
            "memory_used_gb": memory_used_gb,
            "memory_total_gb": memory_total_gb,
        },
    )

    logger.info(f"System health check: {system_health_event}")

    return system_health_event

