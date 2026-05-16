from datetime import date, datetime, timezone

from backend.extensions import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    profile = db.relationship("UserProfile", back_populates="user", uselist=False)
    stats = db.relationship("UserStats", back_populates="user", uselist=False)

    def to_public_dict(self) -> dict:
        return {
            "id": self.id,
            "email": self.email,
            "full_name": self.full_name,
            "created_at": self.created_at.isoformat(),
        }


class UserProfile(db.Model):
    __tablename__ = "user_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    age = db.Column(db.Integer, nullable=True)
    interests = db.Column(db.String(500), nullable=True)
    mood = db.Column(db.String(200), nullable=True)
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    user = db.relationship("User", back_populates="profile")

    def to_dict(self) -> dict:
        return {
            "age": self.age,
            "interests": self.interests or "",
            "mood": self.mood or "",
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class UserStats(db.Model):
    __tablename__ = "user_stats"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    current_streak = db.Column(db.Integer, default=0, nullable=False)
    longest_streak = db.Column(db.Integer, default=0, nullable=False)
    total_read_minutes = db.Column(db.Integer, default=0, nullable=False)
    books_completed = db.Column(db.Integer, default=0, nullable=False)
    xp = db.Column(db.Integer, default=0, nullable=False)
    active_mission_id = db.Column(db.Integer, db.ForeignKey("missions.id"), nullable=True)
    last_read_date = db.Column(db.Date, nullable=True)

    user = db.relationship("User", back_populates="stats")
    active_mission = db.relationship("Mission", foreign_keys=[active_mission_id])

    def ensure(self):
        if self.current_streak is None:
            self.current_streak = 0
        if self.longest_streak is None:
            self.longest_streak = 0


class Mission(db.Model):
    __tablename__ = "missions"

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(64), unique=True, nullable=False)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(300), nullable=True)
    mission_type = db.Column(db.String(32), default="daily", nullable=False)
    target_value = db.Column(db.Integer, default=1, nullable=False)
    xp_reward = db.Column(db.Integer, default=50, nullable=False)
    timer_minutes = db.Column(db.Integer, nullable=True)
    icon = db.Column(db.String(64), default="menu_book", nullable=False)
    sort_order = db.Column(db.Integer, default=0, nullable=False)


class Challenge(db.Model):
    __tablename__ = "challenges"

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(64), unique=True, nullable=False)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(300), nullable=True)
    period_label = db.Column(db.String(32), default="Tuần", nullable=False)
    target_value = db.Column(db.Integer, default=7, nullable=False)
    xp_reward = db.Column(db.Integer, default=500, nullable=False)
    icon = db.Column(db.String(64), default="emoji_events", nullable=False)
    sort_order = db.Column(db.Integer, default=0, nullable=False)


class Badge(db.Model):
    __tablename__ = "badges"

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(64), unique=True, nullable=False)
    title = db.Column(db.String(64), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    icon = db.Column(db.String(64), default="workspace_premium", nullable=False)
    unlock_hint = db.Column(db.String(200), nullable=True)
    sort_order = db.Column(db.Integer, default=0, nullable=False)


class UserMissionProgress(db.Model):
    __tablename__ = "user_mission_progress"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    mission_id = db.Column(db.Integer, db.ForeignKey("missions.id"), nullable=False)
    current_value = db.Column(db.Integer, default=0, nullable=False)
    completed = db.Column(db.Boolean, default=False, nullable=False)
    xp_claimed = db.Column(db.Boolean, default=False, nullable=False)

    __table_args__ = (db.UniqueConstraint("user_id", "mission_id", name="uq_user_mission"),)

    mission = db.relationship("Mission")


class UserChallengeProgress(db.Model):
    __tablename__ = "user_challenge_progress"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    challenge_id = db.Column(db.Integer, db.ForeignKey("challenges.id"), nullable=False)
    current_value = db.Column(db.Integer, default=0, nullable=False)
    completed = db.Column(db.Boolean, default=False, nullable=False)

    __table_args__ = (db.UniqueConstraint("user_id", "challenge_id", name="uq_user_challenge"),)

    challenge = db.relationship("Challenge")


class UserBadge(db.Model):
    __tablename__ = "user_badges"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    badge_id = db.Column(db.Integer, db.ForeignKey("badges.id"), nullable=False)
    unlocked_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    __table_args__ = (db.UniqueConstraint("user_id", "badge_id", name="uq_user_badge"),)

    badge = db.relationship("Badge")


class ReadingDay(db.Model):
    __tablename__ = "reading_days"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    read_date = db.Column(db.Date, nullable=False)
    minutes = db.Column(db.Integer, default=0, nullable=False)

    __table_args__ = (db.UniqueConstraint("user_id", "read_date", name="uq_user_read_date"),)
