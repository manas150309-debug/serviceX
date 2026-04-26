from flask import Blueprint, request, jsonify
from app.models import Provider, Booking
from app.utils import token_required, role_required

provider_bp = Blueprint('provider', __name__, url_prefix='/api/providers')


@provider_bp.route('/<provider_id>', methods=['GET'])
def get_provider(provider_id):
    """Get provider profile."""
    provider = Provider.get_provider_by_id(provider_id)
    
    if not provider:
        return jsonify({'message': 'Provider not found'}), 404
    
    # Remove sensitive data
    provider.pop('password', None)
    provider['_id'] = str(provider['_id'])
    
    return jsonify(provider), 200


@provider_bp.route('/<provider_id>', methods=['PUT'])
@token_required
@role_required('provider')
def update_provider(provider_id):
    """Update provider profile."""
    if request.user_id != provider_id:
        return jsonify({'message': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    # Don't allow updating sensitive fields
    data.pop('password', None)
    data.pop('role', None)
    data.pop('email', None)
    data.pop('is_verified', None)
    
    provider = Provider.update_provider(provider_id, data)
    
    if not provider:
        return jsonify({'message': 'Provider not found'}), 404
    
    provider.pop('password', None)
    provider['_id'] = str(provider['_id'])
    
    return jsonify({
        'message': 'Provider updated successfully',
        'provider': provider
    }), 200


@provider_bp.route('/<provider_id>/availability', methods=['PUT'])
@token_required
@role_required('provider')
def update_availability(provider_id):
    """Update provider availability status."""
    if request.user_id != provider_id:
        return jsonify({'message': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    if 'available' not in data:
        return jsonify({'message': 'Available field is required'}), 400
    
    provider = Provider.update_provider(provider_id, {'available': data['available']})
    
    if not provider:
        return jsonify({'message': 'Provider not found'}), 404
    
    return jsonify({
        'message': 'Availability updated successfully',
        'available': provider['available']
    }), 200


@provider_bp.route('/<provider_id>/jobs', methods=['GET'])
@token_required
def get_provider_jobs(provider_id):
    """Get provider's job history."""
    if request.user_role == 'provider' and request.user_id != provider_id:
        return jsonify({'message': 'Unauthorized'}), 403
    
    jobs = Booking.get_provider_bookings(provider_id)
    
    # Convert ObjectIds to strings
    for job in jobs:
        job['_id'] = str(job['_id'])
        job['user_id'] = str(job['user_id'])
        job['provider_id'] = str(job['provider_id'])
        if job.get('assigned_provider'):
            job['assigned_provider'] = str(job['assigned_provider'])
    
    return jsonify({
        'total': len(jobs),
        'jobs': jobs
    }), 200


@provider_bp.route('/by-service/<service_type>', methods=['GET'])
def get_providers_by_service(service_type):
    """Get all providers for a service type."""
    latitude = request.args.get('latitude', type=float)
    longitude = request.args.get('longitude', type=float)
    
    providers = Provider.get_providers_by_service(service_type)
    
    # Remove sensitive data
    for provider in providers:
        provider.pop('password', None)
        provider['_id'] = str(provider['_id'])
    
    return jsonify({
        'service_type': service_type,
        'total': len(providers),
        'providers': providers
    }), 200
