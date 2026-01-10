import requests
import datetime
import time
from app import app
from db import db
from models import Conference, ConferenceEdition, Paper, Author
from sqlalchemy import func
from services import scholar_service

def seed_data():
    with app.app_context():
        db.create_all()
        print("Database initialized.")
        
        # Incremental Seeding: Do NOT delete existing data
        print("Starting incremental seed...")
        
        seed_tech_conferences()
        fix_coordinates()
        seed_academic_papers()

def seed_tech_conferences():
    url = "https://developers.events/all-events.json"
    print(f"Fetching conferences from {url}...")
    
    try:
        resp = requests.get(url, timeout=30)
        if resp.status_code != 200:
            print(f"Failed to fetch data: {resp.status_code}")
            return
            
        events = resp.json()
        print(f"Found {len(events)} events. Processing...")
        
        count = 0
        new_count = 0
        
        for event in events:
            # Basic validation
            if not event.get('name'):
                continue
            
            # Check if conference already exists
            existing_conf = Conference.query.filter_by(name=event.get('name')).first()
            if existing_conf:
                # Skip if exists (or update if you wanted to sync changes)
                continue

            # Create Conference
            conf = Conference(
                name=event.get('name'),
                website=event.get('hyperlink'),
                city=event.get('city'),
                country=event.get('country'),
                location=event.get('location'),
                source='developers.events'
            )
            
            # Handle Dates (timestamps in ms)
            dates = event.get('date', [])
            if dates and len(dates) >= 1:
                try:
                    start_ts = dates[0] / 1000
                    conf.start_date = datetime.date.fromtimestamp(start_ts)
                    
                    if len(dates) >= 2:
                        end_ts = dates[-1] / 1000
                        conf.end_date = datetime.date.fromtimestamp(end_ts)
                    else:
                        conf.end_date = conf.start_date
                except Exception:
                    pass

            db.session.add(conf)
            db.session.flush() # flush to get the ID
            
            # Create Edition
            if conf.start_date:
                edition = ConferenceEdition(
                    conference_id=conf.id,
                    year=conf.start_date.year,
                    venue=conf.location,
                    acceptance_rate=None 
                )
                db.session.add(edition)
            
            new_count += 1
            count += 1
            if count % 100 == 0:
                print(f"Processed {count} items...")
                db.session.commit()
                
        db.session.commit()
        print(f"Seeding events complete. Added {new_count} new conferences.")
        
    except Exception as e:
        print(f"Error seeding data: {e}")
        db.session.rollback()

def seed_academic_papers():
    """
    Enrich existing conferences with academic papers from Semantic Scholar.
    """
    print("Starting academic paper enrichment...")
    
    conferences = Conference.query.all()
    print(f"Checking {len(conferences)} conferences for papers...")
    
    for i, conf in enumerate(conferences):
        # Skip if papers already exist for this conference
        if conf.papers:
            continue
            
        # Limit the number of conferences we enrich per run to avoid huge delays
        # or remove this check if you want provided we handle rate limits well
        # For now, let's try to enrich all but handle errors gracefully
        
        print(f"[{i+1}/{len(conferences)}] Fetching papers for: {conf.name}...")
        
        papers_data = scholar_service.search_papers_by_conference(conf.name, limit=3)
        
        if not papers_data:
            continue
            
        for p_data in papers_data:
            # Check if paper title exists (basic dedup)
            existing_paper = Paper.query.filter_by(title=p_data.get('title')).first()
            if existing_paper:
                continue
                
            new_paper = Paper(
                title=p_data.get('title'),
                conference_id=conf.id
            )
            db.session.add(new_paper)
            
            # Handle Authors
            authors_list = p_data.get('authors', [])
            for auth_data in authors_list:
                auth_name = auth_data.get('name')
                auth_id = auth_data.get('authorId')
                
                if not auth_name:
                    continue
                    
                # Check if author exists
                # Prioritize checking by ID if available, else Name
                author = None
                if auth_id:
                    author = Author.query.filter_by(semantic_scholar_id=auth_id).first()
                
                if not author:
                    author = Author.query.filter_by(name=auth_name).first()
                    
                if not author:
                    author = Author(
                        name=auth_name,
                        semantic_scholar_id=auth_id,
                        # We can fetch h-index later or now. 
                        # To keep seeding fast, maybe leave it for a background job 
                        # or fetch it if we have the data.
                        # The search_papers endpoint DOES NOT give h-index.
                    )
                    db.session.add(author)
                
                # Link author to paper
                if author not in new_paper.authors:
                    new_paper.authors.append(author)
        
        # Commit per conference to save progress
        try:
            db.session.commit()
            # Be nice to the API
            time.sleep(1) 
        except Exception as e:
            print(f"Error saving papers for {conf.name}: {e}")
            db.session.rollback()


# Deterministic fallback for top cities to ensure map works even if API fails/limits
KNOWN_LOCATIONS = {
    "Paris": (48.8566, 2.3522),
    "London": (51.5074, -0.1278),
    "Amsterdam": (52.3676, 4.9041),
    "Berlin": (52.5200, 13.4050),
    "San Francisco": (37.7749, -122.4194),
    "New York, NY": (40.7128, -74.0060),
    "Tokyo": (35.6762, 139.6503),
    "Atlanta, GA": (33.7490, -84.3880),
    "Barcelona": (41.3851, 2.1734),
    "Austin, TX": (30.2672, -97.7431),
    "Munich": (48.1351, 11.5820),
    "Chicago, IL": (41.8781, -87.6298),
    "Stockholm": (59.3293, 18.0686),
    "Lyon": (45.7640, 4.8357),
    "Madrid": (40.4168, -3.7038),
    "Prague": (50.0755, 14.4378),
    "Seattle, WA": (47.6062, -122.3321),
    "Vienna": (48.2082, 16.3738),
    "Denver, CO": (39.7392, -104.9903),
    "Montreal": (45.5017, -73.5673),
    "Singapore": (1.3521, 103.8198),
    "Zurich": (47.3769, 8.5417),
    "Warsaw": (52.2297, 21.0122),
    "Dublin": (53.3498, -6.2603),
    "Hamburg": (53.5511, 9.9937),
    "Lisbon": (38.7223, -9.1393),
    "Copenhagen": (55.6761, 12.5683),
    "Helsinki": (60.1699, 24.9384),
    "Oslo": (59.9139, 10.7522),
    "Brussels": (50.8503, 4.3517),
    "Seoul": (37.5665, 126.9780),
    "Toronto": (43.6532, -79.3832),
    "Sydney": (33.8688, 151.2093),
    "Melbourne": (37.8136, 144.9631),
    "Bangalore": (12.9716, 77.5946),
    "Hyderabad": (17.3850, 78.4867),
    "Beijing": (39.9042, 116.4074),
    "Shanghai": (31.2304, 121.4737),
    "Boston, MA": (42.3601, -71.0589),
    "Los Angeles, CA": (34.0522, -118.2437),
    "San Diego, CA": (32.7157, -117.1611),
    "Las Vegas, NV": (36.1699, -115.1398),
    "Washington D.C.": (38.9072, -77.0369),
    "Salt Lake City, UT": (40.7608, -111.8910),
    "Istanbul": (41.0082, 28.9784),
    "Krakow": (50.0647, 19.9450)
}

def fix_coordinates():
    print("Checking for missing coordinates...")
    
    # Check if we need to run first
    missing_count = Conference.query.filter(
        (Conference.latitude.is_(None)) | (Conference.longitude.is_(None)),
        Conference.city.isnot(None)
    ).count()
    
    if missing_count == 0:
        print("All conferences have coordinates.")
        return

    print(f"Found {missing_count} conferences missing coordinates. Starting geocoding...")
    
    # Group by valid city+country
    locations = db.session.query(Conference.city, Conference.country, func.count(Conference.id))\
        .filter((Conference.latitude.is_(None)) | (Conference.longitude.is_(None)))\
        .filter(Conference.city.isnot(None))\
        .group_by(Conference.city, Conference.country)\
        .order_by(func.count(Conference.id).desc())\
        .all()
        
    print(f"Unique locations to geocode: {len(locations)}")
    
    for i, (city, country, count) in enumerate(locations):
        # Skip generic/online locations
        if not city or city.lower() in ['online', 'virtual', 'webinar', 'none']:
            continue

        print(f"[{i+1}/{len(locations)}] Processing: {city} | {country} ({count} confs)...")
        
        # 1. Check KNOW_LOCATIONS first (Deterministic Fallback)
        clean_city = city.strip()
        base_city = clean_city.split(',')[0].strip() # Check base city too (e.g. "Seattle" for "Seattle, WA")
        
        lat, lng = None, None
        
        if clean_city in KNOWN_LOCATIONS:
            lat, lng = KNOWN_LOCATIONS[clean_city]
            print(f"  -> Found in dictionary: {lat}, {lng}")
        elif base_city in KNOWN_LOCATIONS:
            lat, lng = KNOWN_LOCATIONS[base_city]
            print(f"  -> Found in dictionary (base): {lat}, {lng}")
        else:
            # 2. Use API
            lat, lng = geocode_city_nominatim(city, country)
        
        if lat and lng:
            if country:
                confs = Conference.query.filter_by(city=city, country=country).all()
            else:
                confs = Conference.query.filter_by(city=city).filter(Conference.country.is_(None)).all()
            
            for conf in confs:
                conf.latitude = lat
                conf.longitude = lng
            
            # Commit frequently
            try:
                db.session.commit()
                print(f"  -> UPDATED {len(confs)} records.")
            except Exception as e:
                print(f"  -> DB Error: {e}")
                db.session.rollback()
        else:
            print(f"  -> FAILED to find coordinates.")
            # Don't sleep if we failed, maybe it's fast failure
        
        # Respect API usage policy only if we used the API
        if clean_city not in KNOWN_LOCATIONS and base_city not in KNOWN_LOCATIONS:
            time.sleep(1.2)
        
def geocode_city_nominatim(city, country, retry=0):
    base_url = "https://nominatim.openstreetmap.org/search"
    clean_city = city.strip()
    
    queries = []
    # 1. City + Country
    if country:
        queries.append(f"{clean_city}, {country}")
    else:
        queries.append(clean_city)
        
    # 2. City only (strip state if likely present e.g. "Austin, TX")
    if "," in clean_city:
        simple_city = clean_city.split(',')[0].strip()
        if country:
            queries.append(f"{simple_city}, {country}")
        else:
            queries.append(simple_city)
            
    headers = {
        'User-Agent': 'ConferenceMapFix/2.0 (debug@localhost)'
    }
    
    for q in queries:
        try:
            params = {'q': q, 'format': 'json', 'limit': 1}
            # 30s timeout as requested
            response = requests.get(base_url, params=params, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if data:
                    return float(data[0]['lat']), float(data[0]['lon'])
            elif response.status_code == 429:
                print(f"  Rate limit hit. Sleeping 5s...")
                time.sleep(5)
                if retry < 3:
                    return geocode_city_nominatim(city, country, retry + 1)
            else:
                print(f"  API StatusCode: {response.status_code}")
                    
        except requests.exceptions.Timeout:
            print(f"  Timeout (30s) querying '{q}'. Retrying...")
            if retry < 2:
                time.sleep(2)
                return geocode_city_nominatim(city, country, retry + 1)
        except Exception as e:
            print(f"  Error querying '{q}': {e}")
            
        time.sleep(1) 
        
    return None, None

if __name__ == '__main__':
    seed_data()
