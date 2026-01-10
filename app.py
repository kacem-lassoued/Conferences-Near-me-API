from flask import Flask
from flask_smorest import Api
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from db import db
import os
import logging
from logging.handlers import RotatingFileHandler

from resources.conference import blp as ConferenceBlueprint
from resources.submission import blp as SubmissionBlueprint
from resources.auth import blp as AuthBlueprint
from resources.admin import blp as AdminBlueprint
from resources.author import blp as AuthorBlueprint
from resources.map import blp as MapBlueprint

app = Flask(__name__)
CORS(app)

# Database config
basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", f"sqlite:///{os.path.join(basedir, 'instance', 'dev.db')}")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# OpenAPI Config
app.config["API_TITLE"] = "Conference Discovery API"
app.config["API_VERSION"] = "v1"
app.config["OPENAPI_VERSION"] = "3.0.3"
app.config["OPENAPI_URL_PREFIX"] = "/"
app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui/"
app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist@4/"

# Auth Config - Enforce JWT secret in production
jwt_secret = os.environ.get("JWT_SECRET_KEY")
if not jwt_secret:
    if os.environ.get("FLASK_ENV") == "production":
        raise ValueError("JWT_SECRET_KEY environment variable must be set in production")
    jwt_secret = "dev-secret-key-change-in-production"
app.config["JWT_SECRET_KEY"] = jwt_secret

print(f"DEBUG: SQLALCHEMY_DATABASE_URI = {app.config['SQLALCHEMY_DATABASE_URI']}")

db.init_app(app)
jwt = JWTManager(app)

api = Api(app)

api.register_blueprint(ConferenceBlueprint)
api.register_blueprint(SubmissionBlueprint)
api.register_blueprint(AuthBlueprint)
api.register_blueprint(AdminBlueprint)
api.register_blueprint(AuthorBlueprint)
api.register_blueprint(MapBlueprint)


@app.route("/")
def index():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <title>Conference Discovery API</title>
        <style>
            body { 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                display: flex; 
                justify-content: center; 
                align-items: center; 
                height: 100vh; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                margin: 0;
            }
            .container { 
                background: white; 
                padding: 3rem; 
                border-radius: 12px; 
                text-align: center; 
                box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                max-width: 600px;
            }
            h1 {
                color: #333;
                margin-bottom: 1rem;
                font-size: 2.5rem;
            }
            .links {
                display: flex;
                flex-direction: column;
                gap: 1rem;
                margin-top: 2rem;
            }
            .links a {
                display: inline-block;
                padding: 12px 24px;
                background: #007bff;
                color: white;
                text-decoration: none;
                border-radius: 6px;
                font-weight: 500;
                transition: background 0.3s;
            }
            .links a:hover {
                background: #0056b3;
            }
            .links a.map-link {
                background: #28a745;
            }
            .links a.map-link:hover {
                background: #218838;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🗺️ Conference Discovery API</h1>
            <p style="color: #666; font-size: 1.1rem;">Discover academic conferences around the world</p>
            <div class="links">
                <a href="/map" class="map-link">🗺️ Interactive Map</a>
                <a href="/swagger-ui/">📚 API Documentation (Swagger)</a>
            </div>
        </div>
    </body>
    </html>
    """

@app.route("/ping")
def ping():
    return {"message": "ping"}

# Configure logging
if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Conference Discovery API startup')

# Create DB tables if not exist
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    # Disable debug mode in production
    debug_mode = os.environ.get("FLASK_DEBUG", "False").lower() == "true"
    app.run(debug=debug_mode, host="0.0.0.0", port=5000)
