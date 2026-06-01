from __future__ import annotations

from pathlib import Path
from dotenv import load_dotenv


def load_lcip_env() -> None:
    """Load the LCIP .env file mounted into the Airflow containers."""
    env_path = Path("/opt/airflow/.env")
    if env_path.exists():
        load_dotenv(env_path)


load_lcip_env()
