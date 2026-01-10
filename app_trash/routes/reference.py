from flask import Blueprint, jsonify
from app.models.conference import Theme, Ranking
from app.extensions import db

reference_bp = Blueprint('reference', __name__)

@reference_bp.route('/themes', methods=['GET'])
def get_themes():
    """
    Get all Themes
    ---
    tags:
      - Reference
    responses:
      200:
        description: List of themes
    """
    themes = Theme.query.all()
    return jsonify([t.to_dict() for t in themes])

@reference_bp.route('/rankings', methods=['GET'])
def get_rankings():
    """
    Get available Ranking Systems
    ---
    tags:
      - Reference
    responses:
      200:
        description: List of ranking systems
    """
    # distinct ranking names
    # SQLAlchemy < 2.0 style
    rankings = db.session.query(Ranking.ranking_name).distinct().all()
    return jsonify([r[0] for r in rankings])
