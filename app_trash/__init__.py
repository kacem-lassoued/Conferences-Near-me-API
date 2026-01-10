from flask import Flask
from config import Config
from app.extensions import db, cors, jwt, swagger

def create_app(config_class=Config):
    """
    The Application Factory:
    This function creates the Flask app, connects the database, 
    and registers all the routes.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize Flask Extensions
    db.init_app(app)
    cors.init_app(app)
    jwt.init_app(app)
    swagger.init_app(app)

    # WORKAROUND: Fix Flasgger BuildError (it expects 'flasgger.static' but registers 'apidocs.static')
    # We simply point the missing endpoint to the existing one.
    if 'flasgger.static' not in app.view_functions:
        with app.app_context():
            # We delay this to ensure blueprint is registered, although init_app should do it.
            # But safer to just add a dummy rule if needed, or better:
            pass # The alias below is safer
            
    # Explicitly alias the endpoint
    # Note: Flask routing is complex, but this tells url_for that 'flasgger.static' exists.
    # We find the view function for apidocs.static and reuse it.
    try:
        app.view_functions['flasgger.static'] = app.view_functions['apidocs.static']
        app.add_url_rule('/apidocs/static/<path:filename>', endpoint='flasgger.static', view_func=app.view_functions['apidocs.static'])
    except KeyError:
        pass # If apidocs.static doesn't exist, we skip (shouldn't happen with Swagger)

    # Register Blueprints (Routes)
    # Think of Blueprints as "Chapters" in a book, organizing routes by topic.
    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    
    from app.routes.conferences import conferences_bp
    app.register_blueprint(conferences_bp, url_prefix='/api/conferences')
    
    from app.routes.submissions import submissions_bp
    app.register_blueprint(submissions_bp, url_prefix='/api/submissions')
    
    from app.routes.admin import admin_bp
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    
    from app.routes.reference import reference_bp
    app.register_blueprint(reference_bp, url_prefix='/api/reference')

    @app.route('/')
    def index():
        from flask import render_template
        return render_template('index.html')

    return app
