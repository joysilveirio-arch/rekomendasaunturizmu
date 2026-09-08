"""
Destinations API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from backend.database import get_db
from backend.models.destination import Destination
from backend.schemas.destination import (
    DestinationCreate,
    DestinationUpdate,
    DestinationResponse,
    DestinationListResponse,
)
from backend.services.sentiment import (
    get_sentiment_summary_for_destination,
)
from backend.services.clustering import (
    get_cluster_info_for_destination,
)


router = APIRouter()


# ============================================================
# GET ALL CATEGORIES
# IMPORTANT: Keep this BEFORE /{destination_id}
# ============================================================

@router.get("/categories/all")
async def get_categories(
    db: Session = Depends(get_db),
):
    """Get all unique destination categories."""

    categories = (
        db.query(Destination.category)
        .filter(Destination.category.isnot(None))
        .distinct()
        .order_by(Destination.category)
        .all()
    )

    return {
        "categories": [category[0] for category in categories]
    }


# ============================================================
# GET ALL MUNICIPALITIES
# IMPORTANT: Keep this BEFORE /{destination_id}
# ============================================================

@router.get("/municipalities/all")
async def get_municipalities(
    db: Session = Depends(get_db),
):
    """Get all unique destination municipalities."""

    municipalities = (
        db.query(Destination.municipality)
        .filter(Destination.municipality.isnot(None))
        .distinct()
        .order_by(Destination.municipality)
        .all()
    )

    return {
        "municipalities": [
            municipality[0]
            for municipality in municipalities
        ]
    }


# ============================================================
# GET DESTINATIONS
# ============================================================

@router.get(
    "/",
    response_model=DestinationListResponse,
)
async def get_destinations(
    skip: int = Query(
        0,
        ge=0,
        description="Number of records to skip",
    ),

    limit: int = Query(
        20,
        ge=1,
        le=100,
        description="Maximum number of records",
    ),

    search: Optional[str] = Query(
        None,
        description="Search destination name, description or municipality",
    ),

    category: Optional[str] = Query(
        None,
        description="Filter by category",
    ),

    municipality: Optional[str] = Query(
        None,
        description="Filter by municipality",
    ),

    min_rating: Optional[float] = Query(
        None,
        ge=0,
        le=5,
        description="Minimum rating",
    ),

    sort_by: Optional[str] = Query(
        None,
        description=(
            "Sort field: rating, popularity, popularity_score, "
            "name, created_at"
        ),
    ),

    sort_order: str = Query(
        "desc",
        pattern="^(asc|desc)$",
        description="Sort direction",
    ),

    db: Session = Depends(get_db),
):
    """
    Get destinations with filtering, sorting and pagination.
    """

    query = db.query(Destination)

    # ========================================================
    # FILTER: SEARCH
    # ========================================================

    if search:
        search_term = f"%{search}%"

        query = query.filter(
            Destination.name.ilike(search_term)
            |
            Destination.description.ilike(search_term)
            |
            Destination.municipality.ilike(search_term)
        )

    # ========================================================
    # FILTER: CATEGORY
    # ========================================================

    if category:
        query = query.filter(
            Destination.category == category
        )

    # ========================================================
    # FILTER: MUNICIPALITY
    # ========================================================

    if municipality:
        query = query.filter(
            Destination.municipality == municipality
        )

    # ========================================================
    # FILTER: MINIMUM RATING
    # ========================================================

    if min_rating is not None:
        query = query.filter(
            Destination.rating >= min_rating
        )

    # ========================================================
    # SORTING
    # ========================================================

    allowed_sort_fields = {
        "rating": Destination.rating,
        "popularity": Destination.popularity_score,
        "popularity_score": Destination.popularity_score,
        "name": Destination.name,
        "created_at": Destination.created_at,
    }

    if sort_by and sort_by in allowed_sort_fields:

        sort_column = allowed_sort_fields[sort_by]

        if sort_order == "desc":
            query = query.order_by(
                sort_column.desc()
            )
        else:
            query = query.order_by(
                sort_column.asc()
            )

    else:
        # Default sorting
        query = query.order_by(
            Destination.popularity_score.desc()
        )

    # ========================================================
    # TOTAL COUNT
    # ========================================================

    total = query.count()

    # ========================================================
    # PAGINATION
    # ========================================================

    destinations = (
        query
        .offset(skip)
        .limit(limit)
        .all()
    )

    # ========================================================
    # RESPONSE
    # ========================================================

    return DestinationListResponse(
        total=total,
        items=destinations,
    )


# ============================================================
# GET SINGLE DESTINATION
# IMPORTANT: This route comes AFTER static routes
# ============================================================

@router.get(
    "/{destination_id}",
    response_model=DestinationResponse,
)
async def get_destination(
    destination_id: int,
    db: Session = Depends(get_db),
):
    """Get a specific destination by ID."""

    destination = (
        db.query(Destination)
        .filter(
            Destination.id == destination_id
        )
        .first()
    )

    if not destination:
        raise HTTPException(
            status_code=404,
            detail="Destination not found",
        )

    # ========================================================
    # SENTIMENT
    # ========================================================

    sentiment = get_sentiment_summary_for_destination(
        destination_id,
        db,
    )

    # ========================================================
    # CLUSTER
    # ========================================================

    cluster = get_cluster_info_for_destination(
        destination_id,
        db,
    )

    # ========================================================
    # RESPONSE DATA
    # ========================================================

    destination_dict = {
        column.name: getattr(destination, column.name)
        for column in Destination.__table__.columns
    }

    destination_dict["sentiment_summary"] = sentiment
    destination_dict["cluster_info"] = cluster

    return destination_dict


# ============================================================
# CREATE DESTINATION
# ============================================================

@router.post(
    "/",
    response_model=DestinationResponse,
)
async def create_destination(
    destination: DestinationCreate,
    db: Session = Depends(get_db),
):
    """Create a new destination."""

    destination_data = destination.model_dump()

    db_destination = Destination(
        **destination_data
    )

    db.add(db_destination)
    db.commit()
    db.refresh(db_destination)

    return db_destination


# ============================================================
# UPDATE DESTINATION
# ============================================================

@router.put(
    "/{destination_id}",
    response_model=DestinationResponse,
)
async def update_destination(
    destination_id: int,
    destination_update: DestinationUpdate,
    db: Session = Depends(get_db),
):
    """Update an existing destination."""

    db_destination = (
        db.query(Destination)
        .filter(
            Destination.id == destination_id
        )
        .first()
    )

    if not db_destination:
        raise HTTPException(
            status_code=404,
            detail="Destination not found",
        )

    update_data = destination_update.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():
        setattr(
            db_destination,
            key,
            value,
        )

    db.commit()
    db.refresh(db_destination)

    return db_destination


# ============================================================
# DELETE DESTINATION
# ============================================================

@router.delete("/{destination_id}")
async def delete_destination(
    destination_id: int,
    db: Session = Depends(get_db),
):
    """Delete a destination."""

    db_destination = (
        db.query(Destination)
        .filter(
            Destination.id == destination_id
        )
        .first()
    )

    if not db_destination:
        raise HTTPException(
            status_code=404,
            detail="Destination not found",
        )

    db.delete(db_destination)
    db.commit()

    return {
        "message": "Destination deleted successfully"
    }