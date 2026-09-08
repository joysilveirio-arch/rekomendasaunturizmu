"""
Sentiment Analysis Tests
"""

import pytest
from backend.services.sentiment import SentimentAnalyzer


def test_sentiment_analyzer_init():
    """Test sentiment analyzer initialization"""
    analyzer = SentimentAnalyzer()
    assert analyzer is not None
    assert analyzer.positive_threshold == 0.05
    assert analyzer.negative_threshold == -0.05


def test_sentiment_positive():
    """Test positive sentiment detection"""
    analyzer = SentimentAnalyzer()
    result = analyzer.analyze("This place is absolutely amazing and beautiful!")
    assert result["sentiment"] == "Positive"
    assert result["score"] > 0


def test_sentiment_negative():
    """Test negative sentiment detection"""
    analyzer = SentimentAnalyzer()
    result = analyzer.analyze("This was terrible and disappointing.")
    assert result["sentiment"] == "Negative"
    assert result["score"] < 0


def test_sentiment_neutral():
    """Test neutral sentiment detection"""
    analyzer = SentimentAnalyzer()
    result = analyzer.analyze("The place is okay.")
    assert result["sentiment"] == "Neutral"


def test_sentiment_empty():
    """Test empty text handling"""
    analyzer = SentimentAnalyzer()
    result = analyzer.analyze("")
    assert result["sentiment"] == "Neutral"
    assert result["score"] == 0.0


def test_extract_keywords():
    """Test keyword extraction"""
    analyzer = SentimentAnalyzer()
    keywords = analyzer.extract_keywords("Beautiful beach with amazing views and great food.")
    assert len(keywords) > 0
    assert "beach" in keywords or "beautiful" in keywords