from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Literal

Status = Literal["healthy", "warning", "unhealthy"]

@dataclass
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
    
    def __str__(self) -> str:
        metrics_str = ", ".join(f"{k}={v}" for k, v in self.metrics.items())
        meta_str = ", ".join(f"{k}={v}" for k, v in self.meta.items())
        return (f"HealthEvent(component={self.component}, status={self.status}," 
                f"timestamp={self.timestamp}, metrics={metrics_str}, meta={meta_str})")