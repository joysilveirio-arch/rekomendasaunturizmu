"""
Data Mining API Endpoints

Provides:
- Sentiment analysis
- Sentiment summary
- Sentiment keywords
- K-Means clustering
- Clustering evaluation
- Cluster statistics
- Cluster details
- Clustering status
"""

from collections import Counter
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.database import get_db
from backend.services.sentiment import (
    SentimentAnalyzer,
    get_sentiment_summary_for_destination,
)
from backend.services.clustering import (
    ClusteringService,
    get_cluster_info_for_destination,
)
from backend.models.destination import Destination
from backend.models.review import Review
from backend.models.cluster import Cluster


router = APIRouter()

sentiment_analyzer = SentimentAnalyzer()


# ================================================================
# SENTIMENT
# ================================================================

@router.post("/sentiment")
async def analyze_sentiment(
    text: str,
    db: Session = Depends(get_db)
):
    """Analyze sentiment of a text."""

    result = sentiment_analyzer.analyze(text)

    return result


@router.get("/sentiment-summary")
async def get_sentiment_summary_global(
    db: Session = Depends(get_db)
):
    """Get global sentiment summary."""

    total = db.query(Review).count()

    if total == 0:
        return {
            "positive": 0,
            "neutral": 0,
            "negative": 0,
            "total": 0,
            "average_score": 0,
        }

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

    avg_score = (
        db.query(func.avg(Review.sentiment_score))
        .scalar()
        or 0
    )

    return {
        "positive": round(
            positive / total * 100,
            1
        ),
        "neutral": round(
            neutral / total * 100,
            1
        ),
        "negative": round(
            negative / total * 100,
            1
        ),
        "total": total,
        "average_score": round(
            float(avg_score),
            3
        ),
    }


@router.get("/sentiment-keywords")
async def get_sentiment_keywords(
    limit: int = Query(
        10,
        ge=1,
        le=50
    ),
    db: Session = Depends(get_db)
):
    """Get top positive and negative keywords."""

    reviews = (
        db.query(Review.review_text)
        .filter(
            Review.review_text.isnot(None)
        )
        .all()
    )

    positive_keywords = []
    negative_keywords = []

    for review in reviews:

        text = review[0]

        if not text:
            continue

        result = sentiment_analyzer.analyze(text)

        keywords = (
            sentiment_analyzer
            .extract_keywords(text)
        )

        if result["sentiment"] == "Positive":
            positive_keywords.extend(
                keywords[:5]
            )

        elif result["sentiment"] == "Negative":
            negative_keywords.extend(
                keywords[:5]
            )

    positive_counter = Counter(
        positive_keywords
    )

    negative_counter = Counter(
        negative_keywords
    )

    return {
        "positive": [
            {
                "word": word,
                "count": count
            }
            for word, count
            in positive_counter.most_common(limit)
        ],
        "negative": [
            {
                "word": word,
                "count": count
            }
            for word, count
            in negative_counter.most_common(limit)
        ],
    }


# ================================================================
# K-MEANS CLUSTERING
# ================================================================

@router.post("/clustering")
async def run_clustering(
    n_clusters: int = Query(
        4,
        ge=2,
        le=10
    ),
    db: Session = Depends(get_db)
):
    """
    Run K-Means clustering.

    Returns:
    - number of clusters
    - number of destinations
    - number of features
    - silhouette score
    - cluster quality
    - cluster distribution
    """

    service = ClusteringService(db)

    try:

        clusters_df = service.perform_clustering(
            n_clusters=n_clusters
        )

        if clusters_df.empty:
            raise HTTPException(
                status_code=400,
                detail=(
                    "No destination data available "
                    "for clustering"
                )
            )

        evaluation = (
            service.get_evaluation_summary()
        )

        return {
            "status": "success",
            "algorithm": "K-Means",
            "n_clusters": n_clusters,
            "n_destinations": len(
                clusters_df
            ),
            "n_features": len(
                service.FEATURE_NAMES
            ),
            "features": (
                service.FEATURE_NAMES
            ),
            "silhouette_score": (
                service.silhouette_score
            ),
            "cluster_quality": (
                evaluation.get(
                    "cluster_quality"
                )
            ),
            "cluster_sizes": (
                evaluation.get(
                    "cluster_sizes",
                    {}
                )
            ),
            "message": (
                f"Clustering completed "
                f"with {n_clusters} clusters"
            ),
        }

    except HTTPException:
        raise

    except Exception as exc:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=(
                f"Clustering failed: {str(exc)}"
            )
        )


# ================================================================
# K-MEANS EVALUATION
# ================================================================

@router.get("/clustering/evaluation")
async def evaluate_clustering(
    k_min: int = Query(
        2,
        ge=2,
        le=10
    ),
    k_max: int = Query(
        6,
        ge=2,
        le=10
    ),
    db: Session = Depends(get_db)
):
    """
    Evaluate K-Means using several K values.

    Uses Silhouette Score to compare cluster quality.

    Example:
        K = 2, 3, 4, 5, 6
    """

    if k_min > k_max:
        raise HTTPException(
            status_code=400,
            detail="k_min must be <= k_max"
        )

    service = ClusteringService(db)

    try:

        k_values = list(
            range(
                k_min,
                k_max + 1
            )
        )

        results = service.evaluate_k_values(
            k_values=k_values
        )

        if not results:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Not enough data for "
                    "clustering evaluation"
                )
            )

        best_result = max(
            results,
            key=lambda item:
            item["silhouette_score"]
        )

        return {
            "status": "success",
            "algorithm": "K-Means",
            "evaluation_metric": (
                "Silhouette Score"
            ),
            "k_range": {
                "min": k_min,
                "max": k_max
            },
            "results": results,
            "best_k": best_result["k"],
            "best_silhouette_score": (
                best_result[
                    "silhouette_score"
                ]
            ),
            "interpretation": (
                "Higher Silhouette Score "
                "indicates better-defined "
                "and better-separated clusters."
            ),
        }

    except HTTPException:
        raise

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Clustering evaluation failed: "
                f"{str(exc)}"
            )
        )


# ================================================================
# CLUSTER RESULTS
# ================================================================

@router.get("/clusters")
async def get_clusters(
    db: Session = Depends(get_db)
):
    """
    Get cluster analysis results.

    Includes:
    - cluster ID
    - cluster name
    - destination count
    - average rating
    - average popularity
    - destination list
    """

    results = (
        db.query(
            Destination.id,
            Destination.name,
            Destination.rating,
            Destination.popularity_score,
            Destination.category,
            Destination.municipality,
            Destination.price_level,
            Cluster.cluster_id,
            Cluster.cluster_name,
            Cluster.cluster_score,
        )
        .join(
            Cluster,
            Cluster.destination_id
            == Destination.id
        )
        .order_by(
            Cluster.cluster_id,
            Destination.id
        )
        .all()
    )

    if not results:
        return []

    cluster_stats = {}

    for result in results:

        cluster_id = int(
            result[7]
        )

        if cluster_id not in cluster_stats:

            cluster_stats[cluster_id] = {
                "cluster_id": cluster_id,
                "cluster_name": result[8],
                "destinations": [],
                "avg_rating": 0.0,
                "avg_popularity": 0.0,
                "count": 0,
                "silhouette_score": (
                    float(result[9])
                    if result[9] is not None
                    else None
                ),
            }

        cluster_stats[
            cluster_id
        ]["destinations"].append({
            "id": result[0],
            "name": result[1],
            "rating": (
                float(result[2])
                if result[2] is not None
                else 0.0
            ),
            "popularity_score": (
                float(result[3])
                if result[3] is not None
                else 0.0
            ),
            "category": result[4],
            "municipality": result[5],
            "price_level": result[6],
        })

        cluster_stats[
            cluster_id
        ]["count"] += 1

        cluster_stats[
            cluster_id
        ]["avg_rating"] += (
            float(result[2])
            if result[2] is not None
            else 0.0
        )

        cluster_stats[
            cluster_id
        ]["avg_popularity"] += (
            float(result[3])
            if result[3] is not None
            else 0.0
        )

    # Calculate averages
    for cluster_id in cluster_stats:

        count = cluster_stats[
            cluster_id
        ]["count"]

        if count > 0:

            cluster_stats[
                cluster_id
            ]["avg_rating"] = round(
                cluster_stats[
                    cluster_id
                ]["avg_rating"] / count,
                2
            )

            cluster_stats[
                cluster_id
            ]["avg_popularity"] = round(
                cluster_stats[
                    cluster_id
                ]["avg_popularity"] / count,
                2
            )

    return list(
        cluster_stats.values()
    )


# ================================================================
# CLUSTER DETAIL
# ================================================================

@router.get("/clusters/{cluster_id}")
async def get_cluster_detail(
    cluster_id: int,
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific cluster."""

    destinations = (
        db.query(Destination)
        .join(
            Cluster,
            Cluster.destination_id
            == Destination.id
        )
        .filter(
            Cluster.cluster_id
            == cluster_id
        )
        .order_by(
            Destination.id
        )
        .all()
    )

    if not destinations:
        raise HTTPException(
            status_code=404,
            detail=(
                f"Cluster {cluster_id} "
                "not found"
            )
        )

    cluster = (
        db.query(Cluster)
        .filter(
            Cluster.cluster_id
            == cluster_id
        )
        .first()
    )

    destination_data = []

    for dest in destinations:

        destination_data.append({
            "id": dest.id,
            "name": dest.name,
            "rating": (
                float(dest.rating)
                if dest.rating is not None
                else 0.0
            ),
            "popularity_score": (
                float(dest.popularity_score)
                if dest.popularity_score is not None
                else 0.0
            ),
            "review_count": (
                int(dest.review_count)
                if dest.review_count is not None
                else 0
            ),
            "category": dest.category,
            "municipality": dest.municipality,
            "price_level": dest.price_level,
        })

    return {
        "cluster_id": cluster_id,
        "cluster_name": (
            cluster.cluster_name
            if cluster
            else f"Cluster {cluster_id}"
        ),
        "cluster_score": (
            float(cluster.cluster_score)
            if cluster
            and cluster.cluster_score is not None
            else None
        ),
        "total_destinations": len(
            destination_data
        ),
        "destinations": destination_data,
    }


# ================================================================
# CLUSTER STATISTICS / INTERPRETATION
# ================================================================

@router.get("/clustering/statistics")
async def get_clustering_statistics(
    db: Session = Depends(get_db)
):
    """
    Get detailed cluster statistics.

    Includes:
    - cluster size
    - average rating
    - average popularity
    - average review count
    - dominant category
    - category distribution
    - municipality distribution
    """

    service = ClusteringService(db)

    try:

        # If clustering has already been performed,
        # calculate statistics from current assignments.
        clusters = (
            db.query(Cluster)
            .order_by(
                Cluster.cluster_id
            )
            .all()
        )

        if not clusters:
            return {
                "status": "not_run",
                "clusters": [],
                "total_clusters": 0,
            }

        destination_ids = [
            cluster.destination_id
            for cluster in clusters
        ]

        labels = [
            cluster.cluster_id
            for cluster in clusters
        ]

        statistics = (
            service._calculate_cluster_statistics(
                destination_ids=destination_ids,
                labels=labels
            )
        )

        return {
            "status": "success",
            "total_clusters": len(
                statistics
            ),
            "total_destinations": len(
                destination_ids
            ),
            "clusters": list(
                statistics.values()
            ),
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Could not retrieve "
                f"cluster statistics: {str(exc)}"
            )
        )


# ================================================================
# CLUSTER STATUS
# ================================================================

@router.get("/clustering/status")
async def get_clustering_status(
    db: Session = Depends(get_db)
):
    """
    Get current clustering status and metrics.

    Silhouette Score is retrieved from the
    stored Cluster records.
    """

    clusters = (
        db.query(
            Cluster.cluster_id,
            Cluster.cluster_score
        )
        .all()
    )

    if not clusters:

        return {
            "status": "not_run",
            "algorithm": "K-Means",
            "n_clusters": 0,
            "n_destinations": 0,
            "silhouette_score": None,
            "cluster_quality": "Not evaluated",
            "message": (
                "Clustering has not "
                "been run yet"
            ),
        }

    cluster_ids = sorted(
        set(
            int(row[0])
            for row in clusters
        )
    )

    silhouette = None

    for row in clusters:

        if row[1] is not None:
            silhouette = float(row[1])
            break

    if silhouette is None:
        quality = "Not evaluated"

    elif silhouette >= 0.70:
        quality = "Excellent"

    elif silhouette >= 0.50:
        quality = "Good"

    elif silhouette >= 0.25:
        quality = "Fair"

    else:
        quality = "Weak"

    cluster_sizes = {}

    for cluster_id in cluster_ids:

        cluster_sizes[str(cluster_id)] = sum(
            1
            for row in clusters
            if int(row[0]) == cluster_id
        )

    return {
        "status": "completed",
        "algorithm": "K-Means",
        "n_clusters": len(
            cluster_ids
        ),
        "n_destinations": len(
            clusters
        ),
        "silhouette_score": (
            round(
                silhouette,
                4
            )
            if silhouette is not None
            else None
        ),
        "cluster_quality": quality,
        "cluster_sizes": cluster_sizes,
        "message": (
            f"Clustering completed "
            f"with {len(cluster_ids)} clusters"
        ),
    }


# ================================================================
# DESTINATION CLUSTER INFORMATION
# ================================================================

@router.get("/destinations/{destination_id}/cluster")
async def get_destination_cluster(
    destination_id: int,
    db: Session = Depends(get_db)
):
    """Get cluster information for one destination."""

    destination = (
        db.query(Destination)
        .filter(
            Destination.id
            == destination_id
        )
        .first()
    )

    if not destination:

        raise HTTPException(
            status_code=404,
            detail="Destination not found"
        )

    result = (
        get_cluster_info_for_destination(
            destination_id,
            db
        )
    )

    if not result:

        return {
            "destination_id": destination_id,
            "destination_name": destination.name,
            "cluster": None,
            "message": (
                "Destination has not "
                "been clustered yet"
            ),
        }

    return {
        "destination_id": destination_id,
        "destination_name": destination.name,
        "cluster": result,
    }