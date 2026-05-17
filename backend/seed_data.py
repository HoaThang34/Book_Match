from backend.extensions import db
from backend.models import Badge, Challenge, Mission


def seed_catalog():
    _seed_missions()
    _seed_challenges()
    _seed_badges()
    db.session.commit()


def _seed_missions():
    if Mission.query.count() > 0:
        return
    missions = [
        ("read-15-min", "Đọc 15 phút", "Đọc tập trung 15 phút", "daily", 1, 50, 15, "check_circle", 1),
        ("finish-chapter", "Hoàn thành 1 chương", "Đọc xong một chương sách", "daily", 1, 100, None, "menu_book", 2),
        ("save-quotes", "Lưu 5 trích dẫn", "Ghi nhớ 5 câu trích dẫn hay", "daily", 5, 75, None, "format_quote", 3),
        ("morning-read", "Đọc buổi sáng", "Đọc trước 10h sáng", "daily", 1, 40, 10, "wb_sunny", 4),
        ("night-read", "Đọc buổi tối", "Đọc sau 21h", "daily", 1, 40, 10, "nightlight_round", 5),
        ("focus-25", "Focus 25 phút", "Phiên tập trung Pomodoro", "daily", 1, 80, 25, "timer", 6),
        ("pages-20", "Đọc 20 trang", "Hoàn thành 20 trang", "daily", 20, 90, None, "auto_stories", 7),
        ("share-book", "Chia sẻ cuốn sách", "Giới thiệu sách cho bạn bè", "daily", 1, 30, None, "share", 8),
        ("new-genre", "Thử thể loại mới", "Đọc thể loại chưa từng đọc", "weekly", 1, 120, None, "explore", 9),
        ("review-book", "Viết nhận xét ngắn", "Đánh giá cuốn đang đọc", "weekly", 1, 60, None, "rate_review", 10),
    ]
    for row in missions:
        db.session.add(
            Mission(
                slug=row[0],
                title=row[1],
                description=row[2],
                mission_type=row[3],
                target_value=row[4],
                xp_reward=row[5],
                timer_minutes=row[6],
                icon=row[7],
                sort_order=row[8],
            )
        )


def _seed_challenges():
    if Challenge.query.count() > 0:
        return
    challenges = [
        ("streak-7", "Đọc 7 ngày liên tiếp", "Duy trì thói quen đọc mỗi ngày", "Tuần", 7, 500, "local_fire_department", 1),
        ("books-2-month", "Hoàn thành 2 cuốn sách", "Đọc trọn 2 cuốn trong tháng", "Tháng", 2, 1000, "library_books", 2),
        ("hours-10", "Tích lũy 10 giờ đọc", "Đọc tổng 600 phút trong tháng", "Tháng", 600, 800, "schedule", 3),
    ]
    for row in challenges:
        db.session.add(
            Challenge(
                slug=row[0],
                title=row[1],
                description=row[2],
                period_label=row[3],
                target_value=row[4],
                xp_reward=row[5],
                icon=row[6],
                sort_order=row[7],
            )
        )


def _seed_badges():
    if Badge.query.count() > 0:
        return
    badges = [
        ("newbie", "Người Mới", "Hoàn thành nhiệm vụ đầu tiên", "auto_awesome", "Hoàn thành 1 nhiệm vụ", 1),
        ("speed", "Tốc Độ", "Đọc 30 phút trong một phiên", "speed", "Focus 30 phút một lần", 2),
        ("night-owl", "Cú Đêm", "Đọc 5 buổi tối", "nightlight_round", "5 lần đọc buổi tối", 3),
        ("scholar", "Học Giả", "Hoàn thành 10 cuốn sách", "library_add_check", "Đọc 10 cuốn", 4),
        ("notekeeper", "Ghi Chép", "Lưu 100 trích dẫn", "edit_note", "100 trích dẫn", 5),
        ("diamond", "Kim Cương", "Chuỗi 30 ngày liên tiếp", "diamond", "Streak 30 ngày", 6),
    ]
    for row in badges:
        db.session.add(
            Badge(
                slug=row[0],
                title=row[1],
                description=row[2],
                icon=row[3],
                unlock_hint=row[4],
                sort_order=row[5],
            )
        )
