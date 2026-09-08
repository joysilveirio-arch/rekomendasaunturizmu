"""
SQLAlchemy Model Registry

Import all models here so SQLAlchemy can resolve
string-based relationships correctly.
"""

from backend.models.destination import Destination
from backend.models.review import Review
from backend.models.cluster import Cluster
from backend.models.recommendation import Recommendation
from backend.models.collection_log import DataCollectionLog

__all__ = [
    "Destination",
    "Review",
    "Cluster",
    "Recommendation",
    "DataCollectionLog",
]