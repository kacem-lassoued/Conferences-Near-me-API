from flask.views import MethodView
from flask_smorest import Blueprint
from flask_jwt_extended import jwt_required, get_jwt
from models import Author, Paper
from schemas import AuthorSchema
from db import db
from services.scholar_service import get_author_h_index
from datetime import datetime

blp = Blueprint("authors", __name__, description="Author and h-index operations")


@blp.route("/authors")
class AuthorList(MethodView):
    @blp.response(200, AuthorSchema(many=True))
    def get(self):
        """
        Get all authors with their h-index.
        Returns list of authors sorted by h-index (highest first).
        """
        authors = Author.query.order_by(Author.h_index.desc().nullslast()).all()
        return authors


@blp.route("/authors/<int:author_id>")
class AuthorDetail(MethodView):
    @blp.response(200, AuthorSchema)
    def get(self, author_id):
        """Get detailed information about a specific author."""
        author = Author.query.get_or_404(author_id)
        return author


@blp.route("/authors/search")
class AuthorSearch(MethodView):
    def get(self):
        """
        Search authors by name.
        Query parameter: ?name=<author_name>
        """
        from flask import request
        
        name = request.args.get('name', '')
        
        if not name:
            return {"message": "Please provide 'name' query parameter"}, 400
        
        # Search in database first
        authors = Author.query.filter(Author.name.ilike(f'%{name}%')).all()
        
        if authors:
            return AuthorSchema(many=True).dump(authors)
        
        return {"message": "No authors found", "results": []}, 404


@blp.route("/authors/<int:author_id>/refresh")
class AuthorRefresh(MethodView):
    @jwt_required()
    def post(self, author_id):
        """
        Manually refresh an author's h-index from Semantic Scholar.
        Admin only.
        """
        # Check if user is admin
        claims = get_jwt()
        if claims.get("role") != "admin":
            return {"message": "Admin required"}, 403
        
        author = Author.query.get_or_404(author_id)
        
        # Fetch fresh h-index data
        author_data = get_author_h_index(author.name)
        
        if author_data:
            # Update author information
            author.h_index = author_data.get('h_index')
            author.semantic_scholar_id = author_data.get('semantic_scholar_id')
            author.affiliation = author_data.get('affiliation')
            author.last_updated = datetime.utcnow()
            
            db.session.commit()
            
            return {
                "message": "Author h-index refreshed",
                "author": AuthorSchema().dump(author)
            }
        else:
            return {"message": "Could not fetch h-index from Semantic Scholar"}, 404


@blp.route("/authors/<int:author_id>/papers")
class AuthorPapers(MethodView):
    def get(self, author_id):
        """Get all papers by a specific author."""
        author = Author.query.get_or_404(author_id)
        
        papers_list = []
        for paper in author.papers:
            papers_list.append({
                'id': paper.id,
                'title': paper.title,
                'conference_id': paper.conference_id,
                'conference_name': paper.conference.name if paper.conference else None
            })
        
        return {
            'author': AuthorSchema().dump(author),
            'papers': papers_list,
            'total_papers': len(papers_list)
        }
