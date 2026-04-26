import os
from datetime import timedelta

class Config:
    """Base configuration."""
    FLASK_ENV = os.environ.get("FLASK_ENV", "development")
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
    MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/servex_pro")
    JWT_SECRET = os.environ.get("JWT_SECRET", "jwt-secret-key")
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRATION = timedelta(hours=24)
    GOOGLE_MAPS_API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY", "")
    
    # SocketIO config
    SOCKETIO_CORS_ALLOWED_ORIGINS = "*"
    
    # Pricing config
    BASE_PRICE = 50  # Base price in currency units
    DEMAND_SUPPLY_RATIO_MULTIPLIER = 1.5
    
    # Matching algorithm weights
    RATING_WEIGHT = 0.4
    DISTANCE_WEIGHT = 0.3
    PRICE_WEIGHT = 0.3


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    TESTING = False


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    MONGO_URI = "mongodb://localhost:27017/servex_pro_test"


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
