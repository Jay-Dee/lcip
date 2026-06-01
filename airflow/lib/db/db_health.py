import logging

from lib.common.db_client import get_postgres_connection
from lib.common.health_schema import HealthEvent

logger = logging.getLogger(__name__)
    
def get_db_health_status():
    logger.info("Performing database health check...")
    with get_postgres_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1;")
            result = cur.fetchone()

    db_health_event = HealthEvent(
        component="database",
        status="healthy" if result and result[0] == 1 else "unhealthy"
    )

    logger.info(f"Database health check: {db_health_event}")

    return db_health_event