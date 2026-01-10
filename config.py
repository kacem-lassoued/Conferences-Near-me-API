import os
import logging

class Config:
    """Base Configuration"""
    # Security - Should be set via environment variable in production
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY and os.environ.get('FLASK_ENV') == 'production':
        raise ValueError('SECRET_KEY environment variable must be set in production')
    if not SECRET_KEY:
        SECRET_KEY = 'dev_key_change_in_production'
    
    # Database
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    if not SQLALCHEMY_DATABASE_URI:
        if os.environ.get('FLASK_ENV') == 'production':
            raise ValueError('DATABASE_URL environment variable must be set in production')
        SQLALCHEMY_DATABASE_URI = 'sqlite:///dev.db'
    
    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    if not JWT_SECRET_KEY:
        if os.environ.get('FLASK_ENV') == 'production':
            raise ValueError('JWT_SECRET_KEY environment variable must be set in production')
        JWT_SECRET_KEY = 'jwt_dev_secret_change_in_production'

    # Admin Auth
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD')
    if not ADMIN_PASSWORD and os.environ.get('FLASK_ENV') == 'production':
        raise ValueError('ADMIN_PASSWORD environment variable must be set in production')
    if not ADMIN_PASSWORD:
        ADMIN_PASSWORD = 'adminpassword'
    
    # Swagger Config
    SWAGGER = {
        'title': 'Conference Discovery API',
        'uiversion': 3,
        'version': '1.0.0',
        'description': 'API for Public Conference Discovery & Research Indexing Platform',
        'specs_route': '/swagger-ui/'
    }
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')

class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False

class TestingConfig(Config):
    DEBUG = False
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    # In production, all required environment variables must be set
    # Enforce via the Config base class

# Configuration selector
def get_config():
    env = os.environ.get('FLASK_ENV', 'development')
    if env == 'production':
        return ProductionConfig
    elif env == 'testing':
        return TestingConfig
    else:
        return DevelopmentConfig
