from flask import Blueprint, request, jsonify
from app.models import Bid, Booking, Provider
from app.utils import token_required, role_required, smart_match_provider
from bson import ObjectId

matching_bp = Blueprint('matching', __name__, url_prefix='/api/matching')


@matching_bp.route('/find-providers/<service_type>', methods=['POST'])
@token_required
def find_providers(service_type):
    """Find best providers for a service."""
    data = request.get_json()
    
    if 'location' not in data:
        return jsonify({'message': 'Location is required'}), 400
    
    location = data['location']
    
    from app.utils import find_best_providers
    providers = find_best_providers(service_type, location, limit=5)
    
    # Remove sensitive data
    for provider in providers:
        provider.pop('password', None)
        provider['_id'] = str(provider['_id'])
    
    return jsonify({
        'service_type': service_type,
        'total': len(providers),
        'providers': providers
    }), 200


@matching_bp.route('/bid/<booking_id>', methods=['POST'])
@token_required
@role_required('provider')
def place_bid(booking_id):
    """Place a bid for a booking."""
    booking = Booking.get_booking_by_id(booking_id)
    
    if not booking:
        return jsonify({'message': 'Booking not found'}), 404
    
    if booking['status'] != 'pending':
        return jsonify({'message': 'Can only bid on pending bookings'}), 400
    
    data = request.get_json()
    
    if 'bid_price' not in data or 'estimated_time' not in data:
        return jsonify({'message': 'Bid price and estimated time are required'}), 400
    
    bid_id = Bid.create_bid(
        booking_id=booking_id,
        provider_id=request.user_id,
        bid_price=data['bid_price'],
        estimated_time=data['estimated_time']
    )
    
    return jsonify({
        'message': 'Bid placed successfully',
        'bid_id': bid_id
    }), 201


@matching_bp.route('/bids/<booking_id>', methods=['GET'])
@token_required
def get_booking_bids(booking_id):
    """Get all bids for a booking."""
    booking = Booking.get_booking_by_id(booking_id)
    
    if not booking:
        return jsonify({'message': 'Booking not found'}), 404
    
    # Check authorization (only customer or admin can view bids)
    if request.user_role == 'customer' and request.user_id != str(booking['user_id']):
        return jsonify({'message': 'Unauthorized'}), 403
    
    bids = Bid.get_bids_for_booking(booking_id)
    
    # Add provider info to each bid
    for bid in bids:
        provider = Provider.get_provider_by_id(str(bid['provider_id']))
        bid['_id'] = str(bid['_id'])
        bid['booking_id'] = str(bid['booking_id'])
        bid['provider_id'] = str(bid['provider_id'])
        if provider:
            bid['provider_info'] = {
                'name': provider['name'],
                'rating': provider.get('rating', 0),
                'experience_years': provider.get('experience_years', 0)
            }
    
    return jsonify({
        'booking_id': booking_id,
        'total_bids': len(bids),
        'bids': bids
    }), 200


@matching_bp.route('/select-provider/<booking_id>/<bid_id>', methods=['POST'])
@token_required
@role_required('customer')
def select_provider_from_bid(booking_id, bid_id):
    """Select a provider from bids."""
    from app import get_db
    db = get_db()
    
    booking = Booking.get_booking_by_id(booking_id)
    
    if not booking:
        return jsonify({'message': 'Booking not found'}), 404
    
    if request.user_id != str(booking['user_id']):
        return jsonify({'message': 'Unauthorized'}), 403
    
    if booking['status'] != 'pending':
        return jsonify({'message': 'Booking is no longer pending'}), 400
    
    bid = db.bids.find_one({'_id': ObjectId(bid_id)})
    
    if not bid:
        return jsonify({'message': 'Bid not found'}), 404
    
    # Assign provider
    booking = Booking.assign_provider(
        booking_id,
        str(bid['provider_id']),
        bid['bid_price']
    )
    
    booking['_id'] = str(booking['_id'])
    booking['user_id'] = str(booking['user_id'])
    booking['provider_id'] = str(booking['provider_id'])
    
    return jsonify({
        'message': 'Provider selected successfully',
        'booking': booking
    }), 200
