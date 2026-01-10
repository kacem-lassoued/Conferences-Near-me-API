from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.submission import PendingSubmission
from app.models.user import User
from app.extensions import db
import logging

submissions_bp = Blueprint('submissions', __name__)
logger = logging.getLogger(__name__)

def validate_submission_payload(submission_type, payload):
    """
    Validate submission payload structure.
    Checks if the data sent by the user matches what we expect
    for that specific type of request.
    """
    errors = []
    
    if submission_type not in ['new_conference', 'cancellation', 'modification']:
        errors.append(f'Invalid submission type. Must be one of: new_conference, cancellation, modification')
        return errors
    
    if not isinstance(payload, dict):
        errors.append('Payload must be a JSON object')
        return errors
    
    if submission_type == 'new_conference':
        if not payload.get('name'):
            errors.append('Conference name is required')
        if not payload.get('country'):
            errors.append('Country is required')
    
    elif submission_type in ['cancellation', 'modification']:
        if not payload.get('conference_id'):
            errors.append(f'conference_id is required for {submission_type}')
        elif not isinstance(payload.get('conference_id'), int):
            errors.append('conference_id must be an integer')
    
    return errors

@submissions_bp.route('/', methods=['POST'])
def submit_request():
    """
    Submit a Request (New Conference, Modification, Cancellation)
    ---
    tags:
      - Submissions
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required:
            - type
            - payload
          properties:
            type:
              type: string
              enum: [new_conference, cancellation, modification]
            payload:
              type: object
    responses:
      201:
        description: Submission received
      400:
        description: Validation error
      500:
        description: Server error
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request body must be valid JSON'}), 400
        
        submission_type = data.get('type')
        payload = data.get('payload')
        
        # Validate request structure
        if not submission_type:
            return jsonify({'error': 'type field is required'}), 400
        
        if payload is None:
            return jsonify({'error': 'payload field is required'}), 400
        
        # Validate payload
        validation_errors = validate_submission_payload(submission_type, payload)
        if validation_errors:
            return jsonify({'error': 'Validation failed', 'details': validation_errors}), 400
        
        # Create submission (Anonymous)
        submission = PendingSubmission(
            type=submission_type,
            payload=payload,
            user_id=None # Anonymous submission
        )
        
        db.session.add(submission)
        db.session.commit()
        
        logger.info(f'New anonymous submission {submission.id}: {submission_type}')
        
        return jsonify({
            'message': 'Submission received, awaiting approval',
            'id': submission.id,
            'status': 'pending'
        }), 201

    except ValueError as e:
        logger.error(f'Validation error: {str(e)}')
        return jsonify({'error': f'Invalid data: {str(e)}'}), 400
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error creating submission: {str(e)}')
        return jsonify({'error': f'Server error: {str(e)}'}), 500
