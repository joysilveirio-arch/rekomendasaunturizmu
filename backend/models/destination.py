"""
Destination Model
Represents tourism destinations in Timor-Leste
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database import Base


class Destination(Base):
    __tablename__ = "destinations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text)
    municipality = Column(String(100), nullable=False, index=True)
    location = Column(String(200))
    latitude = Column(Float)
    longitude = Column(Float)
    category = Column(String(50), nullable=False, index=True)
    rating = Column(Float, default=0.0)
    review_count = Column(Integer, default=0)
    price_level = Column(String(20), default="Medium")
    popularity_score = Column(Float, default=0.0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    reviews = relationship("Review", back_populates="destination", cascade="all, delete-orphan")
    clusters = relationship("Cluster", back_populates="destination", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="destination", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_destination_municipality_category', 'municipality', 'category'),
        Index('idx_destination_rating_popularity', 'rating', 'popularity_score'),
    )
    
    def __repr__(self):
        return f"<Destination(id={self.id}, name='{self.name}', rating={self.rating})>"