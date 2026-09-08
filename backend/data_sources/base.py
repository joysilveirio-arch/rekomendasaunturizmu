"""
Base Data Source Interface
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class BaseDataSource(ABC):
    """Abstract base class for data sources"""
    
    @abstractmethod
    def get_destinations(self) -> List[Dict[str, Any]]:
        """Get destinations data"""
        pass
    
    @abstractmethod
    def get_reviews(self) -> List[Dict[str, Any]]:
        """Get reviews data"""
        pass
    
    @abstractmethod
    def get_tourism_data(self) -> List[Dict[str, Any]]:
        """Get tourism data"""
        pass