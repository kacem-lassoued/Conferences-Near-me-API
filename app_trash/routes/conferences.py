from flask import Blueprint, request, jsonify
from app.models.conference import Conference, Theme, Ranking, ConferenceEdition
from app.extensions import db
from sqlalchemy import or_, and_
import logging

# Refactored for beginner friendliness: Added step-by-step comments.

conferences_bp = Blueprint('conferences', __name__)
logger = logging.getLogger(__name__)

@conferences_bp.route('/', methods=['GET'])
def get_conferences():
    """
    Search and List Conferences
    ---
    tags:
      - Conferences
    parameters:
      - name: q
        in: query
        type: string
        description: Keyword to search for (name or acronym)
      - name: country
        in: query
        type: string
        description: Filter by country
      - name: theme
        in: query
        type: string
        description: Filter by theme name
      - name: year
        in: query
        type: integer
        description: Filter by year
      - name: page
        in: query
        type: integer
        default: 1
        description: Page number
    responses:
      200:
        description: List of conferences
    """
    try:
        # --- Pagination Setup ---
        # Get 'page' from URL query (e.g., ?page=2), default to 1
        page = request.args.get('page', 1, type=int)
        per_page = 20 # Show 20 results per page
        
        # Start building the database query
        # We start with "Select all conferences", then add filters one by one
        query = Conference.query
        
        # --- Filter: Keyword Search ---
        # Get 'q' parameter (e.g., ?q=PyCon)
        keyword = request.args.get('q')
        if keyword:
            # Create a search pattern: %keyword% matches anything containing the keyword
            search_pattern = f"%{keyword}%"
            # Filter where Name OR Acronym matches the pattern
            # ilike means "case-insensitive like" (ignores upper/lowercase)
            query = query.filter(
                or_(
                    Conference.name.ilike(search_pattern), 
                    Conference.acronym.ilike(search_pattern)
                )
            )
        
        # --- Filter: Country ---
        country = request.args.get('country')
        if country:
            query = query.filter(Conference.country.ilike(country))
        
        # --- Filter: Theme ---
        # This is more complex because Theme is a separate table linked to Conference
        theme_name = request.args.get('theme')
        if theme_name:
            # We "join" the tables so we can filter by Theme name
            query = query.outerjoin(Conference.themes).filter(Theme.name.ilike(theme_name))
        
        # --- Filter: Year ---
        # Year is in the ConferenceEdition table (since a conference happens every year)
        year = request.args.get('year', type=int)
        if year:
            # Join with editions table and check the year
            query = query.outerjoin(Conference.editions).filter(ConferenceEdition.year == year)
        
        # --- Execute Query ---
        # Order results by start date (newest first)
        ordered_query = query.order_by(Conference.start_date.desc())
        
        # Run the query and paginate results
        # error_out=False means "don't crash if page number is too high, just return empty list"
        pagination = ordered_query.paginate(page=page, per_page=per_page, error_out=False)
        
        # Convert the complex database objects into simple dictionaries (JSON-ready)
        conference_list = []
        for conference in pagination.items:
            conference_list.append(conference.to_dict())
            
        # Return the data along with pagination info so the frontend knows how many pages exist
        return jsonify({
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page,
            'data': conference_list
        })
    
    except ValueError as e:
        # Handle cases where user sends text where a number was expected
        logger.error(f'Invalid query parameter: {str(e)}')
        return jsonify({'error': f'Invalid query parameters: {str(e)}'}), 400
    except Exception as e:
        logger.error(f'Error fetching conferences: {str(e)}')
        return jsonify({'error': 'Server error'}), 500

@conferences_bp.route('/<int:id>', methods=['GET'])
def get_conference_detail(id):
    """
    Get Conference Detail
    ---
    tags:
      - Conferences
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: Conference ID
    responses:
      200:
        description: Conference details
      404:
        description: Conference not found
    """
    try:
        # Try to find the conference. If not found, automatically return 404 error.
        conf = Conference.query.get_or_404(id)
        
        # Convert base info to dictionary
        data = conf.to_dict()
        
        # Add related data (One-to-Many relationships)
        
        # 1. Editions (Past/Future instances)
        editions_list = []
        for edition in conf.editions:
            editions_list.append(edition.to_dict())
        data['editions'] = editions_list
        
        # 2. Papers (published research)
        papers_list = []
        for paper in conf.papers:
            papers_list.append(paper.to_dict())
        data['papers'] = papers_list
            
        # 3. Workshops
        workshops_list = []
        for workshop in conf.workshops:
            workshops_list.append(workshop.to_dict())
        data['workshops'] = workshops_list
        
        return jsonify(data)
        
    except Exception as e:
        logger.error(f'Error fetching conference {id}: {str(e)}')
        return jsonify({'error': 'Server error'}), 500

@conferences_bp.route('/map', methods=['GET'])
def get_map_data():
    """
    Get Map Data (GeoJSON)
    ---
    tags:
      - Conferences
    parameters:
      - name: min_lat
        in: query
        type: number
      - name: max_lat
        in: query
        type: number
      - name: min_lng
        in: query
        type: number
      - name: max_lng
        in: query
        type: number
      - name: year
        in: query
        type: integer
    responses:
      200:
        description: GeoJSON FeatureCollection
    """
    try:
        # Start looking for conferences that HAVE a location (latitude/longitude)
        # We can't map things that don't have coordinates!
        query = Conference.query.filter(
            Conference.latitude != None, 
            Conference.longitude != None
        )
        
        # --- Bounding Box Filter ---
        # A "bounding box" is the current view of the map (Top, Bottom, Left, Right edges)
        # We only want to send data for what the user is currently looking at.
        min_lat = request.args.get('min_lat', type=float)
        max_lat = request.args.get('max_lat', type=float)
        min_lng = request.args.get('min_lng', type=float)
        max_lng = request.args.get('max_lng', type=float)
        
        # Check if ALL 4 coordinates were sent
        has_bounds = (min_lat is not None and max_lat is not None and 
                      min_lng is not None and max_lng is not None)
                      
        if has_bounds:
            # Add filters to only get conferences INSIDE the box
            query = query.filter(
                Conference.latitude >= min_lat,
                Conference.latitude <= max_lat,
                Conference.longitude >= min_lng,
                Conference.longitude <= max_lng
            )
        
        # --- Year Filter ---
        year = request.args.get('year', type=int)
        if year:
            query = query.outerjoin(Conference.editions).filter(ConferenceEdition.year == year)
        
        # Fetch all matching conferences
        conferences = query.all()
        
        # Convert to GeoJSON format
        # GeoJSON is a standard format for map data
        features = []
        for c in conferences:
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [c.longitude, c.latitude] # Note: GeoJSON uses [Longitude, Latitude] order
                },
                "properties": {
                    "id": c.id,
                    "name": c.name,
                    "city": c.city,
                    "country": c.country,
                    "status": c.status
                }
            })
            
        return jsonify({
            "type": "FeatureCollection",
            "features": features
        })
    
    except ValueError as e:
        logger.error(f'Invalid coordinate parameter: {str(e)}')
        return jsonify({'error': 'Invalid coordinate parameters'}), 400
    except Exception as e:
        logger.error(f'Error fetching map data: {str(e)}')
        return jsonify({'error': 'Server error'}), 500
