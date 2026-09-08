"""
Clustering Tests
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.database import Base
from backend.services.clustering import ClusteringService
from backend.models.destination import Destination
from backend.models.review import Review


@pytest.fixture
def db_session():
    """Create a test database session"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()


def test_clustering_service_init(db_session):
    """Test clustering service initialization"""
    service = ClusteringService(db_session)
    assert service.db is not None
    assert service.kmeans is None


def test_clustering_perform(db_session):
    """Test clustering execution"""
    # Add test destinations
    dest = Destination(
        name="Test Destination",
        municipality="Dili",
        category="Beach",
        rating=4.5,
        review_count=100,
        popularity_score=85,
        price_level="Medium"
    )
    db_session.add(dest)
    db_session.commit()
    
    service = ClusteringService(db_session)
    result = service.perform_clustering(n_clusters=2)
    
    # Should return a DataFrame
    assert result is not None