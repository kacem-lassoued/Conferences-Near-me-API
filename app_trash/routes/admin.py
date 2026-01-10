from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from app.models.submission import PendingSubmission
from app.models.conference import Conference
from app.extensions import db
from functools import wraps
from datetime import datetime
import logging

admin_bp = Blueprint('admin', __name__)
logger = logging.getLogger(__name__)

def admin_only(fn):
    """Decorator to ensure only admins can access the route"""
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        claims = get_jwt()
        if claims.get('role') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        return fn(*args, **kwargs)
    return wrapper

def validate_conference_data(data):
    """Validate conference data before processing"""
    errors = []
    
    if not data.get('name'):
        errors.append('Conference name is required')
    if not data.get('country'):
        errors.append('Country is required')
    
    # Validate dates
    if data.get('start_date') and data.get('end_date'):
        try:
            start = datetime.fromisoformat(data.get('start_date').replace('Z', '+00:00'))
            end = datetime.fromisoformat(data.get('end_date').replace('Z', '+00:00'))
            if start > end:
                errors.append('Start date must be before end date')
        except (ValueError, AttributeError, TypeError):
            errors.append('Invalid date format. Use ISO 8601 format')
    
    # Validate coordinates
    if data.get('latitude') is not None:
        try:
            lat = float(data.get('latitude'))
            if not -90 <= lat <= 90:
                errors.append('Latitude must be between -90 and 90')
        except (ValueError, TypeError):
            errors.append('Latitude must be a valid number')
    
    if data.get('longitude') is not None:
        try:
            lng = float(data.get('longitude'))
            if not -180 <= lng <= 180:
                errors.append('Longitude must be between -180 and 180')
        except (ValueError, TypeError):
            errors.append('Longitude must be a valid number')
    
    return errors

@admin_bp.route('/pending', methods=['GET'])
@admin_only
def get_pending():
    """
    Get Pending Submissions (Admin Only)
    ---
    tags:
      - Admin
    security:
      - Bearer: []
    responses:
      200:
        description: List of pending submissions
      403:
        description: Forbidden
    """
    pending = PendingSubmission.query.filter_by(status='pending').all()
    return jsonify([p.to_dict() for p in pending])

@admin_bp.route('/approve/<int:id>', methods=['POST'])
@admin_only
def approve_submission(id):
    """
    Approve a Submission
    ---
    tags:
      - Admin
    security:
      - Bearer: []
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Approved and Processed
      400:
        description: Invalid submission or validation error
      404:
        description: Submission not found
      500:
        description: Server error
    """
    submission = PendingSubmission.query.get_or_404(id)
    if submission.status != 'pending':
        return jsonify({'error': 'Submission already processed'}), 400
        
    # Process logic based on type
    try:
        if submission.type == 'new_conference':
            data = submission.payload
            
            # Validate conference data
            validation_errors = validate_conference_data(data)
            if validation_errors:
                return jsonify({'error': 'Validation failed', 'details': validation_errors}), 400
            
            # Parse dates
            start_date = None
            end_date = None
            if data.get('start_date'):
                start_date = datetime.fromisoformat(data.get('start_date').replace('Z', '+00:00')).date()
            if data.get('end_date'):
                end_date = datetime.fromisoformat(data.get('end_date').replace('Z', '+00:00')).date()
            
            conf = Conference(
                name=data.get('name'),
                acronym=data.get('acronym'),
                description=data.get('description'),
                website=data.get('website'),
                start_date=start_date,
                end_date=end_date,
                country=data.get('country'),
                city=data.get('city'),
                latitude=float(data.get('latitude')) if data.get('latitude') else None,
                longitude=float(data.get('longitude')) if data.get('longitude') else None,
                source='user_submission'
            )
            db.session.add(conf)
            logger.info(f'Approved new conference: {data.get("name")}')
            
        elif submission.type == 'cancellation':
            conf_id = submission.payload.get('conference_id')
            if not conf_id:
                return jsonify({'error': 'conference_id is required for cancellation'}), 400
            
            conf = Conference.query.get(conf_id)
            if not conf:
                return jsonify({'error': 'Conference not found'}), 404
            
            conf.status = 'cancelled'
            logger.info(f'Cancelled conference ID: {conf_id}')
        
        elif submission.type == 'modification':
            data = submission.payload
            conf_id = data.get('conference_id')
            
            if not conf_id:
                return jsonify({'error': 'conference_id is required for modification'}), 400
            
            conf = Conference.query.get(conf_id)
            if not conf:
                return jsonify({'error': 'Conference not found'}), 404
            
            # Validate modified data
            validation_errors = validate_conference_data(data)
            if validation_errors:
                return jsonify({'error': 'Validation failed', 'details': validation_errors}), 400
            
            # Update fields
            if data.get('name'):
                conf.name = data.get('name')
            if data.get('acronym'):
                conf.acronym = data.get('acronym')
            if data.get('description') is not None:
                conf.description = data.get('description')
            if data.get('website'):
                conf.website = data.get('website')
            if data.get('start_date'):
                conf.start_date = datetime.fromisoformat(data.get('start_date').replace('Z', '+00:00')).date()
            if data.get('end_date'):
                conf.end_date = datetime.fromisoformat(data.get('end_date').replace('Z', '+00:00')).date()
            if data.get('country'):
                conf.country = data.get('country')
            if data.get('city'):
                conf.city = data.get('city')
            if data.get('latitude') is not None:
                conf.latitude = float(data.get('latitude'))
            if data.get('longitude') is not None:
                conf.longitude = float(data.get('longitude'))
            
            logger.info(f'Modified conference ID: {conf_id}')
        
        else:
            return jsonify({'error': f'Unknown submission type: {submission.type}'}), 400
        
        # Mark as approved
        submission.status = 'approved'
        db.session.commit()
        return jsonify({'message': 'Submission approved and processed', 'submission_id': id})
        
    except ValueError as e:
        db.session.rollback()
        logger.error(f'Validation error: {str(e)}')
        return jsonify({'error': f'Invalid data format: {str(e)}'}), 400
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error approving submission {id}: {str(e)}')
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@admin_bp.route('/reject/<int:id>', methods=['POST'])
@admin_only
def reject_submission(id):
    """
    Reject a Submission
    ---
    tags:
      - Admin
    security:
      - Bearer: []
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Submission rejected
      404:
        description: Submission not found
    """
    submission = PendingSubmission.query.get_or_404(id)
    submission.status = 'rejected'
    db.session.commit()
    logger.info(f'Rejected submission ID: {id}')
    return jsonify({'message': 'Submission rejected'})
