"""
Simple Map - Shows conferences grouped by city as scaled circles
"""

from flask.views import MethodView
from flask_smorest import Blueprint
from flask import jsonify
from models import Conference
from sqlalchemy import func
from db import db

blp = Blueprint("map", __name__, description="Map operations")


@blp.route("/map/cities")
class MapCities(MethodView):
    def get(self):
        """
        Group conferences by city, return city coords and count.
        Query parameters: 
          - start_year: Filter by conferences starting from this year
          - end_year: Filter by conferences up to this year
        """
        from flask import request
        from datetime import datetime
        
        try:
            # Get optional date filters
            start_year = request.args.get('start_year', type=int)
            end_year = request.args.get('end_year', type=int)
            
            query = Conference.query.filter(
                Conference.city.isnot(None),
                Conference.latitude.isnot(None),
                Conference.longitude.isnot(None)
            )
            
            # Apply year filters
            if start_year:
                query = query.filter(
                    Conference.start_date >= datetime(start_year, 1, 1)
                )
            if end_year:
                query = query.filter(
                    Conference.start_date <= datetime(end_year, 12, 31)
                )
            
            result = query.with_entities(
                Conference.city,
                Conference.country,
                func.avg(Conference.latitude).label('lat'),
                func.avg(Conference.longitude).label('lng'),
                func.count(Conference.id).label('count')
            ).group_by(Conference.city, Conference.country).all()

            points = [
                {
                    'city': row.city,
                    'country': row.country,
                    'lat': float(row.lat),
                    'lng': float(row.lng),
                    'count': int(row.count)
                }
                for row in result
            ]
            
            return jsonify({
                'points': points,
                'filters': {
                    'start_year': start_year,
                    'end_year': end_year
                },
                'total_cities': len(points),
                'total_conferences': sum(p['count'] for p in points)
            })
        except Exception as e:
            return jsonify({'error': str(e), 'points': []}), 400


@blp.route("/map")
class MapView(MethodView):
    def get(self):
        """
        Render interactive Leaflet map visualization.
        Fetches data from /map/cities endpoint and displays conferences as scaled circles.
        """
        return """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Conference Map</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', sans-serif; height: 100vh; }
        #map { height: 100vh; width: 100%; }
        .info-panel {
            position: absolute;
            top: 10px;
            right: 10px;
            background: white;
            padding: 15px 20px;
            border-radius: 5px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.15);
            z-index: 1000;
            font-size: 13px;
            min-width: 220px;
        }
        .info-panel h3 { margin: 0 0 10px 0; font-size: 14px; color: #333; }
        .info-panel p { margin: 5px 0; color: #666; }
        .filter-panel {
            position: absolute;
            bottom: 10px;
            left: 10px;
            background: white;
            padding: 15px 20px;
            border-radius: 5px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.15);
            z-index: 1000;
            font-size: 13px;
        }
        .filter-panel input {
            padding: 5px 8px;
            margin: 5px 5px 5px 0;
            border: 1px solid #ddd;
            border-radius: 3px;
            font-size: 12px;
        }
        .filter-panel button {
            padding: 5px 12px;
            background: #007bff;
            color: white;
            border: none;
            border-radius: 3px;
            cursor: pointer;
            font-size: 12px;
        }
        .filter-panel button:hover { background: #0056b3; }
    </style>
</head>
<body>
    <div id="map"></div>
    <div class="info-panel" id="info">
        <h3>📍 Conference Map</h3>
        <p id="status">Loading data...</p>
    </div>
    <div class="filter-panel">
        <input type="number" id="startYear" placeholder="Start Year" min="1990" max="2100">
        <input type="number" id="endYear" placeholder="End Year" min="1990" max="2100">
        <button onclick="applyFilters()">Filter</button>
        <button onclick="resetFilters()">Reset</button>
    </div>
    
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script>
        const map = L.map('map').setView([20, 0], 2);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors',
            maxZoom: 19
        }).addTo(map);

        let allMarkers = [];

        async function loadMap() {
            clearMarkers();
            const startYear = document.getElementById('startYear').value;
            const endYear = document.getElementById('endYear').value;
            
            let url = '/map/cities';
            const params = new URLSearchParams();
            if (startYear) params.append('start_year', startYear);
            if (endYear) params.append('end_year', endYear);
            if (params.toString()) url += '?' + params.toString();
            
            try {
                const response = await fetch(url);
                const data = await response.json();
                
                if (!data.points || data.points.length === 0) {
                    document.getElementById('status').innerHTML = '⚠️ No conferences found';
                    return;
                }

                const maxCount = Math.max(...data.points.map(p => p.count));
                
                data.points.forEach(point => {
                    const ratio = point.count / maxCount;
                    const radius = 8 + ratio * 35;
                    const red = Math.floor(255 * ratio);
                    const blue = Math.floor(255 * (1 - ratio));
                    const color = `rgb(${red}, 100, ${blue})`;
                    
                    const marker = L.circleMarker([point.lat, point.lng], {
                        radius: radius,
                        color: color,
                        fillOpacity: 0.75,
                        weight: 2,
                        fillColor: color
                    })
                    .bindPopup(`<b>${point.city}</b><br><small>${point.country}</small><br><strong>${point.count}</strong> conference${point.count !== 1 ? 's' : ''}`);
                    
                    marker.addTo(map);
                    allMarkers.push(marker);
                });

                const total = data.total_conferences || 0;
                document.getElementById('status').innerHTML = 
                    `<b>Cities:</b> ${data.total_cities}<br><b>Conferences:</b> ${total}`;
            } catch (error) {
                document.getElementById('status').innerHTML = '❌ Error loading data';
                console.error('Error:', error);
            }
        }

        function clearMarkers() {
            allMarkers.forEach(marker => map.removeLayer(marker));
            allMarkers = [];
        }

        function applyFilters() {
            loadMap();
        }

        function resetFilters() {
            document.getElementById('startYear').value = '';
            document.getElementById('endYear').value = '';
            loadMap();
        }

        // Initial load
        loadMap();
    </script>
</body>
</html>
        """


