from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token
import logging

# Simplified Authentication: Single Password for Admin Access

auth_bp = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Endpoint for admin login.
    Takes a password and returns a JWT token if correct.
    """
    try:
        # Get JSON data
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request body must be valid JSON'}), 400
        
        # We only look for 'password'
        password = data.get('password', '')
        
        if not password:
            return jsonify({'error': 'Password is required'}), 400
        
        # Check against the configured admin password
        admin_password = current_app.config.get('ADMIN_PASSWORD')
        
        if password == admin_password:
            # Create a "Token" (JWT) with admin role
            # Identity must be a string (the subject)
            access_token = create_access_token(identity="admin", additional_claims={"role": "admin"})
            
            logger.info('Admin logged in successfully')
            
            # Return the token to the user
            return jsonify(access_token=access_token), 200
        
        # If we get here, login failed
        logger.warning('Failed login attempt')
        return jsonify({'error': 'Invalid password'}), 401
    
    except Exception as e:
        logger.error(f'Login error: {str(e)}')
        return jsonify({'error': f'Server error: {str(e)}'}), 500

