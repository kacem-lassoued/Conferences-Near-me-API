"""
Semantic Scholar API Service
Fetches author h-index and academic information from Semantic Scholar.
API Documentation: https://api.semanticscholar.org/
"""

import requests
from typing import Optional, Dict
import time

# Semantic Scholar API base URL
BASE_URL = "https://api.semanticscholar.org/graph/v1"

# Cache to avoid redundant API calls (in-memory, simple implementation)
_author_cache = {}


def search_author(author_name: str) -> Optional[Dict]:
    """
    Search for an author by name using Semantic Scholar API.
    
    Args:
        author_name: Full name of the author to search for
        
    Returns:
        Dictionary with author data or None if not found
        Format: {
            'authorId': str,
            'name': str,
            'hIndex': int,
            'affiliations': list
        }
    """
    # Check cache first
    if author_name in _author_cache:
        return _author_cache[author_name]
    
    try:
        # Search for author - fetch more results to find the best match
        search_url = f"{BASE_URL}/author/search"
        params = {
            'query': author_name,
            'fields': 'name,hIndex,affiliations,authorId,citationCount',
            'limit': 100  # Get top 100 results to filter (needed for common names like Andrew Ng)
        }
        
        response = requests.get(search_url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('data') and len(data['data']) > 0:
                # Filter results: Find the author with the highest h-index
                candidates = data['data']
                
                # Sort by h-index descending
                # Handle cases where hIndex might be None
                candidates.sort(key=lambda x: x.get('hIndex') or 0, reverse=True)
                
                # Pick the top candidate
                best_match = candidates[0]
                
                # Cache the result
                _author_cache[author_name] = best_match
                return best_match
        
        elif response.status_code == 429:
            # Rate limit hit, wait and retry once
            print(f"Rate limit hit, waiting 5 seconds...")
            time.sleep(5)
            return search_author(author_name)  # Retry once
        
        return None
        
    except Exception as e:
        print(f"Error searching for author '{author_name}': {e}")
        return None


def get_author_details(semantic_scholar_id: str) -> Optional[Dict]:
    """
    Get detailed author information by Semantic Scholar ID.
    
    Args:
        semantic_scholar_id: Semantic Scholar author ID
        
    Returns:
        Dictionary with author details or None if not found
    """
    try:
        # Get author details with h-index
        author_url = f"{BASE_URL}/author/{semantic_scholar_id}"
        params = {
            'fields': 'name,hIndex,affiliations,authorId'
        }
        
        response = requests.get(author_url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return {
                'authorId': data.get('authorId'),
                'name': data.get('name'),
                'hIndex': data.get('hIndex', 0),
                'affiliations': data.get('affiliations', [])
            }
        
        return None
        
    except Exception as e:
        print(f"Error getting author details for ID '{semantic_scholar_id}': {e}")
        return None


def get_author_h_index(author_name: str) -> Optional[Dict]:
    """
    Main function to get author h-index by name.
    This is the primary function used by the application.
    
    Args:
        author_name: Full name of the author
        
    Returns:
        Dictionary with author data including h-index:
        {
            'name': str,
            'h_index': int,
            'semantic_scholar_id': str,
            'affiliation': str
        }
        Returns None if author not found.
    """
    author_data = search_author(author_name)
    
    if not author_data:
        return None
    
    # Format affiliation (take first one if multiple)
    affiliations = author_data.get('affiliations', [])
    affiliation = affiliations[0] if affiliations else None
    
    return {
        'name': author_data.get('name', author_name),
        'h_index': author_data.get('hIndex', 0),
        'semantic_scholar_id': author_data.get('authorId'),
        'affiliation': affiliation
    }


def clear_cache():
    """Clear the author cache. Useful for testing or periodic refresh."""
    global _author_cache
    _author_cache = {}


def search_papers_by_conference(conference_name: str, limit: int = 5) -> list:
    """
    Search for papers associated with a specific conference/venue.
    
    Args:
        conference_name: Name of the conference (e.g. "NeurIPS", "React Conf")
        limit: Max number of papers to fetch
        
    Returns:
        List of paper dictionaries
    """
    try:
        url = f"{BASE_URL}/paper/search"
        params = {
            'query': conference_name,
            'limit': limit,
            'fields': 'title,year,venue,authors,citationCount'
        }
        
        # print(f"DEBUG: Searching papers for {conference_name}...") 
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return data.get('data', [])
        elif response.status_code == 429:
            print("Rate limit hit during paper search, waiting...")
            time.sleep(5)
            return search_papers_by_conference(conference_name, limit)
            
        return []
        
    except Exception as e:
        print(f"Error searching papers for {conference_name}: {e}")
        return []
