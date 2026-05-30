from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from backend.extensions import db
from backend.gamification_service import (
    activate_mission,
    clear_active_mission,
    complete_timer_session,
    get_active_mission,
    get_gamification_payload,
    get_or_create_stats,
    get_streak_payload,
    increment_mission_manual,
    stats_to_dict,
)
from backend.models import User, UserProfile, UserStats

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
    try:
        age = int(age_raw) if age_raw not in (None, "") else None
    except (ValueError, TypeError):
        return jsonify({"error": "Tuổi không hợp lệ."}), 400
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
    try:
        amount = int(data.get("amount") or 1)
    except (ValueError, TypeError):
        return jsonify({"error": "Số lượng không hợp lệ."}), 400
    result = increment_mission_manual(user_id, mission_id, amount)
    if "error" in result:
        return jsonify(result), 404
    return jsonify(result)


@user_bp.post("/missions/<int:mission_id>/cancel")
@jwt_required()
def mission_cancel(mission_id: int):
    user_id = int(get_jwt_identity())
    clear_active_mission(user_id)
    return jsonify({"message": "Đã hủy nhiệm vụ."})


@user_bp.post("/books/complete")
@jwt_required()
def book_complete():
    user_id = int(get_jwt_identity())
    stats = get_or_create_stats(user_id)
    stats.books_completed += 1
    db.session.commit()
    return jsonify({"message": "Đã ghi nhận hoàn thành sách.", "books_completed": stats.books_completed})


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
    try:
        minutes = int(data.get("minutes") or 0)
    except (ValueError, TypeError):
        return jsonify({"error": "Thời gian không hợp lệ."}), 400
    if minutes < 1:
        return jsonify({"error": "Thời gian không hợp lệ."}), 400
    journal = (data.get("journal") or "").strip()
    result = complete_timer_session(user_id, minutes, journal)
    if "error" in result:
        status = 400
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


@user_bp.get("/leaderboard")
def leaderboard():
    rows = (
        db.session.query(User, UserStats)
        .join(UserStats, User.id == UserStats.user_id)
        .order_by(UserStats.current_streak.desc(), UserStats.total_read_minutes.desc())
        .limit(50)
        .all()
    )
    entries = []
    for rank, (user, stats) in enumerate(rows, 1):
        initials = "".join(w[0].upper() for w in user.full_name.split() if w)[:2]
        entries.append({
            "rank": rank,
            "user_id": user.id,
            "full_name": user.full_name,
            "initials": initials,
            "current_streak": stats.current_streak or 0,
            "longest_streak": stats.longest_streak or 0,
            "total_read_minutes": stats.total_read_minutes or 0,
            "xp": stats.xp or 0,
        })
    return jsonify({"leaderboard": entries, "total": len(entries)})
