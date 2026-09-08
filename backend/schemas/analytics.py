"""
Analytics Pydantic Schemas
"""

from pydantic import BaseModel
from typing import List, Dict, Any, Optional


class KPICard(BaseModel):
    label: str
    value: Any
    icon: str
    trend: Optional[float] = None
    trend_label: Optional[str] = None


class DashboardSummary(BaseModel):
    total_destinations: int
    total_reviews: int
    average_rating: float
    positive_sentiment: float
    active_clusters: int
    last_update: Optional[str] = None
    kpis: List[KPICard]


class SentimentSummary(BaseModel):
    positive: float
    neutral: float
    negative: float
    total: int
    average_score: float


class TrendData(BaseModel):
    labels: List[str]
    datasets: List[Dict[str, Any]]


class ChartData(BaseModel):
    labels: List[str]
    values: List[float]
    colors: List[str]