import random
from datetime import datetime, timedelta, timezone

from backend.extensions import db
from backend.models import Badge, BookComment, Challenge, Mission, User, UserStats


def seed_catalog():
    _seed_missions()
    _seed_challenges()
    _seed_badges()
    _seed_leaderboard_users()
    _seed_book_comments()
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


def _seed_leaderboard_users():
    if User.query.filter(User.email.like("%@bookmatch.vn")).count() > 0:
        return
    from backend.auth_service import hash_password
    password = hash_password("Reader@123")
    fake_users = [
        ("Nguyễn Văn An", 120, 150, 4800, 12800),
        ("Trần Thị Bình", 89, 95, 3600, 9600),
        ("Lê Hoàng Cường", 65, 80, 2400, 7200),
        ("Phạm Minh Đức", 45, 60, 1800, 5400),
        ("Hoàng Thị Em", 30, 45, 1200, 3800),
        ("Vũ Quốc Huy", 21, 30, 900, 2500),
        ("Đặng Thanh Hương", 18, 25, 750, 2100),
        ("Bùi Thị Hồng", 14, 20, 600, 1800),
        ("Đỗ Văn Khanh", 10, 15, 450, 1200),
        ("Ngô Thị Lan", 7, 12, 300, 800),
        ("Dương Văn Minh", 5, 8, 200, 600),
        ("Hồ Thị Ngọc", 3, 5, 100, 300),
        ("Mai Văn Phúc", 1, 3, 50, 150),
        ("Lý Thị Quyên", 1, 2, 30, 100),
    ]
    now = datetime.now(timezone.utc)
    for i, (name, streak, longest, minutes, xp) in enumerate(fake_users, 1):
        email = f"reader{i}@bookmatch.vn"
        user = User(
            email=email,
            password_hash=password,
            full_name=name,
            created_at=now,
        )
        db.session.add(user)
        db.session.flush()
        db.session.add(UserStats(
            user_id=user.id,
            current_streak=streak,
            longest_streak=longest,
            total_read_minutes=minutes,
            xp=xp,
        ))


COMMENT_TEMPLATES = [
    "Một cuốn sách tuyệt vời! Tôi đã học được rất nhiều điều từ nó.",
    "Đây là một trong những cuốn sách hay nhất tôi từng đọc. Rất đáng để đọc.",
    "Nội dung sâu sắc và ý nghĩa. Tôi sẽ đọc lại nhiều lần.",
    "Sách viết rất dễ hiểu, phù hợp cho người mới bắt đầu.",
    "Tác giả có cách diễn đạt rất cuốn hút. Đọc một lần không thể dừng lại.",
    "Một góc nhìn hoàn toàn mới mẻ về vấn đề. Rất khai sáng.",
    "Tôi đã áp dụng những kiến thức từ cuốn sách này vào thực tế và thấy hiệu quả bất ngờ.",
    "Nên đọc ít nhất một lần trong đời. Cuốn sách thay đổi tư duy.",
    "Sách hay nhưng cần tập trung để hiểu hết được những ý tưởng chính.",
    "Rất thực tế và dễ áp dụng. Tôi giới thiệu cho tất cả bạn bè của mình.",
    "Văn phong mượt mà, dịch thuật tốt. Nội dung cuốn hút từ đầu đến cuối.",
    "Một tác phẩm kinh điển không thể bỏ qua. Giá trị vượt thời gian.",
    "Đây là lần thứ hai tôi đọc cuốn sách này và vẫn tìm thấy những điều mới mẻ.",
    "Sách giúp tôi thay đổi cách nhìn nhận vấn đề. Thực sự hữu ích.",
    "Nếu bạn chỉ đọc một cuốn sách trong năm nay, hãy đọc cuốn này.",
    "Tôi yêu cách tác giả kết hợp giữa lý thuyết và thực hành.",
    "Cuốn sách mở ra một thế giới mới mà tôi chưa từng biết đến.",
    "Đọc xong tôi cảm thấy được truyền cảm hứng rất lớn.",
    "Mỗi chương đều chứa đựng những bài học quý giá.",
    "Tôi ước mình đã đọc cuốn sách này sớm hơn.",
    "Kiến thức trong sách được trình bày rất khoa học và logic.",
    "Một cuốn sách chữa lành tâm hồn. Đọc xong thấy nhẹ nhàng hơn.",
    "Các ví dụ trong sách rất thực tế và dễ hình dung.",
    "Sách phù hợp cho mọi lứa tuổi. Nội dung nhân văn và sâu sắc.",
    "Tôi đã giới thiệu cuốn này cho cả gia đình và ai cũng thích.",
]

COMMENT_BOOK_IDS = list(range(1, 190))


def _seed_book_comments():
    if BookComment.query.count() > 0:
        return
    users = User.query.all()
    if not users:
        return
    now = datetime.now(timezone.utc)
    chosen_books = random.sample(COMMENT_BOOK_IDS, min(80, len(COMMENT_BOOK_IDS)))
    for book_id in chosen_books:
        num_comments = random.randint(2, 5)
        commenters = random.sample(users, min(num_comments, len(users)))
        for i, user in enumerate(commenters):
            content = random.choice(COMMENT_TEMPLATES)
            created_at = now - timedelta(days=random.randint(0, 60), hours=random.randint(0, 23))
            db.session.add(BookComment(
                book_id=book_id,
                user_id=user.id,
                content=content,
                created_at=created_at,
            ))
