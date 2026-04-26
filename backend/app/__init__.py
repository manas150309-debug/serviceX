from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize extensions
socketio = SocketIO()
mongo_client = None
db = None


def create_app(config_name="development"):
    """Application factory."""
    app = Flask(__name__)
    
    # Load configuration
    from config import config
    app.config.from_object(config[config_name])
    
    # Initialize CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Initialize SocketIO
    socketio.init_app(app, cors_allowed_origins="*")
    
    # Initialize MongoDB connection
    global mongo_client, db
    mongo_client = MongoClient(app.config["MONGO_URI"])
    db = mongo_client.get_database()
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.user import user_bp
    from app.routes.provider import provider_bp
    from app.routes.booking import booking_bp
    from app.routes.matching import matching_bp
    from app.routes.pricing import pricing_bp
    from app.routes.rating import rating_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(provider_bp)
    app.register_blueprint(booking_bp)
    app.register_blueprint(matching_bp)
    app.register_blueprint(pricing_bp)
    app.register_blueprint(rating_bp)
    
    # Setup SocketIO events
    from app.events import setup_events
    setup_events(socketio)
    
    # Health check endpoint
    @app.route("/health", methods=["GET"])
    def health_check():
        return {"status": "healthy"}, 200
    
    return app


def get_db():
    """Get database instance."""
    return db
