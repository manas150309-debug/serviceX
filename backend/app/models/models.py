from datetime import datetime
from bson import ObjectId
from app import get_db
import bcrypt


class User:
    """User model for customers."""
    
    @staticmethod
    def create_user(name, email, password, phone, location):
        """Create a new user."""
        db = get_db()
        
        # Check if user exists
        if db.users.find_one({"email": email}):
            return None
        
        # Hash password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        user_data = {
            "name": name,
            "email": email,
            "password": hashed_password,
            "phone": phone,
            "location": {
                "latitude": location.get("latitude"),
                "longitude": location.get("longitude"),
                "address": location.get("address", "")
            },
            "role": "customer",
            "rating": 0,
            "total_bookings": 0,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "is_active": True
        }
        
        result = db.users.insert_one(user_data)
        return str(result.inserted_id)
    
    @staticmethod
    def get_user_by_email(email):
        """Get user by email."""
        db = get_db()
        return db.users.find_one({"email": email})
    
    @staticmethod
    def get_user_by_id(user_id):
        """Get user by ID."""
        db = get_db()
        return db.users.find_one({"_id": ObjectId(user_id)})
    
    @staticmethod
    def verify_password(stored_password, provided_password):
        """Verify password hash."""
        return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password)
    
    @staticmethod
    def update_user(user_id, data):
        """Update user data."""
        db = get_db()
        data["updated_at"] = datetime.utcnow()
        db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": data}
        )
        return User.get_user_by_id(user_id)


class Provider:
    """Provider model for service providers."""
    
    @staticmethod
    def create_provider(name, email, password, phone, service_type, location, experience_years, hourly_rate):
        """Create a new provider."""
        db = get_db()
        
        # Check if provider exists
        if db.providers.find_one({"email": email}):
            return None
        
        # Hash password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        provider_data = {
            "name": name,
            "email": email,
            "password": hashed_password,
            "phone": phone,
            "service_type": service_type,
            "location": {
                "latitude": location.get("latitude"),
                "longitude": location.get("longitude"),
                "address": location.get("address", "")
            },
            "experience_years": experience_years,
            "hourly_rate": hourly_rate,
            "role": "provider",
            "rating": 0,
            "total_jobs": 0,
            "available": True,
            "is_verified": False,
            "documents": [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "is_active": True
        }
        
        result = db.providers.insert_one(provider_data)
        return str(result.inserted_id)
    
    @staticmethod
    def get_provider_by_email(email):
        """Get provider by email."""
        db = get_db()
        return db.providers.find_one({"email": email})
    
    @staticmethod
    def get_provider_by_id(provider_id):
        """Get provider by ID."""
        db = get_db()
        return db.providers.find_one({"_id": ObjectId(provider_id)})
    
    @staticmethod
    def get_providers_by_service(service_type):
        """Get all providers for a service type."""
        db = get_db()
        return list(db.providers.find({"service_type": service_type, "available": True}))
    
    @staticmethod
    def update_provider(provider_id, data):
        """Update provider data."""
        db = get_db()
        data["updated_at"] = datetime.utcnow()
        db.providers.update_one(
            {"_id": ObjectId(provider_id)},
            {"$set": data}
        )
        return Provider.get_provider_by_id(provider_id)
    
    @staticmethod
    def verify_password(stored_password, provided_password):
        """Verify password hash."""
        return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password)


class Booking:
    """Booking model."""
    
    STATUSES = ["pending", "accepted", "in_progress", "completed", "cancelled"]
    
    @staticmethod
    def create_booking(user_id, service_type, description, location, scheduled_date, estimated_hours):
        """Create a new booking."""
        db = get_db()
        
        booking_data = {
            "user_id": ObjectId(user_id),
            "service_type": service_type,
            "description": description,
            "location": location,
            "scheduled_date": scheduled_date,
            "estimated_hours": estimated_hours,
            "provider_id": None,
            "status": "pending",
            "base_price": None,
            "final_price": None,
            "bids": [],
            "assigned_provider": None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "completed_at": None
        }
        
        result = db.bookings.insert_one(booking_data)
        return str(result.inserted_id)
    
    @staticmethod
    def get_booking_by_id(booking_id):
        """Get booking by ID."""
        db = get_db()
        return db.bookings.find_one({"_id": ObjectId(booking_id)})
    
    @staticmethod
    def get_user_bookings(user_id):
        """Get all bookings for a user."""
        db = get_db()
        return list(db.bookings.find({"user_id": ObjectId(user_id)}).sort("created_at", -1))
    
    @staticmethod
    def get_provider_bookings(provider_id):
        """Get all bookings for a provider."""
        db = get_db()
        return list(db.bookings.find({"assigned_provider": ObjectId(provider_id)}).sort("created_at", -1))
    
    @staticmethod
    def update_booking_status(booking_id, status):
        """Update booking status."""
        db = get_db()
        if status not in Booking.STATUSES:
            return None
        
        db.bookings.update_one(
            {"_id": ObjectId(booking_id)},
            {"$set": {
                "status": status,
                "updated_at": datetime.utcnow(),
                "completed_at": datetime.utcnow() if status == "completed" else None
            }}
        )
        return Booking.get_booking_by_id(booking_id)
    
    @staticmethod
    def assign_provider(booking_id, provider_id, final_price):
        """Assign provider to booking."""
        db = get_db()
        db.bookings.update_one(
            {"_id": ObjectId(booking_id)},
            {"$set": {
                "assigned_provider": ObjectId(provider_id),
                "provider_id": ObjectId(provider_id),
                "final_price": final_price,
                "status": "accepted",
                "updated_at": datetime.utcnow()
            }}
        )
        return Booking.get_booking_by_id(booking_id)


class Bid:
    """Bid model for provider bidding."""
    
    @staticmethod
    def create_bid(booking_id, provider_id, bid_price, estimated_time):
        """Create a new bid."""
        db = get_db()
        
        bid_data = {
            "booking_id": ObjectId(booking_id),
            "provider_id": ObjectId(provider_id),
            "bid_price": bid_price,
            "estimated_time": estimated_time,
            "status": "pending",
            "created_at": datetime.utcnow()
        }
        
        result = db.bids.insert_one(bid_data)
        
        # Add bid to booking
        db.bookings.update_one(
            {"_id": ObjectId(booking_id)},
            {"$push": {"bids": str(result.inserted_id)}}
        )
        
        return str(result.inserted_id)
    
    @staticmethod
    def get_bids_for_booking(booking_id):
        """Get all bids for a booking."""
        db = get_db()
        return list(db.bids.find({"booking_id": ObjectId(booking_id)}))


class Rating:
    """Rating/Review model."""
    
    @staticmethod
    def create_rating(booking_id, rater_id, ratee_id, rating, review_text, rater_role):
        """Create a new rating."""
        db = get_db()
        
        rating_data = {
            "booking_id": ObjectId(booking_id),
            "rater_id": ObjectId(rater_id),
            "ratee_id": ObjectId(ratee_id),
            "rating": rating,
            "review_text": review_text,
            "rater_role": rater_role,
            "created_at": datetime.utcnow()
        }
        
        result = db.ratings.insert_one(rating_data)
        
        # Update average rating for the ratee
        ratings = list(db.ratings.find({"ratee_id": ObjectId(ratee_id)}))
        if ratings:
            avg_rating = sum(r["rating"] for r in ratings) / len(ratings)
            
            # Update user or provider
            if rater_role == "customer":
                db.providers.update_one(
                    {"_id": ObjectId(ratee_id)},
                    {"$set": {"rating": round(avg_rating, 2)}}
                )
            else:
                db.users.update_one(
                    {"_id": ObjectId(ratee_id)},
                    {"$set": {"rating": round(avg_rating, 2)}}
                )
        
        return str(result.inserted_id)
    
    @staticmethod
    def get_ratings_for_user(user_id):
        """Get all ratings for a user."""
        db = get_db()
        return list(db.ratings.find({"ratee_id": ObjectId(user_id)}))
