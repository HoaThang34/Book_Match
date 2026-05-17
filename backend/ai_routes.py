from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from backend.ai_service import get_book_recommendations
from backend.extensions import db, limiter
from backend.models import UserProfile, UserStats
from backend.ollama_service import OllamaError

ai_bp = Blueprint("ai", __name__, url_prefix="/api/ai")


@ai_bp.get("/recommendations")
@jwt_required()
@limiter.limit("30 per hour")
def recommendations():
    user_id = int(get_jwt_identity())
    profile = UserProfile.query.filter_by(user_id=user_id).first()
    stats = UserStats.query.filter_by(user_id=user_id).first()

    try:
        result = get_book_recommendations(profile, stats)
    except OllamaError as exc:
        return jsonify({"error": str(exc)}), 503

    return jsonify({"recommendations": result["recommendations"], "comment": result["comment"]})


@ai_bp.post("/recommendations/refresh")
@jwt_required()
@limiter.limit("20 per hour")
def recommendations_refresh():
    """Generate new recommendations that don't overlap with the given exclude_titles list."""
    user_id = int(get_jwt_identity())
    profile = UserProfile.query.filter_by(user_id=user_id).first()
    stats = UserStats.query.filter_by(user_id=user_id).first()

    body = request.get_json(silent=True) or {}
    exclude_titles = body.get("exclude_titles", [])
    if not isinstance(exclude_titles, list):
        exclude_titles = []

    try:
        result = get_book_recommendations(profile, stats, exclude_titles=exclude_titles)
    except OllamaError as exc:
        return jsonify({"error": str(exc)}), 503

    return jsonify({"recommendations": result["recommendations"], "comment": result["comment"]})
