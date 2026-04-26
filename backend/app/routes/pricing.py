from flask import Blueprint, request, jsonify
from app.utils.pricing import DynamicPricingEngine

pricing_bp = Blueprint('pricing', __name__, url_prefix='/api/pricing')


@pricing_bp.route('/calculate', methods=['POST'])
def calculate_price():
    """Calculate dynamic price for a service."""
    data = request.get_json()
    
    if 'service_type' not in data:
        return jsonify({'message': 'Service type is required'}), 400
    
    service_type = data['service_type']
    base_price = data.get('base_price', None)
    
    from flask import current_app
    if not base_price:
        base_price = current_app.config['BASE_PRICE']
    
    dynamic_price = DynamicPricingEngine.calculate_dynamic_price(base_price, service_type)
    
    return jsonify({
        'service_type': service_type,
        'base_price': base_price,
        'dynamic_price': dynamic_price
    }), 200


@pricing_bp.route('/metrics/<service_type>', methods=['GET'])
def get_pricing_metrics(service_type):
    """Get detailed pricing metrics."""
    metrics = DynamicPricingEngine.get_pricing_metrics(service_type)
    
    return jsonify(metrics), 200
