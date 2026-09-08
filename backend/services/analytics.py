"""
Analytics Service

Provides analytics and statistics for the dashboard.
"""

from typing import Dict, Any, List

from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.models.destination import Destination
from backend.models.review import Review
from backend.models.cluster import Cluster
from backend.models.collection_log import DataCollectionLog

from backend.utils.logger import get_logger


logger = get_logger(__name__)


class AnalyticsService:
    """Analytics service for tourism data."""

    def __init__(self, db: Session):
        self.db = db

    # ============================================================
    # DASHBOARD SUMMARY
    # ============================================================

    def get_dashboard_summary(self) -> Dict[str, Any]:
        """Get summary data for the dashboard."""

        # Total destinations
        total_destinations = (
            self.db
            .query(Destination)
            .count()
        )

        # Total reviews
        total_reviews = (
            self.db
            .query(Review)
            .count()
        )

        # Average rating
        avg_rating = (
            self.db
            .query(func.avg(Review.rating))
            .scalar()
            or 0
        )

        # Sentiment distribution
        positive = (
            self.db
            .query(Review)
            .filter(
                Review.sentiment == "Positive"
            )
            .count()
        )

        neutral = (
            self.db
            .query(Review)
            .filter(
                Review.sentiment == "Neutral"
            )
            .count()
        )

        negative = (
            self.db
            .query(Review)
            .filter(
                Review.sentiment == "Negative"
            )
            .count()
        )

        positive_pct = (
            round(
                positive / total_reviews * 100,
                1
            )
            if total_reviews > 0
            else 0
        )

        # Active clusters
        active_clusters = (
            self.db
            .query(Cluster.cluster_id)
            .distinct()
            .count()
        )

        # Last update
        last_log = (
            self.db
            .query(DataCollectionLog)
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
            if last_log
            else None
        )

        return {
            "total_destinations": total_destinations,

            "total_reviews": total_reviews,

            "average_rating": round(
                float(avg_rating),
                1
            ),

            "positive_sentiment": positive_pct,

            "active_clusters": active_clusters,

            "last_update": last_update,

            "sentiment": {
                "positive": positive_pct,

                "neutral": (
                    round(
                        neutral / total_reviews * 100,
                        1
                    )
                    if total_reviews > 0
                    else 0
                ),

                "negative": (
                    round(
                        negative / total_reviews * 100,
                        1
                    )
                    if total_reviews > 0
                    else 0
                ),
            },
        }

    # ============================================================
    # TREND DATA
    # ============================================================

    def get_trend_data(
        self,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get trend data for charts."""

        start_date = (
            datetime.now()
            - timedelta(days=days)
        )

        reviews_by_date = (
            self.db
            .query(
                func.date(
                    Review.review_date
                ).label("date"),

                func.count(
                    Review.id
                ).label("count"),
            )
            .filter(
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
            row[0]
            for row in reviews_by_date
        ]

        values = [
            row[1]
            for row in reviews_by_date
        ]

        return {
            "labels": labels,
            "values": values,
        }

    # ============================================================
    # TOP DESTINATIONS
    # ============================================================

    def get_top_destinations(
        self,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get top destinations by popularity."""

        destinations = (
            self.db
            .query(Destination)
            .order_by(
                Destination.popularity_score.desc()
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
                    destination.review_count
                ),

                "category": destination.category,

                "popularity_score": (
                    destination.popularity_score
                ),
            }
            for destination in destinations
        ]

    # ============================================================
    # CATEGORY ANALYSIS
    # ============================================================

    def get_category_analysis(
        self
    ) -> List[Dict[str, Any]]:
        """Get category analysis."""

        results = (
            self.db
            .query(
                Destination.category,

                func.avg(
                    Destination.rating
                ).label("avg_rating"),

                func.avg(
                    Destination.popularity_score
                ).label("avg_popularity"),

                func.count(
                    Destination.id
                ).label("count"),
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
                "category": (
                    row[0]
                    or "Unknown"
                ),

                "avg_rating": (
                    round(
                        float(row[1]),
                        2
                    )
                    if row[1] is not None
                    else 0
                ),

                "avg_popularity": (
                    round(
                        float(row[2]),
                        2
                    )
                    if row[2] is not None
                    else 0
                ),

                "count": int(row[3]),
            }
            for row in results
        ]

    # ============================================================
    # MUNICIPALITY ANALYSIS
    # ============================================================

    def get_municipality_analysis(
        self
    ) -> List[Dict[str, Any]]:
        """
        Get tourism destination statistics
        grouped by municipality.
        """

        logger.info(
            "Running municipality analysis..."
        )

        results = (
            self.db
            .query(
                Destination.municipality,

                func.avg(
                    Destination.rating
                ).label("avg_rating"),

                func.avg(
                    Destination.popularity_score
                ).label("avg_popularity"),

                func.count(
                    Destination.id
                ).label("count"),
            )
            .filter(
                Destination.municipality.isnot(None)
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

        data = [
            {
                "municipality": (
                    row[0]
                    or "Unknown"
                ),

                "avg_rating": (
                    round(
                        float(row[1]),
                        2
                    )
                    if row[1] is not None
                    else 0
                ),

                "avg_popularity": (
                    round(
                        float(row[2]),
                        2
                    )
                    if row[2] is not None
                    else 0
                ),

                "count": int(row[3]),
            }
            for row in results
        ]

        logger.info(
            f"Municipality analysis returned "
            f"{len(data)} municipalities."
        )

        return data