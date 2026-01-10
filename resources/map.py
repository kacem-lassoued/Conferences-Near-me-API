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
        """Group conferences by city, return city coords and count."""
        result = db.session.query(
            Conference.city,
            Conference.country,
            func.avg(Conference.latitude).label('lat'),
            func.avg(Conference.longitude).label('lng'),
            func.count(Conference.id).label('count')
        ).filter(
            Conference.city.isnot(None),
            Conference.latitude.isnot(None),
            Conference.longitude.isnot(None)
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
        
        return jsonify({'points': points})


@blp.route("/map")
class MapView(MethodView):
    def get(self):
        """Simple map showing conferences as circles scaled by count per city."""
        return """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Conference Heatmap</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <style>
        * { margin: 0; padding: 0; }
        body { font-family: sans-serif; height: 100vh; }
        #map { height: 100vh; width: 100%; }
        .info {
            position: absolute;
            top: 10px;
            right: 10px;
            background: white;
            padding: 15px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
            z-index: 1000;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div id="map"></div>
    <div class="info" id="info">Loading...</div>
    
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script>
        const map = L.map('map').setView([20, 0], 2);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap',
            maxZoom: 19
        }).addTo(map);

        async function loadMap() {
            const response = await fetch('/map/cities');
            const data = await response.json();
            
            if (!data.points || data.points.length === 0) {
                document.getElementById('info').innerHTML = 'No data';
                return;
            }

            const maxCount = Math.max(...data.points.map(p => p.count));
            
            data.points.forEach(point => {
                const ratio = point.count / maxCount;
                const radius = 5 + ratio * 30;
                const red = Math.floor(255 * ratio);
                const color = `rgb(${red}, 0, ${255 - red})`;
                
                L.circleMarker([point.lat, point.lng], {
                    radius: radius,
                    color: color,
                    fillOpacity: 0.7,
                    weight: 2,
                    fillColor: color
                })
                .bindPopup(`<b>${point.city}</b><br>${point.country}<br>${point.count} conferences`)
                .addTo(map);
            });

            document.getElementById('info').innerHTML = `<b>Cities:</b> ${data.points.length}`;
        }

        loadMap();
    </script>
</body>
</html>
        """


