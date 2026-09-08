"""
Analytics API Endpoints

Timor-Leste Tourism Intelligence Platform

Provides:
- Dashboard KPI summary
- Review activity trends
- Top destinations
- Sentiment summary
- Dataset statistics
- Category analysis
- Municipality analysis

Important terminology:
- Stored Review Records = actual rows in the Review table.
- Destination Review Count = review_count reported for each destination.
"""

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.destination import Destination
from backend.models.review import Review
from backend.models.cluster import Cluster
from backend.models.collection_log import DataCollectionLog
from backend.schemas.analytics import (
    DashboardSummary,
    KPICard,
    TrendData,
)


router = APIRouter()


# ============================================================
# DASHBOARD SUMMARY
# ============================================================

@router.get(
    "/dashboard/summary",
    response_model=DashboardSummary
)
async def get_dashboard_summary(
    db: Session = Depends(get_db)
):
    """
    Get summary data for the main dashboard.

    total_reviews means actual stored Review records,
    not the sum of destination review_count.
    """

    # --------------------------------------------------------
    # Total destinations
    # --------------------------------------------------------

    total_destinations = (
        db.query(Destination).count()
    )


    # --------------------------------------------------------
    # Actual stored review records
    # --------------------------------------------------------

    total_reviews = (
        db.query(Review).count()
    )


    # --------------------------------------------------------
    # Average rating from stored reviews
    # --------------------------------------------------------

    avg_rating = (
        db.query(
            func.avg(Review.rating)
        )
        .filter(
            Review.rating.isnot(None),
            Review.rating > 0
        )
        .scalar()
        or 0
    )


    # --------------------------------------------------------
    # Positive sentiment
    # --------------------------------------------------------

    positive_count = (
        db.query(Review)
        .filter(
            Review.sentiment == "Positive"
        )
        .count()
    )


    positive_pct = (
        round(
            positive_count /
            total_reviews *
            100,
            1
        )
        if total_reviews > 0
        else 0
    )


    # --------------------------------------------------------
    # Active clusters
    # --------------------------------------------------------

    active_clusters = (
        db.query(
            Cluster.cluster_id
        )
        .distinct()
        .count()
    )


    # --------------------------------------------------------
    # Last successful collection
    # --------------------------------------------------------

    last_log = (
        db.query(DataCollectionLog)
        .filter(
            DataCollectionLog.status == "success"
        )
        .order_by(
            DataCollectionLog.completed_at.desc()
        )
        .first()
    )


    last_update = (
        last_log.completed_at.isoformat()
        if last_log and last_log.completed_at
        else None
    )


    # --------------------------------------------------------
    # KPI cards
    # --------------------------------------------------------

    kpis = [

        KPICard(
            label="Total Destinations",
            value=total_destinations,
            icon="fa-map-marker-alt",
            trend=0
        ),

        KPICard(
            label="Stored Review Records",
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
        average_rating=round(
            avg_rating,
            1
        ),
        positive_sentiment=positive_pct,
        active_clusters=active_clusters,
        last_update=last_update,
        kpis=kpis
    )


# ============================================================
# REVIEW ACTIVITY TREND
# ============================================================

@router.get("/dashboard/trends")
async def get_trends(
    days: int = Query(
        30,
        ge=1,
        le=365
    ),
    db: Session = Depends(get_db)
):
    """
    Get stored review activity by date.

    This is NOT a tourist-arrival or visitor-count trend.
    It represents the number of stored Review records
    grouped by review date.
    """

    start_date = (
        datetime.now() -
        timedelta(days=days)
    )


    reviews_by_date = (
        db.query(
            func.date(
                Review.review_date
            ).label("date"),

            func.count(
                Review.id
            ).label("count")
        )
        .filter(
            Review.review_date.isnot(None),
            Review.review_date >= start_date
        )
        .group_by(
            func.date(
                Review.review_date
            )
        )
        .order_by(
            func.date(
                Review.review_date
            )
        )
        .all()
    )


    labels = [

        r.date.strftime("%Y-%m-%d")
        if hasattr(r.date, "strftime")
        else str(r.date)

        for r in reviews_by_date
    ]


    values = [

        int(r.count or 0)

        for r in reviews_by_date
    ]


    return TrendData(
        labels=labels,

        datasets=[

            {
                "label": "Stored Review Records",
                "data": values,
                "borderColor": "#2563EB",
                "backgroundColor": (
                    "rgba(37, 99, 235, 0.1)"
                ),
                "fill": True
            }

        ]
    )


# ============================================================
# TOP DESTINATIONS
# ============================================================

@router.get("/dashboard/top-destinations")
async def get_top_destinations(
    limit: int = Query(
        6,
        ge=1,
        le=20
    ),
    db: Session = Depends(get_db)
):
    """
    Get top destinations ranked by destination review_count.

    This endpoint intentionally uses review_count rather than
    popularity_score because the EDA section is specifically
    "Most Reviewed Destinations".
    """

    destinations = (
        db.query(Destination)

        .order_by(
            Destination.review_count.desc(),
            Destination.rating.desc(),
            Destination.name.asc()
        )

        .limit(limit)

        .all()
    )


    return [

        {
            "id": destination.id,

            "name": destination.name,

            "rating": destination.rating,

            "review_count": (
                destination.review_count or 0
            ),

            "category": (
                destination.category
                or "Unknown"
            ),

            "municipality": (
                destination.municipality
                or "Unknown"
            ),

            "popularity_score": (
                destination.popularity_score
                or 0
            )
        }

        for destination in destinations
    ]


# ============================================================
# SENTIMENT SUMMARY
# ============================================================

@router.get("/dashboard/sentiment-summary")
async def get_sentiment_summary(
    db: Session = Depends(get_db)
):
    """
    Get overall sentiment summary based on actual
    stored Review records.
    """

    total = (
        db.query(Review).count()
    )


    positive = (
        db.query(Review)
        .filter(
            Review.sentiment == "Positive"
        )
        .count()
    )


    neutral = (
        db.query(Review)
        .filter(
            Review.sentiment == "Neutral"
        )
        .count()
    )


    negative = (
        db.query(Review)
        .filter(
            Review.sentiment == "Negative"
        )
        .count()
    )


    return {

        "positive": (
            round(
                positive / total * 100,
                1
            )
            if total > 0
            else 0
        ),

        "neutral": (
            round(
                neutral / total * 100,
                1
            )
            if total > 0
            else 0
        ),

        "negative": (
            round(
                negative / total * 100,
                1
            )
            if total > 0
            else 0
        ),

        "total": total
    }


# ============================================================
# COMPREHENSIVE STATISTICS
# ============================================================

@router.get("/statistics")
async def get_statistics(
    db: Session = Depends(get_db)
):
    """
    Get comprehensive EDA statistics.

    The response explicitly separates:
    - stored review records
    - destination review count
    """

    # --------------------------------------------------------
    # Basic counts
    # --------------------------------------------------------

    total_destinations = (
        db.query(Destination).count()
    )


    stored_review_records = (
        db.query(Review).count()
    )


    # --------------------------------------------------------
    # Destination review count
    #
    # This represents the review_count values reported for
    # destinations and is NOT the same as stored review rows.
    # --------------------------------------------------------

    destination_review_count = (
        db.query(
            func.coalesce(
                func.sum(
                    Destination.review_count
                ),
                0
            )
        )
        .scalar()
        or 0
    )


    # --------------------------------------------------------
    # Average destination rating
    # --------------------------------------------------------

    average_destination_rating = (
        db.query(
            func.avg(
                Destination.rating
            )
        )
        .filter(
            Destination.rating.isnot(None),
            Destination.rating > 0
        )
        .scalar()
        or 0
    )


    # --------------------------------------------------------
    # Category distribution
    # --------------------------------------------------------

    categories = (
        db.query(
            Destination.category,
            func.count(
                Destination.id
            ).label("count")
        )
        .group_by(
            Destination.category
        )
        .order_by(
            func.count(
                Destination.id
            ).desc()
        )
        .all()
    )


    # --------------------------------------------------------
    # Municipality distribution
    # --------------------------------------------------------

    municipalities = (
        db.query(
            Destination.municipality,
            func.count(
                Destination.id
            ).label("count")
        )
        .group_by(
            Destination.municipality
        )
        .order_by(
            func.count(
                Destination.id
            ).desc()
        )
        .all()
    )


    # --------------------------------------------------------
    # Rating distribution
    #
    # Use <= 5 for the final bucket so rating 5.0 is included.
    # --------------------------------------------------------

    rating_ranges = [

        ("1-2", 1, 2),

        ("2-3", 2, 3),

        ("3-4", 3, 4),

        ("4-5", 4, 5)

    ]


    rating_dist = []


    for index, (
        label,
        min_rating,
        max_rating
    ) in enumerate(rating_ranges):

        if index == len(rating_ranges) - 1:

            count = (
                db.query(Destination)
                .filter(
                    Destination.rating >= min_rating,
                    Destination.rating <= max_rating
                )
                .count()
            )

        else:

            count = (
                db.query(Destination)
                .filter(
                    Destination.rating >= min_rating,
                    Destination.rating < max_rating
                )
                .count()
            )


        rating_dist.append({

            "range": label,

            "count": count

        })


    # --------------------------------------------------------
    # Sentiment distribution
    # --------------------------------------------------------

    sentiment_dist = (
        db.query(
            Review.sentiment,
            func.count(
                Review.id
            ).label("count")
        )
        .group_by(
            Review.sentiment
        )
        .order_by(
            func.count(
                Review.id
            ).desc()
        )
        .all()
    )


    # --------------------------------------------------------
    # Return
    # --------------------------------------------------------

    return {

        "total_destinations":
            total_destinations,

        # Actual rows in Review table
        "stored_review_records":
            stored_review_records,

        # Sum of Destination.review_count
        "destination_review_count":
            int(destination_review_count),

        # Keep this for compatibility with existing frontend
        "total_reviews":
            stored_review_records,

        "average_destination_rating":
            round(
                average_destination_rating,
                2
            ),

        "categories": [

            {
                "category":
                    category or "Unknown",

                "count":
                    count
            }

            for category, count
            in categories
        ],

        "municipalities": [

            {
                "municipality":
                    municipality or "Unknown",

                "count":
                    count
            }

            for municipality, count
            in municipalities
        ],

        "rating_distribution":
            rating_dist,

        "sentiment_distribution": [

            {
                "sentiment":
                    sentiment or "Unknown",

                "count":
                    count
            }

            for sentiment, count
            in sentiment_dist
        ]
    }


# ============================================================
# CATEGORY ANALYSIS
# ============================================================

@router.get("/categories")
async def get_category_analysis(
    db: Session = Depends(get_db)
):
    """
    Analyze destination categories.
    """

    results = (
        db.query(

            Destination.category,

            func.avg(
                Destination.rating
            ).label("avg_rating"),

            func.avg(
                Destination.popularity_score
            ).label("avg_popularity"),

            func.count(
                Destination.id
            ).label("count")
        )

        .group_by(
            Destination.category
        )

        .order_by(
            func.count(
                Destination.id
            ).desc()
        )

        .all()
    )


    return [

        {

            "category":
                result[0] or "Unknown",

            "avg_rating":
                round(
                    result[1],
                    2
                )
                if result[1] is not None
                else 0,

            "avg_popularity":
                round(
                    result[2],
                    2
                )
                if result[2] is not None
                else 0,

            "count":
                int(result[3] or 0)
        }

        for result in results
    ]


# ============================================================
# MUNICIPALITY ANALYSIS
# ============================================================

@router.get("/municipalities")
async def get_municipality_analysis(
    db: Session = Depends(get_db)
):
    """
    Analyze destination distribution by municipality.
    """

    results = (
        db.query(

            Destination.municipality,

            func.avg(
                Destination.rating
            ).label("avg_rating"),

            func.avg(
                Destination.popularity_score
            ).label("avg_popularity"),

            func.count(
                Destination.id
            ).label("count")
        )

        .group_by(
            Destination.municipality
        )

        .order_by(
            func.count(
                Destination.id
            ).desc()
        )

        .all()
    )


    return [

        {

            "municipality":
                result[0] or "Unknown",

            "avg_rating":
                round(
                    result[1],
                    2
                )
                if result[1] is not None
                else 0,

            "avg_popularity":
                round(
                    result[2],
                    2
                )
                if result[2] is not None
                else 0,

            "count":
                int(result[3] or 0)
        }

        for result in results
    ]