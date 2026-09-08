"""
Sentiment Analysis Service

Analyzes sentiment of tourism reviews using TextBlob
"""

import re
from typing import Dict, Any, List
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
        Analyze sentiment of a text.

        Returns:
            Dict with sentiment, score, polarity, and subjectivity.
        """

        # Empty text is Neutral
        if not text or not text.strip():
            return {
                "sentiment": "Neutral",
                "score": 0.0,
                "polarity": 0.0,
                "subjectivity": 0.0
            }

        try:
            # TextBlob sentiment analysis
            blob = TextBlob(text)

            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity

            # ---------------------------------------------------------
            # Neutral expressions
            # ---------------------------------------------------------
            # TextBlob can sometimes classify expressions such as
            # "okay" as slightly positive. In tourism reviews,
            # expressions like these are better treated as Neutral.
            neutral_phrases = {
                "okay",
                "ok",
                "fine",
                "average",
                "acceptable",
                "ordinary",
                "nothing special",
                "not bad",
                "so so",
                "so-so"
            }

            # Normalize text for phrase matching
            normalized_text = re.sub(
                r"\s+",
                " ",
                text.lower()
            ).strip()

            # Check whether the review contains a neutral expression
            contains_neutral_phrase = any(
                phrase in normalized_text
                for phrase in neutral_phrases
            )

            # ---------------------------------------------------------
            # Determine sentiment
            # ---------------------------------------------------------
            if contains_neutral_phrase:
                sentiment = "Neutral"

            elif polarity > self.positive_threshold:
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

    def extract_keywords(
        self,
        text: str,
        top_n: int = 10
    ) -> List[str]:
        """Extract keywords from text"""

        if not text:
            return []

        # Clean and tokenize
        words = re.findall(
            r"\b[a-zA-Z]{3,}\b",
            text.lower()
        )

        # Remove common stopwords
        stopwords = {
            "the",
            "and",
            "for",
            "are",
            "but",
            "not",
            "you",
            "all",
            "can",
            "had",
            "her",
            "was",
            "one",
            "our",
            "out",
            "day",
            "get",
            "has",
            "him",
            "his",
            "how",
            "its",
            "new",
            "now",
            "old",
            "see",
            "two",
            "way",
            "who",
            "boy",
            "did",
            "yet",
            "she",
            "say",
            "too",
            "put",
            "got",
            "let",
            "use",
            "may",
            "try",
            "set",
            "etc",
            "any",
            "big",
            "own"
        }

        keywords = [
            word
            for word in words
            if word not in stopwords and len(word) > 2
        ]

        # Count keyword frequency
        counter = Counter(keywords)

        # Return most common keywords
        return [
            word
            for word, _ in counter.most_common(top_n)
        ]

    def batch_analyze(
        self,
        texts: List[str]
    ) -> List[Dict[str, Any]]:
        """Analyze multiple texts"""

        return [
            self.analyze(text)
            for text in texts
        ]


def get_sentiment_summary_for_destination(
    destination_id: int,
    db
) -> Dict[str, Any]:
    """Get sentiment summary for a destination"""

    from backend.models.review import Review

    reviews = (
        db.query(Review)
        .filter(Review.destination_id == destination_id)
        .all()
    )

    # No reviews
    if not reviews:
        return {
            "positive": 0,
            "neutral": 0,
            "negative": 0,
            "total": 0,
            "average_score": 0
        }

    total = len(reviews)

    # Count sentiment categories
    positive = sum(
        1
        for review in reviews
        if review.sentiment == "Positive"
    )

    neutral = sum(
        1
        for review in reviews
        if review.sentiment == "Neutral"
    )

    negative = sum(
        1
        for review in reviews
        if review.sentiment == "Negative"
    )

    # Calculate average sentiment score
    avg_score = (
        sum(
            review.sentiment_score
            for review in reviews
        ) / total
        if total > 0
        else 0
    )

    return {
        "positive": round(
            positive / total * 100,
            1
        ),
        "neutral": round(
            neutral / total * 100,
            1
        ),
        "negative": round(
            negative / total * 100,
            1
        ),
        "total": total,
        "average_score": round(
            avg_score,
            3
        )
    }