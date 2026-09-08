"""
Review Model
Represents tourist reviews for destinations
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database import Base


class Review(Base):
    __tablename__ = "reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    destination_id = Column(Integer, ForeignKey("destinations.id", ondelete="CASCADE"), nullable=False)
    review_text = Column(Text)
    rating = Column(Float)
    sentiment = Column(String(20), default="Neutral")
    sentiment_score = Column(Float, default=0.0)
    source = Column(String(100))
    review_date = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    destination = relationship("Destination", back_populates="reviews")
    
    # Indexes
    __table_args__ = (
        Index('idx_review_destination_sentiment', 'destination_id', 'sentiment'),
        Index('idx_review_rating_sentiment_score', 'rating', 'sentiment_score'),
    )
    
    def __repr__(self):
        return f"<Review(id={self.id}, destination_id={self.destination_id}, sentiment='{self.sentiment}')>"