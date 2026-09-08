"""
Sentiment Analysis Service
Analyzes sentiment of tourism reviews using TextBlob
"""

import re
from typing import Dict, Any, List, Tuple, Optional
from textblob import TextBlob
from collections import Counter

from backend.config import settings
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class SentimentAnalyzer:
    """Sentiment analysis service using TextBlob"""
    
    def __init__(self):
        self.positive_threshold = settings.SENTIMENT_POSITIVE_THRESHOLD
        self.negative_threshold = settings.SENTIMENT_NEGATIVE_THRESHOLD
    
    def analyze(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of a text
        
        Returns:
            Dict with sentiment and score
        """
        if not text or not text.strip():
            return {
                "sentiment": "Neutral",
                "score": 0.0,
                "subjectivity": 0.0,
                "polarity": 0.0
            }
        
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity
            
            # Determine sentiment
            if polarity > self.positive_threshold:
                sentiment = "Positive"
            elif polarity < self.negative_threshold:
                sentiment = "Negative"
            else:
                sentiment = "Neutral"
            
            return {
                "sentiment": sentiment,
                "score": polarity,
                "polarity": polarity,
                "subjectivity": subjectivity
            }
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return {
                "sentiment": "Neutral",
                "score": 0.0,
                "polarity": 0.0,
                "subjectivity": 0.0
            }
    
    def extract_keywords(self, text: str, top_n: int = 10) -> List[str]:
        """Extract keywords from text"""
        if not text:
            return []
        
        # Clean and tokenize
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        
        # Remove stopwords
        stopwords = {
            'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had',
            'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his',
            'how', 'its', 'new', 'now', 'old', 'see', 'two', 'way', 'who', 'boy',
            'did', 'yet', 'she', 'say', 'too', 'put', 'got', 'let', 'use', 'may',
            'try', 'set', 'etc', 'any', 'big', 'own', 'try', 'get', 'use', 'way'
        }
        
        keywords = [w for w in words if w not in stopwords and len(w) > 2]
        
        # Get most common
        counter = Counter(keywords)
        return [word for word, _ in counter.most_common(top_n)]
    
    def batch_analyze(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Analyze multiple texts"""
        return [self.analyze(text) for text in texts]


def get_sentiment_summary_for_destination(destination_id: int, db) -> Dict[str, Any]:
    """Get sentiment summary for a destination"""
    from backend.models.review import Review
    
    reviews = db.query(Review).filter(Review.destination_id == destination_id).all()
    
    if not reviews:
        return {
            "positive": 0,
            "neutral": 0,
            "negative": 0,
            "total": 0,
            "average_score": 0
        }
    
    total = len(reviews)
    positive = sum(1 for r in reviews if r.sentiment == "Positive")
    neutral = sum(1 for r in reviews if r.sentiment == "Neutral")
    negative = sum(1 for r in reviews if r.sentiment == "Negative")
    avg_score = sum(r.sentiment_score for r in reviews) / total if total > 0 else 0
    
    return {
        "positive": round(positive / total * 100, 1),
        "neutral": round(neutral / total * 100, 1),
        "negative": round(negative / total * 100, 1),
        "total": total,
        "average_score": round(avg_score, 3)
    }