"""
Destination Pydantic Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class DestinationBase(BaseModel):
    name: str = Field(..., max_length=200)
    description: Optional[str] = None
    municipality: str = Field(..., max_length=100)
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    category: str = Field(..., max_length=50)
    rating: float = Field(default=0.0, ge=0, le=5)
    review_count: int = Field(default=0, ge=0)
    price_level: str = Field(default="Medium", max_length=20)
    popularity_score: float = Field(default=0.0, ge=0, le=100)


class DestinationCreate(DestinationBase):
    pass


class DestinationUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    municipality: Optional[str] = Field(None, max_length=100)
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    category: Optional[str] = Field(None, max_length=50)
    rating: Optional[float] = Field(None, ge=0, le=5)
    review_count: Optional[int] = Field(None, ge=0)
    price_level: Optional[str] = Field(None, max_length=20)
    popularity_score: Optional[float] = Field(None, ge=0, le=100)


class DestinationResponse(DestinationBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    # Additional fields from relationships
    sentiment_summary: Optional[dict] = None
    cluster_info: Optional[dict] = None
    
    class Config:
        from_attributes = True


class DestinationListResponse(BaseModel):
    total: int
    items: List[DestinationResponse]