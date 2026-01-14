from flask.views import MethodView
from flask_smorest import Blueprint
from flask_jwt_extended import jwt_required, get_jwt
from models import Conference
from schemas import ConferenceSchema, ConferenceUpdateSchema
from db import db
import logging
from utils.errors import make_response, make_error_response, NotFoundError, UnauthorizedError
from services.scholar_service import search_conference_info

logger = logging.getLogger(__name__)

blp = Blueprint("conferences", __name__, description="Operations on conferences")


# ============================================================================
# CONFERENCES - Collection Endpoints
# ============================================================================

@blp.route("/conferences")
class ConferenceList(MethodView):
    @blp.response(200)
    def get(self):
        """
        Get list of all conferences.
        """
        try:
            conferences = Conference.query.all()
            conferences_data = ConferenceSchema(many=True).dump(conferences)
            
            logger.debug(f"Retrieved {len(conferences_data)} conferences")
            
            return make_response(
                data=conferences_data,
                message=f"Retrieved {len(conferences_data)} conferences"
            )
        
        except Exception as e:
            logger.error(f"Error fetching conferences: {e}", exc_info=True)
            return {
                "data": [],
                "message": f"Error fetching conferences: {str(e)}",
                "success": True
            }, 200


# ============================================================================
# CONFERENCES - Item Endpoints
# ============================================================================

@blp.route("/conferences/<int:conference_id>")
class ConferenceDetail(MethodView):
    @blp.response(200)
    def get(self, conference_id):
        """
        Get detailed information about a specific conference.
        Includes papers, authors, and enriched data.
        """
        try:
            conference = Conference.query.get_or_404(conference_id)
            conference_data = ConferenceSchema().dump(conference)
            
            # Attempt to get additional Semantic Scholar data
            additional_data = {}
            try:
                conf_info = search_conference_info(conference.name)
                if conf_info:
                    additional_data = {
                        'semantic_scholar_info': {
                            'papers_found': conf_info.get('papers_found'),
                            'unique_authors': conf_info.get('unique_authors'),
                            'total_citations': conf_info.get('total_citations'),
                            'avg_citations_per_paper': round(conf_info.get('avg_citations_per_paper', 0), 2)
                        }
                    }
                    logger.debug(f"Enriched conference {conference_id} with Semantic Scholar data")
            except Exception as e:
                logger.warning(f"Could not enrich conference with Semantic Scholar data: {e}")
            
            return make_response(
                data={
                    **conference_data,
                    **additional_data
                },
                message="Conference details retrieved"
            )
        
        except Exception as e:
            logger.error(f"Error fetching conference {conference_id}: {e}", exc_info=True)
            return make_error_response(
                NotFoundError(f"Conference {conference_id}")
            )
    
    @jwt_required()
    @blp.arguments(ConferenceUpdateSchema)
    @blp.response(200)
    def put(self, update_data, conference_id):
        """
        Update a conference (Admin only).
        Only updates provided fields.
        """
        try:
            # Check admin access
            claims = get_jwt()
            if claims.get("role") != "admin":
                return make_error_response(
                    UnauthorizedError("Admin access required to update conferences")
                )
            
            conference = Conference.query.get_or_404(conference_id)
            
            logger.info(f"Updating conference {conference_id}: {conference.name}")
            
            # Update fields that are provided
            for field, value in update_data.items():
                if value is not None:
                    setattr(conference, field, value)
                    logger.debug(f"Updated {field} for conference {conference_id}")
            
            db.session.commit()
            
            logger.info(f"✓ Conference {conference_id} updated successfully")
            
            return make_response(
                data=ConferenceSchema().dump(conference),
                message="Conference updated successfully"
            )
        
        except Exception as e:
            logger.error(f"Error updating conference {conference_id}: {e}", exc_info=True)
            db.session.rollback()
            return make_error_response(
                NotFoundError(f"Error updating conference: {str(e)}")
            )
    
    @jwt_required()
    @blp.response(200)
    def delete(self, conference_id):
        """Delete a conference (Admin only)"""
        try:
            # Check admin access
            claims = get_jwt()
            if claims.get("role") != "admin":
                return make_error_response(
                    UnauthorizedError("Admin access required to delete conferences")
                )
            
            conference = Conference.query.get_or_404(conference_id)
            conference_name = conference.name
            
            logger.info(f"Deleting conference {conference_id}: {conference_name}")
            
            db.session.delete(conference)
            db.session.commit()
            
            logger.info(f"✓ Conference {conference_id} deleted successfully")
            
            return make_response(
                data={'id': conference_id, 'name': conference_name},
                message=f"Conference '{conference_name}' deleted successfully"
            )
        
        except Exception as e:
            logger.error(f"Error deleting conference {conference_id}: {e}", exc_info=True)
            db.session.rollback()
            return make_error_response(
                NotFoundError(f"Error deleting conference: {str(e)}")
            )
