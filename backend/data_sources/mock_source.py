"""
Mock Data Source
Reads real Google Places crawler data from backend/data/dataset.json
for local testing before switching to Apify.
"""

import json
from pathlib import Path
from typing import Dict, Any, List

from backend.data_sources.base import BaseDataSource
from backend.utils.logger import get_logger


logger = get_logger(__name__)


class MockDataSource(BaseDataSource):
    """
    Data source for testing using the locally stored Google Places dataset.

    The dataset is loaded from:
        backend/data/dataset.json
    """

    def __init__(self):
        self.data_file = (
            Path(__file__).resolve().parent.parent
            / "data"
            / "dataset.json"
        )

        self.raw_data = self._load_data()
        self.destinations = self._normalize_destinations()
        self.reviews = self._normalize_reviews()

        logger.info(
            f"Dataset loaded successfully: "
            f"{len(self.raw_data)} places, "
            f"{len(self.destinations)} destinations, "
            f"{len(self.reviews)} reviews"
        )

    # ------------------------------------------------------------------
    # LOAD DATASET
    # ------------------------------------------------------------------

    def _load_data(self) -> List[Dict[str, Any]]:
        """Load the JSON dataset from backend/data/dataset.json."""

        if not self.data_file.exists():
            raise FileNotFoundError(
                f"Dataset not found: {self.data_file}"
            )

        try:
            with open(self.data_file, "r", encoding="utf-8") as file:
                data = json.load(file)

        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Invalid JSON dataset: {self.data_file}"
            ) from exc

        # Most crawler exports are a list of places.
        if isinstance(data, list):
            return data

        # Some exports may wrap the list inside a dictionary.
        if isinstance(data, dict):
            for key in ("places", "results", "data", "items"):
                if isinstance(data.get(key), list):
                    return data[key]

        raise ValueError(
            "Unsupported dataset structure. "
            "Expected a list of places or a dictionary "
            "containing places/results/data/items."
        )

    # ------------------------------------------------------------------
    # HELPERS
    # ------------------------------------------------------------------

    @staticmethod
    def _safe_float(value: Any, default: float = 0.0) -> float:
        """Safely convert a value to float."""

        try:
            if value is None or value == "":
                return default

            return float(value)

        except (TypeError, ValueError):
            return default

    @staticmethod
    def _safe_int(value: Any, default: int = 0) -> int:
        """Safely convert a value to integer."""

        try:
            if value is None or value == "":
                return default

            return int(value)

        except (TypeError, ValueError):
            return default

    @staticmethod
    def _get_location(place: Dict[str, Any]) -> Dict[str, Any]:
        """Extract latitude and longitude from the crawler location object."""

        location = place.get("location") or {}

        if not isinstance(location, dict):
            return {}

        return location

    @staticmethod
    def _get_category(place: Dict[str, Any]) -> str:
        """Extract the main category."""

        category = place.get("categoryName")

        if category:
            return str(category)

        categories = place.get("categories")

        if isinstance(categories, list) and categories:
            return str(categories[0])

        return "Tourism"

    @staticmethod
    def _calculate_popularity(
        rating: float,
        review_count: int
    ) -> float:
        """
        Calculate a simple popularity score from rating and review count.

        The score is normalized to approximately 0-100.
        """

        rating_score = (rating / 5.0) * 70

        # Logarithmic review score prevents places with huge review
        # counts from completely dominating the result.
        if review_count > 0:
            import math

            review_score = min(
                30,
                math.log10(review_count + 1) * 10
            )
        else:
            review_score = 0

        return round(
            min(100, rating_score + review_score),
            2
        )

    @staticmethod
    def _price_level(price: Any) -> str:
        """Convert Google Places price information to a simple price level."""

        if price is None or price == "":
            return "Unknown"

        price_text = str(price).strip()

        if price_text in ("$", "1"):
            return "Low"

        if price_text in ("$$", "2"):
            return "Medium"

        if price_text in ("$$$", "3"):
            return "High"

        if price_text in ("$$$$", "4"):
            return "Very High"

        return price_text

    # ------------------------------------------------------------------
    # DESTINATIONS
    # ------------------------------------------------------------------

    def _normalize_destinations(self) -> List[Dict[str, Any]]:
        """Convert Google Places records into the application's destination format."""

        destinations = []

        for place in self.raw_data:
            if not isinstance(place, dict):
                continue

            location = self._get_location(place)

            latitude = self._safe_float(
                location.get("lat"),
                0.0
            )

            longitude = self._safe_float(
                location.get("lng"),
                0.0
            )

            rating = self._safe_float(
                place.get("totalScore"),
                0.0
            )

            review_count = self._safe_int(
                place.get("reviewsCount"),
                0
            )

            name = (
                place.get("title")
                or place.get("name")
                or "Unknown Destination"
            )

            description = (
                place.get("description")
                or place.get("ownerDescription")
                or ""
            )

            municipality = (
                place.get("city")
                or place.get("municipality")
                or place.get("state")
                or ""
            )

            category = self._get_category(place)

            destination = {
                # Existing application fields
                "name": name,
                "description": description,
                "municipality": municipality,
                "latitude": latitude,
                "longitude": longitude,
                "category": category,
                "rating": rating,
                "review_count": review_count,
                "price_level": self._price_level(
                    place.get("price")
                ),
                "popularity_score": self._calculate_popularity(
                    rating,
                    review_count
                ),

                # Additional real Google Places information
                "place_id": place.get("placeId"),
                "address": place.get("address"),
                "neighborhood": place.get("neighborhood"),
                "street": place.get("street"),
                "city": place.get("city"),
                "postal_code": place.get("postalCode"),
                "state": place.get("state"),
                "country_code": place.get("countryCode"),
                "website": place.get("website"),
                "phone": place.get("phone"),
                "phone_unformatted": place.get(
                    "phoneUnformatted"
                ),
                "categories": place.get("categories", []),
                "opening_hours": place.get(
                    "openingHours"
                ),
                "images_count": self._safe_int(
                    place.get("imagesCount"),
                    0
                ),
                "permanently_closed": bool(
                    place.get("permanentlyClosed", False)
                ),
                "temporarily_closed": bool(
                    place.get("temporarilyClosed", False)
                ),
                "reviews_distribution": place.get(
                    "reviewsDistribution"
                ),

                # Keep original crawler record available
                # for future analytics/debugging.
                "raw_data": place,
            }

            destinations.append(destination)

        return destinations

    # ------------------------------------------------------------------
    # REVIEWS
    # ------------------------------------------------------------------

    def _normalize_reviews(self) -> List[Dict[str, Any]]:
        """Extract and normalize real reviews from each place."""

        reviews = []

        for place in self.raw_data:
            if not isinstance(place, dict):
                continue

            destination_name = (
                place.get("title")
                or place.get("name")
                or "Unknown Destination"
            )

            place_reviews = place.get("reviews", [])

            if not isinstance(place_reviews, list):
                continue

            for review in place_reviews:
                if not isinstance(review, dict):
                    continue

                review_text = (
                    review.get("text")
                    or review.get("textTranslated")
                    or ""
                )

                rating = self._safe_float(
                    review.get("stars"),
                    0.0
                )

                reviewer = review.get("name")

                if not reviewer:
                    reviewer_info = review.get("reviewer")

                    if isinstance(reviewer_info, dict):
                        reviewer = (
                            reviewer_info.get("name")
                            or reviewer_info.get("displayName")
                        )

                normalized_review = {
                    "destination_name": destination_name,

                    "place_id": place.get("placeId"),

                    "review_text": review_text,

                    "rating": rating,

                    "source": "google_places_dataset",

                    "review_date": (
                        review.get("publishedAtDate")
                        or review.get("publishedAt")
                    ),

                    "reviewer_name": reviewer,

                    "text_original": review.get("text"),

                    "text_translated": review.get(
                        "textTranslated"
                    ),

                    "reviewer_photo": review.get(
                        "reviewerPhotoUrl"
                    ),

                    "raw_data": review,
                }

                reviews.append(normalized_review)

        return reviews

    # ------------------------------------------------------------------
    # PUBLIC INTERFACE
    # ------------------------------------------------------------------

    def get_destinations(self) -> List[Dict[str, Any]]:
        """Get normalized destination data."""

        logger.info(
            f"Mock data source: returning "
            f"{len(self.destinations)} destinations"
        )

        return self.destinations

    def get_reviews(self) -> List[Dict[str, Any]]:
        """Get normalized review data."""

        logger.info(
            f"Mock data source: returning "
            f"{len(self.reviews)} reviews"
        )

        return self.reviews

    def get_tourism_data(self) -> List[Dict[str, Any]]:
        """Get tourism data."""

        return self.destinations