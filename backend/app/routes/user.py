from flask import Blueprint, request, jsonify
from app.models import User, Booking, Rating
from app.utils import token_required, role_required

user_bp = Blueprint('user', __name__, url_prefix='/api/users')


@user_bp.route('/<user_id>', methods=['GET'])
def get_user(user_id):
    """Get user profile."""
    user = User.get_user_by_id(user_id)
    
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    # Remove sensitive data
    user.pop('password', None)
    user['_id'] = str(user['_id'])
    
    return jsonify(user), 200


@user_bp.route('/<user_id>', methods=['PUT'])
@token_required
@role_required('customer')
def update_user(user_id):
    """Update user profile."""
    if request.user_id != user_id:
        return jsonify({'message': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    # Don't allow updating sensitive fields
    data.pop('password', None)
    data.pop('role', None)
    data.pop('email', None)
    
    user = User.update_user(user_id, data)
    
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    user.pop('password', None)
    user['_id'] = str(user['_id'])
    
    return jsonify({
        'message': 'User updated successfully',
        'user': user
    }), 200


@user_bp.route('/<user_id>/bookings', methods=['GET'])
@token_required
def get_user_bookings(user_id):
    """Get user's booking history."""
    if request.user_role == 'customer' and request.user_id != user_id:
        return jsonify({'message': 'Unauthorized'}), 403
    
    bookings = Booking.get_user_bookings(user_id)
    
    # Convert ObjectIds to strings
    for booking in bookings:
        booking['_id'] = str(booking['_id'])
        booking['user_id'] = str(booking['user_id'])
        if booking.get('provider_id'):
            booking['provider_id'] = str(booking['provider_id'])
        if booking.get('assigned_provider'):
            booking['assigned_provider'] = str(booking['assigned_provider'])
    
    return jsonify({
        'total': len(bookings),
        'bookings': bookings
    }), 200


@user_bp.route('/<user_id>/ratings', methods=['GET'])
def get_user_ratings(user_id):
    """Get ratings for a user."""
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
