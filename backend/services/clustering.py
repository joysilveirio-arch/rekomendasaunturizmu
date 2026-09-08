"""
Clustering Service

Implements K-Means clustering for tourism destinations.

Features used:
- Rating
- Review count
- Popularity score
- Sentiment score
- Price level
- Category

Evaluation:
- Silhouette Score
- Cluster size/distribution
- Cluster feature statistics
- Best K comparison
- Cluster interpretation
"""

from typing import Dict, Any, List, Optional, Tuple

import numpy as np
import pandas as pd

from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score

from sqlalchemy.orm import Session

from backend.models.destination import Destination
from backend.models.review import Review
from backend.models.cluster import Cluster
from backend.services.preprocessing import PreprocessingService
from backend.config import settings
from backend.utils.logger import get_logger


logger = get_logger(__name__)


class ClusteringService:
    """K-Means clustering service for tourism destinations."""

    FEATURE_NAMES = [
        "rating",
        "review_count",
        "popularity_score",
        "sentiment_score",
        "price_level",
        "category",
    ]

    PRICE_MAPPING = {
        "Low": 0.0,
        "Medium": 0.5,
        "High": 1.0,
    }

    CATEGORY_MAPPING = {
        "Beach": 1.0,
        "Nature": 0.75,
        "Cultural": 0.5,
        "Adventure": 0.25,
    }

    def __init__(self, db: Session):
        self.db = db
        self.preprocessor = PreprocessingService()
        self.scaler = StandardScaler()
        self.kmeans = None
        self.silhouette_score = None
        self.cluster_labels = {}
        self.evaluation_results = {}
        self.cluster_statistics = {}

        logger.info("ClusteringService initialized")

    # ============================================================
    # FEATURE ENGINEERING
    # ============================================================

    def get_destination_features(
        self,
        destination_id: int
    ) -> Optional[np.ndarray]:
        """
        Get feature vector for a single destination.

        Features:
        1. rating
        2. review_count
        3. popularity_score
        4. sentiment_score
        5. price_level
        6. category
        """

        dest = (
            self.db.query(Destination)
            .filter(Destination.id == destination_id)
            .first()
        )

        if not dest:
            return None

        reviews = (
            self.db.query(Review)
            .filter(Review.destination_id == destination_id)
            .all()
        )

        sentiment_values = []

        for review in reviews:
            if review.sentiment_score is not None:
                try:
                    sentiment_values.append(
                        float(review.sentiment_score)
                    )
                except (TypeError, ValueError):
                    continue

        if sentiment_values:
            avg_sentiment = float(
                np.mean(sentiment_values)
            )
        else:
            avg_sentiment = 0.0

        rating = self._safe_float(
            dest.rating,
            0.0
        )

        review_count = self._safe_float(
            dest.review_count,
            0.0
        )

        popularity_score = self._safe_float(
            dest.popularity_score,
            0.0
        )

        # Rating: 0-5 -> 0-1
        rating_normalized = np.clip(
            rating / 5.0,
            0.0,
            1.0
        )

        # Review count: cap at 1000
        review_count_normalized = np.clip(
            review_count / 1000.0,
            0.0,
            1.0
        )

        # Popularity: 0-100 -> 0-1
        popularity_normalized = np.clip(
            popularity_score / 100.0,
            0.0,
            1.0
        )

        # Sentiment: -1 to +1
        sentiment_normalized = np.clip(
            avg_sentiment,
            -1.0,
            1.0
        )

        price_value = self.PRICE_MAPPING.get(
            dest.price_level,
            0.5
        )

        category_value = self.CATEGORY_MAPPING.get(
            dest.category,
            0.5
        )

        features = [
            rating_normalized,
            review_count_normalized,
            popularity_normalized,
            sentiment_normalized,
            price_value,
            category_value,
        ]

        return np.array(
            features,
            dtype=float
        )

    @staticmethod
    def _safe_float(
        value: Any,
        default: float = 0.0
    ) -> float:
        """Safely convert a value to float."""

        try:
            if value is None:
                return default

            result = float(value)

            if not np.isfinite(result):
                return default

            return result

        except (TypeError, ValueError):
            return default

    # ============================================================
    # PREPARE DATA
    # ============================================================

    def prepare_data(
        self
    ) -> Tuple[np.ndarray, List[int]]:
        """
        Prepare and standardize destination data for clustering.
        """

        destinations = (
            self.db.query(Destination)
            .order_by(Destination.id)
            .all()
        )

        feature_vectors = []
        destination_ids = []

        for dest in destinations:

            features = self.get_destination_features(
                dest.id
            )

            if features is None:
                continue

            if not np.all(np.isfinite(features)):
                logger.warning(
                    f"Skipping destination {dest.id}: "
                    "invalid feature values"
                )
                continue

            feature_vectors.append(features)
            destination_ids.append(dest.id)

        if not feature_vectors:
            return (
                np.empty(
                    (0, len(self.FEATURE_NAMES))
                ),
                []
            )

        X = np.array(
            feature_vectors,
            dtype=float
        )

        X_scaled = self.scaler.fit_transform(X)

        logger.info(
            f"Prepared clustering data: "
            f"{len(destination_ids)} destinations, "
            f"{len(self.FEATURE_NAMES)} features"
        )

        return X_scaled, destination_ids

    # ============================================================
    # VALIDATE K
    # ============================================================

    def _validate_n_clusters(
        self,
        n_clusters: int,
        n_samples: int
    ) -> int:
        """Validate requested number of clusters."""

        if n_clusters is None:
            n_clusters = settings.DEFAULT_N_CLUSTERS

        try:
            n_clusters = int(n_clusters)

        except (TypeError, ValueError):
            n_clusters = settings.DEFAULT_N_CLUSTERS

        if n_clusters < 2:
            n_clusters = 2

        if n_samples > 0 and n_clusters >= n_samples:
            n_clusters = max(
                2,
                n_samples - 1
            )

        return n_clusters

    # ============================================================
    # MAIN CLUSTERING
    # ============================================================

    def perform_clustering(
        self,
        n_clusters: int = None
    ) -> pd.DataFrame:
        """
        Perform K-Means clustering.

        Returns:
            DataFrame containing destination-level
            cluster results.
        """

        X_scaled, destination_ids = (
            self.prepare_data()
        )

        if len(X_scaled) == 0:
            logger.warning(
                "No data available for clustering"
            )

            return pd.DataFrame()

        n_clusters = self._validate_n_clusters(
            n_clusters,
            len(X_scaled)
        )

        if len(X_scaled) < 3:
            logger.warning(
                "Not enough destinations for clustering evaluation"
            )

            return pd.DataFrame()

        logger.info(
            f"Starting K-Means clustering with K={n_clusters}"
        )

        self.kmeans = KMeans(
            n_clusters=n_clusters,
            random_state=settings.CLUSTERING_RANDOM_STATE,
            n_init=10
        )

        labels = self.kmeans.fit_predict(
            X_scaled
        )

        unique_labels = sorted(
            set(labels)
        )

        # --------------------------------------------------------
        # SILHOUETTE SCORE
        # --------------------------------------------------------

        if len(unique_labels) > 1:

            try:
                self.silhouette_score = float(
                    silhouette_score(
                        X_scaled,
                        labels
                    )
                )

            except Exception as exc:

                logger.warning(
                    f"Could not calculate silhouette score: {exc}"
                )

                self.silhouette_score = 0.0

        else:
            self.silhouette_score = 0.0

        self.cluster_labels = dict(
            zip(
                destination_ids,
                labels
            )
        )

        # --------------------------------------------------------
        # EVALUATION
        # --------------------------------------------------------

        self.evaluation_results = (
            self._build_evaluation(
                X_scaled=X_scaled,
                destination_ids=destination_ids,
                labels=labels,
                n_clusters=n_clusters
            )
        )

        # --------------------------------------------------------
        # CLUSTER STATISTICS
        # --------------------------------------------------------

        self.cluster_statistics = (
            self._calculate_cluster_statistics(
                destination_ids=destination_ids,
                labels=labels
            )
        )

        # --------------------------------------------------------
        # CLEAR OLD RESULTS
        # --------------------------------------------------------

        self.db.query(Cluster).delete()

        # --------------------------------------------------------
        # SAVE CLUSTER ASSIGNMENTS
        # --------------------------------------------------------

        for dest_id, cluster_id in zip(
            destination_ids,
            labels
        ):

            cluster_name = (
                self._generate_cluster_name(
                    cluster_id,
                    destination_ids,
                    labels
                )
            )

            cluster = Cluster(
                destination_id=dest_id,
                cluster_id=int(cluster_id),
                cluster_name=cluster_name,
                cluster_score=self.silhouette_score
            )

            self.db.add(cluster)

        self.db.commit()

        # --------------------------------------------------------
        # RESULT DATAFRAME
        # --------------------------------------------------------

        results = []

        destination_map = {
            dest.id: dest
            for dest in (
                self.db.query(Destination)
                .filter(
                    Destination.id.in_(
                        destination_ids
                    )
                )
                .all()
            )
        }

        for dest_id, cluster_id in zip(
            destination_ids,
            labels
        ):

            dest = destination_map.get(
                dest_id
            )

            if not dest:
                continue

            results.append({
                "destination_id": dest_id,
                "destination_name": dest.name,
                "cluster_id": int(cluster_id),
                "cluster_name": (
                    self._generate_cluster_name(
                        cluster_id,
                        destination_ids,
                        labels
                    )
                ),
                "rating": self._safe_float(
                    dest.rating,
                    0.0
                ),
                "popularity_score": self._safe_float(
                    dest.popularity_score,
                    0.0
                ),
                "review_count": self._safe_float(
                    dest.review_count,
                    0.0
                ),
                "category": dest.category,
                "municipality": dest.municipality,
                "price_level": dest.price_level,
            })

        logger.info(
            f"Clustering completed: "
            f"K={n_clusters}, "
            f"destinations={len(destination_ids)}, "
            f"silhouette={self.silhouette_score:.3f}"
        )

        return pd.DataFrame(results)

    # ============================================================
    # EVALUATION
    # ============================================================

    def evaluate_k_values(
        self,
        k_values: Optional[List[int]] = None
    ) -> List[Dict[str, Any]]:
        """
        Evaluate several K values using Silhouette Score.

        This method does NOT modify the database.

        Example:
            K = 2, 3, 4, 5, 6
        """

        X_scaled, destination_ids = (
            self.prepare_data()
        )

        if len(X_scaled) < 3:
            return []

        if not k_values:
            k_values = [
                2,
                3,
                4,
                5,
                6
            ]

        results = []

        for k in k_values:

            if k < 2 or k >= len(X_scaled):
                continue

            try:

                model = KMeans(
                    n_clusters=k,
                    random_state=settings.CLUSTERING_RANDOM_STATE,
                    n_init=10
                )

                labels = model.fit_predict(
                    X_scaled
                )

                if len(set(labels)) < 2:
                    score = 0.0

                else:
                    score = float(
                        silhouette_score(
                            X_scaled,
                            labels
                        )
                    )

                cluster_sizes = {
                    int(cluster_id): int(
                        np.sum(
                            labels == cluster_id
                        )
                    )
                    for cluster_id in sorted(
                        set(labels)
                    )
                }

                results.append({
                    "k": k,
                    "silhouette_score": round(
                        score,
                        4
                    ),
                    "cluster_sizes": cluster_sizes,
                    "total_destinations": len(
                        destination_ids
                    ),
                })

            except Exception as exc:

                logger.warning(
                    f"Evaluation failed for K={k}: {exc}"
                )

        results.sort(
            key=lambda x: x[
                "silhouette_score"
            ],
            reverse=True
        )

        return results

    def _build_evaluation(
        self,
        X_scaled: np.ndarray,
        destination_ids: List[int],
        labels: np.ndarray,
        n_clusters: int
    ) -> Dict[str, Any]:
        """Build evaluation summary for current clustering."""

        cluster_sizes = {}

        for cluster_id in sorted(
            set(labels)
        ):

            cluster_sizes[
                int(cluster_id)
            ] = int(
                np.sum(
                    labels == cluster_id
                )
            )

        score = (
            self.silhouette_score
            or 0.0
        )

        if score >= 0.70:
            quality = "Excellent"

        elif score >= 0.50:
            quality = "Good"

        elif score >= 0.25:
            quality = "Fair"

        else:
            quality = "Weak"

        return {
            "algorithm": "K-Means",
            "n_clusters": int(
                n_clusters
            ),
            "n_destinations": len(
                destination_ids
            ),
            "n_features": len(
                self.FEATURE_NAMES
            ),
            "features": self.FEATURE_NAMES.copy(),
            "silhouette_score": round(
                score,
                4
            ),
            "cluster_quality": quality,
            "cluster_sizes": cluster_sizes,
            "best_k_candidates": [],
        }

    # ============================================================
    # CLUSTER STATISTICS
    # ============================================================

    def _calculate_cluster_statistics(
        self,
        destination_ids: List[int],
        labels: np.ndarray
    ) -> Dict[int, Dict[str, Any]]:
        """
        Calculate statistics for every cluster.

        Used for cluster interpretation.
        """

        destination_map = {
            dest.id: dest
            for dest in (
                self.db.query(Destination)
                .filter(
                    Destination.id.in_(
                        destination_ids
                    )
                )
                .all()
            )
        }

        stats = {}

        for cluster_id in sorted(
            set(labels)
        ):

            cluster_destinations = []

            for dest_id, label in zip(
                destination_ids,
                labels
            ):

                if int(label) == int(
                    cluster_id
                ):

                    dest = destination_map.get(
                        dest_id
                    )

                    if dest:
                        cluster_destinations.append(
                            dest
                        )

            if not cluster_destinations:
                continue

            ratings = [
                self._safe_float(d.rating)
                for d in cluster_destinations
            ]

            popularity = [
                self._safe_float(
                    d.popularity_score
                )
                for d in cluster_destinations
            ]

            review_counts = [
                self._safe_float(
                    d.review_count
                )
                for d in cluster_destinations
            ]

            categories = [
                d.category
                for d in cluster_destinations
                if d.category
            ]

            municipalities = [
                d.municipality
                for d in cluster_destinations
                if d.municipality
            ]

            category_distribution = (
                self._count_values(
                    categories
                )
            )

            municipality_distribution = (
                self._count_values(
                    municipalities
                )
            )

            dominant_category = None

            if category_distribution:

                dominant_category = max(
                    category_distribution,
                    key=category_distribution.get
                )

            stats[int(cluster_id)] = {
                "cluster_id": int(
                    cluster_id
                ),
                "cluster_name": (
                    self._generate_cluster_name(
                        cluster_id,
                        destination_ids,
                        labels
                    )
                ),
                "count": len(
                    cluster_destinations
                ),
                "average_rating": round(
                    float(np.mean(ratings)),
                    3
                ),
                "average_popularity": round(
                    float(np.mean(popularity)),
                    3
                ),
                "average_review_count": round(
                    float(
                        np.mean(review_counts)
                    ),
                    3
                ),
                "dominant_category": (
                    dominant_category
                ),
                "category_distribution": (
                    category_distribution
                ),
                "municipality_distribution": (
                    municipality_distribution
                ),
            }

        return stats

    @staticmethod
    def _count_values(
        values: List[Any]
    ) -> Dict[str, int]:
        """Count categorical values."""

        result = {}

        for value in values:

            if value is None:
                continue

            value = str(value).strip()

            if not value:
                continue

            result[value] = (
                result.get(value, 0) + 1
            )

        return dict(
            sorted(
                result.items(),
                key=lambda item: item[1],
                reverse=True
            )
        )

    # ============================================================
    # CLUSTER INTERPRETATION
    # ============================================================

    def _generate_cluster_name(
        self,
        cluster_id: int,
        destination_ids: List[int],
        labels: List[int]
    ) -> str:
        """
        Generate descriptive cluster name.

        Interpretation is based on:
        - rating
        - popularity
        - review count
        - dominant category
        """

        cluster_dest_ids = [
            dest_id
            for dest_id, label in zip(
                destination_ids,
                labels
            )
            if int(label) == int(
                cluster_id
            )
        ]

        if not cluster_dest_ids:
            return f"Cluster {cluster_id}"

        destinations = (
            self.db.query(Destination)
            .filter(
                Destination.id.in_(
                    cluster_dest_ids
                )
            )
            .all()
        )

        if not destinations:
            return f"Cluster {cluster_id}"

        ratings = [
            self._safe_float(d.rating)
            for d in destinations
        ]

        popularity = [
            self._safe_float(
                d.popularity_score
            )
            for d in destinations
        ]

        review_counts = [
            self._safe_float(
                d.review_count
            )
            for d in destinations
        ]

        avg_rating = float(
            np.mean(ratings)
        )

        avg_popularity = float(
            np.mean(popularity)
        )

        avg_review_count = float(
            np.mean(review_counts)
        )

        categories = [
            d.category
            for d in destinations
            if d.category
        ]

        category_counts = (
            self._count_values(
                categories
            )
        )

        dominant_category = None

        if category_counts:

            dominant_category = max(
                category_counts,
                key=category_counts.get
            )

        dominant_category_lower = (
            str(
                dominant_category or ""
            ).strip().lower()
        )

        # --------------------------------------------------------
        # 1. VERY HIGH REVIEW ACTIVITY
        # --------------------------------------------------------

        if (
            avg_review_count >= 100
            and avg_popularity >= 80
        ):
            return "Highly Reviewed Destinations"

        # --------------------------------------------------------
        # 2. BEACH CLUSTER
        # --------------------------------------------------------

        if (
            dominant_category_lower
            == "beach"
        ):
            return "Beach Destinations"

        # --------------------------------------------------------
        # 3. EMERGING / LOW ACTIVITY
        # --------------------------------------------------------

        if (
            avg_rating < 1
            and avg_popularity < 10
            and avg_review_count < 1
        ):
            return "Emerging Destinations"

        # --------------------------------------------------------
        # 4. HIGH-RATED AND POPULAR
        # --------------------------------------------------------

        if (
            avg_rating >= 4
            and avg_popularity >= 50
        ):
            return "Popular Destinations"

        # --------------------------------------------------------
        # 5. HIGH-RATED
        # --------------------------------------------------------

        if avg_rating >= 4:
            return "Highly Rated Destinations"

        # --------------------------------------------------------
        # 6. OTHER CATEGORY
        # --------------------------------------------------------

        category_names = {
            "nature": "Nature Destinations",
            "adventure": "Adventure Destinations",
            "cultural": (
                "Cultural & Historical Destinations"
            ),
        }

        if dominant_category_lower in category_names:

            return category_names[
                dominant_category_lower
            ]

        # --------------------------------------------------------
        # 7. MODERATE POPULARITY
        # --------------------------------------------------------

        if avg_popularity >= 60:
            return "Popular Destinations"

        # --------------------------------------------------------
        # 8. FALLBACK
        # --------------------------------------------------------

        return "General Tourist Destinations"

    # ============================================================
    # GETTERS
    # ============================================================

    def get_cluster_id(
        self,
        destination_id: int
    ) -> Optional[int]:
        """Get cluster ID for a destination."""

        cluster = (
            self.db.query(Cluster)
            .filter(
                Cluster.destination_id
                == destination_id
            )
            .first()
        )

        return (
            int(cluster.cluster_id)
            if cluster
            else None
        )

    def get_cluster_label(
        self,
        destination_id: int
    ) -> Optional[str]:
        """Get cluster label for a destination."""

        cluster = (
            self.db.query(Cluster)
            .filter(
                Cluster.destination_id
                == destination_id
            )
            .first()
        )

        return (
            cluster.cluster_name
            if cluster
            else None
        )

    def get_cluster_stats(
        self
    ) -> Dict[str, Any]:
        """
        Get cluster statistics from database.

        Includes:
        - cluster ID
        - cluster name
        - number of destinations
        - destination list
        """

        clusters = (
            self.db.query(Cluster)
            .order_by(
                Cluster.cluster_id,
                Cluster.destination_id
            )
            .all()
        )

        if not clusters:
            return {}

        stats = {}

        for cluster in clusters:

            cluster_id = int(
                cluster.cluster_id
            )

            if cluster_id not in stats:

                stats[cluster_id] = {
                    "cluster_id": cluster_id,
                    "cluster_name": (
                        cluster.cluster_name
                    ),
                    "count": 0,
                    "destinations": [],
                    "silhouette_score": (
                        float(
                            cluster.cluster_score
                        )
                        if cluster.cluster_score
                        is not None
                        else None
                    ),
                }

            stats[cluster_id]["count"] += 1

            dest = (
                self.db.query(Destination)
                .filter(
                    Destination.id
                    == cluster.destination_id
                )
                .first()
            )

            if dest:

                stats[
                    cluster_id
                ]["destinations"].append({

                    "id": dest.id,

                    "name": dest.name,

                    "rating": self._safe_float(
                        dest.rating
                    ),

                    "popularity_score": (
                        self._safe_float(
                            dest.popularity_score
                        )
                    ),

                    "category": dest.category,

                    "municipality": (
                        dest.municipality
                    ),
                })

        return stats

    def get_evaluation_summary(
        self
    ) -> Dict[str, Any]:
        """
        Return current clustering evaluation summary.

        Useful for dashboard/API.
        """

        if not self.cluster_labels:

            return {
                "algorithm": "K-Means",
                "status": "not_run",
                "silhouette_score": None,
                "n_clusters": 0,
                "n_destinations": 0,
                "features": (
                    self.FEATURE_NAMES.copy()
                ),
            }

        return {
            "algorithm": "K-Means",
            "status": "completed",

            "silhouette_score": (
                round(
                    float(
                        self.silhouette_score
                    ),
                    4
                )
                if self.silhouette_score
                is not None
                else None
            ),

            "n_clusters": len(
                set(
                    self.cluster_labels.values()
                )
            ),

            "n_destinations": len(
                self.cluster_labels
            ),

            "features": (
                self.FEATURE_NAMES.copy()
            ),

            "cluster_quality": (
                self._get_quality_label(
                    self.silhouette_score
                )
            ),

            "cluster_sizes": {
                int(cluster_id): int(
                    list(
                        self.cluster_labels.values()
                    ).count(cluster_id)
                )
                for cluster_id in sorted(
                    set(
                        self.cluster_labels.values()
                    )
                )
            },

            "cluster_statistics": (
                self.cluster_statistics
            ),

            "evaluation_by_k": (
                self.evaluation_results.get(
                    "evaluation_by_k",
                    []
                )
            ),
        }

    @staticmethod
    def _get_quality_label(
        score: Optional[float]
    ) -> str:
        """Convert silhouette score to quality label."""

        if score is None:
            return "Not evaluated"

        if score >= 0.70:
            return "Excellent"

        if score >= 0.50:
            return "Good"

        if score >= 0.25:
            return "Fair"

        return "Weak"


# ================================================================
# HELPER FUNCTION
# ================================================================

def get_cluster_info_for_destination(
    destination_id: int,
    db: Session
) -> Optional[Dict[str, Any]]:
    """
    Get cluster information for a destination.
    """

    cluster = (
        db.query(Cluster)
        .filter(
            Cluster.destination_id
            == destination_id
        )
        .first()
    )

    if not cluster:
        return None

    return {
        "cluster_id": int(
            cluster.cluster_id
        ),

        "cluster_name": (
            cluster.cluster_name
        ),

        "cluster_score": (
            float(
                cluster.cluster_score
            )
            if cluster.cluster_score
            is not None
            else None
        ),
    }