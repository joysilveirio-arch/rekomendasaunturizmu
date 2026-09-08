from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from backend.models.destination import Destination
from backend.models.review import Review
from backend.models.cluster import Cluster
from backend.schemas.recommendation import RecommendationItem


class RecommendationService:
    """
    Service untuk menghasilkan rekomendasi destinasi wisata.

    Prinsip filtering:
    1. Gunakan category dan municipality jika tersedia.
    2. Gunakan minimum rating sebagai filter awal.
    3. Jika hasil kosong, lakukan fallback secara bertahap.
    4. Budget bukan filter wajib; budget digunakan untuk scoring.
    5. User type bukan filter database; user type digunakan untuk scoring.
    """

    def __init__(self, db: Session):
        self.db = db

        # Bobot kategori berdasarkan tipe wisatawan
        self.user_type_weights = {
            "Adventure": {
                "Adventure": 1.0,
                "Nature": 0.8,
                "Beach": 0.6,
                "Cultural": 0.3,
            },
            "Culture": {
                "Cultural": 1.0,
                "Adventure": 0.5,
                "Nature": 0.6,
                "Beach": 0.4,
            },
            "Relaxation": {
                "Beach": 1.0,
                "Nature": 0.8,
                "Cultural": 0.5,
                "Adventure": 0.2,
            },
            "Nature": {
                "Nature": 1.0,
                "Beach": 0.7,
                "Adventure": 0.8,
                "Cultural": 0.5,
            },
            "Beach": {
                "Beach": 1.0,
                "Nature": 0.7,
                "Adventure": 0.5,
                "Cultural": 0.3,
            },
            "Family": {
                "Beach": 0.9,
                "Nature": 0.8,
                "Cultural": 0.7,
                "Adventure": 0.3,
            },
            "Solo": {
                "Adventure": 0.9,
                "Nature": 0.8,
                "Cultural": 0.7,
                "Beach": 0.6,
            },
            "Group": {
                "Beach": 0.9,
                "Cultural": 0.8,
                "Adventure": 0.7,
                "Nature": 0.6,
            },
        }

        # Bobot budget untuk scoring.
        # Budget tidak digunakan sebagai hard filter.
        self.budget_multipliers = {
            "Low": {
                "Low": 1.0,
                "Medium": 0.7,
                "High": 0.4,
            },
            "Medium": {
                "Low": 0.8,
                "Medium": 1.0,
                "High": 0.7,
            },
            "High": {
                "Low": 0.5,
                "Medium": 0.8,
                "High": 1.0,
            },
        }

    def get_recommendations(
        self,
        user_type: str,
        category: Optional[str] = None,
        municipality: Optional[str] = None,
        min_rating: float = 3.0,
        budget: str = "Medium",
        limit: int = 10,
    ) -> List[RecommendationItem]:
        """
        Menghasilkan rekomendasi destinasi.

        Fallback strategy:

        Level 1
            category + municipality + minimum rating

        Level 2
            category + municipality + rating >= 3.0

        Level 3
            category + minimum rating
            municipality dilepas

        Level 4
            category saja

        Level 5
            seluruh destinasi

        Dengan strategi ini, kombinasi filter yang terlalu ketat
        tidak langsung menghasilkan rekomendasi kosong.
        """

        # Pastikan nilai aman
        user_type = user_type or "Solo"
        budget = budget or "Medium"

        try:
            min_rating = float(min_rating)
        except (TypeError, ValueError):
            min_rating = 3.0

        try:
            limit = int(limit)
        except (TypeError, ValueError):
            limit = 10

        limit = max(1, min(limit, 100))

        # Normalisasi rating minimum
        min_rating = max(0.0, min(5.0, min_rating))

        # ---------------------------------------------------------
        # LEVEL 1
        # Filter lengkap:
        # category + municipality + min_rating
        # ---------------------------------------------------------
        destinations = self._query_destinations(
            category=category,
            municipality=municipality,
            min_rating=min_rating,
        )

        fallback_level = 1

        # ---------------------------------------------------------
        # LEVEL 2
        # Jika kosong, turunkan rating ke 3.0 tetapi tetap
        # mempertahankan category + municipality.
        # ---------------------------------------------------------
        if not destinations and municipality and min_rating > 3.0:
            destinations = self._query_destinations(
                category=category,
                municipality=municipality,
                min_rating=3.0,
            )
            fallback_level = 2

        # ---------------------------------------------------------
        # LEVEL 3
        # Jika masih kosong, lepaskan municipality.
        # Category tetap dipertahankan.
        # ---------------------------------------------------------
        if not destinations and category:
            destinations = self._query_destinations(
                category=category,
                municipality=None,
                min_rating=min_rating,
            )
            fallback_level = 3

        # ---------------------------------------------------------
        # LEVEL 4
        # Jika masih kosong, gunakan category tanpa rating.
        # ---------------------------------------------------------
        if not destinations and category:
            destinations = self._query_destinations(
                category=category,
                municipality=None,
                min_rating=None,
            )
            fallback_level = 4

        # ---------------------------------------------------------
        # LEVEL 5
        # Jika benar-benar tidak ada, gunakan seluruh destinasi.
        # ---------------------------------------------------------
        if not destinations:
            destinations = self._query_destinations(
                category=None,
                municipality=None,
                min_rating=None,
            )
            fallback_level = 5

        # ---------------------------------------------------------
        # SCORING
        # ---------------------------------------------------------
        scored_destinations = []

        for destination in destinations:
            score = self._calculate_score(
                destination=destination,
                user_type=user_type,
                budget=budget,
                category=category,
                municipality=municipality,
            )

            scored_destinations.append(
                {
                    "destination": destination,
                    "score": score,
                    "match_details": self._get_match_details(
                        destination=destination,
                        user_type=user_type,
                        budget=budget,
                        requested_category=category,
                        requested_municipality=municipality,
                        fallback_level=fallback_level,
                    ),
                }
            )

        # Urutkan dari skor tertinggi
        scored_destinations.sort(
            key=lambda item: item["score"],
            reverse=True,
        )

        # Batasi hasil
        scored_destinations = scored_destinations[:limit]

        # ---------------------------------------------------------
        # CONVERT TO RecommendationItem
        # ---------------------------------------------------------
        items = []

        for item in scored_destinations:
            destination = item["destination"]

            items.append(
                RecommendationItem(
                    destination=destination,
                    score=item["score"],
                    match_details=item["match_details"],
                )
            )

        return items

    # =============================================================
    # DATABASE QUERY
    # =============================================================

    def _query_destinations(
        self,
        category: Optional[str] = None,
        municipality: Optional[str] = None,
        min_rating: Optional[float] = None,
    ) -> List[Destination]:
        """
        Mengambil destinasi berdasarkan filter.

        Rating NULL tidak lolos ketika minimum rating digunakan.
        """

        query = self.db.query(Destination)

        if category:
            query = query.filter(
                Destination.category == category
            )

        if municipality:
            query = query.filter(
                Destination.municipality == municipality
            )

        if min_rating is not None:
            query = query.filter(
                Destination.rating >= min_rating
            )

        return query.all()

    # =============================================================
    # SCORE CALCULATION
    # =============================================================

    def _calculate_score(
        self,
        destination: Destination,
        user_type: str,
        budget: str,
        category: Optional[str] = None,
        municipality: Optional[str] = None,
    ) -> float:
        """
        Menghitung skor rekomendasi 0.0 - 1.0.

        Komponen:
        - Rating       : 30%
        - Popularity   : 15%
        - Category     : 25%
        - Budget       : 10%
        - Sentiment    : 15%
        - Cluster      : 5%

        Bonus:
        - Category sesuai pilihan user
        - Municipality sesuai pilihan user
        """

        # ---------------------------------------------------------
        # RATING
        # ---------------------------------------------------------
        rating = self._safe_float(
            getattr(destination, "rating", None),
            default=0.0,
        )

        rating = max(0.0, min(5.0, rating))
        rating_score = rating / 5.0

        # ---------------------------------------------------------
        # POPULARITY
        # ---------------------------------------------------------
        popularity = self._safe_float(
            getattr(destination, "popularity_score", None),
            default=0.0,
        )

        popularity = max(0.0, min(100.0, popularity))
        popularity_score = popularity / 100.0

        # ---------------------------------------------------------
        # CATEGORY MATCH
        # ---------------------------------------------------------
        destination_category = getattr(
            destination,
            "category",
            None,
        )

        category_weights = self.user_type_weights.get(
            user_type,
            {},
        )

        category_match = category_weights.get(
            destination_category,
            0.5,
        )

        # ---------------------------------------------------------
        # BUDGET MATCH
        # ---------------------------------------------------------
        price_level = getattr(
            destination,
            "price_level",
            None,
        )

        budget_weights = self.budget_multipliers.get(
            budget,
            {},
        )

        budget_match = budget_weights.get(
            price_level,
            0.5,
        )

        # ---------------------------------------------------------
        # SENTIMENT
        # ---------------------------------------------------------
        sentiment_score = self._get_sentiment_score(
            destination.id
        )

        # ---------------------------------------------------------
        # CLUSTER
        # ---------------------------------------------------------
        cluster_score = self._get_cluster_score(
            destination.id
        )

        # ---------------------------------------------------------
        # BASE SCORE
        # ---------------------------------------------------------
        score = (
            rating_score * 0.30
            + popularity_score * 0.15
            + category_match * 0.25
            + budget_match * 0.10
            + sentiment_score * 0.15
            + cluster_score * 0.05
        )

        # ---------------------------------------------------------
        # CATEGORY BONUS
        # ---------------------------------------------------------
        if (
            category
            and destination_category
            and destination_category.lower()
            == category.lower()
        ):
            score += 0.10

        # ---------------------------------------------------------
        # MUNICIPALITY BONUS
        # ---------------------------------------------------------
        destination_municipality = getattr(
            destination,
            "municipality",
            None,
        )

        if (
            municipality
            and destination_municipality
            and destination_municipality.lower()
            == municipality.lower()
        ):
            # Municipality menjadi preference.
            # Jika fallback melepas municipality, destinasi
            # dari municipality pilihan tetap mendapat prioritas.
            score += 0.10

        return min(max(score, 0.0), 1.0)

    # =============================================================
    # SENTIMENT
    # =============================================================

    def _get_sentiment_score(
        self,
        destination_id: int,
    ) -> float:
        """
        Mengambil rata-rata sentiment review.

        Sentiment biasanya berada pada range -1 sampai +1,
        kemudian dikonversi menjadi 0 sampai 1.
        """

        reviews = (
            self.db.query(Review)
            .filter(
                Review.destination_id == destination_id
            )
            .all()
        )

        if not reviews:
            return 0.5

        sentiment_values = []

        for review in reviews:
            value = getattr(
                review,
                "sentiment_score",
                None,
            )

            if value is None:
                continue

            try:
                value = float(value)
            except (TypeError, ValueError):
                continue

            # Batasi agar tetap valid
            value = max(-1.0, min(1.0, value))

            sentiment_values.append(value)

        if not sentiment_values:
            return 0.5

        avg_score = sum(sentiment_values) / len(
            sentiment_values
        )

        # -1..1 menjadi 0..1
        normalized_score = (avg_score + 1.0) / 2.0

        return max(
            0.0,
            min(1.0, normalized_score),
        )

    # =============================================================
    # CLUSTER
    # =============================================================

    def _get_cluster_score(
        self,
        destination_id: int,
    ) -> float:
        """
        Mengambil cluster score destinasi.

        Jika cluster belum tersedia, gunakan nilai netral 0.5.
        """

        cluster = (
            self.db.query(Cluster)
            .filter(
                Cluster.destination_id == destination_id
            )
            .first()
        )

        if not cluster:
            return 0.5

        cluster_score = getattr(
            cluster,
            "cluster_score",
            None,
        )

        if cluster_score is None:
            return 0.5

        try:
            cluster_score = float(cluster_score)
        except (TypeError, ValueError):
            return 0.5

        return max(
            0.0,
            min(1.0, cluster_score),
        )

    # =============================================================
    # MATCH DETAILS
    # =============================================================

    def _get_match_details(
        self,
        destination: Destination,
        user_type: str,
        budget: str,
        requested_category: Optional[str] = None,
        requested_municipality: Optional[str] = None,
        fallback_level: int = 1,
    ) -> dict:
        """
        Detail alasan mengapa destinasi direkomendasikan.
        """

        destination_category = getattr(
            destination,
            "category",
            None,
        )

        destination_municipality = getattr(
            destination,
            "municipality",
            None,
        )

        rating = self._safe_float(
            getattr(destination, "rating", None),
            default=0.0,
        )

        popularity = self._safe_float(
            getattr(destination, "popularity_score", None),
            default=0.0,
        )

        category_weights = self.user_type_weights.get(
            user_type,
            {},
        )

        budget_weights = self.budget_multipliers.get(
            budget,
            {},
        )

        category_match = category_weights.get(
            destination_category,
            0.5,
        )

        price_level = getattr(
            destination,
            "price_level",
            None,
        )

        budget_match = budget_weights.get(
            price_level,
            0.5,
        )

        municipality_match = False

        if (
            requested_municipality
            and destination_municipality
        ):
            municipality_match = (
                destination_municipality.lower()
                == requested_municipality.lower()
            )

        category_match_requested = False

        if (
            requested_category
            and destination_category
        ):
            category_match_requested = (
                destination_category.lower()
                == requested_category.lower()
            )

        return {
            "rating_match": rating,
            "category_match": category_match,
            "budget_match": budget_match,
            "popularity": popularity,
            "municipality_match": municipality_match,
            "requested_category": requested_category,
            "requested_municipality": requested_municipality,
            "fallback_level": fallback_level,
        }

    # =============================================================
    # SAFE FLOAT
    # =============================================================

    @staticmethod
    def _safe_float(
        value,
        default: float = 0.0,
    ) -> float:
        """
        Mengubah value menjadi float dengan aman.
        """

        if value is None:
            return default

        try:
            return float(value)
        except (TypeError, ValueError):
            return default