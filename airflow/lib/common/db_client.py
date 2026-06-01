from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Iterator

import psycopg2
from psycopg2.extensions import connection

# Load /opt/airflow/.env before reading environment variables.
from lib.common import config as _config  # noqa: F401


@contextmanager
def get_lcip_data_store_connection() -> Iterator[connection]:
    """Connect to the LCIP domain datastore, not the Airflow metadata store."""
    conn = psycopg2.connect(
        host=os.getenv("LCIP_DATA_STORE_HOST", "lcip-data-store"),
        port=os.getenv("LCIP_DATA_STORE_PORT", "5432"),
        database=os.getenv("LCIP_DATA_STORE_DB", "lcip"),
        user=os.getenv("LCIP_DATA_STORE_USER", "lcip"),
        password=os.getenv("LCIP_DATA_STORE_PASSWORD", "lcip"),
    )

    try:
        yield conn
    finally:
        conn.close()
