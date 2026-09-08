"""
Analytics API Endpoints
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import Optional

from backend.database import get_db
from backend.models.destination import Destination
from backend.models.review import Review
from backend.models.cluster import Cluster
from backend.models.collection_log import DataCollectionLog
from backend.schemas.analytics import DashboardSummary, KPICard, TrendData

router = APIRouter()


@router.get("/dashboard/summary", response_model=DashboardSummary)
async def get_dashboard_summary(db: Session = Depends(get_db)):
    """Get summary data for the dashboard"""

    # Count total destinations
    total_destinations = db.query(Destination).count()

    # Count total reviews
    total_reviews = db.query(Review).count()

    # Average rating
    avg_rating = db.query(func.avg(Review.rating)).scalar() or 0

    # Positive sentiment
    positive_count = (
        db.query(Review)
        .filter(Review.sentiment == "Positive")
        .count()
    )

    positive_pct = (
        round(positive_count / total_reviews * 100, 1)
        if total_reviews > 0
        else 0
    )

    # Active clusters
    active_clusters = (
        db.query(Cluster.cluster_id)
        .distinct()
        .count()
    )

    # Last update
    last_log = (
        db.query(DataCollectionLog)
        .filter(DataCollectionLog.status == "success")
        .order_by(DataCollectionLog.completed_at.desc())
        .first()
    )

    last_update = (
        last_log.completed_at.isoformat()
        if last_log
        else None
    )

    # KPI Cards
    kpis = [
        KPICard(
            label="Total Destinations",
            value=total_destinations,
            icon="fa-map-marker-alt",
            trend=0
        ),
        KPICard(
            label="Total Reviews",
            value=total_reviews,
            icon="fa-comments",
            trend=0
        ),
        KPICard(
            label="Average Rating",
            value=f"{avg_rating:.1f}",
            icon="fa-star",
            trend=0
        ),
        KPICard(
            label="Positive Sentiment",
            value=f"{positive_pct}%",
            icon="fa-smile",
            trend=0
        ),
        KPICard(
            label="Active Clusters",
            value=active_clusters,
            icon="fa-layer-group",
            trend=0
        ),
        KPICard(
            label="Data Status",
            value="Online",
            icon="fa-circle",
            trend=0,
            trend_label="Live"
        )
    ]

    return DashboardSummary(
        total_destinations=total_destinations,
        total_reviews=total_reviews,
        average_rating=round(avg_rating, 1),
        positive_sentiment=positive_pct,
        active_clusters=active_clusters,
        last_update=last_update,
        kpis=kpis
    )


@router.get("/dashboard/trends")
async def get_trends(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Get tourism trend data"""

    start_date = datetime.now() - timedelta(days=days)

    # Get reviews by day
    reviews_by_date = (
        db.query(
            func.date(Review.review_date).label("date"),
            func.count(Review.id).label("count")
        )
        .filter(Review.review_date >= start_date)
        .group_by(func.date(Review.review_date))
        .order_by(func.date(Review.review_date))
        .all()
    )

    # SQLite func.date() can return a string.
    # Therefore, check whether the value has strftime().
    labels = [
        r.date.strftime("%Y-%m-%d")
        if hasattr(r.date, "strftime")
        else str(r.date)
        for r in reviews_by_date
    ]

    values = [r.count for r in reviews_by_date]

    return TrendData(
        labels=labels,
        datasets=[
            {
                "label": "Reviews",
                "data": values,
                "borderColor": "#2563EB",
                "backgroundColor": "rgba(37, 99, 235, 0.1)",
                "fill": True
            }
        ]
    )


@router.get("/dashboard/top-destinations")
async def get_top_destinations(
    limit: int = Query(6, ge=1, le=20),
    db: Session = Depends(get_db)
):
    """Get top destinations by popularity"""

    destinations = (
        db.query(Destination)
        .order_by(Destination.popularity_score.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "id": d.id,
            "name": d.name,
            "rating": d.rating,
            "review_count": d.review_count,
            "category": d.category,
            "popularity_score": d.popularity_score
        }
        for d in destinations
    ]


@router.get("/dashboard/sentiment-summary")
async def get_sentiment_summary(
    db: Session = Depends(get_db)
):
    """Get overall sentiment summary"""

    total = db.query(Review).count()

    positive = (
        db.query(Review)
        .filter(Review.sentiment == "Positive")
        .count()
    )

    neutral = (
        db.query(Review)
        .filter(Review.sentiment == "Neutral")
        .count()
    )

    negative = (
        db.query(Review)
        .filter(Review.sentiment == "Negative")
        .count()
    )

    return {
        "positive": round(positive / total * 100, 1)
        if total > 0 else 0,

        "neutral": round(neutral / total * 100, 1)
        if total > 0 else 0,

        "negative": round(negative / total * 100, 1)
        if total > 0 else 0,

        "total": total
    }


@router.get("/statistics")
async def get_statistics(
    db: Session = Depends(get_db)
):
    """Get comprehensive statistics"""

    total_destinations = db.query(Destination).count()
    total_reviews = db.query(Review).count()

    # Category distribution
    categories = (
        db.query(
            Destination.category,
            func.count(Destination.id).label("count")
        )
        .group_by(Destination.category)
        .all()
    )

    # Municipality distribution
    municipalities = (
        db.query(
            Destination.municipality,
            func.count(Destination.id).label("count")
        )
        .group_by(Destination.municipality)
        .all()
    )

    # Rating distribution
    rating_ranges = [
        ("1-2", 1, 2),
        ("2-3", 2, 3),
        ("3-4", 3, 4),
        ("4-5", 4, 5)
    ]

    rating_dist = []

    for label, min_r, max_r in rating_ranges:
        count = (
            db.query(Destination)
            .filter(
                Destination.rating >= min_r,
                Destination.rating < max_r
            )
            .count()
        )

        rating_dist.append({
            "range": label,
            "count": count
        })

    # Sentiment distribution
    sentiment_dist = (
        db.query(
            Review.sentiment,
            func.count(Review.id).label("count")
        )
        .group_by(Review.sentiment)
        .all()
    )

    return {
        "total_destinations": total_destinations,
        "total_reviews": total_reviews,

        "categories": [
            {
                "name": c[0],
                "count": c[1]
            }
            for c in categories
        ],

        "municipalities": [
            {
                "name": m[0],
                "count": m[1]
            }
            for m in municipalities
        ],

        "rating_distribution": rating_dist,

        "sentiment_distribution": [
            {
                "sentiment": s[0],
                "count": s[1]
            }
            for s in sentiment_dist
        ]
    }


@router.get("/categories")
async def get_category_analysis(
    db: Session = Depends(get_db)
):
    """Get category analysis"""

    results = (
        db.query(
            Destination.category,
            func.avg(Destination.rating).label("avg_rating"),
            func.avg(Destination.popularity_score).label(
                "avg_popularity"
            ),
            func.count(Destination.id).label("count")
        )
        .group_by(Destination.category)
        .all()
    )

    return [
        {
            "category": r[0],
            "avg_rating": round(r[1], 2) if r[1] else 0,
            "avg_popularity": round(r[2], 2) if r[2] else 0,
            "count": r[3]
        }
        for r in results
    ]


@router.get("/municipalities")
async def get_municipality_analysis(
    db: Session = Depends(get_db)
):
    """Get municipality analysis"""

    results = (
        db.query(
            Destination.municipality,
            func.avg(Destination.rating).label("avg_rating"),
            func.avg(Destination.popularity_score).label(
                "avg_popularity"
            ),
            func.count(Destination.id).label("count")
        )
        .group_by(Destination.municipality)
        .all()
    )

    return [
        {
            "municipality": r[0],
            "avg_rating": round(r[1], 2) if r[1] else 0,
            "avg_popularity": round(r[2], 2) if r[2] else 0,
            "count": r[3]
        }
        for r in results
    ]