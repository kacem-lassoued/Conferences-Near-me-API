from flask.views import MethodView
from flask_smorest import Blueprint
from models import PendingSubmission
from schemas import SubmissionSchema
from db import db
from services.scholar_service import get_author_h_index, classify_conference
import logging
from utils.errors import make_response, make_error_response, ExternalServiceError, ValidationError as UtilValidationError

logger = logging.getLogger(__name__)

blp = Blueprint("submissions", __name__, description="Anonymous submissions")

@blp.route("/submissions")
class SubmissionList(MethodView):
    @blp.arguments(SubmissionSchema)
    @blp.response(201)
    @blp.response(200)
    def get(self):
        """
        Get submission status by ID (for tracking).
        Query parameters: ?id=<submission_id> to get specific submission
        """
        from flask import request
        try:
            submission_id = request.args.get('id')
            if submission_id:
                submission = PendingSubmission.query.get(submission_id)
                if not submission:
                    return make_error_response(
                        UtilValidationError(f"Submission {submission_id} not found")
                    )
                return make_response(
                    data={
                        'id': submission.id,
                        'type': submission.type,
                        'status': submission.status,
                        'created_at': submission.created_at.isoformat() if submission.created_at else None,
                        'payload': submission.payload
                    },
                    message="Submission retrieved"
                )
            else:
                return make_error_response(
                    UtilValidationError("Please provide submission id in query: ?id=<id>")
                )
        except Exception as e:
            logger.error(f"Error retrieving submission: {e}", exc_info=True)
            return make_error_response(
                UtilValidationError(f"Error retrieving submission: {str(e)}")
            )

    @blp.arguments(SubmissionSchema)
    @blp.response(201)
    def post(self, submission_data):
        """
        Submit new conference with papers and authors.
        Enriches author data with h-index from Semantic Scholar.
        Handles timeout gracefully by storing submission immediately.
        """
        try:
            # Validate papers data
            papers = submission_data.get('papers', [])
            if not papers:
                return make_error_response(
                    UtilValidationError("At least one paper is required")
                )
            
            logger.info(f"Processing submission: {submission_data.get('name')} with {len(papers)} papers")
            
            # Enrich submission data with h-indexes (with timeout protection)
            enriched_papers = []
            enrichment_errors = []
            
            for idx, paper in enumerate(papers):
                try:
                    paper_title = paper.get('title', 'Unknown')
                    authors = paper.get('authors', [])
                    enriched_authors = []
                    
                    for author_name in authors:
                        try:
                            logger.debug(f"Enriching author: {author_name}")
                            author_data = get_author_h_index(author_name)
                            
                            if author_data:
                                enriched_authors.append({
                                    "name": author_data.get('name'),
                                    "h_index": author_data.get('h_index'),
                                    "semantic_scholar_id": author_data.get('semantic_scholar_id'),
                                    "affiliation": author_data.get('affiliation'),
                                    "citation_count": author_data.get('citation_count', 0),
                                    "match_confidence": author_data.get('match_confidence', 0.8)
                                })
                                logger.debug(f"✓ Enriched: {author_name} (h-index: {author_data.get('h_index')})")
                            else:
                                # Not found, store original name with null h-index
                                enriched_authors.append({
                                    "name": author_name,
                                    "h_index": None,
                                    "semantic_scholar_id": None,
                                    "affiliation": None,
                                    "match_confidence": 0.0,
                                    "note": "Not found in Semantic Scholar"
                                })
                                logger.warning(f"✗ Not found: {author_name}")
                        
                        except Exception as e:
                            logger.warning(f"Error enriching author {author_name}: {e}")
                            # Graceful fallback: store with error info
                            enriched_authors.append({
                                "name": author_name,
                                "h_index": None,
                                "error": str(e),
                                "note": "Error during enrichment"
                            })
                            enrichment_errors.append(f"{author_name}: {str(e)}")
                    
                    enriched_papers.append({
                        "title": paper_title,
                        "authors": authors,  # Keep original for reference
                        "enriched_authors": enriched_authors
                    })
                
                except Exception as e:
                    logger.error(f"Error processing paper {idx}: {e}")
                    enrichment_errors.append(f"Paper {idx}: {str(e)}")
                    # Still add paper with original data
                    enriched_papers.append({
                        "title": paper.get('title', 'Unknown'),
                        "authors": paper.get('authors', []),
                        "enriched_authors": []
                    })
            
            # Classify the conference based on papers
            conference_name = submission_data.get('name', '')
            classification_data = None
            classification_error = None
            
            try:
                logger.info(f"Classifying conference: {conference_name}")
                # Pass papers for better classification
                classification_data = classify_conference(
                    conference_name,
                    papers_data=[{'title': p.get('title')} for p in enriched_papers]
                )
                if classification_data:
                    logger.info(f"✓ Conference classified: {classification_data['primary']} "
                              f"(confidence: {classification_data['confidence']:.2%})")
                else:
                    logger.warning(f"Could not classify conference: {conference_name}")
                    classification_error = "Classification not available"
            except Exception as e:
                logger.warning(f"Error classifying conference: {e}")
                classification_error = str(e)
            
            # Prepare submission payload with enriched data
            submission_payload = {
                'name': submission_data.get('name'),
                'organizers': submission_data.get('organizers'),
                'location': submission_data.get('location'),
                'featured_workshops': submission_data.get('featured_workshops'),
                'papers': enriched_papers,
                'enrichment_status': {
                    'success': len(enrichment_errors) == 0,
                    'errors': enrichment_errors if enrichment_errors else None,
                    'total_authors_processed': sum(len(p.get('enriched_authors', [])) for p in enriched_papers)
                },
                'classification': classification_data,
                'classification_status': {
                    'classified': classification_data is not None,
                    'error': classification_error
                }
            }
            
            # Create pending submission
            submission = PendingSubmission(
                type='new_conference',
                payload=submission_payload
            )
            db.session.add(submission)
            db.session.commit()
            
            logger.info(f"Submission created with ID: {submission.id}")
            
            return make_response(
                data={
                    'submission_id': submission.id,
                    'status': 'pending',
                    'message': 'Conference submission received and will be reviewed',
                    'enrichment_summary': {
                        'total_papers': len(enriched_papers),
                        'total_authors': sum(len(p.get('authors', [])) for p in enriched_papers),
                        'successfully_enriched': sum(
                            len([a for a in p.get('enriched_authors', []) if a.get('h_index') is not None])
                            for p in enriched_papers
                        ),
                        'warnings': enrichment_errors if enrichment_errors else None
                    },
                    'classification': {
                        'primary': classification_data.get('primary') if classification_data else None,
                        'secondary': classification_data.get('secondary') if classification_data else [],
                        'confidence': classification_data.get('confidence') if classification_data else None,
                        'error': classification_error
                    }
                },
                message='Submission processed successfully',
                status_code=201
            )
        
        except Exception as e:
            logger.error(f"Unexpected error in submission: {e}", exc_info=True)
            return make_error_response(
                ExternalServiceError('submission', str(e))
            )

