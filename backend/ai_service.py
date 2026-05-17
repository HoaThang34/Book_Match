from datetime import datetime
from zoneinfo import ZoneInfo

from backend.models import UserProfile, UserStats
from backend.ollama_service import OllamaError, chat_completion, extract_json

TZ = ZoneInfo("Asia/Ho_Chi_Minh")


def _build_recommendation_system_prompt(now: datetime) -> str:
    day = now.day
    month = now.month
    weekday = now.strftime("%A")
    date_str = now.strftime("%d/%m/%Y")

    return f"""Bạn là cố vấn sách AI cho ứng dụng đọc sách tiếng Việt.
Hôm nay là {weekday}, ngày {date_str} (ngày {day}, tháng {month}).

Nhiệm vụ: đề xuất đúng 3 cuốn sách phù hợp người dùng.
- Cân nhắc ngày/tháng: ví dụ 30/4, 2/9 gợi ý sách lịch sử Việt Nam; Tết (tháng 1-2) gợi ý văn hóa/truyền thống; 8/3, 20/10 gợi ý tiểu sử/phụ nữ; cuối năm gợi ý phản tư/tổng kết.
- Ưu tiên sách có bản tiếng Việt hoặc tên quen thuộc tại Việt Nam.
- match_percent từ 75 đến 99 (số nguyên).
- cover_keyword: 3-6 từ tiếng Anh mô tả bìa sách (dùng làm gợi ý hình ảnh).
- comment: nhận xét ngắn 1-2 câu tiếng Việt về hồ sơ đọc sách của người dùng (tính cách, xu hướng, gợi ý thêm).
- TUYỆT ĐỐI KHÔNG đề xuất lại bất kỳ cuốn sách nào đã nằm trong danh sách "Sách cần tránh" (nếu có).

CHỈ trả về JSON hợp lệ, không markdown, không giải thích ngoài JSON:
{{
  "comment": "Nhận xét ngắn về người dùng",
  "recommendations": [
    {{
      "title": "Tên sách",
      "author": "Tác giả",
      "description": "Mô tả ngắn 2-3 câu tiếng Việt",
      "match_percent": 90,
      "why_fit": "Lý do phù hợp với người dùng",
      "cover_keyword": "history book vietnam"
    }}
  ]
}}"""


def _profile_context(profile: UserProfile | None, stats: UserStats | None) -> str:
    parts = []
    if profile:
        if profile.age:
            parts.append(f"Tuổi: {profile.age}")
        if profile.interests:
            parts.append(f"Sở thích: {profile.interests}")
        if profile.mood:
            parts.append(f"Tâm trạng: {profile.mood}")
    if stats:
        parts.append(f"Chuỗi đọc hiện tại: {stats.current_streak} ngày")
        parts.append(f"Tổng thời gian đọc: {stats.total_read_minutes} phút")
        parts.append(f"Sách đã hoàn thành: {stats.books_completed}")
    if not parts:
        return "Chưa có khảo sát; đề xuất sách phổ biến, dễ tiếp cận."
    return "\n".join(parts)


def get_book_recommendations(
    profile: UserProfile | None,
    stats: UserStats | None,
    exclude_titles: list[str] | None = None,
) -> dict:
    now = datetime.now(TZ)
    system = _build_recommendation_system_prompt(now)
    user_msg = f"Thông tin người dùng:\n{_profile_context(profile, stats)}"
    if exclude_titles:
        titles_str = ", ".join(f'"{t}"' for t in exclude_titles)
        user_msg += f"\n\nSách cần tránh (KHÔNG đề xuất lại): {titles_str}"
    user_msg += "\n\nĐề xuất 3 cuốn sách KHÁC NHAU, không trùng với danh sách trên."

    raw = chat_completion(system, user_msg)
    data = extract_json(raw)
    items = data.get("recommendations") or data.get("books") or []
    if not isinstance(items, list) or not items:
        raise OllamaError("AI không trả danh sách đề xuất hợp lệ.")

    result = []
    for item in items[:3]:
        if not isinstance(item, dict):
            continue
        title = (item.get("title") or "").strip()
        if not title:
            continue
        result.append(
            {
                "title": title,
                "author": (item.get("author") or "Không rõ").strip(),
                "description": (item.get("description") or "").strip(),
                "match_percent": min(99, max(75, int(item.get("match_percent") or 85))),
                "why_fit": (item.get("why_fit") or "").strip(),
                "cover_keyword": (item.get("cover_keyword") or "book cover").strip(),
            }
        )
    if not result:
        raise OllamaError("Không có đề xuất sách hợp lệ.")
    comment = (data.get("comment") or "").strip()
    return {"recommendations": result, "comment": comment}
