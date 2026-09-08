"""
Apify Google Maps Places Scraper Data Source

Retrieves tourism destinations and reviews from
Apify Google Maps Places Scraper.
"""

import time
import datetime
import logging
import re
from typing import Dict, Any, List

from apify_client import ApifyClient

from backend.data_sources.base import BaseDataSource
from backend.config import settings
from backend.utils.logger import get_logger


logger = get_logger(__name__)


class ApifyQuotaExceededError(RuntimeError):
    """
    Raised when Apify monthly usage hard limit is exceeded.
    """
    pass


class ApifyDataSource(BaseDataSource):
    """
    Apify Google Maps Places Scraper data source.
    """

    def __init__(self):
        """Initialize Apify data source."""

        self.api_token = getattr(
            settings,
            "APIFY_API_TOKEN",
            None
        )

        self.actor_id = getattr(
            settings,
            "APIFY_SCRAPER_ACTOR_ID",
            "gurify/google-maps-places-scraper"
        )

        self.max_places = int(
            getattr(
                settings,
                "APIFY_MAX_PLACES_PER_QUERY",
                20
            )
        )

        self.max_reviews = int(
            getattr(
                settings,
                "APIFY_MAX_REVIEWS_PER_PLACE",
                10
            )
        )

        self.max_search_queries = int(
            getattr(
                settings,
                "APIFY_MAX_SEARCH_QUERIES",
                20
            )
        )

        self.language = getattr(
            settings,
            "APIFY_SCRAPER_LANGUAGE",
            "en"
        )

        self.query_delay = float(
            getattr(
                settings,
                "APIFY_QUERY_DELAY",
                1
            )
        )

        self.client = None

        self.quota_exceeded = False
        self.last_error = None

        # Cache hasil terakhir
        self._last_destinations: List[
            Dict[str, Any]
        ] = []

        # ====================================================
        # INITIALIZE APIFY CLIENT
        # ====================================================

        if self.api_token:
            try:
                self.client = ApifyClient(
                    self.api_token
                )

                logger.info(
                    "Apify client initialized successfully"
                )

                logger.info(
                    "Apify Actor: %s",
                    self.actor_id
                )

                logger.info(
                    "Max places/query: %s",
                    self.max_places
                )

                logger.info(
                    "Max reviews/place: %s",
                    self.max_reviews
                )

                logger.info(
                    "Max search queries: %s",
                    self.max_search_queries
                )

            except Exception as exc:
                logger.error(
                    "Failed to initialize Apify client: %s",
                    exc
                )

                self.client = None
                self.last_error = str(exc)

        else:
            logger.error(
                "APIFY_API_TOKEN is not configured."
            )

            self.last_error = (
                "APIFY_API_TOKEN is not configured."
            )

        # ====================================================
        # SEARCH QUERIES
        # ====================================================

        self.search_queries = [
            "tourist attractions in Dili Timor-Leste",
            "beaches in Timor-Leste",
            "historical sites in Timor-Leste",
            "nature parks in Timor-Leste",
            "cultural sites in Timor-Leste",
            "adventure tourism Timor-Leste",
            "scenic views Timor-Leste",
            "traditional villages Timor-Leste",
            "diving spots Timor-Leste",
            "tourist destinations Timor-Leste",
        ]

        # ====================================================
        # SPECIFIC LOCATIONS
        # ====================================================

        self.location_queries = [
            "Atauro Island Timor-Leste",
            "Jaco Island Timor-Leste",
            "Cristo Rei Dili",
            "Mount Ramelau Timor-Leste",
            "Tasitolu Dili",
            "Com Beach Lautem",
            "Baucau Timor-Leste",
            "Dare Dili",
            "Maubisse Ainaro",
            "Liquica Timor-Leste",
        ]

        self.all_queries = (
            self.search_queries
            + self.location_queries
        )

    # ========================================================
    # APIFY QUOTA DETECTION
    # ========================================================

    @staticmethod
    def _is_quota_exceeded_error(
        exc: Exception
    ) -> bool:
        """
        Detect Apify monthly usage hard-limit errors.
        """

        error_text = str(exc).lower()

        quota_keywords = [
            "monthly usage hard limit exceeded",
            "usage hard limit exceeded",
            "monthly usage limit exceeded",
            "hard limit exceeded",
            "usage limit exceeded",
        ]

        if any(
            keyword in error_text
            for keyword in quota_keywords
        ):
            return True

        # Apify may return ForbiddenError
        class_name = (
            exc.__class__.__name__.lower()
        )

        if "forbidden" in class_name:
            if (
                "limit" in error_text
                or "usage" in error_text
                or "quota" in error_text
            ):
                return True

        return False

    # ========================================================
    # RUN APIFY SCRAPER
    # ========================================================

    def _run_scraper(
        self,
        queries: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Run Apify Google Maps Places Scraper.

        Important:
        If Apify monthly hard limit is exceeded,
        stop immediately and raise ApifyQuotaExceededError.
        """

        if not self.client:
            logger.error(
                "Apify client is not initialized."
            )
            return []

        all_results: List[
            Dict[str, Any]
        ] = []

        # Limit number of queries
        queries_to_run = queries[
            :self.max_search_queries
        ]

        logger.info(
            "Running %s Apify search queries.",
            len(queries_to_run)
        )

        # ====================================================
        # PROCESS EACH QUERY
        # ====================================================

        for index, query in enumerate(
            queries_to_run,
            start=1
        ):
            logger.info(
                "[%s/%s] Searching Apify: %s",
                index,
                len(queries_to_run),
                query
            )

            try:
                run_input = {
                    "searchQueries": [
                        query
                    ],
                    "maxPlacesPerQuery": (
                        self.max_places
                    ),
                    "maxReviewsPerPlace": (
                        self.max_reviews
                    ),
                    "language": self.language,
                    "proxyConfiguration": {
                        "useApifyProxy": True
                    }
                }

                # =================================================
                # RUN ACTOR
                # =================================================

                run = (
                    self.client
                    .actor(self.actor_id)
                    .call(
                        run_input=run_input
                    )
                )

                if not run:
                    logger.error(
                        "Empty Actor response for: %s",
                        query
                    )
                    continue

                run_status = run.get(
                    "status"
                )

                logger.info(
                    "Apify Actor status for '%s': %s",
                    query,
                    run_status
                )

                if run_status != "SUCCEEDED":
                    logger.error(
                        "Apify Actor failed for '%s'.",
                        query
                    )

                    logger.error(
                        "Run information: %s",
                        run
                    )

                    continue

                # =================================================
                # GET DATASET
                # =================================================

                dataset_id = run.get(
                    "defaultDatasetId"
                )

                if not dataset_id:
                    logger.warning(
                        "No dataset ID returned for query: %s",
                        query
                    )
                    continue

                dataset_client = (
                    self.client.dataset(
                        dataset_id
                    )
                )

                items = (
                    dataset_client
                    .list_items()
                    .items
                )

                logger.info(
                    "Found %s places for '%s'",
                    len(items),
                    query
                )

                # Add source information
                for item in items:
                    item["_source_query"] = query
                    item["_source"] = (
                        "apify_google_maps"
                    )

                all_results.extend(items)

            except Exception as exc:

                # =================================================
                # APIFY MONTHLY QUOTA EXCEEDED
                # =================================================

                if self._is_quota_exceeded_error(
                    exc
                ):
                    self.quota_exceeded = True
                    self.last_error = str(exc)

                    logger.error(
                        "================================================"
                    )

                    logger.error(
                        "APIFY MONTHLY USAGE HARD LIMIT EXCEEDED."
                    )

                    logger.error(
                        "Stopping Apify collection immediately."
                    )

                    logger.error(
                        "The system should use fallback data."
                    )

                    logger.error(
                        "================================================"
                    )

                    raise ApifyQuotaExceededError(
                        "Apify monthly usage hard limit exceeded."
                    ) from exc

                # =================================================
                # OTHER APIFY ERROR
                # =================================================

                self.last_error = str(exc)

                logger.error(
                    "Error running Apify scraper for '%s': %s",
                    query,
                    exc,
                    exc_info=True
                )

            # =================================================
            # DELAY
            # =================================================

            if (
                index < len(queries_to_run)
                and not self.quota_exceeded
            ):
                time.sleep(
                    self.query_delay
                )

        # ====================================================
        # REMOVE DUPLICATES
        # ====================================================

        seen_ids = set()

        unique_results = []

        for item in all_results:

            place_id = (
                item.get("placeId")
                or item.get("place_id")
                or item.get("googlePlaceId")
            )

            if place_id:
                unique_key = str(
                    place_id
                )
            else:
                name = str(
                    item.get("name", "")
                ).strip().lower()

                address = str(
                    item.get("address", "")
                ).strip().lower()

                unique_key = (
                    f"{name}|{address}"
                )

            if unique_key in seen_ids:
                continue

            seen_ids.add(
                unique_key
            )

            unique_results.append(
                item
            )

        logger.info(
            "Total raw places: %s",
            len(all_results)
        )

        logger.info(
            "Total unique places: %s",
            len(unique_results)
        )

        return unique_results

    # ========================================================
    # PARSE PLACE
    # ========================================================

    def _parse_place_to_destination(
        self,
        place: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Convert raw Apify place data into
        application destination format.
        """

        # ====================================================
        # BASIC INFORMATION
        # ====================================================

        name = (
            place.get("name")
            or place.get("title")
            or "Unknown"
        )

        address = (
            place.get("address")
            or place.get("formattedAddress")
            or place.get("location")
            or ""
        )

        # ====================================================
        # COORDINATES
        # ====================================================

        lat = (
            place.get("lat")
            or place.get("latitude")
            or 0
        )

        lng = (
            place.get("lng")
            or place.get("longitude")
            or 0
        )

        try:
            lat = float(lat)
        except (
            TypeError,
            ValueError
        ):
            lat = 0.0

        try:
            lng = float(lng)
        except (
            TypeError,
            ValueError
        ):
            lng = 0.0

        # ====================================================
        # RATING
        # ====================================================

        rating = (
            place.get("rating")
            or 0
        )

        try:
            rating = float(rating)
        except (
            TypeError,
            ValueError
        ):
            rating = 0.0

        rating = max(
            0.0,
            min(5.0, rating)
        )

        # ====================================================
        # REVIEW COUNT
        # ====================================================

        total_ratings = (
            place.get("totalRatings")
            or place.get("reviewCount")
            or place.get("reviewsCount")
            or place.get("userRatingsTotal")
            or 0
        )

        try:
            total_ratings = int(
                total_ratings
            )
        except (
            TypeError,
            ValueError
        ):
            total_ratings = 0

        # ====================================================
        # CATEGORY
        # ====================================================

        raw_category = (
            place.get("category")
            or place.get("type")
            or ""
        )

        category = self._map_category(
            raw_category
        )

        # ====================================================
        # PRICE LEVEL
        # ====================================================

        price_level = (
            place.get("priceLevel")
            or place.get("price_level")
            or 2
        )

        price_map = {
            0: "Low",
            1: "Low",
            2: "Medium",
            3: "High",
            4: "High",
        }

        if isinstance(
            price_level,
            str
        ):
            price_level_lower = (
                price_level.lower()
            )

            if "low" in price_level_lower:
                price_level_text = "Low"
            elif "high" in price_level_lower:
                price_level_text = "High"
            else:
                price_level_text = "Medium"
        else:
            price_level_text = (
                price_map.get(
                    price_level,
                    "Medium"
                )
            )

        # ====================================================
        # POPULARITY SCORE
        # ====================================================

        if (
            rating > 0
            and total_ratings > 0
        ):
            popularity = min(
                100,
                (
                    (rating / 5) * 70
                )
                + min(
                    total_ratings / 50,
                    30
                )
            )
        else:
            popularity = 50

        # ====================================================
        # MUNICIPALITY
        # ====================================================

        municipality = (
            self._extract_municipality(
                address
            )
        )

        # ====================================================
        # PHONE
        # ====================================================

        phone = (
            place.get("phone")
            or place.get("phoneNumber")
            or ""
        )

        # ====================================================
        # WEBSITE
        # ====================================================

        website = (
            place.get("website")
            or place.get("url")
            or ""
        )

        # ====================================================
        # IMAGE
        # ====================================================

        image_url = (
            place.get("imageUrl")
            or place.get("image_url")
            or place.get("thumbnailUrl")
            or ""
        )

        # ====================================================
        # REVIEWS
        # ====================================================

        reviews_data = (
            place.get("reviews")
            or []
        )

        reviews = []

        if isinstance(
            reviews_data,
            list
        ):
            for review in reviews_data:

                if not isinstance(
                    review,
                    dict
                ):
                    continue

                author_name = (
                    review.get("author")
                    or review.get("authorName")
                    or review.get("name")
                    or ""
                )

                review_rating = (
                    review.get("stars")
                    or review.get("rating")
                    or 3
                )

                review_text = (
                    review.get("text")
                    or review.get("reviewText")
                    or ""
                )

                review_time = (
                    review.get("date")
                    or review.get("publishedAtDate")
                    or review.get("time")
                    or ""
                )

                reviews.append({
                    "author_name": author_name,
                    "rating": review_rating,
                    "text": review_text,
                    "time": review_time,
                })

        # ====================================================
        # PLACE ID
        # ====================================================

        place_id = (
            place.get("placeId")
            or place.get("place_id")
            or place.get("googlePlaceId")
        )

        # ====================================================
        # DESCRIPTION
        # ====================================================

        description = (
            self._generate_description(
                place
            )
        )

        # ====================================================
        # RETURN
        # ====================================================

        return {
            "name": name,
            "description": description,
            "municipality": municipality,
            "location": address,
            "address": address,
            "latitude": lat,
            "longitude": lng,
            "category": category,
            "rating": rating,
            "review_count": total_ratings,
            "price_level": price_level_text,
            "popularity_score": round(
                float(popularity),
                1
            ),
            "external_id": (
                str(place_id)
                if place_id
                else None
            ),
            "place_id": place_id,
            "phone": phone,
            "website": website,
            "image_url": image_url,
            "source_data": place,
            "reviews_data": reviews,
        }

    # ========================================================
    # CATEGORY MAPPING
    # ========================================================

    def _map_category(
        self,
        category_str: Any
    ) -> str:
        """
        Map Google Maps categories
        to system tourism categories.
        """

        if isinstance(
            category_str,
            list
        ):
            category_str = " ".join(
                str(x)
                for x in category_str
            )

        category_str = str(
            category_str or ""
        )

        category_lower = (
            category_str.lower()
        )

        category_map = {
            "beach": "Beach",
            "island": "Beach",
            "diving": "Adventure",
            "dive": "Adventure",
            "park": "Nature",
            "nature": "Nature",
            "natural": "Nature",
            "waterfall": "Nature",
            "mountain": "Nature",
            "viewpoint": "Nature",
            "scenic": "Nature",
            "tourist": "Cultural",
            "museum": "Cultural",
            "historical": "Cultural",
            "history": "Cultural",
            "church": "Cultural",
            "temple": "Cultural",
            "mosque": "Cultural",
            "cultural": "Cultural",
            "village": "Cultural",
            "hotel": "Accommodation",
            "resort": "Accommodation",
            "guest house": "Accommodation",
            "guesthouse": "Accommodation",
            "hostel": "Accommodation",
            "restaurant": "Culinary",
            "cafe": "Culinary",
            "coffee": "Culinary",
            "food": "Culinary",
            "adventure": "Adventure",
            "hiking": "Adventure",
            "camping": "Adventure",
            "trekking": "Adventure",
            "outdoor": "Adventure",
        }

        for key, value in category_map.items():

            if key in category_lower:
                return value

        return "Cultural"

    # ========================================================
    # MUNICIPALITY
    # ========================================================

    def _extract_municipality(
        self,
        address: str
    ) -> str:
        """
        Extract Timor-Leste municipality
        from address text.
        """

        municipalities = {
            "dili": "Dili",
            "atauro": "Atauro",
            "lautem": "Lautem",
            "baucau": "Baucau",
            "ainaro": "Ainaro",
            "liquica": "Liquica",
            "manatuto": "Manatuto",
            "viqueque": "Viqueque",
            "aileu": "Aileu",
            "bobonaro": "Bobonaro",
            "covalima": "Covalima",
            "ermera": "Ermera",
            "manufahi": "Manufahi",
            "oecusse": "Oecusse",
            "com beach": "Lautem",
            "tutuala": "Lautem",
            "lospalos": "Lautem",
            "maubisse": "Ainaro",
            "dare": "Dili",
            "ramelau": "Ainaro",
            "tasitolu": "Dili",
        }

        if not address:
            return "Dili"

        address_lower = str(
            address
        ).lower()

        for key, value in municipalities.items():

            if key in address_lower:
                return value

        return "Dili"

    # ========================================================
    # DESCRIPTION
    # ========================================================

    def _generate_description(
        self,
        place: Dict[str, Any]
    ) -> str:
        """
        Generate destination description.
        """

        parts = []

        name = (
            place.get("name")
            or place.get("title")
            or ""
        )

        category = (
            place.get("category")
            or place.get("type")
            or ""
        )

        address = (
            place.get("address")
            or place.get("formattedAddress")
            or ""
        )

        phone = (
            place.get("phone")
            or place.get("phoneNumber")
            or ""
        )

        website = (
            place.get("website")
            or place.get("url")
            or ""
        )

        if name:
            parts.append(
                f"{name} is a notable place "
                f"in Timor-Leste."
            )

        if category:
            parts.append(
                f"Category: {category}."
            )

        if address:
            parts.append(
                f"Located at {address}."
            )

        if phone:
            parts.append(
                f"Contact: {phone}."
            )

        if website:
            parts.append(
                f"Website: {website}."
            )

        if parts:
            return " ".join(parts)

        return (
            f"{name} in Timor-Leste."
        )

    # ========================================================
    # GET DESTINATIONS
    # ========================================================

    def get_destinations(
        self
    ) -> List[Dict[str, Any]]:
        """
        Get tourism destinations from Apify.
        """

        if not self.client:
            logger.error(
                "Apify client unavailable. "
                "Check APIFY_API_TOKEN."
            )
            return []

        try:
            logger.info(
                "Starting Apify Google Maps "
                "destination collection..."
            )

            places = self._run_scraper(
                self.all_queries
            )

            if not places:
                logger.warning(
                    "Apify returned no places."
                )

                self._last_destinations = []

                return []

            destinations = []

            for place in places:

                try:
                    destination = (
                        self._parse_place_to_destination(
                            place
                        )
                    )

                    latitude = destination.get(
                        "latitude",
                        0
                    )

                    longitude = destination.get(
                        "longitude",
                        0
                    )

                    if (
                        latitude != 0
                        and longitude != 0
                    ):
                        destinations.append(
                            destination
                        )
                    else:
                        logger.warning(
                            "Skipping destination "
                            "without coordinates: %s",
                            destination.get(
                                "name"
                            )
                        )

                except Exception as exc:
                    logger.error(
                        "Error parsing place: %s",
                        exc
                    )

            self._last_destinations = (
                destinations
            )

            logger.info(
                "Successfully parsed %s destinations.",
                len(destinations)
            )

            return destinations

        except ApifyQuotaExceededError:
            self.quota_exceeded = True
            self._last_destinations = []

            # IMPORTANT:
            # Do not swallow this exception.
            # data_collector.py will use MockDataSource.
            raise

        except Exception as exc:

            self.last_error = str(exc)

            logger.error(
                "Error getting destinations "
                "from Apify: %s",
                exc,
                exc_info=True
            )

            self._last_destinations = []

            return []

    # ========================================================
    # GET REVIEWS
    # ========================================================

    def get_reviews(
        self
    ) -> List[Dict[str, Any]]:
        """
        Get reviews from destinations collected
        during the latest get_destinations() call.

        IMPORTANT:
        This does NOT run Apify again.
        """

        reviews_list = []

        destinations = (
            self._last_destinations
        )

        if not destinations:
            logger.warning(
                "No cached destinations available "
                "for review extraction."
            )

            return []

        try:

            for destination in destinations:

                destination_name = (
                    destination.get(
                        "name"
                    )
                )

                destination_id = (
                    destination.get(
                        "external_id"
                    )
                    or destination.get(
                        "place_id"
                    )
                )

                reviews_data = (
                    destination.get(
                        "reviews_data",
                        []
                    )
                )

                if not isinstance(
                    reviews_data,
                    list
                ):
                    continue

                for review in reviews_data:

                    if not isinstance(
                        review,
                        dict
                    ):
                        continue

                    review_text = (
                        review.get(
                            "text",
                            ""
                        )
                    )

                    if not review_text:
                        continue

                    rating = (
                        review.get(
                            "rating",
                            3
                        )
                    )

                    try:
                        rating = float(
                            rating
                        )
                    except (
                        TypeError,
                        ValueError
                    ):
                        rating = 3.0

                    rating = max(
                        0.0,
                        min(5.0, rating)
                    )

                    review_date = (
                        self._parse_review_date(
                            review.get(
                                "time",
                                ""
                            )
                        )
                    )

                    reviews_list.append({
                        "destination_id": (
                            destination_id
                        ),
                        "destination_name": (
                            destination_name
                        ),
                        "review_text": (
                            review_text
                        ),
                        "rating": rating,
                        "source": (
                            "apify_google_maps"
                        ),
                        "review_date": (
                            review_date
                        ),
                    })

            logger.info(
                "Total reviews collected "
                "from Apify cache: %s",
                len(reviews_list)
            )

            return reviews_list

        except Exception as exc:

            logger.error(
                "Error extracting reviews: %s",
                exc,
                exc_info=True
            )

            return []

    # ========================================================
    # PARSE REVIEW DATE
    # ========================================================

    def _parse_review_date(
        self,
        date_value: Any
    ) -> datetime.datetime:
        """
        Convert Apify review date into datetime.
        """

        if isinstance(
            date_value,
            datetime.datetime
        ):
            return date_value

        if isinstance(
            date_value,
            datetime.date
        ):
            return datetime.datetime.combine(
                date_value,
                datetime.time.min
            )

        if not date_value:
            return datetime.datetime.now()

        date_str = str(
            date_value
        ).strip()

        # ====================================================
        # ISO FORMAT
        # ====================================================

        try:
            normalized = (
                date_str.replace(
                    "Z",
                    "+00:00"
                )
            )

            parsed = (
                datetime.datetime.fromisoformat(
                    normalized
                )
            )

            if parsed.tzinfo:
                parsed = parsed.replace(
                    tzinfo=None
                )

            return parsed

        except Exception:
            pass

        # ====================================================
        # RELATIVE DATE
        # ====================================================

        lower = date_str.lower()

        try:

            if "day" in lower:
                number = (
                    self._extract_number(
                        lower
                    )
                )

                return (
                    datetime.datetime.now()
                    - datetime.timedelta(
                        days=number
                    )
                )

            if "week" in lower:
                number = (
                    self._extract_number(
                        lower
                    )
                )

                return (
                    datetime.datetime.now()
                    - datetime.timedelta(
                        weeks=number
                    )
                )

            if "month" in lower:
                number = (
                    self._extract_number(
                        lower
                    )
                )

                return (
                    datetime.datetime.now()
                    - datetime.timedelta(
                        days=30 * number
                    )
                )

            if "year" in lower:
                number = (
                    self._extract_number(
                        lower
                    )
                )

                return (
                    datetime.datetime.now()
                    - datetime.timedelta(
                        days=365 * number
                    )
                )

        except Exception:
            pass

        return (
            datetime.datetime.now()
            - datetime.timedelta(
                days=30
            )
        )

    # ========================================================
    # EXTRACT NUMBER
    # ========================================================

    def _extract_number(
        self,
        text: str
    ) -> int:
        """
        Extract first integer from text.
        """

        match = re.search(
            r"\d+",
            text
        )

        if match:
            return int(
                match.group()
            )

        return 1

    # ========================================================
    # GET TOURISM DATA
    # ========================================================

    def get_tourism_data(
        self
    ) -> List[Dict[str, Any]]:
        """
        Get complete tourism destination data.
        """

        return self.get_destinations()


__all__ = [
    "ApifyDataSource",
    "ApifyQuotaExceededError",
]