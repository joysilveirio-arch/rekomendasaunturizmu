"""
Recommendation Tests
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.database import Base
from backend.services.recommendation import RecommendationService
from backend.models.destination import Destination


@pytest.fixture
def db_session():
    """Create a test database session"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()


def test_recommendation_service_init(db_session):
    """Test recommendation service initialization"""
    service = RecommendationService(db_session)
    assert service.db is not None


def test_get_recommendations(db_session):
    """Test getting recommendations"""
    # Add test destinations
    dest1 = Destination(
        name="Beach Paradise",
        municipality="Dili",
        category="Beach",
        rating=4.8,
        review_count=200,
        popularity_score=90,
        price_level="Medium"
    )
    dest2 = Destination(
        name="Mountain Adventure",
        municipality="Ainaro",
        category="Adventure",
        rating=4.6,
        review_count=150,
        popularity_score=80,
        price_level="Low"
    )
    db_session.add_all([dest1, dest2])
    db_session.commit()
    
    service = RecommendationService(db_session)
    recommendations = service.get_recommendations(
        user_type="Adventure",
        category="Adventure",
        min_rating=4.0,
        limit=5
    )
    
    assert len(recommendations) > 0