from flask import Blueprint, request, jsonify
from app.models import Rating, Booking
from app.utils import token_required

rating_bp = Blueprint('rating', __name__, url_prefix='/api/ratings')


@rating_bp.route('', methods=['POST'])
@token_required
def create_rating():
    """Create a rating for a booking."""
    data = request.get_json()
    
    required_fields = ['booking_id', 'ratee_id', 'rating', 'review_text']
    if not all(field in data for field in required_fields):
        return jsonify({'message': 'Missing required fields'}), 400
    
    if not (1 <= data['rating'] <= 5):
        return jsonify({'message': 'Rating must be between 1 and 5'}), 400
    
    # Verify booking exists and is completed
    booking = Booking.get_booking_by_id(data['booking_id'])
    if not booking:
        return jsonify({'message': 'Booking not found'}), 404
    
    if booking['status'] != 'completed':
        return jsonify({'message': 'Can only rate completed bookings'}), 400
    
    # Determine rater role
    rater_role = 'customer' if request.user_id == str(booking['user_id']) else 'provider'
    
    rating_id = Rating.create_rating(
        booking_id=data['booking_id'],
        rater_id=request.user_id,
        ratee_id=data['ratee_id'],
        rating=data['rating'],
        review_text=data['review_text'],
        rater_role=rater_role
    )
    
    return jsonify({
        'message': 'Rating created successfully',
        'rating_id': rating_id
    }), 201


@rating_bp.route('/<user_id>', methods=['GET'])
def get_user_ratings(user_id):
    """Get all ratings for a user."""
    ratings = Rating.get_ratings_for_user(user_id)
    
    # Convert ObjectIds to strings
    for rating in ratings:
        rating['_id'] = str(rating['_id'])
        rating['booking_id'] = str(rating['booking_id'])
        rating['rater_id'] = str(rating['rater_id'])
        rating['ratee_id'] = str(rating['ratee_id'])
    
    avg_rating = sum(r['rating'] for r in ratings) / len(ratings) if ratings else 0
    
    return jsonify({
        'user_id': user_id,
        'average_rating': round(avg_rating, 2),
        'total_ratings': len(ratings),
        'ratings': ratings
    }), 200
