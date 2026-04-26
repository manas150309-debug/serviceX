from flask import Blueprint, request, jsonify
from app.models import User, Provider
from app.utils import generate_token

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/register/customer', methods=['POST'])
def register_customer():
    """Register a new customer."""
    data = request.get_json()
    
    required_fields = ['name', 'email', 'password', 'phone', 'location']
    if not all(field in data for field in required_fields):
        return jsonify({'message': 'Missing required fields'}), 400
    
    # Check if location has required fields
    if 'latitude' not in data['location'] or 'longitude' not in data['location']:
        return jsonify({'message': 'Location must include latitude and longitude'}), 400
    
    user_id = User.create_user(
        name=data['name'],
        email=data['email'],
        password=data['password'],
        phone=data['phone'],
        location=data['location']
    )
    
    if not user_id:
        return jsonify({'message': 'User already exists'}), 409
    
    token = generate_token(user_id, 'customer')
    
    return jsonify({
        'message': 'Customer registered successfully',
        'user_id': user_id,
        'token': token
    }), 201


@auth_bp.route('/register/provider', methods=['POST'])
def register_provider():
    """Register a new service provider."""
    data = request.get_json()
    
    required_fields = ['name', 'email', 'password', 'phone', 'service_type', 'location', 'experience_years', 'hourly_rate']
    if not all(field in data for field in required_fields):
        return jsonify({'message': 'Missing required fields'}), 400
    
    # Check if location has required fields
    if 'latitude' not in data['location'] or 'longitude' not in data['location']:
        return jsonify({'message': 'Location must include latitude and longitude'}), 400
    
    provider_id = Provider.create_provider(
        name=data['name'],
        email=data['email'],
        password=data['password'],
        phone=data['phone'],
        service_type=data['service_type'],
        location=data['location'],
        experience_years=data['experience_years'],
        hourly_rate=data['hourly_rate']
    )
    
    if not provider_id:
        return jsonify({'message': 'Provider already exists'}), 409
    
    token = generate_token(provider_id, 'provider')
    
    return jsonify({
        'message': 'Provider registered successfully',
        'provider_id': provider_id,
        'token': token
    }), 201


@auth_bp.route('/login/customer', methods=['POST'])
def login_customer():
    """Login customer."""
    data = request.get_json()
    
    if 'email' not in data or 'password' not in data:
        return jsonify({'message': 'Email and password required'}), 400
    
    user = User.get_user_by_email(data['email'])
    
    if not user:
        return jsonify({'message': 'Invalid credentials'}), 401
    
    if not User.verify_password(user['password'], data['password']):
        return jsonify({'message': 'Invalid credentials'}), 401
    
    token = generate_token(str(user['_id']), 'customer')
    
    return jsonify({
        'message': 'Login successful',
        'user_id': str(user['_id']),
        'token': token
    }), 200


@auth_bp.route('/login/provider', methods=['POST'])
def login_provider():
    """Login provider."""
    data = request.get_json()
    
    if 'email' not in data or 'password' not in data:
        return jsonify({'message': 'Email and password required'}), 400
    
    provider = Provider.get_provider_by_email(data['email'])
    
    if not provider:
        return jsonify({'message': 'Invalid credentials'}), 401
    
    if not Provider.verify_password(provider['password'], data['password']):
        return jsonify({'message': 'Invalid credentials'}), 401
    
    token = generate_token(str(provider['_id']), 'provider')
    
    return jsonify({
        'message': 'Login successful',
        'provider_id': str(provider['_id']),
        'token': token
    }), 200
