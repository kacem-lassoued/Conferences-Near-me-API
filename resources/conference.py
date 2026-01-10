from flask.views import MethodView
from flask_smorest import Blueprint
from flask_jwt_extended import jwt_required, get_jwt
from models import Conference
from schemas import ConferenceSchema, ConferenceQuerySchema, ConferenceUpdateSchema
from sqlalchemy import or_
from db import db

blp = Blueprint("conferences", __name__, description="Operations on conferences")


# ============================================================================
# CONFERENCES - Collection Endpoints
# ============================================================================

@blp.route("/conferences")
class ConferenceList(MethodView):
    @blp.arguments(ConferenceQuerySchema, location="query")
    @blp.response(200, ConferenceSchema(many=True))
    def get(self, args):
        """Get list of conferences with search, filter, sort, and pagination"""
        query = Conference.query
        
        # Search by name or acronym
        if 'q' in args and args['q']:
            search = f"%{args['q']}%"
            query = query.filter(or_(
                Conference.name.ilike(search),
                Conference.acronym.ilike(search)
            ))
        
        # Filter by country
        if 'country' in args and args['country']:
            query = query.filter(Conference.country.ilike(f"%{args['country']}%"))
        
        # Sorting
        sort_by = args.get('sort_by', 'created_at')
        if sort_by == 'name':
            query = query.order_by(Conference.name)
        elif sort_by == 'start_date':
            query = query.order_by(Conference.start_date.desc())
        else:  # default to created_at
            query = query.order_by(Conference.created_at.desc())
        
        # Pagination
        page = args.get('page', 1)
        per_page = args.get('per_page', 20)
        
        # Get paginated results
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return pagination.items


# ============================================================================
# CONFERENCES - Item Endpoints
# ============================================================================

@blp.route("/conferences/<int:conference_id>")
class ConferenceDetail(MethodView):
    @blp.response(200, ConferenceSchema)
    def get(self, conference_id):
        """Get detailed information about a specific conference"""
        return Conference.query.get_or_404(conference_id)
    
    @jwt_required()
    @blp.arguments(ConferenceUpdateSchema)
    @blp.response(200, ConferenceSchema)
    def put(self, update_data, conference_id):
        """Update a conference (Admin only)"""
        # Check admin access
        claims = get_jwt()
        if claims.get("role") != "admin":
            return {"message": "Admin required"}, 403
        
        conference = Conference.query.get_or_404(conference_id)
        
        # Update fields that are provided
        for field, value in update_data.items():
            if value is not None:  # Only update if value is provided
                setattr(conference, field, value)
        
        db.session.commit()
        return conference
    
    @jwt_required()
    @blp.response(200)
    def delete(self, conference_id):
        """Delete a conference (Admin only)"""
        # Check admin access
        claims = get_jwt()
        if claims.get("role") != "admin":
            return {"message": "Admin required"}, 403
        
        conference = Conference.query.get_or_404(conference_id)
        conference_name = conference.name
        
        db.session.delete(conference)
        db.session.commit()
        
        return {
            "message": f"Conference '{conference_name}' deleted successfully",
            "id": conference_id
        }
