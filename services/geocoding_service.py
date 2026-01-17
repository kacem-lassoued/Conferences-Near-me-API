"""
Geocoding Service - Converts location names to coordinates
Uses Nominatim (OpenStreetMap) for free geocoding
"""

import requests
import time
from typing import Optional, Dict, Tuple
from functools import lru_cache

NOMINATIM_BASE_URL = "https://nominatim.openstreetmap.org/search"
USER_AGENT = "ConferenceDiscoveryAPI/1.0"  # Required by Nominatim

# Cache to avoid redundant API calls
_geocoding_cache = {}


@lru_cache(maxsize=1000)
def geocode_location(city: str = None, country: str = None, location_string: str = None) -> Optional[Dict]:
    """
    Geocode a location to get latitude and longitude.
    
    Args:
        city: City name
        country: Country name
        location_string: Full location string (alternative to city+country)
        
    Returns:
        Dictionary with 'latitude' and 'longitude', or None if not found
    """
    # Build query
    if location_string:
        query = location_string
    elif city and country:
        query = f"{city}, {country}"
    elif city:
        query = city
    elif country:
        query = country
    else:
        return None
    
    # Check cache
    cache_key = query.lower().strip()
    if cache_key in _geocoding_cache:
        return _geocoding_cache[cache_key]
    
    try:
        params = {
            'q': query,
            'format': 'json',
            'limit': 1,
            'addressdetails': 1
        }
        
        headers = {
            'User-Agent': USER_AGENT
        }
        
        response = requests.get(NOMINATIM_BASE_URL, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                result = data[0]
                lat = float(result.get('lat', 0))
                lon = float(result.get('lon', 0))
                
                geocode_result = {
                    'latitude': lat,
                    'longitude': lon,
                    'display_name': result.get('display_name', query),
                    'city': result.get('address', {}).get('city') or result.get('address', {}).get('town'),
                    'country': result.get('address', {}).get('country')
                }
                
                # Cache the result
                _geocoding_cache[cache_key] = geocode_result
                
                # Be nice to the API - rate limiting
                time.sleep(1)
                
                return geocode_result
        
        return None
        
    except Exception as e:
        print(f"Error geocoding '{query}': {e}")
        return None


def reverse_geocode(latitude: float, longitude: float) -> Optional[Dict]:
    """
    Reverse geocode coordinates to get location name.
    
    Args:
        latitude: Latitude coordinate
        longitude: Longitude coordinate
        
    Returns:
        Dictionary with location information
    """
    try:
        url = "https://nominatim.openstreetmap.org/reverse"
        params = {
            'lat': latitude,
            'lon': longitude,
            'format': 'json',
            'addressdetails': 1
        }
        
        headers = {
            'User-Agent': USER_AGENT
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            address = data.get('address', {})
            
            return {
                'display_name': data.get('display_name', ''),
                'city': address.get('city') or address.get('town') or address.get('village'),
                'country': address.get('country'),
                'latitude': latitude,
                'longitude': longitude
            }
        
        return None
        
    except Exception as e:
        print(f"Error reverse geocoding ({latitude}, {longitude}): {e}")
        return None


def clear_cache():
    """Clear the geocoding cache."""
    global _geocoding_cache
    _geocoding_cache = {}
    geocode_location.cache_clear()








