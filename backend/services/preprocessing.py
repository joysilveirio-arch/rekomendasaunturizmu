"""
Data Preprocessing Service
Handles cleaning and preprocessing of tourism data
"""

import re
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from datetime import datetime

from backend.utils.logger import get_logger

logger = get_logger(__name__)


class PreprocessingService:
    """Service for preprocessing tourism data"""
    
    def __init__(self):
        self.stopwords = self._load_stopwords()
    
    def _load_stopwords(self) -> set:
        """Load common stopwords"""
        return {
            'a', 'an', 'the', 'and', 'or', 'but', 'for', 'nor', 'on', 'at', 'to', 'by',
            'in', 'of', 'with', 'without', 'about', 'across', 'after', 'against', 'along',
            'among', 'around', 'at', 'before', 'behind', 'below', 'beneath', 'beside',
            'between', 'beyond', 'by', 'down', 'during', 'except', 'for', 'from', 'in',
            'inside', 'into', 'like', 'near', 'of', 'off', 'on', 'onto', 'out', 'outside',
            'over', 'past', 'since', 'through', 'throughout', 'to', 'toward', 'under',
            'until', 'up', 'upon', 'with', 'within', 'without', 'is', 'am', 'are', 'was',
            'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did'
        }
    
    def clean_text(self, text: str) -> str:
        """Clean text data"""
        if not text:
            return ""
        
        # Lowercase
        text = text.lower()
        
        # Remove special characters and numbers
        text = re.sub(r'[^a-zA-Z\s]', ' ', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def remove_stopwords(self, text: str) -> str:
        """Remove stopwords from text"""
        if not text:
            return ""
        
        words = text.split()
        filtered = [w for w in words if w not in self.stopwords]
        return ' '.join(filtered)
    
    def preprocess_review(self, review_text: str) -> str:
        """Preprocess a review text"""
        if not review_text:
            return ""
        
        # Clean
        cleaned = self.clean_text(review_text)
        
        # Remove stopwords
        cleaned = self.remove_stopwords(cleaned)
        
        return cleaned
    
    def extract_features(self, destination_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract features for clustering"""
        features = {}
        
        # Normalize rating
        features['rating'] = destination_data.get('rating', 0.0) / 5.0
        
        # Normalize review count
        max_reviews = 1000  # Assumed maximum
        features['review_count'] = min(destination_data.get('review_count', 0) / max_reviews, 1.0)
        
        # Normalize popularity
        features['popularity_score'] = destination_data.get('popularity_score', 0.0) / 100.0
        
        # Sentiment score (if available)
        features['sentiment_score'] = destination_data.get('sentiment_score', 0.0) / 1.0
        
        # Price level encoding
        price_map = {'Low': 0.0, 'Medium': 0.5, 'High': 1.0}
        features['price_level'] = price_map.get(destination_data.get('price_level', 'Medium'), 0.5)
        
        # Category encoding (simplified)
        category_map = {
            'Beach': 1.0,
            'Nature': 0.75,
            'Cultural': 0.5,
            'Adventure': 0.25,
            'City': 0.0
        }
        features['category'] = category_map.get(destination_data.get('category', 'Cultural'), 0.5)
        
        return features
    
    def normalize_features(self, features: Dict[str, float]) -> Dict[str, float]:
        """Normalize feature values"""
        normalized = {}
        for key, value in features.items():
            # Ensure values are between 0 and 1
            normalized[key] = max(0, min(1, value))
        return normalized
    
    def prepare_clustering_data(self, destinations: List[Dict[str, Any]]) -> np.ndarray:
        """Prepare data for clustering"""
        feature_vectors = []
        
        for dest in destinations:
            features = self.extract_features(dest)
            normalized = self.normalize_features(features)
            
            # Convert to vector in consistent order
            vector = [
                normalized.get('rating', 0.0),
                normalized.get('review_count', 0.0),
                normalized.get('popularity_score', 0.0),
                normalized.get('sentiment_score', 0.0),
                normalized.get('price_level', 0.5),
                normalized.get('category', 0.5)
            ]
            feature_vectors.append(vector)
        
        return np.array(feature_vectors)