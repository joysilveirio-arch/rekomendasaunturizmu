"""
Cluster Model

Stores K-Means clustering results for tourism destinations.
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    Index,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.database import Base


class Cluster(Base):
    """
    Stores the K-Means clustering result for each destination.
    """

    __tablename__ = "clusters"

    # Primary Key
    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
    )

    # Destination relationship
    destination_id = Column(
        Integer,
        ForeignKey(
            "destinations.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    # K-Means cluster ID
    # Example: 0, 1, 2, 3
    cluster_id = Column(
        Integer,
        nullable=False,
        index=True,
    )

    # Human-readable cluster name
    cluster_name = Column(
        String(100),
        nullable=True,
    )

    # Cluster score
    cluster_score = Column(
        Float,
        nullable=True,
    )

    # Creation timestamp
    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )

    # Relationship with Destination
    destination = relationship(
        "Destination",
        back_populates="clusters",
    )

    # Additional indexes
    __table_args__ = (
        Index(
            "idx_cluster_destination",
            "destination_id",
        ),
        Index(
            "idx_cluster_id",
            "cluster_id",
        ),
    )

    def __repr__(self):
        return (
            f"<Cluster("
            f"id={self.id}, "
            f"destination_id={self.destination_id}, "
            f"cluster_id={self.cluster_id}, "
            f"cluster_name='{self.cluster_name}'"
            f")>"
        )