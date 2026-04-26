from flask import Blueprint, request, jsonify
from app.models import Booking, Bid, Provider
from app.utils import token_required, role_required
from app.utils.pricing import DynamicPricingEngine

booking_bp = Blueprint('booking', __name__, url_prefix='/api/bookings')


@booking_bp.route('', methods=['POST'])
@token_required
@role_required('customer')
def create_booking():
    """Create a new booking."""
    data = request.get_json()
    
    required_fields = ['service_type', 'description', 'location', 'scheduled_date', 'estimated_hours']
    if not all(field in data for field in required_fields):
        return jsonify({'message': 'Missing required fields'}), 400
    
    booking_id = Booking.create_booking(
        user_id=request.user_id,
        service_type=data['service_type'],
        description=data['description'],
        location=data['location'],
        scheduled_date=data['scheduled_date'],
        estimated_hours=data['estimated_hours']
    )
    
    # Calculate base price based on dynamic pricing
    base_price = DynamicPricingEngine.calculate_dynamic_price(
        current_app.config['BASE_PRICE'],
        data['service_type']
    )
    
    # Update booking with base price
    from app import get_db
    db = get_db()
    db.bookings.update_one(
        {'_id': ObjectId(booking_id)},
        {'$set': {'base_price': base_price}}
    )
    
    return jsonify({
        'message': 'Booking created successfully',
        'booking_id': booking_id
    }), 201


@booking_bp.route('/<booking_id>', methods=['GET'])
@token_required
def get_booking(booking_id):
    """Get booking details."""
    booking = Booking.get_booking_by_id(booking_id)
    
    if not booking:
        return jsonify({'message': 'Booking not found'}), 404
    
    # Convert ObjectIds to strings
    booking['_id'] = str(booking['_id'])
    booking['user_id'] = str(booking['user_id'])
    if booking.get('provider_id'):
        booking['provider_id'] = str(booking['provider_id'])
    if booking.get('assigned_provider'):
        booking['assigned_provider'] = str(booking['assigned_provider'])
    
    return jsonify(booking), 200


@booking_bp.route('/<booking_id>/status', methods=['PUT'])
@token_required
def update_booking_status(booking_id):
    """Update booking status."""
    data = request.get_json()
    
    if 'status' not in data:
        return jsonify({'message': 'Status field is required'}), 400
    
    booking = Booking.update_booking_status(booking_id, data['status'])
    
    if not booking:
        return jsonify({'message': 'Booking not found or invalid status'}), 404
    
    booking['_id'] = str(booking['_id'])
    booking['user_id'] = str(booking['user_id'])
    if booking.get('provider_id'):
        booking['provider_id'] = str(booking['provider_id'])
    
    return jsonify({
        'message': 'Booking status updated',
        'booking': booking
    }), 200


@booking_bp.route('/<booking_id>/cancel', methods=['POST'])
@token_required
def cancel_booking(booking_id):
    """Cancel a booking."""
    booking = Booking.get_booking_by_id(booking_id)
    
    if not booking:
        return jsonify({'message': 'Booking not found'}), 404
    
    # Check authorization
    if request.user_role == 'customer' and request.user_id != str(booking['user_id']):
        return jsonify({'message': 'Unauthorized'}), 403
    
    if booking['status'] in ['completed', 'cancelled']:
        return jsonify({'message': 'Cannot cancel completed or already cancelled booking'}), 400
    
    booking = Booking.update_booking_status(booking_id, 'cancelled')
    
    booking['_id'] = str(booking['_id'])
    booking['user_id'] = str(booking['user_id'])
    
    return jsonify({
        'message': 'Booking cancelled successfully',
        'booking': booking
    }), 200


from bson import ObjectId
from flask import current_app
