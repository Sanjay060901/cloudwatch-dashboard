from pydantic import BaseModel
from datetime import datetime
from typing import Dict, Any

class MetricPoint(BaseModel):
    value: float | None
    timestamp: str | None

class LatestMetrics(BaseModel):
    metrics: Dict[str, MetricPoint | None]
    updated_at: str
