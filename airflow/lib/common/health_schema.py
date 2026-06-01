from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Literal

Status = Literal["healthy", "warning", "unhealthy"]


@dataclass(frozen=True)
class HealthEvent:
    component: str
    status: Status
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    metrics: Dict[str, Any] = field(default_factory=dict)
    meta: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "component": self.component,
            "status": self.status,
            "timestamp": self.timestamp,
            "metrics": self.metrics,
            "meta": self.meta,
        }
