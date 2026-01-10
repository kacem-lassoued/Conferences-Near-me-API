from flask.views import MethodView
from flask_smorest import Blueprint
from models import PendingSubmission
from schemas import SubmissionSchema
from db import db
from services.scholar_service import get_author_h_index

blp = Blueprint("submissions", __name__, description="Anonymous submissions")

@blp.route("/submissions")
class SubmissionList(MethodView):
    @blp.arguments(SubmissionSchema)
    @blp.response(201, SubmissionSchema)
    def post(self, submission_data):
        # Enrich submission data with h-indexes immediately
        papers = submission_data.get('papers', [])
        
        for paper in papers:
            authors = paper.get('authors', [])
            enriched_authors = []
            
            for author_name in authors:
                try:
                    # Fetch h-index
                    print(f"Fetching h-index for: {author_name}")
                    author_data = get_author_h_index(author_name)
                    
                    if author_data:
                        enriched_authors.append({
                            "name": author_data.get('name'),
                            "h_index": author_data.get('h_index'),
                            "semantic_scholar_id": author_data.get('semantic_scholar_id'),
                            "affiliation": author_data.get('affiliation')
                        })
                    else:
                        # Fallback if not found
                        enriched_authors.append({
                            "name": author_name,
                            "h_index": None,
                            "note": "Not found in Semantic Scholar"
                        })
                except Exception as e:
                    print(f"Error fetching h-index for {author_name}: {e}")
                    enriched_authors.append({"name": author_name, "error": str(e)})
            
            # Replace users original author list with enriched list
            # We add a new field 'enriched_authors' to avoid schema validation errors if we changed 'authors' type
            paper['enriched_authors'] = enriched_authors

        # Create a pending submission with the enriched data
        submission = PendingSubmission(
            type='new_conference',
            payload=submission_data
        )
        db.session.add(submission)
        db.session.commit()
        return submission_data

