"""
Data Collection Service

Timor-Leste Tourism Intelligence Platform

Responsible for:
- Collecting tourism data from Apify
- Saving destinations and reviews to database
- Sentiment analysis
- Running clustering
- Tracking collection status
- Automatic scheduled collection
- Apify quota fallback to MockDataSource
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from backend.config import settings
from backend.database import SessionLocal

from backend.models.destination import Destination
from backend.models.review import Review
from backend.models.collection_log import DataCollectionLog

from backend.services.preprocessing import PreprocessingService
from backend.services.sentiment import SentimentAnalyzer
from backend.services.clustering import ClusteringService

from backend.data_sources.api_source import (
    ApifyDataSource,
    ApifyQuotaExceededError,
)

from backend.data_sources.mock_source import (
    MockDataSource,
)


# ============================================================
# LOGGER
# ============================================================

logger = logging.getLogger(__name__)


# ============================================================
# GLOBAL COLLECTION STATUS
# ============================================================

_collection_status: Dict[str, Any] = {
    "api_online": False,
    "database_online": False,
    "pipeline_status": "idle",

    "last_update": None,
    "next_update": None,

    "records_collected": 0,
    "destinations_collected": 0,
    "reviews_collected": 0,

    "is_running": False,

    "last_error": None,
    "api_error": None,

    "source": None,
    "fallback_used": False,

    "polling_interval": 300,
}


# ============================================================
# SCHEDULER VARIABLES
# ============================================================

_scheduler_task: Optional[
    asyncio.Task
] = None

_polling_interval: int = 300


# ============================================================
# DATA COLLECTOR SERVICE
# ============================================================

class DataCollectorService:
    """
    Main service responsible for collecting
    and processing tourism data.
    """

    def __init__(self):

        self.preprocessing = (
            PreprocessingService()
        )

        self.sentiment = (
            SentimentAnalyzer()
        )

        self.apify_source = (
            ApifyDataSource()
        )

        self.mock_source = (
            MockDataSource()
        )

        logger.info(
            "DataCollectorService initialized."
        )

    # ========================================================
    # CHECK FALLBACK SETTING
    # ========================================================

    def fallback_enabled(self) -> bool:
        """
        Check whether Apify -> Mock fallback is enabled.
        """

        value = getattr(
            settings,
            "APIFY_FALLBACK_ENABLED",
            True
        )

        if isinstance(
            value,
            str
        ):
            return (
                value.lower().strip()
                in (
                    "true",
                    "1",
                    "yes",
                    "on"
                )
            )

        return bool(value)

    # ========================================================
    # DATA SOURCE
    # ========================================================

    def get_data_source(
        self
    ):
        """
        Return configured data source.
        """

        source_name = getattr(
            settings,
            "DATA_SOURCE",
            "apify"
        )

        source_name = (
            str(source_name)
            .lower()
            .strip()
        )

        logger.info(
            "Configured data source: %s",
            source_name
        )

        if source_name == "mock":

            if not getattr(
                settings,
                "MOCK_DATA_ENABLED",
                True
            ):
                raise RuntimeError(
                    "Mock data source is disabled."
                )

            return self.mock_source

        if source_name == "apify":
            return self.apify_source

        raise ValueError(
            f"Unsupported DATA_SOURCE: "
            f"{source_name}"
        )

    # ========================================================
    # MODEL COLUMN HELPER
    # ========================================================

    @staticmethod
    def _model_columns(
        model
    ) -> set:
        """
        Get SQLAlchemy model column names.
        """

        try:
            return {
                column.name
                for column in model.__table__.columns
            }
        except Exception:
            return set()

    # ========================================================
    # SAVE DESTINATIONS
    # ========================================================

    def _save_destinations(
        self,
        db: Session,
        destinations: list
    ) -> int:
        """
        Save or update destinations.
        """

        saved_count = 0

        model_columns = (
            self._model_columns(
                Destination
            )
        )

        for data in destinations:

            try:

                if not data:
                    continue

                external_id = (
                    data.get(
                        "external_id"
                    )
                    or data.get(
                        "place_id"
                    )
                )

                name = data.get(
                    "name"
                )

                if not name:
                    continue

                destination = None

                # =================================================
                # FIND BY EXTERNAL ID
                # =================================================

                if (
                    external_id
                    and "external_id"
                    in model_columns
                ):

                    destination = (
                        db.query(
                            Destination
                        )
                        .filter(
                            Destination.external_id
                            == str(
                                external_id
                            )
                        )
                        .first()
                    )

                # =================================================
                # FIND BY NAME
                # =================================================

                if not destination:

                    destination = (
                        db.query(
                            Destination
                        )
                        .filter(
                            Destination.name
                            == str(name)
                        )
                        .first()
                    )

                # =================================================
                # PREPARE DATA
                # =================================================

                destination_data = {}

                fields = [
                    "name",
                    "description",
                    "category",
                    "municipality",
                    "latitude",
                    "longitude",
                    "rating",
                    "review_count",
                    "address",
                    "location",
                    "phone",
                    "website",
                    "image_url",
                    "external_id",
                    "price_level",
                    "popularity_score",
                ]

                for field in fields:

                    if (
                        field in data
                        and field in model_columns
                    ):

                        value = data.get(
                            field
                        )

                        if value is not None:
                            destination_data[
                                field
                            ] = value

                # =================================================
                # CREATE
                # =================================================

                if not destination:

                    if "name" not in destination_data:
                        destination_data[
                            "name"
                        ] = str(name)

                    destination = Destination(
                        **destination_data
                    )

                    db.add(
                        destination
                    )

                # =================================================
                # UPDATE
                # =================================================

                else:

                    for field, value in (
                        destination_data.items()
                    ):

                        if (
                            field == "name"
                            and not value
                        ):
                            continue

                        try:
                            setattr(
                                destination,
                                field,
                                value
                            )
                        except Exception:
                            pass

                saved_count += 1

            except Exception as exc:

                logger.exception(
                    "Error saving destination: %s",
                    exc
                )

        try:
            db.commit()

        except Exception as exc:

            db.rollback()

            logger.exception(
                "Destination commit failed: %s",
                exc
            )

        logger.info(
            "Saved/updated destinations: %s",
            saved_count
        )

        return saved_count

    # ========================================================
    # SAVE REVIEWS
    # ========================================================

    def _save_reviews(
        self,
        db: Session,
        reviews: list
    ) -> int:
        """
        Save tourism reviews and calculate sentiment.
        """

        saved_count = 0

        model_columns = (
            self._model_columns(
                Review
            )
        )

        destination_columns = (
            self._model_columns(
                Destination
            )
        )

        for data in reviews:

            try:

                if not data:
                    continue

                destination_id = data.get(
                    "destination_id"
                )

                destination_name = data.get(
                    "destination_name"
                )

                destination = None

                # =================================================
                # FIND DESTINATION BY DATABASE ID
                # =================================================

                if destination_id:

                    try:

                        if (
                            "id"
                            in destination_columns
                        ):
                            destination = (
                                db.query(
                                    Destination
                                )
                                .filter(
                                    Destination.id
                                    == int(
                                        destination_id
                                    )
                                )
                                .first()
                            )

                    except Exception:
                        destination = None

                # =================================================
                # FIND BY EXTERNAL ID
                # =================================================

                if (
                    not destination
                    and destination_id
                    and "external_id"
                    in destination_columns
                ):

                    try:

                        destination = (
                            db.query(
                                Destination
                            )
                            .filter(
                                Destination.external_id
                                == str(
                                    destination_id
                                )
                            )
                            .first()
                        )

                    except Exception:
                        destination = None

                # =================================================
                # FIND BY NAME
                # =================================================

                if (
                    not destination
                    and destination_name
                ):

                    destination = (
                        db.query(
                            Destination
                        )
                        .filter(
                            Destination.name
                            == str(
                                destination_name
                            )
                        )
                        .first()
                    )

                if not destination:

                    logger.warning(
                        "Destination not found for review: %s",
                        destination_name
                    )

                    continue

                # =================================================
                # REVIEW TEXT
                # =================================================

                review_text = (
                    data.get("text")
                    or data.get("review_text")
                    or data.get("comment")
                    or ""
                )

                if not review_text:
                    continue

                # =================================================
                # SENTIMENT ANALYSIS
                # =================================================

                sentiment_result = None

                try:

                    sentiment_result = (
                        self.sentiment.analyze(
                            review_text
                        )
                    )

                except Exception as exc:

                    logger.warning(
                        "Sentiment analysis failed: %s",
                        exc
                    )

                sentiment_label = None
                sentiment_score = None

                if isinstance(
                    sentiment_result,
                    dict
                ):

                    sentiment_label = (
                        sentiment_result.get(
                            "label"
                        )
                        or sentiment_result.get(
                            "sentiment"
                        )
                    )

                    sentiment_score = (
                        sentiment_result.get(
                            "score"
                        )
                        or sentiment_result.get(
                            "confidence"
                        )
                    )

                elif isinstance(
                    sentiment_result,
                    str
                ):

                    sentiment_label = (
                        sentiment_result
                    )

                # =================================================
                # RATING
                # =================================================

                rating = data.get(
                    "rating"
                )

                try:

                    if rating is not None:

                        rating = float(
                            rating
                        )

                        rating = max(
                            0.0,
                            min(
                                5.0,
                                rating
                            )
                        )

                except Exception:

                    rating = None

                # =================================================
                # REVIEW DATE
                # =================================================

                review_date = (
                    data.get("date")
                    or data.get("review_date")
                )

                if isinstance(
                    review_date,
                    str
                ):

                    try:

                        review_date = (
                            datetime.fromisoformat(
                                review_date.replace(
                                    "Z",
                                    "+00:00"
                                )
                            )
                        )

                        if review_date.tzinfo:
                            review_date = (
                                review_date.replace(
                                    tzinfo=None
                                )
                            )

                    except Exception:

                        review_date = None

                # =================================================
                # REVIEW DATA
                # =================================================

                review_kwargs = {}

                if "destination_id" in model_columns:
                    review_kwargs[
                        "destination_id"
                    ] = destination.id

                if "text" in model_columns:
                    review_kwargs[
                        "text"
                    ] = review_text

                if "rating" in model_columns:
                    review_kwargs[
                        "rating"
                    ] = rating

                if "sentiment" in model_columns:
                    review_kwargs[
                        "sentiment"
                    ] = sentiment_label

                if (
                    "sentiment_score"
                    in model_columns
                ):
                    review_kwargs[
                        "sentiment_score"
                    ] = sentiment_score

                if "date" in model_columns:
                    review_kwargs[
                        "date"
                    ] = review_date

                if "source" in model_columns:
                    review_kwargs[
                        "source"
                    ] = data.get(
                        "source",
                        "apify"
                    )

                # Optional author fields
                author_name = data.get(
                    "author_name"
                )

                if (
                    author_name
                    and "author_name"
                    in model_columns
                ):
                    review_kwargs[
                        "author_name"
                    ] = author_name

                if (
                    author_name
                    and "author"
                    in model_columns
                ):
                    review_kwargs[
                        "author"
                    ] = author_name

                # =================================================
                # CREATE REVIEW
                # =================================================

                review = Review(
                    **review_kwargs
                )

                db.add(
                    review
                )

                saved_count += 1

            except Exception as exc:

                logger.exception(
                    "Error saving review: %s",
                    exc
                )

        try:

            db.commit()

        except Exception as exc:

            db.rollback()

            logger.exception(
                "Review commit failed: %s",
                exc
            )

        logger.info(
            "Saved reviews: %s",
            saved_count
        )

        return saved_count

    # ========================================================
    # GET REVIEWS
    # ========================================================

    async def _collect_reviews(
        self,
        source,
        destinations
    ):

        try:

            return await asyncio.to_thread(
                source.get_reviews
            )

        except TypeError:

            return await asyncio.to_thread(
                source.get_reviews,
                destinations
            )

    # ========================================================
    # COLLECT TOURISM DATA
    # ========================================================

    async def collect_data(
        self,
        source_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Collect destinations and reviews.

        Apify quota exceeded:
            Apify -> MockDataSource fallback.
        """

        global _collection_status

        # ====================================================
        # PREVENT DUPLICATE COLLECTION
        # ====================================================

        if _collection_status[
            "is_running"
        ]:

            logger.warning(
                "Collection is already running."
            )

            return {
                "success": False,
                "message": (
                    "Collection is already running."
                ),
                "destinations": 0,
                "reviews": 0,
            }

        # ====================================================
        # INITIAL STATUS
        # ====================================================

        _collection_status[
            "is_running"
        ] = True

        _collection_status[
            "pipeline_status"
        ] = "collecting"

        _collection_status[
            "last_error"
        ] = None

        _collection_status[
            "api_error"
        ] = None

        _collection_status[
            "fallback_used"
        ] = False

        db = None
        collection_log = None

        start_time = datetime.utcnow()

        source = None
        requested_source = (
            source_name
        )

        fallback_used = False
        api_error = None

        try:

            # =================================================
            # DATABASE
            # =================================================

            db = SessionLocal()

            _collection_status[
                "database_online"
            ] = True

            # =================================================
            # SELECT SOURCE
            # =================================================

            if source_name:

                source_name = (
                    source_name
                    .lower()
                    .strip()
                )

                if source_name == "apify":
                    source = (
                        self.apify_source
                    )

                elif source_name == "mock":
                    source = (
                        self.mock_source
                    )

                else:

                    raise ValueError(
                        f"Unknown source: "
                        f"{source_name}"
                    )

            else:

                source = (
                    self.get_data_source()
                )

                source_name = (
                    getattr(
                        settings,
                        "DATA_SOURCE",
                        "apify"
                    )
                )

                source_name = (
                    str(source_name)
                    .lower()
                    .strip()
                )

            logger.info(
                "Starting tourism data collection..."
            )

            logger.info(
                "Requested source: %s",
                source_name
            )

            logger.info(
                "Using source: %s",
                source.__class__.__name__
            )

            # =================================================
            # COLLECTION LOG
            # =================================================

            try:

                collection_log = (
                    DataCollectionLog()
                )

                log_columns = (
                    self._model_columns(
                        DataCollectionLog
                    )
                )

                if "source" in log_columns:

                    collection_log.source = (
                        source.__class__.__name__
                    )

                if "status" in log_columns:

                    collection_log.status = (
                        "running"
                    )

                if "started_at" in log_columns:

                    collection_log.started_at = (
                        start_time
                    )

                db.add(
                    collection_log
                )

                db.commit()

            except Exception as exc:

                logger.warning(
                    "Could not create collection log: %s",
                    exc
                )

                collection_log = None

            # =================================================
            # COLLECT DESTINATIONS
            # =================================================

            logger.info(
                "Collecting destinations..."
            )

            _collection_status[
                "pipeline_status"
            ] = "collecting_destinations"

            # =================================================
            # APIFY COLLECTION
            # =================================================

            try:

                destinations = (
                    await asyncio.to_thread(
                        source.get_destinations
                    )
                )

            # =================================================
            # APIFY QUOTA EXCEEDED
            # =================================================

            except ApifyQuotaExceededError as exc:

                api_error = str(exc)

                logger.warning(
                    "Apify quota exceeded."
                )

                _collection_status[
                    "api_online"
                ] = False

                _collection_status[
                    "api_error"
                ] = api_error

                # =================================================
                # CHECK FALLBACK
                # =================================================

                if (
                    source_name == "apify"
                    and self.fallback_enabled()
                ):

                    logger.warning(
                        "================================================"
                    )

                    logger.warning(
                        "APIFY QUOTA EXCEEDED."
                    )

                    logger.warning(
                        "Switching to MockDataSource."
                    )

                    logger.warning(
                        "================================================"
                    )

                    fallback_used = True

                    source = (
                        self.mock_source
                    )

                    source_name = (
                        "mock_fallback"
                    )

                    _collection_status[
                        "fallback_used"
                    ] = True

                    _collection_status[
                        "pipeline_status"
                    ] = "fallback_mock"

                    destinations = (
                        await asyncio.to_thread(
                            source.get_destinations
                        )
                    )

                else:

                    raise RuntimeError(
                        "Apify monthly usage "
                        "hard limit exceeded "
                        "and fallback is disabled."
                    ) from exc

            # =================================================
            # APIFY RETURNED EMPTY
            # =================================================

            if (
                not destinations
                and source_name == "apify"
                and self.fallback_enabled()
            ):

                logger.warning(
                    "Apify returned no destinations."
                )

                logger.warning(
                    "Trying MockDataSource fallback..."
                )

                api_error = (
                    "Apify returned no destinations."
                )

                _collection_status[
                    "api_online"
                ] = False

                _collection_status[
                    "api_error"
                ] = api_error

                fallback_used = True

                source = (
                    self.mock_source
                )

                source_name = (
                    "mock_fallback"
                )

                _collection_status[
                    "fallback_used"
                ] = True

                _collection_status[
                    "pipeline_status"
                ] = "fallback_mock"

                destinations = (
                    await asyncio.to_thread(
                        source.get_destinations
                    )
                )

            if destinations is None:
                destinations = []

            logger.info(
                "Collected %s destinations.",
                len(destinations)
            )

            # =================================================
            # NO DESTINATIONS AFTER FALLBACK
            # =================================================

            if not destinations:

                raise RuntimeError(
                    "No destinations were returned "
                    "from the configured data source "
                    "or fallback source."
                )

            # =================================================
            # SAVE DESTINATIONS
            # =================================================

            saved_destinations = (
                self._save_destinations(
                    db,
                    destinations
                )
            )

            # =================================================
            # COLLECT REVIEWS
            # =================================================

            logger.info(
                "Collecting reviews..."
            )

            _collection_status[
                "pipeline_status"
            ] = "collecting_reviews"

            reviews = (
                await self._collect_reviews(
                    source,
                    destinations
                )
            )

            if reviews is None:
                reviews = []

            logger.info(
                "Collected %s reviews.",
                len(reviews)
            )

            # =================================================
            # SAVE REVIEWS
            # =================================================

            saved_reviews = (
                self._save_reviews(
                    db,
                    reviews
                )
            )

            # =================================================
            # CLUSTERING
            # =================================================

            _collection_status[
                "pipeline_status"
            ] = "clustering"

            try:

                clustering_service = (
                    ClusteringService()
                )

                result = (
                    clustering_service
                    .perform_clustering()
                )

                logger.info(
                    "Clustering completed: %s",
                    result
                )

            except Exception as exc:

                logger.warning(
                    "Clustering failed: %s",
                    exc
                )

            # =================================================
            # END TIME
            # =================================================

            end_time = datetime.utcnow()

            total_records = (
                saved_destinations
                + saved_reviews
            )

            # =================================================
            # UPDATE COLLECTION LOG
            # =================================================

            if collection_log:

                try:

                    log_columns = (
                        self._model_columns(
                            DataCollectionLog
                        )
                    )

                    if "status" in log_columns:

                        collection_log.status = (
                            "completed"
                        )

                    if "completed_at" in log_columns:

                        collection_log.completed_at = (
                            end_time
                        )

                    if (
                        "destinations_count"
                        in log_columns
                    ):

                        collection_log.destinations_count = (
                            saved_destinations
                        )

                    if (
                        "reviews_count"
                        in log_columns
                    ):

                        collection_log.reviews_count = (
                            saved_reviews
                        )

                    if (
                        "records_count"
                        in log_columns
                    ):

                        collection_log.records_count = (
                            total_records
                        )

                    if (
                        "error_message"
                        in log_columns
                    ):

                        collection_log.error_message = (
                            api_error
                            if fallback_used
                            else None
                        )

                    db.commit()

                except Exception as exc:

                    logger.warning(
                        "Could not update collection log: %s",
                        exc
                    )

            # =================================================
            # UPDATE GLOBAL STATUS
            # =================================================

            _collection_status[
                "api_online"
            ] = (
                source_name == "apify"
            )

            _collection_status[
                "database_online"
            ] = True

            if fallback_used:

                _collection_status[
                    "pipeline_status"
                ] = "completed_with_fallback"

            else:

                _collection_status[
                    "pipeline_status"
                ] = "completed"

            _collection_status[
                "last_update"
            ] = end_time

            _collection_status[
                "records_collected"
            ] = total_records

            _collection_status[
                "destinations_collected"
            ] = saved_destinations

            _collection_status[
                "reviews_collected"
            ] = saved_reviews

            _collection_status[
                "source"
            ] = source_name

            _collection_status[
                "next_update"
            ] = (
                end_time
                + timedelta(
                    seconds=_polling_interval
                )
            )

            _collection_status[
                "polling_interval"
            ] = _polling_interval

            # =================================================
            # SUCCESS MESSAGE
            # =================================================

            if fallback_used:

                message = (
                    "Tourism data collection "
                    "completed using MockDataSource "
                    "fallback because Apify monthly "
                    "usage limit was exceeded."
                )

            else:

                message = (
                    "Tourism data collection "
                    "completed successfully."
                )

            logger.info(
                message
            )

            return {
                "success": True,
                "message": message,

                "destinations": (
                    saved_destinations
                ),

                "reviews": (
                    saved_reviews
                ),

                "total_records": (
                    total_records
                ),

                "source": source_name,

                "requested_source": (
                    requested_source
                    or source_name
                ),

                "fallback_used": (
                    fallback_used
                ),

                "api_error": (
                    api_error
                ),

                "started_at": (
                    start_time.isoformat()
                ),

                "completed_at": (
                    end_time.isoformat()
                ),
            }

        # =====================================================
        # GENERAL ERROR
        # =====================================================

        except Exception as exc:

            logger.exception(
                "Tourism data collection failed."
            )

            _collection_status[
                "pipeline_status"
            ] = "error"

            _collection_status[
                "last_error"
            ] = str(exc)

            if source_name == "apify":
                _collection_status[
                    "api_online"
                ] = False

            if collection_log:

                try:

                    log_columns = (
                        self._model_columns(
                            DataCollectionLog
                        )
                    )

                    if "status" in log_columns:

                        collection_log.status = (
                            "failed"
                        )

                    if (
                        "error_message"
                        in log_columns
                    ):

                        collection_log.error_message = (
                            str(exc)
                        )

                    db.commit()

                except Exception:
                    pass

            return {
                "success": False,

                "message": (
                    "Tourism data collection failed."
                ),

                "error": str(exc),

                "destinations": 0,

                "reviews": 0,

                "fallback_used": (
                    fallback_used
                ),

                "source": (
                    source_name
                ),
            }

        finally:

            if db:

                try:
                    db.close()

                except Exception:
                    pass

            _collection_status[
                "is_running"
            ] = False

    # ========================================================
    # STATUS
    # ========================================================

    def get_status(
        self
    ) -> Dict[str, Any]:

        status = dict(
            _collection_status
        )

        status[
            "polling_interval"
        ] = _polling_interval

        return status


# ============================================================
# GLOBAL SERVICE INSTANCE
# ============================================================

data_collector_service = (
    DataCollectorService()
)


# ============================================================
# COMPATIBILITY FUNCTIONS
# ============================================================

def collection_status() -> Dict[str, Any]:
    """
    Compatibility wrapper used by realtime.py.
    """

    return (
        data_collector_service
        .get_status()
    )


async def trigger_collection(
    source_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Trigger collection manually.
    """

    return await (
        data_collector_service
        .collect_data(
            source_name=source_name
        )
    )


async def collect_tourism_data(
    source_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Backward-compatible collection function.
    """

    return await trigger_collection(
        source_name=source_name
    )


# ============================================================
# UPDATE INTERVAL
# ============================================================

def update_interval(
    interval_seconds: int
) -> Dict[str, Any]:

    global _polling_interval

    interval_seconds = int(
        interval_seconds
    )

    if interval_seconds < 60:

        raise ValueError(
            "Interval cannot be less than 60 seconds."
        )

    if interval_seconds > 3600:

        raise ValueError(
            "Interval cannot exceed 3600 seconds."
        )

    _polling_interval = (
        interval_seconds
    )

    _collection_status[
        "polling_interval"
    ] = _polling_interval

    _collection_status[
        "next_update"
    ] = (
        datetime.utcnow()
        + timedelta(
            seconds=_polling_interval
        )
    )

    logger.info(
        "Polling interval updated to %s seconds.",
        _polling_interval
    )

    return {
        "success": True,

        "interval_seconds": (
            _polling_interval
        ),

        "next_update": (
            _collection_status[
                "next_update"
            ].isoformat()
        ),
    }


# ============================================================
# AUTOMATIC SCHEDULER
# ============================================================

async def _collection_scheduler_loop():

    logger.info(
        "Automatic collection scheduler started."
    )

    while True:

        try:

            await asyncio.sleep(
                _polling_interval
            )

            if not _collection_status[
                "is_running"
            ]:

                logger.info(
                    "Automatic collection started."
                )

                await trigger_collection()

            else:

                logger.info(
                    "Skipping scheduled collection "
                    "because another collection is running."
                )

        except asyncio.CancelledError:

            logger.info(
                "Automatic collection scheduler stopped."
            )

            break

        except Exception as exc:

            logger.exception(
                "Scheduler error: %s",
                exc
            )


# ============================================================
# START SCHEDULER
# ============================================================

def start_scheduler():

    global _scheduler_task

    if (
        _scheduler_task
        and not _scheduler_task.done()
    ):

        logger.info(
            "Collection scheduler is already running."
        )

        return

    try:

        loop = asyncio.get_running_loop()

        _scheduler_task = (
            loop.create_task(
                _collection_scheduler_loop()
            )
        )

        logger.info(
            "Collection scheduler started."
        )

    except RuntimeError:

        logger.warning(
            "No running event loop. "
            "Scheduler was not started."
        )


# ============================================================
# STOP SCHEDULER
# ============================================================

async def stop_scheduler():

    global _scheduler_task

    if _scheduler_task:

        _scheduler_task.cancel()

        try:

            await _scheduler_task

        except asyncio.CancelledError:
            pass

        _scheduler_task = None

        logger.info(
            "Collection scheduler stopped."
        )


# ============================================================
# EXPORTS
# ============================================================

__all__ = [
    "DataCollectorService",
    "data_collector_service",
    "collection_status",
    "trigger_collection",
    "collect_tourism_data",
    "update_interval",
    "start_scheduler",
    "stop_scheduler",
]