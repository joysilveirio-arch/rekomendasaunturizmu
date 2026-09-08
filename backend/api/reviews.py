"""
Reviews API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from backend.database import get_db
from backend.models.review import Review
from backend.models.destination import Destination
from backend.schemas.review import ReviewCreate, ReviewResponse, ReviewListResponse
from backend.services.sentiment import SentimentAnalyzer

router = APIRouter()
sentiment_analyzer = SentimentAnalyzer()


@router.get("/", response_model=ReviewListResponse)
async def get_reviews(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    destination_id: Optional[int] = None,
    sentiment: Optional[str] = Query(None, regex="^(Positive|Neutral|Negative)$"),
    min_rating: Optional[float] = Query(None, ge=0, le=5),
    max_rating: Optional[float] = Query(None, ge=0, le=5),
    db: Session = Depends(get_db)
):
    """Get list of reviews with filtering"""
    
    query = db.query(Review)
    
    if destination_id:
        query = query.filter(Review.destination_id == destination_id)
    
    if sentiment:
        query = query.filter(Review.sentiment == sentiment)
    
    if min_rating:
        query = query.filter(Review.rating >= min_rating)
    
    if max_rating:
        query = query.filter(Review.rating <= max_rating)
    
    total = query.count()
    reviews = query.order_by(Review.created_at.desc()).offset(skip).limit(limit).all()
    
    # Add destination names
    result_items = []
    for review in reviews:
        item = ReviewResponse.model_validate(review)
        dest = db.query(Destination).filter(Destination.id == review.destination_id).first()
        if dest:
            item.destination_name = dest.name
        result_items.append(item)
    
    return ReviewListResponse(
        total=total,
        items=result_items
    )


@router.get("/{review_id}", response_model=ReviewResponse)
async def get_review(
    review_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific review by ID"""
    
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    result = ReviewResponse.model_validate(review)
    dest = db.query(Destination).filter(Destination.id == review.destination_id).first()
    if dest:
        result.destination_name = dest.name
    
    return result


@router.post("/", response_model=ReviewResponse)
async def create_review(
    review: ReviewCreate,
    db: Session = Depends(get_db)
):
    """Create a new review with automatic sentiment analysis"""
    
    # Check if destination exists
    dest = db.query(Destination).filter(Destination.id == review.destination_id).first()
    if not dest:
        raise HTTPException(status_code=404, detail="Destination not found")
    
    # Analyze sentiment if text is provided
    sentiment_result = {"sentiment": "Neutral", "score": 0.0}
    if review.review_text:
        sentiment_result = sentiment_analyzer.analyze(review.review_text)
    
    db_review = Review(
        destination_id=review.destination_id,
        review_text=review.review_text,
        rating=review.rating,
        sentiment=sentiment_result["sentiment"],
        sentiment_score=sentiment_result["score"],
        source=review.source,
        review_date=review.review_date
    )
    
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    
    # Update destination average rating
    avg_rating = db.query(Review).filter(Review.destination_id == dest.id).with_entities(
        db.func.avg(Review.rating)
    ).scalar()
    
    dest.rating = round(avg_rating, 1) if avg_rating else 0
    dest.review_count = db.query(Review).filter(Review.destination_id == dest.id).count()
    db.commit()
    
    result = ReviewResponse.model_validate(db_review)
    result.destination_name = dest.name
    return result


@router.get("/destination/{destination_id}/sentiment-summary")
async def get_destination_sentiment(
    destination_id: int,
    db: Session = Depends(get_db)
):
    """Get sentiment summary for a destination"""
    
    dest = db.query(Destination).filter(Destination.id == destination_id).first()
    if not dest:
        raise HTTPException(status_code=404, detail="Destination not found")
    
    reviews = db.query(Review).filter(Review.destination_id == destination_id).all()
    
    if not reviews:
        return {
            "positive": 0,
            "neutral": 0,
            "negative": 0,
            "total": 0,
            "average_score": 0
        }
    
    total = len(reviews)
    positive = sum(1 for r in reviews if r.sentiment == "Positive")
    neutral = sum(1 for r in reviews if r.sentiment == "Neutral")
    negative = sum(1 for r in reviews if r.sentiment == "Negative")
    avg_score = sum(r.sentiment_score for r in reviews) / total if total > 0 else 0
    
    return {
        "positive": round(positive / total * 100, 1),
        "neutral": round(neutral / total * 100, 1),
        "negative": round(negative / total * 100, 1),
        "total": total,
        "average_score": round(avg_score, 3)
    }