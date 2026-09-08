"""
Review Pydantic Schemas
"""

from typing import List, Optional
from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict


# ============================================================
# REVIEW BASE SCHEMA
# ============================================================

class ReviewBase(BaseModel):
    destination_id: int

    review_text: Optional[str] = None

    rating: float = Field(
        ...,
        ge=0,
        le=5
    )

    sentiment: str = Field(
        default="Neutral",
        max_length=20
    )

    sentiment_score: float = Field(
        default=0.0
    )

    source: Optional[str] = Field(
        default=None,
        max_length=100
    )

    review_date: Optional[datetime] = None


# ============================================================
# REVIEW CREATE
# ============================================================

class ReviewCreate(ReviewBase):
    pass


# ============================================================
# REVIEW RESPONSE
# ============================================================

class ReviewResponse(ReviewBase):
    id: int

    created_at: datetime

    destination_name: Optional[str] = None

    model_config = ConfigDict(
        from_attributes=True
    )


# ============================================================
# REVIEW LIST RESPONSE
# ============================================================

class ReviewListResponse(BaseModel):
    total: int

    items: List[ReviewResponse]