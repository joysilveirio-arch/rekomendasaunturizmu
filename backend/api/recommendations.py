"""
Recommendations API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from backend.database import get_db
from backend.schemas.recommendation import (
    RecommendationRequest, RecommendationResponse, RecommendationItem
)
from backend.services.recommendation import RecommendationService

router = APIRouter()


@router.post("/", response_model=RecommendationResponse)
async def get_recommendations(
    request: RecommendationRequest,
    db: Session = Depends(get_db)
):
    """Get personalized tourism recommendations"""
    
    service = RecommendationService(db)
    
    recommendations = service.get_recommendations(
        user_type=request.user_type,
        category=request.category,
        municipality=request.municipality,
        min_rating=request.min_rating,
        budget=request.budget,
        limit=request.limit
    )
    
    return RecommendationResponse(
        recommendations=recommendations,
        total=len(recommendations),
        query_params=request.model_dump()
    )


@router.get("/")
async def get_recommendations_get(
    user_type: str = Query(..., max_length=50),
    category: Optional[str] = None,
    municipality: Optional[str] = None,
    min_rating: float = Query(3.0, ge=0, le=5),
    budget: str = Query("Medium", max_length=20),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Get personalized tourism recommendations (GET method for simplicity)"""
    
    request = RecommendationRequest(
        user_type=user_type,
        category=category,
        municipality=municipality,
        min_rating=min_rating,
        budget=budget,
        limit=limit
    )
    
    return await get_recommendations(request, db)


@router.get("/user-types")
async def get_user_types():
    """Get available user types for recommendations"""
    
    return {
        "user_types": [
            "Adventure",
            "Culture",
            "Relaxation",
            "Nature",
            "Beach",
            "Family",
            "Solo",
            "Group"
        ]
    }


@router.get("/budget-options")
async def get_budget_options():
    """Get available budget options"""
    
    return {
        "budget_options": [
            {"value": "Low", "label": "Low"},
            {"value": "Medium", "label": "Medium"},
            {"value": "High", "label": "High"}
        ]
    }