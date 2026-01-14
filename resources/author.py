from flask.views import MethodView
from flask_smorest import Blueprint
from flask_jwt_extended import jwt_required, get_jwt
from models import Author, Paper
from schemas import AuthorSchema
from db import db
from services.scholar_service import get_author_h_index
from datetime import datetime
import logging
from utils.errors import make_response, make_error_response, NotFoundError, UnauthorizedError, format_pagination

logger = logging.getLogger(__name__)

blp = Blueprint("authors", __name__, description="Author and h-index operations")


@blp.route("/authors")
class AuthorList(MethodView):
    @blp.arguments(AuthorSchema(partial=True), location="query")
    @blp.response(200)
    def get(self, query_args):
        """
        Get all authors with their h-index and citation count.
        Query parameters: ?name=<search> or no params to list all.
        Returns list of authors sorted by h-index (highest first).
        Supports pagination with ?page=1&per_page=20
        """
        try:
            # Get pagination params
            page = query_args.get('page', 1) if query_args else 1
            per_page = query_args.get('per_page', 20) if query_args else 20
            
            # Validate pagination
            if page < 1:
                page = 1
            if per_page < 1 or per_page > 100:
                per_page = 20
            
            # Query with optional name filter
            query = Author.query
            
            # Search by name if provided
            if 'name' in query_args and query_args['name']:
                name = query_args['name'].strip()
                if len(name) >= 2:
                    query = query.filter(Author.name.ilike(f'%{name}%'))
            
            # Sort by h-index
            query = query.order_by(Author.h_index.desc().nullslast())
            pagination = query.paginate(page=page, per_page=per_page, error_out=False)
            
            authors_data = AuthorSchema(many=True).dump(pagination.items)
            
            return make_response(
                data=format_pagination(
                    items=authors_data,
                    total=pagination.total,
                    page=page,
                    per_page=per_page
                ),
                message=f"Retrieved {len(authors_data)} authors"
            )
        
        except Exception as e:
            logger.error(f"Error fetching authors: {e}", exc_info=True)
            return make_error_response(
                NotFoundError("Authors list")
            )


@blp.route("/authors/<int:author_id>")
class AuthorDetail(MethodView):
    @blp.response(200)
    def get(self, author_id):
        """Get detailed information about a specific author."""
        try:
            author = Author.query.get_or_404(author_id)
            author_data = AuthorSchema().dump(author)
            
            # Include related papers
            papers_data = [
                {
                    'id': paper.id,
                    'title': paper.title,
                    'conference_id': paper.conference_id,
                    'conference_name': paper.conference.name if paper.conference else None
                }
                for paper in author.papers
            ]
            
            return make_response(
                data={
                    'author': author_data,
                    'papers': papers_data,
                    'total_papers': len(papers_data)
                },
                message=f"Author details retrieved"
            )
        
        except Exception as e:
            logger.error(f"Error fetching author {author_id}: {e}", exc_info=True)
            return make_error_response(
                NotFoundError(f"Author {author_id}")
            )


@blp.route("/authors/search")
class AuthorSearch(MethodView):
    def get(self):
        """
        Search authors by name with pagination.
        Query parameters: ?name=<author_name>&page=1&per_page=20
        """
        from flask import request
        
        try:
            name = request.args.get('name', '').strip()
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 20))
            
            # Validate pagination
            if page < 1:
                page = 1
            if per_page < 1 or per_page > 100:
                per_page = 20
            
            if not name or len(name) < 2:
                return make_error_response(
                    NotFoundError("Please provide at least 2 characters for name search")
                )
            
            # Search in database first
            query = Author.query.filter(Author.name.ilike(f'%{name}%'))
            pagination = query.paginate(page=page, per_page=per_page, error_out=False)
            
            if pagination.total == 0:
                return make_response(
                    data=format_pagination([], 0, page, per_page),
                    message="No authors found"
                )
            
            authors_data = AuthorSchema(many=True).dump(pagination.items)
            
            return make_response(
                data=format_pagination(
                    items=authors_data,
                    total=pagination.total,
                    page=page,
                    per_page=per_page
                ),
                message=f"Found {pagination.total} author(s)"
            )
        
        except ValueError:
            return make_error_response(
                NotFoundError("Invalid pagination parameters")
            )
        except Exception as e:
            logger.error(f"Error searching authors: {e}", exc_info=True)
            return make_error_response(
                NotFoundError(f"Search error: {str(e)}")
            )


@blp.route("/authors/<int:author_id>/refresh")
class AuthorRefresh(MethodView):
    @jwt_required()
    def post(self, author_id):
        """
        Manually refresh an author's h-index from Semantic Scholar.
        Admin only.
        """
        try:
            # Check if user is admin
            claims = get_jwt()
            if claims.get("role") != "admin":
                return make_error_response(
                    UnauthorizedError("Admin access required to refresh author data")
                )
            
            author = Author.query.get_or_404(author_id)
            
            logger.info(f"Refreshing h-index for author: {author.name}")
            
            # Fetch fresh h-index data
            author_data = get_author_h_index(author.name)
            
            if author_data:
                # Update author information
                author.h_index = author_data.get('h_index')
                author.semantic_scholar_id = author_data.get('semantic_scholar_id')
                author.affiliation = author_data.get('affiliation')
                author.last_updated = datetime.utcnow()
                
                db.session.commit()
                
                logger.info(f"✓ Author refreshed: {author.name} (new h-index: {author.h_index})")
                
                return make_response(
                    data=AuthorSchema().dump(author),
                    message=f"Author h-index refreshed successfully"
                )
            else:
                logger.warning(f"Could not refresh author: {author.name}")
                return make_error_response(
                    NotFoundError(f"Could not fetch h-index from Semantic Scholar for {author.name}")
                )
        
        except Exception as e:
            logger.error(f"Error refreshing author {author_id}: {e}", exc_info=True)
            return make_error_response(
                NotFoundError(f"Error refreshing author: {str(e)}")
            )


@blp.route("/authors/<int:author_id>/papers")
class AuthorPapers(MethodView):
    def get(self, author_id):
        """
        Get all papers by a specific author with pagination.
        """
        try:
            from flask import request
            
            author = Author.query.get_or_404(author_id)
            
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 20))
            
            # Validate pagination
            if page < 1:
                page = 1
            if per_page < 1 or per_page > 100:
                per_page = 20
            
            # Get papers with pagination
            papers_query = Paper.query.filter_by(author_id=author_id) if hasattr(Paper, 'author_id') else author.papers
            
            papers_list = []
            for paper in author.papers:
                papers_list.append({
                    'id': paper.id,
                    'title': paper.title,
                    'conference_id': paper.conference_id,
                    'conference_name': paper.conference.name if paper.conference else None
                })
            
            # Manual pagination since we have list
            total = len(papers_list)
            start = (page - 1) * per_page
            end = start + per_page
            paginated_papers = papers_list[start:end]
            
            return make_response(
                data={
                    'author': AuthorSchema().dump(author),
                    'papers': format_pagination(
                        items=paginated_papers,
                        total=total,
                        page=page,
                        per_page=per_page
                    )
                },
                message=f"Retrieved {len(paginated_papers)} papers"
            )
        
        except Exception as e:
            logger.error(f"Error fetching papers for author {author_id}: {e}", exc_info=True)
            return make_error_response(
                NotFoundError(f"Papers for author {author_id}")
            )
