from __future__ import annotations

import logging

from lib.common.db_client import get_lcip_data_store_connection
from lib.common.health_schema import HealthEvent

logger = logging.getLogger(__name__)


def get_db_health_status() -> HealthEvent:
    logger.info("Performing LCIP domain datastore health check...")

    try:
        with get_lcip_data_store_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1;")
                result = cur.fetchone()

        status = "healthy" if result and result[0] == 1 else "unhealthy"
        event = HealthEvent(
            component="lcip-data-store",
            status=status,
            metrics={"select_1_result": result[0] if result else None},
        )

    except Exception as exc:
        logger.exception("LCIP domain datastore health check failed")
        event = HealthEvent(
            component="lcip-data-store",
            status="unhealthy",
            meta={"error": str(exc)},
        )

    logger.info("LCIP domain datastore health check result: %s", event.to_dict())
    return event
