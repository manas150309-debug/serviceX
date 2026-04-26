import math
from app.models import Provider
from flask import current_app


def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two coordinates using Haversine formula."""
    R = 6371  # Earth's radius in kilometers
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    distance = R * c
    
    return distance


def calculate_provider_score(provider, user_location):
    """
    Calculate provider score based on:
    Score = (0.4 × Rating) − (0.3 × Distance) − (0.3 × Price)
    """
    
    # Get rating (normalized to 0-1 scale, assuming max rating is 5)
    rating_score = (provider.get('rating', 0) / 5.0) * 0.4
    
    # Calculate distance
    distance = calculate_distance(
        user_location['latitude'],
        user_location['longitude'],
        provider['location']['latitude'],
        provider['location']['longitude']
    )
    distance_score = (distance / 50) * 0.3  # Normalize distance (assuming max acceptable distance is 50km)
    
    # Get price (normalized)
    price_score = (provider.get('hourly_rate', 0) / 200) * 0.3  # Normalize price (assuming max is 200 units)
    
    # Calculate final score
    score = rating_score - distance_score - price_score
    
    return score


def find_best_providers(service_type, user_location, limit=5):
    """Find best providers for a service based on matching algorithm."""
    
    # Get all available providers for the service
    providers = Provider.get_providers_by_service(service_type)
    
    if not providers:
        return []
    
    # Score each provider
    scored_providers = []
    for provider in providers:
        if not provider.get('available', True):
            continue
        
        score = calculate_provider_score(provider, user_location)
        scored_providers.append({
            'provider': provider,
            'score': score
        })
    
    # Sort by score (highest first)
    scored_providers.sort(key=lambda x: x['score'], reverse=True)
    
    # Return top N providers
    return [item['provider'] for item in scored_providers[:limit]]


def smart_match_provider(service_type, user_location, bids):
    """
    Smart matching algorithm to select best provider from bids.
    Considers rating, distance, price, and bid amount.
    """
    
    if not bids:
        return None
    
    best_match = None
    best_score = float('-inf')
    
    for bid in bids:
        provider = Provider.get_provider_by_id(str(bid['provider_id']))
        
        if not provider:
            continue
        
        # Calculate score
        rating_component = (provider.get('rating', 0) / 5.0) * 0.4
        distance = calculate_distance(
            user_location['latitude'],
            user_location['longitude'],
            provider['location']['latitude'],
            provider['location']['longitude']
        )
        distance_component = (distance / 50) * 0.3
        
        # Price component based on bid amount
        price_component = (bid['bid_price'] / 200) * 0.3
        
        score = rating_component - distance_component - price_component
        
        if score > best_score:
            best_score = score
            best_match = provider
    
    return best_match
