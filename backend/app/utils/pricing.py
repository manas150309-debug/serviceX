from flask import current_app
from app import get_db
from datetime import datetime


class DynamicPricingEngine:
    """Dynamic pricing engine based on demand and supply."""
    
    @staticmethod
    def calculate_demand_score(service_type, time_window_hours=2):
        """
        Calculate demand score for a service type.
        Returns a value between 0 and 1, where 1 is maximum demand.
        """
        db = get_db()
        
        # Count active bookings for the service in the time window
        now = datetime.utcnow()
        recent_bookings = db.bookings.count_documents({
            'service_type': service_type,
            'status': {'$in': ['pending', 'accepted', 'in_progress']},
            'created_at': {'$gte': now - timedelta(hours=time_window_hours)}
        })
        
        # Normalize demand (assuming 50 bookings = max demand = 1.0)
        demand_score = min(recent_bookings / 50, 1.0)
        
        return demand_score
    
    @staticmethod
    def calculate_supply_score(service_type, time_window_hours=2):
        """
        Calculate supply score for a service type.
        Returns a value between 0 and 1, where 1 is maximum supply.
        """
        db = get_db()
        
        # Count available providers for the service
        available_providers = db.providers.count_documents({
            'service_type': service_type,
            'available': True,
            'is_active': True
        })
        
        # Normalize supply (assuming 100 providers = max supply = 1.0)
        supply_score = min(available_providers / 100, 1.0)
        
        return supply_score
    
    @staticmethod
    def calculate_dynamic_price(base_price, service_type):
        """
        Calculate dynamic price using: Price = Base Price × (Demand / Supply)
        """
        demand_score = DynamicPricingEngine.calculate_demand_score(service_type)
        supply_score = DynamicPricingEngine.calculate_supply_score(service_type)
        
        # Avoid division by zero
        if supply_score == 0:
            supply_score = 0.1
        
        # Calculate multiplier
        multiplier = max(demand_score / supply_score, 0.5)  # Min multiplier 0.5x
        multiplier = min(multiplier, 2.0)  # Max multiplier 2.0x
        
        dynamic_price = base_price * multiplier
        
        return round(dynamic_price, 2)
    
    @staticmethod
    def get_pricing_metrics(service_type):
        """Get detailed pricing metrics for a service."""
        demand = DynamicPricingEngine.calculate_demand_score(service_type)
        supply = DynamicPricingEngine.calculate_supply_score(service_type)
        
        base_price = current_app.config['BASE_PRICE']
        dynamic_price = DynamicPricingEngine.calculate_dynamic_price(base_price, service_type)
        
        return {
            'service_type': service_type,
            'base_price': base_price,
            'demand_score': round(demand, 2),
            'supply_score': round(supply, 2),
            'dynamic_price': dynamic_price,
            'multiplier': round(dynamic_price / base_price, 2)
        }


from datetime import timedelta
