"""
Data Collection Log Model
Tracks data collection activities and status
"""

from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from backend.database import Base


class DataCollectionLog(Base):
    __tablename__ = "data_collection_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(100))
    status = Column(String(20), default="pending")
    records_collected = Column(Integer, default=0)
    message = Column(Text)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    
    def __repr__(self):
        return f"<DataCollectionLog(id={self.id}, source='{self.source}', status='{self.status}')>"