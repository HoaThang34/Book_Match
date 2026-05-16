from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from backend.extensions import db
from backend.gamification_service import (
    activate_mission,
    complete_timer_session,
    get_active_mission,
    get_gamification_payload,
    get_or_create_stats,
    get_streak_payload,
    increment_mission_manual,
    stats_to_dict,
)
from backend.models import UserProfile

user_bp = Blueprint("user", __name__, url_prefix="/api/user")


def _json_body() -> dict:
    if not request.is_json:
        return {}
    data = request.get_json(silent=True)
    return data if isinstance(data, dict) else {}


@user_bp.get("/stats")
@jwt_required()
def user_stats():
    user_id = int(get_jwt_identity())
    stats = get_or_create_stats(user_id)
    return jsonify({"stats": stats_to_dict(stats)})


@user_bp.get("/profile")
@jwt_required()
def get_profile():
    user_id = int(get_jwt_identity())
    profile = UserProfile.query.filter_by(user_id=user_id).first()
    if not profile:
        return jsonify({"profile": None})
    return jsonify({"profile": profile.to_dict()})


@user_bp.put("/profile")
@jwt_required()
def update_profile():
    user_id = int(get_jwt_identity())
    data = _json_body()
    age_raw = data.get("age")
    age = int(age_raw) if age_raw not in (None, "") else None
    if age is not None and (age < 5 or age > 120):
        return jsonify({"error": "Tuổi không hợp lệ."}), 400

    profile = UserProfile.query.filter_by(user_id=user_id).first()
    if not profile:
        profile = UserProfile(user_id=user_id)
        db.session.add(profile)

    profile.age = age
    profile.interests = (data.get("interests") or "").strip()[:500] or None
    profile.mood = (data.get("mood") or "").strip()[:200] or None
    db.session.commit()
    return jsonify({"profile": profile.to_dict()})


@user_bp.get("/missions")
@jwt_required()
def missions():
    user_id = int(get_jwt_identity())
    return jsonify(get_gamification_payload(user_id))


@user_bp.post("/missions/<int:mission_id>/activate")
@jwt_required()
def mission_activate(mission_id: int):
    user_id = int(get_jwt_identity())
    mission, error = activate_mission(user_id, mission_id)
    if error:
        return jsonify({"error": error}), 404
    return jsonify(
        {
            "message": "Đã chọn nhiệm vụ.",
            "mission": {
                "id": mission.id,
                "title": mission.title,
                "timer_minutes": mission.timer_minutes or 15,
            },
        }
    )


@user_bp.post("/missions/<int:mission_id>/progress")
@jwt_required()
def mission_progress(mission_id: int):
    user_id = int(get_jwt_identity())
    data = _json_body()
    amount = int(data.get("amount") or 1)
    result = increment_mission_manual(user_id, mission_id, amount)
    if "error" in result:
        return jsonify(result), 404
    return jsonify(result)


@user_bp.get("/timer/active")
@jwt_required()
def timer_active():
    user_id = int(get_jwt_identity())
    mission = get_active_mission(user_id)
    if not mission:
        return jsonify({"active": False, "mission": None})
    return jsonify(
        {
            "active": True,
            "mission": {
                "id": mission.id,
                "title": mission.title,
                "timer_minutes": mission.timer_minutes or 15,
            },
        }
    )


@user_bp.post("/timer/complete")
@jwt_required()
def timer_complete():
    user_id = int(get_jwt_identity())
    data = _json_body()
    minutes = int(data.get("minutes") or 0)
    if minutes < 1:
        return jsonify({"error": "Thời gian không hợp lệ."}), 400
    result = complete_timer_session(user_id, minutes)
    if "error" in result:
        status = 400 if "phút" in result["error"] else 409
        return jsonify(result), status
    return jsonify(result)


@user_bp.get("/streak")
@jwt_required()
def streak():
    user_id = int(get_jwt_identity())
    year = request.args.get("year", type=int)
    month = request.args.get("month", type=int)
    from datetime import datetime

    try:
        from zoneinfo import ZoneInfo

        now = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh"))
    except Exception:
        now = datetime.now()
    year = year or now.year
    month = month or now.month
    return jsonify(get_streak_payload(user_id, year, month))
