"""
Database Seeding Script

Loads tourism data from the local Google Places crawler dataset.
"""

import datetime

from sqlalchemy.orm import Session

from backend.database import SessionLocal

from backend.models.destination import Destination
from backend.models.review import Review
from backend.models.cluster import Cluster
from backend.models.recommendation import Recommendation
from backend.models.collection_log import DataCollectionLog

from backend.data_sources.mock_source import MockDataSource

from backend.services.sentiment import SentimentAnalyzer
from backend.services.clustering import ClusteringService
from backend.services.recommendation import RecommendationService

from backend.utils.logger import get_logger


logger = get_logger(__name__)


def parse_review_date(value):
    """
    Mengubah tanggal review dari string ISO 8601
    menjadi Python datetime yang dapat disimpan oleh SQLite.
    """

    if not value:
        return None

    # Jika data sudah berupa datetime
    if isinstance(value, datetime.datetime):
        return value

    # Jika data berupa date
    if isinstance(value, datetime.date):
        return datetime.datetime.combine(
            value,
            datetime.time.min
        )

    try:
        # Contoh data:
        # 2026-09-02T23:03:05.607Z

        if isinstance(value, str):
            # Ubah Z menjadi timezone UTC
            dt = datetime.datetime.fromisoformat(
                value.replace("Z", "+00:00")
            )
        else:
            return None

        # SQLite DateTime lebih aman menggunakan
        # datetime tanpa timezone
        if dt.tzinfo is not None:
            dt = dt.astimezone(
                datetime.timezone.utc
            ).replace(tzinfo=None)

        return dt

    except (ValueError, TypeError, AttributeError):
        logger.warning(
            f"Invalid review date: {value}"
        )
        return None


def seed_database():
    """Load dataset data into the database."""

    db: Session = SessionLocal()

    try:
        logger.info(
            "Starting database seeding from local dataset..."
        )

        # ========================================================
        # LOAD DATA SOURCE
        # ========================================================

        data_source = MockDataSource()

        source_destinations = (
            data_source.get_destinations()
        )

        source_reviews = (
            data_source.get_reviews()
        )

        logger.info(
            f"Loaded {len(source_destinations)} destinations "
            f"and {len(source_reviews)} reviews from dataset."
        )

        # ========================================================
        # CLEAR EXISTING DATA
        # ========================================================

        logger.info(
            "Clearing existing database data..."
        )

        db.query(Recommendation).delete()
        db.query(Cluster).delete()
        db.query(Review).delete()
        db.query(Destination).delete()
        db.query(DataCollectionLog).delete()

        db.commit()

        # ========================================================
        # CREATE DESTINATIONS
        # ========================================================

        destinations = []

        # Map Google Places place_id
        # -> database destination.id
        destination_map = {}

        for data in source_destinations:

            destination_data = {
                "name": (
                    data.get("name")
                    or "Unknown Destination"
                ),

                "description": (
                    data.get("description")
                    or ""
                ),

                "municipality": (
                    data.get("municipality")
                    or data.get("city")
                    or "Unknown"
                ),

                "location": data.get("address"),

                "latitude": data.get("latitude"),

                "longitude": data.get("longitude"),

                "category": (
                    data.get("category")
                    or "Other"
                ),

                "rating": (
                    data.get("rating")
                    or 0.0
                ),

                "review_count": (
                    data.get("review_count")
                    or 0
                ),

                "price_level": (
                    data.get("price_level")
                    or "Medium"
                ),

                "popularity_score": (
                    data.get("popularity_score")
                    or 0.0
                ),
            }

            destination = Destination(
                **destination_data
            )

            db.add(destination)

            # Supaya destination.id tersedia
            db.flush()

            destinations.append(destination)

            place_id = data.get("place_id")

            if place_id:
                destination_map[
                    place_id
                ] = destination.id

        db.commit()

        logger.info(
            f"Created {len(destinations)} "
            f"destinations in database."
        )

        # ========================================================
        # CREATE REVIEWS
        # ========================================================

        sentiment_analyzer = SentimentAnalyzer()

        reviews_created = 0
        reviews_skipped = 0

        for data in source_reviews:

            place_id = data.get("place_id")

            destination_id = destination_map.get(
                place_id
            )

            # Skip review if its destination
            # cannot be found
            if destination_id is None:

                reviews_skipped += 1

                continue

            review_text = (
                data.get("review_text")
                or data.get("text_translated")
                or data.get("text_original")
                or ""
            )

            rating = data.get("rating")

            if rating is None:
                rating = 0.0

            # ----------------------------------------------------
            # PARSE REVIEW DATE
            # ----------------------------------------------------

            review_date = parse_review_date(
                data.get("review_date")
            )

            # ----------------------------------------------------
            # SENTIMENT ANALYSIS
            # ----------------------------------------------------

            sentiment_result = (
                sentiment_analyzer.analyze(
                    review_text
                )
            )

            # ----------------------------------------------------
            # CREATE REVIEW
            # ----------------------------------------------------

            review = Review(
                destination_id=destination_id,

                review_text=review_text,

                rating=float(rating),

                sentiment=(
                    sentiment_result["sentiment"]
                ),

                sentiment_score=(
                    sentiment_result["score"]
                ),

                source=data.get(
                    "source",
                    "google_places_dataset"
                ),

                review_date=review_date,
            )

            db.add(review)

            reviews_created += 1

        db.commit()

        logger.info(
            f"Created {reviews_created} reviews."
        )

        if reviews_skipped:

            logger.warning(
                f"Skipped {reviews_skipped} reviews because "
                f"their destination could not be matched."
            )

        # ========================================================
        # UPDATE DESTINATION REVIEW STATISTICS
        # ========================================================

        logger.info(
            "Updating destination ratings and review counts..."
        )

        for destination in destinations:

            reviews = (
                db.query(Review)
                .filter(
                    Review.destination_id
                    == destination.id
                )
                .all()
            )

            if reviews:

                average_rating = (
                    sum(
                        review.rating
                        for review in reviews
                    )
                    / len(reviews)
                )

                destination.rating = round(
                    average_rating,
                    1
                )

                destination.review_count = len(
                    reviews
                )

        db.commit()

        logger.info(
            "Destination review statistics updated."
        )

        # ========================================================
        # RUN CLUSTERING
        # ========================================================

        logger.info(
            "Running clustering..."
        )

        clustering_service = (
            ClusteringService(db)
        )

        clustering_service.perform_clustering()

        for destination in destinations:

            cluster_id = (
                clustering_service
                .get_cluster_id(
                    destination.id
                )
            )

            if cluster_id is not None:

                cluster_label = (
                    clustering_service
                    .get_cluster_label(
                        destination.id
                    )
                )

                cluster = Cluster(
                    destination_id=destination.id,

                    cluster_id=cluster_id,

                    cluster_name=cluster_label,

                    cluster_score=0.5,

                    created_at=datetime.datetime.now(),
                )

                db.add(cluster)

        db.commit()

        logger.info(
            "Clustering completed."
        )

        # ========================================================
        # GENERATE RECOMMENDATIONS
        # ========================================================

        logger.info(
            "Generating recommendations..."
        )

        recommendation_service = (
            RecommendationService(db)
        )

        for user_type in [
            "Adventure",
            "Culture",
            "Relaxation",
            "Nature",
            "Beach",
        ]:

            for category in [
                "Beach",
                "Nature",
                "Cultural",
                "Adventure",
            ]:

                recommendations = (
                    recommendation_service
                    .get_recommendations(
                        user_type=user_type,
                        category=category,
                        min_rating=4.0,
                        budget="Medium",
                    )
                )

                for rec in recommendations:

                    if not rec.destination:
                        continue

                    db_recommendation = Recommendation(
                        destination_id=(
                            rec.destination.id
                        ),

                        user_type=user_type,

                        category=category,

                        recommendation_score=(
                            rec.score
                        ),
                    )

                    db.add(
                        db_recommendation
                    )

        db.commit()

        logger.info(
            "Recommendations generated."
        )

        # ========================================================
        # COLLECTION LOG
        # ========================================================

        log = DataCollectionLog(
            source="google_places_dataset",

            status="success",

            records_collected=(
                len(source_destinations)
            ),

            message=(
                f"Loaded {len(source_destinations)} "
                f"destinations and "
                f"{reviews_created} reviews "
                f"from local Google Places dataset."
            ),

            started_at=datetime.datetime.now(),

            completed_at=datetime.datetime.now(),
        )

        db.add(log)

        db.commit()

        # ========================================================
        # FINAL RESULT
        # ========================================================

        logger.info(
            "Database seeding completed successfully!"
        )

        print()

        print("=" * 60)
        print("DATABASE SEEDING COMPLETED")
        print("=" * 60)

        print(
            f"Destinations loaded : "
            f"{len(destinations)}"
        )

        print(
            f"Reviews loaded      : "
            f"{reviews_created}"
        )

        print(
            f"Reviews skipped     : "
            f"{reviews_skipped}"
        )

        print("=" * 60)

    except Exception as e:

        logger.error(
            f"Error seeding database: {str(e)}"
        )

        db.rollback()

        raise

    finally:

        db.close()


if __name__ == "__main__":
    seed_database()