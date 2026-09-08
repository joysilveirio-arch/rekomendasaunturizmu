"""
Configuration Management

Loads environment variables and provides application settings.
"""

import os
from pathlib import Path

from dotenv import load_dotenv


# ============================================================
# LOAD .ENV
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"

load_dotenv(dotenv_path=ENV_PATH)


class Settings:
    """Application settings."""

    # ========================================================
    # APPLICATION
    # ========================================================

    APP_NAME = os.getenv(
        "APP_NAME",
        "Timor-Leste Tourism Intelligence Platform"
    )

    APP_VERSION = os.getenv(
        "APP_VERSION",
        "1.0.0"
    )

    DEBUG = os.getenv(
        "DEBUG",
        "True"
    ).lower() == "true"

    HOST = os.getenv(
        "HOST",
        "0.0.0.0"
    )

    PORT = int(
        os.getenv(
            "PORT",
            "8000"
        )
    )

    # ========================================================
    # DATABASE
    # ========================================================

    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "sqlite:///./database/tourism.db"
    )

    # ========================================================
    # GENERIC API
    # ========================================================

    API_BASE_URL = os.getenv(
        "API_BASE_URL",
        ""
    )

    API_KEY = os.getenv(
        "API_KEY",
        ""
    )

    # ========================================================
    # APIFY
    # ========================================================

    APIFY_API_TOKEN = os.getenv(
        "APIFY_API_TOKEN",
        ""
    ).strip()

    # Apify Dataset ID
    APIFY_DATASET_ID = os.getenv(
        "APIFY_DATASET_ID",
        ""
    ).strip()

    # Google Maps scraper Actor ID
    APIFY_SCRAPER_ACTOR_ID = os.getenv(
        "APIFY_SCRAPER_ACTOR_ID",
        "gurify/google-maps-places-scraper"
    ).strip()

    APIFY_MAX_PLACES_PER_QUERY = int(
        os.getenv(
            "APIFY_MAX_PLACES_PER_QUERY",
            "20"
        )
    )

    APIFY_MAX_REVIEWS_PER_PLACE = int(
        os.getenv(
            "APIFY_MAX_REVIEWS_PER_PLACE",
            "10"
        )
    )

    APIFY_SCRAPER_LANGUAGE = os.getenv(
        "APIFY_SCRAPER_LANGUAGE",
        "en"
    ).strip()

    # Delay between Apify queries
    APIFY_QUERY_DELAY = float(
        os.getenv(
            "APIFY_QUERY_DELAY",
            "1"
        )
    )

    # ========================================================
    # APIFY FALLBACK
    # ========================================================

    APIFY_FALLBACK_ENABLED = os.getenv(
        "APIFY_FALLBACK_ENABLED",
        "true"
    ).lower() == "true"

    # ========================================================
    # DATA COLLECTION
    # ========================================================

    POLLING_INTERVAL = int(
        os.getenv(
            "POLLING_INTERVAL",
            "300"
        )
    )

    DATA_SOURCE = os.getenv(
        "DATA_SOURCE",
        "apify"
    ).strip().lower()

    MOCK_DATA_ENABLED = os.getenv(
        "MOCK_DATA_ENABLED",
        "False"
    ).lower() == "true"

    # ========================================================
    # CORS
    # ========================================================

    CORS_ORIGINS_RAW = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:8000,http://127.0.0.1:8000"
    )

    CORS_ORIGINS = [
        origin.strip()
        for origin in CORS_ORIGINS_RAW.split(",")
        if origin.strip()
    ]

    # Development convenience
    if "*" not in CORS_ORIGINS:
        CORS_ORIGINS.append("*")

    # ========================================================
    # LOGGING
    # ========================================================

    LOG_LEVEL = os.getenv(
        "LOG_LEVEL",
        "INFO"
    ).upper()

    # ========================================================
    # SENTIMENT ANALYSIS
    # ========================================================

    SENTIMENT_POSITIVE_THRESHOLD = float(
        os.getenv(
            "SENTIMENT_POSITIVE_THRESHOLD",
            "0.05"
        )
    )

    SENTIMENT_NEGATIVE_THRESHOLD = float(
        os.getenv(
            "SENTIMENT_NEGATIVE_THRESHOLD",
            "-0.05"
        )
    )

    # ========================================================
    # CLUSTERING
    # ========================================================

    DEFAULT_N_CLUSTERS = int(
        os.getenv(
            "DEFAULT_N_CLUSTERS",
            "4"
        )
    )

    CLUSTERING_RANDOM_STATE = int(
        os.getenv(
            "CLUSTERING_RANDOM_STATE",
            "42"
        )
    )

    # ========================================================
    # RECOMMENDATION
    # ========================================================

    DEFAULT_RECOMMENDATION_LIMIT = int(
        os.getenv(
            "DEFAULT_RECOMMENDATION_LIMIT",
            "10"
        )
    )

    # ========================================================
    # PATHS
    # ========================================================

    BASE_DIR = BASE_DIR

    DATA_DIR = BASE_DIR / "data"
    RAW_DATA_DIR = DATA_DIR / "raw"
    PROCESSED_DATA_DIR = DATA_DIR / "processed"

    DATABASE_DIR = BASE_DIR / "database"
    MODELS_DIR = BASE_DIR / "models"
    LOGS_DIR = BASE_DIR / "logs"

    # ========================================================
    # DATABASE URL HELPER
    # ========================================================

    @classmethod
    def get_database_url(cls):
        """
        Get database URL.

        Ensures SQLite database directory exists.
        """

        if "sqlite" in cls.DATABASE_URL:

            db_path_string = cls.DATABASE_URL.replace(
                "sqlite:///",
                ""
            )

            db_path = Path(db_path_string)

            # Handle relative SQLite paths
            if not db_path.is_absolute():
                db_path = cls.BASE_DIR / db_path

            db_path.parent.mkdir(
                parents=True,
                exist_ok=True
            )

        return cls.DATABASE_URL

    # ========================================================
    # VALIDATION
    # ========================================================

    @classmethod
    def validate(cls):
        """
        Validate important configuration.
        """

        errors = []

        valid_sources = {
            "apify",
            "api",
            "mock",
            "csv"
        }

        # ----------------------------------------------------
        # DATA SOURCE
        # ----------------------------------------------------

        if cls.DATA_SOURCE not in valid_sources:

            errors.append(
                f"Invalid DATA_SOURCE='{cls.DATA_SOURCE}'. "
                f"Allowed values: "
                f"{', '.join(sorted(valid_sources))}"
            )

        # ----------------------------------------------------
        # APIFY
        # ----------------------------------------------------

        if cls.DATA_SOURCE == "apify":

            if not cls.APIFY_API_TOKEN:

                errors.append(
                    "APIFY_API_TOKEN is not configured."
                )

            if not cls.APIFY_SCRAPER_ACTOR_ID:

                errors.append(
                    "APIFY_SCRAPER_ACTOR_ID is not configured."
                )

        # ----------------------------------------------------
        # POLLING
        # ----------------------------------------------------

        if cls.POLLING_INTERVAL <= 0:

            errors.append(
                "POLLING_INTERVAL must be greater than 0."
            )

        # ----------------------------------------------------
        # APIFY PLACES
        # ----------------------------------------------------

        if cls.APIFY_MAX_PLACES_PER_QUERY <= 0:

            errors.append(
                "APIFY_MAX_PLACES_PER_QUERY "
                "must be greater than 0."
            )

        # ----------------------------------------------------
        # APIFY REVIEWS
        # ----------------------------------------------------

        if cls.APIFY_MAX_REVIEWS_PER_PLACE < 0:

            errors.append(
                "APIFY_MAX_REVIEWS_PER_PLACE "
                "cannot be negative."
            )

        # ----------------------------------------------------
        # RESULT
        # ----------------------------------------------------

        if errors:

            return False, errors

        return True, []


# ============================================================
# GLOBAL SETTINGS INSTANCE
# ============================================================

settings = Settings()