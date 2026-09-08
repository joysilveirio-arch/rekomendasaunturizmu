"""
Recommendation Pydantic Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from backend.schemas.destination import DestinationResponse


class RecommendationRequest(BaseModel):
    user_type: str = Field(..., max_length=50, description="Adventure, Culture, Relaxation, Nature, Beach")
    category: Optional[str] = Field(None, max_length=50)
    municipality: Optional[str] = Field(None, max_length=100)
    min_rating: float = Field(default=3.0, ge=0, le=5)
    budget: str = Field(default="Medium", max_length=20, description="Low, Medium, High")
    limit: int = Field(default=10, ge=1, le=50)


class RecommendationItem(BaseModel):
    destination: DestinationResponse
    score: float
    match_details: Optional[dict] = None


class RecommendationResponse(BaseModel):
    recommendations: List[RecommendationItem]
    total: int
    query_params: dict