from flask.views import MethodView
from flask_smorest import Blueprint
from flask_jwt_extended import jwt_required, get_jwt
from models import PendingSubmission, Conference, Author, Paper
from schemas import SubmissionSchema, ConferenceSchema, SubmissionActionSchema, PendingSubmissionUpdateSchema
from db import db
from datetime import datetime



blp = Blueprint("admin", __name__, description="Admin operations")

def check_admin():
    claims = get_jwt()
    if claims.get("role") != "admin":
        return True
    return False


# ============================================================================
# PENDING SUBMISSIONS - Collection Endpoints
# ============================================================================

@blp.route("/admin/pending")
class PendingList(MethodView):
    @jwt_required()
    def get(self):
        """Get all pending submissions (Admin only)"""
        if check_admin(): return {"message": "Admin required"}, 403
        pending = PendingSubmission.query.filter_by(status='pending').all()
        return [{"id": p.id, "type": p.type, "payload": p.payload, "status": p.status} for p in pending]
    
    @jwt_required()
    def delete(self):
        """Delete all pending submissions (Admin only)"""
        if check_admin(): return {"message": "Admin required"}, 403
        
        pending_count = PendingSubmission.query.filter_by(status='pending').count()
        PendingSubmission.query.filter_by(status='pending').delete()
        db.session.commit()
        
        return {
            "message": f"Deleted {pending_count} pending submission(s)",
            "deleted_count": pending_count
        }


# ============================================================================
# PENDING SUBMISSIONS - Item Endpoints
# ============================================================================

@blp.route("/admin/pending/<int:submission_id>")
class PendingSubmissionDetail(MethodView):
    @jwt_required()
    @blp.arguments(PendingSubmissionUpdateSchema)
    @blp.response(200)
    def put(self, update_data, submission_id):
        """Update a pending submission's payload (Admin only)"""
        if check_admin(): return {"message": "Admin required"}, 403
        
        submission = PendingSubmission.query.get_or_404(submission_id)
        
        if submission.status != 'pending':
            return {"message": "Can only update pending submissions"}, 400
        
        # Update the payload
        submission.payload = update_data.get('payload', submission.payload)
        db.session.commit()
        
        return {
            "message": "Submission updated successfully",
            "id": submission.id,
            "type": submission.type,
            "payload": submission.payload,
            "status": submission.status
        }


# ============================================================================
# SUBMISSION ACTIONS - Approve/Reject
# ============================================================================

@blp.route("/admin/approve")
class ApproveSubmission(MethodView):
    @jwt_required()
    @blp.arguments(SubmissionActionSchema)
    def post(self, action_data):
        if check_admin(): return {"message": "Admin required"}, 403
        
        submission_id = action_data['submission_id']
        submission = PendingSubmission.query.get_or_404(submission_id)
        
        if submission.status != 'pending':
            return {"message": "Submission already processed"}, 400
        
        # Create conference from submission
        if submission.type == 'new_conference':
            payload = submission.payload
            
            # Create the conference
            conf = Conference(
                name=payload.get('name'),
                organizers=payload.get('organizers'),
                location=payload.get('location'),
                featured_workshops=payload.get('featured_workshops')
            )
            db.session.add(conf)
            db.session.flush()  # Get conference ID
            
            # Process papers and authors
            papers_data = payload.get('papers', [])
            processed_authors = []
            
            for paper_data in papers_data:
                # Create paper
                paper = Paper(
                    title=paper_data.get('title'),
                    conference_id=conf.id
                )
                db.session.add(paper)
                db.session.flush()  # Get paper ID
                
                # Use enriched authors if available, otherwise fall back to raw names
                authors_source = paper_data.get('enriched_authors', [])
                if not authors_source:
                    # Fallback to reconstructing from names (shouldn't happen with new submissions)
                    raw_names = paper_data.get('authors', [])
                    authors_source = [{'name': name, 'h_index': None} for name in raw_names]
                
                for author_info in authors_source:
                    name = author_info.get('name')
                    semantic_scholar_id = author_info.get('semantic_scholar_id')
                    enriched_h_index = author_info.get('h_index')
                    affiliation = author_info.get('affiliation')
                    
                    # First try to find by semantic_scholar_id (most reliable)
                    existing_author = None
                    if semantic_scholar_id:
                        existing_author = Author.query.filter_by(semantic_scholar_id=semantic_scholar_id).first()
                    
                    # If not found by ID, try by name
                    if not existing_author:
                        existing_author = Author.query.filter_by(name=name).first()
                    
                    if existing_author:
                        # Update existing author with enriched data if it's better
                        # Update h_index if enriched data has higher value or existing is None
                        if enriched_h_index is not None:
                            if existing_author.h_index is None or enriched_h_index > existing_author.h_index:
                                existing_author.h_index = enriched_h_index
                        
                        # Update semantic_scholar_id if not set
                        if not existing_author.semantic_scholar_id and semantic_scholar_id:
                            existing_author.semantic_scholar_id = semantic_scholar_id
                        
                        # Update affiliation if not set
                        if not existing_author.affiliation and affiliation:
                            existing_author.affiliation = affiliation
                        
                        # Update last_updated timestamp
                        existing_author.last_updated = datetime.utcnow()
                        
                        paper.authors.append(existing_author)
                        processed_authors.append({
                            'name': existing_author.name,
                            'h_index': existing_author.h_index,
                            'updated': True
                        })
                    else:
                        # Create new author with enriched data from submission
                        new_author = Author(
                            name=name,
                            h_index=enriched_h_index,
                            semantic_scholar_id=semantic_scholar_id,
                            affiliation=affiliation
                        )
                        db.session.add(new_author)
                        paper.authors.append(new_author)
                        processed_authors.append({
                            'name': new_author.name,
                            'h_index': new_author.h_index,
                            'created': True
                        })
            
            submission.status = 'approved'
            db.session.commit()
            
            return {
                "message": "Conference created with papers and authors",
                "conference_id": conf.id,
                "authors_processed": processed_authors
            }
            
        submission.status = 'approved'
        db.session.commit()
        return {"message": "Submission approved"}


@blp.route("/admin/reject")
class RejectSubmission(MethodView):
    @jwt_required()
    @blp.arguments(SubmissionActionSchema)
    def post(self, action_data):
        if check_admin(): return {"message": "Admin required"}, 403
        
        submission_id = action_data['submission_id']
        submission = PendingSubmission.query.get_or_404(submission_id)
        
        if submission.status != 'pending':
            return {"message": "Submission already processed"}, 400
            
        submission.status = 'rejected'
        db.session.commit()
        return {"message": "Submission rejected", "id": submission_id}

