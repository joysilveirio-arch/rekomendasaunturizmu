"""
Timor-Leste Tourism Intelligence Platform
Main FastAPI Application Entry Point
"""

from contextlib import asynccontextmanager
import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.config import settings
from backend.database import engine, Base

from backend.api import (
    destinations,
    reviews,
    analytics,
    recommendations,
    mining,
    realtime,
)

from backend.services.data_collector import (
    start_scheduler,
    stop_scheduler,
)


# ============================================================
# LOGGING CONFIGURATION
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

try:
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized successfully.")
except Exception as e:
    logger.exception("Failed to initialize database: %s", e)


# ============================================================
# FRONTEND PATH
# ============================================================

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

frontend_path = os.path.join(
    PROJECT_ROOT,
    "frontend"
)


# ============================================================
# APPLICATION LIFESPAN
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup and shutdown lifecycle.
    """

    # --------------------------------------------------------
    # STARTUP
    # --------------------------------------------------------

    logger.info(
        "Starting Timor-Leste Tourism Intelligence Platform..."
    )

    try:
        # IMPORTANT:
        # start_scheduler() is a normal synchronous function.
        # Therefore DO NOT use await here.
        start_scheduler()

        logger.info("Scheduler started successfully.")

    except Exception as e:
        logger.exception(
            "Failed to start scheduler: %s",
            e
        )

    # Application is running
    yield

    # --------------------------------------------------------
    # SHUTDOWN
    # --------------------------------------------------------

    logger.info("Shutting down application...")

    try:
        # stop_scheduler() is async
        await stop_scheduler()

        logger.info("Scheduler stopped successfully.")

    except Exception as e:
        logger.exception(
            "Failed to stop scheduler: %s",
            e
        )

    logger.info(
        "Timor-Leste Tourism Intelligence Platform stopped."
    )


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="Timor-Leste Tourism Intelligence API",
    description=(
        "Data Mining and Recommendation System "
        "for Timor-Leste Tourism"
    ),
    version="1.0.0",
    lifespan=lifespan,
)


# ============================================================
# CORS CONFIGURATION
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# API ROUTERS
# ============================================================

app.include_router(
    destinations.router,
    prefix="/api/destinations",
    tags=["Destinations"],
)

app.include_router(
    reviews.router,
    prefix="/api/reviews",
    tags=["Reviews"],
)

app.include_router(
    analytics.router,
    prefix="/api/analytics",
    tags=["Analytics"],
)

app.include_router(
    recommendations.router,
    prefix="/api/recommendations",
    tags=["Recommendations"],
)

app.include_router(
    mining.router,
    prefix="/api/mining",
    tags=["Data Mining"],
)

app.include_router(
    realtime.router,
    prefix="/api/realtime",
    tags=["Real-Time"],
)


# ============================================================
# STATIC FRONTEND
# ============================================================

if os.path.exists(frontend_path):

    app.mount(
        "/static",
        StaticFiles(
            directory=frontend_path,
            html=True,
        ),
        name="static",
    )

    logger.info(
        "Frontend directory mounted: %s",
        frontend_path,
    )

else:

    logger.warning(
        "Frontend directory not found: %s",
        frontend_path,
    )


# ============================================================
# ROOT ENDPOINT
# ============================================================

@app.get("/")
async def root():
    """
    Serve the main frontend page.
    """

    index_path = os.path.join(
        frontend_path,
        "index.html"
    )

    if os.path.exists(index_path):
        return FileResponse(index_path)

    return {
        "message": (
            "Timor-Leste Tourism Intelligence Platform"
        ),
        "status": "running",
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/api/health")
async def health_check():
    """
    Health check endpoint.
    """

    return {
        "status": "healthy",
        "version": "1.0.0",
        "service": "Timor-Leste Tourism Intelligence API",
    }


# ============================================================
# APPLICATION ENTRY POINT
# ============================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "backend.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )