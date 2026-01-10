from flask import Flask
from flask_smorest import Api
from resources.course_item import blp as CourseItemBlueprint
from resources.specialization import blp as SpecializationBlueprint
from db import db
import os
from flask_jwt_extended import JWTManager


app = Flask(__name__)

# Database configuration
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'data.db')
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Flask-Smorest / Swagger configuration
app.config["PROPAGATE_EXCEPTIONS"] = True
app.config["API_TITLE"] = "Specialization REST API"
app.config["API_VERSION"] = "v1"
app.config["OPENAPI_VERSION"] = "3.0.3"
app.config["OPENAPI_URL_PREFIX"] = "/"
app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui/"
app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist@4/"

# JWT configuration
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "super-secret-key")

# Initialize JWT
jwt = JWTManager(app)

# Initialize database
db.init_app(app)

# Import models AFTER db.init_app
from models import SpecializationModel, CourseItemModel


api = Api(app)

api.register_blueprint(CourseItemBlueprint)
api.register_blueprint(SpecializationBlueprint)
from resources.auth import blp as AuthBlueprint
api.register_blueprint(AuthBlueprint)

@app.route("/ping")
def ping():
    return {"message": "ping"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)