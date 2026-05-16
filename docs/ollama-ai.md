# Tích hợp Ollama – Gợi ý sách AI

## Tổng quan

Ứng dụng gọi model local qua [Ollama](https://ollama.com) API (`/api/chat`) để tạo đề xuất sách JSON cho trang `home.html`.

## Cấu hình `.env`

| Biến | Mặc định | Mô tả |
|------|----------|--------|
| `OLLAMA_BASE_URL` | `http://127.0.0.1:11434` | URL máy chủ Ollama |
| `OLLAMA_MODEL` | `llama3.2` | Tên model (`ollama pull llama3.2`) |
| `OLLAMA_TIMEOUT` | `120` | Timeout giây |
| `OLLAMA_TEMPERATURE` | `0.7` | Nhiệt độ sampling |
| `OLLAMA_TOP_P` | `0.9` | top_p |
| `OLLAMA_NUM_PREDICT` | `2048` | Giới hạn token sinh |

## API

| Method | Path | Auth | Mô tả |
|--------|------|------|--------|
| GET | `/api/ai/recommendations` | JWT | 3 cuốn sách + lý do phù hợp |

Phản hồi mẫu:

```json
{
  "recommendations": [
    {
      "title": "...",
      "author": "...",
      "description": "...",
      "match_percent": 90,
      "why_fit": "...",
      "cover_keyword": "history vietnam"
    }
  ]
}
```

## System prompt

- Ngôn ngữ đầu ra: tiếng Việt.
- Bổ sung **ngày/tháng hiện tại** (múi giờ `Asia/Ho_Chi_Minh`) để gợi ý theo sự kiện (30/4, Tết, v.v.).
- Kết hợp khảo sát người dùng (`UserProfile`: tuổi, sở thích, tâm trạng) và thống kê đọc (`UserStats`).

## Module backend

- `backend/ollama_service.py` – HTTP tới Ollama, parse JSON.
- `backend/ai_service.py` – prompt + gọi model.
- `backend/ai_routes.py` – endpoint Flask.

## Lỗi thường gặp

- **503**: Ollama không chạy hoặc model chưa pull → `ollama serve` và `ollama pull <OLLAMA_MODEL>`.
- **401**: Chưa đăng nhập → đăng nhập trước khi mở `home.html`.
