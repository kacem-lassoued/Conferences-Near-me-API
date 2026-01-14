"""
Semantic Scholar API Service
Fetches author h-index and academic information from Semantic Scholar.
API Documentation: https://api.semanticscholar.org/
"""

import requests
from typing import Optional, Dict, List
import time
from difflib import SequenceMatcher
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Semantic Scholar API base URL
BASE_URL = "https://api.semanticscholar.org/graph/v1"

# Cache to avoid redundant API calls (in-memory, simple implementation)
_author_cache = {}
_conference_cache = {}
_papers_cache = {}

# Rate limiting
MAX_RETRIES = 3
RETRY_DELAY = 2  # Base delay, exponential backoff applied


def _name_similarity(name1: str, name2: str) -> float:
    """
    Calculate similarity between two author names (0-1).
    Uses SequenceMatcher for fuzzy matching.
    """
    if not name1 or not name2:
        return 0.0
    return SequenceMatcher(None, name1.lower(), name2.lower()).ratio()


def _exponential_backoff(attempt: int) -> float:
    """Calculate exponential backoff delay in seconds."""
    return min(RETRY_DELAY * (2 ** attempt), 30)  # Cap at 30 seconds


def search_author(author_name: str) -> Optional[Dict]:
    """
    Search for an author by name using Semantic Scholar API.
    Implements fuzzy matching to find the best candidate.
    
    Args:
        author_name: Full name of the author to search for
        
    Returns:
        Dictionary with author data or None if not found
        Format: {
            'authorId': str,
            'name': str,
            'hIndex': int,
            'affiliations': list,
            'citationCount': int,
            'similarity': float (0-1, how well it matched)
        }
    """
    # Check cache first
    if author_name in _author_cache:
        cached_result = _author_cache[author_name]
        if cached_result:
            logger.debug(f"Cache hit for author: {author_name}")
        return cached_result
    
    try:
        # Search for author - fetch more results to find the best match
        search_url = f"{BASE_URL}/author/search"
        params = {
            'query': author_name,
            'fields': 'name,hIndex,affiliations,authorId,citationCount',
            'limit': 20  # Reduced from 100 for better performance
        }
        
        for attempt in range(MAX_RETRIES):
            try:
                response = requests.get(search_url, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get('data') and len(data['data']) > 0:
                        candidates = data['data']
                        
                        # Score candidates by name similarity + h-index
                        scored_candidates = []
                        for candidate in candidates:
                            similarity = _name_similarity(author_name, candidate.get('name', ''))
                            h_index = candidate.get('hIndex', 0) or 0
                            # Weighted score: 70% name match, 30% h-index (normalized)
                            score = (similarity * 0.7) + (min(h_index / 100, 1.0) * 0.3)
                            scored_candidates.append({
                                'score': score,
                                'similarity': similarity,
                                'data': candidate
                            })
                        
                        # Sort by score descending
                        scored_candidates.sort(key=lambda x: x['score'], reverse=True)
                        best_match = scored_candidates[0]['data']
                        
                        result = {
                            'authorId': best_match.get('authorId'),
                            'name': best_match.get('name', author_name),
                            'hIndex': best_match.get('hIndex', 0),
                            'affiliations': best_match.get('affiliations', []),
                            'citationCount': best_match.get('citationCount', 0),
                            'similarity': scored_candidates[0]['similarity']
                        }
                        
                        # Cache the result
                        _author_cache[author_name] = result
                        logger.info(f"Found author: {best_match.get('name')} (similarity: {scored_candidates[0]['similarity']:.2%})")
                        return result
                    else:
                        # No results found
                        _author_cache[author_name] = None
                        logger.warning(f"No author found for: {author_name}")
                        return None
                
                elif response.status_code == 429:
                    # Rate limit hit
                    if attempt < MAX_RETRIES - 1:
                        wait_time = _exponential_backoff(attempt)
                        logger.warning(f"Rate limit hit, retrying in {wait_time}s (attempt {attempt + 1}/{MAX_RETRIES})")
                        time.sleep(wait_time)
                        continue
                    else:
                        logger.error("Rate limit hit, max retries exceeded")
                        return None
                else:
                    logger.error(f"API error {response.status_code}: {response.text}")
                    return None
                    
            except requests.Timeout:
                if attempt < MAX_RETRIES - 1:
                    wait_time = _exponential_backoff(attempt)
                    logger.warning(f"Request timeout, retrying in {wait_time}s (attempt {attempt + 1}/{MAX_RETRIES})")
                    time.sleep(wait_time)
                else:
                    logger.error("Request timeout, max retries exceeded")
                    return None
        
        return None
        
    except Exception as e:
        logger.error(f"Error searching for author '{author_name}': {e}", exc_info=True)
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
            'affiliation': str,
            'citation_count': int,
            'match_confidence': float (0-1)
        }
        Returns None if author not found.
    """
    try:
        author_data = search_author(author_name)
        
        if not author_data:
            logger.info(f"Could not find author: {author_name}")
            return None
        
        # Format affiliation (take first one if multiple)
        affiliations = author_data.get('affiliations', [])
        affiliation = affiliations[0] if affiliations else None
        
        result = {
            'name': author_data.get('name', author_name),
            'h_index': author_data.get('hIndex', 0) or 0,
            'semantic_scholar_id': author_data.get('authorId'),
            'affiliation': affiliation,
            'citation_count': author_data.get('citationCount', 0) or 0,
            'match_confidence': author_data.get('similarity', 0.8)  # Default to 0.8 if not set
        }
        
        logger.debug(f"Author data enriched: {result['name']} (confidence: {result['match_confidence']:.2%})")
        return result
        
    except Exception as e:
        logger.error(f"Error in get_author_h_index for '{author_name}': {e}", exc_info=True)
        return None


def search_papers_by_conference(conference_name: str, limit: int = 5) -> List[Dict]:
    """
    Search for papers associated with a specific conference/venue.
    Enhanced with better error handling and caching.
    
    Args:
        conference_name: Name of the conference (e.g. "NeurIPS", "React Conf")
        limit: Max number of papers to fetch
        
    Returns:
        List of paper dictionaries with author and citation info
    """
    # Check cache first
    cache_key = f"{conference_name}:{limit}"
    if cache_key in _papers_cache:
        logger.debug(f"Cache hit for conference papers: {conference_name}")
        return _papers_cache[cache_key]
    
    try:
        url = f"{BASE_URL}/paper/search"
        params = {
            'query': conference_name,
            'limit': min(limit, 10),  # Cap at 10 for performance
            'fields': 'title,year,venue,authors,citationCount,abstract,paperId'
        }
        
        for attempt in range(MAX_RETRIES):
            try:
                response = requests.get(url, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    papers = data.get('data', [])
                    
                    # Process papers to ensure clean data
                    processed_papers = []
                    for paper in papers:
                        processed_paper = {
                            'title': paper.get('title', 'Unknown Title'),
                            'year': paper.get('year'),
                            'venue': paper.get('venue'),
                            'authors': [
                                {
                                    'name': auth.get('name', 'Unknown Author'),
                                    'authorId': auth.get('authorId')
                                }
                                for auth in paper.get('authors', [])
                            ],
                            'citationCount': paper.get('citationCount', 0) or 0,
                            'abstract': paper.get('abstract', 'No abstract available'),
                            'paperId': paper.get('paperId')
                        }
                        processed_papers.append(processed_paper)
                    
                    # Cache the result
                    _papers_cache[cache_key] = processed_papers
                    logger.info(f"Found {len(processed_papers)} papers for conference: {conference_name}")
                    return processed_papers
                
                elif response.status_code == 429:
                    if attempt < MAX_RETRIES - 1:
                        wait_time = _exponential_backoff(attempt)
                        logger.warning(f"Rate limit hit on paper search, retrying in {wait_time}s")
                        time.sleep(wait_time)
                        continue
                    else:
                        logger.error("Rate limit hit on paper search, max retries exceeded")
                        return []
                else:
                    logger.error(f"API error {response.status_code} on paper search")
                    return []
                    
            except requests.Timeout:
                if attempt < MAX_RETRIES - 1:
                    wait_time = _exponential_backoff(attempt)
                    logger.warning(f"Timeout on paper search, retrying in {wait_time}s")
                    time.sleep(wait_time)
                else:
                    logger.error("Timeout on paper search, max retries exceeded")
                    return []
        
        return []
        
    except Exception as e:
        logger.error(f"Error searching papers for {conference_name}: {e}", exc_info=True)
        return []


def search_conference_info(conference_name: str) -> Optional[Dict]:
    """
    Get information about a conference by searching for papers with that venue.
    Useful for retrieving conference metadata.
    
    Args:
        conference_name: Name of the conference
        
    Returns:
        Dictionary with conference info including top papers
    """
    # Check cache first
    if conference_name in _conference_cache:
        logger.debug(f"Cache hit for conference info: {conference_name}")
        return _conference_cache[conference_name]
    
    try:
        papers = search_papers_by_conference(conference_name, limit=10)
        
        if not papers:
            logger.warning(f"No papers found for conference: {conference_name}")
            return None
        
        # Aggregate conference info from papers
        all_authors = set()
        total_citations = 0
        years = []
        
        for paper in papers:
            total_citations += paper.get('citationCount', 0)
            if paper.get('year'):
                years.append(paper['year'])
            for author in paper.get('authors', []):
                all_authors.add(author.get('name'))
        
        conference_info = {
            'name': conference_name,
            'papers_found': len(papers),
            'top_papers': papers[:5],
            'unique_authors': len(all_authors),
            'total_citations': total_citations,
            'years_active': sorted(set(years)) if years else [],
            'avg_citations_per_paper': total_citations / len(papers) if papers else 0
        }
        
        # Cache the result
        _conference_cache[conference_name] = conference_info
        logger.info(f"Conference info aggregated: {conference_name}")
        return conference_info
        
    except Exception as e:
        logger.error(f"Error getting conference info for '{conference_name}': {e}", exc_info=True)
        return None


def classify_conference(conference_name: str, papers_data: Optional[List[Dict]] = None) -> Optional[Dict]:
    """
    Classify a conference based on its papers and metadata.
    Uses research field analysis from paper titles and venue information.
    
    Args:
        conference_name: Name of the conference
        papers_data: Optional list of papers with titles and authors
        
    Returns:
        Dictionary with classification:
        {
            'primary': str (main field: e.g., "Machine Learning", "Software Engineering"),
            'secondary': [str] (related fields),
            'confidence': float (0-1, how confident the classification is),
            'reasoning': str (explanation of the classification)
        }
        Returns None if classification cannot be determined.
    """
    try:
        # Common conference field mappings
        FIELD_KEYWORDS = {
            'Machine Learning': ['machine learning', 'deep learning', 'neural network', 'neural', 'AI', 
                                'artificial intelligence', 'learning', 'algorithm', 'model', 'prediction'],
            'Natural Language Processing': ['nlp', 'language', 'text', 'nlp', 'translation', 'semantic', 
                                          'natural language', 'linguistic', 'corpus'],
            'Computer Vision': ['vision', 'image', 'visual', 'video', 'detection', 'recognition', 'segmentation',
                              'convolutional', 'cnn', 'object', 'scene'],
            'Robotics': ['robot', 'robotic', 'autonomous', 'control', 'manipulation', 'motion', 'navigation'],
            'Human-Computer Interaction': ['hci', 'interaction', 'interface', 'user experience', 'ux', 'ui',
                                          'usability', 'user study', 'interaction design'],
            'Software Engineering': ['software', 'testing', 'development', 'programming', 'architecture',
                                    'code', 'refactoring', 'debugging', 'devops', 'agile'],
            'Security': ['security', 'cryptography', 'encryption', 'malware', 'attack', 'vulnerability',
                        'privacy', 'authentication', 'authorization'],
            'Database Systems': ['database', 'sql', 'query', 'transaction', 'data management', 'indexing',
                               'distributed database', 'nosql'],
            'Distributed Systems': ['distributed', 'concurrency', 'parallel', 'cluster', 'consensus',
                                   'byzantine', 'replication', 'blockchain'],
            'Web Technology': ['web', 'http', 'browser', 'javascript', 'html', 'css', 'web framework',
                              'web service', 'api', 'rest'],
            'Bioinformatics': ['bioinformatics', 'genetics', 'protein', 'sequence', 'biology', 'dna',
                              'genomics', 'computational biology', 'medical'],
            'Data Science': ['data', 'analytics', 'big data', 'data mining', 'visualization', 'statistics',
                            'data processing', 'data warehouse'],
            'Theory': ['theory', 'complexity', 'algorithm', 'formal', 'proof', 'computational complexity',
                      'decidability', 'p vs np']
        }
        
        # Prepare text to analyze
        analysis_text = f"{conference_name} ".lower()
        
        # Add paper titles if provided
        if papers_data:
            for paper in papers_data[:10]:  # Analyze first 10 papers
                if 'title' in paper:
                    analysis_text += f" {paper['title']}"
        
        analysis_text = analysis_text.lower()
        
        # Score each field based on keyword matches
        field_scores = {}
        total_matches = 0
        
        for field, keywords in FIELD_KEYWORDS.items():
            score = 0
            matches = 0
            for keyword in keywords:
                # Count occurrences of keyword
                count = analysis_text.count(keyword)
                if count > 0:
                    matches += count
                    score += count
            
            if score > 0:
                field_scores[field] = {
                    'score': score,
                    'matches': matches
                }
                total_matches += matches
        
        if not field_scores:
            logger.warning(f"No field keywords matched for conference: {conference_name}")
            return None
        
        # Sort by score
        sorted_fields = sorted(field_scores.items(), key=lambda x: x[1]['score'], reverse=True)
        
        # Get top field (primary) and secondary fields
        primary_field = sorted_fields[0][0]
        primary_score = sorted_fields[0][1]['score']
        secondary_fields = [field for field, _ in sorted_fields[1:4]]  # Top 3 secondary
        
        # Calculate confidence (0-1)
        # Higher confidence if primary field has significantly more matches than others
        confidence = min(primary_score / max(total_matches, 1), 1.0)
        
        # If there are secondary fields, adjust confidence
        if sorted_fields[1:]:
            second_score = sorted_fields[1][1]['score']
            # Reduce confidence if second place is close to first
            if second_score > 0:
                score_ratio = primary_score / (second_score + 1)
                confidence = min(confidence * (score_ratio / 2), 1.0)
        
        reasoning = f"Classified based on keyword analysis of conference name and paper titles. " \
                   f"Primary field matches: {sorted_fields[0][1]['matches']} occurrences"
        
        result = {
            'primary': primary_field,
            'secondary': secondary_fields,
            'confidence': round(confidence, 2),
            'reasoning': reasoning
        }
        
        logger.info(f"Conference '{conference_name}' classified as: {primary_field} (confidence: {confidence:.2%})")
        return result
        
    except Exception as e:
        logger.error(f"Error classifying conference '{conference_name}': {e}", exc_info=True)
        return None


def clear_cache():
    """
    Clear all caches. Useful for testing or periodic refresh.
    Clears author cache, papers cache, and conference info cache.
    """
    global _author_cache, _papers_cache, _conference_cache
    _author_cache = {}
    _papers_cache = {}
    _conference_cache = {}
    logger.info("All caches cleared")
