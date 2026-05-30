from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from backend.extensions import db
from backend.models import (
    Badge,
    Challenge,
    Mission,
    ReadingDay,
    UserBadge,
    UserChallengeProgress,
    UserMissionProgress,
    UserStats,
)

TZ = ZoneInfo("Asia/Ho_Chi_Minh")


def _today() -> date:
    return datetime.now(TZ).date()


def get_or_create_stats(user_id: int) -> UserStats:
    stats = UserStats.query.filter_by(user_id=user_id).first()
    if not stats:
        stats = UserStats(user_id=user_id)
        db.session.add(stats)
        db.session.commit()
    stats.ensure()
    return stats


def _mission_progress(user_id: int, mission_id: int) -> UserMissionProgress:
    row = UserMissionProgress.query.filter_by(
        user_id=user_id, mission_id=mission_id
    ).first()
    if not row:
        row = UserMissionProgress(user_id=user_id, mission_id=mission_id)
        db.session.add(row)
    return row


def _challenge_progress(user_id: int, challenge_id: int) -> UserChallengeProgress:
    row = UserChallengeProgress.query.filter_by(
        user_id=user_id, challenge_id=challenge_id
    ).first()
    if not row:
        row = UserChallengeProgress(user_id=user_id, challenge_id=challenge_id)
        db.session.add(row)
    return row


def activate_mission(user_id: int, mission_id: int) -> tuple[Mission | None, str | None]:
    mission = db.session.get(Mission, mission_id)
    if not mission:
        return None, "Nhiệm vụ không tồn tại."
    stats = get_or_create_stats(user_id)
    stats.active_mission_id = mission.id
    db.session.commit()
    return mission, None


def clear_active_mission(user_id: int):
    stats = get_or_create_stats(user_id)
    stats.active_mission_id = None
    db.session.commit()


def get_active_mission(user_id: int) -> Mission | None:
    stats = get_or_create_stats(user_id)
    if not stats.active_mission_id:
        return None
    return db.session.get(Mission, stats.active_mission_id)


def _word_count(text: str) -> int:
    return len(text.strip().split()) if text.strip() else 0


def complete_timer_session(user_id: int, minutes: int, journal: str = "") -> dict:
    stats = get_or_create_stats(user_id)
    mission = get_active_mission(user_id)
    if not mission:
        return {"error": "Chưa xác định nhiệm vụ."}

    if _word_count(journal) < 30:
        return {"error": "Vui lòng viết ít nhất 30 từ về cuốn sách bạn đã đọc hôm nay để ghi nhận."}

    required = mission.timer_minutes or 15
    if minutes < required:
        return {
            "error": f"Cần đọc ít nhất {required} phút để hoàn thành nhiệm vụ.",
            "required_minutes": required,
        }

    today = _today()
    _record_reading_day(user_id, today, minutes, journal)
    _update_streak(stats, today)

    progress = _mission_progress(user_id, mission.id)
    if not progress.completed:
        progress.current_value = min(mission.target_value, progress.current_value + 1)
        if progress.current_value >= mission.target_value:
            db.session.refresh(progress)
            if progress.completed:
                pass
            else:
                progress.completed = True
                if not progress.xp_claimed:
                    stats.xp += mission.xp_reward
                    progress.xp_claimed = True
                    _try_unlock_badges(user_id, stats)

    stats.total_read_minutes += minutes
    _sync_challenges(user_id, stats, minutes)
    stats.active_mission_id = None
    db.session.commit()

    return {
        "message": "Hoàn thành phiên đọc.",
        "xp_gained": mission.xp_reward if progress.completed else 0,
        "mission_completed": progress.completed,
        "stats": stats_to_dict(stats),
    }


def _record_reading_day(user_id: int, read_date: date, minutes: int, journal: str = ""):
    row = ReadingDay.query.filter_by(user_id=user_id, read_date=read_date).first()
    if row:
        row.minutes += minutes
        if journal:
            row.journal = journal
    else:
        db.session.add(ReadingDay(user_id=user_id, read_date=read_date, minutes=minutes, journal=journal or None))


def _update_streak(stats: UserStats, today: date):
    if stats.last_read_date == today:
        return
    if stats.last_read_date == today - timedelta(days=1):
        stats.current_streak += 1
    elif stats.last_read_date is None or stats.last_read_date < today - timedelta(days=1):
        stats.current_streak = 1
    stats.last_read_date = today
    if stats.current_streak > stats.longest_streak:
        stats.longest_streak = stats.current_streak

    streak_challenge = Challenge.query.filter_by(slug="streak-7").first()
    if streak_challenge:
        cp = _challenge_progress(stats.user_id, streak_challenge.id)
        cp.current_value = min(streak_challenge.target_value, stats.current_streak)
        if cp.current_value >= streak_challenge.target_value:
            cp.completed = True


def _sync_challenges(user_id: int, stats: UserStats, minutes: int):
    hours_challenge = Challenge.query.filter_by(slug="hours-10").first()
    if hours_challenge:
        cp = _challenge_progress(user_id, hours_challenge.id)
        cp.current_value = min(hours_challenge.target_value, stats.total_read_minutes)
        if cp.current_value >= hours_challenge.target_value:
            cp.completed = True

    books_challenge = Challenge.query.filter_by(slug="books-2-month").first()
    if books_challenge:
        cp = _challenge_progress(user_id, books_challenge.id)
        cp.current_value = min(books_challenge.target_value, stats.books_completed)
        if cp.current_value >= books_challenge.target_value:
            cp.completed = True


def _try_unlock_badges(user_id: int, stats: UserStats):
    completed_count = UserMissionProgress.query.filter_by(
        user_id=user_id, completed=True
    ).count()
    night_read_progress = UserMissionProgress.query.join(Mission).filter(
        UserMissionProgress.user_id == user_id,
        Mission.slug == "night-read",
        UserMissionProgress.completed == True,
    ).count()
    notes_progress = UserMissionProgress.query.join(Mission).filter(
        UserMissionProgress.user_id == user_id,
        Mission.slug == "save-quotes",
        UserMissionProgress.completed == True,
    ).count()
    rules = [
        ("newbie", completed_count >= 1),
        ("speed", stats.total_read_minutes >= 30),
        ("diamond", stats.current_streak >= 30),
        ("scholar", stats.books_completed >= 10),
        ("night-owl", night_read_progress >= 5),
        ("notekeeper", notes_progress >= 100),
    ]
    for slug, ok in rules:
        if not ok:
            continue
        badge = Badge.query.filter_by(slug=slug).first()
        if not badge:
            continue
        exists = UserBadge.query.filter_by(user_id=user_id, badge_id=badge.id).first()
        if not exists:
            db.session.add(UserBadge(user_id=user_id, badge_id=badge.id))


def increment_mission_manual(user_id: int, mission_id: int, amount: int = 1) -> dict:
    mission = db.session.get(Mission, mission_id)
    if not mission:
        return {"error": "Nhiệm vụ không tồn tại."}
    progress = _mission_progress(user_id, mission.id)
    stats = get_or_create_stats(user_id)
    if progress.completed:
        return {"message": "Nhiệm vụ đã hoàn thành.", "progress": _mission_dict(mission, progress)}

    progress.current_value = min(mission.target_value, progress.current_value + amount)
    xp = 0
    if progress.current_value >= mission.target_value:
        progress.completed = True
        if not progress.xp_claimed:
            xp = mission.xp_reward
            stats.xp += xp
            progress.xp_claimed = True
            _try_unlock_badges(user_id, stats)
    db.session.commit()
    return {"xp_gained": xp, "progress": _mission_dict(mission, progress)}


def stats_to_dict(stats: UserStats) -> dict:
    return {
        "current_streak": stats.current_streak,
        "longest_streak": stats.longest_streak,
        "total_read_minutes": stats.total_read_minutes,
        "books_completed": stats.books_completed,
        "xp": stats.xp,
        "active_mission_id": stats.active_mission_id,
    }


def _mission_dict(mission: Mission, progress: UserMissionProgress) -> dict:
    return {
        "id": mission.id,
        "slug": mission.slug,
        "title": mission.title,
        "description": mission.description,
        "mission_type": mission.mission_type,
        "target_value": mission.target_value,
        "current_value": progress.current_value,
        "xp_reward": mission.xp_reward,
        "timer_minutes": mission.timer_minutes,
        "icon": mission.icon,
        "completed": progress.completed,
        "xp_claimed": progress.xp_claimed,
    }


def _challenge_dict(challenge: Challenge, progress: UserChallengeProgress) -> dict:
    return {
        "id": challenge.id,
        "slug": challenge.slug,
        "title": challenge.title,
        "description": challenge.description,
        "period_label": challenge.period_label,
        "target_value": challenge.target_value,
        "current_value": progress.current_value,
        "xp_reward": challenge.xp_reward,
        "icon": challenge.icon,
        "completed": progress.completed,
    }


def _badge_dict(badge: Badge, unlocked: bool) -> dict:
    return {
        "id": badge.id,
        "slug": badge.slug,
        "title": badge.title,
        "description": badge.description,
        "icon": badge.icon,
        "unlock_hint": badge.unlock_hint,
        "unlocked": unlocked,
    }


def get_gamification_payload(user_id: int) -> dict:
    stats = get_or_create_stats(user_id)
    missions_out = []
    for mission in Mission.query.order_by(Mission.sort_order).all():
        progress = _mission_progress(user_id, mission.id)
        db.session.flush()
        missions_out.append(_mission_dict(mission, progress))

    challenges_out = []
    for challenge in Challenge.query.order_by(Challenge.sort_order).all():
        progress = _challenge_progress(user_id, challenge.id)
        db.session.flush()
        challenges_out.append(_challenge_dict(challenge, progress))

    unlocked_ids = {
        ub.badge_id for ub in UserBadge.query.filter_by(user_id=user_id).all()
    }
    badges_out = []
    for badge in Badge.query.order_by(Badge.sort_order).all():
        badges_out.append(_badge_dict(badge, badge.id in unlocked_ids))

    db.session.commit()
    return {
        "stats": stats_to_dict(stats),
        "missions": missions_out,
        "challenges": challenges_out,
        "badges": badges_out,
    }


def get_streak_payload(user_id: int, year: int, month: int) -> dict:
    stats = get_or_create_stats(user_id)
    from calendar import monthrange

    _, days_in_month = monthrange(year, month)
    start = date(year, month, 1)
    end = date(year, month, days_in_month)

    rows = ReadingDay.query.filter(
        ReadingDay.user_id == user_id,
        ReadingDay.read_date >= start,
        ReadingDay.read_date <= end,
    ).all()
    day_map = {r.read_date.day: r.minutes for r in rows}

    streak_challenge = Challenge.query.filter_by(slug="streak-7").first()
    milestone_current = stats.current_streak
    milestone_target = streak_challenge.target_value if streak_challenge else 7

    return {
        "stats": stats_to_dict(stats),
        "calendar": {
            "year": year,
            "month": month,
            "days": [
                {"day": d, "minutes": day_map.get(d, 0), "read": d in day_map}
                for d in range(1, days_in_month + 1)
            ],
        },
        "milestone": {
            "title": "Người Đọc Cần Cù",
            "description": f"Đạt chuỗi {milestone_target} ngày liên tiếp",
            "current": milestone_current,
            "target": milestone_target,
        },
    }
