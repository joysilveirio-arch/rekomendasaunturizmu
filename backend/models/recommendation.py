"""
Recommendation Model
Stores generated recommendations for users
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database import Base


class Recommendation(Base):
    __tablename__ = "recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    destination_id = Column(Integer, ForeignKey("destinations.id", ondelete="CASCADE"), nullable=False)
    user_type = Column(String(50), nullable=False)
    category = Column(String(50), nullable=False)
    recommendation_score = Column(Float, default=0.0)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    destination = relationship("Destination", back_populates="recommendations")
    
    # Indexes
    __table_args__ = (
        Index('idx_recommendation_user_category', 'user_type', 'category'),
        Index('idx_recommendation_score', 'recommendation_score'),
    )
    
    def __repr__(self):
        return f"<Recommendation(id={self.id}, destination_id={self.destination_id}, score={self.recommendation_score})>"