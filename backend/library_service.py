from pathlib import Path
from docx import Document

CONTENTS_DIR = Path(__file__).resolve().parent.parent / "library" / "contents"

CATEGORIES = [
    {
        "slug": "van-hoc",
        "title": "Văn học",
        "icon": "menu_book",
        "keywords": [
            "1984", "Anne tóc đỏ", "Around the World", "Bên thắng cuộc", "Charlie",
            "Cho tôi xin", "Dế mèn", "Harry Potter", "Hoàng tử bé", "Không gia đình",
            "Kiêu hãnh", "Kính vạn hoa", "Mắt biếc", "Nhà giả kim", "Những người khốn khổ",
            "Peter Pan", "Pippi", "Rừng Na Uy", "Sherlock Holmes", "Trại súc vật",
            "Totto-chan", "Những tấm lòng cao cả", "On the Road", "Eat Pray Love",
            "Into the Wild", "Vagabonding", "Xách ba lô", "Wild",
        ],
    },
    {
        "slug": "kinh-te",
        "title": "Kinh tế - Kinh doanh",
        "icon": "attach_money",
        "keywords": [
            "Blue Ocean", "Chiến tranh tiền tệ", "Dạy con làm giàu", "Cha giàu",
            "Kinh tế vĩ mô", "Kinh tế vi mô", "Khởi nghiệp", "Người giàu có nhất",
            "Nguyên lý kế toán", "Quản trị học", "Quốc gia khởi nghiệp",
            "Tâm lý học về tiền", "Think and Grow Rich", "Tư bản", "Từ tốt đến vĩ đại",
            "Tư duy nhanh", "Đắc nhân tâm",
        ],
    },
    {
        "slug": "phat-trien",
        "title": "Phát triển bản thân",
        "icon": "psychology",
        "keywords": [
            "7 thói quen", "Atomic Habits", "Can't Hurt Me", "Dám bị ghét", "Deep Work",
            "Ikigai", "Kỹ năng đàm phán", "Kỹ năng giao tiếp", "Kỹ năng làm việc nhóm",
            "Kỹ năng quản lý thời gian", "Leadership", "Nghệ thuật thuyết trình",
            "Nghệ thuật tối giản", "Nghệ thuật yêu", "Quẳng gánh lo",
            "Sức mạnh của hiện tại", "The First 90 Days", "The Mountain Is You",
            "Tuổi trẻ đáng giá", "Tôi tài giỏi", "Yêu những điều", "Đi tìm lẽ sống",
            "Đời ngắn", "CV xin việc", "Hiểu về trái tim", "Không diệt không sinh",
            "Phương pháp nghiên cứu", "Steal Like an Artist", "Show Your Work",
            "Sống như anh", "Đời ngắn",
        ],
    },
    {
        "slug": "khoa-hoc",
        "title": "Khoa học - Triết học",
        "icon": "lightbulb",
        "keywords": [
            "Astrophysics", "Brief Answers", "Cosmos", "Gene vị kỷ", "Homo Deus",
            "Sapiens", "Sophie's World", "Thus Spoke Zarathustra", "Vũ trụ trong vỏ hạt dẻ",
            "Cộng hòa", "Đạo Đức Kinh", "Kinh Phật", "Kinh Thánh", "Binh pháp Tôn Tử",
            "Meditations", "Lược sử thời gian", "Nguồn gốc các loài", "Súng vi trùng",
            "The Elegant Universe", "Cơ thể tự chữa lành", "Gut", "Healing Foods",
            "Sức mạnh của giấc ngủ", "The Body", "The Cancer Code", "Why We Sleep",
            "Y học dinh dưỡng", "Ăn gì không chết", "Xã hội học đại cương",
            "Giáo trình tâm lý học", "Lịch Sử Thế Giới", "Việt Nam Sử Lược",
            "Đường Kách Mệnh", "Những con đường hồi giáo",
        ],
    },
    {
        "slug": "cong-nghe",
        "title": "Công nghệ",
        "icon": "computer",
        "keywords": [
            "AI 2041", "Clean Code", "Code Dạo", "Deep Learning", "Design Patterns",
            "Cybersecurity", "Introduction to Algorithms", "Python Crash Course",
            "Scrum Guide", "The Pragmatic Programmer", "The Design of Everyday Things",
        ],
    },
    {
        "slug": "marketing",
        "title": "Marketing - Truyền thông",
        "icon": "campaign",
        "keywords": [
            "Contagious", "Content Marketing", "Digital Marketing", "Giáo trình Marketing",
            "Hacking Growth", "Lý thuyết truyền thông", "Made to Stick", "Marketing 4.0",
            "Ogilvy on Advertising", "Positioning", "PR thực chiến", "Purple Cow",
            "Quan hệ công chúng", "The Copywriter's Handbook", "This is Marketing",
            "Truyền thông không chỉ là quảng cáo",
        ],
    },
    {
        "slug": "ngon-ngu",
        "title": "Ngôn ngữ - Luyện thi",
        "icon": "language",
        "keywords": [
            "4000 Essential", "30 đề minh họa", "Bứt phá IELTS", "Complete TOEIC",
            "Destination B2", "English Grammar", "Giải đề THPT", "Hack Não 1500",
            "Hack Não Ngữ Pháp", "IELTS Cambridge", "JLPT N3", "Kanji Look and Learn",
            "Luyện thi HSK", "Mindmap English", "Oxford Word Skills", "SAT Prep",
            "TOEIC Analyst", "Tự học giao tiếp",
        ],
    },
    {
        "slug": "nghe-thuat",
        "title": "Nghệ thuật - Ẩm thực",
        "icon": "palette",
        "keywords": [
            "Art & Fear", "Asian Desserts", "Bếp nhà", "Chocolate", "Color and Light",
            "Mastering the Art of French Cooking", "Minh triết trong ăn uống",
            "Món ngon Việt Nam", "Nghệ thuật pha chế", "Professional Baking",
            "Salt Fat Acid Heat", "The Animator's Survival Kit", "The Cake Bible",
            "The Food Lab", "The Story of Art", "Ways of Seeing", "Điện ảnh là gì",
        ],
    },
    {
        "slug": "truyen-tranh",
        "title": "Truyện tranh",
        "icon": "auto_stories",
        "keywords": [
            "Attack on Titan", "Blue Lock", "Conan", "Demon Slayer", "Doraemon",
            "Jujutsu Kaisen", "Naruto", "One Piece", "Slam Dunk", "Tokyo Revengers",
        ],
    },
    {
        "slug": "hoi-ky",
        "title": "Hồi ký - Tiểu sử",
        "icon": "history_edu",
        "keywords": [
            "Becoming", "Diary of a Young Girl", "Educated", "Elon Musk",
            "Hồi ký Nguyễn Hiến Lê", "Long Walk to Freedom", "Steve Jobs",
            "When Breath Becomes Air",
        ],
    },
]


def _categorize(title: str) -> dict:
    for cat in CATEGORIES:
        for kw in cat["keywords"]:
            if kw.lower() in title.lower():
                return {"slug": cat["slug"], "title": cat["title"], "icon": cat["icon"]}
    return {"slug": "khac", "title": "Khác", "icon": "book"}


def _read_docx(path: Path) -> str:
    doc = Document(str(path))
    return "\n".join(p.text for p in doc.paragraphs)


def _get_description(text: str, max_chars: int = 300) -> str:
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    desc = ""
    for line in lines[1:]:
        if len(desc) + len(line) > max_chars:
            desc += " " + line[: max_chars - len(desc)]
            break
        desc += " " + line if desc else line
    return desc.strip()[:max_chars]


_cache = None


def get_library(force_refresh: bool = False) -> list[dict]:
    global _cache
    if _cache is not None and not force_refresh:
        return _cache

    books = []
    for path in sorted(CONTENTS_DIR.glob("*.docx")):
        title = path.stem
        try:
            text = _read_docx(path)
        except Exception:
            text = ""
        category = _categorize(title)
        desc = _get_description(text)
        books.append({
            "id": len(books) + 1,
            "title": title,
            "category": category,
            "description": desc,
            "file_path": str(path),
        })

    _cache = books
    return books


def get_book_by_id(book_id: int) -> dict | None:
    books = get_library()
    for b in books:
        if b["id"] == book_id:
            return b
    return None


def get_book_content(book_id: int) -> str | None:
    book = get_book_by_id(book_id)
    if not book:
        return None
    try:
        path = Path(book["file_path"])
        if path.exists():
            return _read_docx(path)
    except Exception:
        pass
    return None


def get_categories() -> list[dict]:
    seen = set()
    result = []
    for cat in CATEGORIES:
        slug = cat["slug"]
        if slug not in seen:
            seen.add(slug)
            result.append({"slug": slug, "title": cat["title"], "icon": cat["icon"]})
    books = get_library()
    used = {b["category"]["slug"] for b in books}
    return [c for c in result if c["slug"] in used]
