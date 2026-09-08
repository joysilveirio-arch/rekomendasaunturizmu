"""
Database Seeding Script
Populates the database with initial sample data
"""

import random
import datetime
from sqlalchemy.orm import Session
from backend.database import engine, SessionLocal, Base
from backend.models.destination import Destination
from backend.models.review import Review
from backend.models.cluster import Cluster
from backend.models.recommendation import Recommendation
from backend.models.collection_log import DataCollectionLog
from backend.services.sentiment import SentimentAnalyzer
from backend.services.clustering import ClusteringService
from backend.services.recommendation import RecommendationService
from backend.utils.logger import get_logger

logger = get_logger(__name__)

# Timor-Leste sample destinations
SAMPLE_DESTINATIONS = [
    {
        "name": "Atauro Island",
        "description": "A stunning island north of Dili with crystal clear waters, rich marine life, and vibrant local culture. Perfect for diving, snorkeling, and experiencing authentic Timorese island life.",
        "municipality": "Dili",
        "latitude": -8.2065,
        "longitude": 125.6300,
        "category": "Beach",
        "rating": 4.8,
        "review_count": 1250,
        "price_level": "Medium",
        "popularity_score": 95
    },
    {
        "name": "Jaco Island",
        "description": "A pristine tropical paradise at the eastern tip of Timor-Leste. Famous for its white sand beaches, turquoise waters, and diverse marine ecosystem.",
        "municipality": "Lautem",
        "latitude": -8.4250,
        "longitude": 127.3167,
        "category": "Nature",
        "rating": 4.7,
        "review_count": 890,
        "price_level": "Medium",
        "popularity_score": 88
    },
    {
        "name": "Cristo Rei",
        "description": "The iconic statue of Christ overlooking Dili Bay. A popular pilgrimage site offering panoramic views of the city and coastline.",
        "municipality": "Dili",
        "latitude": -8.5222,
        "longitude": 125.5854,
        "category": "Cultural",
        "rating": 4.5,
        "review_count": 750,
        "price_level": "Low",
        "popularity_score": 82
    },
    {
        "name": "Mount Ramelau",
        "description": "The highest peak in Timor-Leste at 2,963 meters. Popular for sunrise trekking and experiencing the cool mountain climate.",
        "municipality": "Ainaro",
        "latitude": -8.9117,
        "longitude": 125.5742,
        "category": "Adventure",
        "rating": 4.9,
        "review_count": 620,
        "price_level": "Low",
        "popularity_score": 78
    },
    {
        "name": "Tasitolu",
        "description": "A beautiful saltwater lake and national park near Dili. Features scenic views, bird watching, and historical significance.",
        "municipality": "Dili",
        "latitude": -8.5619,
        "longitude": 125.5428,
        "category": "Nature",
        "rating": 4.3,
        "review_count": 540,
        "price_level": "Low",
        "popularity_score": 70
    },
    {
        "name": "Com Beach",
        "description": "A stunning stretch of coastline with golden sands and crystal clear waters. Popular for swimming and relaxation.",
        "municipality": "Lautem",
        "latitude": -8.3567,
        "longitude": 126.8928,
        "category": "Beach",
        "rating": 4.4,
        "review_count": 480,
        "price_level": "Low",
        "popularity_score": 68
    },
    {
        "name": "Baucau",
        "description": "Timor-Leste's second largest city with Portuguese colonial architecture, beautiful beaches, and a relaxed atmosphere.",
        "municipality": "Baucau",
        "latitude": -8.4744,
        "longitude": 126.4550,
        "category": "Cultural",
        "rating": 4.2,
        "review_count": 430,
        "price_level": "Low",
        "popularity_score": 62
    },
    {
        "name": "Dare",
        "description": "A peaceful mountain village with cool climate, lush forests, and panoramic views of Dili and the sea.",
        "municipality": "Dili",
        "latitude": -8.5828,
        "longitude": 125.5653,
        "category": "Nature",
        "rating": 4.6,
        "review_count": 390,
        "price_level": "Low",
        "popularity_score": 72
    },
    {
        "name": "Maubisse",
        "description": "A colonial-era mountain retreat with cool temperatures, historic buildings, and stunning mountain scenery.",
        "municipality": "Ainaro",
        "latitude": -8.8403,
        "longitude": 125.5903,
        "category": "Cultural",
        "rating": 4.1,
        "review_count": 320,
        "price_level": "Medium",
        "popularity_score": 55
    },
    {
        "name": "Liquica",
        "description": "A coastal town known for its hot springs, colonial churches, and proximity to beautiful beaches.",
        "municipality": "Liquica",
        "latitude": -8.6156,
        "longitude": 125.3378,
        "category": "Cultural",
        "rating": 3.9,
        "review_count": 280,
        "price_level": "Low",
        "popularity_score": 48
    },
    {
        "name": "Tutuala",
        "description": "A traditional village at the eastern tip with stunning coastline views and access to nearby islands.",
        "municipality": "Lautem",
        "latitude": -8.3878,
        "longitude": 127.2725,
        "category": "Cultural",
        "rating": 4.0,
        "review_count": 210,
        "price_level": "Low",
        "popularity_score": 42
    },
    {
        "name": "Lospalos",
        "description": "An inland town with traditional Timorese culture and access to nearby waterfalls and natural attractions.",
        "municipality": "Lautem",
        "latitude": -8.5186,
        "longitude": 126.9967,
        "category": "Cultural",
        "rating": 3.8,
        "review_count": 180,
        "price_level": "Low",
        "popularity_score": 38
    }
]

# Sample reviews for each destination
SAMPLE_REVIEWS = [
    ("Absolutely breathtaking! The crystal clear waters and vibrant coral reefs made this the highlight of my trip.", 5),
    ("Great place to relax and enjoy nature. The locals are incredibly friendly and welcoming.", 4),
    ("Beautiful island with amazing snorkeling. Definitely worth the boat trip from Dili.", 5),
    ("A must-visit destination in Timor-Leste. The scenery is absolutely stunning.", 5),
    ("Peaceful and serene. Perfect for escaping the city and connecting with nature.", 4),
    ("The views are spectacular but the road to get there needs improvement.", 3),
    ("An unforgettable experience. I would highly recommend this to any traveler.", 5),
    ("Good spot but can get crowded during peak season. Go early in the morning.", 3),
    ("Absolutely magical place. The sunrise view from the top is worth every step.", 5),
    ("Cultural and historical significance makes this a meaningful visit.", 4),
    ("Beautiful scenery but limited facilities. Bring your own food and water.", 3),
    ("One of the best destinations in Timor-Leste. Pure natural beauty.", 5),
    ("Rich in culture and history. The local guides are very knowledgeable.", 4),
    ("Amazing place but prices for tourists are a bit high compared to local standards.", 3),
    ("Perfect for adventure seekers. The hike is challenging but rewarding.", 5),
    ("A hidden gem in Timor-Leste. Not many tourists know about this place.", 5),
    ("Good for a day trip but not much to do for longer stays.", 3),
    ("Stunning natural beauty and very peaceful. Highly recommended.", 5),
    ("Interesting cultural experience but the infrastructure needs improvement.", 3),
    ("I had a wonderful time here. The people are incredibly warm and hospitable.", 4),
]


def seed_database():
    """Seed the database with sample data"""
    db = SessionLocal()
    
    try:
        logger.info("Starting database seeding...")
        
        # Clear existing data
        db.query(Recommendation).delete()
        db.query(Cluster).delete()
        db.query(Review).delete()
        db.query(Destination).delete()
        db.query(DataCollectionLog).delete()
        db.commit()
        
        # Create destinations
        destinations = []
        for dest_data in SAMPLE_DESTINATIONS:
            dest = Destination(**dest_data)
            db.add(dest)
            db.flush()
            destinations.append(dest)
        
        db.commit()
        logger.info(f"Created {len(destinations)} destinations")
        
        # Create reviews for each destination
        sentiment_analyzer = SentimentAnalyzer()
        review_texts = [r[0] for r in SAMPLE_REVIEWS]
        review_ratings = [r[1] for r in SAMPLE_REVIEWS]
        
        for dest in destinations:
            # Add 10-20 reviews per destination
            num_reviews = random.randint(10, 20)
            for i in range(num_reviews):
                review_idx = random.randint(0, len(review_texts) - 1)
                text = review_texts[review_idx]
                rating = review_ratings[review_idx] + random.uniform(-0.5, 0.5)
                rating = max(1, min(5, rating))
                
                # Analyze sentiment
                sentiment_result = sentiment_analyzer.analyze(text)
                
                review = Review(
                    destination_id=dest.id,
                    review_text=text,
                    rating=round(rating, 1),
                    sentiment=sentiment_result["sentiment"],
                    sentiment_score=sentiment_result["score"],
                    source="mock_data",
                    review_date=datetime.datetime.now() - datetime.timedelta(days=random.randint(1, 365))
                )
                db.add(review)
        
        db.commit()
        logger.info("Created sample reviews")
        
        # Update destination ratings based on reviews
        for dest in destinations:
            reviews = db.query(Review).filter(Review.destination_id == dest.id).all()
            if reviews:
                avg_rating = sum(r.rating for r in reviews) / len(reviews)
                dest.rating = round(avg_rating, 1)
                dest.review_count = len(reviews)
        db.commit()
        
        # Run clustering
        logger.info("Running clustering...")
        clustering_service = ClusteringService(db)
        clusters_df = clustering_service.perform_clustering()
        
        # Save cluster assignments
        for dest in destinations:
            cluster_id = clustering_service.get_cluster_id(dest.id)
            if cluster_id is not None:
                cluster_label = clustering_service.get_cluster_label(dest.id)
                cluster = Cluster(
                    destination_id=dest.id,
                    cluster_id=cluster_id,
                    cluster_name=cluster_label,
                    cluster_score=0.5 + random.random() * 0.4,
                    created_at=datetime.datetime.now()
                )
                db.add(cluster)
        db.commit()
        logger.info("Clustering completed")
        
        # Generate recommendations
        logger.info("Generating recommendations...")
        recommendation_service = RecommendationService(db)
        
        for user_type in ["Adventure", "Culture", "Relaxation", "Nature", "Beach"]:
            for category in ["Beach", "Nature", "Cultural", "Adventure"]:
                recommendations = recommendation_service.get_recommendations(
                    user_type=user_type,
                    category=category,
                    min_rating=4.0,
                    budget="Medium"
                )
                # FIX: Use rec.destination.id instead of rec.destination_id
                for rec in recommendations:
                    db_recommendation = Recommendation(
                        destination_id=rec.destination.id,  # FIX HERE
                        user_type=user_type,
                        category=category,
                        recommendation_score=rec.score
                    )
                    db.add(db_recommendation)
        db.commit()
        logger.info("Recommendations generated")
        
        # Create a collection log
        log = DataCollectionLog(
            source="seed_script",
            status="success",
            records_collected=len(SAMPLE_DESTINATIONS),
            message="Database seeded successfully",
            started_at=datetime.datetime.now() - datetime.timedelta(minutes=5),
            completed_at=datetime.datetime.now()
        )
        db.add(log)
        db.commit()
        
        logger.info("Database seeding completed successfully!")
        
    except Exception as e:
        logger.error(f"Error seeding database: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
    print("Database seeded successfully!")